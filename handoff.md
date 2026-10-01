# CAFA v3 campaign — handoff

- Date: 2026-10-01 (session start 13:09 local, UTC+2)
- Branch: `aistats-v3` (from `550f8e2`, the `main` HEAD at session start)
- Final commit hash: TBD-RUN (filled at session end)
- Total wall time: TBD-RUN

> Status: **IN PROGRESS** — this file is updated after every phase. Anything not yet run is `TBD-RUN`.

## 1. Executive summary

- Phase 0: done — nine v3 test files 32 passed (29 torch-free + 3 torch); whole suite 80 passed; synthetic Type-II and feasible end-to-end pass (§5).
- Phase 1 smoke: done — all three dataset kinds (tabular / patches / RGB) train and roll out on CUDA; no crash-level bug. One resource fix (Imagenette greedy policy did 2× the documented forward passes) and several reporting/provenance fixes in the Phase-3 scripts, each with a regression test (§4).
- Phase 1 real (seed 0): 7 backbones done (CUBE and MiniBooNE miss their full-observation targets even after the one allowed 60-epoch retrain; CUBE's target is above the generator's Bayes accuracy 0.97025); tabular caches done (5 datasets × 2 policies, greedy = random full-acquisition accuracy exactly); MNIST / FashionMNIST rollouts and Imagenette in progress (§6.3).
- Phase 2: done — all acceptance checks met (§7, `results_v3/planted/PLANTED_VALIDATION.md`).
- Phase 3: in progress — commits + 100-draw sweeps for the 5 tabular datasets; MiniBooNE greedy and random exceed δ in test stratum-violation rate at λ_ref `dep` (0.110 / 0.120); independent diagnosis found no implementation bug (`results_v3/diagnostics/`), reported as a result (§8).

## 2. Environment

| item | value | source |
|---|---|---|
| OS | Windows 10 Home Single Language 10.0.19045 | `Get-CimInstance Win32_OperatingSystem` |
| CPU | 11th Gen Intel Core i5-11400H, 6 cores / 12 threads | `Win32_Processor` |
| RAM | 16,867,012,608 B (≈15.7 GiB); ≈5.3 GB free at session start | `Win32_ComputerSystem` / `Win32_OperatingSystem` |
| GPU | NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB, driver 610.78 | `nvidia-smi` |
| GPU thermals | under load the GPU runs at 87–90 °C with `clocks_event_reasons.sw_thermal_slowdown = Active`; SM clock observed between 210 MHz and 1057 MHz (max 2100 MHz), on AC power (battery 100 %) | `nvidia-smi --query-gpu=clocks.sm,clocks.max.sm,temperature.gpu,...` |
| Python | 3.12.2 (repo `.venv`) | `.venv\Scripts\python.exe --version` |
| torch / torchvision | 2.13.0+cu126 / 0.28.0+cu126; `torch.cuda.is_available()` = True | `python -c "import torch, torchvision; ..."` |
| numpy / scipy / scikit-learn / pandas | 2.5.1 / 1.18.0 / 1.9.0 / 3.0.3 | `pip list` |
| matplotlib / PyYAML / pytest | 3.11.0 / 6.0.3 / 9.1.1 | `pip list` |
| DATA_ROOT | `F:\CAFA_data` (MNIST raw + OpenML cache copied from the repo's git-ignored `data/`; FashionMNIST, AFABench CSVs, Imagenette downloaded this session) | `set_env.ps1` |
| RESULTS_ROOT | `F:\CAFA_results` (`pool_v2/`, `checkpoints_v2/` copied from the repo's git-ignored `results/`) | `set_env.ps1` |
| Disk free at start | F: 70.4 GB, C: 43.7 GB | `Get-PSDrive` |
| Disk used by roots | TBD-RUN | |

`set_env.ps1` (repo root, git-ignored) sets `DATA_ROOT`, `RESULTS_ROOT`, and `PYTHONIOENCODING=utf-8`.

## 3. Run ledger

Machine-readable ledger of every driver-run cell: `results_v3/run_log.jsonl`; per-cell logs: `results_v3/logs/`.

| phase | cell | command | start (local) | duration | exit | output |
|---|---|---|---|---|---|---|
| 0 | v3 tests | `python -m pytest -q <nine v3 test files>` | 13:1x | 40.4 s | 0 | console (32 passed) |
| 0 | full suite | `python -m pytest -q tests/` | 13:1x | 196.6 s | 0 | `results_v3/logs/phase0_pytest_full_suite.log` (80 passed) |
| 0 | synthetic typeII | make_synthetic_pool_cache → commit_v3 → run_cascade_sweep (20 draws) → make_tables_v3 | 13:1x | < 1 min | 0 | `results_v3/logs/phase0_synthetic_typeII.log` |
| 0 | synthetic feasible | same, `--scenario feasible` | 13:1x | < 1 min | 0 | `results_v3/logs/phase0_synthetic_feasible.log` |
| 1a | data | `python scripts/download_data_v3.py --csv --mnist --fashionmnist --openml` | 13:17 | 55.3 s | 0 | `results_v3/logs/phase1a_download_small.log` |
| 1a | data | `python scripts/download_data_v3.py --imagenette` (background, PID 10264) | 13:18 | ≈ 6 min | 0 | `results_v3/logs/phase1a_download_imagenette.log`; `F:\CAFA_data\imagenette_cache\imagenette_224.npz` (2,016,279,694 B, 13,394 images) |
| 1 smoke | backbones / rollouts | 8 smoke runs + 2 re-timings via `drive_v3.py --tag smoke*` | 13:20–13:51 | see `run_log.jsonl` (cells `smoke*:`) | 0 | `results_v3/logs/smoke*_*.log`; all smoke checkpoints/caches deleted at 13:52 |
| 2 | E5 planted | `python scripts/planted_validation.py --output-dir results_v3/planted --n-replicates 1000` (background, PID 18076) | 13:19 | TBD-RUN | TBD-RUN | `results_v3/logs/phase2_planted_validation.log` |
| 1b | backbones ts0 | `drive_v3.py --phase backbones --seeds 0 --datasets <7 non-Imagenette>` (background, PID 10724) | 13:53 | TBD-RUN | TBD-RUN | `results_v3/logs/backbones_*_na_ts0.log` |

Background jobs: Phase 2 planted validation (PID 18076, started 13:19); seed-0 backbones driver (PID 10724, started 13:53).

## 4. Code changes

Every change below was followed by a rerun of the nine v3 test files (now 33 tests incl. one new) and of `tests/test_v3_scripts.py` (new, 6 tests). The 6 new script tests were also run against the shipped (HEAD) scripts in a scratch copy: all 6 failed there, i.e. they detect the bugs they cover.

| file (lines) | change | class / failure fixed | covering test | commit |
|---|---|---|---|---|
| 33 v3 files from `CAFA_v3_code.zip` | added unchanged | drop-in (the zip holds 33 files, not 38: 9 src + 12 scripts + 9 tests + 1 config + 2 docs) | — | `b1caf84` |
| `tests/conftest.py` (new) | put `src/` on `sys.path` | Environment: the nine v3 test files failed to collect in isolation (`ModuleNotFoundError: No module named 'cafa'`); the v2 tests insert the path themselves | the nine v3 test files | `b1caf84` |
| `.gitignore` | +`set_env.ps1` | keep machine-specific roots out of git | — | `b1caf84` |
| `scripts/drive_v3.py` (new) | resumable driver (instruction §4.0); later `--tag` for smoke runs (separate log names and ledger cells) | — | dry-run; used for every Phase-1/3 cell | `b1caf84`, phase-1 smoke commit |
| `scripts/check_caches_v3.py` (new) | Phase-1 acceptance summary: per cache n, T, full-acquisition accuracy; greedy vs random equality to 1e-12; v2-vs-v3 same-heldout-rows check | — | run on every finished cell (§6) | phase-1 smoke commit |
| `src/cafa/models_v3.py` 217–275 (`GreedyEntropyImagePolicy`) | `select_next` scores only the UNOBSERVED candidates (ascending patch order, so argmin and tie-breaking are unchanged); new `cand_chunk` and `amp` arguments (also on `from_training_data`); `amp` = fp16 autocast for the hypothetical-reveal passes only | **Resource / v3 code bug**: the shipped loop ran ResNet-18 on all 49 patches at every step and discarded the observed ones → 2,401 candidate passes per row instead of the documented 1,225. Imagenette smoke with the shipped code: 64 rows in 925.3 s → ≈ 21.5 h per 5,358-row cell (> 8 h) | `tests/test_models_v3.py::test_greedy_image_policy_matches_reference_and_counts_passes` (identical picks vs. the shipped implementation for cand_chunk 1/4/5/16/49 on random masks incl. 0 and P−1 observed; P(P+1)/2 passes per rollout) | phase-1 smoke commit |
| `scripts/run_pool_rollout_v3.py` 24, 60, 79, 166–169, 216–217, 238–239 | flags `--policy-amp`, `--cand-chunk` (RGB greedy only); cache meta records `max_rows`, `batch_size`, `policy_amp`, `cand_chunk`; RGB progress line shows elapsed seconds | Resource (instruction §5 allows fp16 autocast on the RGB rollout path) + provenance: smoke caches had no partial marker | `tests/test_v3_scripts.py::test_commit_refuses_partial_smoke_cache` | phase-1 smoke commit |
| `scripts/run_cascade_sweep.py` 231–256 | Mondrian oracle record gets per-stratum test risks (abstained strata at full acquisition, as in its `test_risk`) and `stratum_violation`; cheapest-valid oracle record gets `test_risk`, `test_cost`, `stratum_violation` | **v3 code bug (E6 reporting)**: Mondrian `stratum_violation_rate` was always 0.0 (summary averaged a missing key with default False); cheapest-valid oracle was dropped from the summary (n = 0, cost None) | `test_sweep_baseline_stratum_violation_recorded_and_summarised`, `test_sweep_keeps_cheapest_valid_oracle` | phase-1 smoke commit |
| `scripts/run_cascade_sweep.py` 282–286 | summary averages `stratum_violation` only over records that carry it (no `False` default) | same as above | same | phase-1 smoke commit |
| `scripts/run_cascade_sweep.py` 112–122 | refuse a `max_rows` (smoke) cache; refuse a cache whose `checkpoint_sha256` differs from the committed one; clear error if the policy is not in the commit | provenance guard (a stale commit or a smoke cache would have been swept silently) | `test_sweep_refuses_stale_commit` | phase-1 smoke commit |
| `scripts/commit_v3.py` 118–130 | refuse `max_rows` caches; every policy cache must match the greedy cache (shape, heldout digest, labels) | provenance guard | `test_commit_refuses_partial_smoke_cache` | phase-1 smoke commit |
| `scripts/make_tables_v3.py` 50–53, `scripts/make_figures_v3.py` 35–37 | skip a cell that lacks the requested `--scheme` instead of falling back to the first scheme | **v3 code bug (reporting)**: `--scheme inverse_info` printed uniform-cost image rows under an `inverse_info` header | `test_make_tables_skips_missing_scheme` | phase-1 smoke commit |
| `scripts/repair_experiment.py` 70, 80–81, 96–98, 115 | `--n-draws` default = `protocol_v3.n_draws` (100); report records `n_draws`, cache/commit paths, policy | **v3 code bug**: default was 50 draws, against the fixed 100-draw protocol (rule 5) | `test_repair_default_n_draws_is_protocol` | phase-1 smoke commit |
| `tests/test_v3_scripts.py` (new) | 6 regression tests for the script fixes above | — | itself | phase-1 smoke commit |
| `S11_answer.md`, `.gitignore` (`CAFA.zip` line) | committed unchanged | pre-existing working-tree changes on `main` at session start (S11 staged, `.gitignore` modified); committed first so the branch starts clean | — | `8ddb7dc` |

Review method: before the first GPU run, five independent reviewers (one per file group: `models_v3`, `train_backbone_v3`, rollout, data loaders, Phase-3 scripts) read the untested code against the v2 interfaces, and each finding was checked by an adversarial verifier. Findings that were confirmed but not fixed (they only affect the optional Phase 1d or are latent) are listed in §9.

`git diff --stat` vs. base: TBD-RUN (session end).

## 5. Phase 0 results

- Nine v3 test files: `32 passed in 40.37s` (0 skipped; the 3 torch tests in `test_models_v3.py` ran).
- Whole suite `python -m pytest -q tests/`: `80 passed in 196.60s (0:03:16)` — 0 failed, 0 skipped (`results_v3/logs/phase0_pytest_full_suite.log`).
- Synthetic end-to-end (`--n 8000`, 20 draws), console lines (`results_v3/logs/phase0_synthetic_*.log`):

```
typeII:   [cascade] synthetic-planted ts0 greedy_entropy lr[dep]=0.495 G=3 | cert=0.85 tiers={'0': 0.15, '1': 0.0, '2': 0.0, '3': 0.85} viol=0.000 | deepest stratum verdict=type_II
          (lr 0.5: tiers '3'=0.9; lr 0.7 and 0.9: tiers '3'=1.0; all viol=0.000, all verdict=type_II)
feasible: [cascade] synthetic-planted ts0 greedy_entropy lr[dep]=0.455 G=3 | cert=1.00 tiers={'0': 0.0, '1': 1.0, '2': 0.0, '3': 0.0} viol=0.000 | deepest stratum verdict=feasible
          (lr 0.5 / 0.9: '1'=1.0; lr 0.7: '1'=0.95, '0'=0.05; all viol=0.000)
```

  Acceptance: Type II → `type_II` + tier 3 ≥ 0.8 (0.85–1.0) with `viol=0.000` — pass; feasible → `'1': 1.0` at `dep` — pass.
  Synthetic cache / commit / metrics files and `results_v3/tables_smoke/` were deleted afterwards.

## 6. Phase 1 results

### 6.1 Data

| dataset | status | source / size |
|---|---|---|
| `csv:physionet` | downloaded | `F:\CAFA_data\afabench\physionet.csv` (4.1 MB; AFABench `main` raw URL) |
| `csv:diabetes` | downloaded | `F:\CAFA_data\afabench\diabetes.csv` (54.9 MB) |
| `mnist` | present (copied) | `F:\CAFA_data\MNIST\raw` |
| `fashionmnist` | downloaded | `F:\CAFA_data\FashionMNIST\raw` |
| `tabular:MiniBooNE` | OpenML cache | `n_train=78038 d=50` (`phase1a_download_small.log`) |
| `tabular:adult` | OpenML cache | `n_train=27133 d=14` (`phase1a_download_small.log`) |
| `image:imagenette` | downloaded + cached | `imagenette2-320.tgz` → `imagenette_cache/imagenette_224.npz`, 13,394 images at 224 px |
| `cube` | generated | no download |

### 6.2 Smoke runs (all deleted afterwards)

From `results_v3/run_log.jsonl` (cells prefixed `smoke`):

| smoke cell | flags | seconds | console |
|---|---|---|---|
| backbone `csv:physionet` | `--epochs 1 --max-train 2000` | 16.5 | `masked_acc=0.8215 full_obs_acc=0.8445` |
| rollout `csv:physionet` greedy | `--max-rows 256` | 11.5 | `full-acq acc=0.8359` |
| rollout `csv:physionet` random | `--max-rows 256` | 13.3 | `full-acq acc=0.8359` (greedy = random, `check_caches_v3.py`: diff 0.000e+00, PASS) |
| backbone `mnist` | `--epochs 1 --max-train 2000` | 22.6 | `masked_acc=0.1585 full_obs_acc=0.1135` (8 optimizer steps) |
| rollout `mnist` greedy | `--max-rows 256` | 99.9 | `full-acq acc=0.1094` |
| backbone `image:imagenette` | `--epochs 1 --max-train 512` | 77.6 | `masked_acc=0.4238 full_obs_acc=0.8125` |
| rollout `image:imagenette` greedy, shipped policy | `--max-rows 64 --batch-size 16` | 925.3 | `full-acq acc=0.8438` |
| rollout `image:imagenette` greedy, fixed policy, fp32 | `--max-rows 32 --batch-size 16` | 174.2 | `[rgb rollout] 16/32 (43s)`, `full-acq acc=0.8125` |
| rollout `image:imagenette` greedy, fixed policy, `--policy-amp` | `--max-rows 32 --batch-size 16 --policy-amp` | 126.7 | `[rgb rollout] 16/32 (34s)`, `full-acq acc=0.8125` |

Fixed-policy fp32 vs. `--policy-amp` on the same 32 rows: first-step picks identical (32/32), 76.1 % of all picks identical, 11/32 rows with an identical full order, `correct[:, T]` identical and max |score difference at T| = 0.0 (scoring passes stay fp32).

**Imagenette decision (instruction §6).** Shipped code: 925.3 s / 64 rows → 5,358 rows ≈ 77,460 s ≈ 21.5 h (> 8 h). Fixed policy + `--policy-amp`: 126.7 s / 32 rows including data loading → 5,358 rows ≈ 21,214 s ≈ 5.9 h (≤ 8 h; per-batch rate 34 s / 16 rows → ≈ 3.2 h). Decision: run seed-0 Imagenette greedy (`--batch-size 16 --policy-amp`) and random (`--batch-size 16`, same batch size so the depth-T scoring passes are batched identically) as the last GPU jobs. Caveat: the GPU throttles thermally (§2); the estimate holds for the clocks seen during the smoke. MNIST greedy smoke: 99.9 s / 256 rows → 28,000 rows ≈ 10,930 s ≈ 3.0 h per cell (≤ 8 h).

### 6.3 Real runs

(Interim — regenerated with `python scripts/report_v3.py --backbones --caches` at each update; MNIST / FashionMNIST / Imagenette rows are added when they finish.)

Backbones (seed 0; full-observation accuracy on the first 5,000 train rows for tabular, 2,000 for patches, 512 for RGB, as printed by `train_backbone_v3.py`):

| cell | epochs | masked train acc | full-obs train acc | target | pass | seconds | log |
|---|---|---|---|---|---|---|---|
| backbones:csv:physionet:na:ts0 | config (40) | 0.8706 | 0.8936 | 0.86 | pass | 30.7 | `results_v3/logs/backbones_csv-physionet_na_ts0.log` |
| backbones:cube:na:ts0 | config (40) | 0.6450 | 0.9524 | 0.98 | miss | 24.3 | `results_v3/logs/backbones_cube_na_ts0.log` |
| backbones:tabular:adult:na:ts0 | config (40) | 0.8161 | 0.8626 | 0.85 | pass | 56.7 | `results_v3/logs/backbones_tabular-adult_na_ts0.log` |
| backbones:csv:diabetes:na:ts0 | config (40) | 0.8651 | 0.9094 | 0.85 | pass | 195.3 | `results_v3/logs/backbones_csv-diabetes_na_ts0.log` |
| backbones:tabular:MiniBooNE:na:ts0 | config (40) | 0.8625 | 0.9146 | 0.93 | miss | 280.3 | `results_v3/logs/backbones_tabular-MiniBooNE_na_ts0.log` |
| backbones:mnist:na:ts0 | config (30) | 0.9093 | 0.9995 | 0.995 | pass | 1533.4 | `results_v3/logs/backbones_mnist_na_ts0.log` |
| backbones:fashionmnist:na:ts0 | config (30) | 0.8930 | 0.9755 | 0.93 | pass | 1602.9 | `results_v3/logs/backbones_fashionmnist_na_ts0.log` |
| retrain60:backbones:cube:na:ts0 | 60 | 0.6532 | 0.9598 | 0.98 | miss (kept) | 49.8 | `results_v3/logs/retrain60_backbones_cube_na_ts0.log` |
| retrain60:backbones:tabular:MiniBooNE:na:ts0 | 60 | 0.8684 | 0.9158 | 0.93 | miss (kept) | 379.6 | `results_v3/logs/retrain60_backbones_tabular-MiniBooNE_na_ts0.log` |

Target misses (instruction §4.2: raise epochs once, then keep and report): CUBE and MiniBooNE were retrained once with `--epochs 60` (CLI override for those two datasets only; the config's `training_v3.tabular.epochs: 40` is unchanged, so the passing tabular cells are untouched). Both still miss and the 60-epoch checkpoints are the ones used; the 40-epoch checkpoints are kept at `$RESULTS_ROOT\checkpoints_v3_superseded\{cube,tabular-MiniBooNE}_ts0_ep40.pt`. CUBE diagnosis: the exact Bayes classifier of the generator (`generate_cube(20000, 123)`, class-conditional Gaussian likelihoods) has accuracy 0.97025 on all 20,000 rows, so the 0.98 target is above the Bayes ceiling (`results_v3/diagnostics/cube_bayes_accuracy.json`). MiniBooNE: the v2 AAAI backbone's heldout full-acquisition accuracy is 0.915831 (`pool_v2/tabular-MiniBooNE_ts0_greedy_entropy_softmax.npz`); the v3 60-epoch backbone gives 0.922558 on heldout (below).

Pool caches (seed 0; `$RESULTS_ROOT\pool_v3\`; heldout full-acquisition accuracy = mean of `correct[:, T]`):

| dataset | seed | policy | n | T | heldout full-acq acc | rollout seconds | greedy = random (1e-12) | cache |
|---|---|---|---|---|---|---|---|---|
| csv-diabetes | 0 | greedy_entropy | 36825 | 45 | 0.903870 | 487.8 |  | `pool_v3/csv-diabetes_ts0_greedy_entropy_softmax.npz` |
| csv-diabetes | 0 | random | 36825 | 45 | 0.903870 | 28.0 | yes | `pool_v3/csv-diabetes_ts0_random_softmax.npz` |
| csv-physionet | 0 | greedy_entropy | 4800 | 41 | 0.873333 | 44.6 |  | `pool_v3/csv-physionet_ts0_greedy_entropy_softmax.npz` |
| csv-physionet | 0 | random | 4800 | 41 | 0.873333 | 6.3 | yes | `pool_v3/csv-physionet_ts0_random_softmax.npz` |
| cube | 0 | greedy_entropy | 8000 | 20 | 0.953125 | 13.1 |  | `pool_v3/cube_ts0_greedy_entropy_softmax.npz` |
| cube | 0 | random | 8000 | 20 | 0.953125 | 6.2 | yes | `pool_v3/cube_ts0_random_softmax.npz` |
| tabular-MiniBooNE | 0 | greedy_entropy | 52026 | 50 | 0.922558 | 869.8 |  | `pool_v3/tabular-MiniBooNE_ts0_greedy_entropy_softmax.npz` |
| tabular-MiniBooNE | 0 | random | 52026 | 50 | 0.922558 | 42.1 | yes | `pool_v3/tabular-MiniBooNE_ts0_random_softmax.npz` |
| tabular-adult | 0 | greedy_entropy | 18089 | 14 | 0.852507 | 27.7 |  | `pool_v3/tabular-adult_ts0_greedy_entropy_softmax.npz` |
| tabular-adult | 0 | random | 18089 | 14 | 0.852507 | 19.2 | yes | `pool_v3/tabular-adult_ts0_random_softmax.npz` |

Heldout sizes (from the caches): PhysioNet 4,800, Diabetes 36,825, CUBE 8,000, MiniBooNE 52,026, Adult 18,089 (the `PHASES_V3.md` table says 19,537 for Adult; see §9).

v2 "before" caches for E7: **present, not regenerated** — `$RESULTS_ROOT\pool_v2\{mnist,tabular-MiniBooNE,tabular-adult}_ts0_greedy_entropy_softmax.npz` were produced on TinyGPU (`cafa_pool_rollout.o1735175` etc., `created` 2026-07-11) and copied from the repo's git-ignored `results/pool_v2/`; their `checkpoint_sha256` equals the sha256 of `$RESULTS_ROOT\checkpoints_v2\*_ts0.pt` (e3d3c21f13fb / 3e05a708c0de / ed66f5dd5f2a). Heldout full-acquisition accuracy of the v2 caches: MNIST 0.899214, MiniBooNE 0.915831, Adult 0.852286.

## 7. Phase 2 results

Command: `python scripts/planted_validation.py --output-dir results_v3/planted --n-replicates 1000` (CPU, background PID 18076, 13:19:07 → 14:01:32 local, ≈ 42 min, exit 0). Files: `results_v3/planted/PLANTED_VALIDATION.md`, `results_v3/planted/planted_validation.csv`, console `results_v3/logs/phase2_planted_validation.log`.

`results_v3/planted/PLANTED_VALIDATION.md` (verbatim):

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
| B_power_C_route | 250 | 0.030 |  | 0.000 | 0.000 | 0.23 | 12075 | 0.866 |
| B_power_C_route | 500 | 0.030 |  | 0.000 | 0.001 | 0.45 | 12075 | 0.996 |
| B_power_C_route | 1000 | 0.030 |  | 0.000 | 0.108 | 0.90 | 12075 | 1.000 |
| B_power_C_route | 2000 | 0.030 |  | 0.000 | 0.743 | 1.80 | 12075 | 1.000 |
| B_power_C_route | 4000 | 0.030 |  | 0.000 | 0.994 | 3.60 | 12075 | 1.000 |
| B_power_C_route | 250 | 0.050 |  | 0.000 | 0.009 | 0.63 | 4347 | 0.866 |
| B_power_C_route | 500 | 0.050 |  | 0.000 | 0.273 | 1.25 | 4347 | 0.997 |
| B_power_C_route | 1000 | 0.050 |  | 0.000 | 0.926 | 2.50 | 4347 | 1.000 |
| B_power_C_route | 2000 | 0.050 |  | 0.000 | 1.000 | 5.00 | 4347 | 1.000 |
| B_power_C_route | 4000 | 0.050 |  | 0.000 | 1.000 | 10.00 | 4347 | 1.000 |
| B_power_C_route | 250 | 0.100 |  | 0.000 | 0.843 | 2.50 | 1087 | 0.866 |
| B_power_C_route | 500 | 0.100 |  | 0.000 | 0.999 | 5.00 | 1087 | 0.997 |
| B_power_C_route | 1000 | 0.100 |  | 0.000 | 1.000 | 10.00 | 1087 | 1.000 |
| B_power_C_route | 2000 | 0.100 |  | 0.000 | 1.000 | 20.00 | 1087 | 1.000 |
| B_power_C_route | 4000 | 0.100 |  | 0.000 | 1.000 | 40.00 | 1087 | 1.000 |
```

The `unsafe|esc` column is printed only on the console: it is `0.000` in all 15 study-B/C rows (`results_v3/logs/phase2_planted_validation.log`).

| acceptance check (instruction §4.3) | observed | verdict |
|---|---|---|
| false-failure ≤ 0.05 everywhere | max 0.000 (10 study-A rows) | pass |
| cascade violation ≤ 0.10 | max 0.005 (study A, margin −0.03, n_k 4000); 0.000 in all study-B/C rows | pass |
| power increasing in n_kΔ² | monotone within each Δ; at n_kΔ² = 2.5: 0.926 (Δ = 0.05) and 0.843 (Δ = 0.10); at n_kΔ² ≥ 10: 1.000 (Δ = 0.05 and 0.10); Δ = 0.03 reaches 0.994 at n_kΔ² = 3.60 | pass for "1.0 at ≥ 10"; "≈ 0.9 at 2.5" is 0.926 / 0.843 |
| escalation `unsafe|esc` ≈ 0 | 0.000 in every row; escalation rate 0.866 at n_k = 250 → 1.000 at n_k ≥ 1000 | pass |

## 8. Phase 3 results

TBD-RUN

## 9. Deviations, open issues, questions

- The zip contains 33 files (the manifest table lists 12 scripts, not 13); the instruction says 38. All files listed in `V3_FILE_MANIFEST.md` are present.
- `PHASES_V3.md` dataset table, Adult row (48,842 total / 19,537 heldout): the loader drops rows with missing values, so the actual train split is 27,133 rows (`phase1a_download_small.log`); the heldout size is reported in §6.3 from the caches.
- GPU thermal throttling (§2) slows every GPU job by a variable factor; timings in this file are as measured.
- Confirmed by the review but not fixed (they only affect the optional Phase 1d or are latent):
  - `run_pool_rollout_v3.py` `--orders-file` replay calls `load_orders(..., heldout_digest=None)`, so an orders file from another train seed with the same n and T would be replayed without error. Fix before Phase 1d: pass `heldout_digest=split_digest(pool["heldout_index"])`.
  - `afabench_export_orders.py` emits column indices; for one-hot tabular datasets (Adult) the replay expects feature-group indices.
  - `export_heldout_v3.py --out orders/...` writes feature arrays inside the repo, and `orders/` is not git-ignored; write them under `$env:RESULTS_ROOT\orders_v3\` instead.
  - `data_v3._imagenette_arrays` and `download_data_v3.fetch_csvs` write non-atomically (a partial file would be reused). The files written this session are complete (13,394 images; CSV row counts in §6.3).
  - `commit_v3.py` raises `ValueError` if the probe full-acquisition error is exactly 0 (α = 0.05 = design margin); not reachable on the planned datasets (all have nonzero full-acquisition error).

## 10. What remains

TBD-RUN

## 11. Paper-facing numbers

TBD-RUN
