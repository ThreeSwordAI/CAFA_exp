#!/usr/bin/env python
"""WO-12 -- v2 figures (matplotlib only; reads metrics_v2 + analysis_v2 CSVs).

Writes ``figures_v2/*.pdf`` and ``*.png`` (150 dpi):
  F1  realized (risk, cost) scatter with CI error bars, alpha line, oracle
      cheapest (star) / full (square); one panel per policy; primary scheme
      inverse_info (uniform for MNIST).
  F2  per-stratum marginal realized risk bars (CI whiskers), alpha line, fallback
      R_full(k) tick with LCB whisker; abstaining strata hatched; lambda_ref=0.9,
      greedy.
  F3  (a) populated-strata count vs lambda_ref per policy; (b) depth IQR per policy.
  F4  detection scatter: x = n_cal*q (log), y = Delta_hat; markers by detected;
      dashed guide curve n*q = log(1/delta)/(2*Delta^2).

No invented styling beyond matplotlib defaults + labels; every title carries
dataset + train_seed.
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

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def _save(fig, out_dir: Path, name: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{name}.pdf")
    fig.savefig(out_dir / f"{name}.png", dpi=150)
    plt.close(fig)


def load_metrics(metrics_dir: Path):
    out = {}
    for p in sorted(metrics_dir.glob("*.json")):
        data = json.loads(p.read_text())
        m = data["meta"]
        out[(m["dsname"], m["policy"], int(m["train_seed"]))] = data
    return out


def primary_scheme(schemes):
    return "inverse_info" if "inverse_info" in schemes else schemes[0]


def _mean_std(vals):
    arr = np.asarray([v for v in vals if v is not None], dtype=float)
    arr = arr[~np.isnan(arr)]
    if arr.size == 0:
        return float("nan"), float("nan")
    return float(arr.mean()), float(arr.std())


def fig1(metrics, out_dir):
    by_ds = defaultdict(list)
    for (dsname, policy, ts), data in metrics.items():
        by_ds[(dsname, ts)].append((policy, data))
    for (dsname, ts), items in by_ds.items():
        n = len(items)
        fig, axes = plt.subplots(1, n, figsize=(5 * n, 4), squeeze=False)
        for ax, (policy, data) in zip(axes[0], sorted(items)):
            scheme = primary_scheme(data["meta"]["schemes"])
            alpha = float(data["alpha"])
            lr_key = list(data["lambda_refs"].keys())[-1]
            resplits = data["lambda_refs"][lr_key]["resplits"]
            for method, marker in (("cafa_marginal", "o"), ("cafa_iut", "^")):
                risks = [r["schemes"][scheme][method]["realized_risk"] for r in resplits]
                costs = [r["schemes"][scheme][method]["realized_cost"] for r in resplits]
                rm, rs = _mean_std(risks)
                cm, cs = _mean_std(costs)
                ax.errorbar(rm, cm, xerr=rs, yerr=cs, marker=marker, capsize=3, label=method)
            oc_r, oc_c = _mean_std([r["schemes"][scheme]["oracle_cheapest"]["realized_risk"] for r in resplits])
            oc_r2, oc_c2 = _mean_std([r["schemes"][scheme]["oracle_cheapest"]["realized_cost"] for r in resplits])
            of_r, _ = _mean_std([r["schemes"][scheme]["oracle_full"]["realized_risk"] for r in resplits])
            of_c, _ = _mean_std([r["schemes"][scheme]["oracle_full"]["realized_cost"] for r in resplits])
            if not math.isnan(oc_r):
                ax.scatter([oc_r], [oc_c2], marker="*", s=160, label="oracle_cheapest")
            ax.scatter([of_r], [of_c], marker="s", s=80, label="oracle_full")
            ax.axvline(alpha, linestyle="--", label=f"alpha={alpha:g}")
            ax.set_xlabel("realized risk"); ax.set_ylabel(f"realized cost ({scheme})")
            ax.set_title(f"{policy}"); ax.legend(fontsize=7)
        fig.suptitle(f"F1 realized (risk, cost) -- {dsname} ts{ts} (lambda_ref={lr_key})")
        fig.tight_layout()
        _save(fig, out_dir, f"F1_{dsname}_ts{ts}")


def fig2(metrics, out_dir, lr_target="0.9"):
    for (dsname, policy, ts), data in metrics.items():
        if policy != "greedy_entropy":
            continue
        if lr_target not in data["lambda_refs"]:
            continue
        blk = data["lambda_refs"][lr_target]
        pop = blk["population"]; resplits = blk["resplits"]
        alpha = float(data["alpha"])
        strata = sorted(int(k) for k in pop["per_stratum_full"].keys())
        marg_mean, marg_sd, full_r, full_lcb, abstaining = [], [], [], [], []
        for k in strata:
            ks = str(k)
            vals = [r["marginal_per_stratum_risk"].get(ks) for r in resplits]
            m, s = _mean_std(vals)
            marg_mean.append(m); marg_sd.append(s)
            info = pop["per_stratum_full"][ks]
            full_r.append(info["risk"]); full_lcb.append(info["cp_lcb95"])
            # abstaining: mondrian joint_false abstains for this stratum on majority of resplits
            ab = np.mean([1.0 if r["mondrian_audit"]["joint_false"]["lambda_idx_by_bucket"].get(ks) is None
                          else 0.0 for r in resplits]) if resplits else 0.0
            abstaining.append(ab >= 0.5)
        x = np.arange(len(strata))
        fig, ax = plt.subplots(figsize=(1.6 * len(strata) + 3, 4))
        bars = ax.bar(x, marg_mean, yerr=marg_sd, capsize=3, label="marginal realized risk")
        for b, ab in zip(bars, abstaining):
            if ab:
                b.set_hatch("//")
        for xi, fr, fl in zip(x, full_r, full_lcb):
            if fr is not None:
                ax.plot([xi], [fr], marker="_", markersize=18, color="k")
                if fl is not None:
                    ax.plot([xi, xi], [fl, fr], color="k", linewidth=1)
        ax.axhline(alpha, linestyle="--", label=f"alpha={alpha:g}")
        ax.set_xticks(x); ax.set_xticklabels([str(k) for k in strata])
        ax.set_xlabel("stratum"); ax.set_ylabel("risk")
        ax.set_title(f"F2 per-stratum marginal risk -- {dsname} ts{ts} greedy lambda_ref={lr_target}")
        ax.legend(fontsize=8)
        fig.tight_layout()
        _save(fig, out_dir, f"F2_{dsname}_ts{ts}")


def fig3(fork_csv_path, out_dir):
    if not fork_csv_path.exists():
        return
    rows = list(csv.DictReader(open(fork_csv_path, newline="")))
    by_ds = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_ds[r["dataset"]][r["policy"]].append(r)
    for dsname, per_policy in by_ds.items():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
        for policy, rs in sorted(per_policy.items()):
            rs = sorted(rs, key=lambda r: float(r["lambda_ref"]))
            lrs = [float(r["lambda_ref"]) for r in rs]
            counts = [int(r["populated_strata"]) for r in rs]
            iqrs = [float(r["depth_iqr"]) for r in rs]
            ax1.plot(lrs, counts, marker="o", label=policy)
            ax2.plot(lrs, iqrs, marker="s", label=policy)
        ax1.set_xlabel("lambda_ref"); ax1.set_ylabel("populated strata"); ax1.set_title("(a) strata count")
        ax2.set_xlabel("lambda_ref"); ax2.set_ylabel("depth IQR"); ax2.set_title("(b) depth IQR")
        ax1.legend(fontsize=8); ax2.legend(fontsize=8)
        fig.suptitle(f"F3 concentration -- {dsname}")
        fig.tight_layout()
        _save(fig, out_dir, f"F3_{dsname}")


def fig4(detect_csv_path, metrics, out_dir):
    if not detect_csv_path.exists():
        return
    rows = list(csv.DictReader(open(detect_csv_path, newline="")))
    by_ds = defaultdict(list)
    for r in rows:
        by_ds[r["dataset"]].append(r)
    # a representative delta for the guide curve.
    delta = 0.10
    for _, data in metrics.items():
        delta = float(data["delta"]); break
    for dsname, rs in by_ds.items():
        fig, ax = plt.subplots(figsize=(6, 4.5))
        for det, marker, lbl in ((1, "x", "detected"), (0, "o", "not detected")):
            xs = [float(r["n_cal_q"]) for r in rs if int(r["detected"]) == det and float(r["n_cal_q"]) > 0]
            ys = [float(r["delta_hat"]) for r in rs if int(r["detected"]) == det and float(r["n_cal_q"]) > 0]
            if xs:
                ax.scatter(xs, ys, marker=marker, label=lbl)
        # guide curve n*q = log(1/delta)/(2*Delta^2) -> Delta = sqrt(log(1/delta)/(2*x))
        xgrid = np.logspace(0, math.log10(max([float(r["n_cal_q"]) for r in rs] + [10.0])), 100)
        dpos = np.sqrt(math.log(1.0 / delta) / (2.0 * xgrid))
        ax.plot(xgrid, dpos, "--", color="k", label="guide: n*q=log(1/delta)/(2*Delta^2)")
        ax.set_xscale("log")
        ax.set_xlabel("n_cal * q (log)"); ax.set_ylabel("Delta_hat = R_full_LCB - alpha")
        ax.set_title(f"F4 detection -- {dsname}")
        ax.legend(fontsize=7)
        fig.tight_layout()
        _save(fig, out_dir, f"F4_{dsname}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAFA v2 figures.")
    ap.add_argument("--metrics-dir", default="metrics_v2")
    ap.add_argument("--analysis-dir", default="analysis_v2")
    ap.add_argument("--out", default="figures_v2")
    args = ap.parse_args(argv)

    metrics_dir = Path(args.metrics_dir)
    analysis_dir = Path(args.analysis_dir)
    out_dir = Path(args.out)
    metrics = load_metrics(metrics_dir)
    if not metrics:
        print(f"ERROR: no metrics JSONs under {metrics_dir}.", file=sys.stderr)
        return 2

    fig1(metrics, out_dir)
    fig2(metrics, out_dir)
    fig3(analysis_dir / "fork_strata.csv", out_dir)
    fig4(analysis_dir / "detection_scatter.csv", metrics, out_dir)
    print(f"[figures] wrote F1-F4 into {out_dir}.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
