Slice A has 8 discrepancies. Every other number, path, hash and count in the slice matches its source.

**Discrepancies**

1. **Round-3 start time has no source file** (§13 intro, line 1150; header line 5 also says "≈ 12:20").
   - Handoff text: "Start: 2026-10-03 ≈ 12:20 local (first logged timestamp 12:24:55)."
   - Source: "12:24:55" (and 10:24:55 UTC) appears in no file in the repo apart from handoff.md itself, including `results_v3/logs/*` and `results_v3/run_log.jsonl`.
     - The first logged round-3 timestamp is `# start 2026-10-03 13:07:18` in `results_v3/logs/r3_taskL_smoke_backbone.log`.
     - The first round-3 ledger start is 2026-10-03T11:27:51 UTC, which is 13:27:51 local.
     - The earliest round-3 file change is `scripts/__pycache__/run_cascade_sweep.cpython-312.pyc` at 12:29:43.
   - Corrected: "Start: 2026-10-03 ≈ 12:20 local (session start, not logged; first logged round-3 timestamp 13:07:18, `results_v3/logs/r3_taskL_smoke_backbone.log`)."

2. **The review-process claims in §13 "Method" have no source file** (lines 1170–1183).
   - Handoff text: "Four agents implemented the four code tasks in parallel … The reviewers reported 13 findings (2 medium, 11 low). All were fixed before any run, each covered by a test that fails on the unfixed code (mutation checks)."
   - Source: nothing records this.
     - `results_v3/diagnostics/` has only a round-2 review file (`r2_review_taskB.json`), no round-3 one.
     - The commit messages from `16da5a0..HEAD` mention no review, findings or mutation checks.
     - There are five tasks (G, H, I, K, L) in three code commits (`2ffeb04`, `5481269`, `b85ac6a`), not "four code tasks".
   - Corrected: either save the review record (for example `results_v3/diagnostics/r3_review_*.json`) and cite it, or label the paragraph "Method (not recorded in a campaign file)". Also replace "four code tasks" with the actual split.

3. **§13.2 "Reading": the tier-1 share does not rise in every non-degenerate cell.**
   - Handoff text: "the tier-1 share rises with the margin in every non-degenerate cell."
   - Source: `results_v3/tables/TABLE_E9_alpha_margin.csv`.
     - Diabetes greedy is 0.00 / 0.00 / 0.00 at margins 0.02 / 0.05 / 0.10, and it is not degenerate (λ_ref 0.798, G = 2).
     - MNIST is 1.00 → 1.00, and CUBE greedy and Adult greedy are 1.00 → 1.00 from margin 0.05 to 0.10.
   - Corrected: "the tier-1 share never falls as the margin grows, and at margin 0.10 it is 1.00 in every cell except Diabetes (greedy 0.00 at all three margins, deepest stratum `type_II`; random 0.00 → 0.00 → 0.26)."

4. **§13.2 "Reading" overstates what E9 shows and contradicts Task K.**
   - Handoff text: "So the tier-3 cost at margin 0.05 (FashionMNIST, Imagenette, MiniBooNE) is a cost of the target α, not of the cascade."
   - Source: E9 only shows that tier 3 disappears when α is raised by 0.05. At the primary α, `results_v3/tables/TABLE_E4_cost_gap.md` labels these cells "sample-limited":
     - FashionMNIST: cascade / oracle 2.197 / 1.995;
     - Imagenette: 3.806 / 4.974;
     - MiniBooNE random: 3.743.
     - In those cells the ex-post oracle at the same α costs 0.189–0.464 T, against 0.862–0.940 T for the cascade.
     - MiniBooNE greedy is labelled near-oracle, with the oracle infeasible on 3/5 splits.
   - Corrected: "So the tier-3 cost of FashionMNIST, Imagenette and MiniBooNE at margin 0.05 disappears once α is raised by 0.05. At the primary α, Task K classes FashionMNIST, Imagenette and MiniBooNE random as sample-limited (§13.4), so the cost depends on both the target α and the calibration size."

5. **§13.1: the sensitivity columns are not only in the CSV and JSON.**
   - Handoff text: "**Sensitivity columns** (CSV and summary JSON only)".
   - Source: `results_v3/tables/TABLE_E10_margin_summary.md` also has `pred_tier1_nk_calpool` and `pred_tier1_hyper` rows (md lines 11–12 and 15–16). Only `TABLE_E10_margin.md` leaves them out.
   - Corrected: "**Sensitivity columns** (in the CSV and the summary JSON / md; not in `TABLE_E10_margin.md`)".

6. **§11 E7 FashionMNIST row presents a projection as a smoke measurement.**
   - Handoff text: "TBD-RUN (cluster; laptop smoke ≈ 11 h for the greedy rollout, GPU throttled)".
   - Source: the smoke measured 361 s for 256 rows (`results_v3/logs/r3_taskL_smoke_rollout_greedy.log`). The ≈ 11 h is a linear projection: `hpc/README_v3.md` §8 gives 361 × 28,000 / 256 ≈ 39,500 s, where 28,000 is the `n_heldout` in `configs/committed_v3_fashionmnist_ts0.json`.
   - Corrected: "TBD-RUN (cluster; laptop smoke: greedy rollout 361 s for 256 rows, a linear projection of ≈ 11 h for the 28,000 heldout rows; GPU thermally throttled)".

7. **§13.3: the "no draw" claim is broader than the file it cites.**
   - Handoff text: "It is **0.000 in every cell of every table directory** (seed 0; `r3_handoff_facts.log`). In no draw of round 2 or 3 would tier 2 have mattered."
   - Source: `r3_handoff_facts.log` covers table aggregates only. In particular, `inverse_info` appears only at key `dep` for 10 cells.
   - The claim itself is true. A direct count over all 61,720 draw records found 0 draws with `budget` True and `threshold` False, and 0 draws with tier 2. That count covered `metrics_v3`, `_round2`, `_alpha_margin02`, `_alpha_margin10`, `_calfrac025`, `_calfrac100`, `_dw`, `_G8` and `_hbfix_single`, all keys and both schemes. But no campaign file records this count.
   - Corrected: save that check as a log and cite it, or narrow the sentence to "In no table cell of round 2 or 3 would tier 2 have mattered."

8. **§11 E10 row: the figure path is incomplete.**
   - Handoff text: "`results_v3/tables/TABLE_E10_margin_summary.json`, `F7_margin.pdf`".
   - Source: the figure is at `results_v3/figures/F7_margin.pdf`, not in `results_v3/tables/`.
   - Corrected: "`results_v3/tables/TABLE_E10_margin_summary.json`, `results_v3/figures/F7_margin.pdf`".

**Checked and correct**

- **Header line 5:**
  - `F:\CAFA_results\pool_v3` has only the 16 `_ts0` caches and no `_ts1_` / `_ts2_` cache.
  - The end time ≈ 14:30 fits `r3_final_checklist.log` (14:27:16) and the handoff.md modification time (14:28:51).
  - 12:20 → 14:30 is ≈ 2.2 h.
- **§1 paragraph:**
  - `git diff 16da5a0 HEAD -- configs/` shows only the eight `committed_v3_am10_*` files, all added.
  - `r3_taskK_sweep_equivalence.log` shows all 16 cells IDENTICAL, rc 0. The log line says "all round-1 fields", but `scripts/check_sweep_equivalence_v3.py` compares every leaf of the round-2 file except `meta.cache_meta`, so "every round-2 field" is accurate.
- **§13 intro:**
  - The instruction quote matches `C:/Users/USER/Downloads/instruction_round3.md` line 5, and the §0 decisions match.
  - The commit hashes `2ffeb04`/`ecf553f`, `5481269`/`95f9480` and `b85ac6a`/`dfdc149` match the task labels in their messages.
- **§13.1:**
  - The command matches `r3_margin_analysis.log`, rc 0.
  - `tests/test_margin_analysis_v3.py` collects 26 tests.
  - 320 rows (16 cells × 4 keys × 5 splits) and 640 cal-frac rows.
  - Every value in the result table matches `TABLE_E10_margin_summary.json`. That covers ρ, p, within ±0.2, mean absolute error, the 960-point row, the by-key values (0.449 / 0.777 / 0.706; 80, 78, 80) and the by-dataset range (0.762 PhysioNet to 0.975 MiniBooNE; MNIST ρ None, 40/40).
  - The 2 points outside ±0.2 match both the CSV and `r3_handoff_facts.log`.
  - Median n_k is 1,314 and median α is 0.15 over the main points. At key 0.5, 68/80 points have obs = pred = 1.
  - The F7 panel features match the code.
- **§13.2:**
  - The α and λ_ref `dep` table matches `configs/committed_v3_am10_*.json` for all 8 datasets. No α is ≤ the design margin of 0.05.
  - Ledger: `r3am10:commit` is 8 runs, rc 0, 14.9 s; `r3am10:sweep` is 16 runs, rc 0, 2,892.9 s.
  - The pasted E9 rows are byte-identical to `TABLE_E9_alpha_margin.md`, and the CSV has λ_ref and G per margin.
  - All "At margin 0.10" bullets match `tables_e9_alpha_margin10/TABLE_E4_cascade.csv`:
    - certified deployment 1.0 and certified violation 0 in all 16 cells;
    - `max_excess_se` from −11.478 to −2.694;
    - raw violation at most 0.08; FashionMNIST random 0.000–0.400 by split; MiniBooNE greedy 0.03 (0.000–0.100);
    - Diabetes greedy tier 3 1.00 with `type_II`; Diabetes random 0.26 / 0.74;
    - Adult at α 0.30 and PhysioNet at α 0.25: λ_ref 0, G 1, cost / T 0.
- **§13.3:**
  - The column order and the seeds-table columns match the round-2 versions at `16da5a0`.
  - T comes from `meta`. The tier-2 definition matches `make_tables_v3.py`, and "by construction" matches `src/cafa/cascade.py`.
  - The largest gap between `escalated_fraction` and 1 − answered fraction is 2e-16.
  - E6 gains `feasible_rate`. The F3 features match `make_figures_v3.py`.
  - `r3_postrun.sh` and all `r3_make_*` logs end with rc 0. `r3_table_invariance.log` shows 0 value differences and 0 missing rows.
- **§11 rows:**
  - All cost / T values and the marginal (max 0.496) and Mondrian (max 0.548) ranges match `tables/TABLE_E4_cascade.csv`.
  - Every cascade / oracle ratio and label matches `TABLE_E4_cost_gap.md`. "Mixed" is not a label in that table, but §13.4 defines it.
  - All E11 tier-1 triples match `TABLE_E11_calfrac.csv`, which has 5 draws per cell at cal_frac 1.0.
  - The tier-2 row and the E9 row match.

The throwaway script is `C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/verify_A/tier2.py`. I edited no repo files. `hpc/README_v3.md` currently shows an uncommitted change that I did not make; it was not modified in the session-start git status.