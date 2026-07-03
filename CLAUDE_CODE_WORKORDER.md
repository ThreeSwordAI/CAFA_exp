# CAFA v2 — Work Order for Claude Code (Repair + Rigor Release)

*Authoritative instruction set. Prepared by the external reviewer after the full dossier + codebase audit and the authors' response. Every open question has been decided; Claude Code should implement, not re-litigate. If an instruction here conflicts with anything else (dossier, old README, code comments), **this document wins**.*

---

## A. FOR THE HUMAN OPERATOR (read first, 2 minutes)

### A.1 What this is
A single self-contained spec for Claude Code to repair and upgrade the repo at `F:\FAU\PhD\Side Quest\CAFA_exp`. Claude Code will **edit and create files only — it must not run anything**. You push, pull on the FAU NHR cluster (TinyGPU), and run the printed commands manually. All numbers are produced on the cluster; nothing in the repo may contain invented results.

### A.2 The prompt to paste into Claude Code

```
You are working in the repo CAFA_exp (already open in this workspace).

Read the file CLAUDE_CODE_WORKORDER.md at the repo root in full before touching
anything. It is the authoritative spec: implement exactly what it says, in the
order of its work orders (WO-0 through WO-18). Where it gives signatures,
formulas, filenames, or JSON schemas, follow them verbatim.

Hard rules (also in the spec, §C):
- Do NOT run any code, tests, or commands. Edit/create files only.
- Do NOT modify src/cafa/risk_control.py or tests/test_risk_control.py
  (byte-frozen). Do not delete or rewrite any legacy script; only add the
  deprecation headers the spec asks for.
- Do NOT invent, estimate, or placeholder any experimental number anywhere
  (README, RESULTS templates, docstrings). Use the literal placeholder token
  TBD-RUN where a number will come from the cluster.
- All new/edited files: LF line endings, no Windows paths, ASCII-safe.
- Anything the spec marks OUT OF SCOPE stays out, even if it seems useful.

When finished: (1) run through the acceptance checklist in §G of the spec and
fix anything that fails; (2) print the checklist with pass marks; (3) print the
exact cluster command sequence from §F verbatim; (4) list every file you
created or modified with one-line descriptions.
```

### A.3 Files to attach / place
1. **This file** — save it as `CLAUDE_CODE_WORKORDER.md` in the repo root before starting Claude Code (that is the only required "attachment"; the prompt references it by path).
2. Optional background (read-only, subordinate to this spec): `CAFA_AAAI_review.md`, `CAFA_review_response.md`. If attached, tell Claude Code: *"background only; the work order overrides them."* Not required — everything needed is in this file.

### A.4 What you will do after Claude Code finishes
1. Review the diff (especially `tabular.py`, `splits.py`, `risk_control_ext.py`).
2. Commit + push; pull on the cluster.
3. Run **Phase 0** locally or on a login node (tests + bug-verification script). Do not proceed if anything fails.
4. Run Phases 1–4 on the cluster (§F). Phase 4 ends with `analysis_v2/RESULTS.md`.
5. Send RESULTS.md (plus the `metrics_v2/` JSONs if small enough) back to the reviewer for the **fork review** (§H). Phase 5 is pre-approved to queue but its *interpretation* waits for the fork.

---

## B. FOR CLAUDE CODE — mission and context (5-minute orientation)

**Project:** CAFA — distribution-free risk-controlled stopping for Active Feature Acquisition. A frozen masked predictor + frozen acquisition policy generate per-instance trajectories; Learn-then-Test (Hoeffding–Bentkus p-values + fixed-sequence FWER) certifies stopping thresholds λ with risk ≤ α at confidence 1−δ; the cheapest certified λ is deployed. A per-stratum (Mondrian) layer certifies/abstains per reference-depth stratum.

**Why this work order exists:** an external audit confirmed five evidence-invalidating issues (accepted in full by the authors):
- **C1** — the tabular greedy policy scored each candidate feature using its **true value** (clairvoyant); the image version correctly mean-imputes.
- **C2** — MNIST backbone trained once on seed 0's train split, but every seed re-permuted the **entire** 70k pool for cal/test → ~60% of cal/test images were training images.
- **C3** — Mondrian stratum edges were fit on the **same calibration set** used for selection (Theorem 3 requires a pre-committed partition).
- **C4** — per-stratum threshold routing is circular (stratum unknown before the λ_ref crossing); reported Mondrian costs were not deployable.
- **C5** — MNIST's α=0.10 violates the project's own fixed-α rule (floor 0.091 → rule gives 0.15).
Plus: 20 resplits with no CIs cannot support the claims; "infeasibility" margins of +0.009/+0.018 carry no confidence statement; the marginal method's cost-minimizing selection is provably cost-blind in the scalar family (state it, don't hide it).

**Your job:** implement the v2 pipeline that fixes all of the above with an architecture that makes the fixes *structural* (asserted, pre-committed, cached, reproducible), not patched. You write code and docs; the human runs everything on a Slurm cluster.

---

## C. HARD GUARDRAILS (non-negotiable)

1. **Frozen bytes:** `src/cafa/risk_control.py` and `tests/test_risk_control.py` must be byte-identical to their current state. Never edit, reformat, or "improve" them. Also do not edit `tests/test_mondrian.py`, `tests/test_baselines.py`, `tests/test_pipeline.py` except where a work order explicitly says so.
2. **No execution.** Do not run python, pytest, pip, git, or shell commands. If you are unsure whether code works, re-read it; add a test for the human to run.
3. **No invented numbers.** Every empirical value in docs/templates is the literal token `TBD-RUN`. The α values currently in `configs/experiment.yaml` remain as *legacy* values; v2 α comes only from the probe (WO-9) at run time.
4. **Additive architecture.** Legacy scripts (`run_experiment.py`, `run_mondrian.py`, `run_mondrian_mnist.py`, `aggregate_results.py`, `make_figures.py`, `alpha_probe.py`, `step5_*`) are kept, untouched except for a deprecation header (WO-18). All v2 code lives in new files/dirs.
5. **Torch-free analysis path.** Everything downstream of the pool-rollout caches (splits, probe, eval sweep, analysis, figures, all new tests except the two policy-honesty probes) must import cleanly without torch. Follow the existing lazy-import pattern.
6. **Determinism.** Every random draw is seeded from named config values; identical inputs ⇒ identical outputs, bit-for-bit where numpy allows.
7. **Line endings LF; no absolute or Windows paths anywhere;** paths come from `cafa.config.load_paths()` exactly as legacy code does.
8. **OUT OF SCOPE (do not implement, even partially):** the (λ,β) cost-aware family; `weighted_ltt_select`; any RL/JAFA backbone; new datasets; changes to the synthetic generators; deleting anything; CI/GitHub Actions; type-checking overhauls; renaming existing public functions.

---

## D. LOCKED DESIGN DECISIONS (the "final say" — implement as stated)

| # | Decision |
|---|---|
| D1 | **C1 fix:** tabular greedy imputes each candidate feature at its **train-column-mean vector** (computed from the fixed train split's *encoded* matrix: ≈0 for standardized numerics, category frequencies for one-hot blocks). Constructor requires the means; no silent fallback. "EDDI-style" wording removed everywhere; both greedy policies are documented as "myopic mean-imputation entropy" heuristics. |
| D2 | **C2 fix (and S2 upgrade):** all datasets move to a **fixed-train / resplit-heldout** scheme. `train_seed` (default 0) fixes the train split; one backbone per (dataset, train_seed); the heldout 40% is the only thing resplit. Robustness backbones at train_seed ∈ {1,2} are a separate, later phase. |
| D3 | **Probe split (fixes C3, C5, M7):** 10% of the heldout pool (fixed seed 777) becomes the **probe**: it alone determines (a) the full-acquisition floor and thus α via the existing `feasible_alpha_from_floor` rule, (b) the stratum edges for every λ_ref, bucket scheme, and n_buckets, (c) the committed per-scheme feature costs (computed on the fixed train split, recorded here for provenance). The remaining 90% is the **eval pool**; cal/test resplits (50/50) touch only it. Probe artifacts are committed to versioned JSON before any selection runs. |
| D4 | **α discipline:** α per (dataset, train_seed=0) = `feasible_alpha_from_floor(probe_floor)` — mechanically, whatever it returns (MNIST expected ≈0.15; do not hardcode). Recorded in the committed JSON; all methods and all robustness runs evaluate at this α. |
| D5 | **Mondrian per-stratum thresholds = AUDIT ONLY.** Per-stratum risk, certify/abstain, and the full-acquisition fallback are reported; the per-stratum *cost* operating point and the blended Mondrian operating point are dropped from headline outputs (computed nowhere in v2 headline tables). `joint=True` (δ/K) is run alongside as an ablation. |
| D6 | **The deployable per-stratum-valid object = CAFA-IUT:** a single λ certified **simultaneously against every stratum** via the intersection–union test: p_λ = max over populated strata k of the frozen per-stratum HB p-value; fixed-sequence walk over the grid at level δ; deploy the cheapest certified λ. If nothing certifies (e.g., an intrinsically infeasible stratum exists), the method **globally abstains → full acquisition**, and the audit explains which stratum blocked it. Guarantee: P(∃k: R(λ̂|k) > α) ≤ δ, no δ/K, no routing, no circularity — deployable at exactly the reported cost. (Validated by the reviewer in Monte-Carlo on the synthetic generator: any-stratum violation 0.000 at γ=0 and 0.007 at γ=0.12 over 300 draws, δ=0.10.) |
| D7 | **Pool-rollout architecture:** per (dataset, train_seed, policy) the heldout pool is rolled out **once**, storing `scores`, `correct`, `order` (feature chosen per step), `y`, `row_ids`. Cumulative costs are **recomputed post-hoc** per cost scheme from `order` (trajectories are cost-scheme-invariant because both policies ignore costs — assert this in code comments). Resplits are row-index slices of the cache. Consequence: ≥100 fixed-backbone resplits and all three cost schemes are nearly free. |
| D8 | **Statistics:** violation fractions over 100 resplits reported with **Wilson 95% CIs** (footnote: resplits share the pool, intervals heuristic). Stratum infeasibility decided on the **full eval pool** (not resplits): infeasible ⟺ one-sided **Clopper–Pearson 95% lower bound** on R_full(k) > α; feasible ⟺ one-sided 95% *upper* bound < α; otherwise **undetermined** — three-way verdicts, always printed. `none_rate` (abstention) reported explicitly for every method; never silently dropped. |
| D9 | **Fork metrics** (decides the paper's central claim): per (dataset, policy, λ_ref): number of populated strata (deduplicated — marginal results counted once, not per λ_ref); reference-depth concentration on the eval pool (IQR and normalized entropy); detection outcome (does the audit flag an infeasible stratum at 95% LCB); IUT-vs-marginal cost premium. |
| D10 | **λ_ref sweep kept:** {0.5, 0.7, 0.9}. Bucket-scheme ablation: quantile vs equal-width edges; n_buckets ∈ {3,5,8}; min_per_bucket ∈ {25,50,100} — all post-hoc from committed probe edges. |
| D11 | **Policies:** Phase 1 = honest greedy + random. Phase 2 (implemented now, run later) = **ε-greedy mixtures**, ε ∈ {0.25, 0.5}: at each step, with prob ε acquire a uniformly random unacquired feature, else the greedy choice; seeded once per pool rollout. |
| D12 | **Score ablation:** primary readiness score stays `softmax`. One ablation cell only: `margin` on spambase (Phase 5). No entropy-score runs. |
| D13 | **Deferred (documented as future work, not implemented):** (λ,β) family; weighted-CAFA; second backbone family; real-cost dataset; e-process variant. The detection-power **lemma is a writing task**, not code — but its empirical face (detection-outcome vs n·q and Δ scatter) *is* computed by the analysis script. |
| D14 | **Legacy `fetch_openml` versions preserved:** adult v2, MiniBooNE v1, spambase v1 via the existing config-aware loader. Do not change dataset versions. |
| D15 | **Every theorem-relevant invariant becomes a runtime assertion:** train/probe/eval pairwise disjointness; probe-committed edges' provenance hash; "no unpaid value reaches the scorer" (policy-honesty regression test); frozen-file sha256 manifest. |

---

## E. WORK ORDERS

Execute in order. Each WO states: files, contract, and critical details. Where a code snippet is given, it is normative for the lines it shows; fill the rest to match repo style (numpy-docstrings, type hints as in existing modules).

### WO-0 — Save this spec + repo hygiene
- Ensure this file exists at repo root as `CLAUDE_CODE_WORKORDER.md` (the operator placed it; if the name differs, rename to this).
- Create empty dirs with `.gitkeep`: `repro/`, `analysis_v2/` is *not* committed (add to `.gitignore` along with `metrics_v2/`, `figures_v2/` — results are pushed back selectively by the operator; add a `results_committed/` dir with `.gitkeep` that IS tracked, where the operator will copy final JSONs + RESULTS.md for the paper artifact).
- Append to `.gitignore`: `metrics_v2/`, `analysis_v2/`, `figures_v2/`, `*.lock.txt` is NOT ignored (tracked), `__pycache__/` if absent.

### WO-1 — Fix the clairvoyant tabular greedy (C1) — `src/cafa/tabular.py`
**Edit `TabularGreedyEntropyPolicy`:**
```python
class TabularGreedyEntropyPolicy:
    """Myopic mean-imputation entropy policy (cost-unaware, deployable).

    For every unacquired feature a, form the hypothetical observed set
    O ∪ {a} with a's encoded columns imputed at their TRAIN means (computed
    on the fixed train split: ~0 for standardized numerics, category
    frequencies for one-hot blocks), score the predictor's entropy, and
    acquire argmin. The candidate's TRUE value is never consulted before
    acquisition ("no unpaid value reaches the scorer").
    """
    name = "greedy_entropy"

    def __init__(self, col_means: np.ndarray, cand_chunk: int = 16):
        cm = np.asarray(col_means, dtype=np.float32).ravel()
        if cm.ndim != 1 or cm.size == 0:
            raise ValueError("col_means must be a non-empty 1-D [n_cols] array.")
        self.col_means = cm
        self.cand_chunk = int(cand_chunk)

    @classmethod
    def from_training_data(cls, X_train, seed: int = 0):
        X = np.asarray(X_train, dtype=np.float32)
        if X.ndim != 2:
            raise ValueError(f"X_train must be [N, n_cols]; got {X.shape}.")
        return cls(col_means=X.mean(axis=0))
```
**`select_next` core change** (keep the loop structure; the only semantic change is what the predictor sees):
```python
        base_col_mask = expand_feature_mask(observed_feat, feature_groups)   # [B, n_cols]
        X_obs = X * base_col_mask          # true values ONLY where already paid for
        ...
        for a in range(d):
            cand_mask = base_col_mask.copy()
            cand_mask[:, feature_groups[a]] = 1.0
            X_cand = X_obs.copy()
            X_cand[:, feature_groups[a]] = self.col_means[feature_groups[a]][None, :]
            probs = np.asarray(predictor.predict_proba(X_cand, cand_mask, device=device), dtype=float)
```
Notes: `predict_proba` multiplies by the mask internally (`X*mask`), so passing `X_cand` with mean values under `cand_mask=1` yields exactly mean-imputed candidates and true observed values; hidden non-candidates are zeroed twice (harmless).
- Add an inline assertion comment: `# INVARIANT (C1): X_cand[:, group_a] contains train means, never X[:, group_a].`
- `get_tabular_policy` / `from_training_data` call sites already pass `X_train` (`run_mondrian.py` does; the new pool runner will too). In `tabular_rollout`, the string-policy convenience path builds the policy from the rollout `X` itself — change its comment to warn this is test-only and leaks nothing (means from the same rows are population statistics, but production code must pass a train-built policy), and keep behavior (existing tests rely on it).
- Remove the word "EDDI" from this module; fix the class and module docstrings to the honest description above. Also update the **image** policy docstring in `src/cafa/acquisition.py` to drop "EDDI-style" (mechanics there are already honest — do not change its logic).

### WO-2 — Split machinery with hard assertions (C2/C3/D2/D3) — new `src/cafa/splits.py`
Pure numpy. Public API (exact signatures):
```python
def fixed_train_heldout(n_total: int, train_frac: float, train_seed: int) -> tuple[np.ndarray, np.ndarray]
def probe_eval_split(heldout_idx: np.ndarray, probe_frac: float, probe_seed: int = 777) -> tuple[np.ndarray, np.ndarray]
def resplit_cal_test(eval_idx: np.ndarray, resplit_seed: int, cal_frac: float = 0.5) -> tuple[np.ndarray, np.ndarray]
def assert_disjoint(**named_index_sets) -> None   # raises AssertionError naming the offending pair
def split_digest(*index_arrays) -> str            # sha256 hex of concatenated sorted int64 bytes (provenance)
```
Behavior:
- `fixed_train_heldout`: `rng = np.random.default_rng(train_seed)`; permutation of `n_total`; first `round(train_frac*n_total)` = train, rest = heldout. **train depends only on `train_seed`.**
- `probe_eval_split`: permute `heldout_idx` with `default_rng(probe_seed)`; first `round(probe_frac*len)` = probe. **probe_seed is fixed at 777 in config — the probe is identical across every resplit and every run.**
- `resplit_cal_test`: permute `eval_idx` with `default_rng(1_000_000 + resplit_seed)` (offset so resplit seeds never collide with train/probe streams); first `cal_frac` = cal, rest = test.
- Every function returns **sorted-by-permutation** (i.e., permuted order, not re-sorted) int64 arrays; document that row order within a split is itself deterministic.
Module docstring must state the invariant chain: `train ⟂ heldout; probe ⟂ eval; cal ⟂ test; (train ∪ probe) never enters selection or evaluation; edges/α/costs are functions of (train, probe) only.`

### WO-3 — v2 data loaders — edits to `src/cafa/data.py` (ADDITIVE ONLY; legacy functions untouched)
Add:
```python
def load_mnist_pool(cfg: dict, train_seed: int, download: bool = False) -> dict
def load_tabular_pool(name: str, cfg: dict, train_seed: int, download: bool = False) -> dict
```
Both return:
```
{
  "train": (X_train, y_train),          # fixed train split (train_seed only)
  "heldout": (X_held, y_held),          # ALL heldout rows, in fixed order
  "heldout_index": np.ndarray,          # indices into the original pooled order
  "probe_pos": np.ndarray,              # positions WITHIN heldout arrays (from probe_eval_split)
  "eval_pos": np.ndarray,
  "feature_costs_by_scheme": {scheme: np.ndarray[d]},   # tabular only; {"uniform": ones} for mnist
  "feature_groups": ...,                # tabular only
  "n_classes", "n_cols"/"n_patches", "name", "train_seed", "split_digest": {...}
}
```
Rules:
- Use `splits.fixed_train_heldout` with `protocol_v2.train_frac` (0.6) and `splits.probe_eval_split` with `protocol_v2.probe_frac` (0.10) — **positions are computed over the heldout arrays, not global indices**, so downstream code slices `X_held[probe_pos]` etc.
- MNIST: pool = official train+test concatenated exactly as legacy (`/255.0`, patchify). Tabular: reuse the existing fetch/encode path (`openml_spec_for` + the `_frame_to_afa`-style encoding) but **fit scaler/OHE on the fixed train split** and compute `assign_feature_costs` for ALL THREE schemes (`uniform`, `inverse_info`, `random` with seed 0) on the fixed train — returned in `feature_costs_by_scheme`.
- Call `splits.assert_disjoint(train=..., probe=global_probe_idx, eval=global_eval_idx)` before returning; store `split_digest` for train/probe/eval.
- Do not modify `load_mnist_afa` / `load_tabular_afa` / `load_tabular_afa_cfg`.

### WO-4 — Pool-rollout cache + post-hoc costs — new `src/cafa/pool.py`
Torch-free module (rollout itself happens in the runner script, which imports torch lazily; this module defines the cache format and the pure post-hoc math).
```python
CACHE_VERSION = 2

def save_pool_cache(path, *, scores, correct, order, y, row_pos, meta: dict) -> None
def load_pool_cache(path) -> dict        # validates CACHE_VERSION and required keys
def cum_cost_from_order(order: np.ndarray, feature_costs: np.ndarray) -> np.ndarray
def slice_rows(cache: dict, pos: np.ndarray) -> dict   # returns views/copies of scores/correct/order/y for given positions
```
- Arrays: `scores`, `correct` are `[n, T+1]` float; `order` is `[n, T]` int (feature acquired at step t); `y` `[n]`; `row_pos` `[n]` = positions within the heldout arrays (must equal `np.arange(n)` for a full-pool cache — assert; kept for future partial caches).
- `cum_cost_from_order`: `cc[:,0]=0; cc[:,t+1]=cc[:,t]+feature_costs[order[:,t]]` — vectorize with `np.take` + `cumsum`; shape `[n, T+1]`.
- `meta` (stored as JSON string inside the npz under key `meta_json`): dataset, policy, epsilon (None for pure policies), score name, train_seed, backbone checkpoint filename + its sha256, split_digest dict, T, n, numpy version, created ISO timestamp.
- Add a normative comment: `# Trajectories are cost-scheme-invariant: neither greedy nor random consults feature_costs. cum_cost is therefore derived, not stored.`

### WO-5 — CAFA-IUT — new `src/cafa/risk_control_ext.py`
Composes ONLY frozen primitives. Public API:
```python
@dataclass
class IUTResult:
    valid_mask: np.ndarray        # [G] bool
    lambda_idx: Optional[int]     # cheapest certified (== smallest certified; see cost-blindness note)
    lambda_value: Optional[float]
    p_union: np.ndarray           # [G]
    per_stratum_pvalues: dict     # k -> np.ndarray [G]
    stratum_sizes: dict           # k -> int (calibration rows)
    alpha: float; delta: float

def iut_select(losses, costs, grid, alpha, delta, bucket_id,
               procedure: str = "fixed_sequence", min_stratum_warn: int = 30) -> IUTResult
```
Implementation contract:
- For each populated stratum k: `pv_k = ltt_select(losses[mask_k], costs[mask_k], grid, alpha, delta, procedure=procedure).pvalues` (uses the frozen selector purely as a vectorized HB p-value engine; its per-stratum selection output is ignored).
- Strata with **zero** calibration rows contribute `p ≡ 1.0` (blocks certification — conservative by design); strata with `0 < n_k < min_stratum_warn` emit a `warnings.warn` naming k and n_k.
- `p_union = max over strata`; fixed-sequence walk from the top exactly as the frozen selector does (largest λ first, certify while ≤ δ, stop at first failure); `lambda_idx = argmin c_hat over certified` computed from the full `costs` column means (equals the smallest certified index — note this in the docstring, citing the cost-blindness lemma).
- Docstring must contain the validity argument verbatim:
  *"Union-null p-value: for H_λ = ∪_k {R(λ|k) > α}, p_λ := max_k p_{λ,k} is super-uniform, because if H_λ holds then some H_{λ,k*} holds and P(p_λ ≤ u) ≤ P(p_{λ,k*} ≤ u) ≤ u (intersection–union test). FWER over the grid then gives P(∃ λ∈Λ̂, ∃k: R(λ|k) > α) ≤ δ, hence P(∀k: R(λ̂|k) ≤ α) ≥ 1−δ for the deployed λ̂. Global abstention (empty Λ̂) makes no claim and is the correct outcome when some stratum is α-infeasible."*
- No torch import; no edit to the frozen file.

### WO-6 — Bug-verification script (verification-first) — new `scripts/verify_bugs.py`
Torch-free, runnable on a login node. Three sections, each printing PASS/FAIL:
1. **C1 honesty probe (post-fix regression):** build a 1-row `X = [[7.0, -3.0, 2.5]]`, identity feature groups, a recording dummy predictor; construct `TabularGreedyEntropyPolicy(col_means=np.array([0.5, 0.5, 0.5]))`; call `select_next`; **assert** the value reaching the predictor for each candidate column equals 0.5 (the mean) and never the true value. Print the observed values.
2. **C2 legacy-leak demonstration + v2 guarantee:** re-implement the legacy `_disjoint_split_indices` logic inline (or import it); for seeds 0..19 compute `|cal_s ∪ test_s ∩ train_0| / |cal_s ∪ test_s|` on n_total=70_000 and print the table (expected ≈0.60 for s≠0, 0.0 for s=0). Then compute v2 splits (`fixed_train_heldout` + `probe_eval_split` + `resplit_cal_test` for resplit seeds {0, 1, 57, 99}) and **assert** zero overlap of every cal/test with train and probe. Print PASS.
3. **Freeze check:** compute sha256 of `src/cafa/risk_control.py` and `tests/test_risk_control.py`; compare against `repro/MANIFEST.sha256` (WO-17); print match/mismatch.
Exit code nonzero on any FAIL. Header comment: results are appended by the operator to `repro/BUGLOG.md`.

### WO-7 — Backbone training v2 — new `scripts/train_backbone_v2.py`
One script, both dataset families:
```
python scripts/train_backbone_v2.py --dataset mnist --train-seed 0 [--device cuda] [--download]
python scripts/train_backbone_v2.py --dataset tabular:adult --train-seed 0 [--device cpu]
```
- Loads via WO-3 pool loaders; trains `MaskedPredictor` (mnist, `training` cfg block) or `TabularMaskedPredictor` (tabular, `training_tabular` cfg block) on the **fixed train split** with the existing training functions; seeds torch/numpy from `train_seed` exactly as the legacy trainer does.
- Checkpoint: `${RESULTS_ROOT}/checkpoints_v2/{dsname}_ts{train_seed}.pt` where dsname = `mnist` or `tabular-adult` etc. Payload meta must include: dataset, train_seed, split_digest (train), n_train, encoder provenance (tabular: n_cols, feature_groups widths), training cfg, final masked train acc, `pipeline: "v2"`.
- Tabular note: the encoded design depends on the train-fitted encoders, which depend only on `train_seed` — the pool loader is the single source of truth; the trainer must not re-fit anything itself.
- Prints the checkpoint path and its sha256 (the pool runner will embed it in cache meta — implement sha in a small shared helper `cafa/repro_utils.py::file_sha256`).

### WO-8 — Pool rollout runner — new `scripts/run_pool_rollout.py`
```
python scripts/run_pool_rollout.py --dataset mnist --policy greedy_entropy --train-seed 0 --device cuda
python scripts/run_pool_rollout.py --dataset tabular:MiniBooNE --policy random --train-seed 0 --device cpu
python scripts/run_pool_rollout.py --dataset tabular:adult --policy eps_greedy --epsilon 0.25 --train-seed 0
python scripts/run_pool_rollout.py --cell K            # slurm array decode over the Phase-1/2 cell list
```
- Loads pool (WO-3) + checkpoint (WO-7, assert `meta.pipeline == "v2"` and train_seed match); rolls out the **entire heldout split** (probe + eval rows together, in heldout order) with the requested policy and `procedure_score` from config; **must record `order`** — extend the rollout loops minimally:
  - MNIST: write a thin wrapper in this script that mirrors `cafa.acquisition.rollout` but also records `nxt` per step into `order` (do NOT edit the frozen-ish `acquisition.py` rollout; copy its loop here with a comment `# mirrors cafa.acquisition.rollout + order recording; keep in sync`). Costs passed to the wrapper are all-ones (cum_cost from the wrapper is discarded; `order` is the artifact).
  - Tabular: same treatment mirroring `tabular_rollout`.
- ε-greedy: implement in this script (or a tiny `src/cafa/policies_v2.py`, your choice — if a module, torch-free) as a wrapper policy: `rng = np.random.default_rng(policy_seed)` with `policy_seed = 10_000 + int(round(1000*epsilon))`; per instance-step, Bernoulli(ε) → random unacquired else greedy's pick. Batched implementation: compute greedy picks for the batch, compute random picks, mix with a Bernoulli mask.
- Cache path: `${RESULTS_ROOT}/pool_v2/{dsname}_ts{ts}_{policy}[_eps{ε}]_{score}.npz` via `pool.save_pool_cache`, with full meta incl. checkpoint sha and split digests.
- Cell list for `--cell` (document in-script, order fixed): Phase-1 cells = [mnist, adult, MiniBooNE, spambase] × [greedy_entropy, random]; Phase-2 cells = tabular×3 + mnist, × eps ∈ {0.25, 0.5}; Phase-5 extra = (spambase, greedy_entropy, score=margin). Print the resolved cell before running.

### WO-9 — Probe commit (α, edges, costs — pre-committed provenance) — new `scripts/probe_commit.py`
```
python scripts/probe_commit.py --dataset tabular:adult --train-seed 0
```
Reads the greedy-policy pool cache (probe rows only; **edges must come from the same score process used at deployment**, and separately also from the random cache — see below), computes and writes `configs/committed_v2_{dsname}_ts{ts}.json`:
```json
{
  "dataset": ..., "train_seed": 0, "cache_meta": {...}, "probe_n": TBD-int,
  "floor": {"estimate": ..., "cp_lcb95": ..., "cp_ucb95": ...},
  "alpha": <feasible_alpha_from_floor(floor_estimate)>,
  "feature_costs_by_scheme": {...},
  "edges": { "<policy>": { "<lambda_ref>": {
        "quantile": {"3": [...], "5": [...], "8": [...]},
        "equal_width_merged": {"5x25": [...], "5x50": [...], "5x100": [...]} } } },
  "created": ISO, "tool": "probe_commit.py"
}
```
Rules:
- **Floor** = mean(1 − correct_probe[:, T]) from the **greedy** cache (policy-invariant at t=T; assert the random cache agrees to < 1e-12 if present). CP bounds: for k = #errors of n: `lcb = beta.ppf(0.05, k, n-k+1)` (0 if k==0), `ucb = beta.ppf(0.95, k+1, n-k)` (1 if k==n).
- **α** = `feasible_alpha_from_floor(floor_estimate)` — the existing function, defaults. No overrides. (α is per dataset at ts=0; robustness train-seeds reuse ts=0's α — enforce in WO-10 by always reading the ts=0 committed file for α.)
- **Edges per policy** (greedy and random caches both, plus eps-greedy when present): for each λ_ref ∈ config sweep: quantile edges via existing `quantile_bucket_edges(probe_scores, λ_ref, n_buckets)` for n_buckets ∈ {3,5,8}; equal-width-merged edges via `reference_buckets(probe_scores, λ_ref, 5, mpb, edges=None)[1]` for mpb ∈ {25,50,100}. Edges are floats, JSON lists.
- Refuse to overwrite an existing committed file unless `--force` (pre-commitment means committed once).

### WO-10 — Eval sweep (the resplit engine) — new `scripts/run_eval_sweep.py`
```
python scripts/run_eval_sweep.py --dataset tabular:adult --policy greedy_entropy --train-seed 0
python scripts/run_eval_sweep.py --cell K     # slurm decode over Phase-1 dataset×policy cells
```
For the (dataset, policy) cache and the ts=0 committed JSON:
1. Slice eval rows; build `losses[G]`/`stop_depth` once via `stops_from_grid_np(scores, correct, cum_cost_uniform, grid)` — but note costs differ per scheme: compute `cum_cost` per scheme via `pool.cum_cost_from_order` and the committed `feature_costs_by_scheme`, then per-scheme `costs` matrices with a second/third `stops_from_grid_np` call reusing the same scores (or refactor: compute stop index matrix `s[n,G]` once, then `losses = 1-correct[rows,s]`, `costs_scheme = cc_scheme[rows,s]` — implement this direct form; it is exact and 3× cheaper).
2. `bucket_id_eval` per λ_ref from the committed **quantile n_buckets=5** edges (primary); risk is scheme-invariant.
3. For `resplit_seed` in `range(cfg.protocol_v2.n_resplits)` (=100): positions via `splits.resplit_cal_test(eval_positions, resplit_seed)`; then per λ_ref ∈ {0.5,0.7,0.9}:
   - **cafa_marginal**: frozen `ltt_select` on cal (α, δ from committed/config); realized test risk + per-scheme cost + λ_idx + certified-set size + per-stratum realized risk at the marginal λ̂ (for the audit table).
   - **cafa_iut**: WO-5 `iut_select` with cal `bucket_id`; realized test risk/costs; `none` ⇒ global abstention ⇒ realized = full-acquisition risk & cost, flagged `abstained: true`.
   - **mondrian_audit**: frozen `mondrian_select` joint=False AND joint=True on cal; record per-stratum λ_idx / abstentions and per-stratum realized TEST risk (per_bucket_risk); **no cost operating point** (D5).
   - **baselines**: plugin (cal), fixed_conf {0.90,0.95,0.99}, budget {5,10,20 clamped}; **oracles**: cheapest-valid (test), full-feature — reuse `cafa.baselines` functions unchanged; oracle per scheme for costs.
   - Marginal/IUT/plugin `lambda_idx is None` ⇒ record `abstained: true` with fallback full-acq realized numbers; NEVER drop.
4. Once per (dataset, policy, λ_ref), on the **full eval pool**: per-stratum `R_full(k)` = mean full-acq loss with CP one-sided bounds (formulas as WO-9) and verdict ∈ {infeasible, feasible, undetermined} (D8); marginal floor + CI; reference-depth concentration stats: `iqr = np.subtract(*np.percentile(depth, [75, 25]))` and normalized entropy `H(p)/log(#support)` of the empirical depth distribution.
5. Output one JSON per (dataset, policy): `metrics_v2/{dsname}_ts{ts}_{policy}.json` with schema `{meta, alpha, delta, grid, lambda_refs: {lr: {population: {...}, resplits: [ {seed, methods: {...}} ] }}}`. Keep floats rounded to 6 dp to bound file size.
δ = `method.delta` (0.10). Grid = existing config grid. Print a 3-line summary per λ_ref (marginal violation count, IUT abstention count, #infeasible strata).

### WO-11 — Analysis + RESULTS.md — new `scripts/analyze_results.py`
```
python scripts/analyze_results.py [--metrics-dir ...] [--out analysis_v2]
```
Reads all `metrics_v2/*.json`; writes `analysis_v2/RESULTS.md` + machine-readable CSVs. Content contract:
1. **Header:** datasets found, α/δ per dataset (from committed), n_resplits, cache/backbone shas.
2. **H2 table** per (dataset, policy, cost scheme): rows = cafa_marginal, cafa_iut, plugin, fixed_conf×3, budget×3, oracle_cheapest, oracle_full. Columns = violation_frac over resplits with **Wilson 95% CI**, none/abstain rate, mean realized risk, mean realized cost, cost ratio vs full. Wilson: center `(p̂ + z²/2n)/(1+z²/n)`, half-width `z√(p̂(1−p̂)/n + z²/4n²)/(1+z²/n)`, z=1.96. Footnote the resplit-dependence caveat verbatim: *"Resplits share a finite eval pool; intervals are heuristic under dependence."*
3. **Audit table** per (dataset, policy, λ_ref): per stratum — eval size, mean±sd (over resplits) marginal realized risk, mondrian per-δ cert-rate & abstain-rate, joint-δ ditto, `R_full(k)` [LCB, UCB], **verdict**. Bold the verdict line `infeasible` only when LCB > α.
4. **Deployable comparison:** IUT vs marginal — cost premium (per scheme), abstention rate, and the sentence template *"uniform per-stratum validity costs TBD-RUN× the marginal certificate on <dataset>"* filled from data.
5. **Fork metrics** (D9): strata-count table (λ_ref × policy, **marginal rows deduplicated**); depth IQR + normalized entropy per policy; detection outcome per (dataset, policy): flagged-infeasible? at which λ_ref; a one-line per-dataset fork verdict template the operator will read: `insight_signal = (greedy strata < random strata) AND (detection requires λ_ref ≥ TBD)` printed as data, no editorializing.
6. **Ablations:** recompute audit verdicts under quantile n_buckets {3,8} and equal-width {5×25,5×50,5×100} edges (post-hoc from the committed edges + cached matrices — this script re-derives bucket_id and re-runs `mondrian_select`/verdicts on 25 of the 100 resplit seeds to bound runtime; state the subset).
7. **Detection-power scatter data** (CSV): per (dataset, policy, λ_ref, stratum): `n_cal_mean*q`, `Δ̂ = R_full_LCB − α`, detected(0/1); plus the guide-curve column `n_req = log(1/δ)/(2*Δ̂²)` (Hoeffding heuristic; label it heuristic).
8. **GATES block** printed at the end: marginal violation_frac ≤ δ (per dataset, PASS/FAIL against the Wilson upper bound), IUT any-stratum violation computed from per-stratum realized risks ≤ δ, freeze sha check delegated note.
No torch. No plotting here.

### WO-12 — Figures — new `scripts/make_figures_v2.py`
matplotlib only; reads `metrics_v2` + `analysis_v2` CSVs; writes `figures_v2/*.pdf` and `.png` (150 dpi):
- **F1** per dataset: realized (risk, cost) scatter, mean over resplits with CI error bars; α vertical line; oracle-cheapest star; oracle-full square; one panel per policy, primary scheme `inverse_info` (uniform for MNIST).
- **F2** per (dataset, λ_ref=0.9, greedy): per-stratum bars of marginal realized risk (CI whiskers over resplits), α line, fallback `R_full(k)` tick with its LCB whisker; abstaining strata hatched.
- **F3** two panels: (a) populated-strata count vs λ_ref per policy; (b) depth IQR per policy — the concentration evidence independent of binning.
- **F4** detection scatter: x = n_cal·q (log), y = Δ̂; markers by detected; dashed guide curve `n·q = log(1/δ)/(2Δ²)`.
Every figure title carries dataset + ts; no invented styling beyond matplotlib defaults + labels.

### WO-13 — ε-greedy registration (Phase 2 plumbing)
If implemented as `src/cafa/policies_v2.py`: torch-free `EpsGreedyMixture(greedy_policy, epsilon, seed)` exposing the same `select_next` signature as tabular policies (and a thin image variant in the WO-8 script for MNIST). Register in the WO-8 runner's `--policy eps_greedy --epsilon E` path and in the cell list. No other pipeline changes — caches/eval/analysis already key on the policy string `eps_greedy_eps0.25` etc. (use exactly that token in filenames and JSON `policy` fields).

### WO-14 — New tests — `tests/` (add; never edit frozen ones)
1. `tests/test_policy_honesty.py` — the WO-6 §1 probe as a pytest (tabular); plus an image-policy assertion using a monkeypatched `logits_from_patches` recorder verifying candidate patch pixels equal the stored `patch_means` (skip with `pytest.importorskip("torch")`).
2. `tests/test_splits_v2.py` — determinism (same seeds ⇒ identical arrays); pairwise disjointness incl. probe vs every resplit's cal/test for seeds {0,1,57,99}; probe invariance across resplit seeds; `split_digest` stability.
3. `tests/test_pool_v2.py` — `cum_cost_from_order` equals a hand-computed 3×4 example AND equals a brute-force loop on random inputs; `slice_rows` round-trip; cache save/load round-trip with meta (use tmp_path).
4. `tests/test_iut.py` — (a) union-null validity Monte-Carlo on `make_synthetic_mondrian`: n=2000, T=49, γ ∈ {0.0, 0.12}, 150 draws, pre-committed edges from an independent probe draw (seed offset 10_000), assert any-stratum TRUE-risk violation rate ≤ δ + 0.05 slack and (γ=0.12) certification occurs in ≥ 80% of draws; (b) an empty stratum in cal ⇒ that stratum's p ≡ 1 ⇒ certification blocked (construct directly). Runtime target < 90 s.
5. `tests/test_probe_commit.py` — schema round-trip on a synthetic cache written to tmp; `--force` semantics (function-level, not CLI).
Mark nothing as slow; the whole added set must be plausible < 3 min CPU.

### WO-15 — Config additions — `configs/experiment.yaml` (append a clearly delimited block; change no existing key)
```yaml
# --- v2 protocol (fixed-train / probe / resplit; see CLAUDE_CODE_WORKORDER.md) ---
protocol_v2:
  train_frac: 0.6
  probe_frac: 0.10          # of the heldout pool; probe_seed fixed below
  probe_seed: 777
  train_seed_primary: 0
  train_seeds_robustness: [1, 2]
  n_resplits: 100
  cal_frac_of_eval: 0.5
mondrian_v2:
  lambda_refs: [0.5, 0.7, 0.9]
  n_buckets_primary: 5
  n_buckets_ablation: [3, 8]
  min_per_bucket_ablation: [25, 50, 100]
  edges_source: probe        # documentation of D3; code reads committed JSONs
iut:
  enabled: true
policies_v2:
  epsilons: [0.25, 0.5]
score_ablation:
  cells: [{dataset: "tabular:spambase", policy: greedy_entropy, score: margin}]
```

### WO-16 — Slurm files — new `hpc/pool_rollout.slurm`, `hpc/eval_sweep.slurm`
- **Copy the module-load / env-var / logging preamble verbatim from the existing `hpc/train.slurm` and `hpc/sweep.slurm`** (they encode FAU NHR conventions: path-free, env vars, no `--mem` on tinygpu). Do not invent partition names; keep whatever those files use, add `# ADJUST IF NEEDED` comments where cluster-specific.
- `pool_rollout.slurm`: array job; `python scripts/run_pool_rollout.py --cell ${SLURM_ARRAY_TASK_ID} --device ${CAFA_DEVICE:-cuda}` ; comment documenting the Phase-1 array range (8 cells: 4 datasets × 2 policies) and Phase-2 range.
- `eval_sweep.slurm`: CPU array; `python scripts/run_eval_sweep.py --cell ${SLURM_ARRAY_TASK_ID}`; Phase-1 range = 8.
- Both export `PYTHONPATH="$SLURM_SUBMIT_DIR/src:$PYTHONPATH"` consistent with existing files.

### WO-17 — repro/ artifacts
- `repro/MANIFEST.sha256`: two lines, computed by you from the current bytes of `src/cafa/risk_control.py` and `tests/test_risk_control.py` in `sha256sum` format (`<hash>  <path>`). (You may compute a sha mentally? No — you cannot run code. Instead: create `repro/make_manifest.sh` with `sha256sum src/cafa/risk_control.py tests/test_risk_control.py > repro/MANIFEST.sha256` and `repro/verify_freeze.sh` with `sha256sum -c repro/MANIFEST.sha256`; instruct in README that the operator runs `make_manifest.sh` ONCE at the pre-fix commit and never again.)
- `repro/BUGLOG.md`: template with sections C1/C2/C3/C4/C5, each containing: description (one line, copy from §B), fixing commit `TBD-RUN`, verification command (`python scripts/verify_bugs.py`), observed output `TBD-RUN`.
- `repro/requirements.lock.txt`: create containing only the line `# Generate on the cluster with: pip freeze > repro/requirements.lock.txt  (then commit)`.

### WO-18 — Deprecation headers + README rewrite
- Prepend to each legacy script (`run_experiment.py`, `run_mondrian.py`, `run_mondrian_mnist.py`, `aggregate_results.py`, `make_figures.py`, `alpha_probe.py`, `step5_selfcheck_synth.py`, `step5_report.sh`, `step5_sweep_tinygpu.sh`) a 4-line comment block:
  `DEPRECATED (kept for provenance). Superseded by the v2 pipeline (see README + CLAUDE_CODE_WORKORDER.md). Known issues in the legacy pipeline: per-seed full-pool reshuffle (MNIST leakage), cal-fit stratum edges, clairvoyant tabular greedy (pre-fix), λ_ref-duplicated marginal counting. Do not use for paper numbers.`
- **README.md: full rewrite.** Required sections, in order: (1) one-paragraph project summary + the guarantee statement; (2) *Status*: v2 repair release, what changed and why (C1–C5, one line each); (3) repo layout (v2 files annotated, legacy marked deprecated); (4) environment (conda env, torch install note, lock-file instruction); (5) data download (openml pre-fetch on login node, MNIST download — reuse legacy commands); (6) **Pipeline** — the exact §F command sequence, numbered, copy-paste-ready; (7) split & pre-commitment scheme diagram (ASCII: pool → train(ts) → backbone; heldout → probe(777) → {α, edges, costs} committed; eval → 100 × cal/test); (8) methods glossary (marginal, IUT, Mondrian-audit, baselines, oracles — 1–2 lines each incl. the IUT guarantee sentence and the cost-blindness lemma sentence); (9) outputs schema (`metrics_v2` JSON keys, `analysis_v2/RESULTS.md`, `figures_v2`); (10) tests & gates (`pytest -q`, `verify_bugs.py`, `verify_freeze.sh`); (11) reproducibility statement (fixed seeds table: train_seed, probe_seed 777, resplit offset 1_000_000, policy seeds); (12) deprecated/provenance. **No numbers anywhere except TBD-RUN placeholders.**

---

## F. CLUSTER COMMAND SEQUENCE (Claude Code prints this verbatim at the end; also lives in README §6)

Environment (once per session, as in the legacy README):
```bash
module load python/3.12-conda
source activate "$CAFA_ENV"
export CAFA_REPO=~/my_repos/CAFA_exp        # adjust
cd "$CAFA_REPO"
export PYTHONPATH="$PWD/src:$PYTHONPATH"
# DATA_ROOT / RESULTS_ROOT already exported per legacy setup
```

**Phase 0 — verify before compute (login node, ~5 min):**
```bash
pytest -q                                    # all tests incl. new v2 tests must pass
bash repro/make_manifest.sh                  # FIRST TIME ONLY (records frozen hashes)
python scripts/verify_bugs.py                # expect: C1 PASS, C2 legacy table + v2 PASS, freeze PASS
pip freeze > repro/requirements.lock.txt     # commit this
```
Gate: proceed only if everything passes. Append verify output to repro/BUGLOG.md and commit.

**Phase 1a — backbones (primary train seed):**
```bash
python scripts/train_backbone_v2.py --dataset mnist            --train-seed 0 --device cuda   # or cpu
for d in adult MiniBooNE spambase; do
  python scripts/train_backbone_v2.py --dataset tabular:$d --train-seed 0 --device cpu
done
```
(Or submit via `hpc/train.slurm`-style job; MNIST is the only GPU-worthwhile one.)

**Phase 1b — pool rollouts (8 cells; GPU for MNIST recommended):**
```bash
sbatch --array=0-7 hpc/pool_rollout.slurm
# equivalently, serially: python scripts/run_pool_rollout.py --cell K --device cpu   (K=0..7)
```

**Phase 1c — probe commit (login node, seconds; COMMIT the JSONs it writes):**
```bash
for d in mnist tabular:adult tabular:MiniBooNE tabular:spambase; do
  python scripts/probe_commit.py --dataset $d --train-seed 0
done
git add configs/committed_v2_*.json && git commit -m "v2: committed probe artifacts (alpha, edges, costs)"
```
Note the α values it prints — these are the paper's targets (MNIST expected 0.15 by the rule; whatever it prints is final).

**Phase 1d — eval sweep + analysis (CPU, fast):**
```bash
sbatch --array=0-7 hpc/eval_sweep.slurm      # or serially: run_eval_sweep.py --cell K
python scripts/analyze_results.py
python scripts/make_figures_v2.py
```
Outputs: `metrics_v2/*.json`, `analysis_v2/RESULTS.md` (+CSVs), `figures_v2/*`.

**Phase 1e — SEND RESULTS FOR THE FORK REVIEW.** Copy `analysis_v2/RESULTS.md` (and, if size permits, `metrics_v2/`) into `results_committed/`, commit, and send to the reviewer. **Do not draft paper text before the fork verdict.**

**Phase 2 — ε-greedy axis (pre-approved to queue anytime after 1d; interpretation waits for the fork):**
```bash
sbatch --array=8-15 hpc/pool_rollout.slurm    # eps cells per the runner's documented list
python scripts/probe_commit.py ...            # ONLY the edges sections extend; alpha/floor unchanged — script must merge, not overwrite (implement --extend-edges)
sbatch --array=... hpc/eval_sweep.slurm       # eps cells
python scripts/analyze_results.py && python scripts/make_figures_v2.py
```

**Phase 3 — robustness backbones (ts 1, 2), later:** rerun 1a–1d with `--train-seed 1` / `2`; analysis auto-groups by ts; α stays the ts=0 committed value.

**Phase 4 — score ablation (spambase/margin), later:** one pool-rollout cell + one eval cell per the config's `score_ablation`.

*(WO-9/WO-10 addendum implied above: `probe_commit.py` needs an `--extend-edges` mode that adds edge entries for new policies to an existing committed file without touching floor/alpha/costs; implement it.)*

---

## G. ACCEPTANCE CHECKLIST (Claude Code self-audit; print with ✅/❌ before finishing)

1. `git diff --stat`-level review done: `src/cafa/risk_control.py` and `tests/test_risk_control.py` untouched (byte-identical).
2. `tabular.py`: no code path lets a candidate's true value reach `predict_proba` before acquisition; constructor requires `col_means`; "EDDI" absent from `src/` (grep).
3. `splits.py` exists with the five exact signatures; probe_seed default 777; resplit offset 1_000_000.
4. Pool loaders return every key in the WO-3 contract; encoders/costs fit on fixed train only; `assert_disjoint` called.
5. `pool.py`: `cum_cost_from_order` vectorized; cache meta includes checkpoint sha + split digests; CACHE_VERSION=2 enforced on load.
6. `risk_control_ext.iut_select` imports nothing from torch; uses `ltt_select(...).pvalues` per stratum; empty stratum ⇒ p=1; docstring contains the union-null argument verbatim.
7. `run_pool_rollout.py` records `order`; mirrors (does not modify) the frozen rollout loops; ε-greedy seeding as specified; `--cell` lists documented in-script and consistent with the slurm array ranges and §F.
8. `probe_commit.py` refuses overwrite without `--force`; has `--extend-edges`; CP bound formulas exactly `beta.ppf(0.05, k, n-k+1)` / `beta.ppf(0.95, k+1, n-k)` with k=0 / k=n edge cases.
9. `run_eval_sweep.py`: risk computed once (scheme-invariant), costs per scheme via direct `[rows, s]` indexing; Mondrian audit records NO cost operating point; abstentions recorded, never dropped; JSON schema matches WO-10.
10. `analyze_results.py`: Wilson CI formula correct; marginal strata-count deduplication implemented; three-way verdicts; GATES block; ablation subset = 25 resplit seeds, stated.
11. All four figures specced in WO-12 are produced by `make_figures_v2.py` from files, not literals.
12. New tests exist (5 files), import torch only behind `importorskip`, targeted runtime noted in module docstrings.
13. Config block appended exactly; no existing key altered.
14. Slurm files copy the existing preamble; array ranges match the cell lists.
15. `repro/` contains make_manifest.sh, verify_freeze.sh, BUGLOG.md template, requirements.lock placeholder.
16. README rewritten with all 12 required sections; the §F command block appears verbatim; zero numeric results (grep for digits in claims — only TBD-RUN).
17. Deprecation headers on all 9 legacy files; no legacy file otherwise modified.
18. Repo-wide: LF endings on touched files; no absolute/Windows paths; every new module has a module docstring naming its work order (e.g., "WO-5").
19. Printed at the end: this checklist, the §F commands verbatim, and the full created/modified file list.

---

## H. FORK-REVIEW CHECKLIST (for the operator + reviewer, after Phase 1e — not Claude Code's job)

Read `analysis_v2/RESULTS.md` and answer:
1. **Correctness gates:** marginal violation ≤ δ (Wilson UB) everywhere? IUT any-stratum violations ≤ δ? If not — stop, debug, do not interpret.
2. **H2:** post-fix cost ratios (greedy, inverse_info) per dataset; plugin violation CIs — is "plugin unsafe" still supportable anywhere at 95%?
3. **H3:** which strata are `infeasible` at 95% LCB now? (adult b2 expected to survive; MiniBooNE/spambase were thin — verdicts decide.)
4. **Insight:** honest-greedy vs random — strata counts, depth IQR/entropy, detection outcomes. Branch per the authors' §4: survives / narrows / dies.
5. **IUT:** price of uniform validity (cost premium) and abstention pattern vs α — does the α-sweep story (deferred) look worth adding?
Send items 1–5 with the RESULTS.md; the reviewer returns the fork verdict + the writing plan.

---

*End of work order. Anything not covered: choose the smallest-surface option consistent with §C/§D, and leave a `# DECISION:` comment explaining it.*
