"""WO-14.2 -- v2 split machinery: determinism, disjointness, probe invariance.

Targeted runtime < 2 s CPU (pure numpy).
"""

from __future__ import annotations

import numpy as np
import pytest

from cafa.splits import (
    assert_disjoint,
    fixed_train_heldout,
    probe_eval_split,
    resplit_cal_test,
    split_digest,
)

_RESPLIT_SEEDS = (0, 1, 57, 99)


def test_fixed_train_heldout_determinism_and_seed_dependence():
    t1, h1 = fixed_train_heldout(2000, 0.6, 0)
    t2, h2 = fixed_train_heldout(2000, 0.6, 0)
    assert np.array_equal(t1, t2) and np.array_equal(h1, h2)
    assert t1.size == 1200 and h1.size == 800
    tb, _ = fixed_train_heldout(2000, 0.6, 1)
    assert not np.array_equal(t1, tb)   # a different train_seed moves the train split


def test_probe_eval_determinism():
    _, heldout = fixed_train_heldout(2000, 0.6, 0)
    p1, e1 = probe_eval_split(np.arange(heldout.size), 0.10, 777)
    p2, e2 = probe_eval_split(np.arange(heldout.size), 0.10, 777)
    assert np.array_equal(p1, p2) and np.array_equal(e1, e2)


def test_pairwise_disjoint_including_probe_vs_every_resplit():
    train, heldout = fixed_train_heldout(3000, 0.6, 0)
    probe_pos, eval_pos = probe_eval_split(np.arange(heldout.size), 0.10, 777)
    gp = heldout[probe_pos]
    ge = heldout[eval_pos]
    assert_disjoint(train=train, probe=gp, eval=ge)
    for rs in _RESPLIT_SEEDS:
        cal_local, test_local = resplit_cal_test(np.arange(eval_pos.size), rs)
        gc = ge[cal_local]
        gt = ge[test_local]
        # train, probe, cal, test all pairwise disjoint.
        assert_disjoint(train=train, probe=gp, cal=gc, test=gt)


def test_assert_disjoint_raises_naming_pair():
    with pytest.raises(AssertionError, match="probe"):
        assert_disjoint(train=np.array([1, 2, 3]), probe=np.array([3, 4, 5]))


def test_probe_invariant_across_resplit_seeds():
    _, heldout = fixed_train_heldout(2000, 0.6, 0)
    probe_pos, eval_pos = probe_eval_split(np.arange(heldout.size), 0.10, 777)
    # Resplitting the eval pool never changes the probe.
    for rs in _RESPLIT_SEEDS:
        resplit_cal_test(np.arange(eval_pos.size), rs)
    probe_pos2, _ = probe_eval_split(np.arange(heldout.size), 0.10, 777)
    assert np.array_equal(probe_pos, probe_pos2)


def test_split_digest_stability_and_order_invariance():
    d1 = split_digest(np.array([3, 1, 2]))
    d2 = split_digest(np.array([1, 2, 3]))
    assert d1 == d2                      # order of rows within an array does not matter
    assert d1 != split_digest(np.array([1, 2, 4]))
    # argument order matters.
    a, b = np.array([1, 2]), np.array([3, 4])
    assert split_digest(a, b) != split_digest(b, a)
