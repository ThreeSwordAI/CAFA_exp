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
| csv-diabetes | greedy_entropy | 1 | budget_0.25 | 0.101 | 11.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | budget_0.5 | 0.101 | 22.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | budget_0.75 | 0.099 | 34.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | fixed_conf_0.9 | 0.100 | 9.750 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | fixed_conf_0.95 | 0.100 | 12.308 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | fixed_conf_0.99 | 0.099 | 14.343 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | full_acquisition | 0.099 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | mondrian_oracle | 0.100 | 7.362 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | oracle_cheapest_valid | 0.100 | 7.362 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 1 | oracle_stratum_safe | 0.100 | 7.362 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.100 | 7.362 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 1 | plugin | 0.122 | 5.820 | 0.210 | 0.210 | 0.000 |  |
| csv-diabetes | random | 1 | budget_0.25 | 0.167 | 11.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | budget_0.5 | 0.132 | 22.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | budget_0.75 | 0.108 | 34.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.9 | 0.119 | 16.907 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.95 | 0.106 | 20.391 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.99 | 0.100 | 27.028 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | full_acquisition | 0.099 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | mondrian_oracle | 0.162 | 7.837 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | oracle_cheapest_valid | 0.162 | 7.837 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | oracle_stratum_safe | 0.162 | 7.837 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 1 | oracle_stratum_safe_mondrian | 0.162 | 7.837 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 1 | plugin | 0.171 | 6.193 | 0.210 | 0.210 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | budget_0.25 | 0.096 | 11.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | budget_0.5 | 0.096 | 22.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | budget_0.75 | 0.095 | 34.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | fixed_conf_0.9 | 0.095 | 9.371 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | fixed_conf_0.95 | 0.095 | 11.578 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | fixed_conf_0.99 | 0.095 | 13.241 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | full_acquisition | 0.095 | 45.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | mondrian_oracle | 0.109 | 11.966 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | oracle_cheapest_valid | 0.098 | 6.915 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 2 | oracle_stratum_safe | 0.095 | 45.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.109 | 11.966 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | greedy_entropy | 2 | plugin | 0.144 | 3.869 | 1.000 | 0.440 | 1.000 |  |
| csv-diabetes | random | 2 | budget_0.25 | 0.163 | 11.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | budget_0.5 | 0.132 | 22.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | budget_0.75 | 0.107 | 34.000 | 0.400 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.9 | 0.110 | 17.245 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.95 | 0.100 | 20.749 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.99 | 0.096 | 26.009 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | full_acquisition | 0.095 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | mondrian_oracle | 0.166 | 7.699 | 0.030 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | oracle_cheapest_valid | 0.165 | 6.607 | 0.200 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | oracle_stratum_safe | 0.163 | 7.008 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 2 | oracle_stratum_safe_mondrian | 0.169 | 5.235 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 2 | plugin | 0.182 | 3.697 | 0.500 | 0.440 | 0.440 |  |
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
| csv-physionet | greedy_entropy | 1 | budget_0.25 | 0.135 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | budget_0.5 | 0.135 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | budget_0.75 | 0.130 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | fixed_conf_0.9 | 0.137 | 7.526 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | fixed_conf_0.95 | 0.135 | 14.850 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | fixed_conf_0.99 | 0.133 | 30.746 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | full_acquisition | 0.133 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | mondrian_oracle | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | oracle_cheapest_valid | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | oracle_stratum_safe | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 1 | plugin | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | budget_0.25 | 0.141 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | budget_0.5 | 0.137 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | budget_0.75 | 0.138 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | fixed_conf_0.9 | 0.135 | 13.475 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | fixed_conf_0.95 | 0.133 | 27.271 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | fixed_conf_0.99 | 0.133 | 38.353 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | full_acquisition | 0.133 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | mondrian_oracle | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | oracle_cheapest_valid | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 1 | oracle_stratum_safe | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | 1 | oracle_stratum_safe_mondrian | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | 1 | plugin | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | budget_0.25 | 0.137 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | budget_0.5 | 0.137 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | budget_0.75 | 0.132 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | fixed_conf_0.9 | 0.132 | 5.528 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | fixed_conf_0.95 | 0.126 | 13.677 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | fixed_conf_0.99 | 0.126 | 27.275 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | mondrian_oracle | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | oracle_cheapest_valid | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | oracle_stratum_safe | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 2 | plugin | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | budget_0.25 | 0.137 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | budget_0.5 | 0.137 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | budget_0.75 | 0.128 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | fixed_conf_0.9 | 0.128 | 12.315 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | fixed_conf_0.95 | 0.127 | 24.643 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | fixed_conf_0.99 | 0.127 | 36.570 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | mondrian_oracle | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | oracle_cheapest_valid | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | oracle_stratum_safe | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | 2 | oracle_stratum_safe_mondrian | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | 2 | plugin | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 |  |
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
| cube | greedy_entropy | 1 | budget_0.25 | 0.148 | 5.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | budget_0.5 | 0.063 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | budget_0.75 | 0.058 | 15.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.9 | 0.088 | 6.701 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.95 | 0.065 | 8.540 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.99 | 0.047 | 11.873 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | full_acquisition | 0.045 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | mondrian_oracle | 0.153 | 3.972 | 0.010 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | oracle_cheapest_valid | 0.198 | 3.095 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | oracle_stratum_safe | 0.141 | 4.269 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.193 | 3.317 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 1 | plugin | 0.190 | 3.195 | 1.000 | 0.120 | 1.000 |  |
| cube | random | 1 | budget_0.25 | 0.526 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 1 | budget_0.5 | 0.273 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 1 | budget_0.75 | 0.119 | 15.000 | 0.800 | 0.000 | 0.400 |  |
| cube | random | 1 | fixed_conf_0.9 | 0.074 | 12.878 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 1 | fixed_conf_0.95 | 0.056 | 14.234 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 1 | fixed_conf_0.99 | 0.045 | 16.192 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 1 | full_acquisition | 0.045 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 1 | mondrian_oracle | 0.167 | 9.269 | 0.250 | 0.000 | 0.000 |  |
| cube | random | 1 | oracle_cheapest_valid | 0.196 | 8.583 | 1.000 | 0.000 | 0.400 |  |
| cube | random | 1 | oracle_stratum_safe | 0.167 | 9.115 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 1 | oracle_stratum_safe_mondrian | 0.192 | 8.735 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 1 | plugin | 0.204 | 8.454 | 1.000 | 0.620 | 0.570 |  |
| cube | greedy_entropy | 2 | budget_0.25 | 0.136 | 5.000 | 0.200 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | budget_0.5 | 0.067 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | budget_0.75 | 0.061 | 15.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.9 | 0.086 | 6.711 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.95 | 0.063 | 8.519 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.99 | 0.047 | 11.933 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | mondrian_oracle | 0.153 | 3.864 | 0.020 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | oracle_cheapest_valid | 0.198 | 2.827 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 2 | oracle_stratum_safe | 0.154 | 3.767 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.195 | 3.168 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 2 | plugin | 0.192 | 2.926 | 1.000 | 0.190 | 0.810 |  |
| cube | random | 2 | budget_0.25 | 0.521 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 2 | budget_0.5 | 0.260 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 2 | budget_0.75 | 0.119 | 15.000 | 1.000 | 0.000 | 0.800 |  |
| cube | random | 2 | fixed_conf_0.9 | 0.071 | 12.745 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 2 | fixed_conf_0.95 | 0.055 | 14.096 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 2 | fixed_conf_0.99 | 0.047 | 16.032 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 2 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 2 | mondrian_oracle | 0.156 | 9.358 | 0.040 | 0.000 | 0.000 |  |
| cube | random | 2 | oracle_cheapest_valid | 0.194 | 8.386 | 1.000 | 0.000 | 0.400 |  |
| cube | random | 2 | oracle_stratum_safe | 0.171 | 8.808 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 2 | oracle_stratum_safe_mondrian | 0.194 | 8.462 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 2 | plugin | 0.192 | 8.429 | 0.950 | 0.260 | 0.290 |  |
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
| fashionmnist | greedy_entropy | 1 | budget_0.25 | 0.117 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | budget_0.5 | 0.084 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | budget_0.75 | 0.068 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.9 | 0.096 | 9.135 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.95 | 0.078 | 12.630 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.99 | 0.062 | 21.002 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | full_acquisition | 0.059 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | mondrian_oracle | 0.173 | 4.807 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | oracle_cheapest_valid | 0.198 | 3.738 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | oracle_stratum_safe | 0.167 | 4.575 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.196 | 4.121 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 1 | plugin | 0.196 | 3.779 | 1.000 | 0.190 | 1.000 |  |
| fashionmnist | random | 1 | budget_0.25 | 0.140 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | budget_0.5 | 0.088 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | budget_0.75 | 0.071 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.9 | 0.090 | 12.147 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.95 | 0.072 | 15.822 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.99 | 0.061 | 22.971 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | full_acquisition | 0.059 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | mondrian_oracle | 0.166 | 7.283 | 0.020 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | oracle_cheapest_valid | 0.196 | 5.174 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | oracle_stratum_safe | 0.137 | 7.783 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 1 | oracle_stratum_safe_mondrian | 0.191 | 6.199 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 1 | plugin | 0.195 | 5.197 | 1.000 | 0.200 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.25 | 0.120 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.5 | 0.087 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.75 | 0.069 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.9 | 0.097 | 9.258 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.95 | 0.078 | 12.974 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.99 | 0.061 | 21.649 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | full_acquisition | 0.058 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | mondrian_oracle | 0.172 | 5.674 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | oracle_cheapest_valid | 0.194 | 3.625 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | oracle_stratum_safe | 0.131 | 6.108 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.191 | 4.682 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 2 | plugin | 0.194 | 3.644 | 1.000 | 0.090 | 1.000 |  |
| fashionmnist | random | 2 | budget_0.25 | 0.137 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | budget_0.5 | 0.091 | 24.000 | 0.600 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | budget_0.75 | 0.068 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.9 | 0.086 | 12.717 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.95 | 0.070 | 16.240 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.99 | 0.059 | 23.171 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | full_acquisition | 0.058 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | mondrian_oracle | 0.167 | 7.553 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | oracle_cheapest_valid | 0.197 | 5.204 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | oracle_stratum_safe | 0.131 | 8.333 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 2 | oracle_stratum_safe_mondrian | 0.191 | 6.441 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 2 | plugin | 0.196 | 5.272 | 1.000 | 0.230 | 1.000 |  |
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
| image-imagenette | greedy_entropy | 1 | budget_0.25 | 0.119 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | greedy_entropy | 1 | budget_0.5 | 0.058 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | budget_0.75 | 0.037 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | fixed_conf_0.9 | 0.079 | 9.048 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | fixed_conf_0.95 | 0.054 | 11.110 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | fixed_conf_0.99 | 0.037 | 16.456 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | full_acquisition | 0.032 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | mondrian_oracle | 0.111 | 7.641 | 0.210 | 0.000 | 0.020 |  |
| image-imagenette | greedy_entropy | 1 | oracle_cheapest_valid | 0.146 | 6.058 | 1.000 | 0.000 | 0.600 |  |
| image-imagenette | greedy_entropy | 1 | oracle_stratum_safe | 0.127 | 6.628 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.147 | 6.247 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 1 | plugin | 0.151 | 5.915 | 0.890 | 0.640 | 0.610 |  |
| image-imagenette | random | 1 | budget_0.25 | 0.106 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | random | 1 | budget_0.5 | 0.058 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | budget_0.75 | 0.039 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | fixed_conf_0.9 | 0.084 | 8.128 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | fixed_conf_0.95 | 0.055 | 10.459 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | fixed_conf_0.99 | 0.035 | 15.618 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | full_acquisition | 0.032 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | mondrian_oracle | 0.111 | 6.899 | 0.090 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | oracle_cheapest_valid | 0.146 | 5.037 | 1.000 | 0.000 | 0.800 |  |
| image-imagenette | random | 1 | oracle_stratum_safe | 0.114 | 6.316 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 1 | oracle_stratum_safe_mondrian | 0.147 | 5.432 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 1 | plugin | 0.151 | 4.914 | 1.000 | 0.540 | 0.930 |  |
| image-imagenette | greedy_entropy | 2 | budget_0.25 | 0.115 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | greedy_entropy | 2 | budget_0.5 | 0.059 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | budget_0.75 | 0.035 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | fixed_conf_0.9 | 0.076 | 9.167 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | fixed_conf_0.95 | 0.053 | 11.472 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | fixed_conf_0.99 | 0.033 | 16.566 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | full_acquisition | 0.028 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | mondrian_oracle | 0.120 | 7.156 | 0.130 | 0.030 | 0.030 |  |
| image-imagenette | greedy_entropy | 2 | oracle_cheapest_valid | 0.146 | 6.158 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | greedy_entropy | 2 | oracle_stratum_safe | 0.127 | 6.754 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.148 | 6.316 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 2 | plugin | 0.150 | 6.042 | 0.850 | 0.510 | 0.570 |  |
| image-imagenette | random | 2 | budget_0.25 | 0.102 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | random | 2 | budget_0.5 | 0.053 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | budget_0.75 | 0.036 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | fixed_conf_0.9 | 0.072 | 8.081 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | fixed_conf_0.95 | 0.052 | 10.278 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | fixed_conf_0.99 | 0.031 | 15.452 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | full_acquisition | 0.028 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | mondrian_oracle | 0.111 | 6.445 | 0.090 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | oracle_cheapest_valid | 0.148 | 4.552 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | random | 2 | oracle_stratum_safe | 0.108 | 5.951 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 2 | oracle_stratum_safe_mondrian | 0.147 | 5.014 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 2 | plugin | 0.146 | 4.612 | 1.000 | 0.400 | 0.940 |  |
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
| mnist | greedy_entropy | 1 | budget_0.25 | 0.027 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | budget_0.5 | 0.017 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | budget_0.75 | 0.010 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | fixed_conf_0.9 | 0.047 | 4.642 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | fixed_conf_0.95 | 0.028 | 5.936 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | fixed_conf_0.99 | 0.011 | 10.390 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | full_acquisition | 0.005 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | mondrian_oracle | 0.126 | 3.168 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | oracle_cheapest_valid | 0.147 | 2.996 | 1.000 | 0.000 | 1.000 |  |
| mnist | greedy_entropy | 1 | oracle_stratum_safe | 0.116 | 3.279 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.145 | 2.999 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 1 | plugin | 0.148 | 2.988 | 1.000 | 0.350 | 1.000 |  |
| mnist | random | 1 | budget_0.25 | 0.114 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| mnist | random | 1 | budget_0.5 | 0.024 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | budget_0.75 | 0.009 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | fixed_conf_0.9 | 0.049 | 9.781 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | fixed_conf_0.95 | 0.028 | 11.525 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | fixed_conf_0.99 | 0.009 | 15.524 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | full_acquisition | 0.005 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | mondrian_oracle | 0.124 | 7.214 | 0.180 | 0.000 | 0.010 |  |
| mnist | random | 1 | oracle_cheapest_valid | 0.147 | 6.689 | 1.000 | 0.000 | 0.200 |  |
| mnist | random | 1 | oracle_stratum_safe | 0.135 | 6.948 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 1 | oracle_stratum_safe_mondrian | 0.146 | 6.712 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 1 | plugin | 0.150 | 6.623 | 0.960 | 0.600 | 0.510 |  |
| mnist | greedy_entropy | 2 | budget_0.25 | 0.034 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | budget_0.5 | 0.021 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | budget_0.75 | 0.011 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | fixed_conf_0.9 | 0.054 | 5.133 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | fixed_conf_0.95 | 0.030 | 6.915 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | fixed_conf_0.99 | 0.011 | 11.579 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | full_acquisition | 0.005 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | mondrian_oracle | 0.126 | 3.381 | 0.030 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | oracle_cheapest_valid | 0.148 | 3.136 | 1.000 | 0.000 | 1.000 |  |
| mnist | greedy_entropy | 2 | oracle_stratum_safe | 0.113 | 3.561 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.147 | 3.156 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 2 | plugin | 0.148 | 3.134 | 1.000 | 0.320 | 1.000 |  |
| mnist | random | 2 | budget_0.25 | 0.119 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| mnist | random | 2 | budget_0.5 | 0.027 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | budget_0.75 | 0.009 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | fixed_conf_0.9 | 0.053 | 9.749 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | fixed_conf_0.95 | 0.030 | 11.481 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | fixed_conf_0.99 | 0.010 | 15.409 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | full_acquisition | 0.005 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | mondrian_oracle | 0.123 | 7.366 | 0.070 | 0.000 | 0.000 |  |
| mnist | random | 2 | oracle_cheapest_valid | 0.148 | 6.807 | 1.000 | 0.000 | 0.400 |  |
| mnist | random | 2 | oracle_stratum_safe | 0.133 | 7.123 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 2 | oracle_stratum_safe_mondrian | 0.147 | 6.805 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 2 | plugin | 0.148 | 6.795 | 0.860 | 0.360 | 0.490 |  |
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
| tabular-adult | greedy_entropy | 1 | budget_0.25 | 0.189 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | budget_0.5 | 0.185 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | budget_0.75 | 0.177 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.9 | 0.159 | 6.381 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.95 | 0.154 | 8.424 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.99 | 0.151 | 12.064 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | full_acquisition | 0.151 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | mondrian_oracle | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | oracle_cheapest_valid | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | oracle_stratum_safe | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 1 | plugin | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | budget_0.25 | 0.206 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | budget_0.5 | 0.180 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | budget_0.75 | 0.162 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.9 | 0.157 | 7.737 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.95 | 0.152 | 9.551 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.99 | 0.151 | 12.072 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | full_acquisition | 0.151 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | mondrian_oracle | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | oracle_cheapest_valid | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | oracle_stratum_safe | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 1 | oracle_stratum_safe_mondrian | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 1 | plugin | 0.253 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.25 | 0.202 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.5 | 0.185 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.75 | 0.158 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.9 | 0.153 | 7.118 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.95 | 0.148 | 8.708 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.99 | 0.146 | 11.890 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | full_acquisition | 0.146 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | mondrian_oracle | 0.184 | 2.662 | 0.020 | 0.020 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | oracle_cheapest_valid | 0.235 | 0.541 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | oracle_stratum_safe | 0.235 | 0.541 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.235 | 0.541 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 2 | plugin | 0.225 | 0.951 | 0.200 | 0.200 | 0.000 |  |
| tabular-adult | random | 2 | budget_0.25 | 0.204 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | budget_0.5 | 0.173 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | budget_0.75 | 0.159 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.9 | 0.150 | 8.007 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.95 | 0.148 | 9.719 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.99 | 0.146 | 12.158 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | full_acquisition | 0.146 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | mondrian_oracle | 0.186 | 3.303 | 0.020 | 0.020 | 0.000 |  |
| tabular-adult | random | 2 | oracle_cheapest_valid | 0.234 | 0.679 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | oracle_stratum_safe | 0.234 | 0.679 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 2 | oracle_stratum_safe_mondrian | 0.234 | 0.679 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 2 | plugin | 0.226 | 1.175 | 0.200 | 0.200 | 0.000 |  |
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
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.25 | 0.109 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.5 | 0.088 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.75 | 0.082 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.9 | 0.093 | 9.719 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.95 | 0.081 | 16.326 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.99 | 0.077 | 28.213 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | mondrian_oracle | 0.133 | 4.931 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_cheapest_valid | 0.152 | 2.682 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_stratum_safe | 0.103 | 6.984 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.136 | 4.159 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 1 | plugin | 0.152 | 2.682 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | budget_0.25 | 0.158 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | budget_0.5 | 0.110 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | budget_0.75 | 0.089 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.9 | 0.099 | 15.252 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.95 | 0.084 | 22.510 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.99 | 0.077 | 34.065 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | mondrian_oracle | 0.179 | 5.138 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | oracle_cheapest_valid | 0.192 | 4.157 | 1.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | oracle_stratum_safe | 0.179 | 4.899 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 1 | oracle_stratum_safe_mondrian | 0.195 | 3.891 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 1 | plugin | 0.193 | 4.129 | 0.980 | 0.070 | 0.070 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.25 | 0.102 | 12.000 | 0.400 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.5 | 0.092 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.75 | 0.084 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.9 | 0.090 | 11.404 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.95 | 0.081 | 18.347 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.99 | 0.079 | 29.477 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | full_acquisition | 0.080 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | mondrian_oracle | 0.132 | 3.570 | 0.030 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_cheapest_valid | 0.141 | 2.427 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_stratum_safe | 0.108 | 4.962 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.135 | 2.889 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 2 | plugin | 0.141 | 2.427 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.25 | 0.157 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.5 | 0.112 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.75 | 0.092 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.9 | 0.093 | 17.081 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.95 | 0.084 | 23.789 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.99 | 0.080 | 34.609 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | full_acquisition | 0.080 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | mondrian_oracle | 0.175 | 5.144 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | oracle_cheapest_valid | 0.188 | 4.137 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | oracle_stratum_safe | 0.160 | 5.717 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 2 | oracle_stratum_safe_mondrian | 0.188 | 4.323 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 2 | plugin | 0.190 | 4.043 | 1.000 | 0.130 | 1.000 |  |
