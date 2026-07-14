# S5_answer.md -- Verified experimental specification (source material only)

Every value below is read from the repository (code, committed configs,
canonical result artifacts under `results_committed/`, or documentation).
Paths are repo-relative. No value is inferred from convention; unresolved
items are marked NOT FOUND or CONFLICT. "Canonical result freeze" refers to
the committed `results_committed/` artifact set with the frozen-core hashes
recorded in `repro/MANIFEST.sha256`.

---

## 1. Dataset specification

### 1.1 Dataset identity

**MNIST**
- Name in code: `mnist` (`scripts/run_pool_rollout.py`, `src/cafa/data.py::load_mnist_pool`).
- Source: `torchvision.datasets.MNIST`, official train and test sets concatenated (`src/cafa/data.py::load_mnist_pool`).
- Version/ID: torchvision loader default; no explicit version pin beyond the environment lock (`repro/requirements.lock.txt`: torchvision==0.25.0).
- Original examples: 70,000 (verified: train split 42,000 + heldout 28,000 = 70,000; `results_committed/metrics/mnist_ts0_greedy_entropy.json` meta + checkpoint meta n_train).
- Original variables: 28x28 = 784 pixels (patchified; see 1.3).
- Classes: 10 (`n_classes` in pool loader and checkpoint meta).
- Label mapping: torchvision integer digit labels 0-9, used as-is.
- Filtering/subsampling/balancing: none (all 70,000 rows used).

**Adult**
- Name in code: `tabular:adult` / dsname `tabular-adult`.
- Source: OpenML via `sklearn.datasets.fetch_openml(name='adult', version=2)` (`src/cafa/data.py::load_tabular_pool` + `openml_spec_for`; `configs/experiment.yaml` datasets_tabular: `{name: adult, source: openml, version: 2}`).
- OpenML data_id: not set (config `data_id` absent; fetch is by name+version).
- Original examples BEFORE missing-value filtering: NOT FOUND in repo artifacts (the loader drops rows before any count is persisted). Post-filter total: 45,222 (train 27,133 + heldout 18,089; `configs/committed_v2_tabular-adult_ts0.json` cache_meta + checkpoint meta).
- Original variables: 14 acquirable feature columns + 1 target (metrics meta T = 14).
- Classes: 2.
- Label mapping: `y = frame[target].astype('category').cat.codes` -- integer codes in the lexicographic order of the category values (`src/cafa/data.py`). Exact original label strings: NOT FOUND in stored artifacts (rule is verifiable in code; strings are not persisted).
- Filtering: rows with ANY missing feature value are dropped (`keep = ~X_df.isna().any(axis=1)`); no subsampling or balancing.

**MiniBooNE**
- Name in code: `tabular:MiniBooNE` / `tabular-MiniBooNE`.
- Source: OpenML `fetch_openml(name='MiniBooNE', version=1)` (`configs/experiment.yaml`).
- Post-filter total: 130,064 (78,038 + 52,026). Pre-filter count: NOT FOUND in artifacts (same reason as Adult).
- Variables: 50 numeric features; classes: 2; label mapping: category codes as above.
- Filtering: same missing-value row drop; no subsampling/balancing.

**Spambase**
- Name in code: `tabular:spambase` / `tabular-spambase`.
- Source: OpenML `fetch_openml(name='spambase', version=1)`.
- Post-filter total: 4,601 (2,761 + 1,840). Pre-filter: NOT FOUND in artifacts.
- Variables: 57 numeric features; classes: 2; label mapping: category codes.
- Filtering: same rule; no subsampling/balancing.

### 1.2 Final experimental sample sizes

Split rules (`src/cafa/splits.py`, `configs/experiment.yaml` protocol_v2):
train_frac 0.6 of the pooled data (permutation by `train_seed`); probe = 10%
of the heldout pool (fixed seed 777); post-probe evaluation pool = remaining
90%; per resplit, calibration = `int(round(0.5 * n_eval))`, test = the
remainder (Python banker's rounding at .5 -- observed only on MiniBooNE).

| dataset | train | validation | heldout | probe | post-probe pool | cal / resplit | test / resplit |
|---|---:|---|---:|---:|---:|---:|---:|
| MNIST | 42,000 | none used | 28,000 | 2,800 | 25,200 | 12,600 | 12,600 |
| Adult | 27,133 | none used | 18,089 | 1,809 | 16,280 | 8,140 | 8,140 |
| MiniBooNE | 78,038 | none used | 52,026 | 5,203 | 46,823 | 23,412 | 23,411 |
| Spambase | 2,761 | none used | 1,840 | 184 | 1,656 | 828 | 828 |

- Audit-specific subset: the family-wide audit uses the ENTIRE post-probe
  pool (no resplit); the confirmatory stratum is a subset of it (n_k in
  Section 12 Table A context: 5,479 / 6,268 / 9,180 / 249 at lambda_ref 0.9).
- Odd counts: MiniBooNE n_eval = 46,823 (odd); `round(23411.5)` = 23,412
  (round-half-to-even), test = 23,411. Verified arithmetic against
  `src/cafa/splits.py::resplit_cal_test`.
- Counts are identical across the three training seeds (same totals and
  fractions); the MEMBERSHIP of train/heldout differs by `train_seed`, and
  probe/eval positions within the heldout arrays are identical across seeds
  (probe permutation seeded 777 over positions).

### 1.3 Input representation and acquisition units

**MNIST**
- Image shape 28x28, single channel; pixels scaled to [0,1] by division by
  255 (`load_mnist_pool`); no other normalization; no augmentation.
- Patch size 4x4, stride 4 (non-overlapping), 7x7 grid = 49 patches of 16
  pixels; no border handling needed (28 divisible by 4); patch index
  p = r*7 + c row-major (`src/cafa/data.py::patchify_images`,
  `src/cafa/models.py::patches_to_image`).
- One acquisition unit = one 4x4 patch (16 pixels revealed jointly).
- Raw input dim 784; model input = two 28x28 channels (masked image +
  pixel-broadcast mask); acquirable units 49; all units always individually
  selectable; no ordering constraints beyond the policy.

**Adult**
- One acquisition unit = one ORIGINAL column (14 units); every one-hot block
  derived from a categorical column is revealed jointly
  (`feature_groups` in `load_tabular_pool`; `expand_feature_mask` in
  `src/cafa/tabular.py`).
- Encoded dimensionality: 104 columns (checkpoint meta `n_cols`; numerics
  standardized 1 column each, categoricals one-hot blocks).
- Original feature list / categorical-vs-numerical split: determined at load
  time by pandas dtype (`select_dtypes(include=['number'])` = numeric; rest
  categorical). The exact per-column lists are NOT persisted in artifacts;
  only the group WIDTHS are stored (checkpoint meta `feature_group_widths`).
  NOT FOUND as an explicit list.

**MiniBooNE / Spambase**
- All-numeric; one unit = one column; encoded dim = unit count (50 / 57);
  identity feature groups.
- All units always individually available; no acquisition-order constraints.

### 1.4 Preprocessing

Order (tabular, `src/cafa/data.py::load_tabular_pool`): (1) label
categorical-encode; (2) drop rows with any missing feature; (3) fixed
train/heldout split; (4) fit `StandardScaler` on numeric columns and
`OneHotEncoder(handle_unknown='ignore')` on categorical columns USING THE
FIXED TRAIN SPLIT ONLY; (5) transform train and heldout. No clipping, no log
transform, no class weighting/balancing, no deduplication.
MNIST: /255 scaling only; no standardization; no augmentation.
Preprocessing statistics are functions of `train_seed` only.

---

## 2. Predictor architecture

### 2.1 MNIST predictor

`src/cafa/models.py::MaskedPredictor`:
- features: Conv2d(2, 32, kernel 3, stride 1, padding 1) - ReLU -
  Conv2d(32, 32, 3, 1, 1) - ReLU - MaxPool2d(2) [28->14] -
  Conv2d(32, 64, 3, 1, 1) - ReLU - MaxPool2d(2) [14->7]
- head: AdaptiveAvgPool2d(1) - Flatten - Linear(64, 128) - ReLU -
  Dropout(0.2) - Linear(128, 10)
- Activations ReLU (inplace); no normalization layers; output dim 10 logits.
- Parameter count: NOT FOUND (not stored in any artifact).
- Mask input: two-channel input `[masked_image, pixel_mask]`
  (`build_inputs`): unobserved patches are ZEROED in the image channel and
  the per-patch 0/1 mask is broadcast to pixels as channel 2. The model
  receives both masked values and the binary mask.
- Initialization: PyTorch defaults (no special init in code).

### 2.2 Tabular predictors

One SHARED architecture class for all three datasets, instantiated per
dataset dimension (`src/cafa/models.py::TabularMaskedPredictor`):
- Linear(2*n_cols, 128) - ReLU - Linear(128, 128) - ReLU - Dropout(0.1) -
  Linear(128, n_classes); hidden dim 128; ReLU; no normalization layers.
- n_cols: 104 (Adult), 50 (MiniBooNE), 57 (Spambase); output dim 2.
- Parameter count: NOT FOUND (not stored).
- Mask input: input vector = concat(X * mask, mask) -- unobserved encoded
  columns are ZEROED (post-standardization zero = train mean for numerics)
  and the 0/1 column mask is appended, so the model distinguishes "true
  zero" from "unobserved". Whole one-hot blocks flip together.

### 2.3 Predictor outputs

- Networks output logits; `predict_proba` applies softmax
  (`torch.nn.functional.softmax`) and returns numpy probabilities.
- Predicted label: argmax of probabilities; ties broken by numpy argmax
  (lowest class index). Binary problems are handled as 2-class softmax
  (no sigmoid path). No output calibration (no temperature scaling etc.).

---

## 3. Model training

### 3.1 Training objective
- Loss: `nn.CrossEntropyLoss()` on logits; no class weights; no explicit
  regularization terms beyond dropout; no auxiliary losses. Masking enters
  only through the randomly masked inputs (Section 3.4).

### 3.2 Optimisation
- Optimizer: Adam, lr = 0.001 (`configs/experiment.yaml` training /
  training_tabular; `src/cafa/models.py` trainers). Weight decay: not set
  (PyTorch Adam default 0). Betas: defaults (not overridden). No scheduler,
  no warm-up, no gradient clipping, no mixed precision.
- Batch size: 256 (both families).

### 3.3 Training duration and model selection
- Epochs: MNIST 15; tabular 40 (`configs/experiment.yaml`). Fixed; no early
  stopping, no patience, no validation metric, no checkpoint selection --
  the FINAL-epoch model is saved and is the single checkpoint per
  (dataset, train_seed) (`scripts/train_backbone_v2.py`). The same
  checkpoint is reused for every policy, readiness score, cost scheme,
  resplit, and audit of that (dataset, seed).
- Actual epochs = configured epochs (no early exit path exists in code).

### 3.4 Training-time masking
- MNIST: per example per minibatch, k ~ Uniform{0, 1, ..., 49} observed
  patches (mask_min 0, mask_max 49 from config), then a uniformly random
  k-subset (`random_patch_masks`). Tabular: k ~ Uniform{0, ..., d} observed
  FEATURES, expanded to column masks so one-hot blocks flip jointly
  (`_random_feature_col_masks`).
- Masks are sampled independently per example, fresh each minibatch; the
  depth distribution is uniform over 0..T inclusive (empty and full inputs
  included). Identical scheme across datasets (up to d). Acquisition costs
  do not affect training masks.
- Mask RNG: a dedicated torch Generator seeded `train_seed + 1`; minibatch
  shuffling Generator seeded `train_seed` (`src/cafa/models.py` trainers).
- No curriculum or schedule.

### 3.5 Training seeds
- Seeds: 0 (primary), 1, 2 (robustness) -> checkpoints
  `{dsname}_ts{seed}.pt` (12 checkpoints total).
- Seeded RNGs at training: numpy global + fresh Generator via
  `config.set_seed(train_seed)`; `torch.manual_seed(train_seed)` (+ CUDA);
  shuffling generator = train_seed; mask generator = train_seed + 1. The
  train/heldout split permutation also uses `train_seed`
  (`splits.fixed_train_heldout`), so data splitting and initialization share
  the seed value but use separate generator instances.

---

## 4. Acquisition trajectories and policies

### 4.1 Greedy entropy policy
(`src/cafa/tabular.py::TabularGreedyEntropyPolicy`;
`src/cafa/acquisition.py::GreedyEntropyPolicy` for MNIST)
- Score: for each unacquired candidate a, form the hypothetical observed set
  O u {a} with a's columns/patch imputed at their TRAIN MEANS, run the
  predictor, compute Shannon entropy H = -sum_c p_c log p_c (natural log;
  probabilities clipped at 1e-12 inside the log); acquire
  argmin_a H. This is the entropy of the hypothetical mean-imputed reveal --
  NOT expected entropy reduction over an imputation distribution and NOT
  current entropy.
- Mean imputation: column means of the ENCODED fixed train split
  (`from_training_data`: `X_train.mean(axis=0)`); per-patch pixel means for
  MNIST. The candidate's true value is never consulted before acquisition
  (enforced by `tests/test_policy_honesty.py` and `scripts/verify_bugs.py`).
- Probabilities are recomputed with a full predictor forward pass for every
  candidate at every step.
- Ties: numpy argmin -> lowest feature index.
- Cost never enters the score. Deterministic given (example, model, means).
- The policy only orders acquisitions; stopping is applied post hoc by
  thresholds / forced depths on the recorded trajectory (no other stopping
  rule).

### 4.2 Random policy
- Per STEP, a uniformly random unacquired unit is chosen (fresh random keys
  each step, observed units masked out; `TabularRandomPolicy` /
  `RandomPolicy`). Realized over a full rollout this yields one random
  acquisition order per example, generated once and FROZEN; it is not
  resampled per threshold -- all thresholds and depths reuse the same cached
  trajectory.
- Seeding: tabular -- `np.random.default_rng(policy_seed)` with
  policy_seed = train_seed (`scripts/run_pool_rollout.py`). MNIST --
  `torch.rand` without a dedicated generator; determinism comes from the
  global `torch.manual_seed(policy_seed)` set at rollout start (same
  policy_seed = train_seed). Costs do not affect sampling.

### 4.3 Epsilon-greedy policy
(`src/cafa/policies_v2.py::EpsGreedyMixture`; MNIST variant inside
`scripts/run_pool_rollout.py`)
- epsilon in {0.25, 0.5}; robustness-only (Phase-2 cells; not the primary
  policy). At each instance-step, with probability epsilon a uniformly
  random unacquired unit, else the greedy-entropy pick; epsilon fixed
  across depths.
- Seed: `policy_seed = 10000 + round(1000*epsilon)` -> 10,250 (eps 0.25) and
  10,500 (eps 0.5); one `default_rng(policy_seed)` per pool rollout.
  Byte-identical reproducibility of the rollout was verified
  (re-run comparison recorded in the Phase-2 readout).
- Trajectories frozen once per rollout and reused across all thresholds;
  costs never affect the action rule.

### 4.4 Other policies
- No further policies exist in the final experiments. The margin-readiness
  cells reuse the greedy-entropy POLICY with a different STOPPING SCORE
  (Section 5.2) -- robustness only. Deprecated legacy policies/scripts
  (pre-v2 pipeline) are marked DEPRECATED in `scripts/` headers and produce
  no numbers in the canonical freeze.

### 4.5 Trajectory freezing
- Predictor frozen at the end of training; policy parameters (train means)
  frozen with it; probe commitment happens after rollouts but uses only the
  probe split.
- Trajectories are generated ONCE per (dataset, train_seed, policy[,
  readiness score]) over the ENTIRE heldout pool (probe + evaluation rows
  together) and cached as `scores/correct/order` (`src/cafa/pool.py`).
- All thresholds are evaluated on that same frozen trajectory; forced-depth
  rules use the same trajectory's `correct[:, t]` columns; trajectories are
  label-free at acquisition time and independent of calibration/test
  resplits (resplits are row-index slices of the cache).
- For the margin-score cells, `order` and `correct` are byte-identical to
  the softmax cells (verified in `results_committed/PHASE4_SCORE_ABLATION.md`);
  only `scores` differ.

---

## 5. Readiness scores and stopping rules

### 5.1 Primary readiness score
- Max-softmax probability: g = max_c p_c (`src/cafa/scores.py::softmax_score`).
- Range [1/C, 1] (1/C at uniform prediction).
- Stopping: tau_lambda(x) = min{t <= T : g_t(x) >= lambda}; equality STOPS
  (>=). Depth 0 is included (empty-input prediction from the mask-aware
  model). If the threshold is never reached, the rule stops at t = T (full
  acquisition).

### 5.2 Alternative readiness scores
- Margin: g = p_(1) - p_(2) (top-1 minus top-2 probability), clipped to
  [0, 1]; degenerate 1-class case returns the max probability
  (`src/cafa/scores.py::margin_score`). Used ONLY in the Phase-4 robustness
  cells (greedy policy, train_seed 0, datasets Adult, MiniBooNE, MNIST),
  with its own probe-committed stratum edges.
- An `entropy` score (1 - H/log C) and a `set_size` stub exist in
  `src/cafa/scores.py` but are NOT used in any canonical cell (configured
  availability only).

### 5.3 Threshold grid
- `np.linspace(0.0, 1.0, 100)`: 100 values, both endpoints included, spacing
  1/99 ~ 0.0101010101 (verified from stored `grid` in the metrics JSONs).
- Fixed-sequence testing order: DECREASING lambda (grid index 99 down to 0);
  certification proceeds while p <= delta and stops at the first failure
  (`src/cafa/risk_control.py::ltt_select`).
- The identical grid is used for every dataset, seed, policy, readiness
  score, and audit.
- Larger lambda = more required confidence = weakly later stopping = weakly
  higher cost.
- Thresholds with identical realized stopping behavior are retained as
  separate indexed hypotheses (no deduplication); e.g. the family-minimum
  plateaus (Adult: 3 tied thresholds at lambda in {0.8687, 0.8788, 0.8889};
  MNIST: 10 tied from lambda ~ 0.9091; MiniBooNE: 7 from ~ 0.9394;
  Spambase: 11 from ~ 0.8990 -- `results_committed/family_wide_summary.csv`,
  `family_wide_threshold_curves.csv`).
- lambda = 1 note: rows whose score saturates to exactly 1.0 in float32 can
  stop before T under lambda = 1; the measured agreement between the
  lambda = 1 column and the full-acquisition endpoint per dataset is in
  `results_committed/PHASE5_PROVENANCE.md`.

### 5.4 Forced-depth family
- Depths t = 0, 1, ..., T inclusive; depth 0 included; full acquisition
  t = T included. T = number of acquisition units: 49 (MNIST), 14 (Adult),
  50 (MiniBooNE), 57 (Spambase).
- Prediction at forced depth t: argmax of the predictor on the frozen
  trajectory's first t acquisitions (cached `correct[:, t]`).
- Audited jointly with the threshold family: the family-wide p-value is the
  maximum over BOTH component sets (manuscript Eq. 12). Implementation note:
  `scripts/family_wide_feasibility.py` computes the threshold-family max-p
  and the depth-family max-p SEPARATELY and stores both
  (`family_p_value`, `depth_p_value` in `family_wide_summary.csv`); the
  combined Eq.-12 value equals max(threshold-family p, depth-family p). On
  all four primary cells the combined value equals the reported
  threshold-family p (threshold p >= depth p in each case; e.g. Adult
  8.733e-93 vs 4.875e-93).
- Duplicate behaviors are retained separately (each depth is its own
  component).

---

## 6. Costs

### 6.1 Primary cost definition
- Per-unit costs c_j >= 0; trajectory cost = sum of the costs of acquired
  units up to the stop (`cum_cost[:, t+1] = cum_cost[:, t] +
  cost[order[:, t]]`, `src/cafa/pool.py::cum_cost_from_order`).
- `cost/full` = mean selected-rule cost divided by mean full-trajectory cost
  on the same rows.
- Prediction cost is not modeled. Costs NEVER affect acquisition decisions
  (policies are cost-blind); costs are applied post hoc to the cached
  `order` (trajectories are cost-scheme-invariant by construction).

### 6.2 Cost schemes
(`src/cafa/data.py::assign_feature_costs`; committed per (dataset, seed) in
`configs/committed_v2_*.json` `feature_costs_by_scheme`)
- `uniform`: c_j = 1 for every unit. Primary for MNIST; control for tabular.
- `inverse_info`: mutual information of each unit with the label computed on
  the FIXED TRAIN SPLIT via `sklearn.feature_selection.mutual_info_classif`
  (random_state 0), aggregated per unit by the max over its one-hot columns,
  min-max normalized to [0,1]; cost = 1 + 9 * (1 - MI_norm), range [1, 10].
  PRIMARY scheme for the tabular datasets.
- `random`: integer costs ~ Uniform{1, ..., 10}, `default_rng(0)`.
  Robustness only.
- Costs are fixed across resplits; they are recomputed per train_seed (the
  train split changes) and committed in that seed's config file. MNIST uses
  `uniform` only.

### 6.3 Dataset-specific costs
- MNIST: 49 unit costs, all 1.0.
- Adult / MiniBooNE / Spambase: per-unit vectors for all three schemes
  stored in `configs/committed_v2_{ds}_ts{seed}.json`; no excluded or
  zero-cost units (inverse_info minimum is 1 by construction).

---

## 7. Probe commitment and precommitment parameters

### 7.1 Probe construction
- Fraction 0.10 of the heldout pool; seed 777
  (`configs/experiment.yaml` protocol_v2; `src/cafa/splits.py::probe_eval_split`).
- Procedure: a seeded permutation of heldout POSITIONS; the first
  round(0.10 * n_heldout) positions are the probe. NOT stratified.
- Disjointness: probe and evaluation positions partition the heldout arrays;
  every calibration/test resplit is drawn from the evaluation positions
  only, so the probe is disjoint from all resplits (asserted at load;
  `tests/test_splits_v2.py`).
- Fixed across model seeds: the position permutation depends only on
  seed 777 and the heldout size, so probe POSITIONS are identical across
  train seeds; the underlying global rows differ with the train split.
- Probe labels are used only for the target commitment (full-acquisition
  floor) and probe SCORES for stratum edges; probe rows never enter
  selection or evaluation.

### 7.2 Target commitment
- Implemented formula (`src/cafa/data.py::feasible_alpha_from_floor`,
  called by `scripts/probe_commit.py` with defaults headroom = 0.05,
  step = 0.05):
  `alpha = min(1.0, max(0.05, ceil(round((floor + 0.05)/0.05, 9)) * 0.05))`,
  rounded to 4 decimals.
- This is OPTION 1: add the 0.05 margin FIRST, then round UP to the next
  multiple of 0.05.
- Behavior at exact multiples: the inner `round(., 9)` removes float dust,
  so an exact multiple stays (e.g. floor 0.10 -> target 0.15 -> alpha 0.15;
  no extra increment).
- Clipping: alpha in [0.05, 1.0].
- Committed values (from `configs/committed_v2_*_ts*.json`; floor = probe
  full-acquisition error, 6 dp):

| dataset | seed 0 floor -> alpha | seed 1 | seed 2 |
|---|---|---|---|
| MNIST | 0.077857 -> 0.15 | 0.101071 -> 0.20 | 0.094286 -> 0.15 |
| Adult | 0.146490 -> 0.20 | 0.161415 -> 0.25 | 0.145384 -> 0.20 |
| MiniBooNE | 0.084374 -> 0.15 | 0.088603 -> 0.15 | 0.093792 -> 0.15 |
| Spambase | 0.054348 -> 0.15 | 0.070652 -> 0.15 | 0.065217 -> 0.15 |

- Discrepancies: none between code, committed configs, canonical result
  files, and manuscript for these values.

### 7.3 Reference threshold and strata
- lambda_ref in {0.5, 0.7, 0.9}; primary 0.9; 0.5 and 0.7 published as
  sensitivity (all 105 IUT configurations); committed in
  `configs/experiment.yaml` (mondrian_v2.lambda_refs) before results
  (git-history evidence recorded in
  `results_committed/phase5_provenance.json`).
- Reference depth: D_ref(x) = first t with score >= lambda_ref (else T)
  (`src/cafa/metrics.py::reference_depth`).
- G = 5 strata primary; primary binning = QUANTILE edges of the PROBE
  reference-depth distribution (`quantile_bucket_edges`: interior quantiles
  at 1/5, ..., 4/5 via `np.quantile`, duplicates collapsed with
  `np.unique`).
- Alternatives (committed, robustness-only): quantile with G in {3, 8};
  equal-width G = 5 with min_per_bucket in {25, 50, 100} merging
  (`reference_buckets` merge rule). All edge sets are committed per
  (dataset, seed, policy[, score], lambda_ref) in the config JSONs.
- Repeated quantiles: collapsed, so fewer than G populated bins can result.
- Empty bins: membership is `np.digitize` against committed edges; a label
  with zero members is simply unpopulated. In CAFA-IUT an INTERIOR
  zero-count stratum contributes p = 1 at every threshold (blocks
  certification; `src/cafa/risk_control_ext.py`). In the family audit the
  confirmatory stratum is by definition nonempty.
- Bin membership uses only trajectory scores -- never labels.

### 7.4 Confirmatory stratum
- Rule: the DEEPEST (largest-label) precommitted nonempty bucket on the
  post-probe evaluation pool (`scripts/phase53_lib.py::deepest_nonempty`;
  decision recorded in `results_committed/PHASE5_PROVENANCE.md`).
- Nonemptiness: covariate counts (reference depths) on the evaluation pool;
  labels are never used.
- If the deepest nominal bin is empty, the next-deepest populated label is
  the deepest nonempty bucket by construction of the max over populated
  labels.
- The stratum is fixed before any audit labels are examined. On all four
  primary cells the deepest nonempty bucket COINCIDES with the
  maximum-observed-risk stratum (canonical coincidence recorded in the
  provenance file; the argmax rule alone would be post-selection and is
  treated as exploratory).
- Zero-count strata: excluded from "nonempty"; see 7.3 for IUT handling.

---

## 8. Calibration, testing, and audit protocol

### 8.1 Repeated resplits
- 100 resplits; calibration fraction 0.5 of the evaluation pool; test = the
  complement (`configs/experiment.yaml` protocol_v2).
- Seeds: `np.random.default_rng(1_000_000 + j)` for j = 0..99, permuting
  evaluation POSITIONS; the offset prevents collision with train/probe
  streams (`src/cafa/splits.py::resplit_cal_test`).
- NOT stratified by class or by readiness stratum.
- Identical resplit index sequences are used by every configuration of a
  given (dataset, train_seed) (same generator rule, same n_eval); across
  train seeds the rule is identical but the underlying rows differ.

### 8.2 Marginal calibration
- Null per threshold: H_lambda : R(lambda) > alpha.
- p-value: Hoeffding-Bentkus, p = min(exp(-n * KL(r_hat || alpha)),
  e * BinomCDF(ceil(n * r_hat); n, alpha)), clipped to (0, 1]; p = 1 when
  r_hat >= alpha (`src/cafa/risk_control.py::hoeffding_bentkus_pvalue`).
  No additional finite-sample correction.
- Fixed-sequence order: decreasing lambda; certify while p <= delta; stop at
  the first p > delta (contiguous certified block from the top).
- Selection: cheapest certified rule = argmin of mean calibration cost over
  the certified set; because cost is nondecreasing in lambda this is the
  smallest certified index.
- No certificate (empty set): no threshold deployed; the experiment falls
  back to full acquisition and records the outcome explicitly (never a
  violation by convention). All-certified: cheapest still selected.
- alpha: the committed per-(dataset, seed) value (7.2); delta = 0.10
  (`configs/experiment.yaml` method.delta).

### 8.3 CAFA-IUT calibration
- Per (threshold, stratum) null H_{lambda,k}: R_k(lambda) > alpha with the
  same HB p-value computed within the stratum's calibration rows.
- Combination: p_IUT(lambda) = max over the contiguous integer label span of
  the calibration bucket labels; an INTERIOR label with zero calibration
  rows contributes p = 1 (conservative; blocks certification). Strata are
  never silently dropped (`src/cafa/risk_control_ext.py::iut_select`;
  populated strata below 30 calibration rows emit a warning).
- Same fixed-sequence order over thresholds at level delta = 0.10; selection
  = cheapest simultaneously certified threshold.
- Refusal: empty certified set -> certification refusal with
  FULL-ACQUISITION FALLBACK (a prediction is still produced); recorded per
  resplit.
- The guarantee covers the strata of the populated label span; empty
  interior strata prevent certification rather than being excluded.

### 8.4 Family-wide audit
- Family: all 100 grid thresholds PLUS all forced depths t = 0..T
  (per-dataset family sizes M = 150 / 115 / 151 / 158 for
  MNIST/Adult/MiniBooNE/Spambase).
- Component nulls (for failure evidence): H_safe: R_k(component) <= alpha;
  exact one-sided binomial upper-tail p = P(Bin(n_k, alpha) >= S)
  (`scripts/phase53_lib.py::binom_upper_p`, `scipy.stats.binom.sf`).
- Threshold-family max-p and depth-family max-p computed separately and
  stored; the combined family-wide p is their maximum (see 5.4 note).
- Audit level gamma = 0.05 (one-sided).
- Three-way verdict: empirical minimum family risk <= alpha -> "feasible"
  (empirical feasibility; no simultaneous confidence claim); else combined
  p <= gamma -> "family-wide failure certified"; else "unresolved"
  (`scripts/family_wide_feasibility.py::audit_family`).
- n_k = 0 cannot occur for the confirmatory stratum (deepest NONEMPTY).
- The audit uses the FULL post-probe evaluation pool, computed ONCE per
  frozen configuration (no resplits).

### 8.5 Full-pool evaluation
- Calibration-half risk: mean 0/1 loss of a threshold on the calibration
  positions; test-half: same on the complement; full-pool: same on ALL
  post-probe evaluation rows (exact; the probe is EXCLUDED).
- Recorded: test-half realized risk per resplit in the metrics JSONs;
  full-pool risk per resplit in `results_committed/pool_risk_gate.csv`,
  `pool_stratum_resplits.csv`, `pool_plugin_resplits.csv`; the
  calibration-half value is recoverable exactly via the identity
  n_cal*R_cal + n_test*R_test = n_pool*R_pool (asserted numerically per
  resplit in `scripts/pool_stratum_eval.py`).
- Costs: test-half costs per scheme in the metrics JSONs; full-pool costs in
  the pool CSVs. The selected threshold is always evaluated on the same
  fixed post-probe pool.

---

## 9. Experimental configuration counts

### 9.1 Marginal study -- 35 cells (confirmed)
One cell = (dataset, acquisition policy, training seed, readiness score).
Composition (verified: 35 JSON files in `results_committed/metrics/`):
- 4 datasets x {greedy_entropy, random} x seed 0 x softmax = 8
- 4 datasets x {eps 0.25, eps 0.5} x seed 0 x softmax = 8
- 4 datasets x {greedy_entropy, random} x seeds {1, 2} x softmax = 16
- 3 datasets (MNIST, Adult, MiniBooNE) x greedy_entropy x seed 0 x margin = 3
Total 8 + 8 + 16 + 3 = 35. (A configured 36th margin cell for Spambase
exists in the runner's cell list but was NOT run -- configured, not used.)

### 9.2 CAFA-IUT study -- 105 configurations (confirmed)
One configuration = (marginal cell, lambda_ref); 35 x 3 = 105
(`results_committed/iut_by_lambda_ref.csv`, one row each; asserted in
`scripts/iut_by_lambda_ref.py`). The robustness cells (eps, seeds 1-2,
margin) are INCLUDED in the 105; binning is the primary quantile-5 rule and
the primary cost scheme per dataset within these configurations. Alternative
binning rules are a separate ablation, not part of the 105.

### 9.3 Family-wide primary audit -- 4 cells
One primary audit cell = (dataset, greedy_entropy, seed 0, softmax,
lambda_ref 0.9, deepest nonempty stratum): 4 datasets = 4 cells
(`family_wide_summary.csv` rows with is_primary = True). The same audit is
computed for all 105 (cell, lambda_ref) combinations as sensitivity
(same CSV; 105 rows). Primary audit uses one policy and one seed.

---

## 10. Baselines and oracles

### 10.1 Plug-in selector
- Cheapest grid threshold whose EMPIRICAL CALIBRATION risk is <= alpha; no
  multiple-testing correction; ties by argmin of mean calibration cost
  (lowest index on ties) (`src/cafa/baselines.py::plugin_threshold_select`).
- Selection data: the calibration half of each resplit; grid: the same 100
  thresholds; fallback: None -> full acquisition (recorded separately).

### 10.2 Fixed-confidence baselines
- Thresholds {0.90, 0.95, 0.99}; rule: stop at the grid index closest to the
  requested confidence (argmin |grid - t|; ties -> lowest index); ignores
  calibration data entirely; same frozen trajectory and model; no fallback
  needed (`fixed_confidence_select`).

### 10.3 Fixed-budget baselines
- Budgets {5, 10, 20} acquisition-UNIT COUNTS (not normalized costs),
  clamped to [0, T] (relevant on Adult where T = 14 clamps budget 20)
  (`budget_select`); identical budgets across datasets; realized risk/cost
  read directly at that trajectory depth.

### 10.4 Cheapest-valid oracle
- Cheapest grid threshold whose TEST-half realized risk is <= alpha,
  selected using test labels (finite-pool oracle on the test half of each
  resplit; NOT a population oracle); ties by argmin test cost; searches
  THRESHOLD rules only (not forced depths); None -> reported as absent
  (`oracle_cheapest_valid_select`).

### 10.5 Full-feature oracle
- Deterministic full acquisition: risk = mean(1 - correct[:, T]) and
  cost = mean full-trajectory cost on the relevant rows; always predicts
  after acquiring everything (`oracle_full_feature_risk`).

### 10.6 Other baselines
- None in the canonical result files. (Legacy Mondrian per-stratum threshold
  selection appears in v2 outputs strictly as an AUDIT diagnostic without a
  cost operating point -- not a baseline row.)

---

## 11. Primary versus robustness settings

| component | primary | robustness alternatives | datasets | policies | seeds | resplits | output artifact | status |
|---|---|---|---|---|---|---|---|---|
| readiness score | max-softmax | margin (Phase 4) | 4 (margin: MNIST/Adult/MiniBooNE) | greedy (margin cells) | 0 | 100 | metrics JSONs; PHASE4_SCORE_ABLATION.md | final |
| acquisition policy | greedy entropy (honest, mean-imputed) | random; eps-greedy | 4 | -- | 0 (eps); 0-2 (greedy/random) | 100 | metrics JSONs | final |
| epsilon | n/a (0) | 0.25, 0.5 | 4 | eps-greedy | 0 | 100 | metrics JSONs; PHASE2_READOUT.md | final (robustness) |
| reference threshold lambda_ref | 0.9 | 0.5, 0.7 | 4 | all | all | 100 | iut_by_lambda_ref.csv (105 rows) | final |
| number of strata G | 5 | 3, 8 (quantile) | 4 | greedy/random | 0 | 25-seed subset | RESULTS.md ablation section | final (ablation) |
| binning method | probe quantile | equal-width G=5, min-per-bucket {25,50,100} | 4 | greedy/random | 0 | 25-seed subset | RESULTS.md ablation | final (ablation) |
| cost scheme | inverse_info (tabular); uniform (MNIST) | uniform, random (tabular) | 4 | all | all | 100 | metrics JSONs, h2_table.csv | final |
| model seed | 0 | 1, 2 | 4 | greedy/random | -- | 100 | PHASE3_REPORT.md | final |
| threshold grid | linspace(0,1,100) | none | 4 | all | all | -- | configs/experiment.yaml | final |
| calibration level delta | 0.10 | none | 4 | all | all | -- | configs/experiment.yaml | final |
| audit level gamma | 0.05 | none | 4 | all | all | -- | family_wide_summary.json | final |
| entropy readiness / set_size score | -- | configured but NOT USED | -- | -- | -- | -- | src/cafa/scores.py | not used |
| Spambase margin cell (cell 16) | -- | configured but NOT RUN | -- | -- | -- | -- | runner cell list | not used |
| legacy (pre-v2) pipeline | -- | -- | -- | -- | -- | -- | scripts with DEPRECATED headers | deprecated |

---

## 12. Exact values for the three planned S5 tables

### Table A: Datasets and splits
(sizes identical across seeds; floor/alpha per seed from
`configs/committed_v2_*_ts*.json`)

| dataset | seed | post-filter total | train | heldout | probe | post-probe pool | classes | raw dim | encoded dim | units | probe full-acq error | committed alpha |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MNIST | 0 | 70000 | 42000 | 28000 | 2800 | 25200 | 10 | 784 | 49x16 patches (2ch 28x28 input) | 49 | 0.077857 | 0.15 |
| MNIST | 1 | 70000 | 42000 | 28000 | 2800 | 25200 | 10 | 784 | -- | 49 | 0.101071 | 0.20 |
| MNIST | 2 | 70000 | 42000 | 28000 | 2800 | 25200 | 10 | 784 | -- | 49 | 0.094286 | 0.15 |
| Adult | 0 | 45222 | 27133 | 18089 | 1809 | 16280 | 2 | 14 | 104 | 14 | 0.146490 | 0.20 |
| Adult | 1 | 45222 | 27133 | 18089 | 1809 | 16280 | 2 | 14 | 104 | 14 | 0.161415 | 0.25 |
| Adult | 2 | 45222 | 27133 | 18089 | 1809 | 16280 | 2 | 14 | 104 | 14 | 0.145384 | 0.20 |
| MiniBooNE | 0 | 130064 | 78038 | 52026 | 5203 | 46823 | 2 | 50 | 50 | 50 | 0.084374 | 0.15 |
| MiniBooNE | 1 | 130064 | 78038 | 52026 | 5203 | 46823 | 2 | 50 | 50 | 50 | 0.088603 | 0.15 |
| MiniBooNE | 2 | 130064 | 78038 | 52026 | 5203 | 46823 | 2 | 50 | 50 | 50 | 0.093792 | 0.15 |
| Spambase | 0 | 4601 | 2761 | 1840 | 184 | 1656 | 2 | 57 | 57 | 57 | 0.054348 | 0.15 |
| Spambase | 1 | 4601 | 2761 | 1840 | 184 | 1656 | 2 | 57 | 57 | 57 | 0.070652 | 0.15 |
| Spambase | 2 | 4601 | 2761 | 1840 | 184 | 1656 | 2 | 57 | 57 | 57 | 0.065217 | 0.15 |

(Original pre-filter row counts for the tabular datasets: NOT FOUND in repo
artifacts -- see 13.2. "Encoded dim --" for MNIST seeds 1-2 = same as seed 0.)

### Table B: Architecture and training

| dataset/model | architecture | mask representation | optimizer | lr | weight decay | batch | epochs | early stopping | loss | training-mask distribution | model seeds |
|---|---|---|---|---:|---|---:|---:|---|---|---|---|
| MNIST / MaskedPredictor CNN | Conv(2->32,3x3)-ReLU-Conv(32->32,3x3)-ReLU-MaxPool2-Conv(32->64,3x3)-ReLU-MaxPool2-GAP-FC(64->128)-ReLU-Drop0.2-FC(128->10) | 2 channels: zeroed masked image + pixel-broadcast 0/1 mask | Adam | 0.001 | not set (default 0) | 256 | 15 | none | CrossEntropy | k ~ U{0..49} patches, uniform random subset, per example | 0, 1, 2 |
| Adult/MiniBooNE/Spambase / TabularMaskedPredictor MLP | FC(2*n_cols->128)-ReLU-FC(128->128)-ReLU-Drop0.1-FC(128->2); n_cols 104/50/57 | concat(X * mask, mask); unobserved cols zeroed | Adam | 0.001 | not set (default 0) | 256 | 40 | none | CrossEntropy | k ~ U{0..d} features, blocks flip jointly | 0, 1, 2 |

### Table C: Policies, readiness, and calibration

| component | exact definition | parameters | primary | robustness alternatives | grid | delta | gamma | lambda_ref | G | binning | resplits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| greedy entropy policy | argmin over candidates of Shannon entropy after hypothetical TRAIN-MEAN-imputed reveal; recomputed per candidate; ties -> lowest index; cost-blind; deterministic | train-mean imputation vectors | yes | -- | linspace(0,1,100) | 0.10 | 0.05 | 0.9 (primary) | 5 | probe quantile | 100 |
| random policy | uniformly random unacquired unit per step; trajectory frozen once per rollout | seed = train_seed (tabular rng; MNIST via global torch seed) | no (comparison) | -- | same | same | same | all three | 5 | same | 100 |
| eps-greedy | Bernoulli(eps) random unit else greedy pick, per instance-step | eps {0.25, 0.5}; seed 10000+1000*eps (10250/10500) | no | eps values | same | same | same | all three | 5 | same | 100 |
| readiness: max-softmax | g = max_c p_c; stop at first g >= lambda; never -> t=T; depth 0 included | -- | yes | margin = p(1)-p(2) clipped [0,1] (3 datasets, ts0, greedy) | same | same | same | all three | 5 | own committed edges per score | 100 |
| marginal calibration | HB p per threshold vs H: R > alpha; fixed-sequence decreasing lambda; cheapest certified; none -> full-acq fallback | alpha per (dataset, seed); delta 0.10 | yes | -- | same | 0.10 | -- | -- | -- | -- | 100 |
| CAFA-IUT | p_IUT = max over stratum HB p (interior empty -> p=1); same fixed sequence; cheapest certified; refusal -> full-acq fallback | delta 0.10 | yes | lambda_ref 0.5/0.7 | same | 0.10 | -- | 0.9 primary | 5 | probe quantile | 100 |
| family-wide audit | exact binomial upper-tail p per member; max-p over 100 thresholds and T+1 depths; three-way verdict | gamma 0.05; deepest nonempty stratum | yes | all 105 configs as sensitivity | same | -- | 0.05 | 0.9 primary | 5 | probe quantile | none (full pool, once) |

---

## 13. Conflicts and unresolved items

### 13.1 Confirmed conflicts
1. Manuscript abstract/bullet/results claim "0/100 full-pool violations in
   each of 35 cells" vs `results_committed/pool_risk_gate.csv`: 34/35 cells
   at 0/100; MNIST/greedy/seed-1 at 1/100 (Wilson UB 0.0545); all 35 pass
   the gate. CONFLICT -- resolution and replacement wording documented in
   `reviewphase_0_1_reply.md` (manuscript must change).
2. Manuscript "minimum family risk occurs at lambda = 0.899" (Adult) vs
   `family_wide_threshold_curves.csv`: argmin plateau at lambda in
   {0.8687, 0.8788, 0.8889} (R = 0.309030); R(0.899) = 0.309190. CONFLICT --
   the manuscript value is a superseded local-run number; documented in
   `reviewphase_0_1_reply.md`.
3. No other conflicts among code, configs, canonical CSV/JSON artifacts, and
   result markdowns were found.

### 13.2 Missing information (NOT FOUND)
- Pre-filter original row counts for Adult/MiniBooNE/Spambase (searched:
  loaders, configs, cache metas, committed JSONs -- only post-filter counts
  are persisted).
- Exact original class-label strings for the tabular targets (only the
  categorical-codes rule is in code).
- Explicit Adult per-column feature lists / categorical-numeric split
  (only group widths are persisted in checkpoint meta).
- Model parameter counts (never computed or stored).
- OpenML numeric data_ids (fetch is by name+version; data_id null in
  config).

### 13.3 Author decisions required
- Whether S5 should state the tabular datasets' pre-filter sizes from
  external documentation (not derivable from repo artifacts) or report only
  the verified post-filter sizes.
- Whether to name the Adult label strings (requires re-inspecting the raw
  OpenML frame; the repo only guarantees lexicographic category coding).
- Whether the configured-but-unused items (entropy/set_size scores,
  Spambase margin cell) should be mentioned in S5 or omitted.

### 13.4 Safe claims for the supplement
- All split sizes, seeds, and fractions in Table A; identical grids,
  delta = 0.10, gamma = 0.05 everywhere.
- The alpha rule is margin-then-round-up (Option 1) with the exact code
  operation in 7.2 and the 12 committed (floor, alpha) pairs.
- Trajectories are computed once per (dataset, seed, policy[, score]),
  label-free, cost-blind, and reused for every threshold, forced depth, and
  resplit; margin-score rollouts share byte-identical order/correct with
  softmax.
- The confirmatory stratum is the deepest nonempty probe-committed bucket,
  label-free, and coincides with the max-risk stratum on all four primary
  cells.
- The family = 100 thresholds + (T+1) forced depths (M = 150/115/151/158);
  exact binomial IU test at gamma = 0.05; verdicts as in 8.4; audits run
  once on the full post-probe pool.
- Counting: 35 = 8 + 8 + 16 + 3; 105 = 35 x 3 lambda_refs; 4 primary audit
  cells.
- Resplits: 100 unique 50/50 permutations, seeds 1,000,000 + j, unstratified;
  MiniBooNE cal/test = 23,412/23,411.
- Marginal statistics use the 100 unique resplits (never pooled across
  lambda_refs).

### 13.5 Unsafe claims to avoid
- Any statement of pre-filter dataset sizes, original label strings, or
  Adult's per-column type split (not in artifacts).
- "0/100 pool violations in every cell" (false; see 13.1.1).
- Any adult argmin at lambda = 0.899 (superseded local value).
- Calling the empirically-feasible branch "certified" (it is observed-risk
  only; no simultaneous confidence procedure exists for feasibility).
- Describing the greedy score as "expected information gain" or "expected
  entropy reduction" (it is the entropy of a single mean-imputed
  hypothetical reveal).
- Claiming the random policy pre-samples one permutation per example (it
  draws per step; the REALIZED frozen trajectory is equivalent, but the
  implementation is per-step sampling).
- Claiming validation-based model selection or early stopping (none exists).
- Claiming stratified resplits or stratified probe sampling (both are plain
  permutations).
