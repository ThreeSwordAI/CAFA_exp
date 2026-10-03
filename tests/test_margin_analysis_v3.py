"""v3 -- tests of scripts/margin_analysis_v3.py (E10 certifiability margin, E11 calibration-size table, F7).

The prediction is checked on its own (P(certify) ~ 1 for a large margin, ~ 0 for a negative one; mid-range
values against an enumeration of the binomial over the certifiable error counts that does not go through
``k_max``; ``k_max`` nondecreasing in n and equal to the brute-force boundary of the frozen Hoeffding-Bentkus
p-value, with or without a search hint), the hypergeometric (conditional-on-the-pool) prediction against a
brute-force enumeration with exact binomial coefficients and as the indicator at cal_frac 1.0, and the script
end to end on a hand-written metrics layout (``run_cascade_sweep.py`` fields that the script reads) with its
commit JSON in tmp_path: two cells, two splits, keys 0.5 and dep, a split whose deepest stratum is missing,
draws with known tiers, a cal_frac 0.25 directory for one of the two cells, commits whose edges / G disagree
with the metrics, and a cost scheme that only one cell has.
"""

from __future__ import annotations

import csv
import json
import sys
from math import comb
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import binom, spearmanr

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import margin_analysis_v3 as M  # noqa: E402
from cafa.risk_control import hoeffding_bentkus_pvalue  # noqa: E402

LEVEL = 0.05     # delta_1 = 0.10 * 0.5


# --------------------------------------------------------------------------- #
# The prediction
# --------------------------------------------------------------------------- #
def test_prediction_is_one_for_large_margin_and_zero_for_negative_margin():
    assert M.pred_certify(2000, 0.01, 0.15, LEVEL) > 0.999
    assert M.pred_certify(2000, 0.20, 0.15, LEVEL) < 0.001
    # nothing certifiable on 10 rows at alpha 0.1 (p(0) = 0.9^10 > 0.05): prediction 0, k_max -1
    assert M.k_max_certifiable(10, 0.10, LEVEL) == -1
    assert M.pred_certify(10, 0.0, 0.10, LEVEL) == 0.0


def test_k_max_nondecreasing_in_n():
    ks = [M.k_max_certifiable(n, 0.15, LEVEL) for n in range(10, 3001)]
    assert all(b >= a for a, b in zip(ks, ks[1:]))
    assert ks[0] == -1 and ks[-1] > 0


@pytest.mark.parametrize("n", [10, 37, 120, 523, 1500])
def test_k_max_is_the_brute_force_boundary(n):
    alpha = 0.15
    p = np.array([hoeffding_bentkus_pvalue(k / n, n, alpha) for k in range(n + 1)])
    assert np.all(np.diff(p) >= 0)                      # the p-value is nondecreasing in the error count
    km = M.k_max_certifiable(n, alpha, LEVEL)
    assert km == (int(np.nonzero(p <= LEVEL)[0].max()) if np.any(p <= LEVEL) else -1)
    if km >= 0:
        assert p[km] <= LEVEL
    if km + 1 <= n:
        assert p[km + 1] > LEVEL
    for hint in {0, 1, km - 3, km - 1, km, km + 1, km + 3, n // 2, n}:     # the hint only narrows the search
        assert M._k_max_search(n, alpha, LEVEL, hint=hint) == km


@pytest.mark.parametrize("n, r, alpha, expected", [(500, 0.12, 0.15, 0.4248), (1200, 0.13, 0.15, 0.4529),
                                                   (300, 0.15, 0.20, 0.5397), (2000, 0.18, 0.20, 0.5602)])
def test_prediction_mid_range_matches_enumeration(n, r, alpha, expected):
    # P(certify) = sum of Bin(n, r) pmf over the error counts whose HB p-value is <= level: no k_max involved
    # (an off-by-one in k_max or in the cdf argument moves these values by > 0.02)
    ref = sum(binom.pmf(k, n, r) for k in range(n + 1) if hoeffding_bentkus_pvalue(k / n, n, alpha) <= LEVEL)
    assert M.pred_certify(n, r, alpha, LEVEL) == pytest.approx(ref, rel=1e-9)
    assert ref == pytest.approx(expected, abs=1e-4)


def hyper_brute(n_pool, n_k, e_k, n_cal, alpha, level=LEVEL):
    """P(certify | pool) by enumeration with exact binomial coefficients: n_d rows of the stratum in the draw,
    k errors among them, certified iff the HB p-value of k / n_d is <= level (independent of k_max and scipy)."""
    tot = 0.0
    for nd in range(0, min(n_k, n_cal) + 1):
        if n_cal - nd > n_pool - n_k:
            continue
        w = comb(n_k, nd) * comb(n_pool - n_k, n_cal - nd) / comb(n_pool, n_cal)
        for k in range(0, min(e_k, nd) + 1):
            if nd - k <= n_k - e_k and nd > 0 and hoeffding_bentkus_pvalue(k / nd, nd, alpha) <= level:
                tot += w * comb(e_k, k) * comb(n_k - e_k, nd - k) / comb(n_k, nd)
    return tot


@pytest.mark.parametrize("n_pool, n_k, e_k, n_cal, alpha", [(60, 30, 3, 30, 0.3), (60, 30, 1, 30, 0.3),
                                                           (80, 25, 2, 40, 0.3), (90, 60, 7, 45, 0.25)])
def test_hyper_prediction_matches_brute_force(n_pool, n_k, e_k, n_cal, alpha):
    ref = hyper_brute(n_pool, n_k, e_k, n_cal, alpha)
    assert 0.01 < ref < 0.99                                  # a mid-range case
    assert M.pred_certify_hyper(n_pool, n_k, e_k, n_cal, alpha, LEVEL) == pytest.approx(ref, abs=1e-9)
    assert M.pred_certify_hyper(60, 30, 3, 30, 0.3, LEVEL) == pytest.approx(0.18521, abs=1e-5)


def test_hyper_prediction_is_the_indicator_at_cal_frac_one():
    # n_cal = n_pool: the draw is the whole pool, so the stratum count is n_k and the error count e_k surely
    vals = [M.pred_certify_hyper(60, 30, e, 60, 0.3, LEVEL) for e in range(8)]
    assert vals == [float(hoeffding_bentkus_pvalue(e / 30, 30, 0.3) <= LEVEL) for e in range(8)]
    assert vals == [1.0] * 4 + [0.0] * 4                       # k_max(30, 0.3) = 3


# --------------------------------------------------------------------------- #
# Synthetic metrics layout
# --------------------------------------------------------------------------- #
SPLITS = [778, 779]
CELL_A = {  # dsname, policy, seed, alpha, T, keys
    "dsname": "toy", "policy": "greedy_entropy", "seed": 0, "alpha": 0.15, "T": 40, "n_calpool": 6000,
    "keys": {
        "0.5": {"edges": [0.3], "expected": [900.4, 2000.6],
                "audit": {778: {0: (1800, 0.05, 0.05), 1: (4000, 0.01, 0.009)},
                          779: {0: (1800, 0.05, 0.05), 1: (4000, 0.20, 0.19)}},
                "tiers": {778: [1] * 20, 779: [3] * 15 + [0] * 5}, "cost": 10.0, "certviol": 0.0},
        "dep": {"edges": [0.2, 0.5], "expected": [300.0, 400.0, 500.2],
                "audit": {778: {0: (600, 0.05, 0.05), 1: (800, 0.06, 0.06), 2: (1000, 0.12, 0.11)},
                          779: {0: (600, 0.05, 0.05), 1: (800, 0.05, 0.05)}},   # deepest stratum absent
                "tiers": {778: [1] * 10 + [2] * 10, 779: [1] * 20}, "cost": 20.0, "certviol": 0.01},
    }}
CELL_B = {
    "dsname": "toy2", "policy": "random", "seed": 1, "alpha": 0.2, "T": 10, "n_calpool": 3000,
    "keys": {
        "dep": {"edges": [0.4], "expected": [700.0, 800.0],
                "audit": {778: {0: (1400, 0.1, 0.1), 1: (1600, 0.30, 0.30)},
                          779: {0: (1400, 0.1, 0.1), 1: (1600, 0.02, 0.02)}},
                "tiers": {778: [3] * 20, 779: [1] * 20}, "cost": 9.0, "certviol": 0.0},
    }}
CELL_C = {  # G = 1 (no edges), like the PhysioNet dep key
    "dsname": "toy3", "policy": "greedy_entropy", "seed": 0, "alpha": 0.15, "T": 20, "n_calpool": 2160,
    "keys": {
        "dep": {"edges": [], "expected": [1080.0],
                "audit": {778: {0: (2160, 0.10, 0.10)}, 779: {0: (2160, 0.11, 0.10)}},
                "tiers": {778: [1] * 20, 779: [1] * 20}, "cost": 20.0, "certviol": 0.0},
    }}


def metrics_json(cell: dict, cal_frac=None, overrides=None, schemes=("uniform",)) -> dict:
    lr = {}
    for key, spec in cell["keys"].items():
        spec = {**spec, **(overrides or {}).get(key, {})}
        draws = [{"draw": si * 1000 + i, "split_seed": s, "split_index": si, "cascade": {"tier": t}}
                 for si, s in enumerate(SPLITS) for i, t in enumerate(spec["tiers"][s])]
        tiers = np.array([r["cascade"]["tier"] for r in draws])
        summary = {"n_draws": len(draws), "tier_share": {str(t): float(np.mean(tiers == t)) for t in range(4)},
                   "cascade_mean_test_cost": spec["cost"], "cascade_certified_violation_rate": spec["certviol"]}
        aud = {str(s): {str(k): {"k": k, "n_k": nk, "r_full": rf, "rmin_thr": rt, "rmin_depth": rf, "verdict": "feasible"}
                        for k, (nk, rf, rt) in a.items()} for s, a in spec["audit"].items()}
        lr[key] = {"lambda_ref": 0.5, "edges": spec["edges"], "G": len(spec["edges"]) + 1, "audit": aud["778"],
                   "audit_by_split": aud, "schemes": {sc: {"summary": summary, "draws": draws} for sc in schemes}}
    meta = {"dsname": cell["dsname"], "policy": cell["policy"], "train_seed": cell["seed"], "T": cell["T"],
            "test_seeds": SPLITS, "primary_test_seed": SPLITS[0], "n_calpool": cell["n_calpool"]}
    if cal_frac is not None:
        meta["cal_frac"] = cal_frac
    return {"meta": meta, "alpha": cell["alpha"], "delta": 0.10, "delta_weights": [0.5, 0.25, 0.25], "lambda_refs": lr}


def write_metrics(d: Path, cell: dict, **kw) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{cell['dsname']}_ts{cell['seed']}_{cell['policy']}_softmax.json"
    p.write_text(json.dumps(metrics_json(cell, **kw)))
    return p


def write_commit(d: Path, cell: dict, edges_override=None, expected_override=None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    edges = {}
    for key, spec in cell["keys"].items():
        e = (edges_override or {}).get(key, spec["edges"])
        x = (expected_override or {}).get(key, spec["expected"])
        edges[key] = {"edges": e, "G": len(x), "expected_cal_counts": x, "n_min_tier1": 100}
    edges = {cell["policy"]: edges}
    p = d / f"committed_v3_{cell['dsname']}_ts{cell['seed']}.json"
    p.write_text(json.dumps({"alpha": cell["alpha"], "delta": 0.10, "edges": edges,
                             "split": {"cal_frac_of_pool": 0.5, "test_seeds": SPLITS}}))
    return p


@pytest.fixture()
def layout(tmp_path):
    for cell in (CELL_A, CELL_B):
        write_metrics(tmp_path / "metrics", cell)
        write_commit(tmp_path / "configs", cell)
    return tmp_path


def run(tmp_path, *extra):
    out, fig = tmp_path / "tables", tmp_path / "figures" / "F7_margin.pdf"
    assert M.main(["--metrics-dir", str(tmp_path / "metrics"), "--commits-dir", str(tmp_path / "configs"),
                   "--output-dir", str(out), "--figure", str(fig), *extra]) == 0
    return out, fig


def rows(path: Path) -> list:
    return list(csv.DictReader(open(path, encoding="utf-8")))


def find(rs, ds, key, split):
    (r,) = [r for r in rs if r["dataset"] == ds and r["key"] == key and int(r["split"]) == split]
    return r


# --------------------------------------------------------------------------- #
# End to end
# --------------------------------------------------------------------------- #
def test_e10_rows(layout):
    out, _ = run(layout)
    rs = rows(out / "TABLE_E10_margin.csv")
    assert len(rs) == 2 * 2 + 1 * 2                      # cell A: 2 keys x 2 splits; cell B: 1 key x 2 splits
    assert list(rs[0])[:len(M.E10_COLS)] == list(M.E10_COLS)
    r = find(rs, "toy", "0.5", 778)
    assert (int(r["k_star"]), int(r["n_k"]), int(r["n_k_calpool"])) == (1, 2001, 4000)   # round(2000.6)
    assert float(r["obs_tier1"]) == 1.0 and float(r["pred_tier1"]) > 0.999 and int(r["n_draws_split"]) == 20
    r = find(rs, "toy", "0.5", 779)
    assert float(r["obs_tier1"]) == 0.0 and float(r["tier3_share"]) == 0.75 and float(r["pred_tier1"]) < 0.001
    r = find(rs, "toy", "dep", 778)
    assert (int(r["k_star"]), int(r["n_k"])) == (2, 500) and float(r["obs_tier1"]) == 0.5
    alpha, rf, n = 0.15, 0.12, 500
    assert float(r["margin"]) == pytest.approx(alpha - rf)
    assert float(r["z"]) == pytest.approx((alpha - rf) * np.sqrt(n / (alpha * (1 - alpha))))
    assert int(r["k_max"]) == M.k_max_certifiable(n, alpha, LEVEL)
    assert float(r["pred_tier1"]) == pytest.approx(M.pred_certify(n, rf, alpha, LEVEL))
    assert float(r["pred_tier1_thr"]) == pytest.approx(M.pred_certify(n, 0.11, alpha, LEVEL))
    # pred_tier1_hyper: N_pool = meta n_calpool, N_k = n_k_calpool, E_k = round(r_full N_k), n_cal = round(0.5 N_pool)
    assert float(r["pred_tier1_hyper"]) == pytest.approx(M.pred_certify_hyper(6000, 1000, 120, 3000, alpha, LEVEL))
    assert 0.0 < float(r["pred_tier1_hyper"]) < 1.0
    r = find(rs, "toy", "dep", 779)                     # k_star is per split: stratum 2 is absent on 779
    assert (int(r["k_star"]), int(r["n_k"])) == (1, 400)
    r = find(rs, "toy2", "dep", 778)
    assert r["seed"] == "1" and r["policy"] == "random" and float(r["alpha"]) == 0.2
    assert float(r["pred_tier1_hyper"]) == pytest.approx(M.pred_certify_hyper(3000, 1600, 480, 1500, 0.2, LEVEL))
    assert list(rs[0])[-2:] == ["pred_tier1_nk_calpool", "pred_tier1_hyper"]
    md = (out / "TABLE_E10_margin.md").read_text(encoding="utf-8")
    assert md.startswith("# TABLE_E10_margin") and "delta_1" in md
    assert "pred_tier1_hyper" in md and "unconditional" in md and "CONDITIONAL" in md
    assert sum(1 for ln in md.splitlines() if ln.startswith("| toy")) == 6


def test_summary_json(layout):
    out, _ = run(layout)
    s = json.loads((out / "TABLE_E10_margin_summary.json").read_text(encoding="utf-8"))
    rs = rows(out / "TABLE_E10_margin.csv")
    obs = np.array([float(r["obs_tier1"]) for r in rs])
    for name in ("pred_tier1", "pred_tier1_thr", "pred_tier1_hyper"):
        pr = np.array([float(r[name]) for r in rs])
        rho, pv = spearmanr(obs, pr)
        st = s["main"][name]
        assert st["spearman_rho"] == pytest.approx(rho) and st["spearman_p"] == pytest.approx(pv)
        assert st["frac_within_tol"] == pytest.approx(np.mean(np.abs(obs - pr) <= 0.2))
        assert st["n_within_tol"] == int(np.sum(np.abs(obs - pr) <= 0.2))
        assert st["mean_abs_err"] == pytest.approx(np.mean(np.abs(obs - pr)))
    assert s["n_points"] == 6 and s["main"]["n"] == 6 and s["tol"] == 0.2
    assert s["main_dep"]["n"] == 4 and set(s["by_dataset"]) == {"toy", "toy2"}
    assert s["by_dataset"]["toy2"]["n"] == 2 and "calfrac" not in s
    assert "pred_tier1_nk_calpool" in s["main"] and "pred_tier1_hyper" in s["main_dep"]
    smd = (out / "TABLE_E10_margin_summary.md").read_text(encoding="utf-8")
    assert smd.startswith("# TABLE_E10_margin_summary") and "| main (all keys) | pred_tier1_hyper |" in smd


def test_f7_written(layout):
    _, fig = run(layout, "--png")
    assert fig.exists() and fig.stat().st_size > 0
    assert fig.with_suffix(".png").exists()


def test_e11_calfrac_scaling_and_tbd(layout):
    # cal_frac 0.25 run for cell A only (fewer draws, other summary values); no 1.0 run at all
    write_metrics(layout / "cf025", CELL_A, cal_frac=0.25,
                  overrides={"dep": {"tiers": {778: [1] * 3 + [3] * 2, 779: [1] * 5}, "cost": 30.0, "certviol": 0.02}})
    out, _ = run(layout, "--calfrac-dir", "0.25", str(layout / "cf025"))
    e11 = {r["dataset"]: r for r in rows(out / "TABLE_E11_calfrac.csv")}
    a, b = e11["toy"], e11["toy2"]
    assert a["key"] == "dep"
    # n_k: round(500.2 * 0.25 / 0.5) = 250 on split 778 (k* = 2), round(400 * 0.5) = 200 on 779 (k* = 1)
    assert float(a["n_k_cf0.25"]) == 225.0 and float(a["n_k_cf0.5"]) == 450.0
    assert float(a["pred_tier1_cf0.25"]) == pytest.approx(
        (M.pred_certify(250, 0.12, 0.15, LEVEL) + M.pred_certify(200, 0.05, 0.15, LEVEL)) / 2)
    # conditional on the pool: n_cal = round(0.25 * 6000); N_k / E_k from the audit (1000 / 120 on 778, 800 / 40 on 779)
    assert float(a["pred_tier1_hyper_cf0.25"]) == pytest.approx(
        (M.pred_certify_hyper(6000, 1000, 120, 1500, 0.15, LEVEL) + M.pred_certify_hyper(6000, 800, 40, 1500, 0.15, LEVEL)) / 2)
    assert float(a["pred_tier1_hyper_cf0.5"]) == pytest.approx(
        (M.pred_certify_hyper(6000, 1000, 120, 3000, 0.15, LEVEL) + M.pred_certify_hyper(6000, 800, 40, 3000, 0.15, LEVEL)) / 2)
    assert int(a["n_draws_cf0.25"]) == 10 and int(a["n_draws_cf0.5"]) == 40
    assert float(a["tier1_cf0.25"]) == pytest.approx(0.8) and float(a["tier1_cf0.5"]) == pytest.approx(0.75)
    assert float(a["cost_over_T_cf0.25"]) == pytest.approx(30.0 / 40) and float(a["cost_over_T_cf0.5"]) == pytest.approx(0.5)
    assert float(a["certified_violation_cf0.25"]) == pytest.approx(0.02)
    tbd = [c for c in a if c.endswith("_cf1.0")]
    assert len(tbd) == len(M.E11_METRICS) and all(a[c] == M.TBD for c in tbd)      # 1.0 was not run
    assert all(b[c] == M.TBD for c in b if c.endswith("_cf0.25"))                  # no 0.25 file for toy2
    assert b["tier1_cf0.5"] != M.TBD
    e11md = (out / "TABLE_E11_calfrac.md").read_text(encoding="utf-8")
    assert "1 draw per split" in e11md and "pred_tier1_hyper_cf0.25" in e11md and "unconditional" in e11md
    # the cal_frac points: separate CSV with scaled n_k, separate summary statistics
    cf = rows(out / "TABLE_E10_margin_calfrac.csv")
    assert len(cf) == 4 and all(float(r["cal_frac"]) == 0.25 for r in cf)
    assert int(find(cf, "toy", "0.5", 778)["n_k"]) == 1000                        # round(2000.6 * 0.5)
    assert len(rows(out / "TABLE_E10_margin.csv")) == 6                           # main table unchanged
    s = json.loads((out / "TABLE_E10_margin_summary.json").read_text(encoding="utf-8"))
    assert s["n_points"] == 6 and s["calfrac"]["0.25"]["n"] == 4 and s["all_with_calfrac"]["n"] == 10


def test_calfrac_mismatch_with_meta_raises(layout):
    write_metrics(layout / "cf", CELL_A, cal_frac=0.25)
    with pytest.raises(ValueError, match="cal_frac"):
        run(layout, "--calfrac-dir", "1.0", str(layout / "cf"))


def test_commit_mismatch_raises(layout):
    write_commit(layout / "configs", CELL_A, edges_override={"dep": [0.25, 0.5]})
    with pytest.raises(ValueError, match="edges"):
        run(layout)


@pytest.mark.parametrize("edges, expected", [([0.3], [300.0, 780.0]),       # commit G = 2, metrics G = 1
                                             ([], [300.0, 780.0])])          # same edges, commit G = 2
def test_commit_edges_shape_or_g_mismatch_raises(tmp_path, edges, expected):
    # np.allclose([], [0.3]) is True (broadcasting): the shapes and G must be compared, else the G = 1 metrics
    # would silently take n_k from the commit's stratum 0
    write_metrics(tmp_path / "metrics", CELL_C)
    write_commit(tmp_path / "configs", CELL_C, edges_override={"dep": edges}, expected_override={"dep": expected})
    with pytest.raises(ValueError, match="edges / G"):
        run(tmp_path)


def test_g1_commit_match_runs(tmp_path):
    write_metrics(tmp_path / "metrics", CELL_C)
    write_commit(tmp_path / "configs", CELL_C)
    out, _ = run(tmp_path)
    r = find(rows(out / "TABLE_E10_margin.csv"), "toy3", "dep", 778)
    assert (int(r["k_star"]), int(r["n_k"]), int(r["n_k_calpool"])) == (0, 1080, 2160)


def test_missing_scheme_is_na_not_tbd(tmp_path):
    # cell A has the inverse_info scheme, cell B only uniform: B's E11 entries are "n/a (no scheme)", not TBD-RUN
    write_metrics(tmp_path / "metrics", CELL_A, schemes=("uniform", "inverse_info"))
    write_metrics(tmp_path / "metrics", CELL_B)
    for cell in (CELL_A, CELL_B):
        write_commit(tmp_path / "configs", cell)
    out, _ = run(tmp_path, "--scheme", "inverse_info")
    assert {r["dataset"] for r in rows(out / "TABLE_E10_margin.csv")} == {"toy"}
    e11 = {r["dataset"]: r for r in rows(out / "TABLE_E11_calfrac.csv")}
    a, b = e11["toy"], e11["toy2"]
    assert all(b[f"{m}_cf0.5"] == M.NA_E11 == "n/a (no scheme)" for m in M.E11_METRICS)
    assert all(b[c] == M.TBD for c in b if c.endswith(("_cf0.25", "_cf1.0")))      # no file: still TBD-RUN
    assert a["tier1_cf0.5"] not in (M.TBD, M.NA_E11)
    md = (out / "TABLE_E11_calfrac.md").read_text(encoding="utf-8")
    assert "n/a (no scheme): the metrics file exists" in md and "| toy2 | random | 1 | dep | TBD-RUN | n/a (no scheme) | TBD-RUN |" in md
