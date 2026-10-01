"""v3 -- Certify-or-route deployment cascade (torch-free).

CAFA-IUT answers one question: is there a single confidence threshold whose
stratum risk is certified ``<= alpha`` on every represented calibration
stratum?  When the answer is "no", the AAAI version fell back to an
*uncertified* full-acquisition prediction.  The cascade below replaces that
fallback with two further certified tiers, so that every deployed rule carries
a stratum-wise finite-sample certificate:

    tier 1  certified stop        -- CAFA-IUT over the threshold grid
                                     (:func:`cafa.risk_control_ext.iut_select`);
    tier 2  certified budget      -- fixed-sequence IUT over forced depths
                                     ``t = T, T-1, ..., 0`` (the forced-depth
                                     subfamily already present in the audit);
    tier 3  certified escalation  -- full acquisition, predict iff the readiness
                                     score at depth ``T`` is at least ``mu``,
                                     otherwise escalate (abstain / human review);
                                     fixed-sequence IUT over precommitted
                                     escalation levels, most escalation first.

The tiers are evaluated on the same calibration sample at levels
``delta_1 + delta_2 + delta_3 = delta`` and the FIRST certified tier is
deployed.  Theorem 4 (end-to-end stratum-wise validity): under the Theorem-2
assumptions and with the depth-``T`` readiness score fixed independently of the
calibration sample,

    P( deployed rule has R_k > alpha for some k in K_cal ) <= delta,

where ``R_k`` is the selective risk for tier 3.  Proof: the unsafe-deployment
event is contained in the union over tiers of "tier j certifies a rule that is
unsafe on some k"; each tier is a fixed-sequence procedure whose component
Hoeffding--Bentkus p-values are valid conditionally on label-free covariate
information (stratum labels; for tier 3 also the answered indicators
``1{g_T(x) >= mu}``, which are functions of ``x`` only), so each term is at most
``delta_j``; union bound.  No claim is made when every tier refuses.

Everything here composes the frozen primitives only (``hoeffding_bentkus_pvalue``,
``iut_select``, ``stops_from_grid_np``); nothing in :mod:`cafa.risk_control` is
touched.  ASCII-safe, numpy-only, deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .metrics import stops_from_grid_np
from .risk_control import hoeffding_bentkus_pvalue
from .risk_control_ext import iut_select

__all__ = [
    "TierResult",
    "CascadeResult",
    "allocate_delta",
    "depth_family_matrices",
    "tier_threshold",
    "tier_budget",
    "selective_pvalues",
    "tier_escalation",
    "certify_or_route",
    "apply_rule",
    "calibration_span",
]

TIER_NAMES = ("threshold", "budget", "escalation")


# --------------------------------------------------------------------------- #
# Result containers
# --------------------------------------------------------------------------- #
@dataclass
class TierResult:
    """Outcome of one cascade tier.

    Attributes
    ----------
    name : str
        ``"threshold"`` / ``"budget"`` / ``"escalation"``.
    level : float
        The per-tier FWER level ``delta_j`` used.
    param_idx, param_value : int / float or None
        Deployed parameter (grid index and value) if the tier certified,
        else ``None``.  For tier 2 the value is the forced depth ``t``; for tier
        3 the escalation threshold ``mu``.
    valid_mask : np.ndarray[bool]
        Which parameters were certified (contiguous block from the top of the
        fixed sequence).
    p_union : np.ndarray
        Union-null (max over strata) p-value per parameter.
    stratum_sizes : dict
        Stratum label -> number of calibration rows used by the tier (answered
        rows at the deployed level for tier 3; see ``extra``).
    extra : dict
        Tier-specific bookkeeping (e.g. per-level answered counts).
    """

    name: str
    level: float
    param_idx: Optional[int]
    param_value: Optional[float]
    valid_mask: np.ndarray
    p_union: np.ndarray
    stratum_sizes: dict
    extra: dict = field(default_factory=dict)

    @property
    def certified(self) -> bool:
        return self.param_idx is not None


@dataclass
class CascadeResult:
    """Outcome of :func:`certify_or_route`.

    ``tier`` is 1, 2 or 3 for the deployed tier and 0 when every tier refused
    (``rule == "none"``: full escalation, no certificate).  ``tiers`` holds the
    :class:`TierResult` of every evaluated tier (later tiers are still run for
    reporting even when an earlier tier certified; deployment uses the first
    certified tier).
    """

    tier: int
    rule: str
    param_idx: Optional[int]
    param_value: Optional[float]
    tiers: dict
    delta_alloc: tuple
    k_cal: list
    alpha: float
    delta: float

    @property
    def certified(self) -> bool:
        return self.tier > 0


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def allocate_delta(delta: float, weights=(0.5, 0.25, 0.25)) -> "tuple[float, float, float]":
    """Split the overall error budget ``delta`` across the three tiers.

    ``weights`` must be positive and sum to one (default ``delta/2, delta/4,
    delta/4``).  Union bound over tiers gives overall level ``delta``.
    """
    w = np.asarray(weights, dtype=float)
    if w.shape != (3,) or np.any(w <= 0) or abs(float(w.sum()) - 1.0) > 1e-9:
        raise ValueError("weights must be three positive numbers summing to one.")
    d = float(delta)
    return (d * float(w[0]), d * float(w[1]), d * float(w[2]))


def calibration_span(bucket_id: np.ndarray) -> list:
    """Contiguous integer label span ``K_cal = [min, ..., max]`` of ``bucket_id``."""
    b = np.asarray(bucket_id)
    lo, hi = int(b.min()), int(b.max())
    return list(range(lo, hi + 1))


def depth_family_matrices(correct: np.ndarray, cum_cost: np.ndarray):
    """Loss / cost matrices of the forced-depth family, shape ``[n, T+1]``.

    Column ``t`` is the rule "acquire exactly ``t`` units along the frozen
    trajectory, then predict": ``loss = 1 - correct[:, t]``,
    ``cost = cum_cost[:, t]``.
    """
    correct = np.asarray(correct, dtype=float)
    cum_cost = np.asarray(cum_cost, dtype=float)
    if correct.shape != cum_cost.shape:
        raise ValueError("correct and cum_cost must have the same [n, T+1] shape.")
    return 1.0 - correct, cum_cost


def _fixed_sequence_mask(p_union: np.ndarray, level: float,
                         order: "np.ndarray | None" = None) -> np.ndarray:
    """Fixed-sequence certification: walk ``order`` (default: top index down),
    certify while ``p <= level``, stop at the first failure."""
    G = int(p_union.shape[0])
    valid = np.zeros(G, dtype=bool)
    walk = range(G - 1, -1, -1) if order is None else [int(j) for j in np.asarray(order)]
    for j in walk:
        if p_union[j] <= float(level):
            valid[j] = True
        else:
            break
    return valid


# --------------------------------------------------------------------------- #
# Tier 1 -- certified stop (CAFA-IUT)
# --------------------------------------------------------------------------- #
def tier_threshold(
    losses: np.ndarray,
    costs: np.ndarray,
    grid: np.ndarray,
    alpha: float,
    level: float,
    bucket_id: np.ndarray,
) -> TierResult:
    """CAFA-IUT over the ascending threshold ``grid`` at level ``delta_1``."""
    res = iut_select(losses, costs, grid, alpha, level, bucket_id)
    return TierResult(
        name="threshold",
        level=float(level),
        param_idx=res.lambda_idx,
        param_value=res.lambda_value,
        valid_mask=np.asarray(res.valid_mask, dtype=bool),
        p_union=np.asarray(res.p_union, dtype=float),
        stratum_sizes=dict(res.stratum_sizes),
    )


# --------------------------------------------------------------------------- #
# Tier 2 -- certified budget (forced depth)
# --------------------------------------------------------------------------- #
def tier_budget(
    correct: np.ndarray,
    cum_cost: np.ndarray,
    alpha: float,
    level: float,
    bucket_id: np.ndarray,
) -> TierResult:
    """Fixed-sequence IUT over forced depths ``t = T, ..., 0`` at level ``delta_2``.

    Implemented by handing the ``[n, T+1]`` depth-family matrices to the frozen
    :func:`iut_select` with the ascending "grid" ``0, 1, ..., T``: its fixed
    sequence walks from the last index (``t = T``, full information) downward,
    which is exactly the precommitted order, and its cheapest-certified rule is
    the smallest certified depth because cumulative cost is nondecreasing in
    ``t``.  Validity does not require risk to be monotone in ``t``.
    """
    losses_d, costs_d = depth_family_matrices(correct, cum_cost)
    T = losses_d.shape[1] - 1
    depth_grid = np.arange(T + 1, dtype=float)
    res = iut_select(losses_d, costs_d, depth_grid, alpha, level, bucket_id)
    return TierResult(
        name="budget",
        level=float(level),
        param_idx=res.lambda_idx,
        param_value=(None if res.lambda_idx is None else float(res.lambda_idx)),
        valid_mask=np.asarray(res.valid_mask, dtype=bool),
        p_union=np.asarray(res.p_union, dtype=float),
        stratum_sizes=dict(res.stratum_sizes),
    )


# --------------------------------------------------------------------------- #
# Tier 3 -- certified escalation (selective full acquisition)
# --------------------------------------------------------------------------- #
def selective_pvalues(
    scores_T: np.ndarray,
    correct_T: np.ndarray,
    mu_values: np.ndarray,
    alpha: float,
    bucket_id: np.ndarray,
) -> "tuple[np.ndarray, dict, dict]":
    """Per-stratum Hoeffding--Bentkus p-values of the selective rules.

    For escalation level ``mu`` and stratum ``k``, the answered calibration rows
    are ``{i : s(x_i) = k, g_T(x_i) >= mu}``; their errors are Bernoulli with
    mean equal to the selective stratum risk ``R_k^sel(mu)`` conditionally on
    the (label-free) answered indicators, so the frozen HB p-value applies with
    ``n = n_{k,mu}``.  An empty answered set gives ``p = 1`` (conservative: a
    rule that answers nobody in a represented stratum cannot be certified from
    data).  Returns ``(p_union[J], p_by_stratum{k: [J]}, n_by_stratum{k: [J]})``.
    """
    s = np.asarray(scores_T, dtype=float)
    c = np.asarray(correct_T, dtype=float)
    mu = np.asarray(mu_values, dtype=float)
    b = np.asarray(bucket_id)
    if s.shape != c.shape or s.ndim != 1:
        raise ValueError("scores_T and correct_T must be 1-D arrays of equal length.")
    if np.any(np.diff(mu) < 0):
        raise ValueError("mu_values must be ascending.")
    J = mu.shape[0]
    ones = np.ones(J, dtype=float)
    p_union = np.zeros(J, dtype=float)
    p_by: dict = {}
    n_by: dict = {}
    for k in calibration_span(b):
        mask = b == k
        if not mask.any():
            p_by[int(k)] = ones.copy()
            n_by[int(k)] = np.zeros(J, dtype=int)
            p_union = np.maximum(p_union, ones)
            continue
        sk, ck = s[mask], c[mask]
        pk = np.ones(J, dtype=float)
        nk = np.zeros(J, dtype=int)
        for j in range(J):
            ans = sk >= mu[j]
            n_ans = int(ans.sum())
            nk[j] = n_ans
            if n_ans == 0:
                pk[j] = 1.0
                continue
            r_hat = float(1.0 - ck[ans].mean())
            pk[j] = hoeffding_bentkus_pvalue(r_hat, n_ans, alpha)
        p_by[int(k)] = pk
        n_by[int(k)] = nk
        p_union = np.maximum(p_union, pk)
    return p_union, p_by, n_by


def tier_escalation(
    scores_T: np.ndarray,
    correct_T: np.ndarray,
    mu_values: np.ndarray,
    alpha: float,
    level: float,
    bucket_id: np.ndarray,
    order: "np.ndarray | None" = None,
) -> TierResult:
    """Fixed-sequence IUT over precommitted escalation levels at level ``delta_3``.

    ``mu_values`` is the ASCENDING precommitted grid of readiness thresholds at
    depth ``T`` (committed as stratum-aware probe quantiles indexed by target
    answered fractions; see :func:`cafa.commit_rules.escalation_levels`).

    ``order`` is the precommitted testing order over level indices.  Default:
    largest ``mu`` first (most escalation, safest).  The recommended choice is
    :func:`cafa.commit_rules.escalation_order_from_probe`: levels sorted by
    their union p-value on the independent probe, so the walk starts where the
    probe evidence is strongest instead of at a tiny answered set.  Any order
    fixed independently of the calibration sample keeps the FWER guarantee.

    The deployed level is the certified level with the smallest ``mu``
    (largest answered fraction, i.e. the cheapest certified escalation rule).
    """
    mu = np.asarray(mu_values, dtype=float)
    p_union, p_by, n_by = selective_pvalues(scores_T, correct_T, mu, alpha, bucket_id)
    valid = _fixed_sequence_mask(p_union, level, order)
    idx = np.flatnonzero(valid)
    if idx.size == 0:
        param_idx: Optional[int] = None
        param_value: Optional[float] = None
        sizes = {k: int(v[-1]) for k, v in n_by.items()}
    else:
        param_idx = int(idx.min())           # smallest certified mu = most answered
        param_value = float(mu[param_idx])
        sizes = {k: int(v[param_idx]) for k, v in n_by.items()}
    return TierResult(
        name="escalation",
        level=float(level),
        param_idx=param_idx,
        param_value=param_value,
        valid_mask=valid,
        p_union=p_union,
        stratum_sizes=sizes,
        extra={"answered_by_stratum": {k: v.tolist() for k, v in n_by.items()},
               "order": (None if order is None else [int(j) for j in np.asarray(order)])},
    )


# --------------------------------------------------------------------------- #
# The cascade
# --------------------------------------------------------------------------- #
def certify_or_route(
    scores: np.ndarray,
    correct: np.ndarray,
    cum_cost: np.ndarray,
    grid: np.ndarray,
    mu_values: np.ndarray,
    alpha: float,
    delta: float,
    bucket_id: np.ndarray,
    delta_weights=(0.5, 0.25, 0.25),
    run_all_tiers: bool = True,
    escalation_order: "np.ndarray | None" = None,
) -> CascadeResult:
    """Run the certify-or-route cascade on one calibration sample.

    Parameters
    ----------
    scores, correct, cum_cost : np.ndarray, shape ``[n, T+1]``
        Calibration trajectories (pool-cache arrays; ``cum_cost`` from
        :func:`cafa.pool.cum_cost_from_order` for the chosen cost scheme).
    grid : np.ndarray, shape ``[G]``
        Ascending threshold grid (tier 1).
    mu_values : np.ndarray, shape ``[J]``
        Ascending precommitted escalation levels (tier 3).
    alpha, delta : float
        Target risk and overall error budget.
    bucket_id : np.ndarray, shape ``[n]``
        Label-free stratum per calibration row (from the committed edges).
    delta_weights : tuple
        Allocation of ``delta`` over the tiers (default ``1/2, 1/4, 1/4``).
    run_all_tiers : bool
        If True every tier is evaluated for reporting; deployment always uses
        the first certified tier in order 1, 2, 3.
    escalation_order : np.ndarray or None
        Precommitted tier-3 testing order over level indices (see
        :func:`tier_escalation`); default most-conservative-first.
    """
    scores = np.asarray(scores, dtype=float)
    correct = np.asarray(correct, dtype=float)
    cum_cost = np.asarray(cum_cost, dtype=float)
    grid = np.asarray(grid, dtype=float)
    bucket_id = np.asarray(bucket_id)
    if scores.shape != correct.shape or scores.shape != cum_cost.shape:
        raise ValueError("scores, correct, cum_cost must share the shape [n, T+1].")
    n, Tp1 = scores.shape
    T = Tp1 - 1
    if bucket_id.shape[0] != n:
        raise ValueError("bucket_id length must equal the number of calibration rows.")

    d1, d2, d3 = allocate_delta(delta, delta_weights)
    k_cal = calibration_span(bucket_id)

    losses, costs, _ = stops_from_grid_np(scores, correct, cum_cost, grid)
    t1 = tier_threshold(losses, costs, grid, alpha, d1, bucket_id)
    tiers = {"threshold": t1}

    deployed = None
    if t1.certified:
        deployed = (1, "threshold", t1.param_idx, t1.param_value)
    if deployed is None or run_all_tiers:
        t2 = tier_budget(correct, cum_cost, alpha, d2, bucket_id)
        tiers["budget"] = t2
        if deployed is None and t2.certified:
            deployed = (2, "budget", t2.param_idx, t2.param_value)
    if deployed is None or run_all_tiers:
        t3 = tier_escalation(scores[:, T], correct[:, T], mu_values, alpha, d3, bucket_id,
                             order=escalation_order)
        tiers["escalation"] = t3
        if deployed is None and t3.certified:
            deployed = (3, "escalation", t3.param_idx, t3.param_value)
    if deployed is None:
        deployed = (0, "none", None, None)

    tier, rule, pidx, pval = deployed
    return CascadeResult(
        tier=tier, rule=rule, param_idx=pidx, param_value=pval, tiers=tiers,
        delta_alloc=(d1, d2, d3), k_cal=k_cal, alpha=float(alpha), delta=float(delta),
    )


# --------------------------------------------------------------------------- #
# Applying a deployed rule to fresh rows (test split)
# --------------------------------------------------------------------------- #
def apply_rule(
    result: CascadeResult,
    scores: np.ndarray,
    correct: np.ndarray,
    cum_cost: np.ndarray,
    grid: np.ndarray,
    mu_values: np.ndarray,
    bucket_id: "np.ndarray | None" = None,
) -> dict:
    """Realized per-row outcome of the deployed rule on new rows (e.g. the test split).

    Returns a dict with ``loss`` (``[n]``, ``nan`` for escalated rows), ``cost``
    (``[n]``), ``answered`` (``[n]`` bool), ``risk`` (mean loss over answered
    rows; ``nan`` if none answered), ``answered_fraction``, and -- when
    ``bucket_id`` is given -- ``per_stratum`` with the same quantities per
    stratum label.  For ``rule == "none"`` every row is escalated (no
    certificate; loss undefined).
    """
    scores = np.asarray(scores, dtype=float)
    correct = np.asarray(correct, dtype=float)
    cum_cost = np.asarray(cum_cost, dtype=float)
    n, Tp1 = scores.shape
    T = Tp1 - 1
    answered = np.ones(n, dtype=bool)
    if result.rule == "threshold":
        g = np.asarray(grid, dtype=float)
        lam = g[int(result.param_idx)]
        crossed = scores >= lam
        any_cross = crossed.any(axis=1)
        first = crossed.argmax(axis=1)
        s = np.where(any_cross, first, T).astype(int)
        rows = np.arange(n)
        loss = 1.0 - correct[rows, s]
        cost = cum_cost[rows, s]
    elif result.rule == "budget":
        t = int(result.param_idx)
        loss = 1.0 - correct[:, t]
        cost = cum_cost[:, t]
    elif result.rule == "escalation":
        mu = float(np.asarray(mu_values, dtype=float)[int(result.param_idx)])
        answered = scores[:, T] >= mu
        loss = np.where(answered, 1.0 - correct[:, T], np.nan)
        cost = cum_cost[:, T]
    elif result.rule == "none":
        answered = np.zeros(n, dtype=bool)
        loss = np.full(n, np.nan)
        cost = cum_cost[:, T]
    else:
        raise ValueError(f"unknown rule {result.rule!r}.")

    def _summ(mask):
        a = answered & mask
        risk = float(np.nanmean(loss[a])) if a.any() else float("nan")
        return {
            "n": int(mask.sum()),
            "answered_fraction": float(a.sum() / max(int(mask.sum()), 1)),
            "risk": risk,
            "cost": float(cost[mask].mean()) if mask.any() else float("nan"),
        }

    out = {
        "loss": loss, "cost": cost, "answered": answered,
        "risk": float(np.nanmean(loss[answered])) if answered.any() else float("nan"),
        "answered_fraction": float(answered.mean()),
        "mean_cost": float(cost.mean()),
    }
    if bucket_id is not None:
        b = np.asarray(bucket_id)
        out["per_stratum"] = {int(k): _summ(b == k) for k in np.unique(b)}
    return out
