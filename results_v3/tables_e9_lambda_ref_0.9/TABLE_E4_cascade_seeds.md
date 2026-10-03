# TABLE_E4_cascade_seeds (lambda_ref key = 0.9, scheme = uniform; mean ± sd over train seeds, sample sd; single-seed rows show the value only)

| dataset | policy | n_seeds | seeds | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | certified_violation | max_excess_se |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 45.000 | 6.507 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | 0 | 0.000 | 0.000 | 0.870 | 0.130 | 0.870 | 45.000 | 4.014 | 0.688 | 0.000 | 0.000 | -3.680 |
| csv-physionet | greedy_entropy | 1 | 0 | 0.010 | 0.000 | 0.990 | 0.000 | 1.000 | 40.652 |  | 0.891 | 0.010 | 0.000 | -3.187 |
| csv-physionet | random | 1 | 0 | 0.150 | 0.000 | 0.850 | 0.000 | 1.000 | 36.525 |  | 0.920 | 0.060 | 0.000 | -3.447 |
| cube | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 20.000 | 4.781 | 0.947 | 0.000 | 0.000 | -3.651 |
| cube | random | 1 | 0 | 0.030 | 0.000 | 0.970 | 0.000 | 1.000 | 19.785 | 1.995 | 0.963 | 0.020 | 0.000 | -4.026 |
| fashionmnist | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 49.000 | 9.094 | 0.963 | 0.000 | 0.000 | -4.505 |
| fashionmnist | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 49.000 | 6.187 | 0.953 | 0.000 | 0.000 | -4.396 |
| image-imagenette | greedy_entropy | 1 | 0 | 0.020 | 0.000 | 0.980 | 0.000 | 1.000 | 48.987 | 6.091 | 0.935 | 0.020 | 0.000 | -3.459 |
| image-imagenette | random | 1 | 0 | 0.010 | 0.000 | 0.990 | 0.000 | 1.000 | 48.993 | 6.457 | 0.959 | 0.010 | 0.000 | -3.457 |
| mnist | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 4.340 | 1.241 | 1.000 | 0.000 | 0.000 | -3.649 |
| mnist | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 9.539 | 1.151 | 1.000 | 0.000 | 0.000 | -4.121 |
| tabular-MiniBooNE | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 50.000 | 16.287 | 0.905 | 0.050 | 0.000 | -3.226 |
| tabular-MiniBooNE | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 50.000 | 6.459 | 0.903 | 0.010 | 0.000 | -3.707 |
| tabular-adult | greedy_entropy | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 5.877 | 0.847 | 0.170 | 0.000 | -2.318 |
| tabular-adult | random | 1 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 4.045 | 0.806 | 0.050 | 0.000 | -3.321 |
