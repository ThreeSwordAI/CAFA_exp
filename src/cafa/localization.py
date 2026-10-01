"""v3 -- Family-wide feasibility audit with fault localization (torch-free).

The AAAI audit computed, on a precommitted stratum, the exact one-sided
binomial intersection--union p-value over the threshold subfamily (``p_thr``)
and over the forced-depth subfamily (``p_depth``), and reported the combined
``p_fam = max(p_thr, p_depth)`` with a three-way verdict.  v3 keeps every
number and refines the verdict so that a certified failure is LOCALIZED:

    Type II  (information failure)  p_thr <= gamma and p_depth <= gamma
             no confidence threshold AND no acquisition budget along the frozen
             trajectory attains alpha -- full acquisition included; the
             predictor at full information fails on this stratum.
             -> route: certified escalation (tier 3); repair: predictor/policy.
    Type I   (stopping-rule failure) p_thr <= gamma and min_t Rhat_{k,t} <= alpha
             no confidence threshold attains alpha but some budget does: the
             evidence is there and the readiness score cannot find it.
             -> route: certified budget (tier 2); repair: readiness score.
    feasible                         min over the whole family of Rhat <= alpha
             (descriptive, no certificate)
    thr_failure_depth_unresolved     p_thr <= gamma, min_t Rhat > alpha, p_depth > gamma
             (threshold subfamily certified; budget subfamily undecided)
    unresolved                       otherwise

Each certificate is valid at level gamma by the Theorem-3 argument applied to
the relevant subfamily: the max-p over a subfamily is a valid intersection--union
p-value for that subfamily's existential null.  The ordered rule above is
applied top-down; Type II is exactly the AAAI "certified family-wide failure".
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.stats import binom

from .metrics import stops_from_grid_np

__all__ = [
    "binom_upper_p",
    "StratumAudit",
    "classify_verdict",
    "audit_stratum",
    "audit_all_strata",
    "VERDICTS",
]

VERDICTS = ("feasible", "type_I", "type_II", "thr_failure_depth_unresolved", "unresolved")


def binom_upper_p(s, n: int, alpha: float) -> np.ndarray:
    """Exact one-sided binomial upper-tail p-value ``P(Bin(n, alpha) >= s)``.

    Vectorized over ``s``; the p-value for the safe null ``R <= alpha`` against
    ``R > alpha``.  Identical to the AAAI audit helper (``phase53_lib``).
    """
    s = np.asarray(s, dtype=float)
    p = binom.sf(s - 1.0, int(n), float(alpha))
    return np.clip(p, 0.0, 1.0)


@dataclass
class StratumAudit:
    """Audit record of one stratum (all quantities on the audit sample)."""

    k: int
    n_k: int
    alpha: float
    gamma: float
    p_thr: float
    p_depth: float
    p_fam: float
    rmin_thr: float
    rmin_depth: float
    rmin: float
    r_full: float
    argmin_thr: list
    argmin_depth: list
    verdict: str
    risk_curve_thr: np.ndarray = field(repr=False, default=None)
    risk_curve_depth: np.ndarray = field(repr=False, default=None)

    def as_record(self) -> dict:
        """JSON-serialisable summary (curves omitted)."""
        return {
            "k": int(self.k), "n_k": int(self.n_k), "alpha": float(self.alpha),
            "gamma": float(self.gamma), "p_thr": float(self.p_thr),
            "p_depth": float(self.p_depth), "p_fam": float(self.p_fam),
            "rmin_thr": float(self.rmin_thr), "rmin_depth": float(self.rmin_depth),
            "rmin": float(self.rmin), "r_full": float(self.r_full),
            "argmin_thr": [float(v) for v in self.argmin_thr],
            "argmin_depth": [int(v) for v in self.argmin_depth],
            "verdict": str(self.verdict),
        }


def classify_verdict(p_thr: float, p_depth: float, rmin_thr: float,
                     rmin_depth: float, alpha: float, gamma: float) -> str:
    """Ordered verdict rule (see module docstring)."""
    rmin = min(float(rmin_thr), float(rmin_depth))
    if p_thr <= gamma and p_depth <= gamma:
        return "type_II"
    if p_thr <= gamma and rmin_depth <= alpha:
        return "type_I"
    if rmin <= alpha:
        return "feasible"
    if p_thr <= gamma:
        return "thr_failure_depth_unresolved"
    return "unresolved"


def _argmins(values: np.ndarray, tol: float = 1e-12) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    return np.flatnonzero(v <= v.min() + tol)


def audit_stratum(
    losses_thr_k: np.ndarray,
    losses_depth_k: np.ndarray,
    alpha: float,
    gamma: float,
    grid: np.ndarray,
    k: int = -1,
) -> StratumAudit:
    """Audit one stratum from its 0/1 loss matrices.

    ``losses_thr_k`` is ``[n_k, G]`` (threshold family, ascending grid) and
    ``losses_depth_k`` is ``[n_k, T+1]`` (forced depths ``0..T``).
    """
    Lt = np.asarray(losses_thr_k, dtype=float)
    Ld = np.asarray(losses_depth_k, dtype=float)
    if Lt.ndim != 2 or Ld.ndim != 2 or Lt.shape[0] != Ld.shape[0]:
        raise ValueError("loss matrices must be 2-D with the same number of rows.")
    n_k = int(Lt.shape[0])
    if n_k == 0:
        raise ValueError("cannot audit an empty stratum.")
    grid = np.asarray(grid, dtype=float)

    s_thr = Lt.sum(axis=0)
    s_dep = Ld.sum(axis=0)
    p_thr_vec = binom_upper_p(s_thr, n_k, alpha)
    p_dep_vec = binom_upper_p(s_dep, n_k, alpha)
    p_thr = float(p_thr_vec.max())
    p_depth = float(p_dep_vec.max())
    p_fam = max(p_thr, p_depth)

    r_thr = s_thr / n_k
    r_dep = s_dep / n_k
    rmin_thr = float(r_thr.min())
    rmin_depth = float(r_dep.min())
    rmin = min(rmin_thr, rmin_depth)
    verdict = classify_verdict(p_thr, p_depth, rmin_thr, rmin_depth, alpha, gamma)

    return StratumAudit(
        k=int(k), n_k=n_k, alpha=float(alpha), gamma=float(gamma),
        p_thr=p_thr, p_depth=p_depth, p_fam=float(p_fam),
        rmin_thr=rmin_thr, rmin_depth=rmin_depth, rmin=float(rmin),
        r_full=float(r_dep[-1]),
        argmin_thr=[float(grid[j]) for j in _argmins(r_thr)],
        argmin_depth=[int(t) for t in _argmins(r_dep)],
        verdict=verdict,
        risk_curve_thr=r_thr, risk_curve_depth=r_dep,
    )


def audit_all_strata(
    scores: np.ndarray,
    correct: np.ndarray,
    cum_cost: np.ndarray,
    grid: np.ndarray,
    bucket_id: np.ndarray,
    alpha: float,
    gamma: float,
) -> dict:
    """Audit every populated stratum of an audit pool.

    Returns ``{k: StratumAudit}`` for each populated label.  The audit is run on
    the whole calibration pool once per frozen configuration (as in the AAAI
    protocol); it is a diagnostic, not a selection step.
    """
    scores = np.asarray(scores, dtype=float)
    correct = np.asarray(correct, dtype=float)
    cum_cost = np.asarray(cum_cost, dtype=float)
    bucket_id = np.asarray(bucket_id)
    losses_thr, _, _ = stops_from_grid_np(scores, correct, cum_cost, grid)
    losses_depth = 1.0 - correct
    out: dict = {}
    for k in np.unique(bucket_id):
        mask = bucket_id == k
        out[int(k)] = audit_stratum(losses_thr[mask], losses_depth[mask], alpha, gamma, grid, k=int(k))
    return out
