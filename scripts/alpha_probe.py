#!/usr/bin/env python
# DEPRECATED (kept for provenance). Superseded by the v2 pipeline (see README +
# CLAUDE_CODE_WORKORDER.md). Known issues in the legacy pipeline: per-seed
# full-pool reshuffle (MNIST leakage), cal-fit stratum edges, clairvoyant tabular
# greedy (pre-fix), lambda_ref-duplicated marginal counting. Do not use for paper numbers.
"""Report the full-acquisition risk floor and the fixed-rule feasible alpha.

Step 5, Task 1 (the α-feasibility protocol). For a tabular dataset this:

1. trains / loads the exact same ``TabularMaskedPredictor`` the sweep uses and
   rolls out a trajectory (via ``run_mondrian.get_or_rollout_tabular``);
2. evaluates the **full-acquisition population risk floor** on test
   (``oracle_full_feature`` = ``oracle_full_feature_risk(1 - test_correct[:, T])``,
   identical to what ``analyse_cell`` records);
3. applies the **fixed rule** ``alpha = ceil-to-0.05(floor + 0.05)``
   (``cafa.data.feasible_alpha_from_floor``) and prints the recommended
   ``--alpha`` to use for that dataset across the sweep.

The floor is policy- and cost-scheme-independent (it is the risk when *all*
features are acquired), so the probe rolls out with a single, fixed policy/scheme
and averages over seeds.

This does NOT tune α per result — it applies one fixed rule and records
``{floor, α}`` per dataset, defusing caveat §12.1. Run the one-time
``fetch_openml`` for the dataset first (see STEP4_HANDOFF / the run-list); the
probe reads the cached data (``download=False``) exactly like the sweep.

    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    python scripts/alpha_probe.py --dataset tabular:MiniBooNE --device cpu
    python scripts/alpha_probe.py --dataset tabular:spambase  --device cpu --seeds 5
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent.parent / "src"))
sys.path.insert(0, str(THIS.parent))  # allow importing run_mondrian as a module

from cafa import config  # noqa: E402
from cafa.baselines import oracle_full_feature_risk  # noqa: E402
from cafa.data import feasible_alpha_from_floor  # noqa: E402

import run_mondrian as rm  # noqa: E402  (reuse the real train+rollout path)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", required=True,
                   help="tabular:<name> (e.g. tabular:MiniBooNE). MNIST has a "
                        "fixed uniform-cost setup and is not the target here.")
    p.add_argument("--device", default="cpu")
    p.add_argument("--policy", default="greedy_entropy",
                   choices=["greedy_entropy", "random"],
                   help="Rollout policy for the probe (the floor is "
                        "policy-independent; default greedy_entropy).")
    p.add_argument("--cost-scheme", default="uniform",
                   choices=["inverse_info", "random", "uniform"],
                   help="Rollout cost scheme (floor is cost-independent).")
    p.add_argument("--seeds", type=int, default=None,
                   help="How many protocol seeds to average over (default: all).")
    p.add_argument("--headroom", type=float, default=0.05,
                   help="Headroom above the floor before ceiling (default 0.05).")
    p.add_argument("--step", type=float, default=0.05,
                   help="Clean-value granularity for the ceiling (default 0.05).")
    return p.parse_args(argv)


def _floor_for_seed(dataset, policy, cost_scheme, seed, cfg, paths, device):
    """Full-acquisition risk floor for one seed, via the real rollout path."""
    if not dataset.startswith("tabular:"):
        raise ValueError("alpha_probe targets tabular:<name> datasets.")
    name = dataset.split(":", 1)[1]
    traj_dir = Path(paths.results_root) / "trajectories"
    ckpt_dir = Path(paths.results_root) / "checkpoints"
    arr = rm.get_or_rollout_tabular(
        traj_dir, ckpt_dir, name=name, policy=policy, cost_scheme=cost_scheme,
        seed=seed, cfg=cfg, device=device,
    )
    T = arr["test_correct"].shape[1] - 1          # last step = all features acquired
    full_loss = 1.0 - arr["test_correct"][:, T]   # matches analyse_cell exactly
    return float(oracle_full_feature_risk(full_loss))


def main(argv=None) -> int:
    args = parse_args(argv)
    cfg = config.load_experiment()
    paths = config.load_paths()
    seeds = list(cfg["protocol"]["seeds"])
    if args.seeds is not None:
        seeds = seeds[: max(1, args.seeds)]

    print(f"dataset      : {args.dataset}")
    print(f"seeds        : {seeds} ({len(seeds)})")
    print(f"rollout      : policy={args.policy} cost_scheme={args.cost_scheme} "
          f"(floor is invariant to both)")
    print("-" * 70)

    floors = []
    for s in seeds:
        try:
            fl = _floor_for_seed(args.dataset, args.policy, args.cost_scheme, s,
                                 cfg, paths, args.device)
        except FileNotFoundError as exc:
            print(f"ERROR: data/cache missing for seed {s}: {exc}", file=sys.stderr)
            print("Run the one-time fetch_openml for this dataset first (login node), "
                  "into the same DATA_ROOT the sweep uses.", file=sys.stderr)
            return 2
        floors.append(fl)
        print(f"  seed {s:>3}: full-acq floor = {fl:.4f}")

    floor = float(np.mean(floors)) if floors else float("nan")
    floor_sd = float(np.std(floors)) if len(floors) > 1 else 0.0
    alpha = feasible_alpha_from_floor(floor, headroom=args.headroom, step=args.step)

    print("-" * 70)
    print(f"mean full-acquisition risk floor : {floor:.4f}  (sd {floor_sd:.4f})")
    print(f"fixed rule  alpha = ceil{args.step:g}(floor + {args.headroom:g}) "
          f"= {alpha:g}")

    # Compare with whatever is currently recorded in the config, if present.
    name = args.dataset.split(":", 1)[1]
    recorded = None
    for d in cfg.get("datasets_tabular", []):
        if d.get("name") == name:
            recorded = d.get("alpha")
            break
    if recorded is not None:
        same = abs(float(recorded) - alpha) < 1e-9
        print(f"config currently records alpha = {float(recorded):g} "
              f"-> {'OK (matches rule)' if same else 'UPDATE: set it to %g' % alpha}")
    else:
        print(f"config has no alpha recorded for {name} yet -> add "
              f"`alpha: {alpha:g}` to its datasets_tabular entry.")

    if not math.isnan(floor) and floor < 1e-9:
        print("NOTE: floor ~ 0 -- this dataset is trivially easy; H3's abstention "
              "story will not appear here (a legitimate boundary to report).")

    print()
    print(f"Use:  python scripts/run_mondrian.py --dataset {args.dataset} "
          f"... --alpha {alpha:g} --lambda-ref <lr>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())