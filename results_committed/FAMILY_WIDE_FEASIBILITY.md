# CAFA v2 -- FAMILY-WIDE FEASIBILITY AUDIT (Phase 5.3, Task 1)

_Confirmatory stratum = deepest precommitted nonempty bucket (label-free). Intersection-union test over the full committed family; exact one-sided binomial upper-tail p-values; audit level gamma = 0.05. Per-dataset p-values reported separately -- no cross-dataset FWER claim is made._

## Primary cells (ts0, greedy, softmax, lambda_ref = 0.9)

| dataset | stratum (n_k) | alpha | min THRESHOLD risk (argmin lambda) | full risk | p_family | THRESHOLD verdict | min DEPTH risk (argmin t) | p_depth | DEPTH verdict |
|---|---|---|---|---|---|---|---|---|---|
| mnist | 4 (5479) | 0.15 | 0.2479 (0.909) | 0.2479 | 1.37e-79 | **family-wide failure certified** | 0.2479 (49) | 1.37e-79 | **family-wide failure certified** |
| tabular-MiniBooNE | 4 (9180) | 0.15 | 0.2334 (0.939) | 0.2334 | 3.18e-98 | **family-wide failure certified** | 0.2334 (50) | 3.18e-98 | **family-wide failure certified** |
| tabular-adult | 3 (6268) | 0.2 | 0.3090 (0.869) | 0.3092 | 8.73e-93 | **family-wide failure certified** | 0.3092 (14) | 4.87e-93 | **family-wide failure certified** |
| tabular-spambase | 4 (249) | 0.15 | 0.1727 (0.899) | 0.1727 | 1.79e-01 | **unresolved** | 0.1727 (56) | 1.79e-01 | **unresolved** |

Wording licensed by each verdict: threshold-family failure -> 'no stopping threshold in the audited precommitted threshold family attains the target'; depth-family failure -> 'no prefix depth along the frozen acquisition path attains the target'. NEITHER licenses 'no possible feature subset, policy, acquisition strategy, or budget'.

## Sensitivity grid (105 configurations; all cells x lambda_refs)

Full grid in `family_wide_summary.csv`; verdict counts:
- threshold-family verdicts: {'feasible': 60, 'family-wide failure certified': 40, 'unresolved': 5}
- depth-family verdicts: {'feasible': 60, 'family-wide failure certified': 39, 'unresolved': 6}
- threshold curves monotone nonincreasing: 0.40 of configs; local-minima counts in the CSV.