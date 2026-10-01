"""Documents a floating-point defect in the FROZEN p-value primitive (stop condition 5 of the v3
campaign instructions; ``src/cafa/risk_control.py`` must not be edited without the authors' decision).

``risk_control._hb_pvalue_array`` computes the Bentkus term as
``e * binom.cdf(np.ceil(n * r_hat), n, alpha)``.  The empirical risk of a 0/1 loss is ``r_hat = k / n``
for an integer error count ``k``, but ``r_hat`` arrives as a float: ``n * r_hat`` can land a few ulps
ABOVE ``k`` (e.g. ``197 * (1 - mean(correct)) = 17.000000000000007`` for 17 errors in 197 rows), so ``ceil`` returns ``k + 1`` and the
p-value is computed for one error more than was observed.  The error is one-sided (never fewer errors),
so the p-value is only ever too LARGE (conservative: validity is unaffected), but certification
decisions near the threshold change, and they depend on how ``r_hat`` was summed:
``mean(loss)`` vs ``1 - mean(correct)`` give different p-values for the same rows.

Observed in the campaign (handoff.md section 9): csv:diabetes ts0, policy random, lambda_ref 0.9,
calibration draw 8, tier-3 level 37, stratum 4: n = 197 answered rows with 17 errors.  The cascade
(``cafa.cascade.selective_pvalues``: ``1 - ck[ans].mean()``) gets p = 0.02705 > delta_3 = 0.025 and
refuses; the same rows with ``r_hat = mean(loss)`` give p = 0.01486 and certify.

The test asserts the intended behaviour (the p-value is a function of the error count only).  It is
marked ``xfail(strict=True)``: it fails today; if the primitive is ever fixed it will XPASS and must be
un-marked.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.stats import binom

from cafa.risk_control import hoeffding_bentkus_pvalue


def _hb_exact(k: int, n: int, alpha: float) -> float:
    """Hoeffding-Bentkus p-value from the integer error count (the documented formula)."""
    r = k / n
    kl = r * math.log(r / alpha) + (1 - r) * math.log((1 - r) / (1 - alpha)) if r > 0 else -math.log(1 - alpha)
    return min(1.0, math.exp(-n * kl), math.e * float(binom.cdf(k, n, alpha)))


def test_rounding_of_r_hat_reproduces_the_campaign_case():
    n, k = 197, 17
    r_loss = float(np.mean(np.r_[np.ones(k), np.zeros(n - k)]))
    r_correct = 1.0 - float(np.mean(np.r_[np.zeros(k), np.ones(n - k)]))
    assert abs(r_loss - r_correct) < 1e-15          # the same empirical risk ...
    assert n * r_correct > k                          # ... but n * r_hat lands above k (ceil -> k + 1)


@pytest.mark.xfail(strict=True, reason="frozen risk_control._hb_pvalue_array: ceil(n*r_hat) is off by one "
                                       "when n*r_hat exceeds the integer error count by rounding")
def test_hb_pvalue_depends_only_on_error_count():
    n, k, alpha = 197, 17, 0.15
    r_loss = float(np.mean(np.r_[np.ones(k), np.zeros(n - k)]))
    r_correct = 1.0 - float(np.mean(np.r_[np.zeros(k), np.ones(n - k)]))
    expected = _hb_exact(k, n, alpha)
    assert hoeffding_bentkus_pvalue(r_loss, n, alpha) == pytest.approx(expected, rel=1e-9)
    assert hoeffding_bentkus_pvalue(r_correct, n, alpha) == pytest.approx(expected, rel=1e-9)
