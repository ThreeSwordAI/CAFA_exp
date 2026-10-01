#!/usr/bin/env python
"""v3 -- pool rollout for the AISTATS suite (records the acquisition ``order``).

Rolls out the ENTIRE heldout split (probe + calpool + test, in heldout order)
once per (dataset, train_seed, policy[, score]) with the v3 backbone and writes
``${RESULTS_ROOT}/pool_v3/{dsname}_ts{ts}_{policy_token}_{score}.npz`` in the
:mod:`cafa.pool` format (identical to the v2 caches, so every torch-free
script works on either).

Policies: ``greedy_entropy`` | ``random`` | ``eps_greedy --epsilon e`` |
``--orders-file FILE --policy-token NAME`` (replay a frozen external order
matrix, e.g. an AFABench-trained GDFS / AACO; see :mod:`cafa.external_orders`).

    python scripts/run_pool_rollout_v3.py --dataset fashionmnist --policy greedy_entropy --train-seed 0 --device cuda
    python scripts/run_pool_rollout_v3.py --dataset image:imagenette --policy greedy_entropy --train-seed 0 --device cuda --batch-size 32
    python scripts/run_pool_rollout_v3.py --dataset csv:physionet --policy random --train-seed 0
    python scripts/run_pool_rollout_v3.py --dataset csv:physionet --orders-file orders/physionet_ts0_gdfs.npz --policy-token afabench_gdfs --train-seed 0
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
from cafa.data_v3 import dataset_kind, load_pool_v3  # noqa: E402
from cafa.external_orders import load_orders  # noqa: E402
from cafa.policies_v2 import EpsGreedyMixture, eps_greedy_policy_token  # noqa: E402
from cafa.repro_utils import file_sha256  # noqa: E402
from cafa.scores import get_score_fn  # noqa: E402
from cafa.splits import split_digest  # noqa: E402
from cafa.tabular import _as_feature_groups, expand_feature_mask, get_tabular_policy  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commit_v3 import dsname_of  # noqa: E402
from run_pool_rollout import _MnistEpsGreedy, rollout_mnist_with_order, rollout_tabular_with_order  # noqa: E402


# --------------------------------------------------------------------------- #
# RGB rollout (Imagenette) and order replay
# --------------------------------------------------------------------------- #
def rollout_rgb_with_order(model, policy, score_fn, X_uint8, y, device, batch_size=32):
    if isinstance(score_fn, str):
        score_fn = get_score_fn(score_fn)
    device = torch.device(device)
    y_np = np.asarray(y).astype(np.int64)
    N, P, T = X_uint8.shape[0], model.n_patches, model.n_patches
    scores = np.zeros((N, T + 1), dtype=float)
    correct = np.zeros((N, T + 1), dtype=float)
    order = np.zeros((N, T), dtype=np.int64)
    for start in range(0, N, batch_size):
        stop = min(start + batch_size, N)
        xb = torch.as_tensor(X_uint8[start:stop], device=device)
        x_norm = model.normalize(xb)
        B = xb.shape[0]
        observed = torch.zeros((B, P), dtype=torch.float32, device=device)
        for t in range(T + 1):
            with torch.no_grad():
                probs = torch.softmax(model.logits_from_images(x_norm, observed), dim=1).cpu().numpy()
            scores[start:stop, t] = np.asarray(score_fn(probs), dtype=float)
            correct[start:stop, t] = (probs.argmax(axis=1) == y_np[start:stop]).astype(float)
            if t == T:
                break
            nxt = policy.select_next(model, x_norm, observed, device)
            order[start:stop, t] = nxt.detach().cpu().numpy().astype(np.int64)
            observed = observed.clone()
            observed[torch.arange(B, device=device), nxt] = 1.0
        if (start // batch_size) % 10 == 0:
            print(f"  [rgb rollout] {stop}/{N}", flush=True)
    return scores, correct, order


def rollout_replay(model, orders, score_fn, kind, X, y, feature_groups, device, batch_size=256):
    """Readiness / correctness of OUR predictor along a frozen external order matrix."""
    if isinstance(score_fn, str):
        score_fn = get_score_fn(score_fn)
    y_np = np.asarray(y).astype(np.int64)
    N, T = orders.shape
    scores = np.zeros((N, T + 1), dtype=float)
    correct = np.zeros((N, T + 1), dtype=float)
    for start in range(0, N, batch_size):
        stop = min(start + batch_size, N)
        B = stop - start
        if kind == "image_patches":
            Xb = torch.as_tensor(np.asarray(X[start:stop], dtype=np.float32), device=device)
            observed = torch.zeros((B, T), dtype=torch.float32, device=device)
            for t in range(T + 1):
                probs = model.predict_proba(Xb, observed, device=device)
                scores[start:stop, t] = score_fn(probs)
                correct[start:stop, t] = (probs.argmax(1) == y_np[start:stop]).astype(float)
                if t == T:
                    break
                observed = observed.clone()
                observed[torch.arange(B, device=device), torch.as_tensor(orders[start:stop, t], device=device)] = 1.0
        elif kind == "image_rgb":
            xb = model.normalize(torch.as_tensor(X[start:stop], device=device))
            observed = torch.zeros((B, T), dtype=torch.float32, device=device)
            for t in range(T + 1):
                with torch.no_grad():
                    probs = torch.softmax(model.logits_from_images(xb, observed), dim=1).cpu().numpy()
                scores[start:stop, t] = score_fn(probs)
                correct[start:stop, t] = (probs.argmax(1) == y_np[start:stop]).astype(float)
                if t == T:
                    break
                observed = observed.clone()
                observed[torch.arange(B, device=device), torch.as_tensor(orders[start:stop, t], device=device)] = 1.0
        else:
            Xb = np.asarray(X[start:stop], dtype=np.float32)
            groups = _as_feature_groups(feature_groups, Xb.shape[1])
            observed = np.zeros((B, len(groups)), dtype=np.float32)
            for t in range(T + 1):
                probs = np.asarray(model.predict_proba(Xb, expand_feature_mask(observed, groups), device=device))
                scores[start:stop, t] = score_fn(probs)
                correct[start:stop, t] = (probs.argmax(1) == y_np[start:stop]).astype(float)
                if t == T:
                    break
                observed[np.arange(B), orders[start:stop, t]] = 1.0
    return scores, correct, np.asarray(orders, dtype=np.int64)


# --------------------------------------------------------------------------- #
def load_backbone(ckpt_path: Path, kind: str, pool: dict, device):
    payload = torch.load(ckpt_path, map_location=device, weights_only=False)
    meta = payload.get("meta", {})
    assert meta.get("pipeline") == "v3", f"{ckpt_path} is not a v3 backbone."
    arch = meta["arch"]
    if kind == "image_patches":
        from cafa.models_v3 import MaskedPredictorV2
        model = MaskedPredictorV2(n_classes=int(arch["n_classes"]), width_mult=int(arch["width_mult"]))
    elif kind == "image_rgb":
        from cafa.models_v3 import ResNetPatchPredictor
        model = ResNetPatchPredictor(n_classes=int(arch["n_classes"]), patch_grid=tuple(arch["patch_grid"]),
                                     img_size=int(arch["img_size"]), pretrained=False)
    else:
        from cafa.models import TabularMaskedPredictor
        model = TabularMaskedPredictor(n_cols=int(arch["n_cols"]), n_classes=int(arch["n_classes"]),
                                       hidden=int(arch["hidden"]))
    model.load_state_dict(payload["state_dict"])
    model.to(device)
    model.eval()
    return model, meta


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--policy", default="greedy_entropy", help="greedy_entropy | random | eps_greedy")
    p.add_argument("--epsilon", type=float, default=None)
    p.add_argument("--orders-file", default=None, help="replay a frozen external order matrix")
    p.add_argument("--policy-token", default=None, help="cache token for --orders-file (e.g. afabench_gdfs)")
    p.add_argument("--score", default=None)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--device", default="cpu")
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--max-rows", type=int, default=None, help="roll out only the first rows (smoke tests)")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    a = p.parse_args(argv)

    cfg = config.load_experiment(a.config)
    paths = config.load_paths()
    ts = int(a.train_seed)
    dsname = dsname_of(a.dataset)
    kind = dataset_kind(a.dataset)
    score_name = a.score or cfg["method"].get("procedure_score", "softmax")
    device = torch.device(a.device)
    if a.orders_file:
        policy_token = a.policy_token or "external"
    else:
        policy_token = eps_greedy_policy_token(a.epsilon) if a.policy == "eps_greedy" else a.policy
    policy_seed = (10_000 + int(round(1000 * float(a.epsilon)))) if a.policy == "eps_greedy" and a.epsilon is not None else ts
    config.set_seed(policy_seed)
    torch.manual_seed(policy_seed)

    pool = load_pool_v3(a.dataset, cfg, train_seed=ts, download=False)
    X_held, y_held = pool["heldout"]
    X_train = pool["train"][0]
    if a.max_rows:
        X_held, y_held = X_held[: a.max_rows], y_held[: a.max_rows]
    ckpt = Path(paths.results_root) / "checkpoints_v3" / f"{dsname}_ts{ts}.pt"
    if not ckpt.exists():
        raise FileNotFoundError(f"{ckpt} not found; run train_backbone_v3.py first.")
    model, ckpt_meta = load_backbone(ckpt, kind, pool, device)
    bs = a.batch_size or (32 if kind == "image_rgb" else 256)

    if a.orders_file:
        T_expected = int(pool.get("n_patches", pool.get("n_features", 0)))
        od = load_orders(a.orders_file, n_expected=None if a.max_rows else X_held.shape[0], T_expected=T_expected,
                         heldout_digest=None)
        orders = od["orders"][: X_held.shape[0]]
        scores, correct, order = rollout_replay(model, orders, score_name, kind, X_held, y_held,
                                                pool.get("feature_groups"), device, bs)
    elif kind == "image_patches":
        from cafa.acquisition import get_policy
        greedy = get_policy("greedy_entropy", X_train)
        pol = {"greedy_entropy": greedy, "random": get_policy("random", X_train, seed=policy_seed)}.get(a.policy)
        if a.policy == "eps_greedy":
            pol = _MnistEpsGreedy(greedy, a.epsilon, policy_seed)
        scores, correct, order = rollout_mnist_with_order(model, pol, score_name, X_held, y_held, device, bs)
    elif kind == "image_rgb":
        from cafa.models_v3 import GreedyEntropyImagePolicy, RandomImagePolicy
        if a.policy == "greedy_entropy":
            pol = GreedyEntropyImagePolicy.from_training_data(X_train, pool["patch_grid"], pool["img_size"])
        elif a.policy == "random":
            pol = RandomImagePolicy(seed=policy_seed)
        else:
            raise ValueError("Imagenette supports greedy_entropy | random | --orders-file")
        scores, correct, order = rollout_rgb_with_order(model, pol, score_name, X_held, y_held, device, bs)
    else:
        greedy = get_tabular_policy("greedy_entropy", X_train)
        pol = {"greedy_entropy": greedy, "random": get_tabular_policy("random", X_train, seed=policy_seed)}.get(a.policy)
        if a.policy == "eps_greedy":
            pol = EpsGreedyMixture(greedy, a.epsilon, policy_seed)
        scores, correct, order = rollout_tabular_with_order(model, pol, score_name, X_held, y_held,
                                                            pool["feature_groups"], device, bs)

    n = int(scores.shape[0])
    meta = {"dataset": a.dataset, "dsname": dsname, "policy": policy_token, "epsilon": a.epsilon,
            "score": score_name, "train_seed": ts, "pipeline": "v3", "checkpoint": ckpt.name,
            "checkpoint_sha256": file_sha256(ckpt), "checkpoint_meta_arch": ckpt_meta.get("arch"),
            "split_digest": pool["split_digest"], "heldout_digest": split_digest(pool["heldout_index"]),
            "feature_costs_by_scheme": {k: np.asarray(v).tolist() for k, v in pool["feature_costs_by_scheme"].items()},
            "T": int(order.shape[1]), "n": n, "orders_file": a.orders_file,
            "numpy_version": np.__version__, "torch_version": torch.__version__,
            "created": datetime.now(timezone.utc).isoformat()}
    out_dir = Path(paths.results_root) / "pool_v3"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{dsname}_ts{ts}_{policy_token}_{score_name}.npz"
    poolmod.save_pool_cache(out, scores=scores, correct=correct, order=order, y=np.asarray(y_held),
                            row_pos=np.arange(n), meta=meta)
    print(f"[rollout_v3] {a.dataset} ts{ts} {policy_token}: n={n} T={order.shape[1]} "
          f"full-acq acc={correct[:, -1].mean():.4f} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
