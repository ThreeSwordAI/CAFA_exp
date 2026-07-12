# CAFA v2 -- PHASE 5.3 PROVENANCE AUDIT

_git 7bdb1bf27fc3; host tinyx; 2026-07-12T20:49:45.998644+00:00_

## The required provenance decision

- **k\*** as frozen (argmax observed stratum risk) USES evaluation labels -> treated as EXPLORATORY after selection.
- **Confirmatory stratum** = deepest precommitted nonempty bucket (trajectory-defined, label-free). Coincidence with argmax-k\* per primary cell (lambda_ref = 0.9):

| dataset | deepest nonempty | argmax-risk k* | coincide | n(deepest) |
|---|---|---|---|---|
| mnist | 4 | 4 | YES | 5479 |
| tabular-adult | 3 | 3 | YES | 6268 |
| tabular-MiniBooNE | 4 | 4 | YES | 9180 |
| tabular-spambase | 4 | 4 | YES | 249 |

- **lambda_ref = 0.9**: the sweep {0.5, 0.7, 0.9} and the analyzer's 'primary = largest configured' rule live in the tooling commits (git evidence in phase5_provenance.json, q3_q4). Phase 5.3 reports it as the fine-resolution analysis and always publishes all three lambda_refs.

## lambda = 1 interpretation (measured)

| dataset | frac rows stopping at T under lambda=1 | risk at lambda=1 | full-feature risk | identical |
|---|---|---|---|---|
| mnist | 1.0000 | 0.085437 | 0.085437 | yes |
| tabular-adult | 0.9956 | 0.150799 | 0.150799 | yes |
| tabular-MiniBooNE | 0.9962 | 0.083399 | 0.083399 | yes |
| tabular-spambase | 0.8822 | 0.060990 | 0.060990 | yes |

## The remaining answers (q5-q10)

- **q5_grid**: np.linspace(0.0, 1.0, 100) -- 100 thresholds, committed in configs/experiment.yaml (method.grid).
- **q7_threshold_to_predictions**: stop-index matrix: s(i, j) = first t with scores[i, t] >= grid[j] (else T); loss = 1 - correct[i, s]; identical code in run_eval_sweep/metrics.stops_from_grid_np.
- **q8_pool_risk**: mean of the loss column over ALL eval rows (exact on the fixed evaluation pool); per-stratum = same restricted to a probe-committed bucket.
- **q9_refusals**: lambda_idx = None => 'abstained'/refusal recorded explicitly; deployment falls back to FULL ACQUISITION and the system still predicts (certification refusal with full-acquisition fallback, NOT prediction abstention); fallback realized risk/cost recorded; never counted as a violation and never dropped.
- **q10_resplits**: 100 unique resplits: independent seeded permutations (default_rng(1_000_000 + seed)) of the eval indices, split 50/50 -- random split assignments, not folds; marginal CAFA is lambda_ref-independent so the 100 outcomes are counted ONCE (never n = 300).

Full machine-readable record: `phase5_provenance.json` (includes the git-history evidence for the lambda_ref primary designation).