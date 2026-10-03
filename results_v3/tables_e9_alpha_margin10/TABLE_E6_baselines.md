# TABLE_E6_baselines (lambda_ref key = dep, scheme = uniform)

| dataset | policy | seed | baseline | mean_test_risk | mean_test_cost | stratum_violation_rate | aggregate_violation_rate | stratum_certified_violation_rate | feasible_rate |
|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | budget_0.25 | 0.095 | 11.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | budget_0.5 | 0.095 | 22.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | budget_0.75 | 0.095 | 34.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.9 | 0.096 | 9.496 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.95 | 0.096 | 12.179 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.99 | 0.096 | 13.218 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | full_acquisition | 0.096 | 45.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | mondrian_oracle | 0.114 | 11.650 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | oracle_cheapest_valid | 0.099 | 6.915 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 0 | oracle_stratum_safe | 0.096 | 45.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.114 | 11.650 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | greedy_entropy | 0 | plugin | 0.159 | 2.902 | 1.000 | 0.580 | 1.000 |  |
| csv-diabetes | random | 0 | budget_0.25 | 0.164 | 11.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | budget_0.5 | 0.131 | 22.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | budget_0.75 | 0.107 | 34.000 | 0.800 | 0.000 | 0.200 |  |
| csv-diabetes | random | 0 | fixed_conf_0.9 | 0.117 | 16.332 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | fixed_conf_0.95 | 0.103 | 19.841 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | fixed_conf_0.99 | 0.098 | 24.320 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | full_acquisition | 0.096 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | mondrian_oracle | 0.163 | 9.228 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | oracle_cheapest_valid | 0.165 | 6.978 | 1.000 | 0.000 | 0.600 |  |
| csv-diabetes | random | 0 | oracle_stratum_safe | 0.137 | 12.422 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | oracle_stratum_safe_mondrian | 0.166 | 6.120 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | plugin | 0.186 | 2.922 | 1.000 | 0.580 | 0.850 |  |
| csv-physionet | greedy_entropy | 0 | budget_0.25 | 0.141 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | budget_0.5 | 0.136 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | budget_0.75 | 0.128 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.9 | 0.132 | 7.622 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.95 | 0.128 | 14.584 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.99 | 0.127 | 27.377 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | mondrian_oracle | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | oracle_cheapest_valid | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | oracle_stratum_safe | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 0 | plugin | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | budget_0.25 | 0.144 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | budget_0.5 | 0.138 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | budget_0.75 | 0.136 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | fixed_conf_0.9 | 0.133 | 12.147 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | fixed_conf_0.95 | 0.129 | 24.435 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | fixed_conf_0.99 | 0.127 | 36.329 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | mondrian_oracle | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | oracle_cheapest_valid | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | oracle_stratum_safe | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | 0 | oracle_stratum_safe_mondrian | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | 0 | plugin | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | budget_0.25 | 0.133 | 5.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | budget_0.5 | 0.069 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | budget_0.75 | 0.059 | 15.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | fixed_conf_0.9 | 0.085 | 6.589 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | fixed_conf_0.95 | 0.063 | 8.354 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | fixed_conf_0.99 | 0.048 | 11.685 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | mondrian_oracle | 0.157 | 3.702 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | oracle_cheapest_valid | 0.198 | 2.920 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 0 | oracle_stratum_safe | 0.140 | 3.994 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.195 | 3.159 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 0 | plugin | 0.192 | 2.960 | 1.000 | 0.090 | 1.000 |  |
| cube | random | 0 | budget_0.25 | 0.531 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 0 | budget_0.5 | 0.274 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 0 | budget_0.75 | 0.119 | 15.000 | 1.000 | 0.000 | 0.000 |  |
| cube | random | 0 | fixed_conf_0.9 | 0.076 | 12.820 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 0 | fixed_conf_0.95 | 0.058 | 14.195 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 0 | fixed_conf_0.99 | 0.047 | 16.120 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 0 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 0 | mondrian_oracle | 0.165 | 9.317 | 0.030 | 0.000 | 0.000 |  |
| cube | random | 0 | oracle_cheapest_valid | 0.197 | 8.418 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 0 | oracle_stratum_safe | 0.165 | 9.080 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 0 | oracle_stratum_safe_mondrian | 0.195 | 8.643 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 0 | plugin | 0.202 | 8.326 | 1.000 | 0.600 | 0.970 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.25 | 0.117 | 12.000 | 0.800 | 0.000 | 0.400 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.5 | 0.079 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.75 | 0.065 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.091 | 9.031 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.073 | 12.621 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.060 | 20.979 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | full_acquisition | 0.058 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | mondrian_oracle | 0.170 | 4.799 | 0.010 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.198 | 3.308 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | oracle_stratum_safe | 0.139 | 5.267 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.197 | 4.108 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 0 | plugin | 0.191 | 3.444 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | budget_0.25 | 0.141 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | budget_0.5 | 0.090 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | budget_0.75 | 0.069 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.9 | 0.089 | 12.345 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.95 | 0.071 | 15.923 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.99 | 0.059 | 23.110 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | full_acquisition | 0.058 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | mondrian_oracle | 0.168 | 7.079 | 0.040 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | oracle_cheapest_valid | 0.198 | 5.191 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | oracle_stratum_safe | 0.151 | 7.252 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 0 | oracle_stratum_safe_mondrian | 0.192 | 6.070 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 0 | plugin | 0.196 | 5.301 | 1.000 | 0.170 | 1.000 |  |
| image-imagenette | greedy_entropy | 0 | budget_0.25 | 0.104 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | greedy_entropy | 0 | budget_0.5 | 0.062 | 24.000 | 0.200 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | budget_0.75 | 0.041 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.9 | 0.087 | 7.765 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.95 | 0.060 | 10.097 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.99 | 0.036 | 15.312 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | full_acquisition | 0.030 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | mondrian_oracle | 0.109 | 7.453 | 0.110 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | oracle_cheapest_valid | 0.147 | 4.976 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | greedy_entropy | 0 | oracle_stratum_safe | 0.107 | 6.556 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.147 | 5.549 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 0 | plugin | 0.144 | 5.090 | 1.000 | 0.380 | 0.880 |  |
| image-imagenette | random | 0 | budget_0.25 | 0.110 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | random | 0 | budget_0.5 | 0.055 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | budget_0.75 | 0.034 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | fixed_conf_0.9 | 0.077 | 8.154 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | fixed_conf_0.95 | 0.053 | 10.445 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | fixed_conf_0.99 | 0.035 | 15.633 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | full_acquisition | 0.030 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | mondrian_oracle | 0.110 | 6.439 | 0.070 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | oracle_cheapest_valid | 0.149 | 4.581 | 1.000 | 0.000 | 0.800 |  |
| image-imagenette | random | 0 | oracle_stratum_safe | 0.125 | 5.419 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 0 | oracle_stratum_safe_mondrian | 0.148 | 4.930 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 0 | plugin | 0.145 | 4.689 | 0.940 | 0.280 | 0.470 |  |
| mnist | greedy_entropy | 0 | budget_0.25 | 0.027 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | budget_0.5 | 0.016 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | budget_0.75 | 0.010 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.046 | 4.608 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.026 | 5.957 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.011 | 10.331 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | full_acquisition | 0.006 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | mondrian_oracle | 0.126 | 3.127 | 0.010 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.149 | 2.912 | 1.000 | 0.000 | 1.000 |  |
| mnist | greedy_entropy | 0 | oracle_stratum_safe | 0.130 | 3.076 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.147 | 2.912 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 0 | plugin | 0.146 | 2.933 | 1.000 | 0.160 | 0.710 |  |
| mnist | random | 0 | budget_0.25 | 0.115 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| mnist | random | 0 | budget_0.5 | 0.025 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | budget_0.75 | 0.009 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | fixed_conf_0.9 | 0.055 | 9.741 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | fixed_conf_0.95 | 0.031 | 11.456 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | fixed_conf_0.99 | 0.010 | 15.352 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | full_acquisition | 0.006 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | mondrian_oracle | 0.122 | 7.348 | 0.010 | 0.000 | 0.000 |  |
| mnist | random | 0 | oracle_cheapest_valid | 0.148 | 6.741 | 1.000 | 0.000 | 0.400 |  |
| mnist | random | 0 | oracle_stratum_safe | 0.133 | 7.094 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 0 | oracle_stratum_safe_mondrian | 0.147 | 6.767 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 0 | plugin | 0.146 | 6.786 | 1.000 | 0.220 | 0.370 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.25 | 0.216 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.5 | 0.181 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.75 | 0.158 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.9 | 0.151 | 7.320 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.95 | 0.149 | 8.469 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.99 | 0.147 | 11.556 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | full_acquisition | 0.147 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | mondrian_oracle | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | oracle_cheapest_valid | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | oracle_stratum_safe | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 0 | plugin | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | budget_0.25 | 0.206 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | budget_0.5 | 0.181 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | budget_0.75 | 0.160 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.9 | 0.151 | 7.943 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.95 | 0.149 | 9.583 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.99 | 0.147 | 11.953 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | full_acquisition | 0.147 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | mondrian_oracle | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | oracle_cheapest_valid | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | oracle_stratum_safe | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 0 | oracle_stratum_safe_mondrian | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 0 | plugin | 0.247 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.25 | 0.110 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.5 | 0.092 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.75 | 0.085 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.9 | 0.090 | 10.580 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.95 | 0.081 | 16.828 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.99 | 0.078 | 28.661 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | mondrian_oracle | 0.111 | 5.549 | 0.010 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | oracle_cheapest_valid | 0.130 | 3.070 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | oracle_stratum_safe | 0.103 | 6.416 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.116 | 4.714 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | plugin | 0.130 | 3.070 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | budget_0.25 | 0.155 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | budget_0.5 | 0.108 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | budget_0.75 | 0.090 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.9 | 0.093 | 16.647 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.95 | 0.082 | 23.538 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.99 | 0.077 | 35.213 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | mondrian_oracle | 0.173 | 5.272 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | oracle_cheapest_valid | 0.173 | 5.186 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | oracle_stratum_safe | 0.173 | 5.186 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | oracle_stratum_safe_mondrian | 0.178 | 4.829 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | plugin | 0.173 | 5.186 | 0.000 | 0.000 | 0.000 |  |
