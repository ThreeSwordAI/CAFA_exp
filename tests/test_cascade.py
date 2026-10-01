"""v3 -- certify-or-route cascade: Theorem-4 validity (Monte Carlo), Proposition-2
certification, tier routing on planted populations, apply_rule bookkeeping.

Planted populations (cafa.synthetic_planted) have KNOWN true accuracy, so the
true stratum risk of every deployed rule is read off exactly.  Strata are the
TRUE label-free strata (a function of the rise rate beta), which is a valid
stratum map for Theorems 2-4.  Runtime target < 60 s CPU.
"""

from __future__ import annotations

import numpy as np
import pytest

from cafa.cascade import (
    allocate_delta,
    apply_rule,
    certify_or_route,
    tier_budget,
    tier_escalation,
)
from cafa.commit_rules import escalation_levels
from cafa.synthetic_planted import (
    default_strata,
    make_planted_population,
    true_selective_risk,
    true_stratum_risk_of_threshold,
)

T = 30
ALPHA = 0.15
DELTA = 0.10
GRID = np.linspace(0.0, 1.0, 100)
FRACS = np.linspace(0.20, 1.0, 41)   # a_min from escalation_fractions (n_k ~ 1000, alpha 0.15, delta3 0.025)


def _mu_grid(pop):
    mu, _ = escalation_levels(pop["scores"][:, T], FRACS, probe_bucket_id=pop["stratum"])
    return mu


def test_allocate_delta_sums_to_delta():
    d1, d2, d3 = allocate_delta(0.10)
    assert abs(d1 + d2 + d3 - 0.10) < 1e-12
    assert d1 == pytest.approx(0.05) and d2 == pytest.approx(0.025)
    with pytest.raises(ValueError):
        allocate_delta(0.1, (0.5, 0.5, 0.5))


def test_tier1_certifies_when_full_information_is_stratum_safe():
    """Proposition 2(a): all strata safe with margin at full acquisition -> tier 1."""
    strata = default_strata(G=4)            # r = 0.03 everywhere, h = 0
    probe = make_planted_population(5000, T, strata, seed=1)
    mu = _mu_grid(probe)
    n_tier1 = 0
    draws = 40
    for d in range(draws):
        cal = make_planted_population(4000, T, strata, seed=100 + d)
        res = certify_or_route(cal["scores"], cal["correct"], cal["cum_cost"], GRID, mu,
                               ALPHA, DELTA, cal["stratum"])
        n_tier1 += int(res.tier == 1)
    assert n_tier1 >= int(0.95 * draws), f"tier-1 certification in only {n_tier1}/{draws} draws"


def test_theorem4_validity_monte_carlo_all_feasible():
    """P(deployed rule unsafe on some stratum) <= delta, true risks known exactly."""
    strata = default_strata(G=4)
    for s in strata:                          # make it tight: risks close to alpha
        s["r_easy"] = 0.11
    probe = make_planted_population(5000, T, strata, seed=2)
    mu = _mu_grid(probe)
    viol = 0
    draws = 120
    for d in range(draws):
        cal = make_planted_population(3000, T, strata, seed=1000 + d)
        res = certify_or_route(cal["scores"], cal["correct"], cal["cum_cost"], GRID, mu,
                               ALPHA, DELTA, cal["stratum"])
        if res.tier == 0:
            continue
        if res.rule == "threshold":
            tr = true_stratum_risk_of_threshold(cal, cal["stratum"], res.param_value)
        elif res.rule == "budget":
            t = int(res.param_idx)
            r = 1.0 - cal["true_acc"][:, t]
            tr = {int(k): float(r[cal["stratum"] == k].mean()) for k in np.unique(cal["stratum"])}
        else:
            tr = true_selective_risk(cal, cal["stratum"], res.param_value)
        if any((k in res.k_cal) and (np.isfinite(v)) and (v > ALPHA) for k, v in tr.items()):
            viol += 1
    # Binomial(120, 0.10) upper tail: 20 or more violations has prob < 0.01.
    assert viol <= 20, f"{viol}/{draws} unsafe deployments (delta = {DELTA})"


def test_cascade_routes_to_escalation_on_information_failure():
    """Type-II stratum (hard core) -> tiers 1-2 refuse, tier 3 certifies and is safe."""
    strata = default_strata(G=3)
    strata[2].update({"r_easy": 0.05, "r_hard": 0.60, "h": 0.35, "s_cap_hard": 0.6})
    probe = make_planted_population(6000, T, strata, seed=3)
    mu = _mu_grid(probe)
    tiers = []
    unsafe = 0
    draws = 25
    for d in range(draws):
        cal = make_planted_population(6000, T, strata, seed=2000 + d)
        res = certify_or_route(cal["scores"], cal["correct"], cal["cum_cost"], GRID, mu,
                               ALPHA, DELTA, cal["stratum"])
        tiers.append(res.tier)
        if res.tier == 3:
            tr = true_selective_risk(cal, cal["stratum"], res.param_value)
            unsafe += int(any(np.isfinite(v) and v > ALPHA for v in tr.values()))
    assert all(t != 1 for t in tiers), "tier 1 must refuse: deep stratum is family-wide infeasible"
    assert sum(t == 3 for t in tiers) >= int(0.9 * draws), f"tiers taken: {tiers}"
    assert unsafe <= 4


def test_tier_budget_prefers_cheapest_certified_depth():
    strata = default_strata(G=2)
    cal = make_planted_population(4000, T, strata, seed=7)
    res = tier_budget(cal["correct"], cal["cum_cost"], ALPHA, 0.025, cal["stratum"])
    assert res.certified
    idx = np.flatnonzero(res.valid_mask)
    assert res.param_idx == int(idx.min())           # contiguous block from T down
    assert res.valid_mask[-1]                         # full acquisition certified


def test_tier_escalation_fixed_sequence_starts_at_most_conservative_level():
    strata = default_strata(G=2)
    cal = make_planted_population(3000, T, strata, seed=8)
    mu = _mu_grid(cal)
    res = tier_escalation(cal["scores"][:, T], cal["correct"][:, T], mu, ALPHA, 0.025, cal["stratum"])
    assert res.certified
    assert res.valid_mask[-1], "the most conservative level is tested first and must certify here"
    assert res.param_idx == int(np.flatnonzero(res.valid_mask).min())


def test_apply_rule_bookkeeping():
    strata = default_strata(G=2)
    cal = make_planted_population(2000, T, strata, seed=9)
    tst = make_planted_population(2000, T, strata, seed=10)
    mu = _mu_grid(cal)
    res = certify_or_route(cal["scores"], cal["correct"], cal["cum_cost"], GRID, mu,
                           ALPHA, DELTA, cal["stratum"])
    out = apply_rule(res, tst["scores"], tst["correct"], tst["cum_cost"], GRID, mu, tst["stratum"])
    assert out["loss"].shape == (2000,) and out["cost"].shape == (2000,)
    assert set(out["per_stratum"].keys()) == set(np.unique(tst["stratum"]).tolist())
    if res.rule != "escalation":
        assert out["answered_fraction"] == 1.0
    assert 0.0 <= out["risk"] <= 1.0


def test_probe_ordered_escalation_certifies_on_small_strata():
    """With ~300 rows per stratum the most-conservative-first walk is underpowered;
    the probe-ordered walk (a valid precommitted order) certifies escalation."""
    from cafa.commit_rules import escalation_order_from_probe

    strata = default_strata(G=3)
    strata[2].update({"r_easy": 0.05, "r_hard": 0.60, "h": 0.35, "s_cap_hard": 0.6})
    probe = make_planted_population(900, T, strata, seed=21)
    fr = np.linspace(0.05, 1.0, 41)
    mu, _ = escalation_levels(probe["scores"][:, T], fr, probe_bucket_id=probe["stratum"])
    order = escalation_order_from_probe(probe["scores"][:, T], probe["correct"][:, T], mu, ALPHA, probe["stratum"])
    n_cert, unsafe = 0, 0
    draws = 30
    for d in range(draws):
        cal = make_planted_population(900, T, strata, seed=3000 + d)
        res = certify_or_route(cal["scores"], cal["correct"], cal["cum_cost"], GRID, mu, ALPHA, DELTA,
                               cal["stratum"], escalation_order=order)
        if res.tier == 3:
            n_cert += 1
            tr = true_selective_risk(cal, cal["stratum"], res.param_value)
            unsafe += int(any(np.isfinite(v) and v > ALPHA for v in tr.values()))
    assert n_cert >= int(0.8 * draws), f"probe-ordered escalation certified in only {n_cert}/{draws}"
    assert unsafe <= 4
