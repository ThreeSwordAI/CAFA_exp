from cafa.hidden_risk import hidden_excess_bound, n_min_table, stratum_risk_upper_bound, tier1_design_condition


def test_lemma1_numbers():
    assert abs(stratum_risk_upper_bound(0.141, 0.217) - 0.6498) < 1e-3
    assert abs(hidden_excess_bound(0.15, 0.141, 0.217) - 0.4998) < 1e-3
    assert stratum_risk_upper_bound(0.9, 0.1) == 1.0
    assert tier1_design_condition(0.01, 0.2, 0.15) and not tier1_design_condition(0.05, 0.2, 0.15)
    t = n_min_table()
    assert t[0.15][0.05] == 275
