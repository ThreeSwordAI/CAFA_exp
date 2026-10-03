# TABLE_E2_blindness (lambda_ref key = 0.7, scheme = uniform)

| dataset | policy | seed | alpha | marginal_test_risk | marginal_aggregate_violation | max_stratum_over_alpha | hidden_stratum_violation_rate | hidden_certified_violation_rate |
|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 0.150 | 0.099 | 0.000 | 0.661 | 0.000 | 0.000 |
| csv-diabetes | random | 0 | 0.150 | 0.143 | 0.010 | 0.954 | 0.010 | 0.010 |
| csv-physionet | greedy_entropy | 0 | 0.200 | 0.143 | 0.000 | 0.715 | 0.000 | 0.000 |
| csv-physionet | random | 0 | 0.200 | 0.143 | 0.000 | 0.715 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | 0.150 | 0.133 | 0.010 | 1.341 | 1.000 | 0.970 |
| cube | random | 0 | 0.150 | 0.136 | 0.070 | 1.111 | 0.930 | 0.500 |
| fashionmnist | greedy_entropy | 0 | 0.150 | 0.137 | 0.000 | 1.390 | 1.000 | 1.000 |
| fashionmnist | random | 0 | 0.150 | 0.139 | 0.000 | 1.332 | 1.000 | 1.000 |
| image-imagenette | greedy_entropy | 0 | 0.100 | 0.083 | 0.050 | 1.153 | 0.800 | 0.400 |
| image-imagenette | random | 0 | 0.100 | 0.084 | 0.010 | 1.113 | 0.910 | 0.090 |
| mnist | greedy_entropy | 0 | 0.100 | 0.091 | 0.000 | 0.986 | 0.210 | 0.010 |
| mnist | random | 0 | 0.100 | 0.089 | 0.000 | 0.954 | 0.280 | 0.000 |
| tabular-adult | greedy_entropy | 0 | 0.250 | 0.197 | 0.010 | 0.789 | 0.010 | 0.000 |
| tabular-adult | random | 0 | 0.250 | 0.186 | 0.010 | 0.743 | 0.010 | 0.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | 0.150 | 0.130 | 0.000 | 0.864 | 0.000 | 0.000 |
| tabular-MiniBooNE | random | 0 | 0.150 | 0.141 | 0.000 | 0.937 | 0.000 | 0.000 |
