#!/usr/bin/env python
"""v3 -- why did tier 3 refuse?  Replays the committed escalation walk for cells with ``none > 0.05``.

Instruction 4.4 / PHASES 3c: for a cell whose cascade returns no certificate in more than 5 % of draws,
read the escalation block of the committed JSON (``fractions_desc``, ``mu_asc``, ``order``) and the
per-stratum answered counts.  For the first ``--n-draws`` calibration draws this script recomputes,
independently of cafa.cascade, the tier-3 fixed-sequence walk over the committed probe order at level
delta_3: for each level, the answered calibration rows per stratum (s(x) = k and g_T(x) >= mu), their
selective risk, the frozen Hoeffding-Bentkus p-value against alpha, the union p (max over the
represented strata), and where the walk stops.  It also prints the probe-time answered fraction of
each tested level.

    python scripts/diagnose_refusal_v3.py --dataset csv:diabetes --policy greedy_entropy --train-seed 0 --lambda-ref-key 0.9
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
from cafa.splits_v3 import calibration_draw, v3_positions  # noqa: E402
from commit_v3 import dsname_of  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--policy", default="greedy_entropy")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--lambda-ref-key", default="dep")
    p.add_argument("--n-draws", type=int, default=100)
    p.add_argument("--show-levels", type=int, default=4)
    p.add_argument("--output", default=None)
    a = p.parse_args(argv)
    dsn, ts = dsname_of(a.dataset), a.train_seed
    com = json.loads((REPO / "configs" / f"committed_v3_{dsn}_ts{ts}.json").read_text())
    cache = load_pool_cache(Path(os.environ["RESULTS_ROOT"]) / "pool_v3" / f"{dsn}_ts{ts}_{a.policy}_softmax.npz")
    S, C = np.asarray(cache["scores"]), np.asarray(cache["correct"])
    n, T = S.shape[0], S.shape[1] - 1
    alpha, sp = float(com["alpha"]), com["split"]
    d3 = float(com["delta_alloc"][2])  # committed (delta_1, delta_2, delta_3)
    lam = float(com["lambda_refs"][a.policy][a.lambda_ref_key])
    edges = np.asarray(com["edges"][a.policy][a.lambda_ref_key]["edges"], float)
    esc = com["escalation"][a.policy][a.lambda_ref_key]
    mu, fr, order = np.asarray(esc["mu_asc"], float), np.asarray(esc["fractions_desc"], float), list(esc["order"])
    pos = v3_positions(n, sp["probe_frac"], sp["probe_seed"], sp["test_frac_of_eval"], sp["test_seed"])
    cal = pos["calpool"]
    b_pool = reference_buckets(S[cal], lam, 5, 1, edges=edges)[0]
    b_probe = reference_buckets(S[pos["probe"]], lam, 5, 1, edges=edges)[0]
    print(f"[refusal] {dsn} ts{ts} {a.policy} lr[{a.lambda_ref_key}]={lam:.4f} G={edges.size + 1} alpha={alpha} delta_3={d3} "
          f"levels={len(mu)}; first {a.show_levels} levels of the committed order (index: probe answered fraction):",
          ", ".join(f"{j}: {fr[j]:.3f}" for j in order[: a.show_levels]))
    stops, recs = {}, []
    for d in range(a.n_draws):
        cp = calibration_draw(cal, d, sp["cal_frac_of_pool"])
        idx = np.nonzero(np.isin(cal, cp))[0]
        Sc, Cc, bc = S[cal][idx], C[cal][idx], b_pool[idx]
        kcal = sorted(int(k) for k in np.unique(bc))
        walk, certified = [], []
        for j in order:
            ans = Sc[:, T] >= mu[j]
            per = {}
            for k in kcal:
                m = (bc == k) & ans
                nk = int(m.sum())
                r = float((1.0 - Cc[m, T]).mean()) if nk else None
                per[k] = {"n_answered": nk, "n_stratum": int((bc == k).sum()),
                          "sel_risk": r, "p": float(hoeffding_bentkus_pvalue(r, nk, alpha)) if nk else 1.0}
            pu = max(v["p"] for v in per.values())
            walk.append({"level": int(j), "mu": float(mu[j]), "probe_answered_fraction": float(fr[j]), "union_p": pu, "strata": per})
            if pu <= d3:
                certified.append(int(j))
            else:
                break
        stop_level = walk[-1]["level"] if not certified or walk[-1]["union_p"] > d3 else None
        stops[stop_level] = stops.get(stop_level, 0) + 1
        recs.append({"draw": d, "n_certified": len(certified), "walk": walk})
        if d < 3:
            w = walk[-1]
            worst = max(w["strata"].items(), key=lambda kv: kv[1]["p"])
            print(f"[refusal] draw {d}: certified {len(certified)} level(s); stopped at level {w['level']} "
                  f"(probe answered {w['probe_answered_fraction']:.3f}, mu {w['mu']:.4f}, union p {w['union_p']:.4g} > {d3}): "
                  + "; ".join(f"k{k}: answered {v['n_answered']}/{v['n_stratum']} sel risk "
                              f"{'-' if v['sel_risk'] is None else f'{v['sel_risk']:.4f}'} p {v['p']:.4g}"
                              for k, v in w["strata"].items()) + f"  [binding stratum k{worst[0]}]")
    n_refused = sum(1 for r in recs if r["n_certified"] == 0)
    print(f"[refusal] tier 3 certified no level in {n_refused}/{a.n_draws} draws; probe stratum sizes "
          f"{ {int(k): int((b_probe == k).sum()) for k in np.unique(b_probe)} }")
    if a.output:
        Path(a.output).write_text(json.dumps({"dataset": a.dataset, "policy": a.policy, "train_seed": ts,
                                              "lambda_ref_key": a.lambda_ref_key, "lambda_ref": lam, "alpha": alpha,
                                              "delta_3": d3, "edges": edges.tolist(), "n_draws": a.n_draws,
                                              "n_draws_tier3_refused": n_refused, "draws": recs}, indent=1))
        print(f"[refusal] wrote {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
