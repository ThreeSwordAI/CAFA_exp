"""Synthetic active-feature-acquisition (AFA) generator with a *known* true
risk curve, so the finite-sample guarantee can be checked exactly (G1 gate).

This module is synthetic-only: no datasets, no models.  It returns
``(losses, costs, true_risk_curve)`` where ``true_risk_curve`` is the exact
risk ``r(lambda)`` used to draw the losses, letting a test check the *true*
risk at the selected threshold.
"""

from __future__ import annotations

import numpy as np

__all__ = ["make_synthetic_afa", "risk_curve"]


def risk_curve(grid: np.ndarray, true_risk: str = "monotone", alpha: float = 0.1) -> np.ndarray:
    """Exact true risk ``r(lambda)`` on ``grid``, clipped to [0, 1].

    ``"monotone"``
        Decreasing curve ``r(lambda) = 0.5 * (1 - lambda)`` that crosses
        ``alpha`` inside the grid (at ``lambda = 1 - 2*alpha``; e.g. 0.8 for
        alpha=0.1).

    ``"nonmonotone"``
        Two low-risk valleys (deep below alpha) separated by a high-risk wall,
        so the risk-valid lambda are **scattered** into two disjoint intervals.
        A fixed-sequence test (contiguous from the top) can certify only the
        upper valley, whereas Bonferroni recovers both -- the power note in the
        G1 gate.
    """
    grid = np.asarray(grid, dtype=float)
    if true_risk == "monotone":
        r = 0.5 * (1.0 - grid)
    elif true_risk == "nonmonotone":
        r_high = 0.40
        valley_lo = 0.40 * np.exp(-((grid - 0.62) / 0.12) ** 2)  # lower valley ~[0.56, 0.68]
        valley_hi = 0.40 * np.exp(-((grid - 1.00) / 0.10) ** 2)  # upper valley ~[0.95, 1.00]
        r = r_high - valley_lo - valley_hi
    else:
        raise ValueError(f"unknown true_risk {true_risk!r}; expected 'monotone' or 'nonmonotone'.")
    return np.clip(r, 0.0, 1.0)


def make_synthetic_afa(
    n: int,
    grid: np.ndarray,
    true_risk: str = "monotone",
    alpha: float = 0.1,
    seed: int = 0,
    coupling: bool = True,
):
    """Draw a synthetic calibration set with known true risk.

    Parameters
    ----------
    n : int
        Number of calibration instances.
    grid : np.ndarray, shape [G]
        Candidate thresholds ``lambda`` (ascending).
    true_risk : {"monotone", "nonmonotone"}
        Shape of the true risk curve (see :func:`risk_curve`).
    alpha : float
        Target risk level (controls where the monotone curve crosses).
    seed : int
        Seed for all randomness.
    coupling : bool
        If ``True`` (realistic, nested across lambda): draw a single
        ``u_i ~ Uniform(0,1)`` per instance and set
        ``losses[i, j] = 1 if u_i < r(lambda_j) else 0`` -- so each column has
        ``P(loss=1) = r(lambda_j)`` and the losses are coupled across
        thresholds.  If ``False``: independent ``Bernoulli(r(lambda_j))`` per
        cell.

    Returns
    -------
    losses : np.ndarray, shape [n, G], in {0, 1}
    costs  : np.ndarray, shape [n, G], = lambda (increasing in lambda, >= 0)
    true_risk_curve : np.ndarray, shape [G]
        The exact ``r(lambda)`` used to draw the losses.
    """
    grid = np.asarray(grid, dtype=float)
    G = grid.shape[0]
    r = risk_curve(grid, true_risk=true_risk, alpha=alpha)  # [G]
    rng = np.random.default_rng(seed)

    if coupling:
        u = rng.uniform(0.0, 1.0, size=(n, 1))          # one latent per instance
        losses = (u < r[None, :]).astype(float)         # P(loss=1) = r(lambda_j)
    else:
        draws = rng.uniform(0.0, 1.0, size=(n, G))      # independent per cell
        losses = (draws < r[None, :]).astype(float)

    costs = np.tile(grid[None, :], (n, 1)).astype(float)  # c(lambda) = lambda >= 0
    return losses, costs, r