"""Phase 5.3 -- unit tests for the claim-audit statistics (torch-free, < 10 s)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import binom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase53_lib as L  # noqa: E402


def test_binom_upper_p_matches_manual():
    # P(Bin(10, 0.3) >= 5)
    want = sum(binom.pmf(k, 10, 0.3) for k in range(5, 11))
    got = float(L.binom_upper_p([5], 10, 0.3)[0])
    assert abs(got - want) < 1e-12
    # s = 0 -> p = 1 (upper tail includes everything)
    assert float(L.binom_upper_p([0], 10, 0.3)[0]) == 1.0
    # clipped to [0, 1]
    p = L.binom_upper_p(np.arange(0, 11), 10, 0.3)
    assert np.all(p >= 0.0) and np.all(p <= 1.0)
    # monotone nonincreasing in s
    assert np.all(np.diff(p) <= 1e-15)


def test_family_p_value_is_max_of_components():
    losses = np.zeros((50, 4))
    losses[:20, 0] = 1.0   # r = 0.40
    losses[:10, 1] = 1.0   # r = 0.20
    losses[:30, 2] = 1.0   # r = 0.60
    losses[:12, 3] = 1.0   # r = 0.24
    s = losses.sum(axis=0)
    p = L.binom_upper_p(s, 50, 0.15)
    assert float(p.max()) == float(max(p))
    # the weakest evidence (smallest error count) dominates the family p-value
    assert np.argmax(p) == 1


def test_cp_lower_onesided_edges():
    assert L.cp_lower_onesided(0, 100) == 0.0
    lb = L.cp_lower_onesided(30, 100, gamma=0.05)
    assert 0.2 < lb < 0.3   # LB below the point estimate 0.30
    # LB increases with s
    assert L.cp_lower_onesided(40, 100) > lb


def test_wilson_known_value():
    p, lo, hi = L.wilson(5, 100)
    assert abs(p - 0.05) < 1e-12
    assert 0.01 < lo < 0.05 < hi < 0.12


def test_stop_index_matrix_hand_case():
    scores = np.array([[0.1, 0.3, 0.5, 0.8, 0.8]])
    grid = np.array([0.05, 0.3, 0.55, 0.99])
    s = L.stop_index_matrix(scores, grid)
    assert s.tolist() == [[0, 1, 3, 4]]   # never crosses 0.99 -> T = 4


def test_synthetic_power_fpr_controlled():
    import synthetic_power as SP
    rng = np.random.default_rng(0)
    r = SP.run_grid_point(n=10000, q=0.2, delta_eff=0.0, alpha=0.15, gamma=0.05,
                          B=2000, rng=rng)
    # one-sided CP audit at gamma = 0.05: FPR <= gamma (+ MC slack)
    assert r["power"] <= 0.05 + 0.02, f"FPR {r['power']} exceeds gamma + slack"
    r2 = SP.run_grid_point(n=10000, q=0.2, delta_eff=0.10, alpha=0.15, gamma=0.05,
                           B=1000, rng=rng)
    assert r2["power"] > 0.95, "power should be ~1 at n*q = 2000, Delta = 0.10"


def test_synthetic_power_unresolved_on_empty():
    import synthetic_power as SP
    rng = np.random.default_rng(1)
    r = SP.run_grid_point(n=500, q=0.002, delta_eff=0.10, alpha=0.15, gamma=0.05,
                          B=500, rng=rng)
    assert r["unresolved_frac"] > 0.2   # n*q = 1 -> empty strata are common
