#!/usr/bin/env python
"""WO-8 -- pool rollout runner (records the acquisition ``order``).

Rolls out the **entire heldout split** (probe + eval rows together, in heldout
order) once per (dataset, train_seed, policy[, epsilon][, score]) and writes a
:mod:`cafa.pool` cache.  Cumulative costs are NOT stored: because neither greedy
nor random consults feature costs, ``order`` is the artifact and cum_cost is
recomputed post-hoc per cost scheme (see :func:`cafa.pool.cum_cost_from_order`).

Usage
-----
    python scripts/run_pool_rollout.py --dataset mnist --policy greedy_entropy --train-seed 0 --device cuda
    python scripts/run_pool_rollout.py --dataset tabular:MiniBooNE --policy random --train-seed 0 --device cpu
    python scripts/run_pool_rollout.py --dataset tabular:adult --policy eps_greedy --epsilon 0.25 --train-seed 0
    python scripts/run_pool_rollout.py --cell K            # slurm array decode over the cell list

Cell list (fixed order; documented for the slurm arrays and Sec. F):
    Phase-1 cells 0-7   : [mnist, adult, MiniBooNE, spambase] x [greedy_entropy, random]
    Phase-2 cells 8-15  : [adult, MiniBooNE, spambase, mnist] x eps in {0.25, 0.5}
    Phase-4 cell  16    : (tabular:spambase, greedy_entropy, score=margin)  [optional]
    Phase-4 cells 17-19 : [adult, MiniBooNE, mnist] x (greedy_entropy, score=margin)
                          -- the corrected score-ablation scope: run where the
                          audit DETECTS (spambase is undetermined; cell 16 optional)

Cache path:
    ${RESULTS_ROOT}/pool_v2/{dsname}_ts{ts}_{policy_token}_{score}.npz
where policy_token is e.g. ``greedy_entropy`` / ``random`` / ``eps_greedy_eps0.25``.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa import pool as poolmod  # noqa: E402
from cafa.data import load_mnist_pool, load_tabular_pool  # noqa: E402
from cafa.policies_v2 import EpsGreedyMixture, eps_greedy_policy_token  # noqa: E402
from cafa.repro_utils import file_sha256  # noqa: E402
from cafa.scores import get_score_fn  # noqa: E402
from cafa.tabular import _as_feature_groups, expand_feature_mask  # noqa: E402

_TAB = ["tabular:adult", "tabular:MiniBooNE", "tabular:spambase"]


def dsname_of(dataset: str) -> str:
    if dataset.startswith("tabular:"):
        return "tabular-" + dataset.split(":", 1)[1]
    return dataset


# --------------------------------------------------------------------------- #
# Rollout loops (mirror the frozen loops; add `order` recording; keep in sync)
# --------------------------------------------------------------------------- #
def rollout_mnist_with_order(model, policy, score_fn, X, y, device, batch_size=256):
    """mirrors cafa.acquisition.rollout + order recording; keep in sync.

    Costs are all-ones for MNIST and cum_cost is discarded here (order is the
    artifact); scores/correct/order are recorded per step.
    """
    if isinstance(score_fn, str):
        score_fn = get_score_fn(score_fn)
    device = torch.device(device)
    X_np = np.asarray(X, dtype=np.float32)
    y_np = np.asarray(y).astype(np.int64)
    N, P, _ = X_np.shape
    T = P
    scores = np.zeros((N, T + 1), dtype=float)
    correct = np.zeros((N, T + 1), dtype=float)
    order = np.zeros((N, T), dtype=np.int64)

    for start in range(0, N, batch_size):
        stop = min(start + batch_size, N)
        Xb = torch.as_tensor(X_np[start:stop], device=device)
        B = Xb.shape[0]
        observed = torch.zeros((B, P), dtype=torch.float32, device=device)
        for t in range(T + 1):
            probs = model.predict_proba(Xb, observed, device=device)
            scores[start:stop, t] = np.asarray(score_fn(probs), dtype=float)
            correct[start:stop, t] = (probs.argmax(axis=1) == y_np[start:stop]).astype(float)
            if t == T:
                break
            nxt = policy.select_next(model, Xb, observed, device)
            order[start:stop, t] = np.asarray(nxt.detach().cpu().numpy(), dtype=np.int64)
            observed = observed.clone()
            observed[torch.arange(B, device=device), nxt] = 1.0
    return scores, correct, order


def rollout_tabular_with_order(model, policy, score_fn, X, y, feature_groups, device, batch_size=256):
    """mirrors cafa.tabular.tabular_rollout + order recording; keep in sync."""
    if isinstance(score_fn, str):
        score_fn = get_score_fn(score_fn)
    X_np = np.asarray(X, dtype=np.float32)
    y_np = np.asarray(y).astype(np.int64)
    N, n_cols = X_np.shape
    groups = _as_feature_groups(feature_groups, n_cols)
    d = len(groups)
    T = d
    scores = np.zeros((N, T + 1), dtype=float)
    correct = np.zeros((N, T + 1), dtype=float)
    order = np.zeros((N, T), dtype=np.int64)

    for start in range(0, N, batch_size):
        stop = min(start + batch_size, N)
        Xb = X_np[start:stop]
        yb = y_np[start:stop]
        B = Xb.shape[0]
        observed = np.zeros((B, d), dtype=np.float32)
        for t in range(T + 1):
            col_mask = expand_feature_mask(observed, groups)
            probs = np.asarray(model.predict_proba(Xb, col_mask, device=device), dtype=float)
            scores[start:stop, t] = np.asarray(score_fn(probs), dtype=float)
            correct[start:stop, t] = (probs.argmax(axis=1) == yb).astype(float)
            if t == T:
                break
            nxt = np.asarray(
                policy.select_next(model, Xb, observed, groups, device), dtype=int
            )
            order[start:stop, t] = nxt.astype(np.int64)
            observed[np.arange(B), nxt] = 1.0
    return scores, correct, order


class _MnistEpsGreedy:
    """MNIST (patch) epsilon-greedy mixture; matches the image select_next signature.

    Mirrors :class:`cafa.policies_v2.EpsGreedyMixture` but for the torch image
    policy (kept here because it wraps the torch rollout's tensor interface).
    """

    def __init__(self, greedy_policy, epsilon: float, seed: int):
        self.greedy = greedy_policy
        self.epsilon = float(epsilon)
        self.rng = np.random.default_rng(int(seed))

    def select_next(self, predictor, X, observed, device):
        greedy_pick = self.greedy.select_next(predictor, X, observed, device)
        obs_np = observed.detach().cpu().numpy()
        B = obs_np.shape[0]
        keys = self.rng.random(obs_np.shape)
        keys = np.where(obs_np > 0.5, -1.0, keys)
        random_pick = keys.argmax(axis=1).astype(np.int64)
        take_random = self.rng.random(B) < self.epsilon
        greedy_np = np.asarray(greedy_pick.detach().cpu().numpy(), dtype=np.int64)
        mixed = np.where(take_random, random_pick, greedy_np).astype(np.int64)
        return torch.as_tensor(mixed, device=device)


# --------------------------------------------------------------------------- #
# Cell list
# --------------------------------------------------------------------------- #
def build_cells():
    cells = []
    for ds in ["mnist"] + _TAB:                        # Phase 1: cells 0-7
        for pol in ["greedy_entropy", "random"]:
            cells.append({"dataset": ds, "policy": pol, "epsilon": None, "score": None})
    for ds in _TAB + ["mnist"]:                        # Phase 2: cells 8-15
        for eps in [0.25, 0.5]:
            cells.append({"dataset": ds, "policy": "eps_greedy", "epsilon": eps, "score": None})
    cells.append({"dataset": "tabular:spambase", "policy": "greedy_entropy",   # Phase 4: cell 16 (optional)
                  "epsilon": None, "score": "margin"})
    for ds in ["tabular:adult", "tabular:MiniBooNE", "mnist"]:                 # Phase 4: cells 17-19
        cells.append({"dataset": ds, "policy": "greedy_entropy",
                      "epsilon": None, "score": "margin"})
    return cells


def policy_token_of(policy: str, epsilon) -> str:
    if policy == "eps_greedy":
        return eps_greedy_policy_token(epsilon)
    return policy


def run_one(dataset, policy, epsilon, score, train_seed, device, *, cfg, paths):
    ts = int(train_seed)
    dsname = dsname_of(dataset)
    score_name = score or cfg["method"].get("procedure_score", "softmax")
    policy_token = policy_token_of(policy, epsilon)
    policy_seed = (10_000 + int(round(1000 * float(epsilon)))) if policy == "eps_greedy" else ts

    ckpt_path = Path(paths.results_root) / "checkpoints_v2" / f"{dsname}_ts{ts}.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(
            f"backbone checkpoint not found at {ckpt_path}; run train_backbone_v2.py first."
        )

    # Determinism: seed numpy + torch from the policy seed before the rollout.
    config.set_seed(policy_seed)
    torch.manual_seed(policy_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(policy_seed)

    if dataset == "mnist":
        from cafa.acquisition import get_policy
        from cafa.models import MaskedPredictor, N_CLASSES

        payload = torch.load(ckpt_path, map_location=device, weights_only=False)
        meta = payload.get("meta", {})
        assert meta.get("pipeline") == "v2", f"checkpoint {ckpt_path} is not a v2 backbone."
        assert int(meta.get("train_seed", -1)) == ts, "checkpoint train_seed mismatch."
        model = MaskedPredictor(n_classes=int(meta.get("n_classes", N_CLASSES)))
        model.load_state_dict(payload["state_dict"]); model.to(device); model.eval()

        pool = load_mnist_pool(cfg, train_seed=ts, download=False)
        X_held, y_held = pool["heldout"]
        X_train = pool["train"][0]
        greedy = get_policy("greedy_entropy", X_train)
        if policy == "greedy_entropy":
            pol = greedy
        elif policy == "random":
            pol = get_policy("random", X_train, seed=policy_seed)
        elif policy == "eps_greedy":
            pol = _MnistEpsGreedy(greedy, epsilon, policy_seed)
        else:
            raise ValueError(f"unknown policy {policy!r}.")
        scores, correct, order = rollout_mnist_with_order(model, pol, score_name, X_held, y_held, device)
    elif dataset.startswith("tabular:"):
        from cafa.models import TabularMaskedPredictor
        from cafa.tabular import get_tabular_policy

        name = dataset.split(":", 1)[1]
        pool = load_tabular_pool(name, cfg, train_seed=ts, download=False)
        payload = torch.load(ckpt_path, map_location=device, weights_only=False)
        meta = payload.get("meta", {})
        assert meta.get("pipeline") == "v2", f"checkpoint {ckpt_path} is not a v2 backbone."
        assert int(meta.get("train_seed", -1)) == ts, "checkpoint train_seed mismatch."
        model = TabularMaskedPredictor(n_cols=int(pool["n_cols"]), n_classes=int(pool["n_classes"]))
        model.load_state_dict(payload["state_dict"]); model.to(device); model.eval()

        X_held, y_held = pool["heldout"]
        X_train = pool["train"][0]
        fgroups = pool["feature_groups"]
        greedy = get_tabular_policy("greedy_entropy", X_train)
        if policy == "greedy_entropy":
            pol = greedy
        elif policy == "random":
            pol = get_tabular_policy("random", X_train, seed=policy_seed)
        elif policy == "eps_greedy":
            pol = EpsGreedyMixture(greedy, epsilon, policy_seed)
        else:
            raise ValueError(f"unknown policy {policy!r}.")
        scores, correct, order = rollout_tabular_with_order(
            model, pol, score_name, X_held, y_held, fgroups, device
        )
    else:
        raise ValueError(f"unknown dataset {dataset!r}; expected mnist | tabular:<name>.")

    n = int(scores.shape[0])
    row_pos = np.arange(n, dtype=np.int64)
    # DECISION: feature_costs_by_scheme is embedded in cache meta (additive to the
    # WO-4 meta list) so probe_commit / eval_sweep stay torch-free (no data reload)
    # -- the costs are a pure function of the fixed train split (train_seed).
    costs_json = {
        scheme: np.asarray(vals, dtype=float).tolist()
        for scheme, vals in pool["feature_costs_by_scheme"].items()
    }
    cache_meta = {
        "dataset": dataset,
        "policy": policy_token,
        "epsilon": (None if epsilon is None else float(epsilon)),
        "score": score_name,
        "train_seed": ts,
        "checkpoint": ckpt_path.name,
        "checkpoint_sha256": file_sha256(ckpt_path),
        "split_digest": pool["split_digest"],
        "feature_costs_by_scheme": costs_json,
        "T": int(order.shape[1]),
        "n": n,
        "numpy_version": np.__version__,
        "created": datetime.now(timezone.utc).isoformat(),
    }

    out_dir = Path(paths.results_root) / "pool_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dsname}_ts{ts}_{policy_token}_{score_name}.npz"
    poolmod.save_pool_cache(
        out_path, scores=scores, correct=correct, order=order, y=y_held,
        row_pos=row_pos, meta=cache_meta,
    )
    print(f"[pool] saved cache -> {out_path}  (n={n}, T={order.shape[1]})", flush=True)
    return out_path


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="CAFA v2 pool rollout runner.")
    p.add_argument("--dataset", default=None, help="mnist | tabular:<name>")
    p.add_argument("--policy", default="greedy_entropy",
                   choices=["greedy_entropy", "random", "eps_greedy"])
    p.add_argument("--epsilon", type=float, default=None, help="epsilon for eps_greedy.")
    p.add_argument("--score", default=None, help="readiness score (default: config procedure_score).")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--device", default="cpu")
    p.add_argument("--cell", type=int, default=None, help="slurm array index -> a cell.")
    return p.parse_args(argv)


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
        print(f"cell {args.cell}/{len(cells)} -> dataset={c['dataset']} policy={c['policy']} "
              f"epsilon={c['epsilon']} score={c['score']}", flush=True)
        run_one(c["dataset"], c["policy"], c["epsilon"], c["score"],
                args.train_seed, args.device, cfg=cfg, paths=paths)
        return 0

    if args.dataset is None:
        print("ERROR: provide --dataset or --cell.", file=sys.stderr)
        return 1
    if args.policy == "eps_greedy" and args.epsilon is None:
        print("ERROR: --policy eps_greedy requires --epsilon.", file=sys.stderr)
        return 1
    run_one(args.dataset, args.policy, args.epsilon, args.score,
            args.train_seed, args.device, cfg=cfg, paths=paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
