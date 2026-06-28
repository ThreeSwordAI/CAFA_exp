"""Readiness scores ``g_t(probs) -> [0, 1]``.

A *readiness score* maps predictive probabilities ``p [B, C]`` to a scalar in
``[0, 1]`` per instance, measuring how "ready to stop" the model is at the
current observed set.  Because the scores live in ``[0, 1]`` they sit on the
same axis as the stopping threshold ``lambda`` consumed by the frozen
:func:`cafa.risk_control.ltt_select`: the rollout records ``g_t`` at every
acquisition step and :func:`cafa.acquisition.stops_from_grid` turns a
``lambda`` into "stop at the first step with ``g_t >= lambda``".

All scores are **higher = more confident / more ready to stop**, so a larger
``lambda`` demands more confidence and (typically) more acquisitions.

This module is numpy-only and torch-free; the predictor produces the
probabilities, scores only post-process them.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

__all__ = ["softmax_score", "margin_score", "entropy_score", "set_size_score", "get_score_fn"]

_EPS = 1e-12


def _as_2d_probs(p: np.ndarray) -> np.ndarray:
    """Validate / coerce ``p`` to a float array of shape ``[B, C]``."""
    p = np.asarray(p, dtype=float)
    if p.ndim == 1:
        p = p[None, :]
    if p.ndim != 2:
        raise ValueError(f"probs must be [B, C] (or [C]); got shape {p.shape}.")
    return p


def softmax_score(p: np.ndarray) -> np.ndarray:
    """Maximum class probability ``max_c p_c`` (the default readiness score).

    Returns shape ``[B]`` in ``[0, 1]``.  This is the standard top-1 softmax
    confidence: ``1/C`` at the uniform (uninformative) prediction, ``1`` when
    the model is certain.
    """
    p = _as_2d_probs(p)
    return p.max(axis=1)


def margin_score(p: np.ndarray) -> np.ndarray:
    """Top-1 minus top-2 probability, ``p_(1) - p_(2)``.

    Returns shape ``[B]`` in ``[0, 1]``.  ``0`` when the two best classes are
    tied (maximally unsure between them), up to ``1`` when one class has all
    the mass.
    """
    p = _as_2d_probs(p)
    if p.shape[1] < 2:
        # Degenerate single-class case: margin is just the (only) probability.
        return p.max(axis=1)
    # Partition so the two largest values are in the last two slots.
    part = np.partition(p, -2, axis=1)
    top1 = part[:, -1]
    top2 = part[:, -2]
    return np.clip(top1 - top2, 0.0, 1.0)


def entropy_score(p: np.ndarray) -> np.ndarray:
    """Normalized negative entropy ``1 - H(p) / log(C)``.

    Returns shape ``[B]`` in ``[0, 1]``.  ``0`` at the uniform distribution
    (maximum entropy ``H = log C``), ``1`` at a one-hot distribution
    (``H = 0``).  Higher = more confident, matching the other scores.
    """
    p = _as_2d_probs(p)
    C = p.shape[1]
    if C <= 1:
        return np.ones(p.shape[0], dtype=float)
    pc = np.clip(p, _EPS, 1.0)
    H = -np.sum(p * np.log(pc), axis=1)            # natural-log entropy
    return np.clip(1.0 - H / np.log(C), 0.0, 1.0)


def set_size_score(p: np.ndarray) -> np.ndarray:
    """Conformal prediction-set-size readiness (arrives with calibration).

    A set-size score needs a conformal calibration step (a per-step quantile of
    nonconformity scores) to turn ``p`` into a prediction set whose size maps to
    readiness.  That calibration is added in a later step; until then this is a
    deliberate stub so the dispatcher name exists without a silent wrong answer.
    """
    raise NotImplementedError(
        "set_size readiness requires conformal calibration (added in a later step)."
    )


_SCORE_FNS: dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "softmax": softmax_score,
    "margin": margin_score,
    "entropy": entropy_score,
    "set_size": set_size_score,
}


def get_score_fn(name: str) -> Callable[[np.ndarray], np.ndarray]:
    """Return the readiness score function registered under ``name``.

    Valid names: ``"softmax"`` (default), ``"margin"``, ``"entropy"``,
    ``"set_size"`` (stub).  Each takes ``probs [B, C]`` and returns ``[B]`` in
    ``[0, 1]``.
    """
    key = str(name).lower()
    if key not in _SCORE_FNS:
        raise ValueError(
            f"unknown score {name!r}; expected one of {sorted(_SCORE_FNS)}."
        )
    return _SCORE_FNS[key]