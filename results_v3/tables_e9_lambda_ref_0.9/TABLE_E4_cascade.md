# TABLE_E4_cascade (lambda_ref key = 0.9, scheme = uniform)

| dataset | policy | seed | alpha | G | lambda_ref | marginal_cost | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | delta | deepest_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 0.150 | 2 | 0.900 | 6.879 | 0.000 | 0.000 | 0.030 | 0.970 | 0.030 | 45.000 | 6.542 | 0.023 | 0.000 | 0.100 | type_II |
| csv-diabetes | random | 0 | 0.150 | 5 | 0.900 | 11.402 | 0.000 | 0.000 | 0.570 | 0.430 | 0.570 | 45.000 | 3.947 | 0.449 | 0.000 | 0.100 | type_II |
| csv-physionet | greedy_entropy | 0 | 0.200 | 2 | 0.900 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 41.000 |  | 0.911 | 0.000 | 0.100 | feasible |
| csv-physionet | random | 0 | 0.200 | 2 | 0.900 | 0.000 | 0.050 | 0.000 | 0.950 | 0.000 | 1.000 | 39.501 |  | 0.903 | 0.000 | 0.100 | feasible |
| cube | greedy_entropy | 0 | 0.150 | 4 | 0.900 | 4.167 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 20.000 | 4.799 | 0.957 | 0.000 | 0.100 | unresolved |
| cube | random | 0 | 0.150 | 4 | 0.900 | 9.942 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 20.000 | 2.012 | 0.970 | 0.000 | 0.100 | feasible |
| fashionmnist | greedy_entropy | 0 | 0.150 | 5 | 0.900 | 5.413 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 49.000 | 9.052 | 0.962 | 0.000 | 0.100 | thr_failure_depth_unresolved |
| fashionmnist | random | 0 | 0.150 | 5 | 0.900 | 7.900 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 49.000 | 6.203 | 0.953 | 0.000 | 0.100 | type_II |
| mnist | greedy_entropy | 0 | 0.100 | 4 | 0.900 | 3.495 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 4.319 | 1.236 | 1.000 | 0.000 | 0.100 | feasible |
| mnist | random | 0 | 0.100 | 5 | 0.900 | 8.257 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 9.469 | 1.147 | 1.000 | 0.000 | 0.100 | feasible |
| tabular-adult | greedy_entropy | 0 | 0.250 | 3 | 0.900 | 2.379 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 5.884 | 0.850 | 0.000 | 0.100 | type_II |
| tabular-adult | random | 0 | 0.250 | 3 | 0.900 | 3.489 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 4.012 | 0.810 | 0.010 | 0.100 | type_II |
| tabular-MiniBooNE | greedy_entropy | 0 | 0.150 | 5 | 0.900 | 3.047 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 50.000 | 16.408 | 0.909 | 0.180 | 0.100 | type_II |
| tabular-MiniBooNE | random | 0 | 0.150 | 5 | 0.900 | 7.672 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 50.000 | 6.518 | 0.914 | 0.070 | 0.100 | type_II |
