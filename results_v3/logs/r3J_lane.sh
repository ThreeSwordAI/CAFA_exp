#!/bin/bash
# Round 3b (Task J) lane: runs "family:seed:dataset" jobs sequentially through the ledgered runners.
#   main   -> drive_v3.py --phase sweep (metrics_v3)                              tag r3J
#   am10   -> drive_v3.py --phase sweep, committed_v3_am10 -> metrics_v3_alpha_margin10   tag r3Jam10
#   am02   -> drive_v3.py --phase sweep, committed_v3_am02 -> metrics_v3_alpha_margin02   tag r3Jam02
#   repair -> run_repairs_v3.py (predictor_upgrade where a v2 cache exists, policy_change)  tag r3J
# usage: bash results_v3/logs/r3J_lane.sh <lane-name> fam:ts:dataset [...]
set -u
cd "/f/FAU/PhD/Side Quest/CAFA_exp" || exit 9
export DATA_ROOT="F:\\CAFA_data" RESULTS_ROOT="F:\\CAFA_results" PYTHONIOENCODING=utf-8
PY=.venv/Scripts/python.exe
lane=$1; shift
echo "[lane $lane] start $(date '+%Y-%m-%d %H:%M:%S')"
for job in "$@"; do
  fam=${job%%:*}; rest=${job#*:}; ts=${rest%%:*}; ds=${rest#*:}
  echo "[lane $lane] $(date '+%H:%M:%S') $fam ts$ts $ds"
  case $fam in
    main)   $PY scripts/drive_v3.py --phase sweep --seeds "$ts" --datasets "$ds" --tag r3J ;;
    am10)   $PY scripts/drive_v3.py --phase sweep --seeds "$ts" --datasets "$ds" --commit-prefix committed_v3_am10 --metrics-dir-name metrics_v3_alpha_margin10 --tag r3Jam10 ;;
    am02)   $PY scripts/drive_v3.py --phase sweep --seeds "$ts" --datasets "$ds" --commit-prefix committed_v3_am02 --metrics-dir-name metrics_v3_alpha_margin02 --tag r3Jam02 ;;
    repair) $PY scripts/run_repairs_v3.py --seeds "$ts" --datasets "$ds" --tag r3J ;;
    *) echo "unknown family $fam"; exit 8 ;;
  esac
  rc=$?
  if [ $rc -ne 0 ]; then echo "[lane $lane] STOP rc=$rc at $fam ts$ts $ds"; exit $rc; fi
done
echo "[lane $lane] end $(date '+%Y-%m-%d %H:%M:%S')"
