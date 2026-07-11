#!/bin/bash
#SBATCH --job-name=cafa_pool_rollout
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
# Array over the WO-8 cell list (run_pool_rollout.py --cell):
#   Phase-1 : --array=0-7    (4 datasets x 2 policies; MNIST is the GPU-worthwhile cell)
#   Phase-2 : --array=8-15   (tabular x3 + mnist, x eps in {0.25, 0.5})
#   Phase-5 : --array=16     ((tabular:spambase, greedy_entropy, score=margin))
#   sbatch --array=0-7 --output="$RESULTS_ROOT/logs/%x_%A_%a.out" \
#          --error="$RESULTS_ROOT/logs/%x_%A_%a.err" hpc/pool_rollout.slurm
# Preamble copied from hpc/sweep.slurm (FAU NHR conventions; no --mem on tinygpu),
# hardened for batch jobs that do NOT inherit the login shell's exports:
# the repo comes from $SLURM_SUBMIT_DIR (submit from the repo root) and the
# env vars (CAFA_ENV, DATA_ROOT, RESULTS_ROOT) come from hpc/env.local.sh
# (gitignored; copy hpc/env.local.template.sh and fill in your paths).
set -euo pipefail
source /etc/profile
module load python/3.12-conda
cd "${CAFA_REPO:-$SLURM_SUBMIT_DIR}"
if [ -f hpc/env.local.sh ]; then source hpc/env.local.sh; fi
source activate "${CAFA_ENV:?CAFA_ENV not set - create hpc/env.local.sh from hpc/env.local.template.sh}"
: "${DATA_ROOT:?DATA_ROOT not set - add it to hpc/env.local.sh}"
: "${RESULTS_ROOT:?RESULTS_ROOT not set - add it to hpc/env.local.sh}"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/run_pool_rollout.py --cell "$SLURM_ARRAY_TASK_ID" --device "${CAFA_DEVICE:-cuda}"
