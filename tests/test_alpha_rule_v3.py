"""v3 round 2 (Task E) -- the v3-local alpha rule reproduces the committed rule exactly with its defaults.

``commit_v3.alpha_from_floor(floor, margin, grid)`` is the E9 alpha-rule sensitivity's copy of
``cafa.data.feasible_alpha_from_floor(floor, headroom, step)``.  With the defaults (0.05, 0.05) it must give
the identical float on a fine grid of floors and at the boundary cases (exact multiples of the grid, float
dust such as 0.1 + 0.05, floors of 0 and > 1, the seed-0 probe floors of the campaign).
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
from cafa import config  # noqa: E402
from cafa.data import feasible_alpha_from_floor  # noqa: E402

SEED0_FLOORS = (0.125, 0.05375, 0.154229, 0.09723, 0.07438, 0.003929, 0.064286)   # handoff.md section 8.9


def test_defaults_reproduce_feasible_alpha_from_floor_exactly():
    floors = np.concatenate([np.linspace(0.0, 1.0, 20001), np.arange(0, 21) * 0.05, np.arange(0, 21) * 0.05 - 0.05,
                             np.arange(0, 101) * 0.01, [1e-12, 0.1 + 0.05 - 0.05, 0.95, 0.9500000001, 1.2],
                             SEED0_FLOORS])
    for f in floors:
        assert commit_v3.alpha_from_floor(float(f)) == feasible_alpha_from_floor(float(f)), f
        assert commit_v3.alpha_from_floor(float(f), 0.05, 0.05) == feasible_alpha_from_floor(float(f), 0.05, 0.05)


def test_tighter_rule_values():
    # margin 0.02, grid 0.01 on the seed-0 probe floors (E9): PhysioNet, CUBE, Adult, Diabetes, MiniBooNE,
    # MNIST, FashionMNIST
    got = [commit_v3.alpha_from_floor(f, 0.02, 0.01) for f in SEED0_FLOORS]
    assert got == [0.15, 0.08, 0.18, 0.12, 0.10, 0.03, 0.09]
    for f in np.linspace(0, 0.9, 901):
        a = commit_v3.alpha_from_floor(float(f), 0.02, 0.01)
        assert a >= f + 0.02 - 1e-9 and a - (f + 0.02) < 0.01 + 1e-9 and abs(a * 100 - round(a * 100)) < 1e-9


def test_commit_records_nondefault_rule_and_refuses_alpha_below_design_margin(tmp_path):
    pool = tmp_path / "pool_v3"
    assert make_synthetic_pool_cache.main(["--pool-dir", str(pool), "--n", "3000", "--scenario", "feasible"]) == 0
    cfg = config.load_experiment(str(REPO / "configs" / "experiment_v3.yaml"))
    base, alt = tmp_path / "base.json", tmp_path / "alt.json"
    assert commit_v3.commit(dataset="synthetic-planted", train_seed=0, score="softmax", pool_dir=pool,
                            out_path=base, cfg=cfg) == 0
    b = json.loads(base.read_text())
    assert "alpha_rule" not in b                                      # the committed rule leaves no trace
    floor = b["floor"]["estimate"]
    rc = commit_v3.commit(dataset="synthetic-planted", train_seed=0, score="softmax", pool_dir=pool,
                          out_path=alt, cfg=cfg, alpha_margin=0.02, alpha_grid=0.01)
    a_alt = commit_v3.alpha_from_floor(floor, 0.02, 0.01)
    if a_alt <= cfg["cascade"]["design_margin"]:
        assert rc == 7 and not alt.exists()                           # n_min undefined: nothing committed
    else:
        assert rc == 0
        c = json.loads(alt.read_text())
        assert c["alpha_rule"] == {"margin": 0.02, "grid": 0.01} and c["alpha"] == a_alt
    with pytest.raises(SystemExit):                                   # a non-default rule never overwrites the main commit
        commit_v3.main(["--dataset", "synthetic-planted", "--alpha-margin", "0.02", "--alpha-grid", "0.01"])
