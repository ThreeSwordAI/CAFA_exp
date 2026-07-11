# CAFA v2 -- Project Update

Date: 2026-07-12 (Phase 1 complete on cluster + local replication;
Phase 2 [policy-quality axis] complete locally -- see Section 11)
Scope: everything from the v2 repair work order through the Phase-2 readout.
Canonical Phase-1 results: `results_committed/RESULTS.md` (cluster). Local
runs: `analysis_v2/RESULTS.md`, `analysis_v2/PHASE2_READOUT.md`, `figures_v2/`
(this machine, not pushed).

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

### Not run yet (built and queued, or deferred by design)

- **Phase 2 on the cluster** (canonical ts=0 environment): arrays 8-15 for
  `hpc/pool_rollout.slurm` and `hpc/eval_sweep.slurm`.
- **Phase 2b** (finer axis, eps {0.1, 0.75}): only if the 4-point trend were
  borderline -- the local verdict (frontier flat within datasets) suggests 2b
  would refine the concentration curve, not flip the frontier conclusion.
- **Phase 3**: robustness backbones train_seed {1,2} -- one command per seed.
- **Phase 4**: score ablation (spambase, margin score) -- cell 16 ready.
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
| Local figures F1-F4 (pdf+png, per dataset) | `figures_v2/` (gitignored) |
| Phase-2 figures | `figures_v2/F3_phase2_*`, `F3_phase2_frontier.*`, `F4_phase2.*` |
| Local per-resplit metrics | `metrics_v2/` (gitignored) |
| Local probe commits + manifest (reference) | `results/local_committed/` |
| Pool caches / checkpoints (local) | `results/pool_v2/`, `results/checkpoints_v2/` |
| Cluster per-resplit metrics | cluster: `$CAFA_REPO/metrics_v2/` (not in git) |
| Frozen-file manifest | `repro/MANIFEST.sha256` (cluster hashes) |
| Environment lock (cluster) | `repro/requirements.lock.txt` |

Uncommitted local diffs (intentional, not pushed): `.gitignore` (+`.venv/`),
`scripts/verify_bugs.py` (sha256sum `*` prefix + CRLF-normalization fixes),
`scripts/run_eval_sweep.py` (Phase-2 cells 8-15), `hpc/eval_sweep.slurm`
(Phase-2 array comment), new `scripts/phase2_analyze.py`, `project_update.md`.

---

## 10. Next steps

1. **Send for fork review** (Phase 1e): `results_committed/RESULTS.md` +
   `analysis_v2/PHASE2_READOUT.md` (+, if wanted, the metrics JSONs --
   force-add or copy under a non-ignored name). Explicitly flag: (a) the
   borderline marginal cells and the dependence caveat; (b) plugin-unsafe
   being conditional on tight alpha; (c) the Phase-2 verdict (outcome 2,
   Section 11) including the flat within-dataset frontier and the
   between-dataset confound in the aggregate Spearman.
2. **Phase 2 on the cluster** (canonical): `sbatch --array=8-15
   hpc/pool_rollout.slurm`, `probe_commit.py --extend-edges` x4,
   `sbatch --array=8-15 hpc/eval_sweep.slurm` (keep the --gres line TinyGPU
   requires), then `analyze_results.py` + `phase2_analyze.py`. Commit the
   extended `configs/committed_v2_*.json` and the Phase-2 readout.
3. **Phase 3** robustness backbones (`--train-seed 1/2`; alpha stays ts=0).
4. **Phase 4** score ablation (spambase/margin, cell 16).
5. Housekeeping: commit the code diffs listed above; decide how to version the
   cluster `metrics_v2/` JSONs (the Phase-2 instructions require they reach
   git).

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
