# CAFA v2 -- FINAL CLAIM DECISION (Phase 5.3, Task 8)

_git 7bdb1bf27fc3; 2026-07-12T20:52:33.407981+00:00_

## Scientific outcome: **A**

> STRONG: a marginally certified AFA system can conceal a trajectory-defined stratum for which no stopping threshold in the precommitted family meets the target; CAFA audits this family-wide failure and uses a common-threshold certificate that refuses when evidence does not support simultaneous validity.

## Per-dataset claim ledger

| field | mnist | tabular-MiniBooNE | tabular-adult | tabular-spambase |
|---|---|---|---|---|
| committed alpha | 0.15 | 0.15 | 0.2 | 0.15 |
| primary stratum rule | deepest nonempty (label-free) | deepest nonempty (label-free) | deepest nonempty (label-free) | deepest nonempty (label-free) |
| deepest == argmax k* | True | True | True | True |
| endpoint verdict | failure | failure | failure | unresolved |
| threshold-family verdict | failure | failure | failure | unresolved |
| family p-value | 1.37e-79 | 3.18e-98 | 8.73e-93 | 1.79e-01 |
| min threshold risk (argmin lambda) | 0.2479 | 0.2334 | 0.3090 | 0.1727 |
| depth-family verdict | failure | failure | failure | unresolved |
| plugin pool exceed [CI] | 0.00 | 0.00 | 0.00 | 0.45 |
| plugin label | not shown unreliable at this resolution | not shown unreliable at this resolution | not shown unreliable at this resolution | clearly unreliable |
| selected-rule deepest pool risk (mean) | 0.3006 | 0.3554 | 0.3127 | 0.3851 |
| ratio to alpha | 2.004 | 2.370 | 1.563 | 2.567 |
| IUT cert rate @0.9 | 0.00 | 0.00 | 0.00 | 0.00 |
| IUT refusal class | A: refusal with certified family-wide failure | A: refusal with certified family-wide failure | A: refusal with certified family-wide failure | C: refusal, unresolved |

## Allowed / prohibited phrases per dataset

- **mnist** ALLOWED: On this stratum, no stopping threshold in the audited precommitted threshold family attains the target and no prefix depth along the frozen acquisition path attains it.
  PROHIBITED: 'no possible feature subset, policy, acquisition strategy, or budget can attain the target' (never licensed); 'no budget works' beyond the audited family
- **tabular-MiniBooNE** ALLOWED: On this stratum, no stopping threshold in the audited precommitted threshold family attains the target and no prefix depth along the frozen acquisition path attains it.
  PROHIBITED: 'no possible feature subset, policy, acquisition strategy, or budget can attain the target' (never licensed); 'no budget works' beyond the audited family
- **tabular-adult** ALLOWED: On this stratum, no stopping threshold in the audited precommitted threshold family attains the target and no prefix depth along the frozen acquisition path attains it.
  PROHIBITED: 'no possible feature subset, policy, acquisition strategy, or budget can attain the target' (never licensed); 'no budget works' beyond the audited family
- **tabular-spambase** ALLOWED: The audit is unresolved at the available sample size.
  PROHIBITED: 'no possible feature subset, policy, acquisition strategy, or budget can attain the target' (never licensed); 'family-wide failure' (only endpoint/unresolved is certified here)

## Prohibited-phrase scan (11 markdown hits to fix or mark superseded)

- analysis_v2/PHASE3_REPORT.md:50
- analysis_v2/RESULTS.md:2522
- analysis_v2/RESULTS.md:2523
- analysis_v2/RESULTS.md:2560
- project_update.md:86
- project_update.md:652
- project_update.md:763
- results_committed/PHASE3_REPORT.md:50
- results_committed/RESULTS.md:2522
- results_committed/RESULTS.md:2523
- results_committed/RESULTS.md:2560