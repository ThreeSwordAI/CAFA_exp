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
# Preamble copied verbatim from hpc/sweep.slurm (FAU NHR conventions; no --mem on tinygpu).
set -euo pipefail
source /etc/profile
module load python/3.12-conda
source activate "$CAFA_ENV"
cd "$CAFA_REPO"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$CAFA_REPO/src:${PYTHONPATH:-}"   # ADJUST IF NEEDED (or $SLURM_SUBMIT_DIR/src)
python scripts/run_pool_rollout.py --cell "$SLURM_ARRAY_TASK_ID" --device "${CAFA_DEVICE:-cuda}"
