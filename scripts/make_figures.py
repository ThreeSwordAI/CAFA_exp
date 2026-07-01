#!/usr/bin/env python
"""Step 3 figures for per-bucket ("Mondrian") risk control.

Figure A -- synthetic gamma sweep.  Cheap-bucket *true* risk under the single
            marginal threshold vs. under per-bucket Mondrian thresholds, as a
            function of the miscalibration dial ``gamma``, with the target level
            ``alpha`` drawn in.  The marginal curve climbs above ``alpha`` across
            the early-stopping regime while Mondrian stays at/below it.  The
            full-acquisition escape boundary (~0.14, where the marginal retreats
            to acquiring everything) is annotated.
Figure B -- synthetic per-bucket bars at ``gamma_gate``.  Mean true risk per
            reference-depth bucket for marginal vs. Mondrian (top), plus the
            reference-depth histogram with bucket edges (bottom) showing the
            cheap stratum is a clean minority.
Figure C -- MNIST per-bucket realized risk, if metrics JSON files exist under
            ``${results_root}/metrics`` (written by ``run_mondrian_mnist.py``);
            skipped gracefully otherwise.

Figures are written to ``${results_root}/figures`` (or ``--out-dir``).  Figures A
and B are purely synthetic and need no datasets, so they run anywhere; only
Figure C reads the MNIST metrics.

Usage::

    python scripts/make_figures.py                 # A & B (+ C if metrics exist)
    python scripts/make_figures.py --out-dir /tmp/figs --gamma-trials 60
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.data import make_synthetic_mondrian  # noqa: E402
from cafa.metrics import (  # noqa: E402
    per_bucket_risk,
    quantile_bucket_edges,
    reference_buckets,
    reference_depth,
    stops_from_grid_np,
)
from cafa.risk_control import ltt_select, mondrian_select  # noqa: E402

ESCAPE_GAMMA = 0.138   # above this the marginal retreats to full acquisition


# --------------------------------------------------------------------------- #
# Shared synthetic harness
# --------------------------------------------------------------------------- #
def _build_pool(cfg: dict):
    """Pool-estimated quantile edges + cheap label (gamma-independent scores)."""
    T = int(cfg["T"])
    lam = float(cfg["lambda_ref"])
    nb = int(cfg["n_buckets"])
    mpb = int(cfg["min_per_bucket"])
    pool = make_synthetic_mondrian(
        n=int(cfg["pool_n"]), T=T, gamma=0.0, lambda_ref=lam,
        n_buckets=nb, min_per_bucket=mpb, seed=int(cfg["pool_seed"]),
    )
    edges = quantile_bucket_edges(pool["scores"], lam, nb)
    bid, _ = reference_buckets(pool["scores"], lam, nb, mpb, edges=edges)
    cheap = int(np.unique(bid).min())
    return pool, edges, cheap


def _resplit_true_risk(cfg, gamma, edges, n_trials, cal_seed0, test_seed0):
    """Mean *true* per-bucket risk under marginal and Mondrian over resplits.

    Returns ``(marg_mean, mond_mean)`` dicts: bucket label -> mean true risk.
    """
    T = int(cfg["T"]); lam = float(cfg["lambda_ref"])
    nb = int(cfg["n_buckets"]); mpb = int(cfg["min_per_bucket"])
    n_cal = int(cfg["n_cal"]); n_test = int(cfg["n_test"])
    grid = np.linspace(0.0, 1.0, int(cfg["grid_n"]))
    alpha = float(cfg["alpha"]); delta = float(cfg["delta"])

    marg_acc: dict = {}
    mond_acc: dict = {}
    for tr in range(n_trials):
        cal = make_synthetic_mondrian(n=n_cal, T=T, gamma=gamma, lambda_ref=lam,
                                      n_buckets=nb, min_per_bucket=mpb, seed=cal_seed0 + tr)
        tst = make_synthetic_mondrian(n=n_test, T=T, gamma=gamma, lambda_ref=lam,
                                      n_buckets=nb, min_per_bucket=mpb, seed=test_seed0 + tr)
        cb, _ = reference_buckets(cal["scores"], lam, nb, mpb, edges=edges)
        tb, _ = reference_buckets(tst["scores"], lam, nb, mpb, edges=edges)
        cl, cc, _ = stops_from_grid_np(cal["scores"], cal["correct"], cal["cum_cost"], grid)
        marg = ltt_select(cl, cc, grid, alpha, delta)
        mond = mondrian_select(cl, cc, grid, alpha, delta, cb)
        tl, _, _ = stops_from_grid_np(tst["scores"], tst["true_acc"], tst["cum_cost"], grid)
        labels = np.unique(tb)
        mr = per_bucket_risk(tl, tb, {int(k): marg.lambda_idx for k in labels})
        mo = per_bucket_risk(tl, tb, mond.lambda_idx_by_bucket)
        for k in labels:
            marg_acc.setdefault(int(k), []).append(mr[int(k)])
            mond_acc.setdefault(int(k), []).append(mo[int(k)])
    marg_mean = {k: float(np.nanmean(v)) for k, v in marg_acc.items()}
    mond_mean = {k: float(np.nanmean(v)) for k, v in mond_acc.items()}
    return marg_mean, mond_mean


# --------------------------------------------------------------------------- #
# Figures
# --------------------------------------------------------------------------- #
def figure_a(cfg, edges, cheap, out_dir, n_trials):
    alpha = float(cfg["alpha"])
    gammas = list(cfg["gamma_grid"])
    marg_cheap, mond_cheap = [], []
    for g in gammas:
        mm, om = _resplit_true_risk(cfg, g, edges, n_trials, cal_seed0=1000, test_seed0=5000)
        marg_cheap.append(mm.get(cheap, np.nan))
        mond_cheap.append(om.get(cheap, np.nan))

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(gammas, marg_cheap, "o-", color="#c0392b", label="marginal threshold")
    ax.plot(gammas, mond_cheap, "s-", color="#2471a3", label="Mondrian (per-bucket)")
    ax.axhline(alpha, color="black", ls="--", lw=1, label=f"target $\\alpha$ = {alpha:g}")
    ax.axvline(float(cfg["gamma_gate"]), color="#7f8c8d", ls=":", lw=1)
    ax.text(float(cfg["gamma_gate"]), ax.get_ylim()[1], "  gate", va="top",
            ha="left", fontsize=8, color="#7f8c8d")
    if max(gammas) >= ESCAPE_GAMMA:
        ax.axvspan(ESCAPE_GAMMA, max(gammas), color="#fdf2e9", zorder=0)
        ax.text(ESCAPE_GAMMA, alpha, "  full-acquisition escape", va="bottom",
                ha="left", fontsize=8, color="#b9770e")
    ax.set_xlabel("miscalibration $\\gamma$")
    ax.set_ylabel("cheap-bucket true risk")
    ax.set_title("Figure A -- marginal under-covers the cheap bucket; Mondrian does not")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3)
    path = out_dir / "figA_gamma_sweep.png"
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
    return path


def figure_b(cfg, pool, edges, cheap, out_dir, n_trials):
    alpha = float(cfg["alpha"]); lam = float(cfg["lambda_ref"])
    gate = float(cfg["gamma_gate"])
    mm, om = _resplit_true_risk(cfg, gate, edges, n_trials, cal_seed0=1000, test_seed0=5000)
    labels = sorted(set(mm) | set(om))
    marg = [mm.get(k, np.nan) for k in labels]
    mond = [om.get(k, np.nan) for k in labels]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 7.0),
                                   gridspec_kw={"height_ratios": [3, 2]})
    x = np.arange(len(labels)); w = 0.38
    b1 = ax1.bar(x - w / 2, marg, w, color="#c0392b", label="marginal")
    b2 = ax1.bar(x + w / 2, mond, w, color="#2471a3", label="Mondrian")
    ax1.axhline(alpha, color="black", ls="--", lw=1, label=f"target $\\alpha$ = {alpha:g}")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"bucket {k}" + ("\n(cheap)" if k == cheap else "") for k in labels])
    ax1.set_ylabel("mean true risk")
    ax1.set_title(f"Figure B -- per-bucket true risk at $\\gamma$ = {gate:g}")
    ax1.legend(fontsize=9); ax1.grid(alpha=0.3, axis="y")
    ax1.bar_label(b1, fmt="%.3f", fontsize=7, padding=2)
    ax1.bar_label(b2, fmt="%.3f", fontsize=7, padding=2)

    depth = reference_depth(pool["scores"], lam)
    ax2.hist(depth, bins=np.arange(depth.min(), depth.max() + 2) - 0.5,
             color="#95a5a6", edgecolor="white")
    for e in edges:
        ax2.axvline(e, color="#c0392b", ls=":", lw=1)
    ax2.set_xlabel(f"reference depth (first crossing of $\\lambda_{{ref}}$ = {lam:g})")
    ax2.set_ylabel("count (pool)")
    ax2.set_title("reference-depth distribution with bucket edges (red)")
    ax2.grid(alpha=0.3, axis="y")
    path = out_dir / "figB_per_bucket.png"
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
    return path


def figure_c(cfg, results_root, out_dir):
    metrics_dir = Path(results_root) / "metrics" if results_root else None
    files = sorted(glob.glob(str(metrics_dir / "mondrian_mnist_seed*.json"))) if metrics_dir else []
    if not files:
        print("  [Figure C] no MNIST metrics found "
              f"({metrics_dir}/mondrian_mnist_seed*.json) -- skipping.")
        return None

    alpha = float(cfg["alpha"])

    def _is_num(v):
        return v is not None and not (isinstance(v, float) and np.isnan(v))

    # Aggregate realized per-bucket test risk across seeds, tracking abstentions
    # (Mondrian/marginal can certify *nothing* in a stratum -> risk recorded as
    # None == abstain == fall back to full acquisition).
    marg_vals: dict = {}
    mond_vals: dict = {}
    marg_abstain: dict = {}
    mond_abstain: dict = {}
    fallback_vals: dict = {}     # bucket -> full-acquisition risk on seeds it abstained
    for fp in files:
        rec = json.loads(Path(fp).read_text())
        for k, v in rec.get("marginal", {}).get("per_bucket_risk", {}).items():
            kk = int(k)
            (marg_vals.setdefault(kk, []).append(v) if _is_num(v)
             else marg_abstain.__setitem__(kk, marg_abstain.get(kk, 0) + 1))
        for k, v in rec.get("mondrian", {}).get("per_bucket_risk", {}).items():
            kk = int(k)
            (mond_vals.setdefault(kk, []).append(v) if _is_num(v)
             else mond_abstain.__setitem__(kk, mond_abstain.get(kk, 0) + 1))
        for k, v in rec.get("fallback_full_acq_risk_by_bucket", {}).items():
            if _is_num(v):
                fallback_vals.setdefault(int(k), []).append(v)

    labels = sorted(set(marg_vals) | set(mond_vals) | set(marg_abstain) | set(mond_abstain))
    if not labels:
        print("  [Figure C] metrics present but no per_bucket_risk fields -- skipping.")
        return None
    n = len(files)

    def _mean(d, k):
        vals = d.get(k, [])
        return float(np.mean(vals)) if vals else np.nan

    marg = [_mean(marg_vals, k) for k in labels]
    mond = [_mean(mond_vals, k) for k in labels]
    fallback = {k: float(np.mean(v)) for k, v in fallback_vals.items() if v}

    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    x = np.arange(len(labels)); w = 0.38
    ax.bar(x - w / 2, np.nan_to_num(marg, nan=0.0), w, color="#c0392b", label="marginal")
    ax.axhline(alpha, color="black", ls="--", lw=1, label=f"target $\\alpha$ = {alpha:g}")
    ax.set_xticks(x); ax.set_xticklabels([f"bucket {k}" for k in labels])
    ax.set_ylabel("mean realized test risk")
    ax.set_title(f"Figure C -- MNIST per-bucket realized risk ({n} seeds)")

    top = max([v for v in marg + mond if not np.isnan(v)]
              + list(fallback.values()) + [alpha]) * 1.18
    ax.set_ylim(0, top)

    # Mondrian bars: solid where certified (mean over certified seeds); a hatched
    # placeholder up to alpha where Mondrian abstained on EVERY seed (declined to
    # certify -- not "zero risk"). For any abstaining bucket, mark the realized
    # full-acquisition fallback risk (a dark tick) and label it: this shows whether
    # even acquiring everything stays above alpha (i.e. alpha is unachievable there).
    fb_label_used = False
    mond_label_used = False
    for xi, k, mv in zip(x, labels, mond):
        na = mond_abstain.get(k, 0)
        if na >= n:  # abstained on all seeds
            ax.bar(xi + w / 2, alpha, w, facecolor="white", edgecolor="#2471a3",
                   hatch="//", label=(None if mond_label_used else "Mondrian"))
            ax.text(xi + w / 2, alpha * 0.5, f"abstains\n{na}/{n}", ha="center",
                    va="center", fontsize=7, color="#1a5276")
        else:
            ax.bar(xi + w / 2, 0.0 if np.isnan(mv) else mv, w, color="#2471a3",
                   label=(None if mond_label_used else "Mondrian"))
            tag = (f"{mv:.3f}" if not np.isnan(mv) else "")
            if na > 0:
                tag += f"\nabstains {na}/{n}"
            if tag:
                ax.text(xi + w / 2, (mv if not np.isnan(mv) else 0.0), tag,
                        ha="center", va="bottom", fontsize=7)
        mond_label_used = True

        # Full-acquisition fallback marker for abstaining buckets.
        if na > 0 and k in fallback:
            fb = fallback[k]
            ax.hlines(fb, xi + w / 2 - w / 2, xi + w / 2 + w / 2, color="#b9770e",
                      lw=2, label=(None if fb_label_used else "full-acq fallback"))
            ax.text(xi + w / 2, fb, f" full-acq\n {fb:.3f}", ha="center", va="bottom",
                    fontsize=7, color="#9c640c")
            fb_label_used = True

    ax.legend(fontsize=9, loc="upper left"); ax.grid(alpha=0.3, axis="y")

    # Annotate marginal bars: value + a marker when the marginal violates alpha
    # on a majority of certified seeds (the per-budget failure on real data).
    for xi, k, m in zip(x, labels, marg):
        if not np.isnan(m):
            certified = marg_vals.get(k, [])
            n_viol = sum(1 for v in certified if v > alpha)
            vr = (n_viol / len(certified)) if certified else 0.0
            tag = f"{m:.3f}" + (f"\n!{n_viol}/{len(certified)}>α" if vr >= 0.5 else "")
            ax.text(xi - w / 2, m, tag, ha="center", va="bottom", fontsize=7,
                    color=("#922b21" if vr >= 0.5 else "black"))

    path = out_dir / "figC_mnist_per_bucket.png"
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)

    # Console summary of the real-data finding.
    hard = labels[-1]
    n_viol_hard = sum(1 for v in marg_vals.get(hard, []) if v > alpha)
    print(f"  [Figure C] {path}")
    print(f"    marginal bucket {hard} mean risk = {_mean(marg_vals, hard):.3f} "
          f"(violates alpha on {n_viol_hard}/{len(marg_vals.get(hard, []))} certified seeds); "
          f"Mondrian abstains on bucket {hard} for {mond_abstain.get(hard, 0)}/{n} seeds.")
    if hard in fallback:
        print(f"    full-acquisition fallback risk on bucket {hard} = {fallback[hard]:.3f} "
              f"({'still > alpha' if fallback[hard] > alpha else '<= alpha'} "
              "-- acquiring everything " +
              ("does NOT" if fallback[hard] > alpha else "does") +
              " achieve the target).")
    return path


# --------------------------------------------------------------------------- #
def _resolve_out_dir(arg_out_dir):
    """Figures dir: --out-dir, else ${results_root}/figures, else ./results/figures.

    Always tries to resolve a ``results_root`` for locating the MNIST metrics
    (Figure C), even when ``--out-dir`` redirects where the figures are written.
    """
    # Resolve results_root for Figure C metrics independently of the figure dir.
    results_root = os.environ.get("RESULTS_ROOT")
    if results_root is None:
        try:
            results_root = str(config.load_paths().results_root)
        except Exception:  # noqa: BLE001
            results_root = None

    if arg_out_dir:
        out = Path(arg_out_dir)
        out.mkdir(parents=True, exist_ok=True)
        return out, results_root
    if results_root is not None:
        out = Path(results_root) / "figures"
        out.mkdir(parents=True, exist_ok=True)
        return out, results_root
    out = Path("results") / "figures"
    out.mkdir(parents=True, exist_ok=True)
    print(f"  [paths] RESULTS_ROOT unset; using fallback figures dir {out}")
    return out, None


def _load_synthetic_cfg():
    """Pull the synthetic + method knobs from configs/experiment.yaml."""
    exp = config.load_experiment()
    method = exp["method"]
    syn = method.get("mondrian", {}).copy()
    syn.update(method.get("synthetic", {}))
    return {
        "alpha": method["alpha"],
        "delta": method["delta"],
        "grid_n": method["grid"]["n"],
        "lambda_ref": syn.get("lambda_ref", 0.5),
        "n_buckets": syn.get("n_buckets", 5),
        "min_per_bucket": syn.get("min_per_bucket", 50),
        "T": syn.get("T", 49),
        "gamma_gate": syn.get("gamma_gate", 0.12),
        "gamma_grid": syn.get("gamma_grid", [0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14]),
        "n_cal": syn.get("n_cal", 6000),
        "n_test": syn.get("n_test", 6000),
        "pool_n": syn.get("pool_n", 20000),
        "pool_seed": syn.get("pool_seed", 777),
    }


def main():
    ap = argparse.ArgumentParser(description="Step 3 Mondrian figures.")
    ap.add_argument("--out-dir", default=None, help="override output directory")
    ap.add_argument("--gamma-trials", type=int, default=40,
                    help="resplits averaged per gamma for the synthetic figures")
    args = ap.parse_args()

    cfg = _load_synthetic_cfg()
    out_dir, results_root = _resolve_out_dir(args.out_dir)
    print(f"Writing figures to {out_dir}")

    pool, edges, cheap = _build_pool(cfg)
    print(f"  edges={np.round(edges, 3).tolist()}  cheap bucket label={cheap}")

    pa = figure_a(cfg, edges, cheap, out_dir, args.gamma_trials)
    print(f"  [Figure A] {pa}")
    pb = figure_b(cfg, pool, edges, cheap, out_dir, args.gamma_trials)
    print(f"  [Figure B] {pb}")
    figure_c(cfg, results_root, out_dir)


if __name__ == "__main__":
    main()