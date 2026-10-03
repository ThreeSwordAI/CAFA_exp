#!/bin/bash
# Round 3a post-run: equivalence check of the K1 rerun, all tables / figures, E10/E11, E9 alpha-margin summary.
# Run from the repo root after all 64 sweeps exist:  bash results_v3/logs/r3_postrun.sh
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
# K1: every round-2 field of the 16 primary cells is reproduced by the rerun with the oracle code
pairs=()
for f in "$R"/metrics_v3_round2/*.json; do b=$(basename "$f"); pairs+=("$R/metrics_v3_round2/$b" "$R/metrics_v3/$b"); done
step r3_taskK_sweep_equivalence $PY scripts/check_sweep_equivalence_v3.py "${pairs[@]}"
# tables (seed 0); round-2 table dirs regenerated with the round-3 columns
step r3_make_tables_dep $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3 --output-dir results_v3/tables --lambda-ref-key dep --scheme uniform
step r3_make_tables_inverse_info $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3 --output-dir results_v3/tables_inverse_info --lambda-ref-key dep --scheme inverse_info
for k in 0.5 0.7 0.9; do
  step r3_make_tables_lr$k $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3 --output-dir results_v3/tables_e9_lambda_ref_$k --lambda-ref-key $k --scheme uniform
done
step r3_make_tables_am10 $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3_alpha_margin10 --output-dir results_v3/tables_e9_alpha_margin10 --lambda-ref-key dep --scheme uniform
step r3_make_tables_am02 $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3_alpha_margin02 --output-dir results_v3/tables_e9_alpha_margin02 --lambda-ref-key dep --scheme uniform
step r3_make_tables_dw $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3_dw --output-dir results_v3/tables_e9_delta_weights --lambda-ref-key dep --scheme uniform
step r3_make_tables_G8 $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3_G8 --output-dir results_v3/tables_e9_G8 --lambda-ref-key dep --scheme uniform
step r3_make_tables_calfrac025 $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3_calfrac025 --output-dir results_v3/tables_e11_calfrac025 --lambda-ref-key dep --scheme uniform
step r3_make_tables_calfrac100 $PY scripts/make_tables_v3.py --metrics-dir $R/metrics_v3_calfrac100 --output-dir results_v3/tables_e11_calfrac100 --lambda-ref-key dep --scheme uniform
# figures F2-F6 (F3 now cost / T with the E2 number under each bar)
step r3_make_figures $PY scripts/make_figures_v3.py --metrics-dir $R/metrics_v3 --planted results_v3/planted --repair-dir results_v3/repair --output-dir results_v3/figures
# E10 (Task G) + E11 (Task K2) + F7
step r3_margin_analysis $PY scripts/margin_analysis_v3.py --metrics-dir $R/metrics_v3 --calfrac-dir 0.25 $R/metrics_v3_calfrac025 --calfrac-dir 1.0 $R/metrics_v3_calfrac100 --output-dir results_v3/tables --figure results_v3/figures/F7_margin.pdf
# E9 alpha-margin summary (Task H)
step r3_alpha_margin_summary $PY scripts/alpha_margin_summary_v3.py --output-dir results_v3/tables
