"""v3 -- probe-committed design rules."""

from __future__ import annotations

import numpy as np
import pytest

from cafa.commit_rules import (
    deployment_aligned_lambda_ref,
    escalation_fractions,
    detectability_limited_edges,
    escalation_levels,
    kl_bernoulli,
    n_min_required,
    plugin_lambda_on_probe,
)
from cafa.metrics import reference_buckets, reference_depth
from cafa.synthetic_planted import default_strata, make_planted_population

T = 30
GRID = np.linspace(0.0, 1.0, 100)


def test_n_min_table_matches_paper():
    # Section 4.2 table of the revision plan (margin 0.05).
    assert n_min_required(0.10, 0.05) == 180
    assert n_min_required(0.15, 0.05) == 275
    assert n_min_required(0.20, 0.05) == 358
    assert n_min_required(0.25, 0.05) == 428
    assert n_min_required(0.15, 0.10) == 212
    assert abs(kl_bernoulli(0.10, 0.15) - 0.01093) < 2e-4


def test_plugin_lambda_on_probe_is_smallest_feasible():
    pop = make_planted_population(3000, T, default_strata(G=2), seed=1)
    val, idx = plugin_lambda_on_probe(pop["scores"], pop["correct"], GRID, 0.15)
    assert 0.0 <= val <= 1.0 and GRID[idx] == val
    assert deployment_aligned_lambda_ref(pop["scores"], pop["correct"], GRID, 0.15) == val
    # infeasible alpha -> top of the grid
    val2, idx2 = plugin_lambda_on_probe(pop["scores"], pop["correct"], GRID, 0.0)
    assert idx2 == GRID.shape[0] - 1 and val2 == 1.0


def test_detectability_limited_edges_merges_small_bins():
    pop = make_planted_population(2000, T, default_strata(G=4), seed=2)
    d = reference_depth(pop["scores"], 0.9)
    edges5, G5, exp5 = detectability_limited_edges(d, 5, n_cal_expected=10_000, n_min=275)
    assert G5 == edges5.size + 1 and np.all(exp5 >= 275)
    edges_small, G_small, exp_small = detectability_limited_edges(d, 5, n_cal_expected=600, n_min=275)
    assert G_small < G5 and np.all(exp_small >= 275) or G_small == 1
    # committed edges reproduce the partition through reference_buckets
    bid, used = reference_buckets(pop["scores"], 0.9, 5, 1, edges=edges5)
    assert np.array_equal(used, edges5) and bid.max() == G5 - 1 or bid.max() <= G5 - 1


def test_escalation_levels_monotone_and_fraction_aligned():
    pop = make_planted_population(5000, T, default_strata(G=2), seed=3)
    fr = np.linspace(0.02, 1.0, 50)
    mu, a = escalation_levels(pop["scores"][:, T], fr)
    assert np.all(np.diff(mu) >= 0) and np.all(np.diff(a) <= 0)
    g = pop["scores"][:, T]
    # the last level answers about 2%, the first about 100%
    assert abs(float((g >= mu[-1]).mean()) - 0.02) < 0.02
    assert float((g >= mu[0]).mean()) > 0.99
    # stratum-aware levels: every stratum answers at least ~2% at the top level
    mu_s, _ = escalation_levels(g, fr, probe_bucket_id=pop["stratum"])
    for k in np.unique(pop["stratum"]):
        assert float((g[pop["stratum"] == k] >= mu_s[-1]).mean()) >= 0.015
    assert np.all(mu_s <= mu + 1e-12)
    with pytest.raises(ValueError):
        escalation_levels(g, np.array([0.0, 0.5]))


def test_escalation_fractions_start_at_detectable_level():
    fr = escalation_fractions(min_expected_stratum_count=1000, alpha=0.15, level=0.025, n_levels=41)
    # n_min(0.15, 0.025) = 339 -> a_min = 0.339
    assert abs(fr[0] - 0.339) < 1e-6 and fr[-1] == 1.0 and fr.shape == (41,)
    fr2 = escalation_fractions(min_expected_stratum_count=50_000, alpha=0.15, level=0.025)
    assert fr2[0] == 0.10                      # floored
    fr3 = escalation_fractions(min_expected_stratum_count=100, alpha=0.15, level=0.025)
    assert fr3[0] == 1.0                       # capped: tier 3 reduces to full answering
