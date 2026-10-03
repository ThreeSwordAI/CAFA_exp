#!/usr/bin/env python
"""v3 -- paper figures from metrics_v3 / planted / repair outputs (matplotlib, torch-free).

  F2_blindness.pdf   marginal certificate vs. max stratum risk / alpha (per cell)
  F3_cascade.pdf     tier shares (stacked) + deployed cost vs. marginal / Mondrian oracle / full
  F4_repair.pdf      before/after deepest-stratum family minimum and tier-1 share (repair JSONs)
  F5_planted.pdf     planted power vs n_k Delta^2, false-failure rate, cascade violation rate
  F6_violations.pdf  per cell: raw test stratum-violation rate and certified-violation rate side by side
                     (round 2), with the min-max of the raw rate over the splits, and reference lines
                     at delta and delta + 0.05

    python scripts/make_figures_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --planted results_v3/planted \
        --repair-dir results_v3/repair --output-dir results_v3/figures --lambda-ref-key dep --scheme uniform
Figure 1 (the strata-by-rules matrix + pipeline) is drawn by hand (TikZ); see the plan.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def load_cells(metrics_dir: Path, key: str, scheme: str):
    cells = []
    for jp in sorted(Path(metrics_dir).glob("*.json")):
        d = json.loads(jp.read_text())
        blk = d["lambda_refs"].get(key)
        if blk is None:
            continue
        sch = blk["schemes"].get(scheme)
        if sch is None:  # v3 fix: no silent fallback to another cost scheme
            continue
        cells.append((d["meta"], d["alpha"], d["delta"], blk, sch["summary"]))
    return cells


def fig_blindness(cells, out: Path):
    if not cells:
        return
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    names = [f"{m['dsname']}\n{m['policy']} s{m['train_seed']}" for m, *_ in cells]
    agg = [s["marginal_mean_test_risk"] / a if s["marginal_mean_test_risk"] else np.nan for m, a, dl, b, s in cells]
    mx = [s["marginal_max_stratum_over_alpha_mean"] or np.nan for m, a, dl, b, s in cells]
    x = np.arange(len(cells))
    ax.bar(x - 0.2, agg, 0.4, label="aggregate risk / alpha (marginal CAFA)")
    ax.bar(x + 0.2, mx, 0.4, label="max stratum risk / alpha")
    ax.axhline(1.0, color="k", lw=0.8, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=6, rotation=60, ha="right")
    ax.set_ylabel("risk / alpha")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "F2_blindness.pdf")
    plt.close(fig)


def fig_cascade(cells, out: Path):
    if not cells:
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.4))
    names = [f"{m['dsname']}\n{m['policy']} s{m['train_seed']}" for m, *_ in cells]
    x = np.arange(len(cells))
    bottom = np.zeros(len(cells))
    for t, lab in (("1", "tier 1: certified stop"), ("2", "tier 2: certified budget"),
                   ("3", "tier 3: certified escalation"), ("0", "no certificate")):
        v = np.array([s["tier_share"][t] for *_, s in cells])
        a1.bar(x, v, bottom=bottom, label=lab)
        bottom += v
    a1.set_xticks(x)
    a1.set_xticklabels(names, fontsize=6, rotation=60, ha="right")
    a1.set_ylabel("share of calibration draws")
    a1.legend(fontsize=6, loc="lower left")
    full = np.array([s["baselines"].get("full_acquisition", {}).get("mean_test_cost") or np.nan for *_, s in cells])
    dep = np.array([s["cascade_mean_test_cost"] for *_, s in cells]) / full
    marg = np.array([s["marginal_mean_test_cost"] or np.nan for *_, s in cells]) / full
    mon = np.array([s["baselines"].get("mondrian_oracle", {}).get("mean_test_cost") or np.nan for *_, s in cells]) / full
    a2.bar(x, dep, 0.5, label="deployed rule (cascade)")
    a2.plot(x, marg, "k_", ms=14, mew=2, label="marginal CAFA")
    a2.plot(x, mon, "r_", ms=14, mew=2, label="Mondrian oracle (non-deployable)")
    a2.axhline(1.0, color="gray", lw=0.8, ls="--")
    a2.set_xticks(x)
    a2.set_xticklabels(names, fontsize=6, rotation=60, ha="right")
    a2.set_ylabel("cost / full acquisition")
    a2.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(out / "F3_cascade.pdf")
    plt.close(fig)


def fig_violations(cells, out: Path):
    cells = [c for c in cells if "cascade_certified_violation_rate" in c[4]]  # round-2 metrics only
    if not cells:
        return
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    names = [f"{m['dsname']}\n{m['policy']} s{m['train_seed']}" for m, *_ in cells]
    x = np.arange(len(cells))
    raw =np.array([s["cascade_violation_rate"] for *_, s in cells])
    cert = np.array([s["cascade_certified_violation_rate"] for *_, s in cells])
    lo = np.array([min(v["cascade_violation_rate"] for v in s.get("by_split", {}).values()) if s.get("by_split") else r
                   for (*_, s), r in zip(cells, raw)])
    hi = np.array([max(v["cascade_violation_rate"] for v in s.get("by_split", {}).values()) if s.get("by_split") else r
                   for (*_, s), r in zip(cells, raw)])
    ax.bar(x - 0.2, raw, 0.4, label="raw test stratum violation (pooled)")
    ax.errorbar(x - 0.2, raw, yerr=np.vstack([raw - lo, hi - raw]), fmt="none", ecolor="k", lw=0.8, capsize=2,
                label="raw, min-max over splits")
    ax.bar(x + 0.2, cert, 0.4, label="certified violation (exact binomial p <= 0.05)")
    dl = float(cells[0][2])
    ax.axhline(dl, color="k", lw=0.8, ls="--", label=f"delta = {dl:g}")
    ax.axhline(dl + 0.05, color="gray", lw=0.8, ls=":", label=f"delta + 0.05 = {dl + 0.05:g}")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=6, rotation=60, ha="right")
    ax.set_ylabel("share of calibration draws")
    ax.set_ylim(0, max(1e-3, float(max(hi.max(), cert.max(), dl + 0.05))) * 1.1)
    ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(out / "F6_violations.pdf")
    plt.close(fig)


def fig_repair(repair_dir: Path, out: Path, key: str):
    files = sorted(Path(repair_dir).glob("*.json")) if repair_dir and Path(repair_dir).exists() else []
    if not files:
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.2))
    labels, before_r, after_r, before_t1, after_t1, alphas = [], [], [], [], [], []
    for fp in files:
        d = json.loads(fp.read_text())
        blk = d["lambda_refs"].get(key) or next(iter(d["lambda_refs"].values()))
        labels.append(f"{d['dataset']}\n{d['label']}")
        before_r.append(min(blk["before"]["rmin_thr"], blk["before"]["rmin_depth"]))
        after_r.append(min(blk["after"]["rmin_thr"], blk["after"]["rmin_depth"]))
        before_t1.append(blk["before"]["cascade"]["tier_share"]["1"])
        after_t1.append(blk["after"]["cascade"]["tier_share"]["1"])
        alphas.append(d["alpha"])
    x = np.arange(len(labels))
    a1.bar(x - 0.2, before_r, 0.4, label="before")
    a1.bar(x + 0.2, after_r, 0.4, label="after")
    for i, al in enumerate(alphas):
        a1.plot([i - 0.45, i + 0.45], [al, al], "k--", lw=0.8)
    a1.set_ylabel("deepest-stratum family minimum risk")
    a1.set_xticks(x)
    a1.set_xticklabels(labels, fontsize=6, rotation=45, ha="right")
    a1.legend(fontsize=7)
    a2.bar(x - 0.2, before_t1, 0.4, label="before")
    a2.bar(x + 0.2, after_t1, 0.4, label="after")
    a2.set_ylabel("tier-1 share of draws")
    a2.set_xticks(x)
    a2.set_xticklabels(labels, fontsize=6, rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(out / "F4_repair.pdf")
    plt.close(fig)


def fig_planted(planted_dir: Path, out: Path):
    csv_path = Path(planted_dir) / "planted_validation.csv" if planted_dir else None
    if not csv_path or not csv_path.exists():
        return
    rows = list(csv.DictReader(open(csv_path)))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.2))
    pw = [r for r in rows if r["study"].startswith("B")]
    for mg in sorted({float(r["margin"]) for r in pw}):
        rr = sorted([r for r in pw if float(r["margin"]) == mg], key=lambda r: float(r["nk_delta2"]))
        a1.plot([float(r["nk_delta2"]) for r in rr], [float(r["power"]) for r in rr], "o-", label=f"Delta={mg:.2f}")
    a1.set_xscale("log")
    a1.set_xlabel("n_k Delta^2")
    a1.set_ylabel("P(certified Type II)")
    a1.legend(fontsize=7)
    lv = [r for r in rows if r["study"].startswith("A")]
    for mg in sorted({float(r["margin"]) for r in lv}):
        rr = sorted([r for r in lv if float(r["margin"]) == mg], key=lambda r: int(r["n_k"]))
        a2.plot([int(r["n_k"]) for r in rr], [float(r["false_failure_rate"]) for r in rr], "s-",
                label=f"false failure, margin {abs(mg):.2f}")
        a2.plot([int(r["n_k"]) for r in rr], [float(r["cascade_violation_rate"]) for r in rr], "^--",
                label=f"cascade violation, margin {abs(mg):.2f}")
    a2.axhline(0.05, color="k", lw=0.8, ls=":", label="gamma")
    a2.axhline(0.10, color="gray", lw=0.8, ls="--", label="delta")
    a2.set_xscale("log")
    a2.set_xlabel("n_k")
    a2.set_ylabel("rate")
    a2.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(out / "F5_planted.pdf")
    plt.close(fig)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics-dir", required=True)
    p.add_argument("--planted", default=None)
    p.add_argument("--repair-dir", default=None)
    p.add_argument("--output-dir", default="results_v3/figures")
    p.add_argument("--lambda-ref-key", default="dep")
    p.add_argument("--scheme", default="uniform")
    a = p.parse_args(argv)
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cells = load_cells(Path(a.metrics_dir), a.lambda_ref_key, a.scheme)
    fig_blindness(cells, out)
    fig_cascade(cells, out)
    fig_violations(cells, out)
    fig_repair(Path(a.repair_dir) if a.repair_dir else None, out, a.lambda_ref_key)
    fig_planted(Path(a.planted) if a.planted else None, out)
    print(f"figures -> {out} ({len(cells)} cells)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
