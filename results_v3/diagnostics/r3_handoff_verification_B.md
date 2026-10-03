Slice B has 6 real discrepancies and 3 minor ones; everything else matches the source files. Severity order: items 1–3 are factual errors, 4 is a claim no file backs, 5–6 overstate what the numbers show, 7–9 are minor. I edited nothing in the repo or under F:/CAFA_results. My only throwaway script is `C:/Users/USER/AppData/Local/Temp/claude/F--FAU-PhD-Side-Quest-CAFA-exp/46902fe5-0f0d-47f7-83c2-7e4b88242f1d/scratchpad/verify_B/persplit.py`.

Per-split oracle values, recomputed from `F:/CAFA_results/metrics_v3/*.json` with the same logic as `make_tables_v3.cost_gap_row` (δ₁ = 0.05). These back items 2, 3 and 5:

| cell | split | oracle feasible | r_cal | n_needed |
|---|---|---|---|---|
| FashionMNIST greedy | 778 / 779 / 780 / 781 / 782 | 0/20, then 20/20 | — / 0.167 / 0.1371 / 0.1462 / 0.1509 | inf / inf / 4,482 / 51,897 / inf |
| FashionMNIST random | 778 / 779 / 780 / 781 / 782 | 0/20, then 20/20 | — / 0.1651 / 0.1432 / 0.1481 / 0.160 | inf / inf / 16,344 / 215,884 / inf |
| MNIST random | 778 / 779 / 780 / 781 / 782 | 20/20 all | 0.0973 / 0.0938 / 0.1098 / 0.0967 / 0.0927 | 73,960 / 13,594 / inf / 50,242 / 9,898 |
| Imagenette greedy | 778 / 779 / 780 / 781 / 782 | 20/20 all | 0.1205 / 0.0916 / 0.105 / 0.0729 / 0.0668 | inf / 7,539 / inf / 670 / 437 |

**1. §13.4 K1 code, line 1319**
- Handoff: "They record `calpool_stratum_risk` on the split's whole calibration pool at λ*."
- Source: `scripts/run_cascade_sweep.py` (lines 52–66 and 598–611). Only `oracle_stratum_safe` records `calpool_stratum_risk` / `calpool_stratum_n`. `oracle_stratum_safe_mondrian` records only `feasible`, `lambda_by_stratum` and `abstained_fraction`.
- Corrected: "`oracle_stratum_safe` also records `calpool_stratum_risk` / `calpool_stratum_n` on the split's whole calibration pool at λ* (None when infeasible); the Mondrian version records `lambda_by_stratum` and `abstained_fraction`."

**2. §13.4 "Reading the cost gap", sample-limited bullet**
- Handoff: "FashionMNIST 4,482 and 16,344 on its finite splits, vs 1,320 / 1,426;"
- Source: per-split table above. Each policy has two finite splits. 4,482 and 16,344 are only the greedy and random minima (`n_needed_range` 4482–inf and 16344–inf in `TABLE_E4_cost_gap.csv`).
- Corrected: "FashionMNIST greedy 4,482 and 51,897, random 16,344 and 215,884 on its two finite splits (780, 781), vs 1,320 / 1,426;"

**3. Same bullet**
- Handoff: "On the other splits the oracle's λ* has calibration-pool risk ≥ α although its test risk is ≤ α, so no calibration size certifies that exact λ*."
- Source: per-split table above. FashionMNIST split 778 (both policies) has no feasible oracle (0/20 draws), so there is no λ* there. `label_note` in `TABLE_E4_cost_gap.csv` says "oracle infeasible in 1/5 splits; n_needed inf in 3/5 splits".
- Corrected: "On the other splits the oracle's λ* has calibration-pool risk ≥ α although its test risk is ≤ α, so no calibration size certifies that exact λ*. The exception is FashionMNIST split 778 (both policies), where no grid λ is stratum-safe even ex post."

**4. §13.4 K1 rerun, line 1324 (no file backs this)**
- Handoff: "16 files, sha256 in `results_v3/round2/metrics_v3_round2.sha256`, equal to the pre-move hashes."
- Source: no pre-move hash record exists. The hashes appear only in that `.sha256` file (written 13:27:44, one second after the `metrics_v3_round2` folder was created) and in git commits of it. No log or ledger line has hashes taken before the move. `sha256sum -c` against the file passes 16/16 now, and `r3_final_checklist.log` reports "files listed: 16, check rc 0".
- Corrected: "16 files, sha256 recorded at the move in `results_v3/round2/metrics_v3_round2.sha256`; 16/16 OK on re-check (`results_v3/logs/r3_final_checklist.log`)."

**5. §13.4 caveat on `n_needed` (overstated)**
- Handoff: "Example: MNIST random has r_cal 0.097 vs α 0.10, hence n_needed 50,242, yet the cascade certifies a slightly more conservative λ at cost ratio 1.09."
- Source: the table's r_cal 0.0973 belongs to split 778, whose own n_needed is 73,960. 50,242 is the 5-split median, which is split 781's value (r_cal 0.0967). The "more conservative λ" part checks out: the cascade's λ exceeds the oracle's λ* in 100/100 draws, by 0.010–0.071.
- Corrected: "Example: MNIST random's r_cal is 0.093–0.097 vs α 0.10 on four splits (0.110 on split 780), hence n_needed 9,898–73,960 (median 50,242), yet the cascade certifies a slightly more conservative λ at cost ratio 1.09."

**6. §13.4 "Reading the calibration-size table" (overstated)**
- Handoff: "Doubling the calibration draw (0.5 → 1.0) raises the tier-1 share and lowers the cost in the sample-limited cells:"
- Source: `TABLE_E11_calfrac.csv`. MiniBooNE random is a sample-limited cell, and its tier-1 share falls 0.26 → 0.20 while cost/T stays flat (0.862 → 0.858). The handoff's own next bullet says so.
- Corrected: "Doubling the calibration draw (0.5 → 1.0) raises the tier-1 share and lowers the cost in four of the five sample-limited cells (not MiniBooNE random, below):"

**7. §13.4 near-oracle bullet (minor)**
- Handoff: "Near-oracle: PhysioNet, CUBE, MNIST, Adult greedy. The cascade is within 1.04–1.26 of the oracle."
- Source: `TABLE_E4_cost_gap.csv` has `cascade_over_safe_oracle` empty for PhysioNet: both costs are 0. The range 1.041–1.264 covers only CUBE, MNIST and Adult greedy.
- Corrected: "...The cascade is within 1.04–1.26 of the oracle (PhysioNet: both cost 0)."

**8. §13.4 K1 rerun, line 1327 (minor)**
- Handoff: "So every round-2 number in §8 stands; the rerun only adds the oracle fields."
- Source: comparing the key paths of the round-2 and round-3 metrics files, the new files also add `meta.cal_frac`.
- Corrected: "...the rerun only adds the oracle fields (and `meta.cal_frac`)."

**9. §13.4 K2 runs (minor)**
- Handoff: "`drive_v3.py --phase sweep --seeds 0 --metrics-dir-name metrics_v3_calfrac025 --tag r3cf025 "--extra-args=--cal-frac 0.25"`: 16 runs..."
- Source: `results_v3/logs/r3_lane.sh` and `driver_r3_lane*.out`. The runs were issued per dataset (`--datasets <ds>`) through parallel lanes. The output is the same. 1,760.3 s and 488.4 s (and 2,800.2 s for `r3:sweep`) are sums of per-run seconds, not wall time.
- Corrected: add "(run per dataset via `results_v3/logs/r3_lane.sh`; seconds = sum over runs)".

**What checks out:**
- **§8.1 round-3 columns table:** all 16 rows × 11 columns match `results_v3/tables/TABLE_E4_cascade.csv`. `r3_table_invariance.log` shows 22/22 shared columns, 0 differences and 8 added columns. The round-2 table above it also matches the current CSV.
- **§8.4 round-3 E6 rows:** all 32 rows match `TABLE_E6_baselines.csv` (192 rows = 160 + 32). The new rows sit between `oracle_cheapest_valid` and `plugin` in every cell, and the `feasible_rate` column exists.
- **§8.4 E6 note:** under full acquisition, only the deepest stratum exceeds α, on exactly the oracle-infeasible splits: Diabetes 5/5, FashionMNIST split 778, Adult random 778–781, MiniBooNE greedy 778/779/782.
- **K1 equivalence:** the log says IDENTICAL for 16 cells; 10 × 800 + 6 × 400 = 10,400 draw records. The checker compares every leaf of the old file except `meta.cache_meta`, which it drops; I checked that field separately and it is equal in 16/16 files.
- **Ledger:** `r3:sweep` 16 runs, rc 0, 2,800.2 s; `r3cf025` 16 runs, rc 0, 1,760.3 s; `r3cf100` 16 runs, rc 0, 488.4 s.
- **Code and tests:** `tests/test_oracles_v3.py` collects 14 tests. The summary field names, `--cal-frac` default 0.5 and its `--out-dir` guard, and the nesting of 0.25 draws inside 0.5 draws all match the code.
- **Cal-frac metrics:** `meta.cal_frac_note` is present and n_draws = 5 in all 16 cal-frac 1.0 files; the 0.25 files have cal_frac 0.25 and 100 draws.
- **Cost-gap table:** all 16 rows match `TABLE_E4_cost_gap.csv`. The label rule (0.9 / 1.6), the `n_needed` definition with `kl_bernoulli`, and the use of split 778's n_k / r_cal also match.
- **Cost-gap reading bullets:** oracle 0.19–0.46 of T, cascade 2.0–5.0× the oracle, the Imagenette and MiniBooNE `n_needed` values, the 4/5 and 3/5 infeasible splits, 3.595 and 2.761, and Diabetes 0/20 feasible on every split are all correct.
- **E11 table:** all 16 rows match `TABLE_E11_calfrac.csv`.
- **E11 reading bullets:** these match `tables_e11_calfrac{025,100}/TABLE_E4_cascade.csv`. Diabetes greedy at 0.25 is tier 3 0.93 with none 0.07, and it is the only cell with certified deployment below 1. Certified violation ≤ 0.010, raw violation ≤ 0.07 and ≤ 0.20, mean `max_excess_se` < 0 in every cell, MiniBooNE random hyper prediction 0.20, and 640 cal-frac points in F7 (`r3_margin_analysis.log`) are all correct.