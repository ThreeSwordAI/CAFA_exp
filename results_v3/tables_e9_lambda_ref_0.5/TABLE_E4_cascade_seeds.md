# TABLE_E4_cascade_seeds (lambda_ref key = 0.5, scheme = uniform; mean ± sd over train seeds, sample sd; single-seed rows show the value only)

| dataset | policy | n_seeds | seeds | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | certified_violation | max_excess_se |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 6.915 | 1.000 | 1.000 | 0.000 | 0.000 | -18.326 |
| csv-diabetes | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 11.420 | 1.019 | 1.000 | 0.000 | 0.000 | -2.888 |
| csv-physionet | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 |
| csv-physionet | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 |
| cube | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 5.386 | 1.288 | 1.000 | 0.000 | 0.000 | -4.000 |
| cube | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 11.510 | 1.161 | 1.000 | 0.000 | 0.000 | -2.908 |
| fashionmnist | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 9.592 | 1.780 | 1.000 | 0.000 | 0.000 | -3.654 |
| fashionmnist | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 11.095 | 1.401 | 1.000 | 0.030 | 0.000 | -3.945 |
| image-imagenette | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 11.919 | 1.482 | 1.000 | 0.000 | 0.000 | -3.003 |
| image-imagenette | random | 1 | 0 | 0.640 | 0.000 | 0.360 | 0.000 | 1.000 | 25.030 | 3.299 | 0.992 | 0.000 | 0.000 | -3.411 |
| mnist | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.769 | 1.078 | 1.000 | 0.000 | 0.000 | -3.283 |
| mnist | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 9.077 | 1.095 | 1.000 | 0.000 | 0.000 | -4.247 |
| tabular-MiniBooNE | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.070 | 1.000 | 1.000 | 0.000 | 0.000 | -8.749 |
| tabular-MiniBooNE | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 7.839 | 1.013 | 1.000 | 0.000 | 0.000 | -4.506 |
| tabular-adult | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 2.382 | 1.000 | 1.000 | 0.010 | 0.000 | -11.014 |
| tabular-adult | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.461 | 1.000 | 1.000 | 0.010 | 0.000 | -13.371 |
