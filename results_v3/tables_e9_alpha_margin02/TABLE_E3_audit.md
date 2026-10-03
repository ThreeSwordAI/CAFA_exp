# TABLE_E3_audit (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | k | n_k | alpha | rmin_thr | rmin_depth | r_full | p_thr | p_depth | verdict | all_verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 1 | 4289 | 0.120 | 0.329 | 0.327 | 0.333 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 0 | 4 | 3300 | 0.120 | 0.366 | 0.366 | 0.366 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| csv-diabetes | greedy_entropy | 1 | 1 | 3614 | 0.110 | 0.388 | 0.386 | 0.388 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 1 | 4 | 3572 | 0.110 | 0.369 | 0.369 | 0.369 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| csv-diabetes | greedy_entropy | 2 | 1 | 4450 | 0.120 | 0.317 | 0.318 | 0.321 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 2 | 4 | 3243 | 0.120 | 0.319 | 0.318 | 0.319 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| csv-physionet | greedy_entropy | 0 | 0 | 2160 | 0.150 | 0.126 | 0.126 | 0.126 | 0.999 | 0.999 | feasible | 0:feasible |
| csv-physionet | random | 0 | 0 | 2160 | 0.150 | 0.126 | 0.126 | 0.126 | 0.999 | 0.999 | feasible | 0:feasible |
| csv-physionet | greedy_entropy | 1 | 0 | 2160 | 0.170 | 0.131 | 0.125 | 0.131 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 1 | 0 | 2160 | 0.170 | 0.130 | 0.129 | 0.131 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | greedy_entropy | 2 | 0 | 2160 | 0.150 | 0.120 | 0.120 | 0.120 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 2 | 0 | 2160 | 0.150 | 0.120 | 0.119 | 0.120 | 1.000 | 1.000 | feasible | 0:feasible |
| cube | greedy_entropy | 0 | 4 | 799 | 0.080 | 0.164 | 0.164 | 0.164 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| cube | random | 0 | 4 | 735 | 0.080 | 0.146 | 0.148 | 0.148 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| cube | greedy_entropy | 1 | 4 | 707 | 0.090 | 0.181 | 0.181 | 0.181 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| cube | random | 1 | 4 | 875 | 0.090 | 0.120 | 0.120 | 0.120 | 0.002 | 0.002 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| cube | greedy_entropy | 2 | 3 | 692 | 0.080 | 0.189 | 0.189 | 0.189 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| cube | random | 2 | 4 | 760 | 0.080 | 0.154 | 0.155 | 0.155 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | greedy_entropy | 0 | 4 | 2629 | 0.090 | 0.168 | 0.168 | 0.168 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | random | 0 | 4 | 2533 | 0.090 | 0.180 | 0.179 | 0.180 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | greedy_entropy | 1 | 4 | 2752 | 0.080 | 0.181 | 0.180 | 0.181 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | random | 1 | 4 | 2569 | 0.080 | 0.202 | 0.202 | 0.202 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | greedy_entropy | 2 | 4 | 2432 | 0.100 | 0.189 | 0.189 | 0.189 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | random | 2 | 4 | 2482 | 0.100 | 0.206 | 0.206 | 0.206 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-adult | greedy_entropy | 0 | 1 | 1734 | 0.180 | 0.204 | 0.206 | 0.206 | 0.005 | 0.003 | type_II | 0:feasible 1:type_II |
| tabular-adult | random | 0 | 2 | 1860 | 0.180 | 0.254 | 0.253 | 0.254 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:type_II |
| tabular-adult | greedy_entropy | 1 | 2 | 1712 | 0.180 | 0.330 | 0.330 | 0.330 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II 2:type_II |
| tabular-adult | random | 1 | 3 | 1734 | 0.180 | 0.309 | 0.309 | 0.309 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| tabular-adult | greedy_entropy | 2 | 3 | 1958 | 0.170 | 0.294 | 0.289 | 0.294 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| tabular-adult | random | 2 | 3 | 1679 | 0.170 | 0.308 | 0.306 | 0.309 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| tabular-MiniBooNE | greedy_entropy | 0 | 4 | 4963 | 0.100 | 0.181 | 0.181 | 0.181 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | random | 0 | 4 | 4739 | 0.100 | 0.191 | 0.191 | 0.191 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | greedy_entropy | 1 | 4 | 4662 | 0.110 | 0.185 | 0.185 | 0.185 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | random | 1 | 4 | 4698 | 0.110 | 0.171 | 0.171 | 0.171 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | greedy_entropy | 2 | 3 | 4886 | 0.100 | 0.173 | 0.175 | 0.175 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| tabular-MiniBooNE | random | 2 | 4 | 4766 | 0.100 | 0.185 | 0.186 | 0.186 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
