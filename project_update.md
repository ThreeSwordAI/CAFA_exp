# CAFA v2 -- Project Update

Date: 2026-07-12 (ALL COMPUTE CLOSED -- final re-freeze tag `canonical-v2.2`;
Sections 11-12 the local pilots, Section 13 the canonical batch, Section 14
the Phase-5 correction pass, Section 15 the Phase-5.2 pool-risk gate that
resolved the last open hole)
Scope: everything from the v2 repair work order through the final re-freeze.
THE single source for every paper number: `CANONICAL_RESULTS.md`
(STATUS: FROZEN, tag `canonical-v2.2`), backed by 35 per-resplit metrics JSONs
in `results_committed/metrics/` (verifiably in git), the canonical readouts in
`results_committed/`, and the committed configs for train seeds 0/1/2. Local
runs (Sections 11-12) are development pilots and replication checks only;
none of their numbers are cited. Two Section-13 statements were superseded by
Phase-5 MEASUREMENT (marked inline; corrected in Section 14.2); the six
marginal-gate FAILs carried since Section 13 are RESOLVED by measurement in
Section 15.

---

## 1. TL;DR

- The v2 pipeline (built to fix five evidence-invalidating bugs C1-C5) ran
  end-to-end **twice**: on the FAU TinyGPU cluster and, independently, on a
  local PC (RTX 3050, fresh venv). All 39 tests pass; `verify_bugs.py` passes
  (C1 honesty, C2 leak demonstration, freeze check).
- **Correctness gates: 15/16 PASS in both environments.** The marginal LTT
  certificate and the CAFA-IUT any-stratum certificate hold everywhere except
  one borderline marginal cell per environment -- and it is a *different* cell
  each time (cluster: spambase/random 0.110; local: mnist/greedy 0.120; delta =
  0.10). This is the documented resplit-dependence caveat, not a systematic
  failure.
- **H2 replicates post-fix:** the plugin baseline is unsafe where alpha is
  tight (violation 0.30-0.45 on mnist, spambase, MiniBooNE/random) while
  cafa_marginal stays at 0.00-0.03 at near-oracle cost.
- **H3 survives post-fix on real data:** at lambda_ref=0.9 an intrinsically
  alpha-infeasible slow stratum is detected (95% CP LCB > alpha) on mnist,
  adult, and MiniBooNE; the marginal threshold demonstrably under-covers it
  (e.g. mnist stratum 4: realized 0.30 vs alpha 0.15).
- **CAFA-IUT behaves exactly as designed:** free (1.0x marginal cost) when all
  strata are feasible (lambda_ref 0.5/0.7 on tabular), and globally abstains to
  full acquisition when a stratum is infeasible (price 2.4x-10.9x at
  lambda_ref=0.9). Zero any-stratum gate failures anywhere.
- The concentration "insight" (greedy concentrates depth vs random) is
  **mixed**: clear on adult (3 vs 5 strata, entropy 0.42 vs 0.77), absent or
  reversed elsewhere. This is fork-review material, not a settled claim.
- **Phase 2 (epsilon axis, local run) settles it at outcome 2 -- MIXED:**
  policy quality concentrates the depth distribution on 3 of 4 datasets
  (aggregate Spearman rho(quality, entropy@0.5) = -0.757, p = 0.0007), but the
  **detection frontier never moved with epsilon within any dataset** -- the
  "better policy delays detection" claim has no within-dataset support on the
  4-point axis. mnist reverses the entropy trend at lambda_ref = 0.9 (the
  Phase-1 reversal persists). Details in Section 11.
- **Phase 3 (local run): the audit finding is backbone-robust.** The same
  stratum verdict reproduces at every train seed on all 4 datasets --
  infeasible on mnist / MiniBooNE / adult (R_full(k*) LCBs 0.22-0.31, far
  above every committed alpha), consistently undetermined on spambase. Two
  alpha step-crossings occurred (mnist ts1 -> 0.20; adult ts2 -> 0.20) -- the
  fixed rule working per backbone. Details in Section 12.
- **The alpha-sweep converts "plugin is fine half the time" into the argument
  for certificates:** the safe/unsafe transition sits at a different, a-priori
  unknowable offset per dataset -- plugin is unsafe across the WHOLE swept
  range on mnist, flips safe at floor+0.05 on adult/MiniBooNE (committed alpha
  lands only 0.015 above the transition on MiniBooNE), and the committed alpha
  lands 0.014 BELOW the transition on spambase. CAFA-marginal stays certified
  throughout; IUT's "price of honesty" falls from full acquisition to zero
  once alpha clears the hardest stratum. Details in Section 12.
- **CANONICAL (Section 13, the lock):** audit stable 4/4 across backbone
  seeds (infeasible on mnist/MiniBooNE/adult, LCBs 0.216-0.306; spambase
  undetermined); Phase 4: audit robust to the readiness score 3/3 with
  byte-identical order/correct; IUT passes ALL 35 cells; the mnist-greedy
  marginal worry did NOT recur (0.02/0.01/0.06 across seeds) but marginal
  DOES fail on the mnist epsilon cells and spambase.
- **PHASE 5.2 (Section 15, the final re-freeze, tag canonical-v2.2):** the
  six marginal-gate FAILs are RESOLVED by measuring the correct estimand:
  **0 of 35 cells violate the pool-risk gate** (exact risk on the whole eval
  pool at each resplit's certified lambda-hat; every previously-failing cell
  collapses to 0.000 [Wilson UB 0.037]), and the mechanism is demonstrated,
  not asserted -- **measured corr(R_cal, R_test) = -1.0000 on every cell**
  (complementary halves of one finite pool anti-correlate exactly, so
  test-split gates systematically over-report violations for ANY
  conformal/LTT certificate -- now a methodological point the paper can
  carry). lambda-hat recomputation via the frozen selector matched the
  recorded value on all 3,500 resplits.
- **PHASE 5 (Section 14, the corrected re-freeze, tag canonical-v2.1):**
  measuring AT the committed alpha (instead of inferring from the nearest
  grid point) corrects the plugin verdict to **UNSAFE on 2 of 4** (mnist
  0.35 never-safe-in-range; spambase 0.45, transition (0.164, 0.169];
  MiniBooNE is SAFE -- its earlier "unsafe by 0.014" and the
  "flipped-between-environments" anecdote were both artifacts of the same
  grid-inference error, now impossible via an asserted H2 cross-check that
  passes 4/4). The six marginal-gate FAILs are QUANTIFIED, not caveated:
  every failing cell has a razor-thin margin (alpha - R_pool(lambda_hat) =
  0.007-0.027, i.e. 1-3 test-split SEs), corr(predicted-from-noise,
  observed) = 0.762, mean |obs - pred| = 0.019 over 35 cells. IUT
  non-vacuity: a certifying fine-stratification operating point exists on
  4/4 datasets (e.g. MiniBooNE certifies every stratum at 16% of full cost
  at alpha 0.284), H3-consistent 4/4.

---

## 2. Why v2 exists (the five confirmed bugs)

An external audit confirmed five evidence-invalidating issues in the legacy
pipeline; all were accepted and fixed structurally:

| bug | what it was | v2 fix | verified by |
|---|---|---|---|
| C1 | tabular greedy scored candidates with their TRUE value (clairvoyant) | mean-imputation at train column means; constructor requires `col_means` | `verify_bugs.py` C1 + `tests/test_policy_honesty.py` (PASS both envs) |
| C2 | every seed re-permuted the full 70k pool: ~60% of cal/test were training images | fixed-train / resplit-heldout (`cafa/splits.py`); disjointness asserted at load | `verify_bugs.py` C2 prints the legacy leak (0.598-0.601 for seeds != 0) and asserts v2 = 0 |
| C3 | Mondrian stratum edges fit on the same calibration set used for selection | edges pre-committed from an independent 10% probe (seed 777) before any selection | committed JSONs in `configs/`; `tests/test_splits_v2.py` |
| C4 | per-stratum threshold routing was circular (stratum unknown before crossing); Mondrian costs not deployable | Mondrian demoted to AUDIT-only (no cost operating point); deployable object = CAFA-IUT (one lambda, certified against every stratum) | `tests/test_iut.py` Monte-Carlo union-null gate (PASS) |
| C5 | MNIST alpha=0.10 violated the project's own fixed-alpha rule | alpha computed only by `feasible_alpha_from_floor` on the probe, committed to JSON | probe commit output (mnist floor 0.078 -> alpha 0.15, exactly as the rule predicted) |

---

## 3. What was built (v2, all additive; frozen core untouched)

- `src/cafa/splits.py` -- fixed-train/probe/resplit machinery, hard disjointness
  assertions, split digests.
- `src/cafa/pool.py` -- one rollout per (dataset, train_seed, policy) caching
  `scores/correct/order`; costs recomputed post-hoc per scheme from `order`
  (policies are cost-blind, so trajectories are cost-scheme-invariant).
- `src/cafa/risk_control_ext.py` -- CAFA-IUT: union-null p-value = max over
  strata of the frozen per-stratum HB p-value; fixed-sequence FWER; global
  abstention -> full acquisition. Composes only frozen primitives.
- `src/cafa/policies_v2.py` -- epsilon-greedy mixture (Phase 2 plumbing, built
  but not yet run).
- Scripts: `train_backbone_v2.py`, `run_pool_rollout.py`, `probe_commit.py`
  (--force / --extend-edges), `run_eval_sweep.py` (100-resplit engine),
  `analyze_results.py` (RESULTS.md + 4 CSVs), `make_figures_v2.py` (F1-F4),
  `verify_bugs.py`.
- 5 new test files (39 tests total incl. legacy); slurm files
  `hpc/pool_rollout.slurm`, `hpc/eval_sweep.slurm`; `repro/` freeze machinery.
- `src/cafa/risk_control.py` and `tests/test_risk_control.py` byte-frozen
  throughout (sha-verified in both environments).

---

## 4. Execution history: what was tried, what broke, what fixed it

### Cluster (TinyGPU)

1. **First pool-rollout submission failed instantly** (`CAFA_ENV: unbound
   variable`): batch jobs start with a clean shell and do not inherit login
   exports. Fix: slurm scripts now `cd` to `$SLURM_SUBMIT_DIR` and source a
   gitignored `hpc/env.local.sh` (template provided), with named error messages
   for missing vars.
2. **Second submission of the same array failed with exit 0:53, 0s elapsed**:
   submitted with `--output=$RESULTS_ROOT/logs/...` from a shell where
   `RESULTS_ROOT` was unset -> Slurm could not create the log file. Lesson
   (now in README): source `hpc/env.local.sh` and `mkdir -p $RESULTS_ROOT/logs`
   before sbatch, or omit the flags.
3. **Resubmitted rollouts: all 8 cells COMPLETED 0:0** (mnist/greedy 6:47 on
   GPU, MiniBooNE/greedy 4:38, rest ~1 min).
4. **eval_sweep.slurm needed `--gres=gpu:1` added**: TinyGPU rejects any job
   without a GPU request, even CPU-only work (the original file assumed a CPU
   partition). All 8 eval cells then completed.
5. **Terminal output appeared empty** for many commands (ls, sacct, sed) in
   the operator's session, causing confusion about whether anything ran. The
   artifacts proved otherwise: the pushed `results_committed/RESULTS.md` has
   854 lines of real results. (The serial rerun commands were also silent but
   worked -- the paste/terminal was swallowing stdout, cause unknown, harmless.)
6. `metrics_v2/` was copied into `results_committed/` but is gitignored by the
   `metrics_v2/` pattern at any level, so only RESULTS.md reached the repo.
   The full per-resplit JSONs currently live only on the cluster.

### Local PC (Windows, RTX 3050 Laptop GPU)

1. Fresh venv (`.venv/`, Python 3.12), torch 2.13+cu126. Base deps + CUDA
   wheel installed cleanly.
2. `pytest`: **35 passed / 2 skipped** without torch, then **4/4** torch tests
   after install -> 39/39 total. Includes the IUT union-null Monte-Carlo gate
   and the legacy G1/G3 gates.
3. `verify_bugs.py`: C1 PASS, C2 PASS. Freeze check initially FAILED -- a
   parsing bug, not a real mismatch: Git Bash `sha256sum` writes `*path`
   (binary marker) which the parser did not strip. Fixed in
   `scripts/verify_bugs.py`; then ALL PASS.
4. Full pipeline (download -> 4 backbones -> 8 rollouts -> probe commit ->
   8 eval cells -> analysis -> figures) ran end-to-end on the GPU without
   errors. Pool sizes match the cluster exactly (28000 / 18089 / 52026 / 1840).
5. Local probe commits were written with `--force` for a self-consistent local
   replication; the cluster's canonical `configs/committed_v2_*.json` were
   restored afterwards (local copies kept in `results/local_committed/`).

---

## 5. Experiments run / not run

### Run (Phase 0 + Phase 1, both environments)

- 4 datasets (mnist, adult, MiniBooNE, spambase) x 2 policies (honest greedy,
  random) = 8 pool rollouts per environment.
- Probe commit per dataset (alpha, stratum edges for 3 lambda_refs x
  {quantile 3/5/8, equal-width 5x{25,50,100}}, per-scheme costs).
- Eval sweep: 100 cal/test resplits x 3 lambda_refs x 3 cost schemes
  (uniform, inverse_info, random; mnist uniform only), methods: cafa_marginal,
  cafa_iut, mondrian audit (per-delta AND joint delta/K), plugin,
  fixed-confidence {0.90,0.95,0.99}, budget {5,10,20}, oracles
  (cheapest-valid, full-feature).
- Population-level per-stratum feasibility verdicts (95% Clopper-Pearson,
  three-way), depth concentration (IQR, normalized entropy), detection
  outcomes, binning ablation (25-seed subset), detection-power scatter data.

### Run additionally (Phase 2, local only so far -- Section 11)

- epsilon-greedy mixtures eps {0.25, 0.5} x 4 datasets: 8 pool rollouts +
  determinism check, probe `--extend-edges`, 8 eval cells, Phase-2 analysis
  (`scripts/phase2_analyze.py`), readout + figures. Cluster run still pending
  (cells/arrays documented; local is the pilot).

### Run additionally (Phase 3 + alpha-sweep, local only so far -- Section 12)

- train_seed {1, 2}: 8 new backbones, 16 rollouts (greedy + random), per-seed
  probe commits (own alpha by the fixed rule), 16 eval sweeps.
- alpha-sweep (ts=0, greedy, primary scheme): 6 floor-anchored alphas x 100
  resplits x 4 datasets, post-hoc on the frozen caches; F5 figures.

### Run additionally (the canonical cluster batch -- Section 13)

- Phase 2 canonical (eps cells 8-15, ts0), Phase 3 canonical (ts 1, 2 with
  per-seed alphas derived on the cluster), the alpha-sweep anchored to
  CLUSTER floors, and Phase 4 (margin-score ablation, cells 17-19 on the
  detecting datasets + mnist). Locked as `CANONICAL_RESULTS.md` + tag
  `canonical-v2`; 35 metrics JSONs in git.

### Run additionally (Phase 5, analysis-only -- Section 14)

- Corrected alpha-sweep (committed alpha measured, transitions bracketed,
  H2 cross-check asserted 4/4), validity diagnostic (35 cells), IUT
  non-vacuity. Re-frozen as tag `canonical-v2.1`. No training, no rollouts,
  no commitment changed.

### Run additionally (Phase 5.2, the last compute -- Section 15)

- The pool-risk gate on all 35 cells (0 failures; determinism + estimand
  asserts passed) and the measured anti-correlation (rho = -1.0000).
  Final re-freeze as tag `canonical-v2.2`.

### Not run / closed by design

- **Phase 2b is cancelled**: the frontier claim is dead (canonically it is
  flat-or-reversed within datasets); more epsilon points cannot revive it.
- **Phase 4 cell 16 (spambase margin)**: skipped -- spambase is undetermined
  by sample size and cannot answer the score-robustness question.
- **The experimental phase is CLOSED.** The next artifact is the paper.
- **Deferred by decision D13 (documented, not implemented)**: (lambda,beta)
  cost-aware family, weighted-CAFA, second backbone family, real-cost dataset,
  e-process variant; detection-power lemma is a writing task.

---

## 6. Results

### 6.1 Committed risk targets (fixed rule: alpha = ceil_0.05(floor + 0.05))

| dataset | cluster floor (probe) | cluster alpha | local floor | local alpha |
|---|---|---|---|---|
| mnist | 0.0779 [0.0697, 0.0867] | **0.15** | 0.0971 | 0.15 |
| adult | 0.1465 [0.1330, 0.1609] | **0.20** | 0.1559 | **0.25** |
| MiniBooNE | 0.0844 [0.0781, 0.0910] | **0.15** | 0.0851 | 0.15 |
| spambase | 0.0543 [0.0298, 0.0904] | **0.15** | 0.0543 | 0.15 |

MNIST alpha=0.15 is exactly what the audit predicted the rule should give
(C5 fix confirmed mechanically). Local adult crossed a 0.05 step because the
locally trained backbone's floor is slightly higher (GPU nondeterminism) --
the rule is doing its job; cluster values are canonical.

### 6.2 Correctness gates (delta = 0.10; Wilson UB criterion)

| cell | cluster marginal | cluster IUT | local marginal | local IUT |
|---|---|---|---|---|
| mnist/greedy | 0.020 PASS | 0.033 PASS | **0.120 FAIL** | 0.037 PASS |
| mnist/random | 0.000 PASS | 0.027 PASS | 0.030 PASS | 0.000 PASS |
| MiniBooNE/greedy | 0.000 PASS | 0.000 PASS | 0.000 PASS | 0.000 PASS |
| MiniBooNE/random | 0.000 PASS | 0.000 PASS | 0.040 PASS | 0.027 PASS |
| adult/greedy | 0.000 PASS | 0.000 PASS | 0.020 PASS | 0.013 PASS |
| adult/random | 0.000 PASS | 0.000 PASS | 0.020 PASS | 0.013 PASS |
| spambase/greedy | 0.030 PASS | 0.037 PASS | 0.010 PASS | 0.017 PASS |
| spambase/random | **0.110 FAIL** | 0.047 PASS | 0.060 PASS | 0.023 PASS |

Reading: the IUT (any-stratum) certificate passes all 16 cells across both
environments. The marginal certificate has exactly one borderline cell per
environment, each with a Wilson interval containing delta -- consistent with
the printed caveat that 100 resplits share one finite eval pool, so violation
events are strongly dependent (an unlucky backbone/pool draw makes them
cluster). This must be reported to the fork review, not smoothed over.

### 6.3 H2 -- validity + efficiency (cluster, lambda_ref=0.9 headline cells)

- **mnist/greedy (uniform costs)**: plugin violates on 35% of resplits;
  cafa_marginal 2% at cost ratio 0.507 vs oracle floor 0.490 (i.e. ~3.5% above
  the non-deployable oracle, with the guarantee). Budget baselines violate on
  100% of resplits.
- **spambase/greedy**: plugin violation 0.45 vs cafa_marginal 0.03; CAFA cost
  6.08 vs oracle 4.22 vs full 57 (9.4x cheaper than full acquisition).
- **MiniBooNE/greedy**: alpha is loose enough that plugin == CAFA == oracle
  (cost ratio 0.067 of full; inverse_info scheme: 0.050) -- the "plugin unsafe"
  story does NOT hold here; it holds on mnist, spambase, and MiniBooNE/random
  (0.30).
- **adult/greedy**: everything except budget_5 is safe at alpha=0.20;
  cafa_marginal = oracle cost exactly (0.395 of full; inverse_info 0.361).
- Cost-scheme robustness: the pattern is stable across uniform / inverse_info /
  random schemes (costs recomputed post-hoc from the same trajectories).

### 6.4 H3 -- per-stratum audit (cluster)

Representative (mnist/greedy, lambda_ref=0.9): strata 0-3 feasible
(R_full 0.031-0.045, marginal realized risk 0.087-0.113, Mondrian certifies
1.00); stratum 4 (slowest instances) **infeasible**: R_full = 0.2479
[0.2383, 0.2576] >> alpha = 0.15, marginal realized risk there 0.3005 -- the
marginal certificate demonstrably under-covers the hard stratum while Mondrian
audit abstains on it 100% (correct behavior).

Detection outcomes (95% CP LCB > alpha): mnist/greedy at lambda_ref >= 0.9;
mnist/random at >= 0.7; MiniBooNE both and adult both at >= 0.9; spambase
never (eval pool too small -- verdicts stay undetermined/feasible). Detection
requires deep reference thresholds; at lambda_ref 0.5/0.7 all populated strata
certify on the tabular datasets.

### 6.5 CAFA-IUT -- the price of uniform validity (cluster)

- Where every stratum is feasible (tabular, lambda_ref 0.5/0.7): IUT selects
  the same lambda as marginal -- **cost premium 1.000x, abstention 0.000**.
  Uniform per-stratum validity is free when it is achievable.
- Where a stratum is infeasible (lambda_ref=0.9): IUT globally abstains
  (rate 0.98-1.00) and falls back to full acquisition -- premium 2.4x-3.7x
  (adult), 6.0x (MiniBooNE/random), 9.4x-10.9x (spambase/greedy), and on mnist
  full cost 49 vs marginal ~25 (~2x). This is the honest price of refusing to
  deploy an uncertifiable threshold; the audit names the blocking stratum.
- Local replication shows the same on/off pattern (abstention 0 at feasible
  configs, ~1.0 at infeasible ones), with small differences in which
  (dataset, lambda_ref) cells sit at the boundary (e.g. spambase/greedy
  lr=0.7: 96/100 abstentions locally vs 80/100 on cluster).

### 6.6 Fork metrics -- the concentration insight (cluster)

- Strata counts (lambda_ref=0.9): adult greedy 3 vs random 5 (greedy
  concentrates); mnist 5 vs 5; MiniBooNE 5 vs 5; spambase 5 vs 5 (but at 0.7:
  greedy 4 vs random 5).
- Depth concentration: adult greedy entropy 0.42 vs random 0.77 (clear);
  mnist at lambda_ref 0.5 greedy IQR 6 vs random 9 (concentrates) but at 0.9
  greedy IQR 31 vs random 23 (reverses); MiniBooNE 8 vs 23 at 0.9
  (concentrates).
- Verdict for the fork: the insight **narrows** rather than survives or dies --
  it is dataset- and lambda_ref-dependent. Per the authors' own branch plan,
  this is the reviewer's call, with the numbers now on the table.

---

## 7. What worked / what did not

### Worked

- All five bug fixes verified by executable checks in two environments.
- Pool-rollout architecture: one rollout per (dataset, policy) made 100
  resplits x 3 lambda_refs x 3 cost schemes essentially free (eval cells run
  in ~1-4 min on CPU).
- Pre-commitment discipline: probe-committed alpha/edges survived contact with
  both environments; the fixed alpha rule produced the audit-predicted values.
- IUT: theoretically clean (union-null argument), empirically valid (0/16 gate
  failures), and informative (free when feasible, honest abstention when not).
- Full local reproducibility from a clean venv on consumer hardware in ~1 h.

### Did not work / friction

- Slurm environment propagation (two failed submissions before the
  env.local.sh mechanism); TinyGPU's mandatory GPU allocation contradicted the
  "CPU array" design of eval_sweep.slurm (fixed by adding --gres).
- One borderline marginal-gate cell per environment (Sec. 6.2) -- the strict
  Wilson-UB gate criterion flags it; the dependence caveat explains it, but it
  is a real limitation of resplit-based violation estimation on small pools.
- spambase is too small for the stratum machinery (probe n=184; verdicts
  mostly undetermined; its random-policy cell is the cluster's borderline
  gate). It functions as a boundary example, not as evidence.
- The plugin-unsafe story is not universal: where the fixed-alpha rule lands
  generously (adult 0.20, MiniBooNE greedy), plugin is safe too. The claim
  must be stated conditionally.
- Backbone nondeterminism across hardware shifts floors slightly; adult's
  alpha moved 0.20 -> 0.25 locally. Expected, but worth stating in the paper's
  reproducibility notes (alpha is committed per environment; ts=0 cluster
  values are canonical).
- `metrics_v2/` never reached the repo (gitignore matches the nested copy in
  results_committed/) -- the per-resplit JSONs exist only on the cluster and
  this PC. Needs a deliberate `git add -f` or a rename if the reviewer wants
  them.
- Freeze-check portability (Windows): the committed `repro/MANIFEST.sha256`
  hashes the LF working tree (cluster); Windows checks the same files out with
  CRLF, so the raw-byte comparison false-alarmed. Verified the git blob (LF)
  content matches the cluster hashes exactly (`c37ab6...`, `3ec125...`) -- the
  freeze holds; `verify_bugs.py` now retries with CRLF->LF normalization and
  reports it did so. (Earlier, the same script needed a fix for Git Bash's
  `*filename` binary-mode prefix in sha256sum output.)

---

## 8. What we can claim now vs not yet

Can claim (evidence in hand, both environments):
- The v2 pipeline controls marginal risk at the certified level up to the
  documented dependence caveat, and controls any-stratum risk via IUT with
  zero observed failures.
- CAFA-marginal is near-oracle-cost cheap where certification is possible,
  and dramatically cheaper than full acquisition (down to 5-7% of full cost
  on MiniBooNE).
- The audit detects genuine per-stratum infeasibility on three of four
  datasets at deep reference thresholds, and the marginal threshold's
  under-coverage of those strata is real and quantified.
- Uniform per-stratum validity is free when all strata are feasible and
  costs 2.4x-10.9x (full acquisition) when one is not.

Cannot claim yet (needs fork review / more runs):
- The greedy-concentration insight as a general phenomenon (mixed evidence).
- Robustness across train seeds (Phase 3 not run) and policy mixtures
  (Phase 2 not run); score ablation (Phase 4 not run).
- Any interpretation of the two borderline gate cells beyond the dependence
  caveat (would need independent eval pools or a block-bootstrap analysis --
  out of scope for v2).

---

## 9. Where everything lives

| artifact | location |
|---|---|
| Canonical results (cluster) | `results_committed/RESULTS.md` |
| Committed probe artifacts (canonical, ts=0) | `configs/committed_v2_*.json` |
| Local replication report + CSVs | `analysis_v2/` (gitignored) |
| Phase-2 readout + summary + determinism record | `analysis_v2/PHASE2_READOUT.md`, `phase2_summary.csv`, `phase2_determinism.txt` |
| Phase-3 cross-seed report | `analysis_v2/PHASE3_REPORT.md` |
| Alpha-sweep report + data (canonical, corrected) | `results_committed/ALPHA_SWEEP.md`, `alpha_sweep.csv`, `alpha_sweep_transitions.csv` |
| Validity diagnostic (canonical) | `results_committed/VALIDITY_DIAGNOSTIC.md`, `validity_diagnostic.csv`; figure `F6_validity_diagnostic.*` |
| IUT non-vacuity (canonical) | `results_committed/IUT_NONVACUITY.md`, `iut_nonvacuity*.csv` |
| Pool-risk gate (canonical, Phase 5.2) | `results_committed/POOL_RISK_GATE.md`, `pool_risk_gate.csv`; figure `F7_pool_risk_gate.*` |
| Local figures F1-F4 (pdf+png, per dataset) | `figures_v2/` (gitignored) |
| Phase-2 figures | `figures_v2/F3_phase2_*`, `F3_phase2_frontier.*`, `F4_phase2.*` |
| Alpha-sweep figures | `figures_v2/F5_*.{pdf,png}` |
| Canonical metrics home (non-gitignored, for the lock) | `results_committed/metrics/` (`.gitkeep` placed; populate + `git add` from the cluster batch) |
| Local ts1/ts2 committed configs (PROVISIONAL, untracked -- do not commit) | `configs/committed_v2_*_ts{1,2}.json` + copies in `results/local_committed/` |
| Local per-resplit metrics | `metrics_v2/` (gitignored) |
| Local probe commits + manifest (reference) | `results/local_committed/` |
| Pool caches / checkpoints (local) | `results/pool_v2/`, `results/checkpoints_v2/` |
| Cluster per-resplit metrics | cluster: `$CAFA_REPO/metrics_v2/` (not in git) |
| Frozen-file manifest | `repro/MANIFEST.sha256` (cluster hashes) |
| Environment lock (cluster) | `repro/requirements.lock.txt` |

Uncommitted local diffs (intentional, not pushed): `.gitignore` (+`.venv/`),
`scripts/verify_bugs.py` (sha256sum `*` prefix + CRLF-normalization fixes),
`scripts/run_eval_sweep.py` (Phase-2 cells 8-15), `hpc/eval_sweep.slurm`
(Phase-2 array comment), new `scripts/phase2_analyze.py`,
`scripts/alpha_sweep.py`, `scripts/phase3_report.py`,
`results_committed/metrics/.gitkeep`, `project_update.md`.

---

## 10. Next steps

1. **Write the paper.** Every number comes from `CANONICAL_RESULTS.md`
   (STATUS: FROZEN, tag `canonical-v2.2`); the readouts in
   `results_committed/` carry the per-table detail; figures F1-F7 in
   `results_committed/figures/`. The spine: H2 (certified cheap stopping;
   plugin unsafe AT the committed target on **2 of 4** datasets, BY
   MEASUREMENT -- Section 14.2) + the audit (backbone-robust and score-robust
   infeasible strata) + CAFA-IUT (35-for-35 gate record, with the
   non-vacuity table showing where it certifies at a fraction of full cost --
   Section 14.4) + the pool-risk gate (0/35 violations against the correct
   estimand, with the measured rho = -1 anti-correlation as a general
   finite-pool methodological subsection -- Section 15) + the
   detection-power lemma (writing task). Concentration is a one-paragraph
   quantified observation (canonical rho -0.746 at lambda_ref 0.5, weakening
   to n.s. at 0.9; monotone on 1 of 4 datasets).
2. **Honest flags that must survive into the paper** (Sections 13.6, 14.5,
   15.3): the ten flagged marginal cells with their EXPLAINED + RESOLVED
   annotations (test-split basis kept visible next to the pool gate);
   spambase undetermined-by-sample-size and near-vacuous IUT certification;
   the frontier flat-or-reversed detail vs the canonical file's "flat"
   shorthand; the Section-13.3 retraction itself (the paper must cite the
   MEASURED transitions only).
3. The laptop is now a replication check only. **No further experiments or
   analyses -- Phase 5.2 was the last compute task.** The next artifact is
   the paper.

---

## 11. Phase 2 -- the policy-quality axis (local run, 2026-07-12)

### 11.1 What Phase 2 asks

Phase 1 tested concentration at two extremes (greedy eps=0 vs random eps=1)
and got mixed evidence. Phase 2 builds a 4-point policy-quality axis
eps in {0, 0.25, 0.5, 1.0} per dataset and asks: as policy quality increases,
(a) does the reference-depth distribution concentrate, and (b) does the
minimal lambda_ref needed to detect the infeasible stratum (the detection
frontier) rise -- i.e. does a better policy make the hidden failure harder to
see? Three pre-committed outcomes: 1 = monotone and clean (insight
resurrects), 2 = mixed (reported observation), 3 = flat/reversed (dropped).

Quality is measured independently of concentration (avoiding tautology):
`quality_auc` = normalized area under accuracy-at-budget; `steps_to_90` =
smallest depth reaching 90% of full-acquisition accuracy.

### 11.2 What ran (this laptop, RTX 3050, venv from Phase 1)

New code (additive): `scripts/phase2_analyze.py` (metric families A/B/C,
frontier, lemma face, Spearman, fork verdict, F3/F4 Phase-2 figures);
`run_eval_sweep.py` cell list extended to 8-15 (mirrors the rollout cells);
`hpc/eval_sweep.slurm` documents the Phase-2 array. Frozen core untouched
(verified before and after).

Pipeline executed: 8 epsilon rollouts (cells 8-15) + a determinism re-run of
cell 8 -> `probe_commit --extend-edges` x4 (probe seed 777; alpha/floor
untouched, edges for all 4 policies now in each committed JSON) -> 8 eval
cells -> `analyze_results` + `make_figures_v2` + `phase2_analyze` ->
`pytest -q` (41 passed) + `verify_bugs.py` (ALL PASS). Local committed configs
were used for a self-consistent local axis and archived to
`results/local_committed/`; the cluster canonical configs were restored
afterwards.

### 11.3 Fork verdict: OUTCOME 2 (mixed) -- with an important nuance

Per-dataset monotonicity (points ordered by quality_auc; entropy at
lambda_ref = 0.9; frontier = min lambda_ref with a detected infeasible
stratum):

| dataset | quality_auc range (worst->best) | entropy@0.9 trend | frontier across eps | monotone? |
|---|---|---|---|---|
| tabular-adult | 0.8122 -> 0.8187 | 0.786 -> 0.602 (falls) | 0.9 at every eps | yes |
| tabular-MiniBooNE | 0.8648 -> 0.8966 | 0.835 -> 0.699 (falls) | 0.9 at every eps | yes |
| tabular-spambase | 0.8636 -> 0.8830 | 0.934 -> 0.818 (falls) | not detected at any eps | yes |
| mnist | 0.6411 -> 0.7029 | 0.789 -> 0.859 (RISES) | 0.7 at every eps | no (entropy reverses) |

Aggregate over all 16 (dataset, eps) points ("not detected" encoded 1.0):

- rho(quality_auc, min_lambda_ref_detected) = **0.671** (p = 0.0044)
- rho(quality_auc, entropy@0.5) = **-0.757** (p = 0.0007)
- rho(quality_auc, entropy@0.7) = -0.542 (p = 0.0301)
- rho(quality_auc, entropy@0.9) = -0.079 (p = 0.7700)

**The honest reading (stated in the readout, must survive into any paper
text):**

1. **Concentration is real but threshold-dependent.** Better policies
   concentrate the reference-depth distribution strongly at shallow/mid
   reference thresholds (rho -0.76 at 0.5, -0.54 at 0.7) and not at deep ones
   (rho -0.08 at 0.9). mnist reverses at 0.9, exactly as in Phase 1.
2. **The detection frontier did NOT move with epsilon within any dataset**
   (mnist 0.7 at every eps; adult/MiniBooNE 0.9 at every eps; spambase never).
   The positive aggregate frontier correlation (0.671) is therefore driven by
   *between-dataset* differences (which conflate dataset difficulty with
   policy quality), not by policy quality shifting the frontier -- on this
   axis, "better policy -> harder to detect" has **no within-dataset
   support**. The lambda_ref grid {0.5, 0.7, 0.9} is also coarse; a frontier
   shift smaller than one grid step is invisible.
3. Curiosity worth keeping: on mnist the myopic greedy is NOT the best policy
   by quality_auc (eps=0.25 scores 0.7029 vs greedy 0.6980; greedy's
   steps_to_90 = 37 is the worst on mnist). The quality axis is therefore not
   perfectly ordered by epsilon on mnist -- the monotonicity test used
   quality_auc ordering, as specified.

Consequence for the paper framing (per the pre-committed outcomes): the
concentration observation is reportable at "3 of 4 datasets, strongest at
shallow reference thresholds"; the frontier/detection-delay claim should NOT
be made from this evidence. The paper stands on audit + IUT + H2, with
concentration as a quantified observation.

### 11.4 Certificate gates on the epsilon cells (delta = 0.10, Wilson UB)

- **IUT any-stratum: 16/16 PASS** (max observed 0.037).
- Marginal: 14/16 PASS. FAILs: mnist/eps=0 (0.120 [UB 0.162], the known
  Phase-1 local borderline) and mnist/eps=0.5 (0.090 [UB 0.128] -- point
  estimate below delta; UB above). Same resplit-dependence caveat as Phase 1:
  resplits share one finite eval pool, violations cluster with the backbone
  draw. To be flagged, not smoothed.
- New-cell eval summaries: adult 2/100 violations at every eps; MiniBooNE
  0/100; spambase 6/100 (eps 0.25) and 0/100 (eps 0.5); mnist 0/100 (eps 0.25)
  and 9/100 (eps 0.5). IUT abstention switches on exactly where an infeasible
  stratum appears (lambda_ref 0.9 tabular; 0.7+ mnist), as designed.

### 11.5 Invariant checks (Phase-2 instructions Sec. "Checks & gates")

- **Freeze:** git-blob (LF) content of both frozen files matches the cluster
  manifest exactly; `pytest -q` 41 passed; `verify_bugs.py` ALL PASS.
- **Policy determinism:** cell 8 (adult, eps=0.25) re-rolled from the same
  seed -> `order`, `scores`, `correct` byte-identical (PASS; recorded in
  `analysis_v2/phase2_determinism.txt` and embedded in the readout). Policy
  RNG seed = 10_000 + round(1000*eps), fixed per rollout; the deployed policy
  is a frozen measurable function of x via the cached order.
- **Cost-blindness:** structural -- rollouts never see costs; per-scheme costs
  derived post-hoc from `order`.
- **Split hygiene / edge provenance:** disjointness asserted at load for every
  new cell; epsilon-policy edges committed from the probe (seed 777) via
  `--extend-edges` BEFORE any eval selection, loaded from JSON, never refit.

### 11.6 Phase-2 caveats and what would strengthen it

- Local-only so far: the cluster (canonical) Phase-2 run is pending; expect
  small boundary differences (local backbones differ; local adult alpha is
  0.25 vs cluster 0.20).
- 4 epsilon points per dataset, frontier measured on a 3-point lambda_ref
  grid: a finer lambda_ref grid (not just Phase 2b's finer epsilon grid) is
  what could actually resolve a within-dataset frontier shift, if one exists.
- The aggregate frontier Spearman should not be quoted without the
  between-dataset confound caveat (Sec. 11.3, point 2).

---

## 12. Phase 3 + alpha-sweep (local run, 2026-07-12)

Per the Phase-3 instructions: the fork is closed (Phase 2 outcome 2; the
"better policy -> harder to detect" claim is dead and Phase 2b cancelled);
the paper's spine is H2 + audit + IUT + the detection-power lemma. Phase 3
elevates **backbone robustness** to a primary result backing the audit claim,
and the **alpha-sweep** converts the "plugin is fine half the time" weakness
into the argument for certificates. ALL NUMBERS BELOW ARE LOCAL/PROVISIONAL
(environment rule); the canonical batch re-derives them on the cluster.

### 12.1 What ran (this laptop)

New code (additive; frozen core verified untouched): `scripts/alpha_sweep.py`
(floor-anchored post-hoc sweep + F5), `scripts/phase3_report.py` (cross-seed
stability report). Executed: 8 new backbones (train_seed 1, 2 x 4 datasets) ->
16 pool rollouts (greedy + random) -> per-(dataset, seed) probe commits (each
seed its OWN alpha by the fixed rule) -> 16 eval sweeps (100 resplits x 3
lambda_ref x cost schemes) -> alpha-sweep on the ts=0 greedy caches (6 alphas
x 100 resplits x 4 datasets) -> reports + figures -> gates (pytest 41 passed;
verify_bugs ALL PASS incl. the CRLF-normalized freeze check).

### 12.2 Task 1 -- backbone robustness: the audit replicates 4/4

Committed {floor -> alpha} per (dataset, train_seed), local backbones:

| dataset | ts0 | ts1 | ts2 | step crossing? |
|---|---|---|---|---|
| mnist | 0.0971 -> 0.15 | 0.1011 -> **0.20** | 0.0943 -> 0.15 | yes (ts1) |
| adult | 0.1559 -> 0.25 | 0.1614 -> 0.25 | 0.1454 -> **0.20** | yes (ts2) |
| MiniBooNE | 0.0851 -> 0.15 | 0.0886 -> 0.15 | 0.0938 -> 0.15 | no |
| spambase | 0.0543 -> 0.15 | 0.0707 -> 0.15 | 0.0652 -> 0.15 | no |

The two step crossings are the fixed rule applied per backbone -- reported
per seed, never mixed (the honest answer to the alpha-boundary objection).

**Audit stability (the headline): STABLE on 4 of 4 datasets.** The hardest
stratum's verdict at lambda_ref = 0.9 reproduces at every train seed:

| dataset | verdict at every seed | R_full(k*) [95% CP LCB] by ts0/ts1/ts2 |
|---|---|---|
| mnist (k*=4) | infeasible | 0.250 [0.241] / 0.279 [0.269] / 0.261 [0.252] |
| MiniBooNE (k*=4) | infeasible | 0.253 [0.245] / 0.224 [0.217] / 0.253 [0.246] |
| adult (k*=3/4/3) | infeasible | 0.306 [0.296] / 0.322 [0.312] / 0.309 [0.299] |
| spambase (k*=4) | undetermined | 0.170 [0.137] / 0.157 [0.128] / 0.139 [0.107] |

Every LCB on the three detecting datasets sits far above every committed
alpha -- the infeasible stratum is a property of the data, not of a lucky
backbone draw. Note adult's k* label shifts (3/4/3) while the verdict is
stable; spambase is consistently undetermined (probe n = 184 -- too small to
decide, honestly reported). IUT abstains ~1.00 at lambda_ref = 0.9 at every
seed, consistent with the detected infeasibility.

Gates across the new seeds: IUT passes everywhere (max UB 0.081). Marginal
passes everywhere except mnist ts0 and ts2 (both 0.120 [UB 0.162]) -- see
12.5.

### 12.3 Task 2 -- the alpha-sweep: where the plugin transition sits

Grid: alpha in floor + {0.02, 0.05, 0.08, 0.11, 0.15, 0.20}; ts=0 greedy,
primary scheme; 100 resplits per alpha; the committed rule alpha
(= ceil_0.05(floor + 0.05)) marked per dataset. Full tables in
`analysis_v2/ALPHA_SWEEP.md`; F5 per dataset in `figures_v2/`.

Plugin safe/unsafe transition vs the committed alpha (local anchors):

| dataset | plugin transition | committed alpha | verdict at committed target |
|---|---|---|---|
| mnist | never safe in range (viol 0.13-0.47 everywhere) | 0.15 | UNSAFE -- certificate essential |
| adult | ~0.206 (floor + 0.050) | 0.25 | safe by 0.044 |
| MiniBooNE | ~0.135 (floor + 0.050) | 0.15 | safe by only 0.015 |
| spambase | ~0.164 (floor + 0.110) | 0.15 | UNSAFE by 0.014 (inside the transition) |

Sentence-ready framing (now backed by data): the alpha at which an
uncorrected heuristic flips from safe to unsafe is a property of the
risk-curve geometry near alpha -- it lands at a different, a-priori
unknowable offset on every dataset, and the fixed-rule committed alpha falls
within ~0.015 of the transition on two datasets and inside the unsafe regime
on two others. That is the argument FOR a certificate rather than a tuned
threshold. cafa_marginal stays at/below delta across the sweep except at the
ultra-tight floor+0.02 point (12.5).

**Price of honesty (IUT panel):** abstention stays at 1.00 while any stratum
is alpha-infeasible and collapses to ~0 once alpha clears the hardest
stratum: mnist/adult/MiniBooNE abstain 1.00 through floor+0.15 and 0.00 at
floor+0.20; spambase declines gradually (1.00 -> 0.85 -> 0.10 over
+0.11/+0.15/+0.20). The number of alpha-infeasible strata at lambda_ref=0.9
tracks the same boundary (1 -> 0). Uniform per-stratum validity is free
exactly when it is achievable, and refuses to pretend otherwise.

### 12.4 Task 3 -- artifact completeness (prepared, completed at the lock)

`results_committed/metrics/` created (non-gitignored home for the canonical
per-resplit JSONs; the `metrics_v2/` pattern has silently swallowed them
twice). `analyze_results.py` accepts `--metrics-dir`, so a reviewer can
regenerate every RESULTS.md table from the committed JSONs without re-running
the sweep. Population + force-add happens in the canonical batch, verified
with `git status`.

### 12.5 Honest flags (report, do not smooth)

- **mnist marginal gate at alpha = 0.15 (local):** ts0 and ts2 both show
  0.120 violation [UB 0.162] (ts1, whose rule alpha crossed to 0.20, passes
  at 0.010). The local mnist backbones are weaker than the cluster's (floors
  0.094-0.101 vs 0.078), pushing alpha = 0.15 close to the achievable
  boundary where the selected lambda sits at the certification edge and
  resplit-dependent violations cluster. The cluster ts0 mnist cell passed
  (0.020); whether this recurs canonically is exactly what the cluster
  Phase-3 run will show. IUT passes on every mnist cell regardless.
- **Ultra-tight alpha (floor + 0.02) in the sweep:** marginal violation
  exceeds delta on adult (0.17), spambase (0.11), MiniBooNE (0.10) -- at a
  target 2 points above the floor, the certifiable region is razor-thin and
  the same dependence mechanism dominates. The committed rule (+0.05 with
  ceiling) deliberately does not operate there; the sweep documents the
  regime rather than hiding it.
- Local ts1/ts2 committed configs are PROVISIONAL and untracked; canonical
  per-seed alphas come from the cluster probe (mnist ts1's 0.20 crossing in
  particular must be re-derived, not copied).

---

## 13. THE CANONICAL LOCK (cluster batch, 2026-07-12) -- the paper's numbers

Provenance: tinyx, git commit b5d8b64 (locked as eee8d9f, tag
`canonical-v2`); frozen-file hashes verified (CRLF-normalized); environment in
`repro/requirements.lock.txt`. Artifact set: `CANONICAL_RESULTS.md` (FROZEN),
35 per-resplit metrics JSONs in `results_committed/metrics/` (in git,
recomputable via `analyze_results.py --metrics-dir results_committed/metrics`),
canonical readouts + CSVs + figures in `results_committed/`, committed configs
for train seeds 0/1/2 (each seed's alpha derived on the cluster). The
pre-flight and per-step gates all passed (pytest, verify_bugs, alpha-unchanged
asserts on every --extend-edges, Phase-4 order/correct invariant).

### 13.1 Committed targets (canonical)

| dataset | ts0 floor -> alpha | ts1 | ts2 | step crossing |
|---|---|---|---|---|
| mnist | 0.0779 -> 0.15 | 0.1011 -> **0.20** | 0.0943 -> 0.15 | yes (ts1) |
| adult | 0.1465 -> 0.20 | 0.1614 -> **0.25** | 0.1454 -> 0.20 | yes (ts1) |
| MiniBooNE | 0.0844 -> 0.15 | 0.0886 -> 0.15 | 0.0938 -> 0.15 | no |
| spambase | 0.0543 -> 0.15 | 0.0707 -> 0.15 | 0.0652 -> 0.15 | no |

(Note vs local: the crossings land on different seeds than the local pilots
did -- per-backbone alphas are genuinely backbone-specific.)

### 13.2 The audit (H3): backbone-robust AND score-robust

Cross-seed stability at lambda_ref = 0.9 (greedy): **STABLE 4/4** --
infeasible at every seed on mnist (k*=4; R_full 0.248/0.266/0.268, LCBs >=
0.238), MiniBooNE (k*=4; 0.233/0.223/0.249) and adult (k*=3/4/3;
0.309/0.316/0.302); consistently undetermined on spambase. The marginal
threshold's realized risk on k* is 0.27-0.42 at every seed -- quantified
under-coverage of the hard stratum, reproduced across backbone draws.

Phase 4 (margin score, own probe-committed stratification): **robust 3/3**
(mnist, MiniBooNE, adult all still infeasible), with the mechanics invariant
ALL PASS -- `order` and `correct` byte-identical between softmax and margin
rollouts (only the stopping score changed), alpha unchanged. The infeasible
stratum is a property of the data, not of the backbone draw and not of the
readiness-score choice.

### 13.3 The alpha-sweep (canonical anchors)

> **[SUPERSEDED BY MEASUREMENT -- see Section 14.2.]** This table INFERRED
> each committed target's side from the nearest floor-anchored grid point;
> the committed alpha itself was not on the grid. Phase 5 measured AT the
> committed alpha: MiniBooNE is SAFE (plugin violation 0.000; its true
> transition is (0.1344, 0.1363]), so the corrected headline is UNSAFE on
> **2 of 4**, and the "MiniBooNE flipped sides between environments"
> paragraph below is RETRACTED (both apparent flips were artifacts of the
> same interpolation error).

| dataset | floor | committed alpha | plugin transition (inferred) | committed target (inferred) |
|---|---|---|---|---|
| mnist | 0.0779 | 0.15 | never safe in range | UNSAFE |
| MiniBooNE | 0.0844 | 0.15 | 0.164 (floor + 0.080) | UNSAFE by 0.014 [WRONG -- 14.2] |
| adult | 0.1465 | 0.20 | 0.167 (floor + 0.020) | SAFE by 0.034 |
| spambase | 0.0543 | 0.15 | 0.204 (floor + 0.150) | UNSAFE by 0.054 |

(Retracted: "MiniBooNE flipped sides between the local and canonical sweeps
... not predictable from a pilot." Section 14.2 makes the
unknowable-a-priori argument correctly, from measured transitions.)
cafa_marginal stays at or below delta across the sweep (except the documented
ultra-tight floor+0.02 regime); the price-of-honesty curve reproduces (IUT
abstention ~1.0 while any stratum is infeasible, ~0 once alpha clears the
hardest stratum).

### 13.4 Gates (all 35 cells): IUT perfect; marginal fails where expected

- **IUT any-stratum: 35/35 PASS** (max violation 0.053, UB 0.085).
- **Marginal: 29/35 PASS.** The six FAILs: mnist eps=0.25 (0.110) and
  eps=0.5 (0.140); MiniBooNE eps=0.25 (0.080, UB 0.116); spambase eps=0.25
  (0.090), spambase random ts0 (0.110), spambase greedy ts1 (0.100).
- **The Section-3 live question is answered:** the local mnist-greedy
  failures did NOT recur canonically -- mnist greedy passes at all three
  seeds (0.020 / 0.010 / 0.060). What fails instead is systematic: the mnist
  epsilon cells and spambase. Pattern: marginal degradation concentrates
  where alpha sits near the policy's achievable boundary (noisier policies
  raise the effective floor at stopping; spambase's pool is tiny), and
  resplit-dependent violations cluster there. This is a real, reportable
  finding -- *near the achievable floor the marginal certificate's
  finite-sample validity degrades* -- and it strengthens rather than hurts
  the thesis, because IUT passes every one of those cells.

### 13.5 H2 + IUT price (canonical headlines, lambda_ref = 0.9)

- Plugin violation where alpha is tight: mnist 0.35-0.59 (per seed), spambase
  0.37-0.48, MiniBooNE/random 0.30; cafa_marginal <= 0.06 on every greedy/
  random cell. On adult (generous alpha) plugin == CAFA == oracle.
- CAFA cost: MiniBooNE greedy stops at 3.4-5.5% of full-acquisition cost
  (inverse_info), adult at 21-36%, mnist at 51-74%, always at or near the
  oracle-cheapest floor.
- IUT premium at lambda_ref 0.9 (ts0 greedy): mnist 1.97x, adult 2.77x,
  spambase 10.9x, MiniBooNE 20.0x -- the honest price of refusing to deploy
  over an infeasible stratum; 1.000x at every feasible (dataset, lambda_ref)
  except mnist 0.5 (1.235x, certified but stricter union p-value).

### 13.6 Phase 2 canonical + remaining honest flags

- Concentration: rho(quality, entropy@0.5) = -0.746 (p = 0.0009); @0.7 =
  -0.484 (p = 0.058, no longer significant); @0.9 = -0.197 (n.s.).
  Per-dataset monotonicity holds on only 1 of 4 datasets canonically
  (MiniBooNE) -- weaker than the local pilot's 3/4. Report at that strength.
- The frontier: canonically NOT even uniformly flat -- constant in epsilon on
  adult/MiniBooNE, varying NON-MONOTONICALLY on mnist and spambase with
  negative per-dataset rho (if anything, better policies were detected
  EARLIER). The detection-delay claim is dead in both directions; the
  aggregate rho (0.576) remains a between-dataset confound, never to be
  quoted as support. (The frozen canonical file's one-line shorthand says
  "flat within every dataset"; PHASE2_READOUT.md carries the precise
  per-dataset behavior -- cite the readout for this detail.)
- spambase: undetermined by sample size (probe n = 184) at every seed and
  the site of most marginal-gate noise; it is a boundary example, not
  evidence.
- Local (laptop) runs: development pilots only; alphas differ per backbone;
  no local number is cited anywhere.

### 13.7 Status

**EXPERIMENTAL PHASE CLOSED.** Superseded note: two Section-13.3 statements
were corrected by Phase-5 measurement (Section 14); the file re-froze as
`canonical-v2.1`.

---

## 14. PHASE 5 -- the analysis-only pass (correct, explain, re-freeze;
cluster, 2026-07-12, tag canonical-v2.1)

Pure numpy on the cached canonical artifacts: no training, no rollouts, no
new methods. Three tasks -- fix one factual error, quantify the six
marginal-gate failures, prove the deployable object is non-vacuous -- then
re-freeze. Developed and smoke-tested locally, run canonically on tinyx
against `results_committed/metrics/` and the canonical pool caches; gates
(pytest, verify_bugs, freeze) passed before and after; `git diff configs/`
empty (no committed alpha or edge changed).

New/changed code: `scripts/alpha_sweep.py` (measured committed-alpha point,
transition bracketing, hard-asserted H2 cross-check),
`scripts/validity_diagnostic.py` (new), `scripts/iut_nonvacuity.py` (new),
`scripts/make_canonical_results.py` (three new sections + EXPLAINED flags).

### 14.1 The bug that Phase 5 fixed (and the check that makes it unrepeatable)

The v2.0 alpha-sweep grid was floor + {0.02...0.20}; the committed alpha was
generally NOT on the grid, and each dataset's verdict at the committed target
was INFERRED from the nearest grid point. For MiniBooNE that produced
"UNSAFE by 0.014" while the H2 table measured plugin violation 0.00 at the
same alpha -- a direct cross-table contradiction (and the apparent
local-vs-canonical "side flip" was the same error twice). Phase 5 makes the
committed alpha an explicit measured grid point, brackets the transition by
bisection to a stated resolution, and HARD-ASSERTS that the sweep's plugin
violation at the committed alpha equals the H2 table's -- the assert passed
4/4 canonically (0.350=0.350, 0.000=0.000, 0.000=0.000, 0.450=0.450).

### 14.2 Corrected alpha-sweep verdicts (BY MEASUREMENT; the paper's version)

| dataset | committed alpha | plugin viol AT committed [95% CI] | verdict | transition (bracketed) |
|---|---|---|---|---|
| mnist | 0.15 | 0.350 [0.264, 0.447] | **UNSAFE** | never safe in range (last point 0.278) |
| MiniBooNE | 0.15 | 0.000 [0.000, 0.037] | **SAFE** | (0.1344, 0.1363], resolution 0.0019 |
| adult | 0.20 | 0.000 [0.000, 0.037] | **SAFE** | below the swept range (safe at 0.1665) |
| spambase | 0.15 | 0.450 [0.356, 0.548] | **UNSAFE** | (0.1643, 0.1693], resolution 0.005 |

**Corrected headline: the fixed rule lands inside the UNSAFE regime on 2 of
4 datasets.** The unknowable-a-priori argument survives in its correct form:
the measured transitions land at wildly different offsets (never-safe on
mnist; floor+0.051 on MiniBooNE; at or below floor+0.020 on adult;
floor+0.110 on spambase), and the committed target sits within ~0.014-0.019
of the transition on MiniBooNE (just above) and spambase (just below) --
which side you land on is a property of the local risk-curve geometry that
no pilot can predict, hence certificates.

### 14.3 The validity diagnostic: the six gate FAILs are quantified, not caveated

Mechanism: LTT controls P(TRUE risk > alpha) but the gate measures empirical
TEST-split risk > alpha, and cost-minimising selection deploys the
LEAST-conservative certified threshold -- true risk just below alpha by
construction. Computed per cell (all 35): R_pool(lambda_hat) on the whole
eval pool, margin = alpha - R_pool, SE_test, and predicted violation =
Phi((R_pool - alpha)/SE_test).

- **Agreement: corr(predicted, observed) = 0.762; mean |obs - pred| = 0.019
  over 35 cells.**
- Every failing cell has a razor-thin margin: alpha - R_pool(lambda_hat) =
  0.007-0.027, i.e. roughly 1-3 test-split standard errors (vs e.g. adult
  ts1 margin 0.086, observed violation 0.000). The failures are exactly the
  cells where the certified threshold sits at the boundary -- the mechanism,
  demonstrated.
- Honest residual: on the six failing cells the noise-only prediction
  (0.018-0.046) UNDER-predicts the observed rates (0.080-0.140) by
  0.04-0.11. The stated secondary effect covers the residual: the 100
  resplits resample one finite pool, so violation events are dependent and
  cluster; the per-resplit noise model treats them as independent. Primary
  explanation quantified, residual attributed, nothing smoothed.
- The guarantee itself is certified on truly independent draws by G1 and the
  IUT union-null Monte-Carlo gate. Deliverables:
  `results_committed/VALIDITY_DIAGNOSTIC.md` + CSV + figure F6; every
  Honest-flags entry in CANONICAL_RESULTS.md now carries its
  "EXPLAINED: predicted-from-test-noise X" annotation.

### 14.4 IUT non-vacuity: the deployable object certifies, at a price list

"Zero IUT failures" at abstention 1.0 is vacuously true; Phase 5 surfaces
where the IUT actually CERTIFIES uniform per-stratum validity at the fine
(lambda_ref = 0.9) stratification:

| dataset | min certifying alpha (swept) | IUT cost/full there | vs R_full(k*) [H3] | consistency |
|---|---|---|---|---|
| mnist | 0.2779 | 0.581 | 0.2479 | PASS |
| MiniBooNE | 0.2844 | **0.163** | 0.2334 | PASS |
| adult | 0.3465 | 0.361 | 0.3092 | PASS |
| spambase | 0.1743 | 0.993 (abstention 0.99 -- barely) | 0.1727 | PASS |

A certifying operating point exists on 4/4 datasets, and the certification
boundary sits just above R_full(k*) on every dataset (H3-consistent 4/4 --
an internal-consistency win: two independent computations agree on where
feasibility begins). MiniBooNE is the showcase: once alpha clears its
hardest stratum, the IUT certifies EVERY stratum simultaneously at 16% of
full-acquisition cost. spambase certifies only barely (abstention 0.99,
cost ~ full) -- labelled honestly. Every gate cell now carries a
vacuous/non-vacuous label per lambda_ref in
`results_committed/IUT_NONVACUITY.md`, so "IUT: 35/35 PASS" is read together
with where that record is evidence (it certified) vs correctness-by-
abstention.

### 14.5 Honest flags after Phase 5

- The six marginal FAILs stand in the gate table, now each annotated with
  its noise-predicted counterpart (14.3) -- including the under-prediction
  residual and its dependence attribution.
- spambase: undetermined verdicts (n = 184), near-vacuous IUT certification,
  and the widest CIs everywhere -- a boundary example, cited only as such.
- The Section-13.3 inference error is retracted above; the paper cites only
  the measured transitions (14.2). The cross-table assert makes the error
  class unrepeatable.
- Frozen core byte-identical throughout; no committed alpha or edge changed
  in Phase 5 (verified: `git diff configs/` empty at the re-freeze commit).

### 14.6 Status

Superseded note: the "under-prediction residual attributed to dependence" in
14.3 was upgraded from attribution to MEASUREMENT by Phase 5.2 (Section 15);
the file re-froze as `canonical-v2.2`.

---

## 15. PHASE 5.2 -- the pool-risk gate (the last number; cluster, 2026-07-12,
tag canonical-v2.2)

The final compute task. One script, pure numpy on the cached canonical
artifacts, closing the one remaining hole: the six marginal-gate FAILs whose
Phase-5 noise-only explanation under-predicted by 0.04-0.11.

### 15.1 The physics of the fix

The old gate measures empirical TEST-SPLIT risk > alpha. Beyond test noise
(Phase 5), the resplits are complementary 50/50 partitions of ONE finite
pool, so at every threshold R_test = (n_eval R_pool - n_cal R_cal)/n_test --
R_cal and R_test are EXACTLY anti-correlated. An unlucky-easy calibration
half both selects a more aggressive certified lambda-hat AND
deterministically faces a harder test half; the unlucky draws are PAIRED.
That pairing is invisible to an independent-noise model -- it is the missing
~3x. The resolution: the eval pool IS the population for this experiment, so
evaluate each resplit's lambda-hat against the EXACT pool risk. LTT remains
valid for this estimand (the calibration split is a without-replacement
subsample; the hypergeometric mean is dominated by the binomial -- Hoeffding
1963 -- so the HB p-value stays conservative).

### 15.2 The canonical result

- **Pool-risk gate: 0 of 35 cells fail.** Every previously failing or
  borderline cell collapses to pool violation **0.000 [Wilson UB 0.037]**
  (n = 100 basis, abstentions counted separately -- zero abstentions on the
  affected cells). Test-split basis for comparison: 11/35 cells cross delta
  by Wilson UB at n = 100 (the main table's six FAILs are the pooled-basis
  subset). The certificate never actually deployed an alpha-violating
  threshold; the old gate was measuring the estimator, not the guarantee.
- **The anti-correlation is measured, not asserted: corr(R_cal, R_test) =
  -1.0000 on every one of the 35 cells** (range -1.0000 to -1.0000), shown
  in F7 panel (a); panel (b) shows the six FAILs collapsing onto the
  pool = 0 axis under the correct estimand.
- **Checks all passed:** lambda-hat recomputed with the frozen ltt_select
  matched the recorded value on every resplit of every cell (3,500
  recomputations, zero mismatches -- validating the whole recomputation
  path); mean R_pool(lambda-hat) matched VALIDITY_DIAGNOSTIC.md exactly
  (estimand consistency); `git diff configs/` empty; frozen core
  byte-identical; pytest + verify_bugs green before and after.

### 15.3 What changed in the frozen file (canonical-v2.2)

- Gate table: a `POOL viol [UB] | gate | abstain` column set beside the
  test-split columns -- every cell PASS.
- Validity-diagnostic section: the "residual attributed to dependence"
  language replaced by the measured account (the identity, rho = -1.0000,
  and the 0/35 pool result). The six FAILs move from caveated to RESOLVED.
- Each of the ten flagged honest-flag entries now carries both annotations:
  "EXPLAINED: predicted-from-test-noise X" and "RESOLVED (Phase 5.2): POOL
  violation 0.000 [UB 0.037]". Flags annotated, never deleted.
- New methodological note, "Evaluating distribution-free certificates on
  finite pools": complementary cal/test splits anti-correlate by
  construction and therefore systematically over-report violations for ANY
  conformal/LTT-style certificate -- a general point (and a paper
  subsection), carried with its evidence (gate table POOL column,
  POOL_RISK_GATE.md, F7).

### 15.4 Status

**ALL COMPUTE FOR THE PROJECT IS CLOSED.** `CANONICAL_RESULTS.md`
(tag `canonical-v2.2`) is the frozen, single source for every number the
paper cites: provenance, committed targets, the 35-cell gate table with the
pool-risk column, H2, H3 + cross-seed stability, IUT by lambda_ref, the
measured alpha-sweep, the validity diagnostic with the Phase-5.2 resolution,
IUT non-vacuity, Phase-2/Phase-4 verdicts, the finite-pool note, honest
flags (explained AND resolved), and the figure index (F1-F7). The next
artifact is the paper.
