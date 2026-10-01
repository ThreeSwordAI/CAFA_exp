#!/usr/bin/env python
"""v3 -- independent diagnosis of a cell whose cascade test-violation rate exceeds delta (torch-free).

Instruction 4.4: before reporting such a cell, rule out implementation bugs.  This script recomputes,
from the raw pool cache and the committed JSON only (no run_cascade_sweep code):

  1. split integrity: probe / calpool / test positions from splits_v3.v3_positions match the committed
     sha256 digests and sizes, and are pairwise disjoint and cover the heldout set;
  2. stratum alignment: the reference depth (first depth whose score >= lambda_ref, T if never) and the
     bucket ids from the committed edges, recomputed with plain numpy, equal cafa.metrics.reference_buckets
     on both the calibration pool and the test split;
  3. for every draw the sweep flagged as a violation: the calibration rows are a subset of the calpool,
     disjoint from test; the deployed rule's per-stratum calibration risk (selective risk for tier 3) and
     its Hoeffding-Bentkus p-value (frozen risk_control primitive) on the calibration rows, and the
     per-stratum test risk recomputed independently;
  4. the deployed rules' per-stratum risk on calpool, test, and calpool+test pooled (a larger-sample
     estimate of the population stratum risk).

    python scripts/diagnose_violation_v3.py --dataset tabular:MiniBooNE --policy greedy_entropy --train-seed 0 --lambda-ref-key dep
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))
from cafa.metrics import reference_buckets  # noqa: E402
from cafa.pool import load_pool_cache  # noqa: E402
from cafa.risk_control import hoeffding_bentkus_pvalue  # noqa: E402
from cafa.splits import split_digest  # noqa: E402
from cafa.splits_v3 import calibration_draw, v3_positions  # noqa: E402
from commit_v3 import build_grid, dsname_of  # noqa: E402


def ref_depth_np(scores, lam):
    hit = scores >= lam
    T = scores.shape[1] - 1
    return np.where(hit.any(1), hit.argmax(1), T)


def rule_loss_answered(S, C, tier, param, grid, T):
    """(loss, answered) per row for a deployed rule, recomputed independently of cafa.cascade."""
    if tier == 1:                      # stop at first depth with score >= lambda, else T
        d = ref_depth_np(S, param)
        return 1.0 - C[np.arange(len(d)), d], np.ones(len(d), bool)
    if tier == 2:                      # forced depth t
        t = int(round(param))
        return 1.0 - C[:, t], np.ones(S.shape[0], bool)
    ans = S[:, T] >= param             # tier 3: full acquisition, answer iff g_T >= mu
    return 1.0 - C[:, T], ans


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--policy", default="greedy_entropy")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--lambda-ref-key", default="dep")
    p.add_argument("--scheme", default="uniform")
    p.add_argument("--metrics-dir", default=None)
    p.add_argument("--output", default=None, help="write the diagnosis as JSON")
    a = p.parse_args(argv)
    rr = Path(os.environ["RESULTS_ROOT"])
    dsn, ts = dsname_of(a.dataset), a.train_seed
    com = json.loads((REPO / "configs" / f"committed_v3_{dsn}_ts{ts}.json").read_text())
    met = json.loads((Path(a.metrics_dir or rr / "metrics_v3") / f"{dsn}_ts{ts}_{a.policy}_softmax.json").read_text())
    cache = load_pool_cache(rr / "pool_v3" / f"{dsn}_ts{ts}_{a.policy}_softmax.npz")
    S, C = np.asarray(cache["scores"]), np.asarray(cache["correct"])
    n, T = S.shape[0], S.shape[1] - 1
    alpha, sp = float(com["alpha"]), com["split"]
    out = {"dataset": a.dataset, "policy": a.policy, "train_seed": ts, "lambda_ref_key": a.lambda_ref_key,
           "alpha": alpha, "checks": {}}

    # 1. split integrity
    pos = v3_positions(n, sp["probe_frac"], sp["probe_seed"], sp["test_frac_of_eval"], sp["test_seed"])
    dig_ok = all(split_digest(pos[k]) == sp["digest"][k] for k in ("probe", "calpool", "test"))
    sizes_ok = (pos["probe"].size, pos["calpool"].size, pos["test"].size) == (sp["n_probe"], sp["n_calpool"], sp["n_test"])
    allp = np.concatenate([pos["probe"], pos["calpool"], pos["test"]])
    disjoint = np.unique(allp).size == allp.size and np.unique(allp).size == n
    out["checks"]["split_digests_match"] = bool(dig_ok)
    out["checks"]["split_sizes_match"] = bool(sizes_ok)
    out["checks"]["probe_calpool_test_disjoint_and_cover"] = bool(disjoint)
    print(f"[diag] splits: digests match={dig_ok} sizes match={sizes_ok} disjoint+cover={disjoint}")

    # 2. stratum alignment
    lam = float(com["lambda_refs"][a.policy][a.lambda_ref_key])
    edges = np.asarray(com["edges"][a.policy][a.lambda_ref_key]["edges"], float)
    cal, test = pos["calpool"], pos["test"]
    b_np = {nm: np.searchsorted(edges, ref_depth_np(S[ix], lam), side="right") for nm, ix in (("calpool", cal), ("test", test))}
    b_rb = {nm: reference_buckets(S[ix], lam, 5, 1, edges=edges)[0] for nm, ix in (("calpool", cal), ("test", test))}
    align = {nm: bool(np.array_equal(b_np[nm], b_rb[nm])) for nm in b_np}
    # the searchsorted convention is a guess; if it disagrees, report both bucket counts
    out["checks"]["bucket_ids_numpy_vs_reference_buckets"] = align
    print(f"[diag] lambda_ref={lam:.4f} edges={edges.tolist()} bucket ids numpy==reference_buckets: {align}")
    bc, bt = b_rb["calpool"], b_rb["test"]
    out["stratum_sizes"] = {"calpool": {int(k): int((bc == k).sum()) for k in np.unique(bc)},
                            "test": {int(k): int((bt == k).sum()) for k in np.unique(bt)}}

    # 3. + 4. flagged draws
    blk = met["lambda_refs"][a.lambda_ref_key]["schemes"][a.scheme]
    mu = np.asarray(com["escalation"][a.policy][a.lambda_ref_key]["mu_asc"], float)
    grid = build_grid({"grid": com["grid"]})
    rows, rules = [], {}
    for r in blk["draws"]:
        c = r["cascade"]
        if c["tier"] == 0:
            continue
        rules.setdefault((c["tier"], round(float(c["param"]), 12)), []).append((r["draw"], c["violation"]))
    for (tier, param), draws in sorted(rules.items()):
        lc, ac = rule_loss_answered(S[cal], C[cal], tier, param, grid, T)
        lt, at = rule_loss_answered(S[test], C[test], tier, param, grid, T)
        rec = {"tier": tier, "param": param, "n_draws": len(draws), "n_flagged": int(sum(v for _, v in draws)), "strata": {}}
        for k in np.unique(bt):
            mc, mt = (bc == k) & ac, (bt == k) & at
            nc, nt = int(mc.sum()), int(mt.sum())
            rc = float(lc[mc].mean()) if nc else None
            rt = float(lt[mt].mean()) if nt else None
            rp = float((lc[mc].sum() + lt[mt].sum()) / (nc + nt)) if nc + nt else None
            rec["strata"][int(k)] = {"n_answered_calpool": nc, "risk_calpool": rc, "n_answered_test": nt,
                                     "risk_test": rt, "risk_pooled": rp}
        rows.append(rec)
        s = "; ".join(f"k{k}: cal {v['risk_calpool']:.4f} (n {v['n_answered_calpool']}) test {v['risk_test']:.4f} "
                      f"(n {v['n_answered_test']}) pooled {v['risk_pooled']:.4f}" for k, v in rec["strata"].items()
                      if v["risk_test"] is not None)
        print(f"[diag] tier {tier} param {param:.4f}: deployed in {len(draws)} draws, flagged {rec['n_flagged']} | {s}")
    out["deployed_rules"] = rows

    # per flagged draw: calibration rows subset of calpool & disjoint from test; HB p-values on cal rows
    checks = []
    for r in blk["draws"]:
        c = r["cascade"]
        if not c["violation"]:
            continue
        cal_pos = calibration_draw(cal, r["draw"], sp["cal_frac_of_pool"])
        sub_ok = bool(np.isin(cal_pos, cal).all() and not np.isin(cal_pos, test).any())
        idx = np.nonzero(np.isin(cal, cal_pos))[0]
        lc, ac = rule_loss_answered(S[cal][idx], C[cal][idx], c["tier"], c["param"], grid, T)
        pv = {}
        for k in c["k_cal"]:
            m = (bc[idx] == k) & ac
            nk = int(m.sum())
            pv[int(k)] = {"n": nk, "risk_cal_draw": float(lc[m].mean()) if nk else None,
                          "hb_p": float(hoeffding_bentkus_pvalue(float(lc[m].mean()), nk, alpha)) if nk else 1.0}
        checks.append({"draw": r["draw"], "tier": c["tier"], "param": c["param"], "cal_rows_subset_of_calpool_not_test": sub_ok,
                       "per_stratum_cal": pv, "test_stratum_risk_sweep": c["test_stratum_risk"]})
        print(f"[diag] draw {r['draw']}: tier {c['tier']} cal⊂calpool,∉test={sub_ok} | " +
              "; ".join(f"k{k}: n {v['n']} cal risk {v['risk_cal_draw']:.4f} HB p {v['hb_p']:.4g}" for k, v in pv.items()))
    out["flagged_draws"] = checks
    if a.output:
        Path(a.output).parent.mkdir(parents=True, exist_ok=True)
        Path(a.output).write_text(json.dumps(out, indent=1))
        print(f"[diag] wrote {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
