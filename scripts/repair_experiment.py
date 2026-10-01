#!/usr/bin/env python
"""v3 -- E7: audit-guided repair (torch-free).

Takes a BEFORE pool cache (the system that produced a certified failure) and
an AFTER pool cache (same dataset, same train_seed -> same heldout rows in the
same order; a different predictor and/or policy) and re-audits the AFTER system
on the BEFORE system's committed strata.  The stratum map is a label-free
function of the input (reference depth under the BEFORE trajectory), so the
AFTER system can be audited and deployed on exactly the same partition.

Reports, per lambda_ref key: the deepest-stratum verdict before/after, the
family minima, the full-information stratum risk, and the cascade tier shares
and test violation rate before/after over ``--n-draws`` calibration draws.

    python scripts/repair_experiment.py --dataset mnist --train-seed 0 \
        --before-cache $RESULTS_ROOT/pool_v2/mnist_ts0_greedy_entropy_softmax.npz \
        --after-cache  $RESULTS_ROOT/pool_v3/mnist_ts0_greedy_entropy_softmax.npz \
        --committed configs/committed_v3_mnist_ts0.json --label predictor_upgrade
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.cascade import apply_rule, certify_or_route  # noqa: E402
from cafa.localization import audit_all_strata  # noqa: E402
from cafa.metrics import reference_buckets  # noqa: E402
from cafa.pool import cum_cost_from_order, load_pool_cache  # noqa: E402
from cafa.splits_v3 import calibration_draw, v3_positions  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commit_v3 import build_grid  # noqa: E402


def _cascade_stats(S, C, cc, grid, mu, order, alpha, delta, bid_pool, bid_test, S_t, C_t, cc_t,
                   calpool, n_draws, cal_frac, d_weights):
    tiers, viol, costs = [], 0, []
    for d in range(n_draws):
        cal_pos = calibration_draw(calpool, d, cal_frac)
        idx = np.nonzero(np.isin(calpool, cal_pos))[0]
        res = certify_or_route(S[idx], C[idx], cc[idx], grid, mu, alpha, delta, bid_pool[idx], d_weights,
                               escalation_order=order)
        ap = apply_rule(res, S_t, C_t, cc_t, grid, mu, bid_test)
        tiers.append(res.tier)
        costs.append(ap["mean_cost"])
        viol += int(any(np.isfinite(v["risk"]) and v["risk"] > alpha for k, v in ap["per_stratum"].items() if k in res.k_cal))
    tiers = np.asarray(tiers)
    return {"tier_share": {str(t): float(np.mean(tiers == t)) for t in (0, 1, 2, 3)},
            "certified_rate": float(np.mean(tiers > 0)), "violation_rate": viol / n_draws,
            "mean_test_cost": float(np.mean(costs))}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--before-cache", required=True)
    p.add_argument("--after-cache", required=True)
    p.add_argument("--committed", required=True, help="committed_v3 JSON of the BEFORE system")
    p.add_argument("--policy", default="greedy_entropy", help="policy key in the committed JSON")
    p.add_argument("--label", default="repair")
    p.add_argument("--n-draws", type=int, default=None, help="default: protocol_v3.n_draws (100)")
    p.add_argument("--cost-scheme", default="uniform")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    p.add_argument("--output", default=None)
    a = p.parse_args(argv)

    cfg = config.load_experiment(a.config)
    grid = build_grid(cfg["method"])
    gamma = float(cfg.get("audit", {}).get("gamma", 0.05))
    d_weights = tuple(cfg.get("cascade", {}).get("delta_weights", (0.5, 0.25, 0.25)))
    # v3 fix: the default was 50 draws; the protocol fixes n_draws = 100 (as in run_cascade_sweep)
    n_draws = int(a.n_draws or cfg.get("protocol_v3", {}).get("n_draws", 100))
    committed = json.loads(Path(a.committed).read_text())
    alpha, delta = float(committed["alpha"]), float(committed["delta"])
    sp = committed["split"]

    before = load_pool_cache(a.before_cache)
    after = load_pool_cache(a.after_cache)
    assert before["scores"].shape[0] == after["scores"].shape[0], "caches must cover the same heldout rows"
    assert np.array_equal(before["y"], after["y"]), "label vectors differ: not the same heldout rows/order"
    n = int(before["scores"].shape[0])
    T = int(before["scores"].shape[1] - 1)
    pos = v3_positions(n, sp["probe_frac"], sp["probe_seed"], sp["test_frac_of_eval"], sp["test_seed"])
    calpool, test = pos["calpool"], pos["test"]
    costs = np.asarray(committed["feature_costs_by_scheme"].get(a.cost_scheme, [1.0] * T), dtype=float)

    report = {"dataset": a.dataset, "train_seed": a.train_seed, "label": a.label, "alpha": alpha,
              "n_draws": n_draws, "before_cache": str(a.before_cache), "after_cache": str(a.after_cache),
              "committed": str(a.committed), "policy": a.policy, "lambda_refs": {}}
    for lr_key, lr in committed["lambda_refs"][a.policy].items():
        e = np.asarray(committed["edges"][a.policy][lr_key]["edges"], dtype=float)
        mu = np.asarray(committed["escalation"][a.policy][lr_key]["mu_asc"], dtype=float)
        order = np.asarray(committed["escalation"][a.policy][lr_key].get("order", []), dtype=int)
        order = order if order.size else None
        # strata from the BEFORE trajectories (label-free), applied to both systems
        bid_pool, _ = reference_buckets(np.asarray(before["scores"])[calpool], float(lr), 5, 1, edges=e)
        bid_test, _ = reference_buckets(np.asarray(before["scores"])[test], float(lr), 5, 1, edges=e)
        block = {"lambda_ref": float(lr), "G": int(e.size + 1)}
        for name, cache in (("before", before), ("after", after)):
            S, C = np.asarray(cache["scores"]), np.asarray(cache["correct"])
            cc = cum_cost_from_order(cache["order"], costs)
            aud = audit_all_strata(S[calpool], C[calpool], cc[calpool], grid, bid_pool, alpha, gamma)
            deepest = max(aud)
            a_d = aud[deepest]
            stats = _cascade_stats(S[calpool], C[calpool], cc[calpool], grid, mu, order, alpha, delta,
                                   bid_pool, bid_test, S[test], C[test], cc[test], calpool, n_draws,
                                   sp["cal_frac_of_pool"], d_weights)
            block[name] = {"deepest_stratum": int(deepest), "verdict": a_d.verdict,
                           "rmin_thr": a_d.rmin_thr, "rmin_depth": a_d.rmin_depth, "r_full": a_d.r_full,
                           "p_thr": a_d.p_thr, "p_depth": a_d.p_depth,
                           "all_verdicts": {str(k): v.verdict for k, v in aud.items()},
                           "cascade": stats}
        report["lambda_refs"][lr_key] = block
        b, c = block["before"], block["after"]
        print(f"[repair:{a.label}] lr[{lr_key}]={lr:.3f} deepest k={b['deepest_stratum']}: "
              f"{b['verdict']} (rmin {min(b['rmin_thr'], b['rmin_depth']):.3f}, full {b['r_full']:.3f}) -> "
              f"{c['verdict']} (rmin {min(c['rmin_thr'], c['rmin_depth']):.3f}, full {c['r_full']:.3f}); "
              f"tier1 {b['cascade']['tier_share']['1']:.2f} -> {c['cascade']['tier_share']['1']:.2f}; "
              f"viol {b['cascade']['violation_rate']:.2f} -> {c['cascade']['violation_rate']:.2f}", flush=True)

    out = Path(a.output) if a.output else Path("results_v3") / "repair" / f"{a.dataset.replace(':', '-')}_ts{a.train_seed}_{a.label}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
