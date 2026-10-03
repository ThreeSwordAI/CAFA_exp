**Slice A: 6 real discrepancies, 2 minor wording points, 2 items to confirm after the hash commit. Everything else matches its source.**

**1. Header lines 7–8: the caches arrived before `e24fad1`, not after it**
- Handoff text: "Part 3a … its handoff was committed as `e24fad1`; at that point the seed-1/2 caches were absent." and "Part 3b … started when the cluster caches arrived in `$RESULTS_ROOT\pool_v3\` at 14:32 (§13.8)."
- Sources:
  - `git log`: `e24fad1` was committed at 2026-10-03 14:42:19 +0200.
  - `results_v3/logs/r3J_handoff_facts.log`: the cache mtimes are 14:32:54 to 14:33:16.
  - `results_v3/logs/r3_final_checklist.log` (Part 3a, run at 14:27:16, HEAD `dfdc149`): "pool_v3 caches: 16".
  - The first Part-3b log, `r3J_check_caches_v3.log`, starts at 14:43:27.
- So the caches were already present when `e24fad1` was committed.
- Corrected: "Part 3a ran first. Its final checklist (14:27, `results_v3/logs/r3_final_checklist.log`) found only the 16 seed-0 caches, and its handoff was committed as `e24fad1` (14:42). The seed-1/2 caches had arrived in `$RESULTS_ROOT\pool_v3\` at 14:32–14:33; Part 3b (Task J) started after that commit (first log 14:43, §13.8)."
- Outside my slice: §13.8 line 1564 has the same error ("This was after the Part-3a handoff commit `e24fad1`").

**2. Header line 6: the cited file does not contain 12:24**
- Handoff text: "The first logged round-3 timestamp is 12:24 (pre-move hashes, `results_v3/round2/metrics_v3_round2.premove.sha256`, §13.4)."
- Source: that file holds 16 hash lines and no timestamp. Its mtime is 14:39:20. No log and no `run_log.jsonl` line contains 12:24 (the 3a verifier `r3_handoff_verification_A.md` found the same). The earliest logged round-3 time is "# start 2026-10-03 13:07:18" in `results_v3/logs/r3_taskL_smoke_backbone.log`.
- Corrected: "The first logged round-3 timestamp is 13:07:18 (`results_v3/logs/r3_taskL_smoke_backbone.log`)." Alternatively, drop the 12:24 claim.

**3. §1: the 73–79 rows cover only 3 of the 18 refused draws**
- Handoff text: "diagnosed as a tier-3 refusal on a 73–79-row deepest stratum, not a bug."
- Source: `results_v3/diagnostics/r3J_csv-diabetes_ts1_greedy_entropy_dep_refusal.json`, 18 of 20 draws refused. Over those 18 draws, at level 40, stratum k1 has:
  - n_answered 55–81
  - selective risk 0.055–0.132
  - HB p 0.029–0.901
- The 73–79 range comes only from draws 0–2, the three printed in `r3J_diagnose_refusal_diabetes_greedy_ts1.log`.
- Corrected: "diagnosed as a tier-3 refusal: on split 778 the deepest stratum has only 55–81 answered calibration rows at the first level, and tier 3 certifies no level in 18 of 20 draws; not a bug."
- Outside my slice: §13.8 line 1643 has the same error. It should read 55–81 rows, risk 0.055–0.132, p 0.029–0.901 over the 18 refused draws.

**4. §1: "closer to α" is wrong for Adult greedy seed 1**
- Handoff text: "In six of them the low-tier-1 seed has its deepest stratum closer to α, or a different α."
- Source: `results_v3/tables/TABLE_E4_seed_flags.csv`. Adult greedy seed 1 has r_full 0.330 against α 0.25, so it is 0.080 above α. Seed 0 has r_full 0.196, which is 0.054 below α. Seed 1 is therefore farther from α, not closer.
- Corrected: "In six of them the low-tier-1 seed has a smaller (possibly negative) deepest-stratum margin α − r_full, or a different α." I checked this wording against all 7 flagged cells. MiniBooNE random remains the exception.

**5. §10 step 1: the λ_ref sweep is not a remaining ablation**
- Handoff text: "Their commands are those of step 3 with `--seeds 1 2`: the δ split, G = 8, and the λ_ref sweep (the λ_ref 0.5 / 0.7 / 0.9 tables already cover all seeds, …)."
- Sources:
  - `results_v3/tables_e9_lambda_ref_{0.5,0.7,0.9}/TABLE_E4_cascade.csv` have 48 rows each.
  - `r3J_make_tables_lr0.5.log`: "wrote tables for 48 cells".
  - Step 3 has no λ_ref-sweep command.
  - §13.9 lists only "δ-split, G = 8 and cal-frac".
- Corrected: "Their commands are those of step 3 with `--seeds 1 2`: the δ split and G = 8. No λ_ref sweep is needed: the λ_ref 0.5 / 0.7 / 0.9 tables already cover all seeds, since the main sweeps sweep every key."

**6. §13 Scope, "Author decisions" sub-bullet: stale after Part 3b**
- Handoff text: "every existing committed JSON are untouched; the only new commits are the eight E9 `committed_v3_am10_*` files."
- Source: `git diff --name-status 16da5a0 e24fad1 -- configs/` shows 8 added files. `e24fad1..HEAD` shows 50 more added: 16 main, 16 am10, 12 am02 and 6 BEFORE, all seeds 1–2. No file was modified.
- Corrected: "… every existing committed JSON is untouched. The new commits are the eight seed-0 `committed_v3_am10_*` files (Part 3a) and the 50 seed-1/2 files of Part 3b (16 main, 16 am10, 12 am02, 6 E7 BEFORE)."
- This bullet sits under Scope, not in §13.1–13.7, so the "left as written" exemption does not cover it.

**Minor wording**
- **§1, "24 groups":** "The 32 cluster caches … greedy = random … in all 24 (dataset, seed) groups." `r3J_check_caches_v3.log` has 24 PASS lines, which is 8 datasets × seeds 0–2. The 32 cluster caches make up 16 of those groups. Suggested: "in all 24 (dataset, seed) groups of seeds 0–2, 16 of them the cluster seeds".
- **§4 line 283 and §10 step 1, "first submission":** the text says "the first Alex submission died on `DEBUGINFOD_URLS`" and "the defect that failed the first submission". In `hpc_sacct_round3.txt`, the first arrays submitted (`4439152` and `4439153`, at 13:16:11) were CANCELLED+ before they started. The arrays that failed were `4439177` and `4439178`, submitted at 13:29:44; all 16 of their stdout files show the error. Suggested: "the first submissions that ran (`4439177`, `4439178`)".

**To confirm after the hash commit (no file can confirm them yet)**
- **Tag:** §13.9 marks "[x] Tag" and header line 11 says the tag `aistats-v3-results` points to the final commit. `r3J_final_checklist.log` says "aistats-v3-results set: 0", and `git tag -l` does not list it yet. The same applies to "[x] Git: `git status` clean after the hash commit".
- **Instruction text:** I could not check the quoted sentence from `instruction_round3.md` ("If 3b's caches are not present …") or the "Task J.4" reference. The file is not in the repo and I did not find it under `F:/FAU/PhD/Side Quest`.

**Checked and correct**
- **Header:**
  - Round-1, round-2 and round-3 spans and their arithmetic.
  - `550f8e2` is an ancestor of `aistats-v3` and is the target of `aaai27-submission`.
  - `25c04ad` is the round-2 final content commit.
- **§1, Part 3b paragraph:**
  - Alex with A40 (66 stdout files, "on alex").
  - All backbones within 0.03 of seed 0; the largest change is +0.0160.
  - 48 cells:
    - maximum certified violation 0.02;
    - maximum mean `max_excess_se` −1.703;
    - 47 cells at certified deployment 1.00, the exception at 0.05.
  - Tier-1 mean 0.4683, and 0.4869 / 0.4362 / 0.4819 per seed.
  - 7 flagged cells.
  - E10: 960 points, ρ 0.914, 944/960 within ±0.2.
  - E7 MNIST at seeds 1–2.
- **§3:**
  - 158 ledger lines between 12:46:52 and 14:08:49 UTC.
  - Prefix totals: 16/27.1, 16/32.2, 16/29.1, 32/5,635.6, 32/5,733.4, 24/4,778.8, 22/2,819.1.
  - Exactly 4 non-zero return codes, all rc 7 am02 commits.
  - Cluster ledger: 48 lines, all rc 0, with 16 backbones (1,126.3 s) and 32 rollouts (6,822.8 s).
- **§4 rows:**
  - `981943c`: both Slurm files plus `test_slurm_profile_sourced_before_nounset`.
  - `da464ee`: `seed_flags`, `seed_groups`, and 2 new tests in `test_reporting_v3.py`.
  - No `src/` diff since `16da5a0`.
- **§10 step 1b:**
  - README §8 has the two `sbatch` lines.
  - `test_hpc_dry_run_task_l_lines` exists.
  - The `run_repairs_v3.py` flags and output names match.
  - The cal-frac command matches the seed-0 sweep form.
  - `metrics_v3_dw`, `metrics_v3_G8`, `metrics_v3_calfrac025` and `metrics_v3_calfrac100` hold seed 0 only.
- **§11 rows:**
  - E10, seed 0: 320 points, ρ 0.905, 318/320; key `dep`: ρ 0.935, 80/80.
  - E10, all seeds: key `dep` ρ 0.950, 236/240.
  - Every tier-1 mean ± sd and Diabetes greedy certified deployment 0.683 ± 0.548 match `TABLE_E4_cascade_seeds.csv`.
  - MNIST repairs at seeds 1–2: `type_II` → `feasible`, family minimum 0.2391 → 0.0100 and 0.2504 → 0.0132, tier 1 0 → 1, certified violation 0 → 0.
- **§13 Scope, first bullet:** the 16 caches at the start are confirmed by `r3_final_checklist.log`; arrival at 14:32 is confirmed.
- **§13.9:**
  - HEAD and the uncommitted files.
  - Test counts: 33 passed in 66.08 s; 172 passed in 283.99 s, run with `-rxXs`, with no xfailed or skipped tests.
  - 48 caches (16 per seed), none with `max_rows`, no tagged token.
  - 8 seed-0 checkpoints, marked optional in README §6.
  - Metrics files 48 / 48 / 36.
  - `configs/committed_v3*`: 76 files (24 / 24 / 18 / 9 / 1).
  - Repair JSONs: 33, of which 22 are seeds 1–2.
  - Frozen files: one line changed in `risk_control.py`; the four test files are unchanged.
  - Archives: 16 listed each, rc 0.
  - Dry run: 72 tasks, 16 would run (all seed-1/2 backbones), 56 skipped.

I edited no files. My helper script is `C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/verify3b_A/ledger.py`.