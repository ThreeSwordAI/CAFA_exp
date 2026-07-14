# S6_answer.md -- Verified source material for S6 (Complete Marginal Results)

Prepared from the canonical repository artifacts only. Every number below was
re-extracted this pass from the frozen files named in Section 1; nothing is
quoted from memory, drafts, or local replications. Extraction scripts read
`results_committed/metrics/*.json`, `results_committed/pool_risk_gate.csv`,
`results_committed/pool_stratum_resplits.csv`, `results_committed/pool_plugin_eval.csv`,
`results_committed/validity_diagnostic.csv`, and `configs/committed_v2_*.json`.
Where a summary was computed from an exact per-resplit artifact rather than
read from a stored scalar, this is stated explicitly at the point of use.

Conventions: "pool" = the full post-probe evaluation pool (calibration half +
test half together); "test-half" = the complementary 50% split (superseded
diagnostic estimand); counts are exact integers out of 100 resplits; rates are
count/100.

---

## 1. Canonical result sources and scope

1. **Exact canonical files used**
   - `results_committed/metrics/*.json` (35 files) -- per-resplit selections,
     abstention flags, test-half realized risk/cost for every method, grid,
     alpha, delta, meta.
   - `results_committed/pool_risk_gate.csv` + `results_committed/POOL_RISK_GATE.md`
     -- the final marginal validity gate (pool estimand), Phase 5.2.
   - `results_committed/pool_stratum_resplits.csv` (lambda_ref = 0.9 rows) --
     per-resplit exact pool risk `agg_pool_risk`, pool cost `pool_cost`, and
     selected `lambda_idx` for every resplit of every cell (Phase 5.3).
   - `results_committed/pool_plugin_eval.csv` + `POOL_PLUGIN_EVAL.md` -- plugin
     baseline on the pool estimand; also the source of the exact full-pool
     full-acquisition cost per cell (via `mean_pool_cost / cost_over_full`).
   - `results_committed/validity_diagnostic.csv` -- mean pool risk / margin
     cross-check (Phase 5).
   - `results_committed/h2_table.csv` -- test-half method summaries
     (columns: violation_frac, wilson_lo/hi, abstain_rate, mean_risk,
     mean_cost, cost_ratio_full; no cost/oracle column).
   - `configs/committed_v2_<dataset>_ts<seed>.json` -- committed probe floors
     and alphas.
   - `results_committed/FINAL_CLAIM_DECISION.md`, `PHASE5_PROVENANCE.md` --
     freeze metadata and claim ledger.
   - `src/cafa/risk_control.py` (byte-frozen selector), `src/cafa/baselines.py`
     (baseline definitions), `scripts/pool_risk_gate.py` (gate code),
     `scripts/run_eval_sweep.py` (runner).
2. **Freeze label.** Compute closed at tag `canonical-v2.2`; the Phase-5.3
   analysis artifacts are stamped with commit `7bdb1bf27fc3` (recorded inside
   `FINAL_CLAIM_DECISION.md`); the results compendium is versioned v2.3. The
   frozen selector `src/cafa/risk_control.py` has SHA-256
   `c37ab67bbb02...` (full hash in `repro/frozen_hashes.txt`).
3. **Number of marginal cells: 35** (= number of metrics JSONs; verified by count).
4. **Calibration resplits per cell: 100** (`n_resplits` = 100 in every file;
   verified per cell).
5. **Total marginal calibration runs: 3,500** (35 x 100).
6. **Same post-probe evaluation pool within a frozen cell: yes.** The pool is
   fixed by (dataset, train seed, policy, score): probe/eval split at probe
   seed 777, probe_frac 0.10; the 100 resplits are 50/50 partitions of that
   one fixed pool (`resplit_cal_test`, resplit RNG offset 1,000,000 + resplit
   index). n_eval: MNIST 25,200; Adult 16,280; MiniBooNE 46,823; Spambase
   1,656 (read from `meta.n_eval`).
7. **Fallback/refusal: never.** `abstained` is false and `lambda_idx` is not
   None in all 3,500 marginal runs (abstentions column = 0 for all 35 rows of
   `pool_risk_gate.csv`; independently recounted from the metrics JSONs).
8. **Meaning of a cell.** A cell = one frozen combination of (dataset,
   acquisition policy incl. epsilon, training seed, readiness score). The
   threshold grid (100 points, `linspace(0,1,100)`, endpoints 0.0 and 1.0),
   the target risk (the committed alpha of that dataset x seed), and the
   cost schemes are *attributes determined by the cell*, not free dimensions:
   alpha is committed per (dataset, train seed); every cell is evaluated
   under its primary cost scheme (see below); the grid is global. So the cell
   count multiplies only over dataset x policy x seed x score.
9. **Composition of the 35 cells** (verified against the 35 metrics files):
   - 8 primary-seed greedy/random cells: 4 datasets x {greedy_entropy, random} at ts0;
   - 8 epsilon-greedy cells: 4 datasets x eps in {0.25, 0.5} at ts0 (softmax);
   - 16 additional-backbone-seed cells: 4 datasets x {greedy_entropy, random} x ts in {1, 2};
   - 3 margin-readiness cells: {MNIST, Adult, MiniBooNE} x greedy_entropy x ts0, score = margin.
10. **Configured but excluded:** rollout cell 16 = (Spambase, greedy_entropy,
    ts0, score = margin). It exists in the fixed cell list of
    `scripts/run_pool_rollout.py` (lines 20-23) marked "[optional]" with the
    stated reason: the score ablation was scoped to datasets where the
    family-wide audit *detects* (Spambase is unresolved), so cell 16 was
    never run in the canonical batch. No canonical metrics file exists for it.

**Files that must NOT be used for S6:**
- anything under local (non-cluster) result trees -- replication only, never
  citable (two-environment rule);
- `results_committed/RESULTS.md` Sections that predate Phase 5.2/5.3 and any
  test-half violation "gate" numbers (superseded estimand; kept as
  diagnostics -- Section 3.5 below);
- `analysis_v2/*` working copies on any machine (the committed copies under
  `results_committed/` are canonical);
- the pre-Phase-5.2 `validity_gate` / H1 test-half violation tables in
  `PHASE3_REPORT.md` and older `project_update.md` sections (flagged by the
  prohibited-phrase scan in `FINAL_CLAIM_DECISION.md`);
- the local pilot's Adult argmin (lambda = 0.899) and any figure built from
  local CSVs.

---

## 2. Exact marginal gate definition

Source of truth: `scripts/pool_risk_gate.py` (quoted below) and its outputs
`pool_risk_gate.csv` / `POOL_RISK_GATE.md`.

### 2.1 Evaluated estimand

- **Quantity gated: full post-probe pool risk.** For each resplit i, the
  selected threshold lambda_hat_i is evaluated as
  `R_pool(lambda_hat_i) = mean over ALL n_eval pool rows of loss at the stop
  index induced by lambda_hat_i` (code: `r_pool = losses_full.mean(axis=0)`
  over the entire eval pool, indexed at the recorded `lambda_idx`).
- **Threshold selection:** the frozen `ltt_select` (Hoeffding-Bentkus +
  fixed-sequence, procedure `fixed_sequence` from the experiment config) run
  on the **calibration half only** of resplit i, at the committed alpha and
  delta = 0.1, minimizing expected cost among certified thresholds.
- **Rule evaluated on:** all n_eval pool examples (calibration + test halves
  together). Yes, the selected rule is re-evaluated on the full pool for
  every one of the 100 resplits.
- **Same threshold everywhere: yes.** One lambda_hat_i per resplit is used
  for the calibration-risk, test-half-risk, and pool-risk numbers.
- **Estimand status:** the pool is treated as the population for this
  experiment ("The eval pool IS the population"); the gate checks the
  marginal LTT guarantee *for the pool-risk estimand*, which remains a valid
  LTT target because a without-replacement (hypergeometric) calibration
  sample's empirical mean is dominated by its binomial counterpart (Hoeffding
  1963, Sec. 6), so P(R_pool(lambda_hat) > alpha) <= delta holds as
  certified. It is simultaneously exact on the finite pool -- i.e., it is
  the certified guarantee evaluated without estimation noise, NOT an
  independent population-risk estimate (see Section 10, claim 8).
- **Violation target:** the committed alpha of the cell (exact values in the
  Section 3 table; committed before any evaluation, rule
  alpha = ceil_0.05(floor + 0.05)).

### 2.2 Violation event and denominator

Exact code (pool_risk_gate.py, lines 159-169):

```python
if recorded is None:
    abstain += 1
    rp = r_pool_full            # abstain -> full acquisition
else:
    rp = float(r_pool[int(recorded)])
if rp > alpha:
    pool_viol += 1
```

- **Strict `>`**, plain float64 comparison, **no tolerance term**.
- **Abstention handling:** an abstention is counted in a separate `abstain`
  counter and the rule is evaluated at full acquisition; note the code would
  still count it as a violation if the full-acquisition pool risk exceeded
  alpha (the `if rp > alpha` check runs on the fallback value too). This is
  moot in the canonical results: **0 abstentions in all 3,500 runs**, and no
  full-acquisition pool risk exceeds its alpha.
- **Denominator:** n = number of resplits in the lambda_ref = 0.9 block =
  **exactly 100 for every cell** (marginal selection is lambda_ref-independent,
  so the 100 resplits are counted once, not 3x over lambda_ref blocks). A
  cell with fewer eligible runs cannot occur in the canonical artifacts (all
  35 files contain 100 resplits; abstentions could reduce the *certified*
  count but not the denominator, and none occurred).

### 2.3 Confidence interval and pass criterion

Exact code (pool_risk_gate.py):

```python
_Z = 1.96
def wilson(k, n, z=_Z):
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)
...
"pool_gate": "PASS" if phi <= delta else "FAIL",
```

- **Method:** Wilson score interval, hand-coded (no library call), z = 1.96.
- **Level:** 95%, **two-sided** interval; the gate uses its **upper endpoint**.
- **Precommitted criterion:** PASS iff Wilson-95% upper bound <= delta.
  The comparison is on the **confidence upper bound**, not the raw rate.
  **Equality passes** (`<=`).
- **delta = 0.1** (read from every metrics JSON; it is the LTT delta of the
  experiment config, committed at Phase 0).
- **Where committed:** the criterion "Wilson 95% UB <= delta, the same
  criterion as the main gate table" is written into the Phase-5.2 script and
  its header documentation before the pool results existed; it is the
  identical criterion the Phase-1 analyzer (`analyze_results.py`) had applied
  to the (superseded) test-half gate since the first canonical run. The
  estimand change in Phase 5.2 changed *what* is measured, not the criterion.

### 2.4 Determinism and reconstruction checks

All checks are hard `assert`s -- the artifacts could not have been written if
any had failed. None were skipped.

- **Selected-threshold recomputation:** for every resplit of every cell, the
  gate re-runs the frozen `ltt_select` on the resplit's calibration arrays and
  asserts exact equality (integer `lambda_idx`, and matching None-ness) with
  the value recorded in the metrics JSON: **3,500/3,500 match, tolerance =
  exact integer equality**.
- **Estimand cross-check:** per-cell `mean_R_pool_at_lambda` asserted equal to
  the independently computed Phase-5 `validity_diagnostic.csv` value,
  tolerance 1e-9: **35/35 PASS** (script prints the PASS line).
- **Full-pool reconstruction from strata:** in the Phase-5.3 stratum
  evaluation, sum_k q_k * R_k is asserted equal to the aggregate pool risk
  per resplit (tolerance 1e-9), for every resplit (documented in
  RESULTS_FOR_PAPER Section 4: "asserted per resplit").
- **Plugin selection reconstruction:** the Phase-5.3 plugin pool evaluation
  asserts the recomputed plugin threshold equals the recorded one on every
  resplit of every cell (POOL_PLUGIN_EVAL.md header).
- **Full-pool identity with halves:** R_test = (n_eval*R_pool - n_cal*R_cal)/n_test
  is the exact complementary-split identity used throughout Phase 5.2
  (measured corr(R_cal, R_test) at fixed lambda = -1.0000 on all 35 cells,
  range -1.0000 to -1.0000, from POOL_RISK_GATE.md).
- **Family-wide endpoint reproduction vs frozen H3 rows:** asserted exact,
  4/4 (RESULTS_FOR_PAPER Section 3) -- not part of the marginal gate but part
  of the same freeze.

---

## 3. Complete 35-cell marginal results

The complete per-cell extraction is given as a fenced CSV (one row per cell;
no cell omitted). Provenance per column group:

- Identifiers, floors, alphas: metrics JSON meta + `configs/committed_v2_*.json`.
- `certified`, `fallbacks`, test-half risks/costs: metrics JSONs
  (lambda_ref 0.9 block, primary scheme; realized values are stored rounded
  to 6 decimals).
- `lam_*` threshold summaries and all `*_pool_risk` / `*_pool_cost` fields:
  **computed in this response from the exact per-resplit artifact**
  `pool_stratum_resplits.csv` (unrounded `agg_pool_risk`, `pool_cost`,
  `lambda_idx` per resplit; thresholds mapped through the stored grid).
  No summary was computed from rounded values.
- Gate fields (`pool_viol*`, `pool_lo/hi`, `pool_gate`, `test_viol*`,
  `test_hi`, `test_gate`): `pool_risk_gate.csv` verbatim; counts = rate x 100
  (exact, since n = 100).
- `full_pool_cost`: derived exactly as `mean_pool_cost / cost_over_full` from
  `pool_plugin_eval.csv` (both stored unrounded; stated derivation).
- `mean_cal_risk_derived`: derived from the exact identity
  n_cal*R_cal = n_eval*R_pool - n_test*R_test using the unrounded pool mean
  and the 6-dp-rounded test mean -- accurate to ~1e-6; labeled "derived".
  Per-resplit calibration risks are NOT stored, so **median calibration risk:
  NOT FOUND** (searched metrics JSONs, pool_stratum_resplits.csv,
  validity_diagnostic.csv).
- `oracle_test_mean_cost`, `cost_over_oracle_testhalf`, `mean_test_cost`,
  `full_test_cost`: test-half realized values from the metrics JSONs (the
  cost-comparison convention of the canonical H2 table and the manuscript).

Column legend: `primary` 1 = primary cell (greedy_entropy, ts0, softmax);
`certified` = resplits returning a certified threshold; `fallbacks` =
abstentions (implementation term: `abstained`); `pool_viol_count` etc. as
named; `p5/p95` = 5th/95th percentiles (numpy linear interpolation);
`mean_margin` = alpha - mean pool risk; `min_margin` = alpha - max pool risk.

```csv
cell,dataset,policy,eps,seed,score,scheme,floor,alpha,n_resplits,grid_size,primary,certified,fallbacks,lam_min,lam_med,lam_mean,lam_max,pool_viol_count,pool_viol_rate,pool_lo,pool_hi,pool_gate,test_viol_count,test_viol_rate,test_hi,test_gate,mean_test_risk,med_test_risk,mean_pool_risk,med_pool_risk,min_pool_risk,max_pool_risk,p5_pool_risk,p95_pool_risk,mean_margin,min_margin,mean_cal_risk_derived,mean_pool_cost,med_pool_cost,full_pool_cost,mean_cost_over_full,med_cost_over_full,p5_cost_over_full,p95_cost_over_full,mean_test_cost,oracle_test_mean_cost,oracle_none_count,cost_over_oracle_testhalf,full_test_cost
mnist/eps_greedy_eps0.25/ts0,mnist,eps_greedy_eps0.25,0.25,0,softmax,uniform,0.077857,0.15,100,100,0,100,0,0.8181818181818182,0.8282828282828284,0.8295959595959596,0.8383838383838385,0,0.0,0.0,0.03699480747600191,PASS,11,0.11,0.18631463027903022,FAIL,0.14232459000000003,0.142778,0.14197420634920632,0.14253968253968255,0.1376190476190476,0.14813492063492065,0.1376190476190476,0.14813492063492065,0.008025793650793672,0.0018650793650793474,0.14162382269841264,22.294318650793656,22.190833333333334,49.0,0.45498609491415626,0.45287414965986394,0.4380547457078069,0.46846614836410755,22.28730556,21.587838150000003,0,1.0324009937975192,49.0
mnist/eps_greedy_eps0.5/ts0,mnist,eps_greedy_eps0.5,0.5,0,softmax,uniform,0.077857,0.15,100,100,0,100,0,0.787878787878788,0.797979797979798,0.7971717171717168,0.8080808080808082,0,0.0,0.0,0.03699480747600191,PASS,14,0.14,0.22137360383807236,FAIL,0.14181027,0.1409125,0.14160634920634924,0.14103174603174604,0.13607142857142857,0.1471031746031746,0.13607142857142857,0.1471031746031746,0.008393650793650759,0.0028968253968253976,0.1414024284126985,21.626246031746042,21.674801587301587,49.0,0.4413519598315519,0.4423428895367671,0.4296509556203434,0.4553401360544218,21.618394470000002,21.043518230000004,0,1.0273184471207122,49.0
mnist/greedy_entropy/ts0,mnist,greedy_entropy,,0,softmax,uniform,0.077857,0.15,100,100,1,100,0,0.8484848484848485,0.8585858585858587,0.8601010101010101,0.8686868686868687,0,0.0,0.0,0.03699480747600191,PASS,2,0.02,0.07001316294199365,PASS,0.14142696,0.1420635,0.14145158730158733,0.14238095238095239,0.1361111111111111,0.1492063492063492,0.1361111111111111,0.14238095238095239,0.008548412698412666,0.0007936507936507908,0.14147621460317467,24.855126587301584,24.70190476190476,49.0,0.5072474813735017,0.5041205053449951,0.5041205053449951,0.5248436993845157,24.847061089999997,24.02721109,0,1.0341217296060303,49.0
mnist/greedy_entropy/ts0[margin],mnist,greedy_entropy,,0,margin,uniform,0.077857,0.15,100,100,0,100,0,0.7777777777777778,0.787878787878788,0.7880808080808079,0.8080808080808082,0,0.0,0.0,0.03699480747600191,PASS,1,0.01,0.0544875247609346,PASS,0.14232384000000003,0.1425795,0.14222738095238094,0.14246031746031745,0.13313492063492063,0.1461111111111111,0.13817460317460317,0.1461111111111111,0.007772619047619056,0.003888888888888886,0.14213092190476184,24.934960317460323,24.92238095238095,49.0,0.5088767411726597,0.5086200194363459,0.4953158406219631,0.5218262066731454,24.923921500000002,23.90329209,0,1.0426982779676186,49.0
mnist/random/ts0,mnist,random,,0,softmax,uniform,0.077857,0.15,100,100,0,100,0,0.7171717171717172,0.7171717171717172,0.7224242424242427,0.7373737373737375,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.14169996999999998,0.1440875,0.14166031746031743,0.14404761904761904,0.13444444444444445,0.14404761904761904,0.139484126984127,0.14404761904761904,0.008339682539682564,0.005952380952380959,0.14162066492063488,25.905200000000004,25.662142857142857,49.00000000000001,0.5286775510204081,0.5237172011661807,0.5237172011661807,0.5332118561710398,25.90008809,25.39325712,0,1.0199592737396737,49.0
mnist/greedy_entropy/ts1,mnist,greedy_entropy,,1,softmax,uniform,0.101071,0.2,100,100,0,100,0,0.8383838383838385,0.8484848484848485,0.8506060606060604,0.8585858585858587,1,0.01,0.0017673865655472645,0.0544875247609346,PASS,1,0.01,0.0544875247609346,PASS,0.19092615999999998,0.1932935,0.19057658730158736,0.1924206349206349,0.18369047619047618,0.20007936507936508,0.18369047619047618,0.1924206349206349,0.009423412698412653,-7.936507936506798e-05,0.19022701460317476,25.90418650793651,25.680079365079365,49.0,0.5286568675089084,0.5240832523485585,0.5240832523485585,0.545864107547781,25.90280872,25.250807919999993,0,1.02582098767159,49.0
mnist/random/ts1,mnist,random,,1,softmax,uniform,0.101071,0.2,100,100,0,100,0,0.7373737373737375,0.7474747474747475,0.7442424242424245,0.7575757575757577,0,0.0,0.0,0.03699480747600191,PASS,6,0.06,0.12476968531222507,FAIL,0.19161746999999998,0.189444,0.19097619047619055,0.18884920634920635,0.18321428571428572,0.19543650793650794,0.18884920634920635,0.19543650793650794,0.009023809523809462,0.004563492063492075,0.19033491095238117,27.296800793650792,27.469761904761906,49.0,0.5570775672173631,0.5606073858114675,0.5495132815030774,0.5606073858114675,27.296165929999997,26.889488130000004,0,1.015124043939917,49.0
mnist/greedy_entropy/ts2,mnist,greedy_entropy,,2,softmax,uniform,0.094286,0.15,100,100,0,100,0,0.9393939393939394,0.9494949494949496,0.948888888888889,0.9494949494949496,0,0.0,0.0,0.03699480747600191,PASS,6,0.06,0.12476968531222507,FAIL,0.13806986,0.137262,0.13823095238095232,0.1376190476190476,0.1376190476190476,0.14781746031746032,0.1376190476190476,0.14781746031746032,0.011769047619047679,0.002182539682539675,0.13839204476190464,36.19288968253968,36.30289682539683,49.0,0.7386304016844832,0.7408754454162618,0.7034580498866213,0.7408754454162618,36.197265849999994,34.78654447,0,1.0405536508869573,49.0
mnist/random/ts2,mnist,random,,2,softmax,uniform,0.094286,0.15,100,100,0,100,0,0.8181818181818182,0.8383838383838385,0.8339393939393939,0.8484848484848485,0,0.0,0.0,0.03699480747600191,PASS,1,0.01,0.0544875247609346,PASS,0.14137463000000003,0.1389285,0.14140515873015871,0.13904761904761906,0.13416666666666666,0.14932539682539683,0.13904761904761906,0.1444047619047619,0.00859484126984128,0.0006746031746031611,0.14143568746031737,30.00540396825397,30.2759126984127,49.00000000000001,0.6123551830255911,0.6178757693553611,0.6053206997084547,0.6178757693553611,30.00700319,29.242546860000008,0,1.0261419203210944,49.0
tabular-adult/eps_greedy_eps0.25/ts0,tabular-adult,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.14649,0.2,100,100,0,100,0,0.7777777777777778,0.7777777777777778,0.7777777777777776,0.7777777777777778,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.16554791,0.165725,0.1652948402948403,0.1652948402948403,0.1652948402948403,0.1652948402948403,0.1652948402948403,0.1652948402948403,0.03470515970515972,0.03470515970515972,0.1650417705896806,32.42263026312355,32.42263026312354,95.2779627559329,0.34029516716450375,0.3402951671645036,0.3402951671645036,0.3402951671645036,32.377700159999996,32.377700159999996,0,1.0,95.27796300000001
tabular-adult/eps_greedy_eps0.5/ts0,tabular-adult,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.14649,0.2,100,100,0,100,0,0.7777777777777778,0.7777777777777778,0.7777777777777776,0.7777777777777778,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.17182431000000004,0.171622,0.17168304668304665,0.17168304668304668,0.17168304668304668,0.17168304668304668,0.17168304668304668,0.17168304668304668,0.02831695331695336,0.02831695331695333,0.17154178336609327,30.62466144955697,30.62466144955696,95.2779627559329,0.3214243940963147,0.32142439409631457,0.32142439409631457,0.32142439409631457,30.60018052,30.60018052,0,1.0,95.27796300000001
tabular-adult/greedy_entropy/ts0,tabular-adult,greedy_entropy,,0,softmax,inverse_info,0.14649,0.2,100,100,1,100,0,0.7777777777777778,0.7777777777777778,0.7777777777777776,0.7777777777777778,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.16142997999999997,0.161548,0.16124078624078628,0.16124078624078625,0.16124078624078625,0.16124078624078625,0.16124078624078625,0.16124078624078625,0.038759213759213734,0.03875921375921376,0.16105159248157258,34.41586915733372,34.41586915733372,95.2779627559329,0.3612154181496776,0.3612154181496776,0.3612154181496776,0.3612154181496776,34.35980669,34.35980669,0,1.0,95.27796300000001
tabular-adult/greedy_entropy/ts0[margin],tabular-adult,greedy_entropy,,0,margin,inverse_info,0.14649,0.2,100,100,0,100,0,0.5454545454545455,0.5454545454545455,0.5454545454545456,0.5454545454545455,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.16137100000000001,0.161425,0.1611793611793612,0.16117936117936119,0.16117936117936119,0.16117936117936119,0.16117936117936119,0.16117936117936119,0.0388206388206388,0.038820638820638825,0.1609877223587224,33.83521796450876,33.83521796450876,95.2779627559329,0.3551211317477698,0.3551211317477698,0.3551211317477698,0.3551211317477698,33.78472423,33.78472423,0,1.0,95.27796300000001
tabular-adult/random/ts0,tabular-adult,random,,0,softmax,inverse_info,0.14649,0.2,100,100,0,100,0,0.7777777777777778,0.7777777777777778,0.7777777777777776,0.7777777777777778,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.18293241000000002,0.182801,0.18298525798525803,0.182985257985258,0.182985257985258,0.182985257985258,0.182985257985258,0.182985257985258,0.017014742014741985,0.017014742014742013,0.183038105970516,26.418922428542345,26.418922428542345,95.2779627559329,0.27728261251993713,0.27728261251993713,0.27728261251993713,0.27728261251993713,26.409202299999997,26.409202299999997,0,1.0,95.27796300000001
tabular-adult/greedy_entropy/ts1,tabular-adult,greedy_entropy,,1,softmax,inverse_info,0.161415,0.25,100,100,0,100,0,0.7575757575757577,0.7575757575757577,0.7575757575757573,0.7575757575757577,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.16500860999999997,0.164619,0.1644348894348895,0.16443488943488943,0.16443488943488943,0.16443488943488943,0.16443488943488943,0.16443488943488943,0.08556511056511051,0.08556511056511057,0.163861168869779,29.184625851138765,29.18462585113876,94.21552786140265,0.30976449969129616,0.3097644996912961,0.3097644996912961,0.3097644996912961,29.224746199999995,26.032505529999998,0,1.1226251797515703,94.215528
tabular-adult/random/ts1,tabular-adult,random,,1,softmax,inverse_info,0.161415,0.25,100,100,0,100,0,0.7575757575757577,0.7575757575757577,0.7575757575757573,0.7575757575757577,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.20256389,0.2025185,0.20214987714987717,0.20214987714987714,0.20214987714987714,0.20214987714987714,0.20214987714987714,0.20214987714987714,0.04785012285012283,0.047850122850122856,0.20173586429975435,18.894206540805495,18.89420654080549,94.21552786140268,0.20054238372044292,0.20054238372044286,0.20054238372044286,0.20054238372044286,18.88977663,16.818709079999998,0,1.1231406964796613,94.215528
tabular-adult/greedy_entropy/ts2,tabular-adult,greedy_entropy,,2,softmax,inverse_info,0.145384,0.2,100,100,0,100,0,0.7373737373737375,0.7424242424242424,0.7424242424242427,0.7474747474747475,0,0.0,0.0,0.03699480747600191,PASS,1,0.01,0.0544875247609346,PASS,0.18691152999999996,0.1873465,0.18654791154791148,0.18654791154791156,0.18083538083538084,0.19226044226044225,0.18083538083538084,0.19226044226044225,0.013452088452088534,0.007739557739557756,0.18618429309582296,19.561147857052525,19.561147857052518,93.4265632000972,0.20937458456175098,0.2093745845617509,0.19253088439244756,0.2262182847310543,19.57514636,18.03368956,0,1.0854765074485402,93.42656300000004
tabular-adult/random/ts2,tabular-adult,random,,2,softmax,inverse_info,0.145384,0.2,100,100,0,100,0,0.7373737373737375,0.7373737373737375,0.7383838383838386,0.7575757575757577,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.18725919000000002,0.187285,0.18747297297297294,0.1877149877149877,0.18058968058968058,0.1877149877149877,0.18605651105651105,0.1877149877149877,0.012527027027027071,0.012285012285012303,0.18768675594594586,21.572801469294106,21.42198522851351,93.42656320009722,0.23090650806762908,0.2292922322598207,0.2292922322598207,0.24235246282457282,21.619292740000002,21.47063166,0,1.0069239267085448,93.42656300000004
tabular-MiniBooNE/eps_greedy_eps0.25/ts0,tabular-MiniBooNE,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.084374,0.15,100,100,0,100,0,0.7171717171717172,0.7272727272727273,0.7265656565656569,0.7373737373737375,0,0.0,0.0,0.03699480747600191,PASS,8,0.08,0.14998266879403072,FAIL,0.14300251,0.14249699999999998,0.14302244623368854,0.1426435726032078,0.1364500352390919,0.14815368515473165,0.1426435726032078,0.14815368515473165,0.006977553766311456,0.001846314845268343,0.143042381615838,21.015571357339066,21.15127980561571,341.0632155951181,0.06161781862247791,0.06201571684800144,0.05624528570222124,0.06201571684800144,20.991501640000003,19.46472558,0,1.0784380983808355,341.0632160000001
tabular-MiniBooNE/eps_greedy_eps0.5/ts0,tabular-MiniBooNE,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.084374,0.15,100,100,0,100,0,0.7474747474747475,0.7474747474747475,0.7476767676767679,0.7575757575757577,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.14184018,0.141856,0.14175127608226726,0.1418533626636482,0.13674903359460094,0.1418533626636482,0.1418533626636482,0.1418533626636482,0.008248723917732736,0.008146637336351792,0.1416623759618999,29.92971103780145,29.874574040780935,341.0632155951181,0.08775414547586836,0.08759248337189651,0.08759248337189651,0.08759248337189651,29.95460851,28.78135232,0,1.0407644566855432,341.0632160000001
tabular-MiniBooNE/greedy_entropy/ts0,tabular-MiniBooNE,greedy_entropy,,0,softmax,inverse_info,0.084374,0.15,100,100,1,100,0,0.7171717171717172,0.7171717171717172,0.7171717171717176,0.7171717171717172,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.13271973,0.132673,0.13256305661747428,0.1325630566174743,0.1325630566174743,0.1325630566174743,0.1325630566174743,0.1325630566174743,0.017436943382525716,0.017436943382525688,0.13240638992696044,17.036014533399417,17.036014533399417,341.0632155951181,0.04994972707236525,0.04994972707236525,0.04994972707236525,0.04994972707236525,17.01220028,17.01220028,0,1.0,341.0632160000001
tabular-MiniBooNE/greedy_entropy/ts0[margin],tabular-MiniBooNE,greedy_entropy,,0,margin,inverse_info,0.084374,0.15,100,100,0,100,0,0.43434343434343436,0.43434343434343436,0.43434343434343425,0.43434343434343436,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.13271973,0.132673,0.13256305661747428,0.1325630566174743,0.1325630566174743,0.1325630566174743,0.1325630566174743,0.1325630566174743,0.017436943382525716,0.017436943382525688,0.13240638992696044,17.036014533399417,17.036014533399417,341.0632155951181,0.04994972707236525,0.04994972707236525,0.04994972707236525,0.04994972707236525,17.01220028,17.01220028,0,1.0,341.0632160000001
tabular-MiniBooNE/random/ts0,tabular-MiniBooNE,random,,0,softmax,inverse_info,0.084374,0.15,100,100,0,100,0,0.787878787878788,0.787878787878788,0.7902020202020199,0.797979797979798,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.14334413999999998,0.144932,0.1432432778762574,0.14473656109177113,0.13824402537214617,0.14473656109177113,0.13824402537214617,0.14473656109177113,0.006756722123742592,0.005263438908228862,0.14314242006065267,56.52658637178791,55.46290747377196,341.0632155951181,0.16573639075429222,0.1626176759548673,0.1626176759548673,0.17617730551758426,56.480028080000004,54.47955218,0,1.0367197566784405,341.0632160000001
tabular-MiniBooNE/greedy_entropy/ts1,tabular-MiniBooNE,greedy_entropy,,1,softmax,inverse_info,0.088603,0.15,100,100,0,100,0,0.7474747474747475,0.7575757575757577,0.7544444444444443,0.7575757575757577,0,0.0,0.0,0.03699480747600191,PASS,5,0.05,0.11175196527208817,FAIL,0.14279183,0.141045,0.1426606582235226,0.14080686841936654,0.14080686841936654,0.14678683552954744,0.14080686841936654,0.14678683552954744,0.007339341776477382,0.0032131644704525564,0.14252949204980347,11.670197009987781,12.233806912229511,342.2820952322199,0.03409525994069361,0.03574188390990635,0.03043019368663945,0.03574188390990635,11.65601637,10.3547698,0,1.1256663928926745,342.28209500000014
tabular-MiniBooNE/random/ts1,tabular-MiniBooNE,random,,1,softmax,inverse_info,0.088603,0.15,100,100,0,100,0,0.7777777777777778,0.7777777777777778,0.7815151515151513,0.787878787878788,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.1430007,0.1456155,0.14289985690792992,0.14527048672660872,0.13886337910855776,0.14527048672660872,0.13886337910855776,0.14527048672660872,0.007100143092070077,0.004729513273391273,0.1427990181231848,55.6233054407378,53.92109410142048,342.2820952322199,0.1625072015613332,0.15753407745397238,0.15753407745397238,0.1709749534198123,55.628561749999996,53.31899944,0,1.0433159349248282,342.28209500000014
tabular-MiniBooNE/greedy_entropy/ts2,tabular-MiniBooNE,greedy_entropy,,2,softmax,inverse_info,0.093792,0.15,100,100,0,100,0,0.7373737373737375,0.7373737373737375,0.7373737373737376,0.7373737373737375,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.13958867000000003,0.139913,0.13954680392114982,0.13954680392114988,0.13954680392114988,0.13954680392114988,0.13954680392114988,0.13954680392114988,0.010453196078850174,0.010453196078850119,0.13950493963053126,18.74471078176088,18.744710781760876,341.7321950600408,0.05485204804442707,0.05485204804442706,0.05485204804442706,0.05485204804442706,18.74295162,18.74295162,0,1.0,341.7321949999998
tabular-MiniBooNE/random/ts2,tabular-MiniBooNE,random,,2,softmax,inverse_info,0.093792,0.15,100,100,0,100,0,0.797979797979798,0.8080808080808082,0.8040404040404038,0.8080808080808082,0,0.0,0.0,0.03699480747600191,PASS,0,0.0,0.03699480747600191,PASS,0.14288963000000002,0.1405325,0.14291267112316597,0.14070008329239903,0.14070008329239903,0.14623155286931636,0.14070008329239903,0.14623155286931636,0.007087328876834026,0.0037684471306836387,0.14293571126217325,60.34918547830741,62.23650894252333,341.7321950600408,0.17659789259160769,0.1821207069225323,0.1683136710952208,0.1821207069225323,60.343906929999996,57.33168412999999,0,1.0525402810977917,341.7321949999998
tabular-spambase/eps_greedy_eps0.25/ts0,tabular-spambase,eps_greedy_eps0.25,0.25,0,softmax,inverse_info,0.054348,0.15,100,100,0,100,0,0.6767676767676768,0.7171717171717172,0.7203030303030304,0.7777777777777778,0,0.0,0.0,0.03699480747600191,PASS,9,0.09,0.16226374696643667,FAIL,0.12688396000000002,0.128019,0.1257910628019324,0.12741545893719808,0.10628019323671498,0.1461352657004831,0.11343599033816426,0.14009661835748793,0.024208937198067604,0.003864734299516892,0.12469816560386476,45.32606349504132,44.44411982249095,413.77665369817595,0.10954234147802798,0.10741089287002195,0.08514368856831071,0.1352375072824443,45.29869205999999,32.67941469,0,1.386153714492981,413.7766540000002
tabular-spambase/eps_greedy_eps0.5/ts0,tabular-spambase,eps_greedy_eps0.5,0.5,0,softmax,inverse_info,0.054348,0.15,100,100,0,100,0,0.696969696969697,0.7272727272727273,0.7273737373737376,0.7575757575757577,0,0.0,0.0,0.03699480747600191,PASS,5,0.05,0.11175196527208817,FAIL,0.12520527,0.124396,0.1245772946859903,0.12439613526570048,0.10446859903381643,0.14009661835748793,0.11292270531400966,0.13550724637681158,0.025422705314009697,0.00990338164251206,0.12394931937198059,49.412006457090754,49.30829170823225,413.77665369817595,0.11941709619299523,0.11916644225220001,0.10293264059173161,0.13508542586977604,49.302061710000004,37.44978006,0,1.3164846797767815,413.7766540000002
tabular-spambase/greedy_entropy/ts0,tabular-spambase,greedy_entropy,,0,softmax,inverse_info,0.054348,0.15,100,100,1,100,0,0.6464646464646465,0.7272727272727273,0.7102020202020205,0.7777777777777778,0,0.0,0.0,0.03699480747600191,PASS,3,0.03,0.08452078080402699,PASS,0.12548309000000002,0.123188,0.12519323671497584,0.12318840579710146,0.10990338164251208,0.13526570048309178,0.11473429951690821,0.13526570048309178,0.024806763285024153,0.014734299516908217,0.12490338342995166,37.93253646422979,36.38670223239195,413.77665369817606,0.09167394082098015,0.08793802624479086,0.06470622503427341,0.12121527539294803,37.80290888,23.6294652,0,1.5998207559940882,413.7766540000002
tabular-spambase/random/ts0,tabular-spambase,random,,0,softmax,inverse_info,0.054348,0.15,100,100,0,100,0,0.7676767676767677,0.787878787878788,0.7912121212121209,0.8282828282828284,0,0.0,0.0,0.03699480747600191,PASS,11,0.11,0.18631463027903022,FAIL,0.12577296000000002,0.12379200000000001,0.12475241545893717,0.12439613526570048,0.10628019323671498,0.14070048309178743,0.11627415458937199,0.14070048309178743,0.025247584541062823,0.009299516908212568,0.12373187091787431,86.10780152535088,84.55823480831693,413.77665369817606,0.2081021264872065,0.2043571913798617,0.17515899244190541,0.23086140542980782,86.15956746999998,69.50252730999999,0,1.2396609275185795,413.7766540000002
tabular-spambase/greedy_entropy/ts1,tabular-spambase,greedy_entropy,,1,softmax,inverse_info,0.070652,0.15,100,100,0,100,0,0.7070707070707072,0.787878787878788,0.7798989898989896,0.8181818181818182,0,0.0,0.0,0.03699480747600191,PASS,10,0.1,0.1743673043676654,FAIL,0.12306758000000001,0.120773,0.1232427536231884,0.12258454106280194,0.10507246376811594,0.14855072463768115,0.1111111111111111,0.13828502415458938,0.026757246376811594,0.0014492753623188415,0.1234179272463768,73.88261240336494,75.67478637317964,425.41080497021073,0.17367356809035106,0.17788637591957437,0.15642281884680867,0.18954310684534614,73.69477878,62.89751749,0,1.1716643473522883,425.410805
tabular-spambase/random/ts1,tabular-spambase,random,,1,softmax,inverse_info,0.070652,0.15,100,100,0,100,0,0.7474747474747475,0.7777777777777778,0.7795959595959593,0.8181818181818182,0,0.0,0.0,0.03699480747600191,PASS,6,0.06,0.12476968531222507,FAIL,0.12510869,0.125,0.1246316425120773,0.12560386473429952,0.09842995169082126,0.14371980676328502,0.11548913043478261,0.13526570048309178,0.025368357487922696,0.00628019323671497,0.1241545950241546,86.32156928569691,84.79499013773172,425.4108049702108,0.2029134386742752,0.19932495636463546,0.1748331382990565,0.2281857419616113,86.19348533,68.11300255,0,1.2654483300266726,425.410805
tabular-spambase/greedy_entropy/ts2,tabular-spambase,greedy_entropy,,2,softmax,inverse_info,0.065217,0.15,100,100,0,100,0,0.797979797979798,0.8585858585858587,0.8591919191919192,0.8989898989898991,0,0.0,0.0,0.03699480747600191,PASS,3,0.03,0.08452078080402699,PASS,0.12252414000000002,0.121981,0.12330314009661836,0.12258454106280194,0.10628019323671498,0.14070048309178743,0.11259057971014493,0.13707729468599034,0.026696859903381637,0.009299516908212568,0.1240821401932367,69.65617290215836,67.281078414424,408.07828004575117,0.17069316429766598,0.1648729709576331,0.13243944009862801,0.21741832554565435,69.23846777,36.22079671,0,1.911566670505741,408.07828000000006
tabular-spambase/random/ts2,tabular-spambase,random,,2,softmax,inverse_info,0.065217,0.15,100,100,0,100,0,0.787878787878788,0.8080808080808082,0.8130303030303029,0.8484848484848485,0,0.0,0.0,0.03699480747600191,PASS,1,0.01,0.0544875247609346,PASS,0.12083335000000002,0.120773,0.1222403381642512,0.12258454106280194,0.10628019323671498,0.14070048309178743,0.11231884057971014,0.1322463768115942,0.027759661835748795,0.009299516908212568,0.12364732632850237,85.74114424601315,83.41455762163584,408.07828004575106,0.21010955112925986,0.20440822680463155,0.18869695806907896,0.24602839344670102,85.24749676000002,66.76213428,0,1.2768839354726516,408.07828000000006
```

### 3.1 Row identifier fields
All present in the CSV (`cell` ... `primary`). Threshold-grid size = 100 for
every cell; committed floor and alpha at 6 decimals from the committed
configs. Primary rows (primary = 1): the four greedy_entropy/ts0/softmax
cells. All other rows are robustness (eps-greedy, seeds 1-2, margin score).

### 3.2 Certification and fallback fields
- Certified thresholds: **100/100 in every cell** (`certified` column).
- Full-acquisition fallbacks: **0 in every cell** (`fallbacks`).
- Abstentions/refusals (implementation term: `abstained` per resplit;
  `abstentions` in the gate CSV): **0 everywhere**.
- Threshold summaries (`lam_min/med/mean/max`): computed here from the exact
  per-resplit `lambda_idx` in `pool_stratum_resplits.csv` mapped through the
  stored grid; they are not stored as scalars in any canonical artifact
  (that fact itself: threshold summaries per cell NOT STORED; computable, and
  computed, from the exact per-resplit artifact as stated).

### 3.3 Full-pool gate fields
All present (`pool_viol_count/rate`, `pool_lo` = Wilson lower, `pool_hi` =
Wilson upper, `pool_gate`). Only one violating resplit exists in the entire
canonical grid:

- **Cell mnist/greedy_entropy/ts1, resplit index 67 (0-based).**
  Selected lambda_idx = 83, lambda = 0.8383838383838385;
  full-pool risk = 0.20007936507936508 (an exact count: 5,042 errors /
  25,200 pool examples), alpha = 0.2, excess = 7.936507936506798e-05
  (= 2/25,200 -- two examples above the target);
  test-half risk (stored, 6 dp) = 0.206825;
  calibration-half risk (derived by the exact identity from the unrounded
  pool value and the rounded test value) = 0.1933337;
  pool cost = 24.611031746031745 raw units = 0.5022659540006479 of full
  acquisition. Maximum excess over alpha in any cell = this resplit's
  7.94e-05.

### 3.4 Risk summaries
All computed from the exact per-resplit `agg_pool_risk` (unrounded) except:
mean/median test-half risk (from stored 6-dp realized values -- exact to the
stored precision) and mean calibration risk (derived via the identity; see
header note). **Median calibration risk: NOT FOUND** (per-resplit calibration
risks are not stored in metrics JSONs, pool_stratum_resplits.csv, or
validity_diagnostic.csv). Mean safety margin (`mean_margin`) and minimum
margin (`min_margin`) are in the CSV; the only negative minimum margin in the
grid is mnist/greedy_entropy/ts1 (-7.94e-05, the single violation).

### 3.5 Historical test-half diagnostic fields (superseded -- do not mix with the pool gate)
In the CSV: `test_viol_count`, `test_viol_rate`, `test_hi`, `test_gate`.
These are the OLD estimand. 11 of 35 cells "FAIL" that historical test-half
gate (mnist/eps0.25 ts0, mnist/eps0.5 ts0, mnist/greedy ts2, mnist/random
ts1, MiniBooNE/eps0.25 ts0, MiniBooNE/greedy ts1, spambase/greedy ts1,
spambase/random ts0, spambase/random ts1, spambase/eps0.25 ts0,
spambase/eps0.5 ts0). They are **explicitly marked superseded**: Phase 5.2
(`POOL_RISK_GATE.md`) demonstrates the mechanism (complementary halves of a
finite pool give corr(R_cal, R_test) = -1.0000 exactly, measured -1.0000 on
all 35 cells), and `project_update.md` Section 15 + RESULTS_FOR_PAPER
Section 15 record the supersession. Total test-half "violations" across
3,500 runs: 96 (sum of the test_viol_count column) -- a diagnostic count
only.

### 3.6 Acquisition-cost fields
- **Definition of selected-rule cost:** for resplit i, cost = mean over pool
  examples of the cumulative acquired-feature cost at the stop index induced
  by lambda_hat_i under the cell's primary cost scheme (cumulative cost
  matrix `cum_cost_from_order(order, feature_costs)`; stop =
  first grid crossing of the readiness score, else T).
- **Evaluated on:** the `mean_pool_cost/med_pool_cost/..._over_full` columns
  are FULL-POOL costs (from `pool_stratum_resplits.csv`); `mean_test_cost`
  and the oracle comparison are TEST-HALF costs (metrics JSONs, the
  H2/manuscript convention). Costs are nearly estimand-insensitive (e.g.
  MNIST primary: pool 24.8551 vs test-half 24.8471).
- **Full-acquisition cost** (`full_pool_cost`, raw units; derived exactly as
  stated in the header): MNIST 49.0 (uniform, T = 49); Adult
  95.2779627559329 (ts0), 94.2155 (ts1), 93.4266 (ts2); MiniBooNE 341.0632
  (ts0), 342.2821 (ts1), 341.7322 (ts2); Spambase 413.7767 (ts0), 425.4108
  (ts1), 408.0783 (ts2). (Inverse-information costs depend on the train
  seed's mutual-information estimates, hence the per-seed differences.)
- **Normalized cost** (`mean/med/p5/p95_cost_over_full`) in the CSV.
- **Standard error / CI for costs: NOT FOUND** (not stored; per-resplit pool
  costs are in `pool_stratum_resplits.csv` if an SE is ever needed).
- **Cheapest-valid oracle:** `oracle_cheapest_valid_select` -- per resplit,
  the cheapest grid threshold whose realized TEST-HALF risk is <= alpha,
  selected using the test half's labels (retrospective; Section 7.5).
  `oracle_test_mean_cost` = mean over 100 resplits of its realized test-half
  cost; `cost_over_oracle_testhalf` = (CAFA mean test-half cost) / (oracle
  mean test-half cost). **Oracle undefined in 0 resplits of all 35 cells**
  (`oracle_none_count` = 0 everywhere).
- **Scheme verification:** MNIST cells use `uniform` as primary (confirmed in
  all 9 MNIST rows); all tabular cells use `inverse_info` as primary
  (confirmed in all 26 tabular rows). **No canonical marginal cell uses the
  random-cost scheme as its primary scheme.** The random scheme exists as a
  secondary scheme inside the tabular metrics JSONs (robustness), but no
  Section-3 row and no gate row is based on it.

---

## 4. Marginal-result aggregate checks

All recomputed from the exact 35 rows above:

1. Cells with 0/100 full-pool violations: **34**.
2. Cells with >= 1 violation: **1**.
3. Total full-pool violations across 3,500 runs: **1**.
4. Maximum cell-level violation rate: **0.01** (mnist/greedy_entropy/ts1).
5. Largest full-pool Wilson upper bound: **0.054488** (that same cell; every
   other cell has UB 0.036995 at 0/100).
6. Cells passing the final gate: **35**.
7. Cells failing: **0**.
8. Nonzero-violation cell: **mnist/greedy_entropy/ts1** (only).
9. Violating resplit: the single resplit detailed in Section 3.3 (resplit 67,
   lambda = 0.838384, pool risk 0.200079365 = 5,042/25,200, excess 2 examples).
10. Marginal fallbacks/refusals across 3,500 runs: **0**.
11. Normalized-cost range across the 35 cells (mean pool cost / full):
    **0.034095 (MiniBooNE/greedy/ts1) to 0.738630 (mnist/greedy/ts2)**.
12. Cost/oracle range across the 35 cells (test-half convention):
    **1.000000 to 1.911567** (max: spambase/greedy/ts2; several cells sit at
    exactly 1.0 where CAFA's selected threshold coincides with the oracle's).
13. Dataset-level normalized-cost ranges: MNIST 0.4414-0.7386 (9 cells);
    Adult 0.2005-0.3612 (9); MiniBooNE 0.0341-0.1766 (9);
    Spambase 0.0917-0.2101 (8).
14. Policy-level normalized-cost ranges: greedy_entropy 0.0341-0.7386 (15);
    random 0.1625-0.6124 (12); eps-greedy(0.25) 0.0616-0.4550 (4);
    eps-greedy(0.5) 0.0878-0.4414 (4).
15. Margin vs matched max-softmax (greedy, ts0; mean pool risk / mean
    cost-over-full):
    - MNIST: softmax 0.141452 / 0.5072 vs margin 0.142227 / 0.5089
      (margin +0.0008 risk, +0.3% cost);
    - Adult: softmax 0.161241 / 0.3612 vs margin 0.161179 / 0.3551
      (margin -0.00006 risk, -1.7% cost);
    - MiniBooNE: softmax 0.132563 / 0.0499 vs margin 0.132563 / 0.0499
      (identical selected rule; both scores map to the same stop set).
    Conclusion supported: the certificate and its cost are insensitive to
    the readiness-score swap at these cells.
16. Epsilon-greedy vs matched greedy/random (ts0; mean pool risk / cost/full):
    - MNIST: greedy 0.1415/0.5072; eps0.25 0.1420/0.4550; eps0.5
      0.1416/0.4414; random 0.1417/0.5287. (Both eps cells are *cheaper*
      than pure greedy here.)
    - MiniBooNE: greedy 0.1326/0.0499; eps0.25 0.1430/0.0616; eps0.5
      0.1418/0.0878; random 0.1432/0.1657 (cost rises monotonically with
      randomness).
    - Adult: greedy 0.1612/0.3612; eps0.25 0.1653/0.3403; eps0.5
      0.1717/0.3214; random 0.1830/0.2773 (cost falls but risk climbs
      toward alpha = 0.2 as randomness increases).
    - Spambase: greedy 0.1252/0.0917; eps0.25 0.1258/0.1095; eps0.5
      0.1246/0.1194; random 0.1248/0.2081.
    Validity is unchanged in all eps cells (0/100 violations).
17. Cross-seed stability (greedy cells; alpha / mean pool risk / cost/full /
    violations):
    - MNIST: ts0 0.15/0.1415/0.5072/0; ts1 0.20/0.1906/0.5287/1;
      ts2 0.15/0.1382/0.7386/0.
    - MiniBooNE: ts0 0.15/0.1326/0.0499/0; ts1 0.15/0.1427/0.0341/0;
      ts2 0.15/0.1395/0.0549/0.
    - Adult: ts0 0.20/0.1612/0.3612/0; ts1 0.25/0.1644/0.3098/0;
      ts2 0.20/0.1865/0.2094/0.
    - Spambase: ts0 0.15/0.1252/0.0917/0; ts1 0.15/0.1232/0.1737/0;
      ts2 0.15/0.1233/0.1707/0.
    Risk always stays below the (seed-specific) alpha; cost varies by up to
    ~1.7x across seeds of the same dataset (MNIST 0.51 -> 0.74; Spambase
    0.09 -> 0.17) because the committed alpha and the backbone differ per
    seed. No seed produces a gate failure.
18. Wording resolution -- see the contradiction check.

### Required contradiction check

Resolved from the final per-resplit artifact (`pool_stratum_resplits.csv`,
cross-checked against `pool_risk_gate.csv`):

- **CORRECT:** "34 of 35 cells have 0/100 full-pool violations; one cell
  (mnist/greedy_entropy/ts1) has 1/100 (Wilson 95% UB 0.0545). All 35 cells
  pass the precommitted gate (Wilson UB <= 0.10)."
- "0 of 35 cells violate" / "every cell 0.000": **FALSE as a violation-count
  statement; superseded.** The true statement with "0/35" in it is only:
  "0/35 cells FAIL the pool-risk gate" (the POOL_RISK_GATE.md headline, which
  is about gate verdicts, not violation counts, and remains correct).
- The manuscript sentence "in every cell, the selected threshold exceeds
  alpha on the exact evaluation pool in 0 of 100 resplits (95% Wilson upper
  bound 0.037)": **FALSE; must be reworded** (already flagged as blocking
  issue C10 in `reviewphase_0_1_reply.md`, with the exact replacement
  sentence provided there).

---

## 5. Primary four-dataset marginal summary

Primary cell per dataset = (greedy_entropy, ts0, max-softmax readiness,
primary cost scheme, 100 resplits, grid 100); verified in the Section 3 CSV
(`primary` = 1 rows). All values below from those four rows.

| quantity | MNIST | Adult | MiniBooNE | Spambase |
|---|---:|---:|---:|---:|
| cost scheme | uniform | inverse_info | inverse_info | inverse_info |
| committed alpha | 0.15 | 0.20 | 0.15 | 0.15 |
| mean pool risk | 0.14145159 | 0.16124079 | 0.13256306 | 0.12519324 |
| median pool risk | 0.14238095 | 0.16124079 | 0.13256306 | 0.12318841 |
| pool violations / 100 | 0 | 0 | 0 | 0 |
| Wilson 95% UB | 0.036995 | 0.036995 | 0.036995 | 0.036995 |
| mean cost / full (pool) | 0.507247 | 0.361215 | 0.049950 | 0.091674 |
| cost / oracle (test-half) | 1.034122 | 1.000000 | 1.000000 | 1.599821 |
| mean selected threshold | 0.860101 | 0.777778 | 0.717172 | 0.710202 |
| median selected threshold | 0.858586 | 0.777778 | 0.717172 | 0.727273 |
| full-acq. risk (test-half mean over 100 resplits; diagnostic) | 0.085591 | 0.150971 | 0.083459 | 0.061389 |
| full-acq. cost (raw units, pool) | 49.0 | 95.277963 | 341.063216 | 413.776654 |

- **Full-acquisition risk on the evaluation pool as a stored exact scalar:
  NOT FOUND** (searched pool_risk_gate.csv, pool_stratum_eval.csv,
  validity_diagnostic.csv, metrics JSONs; the gate script computes
  `r_pool_full` internally but does not write it). The table gives the
  100-resplit test-half mean (each test half is half the pool; the exact
  pool value is recomputable from the frozen pool caches, and per-stratum
  pool endpoints exist in the family-wide artifacts).
- **Headline values currently quoted in the main paper** (per the C12 audit
  row in `reviewphase_0_1_reply.md`, verified there as matching canonical):
  Table 2 costs 0.507 / 0.050 / 0.361 / 0.091 of full; oracle 0.490 / 0.050 /
  0.361 / 0.057; "5-51%" of full acquisition; "within 3.5% of oracle"
  (1.0347); "~1.60x" for Spambase (1.596). Plus the marginal-gate sentence
  that must be reworded (Section 4 above).

**Aggregate-claim verification:**

- "Selected cost between ~5% and 51% of full acquisition": **SUPPORTED for
  the four primary cells** -- exact pool values 0.049950 (MiniBooNE),
  0.091674 (Spambase), 0.361215 (Adult), 0.507247 (MNIST), i.e. 5.0%-50.7%.
  NOT true of all 35 cells (range 3.4%-73.9%); S6 must scope the sentence to
  the primary cells or quote the 35-cell range.
- "Cost/oracle between ~1.000 and 1.034": **DO NOT CLAIM for all four
  primaries.** Exact: MNIST 1.0341, Adult 1.0000, MiniBooNE 1.0000, Spambase
  1.5998. The 1.000-1.034 range holds only for MNIST/Adult/MiniBooNE; the
  manuscript's own wording ("within 3.5% ... ~1.60x on Spambase") is the
  correct form. (RESULTS_FOR_PAPER's parenthetical "cost/oracle 1.000-1.034
  at ts0" is imprecise on this point -- CONFLICT with the per-cell artifact;
  the per-cell values above are authoritative.)
- "Fixed-confidence baselines cost ~1.5-8x more": **SUPPORTED at t = 0.95**
  with a rounding caveat -- exact cost-vs-CAFA multiples 1.4630 (MNIST),
  1.6395 (Adult), 7.7881 (MiniBooNE), 3.8387 (Spambase); the low end is 1.46,
  which "approximately 1.5" covers. At t = 0.90 the range is 1.17-5.20; at
  t = 0.99 it is 1.84-12.25 (Section 7.2). The claim must name t = 0.95.
- "No fallback on the canonical 35 cells": **SUPPORTED** -- 0 abstentions in
  3,500 runs (Sections 1.7, 4.10).

---

## 6. Baseline definitions

All implemented in `src/cafa/baselines.py` (docstrings quoted from source);
run per resplit by `scripts/run_eval_sweep.py`; evaluated on ALL 35 cells
(every method has a block in every resplit of every metrics JSON). Grid =
the same 100-point readiness grid everywhere. "Certified" below means
"carries a distribution-free guarantee."

1. **CAFA-marginal** (code `cafa_marginal`; paper: the marginal certificate).
   Selection: frozen `ltt_select` (HB p-values + fixed-sequence FWER) on the
   calibration half's loss/cost trajectories; among certified thresholds,
   minimize expected cost. Uses calibration labels. Fallback: full
   acquisition when no threshold certifies (never triggered). Certified:
   yes (P(risk > alpha) <= delta = 0.1). Deployable: yes.
2. **Plug-in selector** (code `plugin`). Selection: cheapest grid index whose
   *empirical calibration risk* <= alpha -- "with no correction for having
   tested the whole grid" (docstring). Uses calibration labels. Tie-break:
   `argmin` of expected cost over valid indices; ties resolve to the lowest
   grid index. Fallback: None (-> full acquisition) if no column's empirical
   risk <= alpha; never triggered in canonical cells (0 fallbacks in
   pool_plugin_eval.csv). Certified: no. Deployable: yes (but uncertified).
3. **Fixed-confidence selector** (code `fixed_conf_{t}`, t in {0.90, 0.95,
   0.99} from the experiment config). Selection: grid index closest to t
   (`argmin |grid - t|`, ties -> lowest index); **ignores calibration data
   entirely**; uses no labels. No fallback (always defined). Certified: no.
   Deployable: yes.
4. **Fixed-budget selector** (code `budget_{k}`, k in {5, 10, 20} raw
   feature-count depths, clamped to T). Every instance stops at depth k;
   no threshold, no labels, no fallback. Certified: no. Deployable: yes.
5. **Cheapest-valid oracle** (code `oracle_cheapest`). Selection: cheapest
   grid index whose realized TEST-HALF risk <= alpha, computed per resplit
   from the test half's labels -- **retrospective, not deployable** ("the
   lowest cost any threshold rule could pay while still honouring alpha in
   truth; a deployable method can only approach this from above").
   Tie-break: lowest-cost, then lowest index. Returns None if alpha is
   infeasible on the test half (never occurred: 0 of 3,500 across all cells).
6. **Full-acquisition oracle/endpoint** (code `oracle_full`). All features
   acquired: risk = mean(1 - correct[:, T]), cost = mean cumulative cost at
   T. Not a selector; the risk floor / cost ceiling reference. Retrospective
   labels not needed for the rule itself (it is data-independent), but its
   risk readout uses labels.

**Risk/cost estimand per baseline in the canonical artifacts:** all six have
per-resplit TEST-HALF realized risk/cost in the metrics JSONs for all 35
cells (100 resplits each). **On the final full-pool estimand, results exist
only for cafa_marginal (pool gate + pool_stratum artifacts) and plugin
(pool_plugin_eval.csv), for all 35 cells.** Fixed-confidence, fixed-budget,
and the oracles have NO stored pool-estimand evaluation (searched
results_committed/*.csv and *.md) -- their comparison values below are
test-half; for the data-independent rules (fixed-conf, budget, oracle_full)
the pool risk is a deterministic constant recomputable from the frozen pool
caches, but it is NOT in the frozen artifacts. Current vs superseded:
pool-estimand numbers (cafa_marginal, plugin) are current; every per-method
violation count from the test-half blocks is a superseded diagnostic and is
labeled as such below.

---

## 7. Baseline comparison values

### 7.1 Per-dataset fields (primary cells, primary scheme, 100 resplits each)

Fenced CSV, extracted from the metrics JSONs (test-half estimand) plus the
plugin pool rows from `pool_plugin_eval.csv`. `testhalf_viol` = count of
resplits with realized test-half risk > alpha (DIAGNOSTIC, superseded, except
in the two `plugin (POOL estimand)`-style rows where the column holds the
POOL exceed count). `cost_over_full/cafa/oracle` are ratios of mean test-half
costs. Eligible = 100 and selection fallbacks = 0 for every method on every
primary cell (verified; plugin fallbacks 0, oracle undefined 0).

```csv
dataset,method,estimand,eligible,viol_count,mean_risk,med_risk,mean_cost,cost_over_full,cost_over_cafa,cost_over_oracle
mnist,cafa_marginal,test-half,100,2,0.14142696,0.1420635,24.84706109,0.50708288,1.0,1.03412173
mnist,plugin,test-half,100,35,0.14667695,0.149127,24.08199836,0.49146935,0.96920913,1.00228022
mnist,fixed_conf_0.9,test-half,100,0,0.11854049,0.118373,28.98737781,0.59157914,1.16663205,1.20643955
mnist,fixed_conf_0.95,test-half,100,0,0.09413415,0.094008,36.35050474,0.74184704,1.46296999,1.51288906
mnist,fixed_conf_0.99,test-half,100,0,0.08575632,0.0856745,45.60284133,0.93067023,1.83534146,1.89796648
mnist,budget_5,test-half,100,100,0.54182934,0.5414285,5.0,0.10204082,0.20123104,0.20809739
mnist,budget_10,test-half,100,100,0.38341669,0.383254,10.0,0.20408163,0.40246208,0.41619479
mnist,budget_20,test-half,100,100,0.27013575,0.270357,20.0,0.40816327,0.80492417,0.83238957
mnist,oracle_cheapest,test-half,100,0,0.1469151,0.146984,24.02721109,0.49035125,0.96700415,1.0
mnist,oracle_full,test-half,100,0,0.08559053,0.085476,49.0,1.0,1.97206421,2.03935446
mnist,plugin_POOL,full-pool,100,0,0.14668095,0.14920635,24.09072976,0.49164755,,
tabular-adult,cafa_marginal,test-half,100,0,0.16142998,0.161548,34.35980669,0.36062701,1.0,1.0
tabular-adult,plugin,test-half,100,0,0.16142998,0.161548,34.35980669,0.36062701,1.0,1.0
tabular-adult,fixed_conf_0.9,test-half,100,0,0.1599779,0.159705,42.12028168,0.4420779,1.2258591,1.2258591
tabular-adult,fixed_conf_0.95,test-half,100,0,0.15345338,0.15344,56.33168846,0.59123523,1.63946465,1.63946465
tabular-adult,fixed_conf_0.99,test-half,100,0,0.15146687,0.151474,77.12165672,0.80943856,2.24453116,2.24453116
tabular-adult,budget_5,test-half,100,100,0.21262168,0.212715,30.14952081,0.3164375,0.8774648,0.8774648
tabular-adult,budget_10,test-half,100,0,0.17027518,0.1704545,68.34658688,0.71733888,1.98914352,1.98914352
tabular-adult,budget_20,test-half,100,0,0.15097054,0.1510445,95.277963,1.0,2.77294817,2.77294817
tabular-adult,oracle_cheapest,test-half,100,0,0.16142998,0.161548,34.35980669,0.36062701,1.0,1.0
tabular-adult,oracle_full,test-half,100,0,0.15097054,0.1510445,95.277963,1.0,2.77294817,2.77294817
tabular-adult,plugin_POOL,full-pool,100,0,0.16124079,0.16124079,34.41586916,0.36121542,,
tabular-MiniBooNE,cafa_marginal,test-half,100,0,0.13271973,0.132673,17.01220028,0.0498799,1.0,1.0
tabular-MiniBooNE,plugin,test-half,100,0,0.13271973,0.132673,17.01220028,0.0498799,1.0,1.0
tabular-MiniBooNE,fixed_conf_0.9,test-half,100,0,0.09073337,0.0906625,88.40467173,0.25920318,5.19654544,5.19654544
tabular-MiniBooNE,fixed_conf_0.95,test-half,100,0,0.08520099,0.085259,132.49330821,0.38847141,7.78813475,7.78813475
tabular-MiniBooNE,fixed_conf_0.99,test-half,100,0,0.083559,0.083593,208.45397445,0.61118867,12.25320482,12.25320482
tabular-MiniBooNE,budget_5,test-half,100,0,0.14649781,0.146341,24.27924228,0.07118693,1.4271665,1.4271665
tabular-MiniBooNE,budget_10,test-half,100,0,0.11012637,0.110119,55.52137069,0.16278909,3.2636208,3.2636208
tabular-MiniBooNE,budget_20,test-half,100,0,0.09945074,0.0993975,125.46422845,0.36786209,7.374956,7.374956
tabular-MiniBooNE,oracle_cheapest,test-half,100,0,0.13271973,0.132673,17.01220028,0.0498799,1.0,1.0
tabular-MiniBooNE,oracle_full,test-half,100,0,0.08345861,0.083508,341.063216,1.0,20.04815429,20.04815429
tabular-MiniBooNE,plugin_POOL,full-pool,100,0,0.13256306,0.13256306,17.03601453,0.04994973,,
tabular-spambase,cafa_marginal,test-half,100,3,0.12548309,0.123188,37.80290888,0.09136066,1.0,1.59982076
tabular-spambase,plugin,test-half,100,45,0.14393721,0.138285,23.6745647,0.05721581,0.62626304,1.00190861
tabular-spambase,fixed_conf_0.9,test-half,100,0,0.06823673,0.067633,112.46652798,0.27180491,2.97507603,4.75958838
tabular-spambase,fixed_conf_0.95,test-half,100,0,0.06480677,0.06401,145.11452182,0.35070737,3.83871311,6.14125291
tabular-spambase,fixed_conf_0.99,test-half,100,0,0.0596739,0.059179,215.63822058,0.52114642,5.70427586,9.12581892
tabular-spambase,budget_5,test-half,100,91,0.16295893,0.163043,25.63364855,0.06195045,0.67808667,1.08481713
tabular-spambase,budget_10,test-half,100,0,0.1262078,0.125604,62.48598765,0.15101381,1.65294126,2.64440973
tabular-spambase,budget_20,test-half,100,0,0.11283814,0.112319,143.34919329,0.34644099,3.79201489,6.06654413
tabular-spambase,oracle_cheapest,test-half,100,0,0.14260865,0.14372,23.6294652,0.05710681,0.62507003,1.0
tabular-spambase,oracle_full,test-half,100,0,0.06138889,0.06099,413.776654,1.0,10.94563001,17.51104608
tabular-spambase,plugin_POOL,full-pool,100,45,0.14375604,0.1352657,23.68954271,0.057252,,
```

Interpretation notes required by 7.1:
- Adult and MiniBooNE: CAFA, plugin, and the cheapest-valid oracle select the
  SAME threshold in every resplit (identical rows) -- the HB margin costs
  nothing there.
- MNIST budget rows: risk crosses the target massively (0.27-0.54 vs alpha
  0.15 at every k <= 20) -- a fixed budget that is safe on one dataset
  (MiniBooNE) violates on another; there is no budget value that is
  simultaneously safe and competitive across datasets (nonmonotone
  cost-risk matching is impossible for a fixed k).
- Spambase plugin: cheaper than CAFA (0.626x) but unreliable -- 45/100 POOL
  exceedances of the committed target (see 7.4).

### 7.2 Fixed-confidence baseline
- Levels: t in {0.90, 0.95, 0.99} (experiment config `fixed_confidence_t`);
  the SAME grid for every dataset (no per-dataset setting).
- Shown in the paper: t = 0.95 (the H2/Table-2 column `fixed_conf_0.95`;
  RESULTS_FOR_PAPER Section 5).
- Exact cost multiples vs CAFA (test-half means):
  - t = 0.90: MNIST 1.1666, Adult 1.2259, MiniBooNE 5.1965, Spambase 2.9751.
  - t = 0.95: MNIST 1.4630, Adult 1.6395, MiniBooNE 7.7881, Spambase 3.8387.
  - t = 0.99: MNIST 1.8353, Adult 2.2445, MiniBooNE 12.2532, Spambase 5.7043.
- Risk/violations: 0/100 test-half violations at every t on every primary
  cell (mean risks in the CSV; all below alpha -- over-acquisition).
  Pool-estimand risk: NOT FOUND (deterministic rule; recomputable).

### 7.3 Fixed-budget baseline
- Budgets: k in {5, 10, 20}, RAW acquired-feature counts (uniform depth),
  clamped to T; not normalized.
- Displayed budget: budget_10 in the canonical H2 table (RESULTS_FOR_PAPER
  Section 5).
- Exact results: in the 7.1 CSV. Test-half target crossings: MNIST 100/100
  at ALL of k = 5, 10, 20; Adult 100/100 at k = 5; Spambase 91/100 at k = 5;
  MiniBooNE 0 at all k.
- Matching: comparisons are matched by NEITHER risk nor cost -- k is a fixed
  externally chosen depth; this is the point of the baseline (no way to pick
  k without labels).

### 7.4 Plug-in selector
- Full-pool committed-target exceed counts, primary cells (from
  `pool_plugin_eval.csv`, selection asserted equal to the recorded threshold
  on every resplit): **MNIST 0/100, Adult 0/100, MiniBooNE 0/100, Spambase
  45/100 [Wilson 95% CI 0.36, 0.55]**.
- Full-pool mean risk / cost-over-full (primary cells): MNIST 0.146681 /
  0.491648; Adult 0.161241 / 0.361215; MiniBooNE 0.132563 / 0.049950;
  Spambase 0.143756 / 0.057252.
- Seeds: the primary plugin rows use the primary seed (ts0); the
  all-35-cell plugin table (pool_plugin_eval.csv) covers the other seeds --
  worst cells overall: mnist/greedy/ts1 0.59 pool exceed, mnist margin ts0
  0.49, MiniBooNE eps0.5 0.49; 16 of 35 cells are labeled "clearly
  unreliable" and 19 "not shown unreliable at this resolution" (labels are
  descriptive benchmark classifications, criterion 0.10, NOT a guarantee;
  0/100 does not mean "safe").
- Defer to S9, not S6: the plugin's nonmonotone/estimand-sensitive
  reliability profile -- e.g. MNIST ts0 flips from 35/100 test-half
  exceedances to 0/100 on the pool while Spambase ts0 stays at 45/100 on
  both, and pool-vs-test differences range from -0.44 to +0.29 across
  cells. S6 should quote only the committed-target pool counts.
- Superseded test-half plugin headlines that must NOT appear in S6: "plugin
  violates in 35/100 (MNIST)" and any per-cell test-half violation
  fractions from h2_table.csv / older RESULTS sections (e.g. MNIST
  greedy ts0 0.35, Spambase random ts0 0.47); these are diagnostics.

### 7.5 Oracle quantities
- **Cheapest-valid oracle:** per resplit, the cheapest threshold in the
  100-point grid whose realized risk on THAT resplit's test half is
  <= alpha. Validity is therefore evaluated on the test half, NOT the fixed
  full pool; it is selected separately for every resplit; it reads the test
  half's labels, hence retrospective and non-deployable. Ties: lowest cost
  wins, residual ties to the lowest grid index. "Oracle cost" in every
  canonical table = the cheapest threshold satisfying the target (a
  threshold-family cost floor), NOT a cheapest audited/certified rule and
  NOT an unrestricted-policy optimum.
- **Full-feature oracle/endpoint:** all T features; risk floor and cost
  ceiling; used as the normalization denominator ("cost/full") and the
  fallback rule.
- Undefined cases: none (0/3,500 oracle_cheapest failures across all 35
  cells).

---

## 8. Candidate compact tables for S6

### 8.1 Candidate Table S4: all 35 marginal cells

Rounding used here (recommended, Section 9): alpha 2 dp; Wilson UB 4 dp;
cost ratios 3 dp. Certified and violation counts are exact integers.
Cost/full = mean pool cost / full pool cost; Cost/oracle = test-half
convention (state this in the caption).

| Dataset | Policy | Seed | Score | Cost scheme | Alpha | Cert/100 | Viol/100 | Wilson UB | Gate | Cost/full | Cost/oracle |
|---|---|---:|---|---|---:|---:|---:|---:|---|---:|---:|
| MNIST | eps-Greedy (0.25) | 0 | max-softmax | uniform | 0.15 | 100 | 0 | 0.0370 | PASS | 0.455 | 1.032 |
| MNIST | eps-Greedy (0.5) | 0 | max-softmax | uniform | 0.15 | 100 | 0 | 0.0370 | PASS | 0.441 | 1.027 |
| MNIST | Greedy | 0 | margin | uniform | 0.15 | 100 | 0 | 0.0370 | PASS | 0.509 | 1.043 |
| MNIST | Greedy | 0 | max-softmax | uniform | 0.15 | 100 | 0 | 0.0370 | PASS | 0.507 | 1.034 |
| MNIST | Greedy | 1 | max-softmax | uniform | 0.20 | 100 | 1 | 0.0545 | PASS | 0.529 | 1.026 |
| MNIST | Greedy | 2 | max-softmax | uniform | 0.15 | 100 | 0 | 0.0370 | PASS | 0.739 | 1.041 |
| MNIST | Random | 0 | max-softmax | uniform | 0.15 | 100 | 0 | 0.0370 | PASS | 0.529 | 1.020 |
| MNIST | Random | 1 | max-softmax | uniform | 0.20 | 100 | 0 | 0.0370 | PASS | 0.557 | 1.015 |
| MNIST | Random | 2 | max-softmax | uniform | 0.15 | 100 | 0 | 0.0370 | PASS | 0.612 | 1.026 |
| Adult | eps-Greedy (0.25) | 0 | max-softmax | inv-info | 0.20 | 100 | 0 | 0.0370 | PASS | 0.340 | 1.000 |
| Adult | eps-Greedy (0.5) | 0 | max-softmax | inv-info | 0.20 | 100 | 0 | 0.0370 | PASS | 0.321 | 1.000 |
| Adult | Greedy | 0 | margin | inv-info | 0.20 | 100 | 0 | 0.0370 | PASS | 0.355 | 1.000 |
| Adult | Greedy | 0 | max-softmax | inv-info | 0.20 | 100 | 0 | 0.0370 | PASS | 0.361 | 1.000 |
| Adult | Greedy | 1 | max-softmax | inv-info | 0.25 | 100 | 0 | 0.0370 | PASS | 0.310 | 1.123 |
| Adult | Greedy | 2 | max-softmax | inv-info | 0.20 | 100 | 0 | 0.0370 | PASS | 0.209 | 1.085 |
| Adult | Random | 0 | max-softmax | inv-info | 0.20 | 100 | 0 | 0.0370 | PASS | 0.277 | 1.000 |
| Adult | Random | 1 | max-softmax | inv-info | 0.25 | 100 | 0 | 0.0370 | PASS | 0.201 | 1.123 |
| Adult | Random | 2 | max-softmax | inv-info | 0.20 | 100 | 0 | 0.0370 | PASS | 0.231 | 1.007 |
| MiniBooNE | eps-Greedy (0.25) | 0 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.062 | 1.078 |
| MiniBooNE | eps-Greedy (0.5) | 0 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.088 | 1.041 |
| MiniBooNE | Greedy | 0 | margin | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.050 | 1.000 |
| MiniBooNE | Greedy | 0 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.050 | 1.000 |
| MiniBooNE | Greedy | 1 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.034 | 1.126 |
| MiniBooNE | Greedy | 2 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.055 | 1.000 |
| MiniBooNE | Random | 0 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.166 | 1.037 |
| MiniBooNE | Random | 1 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.163 | 1.043 |
| MiniBooNE | Random | 2 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.177 | 1.053 |
| Spambase | eps-Greedy (0.25) | 0 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.110 | 1.386 |
| Spambase | eps-Greedy (0.5) | 0 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.119 | 1.316 |
| Spambase | Greedy | 0 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.092 | 1.600 |
| Spambase | Greedy | 1 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.174 | 1.172 |
| Spambase | Greedy | 2 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.171 | 1.912 |
| Spambase | Random | 0 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.208 | 1.240 |
| Spambase | Random | 1 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.203 | 1.265 |
| Spambase | Random | 2 | max-softmax | inv-info | 0.15 | 100 | 0 | 0.0370 | PASS | 0.210 | 1.277 |

### 8.2 Candidate Table S5: primary baseline comparison

Constraint discovered in Section 6: **pool violation counts exist only for
CAFA-marginal and the plug-in.** For the label-free deterministic baselines
(fixed-conf, budget) and the oracle, only test-half diagnostics are frozen.
The candidate table below therefore has two violation columns -- the honest
rendering; a single "Pool violations / 100" column CANNOT be filled for all
methods from the frozen artifacts (see Section 11).

Rounding: risks 3 dp, cost ratios 2-3 dp. Methods shown: the paper's
comparison set (CAFA, plugin, fixed-conf 0.95, budget-10, oracle, full).

| Dataset | Method | Pool viol/100 | Test-half exceed/100 (diagnostic) | Mean risk | Cost/full | Cost/CAFA | Cost/oracle | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| MNIST | CAFA-marginal | 0 | 2 | 0.141 | 0.507 | 1.00 | 1.034 | certified, PASS |
| MNIST | Plug-in | 0 | 35 | 0.147 | 0.491 | 0.97 | 1.002 | uncertified |
| MNIST | Fixed-conf 0.95 | NOT FOUND | 0 | 0.094 | 0.742 | 1.46 | 1.513 | uncertified, over-acquires |
| MNIST | Budget-10 | NOT FOUND | 100 | 0.383 | 0.204 | 0.40 | 0.416 | uncertified, violates |
| MNIST | Oracle (cheapest-valid) | n/a | 0 | 0.147 | 0.490 | 0.97 | 1.000 | retrospective |
| MNIST | Full acquisition | n/a | 0 | 0.086 | 1.000 | 1.97 | 2.039 | endpoint |
| Adult | CAFA-marginal | 0 | 0 | 0.161 | 0.361 | 1.00 | 1.000 | certified, PASS |
| Adult | Plug-in | 0 | 0 | 0.161 | 0.361 | 1.00 | 1.000 | uncertified |
| Adult | Fixed-conf 0.95 | NOT FOUND | 0 | 0.153 | 0.591 | 1.64 | 1.639 | uncertified, over-acquires |
| Adult | Budget-10 | NOT FOUND | 0 | 0.170 | 0.717 | 1.99 | 1.989 | uncertified |
| Adult | Oracle (cheapest-valid) | n/a | 0 | 0.161 | 0.361 | 1.00 | 1.000 | retrospective |
| Adult | Full acquisition | n/a | 0 | 0.151 | 1.000 | 2.77 | 2.773 | endpoint |
| MiniBooNE | CAFA-marginal | 0 | 0 | 0.133 | 0.050 | 1.00 | 1.000 | certified, PASS |
| MiniBooNE | Plug-in | 0 | 0 | 0.133 | 0.050 | 1.00 | 1.000 | uncertified |
| MiniBooNE | Fixed-conf 0.95 | NOT FOUND | 0 | 0.085 | 0.388 | 7.79 | 7.788 | uncertified, over-acquires |
| MiniBooNE | Budget-10 | NOT FOUND | 0 | 0.110 | 0.163 | 3.26 | 3.264 | uncertified |
| MiniBooNE | Oracle (cheapest-valid) | n/a | 0 | 0.133 | 0.050 | 1.00 | 1.000 | retrospective |
| MiniBooNE | Full acquisition | n/a | 0 | 0.083 | 1.000 | 20.05 | 20.048 | endpoint |
| Spambase | CAFA-marginal | 0 | 3 | 0.125 | 0.091 | 1.00 | 1.600 | certified, PASS |
| Spambase | Plug-in | 45 | 45 | 0.144 | 0.057 | 0.63 | 1.002 | uncertified, unreliable |
| Spambase | Fixed-conf 0.95 | NOT FOUND | 0 | 0.065 | 0.351 | 3.84 | 6.141 | uncertified, over-acquires |
| Spambase | Budget-10 | NOT FOUND | 0 | 0.126 | 0.151 | 1.65 | 2.644 | uncertified |
| Spambase | Oracle (cheapest-valid) | n/a | 0 | 0.143 | 0.057 | 0.63 | 1.000 | retrospective |
| Spambase | Full acquisition | n/a | 0 | 0.061 | 1.000 | 10.95 | 17.511 | endpoint |

(Plug-in pool risks in this table: 0.147/0.161/0.133/0.144 from
pool_plugin_eval.csv; its mean-risk cells above use the pool values for the
plugin rows and test-half means elsewhere -- if a single-estimand table is
preferred, use test-half means everywhere and say so in the caption.)

**Can a four-dataset table represent the comparison faithfully?** Yes, with
two required additions: (i) budget_5's failures (MNIST 100/100, Adult
100/100, Spambase 91/100 test-half crossings) or a caption sentence noting
that no fixed budget is simultaneously safe and competitive across datasets
-- budget_10 alone makes the budget baseline look safe on 3 of 4 datasets;
(ii) a caption note that Spambase's plugin row (45/100 POOL exceedances,
committed target) is the reliability counterexample. Row-per-(dataset x
method) as above is sufficient; no extra datasets or cells are essential.

### 8.3 Optional condensed dataset summary

Cost/oracle is the test-half convention; ranges over that dataset's cells.

| Dataset | Marginal cells | Cells passing gate | Nonzero-violation cells | Cost/full range | Cost/oracle range |
|---|---:|---:|---:|---|---|
| MNIST | 9 | 9 | 1 | 0.441-0.739 | 1.015-1.043 |
| Adult | 9 | 9 | 0 | 0.201-0.361 | 1.000-1.123 |
| MiniBooNE | 9 | 9 | 0 | 0.034-0.177 | 1.000-1.126 |
| Spambase | 8 | 8 | 0 | 0.092-0.210 | 1.172-1.912 |

This table conceals nothing cell-level *except* the identity of the one
violating cell; if used, its caption must name mnist/greedy_entropy/ts1
(1/100, Wilson UB 0.054).

---

## 9. Rounding, display, and terminology

Recommended display precision (chosen so that no two distinct canonical
values collide and the deciding digits survive):
- probe floors: 4 dp (committed at 6; 4 suffices for display, e.g. 0.0779);
- alpha: 2 dp (all values are multiples of 0.05);
- violation rates: exact fractions "k/100" preferred over decimals;
- Wilson upper bounds: 3 dp minimum (0.037 vs 0.054 must be
  distinguishable; the gate margin to 0.10 is what matters);
- risks: 3 dp in tables (4 dp when comparing to alpha within 0.001; the
  single violation needs 4 dp or the exact fraction 2/25,200 to be visible);
- thresholds: 3 dp (grid spacing is 1/99 ~ 0.0101);
- normalized costs: 3 dp;
- cost ratios (vs CAFA / vs oracle): 2 dp for multiples > 1.5, 3 dp near 1
  (1.034 vs 1.000 requires 3 dp).

Canonical display names / abbreviations:
- datasets: MNIST, Adult, MiniBooNE, Spambase (code names: mnist,
  tabular-adult, tabular-MiniBooNE, tabular-spambase);
- greedy_entropy -> "Greedy (entropy)" or "Greedy";
- random -> "Random";
- eps_greedy_eps0.25 / eps0.5 -> "eps-Greedy (eps = 0.25)" / "(eps = 0.5)";
- softmax score -> "max-softmax readiness";
- margin score -> "margin readiness" (top-1 minus top-2 probability);
- inverse_info -> "inverse-information cost" (cost = 1 + 9(1 - normalized
  mutual information), range [1, 10]);
- random cost scheme -> "random cost" (robustness scheme; NOT used by any
  canonical marginal cell as primary);
- pool violation -> "full-pool violation" or "exceedance of alpha on the
  fixed evaluation pool";
- fallback -> "full-acquisition fallback"; implementation term "abstained"
  (refuse-and-acquire-everything). Use one term consistently; "abstention"
  = "fallback" here (the marginal rule never leaves an example unlabeled).

Inaccurate / prohibited terminology for S6:
- "independent test guarantee" -- PROHIBITED: the test half is exactly
  anti-correlated with the calibration half (corr = -1), not independent.
- "zero population violations" -- PROHIBITED: the pool is the population for
  this experiment by construction; there is no separate population estimate,
  and the count is 1, not 0.
- "oracle" without stating retrospective label access -- PROHIBITED; always
  "cheapest-valid oracle (retrospective, uses evaluation labels)".
- "all cells have zero violations" -- PROHIBITED: contradicted by the final
  artifact (mnist/greedy_entropy/ts1 has 1/100). Correct: "all cells pass
  the precommitted gate; 34/35 have zero violations."
- "the certificate is always valid" -- PROHIBITED without the finite-sample
  qualifier: the guarantee is P(risk > alpha) <= delta = 0.1 per
  calibration draw, and the observed 1/3,500 is consistent with (far below)
  that budget, not proof of impossibility.
- Also avoid: "guarantee holds on the test set" (superseded estimand), and
  any of the family-audit prohibited phrases (they concern S7-S9, not S6).

---

## 10. Exact claims that S6 may support

1. "All 35 canonical marginal cells pass the precommitted full-pool validity
   gate (Wilson 95% upper bound <= delta = 0.10)." -- **SUPPORTED.**
   35/35 PASS; largest UB 0.054488. Source: pool_risk_gate.csv.
2. "34/35 cells have zero full-pool violations in 100 resplits; one cell
   (MNIST, training seed 1, greedy) has exactly one." -- **SUPPORTED.**
   Counts recomputed from pool_stratum_resplits.csv; the violation is
   resplit 67, pool risk 0.2000794 vs alpha 0.2 (2 examples over, out of
   25,200). Sources: pool_risk_gate.csv + pool_stratum_resplits.csv.
3. "No marginal fallbacks across 3,500 calibration runs." -- **SUPPORTED.**
   abstentions = 0 in all 35 cells; every run returned a certified
   threshold. Sources: pool_risk_gate.csv, metrics JSONs.
4. "Selected acquisition cost ranges from ~5% to ~51% of full acquisition
   across the four primary cells (5.0% MiniBooNE, 9.2% Spambase, 36.1%
   Adult, 50.7% MNIST)." -- **SUPPORTED with the primary-cell scope stated.**
   DO NOT extend to all 35 cells without changing the range to 3.4%-73.9%.
   Source: pool_stratum_resplits.csv + pool_plugin_eval.csv normalization.
5. "The selected rule is within ~3.4% of the cheapest-valid oracle's cost."
   -- **DO NOT CLAIM as a four-dataset statement.** Exact primary values:
   MNIST 1.0341, Adult 1.0000, MiniBooNE 1.0000, Spambase **1.5998**. The
   supportable form: "within 3.5% of the oracle on MNIST/Adult/MiniBooNE
   and 1.60x on Spambase, where the certified margin forces a more
   conservative threshold." Source: metrics JSONs (test-half convention).
6. "Fixed-confidence selection is safe here but ~1.5-8x more expensive than
   CAFA (at t = 0.95: 1.46x MNIST, 1.64x Adult, 7.79x MiniBooNE, 3.84x
   Spambase)." -- **SUPPORTED with t = 0.95 named and 'safe' qualified**:
   0 test-half exceedances at every t on the primary cells, but the rule is
   uncertified (safety is empirical, not guaranteed; and it has no pool
   evaluation in the frozen artifacts). Source: metrics JSONs.
7. "Complementary-test-half failures are superseded diagnostics: the two
   halves of a finite pool are exactly anti-correlated (measured
   corr = -1.0000 on all 35 cells), so test-split gates over-report; the
   final gate evaluates the exact pool risk." -- **SUPPORTED.** Source:
   POOL_RISK_GATE.md.
8. "The full-pool results do not constitute an independent population-risk
   estimate; the pool is the population for this experiment, and the LTT
   certificate covers this estimand because a without-replacement sample's
   empirical mean is dominated by its binomial counterpart." --
   **SUPPORTED** (and required as a scope statement; the manuscript-side
   wording addition is already specified in reviewphase_0_1_reply.md,
   estimand paragraph). Source: pool_risk_gate.py header.

---

## 11. Missing information and author decisions

**Missing numerical values (do not block S6 if the tables above are used):**
1. Pool-estimand risk/violation values for fixed-confidence, fixed-budget,
   and oracle baselines -- only test-half diagnostics are frozen (Section 6).
   These rules are data-independent per cell, so their pool risks are
   deterministic constants recomputable from the frozen pool caches, but
   they are NOT in `results_committed/`.
2. Exact full-acquisition risk on the evaluation pool as a stored scalar
   (only the 100-resplit test-half mean and per-stratum endpoints are
   frozen) -- Section 5.
3. Median calibration-half risk per cell (per-resplit calibration risks not
   stored) -- Section 3.4.
4. Cost standard errors (per-resplit pool costs exist; no SE was frozen).

**Conflicting artifacts:** RESULTS_FOR_PAPER's "cost/oracle 1.000-1.034 at
ts0" omits Spambase (1.5998) -- resolved here in favor of the per-cell
artifact; the manuscript's own "within 3.5% ... ~1.60x" wording is correct.
The manuscript's "0 of 100 in every cell" marginal sentence conflicts with
pool_risk_gate.csv -- resolved (34/35 + 1/100); rewording already specified
in reviewphase_0_1_reply.md (C10).

**Unclear gate semantics:** none remaining -- Section 2 pins the estimand,
comparison, CI, and criterion from source.

**Unclear baseline definitions:** none remaining -- Section 6 quotes the
implementations.

**Unclear table scope (author decisions):**
1. Whether Candidate Table S5 shows a single "Pool violations / 100" column
   (then fixed-conf/budget cells read NOT FOUND or the column must be
   computed) or the two-column rendering used in Section 8.2 (pool where
   frozen, test-half exceedances labeled as diagnostic). Two-column is
   recommended; it requires no new compute.
2. Whether Table S4 quotes cost/oracle (test-half convention) in the same
   row as pool-based cost/full -- if yes, the caption must state the two
   conventions (as done in 8.1).
3. Whether the condensed 8.3 table replaces or supplements the full 8.1
   table (8.1 is required by the "no omitted cells" instruction if only one
   is kept).

**Results existing only in superseded test-half form:** all baseline
violation counts except the plugin's; CAFA test-half violation counts
(kept as diagnostics, Section 3.5).

**Author choices not recoverable from the repository:** none for S6 beyond
the table-scope items above.

### Verdict

`S6 SOURCE MATERIAL INCOMPLETE`

Minimum actions to complete:
1. DECIDE the Table-S5 violation-column rendering (author decision 1). If
   the two-column diagnostic rendering in Section 8.2 is accepted, no new
   computation is needed and this item closes immediately.
2. ONLY IF a uniform pool-violation column is required instead: run a small
   read-only script against the frozen pool caches to evaluate the
   deterministic baseline rules (fixed_conf x3, budget x3, oracle_cheapest
   on the pool definition chosen) on the pool estimand, and commit the
   resulting CSV before S6 is frozen.

Everything else in Sections 1-10 is complete and verified against the
canonical artifacts.
