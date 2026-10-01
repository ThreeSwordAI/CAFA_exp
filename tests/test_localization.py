"""v3 -- localized audit: level-gamma control, Type I / Type II detection."""

from __future__ import annotations

import numpy as np

from cafa.localization import audit_all_strata, binom_upper_p, classify_verdict
from cafa.synthetic_planted import default_strata, make_planted_population

T = 30
ALPHA = 0.15
GAMMA = 0.05
GRID = np.linspace(0.0, 1.0, 100)


def test_binom_upper_p_matches_definition():
    # P(Bin(10, 0.5) >= 5) = 0.623..., P(>= 0) = 1
    assert abs(float(binom_upper_p(5, 10, 0.5)) - 0.623046875) < 1e-9
    assert float(binom_upper_p(0, 10, 0.5)) == 1.0


def test_classify_verdict_order():
    assert classify_verdict(0.01, 0.01, 0.3, 0.3, ALPHA, GAMMA) == "type_II"
    assert classify_verdict(0.01, 0.9, 0.3, 0.10, ALPHA, GAMMA) == "type_I"
    assert classify_verdict(0.9, 0.9, 0.10, 0.3, ALPHA, GAMMA) == "feasible"
    assert classify_verdict(0.01, 0.9, 0.3, 0.3, ALPHA, GAMMA) == "thr_failure_depth_unresolved"
    assert classify_verdict(0.9, 0.9, 0.3, 0.3, ALPHA, GAMMA) == "unresolved"


def test_false_failure_rate_at_most_gamma_on_feasible_stratum():
    """Theorem 3: a feasible stratum (risk alpha - 0.03 at full acquisition) is
    declared failed (Type I or II) in at most gamma of audits."""
    strata = default_strata(G=1)
    strata[0]["r_easy"] = 0.12
    false_fail = 0
    draws = 200
    for d in range(draws):
        pop = make_planted_population(400, T, strata, seed=500 + d)
        a = audit_all_strata(pop["scores"], pop["correct"], pop["cum_cost"], GRID,
                             pop["stratum"], ALPHA, GAMMA)[0]
        false_fail += int(a.verdict in ("type_I", "type_II", "thr_failure_depth_unresolved"))
    # Binomial(200, 0.05): >= 20 false failures has prob < 1e-3.
    assert false_fail < 20, f"false failure rate {false_fail}/{draws} exceeds gamma"


def test_type_II_detected_with_large_margin():
    strata = default_strata(G=2)
    strata[1].update({"r_easy": 0.05, "r_hard": 0.60, "h": 0.40, "s_cap_hard": 0.6})
    pop = make_planted_population(6000, T, strata, seed=11)
    res = audit_all_strata(pop["scores"], pop["correct"], pop["cum_cost"], GRID,
                           pop["stratum"], ALPHA, GAMMA)
    assert res[1].verdict == "type_II", res[1]
    assert res[0].verdict == "feasible", res[0]
    assert res[1].rmin > ALPHA and res[1].p_fam <= GAMMA


def test_type_I_detected_for_overconfident_scores():
    """Scores jump to 1 at depth 1 -> every threshold stops at <= 1 (low accuracy),
    but forced depths reach the target: stopping-rule failure."""
    strata = default_strata(G=1)
    strata[0].update({"r_easy": 0.02, "overconfident_from_t": 1, "beta": (0.3, 0.6)})
    pop = make_planted_population(5000, T, strata, seed=12)
    res = audit_all_strata(pop["scores"], pop["correct"], pop["cum_cost"], GRID,
                           pop["stratum"], ALPHA, GAMMA)[0]
    assert res.verdict == "type_I", res
    assert res.rmin_depth <= ALPHA < res.rmin_thr
