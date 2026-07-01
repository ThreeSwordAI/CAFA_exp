"""Step 4 in-chat gate -- H2 safety, baseline sanity, and the tabular pipeline.

No cluster, no download, fast.  Three parts:

1. **H2 safety (synthetic, ground-truthed).**  Over many resplits with a *known*
   true-risk curve, the certified CAFA-marginal selector
   (:func:`cafa.risk_control.ltt_select`) keeps the true-risk violation rate
   ``<= delta + slack``, while the uncorrected plugin heuristic
   (:func:`cafa.baselines.plugin_threshold_select`) violates ``alpha`` on a large
   fraction of resplits.  This proves the *safety half* of H2 rigorously and
   independently of any dataset.
2. **Baseline sanity.**  The oracle/CAFA/full-feature cost ordering tripwire;
   ``fixed_confidence_select`` returns the nearest grid index; ``budget`` /
   ``realized_at_depth`` evaluate at the requested depth.
3. **Tabular pipeline smoke.**  A tiny in-code synthetic tabular set + a numpy
   dummy predictor flow through :func:`cafa.tabular.tabular_rollout` ->
   ``stops_from_grid_np`` -> ``ltt_select`` + ``mondrian_select`` + every
   baseline, with the trajectory conventions asserted.

Does not import or modify the frozen gates.

    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    pytest -q tests/test_baselines.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cafa.baselines import (  # noqa: E402
    budget_select,
    fixed_confidence_select,
    oracle_cheapest_valid_select,
    oracle_full_feature_risk,
    plugin_threshold_select,
    realized_at_depth,
)
from cafa.data import make_synthetic_afa, make_synthetic_tabular_afa  # noqa: E402
from cafa.metrics import reference_buckets, stops_from_grid_np  # noqa: E402
from cafa.risk_control import ltt_select, mondrian_select  # noqa: E402
from cafa.tabular import tabular_rollout  # noqa: E402

ALPHA = 0.10
DELTA = 0.10
SLACK = 0.05
GRID = np.linspace(0.0, 1.0, 100)


# --------------------------------------------------------------------------- #
# 1. H2 safety (synthetic, ground-truthed)
# --------------------------------------------------------------------------- #
def test_h2_safety_cafa_controls_plugin_overshoots():
    """CAFA-marginal true-risk violation <= delta+slack; plugin overshoots alpha."""
    n_trials, n = 300, 500
    cafa_viol = plugin_viol = 0
    for t in range(n_trials):
        losses, costs, r_curve = make_synthetic_afa(
            n, GRID, true_risk="monotone", alpha=ALPHA, seed=t, coupling=True
        )
        cafa_idx = ltt_select(losses, costs, GRID, ALPHA, DELTA).lambda_idx
        plug_idx = plugin_threshold_select(losses, costs, GRID, ALPHA)
        # True risk at the selected threshold (exact; None -> non-violating).
        if cafa_idx is not None and r_curve[cafa_idx] > ALPHA:
            cafa_viol += 1
        if plug_idx is not None and r_curve[plug_idx] > ALPHA:
            plugin_viol += 1

    cafa_rate = cafa_viol / n_trials
    plugin_rate = plugin_viol / n_trials

    assert cafa_rate <= DELTA + SLACK, (
        f"CAFA-marginal violation {cafa_rate:.3f} exceeds delta+slack "
        f"({DELTA + SLACK}) -- the guarantee failed"
    )
    assert plugin_rate >= 0.30, (
        f"plugin violation {plugin_rate:.3f} too low -- the uncorrected overshoot "
        "did not manifest, so the H2 contrast is not demonstrated"
    )
    assert plugin_rate - cafa_rate >= 0.20, (
        f"plugin-CAFA gap {plugin_rate - cafa_rate:.3f} < 0.20 -- safety half of "
        "H2 not decisive"
    )


# --------------------------------------------------------------------------- #
# 2. Baseline sanity
# --------------------------------------------------------------------------- #
def test_oracle_cafa_full_cost_ordering():
    """oracle_cheapest_valid cost <= CAFA-marginal cost <= full-feature cost."""
    cal_losses, cal_costs, _ = make_synthetic_afa(
        4000, GRID, true_risk="monotone", alpha=ALPHA, seed=1, coupling=True
    )
    test_losses, test_costs, _ = make_synthetic_afa(
        4000, GRID, true_risk="monotone", alpha=ALPHA, seed=2, coupling=True
    )
    marg = ltt_select(cal_losses, cal_costs, GRID, ALPHA, DELTA)
    assert marg.lambda_idx is not None, "CAFA should certify a threshold here"
    oracle_idx = oracle_cheapest_valid_select(test_losses, test_costs, GRID, ALPHA)
    assert oracle_idx is not None, "oracle should find a test-valid threshold here"

    oracle_cost = test_costs[:, oracle_idx].mean()
    cafa_cost = test_costs[:, marg.lambda_idx].mean()
    full_cost = test_costs[:, -1].mean()
    assert oracle_cost <= cafa_cost + 1e-9, (oracle_cost, cafa_cost)
    assert cafa_cost <= full_cost + 1e-9, (cafa_cost, full_cost)


def test_fixed_confidence_returns_nearest_grid_index():
    for t in (0.90, 0.95, 0.99, 0.5):
        idx = fixed_confidence_select(GRID, t)
        assert idx == int(np.argmin(np.abs(GRID - t)))
        assert 0 <= idx < GRID.size


def test_budget_evaluates_at_requested_depth():
    # Deterministic tiny trajectory: correct flips on at depth 2, cost = depth.
    correct = np.array([[0.0, 0.0, 1.0, 1.0, 1.0],
                        [0.0, 1.0, 1.0, 1.0, 1.0]])
    cum_cost = np.tile(np.arange(5, dtype=float), (2, 1))
    T = correct.shape[1] - 1

    assert budget_select(2, T=T) == 2
    assert budget_select(99, T=T) == T          # clamp to T
    assert budget_select(-3, T=T) == 0          # clamp to 0

    risk, cost = realized_at_depth(correct, cum_cost, 2)
    assert np.isclose(risk, np.mean(1.0 - correct[:, 2]))   # (0 + 0)/2 = 0.0
    assert np.isclose(cost, 2.0)
    risk1, cost1 = realized_at_depth(correct, cum_cost, 1)
    assert np.isclose(risk1, 0.5) and np.isclose(cost1, 1.0)


def test_oracle_full_feature_risk_accepts_vector_and_matrix():
    losses_vec = np.array([0.0, 1.0, 0.0, 0.0])          # 1 wrong of 4
    assert np.isclose(oracle_full_feature_risk(losses_vec), 0.25)
    mat = np.zeros((10, 3))
    mat[:2, -1] = 1.0                                    # 2 wrong at full acq
    assert np.isclose(oracle_full_feature_risk(mat), 0.2)


# --------------------------------------------------------------------------- #
# 3. Tabular pipeline smoke (numpy dummy predictor; no torch, no download)
# --------------------------------------------------------------------------- #
class _DummyTabularPredictor:
    """Readiness rises with the observed-column fraction; label-independent.

    Mirrors the ``predict_proba(X, mask, device) -> [B, C]`` surface the tabular
    rollout / policy use, so the whole pipeline runs without torch.
    """

    def __init__(self, n_classes: int = 2):
        self.n_classes = int(n_classes)

    def predict_proba(self, X, mask, device=None):
        mask = np.asarray(mask, dtype=float)
        frac = mask.mean(axis=1, keepdims=True)          # [B, 1] in [0, 1]
        logits = np.zeros((mask.shape[0], self.n_classes))
        logits[:, 0] = 4.0 * frac.squeeze(1)             # sharpen class 0 with info
        z = np.exp(logits - logits.max(axis=1, keepdims=True))
        return z / z.sum(axis=1, keepdims=True)


def test_tabular_pipeline_end_to_end():
    ds = make_synthetic_tabular_afa(n=400, d=8, n_classes=2, n_informative=3, seed=0)
    X, y = ds["X"], ds["y"]
    d = X.shape[1]
    feature_costs = np.arange(1, d + 1, dtype=float)     # heterogeneous costs
    pred = _DummyTabularPredictor(n_classes=2)

    traj = tabular_rollout(pred, "greedy", "softmax", X, y, feature_costs,
                           feature_groups=None, device="cpu")

    n = X.shape[0]
    assert traj.scores.shape == (n, d + 1)
    assert traj.correct.shape == (n, d + 1)
    assert traj.cum_cost.shape == (n, d + 1)
    assert np.all(traj.scores >= 0.0) and np.all(traj.scores <= 1.0)
    assert set(np.unique(traj.correct)).issubset({0.0, 1.0})
    assert np.allclose(traj.cum_cost[:, 0], 0.0)                    # start at 0
    assert np.all(np.diff(traj.cum_cost, axis=1) >= -1e-9)          # non-decreasing
    assert np.allclose(traj.cum_cost[:, -1], feature_costs.sum())   # ends at full cost

    grid = np.linspace(0.0, 1.0, 20)
    losses, costs, stop_depth = stops_from_grid_np(
        traj.scores, traj.correct, traj.cum_cost, grid
    )
    assert losses.shape == costs.shape == (n, grid.size)
    assert set(np.unique(losses)).issubset({0.0, 1.0})
    assert np.all(stop_depth >= 0) and np.all(stop_depth <= d)

    # Frozen selectors + baselines all consume the tabular arrays unchanged.
    bid, edges = reference_buckets(traj.scores, lambda_ref=0.5, n_buckets=3,
                                   min_per_bucket=10)
    marg = ltt_select(losses, costs, grid, ALPHA, DELTA)
    mond = mondrian_select(losses, costs, grid, ALPHA, DELTA, bid)
    plug = plugin_threshold_select(losses, costs, grid, ALPHA)
    fixed = fixed_confidence_select(grid, 0.95)
    br, bc = realized_at_depth(traj.correct, traj.cum_cost, budget_select(4, T=d))

    assert marg.r_hat.shape == (grid.size,)
    assert set(mond.lambda_idx_by_bucket).issubset(set(int(k) for k in np.unique(bid)))
    assert plug is None or 0 <= plug < grid.size
    assert 0 <= fixed < grid.size
    assert 0.0 <= br <= 1.0 and bc >= 0.0