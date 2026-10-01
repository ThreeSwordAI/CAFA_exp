# TABLE_E6_baselines (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | baseline | mean_test_risk | mean_test_cost | stratum_violation_rate | aggregate_violation_rate |
|---|---|---|---|---|---|---|---|
| csv-physionet | greedy_entropy | 0 | budget_0.25 | 0.142 | 10.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | budget_0.5 | 0.134 | 20.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | budget_0.75 | 0.127 | 31.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.9 | 0.131 | 7.430 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.95 | 0.129 | 14.346 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.99 | 0.127 | 26.977 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | mondrian_oracle | 0.144 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | oracle_cheapest_valid | 0.144 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | plugin | 0.144 | 0.000 | 0.000 | 0.000 |
