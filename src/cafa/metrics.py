"""Small, pure metric helpers (numpy only)."""

from __future__ import annotations

import numpy as np

__all__ = [
    "empirical_risk",
    "expected_cost",
    "violation_rate",
    "none_rate",
    "cost_at_selected",
    "risk_at_selected",
    "pareto_point",
]


def empirical_risk(losses: np.ndarray) -> np.ndarray:
    """Per-threshold empirical risk: column means of ``losses`` -> shape [G]."""
    return np.asarray(losses, dtype=float).mean(axis=0)


def expected_cost(costs: np.ndarray) -> np.ndarray:
    """Per-threshold expected cost: column means of ``costs`` -> shape [G]."""
    return np.asarray(costs, dtype=float).mean(axis=0)


def violation_rate(true_risk_at_selected_array: np.ndarray, alpha: float) -> float:
    """Fraction of trials whose selected threshold's *true* risk exceeds alpha.

    ``true_risk_at_selected_array`` holds, per trial, the true risk at the
    selected threshold (use a non-violating sentinel such as 0.0 for trials
    that selected nothing).  Returns 0.0 for an empty array.
    """
    arr = np.asarray(true_risk_at_selected_array, dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.mean(arr > float(alpha)))


def none_rate(selected_indices) -> float:
    """Fraction of trials that certified no threshold (``lambda_idx is None``)."""
    selected_indices = list(selected_indices)
    if len(selected_indices) == 0:
        return 0.0
    return float(np.mean([idx is None for idx in selected_indices]))

def cost_at_selected(costs: np.ndarray, lambda_idx) -> float:
    """Mean acquisition cost at the selected threshold column.

    ``costs`` is ``[n, G]`` (e.g. the TEST cost matrix from
    :func:`cafa.acquisition.stops_from_grid`).  Returns ``float('nan')`` when
    ``lambda_idx is None`` (no certified threshold this draw).
    """
    if lambda_idx is None:
        return float("nan")
    costs = np.asarray(costs, dtype=float)
    return float(costs[:, int(lambda_idx)].mean())


def risk_at_selected(losses: np.ndarray, lambda_idx) -> float:
    """Mean loss (realized risk) at the selected threshold column.

    ``losses`` is ``[n, G]``.  Returns ``float('nan')`` when ``lambda_idx is
    None``.
    """
    if lambda_idx is None:
        return float("nan")
    losses = np.asarray(losses, dtype=float)
    return float(losses[:, int(lambda_idx)].mean())


def pareto_point(losses: np.ndarray, costs: np.ndarray, lambda_idx):
    """The ``(expected_cost, empirical_risk)`` operating point at ``lambda_idx``.

    A single point on the cost--risk plane for the selected threshold, handy for
    plotting CAFA against baselines.  Returns ``(nan, nan)`` if nothing was
    selected.
    """
    return cost_at_selected(costs, lambda_idx), risk_at_selected(losses, lambda_idx)