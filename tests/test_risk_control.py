"""G1 -- the synthetic validity gate for the CAFA risk-control core.

Passing means the distribution-free guarantee is correctly implemented: across
many synthetic calibration draws with a *known* true risk curve, the fraction
of draws whose selected threshold's true risk exceeds ``alpha`` is <= ``delta``
(up to Monte-Carlo slack); the cost-minimizing selection returns the cheapest
risk-valid threshold; and both FWER procedures control risk on monotone and
non-monotone risk curves.

Run from the repo root:

    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    pytest -q
"""

from __future__ import annotations

import os
import sys

import numpy as np

# Make the package importable even if PYTHONPATH was not set (no extra files).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cafa.data import make_synthetic_afa  # noqa: E402
from cafa.metrics import none_rate, violation_rate  # noqa: E402
from cafa.risk_control import hoeffding_bentkus_pvalue, ltt_select  # noqa: E402

MC_SLACK = 0.03  # Monte-Carlo slack on top of delta


def test_pvalue_sanity():
    """p is non-increasing as r_hat decreases below alpha, and is 1.0 at/above alpha."""
    n, alpha = 500, 0.1

    # At or above alpha -> exactly 1.0 (no certification).
    assert hoeffding_bentkus_pvalue(alpha, n, alpha) == 1.0
    assert hoeffding_bentkus_pvalue(0.20, n, alpha) == 1.0
    assert hoeffding_bentkus_pvalue(0.50, n, alpha) == 1.0

    # Decreasing r_hat (below alpha) -> non-increasing p, all in (0, 1].
    r_values = [0.099, 0.09, 0.07, 0.05, 0.03, 0.01, 0.0]
    p_values = [hoeffding_bentkus_pvalue(r, n, alpha) for r in r_values]
    for p in p_values:
        assert 0.0 < p <= 1.0
    for p_hi, p_lo in zip(p_values, p_values[1:]):
        assert p_lo <= p_hi + 1e-12  # monotone non-increasing

    # More calibration data at fixed r_hat -> stronger evidence -> smaller p.
    assert hoeffding_bentkus_pvalue(0.05, 2000, alpha) <= hoeffding_bentkus_pvalue(0.05, 200, alpha)


def test_marginal_validity_monotone():
    """>= 1000 fresh n=500 monotone draws: empirical violation rate <= delta (+ slack)."""
    T, n, alpha, delta = 1000, 500, 0.10, 0.10
    grid = np.linspace(0.0, 1.0, 50)

    true_risk_at_selected = np.zeros(T)  # None selections -> 0.0 (non-violating sentinel)
    selected_indices = []
    for t in range(T):
        losses, costs, r_curve = make_synthetic_afa(
            n, grid, true_risk="monotone", alpha=alpha, seed=t, coupling=True
        )
        res = ltt_select(losses, costs, grid, alpha=alpha, delta=delta, procedure="fixed_sequence")
        selected_indices.append(res.lambda_idx)
        if res.lambda_idx is not None:
            true_risk_at_selected[t] = r_curve[res.lambda_idx]

    v_rate = violation_rate(true_risk_at_selected, alpha)
    n_rate = none_rate(selected_indices)

    assert v_rate <= delta + MC_SLACK, f"violation_rate={v_rate:.3f}, none_rate={n_rate:.3f}"
    assert n_rate < 0.1, f"none_rate={n_rate:.3f} (power sanity), violation_rate={v_rate:.3f}"


def test_cost_min_picks_cheapest_valid():
    """Deterministic case: lambda_star is the cheapest index where valid_mask is True."""
    n = 1000
    grid = np.array([0.0, 0.25, 0.50, 0.75])
    alpha, delta = 0.10, 0.10

    # Craft empirical risks: col0 ~0.30 (invalid), col1 ~0.02, col2 = col3 = 0 (valid).
    losses = np.zeros((n, 4))
    losses[:300, 0] = 1.0   # r_hat[0] = 0.30 >= alpha
    losses[:20, 1] = 1.0    # r_hat[1] = 0.02 << alpha
    # cols 2, 3 remain all-zero -> r_hat = 0

    # Costs increasing in lambda: cheapest valid is col1.
    costs = np.tile(np.array([0.0, 0.10, 0.20, 0.30]), (n, 1))
    res = ltt_select(losses, costs, grid, alpha=alpha, delta=delta, procedure="bonferroni")
    assert res.valid_mask.tolist() == [False, True, True, True]
    assert res.lambda_idx == 1
    assert res.lambda_value == grid[1]

    # Now make col2 the cheapest valid -> selection must follow cost, not index order.
    costs2 = np.tile(np.array([0.00, 0.30, 0.05, 0.40]), (n, 1))
    res2 = ltt_select(losses, costs2, grid, alpha=alpha, delta=delta, procedure="bonferroni")
    assert res2.valid_mask.tolist() == [False, True, True, True]
    assert res2.lambda_idx == 2

    # No valid column -> lambda_star is None.
    losses_bad = np.zeros((n, 4))
    losses_bad[:300, :] = 1.0  # every column r_hat = 0.30 >= alpha
    res3 = ltt_select(losses_bad, costs, grid, alpha=alpha, delta=delta, procedure="bonferroni")
    assert not res3.valid_mask.any()
    assert res3.lambda_idx is None
    assert res3.lambda_value is None


def test_nonmonotone_both_valid():
    """Non-monotone risk: both procedures control risk; Bonferroni certifies >= as many lambda."""
    T, n, alpha, delta = 500, 500, 0.10, 0.10
    grid = np.linspace(0.0, 1.0, 100)

    fs_true = np.zeros(T)
    bf_true = np.zeros(T)
    for t in range(T):
        losses, costs, r_curve = make_synthetic_afa(
            n, grid, true_risk="nonmonotone", alpha=alpha, seed=10_000 + t, coupling=True
        )
        res_fs = ltt_select(losses, costs, grid, alpha, delta, procedure="fixed_sequence")
        res_bf = ltt_select(losses, costs, grid, alpha, delta, procedure="bonferroni")
        if res_fs.lambda_idx is not None:
            fs_true[t] = r_curve[res_fs.lambda_idx]
        if res_bf.lambda_idx is not None:
            bf_true[t] = r_curve[res_bf.lambda_idx]

    v_fs = violation_rate(fs_true, alpha)
    v_bf = violation_rate(bf_true, alpha)
    assert v_fs <= delta + MC_SLACK, f"fixed_sequence violation_rate={v_fs:.3f}"
    assert v_bf <= delta + MC_SLACK, f"bonferroni violation_rate={v_bf:.3f}"

    # Power note: on a large calibration draw the empirical risk tracks the true
    # curve tightly, so the valid masks are stable.  Fixed-sequence certifies
    # only the upper valley (contiguous from the top); Bonferroni recovers the
    # scattered valid set across both valleys -> >= as many certified lambda.
    n_large = 20_000
    losses, costs, _ = make_synthetic_afa(
        n_large, grid, true_risk="nonmonotone", alpha=alpha, seed=777, coupling=True
    )
    res_fs = ltt_select(losses, costs, grid, alpha, delta, procedure="fixed_sequence")
    res_bf = ltt_select(losses, costs, grid, alpha, delta, procedure="bonferroni")
    n_fs = int(res_fs.valid_mask.sum())
    n_bf = int(res_bf.valid_mask.sum())
    assert n_fs >= 1, "fixed_sequence should certify the upper valley"
    assert n_bf >= n_fs, f"bonferroni ({n_bf}) should certify >= fixed_sequence ({n_fs})"