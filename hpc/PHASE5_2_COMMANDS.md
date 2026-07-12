# Phase 5.2 -- the pool-risk gate (the last number): tinyx commands

Pure numpy on cached canonical artifacts; login node, minutes; no sbatch.
Paste blocks in order; STOP if any assert fails (the script hard-asserts the
lambda-hat determinism check and the estimand cross-check).

## Block 0 -- pre-flight

```bash
source /etc/profile && module load python/3.12-conda
cd ~/my_repos/CAFA_exp
git pull                                   # pool_risk_gate.py must be here
source hpc/env.local.sh
source activate "$CAFA_ENV"
export PYTHONPATH="$PWD/src:$PYTHONPATH"

python scripts/verify_bugs.py              # ALL PASS
pytest -q                                  # all green
```

## Block 1 -- the pool-risk gate (canonical)

```bash
# Needs analysis_v2/validity_diagnostic.csv for the estimand cross-check; the
# canonical one is in results_committed/ from Phase 5 -- stage it:
mkdir -p analysis_v2
cp results_committed/validity_diagnostic.csv analysis_v2/

python scripts/pool_risk_gate.py --all --metrics-dir results_committed/metrics
# Watch for:
#  - "estimand cross-check vs validity_diagnostic.csv: PASS (35 cells)"
#  - the headline line: "N/35 cells fail the pool-risk gate ... corr(R_cal, R_test) = ..."
#  - any DETERMINISM FAIL assert would stop the script -- report it, do not work around.
```

## Block 2 -- re-freeze as canonical-v2.2

```bash
# Stage the other Phase-5 CSVs the generator reads (canonical versions):
cp results_committed/alpha_sweep.csv results_committed/alpha_sweep_transitions.csv \
   results_committed/iut_nonvacuity_transitions.csv analysis_v2/ 2>/dev/null || true

python scripts/make_canonical_results.py --metrics-dir results_committed/metrics \
    --out CANONICAL_RESULTS.md

cp analysis_v2/POOL_RISK_GATE.md analysis_v2/pool_risk_gate.csv results_committed/
cp figures_v2/F7_pool_risk_gate.* results_committed/figures/

python scripts/verify_bugs.py && pytest -q
git diff --quiet configs/ && echo "configs untouched: OK"   # MUST print OK

git add CANONICAL_RESULTS.md results_committed/
git status                                  # verify what is staged
git commit -m "phase 5.2: pool-risk gate + anti-correlation; six marginal FAILs resolved"
git tag canonical-v2.2
git push && git push --tags
```

## What the numbers mean

- POOL violation = R_pool(lambda_hat) > alpha with lambda_hat from each
  resplit's calibration half and R_pool the EXACT risk on the whole eval pool
  (the population for this experiment). Expected ~0/35 given the positive
  margins in the validity diagnostic; if a cell genuinely fails, report it as
  a real finding -- do not smooth.
- corr(R_cal, R_test) at fixed lambda should be ~ -1 (complementary halves of
  one pool). This measured number is what upgrades the dependence caveat to a
  demonstrated mechanism.
```
