#!/bin/bash
#SBATCH --job-name=cafa_v3_backbone
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=04:00:00
# v3 backbones, one array task per (dataset, train_seed): task i -> dataset index i % 8, seed i / 8 (24 tasks).
# Datasets in the order csv:physionet cube tabular:adult csv:diabetes tabular:MiniBooNE mnist fashionmnist image:imagenette
#   all:              sbatch --array=0-23 hpc/backbone_v3.slurm
#   Imagenette only:  sbatch --array=7,15,23 hpc/backbone_v3.slurm
# Existing checkpoints are skipped. CUBE: the local seed-0 run missed the full-observation target with the
# config's 40 epochs and was retrained once with --epochs 60 (see handoff.md section 6); pass the same
# override for CUBE seeds 1-2 by setting CAFA_EXTRA="--epochs 60" when submitting the CUBE tasks
# (sbatch --array=9,17 --export=ALL,CAFA_EXTRA="--epochs 60" hpc/backbone_v3.slurm).
set -euo pipefail
source /etc/profile
module load python/3.12-conda
cd "${CAFA_REPO:-$SLURM_SUBMIT_DIR}"
if [ -f hpc/env.local.sh ]; then source hpc/env.local.sh; fi
source activate "${CAFA_ENV:?CAFA_ENV not set - create hpc/env.local.sh from hpc/env.local.template.sh}"
: "${DATA_ROOT:?DATA_ROOT not set - add it to hpc/env.local.sh}"
: "${RESULTS_ROOT:?RESULTS_ROOT not set - add it to hpc/env.local.sh}"
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
DS=(csv:physionet cube tabular:adult csv:diabetes tabular:MiniBooNE mnist fashionmnist image:imagenette)
ds=${DS[$((SLURM_ARRAY_TASK_ID % 8))]}
ts=$((SLURM_ARRAY_TASK_ID / 8))
python scripts/drive_v3.py --phase backbones --datasets "$ds" --seeds "$ts" --device "${CAFA_DEVICE:-cuda}" \
    --extra-args="${CAFA_EXTRA:-}"
