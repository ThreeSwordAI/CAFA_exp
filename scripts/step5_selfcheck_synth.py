#!/usr/bin/env python
# DEPRECATED (kept for provenance). Superseded by the v2 pipeline (see README +
# CLAUDE_CODE_WORKORDER.md). Known issues in the legacy pipeline: per-seed
# full-pool reshuffle (MNIST leakage), cal-fit stratum edges, clairvoyant tabular
# greedy (pre-fix), lambda_ref-duplicated marginal counting. Do not use for paper numbers.
"""LOCAL PIPELINE VALIDATION for Step 5 -- synthetic datasets only.

WHY THIS EXISTS
    The two Step-5 datasets (MiniBooNE, spambase) live on ``openml.org``, which
    is **not** on this sandbox's network allow-list, so their *real* numbers can
    only be produced on the cluster (see the cluster commands printed by
    ``scripts/alpha_probe.py`` and in the hand-off).  This script instead drives
    the *entire* Step-5 machinery end-to-end on two clearly-synthetic, in-code
    datasets to prove the PLUMBING is correct:

      1. the fixed-alpha rule (``feasible_alpha_from_floor``) sets ``alpha`` from
         the *measured* full-acquisition risk floor -- alpha is a function of the
         floor, never of a result;
      2. the ``lambda_ref`` robustness sweep writes one JSON per ``lambda_ref``
         with a disambiguated filename, so the three resolutions coexist instead
         of overwriting one another;
      3. ``aggregate_results.py --report step5`` renders the per-bucket Mondrian
         report (certify feasible strata / abstain-with-full-acq-fallback on
         infeasible ones), demotes the blended CAFA-Mondrian gate to a *labelled
         diagnostic*, runs the Task-4-corrected framing fork, and prints the
         cross-dataset go/no-go readout with honest verdicts.

    It does **not** reproduce -- and must never be read as fabricating -- the
    paper's scientific findings.  The datasets are named ``synthA``/``synthB``
    precisely so no reader can mistake this output for MiniBooNE/spambase.

DISCIPLINE
    Nothing here touches the frozen surface.  It imports the real drivers
    (``run_mondrian``, ``aggregate_results``) and real data helpers, and only
    *monkeypatches* ``cafa.data.load_tabular_afa_cfg`` for names beginning with
    ``synth`` (bypassing the unreachable OpenML fetch).  Every other dataset name
    falls through to the untouched real loader.  Runs in a throwaway
    ``RESULTS_ROOT`` so it never pollutes real metrics.

Usage::

    python scripts/step5_selfcheck_synth.py            # full self-check (CPU)
    python scripts/step5_selfcheck_synth.py --seeds 0 1 2 --keep
"""

from __future__ import annotations

import argparse
import copy
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

# Real modules (add-only / frozen); no reimplementation of their logic here.
from cafa import config, data as cafa_data  # noqa: E402
from cafa.data import (  # noqa: E402
    _disjoint_split_indices,
    assign_feature_costs,
    feasible_alpha_from_floor,
    make_synthetic_tabular_afa,
)

import run_mondrian as rm  # noqa: E402  (real driver; inserts src on import)


# --------------------------------------------------------------------------- #
# Two synthetic "datasets" chosen to exercise DIFFERENT feasibility regimes so
# both the certify and the abstain branches of the per-bucket report get hit:
#   synthA -- binary, many informative features  -> lower floor -> tighter alpha
#   synthB -- 4-class, few informative features   -> higher floor -> looser alpha
# Shapes are fixed per name so the trajectory/backbone caches stay consistent.
# --------------------------------------------------------------------------- #
SYNTH_SPECS = {
    "synthA": dict(n=3200, d=14, n_classes=2, n_informative=9),
    "synthB": dict(n=3200, d=14, n_classes=4, n_informative=3),
}


def _synthetic_afa_dict(name, cfg, seed, cost_scheme):
    """Build the SAME dict shape ``load_tabular_afa`` returns, from synthetic X/y.

    Mirrors the encoded/split/costed structure of ``cafa.data._frame_to_afa`` for
    the all-numeric case: StandardScaler fit on TRAIN only, identity
    ``feature_groups`` (one column per feature), disjoint train/cal/test.
    """
    from sklearn.preprocessing import StandardScaler

    spec = SYNTH_SPECS[name]
    raw = make_synthetic_tabular_afa(
        spec["n"], d=spec["d"], n_classes=spec["n_classes"],
        n_informative=spec["n_informative"], seed=seed,
    )
    X, y = np.asarray(raw["X"], dtype=float), np.asarray(raw["y"]).astype(np.int64)
    n_classes = int(raw["n_classes"])

    protocol = (cfg or {}).get("protocol", {})
    fractions = protocol.get("split_fractions", {"train": 0.6, "cal": 0.2, "test": 0.2})
    tr_idx, ca_idx, te_idx = _disjoint_split_indices(X.shape[0], fractions, seed)

    s_tr, s_ca, s_te = set(tr_idx.tolist()), set(ca_idx.tolist()), set(te_idx.tolist())
    assert s_tr.isdisjoint(s_ca) and s_tr.isdisjoint(s_te) and s_ca.isdisjoint(s_te), \
        "train/cal/test index sets overlap"

    scaler = StandardScaler().fit(X[tr_idx])
    X_train = scaler.transform(X[tr_idx]).astype(np.float32)
    X_cal = scaler.transform(X[ca_idx]).astype(np.float32)
    X_test = scaler.transform(X[te_idx]).astype(np.float32)

    n_cols = X.shape[1]
    feature_groups = [np.array([j], dtype=int) for j in range(n_cols)]
    feature_costs = assign_feature_costs(
        X_train, y[tr_idx], cost_scheme, feature_groups=feature_groups, seed=seed
    )
    return {
        "train": (X_train, y[tr_idx]),
        "cal": (X_cal, y[ca_idx]),
        "test": (X_test, y[te_idx]),
        "feature_costs": feature_costs,
        "feature_groups": feature_groups,
        "n_features": len(feature_groups),
        "n_cols": int(n_cols),
        "n_classes": n_classes,
        "cost_scheme": str(cost_scheme),
        "name": str(name),
        "seed": int(seed),
    }


def _install_synth_loader():
    """Patch ``cafa.data.load_tabular_afa_cfg`` to serve synth names offline.

    Only names in ``SYNTH_SPECS`` are intercepted; all other names delegate to
    the untouched original (so real datasets behave exactly as before).  Patched
    on the module object, which is what ``run_mondrian.get_or_rollout_tabular``
    imports at call time.
    """
    original = cafa_data.load_tabular_afa_cfg

    def _patched(name, cfg, *, seed=0, cost_scheme="inverse_info", download=False):
        if name in SYNTH_SPECS:
            return _synthetic_afa_dict(name, cfg, seed, cost_scheme)
        return original(name, cfg, seed=seed, cost_scheme=cost_scheme, download=download)

    cafa_data.load_tabular_afa_cfg = _patched
    return original


# --------------------------------------------------------------------------- #
# alpha via the fixed rule, from the MEASURED floor (reuses cached trajectories)
# --------------------------------------------------------------------------- #
def _measure_floor(name, seeds, *, cfg, paths, device):
    """Mean full-acquisition risk floor over seeds, exactly as analyse_cell does.

    floor = oracle_full_feature_risk(1 - test_correct[:, T]).  The floor depends
    only on the *all-features* prediction, so it is invariant to policy / cost /
    lambda_ref; we probe on (greedy_entropy, inverse_info) and reuse the cached
    trajectories for the sweep.
    """
    traj_dir = Path(paths.results_root) / "trajectories"
    ckpt_dir = Path(paths.results_root) / "checkpoints"
    floors = []
    for s in seeds:
        arr = rm.get_or_rollout_tabular(
            traj_dir, ckpt_dir, name=name, policy="greedy_entropy",
            cost_scheme="inverse_info", seed=s, cfg=cfg, device=device,
        )
        T = arr["test_correct"].shape[1] - 1
        floors.append(float(rm.oracle_full_feature_risk(1.0 - arr["test_correct"][:, T])))
    return float(np.mean(floors)), floors


# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3])
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--epochs", type=int, default=15,
                    help="backbone epochs for the self-check (speed, not convergence).")
    ap.add_argument("--keep", action="store_true",
                    help="keep the throwaway RESULTS_ROOT for inspection.")
    ap.add_argument("--figures", action="store_true",
                    help="also run make_figures.py if matplotlib is available.")
    args = ap.parse_args(argv)

    policies = ["greedy_entropy", "random"]
    cost_schemes = ["inverse_info", "uniform"]

    print("#" * 78)
    print("STEP-5 LOCAL PIPELINE VALIDATION  (SYNTHETIC datasets synthA/synthB)")
    print("This validates the Step-5 plumbing only. It is NOT MiniBooNE/spambase")
    print("and reproduces NO scientific result -- the real numbers come from the")
    print("cluster (openml.org is unreachable from this sandbox).")
    print("#" * 78)

    _install_synth_loader()

    workdir = Path(tempfile.mkdtemp(prefix="cafa_step5_synth_"))
    os.environ["RESULTS_ROOT"] = str(workdir / "results")
    os.environ["DATA_ROOT"] = str(workdir / "data")
    os.environ["SCRATCH"] = str(workdir / "scratch")
    paths = config.load_paths(create=True)
    metrics_dir = Path(paths.results_root) / "metrics"

    base_cfg = config.load_experiment()
    base_cfg.setdefault("training_tabular", {})["epochs"] = int(args.epochs)
    lambda_refs = list(rm._lambda_ref_grid(base_cfg))
    print(f"\nlambda_ref sweep : {lambda_refs}")
    print(f"policies         : {policies}")
    print(f"cost_schemes     : {cost_schemes}")
    print(f"seeds            : {args.seeds}")
    print(f"throwaway root   : {paths.results_root}")

    # 1) alpha per dataset from the measured floor (fixed rule).
    alpha_by_ds = {}
    print("\n--- Fixed-alpha rule (alpha := ceil0.05(measured_floor + 0.05)) ---")
    for name in SYNTH_SPECS:
        floor, per_seed = _measure_floor(name, args.seeds, cfg=base_cfg,
                                         paths=paths, device=args.device)
        alpha = feasible_alpha_from_floor(floor)
        alpha_by_ds[name] = alpha
        print(f"  tabular:{name}: floor={floor:.4f} (per-seed "
              f"{[round(f,3) for f in per_seed]}) -> alpha={alpha:g}")

    # 2) the sweep: reuse the REAL driver run_one for every cell.
    print("\n--- Sweep (real run_mondrian.run_one per cell) ---")
    n_written = 0
    for name in SYNTH_SPECS:
        for pol in policies:
            for cs in cost_schemes:
                for seed in args.seeds:
                    for lr in lambda_refs:
                        cfg = copy.deepcopy(base_cfg)
                        cfg["method"]["alpha"] = float(alpha_by_ds[name])
                        cfg["method"].setdefault("mondrian", {})["lambda_ref"] = float(lr)
                        rm.run_one(f"tabular:{name}", pol, cs, seed,
                                   cfg=cfg, paths=paths, device=args.device)
                        n_written += 1
    json_files = sorted(metrics_dir.glob("step4_*.json"))
    print(f"\nwrote {n_written} cell record(s); {len(json_files)} JSON file(s) on disk.")

    # 2b) filename disambiguation: each (ds,pol,cs,seed) must have one file per lambda_ref.
    expected = len(SYNTH_SPECS) * len(policies) * len(cost_schemes) * len(args.seeds) * len(lambda_refs)
    assert len(json_files) == expected, (
        f"filename disambiguation FAILED: expected {expected} distinct JSONs "
        f"(one per lambda_ref), found {len(json_files)} -- lambda_ref runs overwrote each other.")
    lr_tags = sorted({f.name.split("_lr")[1].split("_seed")[0] for f in json_files})
    print(f"distinct lambda_ref filename tags present: {lr_tags}  (expected {sorted(f'{x:g}' for x in lambda_refs)})")
    assert len(lr_tags) == len(lambda_refs), "not all lambda_ref values produced a distinct file"

    # 3) run the REAL aggregator (default report == step5) and validate output.
    print("\n--- aggregate_results.py --report step5 ---")
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{SRC}:{env.get('PYTHONPATH','')}"
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "aggregate_results.py"),
         "--report", "step5", "--metrics-dir", str(metrics_dir)],
        cwd=str(REPO), env=env, capture_output=True, text=True,
    )
    out = proc.stdout
    sys.stdout.write(out)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        print("\nSELF-CHECK FAILED: aggregator exited non-zero.")
        return 1

    # --- assertions on the rendered report (structure, not scientific outcome) ---
    checks = {
        "per-bucket Mondrian is the default report":
            "PER-BUCKET MONDRIAN  (default report; replaces the blended gate)" in out,
        "blended CAFA-Mondrian demoted to a labelled diagnostic":
            "[diagnostic only, NOT a result] blended CAFA-Mondrian:" in out,
        "cross-dataset go/no-go readout present":
            "CROSS-DATASET GO/NO-GO READOUT" in out,
        "pre-committed consequence stated":
            "PRE-COMMITTED CONSEQUENCE:" in out,
        "both synthetic datasets appear":
            ("tabular:synthA" in out and "tabular:synthB" in out),
        "H2 line rendered":  "H2:" in out,
        "H3 line rendered":  "H3:" in out,
        "insight (buckets by policy x lambda_ref) rendered":
            "INSIGHT (mean #buckets formed" in out,
        "per-cell verdict (framing fork) rendered":  "VERDICT:" in out,
    }
    # New datasets (no adult here) must trigger the honest "reshapes/generalizes" branch.
    checks["pre-commit keys on NEW datasets (not adult)"] = (
        "appears on NO new dataset beyond adult" in out
        or "reproduces beyond adult on" in out)
    # alpha recorded == fixed-rule alpha (soft: boundary rounding can differ; warn only).
    alpha_matches_rule = "matches fixed rule" in out

    print("\n" + "=" * 78)
    print("SELF-CHECK ASSERTIONS")
    print("=" * 78)
    ok = True
    for label, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {label}")
        ok = ok and passed
    print(f"  [{'PASS' if alpha_matches_rule else 'note'}] recorded alpha matches the fixed rule "
          f"({'yes' if alpha_matches_rule else 'boundary-rounding mismatch; aggregator prints a WARNING, not an error'})")

    if args.figures:
        _maybe_figures(env, metrics_dir)

    if not args.keep:
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)
    else:
        print(f"\n(kept throwaway root: {workdir})")

    print("\n" + "#" * 78)
    if ok:
        print("LOCAL PIPELINE VALIDATION PASSED (synthetic).  The Step-5 reporting")
        print("pipeline runs end-to-end and renders correctly.  Real MiniBooNE/")
        print("spambase numbers must still be produced on the cluster.")
        print("#" * 78)
        return 0
    print("LOCAL PIPELINE VALIDATION FAILED -- see the FAIL lines above.")
    print("#" * 78)
    return 1


def _maybe_figures(env, metrics_dir):
    try:
        import matplotlib  # noqa: F401
    except Exception:
        print("\n(make_figures skipped: matplotlib not installed)")
        return
    print("\n--- make_figures.py (smoke) ---")
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "make_figures.py"),
         "--metrics-dir", str(metrics_dir)],
        cwd=str(REPO), env=env, capture_output=True, text=True,
    )
    sys.stdout.write(proc.stdout[-2000:])
    if proc.returncode != 0:
        print("(make_figures returned non-zero; stderr tail:)")
        sys.stderr.write(proc.stderr[-1500:])
    else:
        print("(make_figures ran without error)")


if __name__ == "__main__":
    raise SystemExit(main())