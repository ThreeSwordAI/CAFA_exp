I applied all three fixes. Only `scripts/run_cascade_sweep.py` and `tests/test_oracles_v3.py` were edited. Nothing was written to F:/CAFA_results or configs/, no frozen file was touched, and I ran no git commands.

**Fix 1 (finding 1): tests now catch the top grid column used in place of full acquisition**
- `tests/test_oracles_v3.py:95-105`, `_toy_test_split`: at depth T, `cum_cost` is now 3.0 on every row while the top grid column's `costs` stays 2.0. Row 1 is now wrong at depth T (`correct[1, 2] = 0`) and right at the top grid column. Docstring updated.
- `tests/test_oracles_v3.py:120-125`: the abstention case of `per_stratum_rule_risks` now asserts cost 1.5 (not 1.0), `ps_[0] == 1/3`, `cn[0] == (1, 3)` and `agg == 1/6`.
- `tests/test_oracles_v3.py:132-143,154`: `_saturate()` sets every 100th row of the greedy_entropy cache to score 1.0 from depth 0. It runs in the `cells` fixture before `commit_v3.commit`, for both scenarios (typeII and feasible).
- `tests/test_oracles_v3.py:273-276`, infeasible branch: it still asserts `test_cost == cc[:, T].mean()`. It now also asserts that the top grid column is strictly cheaper than `cc[:, T]`, and that `test_cost != costs[:, -1].mean()`. typeII still has infeasible draws.
- Module docstring (lines 3-27) updated.
- Mutation check: I reused the reviewer's `review_K/mut/mutplug.py` through `scratchpad/fix_K/run_mutations.py`. A control run with no change gives `14 passed in 14.54s`.

| Mutation | Result | Failing test |
|---|---|---|
| B (abstaining strata use the top grid column) | caught, `1 failed, 13 passed in 18.92s` | `test_cost_order_mondrian_safe_le_common_safe_le_full` |
| B, cost only | caught | same test |
| B, risk only | caught | same test |
| E (infeasible common oracle uses the top grid column) | caught, `1 failed, 13 passed in 14.24s` | `test_sweep_oracle_lambdas_recomputed_from_cache[typeII]` |

**Fix 2 (finding 3): empty calibration draws are refused**
- `scripts/run_cascade_sweep.py:406-411`: after the splits are built, the sweep checks every swept split. If `int(round(cal_frac * calpool.size)) < 1`, it raises a ValueError like this: `cal_frac 0.0001 gives an empty calibration draw: round(cal_frac x N) = 0 for the calibration pool of split S (N rows); use a larger --cal-frac.`
- Documented in the K2 section of the module docstring (lines 83-85).
- Test, `tests/test_oracles_v3.py:381-390` in `test_cal_frac_guards`: it checks that 1e-4 rounds to 0 on every calibration pool, then expects the ValueError. The match covers `cal_frac 0.0001`, the split and the row count, and the named size must be a real pool size. It also checks that nothing was written.
- Mutation G (guard removed) is caught in `test_cal_frac_guards`.

**Fix 3 (finding 2): new summary field `cascade_cost_over_oracle_feasible`**
- `scripts/run_cascade_sweep.py:313-317`, in `summarize()`: mean cascade test cost over the draws whose `oracle_stratum_safe.feasible is True`, divided by the mean `oracle_stratum_safe` test cost over the same draws. It is None when there is no feasible draw or the denominator is 0.
- `summarize()` is called for both the pooled summary and each split, so the field appears pooled and in `by_split`.
- Documented next to `cascade_cost_over_oracle` in the module docstring (lines 68-74). The `summarize` docstring is updated (lines 259-260).
- Test, `tests/test_oracles_v3.py:199,220-234` in `test_sweep_records_and_summary_fields`, for the pooled summary and every split:
  - The value is recomputed from the draws.
  - When every draw is feasible, it must equal `cascade_cost_over_oracle`.
  - When no draw is feasible, it must be None.
  - Both branches must actually occur: a value in both scenarios, and at least one None in typeII.
- Mutation F (ratio taken over all draws) is caught in `test_sweep_records_and_summary_fields[typeII]`.
- On real PhysioNet, lr 0.9 / uniform: the pooled value is 5.3985, against 1.4709 for `cascade_cost_over_oracle`. The feasible rate is 0.4, so splits 778, 779 and 780 give None and splits 781 and 782 equal the existing ratio.

**Test and equivalence results**
- `pytest -q tests/test_oracles_v3.py` → `14 passed in 14.93s`
- `pytest -q tests/test_oracles_v3.py tests/test_v3_scripts.py tests/test_multisplit_v3.py` → `31 passed in 64.18s (0:01:04)`
- `run_cascade_sweep.py --dataset csv:physionet --policy greedy_entropy --train-seed 0 --out-dir <scratch>/fix_K/m`, then `check_sweep_equivalence_v3.py` → `csv-physionet_ts0_greedy_entropy_softmax.json: 800 draw records x all round-1 fields -> IDENTICAL` (exit 0)

No fix was left unapplied.

Files:
- F:/FAU/PhD/Side Quest/CAFA_exp/scripts/run_cascade_sweep.py
- F:/FAU/PhD/Side Quest/CAFA_exp/tests/test_oracles_v3.py
- C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/fix_K/run_mutations.py
- C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/fix_K/m/csv-physionet_ts0_greedy_entropy_softmax.json