# TABLE_E6_baselines (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | baseline | mean_test_risk | mean_test_cost | stratum_violation_rate | aggregate_violation_rate | stratum_certified_violation_rate |
|---|---|---|---|---|---|---|---|---|
| mnist | greedy_entropy | 0 | budget_0.25 | 0.027 | 12.000 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | budget_0.5 | 0.016 | 24.000 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | budget_0.75 | 0.010 | 37.000 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.046 | 4.608 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.026 | 5.957 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.011 | 10.331 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | full_acquisition | 0.006 | 49.000 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | mondrian_oracle | 0.081 | 3.668 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.098 | 3.406 | 1.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 0 | plugin | 0.098 | 3.415 | 0.970 | 0.190 | 0.850 |
