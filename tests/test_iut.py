"""WO-14.4 -- CAFA-IUT: union-null validity (Monte-Carlo) + empty-stratum blocking.

The union-null Monte-Carlo mirrors the G3 (Mondrian) gate's construction on
:func:`cafa.data.make_synthetic_mondrian`, whose known true accuracy lets the
*true* per-stratum risk at the deployed lambda be read off ground truth.  Bucket
edges are pre-committed from an independent probe draw (seed offset 10_000) and
reused on every cal/test split -- never re-estimated on the calibration set.

Targeted runtime < 90 s CPU.
"""

from __future__ import annotations

import numpy as np

from cafa.data import make_synthetic_mondrian
from cafa.metrics import per_bucket_risk, quantile_bucket_edges, reference_buckets, stops_from_grid_np
from cafa.risk_control_ext import iut_select

T = 49
ALPHA = 0.10
DELTA = 0.10
LAMBDA_REF = 0.5
N_BUCKETS = 5
MIN_PER_BUCKET = 50
GRID = np.linspace(0.0, 1.0, 100)
N = 2000
N_DRAWS = 150
SLACK = 0.05

# Pre-committed edges from an INDEPENDENT probe draw (seed offset 10_000).
_PROBE = make_synthetic_mondrian(
    n=20000, T=T, gamma=0.0, lambda_ref=LAMBDA_REF,
    n_buckets=N_BUCKETS, min_per_bucket=MIN_PER_BUCKET, seed=10_000,
)
EDGES = quantile_bucket_edges(_PROBE["scores"], LAMBDA_REF, N_BUCKETS)


def _mc(gamma: float):
    viol = 0
    certified = 0
    for draw in range(N_DRAWS):
        cal = make_synthetic_mondrian(n=N, T=T, gamma=gamma, lambda_ref=LAMBDA_REF,
                                      n_buckets=N_BUCKETS, min_per_bucket=MIN_PER_BUCKET,
                                      seed=1000 + draw)
        tst = make_synthetic_mondrian(n=N, T=T, gamma=gamma, lambda_ref=LAMBDA_REF,
                                      n_buckets=N_BUCKETS, min_per_bucket=MIN_PER_BUCKET,
                                      seed=5000 + draw)
        cal_bid, _ = reference_buckets(cal["scores"], LAMBDA_REF, N_BUCKETS, MIN_PER_BUCKET, edges=EDGES)
        tst_bid, _ = reference_buckets(tst["scores"], LAMBDA_REF, N_BUCKETS, MIN_PER_BUCKET, edges=EDGES)
        cal_losses, cal_costs, _ = stops_from_grid_np(cal["scores"], cal["correct"], cal["cum_cost"], GRID)
        res = iut_select(cal_losses, cal_costs, GRID, ALPHA, DELTA, cal_bid)
        if res.lambda_idx is None:
            continue  # global abstention makes no claim (no certified lambda)
        certified += 1
        true_losses, _, _ = stops_from_grid_np(tst["scores"], tst["true_acc"], tst["cum_cost"], GRID)
        pbr = per_bucket_risk(true_losses, tst_bid, {int(k): res.lambda_idx for k in np.unique(tst_bid)})
        if any((v > ALPHA) for v in pbr.values() if not np.isnan(v)):
            viol += 1
    return viol / N_DRAWS, certified / N_DRAWS


def test_union_null_validity_gamma0():
    viol_rate, _ = _mc(0.0)
    assert viol_rate <= DELTA + SLACK, f"any-stratum violation {viol_rate:.3f} at gamma=0"


def test_union_null_validity_and_certification_gamma012():
    viol_rate, cert_rate = _mc(0.12)
    assert viol_rate <= DELTA + SLACK, f"any-stratum violation {viol_rate:.3f} at gamma=0.12"
    assert cert_rate >= 0.80, f"certification occurred in only {cert_rate:.3f} of draws"


def test_empty_stratum_blocks_certification():
    # Zero losses would certify everything; an interior empty stratum (label 1)
    # forces p == 1 there and blocks the whole grid.
    n, G = 200, GRID.size
    losses = np.zeros((n, G))
    costs = np.tile(GRID[None, :], (n, 1))
    bucket_id = np.array([0] * 100 + [2] * 100)   # label 1 absent -> empty interior stratum
    res = iut_select(losses, costs, GRID, ALPHA, DELTA, bucket_id)
    assert res.lambda_idx is None
    assert res.stratum_sizes.get(1, None) == 0
    assert np.allclose(res.per_stratum_pvalues[1], 1.0)

    # Sanity: without the gap (contiguous populated strata) it DOES certify.
    bucket_ok = np.array([0] * 100 + [1] * 100)
    res_ok = iut_select(losses, costs, GRID, ALPHA, DELTA, bucket_ok)
    assert res_ok.lambda_idx is not None
