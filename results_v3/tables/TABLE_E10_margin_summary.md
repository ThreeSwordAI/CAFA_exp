# TABLE_E10_margin_summary -- obs_tier1 vs the margin predictions (E10)

Inputs: metrics `F:/CAFA_results/metrics_v3/*.json` (16 files, scheme `uniform`, cal_frac 0.5); commits `configs/committed_v3_{dsname}_ts{ts}.json`; cal_frac 0.25: `F:/CAFA_results/metrics_v3_calfrac025`; cal_frac 1.0: `F:/CAFA_results/metrics_v3_calfrac100`.

n_points (main) = 320; tol = 0.2.  spearman_rho / spearman_p: scipy.stats.spearmanr of obs_tier1 vs the predictor (empty when either side is constant); frac_within_tol: share of points with |obs_tier1 - prediction| <= tol; mean_abs_err: mean |obs_tier1 - prediction|.  pred_tier1 uses the deepest stratum's full-information risk r_full, pred_tier1_thr its best threshold-rule risk rmin_thr (optimistic); pred_tier1_nk_calpool (sensitivity) uses n_k = round(cal_frac * n_k_calpool), the split's own expected draw count, instead of the commit's probe-based count.  pred_tier1 (the specified predictor) is the unconditional binomial prediction (the calibration draw as fresh rows of risk r_full, i.e. over resampling of the calibration pool); pred_tier1_hyper (sensitivity) is the prediction conditional on the split's calibration pool (draws without replacement): sum over n_d of Hypergeom(N_pool, N_k, n_cal).pmf(n_d) * Hypergeom(N_k, E_k, n_d).cdf(k_max(n_d)) with N_pool = meta n_calpool, N_k = n_k_calpool, E_k = round(r_full N_k), n_cal = round(cal_frac N_pool) (the indicator 1[E_k <= k_max(N_k)] at cal_frac 1.0).  Explanatory analysis, not a selection step.

| subset | predictor | n | spearman_rho | spearman_p | frac_within_tol | n_within_tol | mean_abs_err |
|---|---|---|---|---|---|---|---|
| main (all keys) | pred_tier1 | 320 | 0.905 | 3.28e-120 | 0.994 | 318 | 0.020 |
| main (all keys) | pred_tier1_thr | 320 | 0.905 | 2.56e-120 | 0.988 | 316 | 0.021 |
| main (all keys) | pred_tier1_nk_calpool | 320 | 0.905 | 2.36e-120 | 0.984 | 315 | 0.021 |
| main (all keys) | pred_tier1_hyper | 320 | 0.894 | 3.55e-113 | 0.997 | 319 | 0.010 |
| main, key dep | pred_tier1 | 80 | 0.935 | 7.17e-37 | 1.000 | 80 | 0.027 |
| main, key dep | pred_tier1_thr | 80 | 0.936 | 3.69e-37 | 1.000 | 80 | 0.028 |
| main, key dep | pred_tier1_nk_calpool | 80 | 0.935 | 7.44e-37 | 1.000 | 80 | 0.027 |
| main, key dep | pred_tier1_hyper | 80 | 0.934 | 1.61e-36 | 1.000 | 80 | 0.014 |
| main, key 0.5 | pred_tier1 | 80 | 0.449 | 3.01e-05 | 1.000 | 80 | 0.010 |
| main, key 0.5 | pred_tier1_thr | 80 | 0.449 | 3.01e-05 | 1.000 | 80 | 0.010 |
| main, key 0.7 | pred_tier1 | 80 | 0.777 | 2.27e-17 | 0.975 | 78 | 0.027 |
| main, key 0.7 | pred_tier1_thr | 80 | 0.777 | 2.28e-17 | 0.975 | 78 | 0.027 |
| main, key 0.9 | pred_tier1 | 80 | 0.706 | 2.62e-13 | 1.000 | 80 | 0.016 |
| main, key 0.9 | pred_tier1_thr | 80 | 0.710 | 1.64e-13 | 0.975 | 78 | 0.019 |
| main, csv-diabetes | pred_tier1 | 40 | 0.926 | 1.16e-17 | 1.000 | 40 | 0.000 |
| main, csv-diabetes | pred_tier1_thr | 40 | 0.926 | 1.16e-17 | 1.000 | 40 | 0.000 |
| main, csv-physionet | pred_tier1 | 40 | 0.762 | 1.09e-08 | 1.000 | 40 | 0.012 |
| main, csv-physionet | pred_tier1_thr | 40 | 0.760 | 1.25e-08 | 0.950 | 38 | 0.018 |
| main, cube | pred_tier1 | 40 | 0.802 | 5.14e-10 | 1.000 | 40 | 0.008 |
| main, cube | pred_tier1_thr | 40 | 0.802 | 5.14e-10 | 1.000 | 40 | 0.007 |
| main, fashionmnist | pred_tier1 | 40 | 0.953 | 2.94e-21 | 0.975 | 39 | 0.037 |
| main, fashionmnist | pred_tier1_thr | 40 | 0.953 | 2.94e-21 | 0.975 | 39 | 0.038 |
| main, image-imagenette | pred_tier1 | 40 | 0.963 | 2.94e-23 | 0.975 | 39 | 0.081 |
| main, image-imagenette | pred_tier1_thr | 40 | 0.963 | 2.94e-23 | 0.975 | 39 | 0.081 |
| main, mnist | pred_tier1 | 40 |  |  | 1.000 | 40 | 0.000 |
| main, mnist | pred_tier1_thr | 40 |  |  | 1.000 | 40 | 0.000 |
| main, tabular-MiniBooNE | pred_tier1 | 40 | 0.975 | 1.70e-26 | 1.000 | 40 | 0.014 |
| main, tabular-MiniBooNE | pred_tier1_thr | 40 | 0.975 | 1.70e-26 | 1.000 | 40 | 0.016 |
| main, tabular-adult | pred_tier1 | 40 | 0.897 | 5.16e-15 | 1.000 | 40 | 0.007 |
| main, tabular-adult | pred_tier1_thr | 40 | 0.897 | 5.16e-15 | 1.000 | 40 | 0.006 |
| cal_frac 0.25 | pred_tier1 | 320 | 0.944 | 9.01e-155 | 0.975 | 312 | 0.025 |
| cal_frac 0.25 | pred_tier1_thr | 320 | 0.944 | 1.16e-154 | 0.975 | 312 | 0.026 |
| cal_frac 1.0 | pred_tier1 | 320 | 0.838 | 1.12e-85 | 0.906 | 290 | 0.044 |
| cal_frac 1.0 | pred_tier1_thr | 320 | 0.838 | 1.21e-85 | 0.906 | 290 | 0.045 |
| main + cal_frac | pred_tier1 | 960 | 0.897 | 0.00e+00 | 0.958 | 920 | 0.030 |
| main + cal_frac | pred_tier1_thr | 960 | 0.897 | 0.00e+00 | 0.956 | 918 | 0.031 |
