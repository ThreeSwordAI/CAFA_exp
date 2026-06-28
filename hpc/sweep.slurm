#!/bin/bash
#SBATCH --job-name=cafa_sweep
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#   sbatch --array=0-19%8 --output="$RESULTS_ROOT/logs/%x_%A_%a.out" \
#          --error="$RESULTS_ROOT/logs/%x_%A_%a.err" hpc/sweep.slurm mnist greedy_entropy
set -euo pipefail
source /etc/profile
module load python/3.12-conda
source activate "$CAFA_ENV"
cd "$CAFA_REPO"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$CAFA_REPO/src:${PYTHONPATH:-}"
python scripts/run_experiment.py --dataset "${1:?dataset}" --backbone "${2:?backbone}" --seed-index "$SLURM_ARRAY_TASK_ID" --device cuda