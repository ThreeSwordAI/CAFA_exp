#!/usr/bin/env python
"""WO-10 -- eval sweep: the resplit engine (torch-free, CPU, fast).

For a (dataset, policy) pool cache and the ts=0 committed probe JSON, slices the
eval rows, computes the stop-index matrix once (risk is scheme-invariant), then
over ``n_resplits`` cal/test resplits and each lambda_ref evaluates:

  * cafa_marginal  -- frozen ltt_select on cal (per cost scheme);
  * cafa_iut       -- WO-5 iut_select on cal with the committed quantile-5 edges;
  * mondrian_audit -- frozen mondrian_select joint=False AND joint=True on cal,
                      per-stratum lambda / abstentions / realized TEST risk only
                      (NO cost operating point -- D5);
  * baselines      -- plugin, fixed_conf x3, budget x3; oracles cheapest-valid
                      (test) and full-feature (per scheme for costs).

Abstentions (lambda_idx is None) are recorded with fallback full-acquisition
realized numbers, flagged, and NEVER dropped.

Usage
-----
    python scripts/run_eval_sweep.py --dataset tabular:adult --policy greedy_entropy --train-seed 0
    python scripts/run_eval_sweep.py --cell K      # Phase-1 dataset x policy cells (0-7)

Output: ``metrics_v2/{dsname}_ts{ts}_{policy_token}.json``.
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
    realized_at_depth,
)
from cafa.metrics import per_bucket_risk, reference_buckets, reference_depth  # noqa: E402
from cafa.pool import cum_cost_from_order, load_pool_cache  # noqa: E402
from cafa.policies_v2 import eps_greedy_policy_token  # noqa: E402
from cafa.risk_control import ltt_select, mondrian_select  # noqa: E402
from cafa.risk_control_ext import iut_select  # noqa: E402
from cafa.splits import probe_eval_split, resplit_cal_test  # noqa: E402

_TAB = ["tabular:adult", "tabular:MiniBooNE", "tabular:spambase"]


def dsname_of(dataset: str) -> str:
    if dataset.startswith("tabular:"):
        return "tabular-" + dataset.split(":", 1)[1]
    return dataset


def build_grid(method_cfg: dict) -> np.ndarray:
    g = method_cfg.get("grid", {"g_min": 0.0, "g_max": 1.0, "n": 100})
    return np.linspace(float(g["g_min"]), float(g["g_max"]), int(g["n"]))


def stop_index_matrix(scores: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """First-crossing stop index ``s[n, G]`` (== T if the score never crosses)."""
    scores = np.asarray(scores, dtype=float)
    grid = np.asarray(grid, dtype=float)
    n, Tp1 = scores.shape
    T = Tp1 - 1
    crossed = scores[:, :, None] >= grid[None, None, :]
    any_cross = crossed.any(axis=1)
    first = crossed.argmax(axis=1)
    return np.where(any_cross, first, T).astype(int)


def cp_bounds(k: int, n: int) -> "tuple[float, float]":
    from scipy.stats import beta
    k = int(k); n = int(n)
    if n == 0:
        return 0.0, 1.0
    lcb = 0.0 if k == 0 else float(beta.ppf(0.05, k, n - k + 1))
    ucb = 1.0 if k == n else float(beta.ppf(0.95, k + 1, n - k))
    return lcb, ucb


def verdict_of(lcb: float, ucb: float, alpha: float) -> str:
    if lcb > alpha:
        return "infeasible"
    if ucb < alpha:
        return "feasible"
    return "undetermined"


def norm_entropy(depth: np.ndarray) -> float:
    """Normalized entropy H(p)/log(#support) of the empirical depth distribution."""
    depth = np.asarray(depth)
    vals, counts = np.unique(depth, return_counts=True)
    if vals.size <= 1:
        return 0.0
    p = counts / counts.sum()
    H = -np.sum(p * np.log(p))
    return float(H / np.log(vals.size))


def r6(x):
    if x is None:
        return None
    if isinstance(x, float) and np.isnan(x):
        return None
    return round(float(x), 6)


def build_cells():
    cells = []
    for ds in ["mnist"] + _TAB:
        for pol in ["greedy_entropy", "random"]:
            cells.append({"dataset": ds, "policy_token": pol, "score": None})
    return cells


def _fallback_full(full_acq_loss_test, cc_scheme_test_rows, T):
    """Realized (risk, cost) at full acquisition for an abstaining method."""
    return float(full_acq_loss_test.mean()), float(cc_scheme_test_rows[:, T].mean())


def run_one(dataset, policy_token, score, train_seed, *, cfg, paths):
    ts = int(train_seed)
    dsname = dsname_of(dataset)
    method_cfg = cfg["method"]
    grid = build_grid(method_cfg)
    G = grid.shape[0]
    delta = float(method_cfg.get("delta", 0.10))
    procedure = method_cfg.get("procedure", "fixed_sequence")
    score_name = score or method_cfg.get("procedure_score", "softmax")

    pv = cfg.get("protocol_v2", {})
    probe_frac = float(pv.get("probe_frac", 0.10))
    probe_seed = int(pv.get("probe_seed", 777))
    n_resplits = int(pv.get("n_resplits", 100))
    cal_frac = float(pv.get("cal_frac_of_eval", 0.5))
    lambda_refs = list(cfg.get("mondrian_v2", {}).get("lambda_refs", [0.5, 0.7, 0.9]))
    min_per_bucket = int(cfg.get("mondrian_v2", {}).get("n_buckets_primary", 5))  # unused w/ edges
    fixed_t = list(cfg.get("fixed_confidence_t", [0.90, 0.95, 0.99]))
    budget_k = list(cfg.get("budget_k", [5, 10, 20]))

    committed_path = Path("configs") / f"committed_v2_{dsname}_ts{ts}.json"
    if not committed_path.exists():
        raise FileNotFoundError(f"committed probe JSON not found at {committed_path}.")
    committed = json.loads(committed_path.read_text())
    alpha = float(committed["alpha"])
    feature_costs_by_scheme = {
        s: np.asarray(v, dtype=float) for s, v in committed["feature_costs_by_scheme"].items()
    }
    schemes = list(feature_costs_by_scheme.keys())
    edges_for_policy = committed["edges"].get(policy_token, {})

    cache_path = Path(paths.results_root) / "pool_v2" / f"{dsname}_ts{ts}_{policy_token}_{score_name}.npz"
    if not cache_path.exists():
        raise FileNotFoundError(f"pool cache not found at {cache_path}.")
    cache = load_pool_cache(cache_path)

    # Eval rows (probe positions recomputed from n + config; eval = the rest).
    n_pool = cache["scores"].shape[0]
    _, eval_pos = probe_eval_split(np.arange(n_pool), probe_frac, probe_seed)
    eval_scores = np.asarray(cache["scores"])[eval_pos]
    eval_correct = np.asarray(cache["correct"])[eval_pos]
    eval_order = np.asarray(cache["order"])[eval_pos]
    n_eval, Tp1 = eval_scores.shape
    T = Tp1 - 1

    # Stop-index matrix + scheme-invariant losses (computed once).
    s_full = stop_index_matrix(eval_scores, grid)                     # [n_eval, G]
    rows = np.arange(n_eval)[:, None]
    losses_full = 1.0 - eval_correct[rows, s_full]                    # [n_eval, G]
    # Per-scheme cumulative cost trajectories, then cost matrices at the stops.
    cc_by_scheme = {
        s: cum_cost_from_order(eval_order, feature_costs_by_scheme[s]) for s in schemes
    }
    costs_full = {s: cc_by_scheme[s][rows, s_full] for s in schemes}  # [n_eval, G]
    full_acq_loss = 1.0 - eval_correct[:, T]

    out = {
        "meta": {
            "dataset": dataset, "policy": policy_token, "score": score_name,
            "train_seed": ts, "dsname": dsname, "schemes": schemes,
            "n_eval": int(n_eval), "T": int(T), "n_resplits": n_resplits,
            "cache_meta": cache["meta"], "committed_floor": committed.get("floor"),
        },
        "alpha": alpha, "delta": delta, "grid": [float(g) for g in grid.tolist()],
        "lambda_refs": {},
    }

    for lr in lambda_refs:
        lr_key = str(float(lr))
        q5 = edges_for_policy.get(lr_key, {}).get("quantile", {}).get("5", [])
        edges = np.asarray(q5, dtype=float)
        bucket_full, _ = reference_buckets(eval_scores, float(lr), 5, min_per_bucket, edges=edges)
        depth = reference_depth(eval_scores, float(lr))

        # ---- population block (full eval pool) ----
        per_stratum_full = {}
        for k in np.unique(bucket_full):
            mask = bucket_full == k
            n_k = int(mask.sum())
            err = int(round(float(np.sum(full_acq_loss[mask]))))
            r_full = float(full_acq_loss[mask].mean()) if n_k else float("nan")
            lcb, ucb = cp_bounds(err, n_k)
            per_stratum_full[str(int(k))] = {
                "n": n_k, "risk": r6(r_full), "cp_lcb95": r6(lcb), "cp_ucb95": r6(ucb),
                "verdict": verdict_of(lcb, ucb, alpha),
            }
        floor_err = int(round(float(np.sum(full_acq_loss))))
        f_lcb, f_ucb = cp_bounds(floor_err, n_eval)
        iqr = float(np.subtract(*np.percentile(depth, [75, 25])))
        population = {
            "eval_n": int(n_eval),
            "floor": {"estimate": r6(float(full_acq_loss.mean())),
                      "cp_lcb95": r6(f_lcb), "cp_ucb95": r6(f_ucb)},
            "per_stratum_full": per_stratum_full,
            "depth_concentration": {"iqr": r6(iqr), "norm_entropy": r6(norm_entropy(depth))},
            "bucket_sizes": {str(int(k)): int((bucket_full == k).sum())
                             for k in np.unique(bucket_full)},
        }

        # ---- resplits ----
        resplits = []
        marg_viol = 0
        iut_abstain = 0
        for rs in range(n_resplits):
            cal_local, test_local = resplit_cal_test(np.arange(n_eval), rs, cal_frac)
            cal_bid = bucket_full[cal_local]
            test_bid = bucket_full[test_local]
            losses_cal = losses_full[cal_local]
            losses_test = losses_full[test_local]
            full_acq_test = full_acq_loss[test_local]

            rec = {"seed": int(rs), "schemes": {}}

            # IUT + marginal lambda are scheme-invariant under fixed_sequence; select
            # per scheme anyway (cheap) so per-scheme cost is exact and well-defined.
            iut_idx_ref = None
            marg_idx_ref = None
            for scheme in schemes:
                costs_cal = costs_full[scheme][cal_local]
                costs_test = costs_full[scheme][test_local]
                cc_test = cc_by_scheme[scheme][test_local]

                m = {}

                # cafa_marginal
                sel = ltt_select(losses_cal, costs_cal, grid, alpha, delta, procedure=procedure)
                cert = int(sel.valid_mask.sum())
                if sel.lambda_idx is None:
                    risk, cost = _fallback_full(full_acq_test, cc_test, T)
                    m["cafa_marginal"] = {"lambda_idx": None, "abstained": True,
                                          "certified_size": cert, "realized_risk": r6(risk),
                                          "realized_cost": r6(cost)}
                else:
                    idx = int(sel.lambda_idx)
                    m["cafa_marginal"] = {"lambda_idx": idx, "abstained": False,
                                          "certified_size": cert,
                                          "realized_risk": r6(float(losses_test[:, idx].mean())),
                                          "realized_cost": r6(float(costs_test[:, idx].mean()))}
                marg_idx_ref = sel.lambda_idx

                # cafa_iut
                iut = iut_select(losses_cal, costs_cal, grid, alpha, delta, cal_bid,
                                 procedure=procedure)
                if iut.lambda_idx is None:
                    risk, cost = _fallback_full(full_acq_test, cc_test, T)
                    m["cafa_iut"] = {"lambda_idx": None, "abstained": True,
                                     "realized_risk": r6(risk), "realized_cost": r6(cost)}
                else:
                    idx = int(iut.lambda_idx)
                    m["cafa_iut"] = {"lambda_idx": idx, "abstained": False,
                                     "realized_risk": r6(float(losses_test[:, idx].mean())),
                                     "realized_cost": r6(float(costs_test[:, idx].mean()))}
                iut_idx_ref = iut.lambda_idx

                # plugin (no correction)
                plug = plugin_threshold_select(losses_cal, costs_cal, grid, alpha)
                if plug is None:
                    risk, cost = _fallback_full(full_acq_test, cc_test, T)
                    m["plugin"] = {"lambda_idx": None, "abstained": True,
                                   "realized_risk": r6(risk), "realized_cost": r6(cost)}
                else:
                    m["plugin"] = {"lambda_idx": int(plug), "abstained": False,
                                   "realized_risk": r6(float(losses_test[:, plug].mean())),
                                   "realized_cost": r6(float(costs_test[:, plug].mean()))}

                # fixed_confidence x3
                for t in fixed_t:
                    fi = fixed_confidence_select(grid, float(t))
                    m[f"fixed_conf_{t}"] = {"lambda_idx": int(fi),
                                            "realized_risk": r6(float(losses_test[:, fi].mean())),
                                            "realized_cost": r6(float(costs_test[:, fi].mean()))}

                # budget x3 (from trajectories at a fixed depth)
                for kk in budget_k:
                    d = budget_select(int(kk), T=T)
                    br = float(np.mean(1.0 - eval_correct[test_local, d]))
                    bc = float(cc_test[:, d].mean())
                    m[f"budget_{kk}"] = {"depth": int(d), "realized_risk": r6(br),
                                         "realized_cost": r6(bc)}

                # oracles (TEST labels; non-deployable)
                oc = oracle_cheapest_valid_select(losses_test, costs_test, grid, alpha)
                if oc is None:
                    m["oracle_cheapest"] = {"lambda_idx": None, "realized_risk": None,
                                            "realized_cost": None}
                else:
                    m["oracle_cheapest"] = {"lambda_idx": int(oc),
                                            "realized_risk": r6(float(losses_test[:, oc].mean())),
                                            "realized_cost": r6(float(costs_test[:, oc].mean()))}
                m["oracle_full"] = {"realized_risk": r6(float(full_acq_loss[test_local].mean())),
                                    "realized_cost": r6(float(cc_test[:, T].mean()))}

                rec["schemes"][scheme] = m

            # ---- scheme-invariant records (risk only) ----
            # marginal per-stratum realized test risk at the marginal lambda.
            marg_map = {int(k): (None if marg_idx_ref is None else int(marg_idx_ref))
                        for k in np.unique(test_bid)}
            rec["marginal_per_stratum_risk"] = {
                str(int(k)): r6(v) for k, v in per_bucket_risk(losses_test, test_bid, marg_map).items()
            }
            # IUT per-stratum realized test risk at the single deployed lambda.
            if iut_idx_ref is None:
                iut_ps = {int(k): float(full_acq_loss[test_local][test_bid == k].mean())
                          if (test_bid == k).any() else float("nan")
                          for k in np.unique(test_bid)}
            else:
                iut_map = {int(k): int(iut_idx_ref) for k in np.unique(test_bid)}
                iut_ps = per_bucket_risk(losses_test, test_bid, iut_map)
            rec["iut_per_stratum_risk"] = {str(int(k)): r6(v) for k, v in iut_ps.items()}
            rec["iut_abstained"] = bool(iut_idx_ref is None)

            # mondrian audit (joint False AND True); NO cost operating point (D5).
            costs_cal_u = costs_full[schemes[0]][cal_local]  # any scheme; cost unused for audit
            mond_audit = {}
            for jkey, jflag in (("joint_false", False), ("joint_true", True)):
                mond = mondrian_select(losses_cal, costs_cal_u, grid, alpha, delta, cal_bid,
                                       procedure=procedure, joint=jflag)
                ps_risk = per_bucket_risk(losses_test, test_bid, mond.lambda_idx_by_bucket)
                mond_audit[jkey] = {
                    "lambda_idx_by_bucket": {str(int(k)): (None if v is None else int(v))
                                             for k, v in mond.lambda_idx_by_bucket.items()},
                    "per_stratum_test_risk": {str(int(k)): r6(v) for k, v in ps_risk.items()},
                }
            rec["mondrian_audit"] = mond_audit

            # summary counters (scheme-invariant risk; use first scheme's marginal record).
            mm = rec["schemes"][schemes[0]]["cafa_marginal"]
            if mm["realized_risk"] is not None and mm["realized_risk"] > alpha:
                marg_viol += 1
            if rec["iut_abstained"]:
                iut_abstain += 1

            resplits.append(rec)

        n_infeasible = sum(1 for v in per_stratum_full.values() if v["verdict"] == "infeasible")
        print(f"[eval] {dataset} {policy_token} lr={lr}: marginal_viol={marg_viol}/{n_resplits} "
              f"iut_abstain={iut_abstain}/{n_resplits} infeasible_strata={n_infeasible}", flush=True)

        out["lambda_refs"][lr_key] = {"population": population, "resplits": resplits}

    metrics_dir = Path("metrics_v2")
    metrics_dir.mkdir(parents=True, exist_ok=True)
    out_path = metrics_dir / f"{dsname}_ts{ts}_{policy_token}.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"[eval] wrote {out_path}", flush=True)
    return out_path


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="CAFA v2 eval sweep (resplit engine).")
    p.add_argument("--dataset", default=None, help="mnist | tabular:<name>")
    p.add_argument("--policy", default="greedy_entropy",
                   choices=["greedy_entropy", "random", "eps_greedy"])
    p.add_argument("--epsilon", type=float, default=None)
    p.add_argument("--score", default=None)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--cell", type=int, default=None, help="Phase-1 dataset x policy cell (0-7).")
    return p.parse_args(argv)


def _policy_token(policy, epsilon):
    if policy == "eps_greedy":
        return eps_greedy_policy_token(epsilon)
    return policy


def main(argv=None) -> int:
    args = parse_args(argv)
    cfg = config.load_experiment()
    paths = config.load_paths()

    if args.cell is not None:
        cells = build_cells()
        if not (0 <= args.cell < len(cells)):
            print(f"ERROR: --cell {args.cell} out of range [0, {len(cells)}).", file=sys.stderr)
            return 1
        c = cells[args.cell]
        print(f"cell {args.cell}/{len(cells)} -> dataset={c['dataset']} policy={c['policy_token']}",
              flush=True)
        run_one(c["dataset"], c["policy_token"], c["score"], args.train_seed, cfg=cfg, paths=paths)
        return 0

    if args.dataset is None:
        print("ERROR: provide --dataset or --cell.", file=sys.stderr)
        return 1
    if args.policy == "eps_greedy" and args.epsilon is None:
        print("ERROR: --policy eps_greedy requires --epsilon.", file=sys.stderr)
        return 1
    run_one(args.dataset, _policy_token(args.policy, args.epsilon), args.score,
            args.train_seed, cfg=cfg, paths=paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
