#!/usr/bin/env python
"""Phase 5.3, Task 4 -- IUT reported separately for all 105 configurations.

35 canonical cells x 3 reference thresholds = 105 distinct IUT configurations;
each is reported over its 100 unique resplits, never pooled before
per-configuration statistics are stored.

Per (cell, lambda_ref):
  * certification rate + refusal rate (Wilson, denominator 100; asserted to
    sum to 100 counts);
  * unconditional any-stratum POOL-failure rate (denominator 100);
  * n_certified and CONDITIONAL any-stratum pool-failure rate among certified
    selections (Wilson, denominator n_certified; no interval when 0);
  * selected-threshold distribution, mean certified cost, mean deployed cost
    (certification refusal -> FULL-ACQUISITION FALLBACK; the system still
    predicts -- this is NOT prediction abstention), premium over marginal;
  * minimum stratum size; blocking-stratum audit verdict.

Refusal configurations are classified (three-outcome semantics):
  A  refusal with certified FAMILY-WIDE failure (Task-1 threshold verdict);
  B  refusal with certified ENDPOINT failure only;
  C  refusal, unresolved.

Requires family_wide_summary.csv (run family_wide_feasibility.py first).

Outputs (to --output-dir): IUT_BY_LAMBDA_REF.md, iut_by_lambda_ref.csv,
iut_by_lambda_ref_resplits.csv, IUT_OUTCOME_CLASSIFICATION.md,
figures/F12_iut_certification_by_lambda_ref.pdf,
figures/F13_iut_cost_refusal_frontier.pdf.

Usage:
    python scripts/iut_by_lambda_ref.py --all-cells --lambda-ref 0.5 0.7 0.9 \
        --metrics-dir results_committed/metrics \
        --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase53_lib as L  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from cafa import config  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase 5.3 IUT by lambda_ref (105 configs).")
    ap.add_argument("--all-cells", action="store_true")
    ap.add_argument("--lambda-ref", nargs="+", default=["0.5", "0.7", "0.9"])
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

    # family verdicts for refusal classification
    fam_path = out_dir / "family_wide_summary.csv"
    fam = {}
    if fam_path.exists():
        for r in csv.DictReader(open(fam_path, newline="")):
            fam[(r["cell"], r["lambda_ref"])] = r["threshold_verdict"]
    else:
        print("[iut-105] WARN: family_wide_summary.csv missing; refusal classes will "
              "use endpoint evidence only.", file=sys.stderr)

    cells = L.load_cells(Path(args.metrics_dir))
    rows, rs_rows = [], []
    for c in cells:
        evald = L.load_eval_arrays(c, cfg, pool_dir)
        committed = L.committed_for(c["dsname"], c["ts"])
        scheme = L.primary_scheme(c["meta"])
        scheme0 = c["meta"]["schemes"][0]
        losses_full, costs_full, cc, _ = L.losses_costs(evald, c["grid"], scheme)
        alpha, delta = c["alpha"], c["delta"]
        T = evald["T"]
        full_c = float(cc[:, T].mean())
        full_loss = 1.0 - evald["correct"][:, T]

        for lr_key in args.lambda_ref:
            blk = c["data"]["lambda_refs"][lr_key]
            resplits = blk["resplits"]
            edges = L.edges_for(committed, c["policy"], c["score"], lr_key)
            bucket = L.bucket_ids(evald["scores"], float(lr_key), edges)
            labels = sorted(int(k) for k in np.unique(bucket))
            masks = {k: bucket == k for k in labels}
            min_nk = min(int(m.sum()) for m in masks.values())

            cert = refuse = uncond_fail = cond_fail = 0
            cert_costs, deployed_costs, sel_idx = [], [], []
            marg_deployed = []
            for rs, r in enumerate(resplits):
                iut_idx = r["schemes"][scheme0]["cafa_iut"].get("lambda_idx")
                m_idx = r["schemes"][scheme0]["cafa_marginal"].get("lambda_idx")
                marg_deployed.append(full_c if m_idx is None
                                     else float(costs_full[:, int(m_idx)].mean()))
                if iut_idx is None:
                    refuse += 1
                    deployed_costs.append(full_c)
                    fail = 0
                else:
                    cert += 1
                    i = int(iut_idx)
                    sel_idx.append(i)
                    cost_i = float(costs_full[:, i].mean())
                    cert_costs.append(cost_i)
                    deployed_costs.append(cost_i)
                    fail = int(any(float(losses_full[masks[k], i].mean()) > alpha
                                   for k in labels))
                    uncond_fail += fail
                    cond_fail += fail
                rs_rows.append({"cell": c["label"], "lambda_ref": lr_key, "resplit": rs,
                                "certified": int(iut_idx is not None),
                                "lambda_idx": (None if iut_idx is None else int(iut_idx)),
                                "any_stratum_pool_fail": fail})
            n = len(resplits)
            assert cert + refuse == n, f"cert+refuse != {n} on {c['label']} lr={lr_key}"
            cr, crlo, crhi = L.wilson(cert, n)
            uf, uflo, ufhi = L.wilson(uncond_fail, n)
            if cert > 0:
                cf, cflo, cfhi = L.wilson(cond_fail, cert)
            else:
                cf = cflo = cfhi = None

            # blocking-stratum evidence for refusal classification
            deep = max(labels)
            pop = blk["population"]["per_stratum_full"].get(str(deep), {})
            endpoint_fail = pop.get("verdict") == "infeasible"
            fam_v = fam.get((c["label"], lr_key))
            if refuse == 0:
                refusal_class = "n/a (never refuses)"
            elif fam_v == "family-wide failure certified":
                refusal_class = "A: refusal with certified family-wide failure"
            elif endpoint_fail:
                refusal_class = "B: refusal with certified endpoint failure only"
            else:
                refusal_class = "C: refusal, unresolved"

            rows.append({
                "cell": c["label"], "lambda_ref": lr_key, "n_resplits": n,
                "alpha": alpha, "delta": delta,
                "cert_rate": cr, "cert_lo": crlo, "cert_hi": crhi,
                "refusal_rate": refuse / n, "n_certified": cert,
                "uncond_fail_rate": uf, "uncond_lo": uflo, "uncond_hi": ufhi,
                "cond_fail_rate": cf, "cond_lo": cflo, "cond_hi": cfhi,
                "sel_lambda_min": (float(c["grid"][min(sel_idx)]) if sel_idx else None),
                "sel_lambda_median": (float(c["grid"][int(np.median(sel_idx))]) if sel_idx else None),
                "sel_lambda_max": (float(c["grid"][max(sel_idx)]) if sel_idx else None),
                "mean_certified_cost": (float(np.mean(cert_costs)) if cert_costs else None),
                "mean_deployed_cost": float(np.mean(deployed_costs)),
                "deployed_cost_over_full": float(np.mean(deployed_costs)) / full_c,
                "premium_vs_marginal": float(np.mean(deployed_costs)) / float(np.mean(marg_deployed)),
                "min_stratum_size": min_nk,
                "deepest_stratum": deep,
                "endpoint_failure_deepest": endpoint_fail,
                "family_verdict_deepest": fam_v or "n/a",
                "refusal_class": refusal_class,
                "nonvacuous": cert > 0,
            })
        print(f"[iut-105] {c['label']}: done 3 lambda_refs", flush=True)

    assert len(rows) == len(cells) * len(args.lambda_ref), "config count mismatch"

    def wcsv(name, data):
        with open(out_dir / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader(); w.writerows(data)
    wcsv("iut_by_lambda_ref.csv", rows)
    wcsv("iut_by_lambda_ref_resplits.csv", rs_rows)

    n_nonvac = sum(1 for r in rows if r["nonvacuous"])
    classes = Counter(r["refusal_class"] for r in rows if r["refusal_rate"] > 0)
    n_cond_fail = sum(1 for r in rows if r["cond_fail_rate"] not in (None, 0.0))

    lines = ["# CAFA v2 -- IUT BY REFERENCE THRESHOLD (105 configurations)\n",
             "_35 canonical cells x 3 lambda_refs, each over its 100 unique resplits; "
             "never pooled. 'Certification refusal with full-acquisition fallback' -- "
             "the system still predicts; this is NOT prediction abstention. "
             "Conditional-failure intervals use denominator n_certified and are "
             "omitted when n_certified = 0._\n",
             f"**Summary: {n_nonvac}/{len(rows)} configurations certify non-vacuously "
             f"(>= 1 certified selection); refusal classes among configs that ever "
             f"refuse: {dict(classes)}; configurations with any conditional "
             f"pool-failure among certified selections: {n_cond_fail}.**\n",
             "| cell | lr | cert rate [95% CI] | refusal | n_cert | uncond fail [CI] | "
             "cond fail [CI] | deployed cost/full | premium vs marginal | min n_k | "
             "refusal class |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        cond = ("n/a" if r["cond_fail_rate"] is None else
                f"{L.fmt(r['cond_fail_rate'], 2)} [{L.fmt(r['cond_lo'], 2)}, "
                f"{L.fmt(r['cond_hi'], 2)}]")
        lines.append(
            f"| {r['cell']} | {r['lambda_ref']} | {L.fmt(r['cert_rate'], 2)} "
            f"[{L.fmt(r['cert_lo'], 2)}, {L.fmt(r['cert_hi'], 2)}] | "
            f"{L.fmt(r['refusal_rate'], 2)} | {r['n_certified']} | "
            f"{L.fmt(r['uncond_fail_rate'], 2)} [{L.fmt(r['uncond_lo'], 2)}, "
            f"{L.fmt(r['uncond_hi'], 2)}] | {cond} | "
            f"{L.fmt(r['deployed_cost_over_full'], 3)} | "
            f"{L.fmt(r['premium_vs_marginal'], 2)} | {r['min_stratum_size']} | "
            f"{r['refusal_class']} |")
    (out_dir / "IUT_BY_LAMBDA_REF.md").write_text("\n".join(lines))

    cl = ["# CAFA v2 -- IUT OUTCOME CLASSIFICATION (three-outcome semantics)\n",
          "Every configuration that ever refuses is classified:\n",
          "- **A -- refusal with certified family-wide failure** (Task-1 IUT test "
          "rejects feasibility over the whole precommitted threshold family on the "
          "blocking stratum);",
          "- **B -- refusal with certified endpoint failure only** (full acquisition "
          "fails on the blocking stratum; family-wide failure not established);",
          "- **C -- refusal, unresolved** (neither established at the audit level).\n",
          f"Counts over the {len(rows)} configurations: {dict(classes)}; "
          f"{n_nonvac} configurations are non-vacuous (certify at least once); "
          "per-configuration labels in `iut_by_lambda_ref.csv` (column "
          "refusal_class).\n",
          "A valid summary sentence: 'Across 105 fixed configurations, "
          f"{n_nonvac} certify non-vacuously; refusals split into "
          f"{classes.get('A: refusal with certified family-wide failure', 0)} "
          "family-failure, "
          f"{classes.get('B: refusal with certified endpoint failure only', 0)} "
          "endpoint-only, and "
          f"{classes.get('C: refusal, unresolved', 0)} unresolved configurations.' "
          "Do NOT summarize as '0/35 false certifications' without certification and "
          "refusal counts."]
    (out_dir / "IUT_OUTCOME_CLASSIFICATION.md").write_text("\n".join(cl))

    # F12: certification rate by lambda_ref (ts0 greedy cells)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    prim = [r for r in rows if r["cell"].endswith("/greedy_entropy/ts0")]
    dsets = sorted({r["cell"].split("/")[0] for r in prim})
    width = 0.25
    for j, lr in enumerate(args.lambda_ref):
        vals = [next(r["cert_rate"] for r in prim
                     if r["cell"].startswith(ds) and r["lambda_ref"] == lr)
                for ds in dsets]
        ax.bar(np.arange(len(dsets)) + (j - 1) * width, vals, width, label=f"lr={lr}")
    ax.set_xticks(np.arange(len(dsets))); ax.set_xticklabels(dsets, fontsize=8)
    ax.set_ylabel("certification rate (100 resplits)")
    ax.set_title("F12 IUT certification rate by lambda_ref (ts0 greedy)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "F12_iut_certification_by_lambda_ref.pdf")
    fig.savefig(fig_dir / "F12_iut_certification_by_lambda_ref.png", dpi=150)
    plt.close(fig)

    # F13: cost/refusal frontier
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    for lr, marker in zip(args.lambda_ref, ("o", "s", "^")):
        xs = [r["refusal_rate"] for r in rows if r["lambda_ref"] == lr]
        ys = [r["deployed_cost_over_full"] for r in rows if r["lambda_ref"] == lr]
        ax.scatter(xs, ys, marker=marker, s=18, label=f"lr={lr}")
    ax.set_xlabel("certification-refusal rate")
    ax.set_ylabel("deployed cost / full (incl. fallback)")
    ax.set_title("F13 IUT cost-refusal frontier (105 configurations)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "F13_iut_cost_refusal_frontier.pdf")
    fig.savefig(fig_dir / "F13_iut_cost_refusal_frontier.png", dpi=150)
    plt.close(fig)

    print(f"[iut-105] wrote {len(rows)} config rows: non-vacuous {n_nonvac}, "
          f"refusal classes {dict(classes)}, conditional failures on {n_cond_fail} "
          "configs.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
