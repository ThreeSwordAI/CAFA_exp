#!/bin/bash
#SBATCH --job-name=cafa_v3_rollout
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=08:00:00
# v3 rollouts, one array task per line of hpc/cells_v3.txt ("<dataset> <policy> <train_seed>"; 48 lines).
# Line i (0-based) = 16*ts + 2*dataset_index + policy_index, datasets in the order
#   csv:physionet cube tabular:adult csv:diabetes tabular:MiniBooNE mnist fashionmnist image:imagenette
# e.g. Imagenette only:  sbatch --array=14,15,30,31,46,47 hpc/rollout_v3.slurm
#      seeds 1 and 2:     sbatch --array=16-47 hpc/rollout_v3.slurm
# The backbone checkpoint of the cell must exist (hpc/backbone_v3.slurm). Run the greedy cell of a
# (dataset, seed) before committing it (commit_v3.py needs the greedy cache). Existing caches are
# skipped (resume by resubmitting). Imagenette uses the same flags as the local seed-0 cells:
# --batch-size 16 for both policies (identical batching of the depth-T scoring passes) and
# --policy-amp for greedy (fp16 autocast of the policy's hypothetical-reveal passes only).
# Preamble as in hpc/pool_rollout.slurm (FAU NHR conventions; env from hpc/env.local.sh).
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
read ds pol ts < <(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" hpc/cells_v3.txt)
extra=()
if [ "$ds" = "image:imagenette" ]; then
  extra=(--batch-size 16)
  if [ "$pol" = "greedy_entropy" ]; then extra+=(--policy-amp); fi
fi
python scripts/drive_v3.py --phase rollouts --datasets "$ds" --policies "$pol" --seeds "$ts" \
    --device "${CAFA_DEVICE:-cuda}" --extra-args="${extra[*]:-}"
