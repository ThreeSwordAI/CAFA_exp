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
    p.add_argument(
        "--report",
        choices=["step4", "step5"],
        default="step5",
        help="Which aggregation to run (default: step5 = per-bucket Mondrian + "
             "cross-dataset go/no-go readout; step4 = original per-cell H2 view). "
             "Ignored when --legacy-g2 is set.",
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
    else:
        # caveat §12.6 fix: the cost-win magnitude (from the ratio) and the
        # plugin's safety are INDEPENDENT facts and must not be conflated.
        # Reaching this branch only means we are not in the (real cost win AND
        # plugin unsafe) case -- the cost win may still be large, with the plugin
        # merely happening to be safe in this regime.  State each separately.
        if real_cost_win:
            cost_phrase = ("cost win is LARGE (ratio < 0.85), but the plugin also "
                           "happens to be safe in this regime")
        else:
            cost_phrase = "cost win is modest (ratio >= 0.85)"
        if cheap_under:
            print(f"{cost_phrase}; under-coverage hits a CHEAP stratum "
                  "-> Mondrian-necessity paper (per-budget validity, synthetic-style).")
        else:
            print(f"{cost_phrase}; under-coverage stays on the HARD/deep stratum "
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


# --------------------------------------------------------------------------- #
# Step 5: lambda_ref-aware loading, per-bucket Mondrian (default), blended-gate
# demotion, and the pre-committed cross-dataset go/no-go readout.
#
# All Step-5 additions below are NEW symbols; the Step-4 loaders / tables /
# run_step4 above are unchanged (run_step4 stays reachable via --report step4).
# --------------------------------------------------------------------------- #
def _load_step5(metrics_dir, args):
    """Like ``_load_step4`` but keyed by ``(dataset, policy, cost_scheme, lambda_ref)``.

    The Step-5 sweep runs the same ``(dataset, policy, scheme, seed)`` cell at
    several ``lambda_ref`` values; grouping on the ``lambda_ref`` recorded inside
    each JSON keeps them distinct and is robust to filename conventions.
    """
    recs = defaultdict(list)
    for fp in sorted(glob.glob(str(metrics_dir / "step4_*.json"))):
        try:
            rec = json.loads(Path(fp).read_text())
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: could not read {fp}: {exc}", file=sys.stderr)
            continue
        ds, pol, cs = rec.get("dataset"), rec.get("policy"), rec.get("cost_scheme")
        lr = rec.get("lambda_ref")
        if args.dataset and ds != args.dataset:
            continue
        if args.policy and pol != args.policy:
            continue
        if args.cost_scheme and cs != args.cost_scheme:
            continue
        recs[(ds, pol, cs, lr)].append(rec)
    return recs


def _n_buckets_formed(rec):
    """Number of non-empty score-buckets that actually formed in a record.

    The 'policy-hides-failures' insight is about how many strata *form*, not the
    configured ``n_buckets``.  Prefer the per-bucket test sizes; fall back to the
    count of per-bucket marginal entries.
    """
    sizes = rec.get("bucket_sizes_test")
    if isinstance(sizes, dict):
        return sum(1 for v in sizes.values() if v)
    if isinstance(sizes, list):
        return sum(1 for v in sizes if v)
    pb = (rec.get("per_bucket") or {}).get("marginal_risk") or {}
    return len(pb)


def _headline_h2_rows(rows):
    """H2 headline rows with the blended CAFA-Mondrian gate removed (caveat §12.4).

    The single blended CAFA-Mondrian number is a stratum-weighting artifact (it
    can read FAIL on greedy / PASS on random purely from how strata are weighted)
    and must not appear as a headline result.  The per-bucket Mondrian report
    replaces it; the blended figure is shown separately, labeled a diagnostic.
    """
    return [r for r in rows if r[0] != "CAFA-Mondrian"]


def _blended_mondrian_row(rows):
    for r in rows:
        if r[0] == "CAFA-Mondrian":
            return r
    return None


def _mondrian_bucket_report(cell, alpha):
    """Per-bucket Mondrian aggregation across a cell's seeds.

    Returns ``(rows, n_seeds)`` where each row summarises one score-bucket:
    how often Mondrian certified it, the mean certified lambda_idx / risk / cost,
    and the mean full-acquisition fallback risk (the proof of (in)feasibility).
    This is the Step-5 default replacement for the blended gate.
    """
    n_seeds = len(cell)
    seen = defaultdict(int); cert = defaultdict(int)
    lam = defaultdict(list); mrisk = defaultdict(list)
    mcost = defaultdict(list); fb = defaultdict(list)
    for r in cell:
        pb = r.get("per_bucket", {}) or {}
        lidx = pb.get("mondrian_lambda_idx") or {}
        mr = pb.get("mondrian_risk") or {}
        mc = pb.get("mondrian_cost") or {}
        fbk = r.get("fallback_full_acq_risk_by_bucket") or {}
        for b in set(lidx) | set(mr) | set(mc) | set(fbk):
            seen[b] += 1
            li = lidx.get(b)
            if li is not None:
                cert[b] += 1
                lam[b].append(li)
                if mr.get(b) is not None:
                    mrisk[b].append(mr[b])
                if mc.get(b) is not None:
                    mcost[b].append(mc[b])
            if fbk.get(b) is not None:
                fb[b].append(fbk[b])
    rows = []
    for b in sorted(seen, key=lambda s: int(s)):
        rows.append({
            "bucket": b, "seen": seen[b], "cert": cert[b],
            "mean_lambda_idx": _mean(lam[b]),
            "mean_mond_risk": _mean(mrisk[b]),
            "mean_mond_cost": _mean(mcost[b]),
            "mean_fallback": _mean(fb[b]),
        })
    return rows, n_seeds


def _bucket_status(row, alpha):
    """Human-readable per-bucket Mondrian status."""
    fb = row["mean_fallback"]
    infeasible = (not math.isnan(fb)) and fb > alpha
    if row["cert"] == 0:
        return ("ABSTAIN (infeasible: full-acq > alpha)" if infeasible
                else "abstains (no lambda certifies)")
    if row["cert"] < row["seen"]:
        return "partial certification across seeds"
    return "certified"


def _print_mondrian_bucket_report(rows, n_seeds, alpha):
    print("PER-BUCKET MONDRIAN  (default report; replaces the blended gate)")
    print(f"{'bucket':>7}{'cert/seen':>11}{'lam_idx':>9}{'mondRisk':>11}"
          f"{'mondCost':>11}{'fallback':>11}   status")
    print("-" * 78)
    for row in rows:
        cs = f"{row['cert']}/{row['seen']}"
        lam_s = f"{'--':>9}" if math.isnan(row['mean_lambda_idx']) else f"{row['mean_lambda_idx']:>9.1f}"
        mr_s = f"{'--':>11}" if math.isnan(row['mean_mond_risk']) else f"{row['mean_mond_risk']:>11.5f}"
        mc_s = f"{'--':>11}" if math.isnan(row['mean_mond_cost']) else f"{row['mean_mond_cost']:>11.4f}"
        fb_s = f"{'--':>11}" if math.isnan(row['mean_fallback']) else f"{row['mean_fallback']:>11.5f}"
        print(f"{row['bucket']:>7}{cs:>11}{lam_s}{mr_s}{mc_s}{fb_s}   {_bucket_status(row, alpha)}")
    print("-" * 78)
    print(f"(alpha={alpha}; certify feasible strata with their lambda_idx/cost, "
          f"abstain on infeasible strata with the full-acq fallback as proof; "
          f"{n_seeds} seeds)")


def _dataset_floor_alpha(dataset_recs):
    """(floor, alpha, alpha_consistent) for a dataset from its records.

    floor = mean oracle_full_feature realized risk (the full-acquisition
    population risk floor); alpha = the value recorded in the JSONs (checked for
    consistency across the dataset's cells).
    """
    floors, alphas = [], []
    for r in dataset_recs:
        m = (r.get("methods") or {}).get("oracle_full_feature")
        if m and m.get("realized_risk") is not None:
            floors.append(m["realized_risk"])
        if r.get("alpha") is not None:
            alphas.append(float(r["alpha"]))
    floor = _mean(floors)
    alpha = alphas[0] if alphas else float("nan")
    alpha_consistent = (len(set(round(a, 6) for a in alphas)) <= 1) if alphas else True
    return floor, alpha, alpha_consistent


def _cafa_marginal_h2(dataset_recs, policy, cost_scheme, alpha):
    """H2 numbers for CAFA-marginal in one (policy, cost_scheme) regime.

    lambda_ref does not affect the marginal selector, so we aggregate over all
    lambda_ref values (identical trajectories) to use every available seed.
    Returns dict or None if the regime is absent.
    """
    risks, costs, full_costs = [], [], []
    for r in dataset_recs:
        if r.get("policy") != policy or r.get("cost_scheme") != cost_scheme:
            continue
        cm = (r.get("methods") or {}).get("cafa_marginal")
        of = (r.get("methods") or {}).get("oracle_full_feature")
        if cm and cm.get("realized_risk") is not None:
            risks.append(cm["realized_risk"]); costs.append(cm.get("realized_cost"))
        if of and of.get("realized_cost") is not None:
            full_costs.append(of["realized_cost"])
    if not risks:
        return None
    n = len(risks)
    n_viol = sum(1 for x in risks if x > alpha)
    mean_cost = _mean(costs); mean_full = _mean(full_costs)
    ratio = (mean_cost / mean_full) if (mean_full and not math.isnan(mean_full)) else float("nan")
    return {"n": n, "valid_frac": 1.0 - n_viol / n, "mean_cost": mean_cost,
            "mean_full_cost": mean_full, "cost_ratio": ratio}


def _plugin_regime(dataset_recs, policy, cost_scheme, alpha, delta):
    """Whether the plugin is unsafe in one regime: returns 'unsafe'|'safe'|'abstain'|None."""
    risks = []
    for r in dataset_recs:
        if r.get("policy") != policy or r.get("cost_scheme") != cost_scheme:
            continue
        pl = (r.get("methods") or {}).get("plugin_threshold")
        if pl and pl.get("realized_risk") is not None:
            risks.append(pl["realized_risk"])
    if not risks:
        return None
    n_viol = sum(1 for x in risks if x > alpha)
    viol_frac = n_viol / len(risks)
    return "unsafe" if viol_frac > delta else "safe"


def _bucket_counts_by_policy(dataset_recs):
    """{lambda_ref: {policy: mean_n_buckets}} using the primary (inverse_info) scheme.

    Bucketing is on readiness scores, not cost, so the count is cost-scheme
    invariant; we read it off the primary scheme when present, else any scheme.
    """
    grp = defaultdict(lambda: defaultdict(list))  # lr -> policy -> [n_buckets]
    have_primary = any(r.get("cost_scheme") == "inverse_info" for r in dataset_recs)
    for r in dataset_recs:
        if have_primary and r.get("cost_scheme") != "inverse_info":
            continue
        lr = r.get("lambda_ref"); pol = r.get("policy")
        grp[lr][pol].append(_n_buckets_formed(r))
    out = {}
    for lr in sorted(grp, key=lambda x: (x is None, x)):
        out[lr] = {pol: _mean(v) for pol, v in grp[lr].items()}
    return out


def _h3_abstention(dataset_recs, alpha, lambda_refs=(0.7, 0.9)):
    """Does a hard stratum with full-acq fallback > alpha exist where Mondrian abstains?

    Scans the fine-resolution cells (lambda_ref in ``lambda_refs``); returns
    (present: bool, detail: str).
    """
    hits = []
    for lr in lambda_refs:
        cells = defaultdict(list)  # (pol,cs) -> recs at this lr
        for r in dataset_recs:
            if r.get("lambda_ref") == lr:
                cells[(r.get("policy"), r.get("cost_scheme"))].append(r)
        for (pol, cs), cell in cells.items():
            rows, _ = _mondrian_bucket_report(cell, alpha)
            for row in rows:
                fb = row["mean_fallback"]
                if (not math.isnan(fb)) and fb > alpha and row["cert"] == 0:
                    hits.append(f"lr={lr:g}/{pol}: bucket {row['bucket']} "
                                f"fallback={fb:.3f}>alpha, Mondrian abstains")
    if hits:
        return True, "; ".join(hits[:4]) + (" ..." if len(hits) > 4 else "")
    return False, "no stratum with full-acq fallback > alpha at lambda_ref in " + str(list(lambda_refs))


def _cross_dataset_readout(all_recs, alpha_rule):
    """Task 5: pre-committed, honest go/no-go readout across datasets.

    Prints, per dataset: {floor, alpha} (and whether alpha matches the fixed
    rule); H2 (CAFA-marginal validity + cost ratio vs full + which policy regime
    the plugin is unsafe in); H3 (hard-stratum abstention at fine resolution);
    the insight (bucket count by policy at each lambda_ref); and one-line honest
    verdicts on whether each phenomenon reproduces.
    """
    datasets = sorted({k[0] for k in all_recs}, key=str)
    print()
    print("#" * 78)
    print("CROSS-DATASET GO/NO-GO READOUT  (pre-committed; honest)")
    print("#" * 78)

    h3_datasets = []
    for ds in datasets:
        drecs = [r for k, cell in all_recs.items() if k[0] == ds for r in cell]
        # per-dataset delta (consistent across cells)
        delta = float(drecs[0].get("delta", 0.10)) if drecs else 0.10
        floor, alpha, alpha_ok = _dataset_floor_alpha(drecs)
        rule_alpha = alpha_rule(floor) if not math.isnan(floor) else float("nan")

        print()
        print("=" * 78)
        print(f"DATASET: {ds}")
        print("=" * 78)
        floor_s = "n/a" if math.isnan(floor) else f"{floor:.4f}"
        alpha_s = "n/a" if math.isnan(alpha) else f"{alpha:g}"
        rule_s = "n/a" if math.isnan(rule_alpha) else f"{rule_alpha:g}"
        match = "" if math.isnan(rule_alpha) else (
            "  (matches fixed rule)" if abs(rule_alpha - alpha) < 1e-9
            else f"  (WARNING: fixed rule would give {rule_s}; recorded alpha differs)")
        print(f"  floor (full-acq risk) = {floor_s}   alpha = {alpha_s}"
              f"   [rule: ceil0.05(floor+0.05) = {rule_s}]{match}")
        if not alpha_ok:
            print("  WARNING: alpha is not consistent across this dataset's JSONs.")

        # --- H2 (primary = greedy_entropy + inverse_info; plus the random regime).
        prim = _cafa_marginal_h2(drecs, "greedy_entropy", "inverse_info", alpha)
        if prim is None:
            # fall back to whatever greedy regime exists
            prim = (_cafa_marginal_h2(drecs, "greedy_entropy", "uniform", alpha))
        plugin_greedy = _plugin_regime(drecs, "greedy_entropy", "inverse_info", alpha, delta) \
            or _plugin_regime(drecs, "greedy_entropy", "uniform", alpha, delta)
        plugin_random = _plugin_regime(drecs, "random", "inverse_info", alpha, delta) \
            or _plugin_regime(drecs, "random", "uniform", alpha, delta)
        if prim is not None:
            unsafe_where = []
            if plugin_greedy == "unsafe":
                unsafe_where.append("greedy")
            if plugin_random == "unsafe":
                unsafe_where.append("random")
            plug_txt = ("plugin unsafe under " + "+".join(unsafe_where)
                        if unsafe_where else "plugin safe in all measured regimes")
            print(f"  H2: CAFA-marginal valid on {prim['valid_frac']*100:.0f}% of "
                  f"{prim['n']} seeds (>= 1-delta={1-delta:g} required); "
                  f"mean cost={prim['mean_cost']:.3f} vs full={prim['mean_full_cost']:.3f} "
                  f"(ratio={prim['cost_ratio']:.2f}); {plug_txt}.")
        else:
            print("  H2: no CAFA-marginal records for this dataset (cannot assess).")

        # --- H3 (fine-resolution hard-stratum abstention).
        h3_present, h3_detail = _h3_abstention(drecs, alpha)
        print(f"  H3: {'PRESENT' if h3_present else 'absent'} -- {h3_detail}.")
        if h3_present:
            h3_datasets.append(ds)

        # --- The insight (bucket count by policy at each lambda_ref).
        bc = _bucket_counts_by_policy(drecs)
        print("  INSIGHT (mean #buckets formed, by policy x lambda_ref):")
        collapse_note = []
        for lr, per_pol in bc.items():
            lr_s = "?" if lr is None else f"{lr:g}"
            g = per_pol.get("greedy_entropy"); rnd = per_pol.get("random")
            g_s = "--" if g is None or math.isnan(g) else f"{g:.1f}"
            r_s = "--" if rnd is None or math.isnan(rnd) else f"{rnd:.1f}"
            print(f"      lambda_ref={lr_s}:  greedy={g_s}   random={r_s}")
            if lr is not None and abs(lr - 0.5) < 1e-9 and g is not None and not math.isnan(g) and g <= 1.5:
                collapse_note.append("greedy collapses toward 1 bucket at lambda_ref=0.5")
        # policy-hides-failures = greedy fewer buckets than random (where both present)
        fewer = [lr for lr, pp in bc.items()
                 if pp.get("greedy_entropy") is not None and pp.get("random") is not None
                 and not math.isnan(pp["greedy_entropy"]) and not math.isnan(pp["random"])
                 and pp["greedy_entropy"] < pp["random"]]

        # --- Honest per-dataset verdicts.
        print("  VERDICT:")
        if prim is not None:
            h2_ok = prim["valid_frac"] >= (1 - delta) - 1e-9
            h2_cheap = (not math.isnan(prim["cost_ratio"])) and prim["cost_ratio"] < 0.85
            print(f"    - H2 reproduces: {'YES' if h2_ok else 'NO'} "
                  f"(marginal {'valid' if h2_ok else 'INVALID'}"
                  f"{', cheap stopping' if h2_cheap else ', but cost win not < 0.85'}).")
        else:
            print("    - H2 reproduces: UNKNOWN (no records).")
        print(f"    - H3 (hard-stratum abstention) reproduces: "
              f"{'YES' if h3_present else 'NO'}.")
        hides = bool(fewer)
        extra = ("; " + "; ".join(sorted(set(collapse_note)))) if collapse_note else ""
        print(f"    - policy-hides-failures reproduces: {'YES' if hides else 'NO'} "
              f"(greedy < random buckets at lambda_ref {[f'{x:g}' for x in fewer]}){extra}.")

    # --- Pre-committed consequence statement.
    print()
    print("=" * 78)
    print("PRE-COMMITTED CONSEQUENCE:")
    new_datasets = [d for d in datasets if d != "tabular:adult"]
    h3_beyond_adult = [d for d in h3_datasets if d != "tabular:adult"]
    if not new_datasets:
        print("  Only adult present here -- run the two new datasets on the cluster to")
        print("  populate this readout before the writeup.")
    else:
        if not h3_beyond_adult:
            print("  H3 (hard-stratum abstention) appears on NO new dataset beyond adult.")
            print("  Per the pre-commit, this reshapes the paper: H3 would be an")
            print("  adult-specific phenomenon, to be reported plainly, not buried.")
        else:
            print(f"  H3 reproduces beyond adult on: {h3_beyond_adult} -- the hard-stratum")
            print("  abstention story generalizes; proceed to the writeup as framed.")
    print("=" * 78)


def run_step5(args) -> int:
    """Step-5 default report: per-bucket Mondrian per cell + cross-dataset readout."""
    from cafa.data import feasible_alpha_from_floor  # additive Step-5 helper

    metrics_dir = _resolve_metrics_dir(args)
    print(f"metrics dir : {metrics_dir}")
    recs = _load_step5(metrics_dir, args)
    if not recs:
        print("No step4_*.json files found yet.")
        print("Run scripts/run_mondrian.py across the {policy} x {lambda_ref} x "
              "{cost} sweep first, then re-run this.")
        print("The cross-dataset readout (H2 cost, H3 abstention, the insight) is "
              "PENDING the cluster run.")
        return 1

    n_cells = len(recs)
    print(f"found {sum(len(v) for v in recs.values())} record(s) across "
          f"{n_cells} (dataset,policy,scheme,lambda_ref) cell(s).")

    def _key(k):
        ds, pol, cs, lr = k
        return (str(ds), str(pol), str(cs), (lr is None, lr))

    for key in sorted(recs, key=_key):
        ds, pol, cs, lr = key
        cell = recs[key]
        alpha = float(cell[0].get("alpha", 0.10))
        delta = float(cell[0].get("delta", 0.10))
        lr_s = "?" if lr is None else f"{lr:g}"
        print()
        print("=" * 78)
        print(f"CELL  dataset={ds}  policy={pol}  cost_scheme={cs}  "
              f"lambda_ref={lr_s}  (seeds={len(cell)})")
        print("=" * 78)

        rows = _h2_table(cell, alpha, delta)
        _print_h2_table(_headline_h2_rows(rows), alpha, delta)

        blended = _blended_mondrian_row(rows)
        if blended is not None:
            _, _, bn, bvalid, brisk, bcost, bviol = blended
            bvalid_s = "--" if math.isnan(bvalid) else f"{bvalid:.3f}"
            print(f"[diagnostic only, NOT a result] blended CAFA-Mondrian: "
                  f"valid={bvalid_s} over {bn} seeds "
                  f"(single-number gate is a stratum-weighting artifact; see the "
                  f"per-bucket report below).")

        print()
        brows, n_seeds = _mondrian_bucket_report(cell, alpha)
        _print_mondrian_bucket_report(brows, n_seeds, alpha)

        # Reuse the (Task-4 corrected) framing fork for the per-cell verdict.
        bucket_rows = _per_bucket_summary(cell, alpha)
        _framing_fork(ds, f"{pol} (lr={lr_s})", cs, rows, bucket_rows, alpha, delta)

    _cross_dataset_readout(recs, feasible_alpha_from_floor)

    print()
    print("=" * 78)
    print("Reminder: CAFA-marginal carries the LTT validity guarantee and the")
    print("per-bucket Mondrian report certifies/abstains per stratum; the blended")
    print("CAFA-Mondrian number is a demoted diagnostic; oracle-* see test labels.")
    print("=" * 78)
    return 0


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.legacy_g2:
        return run_g2_legacy(args)
    if getattr(args, "report", "step5") == "step4":
        return run_step4(args)
    return run_step5(args)


if __name__ == "__main__":
    raise SystemExit(main())