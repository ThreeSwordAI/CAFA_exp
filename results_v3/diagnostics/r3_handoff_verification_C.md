Slice C has 12 discrepancies, listed below most important first. I checked the current text: `handoff.md` and `hpc/README_v3.md` were both edited at 14:28:51, during this check. That edit already fixed the "Active in every busy sample" line, so the new wording (70 of 72 busy samples) is what I verified.

**Discrepancies**

1. **§4 Round 3 header (line 251)**
   - Handoff text: "`git diff --stat 16da5a0 b85ac6a` on the code: 23 files, +3,408 / −63."
   - Source: that command gives 23 files, +3,408/−63, but 5 of those files are `results_v3/logs/` logs (r3_code_pytest_full_suite and the 4 r3_taskL_smoke logs, +111). The code-only figure is 18 files, +3,297/−63. Also, `b85ac6a` is not the last code commit: `ecf553f` (make_tables_v3.py, test_reporting_v3.py) and `95f9480` (README) came after it. Excluding `results_v3/` and `configs/committed_v3*`, 16da5a0..dfdc149 is 18 files, +3,317/−65.
   - Corrected: "`git diff --stat 16da5a0 dfdc149 -- . ':!results_v3' ':!configs/committed_v3*'`: 18 files, +3,317 / −65 (16da5a0..b85ac6a: 23 files, +3,408 / −63, of which 5 are results_v3/logs files)."

2. **§13.6 Tests (line 1476)**
   - Handoff text: "Whole suite after the code commits, before the runs: `169 passed in 273.07s`".
   - Source: the log header says the run started 13:22:31; at 273 s it ended about 13:27:04. `git log` shows the code commits at 13:27:19 (2ffeb04), 13:27:32 (5481269) and 13:27:33 (b85ac6a), so the tests ran before the commits. ecf553f later changed code again.
   - Corrected: "Whole suite on the round-3a code just before it was committed (13:22–13:27; commits 2ffeb04/5481269/b85ac6a at 13:27), before the runs: …"

3. **§13.7 intro (line 1482)**
   - Handoff text: "run at HEAD `dfdc149` with only `handoff.md` uncommitted."
   - Source: the checklist ran at 14:27:16. By then `results_v3/logs/hpc_dry_run.log` had been regenerated (14:26:59, header changed from 7da8c3c to dfdc149) and was also modified. Four logs were untracked: r3_final_checklist, r3_final_pytest_full_suite, r3_final_pytest_nine_v3, r3_handoff_facts. `hpc/README_v3.md` has been modified since (14:28:51).
   - Corrected: "run at HEAD `dfdc149`; uncommitted: `handoff.md`, the regenerated `results_v3/logs/hpc_dry_run.log`, and the untracked `r3_final_*.log` / `r3_handoff_facts.log`."

4. **§13.7 Git (lines 1484–1486)**
   - Handoff text: "[x] `git status` is clean … after the handoff commit … the handoff content commit and the hash commit (the header names both)."
   - Source: line 8 of the header says "Round-3 final content commit: in §13.7", and neither place gives a hash, so each points to the other. `git status` is not clean yet: handoff.md, hpc/README_v3.md and hpc_dry_run.log are modified, and the 4 logs above are untracked.
   - Corrected: put the content-commit hash in §13.7, e.g. "Then the handoff content commit `<hash>` (which includes hpc/README_v3.md, hpc_dry_run.log and the 4 r3 logs) and one follow-up commit that only records that hash". Tick the box only after verifying.

5. **§13.6 Background jobs (line 1466)**
   - Handoff text: "because free RAM had fallen to 1.0 GB".
   - Source: no file records RAM. `r3_background_jobs.log` only says "lanes 5 and 6 paused at 13:29:56 (process trees killed…)".
   - Corrected: "were paused at 13:29:56, about 1 min after launch (low free RAM; console only, not in any file)."

6. **§13.5 Decision (line 1443)**
   - Handoff text: "the greedy cell alone exceeds 8 h (instruction.md §6)".
   - Source: this is a straight-line projection from a 256-row smoke (361 × 28,000 / 256 = 39,484 s). instruction.md §6 (lines 212–215) states the rule in terms of the estimate.
   - Corrected: "the greedy cell's smoke-based estimate (≈ 11 h) exceeds 8 h (instruction.md §6)".

7. **§13.5 smoke table (line 1436) and README §8 (line 253)**
   - Handoff text: "85 s (8 steps; dominated by data loading)", and in the README "dominated by data loading, so it does not time an epoch".
   - Source: "8 steps" is correct (ceil(2000/256), batch 256 in configs/experiment_v3.yaml). "Dominated by data loading" is in no file. The nvidia-smi log only shows the GPU idle for most of the backbone window: of its 16 samples (13:07:18–13:08:43), one is at 29 % and one at 100 %.
   - Corrected: "85 s (8 steps; the GPU was busy in 1 of the 16 nvidia-smi samples of this window, so it does not time an epoch)".

8. **§13.6 Background jobs (line 1465)**
   - Handoff text: "The sweeps ran as six parallel lanes".
   - Source: lanes 1–4 ran from 13:28:58. Lanes 5 and 6 were killed at 13:29:56 and resumed at 13:50:32/38, and lane 7 started at 13:52:44. Completed runs: 10+12+10+18+2+4+8 = 64.
   - Corrected: "The sweeps were split into six lanes (lanes 1–4 ran from 13:29, lanes 5–6 from 13:50, plus lane 7 from 13:52)".

9. **§13.7 Tags (line 1496)**
   - Handoff text: "`git tag` shows `aaai27-submission` (→ `550f8e2`)."
   - Source: `r3_final_checklist.log` and `git tag` list 5 tags: aaai27-submission, canonical-v2, canonical-v2.1, canonical-v2.2, canonical-v2.3.
   - Corrected: "`git tag` shows `aaai27-submission` (→ `550f8e2`) besides the pre-existing `canonical-v2*` tags."

10. **hpc/README_v3.md §7 (lines 184–189), command does not match its own comment**
    - README text: the comment says to "run them last or leave them out of --datasets", but the command is `drive_v3.py --phase commit --seeds 1 2 --commit-prefix committed_v3_am02 …` with no `--datasets`.
    - Source: `drive_v3.py` runs seeds in an outer loop, datasets in PRIORITY order (mnist before fashionmnist and image:imagenette), and returns at the first non-zero rc. If MNIST seed 1 gives rc 7, FashionMNIST and Imagenette seed 1 and all of seed 2 are never committed. Also, "refuse … as at seed 0" for seeds 1–2 is a prediction; only seed 0 was observed (r2am02 logs).
    - Corrected: add `--datasets csv:physionet cube tabular:adult csv:diabetes tabular:MiniBooNE fashionmnist` to the am02 commit line, with an optional separate last line for `mnist image:imagenette`. Change the comment to "may refuse … (they did at seed 0)".

11. **hpc/README_v3.md §8 (line 201)**
    - README text: "This is the second E7 predictor-upgrade dataset".
    - Source: `results_v3/repair/` already holds 3 predictor_upgrade JSONs (mnist, tabular-MiniBooNE, tabular-adult). instruction_round3.md calls it the "Second repair dataset".
    - Corrected: "This is the fourth E7 predictor-upgrade repair (after MNIST, MiniBooNE and Adult; instruction_round3.md calls it the 'second repair dataset')".

12. **§13.5 thermal bullet (line 1440)**, minor precision
    - Handoff text: "The two exceptions are the first seconds of load, at 13:08:34 and 13:08:55".
    - Source: 13:08:34 is the backbone smoke's only busy sample, about 76 s into that run. 13:08:55 is the first busy sample of the greedy rollout, which started at 13:08:43. The 72, 70, 520.8 MHz and 87.94 °C figures are correct.
    - Corrected: "The two exceptions are the backbone smoke's only busy sample (13:08:34, 1,462 MHz) and the greedy rollout's first (13:08:55, 1,492 MHz)."

Not an error, but worth reconciling: README §8's table gives a throttled-laptop estimate of 58,260 s (16.18 h) for the greedy rollout (width scaling). The measured smoke on the same throttled laptop projects ≈ 39,500 s (≈ 11 h). Both are labelled as estimates, but they disagree by about 1.5×.

**Verified correct**
- **Smoke logs:** 85 s / 361 s / 23 s, rc 0, tag `smokerepair`. 28,000 heldout rows; 361 × 28,000 / 256 = 39,484 s ≈ 11 h. pool_v3 has 16 caches, no tagged tokens, and no `checkpoints_v3_smokerepair`.
- **README §8 numbers:** ledger times 1,602.9 / 14,565.1 / 308.2 s. Scaled values 12,823 / 9,045, 58,260 / 41,093, 1,233 / 870 s, using the factor 1.41776. `--time` about 2× (24 h / 11.41 h). Ledger cell names and the dry-run printout match the driver code. `test_hpc_dry_run_task_l_lines` passes.
- **§13.5 code claims** match `5481269`:
  - the tag helpers in `drive_v3.py`;
  - the overrides need a tag (`train_backbone_v3`);
  - `find_policy_caches` skips tagged caches;
  - `check_caches_v3` groups tagged caches;
  - `run_repairs_v3` jobs and labels `predictor_upgrade` / `predictor_upgrade_random`.
- **Task L quote:** it matches instruction_round3.md line 105, but is cut before "(the README's pattern) and mark `TBD-RUN`".
- **§13.6 ledger:** 72 r3 lines, rc 0, 11:27:51 → 12:07:22 UTC. Prefix counts and seconds match: 8 / 14.9, 16 / 2,800.2, 16 / 2,892.9, 16 / 1,760.3, 16 / 488.4. Output dirs are as stated. The lane 5/6 resume and lane 7 skip behaviour is confirmed by the .out files.
- **Test logs:** 169 passed (code log); round 2: 110 (`r2_final_pytest_full_suite.log`).
- **Test counts (`--collect-only`):** test_oracles_v3 14, test_margin_analysis_v3 26, test_reporting_v3 6, test_checkpoint_tag_v3 12; 169 in total.
- **§3/§4:**
  - the file-to-commit mapping in the round-3 table;
  - `git diff 16da5a0 -- src/` is empty;
  - the frozen test files are unchanged against aaai27-submission, and risk_control.py differs by one line;
  - the column names cited exist in the E4, cost-gap, E6 and E10 csvs.
- **§13.7:**
  - 33 and 169 passed, 0 xfailed, 0 skipped;
  - result directories present;
  - 26 committed configs (8 am10);
  - metrics_v3 has 16 files;
  - both archives give 16/16 sha256 OK (re-checked with `sha256sum -c`);
  - aistats-v3-results is not set;
  - the dry run has 72 tasks: 48 would run (24 ts1 + 24 ts2) and 24 skip (ts0);
  - the stop conditions match instruction_round3.md.
- **§8.7 / §8.8 / §10:**
  - am10 commits for all 8 datasets, none refused;
  - the table, figure and metrics directories exist;
  - F7 has open markers and z / prediction panels;
  - F3 shows cost/T with the E2 number;
  - `r3_postrun.sh` regenerates all 11 table directories, the figures, E10/E11/F7, the E9 summary and the K1 check (needs `metrics_v3_round2`); every step has rc 0.
- **README §7 / §8 CLI flags:** they match the parsers of `drive_v3.py`, `run_repairs_v3.py`, `alpha_margin_summary_v3.py` (`--train-seed`, `--output-dir`) and `margin_analysis_v3.py` (`--calfrac-dir CF PATH`, `--figure`). The v2 ts1/ts2 caches are present.

The instruction files are at `C:/Users/USER/Downloads/instruction{,_round2,_round3}.md`, not in the repo. Throwaway scripts are in `C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/verify_C/`.