#!/usr/bin/env python
"""v3 -- probe commit: alpha, deployment-aligned lambda_ref, detectability-limited
strata, escalation levels, and the fixed calpool/test split digest.

Torch-free; seconds.  Reads every pool cache ``{pool_dir}/{dsname}_ts{ts}_*_{score}.npz``
for a (dataset, train_seed) and writes ``configs/committed_v3_{dsname}_ts{ts}.json``.

Everything committed here is a function of the independent PROBE split (v2
probe, seed 777 -- byte-identical to the AAAI commitments) and fixed config:

  * ``alpha``                  same fixed rule as v2 (floor + 0.05, ceil to 0.05 grid)
                               on the greedy cache's probe full-acquisition error;
  * ``lambda_refs``            the committed sweep {0.5, 0.7, 0.9} PLUS the
                               deployment-aligned value ``"dep"`` per policy
                               (plug-in operating point on the probe);
  * ``edges[policy][lr_key]``  detectability-limited probe-quantile depth edges
                               (G-rule: expected calibration count per stratum
                               >= n_min(alpha, delta_1, margin));
  * ``escalation[policy][lr_key]``  target answered fractions, the stratum-aware
                               probe-quantile thresholds mu, and the PROBE-ORDERED
                               fixed-sequence testing order (levels sorted by
                               their probe union p-value);
  * ``split``                  sizes + sha256 digests of probe / calpool / test.

Usage
-----
    python scripts/commit_v3.py --dataset mnist --train-seed 0 [--pool-dir pool_v3] [--force]
    python scripts/commit_v3.py --dataset csv:physionet --train-seed 0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.cascade import allocate_delta  # noqa: E402
from cafa.commit_rules import (  # noqa: E402
    deployment_aligned_lambda_ref,
    detectability_limited_edges,
    escalation_levels,
    escalation_order_from_probe,
    n_min_required,
)
from cafa.data import feasible_alpha_from_floor  # noqa: E402
from cafa.metrics import reference_buckets, reference_depth  # noqa: E402
from cafa.pool import load_pool_cache  # noqa: E402
from cafa.splits import split_digest  # noqa: E402
from cafa.splits_v3 import v3_positions  # noqa: E402

FIXED_LAMBDA_REFS = (0.5, 0.7, 0.9)


def dsname_of(dataset: str) -> str:
    for prefix in ("tabular:", "csv:", "image:"):
        if dataset.startswith(prefix):
            return prefix[:-1] + "-" + dataset.split(":", 1)[1]
    return dataset


def build_grid(method_cfg: dict) -> np.ndarray:
    g = method_cfg.get("grid", {"g_min": 0.0, "g_max": 1.0, "n": 100})
    return np.linspace(float(g["g_min"]), float(g["g_max"]), int(g["n"]))


def find_policy_caches(pool_dir: Path, dsname: str, ts: int, score: str) -> dict:
    out = {}
    for p in sorted(Path(pool_dir).glob(f"{dsname}_ts{ts}_*_{score}.npz")):
        stem = p.name[: -len(".npz")]
        tok = stem[len(f"{dsname}_ts{ts}_"):]
        if tok.endswith(f"_{score}"):
            tok = tok[: -len(f"_{score}")]
        out[tok] = p
    return out


def commit(*, dataset: str, train_seed: int, score: str, pool_dir, out_path, cfg: dict,
           force: bool = False, n_buckets: int = None) -> int:
    ts = int(train_seed)
    dsname = dsname_of(dataset)
    pool_dir = Path(pool_dir)
    out_path = Path(out_path)
    if out_path.exists() and not force:
        print(f"ERROR: {out_path} exists; pre-commitment means committed once (use --force).",
              file=sys.stderr)
        return 3

    pv = cfg.get("protocol_v3", cfg.get("protocol_v2", {}))
    probe_frac = float(pv.get("probe_frac", 0.10))
    probe_seed = int(pv.get("probe_seed", 777))
    test_frac = float(pv.get("test_frac_of_eval", 0.5))
    test_seed = int(pv.get("test_seed", 778))
    cal_frac = float(pv.get("cal_frac_of_pool", 0.5))
    method = cfg["method"]
    grid = build_grid(method)
    delta = float(method.get("delta", 0.10))
    d1, d2, d3 = allocate_delta(delta, tuple(cfg.get("cascade", {}).get("delta_weights", (0.5, 0.25, 0.25))))
    margin = float(cfg.get("cascade", {}).get("design_margin", 0.05))
    n_buckets = int(n_buckets or cfg.get("strata_v3", {}).get("n_buckets_nominal", 5))
    n_levels = int(cfg.get("cascade", {}).get("escalation_levels", 41))
    a_min = float(cfg.get("cascade", {}).get("escalation_a_min", 0.05))

    caches = find_policy_caches(pool_dir, dsname, ts, score)
    if "greedy_entropy" not in caches:
        print(f"ERROR: greedy cache {dsname}_ts{ts}_greedy_entropy_{score}.npz required for alpha.",
              file=sys.stderr)
        return 2

    greedy = load_pool_cache(caches["greedy_entropy"])
    n = int(greedy["scores"].shape[0])
    T = int(greedy["correct"].shape[1] - 1)
    pos = v3_positions(n, probe_frac, probe_seed, test_frac, test_seed)
    probe_pos, calpool_pos, test_pos = pos["probe"], pos["calpool"], pos["test"]
    n_cal_expected = int(round(cal_frac * calpool_pos.size))

    floor = float(np.mean(1.0 - np.asarray(greedy["correct"])[probe_pos, T]))
    alpha = float(feasible_alpha_from_floor(floor))
    n_min_1 = n_min_required(alpha, d1, margin)
    n_min_3 = n_min_required(alpha, d3, margin)

    edges: dict = {}
    escalation: dict = {}
    lambda_refs: dict = {}
    for tok, cpath in caches.items():
        cache = load_pool_cache(cpath)
        sc = np.asarray(cache["scores"])[probe_pos]
        co = np.asarray(cache["correct"])[probe_pos]
        lr_dep = deployment_aligned_lambda_ref(sc, co, grid, alpha)
        lrs = {str(float(v)): float(v) for v in FIXED_LAMBDA_REFS}
        lrs["dep"] = float(lr_dep)
        lambda_refs[tok] = lrs
        edges[tok] = {}
        escalation[tok] = {}
        for key, lr in lrs.items():
            d = reference_depth(sc, float(lr))
            e, G, expected = detectability_limited_edges(d, n_buckets, n_cal_expected, n_min_1)
            bid, _ = reference_buckets(sc, float(lr), n_buckets, 1, edges=e)
            fr = np.linspace(a_min, 1.0, n_levels)
            mu, fr_sorted = escalation_levels(sc[:, T], fr, probe_bucket_id=bid)
            order = escalation_order_from_probe(sc[:, T], co[:, T], mu, alpha, bid)
            edges[tok][key] = {
                "edges": [float(x) for x in e.tolist()],
                "G": int(G),
                "expected_cal_counts": [float(x) for x in expected.tolist()],
                "n_min_tier1": int(n_min_1),
            }
            escalation[tok][key] = {
                "fractions_desc": [float(x) for x in fr_sorted.tolist()],
                "mu_asc": [float(x) for x in mu.tolist()],
                "order": [int(x) for x in order.tolist()],
                "n_min_tier3": int(n_min_3),
            }

    committed = {
        "dataset": dataset, "dsname": dsname, "train_seed": ts, "score": score,
        "pipeline": "v3", "tool": "commit_v3.py",
        "created": datetime.now(timezone.utc).isoformat(),
        "cache_meta": greedy["meta"],
        "T": T, "n_heldout": n, "n_buckets_nominal": n_buckets, "pool_dir": str(pool_dir),
        "probe_n": int(probe_pos.size),
        "floor": {"estimate": round(floor, 6)},
        "alpha": alpha,
        "delta": delta, "delta_alloc": [d1, d2, d3], "design_margin": margin,
        "feature_costs_by_scheme": greedy["meta"].get("feature_costs_by_scheme", {}),
        "grid": {"g_min": float(grid[0]), "g_max": float(grid[-1]), "n": int(grid.size)},
        "lambda_refs": lambda_refs,
        "edges": edges,
        "escalation": escalation,
        "split": {
            "probe_frac": probe_frac, "probe_seed": probe_seed,
            "test_frac_of_eval": test_frac, "test_seed": test_seed,
            "cal_frac_of_pool": cal_frac,
            "n_probe": int(probe_pos.size), "n_calpool": int(calpool_pos.size),
            "n_test": int(test_pos.size), "n_cal_expected": n_cal_expected,
            "digest": {"probe": split_digest(probe_pos), "calpool": split_digest(calpool_pos),
                       "test": split_digest(test_pos)},
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(committed, indent=2))
    print(f"[commit_v3] {dataset} ts{ts}: alpha={alpha} (floor {floor:.4f}); "
          f"n_cal_expected={n_cal_expected}; n_min(tier1)={n_min_1}; policies={sorted(caches)}")
    for tok in caches:
        for key in lambda_refs[tok]:
            o0 = escalation[tok][key]["order"][0]
            print(f"    {tok:>22s} lambda_ref[{key}]={lambda_refs[tok][key]:.4f}  "
                  f"G={edges[tok][key]['G']}  tier3 starts at answered~{escalation[tok][key]['fractions_desc'][o0]:.2f}")
    print(f"[commit_v3] wrote {out_path}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3 probe commit")
    p.add_argument("--dataset", required=True)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--score", default=None)
    p.add_argument("--pool-dir", default=None, help="defaults to ${RESULTS_ROOT}/pool_v3")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    p.add_argument("--force", action="store_true")
    p.add_argument("--out-path", default=None, help="override configs/committed_v3_{dsname}_ts{ts}.json "
                   "(ablations; the repair experiment's BEFORE commit)")
    p.add_argument("--n-buckets", type=int, default=None, help="nominal strata before the G-rule (ablation)")
    a = p.parse_args(argv)
    cfg = config.load_experiment(a.config)
    paths = config.load_paths()
    score = a.score or cfg["method"].get("procedure_score", "softmax")
    pool_dir = Path(a.pool_dir) if a.pool_dir else Path(paths.results_root) / "pool_v3"
    out_path = Path(a.out_path) if a.out_path else \
        Path("configs") / f"committed_v3_{dsname_of(a.dataset)}_ts{int(a.train_seed)}.json"
    return commit(dataset=a.dataset, train_seed=a.train_seed, score=score, pool_dir=pool_dir,
                  out_path=out_path, cfg=cfg, force=a.force, n_buckets=a.n_buckets)


if __name__ == "__main__":
    raise SystemExit(main())
