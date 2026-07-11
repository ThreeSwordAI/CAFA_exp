# Template for hpc/env.local.sh (the real file is gitignored -- it holds YOUR paths).
# Batch jobs on the cluster start with a clean shell and do NOT inherit the exports
# from your login session; the v2 slurm scripts source hpc/env.local.sh so every
# array task gets these. One-time setup:
#
#   cp hpc/env.local.template.sh hpc/env.local.sh
#   $EDITOR hpc/env.local.sh          # fill in the real paths
#
export CAFA_ENV=/home/vault/iwi5/<user>/envs/cafa           # conda env on vault
export DATA_ROOT=/home/woody/iwi5/<user>/CAFA_data          # data on woody
export RESULTS_ROOT=/home/vault/iwi5/<user>/CAFA_results    # results on vault
# Optional: export CAFA_DEVICE=cuda   # device for pool_rollout.slurm (default cuda)
