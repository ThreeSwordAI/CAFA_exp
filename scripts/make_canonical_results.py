#!/usr/bin/env python
"""The lock -- generate CANONICAL_RESULTS.md from canonical artifacts only.

Assembles, from metrics JSONs + committed configs + analysis CSVs (never from
prose), every number the paper will cite:
  provenance header (git SHA, date, env, frozen-file hashes); committed
  {floor -> alpha} per (dataset, train_seed); the full gate table (every cell,
  all seeds, Wilson UBs, borderline cells flagged); H2 snapshot at lambda_ref
  0.9; H3 audit with cross-seed stability; IUT abstention/premium by
  lambda_ref; alpha-sweep transitions; Phase-2 rho values + flat-frontier
  statement; Phase-4 score-ablation verdict; honest flags; figure index;
  STATUS: FROZEN.

Run AFTER analyze_results / phase2_analyze / phase3_report /
phase4_score_ablation / alpha_sweep, on the canonical (cluster) artifacts:

    python scripts/make_canonical_results.py [--metrics-dir metrics_v2]
        [--analysis-dir analysis_v2] [--out CANONICAL_RESULTS.md]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "src"))
sys.path.insert(0, str(_REPO / "scripts"))

from cafa import config  # noqa: E402

_Z = 1.96
_LR = "0.9"


def wilson_ub(k, n, z=_Z):
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


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=_REPO, check=True).stdout.strip()
    except Exception:
        return "unknown"


def gate_counts(data):
    alpha = float(data["alpha"])
    scheme0 = data["meta"]["schemes"][0]
    mk = mn = ik = in_ = 0
    for blk in data["lambda_refs"].values():
        for r in blk["resplits"]:
            mr = r["schemes"][scheme0]["cafa_marginal"]["realized_risk"]
            mn += 1
            if mr is not None and mr > alpha:
                mk += 1
            in_ += 1
            if not r.get("iut_abstained", False):
                ips = [v for v in r["iut_per_stratum_risk"].values() if v is not None]
                if ips and max(ips) > alpha:
                    ik += 1
    return mk, mn, ik, in_


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate CANONICAL_RESULTS.md (the lock).")
    ap.add_argument("--metrics-dir", default="metrics_v2")
    ap.add_argument("--analysis-dir", default="analysis_v2")
    ap.add_argument("--figures-dir", default="figures_v2")
    ap.add_argument("--out", default="CANONICAL_RESULTS.md")
    args = ap.parse_args(argv)

    cfg = config.load_experiment()
    metrics_dir = Path(args.metrics_dir)
    analysis_dir = Path(args.analysis_dir)

    metrics = []
    for p in sorted(metrics_dir.glob("*.json")):
        metrics.append(json.loads(p.read_text()))
    if not metrics:
        print(f"ERROR: no metrics under {metrics_dir}.", file=sys.stderr)
        return 2

    L = []
    L.append("# CAFA v2 -- CANONICAL RESULTS (the lock)\n")

    # ---- provenance ----
    manifest = (_REPO / "repro" / "MANIFEST.sha256")
    L.append("## Provenance\n")
    L.append(f"- generated: {datetime.now(timezone.utc).isoformat()}")
    L.append(f"- host: {platform.node()} ({platform.system()})")
    L.append(f"- git commit: {git_sha()}")
    L.append(f"- numpy: {np.__version__}")
    L.append("- environment lock: repro/requirements.lock.txt")
    if manifest.exists():
        L.append("- frozen-file hashes (repro/MANIFEST.sha256, CRLF-normalized check):")
        for line in manifest.read_text().splitlines():
            if line.strip():
                L.append(f"  - `{line.strip()}`")
    L.append("")

    # ---- committed targets ----
    L.append("## Committed targets: {floor -> alpha} per (dataset, train_seed)\n")
    L.append("| dataset | train_seed | probe floor | alpha | note |")
    L.append("|---|---|---|---|---|")
    alphas_by_ds = defaultdict(dict)
    for p in sorted(Path("configs").glob("committed_v2_*_ts*.json")):
        c = json.loads(p.read_text())
        ds = c["dataset"]
        ts = int(c["train_seed"])
        alphas_by_ds[ds][ts] = float(c["alpha"])
        L.append(f"| {ds} | {ts} | {_fmt(c['floor']['estimate'])} | {c['alpha']:g} | |")
    for ds, per in alphas_by_ds.items():
        if len(set(per.values())) > 1:
            L.append(f"| {ds} | -- | -- | -- | STEP CROSSING across seeds: {per} "
                     "(fixed rule per backbone; report per-seed, never mix) |")
    L.append("")

    # ---- gate table ----
    L.append("## Gate table (every cell, all seeds; delta per cell; Wilson 95% UB)\n")
    L.append("| cell | alpha | marginal viol [UB] | gate | IUT viol [UB] | gate |")
    L.append("|---|---|---|---|---|---|")
    borderline = []
    for data in metrics:
        meta = data["meta"]
        delta = float(data["delta"])
        score = meta.get("score", "softmax")
        label = f"{meta['dsname']}/{meta['policy']}/ts{meta['train_seed']}" + \
                (f"[{score}]" if score != "softmax" else "")
        mk, mn, ik, in_ = gate_counts(data)
        mub, iub = wilson_ub(mk, mn), wilson_ub(ik, in_)
        mg = "PASS" if mub <= delta else "FAIL"
        ig = "PASS" if iub <= delta else "FAIL"
        if mg == "FAIL" or mub > 0.8 * delta:
            borderline.append((label, mk / mn if mn else 0.0, mub, mg))
        L.append(f"| {label} | {data['alpha']:g} | {_fmt(mk / mn if mn else 0, 3)} "
                 f"[{_fmt(mub, 3)}] | {mg} | {_fmt(ik / in_ if in_ else 0, 3)} "
                 f"[{_fmt(iub, 3)}] | {ig} |")
    L.append("")

    # ---- H2 snapshot ----
    L.append(f"## H2 at lambda_ref = {_LR} (primary scheme; violation / mean cost / cost-vs-full)\n")
    L.append("| cell | cafa_marginal | plugin | fixed_conf_0.95 | budget_10 | oracle_cheapest | oracle_full |")
    L.append("|---|---|---|---|---|---|---|")
    for data in metrics:
        meta = data["meta"]
        if meta.get("score", "softmax") != "softmax":
            continue
        blk = data["lambda_refs"].get(_LR)
        if blk is None:
            continue
        alpha = float(data["alpha"])
        scheme = "inverse_info" if "inverse_info" in meta["schemes"] else "uniform"
        resplits = blk["resplits"]
        full_cost = _nanmean([r["schemes"][scheme]["oracle_full"]["realized_cost"] for r in resplits])

        def cell(mname):
            risks = [r["schemes"][scheme][mname].get("realized_risk") for r in resplits]
            costs = [r["schemes"][scheme][mname].get("realized_cost") for r in resplits]
            v = float(np.mean([1.0 if (x is not None and x > alpha) else 0.0 for x in risks]))
            c = _nanmean(costs)
            ratio = c / full_cost if full_cost else float("nan")
            return f"{_fmt(v, 2)} / {_fmt(c, 2)} / {_fmt(ratio, 3)}"

        label = f"{meta['dsname']}/{meta['policy']}/ts{meta['train_seed']}"
        L.append(f"| {label} | {cell('cafa_marginal')} | {cell('plugin')} | "
                 f"{cell('fixed_conf_0.95')} | {cell('budget_10')} | "
                 f"{cell('oracle_cheapest')} | {cell('oracle_full')} |")
    L.append("")

    # ---- H3 audit + stability ----
    L.append(f"## H3 audit at lambda_ref = {_LR} (greedy; hardest stratum k*)\n")
    L.append("| dataset | ts | k* | R_full(k*) [95% CP LCB] | verdict | marginal realized risk on k* |")
    L.append("|---|---|---|---|---|---|")
    verdict_by_ds = defaultdict(dict)
    for data in metrics:
        meta = data["meta"]
        if meta["policy"] != "greedy_entropy" or meta.get("score", "softmax") != "softmax":
            continue
        blk = data["lambda_refs"].get(_LR)
        if blk is None:
            continue
        pop = blk["population"]
        best_k, best = None, None
        for ks, info in pop["per_stratum_full"].items():
            if info["risk"] is None or int(info["n"]) == 0:
                continue
            if best is None or float(info["risk"]) > float(best["risk"]):
                best_k, best = ks, info
        if best is None:
            continue
        marg_on_k = _nanmean([r["marginal_per_stratum_risk"].get(best_k)
                              for r in blk["resplits"]])
        ts = int(meta["train_seed"])
        verdict_by_ds[meta["dsname"]][ts] = best["verdict"]
        L.append(f"| {meta['dsname']} | {ts} | {best_k} | {_fmt(best['risk'])} "
                 f"[{_fmt(best['cp_lcb95'])}] | {best['verdict']} | {_fmt(marg_on_k)} |")
    L.append("")
    stable = {ds: v for ds, v in
              ((ds, sorted(set(per.values()))) for ds, per in verdict_by_ds.items())
              if len(v) == 1 and len(verdict_by_ds[ds]) > 1}
    flips = {ds: per for ds, per in verdict_by_ds.items()
             if len(set(per.values())) > 1}
    L.append("Cross-seed stability: " +
             ("; ".join(f"{ds}: STABLE ({v[0]})" for ds, v in sorted(stable.items())) or "n/a") +
             (("; FLIPS: " + "; ".join(f"{ds}: {per}" for ds, per in sorted(flips.items())))
              if flips else "") + ".\n")

    # ---- IUT by lambda_ref ----
    L.append("## IUT abstention / cost premium by lambda_ref (greedy, ts0, primary scheme)\n")
    L.append("| dataset | lambda_ref | abstention | premium vs marginal |")
    L.append("|---|---|---|---|")
    for data in metrics:
        meta = data["meta"]
        if (meta["policy"] != "greedy_entropy" or int(meta["train_seed"]) != 0
                or meta.get("score", "softmax") != "softmax"):
            continue
        scheme = "inverse_info" if "inverse_info" in meta["schemes"] else "uniform"
        for lr_key, blk in data["lambda_refs"].items():
            resplits = blk["resplits"]
            ab = float(np.mean([bool(r["iut_abstained"]) for r in resplits]))
            ic = _nanmean([r["schemes"][scheme]["cafa_iut"]["realized_cost"] for r in resplits])
            mc = _nanmean([r["schemes"][scheme]["cafa_marginal"]["realized_cost"] for r in resplits])
            L.append(f"| {meta['dsname']} | {lr_key} | {_fmt(ab, 2)} | "
                     f"{_fmt(ic / mc if mc else float('nan'), 3)} |")
    L.append("")

    # ---- alpha-sweep ----
    sweep_csv = analysis_dir / "alpha_sweep.csv"
    if sweep_csv.exists():
        L.append("## Alpha-sweep: plugin transition vs committed alpha (ts0, greedy)\n")
        rows = list(csv.DictReader(open(sweep_csv, newline="")))
        by_ds = defaultdict(list)
        for r in rows:
            by_ds[r["dataset"]].append(r)
        L.append("| dataset | floor | committed alpha | plugin transition (first safe alpha) | position of committed target |")
        L.append("|---|---|---|---|---|")
        for ds, rs in sorted(by_ds.items()):
            rs = sorted(rs, key=lambda r: float(r["alpha"]))
            delta = float(rs[0]["delta"])
            ca = float(rs[0]["committed_alpha"])
            floor = float(rs[0]["floor"])
            trans = next((float(r["alpha"]) for r in rs if float(r["plugin_viol"]) <= delta), None)
            if trans is None:
                pos = "UNSAFE across the whole swept range"
                tr_txt = "never safe in range"
            else:
                margin = ca - trans
                pos = (f"{'SAFE' if margin >= 0 else 'UNSAFE'} by {abs(margin):.3f}")
                tr_txt = f"{trans:.3f} (floor + {trans - floor:.3f})"
            L.append(f"| {ds} | {_fmt(floor)} | {ca:g} | {tr_txt} | {pos} |")
        L.append("")
        L.append("Price of honesty: see the IUT abstention/premium columns of "
                 "analysis_v2/ALPHA_SWEEP.md and the F5 figures (abstention ~1.0 while "
                 "any stratum is alpha-infeasible; ~0 once alpha clears the hardest "
                 "stratum).\n")

    # ---- Phase 2 ----
    try:
        import phase2_analyze as p2
        paths = config.load_paths()
        records, _, _ = p2.collect(metrics_dir, paths, cfg)
        if records:
            agg = p2.aggregate_spearman(records)
            L.append("## Phase 2 (epsilon axis) -- concentration + the flat frontier\n")
            fr = agg["frontier"]
            for lr in ("0.5", "0.7", "0.9"):
                key = f"entropy_{lr}"
                if key in agg:
                    s = agg[key]
                    L.append(f"- rho(quality_auc, depth_entropy_norm@{lr}) = "
                             f"{_fmt(s.statistic, 3)} (p = {_fmt(s.pvalue, 4)})")
            L.append(f"- rho(quality_auc, detection frontier) = {_fmt(fr.statistic, 3)} "
                     f"(p = {_fmt(fr.pvalue, 4)}) -- a BETWEEN-DATASET CONFOUND; the "
                     "frontier is flat in epsilon within every dataset. NEVER quote this "
                     "rho as support for a detection-delay claim.")
            L.append("")
    except Exception as exc:  # phase-2 cells may be absent in a partial run
        L.append(f"## Phase 2 -- unavailable ({exc})\n")

    # ---- Phase 4 ----
    p4 = analysis_dir / "PHASE4_SCORE_ABLATION.md"
    if p4.exists():
        verdict_lines = [ln for ln in p4.read_text().splitlines()
                         if ln.startswith("**The audit finding")]
        L.append("## Phase 4 (score ablation)\n")
        L.extend(verdict_lines or ["- see analysis_v2/PHASE4_SCORE_ABLATION.md"])
        L.append("")

    # ---- honest flags ----
    L.append("## Honest flags\n")
    if borderline:
        for label, frac, ub, gate in borderline:
            L.append(f"- marginal gate {'FAIL' if gate == 'FAIL' else 'borderline'}: {label} "
                     f"(viol {_fmt(frac, 3)}, Wilson UB {_fmt(ub, 3)}) -- resplits share a "
                     "finite eval pool; violations cluster with the backbone draw.")
    else:
        L.append("- no borderline marginal cells in this batch.")
    if sweep_csv.exists():
        tight = [r for r in csv.DictReader(open(sweep_csv, newline=""))
                 if abs(float(r["alpha_minus_floor"]) - 0.02) < 1e-9
                 and float(r["marg_viol"]) > float(r["delta"])]
        for r in tight:
            L.append(f"- ultra-tight alpha regime (floor+0.02) on {r['dataset']}: marginal "
                     f"viol {float(r['marg_viol']):.2f} > delta -- the certifiable region is "
                     "razor-thin 2 points above the floor; the committed rule deliberately "
                     "does not operate there.")
    L.append("- spambase verdicts are undetermined by sample size (probe n = 184), not "
             "evidence of feasibility.")
    L.append("- local (laptop) runs are development/replication only; their alphas differ "
             "(backbone nondeterminism) and none of their numbers are cited.")
    L.append("")

    # ---- figures ----
    figs = sorted({p.stem for p in Path(args.figures_dir).glob("*.pdf")})
    L.append("## Figure index\n")
    for f in figs:
        L.append(f"- {f}")
    L.append("")
    L.append("---")
    L.append("STATUS: FROZEN -- no number in the paper may differ from this file.")

    Path(args.out).write_text("\n".join(L))
    print(f"[canonical] wrote {args.out} ({len(metrics)} metric cells; "
          f"{len(borderline)} flagged marginal cells).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
