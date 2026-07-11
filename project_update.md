# CAFA v2 -- Project Update

Date: 2026-07-11 (Phase 1 complete on cluster + full local replication)
Scope: everything from the v2 repair work order through the first full results.
Canonical results: `results_committed/RESULTS.md` (cluster). Local replication:
`analysis_v2/RESULTS.md` + `figures_v2/` (this machine, not pushed).

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

### Not run yet (built and queued, or deferred by design)

- **Phase 2**: epsilon-greedy mixtures (eps 0.25/0.5) -- code + cells 8-15
  ready, `--extend-edges` path implemented; not submitted.
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
| Local figures F1-F4 (pdf+png, per dataset) | `figures_v2/` (gitignored) |
| Local per-resplit metrics | `metrics_v2/` (gitignored) |
| Local probe commits + manifest (reference) | `results/local_committed/` |
| Pool caches / checkpoints (local) | `results/pool_v2/`, `results/checkpoints_v2/` |
| Cluster per-resplit metrics | cluster: `$CAFA_REPO/metrics_v2/` (not in git) |
| Frozen-file manifest | `repro/MANIFEST.sha256` (cluster hashes) |
| Environment lock (cluster) | `repro/requirements.lock.txt` |

Uncommitted local diffs (intentional, not pushed): `.gitignore` (+`.venv/`),
`scripts/verify_bugs.py` (sha256sum `*` prefix parsing fix).

---

## 10. Next steps

1. **Send for fork review** (Phase 1e): `results_committed/RESULTS.md` +, if
   wanted, the metrics JSONs (force-add or copy under a non-ignored name).
   Explicitly flag: (a) the two borderline marginal cells and the dependence
   caveat; (b) plugin-unsafe being conditional on tight alpha; (c) the mixed
   concentration evidence. The fork verdict decides the paper's framing.
2. **Phase 2** (pre-approved to queue): `sbatch --array=8-15
   hpc/pool_rollout.slurm`, then `probe_commit.py --extend-edges`, eval, and
   re-analysis.
3. **Phase 3** robustness backbones (`--train-seed 1/2`; alpha stays ts=0).
4. **Phase 4** score ablation (spambase/margin, cell 16).
5. Housekeeping: commit the verify_bugs parser fix and the `.gitignore` line;
   decide how to version the cluster `metrics_v2/` JSONs.
