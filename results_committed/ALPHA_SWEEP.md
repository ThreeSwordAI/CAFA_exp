# CAFA v2 -- ALPHA SWEEP (corrected: measured at the committed alpha)

_Grid anchored to the committed probe floor, with the committed alpha as an explicit MEASURED grid point and the plugin transition bracketed by bisection. The verdict at the committed target is by measurement, never inference; the plugin violation at the committed alpha is asserted equal to the H2 table (cross-check column). delta = 0.1; n_resplits = 100._

## mnist (ts0, greedy_entropy, uniform; floor = 0.0779, committed alpha = 0.15)

| alpha | note | plugin viol [95% CI] | marginal viol [95% CI] | marg abstain | marg cost/full | IUT abstain | IUT cost/full | infeasible strata @0.9 |
|---|---|---|---|---|---|---|---|---|
| 0.0979 |  | 0.46 [0.37, 0.56] | 0.03 [0.01, 0.08] | 0.00 | 0.773 | 1.00 | 1.000 | 1 |
| 0.1279 |  | 0.17 [0.11, 0.26] | 0.05 [0.02, 0.11] | 0.00 | 0.587 | 1.00 | 1.000 | 1 |
| 0.1500 | COMMITTED | 0.35 [0.26, 0.45] | 0.02 [0.01, 0.07] | 0.00 | 0.507 | 1.00 | 1.000 | 1 |
| 0.1579 |  | 0.15 [0.09, 0.23] | 0.04 [0.02, 0.10] | 0.00 | 0.485 | 1.00 | 1.000 | 1 |
| 0.1879 |  | 0.40 [0.31, 0.50] | 0.00 [0.00, 0.04] | 0.00 | 0.407 | 1.00 | 1.000 | 1 |
| 0.2279 |  | 0.17 [0.11, 0.26] | 0.03 [0.01, 0.08] | 0.00 | 0.333 | 1.00 | 1.000 | 1 |
| 0.2779 |  | 0.15 [0.09, 0.23] | 0.07 [0.03, 0.14] | 0.00 | 0.256 | 0.00 | 0.581 | 0 |

- MEASURED at the committed alpha 0.15: plugin violation 0.350 [0.264, 0.447] -> **UNSAFE**; plugin never becomes safe in the swept range (last point 0.2779); H2 cross-check: PASS (H2 value 0.350).

## tabular-adult (ts0, greedy_entropy, inverse_info; floor = 0.1465, committed alpha = 0.2)

| alpha | note | plugin viol [95% CI] | marginal viol [95% CI] | marg abstain | marg cost/full | IUT abstain | IUT cost/full | infeasible strata @0.9 |
|---|---|---|---|---|---|---|---|---|
| 0.1665 |  | 0.04 [0.02, 0.10] | 0.04 [0.02, 0.10] | 0.00 | 0.469 | 1.00 | 1.000 | 1 |
| 0.1965 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.361 | 1.00 | 1.000 | 1 |
| 0.2000 | COMMITTED | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.361 | 1.00 | 1.000 | 1 |
| 0.2265 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.361 | 1.00 | 1.000 | 1 |
| 0.2565 |  | 0.01 [0.00, 0.05] | 0.01 [0.00, 0.05] | 0.00 | 0.187 | 1.00 | 1.000 | 1 |
| 0.2965 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.000 | 1.00 | 1.000 | 1 |
| 0.3465 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.000 | 0.00 | 0.361 | 0 |

- MEASURED at the committed alpha 0.2: plugin violation 0.000 [0.000, 0.037] -> **SAFE**; plugin already safe at the smallest swept alpha (0.1665); transition below the range; H2 cross-check: PASS (H2 value 0.000).

## tabular-MiniBooNE (ts0, greedy_entropy, inverse_info; floor = 0.0844, committed alpha = 0.15)

| alpha | note | plugin viol [95% CI] | marginal viol [95% CI] | marg abstain | marg cost/full | IUT abstain | IUT cost/full | infeasible strata @0.9 |
|---|---|---|---|---|---|---|---|---|
| 0.1044 |  | 0.28 [0.20, 0.37] | 0.07 [0.03, 0.14] | 0.00 | 0.167 | 1.00 | 1.000 | 1 |
| 0.1344 |  | 0.16 [0.10, 0.24] | 0.13 [0.08, 0.21] | 0.00 | 0.055 | 1.00 | 1.000 | 1 |
| 0.1363 | bracket | 0.02 [0.01, 0.07] | 0.02 [0.01, 0.07] | 0.00 | 0.053 | 1.00 | 1.000 | 1 |
| 0.1383 | bracket | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.051 | 1.00 | 1.000 | 1 |
| 0.1422 | bracket | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.050 | 1.00 | 1.000 | 1 |
| 0.1500 | COMMITTED | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.050 | 1.00 | 1.000 | 1 |
| 0.1644 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.050 | 1.00 | 1.000 | 1 |
| 0.1944 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.050 | 1.00 | 1.000 | 1 |
| 0.2344 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.050 | 1.00 | 1.000 | 0 |
| 0.2844 |  | 0.05 [0.02, 0.11] | 0.05 [0.02, 0.11] | 0.00 | 0.038 | 0.00 | 0.163 | 0 |

- MEASURED at the committed alpha 0.15: plugin violation 0.000 [0.000, 0.037] -> **SAFE**; transition in (0.1344, 0.1363], resolution 0.0019; H2 cross-check: PASS (H2 value 0.000).

## tabular-spambase (ts0, greedy_entropy, inverse_info; floor = 0.0543, committed alpha = 0.15)

| alpha | note | plugin viol [95% CI] | marginal viol [95% CI] | marg abstain | marg cost/full | IUT abstain | IUT cost/full | infeasible strata @0.9 |
|---|---|---|---|---|---|---|---|---|
| 0.0743 |  | 0.53 [0.43, 0.62] | 0.07 [0.03, 0.14] | 0.69 | 0.810 | 1.00 | 1.000 | 1 |
| 0.1043 |  | 0.45 [0.36, 0.55] | 0.06 [0.03, 0.12] | 0.00 | 0.203 | 1.00 | 1.000 | 1 |
| 0.1343 |  | 0.44 [0.35, 0.54] | 0.07 [0.03, 0.14] | 0.00 | 0.128 | 1.00 | 1.000 | 1 |
| 0.1500 | COMMITTED | 0.45 [0.36, 0.55] | 0.03 [0.01, 0.08] | 0.00 | 0.091 | 1.00 | 1.000 | 0 |
| 0.1643 |  | 0.21 [0.14, 0.30] | 0.04 [0.02, 0.10] | 0.00 | 0.068 | 1.00 | 1.000 | 0 |
| 0.1693 | bracket | 0.07 [0.03, 0.14] | 0.05 [0.02, 0.11] | 0.00 | 0.063 | 1.00 | 1.000 | 0 |
| 0.1743 | bracket | 0.03 [0.01, 0.08] | 0.03 [0.01, 0.08] | 0.00 | 0.057 | 0.99 | 0.993 | 0 |
| 0.1843 | bracket | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.049 | 0.99 | 0.993 | 0 |
| 0.2043 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.045 | 0.97 | 0.978 | 0 |
| 0.2543 |  | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.045 | 0.40 | 0.554 | 0 |

- MEASURED at the committed alpha 0.15: plugin violation 0.450 [0.356, 0.548] -> **UNSAFE**; transition in (0.1643, 0.1693], resolution 0.005; H2 cross-check: PASS (H2 value 0.450).

**Corrected headline: the alpha at which the uncorrected heuristic flips from safe to unsafe lands at a different, a-priori unknowable offset on each dataset, and the principled fixed rule lands inside the UNSAFE regime on 2 of 4 datasets (by measurement).**