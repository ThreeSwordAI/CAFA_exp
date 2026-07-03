#!/usr/bin/env python
"""WO-7 -- v2 backbone training (one script, both dataset families).

Trains a single masked predictor per (dataset, train_seed) on the **fixed train
split** from the v2 pool loaders (:func:`cafa.data.load_mnist_pool` /
:func:`cafa.data.load_tabular_pool`).  The train split depends only on
``train_seed``, so one checkpoint serves every policy / resplit / cost scheme.

Usage
-----
    python scripts/train_backbone_v2.py --dataset mnist --train-seed 0 [--device cuda] [--download]
    python scripts/train_backbone_v2.py --dataset tabular:adult --train-seed 0 [--device cpu]

The checkpoint is written to
``${RESULTS_ROOT}/checkpoints_v2/{dsname}_ts{train_seed}.pt`` (dsname = ``mnist``
or ``tabular-adult`` etc.), with provenance meta (split_digest, encoder widths,
training cfg, final masked train acc, ``pipeline: "v2"``).  Its sha256 is printed
so the pool runner can embed it in cache meta.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.data import load_mnist_pool, load_tabular_pool  # noqa: E402
from cafa.repro_utils import file_sha256  # noqa: E402


def dsname_of(dataset: str) -> str:
    """``mnist`` -> ``mnist``; ``tabular:adult`` -> ``tabular-adult``."""
    if dataset.startswith("tabular:"):
        return "tabular-" + dataset.split(":", 1)[1]
    return dataset


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train the v2 CAFA backbone (fixed train split).")
    p.add_argument("--dataset", required=True, help="mnist | tabular:<name>")
    p.add_argument("--train-seed", type=int, default=0, help="Fixes the train split + backbone.")
    p.add_argument("--device", default="cpu", help="cuda or cpu.")
    p.add_argument("--download", action="store_true", help="Download MNIST via torchvision.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    cfg = config.load_experiment()
    paths = config.load_paths()
    train_seed = int(args.train_seed)

    # Determinism: seed numpy + torch from train_seed exactly as the legacy trainer.
    config.set_seed(train_seed)
    torch.manual_seed(train_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(train_seed)
    device = torch.device(
        args.device if (torch.cuda.is_available() or args.device == "cpu") else "cpu"
    )

    dsname = dsname_of(args.dataset)
    ckpt_dir = Path(paths.results_root) / "checkpoints_v2"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = ckpt_dir / f"{dsname}_ts{train_seed}.pt"

    if args.dataset == "mnist":
        from cafa.models import MaskedPredictor, N_CLASSES, train_masked_predictor

        pool = load_mnist_pool(cfg, train_seed=train_seed, download=args.download)
        X_train, y_train = pool["train"]
        tcfg = cfg.get("training", {})
        epochs = int(tcfg.get("epochs", 15))
        batch_size = int(tcfg.get("batch_size", 256))
        lr = float(tcfg.get("lr", 1e-3))
        mask_min = int(tcfg.get("mask_min", 0))
        mask_max = int(tcfg.get("mask_max", 49))
        print(f"[train-v2] mnist train_seed={train_seed} train_n={X_train.shape[0]} device={device}", flush=True)
        model = MaskedPredictor(n_classes=N_CLASSES)
        history = train_masked_predictor(
            model, X_train, y_train, epochs=epochs, batch_size=batch_size, lr=lr,
            mask_min=mask_min, mask_max=mask_max, device=device, seed=train_seed,
            log_every=max(1, epochs // 5),
        )
        train_cfg_meta = {"epochs": epochs, "batch_size": batch_size, "lr": lr,
                          "mask_min": mask_min, "mask_max": mask_max}
        encoder_meta = {"n_patches": int(pool["n_patches"]), "patch_dim": int(pool["patch_dim"])}
    elif args.dataset.startswith("tabular:"):
        from cafa.models import TabularMaskedPredictor, train_tabular_predictor

        name = args.dataset.split(":", 1)[1]
        pool = load_tabular_pool(name, cfg, train_seed=train_seed, download=args.download)
        X_train, y_train = pool["train"]
        fgroups = pool["feature_groups"]
        tcfg = cfg.get("training_tabular", {})
        epochs = int(tcfg.get("epochs", 40))
        batch_size = int(tcfg.get("batch_size", 256))
        lr = float(tcfg.get("lr", 1e-3))
        print(f"[train-v2] tabular:{name} train_seed={train_seed} "
              f"train_n={X_train.shape[0]} n_cols={pool['n_cols']} device={device}", flush=True)
        model = TabularMaskedPredictor(n_cols=int(pool["n_cols"]), n_classes=int(pool["n_classes"]))
        history = train_tabular_predictor(
            model, X_train, y_train, fgroups, epochs=epochs, batch_size=batch_size,
            lr=lr, device=device, seed=train_seed, log_every=max(1, epochs // 5),
        )
        train_cfg_meta = {"epochs": epochs, "batch_size": batch_size, "lr": lr}
        encoder_meta = {"n_cols": int(pool["n_cols"]),
                        "feature_group_widths": [int(len(g)) for g in fgroups]}
    else:
        print(f"ERROR: unknown dataset {args.dataset!r}; expected mnist | tabular:<name>.",
              file=sys.stderr)
        return 1

    final_acc = float(history["epoch_acc"][-1]) if history.get("epoch_acc") else None
    payload = {
        "state_dict": model.state_dict(),
        "meta": {
            "dataset": args.dataset,
            "train_seed": train_seed,
            "split_digest": pool["split_digest"]["train"],
            "n_train": int(X_train.shape[0]),
            "n_classes": int(pool["n_classes"]),
            "encoder": encoder_meta,
            "training": train_cfg_meta,
            "final_masked_train_acc": final_acc,
            "pipeline": "v2",
        },
    }
    torch.save(payload, ckpt_path)
    sha = file_sha256(ckpt_path)
    print(f"[train-v2] saved checkpoint -> {ckpt_path}", flush=True)
    print(f"[train-v2] sha256={sha}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
