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
| csv-diabetes | greedy_entropy | 0 | plugin | 0.099 | 6.915 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | budget_0.25 | 0.164 | 11.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 0 | budget_0.5 | 0.131 | 22.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 0 | budget_0.75 | 0.107 | 34.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | fixed_conf_0.9 | 0.117 | 16.332 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | fixed_conf_0.95 | 0.103 | 19.841 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | fixed_conf_0.99 | 0.098 | 24.320 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | full_acquisition | 0.096 | 45.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | mondrian_oracle | 0.126 | 11.774 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 0 | oracle_cheapest_valid | 0.117 | 16.332 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 0 | plugin | 0.119 | 16.076 | 1.000 | 0.440 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | budget_0.25 | 0.101 | 11.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | budget_0.5 | 0.101 | 22.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | budget_0.75 | 0.099 | 34.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | fixed_conf_0.9 | 0.100 | 9.750 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | fixed_conf_0.95 | 0.100 | 12.308 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | fixed_conf_0.99 | 0.099 | 14.343 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | full_acquisition | 0.099 | 45.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | mondrian_oracle | 0.144 | 9.913 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | oracle_cheapest_valid | 0.100 | 7.362 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | greedy_entropy | 1 | oracle_stratum_safe | 0.099 | 45.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.144 | 9.913 | 1.000 | 1.000 | 1.000 | 0.000 |
| csv-diabetes | greedy_entropy | 1 | plugin | 0.100 | 7.362 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 1 | budget_0.25 | 0.167 | 11.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 1 | budget_0.5 | 0.132 | 22.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 1 | budget_0.75 | 0.108 | 34.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.9 | 0.119 | 16.907 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.95 | 0.106 | 20.391 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.99 | 0.100 | 27.028 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 1 | full_acquisition | 0.099 | 45.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 1 | mondrian_oracle | 0.124 | 12.717 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 1 | oracle_cheapest_valid | 0.109 | 19.503 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 1 | oracle_stratum_safe | 0.099 | 45.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | random | 1 | oracle_stratum_safe_mondrian | 0.127 | 12.061 | 1.000 | 1.000 | 1.000 | 0.000 |
| csv-diabetes | random | 1 | plugin | 0.110 | 19.103 | 1.000 | 0.550 | 1.000 |  |
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
| csv-diabetes | greedy_entropy | 2 | plugin | 0.098 | 6.915 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | budget_0.25 | 0.163 | 11.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 2 | budget_0.5 | 0.132 | 22.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 2 | budget_0.75 | 0.107 | 34.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.9 | 0.110 | 17.245 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.95 | 0.100 | 20.749 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.99 | 0.096 | 26.009 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | full_acquisition | 0.095 | 45.000 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | mondrian_oracle | 0.136 | 11.361 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 2 | oracle_cheapest_valid | 0.117 | 15.749 | 1.000 | 0.000 | 1.000 |  |
| csv-diabetes | random | 2 | oracle_stratum_safe | 0.095 | 45.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | random | 2 | oracle_stratum_safe_mondrian | 0.141 | 10.723 | 1.000 | 1.000 | 1.000 | 0.000 |
| csv-diabetes | random | 2 | plugin | 0.119 | 15.354 | 1.000 | 0.420 | 1.000 |  |
| csv-physionet | greedy_entropy | 0 | budget_0.25 | 0.141 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | budget_0.5 | 0.136 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | budget_0.75 | 0.128 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.9 | 0.132 | 7.622 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.95 | 0.128 | 14.584 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.99 | 0.127 | 27.377 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | mondrian_oracle | 0.131 | 17.222 | 0.050 | 0.050 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | oracle_cheapest_valid | 0.140 | 1.197 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 0 | plugin | 0.141 | 1.060 | 0.200 | 0.200 | 0.000 |  |
| csv-physionet | random | 0 | budget_0.25 | 0.144 | 10.000 | 0.200 | 0.200 | 0.000 |  |
| csv-physionet | random | 0 | budget_0.5 | 0.138 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | budget_0.75 | 0.136 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | fixed_conf_0.9 | 0.133 | 12.147 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | fixed_conf_0.95 | 0.129 | 24.435 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | fixed_conf_0.99 | 0.127 | 36.329 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | mondrian_oracle | 0.133 | 20.642 | 0.050 | 0.050 | 0.000 |  |
| csv-physionet | random | 0 | oracle_cheapest_valid | 0.142 | 1.165 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 0 | plugin | 0.142 | 1.306 | 0.200 | 0.200 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | budget_0.25 | 0.135 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | budget_0.5 | 0.135 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | budget_0.75 | 0.130 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | fixed_conf_0.9 | 0.137 | 7.526 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | fixed_conf_0.95 | 0.135 | 14.850 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | fixed_conf_0.99 | 0.133 | 30.746 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | full_acquisition | 0.133 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 1 | mondrian_oracle | 0.142 | 1.458 | 0.000 | 0.000 | 0.000 |  |
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
| csv-physionet | random | 1 | mondrian_oracle | 0.141 | 1.439 | 0.000 | 0.000 | 0.000 |  |
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
| csv-physionet | greedy_entropy | 2 | mondrian_oracle | 0.132 | 11.100 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | oracle_cheapest_valid | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | greedy_entropy | 2 | oracle_stratum_safe | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 2 | plugin | 0.139 | 0.065 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | budget_0.25 | 0.137 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | budget_0.5 | 0.137 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | budget_0.75 | 0.128 | 31.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | fixed_conf_0.9 | 0.128 | 12.315 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | fixed_conf_0.95 | 0.127 | 24.643 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | fixed_conf_0.99 | 0.127 | 36.570 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | mondrian_oracle | 0.132 | 14.002 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | oracle_cheapest_valid | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| csv-physionet | random | 2 | oracle_stratum_safe | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | 2 | oracle_stratum_safe_mondrian | 0.139 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | 2 | plugin | 0.139 | 0.088 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | budget_0.25 | 0.133 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | greedy_entropy | 0 | budget_0.5 | 0.069 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 0 | budget_0.75 | 0.059 | 15.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 0 | fixed_conf_0.9 | 0.085 | 6.589 | 1.000 | 1.000 | 1.000 |  |
| cube | greedy_entropy | 0 | fixed_conf_0.95 | 0.063 | 8.354 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 0 | fixed_conf_0.99 | 0.048 | 11.685 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 0 | full_acquisition | 0.046 | 20.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 0 | mondrian_oracle | 0.070 | 8.669 | 1.000 | 0.030 | 1.000 |  |
| cube | greedy_entropy | 0 | oracle_cheapest_valid | 0.079 | 6.983 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 0 | plugin | 0.078 | 7.098 | 1.000 | 0.230 | 1.000 |  |
| cube | random | 0 | budget_0.25 | 0.531 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 0 | budget_0.5 | 0.274 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 0 | budget_0.75 | 0.119 | 15.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 0 | fixed_conf_0.9 | 0.076 | 12.820 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 0 | fixed_conf_0.95 | 0.058 | 14.195 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 0 | fixed_conf_0.99 | 0.047 | 16.120 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 0 | full_acquisition | 0.046 | 20.000 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 0 | mondrian_oracle | 0.065 | 13.791 | 1.000 | 0.010 | 1.000 |  |
| cube | random | 0 | oracle_cheapest_valid | 0.078 | 12.595 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 0 | plugin | 0.080 | 12.462 | 1.000 | 0.570 | 1.000 |  |
| cube | greedy_entropy | 1 | budget_0.25 | 0.148 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | greedy_entropy | 1 | budget_0.5 | 0.063 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | budget_0.75 | 0.058 | 15.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.9 | 0.088 | 6.701 | 1.000 | 0.400 | 1.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.95 | 0.065 | 8.540 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.99 | 0.047 | 11.873 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | full_acquisition | 0.045 | 20.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | mondrian_oracle | 0.076 | 8.208 | 1.000 | 0.010 | 1.000 |  |
| cube | greedy_entropy | 1 | oracle_cheapest_valid | 0.087 | 6.702 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | oracle_stratum_safe | 0.045 | 20.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| cube | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.105 | 7.364 | 1.000 | 1.000 | 1.000 | 0.000 |
| cube | greedy_entropy | 1 | plugin | 0.085 | 6.898 | 1.000 | 0.300 | 1.000 |  |
| cube | random | 1 | budget_0.25 | 0.526 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 1 | budget_0.5 | 0.273 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 1 | budget_0.75 | 0.119 | 15.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 1 | fixed_conf_0.9 | 0.074 | 12.878 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 1 | fixed_conf_0.95 | 0.056 | 14.234 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 1 | fixed_conf_0.99 | 0.045 | 16.192 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 1 | full_acquisition | 0.045 | 20.000 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 1 | mondrian_oracle | 0.072 | 13.232 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 1 | oracle_cheapest_valid | 0.089 | 12.077 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 1 | oracle_stratum_safe | 0.045 | 20.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| cube | random | 1 | oracle_stratum_safe_mondrian | 0.097 | 11.830 | 1.000 | 1.000 | 1.000 | 0.000 |
| cube | random | 1 | plugin | 0.092 | 11.928 | 1.000 | 0.500 | 1.000 |  |
| cube | greedy_entropy | 2 | budget_0.25 | 0.136 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | greedy_entropy | 2 | budget_0.5 | 0.067 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 2 | budget_0.75 | 0.061 | 15.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.9 | 0.086 | 6.711 | 1.000 | 1.000 | 1.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.95 | 0.063 | 8.519 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.99 | 0.047 | 11.933 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 2 | full_acquisition | 0.046 | 20.000 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 2 | mondrian_oracle | 0.073 | 7.960 | 1.000 | 0.090 | 1.000 |  |
| cube | greedy_entropy | 2 | oracle_cheapest_valid | 0.076 | 7.317 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 2 | oracle_stratum_safe | 0.046 | 20.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| cube | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.096 | 6.908 | 1.000 | 1.000 | 1.000 | 0.000 |
| cube | greedy_entropy | 2 | plugin | 0.074 | 7.521 | 1.000 | 0.240 | 1.000 |  |
| cube | random | 2 | budget_0.25 | 0.521 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 2 | budget_0.5 | 0.260 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 2 | budget_0.75 | 0.119 | 15.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 2 | fixed_conf_0.9 | 0.071 | 12.745 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 2 | fixed_conf_0.95 | 0.055 | 14.096 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 2 | fixed_conf_0.99 | 0.047 | 16.032 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 2 | full_acquisition | 0.046 | 20.000 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 2 | mondrian_oracle | 0.065 | 13.486 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 2 | oracle_cheapest_valid | 0.078 | 12.188 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 2 | oracle_stratum_safe | 0.046 | 20.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| cube | random | 2 | oracle_stratum_safe_mondrian | 0.089 | 11.876 | 1.000 | 1.000 | 1.000 | 0.000 |
| cube | random | 2 | plugin | 0.077 | 12.327 | 1.000 | 0.250 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.25 | 0.117 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.5 | 0.079 | 24.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.75 | 0.065 | 37.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.091 | 9.031 | 1.000 | 0.800 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.073 | 12.621 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.060 | 20.979 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | full_acquisition | 0.058 | 49.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | mondrian_oracle | 0.088 | 15.772 | 1.000 | 0.210 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.088 | 9.474 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | plugin | 0.084 | 10.172 | 1.000 | 0.020 | 1.000 |  |
| fashionmnist | random | 0 | budget_0.25 | 0.141 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | random | 0 | budget_0.5 | 0.090 | 24.000 | 1.000 | 0.200 | 1.000 |  |
| fashionmnist | random | 0 | budget_0.75 | 0.069 | 37.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.9 | 0.089 | 12.345 | 1.000 | 0.400 | 1.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.95 | 0.071 | 15.923 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.99 | 0.059 | 23.110 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | full_acquisition | 0.058 | 49.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | mondrian_oracle | 0.095 | 15.590 | 1.000 | 0.890 | 1.000 |  |
| fashionmnist | random | 0 | oracle_cheapest_valid | 0.087 | 12.576 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | plugin | 0.089 | 12.337 | 1.000 | 0.430 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | budget_0.25 | 0.117 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | budget_0.5 | 0.084 | 24.000 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | budget_0.75 | 0.068 | 37.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.9 | 0.096 | 9.135 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.95 | 0.078 | 12.630 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.99 | 0.062 | 21.002 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | full_acquisition | 0.059 | 49.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | mondrian_oracle | 0.087 | 15.381 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | oracle_cheapest_valid | 0.078 | 12.630 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | oracle_stratum_safe | 0.059 | 49.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| fashionmnist | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.100 | 14.362 | 1.000 | 1.000 | 1.000 | 0.000 |
| fashionmnist | greedy_entropy | 1 | plugin | 0.078 | 12.687 | 1.000 | 0.230 | 1.000 |  |
| fashionmnist | random | 1 | budget_0.25 | 0.140 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | random | 1 | budget_0.5 | 0.088 | 24.000 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | random | 1 | budget_0.75 | 0.071 | 37.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.9 | 0.090 | 12.147 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.95 | 0.072 | 15.822 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.99 | 0.061 | 22.971 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | full_acquisition | 0.059 | 49.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | mondrian_oracle | 0.088 | 16.163 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | random | 1 | oracle_cheapest_valid | 0.078 | 14.087 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | oracle_stratum_safe | 0.059 | 49.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| fashionmnist | random | 1 | oracle_stratum_safe_mondrian | 0.103 | 15.065 | 1.000 | 1.000 | 1.000 | 0.000 |
| fashionmnist | random | 1 | plugin | 0.076 | 14.457 | 1.000 | 0.020 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.25 | 0.120 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.5 | 0.087 | 24.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.75 | 0.069 | 37.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.9 | 0.097 | 9.258 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.95 | 0.078 | 12.974 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.99 | 0.061 | 21.649 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | full_acquisition | 0.058 | 49.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | mondrian_oracle | 0.097 | 14.592 | 1.000 | 0.190 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | oracle_cheapest_valid | 0.098 | 9.154 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | oracle_stratum_safe | 0.058 | 49.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| fashionmnist | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.115 | 13.331 | 1.000 | 1.000 | 1.000 | 0.000 |
| fashionmnist | greedy_entropy | 2 | plugin | 0.097 | 9.333 | 1.000 | 0.140 | 1.000 |  |
| fashionmnist | random | 2 | budget_0.25 | 0.137 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| fashionmnist | random | 2 | budget_0.5 | 0.091 | 24.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | budget_0.75 | 0.068 | 37.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.9 | 0.086 | 12.717 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.95 | 0.070 | 16.240 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.99 | 0.059 | 23.171 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | full_acquisition | 0.058 | 49.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | mondrian_oracle | 0.101 | 14.756 | 1.000 | 0.610 | 1.000 |  |
| fashionmnist | random | 2 | oracle_cheapest_valid | 0.098 | 11.144 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | oracle_stratum_safe | 0.058 | 49.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| fashionmnist | random | 2 | oracle_stratum_safe_mondrian | 0.118 | 14.146 | 1.000 | 1.000 | 1.000 | 0.000 |
| fashionmnist | random | 2 | plugin | 0.096 | 11.371 | 1.000 | 0.110 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.25 | 0.216 | 4.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.5 | 0.181 | 7.000 | 1.000 | 0.600 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.75 | 0.158 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.9 | 0.151 | 7.320 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.95 | 0.149 | 8.469 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.99 | 0.147 | 11.556 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | full_acquisition | 0.147 | 14.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | mondrian_oracle | 0.165 | 5.140 | 1.000 | 0.010 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | oracle_cheapest_valid | 0.178 | 3.023 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 0 | plugin | 0.175 | 3.372 | 1.000 | 0.320 | 1.000 |  |
| tabular-adult | random | 0 | budget_0.25 | 0.206 | 4.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-adult | random | 0 | budget_0.5 | 0.181 | 7.000 | 1.000 | 0.800 | 1.000 |  |
| tabular-adult | random | 0 | budget_0.75 | 0.160 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.9 | 0.151 | 7.943 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.95 | 0.149 | 9.583 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.99 | 0.147 | 11.953 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 0 | full_acquisition | 0.147 | 14.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 0 | mondrian_oracle | 0.173 | 4.942 | 1.000 | 0.040 | 1.000 |  |
| tabular-adult | random | 0 | oracle_cheapest_valid | 0.176 | 4.058 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 0 | plugin | 0.173 | 4.282 | 1.000 | 0.150 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | budget_0.25 | 0.189 | 4.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | budget_0.5 | 0.185 | 7.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | budget_0.75 | 0.177 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.9 | 0.159 | 6.381 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.95 | 0.154 | 8.424 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.99 | 0.151 | 12.064 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | full_acquisition | 0.151 | 14.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | mondrian_oracle | 0.172 | 5.554 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | oracle_cheapest_valid | 0.167 | 4.136 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 1 | oracle_stratum_safe | 0.151 | 14.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-adult | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.172 | 5.554 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-adult | greedy_entropy | 1 | plugin | 0.166 | 4.194 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 1 | budget_0.25 | 0.206 | 4.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-adult | random | 1 | budget_0.5 | 0.180 | 7.000 | 1.000 | 0.400 | 1.000 |  |
| tabular-adult | random | 1 | budget_0.75 | 0.162 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.9 | 0.157 | 7.737 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.95 | 0.152 | 9.551 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.99 | 0.151 | 12.072 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 1 | full_acquisition | 0.151 | 14.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 1 | mondrian_oracle | 0.178 | 4.680 | 1.000 | 0.380 | 1.000 |  |
| tabular-adult | random | 1 | oracle_cheapest_valid | 0.178 | 4.615 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 1 | oracle_stratum_safe | 0.151 | 14.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-adult | random | 1 | oracle_stratum_safe_mondrian | 0.188 | 3.815 | 1.000 | 1.000 | 1.000 | 0.000 |
| tabular-adult | random | 1 | plugin | 0.176 | 4.746 | 1.000 | 0.350 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.25 | 0.202 | 4.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.5 | 0.185 | 7.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.75 | 0.158 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.9 | 0.153 | 7.118 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.95 | 0.148 | 8.708 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.99 | 0.146 | 11.890 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | full_acquisition | 0.146 | 14.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | mondrian_oracle | 0.158 | 5.846 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | oracle_cheapest_valid | 0.168 | 4.426 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | greedy_entropy | 2 | oracle_stratum_safe | 0.146 | 14.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-adult | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.167 | 4.188 | 1.000 | 0.200 | 1.000 | 0.000 |
| tabular-adult | greedy_entropy | 2 | plugin | 0.169 | 4.392 | 1.000 | 0.380 | 1.000 |  |
| tabular-adult | random | 2 | budget_0.25 | 0.204 | 4.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-adult | random | 2 | budget_0.5 | 0.173 | 7.000 | 1.000 | 0.800 | 1.000 |  |
| tabular-adult | random | 2 | budget_0.75 | 0.159 | 10.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.9 | 0.150 | 8.007 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.95 | 0.148 | 9.719 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.99 | 0.146 | 12.158 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 2 | full_acquisition | 0.146 | 14.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 2 | mondrian_oracle | 0.171 | 4.634 | 1.000 | 0.600 | 1.000 |  |
| tabular-adult | random | 2 | oracle_cheapest_valid | 0.167 | 4.785 | 1.000 | 0.000 | 1.000 |  |
| tabular-adult | random | 2 | oracle_stratum_safe | 0.146 | 14.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-adult | random | 2 | oracle_stratum_safe_mondrian | 0.181 | 3.735 | 1.000 | 1.000 | 1.000 | 0.000 |
| tabular-adult | random | 2 | plugin | 0.167 | 4.802 | 1.000 | 0.450 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.25 | 0.110 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.5 | 0.092 | 25.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.75 | 0.085 | 38.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.9 | 0.090 | 10.580 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.95 | 0.081 | 16.828 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.99 | 0.078 | 28.661 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | full_acquisition | 0.077 | 50.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | mondrian_oracle | 0.099 | 15.682 | 1.000 | 0.380 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | oracle_cheapest_valid | 0.099 | 7.270 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | plugin | 0.098 | 7.470 | 1.000 | 0.360 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | budget_0.25 | 0.155 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | budget_0.5 | 0.108 | 25.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | budget_0.75 | 0.090 | 38.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.9 | 0.093 | 16.647 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.95 | 0.082 | 23.538 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.99 | 0.077 | 35.213 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | full_acquisition | 0.077 | 50.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | mondrian_oracle | 0.104 | 15.180 | 1.000 | 0.980 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | oracle_cheapest_valid | 0.098 | 14.578 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 0 | plugin | 0.098 | 14.823 | 1.000 | 0.290 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.25 | 0.109 | 12.000 | 1.000 | 0.200 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.5 | 0.088 | 25.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.75 | 0.082 | 38.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.9 | 0.093 | 9.719 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.95 | 0.081 | 16.326 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.99 | 0.077 | 28.213 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | full_acquisition | 0.077 | 50.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | mondrian_oracle | 0.093 | 18.941 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_cheapest_valid | 0.108 | 6.167 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_stratum_safe | 0.077 | 50.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.096 | 12.622 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-MiniBooNE | greedy_entropy | 1 | plugin | 0.107 | 6.316 | 1.000 | 0.210 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | budget_0.25 | 0.158 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | budget_0.5 | 0.110 | 25.000 | 1.000 | 0.600 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | budget_0.75 | 0.089 | 38.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.9 | 0.099 | 15.252 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.95 | 0.084 | 22.510 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.99 | 0.077 | 34.065 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | full_acquisition | 0.077 | 50.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | mondrian_oracle | 0.107 | 15.352 | 1.000 | 0.060 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | oracle_cheapest_valid | 0.108 | 13.076 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | oracle_stratum_safe | 0.077 | 50.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-MiniBooNE | random | 1 | oracle_stratum_safe_mondrian | 0.116 | 13.718 | 1.000 | 1.000 | 1.000 | 0.000 |
| tabular-MiniBooNE | random | 1 | plugin | 0.107 | 13.299 | 1.000 | 0.080 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.25 | 0.102 | 12.000 | 1.000 | 0.800 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.5 | 0.092 | 25.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.75 | 0.084 | 38.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.9 | 0.090 | 11.404 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.95 | 0.081 | 18.347 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.99 | 0.079 | 29.477 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | full_acquisition | 0.080 | 50.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | mondrian_oracle | 0.100 | 20.036 | 1.000 | 0.690 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_cheapest_valid | 0.099 | 7.394 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_stratum_safe | 0.080 | 50.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.102 | 13.580 | 1.000 | 0.800 | 1.000 | 0.000 |
| tabular-MiniBooNE | greedy_entropy | 2 | plugin | 0.101 | 6.880 | 1.000 | 0.550 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.25 | 0.157 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.5 | 0.112 | 25.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.75 | 0.092 | 38.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.9 | 0.093 | 17.081 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.95 | 0.084 | 23.789 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.99 | 0.080 | 34.609 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | full_acquisition | 0.080 | 50.000 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | mondrian_oracle | 0.106 | 15.958 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | oracle_cheapest_valid | 0.098 | 15.119 | 1.000 | 0.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | oracle_stratum_safe | 0.080 | 50.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| tabular-MiniBooNE | random | 2 | oracle_stratum_safe_mondrian | 0.113 | 14.810 | 1.000 | 1.000 | 1.000 | 0.000 |
| tabular-MiniBooNE | random | 2 | plugin | 0.099 | 14.849 | 1.000 | 0.420 | 1.000 |  |
