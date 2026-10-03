#!/usr/bin/env python
"""v3 -- the certify-or-route sweep (torch-free, CPU).

For one (dataset, policy, train_seed) pool cache and its ``committed_v3`` JSON:
over ``n_draws`` seeded calibration draws, for every committed lambda_ref key and cost scheme,

  * marginal CAFA   (frozen ltt_select)               -> test risk / cost / stratum risks
  * certify-or-route cascade (tiers 1-3)              -> deployed tier, test risk,
                                                        stratum risks, answered fraction, cost
  * baselines: plug-in, fixed confidence x3, budgets {T/4, T/2, 3T/4},
               full acquisition, Mondrian oracle (per-stratum LTT, joint),
               cheapest-valid test oracle

and, ONCE per (lambda_ref key, split), the localized family-wide audit of every
stratum on the split's full calibration pool (diagnostic; not a selection step).

Every deployed rule is evaluated on its split's independent test split, so the
reported violation counts are population-risk checks.

Multi-split protocol (round 2)
------------------------------
The commit's ``split.test_seeds`` (e.g. 778..782) each define one calpool / test
split of the eval remainder (same probe); the ``n_draws`` (total, 100) calibration
draws are spread evenly (20 per split).  Draw ``d`` of split index ``s`` uses draw id
``s * 1000 + d`` (:func:`cafa.splits_v3.split_draw_id`; split index 0 = the primary
split 778 reproduces the round-1 draw ids).  Each split's calpool / test digests are
checked against the commit.  ``audit`` is the primary split's audit (as in round 1),
``audit_by_split`` holds every split's, and ``deepest_verdict_agreement`` counts the
splits whose deepest-stratum verdict equals the primary split's.  A commit whose
splits differ from ``protocol_v3.test_seeds`` (e.g. a round-1 commit without
``test_seeds``) is refused unless ``--test-seeds`` names the splits explicitly
(diagnostics; then ``--out-dir`` is required so the canonical file is not overwritten).

Noise-aware violation metrics (round 2; the raw rates are unchanged)
--------------------------------------------------------------------
For a deployed rule and each stratum ``k`` in ``K_cal`` (the cascade's calibration
span) with ``n_k > 0`` rows on the test split (answered rows for tier 3), with
``e_k`` test errors:

  * ``test_pvalue_min``     = min_k ``binom_upper_p(e_k, n_k, alpha)``, the exact one-sided
                              binomial p-value of H0: R_k <= alpha;
  * ``certified_violation`` = ``test_pvalue_min <= 0.05`` (False when nothing is deployed);
  * ``max_excess_se``       = max_k (e_k / n_k - alpha) / sqrt(alpha (1 - alpha) / n_k).

Recorded for the cascade (also ``test_errors_by_stratum`` / ``test_n_by_stratum``),
for marginal CAFA (``hidden_*``) and for every baseline (``stratum_*``); summarised
pooled over all draws and per split (``by_split``).

Usage
-----
    python scripts/run_cascade_sweep.py --dataset mnist --policy greedy_entropy --train-seed 0
    python scripts/run_cascade_sweep.py --dataset csv:physionet --policy greedy_entropy --train-seed 0 --n-draws 100

Output: ``${RESULTS_ROOT}/metrics_v3/{dsname}_ts{ts}_{policy}_{score}.json``
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.baselines import (  # noqa: E402
    budget_select,
    fixed_confidence_select,
    oracle_cheapest_valid_select,
    plugin_threshold_select,
)
from cafa.cascade import apply_rule, certify_or_route  # noqa: E402
from cafa.localization import audit_all_strata, binom_upper_p  # noqa: E402
from cafa.metrics import reference_buckets, stops_from_grid_np  # noqa: E402
from cafa.pool import cum_cost_from_order, load_pool_cache  # noqa: E402
from cafa.risk_control import ltt_select, mondrian_select  # noqa: E402
from cafa.splits import split_digest  # noqa: E402
from cafa.splits_v3 import calibration_draw, draws_per_split, split_draw_id, v3_positions_multi  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commit_v3 import build_grid, dsname_of  # noqa: E402

CERT_LEVEL = 0.05     # level of the per-draw test-split check behind ``certified_violation``


def r6(x):
    try:
        return None if x is None else (float(x) if np.isfinite(x) else None)
    except TypeError:
        return x


def counts_by_stratum(loss, answered, bucket_id) -> dict:
    """``{k: (errors, n)}`` of a 0/1 loss vector over the answered rows of each stratum label."""
    b = np.asarray(bucket_id)
    loss = np.asarray(loss, dtype=float)
    answered = np.asarray(answered, dtype=bool)
    out = {}
    for k in np.unique(b):
        m = (b == k) & answered
        n = int(m.sum())
        out[int(k)] = (int(round(float(np.nansum(loss[m])))) if n else 0, n)
    return out


def noise_aware(counts: dict, k_cal, alpha: float, level: float = CERT_LEVEL) -> dict:
    """Exact one-sided binomial check of every K_cal stratum on the test split (see module doc)."""
    kc = {int(k) for k in k_cal}
    pmin, ex = None, None
    for k, (e, n) in counts.items():
        if int(k) not in kc or n == 0:
            continue
        p = float(binom_upper_p(e, n, alpha))
        z = (e / n - alpha) / math.sqrt(alpha * (1.0 - alpha) / n)
        pmin = p if pmin is None else min(pmin, p)
        ex = z if ex is None else max(ex, z)
    return {"test_pvalue_min": pmin, "certified_violation": bool(pmin is not None and pmin <= level),
            "max_excess_se": ex}


def prefixed(d: dict, prefix: str) -> dict:
    return {f"{prefix}{k}": v for k, v in d.items()}


def stratum_risks_of_threshold(scores, correct, cum_cost, grid, j, bucket_id):
    """(per-stratum test risk, aggregate risk, mean cost, per-stratum (errors, n)) of threshold ``grid[j]``."""
    losses, costs, _ = stops_from_grid_np(scores, correct, cum_cost, grid[[int(j)]])
    b = np.asarray(bucket_id)
    return ({int(k): float(losses[b == k, 0].mean()) for k in np.unique(b)},
            float(losses[:, 0].mean()), float(costs[:, 0].mean()),
            counts_by_stratum(losses[:, 0], np.ones(b.shape[0], bool), b))


def stratum_risks_of_depth(correct, cum_cost, t, bucket_id):
    """(per-stratum test risk, aggregate risk, mean cost, per-stratum (errors, n)) of forced depth ``t``."""
    b = np.asarray(bucket_id)
    loss = 1.0 - np.asarray(correct)[:, int(t)]
    return ({int(k): float(loss[b == k].mean()) for k in np.unique(b)},
            float(loss.mean()), float(np.asarray(cum_cost)[:, int(t)].mean()),
            counts_by_stratum(loss, np.ones(b.shape[0], bool), b))


def any_violation(per_stratum: dict, k_cal, alpha: float) -> bool:
    for k, v in per_stratum.items():
        if int(k) in k_cal and v is not None and np.isfinite(v) and v > alpha:
            return True
    return False


def _nanmean(vals):
    """``r6(np.nanmean(vals))`` without the all-NaN RuntimeWarning (e.g. a split whose marginal never certifies)."""
    v = np.asarray(vals, dtype=float)
    return r6(np.nanmean(v)) if np.isfinite(v).any() else None


def _mean_q90(vals):
    v = [float(x) for x in vals if x is not None]
    return (float(np.mean(v)) if v else None, float(np.quantile(v, 0.9)) if v else None, len(v))


def summarize(draws: list, alpha: float) -> dict:
    """Summary of a list of draw records (pooled over all draws, or one split's draws).

    The raw fields are computed exactly as in round 1; the noise-aware fields are added."""
    tiers = np.array([r["cascade"]["tier"] for r in draws])
    summ = {
        "n_draws": len(draws),
        "tier_share": {str(t): float(np.mean(tiers == t)) for t in (0, 1, 2, 3)},
        "certified_deployment_rate": float(np.mean(tiers > 0)),
        "cascade_violation_rate": float(np.mean([r["cascade"]["violation"] for r in draws])),
        "cascade_mean_test_cost": float(np.mean([r["cascade"]["test_cost"] for r in draws])),
        "cascade_mean_answered_fraction": float(np.mean([r["cascade"]["answered_fraction"] for r in draws])),
        "cascade_mean_test_risk": (lambda v: r6(np.mean(v)) if v else None)([r["cascade"]["test_risk"] for r in draws if r["cascade"]["test_risk"] is not None]),
        "marginal_cert_rate": float(np.mean([r["marginal"]["lambda"] is not None for r in draws])),
        "marginal_mean_test_cost": _nanmean([r["marginal"].get("test_cost", np.nan) for r in draws]),
        "marginal_mean_test_risk": _nanmean([r["marginal"].get("test_risk", np.nan) for r in draws]),
        "marginal_aggregate_violation_rate": float(np.mean([("test_risk" in r["marginal"]) and r["marginal"]["test_risk"] > alpha for r in draws])),
        "marginal_max_stratum_over_alpha_mean": _nanmean([r["marginal"].get("max_stratum_over_alpha", np.nan) for r in draws]),
        "marginal_hidden_stratum_violation_rate": float(np.mean([("test_stratum_risk" in r["marginal"]) and any_violation({int(k): v for k, v in r["marginal"]["test_stratum_risk"].items()}, r["cascade"]["k_cal"], alpha) for r in draws])),
        "cost_premium_cascade_over_marginal": None,
        "baselines": {},
    }
    if summ["marginal_mean_test_cost"]:
        summ["cost_premium_cascade_over_marginal"] = float(summ["cascade_mean_test_cost"] / summ["marginal_mean_test_cost"])
    # noise-aware (round 2)
    summ["cascade_certified_violation_rate"] = float(np.mean([r["cascade"]["certified_violation"] for r in draws]))
    m, q, nn = _mean_q90([r["cascade"]["max_excess_se"] for r in draws])
    summ.update({"cascade_max_excess_se_mean": m, "cascade_max_excess_se_q90": q, "cascade_max_excess_se_n": nn})
    summ["marginal_hidden_certified_violation_rate"] = float(np.mean([r["marginal"]["hidden_certified_violation"] for r in draws]))
    m, q, nn = _mean_q90([r["marginal"]["hidden_max_excess_se"] for r in draws])
    summ.update({"marginal_hidden_max_excess_se_mean": m, "marginal_hidden_max_excess_se_q90": q,
                 "marginal_hidden_max_excess_se_n": nn})
    names = sorted({k for r in draws for k in r["baselines"]})
    for name in names:
        vals = [r["baselines"][name] for r in draws if "test_risk" in r["baselines"][name]]
        sv = [v["stratum_violation"] for v in vals if "stratum_violation" in v]  # v3 fix: no False default
        cv = [v["stratum_certified_violation"] for v in vals if "stratum_certified_violation" in v]
        m, q, nn = _mean_q90([v.get("stratum_max_excess_se") for v in vals])
        summ["baselines"][name] = {
            "mean_test_risk": r6(np.mean([v["test_risk"] for v in vals])) if vals else None,
            "mean_test_cost": r6(np.mean([v["test_cost"] for v in vals])) if vals else None,
            "stratum_violation_rate": r6(np.mean(sv)) if sv else None,
            "aggregate_violation_rate": r6(np.mean([v["test_risk"] > alpha for v in vals])) if vals else None,
            "n": len(vals),
            "stratum_certified_violation_rate": r6(np.mean(cv)) if cv else None,
            "stratum_max_excess_se_mean": m, "stratum_max_excess_se_q90": q,
        }
    return summ


def run_one(dataset, policy_token, score, train_seed, *, cfg, paths, n_draws=None,
            pool_dir=None, out_dir=None, committed_path=None, delta_weights=None, test_seeds=None):
    ts = int(train_seed)
    dsname = dsname_of(dataset)
    committed_path = Path(committed_path) if committed_path else \
        Path("configs") / f"committed_v3_{dsname}_ts{ts}.json"
    if not committed_path.exists():
        raise FileNotFoundError(f"{committed_path} not found; run commit_v3.py first.")
    committed = json.loads(committed_path.read_text())
    alpha = float(committed["alpha"])
    delta = float(committed["delta"])
    gamma = float(cfg.get("audit", {}).get("gamma", 0.05))
    d_weights = tuple(delta_weights or cfg.get("cascade", {}).get("delta_weights", (0.5, 0.25, 0.25)))
    grid = build_grid(cfg["method"])
    T = int(committed["T"])
    sp = committed["split"]
    n_draws = int(n_draws or cfg.get("protocol_v3", {}).get("n_draws", 100))
    fixed_t = list(cfg.get("fixed_confidence_t", [0.90, 0.95, 0.99]))
    budget_fracs = list(cfg.get("budget_fracs", [0.25, 0.5, 0.75]))
    schemes_cfg = cfg.get("cost_schemes", None)

    # the splits: the commit's test_seeds (round 2), else its single test_seed (round-1 commits)
    committed_seeds = [int(x) for x in sp.get("test_seeds", [sp["test_seed"]])]
    proto_seeds = [int(x) for x in cfg.get("protocol_v3", {}).get("test_seeds", [sp["test_seed"]])]
    if test_seeds is None and committed_seeds != proto_seeds:
        raise RuntimeError(f"{committed_path} commits test splits {committed_seeds} but protocol_v3.test_seeds is "
                           f"{proto_seeds}: re-commit with --force (round-2 commit_v3), or pass --test-seeds "
                           "(and --out-dir) for a deliberate single-split diagnostic.")
    if test_seeds is not None and out_dir is None:
        raise RuntimeError("--test-seeds restricts the protocol; give --out-dir so the canonical metrics file is not overwritten.")
    seeds = committed_seeds if test_seeds is None else [int(x) for x in test_seeds]
    unknown = sorted(set(seeds) - set(committed_seeds))
    if unknown:
        raise RuntimeError(f"test seeds {unknown} are not committed in {committed_path} (has {committed_seeds}).")
    primary = int(sp["test_seed"])
    if primary not in seeds:
        raise RuntimeError(f"the primary split {primary} must be swept (audit of record).")
    per_split = draws_per_split(n_draws, len(seeds))

    pool_dir = Path(pool_dir) if pool_dir else Path(paths.results_root) / "pool_v3"
    cache_path = pool_dir / f"{dsname}_ts{ts}_{policy_token}_{score}.npz"
    cache = load_pool_cache(cache_path)
    n = int(cache["scores"].shape[0])
    assert n == int(committed["n_heldout"]), "cache size differs from the committed heldout size"
    # v3 guards (provenance): never sweep a partial smoke cache, a cache from a different backbone
    # than the one the commit was made on, or a policy the commit does not contain
    if cache["meta"].get("max_rows"):
        raise RuntimeError(f"{cache_path} is a partial --max-rows smoke cache; delete it and rerun the rollout.")
    sha_c, sha_k = committed.get("cache_meta", {}).get("checkpoint_sha256"), cache["meta"].get("checkpoint_sha256")
    if sha_c and sha_k and sha_c != sha_k:
        raise RuntimeError(f"{cache_path} (checkpoint {sha_k[:12]}) does not match {committed_path} "
                           f"(checkpoint {sha_c[:12]}); re-commit with --force after regenerating caches.")
    if policy_token not in committed["lambda_refs"]:
        raise RuntimeError(f"policy {policy_token!r} is not in {committed_path} (has {sorted(committed['lambda_refs'])}); "
                           "its cache appeared after the commit -- re-commit with --force and say why.")

    # split positions in COMMITTED split-index order (draw ids depend on it); digests checked
    all_pos = v3_positions_multi(n, sp["probe_frac"], sp["probe_seed"], sp["test_frac_of_eval"], committed_seeds)
    splits = []
    for ps in all_pos:
        if ps["test_seed"] not in seeds:
            continue
        ref = sp["digest"] if ps["test_seed"] == primary else sp["by_test_seed"][str(ps["test_seed"])]["digest"]
        for part in ("calpool", "test"):
            if split_digest(ps[part]) != ref[part]:
                raise RuntimeError(f"{part} digest of split {ps['test_seed']} differs from {committed_path}.")
        splits.append(ps)

    costs_by_scheme = {s: np.asarray(v, dtype=float)
                       for s, v in committed["feature_costs_by_scheme"].items()}
    schemes = [s for s in (schemes_cfg or list(costs_by_scheme)) if s in costs_by_scheme]
    if not schemes:
        schemes = ["uniform"]
        costs_by_scheme["uniform"] = np.ones(T, dtype=float)
    cc_all = {s: cum_cost_from_order(cache["order"], costs_by_scheme[s]) for s in schemes}

    S_all, C_all = np.asarray(cache["scores"]), np.asarray(cache["correct"])
    prim = next(ps for ps in splits if ps["test_seed"] == primary)
    full_test_loss_primary = 1.0 - C_all[prim["test"], T]

    lr_map = committed["lambda_refs"][policy_token]
    out = {
        "meta": {"dataset": dataset, "dsname": dsname, "policy": policy_token, "score": score,
                 "train_seed": ts, "T": T, "n_calpool": int(prim["calpool"].size), "n_test": int(prim["test"].size),
                 "n_draws": n_draws, "test_seeds": [int(ps["test_seed"]) for ps in splits],
                 "primary_test_seed": primary, "draws_per_split": per_split,
                 "schemes": schemes, "cache_meta": cache["meta"], "pipeline": "v3",
                 "cert_level": CERT_LEVEL},
        "alpha": alpha, "delta": delta, "gamma": gamma, "delta_weights": list(d_weights),
        "full_acquisition_test_risk": float(full_test_loss_primary.mean()),
        "full_acquisition_test_risk_by_split": {
            str(ps["test_seed"]): float((1.0 - C_all[ps["test"], T]).mean()) for ps in splits},
        "lambda_refs": {},
    }

    for lr_key, lr in lr_map.items():
        e = np.asarray(committed["edges"][policy_token][lr_key]["edges"], dtype=float)
        mu = np.asarray(committed["escalation"][policy_token][lr_key]["mu_asc"], dtype=float)
        esc_order = np.asarray(committed["escalation"][policy_token][lr_key].get("order", []), dtype=int)
        esc_order = esc_order if esc_order.size else None

        # per-split arrays, strata and the localized audit on the split's whole calibration pool
        sd = {}
        for ps in splits:
            seed = int(ps["test_seed"])
            calpool, test = ps["calpool"], ps["test"]
            S_pool, C_pool, S_test, C_test = S_all[calpool], C_all[calpool], S_all[test], C_all[test]
            bid_pool, _ = reference_buckets(S_pool, float(lr), 5, 1, edges=e)
            bid_test, _ = reference_buckets(S_test, float(lr), 5, 1, edges=e)
            cc_pool_u = cc_all["uniform"][calpool] if "uniform" in cc_all else cc_all[schemes[0]][calpool]
            aud = audit_all_strata(S_pool, C_pool, cc_pool_u, grid, bid_pool, alpha, gamma)
            full_test_loss = 1.0 - C_test[:, T]
            sd[seed] = {"ps": ps, "S_pool": S_pool, "C_pool": C_pool, "S_test": S_test, "C_test": C_test,
                        "bid_pool": bid_pool, "bid_test": bid_test,
                        "audit": {str(k): a.as_record() for k, a in aud.items()},
                        "strata_test": {int(k): int((bid_test == k).sum()) for k in np.unique(bid_test)},
                        "full_acq": {str(int(k)): float(full_test_loss[bid_test == k].mean()) for k in np.unique(bid_test)}}

        audit = sd[primary]["audit"]
        deepest = str(max(int(k) for k in audit))
        v0 = audit[deepest]["verdict"]
        block = {"lambda_ref": float(lr), "edges": e.tolist(), "G": int(e.size + 1),
                 "strata_test_sizes": sd[primary]["strata_test"],
                 "strata_test_sizes_by_split": {str(s): v["strata_test"] for s, v in sd.items()},
                 "schemes": {}, "audit": audit,
                 "audit_by_split": {str(s): v["audit"] for s, v in sd.items()},
                 "deepest_stratum": int(deepest),
                 "deepest_verdict_by_split": {str(s): v["audit"].get(deepest, {}).get("verdict") for s, v in sd.items()},
                 "deepest_verdict_agreement": int(sum(v["audit"].get(deepest, {}).get("verdict") == v0 for v in sd.values())),
                 "n_splits": len(sd),
                 # test-split full-acquisition stratum risks (descriptive)
                 "full_acq_test_stratum_risk": sd[primary]["full_acq"],
                 "full_acq_test_stratum_risk_by_split": {str(s): v["full_acq"] for s, v in sd.items()}}

        for scheme in schemes:
            draws = []
            for ps in splits:
                seed = int(ps["test_seed"])
                x = sd[seed]
                calpool, test = ps["calpool"], ps["test"]
                S_pool, C_pool, S_test, C_test = x["S_pool"], x["C_pool"], x["S_test"], x["C_test"]
                bid_pool, bid_test = x["bid_pool"], x["bid_test"]
                cc_pool, cc_test = cc_all[scheme][calpool], cc_all[scheme][test]
                losses_t, costs_t, _ = stops_from_grid_np(S_test, C_test, cc_test, grid)
                for dd in range(per_split):
                    d = split_draw_id(ps["split_index"], dd)
                    cal_pos = calibration_draw(calpool, d, sp["cal_frac_of_pool"])
                    # calibration-draw positions -> row indices into the calpool arrays
                    idx = np.nonzero(np.isin(calpool, cal_pos))[0]
                    S_cal, C_cal, cc_cal = S_pool[idx], C_pool[idx], cc_pool[idx]
                    b_cal = bid_pool[idx]
                    losses_cal, costs_cal, _ = stops_from_grid_np(S_cal, C_cal, cc_cal, grid)

                    rec = {"draw": d, "split_seed": seed, "split_index": int(ps["split_index"])}
                    # cascade (first: its K_cal defines the strata every violation check uses)
                    res = certify_or_route(S_cal, C_cal, cc_cal, grid, mu, alpha, delta, b_cal, d_weights,
                                           escalation_order=esc_order)
                    ap = apply_rule(res, S_test, C_test, cc_test, grid, mu, bid_test)
                    per = {str(k): r6(v["risk"]) for k, v in ap["per_stratum"].items()}
                    cnt = counts_by_stratum(ap["loss"], ap["answered"], bid_test)
                    rec["cascade"] = {
                        "tier": int(res.tier), "rule": res.rule, "param": r6(res.param_value),
                        "k_cal": [int(k) for k in res.k_cal],
                        "test_risk": r6(ap["risk"]), "test_cost": float(ap["mean_cost"]),
                        "answered_fraction": float(ap["answered_fraction"]),
                        "test_stratum_risk": per,
                        "test_stratum_answered": {str(k): float(v["answered_fraction"]) for k, v in ap["per_stratum"].items()},
                        "violation": bool(any_violation({int(k): v for k, v in per.items()}, res.k_cal, alpha)),
                        "tiers_certified": {name: bool(t.certified) for name, t in res.tiers.items()},
                        "test_errors_by_stratum": {str(k): v[0] for k, v in cnt.items()},
                        "test_n_by_stratum": {str(k): v[1] for k, v in cnt.items()},
                        **noise_aware(cnt, res.k_cal, alpha),
                    }
                    # marginal CAFA
                    m = ltt_select(losses_cal, costs_cal, grid, alpha, delta)
                    if m.lambda_idx is None:
                        rec["marginal"] = {"lambda": None, **prefixed(noise_aware({}, res.k_cal, alpha), "hidden_")}
                    else:
                        ps_, agg, cost, cn = stratum_risks_of_threshold(S_test, C_test, cc_test, grid, m.lambda_idx, bid_test)
                        rec["marginal"] = {"lambda": float(m.lambda_value), "test_risk": agg,
                                           "test_cost": cost, "test_stratum_risk": {str(k): v for k, v in ps_.items()},
                                           "max_stratum_over_alpha": float(max(ps_.values()) / alpha),
                                           **prefixed(noise_aware(cn, res.k_cal, alpha), "hidden_")}
                    # baselines (realized on test)
                    bl = {}

                    def _bl(ps_, agg, cost, cn, **extra):
                        return {**extra, "test_risk": agg, "test_cost": cost,
                                "stratum_violation": any_violation(ps_, res.k_cal, alpha),
                                **prefixed(noise_aware(cn, res.k_cal, alpha), "stratum_")}

                    j = plugin_threshold_select(losses_cal, costs_cal, grid, alpha)
                    if j is not None:
                        bl["plugin"] = _bl(*stratum_risks_of_threshold(S_test, C_test, cc_test, grid, j, bid_test),
                                           **{"lambda": float(grid[j])})
                    else:
                        bl["plugin"] = {"lambda": None}
                    for tt in fixed_t:
                        j = fixed_confidence_select(grid, tt)
                        bl[f"fixed_conf_{tt}"] = _bl(*stratum_risks_of_threshold(S_test, C_test, cc_test, grid, j, bid_test))
                    for f in budget_fracs:
                        t = budget_select(int(round(f * T)), T)
                        bl[f"budget_{f}"] = _bl(*stratum_risks_of_depth(C_test, cc_test, t, bid_test), t=int(t))
                    bl["full_acquisition"] = _bl(*stratum_risks_of_depth(C_test, cc_test, T, bid_test))
                    # Mondrian oracle: per-stratum LTT at delta/G (non-deployable; cost floor)
                    mon = mondrian_select(losses_cal, costs_cal, grid, alpha, delta, b_cal, joint=True)
                    mon_cost, mon_risk, mon_abst, mon_ps, mon_cn = [], [], 0, {}, {}
                    for k in np.unique(bid_test):
                        mt = bid_test == k
                        jj = mon.lambda_idx_by_bucket.get(int(k))
                        if jj is None:
                            mon_abst += int(mt.sum()); mon_cost.append(cc_test[mt, T]); mon_risk.append(1.0 - C_test[mt, T])
                        else:
                            mon_cost.append(costs_t[mt, jj]); mon_risk.append(losses_t[mt, jj])
                        # v3 fix: per-stratum test risk of the deployed Mondrian rule (abstained strata at
                        # full acquisition, as in test_risk) -- the record had no stratum_violation key,
                        # so the summary's stratum_violation_rate was always 0.0
                        mon_ps[int(k)] = float(mon_risk[-1].mean())
                        mon_cn[int(k)] = (int(round(float(mon_risk[-1].sum()))), int(mt.sum()))
                    bl["mondrian_oracle"] = _bl(mon_ps, float(np.concatenate(mon_risk).mean()),
                                                float(np.concatenate(mon_cost).mean()), mon_cn,
                                                abstained_fraction=mon_abst / max(test.size, 1))
                    jo = oracle_cheapest_valid_select(losses_t, costs_t, grid, alpha)
                    if jo is not None:
                        # v3 fix: record test_risk (the summary keeps only records with test_risk, so this
                        # baseline was dropped: n=0, cost None) and the stratum violation
                        bl["oracle_cheapest_valid"] = _bl(*stratum_risks_of_threshold(S_test, C_test, cc_test, grid, jo, bid_test),
                                                          **{"lambda": float(grid[jo])})
                    else:
                        bl["oracle_cheapest_valid"] = {"lambda": None}
                    rec["baselines"] = bl
                    draws.append(rec)

            # ---- summary over draws: pooled, and per split ----
            summ = summarize(draws, alpha)
            summ["by_split"] = {str(int(ps["test_seed"])): summarize([r for r in draws if r["split_seed"] == int(ps["test_seed"])], alpha)
                                for ps in splits}
            block["schemes"][scheme] = {"summary": summ, "draws": draws}
        out["lambda_refs"][lr_key] = block
        s0 = block["schemes"][schemes[0]]["summary"]
        vs = [v["cascade_violation_rate"] for v in s0["by_split"].values()]
        print(f"[cascade] {dsname} ts{ts} {policy_token} lr[{lr_key}]={lr:.3f} G={block['G']} | "
              f"cert={s0['certified_deployment_rate']:.2f} tiers={s0['tier_share']} viol={s0['cascade_violation_rate']:.3f} "
              f"(by split {min(vs):.2f}-{max(vs):.2f}) certviol={s0['cascade_certified_violation_rate']:.3f} | "
              f"deepest stratum verdict={v0} (agree {block['deepest_verdict_agreement']}/{block['n_splits']})", flush=True)

    out_dir = Path(out_dir) if out_dir else Path(paths.results_root) / "metrics_v3"
    out_dir.mkdir(parents=True, exist_ok=True)
    op = out_dir / f"{dsname}_ts{ts}_{policy_token}_{score}.json"
    op.write_text(json.dumps(out, indent=1))
    print(f"[cascade] wrote {op}")
    return op


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3 certify-or-route sweep")
    p.add_argument("--dataset", required=True)
    p.add_argument("--policy", default="greedy_entropy")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--score", default=None)
    p.add_argument("--n-draws", type=int, default=None, help="total over all splits (default protocol_v3.n_draws)")
    p.add_argument("--pool-dir", default=None)
    p.add_argument("--out-dir", default=None)
    p.add_argument("--committed", default=None, help="override the committed_v3 JSON (ablations)")
    p.add_argument("--delta-weights", default=None, help="e.g. 0.5,0.25,0.25 (sensitivity, E9)")
    p.add_argument("--test-seeds", default=None, help="subset of the committed test seeds, e.g. 778 (diagnostics)")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    a = p.parse_args(argv)
    cfg = config.load_experiment(a.config)
    paths = config.load_paths()
    score = a.score or cfg["method"].get("procedure_score", "softmax")
    dw = tuple(float(x) for x in a.delta_weights.split(",")) if a.delta_weights else None
    tsd = [int(x) for x in a.test_seeds.split(",")] if a.test_seeds else None
    run_one(a.dataset, a.policy, score, a.train_seed, cfg=cfg, paths=paths, n_draws=a.n_draws,
            pool_dir=a.pool_dir, out_dir=a.out_dir, committed_path=a.committed, delta_weights=dw, test_seeds=tsd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
