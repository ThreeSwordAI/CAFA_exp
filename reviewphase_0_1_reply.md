# Review Phase 0-1 Reply

## Executive Decision

The canonical evidence base (tag `canonical-v2.3`) is sound, internally
consistent, and supports the paper's central claims. **No rerun was
necessary**: every number was verified or exactly recomputed from stored
canonical artifacts. Three defects must be fixed in the manuscript before
Phase 2:

1. **BLOCKING -- the "0/100 full-pool violations in each of 35 cells" claim
   is FALSE.** The authoritative gate table shows 34/35 cells at exactly
   0/100 and ONE cell (mnist/greedy_entropy/train-seed-1) at **1/100**
   (rate 0.010, Wilson 95% UB 0.0545). All 35 cells PASS the precommitted
   validity gate (Wilson UB <= delta = 0.10). The abstract, contribution
   bullet 3, and the "Marginal Certification and Cost" paragraph must be
   reworded (exact replacements below). Table 2 itself is correct (its four
   primary ts0 rows are genuinely 0/100).
2. **BLOCKING -- Adult family-minimum location is a LOCAL number.** The
   manuscript says the minimum occurs at lambda = 0.899; the canonical curve
   has a 3-threshold argmin plateau at lambda in {0.8687, 0.8788, 0.8889}
   (R = 0.309030), and lambda = 0.899 gives 0.309190 (the endpoint value).
   The 0.3090-vs-0.3092 contrast survives; the location must be corrected.
3. **Detectability theorem needs explicit family-size treatment** (add a
   log M term or a fixed-family caveat), and the Figure-2 generation script
   + claim-ledger verifier are missing from the repository.

Everything else: PASS or PASS WITH WORDING CHANGE, detailed below.

## Inputs Inspected

- Manuscript: `Certified_but_Blind__Auditing_Distribution_Free_Risk_Certificates_in_Active_Feature_Acquisition (3).pdf` (8 pages; full text extracted).
- Figure 2: `F2_evaluation_detectability.pdf` + PNG (inspected visually) and
  its SOURCE DATA (`results_committed/pool_plugin_alpha_sweep.csv`,
  `pool_plugin_eval.csv`, `synthetic_power.csv`) -- values read from CSVs,
  never from pixels.
- Canonical records: `CANONICAL_RESULTS.md`, `project_update.md`,
  `RESULTS_FOR_PAPER.md`, `results_committed/FINAL_CLAIM_DECISION.md` +
  `.json`, `FIGURE1_TABLE4_VALUES.md`, the full `results_committed/` artifact
  set (family/plugin/stratum/IUT/power CSVs + MDs), `repro/MANIFEST.sha256`,
  `repro/requirements.lock.txt`, committed configs.
- Code: `src/cafa/risk_control.py` (frozen), `risk_control_ext.py`,
  `splits.py`, `pool.py`; `scripts/` (eval sweep, family_wide_feasibility,
  pool_plugin_eval, pool_stratum_eval, iut_by_lambda_ref, synthetic_power,
  final_claim_audit, phase5_provenance, pool_risk_gate, verify_bugs); tests
  (48 incl. G1, IUT union-null MC, exact-binomial helpers, splits, policy
  honesty, phase53 stats).
- NOT AVAILABLE in the repo: `Review 1.md`, `Review 2.md`,
  `CAFA_AAAI27_writing_plan.md`, an existing supplement, a Figure-2
  generation script, `claim_ledger.csv`. The audit proceeded against the
  manuscript directly; the missing items are listed as required actions.

## Canonical Freeze and Provenance

```text
Canonical Git commit:  4b8b557 (results), analyses run at 7bdb1bf
Canonical result tag:  canonical-v2.3 (supersedes v2.2 -> v2.1 -> v2; all preserved)
Canonical environment: repro/requirements.lock.txt (python 3.12, numpy 2.4.2, cluster tinyx)
Canonical manifest:    repro/MANIFEST.sha256 -- risk_control.py c37ab67bbb02..., test_risk_control.py 3ec1258ad95d... (CRLF-normalized check PASS)
Canonical manuscript:  "Certified but Blind ..." (3).pdf, 8 pages (anonymous)
Canonical Figure 1:    results_committed/figures/F1_pool_corrected.{pdf,png}; values in pool_stratum_eval.csv (verified vs manuscript: PASS)
Canonical Figure 2:    F2_evaluation_detectability.pdf; source CSVs verified; GENERATION SCRIPT MISSING FROM REPO
Canonical tables:      T1 <- family_wide_summary.csv + pool_stratum_eval.csv; T2 <- pool_risk_gate.csv + h2_table.csv; T3 <- iut_by_lambda_ref.csv
```

Tag order and supersession are documented in `project_update.md` Sections
13-16; earlier freezes are intact (verified `git tag`). Baseline is
immutable: all canonical files are committed under the tag; this audit
created only this reply (plus two documented consistency fixes to the
non-frozen working compendium, see Reruns Performed).

## Claim Ledger Audit

| Claim ID | Manuscript claim | Exact value | Source artifact | Script | Commit/tag | Verified? | Action |
|---|---|---:|---|---|---|---|---|
| C1 | Fig1 aggregate pool risk 0.141 | 0.14145159 | pool_stratum_eval.csv (agg_pool_risk_mean) | pool_stratum_eval.py | v2.3 | PASS | none |
| C2 | Fig1 s0..s3 = .091/.113/.095/.088 | 0.09131675/0.11328998/0.09480510/0.08760844 | pool_stratum_eval.csv | pool_stratum_eval.py | v2.3 | PASS | none |
| C3 | Fig1 s4 = 0.301 = 2.00 x alpha; exceeds alpha in all 100 selections | 0.30057310; exceed_freq 1.00; ratio 2.004 | pool_stratum_eval.csv | pool_stratum_eval.py | v2.3 | PASS | none |
| C4 | Fig1/T1 endpoint 0.248 [LCB 0.238], q 21.7% | 0.247855 [0.238270]; q 0.217421; n 5479 | family_wide_summary.csv; metrics JSON | family_wide_feasibility.py | v2.3 | PASS | none |
| C5 | T1 MNIST: min 0.2479, p 1.37e-79, Failure | 0.247855; 1.369e-79; both families certified | family_wide_summary.csv | family_wide_feasibility.py | v2.3 | PASS | none |
| C6 | T1 MiniBooNE: 9180/.196/0.2334 [0.2262]/0.3554 (2.37)/3.18e-98 | all match (0.233442; 3.178e-98; ratio 2.370) | family_wide_summary.csv; pool_stratum_eval.csv | -- | v2.3 | PASS | none |
| C7 | T1 Adult: 6268/.385/min 0.3090/full 0.3092 [0.2996]/0.3127 (1.56)/8.73e-93 | 0.309030/0.309190 [0.299...]; ratio 1.563; 8.733e-93 | family_wide_summary.csv | -- | v2.3 | PASS | none |
| C8 | Adult min "occurs at lambda = 0.899" | argmin plateau lambda in {0.8687, 0.8788, 0.8889} (3 ties, R 0.309030); R(0.899) = 0.309190 | family_wide_threshold_curves.csv | family_wide_feasibility.py | v2.3 | **FAIL** | replace with "lambda ~ 0.87-0.89" |
| C9 | T1 Spambase: 249/.150/0.1727 [0.1344]/0.3851 (2.57)/p 0.179/Unresolved | all match (1.794e-01) | family_wide_summary.csv | -- | v2.3 | PASS | none |
| C10 | Abstract/bullet/results: "0/100 full-pool violations in each of 35 cells" | 34/35 at 0/100; mnist/greedy/ts1 = 1/100 (UB 0.0545); 35/35 PASS gate | pool_risk_gate.csv | pool_risk_gate.py | v2.2 gate table (still authoritative) | **FAIL** | reword (below) |
| C11 | T2 primary rows 0/100 pool violations | all four ts0 greedy cells 0.000 | pool_risk_gate.csv | pool_risk_gate.py | v2.2/v2.3 | PASS | none |
| C12 | T2 costs .507/.050/.361/.091 vs oracle .490/.050/.361/.057; "5-51%"; "within 3.5% of oracle" (1.0347); "~1.60x" (1.596) | match | h2_table.csv rows (mnist 24), CANONICAL_RESULTS H2 | analyze_results.py | v2 | PASS | none |
| C13 | T3: 61/105 certify; 60/105 refuse; 40 family-failure; 20 unresolved; 0 endpoint-only; sets overlap | match | iut_by_lambda_ref.csv | iut_by_lambda_ref.py | v2.3 | PASS | none |
| C14 | One conditional violation: Spambase greedy ts1 lr0.9, certifies 1/100, that one violates | n_certified 1, cond_fail 1.0 (one configuration = one resplit = one certified selection; estimand: any-stratum exact pool risk at certified lambda) | iut_by_lambda_ref.csv | iut_by_lambda_ref.py | v2.3 | PASS | none |
| C15 | Fig2a: 0/0/0/45 at committed alpha; MNIST nonmonotone | pool_exceed 0.000 x3, 0.450 [0.356, 0.548]; mnist crossings (0.0979,0.1279], (0.1279,0.15], (0.1579,0.1879] | pool_plugin_alpha_sweep.csv; pool_plugin_eval.csv | pool_plugin_eval.py | v2.3 | PASS | none |
| C16 | Fig2b: B=5000, gamma 0.05, max null FPR 0.050 | B 5000, seed 20260712, max_FPR 0.0500, 280 grid points; nulls Delta in {0, -0.02} | synthetic_power_summary.json; synthetic_power.csv | synthetic_power.py | v2.3 | PASS | none |
| C17 | Text: benchmark signals "above 50" (3 datasets), "~0.13" (Spambase) | exact n_k*Delta_k^2 = 52.4652 / 63.9168 / 74.5111 / 0.1282 (recomputed from n_k, alpha, min family risk) | family_wide_summary.csv (recomputation) | this audit | v2.3 | PASS | figure script must use exact values |
| C18 | "p <= 1.4e-79" as bound over the three certified datasets | max of {1.369e-79, 3.178e-98, 8.733e-93} = 1.369e-79 | family_wide_summary.csv | -- | v2.3 | PASS | none |
| C19 | Eq 15 identity + "can overstate" | identity exact by construction; asserted per resplit in pool_stratum_eval.py; "can" (not "always") is correct | pool_stratum_eval.py asserts; POOL_RISK_GATE.md (rho = -1.0000) | -- | v2.2/v2.3 | PASS | add estimand-scope sentence (below) |
| C20 | Alpha rule: probe error ceil to 0.05 + 0.05 margin; alpha .15/.15/.20/.15 | committed configs: floors .0779/.0844/.1465/.0543 -> .15/.15/.20/.15 | configs/committed_v2_*_ts0.json | probe_commit.py | v2 | PASS | none |

## Contradictions Found

**Section-5.3 mandatory check -- RESOLVED as Outcome 2.** Authoritative source:
`results_committed/pool_risk_gate.csv` (estimand: exact full-pool risk at the
per-resplit marginally selected threshold; 100 unique resplits per cell;
abstention = fallback, counted separately, zero on all cells).

- Cells passing the precommitted validity gate (Wilson UB <= 0.10): **35/35**
- Cells with exactly 0/100 violations: **34/35**
- Maximum empirical violation frequency: **0.010** (mnist/greedy_entropy/ts1)
- Maximum Wilson upper bound: **0.0545**
- Estimand: exact pool risk > alpha at the selected threshold (per resplit)

The manuscript's "0/100 in each of 35 cells" (abstract, contribution bullet
3, results paragraph incl. "in every cell ... 0 of 100 ... UB 0.037") is a
generalization from the four primary cells (which ARE 0/100) to all 35.
It must be corrected everywhere; the corrected statement is stronger-because-
honest: all cells pass the gate, worst cell 1/100.

**Second contradiction (C8): Adult argmin location.** The manuscript's
lambda = 0.899 is the LOCAL pilot's argmin; the canonical argmin is the
plateau {0.8687, 0.8788, 0.8889}. This violated the environment rule ("no
local number enters a paper table/figure/text"). The qualitative point
(interior minimum slightly below the endpoint, 0.3090 < 0.3092) is canonical
and survives.

No other cross-artifact conflicts were found; the v2.2 test-half tables are
correctly quarantined as diagnostics and are not cited by the manuscript.

## Audited-Family Definition

**PASS WITH WORDING CHANGE.** Code (family_wide_feasibility.py) audits
exactly A = {tau_lambda : lambda in Lambda(100)} UNION {forced prefix depths
t = 0..T}: constant-threshold stopping rules over the frozen readiness score
and frozen nested acquisition order, plus every forced prefix depth; full
acquisition = t = T (and lambda = 1 behaves as full acquisition up to
measured softmax saturation, PHASE5_PROVENANCE.md q6). No depth-dependent
threshold schedules, no history-dependent policies, no alternative
predictors/policies are included -- matching the manuscript's Problem Setup
and Eq. (11). Family sizes: M = 100 + (T+1) = 150 (mnist), 151 (MiniBooNE),
115 (adult), 158 (spambase).

Recommended wording everywhere a strong phrase appears: "within the audited
constant-threshold and forced-prefix family" (or "within the audited family
A" after Eq. 11). The abstract's "unattainable anywhere in the deployed
operating family" is acceptable ONLY because the family is later defined;
prefer inserting "audited" ("the deployed, audited operating family"). The
Discussion's family-relative paragraph is exemplary and PASSES as written.

## Claim-Language Revisions

See Main-Paper Changes Required for the exact replacement table. Summary of
language rules confirmed: never "all deployable policies"; feasible branch is
"empirically feasible" (the Method section already says this; the
Introduction's three-outcome list drops "empirically" and must add it);
refusal is "certification refusal with full-acquisition fallback".

## Deployment and Fallback Semantics

**PASS.** Code: `ltt_select`/`iut_select` return `lambda_idx = None`; the
eval sweep records `abstained` and evaluates the FULL-ACQUISITION fallback;
the system always outputs a prediction; no abstention/human-review/secondary
model is implemented. The manuscript already states exactly this (Theorem 2:
"refuses certification and falls back to full acquisition while still
producing a prediction; no stratum-wise risk guarantee is claimed for that
fallback") -- and the audit sometimes certifies that even full acquisition
exceeds alpha (the three family-failure datasets), which the paper reports.
Optional strengthening sentence for the Discussion: "Full acquisition
maximizes the evidence available to the frozen predictor; it is not a safety
guarantee. Any subsequent abstention, human review, or routing to another
model is application-specific." Recommend describing the fallback as the
experimental protocol, not a deployment recommendation (one clause).

## Stratum Precommitment and Selection Validity

**PASS.** Data flow (verified in code + PHASE5_PROVENANCE.md):
1. train backbone on the fixed train split (train_seed only);
2. freeze predictor/policy/score;
3. heldout pool fixed; 4. probe = 10% of heldout (seed 777, independent);
5. alpha committed from the probe full-acquisition floor (fixed rule);
6. lambda_ref sweep {0.5, 0.7, 0.9} committed in tooling before results
   (git evidence in phase5_provenance.json; 0.9 = fine-resolution primary);
7. G = 5 committed; 8. bin edges committed from PROBE reference depths;
9. audited stratum = DEEPEST precommitted nonempty bucket -- nonemptiness is
   determined from EVAL COVARIATES only (reference depths; label-free);
   canonically it COINCIDES with the argmax-risk stratum on 4/4 primary
   cells, so the frozen Table-1 rows double as confirmatory tests;
10. 100 unique cal/test resplits (independent seeded permutations);
11. CAFA-IUT selection on cal; 12. family audit on the full pool;
13. full-pool evaluation.

Answers to the mandated questions: alpha <- probe; lambda_ref <- committed
tooling (pre-results); edges <- probe; nonemptiness <- eval covariates
(label-free); evaluation LABELS are never used to choose the confirmatory
stratum; calibration labels never touch edges; strata are defined on probe
statistics and audited on the eval pool (disjoint from probe; the audit
examples are used once); conditioning on the covariate-defined stratum
preserves the binomial model with n_k treated as fixed after conditioning;
the primary test is a single predeclared stratum per (dataset, lambda_ref)
-- no min-p search across strata; multiplicity across lambda_refs is handled
by publishing all three (105 configurations) with 0.9 declared primary.
Recommended supplement addition: Holm-adjusted endpoint p-values across all
strata as a sensitivity (currently absent; non-blocking because the primary
test is predeclared).

## Detectability Theorem Audit

**PASS WITH WORDING CHANGE (Option A with explicit family size), supplement
proof REQUIRED.**

- Inferential target: for stratum k with mass q_k, sample n (calibration/
  audit examples), family A of size M = |Lambda| + (T+1), min family margin
  Delta_k = min_{a in A} (R_{k,a} - alpha) > 0, audit level gamma, miss
  probability eta. Confirmed: Delta_k in Eq. (14) is the MIN over the family
  -- matches family_wide_summary.csv (gap_min_minus_alpha).
- Fixed vs random n_k: the audit conditions on n_k (exact binomial given
  n_k); unconditionally n_k ~ Binomial(n, q_k). The proof MUST include the
  n_k >= c * n q_k concentration step (or state the conditional version);
  the manuscript's "contributes approximately n q_k examples" is fine
  narratively but the supplement must not silently replace n_k by n q_k.
- Family size: the family-failure certificate requires EVERY component null
  rejected (p_fam = max over M components), so the miss event is a UNION
  over M component failures. A rigorous sufficient bound via per-component
  Hoeffding + union bound over misses is
  n q_k Delta_k^2 >= C * (log(1/gamma) + log(M/eta)),
  i.e., the manuscript's log(1/eta) must become log(M/eta) (components share
  data, so the union bound is valid and conservative; ordering/nesting does
  not remove M in general because the risk curves are non-monotone --
  measured: threshold_curve_monotone is False on 3 of 4 primary cells).
  For the audited families log M in [4.7, 5.1], an additive constant per
  experiment -- which is why the up-to-constants scaling LOOKS M-free -- but
  the theorem statement should carry M explicitly.
- Simulation: the main grid is COMPONENT-LEVEL (M = 1), so panel (b)
  validates the component audit, not M-independence; the separate family-size
  calibration (M in {10, 50, 100}, synthetic_power.csv family rows) shows the
  max-p family test behaving as expected. Power curves organized by
  n q Delta^2 are therefore honest for the component curve; the caption/
  supplement must disclose the M = 1 design (one clause).
- The bound is sufficient/conservative (Hoeffding-style), not necessary; the
  manuscript already says "up to constants" and "sufficient" -- keep that.

Replacement text: see Main-Paper Changes Required (rows T1-T3). Supplement
must contain the full proposition + proof (assumptions: frozen system,
committed family, i.i.d. within stratum; exact binomial per component; union
bound over misses; Binomial(n, q_k) lower-tail step).

## Simulation Audit

**PASS.** `scripts/synthetic_power.py`: Bernoulli DGP; homogeneous risk
alpha + Delta per grid point (single component; family study separate with
independent components); grids q {0.02,...,0.40} x Delta {0.01,...,0.15} +
nulls {0, -0.02} x n {500,...,50000}; B = 5000; seed 20260712; detection =
one-sided exact Clopper-Pearson lower bound > alpha at gamma = 0.05 (exact
binomial inversion, no approximation); rejection and max-null-FPR
computations verified in code; max null FPR = 0.0500 (summary json).
Binned median/IQR in Figure 2b are computed by the (missing) figure script
from `synthetic_power.csv` -- values consistent with the CSV on inspection;
benchmark marks are retrospective diagnostics only (manuscript says so).
Unit tests cover FPR control and power sanity (tests/test_phase53.py).
No rerun needed.

## Figure 2 Audit

**Panel (a): PASS.** Source `pool_plugin_alpha_sweep.csv` (7 observed alpha
points per dataset; committed alpha an explicit measured point) + committed
stars from the same rows (`is_committed = 1`): mnist/MiniBooNE/adult 0.000,
spambase 0.450 ("45/100 at committed alpha" annotation correct). Lines
connect observed points only; no interpolation presented as data; the
delta = 0.10 dashed line is labeled "reference" (correct -- delta is the
certificate's level, not a plug-in guarantee); axis labels and legend match
the CSV. MNIST nonmonotonicity is real (three crossings in the CSV).

**Panel (b): PASS WITH DISCLOSURE.** x = n*q*Delta^2 (computable from CSV
columns nq and Delta -- verified), log scale; y = empirical rejection
probability; "max null FPR = 0.050" matches synthetic_power_summary.json
exactly; gamma line at 0.05; benchmark rug marks must be at the EXACT
recomputed signals **52.4652 (MNIST), 63.9168 (MiniBooNE), 74.5111 (Adult),
0.1282 (Spambase)** -- from n_k * (min family risk - alpha)^2; the legend
labels them "Benchmark signal n_k Delta^2" (retrospective diagnostics --
correct, and the caption says so); no theoretical vertical boundary is shown
(correct). Required disclosure (caption or supplement): the simulation grid
is component-level (M = 1); family-size behavior is covered by the separate
calibration study.

**Caption consistency: PASS** (5,000 draws; gamma = 0.05; null FPR 0.050;
variable definitions match the code) -- contingent on adding the M = 1
disclosure and keeping benchmark ticks at the exact values above.

**Reproducibility: FAIL -- the Figure-2 generation script is not in the
repository.** Required: add `scripts/make_figure2.py` reading ONLY the two
CSVs, plus a `verify_figure2_values.py` check.

## Full-Pool Evaluation Audit

**PASS WITH WORDING ADDITION.** Eq. (15) is an exact identity per fixed
threshold (algebra of complementary partitions); it is asserted numerically
per resplit in pool_stratum_eval.py (sum_k q_k R_k == R_pool). The selected
threshold depends on calibration data; the manuscript correctly uses "can
overstate" (possible/observed -- measured corr(R_cal, R_test) = -1.0000 and
the six test-half FAILs collapsing to <= 1/100 on the pool are the observed
evidence; "always overstates" would be false and is not claimed). Full-pool
risk is exact on the fixed pool and is NOT an independent estimate of
population risk -- this scope sentence is currently missing and must be
added verbatim:

> This estimand exactly evaluates the selected rule on the fixed evaluation
> pool; it is not an independent estimate of population risk, which is
> governed by the finite-sample certification guarantee.

## Cross-Dataset Multiplicity

**PASS WITH WORDING CHANGE.** The paper runs four separate per-dataset
analyses and reports "on three of four datasets" as replication -- no global
family-wise claim is made or needed. Add one sentence (Experimental Setup or
supplement): "Audit levels are controlled separately within each
precommitted dataset analysis; cross-dataset results are reported as
replications rather than as one globally family-wise test." The abstract's
"p <= 1.4e-79" is a valid per-dataset bound over the three certificates (it
is the largest of the three p-values), not a joint statement -- acceptable.

## Main-Paper Changes Required

| Location | Current wording/problem | Required replacement | Reason |
|---|---|---|---|
| Abstract | "empirically yields 0/100 full-pool violations in each of 35 precommitted experimental cells" | "satisfies its precommitted full-pool validity gate in all 35 experimental cells (34 cells with zero violations in 100 calibration draws; worst cell 1/100, Wilson upper bound 0.054)" | C10: claim is false as stated |
| Contribution bullet 3 | "marginal CAFA exceeds the target in none of 35 canonical cells" | "marginal CAFA passes the precommitted full-pool validity gate in all 35 canonical cells (worst cell: 1 of 100 selections)" | C10 |
| Results, "Marginal Certification and Cost" | "in every cell, the selected threshold exceeds alpha on the exact evaluation pool in 0 of 100 resplits (95% Wilson upper bound 0.037)" | "in 34 of 35 cells the selected threshold never exceeds alpha on the exact evaluation pool in 100 resplits; the remaining cell (MNIST, training seed 1) exceeds it once (Wilson upper bound 0.054). All 35 cells satisfy the precommitted validity gate." | C10 |
| Results, Family-Wide Feasibility | "the minimum family risk occurs at lambda = 0.899" | "the minimum family risk occurs at interior thresholds (lambda ~ 0.87-0.89)" | C8: 0.899 is a local-run number; canonical argmin plateau {0.8687, 0.8788, 0.8889} |
| Introduction, three-outcome list | "feasible, family-wide failure or unresolved" | "empirically feasible, certified family-wide failure, or unresolved" | feasible branch is observed-risk only (Method already says so) |
| Detectability subsection | "n q_k Delta_k^2 >~ log(1/gamma) + log(1/eta)" | "n q_k Delta_k^2 >~ log(1/gamma) + log(M/eta), where M is the audited family size (here M <= 158, so log M is a small additive constant)" | family-failure miss is a union over M components |
| Detectability subsection (add) | -- | "The bound conditions on the realized stratum count n_k; the unconditional statement follows from Binomial(n, q_k) concentration (supplement)." | random-count treatment |
| Finite-pool paragraph (add after "primary empirical estimand") | -- | the verbatim scope sentence from the Full-Pool Evaluation Audit above | estimand scope |
| Figure 2 caption (add one clause) | -- | "the simulation grid is component-level (family size 1); family-size behavior is reported separately (supplement)" | simulation-theorem alignment |
| Experimental Setup (add one sentence) | -- | the cross-dataset multiplicity sentence above | multiplicity scope |
| Abstract / Intro (optional tighten) | "the deployed operating family" | "the deployed, audited operating family" (first use), thereafter "the audited family" | family scope discipline |
| Discussion (optional add) | -- | "Full acquisition maximizes the evidence available to the frozen predictor; it is not a safety guarantee." | fallback semantics |

Title: no change required ("Auditing Family-Wide Feasibility in
Risk-Controlled Active Feature Acquisition" is family-scoped and accurate).
Table 1/2/3 values: no changes. Ethics/Conclusion: no numeric issues;
Conclusion language is family-relative (PASS).

## Supplement Changes Required

The supplement does not yet exist; it MUST contain (per the manuscript's own
promise on page 7): (A) provenance -- commit 4b8b557, tag canonical-v2.3,
requirements.lock, MANIFEST hashes, seed list (train {0,1,2}, probe 777,
resplit offset 1e6, policy 10000+1000*eps, simulation 20260712), artifact
manifest; (B) the exact family A per dataset with M = 150/151/115/158 and
exclusions; (C) verdict definitions (empirically feasible / certified
family-wide failure / unresolved / certification refusal with
full-acquisition fallback); (D) the 13-step precommitment protocol above,
incl. the deepest-nonempty rule, the deepest==argmax coincidence, and
leakage checks; (E) algorithms incl. fallback pseudocode; (F) proofs --
Theorems 1-3 plus the detectability proposition WITH the log(M/eta) term and
the Binomial(n, q_k) step, and the Eq.-15 selection argument (rho = -1
anti-correlation); (G) complete results -- all 35 marginal cells (INCLUDING
the corrected 34/35-plus-one-cell statement), all 105 IUT configurations,
the four family-audit rows, the exact plugin pool alpha sweep, the raw null
FPR grid, and the benchmark-signal computation (52.4652/63.9168/74.5111/
0.1282 from exact n_k, alpha, min family risk); (H) Figure-2 reproduction
(source CSVs, generation command, caption, numeric validation); (I) the
corrected 35-cell statement used consistently everywhere; (J) limitations
(family scope, no global cross-dataset test, fallback not safe, empirical
feasible branch, fixed-pool estimand scope, simulation = prospective
evidence not proof).

## Code and Reproducibility Changes Required

1. **Add `scripts/make_figure2.py`** generating both panels from
   `pool_plugin_alpha_sweep.csv` + `pool_plugin_eval.csv` +
   `synthetic_power.csv` only (currently the figure has no in-repo script:
   FAIL).
2. **Add `scripts/verify_claim_ledger.py`** (+ `claim_ledger.csv`) failing
   when any manuscript number differs from canonical artifacts; must cover
   the four family rows, costs, the corrected 35-cell statement, the
   105-config accounting, the single IUT violation, plugin committed values,
   max null FPR, and the exact benchmark signals.
3. Optional but recommended: `verify_figure2_values.py`,
   `verify_table_values.py` (thin wrappers over the same checks); the other
   mandated verifiers exist in substance (splits/stratum/family/simulation
   are covered by tests + hard asserts in the analysis scripts) and should
   be referenced in the supplement.
4. No changes to frozen code; MANIFEST verified before and after this audit.

## Reruns Performed

**NONE.** All questions were resolved from stored canonical artifacts via
deterministic read-only recomputation (CSV scans; benchmark signals
recomputed from stored n_k/alpha/min-risk columns; PDF text extraction).
Two documented consistency fixes were applied to NON-frozen working
documents (not canonical artifacts, not silent): `RESULTS_FOR_PAPER.md` and
`project_update.md` -- correcting their own "every cell 0.000" phrasing to
the 34/35-plus-one-cell statement and the Adult argmin location (see
companion edits in this commit). No canonical file was modified; all
previous tags intact.

## Final Phase 0-1 Status

```text
Audited-family definition: PASS (wording tighten recommended)
Claim language: FAIL until the two blocking rewordings land (exact text provided)
Fallback semantics: PASS
Stratum precommitment validity: PASS
Detectability theorem: PASS WITH WORDING CHANGE (Option A with explicit log(M/eta); supplement proof required)
Simulation-theorem alignment: PASS (with the M = 1 disclosure clause)
Figure 2 consistency: PASS (values) / FAIL (no in-repo generation script)
Full-pool estimand wording: PASS WITH WORDING ADDITION (scope sentence)
Canonical number consistency: PASS after C10 + C8 corrections
Supplement consistency plan: COMPLETE (specified above; document itself not yet written)
Code provenance: PASS for results; FAIL for Figure-2 script + claim verifier

Ready for Phase 2 experiments: NO

Blocking issues:
1. Replace the "0/100 in each of 35 cells" claim (abstract, contribution
   bullet 3, results paragraph) with the corrected 34/35 + 1/100 statement.
2. Correct the Adult family-minimum location from lambda = 0.899 (local
   number) to the canonical plateau lambda ~ 0.87-0.89.
3. Add the log(M/eta) family-size term (or fixed-family caveat) to the
   detectability statement in main + supplement, and commit
   scripts/make_figure2.py + the claim-ledger verifier.
```
