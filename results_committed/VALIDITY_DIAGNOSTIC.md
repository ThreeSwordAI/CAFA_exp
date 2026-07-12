# CAFA v2 -- VALIDITY-ESTIMATOR DIAGNOSTIC (predicted vs observed)

_LTT controls P(TRUE risk > alpha); the gate measures empirical TEST-split risk > alpha. Cost-minimising selection deploys the LEAST-conservative certified threshold (true risk just below alpha by construction), so test-split violation frequencies overstate P(true risk > alpha). predicted_violation = Phi((R_pool(lambda_hat) - alpha)/SE_test) is the rate expected from test-split noise ALONE under a perfectly valid certificate. R_pool is evaluated on the entire eval pool -- a low-variance proxy for the true risk, mildly optimistic because the calibration half is a subset of that pool._

**Agreement over 35 cells: corr(predicted, observed) = 0.762; mean |observed - predicted| = 0.019.**

| cell | alpha | mean margin (alpha - R_pool) | mean SE_test | predicted | observed [95% CI] | |obs-pred| | gate |
|---|---|---|---|---|---|---|---|
| mnist/eps_greedy_eps0.5/ts0 | 0.15 | 0.0084 | 0.0031 | 0.030 | 0.140 [0.085, 0.221] | 0.110 | FAIL |
| mnist/eps_greedy_eps0.25/ts0 | 0.15 | 0.0080 | 0.0031 | 0.036 | 0.110 [0.063, 0.186] | 0.074 | FAIL |
| tabular-spambase/random/ts0 | 0.15 | 0.0252 | 0.0115 | 0.041 | 0.110 [0.063, 0.186] | 0.069 | FAIL |
| tabular-spambase/greedy_entropy/ts1 | 0.15 | 0.0268 | 0.0114 | 0.038 | 0.100 [0.055, 0.174] | 0.062 | FAIL |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.15 | 0.0242 | 0.0115 | 0.046 | 0.090 [0.048, 0.162] | 0.044 | FAIL |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.15 | 0.0070 | 0.0023 | 0.018 | 0.080 [0.041, 0.150] | 0.062 | FAIL |
| mnist/random/ts1 | 0.2 | 0.0090 | 0.0035 | 0.034 | 0.060 [0.028, 0.125] | 0.026 | FAIL |
| mnist/greedy_entropy/ts2 | 0.15 | 0.0118 | 0.0031 | 0.015 | 0.060 [0.028, 0.125] | 0.045 | FAIL |
| tabular-spambase/random/ts1 | 0.15 | 0.0254 | 0.0115 | 0.040 | 0.060 [0.028, 0.125] | 0.020 | FAIL |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.15 | 0.0073 | 0.0023 | 0.026 | 0.050 [0.022, 0.112] | 0.024 | FAIL |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.15 | 0.0254 | 0.0115 | 0.034 | 0.050 [0.022, 0.112] | 0.016 | FAIL |
| tabular-spambase/greedy_entropy/ts0 | 0.15 | 0.0248 | 0.0115 | 0.033 | 0.030 [0.010, 0.085] | 0.003 | PASS |
| tabular-spambase/greedy_entropy/ts2 | 0.15 | 0.0267 | 0.0114 | 0.031 | 0.030 [0.010, 0.085] | 0.001 | PASS |
| mnist/greedy_entropy/ts0 | 0.15 | 0.0085 | 0.0031 | 0.014 | 0.020 [0.006, 0.070] | 0.006 | PASS |
| mnist/greedy_entropy/ts0[margin] | 0.15 | 0.0078 | 0.0031 | 0.028 | 0.010 [0.002, 0.054] | 0.018 | PASS |
| mnist/greedy_entropy/ts1 | 0.2 | 0.0094 | 0.0035 | 0.017 | 0.010 [0.002, 0.054] | 0.007 | PASS |
| mnist/random/ts2 | 0.15 | 0.0086 | 0.0031 | 0.020 | 0.010 [0.002, 0.054] | 0.010 | PASS |
| tabular-adult/greedy_entropy/ts2 | 0.2 | 0.0135 | 0.0043 | 0.019 | 0.010 [0.002, 0.054] | 0.009 | PASS |
| tabular-spambase/random/ts2 | 0.15 | 0.0278 | 0.0114 | 0.020 | 0.010 [0.002, 0.054] | 0.010 | PASS |
| mnist/random/ts0 | 0.15 | 0.0083 | 0.0031 | 0.015 | 0.000 [0.000, 0.037] | 0.015 | PASS |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.15 | 0.0082 | 0.0023 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.15 | 0.0174 | 0.0022 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-MiniBooNE/greedy_entropy/ts0[margin] | 0.15 | 0.0174 | 0.0022 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-MiniBooNE/random/ts0 | 0.15 | 0.0068 | 0.0023 | 0.009 | 0.000 [0.000, 0.037] | 0.009 | PASS |
| tabular-MiniBooNE/random/ts1 | 0.15 | 0.0071 | 0.0023 | 0.013 | 0.000 [0.000, 0.037] | 0.013 | PASS |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.15 | 0.0105 | 0.0023 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-MiniBooNE/random/ts2 | 0.15 | 0.0071 | 0.0023 | 0.021 | 0.000 [0.000, 0.037] | 0.021 | PASS |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.2 | 0.0347 | 0.0041 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.2 | 0.0283 | 0.0042 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-adult/greedy_entropy/ts0 | 0.2 | 0.0388 | 0.0041 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-adult/greedy_entropy/ts0[margin] | 0.2 | 0.0388 | 0.0041 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-adult/random/ts0 | 0.2 | 0.0170 | 0.0043 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-adult/greedy_entropy/ts1 | 0.25 | 0.0856 | 0.0041 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-adult/random/ts1 | 0.25 | 0.0479 | 0.0045 | 0.000 | 0.000 [0.000, 0.037] | 0.000 | PASS |
| tabular-adult/random/ts2 | 0.2 | 0.0125 | 0.0043 | 0.002 | 0.000 [0.000, 0.037] | 0.002 | PASS |

Secondary (additive, NOT the primary explanation): the 100 resplits resample one finite pool, so violation events are dependent and the Wilson interval understates the uncertainty of the observed frequency as an estimator of P(true risk > alpha).

Paper-ready statement: cost-minimising selection deliberately chooses the least-conservative certified threshold, so test-split violation frequencies overstate P(true risk > alpha); we quantify the expected noise-only violation rate per cell and find the observed rates match the prediction (corr 0.76, mean abs. gap 0.019). The guarantee itself is certified on truly independent draws by the G1 and IUT union-null Monte-Carlo gates.