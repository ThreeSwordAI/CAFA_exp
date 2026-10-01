#!/usr/bin/env python
"""v3 -- the certify-or-route sweep (torch-free, CPU).

For one (dataset, policy, train_seed) pool cache and its ``committed_v3`` JSON:
over ``n_draws`` seeded calibration draws from the calibration pool, for every
committed lambda_ref key and cost scheme,

  * marginal CAFA   (frozen ltt_select)               -> test risk / cost / stratum risks
  * certify-or-route cascade (tiers 1-3)              -> deployed tier, test risk,
                                                        stratum risks, answered fraction, cost
  * baselines: plug-in, fixed confidence x3, budgets {T/4, T/2, 3T/4},
               full acquisition, Mondrian oracle (per-stratum LTT, joint),
               cheapest-valid test oracle

and, ONCE per (lambda_ref key), the localized family-wide audit of every
stratum on the full calibration pool (diagnostic; not a selection step).

Every deployed rule is evaluated on the FIXED, independent test split, so the
reported violation counts are population-risk checks.

Usage
-----
    python scripts/run_cascade_sweep.py --dataset mnist --policy greedy_entropy --train-seed 0
    python scripts/run_cascade_sweep.py --dataset csv:physionet --policy greedy_entropy --train-seed 0 --n-draws 100

Output: ``${RESULTS_ROOT}/metrics_v3/{dsname}_ts{ts}_{policy}_{score}.json``
"""

from __future__ import annotations

import argparse
import json
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
from cafa.localization import audit_all_strata  # noqa: E402
from cafa.metrics import reference_buckets, stops_from_grid_np  # noqa: E402
from cafa.pool import cum_cost_from_order, load_pool_cache  # noqa: E402
from cafa.risk_control import ltt_select, mondrian_select  # noqa: E402
from cafa.splits_v3 import calibration_draw, v3_positions  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commit_v3 import build_grid, dsname_of  # noqa: E402


def r6(x):
    try:
        return None if x is None else (float(x) if np.isfinite(x) else None)
    except TypeError:
        return x


def stratum_risks_of_threshold(scores, correct, cum_cost, grid, j, bucket_id):
    losses, costs, _ = stops_from_grid_np(scores, correct, cum_cost, grid[[int(j)]])
    b = np.asarray(bucket_id)
    return ({int(k): float(losses[b == k, 0].mean()) for k in np.unique(b)},
            float(losses[:, 0].mean()), float(costs[:, 0].mean()))


def stratum_risks_of_depth(correct, cum_cost, t, bucket_id):
    b = np.asarray(bucket_id)
    loss = 1.0 - np.asarray(correct)[:, int(t)]
    return ({int(k): float(loss[b == k].mean()) for k in np.unique(b)},
            float(loss.mean()), float(np.asarray(cum_cost)[:, int(t)].mean()))


def any_violation(per_stratum: dict, k_cal, alpha: float) -> bool:
    for k, v in per_stratum.items():
        if int(k) in k_cal and v is not None and np.isfinite(v) and v > alpha:
            return True
    return False


def run_one(dataset, policy_token, score, train_seed, *, cfg, paths, n_draws=None,
            pool_dir=None, out_dir=None, committed_path=None, delta_weights=None):
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

    pool_dir = Path(pool_dir) if pool_dir else Path(paths.results_root) / "pool_v3"
    cache_path = pool_dir / f"{dsname}_ts{ts}_{policy_token}_{score}.npz"
    cache = load_pool_cache(cache_path)
    n = int(cache["scores"].shape[0])
    assert n == int(committed["n_heldout"]), "cache size differs from the committed heldout size"
    pos = v3_positions(n, sp["probe_frac"], sp["probe_seed"], sp["test_frac_of_eval"], sp["test_seed"])
    calpool, test = pos["calpool"], pos["test"]

    costs_by_scheme = {s: np.asarray(v, dtype=float)
                       for s, v in committed["feature_costs_by_scheme"].items()}
    schemes = [s for s in (schemes_cfg or list(costs_by_scheme)) if s in costs_by_scheme]
    if not schemes:
        schemes = ["uniform"]
        costs_by_scheme["uniform"] = np.ones(T, dtype=float)
    cc_all = {s: cum_cost_from_order(cache["order"], costs_by_scheme[s]) for s in schemes}

    S_all, C_all = np.asarray(cache["scores"]), np.asarray(cache["correct"])
    S_pool, C_pool = S_all[calpool], C_all[calpool]
    S_test, C_test = S_all[test], C_all[test]
    full_test_loss = 1.0 - C_test[:, T]

    lr_map = committed["lambda_refs"][policy_token]
    out = {
        "meta": {"dataset": dataset, "dsname": dsname, "policy": policy_token, "score": score,
                 "train_seed": ts, "T": T, "n_calpool": int(calpool.size), "n_test": int(test.size),
                 "n_draws": n_draws, "schemes": schemes, "cache_meta": cache["meta"],
                 "pipeline": "v3"},
        "alpha": alpha, "delta": delta, "gamma": gamma, "delta_weights": list(d_weights),
        "full_acquisition_test_risk": float(full_test_loss.mean()),
        "lambda_refs": {},
    }

    for lr_key, lr in lr_map.items():
        e = np.asarray(committed["edges"][policy_token][lr_key]["edges"], dtype=float)
        mu = np.asarray(committed["escalation"][policy_token][lr_key]["mu_asc"], dtype=float)
        esc_order = np.asarray(committed["escalation"][policy_token][lr_key].get("order", []), dtype=int)
        esc_order = esc_order if esc_order.size else None
        bid_pool, _ = reference_buckets(S_pool, float(lr), 5, 1, edges=e)
        bid_test, _ = reference_buckets(S_test, float(lr), 5, 1, edges=e)
        strata_test = {int(k): int((bid_test == k).sum()) for k in np.unique(bid_test)}

        block = {"lambda_ref": float(lr), "edges": e.tolist(), "G": int(e.size + 1),
                 "strata_test_sizes": strata_test, "schemes": {}, "audit": {}}

        # ---- localized audit, once per lambda_ref on the whole calibration pool ----
        cc_pool_u = cc_all["uniform"][calpool] if "uniform" in cc_all else cc_all[schemes[0]][calpool]
        aud = audit_all_strata(S_pool, C_pool, cc_pool_u, grid, bid_pool, alpha, gamma)
        block["audit"] = {str(k): a.as_record() for k, a in aud.items()}
        # test-split full-acquisition stratum risks (descriptive)
        block["full_acq_test_stratum_risk"] = {
            str(int(k)): float(full_test_loss[bid_test == k].mean()) for k in np.unique(bid_test)}

        for scheme in schemes:
            cc_pool, cc_test = cc_all[scheme][calpool], cc_all[scheme][test]
            draws = []
            for d in range(n_draws):
                cal_pos = calibration_draw(calpool, d, sp["cal_frac_of_pool"])
                # calibration-draw positions -> row indices into the calpool arrays
                idx = np.nonzero(np.isin(calpool, cal_pos))[0]
                S_cal, C_cal, cc_cal = S_pool[idx], C_pool[idx], cc_pool[idx]
                b_cal = bid_pool[idx]
                losses_cal, costs_cal, _ = stops_from_grid_np(S_cal, C_cal, cc_cal, grid)

                rec = {"draw": d}
                # marginal CAFA
                m = ltt_select(losses_cal, costs_cal, grid, alpha, delta)
                if m.lambda_idx is None:
                    rec["marginal"] = {"lambda": None}
                else:
                    ps, agg, cost = stratum_risks_of_threshold(S_test, C_test, cc_test, grid, m.lambda_idx, bid_test)
                    rec["marginal"] = {"lambda": float(m.lambda_value), "test_risk": agg,
                                       "test_cost": cost, "test_stratum_risk": {str(k): v for k, v in ps.items()},
                                       "max_stratum_over_alpha": float(max(ps.values()) / alpha)}
                # cascade
                res = certify_or_route(S_cal, C_cal, cc_cal, grid, mu, alpha, delta, b_cal, d_weights,
                                       escalation_order=esc_order)
                ap = apply_rule(res, S_test, C_test, cc_test, grid, mu, bid_test)
                per = {str(k): r6(v["risk"]) for k, v in ap["per_stratum"].items()}
                rec["cascade"] = {
                    "tier": int(res.tier), "rule": res.rule, "param": r6(res.param_value),
                    "k_cal": [int(k) for k in res.k_cal],
                    "test_risk": r6(ap["risk"]), "test_cost": float(ap["mean_cost"]),
                    "answered_fraction": float(ap["answered_fraction"]),
                    "test_stratum_risk": per,
                    "test_stratum_answered": {str(k): float(v["answered_fraction"]) for k, v in ap["per_stratum"].items()},
                    "violation": bool(any_violation({int(k): v for k, v in per.items()}, res.k_cal, alpha)),
                    "tiers_certified": {name: bool(t.certified) for name, t in res.tiers.items()},
                }
                # baselines (realized on test)
                bl = {}
                j = plugin_threshold_select(losses_cal, costs_cal, grid, alpha)
                if j is not None:
                    ps, agg, cost = stratum_risks_of_threshold(S_test, C_test, cc_test, grid, j, bid_test)
                    bl["plugin"] = {"lambda": float(grid[j]), "test_risk": agg, "test_cost": cost,
                                    "stratum_violation": any_violation(ps, res.k_cal, alpha)}
                else:
                    bl["plugin"] = {"lambda": None}
                for tt in fixed_t:
                    j = fixed_confidence_select(grid, tt)
                    ps, agg, cost = stratum_risks_of_threshold(S_test, C_test, cc_test, grid, j, bid_test)
                    bl[f"fixed_conf_{tt}"] = {"test_risk": agg, "test_cost": cost,
                                              "stratum_violation": any_violation(ps, res.k_cal, alpha)}
                for f in budget_fracs:
                    t = budget_select(int(round(f * T)), T)
                    ps, agg, cost = stratum_risks_of_depth(C_test, cc_test, t, bid_test)
                    bl[f"budget_{f}"] = {"t": int(t), "test_risk": agg, "test_cost": cost,
                                         "stratum_violation": any_violation(ps, res.k_cal, alpha)}
                ps, agg, cost = stratum_risks_of_depth(C_test, cc_test, T, bid_test)
                bl["full_acquisition"] = {"test_risk": agg, "test_cost": cost,
                                          "stratum_violation": any_violation(ps, res.k_cal, alpha)}
                # Mondrian oracle: per-stratum LTT at delta/G (non-deployable; cost floor)
                mon = mondrian_select(losses_cal, costs_cal, grid, alpha, delta, b_cal, joint=True)
                losses_t, costs_t, _ = stops_from_grid_np(S_test, C_test, cc_test, grid)
                mon_cost, mon_risk, mon_abst = [], [], 0
                for k in np.unique(bid_test):
                    mt = bid_test == k
                    jj = mon.lambda_idx_by_bucket.get(int(k))
                    if jj is None:
                        mon_abst += int(mt.sum()); mon_cost.append(cc_test[mt, T]); mon_risk.append(1.0 - C_test[mt, T])
                    else:
                        mon_cost.append(costs_t[mt, jj]); mon_risk.append(losses_t[mt, jj])
                bl["mondrian_oracle"] = {"test_risk": float(np.concatenate(mon_risk).mean()),
                                        "test_cost": float(np.concatenate(mon_cost).mean()),
                                        "abstained_fraction": mon_abst / max(test.size, 1)}
                jo = oracle_cheapest_valid_select(losses_t, costs_t, grid, alpha)
                bl["oracle_cheapest_valid"] = ({"lambda": float(grid[jo]), "test_cost": float(costs_t[:, jo].mean())}
                                               if jo is not None else {"lambda": None})
                rec["baselines"] = bl
                draws.append(rec)

            # ---- summary over draws ----
            tiers = np.array([r["cascade"]["tier"] for r in draws])
            summ = {
                "tier_share": {str(t): float(np.mean(tiers == t)) for t in (0, 1, 2, 3)},
                "certified_deployment_rate": float(np.mean(tiers > 0)),
                "cascade_violation_rate": float(np.mean([r["cascade"]["violation"] for r in draws])),
                "cascade_mean_test_cost": float(np.mean([r["cascade"]["test_cost"] for r in draws])),
                "cascade_mean_answered_fraction": float(np.mean([r["cascade"]["answered_fraction"] for r in draws])),
                "cascade_mean_test_risk": (lambda v: r6(np.mean(v)) if v else None)([r["cascade"]["test_risk"] for r in draws if r["cascade"]["test_risk"] is not None]),
                "marginal_cert_rate": float(np.mean([r["marginal"]["lambda"] is not None for r in draws])),
                "marginal_mean_test_cost": r6(np.nanmean([r["marginal"].get("test_cost", np.nan) for r in draws])),
                "marginal_mean_test_risk": r6(np.nanmean([r["marginal"].get("test_risk", np.nan) for r in draws])),
                "marginal_aggregate_violation_rate": float(np.mean([("test_risk" in r["marginal"]) and r["marginal"]["test_risk"] > alpha for r in draws])),
                "marginal_max_stratum_over_alpha_mean": r6(np.nanmean([r["marginal"].get("max_stratum_over_alpha", np.nan) for r in draws])),
                "marginal_hidden_stratum_violation_rate": float(np.mean([("test_stratum_risk" in r["marginal"]) and any_violation({int(k): v for k, v in r["marginal"]["test_stratum_risk"].items()}, r["cascade"]["k_cal"], alpha) for r in draws])),
                "cost_premium_cascade_over_marginal": None,
                "baselines": {},
            }
            if summ["marginal_mean_test_cost"]:
                summ["cost_premium_cascade_over_marginal"] = float(summ["cascade_mean_test_cost"] / summ["marginal_mean_test_cost"])
            names = sorted({k for r in draws for k in r["baselines"]})
            for name in names:
                vals = [r["baselines"][name] for r in draws if "test_risk" in r["baselines"][name]]
                summ["baselines"][name] = {
                    "mean_test_risk": r6(np.mean([v["test_risk"] for v in vals])) if vals else None,
                    "mean_test_cost": r6(np.mean([v["test_cost"] for v in vals])) if vals else None,
                    "stratum_violation_rate": r6(np.mean([v.get("stratum_violation", False) for v in vals])) if vals else None,
                    "aggregate_violation_rate": r6(np.mean([v["test_risk"] > alpha for v in vals])) if vals else None,
                    "n": len(vals),
                }
            block["schemes"][scheme] = {"summary": summ, "draws": draws}
        out["lambda_refs"][lr_key] = block
        deepest = max(int(k) for k in block["audit"])
        s0 = block["schemes"][schemes[0]]["summary"]
        print(f"[cascade] {dsname} ts{ts} {policy_token} lr[{lr_key}]={lr:.3f} G={block['G']} | "
              f"cert={s0['certified_deployment_rate']:.2f} tiers={s0['tier_share']} viol={s0['cascade_violation_rate']:.3f} "
              f"| deepest stratum verdict={block['audit'][str(deepest)]['verdict']}", flush=True)

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
    p.add_argument("--n-draws", type=int, default=None)
    p.add_argument("--pool-dir", default=None)
    p.add_argument("--out-dir", default=None)
    p.add_argument("--committed", default=None, help="override the committed_v3 JSON (ablations)")
    p.add_argument("--delta-weights", default=None, help="e.g. 0.5,0.25,0.25 (sensitivity, E9)")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    a = p.parse_args(argv)
    cfg = config.load_experiment(a.config)
    paths = config.load_paths()
    score = a.score or cfg["method"].get("procedure_score", "softmax")
    dw = tuple(float(x) for x in a.delta_weights.split(",")) if a.delta_weights else None
    run_one(a.dataset, a.policy, score, a.train_seed, cfg=cfg, paths=paths, n_draws=a.n_draws,
            pool_dir=a.pool_dir, out_dir=a.out_dir, committed_path=a.committed, delta_weights=dw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
