#!/usr/bin/env python
"""Phase 3 -- backbone-robustness report (Task 1: audit stability across train seeds).

Reads metrics_v2/{dsname}_ts{ts}_{policy}.json for every available train_seed
plus the per-seed committed configs, and writes analysis_v2/PHASE3_REPORT.md:

  per dataset, across train_seeds:
    - committed {floor -> alpha} per seed (step crossings flagged: the fixed
      rule applied per backbone -- alpha is a property of the backbone);
    - marginal + IUT gate outcomes (violation rate, Wilson 95% UB);
    - H2 at lambda_ref = 0.9, primary scheme: cafa cost ratio vs full and vs
      oracle; plugin violation rate;
    - audit stability (the headline): hardest stratum k* at lambda_ref = 0.9,
      R_full(k*) with 95% CP LCB, three-way verdict -- is the same detection
      outcome reproduced across backbone draws?
    - IUT abstention rate at lambda_ref = 0.9.

  and a cross-seed stability verdict per dataset.

Usage:
    python scripts/phase3_report.py [--metrics-dir metrics_v2] [--out analysis_v2]
                                    [--policy greedy_entropy]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_Z = 1.96
_LR = "0.9"


def wilson_ub(k: int, n: int, z: float = _Z) -> float:
    if n == 0:
        return 0.0
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return min(1.0, center + half)


def _fmt(x, nd=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "n/a"
    return f"{x:.{nd}f}"


def _nanmean(xs):
    arr = np.asarray([x for x in xs if x is not None], dtype=float)
    arr = arr[~np.isnan(arr)]
    return float(arr.mean()) if arr.size else float("nan")


def seed_record(data: dict, dsname: str, ts: int) -> dict:
    """Everything the report needs from one (dataset, ts, policy) metrics JSON."""
    alpha = float(data["alpha"])
    delta = float(data["delta"])
    scheme = "inverse_info" if "inverse_info" in data["meta"]["schemes"] else "uniform"

    marg_k = marg_n = iut_k = iut_n = 0
    for lr_key, blk in data["lambda_refs"].items():
        for r in blk["resplits"]:
            mr = r["schemes"][data["meta"]["schemes"][0]]["cafa_marginal"]["realized_risk"]
            marg_n += 1
            if mr is not None and mr > alpha:
                marg_k += 1
            iut_n += 1
            if not r.get("iut_abstained", False):
                ips = [v for v in r["iut_per_stratum_risk"].values() if v is not None]
                if ips and max(ips) > alpha:
                    iut_k += 1

    blk9 = data["lambda_refs"].get(_LR)
    audit = h2 = None
    if blk9:
        pop = blk9["population"]
        resplits = blk9["resplits"]
        best_k, best = None, None
        for ks, info in pop["per_stratum_full"].items():
            if info["risk"] is None or int(info["n"]) == 0:
                continue
            if best is None or float(info["risk"]) > float(best["risk"]):
                best_k, best = ks, info
        audit = {"k_star": best_k, "R_full": best["risk"], "lcb": best["cp_lcb95"],
                 "verdict": best["verdict"], "n": best["n"]} if best else None
        marg_cost = _nanmean([r["schemes"][scheme]["cafa_marginal"]["realized_cost"]
                              for r in resplits])
        full_cost = _nanmean([r["schemes"][scheme]["oracle_full"]["realized_cost"]
                              for r in resplits])
        oracle_cost = _nanmean([r["schemes"][scheme]["oracle_cheapest"]["realized_cost"]
                                for r in resplits])
        plug_risks = [r["schemes"][scheme]["plugin"]["realized_risk"] for r in resplits]
        plug_viol = float(np.mean([1.0 if (x is not None and x > alpha) else 0.0
                                   for x in plug_risks]))
        iut_abst = float(np.mean([bool(r["iut_abstained"]) for r in resplits]))
        h2 = {"scheme": scheme, "cost_ratio_full": marg_cost / full_cost if full_cost else float("nan"),
              "cost_ratio_oracle": marg_cost / oracle_cost if oracle_cost else float("nan"),
              "plugin_viol": plug_viol, "iut_abstain": iut_abst}

    return {"dsname": dsname, "ts": ts, "alpha": alpha, "delta": delta,
            "marg_frac": marg_k / marg_n if marg_n else 0.0,
            "marg_ub": wilson_ub(marg_k, marg_n),
            "iut_frac": iut_k / iut_n if iut_n else 0.0,
            "iut_ub": wilson_ub(iut_k, iut_n),
            "audit": audit, "h2": h2}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAFA v2 Phase-3 cross-seed report.")
    ap.add_argument("--metrics-dir", default="metrics_v2")
    ap.add_argument("--out", default="analysis_v2")
    ap.add_argument("--policy", default="greedy_entropy")
    args = ap.parse_args(argv)

    metrics_dir = Path(args.metrics_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    by_ds = defaultdict(dict)      # dsname -> ts -> record
    for p in sorted(metrics_dir.glob(f"*_{args.policy}.json")):
        data = json.loads(p.read_text())
        meta = data["meta"]
        if meta["policy"] != args.policy:
            continue
        ts = int(meta["train_seed"])
        by_ds[meta["dsname"]][ts] = seed_record(data, meta["dsname"], ts)
    if not by_ds:
        print(f"ERROR: no {args.policy} metrics under {metrics_dir}.", file=sys.stderr)
        return 2

    lines = ["# CAFA v2 -- PHASE 3 REPORT (backbone robustness across train seeds)\n",
             f"_Policy: {args.policy}. Audit/H2 columns at lambda_ref = {_LR}, primary "
             "cost scheme. alpha is committed per (dataset, train_seed) by the fixed "
             "rule on that backbone's probe floor -- a step crossing is the rule "
             "working, not an inconsistency._\n"]

    stable, unstable = [], []
    for dsname, seeds in sorted(by_ds.items()):
        # committed {floor -> alpha} per seed
        lines.append(f"## {dsname}\n")
        lines.append("| ts | floor (probe) | alpha | marg viol [UB] | gate | "
                     "IUT viol [UB] | gate | plugin viol@0.9 | cafa cost/full | "
                     "cafa cost/oracle | IUT abstain@0.9 | k* | R_full(k*) [LCB] | verdict |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        verdicts = {}
        alphas = {}
        for ts, rec in sorted(seeds.items()):
            committed_path = Path("configs") / f"committed_v2_{dsname}_ts{ts}.json"
            floor = None
            if committed_path.exists():
                floor = json.loads(committed_path.read_text())["floor"]["estimate"]
            a = rec["audit"] or {}
            h = rec["h2"] or {}
            m_gate = "PASS" if rec["marg_ub"] <= rec["delta"] else "FAIL"
            i_gate = "PASS" if rec["iut_ub"] <= rec["delta"] else "FAIL"
            lines.append(
                f"| {ts} | {_fmt(floor)} | {rec['alpha']:g} | "
                f"{_fmt(rec['marg_frac'], 3)} [{_fmt(rec['marg_ub'], 3)}] | {m_gate} | "
                f"{_fmt(rec['iut_frac'], 3)} [{_fmt(rec['iut_ub'], 3)}] | {i_gate} | "
                f"{_fmt(h.get('plugin_viol'), 2)} | {_fmt(h.get('cost_ratio_full'), 3)} | "
                f"{_fmt(h.get('cost_ratio_oracle'), 3)} | {_fmt(h.get('iut_abstain'), 2)} | "
                f"{a.get('k_star', 'n/a')} | {_fmt(a.get('R_full'))} "
                f"[{_fmt(a.get('lcb'))}] | {a.get('verdict', 'n/a')} |")
            verdicts[ts] = a.get("verdict")
            alphas[ts] = rec["alpha"]
        lines.append("")
        # alpha step crossings
        uniq_a = sorted(set(alphas.values()))
        if len(uniq_a) > 1:
            lines.append(f"- alpha step crossing across seeds: {alphas} -- the fixed rule "
                         "applied per backbone; report per-seed alpha, never mix.")
        # stability verdict
        uniq_v = sorted(set(v for v in verdicts.values() if v is not None))
        if len(uniq_v) == 1 and len(verdicts) > 1:
            lines.append(f"- **Audit stability: STABLE** -- verdict '{uniq_v[0]}' at "
                         f"lambda_ref={_LR} reproduced across train_seeds "
                         f"{sorted(verdicts)}.")
            stable.append((dsname, uniq_v[0]))
        elif len(verdicts) > 1:
            lines.append(f"- **Audit stability: FLIPS with the seed** -- verdicts by ts: "
                         f"{verdicts}. Scope any claim accordingly.")
            unstable.append((dsname, verdicts))
        else:
            lines.append("- Only one train_seed present; stability not assessable yet.")
        lines.append("")

    lines.append("## Cross-seed stability verdict\n")
    if stable:
        lines.append("- Replicates (same verdict at every seed): " +
                     ", ".join(f"{d} ({v})" for d, v in stable) + ".")
    if unstable:
        lines.append("- Flips with the seed: " +
                     ", ".join(f"{d} ({v})" for d, v in unstable) + ".")
    if not unstable and stable:
        lines.append("- Claim supported at this scope: the infeasible-stratum finding is "
                     "a property of the data, not of a lucky backbone draw, on the "
                     "datasets listed as replicating.")

    (out_dir / "PHASE3_REPORT.md").write_text("\n".join(lines))
    print(f"[phase3] wrote {out_dir / 'PHASE3_REPORT.md'} "
          f"(stable: {[d for d, _ in stable]}; flips: {[d for d, _ in unstable]})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
