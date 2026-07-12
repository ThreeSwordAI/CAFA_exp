#!/usr/bin/env python
"""Phase 5.3, Task 1 -- family-wide feasibility audit on the primary stratum.

Question: for the fixed confirmatory stratum (the DEEPEST precommitted
nonempty bucket -- label-free), does EVERY stopping threshold in the
precommitted grid exceed alpha, or does only the full-feature endpoint fail?

Per (cell, lambda_ref) this computes, on the whole evaluation pool:
  * the threshold-family risk curve R_pool,k(lambda) at all 100 committed
    thresholds: empirical minimum, argmin threshold(s), full-feature endpoint,
    monotonicity, local minima, gap to alpha, cost at the argmin;
  * the forced-depth risk curve R_pool,k,t for t = 0..T: minimum, argmin
    depth, risk at T, cost at the minimizing depth, monotonicity violations;
  * simultaneous (intersection-union) family-wide inference: per threshold
    the exact one-sided binomial upper-tail p-value P(Bin(n_k, alpha) >= s);
    p_family = max over the family; reject feasibility at level gamma only if
    p_family <= gamma. Same construction over depths. No independence across
    thresholds is required.

Verdicts (the mandatory decision table):
  empirical min <= alpha                     -> "feasible" (family failure FALSE)
  min > alpha but p_family > gamma           -> "unresolved"
  min > alpha and p_family <= gamma          -> "family-wide failure certified"

Wording discipline is embedded in the outputs: threshold-family failure
licenses only "no stopping threshold in the audited precommitted family";
depth-family failure only "no prefix depth along the frozen acquisition
path"; neither licenses any claim about arbitrary subsets/policies/budgets.
Per-dataset p-values are reported separately (no cross-dataset FWER claim).

Endpoint reproduction gate (spec 14.3): before any family result, the
recomputed per-stratum full-feature counts and risks must reproduce the
frozen per_stratum_full values exactly for the four primary cells.

Outputs (to --output-dir): FAMILY_WIDE_FEASIBILITY.md,
family_wide_threshold_curves.csv, family_wide_depth_curves.csv,
family_wide_summary.csv/.json, figures/F8_family_threshold_<ds>.pdf,
figures/F9_family_depth_<ds>.pdf.

Usage:
    python scripts/family_wide_feasibility.py --all-primary --all-thresholds \
        --all-depths --gamma 0.05 --metrics-dir results_committed/metrics \
        --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase53_lib as L  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from cafa import config  # noqa: E402

_LRS = ("0.5", "0.7", "0.9")
_PRIMARY_LR = "0.9"


def local_minima(r: np.ndarray, tol: float = 1e-12):
    """Indices of strict-ish local minima (plateaus collapse to their first index)."""
    mins = []
    G = r.size
    for i in range(G):
        left = r[i - 1] if i > 0 else np.inf
        right = r[i + 1] if i < G - 1 else np.inf
        if r[i] < left + tol and r[i] < right + tol and (r[i] < left - tol or r[i] < right - tol):
            mins.append(i)
    return mins


def audit_family(losses_k: np.ndarray, alpha: float, gamma: float):
    """(curve stats, p_family, verdict) for one 0/1 loss family [n_k, F]."""
    n_k = losses_k.shape[0]
    s = losses_k.sum(axis=0)                       # errors per family member
    r = s / n_k
    p = L.binom_upper_p(s, n_k, alpha)
    p_family = float(p.max())
    rmin = float(r.min())
    argmins = np.flatnonzero(np.isclose(r, rmin)).tolist()
    if rmin <= alpha:
        verdict = "feasible"
    elif p_family <= gamma:
        verdict = "family-wide failure certified"
    else:
        verdict = "unresolved"
    return r, p, p_family, rmin, argmins, verdict


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase 5.3 family-wide feasibility audit.")
    ap.add_argument("--all-primary", action="store_true",
                    help="primary + sensitivity: every canonical cell x lambda_ref.")
    ap.add_argument("--all-thresholds", action="store_true")
    ap.add_argument("--all-depths", action="store_true")
    ap.add_argument("--gamma", type=float, default=0.05)
    ap.add_argument("--metrics-dir", default="results_committed/metrics")
    ap.add_argument("--pool-dir", default=None)
    ap.add_argument("--output-dir", default="results_committed")
    args = ap.parse_args(argv)

    cfg = config.load_experiment()
    pool_dir = Path(args.pool_dir) if args.pool_dir else L.default_pool_dir()
    out_dir = Path(args.output_dir)
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    gamma = float(args.gamma)

    cells = L.load_cells(Path(args.metrics_dir))

    # ---- 14.3 endpoint reproduction gate (primary cells) ----
    for c in cells:
        if not (c["ts"] == 0 and c["policy"] == "greedy_entropy" and c["score"] == "softmax"):
            continue
        evald = L.load_eval_arrays(c, cfg, pool_dir)
        committed = L.committed_for(c["dsname"], 0)
        pop = c["data"]["lambda_refs"][_PRIMARY_LR]["population"]["per_stratum_full"]
        edges = L.edges_for(committed, c["policy"], c["score"], _PRIMARY_LR)
        bucket = L.bucket_ids(evald["scores"], float(_PRIMARY_LR), edges)
        full_loss = 1.0 - evald["correct"][:, evald["T"]]
        for ks, info in pop.items():
            mask = bucket == int(ks)
            n_rec = int(mask.sum())
            assert n_rec == int(info["n"]), (
                f"ENDPOINT REPRODUCTION FAIL {c['label']} stratum {ks}: "
                f"n {n_rec} != frozen {info['n']}")
            if info["risk"] is not None and n_rec:
                r_rec = float(full_loss[mask].mean())
                assert abs(r_rec - float(info["risk"])) < 5e-7, (
                    f"ENDPOINT REPRODUCTION FAIL {c['label']} stratum {ks}: "
                    f"risk {r_rec} != frozen {info['risk']}")
        print(f"[family] endpoint reproduction PASS: {c['label']}", flush=True)

    # ---- the audit ----
    summary, thr_rows, dep_rows = [], [], []
    primary_curves = {}
    for c in cells:
        evald = L.load_eval_arrays(c, cfg, pool_dir)
        committed = L.committed_for(c["dsname"], c["ts"])
        scheme = L.primary_scheme(c["meta"])
        losses_full, costs_full, cc, _ = L.losses_costs(evald, c["grid"], scheme)
        alpha = c["alpha"]
        full_loss = 1.0 - evald["correct"][:, evald["T"]]
        for lr_key in _LRS:
            edges = L.edges_for(committed, c["policy"], c["score"], lr_key)
            bucket = L.bucket_ids(evald["scores"], float(lr_key), edges)
            k_deep = L.deepest_nonempty(bucket)
            mask = bucket == k_deep
            n_k = int(mask.sum())

            # threshold family
            r, p, p_fam, rmin, argmins, verdict = audit_family(losses_full[mask], alpha, gamma)
            cost_at_min = float(costs_full[mask][:, argmins[0]].mean())
            mono = bool(np.all(np.diff(r) <= 1e-12))
            lmins = local_minima(r)
            full_r = float(full_loss[mask].mean())

            # depth family
            depth_losses = 1.0 - evald["correct"][mask]          # [n_k, T+1]
            rd, pd, p_dep, rdmin, dargmins, dverdict = audit_family(depth_losses, alpha, gamma)
            dmono_viol = int(np.sum(np.diff(rd) > 1e-12))
            cost_at_dmin = float(cc[mask][:, dargmins[0]].mean())

            is_primary = (c["ts"] == 0 and c["policy"] == "greedy_entropy"
                          and c["score"] == "softmax" and lr_key == _PRIMARY_LR)
            summary.append({
                "cell": c["label"], "dataset": c["dsname"], "seed": c["ts"],
                "policy": c["policy"], "score": c["score"], "lambda_ref": lr_key,
                "stratum": k_deep, "stratum_rule": "deepest precommitted nonempty",
                "n_k": n_k, "alpha": alpha, "gamma": gamma,
                "min_threshold_risk": rmin,
                "argmin_lambda": float(c["grid"][argmins[0]]),
                "n_argmin_thresholds": len(argmins),
                "cost_at_argmin": cost_at_min,
                "full_feature_risk": full_r,
                "threshold_curve_monotone": mono,
                "n_local_minima": len(lmins),
                "gap_min_minus_alpha": rmin - alpha,
                "family_p_value": p_fam,
                "threshold_verdict": verdict,
                "min_depth_risk": rdmin,
                "argmin_depth": int(dargmins[0]),
                "risk_at_T": float(rd[-1]),
                "cost_at_argmin_depth": cost_at_dmin,
                "depth_monotonicity_violations": dmono_viol,
                "depth_p_value": p_dep,
                "depth_verdict": dverdict,
                "is_primary": is_primary,
            })
            for j, lam in enumerate(c["grid"]):
                thr_rows.append({"cell": c["label"], "lambda_ref": lr_key,
                                 "stratum": k_deep, "lambda": float(lam),
                                 "R_pool_k": float(r[j]), "p_upper": float(p[j])})
            for t in range(evald["T"] + 1):
                dep_rows.append({"cell": c["label"], "lambda_ref": lr_key,
                                 "stratum": k_deep, "depth": t,
                                 "R_pool_k_t": float(rd[t]), "p_upper": float(pd[t])})
            if is_primary:
                primary_curves[c["dsname"]] = (c["grid"], r, rd, alpha, k_deep, n_k)
            if is_primary:
                print(f"[family] {c['dsname']} PRIMARY lr={lr_key} stratum {k_deep} "
                      f"(n={n_k}): min thr risk {rmin:.4f} @ lambda "
                      f"{float(c['grid'][argmins[0]]):.3f}, p_family {p_fam:.2e} -> "
                      f"{verdict}; min depth risk {rdmin:.4f} @ t={dargmins[0]}, "
                      f"p_depth {p_dep:.2e} -> {dverdict}", flush=True)

    # ---- write CSVs / JSON ----
    def wcsv(name, rows):
        with open(out_dir / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    wcsv("family_wide_summary.csv", summary)
    wcsv("family_wide_threshold_curves.csv", thr_rows)
    wcsv("family_wide_depth_curves.csv", dep_rows)
    (out_dir / "family_wide_summary.json").write_text(json.dumps(
        {"header": L.provenance_header({"gamma": gamma}), "summary": summary}, indent=2))

    # ---- figures F8/F9 (primary cells) ----
    for dsname, (grid, r, rd, alpha, k_deep, n_k) in primary_curves.items():
        fig, ax = plt.subplots(figsize=(6.5, 4.2))
        ax.plot(grid, r, marker=".", markersize=3, linewidth=1)
        ax.axhline(alpha, linestyle="--", color="k", label=f"alpha = {alpha:g}")
        j = int(np.argmin(r))
        ax.scatter([grid[j]], [r[j]], marker="*", s=140, zorder=5,
                   label=f"min {r[j]:.4f} @ lambda {grid[j]:.3f}")
        ax.set_xlabel("stopping threshold lambda")
        ax.set_ylabel(f"pool risk on deepest stratum (k={k_deep}, n={n_k})")
        ax.set_title(f"F8 threshold-family risk -- {dsname} ts0 greedy, lr={_PRIMARY_LR}")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(fig_dir / f"F8_family_threshold_{dsname}.pdf")
        fig.savefig(fig_dir / f"F8_family_threshold_{dsname}.png", dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(6.5, 4.2))
        ax.plot(np.arange(rd.size), rd, marker=".", markersize=3, linewidth=1)
        ax.axhline(alpha, linestyle="--", color="k", label=f"alpha = {alpha:g}")
        t = int(np.argmin(rd))
        ax.scatter([t], [rd[t]], marker="*", s=140, zorder=5,
                   label=f"min {rd[t]:.4f} @ depth {t}")
        ax.set_xlabel("forced acquisition depth t")
        ax.set_ylabel(f"pool risk on deepest stratum (k={k_deep})")
        ax.set_title(f"F9 forced-depth risk -- {dsname} ts0 greedy, lr={_PRIMARY_LR}")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(fig_dir / f"F9_family_depth_{dsname}.pdf")
        fig.savefig(fig_dir / f"F9_family_depth_{dsname}.png", dpi=150)
        plt.close(fig)

    # ---- markdown ----
    prim = [s for s in summary if s["is_primary"]]
    lines = ["# CAFA v2 -- FAMILY-WIDE FEASIBILITY AUDIT (Phase 5.3, Task 1)\n",
             f"_Confirmatory stratum = deepest precommitted nonempty bucket "
             f"(label-free). Intersection-union test over the full committed family; "
             f"exact one-sided binomial upper-tail p-values; audit level gamma = "
             f"{gamma:g}. Per-dataset p-values reported separately -- no cross-dataset "
             "FWER claim is made._\n",
             "## Primary cells (ts0, greedy, softmax, lambda_ref = 0.9)\n",
             "| dataset | stratum (n_k) | alpha | min THRESHOLD risk (argmin lambda) | "
             "full risk | p_family | THRESHOLD verdict | min DEPTH risk (argmin t) | "
             "p_depth | DEPTH verdict |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for s in prim:
        lines.append(
            f"| {s['dataset']} | {s['stratum']} ({s['n_k']}) | {s['alpha']:g} | "
            f"{L.fmt(s['min_threshold_risk'])} ({s['argmin_lambda']:.3f}) | "
            f"{L.fmt(s['full_feature_risk'])} | {s['family_p_value']:.2e} | "
            f"**{s['threshold_verdict']}** | {L.fmt(s['min_depth_risk'])} "
            f"({s['argmin_depth']}) | {s['depth_p_value']:.2e} | **{s['depth_verdict']}** |")
    lines.append("")
    lines.append("Wording licensed by each verdict: threshold-family failure -> 'no "
                 "stopping threshold in the audited precommitted threshold family "
                 "attains the target'; depth-family failure -> 'no prefix depth along "
                 "the frozen acquisition path attains the target'. NEITHER licenses "
                 "'no possible feature subset, policy, acquisition strategy, or budget'.\n")
    lines.append(f"## Sensitivity grid ({len(summary)} configurations; all cells x "
                 "lambda_refs)\n")
    lines.append("Full grid in `family_wide_summary.csv`; verdict counts:")
    from collections import Counter
    tc = Counter(s["threshold_verdict"] for s in summary)
    dc = Counter(s["depth_verdict"] for s in summary)
    lines.append(f"- threshold-family verdicts: {dict(tc)}")
    lines.append(f"- depth-family verdicts: {dict(dc)}")
    mono_frac = np.mean([s["threshold_curve_monotone"] for s in summary])
    lines.append(f"- threshold curves monotone nonincreasing: {mono_frac:.2f} of configs; "
                 "local-minima counts in the CSV.")
    (out_dir / "FAMILY_WIDE_FEASIBILITY.md").write_text("\n".join(lines))
    print(f"[family] wrote FAMILY_WIDE_FEASIBILITY.md + 3 CSVs + JSON + F8/F9 "
          f"({len(summary)} configs; primary threshold verdicts: "
          f"{[ (s['dataset'], s['threshold_verdict']) for s in prim ]}).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
