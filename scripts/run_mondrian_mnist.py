#!/usr/bin/env python
# DEPRECATED (kept for provenance). Superseded by the v2 pipeline (see README +
# CLAUDE_CODE_WORKORDER.md). Known issues in the legacy pipeline: per-seed
# full-pool reshuffle (MNIST leakage), cal-fit stratum edges, clairvoyant tabular
# greedy (pre-fix), lambda_ref-duplicated marginal counting. Do not use for paper numbers.
"""Step 3 -- per-bucket ("Mondrian") risk control on MNIST-as-AFA (reporting).

For each protocol seed this script:
  1. loads the frozen backbone checkpoint
     ``${results_root}/checkpoints/{dataset}_{backbone}.pt``;
  2. rebuilds the calibration/test splits with :func:`cafa.data.load_mnist_afa`
     and rolls out the acquisition policy, caching the trajectories to
     ``${results_root}/trajectories/{dataset}_{backbone}_seed{k}.npz`` (reused on
     re-runs, so the torch rollout happens at most once per seed);
  3. buckets instances by reference depth -- edges estimated on the *calibration*
     scores and reused on test (never re-estimated on a held-out selection set);
  4. selects a single marginal threshold (:func:`cafa.risk_control.ltt_select`)
     and per-bucket Mondrian thresholds (:func:`cafa.risk_control.mondrian_select`)
     on calibration;
  5. evaluates realized per-bucket risk and cost on test and writes
     ``${results_root}/metrics/mondrian_mnist_seed{k}.json``.

This is a *reporting* run (not a gate): MNIST has no ground-truth accuracy curve,
so risk is the realized 0/1 test loss at the selected stops.  Feed the resulting
metrics to ``make_figures.py`` for Figure C.

Usage::

    python scripts/run_mondrian_mnist.py --all-seeds --device cuda
    python scripts/run_mondrian_mnist.py --seed-index 0 --device cpu
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.metrics import (  # noqa: E402
    per_bucket_cost,
    per_bucket_risk,
    quantile_bucket_edges,
    reference_buckets,
    stops_from_grid_np,
)
from cafa.risk_control import ltt_select, mondrian_select  # noqa: E402


def build_grid(method_cfg: dict) -> np.ndarray:
    g = method_cfg.get("grid", {"g_min": 0.0, "g_max": 1.0, "n": 100})
    return np.linspace(float(g["g_min"]), float(g["g_max"]), int(g["n"]))


def load_checkpoint(ckpt_path: Path, device):
    """Load the masked predictor + meta (torch imported lazily)."""
    import torch
    from cafa.models import MaskedPredictor, N_CLASSES

    payload = torch.load(ckpt_path, map_location=device, weights_only=False)
    meta = payload.get("meta", {})
    model = MaskedPredictor(n_classes=int(meta.get("n_classes", N_CLASSES)))
    model.load_state_dict(payload["state_dict"])
    model.to(device)
    model.eval()
    return model, meta


def get_or_rollout(traj_path: Path, *, cfg, seed, backbone, model, feature_costs,
                   score_name, device) -> dict:
    """Return cached trajectory arrays or roll out (and cache) fresh ones.

    Cached payload holds the ``scores`` / ``correct`` / ``cum_cost`` arrays for
    both the calibration and test splits, which is all the selection and
    evaluation below need (no torch once cached).
    """
    if traj_path.exists():
        z = np.load(traj_path)
        return {k: z[k] for k in z.files}

    from cafa.acquisition import get_policy, rollout

    data = load_mnist_afa(cfg, seed=seed, download=False)
    X_cal, y_cal = data["cal"]
    X_test, y_test = data["test"]
    policy = get_policy(backbone, data["train"][0], seed=seed)
    cal = rollout(model, policy, score_name, X_cal, y_cal, feature_costs, device=device)
    tst = rollout(model, policy, score_name, X_test, y_test, feature_costs, device=device)
    arrays = {
        "cal_scores": np.asarray(cal.scores), "cal_correct": np.asarray(cal.correct),
        "cal_cum_cost": np.asarray(cal.cum_cost),
        "test_scores": np.asarray(tst.scores), "test_correct": np.asarray(tst.correct),
        "test_cum_cost": np.asarray(tst.cum_cost),
    }
    traj_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(traj_path, **arrays)
    return arrays


# load_mnist_afa is only needed on the rollout path; import lazily there.
def load_mnist_afa(cfg, seed, download=False):  # noqa: D401  (thin lazy wrapper)
    from cafa.data import load_mnist_afa as _impl
    return _impl(cfg, seed=seed, download=download)


def run_one_seed(seed, *, dataset, backbone, model, feature_costs, grid, method_cfg,
                 syn_cfg, score_name, cfg, device, traj_dir) -> dict:
    alpha = float(method_cfg["alpha"])
    delta = float(method_cfg["delta"])
    procedure = method_cfg.get("procedure", "fixed_sequence")
    mond_cfg = method_cfg.get("mondrian", {})
    lam_ref = float(mond_cfg.get("lambda_ref", 0.5))
    n_buckets = int(mond_cfg.get("n_buckets", 5))
    min_per_bucket = int(mond_cfg.get("min_per_bucket", 50))

    traj_path = traj_dir / f"{dataset}_{backbone}_seed{seed}.npz"
    arr = get_or_rollout(traj_path, cfg=cfg, seed=seed, backbone=backbone, model=model,
                         feature_costs=feature_costs, score_name=score_name, device=device)

    # Bucket by reference depth: edges from CALIBRATION scores, reused on test.
    use_quantile = str(syn_cfg.get("bucket_edges", "quantile")).lower() == "quantile"
    if use_quantile:
        edges = quantile_bucket_edges(arr["cal_scores"], lam_ref, n_buckets)
        cal_bid, edges = reference_buckets(arr["cal_scores"], lam_ref, n_buckets,
                                           min_per_bucket, edges=edges)
    else:
        cal_bid, edges = reference_buckets(arr["cal_scores"], lam_ref, n_buckets,
                                           min_per_bucket)
    test_bid, _ = reference_buckets(arr["test_scores"], lam_ref, n_buckets,
                                    min_per_bucket, edges=edges)

    cal_losses, cal_costs, _ = stops_from_grid_np(
        arr["cal_scores"], arr["cal_correct"], arr["cal_cum_cost"], grid)
    test_losses, test_costs, _ = stops_from_grid_np(
        arr["test_scores"], arr["test_correct"], arr["test_cum_cost"], grid)

    marg = ltt_select(cal_losses, cal_costs, grid, alpha=alpha, delta=delta,
                      procedure=procedure)
    mond = mondrian_select(cal_losses, cal_costs, grid, alpha=alpha, delta=delta,
                           bucket_id=cal_bid, procedure=procedure)

    labels = np.unique(test_bid)
    marg_map = {int(k): marg.lambda_idx for k in labels}
    marg_risk = per_bucket_risk(test_losses, test_bid, marg_map)
    marg_cost = per_bucket_cost(test_costs, test_bid, marg_map)
    mond_risk = per_bucket_risk(test_losses, test_bid, mond.lambda_idx_by_bucket)
    mond_cost = per_bucket_cost(test_costs, test_bid, mond.lambda_idx_by_bucket)

    # Full-acquisition fallback: for every bucket where Mondrian abstained
    # (lambda_idx is None -> operationally "acquire everything"), the realized
    # test risk at stop depth = T is mean(1 - correct[:, T]) over the bucket's
    # test rows. Computed directly from the cached trajectories (no re-rollout).
    T_depth = arr["test_correct"].shape[1] - 1
    full_acq_loss = 1.0 - arr["test_correct"][:, T_depth]          # [n_test]
    fallback_full_acq: dict = {}
    for k in labels:
        if mond.lambda_idx_by_bucket.get(int(k)) is None:         # abstained on this bucket
            mask = test_bid == k
            fallback_full_acq[int(k)] = (float(full_acq_loss[mask].mean())
                                         if mask.any() else None)

    def _overall(idx, mat):
        return None if idx is None else float(mat[:, int(idx)].mean())

    def _jsonable(d):
        return {str(int(k)): (None if v is None or (isinstance(v, float) and np.isnan(v))
                              else float(v)) for k, v in d.items()}

    return {
        "dataset": dataset, "backbone": backbone, "seed": int(seed),
        "score": score_name, "alpha": alpha, "delta": delta, "procedure": procedure,
        "lambda_ref": lam_ref, "n_buckets": n_buckets,
        "bucket_edges": [float(e) for e in np.asarray(edges).tolist()],
        "bucket_sizes_cal": {str(int(k)): int((cal_bid == k).sum()) for k in np.unique(cal_bid)},
        "bucket_sizes_test": {str(int(k)): int((test_bid == k).sum()) for k in labels},
        "marginal": {
            "lambda_idx": (None if marg.lambda_idx is None else int(marg.lambda_idx)),
            "lambda_value": (None if marg.lambda_value is None else float(marg.lambda_value)),
            "overall_risk": _overall(marg.lambda_idx, test_losses),
            "overall_cost": _overall(marg.lambda_idx, test_costs),
            "per_bucket_risk": _jsonable(marg_risk),
            "per_bucket_cost": _jsonable(marg_cost),
        },
        "mondrian": {
            "joint": bool(mond.joint),
            "lambda_idx_by_bucket": {str(int(k)): (None if v is None else int(v))
                                     for k, v in mond.lambda_idx_by_bucket.items()},
            "per_bucket_risk": _jsonable(mond_risk),
            "per_bucket_cost": _jsonable(mond_cost),
        },
        "fallback_full_acq_risk_by_bucket": _jsonable(fallback_full_acq),
        "config_snapshot": {"method": method_cfg},
    }


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CAFA Step 3 Mondrian on MNIST (reporting).")
    p.add_argument("--dataset", default="mnist", choices=["mnist"])
    p.add_argument("--backbone", default="greedy_entropy")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--seed-index", type=int, default=None,
                       help="Run a single protocol seed by index.")
    group.add_argument("--all-seeds", action="store_true",
                       help="Run every protocol seed.")
    p.add_argument("--device", default="cpu", help="cuda or cpu.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    cfg = config.load_experiment()
    paths = config.load_paths()
    method_cfg = cfg["method"]
    syn_cfg = method_cfg.get("synthetic", {})
    score_name = method_cfg.get("procedure_score", "softmax")
    grid = build_grid(method_cfg)

    seeds = list(cfg["protocol"]["seeds"])
    if args.all_seeds:
        run_seeds = seeds
    elif args.seed_index is not None:
        run_seeds = [seeds[args.seed_index]]
    else:
        run_seeds = [seeds[0]]

    ckpt_path = Path(paths.results_root) / "checkpoints" / f"{args.dataset}_{args.backbone}.pt"
    if not ckpt_path.exists():
        print(f"ERROR: checkpoint not found at {ckpt_path}. "
              "Train it first (scripts/train_backbone.py).", file=sys.stderr)
        return 1

    metrics_dir = Path(paths.results_root) / "metrics"
    traj_dir = Path(paths.results_root) / "trajectories"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    # Only load the backbone if some seed's trajectory cache is missing (i.e. a
    # rollout is actually required). When every trajectory is cached this recompute
    # needs neither the checkpoint nor a GPU.
    def _traj_file(s):
        return traj_dir / f"{args.dataset}_{args.backbone}_seed{s}.npz"

    missing = [s for s in run_seeds if not _traj_file(s).exists()]
    if missing:
        if not ckpt_path.exists():
            print(f"ERROR: checkpoint not found at {ckpt_path} and trajectories "
                  f"missing for seeds {missing}. Train/rollout first.", file=sys.stderr)
            return 1
        model, meta = load_checkpoint(ckpt_path, args.device)
        feature_costs = np.asarray(meta.get("feature_costs"), dtype=float)
    else:
        model, feature_costs = None, None
        print("All trajectories cached -> recomputing metrics only "
              "(no checkpoint load, no rollout).")

    fallback_acc: dict = {}
    for seed in run_seeds:
        rec = run_one_seed(seed, dataset=args.dataset, backbone=args.backbone, model=model,
                           feature_costs=feature_costs, grid=grid, method_cfg=method_cfg,
                           syn_cfg=syn_cfg, score_name=score_name, cfg=cfg, device=args.device,
                           traj_dir=traj_dir)
        out_path = metrics_dir / f"mondrian_mnist_seed{seed}.json"
        out_path.write_text(json.dumps(rec, indent=2))
        m = rec["marginal"]["per_bucket_risk"]
        o = rec["mondrian"]["per_bucket_risk"]
        fb = rec["fallback_full_acq_risk_by_bucket"]
        for k, v in fb.items():
            if v is not None:
                fallback_acc.setdefault(int(k), []).append(v)
        print(f"seed {seed}: wrote {out_path.name} | "
              f"marginal per-bucket risk={m} | mondrian per-bucket risk={o} | "
              f"full-acq fallback (abstained buckets)={fb}")

    # Cross-seed summary of the full-acquisition fallback on abstaining buckets.
    if fallback_acc:
        print("\nFull-acquisition fallback risk on Mondrian-abstaining buckets "
              f"(alpha={method_cfg['alpha']}):")
        for k in sorted(fallback_acc):
            vals = np.asarray(fallback_acc[k], dtype=float)
            n_over = int((vals > float(method_cfg["alpha"])).sum())
            print(f"  bucket {k}: n={vals.size} seeds | mean={vals.mean():.4f} "
                  f"min={vals.min():.4f} max={vals.max():.4f} | "
                  f"> alpha on {n_over}/{vals.size} "
                  f"(even acquiring everything, risk stays above alpha)")
    else:
        print("\nNo Mondrian abstentions across the processed seeds "
              "(no full-acquisition fallback needed).")

    print(f"\nDone. Metrics in {metrics_dir}. Run scripts/make_figures.py for Figure C.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())