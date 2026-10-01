# TABLE_E3_audit (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | k | n_k | alpha | rmin_thr | rmin_depth | r_full | p_thr | p_depth | verdict | all_verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 1 | 4289 | 0.150 | 0.329 | 0.327 | 0.333 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 0 | 3 | 3305 | 0.150 | 0.241 | 0.241 | 0.241 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| csv-physionet | greedy_entropy | 0 | 0 | 2160 | 0.200 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 0 | 0 | 2160 | 0.200 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible |
| cube | greedy_entropy | 0 | 2 | 1230 | 0.150 | 0.080 | 0.080 | 0.080 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | random | 0 | 3 | 714 | 0.150 | 0.080 | 0.083 | 0.083 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | greedy_entropy | 0 | 2 | 4794 | 0.100 | 0.008 | 0.008 | 0.008 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| mnist | random | 0 | 4 | 2826 | 0.100 | 0.012 | 0.012 | 0.012 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| tabular-adult | greedy_entropy | 0 | 1 | 1788 | 0.250 | 0.196 | 0.196 | 0.196 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible |
| tabular-adult | random | 0 | 2 | 1860 | 0.250 | 0.254 | 0.253 | 0.254 | 0.343 | 0.403 | unresolved | 0:feasible 1:feasible 2:unresolved |
| tabular-MiniBooNE | greedy_entropy | 0 | 2 | 6883 | 0.150 | 0.144 | 0.146 | 0.146 | 0.932 | 0.852 | feasible | 0:feasible 1:feasible 2:feasible |
| tabular-MiniBooNE | random | 0 | 3 | 4635 | 0.150 | 0.132 | 0.132 | 0.132 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
