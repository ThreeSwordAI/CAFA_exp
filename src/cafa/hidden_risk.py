"""v3 -- Lemma 1 (how much a marginal certificate can hide) and design tables.

For any fixed rule with population risk ``R`` and a stratum of mass ``q_k``,
``R_k <= R / q_k``; under a valid marginal certificate ``R <= alpha`` the
stratum risk can therefore reach ``alpha / q_k``.  Proposition 2 turns the
same identity into a design rule for tier-1 certification: if the
full-acquisition risk satisfies ``R_T <= q_min (alpha - margin)`` then the
full-acquisition rule is stratum-wise safe with margin on every stratum.
"""

from __future__ import annotations

import numpy as np

from .commit_rules import n_min_required

__all__ = ["stratum_risk_upper_bound", "hidden_excess_bound", "tier1_design_condition", "n_min_table"]


def stratum_risk_upper_bound(R: float, q_k: float) -> float:
    """``R_k <= R / q_k`` (Lemma 1), clipped to 1."""
    if q_k <= 0:
        raise ValueError("q_k must be positive.")
    return float(min(1.0, float(R) / float(q_k)))


def hidden_excess_bound(alpha: float, R: float, q_k: float) -> float:
    """Largest stratum excess ``r_k - alpha`` consistent with aggregate risk ``R``."""
    return float(max(0.0, stratum_risk_upper_bound(R, q_k) - float(alpha)))


def tier1_design_condition(R_full: float, q_min: float, alpha: float, margin: float = 0.05) -> bool:
    """Proposition 2(c): ``R_T <= q_min (alpha - margin)`` guarantees every stratum
    is safe with margin at full acquisition (sufficient, not necessary)."""
    return float(R_full) <= float(q_min) * (float(alpha) - float(margin))


def n_min_table(alphas=(0.10, 0.15, 0.20, 0.25), levels=(0.05, 0.10), margin: float = 0.05) -> dict:
    """``{alpha: {level: n_min}}`` -- the table printed in the paper's Section 4.2."""
    return {float(a): {float(l): n_min_required(a, l, margin) for l in levels} for a in alphas}
