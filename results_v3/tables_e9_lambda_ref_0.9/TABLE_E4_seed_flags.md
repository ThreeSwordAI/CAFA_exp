# TABLE_E4_seed_flags (lambda_ref key = 0.9, scheme = uniform)

Per (dataset, policy) with several train seeds, values per seed in seed order.  `flag` = FLAG when the tier-1 share differs across seeds by more than 0.25 (`tier1_range` = max - min; instruction_round3 Task J.3).  `deepest_k`, `n_k`, `r_full` (full-information risk), `rmin_thr` and `deepest_verdict` are the deepest stratum's audit of record (primary split's calibration pool, TABLE_E3_audit).

| dataset | policy | seeds | alpha | tier1 | tier3 | tier1_range | flag | deepest_k | n_k | r_full | rmin_thr | deepest_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 1 / 1 / 1 | 3286 / 3447 / 3275 | 0.402 / 0.404 / 0.399 | 0.401 / 0.404 / 0.399 | type_II / type_II / type_II |
| csv-diabetes | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 0.870 / 1.000 / 0.990 | 0.000 |  | 4 / 4 / 4 | 3310 / 3624 / 3235 | 0.357 / 0.347 / 0.370 | 0.357 / 0.347 / 0.370 | type_II / type_II / type_II |
| csv-physionet | greedy_entropy | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 0.010 / 0.340 / 0.920 | 0.990 / 0.660 / 0.080 | 0.910 | FLAG | 1 / 1 / 1 | 910 / 1061 / 1107 | 0.188 / 0.187 / 0.144 | 0.188 / 0.183 / 0.144 | feasible / feasible / feasible |
| csv-physionet | random | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 0.150 / 0.900 / 0.990 | 0.850 / 0.100 / 0.010 | 0.840 | FLAG | 1 / 1 / 1 | 938 / 1252 / 1403 | 0.187 / 0.157 / 0.135 | 0.184 / 0.155 / 0.133 | feasible / feasible / feasible |
| cube | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 3 / 3 / 2 | 717 / 720 / 732 | 0.165 / 0.149 / 0.161 | 0.165 / 0.149 / 0.161 | unresolved / feasible / unresolved |
| cube | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.030 / 0.030 / 0.000 | 0.970 / 0.970 / 1.000 | 0.030 |  | 3 / 3 / 4 | 740 / 765 / 764 | 0.147 / 0.127 / 0.156 | 0.145 / 0.127 / 0.154 | feasible / feasible / unresolved |
| fashionmnist | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 2644 / 2542 / 2444 | 0.162 / 0.175 / 0.183 | 0.162 / 0.175 / 0.183 | thr_failure_depth_unresolved / type_II / type_II |
| fashionmnist | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 2654 / 2591 / 2530 | 0.171 / 0.188 / 0.193 | 0.171 / 0.188 / 0.193 | type_II / type_II / type_II |
| image-imagenette | greedy_entropy | 0 / 1 / 2 | 0.1 / 0.1 / 0.1 | 0.020 / 0.190 / 0.360 | 0.980 / 0.810 / 0.640 | 0.340 | FLAG | 4 / 3 / 3 | 442 / 515 / 465 | 0.093 / 0.091 / 0.075 | 0.093 / 0.091 / 0.075 | feasible / feasible / feasible |
| image-imagenette | random | 0 / 1 / 2 | 0.1 / 0.1 / 0.1 | 0.010 / 0.550 / 0.440 | 0.990 / 0.450 / 0.560 | 0.540 | FLAG | 3 / 3 / 3 | 459 / 606 / 560 | 0.092 / 0.074 / 0.071 | 0.092 / 0.074 / 0.071 | feasible / feasible / feasible |
| mnist | greedy_entropy | 0 / 1 / 2 | 0.1 / 0.1 / 0.1 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 3 / 4 / 4 | 2937 / 3195 / 2651 | 0.013 / 0.011 / 0.014 | 0.013 / 0.011 / 0.014 | feasible / feasible / feasible |
| mnist | random | 0 / 1 / 2 | 0.1 / 0.1 / 0.1 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 4 / 4 / 4 | 2686 / 2733 / 2707 | 0.013 / 0.013 / 0.011 | 0.013 / 0.013 / 0.011 | feasible / feasible / feasible |
| tabular-MiniBooNE | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 4843 / 4789 / 4692 | 0.195 / 0.203 / 0.209 | 0.195 / 0.203 / 0.209 | type_II / type_II / type_II |
| tabular-MiniBooNE | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 4803 / 4689 / 4673 | 0.198 / 0.192 / 0.209 | 0.198 / 0.192 / 0.209 | type_II / type_II / type_II |
| tabular-adult | greedy_entropy | 0 / 1 / 2 | 0.25 / 0.25 / 0.2 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 0.230 | 0.000 |  | 2 / 1 / 3 | 3261 / 3290 / 2774 | 0.292 / 0.305 / 0.323 | 0.292 / 0.305 / 0.323 | type_II / type_II / type_II |
| tabular-adult | random | 0 / 1 / 2 | 0.25 / 0.25 / 0.2 | 0.000 / 0.000 / 0.000 | 1.000 / 0.920 / 0.700 | 0.000 |  | 2 / 3 / 3 | 3036 / 2886 / 3125 | 0.303 / 0.328 / 0.317 | 0.302 / 0.328 / 0.317 | type_II / type_II / type_II |
