#!/usr/bin/env python
"""v3 -- headline tables from metrics_v3/*.json (torch-free).

Produces (to --output-dir):
  * TABLE_E4_cascade.md / .csv  -- the headline certify-or-route table
  * TABLE_E3_audit.md / .csv    -- localized audit verdicts of the deepest stratum
  * TABLE_E2_blindness.md       -- marginal certificate vs. hidden stratum risk
  * TABLE_E6_baselines.md       -- baselines at the primary lambda_ref

Round 2 (multi-split metrics; the raw columns are unchanged):
  * E4: ``violation_by_split`` (min-max of the raw rate over the splits), ``certified_violation``
    (share of draws whose exact one-sided binomial test-split p-value is <= 0.05 in some K_cal
    stratum), ``max_excess_se`` (mean over draws of max_k (R_test,k - alpha) / SE_k) and
    ``verdict_agreement`` (splits whose deepest-stratum audit verdict equals the primary split's,
    x/n).  Round-1 metrics files lack these fields; the cells are left empty.
  * E2: ``hidden_certified_violation_rate``; E6: ``stratum_certified_violation_rate``.
  * TABLE_E4_cascade_seeds.md / .csv -- one row per (dataset, policy): mean +- sd over the train seeds present
    (sample sd, ddof = 1; with a single seed the sd is empty and the row says n = 1).  TABLE_E4_cascade keeps one
    row per (dataset, policy, seed).

Round 3 (Task I; appended after the round-2 columns, which keep their order and values):
  * E4 ``deployed_cost_over_T`` / ``marginal_cost_over_T`` / ``mondrian_cost_over_T`` -- mean test cost of the
    cascade, of marginal CAFA and of the Mondrian oracle divided by T (``meta.T``; = the fraction of full
    acquisition under uniform costs); ``tier2_would_certify`` -- share of the (key, scheme)'s draw records whose
    ``tiers_certified.budget`` is True while ``tiers_certified.threshold`` is False (the Type-I signature).  It
    equals the tier-2 share ``tier2`` by construction of the deployment rule: tier 2 is deployed exactly when tier 1
    does not certify and tier 2 does, so the column measures how often tier 2 mattered (not how often the budget
    certificate would be issued regardless of tier 1); ``escalated_fraction`` = 1 - answered_fraction;
    ``oracle_safe_cost_over_T`` / ``oracle_safe_feasible_rate`` / ``cascade_over_safe_oracle`` -- the ex-post
    stratum-safe oracle (Task K: baseline ``oracle_stratum_safe``, summary ``cascade_cost_over_oracle``), empty
    for metrics written before Task K.  The numeric ones are also averaged in TABLE_E4_cascade_seeds.
  * E6 ``feasible_rate`` (baselines whose records carry ``feasible``: the two Task-K oracles; else empty).
  * TABLE_E4_cost_gap.md / .csv -- only for cells whose metrics carry the Task-K oracle: is the cascade's cost
    intrinsic (even the ex-post stratum-safe oracle needs near-full acquisition: ``oracle_safe_over_full`` = oracle
    cost / full-acquisition cost >= 0.9, which equals the oracle's cost / T under uniform costs and stays correct
    under non-uniform schemes such as inverse_info) or sample-limited (the oracle is cheap, the certified cascade is
    not)?  The label uses the pooled costs only; ``label_note`` qualifies it with the splits whose oracle is
    infeasible or whose n_needed is inf, ``n_splits_finite`` counts the splits with a finite n_needed.  Definitions
    in :func:`cost_gap_row` and in the md header.

    python scripts/make_tables_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --lambda-ref-key dep --scheme uniform
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa.commit_rules import kl_bernoulli  # noqa: E402

SEED_COLS = ("tier1", "tier2", "tier3", "none", "certified_deployment", "deployed_cost", "cost_premium",
             "answered_fraction", "test_stratum_violation", "certified_violation", "max_excess_se",
             # round 3
             "deployed_cost_over_T", "marginal_cost_over_T", "mondrian_cost_over_T", "tier2_would_certify",
             "escalated_fraction", "oracle_safe_cost_over_T", "oracle_safe_feasible_rate", "cascade_over_safe_oracle")

# cost-gap label (TABLE_E4_cost_gap): the oracle itself needs >= 0.9 of the full-acquisition cost -> "intrinsic";
# else a cascade / oracle cost ratio above the cost-premium band 1.0-1.6 (instruction.md section 4.4) ->
# "sample-limited"; else "near-oracle"
INTRINSIC_OVER_FULL, PREMIUM_BAND_TOP = 0.9, 1.6
INF_REASON = "r_cal(lambda*) >= alpha or no feasible draw"
COST_GAP_NOTE = "\n".join([
    "- Ex-post stratum-safe oracle (non-deployable, uses test labels): `oracle_safe_cost_over_T` = its mean test cost "
    "/ T, `oracle_safe_over_full` = its mean test cost / the full-acquisition mean test cost (baseline "
    "`full_acquisition`; = oracle_safe_cost_over_T under uniform costs), `safe_mondrian_cost_over_T` the per-stratum "
    "version's cost / T; `cascade_over_safe_oracle` = cascade cost / oracle cost; "
    "`cascade_over_safe_oracle_feasible` = the same ratio over the draws whose oracle is feasible only (summary "
    "`cascade_cost_over_oracle_feasible`; empty if no draw has a feasible oracle).",
    f"- `label`: \"intrinsic\" if oracle_safe_over_full >= {INTRINSIC_OVER_FULL} (even the oracle needs near-full "
    f"acquisition; the full-acquisition cost, not T, so the rule also holds under non-uniform cost schemes); else "
    f"\"sample-limited\" if cascade_over_safe_oracle >= {PREMIUM_BAND_TOP} (above the cost-premium "
    "band 1.0-1.6 of instruction.md section 4.4: the oracle is cheap, the certified cascade is not); else "
    "\"near-oracle\".  At a zero-cost oracle the ratio is empty and the label compares the costs directly.",
    "- The label uses the pooled costs only (it looks neither at the oracle's feasibility nor at n_needed); "
    "`label_note` qualifies it: empty when the oracle is feasible in every split (some draw of the split has a "
    "feasible oracle) and n_needed is finite in every split, else e.g. \"oracle infeasible in 3/5 splits; n_needed "
    f"inf in 4/5 splits ({INF_REASON})\".  `n_splits_finite` = splits with a finite n_needed / splits.",
    "- Per split s: k* = deepest populated calibration-pool stratum (max key of audit_by_split[s]); n_k_cal = cal_frac "
    "* n_k(k*) (expected count of k* in one calibration draw; cal_frac = meta.cal_frac, default 0.5); r_cal(s) = "
    "median over the split's draws with a feasible oracle of the WHOLE calibration pool's risk of k* at the oracle's "
    "lambda*; n_needed(s) = ln(1/delta_1) / kl(r_cal(s) || alpha) with delta_1 = delta * delta_weights[0] "
    "(cafa.commit_rules.kl_bernoulli), inf if r_cal >= alpha or no draw of the split has a feasible oracle.",
    "- Per cell: `n_needed` = median over splits, `n_needed_range` = min-max over splits; `k_star`, `n_k_cal`, "
    "`r_cal_at_oracle` of the primary split; `n_needed_over_n_k` = n_needed / n_k_cal (primary)."])


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


def by_split_range(s: dict, key: str):
    """``"min–max"`` of a summary field over the splits (None without ``by_split``)."""
    bs = s.get("by_split") or {}
    v = [x[key] for x in bs.values() if x.get(key) is not None]
    return f"{min(v):.3f}–{max(v):.3f}" if v else None


def over_T(v, T):
    """``v / T`` (None when ``v`` or ``T`` is missing)."""
    return None if v is None or not T else float(v) / float(T)


def tier2_would_certify(draws: list):
    """Share of draw records whose tier-2 (budget) certificate is issued while tier 1 (threshold) is not."""
    if not draws:
        return None
    tc = [r["cascade"].get("tiers_certified") or {} for r in draws]
    return sum(t.get("budget") is True and t.get("threshold") is False for t in tc) / len(tc)


def n_needed(r_cal, alpha: float, delta_1: float) -> float:
    """Calibration size that certifies a stratum risk ``r_cal`` at level ``delta_1``:
    ``ln(1/delta_1) / kl(r_cal || alpha)``; inf when ``r_cal`` is None (no feasible oracle) or ``>= alpha``."""
    if r_cal is None or float(r_cal) >= float(alpha):
        return math.inf
    return math.log(1.0 / float(delta_1)) / kl_bernoulli(float(r_cal), float(alpha))


def cost_gap_label(oracle_over_full, cascade_over_oracle):
    """"intrinsic" / "sample-limited" / "near-oracle" (rule in COST_GAP_NOTE); ``oracle_over_full`` = oracle cost /
    full-acquisition cost.  None without the oracle (or the full-acquisition) cost."""
    if oracle_over_full is None:
        return None
    if oracle_over_full >= INTRINSIC_OVER_FULL:
        return "intrinsic"
    if cascade_over_oracle is None:
        return None
    return "sample-limited" if cascade_over_oracle >= PREMIUM_BAND_TOP else "near-oracle"


def _nfmt(x) -> str:
    return "inf" if math.isinf(x) else f"{x:.0f}"


def label_note(n_infeasible: int, n_inf: int, n_splits: int) -> str:
    """``label_note`` of TABLE_E4_cost_gap: "" when the oracle is feasible in every split (``n_infeasible`` = 0) and
    n_needed is finite in every split (``n_inf`` = 0); else the counts, e.g. "oracle infeasible in 3/5 splits;
    n_needed inf in 4/5 splits (r_cal(lambda*) >= alpha or no feasible draw)"."""
    parts = []
    if n_infeasible:
        parts.append(f"oracle infeasible in {n_infeasible}/{n_splits} splits")
    if n_inf:
        parts.append(f"n_needed inf in {n_inf}/{n_splits} splits ({INF_REASON})")
    return "; ".join(parts)


def cost_gap_row(d: dict, blk: dict, s: dict, draws: list) -> dict:
    """TABLE_E4_cost_gap row of one cell (``s`` = the scheme's pooled summary; definitions in COST_GAP_NOTE).

    The label is computed from the pooled costs only (``oracle_safe_over_full`` = oracle / full-acquisition cost,
    ``cascade_over_safe_oracle``); ``label_note`` / ``n_splits_finite`` qualify it per split: a split's oracle is
    infeasible when no draw of the split has a feasible ``oracle_stratum_safe`` record."""
    m = d["meta"]
    T = m["T"]
    alpha = float(d["alpha"])
    delta_1 = float(d["delta"]) * float(d["delta_weights"][0])
    cal_frac = float(m.get("cal_frac", 0.5))
    per = {}
    for sp, aud in blk["audit_by_split"].items():
        k = max(int(x) for x in aud)
        rs, feasible = [], False
        for r in draws:
            o = r["baselines"].get("oracle_stratum_safe") or {}
            if r["split_seed"] != int(sp) or not o.get("feasible"):
                continue
            feasible = True
            v = (o.get("calpool_stratum_risk") or {}).get(str(k))
            if v is not None:
                rs.append(float(v))
        r_cal = statistics.median(rs) if rs else None
        per[sp] = {"k": k, "n_k_cal": cal_frac * aud[str(k)]["n_k"], "r_cal": r_cal, "feasible": feasible,
                   "n_needed": n_needed(r_cal, alpha, delta_1)}
    prim = per.get(str(m.get("primary_test_seed")), per[min(per)])
    nn = [v["n_needed"] for v in per.values()]
    n_med = statistics.median(nn)
    n_fin = sum(not math.isinf(x) for x in nn)
    n_infeasible = sum(not v["feasible"] for v in per.values())
    bl = s["baselines"]
    o_cost = bl["oracle_stratum_safe"].get("mean_test_cost")
    full_cost = (bl.get("full_acquisition") or {}).get("mean_test_cost")
    ratio = s.get("cascade_cost_over_oracle")
    ratio_lab = ratio
    if ratio is None and o_cost == 0:   # the ratio is undefined at a zero-cost oracle: equal costs, or an infinite gap
        ratio_lab = 1.0 if not s["cascade_mean_test_cost"] else math.inf
    o_full = None if o_cost is None or not full_cost else float(o_cost) / float(full_cost)
    return {"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], "T": T, "alpha": d["alpha"],
            "deployed_cost_over_T": over_T(s["cascade_mean_test_cost"], T),
            "oracle_safe_cost_over_T": over_T(o_cost, T),
            "oracle_safe_over_full": o_full,
            "oracle_safe_feasible_rate": bl["oracle_stratum_safe"].get("feasible_rate"),
            "safe_mondrian_cost_over_T": over_T((bl.get("oracle_stratum_safe_mondrian") or {}).get("mean_test_cost"), T),
            "cascade_over_safe_oracle": ratio,
            "cascade_over_safe_oracle_feasible": s.get("cascade_cost_over_oracle_feasible"),
            "label": cost_gap_label(o_full, ratio_lab),
            "label_note": label_note(n_infeasible, len(nn) - n_fin, len(nn)),
            "k_star": prim["k"], "n_k_cal": prim["n_k_cal"], "r_cal_at_oracle": prim["r_cal"],
            "n_needed": n_med, "n_needed_range": f"{_nfmt(min(nn))}–{_nfmt(max(nn))}",
            "n_splits_finite": f"{n_fin}/{len(nn)}",
            "n_needed_over_n_k": n_med / prim["n_k_cal"] if prim["n_k_cal"] else None}


def seed_summary(e4: list) -> "tuple[list, list]":
    """(markdown rows, csv rows) of mean +- sd over seeds per (dataset, policy) for SEED_COLS."""
    groups = {}
    for r in e4:
        groups.setdefault((r["dataset"], r["policy"]), []).append(r)
    md, cs = [], []
    for (ds, pol), rs in sorted(groups.items()):
        seeds = sorted(int(r["seed"]) for r in rs)
        mrow = {"dataset": ds, "policy": pol, "n_seeds": len(rs), "seeds": " ".join(map(str, seeds))}
        crow = dict(mrow)
        for c in SEED_COLS:
            v = [float(r[c]) for r in rs if r.get(c) is not None]
            if not v:
                mrow[c], crow[c + "_mean"], crow[c + "_sd"] = "", None, None
                continue
            m = sum(v) / len(v)
            sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) if len(v) > 1 else None
            mrow[c] = f"{m:.3f}" + (f" ± {sd:.3f}" if sd is not None else "")
            crow[c + "_mean"], crow[c + "_sd"] = m, sd
            if len(v) < len(rs):
                mrow[c] += f" (n={len(v)})"
        md.append(mrow)
        cs.append(crow)
    return md, cs


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics-dir", required=True)
    p.add_argument("--output-dir", default="results_v3/tables")
    p.add_argument("--lambda-ref-key", default="dep")
    p.add_argument("--scheme", default="uniform")
    a = p.parse_args(argv)
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    e4, e3, e2, e6, gap = [], [], [], [], []
    for jp in sorted(Path(a.metrics_dir).glob("*.json")):
        d = json.loads(jp.read_text())
        m = d["meta"]
        blk = d["lambda_refs"].get(a.lambda_ref_key)
        if blk is None:
            continue
        sch = blk["schemes"].get(a.scheme)
        if sch is None:  # v3 fix: no silent fallback to another scheme (image cells are uniform-only)
            print(f"skip {jp.name}: no cost scheme {a.scheme!r} (has {sorted(blk['schemes'])})")
            continue
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
               "test_stratum_violation": s["cascade_violation_rate"],
               "violation_by_split": by_split_range(s, "cascade_violation_rate"),
               "certified_violation": s.get("cascade_certified_violation_rate"),
               "max_excess_se": s.get("cascade_max_excess_se_mean"),
               "delta": d["delta"],
               "deepest_verdict": aud["verdict"],
               "verdict_agreement": (f"{blk['deepest_verdict_agreement']}/{blk['n_splits']}"
                                     if "deepest_verdict_agreement" in blk else None)}
        # round 3 (Task I): cost / T, the tier-2 Type-I signature, escalation, and the Task-K stratum-safe oracle
        T = m["T"]
        bl = s["baselines"]
        osafe = bl.get("oracle_stratum_safe") or {}
        row.update({"deployed_cost_over_T": over_T(s["cascade_mean_test_cost"], T),
                    "marginal_cost_over_T": over_T(s["marginal_mean_test_cost"], T),
                    "mondrian_cost_over_T": over_T((bl.get("mondrian_oracle") or {}).get("mean_test_cost"), T),
                    "tier2_would_certify": tier2_would_certify(sch.get("draws")),
                    "escalated_fraction": 1.0 - s["cascade_mean_answered_fraction"],
                    "oracle_safe_cost_over_T": over_T(osafe.get("mean_test_cost"), T),
                    "oracle_safe_feasible_rate": osafe.get("feasible_rate"),
                    "cascade_over_safe_oracle": s.get("cascade_cost_over_oracle")})
        e4.append(row)
        if "oracle_stratum_safe" in bl and "audit_by_split" in blk:
            gap.append(cost_gap_row(d, blk, s, sch.get("draws") or []))
        e3.append({"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], "k": aud["k"],
                   "n_k": aud["n_k"], "alpha": d["alpha"], "rmin_thr": aud["rmin_thr"], "rmin_depth": aud["rmin_depth"],
                   "r_full": aud["r_full"], "p_thr": aud["p_thr"], "p_depth": aud["p_depth"], "verdict": aud["verdict"],
                   "all_verdicts": " ".join(f"{k}:{v['verdict']}" for k, v in sorted(blk["audit"].items(), key=lambda kv: int(kv[0])))})
        e2.append({"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], "alpha": d["alpha"],
                   "marginal_test_risk": s["marginal_mean_test_risk"],
                   "marginal_aggregate_violation": s["marginal_aggregate_violation_rate"],
                   "max_stratum_over_alpha": s["marginal_max_stratum_over_alpha_mean"],
                   "hidden_stratum_violation_rate": s["marginal_hidden_stratum_violation_rate"],
                   "hidden_certified_violation_rate": s.get("marginal_hidden_certified_violation_rate")})
        for name, b in s["baselines"].items():
            e6.append({"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], "baseline": name,
                       "mean_test_risk": b["mean_test_risk"], "mean_test_cost": b["mean_test_cost"],
                       "stratum_violation_rate": b["stratum_violation_rate"],
                       "aggregate_violation_rate": b["aggregate_violation_rate"],
                       "stratum_certified_violation_rate": b.get("stratum_certified_violation_rate"),
                       "feasible_rate": b.get("feasible_rate")})

    def write(name, rows, note=""):
        if not rows:
            return
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        keys = list(rows[0].keys())
        lines = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
        for r in rows:
            lines.append("| " + " | ".join(f(r[k]) for k in keys) + " |")
        (out / f"{name}.md").write_text(f"# {name} (lambda_ref key = {a.lambda_ref_key}, scheme = {a.scheme})\n\n"
                                        + (note + "\n\n" if note else "") + "\n".join(lines) + "\n", encoding="utf-8")

    write("TABLE_E4_cascade", e4)
    write("TABLE_E3_audit", e3)
    write("TABLE_E2_blindness", e2)
    write("TABLE_E6_baselines", e6)
    write("TABLE_E4_cost_gap", gap, note=COST_GAP_NOTE)  # Task-K metrics only (no file without them)
    md, cs = seed_summary(e4)
    if md:
        write("TABLE_E4_cascade_seeds", cs)
        keys = list(md[0].keys())
        lines = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
        lines += ["| " + " | ".join(str(r[k]) for k in keys) + " |" for r in md]
        (out / "TABLE_E4_cascade_seeds.md").write_text(
            f"# TABLE_E4_cascade_seeds (lambda_ref key = {a.lambda_ref_key}, scheme = {a.scheme}; mean ± sd over train "
            f"seeds, sample sd; single-seed rows show the value only)\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote tables for {len(e4)} cells to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
