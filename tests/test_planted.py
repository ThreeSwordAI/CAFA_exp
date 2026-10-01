"""v3 -- planted population invariants."""

from __future__ import annotations

import numpy as np

from cafa.synthetic_planted import default_strata, make_planted_population, true_family_min_risk

T = 30
GRID = np.linspace(0.0, 1.0, 100)


def test_planted_infeasible_margin_holds_exactly():
    strata = default_strata(G=2)
    strata[1].update({"r_easy": 0.05, "r_hard": 0.60, "h": 0.40, "s_cap_hard": 0.6})
    pop = make_planted_population(20000, T, strata, seed=4)
    r_thr, r_dep = true_family_min_risk(pop, 1, GRID)
    planted_floor = 0.40 * 0.60 + 0.60 * 0.05            # 0.27 in expectation
    assert min(r_thr, r_dep) >= planted_floor - 0.02
    r_thr0, r_dep0 = true_family_min_risk(pop, 0, GRID)
    assert min(r_thr0, r_dep0) <= 0.03 + 0.02


def test_scores_and_accuracy_are_bounded_and_label_free_strata():
    pop = make_planted_population(500, T, default_strata(G=3), seed=5)
    assert pop["scores"].min() >= 0 and pop["scores"].max() <= 1
    assert pop["true_acc"].min() >= 0 and pop["true_acc"].max() <= 1
    assert pop["stratum"].shape == (500,) and pop["correct"].shape == (500, T + 1)
    # deeper strata rise slower on average
    m = [pop["beta"][pop["stratum"] == k].mean() for k in range(3)]
    assert m[0] > m[1] > m[2]
