"""Regression test for the Hoeffding-Bentkus boundary rounding defect (fixed in round 2; CHANGELOG.md).

``risk_control._hb_pvalue_array`` computed the Bentkus term as
``e * binom.cdf(np.ceil(n * r_hat), n, alpha)``.  The empirical risk of a 0/1 loss is ``r_hat = k / n``
for an integer error count ``k``, but ``r_hat`` arrives as a float: ``n * r_hat`` can land a few ulps
ABOVE ``k`` (e.g. ``197 * (1 - mean(correct)) = 17.000000000000007`` for 17 errors in 197 rows), so ``ceil``
returned ``k + 1`` and the p-value was computed for one error more than was observed.  The error was
one-sided (never fewer errors), so the p-value was only ever too LARGE (conservative: validity was
unaffected), but certification decisions near the threshold changed, and they depended on how ``r_hat``
was summed: ``mean(loss)`` vs ``1 - mean(correct)`` gave different p-values for the same rows.

Campaign case (handoff.md sections 8.5 and 12): csv:diabetes ts0, policy random, lambda_ref 0.9,
calibration draw 8, tier-3 level 37, stratum 4: n = 197 answered rows with 17 errors.  With the defect the
cascade (``cafa.cascade.selective_pvalues``: ``1 - ck[ans].mean()``) got p = 0.02705 > delta_3 = 0.025 and
refused; the exact-count p-value is 0.01486.

The fix (``np.ceil(np.round(n * r_hat, 9))``) is in place since round 2; the code as used for the AAAI-27
submission is tagged ``aaai27-submission``.  Until round 2 the second test below was
``xfail(strict=True)``; it is now a plain regression test, and the third test checks the whole grid of
``scripts/scan_hb_ceil_boundary.py``.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import binom

from cafa.risk_control import hoeffding_bentkus_pvalue

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scan_hb_ceil_boundary  # noqa: E402

_TINY = float(np.finfo(float).tiny)


def _hb_exact(k: int, n: int, alpha: float) -> float:
    """Hoeffding-Bentkus p-value from the integer error count (the documented formula), clipped as the
    primitive clips it: ``min(1, p_hoeffding, p_bentkus)``, floored at the smallest positive double."""
    r = k / n
    kl = (r * math.log(r / alpha) if r > 0 else 0.0) + (1 - r) * math.log((1 - r) / (1 - alpha))
    return max(min(1.0, math.exp(-n * kl), math.e * float(binom.cdf(k, n, alpha))), _TINY)


def _r_hats(k: int, n: int) -> "tuple[float, float]":
    """The two ways the code base sums a 0/1 risk: ``mean(loss)`` and ``1 - mean(correct)``."""
    loss = np.zeros(n)
    loss[:k] = 1.0
    correct = np.ones(n)
    correct[:k] = 0.0
    return float(loss.mean()), 1.0 - float(correct.mean())


def test_rounding_of_r_hat_reproduces_the_campaign_case():
    n, k = 197, 17
    r_loss, r_correct = _r_hats(k, n)
    assert abs(r_loss - r_correct) < 1e-15          # the same empirical risk ...
    assert n * r_correct > k                          # ... but n * r_hat lands above k (ceil -> k + 1)


def test_hb_pvalue_depends_only_on_error_count():
    n, k, alpha = 197, 17, 0.15
    r_loss, r_correct = _r_hats(k, n)
    expected = _hb_exact(k, n, alpha)
    assert round(expected, 4) == 0.0149               # the campaign case: 0.0149 <= delta_3 = 0.025
    assert hoeffding_bentkus_pvalue(r_loss, n, alpha) == pytest.approx(expected, rel=1e-9)
    assert hoeffding_bentkus_pvalue(r_correct, n, alpha) == pytest.approx(expected, rel=1e-9)
    assert hoeffding_bentkus_pvalue(r_correct, n, alpha) < 0.025


def test_hb_pvalue_exact_count_on_scan_grid():
    """Every (n, k) pair of scan_hb_ceil_boundary's grid (k / n < alpha): both summation orders give the
    exact-count p-value to 1e-12 (absolute).  The absolute bound alone cannot see an off-by-one at tiny p
    (on the pre-fix code it flags 1,009 of the 16,944 evaluations), so the relative error is also bounded
    by 1e-11 (pre-fix code: 3,768 evaluations fail it; fixed code: worst relative error 7.0e-13 here)."""
    n_pairs = 0
    for alpha in scan_hb_ceil_boundary.ALPHAS:
        for n in scan_hb_ceil_boundary.N_VALUES:
            for k in range(n):
                if not k / n < alpha:
                    continue
                expected = _hb_exact(k, n, alpha)
                for r in _r_hats(k, n):
                    got = hoeffding_bentkus_pvalue(r, n, alpha)
                    assert abs(got - expected) <= 1e-12, (alpha, n, k, r, got, expected)
                    assert abs(got - expected) <= 1e-11 * expected, (alpha, n, k, r, got, expected)
                n_pairs += 1
    assert n_pairs == 8472                            # the grid of results_v3/diagnostics/hb_ceil_boundary_scan.json


def test_fractional_n_rhat_ceiling_unchanged():
    """For a genuinely fractional n * r_hat (non-0/1 losses) the Bentkus count is still the ceiling."""
    n, alpha = 200, 0.15
    r = 20.3 / n                                      # n * r_hat = 20.3 -> ceil 21
    kl = r * math.log(r / alpha) + (1 - r) * math.log((1 - r) / (1 - alpha))
    expected = max(min(1.0, math.exp(-n * kl), math.e * float(binom.cdf(21, n, alpha))), _TINY)
    assert hoeffding_bentkus_pvalue(r, n, alpha) == pytest.approx(expected, rel=1e-12)
