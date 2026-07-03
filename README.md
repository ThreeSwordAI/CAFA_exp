# CAFA -- Distribution-free risk-controlled stopping for Active Feature Acquisition

## 1. What this is

CAFA is a distribution-free stopping rule for active feature acquisition. A
frozen masked predictor and a frozen acquisition policy generate per-instance
acquisition trajectories; Learn-then-Test (Hoeffding-Bentkus p-values with
fixed-sequence FWER control) certifies stopping thresholds `lambda` whose
prediction-at-stop controls a target risk `alpha` at confidence `1 - delta`; the
cheapest certified `lambda` is deployed.

> Guarantee. For the deployed threshold `lambda_hat`,
> `P_over_calibration_draws( R(lambda_hat) > alpha ) <= delta`.
> The per-stratum-valid variant (CAFA-IUT) strengthens this to
> `P( exists stratum k : R(lambda_hat | k) > alpha ) <= delta` -- one `lambda`
> certified simultaneously against every reference-depth stratum, with no
> per-stratum routing.

---

## 2. Status -- v2 repair + rigor release

This release makes the fixes for five evidence-invalidating issues *structural*
(asserted, pre-committed, cached, reproducible) rather than patched. The pure
risk-control core (`src/cafa/risk_control.py`) is byte-frozen and unchanged.

- C1 -- the tabular greedy policy scored candidates using their *true* value
  (clairvoyant). Fixed: candidates are imputed at their train column means; no
  unpaid value reaches the predictor.
- C2 -- every seed re-permuted the whole 70k pool, leaking ~60% of cal/test into
  train. Fixed: fixed-train / resplit-heldout -- one backbone per
  `(dataset, train_seed)`; only the heldout pool is resplit.
- C3 -- Mondrian stratum edges were fit on the calibration set used for
  selection. Fixed: edges are committed from an independent probe split
  (seed 777) before any selection runs.
- C4 -- per-stratum threshold *routing* was circular / not deployable. Fixed:
  the deployable per-stratum-valid object is CAFA-IUT (a single certified
  `lambda`); per-stratum thresholds are audit-only.
- C5 -- a hand-set `alpha` violated the project's own fixed-`alpha` rule. Fixed:
  `alpha` is computed only by `feasible_alpha_from_floor` on the probe and
  committed to JSON (value: TBD-RUN, produced on the cluster).

---

## 3. Repo layout

```
CAFA_exp/
  CLAUDE_CODE_WORKORDER.md      # authoritative spec for the v2 release
  src/cafa/
    risk_control.py             # * FROZEN -- pure LTT selector (arrays in, selection out)
    risk_control_ext.py         # v2: CAFA-IUT (composes only frozen primitives)
    splits.py                   # v2: fixed-train / probe / resplit + disjointness asserts
    pool.py                     # v2: pool-rollout cache format + post-hoc cost math
    policies_v2.py              # v2: epsilon-greedy mixture (tabular)
    repro_utils.py              # v2: file_sha256 helper
    data.py                     # + load_mnist_pool / load_tabular_pool (v2; legacy loaders intact)
    tabular.py                  # C1 fix (mean-imputation greedy)
    acquisition.py              # image policies + rollout (frozen loop; honest docstring)
    models.py, scores.py, metrics.py, config.py
  scripts/
    train_backbone_v2.py        # v2 backbone (fixed train split)
    run_pool_rollout.py         # v2 rollout of the whole heldout pool (records `order`)
    probe_commit.py             # v2 commit alpha / edges / costs (pre-committed)
    run_eval_sweep.py           # v2 resplit engine -> metrics_v2/*.json
    analyze_results.py          # v2 -> analysis_v2/RESULTS.md + CSVs
    make_figures_v2.py          # v2 figures F1-F4
    verify_bugs.py              # v2 verification-first bug script (C1/C2/freeze)
    run_experiment, run_mondrian[_mnist], aggregate_results, make_figures,
    alpha_probe, step5_*        # DEPRECATED -- kept for provenance, do not use
  hpc/  train.slurm, sweep.slurm (legacy) ; pool_rollout.slurm, eval_sweep.slurm (v2)
  repro/  make_manifest.sh, verify_freeze.sh, MANIFEST.sha256, BUGLOG.md, requirements.lock.txt
  configs/  experiment.yaml (+ protocol_v2 block) ; committed_v2_*.json (written by probe_commit)
  results_committed/            # tracked; operator copies final RESULTS.md + JSONs here
  tests/
    test_risk_control.py        # * FROZEN -- G1 validity gate
    test_policy_honesty.py, test_splits_v2.py, test_pool_v2.py,
    test_iut.py, test_probe_commit.py   # v2 tests
    test_mondrian.py, test_baselines.py, test_pipeline.py
```

---

## 4. Environment

```bash
# FAU NHR (TinyGPU / Alex): add torch to the existing vault env (do NOT recreate it).
module load python/3.12-conda
source activate "$CAFA_ENV"
pip install torch torchvision        # or the CUDA build via the pytorch index-url
# On a laptop instead: conda env create -f environment.yml && conda activate cafa
```

The torch-free path (risk control, splits, pool math, probe, eval sweep,
analysis, figures) imports without torch; `cafa.models` / `cafa.acquisition`
import torch lazily. Record the exact environment once on the cluster:

```bash
pip freeze > repro/requirements.lock.txt     # then commit
```

---

## 5. Data download (one-time, login node with internet)

```bash
# MNIST (torchvision) into $DATA_ROOT
python -c "import torchvision,os; r=os.environ['DATA_ROOT']; \
  torchvision.datasets.MNIST(r,train=True,download=True); \
  torchvision.datasets.MNIST(r,train=False,download=True)"

# OpenML tabular (adult v2, MiniBooNE v1, spambase v1) into $DATA_ROOT (cached for offline nodes)
python -c "from sklearn.datasets import fetch_openml; import os; h=os.environ['DATA_ROOT']; \
  fetch_openml('adult',version=2,data_home=h,as_frame=True); \
  fetch_openml('MiniBooNE',version=1,data_home=h,as_frame=True); \
  fetch_openml('spambase',version=1,data_home=h,as_frame=True)"
```

---

## 6. Pipeline (the exact cluster command sequence)

Environment (once per session):

```bash
module load python/3.12-conda
source activate "$CAFA_ENV"
export CAFA_REPO=~/my_repos/CAFA_exp        # adjust
cd "$CAFA_REPO"
export PYTHONPATH="$PWD/src:$PYTHONPATH"
# DATA_ROOT / RESULTS_ROOT already exported per legacy setup
```

Phase 0 -- verify before compute (login node, ~5 min):

```bash
pytest -q                                    # all tests incl. new v2 tests must pass
bash repro/make_manifest.sh                  # FIRST TIME ONLY (records frozen hashes)
python scripts/verify_bugs.py                # expect: C1 PASS, C2 legacy table + v2 PASS, freeze PASS
pip freeze > repro/requirements.lock.txt     # commit this
```

Gate: proceed only if everything passes. Append verify output to repro/BUGLOG.md and commit.

Phase 1a -- backbones (primary train seed):

```bash
python scripts/train_backbone_v2.py --dataset mnist            --train-seed 0 --device cuda   # or cpu
for d in adult MiniBooNE spambase; do
  python scripts/train_backbone_v2.py --dataset tabular:$d --train-seed 0 --device cpu
done
```

Phase 1b -- pool rollouts (8 cells; GPU for MNIST recommended):

```bash
sbatch --array=0-7 hpc/pool_rollout.slurm
# equivalently, serially: python scripts/run_pool_rollout.py --cell K --device cpu   (K=0..7)
```

Phase 1c -- probe commit (login node, seconds; COMMIT the JSONs it writes):

```bash
for d in mnist tabular:adult tabular:MiniBooNE tabular:spambase; do
  python scripts/probe_commit.py --dataset $d --train-seed 0
done
git add configs/committed_v2_*.json && git commit -m "v2: committed probe artifacts (alpha, edges, costs)"
```

Phase 1d -- eval sweep + analysis (CPU, fast):

```bash
sbatch --array=0-7 hpc/eval_sweep.slurm      # or serially: run_eval_sweep.py --cell K
python scripts/analyze_results.py
python scripts/make_figures_v2.py
```

Phase 1e -- SEND RESULTS FOR THE FORK REVIEW. Copy `analysis_v2/RESULTS.md`
(and, if size permits, `metrics_v2/`) into `results_committed/`, commit, and send
to the reviewer. Do not draft paper text before the fork verdict.

Phase 2 -- epsilon-greedy axis (queue anytime after 1d):

```bash
sbatch --array=8-15 hpc/pool_rollout.slurm    # eps cells per the runner's documented list
python scripts/probe_commit.py --dataset $d --train-seed 0 --extend-edges   # edges only; alpha/floor unchanged
sbatch --array=... hpc/eval_sweep.slurm       # eps cells
python scripts/analyze_results.py && python scripts/make_figures_v2.py
```

Phase 3 -- robustness backbones (ts 1, 2), later: rerun 1a-1d with
`--train-seed 1` / `2`; analysis auto-groups by ts; `alpha` stays the ts=0
committed value.

Phase 4 -- score ablation (spambase/margin), later: pool-rollout cell 16 + one
eval cell per the config's `score_ablation`.

---

## 7. Split & pre-commitment scheme

```
pool (dataset)
  |-- fixed_train_heldout(train_seed)  -->  train(ts) (60%)  -->  backbone (one per dataset,ts)
  |
  +-- heldout (40%)
        |-- probe_eval_split(probe_seed=777)
        |     |-- probe (10% of heldout)  -->  COMMIT: {alpha, stratum edges, feature costs}
        |     |                                 (configs/committed_v2_*.json)
        |     +-- eval  (90% of heldout)  -->  100 x resplit_cal_test  -->  cal / test
        |
        +-- invariant: train, probe, eval pairwise disjoint (asserted at load);
                       (train + probe) never enters selection or evaluation;
                       edges / alpha / costs are functions of (train, probe) only.
```

---

## 8. Methods glossary

- cafa_marginal -- the frozen LTT selector: one certified `lambda` controlling
  marginal risk; `P(R(lambda_hat) > alpha) <= delta`.
- cafa_iut -- the deployable per-stratum-valid method: a single `lambda`
  certified simultaneously against every stratum via the intersection-union test
  (union-null p-value = max over strata of the frozen per-stratum HB p-value),
  guaranteeing `P(exists k: R(lambda_hat | k) > alpha) <= delta`; global
  abstention -> full acquisition when a stratum is `alpha`-infeasible.
- mondrian_audit -- the frozen per-bucket selector run per reference-depth
  stratum (joint=False and joint=True). Audit only: per-stratum risk / certify /
  abstain are reported, but no per-stratum *cost* operating point is computed
  (the routing is circular; see C4).
- baselines -- plugin (empirical-risk threshold, no correction), fixed
  confidence, fixed budget. None carries a finite-sample guarantee.
- oracles -- cheapest-valid (uses test labels; cost floor) and full-feature
  (risk floor). Non-deployable reference bounds.
- Cost-blindness lemma -- in the scalar (`lambda`-only) family, cost is monotone
  in the grid index, so the cheapest certified `lambda` equals the smallest
  certified index; the cost minimisation is effectively cost-blind here (stated,
  not hidden).

---

## 9. Outputs schema

- `metrics_v2/{dsname}_ts{ts}_{policy}.json` --
  `{meta, alpha, delta, grid, lambda_refs: {lr: {population: {...}, resplits: [{seed, schemes: {...}, mondrian_audit, marginal_per_stratum_risk, iut_per_stratum_risk, ...}]}}}`.
- `analysis_v2/RESULTS.md` (+ `h2_table.csv`, `audit_table.csv`,
  `fork_strata.csv`, `detection_scatter.csv`) -- header, H2 validity/efficiency
  (Wilson CIs), per-stratum audit (three-way verdicts), IUT-vs-marginal, fork
  metrics, binning ablation, GATES.
- `figures_v2/F1..F4.{pdf,png}` -- realized (risk, cost); per-stratum risk;
  strata-count + depth IQR; detection scatter.

All empirical values are computed on the cluster; the repo ships no numbers
(placeholders read `TBD-RUN`).

---

## 10. Tests & gates

```bash
pytest -q                     # G1 (frozen) + v2 tests (splits, pool, IUT, honesty, probe)
python scripts/verify_bugs.py # C1 honesty, C2 leak-vs-v2, freeze check
bash repro/verify_freeze.sh   # frozen files match repro/MANIFEST.sha256
```

The RESULTS.md GATES block reports, per dataset: marginal violation fraction vs
`delta` (Wilson upper bound) and IUT any-stratum violation vs `delta`.

---

## 11. Reproducibility (fixed seeds)

| stream | seed / rule |
|---|---|
| train split (backbone) | `train_seed` (primary 0; robustness 1, 2) |
| probe split | `probe_seed = 777` (fixed) |
| resplit cal/test | `1_000_000 + resplit_seed` (offset avoids collisions) |
| random policy | `train_seed` |
| epsilon-greedy policy | `10_000 + round(1000 * epsilon)` |

Every random draw is seeded from these named values; identical inputs reproduce
identical outputs. Disjointness and edge-provenance are runtime assertions.

---

## 12. Deprecated / provenance

The legacy scripts (`run_experiment.py`, `run_mondrian.py`,
`run_mondrian_mnist.py`, `aggregate_results.py`, `make_figures.py`,
`alpha_probe.py`, `step5_*`) carry a DEPRECATED header and are retained only for
provenance. They contain the pre-fix pipeline (per-seed reshuffle, cal-fit edges,
clairvoyant tabular greedy, `lambda_ref`-duplicated marginal counting) and must
not be used for paper numbers. Use the v2 pipeline in section 6.
