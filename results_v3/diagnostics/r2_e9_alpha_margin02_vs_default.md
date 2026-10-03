# E9 α-rule sensitivity: margin 0.02 / grid 0.01 vs the committed rule (margin 0.05 / grid 0.05), seed 0

Sources: configs/committed_v3_am02_*_ts0.json vs configs/committed_v3_*_ts0.json; $RESULTS_ROOT/metrics_v3_alpha_margin02 vs metrics_v3 (5 splits x 20 draws); MNIST: no am02 commit (alpha 0.03 <= design margin 0.05, results_v3/logs/r2am02_commit_mnist_na_ts0.log).

Tier pattern = the tiers with share >= 0.05 at λ_ref `dep` (e.g. 1, 3, 1+3). Rows are ordered PhysioNet, Adult, then the rest.

| dataset | policy | α default → am02 | λ_ref dep default → am02 | G default → am02 | tiers 1/2/3/none default | tiers 1/2/3/none am02 | tier pattern changed | cert. deployment am02 | raw viol am02 | certified viol am02 | max_excess_se am02 | deepest verdict default → am02 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-physionet | greedy_entropy | 0.2 → 0.15 | 0.0000 → 0.0000 | 1 → 1 | 1.00/0.00/0.00/0.00 | 0.58/0.00/0.42/0.00 | yes (1 → 1+3) | 1.00 | 0.010 | 0.000 | -3.39 | feasible → feasible |
| csv-physionet | random | 0.2 → 0.15 | 0.0000 → 0.0000 | 1 → 1 | 1.00/0.00/0.00/0.00 | 0.58/0.00/0.42/0.00 | yes (1 → 1+3) | 1.00 | 0.010 | 0.000 | -3.18 | feasible → feasible |
| tabular-adult | greedy_entropy | 0.25 → 0.18 | 0.7576 → 0.8081 | 2 → 2 | 1.00/0.00/0.00/0.00 | 0.00/0.00/1.00/0.00 | yes (1 → 3) | 1.00 | 0.000 | 0.000 | -2.97 | feasible → type_II |
| tabular-adult | random | 0.25 → 0.18 | 0.7576 → 0.7576 | 3 → 3 | 0.00/0.00/1.00/0.00 | 0.00/0.00/1.00/0.00 | no (3) | 1.00 | 0.000 | 0.000 | -2.89 | unresolved → type_II |
| csv-diabetes | greedy_entropy | 0.15 → 0.12 | 0.7980 → 0.7980 | 2 → 2 | 0.00/0.00/1.00/0.00 | 0.00/0.00/1.00/0.00 | no (3) | 1.00 | 0.000 | 0.000 | -4.24 | type_II → type_II |
| csv-diabetes | random | 0.15 → 0.12 | 0.8283 → 0.9091 | 4 → 5 | 0.00/0.00/1.00/0.00 | 0.00/0.00/0.02/0.98 | yes (3 → none) | 0.02 | 0.000 | 0.000 | -0.80 | type_II → type_II |
| cube | greedy_entropy | 0.15 → 0.08 | 0.7980 → 0.9293 | 3 → 5 | 1.00/0.00/0.00/0.00 | 0.00/0.00/1.00/0.00 | yes (1 → 3) | 1.00 | 0.000 | 0.000 | -4.06 | feasible → type_II |
| cube | random | 0.15 → 0.08 | 0.7071 → 0.8990 | 4 → 5 | 0.99/0.00/0.01/0.00 | 0.00/0.00/0.99/0.01 | yes (1 → 3) | 0.99 | 0.000 | 0.000 | -3.98 | feasible → type_II |
| tabular-MiniBooNE | greedy_entropy | 0.15 → 0.1 | 0.7475 → 0.8788 | 3 → 5 | 0.01/0.00/0.99/0.00 | 0.00/0.00/1.00/0.00 | no (3) | 1.00 | 0.000 | 0.000 | -3.43 | feasible → type_II |
| tabular-MiniBooNE | random | 0.15 → 0.1 | 0.7778 → 0.8889 | 4 → 5 | 0.26/0.00/0.74/0.00 | 0.00/0.00/1.00/0.00 | yes (1+3 → 3) | 1.00 | 0.000 | 0.000 | -4.26 | feasible → type_II |
| fashionmnist | greedy_entropy | 0.15 → 0.09 | 0.7778 → 0.9293 | 5 → 5 | 0.12/0.00/0.88/0.00 | 0.00/0.00/1.00/0.00 | yes (1+3 → 3) | 1.00 | 0.000 | 0.000 | -4.17 | feasible → type_II |
| fashionmnist | random | 0.15 → 0.09 | 0.7778 → 0.9192 | 5 → 5 | 0.12/0.00/0.88/0.00 | 0.00/0.00/1.00/0.00 | yes (1+3 → 3) | 1.00 | 0.000 | 0.000 | -3.43 | feasible → type_II |
| mnist | greedy_entropy | 0.1 → not committed | | | | | | | | | | |
| mnist | random | 0.1 → not committed | | | | | | | | | | |
