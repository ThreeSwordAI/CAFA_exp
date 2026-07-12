# CAFA v2 -- CONTROLLED SYNTHETIC POWER VALIDATION (Phase 5.3, Task 6)

_Bernoulli simulation; alpha = 0.15, one-sided audit gamma = 0.05, B = 5000 repetitions per grid point, seed 20260712. Detection = one-sided exact CP lower bound > alpha. The theorem threshold n*q >= log(1/gamma)/(2 Delta^2) is SUFFICIENT (conservative), never a minimum requirement._

**False-positive control: max empirical FPR over all null points (Delta in {0, -0.02}, every (n, q)) = 0.0500 <= gamma = 0.05: PASS.**

Selected operating points (full grid in synthetic_power.csv):

| n | q | Delta | power [MC 95%] | unresolved | mean n_k | n*q | sufficient n*q | above? |
|---|---|---|---|---|---|---|---|---|
| 1000 | 0.05 | 0.02 | 0.081 [0.074, 0.089] | 0.000 | 50 | 50 | 3745 | no |
| 1000 | 0.05 | 0.05 | 0.207 [0.196, 0.218] | 0.000 | 50 | 50 | 599 | no |
| 1000 | 0.05 | 0.1 | 0.516 [0.502, 0.529] | 0.000 | 50 | 50 | 150 | no |
| 1000 | 0.2 | 0.02 | 0.177 [0.167, 0.188] | 0.000 | 200 | 200 | 3745 | no |
| 1000 | 0.2 | 0.05 | 0.557 [0.543, 0.571] | 0.000 | 200 | 200 | 599 | no |
| 1000 | 0.2 | 0.1 | 0.969 [0.964, 0.974] | 0.000 | 200 | 200 | 150 | yes |
| 10000 | 0.05 | 0.02 | 0.332 [0.319, 0.345] | 0.000 | 500 | 500 | 3745 | no |
| 10000 | 0.05 | 0.05 | 0.895 [0.886, 0.903] | 0.000 | 500 | 500 | 599 | no |
| 10000 | 0.05 | 0.1 | 1.000 [0.999, 1.000] | 0.000 | 500 | 500 | 150 | yes |
| 10000 | 0.2 | 0.02 | 0.780 [0.769, 0.791] | 0.000 | 2000 | 2000 | 3745 | no |
| 10000 | 0.2 | 0.05 | 1.000 [0.999, 1.000] | 0.000 | 2000 | 2000 | 599 | yes |
| 10000 | 0.2 | 0.1 | 1.000 [0.999, 1.000] | 0.000 | 2000 | 2000 | 150 | yes |
| 50000 | 0.05 | 0.02 | 0.852 [0.841, 0.861] | 0.000 | 2500 | 2500 | 3745 | no |
| 50000 | 0.05 | 0.05 | 1.000 [0.999, 1.000] | 0.000 | 2500 | 2500 | 599 | yes |
| 50000 | 0.05 | 0.1 | 1.000 [0.999, 1.000] | 0.000 | 2500 | 2500 | 150 | yes |
| 50000 | 0.2 | 0.02 | 1.000 [0.999, 1.000] | 0.000 | 10002 | 10000 | 3745 | yes |
| 50000 | 0.2 | 0.05 | 1.000 [0.999, 1.000] | 0.000 | 9998 | 10000 | 599 | yes |
| 50000 | 0.2 | 0.1 | 1.000 [0.999, 1.000] | 0.000 | 10001 | 10000 | 150 | yes |

## Family-size calibration (IUT max-p; n_k = 2000; a calibration study, not a proof)

| M | scenario | family reject rate [95%] |
|---|---|---|
| 10 | all_infeasible | 1.000 [0.998, 1.000] |
| 10 | one_feasible | 0.000 [0.000, 0.002] |
| 50 | all_infeasible | 1.000 [0.997, 1.000] |
| 50 | one_feasible | 0.000 [0.000, 0.002] |
| 100 | all_infeasible | 0.999 [0.996, 1.000] |
| 100 | one_feasible | 0.000 [0.000, 0.002] |

Allowed interpretation: detection increases with stratum mass, risk margin, and sample size, and the controlled simulation shows the sufficient bound is conservative but directionally predictive. NOT allowed: 'the theorem gives the minimum required sample size'; 'spambase proves no method could detect the failure' (the spambase comparison remains a retrospective design diagnostic).