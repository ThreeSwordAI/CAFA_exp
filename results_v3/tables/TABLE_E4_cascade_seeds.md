# TABLE_E4_cascade_seeds (lambda_ref key = dep, scheme = uniform; mean ± sd over train seeds, sample sd; single-seed rows show the value only)

| dataset | policy | n_seeds | seeds | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | certified_violation | max_excess_se |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 45.000 | 6.507 | 0.817 | 0.000 | 0.000 | -3.877 |
| csv-diabetes | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 45.000 | 4.014 | 0.892 | 0.000 | 0.000 | -3.937 |
| csv-physionet | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 |
| csv-physionet | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 |
| cube | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 5.786 | 1.383 | 1.000 | 0.010 | 0.000 | -3.368 |
| cube | random | 1 | 0 | 0.990 | 0.000 | 0.010 | 0.000 | 1.000 | 11.527 | 1.162 | 1.000 | 0.000 | 0.000 | -3.338 |
| fashionmnist | greedy_entropy | 1 | 0 | 0.120 | 0.000 | 0.880 | 0.000 | 1.000 | 45.544 | 8.453 | 0.982 | 0.100 | 0.000 | -4.109 |
| fashionmnist | random | 1 | 0 | 0.120 | 0.000 | 0.880 | 0.000 | 1.000 | 45.367 | 5.729 | 0.985 | 0.100 | 0.010 | -3.966 |
| image-imagenette | greedy_entropy | 1 | 0 | 0.200 | 0.000 | 0.800 | 0.000 | 1.000 | 43.315 | 5.385 | 0.983 | 0.050 | 0.000 | -3.152 |
| image-imagenette | random | 1 | 0 | 0.090 | 0.000 | 0.910 | 0.000 | 1.000 | 46.072 | 6.072 | 0.963 | 0.000 | 0.000 | -3.604 |
| mnist | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.657 | 1.046 | 1.000 | 0.000 | 0.000 | -3.514 |
| mnist | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 8.994 | 1.085 | 1.000 | 0.000 | 0.000 | -3.759 |
| tabular-MiniBooNE | greedy_entropy | 1 | 0 | 0.010 | 0.000 | 0.990 | 0.000 | 1.000 | 49.653 | 16.174 | 0.965 | 0.020 | 0.010 | -4.055 |
| tabular-MiniBooNE | random | 1 | 0 | 0.260 | 0.000 | 0.740 | 0.000 | 1.000 | 43.097 | 5.567 | 0.985 | 0.030 | 0.000 | -4.613 |
| tabular-adult | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 2.985 | 1.253 | 1.000 | 0.010 | 0.000 | -3.812 |
| tabular-adult | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 4.045 | 0.902 | 0.020 | 0.000 | -3.273 |
