"""WO-14.5 -- probe_commit: schema round-trip + --force/--extend-edges semantics.

Exercised at the function level (``probe_commit.commit`` with explicit paths), so
no CLI / path environment is needed.  Targeted runtime < 3 s CPU.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from cafa.pool import save_pool_cache

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import probe_commit as pc  # noqa: E402

_CFG = {
    "protocol_v2": {"probe_frac": 0.10, "probe_seed": 777},
    "mondrian_v2": {"lambda_refs": [0.5, 0.9]},
    "method": {"procedure_score": "softmax"},
}
_DSNAME = "tabular-adult"
_TS = 0
_SCORE = "softmax"


def _write_cache(pool_dir: Path, policy_token: str, correct_T, seed):
    n, Tp1, T = 300, 6, 5
    rng = np.random.default_rng(seed)
    scores = rng.random((n, Tp1))
    correct = (rng.random((n, Tp1)) > 0.4).astype(float)
    correct[:, T] = correct_T          # full-acq correctness identical across policies
    order = rng.integers(0, T, size=(n, T))
    meta = {
        "dataset": "tabular:adult", "policy": policy_token, "train_seed": _TS,
        "feature_costs_by_scheme": {
            "uniform": [1.0] * T,
            "inverse_info": [1.0, 2.0, 3.0, 4.0, 5.0],
            "random": [2.0, 4.0, 6.0, 8.0, 10.0],
        },
    }
    path = pool_dir / f"{_DSNAME}_ts{_TS}_{policy_token}_{_SCORE}.npz"
    save_pool_cache(path, scores=scores, correct=correct, order=order,
                    y=np.arange(n), row_pos=np.arange(n), meta=meta)
    return path


def _setup(tmp_path):
    pool_dir = tmp_path / "pool_v2"
    pool_dir.mkdir()
    correct_T = (np.random.default_rng(99).random(300) > 0.3).astype(float)
    _write_cache(pool_dir, "greedy_entropy", correct_T, seed=1)
    _write_cache(pool_dir, "random", correct_T, seed=2)
    out_path = tmp_path / "committed.json"
    return pool_dir, out_path


def test_commit_schema_roundtrip(tmp_path):
    pool_dir, out_path = _setup(tmp_path)
    code = pc.commit(dataset="tabular:adult", train_seed=_TS, score=_SCORE,
                     pool_dir=pool_dir, out_path=out_path, cfg=_CFG)
    assert code == 0 and out_path.exists()
    committed = json.loads(out_path.read_text())
    for key in ("dataset", "train_seed", "cache_meta", "probe_n", "floor", "alpha",
                "feature_costs_by_scheme", "edges", "created", "tool"):
        assert key in committed, f"missing schema key {key}"
    assert set(committed["floor"]) == {"estimate", "cp_lcb95", "cp_ucb95"}
    assert 0.0 < committed["alpha"] <= 1.0
    # edges for both policies, each lambda_ref, each scheme.
    assert set(committed["edges"]) == {"greedy_entropy", "random"}
    ge = committed["edges"]["greedy_entropy"]["0.5"]
    assert set(ge["quantile"]) == {"3", "5", "8"}
    assert set(ge["equal_width_merged"]) == {"5x25", "5x50", "5x100"}


def test_commit_refuses_overwrite_without_force(tmp_path):
    pool_dir, out_path = _setup(tmp_path)
    assert pc.commit(dataset="tabular:adult", train_seed=_TS, score=_SCORE,
                     pool_dir=pool_dir, out_path=out_path, cfg=_CFG) == 0
    # second call without force -> refuse (code 3).
    assert pc.commit(dataset="tabular:adult", train_seed=_TS, score=_SCORE,
                     pool_dir=pool_dir, out_path=out_path, cfg=_CFG) == 3
    # with force -> overwrite (code 0).
    assert pc.commit(dataset="tabular:adult", train_seed=_TS, score=_SCORE,
                     pool_dir=pool_dir, out_path=out_path, cfg=_CFG, force=True) == 0


def test_extend_edges_adds_policy_without_touching_floor(tmp_path):
    pool_dir, out_path = _setup(tmp_path)
    assert pc.commit(dataset="tabular:adult", train_seed=_TS, score=_SCORE,
                     pool_dir=pool_dir, out_path=out_path, cfg=_CFG) == 0
    before = json.loads(out_path.read_text())

    # A new eps-greedy cache appears; extend-edges must add it, leave floor/alpha.
    _write_cache(pool_dir, "eps_greedy_eps0.25", before_correct_T(before, pool_dir), seed=7)
    assert pc.commit(dataset="tabular:adult", train_seed=_TS, score=_SCORE,
                     pool_dir=pool_dir, out_path=out_path, cfg=_CFG, extend_edges=True) == 0
    after = json.loads(out_path.read_text())
    assert "eps_greedy_eps0.25" in after["edges"]
    assert after["floor"] == before["floor"]
    assert after["alpha"] == before["alpha"]


def before_correct_T(before, pool_dir):
    # Reuse the greedy cache's full-acq correctness so the (unused for extend) floor
    # invariants stay consistent if a later full commit is attempted.
    from cafa.pool import load_pool_cache
    ge = load_pool_cache(pool_dir / f"{_DSNAME}_ts{_TS}_greedy_entropy_{_SCORE}.npz")
    return np.asarray(ge["correct"])[:, -1]
