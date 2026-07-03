#!/bin/bash
# DEPRECATED (kept for provenance). Superseded by the v2 pipeline (see README +
# CLAUDE_CODE_WORKORDER.md). Known issues in the legacy pipeline: per-seed
# full-pool reshuffle (MNIST leakage), cal-fit stratum edges, clairvoyant tabular
# greedy (pre-fix), lambda_ref-duplicated marginal counting. Do not use for paper numbers.
# ===========================================================================
# Step-5 report -- run AFTER scripts/step5_sweep_tinygpu.sh (all 40 tasks) has
# finished.  Produces:
#   * the cross-dataset go/no-go readout  -> $RESULTS_ROOT/logs/step5_readout.txt
#   * the H2 + per-lambda_ref S4 bucket figures -> $RESULTS_ROOT/figures/
#
# This is pure CPU (numpy + matplotlib), so the SIMPLEST way to run it is
# directly on a login node -- no GPU, no queue:
#
#     source /etc/profile && module load python/3.12-conda
#     source activate /home/vault/iwi5/iwi5359h/envs/cafa
#     cd /home/hpc/iwi5/iwi5359h/my_repos/CAFA_exp
#     export RESULTS_ROOT=/home/vault/iwi5/iwi5359h/CAFA_results DATA_ROOT=/home/woody/iwi5/iwi5359h/CAFA_data
#     export PYTHONPATH="$PWD/src:$PYTHONPATH" MPLBACKEND=Agg
#     python scripts/aggregate_results.py | tee "$RESULTS_ROOT/logs/step5_readout.txt"
#     python scripts/make_figures.py --skip-synthetic
#
# Or submit it as a short TinyGPU job:  sbatch scripts/step5_report.sh
# ===========================================================================
#SBATCH --job-name=cafa_s5_report
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:20:00
#SBATCH --output=/home/vault/iwi5/iwi5359h/CAFA_results/logs/s5_report_%j.log
#SBATCH --error=/home/vault/iwi5/iwi5359h/CAFA_results/logs/s5_report_%j.err

set -euo pipefail

source /etc/profile
module load python/3.12-conda
source activate /home/vault/iwi5/iwi5359h/envs/cafa

export CODE_ROOT=/home/hpc/iwi5/iwi5359h/my_repos/CAFA_exp
export DATA_ROOT=/home/woody/iwi5/iwi5359h/CAFA_data
export RESULTS_ROOT=/home/vault/iwi5/iwi5359h/CAFA_results
export PYTHONPATH="$CODE_ROOT/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export MPLBACKEND=Agg          # headless matplotlib (no display on compute nodes)
cd "$CODE_ROOT"

mkdir -p "$RESULTS_ROOT/logs"

echo "=== Step-5 cross-dataset readout (default report) ==="
python3 scripts/aggregate_results.py | tee "$RESULTS_ROOT/logs/step5_readout.txt"

echo "=== Figures (H2 + per-lambda_ref S4 buckets) ==="
python3 scripts/make_figures.py --skip-synthetic

echo "readout -> $RESULTS_ROOT/logs/step5_readout.txt"
echo "figures -> $RESULTS_ROOT/figures/"