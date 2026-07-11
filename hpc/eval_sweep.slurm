#!/bin/bash
#SBATCH --job-name=cafa_eval_sweep
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
# CPU array over the run_eval_sweep.py --cell list:
#   Phase-1 : --array=0-7    (4 datasets x 2 policies)
#   Phase-2 : --array=8-15   ([adult, MiniBooNE, spambase, mnist] x eps in {0.25, 0.5})
#   sbatch --array=0-7 --output="$RESULTS_ROOT/logs/%x_%A_%a.out" \
#          --error="$RESULTS_ROOT/logs/%x_%A_%a.err" hpc/eval_sweep.slurm
# The eval sweep is torch-free and CPU-only; no --gres / no --mem (tinygpu convention).
# Preamble copied from hpc/sweep.slurm (minus the GPU request), hardened for batch
# jobs that do NOT inherit the login shell's exports: the repo comes from
# $SLURM_SUBMIT_DIR (submit from the repo root) and the env vars (CAFA_ENV,
# DATA_ROOT, RESULTS_ROOT) come from hpc/env.local.sh (gitignored; copy
# hpc/env.local.template.sh and fill in your paths).
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
python scripts/run_eval_sweep.py --cell "$SLURM_ARRAY_TASK_ID"
