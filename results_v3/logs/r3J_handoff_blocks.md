#### Seed-aggregated headline (`results_v3/tables/TABLE_E4_cascade_seeds.csv`; λ_ref `dep`, uniform costs; mean ± sample sd over seeds 0, 1, 2)

| dataset | policy | n | tier 1 | tier 3 | none | cert. deployment | cost / T | cost premium | raw violation | certified violation | max_excess_se | cascade / safe oracle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 3 | 0.000 ± 0.000 | 0.683 ± 0.548 | 0.317 ± 0.548 | 0.683 ± 0.548 | 1.000 ± 0.000 | 6.376 ± 0.228 | 0.000 ± 0.000 | 0.000 ± 0.000 | -3.10 ± 1.21 | 1.000 ± 0.000 |
| csv-diabetes | random | 3 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 4.023 ± 0.193 | 0.010 ± 0.017 | 0.000 ± 0.000 | -3.92 ± 0.16 | 1.000 ± 0.000 |
| csv-physionet | greedy_entropy | 3 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 |  | 0.000 ± 0.000 | 0.000 ± 0.000 | -6.78 ± 0.25 |  |
| csv-physionet | random | 3 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 |  | 0.000 ± 0.000 | 0.000 ± 0.000 | -6.78 ± 0.25 |  |
| cube | greedy_entropy | 3 | 0.857 ± 0.223 | 0.143 ± 0.223 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.429 ± 0.189 | 1.861 ± 0.703 | 0.003 ± 0.006 | 0.000 ± 0.000 | -3.60 ± 0.21 | 1.703 ± 0.531 |
| cube | random | 3 | 0.893 ± 0.176 | 0.107 ± 0.176 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.652 ± 0.100 | 1.314 ± 0.210 | 0.000 ± 0.000 | 0.000 ± 0.000 | -3.33 ± 0.06 | 1.184 ± 0.143 |
| fashionmnist | greedy_entropy | 3 | 0.153 ± 0.172 | 0.847 ± 0.172 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.926 ± 0.076 | 8.132 ± 0.727 | 0.033 ± 0.058 | 0.000 ± 0.000 | -4.75 ± 1.13 | 2.847 ± 0.587 |
| fashionmnist | random | 3 | 0.043 ± 0.067 | 0.957 ± 0.067 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.973 ± 0.041 | 6.088 ± 0.327 | 0.037 ± 0.055 | 0.003 ± 0.006 | -4.19 ± 0.26 | 2.067 ± 0.972 |
| image-imagenette | greedy_entropy | 3 | 0.280 ± 0.080 | 0.720 ± 0.080 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.845 ± 0.036 | 4.876 ± 0.450 | 0.087 ± 0.091 | 0.000 ± 0.000 | -3.08 ± 0.27 | 3.399 ± 1.153 |
| image-imagenette | random | 3 | 0.307 ± 0.189 | 0.693 ± 0.189 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.807 ± 0.118 | 5.197 ± 0.837 | 0.057 ± 0.055 | 0.000 ± 0.000 | -3.03 ± 0.50 | 3.916 ± 0.925 |
| mnist | greedy_entropy | 3 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.086 ± 0.012 | 1.146 ± 0.089 | 0.000 ± 0.000 | 0.000 ± 0.000 | -3.09 ± 0.41 | 1.074 ± 0.030 |
| mnist | random | 3 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.183 ± 0.002 | 1.088 ± 0.006 | 0.000 ± 0.000 | 0.000 ± 0.000 | -3.72 ± 0.04 | 1.091 ± 0.001 |
| tabular-MiniBooNE | greedy_entropy | 3 | 0.007 ± 0.006 | 0.993 ± 0.006 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.995 ± 0.004 | 17.524 ± 2.509 | 0.010 ± 0.010 | 0.007 ± 0.006 | -4.17 ± 0.83 | 1.295 ± 0.285 |
| tabular-MiniBooNE | random | 3 | 0.517 ± 0.346 | 0.483 ± 0.346 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.685 ± 0.240 | 4.440 ± 1.441 | 0.010 ± 0.017 | 0.000 ± 0.000 | -4.02 ± 0.71 | 2.892 ± 1.011 |
| tabular-adult | greedy_entropy | 3 | 0.340 ± 0.572 | 0.660 ± 0.572 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.734 ± 0.451 | 3.202 ± 1.864 | 0.010 ± 0.010 | 0.007 ± 0.012 | -3.99 ± 0.57 | 1.218 ± 0.311 |
| tabular-adult | random | 3 | 0.097 ± 0.167 | 0.903 ± 0.167 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.945 ± 0.095 | 4.135 ± 0.310 | 0.010 ± 0.010 | 0.000 ± 0.000 | -3.61 ± 0.35 | 2.106 ± 1.772 |

#### Seed consistency (`results_v3/tables/TABLE_E4_seed_flags.csv`; values per seed 0 / 1 / 2)

| dataset | policy | α | tier 1 | tier 3 | tier-1 range | flag | deepest k | r_full | verdict |
|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 0.050 / 1.000 | 0.000 |  | 1 / 1 / 1 | 0.333 / 0.388 / 0.321 | type_II / type_II / type_II |
| csv-diabetes | random | 0.15 / 0.15 / 0.15 | 0.000 / 0.000 / 0.000 | 1.000 / 1.000 / 1.000 | 0.000 |  | 3 / 3 / 3 | 0.241 / 0.241 / 0.231 | type_II / type_II / type_II |
| csv-physionet | greedy_entropy | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 0.126 / 0.131 / 0.120 | feasible / feasible / feasible |
| csv-physionet | random | 0.2 / 0.2 / 0.2 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 0 / 0 / 0 | 0.126 / 0.131 / 0.120 | feasible / feasible / feasible |
| cube | greedy_entropy | 0.15 / 0.15 / 0.15 | 1.000 / 0.600 / 0.970 | 0.000 / 0.400 / 0.030 | 0.400 | FLAG | 2 / 3 / 2 | 0.080 / 0.103 / 0.092 | feasible / feasible / feasible |
| cube | random | 0.15 / 0.15 / 0.15 | 0.990 / 0.690 / 1.000 | 0.010 / 0.310 / 0.000 | 0.310 | FLAG | 3 / 3 / 4 | 0.083 / 0.104 / 0.090 | feasible / feasible / feasible |
| fashionmnist | greedy_entropy | 0.15 / 0.15 / 0.15 | 0.120 / 0.340 / 0.000 | 0.880 / 0.660 / 1.000 | 0.340 | FLAG | 4 / 4 / 3 | 0.133 / 0.132 / 0.148 | feasible / feasible / feasible |
| fashionmnist | random | 0.15 / 0.15 / 0.15 | 0.120 / 0.010 / 0.000 | 0.880 / 0.990 / 1.000 | 0.120 |  | 4 / 4 / 4 | 0.129 / 0.144 / 0.153 | feasible / feasible / unresolved |
| image-imagenette | greedy_entropy | 0.1 / 0.1 / 0.1 | 0.200 / 0.280 / 0.360 | 0.800 / 0.720 / 0.640 | 0.160 |  | 3 / 3 / 3 | 0.078 / 0.077 / 0.074 | feasible / feasible / feasible |
| image-imagenette | random | 0.1 / 0.1 / 0.1 | 0.090 / 0.390 / 0.440 | 0.910 / 0.610 / 0.560 | 0.350 | FLAG | 3 / 3 / 3 | 0.083 / 0.075 / 0.069 | feasible / feasible / feasible |
| mnist | greedy_entropy | 0.1 / 0.1 / 0.1 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 2 / 3 / 4 | 0.008 / 0.010 / 0.009 | feasible / feasible / feasible |
| mnist | random | 0.1 / 0.1 / 0.1 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.000 | 0.000 |  | 4 / 4 / 4 | 0.012 / 0.010 / 0.009 | feasible / feasible / feasible |
| tabular-MiniBooNE | greedy_entropy | 0.15 / 0.15 / 0.15 | 0.010 / 0.000 / 0.010 | 0.990 / 1.000 / 0.990 | 0.010 |  | 2 / 2 / 2 | 0.146 / 0.158 / 0.151 | feasible / type_II / unresolved |
| tabular-MiniBooNE | random | 0.15 / 0.15 / 0.15 | 0.260 / 0.380 / 0.910 | 0.740 / 0.620 / 0.090 | 0.650 | FLAG | 3 / 3 / 4 | 0.132 / 0.137 / 0.130 | feasible / feasible / feasible |
| tabular-adult | greedy_entropy | 0.25 / 0.25 / 0.2 | 1.000 / 0.000 / 0.020 | 0.000 / 1.000 / 0.980 | 1.000 | FLAG | 1 / 2 / 1 | 0.196 / 0.330 / 0.206 | feasible / type_II / unresolved |
| tabular-adult | random | 0.25 / 0.25 / 0.2 | 0.000 / 0.290 / 0.000 | 1.000 / 0.710 / 1.000 | 0.290 | FLAG | 2 / 1 / 2 | 0.254 / 0.225 / 0.269 | unresolved / feasible / type_II |

#### E7 repairs, seeds 1-2 (`results_v3/logs/r3J_repair_*_ts{1,2}.log`, lambda_ref `dep` line)

```
csv-diabetes_policy_change_ts1  [repair:policy_change] lr[dep]=0.828 deepest k=3: type_II (rmin 0.240, full 0.241) -> type_II (rmin 0.238, full 0.241); tier1 0.00 -> 0.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-diabetes_policy_change_ts2  [repair:policy_change] lr[dep]=0.828 deepest k=3: type_II (rmin 0.229, full 0.231) -> type_II (rmin 0.227, full 0.231); tier1 0.00 -> 0.00; viol 0.03 -> 0.03; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-physionet_policy_change_ts1  [repair:policy_change] lr[dep]=0.000 deepest k=0: feasible (rmin 0.129, full 0.131) -> feasible (rmin 0.125, full 0.131); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-physionet_policy_change_ts2  [repair:policy_change] lr[dep]=0.000 deepest k=0: feasible (rmin 0.119, full 0.120) -> feasible (rmin 0.120, full 0.120); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
cube_policy_change_ts1  [repair:policy_change] lr[dep]=0.768 deepest k=3: feasible (rmin 0.104, full 0.104) -> feasible (rmin 0.104, full 0.104); tier1 0.69 -> 0.69; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
cube_policy_change_ts2  [repair:policy_change] lr[dep]=0.747 deepest k=4: feasible (rmin 0.088, full 0.090) -> feasible (rmin 0.090, full 0.090); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
fashionmnist_policy_change_ts1  [repair:policy_change] lr[dep]=0.768 deepest k=4: feasible (rmin 0.144, full 0.144) -> feasible (rmin 0.144, full 0.144); tier1 0.01 -> 0.01; viol 0.01 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 4/5
fashionmnist_policy_change_ts2  [repair:policy_change] lr[dep]=0.778 deepest k=4: unresolved (rmin 0.153, full 0.153) -> unresolved (rmin 0.153, full 0.153); tier1 0.00 -> 0.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 4/5 -> 3/5
image-imagenette_policy_change_ts1  [repair:policy_change] lr[dep]=0.838 deepest k=3: feasible (rmin 0.075, full 0.075) -> feasible (rmin 0.072, full 0.075); tier1 0.39 -> 0.39; viol 0.11 -> 0.09; certviol 0.00 -> 0.01; verdict agreement 5/5 -> 5/5
image-imagenette_policy_change_ts2  [repair:policy_change] lr[dep]=0.818 deepest k=3: feasible (rmin 0.069, full 0.069) -> feasible (rmin 0.066, full 0.069); tier1 0.44 -> 0.44; viol 0.06 -> 0.05; certviol 0.00 -> 0.01; verdict agreement 5/5 -> 5/5
mnist_policy_change_ts1  [repair:policy_change] lr[dep]=0.798 deepest k=4: feasible (rmin 0.010, full 0.010) -> feasible (rmin 0.010, full 0.010); tier1 1.00 -> 1.00; viol 0.00 -> 0.04; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_policy_change_ts2  [repair:policy_change] lr[dep]=0.818 deepest k=4: feasible (rmin 0.009, full 0.009) -> feasible (rmin 0.009, full 0.009); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_predictor_upgrade_ts1  [repair:predictor_upgrade] lr[dep]=0.859 deepest k=4: type_II (rmin 0.239, full 0.239) -> feasible (rmin 0.010, full 0.010); tier1 0.00 -> 1.00; viol 0.00 -> 0.02; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_predictor_upgrade_ts2  [repair:predictor_upgrade] lr[dep]=0.919 deepest k=4: type_II (rmin 0.250, full 0.250) -> feasible (rmin 0.013, full 0.013); tier1 0.00 -> 1.00; viol 0.01 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_policy_change_ts1  [repair:policy_change] lr[dep]=0.808 deepest k=3: feasible (rmin 0.136, full 0.137) -> feasible (rmin 0.134, full 0.137); tier1 0.38 -> 0.38; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_policy_change_ts2  [repair:policy_change] lr[dep]=0.747 deepest k=4: feasible (rmin 0.130, full 0.130) -> feasible (rmin 0.129, full 0.130); tier1 0.91 -> 0.91; viol 0.00 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_predictor_upgrade_ts1  [repair:predictor_upgrade] lr[dep]=0.758 deepest k=2: unresolved (rmin 0.152, full 0.153) -> feasible (rmin 0.141, full 0.141); tier1 0.00 -> 0.14; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 4/5 -> 5/5
tabular-MiniBooNE_predictor_upgrade_ts2  [repair:predictor_upgrade] lr[dep]=0.737 deepest k=2: type_II (rmin 0.166, full 0.172) -> feasible (rmin 0.144, full 0.144); tier1 0.00 -> 0.07; viol 0.00 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_policy_change_ts1  [repair:policy_change] lr[dep]=0.747 deepest k=1: feasible (rmin 0.225, full 0.225) -> feasible (rmin 0.225, full 0.225); tier1 0.29 -> 0.29; viol 0.01 -> 0.02; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_policy_change_ts2  [repair:policy_change] lr[dep]=0.737 deepest k=2: type_II (rmin 0.267, full 0.269) -> type_II (rmin 0.259, full 0.269); tier1 0.00 -> 0.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_predictor_upgrade_ts1  [repair:predictor_upgrade] lr[dep]=0.758 deepest k=2: type_II (rmin 0.289, full 0.290) -> type_II (rmin 0.285, full 0.285); tier1 0.00 -> 0.00; viol 0.00 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_predictor_upgrade_ts2  [repair:predictor_upgrade] lr[dep]=0.737 deepest k=1: unresolved (rmin 0.207, full 0.209) -> type_II (rmin 0.217, full 0.221); tier1 0.00 -> 0.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 1/5
```

#### E9 α margin over seeds (`results_v3/tables/TABLE_E9_alpha_margin.csv` (seed 0), `results_v3/tables_e9_alpha_margin_ts{1,2}/TABLE_E9_alpha_margin.csv`): tier-1 share at margin 0.02 / 0.05 / 0.10

| dataset | policy | seed 0 | seed 1 | seed 2 |
|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0.00 (α 0.12) / 0.00 (α 0.15) / 0.00 (α 0.2) | 0.00 (α 0.11) / 0.00 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.12) / 0.00 (α 0.15) / 0.00 (α 0.2) |
| csv-diabetes | random | 0.00 (α 0.12) / 0.00 (α 0.15) / 0.26 (α 0.2) | 0.00 (α 0.11) / 0.00 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.12) / 0.00 (α 0.15) / 0.55 (α 0.2) |
| csv-physionet | greedy_entropy | 0.58 (α 0.15) / 1.00 (α 0.2) / 1.00 (α 0.25) | 0.96 (α 0.17) / 1.00 (α 0.2) / 1.00 (α 0.25) | 0.80 (α 0.15) / 1.00 (α 0.2) / 1.00 (α 0.25) |
| csv-physionet | random | 0.58 (α 0.15) / 1.00 (α 0.2) / 1.00 (α 0.25) | 0.96 (α 0.17) / 1.00 (α 0.2) / 1.00 (α 0.25) | 0.80 (α 0.15) / 1.00 (α 0.2) / 1.00 (α 0.25) |
| cube | greedy_entropy | 0.00 (α 0.08) / 1.00 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.09) / 0.60 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.08) / 0.97 (α 0.15) / 1.00 (α 0.2) |
| cube | random | 0.00 (α 0.08) / 0.99 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.09) / 0.69 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.08) / 1.00 (α 0.15) / 1.00 (α 0.2) |
| fashionmnist | greedy_entropy | 0.00 (α 0.09) / 0.12 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.08) / 0.34 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.1) / 0.00 (α 0.15) / 1.00 (α 0.2) |
| fashionmnist | random | 0.00 (α 0.09) / 0.12 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.08) / 0.01 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.1) / 0.00 (α 0.15) / 1.00 (α 0.2) |
| image-imagenette | greedy_entropy | refused (α 0.05) / 0.20 (α 0.1) / 1.00 (α 0.15) | refused (α 0.05) / 0.28 (α 0.1) / 1.00 (α 0.15) | refused (α 0.05) / 0.36 (α 0.1) / 1.00 (α 0.15) |
| image-imagenette | random | refused (α 0.05) / 0.09 (α 0.1) / 1.00 (α 0.15) | refused (α 0.05) / 0.39 (α 0.1) / 1.00 (α 0.15) | refused (α 0.05) / 0.44 (α 0.1) / 1.00 (α 0.15) |
| mnist | greedy_entropy | refused (α 0.03) / 1.00 (α 0.1) / 1.00 (α 0.15) | refused (α 0.03) / 1.00 (α 0.1) / 1.00 (α 0.15) | refused (α 0.03) / 1.00 (α 0.1) / 1.00 (α 0.15) |
| mnist | random | refused (α 0.03) / 1.00 (α 0.1) / 1.00 (α 0.15) | refused (α 0.03) / 1.00 (α 0.1) / 1.00 (α 0.15) | refused (α 0.03) / 1.00 (α 0.1) / 1.00 (α 0.15) |
| tabular-MiniBooNE | greedy_entropy | 0.00 (α 0.1) / 0.01 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.11) / 0.00 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.1) / 0.01 (α 0.15) / 1.00 (α 0.2) |
| tabular-MiniBooNE | random | 0.00 (α 0.1) / 0.26 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.11) / 0.38 (α 0.15) / 1.00 (α 0.2) | 0.00 (α 0.1) / 0.91 (α 0.15) / 1.00 (α 0.2) |
| tabular-adult | greedy_entropy | 0.00 (α 0.18) / 1.00 (α 0.25) / 1.00 (α 0.3) | 0.00 (α 0.18) / 0.00 (α 0.25) / 1.00 (α 0.3) | 0.00 (α 0.17) / 0.02 (α 0.2) / 1.00 (α 0.25) |
| tabular-adult | random | 0.00 (α 0.18) / 0.00 (α 0.25) / 1.00 (α 0.3) | 0.00 (α 0.18) / 0.29 (α 0.25) / 1.00 (α 0.3) | 0.00 (α 0.17) / 0.00 (α 0.2) / 1.00 (α 0.25) |
