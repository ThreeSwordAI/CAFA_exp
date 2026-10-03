"""v3 round 2 -- multi-split protocol and noise-aware violation metrics.

* splits: 5 calpool / test splits of the eval remainder (same probe), each disjoint, covering and
  deterministic; split 778 is the round-1 split;
* draw ids ``split_index * 1000 + d``: distinct across splits (so are the RNG seeds); split index 0
  reuses the round-1 ids; ``n_draws`` must divide over the splits;
* commit invariance: a re-commit with the round-2 code changes nothing outside the ``split`` block
  (vs. the round-2 Task-A code) and outside ``split`` and ``escalation.*.order`` (vs. the round-1 code,
  where the order changes only because of the HB fix); the fixtures are commits of the same
  deterministic synthetic cache made with the older code (see their ``fixture_note``);
* sweep: per-draw split fields, ``by_split`` summaries, ``audit_by_split`` and the noise-aware fields
  recomputed from the recorded test counts;
* a small version of planted study D: true violation <= delta and certified violation <= delta + 0.05
  (+ sampling slack).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import commit_v3  # noqa: E402
import make_synthetic_pool_cache  # noqa: E402
import planted_validation  # noqa: E402
import run_cascade_sweep  # noqa: E402
from cafa import config  # noqa: E402
from cafa.localization import binom_upper_p  # noqa: E402
from cafa.splits_v3 import (  # noqa: E402
    DRAW_OFFSET,
    calibration_draw,
    draws_per_split,
    split_draw_id,
    v3_positions,
    v3_positions_multi,
)

CFG_PATH = str(REPO / "configs" / "experiment_v3.yaml")
SEEDS = [778, 779, 780, 781, 782]
FIXTURES = REPO / "tests" / "fixtures"
# leaves that legitimately differ between two commits of the same cache: timestamps and the temp pool path
VOLATILE = {"/created", "/pool_dir", "/cache_meta/created", "/fixture_note (removed)"}


def test_config_protocol():
    cfg = config.load_experiment(CFG_PATH)
    pv = cfg["protocol_v3"]
    assert pv["test_seeds"] == SEEDS and pv["test_seed"] == SEEDS[0]
    assert pv["n_draws"] == 100 and draws_per_split(pv["n_draws"], len(pv["test_seeds"])) == 20


def test_positions_multi_disjoint_cover_deterministic():
    n = 10_001
    a = v3_positions_multi(n, test_seeds=SEEDS)
    b = v3_positions_multi(n, test_seeds=SEEDS)
    assert [p["test_seed"] for p in a] == SEEDS and [p["split_index"] for p in a] == list(range(5))
    for pa, pb in zip(a, b):
        for k in ("probe", "calpool", "test"):
            assert np.array_equal(pa[k], pb[k])                                  # deterministic
        allp = np.concatenate([pa["probe"], pa["calpool"], pa["test"]])
        assert np.unique(allp).size == allp.size == n                             # disjoint and covering
        assert np.array_equal(pa["probe"], a[0]["probe"])                         # one probe for all splits
        assert pa["calpool"].size == a[0]["calpool"].size                         # n_cal_expected split-invariant
    single = v3_positions(n, test_seed=778)                                      # split 778 = the round-1 split
    assert np.array_equal(single["calpool"], a[0]["calpool"]) and np.array_equal(single["test"], a[0]["test"])
    cal_sets = [frozenset(p["calpool"].tolist()) for p in a]
    assert len(set(cal_sets)) == 5                                               # the splits differ


def test_draw_ids_distinct_and_round1_compatible():
    ids = [split_draw_id(s, d) for s in range(5) for d in range(20)]
    assert len(set(ids)) == 100
    assert len({DRAW_OFFSET + i for i in ids}) == 100                            # RNG seeds never reused
    assert ids[:20] == list(range(20))                                            # split 0 = round-1 draw ids
    with pytest.raises(ValueError):
        split_draw_id(1, 1000)
    with pytest.raises(ValueError):
        draws_per_split(100, 3)
    pos = v3_positions_multi(4000, test_seeds=SEEDS)
    draws = {}
    for p in pos:
        for d in range(20):
            cd = calibration_draw(p["calpool"], split_draw_id(p["split_index"], d))
            assert set(cd.tolist()) <= set(p["calpool"].tolist()) and not set(cd.tolist()) & set(p["test"].tolist())
            draws[(p["test_seed"], d)] = frozenset(cd.tolist())
    assert len(set(draws.values())) == 100


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    root = tmp_path_factory.mktemp("multisplit")
    pool = root / "pool_v3"
    assert make_synthetic_pool_cache.main(["--pool-dir", str(pool), "--n", "3000", "--scenario", "typeII"]) == 0
    cfg = config.load_experiment(CFG_PATH)
    committed = root / "committed.json"
    assert commit_v3.commit(dataset="synthetic-planted", train_seed=0, score="softmax", pool_dir=pool,
                            out_path=committed, cfg=cfg, force=True) == 0
    return {"root": root, "pool": pool, "cfg": cfg, "committed": committed,
            "commit": json.loads(committed.read_text())}


def test_commit_records_multisplit_block(synth):
    sp = synth["commit"]["split"]
    assert sp["test_seeds"] == SEEDS and sp["test_seed"] == 778
    assert sp["n_draws"] == 100 and sp["draws_per_split"] == 20 and sp["draw_id_stride"] == 1000
    assert sorted(sp["by_test_seed"]) == [str(s) for s in SEEDS]
    assert sp["by_test_seed"]["778"]["digest"] == {k: sp["digest"][k] for k in ("calpool", "test")}
    assert len({v["digest"]["test"] for v in sp["by_test_seed"].values()}) == 5


@pytest.mark.parametrize("fixture,allowed", [
    ("hbfix", ()),                       # Task-A code: only the split block may differ
    ("round1", ("/order",)),             # round-1 code: + the tier-3 order (HB fix, Task A)
])
def test_recommit_changes_only_split_block(synth, fixture, allowed):
    old = json.loads((FIXTURES / f"committed_synthetic_typeII_n3000_{fixture}.json").read_text())
    diffs = [d for d in commit_v3.diff_commits(old, synth["commit"]) if d not in VOLATILE]
    outside = [d for d in diffs if not d.startswith("/split/") and not any(d.endswith(x) for x in allowed)]
    assert outside == [], outside
    assert any(d.startswith("/split/") for d in diffs)                            # the split block did change
    if allowed:
        assert all(d.startswith("/escalation/") for d in diffs if d.endswith("/order"))
    # everything the round-1 split block recorded is unchanged (round 2 only adds keys)
    assert all(d.endswith("(added)") for d in diffs if d.startswith("/split/")), diffs


def test_sweep_multisplit_fields(synth, tmp_path):
    op = run_cascade_sweep.run_one("synthetic-planted", "greedy_entropy", "softmax", 0, cfg=synth["cfg"], paths=None,
                                   n_draws=10, pool_dir=synth["pool"], out_dir=tmp_path, committed_path=synth["committed"])
    m = json.loads(Path(op).read_text())
    alpha = m["alpha"]
    n_cert = 0
    assert m["meta"]["test_seeds"] == SEEDS and m["meta"]["draws_per_split"] == 2
    for blk in m["lambda_refs"].values():
        assert sorted(blk["audit_by_split"]) == [str(s) for s in SEEDS]
        assert blk["audit"] == blk["audit_by_split"]["778"]
        assert 1 <= blk["deepest_verdict_agreement"] <= 5 and blk["n_splits"] == 5
        for sch in blk["schemes"].values():
            draws, summ = sch["draws"], sch["summary"]
            assert [d["draw"] for d in draws] == [s * 1000 + d for s in range(5) for d in range(2)]
            assert [d["split_seed"] for d in draws] == [s for s in SEEDS for _ in range(2)]
            assert sorted(summ["by_split"]) == [str(s) for s in SEEDS]
            assert all(v["n_draws"] == 2 for v in summ["by_split"].values())
            assert summ["cascade_violation_rate"] == pytest.approx(
                np.mean([v["cascade_violation_rate"] for v in summ["by_split"].values()]))
            assert summ["cascade_certified_violation_rate"] == pytest.approx(
                np.mean([d["cascade"]["certified_violation"] for d in draws]))
            for d in draws:
                c = d["cascade"]
                ps, zs = [], []
                for k in c["k_cal"]:
                    e, n = c["test_errors_by_stratum"].get(str(k), 0), c["test_n_by_stratum"].get(str(k), 0)
                    if n:
                        ps.append(float(binom_upper_p(e, n, alpha)))
                        zs.append((e / n - alpha) / math.sqrt(alpha * (1 - alpha) / n))
                        if c["test_stratum_risk"].get(str(k)) is not None:
                            assert c["test_stratum_risk"][str(k)] == pytest.approx(e / n)
                assert (c["test_pvalue_min"] is None) == (not ps)
                if ps:
                    assert c["test_pvalue_min"] == pytest.approx(min(ps))
                    assert c["max_excess_se"] == pytest.approx(max(zs))
                assert c["certified_violation"] == bool(ps and min(ps) <= 0.05)
                if c["certified_violation"]:
                    assert c["violation"]                                         # certified implies raw
                # marginal: recompute the hidden_* fields from its per-stratum test risks and the split's sizes
                sizes = blk["strata_test_sizes_by_split"][str(d["split_seed"])]
                mg = d["marginal"]
                if "test_stratum_risk" in mg:
                    hp, hz = [], []
                    for k in c["k_cal"]:
                        if str(k) not in mg["test_stratum_risk"]:
                            continue
                        n = sizes[str(k)]
                        e = round(mg["test_stratum_risk"][str(k)] * n)
                        hp.append(float(binom_upper_p(e, n, alpha)))
                        hz.append((e / n - alpha) / math.sqrt(alpha * (1 - alpha) / n))
                    assert mg["hidden_test_pvalue_min"] == pytest.approx(min(hp))
                    assert mg["hidden_max_excess_se"] == pytest.approx(max(hz))
                    assert mg["hidden_certified_violation"] == (min(hp) <= 0.05)
                    if mg["hidden_certified_violation"]:
                        n_cert += 1
                        assert any(mg["test_stratum_risk"][str(k)] > alpha for k in c["k_cal"]
                                   if str(k) in mg["test_stratum_risk"])
                else:
                    assert mg["hidden_certified_violation"] is False and mg["hidden_test_pvalue_min"] is None
                for name, b in d["baselines"].items():
                    if "test_risk" in b:
                        assert {"stratum_certified_violation", "stratum_test_pvalue_min", "stratum_max_excess_se"} <= set(b)
                        assert b["stratum_certified_violation"] == bool(
                            b["stratum_test_pvalue_min"] is not None and b["stratum_test_pvalue_min"] <= 0.05)
                        if b["stratum_certified_violation"]:
                            n_cert += 1
                            assert b["stratum_violation"]                         # certified implies raw
                            assert b["stratum_max_excess_se"] > 0
            for name, bs in summ["baselines"].items():
                cv = [d["baselines"][name]["stratum_certified_violation"] for d in draws
                      if "test_risk" in d["baselines"][name]]
                if cv:
                    assert bs["stratum_certified_violation_rate"] == pytest.approx(np.mean(cv))
    assert n_cert > 0                                                             # the certified branches ran


def test_sweep_and_repair_refuse_stale_single_split_commit(synth, tmp_path):
    """A commit made before the multi-split protocol (no test_seeds) is not silently swept on one split."""
    stale = FIXTURES / "committed_synthetic_typeII_n3000_hbfix.json"
    with pytest.raises(RuntimeError, match="re-commit"):
        run_cascade_sweep.run_one("synthetic-planted", "greedy_entropy", "softmax", 0, cfg=synth["cfg"], paths=None,
                                  n_draws=5, pool_dir=synth["pool"], out_dir=tmp_path / "a", committed_path=stale)
    with pytest.raises(RuntimeError, match="out-dir"):                         # subset without its own out dir
        run_cascade_sweep.run_one("synthetic-planted", "greedy_entropy", "softmax", 0, cfg=synth["cfg"], paths=None,
                                  n_draws=5, pool_dir=synth["pool"], committed_path=stale, test_seeds=[778])
    op = run_cascade_sweep.run_one("synthetic-planted", "greedy_entropy", "softmax", 0, cfg=synth["cfg"], paths=None,
                                   n_draws=5, pool_dir=synth["pool"], out_dir=tmp_path / "b", committed_path=stale,
                                   test_seeds=[778])                              # deliberate single-split diagnostic
    assert json.loads(Path(op).read_text())["meta"]["test_seeds"] == [778]
    import repair_experiment
    cache = synth["pool"] / "synthetic-planted_ts0_greedy_entropy_softmax.npz"
    rc = repair_experiment.main(["--dataset", "synthetic-planted", "--before-cache", str(cache), "--after-cache", str(cache),
                                 "--committed", str(stale), "--config", CFG_PATH, "--n-draws", "5",
                                 "--output", str(tmp_path / "r.json")])
    assert rc == 2 and not (tmp_path / "r.json").exists()


def test_study_d_rule_helpers_match_apply_rule():
    """study D's rule evaluation (true and test risks) agrees with cafa.cascade.apply_rule for all three tiers."""
    from types import SimpleNamespace

    from cafa.cascade import apply_rule
    T = 30
    pop = planted_validation.make_planted_population(600, T, planted_validation.study_d_strata(T), seed=5)
    mu = np.array([0.5, 0.9, 0.99])
    for res in (SimpleNamespace(rule="threshold", param_idx=80, param_value=float(planted_validation.GRID[80])),
                SimpleNamespace(rule="budget", param_idx=7, param_value=7.0),
                SimpleNamespace(rule="escalation", param_idx=2, param_value=float(mu[2]))):
        ap = apply_rule(res, pop["scores"], pop["correct"], pop["cum_cost"], planted_validation.GRID, mu, pop["stratum"])
        got = planted_validation._per_stratum(pop, res, 1.0 - pop["correct"])
        for k, v in ap["per_stratum"].items():
            e, n = got[int(k)]
            assert n == round(v["answered_fraction"] * v["n"])
            if n:
                assert e / n == pytest.approx(v["risk"])


def test_study_d_expected_rates_match_enumeration():
    from scipy.stats import binom
    alpha = planted_validation.ALPHA
    for n, R in ((300, 0.146), (2500, 0.146), (2491, 0.149)):
        e = np.arange(n + 1)
        pmf = binom.pmf(e, n, R)
        raw = float(pmf[e / n > alpha].sum())
        cert = float(pmf[np.array([float(binom_upper_p(x, n, alpha)) <= 0.05 for x in e])].sum())
        pr, pc = planted_validation._p_raw_and_cert(R, n, alpha)
        assert pr == pytest.approx(raw, abs=1e-12) and pc == pytest.approx(cert, abs=1e-12)
    with pytest.raises(ValueError):
        planted_validation.study_d_strata(3)                                     # infeasible planting is refused


def test_planted_study_d_small():
    T = 30
    for cfg_name, n_cal in (("D1", 0), ("D2", 180_000)):
        r = planted_validation.study_d(cfg_name, T, n_blocks=2, per_block=3, n_split=5000, n_cal=n_cal, verbose=False)
        assert abs(r["true_full_info_risk"] - (planted_validation.ALPHA - 0.004)) < 1e-6
        slack = 0.20                                                              # 6 replicates
        assert r["true_violation_rate"] <= planted_validation.DELTA
        assert r["certified_violation_rate"] <= planted_validation.DELTA + 0.05 + slack
        assert r["expected_certified_rate"] <= planted_validation.DELTA + 0.05
        assert r["certified_violation_rate"] <= r["raw_test_violation_rate"]          # certified implies raw
        if cfg_name == "D2":
            assert r["cert_rate"] > 0.5                                               # powered calibration certifies
            assert r["deployed_true_deep_risk_max"] <= planted_validation.ALPHA       # ... rules just below alpha
