"""v3 -- split invariants: probe identical to v2, disjointness, determinism."""

from __future__ import annotations

import numpy as np

from cafa.splits import probe_eval_split
from cafa.splits_v3 import calibration_draw, calpool_test_split, v3_positions


def test_probe_identical_to_v2():
    n = 10_001
    pos = v3_positions(n)
    probe_v2, eval_v2 = probe_eval_split(np.arange(n), 0.10, 777)
    assert np.array_equal(pos["probe"], probe_v2)
    assert set(pos["calpool"].tolist()) | set(pos["test"].tolist()) == set(eval_v2.tolist())


def test_disjoint_and_deterministic():
    a = v3_positions(5000)
    b = v3_positions(5000)
    for k in ("probe", "calpool", "test"):
        assert np.array_equal(a[k], b[k])
    assert not set(a["calpool"]) & set(a["test"])
    assert abs(a["calpool"].size - a["test"].size) <= 1


def test_calibration_draws_are_subsets_and_vary():
    pos = v3_positions(4000)
    d0 = calibration_draw(pos["calpool"], 0)
    d1 = calibration_draw(pos["calpool"], 1)
    assert set(d0) <= set(pos["calpool"]) and set(d1) <= set(pos["calpool"])
    assert not np.array_equal(np.sort(d0), np.sort(d1))
    assert np.array_equal(calibration_draw(pos["calpool"], 0), d0)
    assert d0.size == round(0.5 * pos["calpool"].size)
