# CAFA v2 -- PLUGIN ON THE FULL-POOL ESTIMAND (Phase 5.3, Task 2)

_The plugin selects on the calibration half exactly as in the original experiment (selection asserted equal to the recorded threshold on every resplit); the selected threshold is then evaluated on the ENTIRE evaluation pool. 'The plugin's selected threshold exceeds the target on the fixed evaluation pool in x/100 calibration draws.' The three-way label is a descriptive benchmark classification (criterion 0.10), not a distribution-free guarantee; 0/100 does not mean 'safe'._

| cell | alpha | POOL exceed [95% CI] | test-half exceed | diff | mean pool risk (p5, p95) | cost/full | fallbacks | label |
|---|---|---|---|---|---|---|---|---|
| mnist/greedy_entropy/ts1 | 0.2 | 0.59 [0.49, 0.68] | 0.59 | 0.00 | 0.1969 (0.1924, 0.2001) | 0.511 | 0 | clearly unreliable |
| mnist/greedy_entropy/ts0[margin] | 0.15 | 0.49 [0.39, 0.59] | 0.49 | 0.00 | 0.1480 (0.1425, 0.1501) | 0.490 | 0 | clearly unreliable |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.15 | 0.49 [0.39, 0.59] | 0.49 | 0.00 | 0.1460 (0.1419, 0.1503) | 0.083 | 0 | clearly unreliable |
| tabular-spambase/greedy_entropy/ts2 | 0.15 | 0.47 [0.38, 0.57] | 0.48 | 0.01 | 0.1453 (0.1322, 0.1510) | 0.094 | 0 | clearly unreliable |
| tabular-spambase/greedy_entropy/ts0 | 0.15 | 0.45 [0.36, 0.55] | 0.45 | 0.00 | 0.1438 (0.1351, 0.1582) | 0.057 | 0 | clearly unreliable |
| tabular-spambase/random/ts1 | 0.15 | 0.37 [0.28, 0.47] | 0.37 | 0.00 | 0.1465 (0.1353, 0.1636) | 0.159 | 0 | clearly unreliable |
| tabular-MiniBooNE/random/ts0 | 0.15 | 0.30 [0.22, 0.40] | 0.30 | 0.00 | 0.1467 (0.1447, 0.1512) | 0.159 | 0 | clearly unreliable |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.15 | 0.26 [0.18, 0.35] | 0.31 | 0.05 | 0.1469 (0.1341, 0.1594) | 0.079 | 0 | clearly unreliable |
| tabular-spambase/greedy_entropy/ts1 | 0.15 | 0.25 [0.18, 0.34] | 0.47 | 0.22 | 0.1474 (0.1316, 0.1582) | 0.148 | 0 | clearly unreliable |
| mnist/random/ts1 | 0.2 | 0.22 [0.15, 0.31] | 0.22 | 0.00 | 0.1968 (0.1954, 0.2022) | 0.547 | 0 | clearly unreliable |
| mnist/eps_greedy_eps0.5/ts0 | 0.15 | 0.21 [0.14, 0.30] | 0.21 | 0.00 | 0.1476 (0.1410, 0.1524) | 0.429 | 0 | clearly unreliable |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.15 | 0.21 [0.14, 0.30] | 0.30 | 0.09 | 0.1460 (0.1353, 0.1564) | 0.092 | 0 | clearly unreliable |
| tabular-spambase/random/ts0 | 0.15 | 0.18 [0.12, 0.27] | 0.47 | 0.29 | 0.1464 (0.1310, 0.1600) | 0.167 | 0 | clearly unreliable |
| tabular-adult/greedy_entropy/ts1 | 0.25 | 0.16 [0.10, 0.24] | 0.16 | 0.00 | 0.1787 (0.1644, 0.2537) | 0.260 | 0 | clearly unreliable |
| tabular-adult/random/ts1 | 0.25 | 0.16 [0.10, 0.24] | 0.16 | 0.00 | 0.2104 (0.2021, 0.2537) | 0.168 | 0 | clearly unreliable |
| tabular-spambase/random/ts2 | 0.15 | 0.16 [0.10, 0.24] | 0.37 | 0.21 | 0.1448 (0.1322, 0.1618) | 0.170 | 0 | clearly unreliable |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.15 | 0.13 [0.08, 0.21] | 0.13 | 0.00 | 0.1473 (0.1468, 0.1523) | 0.030 | 0 | not shown unreliable at this resolution |
| tabular-MiniBooNE/random/ts2 | 0.15 | 0.09 [0.05, 0.16] | 0.09 | 0.00 | 0.1467 (0.1462, 0.1524) | 0.167 | 0 | not shown unreliable at this resolution |
| mnist/eps_greedy_eps0.25/ts0 | 0.15 | 0.08 [0.04, 0.15] | 0.22 | 0.14 | 0.1471 (0.1425, 0.1541) | 0.441 | 0 | not shown unreliable at this resolution |
| tabular-MiniBooNE/random/ts1 | 0.15 | 0.08 [0.04, 0.15] | 0.08 | 0.00 | 0.1458 (0.1453, 0.1521) | 0.156 | 0 | not shown unreliable at this resolution |
| mnist/random/ts2 | 0.15 | 0.07 [0.03, 0.14] | 0.36 | 0.29 | 0.1479 (0.1444, 0.1532) | 0.597 | 0 | not shown unreliable at this resolution |
| mnist/greedy_entropy/ts0 | 0.15 | 0.00 [0.00, 0.04] | 0.35 | 0.35 | 0.1467 (0.1424, 0.1492) | 0.492 | 0 | not shown unreliable at this resolution |
| mnist/random/ts0 | 0.15 | 0.00 [0.00, 0.04] | 0.44 | 0.44 | 0.1473 (0.1440, 0.1497) | 0.518 | 0 | not shown unreliable at this resolution |
| mnist/greedy_entropy/ts2 | 0.15 | 0.00 [0.00, 0.04] | 0.17 | 0.17 | 0.1461 (0.1376, 0.1478) | 0.710 | 0 | not shown unreliable at this resolution |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.15 | 0.00 [0.00, 0.04] | 0.15 | 0.15 | 0.1473 (0.1426, 0.1482) | 0.057 | 0 | not shown unreliable at this resolution |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.15 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1326 (0.1326, 0.1326) | 0.050 | 0 | not shown unreliable at this resolution |
| tabular-MiniBooNE/greedy_entropy/ts0[margin] | 0.15 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1326 (0.1326, 0.1326) | 0.050 | 0 | not shown unreliable at this resolution |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.15 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1395 (0.1395, 0.1395) | 0.055 | 0 | not shown unreliable at this resolution |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.2 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1653 (0.1653, 0.1653) | 0.340 | 0 | not shown unreliable at this resolution |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.2 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1717 (0.1717, 0.1717) | 0.321 | 0 | not shown unreliable at this resolution |
| tabular-adult/greedy_entropy/ts0 | 0.2 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1612 (0.1612, 0.1612) | 0.361 | 0 | not shown unreliable at this resolution |
| tabular-adult/greedy_entropy/ts0[margin] | 0.2 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1612 (0.1612, 0.1612) | 0.355 | 0 | not shown unreliable at this resolution |
| tabular-adult/random/ts0 | 0.2 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1830 (0.1830, 0.1830) | 0.277 | 0 | not shown unreliable at this resolution |
| tabular-adult/greedy_entropy/ts2 | 0.2 | 0.00 [0.00, 0.04] | 0.01 | 0.01 | 0.1923 (0.1923, 0.1923) | 0.193 | 0 | not shown unreliable at this resolution |
| tabular-adult/random/ts2 | 0.2 | 0.00 [0.00, 0.04] | 0.00 | 0.00 | 0.1877 (0.1877, 0.1877) | 0.229 | 0 | not shown unreliable at this resolution |