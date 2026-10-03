# TABLE_E3_audit (lambda_ref key = 0.9, scheme = uniform)

| dataset | policy | seed | k | n_k | alpha | rmin_thr | rmin_depth | r_full | p_thr | p_depth | verdict | all_verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 1 | 3286 | 0.150 | 0.401 | 0.396 | 0.402 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 0 | 4 | 3310 | 0.150 | 0.357 | 0.357 | 0.357 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| csv-diabetes | greedy_entropy | 1 | 1 | 3447 | 0.150 | 0.404 | 0.403 | 0.404 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 1 | 4 | 3624 | 0.150 | 0.347 | 0.347 | 0.347 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| csv-diabetes | greedy_entropy | 2 | 1 | 3275 | 0.150 | 0.399 | 0.399 | 0.399 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 2 | 4 | 3235 | 0.150 | 0.370 | 0.370 | 0.370 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| csv-physionet | greedy_entropy | 0 | 1 | 910 | 0.200 | 0.188 | 0.188 | 0.188 | 0.830 | 0.830 | feasible | 0:feasible 1:feasible |
| csv-physionet | random | 0 | 1 | 938 | 0.200 | 0.184 | 0.187 | 0.187 | 0.892 | 0.858 | feasible | 0:feasible 1:feasible |
| csv-physionet | greedy_entropy | 1 | 1 | 1061 | 0.200 | 0.183 | 0.170 | 0.187 | 0.926 | 0.995 | feasible | 0:feasible 1:feasible |
| csv-physionet | random | 1 | 1 | 1252 | 0.200 | 0.155 | 0.155 | 0.157 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible |
| csv-physionet | greedy_entropy | 2 | 1 | 1107 | 0.200 | 0.144 | 0.144 | 0.144 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible |
| csv-physionet | random | 2 | 1 | 1403 | 0.200 | 0.133 | 0.133 | 0.135 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible |
| cube | greedy_entropy | 0 | 3 | 717 | 0.150 | 0.165 | 0.165 | 0.165 | 0.149 | 0.149 | unresolved | 0:feasible 1:feasible 2:feasible 3:unresolved |
| cube | random | 0 | 3 | 740 | 0.150 | 0.145 | 0.147 | 0.147 | 0.675 | 0.597 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| cube | greedy_entropy | 1 | 3 | 720 | 0.150 | 0.149 | 0.149 | 0.149 | 0.557 | 0.557 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| cube | random | 1 | 3 | 765 | 0.150 | 0.127 | 0.127 | 0.127 | 0.970 | 0.970 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| cube | greedy_entropy | 2 | 2 | 732 | 0.150 | 0.161 | 0.161 | 0.161 | 0.211 | 0.211 | unresolved | 0:feasible 1:feasible 2:unresolved |
| cube | random | 2 | 4 | 764 | 0.150 | 0.154 | 0.156 | 0.156 | 0.380 | 0.343 | unresolved | 0:feasible 1:feasible 2:feasible 3:feasible 4:unresolved |
| fashionmnist | greedy_entropy | 0 | 4 | 2644 | 0.150 | 0.162 | 0.161 | 0.162 | 0.047 | 0.059 | thr_failure_depth_unresolved | 0:feasible 1:feasible 2:feasible 3:feasible 4:thr_failure_depth_unresolved |
| fashionmnist | random | 0 | 4 | 2654 | 0.150 | 0.171 | 0.170 | 0.171 | 0.002 | 0.003 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | greedy_entropy | 1 | 4 | 2542 | 0.150 | 0.175 | 0.175 | 0.175 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | random | 1 | 4 | 2591 | 0.150 | 0.188 | 0.188 | 0.188 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | greedy_entropy | 2 | 4 | 2444 | 0.150 | 0.183 | 0.183 | 0.183 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| fashionmnist | random | 2 | 4 | 2530 | 0.150 | 0.193 | 0.193 | 0.193 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| image-imagenette | greedy_entropy | 0 | 4 | 442 | 0.100 | 0.093 | 0.093 | 0.093 | 0.717 | 0.717 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| image-imagenette | random | 0 | 3 | 459 | 0.100 | 0.092 | 0.092 | 0.092 | 0.750 | 0.750 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | greedy_entropy | 1 | 3 | 515 | 0.100 | 0.091 | 0.087 | 0.091 | 0.766 | 0.848 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | random | 1 | 3 | 606 | 0.100 | 0.074 | 0.074 | 0.074 | 0.988 | 0.988 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | greedy_entropy | 2 | 3 | 465 | 0.100 | 0.075 | 0.073 | 0.075 | 0.972 | 0.981 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | random | 2 | 3 | 560 | 0.100 | 0.071 | 0.071 | 0.071 | 0.992 | 0.992 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | greedy_entropy | 0 | 3 | 2937 | 0.100 | 0.013 | 0.013 | 0.013 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | random | 0 | 4 | 2686 | 0.100 | 0.013 | 0.013 | 0.013 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | greedy_entropy | 1 | 4 | 3195 | 0.100 | 0.011 | 0.011 | 0.011 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | random | 1 | 4 | 2733 | 0.100 | 0.013 | 0.013 | 0.013 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | greedy_entropy | 2 | 4 | 2651 | 0.100 | 0.014 | 0.014 | 0.014 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| mnist | random | 2 | 4 | 2707 | 0.100 | 0.011 | 0.011 | 0.011 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| tabular-adult | greedy_entropy | 0 | 2 | 3261 | 0.250 | 0.292 | 0.291 | 0.292 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:type_II |
| tabular-adult | random | 0 | 2 | 3036 | 0.250 | 0.302 | 0.303 | 0.303 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:type_II |
| tabular-adult | greedy_entropy | 1 | 1 | 3290 | 0.250 | 0.305 | 0.305 | 0.305 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| tabular-adult | random | 1 | 3 | 2886 | 0.250 | 0.328 | 0.328 | 0.328 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| tabular-adult | greedy_entropy | 2 | 3 | 2774 | 0.200 | 0.323 | 0.321 | 0.323 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| tabular-adult | random | 2 | 3 | 3125 | 0.200 | 0.317 | 0.317 | 0.317 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| tabular-MiniBooNE | greedy_entropy | 0 | 4 | 4843 | 0.150 | 0.195 | 0.195 | 0.195 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | random | 0 | 4 | 4803 | 0.150 | 0.198 | 0.198 | 0.198 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | greedy_entropy | 1 | 4 | 4789 | 0.150 | 0.203 | 0.203 | 0.203 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | random | 1 | 4 | 4689 | 0.150 | 0.192 | 0.192 | 0.192 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | greedy_entropy | 2 | 4 | 4692 | 0.150 | 0.209 | 0.209 | 0.209 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | random | 2 | 4 | 4673 | 0.150 | 0.209 | 0.209 | 0.209 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
