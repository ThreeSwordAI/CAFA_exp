All six fixes are in and the three requested test files pass. On the real metrics, the shared columns of E4, E6, E2, E3 and E4_seeds are unchanged, and F3 for the 16 single-seed cells is pixel-identical to the reviewer's render of the code before the fixes. I did not edit `scripts/alpha_margin_summary_v3.py` (none of the fixes needed it), and I did not touch F:/CAFA_results, configs or git.

**Fix 1: cost-gap label based on oracle / full acquisition** (`scripts/make_tables_v3.py`)
- **Module docstring, L33-39:** describes the new rule.
- **L64-88:** `INTRINSIC_OVER_T` is renamed `INTRINSIC_OVER_FULL` (0.9; nothing else referenced the old name), and `COST_GAP_NOTE` is updated.
- **`cost_gap_label`, L132-141:** now takes `oracle_over_full`.
- **`cost_gap_row`, L160-211:** adds `oracle_safe_over_full` = `oracle_stratum_safe.mean_test_cost / full_acquisition.mean_test_cost` (empty when either cost is missing or full acquisition is 0). The column sits right after `oracle_safe_cost_over_T`, which is kept, and the label is computed from it.
- **Test:** new fixture cell `dsK/inv` has T = 20, full acquisition 40 and oracle cost 20, so oracle / T = 1.0 but oracle / full = 0.5, and the label must be `near-oracle`. `intr` sits exactly at 0.9 of full acquisition.
- **Trial on the Task K metrics (scratchpad copy, not the real metrics):** no uniform label changed and all other columns are equal. Under inverse_info, tabular-adult random goes from `intrinsic` to `near-oracle` (oracle / T 5.82, oracle / full 0.856), which is the case the review reported. Outputs are in `fix_I/tk_uniform` and `fix_I/tk_inverse_info`.

**Fix 2: `label_note` and `n_splits_finite`** (`make_tables_v3.py`)
- **New `label_note()`, L148-157:** the note is empty unless some split has an infeasible oracle or an infinite `n_needed`; otherwise it reads e.g. "oracle infeasible in 3/5 splits; n_needed inf in 4/5 splits (r_cal(lambda*) >= alpha or no feasible draw)".
- A split counts as oracle-infeasible when none of its draws has a feasible oracle. In the Task K data feasibility is all-or-none per split.
- **Columns in `cost_gap_row`:** `label_note` comes after `label`, and `n_splits_finite` ("x/5") after `n_needed_range`.
- **md note:** says the label uses pooled costs only and the note column qualifies it.
- **Tests:**
  - `sl`: 1/5 infeasible, 2/5 inf, "3/5".
  - `near`: 1/5 infeasible, 3/5 inf, "2/5".
  - `inv`: n_needed inf in 1/5 only, "4/5".
  - `intr` and `dsZ`: empty note, "5/5".
  - Direct unit asserts on `label_note`.
  - md text checks.

**Fix 3: F3 with several seeds** (`scripts/make_figures_v3.py`)
- **Docstring, L5-13:** describes the multi-seed mode.
- **New `_f3_values`, L75-85, and `f3_rows(cells)`, L88-128:** with one seed per (dataset, policy), one row per cell exactly as before. With several, one row per (dataset, policy): tier shares, costs / T and E2 are means over seeds, `dep_lo` / `dep_hi` are the min and max, and the tick label ends in "(n seeds)".
- **`fig_cascade`, L131-180:** plots from those rows and adds a min-max error bar (L156) only in multi-seed mode. In multi-seed mode the left y-label and the x-label get a second line saying "mean over seeds"; without that, the 48-cell render clipped the y-label.
- **Test `test_f3_seed_means`:** a synthetic 2 datasets × 2 policies × 3 seeds set (12 cells) gives 4 rows, 4 cost bars and 16 tier patches, with checked means, min-max and E2 text "1.30", one error-bar container, and "(3 seeds)" tick labels. The mixed fixture (dsA with 2 seeds) gives 6 rows.
- **Visual check:** a 48-cell render (16 real cells replicated as seeds 0-2 with scaled costs) shows 16 bars and 0 overlaps of E2 numbers or tick labels.

**Fix 4: fixtures where full-acquisition cost ≠ T** (`tests/test_reporting_v3.py`)
- **Fixtures:** dsA has full cost 30 with T = 20; `inv` has full 40. E9 dsA has am05 full 30 and am02 full 40.
- **Asserts:**
  - E4 `deployed_cost_over_T` / `marginal_cost_over_T` / `mondrian_cost_over_T` divide by T: 0.75 / 0.25 / 0.4 for dsA, 1.2 / 0.3 / 0.5 for `inv`.
  - F3 helper values divide by T; the gray full-acquisition marks are drawn at full / T (1.5, 2.0); there are no error bars in single-seed mode.
  - E9 `am05_deployed_cost_over_T` = 0.75 and `am02_deployed_cost_over_T` = 1.0.
  - `oracle_safe_over_full` = 0.5.
- **Mutation check (scratch copy):** each of these 10 single-line mutations makes the tests fail:
  - label computed on cost / T;
  - `oracle_safe_over_full` divided by T;
  - each of the three E4 cost columns divided by full acquisition;
  - the infeasible-split count dropped from the note;
  - F3 divided by full acquisition;
  - F3 always drawn per cell;
  - E9 divided by full acquisition;
  - E9 `<=` changed to `<`.

**Fix 5: E9 refusal boundary** (`tests/test_reporting_v3.py`)
- dsC's primary commit has floor 0.0299 and design margin 0.05; `alpha_from_floor(0.0299, 0.02, 0.01)` = 0.05.
- Asserts statuses (`refused`, `ok`, `TBD-RUN (not committed)`), `am02_alpha` = 0.05, and the md line "| dsC | greedy_entropy | refused: alpha = 0.05 <= design margin 0.05 (commit_v3 rc 7) |".

**Fix 6: docstring** (`make_tables_v3.py` L24-28)
- It now states that `tier2_would_certify` equals the tier-2 share by construction (tier 2 is deployed exactly when tier 1 does not certify and tier 2 does), so the column measures how often tier 2 mattered.

**Pytest**
- `tests/test_reporting_v3.py`: `6 passed in 3.24s`
- `tests/test_reporting_v3.py tests/test_v3_scripts.py tests/test_hpc_v3.py`: `18 passed in 57.23s`

**Real-data checks** (everything under `C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/fix_I/`)

`make_tables_v3` on F:/CAFA_results/metrics_v3 (16 cells), written to `tables/` and compared with `results_v3/tables`:

| Table | Rows | Shared columns | CSV differences | md lines |
|---|---|---|---|---|
| E4_cascade | 16 | 22 | 0 | each is a prefix of the new one |
| E6_baselines | 160 | 9 | 0 | each is a prefix of the new one |
| E2_blindness | 16 | 9 | 0 | each is a prefix of the new one |
| E3_audit | 16 | 13 | 0 | each is a prefix of the new one |
| E4_cascade_seeds | 16 | 26 | 0 | each is a prefix of the new one |

No cost-gap file is written for these metrics, as before. The F3 render is in `figs/F3_cascade.png`, which I viewed with Read, and the 48-cell render is in `figs48/F3_cascade.png`.