#!/usr/bin/env python
"""Phase 4 -- readiness-score ablation report (Task D of the canonical lock).

Question: is the infeasible stratum an artifact of the max-softmax readiness
score? Strata are defined by the first crossing of lambda_ref by the score, so
the audit's stratification depends on that choice.

For each dataset with both a softmax and a margin metrics JSON (ts, greedy):
  1. INVARIANT: the readiness score governs stopping, not acquisition -- the
     margin rollout's `order` and `correct` must be byte-identical to the
     softmax rollout's (only `scores` may differ). Asserted from the two pool
     caches; a FAIL means the ablation changed more than the stopping score.
  2. alpha unchanged (it comes from the full-acquisition floor, which is
     score-independent; both evals read the same committed JSON) -- asserted.
  3. Audit comparison at lambda_ref = 0.9: hardest stratum k*, R_full(k*) with
     95% CP LCB, three-way verdict, under each score's own probe-committed
     stratification.
  4. H2 snapshot at lambda_ref = 0.9, primary scheme: marginal + plugin
     violation rates, cafa cost ratio.

Verdict: the audit finding is / is not robust to the readiness-score choice
(compared on the DETECTING datasets; spambase is undetermined by design).

Usage:
    python scripts/phase4_score_ablation.py [--metrics-dir metrics_v2]
        [--out analysis_v2] [--train-seed 0] [--score margin]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.pool import load_pool_cache  # noqa: E402

_LR = "0.9"
_POLICY = "greedy_entropy"


def _fmt(x, nd=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "n/a"
    return f"{x:.{nd}f}"


def _nanmean(xs):
    arr = np.asarray([x for x in xs if x is not None], dtype=float)
    arr = arr[~np.isnan(arr)]
    return float(arr.mean()) if arr.size else float("nan")


def audit_and_h2(data: dict):
    """(k*, R_full, LCB, verdict) + H2 snapshot at _LR from one metrics JSON."""
    alpha = float(data["alpha"])
    blk = data["lambda_refs"].get(_LR)
    if blk is None:
        return None
    pop = blk["population"]
    resplits = blk["resplits"]
    scheme = "inverse_info" if "inverse_info" in data["meta"]["schemes"] else "uniform"
    best_k, best = None, None
    for ks, info in pop["per_stratum_full"].items():
        if info["risk"] is None or int(info["n"]) == 0:
            continue
        if best is None or float(info["risk"]) > float(best["risk"]):
            best_k, best = ks, info
    marg_risks = [r["schemes"][scheme]["cafa_marginal"]["realized_risk"] for r in resplits]
    plug_risks = [r["schemes"][scheme]["plugin"]["realized_risk"] for r in resplits]
    marg_cost = _nanmean([r["schemes"][scheme]["cafa_marginal"]["realized_cost"] for r in resplits])
    full_cost = _nanmean([r["schemes"][scheme]["oracle_full"]["realized_cost"] for r in resplits])
    return {
        "alpha": alpha, "scheme": scheme,
        "k_star": best_k, "R_full": best["risk"] if best else None,
        "lcb": best["cp_lcb95"] if best else None,
        "verdict": best["verdict"] if best else "n/a",
        "n_kstar": best["n"] if best else None,
        "marg_viol": float(np.mean([1.0 if (x is not None and x > alpha) else 0.0
                                    for x in marg_risks])),
        "plug_viol": float(np.mean([1.0 if (x is not None and x > alpha) else 0.0
                                    for x in plug_risks])),
        "cost_ratio_full": marg_cost / full_cost if full_cost else float("nan"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAFA v2 Phase-4 score-ablation report.")
    ap.add_argument("--metrics-dir", default="metrics_v2")
    ap.add_argument("--out", default="analysis_v2")
    ap.add_argument("--train-seed", type=int, default=0)
    ap.add_argument("--score", default="margin")
    args = ap.parse_args(argv)

    cfg = config.load_experiment()
    paths = config.load_paths()
    metrics_dir = Path(args.metrics_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = int(args.train_seed)
    base_score = cfg["method"].get("procedure_score", "softmax")

    # Datasets with both variants present.
    pairs = []
    for p in sorted(metrics_dir.glob(f"*_ts{ts}_{_POLICY}_{args.score}.json")):
        dsname = p.name[: -len(f"_ts{ts}_{_POLICY}_{args.score}.json")]
        base = metrics_dir / f"{dsname}_ts{ts}_{_POLICY}.json"
        if base.exists():
            pairs.append((dsname, base, p))
    if not pairs:
        print(f"ERROR: no ({base_score}, {args.score}) metric pairs under {metrics_dir}.",
              file=sys.stderr)
        return 2

    lines = ["# CAFA v2 -- PHASE 4: readiness-score ablation\n",
             f"_Policy: {_POLICY}, train_seed = {ts}, scores: {base_score} (canonical) "
             f"vs {args.score}. The score governs STOPPING, not acquisition; each score "
             "has its own probe-committed stratification (seed 777); alpha is "
             "score-independent. Audit columns at lambda_ref = "
             f"{_LR}, primary scheme._\n"]

    invariant_ok = True
    robust = []
    not_robust = []
    lines.append("## Invariant + alpha checks\n")
    for dsname, base_path, abl_path in pairs:
        cache_dir = Path(paths.results_root) / "pool_v2"
        c_base = load_pool_cache(cache_dir / f"{dsname}_ts{ts}_{_POLICY}_{base_score}.npz")
        c_abl = load_pool_cache(cache_dir / f"{dsname}_ts{ts}_{_POLICY}_{args.score}.npz")
        same_order = bool(np.array_equal(c_base["order"], c_abl["order"]))
        same_correct = bool(np.array_equal(c_base["correct"], c_abl["correct"]))
        scores_differ = not np.array_equal(c_base["scores"], c_abl["scores"])
        ok = same_order and same_correct
        invariant_ok &= ok
        d_base = json.loads(base_path.read_text())
        d_abl = json.loads(abl_path.read_text())
        alpha_same = float(d_base["alpha"]) == float(d_abl["alpha"])
        invariant_ok &= alpha_same
        lines.append(f"- {dsname}: order byte-identical = {same_order}, correct "
                     f"byte-identical = {same_correct}, scores differ = {scores_differ} "
                     f"-> {'PASS' if ok else 'FAIL'}; alpha unchanged = {alpha_same} "
                     f"({d_base['alpha']:g}).")
    lines.append("")

    lines.append("## Audit + H2 under each score\n")
    lines.append("| dataset | score | k* | n(k*) | R_full(k*) [95% LCB] | verdict | "
                 "marg viol@0.9 | plugin viol@0.9 | cafa cost/full |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for dsname, base_path, abl_path in pairs:
        d_base = json.loads(base_path.read_text())
        d_abl = json.loads(abl_path.read_text())
        a_base = audit_and_h2(d_base)
        a_abl = audit_and_h2(d_abl)
        for label, a in ((base_score, a_base), (args.score, a_abl)):
            if a is None:
                continue
            lines.append(f"| {dsname} | {label} | {a['k_star']} | {a['n_kstar']} | "
                         f"{_fmt(a['R_full'])} [{_fmt(a['lcb'])}] | {a['verdict']} | "
                         f"{_fmt(a['marg_viol'], 2)} | {_fmt(a['plug_viol'], 2)} | "
                         f"{_fmt(a['cost_ratio_full'], 3)} |")
        if a_base and a_abl:
            if a_base["verdict"] == a_abl["verdict"]:
                robust.append((dsname, a_base["verdict"]))
            else:
                not_robust.append((dsname, a_base["verdict"], a_abl["verdict"]))
    lines.append("")

    lines.append("## Verdict\n")
    if not not_robust and robust:
        lines.append(f"**The audit finding IS robust to the readiness-score choice** on "
                     f"{len(robust)} of {len(pairs)} tested datasets: " +
                     ", ".join(f"{d} ({v})" for d, v in robust) +
                     f". The verdict at lambda_ref = {_LR} is unchanged when the "
                     f"stopping score is replaced by {args.score} (with its own "
                     "probe-committed stratification).")
    else:
        lines.append("**The audit finding is NOT uniformly robust to the readiness-score "
                     "choice.** Agreement: " + (", ".join(f"{d} ({v})" for d, v in robust) or "none") +
                     ". Disagreement: " +
                     (", ".join(f"{d} ({b} -> {a})" for d, b, a in not_robust) or "none") +
                     ". Scope the audit claim accordingly.")
    lines.append("")
    lines.append(f"Invariant status: {'ALL PASS' if invariant_ok else 'FAILURES PRESENT'} "
                 "(order/correct byte-identical across scores; alpha unchanged).")

    (out_dir / "PHASE4_SCORE_ABLATION.md").write_text("\n".join(lines))
    print(f"[phase4] wrote {out_dir / 'PHASE4_SCORE_ABLATION.md'} "
          f"(invariant={'PASS' if invariant_ok else 'FAIL'}; robust on "
          f"{[d for d, _ in robust]}; disagreement on {[d for d, _, _ in not_robust]})",
          flush=True)
    return 0 if invariant_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
