# CAFA v2 -- CANONICAL RESULTS (the lock)

## Provenance

- generated: 2026-07-12T12:55:36.525714+00:00
- host: tinyx (Linux)
- git commit: 20e59d92a55cca92e2877c5f8101918c1edaee67
- numpy: 2.4.2
- environment lock: repro/requirements.lock.txt
- frozen-file hashes (repro/MANIFEST.sha256, CRLF-normalized check):
  - `c37ab67bbb02890699c73939fd824d54d2c4b6c5fcebdf2f99b94cd39db81490  src/cafa/risk_control.py`
  - `3ec1258ad95d0cf76345326f7323072212502132a6c397622fbd25f52d997dd3  tests/test_risk_control.py`

## Committed targets: {floor -> alpha} per (dataset, train_seed)

| dataset | train_seed | probe floor | alpha | note |
|---|---|---|---|---|
| mnist | 0 | 0.0779 | 0.15 | |
| mnist | 1 | 0.1011 | 0.2 | |
| mnist | 2 | 0.0943 | 0.15 | |
| tabular:MiniBooNE | 0 | 0.0844 | 0.15 | |
| tabular:MiniBooNE | 1 | 0.0886 | 0.15 | |
| tabular:MiniBooNE | 2 | 0.0938 | 0.15 | |
| tabular:adult | 0 | 0.1465 | 0.2 | |
| tabular:adult | 1 | 0.1614 | 0.25 | |
| tabular:adult | 2 | 0.1454 | 0.2 | |
| tabular:spambase | 0 | 0.0543 | 0.15 | |
| tabular:spambase | 1 | 0.0707 | 0.15 | |
| tabular:spambase | 2 | 0.0652 | 0.15 | |
| mnist | -- | -- | -- | STEP CROSSING across seeds: {0: 0.15, 1: 0.2, 2: 0.15} (fixed rule per backbone; report per-seed, never mix) |
| tabular:adult | -- | -- | -- | STEP CROSSING across seeds: {0: 0.2, 1: 0.25, 2: 0.2} (fixed rule per backbone; report per-seed, never mix) |

## Gate table (every cell, all seeds; delta per cell; Wilson 95% UB)

| cell | alpha | marginal viol [UB] | gate | IUT viol [UB] | gate |
|---|---|---|---|---|---|
| mnist/eps_greedy_eps0.25/ts0 | 0.15 | 0.110 [0.150] | FAIL | 0.007 [0.024] | PASS |
| mnist/eps_greedy_eps0.5/ts0 | 0.15 | 0.140 [0.184] | FAIL | 0.007 [0.024] | PASS |
| mnist/greedy_entropy/ts0 | 0.15 | 0.020 [0.043] | PASS | 0.033 [0.060] | PASS |
| mnist/greedy_entropy/ts0[margin] | 0.15 | 0.010 [0.029] | PASS | 0.033 [0.060] | PASS |
| mnist/random/ts0 | 0.15 | 0.000 [0.013] | PASS | 0.027 [0.052] | PASS |
| mnist/greedy_entropy/ts1 | 0.2 | 0.010 [0.029] | PASS | 0.033 [0.060] | PASS |
| mnist/random/ts1 | 0.2 | 0.060 [0.093] | PASS | 0.030 [0.056] | PASS |
| mnist/greedy_entropy/ts2 | 0.15 | 0.060 [0.093] | PASS | 0.000 [0.013] | PASS |
| mnist/random/ts2 | 0.15 | 0.010 [0.029] | PASS | 0.000 [0.013] | PASS |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.15 | 0.080 [0.116] | FAIL | 0.053 [0.085] | PASS |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-MiniBooNE/greedy_entropy/ts0[margin] | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-MiniBooNE/random/ts0 | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.15 | 0.050 [0.081] | PASS | 0.033 [0.060] | PASS |
| tabular-MiniBooNE/random/ts1 | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-MiniBooNE/random/ts2 | 0.15 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.2 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.2 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-adult/greedy_entropy/ts0 | 0.2 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-adult/greedy_entropy/ts0[margin] | 0.2 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-adult/random/ts0 | 0.2 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-adult/greedy_entropy/ts1 | 0.25 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-adult/random/ts1 | 0.25 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-adult/greedy_entropy/ts2 | 0.2 | 0.010 [0.029] | PASS | 0.007 [0.024] | PASS |
| tabular-adult/random/ts2 | 0.2 | 0.000 [0.013] | PASS | 0.000 [0.013] | PASS |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.15 | 0.090 [0.128] | FAIL | 0.050 [0.081] | PASS |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.15 | 0.050 [0.081] | PASS | 0.043 [0.073] | PASS |
| tabular-spambase/greedy_entropy/ts0 | 0.15 | 0.030 [0.056] | PASS | 0.037 [0.064] | PASS |
| tabular-spambase/random/ts0 | 0.15 | 0.110 [0.150] | FAIL | 0.047 [0.077] | PASS |
| tabular-spambase/greedy_entropy/ts1 | 0.15 | 0.100 [0.139] | FAIL | 0.047 [0.077] | PASS |
| tabular-spambase/random/ts1 | 0.15 | 0.060 [0.093] | PASS | 0.033 [0.060] | PASS |
| tabular-spambase/greedy_entropy/ts2 | 0.15 | 0.030 [0.056] | PASS | 0.020 [0.043] | PASS |
| tabular-spambase/random/ts2 | 0.15 | 0.010 [0.029] | PASS | 0.017 [0.038] | PASS |

## H2 at lambda_ref = 0.9 (primary scheme; violation / mean cost / cost-vs-full)

| cell | cafa_marginal | plugin | fixed_conf_0.95 | budget_10 | oracle_cheapest | oracle_full |
|---|---|---|---|---|---|---|
| mnist/eps_greedy_eps0.25/ts0 | 0.11 / 22.29 / 0.455 | 0.22 / 21.59 / 0.441 | 0.00 / 35.55 / 0.725 | 1.00 / 10.00 / 0.204 | 0.00 / 21.59 / 0.441 | 0.00 / 49.00 / 1.000 |
| mnist/eps_greedy_eps0.5/ts0 | 0.14 / 21.62 / 0.441 | 0.21 / 20.99 / 0.428 | 0.00 / 35.67 / 0.728 | 1.00 / 10.00 / 0.204 | 0.00 / 21.04 / 0.429 | 0.00 / 49.00 / 1.000 |
| mnist/greedy_entropy/ts0 | 0.02 / 24.85 / 0.507 | 0.35 / 24.08 / 0.491 | 0.00 / 36.35 / 0.742 | 1.00 / 10.00 / 0.204 | 0.00 / 24.03 / 0.490 | 0.00 / 49.00 / 1.000 |
| mnist/random/ts0 | 0.00 / 25.90 / 0.529 | 0.44 / 25.39 / 0.518 | 0.00 / 39.94 / 0.815 | 1.00 / 10.00 / 0.204 | 0.00 / 25.39 / 0.518 | 0.00 / 49.00 / 1.000 |
| mnist/greedy_entropy/ts1 | 0.01 / 25.90 / 0.529 | 0.59 / 25.04 / 0.511 | 0.00 / 39.21 / 0.800 | 1.00 / 10.00 / 0.204 | 0.00 / 25.25 / 0.515 | 0.00 / 49.00 / 1.000 |
| mnist/random/ts1 | 0.06 / 27.30 / 0.557 | 0.22 / 26.82 / 0.547 | 0.00 / 40.85 / 0.834 | 1.00 / 10.00 / 0.204 | 0.00 / 26.89 / 0.549 | 0.00 / 49.00 / 1.000 |
| mnist/greedy_entropy/ts2 | 0.06 / 36.20 / 0.739 | 0.17 / 34.79 / 0.710 | 0.00 / 36.31 / 0.741 | 1.00 / 10.00 / 0.204 | 0.00 / 34.79 / 0.710 | 0.00 / 49.00 / 1.000 |
| mnist/random/ts2 | 0.01 / 30.01 / 0.612 | 0.36 / 29.23 / 0.597 | 0.00 / 38.68 / 0.789 | 1.00 / 10.00 / 0.204 | 0.00 / 29.24 / 0.597 | 0.00 / 49.00 / 1.000 |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.08 / 20.99 / 0.062 | 0.15 / 19.46 / 0.057 | 0.00 / 136.41 / 0.400 | 0.00 / 56.73 / 0.166 | 0.00 / 19.46 / 0.057 | 0.00 / 341.06 / 1.000 |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.00 / 29.95 / 0.088 | 0.49 / 28.50 / 0.084 | 0.00 / 143.75 / 0.421 | 0.00 / 59.45 / 0.174 | 0.00 / 28.78 / 0.084 | 0.00 / 341.06 / 1.000 |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.00 / 17.01 / 0.050 | 0.00 / 17.01 / 0.050 | 0.00 / 132.49 / 0.388 | 0.00 / 55.52 / 0.163 | 0.00 / 17.01 / 0.050 | 0.00 / 341.06 / 1.000 |
| tabular-MiniBooNE/random/ts0 | 0.00 / 56.48 / 0.166 | 0.30 / 54.10 / 0.159 | 0.00 / 168.16 / 0.493 | 1.00 / 68.22 / 0.200 | 0.00 / 54.48 / 0.160 | 0.00 / 341.06 / 1.000 |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.05 / 11.66 / 0.034 | 0.13 / 10.31 / 0.030 | 0.00 / 120.86 / 0.353 | 0.00 / 55.15 / 0.161 | 0.00 / 10.35 / 0.030 | 0.00 / 342.28 / 1.000 |
| tabular-MiniBooNE/random/ts1 | 0.00 / 55.63 / 0.163 | 0.08 / 53.55 / 0.156 | 0.00 / 183.38 / 0.536 | 1.00 / 68.41 / 0.200 | 0.00 / 53.32 / 0.156 | 0.00 / 342.28 / 1.000 |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.00 / 18.74 / 0.055 | 0.00 / 18.74 / 0.055 | 0.00 / 121.19 / 0.355 | 0.00 / 52.19 / 0.153 | 0.00 / 18.74 / 0.055 | 0.00 / 341.73 / 1.000 |
| tabular-MiniBooNE/random/ts2 | 0.00 / 60.34 / 0.177 | 0.09 / 57.13 / 0.167 | 0.00 / 164.37 / 0.481 | 1.00 / 68.34 / 0.200 | 0.00 / 57.33 / 0.168 | 0.00 / 341.73 / 1.000 |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.00 / 32.38 / 0.340 | 0.00 / 32.38 / 0.340 | 0.00 / 56.67 / 0.595 | 0.00 / 67.58 / 0.709 | 0.00 / 32.38 / 0.340 | 0.00 / 95.28 / 1.000 |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.00 / 30.60 / 0.321 | 0.00 / 30.60 / 0.321 | 0.00 / 57.99 / 0.609 | 0.00 / 67.24 / 0.706 | 0.00 / 30.60 / 0.321 | 0.00 / 95.28 / 1.000 |
| tabular-adult/greedy_entropy/ts0 | 0.00 / 34.36 / 0.361 | 0.00 / 34.36 / 0.361 | 0.00 / 56.33 / 0.591 | 0.00 / 68.35 / 0.717 | 0.00 / 34.36 / 0.361 | 0.00 / 95.28 / 1.000 |
| tabular-adult/random/ts0 | 0.00 / 26.41 / 0.277 | 0.00 / 26.41 / 0.277 | 0.00 / 62.74 / 0.658 | 0.00 / 68.04 / 0.714 | 0.00 / 26.41 / 0.277 | 0.00 / 95.28 / 1.000 |
| tabular-adult/greedy_entropy/ts1 | 0.00 / 29.22 / 0.310 | 0.16 / 24.52 / 0.260 | 0.00 / 56.87 / 0.604 | 0.00 / 71.35 / 0.757 | 0.00 / 26.03 / 0.276 | 0.00 / 94.22 / 1.000 |
| tabular-adult/random/ts1 | 0.00 / 18.89 / 0.200 | 0.16 / 15.86 / 0.168 | 0.00 / 64.69 / 0.687 | 0.00 / 67.30 / 0.714 | 0.00 / 16.82 / 0.179 | 0.00 / 94.22 / 1.000 |
| tabular-adult/greedy_entropy/ts2 | 0.01 / 19.58 / 0.210 | 0.01 / 18.00 / 0.193 | 0.00 / 61.07 / 0.654 | 0.00 / 69.43 / 0.743 | 0.00 / 18.03 / 0.193 | 0.00 / 93.43 / 1.000 |
| tabular-adult/random/ts2 | 0.00 / 21.62 / 0.231 | 0.00 / 21.47 / 0.230 | 0.00 / 62.83 / 0.673 | 0.00 / 66.79 / 0.715 | 0.00 / 21.47 / 0.230 | 0.00 / 93.43 / 1.000 |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.09 / 45.30 / 0.109 | 0.31 / 32.51 / 0.079 | 0.00 / 154.01 / 0.372 | 0.40 / 63.11 / 0.153 | 0.00 / 32.68 / 0.079 | 0.00 / 413.78 / 1.000 |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.05 / 49.30 / 0.119 | 0.30 / 37.84 / 0.091 | 0.00 / 167.48 / 0.405 | 0.52 / 64.40 / 0.156 | 0.00 / 37.45 / 0.091 | 0.00 / 413.78 / 1.000 |
| tabular-spambase/greedy_entropy/ts0 | 0.03 / 37.80 / 0.091 | 0.45 / 23.67 / 0.057 | 0.00 / 145.11 / 0.351 | 0.00 / 62.49 / 0.151 | 0.00 / 23.63 / 0.057 | 0.00 / 413.78 / 1.000 |
| tabular-spambase/random/ts0 | 0.11 / 86.16 / 0.208 | 0.47 / 68.91 / 0.167 | 0.00 / 218.15 / 0.527 | 1.00 / 72.55 / 0.175 | 0.00 / 69.50 / 0.168 | 0.00 / 413.78 / 1.000 |
| tabular-spambase/greedy_entropy/ts1 | 0.10 / 73.69 / 0.173 | 0.47 / 62.89 / 0.148 | 0.00 / 162.85 / 0.383 | 1.00 / 69.24 / 0.163 | 0.00 / 62.90 / 0.148 | 0.00 / 425.41 / 1.000 |
| tabular-spambase/random/ts1 | 0.06 / 86.19 / 0.203 | 0.37 / 67.65 / 0.159 | 0.00 / 218.77 / 0.514 | 1.00 / 74.62 / 0.175 | 0.00 / 68.11 / 0.160 | 0.00 / 425.41 / 1.000 |
| tabular-spambase/greedy_entropy/ts2 | 0.03 / 69.24 / 0.170 | 0.48 / 38.15 / 0.093 | 0.00 / 133.01 / 0.326 | 0.77 / 67.76 / 0.166 | 0.00 / 36.22 / 0.089 | 0.00 / 408.08 / 1.000 |
| tabular-spambase/random/ts2 | 0.01 / 85.25 / 0.209 | 0.37 / 68.97 / 0.169 | 0.00 / 201.84 / 0.495 | 1.00 / 71.48 / 0.175 | 0.00 / 66.76 / 0.164 | 0.00 / 408.08 / 1.000 |

## H3 audit at lambda_ref = 0.9 (greedy; hardest stratum k*)

| dataset | ts | k* | R_full(k*) [95% CP LCB] | verdict | marginal realized risk on k* |
|---|---|---|---|---|---|
| mnist | 0 | 4 | 0.2479 [0.2383] | infeasible | 0.3005 |
| mnist | 1 | 4 | 0.2657 [0.2575] | infeasible | 0.3282 |
| mnist | 2 | 4 | 0.2681 [0.2579] | infeasible | 0.2683 |
| tabular-MiniBooNE | 0 | 4 | 0.2334 [0.2262] | infeasible | 0.3559 |
| tabular-MiniBooNE | 1 | 4 | 0.2226 [0.2156] | infeasible | 0.4203 |
| tabular-MiniBooNE | 2 | 4 | 0.2490 [0.2417] | infeasible | 0.3935 |
| tabular-adult | 0 | 3 | 0.3092 [0.2996] | infeasible | 0.3136 |
| tabular-adult | 1 | 4 | 0.3155 [0.3056] | infeasible | 0.3240 |
| tabular-adult | 2 | 3 | 0.3017 [0.2915] | infeasible | 0.3624 |
| tabular-spambase | 0 | 4 | 0.1727 [0.1344] | undetermined | 0.3844 |
| tabular-spambase | 1 | 4 | 0.1700 [0.1398] | undetermined | 0.3293 |
| tabular-spambase | 2 | 4 | 0.1576 [0.1245] | undetermined | 0.3707 |

Cross-seed stability: mnist: STABLE (infeasible); tabular-MiniBooNE: STABLE (infeasible); tabular-adult: STABLE (infeasible); tabular-spambase: STABLE (undetermined).

## IUT abstention / cost premium by lambda_ref (greedy, ts0, primary scheme)

| dataset | lambda_ref | abstention | premium vs marginal |
|---|---|---|---|
| mnist | 0.5 | 0.00 | 1.235 |
| mnist | 0.7 | 0.92 | 1.918 |
| mnist | 0.9 | 1.00 | 1.972 |
| tabular-MiniBooNE | 0.5 | 0.00 | 1.000 |
| tabular-MiniBooNE | 0.7 | 0.00 | 1.000 |
| tabular-MiniBooNE | 0.9 | 1.00 | 20.048 |
| tabular-adult | 0.5 | 0.00 | 1.000 |
| tabular-adult | 0.7 | 0.00 | 1.000 |
| tabular-adult | 0.9 | 1.00 | 2.773 |
| tabular-spambase | 0.5 | 0.00 | 1.000 |
| tabular-spambase | 0.7 | 0.80 | 9.856 |
| tabular-spambase | 0.9 | 1.00 | 10.946 |

## Alpha-sweep (corrected): MEASURED verdict at the committed alpha (ts0, greedy)

| dataset | floor | committed alpha | plugin viol AT committed alpha [95% CI] | verdict (measured) | transition bracket | H2 cross-check |
|---|---|---|---|---|---|---|
| mnist | 0.0779 | 0.15 | 0.350 [0.264, 0.447] | **UNSAFE** | never safe in range (last 0.2779) | PASS |
| tabular-MiniBooNE | 0.0844 | 0.15 | 0.000 [0.000, 0.037] | **SAFE** | (0.1344, 0.1363], res 0.0019 | PASS |
| tabular-adult | 0.1465 | 0.2 | 0.000 [0.000, 0.037] | **SAFE** | below the swept range (safe at 0.1665) | PASS |
| tabular-spambase | 0.0543 | 0.15 | 0.450 [0.356, 0.548] | **UNSAFE** | (0.1643, 0.1693], res 0.005 | PASS |

The alpha at which the uncorrected heuristic flips from safe to unsafe lands at a different, a-priori unknowable offset per dataset; the principled fixed rule lands inside the UNSAFE regime on 2 of 4 datasets (BY MEASUREMENT at the committed alpha; the verdicts are asserted equal to the H2 table by the cross-check column).

Price of honesty: see analysis_v2/ALPHA_SWEEP.md and F5 (IUT abstention ~1.0 while any stratum is alpha-infeasible; ~0 once alpha clears the hardest stratum).

## Validity-estimator diagnostic (marginal gate, all cells)

LTT controls P(TRUE risk > alpha); the gate measures empirical test-split risk > alpha, and cost-minimising selection deploys the least-conservative certified threshold (true risk just below alpha by construction) -- so test-split violation frequencies OVERSTATE P(true risk > alpha). predicted = Phi((R_pool(lambda_hat) - alpha) / SE_test) is the rate expected from test-split noise alone under a perfectly valid certificate.

- Agreement over 35 cells: corr(predicted, observed) = 0.762; mean |observed - predicted| = 0.019.
- Cells with observed violation above delta, predicted vs observed:
  - mnist/eps_greedy_eps0.5/ts0: predicted 0.030, observed 0.140 [0.085, 0.221] (mean margin alpha - R_pool = 0.0084, SE_test = 0.0031)
  - mnist/eps_greedy_eps0.25/ts0: predicted 0.036, observed 0.110 [0.063, 0.186] (mean margin alpha - R_pool = 0.0080, SE_test = 0.0031)
  - tabular-spambase/random/ts0: predicted 0.041, observed 0.110 [0.063, 0.186] (mean margin alpha - R_pool = 0.0252, SE_test = 0.0115)
  - tabular-spambase/greedy_entropy/ts1: predicted 0.038, observed 0.100 [0.055, 0.174] (mean margin alpha - R_pool = 0.0268, SE_test = 0.0114)
  - tabular-spambase/eps_greedy_eps0.25/ts0: predicted 0.046, observed 0.090 [0.048, 0.162] (mean margin alpha - R_pool = 0.0242, SE_test = 0.0115)
  - tabular-MiniBooNE/eps_greedy_eps0.25/ts0: predicted 0.018, observed 0.080 [0.041, 0.150] (mean margin alpha - R_pool = 0.0070, SE_test = 0.0023)
  - mnist/random/ts1: predicted 0.034, observed 0.060 [0.028, 0.125] (mean margin alpha - R_pool = 0.0090, SE_test = 0.0035)
  - mnist/greedy_entropy/ts2: predicted 0.015, observed 0.060 [0.028, 0.125] (mean margin alpha - R_pool = 0.0118, SE_test = 0.0031)
  - tabular-spambase/random/ts1: predicted 0.040, observed 0.060 [0.028, 0.125] (mean margin alpha - R_pool = 0.0254, SE_test = 0.0115)
  - tabular-MiniBooNE/greedy_entropy/ts1: predicted 0.026, observed 0.050 [0.022, 0.112] (mean margin alpha - R_pool = 0.0073, SE_test = 0.0023)
  - tabular-spambase/eps_greedy_eps0.5/ts0: predicted 0.034, observed 0.050 [0.022, 0.112] (mean margin alpha - R_pool = 0.0254, SE_test = 0.0115)
- Full table: analysis_v2/VALIDITY_DIAGNOSTIC.md; figure F6.
- The guarantee itself is certified on truly independent draws by the G1 gate and the IUT union-null Monte-Carlo gate.

## IUT non-vacuity (lambda_ref = 0.9)

| dataset | committed alpha | min certifying alpha (swept) | IUT cost/full there | premium vs marginal there | R_full(k*) | H3 consistency |
|---|---|---|---|---|---|---|
| mnist | 0.15 | 0.2779 | 0.581 | 2.27 | 0.2479 | PASS |
| tabular-MiniBooNE | 0.15 | 0.2844 | 0.163 | 4.26 | 0.2334 | PASS |
| tabular-adult | 0.2 | 0.3465 | 0.361 | n/a | 0.3092 | PASS |
| tabular-spambase | 0.15 | 0.1743 | 0.993 | 17.28 | 0.1727 | PASS |

At the min certifying alpha the IUT certifies EVERY stratum simultaneously at a cost below full acquisition; below it, the hardest stratum is intrinsically alpha-infeasible (H3 fallback bound) and abstention is the only honest deployment. IUT gate cells with abstention 1.0 at a lambda_ref are labelled VACUOUS in analysis_v2/IUT_NONVACUITY.md (correctness-by-abstention).

## Phase 2 (epsilon axis) -- concentration + the flat frontier

- rho(quality_auc, depth_entropy_norm@0.5) = -0.746 (p = 0.0009)
- rho(quality_auc, depth_entropy_norm@0.7) = -0.484 (p = 0.0576)
- rho(quality_auc, depth_entropy_norm@0.9) = -0.197 (p = 0.4645)
- rho(quality_auc, detection frontier) = 0.576 (p = 0.0196) -- a BETWEEN-DATASET CONFOUND; the frontier is flat in epsilon within every dataset. NEVER quote this rho as support for a detection-delay claim.

## Phase 4 (score ablation)

**The audit finding IS robust to the readiness-score choice** on 3 of 3 tested datasets: mnist (infeasible), tabular-MiniBooNE (infeasible), tabular-adult (infeasible). The verdict at lambda_ref = 0.9 is unchanged when the stopping score is replaced by margin (with its own probe-committed stratification).

## Honest flags

- marginal gate FAIL: mnist/eps_greedy_eps0.25/ts0 (viol 0.110, Wilson UB 0.150). EXPLAINED: predicted-from-test-noise violation 0.036 under a perfectly valid certificate (validity diagnostic).
- marginal gate FAIL: mnist/eps_greedy_eps0.5/ts0 (viol 0.140, Wilson UB 0.184). EXPLAINED: predicted-from-test-noise violation 0.030 under a perfectly valid certificate (validity diagnostic).
- marginal gate borderline: mnist/random/ts1 (viol 0.060, Wilson UB 0.093). EXPLAINED: predicted-from-test-noise violation 0.034 under a perfectly valid certificate (validity diagnostic).
- marginal gate borderline: mnist/greedy_entropy/ts2 (viol 0.060, Wilson UB 0.093). EXPLAINED: predicted-from-test-noise violation 0.015 under a perfectly valid certificate (validity diagnostic).
- marginal gate FAIL: tabular-MiniBooNE/eps_greedy_eps0.25/ts0 (viol 0.080, Wilson UB 0.116). EXPLAINED: predicted-from-test-noise violation 0.018 under a perfectly valid certificate (validity diagnostic).
- marginal gate borderline: tabular-MiniBooNE/greedy_entropy/ts1 (viol 0.050, Wilson UB 0.081). EXPLAINED: predicted-from-test-noise violation 0.026 under a perfectly valid certificate (validity diagnostic).
- marginal gate FAIL: tabular-spambase/eps_greedy_eps0.25/ts0 (viol 0.090, Wilson UB 0.128). EXPLAINED: predicted-from-test-noise violation 0.046 under a perfectly valid certificate (validity diagnostic).
- marginal gate borderline: tabular-spambase/eps_greedy_eps0.5/ts0 (viol 0.050, Wilson UB 0.081). EXPLAINED: predicted-from-test-noise violation 0.034 under a perfectly valid certificate (validity diagnostic).
- marginal gate FAIL: tabular-spambase/random/ts0 (viol 0.110, Wilson UB 0.150). EXPLAINED: predicted-from-test-noise violation 0.041 under a perfectly valid certificate (validity diagnostic).
- marginal gate FAIL: tabular-spambase/greedy_entropy/ts1 (viol 0.100, Wilson UB 0.139). EXPLAINED: predicted-from-test-noise violation 0.038 under a perfectly valid certificate (validity diagnostic).
- marginal gate borderline: tabular-spambase/random/ts1 (viol 0.060, Wilson UB 0.093). EXPLAINED: predicted-from-test-noise violation 0.040 under a perfectly valid certificate (validity diagnostic).
- spambase verdicts are undetermined by sample size (probe n = 184), not evidence of feasibility.
- local (laptop) runs are development/replication only; their alphas differ (backbone nondeterminism) and none of their numbers are cited.

## Figure index

- F1_mnist[margin]_ts0
- F1_mnist_ts0
- F1_mnist_ts1
- F1_mnist_ts2
- F1_tabular-MiniBooNE[margin]_ts0
- F1_tabular-MiniBooNE_ts0
- F1_tabular-MiniBooNE_ts1
- F1_tabular-MiniBooNE_ts2
- F1_tabular-adult[margin]_ts0
- F1_tabular-adult_ts0
- F1_tabular-adult_ts1
- F1_tabular-adult_ts2
- F1_tabular-spambase_ts0
- F1_tabular-spambase_ts1
- F1_tabular-spambase_ts2
- F2_mnist[margin]_ts0
- F2_mnist_ts0
- F2_mnist_ts1
- F2_mnist_ts2
- F2_tabular-MiniBooNE[margin]_ts0
- F2_tabular-MiniBooNE_ts0
- F2_tabular-MiniBooNE_ts1
- F2_tabular-MiniBooNE_ts2
- F2_tabular-adult[margin]_ts0
- F2_tabular-adult_ts0
- F2_tabular-adult_ts1
- F2_tabular-adult_ts2
- F2_tabular-spambase_ts0
- F2_tabular-spambase_ts1
- F2_tabular-spambase_ts2
- F3_mnist
- F3_mnist[margin]
- F3_phase2_frontier
- F3_phase2_mnist
- F3_phase2_tabular-MiniBooNE
- F3_phase2_tabular-adult
- F3_phase2_tabular-spambase
- F3_tabular-MiniBooNE
- F3_tabular-MiniBooNE[margin]
- F3_tabular-adult
- F3_tabular-adult[margin]
- F3_tabular-spambase
- F4_mnist
- F4_mnist[margin]
- F4_phase2
- F4_tabular-MiniBooNE
- F4_tabular-MiniBooNE[margin]
- F4_tabular-adult
- F4_tabular-adult[margin]
- F4_tabular-spambase
- F5_mnist
- F5_tabular-MiniBooNE
- F5_tabular-adult
- F5_tabular-spambase
- F6_validity_diagnostic

---
STATUS: FROZEN -- no number in the paper may differ from this file.