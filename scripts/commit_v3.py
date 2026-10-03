#!/usr/bin/env python
"""v3 -- probe commit: alpha, deployment-aligned lambda_ref, detectability-limited
strata, escalation levels, and the fixed calpool/test split digest.

Torch-free; seconds.  Reads every pool cache ``{pool_dir}/{dsname}_ts{ts}_*_{score}.npz``
for a (dataset, train_seed) and writes ``configs/committed_v3_{dsname}_ts{ts}.json``.

Everything committed here is a function of the independent PROBE split (v2
probe, seed 777 -- byte-identical to the AAAI commitments) and fixed config:

  * ``alpha``                  same fixed rule as v2 (floor + 0.05, ceil to 0.05 grid)
                               on the greedy cache's probe full-acquisition error
                               (:func:`alpha_from_floor`; ``--alpha-margin`` / ``--alpha-grid``
                               change margin and grid for the E9 alpha-rule sensitivity only,
                               written to a separate ``--out-path``; a non-default rule is
                               recorded as ``alpha_rule`` in the commit);
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
  * ``split``                  sizes + sha256 digests of probe / calpool / test (primary split,
                               ``test_seed``) and, since round 2, the multi-split protocol:
                               ``test_seeds``, ``n_draws`` (total), ``draws_per_split``,
                               ``draw_id_stride`` and per-seed calpool / test sizes and digests
                               (``by_test_seed``).  The split block is the ONLY part of the commit
                               that depends on the test seeds: alpha, lambda_ref, edges, mu and the
                               escalation order are functions of the probe only
                               (tests/test_multisplit_v3.py asserts this).

Usage
-----
    python scripts/commit_v3.py --dataset mnist --train-seed 0 [--pool-dir pool_v3] [--force]
    python scripts/commit_v3.py --dataset csv:physionet --train-seed 0
"""

from __future__ import annotations

import argparse
import json
import math
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
from cafa.splits_v3 import SPLIT_DRAW_STRIDE, draws_per_split, v3_positions, v3_positions_multi  # noqa: E402

FIXED_LAMBDA_REFS = (0.5, 0.7, 0.9)


def dsname_of(dataset: str) -> str:
    for prefix in ("tabular:", "csv:", "image:"):
        if dataset.startswith(prefix):
            return prefix[:-1] + "-" + dataset.split(":", 1)[1]
    return dataset


def build_grid(method_cfg: dict) -> np.ndarray:
    g = method_cfg.get("grid", {"g_min": 0.0, "g_max": 1.0, "n": 100})
    return np.linspace(float(g["g_min"]), float(g["g_max"]), int(g["n"]))


ALPHA_MARGIN, ALPHA_GRID = 0.05, 0.05     # the committed rule (cafa.data.feasible_alpha_from_floor defaults)


def alpha_from_floor(floor: float, margin: float = ALPHA_MARGIN, grid: float = ALPHA_GRID) -> float:
    """v3-local copy of the probe alpha rule with a configurable margin and grid (E9 sensitivity).

    ``alpha`` = the smallest multiple of ``grid`` that is >= ``floor + margin`` (the quotient is rounded to
    9 decimals before the ceiling, against float dust), clipped to ``[grid, 1]`` and rounded to 4
    decimals -- line for line the computation of :func:`cafa.data.feasible_alpha_from_floor`, whose
    ``headroom`` / ``step`` are ``margin`` / ``grid`` here.  With the defaults it reproduces that function
    exactly (tests/test_alpha_rule_v3.py).
    """
    floor = float(floor)
    if not math.isfinite(floor):
        raise ValueError(f"floor must be finite; got {floor!r}.")
    floor = max(0.0, floor)
    n_steps = math.ceil(round((floor + float(margin)) / float(grid), 9))
    alpha = min(1.0, max(float(grid), n_steps * float(grid)))
    return round(alpha, 4)


def diff_commits(old: dict, new: dict, path: str = "") -> list:
    """Paths (``/a/b/c``) of the leaves that differ between two committed JSONs (added or removed keys
    are reported with the suffix `` (added)`` / `` (removed)``).  Used to check that a re-commit changes
    nothing it should not (tests/test_multisplit_v3.py, scripts/compare_decisions_v3.py)."""
    if isinstance(old, dict) and isinstance(new, dict):
        out = []
        for k in sorted(set(old) | set(new), key=str):
            if k not in new:
                out.append(f"{path}/{k} (removed)")
            elif k not in old:
                out.append(f"{path}/{k} (added)")
            else:
                out += diff_commits(old[k], new[k], f"{path}/{k}")
        return out
    return [] if old == new else [path]


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
           force: bool = False, n_buckets: int = None, alpha_margin: float = ALPHA_MARGIN,
           alpha_grid: float = ALPHA_GRID) -> int:
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
    test_seeds = [int(x) for x in pv.get("test_seeds", [test_seed])]
    if test_seed not in test_seeds:
        print(f"ERROR: primary test_seed {test_seed} is not in test_seeds {test_seeds}.", file=sys.stderr)
        return 6
    n_draws_total = int(pv.get("n_draws", 100))
    per_split = draws_per_split(n_draws_total, len(test_seeds))
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
    # v3 guards (provenance): refuse partial --max-rows smoke caches, and require every policy
    # cache to cover the same heldout rows as the greedy cache (same n/T, digest and labels)
    for tok, cpath in caches.items():
        c = greedy if tok == "greedy_entropy" else load_pool_cache(cpath)
        if c["meta"].get("max_rows"):
            print(f"ERROR: {cpath} is a partial --max-rows smoke cache; delete it first.", file=sys.stderr)
            return 4
        dig = greedy["meta"].get("heldout_digest")  # absent only for synthetic smoke caches
        same = (c["scores"].shape == greedy["scores"].shape and c["meta"].get("heldout_digest") == dig
                and (dig is None or np.array_equal(c["y"], greedy["y"])))
        if not same:
            print(f"ERROR: {cpath} does not cover the same heldout rows as the greedy cache.", file=sys.stderr)
            return 5
    T = int(greedy["correct"].shape[1] - 1)
    pos = v3_positions(n, probe_frac, probe_seed, test_frac, test_seed)
    probe_pos, calpool_pos, test_pos = pos["probe"], pos["calpool"], pos["test"]
    n_cal_expected = int(round(cal_frac * calpool_pos.size))
    multi = v3_positions_multi(n, probe_frac, probe_seed, test_frac, test_seeds)
    by_test_seed = {}
    for ps in multi:
        # same probe and the same calpool size on every split -> n_cal_expected (and with it the G-rule
        # edges) is split-invariant
        assert np.array_equal(ps["probe"], probe_pos) and ps["calpool"].size == calpool_pos.size
        by_test_seed[str(ps["test_seed"])] = {
            "split_index": int(ps["split_index"]),
            "n_calpool": int(ps["calpool"].size), "n_test": int(ps["test"].size),
            "digest": {"calpool": split_digest(ps["calpool"]), "test": split_digest(ps["test"])}}

    floor = float(np.mean(1.0 - np.asarray(greedy["correct"])[probe_pos, T]))
    default_rule = (float(alpha_margin), float(alpha_grid)) == (ALPHA_MARGIN, ALPHA_GRID)
    alpha = float(feasible_alpha_from_floor(floor)) if default_rule else alpha_from_floor(floor, alpha_margin, alpha_grid)
    if alpha <= margin:
        # n_min(alpha, level, design_margin) needs alpha - design_margin > 0 (cafa.commit_rules.n_min_required)
        print(f"ERROR: alpha={alpha} (floor {floor:.4f}, alpha rule margin {alpha_margin} / grid {alpha_grid}) is not "
              f"above the design margin {margin}: the detectability rule n_min(alpha, level, margin) is undefined; "
              "nothing committed.", file=sys.stderr)
        return 7
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
        **({} if default_rule else {"alpha_rule": {"margin": float(alpha_margin), "grid": float(alpha_grid)}}),
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
            "test_seeds": test_seeds, "n_draws": n_draws_total, "draws_per_split": per_split,
            "draw_id_stride": SPLIT_DRAW_STRIDE,
            "by_test_seed": by_test_seed,
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(committed, indent=2))
    print(f"[commit_v3] {dataset} ts{ts}: alpha={alpha} (floor {floor:.4f}); "
          f"n_cal_expected={n_cal_expected}; n_min(tier1)={n_min_1}; policies={sorted(caches)}; "
          f"test_seeds={test_seeds} x {per_split} draws")
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
    p.add_argument("--alpha-margin", type=float, default=ALPHA_MARGIN,
                   help="alpha = ceil-to-grid(floor + margin) (default 0.05 = the committed rule; E9 ablation only)")
    p.add_argument("--alpha-grid", type=float, default=ALPHA_GRID, help="alpha grid (default 0.05; E9 ablation only)")
    a = p.parse_args(argv)
    if (a.alpha_margin, a.alpha_grid) != (ALPHA_MARGIN, ALPHA_GRID) and not a.out_path:
        p.error("a non-default alpha rule needs --out-path (the main commit is made with the committed rule only)")
    cfg = config.load_experiment(a.config)
    paths = config.load_paths()
    score = a.score or cfg["method"].get("procedure_score", "softmax")
    pool_dir = Path(a.pool_dir) if a.pool_dir else Path(paths.results_root) / "pool_v3"
    out_path = Path(a.out_path) if a.out_path else \
        Path("configs") / f"committed_v3_{dsname_of(a.dataset)}_ts{int(a.train_seed)}.json"
    return commit(dataset=a.dataset, train_seed=a.train_seed, score=score, pool_dir=pool_dir,
                  out_path=out_path, cfg=cfg, force=a.force, n_buckets=a.n_buckets,
                  alpha_margin=a.alpha_margin, alpha_grid=a.alpha_grid)


if __name__ == "__main__":
    raise SystemExit(main())
