# TABLE_E4_cascade (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | alpha | G | lambda_ref | marginal_cost | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | delta | deepest_verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 0.150 | 2 | 0.798 | 6.879 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 45.000 | 6.542 | 0.822 | 0.000 | 0.100 | type_II |
| csv-diabetes | random | 0 | 0.150 | 4 | 0.828 | 11.402 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 45.000 | 3.947 | 0.890 | 0.010 | 0.100 | type_II |
| csv-physionet | greedy_entropy | 0 | 0.200 | 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.100 | feasible |
| csv-physionet | random | 0 | 0.200 | 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.100 | feasible |
| cube | greedy_entropy | 0 | 0.150 | 3 | 0.798 | 4.167 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 5.781 | 1.387 | 1.000 | 0.000 | 0.100 | feasible |
| cube | random | 0 | 0.150 | 4 | 0.707 | 9.942 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 11.469 | 1.154 | 1.000 | 0.000 | 0.100 | feasible |
| fashionmnist | greedy_entropy | 0 | 0.150 | 5 | 0.778 | 5.413 | 0.350 | 0.000 | 0.650 | 0.000 | 1.000 | 39.073 | 7.219 | 0.987 | 0.350 | 0.100 | feasible |
| fashionmnist | random | 0 | 0.150 | 5 | 0.778 | 7.900 | 0.580 | 0.000 | 0.420 | 0.000 | 1.000 | 31.990 | 4.050 | 0.995 | 0.580 | 0.100 | feasible |
| mnist | greedy_entropy | 0 | 0.100 | 3 | 0.788 | 3.495 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.662 | 1.048 | 1.000 | 0.000 | 0.100 | feasible |
| mnist | random | 0 | 0.100 | 5 | 0.788 | 8.257 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 9.126 | 1.105 | 1.000 | 0.000 | 0.100 | feasible |
| tabular-adult | greedy_entropy | 0 | 0.250 | 2 | 0.758 | 2.379 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 2.903 | 1.220 | 1.000 | 0.000 | 0.100 | feasible |
| tabular-adult | random | 0 | 0.250 | 3 | 0.758 | 3.489 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 4.012 | 0.897 | 0.000 | 0.100 | unresolved |
| tabular-MiniBooNE | greedy_entropy | 0 | 0.150 | 3 | 0.747 | 3.047 | 0.040 | 0.000 | 0.960 | 0.000 | 1.000 | 48.658 | 15.967 | 0.973 | 0.110 | 0.100 | feasible |
| tabular-MiniBooNE | random | 0 | 0.150 | 4 | 0.778 | 7.672 | 0.730 | 0.000 | 0.270 | 0.000 | 1.000 | 27.524 | 3.588 | 0.996 | 0.120 | 0.100 | feasible |
