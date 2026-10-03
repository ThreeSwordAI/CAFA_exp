# TABLE_E3_audit (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | k | n_k | alpha | rmin_thr | rmin_depth | r_full | p_thr | p_depth | verdict | all_verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 1 | 4289 | 0.150 | 0.329 | 0.327 | 0.333 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 0 | 3 | 3305 | 0.150 | 0.241 | 0.241 | 0.241 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| csv-diabetes | greedy_entropy | 1 | 1 | 3614 | 0.150 | 0.388 | 0.386 | 0.388 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 1 | 3 | 3633 | 0.150 | 0.241 | 0.240 | 0.241 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| csv-diabetes | greedy_entropy | 2 | 1 | 4450 | 0.150 | 0.317 | 0.318 | 0.321 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 2 | 3 | 3391 | 0.150 | 0.231 | 0.229 | 0.231 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| csv-physionet | greedy_entropy | 0 | 0 | 2160 | 0.200 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 0 | 0 | 2160 | 0.200 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | greedy_entropy | 1 | 0 | 2160 | 0.200 | 0.131 | 0.125 | 0.131 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 1 | 0 | 2160 | 0.200 | 0.130 | 0.129 | 0.131 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | greedy_entropy | 2 | 0 | 2160 | 0.200 | 0.120 | 0.120 | 0.120 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 2 | 0 | 2160 | 0.200 | 0.120 | 0.119 | 0.120 | 1.000 | 1.000 | feasible | 0:feasible |
| cube | greedy_entropy | 0 | 2 | 1230 | 0.150 | 0.080 | 0.080 | 0.080 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | random | 0 | 3 | 714 | 0.150 | 0.080 | 0.083 | 0.083 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| cube | greedy_entropy | 1 | 3 | 942 | 0.150 | 0.103 | 0.103 | 0.103 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| cube | random | 1 | 3 | 763 | 0.150 | 0.104 | 0.104 | 0.104 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| cube | greedy_entropy | 2 | 2 | 1137 | 0.150 | 0.092 | 0.092 | 0.092 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | random | 2 | 4 | 840 | 0.150 | 0.088 | 0.090 | 0.090 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| fashionmnist | greedy_entropy | 0 | 4 | 2640 | 0.150 | 0.133 | 0.133 | 0.133 | 0.995 | 0.995 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| fashionmnist | random | 0 | 4 | 2852 | 0.150 | 0.129 | 0.126 | 0.129 | 0.999 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| fashionmnist | greedy_entropy | 1 | 4 | 2671 | 0.150 | 0.132 | 0.132 | 0.132 | 0.996 | 0.997 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| fashionmnist | random | 1 | 4 | 2606 | 0.150 | 0.144 | 0.144 | 0.144 | 0.830 | 0.816 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| fashionmnist | greedy_entropy | 2 | 3 | 2955 | 0.150 | 0.148 | 0.148 | 0.148 | 0.653 | 0.653 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| fashionmnist | random | 2 | 4 | 2505 | 0.150 | 0.153 | 0.153 | 0.153 | 0.330 | 0.330 | unresolved | 0:feasible 1:feasible 2:feasible 3:feasible 4:unresolved |
| image-imagenette | greedy_entropy | 0 | 3 | 498 | 0.100 | 0.078 | 0.076 | 0.078 | 0.958 | 0.971 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | random | 0 | 3 | 496 | 0.100 | 0.083 | 0.083 | 0.083 | 0.916 | 0.916 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | greedy_entropy | 1 | 3 | 518 | 0.100 | 0.077 | 0.069 | 0.077 | 0.968 | 0.994 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | random | 1 | 3 | 517 | 0.100 | 0.075 | 0.075 | 0.075 | 0.977 | 0.977 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | greedy_entropy | 2 | 3 | 458 | 0.100 | 0.074 | 0.070 | 0.074 | 0.976 | 0.990 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | random | 2 | 3 | 562 | 0.100 | 0.069 | 0.069 | 0.069 | 0.995 | 0.995 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | greedy_entropy | 0 | 2 | 4794 | 0.100 | 0.008 | 0.008 | 0.008 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| mnist | random | 0 | 4 | 2826 | 0.100 | 0.012 | 0.012 | 0.012 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | greedy_entropy | 1 | 3 | 2824 | 0.100 | 0.010 | 0.010 | 0.010 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | random | 1 | 4 | 2394 | 0.100 | 0.010 | 0.010 | 0.010 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | greedy_entropy | 2 | 4 | 3589 | 0.100 | 0.009 | 0.009 | 0.009 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | random | 2 | 4 | 2653 | 0.100 | 0.009 | 0.009 | 0.009 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| tabular-adult | greedy_entropy | 0 | 1 | 1788 | 0.250 | 0.196 | 0.196 | 0.196 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible |
| tabular-adult | random | 0 | 2 | 1860 | 0.250 | 0.254 | 0.253 | 0.254 | 0.343 | 0.403 | unresolved | 0:feasible 1:feasible 2:unresolved |
| tabular-adult | greedy_entropy | 1 | 2 | 1712 | 0.250 | 0.330 | 0.330 | 0.330 | 0.000 | 0.000 | type_II | 0:feasible 1:unresolved 2:type_II |
| tabular-adult | random | 1 | 1 | 1793 | 0.250 | 0.225 | 0.225 | 0.225 | 0.994 | 0.994 | feasible | 0:feasible 1:feasible |
| tabular-adult | greedy_entropy | 2 | 1 | 2098 | 0.200 | 0.206 | 0.203 | 0.206 | 0.257 | 0.372 | unresolved | 0:feasible 1:unresolved |
| tabular-adult | random | 2 | 2 | 1736 | 0.200 | 0.269 | 0.267 | 0.269 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:type_II |
| tabular-MiniBooNE | greedy_entropy | 0 | 2 | 6883 | 0.150 | 0.144 | 0.146 | 0.146 | 0.932 | 0.852 | feasible | 0:feasible 1:feasible 2:feasible |
| tabular-MiniBooNE | random | 0 | 3 | 4635 | 0.150 | 0.132 | 0.132 | 0.132 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| tabular-MiniBooNE | greedy_entropy | 1 | 2 | 6308 | 0.150 | 0.158 | 0.158 | 0.158 | 0.039 | 0.039 | type_II | 0:feasible 1:feasible 2:type_II |
| tabular-MiniBooNE | random | 1 | 3 | 4688 | 0.150 | 0.137 | 0.136 | 0.137 | 0.996 | 0.997 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| tabular-MiniBooNE | greedy_entropy | 2 | 2 | 5395 | 0.150 | 0.150 | 0.151 | 0.151 | 0.479 | 0.434 | unresolved | 0:feasible 1:feasible 2:unresolved |
| tabular-MiniBooNE | random | 2 | 4 | 5335 | 0.150 | 0.130 | 0.130 | 0.130 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
