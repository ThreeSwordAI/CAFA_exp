"""Small, pure metric helpers (numpy only)."""

from __future__ import annotations

import numpy as np

__all__ = [
    "empirical_risk",
    "expected_cost",
    "violation_rate",
    "none_rate",
    "cost_at_selected",
    "risk_at_selected",
    "pareto_point",
]


def empirical_risk(losses: np.ndarray) -> np.ndarray:
    """Per-threshold empirical risk: column means of ``losses`` -> shape [G]."""
    return np.asarray(losses, dtype=float).mean(axis=0)


def expected_cost(costs: np.ndarray) -> np.ndarray:
    """Per-threshold expected cost: column means of ``costs`` -> shape [G]."""
    return np.asarray(costs, dtype=float).mean(axis=0)


def violation_rate(true_risk_at_selected_array: np.ndarray, alpha: float) -> float:
    """Fraction of trials whose selected threshold's *true* risk exceeds alpha.

    ``true_risk_at_selected_array`` holds, per trial, the true risk at the
    selected threshold (use a non-violating sentinel such as 0.0 for trials
    that selected nothing).  Returns 0.0 for an empty array.
    """
    arr = np.asarray(true_risk_at_selected_array, dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.mean(arr > float(alpha)))


def none_rate(selected_indices) -> float:
    """Fraction of trials that certified no threshold (``lambda_idx is None``)."""
    selected_indices = list(selected_indices)
    if len(selected_indices) == 0:
        return 0.0
    return float(np.mean([idx is None for idx in selected_indices]))

def cost_at_selected(costs: np.ndarray, lambda_idx) -> float:
    """Mean acquisition cost at the selected threshold column.

    ``costs`` is ``[n, G]`` (e.g. the TEST cost matrix from
    :func:`cafa.acquisition.stops_from_grid`).  Returns ``float('nan')`` when
    ``lambda_idx is None`` (no certified threshold this draw).
    """
    if lambda_idx is None:
        return float("nan")
    costs = np.asarray(costs, dtype=float)
    return float(costs[:, int(lambda_idx)].mean())


def risk_at_selected(losses: np.ndarray, lambda_idx) -> float:
    """Mean loss (realized risk) at the selected threshold column.

    ``losses`` is ``[n, G]``.  Returns ``float('nan')`` when ``lambda_idx is
    None``.
    """
    if lambda_idx is None:
        return float("nan")
    losses = np.asarray(losses, dtype=float)
    return float(losses[:, int(lambda_idx)].mean())


def pareto_point(losses: np.ndarray, costs: np.ndarray, lambda_idx):
    """The ``(expected_cost, empirical_risk)`` operating point at ``lambda_idx``.

    A single point on the cost--risk plane for the selected threshold, handy for
    plotting CAFA against baselines.  Returns ``(nan, nan)`` if nothing was
    selected.
    """
    return cost_at_selected(costs, lambda_idx), risk_at_selected(losses, lambda_idx)

# ---------------------------------------------------------------------------
# Step 3 (Mondrian) additions -- numpy only, no torch.
#
# These helpers support per-bucket ("Mondrian") risk control.  They are pure
# numpy mirrors of the trajectory -> (losses, costs, stop_depth) mapping in
# ``cafa.acquisition.stops_from_grid`` (kept torch-free so the calibration and
# evaluation paths never import torch), plus reference-depth bucketing and
# per-bucket risk/cost readouts.
# ---------------------------------------------------------------------------

__all__ += [
    "stops_from_grid_np",
    "reference_depth",
    "reference_buckets",
    "quantile_bucket_edges",
    "per_bucket_risk",
    "per_bucket_cost",
]


def stops_from_grid_np(
    scores: np.ndarray,
    correct: np.ndarray,
    cum_cost: np.ndarray,
    grid: np.ndarray,
) -> "tuple[np.ndarray, np.ndarray, np.ndarray]":
    """Numpy mirror of :func:`cafa.acquisition.stops_from_grid`.

    Operates directly on the trajectory arrays (each ``[n, T+1]``) instead of a
    ``Trajectories`` object, so the calibration/evaluation code can map a score
    grid to ``(losses, costs, stop_depth)`` without importing torch.  Semantics
    are identical to the acquisition version: ``grid`` ascending and, for each
    instance ``i`` and threshold ``grid[j]``::

        s = first t in 0..T with scores[i, t] >= grid[j] ; if none, s = T
        losses[i, j]     = 1.0 - correct[i, s]
        costs[i, j]      = cum_cost[i, s]
        stop_depth[i, j] = s

    Passing ``true_acc`` in place of ``correct`` yields the *true*-risk matrix
    ``1 - true_acc[i, s]`` -- used by the synthetic gate.
    """
    scores = np.asarray(scores, dtype=float)
    correct = np.asarray(correct, dtype=float)
    cum_cost = np.asarray(cum_cost, dtype=float)
    grid = np.asarray(grid, dtype=float)
    if np.any(np.diff(grid) < 0):
        raise ValueError("grid must be in ascending order.")

    n, Tp1 = scores.shape
    T = Tp1 - 1

    crossed = scores[:, :, None] >= grid[None, None, :]   # [n, T+1, G]
    any_cross = crossed.any(axis=1)                       # [n, G]
    first = crossed.argmax(axis=1)                        # [n, G] (0 if none)
    s = np.where(any_cross, first, T).astype(int)         # [n, G]

    rows = np.arange(n)[:, None]
    correct_at_s = correct[rows, s]
    losses = 1.0 - correct_at_s
    costs = cum_cost[rows, s]
    stop_depth = s.astype(float)
    return losses, costs, stop_depth


def reference_depth(scores: np.ndarray, lambda_ref: float) -> np.ndarray:
    """First-crossing depth of ``lambda_ref`` per instance -> shape ``[n]``.

    ``d_i = min{ t in 0..T : scores[i, t] >= lambda_ref }`` and ``d_i = T`` if
    the score never reaches ``lambda_ref``.  This is the depth a *reference*
    policy thresholded at ``lambda_ref`` would stop at; buckets are defined on
    it so the partition is a property of the population, not of any particular
    calibration draw.
    """
    scores = np.asarray(scores, dtype=float)
    n, Tp1 = scores.shape
    T = Tp1 - 1
    crossed = scores >= float(lambda_ref)                 # [n, T+1]
    any_cross = crossed.any(axis=1)
    first = crossed.argmax(axis=1)
    return np.where(any_cross, first, T).astype(int)


def quantile_bucket_edges(
    scores: np.ndarray, lambda_ref: float, n_buckets: int
) -> np.ndarray:
    """Equal-mass (quantile) interior depth edges estimated on a pool.

    Returns the ``n_buckets - 1`` interior cut points of the reference-depth
    distribution so each bucket holds ~``1/n_buckets`` of the pool.  Duplicate
    edges (reference depths are integer valued and can tie heavily) are
    collapsed, so the realized bucket count may be smaller than ``n_buckets``.

    Estimate these on the train/rollout pool and pass them to
    :func:`reference_buckets` via ``edges=`` for *both* calibration and test --
    never re-estimate boundaries on the calibration set used for selection.
    """
    d = reference_depth(scores, lambda_ref)
    qs = np.linspace(0.0, 1.0, int(n_buckets) + 1)[1:-1]
    edges = np.quantile(d.astype(float), qs)
    return np.unique(edges)


def reference_buckets(
    scores: np.ndarray,
    lambda_ref: float,
    n_buckets: int,
    min_per_bucket: int,
    edges: "np.ndarray | None" = None,
) -> "tuple[np.ndarray, np.ndarray]":
    """Assign instances to depth buckets from their reference depth.

    Buckets are contiguous reference-depth intervals, so a bucketing is fully
    described by its ascending *interior* edges.  With ``edges=None`` the edges
    start equal-width on ``[0, T]`` (``n_buckets`` of them) and any bucket below
    ``min_per_bucket`` is merged into a neighbour by deleting the interior edge
    toward the smaller-count side -- repeated until every surviving bucket meets
    the floor (or a single bucket remains).  With ``edges`` supplied the merge
    step is skipped and those exact boundaries are applied (the intended way to
    reuse a calibration/pool partition on the test split).

    Returns ``(bucket_id[n], edges)``.  ``bucket_id`` holds ``np.digitize``
    labels, i.e. ascending in reference depth, so the *cheapest* (fastest-rising)
    populated bucket is ``min(np.unique(bucket_id))`` -- with the equal-width
    default that is ``0``; with supplied quantile edges on heavily tied integer
    depths a boundary bucket can be empty, so the cheapest populated label may be
    ``> 0`` (downstream code only ever iterates populated labels).  Because the
    labels are a pure function of ``edges``, passing the same ``edges`` back in
    reproduces the partition exactly on another split.  ``edges`` are the interior
    boundaries actually applied.
    """
    d = reference_depth(scores, lambda_ref)

    if edges is None:
        n, Tp1 = scores.shape
        T = Tp1 - 1
        E = list(np.linspace(0.0, T, int(n_buckets) + 1)[1:-1])
        while len(E) > 0:
            b = np.digitize(d, E)
            counts = np.bincount(b, minlength=len(E) + 1)
            small = np.where(counts < int(min_per_bucket))[0]
            if small.size == 0:
                break
            k = int(small[np.argmin(counts[small])])
            left = k - 1            # index in E of the edge on bucket k's left
            right = k               # index in E of the edge on bucket k's right
            has_left = left >= 0
            has_right = right < len(E)
            if not has_left:
                del E[right]
            elif not has_right:
                del E[left]
            else:
                cl = counts[k - 1]
                cr = counts[k + 1]
                if cl <= cr:
                    del E[left]
                else:
                    del E[right]
        edges_used = np.asarray(E, dtype=float)
    else:
        edges_used = np.asarray(edges, dtype=float)

    bucket_id = np.digitize(d, edges_used).astype(int)
    return bucket_id, edges_used


def per_bucket_risk(
    loss_matrix: np.ndarray, bucket_id: np.ndarray, lambda_by_bucket: dict
) -> dict:
    """Realized mean risk within each bucket at its selected threshold.

    ``loss_matrix`` is ``[n, G]`` (pass the true-risk matrix from
    :func:`stops_from_grid_np` with ``true_acc`` to get *true* per-bucket risk).
    ``lambda_by_bucket`` maps bucket label -> grid index (or ``None``).  A bucket
    that selected nothing -- or is empty -- maps to ``float('nan')``; since
    ``nan > alpha`` is ``False`` this counts as non-violating, matching the
    abstain == fall-back-to-full-acquisition convention.
    """
    loss_matrix = np.asarray(loss_matrix, dtype=float)
    bucket_id = np.asarray(bucket_id)
    out: dict = {}
    for k in np.unique(bucket_id):
        mask = bucket_id == k
        idx = lambda_by_bucket.get(int(k), None)
        if idx is None or not mask.any():
            out[int(k)] = float("nan")
        else:
            out[int(k)] = float(loss_matrix[mask, int(idx)].mean())
    return out


def per_bucket_cost(
    cost_matrix: np.ndarray, bucket_id: np.ndarray, lambda_by_bucket: dict
) -> dict:
    """Realized mean acquisition cost within each bucket at its threshold.

    Same contract as :func:`per_bucket_risk` but over the cost matrix; empty or
    abstaining buckets map to ``float('nan')``.
    """
    cost_matrix = np.asarray(cost_matrix, dtype=float)
    bucket_id = np.asarray(bucket_id)
    out: dict = {}
    for k in np.unique(bucket_id):
        mask = bucket_id == k
        idx = lambda_by_bucket.get(int(k), None)
        if idx is None or not mask.any():
            out[int(k)] = float("nan")
        else:
            out[int(k)] = float(cost_matrix[mask, int(idx)].mean())
    return out

# ---------------------------------------------------------------------------
# Step 4 (H2 efficiency) additions -- numpy only, no torch.
#
# Helpers for the matched-risk cost comparison (does CAFA's certified stopping
# beat the alpha-respecting heuristics at equal or better risk?) and Pareto
# points on the realized (risk, cost) plane.  Existing helpers are untouched.
# ---------------------------------------------------------------------------
__all__ += [
    "realized_risk_cost",
    "validity_fraction",
    "matched_risk_cost_gap",
    "pareto_front",
]


def realized_risk_cost(losses: np.ndarray, costs: np.ndarray, lambda_idx) -> "tuple":
    """Realized ``(risk, cost)`` at a selected grid index (``(nan, nan)`` if None).

    Thin wrapper over :func:`risk_at_selected` / :func:`cost_at_selected` giving
    a method's operating point on the test ``losses``/``costs`` matrices -- the
    unit the H2 table and figure consume.
    """
    return risk_at_selected(losses, lambda_idx), cost_at_selected(costs, lambda_idx)


def validity_fraction(realized_risks, alpha: float) -> float:
    """Fraction of seeds whose realized risk **exceeds** ``alpha`` (the H2 axis).

    A method is "valid" when this is ``<= delta``.  ``nan`` entries (a seed that
    certified nothing) are ignored, matching the abstain convention; an all-nan
    or empty input returns ``0.0``.
    """
    arr = np.asarray(list(realized_risks), dtype=float)
    arr = arr[~np.isnan(arr)]
    if arr.size == 0:
        return 0.0
    return float(np.mean(arr > float(alpha)))


def matched_risk_cost_gap(
    cafa_cost: float, heuristic_cost: float
) -> float:
    """Cost the heuristic pays *above* CAFA at matched (alpha-respecting) risk.

    Positive means CAFA is cheaper.  ``nan`` propagates (either side abstained).
    Used to summarise "CAFA-marginal costs less than the alpha-respecting
    heuristics while carrying the guarantee".
    """
    return float(heuristic_cost) - float(cafa_cost)


def pareto_front(points) -> list:
    """Non-dominated ``(risk, cost)`` points (both minimised) for the H2 plot.

    ``points`` is an iterable of ``(risk, cost)`` tuples; entries with any ``nan``
    are dropped.  Returns the subset not dominated by another point (a point is
    dominated if another has ``risk <=`` and ``cost <=`` with at least one
    strict), sorted by risk.
    """
    pts = [
        (float(r), float(c))
        for (r, c) in points
        if not (np.isnan(r) or np.isnan(c))
    ]
    front = []
    for i, (ri, ci) in enumerate(pts):
        dominated = False
        for j, (rj, cj) in enumerate(pts):
            if j == i:
                continue
            if rj <= ri and cj <= ci and (rj < ri or cj < ci):
                dominated = True
                break
        if not dominated:
            front.append((ri, ci))
    return sorted(set(front))