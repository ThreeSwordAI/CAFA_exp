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

Round 2: multi-split protocol as in run_cascade_sweep (the commit's ``split.test_seeds``, ``n_draws``
total = 20 per split, draw id ``split_index * 1000 + d``, digests checked) and the same noise-aware
metrics (``certified_violation_rate``, ``max_excess_se_mean`` / ``_q90``); the JSON layout is unchanged
plus ``cascade.by_split`` and the deepest-stratum verdict per split.  The audit of record is the
primary split's (``split.test_seed``), as before.
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
from cafa.splits import split_digest  # noqa: E402
from cafa.splits_v3 import calibration_draw, draws_per_split, split_draw_id, v3_positions_multi  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commit_v3 import build_grid  # noqa: E402
from run_cascade_sweep import counts_by_stratum, noise_aware  # noqa: E402


def _stats(recs: list) -> dict:
    tiers = np.asarray([r["tier"] for r in recs])
    ex = [r["max_excess_se"] for r in recs if r["max_excess_se"] is not None]
    return {"tier_share": {str(t): float(np.mean(tiers == t)) for t in (0, 1, 2, 3)},
            "certified_rate": float(np.mean(tiers > 0)),
            "violation_rate": float(np.mean([r["violation"] for r in recs])),
            "mean_test_cost": float(np.mean([r["cost"] for r in recs])),
            "certified_violation_rate": float(np.mean([r["certified_violation"] for r in recs])),
            "max_excess_se_mean": float(np.mean(ex)) if ex else None,
            "max_excess_se_q90": float(np.quantile(ex, 0.9)) if ex else None,
            "n_draws": len(recs)}


def _cascade_stats(S, C, cc, grid, mu, order, alpha, delta, splits, per_split, cal_frac, d_weights):
    """Cascade over ``per_split`` draws on each split; ``splits`` holds the per-split positions and the
    (BEFORE-trajectory) strata of its calpool and test rows."""
    recs = []
    for x in splits:
        calpool, test = x["calpool"], x["test"]
        Sp, Cp, ccp = S[calpool], C[calpool], cc[calpool]
        St, Ct, cct = S[test], C[test], cc[test]
        for dd in range(per_split):
            cal_pos = calibration_draw(calpool, split_draw_id(x["split_index"], dd), cal_frac)
            idx = np.nonzero(np.isin(calpool, cal_pos))[0]
            res = certify_or_route(Sp[idx], Cp[idx], ccp[idx], grid, mu, alpha, delta, x["bid_pool"][idx], d_weights,
                                   escalation_order=order)
            ap = apply_rule(res, St, Ct, cct, grid, mu, x["bid_test"])
            na = noise_aware(counts_by_stratum(ap["loss"], ap["answered"], x["bid_test"]), res.k_cal, alpha)
            recs.append({"split_seed": int(x["test_seed"]), "tier": int(res.tier), "cost": float(ap["mean_cost"]),
                         "violation": bool(any(np.isfinite(v["risk"]) and v["risk"] > alpha
                                               for k, v in ap["per_stratum"].items() if k in res.k_cal)),
                         "certified_violation": na["certified_violation"], "max_excess_se": na["max_excess_se"]})
    out = _stats(recs)
    out["by_split"] = {str(int(x["test_seed"])): _stats([r for r in recs if r["split_seed"] == int(x["test_seed"])])
                       for x in splits}
    return out


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
    primary = int(sp["test_seed"])
    seeds = [int(x) for x in sp.get("test_seeds", [primary])]
    proto_seeds = [int(x) for x in cfg.get("protocol_v3", {}).get("test_seeds", [primary])]
    if seeds != proto_seeds:
        print(f"ERROR: {a.committed} commits test splits {seeds} but protocol_v3.test_seeds is {proto_seeds}; "
              "re-commit it with the round-2 commit_v3.py (--force).", file=sys.stderr)
        return 2
    per_split = draws_per_split(n_draws, len(seeds))
    splits = v3_positions_multi(n, sp["probe_frac"], sp["probe_seed"], sp["test_frac_of_eval"], seeds)
    for ps in splits:
        ref = sp["digest"] if ps["test_seed"] == primary else sp["by_test_seed"][str(ps["test_seed"])]["digest"]
        assert all(split_digest(ps[k]) == ref[k] for k in ("calpool", "test")), f"split {ps['test_seed']} digest mismatch"
    prim = next(ps for ps in splits if ps["test_seed"] == primary)
    calpool = prim["calpool"]
    costs = np.asarray(committed["feature_costs_by_scheme"].get(a.cost_scheme, [1.0] * T), dtype=float)

    report = {"dataset": a.dataset, "train_seed": a.train_seed, "label": a.label, "alpha": alpha,
              "n_draws": n_draws, "before_cache": str(a.before_cache), "after_cache": str(a.after_cache),
              "committed": str(a.committed), "policy": a.policy, "test_seeds": seeds,
              "primary_test_seed": primary, "draws_per_split": per_split, "lambda_refs": {}}
    for lr_key, lr in committed["lambda_refs"][a.policy].items():
        e = np.asarray(committed["edges"][a.policy][lr_key]["edges"], dtype=float)
        mu = np.asarray(committed["escalation"][a.policy][lr_key]["mu_asc"], dtype=float)
        order = np.asarray(committed["escalation"][a.policy][lr_key].get("order", []), dtype=int)
        order = order if order.size else None
        # strata from the BEFORE trajectories (label-free), applied to both systems, on every split
        Sb = np.asarray(before["scores"])
        sx = [dict(ps, bid_pool=reference_buckets(Sb[ps["calpool"]], float(lr), 5, 1, edges=e)[0],
                   bid_test=reference_buckets(Sb[ps["test"]], float(lr), 5, 1, edges=e)[0]) for ps in splits]
        bid_pool = next(x["bid_pool"] for x in sx if x["test_seed"] == primary)
        block = {"lambda_ref": float(lr), "G": int(e.size + 1)}
        for name, cache in (("before", before), ("after", after)):
            S, C = np.asarray(cache["scores"]), np.asarray(cache["correct"])
            cc = cum_cost_from_order(cache["order"], costs)
            aud = audit_all_strata(S[calpool], C[calpool], cc[calpool], grid, bid_pool, alpha, gamma)
            deepest = max(aud)
            a_d = aud[deepest]
            vby = {}
            for x in sx:
                if x["test_seed"] == primary:
                    vby[str(primary)] = a_d.verdict
                    continue
                ax_ = audit_all_strata(S[x["calpool"]], C[x["calpool"]], cc[x["calpool"]], grid, x["bid_pool"], alpha, gamma)
                vby[str(int(x["test_seed"]))] = ax_[deepest].verdict if deepest in ax_ else None
            stats = _cascade_stats(S, C, cc, grid, mu, order, alpha, delta, sx, per_split,
                                   sp["cal_frac_of_pool"], d_weights)
            block[name] = {"deepest_stratum": int(deepest), "verdict": a_d.verdict,
                           "rmin_thr": a_d.rmin_thr, "rmin_depth": a_d.rmin_depth, "r_full": a_d.r_full,
                           "p_thr": a_d.p_thr, "p_depth": a_d.p_depth,
                           "all_verdicts": {str(k): v.verdict for k, v in aud.items()},
                           "deepest_verdict_by_split": vby,
                           "deepest_verdict_agreement": int(sum(v == a_d.verdict for v in vby.values())),
                           "cascade": stats}
        report["lambda_refs"][lr_key] = block
        b, c = block["before"], block["after"]
        print(f"[repair:{a.label}] lr[{lr_key}]={lr:.3f} deepest k={b['deepest_stratum']}: "
              f"{b['verdict']} (rmin {min(b['rmin_thr'], b['rmin_depth']):.3f}, full {b['r_full']:.3f}) -> "
              f"{c['verdict']} (rmin {min(c['rmin_thr'], c['rmin_depth']):.3f}, full {c['r_full']:.3f}); "
              f"tier1 {b['cascade']['tier_share']['1']:.2f} -> {c['cascade']['tier_share']['1']:.2f}; "
              f"viol {b['cascade']['violation_rate']:.2f} -> {c['cascade']['violation_rate']:.2f}; "
              f"certviol {b['cascade']['certified_violation_rate']:.2f} -> {c['cascade']['certified_violation_rate']:.2f}; "
              f"verdict agreement {b['deepest_verdict_agreement']}/{len(seeds)} -> {c['deepest_verdict_agreement']}/{len(seeds)}",
              flush=True)

    out = Path(a.output) if a.output else Path("results_v3") / "repair" / f"{a.dataset.replace(':', '-')}_ts{a.train_seed}_{a.label}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
