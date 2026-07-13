# CAFA v2 -- RESULTS FOR THE PAPER (complete compendium, canonical-v2.3)

One file with every result the paper may use, down to the small details.
Compiled 2026-07-12 from the FINAL claim-validity freeze `canonical-v2.3`
(git 4b8b557; audit run at 7bdb1bf) plus the local replication runs.
Supersedes the v2.2 edition of this file: the plugin and hidden-stratum
headlines now use the CORRECT (full-pool) estimand, IUT is accounted over
105 configurations, and the paper story is fixed to **Outcome A**.

## 0. How to use this file

- **The story is FROZEN: Outcome A** (selected from data by
  `results_committed/FINAL_CLAIM_DECISION.md`, never before it existed).
  Licensed thesis sentence: *"A marginally certified AFA system can conceal
  a trajectory-defined stratum for which no stopping threshold in the
  precommitted family meets the target. CAFA audits this family-wide failure
  and uses a common-threshold certificate that refuses when evidence does
  not support simultaneous validity."*
- **Estimand rule:** headline numbers use the FULL-POOL estimand (exact risk
  on the fixed evaluation pool). Test-half numbers appear only in Section 15
  (diagnostics) -- complementary 50/50 halves anti-correlate exactly
  (measured rho = -1.0000), so test-half gates over-report.
- **CANONICAL only:** every citable number comes from
  `results_committed/` at tag canonical-v2.3. LOCAL numbers appear only in
  Section 16 (reproducibility). Recompute any table:
  the Phase-5.3 scripts with `--metrics-dir results_committed/metrics`.
- **Deleted claims (never reuse):** "plugin unsafe on 2 of 4"; "property of
  the data"; any "no budget/subset/policy could attain the target"
  generalization; "0/35 IUT" as an inferential summary; "prediction
  abstention" (the system always predicts; refusal -> full-acquisition
  fallback).
- Freeze: `repro/MANIFEST.sha256` (CRLF-normalized); frozen core
  `c37ab67bbb02...` / `3ec1258ad95d...`; `git diff configs/` empty at every
  re-freeze.

---

## 1. Experimental setup (the facts reviewers ask for)

### 1.1 Datasets and pools (canonical, ts=0)

| dataset | features T | encoded cols | classes | train n | heldout n | probe n | eval pool n | primary cost scheme |
|---|---|---|---|---|---|---|---|---|
| mnist (7x7 patches of 4x4 px) | 49 | -- | 10 | 42000 | 28000 | 2800 | 25200 | uniform |
| tabular:adult (OpenML v2) | 14 | 104 | 2 | 27133 | 18089 | 1809 | 16280 | inverse_info |
| tabular:MiniBooNE (OpenML v1) | 50 | 50 | 2 | 78038 | 52026 | 5203 | 46823 | inverse_info |
| tabular:spambase (OpenML v1) | 57 | 57 | 2 | 2761 | 1840 | 184 | 1656 | inverse_info |

### 1.2 Protocol constants

- Splits: train 60% (by train_seed), probe 10% of heldout (seed 777, fixed),
  eval = remaining 90%; 100 UNIQUE cal/test resplits (50/50, RNG offset
  1,000,000); train/probe/eval pairwise disjoint (asserted). Edges / alpha /
  costs are functions of (train, probe) only.
- Method: delta = 0.10; grid = 100 thresholds linspace[0, 1] (lambda = 1
  behaves as full acquisition up to softmax saturation -- measured in
  PHASE5_PROVENANCE.md); HB p-values + fixed-sequence FWER; cheapest
  certified lambda deployed. Audit level for feasibility verdicts:
  gamma = 0.05, one-sided exact binomial / Clopper-Pearson.
- Stratification: probe-committed quantile-5 reference-depth buckets at
  lambda_ref in {0.5, 0.7, 0.9}; the CONFIRMATORY stratum is the DEEPEST
  precommitted nonempty bucket (label-free; canonically it coincides with
  the argmax-risk stratum on 4/4 primary cells -- PHASE5_PROVENANCE.md).
  lambda_ref = 0.9 is the fine-resolution analysis (sweep committed in
  tooling before results); all three lambda_refs are always published.
- 35 canonical cells (8 Phase-1 + 8 eps + 16 seeds + 3 margin) x 3
  lambda_refs = 105 IUT configurations. Marginal statistics ALWAYS use the
  100 unique resplits (never n = 300).
- Committed targets (fixed rule alpha = ceil_0.05(floor + 0.05)):
  mnist 0.0779 -> 0.15; adult 0.1465 -> 0.20; MiniBooNE 0.0844 -> 0.15;
  spambase 0.0543 -> 0.15 (ts0). Per-seed: mnist ts1 0.1011 -> 0.20 (step
  crossing), ts2 0.15; adult ts1 0.1614 -> 0.25 (crossing), ts2 0.20;
  MiniBooNE/spambase 0.15 at all seeds.

---

## 2. Headline results (Outcome A; all full-pool estimand)

1. **Family-wide failure, certified.** On the deepest precommitted
   (label-free) stratum, NO stopping threshold among the 100 committed
   thresholds and NO forced acquisition depth attains the target on three of
   four datasets: mnist (min family risk 0.2479, family p = 1.4e-79),
   MiniBooNE (0.2334, p = 3.2e-98), adult (0.3090 at lambda 0.899,
   p = 8.7e-93); both threshold- and depth-family verdicts certified at
   gamma = 0.05. spambase: unresolved (p = 0.18, n_k = 249).
2. **The concealment is quantified on the correct estimand.** At the
   marginally selected threshold, the deepest stratum's mean POOL risk is
   0.3006 (mnist), 0.3554 (MiniBooNE), 0.3127 (adult) -- **1.56-2.37x the
   target** on the resolved datasets (spambase 0.3851, 2.57x, unresolved) --
   while the aggregate pool risk sits comfortably below alpha (mnist
   0.1415 vs 0.15). The marginal certificate is valid AND blind to the
   stratum, simultaneously.
3. **CAFA-IUT, honestly accounted over 105 configurations:** 61 certify
   non-vacuously; the 60 configurations that ever refuse split into **40
   refusals justified by certified family-wide failure, 0 endpoint-only,
   20 unresolved**; exactly 1 conditional pool-failure among certified
   selections in the whole grid (spambase ts1, certified once in 100).
   Uniform per-stratum validity is free where achievable (premium 1.000x at
   feasible configs) and refuses -- with proof of WHY, in the 40 class-A
   configs -- where it is not.
4. **Certified stopping is cheap:** CAFA-marginal stops at 5.0% (MiniBooNE),
   9.1% (spambase), 36.1% (adult), 50.7% (mnist) of full-acquisition cost at
   the committed target, at/near the non-deployable oracle floor
   (cost/oracle 1.000-1.034 at ts0).
5. **The evaluation methodology is itself a contribution:** complementary
   cal/test halves of a finite pool anti-correlate exactly (measured
   rho = -1.0000 on all 35 cells), so test-split gates systematically
   over-report violations for ANY conformal/LTT certificate. On the correct
   pool estimand: the marginal certificate passes the validity gate in all
   35 cells (34 at exactly 0/100; worst cell 1/100 -- Section 10), and the
   plugin headline CHANGES (Section 6).
6. **Detection power is prospectively validated:** controlled Bernoulli
   simulation (B = 5000/grid point), max false-positive rate over all null
   points = 0.0500 = gamma (exact control); power rises in stratum mass,
   margin, and n; the sufficient bound is conservative but directionally
   predictive.

---

## 3. Family-wide feasibility (Task 1 -- the central table)

Confirmatory stratum = deepest precommitted nonempty bucket; gamma = 0.05;
intersection-union over all 100 thresholds / all forced depths; exact
one-sided binomial tails; per-dataset p-values (no cross-dataset FWER claim).

| dataset | stratum (n_k, q_k) | alpha | min threshold-family risk (argmin lambda) | full-feature risk | family p | THRESHOLD verdict | min depth risk (argmin t) | depth p | DEPTH verdict |
|---|---|---|---|---|---|---|---|---|---|
| mnist | 4 (5479, 0.2174) | 0.15 | 0.2479 (~0.9-1.0) | 0.2479 [LCB 0.2383] | 1.4e-79 | **failure certified** | 0.2479 (t=49) | (same order) | **certified** |
| MiniBooNE | 4 (9180, 0.1961) | 0.15 | 0.2334 | 0.2334 [LCB 0.2262] | 3.2e-98 | **certified** | 0.2334 (t=50) | -- | **certified** |
| adult | 3 (6268, 0.3850) | 0.20 | 0.3090 (plateau lambda 0.869-0.889) | 0.3092 [LCB 0.2996] | 8.7e-93 | **certified** | ~0.3090 (t<T) | -- | **certified** |
| spambase | 4 (249, 0.1504) | 0.15 | 0.1727 (lambda 1.0) | 0.1727 [LCB 0.1344] | 1.8e-01 | unresolved | 0.1727 (t=T) | -- | unresolved |

Small details: adult's curve has its minimum slightly BELOW the full
endpoint (0.309030 on a three-threshold plateau at lambda in {0.8687,
0.8788, 0.8889} vs 0.309190 at full; the earlier "at lambda 0.899" was the
LOCAL pilot's argmin -- corrected per reviewphase_0_1_reply.md) -- more
information is not monotonically better, which is exactly why the
family-wide test (not just the endpoint) was needed. Full curves (all 105 configs, threshold +
depth) in `family_wide_threshold_curves.csv` / `family_wide_depth_curves.csv`;
figures F8/F9. Endpoint reproduction vs the frozen H3 rows: asserted exact,
4/4.

**Licensed wording** (three resolved datasets): "no stopping threshold in
the audited precommitted threshold family attains the target, and no prefix
depth along the frozen acquisition path attains it." spambase: "the audit is
unresolved at the available sample size." NEVER: any claim about arbitrary
feature subsets, other policies, or monetary budgets.

---

## 4. Corrected Figure 1 (mnist ts0 greedy, lambda_ref 0.9; POOL estimand)

Per-stratum mean POOL risk at the resplit-selected marginal threshold
(whiskers = p5-p95 across the 100 calibration selections, NOT population
CIs); figure `F1_pool_corrected`:

| stratum | n_k | q_k | mean POOL risk [p5, p95] | exceed freq | endpoint R_full [CP LCB] | verdict |
|---|---|---|---|---|---|---|
| 0 | 4906 | 0.1947 | 0.09131675 [0.091317, 0.091317] | 0.00 | 0.044435 [0.039697] | feasible |
| 1 | 5152 | 0.2044 | 0.11328998 [0.111801, 0.113548] | 0.00 | 0.045031 [0.040374] | feasible |
| 2 | 5490 | 0.2179 | 0.09480510 [0.092896, 0.095082] | 0.00 | 0.039162 [0.034947] | feasible |
| 3 | 4173 | 0.1656 | 0.08760844 [0.075246, 0.089863] | 0.00 | 0.031153 [0.026854] | feasible |
| 4 | 5479 | 0.2174 | **0.30057310 [0.288739, 0.302610]** | **1.00** | **0.247855 [0.238270]** | **family-wide failure** |

Aggregate POOL risk at the selected rule = **0.14145159** (< alpha = 0.15);
sum q_k R_k reconstructs it exactly (asserted per resplit). Paste-ready:

```python
RISK_AGG_POOL = 0.14145159
RISK_S0_S3_POOL = [0.09131675, 0.11328998, 0.09480510, 0.08760844]
RISK_S4_POOL = 0.30057310    # endpoint tick 0.247855, CP LCB 0.238270
```

(The v2.2 test-half values -- agg 0.14142696, s4 0.30053916 -- differ only
in the 4th decimal; Figure 1's qualitative effect is fully preserved under
the estimand correction. Old values now live in Section 15 diagnostics.)

Selected-rule deepest-stratum POOL risks, all primary datasets: mnist
0.3006 (2.004x alpha), MiniBooNE 0.3554 (2.370x), adult 0.3127 (1.563x),
spambase 0.3851 (2.567x, unresolved). Full grid (35 cells x 3 lambda_refs x
strata): `pool_stratum_eval.csv`.

---

## 5. H2 -- cost efficiency (canonical, lambda_ref 0.9, primary scheme)

Costs are estimand-independent (unchanged from v2.2). Violation columns:
see Section 6 (plugin, pool estimand) and Section 15 (test-half diagnostics).

| cell | CAFA cost / cost-vs-full | plugin cost/full | fixed_conf_0.95 | budget_10 | oracle_cheapest | full |
|---|---|---|---|---|---|---|
| mnist/greedy | 24.85 / 0.507 | 0.491 | 0.742 | 0.204 | 0.490 | 49.00 |
| mnist/random | 25.90 / 0.529 | 0.518 | 0.815 | 0.204 | 0.518 | 49.00 |
| MiniBooNE/greedy | 17.01 / 0.050 | 0.050 | 0.388 | 0.163 | 0.050 | 341.06 |
| MiniBooNE/random | 56.48 / 0.166 | 0.159 | 0.493 | 0.200 | 0.160 | 341.06 |
| adult/greedy | 34.36 / 0.361 | 0.361 | 0.591 | 0.717 | 0.361 | 95.28 |
| adult/random | 26.41 / 0.277 | 0.277 | 0.658 | 0.714 | 0.277 | 95.28 |
| spambase/greedy | 37.80 / 0.091 | 0.057 | 0.351 | 0.151 | 0.057 | 413.78 |
| spambase/random | 86.16 / 0.208 | 0.167 | 0.527 | 0.175 | 0.168 | 413.78 |

Fixed-confidence heuristics are safe but 1.5-8x more expensive than CAFA;
budget-k violates massively wherever alpha is tight (test-half diagnostic,
Section 15). CAFA cost/oracle at ts0: 1.000-1.034.

---

## 6. The plugin, corrected (Task 2 -- pool estimand; headline CHANGED)

Pool exceedance of the plugin-selected threshold, committed alpha, 100
calibration draws (selection asserted equal to the original on every draw):

| dataset | POOL exceedance [95% CI] | test-half (diagnostic) | three-way label |
|---|---|---|---|
| mnist | **0.000 [0.000, 0.037]** | 0.35 | not shown unreliable at this resolution |
| MiniBooNE | 0.000 [0.000, 0.037] | 0.00 | not shown unreliable at this resolution |
| adult | 0.000 [0.000, 0.037] | 0.00 | not shown unreliable at this resolution |
| spambase | **0.450 [0.356, 0.548]** | 0.45 | **clearly unreliable** |

- **"Plugin unsafe on 2 of 4" is deleted.** mnist's test-half 0.35 was
  itself the complementary-split artifact; on the pool the selected
  threshold exceeded the target in 0/100 draws. Exact language: "the
  plugin's selected threshold exceeds the target on the fixed evaluation
  pool in x/100 calibration draws" -- and 0/100 is never called "safe".
- Pool alpha-sweep transitions (F11; committed alpha always measured):
  mnist **NONMONOTONE -- no single safety transition exists** (crossings at
  (0.0979, 0.1279], (0.1279, 0.1500], (0.1579, 0.1879]); MiniBooNE single
  crossing (0.1044, 0.1344]; adult safe at every swept alpha; spambase
  single crossing (0.1500, 0.1643] -- the committed target sits at the
  unreliable edge.
- The argument for certificates survives in corrected form: the plugin's
  reliability at a committed target is a nonmonotone, dataset-specific
  property (mnist's sweep has three crossings) that no pilot predicts, and
  on small pools (spambase) it fails badly -- whereas the certificate's
  validity needs no such luck. 'clearly unreliable' on 10 of 35 cells over
  the full grid (all eps/seed/margin cells: `pool_plugin_eval.csv`).

---

## 7. CAFA-IUT over 105 configurations (Task 4 -- replaces "35/35")

- **61/105 configurations certify non-vacuously** (>= 1 certified selection
  among the 100 resplits).
- The 60 configurations that ever refuse: **A: 40 -- refusal justified by
  certified family-wide failure** (the blocking stratum provably fails the
  whole threshold family); **B: 0** endpoint-only; **C: 20 -- unresolved**
  (spambase and small shallow-lambda strata).
- **Conditional pool-failures among certified selections: 1 of 105 configs**
  -- spambase/greedy/ts1 at lambda 0.9: certified exactly once in 100
  resplits and that single certification failed a stratum (n_cert = 1; no
  interval printed at that denominator).
- Terminology: "certification refusal with full-acquisition fallback" -- the
  system still predicts (never "prediction abstention").
- Costs where the IUT certifies: free at feasible configurations (premium
  1.000x vs marginal at lambda 0.5/0.7 tabular); the full price list per
  configuration in `iut_by_lambda_ref.csv`; certification-rate and
  cost-refusal-frontier figures F12/F13. (The v2.1 non-vacuity table --
  min certifying alpha per dataset, e.g. MiniBooNE certifies every stratum
  at 16.3% of full cost at alpha 0.2844 -- remains valid supporting
  material: `IUT_NONVACUITY.md`.)
- Valid summary sentence: "Across 105 fixed configurations, 61 certify
  non-vacuously; refusals split into 40 family-failure, 0 endpoint-only,
  and 20 unresolved configurations."

---

## 8. Synthetic power validation (Task 6 -- prospective)

Bernoulli grid: q in {0.02..0.40} x Delta in {0.01..0.15} (+ nulls 0,
-0.02) x n in {500..50000}, B = 5000/point, alpha 0.15, gamma 0.05
(seed 20260712):

- **False-positive control: max empirical FPR over ALL null points = 0.0500
  = gamma. PASS (exact).**
- Power rises monotonically in q, Delta, n (heatmaps F14, curves F15);
  unresolved frequency tracks empty-stratum probability at tiny n*q.
- The theorem's sufficient threshold n*q >= log(1/gamma)/(2 Delta^2) is
  conservative but directionally predictive: operating points above it show
  near-1 power; points below it degrade as predicted.
- Family-size calibration (M in {10, 50, 100}): the family max-p test
  rejects all-infeasible families and does not reject one-feasible families
  (calibration study, not a proof) -- `synthetic_power.csv` + summary json.
- Licensed wording: "the sufficient bound is comfortably met in the three
  large primary strata and badly missed in spambase's small stratum,
  consistent with the observed resolved/unresolved split" (retrospective
  diagnostic) + the prospective simulation. NEVER: "the theorem gives the
  minimum required sample size" or "spambase proves no method could detect".

---

## 9. Supporting results (unchanged by the estimand correction)

- **Cross-seed stability (Phase 3):** the deepest stratum's verdict
  reproduces at every train seed on every dataset (12/12) -- infeasible on
  mnist (R_full 0.248/0.266/0.268), MiniBooNE (0.233/0.223/0.249), adult
  (0.309/0.316/0.302); undetermined on spambase. Alpha step crossings:
  mnist ts1 -> 0.20, adult ts1 -> 0.25 (the fixed rule per backbone).
- **Score robustness (Phase 4):** verdicts unchanged under the margin score
  with its own probe-committed stratification (3/3); `order`/`correct`
  byte-identical across scores (the ablation changed only the stopping
  score); alpha score-independent.
- **Licensed robustness wording:** "the stratum's failure verdict reproduces
  across backbone draws and readiness scores" (NOT "property of the data").
- **Pool-risk gate (Phase 5.2):** marginal certificate 0/35 cells violated
  on the pool estimand; measured corr(R_cal, R_test) = -1.0000 on every
  cell; lambda-hat recomputation matched 3,500/3,500.
- **Concentration (Phase 2):** a quantified observation only -- rho(quality,
  entropy@0.5) = -0.746 (p = 0.0009), fading to n.s. at 0.9; monotone on
  1 of 4 datasets; the detection frontier does not move with policy quality
  in any supported direction (aggregate frontier rho 0.576 is a
  between-dataset confound; never quote as support).
- **Validity diagnostic (Phase 5):** corr(predicted-from-noise, observed
  test-half violations) = 0.762; failing cells all have margins
  alpha - R_pool = 0.007-0.027 (~1-3 SE) -- the mechanism behind Section 15's
  diagnostics.

---

## 10. Gate summary (correct denominators)

- Marginal certificate, POOL estimand, 100 unique resplits: **all 35 cells
  PASS the precommitted validity gate** (Wilson UB <= delta). 34/35 cells
  have exactly 0/100 violations; the one exception is
  mnist/greedy_entropy/ts1 with 1/100 (rate 0.010, Wilson UB 0.0545).
  NEVER write "0/100 in every cell" (corrected per
  reviewphase_0_1_reply.md, contradiction C10).
- IUT: per-configuration accounting in Section 7 (never pooled across
  lambda_refs; conditional denominators = n_certified).
- Plugin: Section 6 (descriptive benchmark, not a guarantee).
- Test-half gate tables (the historical 29/35 with six FAILs) are
  diagnostics: Section 15.

---

## 11. Provenance decisions (PHASE5_PROVENANCE.md)

- Confirmatory stratum = deepest precommitted nonempty bucket (label-free);
  canonically coincides with argmax-risk k* on 4/4 primary cells.
- lambda_ref = 0.9 = fine-resolution analysis; sweep {0.5, 0.7, 0.9}
  committed in tooling before results (git evidence in
  phase5_provenance.json); all three published.
- lambda = 1 vs full acquisition: measured agreement per dataset in the
  provenance file (softmax saturation caveat).
- 100 resplits are independent seeded 50/50 permutations; marginal
  statistics never use n = 300.

---

## 12. Figures index (canonical, results_committed/figures/)

| figure | contents |
|---|---|
| F1_pool_corrected | THE Figure 1: per-stratum selected-rule POOL risk, mnist primary (Section 4) |
| F1-F4 (per ds/ts) | legacy risk-cost scatters, test-half stratum bars, concentration, detection scatter (diagnostics/supplement) |
| F5_<ds> | alpha sweep (test-half; superseded by F11 for plugin claims) |
| F6 | validity diagnostic (predicted vs observed test-half violations) |
| F7 | pool-risk gate + rho = -1 anti-correlation |
| F8_<ds> / F9_<ds> | family-wide THRESHOLD / DEPTH risk curves on the deepest stratum |
| F10 | plugin pool-vs-test exceedance (35 cells) |
| F11_<ds> | plugin POOL alpha sweep (the corrected transition story) |
| F12 / F13 | IUT certification by lambda_ref / cost-refusal frontier (105 configs) |
| F14_<n> / F15 | synthetic power heatmaps / power-vs-n |

Main-paper candidates: F1_pool_corrected, F8 (mnist), F12 or F13, F11
(mnist, the nonmonotone sweep), F14 or F15. Everything else: supplement.

---

## 13. Sentence-ready claims (licensed; each maps to a canonical row)

1. (Thesis) "A marginally certified AFA system can conceal a
   trajectory-defined stratum for which no stopping threshold in the
   precommitted family meets the target; CAFA audits this family-wide
   failure and uses a common-threshold certificate that refuses when
   evidence does not support simultaneous validity."
2. "On the deepest precommitted stratum of three of four datasets, no
   stopping threshold in the audited 100-threshold family and no prefix
   depth along the frozen acquisition path attains the target (family
   intersection-union p <= 8.7e-93); the fourth dataset is unresolved at
   its sample size (p = 0.18, n = 249)."
3. "At the marginally selected threshold, the concealed stratum's exact
   pool risk is 1.56-2.37x the target on the resolved datasets, while the
   aggregate pool risk stays below it -- the certificate is valid and blind
   simultaneously."
4. "Across 105 fixed configurations, CAFA-IUT certifies non-vacuously in
   61; its 60 refusals split into 40 justified by certified family-wide
   failure, 0 endpoint-only, and 20 unresolved; certified selections failed
   a stratum on the pool exactly once (a single-certification spambase
   configuration)."
5. "Certified stopping is cheap: 5-51% of full-acquisition cost at the
   committed target, within 3.5% of a label-using oracle's cost."
6. "Complementary calibration/test halves of a finite pool anti-correlate
   exactly (measured rho = -1.0000), so test-split violation frequencies
   systematically over-report for any conformal/LTT certificate; on the
   correct pool estimand our marginal certificate satisfies its precommitted
   validity gate in all 35 cells (34 with zero violations in 100 draws;
   worst cell 1/100, Wilson UB 0.054), and the plugin's apparent
   unreliability on mnist (0.35) vanishes (0/100) -- its true failure mode
   is small pools (spambase 45/100) and a nonmonotone safety profile no
   pilot can predict."
7. "A controlled Bernoulli study confirms the audit's exact false-positive
   control (max FPR = gamma) and shows detection power rising in stratum
   mass, margin, and sample size, with the sufficient bound conservative
   but directionally predictive."

## 14. Limitations checklist (must survive into the paper)

- spambase is unresolved everywhere by sample size (probe n = 184, deepest
  stratum n = 249) -- including its 1-certification conditional failure; a
  boundary example, never evidence.
- Family-wide claims are model-relative and family-relative: the frozen
  predictor, the frozen acquisition path, the committed threshold family.
  No claim about other subsets/policies/budgets is licensed.
- The plugin three-way labels are descriptive benchmark classifications,
  not guarantees; 0/100 pool exceedance is not "safe".
- Whiskers on Figure 1 are variation across calibration selections, not
  population CIs; endpoint bounds are one-sided CP.
- k* provenance: confirmatory = deepest bucket; the coincidence with
  argmax-risk is a canonical fact, not an assumption.
- Test-half tables are retained as diagnostics only (Section 15).

## 15. Diagnostics (test-half estimand; historical -- NOT citable as results)

- Old gate table: marginal test-half 29/35 PASS with six FAILs (mnist eps
  0.110/0.140; spambase 0.080-0.110); explained by the validity diagnostic
  (corr 0.762) and resolved by the pool gate (0/35).
- Old plugin test-half violations: mnist 0.35, spambase 0.45, MiniBooNE/
  random 0.30 -- superseded by Section 6.
- Old test-half alpha-sweep (F5) and its "unsafe on 2 of 4 (measured)"
  verdict -- superseded by Section 6's pool sweep.
- Old Figure-1 test-half values (agg 0.14142696; s4 0.30053916) -- match the
  pool values to the 4th decimal; kept in FIGURE1_TABLE4_VALUES.md.
- Per-seed test-half H3 "marginal realized risk on k*" (0.3005/0.3282/...)
  -- superseded by pool_stratum_eval.csv per-seed rows.

## 16. LOCAL replication (laptop; REPRODUCIBILITY SECTION ONLY)

- Structural findings replicate exactly: family-wide failure certified on
  the same three datasets locally (p <= 6.5e-24), spambase unresolved;
  corr(R_cal, R_test) = -1.0000; pool gates 0/33; FPR controlled.
- Environment-sensitive details differ as expected: local alphas (adult ts0
  = 0.25), local floors, which cells are borderline on test-half
  diagnostics, local IUT counts (56/99 non-vacuous, A:33 / C:23).
- 48/48 tests pass locally (41 + 7 Phase-5.3); verify_bugs ALL PASS with the
  CRLF-normalized freeze check.

## 17. Artifact map (canonical-v2.3)

| artifact | path |
|---|---|
| THE claim decision (story + ledger + prohibited list) | `results_committed/FINAL_CLAIM_DECISION.md` + `.json` |
| Family-wide audit | `results_committed/FAMILY_WIDE_FEASIBILITY.md`, `family_wide_*.csv/.json`, F8/F9 |
| Plugin pool eval + pool alpha sweep | `results_committed/POOL_PLUGIN_EVAL.md`, `POOL_PLUGIN_ALPHA_SWEEP.md`, `pool_plugin_*.csv`, F10/F11 |
| Selected-rule stratum pool risks + corrected Fig 1 | `results_committed/POOL_STRATUM_EVAL.md`, `pool_stratum_*.csv`, F1_pool_corrected |
| IUT 105-config accounting | `results_committed/IUT_BY_LAMBDA_REF.md`, `IUT_OUTCOME_CLASSIFICATION.md`, `iut_by_lambda_ref*.csv`, F12/F13 |
| Synthetic power | `results_committed/SYNTHETIC_POWER.md`, `synthetic_power.csv/.json`, F14/F15 |
| Provenance decisions | `results_committed/PHASE5_PROVENANCE.md` + `.json` |
| Frozen v2.2 evidence (pool gate, alpha sweep, validity, non-vacuity, H2/H3, 35 metrics JSONs) | `CANONICAL_RESULTS.md`, `results_committed/` (Sections 5, 9, 15 sources) |
| Committed targets (ts 0/1/2) | `configs/committed_v2_*.json` |
| Freeze + environment | `repro/MANIFEST.sha256`, `repro/requirements.lock.txt` |
| Project history incl. supersessions | `project_update.md` (Sections 13-16) |
