# TABLE_E10_margin_summary -- obs_tier1 vs the margin predictions (E10)

Inputs: metrics `F:/CAFA_results/metrics_v3/*.json` (48 files, scheme `uniform`, cal_frac 0.5); commits `configs/committed_v3_{dsname}_ts{ts}.json`; cal_frac 0.25: `F:/CAFA_results/metrics_v3_calfrac025`; cal_frac 1.0: `F:/CAFA_results/metrics_v3_calfrac100`.

n_points (main) = 960; tol = 0.2.  spearman_rho / spearman_p: scipy.stats.spearmanr of obs_tier1 vs the predictor (empty when either side is constant); frac_within_tol: share of points with |obs_tier1 - prediction| <= tol; mean_abs_err: mean |obs_tier1 - prediction|.  pred_tier1 uses the deepest stratum's full-information risk r_full, pred_tier1_thr its best threshold-rule risk rmin_thr (optimistic); pred_tier1_nk_calpool (sensitivity) uses n_k = round(cal_frac * n_k_calpool), the split's own expected draw count, instead of the commit's probe-based count.  pred_tier1 (the specified predictor) is the unconditional binomial prediction (the calibration draw as fresh rows of risk r_full, i.e. over resampling of the calibration pool); pred_tier1_hyper (sensitivity) is the prediction conditional on the split's calibration pool (draws without replacement): sum over n_d of Hypergeom(N_pool, N_k, n_cal).pmf(n_d) * Hypergeom(N_k, E_k, n_d).cdf(k_max(n_d)) with N_pool = meta n_calpool, N_k = n_k_calpool, E_k = round(r_full N_k), n_cal = round(cal_frac N_pool) (the indicator 1[E_k <= k_max(N_k)] at cal_frac 1.0).  Explanatory analysis, not a selection step.

| subset | predictor | n | spearman_rho | spearman_p | frac_within_tol | n_within_tol | mean_abs_err |
|---|---|---|---|---|---|---|---|
| main (all keys) | pred_tier1 | 960 | 0.914 | 0.00e+00 | 0.983 | 944 | 0.022 |
| main (all keys) | pred_tier1_thr | 960 | 0.914 | 0.00e+00 | 0.981 | 942 | 0.022 |
| main (all keys) | pred_tier1_nk_calpool | 960 | 0.914 | 0.00e+00 | 0.985 | 946 | 0.022 |
| main (all keys) | pred_tier1_hyper | 960 | 0.906 | 0.00e+00 | 0.990 | 950 | 0.015 |
| main, key dep | pred_tier1 | 240 | 0.950 | 1.23e-122 | 0.983 | 236 | 0.031 |
| main, key dep | pred_tier1_thr | 240 | 0.951 | 4.78e-123 | 0.983 | 236 | 0.031 |
| main, key dep | pred_tier1_nk_calpool | 240 | 0.951 | 7.36e-123 | 0.992 | 238 | 0.032 |
| main, key dep | pred_tier1_hyper | 240 | 0.950 | 3.62e-122 | 0.988 | 237 | 0.021 |
| main, key 0.5 | pred_tier1 | 240 | 0.403 | 8.38e-11 | 1.000 | 240 | 0.006 |
| main, key 0.5 | pred_tier1_thr | 240 | 0.404 | 8.12e-11 | 1.000 | 240 | 0.006 |
| main, key 0.7 | pred_tier1 | 240 | 0.808 | 1.63e-56 | 0.967 | 232 | 0.029 |
| main, key 0.7 | pred_tier1_thr | 240 | 0.808 | 1.60e-56 | 0.967 | 232 | 0.028 |
| main, key 0.9 | pred_tier1 | 240 | 0.832 | 5.79e-63 | 0.983 | 236 | 0.021 |
| main, key 0.9 | pred_tier1_thr | 240 | 0.833 | 5.19e-63 | 0.975 | 234 | 0.022 |
| main, csv-diabetes | pred_tier1 | 120 | 0.926 | 1.07e-51 | 1.000 | 120 | 0.000 |
| main, csv-diabetes | pred_tier1_thr | 120 | 0.926 | 1.07e-51 | 1.000 | 120 | 0.000 |
| main, csv-physionet | pred_tier1 | 120 | 0.676 | 2.59e-17 | 1.000 | 120 | 0.015 |
| main, csv-physionet | pred_tier1_thr | 120 | 0.674 | 3.28e-17 | 0.983 | 118 | 0.017 |
| main, cube | pred_tier1 | 120 | 0.868 | 1.00e-37 | 0.983 | 118 | 0.026 |
| main, cube | pred_tier1_thr | 120 | 0.869 | 7.99e-38 | 0.983 | 118 | 0.025 |
| main, fashionmnist | pred_tier1 | 120 | 0.948 | 1.44e-60 | 0.992 | 119 | 0.029 |
| main, fashionmnist | pred_tier1_thr | 120 | 0.948 | 1.16e-60 | 0.992 | 119 | 0.029 |
| main, image-imagenette | pred_tier1 | 120 | 0.961 | 1.89e-67 | 0.900 | 108 | 0.085 |
| main, image-imagenette | pred_tier1_thr | 120 | 0.960 | 7.43e-67 | 0.900 | 108 | 0.085 |
| main, mnist | pred_tier1 | 120 |  |  | 1.000 | 120 | 0.000 |
| main, mnist | pred_tier1_thr | 120 |  |  | 1.000 | 120 | 0.000 |
| main, tabular-MiniBooNE | pred_tier1 | 120 | 0.951 | 3.07e-62 | 0.992 | 119 | 0.011 |
| main, tabular-MiniBooNE | pred_tier1_thr | 120 | 0.951 | 3.87e-62 | 0.992 | 119 | 0.012 |
| main, tabular-adult | pred_tier1 | 120 | 0.894 | 7.40e-43 | 1.000 | 120 | 0.007 |
| main, tabular-adult | pred_tier1_thr | 120 | 0.894 | 7.42e-43 | 1.000 | 120 | 0.007 |
| cal_frac 0.25 | pred_tier1 | 320 | 0.944 | 9.01e-155 | 0.975 | 312 | 0.025 |
| cal_frac 0.25 | pred_tier1_thr | 320 | 0.944 | 1.16e-154 | 0.975 | 312 | 0.026 |
| cal_frac 1.0 | pred_tier1 | 320 | 0.838 | 1.12e-85 | 0.906 | 290 | 0.044 |
| cal_frac 1.0 | pred_tier1_thr | 320 | 0.838 | 1.21e-85 | 0.906 | 290 | 0.045 |
| main + cal_frac | pred_tier1 | 1600 | 0.906 | 0.00e+00 | 0.966 | 1546 | 0.027 |
| main + cal_frac | pred_tier1_thr | 1600 | 0.906 | 0.00e+00 | 0.965 | 1544 | 0.027 |
