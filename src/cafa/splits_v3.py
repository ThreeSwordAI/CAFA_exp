"""v3 -- probe / calibration-pool / independent-test split (pure numpy).

The v2 pipeline evaluated calibration-selected rules on the complementary half
of the SAME fixed pool, so its violation counts described the fixed pool rather
than the population (the AAAI AI review's objection).  v3 keeps the v2 probe
byte-identical (same :func:`cafa.splits.probe_eval_split`, seed 777, so every
committed alpha and every v2 commitment stays valid) and splits the v2 "eval"
remainder once, with a fixed seed, into

    calibration pool   (test_frac = 0.5 of eval  ->  45% of heldout)
    test               (the rest                 ->  45% of heldout)

Each calibration draw is a seeded ``cal_frac`` subsample of the calibration
pool; the deployed rule is then evaluated on the FIXED test split, which never
enters selection, so test risks are independent population-risk estimates.

Invariant chain (asserted):
    train disjoint heldout; probe disjoint calpool disjoint test;
    edges / alpha / lambda_ref / escalation levels are functions of probe only.
"""

from __future__ import annotations

import numpy as np

from .splits import assert_disjoint, probe_eval_split

__all__ = ["calpool_test_split", "calibration_draw", "v3_positions", "DRAW_OFFSET", "TEST_SEED"]

TEST_SEED = 778
DRAW_OFFSET = 2_000_000


def calpool_test_split(
    eval_pos: np.ndarray, test_frac: float = 0.5, test_seed: int = TEST_SEED
) -> "tuple[np.ndarray, np.ndarray]":
    """Split the v2 eval positions once into ``(calpool, test)`` (permuted order)."""
    eval_pos = np.asarray(eval_pos, dtype=np.int64)
    rng = np.random.default_rng(int(test_seed))
    perm = rng.permutation(eval_pos.size)
    permuted = eval_pos[perm]
    n_test = int(round(float(test_frac) * eval_pos.size))
    test = permuted[:n_test]
    calpool = permuted[n_test:]
    return calpool, test


def calibration_draw(
    calpool_pos: np.ndarray, draw: int, cal_frac: float = 0.5
) -> np.ndarray:
    """Seeded ``cal_frac`` subsample of the calibration pool for draw ``draw``.

    Seeds start at ``2_000_000 + draw`` so they can never collide with the
    train / probe / v2-resplit streams.
    """
    calpool_pos = np.asarray(calpool_pos, dtype=np.int64)
    rng = np.random.default_rng(DRAW_OFFSET + int(draw))
    perm = rng.permutation(calpool_pos.size)
    n_cal = int(round(float(cal_frac) * calpool_pos.size))
    return calpool_pos[perm[:n_cal]]


def v3_positions(
    n_heldout: int,
    probe_frac: float = 0.10,
    probe_seed: int = 777,
    test_frac: float = 0.5,
    test_seed: int = TEST_SEED,
) -> dict:
    """Positions (within the heldout arrays / pool cache) of probe, calpool, test."""
    probe, ev = probe_eval_split(np.arange(int(n_heldout)), probe_frac, probe_seed)
    calpool, test = calpool_test_split(ev, test_frac, test_seed)
    assert_disjoint(probe=probe, calpool=calpool, test=test)
    assert probe.size + calpool.size + test.size == int(n_heldout)
    return {"probe": probe, "calpool": calpool, "test": test, "eval_v2": ev}
