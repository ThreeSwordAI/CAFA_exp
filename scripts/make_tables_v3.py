#!/usr/bin/env python
"""v3 -- headline tables from metrics_v3/*.json (torch-free).

Produces (to --output-dir):
  * TABLE_E4_cascade.md / .csv  -- the headline certify-or-route table
  * TABLE_E3_audit.md / .csv    -- localized audit verdicts of the deepest stratum
  * TABLE_E2_blindness.md       -- marginal certificate vs. hidden stratum risk
  * TABLE_E6_baselines.md       -- baselines at the primary lambda_ref

    python scripts/make_tables_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --lambda-ref-key dep --scheme uniform
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def f(v, d=3):
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return f"{v:.{d}f}"
    return str(v)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics-dir", required=True)
    p.add_argument("--output-dir", default="results_v3/tables")
    p.add_argument("--lambda-ref-key", default="dep")
    p.add_argument("--scheme", default="uniform")
    a = p.parse_args(argv)
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    e4, e3, e2, e6 = [], [], [], []
    for jp in sorted(Path(a.metrics_dir).glob("*.json")):
        d = json.loads(jp.read_text())
        m = d["meta"]
        blk = d["lambda_refs"].get(a.lambda_ref_key)
        if blk is None:
            continue
        sch = blk["schemes"].get(a.scheme) or blk["schemes"][next(iter(blk["schemes"]))]
        s = sch["summary"]
        deepest = str(max(int(k) for k in blk["audit"]))
        aud = blk["audit"][deepest]
        row = {"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], "alpha": d["alpha"],
               "G": blk["G"], "lambda_ref": round(blk["lambda_ref"], 3),
               "marginal_cost": s["marginal_mean_test_cost"],
               "tier1": s["tier_share"]["1"], "tier2": s["tier_share"]["2"], "tier3": s["tier_share"]["3"],
               "none": s["tier_share"]["0"], "certified_deployment": s["certified_deployment_rate"],
               "deployed_cost": s["cascade_mean_test_cost"], "cost_premium": s["cost_premium_cascade_over_marginal"],
               "answered_fraction": s["cascade_mean_answered_fraction"],
               "test_stratum_violation": s["cascade_violation_rate"], "delta": d["delta"],
               "deepest_verdict": aud["verdict"]}
        e4.append(row)
        e3.append({"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], "k": aud["k"],
                   "n_k": aud["n_k"], "alpha": d["alpha"], "rmin_thr": aud["rmin_thr"], "rmin_depth": aud["rmin_depth"],
                   "r_full": aud["r_full"], "p_thr": aud["p_thr"], "p_depth": aud["p_depth"], "verdict": aud["verdict"],
                   "all_verdicts": " ".join(f"{k}:{v['verdict']}" for k, v in sorted(blk["audit"].items(), key=lambda kv: int(kv[0])))})
        e2.append({"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], "alpha": d["alpha"],
                   "marginal_test_risk": s["marginal_mean_test_risk"],
                   "marginal_aggregate_violation": s["marginal_aggregate_violation_rate"],
                   "max_stratum_over_alpha": s["marginal_max_stratum_over_alpha_mean"],
                   "hidden_stratum_violation_rate": s["marginal_hidden_stratum_violation_rate"]})
        for name, b in s["baselines"].items():
            e6.append({"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], "baseline": name,
                       "mean_test_risk": b["mean_test_risk"], "mean_test_cost": b["mean_test_cost"],
                       "stratum_violation_rate": b["stratum_violation_rate"],
                       "aggregate_violation_rate": b["aggregate_violation_rate"]})

    def write(name, rows):
        if not rows:
            return
        with open(out / f"{name}.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        keys = list(rows[0].keys())
        lines = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
        for r in rows:
            lines.append("| " + " | ".join(f(r[k]) for k in keys) + " |")
        (out / f"{name}.md").write_text(f"# {name} (lambda_ref key = {a.lambda_ref_key}, scheme = {a.scheme})\n\n"
                                        + "\n".join(lines) + "\n")

    write("TABLE_E4_cascade", e4)
    write("TABLE_E3_audit", e3)
    write("TABLE_E2_blindness", e2)
    write("TABLE_E6_baselines", e6)
    print(f"wrote tables for {len(e4)} cells to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
