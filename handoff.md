# CAFA v3 campaign — handoff

- Date: 2026-10-01 (session start 13:09 local, UTC+2)
- Branch: `aistats-v3` (from `550f8e2`, the `main` HEAD at session start)
- Final commit hash: TBD-RUN (filled at session end)
- Total wall time: TBD-RUN

> Status: **IN PROGRESS** — this file is updated after every phase. Anything not yet run is `TBD-RUN`.

## 1. Executive summary

- Phase 0: done — nine v3 test files 32 passed (29 torch-free + 3 torch); whole suite 80 passed; synthetic Type-II and feasible end-to-end pass (§5).
- Phase 1 smoke: done — all three dataset kinds (tabular / patches / RGB) train and roll out on CUDA; no crash-level bug. One resource fix (Imagenette greedy policy did 2× the documented forward passes) and several reporting/provenance fixes in the Phase-3 scripts, each with a regression test (§4).
- Phase 1 real: TBD-RUN (in progress)
- Phase 2: TBD-RUN (running in background)
- Phase 3: TBD-RUN

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

TBD-RUN

## 7. Phase 2 results

TBD-RUN

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
