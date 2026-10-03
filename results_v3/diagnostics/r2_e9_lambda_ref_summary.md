# E9 λ_ref sweep summary (round 2; 14 seed-0 cells; pooled over 5 splits x 20 draws)

Sources: results_v3/tables_e9_lambda_ref_{0.5,0.7,0.9}/TABLE_E4_cascade.csv, results_v3/tables/TABLE_E4_cascade.csv

| λ_ref key | cells | min certified | mean certified | mean tier-1 | mean tier-3 | max raw violation | cells raw > δ | max certified violation | cells certified > δ+0.05 | cells mean max_excess_se > 0 | cells none > 0.05 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 14 | 1.00 | 1.000 | 1.000 | 0.000 | 0.030 (fashionmnist random) | 0 | 0.000 (csv-diabetes greedy_entropy) | 0 | 0 | 0 |
| 0.7 | 14 | 1.00 | 1.000 | 0.972 | 0.028 | 0.130 (fashionmnist random) | 1: fashionmnist random 0.130 | 0.010 (fashionmnist random) | 0 | 0 | 0 |
| 0.9 | 14 | 0.00 | 0.919 | 0.156 | 0.763 | 0.170 (tabular-adult greedy_entropy) | 1: tabular-adult greedy_entropy 0.170 | 0.000 (csv-diabetes greedy_entropy) | 0 | 0 | 2: csv-diabetes greedy_entropy 1.00; csv-diabetes random 0.13 |
| dep | 14 | 1.00 | 1.000 | 0.536 | 0.464 | 0.100 (fashionmnist greedy_entropy) | 0 | 0.010 (fashionmnist random) | 0 | 0 | 0 |
