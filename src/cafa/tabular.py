"""Tabular active-feature-acquisition rollout (Step 4).

``cafa.acquisition.rollout`` / ``GreedyEntropyPolicy`` are **image-specific**:
they hard-code the ``[N, P, D]`` patch geometry, the ``N_PATCHES`` constant,
per-patch-mean imputation and the 2-channel image build (``logits_from_patches``
-> ``patches_to_image``).  They are frozen and are *not* modified here.  Instead
this module provides a small, dataset-agnostic :func:`tabular_rollout` that
produces the **identical trajectory structure** -- ``scores[n, T+1]``,
``correct[n, T+1]``, ``cum_cost[n, T+1]`` with ``cum_cost[:, 0] == 0`` -- so the
frozen downstream machinery (:func:`cafa.metrics.stops_from_grid_np`,
:func:`cafa.risk_control.ltt_select` / :func:`~cafa.risk_control.mondrian_select`,
:func:`cafa.metrics.reference_buckets`, all baselines, the full-acquisition
fallback) works **unchanged**.

Feature model
-------------
A *feature* is one acquirable unit = one original column.  One-hot categoricals
occupy a contiguous block of encoded columns, so a feature owns a list of
encoded-column indices (``feature_groups[a]``); acquiring feature ``a`` reveals
that whole block at once.  The predictor sees the full encoded matrix
``X[n, n_cols]`` gated by a **column** mask that is constant within each block.

The orchestration is pure numpy: it only calls ``predictor.predict_proba(X_cols,
col_mask, device) -> [B, C]`` (numpy in, numpy out), so a numpy dummy predictor
works in tests and no torch is imported here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .scores import get_score_fn

__all__ = [
    "TabularTrajectories",
    "TabularGreedyEntropyPolicy",
    "TabularRandomPolicy",
    "get_tabular_policy",
    "expand_feature_mask",
    "tabular_rollout",
]

_EPS = 1e-12


@dataclass
class TabularTrajectories:
    """Per-instance tabular acquisition trajectories.

    Field-compatible with :class:`cafa.acquisition.Trajectories` so the same
    ``stops_from_grid_np`` / selection / bucketing code consumes both.

    Attributes
    ----------
    scores : np.ndarray [n, T+1]   readiness ``g_t`` in ``[0, 1]``.
    correct : np.ndarray [n, T+1]  1.0 if argmax == y else 0.0.
    cum_cost : np.ndarray [n, T+1] cumulative feature cost; ``cum_cost[:, 0]==0``.
    """

    scores: np.ndarray
    correct: np.ndarray
    cum_cost: np.ndarray


def _as_feature_groups(feature_groups, n_cols: int):
    """Normalise ``feature_groups`` to a list of int arrays over ``[0, n_cols)``.

    ``None`` -> each column is its own feature (identity grouping), which is the
    right default for all-numeric tabular data with no one-hot blocks.
    """
    if feature_groups is None:
        return [np.array([j], dtype=int) for j in range(int(n_cols))]
    groups = [np.asarray(g, dtype=int).ravel() for g in feature_groups]
    seen = np.concatenate(groups) if groups else np.array([], dtype=int)
    if seen.size != n_cols or set(seen.tolist()) != set(range(n_cols)):
        raise ValueError(
            "feature_groups must partition all encoded columns exactly once."
        )
    return groups


def expand_feature_mask(
    feat_mask: np.ndarray, feature_groups
) -> np.ndarray:
    """Broadcast a per-feature mask ``[B, d]`` to a per-column mask ``[B, n_cols]``.

    Every encoded column inherits its parent feature's observed bit, so a
    categorical's whole one-hot block flips on/off together.
    """
    feat_mask = np.asarray(feat_mask, dtype=np.float32)
    B, d = feat_mask.shape
    n_cols = int(sum(len(g) for g in feature_groups))
    col_mask = np.zeros((B, n_cols), dtype=np.float32)
    for a, cols in enumerate(feature_groups):
        col_mask[:, cols] = feat_mask[:, a : a + 1]
    return col_mask


# --------------------------------------------------------------------------- #
# Policies (order features; do not modify the predictor)
# --------------------------------------------------------------------------- #
class TabularGreedyEntropyPolicy:
    """EDDI-style myopic greedy acquisition by expected predictive entropy.

    Mirrors :class:`cafa.acquisition.GreedyEntropyPolicy` for tabular features:
    for every not-yet-acquired feature ``a`` it forms the hypothetical observed
    set ``O u {a}`` with ``a``'s columns imputed at their (standardised) mean --
    which is the zeroed value the masked predictor already uses -- runs the
    predictor, and acquires ``a* = argmin_a H(predictor)``.  The **true** columns
    of ``a*`` are then revealed.  Deterministic given the predictor.
    """

    name = "greedy_entropy"

    def __init__(self, cand_chunk: int = 16):
        self.cand_chunk = int(cand_chunk)

    @classmethod
    def from_training_data(cls, X_train, seed: int = 0):
        return cls()

    def select_next(self, predictor, X, observed_feat, feature_groups, device):
        """Choose the next feature per instance among the unobserved ones.

        Parameters
        ----------
        X : np.ndarray [B, n_cols]  -- true encoded values.
        observed_feat : np.ndarray [B, d] (0/1) -- current per-feature mask.
        feature_groups : list[np.ndarray] -- encoded columns per feature.

        Returns ``next_idx`` int array ``[B]`` -- the chosen feature per instance.
        """
        X = np.asarray(X, dtype=np.float32)
        B, n_cols = X.shape
        d = observed_feat.shape[1]
        base_col_mask = expand_feature_mask(observed_feat, feature_groups)  # [B, n_cols]

        ent = np.full((B, d), np.inf, dtype=float)
        # Evaluate candidate features in chunks: for each candidate we reveal its
        # columns in the *mask only* (values imputed at mean == the zeroed value),
        # so the base masked input is reused and one predict per candidate suffices.
        for a in range(d):
            cand_mask = base_col_mask.copy()
            cand_mask[:, feature_groups[a]] = 1.0
            probs = np.asarray(
                predictor.predict_proba(X, cand_mask, device=device), dtype=float
            )
            pc = np.clip(probs, _EPS, 1.0)
            ent[:, a] = -(probs * np.log(pc)).sum(axis=1)

        # Never pick an already-observed feature.
        ent = np.where(observed_feat > 0.5, np.inf, ent)
        return ent.argmin(axis=1).astype(int)


class TabularRandomPolicy:
    """Baseline: acquire a uniformly random unacquired feature each step."""

    name = "random"

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(int(seed))

    @classmethod
    def from_training_data(cls, X_train, seed: int = 0):
        return cls(seed=seed)

    def select_next(self, predictor, X, observed_feat, feature_groups, device):
        observed_feat = np.asarray(observed_feat, dtype=float)
        keys = self.rng.random(observed_feat.shape)
        keys = np.where(observed_feat > 0.5, -1.0, keys)
        return keys.argmax(axis=1).astype(int)


def get_tabular_policy(name: str, X_train=None, seed: int = 0):
    """Construct a tabular policy by name (mirrors ``acquisition.get_policy``)."""
    key = str(name).lower()
    if key in ("greedy_entropy", "greedy"):
        return TabularGreedyEntropyPolicy.from_training_data(X_train, seed=seed)
    if key == "random":
        return TabularRandomPolicy.from_training_data(X_train, seed=seed)
    raise ValueError(
        f"unknown policy {name!r}; expected 'greedy_entropy' or 'random'."
    )


# --------------------------------------------------------------------------- #
# Rollout
# --------------------------------------------------------------------------- #
def tabular_rollout(
    predictor,
    policy,
    score_fn,
    X: np.ndarray,
    y: np.ndarray,
    feature_costs: np.ndarray,
    feature_groups=None,
    device: str = "cpu",
    batch_size: int = 256,
) -> TabularTrajectories:
    """Run ``policy`` from empty to full acquisition; record per-step trajectories.

    Semantics match :func:`cafa.acquisition.rollout` exactly, but over tabular
    *features*: for each instance, start from the empty observed set; at each
    step ``t = 0..T`` (``T = d`` features) record ``g_t`` (readiness), whether
    the current argmax prediction is correct, and cumulative feature cost; then
    acquire the next feature chosen by ``policy`` and repeat.  Batched across
    instances.

    ``X`` is the full encoded matrix ``[N, n_cols]``; ``feature_costs`` is per
    *feature* ``[d]``; ``feature_groups`` maps each feature to its encoded
    columns (``None`` -> identity, one column per feature).  ``score_fn`` may be
    a callable ``probs[B,C] -> [B]`` or a name for :func:`cafa.scores.get_score_fn`.
    """
    if isinstance(score_fn, str):
        score_fn = get_score_fn(score_fn)
    if isinstance(policy, str):
        # Symmetric with ``score_fn``: allow a policy name. Use ``X`` itself as
        # the training reference for imputation/dim (callers with a separate
        # training split should pass a constructed policy instead).
        policy = get_tabular_policy(policy, X_train=X)

    X_np = np.asarray(X, dtype=np.float32)
    y_np = np.asarray(y).astype(np.int64)
    if X_np.ndim != 2:
        raise ValueError(f"X must be [N, n_cols]; got {X_np.shape}.")
    N, n_cols = X_np.shape
    groups = _as_feature_groups(feature_groups, n_cols)
    d = len(groups)
    feature_costs = np.asarray(feature_costs, dtype=float)
    if feature_costs.shape != (d,):
        raise ValueError(
            f"feature_costs must be [d]=({d},); got {feature_costs.shape}."
        )
    T = d

    scores = np.zeros((N, T + 1), dtype=float)
    correct = np.zeros((N, T + 1), dtype=float)
    cum_cost = np.zeros((N, T + 1), dtype=float)

    for start in range(0, N, batch_size):
        stop = min(start + batch_size, N)
        Xb = X_np[start:stop]                                   # [B, n_cols]
        yb = y_np[start:stop]                                   # [B]
        B = Xb.shape[0]
        observed = np.zeros((B, d), dtype=np.float32)           # per-feature mask
        running_cost = np.zeros(B, dtype=float)

        for t in range(T + 1):
            col_mask = expand_feature_mask(observed, groups)    # [B, n_cols]
            probs = np.asarray(
                predictor.predict_proba(Xb, col_mask, device=device), dtype=float
            )
            scores[start:stop, t] = np.asarray(score_fn(probs), dtype=float)
            pred = probs.argmax(axis=1)
            correct[start:stop, t] = (pred == yb).astype(float)
            cum_cost[start:stop, t] = running_cost

            if t == T:
                break  # all features acquired

            nxt = np.asarray(
                policy.select_next(predictor, Xb, observed, groups, device), dtype=int
            )
            running_cost = running_cost + feature_costs[nxt]
            observed[np.arange(B), nxt] = 1.0

    return TabularTrajectories(scores=scores, correct=correct, cum_cost=cum_cost)