# TABLE_E4_seed_flags (lambda_ref key = dep, scheme = uniform)

Per (dataset, policy) with several train seeds, values per seed in seed order.  `flag` = FLAG when the tier-1 share differs across seeds by more than 0.25 (`tier1_range` = max - min; instruction_round3 Task J.3).  `deepest_k`, `n_k`, `r_full` (full-information risk), `rmin_thr` and `deepest_verdict` are the deepest stratum's audit of record (primary split's calibration pool, TABLE_E3_audit).

| dataset | policy | seeds | alpha | tier1 | tier3 | tier1_range | flag | deepest_k | n_k | r_full | rmin_thr | deepest_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 / 1 / 2 | 0.12 / 0.11 / 0.12 | 0.000 / 0.000 / 0.000 | 1.000 / 0.000 / 1.000 | 0.000 |  | 1 / 1 / 1 | 4289 / 3614 / 4450 | 0.333 / 0.388 / 0.321 | 0.329 / 0.388 / 0.317 | type_II / type_II / type_II |
| csv-diabetes | random | 0 / 1 / 2 | 0.12 / 0.11 / 0.12 | 0.000 / 0.000 / 0.000 | 0.020 / 0.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 3300 / 3572 / 3243 | 0.366 / 0.369 / 0.319 | 0.366 / 0.369 / 0.319 | type_II / type_II / type_II |
| csv-physionet | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.17 / 0.15 | 0.580 / 0.960 / 0.800 | 0.420 / 0.040 / 0.200 | 0.380 | FLAG | 0 / 0 / 0 | 2160 / 2160 / 2160 | 0.126 / 0.131 / 0.120 | 0.126 / 0.131 / 0.120 | feasible / feasible / feasible |
| csv-physionet | random | 0 / 1 / 2 | 0.15 / 0.17 / 0.15 | 0.580 / 0.960 / 0.800 | 0.420 / 0.040 / 0.200 | 0.380 | FLAG | 0 / 0 / 0 | 2160 / 2160 / 2160 | 0.126 / 0.131 / 0.120 | 0.126 / 0.130 / 0.120 | feasible / feasible / feasible |
| cube | greedy_entropy | 0 / 1 / 2 | 0.08 / 0.09 / 0.08 | 0.000 / 0.000 / 0.000 | 1.000 / 0.870 / 0.530 | 0.000 |  | 4 / 4 / 3 | 799 / 707 / 692 | 0.164 / 0.181 / 0.189 | 0.164 / 0.181 / 0.189 | type_II / type_II / type_II |
| cube | random | 0 / 1 / 2 | 0.08 / 0.09 / 0.08 | 0.000 / 0.000 / 0.000 | 0.990 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 735 / 875 / 760 | 0.148 / 0.120 / 0.155 | 0.146 / 0.120 / 0.154 | type_II / type_II / type_II |
| fashionmnist | greedy_entropy | 0 / 1 / 2 | 0.09 / 0.08 / 0.1 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 2629 / 2752 / 2432 | 0.168 / 0.181 / 0.189 | 0.168 / 0.181 / 0.189 | type_II / type_II / type_II |
| fashionmnist | random | 0 / 1 / 2 | 0.09 / 0.08 / 0.1 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 2533 / 2569 / 2482 | 0.180 / 0.202 / 0.206 | 0.180 / 0.202 / 0.206 | type_II / type_II / type_II |
| tabular-MiniBooNE | greedy_entropy | 0 / 1 / 2 | 0.1 / 0.11 / 0.1 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 3 | 4963 / 4662 / 4886 | 0.181 / 0.185 / 0.175 | 0.181 / 0.185 / 0.173 | type_II / type_II / type_II |
| tabular-MiniBooNE | random | 0 / 1 / 2 | 0.1 / 0.11 / 0.1 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 4 / 4 / 4 | 4739 / 4698 / 4766 | 0.191 / 0.171 / 0.186 | 0.191 / 0.171 / 0.185 | type_II / type_II / type_II |
| tabular-adult | greedy_entropy | 0 / 1 / 2 | 0.18 / 0.18 / 0.17 | 0.000 / 0.000 / 0.000 | 1.000 / 0.750 / 0.970 | 0.000 |  | 1 / 2 / 3 | 1734 / 1712 / 1958 | 0.206 / 0.330 / 0.294 | 0.204 / 0.330 / 0.294 | type_II / type_II / type_II |
| tabular-adult | random | 0 / 1 / 2 | 0.18 / 0.18 / 0.17 | 0.000 / 0.000 / 0.000 | 1.000 / 0.780 / 0.700 | 0.000 |  | 2 / 3 / 3 | 1860 / 1734 / 1679 | 0.254 / 0.309 / 0.309 | 0.254 / 0.309 / 0.308 | type_II / type_II / type_II |
