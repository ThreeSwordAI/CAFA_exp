# TABLE_E4_seed_flags (lambda_ref key = dep, scheme = uniform)

Per (dataset, policy) with several train seeds, values per seed in seed order.  `flag` = FLAG when the tier-1 share differs across seeds by more than 0.25 (`tier1_range` = max - min; instruction_round3 Task J.3).  `deepest_k`, `n_k`, `r_full` (full-information risk), `rmin_thr` and `deepest_verdict` are the deepest stratum's audit of record (primary split's calibration pool, TABLE_E3_audit).

| dataset | policy | seeds | alpha | tier1 | tier3 | tier1_range | flag | deepest_k | n_k | r_full | rmin_thr | deepest_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 0.000 / 1.000 / 0.000 | 1.000 / 0.000 / 1.000 | 1.000 | FLAG | 1 / 0 / 1 | 4289 / 16571 / 4450 | 0.333 / 0.097 / 0.321 | 0.329 / 0.097 / 0.317 | type_II / feasible / type_II |
| csv-diabetes | random | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 0.260 / 1.000 / 0.550 | 0.740 / 0.000 / 0.450 | 0.740 | FLAG | 2 / 0 / 2 | 3468 / 16571 / 3261 | 0.187 / 0.097 / 0.178 | 0.187 / 0.097 / 0.177 | feasible / feasible / feasible |
| csv-physionet | greedy_entropy | 0 / 1 / 2 | 0.25 / 0.25 / 0.25 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 2160 / 2160 / 2160 | 0.126 / 0.131 / 0.120 | 0.126 / 0.131 / 0.120 | feasible / feasible / feasible |
| csv-physionet | random | 0 / 1 / 2 | 0.25 / 0.25 / 0.25 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 2160 / 2160 / 2160 | 0.126 / 0.131 / 0.120 | 0.126 / 0.130 / 0.120 | feasible / feasible / feasible |
| cube | greedy_entropy | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 2 / 2 / 2 | 1100 / 1278 / 988 | 0.067 / 0.066 / 0.077 | 0.067 / 0.066 / 0.077 | feasible / feasible / feasible |
| cube | random | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 2 / 2 / 2 | 795 / 877 / 847 | 0.063 / 0.064 / 0.071 | 0.063 / 0.064 / 0.070 | feasible / feasible / feasible |
| fashionmnist | greedy_entropy | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 3 / 3 / 3 | 3442 / 3716 / 2868 | 0.111 / 0.084 / 0.121 | 0.111 / 0.084 / 0.121 | feasible / feasible / feasible |
| fashionmnist | random | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 4 / 4 / 4 | 2966 / 2992 / 2539 | 0.108 / 0.126 / 0.128 | 0.108 / 0.126 / 0.128 | feasible / feasible / feasible |
| image-imagenette | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 2 / 2 / 1 | 577 / 587 / 1165 | 0.068 / 0.070 / 0.038 | 0.068 / 0.070 / 0.038 | feasible / feasible / feasible |
| image-imagenette | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 2 / 2 / 2 | 602 / 647 / 628 | 0.048 / 0.060 / 0.056 | 0.048 / 0.060 / 0.056 | feasible / feasible / feasible |
| mnist | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 3 / 3 / 3 | 3041 / 3474 / 4249 | 0.010 / 0.006 / 0.006 | 0.010 / 0.006 / 0.006 | feasible / feasible / feasible |
| mnist | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 4 / 4 / 4 | 3137 / 2705 / 2712 | 0.007 / 0.010 / 0.009 | 0.007 / 0.010 / 0.009 | feasible / feasible / feasible |
| tabular-MiniBooNE | greedy_entropy | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 2 / 2 / 2 | 6883 / 5377 / 5395 | 0.146 / 0.160 / 0.151 | 0.144 / 0.160 / 0.150 | feasible / feasible / feasible |
| tabular-MiniBooNE | random | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 3 / 2 / 3 | 5370 / 5447 / 5219 | 0.114 / 0.113 / 0.110 | 0.114 / 0.113 / 0.110 | feasible / feasible / feasible |
| tabular-adult | greedy_entropy | 0 / 1 / 2 | 0.3 / 0.3 / 0.25 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 8140 / 8140 / 8140 | 0.147 / 0.155 / 0.149 | 0.147 / 0.155 / 0.149 | feasible / feasible / feasible |
| tabular-adult | random | 0 / 1 / 2 | 0.3 / 0.3 / 0.25 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 8140 / 8140 / 8140 | 0.147 / 0.155 / 0.149 | 0.147 / 0.155 / 0.149 | feasible / feasible / feasible |
