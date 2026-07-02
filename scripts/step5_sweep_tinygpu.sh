#!/bin/bash
# ===========================================================================
# Step-5 lambda_ref robustness sweep -- TinyGPU (tinyx) array job.
#
# WHAT IT RUNS
#   The two NEW datasets (MiniBooNE, spambase) over the full grid:
#     policy   in {greedy_entropy, random}
#     cost     in {inverse_info, uniform}
#     lambda_ref in {0.5, 0.7, 0.9}
#   at the fixed-rule alpha (0.15 for both, from scripts/alpha_probe.py).
#
# WHY AN ARRAY OF 40 (and this exact granularity)
#   run_mondrian caches the backbone per (name, seed) and the rolled-out
#   trajectories per (name, policy, cost, seed) on shared vault storage.
#   To avoid two tasks racing to WRITE the same cache files, each array task
#   owns a unique (dataset, seed): it writes only its own checkpoint/.npz and
#   loops policy x cost x lambda_ref internally.  2 datasets x 20 seeds = 40
#   tasks, fully parallel, no cache corruption.  (lambda_ref reuses the cached
#   rollout -- only the bucketing/analysis differs -- so the 3 lambda_ref runs
#   per (pol,cost) are cheap.)
#
# SUBMIT (from the repo root, /home/hpc/iwi5/iwi5359h/my_repos/CAFA_exp):
#     mkdir -p /home/vault/iwi5/iwi5359h/CAFA_results/logs   # once
#     sbatch scripts/step5_sweep_tinygpu.sh
#   The '#SBATCH --array' line below makes a single sbatch launch all 40 tasks.
#   Monitor:  squeue -u iwi5359h        tail -f <the .log below>
#   After it finishes, produce the readout+figures: scripts/step5_report.sh
# ===========================================================================
#SBATCH --job-name=cafa_s5_sweep
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=04:00:00
#SBATCH --array=0-39%8
#SBATCH --output=/home/vault/iwi5/iwi5359h/CAFA_results/logs/s5_sweep_%A_%a.log
#SBATCH --error=/home/vault/iwi5/iwi5359h/CAFA_results/logs/s5_sweep_%A_%a.err
# NOTE (TinyGPU): do NOT add --mem (memory is auto-allocated per GPU) and do
# NOT add --partition (TinyGPU needs neither).

set -euo pipefail

# --- environment (exactly the FAU 'own conda env' recipe) ------------------
source /etc/profile
module load python/3.12-conda
source activate /home/vault/iwi5/iwi5359h/envs/cafa

export CODE_ROOT=/home/hpc/iwi5/iwi5359h/my_repos/CAFA_exp
export DATA_ROOT=/home/woody/iwi5/iwi5359h/CAFA_data
export RESULTS_ROOT=/home/vault/iwi5/iwi5359h/CAFA_results
export PYTHONPATH="$CODE_ROOT/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
cd "$CODE_ROOT"

# --- fixed-rule alpha per dataset (from scripts/alpha_probe.py) ------------
declare -A ALPHA=( [tabular:MiniBooNE]=0.15 [tabular:spambase]=0.15 )
DATASETS=( tabular:MiniBooNE tabular:spambase )
POLICIES=( greedy_entropy random )
COSTS=( inverse_info uniform )
LRS=( 0.5 0.7 0.9 )
N_SEEDS=20   # protocol.seeds = 0..19 ; --seed-index k selects seed k

# --- decode this task's (dataset, seed) from the array index ---------------
TASK=${SLURM_ARRAY_TASK_ID:?submit as an array job: sbatch scripts/step5_sweep_tinygpu.sh}
DS_IDX=$(( TASK / N_SEEDS ))
SEED_IDX=$(( TASK % N_SEEDS ))
DS=${DATASETS[$DS_IDX]}
A=${ALPHA[$DS]}

echo "=============================================================="
echo "host=$(hostname)  job=${SLURM_ARRAY_JOB_ID}  task=${TASK}"
echo "dataset=${DS}  seed-index=${SEED_IDX}  alpha=${A}"
python3 -c "import torch;print('cuda:',torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
echo "=============================================================="

# --- the 12 cells for THIS (dataset, seed): pol x cost x lambda_ref --------
rc=0
for POL in "${POLICIES[@]}"; do
  for CS in "${COSTS[@]}"; do
    for LR in "${LRS[@]}"; do
      echo ">>> ${DS} | pol=${POL} cost=${CS} lambda_ref=${LR} seed-index=${SEED_IDX}"
      # Do NOT let one failed cell kill the other 11 for this seed.
      if ! python3 scripts/run_mondrian.py \
            --dataset "$DS" --policy "$POL" --cost-scheme "$CS" \
            --lambda-ref "$LR" --alpha "$A" \
            --seed-index "$SEED_IDX" --device cuda ; then
        echo "[WARN] cell FAILED: ${DS} ${POL} ${CS} lr=${LR} seed-idx=${SEED_IDX}" >&2
        rc=1
      fi
    done
  done
done

echo "task ${TASK} done (rc=${rc}). metrics -> ${RESULTS_ROOT}/metrics"
exit $rc