"""v3 -- regression tests for the fixes made to the torch-free Phase-3 scripts during the campaign.

Each test builds a small synthetic pool cache (cafa.synthetic_planted via
scripts/make_synthetic_pool_cache.py) in a temp dir and exercises the real script code:

* run_cascade_sweep: every baseline draw record carries ``stratum_violation`` and the summary rate
  equals the per-draw mean (the Mondrian oracle's rate was hard-wired to 0.0); the cheapest-valid
  oracle is kept in the summary (it was dropped: n = 0, cost None);
* make_tables_v3: ``--scheme inverse_info`` skips cells that only have uniform costs instead of
  printing uniform numbers under an inverse_info header;
* repair_experiment: the default number of calibration draws is the protocol's 100 (was 50);
* provenance guards: commit_v3 refuses a partial ``--max-rows`` cache; the sweep refuses a cache
  whose checkpoint differs from the committed one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import commit_v3  # noqa: E402
import make_synthetic_pool_cache  # noqa: E402
import make_tables_v3  # noqa: E402
import repair_experiment  # noqa: E402
import run_cascade_sweep  # noqa: E402
from cafa import config  # noqa: E402
from cafa.pool import load_pool_cache, save_pool_cache  # noqa: E402

CFG_PATH = str(REPO / "configs" / "experiment_v3.yaml")


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    root = tmp_path_factory.mktemp("v3scripts")
    pool = root / "pool_v3"
    assert make_synthetic_pool_cache.main(["--pool-dir", str(pool), "--n", "3000", "--scenario", "typeII"]) == 0
    cfg = config.load_experiment(CFG_PATH)
    committed = root / "committed.json"
    rc = commit_v3.commit(dataset="synthetic-planted", train_seed=0, score="softmax", pool_dir=pool,
                          out_path=committed, cfg=cfg, force=True)
    assert rc == 0
    out = root / "metrics_v3"
    op = run_cascade_sweep.run_one("synthetic-planted", "greedy_entropy", "softmax", 0, cfg=cfg, paths=None,
                                   n_draws=5, pool_dir=pool, out_dir=out, committed_path=committed)  # 1 per split (round 2)
    return {"root": root, "pool": pool, "committed": committed, "metrics_dir": out,
            "metrics": json.loads(Path(op).read_text()), "cfg": cfg}


def test_sweep_baseline_stratum_violation_recorded_and_summarised(synth):
    for lr_key, blk in synth["metrics"]["lambda_refs"].items():
        for scheme, sch in blk["schemes"].items():
            draws, summ = sch["draws"], sch["summary"]["baselines"]
            for name in ("mondrian_oracle", "plugin", "full_acquisition"):
                recs = [d["baselines"][name] for d in draws if "test_risk" in d["baselines"][name]]
                assert recs and all("stratum_violation" in r for r in recs), (lr_key, name)
                assert summ[name]["stratum_violation_rate"] == pytest.approx(
                    np.mean([r["stratum_violation"] for r in recs]))
            # Mondrian per-stratum risks recomputed from the record: abstained strata at full acquisition
            mon = [d["baselines"]["mondrian_oracle"] for d in draws]
            assert all(isinstance(r["stratum_violation"], bool) for r in mon)


def test_sweep_keeps_cheapest_valid_oracle(synth):
    alpha = synth["metrics"]["alpha"]
    for blk in synth["metrics"]["lambda_refs"].values():
        for sch in blk["schemes"].values():
            n_sel = sum(d["baselines"]["oracle_cheapest_valid"]["lambda"] is not None for d in sch["draws"])
            s = sch["summary"]["baselines"]["oracle_cheapest_valid"]
            assert s["n"] == n_sel
            if n_sel:
                assert s["mean_test_cost"] is not None and s["mean_test_risk"] <= alpha + 1e-12
                assert s["aggregate_violation_rate"] == 0.0


def test_make_tables_skips_missing_scheme(synth, tmp_path):
    uni, inv = tmp_path / "uniform", tmp_path / "inverse_info"
    assert make_tables_v3.main(["--metrics-dir", str(synth["metrics_dir"]), "--output-dir", str(uni),
                                "--scheme", "uniform"]) == 0
    assert make_tables_v3.main(["--metrics-dir", str(synth["metrics_dir"]), "--output-dir", str(inv),
                                "--scheme", "inverse_info"]) == 0
    assert (uni / "TABLE_E4_cascade.csv").exists()
    assert not (inv / "TABLE_E4_cascade.csv").exists()  # synthetic caches carry uniform costs only


def test_repair_default_n_draws_is_protocol(synth, tmp_path):
    cache = synth["pool"] / "synthetic-planted_ts0_greedy_entropy_softmax.npz"
    out = tmp_path / "repair.json"
    assert repair_experiment.main(["--dataset", "synthetic-planted", "--train-seed", "0",
                                   "--before-cache", str(cache), "--after-cache", str(cache),
                                   "--committed", str(synth["committed"]), "--config", CFG_PATH,
                                   "--output", str(out)]) == 0
    rep = json.loads(out.read_text())
    assert rep["n_draws"] == synth["cfg"]["protocol_v3"]["n_draws"] == 100


def test_commit_refuses_partial_smoke_cache(synth, tmp_path):
    pool = tmp_path / "pool_v3"
    pool.mkdir()
    for pol in ("greedy_entropy", "random"):
        c = load_pool_cache(synth["pool"] / f"synthetic-planted_ts0_{pol}_softmax.npz")
        meta = dict(c["meta"], max_rows=256 if pol == "random" else None)
        save_pool_cache(pool / f"synthetic-planted_ts0_{pol}_softmax.npz", scores=c["scores"],
                        correct=c["correct"], order=c["order"], y=c["y"], row_pos=c["row_pos"], meta=meta)
    rc = commit_v3.commit(dataset="synthetic-planted", train_seed=0, score="softmax", pool_dir=pool,
                          out_path=tmp_path / "c.json", cfg=synth["cfg"], force=True)
    assert rc == 4 and not (tmp_path / "c.json").exists()


def test_sweep_refuses_stale_commit(synth, tmp_path):
    pool = tmp_path / "pool_v3"
    pool.mkdir()
    c = load_pool_cache(synth["pool"] / "synthetic-planted_ts0_greedy_entropy_softmax.npz")
    save_pool_cache(pool / "synthetic-planted_ts0_greedy_entropy_softmax.npz", scores=c["scores"],
                    correct=c["correct"], order=c["order"], y=c["y"], row_pos=c["row_pos"],
                    meta=dict(c["meta"], checkpoint_sha256="b" * 64))
    com = json.loads(synth["committed"].read_text())
    com["cache_meta"]["checkpoint_sha256"] = "a" * 64
    cp = tmp_path / "committed.json"
    cp.write_text(json.dumps(com))
    with pytest.raises(RuntimeError, match="re-commit"):
        run_cascade_sweep.run_one("synthetic-planted", "greedy_entropy", "softmax", 0, cfg=synth["cfg"],
                                  paths=None, n_draws=5, pool_dir=pool, out_dir=tmp_path / "m", committed_path=cp)
