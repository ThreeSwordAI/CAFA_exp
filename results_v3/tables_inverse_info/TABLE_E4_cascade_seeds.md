# TABLE_E4_cascade_seeds (lambda_ref key = dep, scheme = inverse_info; mean ± sd over train seeds, sample sd; single-seed rows show the value only)

| dataset | policy | n_seeds | seeds | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | certified_violation | max_excess_se |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 406.131 | 7.407 | 0.817 | 0.000 | 0.000 | -3.877 |
| csv-diabetes | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 406.131 | 4.030 | 0.892 | 0.000 | 0.000 | -3.937 |
| csv-physionet | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 |
| csv-physionet | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 |
| cube | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 21.261 | 1.875 | 1.000 | 0.010 | 0.000 | -3.368 |
| cube | random | 1 | 0 | 0.990 | 0.000 | 0.010 | 0.000 | 1.000 | 74.048 | 1.164 | 1.000 | 0.000 | 0.000 | -3.338 |
| tabular-MiniBooNE | greedy_entropy | 1 | 0 | 0.010 | 0.000 | 0.990 | 0.000 | 1.000 | 338.607 | 23.287 | 0.965 | 0.020 | 0.010 | -4.055 |
| tabular-MiniBooNE | random | 1 | 0 | 0.260 | 0.000 | 0.740 | 0.000 | 1.000 | 293.880 | 5.589 | 0.985 | 0.030 | 0.000 | -4.613 |
| tabular-adult | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 22.282 | 1.200 | 1.000 | 0.010 | 0.000 | -3.812 |
| tabular-adult | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 95.278 | 4.045 | 0.902 | 0.020 | 0.000 | -3.273 |
