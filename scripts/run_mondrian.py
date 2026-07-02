#!/usr/bin/env python
"""Step 4 -- dataset-agnostic driver for the H2 comparison + per-budget validity.

Supersedes the MNIST-only ``scripts/run_mondrian_mnist.py`` (which is frozen and
left intact).  For each ``(dataset, policy, cost_scheme, seed)`` cell it:

  1. trains-or-loads the backbone and rolls out the policy -- **or reuses cached
     trajectories** (same cache-reuse contract as ``run_mondrian_mnist.py``); for
     MNIST it reuses the Step-3 caches so the H2 numbers cost no new training;
  2. computes, on the SAME trajectories: **CAFA-marginal** (``ltt_select``),
     **CAFA-Mondrian** (``mondrian_select`` over reference-depth buckets), every
     **heuristic baseline** (plugin, fixed_confidence x3, budget x sweep) and the
     **oracles** (cheapest-valid cost floor, full-acquisition risk floor);
  3. evaluates each method's **realized test** ``(risk, cost)``, the per-bucket
     marginal-vs-Mondrian risk, and the full-acquisition fallback on abstaining
     buckets (as in Step 3);
  4. writes one JSON per cell (extends the Step-3 schema) to
     ``${results_root}/metrics/step4_{dataset}_{policy}_{cost_scheme}_seed{k}.json``.

Usage::

    python scripts/run_mondrian.py --dataset mnist --policy greedy_entropy \
        --cost-scheme uniform --all-seeds --device cpu
    python scripts/run_mondrian.py --dataset tabular:adult --policy greedy_entropy \
        --cost-scheme inverse_info --all-seeds --device cpu
    python scripts/run_mondrian.py --cell 42        # slurm: decode -> a single cell
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
    oracle_full_feature_risk,
    plugin_threshold_select,
    realized_at_depth,
)
from cafa.metrics import (  # noqa: E402
    per_bucket_cost,
    per_bucket_risk,
    quantile_bucket_edges,
    realized_risk_cost,
    reference_buckets,
    stops_from_grid_np,
)
from cafa.risk_control import ltt_select, mondrian_select  # noqa: E402


def build_grid(method_cfg: dict) -> np.ndarray:
    g = method_cfg.get("grid", {"g_min": 0.0, "g_max": 1.0, "n": 100})
    return np.linspace(float(g["g_min"]), float(g["g_max"]), int(g["n"]))


def _sanitize(name: str) -> str:
    return name.replace(":", "-").replace("/", "-")


# --------------------------------------------------------------------------- #
# Trajectory production (cached) -- MNIST reuses Step-3 caches; tabular caches
# per (dataset, policy, cost_scheme, seed).
# --------------------------------------------------------------------------- #
def get_or_rollout_mnist(traj_dir, *, policy, seed, cfg, ckpt_path, device):
    """Reuse Step-3 MNIST trajectory cache if present, else roll out via torch."""
    traj_path = traj_dir / f"mnist_{policy}_seed{seed}.npz"
    if traj_path.exists():
        z = np.load(traj_path)
        return {k: z[k] for k in z.files}, np.ones(1)  # feature_costs unused (uniform)

    if not Path(ckpt_path).exists():
        raise FileNotFoundError(
            f"MNIST checkpoint not found at {ckpt_path} and no cached trajectory "
            f"at {traj_path}. Train the backbone or run Step-3 first."
        )
    import torch  # noqa: F401
    from cafa.acquisition import get_policy, rollout
    from cafa.data import load_mnist_afa
    from cafa.models import MaskedPredictor, N_CLASSES

    payload = torch.load(ckpt_path, map_location=device, weights_only=False)
    meta = payload.get("meta", {})
    model = MaskedPredictor(n_classes=int(meta.get("n_classes", N_CLASSES)))
    model.load_state_dict(payload["state_dict"]); model.to(device); model.eval()
    feature_costs = np.asarray(meta.get("feature_costs"), dtype=float)

    data = load_mnist_afa(cfg, seed=seed, download=False)
    pol = get_policy(policy, data["train"][0], seed=seed)
    score_name = cfg["method"].get("procedure_score", "softmax")
    cal = rollout(model, pol, score_name, *data["cal"], feature_costs, device=device)
    tst = rollout(model, pol, score_name, *data["test"], feature_costs, device=device)
    arrays = {
        "cal_scores": cal.scores, "cal_correct": cal.correct, "cal_cum_cost": cal.cum_cost,
        "test_scores": tst.scores, "test_correct": tst.correct, "test_cum_cost": tst.cum_cost,
    }
    traj_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(traj_path, **arrays)
    return arrays, feature_costs


def get_or_rollout_tabular(traj_dir, ckpt_dir, *, name, policy, cost_scheme, seed,
                           cfg, device):
    """Cache tabular trajectories per (name, policy, cost_scheme, seed)."""
    tag = f"tabular-{name}_{policy}_{cost_scheme}_seed{seed}"
    traj_path = traj_dir / f"{tag}.npz"
    if traj_path.exists():
        z = np.load(traj_path)
        return {k: z[k] for k in z.files}

    import torch  # noqa: F401
    from cafa.data import load_tabular_afa_cfg
    from cafa.models import TabularMaskedPredictor, train_tabular_predictor
    from cafa.tabular import get_tabular_policy, tabular_rollout

    data = load_tabular_afa_cfg(name, cfg, seed=seed, cost_scheme=cost_scheme, download=False)
    X_tr, y_tr = data["train"]
    fgroups = data["feature_groups"]
    score_name = cfg["method"].get("procedure_score", "softmax")

    # Backbone is policy/scheme-independent -> cache per (name, seed).
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = ckpt_dir / f"tabular-{name}_seed{seed}.pt"
    model = TabularMaskedPredictor(n_cols=data["n_cols"], n_classes=data["n_classes"])
    if ckpt_path.exists():
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
    else:
        tcfg = cfg.get("training_tabular", {})
        train_tabular_predictor(
            model, X_tr, y_tr, fgroups,
            epochs=int(tcfg.get("epochs", 40)),
            batch_size=int(tcfg.get("batch_size", 256)),
            lr=float(tcfg.get("lr", 1e-3)), device=device, seed=seed, log_every=0,
        )
        torch.save(model.state_dict(), ckpt_path)
    model.to(device); model.eval()

    pol = get_tabular_policy(policy, X_tr, seed=seed)
    fc = data["feature_costs"]
    cal = tabular_rollout(model, pol, score_name, *data["cal"], fc, fgroups, device=device)
    tst = tabular_rollout(model, pol, score_name, *data["test"], fc, fgroups, device=device)
    arrays = {
        "cal_scores": cal.scores, "cal_correct": cal.correct, "cal_cum_cost": cal.cum_cost,
        "test_scores": tst.scores, "test_correct": tst.correct, "test_cum_cost": tst.cum_cost,
    }
    traj_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(traj_path, **arrays)
    return arrays


# --------------------------------------------------------------------------- #
# Per-cell analysis (selection + evaluation on the SAME trajectories)
# --------------------------------------------------------------------------- #
def _jsonable(d):
    return {str(int(k)): (None if v is None or (isinstance(v, float) and np.isnan(v))
                          else float(v)) for k, v in d.items()}


def _mondrian_operating_point(test_losses, test_costs, test_correct, test_cum_cost,
                              test_bid, lambda_by_bucket, T):
    """Size-weighted realized (risk, cost) for Mondrian; abstain -> full acquisition."""
    labels, counts = np.unique(test_bid, return_counts=True)
    total = counts.sum()
    risk = 0.0
    cost = 0.0
    for k, c in zip(labels, counts):
        mask = test_bid == k
        idx = lambda_by_bucket.get(int(k))
        if idx is None:  # abstain -> acquire everything on this stratum
            r = float(np.mean(1.0 - test_correct[mask, T]))
            co = float(np.mean(test_cum_cost[mask, T]))
        else:
            r = float(test_losses[mask, int(idx)].mean())
            co = float(test_costs[mask, int(idx)].mean())
        risk += (c / total) * r
        cost += (c / total) * co
    return float(risk), float(cost)


def analyse_cell(arr, *, grid, method_cfg, mond_cfg, budget_k, fixed_t) -> dict:
    alpha = float(method_cfg["alpha"]); delta = float(method_cfg["delta"])
    procedure = method_cfg.get("procedure", "fixed_sequence")
    lam_ref = float(mond_cfg.get("lambda_ref", 0.5))
    n_buckets = int(mond_cfg.get("n_buckets", 5))
    min_per_bucket = int(mond_cfg.get("min_per_bucket", 50))

    cal_losses, cal_costs, _ = stops_from_grid_np(
        arr["cal_scores"], arr["cal_correct"], arr["cal_cum_cost"], grid)
    test_losses, test_costs, _ = stops_from_grid_np(
        arr["test_scores"], arr["test_correct"], arr["test_cum_cost"], grid)
    T = arr["test_correct"].shape[1] - 1

    # Buckets: quantile edges from CAL scores, reused on test.
    edges = quantile_bucket_edges(arr["cal_scores"], lam_ref, n_buckets)
    cal_bid, edges = reference_buckets(arr["cal_scores"], lam_ref, n_buckets,
                                       min_per_bucket, edges=edges)
    test_bid, _ = reference_buckets(arr["test_scores"], lam_ref, n_buckets,
                                    min_per_bucket, edges=edges)

    # --- selections (all on CALIBRATION except the oracles, which see TEST) ---
    marg = ltt_select(cal_losses, cal_costs, grid, alpha, delta, procedure=procedure)
    mond = mondrian_select(cal_losses, cal_costs, grid, alpha, delta, cal_bid,
                           procedure=procedure)
    plug_idx = plugin_threshold_select(cal_losses, cal_costs, grid, alpha)
    oracle_idx = oracle_cheapest_valid_select(test_losses, test_costs, grid, alpha)

    methods = {}

    # CAFA-marginal (certified).
    mr, mc = realized_risk_cost(test_losses, test_costs, marg.lambda_idx)
    methods["cafa_marginal"] = {"lambda_idx": (None if marg.lambda_idx is None else int(marg.lambda_idx)),
                                "realized_risk": mr, "realized_cost": mc, "guarantee": True}

    # CAFA-Mondrian (certified per bucket; size-weighted operating point).
    om_r, om_c = _mondrian_operating_point(test_losses, test_costs, arr["test_correct"],
                                           arr["test_cum_cost"], test_bid,
                                           mond.lambda_idx_by_bucket, T)
    methods["cafa_mondrian"] = {"realized_risk": om_r, "realized_cost": om_c,
                                "guarantee": True, "joint": bool(mond.joint)}

    # Plugin (no correction) -- the main foil.
    pr, pc = realized_risk_cost(test_losses, test_costs, plug_idx)
    methods["plugin_threshold"] = {"lambda_idx": (None if plug_idx is None else int(plug_idx)),
                                   "realized_risk": pr, "realized_cost": pc, "guarantee": False}

    # Fixed-confidence heuristics.
    for t in fixed_t:
        fi = fixed_confidence_select(grid, float(t))
        fr, fc = realized_risk_cost(test_losses, test_costs, fi)
        methods[f"fixed_conf_{t}"] = {"lambda_idx": int(fi), "t": float(t),
                                      "realized_risk": fr, "realized_cost": fc,
                                      "guarantee": False}

    # Fixed-budget heuristics (evaluated at depth from trajectories).
    for k in budget_k:
        kk = budget_select(int(k), T=T)
        br, bc = realized_at_depth(arr["test_correct"], arr["test_cum_cost"], kk)
        methods[f"budget_{k}"] = {"depth": int(kk), "realized_risk": br,
                                  "realized_cost": bc, "guarantee": False}

    # Oracles (TEST labels; NON-deployable reference bounds).
    orr, orc = realized_risk_cost(test_losses, test_costs, oracle_idx)
    methods["oracle_cheapest_valid"] = {"lambda_idx": (None if oracle_idx is None else int(oracle_idx)),
                                        "realized_risk": orr, "realized_cost": orc,
                                        "deployable": False}
    full_loss = 1.0 - arr["test_correct"][:, T]
    methods["oracle_full_feature"] = {"realized_risk": float(oracle_full_feature_risk(full_loss)),
                                      "realized_cost": float(arr["test_cum_cost"][:, T].mean()),
                                      "deployable": False}

    # --- per-bucket marginal vs Mondrian + full-acq fallback (Step-3 style) ---
    labels = np.unique(test_bid)
    marg_map = {int(k): marg.lambda_idx for k in labels}
    marg_risk = per_bucket_risk(test_losses, test_bid, marg_map)
    marg_cost = per_bucket_cost(test_costs, test_bid, marg_map)
    mond_risk = per_bucket_risk(test_losses, test_bid, mond.lambda_idx_by_bucket)
    mond_cost = per_bucket_cost(test_costs, test_bid, mond.lambda_idx_by_bucket)

    full_acq_loss = 1.0 - arr["test_correct"][:, T]
    fallback = {}
    for k in labels:
        if mond.lambda_idx_by_bucket.get(int(k)) is None:
            mask = test_bid == k
            fallback[int(k)] = float(full_acq_loss[mask].mean()) if mask.any() else None

    return {
        "alpha": alpha, "delta": delta, "procedure": procedure,
        "lambda_ref": lam_ref, "n_buckets": n_buckets, "T": int(T),
        "bucket_edges": [float(e) for e in np.asarray(edges).tolist()],
        "bucket_sizes_test": {str(int(k)): int((test_bid == k).sum()) for k in labels},
        "methods": {m: {kk: (None if (isinstance(vv, float) and np.isnan(vv)) else vv)
                        for kk, vv in d.items()} for m, d in methods.items()},
        "per_bucket": {
            "marginal_risk": _jsonable(marg_risk), "marginal_cost": _jsonable(marg_cost),
            "mondrian_risk": _jsonable(mond_risk), "mondrian_cost": _jsonable(mond_cost),
            "mondrian_lambda_idx": {str(int(k)): (None if v is None else int(v))
                                    for k, v in mond.lambda_idx_by_bucket.items()},
        },
        "fallback_full_acq_risk_by_bucket": _jsonable(fallback),
    }


# --------------------------------------------------------------------------- #
# Cell enumeration for --cell (path-free slurm decode)
# --------------------------------------------------------------------------- #
def _dataset_alpha(cfg, dataset):
    """Feasible-target alpha for a dataset, honouring the per-dataset override.

    Step 5 records a fixed-rule alpha (ceil-to-0.05 of floor+0.05) per tabular
    dataset in ``datasets_tabular``.  Return that value for a ``tabular:<name>``
    dataset when set; otherwise (and for ``mnist``) fall back to the global
    ``method.alpha``.  Used only by the ``--cell`` slurm path, which has no
    ``--alpha`` flag to carry the per-dataset target.
    """
    default = float(cfg["method"]["alpha"])
    if isinstance(dataset, str) and dataset.startswith("tabular:"):
        name = dataset.split(":", 1)[1]
        for d in cfg.get("datasets_tabular", []):
            if d.get("name") == name and d.get("alpha") is not None:
                return float(d["alpha"])
    return default


def _lambda_ref_grid(cfg):
    """lambda_ref values to sweep for the --cell path.

    Prefer the Step-5 ``lambda_ref_sweep`` list; if absent, fall back to the
    single configured ``method.mondrian.lambda_ref`` so the enumeration is
    identical for pre-Step-5 configs (one lambda_ref per cell).
    """
    sweep = cfg.get("lambda_ref_sweep")
    if not sweep:
        sweep = [cfg.get("method", {}).get("mondrian", {}).get("lambda_ref", 0.5)]
    return [float(x) for x in sweep]


def build_cells(cfg):
    datasets = ["mnist"] + [f"tabular:{d['name']}" for d in cfg.get("datasets_tabular", [])]
    policies = ["greedy_entropy", "random"]
    schemes = list(cfg.get("cost_schemes", ["inverse_info", "random", "uniform"]))
    seeds = list(cfg["protocol"]["seeds"])
    lambda_refs = _lambda_ref_grid(cfg)
    cells = []
    for ds in datasets:
        for pol in policies:
            for cs in schemes:
                if ds == "mnist" and cs != "uniform":
                    continue  # MNIST costs are uniform; only that scheme is meaningful
                for lr in lambda_refs:
                    for s in seeds:
                        cells.append((ds, pol, cs, s, lr))
    return cells


def run_one(dataset, policy, cost_scheme, seed, *, cfg, paths, device):
    method_cfg = cfg["method"]
    mond_cfg = method_cfg.get("mondrian", {})
    grid = build_grid(method_cfg)
    budget_k = list(cfg.get("budget_k", [5, 10, 20]))
    fixed_t = list(cfg.get("fixed_confidence_t", [0.90, 0.95, 0.99]))

    traj_dir = Path(paths.results_root) / "trajectories"
    ckpt_dir = Path(paths.results_root) / "checkpoints"

    if dataset == "mnist":
        if cost_scheme != "uniform":
            print(f"[skip] MNIST only supports cost_scheme=uniform (got {cost_scheme}).")
            return None
        ckpt = ckpt_dir / f"mnist_{policy}.pt"
        arr, _ = get_or_rollout_mnist(traj_dir, policy=policy, seed=seed, cfg=cfg,
                                      ckpt_path=ckpt, device=device)
        name = "mnist"
    elif dataset.startswith("tabular:"):
        name = dataset.split(":", 1)[1]
        arr = get_or_rollout_tabular(traj_dir, ckpt_dir, name=name, policy=policy,
                                     cost_scheme=cost_scheme, seed=seed, cfg=cfg,
                                     device=device)
    else:
        raise ValueError(f"unknown dataset {dataset!r}; expected 'mnist' or 'tabular:<name>'.")

    rec = analyse_cell(arr, grid=grid, method_cfg=method_cfg, mond_cfg=mond_cfg,
                       budget_k=budget_k, fixed_t=fixed_t)
    rec.update({"dataset": dataset, "policy": policy, "cost_scheme": cost_scheme,
                "seed": int(seed)})

    metrics_dir = Path(paths.results_root) / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    # Step 5: the lambda_ref robustness sweep runs the SAME (dataset,policy,scheme,
    # seed) cell at several lambda_ref values (only the bucketing / Mondrian view
    # changes).  Tag the filename with lambda_ref so those runs coexist instead of
    # overwriting one another; the aggregator groups by the lambda_ref recorded
    # inside each JSON.
    lam_ref = float(cfg.get("method", {}).get("mondrian", {}).get("lambda_ref", 0.5))
    fname = f"step4_{_sanitize(dataset)}_{policy}_{cost_scheme}_lr{lam_ref:g}_seed{seed}.json"
    (metrics_dir / fname).write_text(json.dumps(rec, indent=2))
    cm = rec["methods"]["cafa_marginal"]; pl = rec["methods"]["plugin_threshold"]
    print(f"[{fname}] CAFA-marg risk={cm['realized_risk']} cost={cm['realized_cost']} | "
          f"plugin risk={pl['realized_risk']} cost={pl['realized_cost']}")
    return rec


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="CAFA Step 4 dataset-agnostic driver.")
    p.add_argument("--dataset", default="mnist",
                   help="mnist | tabular:<name> (e.g. tabular:adult)")
    p.add_argument("--policy", default="greedy_entropy",
                   choices=["greedy_entropy", "random"])
    p.add_argument("--cost-scheme", default="uniform",
                   choices=["inverse_info", "random", "uniform"])
    g = p.add_mutually_exclusive_group()
    g.add_argument("--seed-index", type=int, default=None)
    g.add_argument("--all-seeds", action="store_true")
    g.add_argument("--cell", type=int, default=None,
                   help="Slurm array index -> (dataset, policy, cost_scheme, seed, lambda_ref).")
    p.add_argument("--device", default="cpu")
    # Optional overrides of configs/experiment.yaml (recorded into each JSON, so
    # the aggregator reports each cell against the alpha it actually ran with).
    p.add_argument("--alpha", type=float, default=None,
                   help="override method.alpha (risk target).")
    p.add_argument("--delta", type=float, default=None,
                   help="override method.delta (failure prob).")
    p.add_argument("--lambda-ref", type=float, default=None,
                   help="override method.mondrian.lambda_ref (bucketing readiness).")
    p.add_argument("--n-buckets", type=int, default=None,
                   help="override method.mondrian.n_buckets.")
    return p.parse_args(argv)


def _apply_overrides(cfg, args):
    """Patch alpha/delta/lambda_ref/n_buckets in-place from CLI, if provided."""
    m = cfg.setdefault("method", {})
    mond = m.setdefault("mondrian", {})
    changed = {}
    if args.alpha is not None:
        m["alpha"] = float(args.alpha); changed["alpha"] = m["alpha"]
    if args.delta is not None:
        m["delta"] = float(args.delta); changed["delta"] = m["delta"]
    if args.lambda_ref is not None:
        mond["lambda_ref"] = float(args.lambda_ref); changed["lambda_ref"] = mond["lambda_ref"]
    if args.n_buckets is not None:
        mond["n_buckets"] = int(args.n_buckets); changed["n_buckets"] = mond["n_buckets"]
    if changed:
        print(f"[override] {changed}")
    return cfg


def main(argv=None) -> int:
    args = parse_args(argv)
    cfg = config.load_experiment()
    cfg = _apply_overrides(cfg, args)
    paths = config.load_paths()
    seeds = list(cfg["protocol"]["seeds"])

    if args.cell is not None:
        cells = build_cells(cfg)
        if not (0 <= args.cell < len(cells)):
            print(f"ERROR: --cell {args.cell} out of range [0, {len(cells)}).", file=sys.stderr)
            return 1
        ds, pol, cs, seed, lr = cells[args.cell]
        # The array path uses config, not CLI overrides (STEP4_HANDOFF §6): stamp
        # this cell's lambda_ref and the dataset's fixed-rule alpha into cfg unless
        # the caller already set them on the command line (CLI wins, applied above
        # by _apply_overrides).
        if args.lambda_ref is None:
            cfg["method"]["mondrian"]["lambda_ref"] = lr
        if args.alpha is None:
            cfg["method"]["alpha"] = _dataset_alpha(cfg, ds)
        print(f"cell {args.cell}/{len(cells)} -> dataset={ds} policy={pol} "
              f"cost_scheme={cs} seed={seed} "
              f"lambda_ref={cfg['method']['mondrian']['lambda_ref']:g} "
              f"alpha={cfg['method']['alpha']:g}")
        run_one(ds, pol, cs, seed, cfg=cfg, paths=paths, device=args.device)
        return 0

    if args.all_seeds:
        run_seeds = seeds
    elif args.seed_index is not None:
        run_seeds = [seeds[args.seed_index]]
    else:
        run_seeds = [seeds[0]]

    for seed in run_seeds:
        run_one(args.dataset, args.policy, args.cost_scheme, seed,
                cfg=cfg, paths=paths, device=args.device)
    print(f"\nDone. Metrics in {Path(paths.results_root) / 'metrics'}. "
          "Run scripts/aggregate_results.py for the H2 table + framing-fork readout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())