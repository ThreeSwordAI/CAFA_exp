"""WO-13 -- Phase-2 epsilon-greedy mixture policy (tabular; torch-free).

At each acquisition step, with probability ``epsilon`` acquire a uniformly
random unacquired feature, else take the wrapped greedy policy's choice.  The
RNG is seeded once per pool rollout (``policy_seed = 10_000 + round(1000*eps)``,
set by the runner) so the mixture is deterministic.

The MNIST (patch) variant lives in ``scripts/run_pool_rollout.py`` because it
mirrors the frozen torch rollout loop; this module is the tabular wrapper and
exposes the same ``select_next`` signature as :mod:`cafa.tabular` policies, so
the rollout, eval sweep and analysis all key on the policy string
(``eps_greedy_eps0.25`` etc.) with no further plumbing.
"""

from __future__ import annotations

import numpy as np

__all__ = ["EpsGreedyMixture", "eps_greedy_policy_token"]


def eps_greedy_policy_token(epsilon: float) -> str:
    """Canonical policy string used in cache filenames and JSON ``policy`` fields."""
    return f"eps_greedy_eps{float(epsilon):g}"


class EpsGreedyMixture:
    """Epsilon-greedy wrapper over a tabular greedy policy.

    Parameters
    ----------
    greedy_policy : object
        A policy exposing ``select_next(predictor, X, observed_feat,
        feature_groups, device) -> [B]`` (e.g.
        :class:`cafa.tabular.TabularGreedyEntropyPolicy`).
    epsilon : float
        Per-step probability of a uniformly random unacquired feature.
    seed : int
        RNG seed (the runner passes ``10_000 + round(1000*epsilon)``).
    """

    def __init__(self, greedy_policy, epsilon: float, seed: int):
        self.greedy = greedy_policy
        self.epsilon = float(epsilon)
        self.rng = np.random.default_rng(int(seed))
        self.name = eps_greedy_policy_token(epsilon)

    def select_next(self, predictor, X, observed_feat, feature_groups, device):
        observed = np.asarray(observed_feat, dtype=float)
        B = observed.shape[0]

        greedy_pick = np.asarray(
            self.greedy.select_next(predictor, X, observed_feat, feature_groups, device),
            dtype=int,
        )
        # Random unacquired feature per instance (observed features masked out).
        keys = self.rng.random(observed.shape)
        keys = np.where(observed > 0.5, -1.0, keys)
        random_pick = keys.argmax(axis=1).astype(int)

        take_random = self.rng.random(B) < self.epsilon
        return np.where(take_random, random_pick, greedy_pick).astype(int)
