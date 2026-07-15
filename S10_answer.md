# S10_answer.md -- Verified source material for S10 (Robustness Analyses)

Prepared from canonical frozen artifacts only. Every value was re-extracted
this pass from the row-level artifacts in Section 1; the five embedded CSV
blocks were generated programmatically from those artifacts. One additional
verification was run for this dossier: selection invariance across cost
schemes was checked on every stored resplit (Section 6).

---

## 1. Canonical sources and freeze metadata

1. **Artifacts by robustness dimension.**
   - Reference-threshold sensitivity: `family_wide_summary.csv` (105 rows,
     all 3 lambda_refs), `iut_by_lambda_ref.csv` (+ `_resplits.csv`),
     metrics JSONs (per-lambda_ref population blocks: realized strata,
     endpoint CP bounds).
   - Backbone-seed robustness: same files, ts in {0, 1, 2} rows;
     `configs/committed_v2_<ds>_ts<seed>.json` (floors, alphas);
     `pool_stratum_eval.csv` (selected-rule stratum risks).
   - Policy robustness: same files, 4 policies; `fork_strata.csv`
     (depth concentration: populated strata, IQR, normalized entropy);
     `PHASE2_READOUT.md` + `phase2_summary.csv` (policy-quality frontier,
     Spearman aggregates -- canonical cluster regeneration).
   - Readiness-score robustness: `PHASE4_SCORE_ABLATION.md` (invariant
     checks + audit under margin), the 3 margin cells in the family/IUT
     tables.
   - Cost-scheme robustness: metrics JSONs (per-scheme blocks), the
     structural notes in `PHASE2_READOUT.md` (determinism section) and
     `run_eval_sweep.py`; the invariance check run for this dossier.
   - Quantile-binning and equal-width/min-bucket sensitivity:
     `results_committed/RESULTS.md` Section "6. Binning ablation (verdicts
     under alt edges)" (the only frozen binning-fork artifact; per-stratum
     ENDPOINT verdicts, no CSV -- parsed programmatically here), plus the
     committed alternative edge families in `configs/committed_v2_*.json`
     (`quantile: {3, 5, 8}`, `equal_width_merged: {5x25, 5x50, 5x100}`).
   - Verdict/certification/cost summaries: `family_wide_summary.csv`,
     `iut_by_lambda_ref.csv`, `pool_stratum_resplits.csv`,
     `pool_plugin_eval.csv` (full-cost normalization).
2. **Scripts.** `family_wide_feasibility.py` (audit; quantile-5 edges only),
   `iut_by_lambda_ref.py`, `phase53_lib.py` (`edges_for`, `bucket_ids`),
   `analyze_results.py::ablation_verdicts` (binning ablation; edge kinds
   quantile:3/8 + equal_width_merged:5x25/50/100), `phase2_analyze.py`
   (policy frontier), `phase4_score_ablation.py` (score invariance),
   `src/cafa/metrics.py::reference_buckets` (equal-width merge rule),
   `probe_commit.py` (edge commitment).
3. **Freeze.** Tag `canonical-v2.2`; Phase-5.3 artifacts stamped commit
   `7bdb1bf27fc3`; compendium v2.3.
4. **Status classes.** Canonical: everything in `results_committed/` +
   committed configs. Superseded: test-half violation columns (any file),
   v2.1 IUT accounting, `alpha_sweep_transitions.csv` verdicts. Local-pilot
   only (never citable): the local Phase-2 Spearman values in
   project_update Section 12 (e.g. rho(quality, entropy@0.5) = -0.757 --
   canonical is -0.746), local IUT counts (56/99). Unavailable: family-wide
   IU audits (minima, p-values) under the ALTERNATIVE binnings -- only
   endpoint verdicts are frozen (Sections 7-8, 15).
5. **Robustness configurations contributing to S10:** 105 family/IUT
   configurations (35 cells x 3 lambda_refs) + 60 binning-ablation rows for
   the primary policy cells (4 datasets x 3 lambda_refs x 5 alternative
   edge schemes; 480 rows exist across all softmax cells) + 6 score rows +
   the per-scheme cost blocks (23,400 selection checks).

---

## 2. Reference-threshold sensitivity (primary cells; 12 rows)

`family_min` and `family_p` are the combined indexed family (min/max over
threshold + depth branches); `endpoint_lcb95` is the stored one-sided 95%
Clopper-Pearson LCB of the deepest-stratum endpoint risk for that
lambda_ref; `marginal_cost_over_full` is the pool-based marginal CAFA cost
(lambda_ref-independent by construction -- the marginal selector never sees
strata); IUT cost is end-to-end deployed (fallback included).

```csv
dataset,lambda_ref,floor,alpha,G0,G_realized,k_star,n_k,q_k,family_min,endpoint_risk,endpoint_lcb95,family_p,verdict,iut_certified,iut_refused,iut_cost_over_full,marginal_cost_over_full,iut_premium_vs_marginal,primary
mnist,0.5,0.077857,0.15,5,5,4,6440,0.255556,0.11614906832298137,0.11630434782608695,0.109785,0.9999999999999984,feasible,100,0,0.626482,0.507247,1.235061,0
mnist,0.7,0.077857,0.15,5,5,4,5376,0.213333,0.1449032738095238,0.1449032738095238,0.137057,0.8568577366473663,feasible,8,92,0.972424,0.507247,1.917061,0
mnist,0.9,0.077857,0.15,5,5,4,5479,0.217421,0.24785544807446613,0.24785544807446613,0.23827,1.36921550028183e-79,family-wide failure certified,0,100,1.0,0.507247,1.971424,1
tabular-adult,0.5,0.14649,0.2,5,1,1,16280,1.0,0.1507985257985258,0.1507985257985258,0.146201,1.0,feasible,100,0,0.361215,0.361215,1.0,0
tabular-adult,0.7,0.14649,0.2,5,1,1,16280,1.0,0.1507985257985258,0.1507985257985258,0.146201,1.0,feasible,100,0,0.361215,0.361215,1.0,0
tabular-adult,0.9,0.14649,0.2,5,3,3,6268,0.385012,0.3090299936183791,0.309189534141672,0.299575,8.733138398189605e-93,family-wide failure certified,0,100,1.0,0.361215,2.768431,1
tabular-MiniBooNE,0.5,0.084374,0.15,5,1,1,46823,1.0,0.08339918416162997,0.08339918416162997,0.081306,1.0,feasible,100,0,0.04995,0.04995,1.0,0
tabular-MiniBooNE,0.7,0.084374,0.15,5,1,1,46823,1.0,0.08339918416162997,0.08339918416162997,0.081306,1.0,feasible,100,0,0.04995,0.04995,1.0,0
tabular-MiniBooNE,0.9,0.084374,0.15,5,5,4,9180,0.196057,0.23344226579520697,0.23344226579520697,0.226189,3.178314386914752e-98,family-wide failure certified,0,100,1.0,0.04995,20.020129,1
tabular-spambase,0.5,0.054348,0.15,5,1,1,1656,1.0,0.059178743961352656,0.06099033816425121,0.051599,1.0,feasible,100,0,0.091674,0.091674,1.0,0
tabular-spambase,0.7,0.054348,0.15,5,4,4,344,0.207729,0.11627906976744186,0.11627906976744186,0.088948,0.9695492825562712,feasible,20,80,0.900832,0.091674,9.826478,0
tabular-spambase,0.9,0.054348,0.15,5,5,4,249,0.150362,0.17269076305220885,0.17269076305220885,0.134359,0.17935656493362384,unresolved,0,100,1.0,0.091674,10.908225,1
```

Aggregate statements (exact):

1. **First certified family-wide failure:** lambda_ref = 0.9 for MNIST,
   Adult, and MiniBooNE (primary cells; nothing certified at 0.5/0.7);
   never for Spambase (unresolved at 0.9).
2. **CAFA-IUT first refusals:** MNIST at 0.7 (92/100 refused; 100/100 at
   0.9); Spambase at 0.7 (80/100; 100/100 at 0.9); Adult and MiniBooNE
   only at 0.9 (0 -> 0 -> 100 refusals).
3. **Verdict monotone in lambda_ref:** yes on the tested grid -- every
   primary dataset moves one-way (feasible -> feasible -> failure/
   unresolved); no reversals.
4. **Realized strata monotone non-decreasing:** yes -- 5/5/5 (MNIST),
   1/1/3 (Adult), 1/1/5 (MiniBooNE), 1/4/5 (Spambase).
5. **Confirmatory-stratum mass monotone decreasing:** NO, not strictly --
   Adult/MiniBooNE/Spambase decrease (1.0 -> ... -> 0.385/0.196/0.150) but
   MNIST up-ticks from 0.2133 (0.7) to 0.2174 (0.9). Say "generally
   decreasing", not "monotone".
6. **Primary 0.9 conclusion qualitatively stable:** the failure is a
   deep-stratification phenomenon -- at 0.5/0.7 the audit is feasible or
   the stratification is trivial (G = 1 on all tabular cells at 0.5); at
   0.9 the deep stratum resolves and the three failures certify. The 0.9
   verdicts themselves are stable across seeds/policies/scores (Sections
   3-5); the DEPTH at which failure first certifies varies (see 8 and
   Section 3).
7. **Certify at 0.5 and 0.7 but refuse at 0.9 (IUT, primary):** Adult
   (100/100 -> 100/100 -> 0/100) and MiniBooNE (same); MNIST and Spambase
   already mostly refuse at 0.7 (8/100 and 20/100 certified).
8. **Unresolved because the stratum is small:** all unresolved cases are
   Spambase at lambda_ref 0.9 (primary n_k = 249; across policies/seeds
   n_k = 203-400; the 5 unresolved configurations in the 105-grid are all
   Spambase @0.9).

**Expected headline pattern: VERIFIED** -- Adult/MiniBooNE fully certify at
0.5/0.7 and refuse at 0.9; MNIST certifies at 0.5, mostly refuses at 0.7
(8/100), fully refuses at 0.9; Spambase certifies at 0.5, mostly refuses at
0.7 (20/100), fully refuses at 0.9; family-wide failure certifies only
where stratification resolves the deep bucket. No "not detected" case is
reported as "feasible": the three-way verdict is preserved in every row.

---

## 3. Backbone-seed robustness (greedy @0.9; 12 rows)

`marginal_selected_rule_risk_kstar` = deepest-stratum pool risk of the
marginal selected rule, mean over 100 resplits (S8 Section 6 semantics).

```csv
dataset,seed,floor,alpha,G_realized,k_star,n_k,q_k,family_min,endpoint_risk,endpoint_lcb95,family_p,verdict,marginal_selected_rule_risk_kstar,marginal_cost_over_full,iut_certified,iut_refused,iut_cost_over_full
mnist,0,0.077857,0.15,5,4,5479,0.217421,0.24785544807446613,0.24785544807446613,0.23827,1.36921550028183e-79,family-wide failure certified,0.300573,0.507247,0,100,1.0
mnist,1,0.101071,0.2,5,4,7798,0.309444,0.26570915619389585,0.26570915619389585,0.257483,1.0328930164305264e-44,family-wide failure certified,0.328536,0.528657,0,100,1.0
mnist,2,0.094286,0.15,5,4,5193,0.206071,0.268053148469093,0.268053148469093,0.257945,1.785787832286744e-106,family-wide failure certified,0.268053,0.73863,0,100,1.0
tabular-adult,0,0.14649,0.2,3,3,6268,0.385012,0.3090299936183791,0.309189534141672,0.299575,8.733138398189605e-93,family-wide failure certified,0.312699,0.361215,0,100,1.0
tabular-adult,1,0.161415,0.25,4,4,6023,0.369963,0.31545741324921134,0.31545741324921134,0.305593,1.6561067462188007e-30,family-wide failure certified,0.322431,0.309764,0,100,1.0
tabular-adult,2,0.145384,0.2,4,3,5462,0.335504,0.3017209813255218,0.3017209813255218,0.291494,2.5750993344329564e-71,family-wide failure certified,0.361406,0.209375,0,100,1.0
tabular-MiniBooNE,0,0.084374,0.15,5,4,9180,0.196057,0.23344226579520697,0.23344226579520697,0.226189,3.178314386914752e-98,family-wide failure certified,0.355447,0.04995,0,100,1.0
tabular-MiniBooNE,1,0.088603,0.15,5,4,9387,0.200478,0.2226483434537126,0.2226483434537126,0.215596,1.1223982692930185e-77,family-wide failure certified,0.419729,0.034095,0,100,1.0
tabular-MiniBooNE,2,0.093792,0.15,5,4,9486,0.202593,0.24678473539953616,0.24899852414083914,0.2417,1.7250016239596908e-133,family-wide failure certified,0.393527,0.054852,0,100,1.0
tabular-spambase,0,0.054348,0.15,5,4,249,0.150362,0.17269076305220885,0.17269076305220885,0.134359,0.17935656493362384,unresolved,0.3851,0.091674,0,100,1.0
tabular-spambase,1,0.070652,0.15,5,4,400,0.241546,0.165,0.17,0.139751,0.21862042034183843,unresolved,0.33255,0.173674,1,99,0.993496
tabular-spambase,2,0.065217,0.15,5,4,311,0.187802,0.15755627009646303,0.15755627009646303,0.124513,0.37804484811612166,unresolved,0.37418,0.170693,0,100,1.0
```

- **Expected stability: VERIFIED.** MNIST / Adult / MiniBooNE: certified
  family-wide failure at all 3 seeds; Spambase: unresolved at all 3 seeds
  (p = 0.179 / 0.219 / 0.378).
- **k\* labels:** MNIST 4/4/4; Adult **3/4/3** (seed 1 realizes buckets up
  to label 4); MiniBooNE 4/4/4; Spambase 4/4/4.
- **Alpha step crossings: VERIFIED** -- MNIST seed 1 floor 0.101071 ->
  alpha 0.20; Adult seed 1 floor 0.161415 -> alpha 0.25 (all other cells
  keep 0.15/0.20).
- **Verdict changes with seed: none** (at lambda_ref 0.9).
- **First-detecting lambda_ref changes with seed: YES on MNIST** -- ts2
  certifies family-wide failure already at 0.7 (ts0/ts1 first certify at
  0.9); Adult/MiniBooNE/Spambase frontiers are seed-stable (0.9 / 0.9 /
  never).
- **Cost/full varies materially across seeds:** MNIST 0.507 / 0.529 /
  0.739; Adult 0.361 / 0.310 / 0.209; MiniBooNE 0.050 / 0.034 / 0.055;
  Spambase 0.092 / 0.174 / 0.171 (up to ~1.9x within a dataset; alpha and
  backbone change together, so this is expected and must not be read as a
  pure seed effect).

---

## 4. Policy robustness (@0.9, softmax; 32 rows)

Scope: all four datasets; greedy/random at seeds 0-2, eps-greedy (0.25,
0.5) at seed 0 only (the committed design -- all four policies exist for
every dataset, eps only at ts0); max-softmax; lambda_ref 0.9 shown;
primary cost scheme. `first_detect_lr` = smallest lambda_ref whose
family-wide threshold verdict is "failure certified" for that cell (the
Phase-5.3 family audit; the Phase-2 "frontier" column is the older
endpoint-based flag). `depth_norm_entropy_0.9` from fork_strata.csv.

```csv
dataset,policy,eps,seed,alpha,G_realized,k_star,n_k,family_min,endpoint_risk,family_p,verdict,first_detect_lr,iut_cert_refuse,marginal_cost_over_full,iut_cost_over_full,depth_norm_entropy_0.9
mnist,greedy_entropy,,0,0.15,5,4,5479,0.24785544807446613,0.24785544807446613,1.36921550028183e-79,family-wide failure certified,0.9,0/100,0.507247,1.0,0.901228
mnist,greedy_entropy,,1,0.2,5,4,7798,0.26570915619389585,0.26570915619389585,1.0328930164305264e-44,family-wide failure certified,0.9,0/100,0.528657,1.0,0.901228
mnist,greedy_entropy,,2,0.15,5,4,5193,0.268053148469093,0.268053148469093,1.785787832286744e-106,family-wide failure certified,0.7,0/100,0.73863,1.0,0.901228
mnist,random,,0,0.15,5,4,7074,0.2544529262086514,0.2544529262086514,3.509508216929623e-115,family-wide failure certified,0.7,0/100,0.528678,1.0,0.837438
mnist,random,,1,0.2,5,4,9352,0.2650769888793841,0.2650769888793841,2.8408643411137154e-52,family-wide failure certified,0.7,0/100,0.557078,1.0,0.837438
mnist,random,,2,0.15,5,4,7301,0.27489385015751266,0.27489385015751266,4.783899454955771e-165,family-wide failure certified,0.5,0/100,0.612355,1.0,0.837438
mnist,eps_greedy_eps0.25,0.25,0,0.15,5,4,5695,0.25320456540825287,0.25320456540825287,4.1010577267893574e-91,family-wide failure certified,0.7,0/100,0.454986,1.0,0.886447
mnist,eps_greedy_eps0.5,0.5,0,0.15,5,4,6011,0.26335052403926135,0.26335052403926135,4.416502717776924e-114,family-wide failure certified,0.7,0/100,0.441352,1.0,0.866682
tabular-adult,greedy_entropy,,0,0.2,3,3,6268,0.3090299936183791,0.309189534141672,8.733138398189605e-93,family-wide failure certified,0.9,0/100,0.361215,1.0,0.744701
tabular-adult,greedy_entropy,,1,0.25,4,4,6023,0.31545741324921134,0.31545741324921134,1.6561067462188007e-30,family-wide failure certified,0.9,0/100,0.309764,1.0,0.744701
tabular-adult,greedy_entropy,,2,0.2,4,3,5462,0.3017209813255218,0.3017209813255218,2.5750993344329564e-71,family-wide failure certified,0.9,0/100,0.209375,1.0,0.744701
tabular-adult,random,,0,0.2,5,4,6044,0.3084050297816016,0.3084050297816016,1.3648917067129054e-88,family-wide failure certified,0.9,0/100,0.277283,1.0,0.783264
tabular-adult,random,,1,0.25,5,4,5954,0.31373866308364123,0.3139066174000672,9.508063491612882e-29,family-wide failure certified,0.9,0/100,0.200542,1.0,0.783264
tabular-adult,random,,2,0.2,5,4,6100,0.30655737704918035,0.30655737704918035,1.4151052357275279e-86,family-wide failure certified,0.9,0/100,0.230907,1.0,0.783264
tabular-adult,eps_greedy_eps0.25,0.25,0,0.2,3,3,6261,0.30825746685832933,0.3084171857530746,1.8310261821850253e-91,family-wide failure certified,0.9,0/100,0.340295,1.0,0.53491
tabular-adult,eps_greedy_eps0.5,0.5,0,0.2,4,4,6207,0.3082004188819075,0.3082004188819075,1.3254252359915536e-90,family-wide failure certified,0.9,0/100,0.321424,1.0,0.626384
tabular-MiniBooNE,greedy_entropy,,0,0.15,5,4,9180,0.23344226579520697,0.23344226579520697,3.178314386914752e-98,family-wide failure certified,0.9,0/100,0.04995,1.0,0.685888
tabular-MiniBooNE,greedy_entropy,,1,0.15,5,4,9387,0.2226483434537126,0.2226483434537126,1.1223982692930185e-77,family-wide failure certified,0.9,0/100,0.034095,1.0,0.685888
tabular-MiniBooNE,greedy_entropy,,2,0.15,5,4,9486,0.24678473539953616,0.24899852414083914,1.7250016239596908e-133,family-wide failure certified,0.9,0/100,0.054852,1.0,0.685888
tabular-MiniBooNE,random,,0,0.15,5,4,9425,0.22514588859416446,0.22514588859416446,5.106516850259887e-83,family-wide failure certified,0.9,0/100,0.165736,1.0,0.835909
tabular-MiniBooNE,random,,1,0.15,5,4,9161,0.2474620674598843,0.2474620674598843,1.149609957686184e-130,family-wide failure certified,0.9,0/100,0.162507,1.0,0.835909
tabular-MiniBooNE,random,,2,0.15,5,4,9432,0.23536895674300254,0.23558100084817643,3.2251513504454566e-105,family-wide failure certified,0.9,0/100,0.176598,1.0,0.835909
tabular-MiniBooNE,eps_greedy_eps0.25,0.25,0,0.15,5,4,9425,0.23214854111405836,0.2323607427055703,6.506685968034752e-98,family-wide failure certified,0.9,0/100,0.061618,1.0,0.750388
tabular-MiniBooNE,eps_greedy_eps0.5,0.5,0,0.15,5,4,9132,0.23313622426631625,0.23324572930354795,4.6454564250086713e-97,family-wide failure certified,0.9,0/100,0.087754,1.0,0.789242
tabular-spambase,greedy_entropy,,0,0.15,5,4,249,0.17269076305220885,0.17269076305220885,0.17935656493362384,unresolved,not detected,0/100,0.091674,1.0,0.800592
tabular-spambase,greedy_entropy,,1,0.15,5,4,400,0.165,0.17,0.21862042034183843,unresolved,not detected,1/99,0.173674,0.993496,0.800592
tabular-spambase,greedy_entropy,,2,0.15,5,4,311,0.15755627009646303,0.15755627009646303,0.37804484811612166,unresolved,not detected,0/100,0.170693,1.0,0.800592
tabular-spambase,random,,0,0.15,5,4,353,0.1388101983002833,0.1388101983002833,0.7432690124318755,feasible,not detected,2/98,0.208102,0.989173,0.921199
tabular-spambase,random,,1,0.15,5,4,307,0.19218241042345277,0.19543973941368079,0.026096612619321703,family-wide failure certified,0.9,0/100,0.202913,1.0,0.921199
tabular-spambase,random,,2,0.15,5,4,279,0.17204301075268819,0.17921146953405018,0.1711199656813039,unresolved,not detected,0/100,0.21011,1.0,0.921199
tabular-spambase,eps_greedy_eps0.25,0.25,0,0.15,5,4,306,0.17973856209150327,0.19281045751633988,0.0865886782865218,family-wide failure certified,0.9,0/100,0.109542,1.0,0.852654
tabular-spambase,eps_greedy_eps0.5,0.5,0,0.15,5,4,346,0.15895953757225434,0.17630057803468208,0.3422911891403479,unresolved,not detected,0/100,0.119417,1.0,0.875076
```

Checks:

1. **Verdict vs policy @0.9:** unchanged on MNIST, Adult, MiniBooNE (all
   four policies: failure certified). **NOT unchanged on Spambase:**
   greedy ts0 unresolved, random ts0 **feasible** (empirical min 0.1388 <
   alpha), eps0.25 **failure certified** (p = 0.026), eps0.5 unresolved --
   the small (n_k ~ 250-353) near-threshold stratum flips the three-way
   verdict with the policy.
2. **Detection frontier within a dataset:** Adult and MiniBooNE flat (0.9
   for every policy/seed); MNIST varies -- greedy ts0/ts1 detect first at
   0.9, but eps0.25/eps0.5/random-ts0/ts1 at 0.7 and random ts2 at 0.5;
   Spambase mixed (eps0.25 and random ts1 at 0.9, others never).
3. **Aggregate correlation vs between-dataset differences:** the canonical
   aggregate Spearman rho(quality_auc, min-lambda_ref-detected) = 0.576
   (p = 0.0196, n = 16, 'not detected' coded 1.0) pools datasets; the
   per-dataset picture is MIXED ("Outcome 2 -- monotone on 1 of 4
   datasets"; per-dataset rho = -0.258 on MNIST and -0.775 on Spambase,
   i.e. the OPPOSITE sign). The aggregate is materially shaped by
   between-dataset composition and the 'not detected' coding;
   PHASE2_READOUT itself carries a power caveat. Do not quote the
   aggregate without this.
4. **"Stronger policy systematically hides failure": NOT supported as a
   systematic claim.** Evidence both ways: on MNIST the strongest policy
   (greedy) detects latest (0.9 vs 0.7/0.5 for weaker policies) --
   consistent with concentration -- but the per-dataset Spearman signs
   flip, Adult/MiniBooNE are flat, and Spambase is nonmonotone.
5. **Supported statement (corrected from the expected sentence):** "The
   certified-failure verdict at lambda_ref = 0.9 is stable across all four
   policies on the three resolved datasets; on Spambase, where the
   confirmatory stratum is small, the three-way outcome varies with policy
   (feasible / unresolved / failure). The detection frontier is flat on
   Adult and MiniBooNE and non-flat (weaker policies detect earlier) on
   MNIST; no claim is made that better policies systematically hide
   failure." The expected sentence's "verdict stable within datasets" must
   be scoped to the three resolved datasets.

---

## 5. Readiness-score robustness (@0.9, greedy ts0; 6 rows)

**Spambase margin was NOT run: confirmed** -- rollout cell 16
(spambase/greedy/margin) is marked "[optional]" in `run_pool_rollout.py`
and has no canonical metrics file; no Spambase score-robustness claim can
be made.

```csv
dataset,score,alpha,G_realized,k_star,n_k,family_min,endpoint_risk,endpoint_lcb95,family_p,verdict,marginal_selected_rule_risk_kstar,marginal_cost_over_full
mnist,softmax,0.15,5,4,5479,0.24785544807446613,0.24785544807446613,0.23827,1.36921550028183e-79,family-wide failure certified,0.300573,0.507247
mnist,margin,0.15,5,4,8300,0.2010843373493976,0.2010843373493976,0.193866,4.090423477224783e-36,family-wide failure certified,0.283161,0.508877
tabular-adult,softmax,0.2,3,3,6268,0.3090299936183791,0.309189534141672,0.299575,8.733138398189605e-93,family-wide failure certified,0.312699,0.361215
tabular-adult,margin,0.2,4,3,8026,0.2775978071268378,0.2775978071268378,0.269374,1.353967685314748e-62,family-wide failure certified,0.286195,0.355121
tabular-MiniBooNE,softmax,0.15,5,4,9180,0.23344226579520697,0.23344226579520697,0.226189,3.178314386914752e-98,family-wide failure certified,0.355447,0.04995
tabular-MiniBooNE,margin,0.15,5,4,12279,0.2382115807476179,0.2382115807476179,0.231894,6.9784677229539e-145,family-wide failure certified,0.35353,0.04995
```

- **Verdict unchanged on all 3 tested datasets: VERIFIED** (failure
  certified under both scores; margin p-values 4.09e-36 / 1.35e-62 /
  6.98e-145).
- **Order/correct byte-identical: VERIFIED** (PHASE4_SCORE_ABLATION
  invariant checks: order byte-identical = True, correct byte-identical =
  True, scores differ = True, alpha unchanged = True, for all three
  datasets -- ALL PASS). Only readiness scores and stopping depths change.
- **Each score uses its own probe-committed strata: VERIFIED** (committed
  edge key `greedy_entropy@margin`; k\* stays 4/3/4 but n_k changes:
  5479 -> 8300 (MNIST), 6268 -> 8026 (Adult), 9180 -> 12279 (MiniBooNE)).

---

## 6. Cost-scheme robustness

**Availability:** MNIST has ONLY `uniform` (single-scheme cell); the three
tabular datasets have `uniform`, `inverse_info` (primary), and `random`
(random integer costs). "Random costs" therefore exist for tabular cells
only.

**Structural claim: VERIFIED, with a new empirical check.** (i) Policies
are cost-blind: the rollout never consults feature costs; per-scheme costs
are recomputed post hoc from the cached acquisition `order`
(`cum_cost_from_order`; PHASE2_READOUT determinism note) -- trajectories,
losses, risk curves, and audit verdicts are therefore cost-scheme-invariant
by construction (the family audit consumes losses only). (ii) Selection is
scheme-invariant under fixed_sequence: the certified set depends only on
losses, and every scheme's cumulative cost is monotone in the grid index,
so the cost-argmin is the same smallest certified index. (iii) **Empirical
verification run for this dossier: across all multi-scheme cells, all 3
lambda_refs, all 100 resplits, and all three selectors (marginal CAFA,
CAFA-IUT, plug-in), the stored per-scheme `lambda_idx` values are
identical -- 23,400 method-resplit checks, 0 mismatches.** Only the
reported acquisition cost changes with the scheme. No exception exists in
the canonical artifacts.

Per-scheme numeric display: per-scheme realized costs are stored (metrics,
test-half convention) for every cell; pool costs are frozen for the primary
scheme only. Given the exact invariance, S10 needs no per-scheme risk table
-- one sentence plus the check above suffices (author decision, Section 15).

---

## 7-8. Binning sensitivity (quantile G0 in {3, 5, 8}; equal-width 5 bins merged at m_min in {25, 50, 100})

**What is canonical:** the committed ALTERNATIVE edge families exist for
every cell (probe-committed, seed 777, never refit): `quantile: 3/5/8`
(duplicate quantile cuts collapse -- e.g. Adult's quantile-8 edges collapse
to G = 2 realized strata) and `equal_width_merged: 5x25/5x50/5x100`
(5 equal-width bins on [0, T]; any bucket below m_min is merged into the
neighbour toward the smaller-count side, repeated until every bucket meets
the floor -- `reference_buckets` docstring). The frozen RESULT under these
alternative binnings is the Phase-1 analyzer's **binning ablation**
(RESULTS.md Section 6): per-stratum three-way ENDPOINT verdicts
(full-acquisition risk, one-sided 95% CP bounds, full eval pool) --
deterministic audits, no resplits (the Mondrian rates in that section used
25 resplit seeds; the verdicts are pool-level). **The family-wide IU audit
(family minima, family p-values) and the IUT certification counts were NOT
run under alternative binnings** -- those columns are NOT FOUND (Section
15). n_k and q_k under alternative binnings are also not stored (only the
realized G and verdict strings).

Parsed greedy-ts0 rows (60 = 4 datasets x 3 lambda_refs x 5 schemes;
section headers in RESULTS.md omit the seed -- rows were assigned by the
generator's sorted iteration order, a report defect flagged in Section 15):

```csv
dataset,lambda_ref,edge_scheme,G_realized,deepest_label,deepest_verdict,n_infeasible,all_verdicts
mnist,0.5,quantile:3,3,2,feasible,0,"0:feasible, 1:feasible, 2:feasible"
mnist,0.5,quantile:8,8,7,feasible,0,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:feasible, 5:feasible, 6:feasible, 7:feasible"
mnist,0.5,equal_width_merged:5x25,3,2,infeasible,1,"0:feasible, 1:feasible, 2:infeasible"
mnist,0.5,equal_width_merged:5x50,3,2,infeasible,1,"0:feasible, 1:feasible, 2:infeasible"
mnist,0.5,equal_width_merged:5x100,2,1,feasible,0,"0:feasible, 1:feasible"
mnist,0.7,quantile:3,3,2,feasible,0,"0:feasible, 1:feasible, 2:feasible"
mnist,0.7,quantile:8,8,7,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:feasible, 5:feasible, 6:feasible, 7:infeasible"
mnist,0.7,equal_width_merged:5x25,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
mnist,0.7,equal_width_merged:5x50,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
mnist,0.7,equal_width_merged:5x100,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
mnist,0.9,quantile:3,3,2,infeasible,1,"0:feasible, 1:feasible, 2:infeasible"
mnist,0.9,quantile:8,8,7,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:feasible, 5:feasible, 6:feasible, 7:infeasible"
mnist,0.9,equal_width_merged:5x25,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
mnist,0.9,equal_width_merged:5x50,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
mnist,0.9,equal_width_merged:5x100,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
tabular-MiniBooNE,0.5,quantile:3,1,1,feasible,0,1:feasible
tabular-MiniBooNE,0.5,quantile:8,1,1,feasible,0,1:feasible
tabular-MiniBooNE,0.5,equal_width_merged:5x25,1,0,feasible,0,0:feasible
tabular-MiniBooNE,0.5,equal_width_merged:5x50,1,0,feasible,0,0:feasible
tabular-MiniBooNE,0.5,equal_width_merged:5x100,1,0,feasible,0,0:feasible
tabular-MiniBooNE,0.7,quantile:3,1,1,feasible,0,1:feasible
tabular-MiniBooNE,0.7,quantile:8,1,1,feasible,0,1:feasible
tabular-MiniBooNE,0.7,equal_width_merged:5x25,1,0,feasible,0,0:feasible
tabular-MiniBooNE,0.7,equal_width_merged:5x50,1,0,feasible,0,0:feasible
tabular-MiniBooNE,0.7,equal_width_merged:5x100,1,0,feasible,0,0:feasible
tabular-MiniBooNE,0.9,quantile:3,3,2,infeasible,1,"0:feasible, 1:feasible, 2:infeasible"
tabular-MiniBooNE,0.9,quantile:8,8,7,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:feasible, 5:feasible, 6:feasible, 7:infeasible"
tabular-MiniBooNE,0.9,equal_width_merged:5x25,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
tabular-MiniBooNE,0.9,equal_width_merged:5x50,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
tabular-MiniBooNE,0.9,equal_width_merged:5x100,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
tabular-adult,0.5,quantile:3,1,1,feasible,0,1:feasible
tabular-adult,0.5,quantile:8,1,1,feasible,0,1:feasible
tabular-adult,0.5,equal_width_merged:5x25,1,0,feasible,0,0:feasible
tabular-adult,0.5,equal_width_merged:5x50,1,0,feasible,0,0:feasible
tabular-adult,0.5,equal_width_merged:5x100,1,0,feasible,0,0:feasible
tabular-adult,0.7,quantile:3,1,1,feasible,0,1:feasible
tabular-adult,0.7,quantile:8,1,1,feasible,0,1:feasible
tabular-adult,0.7,equal_width_merged:5x25,1,0,feasible,0,0:feasible
tabular-adult,0.7,equal_width_merged:5x50,1,0,feasible,0,0:feasible
tabular-adult,0.7,equal_width_merged:5x100,1,0,feasible,0,0:feasible
tabular-adult,0.9,quantile:3,2,2,infeasible,1,"1:feasible, 2:infeasible"
tabular-adult,0.9,quantile:8,2,2,infeasible,1,"1:feasible, 2:infeasible"
tabular-adult,0.9,equal_width_merged:5x25,5,4,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:feasible, 4:infeasible"
tabular-adult,0.9,equal_width_merged:5x50,4,3,infeasible,1,"0:feasible, 1:feasible, 2:feasible, 3:infeasible"
tabular-adult,0.9,equal_width_merged:5x100,3,2,infeasible,1,"0:feasible, 1:feasible, 2:infeasible"
tabular-spambase,0.5,quantile:3,1,1,feasible,0,1:feasible
tabular-spambase,0.5,quantile:8,1,1,feasible,0,1:feasible
tabular-spambase,0.5,equal_width_merged:5x25,1,0,feasible,0,0:feasible
tabular-spambase,0.5,equal_width_merged:5x50,1,0,feasible,0,0:feasible
tabular-spambase,0.5,equal_width_merged:5x100,1,0,feasible,0,0:feasible
tabular-spambase,0.7,quantile:3,3,2,feasible,0,"0:feasible, 1:feasible, 2:feasible"
tabular-spambase,0.7,quantile:8,5,5,feasible,0,"1:feasible, 2:feasible, 3:feasible, 4:feasible, 5:feasible"
tabular-spambase,0.7,equal_width_merged:5x25,1,0,feasible,0,0:feasible
tabular-spambase,0.7,equal_width_merged:5x50,1,0,feasible,0,0:feasible
tabular-spambase,0.7,equal_width_merged:5x100,1,0,feasible,0,0:feasible
tabular-spambase,0.9,quantile:3,3,2,undetermined,0,"0:feasible, 1:feasible, 2:undetermined"
tabular-spambase,0.9,quantile:8,6,6,infeasible,1,"1:feasible, 2:feasible, 3:feasible, 4:feasible, 5:undetermined, 6:infeasible"
tabular-spambase,0.9,equal_width_merged:5x25,3,2,undetermined,0,"0:feasible, 1:feasible, 2:undetermined"
tabular-spambase,0.9,equal_width_merged:5x50,2,1,feasible,0,"0:feasible, 1:feasible"
tabular-spambase,0.9,equal_width_merged:5x100,1,0,feasible,0,0:feasible
```

Findings at the primary lambda_ref = 0.9:

1. **Verdict stability (three resolved datasets): the deepest stratum is
   endpoint-INFEASIBLE under ALL five alternative binnings** on MNIST,
   Adult, and MiniBooNE (quantile 3 and 8, equal-width at every m_min).
   The failure is not an artifact of the quantile-5 stratification.
2. **Spambase moves in BOTH directions:** quantile-3 and 5x25 ->
   undetermined (like the primary unresolved); **quantile-8 -> the deepest
   stratum is endpoint-infeasible** (finer binning isolates the hard core
   enough for the endpoint CP bound to clear alpha); **5x50 -> G = 2, all
   feasible; 5x100 -> G = 1, feasible** -- coarse equal-width binning
   DILUTES the hard stratum into bulk buckets.
3. **Dilution exists elsewhere too:** MNIST at lambda_ref 0.5 loses its
   equal-width infeasible bucket when m_min grows (5x25/5x50 flag stratum
   2 infeasible; 5x100 merges it away); Adult's realized G shrinks 5 -> 4
   -> 3 as m_min grows at 0.9 (verdict unchanged).
4. **Finer is not uniformly better:** quantile-8 helps on Spambase but is
   all-feasible on MNIST at 0.5 where equal-width 5x25 already flags an
   infeasible bucket; finer bins shrink n_k and CP power.
5. **Duplicate-cut collapse changes realized G:** yes -- Adult quantile-8
   realizes G = 2 (heavy duplicate cuts at T = 14); Spambase quantile-8
   realizes G = 6; several equal-width settings collapse to G = 1.

Answers to the Section-8 questions: verdicts of the three resolved
datasets are stable at 0.9 under every tested binning; no certified-failure
case disappears at 0.9 (dilution effects appear at 0.5/0.7 and on
Spambase); the unresolved Spambase case becomes endpoint-infeasible under
quantile-8 (an ENDPOINT CP verdict, not a family-wide certificate -- do
not upgrade it) and trivially "feasible" under 5x50/5x100 dilution --
**"Spambase remains unresolved" does NOT hold across all stratifications**
(Section 11, claim 9); larger m_min demonstrably dilutes the hard stratum.

---

## 9. Candidate compact tables

### Table S11, Panel A (reference threshold; exact values from the Section-2 CSV)

| Dataset | lr | G | n_k | Family min | p_fam | Verdict | IUT cert/refuse | Cost/full |
|---|---:|---:|---:|---:|---|---|---|---:|
| MNIST | 0.5 | 5 | 6440 | 0.1161 | 1.0e+00 | feasible | 100/0 | 0.626 |
| MNIST | 0.7 | 5 | 5376 | 0.1449 | 8.6e-01 | feasible | 8/92 | 0.972 |
| MNIST | 0.9 | 5 | 5479 | 0.2479 | 1.4e-79 | failure | 0/100 | 1.000 |
| Adult | 0.5 | 1 | 16280 | 0.1508 | 1.0e+00 | feasible | 100/0 | 0.361 |
| Adult | 0.7 | 1 | 16280 | 0.1508 | 1.0e+00 | feasible | 100/0 | 0.361 |
| Adult | 0.9 | 3 | 6268 | 0.3090 | 8.7e-93 | failure | 0/100 | 1.000 |
| MiniBooNE | 0.5 | 1 | 46823 | 0.0834 | 1.0e+00 | feasible | 100/0 | 0.050 |
| MiniBooNE | 0.7 | 1 | 46823 | 0.0834 | 1.0e+00 | feasible | 100/0 | 0.050 |
| MiniBooNE | 0.9 | 5 | 9180 | 0.2334 | 3.2e-98 | failure | 0/100 | 1.000 |
| Spambase | 0.5 | 1 | 1656 | 0.0592 | 1.0e+00 | feasible | 100/0 | 0.092 |
| Spambase | 0.7 | 4 | 344 | 0.1163 | 9.7e-01 | feasible | 20/80 | 0.901 |
| Spambase | 0.9 | 5 | 249 | 0.1727 | 1.8e-01 | unresolved | 0/100 | 1.000 |

(Caption must note: G = 1 rows are trivial stratifications where the audit
reduces to the aggregate; "feasible" there means the marginal target is
empirically attainable, not that a deep stratum was tested.)

### Table S11, Panel B (backbone seed; exact)

| Dataset | Seed | alpha | k* | n_k | Endpoint | LCB | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| MNIST | 0 | 0.15 | 4 | 5479 | 0.2479 | 0.238 | failure |
| MNIST | 1 | 0.20 | 4 | 7798 | 0.2657 | 0.257 | failure |
| MNIST | 2 | 0.15 | 4 | 5193 | 0.2681 | 0.258 | failure |
| Adult | 0 | 0.20 | 3 | 6268 | 0.3092 | 0.300 | failure |
| Adult | 1 | 0.25 | 4 | 6023 | 0.3155 | 0.306 | failure |
| Adult | 2 | 0.20 | 3 | 5462 | 0.3017 | 0.291 | failure |
| MiniBooNE | 0 | 0.15 | 4 | 9180 | 0.2334 | 0.226 | failure |
| MiniBooNE | 1 | 0.15 | 4 | 9387 | 0.2226 | 0.216 | failure |
| MiniBooNE | 2 | 0.15 | 4 | 9486 | 0.2490 | 0.242 | failure |
| Spambase | 0 | 0.15 | 4 | 249 | 0.1727 | 0.134 | unresolved |
| Spambase | 1 | 0.15 | 4 | 400 | 0.1700 | 0.140 | unresolved |
| Spambase | 2 | 0.15 | 4 | 311 | 0.1576 | 0.125 | unresolved |

### Table S12 (combined robustness summary; one row per dimension-setting per dataset)

Rows available exactly from the CSVs above: policy (4 settings; from the
Section-4 CSV), readiness score (2; Section-5), cost scheme (up to 3;
verdict identical by the 23,400-check invariance), quantile G0 (3;
endpoint-verdict basis), equal-width m_min (3; endpoint-verdict basis).
Compactness ruling: policy and binning should be SEPARATE panels or the
"Setting" column must carry the basis -- the binning rows report ENDPOINT
verdicts while policy/score/scheme rows report family verdicts; mixing the
two bases in one undifferentiated column would be misleading. Recommended:
Table S12 with a "basis" footnote and two visual groups (family-audit
dimensions; endpoint-audit binning dimensions), or move binning entirely
into the figure.

---

## 10. Data for Figure S10.1 (stratification sensitivity)

**The requested quantitative fields do not exist for the binning forks:**
family minimum minus alpha, family -log10(p), and q_k are frozen ONLY for
the quantile-5 stratification (the 105-config family audit). For G0 in
{3, 8} and equal-width m_min in {25, 50, 100} the canonical data are the
three-way per-stratum ENDPOINT verdicts and realized G (Section 7-8 CSV) --
no minima, no p-values, no stratum counts. Two options:

- **Option 1 (from frozen data, available now):** a verdict matrix/heatmap
  -- rows = datasets, columns = the 6 stratifications (quantile 3/5/8,
  equal-width 5x25/50/100) at lambda_ref 0.9, cell color = three-way
  verdict (deepest-stratum endpoint verdict for the five alternatives; the
  family verdict for quantile-5), annotated with realized G. The
  quantile-5 column carries the family audit; the caption must state the
  two bases. This shows exactly whether the 3-failure/1-unresolved pattern
  survives binning changes (it does for the three failures; Spambase's
  cell flips verdict with the binning -- the story of Section 7-8).
- **Option 2 (requires new compute):** extend `family_wide_feasibility.py`
  to loop the committed alternative edge families (the edges are already
  committed; the script change is one loop plus edge selection), run on
  the cluster pool caches, freeze `family_wide_binning_forks.csv`, and then
  build the requested (R_min - alpha, -log10 p, q_k) panels exactly as
  specified.

Exact data for Option 1 are fully contained in the Section 7-8 CSV. The
n_k*Delta^2 annotations requested for a heatmap are computable only for
quantile-5 (from the family table); for the forks they need Option 2.

---

## 11. Robustness claims

1. "Primary family-wide verdict stable across three backbone seeds." --
   **SUPPORTED** (12/12 rows: 3 failures x 3 seeds + Spambase unresolved
   x 3).
2. "Verdict unchanged under max-softmax and margin on all tested datasets."
   -- **SUPPORTED WITH SCOPE** (3 tested datasets; Spambase margin never
   run -- say "all three tested datasets").
3. "Verdict invariant to cost scheme." -- **SUPPORTED** (structural
   cost-blindness + 23,400/23,400 identical selections; the audit consumes
   losses only). MNIST has a single scheme; the claim is vacuous there.
4. "Verdict stable across greedy, random, and eps-greedy policies." --
   **SUPPORTED WITH SCOPE:** true at lambda_ref 0.9 on MNIST/Adult/
   MiniBooNE (12/12 policy-seed cells: failure); FALSE on Spambase
   (feasible / unresolved / failure across policies) -- scope to the three
   resolved datasets.
5. "Better policies systematically hide family-wide failure." --
   **UNSUPPORTED; DO NOT CLAIM** (per-dataset evidence is mixed and
   sign-flipping; only the composition-sensitive aggregate Spearman is
   positive; PHASE2's own fork verdict is "MIXED, monotone on 1 of 4").
6. "The detection frontier is unchanged within datasets." --
   **UNSUPPORTED as stated:** flat on Adult/MiniBooNE only; MNIST's
   frontier moves with policy (0.5-0.9) and seed (ts2 detects at 0.7);
   Spambase is mixed. Use the Section-4 corrected sentence.
7. "The three-failure/one-unresolved pattern survives quantile G0 in
   {3, 5, 8}." -- **SUPPORTED WITH SCOPE:** the three failures survive as
   deepest-stratum endpoint-infeasibility at G0 = 3 and 8 (family
   certificates exist only at G0 = 5); the "one-unresolved" half does NOT
   survive verbatim -- Spambase is undetermined at G0 = 3 and
   endpoint-infeasible at G0 = 8.
8. "The pattern survives equal-width binning with m_min 25/50/100." --
   **SUPPORTED WITH SCOPE:** the three failures survive at all three
   m_min; Spambase dilutes to feasible-by-collapse at m_min 50/100
   (G = 2/1) -- state the dilution, don't call it survival.
9. "Spambase remains unresolved across all reasonable stratifications." --
   **UNSUPPORTED; DO NOT CLAIM.** Unresolved at quantile-5 for all seeds,
   policies (except the two policy flips), and lambda_refs; but
   quantile-8 yields an endpoint-infeasible deepest stratum and coarse
   equal-width yields trivial "feasible" collapses. Correct: "unresolved
   at the primary stratification for every seed; alternative binnings move
   it in both directions."
10. "The primary lambda_ref = 0.9 result is not an artifact of one
    reference threshold." -- **SUPPORTED WITH SCOPE:** 0.9 was committed
    in the Phase-0 config grid {0.5, 0.7, 0.9} and designated primary in
    the Phase-5.3 spec (not post hoc); the failures certify only at 0.9
    for greedy ts0 -- BUT weaker policies and MNIST ts2 certify already at
    0.7 (and mnist random ts2 at 0.5), so the phenomenon is not tied to
    the single value 0.9; visibility requires sufficient stratification
    depth. Never say "reference-threshold invariant".
11. "Coarser stratification can hide an infeasible core through dilution."
    -- **SUPPORTED** (Spambase 5x100: G = 1, feasible; 5x50: G = 2,
    feasible; MNIST @0.5 loses the flagged bucket at 5x100).
12. "Finer stratification always improves detectability." --
    **UNSUPPORTED; DO NOT CLAIM** ("always" fails: MNIST @0.5 quantile-8
    is all-feasible where equal-width 5x25 flags a bucket; finer bins cut
    n_k and CP/binomial power; Spambase quantile-8 helps -- direction is
    dataset-dependent).

---

## 12. Scope and prohibited wording

Use: "stable across the tested settings"; "within each dataset"; "under
the frozen predictor and policy family"; "verdict unchanged"; "not
detected"; "unresolved"; "visibility depends on stratification
resolution". Do not use: "fully robust"; "invariant to all
hyperparameters"; "better policies hide failure"; "Spambase is feasible";
"reference-threshold invariant" (only structural quantities like the
marginal selection are lambda_ref-independent); "finer is always better";
"all cost-aware policies" (the tested policies are cost-blind);
"all possible strata" (six binnings were tested, all probe-committed).

---

## 13. Contradiction checks

- Seed alphas: consistent everywhere (MNIST ts1 0.20, Adult ts1 0.25, rest
  0.15/0.20).
- Adult k\* across seeds: 3 / 4 / 3 -- any manuscript sentence saying
  "stratum 3" must be scoped to seeds 0/2 (seed 1 realizes label 4).
- Margin scope: three datasets; Spambase margin never run (optional cell
  16) -- consistent; no artifact claims otherwise.
- Local vs canonical Spearman: local pilot values (rho(quality,
  entropy@0.5) = -0.757, p = 0.0007) differ from canonical (-0.746,
  p = 0.0009); frontier rho canonical = 0.576 (p = 0.0196). Cite canonical
  only; project_update already warns not to quote the aggregate without
  the caveat.
- "Flat frontier": PHASE2's fork verdict is "MIXED (monotone on 1 of 4
  datasets)" and the family-audit frontier varies on MNIST/Spambase -- any
  flat-frontier sentence must be per-dataset. Note also that TWO frontier
  definitions exist (Phase-2 endpoint flag vs Phase-5.3 family
  certificate); S10 should use the family-audit frontier and say so.
- Cost-scheme invariance: no conflict; now verified empirically
  (23,400/23,400).
- Quantile G0 values {3, 5, 8} and equal-width m_min {25, 50, 100} (as
  5x25/5x50/5x100): match the request exactly.
- Verdict counts under alternative binnings: no artifact reports
  family-level counts under alternative binnings -- S10 must not invent
  them (endpoint basis only).
- lambda_ref = 0.9 primary vs post hoc: committed in the Phase-0
  experiment config and hard-coded as `_PRIMARY_LR` in the Phase-5.3
  scripts before results -- primary by commitment.
- Binning-ablation section headers omit seed/score: a report defect; rows
  disambiguated here by the generator's sorted iteration order (flagged in
  Section 15).

---

## 14. Rounding and terminology

Precision: risks and family minima 4 dp; q_k 3 dp; p-values scientific 2
significant digits (exact values in the CSVs); costs 3 dp;
certification/refusal counts exact "k/100"; thresholds 3 dp; robustness
differences (e.g. min - alpha) 3-4 dp. Short names: Greedy / Random /
eG(.25) / eG(.5); max-softmax / margin; uniform / inv-info / random-cost;
"quantile-3/5/8"; "equal-width 5 bins, min-bucket 25/50/100" (code keys
5x25/5x50/5x100); verdicts: "feasible" (empirically feasible) / "failure"
(certified family-wide failure) / "unresolved"; endpoint basis:
"endpoint-feasible / endpoint-infeasible / undetermined" -- keep the two
vocabularies distinct.

---

## 15. Missing information and final verdict

### Missing information

1. **Family-wide IU audit under alternative binnings** (family minima,
   family p-values, LCBs, n_k, q_k for quantile-3/8 and equal-width
   5x25/50/100): not stored -- only per-stratum endpoint verdicts +
   realized G (RESULTS.md Section 6). Reconstructable: the alternative
   edges are committed; the audit script needs a small loop extension +
   cluster pool caches.
2. **IUT certification/refusal counts under alternative binnings:** not
   stored (same gap).
3. Binning-ablation rows exist only as markdown tables with seed-less
   section headers (parsed here by generator order); no CSV artifact.
4. Depth-concentration statistic per (dataset, policy, seed): fork_strata
   is keyed without seed (one row per dataset x policy x lambda_ref).
5. Per-scheme pool costs: primary scheme only (per-scheme test-half costs
   stored; invariance makes risk columns redundant).
6. Local-pilot-only: the alternative Spearman values (superseded by
   canonical PHASE2_READOUT).
7. Ambiguous/contradicted: none beyond the header defect (3).

### Required author decisions

1. Figure type: Option-1 verdict heatmap from frozen endpoint verdicts
   (available now, two-basis caption) vs Option-2 quantitative panels
   (requires the binning-fork family audit run).
2. Whether reference-threshold sensitivity lives in Table S11 Panel A
   (recommended -- 12 exact rows ready) or joins the figure.
3. Cost-scheme robustness: prose sentence + the 23,400-check statement
   (recommended); no numeric table needed.
4. Policy robustness: Section-4 CSV as a compact table vs prose-only; the
   Spambase verdict flips argue for showing the 16 ts0 rows.
5. One vs two compact tables: keep S11 (two panels) + S12 with the
   two-basis footnote, or fold S12's binning rows into the figure.

### Final verdict

`S10 SOURCE MATERIAL INCOMPLETE`

Everything for S10.1 and the policy/score/cost-scheme half of S10.2 is
complete and embedded above. The single gap is the binning-sensitivity
QUANTITATIVE data requested for Figure S10.1 (family minima, p-values, q_k
under G0 in {3, 8} and equal-width m_min in {25, 50, 100}). Minimum
actions, either one sufficient:

1. AUTHOR DECISION: accept the Option-1 verdict-heatmap figure built from
   the frozen endpoint verdicts (Section 7-8 CSV) with a two-basis
   caption -- then S10 source material is complete as-is; or
2. RUN: extend `family_wide_feasibility.py` to iterate the committed
   alternative edge families (quantile 3/8, equal_width_merged
   5x25/50/100), execute on the cluster pool caches, commit
   `family_wide_binning_forks.csv`, and then build the figure exactly as
   requested in Section 10.
