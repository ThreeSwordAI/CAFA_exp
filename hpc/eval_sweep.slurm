#!/bin/bash
#SBATCH --job-name=cafa_eval_sweep
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
# CPU array over the WO-10 Phase-1 cells (run_eval_sweep.py --cell):
#   Phase-1 : --array=0-7    (4 datasets x 2 policies)
#   sbatch --array=0-7 --output="$RESULTS_ROOT/logs/%x_%A_%a.out" \
#          --error="$RESULTS_ROOT/logs/%x_%A_%a.err" hpc/eval_sweep.slurm
# The eval sweep is torch-free and CPU-only; no --gres / no --mem (tinygpu convention).
# Preamble copied verbatim from hpc/sweep.slurm (minus the GPU request).
set -euo pipefail
source /etc/profile
module load python/3.12-conda
source activate "$CAFA_ENV"
cd "$CAFA_REPO"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$CAFA_REPO/src:${PYTHONPATH:-}"   # ADJUST IF NEEDED (or $SLURM_SUBMIT_DIR/src)
python scripts/run_eval_sweep.py --cell "$SLURM_ARRAY_TASK_ID"
