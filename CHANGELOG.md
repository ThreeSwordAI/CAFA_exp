# Changelog

## 2026-10-03 — Hoeffding–Bentkus boundary rounding fix (`src/cafa/risk_control.py`)

- **Defect.** `_hb_pvalue_array` evaluated the Bentkus term at `np.ceil(n * r_hat)`. For a 0/1 loss,
  `r_hat = k / n` with an integer error count `k`, but `r_hat` arrives as a float, and `n * r_hat` can land a
  few ulps above `k` (e.g. 17 errors in 197 rows: `197 * (1 - mean(correct)) = 17.000000000000007`). `ceil`
  then returned `k + 1`, so the p-value was computed for one error more than observed. Whether this happened
  depended on how `r_hat` was summed (`mean(loss)` vs `1 - mean(correct)`).
- **Direction: conservative only.** The count was never too small, so p-values were only ever too large.
  Every certificate issued with the defect is still valid; the effect was lower power and decisions near the
  threshold that depended on summation order (example: p = 0.0270 instead of 0.0149 for (n, k, α) =
  (197, 17, 0.15)).
- **Fix.** `k = np.ceil(np.round(n * rb, 9)).astype(int)` — the Bentkus term is evaluated at the integer
  error count. For a genuinely fractional `n * r_hat` the ceiling is unchanged. No other line of the file
  changed. `src/cafa/risk_control_ext.py` contains no other `ceil(n * …)`.
- **Tests.** `tests/test_frozen_hb_boundary.py` is now a plain regression test (was `xfail(strict=True)`):
  the (197, 17, 0.15) case gives 0.0149, and every (n, k) pair of the `scripts/scan_hb_ceil_boundary.py`
  grid (8,472 pairs, both summation orders) matches the exact-count p-value to 1e-12.
  `tests/test_risk_control.py` is unchanged and passes.
- **Tag.** The code as used for the AAAI-27 submission (defect present) is tagged `aaai27-submission`
  (commit `550f8e2`, the base of branch `aistats-v3`).
- **Superseded results.** Every round-1 Phase-3 number of the v3 campaign (commits, sweeps, tables, figures,
  E7 repairs, E9 ablations; `handoff.md` before round 2) was computed with the defect present. They are
  superseded by the round-2 results. The round-1 files are kept: `$RESULTS_ROOT/metrics_v3_round1/`,
  `results_v3/round1/`.
