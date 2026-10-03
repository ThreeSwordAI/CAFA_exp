#!/bin/bash
#SBATCH --job-name=cafa_v3_backbone
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=04:00:00
# v3 backbones, one array task per (dataset, train_seed): task i -> dataset index i % 8, seed i / 8 (24 tasks).
# Datasets in the order csv:physionet cube tabular:adult csv:diabetes tabular:MiniBooNE mnist fashionmnist image:imagenette
#   all:              sbatch --array=0-23 hpc/backbone_v3.slurm
#   Imagenette only:  sbatch --array=7,15,23 hpc/backbone_v3.slurm
# Existing checkpoints are skipped. CUBE and MiniBooNE: the local seed-0 runs missed the full-observation
# target with the config's 40 epochs and were retrained once with --epochs 60 (see handoff.md section 6.3);
# pass the same override for their seeds 1-2 by setting CAFA_EXTRA when submitting those tasks
# (cube = tasks 9, 17; MiniBooNE = tasks 12, 20):
#   CAFA_EXTRA="--epochs 60" sbatch --export=ALL --array=9,12,17,20 hpc/backbone_v3.slurm
#   sbatch --array=8,10,11,13,14,15,16,18,19,21,22,23 hpc/backbone_v3.slurm    # the other seeds 1-2 (incl. Imagenette)
# Exact submission lines: hpc/README_v3.md.  CAFA_DRIVER_FLAGS (e.g. --dry-run) is appended to the driver
# call (hpc/dry_run_v3.sh).
# -u only after the environment is loaded: the cluster login profile (and module / conda activate) are not
# `set -u` clean -- round 3 on Alex: array job 4439177 failed with
# "/etc/profile.d/debuginfod.sh: line 8: DEBUGINFOD_URLS: unbound variable" (handoff.md section 13.8)
set -eo pipefail
source /etc/profile
module load python/3.12-conda
cd "${CAFA_REPO:-$SLURM_SUBMIT_DIR}"
if [ -f hpc/env.local.sh ]; then source hpc/env.local.sh; fi
source activate "${CAFA_ENV:?CAFA_ENV not set - create hpc/env.local.sh from hpc/env.local.template.sh}"
set -u
: "${DATA_ROOT:?DATA_ROOT not set - add it to hpc/env.local.sh}"
: "${RESULTS_ROOT:?RESULTS_ROOT not set - add it to hpc/env.local.sh}"
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
DS=(csv:physionet cube tabular:adult csv:diabetes tabular:MiniBooNE mnist fashionmnist image:imagenette)
ds=${DS[$((SLURM_ARRAY_TASK_ID % 8))]}
ts=$((SLURM_ARRAY_TASK_ID / 8))
python scripts/drive_v3.py --phase backbones --datasets "$ds" --seeds "$ts" --device "${CAFA_DEVICE:-cuda}" \
    --extra-args="${CAFA_EXTRA:-}" ${CAFA_DRIVER_FLAGS:-}
