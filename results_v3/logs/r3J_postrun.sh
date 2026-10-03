#!/bin/bash
# Round 3b (Task J) post-run: all tables over seeds 0-2 (TABLE_E4_cascade_seeds = mean +- sd; TABLE_E4_seed_flags),
# E10 over all seeds (+ the seed-0 cal_frac points), F7, figures, the per-seed E9 alpha-margin summaries.
# Run from the repo root after every seed-1/2 sweep exists:  bash results_v3/logs/r3J_postrun.sh
set -u
cd "/f/FAU/PhD/Side Quest/CAFA_exp" || exit 9
export DATA_ROOT="F:\\CAFA_data" RESULTS_ROOT="F:\\CAFA_results" PYTHONIOENCODING=utf-8
PY=.venv/Scripts/python.exe
R=F:/CAFA_results
L=results_v3/logs
step() {  # log-name, command...
  local name=$1; shift
  { echo "# $*"; echo "# start $(date '+%Y-%m-%d %H:%M:%S')"; "$@"; echo "# returncode $?"; } > "$L/$name.log" 2>&1
  echo "$name: $(tail -1 "$L/$name.log")"
}
step r3J_make_tables_dep $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3 --output-dir results_v3/tables --lambda-ref-key dep --scheme uniform
step r3J_make_tables_inverse_info $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3 --output-dir results_v3/tables_inverse_info --lambda-ref-key dep --scheme inverse_info
for k in 0.5 0.7 0.9; do
  step r3J_make_tables_lr$k $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3 --output-dir results_v3/tables_e9_lambda_ref_$k --lambda-ref-key $k --scheme uniform
done
step r3J_make_tables_am10 $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3_alpha_margin10 --output-dir results_v3/tables_e9_alpha_margin10 --lambda-ref-key dep --scheme uniform
step r3J_make_tables_am02 $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3_alpha_margin02 --output-dir results_v3/tables_e9_alpha_margin02 --lambda-ref-key dep --scheme uniform
step r3J_make_figures $PY scripts/make_figures_v3.py --metrics-dir $R/metrics_v3 --planted results_v3/planted --repair-dir results_v3/repair --output-dir results_v3/figures
step r3J_margin_analysis $PY scripts/margin_analysis_v3.py --metrics-dir $R/metrics_v3 --calfrac-dir 0.25 $R/metrics_v3_calfrac025 --calfrac-dir 1.0 $R/metrics_v3_calfrac100 --output-dir results_v3/tables --figure results_v3/figures/F7_margin.pdf
for ts in 1 2; do
  step r3J_alpha_margin_summary_ts$ts $PY scripts/alpha_margin_summary_v3.py --train-seed $ts --output-dir results_v3/tables_e9_alpha_margin_ts$ts
done
