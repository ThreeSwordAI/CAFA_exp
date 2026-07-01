"""Heuristic stopping selectors and oracle references for the H2 comparison.

This module is **new** in Step 4 and lives *outside* the certified core
(:mod:`cafa.risk_control` is frozen).  Everything here consumes the *same*
arrays :func:`cafa.acquisition.stops_from_grid` /
:func:`cafa.metrics.stops_from_grid_np` produce -- ``losses[n, G]`` and
``costs[n, G]`` on an ascending threshold ``grid`` -- and returns a stopping
rule the runner evaluates to a realized ``(risk, cost)`` on the test split.

The point of H2 is that **none of the heuristics carries a finite-sample
guarantee**.  In particular :func:`plugin_threshold_select` targets ``alpha``
by the *empirical* calibration risk with **no multiple-testing correction**, so
it overshoots ``alpha`` on fresh test data -- exactly the failure Learn-then-Test
(:func:`cafa.risk_control.ltt_select`) is built to prevent.  The two *oracle*
references use the **test** labels and are therefore NON-deployable; they bound
what any method could do (the cost floor at matched risk, and the risk floor at
full acquisition).

All functions are numpy-only and torch-free.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

__all__ = [
    "plugin_threshold_select",
    "fixed_confidence_select",
    "budget_select",
    "realized_at_depth",
    "oracle_cheapest_valid_select",
    "oracle_full_feature_risk",
]


# --------------------------------------------------------------------------- #
# Heuristic stopping selectors (no guarantee)
# --------------------------------------------------------------------------- #
def plugin_threshold_select(
    losses: np.ndarray,
    costs: np.ndarray,
    grid: np.ndarray,
    alpha: float,
) -> Optional[int]:
    """Cheapest grid index whose *empirical* calibration risk is ``<= alpha``.

    The "plug-in" heuristic: estimate the per-threshold risk on the calibration
    set as the column mean of ``losses`` and keep every threshold whose estimate
    is at or below ``alpha`` -- **with no correction for having tested the whole
    grid**.  Among those, return the one with the smallest expected cost (column
    mean of ``costs``), matching the cost-minimising rule the certified selector
    uses.  Returns ``None`` if no column's empirical risk is ``<= alpha``.

    This is the main foil for H2: because it targets ``alpha`` on the point
    estimate it sits *right at* the boundary and overshoots on test, whereas
    :func:`cafa.risk_control.ltt_select` pays a Hoeffding--Bentkus margin so that
    ``P(R(lambda_star) > alpha) <= delta``.
    """
    losses = np.asarray(losses, dtype=float)
    costs = np.asarray(costs, dtype=float)
    grid = np.asarray(grid, dtype=float)
    r_hat = losses.mean(axis=0)
    c_hat = costs.mean(axis=0)
    valid = np.flatnonzero(r_hat <= float(alpha))
    if valid.size == 0:
        return None
    return int(valid[np.argmin(c_hat[valid])])


def fixed_confidence_select(grid: np.ndarray, t: float) -> int:
    """Grid index closest to a hand-set confidence level ``t`` (``0 <= t <= 1``).

    Implements the ubiquitous "stop once the model is at least ``t`` confident"
    heuristic by mapping ``t`` onto the readiness-threshold grid: the returned
    index is ``argmin_j |grid[j] - t|`` (ties -> lowest index).  It ignores the
    calibration data entirely, so it has no risk guarantee -- for small ``t`` it
    stops too early (unsafe), for large ``t`` it over-acquires (wasteful).
    """
    grid = np.asarray(grid, dtype=float)
    return int(np.argmin(np.abs(grid - float(t))))


def budget_select(k: int, T: Optional[int] = None) -> int:
    """Fixed acquired-budget rule: every instance stops at depth ``k``.

    Score-independent -- "acquire a fixed number of features, then predict".
    Returns the (optionally ``T``-clamped) stop depth ``k``; the runner reads the
    realized ``(risk, cost)`` straight off the trajectories at that depth with
    :func:`realized_at_depth` (there is no threshold on the ``grid`` for this
    rule).  Clamping to ``[0, T]`` handles tabular datasets whose feature count
    ``d`` is below a requested budget.
    """
    k = int(k)
    if k < 0:
        k = 0
    if T is not None:
        k = min(k, int(T))
    return k


def realized_at_depth(
    correct: np.ndarray, cum_cost: np.ndarray, k: int
) -> "tuple[float, float]":
    """Realized ``(risk, cost)`` at a fixed stop depth ``k`` from trajectories.

    ``correct`` / ``cum_cost`` are the ``[n, T+1]`` trajectory arrays (the same
    ones :func:`cafa.metrics.stops_from_grid_np` consumes).  Every instance stops
    at column ``k`` (clamped to ``[0, T]``), so::

        risk = mean(1 - correct[:, k]) ;  cost = mean(cum_cost[:, k]).

    Used to evaluate :func:`budget_select` and the full-acquisition fallback.
    """
    correct = np.asarray(correct, dtype=float)
    cum_cost = np.asarray(cum_cost, dtype=float)
    T = correct.shape[1] - 1
    k = int(np.clip(int(k), 0, T))
    risk = float(np.mean(1.0 - correct[:, k]))
    cost = float(np.mean(cum_cost[:, k]))
    return risk, cost


# --------------------------------------------------------------------------- #
# Oracles -- use TEST labels; reference bounds only, NON-deployable
# --------------------------------------------------------------------------- #
def oracle_cheapest_valid_select(
    losses_test: np.ndarray,
    costs_test: np.ndarray,
    grid: np.ndarray,
    alpha: float,
) -> Optional[int]:
    """Cheapest grid index whose *true test* risk is ``<= alpha`` (cost floor).

    Uses the **test** losses directly, so it is an oracle: it reports the lowest
    cost any threshold rule could pay while still honouring ``alpha`` in truth.
    A deployable method (LTT) can only approach this from above.  Returns
    ``None`` if no threshold controls the true test risk (``alpha`` infeasible on
    this population).
    """
    losses_test = np.asarray(losses_test, dtype=float)
    costs_test = np.asarray(costs_test, dtype=float)
    grid = np.asarray(grid, dtype=float)
    r_true = losses_test.mean(axis=0)
    c_true = costs_test.mean(axis=0)
    valid = np.flatnonzero(r_true <= float(alpha))
    if valid.size == 0:
        return None
    return int(valid[np.argmin(c_true[valid])])


def oracle_full_feature_risk(losses_test: np.ndarray) -> float:
    """Risk at **full acquisition** -- the achievable risk floor.

    Accepts either the per-instance full-acquisition loss vector ``[n]`` (i.e.
    ``1 - correct[:, T]``) or the full ``[n, G]`` test-loss matrix, in which case
    the most-acquired column (the top of an ascending grid, which forces the
    deepest stop) is used.  This is the smallest risk any stopping rule on this
    population can reach: no threshold can beat acquiring every feature.
    """
    arr = np.asarray(losses_test, dtype=float)
    if arr.ndim == 1:
        return float(arr.mean())
    if arr.ndim == 2:
        # Top-of-grid column = deepest forced stop = full acquisition.
        return float(arr[:, -1].mean())
    raise ValueError(f"losses_test must be 1-D [n] or 2-D [n, G]; got {arr.shape}.")