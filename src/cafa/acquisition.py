"""Acquisition policies and the rollout that bridges to the frozen selector.

A *policy* orders patch-features per instance at inference time; it does **not**
change the predictor.  The *rollout* runs a policy from the empty observed set
to full acquisition, recording at every step ``t = 0..T`` the readiness score
``g_t``, whether the current argmax prediction is correct, and the cumulative
acquisition cost.  :func:`stops_from_grid` then turns those trajectories into
the ``(losses, costs, stop_depth)`` matrices that
:func:`cafa.risk_control.ltt_select` consumes -- one rollout per (model, split,
seed) yields the whole ``lambda``-grid (and, later, all baselines).

Conventions (shared with :mod:`cafa.models`)
--------------------------------------------
* ``X`` patchified: ``[N, P, D]`` (P = 49 patches, D = 16 pixels), row-major.
* a patch mask is ``[N, P]`` with 1.0 = observed.
* ``feature_costs`` is ``[P]`` (uniform ones for MNIST); ``T = P``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch

from .models import N_PATCHES
from .scores import get_score_fn

__all__ = [
    "Trajectories",
    "GreedyEntropyPolicy",
    "RandomPolicy",
    "get_policy",
    "rollout",
    "stops_from_grid",
]

_EPS = 1e-12


# --------------------------------------------------------------------------- #
# Trajectory container (rollout output)
# --------------------------------------------------------------------------- #
@dataclass
class Trajectories:
    """Per-instance acquisition trajectories (rollout output).

    Attributes
    ----------
    scores : np.ndarray, shape [n, T+1]
        Readiness ``g_t`` at step ``t`` (number of patches acquired), in [0, 1].
    correct : np.ndarray, shape [n, T+1]
        1.0 if the argmax prediction at step ``t`` equals ``y`` else 0.0.
    cum_cost : np.ndarray, shape [n, T+1]
        Cumulative acquisition cost; ``cum_cost[:, 0] == 0``.
    """

    scores: np.ndarray
    correct: np.ndarray
    cum_cost: np.ndarray


# --------------------------------------------------------------------------- #
# Policies (order features; do not modify the predictor)
# --------------------------------------------------------------------------- #
class GreedyEntropyPolicy:
    """EDDI-style myopic greedy acquisition by expected predictive entropy.

    At each step, for every not-yet-acquired patch ``a``: impute patch ``a`` with
    its **per-patch training mean** (precomputed once), run the predictor on the
    hypothetical observed set ``O u {a}`` (all candidates batched in one forward
    pass), and acquire ``a* = argmin_a H(predictor)`` -- the patch whose
    hypothetical reveal yields the most confident (lowest-entropy) prediction.
    The **true** patch ``a*`` is then revealed and acquisition continues.  Stops
    are applied post-hoc by the grid, so the policy just produces the full
    acquisition order.

    Deterministic given the predictor and the imputation means.
    """

    name = "greedy_entropy"

    def __init__(self, patch_means: np.ndarray):
        pm = np.asarray(patch_means, dtype=np.float32)
        if pm.ndim != 2 or pm.shape[0] != N_PATCHES:
            raise ValueError(
                f"patch_means must be [P, D] with P={N_PATCHES}; got {pm.shape}."
            )
        self.patch_means = pm

    @classmethod
    def from_training_data(cls, X_train: np.ndarray) -> "GreedyEntropyPolicy":
        """Precompute per-patch means ``[P, D]`` from patchified training data."""
        X = np.asarray(X_train, dtype=np.float32)
        if X.ndim != 3:
            raise ValueError(f"X_train must be [N, P, D]; got {X.shape}.")
        return cls(X.mean(axis=0))

    @torch.no_grad()
    def select_next(
        self,
        predictor,
        X: torch.Tensor,
        observed: torch.Tensor,
        device,
        cand_chunk: int = 8,
    ) -> torch.Tensor:
        """Choose the next patch per instance among the unobserved ones.

        Parameters
        ----------
        X : torch.Tensor [B, P, D]   -- true patch pixels.
        observed : torch.Tensor [B, P] (0/1 float) -- current observed mask.
        cand_chunk : int
            How many candidate patches to evaluate per forward pass.  Peak memory
            is ``O(B * cand_chunk * P * D)`` rather than ``O(B * P * P * D)``,
            which keeps the greedy rollout tractable for large batches.

        Returns ``next_idx`` LongTensor [B] -- the chosen patch per instance.
        """
        B, P, D = X.shape
        means = torch.as_tensor(self.patch_means, dtype=X.dtype, device=device)  # [P, D]

        # Base imputed pixels/mask for the *current* observed set (shared by all
        # candidates): observed patches keep true pixels, hidden patches get the
        # per-patch mean.  Each candidate then additionally reveals one patch.
        obs3 = observed.unsqueeze(-1)                              # [B, P, 1]
        base_pix = torch.where(obs3 > 0.5, X, means.unsqueeze(0))  # [B, P, D]
        means_row = means.unsqueeze(0)                            # [1, P, D]

        ent = torch.full((B, P), float("inf"), device=device, dtype=base_pix.dtype)
        for c0 in range(0, P, int(cand_chunk)):
            cands = list(range(c0, min(c0 + int(cand_chunk), P)))
            kc = len(cands)
            # Build [B, kc, P, D] / [B, kc, P] only for this chunk of candidates.
            pix = base_pix.unsqueeze(1).expand(B, kc, P, D).clone()
            msk = observed.unsqueeze(1).expand(B, kc, P).clone()
            for j, a in enumerate(cands):
                # Reveal patch a: impute its mean pixels and set its mask bit.
                pix[:, j, a, :] = means_row[0, a, :]
                msk[:, j, a] = 1.0
            flat_pix = pix.reshape(B * kc, P, D)
            flat_msk = msk.reshape(B * kc, P)
            logits = predictor.logits_from_patches(flat_pix, flat_msk)  # [B*kc, C]
            probs = torch.softmax(logits, dim=1)
            e = -(probs * torch.log(probs.clamp_min(_EPS))).sum(dim=1)  # [B*kc]
            ent[:, c0 : c0 + kc] = e.view(B, kc)

        # Never pick an already-observed patch.
        ent = ent.masked_fill(observed > 0.5, float("inf"))
        return ent.argmin(dim=1)


class RandomPolicy:
    """Baseline: acquire a uniformly random unacquired patch each step."""

    name = "random"

    def __init__(self, seed: int = 0):
        self.seed = int(seed)

    @classmethod
    def from_training_data(cls, X_train: np.ndarray, seed: int = 0) -> "RandomPolicy":
        return cls(seed=seed)

    @torch.no_grad()
    def select_next(self, predictor, X, observed, device) -> torch.Tensor:
        # Random keys over unobserved patches; +inf-equivalent on observed.
        scores = torch.rand(observed.shape, device=device)
        scores = scores.masked_fill(observed > 0.5, -1.0)
        return scores.argmax(dim=1)


def get_policy(name: str, X_train: np.ndarray, seed: int = 0):
    """Construct a policy by ``--backbone`` name from patchified training data."""
    key = str(name).lower()
    if key in ("greedy_entropy", "greedy"):
        return GreedyEntropyPolicy.from_training_data(X_train)
    if key == "random":
        return RandomPolicy.from_training_data(X_train, seed=seed)
    raise ValueError(f"unknown policy {name!r}; expected 'greedy_entropy' or 'random'.")


# --------------------------------------------------------------------------- #
# Rollout
# --------------------------------------------------------------------------- #
def rollout(
    predictor,
    policy,
    score_fn,
    X: np.ndarray,
    y: np.ndarray,
    feature_costs: np.ndarray,
    device: "torch.device | str" = "cpu",
    batch_size: int = 256,
) -> Trajectories:
    """Run ``policy`` from empty to full acquisition; record per-step trajectories.

    For each instance: start from the empty observed set; at each step
    ``t = 0..T`` record ``g_t`` (readiness), correctness of the current argmax
    prediction, and cumulative cost; then acquire the next patch chosen by
    ``policy`` and repeat until all ``T = P`` patches are acquired.  Batched
    across instances for speed.

    ``score_fn`` may be a callable ``probs[B,C] -> [B]`` or a string name passed
    to :func:`cafa.scores.get_score_fn`.
    """
    if isinstance(score_fn, str):
        score_fn = get_score_fn(score_fn)

    device = torch.device(device)
    X_np = np.asarray(X, dtype=np.float32)
    y_np = np.asarray(y).astype(np.int64)
    if X_np.ndim != 3:
        raise ValueError(f"X must be [N, P, D]; got {X_np.shape}.")
    N, P, _ = X_np.shape
    feature_costs = np.asarray(feature_costs, dtype=float)
    if feature_costs.shape != (P,):
        raise ValueError(f"feature_costs must be [P]=({P},); got {feature_costs.shape}.")
    T = P

    scores = np.zeros((N, T + 1), dtype=float)
    correct = np.zeros((N, T + 1), dtype=float)
    cum_cost = np.zeros((N, T + 1), dtype=float)

    costs_t = torch.as_tensor(feature_costs, dtype=torch.float32, device=device)

    for start in range(0, N, batch_size):
        stop = min(start + batch_size, N)
        Xb = torch.as_tensor(X_np[start:stop], device=device)         # [B, P, D]
        yb = torch.as_tensor(y_np[start:stop], device=device)         # [B]
        B = Xb.shape[0]
        observed = torch.zeros((B, P), dtype=torch.float32, device=device)
        running_cost = torch.zeros(B, dtype=torch.float32, device=device)

        for t in range(T + 1):
            # Record current state (predict on the current observed set).
            probs = predictor.predict_proba(Xb, observed, device=device)  # np [B, C]
            scores[start:stop, t] = np.asarray(score_fn(probs), dtype=float)
            pred = probs.argmax(axis=1)
            correct[start:stop, t] = (pred == y_np[start:stop]).astype(float)
            cum_cost[start:stop, t] = running_cost.detach().cpu().numpy()

            if t == T:
                break  # all patches acquired; nothing left to choose

            nxt = policy.select_next(predictor, Xb, observed, device)     # [B]
            # Reveal chosen patch; add its cost.
            running_cost = running_cost + costs_t[nxt]
            observed = observed.clone()
            observed[torch.arange(B, device=device), nxt] = 1.0

    return Trajectories(scores=scores, correct=correct, cum_cost=cum_cost)


# --------------------------------------------------------------------------- #
# Grid -> selector inputs
# --------------------------------------------------------------------------- #
def stops_from_grid(
    traj: Trajectories, grid: np.ndarray
) -> "tuple[np.ndarray, np.ndarray, np.ndarray]":
    """Turn trajectories into ``(losses, costs, stop_depth)`` for ``ltt_select``.

    ``grid`` ascending.  For each instance ``i`` and threshold ``lambda_j``::

        s = first t in 0..T with scores[i, t] >= lambda_j ; if none, s = T
        losses[i, j]     = 1.0 - correct[i, s]
        costs[i, j]      = cum_cost[i, s]
        stop_depth[i, j] = s

    Returns ``(losses[n, G], costs[n, G], stop_depth[n, G])`` -- exactly what the
    frozen selector consumes.  Vectorized over the grid (no Python loop over
    thresholds).
    """
    scores = np.asarray(traj.scores, dtype=float)         # [n, T+1]
    correct = np.asarray(traj.correct, dtype=float)       # [n, T+1]
    cum_cost = np.asarray(traj.cum_cost, dtype=float)     # [n, T+1]
    grid = np.asarray(grid, dtype=float)                  # [G]
    if np.any(np.diff(grid) < 0):
        raise ValueError("grid must be in ascending order.")

    n, Tp1 = scores.shape
    T = Tp1 - 1
    G = grid.shape[0]

    # crossed[i, t, j] = scores[i, t] >= grid[j]
    crossed = scores[:, :, None] >= grid[None, None, :]   # [n, T+1, G]
    any_cross = crossed.any(axis=1)                       # [n, G]
    # First crossing index along t; if none, argmax over all-False gives 0, so
    # override with T where no crossing exists.
    first = crossed.argmax(axis=1)                        # [n, G] (0 if none)
    s = np.where(any_cross, first, T).astype(int)         # [n, G]

    rows = np.arange(n)[:, None]                           # [n, 1] broadcast over G
    correct_at_s = correct[rows, s]                       # [n, G]
    losses = 1.0 - correct_at_s
    costs = cum_cost[rows, s]
    stop_depth = s.astype(float)
    return losses, costs, stop_depth