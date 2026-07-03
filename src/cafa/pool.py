"""WO-4 -- pool-rollout cache format + post-hoc cost math (v2 pipeline).

Torch-free.  The heldout pool is rolled out **once** per (dataset, train_seed,
policy) by the runner script (:mod:`scripts.run_pool_rollout`, which imports
torch lazily) and stored here as an ``.npz`` cache holding ``scores``,
``correct``, ``order`` (feature chosen per step), ``y`` and ``row_pos``.

Trajectories are cost-scheme-invariant: neither greedy nor random consults
feature_costs.  cum_cost is therefore derived, not stored -- :func:`cum_cost_from_order`
recomputes cumulative cost from ``order`` for any cost scheme post-hoc, so every
cost scheme and every resplit (a row-index slice of the cache) is nearly free.

This module defines only the cache I/O and the pure post-hoc math; it never
touches torch or the frozen risk-control core.
"""

from __future__ import annotations

import json

import numpy as np

__all__ = [
    "CACHE_VERSION",
    "save_pool_cache",
    "load_pool_cache",
    "cum_cost_from_order",
    "slice_rows",
]

CACHE_VERSION = 2

_REQUIRED_KEYS = ("scores", "correct", "order", "y", "row_pos")


def save_pool_cache(path, *, scores, correct, order, y, row_pos, meta: dict) -> None:
    """Write a pool-rollout cache to ``path`` (an ``.npz``).

    Parameters
    ----------
    scores, correct : np.ndarray, shape ``[n, T+1]`` float
        Per-instance readiness score and correctness at each acquisition step.
    order : np.ndarray, shape ``[n, T]`` int
        Feature acquired at step ``t`` (the artifact from which cum_cost is
        derived per cost scheme).
    y : np.ndarray, shape ``[n]``
        Integer labels.
    row_pos : np.ndarray, shape ``[n]``
        Positions within the heldout arrays.  For a full-pool cache this MUST
        equal ``np.arange(n)`` (asserted); the field is kept for future partial
        caches.
    meta : dict
        Provenance (dataset, policy, epsilon, score, train_seed, checkpoint +
        sha256, split_digest, T, n, numpy version, created timestamp, ...).
        Serialized to JSON under the npz key ``meta_json``.
    """
    scores = np.asarray(scores, dtype=float)
    correct = np.asarray(correct, dtype=float)
    order = np.asarray(order, dtype=np.int64)
    y = np.asarray(y, dtype=np.int64)
    row_pos = np.asarray(row_pos, dtype=np.int64)

    n, Tp1 = scores.shape
    if correct.shape != scores.shape:
        raise ValueError(f"correct shape {correct.shape} must match scores {scores.shape}.")
    if order.shape != (n, Tp1 - 1):
        raise ValueError(f"order must be [n, T]=({n}, {Tp1 - 1}); got {order.shape}.")
    if y.shape != (n,):
        raise ValueError(f"y must be [n]=({n},); got {y.shape}.")
    if row_pos.shape != (n,):
        raise ValueError(f"row_pos must be [n]=({n},); got {row_pos.shape}.")
    # Full-pool invariant: row_pos is the identity for a whole-pool cache.
    assert np.array_equal(row_pos, np.arange(n, dtype=np.int64)), (
        "row_pos must equal np.arange(n) for a full-pool cache."
    )

    np.savez_compressed(
        path,
        cache_version=np.int64(CACHE_VERSION),
        scores=scores,
        correct=correct,
        order=order,
        y=y,
        row_pos=row_pos,
        meta_json=json.dumps(meta),
    )


def load_pool_cache(path) -> dict:
    """Load and validate a pool-rollout cache written by :func:`save_pool_cache`.

    Validates ``CACHE_VERSION`` and the presence of every required array key,
    then returns ``{scores, correct, order, y, row_pos, meta}`` with ``meta`` the
    parsed JSON dict.
    """
    z = np.load(path, allow_pickle=False)
    version = int(z["cache_version"]) if "cache_version" in z.files else -1
    if version != CACHE_VERSION:
        raise ValueError(
            f"pool cache version {version} != expected {CACHE_VERSION} (path={path})."
        )
    missing = [k for k in _REQUIRED_KEYS if k not in z.files]
    if missing:
        raise ValueError(f"pool cache missing required keys {missing} (path={path}).")
    meta = json.loads(str(z["meta_json"])) if "meta_json" in z.files else {}
    return {
        "scores": z["scores"],
        "correct": z["correct"],
        "order": z["order"].astype(np.int64),
        "y": z["y"].astype(np.int64),
        "row_pos": z["row_pos"].astype(np.int64),
        "meta": meta,
    }


def cum_cost_from_order(order: np.ndarray, feature_costs: np.ndarray) -> np.ndarray:
    """Cumulative acquisition cost ``[n, T+1]`` from an acquisition ``order``.

    ``cc[:, 0] = 0`` and ``cc[:, t+1] = cc[:, t] + feature_costs[order[:, t]]``.
    Vectorized via ``np.take`` + ``cumsum``.  Because the policies never consult
    ``feature_costs``, this derives the cost trajectory for any cost scheme
    post-hoc from a single rollout.
    """
    order = np.asarray(order, dtype=np.int64)
    feature_costs = np.asarray(feature_costs, dtype=float)
    n, T = order.shape
    step_cost = np.take(feature_costs, order)             # [n, T]
    cc = np.zeros((n, T + 1), dtype=float)
    cc[:, 1:] = np.cumsum(step_cost, axis=1)
    return cc


def slice_rows(cache: dict, pos: np.ndarray) -> dict:
    """Row-slice a loaded cache's arrays at positions ``pos``.

    Returns ``{scores, correct, order, y}`` restricted to ``pos`` (copies).  Used
    to carve a resplit's cal/test rows out of the full-pool cache.
    """
    pos = np.asarray(pos, dtype=np.int64)
    return {
        "scores": np.asarray(cache["scores"])[pos],
        "correct": np.asarray(cache["correct"])[pos],
        "order": np.asarray(cache["order"])[pos],
        "y": np.asarray(cache["y"])[pos],
    }
