# E9 λ_ref sweep summary (round 2; 16 seed-0 cells; pooled over 5 splits x 20 draws)

Sources: results_v3/tables_e9_lambda_ref_{0.5,0.7,0.9}/TABLE_E4_cascade.csv, results_v3/tables/TABLE_E4_cascade.csv

| λ_ref key | cells | min certified | mean certified | mean tier-1 | mean tier-3 | max raw violation | cells raw > δ | max certified violation | cells certified > δ+0.05 | cells mean max_excess_se > 0 | cells none > 0.05 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 16 | 1.00 | 1.000 | 0.978 | 0.022 | 0.030 (fashionmnist random) | 0 | 0.000 (csv-diabetes greedy_entropy) | 0 | 0 | 0 |
| 0.7 | 16 | 1.00 | 1.000 | 0.908 | 0.092 | 0.130 (fashionmnist random) | 1: fashionmnist random 0.130 | 0.010 (fashionmnist random) | 0 | 0 | 0 |
| 0.9 | 16 | 0.00 | 0.929 | 0.139 | 0.791 | 0.170 (tabular-adult greedy_entropy) | 1: tabular-adult greedy_entropy 0.170 | 0.000 (csv-diabetes greedy_entropy) | 0 | 0 | 2: csv-diabetes greedy_entropy 1.00; csv-diabetes random 0.13 |
| dep | 16 | 1.00 | 1.000 | 0.487 | 0.513 | 0.100 (fashionmnist greedy_entropy) | 0 | 0.010 (fashionmnist random) | 0 | 0 | 0 |
