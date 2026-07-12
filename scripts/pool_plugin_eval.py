#!/usr/bin/env python
"""Phase 5.3, Task 2 -- correct the plugin evaluation on the full-pool estimand.

For every canonical cell and each of the 100 unique resplits: reconstruct the
calibration half, run the FROZEN plugin selector exactly as in the original
experiment (asserting the selected threshold matches the recorded one),
evaluate the selected threshold on the ENTIRE evaluation pool, and record
exceedance R_pool(lambda_plugin) > alpha. Fallback/empty selections are
counted separately (fallback = full acquisition; the system still predicts).

Descriptive three-way label (a benchmark classification, NOT a
distribution-free guarantee), criterion delta = 0.10:
  clearly unreliable          -- Wilson 95% LOWER bound > delta
  not shown unreliable        -- interval overlaps or lies below delta
  unresolved                  -- excessive fallbacks/empty selections

--alpha-sweep additionally regenerates the plugin alpha sweep on POOL risk
for the four primary cells (floor-anchored grid + the committed alpha as an
explicit measured point). Transition reporting: single crossing -> bracket;
several crossings -> list all; nonmonotone -> "no single safety transition".
The committed alpha is always measured directly, never interpolated.

Outputs (to --output-dir): POOL_PLUGIN_EVAL.md, pool_plugin_eval.csv,
pool_plugin_resplits.csv, POOL_PLUGIN_ALPHA_SWEEP.md,
pool_plugin_alpha_sweep.csv, figures/F10_plugin_pool_vs_test.pdf,
figures/F11_plugin_pool_alpha_sweep_<ds>.pdf.

Usage:
    python scripts/pool_plugin_eval.py --all-cells --alpha-sweep \
        --metrics-dir results_committed/metrics \
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
from cafa.baselines import plugin_threshold_select  # noqa: E402

_DELTA_BENCH = 0.10
_OFFSETS = (0.02, 0.05, 0.08, 0.11, 0.15, 0.20)
_LR_BLOCK = "0.9"     # plugin selection is lambda_ref-independent; one block = 100 unique


def eval_cell(cell, cfg, pool_dir, n_resplits, cal_frac):
    evald = L.load_eval_arrays(cell, cfg, pool_dir)
    scheme = L.primary_scheme(cell["meta"])
    losses_full, costs_full, cc, _ = L.losses_costs(evald, cell["grid"], scheme)
    alpha = cell["alpha"]
    T = evald["T"]
    full_r = float((1.0 - evald["correct"][:, T]).mean())
    full_c = float(cc[:, T].mean())
    blk = cell["data"]["lambda_refs"].get(_LR_BLOCK) or \
        next(iter(cell["data"]["lambda_refs"].values()))
    recorded = [r["schemes"][scheme]["plugin"].get("lambda_idx") for r in blk["resplits"]]
    test_exceed = sum(1 for r in blk["resplits"]
                      if (r["schemes"][scheme]["plugin"].get("realized_risk") is not None
                          and r["schemes"][scheme]["plugin"]["realized_risk"] > alpha))

    rows, pool_risks, pool_costs, sel_idx = [], [], [], []
    exceed = fallback = 0
    for rs, (cal_local, _t) in enumerate(L.resplit_ix(evald["n_eval"], n_resplits, cal_frac)):
        idx = plugin_threshold_select(losses_full[cal_local], costs_full[cal_local],
                                      cell["grid"], alpha)
        rec = recorded[rs] if rs < len(recorded) else None
        assert (idx is None) == (rec is None) and (idx is None or int(idx) == int(rec)), (
            f"PLUGIN RECONSTRUCTION FAIL {cell['label']} resplit {rs}: "
            f"recomputed {idx} != recorded {rec}")
        if idx is None:
            fallback += 1
            rp, cp_ = full_r, full_c
        else:
            rp = float(losses_full[:, int(idx)].mean())
            cp_ = float(costs_full[:, int(idx)].mean())
            sel_idx.append(int(idx))
        ex = rp > alpha
        exceed += int(ex)
        pool_risks.append(rp)
        pool_costs.append(cp_)
        rows.append({"cell": cell["label"], "resplit": rs,
                     "lambda_idx": (None if idx is None else int(idx)),
                     "pool_risk": rp, "pool_cost": cp_, "exceed": int(ex),
                     "fallback": int(idx is None)})

    n = n_resplits
    p, lo, hi = L.wilson(exceed, n)
    pr = np.asarray(pool_risks)
    if fallback > 0.2 * n:
        label = "unresolved (excessive fallback)"
    elif lo > _DELTA_BENCH:
        label = "clearly unreliable"
    else:
        label = "not shown unreliable at this resolution"
    summ = {
        "cell": cell["label"], "alpha": alpha, "scheme": scheme, "n_resplits": n,
        "pool_exceed": p, "wilson_lo": lo, "wilson_hi": hi,
        "test_exceed": test_exceed / n,
        "test_minus_pool": test_exceed / n - p,
        "mean_pool_risk": float(pr.mean()), "median_pool_risk": float(np.median(pr)),
        "sd_pool_risk": float(pr.std()),
        "p5_pool_risk": float(np.percentile(pr, 5)),
        "p95_pool_risk": float(np.percentile(pr, 95)),
        "mean_pool_cost": float(np.mean(pool_costs)),
        "cost_over_full": float(np.mean(pool_costs)) / full_c if full_c else float("nan"),
        "fallbacks": fallback,
        "sel_lambda_min": (float(cell["grid"][min(sel_idx)]) if sel_idx else None),
        "sel_lambda_median": (float(cell["grid"][int(np.median(sel_idx))]) if sel_idx else None),
        "sel_lambda_max": (float(cell["grid"][max(sel_idx)]) if sel_idx else None),
        "label": label,
    }
    return summ, rows, (losses_full, costs_full, full_r, full_c, evald)


def sweep_cell(cell, losses_full, costs_full, full_r, full_c, n_eval, cfg,
               n_resplits, cal_frac):
    committed = L.committed_for(cell["dsname"], cell["ts"])
    floor = float(committed["floor"]["estimate"])
    committed_alpha = float(committed["alpha"])
    alphas = sorted({round(min(0.999, floor + o), 4) for o in _OFFSETS}
                    | {round(committed_alpha, 4)})
    ix = L.resplit_ix(n_eval, n_resplits, cal_frac)
    out = []
    for a in alphas:
        exceed = fallback = 0
        risks, costs = [], []
        for cal_local, _t in ix:
            idx = plugin_threshold_select(losses_full[cal_local], costs_full[cal_local],
                                          cell["grid"], a)
            if idx is None:
                fallback += 1
                rp, cp_ = full_r, full_c
            else:
                rp = float(losses_full[:, int(idx)].mean())
                cp_ = float(costs_full[:, int(idx)].mean())
            exceed += int(rp > a)
            risks.append(rp)
            costs.append(cp_)
        p, lo, hi = L.wilson(exceed, n_resplits)
        out.append({"dataset": cell["dsname"], "alpha": a,
                    "is_committed": int(abs(a - committed_alpha) < 1e-9),
                    "floor": floor, "committed_alpha": committed_alpha,
                    "pool_exceed": p, "wilson_lo": lo, "wilson_hi": hi,
                    "mean_pool_risk": float(np.mean(risks)),
                    "mean_pool_cost": float(np.mean(costs)), "fallbacks": fallback})
    return out


def transition_text(rows, bench=_DELTA_BENCH):
    rows = sorted(rows, key=lambda r: r["alpha"])
    safe = [r["pool_exceed"] <= bench for r in rows]
    changes = [i for i in range(1, len(safe)) if safe[i] != safe[i - 1]]
    if all(safe):
        return "safe (exceed <= 0.10) at every swept alpha; no crossing in range"
    if not any(safe):
        return "exceeds 0.10 at every swept alpha; no crossing in range"
    if len(changes) == 1:
        i = changes[0]
        return (f"single crossing in ({rows[i-1]['alpha']:.4f}, {rows[i]['alpha']:.4f}]")
    return ("NONMONOTONE; no single safety transition exists (crossings at " +
            ", ".join(f"({rows[i-1]['alpha']:.4f}, {rows[i]['alpha']:.4f}]" for i in changes) + ")")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase 5.3 pool plugin evaluation.")
    ap.add_argument("--all-cells", action="store_true")
    ap.add_argument("--alpha-sweep", action="store_true")
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
    pv = cfg.get("protocol_v2", {})
    n_resplits = int(pv.get("n_resplits", 100))
    cal_frac = float(pv.get("cal_frac_of_eval", 0.5))

    cells = L.load_cells(Path(args.metrics_dir))
    summs, all_rows, sweep_rows = [], [], []
    for c in cells:
        summ, rows, (lf, cf, full_r, full_c, evald) = eval_cell(
            c, cfg, pool_dir, n_resplits, cal_frac)
        summs.append(summ)
        all_rows.extend(rows)
        print(f"[plugin-pool] {c['label']}: pool exceed {summ['pool_exceed']:.2f} "
              f"[{summ['wilson_lo']:.2f}, {summ['wilson_hi']:.2f}] "
              f"(test-half {summ['test_exceed']:.2f}) -> {summ['label']}", flush=True)
        if args.alpha_sweep and c["ts"] == 0 and c["policy"] == "greedy_entropy" \
                and c["score"] == "softmax":
            sweep_rows.extend(sweep_cell(c, lf, cf, full_r, full_c, evald["n_eval"],
                                         cfg, n_resplits, cal_frac))

    def wcsv(name, rows):
        with open(out_dir / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    wcsv("pool_plugin_eval.csv", summs)
    wcsv("pool_plugin_resplits.csv", all_rows)

    lines = ["# CAFA v2 -- PLUGIN ON THE FULL-POOL ESTIMAND (Phase 5.3, Task 2)\n",
             "_The plugin selects on the calibration half exactly as in the original "
             "experiment (selection asserted equal to the recorded threshold on every "
             "resplit); the selected threshold is then evaluated on the ENTIRE "
             "evaluation pool. 'The plugin's selected threshold exceeds the target on "
             "the fixed evaluation pool in x/100 calibration draws.' The three-way "
             "label is a descriptive benchmark classification (criterion 0.10), not a "
             "distribution-free guarantee; 0/100 does not mean 'safe'._\n",
             "| cell | alpha | POOL exceed [95% CI] | test-half exceed | diff | mean pool risk (p5, p95) | cost/full | fallbacks | label |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s in sorted(summs, key=lambda s: -s["pool_exceed"]):
        lines.append(
            f"| {s['cell']} | {s['alpha']:g} | {L.fmt(s['pool_exceed'], 2)} "
            f"[{L.fmt(s['wilson_lo'], 2)}, {L.fmt(s['wilson_hi'], 2)}] | "
            f"{L.fmt(s['test_exceed'], 2)} | {L.fmt(s['test_minus_pool'], 2)} | "
            f"{L.fmt(s['mean_pool_risk'])} ({L.fmt(s['p5_pool_risk'])}, "
            f"{L.fmt(s['p95_pool_risk'])}) | {L.fmt(s['cost_over_full'], 3)} | "
            f"{s['fallbacks']} | {s['label']} |")
    (out_dir / "POOL_PLUGIN_EVAL.md").write_text("\n".join(lines))

    if sweep_rows:
        wcsv("pool_plugin_alpha_sweep.csv", sweep_rows)
        by_ds = {}
        for r in sweep_rows:
            by_ds.setdefault(r["dataset"], []).append(r)
        sl = ["# CAFA v2 -- PLUGIN ALPHA SWEEP ON POOL RISK (Phase 5.3)\n",
              "_Select on calibration, evaluate on the full pool. The committed alpha "
              "is measured directly; monotonicity is not assumed._\n"]
        for ds, rows in sorted(by_ds.items()):
            rows = sorted(rows, key=lambda r: r["alpha"])
            sl.append(f"## {ds} (floor {rows[0]['floor']:.4f}, committed alpha "
                      f"{rows[0]['committed_alpha']:g})\n")
            sl.append("| alpha | note | POOL exceed [95% CI] | mean pool risk | fallbacks |")
            sl.append("|---|---|---|---|---|")
            for r in rows:
                sl.append(f"| {r['alpha']:.4f} | {'COMMITTED' if r['is_committed'] else ''} | "
                          f"{L.fmt(r['pool_exceed'], 2)} [{L.fmt(r['wilson_lo'], 2)}, "
                          f"{L.fmt(r['wilson_hi'], 2)}] | {L.fmt(r['mean_pool_risk'])} | "
                          f"{r['fallbacks']} |")
            sl.append("")
            sl.append(f"- Transition: {transition_text(rows)}.")
            crow = next(r for r in rows if r["is_committed"])
            sl.append(f"- MEASURED at committed alpha {crow['alpha']:g}: pool exceed "
                      f"{L.fmt(crow['pool_exceed'], 3)} [{L.fmt(crow['wilson_lo'], 3)}, "
                      f"{L.fmt(crow['wilson_hi'], 3)}].")
            sl.append("")
            fig, ax = plt.subplots(figsize=(6.2, 4.2))
            a = [r["alpha"] for r in rows]
            ax.errorbar(a, [r["pool_exceed"] for r in rows],
                        yerr=[[r["pool_exceed"] - r["wilson_lo"] for r in rows],
                              [r["wilson_hi"] - r["pool_exceed"] for r in rows]],
                        marker="o", capsize=3, label="plugin POOL exceedance")
            ax.axhline(_DELTA_BENCH, linestyle="--", color="k", label="0.10 benchmark")
            ax.axvline(crow["alpha"], linestyle=":", color="gray",
                       label=f"committed alpha {crow['alpha']:g}")
            ax.set_xlabel("alpha"); ax.set_ylabel("pool exceedance frequency")
            ax.set_title(f"F11 plugin pool alpha sweep -- {ds} ts0 greedy")
            ax.legend(fontsize=8)
            fig.tight_layout()
            fig.savefig(fig_dir / f"F11_plugin_pool_alpha_sweep_{ds}.pdf")
            fig.savefig(fig_dir / f"F11_plugin_pool_alpha_sweep_{ds}.png", dpi=150)
            plt.close(fig)
        (out_dir / "POOL_PLUGIN_ALPHA_SWEEP.md").write_text("\n".join(sl))

    # F10: pool vs test exceedance per cell
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter([s["test_exceed"] for s in summs], [s["pool_exceed"] for s in summs], s=24)
    lim = max(0.6, max(s["test_exceed"] for s in summs) * 1.1)
    ax.plot([0, lim], [0, lim], "k--", linewidth=0.8, label="pool = test-half")
    ax.axhline(_DELTA_BENCH, linestyle=":", color="gray", linewidth=0.8, label="0.10")
    ax.set_xlabel("test-half exceedance (old estimand)")
    ax.set_ylabel("POOL exceedance (correct estimand)")
    ax.set_title("F10 plugin: pool vs test-half exceedance (35 cells)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "F10_plugin_pool_vs_test.pdf")
    fig.savefig(fig_dir / "F10_plugin_pool_vs_test.png", dpi=150)
    plt.close(fig)

    n_unrel = sum(1 for s in summs if s["label"] == "clearly unreliable")
    print(f"[plugin-pool] wrote POOL_PLUGIN_EVAL.md (+sweep) + CSVs + F10/F11; "
          f"'clearly unreliable' on {n_unrel}/{len(summs)} cells.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
