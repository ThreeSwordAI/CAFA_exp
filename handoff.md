# CAFA v3 campaign â€” handoff

- Date: 2026-10-01 (session start 13:09 local)
- Branch: `aistats-v3` (from `550f8e2`, main HEAD at session start)
- Final commit hash: TBD-RUN (filled at session end)
- Total wall time: TBD-RUN

> Status: **IN PROGRESS** â€” this file is updated after every phase. Anything not yet run is `TBD-RUN`.

## 1. Executive summary

- Phase 0: done â€” nine v3 test files 32 passed (29 torch-free + 3 torch); synthetic Type-II and feasible end-to-end pass (Â§5).
- Phase 1: TBD-RUN
- Phase 2: TBD-RUN
- Phase 3: TBD-RUN

## 2. Environment

| item | value | source |
|---|---|---|
| OS | Windows 10 Home Single Language 10.0.19045 | `Get-CimInstance Win32_OperatingSystem` |
| CPU | 11th Gen Intel Core i5-11400H, 6 cores / 12 threads | `Win32_Processor` |
| RAM | 16,867,012,608 B (â‰ˆ15.7 GiB); â‰ˆ5.3 GB free at session start | `Win32_ComputerSystem` / `Win32_OperatingSystem` |
| GPU | NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB, driver 610.78 | `nvidia-smi` |
| Python | 3.12.2 (repo `.venv`) | `.venv\Scripts\python.exe --version` |
| torch / torchvision | 2.13.0+cu126 / 0.28.0+cu126; `torch.cuda.is_available()` = True | `python -c "import torch, torchvision; ..."` |
| numpy / scipy / scikit-learn / pandas | 2.5.1 / 1.18.0 / 1.9.0 / 3.0.3 | `pip list` |
| matplotlib / PyYAML / pytest | 3.11.0 / 6.0.3 / 9.1.1 | `pip list` |
| DATA_ROOT | `F:\CAFA_data` (MNIST raw + OpenML cache copied from the repo's git-ignored `data/`) | `set_env.ps1` |
| RESULTS_ROOT | `F:\CAFA_results` (`pool_v2/`, `checkpoints_v2/` copied from the repo's git-ignored `results/`) | `set_env.ps1` |
| Disk free at start | F: 70.4 GB, C: 43.7 GB | `Get-PSDrive` |
| Disk used by roots | TBD-RUN | |

`set_env.ps1` (repo root, git-ignored) sets `DATA_ROOT`, `RESULTS_ROOT`, and `PYTHONIOENCODING=utf-8`.

## 3. Run ledger

Machine-readable ledger of every driver-run cell: `results_v3/run_log.jsonl`; per-cell logs: `results_v3/logs/`.

| phase | cell | command | start | duration | exit | output |
|---|---|---|---|---|---|---|
| 0 | v3 tests | `python -m pytest -q <nine v3 test files>` | 2026-10-01 13:2x | 40.4 s | 0 | console (32 passed) |
| 0 | full suite | `python -m pytest -q tests/` | 2026-10-01 13:1x | 196.6 s | 0 | `results_v3/logs/phase0_pytest_full_suite.log` (80 passed) |
| 0 | synthetic typeII | make_synthetic_pool_cache â†’ commit_v3 â†’ run_cascade_sweep (20 draws) â†’ make_tables_v3 | 2026-10-01 | < 1 min | 0 | `results_v3/logs/phase0_synthetic_typeII.log` |
| 0 | synthetic feasible | same, `--scenario feasible` | 2026-10-01 | < 1 min | 0 | `results_v3/logs/phase0_synthetic_feasible.log` |

Background jobs: none yet.

## 4. Code changes

| file | change | reason / failure fixed | covering test | commit |
|---|---|---|---|---|
| 33 v3 files from `CAFA_v3_code.zip` | added unchanged | drop-in (the zip holds 33 files, not 38: 9 src + 12 scripts + 9 tests + 1 config + 2 docs) | â€” | phase-0 commit |
| `tests/conftest.py` | new (adds `src/` to `sys.path`) | Environment: the nine v3 test files failed to collect in isolation with `ModuleNotFoundError: No module named 'cafa'` (v2 tests insert the path themselves) | the nine v3 test files | phase-0 commit |
| `.gitignore` | +`set_env.ps1` | keep machine-specific roots out of git | â€” | phase-0 commit |
| `scripts/drive_v3.py` | new | resumable Phase-1/3 driver (instruction Â§4.0) | dry-run | phase-0 commit |
| `S11_answer.md`, `.gitignore` (`CAFA.zip` line) | committed unchanged | pre-existing working-tree changes on `main` at session start (S11 staged, .gitignore modified); committed first so the branch starts clean | â€” | `8ddb7dc` |

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

  Acceptance: Type II â†’ `type_II` + tier 3 â‰¥ 0.8 (0.85â€“1.0) with `viol=0.000` â€” pass; feasible â†’ `'1': 1.0` at `dep` â€” pass.
  Synthetic cache / commit / metrics files and `results_v3/tables_smoke/` deleted afterwards.

## 6. Phase 1 results

TBD-RUN

## 7. Phase 2 results

TBD-RUN

## 8. Phase 3 results

TBD-RUN

## 9. Deviations, open issues, questions

- The zip contains 33 files (manifest table: 12 scripts, not 13); instruction says 38. All 33 listed in `V3_FILE_MANIFEST.md` are present.

## 10. What remains

TBD-RUN

## 11. Paper-facing numbers

TBD-RUN
