#!/usr/bin/env python
"""WO-9 -- probe commit: pre-commit alpha, stratum edges, and feature costs.

Torch-free (login node, seconds).  Reads the probe rows (fixed 10%, seed 777) of
the pool caches for a (dataset, train_seed) and writes
``configs/committed_v2_{dsname}_ts{ts}.json`` -- the pre-committed provenance
that fixes:
  * the full-acquisition floor and thus alpha (via feasible_alpha_from_floor),
  * the stratum edges for every lambda_ref / bucket scheme / n_buckets,
  * the committed per-scheme feature costs (from the cache meta).

Usage
-----
    python scripts/probe_commit.py --dataset tabular:adult --train-seed 0
    python scripts/probe_commit.py --dataset tabular:adult --train-seed 0 --force
    python scripts/probe_commit.py --dataset tabular:adult --train-seed 0 --extend-edges

``--extend-edges`` merges edge entries for newly-present policies (e.g. the
Phase-2 eps-greedy caches) into an existing committed file WITHOUT touching
floor / alpha / costs.  Refuses to overwrite an existing full commit without
``--force`` (pre-commitment means committed once).

The commit logic lives in :func:`commit` (paths passed explicitly) so it is
unit-testable without the CLI / environment.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import beta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.data import feasible_alpha_from_floor  # noqa: E402
from cafa.metrics import quantile_bucket_edges, reference_buckets  # noqa: E402
from cafa.pool import load_pool_cache  # noqa: E402
from cafa.splits import probe_eval_split  # noqa: E402

_N_BUCKETS = (3, 5, 8)
_MIN_PER_BUCKET = (25, 50, 100)


def dsname_of(dataset: str) -> str:
    if dataset.startswith("tabular:"):
        return "tabular-" + dataset.split(":", 1)[1]
    return dataset


def cp_bounds(k: int, n: int) -> "tuple[float, float]":
    """One-sided 95% Clopper-Pearson lower/upper bounds for k errors of n.

    lcb = beta.ppf(0.05, k, n-k+1)  (0 if k == 0)
    ucb = beta.ppf(0.95, k+1, n-k)  (1 if k == n)
    """
    k = int(k)
    n = int(n)
    lcb = 0.0 if k == 0 else float(beta.ppf(0.05, k, n - k + 1))
    ucb = 1.0 if k == n else float(beta.ppf(0.95, k + 1, n - k))
    return lcb, ucb


def compute_edges(probe_scores: np.ndarray, lambda_refs) -> dict:
    """Committed edges for one policy's probe scores over all lambda_refs/schemes."""
    out = {}
    for lr in lambda_refs:
        quant = {}
        for nb in _N_BUCKETS:
            quant[str(nb)] = [float(e) for e in np.asarray(
                quantile_bucket_edges(probe_scores, float(lr), nb)).tolist()]
        eqw = {}
        for mpb in _MIN_PER_BUCKET:
            _, edges = reference_buckets(probe_scores, float(lr), 5, mpb, edges=None)
            eqw[f"5x{mpb}"] = [float(e) for e in np.asarray(edges).tolist()]
        out[str(float(lr))] = {"quantile": quant, "equal_width_merged": eqw}
    return out


def _probe_scores(cache: dict, probe_frac: float, probe_seed: int) -> np.ndarray:
    """Probe-row scores, recomputing probe positions from n + config (torch-free)."""
    n = cache["scores"].shape[0]
    probe_pos, _ = probe_eval_split(np.arange(n), probe_frac, probe_seed)
    return np.asarray(cache["scores"])[probe_pos]


def find_policy_caches(pool_dir: Path, dsname: str, ts: int, score: str) -> dict:
    """Map policy-token -> cache path for every pool cache of this (dataset, ts, score)."""
    out = {}
    for p in sorted(Path(pool_dir).glob(f"{dsname}_ts{ts}_*_{score}.npz")):
        stem = p.name[: -len(".npz")]
        prefix = f"{dsname}_ts{ts}_"
        suffix = f"_{score}"
        policy_token = stem[len(prefix):]
        if policy_token.endswith(suffix):
            policy_token = policy_token[: -len(suffix)]
        out[policy_token] = p
    return out


def commit(*, dataset, train_seed, score, pool_dir, out_path, cfg,
           force=False, extend_edges=False) -> int:
    """Compute + write the committed probe JSON. Returns a process exit code.

    Paths are explicit (``pool_dir``, ``out_path``) so this is unit-testable
    without the CLI or the path environment.
    """
    ts = int(train_seed)
    dsname = dsname_of(dataset)
    pool_dir = Path(pool_dir)
    out_path = Path(out_path)

    pv = cfg.get("protocol_v2", {})
    probe_frac = float(pv.get("probe_frac", 0.10))
    probe_seed = int(pv.get("probe_seed", 777))
    lambda_refs = list(cfg.get("mondrian_v2", {}).get("lambda_refs", [0.5, 0.7, 0.9]))

    policy_caches = find_policy_caches(pool_dir, dsname, ts, score)
    if not policy_caches:
        print(f"ERROR: no pool caches under {pool_dir} for {dsname}_ts{ts}_*_{score}.npz.",
              file=sys.stderr)
        return 2

    edges = {}
    for policy_token, cpath in policy_caches.items():
        cache = load_pool_cache(cpath)
        edges[policy_token] = compute_edges(
            _probe_scores(cache, probe_frac, probe_seed), lambda_refs
        )

    if extend_edges:
        if not out_path.exists():
            print(f"ERROR: --extend-edges but {out_path} does not exist yet.", file=sys.stderr)
            return 2
        committed = json.loads(out_path.read_text())
        alpha_before = committed.get("alpha")
        committed.setdefault("edges", {})
        # A non-default readiness score defines a DIFFERENT stratification, so
        # its edges live under "<policy>@<score>" -- never under the plain
        # policy key, which stays reserved for the committed base score.
        base_score = committed.get("score", "softmax")
        keyed = {(tok if score == base_score else f"{tok}@{score}"): v
                 for tok, v in edges.items()}
        committed["edges"].update(keyed)
        committed["edges_extended"] = datetime.now(timezone.utc).isoformat()
        # --extend-edges must never touch alpha / floor / costs (pre-commitment).
        assert committed.get("alpha") == alpha_before
        out_path.write_text(json.dumps(committed, indent=2))
        print(f"[probe] extended edges for keys {sorted(keyed)} -> {out_path} "
              f"(alpha unchanged: {alpha_before})", flush=True)
        return 0

    if out_path.exists() and not force:
        print(f"ERROR: {out_path} already exists; pre-commitment means committed once. "
              "Use --force to overwrite or --extend-edges to add policies.", file=sys.stderr)
        return 3

    greedy_token = "greedy_entropy"
    if greedy_token not in policy_caches:
        print(f"ERROR: greedy cache {dsname}_ts{ts}_{greedy_token}_{score}.npz required for the "
              "floor is missing.", file=sys.stderr)
        return 2
    greedy_cache = load_pool_cache(policy_caches[greedy_token])
    n = greedy_cache["scores"].shape[0]
    probe_pos, _ = probe_eval_split(np.arange(n), probe_frac, probe_seed)
    T = greedy_cache["correct"].shape[1] - 1
    probe_correct_T = np.asarray(greedy_cache["correct"])[probe_pos, T]
    probe_n = int(probe_pos.size)
    floor = float(np.mean(1.0 - probe_correct_T))
    k = int(round(float(np.sum(1.0 - probe_correct_T))))
    lcb, ucb = cp_bounds(k, probe_n)
    alpha = float(feasible_alpha_from_floor(floor))

    if "random" in policy_caches:
        rc = load_pool_cache(policy_caches["random"])
        r_floor = float(np.mean(1.0 - np.asarray(rc["correct"])[probe_pos, T]))
        assert abs(r_floor - floor) < 1e-12, (
            f"random floor {r_floor} disagrees with greedy floor {floor}."
        )

    feature_costs_by_scheme = greedy_cache["meta"].get("feature_costs_by_scheme", {})

    committed = {
        "dataset": dataset,
        "train_seed": ts,
        "score": score,
        "cache_meta": greedy_cache["meta"],
        "probe_n": probe_n,
        "floor": {"estimate": round(floor, 6), "cp_lcb95": round(lcb, 6), "cp_ucb95": round(ucb, 6)},
        "alpha": alpha,
        "feature_costs_by_scheme": feature_costs_by_scheme,
        "edges": edges,
        "created": datetime.now(timezone.utc).isoformat(),
        "tool": "probe_commit.py",
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(committed, indent=2))
    print(f"[probe] {dataset} ts{ts}: probe_n={probe_n} floor={floor:.4f} "
          f"[{lcb:.4f}, {ucb:.4f}] -> alpha={alpha:g}", flush=True)
    print(f"[probe] wrote {out_path}", flush=True)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Commit probe artifacts (alpha, edges, costs).")
    p.add_argument("--dataset", required=True, help="mnist | tabular:<name>")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--score", default=None, help="readiness score (default: config procedure_score).")
    p.add_argument("--force", action="store_true", help="overwrite an existing committed file.")
    p.add_argument("--extend-edges", action="store_true",
                   help="merge new-policy edges into an existing committed file.")
    args = p.parse_args(argv)

    cfg = config.load_experiment()
    paths = config.load_paths()
    ts = int(args.train_seed)
    dsname = dsname_of(args.dataset)
    score = args.score or cfg["method"].get("procedure_score", "softmax")

    pool_dir = Path(paths.results_root) / "pool_v2"
    out_path = Path("configs") / f"committed_v2_{dsname}_ts{ts}.json"
    return commit(dataset=args.dataset, train_seed=ts, score=score, pool_dir=pool_dir,
                  out_path=out_path, cfg=cfg, force=args.force, extend_edges=args.extend_edges)


if __name__ == "__main__":
    raise SystemExit(main())
