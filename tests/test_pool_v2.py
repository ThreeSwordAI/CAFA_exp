"""WO-14.3 -- pool cache format + post-hoc cost math.

Targeted runtime < 3 s CPU (pure numpy + npz I/O).
"""

from __future__ import annotations

import numpy as np
import pytest

from cafa.pool import (
    CACHE_VERSION,
    cum_cost_from_order,
    load_pool_cache,
    save_pool_cache,
    slice_rows,
)


def test_cum_cost_hand_example_3x4():
    order = np.array([[0, 1, 2], [2, 1, 0], [1, 1, 1]])   # [3, 3]
    fc = np.array([1.0, 10.0, 100.0])
    cc = cum_cost_from_order(order, fc)                    # [3, 4]
    expected = np.array([
        [0.0, 1.0, 11.0, 111.0],
        [0.0, 100.0, 110.0, 111.0],
        [0.0, 10.0, 20.0, 30.0],
    ])
    assert np.allclose(cc, expected)
    assert np.all(cc[:, 0] == 0.0)


def test_cum_cost_matches_bruteforce():
    rng = np.random.default_rng(3)
    n, T, d = 40, 12, 7
    order = rng.integers(0, d, size=(n, T))
    fc = rng.uniform(1.0, 10.0, size=d)
    cc = cum_cost_from_order(order, fc)
    brute = np.zeros((n, T + 1))
    for i in range(n):
        for t in range(T):
            brute[i, t + 1] = brute[i, t] + fc[order[i, t]]
    assert np.allclose(cc, brute)


def test_slice_rows_roundtrip():
    n, Tp1 = 10, 5
    cache = {
        "scores": np.arange(n * Tp1).reshape(n, Tp1).astype(float),
        "correct": np.zeros((n, Tp1)),
        "order": np.arange(n * (Tp1 - 1)).reshape(n, Tp1 - 1),
        "y": np.arange(n),
    }
    pos = np.array([2, 5, 7])
    sliced = slice_rows(cache, pos)
    assert np.array_equal(sliced["scores"], cache["scores"][pos])
    assert np.array_equal(sliced["order"], cache["order"][pos])
    assert np.array_equal(sliced["y"], cache["y"][pos])


def test_cache_save_load_roundtrip(tmp_path):
    n, Tp1, T = 8, 6, 5
    scores = np.random.default_rng(0).random((n, Tp1))
    correct = (scores > 0.5).astype(float)
    order = np.random.default_rng(1).integers(0, T, size=(n, T))
    y = np.arange(n)
    row_pos = np.arange(n)
    meta = {"dataset": "mnist", "policy": "greedy_entropy", "train_seed": 0, "T": T}
    path = tmp_path / "cache.npz"
    save_pool_cache(path, scores=scores, correct=correct, order=order, y=y,
                    row_pos=row_pos, meta=meta)
    loaded = load_pool_cache(path)
    assert np.allclose(loaded["scores"], scores)
    assert np.array_equal(loaded["order"], order)
    assert loaded["meta"]["policy"] == "greedy_entropy"
    assert loaded["meta"]["T"] == T


def test_save_requires_identity_row_pos(tmp_path):
    n, Tp1, T = 4, 4, 3
    with pytest.raises(AssertionError):
        save_pool_cache(
            tmp_path / "bad.npz",
            scores=np.zeros((n, Tp1)), correct=np.zeros((n, Tp1)),
            order=np.zeros((n, T), dtype=int), y=np.zeros(n),
            row_pos=np.array([1, 0, 2, 3]), meta={},
        )


def test_load_rejects_wrong_version(tmp_path):
    path = tmp_path / "v1.npz"
    np.savez_compressed(path, cache_version=np.int64(CACHE_VERSION - 1),
                        scores=np.zeros((2, 2)), correct=np.zeros((2, 2)),
                        order=np.zeros((2, 1), dtype=int), y=np.zeros(2),
                        row_pos=np.arange(2), meta_json="{}")
    with pytest.raises(ValueError):
        load_pool_cache(path)
