"""G3 gate -- per-bucket ("Mondrian") risk control on synthetic AFA data.

The synthetic generator (:func:`cafa.data.make_synthetic_mondrian`) builds a
population whose *true* accuracy is depressed, near the start of acquisition, by
a bucket-correlated amount ``gamma``.  With ``gamma = 0`` it is perfectly
calibrated; as ``gamma`` grows the fastest-rising ("cheap") instances become the
most over-confident, so a single *marginal* Learn-then-Test threshold
under-covers them while *over*-covering the slow/expensive strata.  Per-bucket
(Mondrian) selection -- the frozen :func:`cafa.risk_control.ltt_select` run
independently inside each reference-depth bucket -- restores per-budget control.

Because the construction exposes the true accuracy, the *true* per-bucket risk at
any threshold is computed exactly, so violations are read off ground truth with
no held-out estimation noise.

What this gate asserts
----------------------
#1  gamma = 0 sanity: both methods keep *every* populated bucket within
    ``delta + SLACK`` (no gross miscalibration, no false alarm).
#2  gamma = GAMMA_GATE: Mondrian controls *every* populated bucket within
    ``delta + SLACK``.
#3  gamma = GAMMA_GATE: the marginal threshold violates the cheap bucket on a
    large fraction of resplits (>= 0.5), while Mondrian keeps it controlled --
    the discriminating contrast.
#4  determinism: identical seeds reproduce identical violation rates.
Plus an agreement check that the torch-free :func:`cafa.metrics.stops_from_grid_np`
matches torch ``cafa.acquisition.stops_from_grid`` exactly.

Operating point.  The marginal selector retreats to *full acquisition*
(``lambda = 1.0`` -- the top of the grid, where every instance is forced to the
calibrated final depth) once ``gamma`` exceeds ~0.14: scores asymptote to 1 and
never cross 1.0, so the whole population is driven to depth ``T`` where the model
is calibrated, trivially "controlling" risk by acquiring everything (the
degeneracy Step 2 already flagged on MNIST).  That masks the per-budget failure.
We therefore gate at ``GAMMA_GATE = 0.12`` -- inside the genuine early-stopping
regime, below the escape boundary -- where the phenomenon is decisive
(marginal cheap-bucket violation ~0.97, Mondrian ~0.02).
"""

from __future__ import annotations

import numpy as np
import pytest

from cafa.data import make_synthetic_mondrian
from cafa.metrics import (
    per_bucket_risk,
    quantile_bucket_edges,
    reference_buckets,
    stops_from_grid_np,
)
from cafa.risk_control import ltt_select, mondrian_select

# --- fixed experimental constants -------------------------------------------
T = 49
ALPHA = 0.10
DELTA = 0.10
LAMBDA_REF = 0.5
N_BUCKETS = 5
MIN_PER_BUCKET = 50
GRID = np.linspace(0.0, 1.0, 100)        # config grid: ascending [0, 1], n = 100
GAMMA_GATE = 0.12                        # below the full-acquisition escape (~0.14)
N_CAL = 6000
N_TEST = 6000
N_TRIALS = 300
SLACK = 0.05                             # small finite-sample / boundary slack
POOL_N = 20000
POOL_SEED = 777

# Bucket edges are estimated ONCE on a separate pool and reused on every cal/test
# split (never re-estimated on the calibration set used for selection).  The
# scores -- hence reference depths and edges -- do not depend on gamma, so a
# single pool fixes the partition for all gamma values below.
_POOL = make_synthetic_mondrian(
    n=POOL_N, T=T, gamma=0.0, lambda_ref=LAMBDA_REF,
    n_buckets=N_BUCKETS, min_per_bucket=MIN_PER_BUCKET, seed=POOL_SEED,
)
EDGES = quantile_bucket_edges(_POOL["scores"], LAMBDA_REF, N_BUCKETS)
_POOL_BID, _ = reference_buckets(
    _POOL["scores"], LAMBDA_REF, N_BUCKETS, MIN_PER_BUCKET, edges=EDGES
)
CHEAP_LABEL = int(np.unique(_POOL_BID).min())   # lowest reference depth = cheapest


def _violation_rate(values) -> float:
    """Fraction of trials whose true bucket risk exceeds ALPHA.

    ``nan`` (empty / abstaining bucket -> fall back to full acquisition) counts
    as non-violating since ``nan > ALPHA`` is ``False``.
    """
    return float(np.mean(np.asarray(values, dtype=float) > ALPHA))


def _run_trials(gamma: float, n_trials: int, cal_seed0: int, test_seed0: int) -> dict:
    """Resplit experiment at a given ``gamma``.

    For each trial: draw a fresh calibration and test split, bucket both with the
    fixed pool ``EDGES``, select a single marginal threshold and a per-bucket
    Mondrian threshold on calibration, then evaluate the *true* per-bucket risk
    on test.  Returns per-bucket violation rates and the cheap-bucket arrays for
    both methods.
    """
    marg_cheap, mond_cheap = [], []
    marg_by_bucket: dict = {}
    mond_by_bucket: dict = {}
    for tr in range(n_trials):
        cal = make_synthetic_mondrian(
            n=N_CAL, T=T, gamma=gamma, lambda_ref=LAMBDA_REF,
            n_buckets=N_BUCKETS, min_per_bucket=MIN_PER_BUCKET, seed=cal_seed0 + tr,
        )
        tst = make_synthetic_mondrian(
            n=N_TEST, T=T, gamma=gamma, lambda_ref=LAMBDA_REF,
            n_buckets=N_BUCKETS, min_per_bucket=MIN_PER_BUCKET, seed=test_seed0 + tr,
        )
        cal_bid, _ = reference_buckets(cal["scores"], LAMBDA_REF, N_BUCKETS,
                                       MIN_PER_BUCKET, edges=EDGES)
        tst_bid, _ = reference_buckets(tst["scores"], LAMBDA_REF, N_BUCKETS,
                                       MIN_PER_BUCKET, edges=EDGES)

        # Calibrate on the OBSERVED (correct) labels.
        cal_losses, cal_costs, _ = stops_from_grid_np(
            cal["scores"], cal["correct"], cal["cum_cost"], GRID
        )
        marg = ltt_select(cal_losses, cal_costs, GRID, ALPHA, DELTA)
        mond = mondrian_select(cal_losses, cal_costs, GRID, ALPHA, DELTA, cal_bid)

        # Evaluate the TRUE risk on test: pass true_acc as the "correct" channel
        # so losses[i, j] = 1 - true_acc[i, stop_depth(i, j)].
        true_losses, _, _ = stops_from_grid_np(
            tst["scores"], tst["true_acc"], tst["cum_cost"], GRID
        )
        labels = np.unique(tst_bid)
        marg_risk = per_bucket_risk(
            true_losses, tst_bid, {int(k): marg.lambda_idx for k in labels}
        )
        mond_risk = per_bucket_risk(true_losses, tst_bid, mond.lambda_idx_by_bucket)

        marg_cheap.append(marg_risk[CHEAP_LABEL])
        mond_cheap.append(mond_risk[CHEAP_LABEL])
        for k in labels:
            marg_by_bucket.setdefault(int(k), []).append(marg_risk[int(k)])
            mond_by_bucket.setdefault(int(k), []).append(mond_risk[int(k)])

    return {
        "marg_cheap_viol": _violation_rate(marg_cheap),
        "mond_cheap_viol": _violation_rate(mond_cheap),
        "marg_bucket_viol": {k: _violation_rate(v) for k, v in marg_by_bucket.items()},
        "mond_bucket_viol": {k: _violation_rate(v) for k, v in mond_by_bucket.items()},
    }


@pytest.fixture(scope="module")
def gate_results() -> dict:
    """Resplit experiment at GAMMA_GATE (shared by the gate assertions)."""
    return _run_trials(GAMMA_GATE, N_TRIALS, cal_seed0=1000, test_seed0=5000)


@pytest.fixture(scope="module")
def sanity_results() -> dict:
    """Resplit experiment at gamma = 0 (calibrated sanity)."""
    return _run_trials(0.0, N_TRIALS, cal_seed0=20000, test_seed0=40000)


def test_cheap_bucket_is_populated_minority():
    """The cheap bucket exists, is the lowest-depth stratum, and is a minority."""
    labels, counts = np.unique(_POOL_BID, return_counts=True)
    assert CHEAP_LABEL in labels
    cheap_frac = counts[labels == CHEAP_LABEL][0] / counts.sum()
    assert 0.0 < cheap_frac < 0.5, f"cheap fraction {cheap_frac:.3f} not a minority"
    assert len(labels) >= 3, "need several populated buckets for a meaningful gate"


def test_gamma0_sanity_both_methods_control_all_buckets(sanity_results):
    """#1  At gamma = 0 both methods keep every populated bucket <= delta + slack."""
    marg = sanity_results["marg_bucket_viol"]
    mond = sanity_results["mond_bucket_viol"]
    assert max(marg.values()) <= DELTA + SLACK, f"marginal buckets at gamma=0: {marg}"
    assert max(mond.values()) <= DELTA + SLACK, f"Mondrian buckets at gamma=0: {mond}"
    # And specifically no false alarm on the cheap bucket.
    assert sanity_results["marg_cheap_viol"] <= DELTA + SLACK
    assert sanity_results["mond_cheap_viol"] <= DELTA + SLACK


def test_mondrian_controls_every_bucket_at_gate(gate_results):
    """#2  At GAMMA_GATE Mondrian controls every populated bucket <= delta + slack."""
    mond = gate_results["mond_bucket_viol"]
    assert max(mond.values()) <= DELTA + SLACK, f"Mondrian buckets at gate: {mond}"


def test_marginal_undercovers_cheap_bucket_while_mondrian_fixes_it(gate_results):
    """#3  The discriminating contrast at GAMMA_GATE.

    The marginal threshold violates the cheap bucket on a large fraction of
    resplits; Mondrian keeps the same bucket controlled.
    """
    marg_cheap = gate_results["marg_cheap_viol"]
    mond_cheap = gate_results["mond_cheap_viol"]
    assert marg_cheap >= 0.5, (
        f"marginal cheap-bucket violation {marg_cheap:.3f} too low -- "
        "the phenomenon did not manifest"
    )
    assert mond_cheap <= DELTA + SLACK, (
        f"Mondrian cheap-bucket violation {mond_cheap:.3f} exceeds delta + slack"
    )
    # The whole point: Mondrian is dramatically better on the cheap bucket.
    assert marg_cheap - mond_cheap >= 0.3


def test_determinism_same_seeds_reproduce():
    """#4  Identical seeds reproduce identical violation rates exactly."""
    a = _run_trials(GAMMA_GATE, 40, cal_seed0=1000, test_seed0=5000)
    b = _run_trials(GAMMA_GATE, 40, cal_seed0=1000, test_seed0=5000)
    assert a["marg_cheap_viol"] == b["marg_cheap_viol"]
    assert a["mond_cheap_viol"] == b["mond_cheap_viol"]
    assert a["marg_bucket_viol"] == b["marg_bucket_viol"]


def test_stops_from_grid_np_matches_torch():
    """The numpy stop-mapping mirrors torch ``stops_from_grid`` byte-for-byte."""
    pytest.importorskip("torch")
    from cafa.acquisition import Trajectories, stops_from_grid

    # Frozen hand-checked tiny case.
    scores = np.array([[0.1, 0.3, 0.5, 0.8, 0.8]])
    correct = np.array([[0, 0, 1, 1, 1]])
    cum_cost = np.array([[0, 1, 2, 3, 4]])
    grid = np.array([0.05, 0.3, 0.55, 0.99])
    tl, tc, ts = stops_from_grid(
        Trajectories(scores=scores, correct=correct, cum_cost=cum_cost), grid
    )
    nl, nc, ns = stops_from_grid_np(scores, correct, cum_cost, grid)
    assert np.array_equal(tl, nl) and np.array_equal(tc, nc) and np.array_equal(ts, ns)
    assert ts.astype(int).tolist() == [[0, 1, 3, 4]]   # documented expectation

    # Random larger case (non-monotone scores, full grid).
    rng = np.random.default_rng(7)
    n, Tp1 = 400, 50
    sc = rng.uniform(0.0, 1.0, size=(n, Tp1))
    co = rng.binomial(1, 0.7, size=(n, Tp1)).astype(float)
    cc = np.tile(np.arange(Tp1, dtype=float), (n, 1))
    gr = np.linspace(0.0, 1.0, 100)
    tl, tc, ts = stops_from_grid(
        Trajectories(scores=sc, correct=co, cum_cost=cc), gr
    )
    nl, nc, ns = stops_from_grid_np(sc, co, cc, gr)
    assert np.array_equal(tl, nl) and np.array_equal(tc, nc) and np.array_equal(ts, ns)