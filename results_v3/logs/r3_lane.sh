#!/bin/bash
# Round-3 sweep lane: runs a list of "family:dataset" jobs sequentially through drive_v3.py (ledgered).
# usage: bash r3_lane.sh <lane-name> fam:ds [fam:ds ...]   fam in main|am10|cf025|cf100
set -u
cd "/f/FAU/PhD/Side Quest/CAFA_exp" || exit 9
export DATA_ROOT="F:\\CAFA_data" RESULTS_ROOT="F:\\CAFA_results" PYTHONIOENCODING=utf-8
PY=.venv/Scripts/python.exe
lane=$1; shift
echo "[lane $lane] start $(date '+%Y-%m-%d %H:%M:%S')"
for job in "$@"; do
  fam=${job%%:*}; ds=${job#*:}
  case $fam in
    main)  args=(--tag r3) ;;
    am10)  args=(--commit-prefix committed_v3_am10 --metrics-dir-name metrics_v3_alpha_margin10 --tag r3am10) ;;
    cf025) args=(--metrics-dir-name metrics_v3_calfrac025 --tag r3cf025 "--extra-args=--cal-frac 0.25") ;;
    cf100) args=(--metrics-dir-name metrics_v3_calfrac100 --tag r3cf100 "--extra-args=--cal-frac 1.0") ;;
    *) echo "unknown family $fam"; exit 8 ;;
  esac
  echo "[lane $lane] $(date '+%H:%M:%S') $fam $ds"
  $PY scripts/drive_v3.py --phase sweep --seeds 0 --datasets "$ds" "${args[@]}"
  rc=$?
  if [ $rc -ne 0 ]; then echo "[lane $lane] STOP rc=$rc at $fam $ds"; exit $rc; fi
done
echo "[lane $lane] end $(date '+%Y-%m-%d %H:%M:%S')"
