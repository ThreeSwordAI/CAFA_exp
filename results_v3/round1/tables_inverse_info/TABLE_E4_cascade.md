# TABLE_E4_cascade (lambda_ref key = dep, scheme = inverse_info)

| dataset | policy | seed | alpha | G | lambda_ref | marginal_cost | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | delta | deepest_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 0.150 | 2 | 0.798 | 54.498 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 406.131 | 7.452 | 0.822 | 0.000 | 0.100 | type_II |
| csv-diabetes | random | 0 | 0.150 | 4 | 0.828 | 102.492 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 406.131 | 3.963 | 0.890 | 0.010 | 0.100 | type_II |
| csv-physionet | greedy_entropy | 0 | 0.200 | 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.100 | feasible |
| csv-physionet | random | 0 | 0.200 | 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.100 | feasible |
| cube | greedy_entropy | 0 | 0.150 | 3 | 0.798 | 11.242 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 21.240 | 1.889 | 1.000 | 0.000 | 0.100 | feasible |
| cube | random | 0 | 0.150 | 4 | 0.707 | 63.753 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 73.632 | 1.155 | 1.000 | 0.000 | 0.100 | feasible |
| tabular-adult | greedy_entropy | 0 | 0.250 | 2 | 0.758 | 18.585 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 21.753 | 1.170 | 1.000 | 0.000 | 0.100 | feasible |
| tabular-adult | random | 0 | 0.250 | 3 | 0.758 | 23.740 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 95.278 | 4.013 | 0.897 | 0.000 | 0.100 | unresolved |
| tabular-MiniBooNE | greedy_entropy | 0 | 0.150 | 3 | 0.747 | 14.421 | 0.040 | 0.000 | 0.960 | 0.000 | 1.000 | 331.566 | 22.993 | 0.973 | 0.110 | 0.100 | feasible |
| tabular-MiniBooNE | random | 0 | 0.150 | 4 | 0.778 | 52.130 | 0.730 | 0.000 | 0.270 | 0.000 | 1.000 | 187.488 | 3.597 | 0.996 | 0.120 | 0.100 | feasible |
