I applied all four fixes. Only `scripts/margin_analysis_v3.py` (755 lines) and `tests/test_margin_analysis_v3.py` (349 lines) were edited, nothing was written to F:/CAFA_results or configs, and there was no git activity. On the real data the existing outputs are unchanged: the TABLE_E10 and TABLE_E11 CSVs have 0 changed values in the old columns, and the summary JSON is identical apart from the new `pred_tier1_hyper` entries and the extended `what` text.

**Fix 1: `pred_tier1_hyper`, the prediction conditional on the split's calibration pool**
- `pred_certify_hyper` (lines 211-252) computes it as specified, keeping only the n_d values with pmf > 1e-12 (`HYPER_TAIL`, line 131).
- Inputs come from `read_cell` (lines 283-284 and 336):
  - N_pool is `meta["n_calpool"]`, or the commit's `split["n_calpool"]` if that is missing.
  - n_cal is round(cf × N_pool), with cf = 0.5 for the main directory and CF for each `--calfrac-dir`.
  - E_k is round(r_full × n_k_calpool).
- **Runtime:** the first straight version took 42.5 s; 30 s of that was `hypergeom.pmf` over the full support. I changed two things:
  - The pmf is now evaluated on a window around the mean that is widened until both ends are ≤ 1e-12 or at the support bounds. The pmf is unimodal, so this is exact.
  - k_max is memoised per (n, alpha, level) in a dict (`_KMAX`, lines 157-199). The previous n_d's k_max is passed as a hint that only narrows the binary search, so it cannot change the result.
- On the real data all six output files are byte-identical to the slow version's output.
- **Where it appears:**
  - CSV columns: `E10_COLS + SENSITIVITY`, so TABLE_E10 and TABLE_E10_margin_calfrac.
  - Summary JSON: every agreement block.
  - Summary md: the main and dep rows.
  - TABLE_E11: `pred_tier1_hyper_cf{CF}` columns in both the CSV and the md (it fits: 25 columns).
  - The printed headline lines.
- **Definitions in the md headers:** TABLE_E10_margin.md (lines 695-703), the summary md (lines 463-468) and TABLE_E11_calfrac.md (lines 727-730) each state that `pred_tier1` (the specified predictor) is the unconditional binomial over resampling of the pool, and `pred_tier1_hyper` the conditional one. The module docstring is updated too.
- **Tests:**
  - CSV wiring in `test_e10_rows`.
  - Summary statistics in `test_summary_json`.
  - E11 hyper columns at cf 0.25 and 0.5 in `test_e11_calfrac_scaling_and_tbd`.

**Fix 2: edges and G cross-check (lines 292-303)**
- The edges' shapes are now compared before `np.allclose`.
- `blk["G"]` and the commit's `G` must both equal `len(expected_cal_counts)`; otherwise it raises `ValueError` ("... stratum edges / G differ ...").
- **Tests** (`test_commit_edges_shape_or_g_mismatch_raises`):
  - Metrics edges `[]` against commit edges `[0.3]` with expected `[300, 780]` now raises.
  - Equal edges `[]` against a commit with G = 2 also raises.
- `test_g1_commit_match_runs` checks that a matching G = 1 commit still runs.

**Fix 3: independent tests**
- `test_prediction_mid_range_matches_enumeration` covers (500, 0.12, 0.15) = 0.4248, (1200, 0.13, 0.15) = 0.4529, (300, 0.15, 0.20) = 0.5397 and (2000, 0.18, 0.20) = 0.5602. Each is checked against the sum of `binom.pmf` over the k with HB p-value ≤ 0.05, without going through k_max.
- `test_hyper_prediction_matches_brute_force` uses exact `math.comb` enumeration on 4 cases, including (60, 30, 3, 30, 0.3) = 0.18521.
- `test_hyper_prediction_is_the_indicator_at_cal_frac_one` checks E_k = 0..7 at n_cal = N_pool, giving [1,1,1,1,0,0,0,0], equal to 1[HB ≤ 0.05].
- The brute-force boundary test now also checks the k_max hint.
- **Mutation check** (on scratch copies):

| Mutation | Tests failed (of 26) |
|---|---|
| `binom.cdf(km - 1)` | 4 |
| `binom.cdf(km + 1)` | 4 |
| hypergeom cdf at km − 1 | 5 |
| hypergeom cdf at km + 1 | 5 |
| old broadcasting edges check | 2 |

**Fix 4: missing scheme is n/a, not TBD-RUN**
- `read_cell` sets `by_key[key] = "n/a"` when the key's block lacks the requested scheme (line 308).
- `e11_rows` writes `"n/a (no scheme)"` there (line 486). TBD-RUN is now only for a missing file or directory.
- The E11 md header defines both markers (line 733).
- **Test:** `test_missing_scheme_is_na_not_tbd`.
- **Real data with `--scheme inverse_info`:** the mnist, fashionmnist and imagenette rows show `n/a (no scheme)` in the cf0.5 columns and TBD-RUN in cf0.25 and cf1.0.

**Pytest:** `26 passed in 7.95s` (`tests/test_margin_analysis_v3.py`)

**Real-data run** (`F:/CAFA_results/metrics_v3`, 320 points; outputs in `C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/fix_G/tables` and `fix_G/figures`):
```
[margin] main (all keys)        n= 320 | pred_tier1: Spearman rho = 0.905 (p = 3.28e-120), within tol = 0.994 (318/320) | pred_tier1_thr: Spearman rho = 0.905 (p = 2.56e-120), within tol = 0.988 (316/320) | pred_tier1_hyper: Spearman rho = 0.894 (p = 3.55e-113), within tol = 0.997 (319/320)
[margin] main, key dep          n=  80 | pred_tier1: Spearman rho = 0.935 (p = 7.17e-37), within tol = 1.000 (80/80) | pred_tier1_thr: Spearman rho = 0.936 (p = 3.69e-37), within tol = 1.000 (80/80) | pred_tier1_hyper: Spearman rho = 0.934 (p = 1.61e-36), within tol = 1.000 (80/80)
```
- Mean absolute error: `pred_tier1_hyper` 0.0102 on all keys and 0.0136 on dep, against `pred_tier1` 0.0197.
- **Runtime:** 7.1 s in-script and 8.8 s wall. Before the fix it was about 3 s; the unoptimised hyper version took 42.5 s.

**Extra check with Task G's K2 trial directories** (`--calfrac-dir 0.25 scratchpad/G/k2_cf025_trial --calfrac-dir 1.0 scratchpad/G/k2_cf100_trial`, outputs in `fix_G/k2trial/`):
- Runtime 7.8 s.
- At cal_frac 1.0 all 20 `pred_tier1_hyper` values equal 1[HB(E_k/N_k) ≤ 0.05] (asserted). For key 0.9 they are 0 where `pred_tier1` gives 0.118 / 0.094 / 0.059 against observed 0.
- cal_frac 1.0 summary: `pred_tier1_hyper` rho 1.000, 20/20 within 0.2; `pred_tier1` rho 0.757.

No fix was left unapplied.