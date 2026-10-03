"""v3 round 3 (Task K) -- ex-post stratum-safe oracles and the ``--cal-frac`` option of run_cascade_sweep.

* selection helpers on hand-made ``[strata x grid]`` arrays with known answers:
  :func:`run_cascade_sweep.stratum_safe_oracle` returns the cheapest threshold that is safe in every
  K_cal stratum (the overall cheapest one is unsafe in one stratum; cheapest is not the smallest index;
  ties -> smallest index; strata outside K_cal are not constrained) and ``None`` when no threshold is
  safe; :func:`stratum_safe_mondrian` selects per stratum (``None`` = abstain); the per-stratum rule
  puts abstained strata at full acquisition (depth T, whose cost / loss differ from the top grid
  column's in the hand-made split); cost order Mondrian-safe <= common-safe <= full acquisition;
* sweep integration on two synthetic pool caches (pattern of tests/test_v3_scripts.py): ``typeII``
  (stratum 1 is unsafe even at full information on most splits -> infeasible oracle) and ``feasible``;
  in both, every 100th row has score 1.0 from depth 0, so the top grid column (1.0) stops those rows
  before T and is cheaper than full acquisition, as on the real caches.
  Both baselines are in every draw with the documented keys, after the round-2 baselines (insertion
  order kept); the summary has ``feasible_rate``, ``cascade_cost_over_oracle``,
  ``cascade_cost_over_oracle_feasible`` (recomputed from the feasible draws) and
  ``cascade_cost_over_safe_mondrian_oracle`` (pooled and by_split); the recorded lambdas are recomputed
  independently from the cache arrays (safe in every K_cal stratum, no cheaper safe grid column, the
  calpool risks); infeasible records are full acquisition (``cc[:, T]``, not the top grid column); the
  cost order holds on every draw whose test strata lie in K_cal;
* ``--cal-frac``: a default run records ``meta.cal_frac`` 0.5; 1.0 runs one draw per split, each the
  whole calibration pool (the recorded cascade equals ``certify_or_route`` on the whole pool), and so
  does 0.25 on its own draws; ``n_draws`` != number of splits at 1.0, a non-default value without
  ``out_dir``, values outside (0, 1] and a value whose calibration draw would be empty raise; 0.25
  draws are nested in the 0.5 draws; ``main()`` passes ``--cal-frac`` through.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import commit_v3  # noqa: E402
import make_synthetic_pool_cache  # noqa: E402
import run_cascade_sweep as rcs  # noqa: E402
from cafa import config  # noqa: E402
from cafa.cascade import certify_or_route  # noqa: E402
from cafa.metrics import reference_buckets, stops_from_grid_np  # noqa: E402
from cafa.pool import cum_cost_from_order, load_pool_cache, save_pool_cache  # noqa: E402
from cafa.splits_v3 import calibration_draw, split_draw_id, v3_positions_multi  # noqa: E402

CFG_PATH = str(REPO / "configs" / "experiment_v3.yaml")
POLICY = "greedy_entropy"
ROUND2_BASELINES = ["plugin", "fixed_conf_0.9", "fixed_conf_0.95", "fixed_conf_0.99", "budget_0.25", "budget_0.5",
                    "budget_0.75", "full_acquisition", "mondrian_oracle", "oracle_cheapest_valid"]
SAFE_KEYS = {"lambda", "lambda_idx", "feasible", "calpool_stratum_risk", "calpool_stratum_n", "test_risk", "test_cost",
             "stratum_violation", "stratum_test_pvalue_min", "stratum_certified_violation", "stratum_max_excess_se"}
SMON_KEYS = {"feasible", "lambda_by_stratum", "abstained_fraction", "test_risk", "test_cost", "stratum_violation",
             "stratum_test_pvalue_min", "stratum_certified_violation", "stratum_max_excess_se"}


# --------------------------------------------------------------------------- #
# hand-made arrays
# --------------------------------------------------------------------------- #

def test_safe_oracle_cheapest_safe_lambda_known_answer():
    strata = [0, 1, 2]
    R = np.array([[0.30, 0.10, 0.05, 0.02, 0.01],      # stratum 0: unsafe only at column 0
                  [0.05, 0.25, 0.08, 0.01, 0.00],      # stratum 1: unsafe only at column 1
                  [0.50, 0.50, 0.50, 0.50, 0.50]])     # stratum 2: never safe (outside K_cal below)
    cost = np.array([1.0, 2.0, 4.0, 3.0, 5.0])         # not monotone: column 3 is cheaper than column 2
    # the overall cheapest column 0 is unsafe in stratum 0, column 1 in stratum 1; 3 is cheaper than 2
    assert rcs.stratum_safe_oracle(R, cost, strata, [0, 1], 0.10) == 3
    assert rcs.stratum_safe_oracle(R, cost, strata, [1], 0.10) == 0          # stratum 0 unconstrained
    assert rcs.stratum_safe_oracle(R, cost, strata, [0], 0.10) == 1          # risk == alpha qualifies
    assert rcs.stratum_safe_oracle(R, cost, strata, [0, 1, 7], 0.10) == 3    # K_cal label without test rows
    assert rcs.stratum_safe_oracle(R, cost, strata, [7], 0.10) == 0          # nothing to constrain
    tie = np.array([1.0, 2.0, 3.0, 3.0, 5.0])
    assert rcs.stratum_safe_oracle(R, tie, strata, [0, 1], 0.10) == 2        # tie -> smallest index
    # per-stratum (Mondrian) selection on the same matrix, stratum costs = column costs
    C = np.tile(cost, (3, 1))
    assert rcs.stratum_safe_mondrian(R, C, strata, 0.10) == {0: 1, 1: 0, 2: None}
    # stratum_means: per-label column means in sorted label order
    mat = np.array([[1.0, 0.0], [0.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    ks, M = rcs.stratum_means(mat, np.array([3, 1, 3, 1]))
    assert ks == [1, 3] and np.allclose(M, [[0.0, 0.5], [1.0, 0.5]])


def test_safe_oracle_infeasible_returns_none():
    R = np.array([[0.30, 0.20, 0.15], [0.05, 0.02, 0.01]])
    cost = np.array([1.0, 2.0, 3.0])
    assert rcs.stratum_safe_oracle(R, cost, [0, 1], [0, 1], 0.10) is None
    assert rcs.stratum_safe_oracle(R, cost, [0, 1], [1], 0.10) == 0
    assert rcs.stratum_safe_mondrian(R, np.tile(cost, (2, 1)), [0, 1], 0.10) == {0: None, 1: 0}


def _toy_test_split():
    """6 test rows, 2 strata, T = 2, 3 grid columns.  Full acquisition (depth T) differs from the top grid
    column (as when a score reaches 1.0 before T): cost 3 vs. 2 on every row, and row 1 is wrong at depth T
    but right at the top grid column."""
    bid = np.array([0, 0, 0, 1, 1, 1])
    losses = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0],      # stratum 0: risk 1/3 at column 0
                       [0, 1, 0], [0, 0, 0], [0, 0, 0]], float)  # stratum 1: risk 1/3 at column 1
    costs = np.tile([0.0, 1.0, 2.0], (6, 1))
    correct = np.array([[0, 1, 1], [0, 1, 0]] + [[0, 1, 1]] * 4, float)
    cum_cost = np.tile([0.0, 1.0, 3.0], (6, 1))
    return bid, losses, costs, correct, cum_cost


def test_cost_order_mondrian_safe_le_common_safe_le_full():
    bid, losses, costs, correct, cum_cost = _toy_test_split()
    tk, R = rcs.stratum_means(losses, bid)
    _, C = rcs.stratum_means(costs, bid)
    js = rcs.stratum_safe_oracle(R, costs.mean(axis=0), tk, [0, 1], 0.2)
    jk = rcs.stratum_safe_mondrian(R, C, tk, 0.2)
    assert js == 2 and jk == {0: 1, 1: 0}
    ps_, agg, mon_cost, cn, abst = rcs.per_stratum_rule_risks(jk, losses, costs, correct, cum_cost, 2, bid)
    assert mon_cost == pytest.approx(0.5) and agg == 0.0 and abst == 0
    assert ps_ == {0: 0.0, 1: 0.0} and cn == {0: (0, 3), 1: (0, 3)}
    full = cum_cost[:, 2].mean()
    assert mon_cost <= costs[:, js].mean() <= full
    # an abstaining stratum is at full acquisition (depth T: cost 3, row 1 wrong), as in the Mondrian oracle --
    # not at the top grid column (cost 2, no error there)
    ps_, agg, cost, cn, abst = rcs.per_stratum_rule_risks({0: None, 1: 0}, losses, costs, correct, cum_cost, 2, bid)
    assert abst == 3 and cost == pytest.approx((3 * 3.0 + 3 * 0.0) / 6) and cost != pytest.approx((3 * 2.0) / 6)
    assert ps_[0] == pytest.approx(1 / 3) and cn[0] == (1, 3) and agg == pytest.approx(1 / 6)
    assert ps_[1] == 0.0 and cn[1] == (0, 3)


# --------------------------------------------------------------------------- #
# sweep integration on synthetic pool caches
# --------------------------------------------------------------------------- #

SATURATED_EVERY = 100    # every 100th cache row gets score 1.0 from depth 0 (see _saturate)


def _saturate(path):
    """Rows 0, 100, 200, ... of the cache at ``path`` get score 1.0 from depth 0: they stop at depth 0 at every
    grid threshold (the top one, 1.0, included), so the top grid column is cheaper than full acquisition
    (depth T) -- as on the real caches, where up to ~14% of the rows reach 1.0 before T."""
    c = load_pool_cache(path)
    scores = np.array(c["scores"], dtype=float)
    scores[::SATURATED_EVERY] = 1.0
    save_pool_cache(path, scores=scores, correct=c["correct"], order=c["order"], y=c["y"], row_pos=c["row_pos"],
                    meta=c["meta"])


@pytest.fixture(scope="module")
def cells(tmp_path_factory):
    cfg = config.load_experiment(CFG_PATH)
    out = {"cfg": cfg}
    for scen in ("typeII", "feasible"):
        root = tmp_path_factory.mktemp(f"oracles_{scen}")
        pool = root / "pool_v3"
        assert make_synthetic_pool_cache.main(["--pool-dir", str(pool), "--n", "3000", "--scenario", scen]) == 0
        _saturate(pool / f"synthetic-planted_ts0_{POLICY}_softmax.npz")      # before committing
        committed = root / "committed.json"
        assert commit_v3.commit(dataset="synthetic-planted", train_seed=0, score="softmax", pool_dir=pool,
                                out_path=committed, cfg=cfg, force=True) == 0
        op = rcs.run_one("synthetic-planted", POLICY, "softmax", 0, cfg=cfg, paths=None, n_draws=10,
                         pool_dir=pool, out_dir=root / "metrics_v3", committed_path=committed)
        out[scen] = {"root": root, "pool": pool, "committed": committed,
                     "commit": json.loads(committed.read_text()), "metrics": json.loads(Path(op).read_text())}
    return out


def _split_arrays(cell, cfg, key, seed, cal_frac=None, draw=None):
    """Independent recomputation from the cache: per part (test / calpool / a calibration draw) the
    stop-loss and cost matrices, strata (commit edges), correct and cumulative costs."""
    com = cell["commit"]
    sp = com["split"]
    cache = load_pool_cache(cell["pool"] / f"synthetic-planted_ts0_{POLICY}_softmax.npz")
    S_all, C_all = np.asarray(cache["scores"]), np.asarray(cache["correct"])
    pos = {p["test_seed"]: p for p in v3_positions_multi(S_all.shape[0], sp["probe_frac"], sp["probe_seed"],
                                                       sp["test_frac_of_eval"], sp["test_seeds"])}[int(seed)]
    cc_all = cum_cost_from_order(cache["order"], np.asarray(com["feature_costs_by_scheme"]["uniform"], float))
    lr = float(com["lambda_refs"][POLICY][key])
    edges = np.asarray(com["edges"][POLICY][key]["edges"], float)
    grid = commit_v3.build_grid(cfg["method"])
    parts = {"test": pos["test"], "calpool": pos["calpool"]}
    if draw is not None:   # the draw's positions, in calpool order (as the sweep indexes its calpool arrays)
        parts["cal"] = pos["calpool"][np.isin(pos["calpool"], calibration_draw(pos["calpool"], draw, cal_frac))]
    out = {"grid": grid, "pos": pos}
    for name, p in parts.items():
        S, C, cc = S_all[p], C_all[p], cc_all[p]
        losses, costs, _ = stops_from_grid_np(S, C, cc, grid)
        bid, _ = reference_buckets(S, lr, 5, 1, edges=edges)
        out[name] = {"S": S, "C": C, "cc": cc, "losses": losses, "costs": costs, "bid": bid}
    return out


def _risk_by_stratum(part):
    """``{k: [G] test risk of every grid column}`` for the strata of one part."""
    return {int(k): part["losses"][part["bid"] == k].mean(axis=0) for k in np.unique(part["bid"])}


@pytest.mark.parametrize("scen", ["typeII", "feasible"])
def test_sweep_records_and_summary_fields(cells, scen):
    m = cells[scen]["metrics"]
    assert m["meta"]["cal_frac"] == 0.5 and "cal_frac_note" not in m["meta"]           # default recorded
    n_ratio = n_none = 0
    for blk in m["lambda_refs"].values():
        for sch in blk["schemes"].values():
            draws, summ = sch["draws"], sch["summary"]
            for d in draws:
                bl = d["baselines"]
                assert list(bl) == ROUND2_BASELINES + ["oracle_stratum_safe", "oracle_stratum_safe_mondrian"]
                assert set(bl["oracle_stratum_safe"]) == SAFE_KEYS
                assert set(bl["oracle_stratum_safe_mondrian"]) == SMON_KEYS
            for split, s in [(None, summ)] + list(summ["by_split"].items()):
                sel = [d for d in draws if split is None or str(d["split_seed"]) == split]
                for name in ("oracle_stratum_safe", "oracle_stratum_safe_mondrian"):
                    b = s["baselines"][name]
                    assert b["n"] == len(sel)
                    assert b["feasible_rate"] == pytest.approx(np.mean([d["baselines"][name]["feasible"] for d in sel]))
                    assert b["mean_test_cost"] == pytest.approx(np.mean([d["baselines"][name]["test_cost"] for d in sel]))
                assert s["cascade_cost_over_oracle"] == pytest.approx(
                    s["cascade_mean_test_cost"] / s["baselines"]["oracle_stratum_safe"]["mean_test_cost"])
                assert s["cascade_cost_over_safe_mondrian_oracle"] == pytest.approx(
                    s["cascade_mean_test_cost"] / s["baselines"]["oracle_stratum_safe_mondrian"]["mean_test_cost"])
                # the ratio over only the draws whose oracle_stratum_safe is feasible (None if none / oracle cost 0)
                fe = [d for d in sel if d["baselines"]["oracle_stratum_safe"]["feasible"]]
                den = np.mean([d["baselines"]["oracle_stratum_safe"]["test_cost"] for d in fe]) if fe else 0.0
                if den:
                    exp = np.mean([d["cascade"]["test_cost"] for d in fe]) / den
                    assert s["cascade_cost_over_oracle_feasible"] == pytest.approx(exp)
                    n_ratio += 1
                    if len(fe) == len(sel):   # every draw feasible: the two ratios coincide
                        assert s["cascade_cost_over_oracle_feasible"] == pytest.approx(s["cascade_cost_over_oracle"])
                else:
                    assert s["cascade_cost_over_oracle_feasible"] is None
                    n_none += 1
                # round-2 baselines carry no ``feasible`` -> no feasible_rate
                assert all("feasible_rate" not in s["baselines"][n] for n in ROUND2_BASELINES)
    # the feasible-draws ratio is exercised: a value in both scenarios, None where no draw is feasible (typeII)
    assert n_ratio > 0 and ((n_none > 0) if scen == "typeII" else True)


@pytest.mark.parametrize("scen", ["typeII", "feasible"])
def test_sweep_oracle_lambdas_recomputed_from_cache(cells, scen):
    cell, cfg = cells[scen], cells["cfg"]
    m = cell["metrics"]
    alpha, T = m["alpha"], m["meta"]["T"]
    n_feas = n_infeas = 0
    for key, blk in m["lambda_refs"].items():
        draws = blk["schemes"]["uniform"]["draws"]
        for seed in sorted({d["split_seed"] for d in draws}):
            a = _split_arrays(cell, cfg, key, seed)
            t, cp, grid = a["test"], a["calpool"], a["grid"]
            rk = _risk_by_stratum(t)
            tks = sorted(rk)
            col_cost = t["costs"].mean(axis=0)
            for d in [d for d in draws if d["split_seed"] == seed]:
                o, full = d["baselines"]["oracle_stratum_safe"], d["baselines"]["full_acquisition"]
                ks = [k for k in d["cascade"]["k_cal"] if k in tks]
                safe_cols = [j for j in range(grid.size) if all(rk[k][j] <= alpha for k in ks)]
                if o["feasible"]:
                    n_feas += 1
                    j = o["lambda_idx"]
                    assert o["lambda"] == float(grid[j]) and j in safe_cols
                    # no cheaper safe column; equally cheap safe columns only at larger indices
                    assert all(col_cost[jj] > col_cost[j] or (col_cost[jj] == col_cost[j] and jj >= j) for jj in safe_cols)
                    assert o["test_cost"] == pytest.approx(col_cost[j])
                    assert o["test_risk"] == pytest.approx(t["losses"][:, j].mean())
                    pks = [int(k) for k in np.unique(cp["bid"])]
                    assert sorted(o["calpool_stratum_risk"]) == sorted(o["calpool_stratum_n"]) == sorted(str(k) for k in pks)
                    for k in pks:
                        assert o["calpool_stratum_risk"][str(k)] == pytest.approx(cp["losses"][cp["bid"] == k, j].mean())
                        assert o["calpool_stratum_n"][str(k)] == int((cp["bid"] == k).sum())
                else:
                    n_infeas += 1
                    assert safe_cols == []
                    assert o["lambda"] is None and o["lambda_idx"] is None
                    assert o["calpool_stratum_risk"] is None and o["calpool_stratum_n"] is None
                    assert o["test_cost"] == pytest.approx(t["cc"][:, T].mean()) == pytest.approx(full["test_cost"])
                    # ... and not the top grid column (1.0), which stops the saturated rows at depth 0
                    assert t["costs"][:, -1].mean() < t["cc"][:, T].mean() - 1e-6
                    assert o["test_cost"] != pytest.approx(t["costs"][:, -1].mean())
                    assert o["test_risk"] == pytest.approx(1.0 - t["C"][:, T].mean()) == pytest.approx(full["test_risk"])
                # Mondrian-safe: per test stratum the cheapest safe column, full acquisition where none
                mo = d["baselines"]["oracle_stratum_safe_mondrian"]
                assert sorted(mo["lambda_by_stratum"]) == sorted(str(k) for k in tks)
                cost_sum, abst = 0.0, 0
                for k in tks:
                    mk = t["bid"] == k
                    sc = [j for j in range(grid.size) if rk[k][j] <= alpha]
                    lam = mo["lambda_by_stratum"][str(k)]
                    if lam is None:
                        assert sc == []
                        cost_sum += t["cc"][mk, T].sum()
                        abst += int(mk.sum())
                    else:
                        j = int(np.flatnonzero(grid == lam)[0])
                        kc = t["costs"][mk].mean(axis=0)
                        assert j in sc and all(kc[jj] > kc[j] or (kc[jj] == kc[j] and jj >= j) for jj in sc)
                        cost_sum += t["costs"][mk, j].sum()
                assert mo["test_cost"] == pytest.approx(cost_sum / t["bid"].size)
                assert mo["abstained_fraction"] == pytest.approx(abst / t["bid"].size)
                assert mo["feasible"] == all(v is not None for v in mo["lambda_by_stratum"].values())
    # both branches are exercised: typeII is mostly infeasible, the feasible scenario is feasible
    assert (n_infeas > 0) if scen == "typeII" else (n_feas > 0)


@pytest.mark.parametrize("scen", ["typeII", "feasible"])
def test_sweep_cost_order(cells, scen):
    n_checked = 0
    for blk in cells[scen]["metrics"]["lambda_refs"].values():
        sizes = blk["strata_test_sizes_by_split"]
        for sch in blk["schemes"].values():
            for d in sch["draws"]:
                if not {int(k) for k in sizes[str(d["split_seed"])]} <= set(d["cascade"]["k_cal"]):
                    continue
                b = d["baselines"]
                smon, safe, full = (b["oracle_stratum_safe_mondrian"]["test_cost"], b["oracle_stratum_safe"]["test_cost"],
                                    b["full_acquisition"]["test_cost"])
                assert smon <= safe + 1e-9 and safe <= full + 1e-9
                n_checked += 1
    assert n_checked > 0


# --------------------------------------------------------------------------- #
# --cal-frac
# --------------------------------------------------------------------------- #

def _cascade_matches_recomputation(cell, cfg, m, key, cal_frac):
    """Every recorded cascade of ``key`` equals certify_or_route on its recomputed calibration draw."""
    com = cell["commit"]
    esc = com["escalation"][POLICY][key]
    mu = np.asarray(esc["mu_asc"], float)
    order = np.asarray(esc.get("order", []), int)
    for d in m["lambda_refs"][key]["schemes"]["uniform"]["draws"]:
        a = _split_arrays(cell, cfg, key, d["split_seed"], cal_frac=cal_frac, draw=d["draw"])
        c = a["cal"]
        exp_n = int(round(cal_frac * a["pos"]["calpool"].size))
        assert c["S"].shape[0] == exp_n
        if cal_frac == 1.0:
            assert set(np.asarray(calibration_draw(a["pos"]["calpool"], d["draw"], 1.0)).tolist()) == \
                set(a["pos"]["calpool"].tolist())
        res = certify_or_route(c["S"], c["C"], c["cc"], a["grid"], mu, m["alpha"], m["delta"], c["bid"],
                               tuple(m["delta_weights"]), escalation_order=order if order.size else None)
        rec = d["cascade"]
        assert (rec["tier"], rec["rule"], rec["k_cal"]) == (int(res.tier), res.rule, [int(k) for k in res.k_cal])
        assert rec["param"] == (None if res.param_value is None else pytest.approx(float(res.param_value)))
        assert rec["tiers_certified"] == {n: bool(t.certified) for n, t in res.tiers.items()}


def test_cal_frac_one_runs_one_draw_per_split_on_the_whole_pool(cells, tmp_path, capsys):
    cell, cfg = cells["feasible"], cells["cfg"]
    op = rcs.run_one("synthetic-planted", POLICY, "softmax", 0, cfg=cfg, paths=None, pool_dir=cell["pool"],
                     out_dir=tmp_path, committed_path=cell["committed"], cal_frac=1.0)
    out = capsys.readouterr().out
    assert "1 draw per split" in out and "cal_frac=1.0" in out
    m = json.loads(Path(op).read_text())
    seeds = cell["commit"]["split"]["test_seeds"]
    assert m["meta"]["n_draws"] == len(seeds) == 5 and m["meta"]["draws_per_split"] == 1
    assert m["meta"]["cal_frac"] == 1.0 and "whole calibration pool" in m["meta"]["cal_frac_note"]
    for blk in m["lambda_refs"].values():
        draws = blk["schemes"]["uniform"]["draws"]
        assert [d["draw"] for d in draws] == [split_draw_id(i, 0) for i in range(len(seeds))]
        assert blk["schemes"]["uniform"]["summary"]["cascade_cost_over_oracle"] is not None
    _cascade_matches_recomputation(cell, cfg, m, "dep", 1.0)


def test_cal_frac_quarter_uses_its_own_draws(cells, tmp_path, capsys):
    cell, cfg = cells["feasible"], cells["cfg"]
    op = rcs.run_one("synthetic-planted", POLICY, "softmax", 0, cfg=cfg, paths=None, n_draws=5, pool_dir=cell["pool"],
                     out_dir=tmp_path, committed_path=cell["committed"], cal_frac=0.25)
    assert "cal_frac=0.25" in capsys.readouterr().out
    m = json.loads(Path(op).read_text())
    assert m["meta"]["cal_frac"] == 0.25 and m["meta"]["n_draws"] == 5 and "cal_frac_note" not in m["meta"]
    _cascade_matches_recomputation(cell, cfg, m, "dep", 0.25)


def test_cal_frac_guards(cells, tmp_path):
    cell, cfg = cells["typeII"], cells["cfg"]
    kw = dict(cfg=cfg, paths=None, pool_dir=cell["pool"], committed_path=cell["committed"])
    with pytest.raises(ValueError, match="number of splits"):
        rcs.run_one("synthetic-planted", POLICY, "softmax", 0, n_draws=10, out_dir=tmp_path, cal_frac=1.0, **kw)
    with pytest.raises(RuntimeError, match="out-dir"):                    # canonical file never overwritten
        rcs.run_one("synthetic-planted", POLICY, "softmax", 0, n_draws=5, cal_frac=0.25, **kw)
    for bad in (0.0, -0.1, 1.5):
        with pytest.raises(ValueError, match="cal_frac"):
            rcs.run_one("synthetic-planted", POLICY, "softmax", 0, n_draws=5, out_dir=tmp_path, cal_frac=bad, **kw)
    # in (0, 1] but round(cal_frac * n_calpool) = 0 on the calibration pools: an empty calibration draw
    sp = cell["commit"]["split"]
    n_cp = [p["calpool"].size for p in v3_positions_multi(3000, sp["probe_frac"], sp["probe_seed"],
                                                          sp["test_frac_of_eval"], sp["test_seeds"])]
    assert max(int(round(1e-4 * n)) for n in n_cp) == 0
    with pytest.raises(ValueError, match=r"cal_frac 0\.0001 .*calibration pool of split \d+ \(\d+ rows\)") as ei:
        rcs.run_one("synthetic-planted", POLICY, "softmax", 0, n_draws=5, out_dir=tmp_path, cal_frac=1e-4, **kw)
    assert int(re.search(r"\((\d+) rows\)", str(ei.value)).group(1)) in n_cp      # the pool size is named
    assert not list(tmp_path.iterdir())                                     # nothing was written


def test_cal_frac_quarter_draws_nested_in_half_draws():
    for p in v3_positions_multi(3000, 0.10, 777, 0.5, [778, 779, 780, 781, 782]):
        for dd in (0, 7, 19):
            d = split_draw_id(p["split_index"], dd)
            q, h = calibration_draw(p["calpool"], d, 0.25), calibration_draw(p["calpool"], d, 0.5)
            assert np.array_equal(q, h[:q.size]) and set(q.tolist()) < set(h.tolist())


def test_main_passes_cal_frac(monkeypatch):
    seen = []
    monkeypatch.setattr(rcs, "run_one", lambda *a, **k: seen.append(k))
    monkeypatch.setattr(rcs.config, "load_paths", lambda *a, **k: None)
    base = ["--dataset", "synthetic-planted", "--config", CFG_PATH, "--out-dir", "unused"]
    assert rcs.main(base + ["--cal-frac", "0.25"]) == 0
    assert rcs.main(base) == 0
    assert seen[0]["cal_frac"] == 0.25 and seen[1]["cal_frac"] is None
