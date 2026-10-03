# CAFA v3 — cluster package for seeds 1–2 (incl. Imagenette seeds 1–2) on TinyGPU

Round 2 of the v3 campaign ran seed 0 locally (laptop, RTX 3050 4 GB, thermally throttled). Seeds 1 and 2 of all
eight datasets, Imagenette seeds 1–2 included, are run on the FAU NHR TinyGPU cluster. Only the GPU phases
(backbones, rollouts) run there; commits, sweeps, repairs and tables are torch-free and run locally afterwards
(round 3). Everything below is written for the existing cluster checkout `~/my_repos/CAFA_exp` used for the v2
batches (`hpc/CANONICAL_BATCH_COMMANDS.md`). Adapt the paths if yours differ.

## 1. Push (laptop, repo root)

```bash
git push -u origin aistats-v3
git push origin aaai27-submission     # tag: the code as used for the AAAI-27 submission
```

Then on the cluster (`tinyx` login node):

```bash
cd ~/my_repos/CAFA_exp
git fetch origin && git checkout aistats-v3 && git pull
git log -1 --oneline                  # must equal `git rev-parse --short aistats-v3` on the laptop after the push
```

## 2. Data on the cluster (`$DATA_ROOT`, on woody)

Copy from the laptop (sizes from `F:\CAFA_data`), or re-download on the login node (compute nodes may lack
internet access, so download on `tinyx`, never inside a job):

| item | laptop path | size | re-download on the cluster |
|---|---|---|---|
| AFABench CSVs | `F:\CAFA_data\afabench\{physionet,diabetes}.csv` | 58,982,374 B | `python scripts/download_data_v3.py --csv` |
| MNIST, FashionMNIST | `F:\CAFA_data\{MNIST,FashionMNIST}\` | 66,544,770 B, 85,828,693 B | `python scripts/download_data_v3.py --mnist --fashionmnist` |
| OpenML cache (MiniBooNE, adult) | `F:\CAFA_data\openml\` | 28,836,023 B | `python scripts/download_data_v3.py --openml` |
| Imagenette (224 px cache) | `F:\CAFA_data\imagenette_cache\imagenette_224.npz` | 2,016,279,694 B | `python scripts/download_data_v3.py --imagenette` (archive + cache build; ≈ 6 min locally) |

CUBE is generated on the fly. Byte sizes are `du -sb` of the laptop directories. Copy commands (laptop, Git Bash, which has
`ssh`/`scp` but no `rsync`; add `-J <user>@csnhr.nhr.fau.de` to `ssh`/`scp` if you connect from outside the FAU network):

```bash
H=<user>@tinyx.nhr.fau.de
ssh "$H" 'mkdir -p /home/woody/iwi5/<user>/CAFA_data'
scp -r /f/CAFA_data/afabench /f/CAFA_data/MNIST /f/CAFA_data/FashionMNIST /f/CAFA_data/openml /f/CAFA_data/imagenette_cache \
    "$H:/home/woody/iwi5/<user>/CAFA_data/"
```

Not needed on the cluster: the v2 seed-1/2 caches that the round-3 E7 predictor-upgrade repair uses are already on
the laptop (`F:\CAFA_results\pool_v2\{mnist,tabular-MiniBooNE,tabular-adult}_ts{1,2}_greedy_entropy_softmax.npz`).

## 3. Environment

```bash
source /etc/profile && module load python/3.12-conda
# reuse the v2 env if it has torch >= 2.3 and torchvision >= 0.17 (Imagenette dataset class); otherwise:
conda create -y -p /home/vault/iwi5/<user>/envs/cafa_v3 python=3.12
source activate /home/vault/iwi5/<user>/envs/cafa_v3
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121   # pick the CUDA build the node driver supports (nvidia-smi)
pip install numpy scipy scikit-learn pandas matplotlib pyyaml pytest
python -c "import torch, torchvision; print(torch.__version__, torchvision.__version__)"   # laptop: 2.13.0+cu126 / 0.28.0+cu126
```

The batch scripts start in a clean shell and read their roots from `hpc/env.local.sh` (git-ignored; this
plays the role of the laptop's `set_env.ps1`):

```bash
cp hpc/env.local.template.sh hpc/env.local.sh
# edit hpc/env.local.sh:
export CAFA_ENV=/home/vault/iwi5/<user>/envs/cafa_v3
export DATA_ROOT=/home/woody/iwi5/<user>/CAFA_data
export RESULTS_ROOT=/home/vault/iwi5/<user>/CAFA_results
```

Pre-flight on the login node (CPU, ≈ 5 min):

```bash
source hpc/env.local.sh && source activate "$CAFA_ENV" && export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python -m pytest -q tests/                                          # laptop, round 2: all pass, 0 xfailed
PYTHON=python bash hpc/dry_run_v3.sh | tail -3                      # every array task prints a driver line
```

## 4. Submission (`sbatch` lines; run from the repo root)

Array layout (unchanged from round 1): backbone task `i` = dataset `i % 8`, seed `i / 8`, datasets in the
order `csv:physionet cube tabular:adult csv:diabetes tabular:MiniBooNE mnist fashionmnist image:imagenette`;
rollout task `i` = line `i` (0-based) of `hpc/cells_v3.txt` = `16·ts + 2·dataset + policy` (greedy 0, random 1).
Seed 0 (tasks 0–7 and 0–15) is done locally. **Do not submit them.** The one exception is the round-3 Task-L jobs
of §8: they reuse indices 6 and 12–13 with a checkpoint tag and write tagged outputs.

```bash
cd ~/my_repos/CAFA_exp
# backbones, seeds 1-2, config epochs (physionet, adult, diabetes, mnist, fashionmnist, imagenette)
BB1=$(sbatch --parsable --array=8,10,11,13,14,15,16,18,19,21,22,23 hpc/backbone_v3.slurm)
# backbones, seeds 1-2, CUBE and MiniBooNE with --epochs 60 (as seed 0, handoff.md section 6.3)
BB2=$(CAFA_EXTRA="--epochs 60" sbatch --parsable --export=ALL --array=9,12,17,20 hpc/backbone_v3.slurm)
# rollouts, seeds 1-2, all datasets except Imagenette (greedy and random)
sbatch --dependency=afterok:${BB1}:${BB2} --array=16-29,32-45 hpc/rollout_v3.slurm
# rollouts, Imagenette seeds 1-2: --batch-size 32 for both policies, greedy also --policy-amp (set in the script)
sbatch --dependency=afterok:${BB1} --time=12:00:00 --array=30,31,46,47 hpc/rollout_v3.slurm
squeue -u $USER
```

- `--export=ALL` with `CAFA_EXTRA` set in the submitting shell passes `--epochs 60` to the four CUBE/MiniBooNE
  tasks only. The script forwards it as one quoted `--extra-args=...` argument.
- `afterok` on an array job waits for ALL of its tasks: if any backbone task fails, the whole dependent rollout
  job stays pending (`DependencyNeverSatisfied`). Then `scancel` it, fix and resubmit the failed backbone task(s),
  and resubmit the rollout line(s) with a dependency on the new backbone job. The driver skips every cell whose
  output exists, so resubmitting the full rollout arrays is also safe.
- Imagenette batch size: `CAFA_RGB_BATCH` overrides the default 32 (both policies of a seed must use the same
  value). The local seed-0 Imagenette cells used 16 on the 4 GB laptop GPU.
- The dry run of every array index against the current driver flags is `results_v3/logs/hpc_dry_run.log`
  (made with `hpc/dry_run_v3.sh`, which executes the real batch scripts with `CAFA_DRIVER_FLAGS=--dry-run`).

## 5. Expected wall times

From the laptop ledger (`results_v3/run_log.jsonl`, seed 0) divided by the measured thermal-throttling factor
**15,491.9 / 10,927 = 1.4178** (MNIST greedy rollout: 15,491.9 s measured vs 10,927 s extrapolated from its unthrottled
smoke run, handoff.md §6.2; estimates rounded to whole seconds). The result estimates the same laptop GPU at full clock. It is **not** a measurement of a
TinyGPU node, which has a larger and faster GPU, so treat it as a planning bound. The Slurm limits
(`backbone_v3.slurm` 4 h, `rollout_v3.slurm` 8 h, Imagenette 12 h via `--time`) keep ≥ 2× headroom over these
figures.

<!-- timing:start -->
| dataset | backbone epochs | backbone: laptop s → full-clock estimate | greedy rollout: laptop s → estimate | random rollout: laptop s → estimate | array tasks ts1 / ts2: backbone; rollouts |
|---|---|---|---|---|---|
| csv:physionet | config | 30.7 → 22 s (0.01 h) | 44.6 → 31 s (0.01 h) | 6.3 → 4 s (0.00 h) | 8 / 16; 16,17 / 32,33 |
| cube | 60 (`--epochs 60`) | 49.8 → 35 s (0.01 h) | 13.1 → 9 s (0.00 h) | 6.2 → 4 s (0.00 h) | 9 / 17; 18,19 / 34,35 |
| tabular:adult | config | 56.7 → 40 s (0.01 h) | 27.7 → 20 s (0.01 h) | 19.2 → 14 s (0.00 h) | 10 / 18; 20,21 / 36,37 |
| csv:diabetes | config | 195.3 → 138 s (0.04 h) | 487.8 → 344 s (0.10 h) | 28.0 → 20 s (0.01 h) | 11 / 19; 22,23 / 38,39 |
| tabular:MiniBooNE | 60 (`--epochs 60`) | 379.6 → 268 s (0.07 h) | 869.8 → 614 s (0.17 h) | 42.1 → 30 s (0.01 h) | 12 / 20; 24,25 / 40,41 |
| mnist | config | 1,533.4 → 1,082 s (0.30 h) | 15,491.9 → 10,927 s (3.04 h) | 389.9 → 275 s (0.08 h) | 13 / 21; 26,27 / 42,43 |
| fashionmnist | config | 1,602.9 → 1,131 s (0.31 h) | 14,565.1 → 10,273 s (2.85 h) | 308.2 → 217 s (0.06 h) | 14 / 22; 28,29 / 44,45 |
| image:imagenette | config | 1,067.0 → 753 s (0.21 h) | 26,368.4 → 18,599 s (5.17 h) | 1,481.7 → 1,045 s (0.29 h) | 15 / 23; 30,31 / 46,47 |

Sources: ledger cells `backbones:*:ts0` (`retrain60:*` for the 60-epoch CUBE/MiniBooNE) and `rollouts:*:ts0`; Imagenette rollouts at `--batch-size 16` locally (32 on the cluster).
<!-- timing:end -->

Critical path of one submission (all eight datasets): the longest backbone (FashionMNIST, ≈ 0.31 h) then, after
`afterok`, the longest rollout (see the table), before any queueing time. Per seed this is ≈ 1.0 h of backbones (all eight) and ≈ 6.3 h of non-Imagenette rollouts if run serially. The array runs them in parallel, so the wall time is that of the longest task (MNIST or FashionMNIST greedy ≈ 3 h, Imagenette greedy ≈ 5.2 h at full clock).

## 6. What comes back (cluster → laptop)

Required: the pool caches. Optional: checkpoints (the commit and the sweeps only need the caches, whose meta
records the checkpoint sha256), and the cluster's logs/ledger lines for the record. `results_v3/run_log.jsonl` and
`results_v3/logs/` are git-tracked, so on the cluster they also hold the laptop's history; take only what the cluster
added (relative to the pulled commit):

```bash
# on the cluster, repo root, after the jobs:
git diff -U0 results_v3/run_log.jsonl | sed -n 's/^+{/{/p' > ~/run_log_tinygpu.jsonl
git status --porcelain results_v3/logs | awk '{print $2}' | tar czf ~/logs_tinygpu.tgz -T -
```

```bash
# on the laptop (Git Bash):
H=<user>@tinyx.nhr.fau.de
scp "$H:/home/vault/iwi5/<user>/CAFA_results/pool_v3/*_ts[12]_*.npz" /f/CAFA_results/pool_v3/
scp "$H:/home/vault/iwi5/<user>/CAFA_results/checkpoints_v3/*_ts[12].pt" /f/CAFA_results/checkpoints_v3/   # optional
scp "$H:run_log_tinygpu.jsonl" results_v3/run_log_tinygpu.jsonl
scp "$H:logs_tinygpu.tgz" . && mkdir -p results_v3/logs_tinygpu && tar xzf logs_tinygpu.tgz -C results_v3/logs_tinygpu && rm logs_tinygpu.tgz
```

Check on the laptop: 32 new caches (8 datasets × 2 policies × 2 seeds), and `check_caches_v3.py` passes
(greedy = random full-acquisition accuracy per (dataset, seed)):

```powershell
. .\set_env.ps1
python scripts/check_caches_v3.py --v2-dir F:/CAFA_results/pool_v2 --csv results_v3/phase1_caches.csv
```

## 7. Round 3 on the laptop (torch-free; PowerShell, repo root)

```powershell
. .\set_env.ps1
python scripts/drive_v3.py --phase commit --seeds 1 2 --tag r3
python scripts/drive_v3.py --phase sweep  --seeds 1 2 --tag r3
# E7: the BEFORE commits of the predictor-upgrade repair (v2 caches, already on the laptop), then the repairs
foreach ($ts in 1, 2) { foreach ($ds in "mnist", "tabular:MiniBooNE", "tabular:adult") {
  $dsn = $ds -replace ":", "-"
  python scripts/commit_v3.py --dataset $ds --train-seed $ts --pool-dir F:/CAFA_results/pool_v2 --out-path configs/committed_v3before_${dsn}_ts$ts.json } }
python scripts/run_repairs_v3.py --seeds 1 2 --tag r3
python scripts/make_tables_v3.py --metrics-dir $env:RESULTS_ROOT/metrics_v3 --output-dir results_v3/tables --lambda-ref-key dep --scheme uniform
#   -> TABLE_E4_cascade.md (one row per dataset, policy, seed) and TABLE_E4_cascade_seeds.md (mean ± sd over seeds)
python scripts/report_violations_v3.py --metrics-dir $env:RESULTS_ROOT/metrics_v3 --lambda-ref-key dep --output results_v3/diagnostics/r3_violations_dep.md
python scripts/make_figures_v3.py --metrics-dir $env:RESULTS_ROOT/metrics_v3 --planted results_v3/planted --repair-dir results_v3/repair --output-dir results_v3/figures
# round 3 (instruction_round3.md Task J): E9 alpha-margin commits and sweeps for seeds 1-2 (MNIST / Imagenette
# refuse at margin 0.02 with rc 7, as at seed 0 -- run them last or leave them out of --datasets)
python scripts/drive_v3.py --phase commit --seeds 1 2 --commit-prefix committed_v3_am10 --tag r3am10 "--extra-args=--alpha-margin 0.10 --alpha-grid 0.05"
python scripts/drive_v3.py --phase sweep  --seeds 1 2 --commit-prefix committed_v3_am10 --metrics-dir-name metrics_v3_alpha_margin10 --tag r3am10
python scripts/drive_v3.py --phase commit --seeds 1 2 --commit-prefix committed_v3_am02 --tag r3am02 "--extra-args=--alpha-margin 0.02 --alpha-grid 0.01"
python scripts/drive_v3.py --phase sweep  --seeds 1 2 --commit-prefix committed_v3_am02 --metrics-dir-name metrics_v3_alpha_margin02 --tag r3am02
foreach ($ts in 1, 2) { python scripts/alpha_margin_summary_v3.py --train-seed $ts --output-dir results_v3/tables_e9_alpha_margin_ts$ts }
# E10 over all seeds (3 x 320 points; reads every seed present in metrics_v3) and F7
python scripts/margin_analysis_v3.py --metrics-dir $env:RESULTS_ROOT/metrics_v3 --calfrac-dir 0.25 $env:RESULTS_ROOT/metrics_v3_calfrac025 --calfrac-dir 1.0 $env:RESULTS_ROOT/metrics_v3_calfrac100 --output-dir results_v3/tables --figure results_v3/figures/F7_margin.pdf
```

The commits use the round-2 code: 5 test splits × 20 draws, the HB fix, `split` block; the sweeps use the round-3
code (the ex-post stratum-safe oracles of Task K are added to every metrics file). For the other λ_ref keys, the
cost scheme and the remaining E9 ablations, use the seed-0 commands of handoff.md §10 with `--seeds 1 2`.

## 8. Round 3, Task L — FashionMNIST predictor upgrade (seed 0, checkpoint tag `repair`)

This is the second E7 predictor-upgrade dataset (`instruction_round3.md`, Task L). A stronger FashionMNIST backbone
(`width_mult` 4, 60 epochs, `p_full` 0.3, same loader and split) is trained as a NEW checkpoint
`$RESULTS_ROOT/checkpoints_v3_repair/fashionmnist_ts0.pt`. The greedy and random rollouts use it and write
`pool_v3/fashionmnist_ts0_{greedy_entropy,random}-repair_softmax.npz`. `--checkpoint-tag repair` changes only the
checkpoint folder and the cache token suffix. The protocol seed-0 backbone and caches (made on the laptop) are never
overwritten, and `commit_v3.py` ignores tagged caches. The two jobs use seed-0 array indices: backbone task 6
(dataset index 6 = `fashionmnist`, seed 0) and rollout lines 12 and 13 of `hpc/cells_v3.txt` (`16·0 + 2·6 + 0/1`,
greedy and random). §4 says not to submit seed 0; that rule covers the untagged runs. Submit these indices only with
`CAFA_DRIVER_FLAGS="--checkpoint-tag repair"`, exactly as below. On the cluster they need only the FashionMNIST data
of §2. The repair itself runs on the laptop.

```bash
cd ~/my_repos/CAFA_exp
# backbone: fashionmnist seed 0, width 4, 60 epochs, p_full 0.3 -> checkpoints_v3_repair/fashionmnist_ts0.pt
BBR=$(CAFA_EXTRA="--epochs 60 --width-mult 4 --p-full 0.3" CAFA_DRIVER_FLAGS="--checkpoint-tag repair" \
      sbatch --parsable --export=ALL --time=08:00:00 --array=6 hpc/backbone_v3.slurm)
# rollouts with that backbone: greedy (line 12) and random (line 13) -> pool_v3/fashionmnist_ts0_{greedy_entropy,random}-repair_softmax.npz
CAFA_DRIVER_FLAGS="--checkpoint-tag repair" sbatch --export=ALL --dependency=afterok:${BBR} --time=24:00:00 \
      --array=12,13 hpc/rollout_v3.slurm
squeue -u $USER
```

- `CAFA_EXTRA` reaches `train_backbone_v3.py` through the driver's `--extra-args`. Both batch scripts append
  `CAFA_DRIVER_FLAGS` to the driver call, so `--checkpoint-tag repair` reaches `drive_v3.py`. The driver then uses the
  tagged output and prerequisite paths and passes the flag on to the script. Ledger cells:
  `backbones:fashionmnist:na-repair:ts0` and `rollouts:fashionmnist:{greedy_entropy,random}-repair:ts0`.
- Set both variables only in front of `sbatch`, as above. Never `export` them in the login shell: an exported
  `CAFA_DRIVER_FLAGS` would tag every later submission.
- Dry run of exactly these two lines (no Slurm, no GPU; prints the tagged checkpoint path and the overrides;
  covered by `tests/test_hpc_v3.py::test_hpc_dry_run_task_l_lines`):
  ```bash
  BB_INDICES=6 RO_INDICES="12 13" BB_EXTRA="--epochs 60 --width-mult 4 --p-full 0.3" \
    DRY_DRIVER_FLAGS="--checkpoint-tag repair" PYTHON=python bash hpc/dry_run_v3.sh
  ```
  It prints `would run backbones:fashionmnist:na-repair:ts0: python scripts/train_backbone_v3.py --dataset fashionmnist
  --train-seed 0 --device cuda --checkpoint-tag repair --epochs 60 --width-mult 4 --p-full 0.3 [output:
  …/checkpoints_v3_repair/fashionmnist_ts0.pt]`, and for both rollouts `--checkpoint-tag repair` with
  `[prerequisite missing now: checkpoints_v3_repair/fashionmnist_ts0.pt]` until the backbone exists.

Expected wall times. These are **estimates, not measurements**. They start from the round-1 laptop ledger for the
width-2 FashionMNIST seed-0 cells (RTX 3050 4 GB, thermally throttled): backbone 1,602.9 s for 30 epochs, greedy
rollout 14,565.1 s, random rollout 308.2 s. Width 4 costs roughly 4× the conv FLOPs (they grow with input × output
channels) and 60 epochs cost 2×. Dividing by the throttling factor 1.4178 of §5 gives the full-clock laptop figure.

| job | laptop ledger (width 2) | scaling | throttled-laptop estimate | full-clock laptop estimate | `--time` |
|---|---|---|---|---|---|
| backbone (task 6) | 1,602.9 s (30 epochs) | × 4 (width) × 2 (epochs) | 12,823 s (3.56 h) | 9,045 s (2.51 h) | 08:00:00 |
| greedy rollout (line 12) | 14,565.1 s | × 4 (width) | 58,260 s (16.18 h) | 41,093 s (11.41 h) | 24:00:00 |
| random rollout (line 13) | 308.2 s | × 4 (width) | 1,233 s (0.34 h) | 870 s (0.24 h) | 24:00:00 (same array job) |

Measured smoke on the laptop (round 3, 2026-10-03; documented smoke flags, separate tag `smokerepair`, outputs
deleted afterwards; logs `results_v3/logs/r3_taskL_smoke_{backbone,rollout_greedy,rollout_random,nvidia_smi}.log`):
width-4 backbone `--epochs 1 --max-train 2000` 85 s (8 optimizer steps; dominated by data loading, so it does not
time an epoch); greedy rollout `--max-rows 256` 361 s, i.e. 361 × 28,000 / 256 ≈ 39,500 s ≈ 11 h for the full
heldout split; random rollout `--max-rows 256` 23 s. During the smoke the GPU reported
`clocks_event_reasons.sw_thermal_slowdown = Active` in every busy sample (mean SM clock 521 MHz of 2,100, mean
87.9 °C). That is why these jobs are not run on the laptop (instruction.md §6: > 8 h per cell; instruction_round3.md
Task L: throttled GPU → cluster).

The TinyGPU GPUs are larger and faster than the laptop's, so treat these figures as planning bounds. The greedy
rollout is the critical path. `--time=24:00:00` assumes a 24 h walltime limit on the TinyGPU partition you submit to
(check the current limit in the NHR documentation or with `sinfo -o "%P %l"` before submitting); it is about 2× the
full-clock estimate. A rollout writes its cache only at the end, so if line 12 hits the limit nothing partial is left
behind: resubmit line 12 alone with the same flags and the dependency removed.

What comes back (laptop, Git Bash). The checkpoint is optional because the cache meta records its sha256,
`checkpoint_tag` and `checkpoint_dir`. Take the cluster's ledger lines and logs as in §6.

```bash
H=<user>@tinyx.nhr.fau.de
scp "$H:/home/vault/iwi5/<user>/CAFA_results/pool_v3/fashionmnist_ts0_*-repair_softmax.npz" /f/CAFA_results/pool_v3/
mkdir -p /f/CAFA_results/checkpoints_v3_repair
scp "$H:/home/vault/iwi5/<user>/CAFA_results/checkpoints_v3_repair/fashionmnist_ts0.pt" /f/CAFA_results/checkpoints_v3_repair/   # optional
```

Local follow-up (PowerShell, repo root). `check_caches_v3.py` checks the tagged pair as its own group
(`fashionmnist ts0 [repair]`: greedy = random full-acquisition accuracy) and never compares it with the untagged pair.
The repair then audits the tagged caches on the round-2 strata: BEFORE = `pool_v3/fashionmnist_ts0_{pol}_softmax.npz`
on `configs/committed_v3_fashionmnist_ts0.json` (`--policy {pol}`), AFTER = `pool_v3/fashionmnist_ts0_{pol}-repair_softmax.npz`.

```powershell
. .\set_env.ps1
python scripts/check_caches_v3.py
python scripts/run_repairs_v3.py --seeds 0 --datasets fashionmnist --repair-tag repair --tag r3L
#   -> results_v3/repair/fashionmnist_ts0_predictor_upgrade.json (greedy) and fashionmnist_ts0_predictor_upgrade_random.json (random)
```

The same two jobs on the laptop instead, if its GPU is not throttled (same flags, same outputs):

```powershell
python scripts/drive_v3.py --phase backbones --seeds 0 --datasets fashionmnist --checkpoint-tag repair --extra-args="--epochs 60 --width-mult 4 --p-full 0.3" --tag r3L
python scripts/drive_v3.py --phase rollouts  --seeds 0 --datasets fashionmnist --checkpoint-tag repair --tag r3L
```
