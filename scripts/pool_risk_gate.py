#!/usr/bin/env python
"""Phase 5.2 -- the pool-risk gate (the correct estimand) + the anti-correlation demo.

WHY. The existing gate flags a violation when the empirical TEST-SPLIT risk at
the selected threshold exceeds alpha. Two defects: (1) the test half is a
noisy estimate of the true risk, and cost-minimisation deploys the least-
conservative certified lambda-hat (true risk just below alpha by
construction), so the noise crosses alpha often; (2) the resplits are
complementary 50/50 partitions of ONE finite pool, so for any fixed lambda

    R_test(lambda) = (n_eval * R_pool(lambda) - n_cal * R_cal(lambda)) / n_test

-- R_cal and R_test are EXACTLY anti-correlated (rho = -1), not merely
"dependent". An unlucky-easy cal draw selects a more aggressive lambda-hat
AND, deterministically, faces a harder test half. An independent-noise model
cannot see this pairing, which is why the Phase-5 validity diagnostic
under-predicted the failing cells by 0.04-0.11.

THE RESOLUTION. The eval pool IS the population for this experiment, so this
script evaluates each resplit's selected lambda-hat against the EXACT pool
risk: pool violation iff R_pool(lambda_hat_i) > alpha. No test-split noise,
no anti-correlation.

VALIDITY. LTT remains valid for this estimand: the calibration split is a
without-replacement subsample of the finite pool, the empirical mean of a
hypergeometric sample is dominated by its binomial counterpart (Hoeffding
1963, Sec. 6), so the Hoeffding-Bentkus p-value stays conservative and
P(R_pool(lambda_hat) > alpha) <= delta holds exactly as certified.

CHECKS BUILT IN.
  * Determinism: lambda_hat is recomputed with the frozen ltt_select on each
    resplit's cached cal arrays and ASSERTED equal to the lambda_idx recorded
    in the metrics JSON, for every resplit of every cell.
  * Estimand consistency: the mean R_pool(lambda_hat) is cross-checked
    against analysis_v2/validity_diagnostic.csv (same quantity).
  * Abstentions (lambda_hat = None -> full acquisition, not a violation) are
    counted and reported separately, never silently deflating a rate.
  * Basis note: marginal selection is lambda_ref-independent, so the 100
    resplits are counted ONCE (n = 100; the main gate table's pooling over 3
    lambda_ref blocks repeats identical outcomes 3x).

Outputs: analysis_v2/pool_risk_gate.csv, POOL_RISK_GATE.md,
figures_v2/F7_pool_risk_gate.* (panel a: R_cal vs R_test anti-correlation at
a fixed lambda; panel b: per-cell test-split vs pool violation rates).

Usage:
    python scripts/pool_risk_gate.py --all [--metrics-dir results_committed/metrics]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from cafa import config  # noqa: E402
from cafa.pool import cum_cost_from_order, load_pool_cache  # noqa: E402
from cafa.risk_control import ltt_select  # noqa: E402
from cafa.splits import probe_eval_split, resplit_cal_test  # noqa: E402

_Z = 1.96
_LR = "0.9"   # marginal selection is bucket-free; one block = the 100 resplits once


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


def stop_index_matrix(scores, grid):
    scores = np.asarray(scores, dtype=float)
    grid = np.asarray(grid, dtype=float)
    T = scores.shape[1] - 1
    crossed = scores[:, :, None] >= grid[None, None, :]
    any_cross = crossed.any(axis=1)
    first = crossed.argmax(axis=1)
    return np.where(any_cross, first, T).astype(int)


def gate_cell(metrics_path: Path, cfg, paths):
    """Pool-risk gate + anti-correlation stats for one cell. Returns (row, panelA)."""
    data = json.loads(metrics_path.read_text())
    meta = data["meta"]
    alpha = float(data["alpha"])
    delta = float(data["delta"])
    grid = np.asarray(data["grid"], dtype=float)
    procedure = cfg["method"].get("procedure", "fixed_sequence")
    blk = data["lambda_refs"].get(_LR) or next(iter(data["lambda_refs"].values()))
    resplits = blk["resplits"]
    scheme0 = meta["schemes"][0]

    dsname, ts, policy, score = meta["dsname"], int(meta["train_seed"]), meta["policy"], meta["score"]
    label = f"{dsname}/{policy}/ts{ts}" + (f"[{score}]" if score != "softmax" else "")

    cache_path = Path(paths.results_root) / "pool_v2" / f"{dsname}_ts{ts}_{policy}_{score}.npz"
    if not cache_path.exists():
        print(f"[pool-gate] WARN: cache missing for {label}; skipped.", file=sys.stderr)
        return None, None
    cache = load_pool_cache(cache_path)
    pv = cfg.get("protocol_v2", {})
    n_pool = cache["scores"].shape[0]
    _, eval_pos = probe_eval_split(np.arange(n_pool), float(pv.get("probe_frac", 0.10)),
                                   int(pv.get("probe_seed", 777)))
    scores_e = np.asarray(cache["scores"])[eval_pos]
    correct_e = np.asarray(cache["correct"])[eval_pos]
    order_e = np.asarray(cache["order"])[eval_pos]
    n_eval, Tp1 = scores_e.shape
    s_full = stop_index_matrix(scores_e, grid)
    losses_full = 1.0 - correct_e[np.arange(n_eval)[:, None], s_full]
    r_pool = losses_full.mean(axis=0)
    r_pool_full = float((1.0 - correct_e[:, Tp1 - 1]).mean())
    fc = np.asarray(cache["meta"]["feature_costs_by_scheme"][scheme0], dtype=float)
    cc = cum_cost_from_order(order_e, fc)
    costs_full = cc[np.arange(n_eval)[:, None], s_full]

    cal_frac = float(pv.get("cal_frac_of_eval", 0.5))
    resplit_ix = [resplit_cal_test(np.arange(n_eval), rs, cal_frac)
                  for rs in range(len(resplits))]

    pool_viol = test_viol = abstain = 0
    margins, r_pools_at = [], []
    lam_hats, rcal_at_hat, test_excess = [], [], []
    for rs, r in enumerate(resplits):
        rec = r["schemes"][scheme0]["cafa_marginal"]
        recorded = rec.get("lambda_idx")

        # Determinism: recompute lambda_hat with the FROZEN selector.
        cal_local, test_local = resplit_ix[rs]
        sel = ltt_select(losses_full[cal_local], costs_full[cal_local], grid,
                         alpha, delta, procedure=procedure)
        recomputed = sel.lambda_idx
        assert (recorded is None) == (recomputed is None) and \
               (recorded is None or int(recorded) == int(recomputed)), (
            f"DETERMINISM FAIL {label} resplit {rs}: recorded lambda_idx {recorded} "
            f"!= recomputed {recomputed}")

        if recorded is None:
            abstain += 1
            rp = r_pool_full            # abstain -> full acquisition (not a violation)
        else:
            idx = int(recorded)
            rp = float(r_pool[idx])
            lam_hats.append(idx)
            rcal_at_hat.append(float(losses_full[cal_local][:, idx].mean()))
            test_excess.append(float(losses_full[test_local][:, idx].mean()) - rp)
        if rp > alpha:
            pool_viol += 1
        r_pools_at.append(rp)
        margins.append(alpha - rp)

        rr = rec.get("realized_risk")
        if rr is not None and rr > alpha:
            test_viol += 1

    n = len(resplits)
    pvr, plo, phi = wilson(pool_viol, n)
    tvr, tlo, thi = wilson(test_viol, n)

    # Anti-correlation at a FIXED lambda (the modal lambda_hat).
    corr_fixed = corr_mech = float("nan")
    panelA = None
    if lam_hats:
        modal = int(np.bincount(np.asarray(lam_hats)).argmax())
        rc = np.array([float(losses_full[c][:, modal].mean()) for c, _ in resplit_ix])
        rt = np.array([float(losses_full[t][:, modal].mean()) for _, t in resplit_ix])
        if rc.std() > 0 and rt.std() > 0:
            corr_fixed = float(np.corrcoef(rc, rt)[0, 1])
        panelA = (rc, rt, modal)
        if len(rcal_at_hat) > 2 and np.std(rcal_at_hat) > 0 and np.std(test_excess) > 0:
            corr_mech = float(np.corrcoef(rcal_at_hat, test_excess)[0, 1])

    row = {
        "cell": label, "alpha": alpha, "delta": delta, "n_resplits": n,
        "abstentions": abstain,
        "pool_viol": pvr, "pool_lo": plo, "pool_hi": phi,
        "pool_gate": "PASS" if phi <= delta else "FAIL",
        "test_viol": tvr, "test_lo": tlo, "test_hi": thi,
        "test_gate": "PASS" if thi <= delta else "FAIL",
        "mean_margin_alpha_minus_Rpool": float(np.mean(margins)),
        "mean_R_pool_at_lambda": float(np.mean(r_pools_at)),
        "corr_Rcal_Rtest_fixed_lambda": corr_fixed,
        "corr_Rcal_at_hat_vs_test_excess": corr_mech,
    }
    return row, panelA


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAFA v2 pool-risk gate (Phase 5.2).")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--metrics-dir", default="metrics_v2")
    ap.add_argument("--analysis-dir", default="analysis_v2")
    ap.add_argument("--out", default="analysis_v2")
    ap.add_argument("--figures", default="figures_v2")
    args = ap.parse_args(argv)

    cfg = config.load_experiment()
    paths = config.load_paths()
    metrics_dir = Path(args.metrics_dir)
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = Path(args.figures); fig_dir.mkdir(parents=True, exist_ok=True)

    rows, panels = [], {}
    for p in sorted(metrics_dir.glob("*.json")):
        row, panelA = gate_cell(p, cfg, paths)
        if row is not None:
            rows.append(row)
            if panelA is not None:
                panels[row["cell"]] = panelA
    if not rows:
        print(f"ERROR: no cells under {metrics_dir}.", file=sys.stderr)
        return 2

    # Estimand consistency vs the Phase-5 validity diagnostic (same quantity).
    vd_csv = Path(args.analysis_dir) / "validity_diagnostic.csv"
    if vd_csv.exists():
        vd = {r["cell"]: float(r["mean_R_pool_at_lambda"])
              for r in csv.DictReader(open(vd_csv, newline=""))}
        for row in rows:
            if row["cell"] in vd:
                assert abs(row["mean_R_pool_at_lambda"] - vd[row["cell"]]) < 1e-9, (
                    f"ESTIMAND MISMATCH {row['cell']}: pool gate "
                    f"{row['mean_R_pool_at_lambda']} != validity diagnostic {vd[row['cell']]}")
        print("[pool-gate] estimand cross-check vs validity_diagnostic.csv: PASS "
              f"({sum(1 for r in rows if r['cell'] in vd)} cells).", flush=True)

    with open(out_dir / "pool_risk_gate.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    n_pool_fail = sum(1 for r in rows if r["pool_gate"] == "FAIL")
    n_test_fail = sum(1 for r in rows if r["test_gate"] == "FAIL")
    corrs = [r["corr_Rcal_Rtest_fixed_lambda"] for r in rows
             if not math.isnan(r["corr_Rcal_Rtest_fixed_lambda"])]

    lines = ["# CAFA v2 -- POOL-RISK GATE (the correct estimand)\n",
             "_The eval pool IS the population for this experiment; each resplit's "
             "selected lambda-hat is evaluated against the EXACT pool risk. LTT stays "
             "valid for this estimand (a without-replacement subsample's empirical mean "
             "is dominated by the binomial -- Hoeffding 1963 -- so the HB p-value remains "
             "conservative). GATE criterion: Wilson 95% UB <= delta, the same criterion "
             "as the main gate table, on an n = 100 basis (the marginal selection is "
             "lambda_ref-independent, so the 100 resplits are counted once; the main "
             "table's pooling over 3 lambda_ref blocks repeats identical outcomes). "
             "lambda-hat per resplit was recomputed with the frozen ltt_select and "
             "asserted equal to the recorded value on every resplit of every cell; "
             "abstentions are counted separately (abstain = full acquisition, "
             "not a violation)._\n",
             f"**Headline: {n_pool_fail}/{len(rows)} cells fail the pool-risk gate "
             f"(test-split gate: {n_test_fail}/{len(rows)}); measured "
             f"corr(R_cal, R_test) at fixed lambda = "
             f"{_fmt(float(np.mean(corrs)), 4) if corrs else 'n/a'} "
             f"(range {_fmt(min(corrs), 4)} to {_fmt(max(corrs), 4)}).**\n" if corrs else "",
             "| cell | alpha | abstain | POOL viol [95% CI] | gate | test viol [95% CI] | "
             "gate | mean margin | corr(Rcal,Rtest)@fixed | corr(Rcal@hat, test excess) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (-r["test_viol"], r["cell"])):
        lines.append(
            f"| {r['cell']} | {r['alpha']:g} | {r['abstentions']} | "
            f"{_fmt(r['pool_viol'], 3)} [{_fmt(r['pool_lo'], 3)}, {_fmt(r['pool_hi'], 3)}] | "
            f"{r['pool_gate']} | "
            f"{_fmt(r['test_viol'], 3)} [{_fmt(r['test_lo'], 3)}, {_fmt(r['test_hi'], 3)}] | "
            f"{r['test_gate']} | {_fmt(r['mean_margin_alpha_minus_Rpool'])} | "
            f"{_fmt(r['corr_Rcal_Rtest_fixed_lambda'], 3)} | "
            f"{_fmt(r['corr_Rcal_at_hat_vs_test_excess'], 3)} |")
    lines.append("")
    lines.append("Mechanism, demonstrated: R_test(lambda) = (n_eval R_pool - n_cal R_cal)/"
                 "n_test, so complementary 50/50 resplits anti-correlate exactly; an "
                 "unlucky-easy calibration half both selects a more aggressive lambda-hat "
                 "AND deterministically faces a harder test half. The negative "
                 "corr(R_cal at lambda-hat, test excess) column shows the pairing that an "
                 "independent-noise model cannot capture -- and the pool gate removes it "
                 "by evaluating the exact population risk.")
    (out_dir / "POOL_RISK_GATE.md").write_text("\n".join(lines))

    # ---- F7 ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    worst = max(rows, key=lambda r: r["test_viol"])
    pa = panels.get(worst["cell"])
    if pa is not None:
        rc, rt, modal = pa
        ax1.scatter(rc, rt, s=14)
        b = np.polyfit(rc, rt, 1)
        xs = np.linspace(rc.min(), rc.max(), 10)
        ax1.plot(xs, np.polyval(b, xs), "r--",
                 label=f"fit (rho = {worst['corr_Rcal_Rtest_fixed_lambda']:.3f})")
        ax1.set_xlabel(f"R_cal at fixed lambda (grid idx {modal})")
        ax1.set_ylabel("R_test at the same lambda")
        ax1.set_title(f"(a) exact anti-correlation -- {worst['cell']}")
        ax1.legend(fontsize=8)
    for r in rows:
        color = "tab:red" if r["test_gate"] == "FAIL" else "tab:blue"
        ax2.scatter(r["test_viol"], r["pool_viol"], marker="o", color=color, s=22)
    delta = rows[0]["delta"]
    lim = max(0.2, max(r["test_viol"] for r in rows) * 1.15)
    ax2.plot([0, lim], [0, lim], "k--", linewidth=0.8, label="pool = test")
    ax2.axvline(delta, linestyle=":", color="gray", linewidth=0.8)
    ax2.axhline(delta, linestyle=":", color="gray", linewidth=0.8, label=f"delta={delta:g}")
    ax2.set_xlabel("test-split violation rate (old gate)")
    ax2.set_ylabel("POOL violation rate (correct estimand)")
    ax2.set_title("(b) the six FAILs under the correct estimand (red = old-gate FAIL)")
    ax2.legend(fontsize=8)
    fig.suptitle("F7 pool-risk gate")
    fig.tight_layout()
    fig.savefig(fig_dir / "F7_pool_risk_gate.pdf")
    fig.savefig(fig_dir / "F7_pool_risk_gate.png", dpi=150)
    plt.close(fig)

    print(f"[pool-gate] {len(rows)} cells: POOL gate fails = {n_pool_fail} "
          f"(test gate fails = {n_test_fail}); mean corr(R_cal, R_test) = "
          f"{np.mean(corrs):.4f}. Wrote POOL_RISK_GATE.md + CSV + F7.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
