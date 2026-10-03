#!/usr/bin/env python
"""v3 -- independent diagnosis of a cell whose cascade test-violation rate exceeds delta (torch-free).

Instruction 4.4: before reporting such a cell, rule out implementation bugs.  This script recomputes,
from the raw pool cache and the committed JSON only (no run_cascade_sweep code):

  1. split integrity, per split: probe / calpool / test positions from splits_v3 match the committed
     sha256 digests and sizes, and are pairwise disjoint and cover the heldout set;
  2. stratum alignment, per split: the reference depth (first depth whose score >= lambda_ref, T if never)
     and the bucket ids from the committed edges, recomputed with plain numpy, equal
     cafa.metrics.reference_buckets on both the calibration pool and the test split;
  3. for every draw the sweep flagged as a (raw) violation: the calibration rows are a subset of its
     split's calpool, disjoint from that split's test; the deployed rule's per-stratum calibration risk
     (selective risk for tier 3) and its Hoeffding-Bentkus p-value (risk_control primitive) on the
     calibration rows; the per-stratum test errors / n recomputed independently and the exact one-sided
     binomial test p-value (round-2 ``certified_violation``), compared with the sweep record;
  4. per split, the deployed rules' per-stratum risk on calpool, test, and calpool+test pooled (a
     larger-sample estimate of the population stratum risk), and the split's raw / certified violation
     rates.

Round 2: multi-split layout (the commit's ``split.test_seeds``; each draw record carries ``split_seed``).
A round-1 metrics file (single split, no ``split_seed``) is diagnosed on the primary split.

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
from cafa.localization import binom_upper_p  # noqa: E402
from cafa.metrics import reference_buckets  # noqa: E402
from cafa.pool import load_pool_cache  # noqa: E402
from cafa.risk_control import hoeffding_bentkus_pvalue  # noqa: E402
from cafa.splits import split_digest  # noqa: E402
from cafa.splits_v3 import calibration_draw, v3_positions_multi  # noqa: E402
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
    p.add_argument("--committed", default=None, help="committed JSON (default configs/committed_v3_{ds}_ts{ts}.json)")
    p.add_argument("--output", default=None, help="write the diagnosis as JSON")
    a = p.parse_args(argv)
    rr = Path(os.environ["RESULTS_ROOT"])
    dsn, ts = dsname_of(a.dataset), a.train_seed
    com = json.loads(Path(a.committed or REPO / "configs" / f"committed_v3_{dsn}_ts{ts}.json").read_text())
    met = json.loads((Path(a.metrics_dir or rr / "metrics_v3") / f"{dsn}_ts{ts}_{a.policy}_softmax.json").read_text())
    cache = load_pool_cache(rr / "pool_v3" / f"{dsn}_ts{ts}_{a.policy}_softmax.npz")
    S, C = np.asarray(cache["scores"]), np.asarray(cache["correct"])
    n, T = S.shape[0], S.shape[1] - 1
    alpha, sp = float(com["alpha"]), com["split"]
    primary = int(sp["test_seed"])
    seeds = [int(x) for x in sp.get("test_seeds", [primary])]
    out = {"dataset": a.dataset, "policy": a.policy, "train_seed": ts, "lambda_ref_key": a.lambda_ref_key,
           "alpha": alpha, "test_seeds": seeds, "checks": {}, "by_split": {}}

    lam = float(com["lambda_refs"][a.policy][a.lambda_ref_key])
    edges = np.asarray(com["edges"][a.policy][a.lambda_ref_key]["edges"], float)
    blk = met["lambda_refs"][a.lambda_ref_key]["schemes"][a.scheme]
    mu = np.asarray(com["escalation"][a.policy][a.lambda_ref_key]["mu_asc"], float)
    grid = build_grid({"grid": com["grid"]})
    print(f"[diag] lambda_ref={lam:.4f} edges={edges.tolist()} splits={seeds}")

    pos_all = {ps["test_seed"]: ps for ps in v3_positions_multi(n, sp["probe_frac"], sp["probe_seed"],
                                                               sp["test_frac_of_eval"], seeds)}
    all_ok = {"split_digests_match": True, "split_sizes_match": True, "probe_calpool_test_disjoint_and_cover": True,
              "bucket_ids_numpy_vs_reference_buckets": True}
    for seed, pos in pos_all.items():
        bs = {}
        # 1. split integrity
        ref = sp["digest"] if seed == primary else sp["by_test_seed"][str(seed)]["digest"]
        sz = (sp["n_calpool"], sp["n_test"]) if seed == primary else \
            (sp["by_test_seed"][str(seed)]["n_calpool"], sp["by_test_seed"][str(seed)]["n_test"])
        dig_ok = split_digest(pos["probe"]) == sp["digest"]["probe"] and all(
            split_digest(pos[k]) == ref[k] for k in ("calpool", "test"))
        sizes_ok = pos["probe"].size == sp["n_probe"] and (pos["calpool"].size, pos["test"].size) == tuple(sz)
        allp = np.concatenate([pos["probe"], pos["calpool"], pos["test"]])
        disjoint = np.unique(allp).size == allp.size == n
        # 2. stratum alignment
        cal, test = pos["calpool"], pos["test"]
        b_np = {nm: np.searchsorted(edges, ref_depth_np(S[ix], lam), side="right") for nm, ix in (("calpool", cal), ("test", test))}
        b_rb = {nm: reference_buckets(S[ix], lam, 5, 1, edges=edges)[0] for nm, ix in (("calpool", cal), ("test", test))}
        align = {nm: bool(np.array_equal(b_np[nm], b_rb[nm])) for nm in b_np}
        for k_, v_ in (("split_digests_match", dig_ok), ("split_sizes_match", sizes_ok),
                       ("probe_calpool_test_disjoint_and_cover", disjoint),
                       ("bucket_ids_numpy_vs_reference_buckets", all(align.values()))):
            all_ok[k_] = bool(all_ok[k_] and v_)
        bc, bt = b_rb["calpool"], b_rb["test"]
        bs["checks"] = {"split_digests_match": bool(dig_ok), "split_sizes_match": bool(sizes_ok),
                        "probe_calpool_test_disjoint_and_cover": bool(disjoint), "bucket_ids": align}
        bs["stratum_sizes"] = {"calpool": {int(k): int((bc == k).sum()) for k in np.unique(bc)},
                               "test": {int(k): int((bt == k).sum()) for k in np.unique(bt)}}
        full_c, full_t = 1.0 - C[cal, T], 1.0 - C[test, T]
        bs["full_acq_stratum_risk"] = {int(k): {"calpool": float(full_c[bc == k].mean()), "test": float(full_t[bt == k].mean())}
                                       for k in np.unique(bt)}
        draws = [r for r in blk["draws"] if int(r.get("split_seed", primary)) == seed]
        bs["n_draws"] = len(draws)
        bs["raw_violation_rate"] = float(np.mean([r["cascade"]["violation"] for r in draws])) if draws else None
        bs["certified_violation_rate"] = (float(np.mean([r["cascade"]["certified_violation"] for r in draws]))
                                          if draws and "certified_violation" in draws[0]["cascade"] else None)
        print(f"[diag] split {seed}: digests={dig_ok} sizes={sizes_ok} disjoint+cover={disjoint} buckets={align} | "
              f"draws {len(draws)} raw viol {bs['raw_violation_rate']} certified {bs['certified_violation_rate']}")

        # 4. deployed rules on this split
        rules = {}
        for r in draws:
            c = r["cascade"]
            if c["tier"] == 0:
                continue
            rules.setdefault((c["tier"], round(float(c["param"]), 12)), []).append((r["draw"], c["violation"]))
        rows = []
        for (tier, param), dl in sorted(rules.items()):
            lc, ac = rule_loss_answered(S[cal], C[cal], tier, param, grid, T)
            lt, at = rule_loss_answered(S[test], C[test], tier, param, grid, T)
            rec = {"tier": tier, "param": param, "n_draws": len(dl), "n_flagged": int(sum(v for _, v in dl)), "strata": {}}
            for k in np.unique(bt):
                mc, mt = (bc == k) & ac, (bt == k) & at
                nc, nt = int(mc.sum()), int(mt.sum())
                rec["strata"][int(k)] = {
                    "n_answered_calpool": nc, "risk_calpool": float(lc[mc].mean()) if nc else None,
                    "n_answered_test": nt, "risk_test": float(lt[mt].mean()) if nt else None,
                    "test_errors": int(round(float(lt[mt].sum()))) if nt else 0,
                    "risk_pooled": float((lc[mc].sum() + lt[mt].sum()) / (nc + nt)) if nc + nt else None}
            rows.append(rec)
            s_ = "; ".join(f"k{k}: cal {v['risk_calpool']:.4f} (n {v['n_answered_calpool']}) test {v['risk_test']:.4f} "
                           f"(n {v['n_answered_test']}) pooled {v['risk_pooled']:.4f}" for k, v in rec["strata"].items()
                           if v["risk_test"] is not None and v["risk_calpool"] is not None)
            print(f"[diag]   tier {tier} param {param:.4f}: deployed in {len(dl)} draws, flagged {rec['n_flagged']} | {s_}")
        bs["deployed_rules"] = rows

        # 3. flagged draws of this split
        checks = []
        for r in draws:
            c = r["cascade"]
            if not c["violation"]:
                continue
            cal_pos = calibration_draw(cal, r["draw"], sp["cal_frac_of_pool"])
            sub_ok = bool(np.isin(cal_pos, cal).all() and not np.isin(cal_pos, test).any())
            idx = np.nonzero(np.isin(cal, cal_pos))[0]
            lcal, acal = rule_loss_answered(S[cal][idx], C[cal][idx], c["tier"], c["param"], grid, T)
            lt, at = rule_loss_answered(S[test], C[test], c["tier"], c["param"], grid, T)
            pv, tp = {}, {}
            for k in c["k_cal"]:
                m = (bc[idx] == k) & acal
                nk = int(m.sum())
                pv[int(k)] = {"n": nk, "risk_cal_draw": float(lcal[m].mean()) if nk else None,
                              "hb_p": float(hoeffding_bentkus_pvalue(float(lcal[m].mean()), nk, alpha)) if nk else 1.0}
                mt = (bt == k) & at
                nt, et = int(mt.sum()), int(round(float(lt[mt].sum())))
                tp[int(k)] = {"n": nt, "errors": et, "binom_p": float(binom_upper_p(et, nt, alpha)) if nt else None}
            pmin = min((v["binom_p"] for v in tp.values() if v["binom_p"] is not None), default=None)
            rec_match = ("test_pvalue_min" not in c) or (
                (pmin is None and c["test_pvalue_min"] is None) or
                (pmin is not None and c["test_pvalue_min"] is not None and abs(pmin - c["test_pvalue_min"]) <= 1e-12))
            checks.append({"draw": r["draw"], "tier": c["tier"], "param": c["param"],
                           "cal_rows_subset_of_calpool_not_test": sub_ok, "per_stratum_cal": pv,
                           "per_stratum_test": tp, "test_pvalue_min_recomputed": pmin,
                           "test_pvalue_min_matches_sweep": bool(rec_match),
                           "test_stratum_risk_sweep": c["test_stratum_risk"]})
            print(f"[diag]   draw {r['draw']}: tier {c['tier']} cal⊂calpool,∉test={sub_ok} test p_min={pmin} "
                  f"(sweep match {rec_match}) | " +
                  "; ".join(f"k{k}: n {v['n']} cal risk {v['risk_cal_draw']:.4f} HB p {v['hb_p']:.4g}" for k, v in pv.items()
                            if v['risk_cal_draw'] is not None))
        bs["flagged_draws"] = checks
        out["by_split"][str(seed)] = bs

    out["checks"] = all_ok
    out["checks"]["all_flagged_cal_rows_ok"] = all(c["cal_rows_subset_of_calpool_not_test"]
                                                    for v in out["by_split"].values() for c in v["flagged_draws"])
    out["checks"]["all_test_pvalues_match_sweep"] = all(c["test_pvalue_min_matches_sweep"]
                                                         for v in out["by_split"].values() for c in v["flagged_draws"])
    print(f"[diag] checks: {out['checks']}")
    if a.output:
        Path(a.output).parent.mkdir(parents=True, exist_ok=True)
        Path(a.output).write_text(json.dumps(out, indent=1))
        print(f"[diag] wrote {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
