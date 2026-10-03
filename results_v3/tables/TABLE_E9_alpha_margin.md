# TABLE_E9_alpha_margin (train seed 0, lambda_ref key = dep, scheme = uniform)

alpha = ceil-to-grid(probe floor + margin); per margin: alpha, tier-1 / tier-3 share, certified-deployment rate (cert) and deployed cost / T of the cascade (pooled over all draws).  "refused": commit_v3 refuses alpha <= design margin (rc 7); "TBD-RUN (not committed)": no commit yet (alpha from the rule); "TBD-RUN": committed, not swept.  lambda_ref and G per margin are in the csv.

Sources:
- margin 0.02 (grid 0.01): metrics `F:\CAFA_results\metrics_v3_alpha_margin02`, commits `configs\committed_v3_am02_{dsname}_ts0.json`
- margin 0.05 (grid 0.05): metrics `F:\CAFA_results\metrics_v3`, commits `configs\committed_v3_{dsname}_ts0.json`
- margin 0.10 (grid 0.05): metrics `F:\CAFA_results\metrics_v3_alpha_margin10`, commits `configs\committed_v3_am10_{dsname}_ts0.json`

| dataset | policy | margin 0.02 (grid 0.01) | margin 0.05 (grid 0.05, primary) | margin 0.10 (grid 0.05) |
|---|---|---|---|---|
| csv-diabetes | greedy_entropy | alpha 0.12: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.20: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 |
| csv-diabetes | random | alpha 0.12: tier1 0.00, tier3 0.02, cert 0.02, cost/T 1.00 | alpha 0.15: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.20: tier1 0.26, tier3 0.74, cert 1.00, cost/T 0.89 |
| csv-physionet | greedy_entropy | alpha 0.15: tier1 0.58, tier3 0.42, cert 1.00, cost/T 0.56 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| csv-physionet | random | alpha 0.15: tier1 0.58, tier3 0.42, cert 1.00, cost/T 0.62 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| cube | greedy_entropy | alpha 0.08: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.29 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.25 |
| cube | random | alpha 0.08: tier1 0.00, tier3 0.99, cert 0.99, cost/T 1.00 | alpha 0.15: tier1 0.99, tier3 0.01, cert 1.00, cost/T 0.58 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.49 |
| fashionmnist | greedy_entropy | alpha 0.09: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.12, tier3 0.88, cert 1.00, cost/T 0.93 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.13 |
| fashionmnist | random | alpha 0.09: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.12, tier3 0.88, cert 1.00, cost/T 0.93 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.17 |
| image-imagenette | greedy_entropy | refused: alpha = 0.05 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 0.20, tier3 0.80, cert 1.00, cost/T 0.88 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.19 |
| image-imagenette | random | refused: alpha = 0.05 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 0.09, tier3 0.91, cert 1.00, cost/T 0.94 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.15 |
| mnist | greedy_entropy | refused: alpha = 0.03 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.07 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.07 |
| mnist | random | refused: alpha = 0.03 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.18 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.16 |
| tabular-adult | greedy_entropy | alpha 0.18: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.21 | alpha 0.30: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| tabular-adult | random | alpha 0.18: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.25: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.30: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| tabular-MiniBooNE | greedy_entropy | alpha 0.10: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.01, tier3 0.99, cert 1.00, cost/T 0.99 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.15 |
| tabular-MiniBooNE | random | alpha 0.10: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.26, tier3 0.74, cert 1.00, cost/T 0.86 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.12 |
