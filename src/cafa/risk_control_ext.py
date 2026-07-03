"""WO-5 -- CAFA-IUT: a single lambda certified simultaneously against every stratum.

Composes ONLY the frozen primitives in :mod:`cafa.risk_control` (never edits
them, never imports torch).  The frozen :func:`ltt_select` is used purely as a
vectorized Hoeffding-Bentkus p-value engine per stratum; its per-stratum
*selection* output is ignored.

The deployable per-stratum-valid object is a single lambda certified via the
intersection-union test (IUT): the union-null p-value is the per-lambda max of
the frozen per-stratum HB p-values, a fixed-sequence walk over the grid certifies
at level delta, and the cheapest certified lambda is deployed.  If nothing
certifies, the method globally abstains -> full acquisition (the correct outcome
when a stratum is intrinsically alpha-infeasible).

    Guarantee: P(exists k: R(lambda_hat | k) > alpha) <= delta.
    No delta/K, no routing, no circularity -- deployable at exactly the
    reported cost.

DECISION: the union-null validity argument (below) is reproduced in ASCII math
(union/intersect/<=/>=/lambda/alpha/delta/exists/for-all) to honour the hard
ASCII-safe guardrail (spec Sec. C.7) while preserving the argument verbatim in
meaning.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .risk_control import ltt_select

__all__ = ["IUTResult", "iut_select"]


@dataclass
class IUTResult:
    """Result of :func:`iut_select`.

    Attributes
    ----------
    valid_mask : np.ndarray[bool], shape [G]
        Grid thresholds certified simultaneously across every stratum.
    lambda_idx : int or None
        Cheapest certified threshold (== smallest certified index in the scalar
        family; see cost-blindness note in :func:`iut_select`).  None on global
        abstention.
    lambda_value : float or None
        ``grid[lambda_idx]`` (or None).
    p_union : np.ndarray, shape [G]
        Union-null p-value per grid index (max over strata of the per-stratum
        HB p-value).
    per_stratum_pvalues : dict
        Stratum label -> per-threshold HB p-values ``[G]`` (empty strata map to
        an all-ones vector).
    stratum_sizes : dict
        Stratum label -> number of calibration rows (0 for an empty stratum).
    alpha, delta : float
        Target risk level and FWER budget.
    """

    valid_mask: np.ndarray
    lambda_idx: Optional[int]
    lambda_value: Optional[float]
    p_union: np.ndarray
    per_stratum_pvalues: dict
    stratum_sizes: dict
    alpha: float
    delta: float


def iut_select(
    losses: np.ndarray,
    costs: np.ndarray,
    grid: np.ndarray,
    alpha: float,
    delta: float,
    bucket_id: np.ndarray,
    procedure: str = "fixed_sequence",
    min_stratum_warn: int = 30,
) -> IUTResult:
    """Certify one lambda valid against every stratum via the intersection-union test.

    Validity argument (verbatim, ASCII):
    Union-null p-value: for H_lambda = union_k {R(lambda | k) > alpha},
    p_lambda := max_k p_{lambda,k} is super-uniform, because if H_lambda holds
    then some H_{lambda,k*} holds and P(p_lambda <= u) <= P(p_{lambda,k*} <= u)
    <= u (intersection-union test).  FWER over the grid then gives
    P(exists lambda in Lambda_hat, exists k: R(lambda | k) > alpha) <= delta,
    hence P(for all k: R(lambda_hat | k) <= alpha) >= 1 - delta for the deployed
    lambda_hat.  Global abstention (empty Lambda_hat) makes no claim and is the
    correct outcome when some stratum is alpha-infeasible.

    Parameters
    ----------
    losses, costs : np.ndarray, shape ``[n, G]``
        Per-calibration-row, per-threshold losses in [0, 1] and non-negative
        costs (the same matrices :func:`ltt_select` consumes).
    grid : np.ndarray, shape ``[G]``
        Ascending threshold grid.
    alpha, delta : float
        Target risk level and FWER budget.
    bucket_id : np.ndarray, shape ``[n]``
        Integer stratum label per calibration row.
    procedure : str, default "fixed_sequence"
        Forwarded to :func:`ltt_select` for the per-stratum p-value computation
        (the p-values themselves are procedure-independent) and used for the
        union-level FWER walk over the grid.
    min_stratum_warn : int, default 30
        Emit ``warnings.warn`` for any populated stratum with fewer than this
        many calibration rows.

    Notes
    -----
    Strata are taken over the contiguous integer label span ``[min, max]`` of
    ``bucket_id``.  A label in that span with **zero** calibration rows (an
    interior gap) contributes ``p == 1.0`` at every grid index, which blocks
    certification -- conservative by design (we cannot certify a stratum we did
    not observe).

    Cost-blindness: ``lambda_idx`` is ``argmin`` of the full-column cost means
    over the certified set.  In the scalar (lambda-only) family cost is monotone
    in the grid index, so the cheapest certified index equals the smallest
    certified index (the bottom of the fixed-sequence block) -- the cost
    minimisation is effectively cost-blind here, stated rather than hidden.
    """
    losses = np.asarray(losses, dtype=float)
    costs = np.asarray(costs, dtype=float)
    grid = np.asarray(grid, dtype=float)
    bucket_id = np.asarray(bucket_id)
    if losses.ndim != 2:
        raise ValueError(f"losses must be 2-D [n, G]; got shape {losses.shape}.")
    n, G = losses.shape
    if bucket_id.shape[0] != n:
        raise ValueError("bucket_id length must match the number of rows in losses.")

    labels = np.unique(bucket_id)
    lo, hi = int(labels.min()), int(labels.max())
    ones = np.ones(G, dtype=float)

    per_stratum_pvalues: dict = {}
    stratum_sizes: dict = {}
    p_union = np.zeros(G, dtype=float)
    for k in range(lo, hi + 1):
        mask = bucket_id == k
        n_k = int(mask.sum())
        stratum_sizes[int(k)] = n_k
        if n_k == 0:
            # Interior empty stratum: p == 1 everywhere -> blocks certification.
            per_stratum_pvalues[int(k)] = ones.copy()
            p_union = np.maximum(p_union, ones)
            continue
        if n_k < int(min_stratum_warn):
            warnings.warn(
                f"stratum {int(k)} has only n_k={n_k} calibration rows "
                f"(< min_stratum_warn={int(min_stratum_warn)}); IUT p-values are "
                "loose here.",
                stacklevel=2,
            )
        pv = ltt_select(
            losses[mask], costs[mask], grid, alpha, delta, procedure=procedure
        ).pvalues
        per_stratum_pvalues[int(k)] = np.asarray(pv, dtype=float)
        p_union = np.maximum(p_union, per_stratum_pvalues[int(k)])

    # Union-level FWER walk over the grid (mirrors the frozen selector).
    valid_mask = np.zeros(G, dtype=bool)
    if procedure == "fixed_sequence":
        for j in range(G - 1, -1, -1):
            if p_union[j] <= float(delta):
                valid_mask[j] = True
            else:
                break
    elif procedure == "bonferroni":
        valid_mask = p_union <= (float(delta) / G)
    else:
        raise ValueError(
            f"unknown procedure {procedure!r}; expected 'fixed_sequence' or 'bonferroni'."
        )

    valid_idx = np.flatnonzero(valid_mask)
    if valid_idx.size == 0:
        lambda_idx: Optional[int] = None
        lambda_value: Optional[float] = None
    else:
        c_hat = costs.mean(axis=0)                       # full-column cost means
        lambda_idx = int(valid_idx[np.argmin(c_hat[valid_idx])])
        lambda_value = float(grid[lambda_idx])

    return IUTResult(
        valid_mask=valid_mask,
        lambda_idx=lambda_idx,
        lambda_value=lambda_value,
        p_union=p_union,
        per_stratum_pvalues=per_stratum_pvalues,
        stratum_sizes=stratum_sizes,
        alpha=float(alpha),
        delta=float(delta),
    )
