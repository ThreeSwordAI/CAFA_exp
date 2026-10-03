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
Seed 0 (tasks 0–7 and 0–15) is done locally. **Do not submit them.**

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
```

The commits use the round-2 code: 5 test splits × 20 draws, the HB fix, `split` block. For the other λ_ref keys,
the cost scheme and the E9 ablations, use the seed-0 commands of handoff.md §10 with `--seeds 1 2`.
