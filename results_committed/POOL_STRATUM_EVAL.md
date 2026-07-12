# CAFA v2 -- SELECTED-RULE PER-STRATUM POOL RISK (Phase 5.3, Task 3)

_The marginal CAFA threshold selected on each calibration half is evaluated on the ENTIRE evaluation pool, per probe-committed stratum (fixed across resplits). Spread columns describe VARIATION ACROSS CALIBRATION SELECTIONS, not population confidence intervals. Weighted per-stratum risks reconstruct the aggregate exactly (asserted per resplit)._

## Primary cells (ts0 greedy softmax, lambda_ref = 0.9)

| dataset | stratum | n_k | q_k | mean pool risk (p5, p95) | exceed freq | ratio to alpha | endpoint full risk | selected - endpoint |
|---|---|---|---|---|---|---|---|---|
| mnist | 0 | 4906 | 0.1947 | 0.0913 (0.0913, 0.0913) | 0.00 | 0.609 | 0.0444 | 0.0469 |
| mnist | 1 | 5152 | 0.2044 | 0.1133 (0.1118, 0.1135) | 0.00 | 0.755 | 0.0450 | 0.0683 |
| mnist | 2 | 5490 | 0.2179 | 0.0948 (0.0929, 0.0951) | 0.00 | 0.632 | 0.0392 | 0.0556 |
| mnist | 3 | 4173 | 0.1656 | 0.0876 (0.0752, 0.0899) | 0.00 | 0.584 | 0.0312 | 0.0565 |
| mnist | 4 | 5479 | 0.2174 | 0.3006 (0.2887, 0.3026) | 1.00 | 2.004 | 0.2479 | 0.0527 |
| tabular-MiniBooNE | 0 | 7345 | 0.1569 | 0.0253 (0.0253, 0.0253) | 0.00 | 0.169 | 0.0163 | 0.0090 |
| tabular-MiniBooNE | 1 | 8863 | 0.1893 | 0.0431 (0.0431, 0.0431) | 0.00 | 0.287 | 0.0327 | 0.0104 |
| tabular-MiniBooNE | 2 | 9523 | 0.2034 | 0.1149 (0.1149, 0.1149) | 0.00 | 0.766 | 0.0544 | 0.0605 |
| tabular-MiniBooNE | 3 | 11912 | 0.2544 | 0.1076 (0.1076, 0.1076) | 0.00 | 0.717 | 0.0700 | 0.0376 |
| tabular-MiniBooNE | 4 | 9180 | 0.1961 | 0.3554 (0.3554, 0.3554) | 1.00 | 2.370 | 0.2334 | 0.1220 |
| tabular-adult | 1 | 9713 | 0.5966 | 0.0670 (0.0670, 0.0670) | 0.00 | 0.335 | 0.0519 | 0.0151 |
| tabular-adult | 2 | 299 | 0.0184 | 0.0468 (0.0468, 0.0468) | 0.00 | 0.234 | 0.0435 | 0.0033 |
| tabular-adult | 3 | 6268 | 0.3850 | 0.3127 (0.3127, 0.3127) | 1.00 | 1.563 | 0.3092 | 0.0035 |
| tabular-spambase | 0 | 335 | 0.2023 | 0.0030 (0.0030, 0.0030) | 0.00 | 0.020 | 0.0060 | -0.0030 |
| tabular-spambase | 1 | 308 | 0.1860 | 0.0390 (0.0390, 0.0390) | 0.00 | 0.260 | 0.0227 | 0.0162 |
| tabular-spambase | 2 | 402 | 0.2428 | 0.0553 (0.0498, 0.0597) | 0.00 | 0.369 | 0.0448 | 0.0105 |
| tabular-spambase | 3 | 362 | 0.2186 | 0.2105 (0.1851, 0.2431) | 1.00 | 1.403 | 0.0856 | 0.1248 |
| tabular-spambase | 4 | 249 | 0.1504 | 0.3851 (0.3614, 0.4016) | 1.00 | 2.567 | 0.1727 | 0.2124 |

Full grid (all 35 cells x 3 lambda_refs x strata): `pool_stratum_eval.csv`; per-resplit values at lambda_ref 0.9: `pool_stratum_resplits.csv`.