#!/usr/bin/env python
"""Aggregate per-seed metrics JSONs.

Two modes:

* **Step 4 (default, bare invocation).** Reads every
  ``${RESULTS_ROOT}/metrics/step4_{dataset}_{policy}_{scheme}_seed{seed}.json``
  written by ``scripts/run_mondrian.py``, groups by
  ``(dataset, policy, cost_scheme)``, and for each cell prints the **H2 table**
  (per method: validity = fraction of seeds respecting alpha, mean realized risk,
  mean realized cost), the per-bucket marginal-vs-Mondrian risk with the
  full-acquisition fallback, and the **framing-fork readout** (H2 cost verdict +
  H3-cheap stratum verdict + which paper the evidence points to).

      python scripts/aggregate_results.py
      python scripts/aggregate_results.py --dataset tabular:adult --cost-scheme inverse_info

* **Legacy G2 (``--legacy-g2``).** The original Step-3 gate: reads
  ``${RESULTS_ROOT}/metrics/{dataset}_{backbone}_seed{seed}.json`` and reports

      violation_fraction = (# seeds with realized_risk > alpha) / (# seeds)
      GATE: violation_fraction <= delta

  Non-certifying seeds (lambda_idx is None) are counted as non-violations,
  matching the ``run_experiment.py`` summary convention.

      python scripts/aggregate_results.py --legacy-g2 --dataset mnist --backbone greedy_entropy
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent.parent / "src"))

from cafa import config  # noqa: E402


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--legacy-g2", action="store_true",
                   help="Run the original Step-3 G2 gate instead of Step-4 aggregation.")
    # Filters (Step-4) / selectors (legacy).
    p.add_argument("--dataset", default=None,
                   help="Filter to one dataset, e.g. mnist or tabular:adult. "
                        "Legacy mode defaults to 'mnist'.")
    p.add_argument("--policy", default=None,
                   help="Step-4: filter to one policy (greedy_entropy|random).")
    p.add_argument("--cost-scheme", default=None,
                   help="Step-4: filter to one cost scheme (inverse_info|random|uniform).")
    p.add_argument("--backbone", default="greedy_entropy",
                   help="Legacy G2 only: backbone/policy tag in the filename.")
    p.add_argument(
        "--metrics-dir",
        default=None,
        help="Override metrics dir (default: ${RESULTS_ROOT}/metrics).",
    )
    return p.parse_args(argv)


def _resolve_metrics_dir(args):
    if args.metrics_dir is not None:
        return Path(args.metrics_dir)
    paths = config.load_paths(create=False)
    return Path(paths.results_root) / "metrics"


def run_g2_legacy(args) -> int:
    dataset = args.dataset or "mnist"
    backbone = args.backbone

    cfg = config.load_experiment()
    protocol = cfg.get("protocol", {})
    method_cfg = cfg.get("method", {})
    alpha = float(method_cfg.get("alpha", 0.10))
    delta = float(method_cfg.get("delta", 0.10))
    seeds = list(protocol.get("seeds", list(range(20))))

    metrics_dir = _resolve_metrics_dir(args)

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
        fp = metrics_dir / f"{dataset}_{backbone}_seed{s}.json"
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


# --------------------------------------------------------------------------- #
# Step 4: H2 table + per-bucket + framing-fork readout
# --------------------------------------------------------------------------- #
# Fixed display order; the "*" methods have a validity guarantee.
_METHOD_ORDER = [
    ("cafa_marginal", "CAFA-marginal", True),
    ("cafa_mondrian", "CAFA-Mondrian", True),
    ("plugin_threshold", "plugin", False),
    ("__fixed__", None, False),   # expands to every fixed_conf_* present
    ("__budget__", None, False),  # expands to every budget_* present
    ("oracle_cheapest_valid", "oracle-cheapest", False),
    ("oracle_full_feature", "oracle-full", False),
]


def _mean(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return (sum(xs) / len(xs)) if xs else float("nan")


def _load_step4(metrics_dir, args):
    recs = defaultdict(list)  # (dataset, policy, cost_scheme) -> [rec, ...]
    for fp in sorted(glob.glob(str(metrics_dir / "step4_*.json"))):
        try:
            rec = json.loads(Path(fp).read_text())
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: could not read {fp}: {exc}", file=sys.stderr)
            continue
        ds, pol, cs = rec.get("dataset"), rec.get("policy"), rec.get("cost_scheme")
        if args.dataset and ds != args.dataset:
            continue
        if args.policy and pol != args.policy:
            continue
        if args.cost_scheme and cs != args.cost_scheme:
            continue
        recs[(ds, pol, cs)].append(rec)
    return recs


def _expand_methods(recs):
    """Ordered (key, label, guaranteed) list, expanding fixed_/budget_ families."""
    present = set()
    for r in recs:
        present.update(r.get("methods", {}).keys())
    fixed = sorted(m for m in present if m.startswith("fixed_conf_"))
    budget = sorted((m for m in present if m.startswith("budget_")),
                    key=lambda s: float(s.split("_")[-1]))
    out = []
    for key, label, guar in _METHOD_ORDER:
        if key == "__fixed__":
            out += [(m, m.replace("fixed_conf_", "fixed@"), False) for m in fixed]
        elif key == "__budget__":
            out += [(m, m.replace("budget_", "budget@"), False) for m in budget]
        elif any(key in r.get("methods", {}) for r in recs):
            out.append((key, label, guar))
    return out


def _h2_table(recs, alpha, delta):
    """Return rows: (label, guaranteed, n_seeds, valid_frac, mean_risk, mean_cost, viol_frac)."""
    rows = []
    for key, label, guar in _expand_methods(recs):
        risks, costs = [], []
        for r in recs:
            m = r.get("methods", {}).get(key)
            if not m:
                continue
            risks.append(m.get("realized_risk"))
            costs.append(m.get("realized_cost"))
        rr = [x for x in risks if x is not None and not (isinstance(x, float) and math.isnan(x))]
        n = len(rr)
        n_viol = sum(1 for x in rr if x > alpha)
        valid_frac = (1.0 - n_viol / n) if n else float("nan")
        rows.append((label, guar, n, valid_frac, _mean(risks), _mean(costs),
                     (n_viol / n) if n else float("nan")))
    return rows


def _print_h2_table(rows, alpha, delta):
    print(f"{'method':<16}{'grt':>4}{'seeds':>7}{'valid':>8}{'meanRisk':>11}"
          f"{'meanCost':>11}{'gate':>7}")
    print("-" * 64)
    for label, guar, n, valid, mrisk, mcost, viol in rows:
        # A guaranteed method 'passes' its own gate if violation frac <= delta.
        # Distinguish "abstained on every seed" (no certification) from a real
        # gate failure.
        gate = ""
        if guar:
            if n == 0 or math.isnan(viol):
                gate = "abst"
            else:
                gate = "ok" if viol <= delta else "FAIL"
        star = "*" if guar else " "
        valid_s = "  --  " if math.isnan(valid) else f"{valid:>8.3f}"
        mrisk_s = f"{'--':>11}" if math.isnan(mrisk) else f"{mrisk:>11.5f}"
        mcost_s = f"{'--':>11}" if math.isnan(mcost) else f"{mcost:>11.4f}"
        print(f"{label:<16}{star:>4}{n:>7}{valid_s}{mrisk_s}{mcost_s}{gate:>7}")
    print("-" * 64)
    print(f"validity = fraction of seeds with realized_risk <= alpha={alpha}; "
          f"gate (grt): viol_frac<=delta={delta}; 'abst' = abstained on every seed")


def _per_bucket_summary(recs, alpha):
    """Mean marginal vs Mondrian risk per bucket, plus mean full-acq fallback."""
    marg = defaultdict(list); mond = defaultdict(list); fb = defaultdict(list)
    for r in recs:
        pb = r.get("per_bucket", {})
        for b, v in (pb.get("marginal_risk") or {}).items():
            marg[b].append(v)
        for b, v in (pb.get("mondrian_risk") or {}).items():
            mond[b].append(v)
        for b, v in (r.get("fallback_full_acq_risk_by_bucket") or {}).items():
            fb[b].append(v)
    buckets = sorted(set(marg) | set(mond) | set(fb), key=lambda s: int(s))
    rows = []
    for b in buckets:
        rows.append((b, _mean(marg.get(b, [])), _mean(mond.get(b, [])),
                     _mean(fb.get(b, []))))
    return rows


def _print_per_bucket(rows, alpha):
    print(f"{'bucket':>7}{'marg_risk':>12}{'mond_risk':>12}{'fallback':>12}   note")
    print("-" * 60)
    for b, mr, mo, fbk in rows:
        note = ""
        if not math.isnan(mr) and mr > alpha:
            note = "marg > alpha"
            if not math.isnan(fbk) and fbk > alpha:
                note += "; full-acq ALSO > alpha (infeasible)"
            elif math.isnan(mo):
                note += "; Mondrian abstains"
        fbs = f"{'--':>12}" if math.isnan(fbk) else f"{fbk:>12.5f}"
        mos = f"{'(abstain)':>12}" if math.isnan(mo) else f"{mo:>12.5f}"
        print(f"{b:>7}{mr:>12.5f}{mos}{fbs}   {note}")
    print("-" * 60)
    print(f"(alpha = {alpha}; 'fallback' = full-acquisition risk on that stratum)")


def _framing_fork(dataset, policy, scheme, rows, bucket_rows, alpha, delta):
    """Print the per-cell framing-fork verdict from aggregated numbers."""
    by = {r[0]: r for r in rows}
    marg = by.get("CAFA-marginal")
    plug = by.get("plugin")
    full = by.get("oracle-full")
    floor = by.get("oracle-cheapest")

    print()
    print(f"FRAMING FORK  --  {dataset} | policy={policy} | cost_scheme={scheme}")
    print("." * 64)

    if marg is None:
        print("  (no CAFA-marginal record in this cell)")
        return

    marg_n = marg[2]; marg_viol = marg[6]; marg_cost = marg[5]; marg_risk = marg[4]
    full_risk = full[4] if (full and not math.isnan(full[4])) else float("nan")

    # Distinguish three states for CAFA-marginal:
    #   (a) never certifies on any seed  -> abstention, usually because alpha is
    #       below the achievable error floor (full-acquisition risk > alpha);
    #   (b) certifies and respects alpha -> SAFE;
    #   (c) certifies but violates alpha -> genuine violation.
    all_abstain = (marg_n == 0) or math.isnan(marg_viol)
    infeasible_alpha = (not math.isnan(full_risk)) and full_risk > alpha
    h2_safe = (not all_abstain) and marg_viol <= delta

    if all_abstain:
        floor_txt = (f"full-acquisition risk={full_risk:.5f} > alpha={alpha:g}"
                     if not math.isnan(full_risk) else "no full-acq reference")
        print(f"  H2 safety : CAFA-marginal ABSTAINS on every seed "
              f"-- no threshold certifies "
              f"({'alpha INFEASIBLE: ' + floor_txt if infeasible_alpha else floor_txt}).")
    else:
        print(f"  H2 safety : CAFA-marginal respects alpha on "
              f"{(1 - marg_viol) * 100:.0f}% of {marg_n} certified seeds "
              f"-> {'SAFE (<= 1-delta)' if h2_safe else 'UNSAFE (violates on > delta)'}")

    # Cost verdict (only meaningful when CAFA certifies).
    if all_abstain:
        print(f"  H2 cost   : n/a -- CAFA never certifies "
              f"(full-acq risk floor={full_risk:.5f}; even acquiring everything "
              f"stays {'above' if infeasible_alpha else 'at/below'} alpha).")
    else:
        cost_line = f"  H2 cost   : CAFA-marginal mean cost={marg_cost:.3f}"
        if full and not math.isnan(full[5]):
            frac = marg_cost / full[5] if full[5] else float("nan")
            cost_line += f"  (full-acq={full[5]:.3f}, ratio={frac:.2f})"
        if floor and not math.isnan(floor[5]):
            cost_line += f"  (oracle floor={floor[5]:.3f})"
        print(cost_line)

    plugin_abstain = plug is None or plug[2] == 0 or math.isnan(plug[6])
    plugin_unsafe = (not plugin_abstain) and plug[6] > delta
    if plug is not None:
        if plugin_abstain:
            print("  plugin    : abstains on all seeds (no grid point meets alpha).")
        else:
            print(f"  plugin    : cost={plug[5]:.3f} risk={plug[4]:.5f} "
                  f"-> {'VIOLATES alpha' if plugin_unsafe else 'respects alpha'}")

    real_cost_win = (
        h2_safe and full is not None and not math.isnan(full[5])
        and full[5] > 0 and (marg_cost / full[5]) < 0.85
    )

    # H3-cheap verdict: on which stratum does marginal under-cover?
    n_buckets_seen = len(bucket_rows)
    under = [(b, mr, fbk) for (b, mr, mo, fbk) in bucket_rows
             if not math.isnan(mr) and mr > alpha]
    if all_abstain:
        h3 = ("n/a -- marginal certifies nothing to stratify"
              + ("; note only 1 score-bucket formed (no stratification possible)"
                 if n_buckets_seen <= 1 else ""))
        cheap_under = False
    elif not under:
        h3 = "no bucket shows marginal under-coverage (marginal is uniformly safe)"
        cheap_under = False
    else:
        idxs = [int(b) for b, _, _ in under]
        nb = max(int(b) for (b, *_ ) in bucket_rows) if bucket_rows else 0
        cheap_under = min(idxs) <= (nb // 3)  # under-coverage reaches a low/cheap stratum
        infeasible = [b for b, _mr, fbk in under
                      if not math.isnan(fbk) and fbk > alpha]
        where = "CHEAP/shallow" if cheap_under else "HARD/deep"
        h3 = (f"marginal under-covers buckets {idxs} (of 0..{nb}) -> {where} stratum")
        if infeasible:
            h3 += (f"; buckets {infeasible} remain > alpha even at full acquisition "
                   f"(genuinely infeasible -> honest abstention)")
    print(f"  H3-cheap  : {h3}")

    print("  VERDICT   :", end=" ")
    if all_abstain:
        if infeasible_alpha:
            print(f"alpha={alpha:g} is INFEASIBLE here (achievable floor "
                  f"{full_risk:.3f} > alpha) -- this cell cannot decide H2/H3. "
                  "Raise alpha above the floor (or use a dataset where alpha is "
                  "achievable), then re-run this cell.")
        else:
            print("CAFA certifies nothing despite a feasible floor -- check the "
                  "grid / calibration split before drawing conclusions.")
    elif not h2_safe:
        print("CAFA-marginal certifies but violates on > delta seeds -> lean on "
              "CAFA-Mondrian; paper = per-stratum validity + honest abstention.")
    elif real_cost_win and plugin_unsafe:
        print("real cost win AND plugin unsafe -> EFFICIENCY paper "
              "(cost savings + per-budget validity).")
    elif cheap_under:
        print("cost win modest; under-coverage hits a CHEAP stratum "
              "-> Mondrian-necessity paper (per-budget validity, synthetic-style).")
    else:
        print("cost win modest; under-coverage stays on the HARD/deep stratum "
              "(MNIST-style) -> per-budget validity + honest abstention paper.")


def run_step4(args) -> int:
    metrics_dir = _resolve_metrics_dir(args)
    print(f"metrics dir : {metrics_dir}")
    recs = _load_step4(metrics_dir, args)
    if not recs:
        print("No step4_*.json files found yet.")
        print("Run scripts/run_mondrian.py first (see the run-list), then re-run this.")
        print("Data legs of the framing fork (H2 cost, H3-cheap stratum) are PENDING "
              "the cluster run.")
        return 1

    n_cells = len(recs)
    print(f"found {sum(len(v) for v in recs.values())} record(s) across "
          f"{n_cells} cell(s).")

    for (ds, pol, cs) in sorted(recs, key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
        cell = recs[(ds, pol, cs)]
        alpha = float(cell[0].get("alpha", 0.10))
        delta = float(cell[0].get("delta", 0.10))
        print()
        print("=" * 64)
        print(f"CELL  dataset={ds}  policy={pol}  cost_scheme={cs}  "
              f"(seeds={len(cell)})")
        print("=" * 64)
        rows = _h2_table(cell, alpha, delta)
        _print_h2_table(rows, alpha, delta)
        print()
        bucket_rows = _per_bucket_summary(cell, alpha)
        _print_per_bucket(bucket_rows, alpha)
        _framing_fork(ds, pol, cs, rows, bucket_rows, alpha, delta)

    print()
    print("=" * 64)
    print("Reminder: CAFA-marginal / CAFA-Mondrian carry the LTT/Mondrian validity")
    print("guarantee; plugin / fixed@ / budget@ do not; oracle-* are non-deployable")
    print("reference bounds (they see test labels).")
    print("=" * 64)
    return 0


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.legacy_g2:
        return run_g2_legacy(args)
    return run_step4(args)


if __name__ == "__main__":
    raise SystemExit(main())