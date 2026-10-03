# TABLE_E4_cascade_seeds (lambda_ref key = dep, scheme = inverse_info; mean ± sd over train seeds, sample sd; single-seed rows show the value only)

| dataset | policy | n_seeds | seeds | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | certified_violation | max_excess_se | deployed_cost_over_T | marginal_cost_over_T | mondrian_cost_over_T | tier2_would_certify | escalated_fraction | oracle_safe_cost_over_T | oracle_safe_feasible_rate | cascade_over_safe_oracle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 406.131 | 7.407 | 0.817 | 0.000 | 0.000 | -3.877 | 9.025 | 1.218 | 2.337 | 0.000 | 0.183 | 9.025 | 0.000 | 1.000 |
| csv-diabetes | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 406.131 | 4.030 | 0.892 | 0.000 | 0.000 | -3.937 | 9.025 | 2.239 | 2.116 | 0.000 | 0.108 | 9.025 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |  |
| csv-physionet | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 21.261 | 1.875 | 1.000 | 0.010 | 0.000 | -3.368 | 1.063 | 0.567 | 0.820 | 0.000 | 0.000 | 0.682 | 1.000 | 1.559 |
| cube | random | 1 | 0 | 0.990 | 0.000 | 0.010 | 0.000 | 1.000 | 74.048 | 1.164 | 1.000 | 0.000 | 0.000 | -3.338 | 3.702 | 3.182 | 3.522 | 0.000 | 0.000 | 3.326 | 1.000 | 1.113 |
| tabular-MiniBooNE | greedy_entropy | 1 | 0 | 0.010 | 0.000 | 0.990 | 0.000 | 1.000 | 338.607 | 23.287 | 0.965 | 0.020 | 0.010 | -4.055 | 6.772 | 0.291 | 2.018 | 0.000 | 0.035 | 5.014 | 0.400 | 1.351 |
| tabular-MiniBooNE | random | 1 | 0 | 0.260 | 0.000 | 0.740 | 0.000 | 1.000 | 293.880 | 5.589 | 0.985 | 0.030 | 0.000 | -4.613 | 5.878 | 1.052 | 1.734 | 0.000 | 0.015 | 1.565 | 1.000 | 3.757 |
| tabular-adult | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 22.282 | 1.200 | 1.000 | 0.010 | 0.000 | -3.812 | 1.592 | 1.326 | 1.037 | 0.000 | 0.000 | 1.494 | 1.000 | 1.065 |
| tabular-adult | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 95.278 | 4.045 | 0.902 | 0.020 | 0.000 | -3.273 | 6.806 | 1.682 | 1.741 | 0.000 | 0.098 | 5.822 | 0.200 | 1.169 |
