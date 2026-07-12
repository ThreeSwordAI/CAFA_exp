#!/usr/bin/env python
"""Phase 5.3, Step 0 -- provenance and implementation audit.

Answers, from the code and versioned history plus light computed checks on
the canonical caches, the ten provenance questions of the Phase-5.3 spec, and
records the REQUIRED PROVENANCE DECISION:

  * k* (argmax of observed full-feature stratum risk) USES evaluation labels
    -> exploratory after selection. The label-free confirmatory stratum is
    the DEEPEST precommitted nonempty bucket. This script computes both per
    primary cell and reports where they coincide.
  * lambda_ref = 0.9 as the fine-resolution primary: checks whether the
    sweep values and the "primary = largest configured lambda_ref" rule are
    visible in versioned history before the first canonical results commit.

Outputs: <output-dir>/PHASE5_PROVENANCE.md + phase5_provenance.json.

Usage:
    python scripts/phase5_provenance.py --metrics-dir results_committed/metrics \
        --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase53_lib as L  # noqa: E402

from cafa import config  # noqa: E402

_PRIMARY = [("mnist", "greedy_entropy"), ("tabular-adult", "greedy_entropy"),
            ("tabular-MiniBooNE", "greedy_entropy"), ("tabular-spambase", "greedy_entropy")]
_LR = "0.9"


def _git(args):
    try:
        return subprocess.run(["git"] + args, capture_output=True, text=True,
                              cwd=Path(__file__).resolve().parents[1],
                              check=True).stdout.strip()
    except Exception as exc:
        return f"(git query failed: {exc})"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase 5.3 provenance audit.")
    ap.add_argument("--metrics-dir", default="results_committed/metrics")
    ap.add_argument("--pool-dir", default=None)
    ap.add_argument("--output-dir", default="results_committed")
    args = ap.parse_args(argv)

    cfg = config.load_experiment()
    pool_dir = Path(args.pool_dir) if args.pool_dir else L.default_pool_dir()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cells = L.load_cells(Path(args.metrics_dir))

    # ---- computed checks on the primary cells ----
    stratum_rows = []
    lambda1_rows = []
    for dsname, policy in _PRIMARY:
        cell = next(c for c in cells if c["dsname"] == dsname and c["policy"] == policy
                    and c["ts"] == 0 and c["score"] == "softmax")
        evald = L.load_eval_arrays(cell, cfg, pool_dir)
        committed = L.committed_for(dsname, 0)
        edges = L.edges_for(committed, policy, "softmax", _LR)
        bucket = L.bucket_ids(evald["scores"], float(_LR), edges)
        deep = L.deepest_nonempty(bucket)
        pop = cell["data"]["lambda_refs"][_LR]["population"]["per_stratum_full"]
        argmax_k = max((k for k in pop if pop[k]["risk"] is not None and pop[k]["n"] > 0),
                       key=lambda k: pop[k]["risk"])
        stratum_rows.append({"dataset": dsname, "deepest_nonempty": deep,
                             "argmax_risk_kstar": int(argmax_k),
                             "coincide": deep == int(argmax_k),
                             "n_deepest": int((bucket == deep).sum())})
        # lambda = 1 interpretation: does the last grid column equal full acquisition?
        grid = cell["grid"]
        s_full = L.stop_index_matrix(evald["scores"], grid)
        frac_at_T = float((s_full[:, -1] == evald["T"]).mean())
        r_last = float((1.0 - evald["correct"][np.arange(evald["n_eval"]), s_full[:, -1]]).mean())
        r_full = float((1.0 - evald["correct"][:, evald["T"]]).mean())
        lambda1_rows.append({"dataset": dsname, "frac_rows_stopping_at_T_under_lambda1": frac_at_T,
                             "risk_at_lambda1": r_last, "full_feature_risk": r_full,
                             "identical": abs(r_last - r_full) < 1e-12})

    # ---- versioned-history checks ----
    hist_sweep = _git(["log", "--format=%h %ad %s", "--date=short", "-S",
                       "lambda_refs: [0.5, 0.7, 0.9]", "--", "configs/experiment.yaml"])
    hist_primary = _git(["log", "--format=%h %ad %s", "--date=short", "-S",
                         "primary_lr", "--", "scripts/analyze_results.py"])
    hist_first_metrics = _git(["log", "--diff-filter=A", "--format=%h %ad %s",
                               "--date=short", "--", "results_committed/metrics"])

    record = {
        "header": L.provenance_header({"metrics_dir": str(args.metrics_dir),
                                       "pool_dir": str(pool_dir)}),
        "q1_kstar_rule": ("k* in the frozen H3 tables = argmax over populated strata of "
                          "the observed full-feature pool risk (make_canonical_results.py, "
                          "phase3_report.py)."),
        "q2_kstar_uses_labels": ("YES -- argmax-of-observed-risk consumes evaluation labels; "
                                 "pointwise intervals on that stratum are post-selection. "
                                 "DECISION: the confirmatory stratum for Phase 5.3 is the "
                                 "DEEPEST precommitted nonempty bucket (label-free, "
                                 "trajectory-defined); the argmax-risk stratum is reported "
                                 "as exploratory where the two differ."),
        "q3_q4_lambda_ref_history": {
            "lambda_ref_sweep_in_config": hist_sweep,
            "primary_equals_largest_rule_in_analyzer": hist_primary,
            "first_canonical_metrics_commit": hist_first_metrics,
            "assessment": ("The {0.5, 0.7, 0.9} sweep and the 'primary = largest "
                           "configured lambda_ref' analyzer rule were committed in the "
                           "tooling commits; whether those PRECEDE the first canonical "
                           "results commit is read off the dates above. lambda_ref = 0.9 "
                           "is reported as the fine-resolution analysis; all three "
                           "lambda_refs are always computed and reported (105 IUT "
                           "configurations in Phase 5.3)."),
        },
        "q5_grid": "np.linspace(0.0, 1.0, 100) -- 100 thresholds, committed in configs/experiment.yaml (method.grid).",
        "q6_lambda1": {
            "definition": ("stop at the first step t with score >= 1.0; rows never "
                           "reaching 1.0 stop at T (full acquisition). Softmax scores can "
                           "saturate to exactly 1.0 in float32, so lambda=1 is NOT "
                           "guaranteed to equal the full-feature endpoint row-by-row; "
                           "measured below."),
            "measured": lambda1_rows,
        },
        "q7_threshold_to_predictions": ("stop-index matrix: s(i, j) = first t with "
                                        "scores[i, t] >= grid[j] (else T); loss = "
                                        "1 - correct[i, s]; identical code in "
                                        "run_eval_sweep/metrics.stops_from_grid_np."),
        "q8_pool_risk": ("mean of the loss column over ALL eval rows (exact on the fixed "
                         "evaluation pool); per-stratum = same restricted to a "
                         "probe-committed bucket."),
        "q9_refusals": ("lambda_idx = None => 'abstained'/refusal recorded explicitly; "
                        "deployment falls back to FULL ACQUISITION and the system still "
                        "predicts (certification refusal with full-acquisition fallback, "
                        "NOT prediction abstention); fallback realized risk/cost recorded; "
                        "never counted as a violation and never dropped."),
        "q10_resplits": ("100 unique resplits: independent seeded permutations "
                         "(default_rng(1_000_000 + seed)) of the eval indices, split "
                         "50/50 -- random split assignments, not folds; marginal CAFA is "
                         "lambda_ref-independent so the 100 outcomes are counted ONCE "
                         "(never n = 300)."),
        "stratum_decision_table": stratum_rows,
    }

    (out_dir / "phase5_provenance.json").write_text(json.dumps(record, indent=2))

    lines = ["# CAFA v2 -- PHASE 5.3 PROVENANCE AUDIT\n"]
    lines.append(f"_git {record['header']['git_commit'][:12]}; host "
                 f"{record['header']['host']}; {record['header']['generated']}_\n")
    lines.append("## The required provenance decision\n")
    lines.append("- **k\\*** as frozen (argmax observed stratum risk) USES evaluation "
                 "labels -> treated as EXPLORATORY after selection.")
    lines.append("- **Confirmatory stratum** = deepest precommitted nonempty bucket "
                 "(trajectory-defined, label-free). Coincidence with argmax-k\\* per "
                 "primary cell (lambda_ref = 0.9):\n")
    lines.append("| dataset | deepest nonempty | argmax-risk k* | coincide | n(deepest) |")
    lines.append("|---|---|---|---|---|")
    for r in stratum_rows:
        lines.append(f"| {r['dataset']} | {r['deepest_nonempty']} | {r['argmax_risk_kstar']} | "
                     f"{'YES' if r['coincide'] else 'NO -- argmax stratum is exploratory'} | "
                     f"{r['n_deepest']} |")
    lines.append("")
    lines.append("- **lambda_ref = 0.9**: the sweep {0.5, 0.7, 0.9} and the analyzer's "
                 "'primary = largest configured' rule live in the tooling commits (git "
                 "evidence in phase5_provenance.json, q3_q4). Phase 5.3 reports it as the "
                 "fine-resolution analysis and always publishes all three lambda_refs.")
    lines.append("")
    lines.append("## lambda = 1 interpretation (measured)\n")
    lines.append("| dataset | frac rows stopping at T under lambda=1 | risk at lambda=1 | full-feature risk | identical |")
    lines.append("|---|---|---|---|---|")
    for r in lambda1_rows:
        lines.append(f"| {r['dataset']} | {L.fmt(r['frac_rows_stopping_at_T_under_lambda1'])} | "
                     f"{L.fmt(r['risk_at_lambda1'], 6)} | {L.fmt(r['full_feature_risk'], 6)} | "
                     f"{'yes' if r['identical'] else 'NO (softmax saturation)'} |")
    lines.append("")
    lines.append("## The remaining answers (q5-q10)\n")
    for k in ("q5_grid", "q7_threshold_to_predictions", "q8_pool_risk", "q9_refusals",
              "q10_resplits"):
        lines.append(f"- **{k}**: {record[k]}")
    lines.append("")
    lines.append("Full machine-readable record: `phase5_provenance.json` (includes the "
                 "git-history evidence for the lambda_ref primary designation).")
    (out_dir / "PHASE5_PROVENANCE.md").write_text("\n".join(lines))
    print(f"[provenance] wrote PHASE5_PROVENANCE.md + json "
          f"(deepest==argmax on "
          f"{sum(1 for r in stratum_rows if r['coincide'])}/{len(stratum_rows)} primary cells).",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
