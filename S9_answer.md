# S9_answer.md -- Verified source material for S9 (Corrected Plug-In and Finite-Pool Evaluation)

Prepared from canonical frozen artifacts only. Every number was re-extracted
this pass from the row-level artifacts in Section 1. Where a quantity is not
stored and was reconstructed through the exact finite-pool identity, this is
stated at the point of use and flagged again in Section 17 -- nothing is
silently derived.

---

## 1. Canonical sources and freeze metadata

1. **Artifacts.**
   - Per-resplit CAFA selections, exact full-pool risks and pool costs (all
     35 cells, lambda_ref 0.9 block): `results_committed/pool_stratum_resplits.csv`.
   - Per-resplit plug-in selections, full-pool risks/costs, exceed and
     fallback flags (all 35 cells): `results_committed/pool_plugin_resplits.csv`
     (3,500 rows).
   - Complementary test-half risks per resplit (6-dp): the `cafa_marginal`
     and `plugin` blocks of `results_committed/metrics/*.json`.
   - Calibration-half risks per resplit: **not stored** -- reconstructable
     exactly via the identity (Section 2.2); independently recomputed inside
     the gate script but not persisted.
   - Pool-risk gate + anti-correlation diagnostics:
     `results_committed/pool_risk_gate.csv` / `POOL_RISK_GATE.md`
     (columns `corr_Rcal_Rtest_fixed_lambda`, `corr_Rcal_at_hat_vs_test_excess`).
   - Plug-in cell-level pool evaluation: `results_committed/pool_plugin_eval.csv`
     / `POOL_PLUGIN_EVAL.md`.
   - Plug-in alpha sweep on the POOL estimand:
     `results_committed/pool_plugin_alpha_sweep.csv` / `POOL_PLUGIN_ALPHA_SWEEP.md`.
   - Superseded test-half alpha sweep (Phase 5): `results_committed/alpha_sweep.csv`,
     `alpha_sweep_transitions.csv`, `ALPHA_SWEEP.md` -- diagnostics only.
   - Fixed-sequence p-values: computed inside the frozen selector (not
     persisted per resplit; the gate re-runs the selector and asserts the
     selection, which pins them implicitly).
2. **Code.** Complementary resplits: `src/cafa/splits.py::resplit_cal_test`.
   Marginal CAFA selection: frozen `src/cafa/risk_control.py::ltt_select`
   (SHA-256 c37ab67bbb02..., byte-frozen). Plug-in:
   `src/cafa/baselines.py::plugin_threshold_select`. Full-pool evaluation +
   gate + Wilson + anti-correlation: `scripts/pool_risk_gate.py` (functions
   `wilson`, `gate_cell`; z = 1.96 hand-coded Wilson). Plug-in pool
   evaluation and sweep: Phase-5.3 scripts `pool_plugin_eval.py` (with
   selection reproduction asserts) using `scripts/phase53_lib.py`.
3. **Freeze.** Tag `canonical-v2.2` (compute closed); Phase-5.3 artifacts
   stamped commit `7bdb1bf27fc3`; compendium v2.3.
4. **Must not cite** (superseded estimand or environment): test-half
   violation columns anywhere (h2_table `violation_frac`, metrics
   `realized_risk`-based gates, `alpha_sweep.csv` `marg_viol`/`plugin_viol`,
   `alpha_sweep_transitions.csv` verdicts -- the mnist "UNSAFE at committed"
   there is the OLD estimand, corrected below); the v2.1/v2.2 "gate FAIL"
   headlines; all local-replication artifacts.

---

## 2. Exact finite-pool setup

### 2.1 Evaluation-pool sizes (verified from meta.n_eval + the split rule)

| Dataset | n_eval | n_cal | n_test | equal halves |
|---|---:|---:|---:|---|
| MNIST | 25,200 | 12,600 | 12,600 | yes |
| Adult | 16,280 | 8,140 | 8,140 | yes |
| MiniBooNE | 46,823 | 23,412 | 23,411 | no (odd pool) |
| Spambase | 1,656 | 828 | 828 | yes |

All four expected rows CONFIRMED. Rule (`resplit_cal_test`): permute the
pool with `np.random.default_rng(1_000_000 + resplit_seed)`, take the first
`n_cal = int(round(0.5 * n_eval))` as the calibration half, rest as test.
For MiniBooNE, `round(23411.5)` under Python banker's rounding
(round-half-to-even) gives **23,412 calibration / 23,411 test**. Resplit
seeds: 0..99 (offset 1,000,000 keeps the streams disjoint from train/probe);
**100 resplits per cell**, every cell.

### 2.2 Exact empirical-risk identity

For every fixed indexed rule a and resplit b, the halves partition the pool,
so at the integer error-count level e_cal(a) + e_test(a) = e_pool(a),
equivalently

    n_cal * R_cal^(b)(a) + n_test * R_test^(b)(a) = n_eval * R_pool(a).

- Equal halves: R_test^(b)(a) = 2 * R_pool(a) - R_cal^(b)(a). CONFIRMED as
  an algebraic identity of the partition (and it is the mechanism the gate
  script states and measures).
- MiniBooNE rearrangement: R_test^(b)(a) = (46823 * R_pool(a) - 23412 *
  R_cal^(b)(a)) / 23411.
- R_pool(a) is **independent of the resplit index b** for fixed a (it is a
  deterministic function of the frozen pool and the rule).
- The identity is **exact at integer error-count level** (no rounding
  involved; float means of 0/1 losses are exact rationals).
- Substituting the data-dependent selected rule a_hat_b: the identity
  **still holds pointwise for every b** (within resplit b, a_hat_b is one
  fixed rule; the partition argument does not care how a was chosen). What
  varies with b: a_hat_b itself, R_cal^(b)(a_hat_b), R_test^(b)(a_hat_b),
  and R_pool(a_hat_b) -- the last varies ONLY through a_hat_b (piecewise
  constant over the 1-11 distinct selections per cell).

---

## 3. Anti-correlation: exact scope

### 3.1 Fixed-rule correlation

Canonical measurement (`pool_risk_gate.csv`): for each of the 35 cells, the
gate computes R_cal^(b)(a) and R_test^(b)(a) **independently from the raw
loss matrices** at one fixed rule a = the modal selected threshold of that
cell, over the 100 resplits, and reports their Pearson correlation.

- Result: **-1.0000 in all 35 cells**; numerical range over cells
  [-1.0, -0.9999999999999993] (float rounding only); no NaN entries.
- Zero-variance handling: the code emits NaN when either half's risk is
  constant across resplits; this occurred in **0 of 35 cells** at the modal
  threshold, so no correlation was claimed for a constant-risk rule.
- Algebraic status: for ANY fixed rule and any half sizes, R_test is an
  affine strictly-decreasing function of R_cal (slope -n_cal/n_test), so the
  correlation is **exactly -1 whenever the variance is nonzero** -- the
  expected statement is CONFIRMED, with the variance qualifier.

### 3.2 Selected-rule correlation (mandatory distinction)

The canonical artifact does NOT store corr(R_cal(a_hat_b), R_test(a_hat_b)).
The gate's stored selected-rule diagnostic is a different quantity:
corr(R_cal at a_hat_b, test EXCESS R_test(a_hat_b) - R_pool(a_hat_b)),
range across the 35 cells **[-1.000, +0.471]**. The correlations below were
computed in this pass from stored per-resplit quantities (R_pool exact from
pool_stratum_resplits, R_test 6-dp from metrics) with R_cal reconstructed
through the exact identity:

| quantity (100 resplits) | MNIST | Adult | MiniBooNE | Spambase |
|---|---:|---:|---:|---:|
| corr(R_cal(a_hat), R_test(a_hat)) | **+0.2023** | -1.0000 | -1.0000 | **-0.0753** |
| corr(lambda_hat idx, R_cal) | -0.5186 | undefined | undefined | +0.0838 |
| corr(lambda_hat idx, R_test) | -0.9418 | undefined | undefined | -0.9622 |
| corr(pool margin, test-violation) | -0.4264 | undefined | undefined | -0.2556 |
| unique selected thresholds | 3 | 1 | 1 | 11 |

("undefined" = zero variance: Adult and MiniBooNE select the same threshold
in all 100 resplits and have no test violations, so lambda_hat and the
violation indicator are constants.)

Across all 35 cells: corr(R_cal(a_hat), R_test(a_hat)) ranges **-1.000 to
+0.778** (mean -0.13; defined in all 35). It equals exactly -1 precisely in
the **10 cells where the selection is constant** (the selected rule then IS
a fixed rule); wherever the selection varies, the correlation is NOT -1 and
can even be positive (MNIST +0.20). **S9 must therefore scope "correlation
= -1" to fixed rules; the actual selector does NOT inherit it.** What the
selector does inherit is the pointwise identity (Section 2.2) and the
mechanism visible in corr(lambda_hat, R_test) ~ -0.94/-0.96: easier
calibration halves push the selection to more aggressive thresholds whose
complementary halves are deterministically harder.

---

## 4. Exact marginal-CAFA selection coupling

Definition (frozen `ltt_select`, procedure fixed_sequence): ascending
100-point grid; the fixed-sequence walk starts at the TOP (most
conservative, index 99) and steps down, certifying every threshold whose
Hoeffding-Bentkus p-value <= delta = 0.1 until the first failure; the
certified set is that contiguous top block. The selected threshold is the
argmin of expected calibration cost over the certified set; expected cost is
monotone increasing in the grid index, so this is **always the smallest
certified index -- the bottom of the block, i.e. the least-conservative
certified threshold** (its p-value is the closest to the delta boundary; one
grid step lower already failed). Cost enters selection only formally
(monotonicity makes it cost-blind, stated in the code). Fallback: full
acquisition when nothing certifies -- **never triggered (3,500/3,500
certified)**.

Per primary cell over 100 resplits (selection frequencies exact; pool risk
per selected threshold is exact and resplit-independent; cal risks
identity-reconstructed; test risks stored 6-dp):

- **MNIST** (alpha 0.15): lambda_hat idx {84: 2, 85: 81, 86: 17} -> values
  0.8485 (min) / 0.8586 (median) / 0.8687 (max); mean 0.860101. Pool risk by
  selection: 0.14920635 (idx 84), 0.14238095 (85), 0.13611111 (86). Mean cal
  risk 0.141476; mean test risk 0.141427; mean pool margin +0.008548; test
  violations 2; pool violations 0; fallbacks 0.
- **Adult** (alpha 0.20): idx 77 in all 100 resplits (0.777778). Pool risk
  0.16124079. Mean cal 0.161052; mean test 0.161430; margin +0.038759;
  test violations 0; pool violations 0; fallbacks 0.
- **MiniBooNE** (alpha 0.15): idx 71 in all 100 (0.717172). Pool risk
  0.13256306. Mean cal 0.132406; mean test 0.132720; margin +0.017437;
  test violations 0; pool violations 0; fallbacks 0.
- **Spambase** (alpha 0.15): 11 distinct selections, idx {64: 14, 66: 9,
  68: 7, 69: 4, 70: 5, 71: 9, 72: 20, 73: 13, 74: 17, 76: 1, 77: 1} ->
  0.6465 (min) / 0.7273 (median) / 0.7778 (max); mean 0.710202. Pool risk by
  selection from 0.13526570 (idx 64) down to 0.10990338 (idx 77). Mean cal
  0.124903; mean test 0.125483; margin +0.024807; test violations 3; pool
  violations 0; fallbacks 0.

All-35-cell aggregates: 3,500/3,500 certified, 0 fallbacks, **96 test-half
violations** (superseded diagnostic count), **1 full-pool violation**
(mnist/greedy/ts1 resplit 67), mean pool margins per cell from +0.0068 to
+0.0856 (S6 CSV, `mean_margin` column); per-cell selection-frequency and
threshold-summary columns for all 35 cells are in the S6 dossier table.

---

## 5. Correct full-pool gate

1. **Unit of analysis: both.** Resplit-level violation events, aggregated to
   a cell-level pass/fail.
2. Resplit event: exactly `R_pool(a_hat_b) > alpha` (strict `>`, float64, no
   tolerance) -- `pool_risk_gate.py` line `if rp > alpha: pool_viol += 1`.
3. Cell criterion: **Wilson upper bound <= delta**, not the raw rate
   (`"PASS" if phi <= delta else "FAIL"`); comparison value delta = 0.1.
4. Wilson: two-sided 95% (z = 1.96), hand-coded; the gate uses the upper
   endpoint.
5. Equality: R_pool = alpha is **not** a violation (strict >); UB = delta
   **passes** (<=).
6. Fallback/abstention: counted in a separate `abstentions` counter; the
   fallback rule is evaluated at full acquisition and would count as a
   violation only if the full-acquisition pool risk exceeded alpha. Moot:
   0 abstentions in all 3,500 runs.
7. Denominator: always the full 100 resplits (fallbacks would stay in the
   denominator).
8. **Precommitted: yes** -- the criterion is written in the Phase-5.2 script
   header and is the identical criterion the Phase-1 analyzer applied to the
   (superseded) test-half gate from the first canonical run; the Phase-5.2
   estimand change did not touch the criterion.
9. Artifacts proving it: `scripts/pool_risk_gate.py` docstring + gate line;
   `POOL_RISK_GATE.md` header ("GATE criterion: Wilson 95% UB <= delta, the
   same criterion as the main gate table"); the Phase-1 analyzer's gate
   (same formula) predating the pool results.
10. Passing cells: **35 of 35**.

Expected summary RESOLVED as stated: 34/35 cells at 0/100; mnist/greedy_
entropy/ts1 at 1/100 (resplit 67, pool risk 0.20007937 = 5,042/25,200,
excess 2 pool examples); Wilson UB for that cell **0.054488** (0.0545 at
4 dp); all 35 PASS. No correction needed.

---

## 6. Plug-in selector

Definition (`plugin_threshold_select`): calibration statistic = per-threshold
empirical calibration risk (column mean of the same frozen 0/1 loss matrix
CAFA uses); same ascending 100-point grid, same frozen trajectories, same
cost matrices as CAFA. Selection: keep every threshold whose empirical
calibration risk <= alpha -- **no finite-sample correction of any kind** --
and among those return the one with the smallest expected calibration cost
(ties -> lowest index). Costs affect selection exactly as in CAFA (and are
equally cost-blind wherever risk is monotone). Fallback: None -> full
acquisition if no threshold's empirical risk <= alpha; **0 fallbacks in all
3,500 plug-in runs**.

Per-resplit values for every cell (not just the primaries) are frozen in
`pool_plugin_resplits.csv`: selected lambda_idx, exact full-pool risk, pool
cost, exceed flag, fallback flag; the complementary-test risk per resplit is
in the metrics `plugin` blocks (6-dp); the calibration risk is
reconstructable via the identity. **The corrected plug-in comparison is
available for all 35 cells** (selection asserted equal to the recorded
threshold on every resplit; POOL_PLUGIN_EVAL.md header).

---

## 7. Primary four-dataset comparison table

**Risk definition verified:** the stored per-cell quantity is exactly the
preferred (1/100) * sum_b R_pool(a_hat_b) -- the mean over the 100 selected
rules of the exact full-pool risk (cross-checked against
validity_diagnostic.csv by the gate's 1e-9 assert; pool_plugin_eval's
`mean_pool_risk` is the same construction for the plug-in). Not a
median-threshold risk, not a pooled error count.

| Dataset | alpha | CAFA pool risk | CAFA viol./100 [Wilson UB] | Plug-in pool risk | Plug-in viol./100 [Wilson UB] | CAFA cost/full | Plug-in cost/full |
|---|---:|---:|---:|---:|---:|---:|---:|
| MNIST | 0.15 | 0.141452 | 0 [0.037] | 0.146681 | 0 [0.037] | 0.5072 | 0.4916 |
| Adult | 0.20 | 0.161241 | 0 [0.037] | 0.161241 | 0 [0.037] | 0.3612 | 0.3612 |
| MiniBooNE | 0.15 | 0.132563 | 0 [0.037] | 0.132563 | 0 [0.037] | 0.0499 | 0.0499 |
| Spambase | 0.15 | 0.125193 | 0 [0.037] | 0.143756 | **45 [0.548]** | 0.0917 | 0.0573 |

Spread across resplits (sd / min / max of pool risk; sd of cost/full):

- MNIST: CAFA 0.00261 / 0.13611 / 0.14921, cost sd 0.00847 (range
  0.4843-0.5248); plug-in sd 0.00330 (p5 0.14238, p95 0.14921).
- Adult: CAFA 0 / 0.16124 / 0.16124 (constant selection), cost sd 0;
  plug-in sd 0 (identical selection).
- MiniBooNE: CAFA 0 / 0.13256 / 0.13256, cost sd 0; plug-in identical.
- Spambase: CAFA 0.00697 / 0.10990 / 0.13527, cost sd 0.02130 (range
  0.0647-0.1331); plug-in sd 0.00994 (p5 0.13511, p95 0.15821), selected
  lambda 0.6162/0.6465/0.6869 (min/med/max).

Fallbacks: 0 for both methods on all four cells. On Adult and MiniBooNE the
two selectors chose the SAME threshold in every resplit (identical rows);
on MNIST they agreed in 22/100 resplits (CAFA higher by +0.78 grid steps on
average); on Spambase they never agreed (CAFA higher by +7.14 steps on
average) -- the HB margin buys the 45-violation gap. No test-half rates
appear in this table.

---

## 8. Complete 35-cell corrected comparison

One row per marginal cell; CAFA fields from pool_stratum_resplits /
pool_risk_gate, plug-in fields from pool_plugin_eval / pool_plugin_resplits;
`same_lambda_count` = resplits (of 100) where both selected the identical
threshold; `mean_idx_diff` = mean(CAFA idx - plugin idx) (CAFA is never
below the plug-in). Plug-in full-pool values exist for ALL 35 cells (no
NOT FOUND rows).

```csv
cell,dataset,policy,eps,seed,score,scheme,alpha,cafa_certified,cafa_fallbacks,cafa_mean_pool_risk,cafa_pool_viol,cafa_wilson_hi,cafa_mean_cost_over_full,plugin_mean_pool_risk,plugin_pool_viol,plugin_wilson_hi,plugin_mean_cost_over_full,plugin_fallbacks,risk_diff_cafa_minus_plugin,cost_diff_cafa_minus_plugin,same_lambda_count,mean_idx_diff_cafa_minus_plugin
mnist/eps_greedy_eps0.25/ts0,mnist,eps_greedy_eps0.25,0.25,0,softmax,uniform,0.15,100,0,0.141974206,0,0.036995,0.454986,0.147100397,8,0.149983,0.440855,0,-0.00512619,0.014131,6,0.94
mnist/eps_greedy_eps0.5/ts0,mnist,eps_greedy_eps0.5,0.5,0,softmax,uniform,0.15,100,0,0.141606349,0,0.036995,0.441352,0.147604365,21,0.299801,0.428517,0,-0.005998016,0.012835,3,1.03
mnist/greedy_entropy/ts0,mnist,greedy_entropy,,0,softmax,uniform,0.15,100,0,0.141451587,0,0.036995,0.507247,0.146680952,0,0.036995,0.491648,0,-0.005229365,0.0156,22,0.78
mnist/greedy_entropy/ts0[margin],mnist,greedy_entropy,,0,margin,uniform,0.15,100,0,0.142227381,0,0.036995,0.508877,0.147950794,49,0.586522,0.489607,0,-0.005723413,0.019269,0,1.48
mnist/greedy_entropy/ts1,mnist,greedy_entropy,,1,softmax,uniform,0.2,100,0,0.190576587,1,0.054488,0.528657,0.196939286,59,0.681328,0.511211,0,-0.006362698,0.017446,20,0.8
mnist/greedy_entropy/ts2,mnist,greedy_entropy,,2,softmax,uniform,0.15,100,0,0.138230952,0,0.036995,0.73863,0.14608373,0,0.036995,0.709819,0,-0.007852778,0.028811,23,0.77
mnist/random/ts0,mnist,random,,0,softmax,uniform,0.15,100,0,0.141660317,0,0.036995,0.528678,0.147282143,0,0.036995,0.518317,0,-0.005621825,0.010361,0,1.09
mnist/random/ts1,mnist,random,,1,softmax,uniform,0.2,100,0,0.19097619,0,0.036995,0.557078,0.196788889,22,0.310705,0.547262,0,-0.005812698,0.009816,13,0.88
mnist/random/ts2,mnist,random,,2,softmax,uniform,0.15,100,0,0.141405159,0,0.036995,0.612355,0.147872619,7,0.137497,0.596608,0,-0.00646746,0.015747,1,1.28
tabular-MiniBooNE/eps_greedy_eps0.25/ts0,tabular-MiniBooNE,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.15,100,0,0.143022446,0,0.036995,0.061618,0.147327168,0,0.036995,0.057111,0,-0.004304722,0.004507,22,0.78
tabular-MiniBooNE/eps_greedy_eps0.5/ts0,tabular-MiniBooNE,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.15,100,0,0.141751276,0,0.036995,0.087754,0.14599748,49,0.586522,0.083459,0,-0.004246204,0.004295,49,0.51
tabular-MiniBooNE/greedy_entropy/ts0,tabular-MiniBooNE,greedy_entropy,,0,softmax,inverse_info,0.15,100,0,0.132563057,0,0.036995,0.04995,0.132563057,0,0.036995,0.04995,0,0.0,0.0,100,0.0
tabular-MiniBooNE/greedy_entropy/ts0[margin],tabular-MiniBooNE,greedy_entropy,,0,margin,inverse_info,0.15,100,0,0.132563057,0,0.036995,0.04995,0.132563057,0,0.036995,0.04995,0,0.0,0.0,100,0.0
tabular-MiniBooNE/greedy_entropy/ts1,tabular-MiniBooNE,greedy_entropy,,1,softmax,inverse_info,0.15,100,0,0.142660658,0,0.036995,0.034095,0.147258399,13,0.209805,0.030164,0,-0.00459774,0.003931,22,0.78
tabular-MiniBooNE/greedy_entropy/ts2,tabular-MiniBooNE,greedy_entropy,,2,softmax,inverse_info,0.15,100,0,0.139546804,0,0.036995,0.054852,0.139546804,0,0.036995,0.054852,0,0.0,0.0,100,0.0
tabular-MiniBooNE/random/ts0,tabular-MiniBooNE,random,,0,softmax,inverse_info,0.15,100,0,0.143243278,0,0.036995,0.165736,0.146671508,30,0.39585,0.15875,0,-0.00342823,0.006987,47,0.53
tabular-MiniBooNE/random/ts1,tabular-MiniBooNE,random,,1,softmax,inverse_info,0.15,100,0,0.142899857,0,0.036995,0.162507,0.145820644,8,0.149983,0.156439,0,-0.002920787,0.006068,55,0.45
tabular-MiniBooNE/random/ts2,tabular-MiniBooNE,random,,2,softmax,inverse_info,0.15,100,0,0.142912671,0,0.036995,0.176598,0.146729812,9,0.162264,0.167207,0,-0.003817141,0.009391,32,0.68
tabular-adult/eps_greedy_eps0.25/ts0,tabular-adult,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.2,100,0,0.16529484,0,0.036995,0.340295,0.16529484,0,0.036995,0.340295,0,0.0,0.0,100,0.0
tabular-adult/eps_greedy_eps0.5/ts0,tabular-adult,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.2,100,0,0.171683047,0,0.036995,0.321424,0.171683047,0,0.036995,0.321424,0,0.0,-0.0,100,0.0
tabular-adult/greedy_entropy/ts0,tabular-adult,greedy_entropy,,0,softmax,inverse_info,0.2,100,0,0.161240786,0,0.036995,0.361215,0.161240786,0,0.036995,0.361215,0,0.0,-0.0,100,0.0
tabular-adult/greedy_entropy/ts0[margin],tabular-adult,greedy_entropy,,0,margin,inverse_info,0.2,100,0,0.161179361,0,0.036995,0.355121,0.161179361,0,0.036995,0.355121,0,0.0,0.0,100,0.0
tabular-adult/greedy_entropy/ts1,tabular-adult,greedy_entropy,,1,softmax,inverse_info,0.25,100,0,0.164434889,0,0.036995,0.309764,0.178724816,16,0.244204,0.260202,0,-0.014289926,0.049562,84,12.0
tabular-adult/greedy_entropy/ts2,tabular-adult,greedy_entropy,,2,softmax,inverse_info,0.2,100,0,0.186547912,0,0.036995,0.209375,0.192260442,0,0.036995,0.192531,0,-0.005712531,0.016844,50,0.5
tabular-adult/random/ts0,tabular-adult,random,,0,softmax,inverse_info,0.2,100,0,0.182985258,0,0.036995,0.277283,0.182985258,0,0.036995,0.277283,0,0.0,-0.0,100,0.0
tabular-adult/random/ts1,tabular-adult,random,,1,softmax,inverse_info,0.25,100,0,0.202149877,0,0.036995,0.200542,0.210405405,16,0.244204,0.168456,0,-0.008255528,0.032087,84,12.0
tabular-adult/random/ts2,tabular-adult,random,,2,softmax,inverse_info,0.2,100,0,0.187472973,0,0.036995,0.230907,0.187714988,0,0.036995,0.229292,0,-0.000242015,0.001614,92,0.1
tabular-spambase/eps_greedy_eps0.25/ts0,tabular-spambase,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.15,100,0,0.125791063,0,0.036995,0.109542,0.146890097,26,0.353712,0.078614,0,-0.021099034,0.030928,0,4.31
tabular-spambase/eps_greedy_eps0.5/ts0,tabular-spambase,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.15,100,0,0.124577295,0,0.036995,0.119417,0.146032609,21,0.299801,0.091721,0,-0.021455314,0.027696,0,3.73
tabular-spambase/greedy_entropy/ts0,tabular-spambase,greedy_entropy,,0,softmax,inverse_info,0.15,100,0,0.125193237,0,0.036995,0.091674,0.143756039,45,0.547556,0.057252,0,-0.018562802,0.034422,0,7.14
tabular-spambase/greedy_entropy/ts1,tabular-spambase,greedy_entropy,,1,softmax,inverse_info,0.15,100,0,0.123242754,0,0.036995,0.173674,0.147439614,25,0.343046,0.147879,0,-0.02419686,0.025795,0,6.81
tabular-spambase/greedy_entropy/ts2,tabular-spambase,greedy_entropy,,2,softmax,inverse_info,0.15,100,0,0.12330314,0,0.036995,0.170693,0.145259662,47,0.567113,0.094304,0,-0.021956522,0.076389,0,14.23
tabular-spambase/random/ts0,tabular-spambase,random,,0,softmax,inverse_info,0.15,100,0,0.124752415,0,0.036995,0.208102,0.146413043,18,0.266675,0.166661,0,-0.021660628,0.041442,0,2.94
tabular-spambase/random/ts1,tabular-spambase,random,,1,softmax,inverse_info,0.15,100,0,0.124631643,0,0.036995,0.202913,0.146509662,37,0.467797,0.15928,0,-0.021878019,0.043634,0,3.62
tabular-spambase/random/ts2,tabular-spambase,random,,2,softmax,inverse_info,0.15,100,0,0.122240338,0,0.036995,0.21011,0.144758454,16,0.244204,0.170186,0,-0.022518116,0.039924,0,3.0
```

Aggregates: plug-in total pool violations **542/3,500** across **21 nonzero
cells** (vs CAFA 1/3,500 in 1 cell); plug-in fallbacks 0; CAFA mean
cost/full >= plug-in mean cost/full in **35/35 cells**; the selectors agree
on all 100 resplits in 8 cells (where the empirical boundary is far from
alpha and both sit at the same cost minimum).

---

## 9. Data required for Figure S9.1

### Panel A: complementary-split coupling for the actual selector

One row per resplit for the four primary cells (400 rows). Provenance:
`lambda_idx/lambda/pool_risk/cost` exact from pool_stratum_resplits;
`test_risk` stored 6-dp from metrics; **`cal_risk_derived` is reconstructed
through the exact identity** (n_eval*R_pool - n_test*R_test)/n_cal -- per-
resplit calibration risks are not independently persisted anywhere (the
gate recomputed them internally from raw arrays but wrote only correlation
summaries). Any plot that shows cal risk from frozen artifacts is therefore
a visualization of the identity, not an independent measurement -- flagged
as author decision 17.2.

```csv
dataset,resplit,lambda_idx,lambda,cal_risk_derived,test_risk,pool_risk,alpha,pool_viol,test_viol,cost_over_full,fallback
mnist,0,86,0.8686868686868687,0.140635222,0.131587,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,1,85,0.8585858585858587,0.143650905,0.141111,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,2,85,0.8585858585858587,0.143412905,0.141349,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,3,85,0.8585858585858587,0.143729905,0.141032,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,4,85,0.8585858585858587,0.143491905,0.14127,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,5,85,0.8585858585858587,0.144126905,0.140635,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,6,85,0.8585858585858587,0.143650905,0.141111,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,7,85,0.8585858585858587,0.143015905,0.141746,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,8,86,0.8686868686868687,0.138809222,0.133413,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,9,85,0.8585858585858587,0.139761905,0.145,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,10,85,0.8585858585858587,0.139840905,0.144921,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,11,85,0.8585858585858587,0.142459905,0.142302,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,12,85,0.8585858585858587,0.141348905,0.143413,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,13,85,0.8585858585858587,0.142936905,0.141825,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,14,85,0.8585858585858587,0.142539905,0.142222,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,15,85,0.8585858585858587,0.140793905,0.143968,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,16,85,0.8585858585858587,0.141666905,0.143095,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,17,85,0.8585858585858587,0.141428905,0.143333,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,18,85,0.8585858585858587,0.142777905,0.141984,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,19,86,0.8686868686868687,0.138809222,0.133413,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,20,85,0.8585858585858587,0.143729905,0.141032,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,21,85,0.8585858585858587,0.143412905,0.141349,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,22,85,0.8585858585858587,0.141666905,0.143095,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,23,86,0.8686868686868687,0.140159222,0.132063,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,24,85,0.8585858585858587,0.139602905,0.145159,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,25,85,0.8585858585858587,0.140555905,0.144206,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,26,85,0.8585858585858587,0.142142905,0.142619,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,27,86,0.8686868686868687,0.138492222,0.13373,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,28,85,0.8585858585858587,0.140317905,0.144444,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,29,85,0.8585858585858587,0.143015905,0.141746,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,30,85,0.8585858585858587,0.139840905,0.144921,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,31,85,0.8585858585858587,0.141269905,0.143492,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,32,85,0.8585858585858587,0.141983905,0.142778,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,33,85,0.8585858585858587,0.142856905,0.141905,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,34,84,0.8484848484848485,0.144206698,0.154206,0.1492063492063492,0.15,0,1,0.484322157,0
mnist,35,85,0.8585858585858587,0.141586905,0.143175,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,36,85,0.8585858585858587,0.140078905,0.144683,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,37,85,0.8585858585858587,0.139840905,0.144921,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,38,85,0.8585858585858587,0.141348905,0.143413,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,39,85,0.8585858585858587,0.140872905,0.143889,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,40,86,0.8686868686868687,0.141508222,0.130714,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,41,86,0.8686868686868687,0.141508222,0.130714,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,42,85,0.8585858585858587,0.144126905,0.140635,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,43,85,0.8585858585858587,0.140317905,0.144444,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,44,85,0.8585858585858587,0.140158905,0.144603,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,45,85,0.8585858585858587,0.140237905,0.144524,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,46,85,0.8585858585858587,0.144047905,0.140714,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,47,85,0.8585858585858587,0.141428905,0.143333,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,48,85,0.8585858585858587,0.144126905,0.140635,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,49,86,0.8686868686868687,0.138571222,0.133651,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,50,85,0.8585858585858587,0.140078905,0.144683,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,51,85,0.8585858585858587,0.141190905,0.143571,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,52,85,0.8585858585858587,0.139920905,0.144841,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,53,85,0.8585858585858587,0.140475905,0.144286,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,54,86,0.8686868686868687,0.139603222,0.132619,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,55,85,0.8585858585858587,0.141269905,0.143492,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,56,85,0.8585858585858587,0.139999905,0.144762,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,57,85,0.8585858585858587,0.140555905,0.144206,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,58,86,0.8686868686868687,0.138254222,0.133968,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,59,85,0.8585858585858587,0.143094905,0.141667,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,60,85,0.8585858585858587,0.142777905,0.141984,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,61,85,0.8585858585858587,0.143094905,0.141667,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,62,85,0.8585858585858587,0.143253905,0.141508,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,63,85,0.8585858585858587,0.139126905,0.145635,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,64,85,0.8585858585858587,0.141824905,0.142937,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,65,85,0.8585858585858587,0.142618905,0.142143,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,66,85,0.8585858585858587,0.143174905,0.141587,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,67,85,0.8585858585858587,0.143650905,0.141111,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,68,86,0.8686868686868687,0.137857222,0.134365,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,69,85,0.8585858585858587,0.143332905,0.141429,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,70,85,0.8585858585858587,0.143094905,0.141667,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,71,85,0.8585858585858587,0.139205905,0.145556,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,72,85,0.8585858585858587,0.139444905,0.145317,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,73,85,0.8585858585858587,0.141190905,0.143571,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,74,86,0.8686868686868687,0.139127222,0.133095,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,75,85,0.8585858585858587,0.143253905,0.141508,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,76,85,0.8585858585858587,0.143650905,0.141111,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,77,85,0.8585858585858587,0.143412905,0.141349,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,78,86,0.8686868686868687,0.140397222,0.131825,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,79,85,0.8585858585858587,0.140237905,0.144524,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,80,85,0.8585858585858587,0.143412905,0.141349,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,81,85,0.8585858585858587,0.139364905,0.145397,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,82,84,0.8484848484848485,0.143968698,0.154444,0.1492063492063492,0.15,0,1,0.484322157,0
mnist,83,85,0.8585858585858587,0.141110905,0.143651,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,84,85,0.8585858585858587,0.140475905,0.144286,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,85,85,0.8585858585858587,0.142539905,0.142222,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,86,85,0.8585858585858587,0.138729905,0.146032,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,87,85,0.8585858585858587,0.143174905,0.141587,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,88,85,0.8585858585858587,0.143174905,0.141587,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,89,86,0.8686868686868687,0.140159222,0.132063,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,90,85,0.8585858585858587,0.143809905,0.140952,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,91,85,0.8585858585858587,0.144047905,0.140714,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,92,86,0.8686868686868687,0.138571222,0.133651,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,93,85,0.8585858585858587,0.140158905,0.144603,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,94,85,0.8585858585858587,0.139761905,0.145,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,95,85,0.8585858585858587,0.139444905,0.145317,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,96,85,0.8585858585858587,0.143729905,0.141032,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,97,86,0.8686868686868687,0.142539222,0.129683,0.1361111111111111,0.15,0,0,0.524843699,0
mnist,98,85,0.8585858585858587,0.141745905,0.143016,0.14238095238095239,0.15,0,0,0.504120505,0
mnist,99,86,0.8686868686868687,0.137619222,0.134603,0.1361111111111111,0.15,0,0,0.524843699,0
tabular-MiniBooNE,0,71,0.7171717171717172,0.130617196,0.134509,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,1,71,0.7171717171717172,0.134803018,0.130323,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,2,71,0.7171717171717172,0.132026136,0.1331,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,3,71,0.7171717171717172,0.131300167,0.133826,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,4,71,0.7171717171717172,0.130275211,0.134851,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,5,71,0.7171717171717172,0.131300167,0.133826,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,6,71,0.7171717171717172,0.132752105,0.132374,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,7,71,0.7171717171717172,0.132496116,0.13263,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,8,71,0.7171717171717172,0.132710107,0.132416,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,9,71,0.7171717171717172,0.132282125,0.132844,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,10,71,0.7171717171717172,0.131642153,0.133484,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,11,71,0.7171717171717172,0.13497401,0.130152,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,12,71,0.7171717171717172,0.135571985,0.129554,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,13,71,0.7171717171717172,0.130318209,0.134808,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,14,71,0.7171717171717172,0.132453118,0.132673,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,15,71,0.7171717171717172,0.132752105,0.132374,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,16,71,0.7171717171717172,0.132667109,0.132459,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,17,71,0.7171717171717172,0.131642153,0.133484,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,18,71,0.7171717171717172,0.1305312,0.134595,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,19,71,0.7171717171717172,0.130830187,0.134296,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,20,71,0.7171717171717172,0.132795103,0.132331,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,21,71,0.7171717171717172,0.131428162,0.133698,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,22,71,0.7171717171717172,0.134290039,0.130836,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,23,71,0.7171717171717172,0.133478074,0.131648,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,24,71,0.7171717171717172,0.132667109,0.132459,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,25,71,0.7171717171717172,0.131385164,0.133741,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,26,71,0.7171717171717172,0.132154131,0.132972,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,27,71,0.7171717171717172,0.132581112,0.132545,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,28,71,0.7171717171717172,0.135485988,0.12964,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,29,71,0.7171717171717172,0.130830187,0.134296,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,30,71,0.7171717171717172,0.134076049,0.13105,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,31,71,0.7171717171717172,0.134290039,0.130836,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,32,71,0.7171717171717172,0.134290039,0.130836,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,33,71,0.7171717171717172,0.133222085,0.131904,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,34,71,0.7171717171717172,0.131300167,0.133826,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,35,71,0.7171717171717172,0.135400992,0.129725,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,36,71,0.7171717171717172,0.131385164,0.133741,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,37,71,0.7171717171717172,0.129079262,0.136047,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,38,71,0.7171717171717172,0.132325123,0.132801,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,39,71,0.7171717171717172,0.13591297,0.129213,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,40,71,0.7171717171717172,0.128267297,0.136859,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,41,71,0.7171717171717172,0.131727149,0.133399,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,42,71,0.7171717171717172,0.134546029,0.13058,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,43,71,0.7171717171717172,0.129634238,0.135492,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,44,71,0.7171717171717172,0.134632025,0.130494,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,45,71,0.7171717171717172,0.130574198,0.134552,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,46,71,0.7171717171717172,0.131898142,0.133228,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,47,71,0.7171717171717172,0.134418034,0.130708,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,48,71,0.7171717171717172,0.132752105,0.132374,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,49,71,0.7171717171717172,0.133863058,0.131263,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,50,71,0.7171717171717172,0.132453118,0.132673,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,51,71,0.7171717171717172,0.129250255,0.135876,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,52,71,0.7171717171717172,0.133051092,0.132075,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,53,71,0.7171717171717172,0.132624111,0.132502,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,54,71,0.7171717171717172,0.128865271,0.136261,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,55,71,0.7171717171717172,0.132453118,0.132673,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,56,71,0.7171717171717172,0.131428162,0.133698,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,57,71,0.7171717171717172,0.129677237,0.135449,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,58,71,0.7171717171717172,0.131813145,0.133313,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,59,71,0.7171717171717172,0.133906056,0.13122,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,60,71,0.7171717171717172,0.128951268,0.136175,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,61,71,0.7171717171717172,0.132325123,0.132801,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,62,71,0.7171717171717172,0.13194114,0.133185,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,63,71,0.7171717171717172,0.133265083,0.131861,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,64,71,0.7171717171717172,0.134418034,0.130708,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,65,71,0.7171717171717172,0.134546029,0.13058,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,66,71,0.7171717171717172,0.131514158,0.133612,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,67,71,0.7171717171717172,0.132966096,0.13216,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,68,71,0.7171717171717172,0.132069134,0.133057,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,69,71,0.7171717171717172,0.13382006,0.131306,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,70,71,0.7171717171717172,0.133906056,0.13122,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,71,71,0.7171717171717172,0.132325123,0.132801,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,72,71,0.7171717171717172,0.134119047,0.131007,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,73,71,0.7171717171717172,0.133777061,0.131349,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,74,71,0.7171717171717172,0.129890227,0.135236,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,75,71,0.7171717171717172,0.133222085,0.131904,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,76,71,0.7171717171717172,0.133051092,0.132075,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,77,71,0.7171717171717172,0.133393078,0.131733,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,78,71,0.7171717171717172,0.135016008,0.13011,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,79,71,0.7171717171717172,0.13638295,0.128743,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,80,71,0.7171717171717172,0.131898142,0.133228,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,81,71,0.7171717171717172,0.130787189,0.134339,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,82,71,0.7171717171717172,0.132069134,0.133057,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,83,71,0.7171717171717172,0.132282125,0.132844,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,84,71,0.7171717171717172,0.1281823,0.136944,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,85,71,0.7171717171717172,0.130787189,0.134339,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,86,71,0.7171717171717172,0.131428162,0.133698,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,87,71,0.7171717171717172,0.132624111,0.132502,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,88,71,0.7171717171717172,0.1328801,0.132246,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,89,71,0.7171717171717172,0.129720235,0.135406,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,90,71,0.7171717171717172,0.134290039,0.130836,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,91,71,0.7171717171717172,0.133906056,0.13122,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,92,71,0.7171717171717172,0.129634238,0.135492,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,93,71,0.7171717171717172,0.1328801,0.132246,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,94,71,0.7171717171717172,0.1328801,0.132246,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,95,71,0.7171717171717172,0.131343165,0.133783,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,96,71,0.7171717171717172,0.132240127,0.132886,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,97,71,0.7171717171717172,0.131129174,0.133997,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,98,71,0.7171717171717172,0.135784976,0.129341,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-MiniBooNE,99,71,0.7171717171717172,0.132838101,0.132288,0.1325630566174743,0.15,0,0,0.049949727,0
tabular-adult,0,77,0.7777777777777778,0.163144572,0.159337,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,1,77,0.7777777777777778,0.163636572,0.158845,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,2,77,0.7777777777777778,0.160933572,0.161548,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,3,77,0.7777777777777778,0.161793572,0.160688,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,4,77,0.7777777777777778,0.160319572,0.162162,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,5,77,0.7777777777777778,0.157862572,0.164619,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,6,77,0.7777777777777778,0.162162572,0.160319,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,7,77,0.7777777777777778,0.168058572,0.154423,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,8,77,0.7777777777777778,0.163513572,0.158968,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,9,77,0.7777777777777778,0.166216572,0.156265,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,10,77,0.7777777777777778,0.161547572,0.160934,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,11,77,0.7777777777777778,0.158722572,0.163759,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,12,77,0.7777777777777778,0.161302572,0.161179,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,13,77,0.7777777777777778,0.160565572,0.161916,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,14,77,0.7777777777777778,0.161916572,0.160565,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,15,77,0.7777777777777778,0.158476572,0.164005,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,16,77,0.7777777777777778,0.163022572,0.159459,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,17,77,0.7777777777777778,0.154545572,0.167936,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,18,77,0.7777777777777778,0.158476572,0.164005,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,19,77,0.7777777777777778,0.159459572,0.163022,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,20,77,0.7777777777777778,0.163022572,0.159459,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,21,77,0.7777777777777778,0.157616572,0.164865,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,22,77,0.7777777777777778,0.159582572,0.162899,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,23,77,0.7777777777777778,0.157125572,0.165356,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,24,77,0.7777777777777778,0.156756572,0.165725,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,25,77,0.7777777777777778,0.157002572,0.165479,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,26,77,0.7777777777777778,0.164741572,0.15774,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,27,77,0.7777777777777778,0.162899572,0.159582,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,28,77,0.7777777777777778,0.167567572,0.154914,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,29,77,0.7777777777777778,0.168550572,0.153931,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,30,77,0.7777777777777778,0.155896572,0.166585,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,31,77,0.7777777777777778,0.156756572,0.165725,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,32,77,0.7777777777777778,0.163022572,0.159459,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,33,77,0.7777777777777778,0.161056572,0.161425,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,34,77,0.7777777777777778,0.160933572,0.161548,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,35,77,0.7777777777777778,0.159213572,0.163268,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,36,77,0.7777777777777778,0.159582572,0.162899,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,37,77,0.7777777777777778,0.160687572,0.161794,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,38,77,0.7777777777777778,0.160933572,0.161548,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,39,77,0.7777777777777778,0.163267572,0.159214,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,40,77,0.7777777777777778,0.159213572,0.163268,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,41,77,0.7777777777777778,0.164496572,0.157985,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,42,77,0.7777777777777778,0.166093572,0.156388,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,43,77,0.7777777777777778,0.163144572,0.159337,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,44,77,0.7777777777777778,0.159950572,0.162531,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,45,77,0.7777777777777778,0.163022572,0.159459,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,46,77,0.7777777777777778,0.159950572,0.162531,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,47,77,0.7777777777777778,0.158353572,0.164128,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,48,77,0.7777777777777778,0.167076572,0.155405,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,49,77,0.7777777777777778,0.158845572,0.163636,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,50,77,0.7777777777777778,0.161424572,0.161057,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,51,77,0.7777777777777778,0.158845572,0.163636,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,52,77,0.7777777777777778,0.159582572,0.162899,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,53,77,0.7777777777777778,0.159336572,0.163145,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,54,77,0.7777777777777778,0.159950572,0.162531,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,55,77,0.7777777777777778,0.157002572,0.165479,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,56,77,0.7777777777777778,0.158476572,0.164005,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,57,77,0.7777777777777778,0.163144572,0.159337,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,58,77,0.7777777777777778,0.162284572,0.160197,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,59,77,0.7777777777777778,0.163022572,0.159459,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,60,77,0.7777777777777778,0.155528572,0.166953,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,61,77,0.7777777777777778,0.164373572,0.158108,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,62,77,0.7777777777777778,0.161670572,0.160811,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,63,77,0.7777777777777778,0.155773572,0.166708,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,64,77,0.7777777777777778,0.163267572,0.159214,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,65,77,0.7777777777777778,0.160565572,0.161916,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,66,77,0.7777777777777778,0.160565572,0.161916,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,67,77,0.7777777777777778,0.157125572,0.165356,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,68,77,0.7777777777777778,0.164373572,0.158108,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,69,77,0.7777777777777778,0.161670572,0.160811,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,70,77,0.7777777777777778,0.164250572,0.158231,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,71,77,0.7777777777777778,0.156019572,0.166462,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,72,77,0.7777777777777778,0.162653572,0.159828,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,73,77,0.7777777777777778,0.159090572,0.163391,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,74,77,0.7777777777777778,0.163267572,0.159214,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,75,77,0.7777777777777778,0.158967572,0.163514,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,76,77,0.7777777777777778,0.157125572,0.165356,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,77,77,0.7777777777777778,0.160687572,0.161794,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,78,77,0.7777777777777778,0.162039572,0.160442,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,79,77,0.7777777777777778,0.160565572,0.161916,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,80,77,0.7777777777777778,0.161547572,0.160934,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,81,77,0.7777777777777778,0.161670572,0.160811,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,82,77,0.7777777777777778,0.160319572,0.162162,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,83,77,0.7777777777777778,0.157862572,0.164619,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,84,77,0.7777777777777778,0.161056572,0.161425,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,85,77,0.7777777777777778,0.158230572,0.164251,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,86,77,0.7777777777777778,0.161670572,0.160811,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,87,77,0.7777777777777778,0.163881572,0.1586,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,88,77,0.7777777777777778,0.161916572,0.160565,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,89,77,0.7777777777777778,0.157862572,0.164619,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,90,77,0.7777777777777778,0.158967572,0.163514,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,91,77,0.7777777777777778,0.167444572,0.155037,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,92,77,0.7777777777777778,0.160810572,0.161671,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,93,77,0.7777777777777778,0.161916572,0.160565,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,94,77,0.7777777777777778,0.159705572,0.162776,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,95,77,0.7777777777777778,0.161056572,0.161425,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,96,77,0.7777777777777778,0.162407572,0.160074,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,97,77,0.7777777777777778,0.164004572,0.158477,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,98,77,0.7777777777777778,0.160933572,0.161548,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-adult,99,77,0.7777777777777778,0.167198572,0.155283,0.16124078624078625,0.2,0,0,0.361215418,0
tabular-spambase,0,73,0.7373737373737375,0.126811623,0.115942,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,1,64,0.6464646464646465,0.123188401,0.147343,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,2,74,0.7474747474747475,0.119565599,0.109903,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,3,66,0.6666666666666667,0.126811754,0.137681,0.1322463768115942,0.15,0,0,0.070143299,0
tabular-spambase,4,66,0.6666666666666667,0.125603754,0.138889,0.1322463768115942,0.15,0,0,0.070143299,0
tabular-spambase,5,72,0.7272727272727273,0.126811812,0.119565,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,6,64,0.6464646464646465,0.124396401,0.146135,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,7,77,0.7777777777777778,0.126811763,0.092995,0.10990338164251208,0.15,0,0,0.133123398,0
tabular-spambase,8,64,0.6464646464646465,0.126811401,0.14372,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,9,71,0.7171717171717172,0.125604188,0.128019,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,10,72,0.7272727272727273,0.124395812,0.121981,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,11,72,0.7272727272727273,0.126811812,0.119565,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,12,72,0.7272727272727273,0.123188812,0.123188,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,13,72,0.7272727272727273,0.125603812,0.120773,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,14,68,0.686868686868687,0.126811295,0.135266,0.13103864734299517,0.15,0,0,0.073929979,0
tabular-spambase,15,73,0.7373737373737375,0.126811623,0.115942,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,16,70,0.7070707070707072,0.126811377,0.130435,0.1286231884057971,0.15,0,0,0.082544441,0
tabular-spambase,17,74,0.7474747474747475,0.118357599,0.111111,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,18,71,0.7171717171717172,0.126811188,0.126812,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,19,69,0.696969696969697,0.126811836,0.13285,0.12983091787439613,0.15,0,0,0.080036863,0
tabular-spambase,20,73,0.7373737373737375,0.125603623,0.11715,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,21,70,0.7070707070707072,0.126811377,0.130435,0.1286231884057971,0.15,0,0,0.082544441,0
tabular-spambase,22,74,0.7474747474747475,0.126811599,0.102657,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,23,70,0.7070707070707072,0.126811377,0.130435,0.1286231884057971,0.15,0,0,0.082544441,0
tabular-spambase,24,64,0.6464646464646465,0.124396401,0.146135,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,25,72,0.7272727272727273,0.124395812,0.121981,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,26,72,0.7272727272727273,0.126811812,0.119565,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,27,72,0.7272727272727273,0.124395812,0.121981,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,28,74,0.7474747474747475,0.123188599,0.10628,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,29,74,0.7474747474747475,0.119565599,0.109903,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,30,68,0.686868686868687,0.125604295,0.136473,0.13103864734299517,0.15,0,0,0.073929979,0
tabular-spambase,31,76,0.7676767676767677,0.125603681,0.099034,0.11231884057971014,0.15,0,0,0.129242869,0
tabular-spambase,32,71,0.7171717171717172,0.124396188,0.129227,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,33,72,0.7272727272727273,0.125603812,0.120773,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,34,72,0.7272727272727273,0.126811812,0.119565,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,35,73,0.7373737373737375,0.126811623,0.115942,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,36,68,0.686868686868687,0.124396295,0.137681,0.13103864734299517,0.15,0,0,0.073929979,0
tabular-spambase,37,64,0.6464646464646465,0.119565401,0.150966,0.13526570048309178,0.15,0,1,0.064706225,0
tabular-spambase,38,64,0.6464646464646465,0.124396401,0.146135,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,39,73,0.7373737373737375,0.125603623,0.11715,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,40,74,0.7474747474747475,0.121980599,0.107488,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,41,72,0.7272727272727273,0.123188812,0.123188,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,42,71,0.7171717171717172,0.125604188,0.128019,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,43,64,0.6464646464646465,0.126811401,0.14372,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,44,71,0.7171717171717172,0.125604188,0.128019,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,45,64,0.6464646464646465,0.117149401,0.153382,0.13526570048309178,0.15,0,1,0.064706225,0
tabular-spambase,46,66,0.6666666666666667,0.123188754,0.141304,0.1322463768115942,0.15,0,0,0.070143299,0
tabular-spambase,47,69,0.696969696969697,0.126811836,0.13285,0.12983091787439613,0.15,0,0,0.080036863,0
tabular-spambase,48,68,0.686868686868687,0.126811295,0.135266,0.13103864734299517,0.15,0,0,0.073929979,0
tabular-spambase,49,73,0.7373737373737375,0.125603623,0.11715,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,50,73,0.7373737373737375,0.125603623,0.11715,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,51,74,0.7474747474747475,0.121980599,0.107488,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,52,71,0.7171717171717172,0.126811188,0.126812,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,53,72,0.7272727272727273,0.125603812,0.120773,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,54,74,0.7474747474747475,0.121980599,0.107488,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,55,73,0.7373737373737375,0.124396623,0.118357,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,56,64,0.6464646464646465,0.117149401,0.153382,0.13526570048309178,0.15,0,1,0.064706225,0
tabular-spambase,57,72,0.7272727272727273,0.124395812,0.121981,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,58,72,0.7272727272727273,0.126811812,0.119565,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,59,74,0.7474747474747475,0.125603599,0.103865,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,60,72,0.7272727272727273,0.125603812,0.120773,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,61,73,0.7373737373737375,0.126811623,0.115942,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,62,69,0.696969696969697,0.126811836,0.13285,0.12983091787439613,0.15,0,0,0.080036863,0
tabular-spambase,63,64,0.6464646464646465,0.124396401,0.146135,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,64,74,0.7474747474747475,0.125603599,0.103865,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,65,66,0.6666666666666667,0.126811754,0.137681,0.1322463768115942,0.15,0,0,0.070143299,0
tabular-spambase,66,73,0.7373737373737375,0.123188623,0.119565,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,67,74,0.7474747474747475,0.124396599,0.105072,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,68,74,0.7474747474747475,0.125603599,0.103865,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,69,72,0.7272727272727273,0.123188812,0.123188,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,70,64,0.6464646464646465,0.125603401,0.144928,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,71,73,0.7373737373737375,0.126811623,0.115942,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,72,69,0.696969696969697,0.126811836,0.13285,0.12983091787439613,0.15,0,0,0.080036863,0
tabular-spambase,73,74,0.7474747474747475,0.125603599,0.103865,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,74,73,0.7373737373737375,0.124396623,0.118357,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,75,71,0.7171717171717172,0.125604188,0.128019,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,76,68,0.686868686868687,0.125604295,0.136473,0.13103864734299517,0.15,0,0,0.073929979,0
tabular-spambase,77,74,0.7474747474747475,0.123188599,0.10628,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,78,71,0.7171717171717172,0.126811188,0.126812,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,79,70,0.7070707070707072,0.125603377,0.131643,0.1286231884057971,0.15,0,0,0.082544441,0
tabular-spambase,80,72,0.7272727272727273,0.125603812,0.120773,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,81,64,0.6464646464646465,0.121980401,0.148551,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,82,68,0.686868686868687,0.126811295,0.135266,0.13103864734299517,0.15,0,0,0.073929979,0
tabular-spambase,83,72,0.7272727272727273,0.125603812,0.120773,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,84,66,0.6666666666666667,0.123188754,0.141304,0.1322463768115942,0.15,0,0,0.070143299,0
tabular-spambase,85,74,0.7474747474747475,0.123188599,0.10628,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,86,73,0.7373737373737375,0.124396623,0.118357,0.1213768115942029,0.15,0,0,0.117673947,0
tabular-spambase,87,72,0.7272727272727273,0.124395812,0.121981,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,88,64,0.6464646464646465,0.125603401,0.144928,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,89,70,0.7070707070707072,0.125603377,0.131643,0.1286231884057971,0.15,0,0,0.082544441,0
tabular-spambase,90,66,0.6666666666666667,0.125603754,0.138889,0.1322463768115942,0.15,0,0,0.070143299,0
tabular-spambase,91,72,0.7272727272727273,0.125603812,0.120773,0.12318840579710146,0.15,0,0,0.087938026,0
tabular-spambase,92,71,0.7171717171717172,0.126811188,0.126812,0.12681159420289856,0.15,0,0,0.085365549,0
tabular-spambase,93,74,0.7474747474747475,0.121980599,0.107488,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,94,66,0.6666666666666667,0.123188754,0.141304,0.1322463768115942,0.15,0,0,0.070143299,0
tabular-spambase,95,64,0.6464646464646465,0.124396401,0.146135,0.13526570048309178,0.15,0,0,0.064706225,0
tabular-spambase,96,74,0.7474747474747475,0.125603599,0.103865,0.11473429951690821,0.15,0,0,0.121215275,0
tabular-spambase,97,68,0.686868686868687,0.126811295,0.135266,0.13103864734299517,0.15,0,0,0.073929979,0
tabular-spambase,98,66,0.6666666666666667,0.125603754,0.138889,0.1322463768115942,0.15,0,0,0.070143299,0
tabular-spambase,99,66,0.6666666666666667,0.124395754,0.140097,0.1322463768115942,0.15,0,0,0.070143299,0
```

Panel-A facts: exact selected-rule correlations per dataset are in Section
3.2 (+0.2023 / -1 / -1 / -0.0753); a least-squares line is NOT
scientifically meaningful for the selected-rule scatter (the points lie on
1-11 discrete fixed-rule lines, not one linear trend); the meaningful guides
are, per unique selected threshold, the exact fixed-rule line R_test =
(n_eval*R_pool(lambda) - n_cal*R_cal)/n_test (slope -1 for equal halves,
-23412/23411 for MiniBooNE), plus the alpha line. Coloring by selected
threshold is essential for MNIST (3 values) and Spambase (11); Adult and
MiniBooNE degenerate to a single line each (constant selection). Four small
multiples are clearer than one pooled panel (risk scales differ:
0.10-0.15 vs 0.13-0.21).

### Panel B: target-risk sweep comparing CAFA and plug-in

The canonical POOL-estimand sweep exists for the **plug-in only**:
`pool_plugin_alpha_sweep.csv` (28 rows = 4 datasets x 7 alphas), reproduced
verbatim (columns as stored; `is_committed` = 1 marks the committed alpha;
`pool_exceed` is the violation rate over 100 resplits; Wilson lo/hi stored;
fallbacks stored):

```csv
dataset,alpha,is_committed,floor,committed_alpha,pool_exceed,wilson_lo,wilson_hi,mean_pool_risk,mean_pool_cost,fallbacks
mnist,0.0979,0,0.077857,0.15,0.01,0.0017673865655472645,0.0544875247609346,0.09599801587301587,35.42083849206351,0
mnist,0.1279,0,0.077857,0.15,0.17,0.10893476059773155,0.25548181233642975,0.12500198412698413,27.7097234126984,0
mnist,0.15,1,0.077857,0.15,0.0,0.0,0.03699480747600191,0.14668095238095236,24.090729761904758,0
mnist,0.1579,0,0.077857,0.15,0.03,0.010254338223414816,0.08452078080402699,0.1547888888888889,22.90638333333334,0
mnist,0.1879,0,0.077857,0.15,0.4,0.3093997461136028,0.4979992153815976,0.18407857142857142,19.31700873015873,0
mnist,0.2279,0,0.077857,0.15,0.17,0.10893476059773155,0.25548181233642975,0.22441309523809527,15.730889285714285,0
mnist,0.2779,0,0.077857,0.15,0.15,0.09305903191162297,0.23283733332157835,0.27421269841269846,12.107984126984123,0
tabular-MiniBooNE,0.1044,0,0.084374,0.15,0.26,0.18404578126986462,0.35371172631861636,0.1034480917497811,48.4137882681383,0
tabular-MiniBooNE,0.1344,0,0.084374,0.15,0.0,0.0,0.03699480747600191,0.1320936291993251,17.254530320847824,0
tabular-MiniBooNE,0.15,1,0.084374,0.15,0.0,0.0,0.03699480747600191,0.13256305661747428,17.036014533399417,0
tabular-MiniBooNE,0.1644,0,0.084374,0.15,0.0,0.0,0.03699480747600191,0.13256305661747428,17.036014533399417,0
tabular-MiniBooNE,0.1944,0,0.084374,0.15,0.0,0.0,0.03699480747600191,0.13256305661747428,17.036014533399417,0
tabular-MiniBooNE,0.2344,0,0.084374,0.15,0.0,0.0,0.03699480747600191,0.13256305661747428,17.036014533399417,0
tabular-MiniBooNE,0.2844,0,0.084374,0.15,0.0,0.0,0.03699480747600191,0.27771180829933995,0.3407202906679883,0
tabular-adult,0.1665,0,0.14649,0.2,0.0,0.0,0.03699480747600191,0.16103869778869784,34.955096932897334,0
tabular-adult,0.1965,0,0.14649,0.2,0.0,0.0,0.03699480747600191,0.16124078624078628,34.41586915733372,0
tabular-adult,0.2,1,0.14649,0.2,0.0,0.0,0.03699480747600191,0.16124078624078628,34.41586915733372,0
tabular-adult,0.2265,0,0.14649,0.2,0.0,0.0,0.03699480747600191,0.16124078624078628,34.41586915733372,0
tabular-adult,0.2565,0,0.14649,0.2,0.0,0.0,0.03699480747600191,0.24821867321867327,0.0,0
tabular-adult,0.2965,0,0.14649,0.2,0.0,0.0,0.03699480747600191,0.24821867321867327,0.0,0
tabular-adult,0.3465,0,0.14649,0.2,0.0,0.0,0.03699480747600191,0.24821867321867327,0.0,0
tabular-spambase,0.0743,0,0.054348,0.15,0.22,0.15001174503655804,0.3107053471500031,0.0730132850241546,103.34553573868288,0
tabular-spambase,0.1043,0,0.054348,0.15,0.39,0.300167219319702,0.48797163832501844,0.10303140096618359,60.329023911034156,0
tabular-spambase,0.1343,0,0.054348,0.15,0.44,0.34671865400968327,0.537720722887437,0.1316485507246377,30.88739025688804,0
tabular-spambase,0.15,1,0.054348,0.15,0.45,0.3561437510640346,0.5475557296835656,0.143756038647343,23.68954271267643,0
tabular-spambase,0.1643,0,0.054348,0.15,0.0,0.0,0.03699480747600191,0.1556582125603865,19.520608279196395,0
tabular-spambase,0.2043,0,0.054348,0.15,0.0,0.0,0.03699480747600191,0.15821256038647347,18.763222744268994,0
tabular-spambase,0.2543,0,0.054348,0.15,0.0,0.0,0.03699480747600191,0.15821256038647347,18.763222744268994,0
```

- **Alpha grid:** per dataset, floor + offsets {0.02, 0.05, 0.08, 0.12,
  0.17} clipped/ordered plus the committed alpha itself -- as listed: MNIST
  {0.0979, 0.1279, 0.15, 0.1579, 0.1879, 0.2279, 0.2779}; MiniBooNE
  {0.1044, 0.1344, 0.15, 0.1644, 0.1944, 0.2344, 0.2844}; Adult {0.1665,
  0.1965, 0.20, 0.2265, 0.2565, 0.2965, 0.3465}; Spambase {0.0743, 0.1043,
  0.1343, 0.15, 0.1643, 0.2043, 0.2543}.
- **Every committed alpha is measured directly** (is_committed rows;
  "MEASURED at committed alpha" lines in the MD).
- **Plug-in pool safety transitions:** MiniBooNE single crossing in
  (0.1044, 0.1344]; Spambase single crossing in (0.1500, 0.1643] (unsafe AT
  the committed target); Adult no crossing in range (exceed <= 0.10
  everywhere swept); **MNIST NONMONOTONE -- no single transition exists**
  (crossings in (0.0979, 0.1279], (0.1279, 0.1500], (0.1579, 0.1879];
  exceed sequence 0.01 -> 0.17 -> 0.00 -> 0.03 -> 0.40 -> 0.17 -> 0.15).
- **CAFA on the same alpha grid: NOT FOUND on the pool estimand.** The
  Phase-5 `alpha_sweep.csv` contains marginal-CAFA violation rates on the
  superseded test half only; the only pool-estimand CAFA points are at the
  committed alphas (the gate: 0/100, 0/100, 0/100, 0/100 on the primaries).
  Panel B must therefore show plug-in curves plus CAFA committed-alpha
  points, or the caption must state the CAFA curve is test-half.
- Fallbacks at every swept alpha point: 0 (column). The sweep uses the
  current full-pool estimand (select on calibration half, evaluate the
  selected threshold on the entire pool; committed floors shown).

---

## 10. Recommended Figure S9.1 design decision

**Recommendation: Option B for Panel A**, with one honesty caveat and one
stored-only alternative:

- Option A (cal vs test scatter) needs four small multiples (scales differ;
  Adult/MiniBooNE collapse to single fixed-rule lines) inside half a
  `figure*` -- readable but cramped, and its x-axis is identity-
  reconstructed (Section 9).
- **Option B (deviation form)** pools all four datasets into ONE panel: x =
  R_cal(a_hat_b) - R_pool(a_hat_b), y = R_test(a_hat_b) - R_pool(a_hat_b).
  Because the identity holds pointwise for the actual selector, every one of
  the 400 points lies EXACTLY on the line y = -(n_cal/n_test) x (slope -1;
  MiniBooNE -1.0000427) -- the cleanest possible demonstration that the
  coupling is mechanical for the deployed selector, with dataset markers and
  the 96-vs-1 violation asymmetry annotated. Same caveat: the x-coordinate
  is identity-derived, so the panel illustrates the algebra rather than an
  independent measurement (state in the caption, or recompute cal risks
  from the pool caches before figure freeze).
- Stored-only alternative (no reconstruction anywhere): plot R_test(a_hat_b)
  (stored) vs R_pool(a_hat_b) (stored) with the alpha lines -- the
  test-half false-alarm quadrant holds the 96 test-only violations vs the
  single true pool violation. If the authors want zero derived quantities in
  the figure, use this; it demonstrates over-reporting, though not the
  slope--1 mechanism.

Panel B: plug-in pool exceedance vs alpha (7 points per dataset, Wilson
bars), committed alpha marked per dataset, CAFA committed-alpha pool points
overlaid at 0/100; annotate MNIST's nonmonotone profile. Fits the page
budget as one two-panel `figure*`.

---

## 11. Fixed-pool estimand and population limitation (exact wording)

1. Estimand: "R_pool(a_hat_b), the exact risk of the selected rule on the
   fixed post-probe evaluation pool" -- a deterministic function of the pool
   and the selection; no estimation noise.
2. "Each calibration half is a without-replacement subsample (a uniformly
   random half) of the fixed pool" -- resplit_cal_test permutes the pool and
   takes the first half.
3. Conservativeness (if retained): "the empirical mean of a
   without-replacement sample is stochastically dominated by its
   with-replacement (binomial) counterpart (Hoeffding 1963, Sec. 6), so the
   Hoeffding-Bentkus p-values remain conservative for the pool-risk
   estimand and P(R_pool(a_hat) > alpha) <= delta holds as certified." This
   is the sentence already used in `pool_risk_gate.py`/`POOL_RISK_GATE.md`;
   the citation to use is exactly Hoeffding (1963), Section 6.
4. What the gate establishes: "the deployed rule met the committed target on
   the fixed evaluation pool in 3,499 of 3,500 calibration draws (34/35
   cells at 0/100; worst cell 1/100, Wilson UB 0.054), consistent with the
   delta = 0.1 certificate."
5. What it does NOT establish: it is not an estimate of
   Pr_{D_cal}{R(a_hat) > alpha} for independent draws from the underlying
   population -- the pool is one fixed sample, the 100 resplits are
   dependent halves of it, and the observed violation frequency is a
   finite-pool check of the certificate, not a population-level frequency.
6. The population-level claim rests on the LTT/HB theorem itself (frozen
   selector + its tests), extended to the pool estimand by the
   hypergeometric domination above; the controlled Bernoulli simulation
   (SYNTHETIC_POWER: B = 5,000 independent draws per grid point, max false-
   positive rate 0.0500 = gamma) validates the exact binomial machinery of
   the family audit under true independent sampling -- cite it for the
   audit, not as a marginal-certificate proof.
7. Hypergeometric domination: yes, S9 should keep one sentence (item 3);
   source: Hoeffding 1963, Sec. 6 (already cited in the manuscript and the
   gate header).

Avoid "the certificate is validated by the full pool"; use "the selected
rule meets the target on the fixed evaluation pool".

---

## 12. Nonmonotone risk profiles

Deepest-stratum curve evidence (primary cells, from the S8 row-level CSVs):

| dataset | thr-grid adjacent increases | largest thr increase | depth adjacent increases | largest depth increase |
|---|---:|---:|---:|---:|
| MNIST | 1 | 0.010038 | 1 | 0.000365 |
| Adult | 2 | 0.000160 | 1 | 0.093491 |
| MiniBooNE | 0 | 0 | 6 | 0.055120 |
| Spambase | 5 | 0.048193 | 17 | 0.265060 |

Plus the aggregate-level evidence specific to S9: the plug-in's pool
exceedance profile on MNIST is nonmonotone in alpha (0.17 at alpha 0.1279,
0.00 at the committed 0.15, 0.40 at 0.1879) -- no single safety transition
exists. Nonmonotonicity does NOT affect fixed-sequence validity (the walk
certifies a contiguous top block via p-values; no monotone-risk assumption
is used). It DOES matter for the plug-in: the cheapest empirically-valid
threshold can sit in a local dip of the calibration curve that does not
persist on the pool, which is exactly the MNIST profile above.
Recommendation: one sentence in S9 (the MNIST plug-in profile), pointing to
S8 for the stratum curves and S10 for the sensitivity grid.

---

## 13. Candidate claims

1. "Complementary calibration and test halves are exactly anti-correlated
   for every fixed rule." -- **SUPPORTED WITH SCOPE** (add "whenever the
   risks are non-constant across resplits"; algebraic identity + measured
   -1.0000 in 35/35 cells at the modal threshold).
2. "The actual data-dependent selector inherits exact correlation -1." --
   **UNSUPPORTED; DO NOT CLAIM.** Measured selected-rule correlations:
   MNIST +0.2023, Spambase -0.0753; range over 35 cells [-1, +0.778]; it is
   -1 only in the 10 constant-selection cells. What the selector inherits is
   the pointwise identity, not the correlation.
3. "A low calibration risk mechanically implies a high complementary-test
   risk for the same fixed rule." -- **SUPPORTED** (exact identity; for
   equal halves R_test = 2R_pool - R_cal).
4. "Selection toward the least-conservative certified threshold amplifies
   the apparent test-half violation rate." -- **SUPPORTED WITH SCOPE**
   (mechanism evidence: corr(lambda_hat, R_test) = -0.94/-0.96 on the
   varying primary cells; small mean pool margins 0.007-0.039; 96 test-half
   violations vs 1 pool violation across 3,500 selections; phrase as the
   documented mechanism, not a theorem).
5. "The complementary-test protocol over-reports violations relative to the
   fixed-pool estimand." -- **SUPPORTED** (96 vs 1 overall; 11 of 35 cells
   fail the old test-half gate, 0 fail the pool gate).
6. "Marginal CAFA has zero full-pool violations in all 35 cells." --
   **UNSUPPORTED as stated** (one violation exists); correct statement is
   claim 7 + the gate result.
7. "Marginal CAFA has one full-pool violation among 3,500 selections." --
   **SUPPORTED** (mnist/greedy/ts1, resplit 67, excess 2/25,200).
8. "All 35 marginal cells pass the precommitted pool-risk gate." --
   **SUPPORTED** (Wilson UB <= 0.1 everywhere; max UB 0.054488).
9. "The plug-in selector is unsafe on MNIST and Spambase at the committed
   target." -- **UNSUPPORTED on the corrected estimand; DO NOT CLAIM.**
   That is the superseded test-half verdict (0.35/0.45). Corrected
   full-pool at the committed alphas: MNIST 0/100, Adult 0/100, MiniBooNE
   0/100, **Spambase 45/100 [Wilson 0.356, 0.548]** -- unsafe on Spambase
   only, with MNIST's profile nonmonotone at nearby alphas (up to 0.40
   exceedance at alpha 0.1879) and 21/35 cells nonzero across the full
   grid (542/3,500 total).
10. "The plug-in selector is safe on Adult and MiniBooNE at the committed
    target." -- **SUPPORTED WITH SCOPE**: 0/100 exceedances (UB 0.037) on
    the fixed pool, and on these two cells it selected the identical
    threshold as CAFA in every resplit; say "no exceedances observed /
    not shown unreliable at this resolution" (the artifact's own label),
    never "safe" as a guarantee -- it remains uncertified.
11. "CAFA dominates plug-in in both risk and cost." -- **UNSUPPORTED; DO
    NOT CLAIM.** CAFA is never cheaper (cost >= plug-in in 35/35 cells;
    strictly more expensive wherever they differ) -- CAFA buys reliability
    (1 vs 542 violations), not cost. On Adult/MiniBooNE the two coincide
    exactly.
12. "The full-pool gate proves the population-level validity theorem." --
    **UNSUPPORTED; DO NOT CLAIM.** The gate is a finite-pool consistency
    check of the certified bound (Section 11); the theorem is proven, not
    validated by the pool.

---

## 14. Compact S9 table and text plan

Table S10 exactly as proposed (the Section-7 table: 8 columns, 4 rows) --
report BOTH mean pool risk and violations/100 (the risk column is what
shows plug-in sitting at the boundary, 0.1438 vs alpha 0.15 on Spambase,
while the violation column shows the consequence); add Wilson UBs in
brackets inside the violation cells rather than as separate columns. Text:
three paragraphs as planned (identity+coupling with the Section 3.2
distinction; corrected comparison; fixed-pool scope with the hypergeometric
sentence). Figure: one two-panel `figure*` per Section 10. This fits in
~1.75 pages; the full 35-cell comparison stays here as the Section-8 CSV
only if the supplement carries machine-readable appendices -- otherwise it
duplicates S6's table and should be referenced, keeping only the
542-vs-1 / 21-cell / 35-of-35-cost sentence in prose.

---

## 15. Rounding and terminology

Precision: risks 3-4 dp (4 where the alpha comparison is tight: 0.1438 vs
0.15); violation rates as exact "k/100"; Wilson bounds 3 dp; thresholds 3-4
dp (grid step 0.0101); correlations 2-3 dp (never report -1 unless it is
the algebraic case); normalized costs 3 dp; alpha-sweep transition brackets
4 dp as half-open intervals, e.g. "(0.1500, 0.1643]".

Canonical terms: "calibration half", "complementary test half", "fixed
post-probe evaluation pool", "full-pool risk", "selected rule", "marginal
CAFA", "plug-in selector", "fixed-pool estimand", "population-level
validity guarantee". Avoid: "independent test set" (halves are
complementary, not independent); "unbiased test risk" (at the selected rule
it is anti-biased by selection); "the correlation is -1 for the selected
rule" (false in general -- Section 3.2); "zero violations" without the
resplit/cell scope; "the plug-in cheats" (it is uncorrected, not
dishonest); "the pool gate proves distribution-free validity".

---

## 16. Contradiction checks

- 0/35 vs 34/35+1: resolved -- 34 cells at 0/100 plus mnist/greedy/ts1 at
  1/100; "0/35" is true only of gate FAILURES. Same resolution as S6.
- The MNIST seed-1 event: a genuine resplit-level violation that still
  PASSES the cell gate (UB 0.054488 <= 0.1). Consistent everywhere.
- Wilson UB 0.0545: exact 0.054488 -- consistent.
- "corr = -1.0000": canonical artifacts scope it to FIXED thresholds
  (POOL_RISK_GATE headline "at fixed lambda"); no canonical artifact claims
  -1 for the selected rule; S9 must preserve that scoping (Section 3.2
  measured +0.20 on MNIST).
- Test-half vs full-pool: all violation claims in S9 use the pool artifacts;
  test-half numbers appear only as labeled diagnostics.
- "Plug-in unsafe on 2/4": alpha_sweep_transitions (test-half) says UNSAFE
  on MNIST and Spambase; the pool sweep corrects MNIST to 0/100 at the
  committed alpha (nonmonotone nearby) -- resolved in favor of the pool
  artifact; the 2/4-unsafe phrasing must not appear.
- MiniBooNE corrected verdict: 0/100 at committed on BOTH estimands
  (test-half transition bracket (0.1344, 0.1363]; pool crossing
  (0.1044, 0.1344]) -- no conflict, but quote the pool bracket.
- Committed alphas: measured directly in the pool sweep (is_committed
  rows), not interpolated -- confirmed.
- CAFA fallback in primary cells: none (0/3,500 overall) -- consistent.
- Gate precommitment: documented in script + MD header; no artifact
  contradicts it.

No unresolved conflicts remain.

---

## 17. Missing information and final verdict

### Missing information

1. Per-resplit calibration-half risks at the selected rule: not stored;
   exactly reconstructable via the finite-pool identity (done here, flagged
   in every use); independently computed only transiently inside
   pool_risk_gate.py.
2. CAFA (and IUT) pool-estimand results on the alpha-sweep grid away from
   the committed alphas: not stored (test-half only -- superseded); pool
   CAFA exists only at the committed alphas via the gate.
3. Plug-in per-resplit test-half risks: stored (metrics, 6-dp); plug-in
   per-resplit calibration risks: not stored (same identity reconstruction
   applies).
4. Per-resplit fixed-sequence p-values: not persisted (selector recomputed
   and asserted by the gate instead).
5. Selected-rule correlations: not stored as scalars; computed here from
   stored pool/test values plus the identity (Section 3.2).
6. Superseded-estimand-only: test-half sweep verdicts and violation rates.
7. Ambiguous/contradicted: none after Section 16.

### Required author decisions

1. Panel A: Option B (recommended), Option A small multiples, or the
   stored-only test-vs-pool scatter (Section 10).
2. Whether the Panel-A x-coordinate may be identity-reconstructed with a
   caption note, or cal risks must first be recomputed from the pool caches
   (one small read-only cache script; outside the frozen repo).
3. One pooled panel vs four small multiples if Option A is chosen.
4. Table S10: keep mean pool risk + violations (recommended) vs violations
   only.
5. Include the hypergeometric-conservativeness sentence: recommended yes
   (exact wording and citation in Section 11.3).
6. The complete 35-cell comparison: keep in S6 and reference from S9
   (recommended), embedding only the aggregate sentence.

### Final verdict

`S9 SOURCE MATERIAL COMPLETE`

All values for the equation block, Table S10, and both figure panels are
verified and embedded above (400-row Panel A CSV, 28-row Panel B CSV,
35-row comparison CSV); `figS9_01_instruction.md` can be written as soon as
decisions 1-3 are made.
