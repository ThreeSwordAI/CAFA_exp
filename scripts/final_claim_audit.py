#!/usr/bin/env python
"""Phase 5.3, Task 8 -- the final claim-decision artifact.

Assembles, from the Phase-5.3 canonical outputs ONLY (never from prose), the
per-dataset claim ledger and selects the licensed paper story (A/B/C per the
governing rule). Also scans the repository's markdown for prohibited phrases
so superseded claims can be fixed or moved to the changelog.

Requires (in --results-dir): family_wide_summary.csv, pool_plugin_eval.csv,
pool_stratum_eval.csv, iut_by_lambda_ref.csv, phase5_provenance.json.

Outputs: FINAL_CLAIM_DECISION.md + final_claim_decision.json.

Usage:
    python scripts/final_claim_audit.py --results-dir results_committed \
        --output-dir results_committed
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase53_lib as L  # noqa: E402

_REPO = Path(__file__).resolve().parents[1]
_PRIMARY_LR = "0.9"
_DATASETS = ("mnist", "tabular-MiniBooNE", "tabular-adult", "tabular-spambase")

_PROHIBITED = re.compile(
    r"no acquisition budget|no amount of acquisition|no rule could|"
    r"property of the data|coincides with|IUT abstains with proof|"
    r"2\.?3x|1\.6.?2\.4x|unsafe on 2 of 4", re.IGNORECASE)


def _read_csv(path: Path):
    return list(csv.DictReader(open(path, newline=""))) if path.exists() else []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase 5.3 final claim decision.")
    ap.add_argument("--results-dir", default="results_committed")
    ap.add_argument("--output-dir", default="results_committed")
    args = ap.parse_args(argv)

    rdir = Path(args.results_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fam = _read_csv(rdir / "family_wide_summary.csv")
    plug = _read_csv(rdir / "pool_plugin_eval.csv")
    strat = _read_csv(rdir / "pool_stratum_eval.csv")
    iut = _read_csv(rdir / "iut_by_lambda_ref.csv")
    prov = json.loads((rdir / "phase5_provenance.json").read_text()) \
        if (rdir / "phase5_provenance.json").exists() else {}

    decisions = []
    for ds in _DATASETS:
        cell = f"{ds}/greedy_entropy/ts0"
        f = next((r for r in fam if r["cell"] == cell and r["lambda_ref"] == _PRIMARY_LR), None)
        p = next((r for r in plug if r["cell"] == cell), None)
        deep = None
        if f:
            deep = next((r for r in strat if r["cell"] == cell
                         and r["lambda_ref"] == _PRIMARY_LR
                         and int(r["stratum"]) == int(f["stratum"])), None)
        i9 = next((r for r in iut if r["cell"] == cell and r["lambda_ref"] == _PRIMARY_LR), None)
        prov_row = next((r for r in prov.get("stratum_decision_table", [])
                         if r["dataset"] == ds), {})

        endpoint = "unresolved"
        if f:
            full_r = float(f["full_feature_risk"])
            alpha = float(f["alpha"])
            # endpoint failure = CP-certified (Task-1 threshold family includes the
            # lambda=1/full column, but the endpoint verdict itself uses the exact
            # binomial one-sided test on the full-feature column).
            n_k = int(f["n_k"])
            s_full = round(full_r * n_k)
            p_end = float(L.binom_upper_p([s_full], n_k, alpha)[0])
            gamma = float(f["gamma"])
            endpoint = ("failure" if p_end <= gamma else
                        ("feasible" if full_r <= alpha else "unresolved"))

        thr_v = f["threshold_verdict"] if f else "n/a"
        dep_v = f["depth_verdict"] if f else "n/a"
        thr_word = {"family-wide failure certified": "failure",
                    "feasible": "feasible", "unresolved": "unresolved"}.get(thr_v, "n/a")
        dep_word = {"family-wide failure certified": "failure",
                    "feasible": "feasible", "unresolved": "unresolved"}.get(dep_v, "n/a")

        if thr_word == "failure":
            allowed = ("On this stratum, no stopping threshold in the audited "
                       "precommitted threshold family attains the target"
                       + (" and no prefix depth along the frozen acquisition path "
                          "attains it" if dep_word == "failure" else "") + ".")
        elif endpoint == "failure":
            allowed = ("Even acquiring every available feature does not meet the "
                       "target for the deployed predictor on this stratum "
                       "(maximum-information / full-acquisition endpoint failure).")
        else:
            allowed = "The audit is unresolved at the available sample size."
        prohibited = ("'no possible feature subset, policy, acquisition strategy, or "
                      "budget can attain the target' (never licensed); "
                      + ("'family-wide failure' (only endpoint"
                         + ("/unresolved" if endpoint != "failure" else "")
                         + " is certified here)" if thr_word != "failure" else
                         "'no budget works' beyond the audited family"))

        decisions.append({
            "dataset": ds,
            "committed_alpha": float(f["alpha"]) if f else None,
            "primary_stratum_rule": "deepest precommitted nonempty bucket (label-free)",
            "deepest_equals_argmax_kstar": prov_row.get("coincide"),
            "lambda_ref_status": ("fine-resolution analysis; sweep {0.5,0.7,0.9} "
                                  "committed in tooling (provenance json q3/q4)"),
            "endpoint_verdict": endpoint,
            "threshold_family_verdict": thr_word,
            "threshold_family_p": float(f["family_p_value"]) if f else None,
            "min_threshold_risk": float(f["min_threshold_risk"]) if f else None,
            "argmin_lambda": float(f["argmin_lambda"]) if f else None,
            "depth_family_verdict": dep_word,
            "depth_family_p": float(f["depth_p_value"]) if f else None,
            "min_depth_risk": float(f["min_depth_risk"]) if f else None,
            "plugin_pool_exceed": float(p["pool_exceed"]) if p else None,
            "plugin_pool_ci": ([float(p["wilson_lo"]), float(p["wilson_hi"])] if p else None),
            "plugin_label": p["label"] if p else None,
            "selected_rule_deepest_pool_risk_mean": (float(deep["mean_pool_risk"]) if deep else None),
            "selected_rule_deepest_ratio_to_alpha": (float(deep["mean_ratio_to_alpha"]) if deep else None),
            "iut_primary_cert_rate": float(i9["cert_rate"]) if i9 else None,
            "iut_primary_cert_ci": ([float(i9["cert_lo"]), float(i9["cert_hi"])] if i9 else None),
            "iut_refusal_class": i9["refusal_class"] if i9 else None,
            "allowed_phrase": allowed,
            "prohibited_phrase": prohibited,
        })

    resolved = [d for d in decisions if d["endpoint_verdict"] == "failure"]
    fam_ok = [d for d in resolved if d["threshold_family_verdict"] == "failure"]
    if resolved and len(fam_ok) == len(resolved):
        story = ("STRONG: a marginally certified AFA system can conceal a "
                 "trajectory-defined stratum for which no stopping threshold in the "
                 "precommitted family meets the target; CAFA audits this family-wide "
                 "failure and uses a common-threshold certificate that refuses when "
                 "evidence does not support simultaneous validity.")
        outcome = "A"
    elif resolved:
        story = ("SAFE ENDPOINT: a marginally certified AFA system can conceal a "
                 "trajectory-defined stratum for which even the full-feature deployed "
                 "predictor remains above target; CAFA exposes this model-relative "
                 "endpoint failure and separates simultaneous certification from "
                 "evidence-sensitive refusal.")
        outcome = "B"
    else:
        story = ("UNRESOLVED: CAFA provides a trajectory-conditioned audit and "
                 "simultaneous certification framework; the benchmark study reveals "
                 "where available data can certify failure and where it must remain "
                 "unresolved.")
        outcome = "C"

    # prohibited-phrase scan over markdown (excluding instruction/changelog files)
    hits = []
    for p in sorted(_REPO.rglob("*.md")):
        rel = p.relative_to(_REPO).as_posix()
        if any(seg in rel for seg in (".venv", "data/", "results/")):
            continue
        for ln, line in enumerate(p.read_text(encoding="utf-8", errors="ignore")
                                  .splitlines(), 1):
            if _PROHIBITED.search(line):
                hits.append(f"{rel}:{ln}")
    record = {"header": L.provenance_header(), "scientific_outcome": outcome,
              "story": story, "decisions": decisions,
              "prohibited_phrase_hits": hits}
    (out_dir / "final_claim_decision.json").write_text(json.dumps(record, indent=2))

    lines = ["# CAFA v2 -- FINAL CLAIM DECISION (Phase 5.3, Task 8)\n",
             f"_git {record['header']['git_commit'][:12]}; "
             f"{record['header']['generated']}_\n",
             f"## Scientific outcome: **{outcome}**\n", f"> {story}\n",
             "## Per-dataset claim ledger\n",
             "| field | " + " | ".join(d["dataset"] for d in decisions) + " |",
             "|---|" + "---|" * len(decisions)]
    fields = [
        ("committed alpha", "committed_alpha", lambda v: f"{v:g}"),
        ("primary stratum rule", "primary_stratum_rule", lambda v: "deepest nonempty (label-free)"),
        ("deepest == argmax k*", "deepest_equals_argmax_kstar", str),
        ("endpoint verdict", "endpoint_verdict", str),
        ("threshold-family verdict", "threshold_family_verdict", str),
        ("family p-value", "threshold_family_p", lambda v: f"{v:.2e}"),
        ("min threshold risk (argmin lambda)", "min_threshold_risk",
         lambda v: f"{v:.4f}"),
        ("depth-family verdict", "depth_family_verdict", str),
        ("plugin pool exceed [CI]", "plugin_pool_exceed", lambda v: f"{v:.2f}"),
        ("plugin label", "plugin_label", str),
        ("selected-rule deepest pool risk (mean)", "selected_rule_deepest_pool_risk_mean",
         lambda v: f"{v:.4f}"),
        ("ratio to alpha", "selected_rule_deepest_ratio_to_alpha", lambda v: f"{v:.3f}"),
        ("IUT cert rate @0.9", "iut_primary_cert_rate", lambda v: f"{v:.2f}"),
        ("IUT refusal class", "iut_refusal_class", str),
    ]
    for name, key, f_ in fields:
        vals = []
        for d in decisions:
            v = d[key]
            vals.append("n/a" if v is None else f_(v))
        lines.append(f"| {name} | " + " | ".join(vals) + " |")
    lines.append("")
    lines.append("## Allowed / prohibited phrases per dataset\n")
    for d in decisions:
        lines.append(f"- **{d['dataset']}** ALLOWED: {d['allowed_phrase']}")
        lines.append(f"  PROHIBITED: {d['prohibited_phrase']}")
    lines.append("")
    lines.append(f"## Prohibited-phrase scan ({len(hits)} markdown hits to fix or "
                 "mark superseded)\n")
    for h in hits[:60]:
        lines.append(f"- {h}")
    if len(hits) > 60:
        lines.append(f"- ... and {len(hits) - 60} more (full list in the json)")
    (out_dir / "FINAL_CLAIM_DECISION.md").write_text("\n".join(lines))
    print(f"[claim] outcome {outcome}; wrote FINAL_CLAIM_DECISION.md + json "
          f"({len(hits)} prohibited-phrase hits found in repo markdown).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
