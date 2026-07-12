# CAFA v2 -- IUT NON-VACUITY

_An abstaining certificate claims nothing, so 'zero IUT failures' at an operating point with abstention 1.0 is vacuously true. This report surfaces where the IUT CERTIFIES uniform per-stratum validity at lambda_ref = 0.9 (fine stratification) at a cost below full acquisition, extracted from the alpha-sweep (no re-run)._

## Minimum certifying alpha at lambda_ref = 0.9 (per dataset)

| dataset | committed alpha | min certifying alpha (swept grid) | abstention there | IUT cost/full | IUT premium vs marginal | R_full(k*) [H3] | consistency (min cert alpha > R_full(k*)) |
|---|---|---|---|---|---|---|---|
| mnist | 0.15 | 0.2779 | 0.00 | 0.581 | 2.27 | 0.2479 [LCB 0.2383] | PASS |
| tabular-MiniBooNE | 0.15 | 0.2844 | 0.00 | 0.163 | 4.26 | 0.2334 [LCB 0.2262] | PASS |
| tabular-adult | 0.2 | 0.3465 | 0.00 | 0.361 | n/a | 0.3092 [LCB 0.2996] | PASS |
| tabular-spambase | 0.15 | 0.1743 | 0.99 | 0.993 | 17.28 | 0.1727 [LCB 0.1344] | PASS |

Reading: at the min certifying alpha the IUT stops abstaining and certifies EVERY stratum simultaneously at a cost below full acquisition (cost/full < 1); below it, the hardest stratum is intrinsically alpha-infeasible (proven by the H3 fallback bound) and abstention -> full acquisition is the only honest deployment. The consistency column verifies the certification boundary sits above R_full(k*), as the theory requires.

## Vacuity labels (every gate cell; abstention per lambda_ref)

| cell | abstain@0.5 | abstain@0.7 | abstain@0.9 | vacuous@0.9 | non-vacuous somewhere |
|---|---|---|---|---|---|
| mnist/eps_greedy_eps0.25/ts0 | 0.00 | 1.00 | 1.00 | yes | yes |
| mnist/eps_greedy_eps0.5/ts0 | 0.00 | 1.00 | 1.00 | yes | yes |
| mnist/greedy_entropy/ts0 | 0.00 | 0.92 | 1.00 | yes | yes |
| mnist/greedy_entropy/ts0[margin] | 0.55 | 1.00 | 1.00 | yes | yes |
| mnist/greedy_entropy/ts1 | 0.00 | 0.96 | 1.00 | yes | yes |
| mnist/greedy_entropy/ts2 | 0.10 | 1.00 | 1.00 | yes | yes |
| mnist/random/ts0 | 0.23 | 1.00 | 1.00 | yes | yes |
| mnist/random/ts1 | 0.24 | 1.00 | 1.00 | yes | yes |
| mnist/random/ts2 | 1.00 | 1.00 | 1.00 | yes | no |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-MiniBooNE/greedy_entropy/ts0[margin] | 1.00 | 1.00 | 1.00 | yes | no |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-MiniBooNE/random/ts0 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-MiniBooNE/random/ts1 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-MiniBooNE/random/ts2 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-adult/greedy_entropy/ts0 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-adult/greedy_entropy/ts0[margin] | 0.00 | 1.00 | 1.00 | yes | yes |
| tabular-adult/greedy_entropy/ts1 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-adult/greedy_entropy/ts2 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-adult/random/ts0 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-adult/random/ts1 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-adult/random/ts2 | 0.00 | 0.00 | 1.00 | yes | yes |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.00 | 0.72 | 1.00 | yes | yes |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.00 | 0.81 | 1.00 | yes | yes |
| tabular-spambase/greedy_entropy/ts0 | 0.00 | 0.80 | 1.00 | yes | yes |
| tabular-spambase/greedy_entropy/ts1 | 0.00 | 0.97 | 0.99 | NO | yes |
| tabular-spambase/greedy_entropy/ts2 | 0.00 | 0.62 | 1.00 | yes | yes |
| tabular-spambase/random/ts0 | 0.00 | 0.01 | 0.98 | NO | yes |
| tabular-spambase/random/ts1 | 0.00 | 0.41 | 1.00 | yes | yes |
| tabular-spambase/random/ts2 | 0.00 | 0.77 | 1.00 | yes | yes |

An IUT gate PASS is evidence only where the cell is non-vacuous (it certified on at least some resplits at that lambda_ref); vacuous cells are correctness-by-abstention and are labelled so a reviewer does not have to do this arithmetic.