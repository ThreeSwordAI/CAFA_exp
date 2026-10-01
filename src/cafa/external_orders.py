"""v3 -- frozen acquisition orders from EXTERNAL policies (torch-free I/O).

An external AFA policy (e.g. an AFABench-trained GDFS or AACO) is integrated as
a FROZEN ORDER MATRIX: for each heldout row (in heldout order) the sequence of
feature indices it would acquire if forced to acquire every feature.  Our
frozen predictor then produces readiness / correctness along that order
(:mod:`scripts.run_pool_rollout_v3` ``--orders-file``), and the resulting pool
cache is indistinguishable from an internal-policy cache for everything
downstream (commit, cascade, audit).  This is exactly the paper's setting: a
frozen policy pi and a frozen predictor f; the policy may use its own internal
model to choose features.

File format (``.npz``): ``orders`` int64 ``[n_heldout, T]`` (each row a
permutation of ``0..T-1``), ``policy`` (str), ``dataset`` (str),
``heldout_digest`` (sha256 of the heldout index array; must match the pool
loader's), ``meta_json``.
"""

from __future__ import annotations

import json

import numpy as np

__all__ = ["save_orders", "load_orders", "validate_orders"]


def validate_orders(orders: np.ndarray, n_expected: int = None, T_expected: int = None) -> np.ndarray:
    o = np.asarray(orders, dtype=np.int64)
    if o.ndim != 2:
        raise ValueError(f"orders must be [n, T]; got {o.shape}.")
    n, T = o.shape
    if n_expected is not None and n != int(n_expected):
        raise ValueError(f"orders have {n} rows; expected {n_expected} heldout rows.")
    if T_expected is not None and T != int(T_expected):
        raise ValueError(f"orders have T={T}; expected {T_expected}.")
    sorted_rows = np.sort(o, axis=1)
    if not np.array_equal(sorted_rows, np.tile(np.arange(T), (n, 1))):
        bad = int(np.flatnonzero(~(sorted_rows == np.arange(T)[None, :]).all(axis=1))[0])
        raise ValueError(f"row {bad} of orders is not a permutation of 0..{T - 1}.")
    return o


def save_orders(path, orders, *, policy: str, dataset: str, heldout_digest: str, meta: dict = None) -> None:
    o = validate_orders(orders)
    np.savez_compressed(path, orders=o, policy=str(policy), dataset=str(dataset),
                        heldout_digest=str(heldout_digest), meta_json=json.dumps(meta or {}))


def load_orders(path, n_expected: int = None, T_expected: int = None, heldout_digest: str = None) -> dict:
    z = np.load(path, allow_pickle=False)
    o = validate_orders(z["orders"], n_expected, T_expected)
    digest = str(z["heldout_digest"]) if "heldout_digest" in z.files else ""
    if heldout_digest is not None and digest and digest != str(heldout_digest):
        raise ValueError("orders file heldout_digest does not match the pool's heldout split "
                         "(wrong dataset / train_seed / row order).")
    return {"orders": o, "policy": str(z["policy"]), "dataset": str(z["dataset"]),
            "heldout_digest": digest,
            "meta": json.loads(str(z["meta_json"])) if "meta_json" in z.files else {}}
