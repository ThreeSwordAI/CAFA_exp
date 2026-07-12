#!/bin/bash
#SBATCH --job-name=cafa_train_v2
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=04:00:00
# Train all four v2 backbones for ONE train seed (script argument $1, default 0):
#   sbatch hpc/train_backbone_v2.slurm 1
# Preamble matches pool_rollout.slurm (batch jobs do not inherit login exports;
# submit from the repo root; put CAFA_ENV/DATA_ROOT/RESULTS_ROOT in hpc/env.local.sh).
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
TS="${1:-0}"
python scripts/train_backbone_v2.py --dataset mnist             --train-seed "$TS" --device cuda
python scripts/train_backbone_v2.py --dataset tabular:adult     --train-seed "$TS" --device cuda
python scripts/train_backbone_v2.py --dataset tabular:MiniBooNE --train-seed "$TS" --device cuda
python scripts/train_backbone_v2.py --dataset tabular:spambase  --train-seed "$TS" --device cuda
