"""v3 -- Synthetic trajectories with PLANTED stratum-wise feasibility (numpy).

Used by the validity / power study (E5) and the unit tests of the cascade and
the localized audit.  Everything is label-free except the drawn correctness,
and the true accuracy is known, so true stratum risks, true family minima and
true selective risks can be read off exactly.

Construction (``t = 0..T``), per instance ``i`` in stratum ``k`` (drawn with
mass ``q_k``), with a rise rate ``beta_i ~ Uniform(beta_lo_k, beta_hi_k)``::

    score_i(t)    = cap_i * (1 - exp(-beta_i t))          # readiness, in [0, 1)
    true_acc_i(t) = c0 + (A_i - c0) * (1 - exp(-3 beta_i t))   # converges faster than the score
    correct_i(t)  ~ Bernoulli(true_acc_i(t))
    cum_cost_i(t) = t

where ``A_i = 1 - r_easy_k`` and ``cap_i = 1`` for an "easy" instance and
``A_i = 1 - r_hard_k``, ``cap_i = s_cap_hard_k`` for a "hard" instance
(``hard ~ Bernoulli(h_k)``).  Hence:

* every rule in the threshold AND forced-depth family has stratum risk
  ``>= h_k r_hard_k + (1 - h_k) r_easy_k`` -- planting ``> alpha`` makes the
  stratum family-wide infeasible (Type II) with a known margin;
* the depth-``T`` readiness of a hard instance never exceeds ``s_cap_hard_k``,
  so escalating inputs with ``g_T < mu`` for ``mu > s_cap_hard_k`` answers only
  easy instances and the selective risk drops to about ``r_easy_k`` -- planting
  ``r_easy_k < alpha`` makes certified escalation feasible;
* ``overconfident_from_t`` (optional, per stratum) forces ``score = 1`` from a
  depth onward, so every constant threshold stops early while a forced depth
  still attains the target -- a planted Type I (stopping-rule) failure.

Deeper strata are given slower rise rates so that reference-depth buckets at
``lambda_ref`` recover the planted strata (up to integer-depth ties); the TRUE
stratum id is also returned (a label-free function of ``beta``), and both can be
used as the stratum map.
"""

from __future__ import annotations

import numpy as np

from .metrics import reference_buckets, reference_depth

__all__ = [
    "default_strata",
    "make_planted_population",
    "true_family_min_risk",
    "true_selective_risk",
    "true_stratum_risk_of_threshold",
    "depth_strata",
]


def default_strata(G: int = 4, masses=None):
    """Equal-mass strata with disjoint, decreasing rise-rate ranges."""
    masses = [1.0 / G] * G if masses is None else list(masses)
    lo, hi = 0.05, 0.6
    cuts = np.linspace(hi, lo, G + 1)   # descending: shallow stratum rises fastest
    out = []
    for k in range(G):
        out.append({
            "q": float(masses[k]),
            "beta": (float(cuts[k + 1]), float(cuts[k])),
            "r_easy": 0.03, "r_hard": 0.03, "h": 0.0, "s_cap_hard": 0.6,
            "overconfident_from_t": None,
        })
    return out


def make_planted_population(n: int, T: int, strata: list, seed: int = 0, c0: float = 0.1,
                            acc_rate_mult: float = 3.0) -> dict:
    """Draw ``n`` instances; see the module docstring for the construction.

    ``acc_rate_mult`` makes the true accuracy converge faster than the readiness
    score (rate ``acc_rate_mult * beta``), so that every instance has reached
    its accuracy cap at depth ``T`` and the planted caps are the full-information
    risks (the score may still be far from 1 for slow risers).
    """
    rng = np.random.default_rng(int(seed))
    G = len(strata)
    q = np.asarray([s["q"] for s in strata], dtype=float)
    q = q / q.sum()
    stratum = rng.choice(G, size=int(n), p=q)
    beta = np.empty(int(n), dtype=float)
    hard = np.zeros(int(n), dtype=bool)
    A = np.empty(int(n), dtype=float)
    cap = np.ones(int(n), dtype=float)
    for k, spec in enumerate(strata):
        m = stratum == k
        nk = int(m.sum())
        if nk == 0:
            continue
        lo, hi = spec["beta"]
        beta[m] = rng.uniform(float(lo), float(hi), size=nk)
        hk = rng.uniform(size=nk) < float(spec.get("h", 0.0))
        hard[m] = hk
        A[m] = np.where(hk, 1.0 - float(spec.get("r_hard", 0.0)), 1.0 - float(spec.get("r_easy", 0.0)))
        cap[m] = np.where(hk, float(spec.get("s_cap_hard", 1.0)), 1.0)

    t = np.arange(int(T) + 1, dtype=float)[None, :]
    rise = 1.0 - np.exp(-beta[:, None] * t)                      # [n, T+1]
    rise_acc = 1.0 - np.exp(-float(acc_rate_mult) * beta[:, None] * t)
    scores = cap[:, None] * rise
    true_acc = np.clip(float(c0) + (A[:, None] - float(c0)) * rise_acc, 0.0, 1.0)
    for k, spec in enumerate(strata):
        oc = spec.get("overconfident_from_t")
        if oc is not None:
            m = stratum == k
            scores[m, int(oc):] = 1.0
    correct = (rng.uniform(size=scores.shape) < true_acc).astype(float)
    cum_cost = np.tile(t, (int(n), 1)).astype(float)
    return {
        "scores": scores, "correct": correct, "true_acc": true_acc, "cum_cost": cum_cost,
        "stratum": stratum.astype(int), "is_hard": hard, "beta": beta, "T": int(T),
        "y": np.zeros(int(n), dtype=np.int64),
    }


def true_family_min_risk(pop: dict, k: int, grid: np.ndarray) -> "tuple[float, float]":
    """Exact (min over thresholds, min over depths) of TRUE stratum-k risk."""
    m = pop["stratum"] == k
    acc = pop["true_acc"][m]
    sc = pop["scores"][m]
    T = pop["T"]
    grid = np.asarray(grid, dtype=float)
    crossed = sc[:, :, None] >= grid[None, None, :]
    any_cross = crossed.any(axis=1)
    first = crossed.argmax(axis=1)
    s = np.where(any_cross, first, T).astype(int)
    rows = np.arange(acc.shape[0])[:, None]
    r_thr = (1.0 - acc[rows, s]).mean(axis=0)
    r_dep = (1.0 - acc).mean(axis=0)
    return float(r_thr.min()), float(r_dep.min())


def true_stratum_risk_of_threshold(pop: dict, bucket_id: np.ndarray, lam: float) -> dict:
    """TRUE risk of threshold rule ``lam`` within each bucket of ``bucket_id``."""
    sc, acc, T = pop["scores"], pop["true_acc"], pop["T"]
    crossed = sc >= float(lam)
    any_cross = crossed.any(axis=1)
    first = crossed.argmax(axis=1)
    s = np.where(any_cross, first, T).astype(int)
    r = 1.0 - acc[np.arange(sc.shape[0]), s]
    b = np.asarray(bucket_id)
    return {int(k): float(r[b == k].mean()) for k in np.unique(b)}


def true_selective_risk(pop: dict, bucket_id: np.ndarray, mu: float) -> dict:
    """TRUE selective risk at depth T of the escalation rule ``mu`` per bucket
    (``nan`` where nobody is answered)."""
    T = pop["T"]
    ans = pop["scores"][:, T] >= float(mu)
    r = 1.0 - pop["true_acc"][:, T]
    b = np.asarray(bucket_id)
    out = {}
    for k in np.unique(b):
        m = (b == k) & ans
        out[int(k)] = float(r[m].mean()) if m.any() else float("nan")
    return out


def depth_strata(scores: np.ndarray, lambda_ref: float, edges: np.ndarray) -> np.ndarray:
    """Label-free reference-depth strata with committed ``edges``."""
    bid, _ = reference_buckets(scores, float(lambda_ref), 5, 1, edges=np.asarray(edges, dtype=float))
    return bid
