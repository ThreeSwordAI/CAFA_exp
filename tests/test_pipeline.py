"""Fast smoke test for the Step-2 pipeline wiring (no training, no download).

This checks that a rollout over a *dummy* predictor produces trajectories of the
right shape and semantics, that :func:`cafa.acquisition.stops_from_grid`
implements the "first crossing, else T" rule (hand-checked on a tiny case) and
the ``cum_cost[:, 0] == 0`` convention, and that the resulting arrays flow into
the frozen :func:`cafa.risk_control.ltt_select` and return a ``SelectionResult``.

It does **not** import or modify ``tests/test_risk_control.py`` (the frozen G1
gate).  Runs in well under a couple of seconds.

    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    pytest -q tests/test_pipeline.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cafa.acquisition import Trajectories, rollout, stops_from_grid  # noqa: E402
from cafa.models import N_PATCHES, PATCH_DIM  # noqa: E402
from cafa.risk_control import SelectionResult, ltt_select  # noqa: E402
from cafa.scores import get_score_fn  # noqa: E402


class DummyPredictor:
    """A predictor stand-in that returns fixed pseudo-random probabilities.

    It mimics the :class:`cafa.models.MaskedPredictor` surface used by the
    rollout and the greedy policy: ``predict_proba(images, masks)`` -> ``[B, C]``
    numpy, and ``logits_from_patches(patches, mask)`` -> torch ``[B, C]``.  The
    probabilities depend only on how many patches are observed, so readiness
    rises monotonically with acquisition (a clean signal for the crossing test),
    but never on the labels (so it is a genuine dummy).
    """

    def __init__(self, n_classes: int = 4):
        self.n_classes = n_classes

    def predict_proba(self, images, masks, device=None):
        import torch

        masks = torch.as_tensor(masks, dtype=torch.float32)
        B = masks.shape[0]
        frac = masks.float().mean(dim=1, keepdim=True)  # [B, 1] in [0, 1]
        # Sharpen class 0 as more patches are observed; keep it a valid simplex.
        logits = torch.zeros(B, self.n_classes)
        logits[:, 0] = 4.0 * frac.squeeze(1)
        probs = torch.softmax(logits, dim=1)
        return probs.detach().cpu().numpy()

    def logits_from_patches(self, patches, mask):
        import torch

        mask = torch.as_tensor(mask, dtype=torch.float32)
        B = mask.shape[0]
        frac = mask.float().mean(dim=1, keepdim=True)
        logits = torch.zeros(B, self.n_classes)
        logits[:, 0] = 4.0 * frac.squeeze(1)
        return logits


class _SequentialPolicy:
    """Deterministic policy: always acquire the lowest-index unobserved patch."""

    name = "sequential"

    def select_next(self, predictor, X, observed, device):
        import torch

        scores = torch.where(observed > 0.5, torch.full_like(observed, 1e9), -observed)
        # Pick the smallest index among unobserved (observed get +inf penalty).
        penalized = torch.where(observed > 0.5, torch.full_like(observed, 1e9),
                                torch.arange(observed.shape[1], device=observed.device)
                                .float().unsqueeze(0).expand_as(observed))
        return penalized.argmin(dim=1)


def _tiny_batch(n=5, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.random((n, N_PATCHES, PATCH_DIM)).astype(np.float32)
    y = rng.integers(0, 4, size=n).astype(np.int64)
    feature_costs = np.ones(N_PATCHES, dtype=float)
    return X, y, feature_costs


def test_rollout_shapes_and_conventions():
    """Rollout output shapes; scores in [0,1]; cum_cost[:,0]==0 and non-decreasing."""
    X, y, feature_costs = _tiny_batch(n=6)
    pred = DummyPredictor(n_classes=4)
    traj = rollout(pred, _SequentialPolicy(), get_score_fn("softmax"), X, y, feature_costs, device="cpu")

    n, T = X.shape[0], N_PATCHES
    assert isinstance(traj, Trajectories)
    assert traj.scores.shape == (n, T + 1)
    assert traj.correct.shape == (n, T + 1)
    assert traj.cum_cost.shape == (n, T + 1)

    assert np.all(traj.scores >= 0.0) and np.all(traj.scores <= 1.0)
    assert set(np.unique(traj.correct)).issubset({0.0, 1.0})

    # cost convention: start at 0, non-decreasing, end at sum of all feature costs.
    assert np.allclose(traj.cum_cost[:, 0], 0.0)
    assert np.all(np.diff(traj.cum_cost, axis=1) >= -1e-9)
    assert np.allclose(traj.cum_cost[:, -1], feature_costs.sum())


def test_stops_from_grid_shapes_and_ranges():
    """stops_from_grid returns [n,G]; losses in {0,1}; costs>=0; depths in [0,T]."""
    X, y, feature_costs = _tiny_batch(n=7)
    pred = DummyPredictor(n_classes=4)
    traj = rollout(pred, _SequentialPolicy(), "softmax", X, y, feature_costs, device="cpu")

    grid = np.linspace(0.0, 1.0, 20)
    losses, costs, stop_depth = stops_from_grid(traj, grid)

    n, G = X.shape[0], grid.size
    assert losses.shape == (n, G)
    assert costs.shape == (n, G)
    assert stop_depth.shape == (n, G)

    assert set(np.unique(losses)).issubset({0.0, 1.0})
    assert np.all(costs >= 0.0)
    assert np.all(stop_depth >= 0) and np.all(stop_depth <= N_PATCHES)


def test_stops_from_grid_first_crossing_handchecked():
    """Hand-checked tiny case for the 'first t with score>=lambda, else T' rule."""
    # One instance, T = 4 (so T+1 = 5 steps).  Scores rise then are flat.
    scores = np.array([[0.10, 0.30, 0.50, 0.80, 0.80]])
    correct = np.array([[0.0, 0.0, 1.0, 1.0, 1.0]])
    cum_cost = np.array([[0.0, 1.0, 2.0, 3.0, 4.0]])
    traj = Trajectories(scores=scores, correct=correct, cum_cost=cum_cost)

    grid = np.array([0.05, 0.30, 0.55, 0.99])  # ascending
    losses, costs, stop_depth = stops_from_grid(traj, grid)

    # lambda=0.05 -> first t with score>=0.05 is t=0 -> correct=0 -> loss=1, cost=0, s=0
    # lambda=0.30 -> first >=0.30 is t=1 -> correct=0 -> loss=1, cost=1, s=1
    # lambda=0.55 -> first >=0.55 is t=3 (0.80) -> correct=1 -> loss=0, cost=3, s=3
    # lambda=0.99 -> never crossed -> s=T=4 -> correct=1 -> loss=0, cost=4, s=4
    assert stop_depth[0].tolist() == [0.0, 1.0, 3.0, 4.0]
    assert losses[0].tolist() == [1.0, 1.0, 0.0, 0.0]
    assert costs[0].tolist() == [0.0, 1.0, 3.0, 4.0]


def test_pipeline_feeds_ltt_select():
    """The full chain rollout -> stops_from_grid -> ltt_select returns a result."""
    X, y, feature_costs = _tiny_batch(n=40, seed=3)
    pred = DummyPredictor(n_classes=4)
    traj = rollout(pred, _SequentialPolicy(), "softmax", X, y, feature_costs, device="cpu")

    grid = np.linspace(0.0, 1.0, 25)
    losses, costs, _ = stops_from_grid(traj, grid)

    # Sanity for the selector's input contract.
    assert losses.shape == costs.shape == (X.shape[0], grid.size)
    assert np.all((losses >= 0.0) & (losses <= 1.0))
    assert np.all(costs >= 0.0)
    assert np.all(np.diff(grid) >= 0.0)

    sel = ltt_select(losses, costs, grid, alpha=0.2, delta=0.1, procedure="fixed_sequence")
    assert isinstance(sel, SelectionResult)
    assert sel.r_hat.shape == (grid.size,)
    assert sel.c_hat.shape == (grid.size,)
    assert sel.valid_mask.shape == (grid.size,)
    # lambda_idx is either None or a valid column index.
    assert sel.lambda_idx is None or 0 <= sel.lambda_idx < grid.size