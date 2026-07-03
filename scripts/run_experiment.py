#!/usr/bin/env python
# DEPRECATED (kept for provenance). Superseded by the v2 pipeline (see README +
# CLAUDE_CODE_WORKORDER.md). Known issues in the legacy pipeline: per-seed
# full-pool reshuffle (MNIST leakage), cal-fit stratum edges, clairvoyant tabular
# greedy (pre-fix), lambda_ref-duplicated marginal counting. Do not use for paper numbers.
"""End-to-end MNIST run: rollout -> grid -> frozen selector -> realized test risk.

For each protocol seed this:

1. loads the frozen checkpoint; builds the policy (from ``--backbone``) and the
   readiness score fn (``method.procedure_score``, default ``softmax``);
2. gets disjoint ``cal`` / ``test`` for the seed via ``load_mnist_afa``;
3. ``rollout`` on cal and on test -> ``stops_from_grid`` with the config grid ->
   ``(cal_losses, cal_costs)`` and ``(test_losses, test_costs)``;
4. ``sel = ltt_select(cal_losses, cal_costs, grid, alpha, delta, procedure=...)``
   -- the **frozen** selector;
5. evaluates at ``sel.lambda_idx`` on TEST: realized risk, realized cost, mean
   stop depth;
6. writes ``${results_root}/metrics/{dataset}_{backbone}_seed{seed}.json`` with
   seed, config snapshot, selection, and realized test numbers.

With ``--all-seeds``, after the loop it prints the **G2 summary**: the fraction
of seeds with ``realized_risk > alpha`` (must be <= delta), plus mean realized
cost and mean stop depth across seeds -- the end-to-end gate.

Usage
-----
    python scripts/run_experiment.py --dataset mnist --backbone greedy_entropy \
        [--seed-index K | --all-seeds] [--device cuda|cpu]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.acquisition import get_policy, rollout, stops_from_grid  # noqa: E402
from cafa.data import load_mnist_afa  # noqa: E402
from cafa.metrics import cost_at_selected, risk_at_selected  # noqa: E402
from cafa.models import MaskedPredictor, N_CLASSES  # noqa: E402
from cafa.risk_control import ltt_select  # noqa: E402


def build_grid(method_cfg: dict) -> np.ndarray:
    """Ascending lambda grid from the config ``method.grid`` block."""
    g = method_cfg.get("grid", {"g_min": 0.0, "g_max": 1.0, "n": 100})
    grid = np.linspace(float(g["g_min"]), float(g["g_max"]), int(g["n"]))
    return grid  # linspace is ascending for g_min < g_max


def load_checkpoint(ckpt_path: Path, device) -> "tuple[MaskedPredictor, dict]":
    payload = torch.load(ckpt_path, map_location=device, weights_only=False)
    meta = payload.get("meta", {})
    model = MaskedPredictor(n_classes=int(meta.get("n_classes", N_CLASSES)))
    model.load_state_dict(payload["state_dict"])
    model.to(device)
    model.eval()
    return model, meta


def run_one_seed(
    seed: int,
    *,
    dataset: str,
    backbone: str,
    model: MaskedPredictor,
    feature_costs: np.ndarray,
    grid: np.ndarray,
    alpha: float,
    delta: float,
    procedure: str,
    score_name: str,
    cfg: dict,
    device,
) -> dict:
    """Steps 2-5 for a single seed; returns the metrics record (step 6 payload)."""
    data = load_mnist_afa(cfg, seed=seed, download=False)
    X_cal, y_cal = data["cal"]
    X_test, y_test = data["test"]

    policy = get_policy(backbone, data["train"][0], seed=seed)

    cal_traj = rollout(model, policy, score_name, X_cal, y_cal, feature_costs, device=device)
    test_traj = rollout(model, policy, score_name, X_test, y_test, feature_costs, device=device)

    cal_losses, cal_costs, _ = stops_from_grid(cal_traj, grid)
    test_losses, test_costs, test_stop = stops_from_grid(test_traj, grid)

    sel = ltt_select(cal_losses, cal_costs, grid, alpha=alpha, delta=delta, procedure=procedure)

    idx = sel.lambda_idx
    if idx is None:
        realized_risk = float("nan")
        realized_cost = float("nan")
        mean_stop_depth = float("nan")
        certified = False
    else:
        realized_risk = risk_at_selected(test_losses, idx)
        realized_cost = cost_at_selected(test_costs, idx)
        mean_stop_depth = float(test_stop[:, idx].mean())
        certified = True

    record = {
        "dataset": dataset,
        "backbone": backbone,
        "seed": int(seed),
        "score": score_name,
        "alpha": float(alpha),
        "delta": float(delta),
        "procedure": procedure,
        "grid": {"g_min": float(grid[0]), "g_max": float(grid[-1]), "n": int(grid.size)},
        "n_cal": int(X_cal.shape[0]),
        "n_test": int(X_test.shape[0]),
        "selection": {
            "certified": certified,
            "lambda_idx": (None if idx is None else int(idx)),
            "lambda_value": (None if sel.lambda_value is None else float(sel.lambda_value)),
            "n_valid": int(sel.valid_mask.sum()),
            "cal_risk_at_selected": (None if idx is None else float(sel.r_hat[idx])),
            "cal_cost_at_selected": (None if idx is None else float(sel.c_hat[idx])),
        },
        "realized_test": {
            "realized_risk": realized_risk,
            "realized_cost": realized_cost,
            "mean_stop_depth": mean_stop_depth,
        },
        "config_snapshot": {"method": cfg.get("method", {}), "protocol": cfg.get("protocol", {})},
    }
    return record


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CAFA end-to-end MNIST run (G2).")
    p.add_argument("--dataset", default="mnist", choices=["mnist"])
    p.add_argument("--backbone", default="greedy_entropy")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--seed-index", type=int, default=None, help="Run a single protocol seed by index.")
    group.add_argument("--all-seeds", action="store_true", help="Run every protocol seed + G2 summary.")
    p.add_argument("--device", default="cpu", help="cuda or cpu.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    cfg = config.load_experiment()
    paths = config.load_paths()
    method_cfg = cfg.get("method", {})
    protocol = cfg.get("protocol", {})

    alpha = float(method_cfg.get("alpha", 0.10))
    delta = float(method_cfg.get("delta", 0.10))
    procedure = str(method_cfg.get("procedure", "fixed_sequence"))
    score_name = str(method_cfg.get("procedure_score", "softmax"))
    grid = build_grid(method_cfg)

    seeds = list(protocol.get("seeds", list(range(20))))
    if args.all_seeds:
        selected_seeds = seeds
    else:
        k = args.seed_index if args.seed_index is not None else 0
        if not (0 <= k < len(seeds)):
            raise SystemExit(f"--seed-index {k} out of range [0, {len(seeds)}).")
        selected_seeds = [seeds[k]]

    device = torch.device(args.device if torch.cuda.is_available() or args.device == "cpu" else "cpu")

    ckpt_path = Path(paths.results_root) / "checkpoints" / f"{args.dataset}_{args.backbone}.pt"
    if not ckpt_path.is_file():
        raise SystemExit(
            f"checkpoint not found: {ckpt_path}\n"
            f"Train it first: python scripts/train_backbone.py "
            f"--dataset {args.dataset} --backbone {args.backbone}"
        )
    model, meta = load_checkpoint(ckpt_path, device)
    feature_costs = np.asarray(meta.get("feature_costs", np.ones(49)), dtype=float)

    metrics_dir = Path(paths.results_root) / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for seed in selected_seeds:
        # Determinism per seed (rollout policies / any sampling).
        config.set_seed(seed)
        torch.manual_seed(int(seed))
        rec = run_one_seed(
            seed,
            dataset=args.dataset,
            backbone=args.backbone,
            model=model,
            feature_costs=feature_costs,
            grid=grid,
            alpha=alpha,
            delta=delta,
            procedure=procedure,
            score_name=score_name,
            cfg=cfg,
            device=device,
        )
        out_path = metrics_dir / f"{args.dataset}_{args.backbone}_seed{seed}.json"
        with open(out_path, "w") as f:
            json.dump(rec, f, indent=2)
        records.append(rec)

        rt = rec["realized_test"]
        sel = rec["selection"]
        if sel["certified"]:
            print(
                f"[run] seed={seed:>3}  lambda={sel['lambda_value']:.4f} "
                f"(idx {sel['lambda_idx']})  realized_risk={rt['realized_risk']:.4f}  "
                f"realized_cost={rt['realized_cost']:.3f}  "
                f"mean_stop_depth={rt['mean_stop_depth']:.3f}  -> {out_path.name}",
                flush=True,
            )
        else:
            print(f"[run] seed={seed:>3}  NO CERTIFICATION (lambda_idx is None)  -> {out_path.name}", flush=True)

    if args.all_seeds:
        _print_g2_summary(records, alpha=alpha, delta=delta)
    return 0


def _print_g2_summary(records, *, alpha: float, delta: float) -> None:
    """G2 gate: violation fraction <= delta, plus mean cost / stop depth."""
    n_seeds = len(records)
    certified = [r for r in records if r["selection"]["certified"]]
    n_cert = len(certified)
    n_none = n_seeds - n_cert

    risks = np.array([r["realized_test"]["realized_risk"] for r in certified], dtype=float)
    costs = np.array([r["realized_test"]["realized_cost"] for r in certified], dtype=float)
    depths = np.array([r["realized_test"]["mean_stop_depth"] for r in certified], dtype=float)

    # Non-certifying draws do not violate (they make no risk claim) -> count as
    # non-violations over all seeds, matching the metrics.violation_rate sentinel.
    n_violations = int(np.sum(risks > alpha)) if risks.size else 0
    violation_fraction = n_violations / n_seeds if n_seeds else 0.0

    print("\n================ G2 summary (end-to-end MNIST) ================", flush=True)
    print(f"seeds run                : {n_seeds}", flush=True)
    print(f"certified (lambda found) : {n_cert}   |  no certification: {n_none}", flush=True)
    print(f"alpha / delta            : {alpha:.3f} / {delta:.3f}", flush=True)
    print(
        f"violation fraction       : {violation_fraction:.3f}  "
        f"({n_violations}/{n_seeds} seeds with realized_risk > alpha)   "
        f"[GATE: <= delta={delta:.3f} -> {'PASS' if violation_fraction <= delta else 'FAIL'}]",
        flush=True,
    )
    if risks.size:
        print(f"mean realized risk       : {np.nanmean(risks):.4f}", flush=True)
        print(f"mean realized cost       : {np.nanmean(costs):.3f}  (of 49 patches)", flush=True)
        print(
            f"mean stop depth          : {np.nanmean(depths):.3f}  "
            f"[expect < 49 -> {'PASS' if np.nanmean(depths) < 49 else 'FAIL'}]",
            flush=True,
        )
    print("==============================================================\n", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())