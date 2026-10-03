#!/usr/bin/env python
"""v3 -- E5: validity and power of the audit and the cascade on planted strata (CPU).

Three studies, all on :mod:`cafa.synthetic_planted` populations whose true
accuracy is known (so true stratum risks are exact):

  A. LEVEL  -- a feasible stratum (full-information risk alpha - 0.03) is
               declared failed (Type I/II) in at most gamma of audits, and the
               cascade's deployed rule violates a stratum in at most delta of
               draws.  Across n_k in the configured grid.
  B. POWER  -- a Type-II stratum with planted margin Delta in {0.03, 0.05,
               0.10} is certified failed with probability rising in n_k Delta^2;
               reported next to the conservative sufficient condition.
  C. ROUTE  -- on the Type-II populations, the cascade routes to certified
               escalation; report the rate and the true selective risk.
  D. TEST NOISE (round 2; appendix evidence for the noise-aware violation metric)
            -- the deepest stratum's TRUE full-information risk is alpha - 0.004
               (homogeneous stratum, so every full-acquisition rule has that true
               risk); replicates come in blocks of 20 that share ONE test split with
               n_k ~ 2,500 in the deepest stratum (as the 20 draws of one split share
               it in the multi-split protocol).  Reported: the true violation rate
               (deployed rule's TRUE risk > alpha in some K_cal stratum; exact, from a
               beta-quadrature population), the raw test violation rate (test-split
               risk > alpha), the certified-violation rate (exact one-sided binomial
               p-value <= 0.05 on the test split, as in run_cascade_sweep), the mean
               max_excess_se, and the noise-free EXPECTED raw / certified rates given
               the deployed rules' true risks and the test n_k.  Two calibration sizes:
                 D1  as specified: a calibration pool with n_k ~ 2,500 per block and 20
                     draws of 50 % of it (the real protocol's sizes);
                 D2  powered calibration: each replicate draws a fresh calibration
                     sample with n_k ~ 90,000, large enough for the cascade to certify
                     a rule this close to alpha (at the D1 sizes it essentially never
                     does, so D1's rates are all ~0).

Outputs (to --output-dir): planted_validation.csv and PLANTED_VALIDATION.md.

    python scripts/planted_validation.py --output-dir results_v3/planted --n-replicates 1000
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa.cascade import certify_or_route  # noqa: E402
from cafa.commit_rules import escalation_levels, escalation_order_from_probe, n_min_required  # noqa: E402
from cafa.localization import audit_all_strata, binom_upper_p  # noqa: E402
from cafa.synthetic_planted import (  # noqa: E402
    default_strata,
    make_planted_population,
    true_selective_risk,
    true_stratum_risk_of_threshold,
)

ALPHA, DELTA, GAMMA = 0.15, 0.10, 0.05
GRID = np.linspace(0.0, 1.0, 100)
CERT_LEVEL = 0.05            # level of the test-split check behind certified_violation (as in run_cascade_sweep)
C0, ACC_RATE_MULT = 0.1, 3.0  # make_planted_population defaults (the quadrature population mirrors them)


def _strata(scenario: str, margin: float = 0.0):
    strata = default_strata(G=2)
    if scenario == "feasible":
        strata[1].update({"r_easy": ALPHA - float(margin)})
    elif scenario == "typeII":
        # hard core h with risk r_hard; easy risk 0.05: family floor = h r_hard + (1-h) 0.05
        h = 0.5
        r_hard = (ALPHA + margin - (1 - h) * 0.05) / h
        strata[1].update({"r_easy": 0.05, "r_hard": float(min(0.95, r_hard)), "h": h, "s_cap_hard": 0.6})
    return strata


def _planted_margin(strata) -> float:
    s = strata[1]
    floor = s["h"] * s["r_hard"] + (1 - s["h"]) * s["r_easy"]
    return float(floor - ALPHA)


def sufficient_nk(delta_k: float, M: int, gamma: float = GAMMA, eta: float = 0.05) -> int:
    """Conservative conditional sufficient condition n_k Delta^2 >= ln(1/gamma) + ln(M/eta)."""
    return int(math.ceil((math.log(1 / gamma) + math.log(M / eta)) / (delta_k ** 2)))


# ------------------------------------------------------------------------------------------------ #
# Study D -- test noise
# ------------------------------------------------------------------------------------------------ #
def study_d_strata(T: int, gap: float = 0.004, alpha: float = ALPHA):
    """Two strata; the deepest (slow risers) is homogeneous (h = 0) with r_easy set so that its TRUE
    full-information risk E_beta[1 - true_acc_T] equals ``alpha - gap`` exactly:
    risk_T(beta) = r + (1 - r - c0) exp(-3 beta T), beta ~ U(lo, hi)  =>  r = (target - (1-c0) m) / (1 - m)
    with m = E[exp(-3 beta T)]."""
    strata = default_strata(G=2)
    lo, hi = strata[1]["beta"]
    a = ACC_RATE_MULT * T
    m = (math.exp(-a * lo) - math.exp(-a * hi)) / (a * (hi - lo))
    target = float(alpha) - float(gap)
    r = (target - (1.0 - C0) * m) / (1.0 - m)
    if not 0.0 <= r <= 1.0 - C0:
        raise ValueError(f"study D infeasible at T={T}: r_easy={r:.4f} (true_acc would be clipped); "
                         "T must be large enough that (1 - c0) E[exp(-3 beta T)] <= alpha - gap.")
    strata[1].update({"r_easy": r, "h": 0.0})
    return strata


def quadrature_population(strata, T: int, m_per_stratum: int = 20000) -> dict:
    """Deterministic stand-in for the planted POPULATION (h = 0 strata only): every stratum's beta at the
    midpoints of ``m_per_stratum`` equal-probability bins of U(lo, hi); same formulas as
    :func:`make_planted_population`.  Stratum means over it are the true population stratum risks up to
    O(1 / m^2) quadrature error; strata have equal masses in study D, so the rows are equally weighted."""
    sc, acc, lab = [], [], []
    t = np.arange(int(T) + 1, dtype=float)[None, :]
    for k, spec in enumerate(strata):
        if float(spec.get("h", 0.0)) != 0.0 or spec.get("overconfident_from_t") is not None:
            raise ValueError("quadrature_population supports h = 0 strata without overconfidence only.")
        lo, hi = spec["beta"]
        beta = lo + (hi - lo) * (np.arange(m_per_stratum) + 0.5) / m_per_stratum
        A = 1.0 - float(spec.get("r_easy", 0.0))
        sc.append(1.0 - np.exp(-beta[:, None] * t))
        acc.append(np.clip(C0 + (A - C0) * (1.0 - np.exp(-ACC_RATE_MULT * beta[:, None] * t)), 0.0, 1.0))
        lab.append(np.full(m_per_stratum, k, dtype=int))
    return {"scores": np.concatenate(sc), "true_acc": np.concatenate(acc), "stratum": np.concatenate(lab), "T": int(T)}


def _rule_stop_and_answered(pop: dict, res):
    """(stop depth per row, answered mask) of the deployed cascade rule on ``pop``."""
    T = int(pop["T"])
    sc = pop["scores"]
    n = sc.shape[0]
    if res.rule == "threshold":
        crossed = sc >= float(res.param_value)
        return np.where(crossed.any(axis=1), crossed.argmax(axis=1), T), np.ones(n, dtype=bool)
    if res.rule == "budget":
        return np.full(n, int(res.param_idx)), np.ones(n, dtype=bool)
    if res.rule == "escalation":
        return np.full(n, T), sc[:, T] >= float(res.param_value)
    raise ValueError(res.rule)


def _per_stratum(pop: dict, res, values: np.ndarray) -> dict:
    """Per stratum label: (sum, n) of ``values`` (``[n, T+1]``) at the rule's stop depth over answered rows."""
    stop, ans = _rule_stop_and_answered(pop, res)
    v = values[np.arange(stop.shape[0]), stop]
    out = {}
    for k in np.unique(pop["stratum"]):
        m = (pop["stratum"] == k) & ans
        out[int(k)] = (float(v[m].sum()), int(m.sum()))
    return out


def _p_raw_and_cert(R: float, n: int, alpha: float) -> "tuple[float, float]":
    """P(Bin(n, R) / n > alpha) and P(binom_upper_p(Bin(n, R), n, alpha) <= CERT_LEVEL)."""
    k_raw = int(math.floor(round(alpha * n, 9)))             # e / n > alpha  <=>  e > floor(alpha n)
    e = np.arange(n + 1)
    p_up = binom_upper_p(e, n, alpha)
    cert = e[p_up <= CERT_LEVEL]
    k_cert = int(cert.min()) if cert.size else n + 1
    return float(binom.sf(k_raw, n, R)), float(binom.sf(k_cert - 1, n, R)) if k_cert <= n else 0.0


def study_d(config: str, T: int, n_blocks: int, per_block: int, n_split: int, n_cal: int, gap: float = 0.004,
            seed0: int = 0, quad_m: int = 20000, verbose: bool = True) -> dict:
    """One study-D configuration (see the module doc).  ``config`` "D1": the block's calibration pool has
    ``n_split`` rows and each draw is a 50 % subsample of it (``n_cal`` is ignored); "D2": each draw is a fresh
    calibration sample of ``n_cal`` rows.  Every block shares one test split of ``n_split`` rows."""
    strata = study_d_strata(T, gap)
    quad = quadrature_population(strata, T, quad_m)
    deep = len(strata) - 1
    true_full = float((1.0 - quad["true_acc"][quad["stratum"] == deep, T]).mean())
    probe = make_planted_population(4000, T, strata, seed=seed0 + 3)
    fr = np.linspace(0.05, 1.0, 41)
    mu, _ = escalation_levels(probe["scores"][:, T], fr, probe_bucket_id=probe["stratum"])
    order = escalation_order_from_probe(probe["scores"][:, T], probe["correct"][:, T], mu, ALPHA, probe["stratum"])
    recs = []
    for b in range(int(n_blocks)):
        test = make_planted_population(int(n_split), T, strata, seed=seed0 + 31_000 + b)
        if config == "D1":
            calpool = make_planted_population(int(n_split), T, strata, seed=seed0 + 30_000 + b)
            rng = np.random.default_rng(seed0 + 32_000 + b)
        for d in range(int(per_block)):
            if config == "D1":
                idx = np.sort(rng.choice(int(n_split), int(n_split) // 2, replace=False))
                cal = {k: calpool[k][idx] for k in ("scores", "correct", "cum_cost", "stratum")}
            else:
                cal = make_planted_population(int(n_cal), T, strata, seed=seed0 + 40_000 + 1000 * b + d)
            res = certify_or_route(cal["scores"], cal["correct"], cal["cum_cost"], GRID, mu, ALPHA, DELTA,
                                   cal["stratum"], escalation_order=order)
            rec = {"block": b, "tier": int(res.tier), "true_violation": False, "raw_violation": False,
                   "certified_violation": False, "max_excess_se": None, "p_raw": 0.0, "p_cert": 0.0,
                   "true_deep_risk": None, "n_cal_deep": int((cal["stratum"] == deep).sum()),
                   "n_test_deep": int((test["stratum"] == deep).sum())}
            if res.tier > 0:
                tr = _per_stratum(quad, res, 1.0 - quad["true_acc"])
                te = _per_stratum(test, res, 1.0 - test["correct"])
                kc = [int(k) for k in res.k_cal]
                true_r = {k: (s_ / n_ if n_ else float("nan")) for k, (s_, n_) in tr.items()}
                rec["true_deep_risk"] = true_r.get(deep)
                rec["true_violation"] = any(np.isfinite(true_r[k]) and true_r[k] > ALPHA for k in kc if k in true_r)
                pmin, ex, q_raw, q_cert = None, None, 1.0, 1.0
                for k in kc:
                    e_, n_ = te.get(k, (0.0, 0))
                    if n_ == 0:
                        continue
                    e_ = int(round(e_))
                    rec["raw_violation"] |= e_ / n_ > ALPHA
                    p_ = float(binom_upper_p(e_, n_, ALPHA))
                    z_ = (e_ / n_ - ALPHA) / math.sqrt(ALPHA * (1 - ALPHA) / n_)
                    pmin = p_ if pmin is None else min(pmin, p_)
                    ex = z_ if ex is None else max(ex, z_)
                    if np.isfinite(true_r.get(k, float("nan"))):
                        pr, pc = _p_raw_and_cert(true_r[k], n_, ALPHA)
                        q_raw *= 1.0 - pr
                        q_cert *= 1.0 - pc
                rec["certified_violation"] = bool(pmin is not None and pmin <= CERT_LEVEL)
                rec["max_excess_se"] = ex
                rec["p_raw"], rec["p_cert"] = 1.0 - q_raw, 1.0 - q_cert
            recs.append(rec)
    n = len(recs)
    dep = [r for r in recs if r["tier"] > 0]
    ex = [r["max_excess_se"] for r in recs if r["max_excess_se"] is not None]
    blk = [np.mean([r["raw_violation"] for r in recs if r["block"] == b]) for b in range(int(n_blocks))]
    out = {"study": "D_test_noise", "config": config, "n_blocks": int(n_blocks), "per_block": int(per_block),
           "replicates": n, "n_k_cal": int(np.mean([r["n_cal_deep"] for r in recs])),
           "n_k_test": int(np.mean([r["n_test_deep"] for r in recs])), "true_full_info_risk": true_full,
           "alpha": ALPHA, "delta": DELTA,
           "cert_rate": len(dep) / n,
           "tier_share": {str(t): float(np.mean([r["tier"] == t for r in recs])) for t in (0, 1, 2, 3)},
           "true_violation_rate": float(np.mean([r["true_violation"] for r in recs])),
           "raw_test_violation_rate": float(np.mean([r["raw_violation"] for r in recs])),
           "certified_violation_rate": float(np.mean([r["certified_violation"] for r in recs])),
           "expected_raw_rate": float(np.mean([r["p_raw"] for r in recs])),
           "expected_certified_rate": float(np.mean([r["p_cert"] for r in recs])),
           "max_excess_se_mean": float(np.mean(ex)) if ex else None,
           "block_raw_min": float(min(blk)), "block_raw_max": float(max(blk)),
           "deployed_true_deep_risk_min": min((r["true_deep_risk"] for r in dep if r["true_deep_risk"] is not None), default=None),
           "deployed_true_deep_risk_max": max((r["true_deep_risk"] for r in dep if r["true_deep_risk"] is not None), default=None)}
    if verbose:
        print(f"[D] {config} n_k cal~{out['n_k_cal']} test~{out['n_k_test']} {n_blocks}x{per_block}: cert={out['cert_rate']:.3f} "
              f"true={out['true_violation_rate']:.3f} raw={out['raw_test_violation_rate']:.3f} (blocks {out['block_raw_min']:.2f}-"
              f"{out['block_raw_max']:.2f}; expected {out['expected_raw_rate']:.3f}) certified={out['certified_violation_rate']:.3f} "
              f"(expected {out['expected_certified_rate']:.3f})", flush=True)
    return out


def run(out_dir: Path, T: int, n_reps: int, deltas, n_ks, seed0: int = 0, d_cfg: dict = None):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    M = GRID.size + T + 1
    fr = np.linspace(0.05, 1.0, 41)

    # ---------------- A. level ----------------
    for a_margin in (0.03, 0.05):
      strata = _strata("feasible", margin=a_margin)
      probe = make_planted_population(4000, T, strata, seed=seed0 + 1)
      mu, _ = escalation_levels(probe["scores"][:, T], fr, probe_bucket_id=probe["stratum"])
      order = escalation_order_from_probe(probe["scores"][:, T], probe["correct"][:, T], mu, ALPHA, probe["stratum"])
      for n_k in n_ks:
          n = 2 * int(n_k)
          false_fail = 0
          viol = 0
          cert = 0
          for r in range(n_reps):
              pop = make_planted_population(n, T, strata, seed=seed0 + 10_000 + r)
              aud = audit_all_strata(pop["scores"], pop["correct"], pop["cum_cost"], GRID, pop["stratum"], ALPHA, GAMMA)
              false_fail += int(aud[1].verdict in ("type_I", "type_II", "thr_failure_depth_unresolved"))
              res = certify_or_route(pop["scores"], pop["correct"], pop["cum_cost"], GRID, mu, ALPHA, DELTA,
                                     pop["stratum"], escalation_order=order)
              if res.tier == 0:
                  continue
              cert += 1
              if res.rule == "threshold":
                  tr = true_stratum_risk_of_threshold(pop, pop["stratum"], res.param_value)
              elif res.rule == "budget":
                  rr = 1.0 - pop["true_acc"][:, int(res.param_idx)]
                  tr = {int(k): float(rr[pop["stratum"] == k].mean()) for k in (0, 1)}
              else:
                  tr = true_selective_risk(pop, pop["stratum"], res.param_value)
              viol += int(any(np.isfinite(v) and v > ALPHA for k, v in tr.items() if k in res.k_cal))
          rows.append({"study": "A_level", "scenario": "feasible", "n_k": n_k, "margin": -a_margin,
                       "false_failure_rate": false_fail / n_reps, "gamma": GAMMA,
                       "cascade_cert_rate": cert / n_reps, "cascade_violation_rate": viol / n_reps, "delta": DELTA,
                       "power": None, "nk_delta2": None, "sufficient_nk": None, "escalation_rate": None})
          print(f"[A] margin={a_margin:.2f} n_k={n_k:5d} false-failure={false_fail / n_reps:.3f} (gamma {GAMMA})  "
                f"cascade cert={cert / n_reps:.3f} viol={viol / n_reps:.3f} (delta {DELTA})", flush=True)

    # ---------------- B. power + C. route ----------------
    for dk in deltas:
        strata = _strata("typeII", margin=float(dk))
        true_margin = _planted_margin(strata)
        probe = make_planted_population(4000, T, strata, seed=seed0 + 2)
        mu, _ = escalation_levels(probe["scores"][:, T], fr, probe_bucket_id=probe["stratum"])
        order = escalation_order_from_probe(probe["scores"][:, T], probe["correct"][:, T], mu, ALPHA, probe["stratum"])
        for n_k in n_ks:
            n = 2 * int(n_k)
            detected = 0
            esc = 0
            esc_unsafe = 0
            for r in range(n_reps):
                pop = make_planted_population(n, T, strata, seed=seed0 + 20_000 + r)
                aud = audit_all_strata(pop["scores"], pop["correct"], pop["cum_cost"], GRID, pop["stratum"], ALPHA, GAMMA)
                detected += int(aud[1].verdict == "type_II")
                res = certify_or_route(pop["scores"], pop["correct"], pop["cum_cost"], GRID, mu, ALPHA, DELTA,
                                       pop["stratum"], escalation_order=order)
                if res.tier == 3:
                    esc += 1
                    tr = true_selective_risk(pop, pop["stratum"], res.param_value)
                    esc_unsafe += int(any(np.isfinite(v) and v > ALPHA for v in tr.values()))
            rows.append({"study": "B_power_C_route", "scenario": "typeII", "n_k": n_k, "margin": true_margin,
                         "false_failure_rate": None, "gamma": GAMMA,
                         "cascade_cert_rate": None, "cascade_violation_rate": (esc_unsafe / max(esc, 1)),
                         "delta": DELTA, "power": detected / n_reps, "nk_delta2": n_k * true_margin ** 2,
                         "sufficient_nk": sufficient_nk(true_margin, M), "escalation_rate": esc / n_reps})
            print(f"[B/C] Delta={true_margin:.3f} n_k={n_k:5d} nkD2={n_k * true_margin ** 2:6.2f} "
                  f"power={detected / n_reps:.3f} (suff. n_k={sufficient_nk(true_margin, M)})  "
                  f"escalation={esc / n_reps:.3f} unsafe|esc={esc_unsafe / max(esc, 1):.3f}", flush=True)

    # ---------------- D. test noise ----------------
    d_rows = []
    if d_cfg is not None:
        for cfg_name in ("D1", "D2"):
            d_rows.append(study_d(cfg_name, T, d_cfg["blocks"], d_cfg["per_block"], d_cfg["n_split"], d_cfg["n_cal"],
                                  d_cfg["gap"], seed0))

    flat_d = [{k: (v if not isinstance(v, dict) else "/".join(f"{x:.3f}" for x in v.values())) for k, v in r.items()}
              for r in d_rows]
    fields = list(rows[0].keys()) + [k for k in (flat_d[0].keys() if flat_d else []) if k not in rows[0]]
    with open(out_dir / "planted_validation.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="")
        w.writeheader()
        w.writerows(rows)
        w.writerows(flat_d)
    lines = ["# Planted validation (E5)", "",
             f"alpha={ALPHA}, delta={DELTA}, gamma={GAMMA}, T={T}, replicates={n_reps}, M={M}", "",
             "| study | n_k | margin | false-failure (<= gamma) | cascade viol (<= delta) | power | n_k Delta^2 | sufficient n_k | escalation rate |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        f_ = lambda v, d=3: ("" if v is None else f"{v:.{d}f}")
        lines.append(f"| {r['study']} | {r['n_k']} | {f_(r['margin'])} | {f_(r['false_failure_rate'])} | "
                     f"{f_(r['cascade_violation_rate'])} | {f_(r['power'])} | {f_(r['nk_delta2'], 2)} | "
                     f"{'' if r['sufficient_nk'] is None else r['sufficient_nk']} | {f_(r['escalation_rate'])} |")
    if d_rows:
        f3 = lambda v: "" if v is None else f"{v:.3f}"  # noqa: E731
        lines += ["", "## Study D -- test noise (round 2)", "",
                  f"Deepest stratum: TRUE full-information risk alpha - {d_cfg['gap']} = "
                  f"{d_rows[0]['true_full_info_risk']:.4f} (homogeneous; exact by beta quadrature). "
                  f"Blocks of {d_cfg['per_block']} replicates share one test split; certified violation = exact one-sided "
                  f"binomial p <= {CERT_LEVEL} on the test split. Expected rates: noise-free, from the deployed rules' "
                  "true risks and the test n_k.", "",
                  "| config | n_k cal | n_k test | blocks x draws | cert rate | true viol (<= delta) | raw test viol "
                  "| raw by block (min-max) | expected raw | certified viol (<= delta + 0.05) | expected certified "
                  "| mean max_excess_se | deployed true deepest risk (min-max) |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in d_rows:
            lines.append(f"| {r['config']} | {r['n_k_cal']} | {r['n_k_test']} | {r['n_blocks']} x {r['per_block']} | "
                         f"{r['cert_rate']:.3f} | {r['true_violation_rate']:.3f} | {r['raw_test_violation_rate']:.3f} | "
                         f"{r['block_raw_min']:.2f}-{r['block_raw_max']:.2f} | {r['expected_raw_rate']:.3f} | "
                         f"{r['certified_violation_rate']:.3f} | {r['expected_certified_rate']:.3f} | "
                         f"{f3(r['max_excess_se_mean'])} | {f3(r['deployed_true_deep_risk_min'])}-{f3(r['deployed_true_deep_risk_max'])} |")
    (out_dir / "PLANTED_VALIDATION.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {out_dir / 'planted_validation.csv'} and PLANTED_VALIDATION.md")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", default="results_v3/planted")
    p.add_argument("--T", type=int, default=30)
    p.add_argument("--n-replicates", type=int, default=1000)
    p.add_argument("--deltas", default="0.03,0.05,0.10")
    p.add_argument("--n-k", default="250,500,1000,2000,4000")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--d-blocks", type=int, default=10, help="study D: blocks (one shared test split each)")
    p.add_argument("--d-per-block", type=int, default=20, help="study D: replicates per block (10 x 20 = 200)")
    p.add_argument("--d-n-split", type=int, default=5000, help="study D: rows per split (deepest n_k ~ half)")
    p.add_argument("--d-n-cal", type=int, default=180000, help="study D2: rows per powered calibration sample")
    p.add_argument("--d-gap", type=float, default=0.004, help="study D: alpha minus the true full-info risk")
    p.add_argument("--skip-d", action="store_true")
    a = p.parse_args(argv)
    d_cfg = None if a.skip_d else {"blocks": a.d_blocks, "per_block": a.d_per_block, "n_split": a.d_n_split,
                                   "n_cal": a.d_n_cal, "gap": a.d_gap}
    run(Path(a.output_dir), a.T, a.n_replicates, [float(x) for x in a.deltas.split(",")],
        [int(x) for x in a.n_k.split(",")], a.seed, d_cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
