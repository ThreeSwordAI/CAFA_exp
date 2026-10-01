# CAFA v3 — Phased execution plan (AISTATS resubmission)

This file is the operational companion to `CAFA_AISTATS2027_Revision_Plan.md`.
Every command below is run from the repo root (`F:\FAU\PhD\Side Quest\CAFA_exp` locally;
the cloned repo on TinyGPU). Set the two roots first (or `configs/paths.yaml`):

```
export DATA_ROOT=/path/to/CAFA_data        # Windows PowerShell: $env:DATA_ROOT="F:\CAFA_data"
export RESULTS_ROOT=/path/to/CAFA_results  #                     $env:RESULTS_ROOT="F:\CAFA_results"
```

Conventions used throughout: `{ds}` ranges over the v3 datasets, `{ts}` over train seeds `0 1 2`,
`{pol}` over `greedy_entropy random`. Caches land in `${RESULTS_ROOT}/pool_v3/`, checkpoints in
`${RESULTS_ROOT}/checkpoints_v3/`, metrics in `${RESULTS_ROOT}/metrics_v3/`, everything else in `results_v3/`.
Nothing in `src/cafa/risk_control.py` is touched; all v3 code is additive.

| Dataset token | kind | T | n total | heldout (40%) | cal pool / test | notes |
|---|---|---|---|---|---|---|
| `mnist` | 7x7 patches | 49 | 70,000 | 28,000 | 12,600 / 12,600 | v3 backbone replaces the AAAI CNN |
| `fashionmnist` | 7x7 patches | 49 | 70,000 | 28,000 | 12,600 / 12,600 | new |
| `image:imagenette` | RGB 224, 7x7 patches | 49 | 13,394 | 5,358 | 2,411 / 2,411 | ResNet-18, GPU |
| `tabular:MiniBooNE` | OpenML | 50 | 130,064 | 52,026 | 23,411 / 23,412 | existing loader |
| `csv:physionet` | AFABench CSV | 41 | 12,000 | 4,800 | 2,160 / 2,160 | tier-3 expected |
| `csv:diabetes` | AFABench CSV | 45 | 92,062 | 36,825 | 16,571 / 16,572 | 3 classes |
| `cube` | synthetic (AFABench law) | 20 | 20,000 | 8,000 | 3,600 / 3,600 | E5 uses `synthetic_planted` instead |
| `tabular:adult` | OpenML | 14 | 48,842 | 19,537 | 8,792 / 8,792 | appendix continuity + E7 "before" |

Where to run what (RTX 3050 laptop vs. TinyGPU):

| Step | Local (RTX 3050) | TinyGPU | Recommendation |
|---|---|---|---|
| Phase 0 tests + synthetic smoke | 5 min | — | local |
| Backbones: tabular/cube/MNIST/FashionMNIST | 2–20 min each | 1–5 min | local |
| Backbone: Imagenette ResNet-18 (12 epochs, AMP) | ~25 min | ~6 min | either |
| Rollouts: tabular/cube (greedy) | 5–40 min each (MiniBooNE/Diabetes longest, CPU-bound batches) | 2–10 min | local or array job |
| Rollouts: MNIST/FashionMNIST greedy (28k x 1,225 passes) | ~1 h each | ~15 min | either |
| Rollout: Imagenette greedy (5.4k x 1,225 ResNet passes) | 4–7 h each | 45–90 min | **TinyGPU** |
| Random-policy rollouts | ~1/50 of greedy | — | local |
| Phase 2 (E5, CPU) | 1–2 h | 20 min | local overnight or 1 CPU job |
| Phase 3 (commit/sweep/audit/tables, CPU) | 2–10 min per cell | — | local |
| External policies (AFABench GDFS/AACO) | hours (their training) | hours | TinyGPU, optional |

Full 3-seed grid: 8 datasets x 2 policies x 3 seeds = 48 rollouts. Everything except Imagenette
fits in a few evenings locally; with TinyGPU the whole grid is one afternoon of array jobs.

---

## Phase 0 — Drop-in and verification (local, ~15 minutes)

1. Copy the v3 tree into the repo (see `V3_FILE_MANIFEST.md`): `src/cafa/*.py` (9 new modules),
   `scripts/*.py` (13 new scripts), `tests/*.py` (9 new tests), `configs/experiment_v3.yaml`,
   `PHASES_V3.md`, `V3_FILE_MANIFEST.md`. No existing file is modified.
2. Tests (torch-free ones take ~15 s; `test_models_v3.py` needs torch and takes ~1 min):
   ```
   python -m pytest -q tests/test_cascade.py tests/test_localization.py tests/test_commit_rules.py \
       tests/test_splits_v3.py tests/test_planted.py tests/test_hidden_risk.py tests/test_data_v3.py \
       tests/test_external_orders.py tests/test_models_v3.py
   python -m pytest -q tests/        # whole suite incl. v2 (≈3 min; the two v2 policy-honesty probes need torch)
   ```
   Acceptance: all pass (29 torch-free + 3 torch).
3. Synthetic end-to-end ("Tier A") on CPU, seconds:
   ```
   python scripts/make_synthetic_pool_cache.py --pool-dir $RESULTS_ROOT/pool_v3 --n 8000 --scenario typeII
   python scripts/commit_v3.py --dataset synthetic-planted --train-seed 0 --force
   python scripts/run_cascade_sweep.py --dataset synthetic-planted --policy greedy_entropy --train-seed 0 --n-draws 20
   python scripts/make_tables_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --output-dir results_v3/tables_smoke
   ```
   Acceptance: console shows `deepest stratum verdict=type_II` and `tiers={'3': ≥0.8}` with `viol=0.000`.
   Repeat with `--scenario feasible` (after `--force` re-commit): expect `'1': 1.0`.
   Delete the synthetic cache/commit afterwards so it does not pollute the real grid:
   `rm $RESULTS_ROOT/pool_v3/synthetic-planted_* configs/committed_v3_synthetic-planted_ts0.json $RESULTS_ROOT/metrics_v3/synthetic-planted_*`.

---

## Phase 1 — Data, backbones, rollouts (GPU; local or TinyGPU)

### 1a. One-time data fetch (login node or laptop, ~10 min + Imagenette download)
```
python scripts/download_data_v3.py --csv --mnist --fashionmnist --openml
python scripts/download_data_v3.py --imagenette          # ~330 MB archive; builds imagenette_cache/imagenette_224.npz (~2 GB)
```
`cube` needs nothing. `tabular:adult` / `spambase` come from the v2 OpenML cache.

### 1b. Backbones (one checkpoint per dataset x train seed)
```
for ts in 0 1 2; do
  python scripts/train_backbone_v3.py --dataset mnist             --train-seed $ts --device cuda
  python scripts/train_backbone_v3.py --dataset fashionmnist      --train-seed $ts --device cuda
  python scripts/train_backbone_v3.py --dataset image:imagenette  --train-seed $ts --device cuda
  python scripts/train_backbone_v3.py --dataset tabular:MiniBooNE --train-seed $ts --device cuda
  python scripts/train_backbone_v3.py --dataset csv:physionet     --train-seed $ts --device cuda
  python scripts/train_backbone_v3.py --dataset csv:diabetes      --train-seed $ts --device cuda
  python scripts/train_backbone_v3.py --dataset cube              --train-seed $ts --device cuda
  python scripts/train_backbone_v3.py --dataset tabular:adult     --train-seed $ts --device cuda
done
```
Smoke first: add `--epochs 1 --max-train 2000` to one command of each kind (patches / rgb / tabular) and check it
writes `${RESULTS_ROOT}/checkpoints_v3/{dsname}_ts0.pt`.
Acceptance (printed `full_obs_acc` on train): MNIST ≥ 0.995, FashionMNIST ≥ 0.93, Imagenette ≥ 0.95
(pretrained ResNet-18 on train), MiniBooNE ≥ 0.93, PhysioNet ≥ 0.86, Diabetes ≥ 0.85, CUBE ≥ 0.98, Adult ≥ 0.85.
If MNIST/FashionMNIST full-observation accuracy is below target, raise `training_v3.image_patches.epochs` to 40.

### 1c. Rollouts (the expensive step; order = the artifact)
```
for ts in 0 1 2; do for pol in greedy_entropy random; do
  python scripts/run_pool_rollout_v3.py --dataset mnist             --policy $pol --train-seed $ts --device cuda
  python scripts/run_pool_rollout_v3.py --dataset fashionmnist      --policy $pol --train-seed $ts --device cuda
  python scripts/run_pool_rollout_v3.py --dataset image:imagenette  --policy $pol --train-seed $ts --device cuda --batch-size 32
  python scripts/run_pool_rollout_v3.py --dataset tabular:MiniBooNE --policy $pol --train-seed $ts --device cuda
  python scripts/run_pool_rollout_v3.py --dataset csv:physionet     --policy $pol --train-seed $ts --device cuda
  python scripts/run_pool_rollout_v3.py --dataset csv:diabetes      --policy $pol --train-seed $ts --device cuda
  python scripts/run_pool_rollout_v3.py --dataset cube              --policy $pol --train-seed $ts --device cuda
  python scripts/run_pool_rollout_v3.py --dataset tabular:adult     --policy $pol --train-seed $ts --device cuda
done; done
```
Smoke first with `--max-rows 256` on one dataset of each kind (the cache is then partial — delete it before the real run).
Slurm array template for TinyGPU (48 cells; put the 8 x 2 x 3 combinations in a text file, one per line):
```
#!/bin/bash
#SBATCH --job-name=cafa_v3_rollout --gres=gpu:1 --time=08:00:00 --array=0-47
module load python/3.12 cuda; source $WORK/cafa_env/bin/activate
export DATA_ROOT=$WORK/CAFA_data RESULTS_ROOT=$WORK/CAFA_results
read ds pol ts < <(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" hpc/cells_v3.txt)
python scripts/run_pool_rollout_v3.py --dataset $ds --policy $pol --train-seed $ts --device cuda
```
Acceptance: 48 files `${RESULTS_ROOT}/pool_v3/{dsname}_ts{ts}_{pol}_softmax.npz`; the printed full-acquisition
accuracy on heldout equals the greedy and random caches of the same (dataset, seed) up to 1e-12 (same predictor,
same final observed set).

### 1d. External policies (optional; appendix; TinyGPU)
Only for tabular datasets; adds the "published policy" row the plan asks for. Steps:
```
python scripts/export_heldout_v3.py --dataset csv:physionet --train-seed 0 --out orders/physionet_ts0_heldout.npz
# inside the AFABench checkout (uv env):
uv run python /path/to/CAFA_exp/scripts/afabench_export_orders.py --heldout .../physionet_ts0_heldout.npz \
    --bundle extra/output/methods/gdfs/physionet/seed0.bundle --policy afabench_gdfs --out .../physionet_ts0_afabench_gdfs.npz
# back in CAFA_exp:
python scripts/run_pool_rollout_v3.py --dataset csv:physionet --orders-file orders/physionet_ts0_afabench_gdfs.npz \
    --policy-token afabench_gdfs --train-seed 0 --device cuda
```
`afabench_export_orders.py` follows AFABench's `AFAMethod.act` / `load_bundle` API at commit 8ebf5e9 and must be
validated inside that environment (it could not be executed here). If AFABench's own train/val/test split is used to
train the method, say so in the appendix ("policy trained on the benchmark split; evaluated on our heldout rows").
Skip this step entirely if time is short — nothing in Phases 2–3 depends on it.

---

## Phase 2 — E5 planted validity/power study (CPU, 1–2 h)
```
python scripts/planted_validation.py --output-dir results_v3/planted --n-replicates 1000
```
Writes `results_v3/planted/planted_validation.csv` + `PLANTED_VALIDATION.md`.
Acceptance: study A false-failure rate ≤ 0.05 at every n_k (expect ≈ 0.00–0.02); cascade violation rate ≤ 0.10
(expect ≈ 0); study B power increasing in n_k Δ², ≈ 0.9 at n_k Δ² ≈ 2.5, 1.0 at ≥ 10; study C escalation
rate → 1 as n_k grows, `unsafe|esc` ≈ 0.

---

## Phase 3 — Commit, certify-or-route sweep, audit, tables, repair (CPU, torch-free; ~1–2 h total)

### 3a. Probe commits (one JSON per dataset x seed; committed once)
```
for ts in 0 1 2; do for ds in mnist fashionmnist image:imagenette tabular:MiniBooNE csv:physionet csv:diabetes cube tabular:adult; do
  python scripts/commit_v3.py --dataset $ds --train-seed $ts
done; done
```
Each run prints α, the expected calibration size, n_min(tier 1), and per policy the four λ_ref keys
(`0.5 0.7 0.9 dep`) with the realized number of strata G and where the tier-3 walk starts.
Acceptance: `configs/committed_v3_{dsname}_ts{ts}.json` exists for all 24 cells; `G ≥ 2` for the `dep` key on every
dataset except possibly PhysioNet/CUBE (small pools); α equals the AAAI value where the dataset is shared (MNIST 0.10
only if the floor rule says so — the v3 backbone may lower the floor; report the rule, not the number).

### 3b. The sweep (100 calibration draws per cell; marginal + cascade + baselines + localized audit)
```
for ts in 0 1 2; do for pol in greedy_entropy random; do for ds in mnist fashionmnist image:imagenette tabular:MiniBooNE csv:physionet csv:diabetes cube tabular:adult; do
  python scripts/run_cascade_sweep.py --dataset $ds --policy $pol --train-seed $ts
done; done; done
```
(Add `--policy afabench_gdfs` cells if Phase 1d was run.) Output: `${RESULTS_ROOT}/metrics_v3/{dsname}_ts{ts}_{pol}_softmax.json`
with per-λ_ref blocks: audit (E3), marginal blindness numbers (E2), cascade summary (E4), baselines (E6), all draws.

### 3c. Tables and figures
```
python scripts/make_tables_v3.py  --metrics-dir $RESULTS_ROOT/metrics_v3 --output-dir results_v3/tables --lambda-ref-key dep --scheme uniform
python scripts/make_tables_v3.py  --metrics-dir $RESULTS_ROOT/metrics_v3 --output-dir results_v3/tables_inverse_info --lambda-ref-key dep --scheme inverse_info
python scripts/make_figures_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --planted results_v3/planted --repair-dir results_v3/repair --output-dir results_v3/figures
```
Headline acceptance (E4, `TABLE_E4_cascade.md`): `certified_deployment ≈ 1.00` in every cell; `test_stratum_violation ≤ 0.10`
everywhere; tier 1 dominant on MNIST/FashionMNIST/Imagenette/MiniBooNE/CUBE with `cost_premium` 1.0–1.6; tier 3 on
PhysioNet (and possibly Diabetes) with answered fraction reported. If any cell has `none > 0.05`, read its audit row:
`unresolved` means the stratum is undecided (report), `type_II` with `none > 0` means tier 3 could not certify any level —
check the escalation block of the committed JSON (`fractions_desc`, `order`) and the per-stratum answered counts.

### 3d. E7 audit-guided repair (the AAAI system as "before", the v3 system as "after")
The v2 caches `${RESULTS_ROOT}/pool_v2/{mnist,tabular-MiniBooNE,tabular-adult}_ts0_greedy_entropy_softmax.npz` cover the same
heldout rows in the same order as the v3 caches (same loader, same train seed), so the before-system strata apply to both.
```
for ds in mnist tabular:MiniBooNE tabular:adult; do
  dsn=$(echo $ds | sed 's/tabular:/tabular-/')
  python scripts/commit_v3.py --dataset $ds --train-seed 0 --pool-dir $RESULTS_ROOT/pool_v2 --out-path configs/committed_v3before_${dsn}_ts0.json
  python scripts/repair_experiment.py --dataset $ds --train-seed 0 \
      --before-cache $RESULTS_ROOT/pool_v2/${dsn}_ts0_greedy_entropy_softmax.npz \
      --after-cache  $RESULTS_ROOT/pool_v3/${dsn}_ts0_greedy_entropy_softmax.npz \
      --committed configs/committed_v3before_${dsn}_ts0.json --label predictor_upgrade
done
```
Expected: MNIST deepest stratum `type_II` → `feasible` (family minimum from ≈ 0.32 to < 0.10) and tier-1 share 0 → ≈ 1;
Adult stays infeasible (irreducible floor ≈ 0.15 at α = 0.20? — if it stays Type II the repair text says "information floor,
not a model defect"); MiniBooNE: report whatever the audit says. A second repair pair (policy change: `random` → `greedy_entropy`
within v3) uses `--after-cache ..._greedy_entropy_...` against `--before-cache ..._random_...` with the before commit made on
the random cache (`--policy random` in `repair_experiment.py`).

### 3e. E9 sensitivity (appendix; cheap)
```
# delta split
python scripts/run_cascade_sweep.py --dataset csv:physionet --policy greedy_entropy --train-seed 0 --delta-weights 0.34,0.33,0.33 --out-dir $RESULTS_ROOT/metrics_v3_dw
# number of strata
python scripts/commit_v3.py --dataset mnist --train-seed 0 --n-buckets 8 --out-path configs/committed_v3_G8_mnist_ts0.json
python scripts/run_cascade_sweep.py --dataset mnist --policy greedy_entropy --train-seed 0 --committed configs/committed_v3_G8_mnist_ts0.json --out-dir $RESULTS_ROOT/metrics_v3_G8
# lambda_ref sweep and cost schemes are already inside every metrics JSON (keys 0.5 / 0.7 / 0.9 / dep; schemes uniform / inverse_info)
```

---

## Phase 4 — Writing and compliance (no compute)

1. Start from `AISTATS2027PaperPack/sample_paper.tex` (8 pages + references + appendix). Section plan and clarity rules:
   revision plan §8; terminology table §8.2; scope box §8.3.
2. Numbers: every bracketed number in the abstract/contributions comes from `results_v3/tables/TABLE_E4_cascade.csv`
   (certified deployment, tier-1 share, cost premium), `TABLE_E2_blindness.csv` (max stratum risk / α),
   `TABLE_E3_audit.csv` (verdicts), `PLANTED_VALIDATION.md` (E5), `results_v3/repair/*.json` (E7). Keep the
   "Reporting rule" of plan §7: no number in the paper without a file in `results_v3/`.
3. Figure 1 (strata-by-rules matrix + pipeline): draw in TikZ from the sketch in plan §5; Figures 2–5 from `make_figures_v3.py`.
4. Mandatory AISTATS 2027 items: AI Use Statement; reciprocal-reviewing acknowledgement; author list fixed at abstract
   registration; anonymized code appendix (scrub every "AAAI", "26549", author names and institution strings from
   README/results/docstrings before zipping: `grep -rn "AAAI\|26549" --include=*.md --include=*.py .`).
5. Defense: plan §9 (prepared answers incl. "tier-3 order is precommitted from the probe", "strata are not fairness groups").

---

## Deliverables checklist

- [ ] Phase 0: tests green; synthetic Type-II routes to tier 3; synthetic feasible deploys tier 1
- [ ] Phase 1: 24 checkpoints, 48 caches (+ optional external-policy caches)
- [ ] Phase 2: `results_v3/planted/PLANTED_VALIDATION.md`
- [ ] Phase 3: 24 committed JSONs, 48 metrics JSONs, `results_v3/tables/TABLE_E{2,3,4,6}_*.md`, `results_v3/figures/F{2,3,4,5}_*.pdf`, `results_v3/repair/*.json`
- [ ] Phase 4: paper draft with every number traceable to a file in `results_v3/`
