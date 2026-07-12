#!/usr/bin/env python
"""Phase 5, Task 3 -- IUT non-vacuity (extracted from the alpha-sweep; no re-run).

At the committed alpha and lambda_ref = 0.9 the IUT abstains ~1.00 everywhere
that a stratum is alpha-infeasible -- correct, but "zero failures" is then
vacuously true. This script surfaces the operating points where the IUT
CERTIFIES uniform per-stratum validity at a cost below full acquisition:

  1. From analysis_v2/alpha_sweep.csv (run alpha_sweep first): per dataset,
     the (alpha, lambda_ref = 0.9) rows with abstention < 1 -- certified cost,
     cost ratio vs full, marginal cost, premium.
  2. The minimum swept alpha at which the IUT certifies at lambda_ref = 0.9 --
     cross-checked against R_full(k*) from the H3 table (certification
     requires the hardest stratum to be alpha-feasible with margin, so
     min-certifying-alpha should sit at/above R_full(k*)).
  3. Vacuity labels for every gate cell: per (cell, lambda_ref) IUT abstention
     rate; a cell is VACUOUS at a lambda_ref where abstention == 1.0 (it never
     certified, so it could never be wrong) and NON-VACUOUS otherwise.

Outputs: analysis_v2/iut_nonvacuity.csv (vacuity labels, all cells),
analysis_v2/iut_nonvacuity_transitions.csv (per-dataset min certifying alpha +
H3 cross-check), analysis_v2/IUT_NONVACUITY.md.

Usage:
    python scripts/iut_nonvacuity.py --all [--metrics-dir results_committed/metrics]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_LR = "0.9"


def _fmt(x, nd=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "n/a"
    return f"{x:.{nd}f}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAFA v2 IUT non-vacuity report.")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--metrics-dir", default="metrics_v2")
    ap.add_argument("--analysis-dir", default="analysis_v2")
    ap.add_argument("--out", default="analysis_v2")
    args = ap.parse_args(argv)

    metrics_dir = Path(args.metrics_dir)
    analysis_dir = Path(args.analysis_dir)
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)

    sweep_csv = analysis_dir / "alpha_sweep.csv"
    if not sweep_csv.exists():
        print(f"ERROR: {sweep_csv} not found; run alpha_sweep.py first.", file=sys.stderr)
        return 2
    sweep = list(csv.DictReader(open(sweep_csv, newline="")))
    by_ds = defaultdict(list)
    for r in sweep:
        by_ds[r["dataset"]].append(r)

    # ---- per-dataset: min certifying alpha at lambda_ref 0.9 + H3 cross-check ----
    transitions = []
    for ds, rs in sorted(by_ds.items()):
        rs = sorted(rs, key=lambda r: float(r["alpha"]))
        committed_alpha = float(rs[0]["committed_alpha"])
        cert_rows = [r for r in rs if float(r["iut_abstain"]) < 1.0]
        min_cert = cert_rows[0] if cert_rows else None
        # H3: R_full(k*) from the softmax greedy ts0 metrics (population block).
        mfile = metrics_dir / f"{ds}_ts0_greedy_entropy.json"
        r_full_kstar = lcb = None
        if mfile.exists():
            data = json.loads(mfile.read_text())
            blk = data["lambda_refs"].get(_LR)
            if blk:
                best = None
                for ks, info in blk["population"]["per_stratum_full"].items():
                    if info["risk"] is None or int(info["n"]) == 0:
                        continue
                    if best is None or float(info["risk"]) > float(best["risk"]):
                        best = info
                if best:
                    r_full_kstar, lcb = float(best["risk"]), best["cp_lcb95"]
        consistent = None
        if min_cert is not None and r_full_kstar is not None:
            # certification needs the hardest stratum feasible with an HB margin,
            # so the min certifying alpha must exceed R_full(k*).
            consistent = float(min_cert["alpha"]) > r_full_kstar
        transitions.append({
            "dataset": ds, "committed_alpha": committed_alpha,
            "min_certifying_alpha_lr0.9": None if min_cert is None else float(min_cert["alpha"]),
            "abstention_there": None if min_cert is None else float(min_cert["iut_abstain"]),
            "iut_cost_ratio_full_there": None if min_cert is None else float(min_cert["iut_cost_ratio_full"]),
            "iut_premium_there": None if min_cert is None else float(min_cert["iut_premium_vs_marginal"]),
            "marg_cost_ratio_full_there": None if min_cert is None else float(min_cert["marg_cost_ratio_full"]),
            "R_full_kstar": r_full_kstar, "R_full_kstar_lcb": lcb,
            "h3_consistent": (None if consistent is None else ("PASS" if consistent else "FAIL")),
        })

    # ---- vacuity labels for every gate cell x lambda_ref ----
    vac_rows = []
    for p in sorted(metrics_dir.glob("*.json")):
        data = json.loads(p.read_text())
        meta = data["meta"]
        score = meta.get("score", "softmax")
        label = f"{meta['dsname']}/{meta['policy']}/ts{meta['train_seed']}" + \
                (f"[{score}]" if score != "softmax" else "")
        row = {"cell": label}
        vacuous_all = True
        for lr_key, blk in sorted(data["lambda_refs"].items()):
            ab = float(np.mean([bool(r["iut_abstained"]) for r in blk["resplits"]]))
            row[f"abstain@{lr_key}"] = round(ab, 3)
            if ab < 1.0:
                vacuous_all = False
        row["nonvacuous_at_some_lambda_ref"] = int(not vacuous_all)
        row[f"vacuous@{_LR}"] = int(row.get(f"abstain@{_LR}", 0.0) >= 1.0)
        vac_rows.append(row)

    # ---- write CSVs ----
    with open(out_dir / "iut_nonvacuity_transitions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(transitions[0].keys()))
        w.writeheader(); w.writerows(transitions)
    fieldnames = sorted({k for r in vac_rows for k in r}, key=lambda k: (k != "cell", k))
    with open(out_dir / "iut_nonvacuity.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(vac_rows)

    # ---- markdown ----
    lines = ["# CAFA v2 -- IUT NON-VACUITY\n",
             "_An abstaining certificate claims nothing, so 'zero IUT failures' at an "
             "operating point with abstention 1.0 is vacuously true. This report "
             "surfaces where the IUT CERTIFIES uniform per-stratum validity at "
             "lambda_ref = 0.9 (fine stratification) at a cost below full acquisition, "
             "extracted from the alpha-sweep (no re-run)._\n",
             "## Minimum certifying alpha at lambda_ref = 0.9 (per dataset)\n",
             "| dataset | committed alpha | min certifying alpha (swept grid) | "
             "abstention there | IUT cost/full | IUT premium vs marginal | "
             "R_full(k*) [H3] | consistency (min cert alpha > R_full(k*)) |",
             "|---|---|---|---|---|---|---|---|"]
    for t in transitions:
        mca = t["min_certifying_alpha_lr0.9"]
        lines.append(
            f"| {t['dataset']} | {t['committed_alpha']:g} | "
            f"{'none in swept range' if mca is None else f'{mca:.4f}'} | "
            f"{_fmt(t['abstention_there'], 2)} | {_fmt(t['iut_cost_ratio_full_there'], 3)} | "
            f"{_fmt(t['iut_premium_there'], 2)} | {_fmt(t['R_full_kstar'])} "
            f"[LCB {_fmt(t['R_full_kstar_lcb'])}] | {t['h3_consistent'] or 'n/a'} |")
    lines.append("")
    lines.append("Reading: at the min certifying alpha the IUT stops abstaining and "
                 "certifies EVERY stratum simultaneously at a cost below full "
                 "acquisition (cost/full < 1); below it, the hardest stratum is "
                 "intrinsically alpha-infeasible (proven by the H3 fallback bound) and "
                 "abstention -> full acquisition is the only honest deployment. The "
                 "consistency column verifies the certification boundary sits above "
                 "R_full(k*), as the theory requires.\n")

    lines.append("## Vacuity labels (every gate cell; abstention per lambda_ref)\n")
    lr_cols = sorted({k for r in vac_rows for k in r if k.startswith("abstain@")})
    lines.append("| cell | " + " | ".join(lr_cols) +
                 f" | vacuous@{_LR} | non-vacuous somewhere |")
    lines.append("|---|" + "---|" * (len(lr_cols) + 2))
    for r in sorted(vac_rows, key=lambda r: r["cell"]):
        lines.append("| " + r["cell"] + " | " +
                     " | ".join(_fmt(r.get(c), 2) for c in lr_cols) +
                     f" | {'yes' if r[f'vacuous@{_LR}'] else 'NO'} | "
                     f"{'yes' if r['nonvacuous_at_some_lambda_ref'] else 'no'} |")
    lines.append("")
    lines.append("An IUT gate PASS is evidence only where the cell is non-vacuous (it "
                 "certified on at least some resplits at that lambda_ref); vacuous cells "
                 "are correctness-by-abstention and are labelled so a reviewer does not "
                 "have to do this arithmetic.")
    (out_dir / "IUT_NONVACUITY.md").write_text("\n".join(lines))

    n_cert = sum(1 for t in transitions if t["min_certifying_alpha_lr0.9"] is not None)
    print(f"[iut-nonvacuity] wrote IUT_NONVACUITY.md + 2 CSVs "
          f"(certifying operating point found on {n_cert}/{len(transitions)} datasets; "
          f"H3 consistency: {[t['h3_consistent'] for t in transitions]}).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
