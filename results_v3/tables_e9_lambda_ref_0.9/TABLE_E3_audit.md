# TABLE_E3_audit (lambda_ref key = 0.9, scheme = uniform)

| dataset | policy | seed | k | n_k | alpha | rmin_thr | rmin_depth | r_full | p_thr | p_depth | verdict | all_verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 1 | 3286 | 0.150 | 0.401 | 0.396 | 0.402 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 0 | 4 | 3310 | 0.150 | 0.357 | 0.357 | 0.357 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| csv-physionet | greedy_entropy | 0 | 1 | 910 | 0.200 | 0.188 | 0.188 | 0.188 | 0.830 | 0.830 | feasible | 0:feasible 1:feasible |
| csv-physionet | random | 0 | 1 | 938 | 0.200 | 0.184 | 0.187 | 0.187 | 0.892 | 0.858 | feasible | 0:feasible 1:feasible |
| cube | greedy_entropy | 0 | 3 | 717 | 0.150 | 0.165 | 0.165 | 0.165 | 0.149 | 0.149 | unresolved | 0:feasible 1:feasible 2:feasible 3:unresolved |
| cube | random | 0 | 3 | 740 | 0.150 | 0.145 | 0.147 | 0.147 | 0.675 | 0.597 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| fashionmnist | greedy_entropy | 0 | 4 | 2644 | 0.150 | 0.162 | 0.161 | 0.162 | 0.047 | 0.059 | thr_failure_depth_unresolved | 0:feasible 1:feasible 2:feasible 3:feasible 4:thr_failure_depth_unresolved |
| fashionmnist | random | 0 | 4 | 2654 | 0.150 | 0.171 | 0.170 | 0.171 | 0.002 | 0.003 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| mnist | greedy_entropy | 0 | 3 | 2937 | 0.100 | 0.013 | 0.013 | 0.013 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | random | 0 | 4 | 2686 | 0.100 | 0.013 | 0.013 | 0.013 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| tabular-adult | greedy_entropy | 0 | 2 | 3261 | 0.250 | 0.292 | 0.291 | 0.292 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:type_II |
| tabular-adult | random | 0 | 2 | 3036 | 0.250 | 0.302 | 0.303 | 0.303 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:type_II |
| tabular-MiniBooNE | greedy_entropy | 0 | 4 | 4843 | 0.150 | 0.195 | 0.195 | 0.195 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
| tabular-MiniBooNE | random | 0 | 4 | 4803 | 0.150 | 0.198 | 0.198 | 0.198 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:feasible 4:type_II |
