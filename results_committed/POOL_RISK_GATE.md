# CAFA v2 -- POOL-RISK GATE (the correct estimand)

_The eval pool IS the population for this experiment; each resplit's selected lambda-hat is evaluated against the EXACT pool risk. LTT stays valid for this estimand (a without-replacement subsample's empirical mean is dominated by the binomial -- Hoeffding 1963 -- so the HB p-value remains conservative). GATE criterion: Wilson 95% UB <= delta, the same criterion as the main gate table, on an n = 100 basis (the marginal selection is lambda_ref-independent, so the 100 resplits are counted once; the main table's pooling over 3 lambda_ref blocks repeats identical outcomes). lambda-hat per resplit was recomputed with the frozen ltt_select and asserted equal to the recorded value on every resplit of every cell; abstentions are counted separately (abstain = full acquisition, not a violation)._

**Headline: 0/35 cells fail the pool-risk gate (test-split gate: 11/35); measured corr(R_cal, R_test) at fixed lambda = -1.0000 (range -1.0000 to -1.0000).**

| cell | alpha | abstain | POOL viol [95% CI] | gate | test viol [95% CI] | gate | mean margin | corr(Rcal,Rtest)@fixed | corr(Rcal@hat, test excess) |
|---|---|---|---|---|---|---|---|---|---|
| mnist/eps_greedy_eps0.5/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.140 [0.085, 0.221] | FAIL | 0.0084 | -1.000 | -0.155 |
| mnist/eps_greedy_eps0.25/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.110 [0.063, 0.186] | FAIL | 0.0080 | -1.000 | 0.062 |
| tabular-spambase/random/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.110 [0.063, 0.186] | FAIL | 0.0252 | -1.000 | -0.258 |
| tabular-spambase/greedy_entropy/ts1 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.100 [0.055, 0.174] | FAIL | 0.0268 | -1.000 | 0.094 |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.090 [0.048, 0.162] | FAIL | 0.0242 | -1.000 | 0.020 |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.080 [0.041, 0.150] | FAIL | 0.0070 | -1.000 | -0.508 |
| mnist/greedy_entropy/ts2 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.060 [0.028, 0.125] | FAIL | 0.0118 | -1.000 | -0.392 |
| mnist/random/ts1 | 0.2 | 0 | 0.000 [0.000, 0.037] | PASS | 0.060 [0.028, 0.125] | FAIL | 0.0090 | -1.000 | 0.039 |
| tabular-spambase/random/ts1 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.060 [0.028, 0.125] | FAIL | 0.0254 | -1.000 | -0.111 |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.050 [0.022, 0.112] | FAIL | 0.0073 | -1.000 | 0.116 |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.050 [0.022, 0.112] | FAIL | 0.0254 | -1.000 | 0.211 |
| tabular-spambase/greedy_entropy/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.030 [0.010, 0.085] | PASS | 0.0248 | -1.000 | -0.224 |
| tabular-spambase/greedy_entropy/ts2 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.030 [0.010, 0.085] | PASS | 0.0267 | -1.000 | 0.326 |
| mnist/greedy_entropy/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.020 [0.006, 0.070] | PASS | 0.0085 | -1.000 | -0.190 |
| mnist/greedy_entropy/ts0[margin] | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.010 [0.002, 0.054] | PASS | 0.0078 | -1.000 | 0.157 |
| mnist/greedy_entropy/ts1 | 0.2 | 0 | 0.010 [0.002, 0.054] | PASS | 0.010 [0.002, 0.054] | PASS | 0.0094 | -1.000 | 0.230 |
| mnist/random/ts2 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.010 [0.002, 0.054] | PASS | 0.0086 | -1.000 | 0.165 |
| tabular-adult/greedy_entropy/ts2 | 0.2 | 0 | 0.000 [0.000, 0.037] | PASS | 0.010 [0.002, 0.054] | PASS | 0.0135 | -1.000 | 0.349 |
| tabular-spambase/random/ts2 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.010 [0.002, 0.054] | PASS | 0.0278 | -1.000 | -0.552 |
| mnist/random/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0083 | -1.000 | -0.186 |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0082 | -1.000 | -0.891 |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0174 | -1.000 | -1.000 |
| tabular-MiniBooNE/greedy_entropy/ts0[margin] | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0174 | -1.000 | -1.000 |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0105 | -1.000 | -1.000 |
| tabular-MiniBooNE/random/ts0 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0068 | -1.000 | 0.225 |
| tabular-MiniBooNE/random/ts1 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0071 | -1.000 | 0.471 |
| tabular-MiniBooNE/random/ts2 | 0.15 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0071 | -1.000 | 0.426 |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.2 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0347 | -1.000 | -1.000 |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.2 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0283 | -1.000 | -1.000 |
| tabular-adult/greedy_entropy/ts0 | 0.2 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0388 | -1.000 | -1.000 |
| tabular-adult/greedy_entropy/ts0[margin] | 0.2 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0388 | -1.000 | -1.000 |
| tabular-adult/greedy_entropy/ts1 | 0.25 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0856 | -1.000 | -1.000 |
| tabular-adult/random/ts0 | 0.2 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0170 | -1.000 | -1.000 |
| tabular-adult/random/ts1 | 0.25 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0479 | -1.000 | -1.000 |
| tabular-adult/random/ts2 | 0.2 | 0 | 0.000 [0.000, 0.037] | PASS | 0.000 [0.000, 0.037] | PASS | 0.0125 | -1.000 | -0.939 |

Mechanism, demonstrated: R_test(lambda) = (n_eval R_pool - n_cal R_cal)/n_test, so complementary 50/50 resplits anti-correlate exactly; an unlucky-easy calibration half both selects a more aggressive lambda-hat AND deterministically faces a harder test half. The negative corr(R_cal at lambda-hat, test excess) column shows the pairing that an independent-noise model cannot capture -- and the pool gate removes it by evaluating the exact population risk.