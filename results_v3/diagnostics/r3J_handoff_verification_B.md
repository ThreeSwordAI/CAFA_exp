I found five discrepancies in §13.8 and one optional clarification. Everything else in the section matches its sources.

**Discrepancies**

1. **Line 1564 (Start): order relative to `e24fad1`**
   - Handoff: "This was after the Part-3a handoff commit `e24fad1`, which therefore still says 3b did not start."
   - Source:
     - `git log` gives `e24fad1` at 2026-10-03 14:42:19 +0200 (author and committer date).
     - The cache mtimes are 14:32:54–14:33:16 (`r3J_handoff_facts.log`; re-checked on all 32 files in `F:/CAFA_results/pool_v3`). The ledger, sacct and tgz mtimes are 14:35:52–14:35:54.
     - So the files arrived about 7–9 min **before** `e24fad1`. Only the 3a checklist came first: `results_v3/logs/r3_final_checklist.log` was run at 14:27:16 on HEAD `dfdc149`.
   - Corrected: "This was after the Part-3a final checklist (14:27:16, `results_v3/logs/r3_final_checklist.log`) and 7–9 min before the Part-3a handoff commit `e24fad1` (14:42:19 local), which nevertheless still says 3b did not start."

2. **Line 1588 (Cluster provenance): the cluster-side fix is partly in the returned files**
   - Handoff: "The change made on the cluster before the successful resubmission is not in the returned files."
   - Source: `results_v3/logs_hpc_round3/cafa_v3_backbone.o4439223_8` contains a shell trace of the modified preamble (lines 25–1099). In order it runs:
     - `+ set +eu`
     - `+ source /etc/profile`
     - `+ module load python`
     - `+ cd …`
     - `+ source hpc/env.local.sh`
     - `+ source activate /home/vault/iwi5/iwi5359h/envs/cafa`
     - `+ set -eu`
   - None of the other 65 stdout files contains a trace.
   - Corrected: "The modified batch script itself is not in the returned files. The stdout of the first successful task (`logs_hpc_round3/cafa_v3_backbone.o4439223_8`) traces its preamble: `set +eu`, `source /etc/profile`, `module load python`, `source activate …`, then `set -eu`. The other successful arrays' stdout files have no trace."

3. **Line 1643 (Diabetes greedy seed 1 refusal): ranges come only from draws 0–2**
   - Handoff: "has only 73–79 answered calibration rows. Their selective risk is 0.064–0.076 and their HB p-values are 0.047–0.103, all above δ₃ = 0.025. Tier 3 certified no level in 18 of 20 draws."
   - Source: `results_v3/diagnostics/r3J_csv-diabetes_ts1_greedy_entropy_dep_refusal.json`. The log prints only draws 0–2; the JSON has all 20.
     - In the 18 refused draws, stratum k=1 at level 40 has n_answered 55–81, sel_risk 0.0548–0.1316 and p 0.0286–0.9005.
     - In the 2 certified draws (3 and 12), p is 0.0155 and 0.0162, below δ₃. These match the tier-3 draws (778, 3) and (778, 12) in `F:/CAFA_results/metrics_v3/csv-diabetes_ts1_greedy_entropy_softmax.json`.
   - Corrected: "In the 18 draws where tier 3 certified no level, the deepest stratum has only 55–81 answered calibration rows, selective risk 0.055–0.132 and HB p-values 0.029–0.901, all above δ₃ = 0.025. In the other 2 draws (3, 12), p = 0.016 and tier 3 certifies."

4. **Line 1648 (Imagenette greedy seed 2, split 780): ranges miss two of the five deployed tier-1 rules**
   - Handoff: "the deployed tier-1 rules have deepest-stratum (k = 3) calibration-pool risk 0.065–0.077 against test-split risk 0.103–0.105 (n 447). The pooled risk is 0.084–0.090 < α = 0.10."
   - Source: `r3J_diagnose_violation_imagenette_greedy_ts2.log` and `results_v3/diagnostics/r3J_image-imagenette_ts2_greedy_entropy_dep.json`, `by_split.780.deployed_rules`. Five tier-1 rules were deployed (16 flagged draws):

     | rule param | draws | cal | test | pooled |
     |---|---|---|---|---|
     | 0.9596 | 3 | 0.0772 | 0.1029 | 0.0896 |
     | 0.9697 | 5 | 0.0689 | 0.1029 | 0.0853 |
     | 0.9798 | 4 | 0.0647 | 0.1051 | 0.0842 |
     | 0.9899 | 1 | 0.0626 | 0.1074 | 0.0842 |
     | 1.0000 | 3 | 0.0585 | 0.1007 | 0.0788 |

     The handoff ranges cover only the first three rules.
   - Corrected: "calibration-pool risk 0.059–0.077 against test-split risk 0.101–0.107 (n 447). The pooled risk is 0.079–0.090 < α = 0.10."

5. **Line 1723 (E7, policy change): "only movement" overstates**
   - Handoff: "The only movement is in FashionMNIST's verdict agreement over the splits: 5/5 → 4/5 at seed 1 and 4/5 → 3/5 at seed 2."
   - Source: the pasted lines and `results_v3/repair/*_ts{1,2}_policy_change.json` show violation changes:

     | cell | raw violation | certified violation |
     |---|---|---|
     | Imagenette seed 1 | 0.11 → 0.09 | 0.00 → 0.01 |
     | Imagenette seed 2 | 0.06 → 0.05 | 0.00 → 0.01 |
     | MNIST seed 1 | 0.00 → 0.04 | 0.00 → 0.00 |
     | MiniBooNE seed 2 | 0.00 → 0.01 | 0.00 → 0.00 |
     | Adult seed 1 | 0.01 → 0.02 | 0.00 → 0.00 |

   - Corrected: "The only change in verdict agreement is FashionMNIST's: 5/5 → 4/5 at seed 1 and 4/5 → 3/5 at seed 2. Violation rates move slightly: Imagenette raw 0.11 → 0.09 and certified 0.00 → 0.01 at seed 1, raw 0.06 → 0.05 and certified 0.00 → 0.01 at seed 2; raw only, MNIST seed 1 0.00 → 0.04, MiniBooNE seed 2 0.00 → 0.01, Adult seed 1 0.01 → 0.02."

**Optional clarification (lines 1580 and 1582; the text is literally correct)**
- "`4439226` (12 tasks)" and "backbones 6–171 s": task `4439226_8` ran for 6 s and trained nothing. Its stdout says `skip (exists) backbones:csv:physionet:na:ts1`, because `4439223_8` had already trained that checkpoint.
- So 1 + 11 + 4 = 16 backbones were trained, matching the ledger. The 16 trainings took 27–171 s in sacct.
- Suggested: "`4439226` (12 tasks; task 8 only skipped the existing PhysioNet seed-1 checkpoint)" and "backbones 27–171 s (the 6-s task trained nothing)".

**What I checked and found correct**
- **J.1 cache checks** against `r3J_check_caches_v3.log`, `r3J_verify_cluster_caches.log` and the cache metadata of all 32 seed-1/2 caches:
  - 24/24 PASS with |Δ| = 0;
  - v2/v3 heldout rows identical for MNIST, MiniBooNE and Adult;
  - n and T as at seed 0, `max_rows` None;
  - Imagenette greedy has `policy_amp` True and batch size 32;
  - each cache's 64-character checkpoint sha256 starts with the 12-character prefix in its cluster backbone log;
  - MNIST full-acquisition accuracy 0.994964 at both seeds (141 errors), with labels, scores, orders and digests differing;
  - `phase1_caches.csv` has 48 rows;
  - `full_obs_acc` is the same value as `full_obs_train_acc` (`train_backbone_v3.py`), all within 0.03, largest drop Adult seed 2 −0.0086;
  - no seed-1/2 checkpoints in `F:/CAFA_results/checkpoints_v3`.
- **Cluster provenance** against `hpc_sacct_round3.txt`, `r3J_cluster_provenance.log`, `run_log_hpc_round3.jsonl` and the stdout files:
  - Alex, partition a40, NVIDIA A40 in all 66 stdout files;
  - array IDs and task counts; `4439227` is the 4 `--epochs 60` tasks and `4439229` the 4 Imagenette tasks;
  - elapsed ranges, failure message, the cancelled and failed arrays;
  - cluster ledger 48 lines, rc 0, 16 / 1,126.3 s / longest 157.0 s and 32 / 6,822.8 s / longest 945.9 s, times correct in local time;
  - TinyGPU assumption in `hpc/README_v3.md`; the slurm diff and test name in `981943c`.
- **J.2 ledger table:** every row's count, seconds and rc matches `run_log.jsonl`, 158 lines in total. The six BEFORE commits are outside the ledger and were made from `pool_v2`.
- **Committed α** in all 48 main, am10 and am02 configs at seeds 0–2, including Adult seed 2 at 0.20 (floor 0.1415) and the am02 rc-7 messages.
- **Seed-aggregated table:** all 16 rows × 11 columns match `TABLE_E4_cascade_seeds.csv`, which itself matches `TABLE_E4_cascade.csv` (sample sd).
- **Seed-flags table:** all 16 rows match `TABLE_E4_seed_flags.csv`; the flag threshold is 0.25 (`make_tables_v3.py`); the flagged-cell list and every number in the flagged-cells reading are correct.
- **Acceptance bullets:**
  - certified violation max 0.02 (Adult greedy seed 2);
  - max_excess_se from −7.068 to −1.703;
  - 47 of 48 cells deployed, Diabetes greedy seed 1 at 0.05 (none 0.95);
  - Imagenette raw violation 0.19 and 0.11 with their by-split values;
  - mean tier-1 share 0.468, per seed 0.487 / 0.436 / 0.482;
  - integrity checks all True in both diagnosis JSONs;
  - 18 of 20 refused draws, split 778.
- **E7:** all 22 pasted lines are identical to the repair logs and consistent with the JSONs. The MNIST, MiniBooNE and Adult predictor-upgrade readings are correct. F4 globs all 33 repair JSONs.
- **E9:** all 48 cells match the three CSVs; the margin-0.10, 0.96-maximum and refused statements hold; tier-1 share never falls with margin; the per-seed and am10/am02 table directories exist.
- **E10:** 960 points (seeds × keys × splits) and 0.914, 944/960, 942/960, 0.906, 950/960, 0.950, 236/240. The cal-frac points are seed 0 only.
- **Cost gap and J.4:** `TABLE_E4_cost_gap.csv` has 48 rows; `r3J_table_invariance.log` shows no changes to seed-0 rows; Task L outputs are absent.

**Note (no edit needed):** in `results_v3/tables_e9_alpha_margin02/TABLE_E6_baselines.csv`, seed 0 has 10 baselines and seeds 1–2 have 12. The seed-0 rows lack `oracle_stratum_safe` and `oracle_stratum_safe_mondrian`.

I did not verify "Task J does not ask for them" in J.4, because `instruction_round3.md` is not in the repo.

Scratch scripts are in `C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/verify3b_B/`. No repo files or files under `F:/CAFA_results` were modified.