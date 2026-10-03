# TABLE_E4_cascade_seeds (lambda_ref key = dep, scheme = uniform; mean ± sd over train seeds, sample sd; single-seed rows show the value only)

| dataset | policy | n_seeds | seeds | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | certified_violation | max_excess_se |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 45.000 | 6.507 | 0.778 | 0.000 | 0.000 | -4.244 |
| csv-diabetes | random | 1 | 0 | 0.000 | 0.000 | 0.020 | 0.980 | 0.020 | 45.000 | 2.579 | 0.016 | 0.000 | 0.000 | -0.805 |
| csv-physionet | greedy_entropy | 1 | 0 | 0.580 | 0.000 | 0.420 | 0.000 | 1.000 | 22.991 | 2.593 | 0.978 | 0.010 | 0.000 | -3.386 |
| csv-physionet | random | 1 | 0 | 0.580 | 0.000 | 0.420 | 0.000 | 1.000 | 25.433 | 1.885 | 0.978 | 0.010 | 0.000 | -3.180 |
| cube | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 20.000 | 2.489 | 0.866 | 0.000 | 0.000 | -4.058 |
| cube | random | 1 | 0 | 0.000 | 0.000 | 0.990 | 0.010 | 0.990 | 20.000 | 1.499 | 0.882 | 0.000 | 0.000 | -3.981 |
| fashionmnist | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 49.000 | 4.404 | 0.897 | 0.000 | 0.000 | -4.169 |
| fashionmnist | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 49.000 | 3.682 | 0.891 | 0.000 | 0.000 | -3.426 |
| tabular-MiniBooNE | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 50.000 | 5.722 | 0.825 | 0.000 | 0.000 | -3.427 |
| tabular-MiniBooNE | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 50.000 | 2.951 | 0.827 | 0.000 | 0.000 | -4.260 |
| tabular-adult | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 2.993 | 0.795 | 0.000 | 0.000 | -2.966 |
| tabular-adult | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 2.730 | 0.749 | 0.000 | 0.000 | -2.893 |
