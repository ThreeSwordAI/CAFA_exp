"""Small, pure metric helpers (numpy only)."""

from __future__ import annotations

import numpy as np

__all__ = ["empirical_risk", "expected_cost", "violation_rate", "none_rate"]


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