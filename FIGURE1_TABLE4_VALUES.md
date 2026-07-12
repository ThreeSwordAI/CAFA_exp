# Figure 1 + Table 4 -- canonical values (forensic extraction, read-only)

Cell: dataset = mnist, policy = greedy_entropy, train_seed = 0,
lambda_ref = 0.9, cost scheme = uniform (mnist primary), readiness score =
max-softmax (file carries `"score": "softmax"`; NOT the [margin] variant).
All values from CANONICAL cluster artifacts at tag `canonical-v2.2`
(git HEAD db224a2); no local/laptop number used; nothing recomputed from
rollouts -- every number exists in a committed artifact.

## STEP 0 -- freeze check

`src/cafa/risk_control.py` and `tests/test_risk_control.py` MATCH
`repro/MANIFEST.sha256` after CRLF->LF normalization (the verify_bugs.py
convention; Windows checkout carries CRLF, manifest hashes LF content):
`c37ab67bbb02...` and `3ec1258ad95d...`. **PASS.**

## STEP 1 -- computation path (the anchor)

CANONICAL_RESULTS.md line 116 (`| mnist | 0 | 4 | 0.2479 [0.2383] |
infeasible | 0.3005 |`) is produced by `scripts/make_canonical_results.py`
(H3 section) from `results_committed/metrics/mnist_ts0_greedy_entropy.json`:

- per-stratum marginal risk = **mean over the 100 resplits of the realized
  TEST-split risk at the resplit's certified lambda-hat, within the stratum**
  (`lambda_refs["0.9"].resplits[*].marginal_per_stratum_risk[k]`, produced by
  `scripts/run_eval_sweep.py` via `per_bucket_risk`); strata are the
  probe-committed quantile-5 buckets at lambda_ref = 0.9;
- R_full(k*) and its LCB = population block
  (`lambda_refs["0.9"].population.per_stratum_full`), exact full-acquisition
  risk on the whole eval pool with one-sided 95% Clopper-Pearson bounds.

`results_committed/audit_table.csv` rows 42-46 carry the identical
per-stratum means (same generator family, `scripts/analyze_results.py`);
values verified byte-equal to the JSON-derived means. All six Figure-1 bars
below use this single estimand (mean realized test risk over 100 resplits,
scheme uniform, lambda_ref-0.9 block).

## STEP 2 + 3 -- values (full precision)

| quantity | value | source (file + row) | estimand |
|---|---|---|---|
| s0 (stratum 0 marginal risk) | 0.0919444000 | metrics/mnist_ts0_greedy_entropy.json `lambda_refs.0.9.resplits[*].marginal_per_stratum_risk["0"]` (mean of 100); = audit_table.csv row 42 | mean realized test risk over resplits |
| s1 | 0.1128668000 | same, key "1"; = audit_table.csv row 43 | same |
| s2 | 0.0951693700 | same, key "2"; = audit_table.csv row 44 | same |
| s3 | 0.0871343100 | same, key "3"; = audit_table.csv row 45 | same |
| s4 (= k*) | 0.3005391600 | same, key "4"; = audit_table.csv row 46; anchor: CANONICAL_RESULTS.md line 116 (0.3005) | same |
| aggregate cafa_marginal risk | 0.1414269600 | h2_table.csv row 24 (mean_risk); recomputable from `resplits[*].schemes.uniform.cafa_marginal.realized_risk` | **mean realized TEST risk at lambda-hat over the 100 resplits** (the estimand consistent with the five stratum bars); 0 abstentions |
| (alt estimand, NOT for Fig. 1) | 0.1414515873 | validity_diagnostic.csv row 4, `mean_R_pool_at_lambda` | mean R_pool(lambda-hat) -- pool estimand; listed to disambiguate, do not mix with test-split bars |
| R_full(k*=4) | 0.2478550000 (stored 0.247855, 6 dp) | metrics JSON `population.per_stratum_full["4"].risk` | exact full-acquisition risk on eval pool, stratum 4 |
| R_full(k*) 95% CP LCB | 0.2382700000 (stored 0.238270) | same, `.cp_lcb95` | one-sided Clopper-Pearson lower bound |
| n_0, q_0 | 4906, 0.1946825397 | metrics JSON `population.bucket_sizes` / eval_n | eval-pool stratum size / mass |
| n_1, q_1 | 5152, 0.2044444444 | same | same |
| n_2, q_2 | 5490, 0.2178571429 | same | same |
| n_3, q_3 | 4173, 0.1655952381 | same | same |
| n_4, q_4 | 5479, 0.2174206349 | same | same |
| mnist eval-pool size | 25200 | metrics JSON `meta.n_eval` (= population.eval_n) | heldout eval rows (28000 heldout x 0.9) |

Consistency: sum(n_k) = 25200 = eval_n; mass-weighted stratum means
sum(q_k * s_k) = 0.1414847 ~ aggregate 0.1414270 (small gap: per-resplit
test-half stratum sizes fluctuate around the pool masses).

## STEP 4 -- sanity gates

| gate | result |
|---|---|
| s4 == 0.3005 (tol 0.00005): 0.30053916, diff 0.0000392 | **PASS** |
| R_full(k*) == 0.2479 and LCB == 0.2383 (stored 0.247855 / 0.238270; equal at reported 4-dp precision) | **PASS** |
| aggregate 0.14142696 <= 0.15 | **PASS** |
| s0..s3 in [0.087, 0.113]: 0.091944 / 0.112867 / 0.095169 / 0.087134 | **PASS** (s1 and s3 close to the edges but inside) |
| sum q_k = 1.0000000000; sum n_k = 25200 = eval-pool size | **PASS** |
| Table-4 inequalities (below) | **ALL HOLD** |

## Paste-ready lines for make_figure1.py

```python
RISK_AGG = 0.14142696
RISK_S0_S3 = [0.09194440, 0.11286680, 0.09516937, 0.08713431]
# RISK_S4 = 0.30053916   (k* bar; R_full fallback tick 0.247855, LCB 0.238270)
```

## Table 4 -- k* stratum sizes and eval pools (ts0, greedy_entropy, lambda_ref = 0.9)

Source: `results_committed/metrics/{ds}_ts0_greedy_entropy.json`,
`lambda_refs.0.9.population` (k* = argmax R_full over populated strata).

| dataset | k* | n_k* | q_k* | eval pool | required | holds? |
|---|---|---|---|---|---|---|
| mnist | 4 | 5479 | 0.2174206349 | 25200 | n_k* >= 551 | YES |
| tabular-MiniBooNE | 4 | 9180 | 0.1960574931 | 46823 | n_k* >= 760 | YES |
| tabular-adult | 3 | 6268 | 0.3850122850 | 16280 | n_k* >= 443 | YES |
| tabular-spambase | 4 | 249 | 0.1503623188 | 1656 | eval pool < 10250 | YES |

(spambase k* verdict is `undetermined` on the canonical pool -- consistent
with the frozen H3 table; its row is included for Table 4 sizes only.)

---
Provenance: extracted read-only on 2026-07-12 from git db224a2 (tag
canonical-v2.2). Anchors verified: CANONICAL_RESULTS.md lines 41 (gate row),
81 (H2 row), 116 (H3 row).
