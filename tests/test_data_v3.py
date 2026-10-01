"""v3 -- dataset loaders (numpy paths; torch loaders are covered by the Phase-1 smoke run)."""

from __future__ import annotations

import numpy as np
import pytest

from cafa.data_v3 import dataset_kind, generate_cube, load_csv_tabular_pool, load_cube_pool

CFG = {"protocol_v3": {"train_frac": 0.6, "probe_frac": 0.10, "probe_seed": 777},
       "datasets_v3": [{"name": "cube", "n_samples": 3000, "seed": 123}]}


def test_dataset_kind():
    assert dataset_kind("mnist") == "image_patches"
    assert dataset_kind("fashionmnist") == "image_patches"
    assert dataset_kind("image:imagenette") == "image_rgb"
    assert dataset_kind("tabular:MiniBooNE") == "tabular_openml"
    assert dataset_kind("csv:physionet") == "tabular_csv"
    assert dataset_kind("cube") == "synthetic_cube"
    with pytest.raises(ValueError):
        dataset_kind("nope")


def test_cube_generator_matches_afabench_law():
    X, y = generate_cube(4000, seed=7)
    assert X.shape == (4000, 20) and y.shape == (4000,) and set(np.unique(y)) <= set(range(8))
    codes = np.array([[int(b) for b in format(i, "03b")][::-1] for i in range(8)], dtype=float)
    # informative entries sit at positions y, y+1, y+2 with the label's 3-bit code (std 0.1)
    for lbl in range(8):
        rows = X[y == lbl]
        block = rows[:, lbl:lbl + 3]
        assert np.allclose(block.mean(axis=0), codes[lbl], atol=0.03)
        assert np.all(block.std(axis=0) < 0.15)
    # dummy features are N(0.5, 0.3)
    assert abs(X[:, 10:].mean() - 0.5) < 0.03 and abs(X[:, 10:].std() - 0.3) < 0.03
    X2, _ = generate_cube(4000, seed=7)
    assert np.array_equal(X, X2)


def test_cube_pool_contract(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    monkeypatch.setenv("RESULTS_ROOT", str(tmp_path))
    pool = load_cube_pool(CFG, train_seed=0)
    assert pool["train"][0].shape == (1800, 20) and pool["heldout"][0].shape == (1200, 20)
    assert pool["n_classes"] == 8 and pool["n_features"] == 20
    assert set(pool["feature_costs_by_scheme"]) == {"uniform", "inverse_info", "random"}
    assert pool["probe_pos"].size == 120
    assert not (set(pool["heldout_index"]) & set(np.setdiff1d(np.arange(3000), pool["heldout_index"])))
    pool1 = load_cube_pool(CFG, train_seed=1)
    assert not np.array_equal(pool["heldout_index"], pool1["heldout_index"])


def test_csv_loader_train_only_preprocessing(monkeypatch, tmp_path):
    import pandas as pd

    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    monkeypatch.setenv("RESULTS_ROOT", str(tmp_path))
    rng = np.random.default_rng(0)
    n = 500
    X = rng.normal(size=(n, 5)) * np.array([1, 10, 100, 1, 1]) + np.array([0, 5, 50, 0, 0])
    X[rng.uniform(size=(n, 5)) < 0.2] = np.nan
    y = (X[:, 0] > 0).astype(float)
    y[np.isnan(y)] = 0.0
    df = pd.DataFrame(X, columns=[f"f{j}" for j in range(5)])
    df["Outcome"] = y
    (tmp_path / "afabench").mkdir()
    df.to_csv(tmp_path / "afabench" / "toy.csv", index=False)
    pool = load_csv_tabular_pool("toy", CFG, train_seed=0)
    Xtr = pool["train"][0]
    assert not np.isnan(Xtr).any() and not np.isnan(pool["heldout"][0]).any()
    assert np.allclose(Xtr.mean(axis=0), 0.0, atol=0.15) and np.allclose(Xtr.std(axis=0), 1.0, atol=0.2)
    assert pool["n_classes"] == 2 and pool["name"] == "csv:toy"
