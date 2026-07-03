"""WO-2 -- split machinery with hard disjointness assertions (v2 pipeline).

Pure numpy; no torch, no data, no models.  Implements the fixed-train /
probe / resplit scheme that structurally fixes bugs C2 (per-seed full-pool
reshuffle -> train/eval leakage), C3 (calibration-fit stratum edges) and C5
(alpha not committed on an independent split).

Invariant chain (enforced by :func:`assert_disjoint` at load time and asserted
in tests):

    train  disjoint  heldout          (fixed_train_heldout; train depends only
                                        on train_seed)
    probe  disjoint  eval             (probe_eval_split; probe fixed at seed 777)
    cal    disjoint  test             (resplit_cal_test; per resplit_seed)
    (train union probe) never enters selection or evaluation
    edges / alpha / feature-costs are functions of (train, probe) ONLY

Row order within every returned split is itself deterministic: each function
returns the *permuted* order (not re-sorted), so identical seeds reproduce
identical arrays bit-for-bit.
"""

from __future__ import annotations

import hashlib

import numpy as np

__all__ = [
    "fixed_train_heldout",
    "probe_eval_split",
    "resplit_cal_test",
    "assert_disjoint",
    "split_digest",
]

# Offset so resplit RNG streams can never collide with the train / probe streams
# (train_seed and probe_seed are small integers; resplits start at 1_000_000).
_RESPLIT_OFFSET = 1_000_000


def fixed_train_heldout(
    n_total: int, train_frac: float, train_seed: int
) -> "tuple[np.ndarray, np.ndarray]":
    """Fixed train / heldout partition of ``[0, n_total)`` (train depends only on seed).

    Permutes ``range(n_total)`` with ``np.random.default_rng(train_seed)`` and
    takes the first ``round(train_frac * n_total)`` as train, the rest as
    heldout.  Because the permutation depends only on ``train_seed``, the train
    split (hence the backbone) is fixed across every probe/resplit draw.

    Returns ``(train_idx, heldout_idx)`` int64 arrays in permuted order.
    """
    rng = np.random.default_rng(int(train_seed))
    perm = rng.permutation(int(n_total)).astype(np.int64)
    n_train = int(round(float(train_frac) * int(n_total)))
    return perm[:n_train], perm[n_train:]


def probe_eval_split(
    heldout_idx: np.ndarray, probe_frac: float, probe_seed: int = 777
) -> "tuple[np.ndarray, np.ndarray]":
    """Split ``heldout_idx`` into a fixed probe and the eval remainder.

    Permutes ``heldout_idx`` with ``np.random.default_rng(probe_seed)`` and takes
    the first ``round(probe_frac * len)`` as probe, the rest as eval.  With
    ``probe_seed`` fixed at 777 (the config default) the probe is *identical*
    across every resplit and every run, so the alpha / edges / costs it commits
    are pre-committed once and never re-derived on selection data.

    Pass ``np.arange(len(heldout))`` to obtain *positions within the heldout
    arrays*; pass the global heldout indices to obtain global indices.  Returns
    ``(probe, eval)`` int64 arrays in permuted order.
    """
    heldout_idx = np.asarray(heldout_idx, dtype=np.int64)
    rng = np.random.default_rng(int(probe_seed))
    perm = rng.permutation(heldout_idx.size)
    permuted = heldout_idx[perm]
    n_probe = int(round(float(probe_frac) * heldout_idx.size))
    return permuted[:n_probe], permuted[n_probe:]


def resplit_cal_test(
    eval_idx: np.ndarray, resplit_seed: int, cal_frac: float = 0.5
) -> "tuple[np.ndarray, np.ndarray]":
    """Split ``eval_idx`` into cal / test for one resplit.

    Permutes ``eval_idx`` with ``np.random.default_rng(1_000_000 + resplit_seed)``
    (the offset keeps resplit streams from ever colliding with the train / probe
    streams) and takes the first ``cal_frac`` as cal, the rest as test.

    Pass eval *positions* (``np.arange``-based) to get cal/test positions.
    Returns ``(cal, test)`` int64 arrays in permuted order.
    """
    eval_idx = np.asarray(eval_idx, dtype=np.int64)
    rng = np.random.default_rng(_RESPLIT_OFFSET + int(resplit_seed))
    perm = rng.permutation(eval_idx.size)
    permuted = eval_idx[perm]
    n_cal = int(round(float(cal_frac) * eval_idx.size))
    return permuted[:n_cal], permuted[n_cal:]


def assert_disjoint(**named_index_sets) -> None:
    """Assert every pair of the named index sets is disjoint.

    Raises ``AssertionError`` naming the offending pair (and the overlap size)
    on the first violation.  Example::

        assert_disjoint(train=train_idx, probe=probe_idx, eval=eval_idx)
    """
    items = [(name, np.asarray(idx, dtype=np.int64)) for name, idx in named_index_sets.items()]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            (na, a), (nb, b) = items[i], items[j]
            overlap = np.intersect1d(a, b, assume_unique=False)
            if overlap.size:
                raise AssertionError(
                    f"index sets {na!r} and {nb!r} overlap in {overlap.size} element(s); "
                    f"first offending index = {int(overlap[0])}"
                )


def split_digest(*index_arrays) -> str:
    """sha256 hex of the concatenated sorted int64 bytes of the index arrays.

    Each array is sorted independently, cast to int64, then concatenated in
    argument order; the byte stream is hashed.  A stable provenance fingerprint
    for a set of splits (order of *rows within* an array does not matter, order
    of *arguments* does).
    """
    parts = [np.sort(np.asarray(a, dtype=np.int64)) for a in index_arrays]
    blob = np.concatenate(parts).tobytes() if parts else b""
    return hashlib.sha256(blob).hexdigest()
