"""Pure risk-control core for CAFA (Conformal Active Feature Acquisition).

This module is **pure**: it takes plain arrays in and returns a selection out.
It depends only on ``numpy`` and ``scipy`` -- no torch, no data, no models --
so its finite-sample guarantee can be unit-tested in isolation against a
synthetic problem with known true risk (the G1 gate) *before* any deep
learning exists.

Method
------
For a grid of candidate stopping thresholds ``lambda`` we form, per threshold,
an empirical risk ``r_hat`` from a calibration set and a Hoeffding--Bentkus
p-value for the null ``H: R(lambda) > alpha``.  We then control the
family-wise error rate (FWER) across the grid -- via fixed-sequence testing or
Bonferroni -- to obtain the set of thresholds that are *certified* to control
risk at level ``alpha`` with confidence ``1 - delta``.  Among the certified
thresholds we return the one with the smallest expected cost ``c_hat`` (the
cheapest risk-valid stopping threshold).

Guarantee
---------
With ``lambda_star`` the selected threshold,

    P_over_calibration_draws( R(lambda_star) > alpha ) <= delta.

References
----------
Hoeffding--Bentkus bound: Bates, Angelopoulos, Lei, Malik & Jordan (2021),
"Distribution-Free, Risk-Controlling Prediction Sets".  Multiple-testing /
selection view: Angelopoulos et al. (2021), "Learn then Test: Calibrating
Predictive Algorithms to Achieve Risk Control".
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.stats import binom

_E = math.e
_TINY = float(np.finfo(float).tiny)  # smallest positive double; keeps p strictly > 0

__all__ = [
    "hoeffding_bentkus_pvalue",
    "ltt_select",
    "SelectionResult",
    "mondrian_select",
    "weighted_ltt_select",
]


# --------------------------------------------------------------------------- #
# Binary KL divergence (used by the Hoeffding term)
# --------------------------------------------------------------------------- #
def _binary_kl(a: np.ndarray, b: float) -> np.ndarray:
    """Binary KL divergence ``d(a, b)`` for ``a`` an array, ``b`` a scalar in (0,1).

        d(a, b) = a*ln(a/b) + (1-a)*ln((1-a)/(1-b))

    with the limits handled exactly:
        a == 0  ->  d = -ln(1-b)
        a == 1  ->  d = -ln(b)
    """
    a = np.asarray(a, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        # ``np.where`` evaluates both branches; the unused (nan) branch at the
        # a==0 / a==1 limits is discarded, and errstate silences the warning.
        term1 = np.where(a > 0.0, a * np.log(a / b), 0.0)
        term2 = np.where(a < 1.0, (1.0 - a) * np.log((1.0 - a) / (1.0 - b)), 0.0)
    return term1 + term2


# --------------------------------------------------------------------------- #
# Hoeffding--Bentkus p-value
# --------------------------------------------------------------------------- #
def _hb_pvalue_array(r_hat: np.ndarray, n: int, alpha: float) -> np.ndarray:
    """Vectorized Hoeffding--Bentkus p-value (single source of truth).

    Columns with ``r_hat >= alpha`` get p = 1.0 (no evidence that R <= alpha).
    Otherwise p = min(p_hoeffding, p_bentkus) clipped to (0, 1].
    """
    r_hat = np.asarray(r_hat, dtype=float)
    n = int(n)
    alpha = float(alpha)

    p = np.ones_like(r_hat, dtype=float)
    below = r_hat < alpha
    if np.any(below):
        rb = r_hat[below]

        # Hoeffding (Chernoff / relative-entropy form):
        #   P(R_hat <= r) <= exp(-n * d(r, alpha))
        p_hoeffding = np.exp(-n * _binary_kl(rb, alpha))

        # Bentkus:
        #   P(R_hat <= r) <= e * P(Binom(n, alpha) <= ceil(n * r))
        k = np.ceil(n * rb).astype(int)
        p_bentkus = _E * binom.cdf(k, n, alpha)

        pv = np.minimum(p_hoeffding, p_bentkus)
        pv = np.minimum(pv, 1.0)          # clip upper to 1
        pv = np.maximum(pv, _TINY)        # keep strictly > 0
        p[below] = pv
    return p


def hoeffding_bentkus_pvalue(r_hat: float, n: int, alpha: float) -> float:
    """Valid p-value for the null ``H: R > alpha`` (a small p certifies R <= alpha).

    If ``r_hat >= alpha`` return ``1.0``.  Otherwise return
    ``min(p_hoeffding, p_bentkus)`` clipped to ``(0, 1]`` where

        p_hoeffding = exp(-n * d(r_hat, alpha))        # d = binary KL
        p_bentkus   = e * BinomCDF(ceil(n*r_hat); n, alpha)

    This is the Hoeffding--Bentkus bound (Bates et al. 2021; used in
    Learn-then-Test, Angelopoulos et al. 2021).

    Parameters
    ----------
    r_hat : float
        Empirical risk (mean loss) in [0, 1].
    n : int
        Calibration sample size.
    alpha : float
        Target risk level in (0, 1).
    """
    r_hat = float(r_hat)
    if r_hat >= float(alpha):
        return 1.0
    return float(_hb_pvalue_array(np.array([r_hat], dtype=float), n, alpha)[0])


# --------------------------------------------------------------------------- #
# Selection
# --------------------------------------------------------------------------- #
@dataclass
class SelectionResult:
    """Result of :func:`ltt_select`.

    Attributes
    ----------
    valid_mask : np.ndarray[bool], shape [G]
        Which grid thresholds are certified to control risk at FWER <= delta.
    lambda_idx : int or None
        Index of the selected (cheapest risk-valid) threshold; None if no
        threshold is certified.
    lambda_value : float or None
        ``grid[lambda_idx]`` (or None).
    r_hat : np.ndarray, shape [G]
        Per-threshold empirical risk (column means of ``losses``).
    c_hat : np.ndarray, shape [G]
        Per-threshold expected cost (column means of ``costs``).
    pvalues : np.ndarray, shape [G]
        Per-threshold Hoeffding--Bentkus p-values.
    alpha, delta : float
        Target risk level and error budget.
    procedure : str
        FWER procedure used ("fixed_sequence" or "bonferroni").
    """

    valid_mask: np.ndarray
    lambda_idx: Optional[int]
    lambda_value: Optional[float]
    r_hat: np.ndarray
    c_hat: np.ndarray
    pvalues: np.ndarray
    alpha: float
    delta: float
    procedure: str


def ltt_select(
    losses: np.ndarray,
    costs: np.ndarray,
    grid: np.ndarray,
    alpha: float,
    delta: float,
    bound: str = "hb",
    procedure: str = "fixed_sequence",
) -> SelectionResult:
    """Select the cheapest risk-valid stopping threshold via Learn-then-Test.

    Parameters
    ----------
    losses : np.ndarray, shape [n, G], values in [0, 1]
        Per-instance, per-threshold losses.
    costs : np.ndarray, shape [n, G], values >= 0
        Per-instance, per-threshold acquisition costs.
    grid : np.ndarray, shape [G]
        Candidate thresholds ``lambda`` in **ascending** order.
    alpha : float
        Target risk level.
    delta : float
        Error budget (FWER is controlled at <= delta).
    bound : {"hb", "hoeffding_bentkus"}
        P-value bound.  Only Hoeffding--Bentkus is available in Step 1.
    procedure : {"fixed_sequence", "bonferroni"}
        FWER-controlling multiple-testing procedure.

        * ``fixed_sequence`` -- test in the pre-specified order of **decreasing
          lambda** (column ``G-1`` -> ``0``); certify while ``p <= delta`` and
          stop at the first ``p > delta``.  Valid for any risk; high power when
          risk is monotone decreasing in lambda.
        * ``bonferroni`` -- ``valid_mask[j] = (p[j] <= delta / G)``.  Valid for
          arbitrary risk; recovers scattered valid lambda.

    Returns
    -------
    SelectionResult

    Guarantee
    ---------
        P_over_calibration_draws( R(lambda_star) > alpha ) <= delta.
    """
    losses = np.asarray(losses, dtype=float)
    costs = np.asarray(costs, dtype=float)
    grid = np.asarray(grid, dtype=float)

    if losses.ndim != 2:
        raise ValueError(f"losses must be 2-D [n, G]; got shape {losses.shape}.")
    n, G = losses.shape
    if costs.shape != losses.shape:
        raise ValueError(f"costs shape {costs.shape} must match losses {losses.shape}.")
    if grid.shape != (G,):
        raise ValueError(f"grid shape {grid.shape} must be [G]=({G},).")
    if np.any(np.diff(grid) < 0):
        raise ValueError("grid must be in ascending order.")
    if bound not in ("hb", "hoeffding_bentkus"):
        raise ValueError(f"unknown bound {bound!r}; only Hoeffding--Bentkus in Step 1.")

    r_hat = losses.mean(axis=0)
    c_hat = costs.mean(axis=0)
    p = _hb_pvalue_array(r_hat, n, alpha)

    valid_mask = np.zeros(G, dtype=bool)
    if procedure == "fixed_sequence":
        # Pre-specified order: decreasing lambda (largest grid value first).
        # Certify a contiguous block from the top; stop at the first failure.
        for j in range(G - 1, -1, -1):
            if p[j] <= delta:
                valid_mask[j] = True
            else:
                break
    elif procedure == "bonferroni":
        valid_mask = p <= (delta / G)
    else:
        raise ValueError(
            f"unknown procedure {procedure!r}; "
            "expected 'fixed_sequence' or 'bonferroni'."
        )

    valid_idx = np.flatnonzero(valid_mask)
    if valid_idx.size == 0:
        lambda_idx: Optional[int] = None
        lambda_value: Optional[float] = None
    else:
        # Cheapest risk-valid threshold; ties resolved to the lowest index.
        lambda_idx = int(valid_idx[np.argmin(c_hat[valid_idx])])
        lambda_value = float(grid[lambda_idx])

    return SelectionResult(
        valid_mask=valid_mask,
        lambda_idx=lambda_idx,
        lambda_value=lambda_value,
        r_hat=r_hat,
        c_hat=c_hat,
        pvalues=p,
        alpha=float(alpha),
        delta=float(delta),
        procedure=procedure,
    )


# --------------------------------------------------------------------------- #
# Stubs -- implemented in later steps (do NOT implement now)
# --------------------------------------------------------------------------- #
def mondrian_select(*args, **kwargs):
    """Step 3: per-bucket (Mondrian) risk control -- group-conditional LTT across
    cost / stop-depth buckets for per-budget coverage."""
    raise NotImplementedError("mondrian_select is implemented in Step 3.")


def weighted_ltt_select(*args, **kwargs):
    """Step 5: covariate-shift-robust LTT via importance-weighted risk estimates
    (weighted-CAFA)."""
    raise NotImplementedError("weighted_ltt_select is implemented in Step 5.")