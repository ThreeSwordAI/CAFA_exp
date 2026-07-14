# S7_answer.md -- Verified source material for S7 (Complete CAFA-IUT Results)

Prepared from canonical frozen artifacts only. Every number was re-extracted
this pass from the files in Section 1; per-configuration counts were recomputed
from the exact per-resplit artifact (`iut_by_lambda_ref_resplits.csv`, 10,500
rows) and asserted equal to the stored per-configuration summaries
(`iut_by_lambda_ref.csv`) -- all cross-checks passed, including a third
independent check against the `abstained` flags in the 35 metrics JSONs
(105/105 configurations match). Nothing is inferred from rounded manuscript
text.

Conventions: a "configuration" = (marginal cell, lambda_ref); counts are exact
integers out of 100 resplits; "pool" = the full post-probe evaluation pool.

---

## 1. Canonical sources and freeze metadata

1. **Exact canonical files used**
   - `results_committed/iut_by_lambda_ref_resplits.csv` -- per-resplit CAFA-IUT
     record for all 10,500 runs: (cell, lambda_ref, resplit, certified,
     lambda_idx, any_stratum_pool_fail). The ground-truth artifact.
   - `results_committed/iut_by_lambda_ref.csv` + `IUT_BY_LAMBDA_REF.md` --
     per-configuration certification/refusal/violation/cost summaries
     (105 rows).
   - `results_committed/IUT_OUTCOME_CLASSIFICATION.md` -- the three-outcome
     refusal-diagnosis semantics and counts.
   - `results_committed/family_wide_summary.csv` (+ `FAMILY_WIDE_FEASIBILITY.md`)
     -- family-wide audit verdict, family p-value, empirical family minimum,
     endpoint risk per configuration (105 rows); joined for refusal diagnosis.
   - `results_committed/family_wide_threshold_curves.csv` -- deepest-stratum
     pool risk R_k(lambda) and exact binomial upper-tail p per grid threshold
     (105 x 100 rows); used to identify the violating stratum risk exactly.
   - `results_committed/metrics/*.json` (35 files) -- per-resplit `cafa_iut`
     selections (`lambda_idx`, `abstained`), per-lambda_ref population blocks
     (realized pool strata `bucket_sizes`), alpha, delta, grid.
   - `configs/committed_v2_<dataset>_ts<seed>.json` -- committed floors,
     alphas, probe-committed stratum edges.
   - Code defining the events: `src/cafa/risk_control_ext.py` (`iut_select`;
     the IUT itself), `src/cafa/risk_control.py` (frozen HB p-value engine),
     `scripts/run_eval_sweep.py` (per-resplit selection + fallback recording),
     `scripts/iut_by_lambda_ref.py` (violation event, Wilson intervals,
     refusal classification), `scripts/family_wide_feasibility.py` (diagnosis
     source), `scripts/phase53_lib.py` (bucketization, Wilson, primary scheme).
   - `results_committed/pool_plugin_eval.csv` -- used only to derive the exact
     full-pool full-acquisition cost per cell (`mean_pool_cost /
     cost_over_full`) for the certified-only cost normalization in Section 8.
2. **Freeze metadata.** Compute closed at tag `canonical-v2.2`; the Phase-5.3
   IUT/family artifacts are stamped with commit `7bdb1bf27fc3` (recorded in
   `FINAL_CLAIM_DECISION.md`; `PHASE5_PROVENANCE.md` records artifact hashes);
   results-compendium version v2.3.
3. **Counts.** Frozen marginal cells: 35. Reference thresholds: 3. CAFA-IUT
   configurations: 105 (verified: 105 rows). Resplits per configuration: 100
   (verified in all 105). Total CAFA-IUT runs: 10,500 (verified: 10,500
   per-resplit rows).
4. **Confirmed: 35 x 3 = 105 with lambda_ref in {0.5, 0.7, 0.9}** (the three
   `lambda_refs` blocks present in every metrics JSON; the audit script's
   default `--lambda-ref 0.5 0.7 0.9`).
5. **Superseded / must not use:**
   - `IUT_NONVACUITY.md` (Phase 5 / v2.1): lambda_ref = 0.9 only, earlier
     accounting; explicitly superseded by the 105-configuration accounting
     (RESULTS_FOR_PAPER Section 7: "replaces 35/35").
   - `h2_table.csv` `cafa_iut` rows: test-half realized values pooled over the
     3 lambda_ref blocks -- wrong denominator for per-configuration claims
     and the superseded estimand; do not quote for S7.
   - Local-replication IUT counts ("56/99 non-vacuous, A:33 / C:23") --
     local environment, never citable (flagged in RESULTS_FOR_PAPER
     Section 16).
   - Any "0/35 IUT" phrasing as an inferential summary (prohibited list,
     RESULTS_FOR_PAPER Section 1).

---

## 2. Exact CAFA-IUT configuration and procedure

### 2.1 Configuration identity

A configuration = (dataset, acquisition policy incl. epsilon, training seed,
readiness score, lambda_ref). The remaining quantities are **fixed attributes
determined by the configuration, not independent dimensions**:

- committed alpha: a function of (dataset, training seed) -- values 0.15/0.20/
  0.25, committed by the probe rule alpha = ceil_0.05(floor + 0.05);
- cost scheme: the cell's primary scheme (MNIST uniform; all tabular
  inverse_info); selection is scheme-invariant under fixed_sequence, the
  scheme fixes the reported cost;
- threshold grid: global, 100 points, linspace(0, 1, 100);
- delta = 0.1 (FWER budget), gamma = 0.05 (family audit), both global;
- nominal strata G0 = 5 (probe-committed quantile-5 reference-depth edges,
  per (policy, score, lambda_ref)); realized strata G = number of nonempty
  pool buckets, an outcome, not a knob: G = 5 in 54 configurations, 4 in 7,
  3 in 3, 1 in 41 (from the per-lambda_ref `bucket_sizes` in the metrics
  JSONs). G = 1 occurs where every pool example crosses lambda_ref in the
  same reference-depth bucket (all tabular cells at lambda_ref 0.5 and most
  at 0.7), making the IUT identical to the marginal test there.

### 2.2 Calibration span

Implementation (`iut_select`, risk_control_ext.py lines 139-166): the strata
tested are the **contiguous integer label span [min, max] of the calibration
half's bucket labels** -- `labels = np.unique(bucket_id)`, `lo, hi =
labels.min(), labels.max()`, loop `for k in range(lo, hi+1)`.

- k_min / k_max: the smallest / largest bucket label present among the
  calibration rows of that resplit (bucket labels are assigned once on the
  full pool from the probe-committed edges and inherited by the resplit
  halves; never refit).
- Labels outside the represented span (below k_min or above k_max): excluded
  -- the certificate makes no claim about them.
- Empty interior label (in the span, zero calibration rows): receives
  p_{lambda,k} = 1.0 at every grid index ("Interior empty stratum: p == 1
  everywhere -> blocks certification" -- code comment), which makes
  p_IUT = 1 > delta everywhere; **certification is conservatively blocked**.
- **Canonical occurrences:** per-resplit calibration spans are NOT stored
  (searched both IUT CSVs and the metrics JSONs), so a per-resplit count is
  `NOT FOUND`. However, the pool-level bucket sizes ARE stored, and exactly
  one configuration has a pool-level interior gap:
  **tabular-adult/greedy_entropy/ts1 @ lambda_ref 0.9**, pool buckets
  {0: 8693, 2: 1181, 3: 383, 4: 6023} -- label 1 has zero pool rows. Every
  calibration half of that configuration therefore necessarily contains an
  empty interior stratum (label 1) with span [0, 4], so all 100 of its
  resplits are structurally blocked; observed certification 0/100, consistent.
  All other 104 configurations have contiguous nonempty pool buckets with
  minimum realized pool-stratum size 133 (min over the `min_stratum_size`
  column), so an empty calibration stratum would require a hypergeometric
  draw missing all >= 133 members of a stratum -- not verifiable per resplit
  from the artifacts, but combinatorially negligible.

### 2.3 Selection and fallback

From `iut_select` (exact code cited in Section 1):

- **Threshold order:** the ascending global grid; the fixed-sequence walk
  starts at the TOP of the grid (index G-1, the most-acquisitive threshold)
  and steps downward.
- **Fixed-sequence stopping rule:** `for j in range(G-1, -1, -1): if
  p_union[j] <= delta: valid_mask[j] = True else: break` -- certify a
  contiguous top block, stop at the first failure.
- **p_IUT:** `p_union = max over strata k in [lo, hi] of p_{lambda,k}`, where
  p_{lambda,k} are the frozen Hoeffding-Bentkus p-values of `ltt_select` run
  on stratum k's calibration rows (its selection output is discarded; empty
  interior strata contribute all-ones).
- **Certification criterion:** p_union[j] <= delta = 0.1 inside the
  fixed-sequence block; guarantee P(exists k in span: R(lambda_hat | k) >
  alpha) <= delta.
- **Selected threshold:** argmin of full-column mean cost over the certified
  set; in this scalar family cost is monotone in the grid index, so this is
  the SMALLEST certified index (bottom of the certified block) -- stated in
  the code as "effectively cost-blind".
- **Fallback:** if the certified set is empty, `lambda_idx = None` ->
  **full acquisition** (`_fallback_full` in the runner: every instance
  acquires all T features and the model predicts). The system **still
  predicts** -- this is certification refusal, NOT prediction abstention.
- **Certificate under fallback:** none. The full-acquisition fallback carries
  no marginal and no simultaneous certificate in the artifacts; it is the
  no-claim outcome (the marginal certificate is a separate method, not
  attached to the IUT fallback).

### 2.4 Certification and refusal events

Per resplit (runner, run_eval_sweep.py lines 296-308):

- `certified` := `cafa_iut.lambda_idx is not None` (equivalently
  `abstained == False`);
- `refused` := `lambda_idx is None` (recorded as `abstained: true`);
- `fallback` := refusal; identical event (refusal -> full-acquisition
  fallback, 1:1);
- certification and refusal are **exact complements**: asserted per
  configuration in the audit (`assert cert + refuse == n`), and re-verified
  here for all 105 configurations from the per-resplit rows;
- denominator for all rates: **n = 100 resplits**, every configuration
  (verified: each of the 105 configurations has exactly 100 per-resplit
  rows; no missing or malformed selections encountered -- the extraction
  asserts lambda_idx presence exactly matches the certified flag on all
  10,500 rows);
- eligible runs: exactly 100 everywhere; no exclusions of any kind.

---

## 3. Complete 105-configuration result table

One row per (cell, lambda_ref), ordered lambda_ref 0.5 (35 cells), then 0.7,
then 0.9; within a panel: dataset, policy, seed, score. Field provenance:

- identifiers, floor, alpha: metrics JSONs + committed configs;
- `G_realized`: number of nonempty pool buckets (metrics `bucket_sizes`);
- `certified`, `refused`, `fallbacks` (= refused): recomputed exactly from
  `iut_by_lambda_ref_resplits.csv` and asserted equal to the stored
  `n_certified`;
- `lam_min/med/max`: stored in `iut_by_lambda_ref.csv` and re-derived from
  the per-resplit lambda_idx (asserted equal); `lam_mean`: **computed here
  from the exact per-resplit lambda_idx** (not stored as a scalar);
- `uncond_fail_count` / `cond_fail_count`: recomputed from the per-resplit
  `any_stratum_pool_fail`; by construction the two counts are identical
  (the event is only evaluated on certified runs; refused runs contribute 0)
  -- the rates differ only in denominator (100 vs n_certified);
- `cond_wilson_hi`: the stored Wilson-95% upper bound with denominator
  n_certified (empty when n_certified = 0);
- costs: stored per-configuration values, FULL-POOL convention (Section 8);
  `certonly_cost_over_full` derived here as mean_certified_cost divided by
  the exact full-pool full-acquisition cost;
- `family_verdict`, `family_p_value`, `min_threshold_risk`: joined from
  `family_wide_summary.csv` (threshold family; deepest precommitted nonempty
  stratum); `diag_code` from the stored `refusal_class` (F = A-class,
  U = C-class, `--` = never refuses; B never occurs).

`NOT FOUND` fields for every row (searched all Section-1 artifacts):
per-resplit realized calibration spans and their histogram; per-resplit
empty-interior-stratum counts (Section 2.2 gives the one structurally forced
configuration); cost percentiles (p5/p95) and median deployed cost (only
means are stored; per-resplit deployed costs are reconstructable from
lambda_idx + the frozen pool caches, which are not in the repository).

```csv
config_id,dataset,policy,eps,seed,score,scheme,floor,alpha,lambda_ref,G_nominal,G_realized,primary,certified,refused,fallbacks,lam_min,lam_med,lam_mean,lam_max,uncond_fail_count,cond_fail_count,cond_fail_rate,cond_wilson_hi,mean_certified_cost,mean_deployed_cost,deployed_cost_over_full,certonly_cost_over_full,premium_vs_marginal,min_stratum_size,deepest_stratum,family_verdict,family_p_value,min_threshold_risk,diag_code
mnist/eps_greedy_eps0.25/ts0@lr0.5,mnist,eps_greedy_eps0.25,0.25,0,softmax,uniform,0.077857,0.15,0.5,5,5,0,100,0,0,0.858586,0.878788,0.875556,0.909091,0,0,0.000000,0.036995,26.164023,26.164023,0.533960,0.533960,1.173574,2635,4,feasible,0.9999999925345465,0.12315455055129883,--
mnist/eps_greedy_eps0.5/ts0@lr0.5,mnist,eps_greedy_eps0.5,0.5,0,softmax,uniform,0.077857,0.15,0.5,5,5,0,100,0,0,0.818182,0.838384,0.842626,0.919192,0,0,0.000000,0.036995,24.668252,24.668252,0.503434,0.503434,1.140663,4349,4,feasible,0.999999999469505,0.12314874436574372,--
mnist/greedy_entropy/ts0[margin]@lr0.5,mnist,greedy_entropy,,0,margin,uniform,0.077857,0.15,0.5,5,5,0,45,55,55,0.828283,0.878788,0.881930,0.949495,0,0,0.000000,0.078654,32.366305,41.514837,0.847242,0.660537,1.664925,3540,4,feasible,0.9940366804891108,0.13797585886722377,U
mnist/greedy_entropy/ts0@lr0.5,mnist,greedy_entropy,,0,softmax,uniform,0.077857,0.15,0.5,5,5,1,100,0,0,0.898990,0.909091,0.912121,0.929293,0,0,0.000000,0.036995,30.697605,30.697605,0.626482,0.626482,1.235061,3160,4,feasible,0.9999999999999984,0.11614906832298137,--
mnist/greedy_entropy/ts1@lr0.5,mnist,greedy_entropy,,1,softmax,uniform,0.101071,0.2,0.5,5,5,0,100,0,0,0.888889,0.909091,0.908788,0.969697,0,0,0.000000,0.036995,33.055227,33.055227,0.674596,0.674596,1.276057,2846,4,feasible,0.9999999999998955,0.16808799901124707,--
mnist/greedy_entropy/ts2@lr0.5,mnist,greedy_entropy,,2,softmax,uniform,0.094286,0.15,0.5,5,5,0,90,10,10,0.969697,0.979798,0.977890,1.000000,0,0,0.000000,0.040937,42.377731,43.039958,0.878366,0.864852,1.189183,2960,4,feasible,0.9998747452926656,0.13314888466194016,U
mnist/random/ts0@lr0.5,mnist,random,,0,softmax,uniform,0.077857,0.15,0.5,5,5,0,77,23,23,0.787879,0.858586,0.861603,0.969697,0,0,0.000000,0.047520,33.381877,36.974046,0.754572,0.681263,1.427283,4022,4,feasible,0.9997537499669857,0.13406106089032918,U
mnist/random/ts1@lr0.5,mnist,random,,1,softmax,uniform,0.101071,0.2,0.5,5,5,0,76,24,24,0.818182,0.878788,0.889288,0.979798,0,0,0.000000,0.048115,36.156366,39.238838,0.800793,0.737885,1.437489,3217,4,feasible,0.9991184792416892,0.18498222748815166,U
mnist/random/ts2@lr0.5,mnist,random,,2,softmax,uniform,0.094286,0.15,0.5,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.633039,4241,4,family-wide failure certified,0.009190952476743789,0.1631690639000236,F
tabular-MiniBooNE/eps_greedy_eps0.25/ts0@lr0.5,tabular-MiniBooNE,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.084374,0.15,0.5,5,1,0,100,0,0,0.717172,0.727273,0.726566,0.737374,0,0,0.000000,0.036995,21.015571,21.015571,0.061618,0.061618,1.000000,46823,1,feasible,1.0,0.08335647011084296,--
tabular-MiniBooNE/eps_greedy_eps0.5/ts0@lr0.5,tabular-MiniBooNE,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.084374,0.15,0.5,5,1,0,100,0,0,0.747475,0.747475,0.747677,0.757576,0,0,0.000000,0.036995,29.929711,29.929711,0.087754,0.087754,1.000000,46823,1,feasible,1.0,0.08339918416162997,--
tabular-MiniBooNE/greedy_entropy/ts0[margin]@lr0.5,tabular-MiniBooNE,greedy_entropy,,0,margin,inverse_info,0.084374,0.15,0.5,5,4,0,0,100,100,,,,,0,0,,,,341.063216,1.000000,,20.020129,9447,4,family-wide failure certified,0.0016115171356150294,0.15925785687239682,F
tabular-MiniBooNE/greedy_entropy/ts0@lr0.5,tabular-MiniBooNE,greedy_entropy,,0,softmax,inverse_info,0.084374,0.15,0.5,5,1,1,100,0,0,0.717172,0.717172,0.717172,0.717172,0,0,0.000000,0.036995,17.036015,17.036015,0.049950,0.049950,1.000000,46823,1,feasible,1.0,0.08339918416162997,--
tabular-MiniBooNE/greedy_entropy/ts1@lr0.5,tabular-MiniBooNE,greedy_entropy,,1,softmax,inverse_info,0.088603,0.15,0.5,5,1,0,100,0,0,0.747475,0.757576,0.754444,0.757576,0,0,0.000000,0.036995,11.670197,11.670197,0.034095,0.034095,1.000000,46823,1,feasible,1.0,0.08474467676142067,--
tabular-MiniBooNE/greedy_entropy/ts2@lr0.5,tabular-MiniBooNE,greedy_entropy,,2,softmax,inverse_info,0.093792,0.15,0.5,5,1,0,100,0,0,0.737374,0.737374,0.737374,0.737374,0,0,0.000000,0.036995,18.744711,18.744711,0.054852,0.054852,1.000000,46823,1,feasible,1.0,0.0890160818401213,--
tabular-MiniBooNE/random/ts0@lr0.5,tabular-MiniBooNE,random,,0,softmax,inverse_info,0.084374,0.15,0.5,5,1,0,100,0,0,0.787879,0.787879,0.790202,0.797980,0,0,0.000000,0.036995,56.526586,56.526586,0.165736,0.165736,1.000000,46823,1,feasible,1.0,0.08339918416162997,--
tabular-MiniBooNE/random/ts1@lr0.5,tabular-MiniBooNE,random,,1,softmax,inverse_info,0.088603,0.15,0.5,5,1,0,100,0,0,0.777778,0.777778,0.781515,0.787879,0,0,0.000000,0.036995,55.623305,55.623305,0.162507,0.162507,1.000000,46823,1,feasible,1.0,0.08476603378681417,--
tabular-MiniBooNE/random/ts2@lr0.5,tabular-MiniBooNE,random,,2,softmax,inverse_info,0.093792,0.15,0.5,5,1,0,100,0,0,0.797980,0.808081,0.804040,0.808081,0,0,0.000000,0.036995,60.349185,60.349185,0.176598,0.176598,1.000000,46823,1,feasible,1.0,0.0890160818401213,--
tabular-adult/eps_greedy_eps0.25/ts0@lr0.5,tabular-adult,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.14649,0.2,0.5,5,1,0,100,0,0,0.777778,0.777778,0.777778,0.777778,0,0,0.000000,0.036995,32.422630,32.422630,0.340295,0.340295,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/eps_greedy_eps0.5/ts0@lr0.5,tabular-adult,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.14649,0.2,0.5,5,1,0,100,0,0,0.777778,0.777778,0.777778,0.777778,0,0,0.000000,0.036995,30.624661,30.624661,0.321424,0.321424,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/greedy_entropy/ts0[margin]@lr0.5,tabular-adult,greedy_entropy,,0,margin,inverse_info,0.14649,0.2,0.5,5,1,0,100,0,0,0.545455,0.545455,0.545455,0.545455,0,0,0.000000,0.036995,33.835218,33.835218,0.355121,0.355121,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/greedy_entropy/ts0@lr0.5,tabular-adult,greedy_entropy,,0,softmax,inverse_info,0.14649,0.2,0.5,5,1,1,100,0,0,0.777778,0.777778,0.777778,0.777778,0,0,0.000000,0.036995,34.415869,34.415869,0.361215,0.361215,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/greedy_entropy/ts1@lr0.5,tabular-adult,greedy_entropy,,1,softmax,inverse_info,0.161415,0.25,0.5,5,1,0,100,0,0,0.757576,0.757576,0.757576,0.757576,0,0,0.000000,0.036995,29.184626,29.184626,0.309764,0.309764,1.000000,16280,1,feasible,1.0,0.15245700245700244,--
tabular-adult/greedy_entropy/ts2@lr0.5,tabular-adult,greedy_entropy,,2,softmax,inverse_info,0.145384,0.2,0.5,5,1,0,100,0,0,0.737374,0.742424,0.742424,0.747475,0,0,0.000000,0.036995,19.561148,19.561148,0.209375,0.209375,1.000000,16280,1,feasible,1.0,0.14686732186732188,--
tabular-adult/random/ts0@lr0.5,tabular-adult,random,,0,softmax,inverse_info,0.14649,0.2,0.5,5,1,0,100,0,0,0.777778,0.777778,0.777778,0.777778,0,0,0.000000,0.036995,26.418922,26.418922,0.277283,0.277283,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/random/ts1@lr0.5,tabular-adult,random,,1,softmax,inverse_info,0.161415,0.25,0.5,5,1,0,100,0,0,0.757576,0.757576,0.757576,0.757576,0,0,0.000000,0.036995,18.894207,18.894207,0.200542,0.200542,1.000000,16280,1,feasible,1.0,0.15245700245700244,--
tabular-adult/random/ts2@lr0.5,tabular-adult,random,,2,softmax,inverse_info,0.145384,0.2,0.5,5,1,0,100,0,0,0.737374,0.737374,0.738384,0.757576,0,0,0.000000,0.036995,21.572801,21.572801,0.230907,0.230907,1.000000,16280,1,feasible,1.0,0.14686732186732188,--
tabular-spambase/eps_greedy_eps0.25/ts0@lr0.5,tabular-spambase,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.054348,0.15,0.5,5,1,0,100,0,0,0.676768,0.717172,0.720303,0.777778,0,0,0.000000,0.036995,45.326063,45.326063,0.109542,0.109542,1.000000,1656,1,feasible,1.0,0.059178743961352656,--
tabular-spambase/eps_greedy_eps0.5/ts0@lr0.5,tabular-spambase,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.054348,0.15,0.5,5,1,0,100,0,0,0.696970,0.727273,0.727374,0.757576,0,0,0.000000,0.036995,49.412006,49.412006,0.119417,0.119417,1.000000,1656,1,feasible,1.0,0.06038647342995169,--
tabular-spambase/greedy_entropy/ts0@lr0.5,tabular-spambase,greedy_entropy,,0,softmax,inverse_info,0.054348,0.15,0.5,5,1,1,100,0,0,0.646465,0.727273,0.710202,0.777778,0,0,0.000000,0.036995,37.932536,37.932536,0.091674,0.091674,1.000000,1656,1,feasible,1.0,0.059178743961352656,--
tabular-spambase/greedy_entropy/ts1@lr0.5,tabular-spambase,greedy_entropy,,1,softmax,inverse_info,0.070652,0.15,0.5,5,1,0,100,0,0,0.707071,0.787879,0.779899,0.818182,0,0,0.000000,0.036995,73.882612,73.882612,0.173674,0.173674,1.000000,1656,1,feasible,1.0,0.059178743961352656,--
tabular-spambase/greedy_entropy/ts2@lr0.5,tabular-spambase,greedy_entropy,,2,softmax,inverse_info,0.065217,0.15,0.5,5,1,0,100,0,0,0.797980,0.858586,0.859192,0.898990,0,0,0.000000,0.036995,69.656173,69.656173,0.170693,0.170693,1.000000,1656,1,feasible,1.0,0.059782608695652176,--
tabular-spambase/random/ts0@lr0.5,tabular-spambase,random,,0,softmax,inverse_info,0.054348,0.15,0.5,5,1,0,100,0,0,0.767677,0.787879,0.791212,0.828283,0,0,0.000000,0.036995,86.107802,86.107802,0.208102,0.208102,1.000000,1656,1,feasible,1.0,0.059782608695652176,--
tabular-spambase/random/ts1@lr0.5,tabular-spambase,random,,1,softmax,inverse_info,0.070652,0.15,0.5,5,1,0,100,0,0,0.747475,0.777778,0.779596,0.818182,0,0,0.000000,0.036995,86.321569,86.321569,0.202913,0.202913,1.000000,1656,1,feasible,1.0,0.06219806763285024,--
tabular-spambase/random/ts2@lr0.5,tabular-spambase,random,,2,softmax,inverse_info,0.065217,0.15,0.5,5,1,0,100,0,0,0.787879,0.808081,0.813030,0.848485,0,0,0.000000,0.036995,85.741144,85.741144,0.210110,0.210110,1.000000,1656,1,feasible,1.0,0.06038647342995169,--
mnist/eps_greedy_eps0.25/ts0@lr0.7,mnist,eps_greedy_eps0.25,0.25,0,softmax,uniform,0.077857,0.15,0.7,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,2.197869,4119,4,family-wide failure certified,0.013519104317792867,0.1608920014743826,F
mnist/eps_greedy_eps0.5/ts0@lr0.7,mnist,eps_greedy_eps0.5,0.5,0,softmax,uniform,0.077857,0.15,0.7,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,2.265765,4288,4,family-wide failure certified,6.2639471262963e-07,0.17502986857825567,F
mnist/greedy_entropy/ts0[margin]@lr0.7,mnist,greedy_entropy,,0,margin,uniform,0.077857,0.15,0.7,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.965112,4504,4,family-wide failure certified,6.096586693335673e-05,0.16942307692307693,F
mnist/greedy_entropy/ts0@lr0.7,mnist,greedy_entropy,,0,softmax,uniform,0.077857,0.15,0.7,5,5,1,8,92,92,0.898990,0.919192,0.921717,0.939394,0,0,0.000000,0.324416,32.109936,47.648795,0.972424,0.655305,1.917061,4076,4,feasible,0.8568577366473663,0.1449032738095238,U
mnist/greedy_entropy/ts1@lr0.7,mnist,greedy_entropy,,1,softmax,uniform,0.101071,0.2,0.7,5,5,0,4,96,96,0.979798,0.984848,0.984848,0.989899,0,0,0.000000,0.489900,45.952659,48.878106,0.997512,0.937809,1.886881,3515,4,feasible,0.8332802043705964,0.19559706470980653,U
mnist/greedy_entropy/ts2@lr0.7,mnist,greedy_entropy,,2,softmax,uniform,0.094286,0.15,0.7,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.353857,3022,4,family-wide failure certified,0.00603719623763175,0.16222542311847318,F
mnist/random/ts0@lr0.7,mnist,random,,0,softmax,uniform,0.077857,0.15,0.7,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.891512,4212,4,family-wide failure certified,4.85150007777177e-25,0.2015982564475118,F
mnist/random/ts1@lr0.7,mnist,random,,1,softmax,uniform,0.101071,0.2,0.7,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.795082,3614,4,family-wide failure certified,9.290848309103202e-05,0.21786855634292066,F
mnist/random/ts2@lr0.7,mnist,random,,2,softmax,uniform,0.094286,0.15,0.7,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.633039,4527,4,family-wide failure certified,6.0162652955265496e-40,0.22308188265635073,F
tabular-MiniBooNE/eps_greedy_eps0.25/ts0@lr0.7,tabular-MiniBooNE,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.084374,0.15,0.7,5,1,0,100,0,0,0.717172,0.727273,0.726566,0.737374,0,0,0.000000,0.036995,21.015571,21.015571,0.061618,0.061618,1.000000,46823,1,feasible,1.0,0.08335647011084296,--
tabular-MiniBooNE/eps_greedy_eps0.5/ts0@lr0.7,tabular-MiniBooNE,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.084374,0.15,0.7,5,1,0,100,0,0,0.747475,0.747475,0.747677,0.757576,0,0,0.000000,0.036995,29.929711,29.929711,0.087754,0.087754,1.000000,46823,1,feasible,1.0,0.08339918416162997,--
tabular-MiniBooNE/greedy_entropy/ts0[margin]@lr0.7,tabular-MiniBooNE,greedy_entropy,,0,margin,inverse_info,0.084374,0.15,0.7,5,5,0,0,100,100,,,,,0,0,,,,341.063216,1.000000,,20.020129,1731,4,family-wide failure certified,4.9481989077821194e-42,0.19923481587757055,F
tabular-MiniBooNE/greedy_entropy/ts0@lr0.7,tabular-MiniBooNE,greedy_entropy,,0,softmax,inverse_info,0.084374,0.15,0.7,5,1,1,100,0,0,0.717172,0.717172,0.717172,0.717172,0,0,0.000000,0.036995,17.036015,17.036015,0.049950,0.049950,1.000000,46823,1,feasible,1.0,0.08339918416162997,--
tabular-MiniBooNE/greedy_entropy/ts1@lr0.7,tabular-MiniBooNE,greedy_entropy,,1,softmax,inverse_info,0.088603,0.15,0.7,5,1,0,100,0,0,0.747475,0.757576,0.754444,0.757576,0,0,0.000000,0.036995,11.670197,11.670197,0.034095,0.034095,1.000000,46823,1,feasible,1.0,0.08474467676142067,--
tabular-MiniBooNE/greedy_entropy/ts2@lr0.7,tabular-MiniBooNE,greedy_entropy,,2,softmax,inverse_info,0.093792,0.15,0.7,5,1,0,100,0,0,0.737374,0.737374,0.737374,0.737374,0,0,0.000000,0.036995,18.744711,18.744711,0.054852,0.054852,1.000000,46823,1,feasible,1.0,0.0890160818401213,--
tabular-MiniBooNE/random/ts0@lr0.7,tabular-MiniBooNE,random,,0,softmax,inverse_info,0.084374,0.15,0.7,5,1,0,100,0,0,0.787879,0.787879,0.790202,0.797980,0,0,0.000000,0.036995,56.526586,56.526586,0.165736,0.165736,1.000000,46823,1,feasible,1.0,0.08339918416162997,--
tabular-MiniBooNE/random/ts1@lr0.7,tabular-MiniBooNE,random,,1,softmax,inverse_info,0.088603,0.15,0.7,5,1,0,100,0,0,0.777778,0.777778,0.781515,0.787879,0,0,0.000000,0.036995,55.623305,55.623305,0.162507,0.162507,1.000000,46823,1,feasible,1.0,0.08476603378681417,--
tabular-MiniBooNE/random/ts2@lr0.7,tabular-MiniBooNE,random,,2,softmax,inverse_info,0.093792,0.15,0.7,5,1,0,100,0,0,0.797980,0.808081,0.804040,0.808081,0,0,0.000000,0.036995,60.349185,60.349185,0.176598,0.176598,1.000000,46823,1,feasible,1.0,0.0890160818401213,--
tabular-adult/eps_greedy_eps0.25/ts0@lr0.7,tabular-adult,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.14649,0.2,0.7,5,1,0,100,0,0,0.777778,0.777778,0.777778,0.777778,0,0,0.000000,0.036995,32.422630,32.422630,0.340295,0.340295,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/eps_greedy_eps0.5/ts0@lr0.7,tabular-adult,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.14649,0.2,0.7,5,1,0,100,0,0,0.777778,0.777778,0.777778,0.777778,0,0,0.000000,0.036995,30.624661,30.624661,0.321424,0.321424,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/greedy_entropy/ts0[margin]@lr0.7,tabular-adult,greedy_entropy,,0,margin,inverse_info,0.14649,0.2,0.7,5,3,0,0,100,100,,,,,0,0,,,,95.277963,1.000000,,2.815941,962,3,family-wide failure certified,7.103943893294697e-111,0.3258741258741259,F
tabular-adult/greedy_entropy/ts0@lr0.7,tabular-adult,greedy_entropy,,0,softmax,inverse_info,0.14649,0.2,0.7,5,1,1,100,0,0,0.777778,0.777778,0.777778,0.777778,0,0,0.000000,0.036995,34.415869,34.415869,0.361215,0.361215,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/greedy_entropy/ts1@lr0.7,tabular-adult,greedy_entropy,,1,softmax,inverse_info,0.161415,0.25,0.7,5,1,0,100,0,0,0.757576,0.757576,0.757576,0.757576,0,0,0.000000,0.036995,29.184626,29.184626,0.309764,0.309764,1.000000,16280,1,feasible,1.0,0.15245700245700244,--
tabular-adult/greedy_entropy/ts2@lr0.7,tabular-adult,greedy_entropy,,2,softmax,inverse_info,0.145384,0.2,0.7,5,1,0,100,0,0,0.737374,0.742424,0.742424,0.747475,0,0,0.000000,0.036995,19.561148,19.561148,0.209375,0.209375,1.000000,16280,1,feasible,1.0,0.14686732186732188,--
tabular-adult/random/ts0@lr0.7,tabular-adult,random,,0,softmax,inverse_info,0.14649,0.2,0.7,5,1,0,100,0,0,0.777778,0.777778,0.777778,0.777778,0,0,0.000000,0.036995,26.418922,26.418922,0.277283,0.277283,1.000000,16280,1,feasible,1.0,0.1507985257985258,--
tabular-adult/random/ts1@lr0.7,tabular-adult,random,,1,softmax,inverse_info,0.161415,0.25,0.7,5,1,0,100,0,0,0.757576,0.757576,0.757576,0.757576,0,0,0.000000,0.036995,18.894207,18.894207,0.200542,0.200542,1.000000,16280,1,feasible,1.0,0.15245700245700244,--
tabular-adult/random/ts2@lr0.7,tabular-adult,random,,2,softmax,inverse_info,0.145384,0.2,0.7,5,1,0,100,0,0,0.737374,0.737374,0.738384,0.757576,0,0,0.000000,0.036995,21.572801,21.572801,0.230907,0.230907,1.000000,16280,1,feasible,1.0,0.14686732186732188,--
tabular-spambase/eps_greedy_eps0.25/ts0@lr0.7,tabular-spambase,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.054348,0.15,0.7,5,5,0,28,72,72,0.878788,0.929293,0.922078,0.979798,0,0,0.000000,0.120647,136.293362,336.081332,0.812229,0.329389,7.414748,209,4,feasible,0.993729800424387,0.10655737704918032,U
tabular-spambase/eps_greedy_eps0.5/ts0@lr0.7,tabular-spambase,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.054348,0.15,0.7,5,5,0,19,81,81,0.808081,0.909091,0.901648,0.989899,0,0,0.000000,0.168184,136.489461,361.092087,0.872674,0.329863,7.307780,201,4,feasible,0.974927703020724,0.11258278145695365,U
tabular-spambase/greedy_entropy/ts0@lr0.7,tabular-spambase,greedy_entropy,,0,softmax,inverse_info,0.054348,0.15,0.7,5,4,1,20,80,80,0.888889,0.969697,0.952020,1.000000,0,0,0.000000,0.161130,208.609528,372.743229,0.900832,0.504160,9.826478,278,4,feasible,0.9695492825562712,0.11627906976744186,U
tabular-spambase/greedy_entropy/ts1@lr0.7,tabular-spambase,greedy_entropy,,1,softmax,inverse_info,0.070652,0.15,0.7,5,5,0,3,97,97,0.929293,0.929293,0.949495,0.989899,0,0,0.000000,0.561506,175.186903,417.904088,0.982354,0.411806,5.656325,133,4,feasible,0.8382300188042027,0.1323529411764706,U
tabular-spambase/greedy_entropy/ts2@lr0.7,tabular-spambase,greedy_entropy,,2,softmax,inverse_info,0.065217,0.15,0.7,5,4,0,38,62,62,0.969697,0.979798,0.980064,0.989899,0,0,0.000000,0.091813,177.261023,320.367722,0.785064,0.434380,4.599273,213,4,feasible,0.9933380939713045,0.10922330097087378,U
tabular-spambase/random/ts0@lr0.7,tabular-spambase,random,,0,softmax,inverse_info,0.054348,0.15,0.7,5,5,0,99,1,1,0.828283,0.888889,0.895215,0.979798,0,0,0.000000,0.037355,161.015919,163.543526,0.395246,0.389137,1.899288,235,4,feasible,0.999999825714009,0.07484407484407485,U
tabular-spambase/random/ts1@lr0.7,tabular-spambase,random,,1,softmax,inverse_info,0.070652,0.15,0.7,5,5,0,59,41,41,0.818182,0.898990,0.908235,1.000000,0,0,0.000000,0.061131,200.925113,292.964247,0.688662,0.472308,3.393871,220,4,feasible,0.9999946806660378,0.08163265306122448,U
tabular-spambase/random/ts2@lr0.7,tabular-spambase,random,,2,softmax,inverse_info,0.065217,0.15,0.7,5,5,0,23,77,77,0.909091,0.959596,0.955204,1.000000,0,0,0.000000,0.143121,219.847433,364.785185,0.893910,0.538738,4.254494,261,4,feasible,0.9913057409199778,0.10437710437710437,U
mnist/eps_greedy_eps0.25/ts0@lr0.9,mnist,eps_greedy_eps0.25,0.25,0,softmax,uniform,0.077857,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,2.197869,3934,4,family-wide failure certified,4.1010577267893574e-91,0.25320456540825287,F
mnist/eps_greedy_eps0.5/ts0@lr0.9,mnist,eps_greedy_eps0.5,0.5,0,softmax,uniform,0.077857,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,2.265765,4174,4,family-wide failure certified,4.416502717776924e-114,0.26335052403926135,F
mnist/greedy_entropy/ts0[margin]@lr0.9,mnist,greedy_entropy,,0,margin,uniform,0.077857,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.965112,1423,4,family-wide failure certified,4.090423477224783e-36,0.2010843373493976,F
mnist/greedy_entropy/ts0@lr0.9,mnist,greedy_entropy,,0,softmax,uniform,0.077857,0.15,0.9,5,5,1,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.971424,4173,4,family-wide failure certified,1.36921550028183e-79,0.24785544807446613,F
mnist/greedy_entropy/ts1@lr0.9,mnist,greedy_entropy,,1,softmax,uniform,0.101071,0.2,0.9,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.891586,3301,4,family-wide failure certified,1.0328930164305264e-44,0.26570915619389585,F
mnist/greedy_entropy/ts2@lr0.9,mnist,greedy_entropy,,2,softmax,uniform,0.094286,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.353857,3888,4,family-wide failure certified,1.785787832286744e-106,0.268053148469093,F
mnist/random/ts0@lr0.9,mnist,random,,0,softmax,uniform,0.077857,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.891512,3333,4,family-wide failure certified,3.509508216929623e-115,0.2544529262086514,F
mnist/random/ts1@lr0.9,mnist,random,,1,softmax,uniform,0.101071,0.2,0.9,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.795082,3439,4,family-wide failure certified,2.8408643411137154e-52,0.2650769888793841,F
mnist/random/ts2@lr0.9,mnist,random,,2,softmax,uniform,0.094286,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,49.000000,1.000000,,1.633039,2713,4,family-wide failure certified,4.783899454955771e-165,0.27489385015751266,F
tabular-MiniBooNE/eps_greedy_eps0.25/ts0@lr0.9,tabular-MiniBooNE,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.084374,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,341.063216,1.000000,,16.229072,8226,4,family-wide failure certified,6.506685968034752e-98,0.23214854111405836,F
tabular-MiniBooNE/eps_greedy_eps0.5/ts0@lr0.9,tabular-MiniBooNE,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.084374,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,341.063216,1.000000,,11.395473,8124,4,family-wide failure certified,4.6454564250086713e-97,0.23313622426631625,F
tabular-MiniBooNE/greedy_entropy/ts0[margin]@lr0.9,tabular-MiniBooNE,greedy_entropy,,0,margin,inverse_info,0.084374,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,341.063216,1.000000,,20.020129,6252,4,family-wide failure certified,6.9784677229539e-145,0.2382115807476179,F
tabular-MiniBooNE/greedy_entropy/ts0@lr0.9,tabular-MiniBooNE,greedy_entropy,,0,softmax,inverse_info,0.084374,0.15,0.9,5,5,1,0,100,100,,,,,0,0,,,,341.063216,1.000000,,20.020129,7345,4,family-wide failure certified,3.178314386914752e-98,0.23344226579520697,F
tabular-MiniBooNE/greedy_entropy/ts1@lr0.9,tabular-MiniBooNE,greedy_entropy,,1,softmax,inverse_info,0.088603,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,342.282095,1.000000,,29.329590,1184,4,family-wide failure certified,1.1223982692930185e-77,0.2226483434537126,F
tabular-MiniBooNE/greedy_entropy/ts2@lr0.9,tabular-MiniBooNE,greedy_entropy,,2,softmax,inverse_info,0.093792,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,341.732195,1.000000,,18.230860,2458,4,family-wide failure certified,7.94628417465382e-138,0.24847143158338605,F
tabular-MiniBooNE/random/ts0@lr0.9,tabular-MiniBooNE,random,,0,softmax,inverse_info,0.084374,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,341.063216,1.000000,,6.033678,6014,4,family-wide failure certified,5.106516850259887e-83,0.22514588859416446,F
tabular-MiniBooNE/random/ts1@lr0.9,tabular-MiniBooNE,random,,1,softmax,inverse_info,0.088603,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,342.282095,1.000000,,6.153573,7976,4,family-wide failure certified,1.149609957686184e-130,0.2474620674598843,F
tabular-MiniBooNE/random/ts2@lr0.9,tabular-MiniBooNE,random,,2,softmax,inverse_info,0.093792,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,341.732195,1.000000,,5.662582,8055,4,family-wide failure certified,3.2251513504454566e-105,0.23536895674300254,F
tabular-adult/eps_greedy_eps0.25/ts0@lr0.9,tabular-adult,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.14649,0.2,0.9,5,3,0,0,100,100,,,,,0,0,,,,95.277963,1.000000,,2.938625,333,3,family-wide failure certified,1.8310261821850253e-91,0.30825746685832933,F
tabular-adult/eps_greedy_eps0.5/ts0@lr0.9,tabular-adult,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.14649,0.2,0.9,5,4,0,0,100,100,,,,,0,0,,,,95.277963,1.000000,,3.111152,238,4,family-wide failure certified,1.3254252359915536e-90,0.3082004188819075,F
tabular-adult/greedy_entropy/ts0[margin]@lr0.9,tabular-adult,greedy_entropy,,0,margin,inverse_info,0.14649,0.2,0.9,5,4,0,0,100,100,,,,,0,0,,,,95.277963,1.000000,,2.815941,2281,3,family-wide failure certified,1.353967685314748e-62,0.2775978071268378,F
tabular-adult/greedy_entropy/ts0@lr0.9,tabular-adult,greedy_entropy,,0,softmax,inverse_info,0.14649,0.2,0.9,5,3,1,0,100,100,,,,,0,0,,,,95.277963,1.000000,,2.768431,299,3,family-wide failure certified,8.733138398189605e-93,0.3090299936183791,F
tabular-adult/greedy_entropy/ts1@lr0.9,tabular-adult,greedy_entropy,,1,softmax,inverse_info,0.161415,0.25,0.9,5,4,0,0,100,100,,,,,0,0,,,,94.215528,1.000000,,3.228259,383,4,family-wide failure certified,1.6561067462188007e-30,0.31545741324921134,F
tabular-adult/greedy_entropy/ts2@lr0.9,tabular-adult,greedy_entropy,,2,softmax,inverse_info,0.145384,0.2,0.9,5,4,0,0,100,100,,,,,0,0,,,,93.426563,1.000000,,4.776129,1620,3,family-wide failure certified,2.5750993344329564e-71,0.3017209813255218,F
tabular-adult/random/ts0@lr0.9,tabular-adult,random,,0,softmax,inverse_info,0.14649,0.2,0.9,5,5,0,0,100,100,,,,,0,0,,,,95.277963,1.000000,,3.606429,493,4,family-wide failure certified,1.3648917067129054e-88,0.3084050297816016,F
tabular-adult/random/ts1@lr0.9,tabular-adult,random,,1,softmax,inverse_info,0.161415,0.25,0.9,5,5,0,0,100,100,,,,,0,0,,,,94.215528,1.000000,,4.986477,618,4,family-wide failure certified,9.508063491612882e-29,0.31373866308364123,F
tabular-adult/random/ts2@lr0.9,tabular-adult,random,,2,softmax,inverse_info,0.145384,0.2,0.9,5,5,0,0,100,100,,,,,0,0,,,,93.426563,1.000000,,4.330757,612,4,family-wide failure certified,1.4151052357275279e-86,0.30655737704918035,F
tabular-spambase/eps_greedy_eps0.25/ts0@lr0.9,tabular-spambase,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.054348,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,413.776654,1.000000,,9.128890,289,4,family-wide failure certified,0.024592178429562198,0.19281045751633988,F
tabular-spambase/eps_greedy_eps0.5/ts0@lr0.9,tabular-spambase,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.054348,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,413.776654,1.000000,,8.374010,241,4,unresolved,0.09951699064714752,0.17630057803468208,U
tabular-spambase/greedy_entropy/ts0@lr0.9,tabular-spambase,greedy_entropy,,0,softmax,inverse_info,0.054348,0.15,0.9,5,5,1,0,100,100,,,,,0,0,,,,413.776654,1.000000,,10.908225,249,4,unresolved,0.17935656493362384,0.17269076305220885,U
tabular-spambase/greedy_entropy/ts1@lr0.9,tabular-spambase,greedy_entropy,,1,softmax,inverse_info,0.070652,0.15,0.9,5,5,0,1,99,99,0.929293,0.929293,0.929293,0.929293,1,1,1.000000,1.000000,148.739567,422.644093,0.993496,0.349637,5.720481,203,4,unresolved,0.18056208481261887,0.1675,U
tabular-spambase/greedy_entropy/ts2@lr0.9,tabular-spambase,greedy_entropy,,2,softmax,inverse_info,0.065217,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,408.078280,1.000000,,5.858465,233,4,unresolved,0.37804484811612166,0.15755627009646303,U
tabular-spambase/random/ts0@lr0.9,tabular-spambase,random,,0,softmax,inverse_info,0.054348,0.15,0.9,5,5,0,2,98,98,0.898990,0.924242,0.924242,0.949495,0,0,0.000000,0.657628,189.783794,409.296797,0.989173,0.458662,4.753307,266,4,feasible,0.7432690124318755,0.1388101983002833,U
tabular-spambase/random/ts1@lr0.9,tabular-spambase,random,,1,softmax,inverse_info,0.070652,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,425.410805,1.000000,,4.928210,268,4,family-wide failure certified,0.026096612619321703,0.19218241042345277,F
tabular-spambase/random/ts2@lr0.9,tabular-spambase,random,,2,softmax,inverse_info,0.065217,0.15,0.9,5,5,0,0,100,100,,,,,0,0,,,,408.078280,1.000000,,4.759422,273,4,unresolved,0.10174665781083211,0.17921146953405018,U
```

### 3.3 Simultaneous-risk evaluation (exact event)

From `iut_by_lambda_ref.py` lines 124-127: for a CERTIFIED resplit with
selected index i,

```
fail = any( mean loss over pool rows of stratum k at index i  >  alpha
            for k in labels )
```

- The event is exactly `exists k in K_eval: R_hat_k(lambda_hat) > alpha`
  with strict `>`, no tolerance, evaluated on the **full evaluation pool**.
- **Evaluated stratum domain: all nonempty pool strata** of that
  configuration's lambda_ref bucketization (`labels = np.unique(bucket)` on
  the pool) -- NOT the per-resplit calibration span and NOT the nominal 5.
  This domain is in general a superset of the certified calibration span, so
  the check is conservative relative to the certificate's own scope.
- Refused resplits contribute `fail = 0` and are excluded from the
  conditional denominator; the unconditional rate uses denominator 100, the
  conditional rate uses denominator n_certified (Wilson interval per
  configuration; omitted when n_certified = 0).
- Maximum observed excess above alpha: the single violation's stratum risk
  0.1675 vs alpha 0.15 -> **excess 0.0175** (Section 6).
- This is the CURRENT full-pool estimand. The `realized_risk` stored for
  `cafa_iut` in the metrics JSONs is the superseded complementary-test-half
  AGGREGATE risk (not per-stratum) -- do not mix it into S7; the h2_table
  `cafa_iut` violation column is likewise superseded.

### 3.4 Acquisition cost

- Selected-rule cost per certified resplit: `costs_full[:, i].mean()` = mean
  over ALL pool rows of the cumulative acquired cost at the stop index
  induced by lambda_hat_i, primary scheme -- **full-pool convention**.
- Refused resplit: full-acquisition cost `full_c = cc[:, T].mean()` (pool).
- Stored per configuration: `mean_certified_cost` (certified runs only;
  empty when none), `mean_deployed_cost` (all 100 runs, fallback included),
  `deployed_cost_over_full`, `premium_vs_marginal` (deployed IUT cost /
  deployed marginal cost, same resplits, same convention).
- Medians and p5/p95: NOT FOUND (not stored; see Section 3 header).
- Oracle comparison for CAFA-IUT: **NOT FOUND** -- no oracle is defined or
  evaluated against the IUT in any canonical artifact; the only stored
  comparison is `premium_vs_marginal`.

---

## 4. Aggregate certification and refusal checks

Recomputed from the exact 10,500 per-resplit rows:

1. Configurations certifying in >= 1 resplit: **61**.
2. Configurations refusing in >= 1 resplit: **60**.
3. Configurations that both certify and refuse (mixed): **16**
   (61 + 60 - 105 = 16; the 16 configs with 0 < certified < 100 are listed
   with exact counts in the CSV: mnist margin ts0@0.5 (45), mnist greedy
   ts2@0.5 (90), mnist random ts0@0.5 (77), mnist random ts1@0.5 (76),
   mnist greedy ts0@0.7 (8), mnist greedy ts1@0.7 (4), spambase eps0.25@0.7
   (28), eps0.5@0.7 (19), greedy ts0@0.7 (20), greedy ts1@0.7 (3), greedy
   ts2@0.7 (38), random ts0@0.7 (99), random ts1@0.7 (59), random ts2@0.7
   (23), spambase greedy ts1@0.9 (1), spambase random ts0@0.9 (2)).
4. Certifying in all 100 resplits: **45**.
5. Refusing in all 100 resplits: **44**.
6. Never certifying: **44** (same 44).
7. Total certified runs / 10,500: **5,092**.
8. Total refused runs / 10,500: **5,408** (5,092 + 5,408 = 10,500).
9. Certification-rate range: **0.00 to 1.00**.
10. Refusal-rate range: **0.00 to 1.00**.
11. Dataset level (n = 27, 27, 27, 24): MNIST ever-cert 10, full-cert 4,
    full-refuse 17, certified runs 700; Adult 17 / 17 / 10 / 1,700;
    MiniBooNE 16 / 16 / 11 / 1,600; Spambase 18 / 8 / 6 / 1,092.
12. lambda_ref level (n = 35 each): lr 0.5 ever-cert 33, full-cert 29,
    full-refuse 2, certified runs 3,188; lr 0.7: 26 / 16 / 9 / 1,901;
    lr 0.9: **2 / 0 / 33 / 3**.
13. Policy level: greedy_entropy (45 configs) ever-cert 26, certified runs
    2,009; random (36) 21 / 1,836; eps-greedy 0.25 (12) 7 / 628; eps-greedy
    0.5 (12) 7 / 619.
14. Backbone-seed level: ts0 (57 configs) ever-cert 32, certified runs
    2,698; ts1 (24) 16 / 1,243; ts2 (24) 13 / 1,151.
15. Readiness-score level: softmax (96 configs) ever-cert 59, certified runs
    4,947; margin (9) ever-cert 2 (mnist margin@0.5 with 45, adult
    margin@0.5 with 100), certified runs 145.

**Headline verification: 61/105 ever-certify -- CONFIRMED. 60/105
ever-refuse -- CONFIRMED. Overlap allowed and equal to exactly 16
configurations.**

---

## 5. Refusal diagnosis

### 5.1 Diagnostic source and timing

- The family-wide audit (`family_wide_feasibility.py`, Task 1) is computed
  **once per frozen configuration** (cell x lambda_ref) -- never per resplit.
- It **depends on lambda_ref** (the bucketization and therefore the audited
  stratum change with lambda_ref); `family_wide_summary.csv` has one row per
  configuration.
- Audited stratum: the **deepest precommitted nonempty pool bucket**
  (`stratum_rule = "deepest precommitted nonempty"`; label-free choice).
- It uses the **full post-probe pool** with labels: exact one-sided binomial
  upper-tail p-values per threshold, intersection-union over all 100
  thresholds (and separately all forced depths), gamma = 0.05.
- The labels are the SAME pool labels used by the conditional full-pool
  check -- the diagnosis is a descriptive audit of the frozen configuration,
  not an independently-sampled test; it is not part of the deployed
  certificate.
- Verdict is three-way: `feasible` (empirical family minimum below alpha),
  `family-wide failure certified` (IU test rejects at gamma), `unresolved`.

### 5.2 Exact diagnosis counts

Refusal classes are **configuration-level**: a class is assigned to every
configuration with refusal_rate > 0, from that configuration's family
verdict; when refusal occurs on only some resplits the configuration still
carries one class (the audit is resplit-independent). Among the **60
ever-refusing configurations**:

- **A -- refusal with certified family-wide failure: 40** (all 40 have
  family verdict "family-wide failure certified");
- **B -- refusal with certified endpoint failure only: 0** (the category
  exists in code; no configuration triggers it);
- **C -- refusal, unresolved: 20.**

**Verification of the expected 40 / 0 / 20 split: CONFIRMED.**

Refinement the S7 text must respect: class C means "family-wide failure NOT
certified", not "audit returned unresolved". Among the 20 C-class
configurations the family-audit verdict is **"feasible" for 15** (the
empirical family minimum is below alpha -- e.g. all 8 spambase cells at
lr 0.7, mnist greedy ts0/ts1 at lr 0.7, four mnist cells at lr 0.5, spambase
random ts0 at lr 0.9) **and "unresolved" for 5** (spambase eps0.5, greedy
ts0/ts1/ts2, random ts2, all at lr 0.9). These refusals reflect insufficient
per-stratum calibration evidence at delta = 0.1 (small strata, risks near
alpha), not certified infeasibility. The never-refusing 45 configurations
all have verdict "feasible". Family verdicts over all 105: 60 feasible, 40
failure-certified, 5 unresolved.

### 5.3 Per-configuration diagnosis table

The diagnosis fields are columns of the 105-row CSV in Section 3
(`family_verdict`, `family_p_value`, `min_threshold_risk` = empirical family
minimum on the audited stratum, `diag_code`), so no second CSV is needed.
Endpoint risk (`full_feature_risk` / `risk_at_T` per configuration) is in
`family_wide_summary.csv`; it equals `min_threshold_risk` wherever the curve
is minimized at the endpoint.

Codes: `F` = certified family-wide failure (= class A), `U` = family-wide
failure not certified (= class C; audit verdict feasible or unresolved),
`--` = no refusal in any resplit. `B`/`E` are NOT needed as separate codes in
the table: B never occurs (0/105), and "empirically feasible" is a family-
audit verdict, not a refusal class -- if the author wants it visible, split
U into U-f (15) and U-u (5) using the `family_verdict` column. With that
caveat stated in the caption, {F, U, --} is sufficient and exhaustive.

---

## 6. Conditional full-pool violations

**Exactly one conditional violation exists in all 10,500 runs.** Complete
audit of the single case:

- configuration: `tabular-spambase/greedy_entropy/ts1@lr0.9`; dataset
  Spambase, greedy entropy (no epsilon), training seed 1, max-softmax
  readiness, inverse-information cost, alpha = 0.15, lambda_ref = 0.9;
- resplit index: **79** (0-based, from the per-resplit artifact);
- selected threshold: index **92**, lambda = **0.9292929292929294**;
- status: certified (this configuration certifies in exactly **1 of 100**
  resplits -- "certified once" means precisely 1/100);
- calibration stratum span: NOT stored per resplit; the pool bucketization
  has 5 nonempty strata, labels 0-4, sizes {0: 355, 1: 357, 2: 203, 3: 341,
  4: 400} (metrics `bucket_sizes`), so the span is [0, 4] whenever all
  labels appear in the calibration half (not artifact-verifiable per
  resplit);
- evaluated strata: all 5 nonempty pool strata (labels 0-4, sizes above);
- violating stratum: the deepest stratum **k = 4** (n_4 = 400): pool risk at
  lambda = 0.9293 is **0.1675** (= 67/400 exactly; read from
  `family_wide_threshold_curves.csv` at that exact lambda -- the certified
  threshold happens to sit at the family argmin, where `min_threshold_risk`
  = 0.1675 and the binomial upper-tail p = 0.1806, matching the stored
  family p-value). Whether any OTHER stratum also exceeds alpha at that
  lambda is NOT FOUND (per-stratum curves are frozen only for the deepest
  stratum); the event is "any stratum", and stratum 4 suffices;
- target alpha = 0.15; **excess = 0.0175**;
- acquisition cost of that selection: the configuration's
  mean_certified_cost = **148.739567** raw units (with 1 certified run, the
  mean IS that resplit's cost) = **0.349637** of full acquisition
  (425.410805);
- estimand: the CURRENT full-pool estimand (pool stratum risks), not a
  test-half diagnostic;
- it is counted in both the numerator (1) and denominator (1) of that
  configuration's conditional rate: cond rate 1/1 = 1.00, stored Wilson
  interval [0.055, 1.000] (upper bound 1.0); unconditional rate 1/100 = 0.01.

**Verification of the expected statement: CONFIRMED** -- the only
conditional full-pool violation among certified selections is Spambase /
greedy entropy / seed 1 / lambda_ref 0.9; the configuration certifies once
(1/100), and that one certified selection exceeds the stratum target.

Overall accounting:

- total certified selections across all configurations: **5,092**;
- total conditional violations: **1**;
- overall conditional violation rate: **1/5,092 = 1.9639e-04** (computed
  here from the exact per-resplit artifact; not stored as a scalar);
- Wilson 95% interval (computed here, z = 1.96): **[3.47e-05, 1.11e-03]**;
- configurations with any conditional violation: **1 of 105**.

Both certified selections of spambase/random/ts0@lr0.9 (the only other
lr 0.9 certifications) have zero violations.

---

## 7. Primary CAFA-IUT results

Primary configuration per dataset = (greedy entropy, ts0, max-softmax,
primary cost scheme, lambda_ref = 0.9), 100 resplits. Exact four-row summary:

| Dataset | alpha | G realized | Cert/100 | Refuse/100 | Cond. viol. | Mean sel. lambda (cert.) | End-to-end cost/full | Family verdict | Empirical family min | Family p-value |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| MNIST | 0.15 | 5 | 0 | 100 | 0 | n/a | 1.000 | family-wide failure certified | 0.247855 | 1.369e-79 |
| Adult | 0.20 | 3 | 0 | 100 | 0 | n/a | 1.000 | family-wide failure certified | 0.309030 | 8.733e-93 |
| MiniBooNE | 0.15 | 5 | 0 | 100 | 0 | n/a | 1.000 | family-wide failure certified | 0.233442 | 3.178e-98 |
| Spambase | 0.15 | 5 | 0 | 100 | 0 | n/a | 1.000 | unresolved | 0.172691 | 1.794e-01 |

All four primary configurations refuse in 100/100 resplits at lambda_ref =
0.9 -- the outcome-A story: refusal with a certified explanation on the three
resolved datasets, refusal-unresolved on Spambase. (Cost premiums vs
marginal at these rows: 1.9714, 2.7684, 20.0201, 10.9082.)

Already in the main paper (per RESULTS_FOR_PAPER / FINAL_CLAIM_DECISION):
the 61/105 and 40/0/20 headline, "IUT cert rate @0.9 = 0.00" for the four
primary datasets, the family verdicts/p-values/minima of the four primary
rows, the single conditional violation sentence, and "premium 1.000x at
feasible configs". Supplementary-only: the full 105-row table, the per-
configuration selected-threshold and cost columns, the 16 mixed
configurations, the per-lambda_ref aggregates, and the Section 6 violation
detail.

---

## 8. End-to-end cost under refusal

**Estimand (exact, from code):** per resplit, C_deploy = C(lambda_hat) if
certified, C(T) = full-acquisition cost if refused; both are means over the
FULL EVALUATION POOL under the primary scheme (complete-pool convention, not
test-half). `mean_deployed_cost` (stored) is the average of C_deploy over the
100 resplits; `mean_certified_cost` (stored) conditions on certification;
fallback cost/full = 1.0 by definition. The refusal-weighted decomposition

    mean_deployed = (n_cert * mean_certified_cost + n_refuse * full_c) / 100

was **verified exactly for all 105 configurations** (max relative deviation
< 1e-6; full_c derived per cell as `mean_pool_cost / cost_over_full` from
pool_plugin_eval.csv). End-to-end cost is stored; the certified-only
normalization (`certonly_cost_over_full`) is derived here.

Recomputed values:

- Range across 105 configurations (end-to-end cost/full): **0.034095
  (MiniBooNE/greedy/ts1@lr0.5, cert 100/100) to 1.000000 (all 44
  full-refusal configurations sit at exactly 1.0)**.
- Four primary cells at lr 0.9: 1.000, 1.000, 1.000, 1.000 (all refuse
  100/100). At lr 0.5 the same cells cost 0.626 (MNIST), 0.361 (Adult),
  0.050 (MiniBooNE), 0.092 (Spambase) -- identical to marginal CAFA except
  MNIST (marginal 0.507; the IUT certifies a more conservative block).
- Dataset-level ranges (end-to-end): MNIST 0.503-1.000; Adult 0.201-1.000;
  MiniBooNE 0.034-1.000; Spambase 0.092-1.000.
- lambda_ref-level ranges: lr 0.5: 0.034-1.000; lr 0.7: 0.034-1.000;
  lr 0.9: **0.989-1.000** (nothing meaningfully cheaper than full
  acquisition survives at 0.9).
- Lowest end-to-end cost: MiniBooNE/greedy/ts1@lr0.5 (0.0341); highest:
  the 44 full-refusal configurations (exactly 1.0).
- High refusal -> cost -> 1: yes, mechanically; e.g. mnist/greedy/ts1@lr0.7
  (96/100 refusals, 0.9975), spambase/greedy/ts1@lr0.9 (99/100, 0.9935),
  spambase/random/ts0@lr0.9 (98/100, 0.9892).
- Certified-only cost/full over the 61 certifying configurations:
  0.034095 to 0.937809.

**"Simultaneous certification increases acquisition cost relative to
marginal CAFA": SUPPORTED WITH SCOPE.** The exact matched comparison is the
stored `premium_vs_marginal` = mean deployed IUT cost / mean deployed
marginal cost, same cell, same 100 resplits, same pool convention (the
marginal method never falls back, Section S6). Over all 105 configurations
the premium is **never below 1**: exactly 1.000000 in 41 configurations --
precisely the 41 with G_realized = 1, where the IUT degenerates to the
marginal test -- and > 1 in the other 64, ranging up to 29.33
(MiniBooNE/greedy/ts1@lr0.9, where full-acquisition fallback replaces a
3.4%-of-full marginal rule). Correct scoped sentence: "simultaneous
certification is never cheaper than marginal CAFA; it is free exactly where
the stratification is trivial (G = 1) and costs up to the full-acquisition
fallback where certification fails."

---

## 9. Candidate compact table design

### Table S6: complete 105 configurations, three 35-row panels

Recommended columns confirmed available and exact; `Cost/full` below is the
**end-to-end deployed cost including fallback** (state in caption);
`Diag` is **configuration-level** while Cert/Refuse are resplit-level counts
(state in caption). Values are table-ready:

#### Panel A: lambda_ref = 0.5
| Dataset | Policy | Seed | Score | Alpha | Cert/100 | Refuse/100 | Cond.viol | Cost/full | Diag |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| MNIST | eG(.25) | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.534 | -- |
| MNIST | eG(.5) | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.503 | -- |
| MNIST | Greedy | 0 | margin | 0.15 | 45 | 55 | 0 | 0.847 | U |
| MNIST | Greedy | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.626 | -- |
| MNIST | Greedy | 1 | softmax | 0.20 | 100 | 0 | 0 | 0.675 | -- |
| MNIST | Greedy | 2 | softmax | 0.15 | 90 | 10 | 0 | 0.878 | U |
| MNIST | Random | 0 | softmax | 0.15 | 77 | 23 | 0 | 0.755 | U |
| MNIST | Random | 1 | softmax | 0.20 | 76 | 24 | 0 | 0.801 | U |
| MNIST | Random | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| Adult | eG(.25) | 0 | softmax | 0.20 | 100 | 0 | 0 | 0.340 | -- |
| Adult | eG(.5) | 0 | softmax | 0.20 | 100 | 0 | 0 | 0.321 | -- |
| Adult | Greedy | 0 | margin | 0.20 | 100 | 0 | 0 | 0.355 | -- |
| Adult | Greedy | 0 | softmax | 0.20 | 100 | 0 | 0 | 0.361 | -- |
| Adult | Greedy | 1 | softmax | 0.25 | 100 | 0 | 0 | 0.310 | -- |
| Adult | Greedy | 2 | softmax | 0.20 | 100 | 0 | 0 | 0.209 | -- |
| Adult | Random | 0 | softmax | 0.20 | 100 | 0 | 0 | 0.277 | -- |
| Adult | Random | 1 | softmax | 0.25 | 100 | 0 | 0 | 0.201 | -- |
| Adult | Random | 2 | softmax | 0.20 | 100 | 0 | 0 | 0.231 | -- |
| MiniBooNE | eG(.25) | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.062 | -- |
| MiniBooNE | eG(.5) | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.088 | -- |
| MiniBooNE | Greedy | 0 | margin | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Greedy | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.050 | -- |
| MiniBooNE | Greedy | 1 | softmax | 0.15 | 100 | 0 | 0 | 0.034 | -- |
| MiniBooNE | Greedy | 2 | softmax | 0.15 | 100 | 0 | 0 | 0.055 | -- |
| MiniBooNE | Random | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.166 | -- |
| MiniBooNE | Random | 1 | softmax | 0.15 | 100 | 0 | 0 | 0.163 | -- |
| MiniBooNE | Random | 2 | softmax | 0.15 | 100 | 0 | 0 | 0.177 | -- |
| Spambase | eG(.25) | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.110 | -- |
| Spambase | eG(.5) | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.119 | -- |
| Spambase | Greedy | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.092 | -- |
| Spambase | Greedy | 1 | softmax | 0.15 | 100 | 0 | 0 | 0.174 | -- |
| Spambase | Greedy | 2 | softmax | 0.15 | 100 | 0 | 0 | 0.171 | -- |
| Spambase | Random | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.208 | -- |
| Spambase | Random | 1 | softmax | 0.15 | 100 | 0 | 0 | 0.203 | -- |
| Spambase | Random | 2 | softmax | 0.15 | 100 | 0 | 0 | 0.210 | -- |

#### Panel B: lambda_ref = 0.7
| Dataset | Policy | Seed | Score | Alpha | Cert/100 | Refuse/100 | Cond.viol | Cost/full | Diag |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| MNIST | eG(.25) | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | eG(.5) | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Greedy | 0 | margin | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Greedy | 0 | softmax | 0.15 | 8 | 92 | 0 | 0.972 | U |
| MNIST | Greedy | 1 | softmax | 0.20 | 4 | 96 | 0 | 0.998 | U |
| MNIST | Greedy | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Random | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Random | 1 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Random | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| Adult | eG(.25) | 0 | softmax | 0.20 | 100 | 0 | 0 | 0.340 | -- |
| Adult | eG(.5) | 0 | softmax | 0.20 | 100 | 0 | 0 | 0.321 | -- |
| Adult | Greedy | 0 | margin | 0.20 | 0 | 100 | 0 | 1.000 | F |
| Adult | Greedy | 0 | softmax | 0.20 | 100 | 0 | 0 | 0.361 | -- |
| Adult | Greedy | 1 | softmax | 0.25 | 100 | 0 | 0 | 0.310 | -- |
| Adult | Greedy | 2 | softmax | 0.20 | 100 | 0 | 0 | 0.209 | -- |
| Adult | Random | 0 | softmax | 0.20 | 100 | 0 | 0 | 0.277 | -- |
| Adult | Random | 1 | softmax | 0.25 | 100 | 0 | 0 | 0.201 | -- |
| Adult | Random | 2 | softmax | 0.20 | 100 | 0 | 0 | 0.231 | -- |
| MiniBooNE | eG(.25) | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.062 | -- |
| MiniBooNE | eG(.5) | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.088 | -- |
| MiniBooNE | Greedy | 0 | margin | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Greedy | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.050 | -- |
| MiniBooNE | Greedy | 1 | softmax | 0.15 | 100 | 0 | 0 | 0.034 | -- |
| MiniBooNE | Greedy | 2 | softmax | 0.15 | 100 | 0 | 0 | 0.055 | -- |
| MiniBooNE | Random | 0 | softmax | 0.15 | 100 | 0 | 0 | 0.166 | -- |
| MiniBooNE | Random | 1 | softmax | 0.15 | 100 | 0 | 0 | 0.163 | -- |
| MiniBooNE | Random | 2 | softmax | 0.15 | 100 | 0 | 0 | 0.177 | -- |
| Spambase | eG(.25) | 0 | softmax | 0.15 | 28 | 72 | 0 | 0.812 | U |
| Spambase | eG(.5) | 0 | softmax | 0.15 | 19 | 81 | 0 | 0.873 | U |
| Spambase | Greedy | 0 | softmax | 0.15 | 20 | 80 | 0 | 0.901 | U |
| Spambase | Greedy | 1 | softmax | 0.15 | 3 | 97 | 0 | 0.982 | U |
| Spambase | Greedy | 2 | softmax | 0.15 | 38 | 62 | 0 | 0.785 | U |
| Spambase | Random | 0 | softmax | 0.15 | 99 | 1 | 0 | 0.395 | U |
| Spambase | Random | 1 | softmax | 0.15 | 59 | 41 | 0 | 0.689 | U |
| Spambase | Random | 2 | softmax | 0.15 | 23 | 77 | 0 | 0.894 | U |

#### Panel C: lambda_ref = 0.9
| Dataset | Policy | Seed | Score | Alpha | Cert/100 | Refuse/100 | Cond.viol | Cost/full | Diag |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| MNIST | eG(.25) | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | eG(.5) | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Greedy | 0 | margin | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Greedy | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Greedy | 1 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Greedy | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Random | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Random | 1 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| MNIST | Random | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| Adult | eG(.25) | 0 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| Adult | eG(.5) | 0 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| Adult | Greedy | 0 | margin | 0.20 | 0 | 100 | 0 | 1.000 | F |
| Adult | Greedy | 0 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| Adult | Greedy | 1 | softmax | 0.25 | 0 | 100 | 0 | 1.000 | F |
| Adult | Greedy | 2 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| Adult | Random | 0 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| Adult | Random | 1 | softmax | 0.25 | 0 | 100 | 0 | 1.000 | F |
| Adult | Random | 2 | softmax | 0.20 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | eG(.25) | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | eG(.5) | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Greedy | 0 | margin | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Greedy | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Greedy | 1 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Greedy | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Random | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Random | 1 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| MiniBooNE | Random | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| Spambase | eG(.25) | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| Spambase | eG(.5) | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | U |
| Spambase | Greedy | 0 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | U |
| Spambase | Greedy | 1 | softmax | 0.15 | 1 | 99 | 1 | 0.993 | U |
| Spambase | Greedy | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | U |
| Spambase | Random | 0 | softmax | 0.15 | 2 | 98 | 0 | 0.989 | U |
| Spambase | Random | 1 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | F |
| Spambase | Random | 2 | softmax | 0.15 | 0 | 100 | 0 | 1.000 | U |

**Faithfulness:** these 10 columns represent all essential per-configuration
results EXCEPT (i) the premium vs marginal and (ii) the certified-only cost.
Both are one caption sentence away ("cost is free vs marginal exactly where
G = 1; premium up to 29.3x under full refusal") or one optional column; no
figure is needed. Panel C is highly repetitive (33 identical refusal rows) --
if space forces it, Panel C may be summarized in text plus its 2 certifying
rows, but the instruction "no omitted cells" favors keeping all three panels.

### Table S7: aggregate diagnosis + primary summary (proposal with exact values)

Panel 1 (primary, lambda_ref = 0.9): the four-row table of Section 7.

Panel 2 (aggregate by lambda_ref):

| lambda_ref | Configs certifying >= 1 | Full refusal | Certified runs / 3,500 | Cond. viol. | End-to-end cost/full range |
|---:|---:|---:|---:|---:|---|
| 0.5 | 33/35 | 2 | 3,188 | 0 | 0.034-1.000 |
| 0.7 | 26/35 | 9 | 1,901 | 0 | 0.034-1.000 |
| 0.9 | 2/35 | 33 | 3 | 1 | 0.989-1.000 |

Plus one diagnosis line: "60 ever-refusing configurations: 40 F / 0
endpoint-only / 20 U (of which 15 audit-feasible, 5 audit-unresolved);
total 61/105 certify at least once; overlap 16." This two-panel layout fits
the budget without hiding any aggregate; no figure required (existing F12/F13
remain available but are not needed for S7).

---

## 10. Rounding and terminology

Recommended display precision:
- alpha: 2 dp; lambda_ref: 1 dp;
- selected thresholds: 3 dp (grid spacing 1/99 ~ 0.0101);
- certification/refusal counts: exact integers out of 100 (never percent);
- conditional-violation rates: exact fractions "k/n_cert" (a decimal is
  misleading when n_cert = 1);
- Wilson bounds: 3 dp;
- risks and empirical family minima: 3-4 dp (the violation needs 4 dp:
  0.1675 vs 0.15, or the exact 67/400);
- family p-values: scientific notation, 2-3 significant digits (e.g.
  8.73e-93); give 2 dp for non-tiny values (0.18);
- normalized costs: 3 dp.

Canonical display names: datasets MNIST / Adult / MiniBooNE / Spambase;
"Greedy (entropy)"; "Random"; "eps-Greedy (eps = 0.25 / 0.5)"; "max-softmax
readiness"; "margin readiness"; "uniform cost" / "inverse-information cost";
diagnosis categories "certified family-wide failure (F)", "not certified /
unresolved refusal (U)", "never refuses (--)"; the fallback event:
**"certification refusal with full-acquisition fallback"** (implementation
flag: `abstained`; refusal = fallback = "abstention" in code -- pick the
refusal/fallback wording and state the equivalence once; NEVER "prediction
abstention": the system always predicts).

Prohibited or misleading wording:
- "refusal proves failure" -- PROHIBITED: 20 of 60 ever-refusing
  configurations have NO certified family-wide failure, and 15 of those are
  audit-FEASIBLE (refusal there reflects insufficient evidence at
  delta = 0.1, not infeasibility);
- "all strata" -- the certificate covers the represented calibration span
  [k_min, k_max] only (and the conditional check runs on all nonempty pool
  strata; keep the two domains distinct);
- "no threshold works" -- only as the certified family-wide audit claim on
  the audited stratum, at gamma = 0.05, for the 40 F-configurations;
- "endpoint failure" -- do not use unless formally defined; the category
  exists in the classification (class B) and is EMPTY (0/105);
- "conditional guarantee" -- PROHIBITED for the conditional full-pool check;
  it is a descriptive audit of certified selections, not a certified
  conditional guarantee (the certificate itself is the simultaneous
  P(exists k: R_k > alpha) <= delta statement);
- "independent test set" -- complementary halves of one pool are exactly
  anti-correlated (S6); never "independent";
- "all deployable policies" -- the audit indexes the precommitted threshold
  family (and forced depths) on the frozen trajectories, nothing broader;
- "0/35 IUT" as an inferential summary -- prohibited (RESULTS_FOR_PAPER
  Section 1); always give certification AND refusal counts.

---

## 11. Exact claims S7 may support

1. "CAFA-IUT certifies in >= 1 resplit for 61 of 105 configurations." --
   **SUPPORTED.** Recomputed from iut_by_lambda_ref_resplits.csv; matches
   IUT_BY_LAMBDA_REF.md headline.
2. "CAFA-IUT refuses in >= 1 resplit for 60 of 105 configurations." --
   **SUPPORTED.** Same sources.
3. "Certification and refusal overlap because a configuration can certify on
   some resplits and refuse on others." -- **SUPPORTED.** Exactly 16 mixed
   configurations (listed in Section 4.3).
4. "Among ever-refusing configurations, 40 are diagnosed as certified
   family-wide failures and 20 remain unresolved." -- **SUPPORTED WITH
   SCOPE:** say "20 are not explained by a certified family-wide failure";
   at the audit-verdict level those 20 split 15 feasible / 5 unresolved
   (Section 5.2). Source: refusal_class in iut_by_lambda_ref.csv +
   family_wide_summary.csv.
5. "No ever-refusing configuration is explained by endpoint-only failure."
   -- **SUPPORTED.** Class B count = 0/105.
6. "Only one certified selection has a conditional full-pool stratum
   violation." -- **SUPPORTED.** 1 of 5,092 certified selections (Section 6).
7. "That violation occurs for Spambase, greedy entropy, seed 1,
   lambda_ref = 0.9." -- **SUPPORTED.** Resplit 79, lambda = 0.929,
   stratum 4 risk 0.1675 vs alpha 0.15; the configuration certifies exactly
   once.
8. "CAFA-IUT refusal triggers full acquisition but does not itself prove
   infeasibility." -- **SUPPORTED.** Refusal = empty certified set at
   delta = 0.1 (no claim); the proof of infeasibility, where it exists, is
   the separate family-wide audit (40 configurations); 15 refusing
   configurations are audit-feasible.
9. "Simultaneous certification is more costly than marginal CAFA." --
   **SUPPORTED WITH SCOPE** (Section 8): premium vs marginal >= 1 in all 105
   configurations; = 1 exactly in the 41 trivially-stratified (G = 1)
   configurations; > 1 in 64, up to 29.33. Use "never cheaper; free where
   stratification is trivial".
10. "Higher lambda_ref systematically improves or worsens certification." --
    **SUPPORTED WITH SCOPE (worsens, weakly monotone):** per-cell certified
    counts are non-increasing in lambda_ref for all 35 cells (33 strictly
    decrease somewhere, 2 are constant at zero); aggregate certified runs
    3,188 -> 1,901 -> 3. No cell increases. Source: the 105-row table.
11. "The primary lambda_ref = 0.9 setting is representative of the
    sensitivity settings." -- **UNSUPPORTED; DO NOT CLAIM.** lambda_ref =
    0.9 is the extreme setting: 2/35 ever-certify vs 33/35 (0.5) and 26/35
    (0.7); certified runs 3 vs 3,188/1,901; end-to-end cost floor 0.989 vs
    0.034. State instead: 0.9 is the deepest, hardest reference threshold,
    and the qualitative refusal-with-diagnosis behavior at 0.9 is where the
    audit resolves most (40 of the 44 full-refusal configurations at
    lr 0.7/0.9 carry certified family-wide failures).

---

## 12. Contradiction and completeness checks

Searched: iut_by_lambda_ref.csv/-resplits.csv, IUT_BY_LAMBDA_REF.md,
IUT_OUTCOME_CLASSIFICATION.md, family_wide_summary.csv,
FINAL_CLAIM_DECISION.md, RESULTS_FOR_PAPER.md, project_update.md,
reviewphase_0_1_reply.md.

- 61/105: consistent everywhere (headline, classification MD, compendium).
  No conflicting count found.
- 60/105 ever-refuse: consistent (40 + 20 classes = 60; recomputed 60).
- 40/0/20: consistent; refine wording per Section 5.2 (class C is "failure
  not certified", audit verdicts 15 feasible + 5 unresolved -- calling all
  20 "unresolved audits" would be wrong; the canonical class NAME is
  "refusal, unresolved", so define it once).
- Number of conditional violations: 1 -- consistent (compendium: "exactly 1
  conditional pool-failure among certified selections in the whole grid").
- Identity of the violation: spambase ts1 (compendium) = spambase/
  greedy_entropy/ts1@lr0.9 (artifact) -- consistent; S7 should always give
  the full identity including lambda_ref = 0.9 and policy.
- "Certifies once": confirmed, exactly 1/100.
- Diagnosis per configuration vs per resplit: per configuration
  (code-verified); no artifact says otherwise.
- Span vs nominal strata: the IUT operates over the represented calibration
  span (code-verified); the conditional check over all nonempty pool strata;
  the audit over the deepest nonempty pool stratum. No artifact conflicts,
  but S7 must not blur the three domains.
- Fallback naming: code flag `abstained`; canonical docs mandate
  "certification refusal with full-acquisition fallback / NOT prediction
  abstention" -- terminological, resolved (Section 10).
- Costs include fallback: yes in `mean_deployed_cost` / `deployed_cost_over_
  full` (and the identity check passes); `mean_certified_cost` excludes it.
  Both exist -- label columns explicitly.
- Full-pool vs test-half: the IUT tables use pool costs and pool stratum
  risks; the metrics JSONs' `cafa_iut.realized_risk` and h2_table rows are
  test-half (superseded for S7) -- not mixed here.
- FINAL_CLAIM_DECISION "IUT cert rate @0.9 = 0.00" for the four primaries:
  consistent (0/100 each).
- Local counts (56/99, A:33/C:23): local replication only, flagged
  non-citable -- not a conflict.

No numerical contradiction between canonical artifacts was found.

---

## 13. Missing values and verdict

### Missing information

- Per-resplit realized calibration spans and empty-interior-stratum counts:
  not stored (Section 2.2 gives the one structurally forced case,
  adult/greedy/ts1@lr0.9, from pool-level bucket sizes).
- Median and p5/p95 of deployed/certified costs: not stored; reconstructable
  only via the frozen pool caches (outside the repo).
- Overall conditional violation rate (1/5,092) and its Wilson interval:
  computed here from the exact per-resplit artifact; not stored as a scalar.
- Mean selected threshold per configuration: computed here from exact
  per-resplit lambda_idx; only min/median/max are stored.
- Whether strata other than k = 4 also exceed alpha in the single violating
  resplit: not determinable from frozen artifacts (curves exist for the
  deepest stratum only); the "any stratum" event is established by k = 4.
- Oracle comparison for CAFA-IUT: does not exist in any canonical artifact.
- Superseded-estimand-only values: cafa_iut test-half realized risks
  (metrics JSONs, h2_table) -- excluded by design.

None of these blocks the planned tables: every cell of Table S6 (all three
panels) and Table S7 is populated above from frozen artifacts.

### Required author decisions

1. One 105-row table vs three 35-row panels: three panels recommended
   (values ready above); decide whether Panel C (33 identical full-refusal
   rows) is kept verbatim or condensed with its 2 certifying rows shown --
   keeping it verbatim honors "no omitted cells".
2. End-to-end vs certified-only cost in the Cost/full column: end-to-end
   (fallback included) recommended and used above; if certified-only is also
   wanted, add the `certonly_cost_over_full` column from the CSV.
3. Whether the compact aggregate table (Table S7, two panels) is included:
   recommended, exact values provided.
4. Figure: none needed; all essential results are tabular (F12/F13 exist if
   the authors later prefer a visual for the cost-refusal frontier). No
   `figS7_instruction.md` is required on the current evidence.
5. Whether to display the U-class split (15 audit-feasible / 5
   audit-unresolved) in the table caption or only in the S7 text.

### Final verdict

`S7 SOURCE MATERIAL COMPLETE`
