# TABLE_E3_audit (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | k | n_k | alpha | rmin_thr | rmin_depth | r_full | p_thr | p_depth | verdict | all_verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 1 | 4289 | 0.120 | 0.329 | 0.327 | 0.333 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 0 | 4 | 3300 | 0.120 | 0.366 | 0.366 | 0.366 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| csv-physionet | greedy_entropy | 0 | 0 | 2160 | 0.150 | 0.126 | 0.126 | 0.126 | 0.999 | 0.999 | feasible | 0:feasible |
| csv-physionet | random | 0 | 0 | 2160 | 0.150 | 0.126 | 0.126 | 0.126 | 0.999 | 0.999 | feasible | 0:feasible |
| cube | greedy_entropy | 0 | 4 | 799 | 0.080 | 0.164 | 0.164 | 0.164 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| cube | random | 0 | 4 | 735 | 0.080 | 0.146 | 0.148 | 0.148 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | greedy_entropy | 0 | 4 | 2629 | 0.090 | 0.168 | 0.168 | 0.168 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | random | 0 | 4 | 2533 | 0.090 | 0.180 | 0.179 | 0.180 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-adult | greedy_entropy | 0 | 1 | 1734 | 0.180 | 0.204 | 0.206 | 0.206 | 0.005 | 0.003 | type_II | 0:feasible 1:type_II |
| tabular-adult | random | 0 | 2 | 1860 | 0.180 | 0.254 | 0.253 | 0.254 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:type_II |
| tabular-MiniBooNE | greedy_entropy | 0 | 4 | 4963 | 0.100 | 0.181 | 0.181 | 0.181 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | random | 0 | 4 | 4739 | 0.100 | 0.191 | 0.191 | 0.191 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
