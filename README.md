# CAFA — Conformal Active Feature Acquisition (CAFA)

A distribution-free stopping rule for active feature acquisition: instead of stopping acquisition on a heuristic confidence threshold, CAFA selects the **cheapest** threshold whose prediction-at-stop **provably** controls a target risk α with confidence 1−δ, using Learn-then-Test.

> **Status: Step 1** — the core risk-control method and its synthetic validity gate. **No deep learning yet** (backbones, datasets, and acquisition policies arrive in later steps). The point of this step is to prove the finite-sample guarantee is implemented correctly *before* any model exists.

---

## What's in this step

- **`src/cafa/risk_control.py`** — the pure method. Hoeffding–Bentkus p-values, FWER control (fixed-sequence / Bonferroni), and selection of the cheapest risk-valid stopping threshold. It depends only on `numpy`/`scipy` — no torch, no data, no models — so it can be tested in isolation.
- **`src/cafa/data.py`** — a synthetic generator with a **known true risk curve**, so validity can be checked exactly.
- **`tests/test_risk_control.py`** — the validity gate (**G1**): across ≥1000 synthetic calibration draws, the fraction where the selected threshold's *true* risk exceeds α must be ≤ δ.

---

## Install

```bash
# FAU NHR (TinyGPU / Alex):
module load python/3.12-conda
conda env create -p "$CAFA_ENV" -f environment.yml      # one time
source activate "$CAFA_ENV"

# On a laptop instead:
# conda env create -f environment.yml && conda activate cafa
```

Step 1 needs only `numpy`, `scipy`, `pyyaml`, `pytest` (no GPU, no PyTorch).

---

## Paths (nothing machine-specific is committed)

All paths come from environment variables; the repo ships only `configs/paths.template.yaml`. Set these once (examples for FAU NHR — point them anywhere):

```bash
export DATA_ROOT=/home/woody/iwi5/<user>/CAFA_data       # data on woody
export RESULTS_ROOT=/home/vault/iwi5/<user>/CAFA_results # results on vault
export CAFA_ENV=/home/vault/iwi5/<user>/envs/cafa              # conda env on vault
export CAFA_REPO=/home/hpc/iwi5/<user>/my_repos/CAFA_exp
```

Step 1 barely touches these, but later steps need them. `config.py` resolves env vars first, then a local (gitignored) `configs/paths.yaml`.

---

## Run the gate (G1)

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
pytest -q
```

**Passing means the distribution-free guarantee is correctly implemented:** over ≥1000 synthetic calibration draws, the fraction where the selected threshold's *true* risk exceeds α is ≤ δ, the cost-minimizing selection returns the cheapest valid threshold, and both FWER procedures control risk on monotone and non-monotone risk curves.

**Do not proceed to Step 2 until G1 passes** — everything downstream feeds arrays into this module, so its correctness is the foundation.

---

## Layout (Step 1)

```
CAFA_exp/
├── README.md
├── environment.yml
├── .gitignore
├── configs/
│   ├── paths.template.yaml     # placeholders only — no real paths
│   └── experiment.yaml         # alpha, delta, grid, seeds (full target config; method+protocol used now)
├── src/cafa/
│   ├── __init__.py
│   ├── config.py               # env-var path resolution + experiment config + seeding
│   ├── data.py                 # synthetic generator with known true risk
│   ├── risk_control.py         # ★ the method (pure arrays): LTT p-values, FWER, cost-min selection
│   └── metrics.py              # empirical risk, expected cost, violation rate
└── tests/
    └── test_risk_control.py    # ★ G1 validity gate
```

---

## Roadmap

| Step | Adds |
|---|---|
| **1 (here)** | core method + synthetic validity gate (no DL) |
| 2 | masked predictor + one acquisition policy + rollout, end-to-end on MNIST (TinyGPU) |
| 3 | per-budget (Mondrian) coverage — the contribution's centerpiece |
| 4 | all datasets, second backbone, all baselines, full array sweep |
| 5 | covariate-shift robustness (weighted-CAFA) + ablations |
| 6 | figures finalized + reproducibility polish → publication repo |

The full build plan, math, and per-step file breakdown live in `cafa_repo_design.md`.

---

## Design rule that carries through every step

`src/cafa/risk_control.py` is **pure** — arrays in, selection out — and is **not edited after Step 3**. Everything else (data, models, policies) exists only to feed it `(loss, cost)` matrices. That isolation is what makes the guarantee testable in Step 1 and what lets the method run unchanged on any dataset later.