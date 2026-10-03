# TABLE_E4_seed_flags (lambda_ref key = dep, scheme = inverse_info)

Per (dataset, policy) with several train seeds, values per seed in seed order.  `flag` = FLAG when the tier-1 share differs across seeds by more than 0.25 (`tier1_range` = max - min; instruction_round3 Task J.3).  `deepest_k`, `n_k`, `r_full` (full-information risk), `rmin_thr` and `deepest_verdict` are the deepest stratum's audit of record (primary split's calibration pool, TABLE_E3_audit).

| dataset | policy | seeds | alpha | tier1 | tier3 | tier1_range | flag | deepest_k | n_k | r_full | rmin_thr | deepest_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 0.050 / 1.000 | 0.000 |  | 1 / 1 / 1 | 4289 / 3614 / 4450 | 0.333 / 0.388 / 0.321 | 0.329 / 0.388 / 0.317 | type_II / type_II / type_II |
| csv-diabetes | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 3 / 3 / 3 | 3305 / 3633 / 3391 | 0.241 / 0.241 / 0.231 | 0.241 / 0.241 / 0.231 | type_II / type_II / type_II |
| csv-physionet | greedy_entropy | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 2160 / 2160 / 2160 | 0.126 / 0.131 / 0.120 | 0.126 / 0.131 / 0.120 | feasible / feasible / feasible |
| csv-physionet | random | 0 / 1 / 2 | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 2160 / 2160 / 2160 | 0.126 / 0.131 / 0.120 | 0.126 / 0.130 / 0.120 | feasible / feasible / feasible |
| cube | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 1.000 / 0.600 / 0.970 | 0.000 / 0.400 / 0.030 | 0.400 | FLAG | 2 / 3 / 2 | 1230 / 942 / 1137 | 0.080 / 0.103 / 0.092 | 0.080 / 0.103 / 0.092 | feasible / feasible / feasible |
| cube | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.990 / 0.690 / 1.000 | 0.010 / 0.310 / 0.000 | 0.310 | FLAG | 3 / 3 / 4 | 714 / 763 / 840 | 0.083 / 0.104 / 0.090 | 0.080 / 0.104 / 0.088 | feasible / feasible / feasible |
| tabular-MiniBooNE | greedy_entropy | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.010 / 0.000 / 0.010 | 0.990 / 1.000 / 0.990 | 0.010 |  | 2 / 2 / 2 | 6883 / 6308 / 5395 | 0.146 / 0.158 / 0.151 | 0.144 / 0.158 / 0.150 | feasible / type_II / unresolved |
| tabular-MiniBooNE | random | 0 / 1 / 2 | 0.15 / 0.15 / 0.15 | 0.260 / 0.380 / 0.910 | 0.740 / 0.620 / 0.090 | 0.650 | FLAG | 3 / 3 / 4 | 4635 / 4688 / 5335 | 0.132 / 0.137 / 0.130 | 0.132 / 0.137 / 0.130 | feasible / feasible / feasible |
| tabular-adult | greedy_entropy | 0 / 1 / 2 | 0.25 / 0.25 / 0.2 | 1.000 / 0.000 / 0.020 | 0.000 / 1.000 / 0.980 | 1.000 | FLAG | 1 / 2 / 1 | 1788 / 1712 / 2098 | 0.196 / 0.330 / 0.206 | 0.196 / 0.330 / 0.206 | feasible / type_II / unresolved |
| tabular-adult | random | 0 / 1 / 2 | 0.25 / 0.25 / 0.2 | 0.000 / 0.290 / 0.000 | 1.000 / 0.710 / 1.000 | 0.290 | FLAG | 2 / 1 / 2 | 1860 / 1793 / 1736 | 0.254 / 0.225 / 0.269 | 0.254 / 0.225 / 0.269 | unresolved / feasible / type_II |
