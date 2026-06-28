#!/usr/bin/env python
"""Train the masked predictor (backbone) for patch-wise AFA on MNIST.

The predictor is trained **once** on the protocol ``train`` split with random
patch masking, so it can predict from any observed subset (including empty and
full).  The acquisition policy is frozen at inference and does not change the
predictor, so a single checkpoint serves every policy.

Usage
-----
    python scripts/train_backbone.py --dataset mnist --backbone greedy_entropy \
        [--download] [--epochs N] [--device cuda|cpu]

``--download`` triggers the torchvision MNIST download (run once on a login node
with internet).  The checkpoint is written to
``${results_root}/checkpoints/{dataset}_{backbone}.pt`` together with metadata
(patch grid, feature costs, class count, training config, seed).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

# Make ``cafa`` importable even without PYTHONPATH set.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.data import load_mnist_afa  # noqa: E402
from cafa.models import MaskedPredictor, N_CLASSES, train_masked_predictor  # noqa: E402


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train the CAFA masked predictor.")
    p.add_argument("--dataset", default="mnist", choices=["mnist"])
    p.add_argument(
        "--backbone",
        default="greedy_entropy",
        help="Policy name this checkpoint is labelled with (the predictor is "
        "policy-agnostic; the label only sets the checkpoint filename).",
    )
    p.add_argument("--download", action="store_true", help="Download MNIST via torchvision.")
    p.add_argument("--epochs", type=int, default=None, help="Override training.epochs.")
    p.add_argument("--batch-size", type=int, default=None, help="Override training.batch_size.")
    p.add_argument("--lr", type=float, default=None, help="Override training.lr.")
    p.add_argument("--device", default="cpu", help="cuda or cpu.")
    p.add_argument("--seed", type=int, default=0, help="Seed for split + training.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    cfg = config.load_experiment()
    paths = config.load_paths()
    train_cfg = cfg.get("training", {})

    epochs = args.epochs if args.epochs is not None else int(train_cfg.get("epochs", 15))
    batch_size = (
        args.batch_size if args.batch_size is not None else int(train_cfg.get("batch_size", 256))
    )
    lr = args.lr if args.lr is not None else float(train_cfg.get("lr", 1e-3))
    mask_min = int(train_cfg.get("mask_min", 0))
    mask_max = int(train_cfg.get("mask_max", 49))

    # Determinism: seed numpy (via config.set_seed) and torch from the seed.
    config.set_seed(args.seed)
    torch.manual_seed(int(args.seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(args.seed))

    device = torch.device(args.device if torch.cuda.is_available() or args.device == "cpu" else "cpu")

    data = load_mnist_afa(cfg, seed=args.seed, download=args.download)
    X_train, y_train = data["train"]
    print(
        f"[train] dataset={args.dataset} backbone={args.backbone} "
        f"train_n={X_train.shape[0]} patches={data['n_patches']} device={device}",
        flush=True,
    )

    model = MaskedPredictor(n_classes=N_CLASSES)
    history = train_masked_predictor(
        model,
        X_train,
        y_train,
        epochs=epochs,
        batch_size=batch_size,
        lr=lr,
        mask_min=mask_min,
        mask_max=mask_max,
        device=device,
        seed=args.seed,
        log_every=max(1, epochs // 5),
    )

    ckpt_dir = Path(paths.results_root) / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = ckpt_dir / f"{args.dataset}_{args.backbone}.pt"

    payload = {
        "state_dict": model.state_dict(),
        "meta": {
            "dataset": args.dataset,
            "backbone": args.backbone,
            "patch_grid": list(data["patch_grid"]),
            "n_patches": int(data["n_patches"]),
            "patch_dim": int(data["patch_dim"]),
            "n_classes": int(data["n_classes"]),
            "feature_costs": np.asarray(data["feature_costs"]).tolist(),
            "training": {
                "epochs": epochs,
                "batch_size": batch_size,
                "lr": lr,
                "mask_min": mask_min,
                "mask_max": mask_max,
            },
            "seed": int(args.seed),
            "final_masked_train_acc": float(history["epoch_acc"][-1]) if history["epoch_acc"] else None,
        },
    }
    torch.save(payload, ckpt_path)
    print(f"[train] saved checkpoint -> {ckpt_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())