# Phase 5 -- the analysis-only pass (correct, explain, re-freeze): tinyx commands

Phase 5 is pure numpy on cached canonical artifacts: NO training, NO rollouts,
NO sbatch. Everything runs on the login node in minutes. Paste the blocks in
order; STOP if any assert fails.

## Block 0 -- pre-flight

```bash
source /etc/profile && module load python/3.12-conda
cd ~/my_repos/CAFA_exp
git pull                                   # the Phase-5 scripts must be here
source hpc/env.local.sh
source activate "$CAFA_ENV"
export PYTHONPATH="$PWD/src:$PYTHONPATH"

python scripts/verify_bugs.py              # ALL PASS (freeze incl.)
pytest -q                                  # all green
```

## Block 1 -- the three analyses (canonical: metrics from results_committed/metrics)

```bash
# Task 1: corrected alpha-sweep. The committed alpha is a MEASURED grid point;
# the transition is bracketed; the H2 cross-check is asserted per dataset
# (a FAIL here means the two tables disagree -- stop and report).
python scripts/alpha_sweep.py --all --grid-from-floor \
    --include-committed-alpha --bracket --metrics-dir results_committed/metrics

# Task 2: validity-estimator diagnostic (predicted-from-noise vs observed).
python scripts/validity_diagnostic.py --all --metrics-dir results_committed/metrics

# Task 3: IUT non-vacuity (extracted from the sweep; needs Task 1's CSV).
python scripts/iut_nonvacuity.py --all --metrics-dir results_committed/metrics
```

## Block 2 -- re-freeze

```bash
python scripts/make_canonical_results.py --metrics-dir results_committed/metrics \
    --out CANONICAL_RESULTS.md

# copy the Phase-5 artifacts next to the frozen file
cp analysis_v2/ALPHA_SWEEP.md analysis_v2/alpha_sweep.csv \
   analysis_v2/alpha_sweep_transitions.csv \
   analysis_v2/VALIDITY_DIAGNOSTIC.md analysis_v2/validity_diagnostic.csv \
   analysis_v2/IUT_NONVACUITY.md analysis_v2/iut_nonvacuity.csv \
   analysis_v2/iut_nonvacuity_transitions.csv results_committed/
cp figures_v2/F5_*.png figures_v2/F5_*.pdf \
   figures_v2/F6_validity_diagnostic.* results_committed/figures/

# final gates (frozen core byte-identical; no alpha or edge changed --
# git diff on configs must be EMPTY)
python scripts/verify_bugs.py && pytest -q
git diff --stat configs/            # MUST be empty (Phase 5 changes no commitment)

git add CANONICAL_RESULTS.md results_committed/
git commit -m "phase 5: alpha-sweep correction, validity diagnostic, IUT non-vacuity (re-freeze)"
git tag canonical-v2.1
git push && git push --tags
```

## What to check while it runs

- Block 1 / Task 1 prints an `H2 cross-check ... -> PASS` line per dataset.
  This is the automated consistency check that catches the MiniBooNE class of
  error; the script hard-asserts it.
- The corrected verdict-at-committed-alpha table decides N-of-4 for the
  "plugin unsafe at the committed target" sentence -- read it off
  `analysis_v2/ALPHA_SWEEP.md`, do not assume it is still 3.
- Task 2 prints `corr(pred, obs)` -- this is the number that turns the six
  gate FAILs into a quantified measurement artifact.
- Task 3 prints the per-dataset H3-consistency verdicts.
```
