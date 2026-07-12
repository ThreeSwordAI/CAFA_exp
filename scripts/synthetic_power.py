#!/usr/bin/env python
"""Phase 5.3, Task 6 -- controlled synthetic power validation (Bernoulli).

Prospectively validates the detection-power behavior of the one-sided exact
Clopper-Pearson audit when stratum mass q, risk margin Delta, and total
sample size n are CONTROLLED (the existing detection table is retrospective).
The only genuinely new experiment of the phase; no network training.

Per grid point (q, Delta, n), B repetitions:
  1. n_k ~ Binomial(n, q);  n_k = 0 -> unresolved;
  2. S_k ~ Binomial(n_k, alpha + Delta) (clipped to [0, 1] risk);
  3. CP one-sided lower bound at level gamma;  detect iff LB > alpha.
Null calibration at Delta = 0 and Delta = -0.02 gives the empirical
false-positive rate (must be <= gamma up to MC noise).

The theorem's sufficient threshold n*q >= log(1/gamma) / (2 Delta^2) is
reported alongside -- interpreted as SUFFICIENT (conservative), never as the
minimum required sample size.

Optional family-size calibration (--family): for family sizes M in
{10, 50, 100}, all-infeasible families vs families with one feasible member,
rejection rate of the family IUT p-value max_m p_m -- labeled a calibration
study, not a proof.

Outputs (to --output-dir): SYNTHETIC_POWER.md, synthetic_power.csv,
synthetic_power_summary.json, figures/F14_power_heatmap_q_delta_<n>.pdf,
figures/F15_power_vs_n.pdf.

Usage:
    python scripts/synthetic_power.py --alpha 0.15 --gamma 0.05 \
        --repetitions 5000 --output-dir results_committed
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase53_lib as L  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

_QS = (0.02, 0.05, 0.10, 0.20, 0.40)
_DELTAS = (0.01, 0.02, 0.05, 0.08, 0.10, 0.15)
_NULLS = (0.0, -0.02)
_NS = (500, 1000, 2500, 5000, 10000, 25000, 50000)
_SEED = 20260712


def run_grid_point(n: int, q: float, delta_eff: float, alpha: float, gamma: float,
                   B: int, rng: np.random.Generator) -> dict:
    """Vectorized MC for one (n, q, Delta): detection = CP one-sided LB > alpha."""
    risk = float(np.clip(alpha + delta_eff, 0.0, 1.0))
    n_k = rng.binomial(int(n), float(q), size=B)
    unresolved = n_k == 0
    s = np.zeros(B, dtype=np.int64)
    pos = ~unresolved
    s[pos] = rng.binomial(n_k[pos], risk)
    # CP one-sided lower bound: 0 when s == 0, else Beta(gamma; s, n_k - s + 1).
    lb = np.zeros(B, dtype=float)
    nz = pos & (s > 0)
    lb[nz] = beta.ppf(gamma, s[nz], n_k[nz] - s[nz] + 1)
    detect = pos & (lb > alpha)
    k = int(detect.sum())
    p, lo, hi = L.wilson(k, B)
    n_req = np.log(1.0 / gamma) / (2.0 * delta_eff ** 2) if delta_eff > 0 else float("inf")
    return {
        "n": int(n), "q": float(q), "Delta": float(delta_eff), "risk": risk,
        "B": int(B), "power": p, "mc_lo": lo, "mc_hi": hi,
        "unresolved_frac": float(unresolved.mean()),
        "mean_n_k": float(n_k.mean()),
        "p5_n_k": float(np.percentile(n_k, 5)), "p95_n_k": float(np.percentile(n_k, 95)),
        "theorem_sufficient_nq": (None if not np.isfinite(n_req) else float(n_req)),
        "nq": float(n * q),
        "above_sufficient": (None if not np.isfinite(n_req) else bool(n * q >= n_req)),
    }


def family_calibration(alpha: float, gamma: float, B: int, rng: np.random.Generator):
    """Optional family-size study: IUT max-p over M Bernoulli thresholds."""
    from scipy.stats import binom as _binom
    rows = []
    n_k = 2000
    for M in (10, 50, 100):
        for scenario, risks in (("all_infeasible", np.full(M, alpha + 0.05)),
                                ("one_feasible", np.concatenate(
                                    [[alpha - 0.05], np.full(M - 1, alpha + 0.05)]))):
            rej = 0
            for _ in range(B):
                s = rng.binomial(n_k, risks)
                p = _binom.sf(s - 1, n_k, alpha)
                if float(np.max(p)) <= gamma:
                    rej += 1
            p_, lo, hi = L.wilson(rej, B)
            rows.append({"M": M, "scenario": scenario, "n_k": n_k,
                         "family_reject_rate": p_, "lo": lo, "hi": hi})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase 5.3 synthetic power validation.")
    ap.add_argument("--alpha", type=float, default=0.15)
    ap.add_argument("--gamma", type=float, default=0.05)
    ap.add_argument("--repetitions", type=int, default=5000)
    ap.add_argument("--family", action="store_true", default=True)
    ap.add_argument("--seed", type=int, default=_SEED)
    ap.add_argument("--output-dir", default="results_committed")
    args = ap.parse_args(argv)

    out_dir = Path(args.output_dir)
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(int(args.seed))
    B = int(args.repetitions)
    alpha, gamma = float(args.alpha), float(args.gamma)

    rows = []
    for n in _NS:
        for q in _QS:
            for d in list(_DELTAS) + list(_NULLS):
                rows.append(run_grid_point(n, q, d, alpha, gamma, B, rng))
    fps = [r for r in rows if r["Delta"] <= 0.0]
    max_fpr = max(r["power"] for r in fps)
    fam_rows = family_calibration(alpha, gamma, min(B, 2000), rng) if args.family else []

    with open(out_dir / "synthetic_power.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    (out_dir / "synthetic_power_summary.json").write_text(json.dumps({
        "header": L.provenance_header({"alpha": alpha, "gamma": gamma, "B": B,
                                       "seed": int(args.seed)}),
        "max_false_positive_rate_over_nulls": max_fpr,
        "n_grid_points": len(rows),
        "family_calibration": fam_rows,
    }, indent=2))

    lines = ["# CAFA v2 -- CONTROLLED SYNTHETIC POWER VALIDATION (Phase 5.3, Task 6)\n",
             f"_Bernoulli simulation; alpha = {alpha:g}, one-sided audit gamma = "
             f"{gamma:g}, B = {B} repetitions per grid point, seed {args.seed}. "
             "Detection = one-sided exact CP lower bound > alpha. The theorem "
             "threshold n*q >= log(1/gamma)/(2 Delta^2) is SUFFICIENT (conservative), "
             "never a minimum requirement._\n",
             f"**False-positive control: max empirical FPR over all null points "
             f"(Delta in {{0, -0.02}}, every (n, q)) = {max_fpr:.4f} <= gamma = "
             f"{gamma:g}: {'PASS' if max_fpr <= gamma + 3 * (gamma / B) ** 0.5 else 'CHECK'}.**\n",
             "Selected operating points (full grid in synthetic_power.csv):\n",
             "| n | q | Delta | power [MC 95%] | unresolved | mean n_k | n*q | sufficient n*q | above? |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["Delta"] in (0.02, 0.05, 0.10) and r["q"] in (0.05, 0.20) \
                and r["n"] in (1000, 10000, 50000):
            suff = ("inf" if r["theorem_sufficient_nq"] is None
                    else f"{r['theorem_sufficient_nq']:.0f}")
            above = ("n/a" if r["above_sufficient"] is None
                     else ("yes" if r["above_sufficient"] else "no"))
            lines.append(f"| {r['n']} | {r['q']:g} | {r['Delta']:g} | "
                         f"{L.fmt(r['power'], 3)} [{L.fmt(r['mc_lo'], 3)}, "
                         f"{L.fmt(r['mc_hi'], 3)}] | {L.fmt(r['unresolved_frac'], 3)} | "
                         f"{r['mean_n_k']:.0f} | {r['nq']:.0f} | {suff} | {above} |")
    lines.append("")
    if fam_rows:
        lines.append("## Family-size calibration (IUT max-p; n_k = 2000; a calibration "
                     "study, not a proof)\n")
        lines.append("| M | scenario | family reject rate [95%] |")
        lines.append("|---|---|---|")
        for r in fam_rows:
            lines.append(f"| {r['M']} | {r['scenario']} | {L.fmt(r['family_reject_rate'], 3)} "
                         f"[{L.fmt(r['lo'], 3)}, {L.fmt(r['hi'], 3)}] |")
        lines.append("")
    lines.append("Allowed interpretation: detection increases with stratum mass, risk "
                 "margin, and sample size, and the controlled simulation shows the "
                 "sufficient bound is conservative but directionally predictive. NOT "
                 "allowed: 'the theorem gives the minimum required sample size'; "
                 "'spambase proves no method could detect the failure' (the spambase "
                 "comparison remains a retrospective design diagnostic).")
    (out_dir / "SYNTHETIC_POWER.md").write_text("\n".join(lines))

    # F14 heatmaps (two representative n)
    for n_show in (2500, 25000):
        sub = [r for r in rows if r["n"] == n_show and r["Delta"] > 0]
        P = np.zeros((len(_QS), len(_DELTAS)))
        for i, q in enumerate(_QS):
            for j, d in enumerate(_DELTAS):
                P[i, j] = next(r["power"] for r in sub if r["q"] == q and r["Delta"] == d)
        fig, ax = plt.subplots(figsize=(6.2, 4.4))
        im = ax.imshow(P, aspect="auto", origin="lower", vmin=0, vmax=1, cmap="viridis")
        ax.set_xticks(range(len(_DELTAS))); ax.set_xticklabels([f"{d:g}" for d in _DELTAS])
        ax.set_yticks(range(len(_QS))); ax.set_yticklabels([f"{q:g}" for q in _QS])
        ax.set_xlabel("Delta (risk margin above alpha)"); ax.set_ylabel("q (stratum mass)")
        ax.set_title(f"F14 detection power, n = {n_show} (alpha {alpha:g}, gamma {gamma:g})")
        fig.colorbar(im, ax=ax, label="empirical power")
        fig.tight_layout()
        fig.savefig(fig_dir / f"F14_power_heatmap_q_delta_n{n_show}.pdf")
        fig.savefig(fig_dir / f"F14_power_heatmap_q_delta_n{n_show}.png", dpi=150)
        plt.close(fig)

    # F15 power vs n
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    for q, d in ((0.05, 0.02), (0.05, 0.05), (0.20, 0.02), (0.20, 0.05), (0.20, 0.10)):
        ys = [next(r["power"] for r in rows if r["n"] == n and r["q"] == q and r["Delta"] == d)
              for n in _NS]
        ax.plot(_NS, ys, marker="o", label=f"q={q:g}, Delta={d:g}")
    ax.set_xscale("log")
    ax.set_xlabel("total sample size n"); ax.set_ylabel("empirical detection power")
    ax.axhline(gamma, linestyle=":", color="gray", linewidth=0.8, label=f"gamma={gamma:g}")
    ax.set_title("F15 power vs n (one-sided CP audit)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "F15_power_vs_n.pdf")
    fig.savefig(fig_dir / "F15_power_vs_n.png", dpi=150)
    plt.close(fig)

    print(f"[power] {len(rows)} grid points, B={B}: max null FPR {max_fpr:.4f} "
          f"(gamma {gamma:g}); wrote SYNTHETIC_POWER.md + CSV + JSON + F14/F15.",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
