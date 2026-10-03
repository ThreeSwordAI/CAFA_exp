# TABLE_E6_baselines (lambda_ref key = 0.5, scheme = uniform)

| dataset | policy | seed | baseline | mean_test_risk | mean_test_cost | stratum_violation_rate | aggregate_violation_rate | stratum_certified_violation_rate | feasible_rate |
|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | budget_0.25 | 0.095 | 11.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | budget_0.5 | 0.095 | 22.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | budget_0.75 | 0.095 | 34.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.9 | 0.096 | 9.496 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.95 | 0.096 | 12.179 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.99 | 0.096 | 13.218 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | full_acquisition | 0.096 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | mondrian_oracle | 0.099 | 6.915 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | oracle_cheapest_valid | 0.099 | 6.915 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 0 | oracle_stratum_safe | 0.099 | 6.915 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.099 | 6.915 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | plugin | 0.099 | 6.915 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | budget_0.25 | 0.164 | 11.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 0 | budget_0.5 | 0.131 | 22.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | budget_0.75 | 0.107 | 34.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | fixed_conf_0.9 | 0.117 | 16.332 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | fixed_conf_0.95 | 0.103 | 19.841 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | fixed_conf_0.99 | 0.098 | 24.320 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | full_acquisition | 0.096 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | mondrian_oracle | 0.143 | 11.211 | 0.010 | 0.010 | 0.010 |  |
| csv-diabetes | random | 0 | oracle_cheapest_valid | 0.148 | 10.300 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 0 | oracle_stratum_safe | 0.148 | 10.300 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | oracle_stratum_safe_mondrian | 0.148 | 10.300 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | plugin | 0.150 | 9.908 | 0.400 | 0.400 | 0.160 |  |
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
| csv-diabetes | greedy_entropy | 1 | plugin | 0.100 | 7.362 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | budget_0.25 | 0.167 | 11.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 1 | budget_0.5 | 0.132 | 22.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | budget_0.75 | 0.108 | 34.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.9 | 0.119 | 16.907 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.95 | 0.106 | 20.391 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | fixed_conf_0.99 | 0.100 | 27.028 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | full_acquisition | 0.099 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | mondrian_oracle | 0.142 | 11.734 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | oracle_cheapest_valid | 0.146 | 10.834 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 1 | oracle_stratum_safe | 0.146 | 10.834 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 1 | oracle_stratum_safe_mondrian | 0.146 | 10.834 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 1 | plugin | 0.147 | 10.693 | 0.140 | 0.140 | 0.060 |  |
| csv-diabetes | greedy_entropy | 2 | budget_0.25 | 0.096 | 11.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | budget_0.5 | 0.096 | 22.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | budget_0.75 | 0.095 | 34.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | fixed_conf_0.9 | 0.095 | 9.371 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | fixed_conf_0.95 | 0.095 | 11.578 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | fixed_conf_0.99 | 0.095 | 13.241 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | full_acquisition | 0.095 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | mondrian_oracle | 0.098 | 6.915 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | oracle_cheapest_valid | 0.098 | 6.915 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | greedy_entropy | 2 | oracle_stratum_safe | 0.098 | 6.915 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.098 | 6.915 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 2 | plugin | 0.098 | 6.915 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | budget_0.25 | 0.163 | 11.000 | 1.000 | 1.000 | 1.000 |  |
| csv-diabetes | random | 2 | budget_0.5 | 0.132 | 22.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | budget_0.75 | 0.107 | 34.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.9 | 0.110 | 17.245 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.95 | 0.100 | 20.749 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | fixed_conf_0.99 | 0.096 | 26.009 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | full_acquisition | 0.095 | 45.000 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | mondrian_oracle | 0.143 | 10.662 | 0.200 | 0.200 | 0.010 |  |
| csv-diabetes | random | 2 | oracle_cheapest_valid | 0.146 | 10.234 | 0.000 | 0.000 | 0.000 |  |
| csv-diabetes | random | 2 | oracle_stratum_safe | 0.146 | 10.234 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 2 | oracle_stratum_safe_mondrian | 0.146 | 10.234 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-diabetes | random | 2 | plugin | 0.150 | 9.525 | 0.380 | 0.380 | 0.250 |  |
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
| cube | greedy_entropy | 0 | mondrian_oracle | 0.122 | 4.425 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 0 | oracle_cheapest_valid | 0.149 | 3.733 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 0 | oracle_stratum_safe | 0.126 | 4.369 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.148 | 3.704 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 0 | plugin | 0.148 | 3.749 | 0.990 | 0.310 | 0.870 |  |
| cube | random | 0 | budget_0.25 | 0.531 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 0 | budget_0.5 | 0.274 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 0 | budget_0.75 | 0.119 | 15.000 | 1.000 | 0.000 | 0.800 |  |
| cube | random | 0 | fixed_conf_0.9 | 0.076 | 12.820 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 0 | fixed_conf_0.95 | 0.058 | 14.195 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 0 | fixed_conf_0.99 | 0.047 | 16.120 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 0 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 0 | mondrian_oracle | 0.113 | 10.918 | 0.080 | 0.000 | 0.000 |  |
| cube | random | 0 | oracle_cheapest_valid | 0.147 | 9.602 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 0 | oracle_stratum_safe | 0.124 | 10.303 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 0 | oracle_stratum_safe_mondrian | 0.147 | 9.681 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 0 | plugin | 0.151 | 9.470 | 1.000 | 0.570 | 0.960 |  |
| cube | greedy_entropy | 1 | budget_0.25 | 0.148 | 5.000 | 0.800 | 0.400 | 0.200 |  |
| cube | greedy_entropy | 1 | budget_0.5 | 0.063 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | budget_0.75 | 0.058 | 15.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.9 | 0.088 | 6.701 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.95 | 0.065 | 8.540 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | fixed_conf_0.99 | 0.047 | 11.873 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | full_acquisition | 0.045 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | mondrian_oracle | 0.117 | 5.029 | 0.020 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 1 | oracle_cheapest_valid | 0.148 | 3.990 | 1.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1 | oracle_stratum_safe | 0.114 | 5.274 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.147 | 4.108 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 1 | plugin | 0.142 | 4.258 | 1.000 | 0.200 | 0.950 |  |
| cube | random | 1 | budget_0.25 | 0.526 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 1 | budget_0.5 | 0.273 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 1 | budget_0.75 | 0.119 | 15.000 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 1 | fixed_conf_0.9 | 0.074 | 12.878 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 1 | fixed_conf_0.95 | 0.056 | 14.234 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 1 | fixed_conf_0.99 | 0.045 | 16.192 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 1 | full_acquisition | 0.045 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 1 | mondrian_oracle | 0.115 | 10.944 | 0.120 | 0.000 | 0.000 |  |
| cube | random | 1 | oracle_cheapest_valid | 0.147 | 9.565 | 1.000 | 0.000 | 0.800 |  |
| cube | random | 1 | oracle_stratum_safe | 0.129 | 10.234 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 1 | oracle_stratum_safe_mondrian | 0.146 | 9.728 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 1 | plugin | 0.154 | 9.397 | 0.980 | 0.700 | 0.770 |  |
| cube | greedy_entropy | 2 | budget_0.25 | 0.136 | 5.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | budget_0.5 | 0.067 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | budget_0.75 | 0.061 | 15.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.9 | 0.086 | 6.711 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.95 | 0.063 | 8.519 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | fixed_conf_0.99 | 0.047 | 11.933 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | mondrian_oracle | 0.113 | 5.029 | 0.000 | 0.000 | 0.000 |  |
| cube | greedy_entropy | 2 | oracle_cheapest_valid | 0.148 | 3.921 | 1.000 | 0.000 | 0.800 |  |
| cube | greedy_entropy | 2 | oracle_stratum_safe | 0.130 | 4.385 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.147 | 3.987 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 2 | plugin | 0.141 | 4.118 | 0.840 | 0.100 | 0.350 |  |
| cube | random | 2 | budget_0.25 | 0.521 | 5.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 2 | budget_0.5 | 0.260 | 10.000 | 1.000 | 1.000 | 1.000 |  |
| cube | random | 2 | budget_0.75 | 0.119 | 15.000 | 1.000 | 0.000 | 1.000 |  |
| cube | random | 2 | fixed_conf_0.9 | 0.071 | 12.745 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 2 | fixed_conf_0.95 | 0.055 | 14.096 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 2 | fixed_conf_0.99 | 0.047 | 16.032 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 2 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |  |
| cube | random | 2 | mondrian_oracle | 0.106 | 10.856 | 0.020 | 0.000 | 0.000 |  |
| cube | random | 2 | oracle_cheapest_valid | 0.148 | 9.331 | 1.000 | 0.000 | 0.800 |  |
| cube | random | 2 | oracle_stratum_safe | 0.125 | 10.046 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 2 | oracle_stratum_safe_mondrian | 0.147 | 9.481 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | 2 | plugin | 0.140 | 9.551 | 0.840 | 0.100 | 0.420 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.25 | 0.117 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.5 | 0.079 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | budget_0.75 | 0.065 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.091 | 9.031 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.073 | 12.621 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.060 | 20.979 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | full_acquisition | 0.058 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | mondrian_oracle | 0.128 | 6.695 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.148 | 4.793 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 0 | oracle_stratum_safe | 0.106 | 7.486 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.148 | 5.389 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 0 | plugin | 0.144 | 5.003 | 1.000 | 0.040 | 1.000 |  |
| fashionmnist | random | 0 | budget_0.25 | 0.141 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | budget_0.5 | 0.090 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | budget_0.75 | 0.069 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.9 | 0.089 | 12.345 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.95 | 0.071 | 15.923 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | fixed_conf_0.99 | 0.059 | 23.110 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | full_acquisition | 0.058 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 0 | mondrian_oracle | 0.126 | 9.445 | 0.040 | 0.000 | 0.010 |  |
| fashionmnist | random | 0 | oracle_cheapest_valid | 0.147 | 7.452 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 0 | oracle_stratum_safe | 0.124 | 8.935 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 0 | oracle_stratum_safe_mondrian | 0.148 | 7.782 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 0 | plugin | 0.147 | 7.469 | 1.000 | 0.250 | 0.980 |  |
| fashionmnist | greedy_entropy | 1 | budget_0.25 | 0.117 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | budget_0.5 | 0.084 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | budget_0.75 | 0.068 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.9 | 0.096 | 9.135 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.95 | 0.078 | 12.630 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | fixed_conf_0.99 | 0.062 | 21.002 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | full_acquisition | 0.059 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | mondrian_oracle | 0.131 | 6.422 | 0.040 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 1 | oracle_cheapest_valid | 0.147 | 5.364 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 1 | oracle_stratum_safe | 0.133 | 6.083 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.148 | 5.413 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 1 | plugin | 0.148 | 5.356 | 1.000 | 0.370 | 0.800 |  |
| fashionmnist | random | 1 | budget_0.25 | 0.140 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | budget_0.5 | 0.088 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | budget_0.75 | 0.071 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.9 | 0.090 | 12.147 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.95 | 0.072 | 15.822 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | fixed_conf_0.99 | 0.061 | 22.971 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | full_acquisition | 0.059 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | mondrian_oracle | 0.126 | 8.979 | 0.030 | 0.000 | 0.000 |  |
| fashionmnist | random | 1 | oracle_cheapest_valid | 0.147 | 7.214 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 1 | oracle_stratum_safe | 0.120 | 8.844 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 1 | oracle_stratum_safe_mondrian | 0.147 | 7.510 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 1 | plugin | 0.148 | 7.173 | 1.000 | 0.300 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.25 | 0.120 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.5 | 0.087 | 24.000 | 0.200 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | budget_0.75 | 0.069 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.9 | 0.097 | 9.258 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.95 | 0.078 | 12.974 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | fixed_conf_0.99 | 0.061 | 21.649 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | full_acquisition | 0.058 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | mondrian_oracle | 0.128 | 8.085 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | greedy_entropy | 2 | oracle_cheapest_valid | 0.148 | 5.197 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | greedy_entropy | 2 | oracle_stratum_safe | 0.102 | 8.736 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.146 | 6.262 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 2 | plugin | 0.147 | 5.257 | 1.000 | 0.400 | 1.000 |  |
| fashionmnist | random | 2 | budget_0.25 | 0.137 | 12.000 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | budget_0.5 | 0.091 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | budget_0.75 | 0.068 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.9 | 0.086 | 12.717 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.95 | 0.070 | 16.240 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | fixed_conf_0.99 | 0.059 | 23.171 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | full_acquisition | 0.058 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | mondrian_oracle | 0.126 | 9.298 | 0.150 | 0.000 | 0.000 |  |
| fashionmnist | random | 2 | oracle_cheapest_valid | 0.147 | 7.318 | 1.000 | 0.000 | 1.000 |  |
| fashionmnist | random | 2 | oracle_stratum_safe | 0.118 | 9.314 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 2 | oracle_stratum_safe_mondrian | 0.148 | 7.866 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | random | 2 | plugin | 0.146 | 7.406 | 1.000 | 0.210 | 1.000 |  |
| image-imagenette | greedy_entropy | 0 | budget_0.25 | 0.104 | 12.000 | 1.000 | 0.800 | 1.000 |  |
| image-imagenette | greedy_entropy | 0 | budget_0.5 | 0.062 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | budget_0.75 | 0.041 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.9 | 0.087 | 7.765 | 0.600 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.95 | 0.060 | 10.097 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.99 | 0.036 | 15.312 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | full_acquisition | 0.030 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 0 | mondrian_oracle | 0.068 | 10.173 | 0.110 | 0.000 | 0.010 |  |
| image-imagenette | greedy_entropy | 0 | oracle_cheapest_valid | 0.098 | 7.057 | 1.000 | 0.000 | 0.400 |  |
| image-imagenette | greedy_entropy | 0 | oracle_stratum_safe | 0.082 | 8.076 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.098 | 7.325 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 0 | plugin | 0.099 | 6.994 | 0.980 | 0.490 | 0.190 |  |
| image-imagenette | random | 0 | budget_0.25 | 0.110 | 12.000 | 1.000 | 0.800 | 1.000 |  |
| image-imagenette | random | 0 | budget_0.5 | 0.055 | 24.000 | 0.400 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | budget_0.75 | 0.034 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | fixed_conf_0.9 | 0.077 | 8.154 | 0.800 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | fixed_conf_0.95 | 0.053 | 10.445 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | fixed_conf_0.99 | 0.035 | 15.633 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | full_acquisition | 0.030 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | mondrian_oracle | 0.067 | 12.101 | 0.030 | 0.000 | 0.000 |  |
| image-imagenette | random | 0 | oracle_cheapest_valid | 0.099 | 6.529 | 1.000 | 0.000 | 0.800 |  |
| image-imagenette | random | 0 | oracle_stratum_safe | 0.072 | 8.554 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 0 | oracle_stratum_safe_mondrian | 0.097 | 6.972 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 0 | plugin | 0.098 | 6.612 | 1.000 | 0.330 | 0.660 |  |
| image-imagenette | greedy_entropy | 1 | budget_0.25 | 0.119 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| image-imagenette | greedy_entropy | 1 | budget_0.5 | 0.058 | 24.000 | 0.400 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | budget_0.75 | 0.037 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | fixed_conf_0.9 | 0.079 | 9.048 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | fixed_conf_0.95 | 0.054 | 11.110 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | fixed_conf_0.99 | 0.037 | 16.456 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | full_acquisition | 0.032 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | mondrian_oracle | 0.062 | 12.375 | 0.020 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | oracle_cheapest_valid | 0.097 | 7.822 | 1.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 1 | oracle_stratum_safe | 0.086 | 8.441 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.096 | 7.885 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 1 | plugin | 0.098 | 7.810 | 0.740 | 0.450 | 0.150 |  |
| image-imagenette | random | 1 | budget_0.25 | 0.106 | 12.000 | 1.000 | 0.800 | 1.000 |  |
| image-imagenette | random | 1 | budget_0.5 | 0.058 | 24.000 | 0.200 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | budget_0.75 | 0.039 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | fixed_conf_0.9 | 0.084 | 8.128 | 0.400 | 0.000 | 0.200 |  |
| image-imagenette | random | 1 | fixed_conf_0.95 | 0.055 | 10.459 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | fixed_conf_0.99 | 0.035 | 15.618 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | full_acquisition | 0.032 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 1 | mondrian_oracle | 0.069 | 9.314 | 0.190 | 0.000 | 0.050 |  |
| image-imagenette | random | 1 | oracle_cheapest_valid | 0.098 | 7.178 | 1.000 | 0.000 | 0.600 |  |
| image-imagenette | random | 1 | oracle_stratum_safe | 0.079 | 8.445 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 1 | oracle_stratum_safe_mondrian | 0.097 | 7.345 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 1 | plugin | 0.101 | 6.994 | 0.980 | 0.510 | 0.550 |  |
| image-imagenette | greedy_entropy | 2 | budget_0.25 | 0.115 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| image-imagenette | greedy_entropy | 2 | budget_0.5 | 0.059 | 24.000 | 1.000 | 0.000 | 0.400 |  |
| image-imagenette | greedy_entropy | 2 | budget_0.75 | 0.035 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | fixed_conf_0.9 | 0.076 | 9.167 | 0.400 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | fixed_conf_0.95 | 0.053 | 11.472 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | fixed_conf_0.99 | 0.033 | 16.566 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | full_acquisition | 0.028 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | greedy_entropy | 2 | mondrian_oracle | 0.061 | 11.247 | 0.060 | 0.000 | 0.020 |  |
| image-imagenette | greedy_entropy | 2 | oracle_cheapest_valid | 0.098 | 7.848 | 1.000 | 0.000 | 0.400 |  |
| image-imagenette | greedy_entropy | 2 | oracle_stratum_safe | 0.077 | 9.048 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.097 | 8.119 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 2 | plugin | 0.099 | 7.870 | 0.790 | 0.500 | 0.530 |  |
| image-imagenette | random | 2 | budget_0.25 | 0.102 | 12.000 | 1.000 | 0.800 | 1.000 |  |
| image-imagenette | random | 2 | budget_0.5 | 0.053 | 24.000 | 0.200 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | budget_0.75 | 0.036 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | fixed_conf_0.9 | 0.072 | 8.081 | 0.600 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | fixed_conf_0.95 | 0.052 | 10.278 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | fixed_conf_0.99 | 0.031 | 15.452 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | full_acquisition | 0.028 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | mondrian_oracle | 0.067 | 11.031 | 0.000 | 0.000 | 0.000 |  |
| image-imagenette | random | 2 | oracle_cheapest_valid | 0.098 | 6.385 | 1.000 | 0.000 | 1.000 |  |
| image-imagenette | random | 2 | oracle_stratum_safe | 0.069 | 8.303 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 2 | oracle_stratum_safe_mondrian | 0.098 | 6.643 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | 2 | plugin | 0.100 | 6.323 | 1.000 | 0.580 | 0.860 |  |
| mnist | greedy_entropy | 0 | budget_0.25 | 0.027 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | budget_0.5 | 0.016 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | budget_0.75 | 0.010 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.046 | 4.608 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.026 | 5.957 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.011 | 10.331 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | full_acquisition | 0.006 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | mondrian_oracle | 0.084 | 3.620 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.098 | 3.406 | 1.000 | 0.000 | 0.200 |  |
| mnist | greedy_entropy | 0 | oracle_stratum_safe | 0.089 | 3.514 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.097 | 3.416 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 0 | plugin | 0.098 | 3.415 | 0.930 | 0.190 | 0.280 |  |
| mnist | random | 0 | budget_0.25 | 0.115 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| mnist | random | 0 | budget_0.5 | 0.025 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | budget_0.75 | 0.009 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | fixed_conf_0.9 | 0.055 | 9.741 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | fixed_conf_0.95 | 0.031 | 11.456 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | fixed_conf_0.99 | 0.010 | 15.352 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | full_acquisition | 0.006 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 0 | mondrian_oracle | 0.076 | 8.724 | 0.050 | 0.000 | 0.010 |  |
| mnist | random | 0 | oracle_cheapest_valid | 0.097 | 8.036 | 0.800 | 0.000 | 0.000 |  |
| mnist | random | 0 | oracle_stratum_safe | 0.091 | 8.238 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 0 | oracle_stratum_safe_mondrian | 0.097 | 8.043 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 0 | plugin | 0.096 | 8.072 | 0.790 | 0.280 | 0.090 |  |
| mnist | greedy_entropy | 1 | budget_0.25 | 0.027 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | budget_0.5 | 0.017 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | budget_0.75 | 0.010 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | fixed_conf_0.9 | 0.047 | 4.642 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | fixed_conf_0.95 | 0.028 | 5.936 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | fixed_conf_0.99 | 0.011 | 10.390 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | full_acquisition | 0.005 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | mondrian_oracle | 0.082 | 3.752 | 0.110 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | oracle_cheapest_valid | 0.098 | 3.507 | 0.800 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 1 | oracle_stratum_safe | 0.089 | 3.626 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.098 | 3.508 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 1 | plugin | 0.096 | 3.539 | 0.600 | 0.110 | 0.100 |  |
| mnist | random | 1 | budget_0.25 | 0.114 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| mnist | random | 1 | budget_0.5 | 0.024 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | budget_0.75 | 0.009 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | fixed_conf_0.9 | 0.049 | 9.781 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | fixed_conf_0.95 | 0.028 | 11.525 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | fixed_conf_0.99 | 0.009 | 15.524 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | full_acquisition | 0.005 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | mondrian_oracle | 0.079 | 8.539 | 0.100 | 0.000 | 0.000 |  |
| mnist | random | 1 | oracle_cheapest_valid | 0.098 | 7.877 | 1.000 | 0.000 | 0.000 |  |
| mnist | random | 1 | oracle_stratum_safe | 0.091 | 8.101 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 1 | oracle_stratum_safe_mondrian | 0.097 | 7.909 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 1 | plugin | 0.099 | 7.858 | 0.810 | 0.380 | 0.070 |  |
| mnist | greedy_entropy | 2 | budget_0.25 | 0.034 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | budget_0.5 | 0.021 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | budget_0.75 | 0.011 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | fixed_conf_0.9 | 0.054 | 5.133 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | fixed_conf_0.95 | 0.030 | 6.915 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | fixed_conf_0.99 | 0.011 | 11.579 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | full_acquisition | 0.005 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | mondrian_oracle | 0.083 | 4.093 | 0.030 | 0.000 | 0.000 |  |
| mnist | greedy_entropy | 2 | oracle_cheapest_valid | 0.097 | 3.800 | 1.000 | 0.000 | 0.200 |  |
| mnist | greedy_entropy | 2 | oracle_stratum_safe | 0.090 | 3.937 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.097 | 3.804 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | 2 | plugin | 0.098 | 3.793 | 0.910 | 0.210 | 0.310 |  |
| mnist | random | 2 | budget_0.25 | 0.119 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| mnist | random | 2 | budget_0.5 | 0.027 | 24.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | budget_0.75 | 0.009 | 37.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | fixed_conf_0.9 | 0.053 | 9.749 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | fixed_conf_0.95 | 0.030 | 11.481 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | fixed_conf_0.99 | 0.010 | 15.409 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | full_acquisition | 0.005 | 49.000 | 0.000 | 0.000 | 0.000 |  |
| mnist | random | 2 | mondrian_oracle | 0.078 | 8.742 | 0.110 | 0.000 | 0.000 |  |
| mnist | random | 2 | oracle_cheapest_valid | 0.096 | 8.118 | 0.600 | 0.000 | 0.000 |  |
| mnist | random | 2 | oracle_stratum_safe | 0.092 | 8.254 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 2 | oracle_stratum_safe_mondrian | 0.097 | 8.086 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | 2 | plugin | 0.097 | 8.102 | 0.530 | 0.270 | 0.170 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.25 | 0.216 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.5 | 0.181 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | budget_0.75 | 0.158 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.9 | 0.151 | 7.320 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.95 | 0.149 | 8.469 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.99 | 0.147 | 11.556 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | full_acquisition | 0.147 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | mondrian_oracle | 0.197 | 2.382 | 0.010 | 0.010 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | oracle_cheapest_valid | 0.237 | 0.476 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 0 | oracle_stratum_safe | 0.237 | 0.476 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.237 | 0.476 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 0 | plugin | 0.220 | 1.273 | 0.150 | 0.150 | 0.000 |  |
| tabular-adult | random | 0 | budget_0.25 | 0.206 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | budget_0.5 | 0.181 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | budget_0.75 | 0.160 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.9 | 0.151 | 7.943 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.95 | 0.149 | 9.583 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | fixed_conf_0.99 | 0.147 | 11.953 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | full_acquisition | 0.147 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | mondrian_oracle | 0.186 | 3.461 | 0.010 | 0.010 | 0.000 |  |
| tabular-adult | random | 0 | oracle_cheapest_valid | 0.234 | 0.688 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 0 | oracle_stratum_safe | 0.234 | 0.688 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 0 | oracle_stratum_safe_mondrian | 0.234 | 0.688 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 0 | plugin | 0.214 | 1.856 | 0.150 | 0.150 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | budget_0.25 | 0.189 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | budget_0.5 | 0.185 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | budget_0.75 | 0.177 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.9 | 0.159 | 6.381 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.95 | 0.154 | 8.424 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | fixed_conf_0.99 | 0.151 | 12.064 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | full_acquisition | 0.151 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | mondrian_oracle | 0.167 | 4.136 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | oracle_cheapest_valid | 0.167 | 4.136 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 1 | oracle_stratum_safe | 0.167 | 4.136 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.167 | 4.136 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 1 | plugin | 0.180 | 3.513 | 0.150 | 0.150 | 0.000 |  |
| tabular-adult | random | 1 | budget_0.25 | 0.206 | 4.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | budget_0.5 | 0.180 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | budget_0.75 | 0.162 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.9 | 0.157 | 7.737 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.95 | 0.152 | 9.551 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | fixed_conf_0.99 | 0.151 | 12.072 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | full_acquisition | 0.151 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | mondrian_oracle | 0.204 | 2.608 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | oracle_cheapest_valid | 0.204 | 2.608 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 1 | oracle_stratum_safe | 0.204 | 2.608 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 1 | oracle_stratum_safe_mondrian | 0.204 | 2.608 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 1 | plugin | 0.211 | 2.215 | 0.150 | 0.150 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.25 | 0.202 | 4.000 | 0.800 | 0.800 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.5 | 0.185 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | budget_0.75 | 0.158 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.9 | 0.153 | 7.118 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.95 | 0.148 | 8.708 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | fixed_conf_0.99 | 0.146 | 11.890 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | full_acquisition | 0.146 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | mondrian_oracle | 0.182 | 2.790 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | oracle_cheapest_valid | 0.182 | 2.716 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | greedy_entropy | 2 | oracle_stratum_safe | 0.182 | 2.716 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.182 | 2.716 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 2 | plugin | 0.182 | 2.716 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | budget_0.25 | 0.204 | 4.000 | 0.800 | 0.800 | 0.200 |  |
| tabular-adult | random | 2 | budget_0.5 | 0.173 | 7.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | budget_0.75 | 0.159 | 10.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.9 | 0.150 | 8.007 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.95 | 0.148 | 9.719 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | fixed_conf_0.99 | 0.146 | 12.158 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | full_acquisition | 0.146 | 14.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | mondrian_oracle | 0.180 | 3.608 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | oracle_cheapest_valid | 0.184 | 3.371 | 0.000 | 0.000 | 0.000 |  |
| tabular-adult | random | 2 | oracle_stratum_safe | 0.184 | 3.371 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 2 | oracle_stratum_safe_mondrian | 0.184 | 3.371 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | 2 | plugin | 0.184 | 3.371 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.25 | 0.110 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.5 | 0.092 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.75 | 0.085 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.9 | 0.090 | 10.580 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.95 | 0.081 | 16.828 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.99 | 0.078 | 28.661 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | mondrian_oracle | 0.130 | 3.070 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | oracle_cheapest_valid | 0.130 | 3.070 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 0 | oracle_stratum_safe | 0.130 | 3.070 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | oracle_stratum_safe_mondrian | 0.130 | 3.070 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | plugin | 0.130 | 3.070 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | budget_0.25 | 0.155 | 12.000 | 1.000 | 1.000 | 0.800 |  |
| tabular-MiniBooNE | random | 0 | budget_0.5 | 0.108 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | budget_0.75 | 0.090 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.9 | 0.093 | 16.647 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.95 | 0.082 | 23.538 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.99 | 0.077 | 35.213 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | mondrian_oracle | 0.141 | 7.741 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | oracle_cheapest_valid | 0.147 | 7.113 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 0 | oracle_stratum_safe | 0.147 | 7.113 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | oracle_stratum_safe_mondrian | 0.147 | 7.113 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | plugin | 0.146 | 7.188 | 0.080 | 0.080 | 0.080 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.25 | 0.109 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.5 | 0.088 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | budget_0.75 | 0.082 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.9 | 0.093 | 9.719 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.95 | 0.081 | 16.326 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | fixed_conf_0.99 | 0.077 | 28.213 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | mondrian_oracle | 0.140 | 3.129 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_cheapest_valid | 0.147 | 2.863 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_stratum_safe | 0.147 | 2.863 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 1 | oracle_stratum_safe_mondrian | 0.147 | 2.863 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 1 | plugin | 0.146 | 2.915 | 0.060 | 0.060 | 0.050 |  |
| tabular-MiniBooNE | random | 1 | budget_0.25 | 0.158 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | random | 1 | budget_0.5 | 0.110 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | budget_0.75 | 0.089 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.9 | 0.099 | 15.252 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.95 | 0.084 | 22.510 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | fixed_conf_0.99 | 0.077 | 34.065 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | mondrian_oracle | 0.140 | 7.914 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | oracle_cheapest_valid | 0.149 | 6.994 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 1 | oracle_stratum_safe | 0.149 | 6.994 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 1 | oracle_stratum_safe_mondrian | 0.149 | 6.994 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 1 | plugin | 0.146 | 7.320 | 0.010 | 0.010 | 0.010 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.25 | 0.102 | 12.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.5 | 0.092 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | budget_0.75 | 0.084 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.9 | 0.090 | 11.404 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.95 | 0.081 | 18.347 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | fixed_conf_0.99 | 0.079 | 29.477 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | full_acquisition | 0.080 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | mondrian_oracle | 0.141 | 2.432 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_cheapest_valid | 0.141 | 2.427 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_stratum_safe | 0.141 | 2.427 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 2 | oracle_stratum_safe_mondrian | 0.141 | 2.427 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 2 | plugin | 0.141 | 2.427 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.25 | 0.157 | 12.000 | 1.000 | 1.000 | 1.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.5 | 0.112 | 25.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | budget_0.75 | 0.092 | 38.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.9 | 0.093 | 17.081 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.95 | 0.084 | 23.789 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | fixed_conf_0.99 | 0.080 | 34.609 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | full_acquisition | 0.080 | 50.000 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | mondrian_oracle | 0.143 | 7.319 | 0.020 | 0.020 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | oracle_cheapest_valid | 0.147 | 6.938 | 0.000 | 0.000 | 0.000 |  |
| tabular-MiniBooNE | random | 2 | oracle_stratum_safe | 0.147 | 6.938 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 2 | oracle_stratum_safe_mondrian | 0.147 | 6.938 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 2 | plugin | 0.148 | 6.794 | 0.460 | 0.460 | 0.010 |  |
