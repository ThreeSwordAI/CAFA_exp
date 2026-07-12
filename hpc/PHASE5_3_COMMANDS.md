# Phase 5.3 -- final claim-validity pass: tinyx commands

Analysis-only on canonical caches + one Bernoulli simulation; login node,
~20-40 minutes total; no sbatch. Paste blocks in order; STOP on any assert
(endpoint reproduction, plugin/lambda-hat reconstruction, aggregate
reconstruction -- each is a hard gate).

## Block 0 -- pre-flight (preserve the previous freeze)

```bash
source /etc/profile && module load python/3.12-conda
cd ~/my_repos/CAFA_exp
git fetch --all --tags
git pull                                   # the Phase-5.3 scripts must be here
git tag --list | tail -3                   # canonical-v2, v2.1, v2.2 must exist
git rev-parse canonical-v2.2
source hpc/env.local.sh
source activate "$CAFA_ENV"
export PYTHONPATH="$PWD/src:$PYTHONPATH"

python scripts/verify_bugs.py              # ALL PASS
pytest -q                                  # all green (incl. tests/test_phase53.py)
```

## Block 1 -- the seven analyses (order matters: family before iut; all before audit)

```bash
python scripts/phase5_provenance.py \
  --metrics-dir results_committed/metrics \
  --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed

python scripts/family_wide_feasibility.py \
  --all-primary --all-thresholds --all-depths --gamma 0.05 \
  --metrics-dir results_committed/metrics \
  --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed
# WATCH: "endpoint reproduction PASS" x4, then the PRIMARY verdict lines
# (threshold + depth verdict per dataset -- these decide the paper story).

python scripts/pool_plugin_eval.py \
  --all-cells --alpha-sweep \
  --metrics-dir results_committed/metrics \
  --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed
# WATCH: per-cell "pool exceed" lines; a PLUGIN RECONSTRUCTION FAIL assert
# means the recomputation path diverged -- stop and report.

python scripts/pool_stratum_eval.py \
  --all-cells --all-lambda-ref \
  --metrics-dir results_committed/metrics \
  --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed

python scripts/iut_by_lambda_ref.py \
  --all-cells --lambda-ref 0.5 0.7 0.9 \
  --metrics-dir results_committed/metrics \
  --pool-dir "$RESULTS_ROOT/pool_v2" --output-dir results_committed
# WATCH: the summary line (non-vacuous count, refusal classes A/B/C).

python scripts/synthetic_power.py \
  --alpha 0.15 --gamma 0.05 --repetitions 5000 --output-dir results_committed
# WATCH: "max null FPR ... (gamma 0.05)" -- must be <= gamma up to MC noise.

python scripts/final_claim_audit.py \
  --results-dir results_committed --output-dir results_committed
# WATCH: "outcome A/B/C" -- the licensed story; and the prohibited-phrase count.
```

## Block 2 -- gates + re-freeze as canonical-v2.3

```bash
python scripts/verify_bugs.py && pytest -q
git diff --quiet configs/ && echo "configs untouched: OK"    # MUST print OK
git status --short                          # only new results_committed files + none in src

git add results_committed/ scripts/ tests/
git commit -m "phase 5.3: final claim-validity audit and corrected pool analyses"
git tag -a canonical-v2.3 -m "CAFA canonical v2.3: final AAAI claim-validity freeze"
git push && git push --tags
```

(The CANONICAL_RESULTS.md / RESULTS_FOR_PAPER.md / project_update.md rewrite
happens AFTER these outputs are pulled back locally and read -- the paper
story must be selected FROM the decision file, never before it exists.)

## What decides what

- FAMILY_WIDE_FEASIBILITY.md primary table -> Outcome A (family-wide failure)
  vs B (endpoint-only) vs C (unresolved), per dataset.
- POOL_PLUGIN_EVAL.md -> whether any plugin-unsafe headline survives, as
  exact "x/100 pool exceedance" numbers with the three-way label.
- POOL_STRATUM_EVAL.md -> what replaces 0.3005 / 0.3559 / 0.3136 / 0.3844
  (the selected-rule deepest-stratum POOL risks) and the corrected
  ratio-to-alpha range; F1_pool_corrected is the new Figure 1.
- IUT_BY_LAMBDA_REF.md + IUT_OUTCOME_CLASSIFICATION.md -> the 105-config
  accounting that replaces "35/35 IUT".
- SYNTHETIC_POWER.md -> the prospective power validation (FPR control +
  power surfaces).
- FINAL_CLAIM_DECISION.md -> the licensed thesis sentence + the
  prohibited-phrase hit list to clean in the writing pass.
```
