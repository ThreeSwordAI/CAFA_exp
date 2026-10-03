# TABLE_E2_blindness (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | alpha | marginal_test_risk | marginal_aggregate_violation | max_stratum_over_alpha | hidden_stratum_violation_rate | hidden_certified_violation_rate |
|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 0.150 | 0.099 | 0.000 | 2.198 | 1.000 | 1.000 |
| csv-diabetes | random | 0 | 0.150 | 0.140 | 0.020 | 1.723 | 1.000 | 1.000 |
| csv-physionet | greedy_entropy | 0 | 0.200 | 0.143 | 0.000 | 0.713 | 0.000 | 0.000 |
| csv-physionet | random | 0 | 0.200 | 0.143 | 0.000 | 0.714 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | 0.150 | 0.126 | 0.010 | 1.037 | 0.600 | 0.220 |
| cube | random | 0 | 0.150 | 0.128 | 0.020 | 1.033 | 0.620 | 0.280 |
| fashionmnist | greedy_entropy | 0 | 0.150 | 0.134 | 0.000 | 1.507 | 1.000 | 1.000 |
| fashionmnist | random | 0 | 0.150 | 0.136 | 0.020 | 1.420 | 1.000 | 1.000 |
| image-imagenette | greedy_entropy | 0 | 0.100 | 0.077 | 0.020 | 1.250 | 0.960 | 0.460 |
| image-imagenette | random | 0 | 0.100 | 0.078 | 0.000 | 1.169 | 0.880 | 0.230 |
| mnist | greedy_entropy | 0 | 0.100 | 0.089 | 0.010 | 0.922 | 0.180 | 0.040 |
| mnist | random | 0 | 0.100 | 0.087 | 0.020 | 0.928 | 0.150 | 0.010 |
| tabular-adult | greedy_entropy | 0 | 0.250 | 0.197 | 0.010 | 1.180 | 1.000 | 1.000 |
| tabular-adult | random | 0 | 0.250 | 0.186 | 0.010 | 1.049 | 1.000 | 0.210 |
| tabular-MiniBooNE | greedy_entropy | 0 | 0.150 | 0.130 | 0.000 | 1.653 | 1.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | 0.150 | 0.138 | 0.000 | 1.130 | 1.000 | 0.980 |
