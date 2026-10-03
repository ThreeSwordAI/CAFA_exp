# TABLE_E9_alpha_margin (train seed 2, lambda_ref key = dep, scheme = uniform)

alpha = ceil-to-grid(probe floor + margin); per margin: alpha, tier-1 / tier-3 share, certified-deployment rate (cert) and deployed cost / T of the cascade (pooled over all draws).  "refused": commit_v3 refuses alpha <= design margin (rc 7); "TBD-RUN (not committed)": no commit yet (alpha from the rule); "TBD-RUN": committed, not swept.  lambda_ref and G per margin are in the csv.

Sources:
- margin 0.02 (grid 0.01): metrics `F:\CAFA_results\metrics_v3_alpha_margin02`, commits `configs\committed_v3_am02_{dsname}_ts2.json`
- margin 0.05 (grid 0.05): metrics `F:\CAFA_results\metrics_v3`, commits `configs\committed_v3_{dsname}_ts2.json`
- margin 0.10 (grid 0.05): metrics `F:\CAFA_results\metrics_v3_alpha_margin10`, commits `configs\committed_v3_am10_{dsname}_ts2.json`

| dataset | policy | margin 0.02 (grid 0.01) | margin 0.05 (grid 0.05, primary) | margin 0.10 (grid 0.05) |
|---|---|---|---|---|
| csv-diabetes | greedy_entropy | alpha 0.12: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.20: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 |
| csv-diabetes | random | alpha 0.12: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.20: tier1 0.55, tier3 0.45, cert 1.00, cost/T 0.63 |
| csv-physionet | greedy_entropy | alpha 0.15: tier1 0.80, tier3 0.20, cert 1.00, cost/T 0.36 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| csv-physionet | random | alpha 0.15: tier1 0.80, tier3 0.20, cert 1.00, cost/T 0.46 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| cube | greedy_entropy | alpha 0.08: tier1 0.00, tier3 0.53, cert 0.53, cost/T 1.00 | alpha 0.15: tier1 0.97, tier3 0.03, cert 1.00, cost/T 0.35 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.23 |
| cube | random | alpha 0.08: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.62 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.49 |
| fashionmnist | greedy_entropy | alpha 0.10: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.17 |
| fashionmnist | random | alpha 0.10: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.21 |
| image-imagenette | greedy_entropy | refused: alpha = 0.05 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 0.36, tier3 0.64, cert 1.00, cost/T 0.84 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.15 |
| image-imagenette | random | refused: alpha = 0.05 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 0.44, tier3 0.56, cert 1.00, cost/T 0.76 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.16 |
| mnist | greedy_entropy | refused: alpha = 0.03 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.10 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.08 |
| mnist | random | refused: alpha = 0.03 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.18 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.16 |
| tabular-adult | greedy_entropy | alpha 0.17: tier1 0.00, tier3 0.97, cert 0.97, cost/T 1.00 | alpha 0.20: tier1 0.02, tier3 0.98, cert 1.00, cost/T 0.99 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.19 |
| tabular-adult | random | alpha 0.17: tier1 0.00, tier3 0.70, cert 0.70, cost/T 1.00 | alpha 0.20: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.24 |
| tabular-MiniBooNE | greedy_entropy | alpha 0.10: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.01, tier3 0.99, cert 1.00, cost/T 0.99 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.13 |
| tabular-MiniBooNE | random | alpha 0.10: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.91, tier3 0.09, cert 1.00, cost/T 0.41 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.14 |
