# CAFA v3 — file manifest and drop-in instructions

All files are ADDITIVE: nothing existing is modified, `src/cafa/risk_control.py` stays byte-frozen, and every v3
module composes the frozen primitives (`hoeffding_bentkus_pvalue`, `ltt_select`, `iut_select`, `stops_from_grid_np`,
`reference_buckets`, `probe_eval_split`). Everything downstream of the pool caches is torch-free.

Prompt for Claude Code (paste as-is):

```
Unzip CAFA_v3_code.zip into the repo root (F:\FAU\PhD\Side Quest\CAFA_exp), preserving paths
(src/cafa/, scripts/, tests/, configs/, plus PHASES_V3.md and V3_FILE_MANIFEST.md at the root).
Do not modify any pre-existing file. Then run, from the repo root:
  python -m pytest -q tests/test_cascade.py tests/test_localization.py tests/test_commit_rules.py tests/test_splits_v3.py tests/test_planted.py tests/test_hidden_risk.py tests/test_data_v3.py tests/test_external_orders.py tests/test_models_v3.py
and report the result. Then execute PHASES_V3.md Phase 0 step 3 (synthetic end-to-end) and report the
console lines starting with "[cascade]". Stop there; Phases 1-3 are run by me (GPU / cluster).
```

## src/cafa/ (9 new modules)

| file | what it is | tests |
|---|---|---|
| `cascade.py` | Certify-or-route cascade: tier 1 (CAFA-IUT), tier 2 (certified budget over forced depths T..0), tier 3 (certified escalation over precommitted levels, precommitted order); `certify_or_route`, `apply_rule` (test-split evaluation), Theorem 4 in the docstring | `test_cascade.py` (Theorem-4 Monte Carlo, Prop-2 certification, routing, probe-ordered escalation) |
| `localization.py` | Family-wide audit with fault localization: exact binomial IUT p-values `p_thr`, `p_depth`, ordered verdict rule (`type_II`, `type_I`, `feasible`, `thr_failure_depth_unresolved`, `unresolved`) | `test_localization.py` (γ control, Type I/II detection) |
| `commit_rules.py` | Probe-committed design: deployment-aligned λ_ref (plug-in point on the probe), `n_min_required` (180/275/358/428 at α = .10/.15/.20/.25, level .05), G-rule `detectability_limited_edges`, stratum-aware `escalation_levels`, `escalation_order_from_probe` | `test_commit_rules.py` |
| `splits_v3.py` | Probe (v2-identical, seed 777) / calibration pool / independent test (seed 778); seeded calibration draws (`2_000_000 + draw`) | `test_splits_v3.py` |
| `synthetic_planted.py` | Planted-strata trajectories with known true accuracy (Type-II hard cores, Type-I overconfidence, feasible strata) for E5 and the unit tests | `test_planted.py` |
| `hidden_risk.py` | Lemma 1 (`R_k ≤ R/q_k`), Proposition 2 design condition, n_min table | `test_hidden_risk.py` |
| `data_v3.py` | Loaders: AFABench CSVs (PhysioNet, Diabetes; train-only NaN fill + standardisation), CUBE (numpy port of AFABench's generator), FashionMNIST, Imagenette (uint8 224, 7x7 patches), dispatcher `load_pool_v3` | `test_data_v3.py` |
| `models_v3.py` | `MaskedPredictorV2` (BN-CNN, same interface as v2), `train_masked_predictor_v2` (p_full share of full-observation masks), `ResNetPatchPredictor` (4-channel ResNet-18), `GreedyEntropyImagePolicy`, `RandomImagePolicy`, `train_resnet_patch_predictor` | `test_models_v3.py` (torch; skipped without it) |
| `external_orders.py` | Frozen order-matrix I/O for external (AFABench) policies | `test_external_orders.py` |

## scripts/ (13 new scripts)

| file | phase | torch? | purpose |
|---|---|---|---|
| `download_data_v3.py` | 1a | yes | one-time fetch (MNIST, FashionMNIST, Imagenette, OpenML, AFABench CSVs) |
| `train_backbone_v3.py` | 1b | yes | one checkpoint per (dataset, seed) → `checkpoints_v3/` |
| `run_pool_rollout_v3.py` | 1c | yes | rollouts for every dataset kind (+ `--orders-file` replay) → `pool_v3/` |
| `export_heldout_v3.py` | 1d | no | export heldout features for an external policy environment |
| `afabench_export_orders.py` | 1d | AFABench env | replay a trained AFABench method on our heldout rows → order matrix (validate in that env) |
| `planted_validation.py` | 2 | no | E5: level / power / routing on planted populations → `results_v3/planted/` |
| `commit_v3.py` | 3a | no | probe commit: α, λ_ref keys, G-rule edges, escalation grid + order, split digests → `configs/committed_v3_*.json` |
| `run_cascade_sweep.py` | 3b | no | 100 calibration draws per cell: marginal, cascade, baselines, localized audit → `metrics_v3/` |
| `make_tables_v3.py` | 3c | no | TABLE_E2/E3/E4/E6 (md + csv) |
| `make_figures_v3.py` | 3c | no | F2 blindness, F3 cascade, F4 repair, F5 planted (pdf) |
| `repair_experiment.py` | 3d | no | E7: re-audit an AFTER system on the BEFORE system's committed strata |
| `make_synthetic_pool_cache.py` | 0 | no | synthetic pool caches for the end-to-end smoke test |

## configs/ and docs

- `configs/experiment_v3.yaml` — v3 protocol (probe/calpool/test, 100 draws, 3 seeds), G-rule, δ split (½, ¼, ¼), escalation grid, audit γ, budgets as T-fractions, dataset list, training hyper-parameters, E5 grid.
- `PHASES_V3.md` — the execution plan with commands, acceptance checks, time estimates (local vs. TinyGPU).
- `V3_FILE_MANIFEST.md` — this file.

## Verified in the sandbox (CPU, no torch)

- 29 torch-free tests pass (`test_models_v3.py` skipped without torch); the pre-existing torch-free suite still passes (40 passed, 1 skipped).
- End-to-end on synthetic caches: feasible → tier 1 in 100 % of draws, 0 violations, deployed cost 1.23x marginal, Mondrian oracle 0.95x; planted Type II → audit `type_II`, tier 3 in 80–100 % of draws, 0 test violations; repair (Type II before → feasible after) → tier-1 share 0 → 1.
- E5 small run: false-failure 0.000, power 0.90 at n_kΔ² = 2.5 and 1.00 at 10, escalation safe.

## Not executed here (needs torch / data / the AFABench environment)

`models_v3.py`, `train_backbone_v3.py`, `run_pool_rollout_v3.py`, `download_data_v3.py`, the torchvision loaders in
`data_v3.py`, and `afabench_export_orders.py` are syntax-checked and written against the exact v2 interfaces, but
their first real run is Phase 0/1 on your GPU. Run the smoke commands (`--epochs 1 --max-train 2000`, `--max-rows 256`)
before the full grid.

## Anonymity reminder

Before any code appendix is zipped: `grep -rn "AAAI\|26549\|FAU\|Erlangen" --include=*.md --include=*.py --include=*.yaml .`
and scrub `README.md`, `RESULTS_FOR_PAPER.md`, `CANONICAL_RESULTS.md`, `reviewphase_0_1_reply.md`, `S*_answer.md`,
`CLAUDE_CODE_WORKORDER.md` (or exclude them from the appendix).
