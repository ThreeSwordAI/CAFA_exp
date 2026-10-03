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

Round 2 (multi-split protocol): the eval remainder is split into calpool / test once PER test seed
(``protocol_v3.test_seeds``, e.g. 778..782; :func:`v3_positions_multi`), and the ``n_draws``
calibration draws are spread evenly over the splits (``n_draws / len(test_seeds)`` per split).  The
probe is the same for every split, so every committed quantity is unchanged.  Calibration draw ``d``
of split index ``s`` uses the draw id :func:`split_draw_id` ``= s * SPLIT_DRAW_STRIDE + d`` with
``SPLIT_DRAW_STRIDE = 1000`` (requires ``d < 1000``), i.e. the RNG seed ``DRAW_OFFSET + s * 1000 + d``:
no draw seed is reused across splits, and split index 0 (the primary split, test seed 778) uses the
round-1 draw ids ``0, 1, ...`` -- its first draws are the round-1 draws on the same calibration pool.
"""

from __future__ import annotations

import numpy as np

from .splits import assert_disjoint, probe_eval_split

__all__ = ["calpool_test_split", "calibration_draw", "v3_positions", "v3_positions_multi",
           "draws_per_split", "split_draw_id", "DRAW_OFFSET", "TEST_SEED", "SPLIT_DRAW_STRIDE"]

TEST_SEED = 778
DRAW_OFFSET = 2_000_000
SPLIT_DRAW_STRIDE = 1000


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


def draws_per_split(n_draws: int, n_splits: int) -> int:
    """Calibration draws per split; ``n_draws`` (the protocol total, 100) must divide evenly."""
    n_draws, n_splits = int(n_draws), int(n_splits)
    if n_splits < 1 or n_draws % n_splits:
        raise ValueError(f"n_draws={n_draws} is not divisible by the number of splits {n_splits}.")
    per = n_draws // n_splits
    if per > SPLIT_DRAW_STRIDE:
        raise ValueError(f"{per} draws per split exceed SPLIT_DRAW_STRIDE={SPLIT_DRAW_STRIDE} (draw ids would collide).")
    return per


def split_draw_id(split_index: int, d: int) -> int:
    """Draw id of calibration draw ``d`` of split ``split_index`` (pass it to :func:`calibration_draw`)."""
    if not 0 <= int(d) < SPLIT_DRAW_STRIDE:
        raise ValueError(f"draw index {d} outside [0, {SPLIT_DRAW_STRIDE}).")
    return int(split_index) * SPLIT_DRAW_STRIDE + int(d)


def v3_positions_multi(
    n_heldout: int,
    probe_frac: float = 0.10,
    probe_seed: int = 777,
    test_frac: float = 0.5,
    test_seeds=(TEST_SEED,),
) -> list:
    """One :func:`v3_positions` dict per test seed (same probe; calpool / test re-split per seed).

    Returns a list in ``test_seeds`` order; each dict also carries ``test_seed`` and ``split_index``
    (the index used by :func:`split_draw_id`).
    """
    seeds = [int(s) for s in test_seeds]
    if len(set(seeds)) != len(seeds):
        raise ValueError(f"test_seeds must be distinct; got {seeds}.")
    out = []
    for i, ts in enumerate(seeds):
        pos = v3_positions(n_heldout, probe_frac, probe_seed, test_frac, ts)
        pos["test_seed"] = ts
        pos["split_index"] = i
        out.append(pos)
    return out
