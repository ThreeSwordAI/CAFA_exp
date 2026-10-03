# TABLE_E4_seed_flags (lambda_ref key = 0.5, scheme = uniform)

Per (dataset, policy) with several train seeds, values per seed in seed order.  `flag` = FLAG when the tier-1 share differs across seeds by more than 0.25 (`tier1_range` = max - min; instruction_round3 Task J.3).  `deepest_k`, `n_k`, `r_full` (full-information risk), `rmin_thr` and `deepest_verdict` are the deepest stratum's audit of record (primary split's calibration pool, TABLE_E3_audit).

| dataset | policy | seeds | alpha | tier1 | tier3 | tier1_range | flag | deepest_k | n_k | r_full | rmin_thr | deepest_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 16571 / 16571 / 16571 | 0.095 / 0.097 / 0.095 | 0.095 / 0.097 / 0.094 | feasible / feasible / feasible |
| csv-diabetes | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 16571 / 16571 / 16571 | 0.095 / 0.097 / 0.095 | 0.095 / 0.097 / 0.095 | feasible / feasible / feasible |
| csv-physionet | greedy_entropy | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 2160 / 2160 / 2160 | 0.126 / 0.131 / 0.120 | 0.126 / 0.131 / 0.120 | feasible / feasible / feasible |
| csv-physionet | random | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 2160 / 2160 / 2160 | 0.126 / 0.131 / 0.120 | 0.126 / 0.130 / 0.120 | feasible / feasible / feasible |
| cube | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 1 / 1 / 1 | 1862 / 2382 / 1559 | 0.060 / 0.050 / 0.055 | 0.060 / 0.050 / 0.055 | feasible / feasible / feasible |
| cube | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 3 / 3 / 3 | 707 / 677 / 933 | 0.054 / 0.050 / 0.068 | 0.054 / 0.050 / 0.068 | feasible / feasible / feasible |
| fashionmnist | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 2 / 2 / 2 | 3111 / 4961 / 3051 | 0.103 / 0.073 / 0.109 | 0.103 / 0.073 / 0.109 | feasible / feasible / feasible |
| fashionmnist | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 3 / 3 / 3 | 3894 / 3679 / 3986 | 0.085 / 0.088 / 0.083 | 0.085 / 0.088 / 0.082 | feasible / feasible / feasible |
| image-imagenette | greedy_entropy | 0 / 1 / 2 | 0.1 / 0.1 / 0.1 | 1.000 / 0.860 / 0.990 | 0.000 / 0.140 / 0.010 | 0.140 |  | 2 / 3 / 3 | 811 / 482 / 525 | 0.046 / 0.058 / 0.040 | 0.046 / 0.058 / 0.040 | feasible / feasible / feasible |
| image-imagenette | random | 0 / 1 / 2 | 0.1 / 0.1 / 0.1 | 0.640 / 1.000 / 0.840 | 0.360 / 0.000 / 0.160 | 0.360 | FLAG | 2 / 2 / 2 | 482 / 847 / 488 | 0.050 / 0.041 / 0.053 | 0.050 / 0.041 / 0.053 | feasible / feasible / feasible |
| mnist | greedy_entropy | 0 / 1 / 2 | 0.1 / 0.1 / 0.1 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 2 / 2 / 2 | 2658 / 2737 / 2905 | 0.008 / 0.006 / 0.004 | 0.008 / 0.006 / 0.004 | feasible / feasible / feasible |
| mnist | random | 0 / 1 / 2 | 0.1 / 0.1 / 0.1 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 4 / 4 / 4 | 2587 / 2433 / 2552 | 0.006 / 0.008 / 0.007 | 0.006 / 0.008 / 0.007 | feasible / feasible / feasible |
| tabular-MiniBooNE | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 23411 / 23411 / 23411 | 0.075 / 0.079 / 0.076 | 0.075 / 0.079 / 0.076 | feasible / feasible / feasible |
| tabular-MiniBooNE | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 23411 / 23411 / 23411 | 0.075 / 0.079 / 0.076 | 0.075 / 0.079 / 0.076 | feasible / feasible / feasible |
| tabular-adult | greedy_entropy | 0 / 1 / 2 | 0.25 / 0.25 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 8140 / 8140 / 8140 | 0.147 / 0.155 / 0.149 | 0.147 / 0.155 / 0.149 | feasible / feasible / feasible |
| tabular-adult | random | 0 / 1 / 2 | 0.25 / 0.25 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 8140 / 8140 / 8140 | 0.147 / 0.155 / 0.149 | 0.147 / 0.155 / 0.149 | feasible / feasible / feasible |
