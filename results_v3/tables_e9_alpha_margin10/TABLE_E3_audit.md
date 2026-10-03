# TABLE_E3_audit (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | k | n_k | alpha | rmin_thr | rmin_depth | r_full | p_thr | p_depth | verdict | all_verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 1 | 4289 | 0.200 | 0.329 | 0.327 | 0.333 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 0 | 2 | 3468 | 0.200 | 0.187 | 0.187 | 0.187 | 0.978 | 0.978 | feasible | 0:feasible 1:feasible 2:feasible |
| csv-diabetes | greedy_entropy | 1 | 0 | 16571 | 0.200 | 0.097 | 0.096 | 0.097 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-diabetes | random | 1 | 0 | 16571 | 0.200 | 0.097 | 0.097 | 0.097 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-diabetes | greedy_entropy | 2 | 1 | 4450 | 0.200 | 0.317 | 0.318 | 0.321 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 2 | 2 | 3261 | 0.200 | 0.177 | 0.175 | 0.178 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| csv-physionet | greedy_entropy | 0 | 0 | 2160 | 0.250 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 0 | 0 | 2160 | 0.250 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | greedy_entropy | 1 | 0 | 2160 | 0.250 | 0.131 | 0.125 | 0.131 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 1 | 0 | 2160 | 0.250 | 0.130 | 0.129 | 0.131 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | greedy_entropy | 2 | 0 | 2160 | 0.250 | 0.120 | 0.120 | 0.120 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 2 | 0 | 2160 | 0.250 | 0.120 | 0.119 | 0.120 | 1.000 | 1.000 | feasible | 0:feasible |
| cube | greedy_entropy | 0 | 2 | 1100 | 0.200 | 0.067 | 0.067 | 0.067 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | random | 0 | 2 | 795 | 0.200 | 0.063 | 0.063 | 0.063 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | greedy_entropy | 1 | 2 | 1278 | 0.200 | 0.066 | 0.066 | 0.066 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | random | 1 | 2 | 877 | 0.200 | 0.064 | 0.064 | 0.064 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | greedy_entropy | 2 | 2 | 988 | 0.200 | 0.077 | 0.077 | 0.077 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | random | 2 | 2 | 847 | 0.200 | 0.070 | 0.071 | 0.071 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| fashionmnist | greedy_entropy | 0 | 3 | 3442 | 0.200 | 0.111 | 0.109 | 0.111 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| fashionmnist | random | 0 | 4 | 2966 | 0.200 | 0.108 | 0.107 | 0.108 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| fashionmnist | greedy_entropy | 1 | 3 | 3716 | 0.200 | 0.084 | 0.082 | 0.084 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| fashionmnist | random | 1 | 4 | 2992 | 0.200 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| fashionmnist | greedy_entropy | 2 | 3 | 2868 | 0.200 | 0.121 | 0.121 | 0.121 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| fashionmnist | random | 2 | 4 | 2539 | 0.200 | 0.128 | 0.128 | 0.128 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| image-imagenette | greedy_entropy | 0 | 2 | 577 | 0.150 | 0.068 | 0.066 | 0.068 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| image-imagenette | random | 0 | 2 | 602 | 0.150 | 0.048 | 0.048 | 0.048 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| image-imagenette | greedy_entropy | 1 | 2 | 587 | 0.150 | 0.070 | 0.063 | 0.070 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| image-imagenette | random | 1 | 2 | 647 | 0.150 | 0.060 | 0.059 | 0.060 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| image-imagenette | greedy_entropy | 2 | 1 | 1165 | 0.150 | 0.038 | 0.038 | 0.038 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible |
| image-imagenette | random | 2 | 2 | 628 | 0.150 | 0.056 | 0.056 | 0.056 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| mnist | greedy_entropy | 0 | 3 | 3041 | 0.150 | 0.010 | 0.010 | 0.010 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | random | 0 | 4 | 3137 | 0.150 | 0.007 | 0.007 | 0.007 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | greedy_entropy | 1 | 3 | 3474 | 0.150 | 0.006 | 0.006 | 0.006 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | random | 1 | 4 | 2705 | 0.150 | 0.010 | 0.010 | 0.010 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | greedy_entropy | 2 | 3 | 4249 | 0.150 | 0.006 | 0.006 | 0.006 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | random | 2 | 4 | 2712 | 0.150 | 0.009 | 0.009 | 0.009 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| tabular-adult | greedy_entropy | 0 | 0 | 8140 | 0.300 | 0.147 | 0.147 | 0.147 | 1.000 | 1.000 | feasible | 0:feasible |
| tabular-adult | random | 0 | 0 | 8140 | 0.300 | 0.147 | 0.147 | 0.147 | 1.000 | 1.000 | feasible | 0:feasible |
| tabular-adult | greedy_entropy | 1 | 0 | 8140 | 0.300 | 0.155 | 0.155 | 0.155 | 1.000 | 1.000 | feasible | 0:feasible |
| tabular-adult | random | 1 | 0 | 8140 | 0.300 | 0.155 | 0.155 | 0.155 | 1.000 | 1.000 | feasible | 0:feasible |
| tabular-adult | greedy_entropy | 2 | 0 | 8140 | 0.250 | 0.149 | 0.148 | 0.149 | 1.000 | 1.000 | feasible | 0:feasible |
| tabular-adult | random | 2 | 0 | 8140 | 0.250 | 0.149 | 0.149 | 0.149 | 1.000 | 1.000 | feasible | 0:feasible |
| tabular-MiniBooNE | greedy_entropy | 0 | 2 | 6883 | 0.200 | 0.144 | 0.146 | 0.146 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| tabular-MiniBooNE | random | 0 | 3 | 5370 | 0.200 | 0.114 | 0.114 | 0.114 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| tabular-MiniBooNE | greedy_entropy | 1 | 2 | 5377 | 0.200 | 0.160 | 0.160 | 0.160 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| tabular-MiniBooNE | random | 1 | 2 | 5447 | 0.200 | 0.113 | 0.113 | 0.113 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| tabular-MiniBooNE | greedy_entropy | 2 | 2 | 5395 | 0.200 | 0.150 | 0.151 | 0.151 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| tabular-MiniBooNE | random | 2 | 3 | 5219 | 0.200 | 0.110 | 0.110 | 0.110 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
