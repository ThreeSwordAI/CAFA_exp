# CAFA v2 -- PLUGIN ALPHA SWEEP ON POOL RISK (Phase 5.3)

_Select on calibration, evaluate on the full pool. The committed alpha is measured directly; monotonicity is not assumed._

## mnist (floor 0.0779, committed alpha 0.15)

| alpha | note | POOL exceed [95% CI] | mean pool risk | fallbacks |
|---|---|---|---|---|
| 0.0979 |  | 0.01 [0.00, 0.05] | 0.0960 | 0 |
| 0.1279 |  | 0.17 [0.11, 0.26] | 0.1250 | 0 |
| 0.1500 | COMMITTED | 0.00 [0.00, 0.04] | 0.1467 | 0 |
| 0.1579 |  | 0.03 [0.01, 0.08] | 0.1548 | 0 |
| 0.1879 |  | 0.40 [0.31, 0.50] | 0.1841 | 0 |
| 0.2279 |  | 0.17 [0.11, 0.26] | 0.2244 | 0 |
| 0.2779 |  | 0.15 [0.09, 0.23] | 0.2742 | 0 |

- Transition: NONMONOTONE; no single safety transition exists (crossings at (0.0979, 0.1279], (0.1279, 0.1500], (0.1579, 0.1879]).
- MEASURED at committed alpha 0.15: pool exceed 0.000 [0.000, 0.037].

## tabular-MiniBooNE (floor 0.0844, committed alpha 0.15)

| alpha | note | POOL exceed [95% CI] | mean pool risk | fallbacks |
|---|---|---|---|---|
| 0.1044 |  | 0.26 [0.18, 0.35] | 0.1034 | 0 |
| 0.1344 |  | 0.00 [0.00, 0.04] | 0.1321 | 0 |
| 0.1500 | COMMITTED | 0.00 [0.00, 0.04] | 0.1326 | 0 |
| 0.1644 |  | 0.00 [0.00, 0.04] | 0.1326 | 0 |
| 0.1944 |  | 0.00 [0.00, 0.04] | 0.1326 | 0 |
| 0.2344 |  | 0.00 [0.00, 0.04] | 0.1326 | 0 |
| 0.2844 |  | 0.00 [0.00, 0.04] | 0.2777 | 0 |

- Transition: single crossing in (0.1044, 0.1344].
- MEASURED at committed alpha 0.15: pool exceed 0.000 [0.000, 0.037].

## tabular-adult (floor 0.1465, committed alpha 0.2)

| alpha | note | POOL exceed [95% CI] | mean pool risk | fallbacks |
|---|---|---|---|---|
| 0.1665 |  | 0.00 [0.00, 0.04] | 0.1610 | 0 |
| 0.1965 |  | 0.00 [0.00, 0.04] | 0.1612 | 0 |
| 0.2000 | COMMITTED | 0.00 [0.00, 0.04] | 0.1612 | 0 |
| 0.2265 |  | 0.00 [0.00, 0.04] | 0.1612 | 0 |
| 0.2565 |  | 0.00 [0.00, 0.04] | 0.2482 | 0 |
| 0.2965 |  | 0.00 [0.00, 0.04] | 0.2482 | 0 |
| 0.3465 |  | 0.00 [0.00, 0.04] | 0.2482 | 0 |

- Transition: safe (exceed <= 0.10) at every swept alpha; no crossing in range.
- MEASURED at committed alpha 0.2: pool exceed 0.000 [0.000, 0.037].

## tabular-spambase (floor 0.0543, committed alpha 0.15)

| alpha | note | POOL exceed [95% CI] | mean pool risk | fallbacks |
|---|---|---|---|---|
| 0.0743 |  | 0.22 [0.15, 0.31] | 0.0730 | 0 |
| 0.1043 |  | 0.39 [0.30, 0.49] | 0.1030 | 0 |
| 0.1343 |  | 0.44 [0.35, 0.54] | 0.1316 | 0 |
| 0.1500 | COMMITTED | 0.45 [0.36, 0.55] | 0.1438 | 0 |
| 0.1643 |  | 0.00 [0.00, 0.04] | 0.1557 | 0 |
| 0.2043 |  | 0.00 [0.00, 0.04] | 0.1582 | 0 |
| 0.2543 |  | 0.00 [0.00, 0.04] | 0.1582 | 0 |

- Transition: single crossing in (0.1500, 0.1643].
- MEASURED at committed alpha 0.15: pool exceed 0.450 [0.356, 0.548].
