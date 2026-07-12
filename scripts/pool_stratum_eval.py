#!/usr/bin/env python
"""Phase 5.3, Task 3 -- selected-rule per-stratum risk on the full-pool estimand.

For every canonical cell, lambda_ref, and resplit: take the marginal
CAFA-selected threshold (recorded; lambda_ref-independent), evaluate it on
the ENTIRE evaluation pool, aggregate and per probe-committed stratum
(stratum membership is FIXED across resplits, never refit on cal).

Integrity assertions: sum_k q_k * R_pool,k(lambda_s) == R_pool(lambda_s)
per resplit; stratum counts sum to the eval-pool size.

Also renders the corrected Figure 1 (mnist primary cell): per-stratum MEAN
full-pool risk at the resplit-selected marginal threshold, with whiskers
labeled as VARIATION ACROSS CALIBRATION SELECTIONS (not population CIs), the
target line, aggregate pool risk, the full-feature endpoint marker on the
deepest stratum, and stratum masses.

Outputs (to --output-dir): POOL_STRATUM_EVAL.md, pool_stratum_eval.csv,
pool_stratum_resplits.csv, figures/F1_pool_corrected.{pdf,png}.

Usage:
    python scripts/pool_stratum_eval.py --all-cells --all-lambda-ref \
        --metrics-dir results_committed/metrics \
        --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed
"""

from __future__ import annotations

import argparse
import csv
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase 5.3 pool stratum evaluation.")
    ap.add_argument("--all-cells", action="store_true")
    ap.add_argument("--all-lambda-ref", action="store_true")
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

    cells = L.load_cells(Path(args.metrics_dir))
    summ_rows, rs_rows = [], []
    f1_payload = None
    for c in cells:
        evald = L.load_eval_arrays(c, cfg, pool_dir)
        committed = L.committed_for(c["dsname"], c["ts"])
        scheme = L.primary_scheme(c["meta"])
        losses_full, costs_full, cc, _ = L.losses_costs(evald, c["grid"], scheme)
        alpha = c["alpha"]
        T = evald["T"]
        n_eval = evald["n_eval"]
        full_loss = 1.0 - evald["correct"][:, T]
        full_r = float(full_loss.mean())
        full_c = float(cc[:, T].mean())

        # selected thresholds (marginal; lambda_ref-independent; block 0.9)
        blk = c["data"]["lambda_refs"].get(_PRIMARY_LR) or \
            next(iter(c["data"]["lambda_refs"].values()))
        scheme0 = c["meta"]["schemes"][0]
        sel = [r["schemes"][scheme0]["cafa_marginal"].get("lambda_idx")
               for r in blk["resplits"]]

        # per-resplit aggregate + cost
        agg = np.array([full_r if i is None else float(losses_full[:, int(i)].mean())
                        for i in sel])
        cost = np.array([full_c if i is None else float(costs_full[:, int(i)].mean())
                         for i in sel])

        for lr_key in _LRS:
            edges = L.edges_for(committed, c["policy"], c["score"], lr_key)
            bucket = L.bucket_ids(evald["scores"], float(lr_key), edges)
            labels = sorted(int(k) for k in np.unique(bucket))
            n_by_k = {k: int((bucket == k).sum()) for k in labels}
            assert sum(n_by_k.values()) == n_eval
            per_k = {k: [] for k in labels}
            for rs, i in enumerate(sel):
                acc = 0.0
                for k in labels:
                    mask = bucket == k
                    rk = (float(full_loss[mask].mean()) if i is None
                          else float(losses_full[mask, int(i)].mean()))
                    per_k[k].append(rk)
                    acc += n_by_k[k] / n_eval * rk
                # integrity: weighted per-stratum pool risks reconstruct aggregate
                assert abs(acc - agg[rs]) < 1e-9, (
                    f"AGGREGATE RECONSTRUCTION FAIL {c['label']} lr={lr_key} rs={rs}")
                if lr_key == _PRIMARY_LR:
                    rs_rows.append({"cell": c["label"], "lambda_ref": lr_key,
                                    "resplit": rs,
                                    "lambda_idx": (None if i is None else int(i)),
                                    "agg_pool_risk": float(agg[rs]),
                                    "pool_cost": float(cost[rs]),
                                    **{f"R_pool_s{k}": round(per_k[k][-1], 6)
                                       for k in labels}})
            for k in labels:
                arr = np.asarray(per_k[k])
                endpoint = float(full_loss[bucket == k].mean())
                summ_rows.append({
                    "cell": c["label"], "lambda_ref": lr_key, "stratum": k,
                    "n_k": n_by_k[k], "q_k": n_by_k[k] / n_eval, "alpha": alpha,
                    "mean_pool_risk": float(arr.mean()),
                    "median_pool_risk": float(np.median(arr)),
                    "sd_pool_risk": float(arr.std()),
                    "p5_pool_risk": float(np.percentile(arr, 5)),
                    "p95_pool_risk": float(np.percentile(arr, 95)),
                    "min_pool_risk": float(arr.min()), "max_pool_risk": float(arr.max()),
                    "exceed_freq": float((arr > alpha).mean()),
                    "mean_ratio_to_alpha": float(arr.mean() / alpha),
                    "agg_pool_risk_mean": float(agg.mean()),
                    "contribution_qk_Rk": float(n_by_k[k] / n_eval * arr.mean()),
                    "endpoint_full_risk": endpoint,
                    "gap_selected_minus_endpoint": float(arr.mean() - endpoint),
                })
            if (c["dsname"] == "mnist" and c["ts"] == 0 and c["policy"] == "greedy_entropy"
                    and c["score"] == "softmax" and lr_key == _PRIMARY_LR):
                f1_payload = (labels, n_by_k, per_k, alpha, float(agg.mean()),
                              {k: float(full_loss[bucket == k].mean()) for k in labels},
                              n_eval)
        print(f"[stratum-pool] {c['label']}: agg pool risk mean {agg.mean():.4f} "
              f"(marginal selections, {len(sel)} resplits)", flush=True)

    def wcsv(name, rows):
        with open(out_dir / name, "w", newline="") as f:
            keys = sorted({k for r in rows for k in r}, key=lambda k: (k != "cell", k))
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader(); w.writerows(rows)
    wcsv("pool_stratum_eval.csv", summ_rows)
    wcsv("pool_stratum_resplits.csv", rs_rows)

    # markdown: primary cells at lambda 0.9
    lines = ["# CAFA v2 -- SELECTED-RULE PER-STRATUM POOL RISK (Phase 5.3, Task 3)\n",
             "_The marginal CAFA threshold selected on each calibration half is "
             "evaluated on the ENTIRE evaluation pool, per probe-committed stratum "
             "(fixed across resplits). Spread columns describe VARIATION ACROSS "
             "CALIBRATION SELECTIONS, not population confidence intervals. Weighted "
             "per-stratum risks reconstruct the aggregate exactly (asserted per "
             "resplit)._\n",
             "## Primary cells (ts0 greedy softmax, lambda_ref = 0.9)\n",
             "| dataset | stratum | n_k | q_k | mean pool risk (p5, p95) | exceed freq | "
             "ratio to alpha | endpoint full risk | selected - endpoint |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in summ_rows:
        if r["lambda_ref"] != _PRIMARY_LR:
            continue
        if not (r["cell"].endswith("/greedy_entropy/ts0")):
            continue
        ds = r["cell"].split("/")[0]
        lines.append(
            f"| {ds} | {r['stratum']} | {r['n_k']} | {L.fmt(r['q_k'])} | "
            f"{L.fmt(r['mean_pool_risk'])} ({L.fmt(r['p5_pool_risk'])}, "
            f"{L.fmt(r['p95_pool_risk'])}) | {L.fmt(r['exceed_freq'], 2)} | "
            f"{L.fmt(r['mean_ratio_to_alpha'], 3)} | {L.fmt(r['endpoint_full_risk'])} | "
            f"{L.fmt(r['gap_selected_minus_endpoint'])} |")
    lines.append("")
    lines.append("Full grid (all 35 cells x 3 lambda_refs x strata): "
                 "`pool_stratum_eval.csv`; per-resplit values at lambda_ref 0.9: "
                 "`pool_stratum_resplits.csv`.")
    (out_dir / "POOL_STRATUM_EVAL.md").write_text("\n".join(lines))

    # corrected Figure 1
    if f1_payload:
        labels, n_by_k, per_k, alpha, agg_mean, endpoints, n_eval = f1_payload
        x = np.arange(len(labels))
        means = [float(np.mean(per_k[k])) for k in labels]
        p5 = [float(np.percentile(per_k[k], 5)) for k in labels]
        p95 = [float(np.percentile(per_k[k], 95)) for k in labels]
        fig, ax = plt.subplots(figsize=(7.2, 4.4))
        bars = ax.bar(x, means,
                      yerr=[[m - a for m, a in zip(means, p5)],
                            [b - m for m, b in zip(means, p95)]],
                      capsize=4, label="mean POOL risk at selected threshold\n"
                                       "(whiskers: p5-p95 across calibration selections)")
        deep = max(labels)
        ax.plot([labels.index(deep)], [endpoints[deep]], marker="D", color="k",
                markersize=7, linestyle="none",
                label=f"full-feature endpoint on deepest stratum ({endpoints[deep]:.4f})")
        ax.axhline(alpha, linestyle="--", color="k", label=f"target alpha = {alpha:g}")
        ax.axhline(agg_mean, linestyle=":", color="tab:green",
                   label=f"aggregate pool risk = {agg_mean:.4f}")
        for xi, k in zip(x, labels):
            ax.text(xi, 0.005, f"q={n_by_k[k]/n_eval:.2f}", ha="center", fontsize=7)
        ax.set_xticks(x); ax.set_xticklabels([str(k) for k in labels])
        ax.set_xlabel("probe-committed stratum (reference depth at lambda_ref = 0.9)")
        ax.set_ylabel("full-pool risk")
        ax.set_title("F1 (pool-corrected) -- mnist ts0 greedy: selected-rule stratum risk")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(fig_dir / "F1_pool_corrected.pdf")
        fig.savefig(fig_dir / "F1_pool_corrected.png", dpi=150)
        plt.close(fig)

    print(f"[stratum-pool] wrote POOL_STRATUM_EVAL.md + 2 CSVs + F1_pool_corrected "
          f"({len(summ_rows)} (cell, lambda_ref, stratum) rows).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
