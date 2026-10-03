#!/bin/bash
# Dry run of hpc/backbone_v3.slurm and hpc/rollout_v3.slurm for EVERY array index, without Slurm and without a GPU.
#
# The real batch scripts are executed with SLURM_ARRAY_TASK_ID / SLURM_SUBMIT_DIR set and CAFA_DRIVER_FLAGS=--dry-run,
# so drive_v3.py prints the exact command each array task would run (and whether its output already exists or a
# prerequisite is missing on this machine).  Cluster-only commands are stubbed when absent: `module`, and the conda
# `source activate` (a no-op file named `activate` on PATH); `python` is the interpreter in $PYTHON.  The ONLY line of
# the batch scripts that is not executed verbatim is `source /etc/profile` (the cluster's login profile; a
# workstation's own profile is not `set -u` clean): the scripts are copied with that one line commented out.
# The --epochs 60 tasks (CUBE 9/17, MiniBooNE 12/20) get CAFA_EXTRA="--epochs 60", exactly as in hpc/README_v3.md.
#
#   PYTHON=.venv/Scripts/python.exe DATA_ROOT=... RESULTS_ROOT=... bash hpc/dry_run_v3.sh > results_v3/logs/hpc_dry_run.log
# BB_INDICES / RO_INDICES (space-separated) restrict the backbone / rollout indices (default: all 0-23 / 0-47).
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
: "${DATA_ROOT:?set DATA_ROOT}" "${RESULTS_ROOT:?set RESULTS_ROOT}"
PY="${PYTHON:-python}"
case "$PY" in /*|[A-Za-z]:*) ;; *) PY="$REPO/$PY" ;; esac
STUB="$(mktemp -d)"
trap 'rm -rf "$STUB"' EXIT
printf '#!/bin/bash\nexec "%s" "$@"\n' "$PY" > "$STUB/python"
printf ': # dry-run stub for conda activate\n' > "$STUB/activate"
command -v module >/dev/null 2>&1 || printf '#!/bin/bash\nexit 0\n' > "$STUB/module"
chmod +x "$STUB"/*
for f in backbone_v3 rollout_v3; do
  sed 's|^source /etc/profile$|: # dry run: source /etc/profile (cluster login profile) not executed|' "$REPO/hpc/$f.slurm" > "$STUB/$f.slurm"
  [ "$(diff "$REPO/hpc/$f.slurm" "$STUB/$f.slurm" | grep -c '^>')" = 1 ] || { echo "unexpected diff in $f.slurm"; exit 1; }
done
export PATH="$STUB:$PATH" CAFA_ENV=dry-run CAFA_DRIVER_FLAGS=--dry-run SLURM_SUBMIT_DIR="$REPO" CAFA_REPO="$REPO"
echo "# hpc dry run: $(date -Iseconds) repo $REPO commit $(git -C "$REPO" rev-parse --short HEAD) python $PY"
fails=0
for i in ${BB_INDICES:-$(seq 0 23)}; do
  case $i in 9|12|17|20) ex="--epochs 60" ;; *) ex="" ;; esac
  echo "### backbone_v3.slurm SLURM_ARRAY_TASK_ID=$i CAFA_EXTRA='$ex'"
  CAFA_EXTRA="$ex" SLURM_ARRAY_TASK_ID=$i bash "$STUB/backbone_v3.slurm" 2>&1 | grep -E "\[drive_v3\]|Error|error" || fails=$((fails+1))
done
for i in ${RO_INDICES:-$(seq 0 47)}; do
  echo "### rollout_v3.slurm SLURM_ARRAY_TASK_ID=$i ($(sed -n "$((i+1))p" "$REPO/hpc/cells_v3.txt"))"
  SLURM_ARRAY_TASK_ID=$i bash "$STUB/rollout_v3.slurm" 2>&1 | grep -E "\[drive_v3\]|Error|error" || fails=$((fails+1))
done
echo "# array tasks without driver output: $fails"
