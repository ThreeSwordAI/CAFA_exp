# TABLE_E6_baselines (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | baseline | mean_test_risk | mean_test_cost | stratum_violation_rate | aggregate_violation_rate |
|---|---|---|---|---|---|---|---|
| mnist | greedy_entropy | 0 | budget_0.25 | 0.026 | 12.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | budget_0.5 | 0.015 | 24.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | budget_0.75 | 0.010 | 37.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.046 | 4.583 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.025 | 5.970 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.010 | 10.324 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | full_acquisition | 0.006 | 49.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | mondrian_oracle | 0.080 | 3.662 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.099 | 3.392 | 1.000 | 0.000 |
| mnist | greedy_entropy | 0 | plugin | 0.097 | 3.417 | 0.990 | 0.040 |
