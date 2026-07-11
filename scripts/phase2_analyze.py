#!/usr/bin/env python
"""Phase 2 -- policy-quality axis analysis (frontier + lemma face + readout).

Reads all metrics_v2/*.json whose policy maps onto the epsilon axis
(greedy_entropy = 0.0, eps_greedy_eps* = eps, random = 1.0) plus the pool
caches (for the policy-quality scalar), and writes:

  analysis_v2/phase2_summary.csv   -- long format: one row per (dataset, eps, lambda_ref)
  analysis_v2/PHASE2_READOUT.md    -- per-dataset monotonicity tables, aggregate
                                      Spearman stats, gates, fork verdict (1/2/3)
  figures_v2/F3_phase2_<ds>.*      -- concentration vs eps (strata / IQR / entropy)
  figures_v2/F3_phase2_frontier.*  -- detection frontier vs quality_auc
  figures_v2/F4_phase2.*           -- lemma face: (n_q, Delta) vs log(2/delta) guide

Metric families (Phase-2 instructions):
  (A) quality_auc  = normalized area under acc_at_budget (accuracy-per-depth;
                     NOT a concentration metric -- avoids tautology);
      steps_to_90  = smallest depth k with acc_at_budget[k] >= 0.9 * acc_full
                     (population-curve definition; stated in the readout).
  (B) per lambda_ref: strata_count (populated, probe-committed edges),
      depth_iqr, depth_entropy_norm  -- read from the eval JSONs' population block.
  (C) per lambda_ref, hardest populated stratum k* (max R_full): R_full(k*),
      95% one-sided CP LCB/UCB, three-way verdict, marginal_undercoverage
      (mean over resplits of marginal realized risk on k* minus alpha),
      q = n_k*/n_eval, Delta = R_full(k*) - alpha, n_q = n_k*.
  Derived: detection frontier min_lambda_ref_detected(dataset, eps); lemma face
      over ALL (dataset, eps, lambda_ref, stratum) points with guide curve
      n_q = log(2/delta) / (2*Delta^2).

Encoding note: "not detected in range" is encoded as 1.0 (above the largest
lambda_ref 0.9) for the Spearman statistics; stated wherever used.

Usage:
    python scripts/phase2_analyze.py [--metrics-dir metrics_v2] [--out analysis_v2]
                                     [--figures figures_v2]
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

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from cafa import config  # noqa: E402
from cafa.pool import load_pool_cache  # noqa: E402
from cafa.splits import probe_eval_split  # noqa: E402

_Z = 1.96
_NOT_DETECTED = 1.0   # sentinel above lambda_ref 0.9 for "not detected in range"


def eps_of_policy(policy_token: str):
    """Map a policy token onto the epsilon axis; None if not on the axis."""
    if policy_token == "greedy_entropy":
        return 0.0
    if policy_token == "random":
        return 1.0
    if policy_token.startswith("eps_greedy_eps"):
        try:
            return float(policy_token[len("eps_greedy_eps"):])
        except ValueError:
            return None
    return None


def wilson(k: int, n: int, z: float = _Z):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def _fmt(x, nd=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "n/a"
    return f"{x:.{nd}f}"


def quality_metrics(cache_path: Path, probe_frac: float, probe_seed: int):
    """(A) quality_auc + steps_to_90 from a pool cache's EVAL rows (cost-free)."""
    cache = load_pool_cache(cache_path)
    n = cache["scores"].shape[0]
    _, eval_pos = probe_eval_split(np.arange(n), probe_frac, probe_seed)
    correct = np.asarray(cache["correct"])[eval_pos]
    acc = correct.mean(axis=0)                       # acc_at_budget[k], k = 0..T
    T = acc.size - 1
    quality_auc = float(np.trapezoid(acc, dx=1.0 / T)) if hasattr(np, "trapezoid") \
        else float(np.trapz(acc, dx=1.0 / T))
    target = 0.9 * acc[-1]
    hit = np.flatnonzero(acc >= target)
    steps_to_90 = int(hit[0]) if hit.size else T
    return quality_auc, steps_to_90


def collect(metrics_dir: Path, paths, cfg):
    """Gather per-(dataset, eps) records from metrics JSONs + pool caches."""
    pv = cfg.get("protocol_v2", {})
    probe_frac = float(pv.get("probe_frac", 0.10))
    probe_seed = int(pv.get("probe_seed", 777))

    records = {}          # (dsname, eps) -> record dict
    lemma_rows = []       # every (dataset, eps, lambda_ref, stratum) point
    gates = []            # per (dsname, policy) gate summary
    for p in sorted(metrics_dir.glob("*.json")):
        data = json.loads(p.read_text())
        meta = data["meta"]
        dsname = meta["dsname"]
        policy = meta["policy"]
        eps = eps_of_policy(policy)
        if eps is None:
            continue    # not on the epsilon axis (e.g. score ablation)
        ts = int(meta["train_seed"])
        alpha = float(data["alpha"])
        delta = float(data["delta"])

        cache_path = (Path(paths.results_root) / "pool_v2" /
                      f"{dsname}_ts{ts}_{policy}_{meta['score']}.npz")
        if cache_path.exists():
            q_auc, steps90 = quality_metrics(cache_path, probe_frac, probe_seed)
        else:
            q_auc, steps90 = float("nan"), None

        rec = {"dsname": dsname, "policy": policy, "eps": eps, "ts": ts,
               "alpha": alpha, "delta": delta, "quality_auc": q_auc,
               "steps_to_90": steps90, "per_lr": {}}

        marg_k = marg_n = iut_k = iut_n = 0
        scheme0 = meta["schemes"][0]
        for lr_key, blk in data["lambda_refs"].items():
            pop = blk["population"]
            resplits = blk["resplits"]
            n_eval = int(pop["eval_n"])
            strata_count = sum(1 for v in pop["bucket_sizes"].values() if int(v) > 0)
            dc = pop["depth_concentration"]

            # hardest populated stratum k* = max R_full estimate
            best_k, best = None, None
            for ks, info in pop["per_stratum_full"].items():
                if info["risk"] is None or int(info["n"]) == 0:
                    continue
                if best is None or float(info["risk"]) > float(best["risk"]):
                    best_k, best = ks, info
                # lemma-face row for EVERY populated stratum
                lemma_rows.append({
                    "dsname": dsname, "eps": eps, "lambda_ref": lr_key, "stratum": ks,
                    "n_q": int(info["n"]),
                    "Delta": float(info["risk"]) - alpha,
                    "verdict": info["verdict"], "delta": delta,
                })
            if best is None:
                continue

            marg_vals = [r["marginal_per_stratum_risk"].get(best_k) for r in resplits]
            arr = np.asarray([v for v in marg_vals if v is not None], dtype=float)
            arr = arr[~np.isnan(arr)]
            marg_under = (float(arr.mean()) - alpha) if arr.size else float("nan")

            rec["per_lr"][lr_key] = {
                "strata_count": strata_count,
                "depth_iqr": dc["iqr"],
                "depth_entropy_norm": dc["norm_entropy"],
                "k_star": int(best_k),
                "R_full_kstar": float(best["risk"]),
                "cp_lcb95": best["cp_lcb95"],
                "cp_ucb95": best["cp_ucb95"],
                "verdict": best["verdict"],
                "marginal_undercoverage": marg_under,
                "q": int(best["n"]) / n_eval if n_eval else float("nan"),
                "Delta": float(best["risk"]) - alpha,
                "n_q": int(best["n"]),
            }

            # certificate gates over resplits (marginal + IUT any-stratum)
            for r in resplits:
                mr = r["schemes"][scheme0]["cafa_marginal"]["realized_risk"]
                marg_n += 1
                if mr is not None and mr > alpha:
                    marg_k += 1
                iut_n += 1
                if not r.get("iut_abstained", False):
                    ips = [v for v in r["iut_per_stratum_risk"].values() if v is not None]
                    if ips and max(ips) > alpha:
                        iut_k += 1

        # detection frontier
        detected_lrs = [float(lr) for lr, d in rec["per_lr"].items()
                        if d["verdict"] == "infeasible"]
        rec["min_lambda_ref_detected"] = min(detected_lrs) if detected_lrs else None

        _, _, m_ub = wilson(marg_k, marg_n)
        _, _, i_ub = wilson(iut_k, iut_n)
        gates.append({"dsname": dsname, "policy": policy, "eps": eps,
                      "marg_frac": marg_k / marg_n if marg_n else 0.0, "marg_ub": m_ub,
                      "marg_gate": "PASS" if m_ub <= rec["delta"] else "FAIL",
                      "iut_frac": iut_k / iut_n if iut_n else 0.0, "iut_ub": i_ub,
                      "iut_gate": "PASS" if i_ub <= rec["delta"] else "FAIL"})

        records[(dsname, eps)] = rec
    return records, lemma_rows, gates


def monotonicity_per_dataset(records):
    """Per dataset: is the frontier non-decreasing and entropy non-increasing in quality?"""
    from scipy.stats import spearmanr

    by_ds = defaultdict(list)
    for (dsname, eps), rec in records.items():
        by_ds[dsname].append(rec)
    out = {}
    for dsname, recs in by_ds.items():
        recs = sorted(recs, key=lambda r: r["quality_auc"])       # ascending quality
        q = [r["quality_auc"] for r in recs]
        frontier = [r["min_lambda_ref_detected"] if r["min_lambda_ref_detected"] is not None
                    else _NOT_DETECTED for r in recs]
        # entropy at the deepest lambda_ref present (primary: 0.9)
        ent09 = [r["per_lr"].get("0.9", {}).get("depth_entropy_norm") for r in recs]
        ent09 = [e if e is not None else float("nan") for e in ent09]
        frontier_nondec = all(frontier[i + 1] >= frontier[i] - 1e-12
                              for i in range(len(frontier) - 1))
        ent_valid = [e for e in ent09 if not math.isnan(e)]
        ent_noninc = (len(ent_valid) == len(ent09) and
                      all(ent09[i + 1] <= ent09[i] + 1e-12 for i in range(len(ent09) - 1)))
        rho_f = spearmanr(q, frontier).statistic if len(set(frontier)) > 1 else float("nan")
        out[dsname] = {"recs": recs, "quality": q, "frontier": frontier,
                       "entropy09": ent09, "frontier_nondecreasing": frontier_nondec,
                       "entropy_nonincreasing": ent_noninc, "rho_frontier": rho_f}
    return out


def aggregate_spearman(records):
    from scipy.stats import spearmanr

    pts = list(records.values())
    q = [r["quality_auc"] for r in pts]
    frontier = [r["min_lambda_ref_detected"] if r["min_lambda_ref_detected"] is not None
                else _NOT_DETECTED for r in pts]
    out = {"n_points": len(pts)}
    out["frontier"] = spearmanr(q, frontier)
    for lr in ("0.5", "0.7", "0.9"):
        ent = [r["per_lr"].get(lr, {}).get("depth_entropy_norm") for r in pts]
        keep = [(a, b) for a, b in zip(q, ent) if b is not None]
        if len(keep) >= 3:
            out[f"entropy_{lr}"] = spearmanr([a for a, _ in keep], [b for _, b in keep])
    return out


def fork_verdict(mono):
    supporting = [ds for ds, m in mono.items()
                  if m["frontier_nondecreasing"] and m["entropy_nonincreasing"]]
    n = len(mono)
    if len(supporting) == n and n > 0:
        v = 1
        txt = ("MONOTONE (outcome 1): on all datasets the detection frontier is "
               "non-decreasing and depth entropy non-increasing in policy quality.")
    elif supporting:
        v = 2
        txt = (f"MIXED (outcome 2): monotone on {len(supporting)} of {n} datasets "
               f"({', '.join(sorted(supporting))}); reported as an observation at "
               "that strength, carried by the frontier figure's nuance.")
    else:
        v = 3
        txt = ("FLAT/REVERSED (outcome 3): no dataset shows the monotone pattern; "
               "the concentration claim is dropped from the headline (paper stands "
               "on audit + IUT + H2).")
    return v, txt, supporting


# --------------------------------------------------------------------------- #
# Figures
# --------------------------------------------------------------------------- #
def fig_concentration(records, fig_dir: Path):
    by_ds = defaultdict(list)
    for (dsname, eps), rec in records.items():
        by_ds[dsname].append(rec)
    for dsname, recs in by_ds.items():
        recs = sorted(recs, key=lambda r: r["eps"])
        lrs = sorted({lr for r in recs for lr in r["per_lr"]}, key=float)
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        for lr in lrs:
            xs = [r["eps"] for r in recs if lr in r["per_lr"]]
            sc = [r["per_lr"][lr]["strata_count"] for r in recs if lr in r["per_lr"]]
            iq = [r["per_lr"][lr]["depth_iqr"] for r in recs if lr in r["per_lr"]]
            en = [r["per_lr"][lr]["depth_entropy_norm"] for r in recs if lr in r["per_lr"]]
            axes[0].plot(xs, sc, marker="o", label=f"lr={lr}")
            axes[1].plot(xs, iq, marker="s", label=f"lr={lr}")
            axes[2].plot(xs, en, marker="^", label=f"lr={lr}")
        for ax, ttl in zip(axes, ("strata_count", "depth_IQR", "depth_entropy_norm")):
            ax.set_xlabel("epsilon (0 = greedy, 1 = random)")
            ax.set_ylabel(ttl)
            ax.set_title(ttl)
            ax.legend(fontsize=8)
        fig.suptitle(f"F3 (phase 2) concentration vs epsilon -- {dsname} ts0")
        fig.tight_layout()
        fig.savefig(fig_dir / f"F3_phase2_{dsname}.pdf")
        fig.savefig(fig_dir / f"F3_phase2_{dsname}.png", dpi=150)
        plt.close(fig)


def fig_frontier(records, fig_dir: Path):
    by_ds = defaultdict(list)
    for (dsname, eps), rec in records.items():
        by_ds[dsname].append(rec)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for dsname, recs in sorted(by_ds.items()):
        recs = sorted(recs, key=lambda r: r["quality_auc"])
        xs = [r["quality_auc"] for r in recs]
        ys, det = [], []
        for r in recs:
            f = r["min_lambda_ref_detected"]
            ys.append(f if f is not None else _NOT_DETECTED)
            det.append(f is not None)
        line, = ax.plot(xs, ys, marker="o", label=dsname)
        for x, y, d in zip(xs, ys, det):
            if not d:
                ax.plot([x], [y], marker="o", mfc="white", mec=line.get_color())
    ax.axhline(_NOT_DETECTED, linestyle=":", linewidth=1)
    ax.text(0.01, _NOT_DETECTED + 0.005, "not detected in range (encoded 1.0)",
            fontsize=7, transform=ax.get_yaxis_transform())
    ax.set_xlabel("quality_auc (higher = better policy)")
    ax.set_ylabel("min lambda_ref with detection")
    ax.set_title("F3 (phase 2) detection frontier vs policy quality (ts0)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "F3_phase2_frontier.pdf")
    fig.savefig(fig_dir / "F3_phase2_frontier.png", dpi=150)
    plt.close(fig)


def fig_lemma(lemma_rows, fig_dir: Path):
    if not lemma_rows:
        return
    delta = lemma_rows[0]["delta"]
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    tags = (("infeasible", "x", "detected (LCB > alpha)"),
            ("undetermined", "o", "undetermined"),
            ("feasible", "s", "feasible (UCB < alpha)"))
    for verdict, marker, label in tags:
        xs = [r["n_q"] for r in lemma_rows if r["verdict"] == verdict and r["n_q"] > 0]
        ys = [r["Delta"] for r in lemma_rows if r["verdict"] == verdict and r["n_q"] > 0]
        if xs:
            ax.scatter(xs, ys, marker=marker, s=22, label=label)
    xmax = max(r["n_q"] for r in lemma_rows if r["n_q"] > 0)
    xg = np.logspace(0.5, math.log10(max(xmax, 10.0)), 120)
    ax.plot(xg, np.sqrt(math.log(2.0 / delta) / (2.0 * xg)), "k--",
            label="guide: n_q = log(2/delta)/(2 Delta^2)")
    ax.axhline(0.0, linewidth=0.6, color="gray")
    ax.set_xscale("log")
    ax.set_xlabel("n_q = n_eval * q (log)")
    ax.set_ylabel("Delta = R_full(k) - alpha")
    ax.set_title("F4 (phase 2) detection power -- lemma face (ts0)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(fig_dir / "F4_phase2.pdf")
    fig.savefig(fig_dir / "F4_phase2.png", dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Outputs
# --------------------------------------------------------------------------- #
def write_summary_csv(records, out_dir: Path):
    rows = [("dataset", "eps", "alpha", "quality_auc", "steps_to_90", "lambda_ref",
             "strata_count", "depth_iqr", "depth_entropy_norm", "k_star",
             "R_full_kstar", "cp_lcb95", "cp_ucb95", "verdict",
             "marginal_undercoverage", "q", "Delta", "n_q",
             "min_lambda_ref_detected")]
    for (dsname, eps), rec in sorted(records.items()):
        for lr_key in sorted(rec["per_lr"], key=float):
            d = rec["per_lr"][lr_key]
            rows.append((dsname, eps, rec["alpha"], rec["quality_auc"],
                         rec["steps_to_90"], lr_key, d["strata_count"], d["depth_iqr"],
                         d["depth_entropy_norm"], d["k_star"], d["R_full_kstar"],
                         d["cp_lcb95"], d["cp_ucb95"], d["verdict"],
                         d["marginal_undercoverage"], d["q"], d["Delta"], d["n_q"],
                         rec["min_lambda_ref_detected"]))
    with open(out_dir / "phase2_summary.csv", "w", newline="") as f:
        csv.writer(f).writerows(rows)


def write_readout(records, mono, agg, verdict, gates, out_dir: Path, determinism_note):
    v_num, v_txt, supporting = verdict
    lines = []
    lines.append("# CAFA v2 -- PHASE 2 READOUT (policy-quality axis)\n")
    lines.append("_Generated by scripts/phase2_analyze.py from metrics_v2/*.json + pool "
                 "caches. All values computed from data._\n")
    lines.append("Quality is measured by accuracy-per-depth (quality_auc = normalized "
                 "area under acc_at_budget; steps_to_90 = smallest depth reaching 90% of "
                 "full-acquisition accuracy on the population curve), independently of "
                 "how depths are distributed -- so 'better policy -> harder to detect' "
                 "is a claim, not a definition.\n")

    lines.append("## Fork verdict\n")
    lines.append(f"**Outcome {v_num}** -- {v_txt}\n")

    lines.append("## Per-dataset monotonicity (points ordered by quality_auc, ascending)\n")
    for dsname, m in sorted(mono.items()):
        lines.append(f"### {dsname}\n")
        lines.append("| eps | quality_auc | steps_to_90 | entropy@0.5 | entropy@0.7 | "
                     "entropy@0.9 | strata@0.9 | IQR@0.9 | frontier (min lr detected) |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for r in m["recs"]:
            e = {lr: r["per_lr"].get(lr, {}) for lr in ("0.5", "0.7", "0.9")}
            f = r["min_lambda_ref_detected"]
            lines.append(
                f"| {r['eps']:g} | {_fmt(r['quality_auc'])} | {r['steps_to_90']} | "
                f"{_fmt(e['0.5'].get('depth_entropy_norm'))} | "
                f"{_fmt(e['0.7'].get('depth_entropy_norm'))} | "
                f"{_fmt(e['0.9'].get('depth_entropy_norm'))} | "
                f"{e['0.9'].get('strata_count', 'n/a')} | "
                f"{_fmt(e['0.9'].get('depth_iqr'), 1)} | "
                f"{f if f is not None else 'not detected in range'} |")
        lines.append("")
        lines.append(f"- frontier non-decreasing in quality: "
                     f"**{m['frontier_nondecreasing']}**; entropy@0.9 non-increasing: "
                     f"**{m['entropy_nonincreasing']}** "
                     f"(per-dataset Spearman rho(quality, frontier) = "
                     f"{_fmt(m['rho_frontier'], 3)})")
        lines.append("")

    lines.append("## Aggregate statistics (all (dataset, eps) points; 'not detected' "
                 "encoded as 1.0)\n")
    fr = agg["frontier"]
    lines.append(f"- Spearman quality_auc vs min_lambda_ref_detected: rho = "
                 f"{_fmt(fr.statistic, 3)}, p = {_fmt(fr.pvalue, 4)} "
                 f"(n = {agg['n_points']}; positive rho supports 'better policy -> "
                 "later detection').")
    for lr in ("0.5", "0.7", "0.9"):
        key = f"entropy_{lr}"
        if key in agg:
            s = agg[key]
            lines.append(f"- Spearman quality_auc vs depth_entropy_norm@{lr}: rho = "
                         f"{_fmt(s.statistic, 3)}, p = {_fmt(s.pvalue, 4)} "
                         "(negative rho supports 'better policy -> more concentration').")
    lines.append("- Power caveat: 4-6 epsilon points per dataset is limited; the "
                 "aggregate correlation plus the lemma-face figure carry the claim, "
                 "not any single dataset.\n")

    lines.append("## Certificate gates on the epsilon cells (delta = 0.10, Wilson UB)\n")
    lines.append("| cell | marginal viol [UB] | gate | IUT any-stratum viol [UB] | gate |")
    lines.append("|---|---|---|---|---|")
    for g in sorted(gates, key=lambda g: (g["dsname"], g["eps"])):
        lines.append(f"| {g['dsname']}/eps={g['eps']:g} | "
                     f"{_fmt(g['marg_frac'], 3)} [{_fmt(g['marg_ub'], 3)}] | "
                     f"{g['marg_gate']} | {_fmt(g['iut_frac'], 3)} "
                     f"[{_fmt(g['iut_ub'], 3)}] | {g['iut_gate']} |")
    lines.append("")
    lines.append("> Resplits share a finite eval pool; intervals are heuristic under "
                 "dependence. Borderline cells must be flagged, not smoothed over.\n")

    lines.append("## Determinism / invariant checks\n")
    lines.append(determinism_note if determinism_note else
                 "_No determinism-check record found (analysis_v2/phase2_determinism.txt "
                 "missing); run the rollout re-run check._")
    lines.append("")
    lines.append("- Cost-blindness is structural: the rollout never consults feature "
                 "costs; per-scheme costs are recomputed post-hoc from the cached "
                 "`order` (`cafa.pool.cum_cost_from_order`), so trajectories are "
                 "cost-scheme-invariant by construction.")
    lines.append("- Stratum edges for the epsilon policies were extended into the "
                 "committed JSONs from the probe split (seed 777) via probe_commit "
                 "--extend-edges BEFORE any eval selection; the eval sweep loads them "
                 "from JSON and never refits on selection cal.")

    (out_dir / "PHASE2_READOUT.md").write_text("\n".join(lines))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAFA v2 Phase-2 analysis.")
    ap.add_argument("--metrics-dir", default="metrics_v2")
    ap.add_argument("--out", default="analysis_v2")
    ap.add_argument("--figures", default="figures_v2")
    args = ap.parse_args(argv)

    cfg = config.load_experiment()
    paths = config.load_paths()
    metrics_dir = Path(args.metrics_dir)
    out_dir = Path(args.out)
    fig_dir = Path(args.figures)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    records, lemma_rows, gates = collect(metrics_dir, paths, cfg)
    if not records:
        print(f"ERROR: no epsilon-axis metrics found under {metrics_dir}.", file=sys.stderr)
        return 2
    eps_per_ds = defaultdict(set)
    for (dsname, eps) in records:
        eps_per_ds[dsname].add(eps)
    print("[phase2] axis points:",
          {ds: sorted(v) for ds, v in sorted(eps_per_ds.items())}, flush=True)

    mono = monotonicity_per_dataset(records)
    agg = aggregate_spearman(records)
    verdict = fork_verdict(mono)

    det_path = out_dir / "phase2_determinism.txt"
    determinism_note = det_path.read_text().strip() if det_path.exists() else None

    write_summary_csv(records, out_dir)
    write_readout(records, mono, agg, verdict, gates, out_dir, determinism_note)
    fig_concentration(records, fig_dir)
    fig_frontier(records, fig_dir)
    fig_lemma(lemma_rows, fig_dir)

    print(f"[phase2] fork verdict: outcome {verdict[0]} "
          f"(supporting datasets: {verdict[2] or 'none'})", flush=True)
    print(f"[phase2] wrote {out_dir / 'PHASE2_READOUT.md'}, phase2_summary.csv, "
          f"F3_phase2_*/F3_phase2_frontier/F4_phase2 figures.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
