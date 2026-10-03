# TABLE_E4_cascade_seeds (lambda_ref key = 0.7, scheme = uniform; mean ± sd over train seeds, sample sd; single-seed rows show the value only)

| dataset | policy | n_seeds | seeds | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | certified_violation | max_excess_se |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 6.915 | 1.000 | 1.000 | 0.000 | 0.000 | -18.326 |
| csv-diabetes | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 11.420 | 1.019 | 1.000 | 0.000 | 0.000 | -2.888 |
| csv-physionet | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 |
| csv-physionet | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000 | -6.616 |
| cube | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 6.989 | 1.671 | 1.000 | 0.000 | 0.000 | -3.586 |
| cube | random | 1 | 0 | 0.990 | 0.000 | 0.010 | 0.000 | 1.000 | 11.507 | 1.160 | 1.000 | 0.000 | 0.000 | -3.265 |
| fashionmnist | greedy_entropy | 1 | 0 | 0.920 | 0.000 | 0.080 | 0.000 | 1.000 | 17.755 | 3.295 | 0.999 | 0.020 | 0.000 | -3.029 |
| fashionmnist | random | 1 | 0 | 0.700 | 0.000 | 0.300 | 0.000 | 1.000 | 27.835 | 3.515 | 0.997 | 0.130 | 0.010 | -3.322 |
| image-imagenette | greedy_entropy | 1 | 0 | 0.340 | 0.000 | 0.660 | 0.000 | 1.000 | 41.499 | 5.160 | 0.985 | 0.000 | 0.000 | -3.411 |
| image-imagenette | random | 1 | 0 | 0.580 | 0.000 | 0.420 | 0.000 | 1.000 | 28.649 | 3.776 | 0.991 | 0.000 | 0.000 | -2.907 |
| mnist | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.890 | 1.112 | 1.000 | 0.000 | 0.000 | -3.346 |
| mnist | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 8.900 | 1.074 | 1.000 | 0.000 | 0.000 | -3.546 |
| tabular-MiniBooNE | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.070 | 1.000 | 1.000 | 0.000 | 0.000 | -8.749 |
| tabular-MiniBooNE | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 7.839 | 1.013 | 1.000 | 0.000 | 0.000 | -4.506 |
| tabular-adult | greedy_entropy | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 2.382 | 1.000 | 1.000 | 0.010 | 0.000 | -11.014 |
| tabular-adult | random | 1 | 0 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.461 | 1.000 | 1.000 | 0.010 | 0.000 | -13.371 |
