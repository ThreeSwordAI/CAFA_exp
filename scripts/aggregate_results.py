#!/usr/bin/env python
"""Aggregate per-seed metrics JSONs and print the G2 gate verdict.

Reads ``${RESULTS_ROOT}/metrics/{dataset}_{backbone}_seed{seed}.json`` for every
protocol seed, prints a per-seed table, and reports the G2 decision:

    violation_fraction = (# seeds with realized_risk > alpha) / (# certified seeds)
    GATE: violation_fraction <= delta

Non-certifying seeds (lambda_idx is None) are reported separately and counted as
non-violations, matching the ``run_experiment.py`` summary convention.

Usage:
    python scripts/aggregate_results.py --dataset mnist --backbone greedy_entropy
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent.parent / "src"))

from cafa import config  # noqa: E402


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", default="mnist")
    p.add_argument("--backbone", default="greedy_entropy")
    p.add_argument(
        "--metrics-dir",
        default=None,
        help="Override metrics dir (default: ${RESULTS_ROOT}/metrics).",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    cfg = config.load_experiment()
    protocol = cfg.get("protocol", {})
    method_cfg = cfg.get("method", {})
    alpha = float(method_cfg.get("alpha", 0.10))
    delta = float(method_cfg.get("delta", 0.10))
    seeds = list(protocol.get("seeds", list(range(20))))

    if args.metrics_dir is not None:
        metrics_dir = Path(args.metrics_dir)
    else:
        paths = config.load_paths(create=False)
        metrics_dir = Path(paths.results_root) / "metrics"

    print(f"metrics dir : {metrics_dir}")
    print(f"alpha={alpha}  delta={delta}  seeds={len(seeds)}")
    print("-" * 78)
    print(f"{'seed':>4}  {'cert':>4}  {'lam':>4}  {'nval':>4}  "
          f"{'realized_risk':>13}  {'realized_cost':>13}  {'stop_depth':>10}")
    print("-" * 78)

    n_found = 0
    n_certified = 0
    n_violation = 0
    n_missing = 0
    risks, costs, depths = [], [], []
    missing_seeds, uncertified_seeds = [], []

    for s in seeds:
        fp = metrics_dir / f"{args.dataset}_{args.backbone}_seed{s}.json"
        if not fp.is_file():
            n_missing += 1
            missing_seeds.append(s)
            print(f"{s:>4}  {'--':>4}  {'--':>4}  {'--':>4}  "
                  f"{'MISSING':>13}  {'--':>13}  {'--':>10}")
            continue

        with open(fp) as f:
            rec = json.load(f)
        n_found += 1

        sel = rec.get("selection", {})
        rt = rec.get("realized_test", {})
        certified = bool(sel.get("certified", sel.get("lambda_idx") is not None))
        lam = sel.get("lambda_idx")
        nval = sel.get("n_valid")

        if certified and rt.get("realized_risk") is not None:
            n_certified += 1
            rr = float(rt["realized_risk"])
            rc = float(rt["realized_cost"])
            sd = float(rt.get("mean_stop_depth", rc))
            risks.append(rr)
            costs.append(rc)
            depths.append(sd)
            viol = rr > alpha
            if viol:
                n_violation += 1
            flag = "  <-- VIOLATION" if viol else ""
            print(f"{s:>4}  {'yes':>4}  {str(lam):>4}  {str(nval):>4}  "
                  f"{rr:>13.5f}  {rc:>13.4f}  {sd:>10.4f}{flag}")
        else:
            uncertified_seeds.append(s)
            print(f"{s:>4}  {'no':>4}  {str(lam):>4}  {str(nval):>4}  "
                  f"{'(no cert)':>13}  {'--':>13}  {'--':>10}")

    print("-" * 78)

    if n_missing:
        print(f"WARNING: {n_missing} seed(s) missing: {missing_seeds}")
    if uncertified_seeds:
        print(f"note: {len(uncertified_seeds)} seed(s) did not certify "
              f"(counted as non-violations): {uncertified_seeds}")

    denom = n_found  # all seeds with a result file count toward the protocol
    if denom == 0:
        print("No result files found — nothing to aggregate.")
        return 1

    violation_fraction = n_violation / denom
    gate_ok = violation_fraction <= delta

    mean_cost = sum(costs) / len(costs) if costs else float("nan")
    mean_depth = sum(depths) / len(depths) if depths else float("nan")
    max_risk = max(risks) if risks else float("nan")

    print()
    print("=" * 78)
    print("G2 SUMMARY")
    print("=" * 78)
    print(f"seeds with results     : {n_found}/{len(seeds)}")
    print(f"certified seeds        : {n_certified}")
    print(f"violations (risk>alpha): {n_violation}")
    print(f"violation_fraction     : {violation_fraction:.4f}   (gate: <= delta = {delta})")
    print(f"max realized_risk      : {max_risk:.5f}   (alpha = {alpha})")
    print(f"mean realized_cost     : {mean_cost:.4f}   (of 49 features)")
    print(f"mean stop_depth        : {mean_depth:.4f}")
    print("-" * 78)
    verdict = "PASS" if (gate_ok and n_missing == 0) else ("PASS*" if gate_ok else "FAIL")
    note = "" if n_missing == 0 else "   (* incomplete: some seeds missing)"
    print(f"G2 GATE: {verdict}{note}")
    print("=" * 78)
    return 0 if gate_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())