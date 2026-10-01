#!/usr/bin/env python
"""v3 -- which calibration draws of a cell change their tier-3 outcome because of the frozen
``ceil(n * r_hat)`` off-by-one (diagnostic for handoff.md section 9; nothing frozen is changed).

For every draw, the committed tier-3 fixed-sequence walk is evaluated twice on the same calibration rows:
(i) with the cascade's own p-values (``cafa.cascade.selective_pvalues``: frozen HB on r_hat = 1 - mean(correct))
and (ii) with Hoeffding-Bentkus p-values computed from the INTEGER error count (the documented formula).
Draws whose certification differs are reported with the (level, stratum, n, errors, p_frozen, p_exact)
that decides the difference.

    python scripts/hb_boundary_draws_v3.py --dataset csv:diabetes --policy random --train-seed 0 --lambda-ref-key 0.9 \
        --output results_v3/diagnostics/csv-diabetes_ts0_random_lr0.9_hb_boundary_draws.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))
from cafa.cascade import selective_pvalues  # noqa: E402
from cafa.metrics import reference_buckets  # noqa: E402
from cafa.pool import load_pool_cache  # noqa: E402
from cafa.splits_v3 import calibration_draw, v3_positions  # noqa: E402
from commit_v3 import dsname_of  # noqa: E402


def hb_exact(k: int, n: int, alpha: float) -> float:
    if n == 0:
        return 1.0
    r = k / n
    if r >= alpha:
        return 1.0
    kl = (r * math.log(r / alpha) if r > 0 else 0.0) + (1 - r) * math.log((1 - r) / (1 - alpha))
    return max(min(1.0, math.exp(-n * kl), math.e * float(binom.cdf(k, n, alpha))), 1e-300)


def walk(p_union, order, level):
    cert = []
    for j in order:
        if p_union[j] <= level:
            cert.append(int(j))
        else:
            break
    return cert


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--policy", default="greedy_entropy")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--lambda-ref-key", default="dep")
    p.add_argument("--n-draws", type=int, default=100)
    p.add_argument("--output", required=True)
    a = p.parse_args(argv)
    dsn, ts = dsname_of(a.dataset), a.train_seed
    com = json.loads((REPO / "configs" / f"committed_v3_{dsn}_ts{ts}.json").read_text())
    c = load_pool_cache(Path(os.environ["RESULTS_ROOT"]) / "pool_v3" / f"{dsn}_ts{ts}_{a.policy}_softmax.npz")
    S, C = np.asarray(c["scores"]), np.asarray(c["correct"])
    T = S.shape[1] - 1
    alpha, sp, d3 = float(com["alpha"]), com["split"], float(com["delta_alloc"][2])
    pos = v3_positions(S.shape[0], sp["probe_frac"], sp["probe_seed"], sp["test_frac_of_eval"], sp["test_seed"])
    cal = pos["calpool"]
    lam = float(com["lambda_refs"][a.policy][a.lambda_ref_key])
    e = np.asarray(com["edges"][a.policy][a.lambda_ref_key]["edges"], float)
    esc = com["escalation"][a.policy][a.lambda_ref_key]
    mu, order = np.asarray(esc["mu_asc"], float), [int(j) for j in esc["order"]]
    b = reference_buckets(S[cal], lam, 5, 1, edges=e)[0]
    diffs, n_frozen, n_exact = [], 0, 0
    for d in range(a.n_draws):
        cp = calibration_draw(cal, d, sp["cal_frac_of_pool"])
        idx = np.nonzero(np.isin(cal, cp))[0]
        sT, cT, bb = S[cal][idx][:, T], C[cal][idx][:, T], b[idx]
        pu_f, pby_f, nby = selective_pvalues(sT, cT, mu, alpha, bb)
        pu_e = np.zeros(mu.size)
        pby_e = {}
        for k in range(int(bb.min()), int(bb.max()) + 1):
            pk = np.ones(mu.size)
            for j in range(mu.size):
                m = (bb == k) & (sT >= mu[j])
                nk = int(m.sum())
                pk[j] = hb_exact(int(np.count_nonzero(cT[m] == 0)), nk, alpha) if nk else 1.0
            pby_e[k] = pk
            pu_e = np.maximum(pu_e, pk)
        cf, ce = walk(pu_f, order, d3), walk(pu_e, order, d3)
        n_frozen += bool(cf)
        n_exact += bool(ce)
        if bool(cf) != bool(ce):
            j = order[len(cf)] if len(cf) < len(ce) else order[len(ce)]
            k = max(pby_f, key=lambda kk: pby_f[kk][j])
            m = (bb == k) & (sT >= mu[j])
            diffs.append({"draw": d, "certified_frozen": bool(cf), "certified_exact_count": bool(ce), "level": int(j),
                          "stratum": int(k), "n_answered": int(m.sum()), "errors": int(np.count_nonzero(cT[m] == 0)),
                          "p_frozen": float(pby_f[k][j]), "p_exact_count": float(pby_e[k][j])})
    out = {"dataset": a.dataset, "policy": a.policy, "train_seed": ts, "lambda_ref_key": a.lambda_ref_key,
           "alpha": alpha, "delta_3": d3, "n_draws": a.n_draws, "tier3_certified_frozen": n_frozen,
           "tier3_certified_exact_count": n_exact, "differing_draws": diffs}
    Path(a.output).write_text(json.dumps(out, indent=1))
    print(f"[hb_boundary] {dsn} ts{ts} {a.policy} lr[{a.lambda_ref_key}]: tier 3 certifies in {n_frozen} draws with the "
          f"frozen p-values, {n_exact} with exact-count p-values; differing draws: "
          + "; ".join(f"d{x['draw']} level {x['level']} k{x['stratum']} n={x['n_answered']} err={x['errors']} "
                      f"p {x['p_frozen']:.4f} vs {x['p_exact_count']:.4f}" for x in diffs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
