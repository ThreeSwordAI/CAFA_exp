# CAFA v2 -- PHASE 3 REPORT (backbone robustness across train seeds)

_Policy: greedy_entropy. Audit/H2 columns at lambda_ref = 0.9, primary cost scheme. alpha is committed per (dataset, train_seed) by the fixed rule on that backbone's probe floor -- a step crossing is the rule working, not an inconsistency._

## mnist

| ts | floor (probe) | alpha | marg viol [UB] | gate | IUT viol [UB] | gate | plugin viol@0.9 | cafa cost/full | cafa cost/oracle | IUT abstain@0.9 | k* | R_full(k*) [LCB] | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0779 | 0.15 | 0.020 [0.043] | PASS | 0.033 [0.060] | PASS | 0.35 | 0.507 | 1.034 | 1.00 | 4 | 0.2479 [0.2383] | infeasible |
| 1 | 0.1011 | 0.2 | 0.010 [0.029] | PASS | 0.033 [0.060] | PASS | 0.59 | 0.529 | 1.026 | 1.00 | 4 | 0.2657 [0.2575] | infeasible |
| 2 | 0.0943 | 0.15 | 0.060 [0.093] | PASS | 0.000 [0.013] | PASS | 0.17 | 0.739 | 1.041 | 1.00 | 4 | 0.2681 [0.2579] | infeasible |

- alpha step crossing across seeds: {0: 0.15, 1: 0.2, 2: 0.15} -- the fixed rule applied per backbone; report per-seed alpha, never mix.
- **Audit stability: STABLE** -- verdict 'infeasible' at lambda_ref=0.9 reproduced across train_seeds [0, 1, 2].

## tabular-MiniBooNE

| ts | floor (probe) | alpha | marg viol [UB] | gate | IUT viol [UB] | gate | plugin viol@0.9 | cafa cost/full | cafa cost/oracle | IUT abstain@0.9 | k* | R_full(k*) [LCB] | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0844 | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS | 0.00 | 0.050 | 1.000 | 1.00 | 4 | 0.2334 [0.2262] | infeasible |
| 1 | 0.0886 | 0.15 | 0.050 [0.081] | PASS | 0.033 [0.060] | PASS | 0.13 | 0.034 | 1.126 | 1.00 | 4 | 0.2226 [0.2156] | infeasible |
| 2 | 0.0938 | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS | 0.00 | 0.055 | 1.000 | 1.00 | 4 | 0.2490 [0.2417] | infeasible |

- **Audit stability: STABLE** -- verdict 'infeasible' at lambda_ref=0.9 reproduced across train_seeds [0, 1, 2].

## tabular-adult

| ts | floor (probe) | alpha | marg viol [UB] | gate | IUT viol [UB] | gate | plugin viol@0.9 | cafa cost/full | cafa cost/oracle | IUT abstain@0.9 | k* | R_full(k*) [LCB] | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.1465 | 0.2 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS | 0.00 | 0.361 | 1.000 | 1.00 | 3 | 0.3092 [0.2996] | infeasible |
| 1 | 0.1614 | 0.25 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS | 0.16 | 0.310 | 1.123 | 1.00 | 4 | 0.3155 [0.3056] | infeasible |
| 2 | 0.1454 | 0.2 | 0.010 [0.029] | PASS | 0.007 [0.024] | PASS | 0.01 | 0.210 | 1.085 | 1.00 | 3 | 0.3017 [0.2915] | infeasible |

- alpha step crossing across seeds: {0: 0.2, 1: 0.25, 2: 0.2} -- the fixed rule applied per backbone; report per-seed alpha, never mix.
- **Audit stability: STABLE** -- verdict 'infeasible' at lambda_ref=0.9 reproduced across train_seeds [0, 1, 2].

## tabular-spambase

| ts | floor (probe) | alpha | marg viol [UB] | gate | IUT viol [UB] | gate | plugin viol@0.9 | cafa cost/full | cafa cost/oracle | IUT abstain@0.9 | k* | R_full(k*) [LCB] | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0543 | 0.15 | 0.030 [0.056] | PASS | 0.037 [0.064] | PASS | 0.45 | 0.091 | 1.600 | 1.00 | 4 | 0.1727 [0.1344] | undetermined |
| 1 | 0.0707 | 0.15 | 0.100 [0.139] | FAIL | 0.047 [0.077] | PASS | 0.47 | 0.173 | 1.172 | 0.99 | 4 | 0.1700 [0.1398] | undetermined |
| 2 | 0.0652 | 0.15 | 0.030 [0.056] | PASS | 0.020 [0.043] | PASS | 0.48 | 0.170 | 1.912 | 1.00 | 4 | 0.1576 [0.1245] | undetermined |

- **Audit stability: STABLE** -- verdict 'undetermined' at lambda_ref=0.9 reproduced across train_seeds [0, 1, 2].

## Cross-seed stability verdict

- Replicates (same verdict at every seed): mnist (infeasible), tabular-MiniBooNE (infeasible), tabular-adult (infeasible), tabular-spambase (undetermined).
- Claim supported at this scope: the infeasible-stratum finding is a property of the data, not of a lucky backbone draw, on the datasets listed as replicating.