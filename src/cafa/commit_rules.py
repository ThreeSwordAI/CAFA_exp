"""v3 -- Probe-committed design rules: lambda_ref, number of strata, escalation levels.

Everything in this module is a function of the INDEPENDENT PROBE split only
(plus fixed configuration), so the resulting stratum map, reference threshold
and escalation grid are fixed independently of every calibration draw and of
the audit labels, exactly as Theorems 2--4 require.

Rules
-----
``deployment_aligned_lambda_ref``
    lambda_ref := the plug-in operating point on the probe (the smallest grid
    threshold whose probe risk is <= alpha; the top of the grid if none).
    Strata are then quantile bins of the depth at which the rule the system
    will actually deploy becomes confident -- the decision-relevant partition.
``n_min_required``
    Number of stratum examples needed so that a rule with stratum risk
    ``alpha - margin`` is certifiable at the per-tier level (Hoeffding term of
    the HB p-value): ``n_min = ln(1/level) / kl(alpha - margin || alpha)``.
``detectability_limited_edges``
    Start from ``n_buckets`` probe-quantile cut points of the reference depth
    and merge bins until every bin's expected calibration count is >= n_min.
    This makes "refused because the stratum was too small" impossible by
    construction; the number of strata shrinks on small datasets instead.
``escalation_levels``
    Escalation thresholds ``mu_j`` are probe quantiles of the depth-T readiness
    score indexed by target answered fractions ``a_j``, so the most conservative
    level still answers a known fraction and the tier-3 fixed sequence never
    starts at an empty answered set.
"""

from __future__ import annotations

import math

import numpy as np

from .metrics import reference_depth, stops_from_grid_np

__all__ = [
    "escalation_fractions",
    "escalation_order_from_probe",
    "plugin_lambda_on_probe",
    "deployment_aligned_lambda_ref",
    "kl_bernoulli",
    "n_min_required",
    "quantile_depth_edges",
    "detectability_limited_edges",
    "escalation_levels",
]


def plugin_lambda_on_probe(
    probe_scores: np.ndarray,
    probe_correct: np.ndarray,
    grid: np.ndarray,
    alpha: float,
) -> "tuple[float, int]":
    """Smallest grid threshold whose PROBE risk is <= alpha (``(value, index)``).

    Falls back to the top of the grid when no threshold attains alpha on the
    probe (then strata are defined by the full-acquisition-depth trajectory).
    """
    grid = np.asarray(grid, dtype=float)
    cc = np.zeros_like(np.asarray(probe_scores, dtype=float))
    losses, _, _ = stops_from_grid_np(probe_scores, probe_correct, cc, grid)
    r_hat = losses.mean(axis=0)
    ok = np.flatnonzero(r_hat <= float(alpha))
    if ok.size == 0:
        j = int(grid.shape[0] - 1)
    else:
        j = int(ok.min())
    return float(grid[j]), j


def deployment_aligned_lambda_ref(
    probe_scores: np.ndarray,
    probe_correct: np.ndarray,
    grid: np.ndarray,
    alpha: float,
) -> float:
    """The committed deployment-aligned reference threshold (see module doc)."""
    value, _ = plugin_lambda_on_probe(probe_scores, probe_correct, grid, alpha)
    return float(value)


def kl_bernoulli(a: float, b: float) -> float:
    """Binary relative entropy ``kl(a || b)`` with the usual limits."""
    a = float(a)
    b = float(b)
    if not (0.0 < b < 1.0):
        raise ValueError("b must be in (0, 1).")
    out = 0.0
    if a > 0.0:
        out += a * math.log(a / b)
    if a < 1.0:
        out += (1.0 - a) * math.log((1.0 - a) / (1.0 - b))
    return out


def n_min_required(alpha: float, level: float, margin: float = 0.05) -> int:
    """Stratum size needed to certify a rule with stratum risk ``alpha - margin``.

    From the Hoeffding term of the Hoeffding--Bentkus p-value:
    ``exp(-n kl(alpha - margin || alpha)) <= level`` iff
    ``n >= ln(1/level) / kl(alpha - margin || alpha)``.  Rounded up.
    (At alpha = 0.15, level = 0.05, margin = 0.05 this is 275.)
    """
    a = float(alpha) - float(margin)
    if a <= 0.0:
        raise ValueError("alpha - margin must be positive.")
    k = kl_bernoulli(a, float(alpha))
    return int(math.ceil(math.log(1.0 / float(level)) / k))


def quantile_depth_edges(depths: np.ndarray, n_buckets: int) -> np.ndarray:
    """Distinct probe-quantile interior cut points of integer reference depths."""
    d = np.asarray(depths, dtype=float)
    qs = np.linspace(0.0, 1.0, int(n_buckets) + 1)[1:-1]
    return np.unique(np.quantile(d, qs))


def detectability_limited_edges(
    probe_depths: np.ndarray,
    n_buckets: int,
    n_cal_expected: int,
    n_min: int,
) -> "tuple[np.ndarray, int, np.ndarray]":
    """Merge probe-quantile depth bins until each bin's expected cal count >= n_min.

    ``n_cal_expected`` is the number of rows a calibration draw will contain;
    the expected count of bin ``k`` is ``n_cal_expected * (probe fraction of
    bin k)``.  A deficient bin is merged with a neighbour by deleting the
    interior edge toward the smaller neighbour (the deepest bin merges into its
    shallower neighbour; the shallowest into its deeper neighbour), repeating
    until no bin is deficient or one bin remains.

    Returns ``(edges, realized_G, expected_counts)``; ``edges`` are the interior
    cut points to pass to :func:`cafa.metrics.reference_buckets` via ``edges=``.
    """
    d = np.asarray(probe_depths, dtype=float)
    E = list(quantile_depth_edges(d, n_buckets).tolist())
    n_cal_expected = float(n_cal_expected)
    while True:
        b = np.digitize(d, np.asarray(E, dtype=float)) if E else np.zeros(d.shape[0], dtype=int)
        counts = np.bincount(b, minlength=len(E) + 1).astype(float)
        expected = counts / max(d.shape[0], 1) * n_cal_expected
        deficient = np.flatnonzero(expected < float(n_min))
        if deficient.size == 0 or len(E) == 0:
            break
        k = int(deficient[np.argmin(expected[deficient])])
        left, right = k - 1, k
        has_left = left >= 0
        has_right = right < len(E)
        if not has_left:
            del E[right]
        elif not has_right:
            del E[left]
        else:
            if counts[k - 1] <= counts[k + 1]:
                del E[left]
            else:
                del E[right]
    edges = np.asarray(E, dtype=float)
    b = np.digitize(d, edges) if edges.size else np.zeros(d.shape[0], dtype=int)
    counts = np.bincount(b, minlength=edges.size + 1).astype(float)
    expected = counts / max(d.shape[0], 1) * n_cal_expected
    return edges, int(edges.size + 1), expected


def escalation_fractions(
    min_expected_stratum_count: float,
    alpha: float,
    level: float,
    n_levels: int = 41,
    margin: float = 0.05,
    a_floor: float = 0.10,
) -> np.ndarray:
    """Target answered fractions ``a_min, ..., 1.0`` for the tier-3 grid.

    The most conservative level must still be certifiable: its expected
    answered count in the SMALLEST stratum, ``a_min * min_k E[n_k]``, is set to
    at least ``n_min(alpha, level, margin)`` (the Hoeffding sample size for a
    rule with selective risk ``alpha - margin``).  ``a_min`` is floored at
    ``a_floor`` and capped at 1.  Levels are equally spaced on ``[a_min, 1]``.
    """
    n_min = n_min_required(alpha, level, margin)
    a_min = float(n_min) / max(float(min_expected_stratum_count), 1.0)
    a_min = float(min(1.0, max(float(a_floor), a_min)))
    return np.linspace(a_min, 1.0, int(n_levels))


def escalation_levels(
    probe_scores_T: np.ndarray,
    answered_fractions: np.ndarray,
    probe_bucket_id: "np.ndarray | None" = None,
) -> "tuple[np.ndarray, np.ndarray]":
    """Escalation thresholds from target answered fractions (probe quantiles).

    ``answered_fractions`` are the target fractions ``a_j`` in ``(0, 1]``
    (e.g. ``0.02, 0.04, ..., 1.0``).  Level ``a`` answers an input iff
    ``g_T(x) >= mu(a)``.  With ``probe_bucket_id`` given (the committed probe
    strata), ``mu(a) = min_k Quantile_probe,k(g_T; 1 - a)`` over populated
    strata, so that EVERY stratum answers at least about a fraction ``a`` of its
    probe rows; without it the pooled quantile is used.  The stratum-aware form
    is the one to commit: the tier-3 fixed sequence starts at the most
    conservative level, and a level that answers nobody in some represented
    stratum has p = 1 there and would block certification at the first step.

    Returns ``(mu_values_ascending, fractions_matching)``: ``mu`` ascending, so
    the LAST entry is the most conservative level (smallest answered fraction).
    """
    g = np.asarray(probe_scores_T, dtype=float)
    a = np.asarray(answered_fractions, dtype=float)
    if np.any(a <= 0.0) or np.any(a > 1.0):
        raise ValueError("answered fractions must lie in (0, 1].")
    a_sorted = np.sort(a)[::-1]                       # descending fractions
    if probe_bucket_id is None:
        mu = np.quantile(g, 1.0 - a_sorted)
    else:
        b = np.asarray(probe_bucket_id)
        if b.shape[0] != g.shape[0]:
            raise ValueError("probe_bucket_id must align with probe_scores_T.")
        per = [np.quantile(g[b == k], 1.0 - a_sorted) for k in np.unique(b)]
        mu = np.min(np.stack(per, axis=0), axis=0)
    mu = np.maximum.accumulate(mu)                    # enforce monotone (ties)
    return mu.astype(float), a_sorted.astype(float)


def escalation_order_from_probe(
    probe_scores_T: np.ndarray,
    probe_correct_T: np.ndarray,
    mu_values: np.ndarray,
    alpha: float,
    probe_bucket_id: np.ndarray,
) -> np.ndarray:
    """Precommitted tier-3 testing order: levels sorted by their PROBE union p-value.

    For each escalation level the union-null Hoeffding--Bentkus p-value (max over
    probe strata) is computed on the independent probe exactly as tier 3 will
    compute it on calibration data; levels are ordered by increasing probe
    p-value, ties broken toward the smaller ``mu`` (more answered).  Because the
    probe is independent of every calibration draw, this is a legitimate
    precommitted order for the fixed-sequence procedure, and it starts the walk
    where the evidence is expected to be strongest rather than at the smallest
    answered set.  Returns level indices (into the ascending ``mu_values``).
    """
    from .cascade import selective_pvalues  # local import: avoid a cycle at import time

    mu = np.asarray(mu_values, dtype=float)
    p_union, _, _ = selective_pvalues(probe_scores_T, probe_correct_T, mu, alpha, probe_bucket_id)
    J = mu.shape[0]
    # sort by (p ascending, index ascending) -> smaller mu first among ties
    keys = np.lexsort((np.arange(J), p_union))
    return keys.astype(int)
