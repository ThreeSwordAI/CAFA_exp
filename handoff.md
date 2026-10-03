# CAFA v3 campaign — handoff

- Round 1: 2026-10-01 13:09 → 2026-10-02 ≈ 01:15 local (UTC+2), ≈ 12 h; ended at stop condition 5 (§9, resolved in round 2).
- Round 2 (`instruction_round2.md`, Tasks A–F): 2026-10-03 00:55 → ≈ 09:30 local, ≈ 8.5 h (most of it waiting for the thermally throttled GPU, §12.4).
- Round 3 (`instruction_round3.md`, Part 3a: Tasks G, H, I, K, L): 2026-10-03 ≈ 12:20 → ≈ 14:50 local, ≈ 2.5 h. The start is the session start, which is not logged. The first logged round-3 timestamp is 12:24 (pre-move hashes, `results_v3/round2/metrics_v3_round2.premove.sha256`, §13.4). Part 3b (Task J) did not start, because the seed-1/2 cluster caches are not in `$RESULTS_ROOT\pool_v3\` (§13).
- Branch: `aistats-v3` (from `550f8e2`, the `main` HEAD at the round-1 session start; tagged `aaai27-submission`)
- Round-2 final content commit: `25c04ad`.
- Round-3 final content commit: written by the follow-up hash commit; that commit changes only this line. `git log -1 aistats-v3` gives the branch tip.
- No job is running at the end of round 3. The tag `aistats-v3-results` belongs to Part 3b and is not set.

## 1. Executive summary

**Round 3, Part 3a (§13).** This round adds explanatory analyses only. No primary quantity changed: λ_ref `dep`, α rule, δ, γ, grids and committed JSONs are as in round 2. The 16 main sweeps were rerun with the new oracle code and every round-2 field is IDENTICAL (`results_v3/logs/r3_taskK_sweep_equivalence.log`), so the round-2 headline below stands.

- **E10, certifiability margin (Task G).** The tier-1 share of a (cell, λ_ref key, split) is predicted by the deepest stratum's full-information margin at the calibration-draw size. Over 320 points, Spearman ρ(observed, predicted) = 0.905 and 318/320 points lie within ±0.2 of the prediction. At key `dep` it is ρ 0.935 with 80/80 within ±0.2 (`results_v3/tables/TABLE_E10_margin_summary.json`, F7).
- **E9, α margin 0.10 (Task H).** All 8 datasets are committed. Every cell except Diabetes goes to tier 1 = 1.00. Certified violation is 0.000 in all 16 cells. Adult becomes degenerate at α 0.30, as PhysioNet already is (`results_v3/tables/TABLE_E9_alpha_margin.md`).
- **Cost / T and tier 2 (Task I).** The deployed cost / T ranges from 0.000 (PhysioNet) to 1.000 (Diabetes, Adult random). `tier2_would_certify` is 0.000 in every cell of every table directory. At draw level, budget certifies without threshold in 0 of 61,720 draw records (`results_v3/logs/r3_tier2_draw_count.log`), so tier 2 never mattered.
- **Is the cost intrinsic? (Task K).** This compares the cascade's cost with an ex-post stratum-safe oracle (`results_v3/tables/TABLE_E4_cost_gap.md`):
  - **intrinsic:** Diabetes;
  - **sample-limited:** FashionMNIST, Imagenette and MiniBooNE random (cascade / oracle 2.0–5.0);
  - **near-oracle:** PhysioNet, CUBE, MNIST and Adult greedy (1.04–1.26);
  - **mixed:** Adult random and MiniBooNE greedy (oracle infeasible on most splits).
- **Calibration size (Task K).** Doubling the calibration draw raises tier 1 from 0.12 to 0.40 (FashionMNIST greedy) and from 0.20 to 0.40 (Imagenette greedy) (`results_v3/tables/TABLE_E11_calfrac.md`).
- **FashionMNIST predictor upgrade (Task L): `TBD-RUN`.** The laptop smoke ran the greedy rollout at 361 s per 256 rows, which projects linearly to ≈ 11 h on the thermally throttled GPU. Cluster lines are in `hpc/README_v3.md` §8.

**Round 2 (final).** Round 2 fixed the Hoeffding–Bentkus boundary defect (tag `aaai27-submission`, `CHANGELOG.md`). It replaced the single calibration/test split with 5 splits × 20 draws and added noise-aware violation metrics next to the raw rate: certified violation (exact one-sided binomial test-split p ≤ 0.05) and `max_excess_se`. It also re-ran all of Phase 3 and finished Imagenette seed 0, which gives **16 seed-0 cells**. At λ_ref `dep`, pooled over the 5 splits (`results_v3/tables/TABLE_E4_cascade.md`, §8):
- certified deployment is 1.00 in all 16 cells;
- certified violation is ≤ 0.010 and mean `max_excess_se` < 0 (−6.616 … −3.152) in every cell;
- the raw test stratum-violation rate is ≤ 0.100 pooled in every cell. The round-1 over-δ cells reach it only on split 778, with FashionMNIST up to 0.45 / 0.50 there;
- mean tier-1 share is 48.7 % over 16 cells, 53.6 % on the 14 round-1 cells (round 1: 62.1 %);
- Imagenette deploys tier 3 in 0.80 / 0.91 of draws (greedy / random).

Further results:
- **E5 study D** (§7, §12.2): with powered calibration, valid rules just below α give raw test violation 0.235 against true violation 0.000 and certified violation 0.005.
- **E7:** MNIST `type_II` → `feasible`, tier 1 0.00 → 1.00 (§8.6).
- **E9 α rule** (margin 0.02, grid 0.01; §8.7): PhysioNet tier 1 → 1+3, Adult greedy tier 1 → 3; MNIST and Imagenette cannot be committed (α ≤ design margin).
- **Seeds 1–2:** `TBD-RUN` on TinyGPU (`hpc/README_v3.md`). Round-2 details and the HB-fix decision flips: §12.

**Round 2, Task A.** The Hoeffding–Bentkus boundary defect of §9 is fixed (option (b) of §9, the authors' decision; tag `aaai27-submission`, `CHANGELOG.md`, §12.1). The round-1 Phase-3 numbers were computed with the defect present and the single-split protocol and are superseded; §8 and §11 now hold the round-2 numbers. The round-1 files are archived (`$RESULTS_ROOT\metrics_v3_round1\`, `results_v3/round1/`). On the round-1 protocol the fix changes 186 of 5,600 deployed (cell, λ_ref, draw) decisions (§12.1). The Imagenette greedy rollout left running in round 1 had died at 1296/5358 rows without writing a cache; it was relaunched (§12.1).

Round-1 summary (superseded numbers kept for reference):

- **Phase 0 — done.** Nine v3 test files: 33 passed, including 1 regression test added this session. Whole suite: see §5. Synthetic Type-II and feasible end-to-end checks pass.
- **Phase 1 — seed 0 done for 7 datasets.** All 7 backbones and all 14 caches exist; greedy and random give the same full-acquisition accuracy (difference 0) in every cell. CUBE and MiniBooNE miss their full-observation targets even after the one allowed 60-epoch retrain; CUBE's 0.98 target is above the generator's Bayes accuracy of 0.97025.
- **Imagenette seed 0 — partial.** The backbone is done (full-observation accuracy 1.0000). The greedy rollout was running at session end; the random rollout is `TBD-RUN`.
- **Seeds 1 and 2:** `TBD-RUN`.
- **Phase 2 — done.** Every acceptance check is met (§7).
- **Phase 3 — done for the 14 seed-0 cells.** Commits, 100-draw sweeps, tables, figures, E7 (9 repair JSONs) and E9 (λ_ref sweep, δ split, G = 8) are complete. At λ_ref `dep`, certified deployment is 1.00 in all 14 cells (`results_v3/tables/TABLE_E4_cascade.md`).
- **Over-δ cells.** The test stratum-violation rate exceeds δ = 0.10 in 4 of the 14 cells: MiniBooNE 0.110 / 0.120 and FashionMNIST 0.350 / 0.580. Independent diagnoses found no implementation bug (`results_v3/diagnostics/`), so they are reported as results (§8.5).
- **E7 MNIST matches the plan's expectation.** At `dep` the deepest stratum goes `type_II` → `feasible` (family minimum 0.295 → 0.011) and the tier-1 share goes 0.00 → 1.00 (`results_v3/repair/mnist_ts0_predictor_upgrade.json`).
- **Stop condition.** `_hb_pvalue_array` computes `ceil(n * r_hat)` and is off by one when floating-point rounding pushes n·r̂ just above the integer error count. This only makes p-values larger (validity holds, power drops), and it flips some certification decisions. It is documented with a strict-xfail test (`tests/test_frozen_hb_boundary.py`) and a prevalence scan. Fixing a frozen file, and with it the AAAI numbers, is the authors' decision (§9).

## 2. Environment

| item | value | source |
|---|---|---|
| OS | Windows 10 Home Single Language 10.0.19045 | `Get-CimInstance Win32_OperatingSystem` |
| CPU | 11th Gen Intel Core i5-11400H, 6 cores / 12 threads | `Win32_Processor` |
| RAM | 16,867,012,608 B (≈15.7 GiB); ≈5.3 GB free at session start | `Win32_ComputerSystem` / `Win32_OperatingSystem` |
| GPU | NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB, driver 610.78 | `nvidia-smi` |
| GPU thermals | under sustained load 87–91 °C with `clocks_event_reasons.sw_thermal_slowdown = Active`; SM clock observed between 210 and 1057 MHz (max 2100), on AC power (battery 100 %) | one reading saved at session end (`results_v3/logs/nvidia_smi_session_end.log`: 210 MHz, 91 °C, 19.54 W, sw_thermal_slowdown Active); the earlier readings are console-only (`nvidia-smi`) |
| Python | 3.12.2 (repo `.venv`) | `.venv\Scripts\python.exe --version` |
| torch / torchvision | 2.13.0+cu126 / 0.28.0+cu126; `torch.cuda.is_available()` = True | `python -c "import torch, torchvision; ..."` |
| numpy / scipy / scikit-learn / pandas | 2.5.1 / 1.18.0 / 1.9.0 / 3.0.3 | `pip list` |
| matplotlib / PyYAML / pytest | 3.11.0 / 6.0.3 / 9.1.1 | `pip list` |
| DATA_ROOT | `F:\CAFA_data` — MNIST raw + OpenML cache copied from the repo's git-ignored `data/`; FashionMNIST, AFABench CSVs, Imagenette downloaded this session | `set_env.ps1` |
| RESULTS_ROOT | `F:\CAFA_results` — `pool_v2/`, `checkpoints_v2/` copied from the repo's git-ignored `results/` | `set_env.ps1` |
| Disk | F: free 70.4 GiB at start, 67.3 GiB at end (PowerShell binary GB); DATA_ROOT 2,947,674,066 B; RESULTS_ROOT 332,001,505 B (at ≈ 00:45) | console: `Get-PSDrive`, `Get-ChildItem -Recurse \| Measure-Object Length -Sum` |

`set_env.ps1` (repo root, git-ignored) sets `DATA_ROOT`, `RESULTS_ROOT`, `PYTHONIOENCODING=utf-8`; source it in every shell.

## 3. Run ledger

Every driver-run cell has one JSON line in `results_v3/run_log.jsonl`: cell, command, start, end, seconds, returncode, output_path, log. That is 54 runs, all with return code 0:

| ledger cell prefix | runs | total seconds | non-zero rc |
|---|---|---|---|
| `smoke:` (backbones + rollouts, `--epochs 1 --max-train …`, `--max-rows …`) | 7 | 1166.7 | 0 |
| `smoke-fixfp32:` / `smoke-fixamp:` (Imagenette re-timing after the policy fix) | 1 / 1 | 174.2 / 126.7 | 0 |
| `backbones:` (seed 0, 8 datasets) | 8 | 4790.6 | 0 |
| `retrain60:` (CUBE, MiniBooNE `--epochs 60`) | 2 | 429.4 | 0 |
| `rollouts:` (seed 0, 7 datasets × 2 policies) | 14 | 32299.9 | 0 |
| `commit:` (seed 0, 7 datasets) | 7 | 16.2 | 0 |
| `sweep:` (seed 0, 14 cells, 100 draws) | 14 | 3482.7 | 0 |

Commands run outside the driver (logs in `results_v3/logs/`). Durations marked "console" were read from a `Get-Date` wrapper in the shell and are not in any file:

| phase | command | start (local) | duration | exit | output / log |
|---|---|---|---|---|---|
| 0 | `python -m pytest -q <nine v3 test files>` (after adding `tests/conftest.py`, before the code fixes) | 2026-10-01 13:1x | 40.4 s (console) | 0 | 32 passed (console; also in the `b1caf84` commit message) |
| 0 | `python -m pytest -q tests/` | 13:1x | 196.6 s | 0 | `phase0_pytest_full_suite.log` (80 passed) |
| 0 | synthetic typeII / feasible (make_synthetic_pool_cache → commit_v3 → run_cascade_sweep `--n-draws 20` → make_tables_v3) | 13:1x | < 1 min each | 0 | `phase0_synthetic_typeII.log`, `phase0_synthetic_feasible.log` |
| 1a | `python scripts/download_data_v3.py --csv --mnist --fashionmnist --openml` | 13:17 | 55.3 s (console) | 0 | `phase1a_download_small.log` |
| 1a | `python scripts/download_data_v3.py --imagenette` (background PID 10264) | 13:18 | ≈ 6 min | 0 | `phase1a_download_imagenette.log`; `F:\CAFA_data\imagenette_cache\imagenette_224.npz` (2,016,279,694 B, 13,394 images) |
| 2 | `python scripts/planted_validation.py --output-dir results_v3/planted --n-replicates 1000` (background PID 18076) | 13:19:07 | 42 min | 0 | `phase2_planted_validation.log` |
| 3d | `commit_v3.py --pool-dir F:/CAFA_results/pool_v2 --out-path configs/committed_v3before_{ds}_ts0.json` for mnist, tabular:MiniBooNE, tabular:adult | 15:1x–19:5x | seconds | 0 | `phase3d_commit_before_*_ts0.log` |
| 3d | `repair_experiment.py` × 9 (exact commands in §10 step 5): `--label predictor_upgrade` for mnist, tabular:MiniBooNE, tabular:adult; `--policy random --label policy_change` for csv:physionet, cube, tabular:adult, csv:diabetes, tabular:MiniBooNE, mnist | 15:15–20:00 | ≈ 0.6–3.3 min each (file mtimes) | 0 | `phase3d_repair_*.log`, `results_v3/repair/*.json`; batch logs `driver_repair_batch{1,2}.out` |
| 3e | `run_cascade_sweep.py --dataset csv:physionet --policy greedy_entropy --train-seed 0 --delta-weights 0.34,0.33,0.33 --out-dir F:/CAFA_results/metrics_v3_dw` | 15:17 | 66 s (console) | 0 | `phase3e_sweep_dw_csv-physionet_greedy_entropy_ts0.log` |
| 3e | `commit_v3.py --dataset mnist --train-seed 0 --n-buckets 8 --out-path configs/committed_v3_G8_mnist_ts0.json`; `run_cascade_sweep.py --dataset mnist --policy greedy_entropy --train-seed 0 --committed configs/committed_v3_G8_mnist_ts0.json --out-dir F:/CAFA_results/metrics_v3_G8` | 19:54:22 | ≈ 4 min (file mtimes 19:54:22 → 19:58:06) | 0 | `phase3e_commit_G8_mnist_ts0.log`, `phase3e_sweep_G8_mnist_greedy_entropy_ts0.log`, `driver_e9_g8.out` |
| 1 check | `python scripts/check_caches_v3.py --v2-dir F:/CAFA_results/pool_v2 --csv results_v3/phase1_caches.csv` | 01:0x | seconds | 0 | `phase1_check_caches_v3.log`, `results_v3/phase1_caches.csv` |
| 3c | `make_tables_v3.py` (dep / inverse_info / λ_ref 0.5, 0.7, 0.9 / `metrics_v3_dw` / `metrics_v3_G8`) and `make_figures_v3.py` (commands in §10 step 4) | 00:34–00:35 | seconds | 0 | `results_v3/tables*/`, `results_v3/figures/` |
| 3 diag | `diagnose_violation_v3.py` (4 cells), `diagnose_refusal_v3.py` (2 cells), `hb_boundary_draws_v3.py` (1 cell), `split_balance_v3.py` (7 datasets), `calpool_vs_test_v3.py`, `cube_bayes_v3.py`, `scan_hb_ceil_boundary.py` | 15:4x–01:0x | ≤ 2 min each | 0 | `results_v3/diagnostics/*.json`, `phase3_*.log`, `phase1_cube_bayes.log` |
| check | `tests/test_v3_scripts.py` run against the shipped (HEAD) scripts in a scratch copy | 01:04 | 12.9 s | 1 (6 failed, as intended) | `test_v3_scripts_against_shipped_scripts.log` |
| final | nine v3 test files; `tests/test_v3_scripts.py tests/test_frozen_hb_boundary.py`; whole suite | 00:4x | see §5 | 0 | `final_pytest_*.log` |

Background orchestration: chain A (seed-0 retrains + rollouts; `driver_chain_ts0_a.out`) and chain B (Imagenette seed 0, then seeds 1–2; `driver_chain_b.out`) were PowerShell scripts that call `drive_v3.py`. The CPU loops (`driver_cpu_loop_ts0.out`, `driver_cpu_loop_ts12.out`) repeated `drive_v3.py --phase commit` / `--phase sweep`. Other orchestration logs: `driver_backbones_ts0.out`, `driver_sweep_physionet_ts0.out`, `driver_sweep_cube_adult_ts0.out`, `driver_repair_batch{1,2}.out`, `driver_e9_g8.out`. At the stop condition (≈ 00:43; last CPU-loop line 00:41:25), chain B and both CPU loops were stopped (`Stop-Process`). Nothing beyond the job below was launched; seeds 1–2 never started.

**Running at session end:**
- **Job:** `drive_v3.py --phase rollouts --seeds 0 --datasets image:imagenette --policies greedy_entropy "--extra-args=--batch-size 16 --policy-amp"`. Driver PID 20216, rollout PID 29264, started 2026-10-02 00:19:48 local.
- **Rate:** latest progress line in `results_v3/logs/rollouts_image-imagenette_greedy_entropy_ts0.log` is `[rgb rollout] 496/5358 (2405s)` (01:04). 2405 s / 496 rows projects to ≈ 25,980 s ≈ 7.2 h, i.e. an expected end around 07:33 local. The GPU was at 210 MHz at 01:04 (`nvidia_smi_session_end.log`), so it may take longer.
- **Output:** `$RESULTS_ROOT\pool_v3\image-imagenette_ts0_greedy_entropy_softmax.npz`. The cache is written before the driver's final console line. The driver's parent (chain B) was stopped, so that final print may fail; if `run_log.jsonl` has no line for this cell, the cache file and its log are the record.
- **Check on return:** `python scripts/check_caches_v3.py` (the cache meta has `max_rows: None`, `policy_amp: true`, `batch_size: 16`).

**Round 2 ledger** (`results_v3/run_log.jsonl`, lines with start ≥ 2026-10-03 00:55 local: 81 runs). Background launches with their PIDs: `results_v3/logs/r2_background_jobs.log`.

| ledger cell prefix | runs | total seconds | non-zero rc |
|---|---|---|---|
| `r2hbfix:commit:` (Task A re-commits) | 7 | 12.7 | 0 |
| `r2hbfix:sweep:` (Task A, round-1 protocol, worktree at `5089d5e`) | 14 | 4,358.4 | 0 |
| `r2:commit:` (Tasks C, D) | 8 | 24.6 | 0 |
| `r2G8:commit:` | 1 | 3.6 | 0 |
| `r2:sweep:` (Tasks C, D; 16 cells) | 16 | 5,666.7 | 0 |
| `r2dw:sweep:` / `r2G8:sweep:` (E9) | 1 / 1 | 113.8 / 331.8 | 0 |
| `r2:repair:` (E7, via `run_repairs_v3.py`) | 11 | 2,319.2 | 0 |
| `r2am02:commit:` (Task E) | 8 | 24.5 | 2 (MNIST, Imagenette: rc 7, α ≤ design margin, by design) |
| `r2am02:sweep:` (Task E) | 12 | 4,660.8 | 0 |
| `rollouts:` (Imagenette seed 0 greedy / random) | 2 | 26,368.4 / 1,481.7 | 0 |

Run outside the ledger: the E7 BEFORE re-commits (`results_v3/logs/r2_commit_before_*`), the planted rerun (`results_v3/logs/r2_phase2_planted_validation.log`), table/figure/report scripts (`results_v3/logs/r2_*make_tables*.log`, `r2_final_make_figures.log`) and the checks in §12.

**Round 3 ledger** (`results_v3/run_log.jsonl`; prefixes `r3am10:commit:`, `r3:sweep:`, `r3am10:sweep:`, `r3cf025:sweep:`, `r3cf100:sweep:`): 72 runs, all with return code 0, between 13:27 and 14:07 local. The per-prefix table, the parallel lanes (`results_v3/logs/r3_background_jobs.log`), the two paused lanes and the runs outside the ledger are in §13.6. Nothing was launched on the GPU except the Task-L smoke (§13.5), whose outputs were deleted.

## 4. Code changes

Every change to `src/cafa/` or the Phase-3 scripts was followed by a rerun of the nine v3 test files and `tests/test_v3_scripts.py`. The 6 script tests were also run against the shipped (HEAD) scripts in a scratch copy, where all 6 failed, i.e. they detect the bugs they cover (`results_v3/logs/test_v3_scripts_against_shipped_scripts.log`). No frozen file was edited: `git diff 550f8e2 -- src/cafa/risk_control.py tests/test_risk_control.py tests/test_mondrian.py tests/test_baselines.py tests/test_pipeline.py` is empty.

| file (lines) | change | class / failure fixed | covering test | commit |
|---|---|---|---|---|
| 33 v3 files from `CAFA_v3_code.zip` | added unchanged | drop-in (the zip holds 33 files, not 38: 9 src + 12 scripts + 9 tests + 1 config + 2 docs) | — | `b1caf84` |
| `tests/conftest.py` (new) | put `src/` on `sys.path` | Environment: the nine v3 test files failed to collect in isolation (`ModuleNotFoundError: No module named 'cafa'`) | the nine v3 test files | `b1caf84` |
| `.gitignore` | +`set_env.ps1` | keep machine-specific roots out of git | — | `b1caf84` |
| `scripts/drive_v3.py` (new) | resumable driver (instruction §4.0); `--tag` for smoke runs; a commit waits for the caches of ALL policies | — (the last change prevents a one-time commit made before the random cache exists) | used for every Phase-1 cell and the Phase-3 main commits / sweeps (E7, E9 and the diagnostics ran outside it, §3) | `b1caf84`, `c4f0fcc`, `bd67b14` |
| `src/cafa/models_v3.py` 217–275 (`GreedyEntropyImagePolicy`) | `select_next` scores only the UNOBSERVED candidates (ascending order, so argmin and tie-breaking are unchanged); `cand_chunk` and `amp` arguments (also on `from_training_data`); `amp` = fp16 autocast for the hypothetical-reveal passes only | **Resource / v3 code bug**: the shipped loop ran ResNet-18 on all 49 patches every step → 2,401 candidate passes per row instead of the documented 1,225; shipped-code smoke 64 rows / 925.3 s → ≈ 21.5 h per cell (> 8 h) | `tests/test_models_v3.py::test_greedy_image_policy_matches_reference_and_counts_passes` (identical picks vs. the shipped implementation for cand_chunk 1/4/5/16/49; P(P+1)/2 passes per rollout) | `c4f0fcc` |
| `scripts/run_pool_rollout_v3.py` 24, 60, 79, 166–169, 216–217, 238–239 | flags `--policy-amp`, `--cand-chunk` (RGB greedy only); cache meta records `max_rows`, `batch_size`, `policy_amp`, `cand_chunk`; RGB progress shows elapsed seconds | Resource (instruction §5 allows fp16 autocast on the RGB rollout path) + provenance | `test_commit_refuses_partial_smoke_cache` | `c4f0fcc` |
| `scripts/run_cascade_sweep.py` 231–256, 282–286 | Mondrian-oracle record gets per-stratum test risks (abstained strata at full acquisition, as in its `test_risk`) and `stratum_violation`; cheapest-valid oracle gets `test_risk`, `test_cost`, `stratum_violation`; summary averages `stratum_violation` only over records that carry it | **v3 code bug (E6)**: Mondrian `stratum_violation_rate` was always 0.0; cheapest-valid oracle was dropped (n = 0) | `test_sweep_baseline_stratum_violation_recorded_and_summarised`, `test_sweep_keeps_cheapest_valid_oracle` | `c4f0fcc` |
| `scripts/run_cascade_sweep.py` 112–122 | refuse a `max_rows` cache, a cache whose `checkpoint_sha256` differs from the committed one, or a policy not in the commit | provenance guard | `test_sweep_refuses_stale_commit` | `c4f0fcc` |
| `scripts/commit_v3.py` 118–130 | refuse `max_rows` caches; every policy cache must match the greedy cache (shape, heldout digest, labels) | provenance guard | `test_commit_refuses_partial_smoke_cache` | `c4f0fcc` |
| `scripts/make_tables_v3.py` 50–53, `scripts/make_figures_v3.py` 35–37 | skip a cell lacking the requested `--scheme` (no fallback) | **v3 code bug**: `--scheme inverse_info` printed uniform-cost image rows under an `inverse_info` header | `test_make_tables_skips_missing_scheme` | `c4f0fcc` |
| `scripts/repair_experiment.py` 70, 80–81, 96–98, 115 | `--n-draws` default = `protocol_v3.n_draws` (100); report records n_draws, caches, commit, policy | **v3 code bug**: default was 50 draws (rule 5 fixes 100) | `test_repair_default_n_draws_is_protocol` | `c4f0fcc` |
| `tests/test_v3_scripts.py` (new) | 6 regression tests for the script fixes | — | itself | `c4f0fcc` |
| `tests/test_frozen_hb_boundary.py` (new) | documents the frozen-primitive defect; `xfail(strict=True)` | stop condition 5 (§9) | itself (1 passed, 1 xfailed) | final commit |
| `scripts/check_caches_v3.py`, `scripts/report_v3.py` (new) | Phase-1 acceptance summary (greedy = random; v2-vs-v3 same rows via labels and split digests); handoff tables generated from logs / caches / commits | — | — | `c4f0fcc`, `490b31a`, final commit |
| `scripts/diagnose_violation_v3.py`, `diagnose_refusal_v3.py`, `hb_boundary_draws_v3.py`, `split_balance_v3.py`, `calpool_vs_test_v3.py`, `cube_bayes_v3.py`, `scan_hb_ceil_boundary.py` (new) | independent diagnostics (§6.3, §8.5, §9) | — | — | `490b31a`, `dae7a0e`, final commit |
| `hpc/cells_v3.txt`, `hpc/rollout_v3.slurm`, `hpc/backbone_v3.slurm` (new) | TinyGPU array templates (§10) | — | — | `3069adc` |
| `S11_answer.md`, `.gitignore` (`CAFA.zip` line) | committed unchanged | pre-existing working-tree changes on `main` at session start; committed first so the branch starts clean | — | `8ddb7dc` |

Review method: before the first GPU run, a workflow ran five reviewers (one per file group: `models_v3`, `train_backbone_v3`, rollout, data loaders, Phase-3 scripts) and one adversarial verifier per reviewer's findings. Confirmed findings that were not fixed (they affect only the optional Phase 1d or are latent) are in §9.

Diff of the branch vs its base at the content commit (`git diff --stat 550f8e2 d66522b` restricted to code and docs, then per-directory totals and the overall shortstat):

```
 .gitignore                           |   6 +-
 PHASES_V3.md                         | 247 +++++++++++++++++++
 S11_answer.md                        | 852 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 V3_FILE_MANIFEST.md                  |  72 ++++++
 configs/experiment_v3.yaml           |  65 +++++
 hpc/backbone_v3.slurm                |  30 +++
 hpc/cells_v3.txt                     |  48 ++++
 hpc/rollout_v3.slurm                 |  34 +++
 scripts/afabench_export_orders.py    | 112 +++++++++
 scripts/calpool_vs_test_v3.py        |  48 ++++
 scripts/check_caches_v3.py           |  93 +++++++
 scripts/commit_v3.py                 | 235 ++++++++++++++++++
 scripts/cube_bayes_v3.py             |  49 ++++
 scripts/diagnose_refusal_v3.py       | 110 +++++++++
 scripts/diagnose_violation_v3.py     | 165 +++++++++++++
 scripts/download_data_v3.py          |  88 +++++++
 scripts/drive_v3.py                  | 154 ++++++++++++
 scripts/export_heldout_v3.py         |  57 +++++
 scripts/hb_boundary_draws_v3.py      | 117 +++++++++
 scripts/make_figures_v3.py           | 182 ++++++++++++++
 scripts/make_synthetic_pool_cache.py |  60 +++++
 scripts/make_tables_v3.py            | 105 ++++++++
 scripts/planted_validation.py        | 175 ++++++++++++++
 scripts/repair_experiment.py         | 138 +++++++++++
 scripts/report_v3.py                 | 111 +++++++++
 scripts/run_cascade_sweep.py         | 329 +++++++++++++++++++++++++
 scripts/run_pool_rollout_v3.py       | 253 ++++++++++++++++++++
 scripts/scan_hb_ceil_boundary.py     |  76 ++++++
 scripts/split_balance_v3.py          |  66 +++++
 scripts/train_backbone_v3.py         | 115 +++++++++
 src/cafa/cascade.py                  | 512 +++++++++++++++++++++++++++++++++++++++
 src/cafa/commit_rules.py             | 254 ++++++++++++++++++++
 src/cafa/data_v3.py                  | 292 ++++++++++++++++++++++
 src/cafa/external_orders.py          |  59 +++++
 src/cafa/hidden_risk.py              |  40 ++++
 src/cafa/localization.py             | 191 +++++++++++++++
 src/cafa/models_v3.py                | 345 ++++++++++++++++++++++++++
 src/cafa/splits_v3.py                |  75 ++++++
 src/cafa/synthetic_planted.py        | 164 +++++++++++++
 tests/conftest.py                    |  13 +
 tests/test_cascade.py                | 173 +++++++++++++
 tests/test_commit_rules.py           |  81 +++++++
 tests/test_data_v3.py                |  73 ++++++
 tests/test_external_orders.py        |  21 ++
 tests/test_frozen_hb_boundary.py     |  57 +++++
 tests/test_hidden_risk.py            |  10 +
 tests/test_localization.py           |  66 +++++
 tests/test_models_v3.py              | 115 +++++++++
 tests/test_planted.py                |  31 +++
 tests/test_splits_v3.py              |  35 +++
 tests/test_v3_scripts.py             | 129 ++++++++++
 51 files changed, 6927 insertions(+), 1 deletion(-)

per-directory share of changed files (git diff --cached --dirstat=files,0 550f8e2):
   4.5% configs/
   1.1% hpc/
   6.3% results_v3/diagnostics/
   1.5% results_v3/figures/
  42.4% results_v3/logs/
   0.7% results_v3/planted/
   3.3% results_v3/repair/
   3.0% results_v3/tables/
   3.0% results_v3/tables_e9_G8/
   3.0% results_v3/tables_e9_delta_weights/
   3.0% results_v3/tables_e9_lambda_ref_0.5/
   3.0% results_v3/tables_e9_lambda_ref_0.7/
   3.0% results_v3/tables_e9_lambda_ref_0.9/
   3.0% results_v3/tables_inverse_info/
   0.7% results_v3/
   8.2% scripts/
   3.3% src/cafa/
   4.5% tests/

results_v3/: 203 files (logs, tables, figures, planted, repair, diagnostics, run_log.jsonl); configs/committed_v3*: 11 files
total: 266 files changed, 73391 insertions(+), 1 deletion(-)
```

**Round 2** (details and covering tests in §12.1–12.6; commits `5089d5e` … the final commit):

| file | change | task / commit |
|---|---|---|
| `src/cafa/risk_control.py` (1 line) | HB boundary: `np.ceil(np.round(n * rb, 9))` | A, `5089d5e` |
| `tests/test_frozen_hb_boundary.py`, `CHANGELOG.md`, `scripts/scan_hb_ceil_boundary.py`, `scripts/compare_decisions_v3.py` | regression test, changelog, scan floor fix, decision-flip comparison | A, `5089d5e`, `3825b6c` |
| `scripts/drive_v3.py` | `--force`, `--metrics-dir-name`, `--commit-prefix`; dry run shows cells with missing prerequisites | A `5089d5e`, F `0d02588` |
| `configs/experiment_v3.yaml`, `src/cafa/splits_v3.py`, `scripts/commit_v3.py`, `scripts/run_cascade_sweep.py`, `scripts/repair_experiment.py`, `scripts/make_tables_v3.py`, `scripts/make_figures_v3.py`, `scripts/diagnose_violation_v3.py`, `scripts/planted_validation.py`, `scripts/check_sweep_equivalence_v3.py`, `tests/test_multisplit_v3.py`, `tests/fixtures/*`, `tests/test_v3_scripts.py` (draw counts) | multi-split protocol, noise-aware metrics, study D | B, `ac658f4`, `8e1858e` |
| `scripts/run_repairs_v3.py`, `scripts/report_violations_v3.py` | ledgered E7 runner; violation report | C, `799b214` |
| `scripts/commit_v3.py`, `tests/test_alpha_rule_v3.py` | `--alpha-margin` / `--alpha-grid`, `alpha_from_floor`, rc 7 | E, `00c2c4a`, `32fec67` |
| `hpc/README_v3.md`, `hpc/dry_run_v3.sh`, `hpc/{backbone,rollout}_v3.slurm`, `.gitattributes`, `.gitignore`, `scripts/run_pool_rollout_v3.py`, `scripts/export_heldout_v3.py`, `scripts/make_tables_v3.py` (seed table), `tests/test_hpc_v3.py` | cluster package, latent fixes | F, `0d02588`, `32fec67` |

**Round 3** (§13). There are no edits to `src/cafa/` or to frozen files: `git diff 16da5a0 -- src/` is empty.

`git diff --shortstat 16da5a0 95f9480 -- . ':!results_v3' ':!configs/committed_v3*'` (code, tests, hpc; before the handoff commit, which only adds README wording): 18 files, +3,317 / −65.

| file | change | task / commit |
|---|---|---|
| `scripts/run_cascade_sweep.py` | Two ex-post baselines, `oracle_stratum_safe` and `oracle_stratum_safe_mondrian`, computed once per (split, scheme) and selected per draw. Summary fields `feasible_rate`, `cascade_cost_over_oracle(_feasible)` and `cascade_cost_over_safe_mondrian_oracle`. `--cal-frac` (default = the commit's 0.5; non-default needs `--out-dir`; 1.0 = one draw per split; an empty draw is refused). Every round-2 field is unchanged (§13.4). | K, `2ffeb04` |
| `tests/test_oracles_v3.py` (new, 14 tests) | Cheapest safe λ on hand-made splits; infeasible → full acquisition (depth T, not the top grid column); Mondrian-safe ≤ common ≤ full; λ recomputed from the cache; `--cal-frac` guards and the one-draw-per-split rule | K, `2ffeb04` |
| `scripts/margin_analysis_v3.py` (new), `tests/test_margin_analysis_v3.py` (new, 26 tests) | E10 table, summary and F7; E11 table; sensitivity predictors (`_thr`, `_nk_calpool`, `_hyper`) | G / K2, `b85ac6a` |
| `scripts/make_tables_v3.py` | E4 cost / T, `tier2_would_certify`, `escalated_fraction` and safe-oracle columns; E6 `feasible_rate`; `TABLE_E4_cost_gap` (label, `label_note`, `n_needed`, feasible-draws ratio) | I / K, `b85ac6a`, `ecf553f` |
| `scripts/make_figures_v3.py` | F3 cost panel in cost / T with the E2 number under each bar; seed means with several seeds | I, `b85ac6a` |
| `scripts/alpha_margin_summary_v3.py` (new), `tests/test_reporting_v3.py` (new, 6 tests) | `TABLE_E9_alpha_margin`; tests of the E4/E6/cost-gap/F3/E9 reporting | H / I, `b85ac6a`, `ecf553f` |
| `scripts/train_backbone_v3.py`, `scripts/run_pool_rollout_v3.py`, `scripts/drive_v3.py`, `scripts/commit_v3.py` (`find_policy_caches` only), `scripts/check_caches_v3.py`, `scripts/run_repairs_v3.py`, `hpc/dry_run_v3.sh`, `hpc/README_v3.md` (§7, §8), `tests/test_checkpoint_tag_v3.py` (new, 12 tests), `tests/test_hpc_v3.py` | `--checkpoint-tag` (folder `checkpoints_v3_TAG`, cache token `{policy}-TAG`); `--width-mult` / `--p-full` overrides, which need a tag; tagged caches are ignored by commits and grouped by the cache check; `run_repairs_v3.py --repair-tag`; Task-L cluster lines | L, `5481269`, `95f9480` |

## 5. Phase 0 results

- Nine v3 test files at session start: they failed to collect (`ModuleNotFoundError: No module named 'cafa'`); after adding `tests/conftest.py`, before any code fix: `32 passed in 40.37s`, 0 skipped, so the 3 torch tests ran (console; the count is also in the `b1caf84` commit message). At the final state, with the added RGB-policy test: `33 passed in 50.91s` (`results_v3/logs/final_pytest_nine_v3.log`).
- New test files at the final state (`tests/test_v3_scripts.py tests/test_frozen_hb_boundary.py`): `7 passed, 1 xfailed in 20.65s` (`results_v3/logs/final_pytest_new_v3.log`).
- Whole suite `python -m pytest -q tests/`: session start `80 passed in 196.60s (0:03:16)` (`results_v3/logs/phase0_pytest_full_suite.log`); final state `88 passed, 1 xfailed in 242.20s (0:04:02)` (`results_v3/logs/final_pytest_full_suite.log`).
- Synthetic end-to-end (`--n 8000`, 20 draws; `results_v3/logs/phase0_synthetic_*.log`):

```
typeII:   [cascade] synthetic-planted ts0 greedy_entropy lr[dep]=0.495 G=3 | cert=0.85 tiers={'0': 0.15, '1': 0.0, '2': 0.0, '3': 0.85} viol=0.000 | deepest stratum verdict=type_II
          (lr 0.5: tiers '3'=0.9; lr 0.7 and 0.9: tiers '3'=1.0; all viol=0.000, all verdict=type_II)
feasible: [cascade] synthetic-planted ts0 greedy_entropy lr[dep]=0.455 G=3 | cert=1.00 tiers={'0': 0.0, '1': 1.0, '2': 0.0, '3': 0.0} viol=0.000 | deepest stratum verdict=feasible
          (lr 0.5 / 0.9: '1'=1.0; lr 0.7: '1'=0.95, '0'=0.05; all viol=0.000)
```

  Acceptance: Type II → `type_II` with tier 3 at 0.85–1.0 and `viol=0.000`: pass. Feasible → `'1': 1.0` at `dep`: pass. The synthetic cache, commit and metrics files and `results_v3/tables_smoke/` were deleted afterwards.

## 6. Phase 1 results

### 6.1 Data

| dataset | status | source / size |
|---|---|---|
| `csv:physionet` | downloaded | `F:\CAFA_data\afabench\physionet.csv` (4.1 MB; AFABench `main` raw URL); heldout 4,800 rows |
| `csv:diabetes` | downloaded | `F:\CAFA_data\afabench\diabetes.csv` (54.9 MB); heldout 36,825 |
| `mnist` | present (copied) | `F:\CAFA_data\MNIST\raw`; heldout 28,000 |
| `fashionmnist` | downloaded | `F:\CAFA_data\FashionMNIST\raw`; heldout 28,000 |
| `tabular:MiniBooNE` | OpenML cache | `n_train=78038 d=50` (`phase1a_download_small.log`); heldout 52,026 |
| `tabular:adult` | OpenML cache | `n_train=27133 d=14`; heldout 18,089 (rows with missing values are dropped by the v2 loader) |
| `image:imagenette` | downloaded + cached | `imagenette2-320.tgz` → `imagenette_cache/imagenette_224.npz`, 13,394 images at 224 px |
| `cube` | generated | heldout 8,000 |

### 6.2 Smoke runs (all smoke checkpoints/caches deleted at 13:52)

| smoke cell | flags | seconds | console |
|---|---|---|---|
| backbone `csv:physionet` | `--epochs 1 --max-train 2000` | 16.5 | `masked_acc=0.8215 full_obs_acc=0.8445` |
| rollout `csv:physionet` greedy / random | `--max-rows 256` | 11.5 / 13.3 | `full-acq acc=0.8359` both (`smoke_rollouts_csv-physionet_*_ts0.log`; a `check_caches_v3.py` run on the smoke caches printed diff 0.000e+00, PASS — console only) |
| backbone `mnist` | `--epochs 1 --max-train 2000` | 22.6 | `masked_acc=0.1585 full_obs_acc=0.1135` (8 optimizer steps) |
| rollout `mnist` greedy | `--max-rows 256` | 99.9 | `full-acq acc=0.1094` |
| backbone `image:imagenette` | `--epochs 1 --max-train 512` | 77.6 | `masked_acc=0.4238 full_obs_acc=0.8125` |
| rollout `image:imagenette` greedy, shipped policy | `--max-rows 64 --batch-size 16` | 925.3 | `full-acq acc=0.8438` |
| rollout `image:imagenette` greedy, fixed policy fp32 | `--max-rows 32 --batch-size 16` | 174.2 | `[rgb rollout] 16/32 (43s)`, `full-acq acc=0.8125` |
| rollout `image:imagenette` greedy, fixed policy `--policy-amp` | `--max-rows 32 --batch-size 16 --policy-amp` | 126.7 | `[rgb rollout] 16/32 (34s)`, `full-acq acc=0.8125` |

Fixed-policy fp32 vs `--policy-amp` on the same 32 rows: first-step picks identical (32/32), 76.1 % of all picks identical, 11/32 rows with an identical full order; `correct[:, T]` identical and max |Δ score at T| = 0.0 (scoring passes stay fp32). These figures are console-only: they were computed from the two smoke caches, which were then deleted as instruction §4.2 requires. Both smoke logs print `full-acq acc=0.8125`.

**Imagenette decision (instruction §6).**
- **Shipped code:** 925.3 s / 64 rows → ≈ 21.5 h per 5,358-row cell (> 8 h).
- **Fixed policy + `--policy-amp`:** 126.7 s / 32 rows including data loading → ≈ 5.9 h (per-batch rate 34 s / 16 rows → ≈ 3.2 h).
- **Decision:** run seed-0 greedy (`--batch-size 16 --policy-amp`) and random (`--batch-size 16`, the same batch size so the depth-T scoring passes are batched identically) as the last seed-0 GPU jobs.
- **Measured afterwards:** MNIST greedy took 15,491.9 s, against its smoke extrapolation of 99.9 s / 256 rows × 28,000 = 10,927 s, i.e. 1.42× slower because of sustained throttling. Applied to Imagenette, the same factor gives ≈ 8.4 h on the total-time basis (5.9 h × 1.42) and ≈ 4.5 h on the per-batch basis. The in-run rate at session end projects ≈ 7.2 h (§3). The go decision was taken on the smoke estimate, as instruction §6 prescribes.

### 6.3 Real runs (seed 0)

Backbones (`python scripts/report_v3.py --backbones`). Full-observation accuracy is measured on the first 5,000 train rows (tabular), 2,000 (patches) or 512 (RGB):

| cell | epochs | masked train acc | full-obs train acc | target | pass | seconds | log |
|---|---|---|---|---|---|---|---|
| backbones:csv:physionet:na:ts0 | config | 0.8706 | 0.8936 | 0.86 | pass | 30.7 | `results_v3\logs\backbones_csv-physionet_na_ts0.log` |
| backbones:cube:na:ts0 | config | 0.6450 | 0.9524 | 0.98 | miss | 24.3 | `results_v3\logs\backbones_cube_na_ts0.log` |
| backbones:tabular:adult:na:ts0 | config | 0.8161 | 0.8626 | 0.85 | pass | 56.7 | `results_v3\logs\backbones_tabular-adult_na_ts0.log` |
| backbones:csv:diabetes:na:ts0 | config | 0.8651 | 0.9094 | 0.85 | pass | 195.3 | `results_v3\logs\backbones_csv-diabetes_na_ts0.log` |
| backbones:tabular:MiniBooNE:na:ts0 | config | 0.8625 | 0.9146 | 0.93 | miss | 280.3 | `results_v3\logs\backbones_tabular-MiniBooNE_na_ts0.log` |
| backbones:mnist:na:ts0 | config | 0.9093 | 0.9995 | 0.995 | pass | 1533.4 | `results_v3\logs\backbones_mnist_na_ts0.log` |
| backbones:fashionmnist:na:ts0 | config | 0.8930 | 0.9755 | 0.93 | pass | 1602.9 | `results_v3\logs\backbones_fashionmnist_na_ts0.log` |
| retrain60:backbones:cube:na:ts0 | 60 | 0.6532 | 0.9598 | 0.98 | miss | 49.8 | `results_v3\logs\retrain60_backbones_cube_na_ts0.log` |
| retrain60:backbones:tabular:MiniBooNE:na:ts0 | 60 | 0.8684 | 0.9158 | 0.93 | miss | 379.6 | `results_v3\logs\retrain60_backbones_tabular-MiniBooNE_na_ts0.log` |
| backbones:image:imagenette:na:ts0 | config | 0.9375 | 1.0000 | 0.95 | pass | 1067.0 | `results_v3\logs\backbones_image-imagenette_na_ts0.log` |

Acceptance misses (instruction §4.2: raise the epochs once, then keep the result and report it):
- **Retrain:** CUBE and MiniBooNE were retrained once with `--epochs 60`, a CLI override for those two datasets only (`training_v3.tabular.epochs: 40` is unchanged, so the passing tabular cells are untouched). Both still miss; the 60-epoch checkpoints are the ones used. The 40-epoch checkpoints are kept at `$RESULTS_ROOT\checkpoints_v3_superseded\{cube,tabular-MiniBooNE}_ts0_ep40.pt`.
- **CUBE:** the exact Bayes classifier of `generate_cube(20000, 123)` has accuracy 0.97025, below the 0.98 target (`results_v3/diagnostics/cube_bayes_accuracy.json`).
- **MiniBooNE:** heldout full-acquisition accuracy is 0.922558 for v3 vs 0.915831 for the v2 AAAI backbone.
- **Seeds 1–2 (not run):** the plan was the 60-epoch protocol for CUBE and MiniBooNE and the config defaults for the rest (§10).

Pool caches (`python scripts/report_v3.py --caches`; `check_caches_v3.py` PASS for all 7 datasets: `results_v3/logs/phase1_check_caches_v3.log`, `results_v3/phase1_caches.csv`):

| dataset | seed | policy | n | T | heldout full-acq acc | rollout seconds | greedy = random (1e-12) | cache |
|---|---|---|---|---|---|---|---|---|
| csv-diabetes | 0 | greedy_entropy | 36825 | 45 | 0.903870 | 487.8 |  | `pool_v3/csv-diabetes_ts0_greedy_entropy_softmax.npz` |
| csv-diabetes | 0 | random | 36825 | 45 | 0.903870 | 28.0 | yes | `pool_v3/csv-diabetes_ts0_random_softmax.npz` |
| csv-physionet | 0 | greedy_entropy | 4800 | 41 | 0.873333 | 44.6 |  | `pool_v3/csv-physionet_ts0_greedy_entropy_softmax.npz` |
| csv-physionet | 0 | random | 4800 | 41 | 0.873333 | 6.3 | yes | `pool_v3/csv-physionet_ts0_random_softmax.npz` |
| cube | 0 | greedy_entropy | 8000 | 20 | 0.953125 | 13.1 |  | `pool_v3/cube_ts0_greedy_entropy_softmax.npz` |
| cube | 0 | random | 8000 | 20 | 0.953125 | 6.2 | yes | `pool_v3/cube_ts0_random_softmax.npz` |
| fashionmnist | 0 | greedy_entropy | 28000 | 49 | 0.941286 | 14565.1 |  | `pool_v3/fashionmnist_ts0_greedy_entropy_softmax.npz` |
| fashionmnist | 0 | random | 28000 | 49 | 0.941286 | 308.2 | yes | `pool_v3/fashionmnist_ts0_random_softmax.npz` |
| mnist | 0 | greedy_entropy | 28000 | 49 | 0.994893 | 15491.9 |  | `pool_v3/mnist_ts0_greedy_entropy_softmax.npz` |
| mnist | 0 | random | 28000 | 49 | 0.994893 | 389.9 | yes | `pool_v3/mnist_ts0_random_softmax.npz` |
| tabular-MiniBooNE | 0 | greedy_entropy | 52026 | 50 | 0.922558 | 869.8 |  | `pool_v3/tabular-MiniBooNE_ts0_greedy_entropy_softmax.npz` |
| tabular-MiniBooNE | 0 | random | 52026 | 50 | 0.922558 | 42.1 | yes | `pool_v3/tabular-MiniBooNE_ts0_random_softmax.npz` |
| tabular-adult | 0 | greedy_entropy | 18089 | 14 | 0.852507 | 27.7 |  | `pool_v3/tabular-adult_ts0_greedy_entropy_softmax.npz` |
| tabular-adult | 0 | random | 18089 | 14 | 0.852507 | 19.2 | yes | `pool_v3/tabular-adult_ts0_random_softmax.npz` |
| image-imagenette | 0 | greedy_entropy | 5358 | 49 | 0.971818 | 26368.4 (round 2, §12.4) |  | `pool_v3/image-imagenette_ts0_greedy_entropy_softmax.npz` |
| image-imagenette | 0 | random | 5358 | 49 | 0.971818 | 1481.7 (round 2) | yes | `pool_v3/image-imagenette_ts0_random_softmax.npz` |

**v2 "before" caches for E7: present, not regenerated.** `$RESULTS_ROOT\pool_v2\{mnist,tabular-MiniBooNE,tabular-adult}_ts0_greedy_entropy_softmax.npz` were produced on TinyGPU (`cafa_pool_rollout.o1735175` etc., `created` 2026-07-11) and copied from the repo's git-ignored `results/pool_v2/`.
- **Provenance:** their `checkpoint_sha256` equals the sha256 of `$RESULTS_ROOT\checkpoints_v2\*_ts0.pt` (e3d3c21f13fb / 3e05a708c0de / ed66f5dd5f2a).
- **Same rows:** `check_caches_v3.py --v2-dir` finds, for v2 and v3, the same n, the same label vector in the same order, and identical `split_digest` (sha256 of the train / probe / eval index sets) in the cache meta: MNIST 28,000, MiniBooNE 52,026, Adult 18,089 (`results_v3/logs/phase1_check_caches_v3.log`).
- **v2 full-acquisition accuracy:** MNIST 0.899214, MiniBooNE 0.915831, Adult 0.852286.

## 7. Phase 2 results

**Round 2 rerun** (HB fix; study D added): `python scripts/planted_validation.py --output-dir results_v3/planted --n-replicates 1000` on CPU, 2026-10-03 02:00:23 → 03:32 local (background job, `results_v3/logs/r2_background_jobs.log`; log `results_v3/logs/r2_phase2_planted_validation.log`). Studies A–C: 1,000 replicates per row (as round 1); study D: 10 blocks × 20 replicates per configuration. The round-1 files are in `results_v3/round1/planted/`. Against round 1, the fix changes 7 study-A/C fields (cascade certification in study A at margin −0.03 and n_k 1000: 0.747 → 0.750; escalation rate at n_k 250: 0.866 → 0.881 for all three Δ; at n_k 500: 0.996 → 0.997 (Δ 0.03), 0.997 → 0.998 (Δ 0.05, 0.10)). It leaves every false-failure, violation and power value unchanged. `results_v3/planted/PLANTED_VALIDATION.md`, verbatim:

```
# Planted validation (E5)

alpha=0.15, delta=0.1, gamma=0.05, T=30, replicates=1000, M=131

| study | n_k | margin | false-failure (<= gamma) | cascade viol (<= delta) | power | n_k Delta^2 | sufficient n_k | escalation rate |
|---|---|---|---|---|---|---|---|---|
| A_level | 250 | -0.030 | 0.000 | 0.000 |  |  |  |  |
| A_level | 500 | -0.030 | 0.000 | 0.000 |  |  |  |  |
| A_level | 1000 | -0.030 | 0.000 | 0.000 |  |  |  |  |
| A_level | 2000 | -0.030 | 0.000 | 0.000 |  |  |  |  |
| A_level | 4000 | -0.030 | 0.000 | 0.005 |  |  |  |  |
| A_level | 250 | -0.050 | 0.000 | 0.000 |  |  |  |  |
| A_level | 500 | -0.050 | 0.000 | 0.000 |  |  |  |  |
| A_level | 1000 | -0.050 | 0.000 | 0.002 |  |  |  |  |
| A_level | 2000 | -0.050 | 0.000 | 0.004 |  |  |  |  |
| A_level | 4000 | -0.050 | 0.000 | 0.003 |  |  |  |  |
| B_power_C_route | 250 | 0.030 |  | 0.000 | 0.000 | 0.23 | 12075 | 0.881 |
| B_power_C_route | 500 | 0.030 |  | 0.000 | 0.001 | 0.45 | 12075 | 0.997 |
| B_power_C_route | 1000 | 0.030 |  | 0.000 | 0.108 | 0.90 | 12075 | 1.000 |
| B_power_C_route | 2000 | 0.030 |  | 0.000 | 0.743 | 1.80 | 12075 | 1.000 |
| B_power_C_route | 4000 | 0.030 |  | 0.000 | 0.994 | 3.60 | 12075 | 1.000 |
| B_power_C_route | 250 | 0.050 |  | 0.000 | 0.009 | 0.63 | 4347 | 0.881 |
| B_power_C_route | 500 | 0.050 |  | 0.000 | 0.273 | 1.25 | 4347 | 0.998 |
| B_power_C_route | 1000 | 0.050 |  | 0.000 | 0.926 | 2.50 | 4347 | 1.000 |
| B_power_C_route | 2000 | 0.050 |  | 0.000 | 1.000 | 5.00 | 4347 | 1.000 |
| B_power_C_route | 4000 | 0.050 |  | 0.000 | 1.000 | 10.00 | 4347 | 1.000 |
| B_power_C_route | 250 | 0.100 |  | 0.000 | 0.843 | 2.50 | 1087 | 0.881 |
| B_power_C_route | 500 | 0.100 |  | 0.000 | 0.999 | 5.00 | 1087 | 0.998 |
| B_power_C_route | 1000 | 0.100 |  | 0.000 | 1.000 | 10.00 | 1087 | 1.000 |
| B_power_C_route | 2000 | 0.100 |  | 0.000 | 1.000 | 20.00 | 1087 | 1.000 |
| B_power_C_route | 4000 | 0.100 |  | 0.000 | 1.000 | 40.00 | 1087 | 1.000 |

## Study D -- test noise (round 2)

Deepest stratum: TRUE full-information risk alpha - 0.004 = 0.1460 (homogeneous; exact by beta quadrature). Blocks of 20 replicates share one test split; certified violation = exact one-sided binomial p <= 0.05 on the test split. Expected rates: noise-free, from the deployed rules' true risks and the test n_k.

| config | n_k cal | n_k test | blocks x draws | cert rate | true viol (<= delta) | raw test viol | raw by block (min-max) | expected raw | certified viol (<= delta + 0.05) | expected certified | mean max_excess_se | deployed true deepest risk (min-max) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | 1250 | 2492 | 10 x 20 | 0.055 | 0.000 | 0.020 | 0.00-0.15 | 0.016 | 0.000 | 0.001 | -0.589 | 0.146-0.146 |
| D2 | 89984 | 2492 | 10 x 20 | 0.880 | 0.000 | 0.235 | 0.00-0.55 | 0.269 | 0.005 | 0.013 | -0.661 | 0.146-0.149 |
```

`unsafe|esc` is printed only on the console: `0.000` in all 15 study-B/C rows (`results_v3/logs/r2_phase2_planted_validation.log`).

| acceptance check (instruction §4.3, round 2 §B) | observed | verdict |
|---|---|---|
| false-failure ≤ 0.05 everywhere | max 0.000 | pass |
| cascade violation ≤ 0.10 | max 0.005 (study A, margin -0.03, n_k 4000) | pass |
| power increasing in n_kΔ² (≈ 0.9 at 2.5, 1.0 at ≥ 10) | monotone within each Δ; 0.926 (Δ 0.05) and 0.843 (Δ 0.10) at 2.5; 1.000 at ≥ 10 | pass |
| escalation `unsafe|esc` ≈ 0 | 0.000 everywhere | pass |
| study D: true violation ≤ δ | D1 0.000, D2 0.000 | pass |
| study D: raw test violation (expected > δ) | D1 0.020 (the cascade certifies in 5.5 % of D1 replicates only); D2 0.235 (per block 0.00–0.55; noise-free expectation 0.269) | D2: > δ as expected; D1: ≤ δ |
| study D: certified violation ≤ δ + 0.05 | D1 0.000, D2 0.005 (expected 0.013) | pass |

## 8. Phase 3 results (round 2: seed 0, 16 cells, 5 splits × 20 draws; seeds 1–2 `TBD-RUN` (cluster, §10))

All round-2 metrics JSONs are at `$RESULTS_ROOT\metrics_v3\{dsname}_ts0_{policy}_softmax.json`: 100 draws = 5 calibration/test splits (test seeds 778–782) × 20 draws, HB boundary fix in place (§12). Tables: `make_tables_v3.py --lambda-ref-key dep --scheme uniform` → `results_v3/tables/`; `--scheme inverse_info` → `results_v3/tables_inverse_info/` (tabular cells only; image cells have uniform costs). The round-1 versions of every table, figure and repair file are in `results_v3/round1/` (HB defect present, single split; superseded).

Column meanings added in round 2: `violation_by_split` = min–max over the 5 splits of the raw test stratum-violation rate; `certified_violation` = share of the 100 draws in which some K_cal stratum's exact one-sided binomial test-split p-value (H0: R_k ≤ α) is ≤ 0.05; `max_excess_se` = mean over draws of max_k (R̂_test,k − α)/√(α(1−α)/n_k); `verdict_agreement` = splits whose deepest-stratum audit verdict equals split 778's.

### 8.1 TABLE_E4_cascade (headline)

| dataset | policy | seed | alpha | G | lambda_ref | marginal_cost | tier1 | tier2 | tier3 | none | certified_deployment | deployed_cost | cost_premium | answered_fraction | test_stratum_violation | violation_by_split | certified_violation | max_excess_se | delta | deepest_verdict | verdict_agreement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 0.150 | 2 | 0.798 | 6.915 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 45.000 | 6.507 | 0.817 | 0.000 | 0.000–0.000 | 0.000 | -3.877 | 0.100 | type_II | 5/5 |
| csv-diabetes | random | 0 | 0.150 | 4 | 0.828 | 11.211 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 45.000 | 4.014 | 0.892 | 0.000 | 0.000–0.000 | 0.000 | -3.937 | 0.100 | type_II | 5/5 |
| csv-physionet | greedy_entropy | 0 | 0.200 | 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000–0.000 | 0.000 | -6.616 | 0.100 | feasible | 5/5 |
| csv-physionet | random | 0 | 0.200 | 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |  | 1.000 | 0.000 | 0.000–0.000 | 0.000 | -6.616 | 0.100 | feasible | 5/5 |
| cube | greedy_entropy | 0 | 0.150 | 3 | 0.798 | 4.183 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 5.786 | 1.383 | 1.000 | 0.010 | 0.000–0.050 | 0.000 | -3.368 | 0.100 | feasible | 5/5 |
| cube | random | 0 | 0.150 | 4 | 0.707 | 9.917 | 0.990 | 0.000 | 0.010 | 0.000 | 1.000 | 11.527 | 1.162 | 1.000 | 0.000 | 0.000–0.000 | 0.000 | -3.338 | 0.100 | feasible | 5/5 |
| fashionmnist | greedy_entropy | 0 | 0.150 | 5 | 0.778 | 5.388 | 0.120 | 0.000 | 0.880 | 0.000 | 1.000 | 45.544 | 8.453 | 0.982 | 0.100 | 0.000–0.450 | 0.000 | -4.109 | 0.100 | feasible | 5/5 |
| fashionmnist | random | 0 | 0.150 | 5 | 0.778 | 7.919 | 0.120 | 0.000 | 0.880 | 0.000 | 1.000 | 45.367 | 5.729 | 0.985 | 0.100 | 0.000–0.500 | 0.010 | -3.966 | 0.100 | feasible | 5/5 |
| image-imagenette | greedy_entropy | 0 | 0.100 | 4 | 0.859 | 8.043 | 0.200 | 0.000 | 0.800 | 0.000 | 1.000 | 43.315 | 5.385 | 0.983 | 0.050 | 0.000–0.150 | 0.000 | -3.152 | 0.100 | feasible | 5/5 |
| image-imagenette | random | 0 | 0.100 | 4 | 0.838 | 7.587 | 0.090 | 0.000 | 0.910 | 0.000 | 1.000 | 46.072 | 6.072 | 0.963 | 0.000 | 0.000–0.000 | 0.000 | -3.604 | 0.100 | feasible | 5/5 |
| mnist | greedy_entropy | 0 | 0.100 | 3 | 0.788 | 3.497 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 3.657 | 1.046 | 1.000 | 0.000 | 0.000–0.000 | 0.000 | -3.514 | 0.100 | feasible | 5/5 |
| mnist | random | 0 | 0.100 | 5 | 0.788 | 8.286 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 8.994 | 1.085 | 1.000 | 0.000 | 0.000–0.000 | 0.000 | -3.759 | 0.100 | feasible | 5/5 |
| tabular-adult | greedy_entropy | 0 | 0.250 | 2 | 0.758 | 2.382 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 2.985 | 1.253 | 1.000 | 0.010 | 0.000–0.050 | 0.000 | -3.812 | 0.100 | feasible | 5/5 |
| tabular-adult | random | 0 | 0.250 | 3 | 0.758 | 3.461 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 | 14.000 | 4.045 | 0.902 | 0.020 | 0.000–0.100 | 0.000 | -3.273 | 0.100 | unresolved | 2/5 |
| tabular-MiniBooNE | greedy_entropy | 0 | 0.150 | 3 | 0.747 | 3.070 | 0.010 | 0.000 | 0.990 | 0.000 | 1.000 | 49.653 | 16.174 | 0.965 | 0.020 | 0.000–0.100 | 0.010 | -4.055 | 0.100 | feasible | 2/5 |
| tabular-MiniBooNE | random | 0 | 0.150 | 4 | 0.778 | 7.741 | 0.260 | 0.000 | 0.740 | 0.000 | 1.000 | 43.097 | 5.567 | 0.985 | 0.030 | 0.000–0.150 | 0.000 | -4.613 | 0.100 | feasible | 5/5 |

Acceptance (instruction_round2 Task C, applied to all 16 cells):
- **Certified deployment ≈ 1.00:** 1.000 in all 16 cells (pass).
- **Certified violation ≤ δ + 0.05 = 0.15:** max 0.010 (FashionMNIST random, MiniBooNE greedy); 0.000 in the other 14 cells, Imagenette included (pass in every cell).
- **Mean `max_excess_se` ≤ 0:** negative in all 16 cells, from −6.616 (PhysioNet) to −3.152 (Imagenette greedy) (pass in every cell; no cell needs its `by_split` range listed for this criterion).
- **Raw `test_stratum_violation`** (reported, no threshold): pooled ≤ 0.100 in all 16 cells; per split up to 0.450 (FashionMNIST greedy) and 0.500 (FashionMNIST random), both on split 778; Imagenette greedy 0.050 pooled (by split 0.000 / 0.000 / 0.000 / 0.100 / 0.150), Imagenette random 0.000 (§8.5).
- **Tier pattern at `dep`:** tier 1 ≥ 0.99 on MNIST (1.00 / 1.00), CUBE (1.00 / 0.99), Adult greedy (1.00) and PhysioNet (1.00 / 1.00); tier 3 is the majority on Diabetes (1.00 / 1.00), Adult random (1.00), MiniBooNE greedy (0.99), Imagenette (0.80 greedy / 0.91 random; tier 1 0.20 / 0.09), FashionMNIST (0.88 / 0.88) and MiniBooNE random (0.74). The instruction-§4.4 expectation "tier 1 dominant on MNIST / FashionMNIST / Imagenette / MiniBooNE / CUBE" is met for MNIST and CUBE only. Cost premium in the tier-1 cells: MNIST 1.046 / 1.085, CUBE 1.383 / 1.162, Adult greedy 1.253; Imagenette 5.385 / 6.072.
- **PhysioNet:** α = 0.20 makes the `dep` target degenerate (λ_ref = 0, G = 1, tier 1 at zero acquisition cost); kept as is and moved to the appendix (author decision, round 2 §0; α-rule sensitivity in §8.7).
- **Changes against round 1** (HB fix + 5 splits; the 14 cells common to both rounds; `old → new` in §11 and `results_v3/diagnostics/r2_old_vs_new_dep.md`): tier-1 share FashionMNIST 0.35 → 0.12 (greedy) and 0.58 → 0.12 (random), MiniBooNE 0.04 → 0.01 (greedy) and 0.73 → 0.26 (random); raw violation FashionMNIST 0.350 → 0.100 and 0.580 → 0.100, MiniBooNE 0.110 → 0.020 and 0.120 → 0.030; all other cells change by ≤ 0.02 in tier shares and raw violation. Imagenette is new in round 2 (Task D).

**Round-3 columns of TABLE_E4_cascade** (Tasks I and K, §13.3–13.4; same file, appended columns; the round-2 columns above are unchanged, `results_v3/logs/r3_table_invariance.log`):

| dataset | policy | tier1 | tier2 | tier3 | deployed_cost_over_T | marginal_cost_over_T | mondrian_cost_over_T | tier2_would_certify | escalated_fraction | oracle_safe_cost_over_T | oracle_safe_feasible_rate | cascade_over_safe_oracle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0.000 | 0.000 | 1.000 | 1.000 | 0.154 | 0.259 | 0.000 | 0.183 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0.000 | 0.000 | 1.000 | 1.000 | 0.249 | 0.235 | 0.000 | 0.108 | 1.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |  |
| csv-physionet | random | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |  |
| cube | greedy_entropy | 1.000 | 0.000 | 0.000 | 0.289 | 0.209 | 0.248 | 0.000 | 0.000 | 0.229 | 1.000 | 1.264 |
| cube | random | 0.990 | 0.000 | 0.010 | 0.576 | 0.496 | 0.548 | 0.000 | 0.000 | 0.518 | 1.000 | 1.112 |
| fashionmnist | greedy_entropy | 0.120 | 0.000 | 0.880 | 0.929 | 0.110 | 0.262 | 0.000 | 0.018 | 0.423 | 0.800 | 2.197 |
| fashionmnist | random | 0.120 | 0.000 | 0.880 | 0.926 | 0.162 | 0.294 | 0.000 | 0.015 | 0.464 | 0.800 | 1.995 |
| image-imagenette | greedy_entropy | 0.200 | 0.000 | 0.800 | 0.884 | 0.164 | 0.295 | 0.000 | 0.017 | 0.232 | 1.000 | 3.806 |
| image-imagenette | random | 0.090 | 0.000 | 0.910 | 0.940 | 0.155 | 0.285 | 0.000 | 0.037 | 0.189 | 1.000 | 4.974 |
| mnist | greedy_entropy | 1.000 | 0.000 | 0.000 | 0.075 | 0.071 | 0.074 | 0.000 | 0.000 | 0.072 | 1.000 | 1.041 |
| mnist | random | 1.000 | 0.000 | 0.000 | 0.184 | 0.169 | 0.178 | 0.000 | 0.000 | 0.168 | 1.000 | 1.092 |
| tabular-adult | greedy_entropy | 1.000 | 0.000 | 0.000 | 0.213 | 0.170 | 0.151 | 0.000 | 0.000 | 0.198 | 1.000 | 1.079 |
| tabular-adult | random | 0.000 | 0.000 | 1.000 | 1.000 | 0.247 | 0.255 | 0.000 | 0.098 | 0.856 | 0.200 | 1.169 |
| tabular-MiniBooNE | greedy_entropy | 0.010 | 0.000 | 0.990 | 0.993 | 0.061 | 0.303 | 0.000 | 0.035 | 0.745 | 0.400 | 1.333 |
| tabular-MiniBooNE | random | 0.260 | 0.000 | 0.740 | 0.862 | 0.155 | 0.255 | 0.000 | 0.015 | 0.230 | 1.000 | 3.743 |

### 8.2 TABLE_E3_audit (deepest stratum; audit of record = split 778's calibration pool)

| dataset | policy | seed | k | n_k | alpha | rmin_thr | rmin_depth | r_full | p_thr | p_depth | verdict | all_verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 1 | 4289 | 0.150 | 0.329 | 0.327 | 0.333 | 0.000 | 0.000 | type_II | 0:feasible 1:type_II |
| csv-diabetes | random | 0 | 3 | 3305 | 0.150 | 0.241 | 0.241 | 0.241 | 0.000 | 0.000 | type_II | 0:feasible 1:feasible 2:feasible 3:type_II |
| csv-physionet | greedy_entropy | 0 | 0 | 2160 | 0.200 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible |
| csv-physionet | random | 0 | 0 | 2160 | 0.200 | 0.126 | 0.126 | 0.126 | 1.000 | 1.000 | feasible | 0:feasible |
| cube | greedy_entropy | 0 | 2 | 1230 | 0.150 | 0.080 | 0.080 | 0.080 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| cube | random | 0 | 3 | 714 | 0.150 | 0.080 | 0.083 | 0.083 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| fashionmnist | greedy_entropy | 0 | 4 | 2640 | 0.150 | 0.133 | 0.133 | 0.133 | 0.995 | 0.995 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| fashionmnist | random | 0 | 4 | 2852 | 0.150 | 0.129 | 0.126 | 0.129 | 0.999 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| image-imagenette | greedy_entropy | 0 | 3 | 498 | 0.100 | 0.078 | 0.076 | 0.078 | 0.958 | 0.971 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| image-imagenette | random | 0 | 3 | 496 | 0.100 | 0.083 | 0.083 | 0.083 | 0.916 | 0.916 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |
| mnist | greedy_entropy | 0 | 2 | 4794 | 0.100 | 0.008 | 0.008 | 0.008 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible |
| mnist | random | 0 | 4 | 2826 | 0.100 | 0.012 | 0.012 | 0.012 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible 4:feasible |
| tabular-adult | greedy_entropy | 0 | 1 | 1788 | 0.250 | 0.196 | 0.196 | 0.196 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible |
| tabular-adult | random | 0 | 2 | 1860 | 0.250 | 0.254 | 0.253 | 0.254 | 0.343 | 0.403 | unresolved | 0:feasible 1:feasible 2:unresolved |
| tabular-MiniBooNE | greedy_entropy | 0 | 2 | 6883 | 0.150 | 0.144 | 0.146 | 0.146 | 0.932 | 0.852 | feasible | 0:feasible 1:feasible 2:feasible |
| tabular-MiniBooNE | random | 0 | 3 | 4635 | 0.150 | 0.132 | 0.132 | 0.132 | 1.000 | 1.000 | feasible | 0:feasible 1:feasible 2:feasible 3:feasible |

`verdict_agreement` (§8.1) is 5/5 in 14 cells, Imagenette included (deepest stratum k = 3, n_k 498 / 496 on split 778's calibration pool, `feasible` on every split). The two exceptions sit at α: MiniBooNE greedy (`dep`, deepest stratum k = 2) is `feasible` on splits 778 and 782, `unresolved` on 779 and 781 and `type_II` on 780; Adult random (`dep`, k = 2) is `unresolved` on 778 and 782 and `feasible` on 779–781 (`results_v3/logs/r2_taskC_facts.log`, from `deepest_verdict_by_split` in the metrics JSONs). At λ_ref 0.9 both cells are `type_II` on all 5 splits.

### 8.3 TABLE_E2_blindness

| dataset | policy | seed | alpha | marginal_test_risk | marginal_aggregate_violation | max_stratum_over_alpha | hidden_stratum_violation_rate | hidden_certified_violation_rate |
|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | 0.150 | 0.099 | 0.000 | 2.198 | 1.000 | 1.000 |
| csv-diabetes | random | 0 | 0.150 | 0.143 | 0.010 | 1.730 | 1.000 | 1.000 |
| csv-physionet | greedy_entropy | 0 | 0.200 | 0.143 | 0.000 | 0.715 | 0.000 | 0.000 |
| csv-physionet | random | 0 | 0.200 | 0.143 | 0.000 | 0.715 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | 0.150 | 0.133 | 0.010 | 1.095 | 0.910 | 0.320 |
| cube | random | 0 | 0.150 | 0.136 | 0.070 | 1.109 | 0.930 | 0.500 |
| fashionmnist | greedy_entropy | 0 | 0.150 | 0.137 | 0.000 | 1.533 | 1.000 | 1.000 |
| fashionmnist | random | 0 | 0.150 | 0.139 | 0.000 | 1.438 | 1.000 | 1.000 |
| image-imagenette | greedy_entropy | 0 | 0.100 | 0.083 | 0.050 | 1.308 | 1.000 | 0.520 |
| image-imagenette | random | 0 | 0.100 | 0.084 | 0.010 | 1.245 | 1.000 | 0.350 |
| mnist | greedy_entropy | 0 | 0.100 | 0.091 | 0.000 | 0.952 | 0.300 | 0.020 |
| mnist | random | 0 | 0.100 | 0.089 | 0.000 | 0.949 | 0.140 | 0.000 |
| tabular-adult | greedy_entropy | 0 | 0.250 | 0.197 | 0.010 | 1.180 | 1.000 | 1.000 |
| tabular-adult | random | 0 | 0.250 | 0.186 | 0.010 | 1.049 | 1.000 | 0.210 |
| tabular-MiniBooNE | greedy_entropy | 0 | 0.150 | 0.130 | 0.000 | 1.654 | 1.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | 0.150 | 0.141 | 0.000 | 1.143 | 1.000 | 1.000 |

### 8.4 TABLE_E6_baselines

Convention for `mondrian_oracle.stratum_violation`: strata where the per-stratum oracle certifies no λ fall back to full acquisition, the same rule its `test_risk` and `test_cost` use.

| dataset | policy | seed | baseline | mean_test_risk | mean_test_cost | stratum_violation_rate | aggregate_violation_rate | stratum_certified_violation_rate |
|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 0 | budget_0.25 | 0.095 | 11.000 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | budget_0.5 | 0.095 | 22.000 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | budget_0.75 | 0.095 | 34.000 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.9 | 0.096 | 9.496 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.95 | 0.096 | 12.179 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | fixed_conf_0.99 | 0.096 | 13.218 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | full_acquisition | 0.096 | 45.000 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | mondrian_oracle | 0.114 | 11.650 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | oracle_cheapest_valid | 0.099 | 6.915 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | greedy_entropy | 0 | plugin | 0.099 | 6.915 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | budget_0.25 | 0.164 | 11.000 | 1.000 | 1.000 | 1.000 |
| csv-diabetes | random | 0 | budget_0.5 | 0.131 | 22.000 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | budget_0.75 | 0.107 | 34.000 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | fixed_conf_0.9 | 0.117 | 16.332 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | fixed_conf_0.95 | 0.103 | 19.841 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | fixed_conf_0.99 | 0.098 | 24.320 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | full_acquisition | 0.096 | 45.000 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | mondrian_oracle | 0.150 | 10.563 | 1.000 | 0.380 | 1.000 |
| csv-diabetes | random | 0 | oracle_cheapest_valid | 0.148 | 10.300 | 1.000 | 0.000 | 1.000 |
| csv-diabetes | random | 0 | plugin | 0.150 | 9.908 | 1.000 | 0.400 | 1.000 |
| csv-physionet | greedy_entropy | 0 | budget_0.25 | 0.141 | 10.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | budget_0.5 | 0.136 | 20.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | budget_0.75 | 0.128 | 31.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.9 | 0.132 | 7.622 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.95 | 0.128 | 14.584 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | fixed_conf_0.99 | 0.127 | 27.377 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | mondrian_oracle | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | oracle_cheapest_valid | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | greedy_entropy | 0 | plugin | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | budget_0.25 | 0.144 | 10.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | budget_0.5 | 0.138 | 20.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | budget_0.75 | 0.136 | 31.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | fixed_conf_0.9 | 0.133 | 12.147 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | fixed_conf_0.95 | 0.129 | 24.435 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | fixed_conf_0.99 | 0.127 | 36.329 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | full_acquisition | 0.127 | 41.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | mondrian_oracle | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | oracle_cheapest_valid | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |
| csv-physionet | random | 0 | plugin | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | budget_0.25 | 0.133 | 5.000 | 1.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 0 | budget_0.5 | 0.069 | 10.000 | 0.000 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | budget_0.75 | 0.059 | 15.000 | 0.000 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | fixed_conf_0.9 | 0.085 | 6.589 | 0.000 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | fixed_conf_0.95 | 0.063 | 8.354 | 0.000 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | fixed_conf_0.99 | 0.048 | 11.685 | 0.000 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | mondrian_oracle | 0.115 | 4.960 | 0.050 | 0.000 | 0.000 |
| cube | greedy_entropy | 0 | oracle_cheapest_valid | 0.149 | 3.733 | 1.000 | 0.000 | 1.000 |
| cube | greedy_entropy | 0 | plugin | 0.148 | 3.749 | 1.000 | 0.310 | 0.990 |
| cube | random | 0 | budget_0.25 | 0.531 | 5.000 | 1.000 | 1.000 | 1.000 |
| cube | random | 0 | budget_0.5 | 0.274 | 10.000 | 1.000 | 1.000 | 1.000 |
| cube | random | 0 | budget_0.75 | 0.119 | 15.000 | 1.000 | 0.000 | 1.000 |
| cube | random | 0 | fixed_conf_0.9 | 0.076 | 12.820 | 0.000 | 0.000 | 0.000 |
| cube | random | 0 | fixed_conf_0.95 | 0.058 | 14.195 | 0.000 | 0.000 | 0.000 |
| cube | random | 0 | fixed_conf_0.99 | 0.047 | 16.120 | 0.000 | 0.000 | 0.000 |
| cube | random | 0 | full_acquisition | 0.046 | 20.000 | 0.000 | 0.000 | 0.000 |
| cube | random | 0 | mondrian_oracle | 0.112 | 10.954 | 0.030 | 0.000 | 0.000 |
| cube | random | 0 | oracle_cheapest_valid | 0.147 | 9.602 | 1.000 | 0.000 | 1.000 |
| cube | random | 0 | plugin | 0.151 | 9.470 | 1.000 | 0.570 | 1.000 |
| fashionmnist | greedy_entropy | 0 | budget_0.25 | 0.117 | 12.000 | 1.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 0 | budget_0.5 | 0.079 | 24.000 | 1.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 0 | budget_0.75 | 0.065 | 37.000 | 1.000 | 0.000 | 0.200 |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.091 | 9.031 | 1.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.073 | 12.621 | 0.600 | 0.000 | 0.000 |
| fashionmnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.060 | 20.979 | 0.200 | 0.000 | 0.000 |
| fashionmnist | greedy_entropy | 0 | full_acquisition | 0.058 | 49.000 | 0.200 | 0.000 | 0.000 |
| fashionmnist | greedy_entropy | 0 | mondrian_oracle | 0.123 | 12.859 | 0.210 | 0.000 | 0.000 |
| fashionmnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.148 | 4.793 | 1.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | 0 | plugin | 0.144 | 5.003 | 1.000 | 0.040 | 1.000 |
| fashionmnist | random | 0 | budget_0.25 | 0.141 | 12.000 | 1.000 | 0.000 | 1.000 |
| fashionmnist | random | 0 | budget_0.5 | 0.090 | 24.000 | 1.000 | 0.000 | 1.000 |
| fashionmnist | random | 0 | budget_0.75 | 0.069 | 37.000 | 1.000 | 0.000 | 1.000 |
| fashionmnist | random | 0 | fixed_conf_0.9 | 0.089 | 12.345 | 1.000 | 0.000 | 0.800 |
| fashionmnist | random | 0 | fixed_conf_0.95 | 0.071 | 15.923 | 0.600 | 0.000 | 0.200 |
| fashionmnist | random | 0 | fixed_conf_0.99 | 0.059 | 23.110 | 0.200 | 0.000 | 0.000 |
| fashionmnist | random | 0 | full_acquisition | 0.058 | 49.000 | 0.200 | 0.000 | 0.000 |
| fashionmnist | random | 0 | mondrian_oracle | 0.127 | 14.402 | 0.210 | 0.000 | 0.010 |
| fashionmnist | random | 0 | oracle_cheapest_valid | 0.147 | 7.452 | 1.000 | 0.000 | 1.000 |
| fashionmnist | random | 0 | plugin | 0.147 | 7.469 | 1.000 | 0.250 | 1.000 |
| image-imagenette | greedy_entropy | 0 | budget_0.25 | 0.104 | 12.000 | 1.000 | 0.800 | 1.000 |
| image-imagenette | greedy_entropy | 0 | budget_0.5 | 0.062 | 24.000 | 1.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | 0 | budget_0.75 | 0.041 | 37.000 | 0.800 | 0.000 | 0.200 |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.9 | 0.087 | 7.765 | 1.000 | 0.000 | 0.600 |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.95 | 0.060 | 10.097 | 0.600 | 0.000 | 0.000 |
| image-imagenette | greedy_entropy | 0 | fixed_conf_0.99 | 0.036 | 15.312 | 0.000 | 0.000 | 0.000 |
| image-imagenette | greedy_entropy | 0 | full_acquisition | 0.030 | 49.000 | 0.000 | 0.000 | 0.000 |
| image-imagenette | greedy_entropy | 0 | mondrian_oracle | 0.065 | 14.464 | 0.080 | 0.000 | 0.000 |
| image-imagenette | greedy_entropy | 0 | oracle_cheapest_valid | 0.098 | 7.057 | 1.000 | 0.000 | 0.800 |
| image-imagenette | greedy_entropy | 0 | plugin | 0.099 | 6.994 | 1.000 | 0.490 | 0.990 |
| image-imagenette | random | 0 | budget_0.25 | 0.110 | 12.000 | 1.000 | 0.800 | 1.000 |
| image-imagenette | random | 0 | budget_0.5 | 0.055 | 24.000 | 1.000 | 0.000 | 1.000 |
| image-imagenette | random | 0 | budget_0.75 | 0.034 | 37.000 | 0.000 | 0.000 | 0.000 |
| image-imagenette | random | 0 | fixed_conf_0.9 | 0.077 | 8.154 | 1.000 | 0.000 | 0.000 |
| image-imagenette | random | 0 | fixed_conf_0.95 | 0.053 | 10.445 | 0.200 | 0.000 | 0.000 |
| image-imagenette | random | 0 | fixed_conf_0.99 | 0.035 | 15.633 | 0.000 | 0.000 | 0.000 |
| image-imagenette | random | 0 | full_acquisition | 0.030 | 49.000 | 0.000 | 0.000 | 0.000 |
| image-imagenette | random | 0 | mondrian_oracle | 0.066 | 13.961 | 0.110 | 0.000 | 0.010 |
| image-imagenette | random | 0 | oracle_cheapest_valid | 0.099 | 6.529 | 1.000 | 0.000 | 1.000 |
| image-imagenette | random | 0 | plugin | 0.098 | 6.612 | 1.000 | 0.330 | 0.990 |
| mnist | greedy_entropy | 0 | budget_0.25 | 0.027 | 12.000 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | budget_0.5 | 0.016 | 24.000 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | budget_0.75 | 0.010 | 37.000 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.9 | 0.046 | 4.608 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.95 | 0.026 | 5.957 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | fixed_conf_0.99 | 0.011 | 10.331 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | full_acquisition | 0.006 | 49.000 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | mondrian_oracle | 0.084 | 3.604 | 0.000 | 0.000 | 0.000 |
| mnist | greedy_entropy | 0 | oracle_cheapest_valid | 0.098 | 3.406 | 1.000 | 0.000 | 0.800 |
| mnist | greedy_entropy | 0 | plugin | 0.098 | 3.415 | 0.970 | 0.190 | 0.620 |
| mnist | random | 0 | budget_0.25 | 0.115 | 12.000 | 1.000 | 1.000 | 1.000 |
| mnist | random | 0 | budget_0.5 | 0.025 | 24.000 | 0.000 | 0.000 | 0.000 |
| mnist | random | 0 | budget_0.75 | 0.009 | 37.000 | 0.000 | 0.000 | 0.000 |
| mnist | random | 0 | fixed_conf_0.9 | 0.055 | 9.741 | 0.000 | 0.000 | 0.000 |
| mnist | random | 0 | fixed_conf_0.95 | 0.031 | 11.456 | 0.000 | 0.000 | 0.000 |
| mnist | random | 0 | fixed_conf_0.99 | 0.010 | 15.352 | 0.000 | 0.000 | 0.000 |
| mnist | random | 0 | full_acquisition | 0.006 | 49.000 | 0.000 | 0.000 | 0.000 |
| mnist | random | 0 | mondrian_oracle | 0.076 | 8.727 | 0.000 | 0.000 | 0.000 |
| mnist | random | 0 | oracle_cheapest_valid | 0.097 | 8.036 | 1.000 | 0.000 | 0.000 |
| mnist | random | 0 | plugin | 0.096 | 8.072 | 0.760 | 0.280 | 0.090 |
| tabular-adult | greedy_entropy | 0 | budget_0.25 | 0.216 | 4.000 | 1.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 0 | budget_0.5 | 0.181 | 7.000 | 1.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 0 | budget_0.75 | 0.158 | 10.000 | 0.000 | 0.000 | 0.000 |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.9 | 0.151 | 7.320 | 0.000 | 0.000 | 0.000 |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.95 | 0.149 | 8.469 | 0.000 | 0.000 | 0.000 |
| tabular-adult | greedy_entropy | 0 | fixed_conf_0.99 | 0.147 | 11.556 | 0.000 | 0.000 | 0.000 |
| tabular-adult | greedy_entropy | 0 | full_acquisition | 0.147 | 14.000 | 0.000 | 0.000 | 0.000 |
| tabular-adult | greedy_entropy | 0 | mondrian_oracle | 0.179 | 2.113 | 0.010 | 0.000 | 0.000 |
| tabular-adult | greedy_entropy | 0 | oracle_cheapest_valid | 0.237 | 0.476 | 1.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | 0 | plugin | 0.220 | 1.273 | 1.000 | 0.150 | 1.000 |
| tabular-adult | random | 0 | budget_0.25 | 0.206 | 4.000 | 1.000 | 0.000 | 1.000 |
| tabular-adult | random | 0 | budget_0.5 | 0.181 | 7.000 | 1.000 | 0.000 | 1.000 |
| tabular-adult | random | 0 | budget_0.75 | 0.160 | 10.000 | 1.000 | 0.000 | 1.000 |
| tabular-adult | random | 0 | fixed_conf_0.9 | 0.151 | 7.943 | 0.800 | 0.000 | 0.000 |
| tabular-adult | random | 0 | fixed_conf_0.95 | 0.149 | 9.583 | 0.800 | 0.000 | 0.000 |
| tabular-adult | random | 0 | fixed_conf_0.99 | 0.147 | 11.953 | 0.800 | 0.000 | 0.000 |
| tabular-adult | random | 0 | full_acquisition | 0.147 | 14.000 | 0.800 | 0.000 | 0.000 |
| tabular-adult | random | 0 | mondrian_oracle | 0.190 | 3.564 | 0.800 | 0.000 | 0.000 |
| tabular-adult | random | 0 | oracle_cheapest_valid | 0.234 | 0.688 | 1.000 | 0.000 | 0.800 |
| tabular-adult | random | 0 | plugin | 0.214 | 1.856 | 1.000 | 0.150 | 0.560 |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.25 | 0.110 | 12.000 | 1.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.5 | 0.092 | 25.000 | 1.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | budget_0.75 | 0.085 | 38.000 | 1.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.9 | 0.090 | 10.580 | 1.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.95 | 0.081 | 16.828 | 0.800 | 0.000 | 0.200 |
| tabular-MiniBooNE | greedy_entropy | 0 | fixed_conf_0.99 | 0.078 | 28.661 | 0.600 | 0.000 | 0.200 |
| tabular-MiniBooNE | greedy_entropy | 0 | full_acquisition | 0.077 | 50.000 | 0.600 | 0.000 | 0.200 |
| tabular-MiniBooNE | greedy_entropy | 0 | mondrian_oracle | 0.103 | 15.161 | 0.600 | 0.000 | 0.200 |
| tabular-MiniBooNE | greedy_entropy | 0 | oracle_cheapest_valid | 0.130 | 3.070 | 1.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | greedy_entropy | 0 | plugin | 0.130 | 3.070 | 1.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | budget_0.25 | 0.155 | 12.000 | 1.000 | 1.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | budget_0.5 | 0.108 | 25.000 | 1.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | budget_0.75 | 0.090 | 38.000 | 1.000 | 0.000 | 0.800 |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.9 | 0.093 | 16.647 | 0.000 | 0.000 | 0.000 |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.95 | 0.082 | 23.538 | 0.000 | 0.000 | 0.000 |
| tabular-MiniBooNE | random | 0 | fixed_conf_0.99 | 0.077 | 35.213 | 0.000 | 0.000 | 0.000 |
| tabular-MiniBooNE | random | 0 | full_acquisition | 0.077 | 50.000 | 0.000 | 0.000 | 0.000 |
| tabular-MiniBooNE | random | 0 | mondrian_oracle | 0.132 | 12.771 | 0.030 | 0.000 | 0.000 |
| tabular-MiniBooNE | random | 0 | oracle_cheapest_valid | 0.147 | 7.113 | 1.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | 0 | plugin | 0.146 | 7.188 | 1.000 | 0.080 | 1.000 |

**Round 3 (Task K).** E6 also has a `feasible_rate` column, and two new rows per cell, inserted alphabetically between `oracle_cheapest_valid` and `plugin` in `results_v3/tables/TABLE_E6_baselines.csv`. Both are ex-post baselines that use test labels and cannot be deployed (definitions in §13.4).
- **Stratum-violation rate of the oracles.** It is not 0 everywhere. In infeasible draws the oracle falls back to full acquisition, which itself violates where the deepest stratum's full-information test risk exceeds α: Diabetes, and some splits of FashionMNIST, Adult random and MiniBooNE greedy. The safe-Mondrian oracle keeps full acquisition in its abstaining strata.

| dataset | policy | baseline | mean_test_risk | mean_test_cost | stratum_violation_rate | aggregate_violation_rate | stratum_certified_violation_rate | feasible_rate |
|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | oracle_stratum_safe | 0.096 | 45.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | greedy_entropy | oracle_stratum_safe_mondrian | 0.114 | 11.650 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | random | oracle_stratum_safe | 0.096 | 45.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| csv-diabetes | random | oracle_stratum_safe_mondrian | 0.150 | 10.467 | 1.000 | 0.400 | 1.000 | 0.000 |
| csv-physionet | greedy_entropy | oracle_stratum_safe | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | greedy_entropy | oracle_stratum_safe_mondrian | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | oracle_stratum_safe | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| csv-physionet | random | oracle_stratum_safe_mondrian | 0.143 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | oracle_stratum_safe | 0.121 | 4.578 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | greedy_entropy | oracle_stratum_safe_mondrian | 0.143 | 4.109 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | oracle_stratum_safe | 0.123 | 10.366 | 0.000 | 0.000 | 0.000 | 1.000 |
| cube | random | oracle_stratum_safe_mondrian | 0.145 | 9.765 | 0.000 | 0.000 | 0.000 | 1.000 |
| fashionmnist | greedy_entropy | oracle_stratum_safe | 0.069 | 20.726 | 0.200 | 0.000 | 0.000 | 0.800 |
| fashionmnist | greedy_entropy | oracle_stratum_safe_mondrian | 0.143 | 8.979 | 0.200 | 0.000 | 0.000 | 0.800 |
| fashionmnist | random | oracle_stratum_safe | 0.068 | 22.741 | 0.200 | 0.000 | 0.000 | 0.800 |
| fashionmnist | random | oracle_stratum_safe_mondrian | 0.149 | 10.992 | 0.200 | 0.000 | 0.000 | 0.800 |
| image-imagenette | greedy_entropy | oracle_stratum_safe | 0.051 | 11.382 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | greedy_entropy | oracle_stratum_safe_mondrian | 0.097 | 8.331 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | oracle_stratum_safe | 0.062 | 9.263 | 0.000 | 0.000 | 0.000 | 1.000 |
| image-imagenette | random | oracle_stratum_safe_mondrian | 0.098 | 7.505 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | oracle_stratum_safe | 0.089 | 3.514 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | greedy_entropy | oracle_stratum_safe_mondrian | 0.096 | 3.417 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | oracle_stratum_safe | 0.091 | 8.236 | 0.000 | 0.000 | 0.000 | 1.000 |
| mnist | random | oracle_stratum_safe_mondrian | 0.097 | 8.035 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | oracle_stratum_safe | 0.184 | 2.766 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | greedy_entropy | oracle_stratum_safe_mondrian | 0.184 | 1.936 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-adult | random | oracle_stratum_safe | 0.154 | 11.979 | 0.800 | 0.000 | 0.000 | 0.200 |
| tabular-adult | random | oracle_stratum_safe_mondrian | 0.200 | 3.022 | 0.800 | 0.000 | 0.000 | 0.200 |
| tabular-MiniBooNE | greedy_entropy | oracle_stratum_safe | 0.079 | 37.244 | 0.600 | 0.000 | 0.200 | 0.400 |
| tabular-MiniBooNE | greedy_entropy | oracle_stratum_safe_mondrian | 0.103 | 13.400 | 0.600 | 0.000 | 0.200 | 0.400 |
| tabular-MiniBooNE | random | oracle_stratum_safe | 0.112 | 11.515 | 0.000 | 0.000 | 0.000 | 1.000 |
| tabular-MiniBooNE | random | oracle_stratum_safe_mondrian | 0.145 | 8.053 | 0.000 | 0.000 | 0.000 | 1.000 |

### 8.5 Violations per split (cells over δ in round 1, and every other cell)

`python scripts/report_violations_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --lambda-ref-key dep --focus ...` → `results_v3/diagnostics/r2_violations_dep.md` (and `r2_violations_lr{0.5,0.7,0.9}.md`). By-split columns are in test-seed order 778, 779, 780, 781, 782.


Metrics: F:/CAFA_results/metrics_v3; lambda_ref key dep; scheme uniform; by-split columns in test-seed order ['778', '779', '780', '781', '782'].

| cell | focus | cert. deployment | raw viol pooled | raw by split | certified viol | certified by split | max_excess_se mean | q90 | by split (means) | certified ≤ δ+0.05 | mean excess ≤ 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes:greedy_entropy:ts0 |  | 1.00 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.877 | -1.821 | -3.863 -4.150 -3.414 -2.365 -5.592 | pass | pass |
| csv-diabetes:random:ts0 |  | 1.00 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.937 | -1.845 | -4.295 -3.904 -4.000 -2.911 -4.576 | pass | pass |
| csv-physionet:greedy_entropy:ts0 |  | 1.00 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -6.616 | -5.756 | -6.455 -7.262 -6.509 -7.100 -5.756 | pass | pass |
| csv-physionet:random:ts0 |  | 1.00 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -6.616 | -5.756 | -6.455 -7.262 -6.509 -7.100 -5.756 | pass | pass |
| cube:greedy_entropy:ts0 |  | 1.00 | 0.010 | 0.000 0.000 0.000 0.000 0.050 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.368 | -2.093 | -4.010 -3.323 -4.189 -2.856 -2.462 | pass | pass |
| cube:random:ts0 |  | 1.00 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.338 | -2.108 | -3.350 -4.547 -3.267 -2.936 -2.588 | pass | pass |
| fashionmnist:greedy_entropy:ts0 | yes | 1.00 | 0.100 | 0.450 0.000 0.050 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -4.109 | -0.026 | -1.934 -4.967 -2.713 -5.508 -5.425 | pass | pass |
| fashionmnist:random:ts0 | yes | 1.00 | 0.100 | 0.500 0.000 0.000 0.000 0.000 | 0.010 | 0.050 0.000 0.000 0.000 0.000 | -3.966 | -0.209 | -0.088 -5.250 -3.352 -5.256 -5.884 | pass | pass |
| image-imagenette:greedy_entropy:ts0 |  | 1.00 | 0.050 | 0.000 0.000 0.000 0.100 0.150 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.152 | -1.057 | -4.750 -3.198 -3.858 -2.407 -1.546 | pass | pass |
| image-imagenette:random:ts0 |  | 1.00 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.604 | -1.616 | -4.495 -2.632 -3.759 -4.736 -2.397 | pass | pass |
| mnist:greedy_entropy:ts0 |  | 1.00 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.514 | -2.681 | -3.823 -3.415 -2.923 -3.167 -4.243 | pass | pass |
| mnist:random:ts0 |  | 1.00 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.759 | -3.015 | -4.622 -3.444 -3.651 -3.699 -3.381 | pass | pass |
| tabular-adult:greedy_entropy:ts0 |  | 1.00 | 0.010 | 0.000 0.000 0.000 0.000 0.050 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.812 | -3.320 | -4.154 -3.320 -3.393 -4.219 -3.973 | pass | pass |
| tabular-adult:random:ts0 |  | 1.00 | 0.020 | 0.000 0.100 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -3.273 | -0.816 | -3.993 -1.200 -3.401 -3.012 -4.760 | pass | pass |
| tabular-MiniBooNE:greedy_entropy:ts0 | yes | 1.00 | 0.020 | 0.100 0.000 0.000 0.000 0.000 | 0.010 | 0.050 0.000 0.000 0.000 0.000 | -4.055 | -1.557 | -1.670 -4.127 -6.551 -6.038 -1.890 | pass | pass |
| tabular-MiniBooNE:random:ts0 | yes | 1.00 | 0.030 | 0.150 0.000 0.000 0.000 0.000 | 0.000 | 0.000 0.000 0.000 0.000 0.000 | -4.613 | -1.458 | -1.445 -5.308 -5.714 -5.880 -4.717 | pass | pass |

Cells failing an acceptance check: none

The four cells over δ in round 1 (raw rate on split 778 alone): FashionMNIST greedy 0.350 → by split 0.450 / 0.000 / 0.050 / 0.000 / 0.000 (pooled 0.100); FashionMNIST random 0.580 → 0.500 / 0.000 / 0.000 / 0.000 / 0.000 (0.100); MiniBooNE greedy 0.110 → 0.100 / 0.000 / 0.000 / 0.000 / 0.000 (0.020); MiniBooNE random 0.120 → 0.150 / 0.000 / 0.000 / 0.000 / 0.000 (0.030). In each of them the largest per-split rate is on split 778 and the other four splits are ≤ 0.050 (the only nonzero one: FashionMNIST greedy, 0.050 on split 780). Split 778 is above δ = 0.10 in three of the cells and equal to δ in MiniBooNE greedy. The certified-violation rate is ≤ 0.010 pooled and ≤ 0.05 on split 778.

Multi-split diagnosis of FashionMNIST random `dep` (`python scripts/diagnose_violation_v3.py --dataset fashionmnist --policy random --train-seed 0 --lambda-ref-key dep --output results_v3/diagnostics/r2_fashionmnist_ts0_random_dep.json`; log `results_v3/logs/r2_taskC_diagnose_fashionmnist_random_dep.log`). Every split passes every integrity check (digests, sizes, disjointness and coverage, numpy-vs-`reference_buckets` strata; the flagged draws' calibration rows lie in their own calpool and outside the test split; the test p-values recomputed independently equal the sweep's). Deepest-stratum (k = 4) full-acquisition risk, calibration pool → test split: 778 0.1287 → 0.1557; 779 0.1480 → 0.1364; 780 0.1422 → 0.1421; 781 0.1443 → 0.1400; 782 0.1487 → 0.1356. Only split 778 pairs an optimistic calibration pool with a pessimistic test split, and only split 778 has raw violations (0.50; certified 0.05). The round-1 diagnoses of these cells are in `results_v3/round1/diagnostics/` (superseded; they used split 778 only).

### 8.6 E7 — audit-guided repair (`results_v3/repair/*.json`, 5 splits × 20 draws each)

`python scripts/run_repairs_v3.py --seeds 0 --tag r2 --force` (ledger `r2:repair:*`; logs `results_v3/logs/r2_repair_*.log`; console lines collected in `results_v3/logs/r2_taskC_repair_console.log`). Predictor upgrade: BEFORE = AAAI v2 cache + `configs/committed_v3before_{ds}_ts0.json` (re-committed in round 2), AFTER = v3 greedy cache on the BEFORE strata. Policy change: BEFORE = v3 random cache on the main commit (`--policy random`), AFTER = v3 greedy cache. Policy change covers the 7 seed-0 datasets of Task C (round 1 ran 6; FashionMNIST added because Task C says "policy change for the 7 datasets") and Imagenette (Task D; uniform costs only).

```
csv-diabetes_policy_change  [repair:policy_change] lr[0.5]=0.500 deepest k=0: feasible (rmin 0.095, full 0.095) -> feasible (rmin 0.094, full 0.095); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-diabetes_policy_change  [repair:policy_change] lr[0.7]=0.700 deepest k=0: feasible (rmin 0.095, full 0.095) -> feasible (rmin 0.094, full 0.095); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-diabetes_policy_change  [repair:policy_change] lr[0.9]=0.900 deepest k=4: type_II (rmin 0.357, full 0.357) -> type_II (rmin 0.352, full 0.357); tier1 0.00 -> 0.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-diabetes_policy_change  [repair:policy_change] lr[dep]=0.828 deepest k=3: type_II (rmin 0.241, full 0.241) -> type_II (rmin 0.236, full 0.241); tier1 0.00 -> 0.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-physionet_policy_change  [repair:policy_change] lr[0.5]=0.500 deepest k=0: feasible (rmin 0.126, full 0.126) -> feasible (rmin 0.126, full 0.126); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-physionet_policy_change  [repair:policy_change] lr[0.7]=0.700 deepest k=0: feasible (rmin 0.126, full 0.126) -> feasible (rmin 0.126, full 0.126); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-physionet_policy_change  [repair:policy_change] lr[0.9]=0.900 deepest k=1: feasible (rmin 0.184, full 0.187) -> feasible (rmin 0.187, full 0.187); tier1 0.15 -> 0.15; viol 0.06 -> 0.02; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
csv-physionet_policy_change  [repair:policy_change] lr[dep]=0.000 deepest k=0: feasible (rmin 0.126, full 0.126) -> feasible (rmin 0.126, full 0.126); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
cube_policy_change  [repair:policy_change] lr[0.5]=0.500 deepest k=3: feasible (rmin 0.054, full 0.054) -> feasible (rmin 0.054, full 0.054); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
cube_policy_change  [repair:policy_change] lr[0.7]=0.700 deepest k=3: feasible (rmin 0.080, full 0.083) -> feasible (rmin 0.083, full 0.083); tier1 0.99 -> 0.99; viol 0.00 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
cube_policy_change  [repair:policy_change] lr[0.9]=0.900 deepest k=3: feasible (rmin 0.145, full 0.147) -> feasible (rmin 0.147, full 0.147); tier1 0.03 -> 0.03; viol 0.02 -> 0.02; certviol 0.00 -> 0.01; verdict agreement 5/5 -> 5/5
cube_policy_change  [repair:policy_change] lr[dep]=0.707 deepest k=3: feasible (rmin 0.080, full 0.083) -> feasible (rmin 0.083, full 0.083); tier1 0.99 -> 0.99; viol 0.00 -> 0.02; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
fashionmnist_policy_change  [repair:policy_change] lr[0.5]=0.500 deepest k=3: feasible (rmin 0.082, full 0.085) -> feasible (rmin 0.084, full 0.085); tier1 1.00 -> 1.00; viol 0.03 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
fashionmnist_policy_change  [repair:policy_change] lr[0.7]=0.700 deepest k=4: feasible (rmin 0.114, full 0.116) -> feasible (rmin 0.116, full 0.116); tier1 0.70 -> 0.70; viol 0.13 -> 0.01; certviol 0.01 -> 0.00; verdict agreement 5/5 -> 5/5
fashionmnist_policy_change  [repair:policy_change] lr[0.9]=0.900 deepest k=4: type_II (rmin 0.170, full 0.171) -> type_II (rmin 0.171, full 0.171); tier1 0.00 -> 0.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
fashionmnist_policy_change  [repair:policy_change] lr[dep]=0.778 deepest k=4: feasible (rmin 0.126, full 0.129) -> feasible (rmin 0.128, full 0.129); tier1 0.12 -> 0.12; viol 0.10 -> 0.10; certviol 0.01 -> 0.01; verdict agreement 5/5 -> 5/5
image-imagenette_policy_change  [repair:policy_change] lr[0.5]=0.500 deepest k=2: feasible (rmin 0.050, full 0.050) -> feasible (rmin 0.048, full 0.050); tier1 0.64 -> 0.64; viol 0.00 -> 0.03; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
image-imagenette_policy_change  [repair:policy_change] lr[0.7]=0.700 deepest k=3: feasible (rmin 0.050, full 0.050) -> feasible (rmin 0.050, full 0.050); tier1 0.58 -> 0.58; viol 0.00 -> 0.06; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
image-imagenette_policy_change  [repair:policy_change] lr[0.9]=0.900 deepest k=3: feasible (rmin 0.092, full 0.092) -> feasible (rmin 0.092, full 0.092); tier1 0.01 -> 0.01; viol 0.01 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
image-imagenette_policy_change  [repair:policy_change] lr[dep]=0.838 deepest k=3: feasible (rmin 0.083, full 0.083) -> feasible (rmin 0.081, full 0.083); tier1 0.09 -> 0.09; viol 0.00 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_policy_change  [repair:policy_change] lr[0.5]=0.500 deepest k=4: feasible (rmin 0.006, full 0.006) -> feasible (rmin 0.006, full 0.006); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_policy_change  [repair:policy_change] lr[0.7]=0.700 deepest k=4: feasible (rmin 0.008, full 0.008) -> feasible (rmin 0.008, full 0.008); tier1 1.00 -> 1.00; viol 0.00 -> 0.16; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_policy_change  [repair:policy_change] lr[0.9]=0.900 deepest k=4: feasible (rmin 0.013, full 0.013) -> feasible (rmin 0.013, full 0.013); tier1 1.00 -> 1.00; viol 0.00 -> 0.05; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_policy_change  [repair:policy_change] lr[dep]=0.788 deepest k=4: feasible (rmin 0.012, full 0.012) -> feasible (rmin 0.012, full 0.012); tier1 1.00 -> 1.00; viol 0.00 -> 0.08; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_predictor_upgrade  [repair:predictor_upgrade] lr[0.5]=0.500 deepest k=4: feasible (rmin 0.144, full 0.145) -> feasible (rmin 0.008, full 0.008); tier1 0.04 -> 1.00; viol 0.04 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_predictor_upgrade  [repair:predictor_upgrade] lr[0.7]=0.700 deepest k=4: type_II (rmin 0.195, full 0.196) -> feasible (rmin 0.010, full 0.010); tier1 0.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_predictor_upgrade  [repair:predictor_upgrade] lr[0.9]=0.900 deepest k=4: type_II (rmin 0.255, full 0.255) -> feasible (rmin 0.011, full 0.011); tier1 0.00 -> 1.00; viol 0.00 -> 0.03; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
mnist_predictor_upgrade  [repair:predictor_upgrade] lr[dep]=0.869 deepest k=4: type_II (rmin 0.295, full 0.296) -> feasible (rmin 0.011, full 0.012); tier1 0.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_policy_change  [repair:policy_change] lr[0.5]=0.500 deepest k=0: feasible (rmin 0.075, full 0.075) -> feasible (rmin 0.075, full 0.075); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_policy_change  [repair:policy_change] lr[0.7]=0.700 deepest k=0: feasible (rmin 0.075, full 0.075) -> feasible (rmin 0.075, full 0.075); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_policy_change  [repair:policy_change] lr[0.9]=0.900 deepest k=4: type_II (rmin 0.198, full 0.198) -> type_II (rmin 0.198, full 0.198); tier1 0.00 -> 0.00; viol 0.01 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_policy_change  [repair:policy_change] lr[dep]=0.778 deepest k=3: feasible (rmin 0.132, full 0.132) -> feasible (rmin 0.132, full 0.132); tier1 0.26 -> 0.26; viol 0.03 -> 0.02; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_predictor_upgrade  [repair:predictor_upgrade] lr[0.5]=0.500 deepest k=0: feasible (rmin 0.082, full 0.082) -> feasible (rmin 0.075, full 0.075); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_predictor_upgrade  [repair:predictor_upgrade] lr[0.7]=0.700 deepest k=0: feasible (rmin 0.082, full 0.082) -> feasible (rmin 0.075, full 0.075); tier1 1.00 -> 1.00; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_predictor_upgrade  [repair:predictor_upgrade] lr[0.9]=0.900 deepest k=4: type_II (rmin 0.247, full 0.248) -> type_II (rmin 0.223, full 0.223); tier1 0.00 -> 0.00; viol 0.03 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-MiniBooNE_predictor_upgrade  [repair:predictor_upgrade] lr[dep]=0.727 deepest k=3: unresolved (rmin 0.157, full 0.157) -> feasible (rmin 0.142, full 0.143); tier1 0.00 -> 0.01; viol 0.00 -> 0.01; certviol 0.00 -> 0.01; verdict agreement 1/5 -> 2/5
tabular-adult_policy_change  [repair:policy_change] lr[0.5]=0.500 deepest k=0: feasible (rmin 0.147, full 0.147) -> feasible (rmin 0.147, full 0.147); tier1 1.00 -> 1.00; viol 0.01 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_policy_change  [repair:policy_change] lr[0.7]=0.700 deepest k=0: feasible (rmin 0.147, full 0.147) -> feasible (rmin 0.147, full 0.147); tier1 1.00 -> 1.00; viol 0.01 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_policy_change  [repair:policy_change] lr[0.9]=0.900 deepest k=2: type_II (rmin 0.302, full 0.303) -> type_II (rmin 0.301, full 0.303); tier1 0.00 -> 0.00; viol 0.05 -> 0.05; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_policy_change  [repair:policy_change] lr[dep]=0.758 deepest k=2: unresolved (rmin 0.253, full 0.254) -> feasible (rmin 0.248, full 0.254); tier1 0.00 -> 0.00; viol 0.02 -> 0.02; certviol 0.00 -> 0.00; verdict agreement 2/5 -> 4/5
tabular-adult_predictor_upgrade  [repair:predictor_upgrade] lr[0.5]=0.500 deepest k=0: feasible (rmin 0.148, full 0.148) -> feasible (rmin 0.147, full 0.147); tier1 1.00 -> 1.00; viol 0.01 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_predictor_upgrade  [repair:predictor_upgrade] lr[0.7]=0.700 deepest k=0: feasible (rmin 0.148, full 0.148) -> feasible (rmin 0.147, full 0.147); tier1 1.00 -> 1.00; viol 0.01 -> 0.01; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
tabular-adult_predictor_upgrade  [repair:predictor_upgrade] lr[0.9]=0.900 deepest k=2: type_II (rmin 0.296, full 0.296) -> type_II (rmin 0.292, full 0.292); tier1 0.00 -> 0.00; viol 0.11 -> 0.18; certviol 0.00 -> 0.05; verdict agreement 5/5 -> 5/5
tabular-adult_predictor_upgrade  [repair:predictor_upgrade] lr[dep]=0.758 deepest k=1: feasible (rmin 0.196, full 0.197) -> feasible (rmin 0.194, full 0.194); tier1 1.00 -> 0.99; viol 0.00 -> 0.00; certviol 0.00 -> 0.00; verdict agreement 5/5 -> 5/5
```

E7 against the plan's expectation (`dep`): **MNIST** predictor upgrade `type_II` → `feasible` (family minimum 0.295 → 0.011), tier-1 share 0.00 → 1.00 (also at λ_ref 0.7 and 0.9); raw violation 0.00 → 0.00, certified 0.00 → 0.00 (`results_v3/repair/mnist_ts0_predictor_upgrade.json`). **MiniBooNE** predictor upgrade `unresolved` → `feasible` (0.157 → 0.142), tier 1 0.00 → 0.01 (round 1: 0.07; verdict agreement 1/5 → 2/5). **Adult** policy change `unresolved` → `feasible` (0.253 → 0.248; agreement 2/5 → 4/5), tier 1 unchanged at 0.00. **Imagenette** policy change `feasible` → `feasible` (0.083 → 0.081), tier 1 0.09 → 0.09. The `type_II` verdicts at λ_ref 0.9 (Adult, MiniBooNE, Diabetes, FashionMNIST) are unchanged by either repair.

### 8.7 E9 — sensitivity

λ_ref sweep (`results_v3/tables_e9_lambda_ref_{0.5,0.7,0.9}/`, `results_v3/tables/` for `dep`; summary `results_v3/diagnostics/r2_e9_lambda_ref_summary.md`):

| λ_ref key | cells | min certified | mean certified | mean tier-1 | mean tier-3 | max raw violation | cells raw > δ | max certified violation | cells certified > δ+0.05 | cells mean max_excess_se > 0 | cells none > 0.05 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 16 | 1.00 | 1.000 | 0.978 | 0.022 | 0.030 (fashionmnist random) | 0 | 0.000 (csv-diabetes greedy_entropy) | 0 | 0 | 0 |
| 0.7 | 16 | 1.00 | 1.000 | 0.908 | 0.092 | 0.130 (fashionmnist random) | 1: fashionmnist random 0.130 | 0.010 (fashionmnist random) | 0 | 0 | 0 |
| 0.9 | 16 | 0.00 | 0.929 | 0.139 | 0.791 | 0.170 (tabular-adult greedy_entropy) | 1: tabular-adult greedy_entropy 0.170 | 0.000 (csv-diabetes greedy_entropy) | 0 | 0 | 2: csv-diabetes greedy_entropy 1.00; csv-diabetes random 0.13 |
| dep | 16 | 1.00 | 1.000 | 0.487 | 0.513 | 0.100 (fashionmnist greedy_entropy) | 0 | 0.010 (fashionmnist random) | 0 | 0 | 0 |

Other ablations:
- **δ split:** PhysioNet greedy with `--delta-weights 0.34,0.33,0.33` (`results_v3/tables_e9_delta_weights/`, `$RESULTS_ROOT\metrics_v3_dw\`; ledger `r2dw:sweep:*`): at `dep` tier 1 = 1.00, certified deployment 1.00, raw violation 0.000, certified violation 0.000 — the same as the committed split (§8.1). The same holds at every λ_ref key: tier shares (1/2/3/none) 1.00/0.00/0.00/0.00 at 0.5 and 0.7, 0.01/0.00/0.99/0.00 at 0.9, for both splits of δ (`results_v3/logs/r2_taskC_facts.log`).
- **Number of strata:** MNIST greedy with `--n-buckets 8` (`configs/committed_v3_G8_mnist_ts0.json`, re-committed in round 2; `results_v3/tables_e9_G8/`; ledger `r2G8:*`): G = 4 after the G-rule (vs 3), tier 1 = 1.00, deployed cost 3.791 (premium 1.084, vs 1.046 at G = 3 (§8.1)), raw violation 0.000, certified violation 0.000.
- **α rule (margin 0.02, grid 0.01):** (Task E; `commit_v3.py --alpha-margin 0.02 --alpha-grid 0.01 --out-path configs/committed_v3_am02_{dsname}_ts0.json`, sweeps `$RESULTS_ROOT\metrics_v3_alpha_margin02\`, tables `results_v3/tables_e9_alpha_margin02/`, comparison `results_v3/diagnostics/r2_e9_alpha_margin02_vs_default.md`). **PhysioNet:** α 0.20 → 0.15; λ_ref `dep` stays 0 and G stays 1 (the target is still degenerate); the tier pattern changes from tier 1 (1.00) to 0.58 tier 1 / 0.42 tier 3 for both policies. **Adult:** α 0.25 → 0.18; greedy λ_ref `dep` 0.758 → 0.808 with G 2, tier 1 → tier 3 (1.00) and the deepest stratum `feasible` → `type_II`; random λ_ref 0.758 and G 3 unchanged, stays tier 3, `unresolved` → `type_II`. **Other cells:** tier pattern changes in CUBE (both: 1 → 3), MiniBooNE random and FashionMNIST (both: 1+3 → 3) and Diabetes random (3 → none: certified deployment 0.02); unchanged in Diabetes greedy and MiniBooNE greedy (3). The deepest stratum becomes `type_II` in every committed cell except PhysioNet. **MNIST and Imagenette:** not committed. The rule gives α = 0.03 (MNIST) and 0.05 (Imagenette, probe floor 0.0299), both ≤ the design margin 0.05, so `n_min(α, level, margin)` is undefined and `commit_v3.py` stops with rc 7 (`results_v3/logs/r2am02_commit_{mnist,image-imagenette}_na_ts0.log`). In all 12 committed cells, certified violation = 0.000, mean max_excess_se < 0 and raw violation ≤ 0.010 (`results_v3/diagnostics/r2_violations_alpha_margin02_dep.md`).

| dataset | policy | α default → am02 | λ_ref dep default → am02 | G default → am02 | tiers 1/2/3/none default | tiers 1/2/3/none am02 | tier pattern changed | cert. deployment am02 | raw viol am02 | certified viol am02 | max_excess_se am02 | deepest verdict default → am02 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| csv-physionet | greedy_entropy | 0.2 → 0.15 | 0.0000 → 0.0000 | 1 → 1 | 1.00/0.00/0.00/0.00 | 0.58/0.00/0.42/0.00 | yes (1 → 1+3) | 1.00 | 0.010 | 0.000 | -3.39 | feasible → feasible |
| csv-physionet | random | 0.2 → 0.15 | 0.0000 → 0.0000 | 1 → 1 | 1.00/0.00/0.00/0.00 | 0.58/0.00/0.42/0.00 | yes (1 → 1+3) | 1.00 | 0.010 | 0.000 | -3.18 | feasible → feasible |
| tabular-adult | greedy_entropy | 0.25 → 0.18 | 0.7576 → 0.8081 | 2 → 2 | 1.00/0.00/0.00/0.00 | 0.00/0.00/1.00/0.00 | yes (1 → 3) | 1.00 | 0.000 | 0.000 | -2.97 | feasible → type_II |
| tabular-adult | random | 0.25 → 0.18 | 0.7576 → 0.7576 | 3 → 3 | 0.00/0.00/1.00/0.00 | 0.00/0.00/1.00/0.00 | no (3) | 1.00 | 0.000 | 0.000 | -2.89 | unresolved → type_II |
| csv-diabetes | greedy_entropy | 0.15 → 0.12 | 0.7980 → 0.7980 | 2 → 2 | 0.00/0.00/1.00/0.00 | 0.00/0.00/1.00/0.00 | no (3) | 1.00 | 0.000 | 0.000 | -4.24 | type_II → type_II |
| csv-diabetes | random | 0.15 → 0.12 | 0.8283 → 0.9091 | 4 → 5 | 0.00/0.00/1.00/0.00 | 0.00/0.00/0.02/0.98 | yes (3 → none) | 0.02 | 0.000 | 0.000 | -0.80 | type_II → type_II |
| cube | greedy_entropy | 0.15 → 0.08 | 0.7980 → 0.9293 | 3 → 5 | 1.00/0.00/0.00/0.00 | 0.00/0.00/1.00/0.00 | yes (1 → 3) | 1.00 | 0.000 | 0.000 | -4.06 | feasible → type_II |
| cube | random | 0.15 → 0.08 | 0.7071 → 0.8990 | 4 → 5 | 0.99/0.00/0.01/0.00 | 0.00/0.00/0.99/0.01 | yes (1 → 3) | 0.99 | 0.000 | 0.000 | -3.98 | feasible → type_II |
| tabular-MiniBooNE | greedy_entropy | 0.15 → 0.1 | 0.7475 → 0.8788 | 3 → 5 | 0.01/0.00/0.99/0.00 | 0.00/0.00/1.00/0.00 | no (3) | 1.00 | 0.000 | 0.000 | -3.43 | feasible → type_II |
| tabular-MiniBooNE | random | 0.15 → 0.1 | 0.7778 → 0.8889 | 4 → 5 | 0.26/0.00/0.74/0.00 | 0.00/0.00/1.00/0.00 | yes (1+3 → 3) | 1.00 | 0.000 | 0.000 | -4.26 | feasible → type_II |
| fashionmnist | greedy_entropy | 0.15 → 0.09 | 0.7778 → 0.9293 | 5 → 5 | 0.12/0.00/0.88/0.00 | 0.00/0.00/1.00/0.00 | yes (1+3 → 3) | 1.00 | 0.000 | 0.000 | -4.17 | feasible → type_II |
| fashionmnist | random | 0.15 → 0.09 | 0.7778 → 0.9192 | 5 → 5 | 0.12/0.00/0.88/0.00 | 0.00/0.00/1.00/0.00 | yes (1+3 → 3) | 1.00 | 0.000 | 0.000 | -3.43 | feasible → type_II |
| mnist | greedy_entropy | 0.1 → 0.03 (not committed, rc 7) | | | | | | | | | | |
| mnist | random | 0.1 → 0.03 (not committed, rc 7) | | | | | | | | | | |
| image-imagenette | greedy_entropy | 0.1 → 0.05 (not committed, rc 7) | | | | | | | | | | |
| image-imagenette | random | 0.1 → 0.05 (not committed, rc 7) | | | | | | | | | | |
- **Cost schemes:** `results_v3/tables_inverse_info/`.
- **α rule, margin 0.10 (round 3, Task H; §13.2).**
  - Commits `configs/committed_v3_am10_{dsname}_ts0.json` exist for all 8 datasets; none is refused.
  - Sweeps are in `$RESULTS_ROOT\metrics_v3_alpha_margin10\` and tables in `results_v3/tables_e9_alpha_margin10/`.
  - The comparison of margins 0.02 / 0.05 / 0.10 is `results_v3/tables/TABLE_E9_alpha_margin.md`, pasted in §13.2.
- **Calibration size (round 3, Task K2; §13.4).** `TABLE_E11_calfrac` covers cal_frac 0.25 / 0.5 / 1.0, with sweeps in `$RESULTS_ROOT\metrics_v3_calfrac{025,100}\`.

### 8.8 Figures

`python scripts/make_figures_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --planted results_v3/planted --repair-dir results_v3/repair --output-dir results_v3/figures` writes these files to `results_v3/figures/`:
- `F2_blindness.pdf`;
- `F3_cascade.pdf`;
- `F4_repair.pdf`;
- `F5_planted.pdf`;
- `F6_violations.pdf` (new: the raw pooled rate with the min–max over splits, the certified rate, and lines at δ and δ + 0.05).

All 16 cells are included. F5 is drawn from the round-2 planted run (`results_v3/planted/planted_validation.csv`; §7, §12.2).

Round-3 figure changes (rerun with `results_v3/logs/r3_postrun.sh`):
- **F3, Task I:** the cost panel is now in cost / T, and the E2 worst-stratum risk / α of marginal CAFA is printed under each bar.
- **F7, Task G (new):** `results_v3/figures/F7_margin.pdf`, written by `scripts/margin_analysis_v3.py`. It shows the observed tier-1 share against the deepest-stratum margin z, and against the prediction; the cal_frac 0.25 / 1.0 points are drawn as open markers.

### 8.9 Committed JSONs (`python scripts/report_v3.py --commits`; round-2 re-commits)

| commit | alpha | probe floor | n_cal expected | n_min tier1 | policy | G (0.5 / 0.7 / 0.9 / dep) | lambda_ref dep | tier-3 start (dep, answered frac.) |
|---|---|---|---|---|---|---|---|---|
| `committed_v3_am02_csv-diabetes_ts0.json` | 0.12 | 0.09723 | 8286 | 220 | greedy_entropy | 1 / 1 / 2 / 2 | 0.7980 | 0.050 |
| `committed_v3_am02_csv-diabetes_ts0.json` | 0.12 | 0.09723 | 8286 | 220 | random | 1 / 1 / 5 / 5 | 0.9091 | 0.098 |
| `committed_v3_am02_csv-physionet_ts0.json` | 0.15 | 0.125 | 1080 | 275 | greedy_entropy | 1 / 1 / 2 / 1 | 0.0000 | 0.549 |
| `committed_v3_am02_csv-physionet_ts0.json` | 0.15 | 0.125 | 1080 | 275 | random | 1 / 1 / 3 / 1 | 0.0000 | 0.549 |
| `committed_v3_am02_cube_ts0.json` | 0.08 | 0.05375 | 1800 | 137 | greedy_entropy | 3 / 3 / 4 / 5 | 0.9293 | 0.383 |
| `committed_v3_am02_cube_ts0.json` | 0.08 | 0.05375 | 1800 | 137 | random | 5 / 5 / 5 / 5 | 0.8990 | 0.430 |
| `committed_v3_am02_fashionmnist_ts0.json` | 0.09 | 0.064286 | 6300 | 159 | greedy_entropy | 3 / 4 / 5 / 5 | 0.9293 | 0.240 |
| `committed_v3_am02_fashionmnist_ts0.json` | 0.09 | 0.064286 | 6300 | 159 | random | 4 / 5 / 5 / 5 | 0.9192 | 0.264 |
| `committed_v3_am02_tabular-adult_ts0.json` | 0.18 | 0.154229 | 4070 | 326 | greedy_entropy | 1 / 1 / 3 / 2 | 0.8081 | 0.287 |
| `committed_v3_am02_tabular-adult_ts0.json` | 0.18 | 0.154229 | 4070 | 326 | random | 1 / 1 / 4 / 3 | 0.7576 | 0.145 |
| `committed_v3_am02_tabular-MiniBooNE_ts0.json` | 0.1 | 0.07438 | 11706 | 180 | greedy_entropy | 1 / 1 / 5 / 5 | 0.8788 | 0.169 |
| `committed_v3_am02_tabular-MiniBooNE_ts0.json` | 0.1 | 0.07438 | 11706 | 180 | random | 1 / 1 / 5 / 5 | 0.8889 | 0.098 |
| `committed_v3_csv-diabetes_ts0.json` | 0.15 | 0.09723 | 8286 | 275 | greedy_entropy | 1 / 1 / 2 / 2 | 0.7980 | 0.050 |
| `committed_v3_csv-diabetes_ts0.json` | 0.15 | 0.09723 | 8286 | 275 | random | 1 / 1 / 5 / 4 | 0.8283 | 0.335 |
| `committed_v3_csv-physionet_ts0.json` | 0.2 | 0.125 | 1080 | 358 | greedy_entropy | 1 / 1 / 2 / 1 | 0.0000 | 0.573 |
| `committed_v3_csv-physionet_ts0.json` | 0.2 | 0.125 | 1080 | 358 | random | 1 / 1 / 2 / 1 | 0.0000 | 0.573 |
| `committed_v3_cube_ts0.json` | 0.15 | 0.05375 | 1800 | 275 | greedy_entropy | 2 / 3 / 4 / 3 | 0.7980 | 0.596 |
| `committed_v3_cube_ts0.json` | 0.15 | 0.05375 | 1800 | 275 | random | 4 / 4 / 4 / 4 | 0.7071 | 0.644 |
| `committed_v3_fashionmnist_ts0.json` | 0.15 | 0.064286 | 6300 | 275 | greedy_entropy | 3 / 4 / 5 / 5 | 0.7778 | 0.311 |
| `committed_v3_fashionmnist_ts0.json` | 0.15 | 0.064286 | 6300 | 275 | random | 4 / 5 / 5 / 5 | 0.7778 | 0.454 |
| `committed_v3_G8_mnist_ts0.json` | 0.1 | 0.003929 | 6300 | 180 | greedy_entropy | 3 / 5 / 5 / 4 | 0.7879 | 0.929 |
| `committed_v3_G8_mnist_ts0.json` | 0.1 | 0.003929 | 6300 | 180 | random | 7 / 8 / 8 / 8 | 0.7879 | 0.929 |
| `committed_v3_image-imagenette_ts0.json` | 0.1 | 0.029851 | 1206 | 180 | greedy_entropy | 3 / 3 / 5 / 4 | 0.8586 | 0.620 |
| `committed_v3_image-imagenette_ts0.json` | 0.1 | 0.029851 | 1206 | 180 | random | 3 / 4 / 4 / 4 | 0.8384 | 0.549 |
| `committed_v3_mnist_ts0.json` | 0.1 | 0.003929 | 6300 | 180 | greedy_entropy | 3 / 4 / 4 / 3 | 0.7879 | 0.976 |
| `committed_v3_mnist_ts0.json` | 0.1 | 0.003929 | 6300 | 180 | random | 5 / 5 / 5 / 5 | 0.7879 | 0.881 |
| `committed_v3_tabular-adult_ts0.json` | 0.25 | 0.154229 | 4070 | 428 | greedy_entropy | 1 / 1 / 3 / 2 | 0.7576 | 0.240 |
| `committed_v3_tabular-adult_ts0.json` | 0.25 | 0.154229 | 4070 | 428 | random | 1 / 1 / 3 / 3 | 0.7576 | 0.454 |
| `committed_v3_tabular-MiniBooNE_ts0.json` | 0.15 | 0.07438 | 11706 | 275 | greedy_entropy | 1 / 1 / 5 / 3 | 0.7475 | 0.430 |
| `committed_v3_tabular-MiniBooNE_ts0.json` | 0.15 | 0.07438 | 11706 | 275 | random | 1 / 1 / 5 / 4 | 0.7778 | 0.477 |
| `committed_v3before_mnist_ts0.json` | 0.15 | 0.097143 | 6300 | 275 | eps_greedy_eps0.25 | 5 / 5 / 5 / 5 | 0.8384 | 0.335 |
| `committed_v3before_mnist_ts0.json` | 0.15 | 0.097143 | 6300 | 275 | eps_greedy_eps0.5 | 5 / 5 / 5 / 5 | 0.8081 | 0.359 |
| `committed_v3before_mnist_ts0.json` | 0.15 | 0.097143 | 6300 | 275 | greedy_entropy | 5 / 5 / 5 / 5 | 0.8687 | 0.311 |
| `committed_v3before_mnist_ts0.json` | 0.15 | 0.097143 | 6300 | 275 | random | 5 / 5 / 5 / 5 | 0.7475 | 0.477 |
| `committed_v3before_tabular-adult_ts0.json` | 0.25 | 0.155887 | 4070 | 428 | eps_greedy_eps0.25 | 1 / 1 / 4 / 2 | 0.7576 | 0.193 |
| `committed_v3before_tabular-adult_ts0.json` | 0.25 | 0.155887 | 4070 | 428 | eps_greedy_eps0.5 | 1 / 1 / 4 / 2 | 0.7576 | 0.193 |
| `committed_v3before_tabular-adult_ts0.json` | 0.25 | 0.155887 | 4070 | 428 | greedy_entropy | 1 / 1 / 3 / 2 | 0.7576 | 0.216 |
| `committed_v3before_tabular-adult_ts0.json` | 0.25 | 0.155887 | 4070 | 428 | random | 1 / 1 / 4 / 3 | 0.7576 | 0.335 |
| `committed_v3before_tabular-MiniBooNE_ts0.json` | 0.15 | 0.085143 | 11706 | 275 | eps_greedy_eps0.25 | 1 / 1 / 5 / 4 | 0.7273 | 0.311 |
| `committed_v3before_tabular-MiniBooNE_ts0.json` | 0.15 | 0.085143 | 11706 | 275 | eps_greedy_eps0.5 | 1 / 1 / 5 / 4 | 0.7374 | 0.454 |
| `committed_v3before_tabular-MiniBooNE_ts0.json` | 0.15 | 0.085143 | 11706 | 275 | greedy_entropy | 1 / 1 / 5 / 4 | 0.7273 | 0.430 |
| `committed_v3before_tabular-MiniBooNE_ts0.json` | 0.15 | 0.085143 | 11706 | 275 | random | 1 / 1 / 5 / 5 | 0.7879 | 0.477 |

The main, G8 and E7-BEFORE commits were re-made with `--force` (reasons: Task A changes the tier-3 order, Task B adds the multi-split `split` block); α, λ_ref, edges, μ and G are unchanged from round 1 (`results_v3/logs/r2_taskC_commit_invariance.log`). `committed_v3_image-imagenette_ts0.json` is new (Task D, first commit). The `committed_v3_am02_*` rows are the E9 α-rule commits (Task E, §8.7; new files; no MNIST or Imagenette row: refused). The G-rule gives G ≥ 2 at `dep` for every dataset except PhysioNet (G = 1 because λ_ref `dep` = 0).

## 9. Deviations, open issues, questions

**Resolved in round 2:** the authors chose option (b) below; the primitive is fixed (§12.1, `CHANGELOG.md`). The text below is the round-1 record.

**STOP-CONDITION QUESTION (instruction §7, item 5): a defect in the frozen p-value primitive.**
- **The defect:** `src/cafa/risk_control.py::_hb_pvalue_array` computes the Bentkus term as `_E * binom.cdf(np.ceil(n * rb).astype(int), n, alpha)`. For a 0/1 loss, r̂ = k/n with an integer error count k, but r̂ arrives as a float. n·r̂ can land a few ulps above k, so `ceil` gives k + 1 and the p-value is computed for one error more than observed.
- **Reproduction:** n = 197 rows with 17 errors, α = 0.15. With r̂ = 1 − mean(correct) = 0.08629441624365486, n·r̂ = 17.000000000000007 and p = 0.0270. With r̂ = mean(loss) = 0.08629441624365482, n·r̂ = 17.0 and p = 0.0149. `tests/test_frozen_hb_boundary.py` reproduces this; its exact-count test is `xfail(strict=True)` and fails on the frozen code.
- **Observed in the campaign:** Diabetes random, λ_ref 0.9, calibration draw 8, tier-3 level 37, stratum 4. The cascade gets p = 0.0270 > δ₃ = 0.025 and refuses; with the exact count it would certify. 4 of 100 draws of that cell differ (draws 8, 40, 66, 88): tier 3 certifies in 57 draws with the frozen p-values and in 61 with exact-count p-values (`results_v3/diagnostics/csv-diabetes_ts0_random_lr0.9_hb_boundary_draws.json`, §8.5).
- **Prevalence** (`scripts/scan_hb_ceil_boundary.py` → `results_v3/diagnostics/hb_ceil_boundary_scan.json`; 8,472 (n, k) pairs over the grid n ∈ {50, 100, 197, 250, 500, 1000, 2000, 3000, 5000}, α ∈ {0.10, 0.15, 0.20, 0.25}, all k with k/n < α):
  - r̂ = 1 − mean(correct), as in v3 tier 3 (`cafa.cascade.selective_pvalues`): off by one in 3,715 pairs (44 %); the p-value changes by more than 1 % in 3,621.
  - r̂ = mean(loss), as in the marginal LTT and IUT paths: off by one in 403 pairs (4.8 %); the p-value changes by more than 1 % in 397.
- **Validity:** the error only ever increases p (k + 1 instead of k), so every certificate issued with it is still valid. The effects are lower power and decisions that depend on summation order. The audit's exact binomial p-values (`cafa.localization.binom_upper_p`) take integer counts and are not affected.
- **Options (authors' decision):**
  - **(a)** Keep the primitive as frozen and report the results as computed: valid, slightly conservative.
  - **(b)** Fix the frozen primitive, e.g. `k = np.ceil(np.round(n * rb, 9))`. This changes the AAAI v2 numbers and needs your sign-off on editing a frozen file.
  - **(c)** Add a v3-only HB p-value that takes integer error counts, and use it in `cascade.py`, `commit_rules.escalation_order_from_probe` and the v3 tier-1/2 calls, leaving v2 byte-identical.
- **What (b) or (c) would require:** re-running all commits (`--force`; the probe-ordered tier-3 order uses these p-values), all sweeps and all repairs. Rollouts and caches are unaffected. Every Phase-3 number in this file was computed with the primitive as shipped.
- **Action taken:** on finding this I stopped all p-value-dependent work (CPU loops) and launched nothing new. Only the GPU rollout in §3, which does not use p-values, was left running.

Other deviations / open issues:
- **Zip contents:** the zip holds 33 files; the manifest table lists 12 scripts, not 13; the instruction says 38. All files the manifest lists are present.
- **Adult size in `PHASES_V3.md`:** 48,842 total / 19,537 heldout ignores the rows the loader drops. Actual: train 27,133, heldout 18,089.
- **Thermal throttling (§2):** every GPU job ran slower than the plan's estimates (MNIST / FashionMNIST greedy 15,491.9 s / 14,565.1 s; PHASES says ≈ 1 h).
- **Acceptance misses kept and reported:** CUBE 0.9598 and MiniBooNE 0.9158 full-observation train accuracy (§6.3). Test stratum violation above δ in 4 seed-0 cells (§8.5). Tier 1 not dominant on FashionMNIST and MiniBooNE greedy (§8.1). PhysioNet's `dep` commit degenerates to λ_ref = 0, G = 1 under α = 0.20.
- **Instruction §4.4 violation metric:** a draw counts as violating if a stratum's empirical risk on the fixed test split exceeds α. All 100 draws share one calibration pool and one test split, so the per-cell rate is a conditional frequency given those two samples, not an i.i.d. estimate of the Theorem-4 probability. §8.5 gives pooled (calpool + test) estimates next to it.
- **Policy AMP:** the Imagenette greedy policy uses fp16 autocast for its candidate passes (`policy_amp: true` in the cache meta; allowed by instruction §5). With it, about 24 % of picks differ from fp32 on 32 smoke rows (console-only, see §6.2); scores and `correct` come from fp32 passes either way.
- **Confirmed by review, not fixed** (they affect only the optional Phase 1d or are latent):
  - `run_pool_rollout_v3.py --orders-file` calls `load_orders(..., heldout_digest=None)`. Pass `heldout_digest=split_digest(pool["heldout_index"])` before Phase 1d.
  - `afabench_export_orders.py` emits column indices, but for one-hot tabular datasets (Adult) the replay expects feature-group indices.
  - `export_heldout_v3.py --out orders/...` writes feature arrays inside the repo, and `orders/` is not git-ignored. Use `$env:RESULTS_ROOT\orders_v3\` instead.
  - `data_v3._imagenette_arrays` and `download_data_v3.fetch_csvs` write non-atomically. This session's files are complete (13,394 images; heldout sizes in §6.1).
  - α ≤ design margin (resolved in round 2, Task E): `commit_v3.py` now stops with rc 7 and writes nothing whenever α ≤ the design margin 0.05, where `n_min(α, level, margin)` is undefined. Under the committed α rule this needs a probe floor of exactly 0 (not reached on any planned dataset); under the E9 rule (margin 0.02, grid 0.01) it is reached by MNIST (α = 0.03; §8.7, `results_v3/logs/r2am02_commit_mnist_na_ts0.log`).

## 10. What remains (exact commands; PowerShell, repo root, after `. .\set_env.ps1`)

1. **Seeds 1–2 for all eight datasets, Imagenette seeds 1–2 included (`TBD-RUN`): TinyGPU.** Everything is in **`hpc/README_v3.md`**:
   - what to push;
   - the data to copy or re-download;
   - the environment and `hpc/env.local.sh`;
   - the exact `sbatch` lines and the expected wall times;
   - the files to bring back;
   - the local round-3 commands (README §7: commit, sweep, repairs, `TABLE_E4_cascade_seeds.md`, and, added in round 3, the α-margin 0.02 / 0.10 commits and sweeps for seeds 1–2 and E10 over all seeds).

   The dry run of every array index is `results_v3/logs/hpc_dry_run.log`. Once the caches are back, Part 3b of `instruction_round3.md` (Task J) applies: run `check_caches_v3.py`, then the README §7 commands, then the final checks and the tag `aistats-v3-results`.
1b. **FashionMNIST predictor-upgrade repair (Task L, `TBD-RUN`): TinyGPU.**
   - Run the two `sbatch` lines of `hpc/README_v3.md` §8 (dry run: `tests/test_hpc_v3.py::test_hpc_dry_run_task_l_lines`).
   - Then, locally: `python scripts/check_caches_v3.py`, followed by `python scripts/run_repairs_v3.py --seeds 0 --datasets fashionmnist --repair-tag repair --tag r3L`.
   - This writes `results_v3/repair/fashionmnist_ts0_predictor_upgrade{,_random}.json`; report them as E7 MNIST is reported (§8.6).
2. **Tables and figures** (rerun whenever cells are added; seed 0 as in round 2):
   - `python scripts/make_tables_v3.py --metrics-dir $env:RESULTS_ROOT/metrics_v3 --output-dir results_v3/tables --lambda-ref-key dep --scheme uniform` (also writes `TABLE_E4_cascade_seeds.md`)
   - the same with `--output-dir results_v3/tables_inverse_info --scheme inverse_info`, and with `--lambda-ref-key 0.5|0.7|0.9 --output-dir results_v3/tables_e9_lambda_ref_<key>`
   - `python scripts/make_figures_v3.py --metrics-dir $env:RESULTS_ROOT/metrics_v3 --planted results_v3/planted --repair-dir results_v3/repair --output-dir results_v3/figures`
   - `python scripts/report_violations_v3.py --metrics-dir $env:RESULTS_ROOT/metrics_v3 --lambda-ref-key dep --output results_v3/diagnostics/r2_violations_dep.md`
   - round 3: `bash results_v3/logs/r3_postrun.sh` regenerates every table directory and the figures, writes E10 / E11 / F7 (`scripts/margin_analysis_v3.py`) and `TABLE_E9_alpha_margin` (`scripts/alpha_margin_summary_v3.py`), and checks that the K1 rerun matches round 2. It needs the round-2 archive `metrics_v3_round2`.
3. **E7 / E9 for further seeds** (`<ts>` = 1 or 2; round-2 code):
   - E7: `python scripts/commit_v3.py --dataset <ds> --train-seed <ts> --pool-dir F:/CAFA_results/pool_v2 --out-path configs/committed_v3before_<dsn>_ts<ts>.json` for mnist, tabular:MiniBooNE, tabular:adult (needs the v2 ts1/ts2 caches), then `python scripts/run_repairs_v3.py --seeds <ts> --tag r3`
   - E9 δ split: `python scripts/drive_v3.py --phase sweep --seeds <ts> --datasets csv:physionet --policies greedy_entropy --metrics-dir-name metrics_v3_dw --tag r3dw "--extra-args=--delta-weights 0.34,0.33,0.33"`
   - E9 G = 8: `python scripts/drive_v3.py --phase commit --seeds <ts> --datasets mnist --commit-prefix committed_v3_G8 --tag r3G8 "--extra-args=--n-buckets 8"`, then `--phase sweep` with the same `--commit-prefix` and `--metrics-dir-name metrics_v3_G8`
   - E9 α rule: `python scripts/drive_v3.py --phase commit --seeds <ts> --commit-prefix committed_v3_am02 --tag r3am02 "--extra-args=--alpha-margin 0.02 --alpha-grid 0.01"` (MNIST stops with rc 7, §8.7; run it last or leave it out), then `--phase sweep --seeds <ts> --commit-prefix committed_v3_am02 --metrics-dir-name metrics_v3_alpha_margin02 --tag r3am02`
   - Diagnostics for a cell that fails the certified criterion: `python scripts/diagnose_violation_v3.py --dataset <ds> --policy <pol> --train-seed <ts> --lambda-ref-key dep --output results_v3/diagnostics/<dsn>_ts<ts>_<pol>_dep.json` (multi-split).
4. **Optional Phase 1d (AFABench GDFS / AACO): `TBD-RUN`** (no AFABench `uv` environment here). The two latent items of §9 that affected it are fixed in round 2 (§12.6): `export_heldout_v3.py` now writes to `$RESULTS_ROOT\orders_v3\{dsname}_ts{ts}_heldout.npz` by default, and `run_pool_rollout_v3.py --orders-file` checks the heldout digest. Then follow `PHASES_V3.md` 1d: `python scripts/export_heldout_v3.py --dataset csv:physionet --train-seed 0`, run `scripts/afabench_export_orders.py` in the AFABench environment, and replay with `python scripts/run_pool_rollout_v3.py --dataset csv:physionet --train-seed 0 --orders-file $env:RESULTS_ROOT/orders_v3/physionet_ts0_gdfs.npz --policy-token afabench_gdfs`. The column-index vs feature-group issue of `afabench_export_orders.py` for one-hot datasets (Adult, §9) remains open.
5. **Resume after any interruption:** rerun the same `drive_v3.py` / `run_repairs_v3.py` command. Each skips cells whose output exists and stops at the first non-zero return code (`results_v3/run_log.jsonl`, `results_v3/logs/`).

## 11. Paper-facing numbers (seed 0, λ_ref `dep`, uniform costs; round 2 = HB fix + 5 splits × 20 draws; `old → new` = round 1 → round 2; `TBD-RUN` where not available)

| quantity (plan abstract / §7) | value | source |
|---|---|---|
| certified deployment % | 100 % in each of the 16 seed-0 cells (14 unchanged; Imagenette new) | `results_v3/tables/TABLE_E4_cascade.csv` (`certified_deployment`) |
| tier-1 % | MNIST 100 / 100, CUBE 100 / 100 → 100 / 99, Adult greedy 100, PhysioNet 100 / 100, MiniBooNE random 73 → 26, FashionMNIST random 58 → 12, FashionMNIST greedy 35 → 12, MiniBooNE greedy 4 → 1, Adult random 0, Diabetes 0 / 0 (greedy / random); Imagenette 20 / 9 (new); mean over the 14 round-1 cells 62.1 % → 53.6 %, over all 16 cells 48.7 % | new: same (`tier1`); old: `results_v3/round1/tables/TABLE_E4_cascade.csv`; per-cell old → new and both means: `results_v3/diagnostics/r2_old_vs_new_dep.md` |
| cost premium (cascade / marginal) | tier-1 cells: MNIST 1.048 → 1.046 / 1.105 → 1.085, CUBE 1.387 → 1.383 / 1.154 → 1.162, Adult greedy 1.220 → 1.253; Imagenette 5.385 / 6.072 (tier 3 majority); PhysioNet undefined (marginal cost 0) | same (`cost_premium`); old: `results_v3/round1/tables/TABLE_E4_cascade.csv` (`results_v3/diagnostics/r2_old_vs_new_dep.md`) |
| answered fraction (mean over draws; tier-1 draws count as 1.0) | Diabetes 0.822 → 0.817 / 0.890 → 0.892, Adult random 0.897 → 0.902, MiniBooNE greedy 0.973 → 0.965, FashionMNIST greedy 0.987 → 0.982, FashionMNIST random 0.995 → 0.985, MiniBooNE random 0.996 → 0.985; Imagenette 0.983 / 0.963 | same (`answered_fraction`); old: `results_v3/round1/tables/TABLE_E4_cascade.csv` (`results_v3/diagnostics/r2_old_vs_new_dep.md`) |
| raw test stratum-violation frequency (pooled; no threshold since round 2) | FashionMNIST 0.350 → 0.100 / 0.580 → 0.100, MiniBooNE 0.110 → 0.020 / 0.120 → 0.030, CUBE greedy 0.000 → 0.010, Adult 0.000 → 0.010 / 0.000 → 0.020, Diabetes random 0.010 → 0.000, Imagenette 0.050 / 0.000 (new; greedy per split up to 0.150), all others 0.000; per split at most 0.450 / 0.500 (FashionMNIST, split 778) | same (`test_stratum_violation`, `violation_by_split`); `results_v3/diagnostics/r2_violations_dep.md`; old: `results_v3/round1/tables/TABLE_E4_cascade.csv` |
| certified violation (new) | ≤ 0.010 in every cell of 16 (0.010: FashionMNIST random, MiniBooNE greedy; Imagenette 0.000) vs δ + 0.05 = 0.15 | same (`certified_violation`) |
| max_excess_se (new; mean over draws) | negative in every cell of 16, −6.616 (PhysioNet) … −3.152 (Imagenette greedy) | same (`max_excess_se`) |
| max stratum risk / α of marginal CAFA (mean over draws) | 0.722 → 0.715 (PhysioNet) … 2.204 → 2.198 (Diabetes greedy); MNIST 0.954 → 0.952 / 0.920 → 0.949; FashionMNIST 1.567 → 1.533 / 1.509 → 1.438; MiniBooNE 1.708 → 1.654 / 1.183 → 1.143; Imagenette 1.308 / 1.245 | `results_v3/tables/TABLE_E2_blindness.csv`; old: `results_v3/round1/tables/TABLE_E2_blindness.csv` (`results_v3/diagnostics/r2_old_vs_new_dep.md`) |
| hidden certified violation of marginal CAFA (new) | 1.000 in Diabetes, FashionMNIST, MiniBooNE (both policies) and Adult greedy; Adult random 0.210; CUBE 0.320 / 0.500; MNIST 0.020 / 0.000; Imagenette 0.520 / 0.350; PhysioNet 0.000 | same (`hidden_certified_violation_rate`) |
| deepest-stratum verdicts (split 778) | unchanged: `type_II` Diabetes (both), `unresolved` Adult random, `feasible` the other 11 and Imagenette (both); agreement over splits 5/5 except MiniBooNE greedy 2/5 and Adult random 2/5 | `results_v3/tables/TABLE_E3_audit.csv`, `TABLE_E4_cascade.csv` (`verdict_agreement`) |
| E5 level / power | unchanged by the fix: false-failure ≤ 0.000, cascade violation ≤ 0.005, power 0.926 / 0.843 at n_kΔ² = 2.5, 1.000 at ≥ 10, unsafe given escalation 0.000; escalation rate at n_k 250 0.866 → 0.881 | `results_v3/planted/PLANTED_VALIDATION.md`, `results_v3/logs/r2_phase2_planted_validation.log` |
| E5 study D (test noise, new) | true deepest-stratum risk α − 0.004, test n_k ≈ 2,492, 10 blocks × 20: D2 (powered calibration) certification 0.880, true violation 0.000, raw 0.235 (blocks 0.00–0.55), certified 0.005; D1 (as specified) certification 0.055, raw 0.020, certified 0.000 | `results_v3/planted/PLANTED_VALIDATION.md` |
| E7 before → after (MNIST, predictor upgrade) | unchanged: `type_II` → `feasible`; family minimum 0.295 → 0.011; tier-1 share 0.00 → 1.00; violation 0.00 → 0.00 (certified 0.00 → 0.00) | `results_v3/repair/mnist_ts0_predictor_upgrade.json` |
| Imagenette seed 0 | heldout full-acquisition accuracy 0.971818 (both policies); α 0.10; tiers 1/3 = 0.20/0.80 (greedy), 0.09/0.91 (random); certified deployment 1.00; raw violation 0.050 / 0.000; certified 0.000 / 0.000 | `results_v3/tables/TABLE_E4_cascade.csv`, `results_v3/logs/r2_taskD_verify_greedy_cache.log` |
| deployed cost / T (round 3) | 0.000 (PhysioNet, both) … 1.000 (Diabetes both, Adult random). Tier-1 cells: MNIST 0.075 / 0.184, CUBE 0.289 / 0.576, Adult greedy 0.213. Imagenette 0.884 / 0.940, FashionMNIST 0.929 / 0.926, MiniBooNE 0.993 / 0.862. Marginal CAFA 0.000 … 0.496; Mondrian oracle 0.000 … 0.548 | `results_v3/tables/TABLE_E4_cascade.csv` (`*_cost_over_T`) |
| tier-2 would-certify share (round 3) | 0.000 in every cell of every table directory, and 0 of 61,720 draw records. Equal to the tier-2 share by construction; tier 2 never mattered | same (`tier2_would_certify`); `results_v3/logs/r3_handoff_facts.log`, `r3_tier2_draw_count.log` |
| cascade cost / ex-post stratum-safe oracle (round 3) | intrinsic: Diabetes (oracle infeasible, 1.000 / 1.000). Sample-limited: FashionMNIST 2.197 / 1.995, Imagenette 3.806 / 4.974, MiniBooNE random 3.743. Near-oracle: MNIST 1.041 / 1.092, CUBE 1.264 / 1.112, Adult greedy 1.079, PhysioNet 0/0. Mixed: Adult random 1.169 (3.595 on feasible draws), MiniBooNE greedy 1.333 (2.761) | `results_v3/tables/TABLE_E4_cost_gap.{md,csv}` (§13.4) |
| E10: tier 1 predicted by the deepest-stratum margin (round 3) | 320 points: Spearman ρ 0.905, 318/320 within ±0.2. Key `dep`: ρ 0.935, 80/80 | `results_v3/tables/TABLE_E10_margin_summary.json`, `results_v3/figures/F7_margin.pdf` |
| E9 α margin 0.10 (round 3) | Tier 1 = 1.00 in every cell except Diabetes (greedy tier 3 1.00; random tier 1 0.26). Certified violation 0.000 in all 16 cells. Adult degenerate at α 0.30 | `results_v3/tables/TABLE_E9_alpha_margin.md`, `results_v3/tables_e9_alpha_margin10/` |
| E11 calibration size (round 3) | Tier-1 share at cal_frac 0.25 / 0.5 / 1.0. FashionMNIST greedy 0.12 / 0.12 / 0.40; Imagenette greedy 0.09 / 0.20 / 0.40, random 0.03 / 0.09 / 0.20; MiniBooNE random 0.10 / 0.26 / 0.20; CUBE random 0.69 / 0.99 / 1.00. 1.0 = one draw per split | `results_v3/tables/TABLE_E11_calfrac.md` |
| E7 FashionMNIST predictor upgrade (round 3) | TBD-RUN on the cluster. The laptop smoke ran the greedy rollout for 256 rows in 361 s; projected linearly that is ≈ 11 h for the 28,000 heldout rows, and the GPU was thermally throttled. | `hpc/README_v3.md` §8, `results_v3/logs/r3_taskL_smoke_*.log` |
| seeds 1–2 (all quantities) | TBD-RUN (cluster package `hpc/README_v3.md`, Task F) | — |
| external AFABench policies | TBD-RUN | — |

## 12. Round 2

Round 2 follows `instruction_round2.md` (Tasks A → F; decisions of its §0 are the authors'). Start 2026-10-03 00:55 local (UTC+2).

### 12.1 Task A — HB boundary fix and its one-to-one impact

**Tag.** `aaai27-submission` → `550f8e2` (annotated; "code as used for the AAAI-27 submission (HB boundary rounding defect present)"). `550f8e2` is `git merge-base main aistats-v3`, the commit the branch was created from. The instruction's alternative, the first parent of `b1caf84`, is `8ddb7dc`; it differs from `550f8e2` only by `S11_answer.md` and one `.gitignore` line (no code) and is not tagged.

**Patch** (`git diff aaai27-submission -- src/cafa/risk_control.py`: one line). `_hb_pvalue_array`: `k = np.ceil(n * rb).astype(int)` → `k = np.ceil(np.round(n * rb, 9)).astype(int)`. No other `ceil(n * …)` exists in `risk_control.py` or `risk_control_ext.py` (grep over `src/cafa/`).

**Tests.**
- `tests/test_frozen_hb_boundary.py`: `xfail(strict=True)` removed; (197, 17, 0.15) gives 0.0149 for both summation orders; every (n, k) pair of the `scripts/scan_hb_ceil_boundary.py` grid (8,472 pairs × 2 summation orders) equals the exact-count value to 1e-12 absolute and 1e-11 relative (the absolute bound alone cannot see an off-by-one at tiny p). Evaluated against the pre-fix primitive these assertions fail in 3,768 of 16,944 evaluations (absolute alone: 1,009); fixed primitive: 0, worst relative error 6.98e-13. Campaign case p = 0.027047 → 0.014856 (`results_v3/logs/r2_taskA_boundary_test_vs_prefix_primitive.log`).
- `tests/test_risk_control.py`: untouched; passes. None of its assertions encoded the defect.
- Whole suite: `91 passed in 225.01s (0:03:45)`, 0 xfailed (`results_v3/logs/r2_taskA_pytest_full_suite.log`; round 1: 88 passed, 1 xfailed).
- `CHANGELOG.md` (repo root): one entry (date, defect, direction, fix, tag, round-1 numbers superseded).
- Commit `5089d5e`.

**Prevalence scan, rerun.** On the fixed primitive no grid pair differs from the exact-count p-value by more than 1 % (`results_v3/diagnostics/hb_ceil_boundary_scan_postfix.json`). Correction to the round-1 numbers of §9: the scan's exact reference was floored at 1e-300, while the primitive floors at 2.2e-308, so pairs with p < 1e-300 were counted as "differs" although only the floors differed. With the floor corrected (`scripts/scan_hb_ceil_boundary.py`) the pre-fix counts are: off-by-one 403 (mean(loss)) / 3,715 (1 − mean(correct)), unchanged; p differs by > 1 % in 397 → **371** and 3,621 → **3,393** pairs (`results_v3/logs/r2_taskA_scan_hb_ceil_boundary_prefix_corrected_floor.log`).

**One-to-one impact (A.6; round-1 protocol: test seed 778, the same 100 draw ids).**
- Re-commits: `drive_v3.py --phase commit --seeds 0 --force --tag r2hbfix` (reason: the probe-ordered tier-3 order uses HB p-values). Compared with the round-1 commits (`results_v3/round1/configs/`), only `created` and `escalation.*.order` differ. The order changed in 39 of 56 (policy, λ_ref) entries; its first level changed in 2: PhysioNet greedy λ_ref 0.9 (answered fraction 0.383 → 0.430) and MiniBooNE greedy `dep` (0.573 → 0.430) (`results_v3/diagnostics/r2_hbfix_decision_flips.json`).
- Sweeps: the 14 seed-0 cells with the fixed primitive, the round-1 sweep code and the round-1 protocol, run as four parallel driver processes from a detached worktree at `5089d5e` (so that the Task-B edits could not leak in) → `$RESULTS_ROOT\metrics_v3_hbfix_single\`. Ledger `r2hbfix:sweep:*` in `results_v3/run_log.jsonl` (14 runs, rc 0, 4,358.4 s summed); logs `results_v3/logs/r2hbfix_sweep_*.log`, `driver_r2hbfix_sweep_g{0..3}.out`.
- Comparison: `python scripts/compare_decisions_v3.py --old-dir $RESULTS_ROOT/metrics_v3_round1 --new-dir $RESULTS_ROOT/metrics_v3_hbfix_single --old-commits results_v3/round1/configs --new-commits configs --output results_v3/diagnostics/r2_hbfix_decision_flips` (scheme `uniform`). A flip is a draw whose deployed (tier, rule, parameter) differs.

**Decision-flip table** (rows with at least one flip; the other 32 of the 56 (cell, λ_ref) rows have 0 flips; full table `results_v3/diagnostics/r2_hbfix_decision_flips.md`):

| dataset | policy | λ_ref | draws | flips | tier changed | tiers 1/2/3/none old → new | cert old → new | raw viol old → new |
|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | dep | 100 | 31 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| csv-diabetes | random | 0.9 | 100 | 18 | 4 | 0.00/0.00/0.57/0.43 → 0.00/0.00/0.61/0.39 | 0.57 → 0.61 | 0.000 → 0.000 |
| csv-diabetes | random | dep | 100 | 1 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.010 → 0.010 |
| csv-physionet | greedy_entropy | 0.9 | 100 | 16 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| csv-physionet | random | 0.9 | 100 | 17 | 0 | 0.05/0.00/0.95/0.00 → 0.05/0.00/0.95/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| cube | greedy_entropy | 0.9 | 100 | 11 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| cube | random | 0.9 | 100 | 18 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| fashionmnist | greedy_entropy | 0.5 | 100 | 1 | 0 | 1.00/0.00/0.00/0.00 → 1.00/0.00/0.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| fashionmnist | greedy_entropy | 0.7 | 100 | 1 | 0 | 0.97/0.00/0.03/0.00 → 0.97/0.00/0.03/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| fashionmnist | greedy_entropy | 0.9 | 100 | 2 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| fashionmnist | greedy_entropy | dep | 100 | 1 | 0 | 0.35/0.00/0.65/0.00 → 0.35/0.00/0.65/0.00 | 1.00 → 1.00 | 0.350 → 0.350 |
| fashionmnist | random | 0.7 | 100 | 2 | 0 | 1.00/0.00/0.00/0.00 → 1.00/0.00/0.00/0.00 | 1.00 → 1.00 | 0.340 → 0.340 |
| fashionmnist | random | 0.9 | 100 | 3 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| fashionmnist | random | dep | 100 | 8 | 0 | 0.58/0.00/0.42/0.00 → 0.58/0.00/0.42/0.00 | 1.00 → 1.00 | 0.580 → 0.580 |
| mnist | greedy_entropy | 0.7 | 100 | 7 | 0 | 1.00/0.00/0.00/0.00 → 1.00/0.00/0.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| mnist | random | 0.7 | 100 | 1 | 0 | 1.00/0.00/0.00/0.00 → 1.00/0.00/0.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| mnist | random | dep | 100 | 2 | 0 | 1.00/0.00/0.00/0.00 → 1.00/0.00/0.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| tabular-adult | greedy_entropy | 0.9 | 100 | 16 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| tabular-adult | random | 0.9 | 100 | 4 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.010 → 0.010 |
| tabular-adult | random | dep | 100 | 15 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.000 → 0.000 |
| tabular-MiniBooNE | greedy_entropy | 0.9 | 100 | 4 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.180 → 0.210 |
| tabular-MiniBooNE | greedy_entropy | dep | 100 | 3 | 0 | 0.04/0.00/0.96/0.00 → 0.04/0.00/0.96/0.00 | 1.00 → 1.00 | 0.110 → 0.130 |
| tabular-MiniBooNE | random | 0.9 | 100 | 2 | 0 | 0.00/0.00/1.00/0.00 → 0.00/0.00/1.00/0.00 | 1.00 → 1.00 | 0.070 → 0.070 |
| tabular-MiniBooNE | random | dep | 100 | 2 | 1 | 0.73/0.00/0.27/0.00 → 0.74/0.00/0.26/0.00 | 1.00 → 1.00 | 0.120 → 0.120 |

Total: **186 of 5,600** (cell, λ_ref, draw) decisions changed, 5 of them changed the tier (Diabetes random 0.9: 4 draws none → tier 3; MiniBooNE random `dep`: 1 draw tier 3 → tier 1). Summary-level changes: certified deployment Diabetes random λ_ref 0.9 0.57 → 0.61 (as predicted in §9 from the exact-count replay, `results_v3/diagnostics/csv-diabetes_ts0_random_lr0.9_hb_boundary_draws.json`); raw test violation MiniBooNE greedy 0.9 0.180 → 0.210 and `dep` 0.110 → 0.130; tier-1 share MiniBooNE random `dep` 0.73 → 0.74. Every other tier share, certification and violation rate is unchanged.

**Archive (nothing deleted).**
- Moved: `$RESULTS_ROOT\metrics_v3\*.json` (14) → `$RESULTS_ROOT\metrics_v3_round1\`; `metrics_v3_G8\` and `metrics_v3_dw\` → `metrics_v3_round1\metrics_v3_G8\`, `metrics_v3_round1\metrics_v3_dw\`. sha256 of all 16 files: `results_v3/round1/metrics_v3_round1.sha256` (re-check at the end of round 2: §12.7).
- Copied to `results_v3/round1/`: `tables/`, `tables_inverse_info/`, `tables_e9_lambda_ref_{0.5,0.7,0.9}/`, `tables_e9_delta_weights/`, `tables_e9_G8/`, `figures/`, `repair/`, `diagnostics/`, and `configs/` (the 11 round-1 committed JSONs: 7 main, G8, 3 E7 BEFORE).

**Imagenette seed-0 greedy rollout.** Found dead at the start of round 2: last log line `[rgb rollout] 1296/5358 (5723s)`, last write 2026-10-02 01:55:57, no cache, no return-code line. The partial log is kept as `results_v3/logs/rollouts_image-imagenette_greedy_entropy_ts0_round1_died.log`. Relaunched with the §10 command: the first attempt (00:55) did not start because `Start-Process` split the `--extra-args` value at its spaces (driver usage error, console only); the second attempt runs since 2026-10-03 01:15:09 (`results_v3/logs/r2_background_jobs.log`, `results_v3/logs/driver_round2_imagenette_greedy.out`).

### 12.2 Task B — multi-split protocol and noise-aware violation metrics

**Protocol** (`configs/experiment_v3.yaml`, `protocol_v3`): `test_seeds: [778, 779, 780, 781, 782]`; `n_draws: 100` is the total, 20 per split (`splits_v3.draws_per_split` raises unless it divides); `test_seed: 778` stays the primary split. α, δ, γ, the δ split, the grids and the committed rules are unchanged.

**Code** (commit of this section; every changed file is listed in §4-style form here):
- `src/cafa/splits_v3.py`: `v3_positions_multi(n_heldout, …, test_seeds)` (one positions dict per seed, same probe), `draws_per_split`, `split_draw_id(s, d) = s·1000 + d` (`SPLIT_DRAW_STRIDE = 1000`, requires d < 1000). Draw d of split index s uses RNG seed 2,000,000 + s·1000 + d, so no draw seed is reused across splits, and split index 0 (seed 778) reuses the round-1 draw ids 0–19 on the round-1 calibration pool.
- `scripts/commit_v3.py`: the `split` block adds `test_seeds`, `n_draws`, `draws_per_split`, `draw_id_stride` and `by_test_seed` (per seed: split index, calpool/test sizes and sha256 digests); nothing else in the commit depends on the test seeds. `diff_commits` helper.
- `scripts/run_cascade_sweep.py`: loops over the committed splits (digests checked against the commit); per λ_ref key `audit` = split 778, `audit_by_split`, `deepest_verdict_by_split`, `deepest_verdict_agreement` (x of 5); per draw `split_seed`, `split_index`, `draw` (the draw id); for the cascade `test_errors_by_stratum`, `test_n_by_stratum` (answered rows for tier 3), `test_pvalue_min` = min over k ∈ K_cal of `binom_upper_p(e_k, n_k, α)`, `certified_violation` = (`test_pvalue_min` ≤ 0.05; False when nothing is deployed), `max_excess_se` = max over k ∈ K_cal of (R̂_k − α)/√(α(1−α)/n_k); the same three for marginal CAFA (`hidden_*`) and every baseline (`stratum_*`); summaries pooled over the 100 draws plus `by_split` (same fields per split). The raw fields are computed as in round 1. A commit whose splits differ from `protocol_v3.test_seeds` is refused unless `--test-seeds` (with `--out-dir`) is given explicitly.
- `scripts/repair_experiment.py`: the same multi-split protocol and noise-aware metrics; JSON layout unchanged plus `cascade.by_split`, `deepest_verdict_by_split`, `deepest_verdict_agreement`; refuses a commit without the protocol's splits.
- `scripts/make_tables_v3.py`: E4 + `violation_by_split` (min–max over splits), `certified_violation`, `max_excess_se` (mean), `verdict_agreement` (x/5); E2 + `hidden_certified_violation_rate`; E6 + `stratum_certified_violation_rate`; files written as UTF-8. `scripts/make_figures_v3.py`: `F6_violations.pdf` (raw pooled rate with the min–max over splits, certified rate, lines at δ and δ + 0.05).
- `scripts/diagnose_violation_v3.py`: multi-split layout (per-split digest/size/alignment checks, rules per split, flagged draws on their own split, test p-values recomputed and compared with the sweep).
- `scripts/planted_validation.py`: study D (below). `scripts/check_sweep_equivalence_v3.py` (new).
- Note on the metric as specified: `test_pvalue_min` is a minimum over the K_cal strata without a multiplicity adjustment.

**Refactor check.** On the single-split (Task-A) commits, the rewritten sweep reproduces every round-1 field of 4 cells exactly: cube greedy, PhysioNet random, Adult random, MNIST greedy (2,800 draw records, both cost schemes; `results_v3/logs/r2_taskB_sweep_equivalence_single_split.log`; run before the stale-commit guard existed; to reproduce now, add `--test-seeds 778 --out-dir <dir>`).

**Tests.** `tests/test_multisplit_v3.py` (11 tests): config; per-split disjointness, coverage, determinism, shared probe, split 778 = round-1 split; distinct draw ids and RNG seeds, round-1-compatible ids for split 0, calibration draws inside their own calpool; the commit's split block; **commit invariance** against two fixtures, commits of the same deterministic synthetic cache made with the round-1 code (`6466118`) and with the Task-A code (`5089d5e`) (`tests/fixtures/`): vs Task-A code only `split` differs (and only by added keys), vs round-1 code additionally `escalation.*.order`; the sweep's per-split fields with the noise-aware values recomputed from the recorded counts (cascade), from per-stratum risks and split sizes (marginal), and certified ⇒ raw (baselines); refusal of stale single-split commits by sweep and repair; study D's rule evaluation against `cafa.cascade.apply_rule` for all three tiers; study D's expected rates against binomial enumeration; a small study D (2 × 3 replicates per configuration). `tests/test_v3_scripts.py`: sweep draw counts 4 → 5 and 1 → 5 (they must divide over 5 splits); nothing else changed. Whole suite: `102 passed in 293.34s (0:04:53)` (`results_v3/logs/r2_taskB_pytest_full_suite.log`).

**Review** (`results_v3/diagnostics/r2_review_taskB.json`). A workflow of 11 agents (4 reviewers, one per file group, each against the Task-B spec, plus one adversarial verifier per finding) returned 7 findings, 3 confirmed. Two of the confirmed findings are the same defect: sweep and repair silently fell back to one split for a commit without `test_seeds`; both now refuse. The third: the sweep test never exercised the certified-violation branch, and study D's budget/escalation evaluation was untested; tests added above. Of the 4 rejected findings, 1 is a third report of the fallback, judged intended behaviour by its verifier and fixed anyway. Two concern hardening that was applied anyway: `--out-dir` is now required with `--test-seeds`, and study D raises for an infeasible planting (T ≤ 3). The last says the D1 checks of the small study-D test are weak. They are, because D1 rarely certifies (5.5 % of replicates in the full run, §7).

**Study D design** (`scripts/planted_validation.py`, appendix evidence for the metric change). Two strata; the deepest is homogeneous with TRUE full-information risk α − 0.004 = 0.146 (r_easy solved analytically; checked by β-quadrature, which also gives the exact true risk of every deployed rule). Replicates come in blocks of 20 that share one test split with n_k ≈ 2,500 in the deepest stratum; 10 blocks = 200 replicates. Two calibration sizes:
- **D1 (as specified):** per block a calibration pool with n_k ≈ 2,500 and 20 draws of 50 % of it (the real protocol's sizes). At these sizes the cascade rarely certifies a rule 0.004 below α (full run: 11 of 200 replicates, §7), so D1's rates stay small whatever the metric.
- **D2 (powered calibration):** each replicate draws a fresh calibration sample with n_k ≈ 90,000, so the cascade certifies rules whose true risk sits just below α. This is the regime in which test-split noise alone produces raw "violations".
Both are reported, with the noise-free expected raw and certified rates computed from the deployed rules' true risks and the test n_k.

**Study D results** (`results_v3/planted/PLANTED_VALIDATION.md`, `planted_validation.csv`; full run §7):
- **D1 (as specified; calibration n_k ≈ 1,250 per draw, test n_k ≈ 2,492):** the cascade certifies in 11 of 200 replicates (rate 0.055). True violation 0.000; raw test violation 0.020 (per block 0.00–0.15; expected 0.016); certified violation 0.000 (expected 0.001). At the real protocol's sizes, a stratum 0.004 below α is almost never certified, so the raw rate stays below δ here.
- **D2 (powered calibration; n_k ≈ 89,984 per draw, same test sizes):** certification 0.880; deployed rules' true deepest-stratum risk 0.146–0.149 (all ≤ α); **true violation 0.000** (≤ δ); **raw test violation 0.235** (> δ; per block 0.00–0.55; expected 0.269); **certified violation 0.005** (≤ δ + 0.05; expected 0.013); mean max_excess_se −0.661.
- So when the deployed rules are valid but within a few thousandths of α, test-split noise alone puts the raw rate above δ (and makes it vary from 0 to 0.55 between blocks that share a test split), while the certified-violation rate stays near its nominal level.

### 12.3 Task C — Phase 3 rerun with the round-2 code (seed 0, 14 cells)

**Commits** (all `--force`; reason: Task A changes the tier-3 order, Task B adds the `split` block). `drive_v3.py --phase commit --seeds 0 --force --tag r2` (7 datasets); `drive_v3.py --phase commit --seeds 0 --datasets mnist --force --tag r2G8 --commit-prefix committed_v3_G8 "--extra-args=--n-buckets 8"`; the three E7 BEFORE commits `commit_v3.py --dataset <ds> --train-seed 0 --pool-dir F:/CAFA_results/pool_v2 --out-path configs/committed_v3before_<dsn>_ts0.json --force` (logs `results_v3/logs/r2_commit_*`, `r2G8_commit_*`, `r2_commit_before_*`). Invariance on the real data (`results_v3/logs/r2_taskC_commit_invariance.log`): the 7 main commits differ from the Task-A commits only by added `split` keys; G8 and the BEFORE commits (not re-committed in Task A) differ from round 1 only by added `split` keys and tier-3 orders (G8: 3 of 8 orders; BEFORE: 16 of 16 each).

**Sweeps** (`$RESULTS_ROOT\metrics_v3\`, the round-1 files having been moved, §12.1): 4 parallel `drive_v3.py --phase sweep --seeds 0 --tag r2 --datasets …` processes (ledger `r2:sweep:*`, 14 runs, rc 0; logs `results_v3/logs/r2_sweep_*.log`, `driver_r2_sweep_g{0..3}.out`). E9: `r2dw:sweep:csv:physionet:greedy_entropy:ts0` (`--delta-weights 0.34,0.33,0.33` → `metrics_v3_dw`) and `r2G8:sweep:mnist:greedy_entropy:ts0` (→ `metrics_v3_G8`). E7: `scripts/run_repairs_v3.py --seeds 0 --tag r2 --force` (new ledgered runner; 10 runs, rc 0). These ran as one chain (`results_v3/logs/driver_r2_e9_e7_chain.out`) concurrently with the sweeps, the planted rerun and the Imagenette rollout.

**Tables / figures / reports:** `results_v3/logs/r2_taskC_make_tables.log`; figures `results_v3/figures/` (F5 redrawn from the round-2 planted CSV in commit `8e1858e`); `scripts/report_violations_v3.py` → `results_v3/diagnostics/r2_violations_{dep,lr0.5,lr0.7,lr0.9}.{md,json}` (no cell fails an acceptance check at any λ_ref key); `results_v3/diagnostics/r2_e9_lambda_ref_summary.md`.

**Acceptance (headline, `dep`):** certified deployment 1.00 in all 14 cells; certified violation ≤ 0.010 ≤ δ + 0.05 in every cell; mean max_excess_se < 0 in every cell (max −3.273). So `scripts/diagnose_violation_v3.py` was not required; it was run once on FashionMNIST random `dep` (largest single-split raw rate) to check the multi-split diagnostic on real data (§8.5). **By-split ranges of the cells over δ in round 1:** FashionMNIST greedy 0.000–0.450, FashionMNIST random 0.000–0.500, MiniBooNE greedy 0.000–0.100, MiniBooNE random 0.000–0.150; in each case the maximum is split 778 and the other four splits are ≤ 0.050 (§8.5).

### 12.4 Task D — Imagenette seed 0

- **D.1, greedy cache.** The round-1 rollout had died (§12.1). The relaunch (`drive_v3.py --phase rollouts --seeds 0 --datasets image:imagenette --policies greedy_entropy "--extra-args=--batch-size 16 --policy-amp"`) ran 2026-10-03 01:15:11 → 08:34:39 local: 26,368.4 s, rc 0 (ledger `rollouts:image:imagenette:greedy_entropy:ts0`; log `results_v3/logs/rollouts_image-imagenette_greedy_entropy_ts0.log`). The GPU was thermally throttled for most of the run (≈ 5 s/row; 210 MHz at 92–93 °C in the `nvidia-smi` readings taken at 03:43 and 04:44, console). Verification (`results_v3/logs/r2_taskD_verify_greedy_cache.log`): the cache loads; 5,358 rows, T = 49; meta `max_rows` None, `policy_amp` true, `batch_size` 16, `cand_chunk` 4; **heldout full-acquisition accuracy 0.971818** (§6.3).
- **D.2, random rollout.** `drive_v3.py --phase rollouts --seeds 0 --datasets image:imagenette --policies random "--extra-args=--batch-size 16"`, queued behind the greedy run (`results_v3/logs/driver_round2_imagenette_random_chain.out`): 1,481.7 s, rc 0. Greedy = random full-acquisition accuracy: |Δ| = 0.000e+00, same labels, same `correct[:, T]` → PASS (`python scripts/check_caches_v3.py --v2-dir F:/CAFA_results/pool_v2 --csv results_v3/phase1_caches.csv`, `results_v3/logs/r2_taskD_check_caches_v3.log`).
- **D.3.** Commit `r2:commit:image:imagenette:na:ts0` (α = 0.10 from probe floor 0.029851; λ_ref `dep` 0.8586 / 0.8384; G at `dep` 4 / 4). Sweeps `r2:sweep:image:imagenette:{greedy_entropy,random}:ts0` (25.1 s / 24.6 s). E7 policy change `r2:repair:image:imagenette:policy_change:ts0` (§8.6). Tables and figures regenerated with all 16 cells (`results_v3/logs/r2_final_make_tables.log`, `r2_final_make_figures.log`). Imagenette has uniform costs only; `tables_inverse_info` keeps 10 cells. Result (§8.1): certified deployment 1.00; tiers 1/3 = 0.20/0.80 (greedy) and 0.09/0.91 (random); raw violation 0.050 (by split 0.000–0.150) / 0.000; certified violation 0.000 / 0.000; verdict agreement 5/5. Under the E9 α rule Imagenette is not committed (α 0.05 ≤ design margin, rc 7; §8.7).

### 12.5 Task E — E9 α-rule sensitivity (seed 0)

- **Code:** `scripts/commit_v3.py` gains `--alpha-margin` (default 0.05) and `--alpha-grid` (default 0.05), implemented in the v3-local `alpha_from_floor(floor, margin, grid)`. With the defaults the commit still calls `cafa.data.feasible_alpha_from_floor`, and a non-default rule is recorded as `alpha_rule` in the commit and requires `--out-path`, so the main commits cannot be overwritten with it. A rule giving α ≤ the design margin stops with rc 7 instead of a traceback.
- **Tests:** `tests/test_alpha_rule_v3.py`: `alpha_from_floor` with the defaults equals `feasible_alpha_from_floor` exactly on 20,001 + 155 floors (grid multiples, float-dust cases, the seed-0 probe floors); the tighter rule's values on the seed-0 floors (0.15, 0.08, 0.18, 0.12, 0.10, 0.03, 0.09); on a synthetic cache, a committing non-default rule (margin 0.04 → `alpha_rule` recorded) and the rc-7 refusal (margin 0.02). Re-committing all 7 seed-0 datasets with the options at their defaults reproduces `configs/committed_v3_*_ts0.json` except `created` (`results_v3/logs/r2_taskE_default_rule_unchanged.log`).
- **Runs:** `drive_v3.py --phase commit --seeds 0 --tag r2am02 --commit-prefix committed_v3_am02 "--extra-args=--alpha-margin 0.02 --alpha-grid 0.01"` (6 datasets, rc 0; MNIST rc 7). Sweeps: `drive_v3.py --phase sweep --seeds 0 --tag r2am02 --commit-prefix committed_v3_am02 --metrics-dir-name metrics_v3_alpha_margin02` (12 cells, 4 parallel groups, rc 0). Tables: `make_tables_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3_alpha_margin02 --output-dir results_v3/tables_e9_alpha_margin02`. Provenance: `TABLE_E4_cascade_seeds.{md,csv}` in that directory was written by the Task-F version of `make_tables_v3.py` (committed in `0d02588`, one commit after these tables); E2/E3/E4/E6 are identical with either version.
- **Result:** §8.7 (PhysioNet and Adult first).
- **Imagenette:** committed after Task D with the same options: α = 0.05 ≤ the design margin, rc 7, nothing written (`results_v3/logs/r2am02_commit_image-imagenette_na_ts0.log`).

### 12.6 Task F — cluster package for seeds 1–2 (prepared, not executed)

- **Latent fixes** (§9): `scripts/run_pool_rollout_v3.py --orders-file` passes `heldout_digest=split_digest(pool["heldout_index"])` to `load_orders`, so an orders file exported from another split is refused. `scripts/export_heldout_v3.py --out` now defaults to `$RESULTS_ROOT\orders_v3\{dsname}_ts{ts}_heldout.npz`, and `orders/` is git-ignored. Tests: `tests/test_hpc_v3.py` (a wrong-digest orders file raises, the right one reaches the replay; the export default path).
- **`hpc/README_v3.md`** (new): push (`git push -u origin aistats-v3`, plus the tag); data to copy (sizes) or re-download; environment (modules, conda env, torch/torchvision versions, `hpc/env.local.sh` as the cluster's `set_env`); pre-flight (tests, dry run); the `sbatch` lines (backbones: tasks 8,10,11,13,14,15,16,18,19,21,22,23 with config epochs and 9,12,17,20 with `CAFA_EXTRA="--epochs 60"`; rollouts: 16–29,32–45, and Imagenette 30,31,46,47 with `--batch-size 32`, greedy also `--policy-amp`, `--time=12:00:00`; `afterok` dependencies); expected wall times (laptop ledger ÷ the measured throttling factor 1.418, labelled as a full-clock laptop estimate, not a TinyGPU measurement); the files to bring back with `rsync`/`scp` lines; the round-3 local commands.
- **Slurm scripts:** `hpc/rollout_v3.slurm` runs Imagenette at `--batch-size ${CAFA_RGB_BATCH:-32}` (both policies of a seed) with `--policy-amp` for greedy; both scripts append `${CAFA_DRIVER_FLAGS:-}` to the driver call. `.gitattributes` forces LF for `*.slurm` / `*.sh`.
- **Driver:** `drive_v3.py --dry-run` now prints the command of a cell whose prerequisite is missing on this machine (marked `[prerequisite missing now: …]`). Before, it printed only `skip (missing prerequisite)`, which hid every seed-1/2 command.
- **Dry run** (`hpc/dry_run_v3.sh`): executes the real batch scripts for all 24 backbone and 48 rollout array indices under bash, with `SLURM_ARRAY_TASK_ID` set and `CAFA_DRIVER_FLAGS=--dry-run`. `module` and `source activate` are stubbed; `source /etc/profile` is the only line not executed (this workstation's profile is not `set -u` clean). Output: `results_v3/logs/hpc_dry_run.log` (every array task produces a driver line). Covered by `tests/test_hpc_v3.py::test_hpc_dry_run_all_array_indices` (representative indices with empty roots: all would run, `--epochs 60` exactly on 9/12/17/20, Imagenette `--batch-size 32`, `--policy-amp` exactly on greedy).
- **Seed aggregation:** `make_tables_v3.py` also writes `TABLE_E4_cascade_seeds.{md,csv}`, mean ± sample sd over seeds per (dataset, policy), tested on seed 0 alone (`n_seeds` = 1, value only) and on synthetic 3-seed rows.
- **Tests:** whole suite `110 passed in 354.09s (0:05:54)` (`results_v3/logs/r2_taskF_pytest_full_suite.log`).

### 12.7 Final checklist (instruction.md §10 + instruction_round2.md; `results_v3/logs/r2_final_checklist.log`)

- [x] `git status` clean on `aistats-v3` after the final commit. Round-2 commits, one or more per task: A `5089d5e`, `3825b6c`; B `ac658f4`, `8e1858e`; C `799b214`; E `00c2c4a`; F `0d02588`, `32fec67` (audit fixes); D `7da8c3c`; then the final content commit and the hash commit (header).
- [x] Nine v3 test files green at the final state: `33 passed in 34.14s` (`results_v3/logs/r2_final_pytest_nine_v3.log`).
- [x] Whole suite: `110 passed in 196.75s (0:03:16)`, **0 xfailed, 0 skipped** (`results_v3/logs/r2_final_pytest_full_suite.log`, run with `-rxXs`).
- [x] `results_v3/run_log.jsonl`, `logs/`, `tables/`, `figures/`, `planted/`, `repair/`, `diagnostics/`, `round1/` present.
- [x] No smoke artifacts: `$RESULTS_ROOT\pool_v3\` holds 16 caches, none with `max_rows`; `checkpoints_v3\` holds the 8 seed-0 checkpoints; `metrics_v3\` holds 16 JSONs; `configs/committed_v3*` holds 18 commits (8 main, G8, 3 E7 BEFORE, 6 am02), none synthetic.
- [x] `handoff.md` complete per instruction.md §8 plus §12. Every `TBD-RUN` has its command: seeds 1–2 in `hpc/README_v3.md` (§10 step 1); Phase 1d in §10 step 4.
- [x] Frozen files: against `aaai27-submission`, `src/cafa/risk_control.py` differs by the one authorised line (§12.1); `tests/test_risk_control.py`, `tests/test_mondrian.py`, `tests/test_baselines.py`, `tests/test_pipeline.py` are unchanged.
- [x] `git tag` shows `aaai27-submission` (→ `550f8e2`).
- [x] `$RESULTS_ROOT\metrics_v3_round1\` exists and is untouched: 16 of 16 sha256 OK against `results_v3/round1/metrics_v3_round1.sha256` (`results_v3/logs/r2_round1_archive_check.log` during round 2 and `r2_final_checklist.log` at the end).
- [x] HPC dry run on the committed tree (`results_v3/logs/hpc_dry_run.log`, header: commit `7da8c3c`, 0 uncommitted files): 72 array tasks, 48 would run (seeds 1–2), 24 skip because their seed-0 output exists.

## 13. Round 3 (`instruction_round3.md`, Part 3a)

Round 3 follows `instruction_round3.md` (Tasks G, H, I, K, L); `instruction.md` and `instruction_round2.md` stay in force. Start and end times are in the header.

**Scope**
- **Part 3a only.** `$RESULTS_ROOT\pool_v3\` holds the 16 seed-0 caches and no `*_ts1_*` / `*_ts2_*` cache, so Task J (3b) was not started. The instruction covers this case: "If 3b's caches are not present when you start, do 3a, update the handoff, commit, and stop." Seeds 1–2 stay `TBD-RUN` (§10).
- **Author decisions of round 3 §0, applied:**
  - Nothing primary changes. λ_ref `dep`, the α rule, δ, γ, the δ split, the grids and every existing committed JSON are untouched; the only new commits are the eight E9 `committed_v3_am10_*` files.
  - Tier 2 stays in the cascade.
  - Phase 1d stays `TBD-RUN`.

**Commits**

| task | code | results |
|---|---|---|
| K | `2ffeb04` | `ecf553f` |
| L | `5481269` | `95f9480` (README: measured smoke) |
| G / H / I | `b85ac6a` | `dfdc149` |

Then the handoff commit (header).

**Method**
- The code was written in four parallel slices, each on its own files: G (E10 / E11 / F7); I plus the H summary; K (the sweep); L (checkpoint tag). One adversarial reviewer per slice then checked it and reproduced every finding it reported.
  - Reviews: `results_v3/diagnostics/r3_review_task{G,I,K,L}.json`.
  - Fix reports, with the mutation checks: `results_v3/diagnostics/r3_review_fixes_task{G,I,K,L}.md`.
- The reviewers reported 13 findings (2 medium, 11 low). All were fixed before any run. Each fix is covered by a test that fails on the unfixed code; the fix reports list the mutation checks.
- The handoff itself was then checked number by number against the files by three read-only verifiers: `results_v3/diagnostics/r3_handoff_verification_{A,B,C}.md`. Their corrections are applied in this text.
- The two medium findings:
  - The cost-gap "intrinsic" rule used cost / T, which is wrong under non-uniform costs. It now uses oracle cost / full-acquisition cost.
  - F3 was illegible with 48 cells. It now draws one bar per (dataset, policy) with seed means.
- The low ones:
  - Tests could not tell full acquisition apart from the top grid column.
  - A tiny `--cal-frac` gave an unclear numpy error.
  - The edges shape check used broadcasting.
  - E11 printed `TBD-RUN` for a missing cost scheme; it now prints `n/a`.
  - An empty `--checkpoint-tag` fell back to the protocol paths.
  - Test gaps: the core prediction, cost / T vs cost / full acquisition, and the α = design-margin refusal boundary.
  - Two reporting additions: `label_note` / `n_splits_finite`, and `cascade_cost_over_oracle_feasible`.
  - The hypergeometric sensitivity column `pred_tier1_hyper`.

### 13.1 Task G — certifiability margin (E10)

**Code and command**
- Script and test: `scripts/margin_analysis_v3.py` (torch-free), `tests/test_margin_analysis_v3.py` (26 tests).
- Command: `python scripts/margin_analysis_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --calfrac-dir 0.25 $RESULTS_ROOT/metrics_v3_calfrac025 --calfrac-dir 1.0 $RESULTS_ROOT/metrics_v3_calfrac100 --output-dir results_v3/tables --figure results_v3/figures/F7_margin.pdf`
- Log: `results_v3/logs/r3_margin_analysis.log`.

**Points.** One point per (dataset, policy, seed, λ_ref key ∈ {0.5, 0.7, 0.9, dep}, split): 16 cells × 4 × 5 = **320**.

**Definitions (as specified)**
- k* is the deepest stratum of `audit_by_split[s]`. `r_full`, `rmin_thr` and `rmin_depth` are its calibration-pool values.
- n_k is the commit's `expected_cal_counts[k*]`.
- margin = α − r_full and z = margin · √(n_k / (α(1−α))).
- k_max is the largest error count with `hoeffding_bentkus_pvalue(k/n_k, n_k, α) ≤ δ₁ = 0.05`.
- `pred_tier1` = P(Bin(n_k, r_full) ≤ k_max). `pred_tier1_thr` is the same with `rmin_thr`.
- `obs_tier1` is the tier-1 share over the split's 20 draws.

**Sensitivity columns** (in the CSV and the summary JSON / md; not in `TABLE_E10_margin.md`)
- `pred_tier1_nk_calpool` uses n_k = round(0.5 · the split's calibration-pool count of k*).
- `pred_tier1_hyper` is the prediction conditional on the split's calibration pool (draws without replacement, hypergeometric). At cal_frac 1.0 it reduces to an indicator.

**Outputs**
- `results_v3/tables/TABLE_E10_margin.{md,csv}` (320 rows).
- `TABLE_E10_margin_calfrac.csv` (the 640 cal-frac points).
- `TABLE_E10_margin_summary.{json,md}`.
- `results_v3/figures/F7_margin.pdf`:
  - panel (a): obs vs z, colour = dataset, marker = λ_ref key, with the curve at the median n_k 1,314 and median α 0.15;
  - panel (b): obs vs pred, with the diagonal and a ±0.2 band;
  - the cal-frac points are open markers.

**Result** (`TABLE_E10_margin_summary.json`)

| subset | predictor | n | Spearman ρ (p) | within ±0.2 | mean abs. error |
|---|---|---|---|---|---|
| all keys | `pred_tier1` | 320 | **0.905** (3.28e-120) | **0.994** (318/320) | 0.020 |
| all keys | `pred_tier1_thr` | 320 | 0.905 (2.56e-120) | 0.988 (316/320) | 0.021 |
| all keys | `pred_tier1_hyper` (sensitivity) | 320 | 0.894 (3.55e-113) | 0.997 (319/320) | 0.010 |
| key `dep` | `pred_tier1` | 80 | 0.935 (7.17e-37) | 1.000 (80/80) | 0.027 |
| cal_frac 0.25 points | `pred_tier1` | 320 | 0.944 (9.01e-155) | 0.975 (312/320) | 0.025 |
| cal_frac 1.0 points (1 draw per split) | `pred_tier1` / `pred_tier1_hyper` | 320 | 0.838 (1.12e-85) / 1.000 | 0.906 (290/320) / 1.000 (320/320) | — |
| main + cal_frac (960 points) | `pred_tier1` | 960 | 0.897 | 0.958 (920/960) | 0.030 |

**Notes on the result**
- **The 2 points outside ±0.2 for `pred_tier1`** (`results_v3/logs/r3_handoff_facts.log`):
  - FashionMNIST greedy, key 0.7, split 779: pred 0.629, obs 0.85, z 2.37, n_k 1,487.
  - Imagenette greedy, key 0.7, split 779: pred 0.256, obs 0.05, z 1.52, n_k 256.
- **By key:** ρ is 0.449 / 0.777 / 0.706 at keys 0.5 / 0.7 / 0.9, with 80/80, 78/80 and 80/80 points within ±0.2. At key 0.5 most points sit at obs = pred = 1, so ρ is low while the agreement is full.
- **By dataset:** ρ is 0.762 (PhysioNet) to 0.975 (MiniBooNE). MNIST has no ρ because every share is 1; it has 40/40 within ±0.2.
- **At cal_frac 1.0:** a split's outcome is fixed given its calibration pool. So the unconditional binomial scores lower there, while the conditional prediction is exact.

### 13.2 Task H — α margin 0.10 (E9)

**Commits**
- Command: `drive_v3.py --phase commit --seeds 0 --commit-prefix committed_v3_am10 --tag r3am10 "--extra-args=--alpha-margin 0.10 --alpha-grid 0.05"`.
- 8 datasets, rc 0, 14.9 s in total (`results_v3/logs/driver_r3am10_commit.out`, `r3am10_commit_*.log`).
- None refused: every α is ≥ 0.15, above the design margin.

| dataset | α | λ_ref `dep` (greedy / random) |
|---|---|---|
| Diabetes | 0.20 | 0.7980 / 0.7980 |
| PhysioNet | 0.25 | 0.0000 / 0.0000 |
| CUBE | 0.20 | 0.6263 / 0.6162 |
| FashionMNIST | 0.20 | 0.6263 / 0.6667 |
| Imagenette | 0.15 | 0.7475 / 0.7273 |
| MNIST | 0.15 | 0.6768 / 0.6869 |
| MiniBooNE | 0.20 | 0.7475 / 0.7475 |
| Adult | 0.30 | 0.0000 / 0.0000 |

Source: `r3_handoff_facts.log`.

**Sweeps and tables**
- 16 cells into `$RESULTS_ROOT\metrics_v3_alpha_margin10\`; ledger `r3am10:sweep:*` (16 runs, rc 0, 2,892.9 s).
- Tables: `results_v3/tables_e9_alpha_margin10/`.
- Summary: `python scripts/alpha_margin_summary_v3.py --output-dir results_v3/tables` → `results_v3/tables/TABLE_E9_alpha_margin.{md,csv}`. Pasted below; the CSV also has λ_ref and G per margin.

| dataset | policy | margin 0.02 (grid 0.01) | margin 0.05 (grid 0.05, primary) | margin 0.10 (grid 0.05) |
|---|---|---|---|---|
| csv-diabetes | greedy_entropy | alpha 0.12: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.20: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 |
| csv-diabetes | random | alpha 0.12: tier1 0.00, tier3 0.02, cert 0.02, cost/T 1.00 | alpha 0.15: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.20: tier1 0.26, tier3 0.74, cert 1.00, cost/T 0.89 |
| csv-physionet | greedy_entropy | alpha 0.15: tier1 0.58, tier3 0.42, cert 1.00, cost/T 0.56 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| csv-physionet | random | alpha 0.15: tier1 0.58, tier3 0.42, cert 1.00, cost/T 0.62 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| cube | greedy_entropy | alpha 0.08: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.29 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.25 |
| cube | random | alpha 0.08: tier1 0.00, tier3 0.99, cert 0.99, cost/T 1.00 | alpha 0.15: tier1 0.99, tier3 0.01, cert 1.00, cost/T 0.58 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.49 |
| fashionmnist | greedy_entropy | alpha 0.09: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.12, tier3 0.88, cert 1.00, cost/T 0.93 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.13 |
| fashionmnist | random | alpha 0.09: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.12, tier3 0.88, cert 1.00, cost/T 0.93 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.17 |
| image-imagenette | greedy_entropy | refused: alpha = 0.05 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 0.20, tier3 0.80, cert 1.00, cost/T 0.88 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.19 |
| image-imagenette | random | refused: alpha = 0.05 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 0.09, tier3 0.91, cert 1.00, cost/T 0.94 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.15 |
| mnist | greedy_entropy | refused: alpha = 0.03 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.07 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.07 |
| mnist | random | refused: alpha = 0.03 <= design margin 0.05 (commit_v3 rc 7) | alpha 0.10: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.18 | alpha 0.15: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.16 |
| tabular-adult | greedy_entropy | alpha 0.18: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.25: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.21 | alpha 0.30: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| tabular-adult | random | alpha 0.18: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.25: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.30: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.00 |
| tabular-MiniBooNE | greedy_entropy | alpha 0.10: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.01, tier3 0.99, cert 1.00, cost/T 0.99 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.15 |
| tabular-MiniBooNE | random | alpha 0.10: tier1 0.00, tier3 1.00, cert 1.00, cost/T 1.00 | alpha 0.15: tier1 0.26, tier3 0.74, cert 1.00, cost/T 0.86 | alpha 0.20: tier1 1.00, tier3 0.00, cert 1.00, cost/T 0.12 |

**At margin 0.10** (`results_v3/tables_e9_alpha_margin10/TABLE_E4_cascade.csv`)
- **Certification and violations, all 16 cells:**
  - certified deployment is 1.00;
  - certified violation is 0.000;
  - mean `max_excess_se` is < 0 (−11.478 … −2.694);
  - the raw pooled violation rate is ≤ 0.080 (FashionMNIST random: 0.000–0.400 by split; MiniBooNE greedy 0.030, 0.000–0.100).
- **Tiers:** every cell is tier 1 = 1.00 except Diabetes:
  - greedy: tier 3 = 1.00, deepest stratum `type_II`;
  - random: tier 1 / tier 3 = 0.26 / 0.74.
- **Degenerate targets:** at α 0.30, Adult becomes degenerate like PhysioNet (λ_ref `dep` = 0, G = 1, cost / T 0.000). PhysioNet stays so at α 0.25.
- **Reading:**
  - The tier-1 share never falls as the margin grows.
  - At margin 0.10 the tier-1 share is 1.00 in every cell except Diabetes: greedy is 0.00 at all three margins (deepest stratum `type_II`); random goes 0.00 → 0.00 → 0.26.
  - So the tier-3 cost of FashionMNIST, Imagenette and MiniBooNE at margin 0.05 disappears once α is raised by 0.05.
  - At the primary α, Task K classes FashionMNIST, Imagenette and MiniBooNE random as sample-limited (§13.4). The cost therefore depends on both the target α and the calibration size.
  - The α rule itself is the author's (round 3 §0); this table is explanatory.

### 13.3 Task I — reporting additions

**E4 columns** (`scripts/make_tables_v3.py`; appended after the round-2 columns, which keep their order and values):
- `deployed_cost_over_T`, `marginal_cost_over_T`, `mondrian_cost_over_T`. T comes from the metrics meta.
- `tier2_would_certify`: the share of draws with `tiers_certified.budget` True and `tiers_certified.threshold` False.
  - The cascade deploys tier 2 exactly then, so the column equals the tier-2 share by construction.
  - It is **0.000 in every cell of every table directory** (seed 0; `r3_handoff_facts.log`).
  - At draw level, 0 of 61,720 draw records have budget certified without threshold, and 0 deploy tier 2. This covers every metrics JSON of `metrics_v3`, `_round2`, `_alpha_margin02`, `_alpha_margin10`, `_calfrac025`, `_calfrac100`, `_dw`, `_G8` and `_hbfix_single`, at all λ_ref keys and both cost schemes (`results_v3/logs/r3_tier2_draw_count.log`).
  - So in no draw of rounds 2–3 would tier 2 have mattered.
- `escalated_fraction` = 1 − answered fraction.
- `oracle_safe_cost_over_T`, `oracle_safe_feasible_rate`, `cascade_over_safe_oracle` (from Task K).
- The new numeric columns are also averaged in `TABLE_E4_cascade_seeds`.

**E6** gains `feasible_rate`.

**F3** (`scripts/make_figures_v3.py`):
- The cost panel is in cost / T, keeping the marginal and Mondrian marks.
- The E2 worst-stratum risk / α of marginal CAFA is printed under each cell's bar, in red when > 1.
- With several seeds, F3 shows one bar per (dataset, policy): the seed mean with a min–max bar.

**Regeneration and check**
- Every table directory was regenerated with `results_v3/logs/r3_postrun.sh` (logs `r3_make_tables_*.log`, `r3_make_figures.log`): `tables`, `tables_inverse_info`, `tables_e9_lambda_ref_{0.5,0.7,0.9}`, `tables_e9_alpha_margin02`, `tables_e9_delta_weights`, `tables_e9_G8`.
- Keyed-row invariance against the committed round-2 CSVs: 0 value differences, 0 missing rows. The only changes are new columns and the two oracle rows per cell in E6 (`results_v3/logs/r3_table_invariance.log`).
- New values: §8.1, §8.4. Paper-facing numbers: §11.

### 13.4 Task K — is the cost intrinsic? (stratum-safe oracle, calibration size)

**K1, code.** `scripts/run_cascade_sweep.py` adds two ex-post, non-deployable baselines per split and draw, computed on the full test split:
- `oracle_stratum_safe`: the cheapest grid λ with R̂_test,k(λ) ≤ α for every k ∈ K_cal. If none qualifies: full acquisition and `feasible` False.
- `oracle_stratum_safe_mondrian`: per stratum the cheapest safe λ_k; full acquisition where none exists.
- `oracle_stratum_safe` also records `calpool_stratum_risk` / `calpool_stratum_n`, taken on the split's whole calibration pool at λ* (None when infeasible). The Mondrian version records `lambda_by_stratum` and `abstained_fraction`.
- Summary fields: `feasible_rate`, `cascade_cost_over_oracle`, `cascade_cost_over_oracle_feasible` (oracle-feasible draws only), `cascade_cost_over_safe_mondrian_oracle`.
- Test: `tests/test_oracles_v3.py` (14 tests).

**K1, rerun of the 16 main cells**
- The 16 round-2 files were moved to `$RESULTS_ROOT\metrics_v3_round2\`.
  - Hashes taken in `metrics_v3\` before the move (12:24): `results_v3/round2/metrics_v3_round2.premove.sha256`.
  - Hashes taken after the move: `results_v3/round2/metrics_v3_round2.sha256`. Identical to the pre-move ones.
  - 16/16 OK on re-check at the end (`results_v3/logs/r3_final_checklist.log`).
- The 16 cells were then swept again with the round-3 code into `metrics_v3\`; ledger `r3:sweep:*`, 16 runs, rc 0, 2,800.2 s.
- `check_sweep_equivalence_v3.py` says **IDENTICAL for all 16 cells**: every field of the round-2 file is reproduced (10,400 draw records, plus summaries, audits and meta; `results_v3/logs/r3_taskK_sweep_equivalence.log`).
- So every round-2 number in §8 stands. The rerun only adds the oracle fields and `meta.cal_frac`.

**Cost gap** (`results_v3/tables/TABLE_E4_cost_gap.{md,csv}`; definitions in its header)
- **Label:**
  - "intrinsic" if oracle cost / full-acquisition cost ≥ 0.9;
  - otherwise "sample-limited" if cascade / oracle ≥ 1.6, i.e. above the cost-premium band 1.0–1.6 of instruction.md §4.4;
  - otherwise "near-oracle".
- **`n_needed`** = ln(1/δ₁) / kl(r_cal(λ*) ‖ α), where r_cal(λ*) is the deepest stratum's calibration-pool risk at the oracle's λ* (computed with `cafa.commit_rules.kl_bernoulli`).
  - It is inf if r_cal ≥ α or the split has no feasible oracle.
  - The per-cell value is the median over the 5 splits.
- **Table columns:** `n_k` and `r_cal(λ*)` are those of the primary split 778 (`—`: oracle infeasible there). "same, feasible draws" is `cascade_over_safe_oracle_feasible`.

| dataset | policy | cascade cost / T | safe-oracle cost / T | oracle feasible | cascade / safe oracle | same, feasible draws | label | n_k (cal. draw, k*) | r_cal(λ*) | n_needed (median; range; finite splits) |
|---|---|---|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1.000 | 1.000 | 0.000 | 1.000 | — | intrinsic | 2,144 | — | inf; inf–inf; 0/5 |
| csv-diabetes | random | 1.000 | 1.000 | 0.000 | 1.000 | — | intrinsic | 1,652 | — | inf; inf–inf; 0/5 |
| csv-physionet | greedy_entropy | 0.000 | 0.000 | 1.000 | — (0/0) | — | near-oracle | 1,080 | 0.141 | 255; 205–325; 5/5 |
| csv-physionet | random | 0.000 | 0.000 | 1.000 | — (0/0) | — | near-oracle | 1,080 | 0.141 | 255; 205–325; 5/5 |
| cube | greedy_entropy | 0.289 | 0.229 | 1.000 | 1.264 | 1.264 | near-oracle | 615 | 0.142 | 1,907; 561–12,622; 5/5 |
| cube | random | 0.576 | 0.518 | 1.000 | 1.112 | 1.112 | near-oracle | 357 | 0.106 | 309; 206–427; 5/5 |
| fashionmnist | greedy_entropy | 0.929 | 0.423 | 0.800 | 2.197 | 3.500 | sample-limited | 1,320 | — | inf; 4,482–inf; 2/5 |
| fashionmnist | random | 0.926 | 0.464 | 0.800 | 1.995 | 2.985 | sample-limited | 1,426 | — | inf; 16,344–inf; 2/5 |
| image-imagenette | greedy_entropy | 0.884 | 0.232 | 1.000 | 3.806 | 3.806 | sample-limited | 249 | 0.120 | 7,539; 437–inf; 3/5 |
| image-imagenette | random | 0.940 | 0.189 | 1.000 | 4.974 | 4.974 | sample-limited | 248 | 0.099 | 367,175; 1,553–inf; 3/5 |
| mnist | greedy_entropy | 0.075 | 0.072 | 1.000 | 1.041 | 1.041 | near-oracle | 2,397 | 0.088 | 3,942; 3,785–7,213; 5/5 |
| mnist | random | 0.184 | 0.168 | 1.000 | 1.092 | 1.092 | near-oracle | 1,413 | 0.097 | 50,242; 9,898–inf; 4/5 |
| tabular-adult | greedy_entropy | 0.213 | 0.198 | 1.000 | 1.079 | 1.079 | near-oracle | 894 | 0.251 | inf; 382–inf; 2/5 |
| tabular-adult | random | 1.000 | 0.856 | 0.200 | 1.169 | 3.595 | near-oracle (oracle infeasible on 4/5 splits) | 930 | — | inf; inf–inf; 0/5 |
| tabular-MiniBooNE | greedy_entropy | 0.993 | 0.745 | 0.400 | 1.333 | 2.761 | near-oracle (oracle infeasible on 3/5 splits) | 3,442 | — | inf; inf–inf; 0/5 |
| tabular-MiniBooNE | random | 0.862 | 0.230 | 1.000 | 3.743 | 3.743 | sample-limited | 2,318 | 0.139 | inf; 6,119–inf; 1/5 |

**Reading the cost gap**
- **Intrinsic: Diabetes (both policies).** Even ex post, no grid threshold is stratum-safe on any split; the deepest stratum is `type_II`. Full acquisition is the price of the stratum guarantee itself.
- **Sample-limited: FashionMNIST (both), Imagenette (both), MiniBooNE random.**
  - The ex-post oracle needs 0.19–0.46 of T; the cascade pays 2.0–5.0 times that.
  - Where `n_needed` is finite, it exceeds the deepest stratum's calibration-draw count:
    - Imagenette 7,539 vs 249 (greedy) and 367,175 vs 248 (random);
    - FashionMNIST: finite on 2 of 5 splits; the smaller value is 4,482 (greedy) / 16,344 (random), vs 1,320 / 1,426;
    - MiniBooNE random: 6,119 on its one finite split, vs 2,318.
  - On the other splits, the oracle's λ* has calibration-pool risk ≥ α although its test risk is ≤ α, so no calibration size certifies that exact λ*.
  - The exception is FashionMNIST split 778 (both policies). There no grid λ is stratum-safe even ex post (`label_note`: oracle infeasible in 1/5 splits).
- **Near-oracle: PhysioNet, CUBE, MNIST, Adult greedy.** The cascade is within 1.04–1.26 of the oracle (CUBE, MNIST, Adult greedy). For PhysioNet both cost 0.
- **Mixed: Adult random and MiniBooNE greedy.**
  - The pooled-cost rule labels them near-oracle, but the oracle is infeasible on 4/5 and 3/5 splits, where it pays full acquisition too.
  - On the oracle-feasible draws the cascade costs 3.595 and 2.761 times the oracle.
  - These are the two cells whose deepest stratum sits at α (`unresolved` / split-dependent verdicts, §8.2).
- **Caveat on `n_needed`:** it refers to certifying the oracle's exact λ*, whose calibration risk often sits within thousandths of α.
  - Example: MNIST random has r_cal(λ*) 0.097 vs α 0.10 on the primary split, and n_needed median 50,242 (range 9,898–inf over splits).
  - Yet the cascade deploys tier 1 in every draw at cost ratio 1.092.
  - The K2 curve below is the direct evidence on sample size.

**K2, calibration size**
- `--cal-frac` was added to `run_cascade_sweep.py`. It defaults to the commit's 0.5; a non-default value needs `--out-dir`.
- At 1.0 the 20 draws of a split all coincide (the whole calibration pool), so **one draw per split, 5 per cell, was run** (`meta.cal_frac_note`).
- Runs, issued per dataset (`--datasets <ds>`) through the parallel lanes of `results_v3/logs/r3_lane.sh`; seconds are summed over runs:
  - `drive_v3.py --phase sweep --seeds 0 --metrics-dir-name metrics_v3_calfrac025 --tag r3cf025 "--extra-args=--cal-frac 0.25"`: 16 runs, rc 0, 1,760.3 s;
  - the same with `metrics_v3_calfrac100`, `--tag r3cf100`, `--cal-frac 1.0`: 16 runs, rc 0, 488.4 s.
- The 0.25 draws are nested in the 0.5 draws (same permutation, first half).
- Tables: `results_v3/tables_e11_calfrac{025,100}/`.
- Summary: `results_v3/tables/TABLE_E11_calfrac.{md,csv}`, at λ_ref `dep` with uniform costs.
  - `n_k` = the mean over splits of the expected calibration-draw count of k*.
  - `pred_tier1` / `pred_tier1_hyper` = the E10 predictions recomputed at that n_k.

| dataset | policy | n_k (0.25 / 0.5 / 1.0) | tier-1 share | pred_tier1 | pred_tier1_hyper | cost / T | certified violation |
|---|---|---|---|---|---|---|---|
| csv-diabetes | greedy_entropy | 1,079 / 2,158 / 4,316 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 1.00 / 1.00 / 1.00 | 0.000 / 0.000 / 0.000 |
| csv-diabetes | random | 851 / 1,701 / 3,403 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 1.00 / 1.00 / 1.00 | 0.000 / 0.000 / 0.000 |
| csv-physionet | greedy_entropy | 540 / 1,080 / 2,160 | 0.99 / 1.00 / 1.00 | 0.99 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 0.02 / 0.00 / 0.00 | 0.000 / 0.000 / 0.000 |
| csv-physionet | random | 540 / 1,080 / 2,160 | 0.99 / 1.00 / 1.00 | 0.99 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 0.03 / 0.00 / 0.00 | 0.000 / 0.000 / 0.000 |
| cube | greedy_entropy | 296 / 592 / 1,184 | 0.98 / 1.00 / 1.00 | 0.97 / 1.00 / 1.00 | 0.98 / 1.00 / 1.00 | 0.34 / 0.29 / 0.27 | 0.000 / 0.000 / 0.000 |
| cube | random | 186 / 371 / 742 | 0.69 / 0.99 / 1.00 | 0.78 / 0.98 / 1.00 | 0.77 / 0.99 / 1.00 | 0.74 / 0.58 / 0.55 | 0.000 / 0.000 / 0.000 |
| fashionmnist | greedy_entropy | 645 / 1,289 / 2,578 | 0.12 / 0.12 / 0.40 | 0.08 / 0.16 / 0.29 | 0.07 / 0.11 / 0.40 | 0.92 / 0.93 / 0.77 | 0.010 / 0.000 / 0.000 |
| fashionmnist | random | 730 / 1,460 / 2,920 | 0.06 / 0.12 / 0.20 | 0.09 / 0.16 / 0.25 | 0.07 / 0.13 / 0.20 | 0.96 / 0.93 / 0.87 | 0.010 / 0.010 / 0.000 |
| image-imagenette | greedy_entropy | 136 / 272 / 544 | 0.09 / 0.20 / 0.40 | 0.14 / 0.26 / 0.53 | 0.09 / 0.19 / 0.40 | 0.97 / 0.88 / 0.71 | 0.000 / 0.000 / 0.000 |
| image-imagenette | random | 122 / 243 / 486 | 0.03 / 0.09 / 0.20 | 0.09 / 0.17 / 0.33 | 0.05 / 0.10 / 0.20 | 0.98 / 0.94 / 0.85 | 0.000 / 0.000 / 0.000 |
| mnist | greedy_entropy | 1,097 / 2,194 / 4,388 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 0.08 / 0.07 / 0.07 | 0.000 / 0.000 / 0.000 |
| mnist | random | 721 / 1,442 / 2,884 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 0.19 / 0.18 / 0.18 | 0.000 / 0.000 / 0.000 |
| tabular-MiniBooNE | greedy_entropy | 1,660 / 3,321 / 6,642 | 0.02 / 0.01 / 0.00 | 0.02 / 0.02 / 0.03 | 0.01 / 0.01 / 0.00 | 0.99 / 0.99 / 1.00 | 0.010 / 0.010 / 0.000 |
| tabular-MiniBooNE | random | 1,186 / 2,371 / 4,743 | 0.10 / 0.26 / 0.20 | 0.18 / 0.32 / 0.53 | 0.14 / 0.25 / 0.20 | 0.94 / 0.86 / 0.86 | 0.000 / 0.000 / 0.000 |
| tabular-adult | greedy_entropy | 436 / 873 / 1,746 | 0.81 / 1.00 / 1.00 | 0.75 / 0.97 / 1.00 | 0.79 / 0.99 / 1.00 | 0.39 / 0.21 / 0.21 | 0.010 / 0.000 / 0.000 |
| tabular-adult | random | 454 / 909 / 1,818 | 0.02 / 0.00 / 0.00 | 0.02 / 0.02 / 0.03 | 0.01 / 0.00 / 0.00 | 0.99 / 1.00 / 1.00 | 0.000 / 0.000 / 0.000 |

**Reading the calibration-size table**
- **Doubling the calibration draw (0.5 → 1.0)** raises the tier-1 share and lowers the cost in four of the five sample-limited cells (MiniBooNE random is the exception, below):
  - FashionMNIST greedy: tier 1 0.12 → 0.40, cost / T 0.93 → 0.77.
  - Imagenette greedy: tier 1 0.20 → 0.40, cost / T 0.88 → 0.71.
  - Imagenette random: tier 1 0.09 → 0.20.
  - FashionMNIST random: tier 1 0.12 → 0.20.
- **Halving it (0.5 → 0.25)** lowers the tier-1 share in CUBE random (0.99 → 0.69) and Adult greedy (1.00 → 0.81).
- **MiniBooNE random does not improve** (0.26 → 0.20). Its deepest stratum is at the certifiability edge on most splits, and `pred_tier1_hyper` there is also 0.20.
- **The two intrinsic Diabetes cells** are at full cost at every size. They are tier 3 at 0.5 and 1.0. At 0.25 Diabetes greedy certifies in only 0.93 of the draws (tier 3; none 0.07). That is the only cell with certified deployment < 1 at any calibration size (`results_v3/tables_e11_calfrac{025,100}/TABLE_E4_cascade.csv`).
- **Certified violation** is ≤ 0.010 at every size.
- **Raw pooled violation** is ≤ 0.07 at 0.25 and ≤ 0.20 at 1.0. At 1.0 it moves in steps of 0.2 (5 draws).
- **Mean `max_excess_se`** is < 0 in every cell at both sizes.
- **Resolution at 1.0:** with one draw per split, a tier-1 share there moves in steps of 0.2.
- F7 shows the 640 cal-frac points (open markers) on the same curve.

### 13.5 Task L — FashionMNIST predictor-upgrade repair: `TBD-RUN` (cluster)

**Code (`5481269`)**
- `--checkpoint-tag TAG` on `train_backbone_v3.py`, `run_pool_rollout_v3.py` and `drive_v3.py` (backbones and rollouts phases). It changes only the checkpoint folder (`checkpoints_v3_TAG`) and the cache token suffix (`{policy}-TAG`).
- `--width-mult` / `--p-full` overrides, which require a tag.
- `commit_v3.find_policy_caches` ignores tagged caches, so a future re-commit never picks them up.
- `check_caches_v3.py` checks a tagged greedy/random pair as its own group.
- `run_repairs_v3.py --repair-tag TAG` runs two repairs:
  - greedy: BEFORE = `pool_v3/fashionmnist_ts0_greedy_entropy_softmax.npz` on `configs/committed_v3_fashionmnist_ts0.json`, AFTER = `…greedy_entropy-repair…`, label `predictor_upgrade`;
  - random: the same with `--policy random`, label `predictor_upgrade_random`.
- Tests: `tests/test_checkpoint_tag_v3.py` (12 tests) and `tests/test_hpc_v3.py::test_hpc_dry_run_task_l_lines`.

**Smoke on the laptop.** Documented smoke flags, under a separate tag `smokerepair`. All its outputs were deleted afterwards; `pool_v3` holds 16 caches again.

| smoke step | time |
|---|---|
| width-4 backbone, `--epochs 1 --max-train 2000` | 85 s (8 optimizer steps; the GPU was busy in 1 of the 16 `nvidia-smi` samples of this window, so this does not time an epoch) |
| greedy rollout, `--max-rows 256` | **361 s**; projected linearly to ≈ 39,500 s ≈ 11 h for the 28,000 heldout rows |
| random rollout, `--max-rows 256` | 23 s |

- `nvidia-smi` reported `sw_thermal_slowdown = Active` in 70 of 72 busy samples (utilization > 50 %).
  - The two exceptions are the backbone smoke's only busy sample (13:08:34, 1,462 MHz) and the greedy rollout's first busy sample (13:08:55, 1,492 MHz).
  - Over the busy samples the mean SM clock was 521 MHz of 2,100 and the mean temperature 87.9 °C.
- Logs: `results_v3/logs/r3_taskL_smoke_{backbone,rollout_greedy,rollout_random,nvidia_smi}.log`.

**Decision:** not run locally, for two reasons:
- The GPU is throttled. Task L says: "If the GPU is throttled, prepare the two cluster lines instead (the README's pattern) and mark `TBD-RUN`."
- The greedy cell's smoke-based estimate (≈ 11 h) exceeds 8 h (instruction.md §6).

**Cluster package.** `hpc/README_v3.md` §8 has the two `sbatch` lines, the wall-time estimates, the copy-back and the local follow-up:
- backbone: task 6 with `CAFA_EXTRA="--epochs 60 --width-mult 4 --p-full 0.3"`;
- rollouts: lines 12–13;
- both with `CAFA_DRIVER_FLAGS="--checkpoint-tag repair"`.

**E7 FashionMNIST before → after:** `TBD-RUN`. When the caches are back, run `python scripts/run_repairs_v3.py --seeds 0 --datasets fashionmnist --repair-tag repair --tag r3L`.

### 13.6 Ledger, background jobs, tests

**Ledger.** `results_v3/run_log.jsonl` has 72 round-3 runs, 0 with a non-zero rc. They ran 11:27:51 → 12:07:22 UTC (13:27–14:07 local).

| ledger cell prefix | runs | total seconds | non-zero rc |
|---|---|---|---|
| `r3am10:commit:` | 8 | 14.9 | 0 |
| `r3:sweep:` (K1 rerun, `metrics_v3`) | 16 | 2,800.2 | 0 |
| `r3am10:sweep:` | 16 | 2,892.9 | 0 |
| `r3cf025:sweep:` | 16 | 1,760.3 | 0 |
| `r3cf100:sweep:` | 16 | 488.4 | 0 |

**Background jobs**
- The sweeps were split into six lanes of sequential `drive_v3.py` calls (`results_v3/logs/r3_lane.sh`; plan and times in `r3_background_jobs.log`; outputs `driver_r3_lane*.out`).
  - Lanes 1–4 ran from 13:29.
  - Lanes 5 and 6 were paused at 13:29:56, about 1 min after launch, because free RAM was low. The reading was 1.0 GB, from the console only and not in a file. Their process trees were killed before their first cell finished, so there is no ledger line and no metrics file from them.
  - Lanes 5 and 6 were relaunched at 13:50 (`driver_r3_lane{5,6}_resume.out`).
  - A lane 7 started at 13:52 and took their short tail jobs; lanes 5 and 6 then skipped those as already existing.

**Run outside the ledger**
- the Task L smoke (§13.5);
- the post-run tables, figures, E10 and E9 summary (`results_v3/logs/r3_postrun.sh`, logs `r3_*.log`);
- the checks `r3_taskK_sweep_equivalence.log` and `r3_table_invariance.log`;
- the handoff facts in `r3_handoff_facts.log`.

**Tests**
- Whole suite on the round-3a code just before it was committed (13:22–13:27; commits `2ffeb04` / `5481269` / `b85ac6a` at 13:27) and before the runs: `169 passed in 273.07s (0:04:33)` (`results_v3/logs/r3_code_pytest_full_suite.log`; round 2: 110).
- Final state: §13.7.


### 13.7 Final checklist

Sources: instruction.md §10, instruction_round2.md, instruction_round3.md.

The log is `results_v3/logs/r3_final_checklist.log`, run at HEAD `dfdc149`. At that point these were uncommitted, and all of them go into the handoff content commit:
- `handoff.md`;
- `hpc/README_v3.md` (wording);
- the regenerated `results_v3/logs/hpc_dry_run.log`;
- the new `r3_final_*.log`, `r3_handoff_facts.log` and `r3_tier2_draw_count.log`;
- `results_v3/round2/metrics_v3_round2.premove.sha256`;
- the `results_v3/diagnostics/r3_*` review records.

- [x] **Git.** `git status` is clean on `aistats-v3` after the hash commit; this was checked after committing.
  - Round-3 commits: K `2ffeb04`, `ecf553f`; L `5481269`, `95f9480`; G/H/I `b85ac6a`, `dfdc149`.
  - Then the handoff content commit, whose hash the header records, and one follow-up commit that only writes that hash.
- [x] **Nine v3 test files:** `33 passed in 62.66s (0:01:02)` (`results_v3/logs/r3_final_pytest_nine_v3.log`).
- [x] **Whole suite:** `169 passed in 285.70s (0:04:45)`, with **0 xfailed and 0 skipped** (`results_v3/logs/r3_final_pytest_full_suite.log`, run with `-rxXs`).
- [x] **Result directories present:** `results_v3/run_log.jsonl`, `logs/`, `tables/`, `figures/`, `planted/`, `repair/`, `diagnostics/`, `round1/` and `round2/`. Also the new `tables_e9_alpha_margin10/` and `tables_e11_calfrac{025,100}/`.
- [x] **No smoke artifacts:**
  - `pool_v3`: 16 caches, none with `max_rows`, no tagged policy token. The Task-L smoke caches and `checkpoints_v3_smokerepair/` were deleted.
  - `checkpoints_v3`: the 8 seed-0 checkpoints.
  - `metrics_v3`: 16 files.
  - `configs/committed_v3*`: 26 files (18 from round 2 plus 8 `am10`), none synthetic.
- [x] **Frozen files.** Against `aaai27-submission`, `src/cafa/risk_control.py` differs by the one authorised line (§12.1). `tests/test_risk_control.py`, `tests/test_mondrian.py`, `tests/test_baselines.py` and `tests/test_pipeline.py` are unchanged. Round 3 changed nothing under `src/`.
- [x] **Tags.** `git tag` shows `aaai27-submission` (→ `550f8e2`) and the older `canonical-v2*` tags. `aistats-v3-results` is **not set**: it belongs to Part 3b (Task J), which did not run.
- [x] **Archives intact:**
  - `$RESULTS_ROOT\metrics_v3_round1\`: 16 of 16 sha256 OK.
  - `$RESULTS_ROOT\metrics_v3_round2\`, the archive of the round-2 primary metrics: 16 of 16 sha256 OK against `results_v3/round2/metrics_v3_round2.sha256`.
- [x] **HPC dry run on the committed tree** (`results_v3/logs/hpc_dry_run.log`; header: commit `dfdc149`, 0 uncommitted files under hpc/, scripts/, src/, configs/):
  - 72 array tasks: 48 would run (seeds 1–2) and 24 skip because their seed-0 output exists.
  - The Task-L lines are covered by `tests/test_hpc_v3.py::test_hpc_dry_run_task_l_lines`.
- [x] **`TBD-RUN` items and their commands:**
  - seeds 1–2 and Task J: §10 step 1, `hpc/README_v3.md` §1–7;
  - the FashionMNIST repair (Task L): §10 step 1b, `hpc/README_v3.md` §8;
  - Phase 1d: §10 step 4.
- [x] **Stop conditions:** none reached. The round-3 conditions concern seed-1/2 caches and cluster checkpoints, which Part 3b would check. The instruction.md §7 conditions did not occur.
