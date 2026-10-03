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
# Round 3 (Task L lines of hpc/README_v3.md section 8): DRY_DRIVER_FLAGS is appended to --dry-run in CAFA_DRIVER_FLAGS
# (e.g. "--checkpoint-tag repair"), and BB_EXTRA, when set, replaces the per-index CAFA_EXTRA of the backbone tasks:
#   BB_INDICES=6 RO_INDICES="12 13" BB_EXTRA="--epochs 60 --width-mult 4 --p-full 0.3" \
#     DRY_DRIVER_FLAGS="--checkpoint-tag repair" PYTHON=... DATA_ROOT=... RESULTS_ROOT=... bash hpc/dry_run_v3.sh
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
: "${DATA_ROOT:?set DATA_ROOT}" "${RESULTS_ROOT:?set RESULTS_ROOT}"
PY="${PYTHON:-python}"
case "$PY" in
  /*|[A-Za-z]:*) ;;                                   # absolute path
  */*) PY="$REPO/$PY" ;;                              # path relative to the repo (e.g. .venv/Scripts/python.exe)
  *) PY="$(command -v "$PY")" || { echo "python interpreter '${PYTHON:-python}' not found on PATH"; exit 1; } ;;
esac
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
export PATH="$STUB:$PATH" CAFA_ENV=dry-run CAFA_DRIVER_FLAGS="--dry-run${DRY_DRIVER_FLAGS:+ $DRY_DRIVER_FLAGS}" \
  SLURM_SUBMIT_DIR="$REPO" CAFA_REPO="$REPO"
dirty=$(git -C "$REPO" status --porcelain -- hpc scripts src configs | wc -l)
echo "# hpc dry run: $(date -Iseconds) repo $REPO commit $(git -C "$REPO" rev-parse --short HEAD) (uncommitted changes under hpc/ scripts/ src/ configs/: $dirty files) python $PY"
if [ -n "${DRY_DRIVER_FLAGS:-}${BB_EXTRA+x}" ]; then echo "# CAFA_DRIVER_FLAGS='$CAFA_DRIVER_FLAGS' BB_EXTRA='${BB_EXTRA-}'"; fi
fails=0
for i in ${BB_INDICES:-$(seq 0 23)}; do
  if [ -n "${BB_EXTRA+x}" ]; then ex="$BB_EXTRA"; else case $i in 9|12|17|20) ex="--epochs 60" ;; *) ex="" ;; esac; fi
  echo "### backbone_v3.slurm SLURM_ARRAY_TASK_ID=$i CAFA_EXTRA='$ex'"
  CAFA_EXTRA="$ex" SLURM_ARRAY_TASK_ID=$i bash "$STUB/backbone_v3.slurm" 2>&1 | grep -E "\[drive_v3\]|Error|error" || fails=$((fails+1))
done
for i in ${RO_INDICES:-$(seq 0 47)}; do
  echo "### rollout_v3.slurm SLURM_ARRAY_TASK_ID=$i ($(sed -n "$((i+1))p" "$REPO/hpc/cells_v3.txt"))"
  SLURM_ARRAY_TASK_ID=$i bash "$STUB/rollout_v3.slurm" 2>&1 | grep -E "\[drive_v3\]|Error|error" || fails=$((fails+1))
done
echo "# array tasks without driver output: $fails"
