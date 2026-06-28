#!/bin/bash
#SBATCH --job-name=cafa_train
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
# Pass log paths at submit time (env vars expand in your shell):
#   sbatch --output="$RESULTS_ROOT/logs/%x_%j.out" --error="$RESULTS_ROOT/logs/%x_%j.err" \
#          hpc/train.slurm mnist greedy_entropy
set -euo pipefail
source /etc/profile
module load python/3.12-conda
source activate "$CAFA_ENV"
cd "$CAFA_REPO"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$CAFA_REPO/src:${PYTHONPATH:-}"
python scripts/train_backbone.py --dataset "${1:?dataset}" --backbone "${2:?backbone}" --device cuda