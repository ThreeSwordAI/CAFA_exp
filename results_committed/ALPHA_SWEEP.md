# CAFA v2 -- ALPHA SWEEP (post-hoc on cached rollouts)

_Grid anchored to the committed probe floor. The committed fixed-rule alpha is ceil_0.05(floor + 0.05) and generally sits above the +0.05 grid point; it is stated per dataset below and marked on F5. Same frozen trajectories, same pre-committed strata edges; delta = 0.1; n_resplits = 100._

## mnist (ts0, greedy_entropy, uniform; floor = 0.0779, committed alpha = 0.15)

| alpha | alpha-floor | plugin viol [95% CI] | marginal viol [95% CI] | marg abstain | marg cost/full | oracle cost | IUT abstain | IUT premium | infeasible strata @0.9 |
|---|---|---|---|---|---|---|---|---|---|
| 0.098 | +0.020 | 0.46 [0.37, 0.56] | 0.03 [0.01, 0.08] | 0.00 | 0.773 | 35.47 | 1.00 | 1.29 | 1 |
| 0.128 | +0.050 | 0.17 [0.11, 0.26] | 0.05 [0.02, 0.11] | 0.00 | 0.587 | 27.76 | 1.00 | 1.70 | 1 |
| 0.158 | +0.080 | 0.15 [0.09, 0.23] | 0.04 [0.02, 0.10] | 0.00 | 0.485 | 22.87 | 1.00 | 2.06 | 1 |
| 0.188 | +0.110 | 0.40 [0.31, 0.50] | 0.00 [0.00, 0.04] | 0.00 | 0.407 | 19.26 | 1.00 | 2.46 | 1 |
| 0.228 | +0.150 | 0.17 [0.11, 0.26] | 0.03 [0.01, 0.08] | 0.00 | 0.333 | 15.68 | 1.00 | 3.00 | 1 |
| 0.278 | +0.200 | 0.15 [0.09, 0.23] | 0.07 [0.03, 0.14] | 0.00 | 0.256 | 12.06 | 0.00 | 2.27 | 0 |

- Plugin transition: plugin remains UNSAFE across the whole swept range on mnist; the committed alpha 0.15 sits in the unsafe regime -- the certificate is doing real work at the committed target.

## tabular-adult (ts0, greedy_entropy, inverse_info; floor = 0.1465, committed alpha = 0.2)

| alpha | alpha-floor | plugin viol [95% CI] | marginal viol [95% CI] | marg abstain | marg cost/full | oracle cost | IUT abstain | IUT premium | infeasible strata @0.9 |
|---|---|---|---|---|---|---|---|---|---|
| 0.167 | +0.020 | 0.04 [0.02, 0.10] | 0.04 [0.02, 0.10] | 0.00 | 0.469 | 34.44 | 1.00 | 2.13 | 1 |
| 0.197 | +0.050 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.361 | 34.36 | 1.00 | 2.77 | 1 |
| 0.227 | +0.080 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.361 | 34.36 | 1.00 | 2.77 | 1 |
| 0.257 | +0.110 | 0.01 [0.00, 0.05] | 0.01 [0.00, 0.05] | 0.00 | 0.187 | 0.35 | 1.00 | 5.35 | 1 |
| 0.296 | +0.150 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.000 | 0.00 | 1.00 | n/a | 1 |
| 0.346 | +0.200 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.000 | 0.00 | 0.00 | n/a | 0 |

- Plugin transition on tabular-adult: plugin flips safe at alpha ~ 0.167 (floor + 0.020); the committed alpha 0.2 lands 0.034 above the transition (committed target is in the SAFE regime). The transition point is a property of the risk-curve geometry near alpha -- unknowable a priori, which is the argument for a certificate over a tuned threshold.

## tabular-MiniBooNE (ts0, greedy_entropy, inverse_info; floor = 0.0844, committed alpha = 0.15)

| alpha | alpha-floor | plugin viol [95% CI] | marginal viol [95% CI] | marg abstain | marg cost/full | oracle cost | IUT abstain | IUT premium | infeasible strata @0.9 |
|---|---|---|---|---|---|---|---|---|---|
| 0.104 | +0.020 | 0.28 [0.20, 0.37] | 0.07 [0.03, 0.14] | 0.00 | 0.167 | 48.42 | 1.00 | 5.98 | 1 |
| 0.134 | +0.050 | 0.16 [0.10, 0.24] | 0.13 [0.08, 0.21] | 0.00 | 0.055 | 17.26 | 1.00 | 18.16 | 1 |
| 0.164 | +0.080 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.050 | 17.01 | 1.00 | 20.05 | 1 |
| 0.194 | +0.110 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.050 | 17.01 | 1.00 | 20.05 | 1 |
| 0.234 | +0.150 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.050 | 17.01 | 1.00 | 20.05 | 0 |
| 0.284 | +0.200 | 0.05 [0.02, 0.11] | 0.05 [0.02, 0.11] | 0.00 | 0.038 | 0.85 | 0.00 | 4.26 | 0 |

- Plugin transition on tabular-MiniBooNE: plugin flips safe at alpha ~ 0.164 (floor + 0.080); the committed alpha 0.15 lands 0.014 below the transition (committed target is in the UNSAFE regime). The transition point is a property of the risk-curve geometry near alpha -- unknowable a priori, which is the argument for a certificate over a tuned threshold.

## tabular-spambase (ts0, greedy_entropy, inverse_info; floor = 0.0543, committed alpha = 0.15)

| alpha | alpha-floor | plugin viol [95% CI] | marginal viol [95% CI] | marg abstain | marg cost/full | oracle cost | IUT abstain | IUT premium | infeasible strata @0.9 |
|---|---|---|---|---|---|---|---|---|---|
| 0.074 | +0.020 | 0.53 [0.43, 0.62] | 0.07 [0.03, 0.14] | 0.69 | 0.810 | 104.49 | 1.00 | 1.24 | 1 |
| 0.104 | +0.050 | 0.45 [0.36, 0.55] | 0.06 [0.03, 0.12] | 0.00 | 0.203 | 60.52 | 1.00 | 4.93 | 1 |
| 0.134 | +0.080 | 0.44 [0.35, 0.54] | 0.07 [0.03, 0.14] | 0.00 | 0.128 | 30.39 | 1.00 | 7.79 | 1 |
| 0.164 | +0.110 | 0.21 [0.14, 0.30] | 0.04 [0.02, 0.10] | 0.00 | 0.068 | 19.28 | 1.00 | 14.66 | 0 |
| 0.204 | +0.150 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.045 | 18.76 | 0.97 | 21.54 | 0 |
| 0.254 | +0.200 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 | 0.045 | 18.76 | 0.40 | 12.21 | 0 |

- Plugin transition on tabular-spambase: plugin flips safe at alpha ~ 0.204 (floor + 0.150); the committed alpha 0.15 lands 0.054 below the transition (committed target is in the UNSAFE regime). The transition point is a property of the risk-curve geometry near alpha -- unknowable a priori, which is the argument for a certificate over a tuned threshold.
