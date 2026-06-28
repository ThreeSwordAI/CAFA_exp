# CAFA — Conformal Active Feature Acquisition (CAFA)

A distribution-free stopping rule for active feature acquisition: instead of stopping acquisition on a heuristic confidence threshold, CAFA selects the **cheapest** threshold whose prediction-at-stop **provably** controls a target risk α with confidence 1−δ, using Learn-then-Test.

> **Status: Step 2** — the real machinery that produces the selector's input arrays on MNIST: a **masked predictor**, one **acquisition policy** (EDDI-style greedy entropy) + a random baseline, readiness **scores**, and a **rollout** that turns *(predictor, policy, score)* into the `(loss, cost, stop_depth)` matrices the frozen selector consumes. The pure risk-control core from Step 1 is unchanged and still gated by G1.

---

## What's in this step

**Frozen from Step 1 (do not edit):**
- **`src/cafa/risk_control.py`** — the pure method. Hoeffding–Bentkus p-values, FWER control (fixed-sequence / Bonferroni), and selection of the cheapest risk-valid stopping threshold. `numpy`/`scipy` only — no torch.
- **`tests/test_risk_control.py`** — the Step-1 validity gate (**G1**).

**New in Step 2:**
- **`src/cafa/models.py`** — `MaskedPredictor`, a small 2-channel CNN that classifies from any observed subset of the 49 patches (incl. empty/full), trained with random patch masking. Owns the patch geometry shared across the package.
- **`src/cafa/acquisition.py`** — `GreedyEntropyPolicy` (primary, deterministic, myopic EDDI-style) and `RandomPolicy`, the `rollout` that records per-step readiness/correctness/cost, and `stops_from_grid` that derives the selector's `(losses, costs, stop_depth)` arrays from one rollout.
- **`src/cafa/scores.py`** — readiness scores `softmax` (default), `margin`, `entropy` (all in `[0,1]`), plus a `set_size` stub; `get_score_fn(name)` dispatcher.
- **`src/cafa/data.py`** — adds `load_mnist_afa` (patchified MNIST, **disjoint** train/cal/test per seed, uniform per-feature costs); synthetic Step-1 code is untouched.
- **`scripts/train_backbone.py`**, **`scripts/run_experiment.py`** — train the predictor once, then run the end-to-end MNIST experiment per protocol seed.
- **`tests/test_pipeline.py`** — fast smoke test (dummy predictor, no training): rollout → grid → `ltt_select` wired with correct shapes/semantics.

### MNIST as an AFA problem
Each 28×28 image is a **7×7 grid of 4×4 patches = 49 features**; acquiring a patch reveals its 16 pixels. Uniform cost `c_a = 1` per patch (`cost_model: uniform`).

---

## Install

```bash
# FAU NHR (TinyGPU / Alex): add torch to the existing vault env (do NOT recreate it).
module load python/3.12-conda
source activate "$CAFA_ENV"
pip install torch torchvision
#   ...or the CUDA build:
#   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# On a laptop instead:
# conda env create -f environment.yml && conda activate cafa
```

`environment.yml` now lists `torch` + `torchvision` (pip section). The pure path (risk control, synthetic data, metrics, scores) still imports without torch; `cafa.models` / `cafa.acquisition` import torch lazily on first use.

---

## Paths (nothing machine-specific is committed)

All paths come from environment variables; the repo ships only `configs/paths.template.yaml`.

```bash
export DATA_ROOT=/home/woody/iwi5/<user>/CAFA_data       # data on woody
export RESULTS_ROOT=/home/vault/iwi5/<user>/CAFA_results # results on vault
export CAFA_ENV=/home/vault/iwi5/<user>/envs/cafa        # conda env on vault
export CAFA_REPO=/home/hpc/iwi5/<user>/my_repos/CAFA_exp
```

`config.py` resolves env vars first, then a local (gitignored) `configs/paths.yaml`. Checkpoints land in `${RESULTS_ROOT}/checkpoints`, per-seed metrics in `${RESULTS_ROOT}/metrics`.

---

## Run the gates

### G1 + smoke test (no GPU, no download)

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
pytest -q                       # G1 (test_risk_control.py) + smoke test (test_pipeline.py)
```

### End-to-end on MNIST (G2)

```bash
# one-time, on a login node (internet): download MNIST into $DATA_ROOT
python -c "import torchvision,os; r=os.environ['DATA_ROOT']; \
  torchvision.datasets.MNIST(r,train=True,download=True); \
  torchvision.datasets.MNIST(r,train=False,download=True)"

# train the masked predictor once (CPU is fine for MNIST; --download also works)
python scripts/train_backbone.py --dataset mnist --backbone greedy_entropy --download --device cpu

# run every protocol seed and print the G2 summary
python scripts/run_experiment.py --dataset mnist --backbone greedy_entropy --all-seeds --device cpu
```

Use `--device cuda` on a GPU node (e.g. `salloc.tinygpu --gres=gpu:1 --time=00:30:00`, no `--mem`/partition flags). On the cluster, submit via `hpc/train.slurm` and `hpc/sweep.slurm` (path-free; pass log paths at submit time).

**G2 (the exit gate):** the `--all-seeds` summary reports the fraction of seeds whose **held-out realized risk exceeds α** — this must be **≤ δ** — together with mean realized cost and mean stop depth (which should be **< 49**, i.e. the policy stops early and saves cost). If validity fails (> δ), it is a pipeline bug (split leakage, a non-frozen model, or a shape/semantics error in `stops_from_grid`) — fix the pipeline, **not** the selector.

---

## Layout (Step 2)

```
CAFA_exp/
├── README.md
├── environment.yml             # python + numpy/scipy/pyyaml/pytest + torch/torchvision
├── .gitignore
├── configs/
│   ├── paths.template.yaml     # placeholders only — no real paths
│   └── experiment.yaml         # method + protocol + datasets/backbones/scores/training
├── src/cafa/
│   ├── __init__.py             # pure exports eager; models/acquisition lazy (torch)
│   ├── config.py               # env-var path resolution + experiment config + seeding
│   ├── data.py                 # synthetic (Step 1) + load_mnist_afa (Step 2)
│   ├── risk_control.py         # ★ FROZEN — the method (pure arrays)
│   ├── metrics.py              # risk/cost/violation + cost-at-selected / pareto-point
│   ├── models.py               # ★ MaskedPredictor + patch geometry
│   ├── acquisition.py          # ★ policies + rollout + stops_from_grid
│   └── scores.py               # readiness scores + get_score_fn
├── scripts/
│   ├── train_backbone.py       # train the masked predictor → checkpoint + metadata
│   └── run_experiment.py       # rollout → grid → ltt_select → realized test risk (G2)
├── hpc/
│   ├── train.slurm             # path-free; log paths at submit time
│   └── sweep.slurm             # array job over protocol seeds
└── tests/
    ├── test_risk_control.py    # ★ FROZEN — G1 validity gate
    └── test_pipeline.py        # smoke test: rollout → stops_from_grid → ltt_select
```

---

## Roadmap

| Step | Adds |
|---|---|
| 1 | core method + synthetic validity gate (no DL) |
| **2 (here)** | masked predictor + one acquisition policy + rollout, end-to-end on MNIST (TinyGPU) |
| 3 | per-budget (Mondrian) coverage — the contribution's centerpiece |
| 4 | all datasets, second backbone, all baselines, full array sweep |
| 5 | covariate-shift robustness (weighted-CAFA) + ablations |
| 6 | figures finalized + reproducibility polish → publication repo |

---

## Design rule that carries through every step

`src/cafa/risk_control.py` is **pure** — arrays in, selection out — and is **not edited after Step 3**. Everything else (data, models, policies) exists only to feed it `(loss, cost)` matrices. That isolation is what makes the guarantee testable in Step 1 and what lets the method run unchanged on any dataset later.