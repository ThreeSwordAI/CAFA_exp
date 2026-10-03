#!/usr/bin/env python
"""v3 -- backbone training for the AISTATS suite (one script, all dataset kinds).

Trains ONE masked predictor per (dataset, train_seed) on the fixed train split
of :func:`cafa.data_v3.load_pool_v3` and writes
``${RESULTS_ROOT}/checkpoints_v3/{dsname}_ts{ts}.pt`` with provenance meta
(``pipeline: "v3"``, arch, training cfg, split digests, masked train acc, and
the full-observation train accuracy).

    python scripts/train_backbone_v3.py --dataset mnist --train-seed 0 --device cuda
    python scripts/train_backbone_v3.py --dataset fashionmnist --train-seed 0 --device cuda
    python scripts/train_backbone_v3.py --dataset image:imagenette --train-seed 0 --device cuda
    python scripts/train_backbone_v3.py --dataset csv:physionet --train-seed 0
    python scripts/train_backbone_v3.py --dataset cube --train-seed 0
    python scripts/train_backbone_v3.py --dataset tabular:MiniBooNE --train-seed 0

Round 3 (Task L, the FashionMNIST predictor-upgrade repair): ``--checkpoint-tag TAG`` writes
``${RESULTS_ROOT}/checkpoints_v3_TAG/{dsname}_ts{ts}.pt`` instead (the protocol backbone is never
overwritten) and records ``checkpoint_tag`` in the meta; ``--width-mult`` / ``--p-full`` override the
config (image_patches only; recorded in ``meta["training"]``, the width also in ``meta["arch"]``).
``--width-mult`` / ``--p-full`` REQUIRE ``--checkpoint-tag`` (a usage error without it, as is an empty
tag), so a non-protocol backbone can never land in ``checkpoints_v3/``; ``--epochs`` alone stays the
protocol retrain override (CUBE / MiniBooNE, ``--epochs 60``).  Without these flags the behaviour is unchanged.

    python scripts/train_backbone_v3.py --dataset fashionmnist --train-seed 0 --device cuda --checkpoint-tag repair --epochs 60 --width-mult 4 --p-full 0.3
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
from cafa.data_v3 import dataset_kind, load_pool_v3  # noqa: E402
from cafa.repro_utils import file_sha256  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commit_v3 import dsname_of  # noqa: E402
from drive_v3 import checkpoint_dir_name, checkpoint_tag_arg  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--device", default="cpu")
    p.add_argument("--download", action="store_true")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    p.add_argument("--epochs", type=int, default=None, help="override the config epochs (smoke tests)")
    p.add_argument("--max-train", type=int, default=None, help="subsample the train split (smoke tests)")
    # round 3 (Task L): a second, stronger backbone next to the protocol one
    p.add_argument("--checkpoint-tag", type=checkpoint_tag_arg, default=None,
                   help="write checkpoints_v3_TAG/{dsname}_ts{ts}.pt (letters, digits, underscore)")
    p.add_argument("--width-mult", type=int, default=None,
                   help="image_patches only, needs --checkpoint-tag: override the config width_mult")
    p.add_argument("--p-full", type=float, default=None,
                   help="image_patches only, needs --checkpoint-tag: override the config p_full")
    return p


def training_cfg(cfg: dict, kind: str, epochs=None, width_mult=None, p_full=None) -> dict:
    """The training cfg of one dataset kind (``training_v3``) with the command-line overrides; recorded as
    ``meta["training"]``.  ``width_mult`` / ``p_full`` exist for the masked patch CNN only (ValueError otherwise)."""
    tcfg = dict(cfg.get("training_v3", {}).get("tabular" if kind.startswith(("tabular", "synthetic")) else kind, {}))
    if epochs is not None:
        tcfg["epochs"] = int(epochs)
    for flag, val in (("--width-mult", width_mult), ("--p-full", p_full)):
        if val is not None and kind != "image_patches":
            raise ValueError(f"{flag} applies to image_patches datasets (mnist, fashionmnist) only; got kind {kind!r}.")
    if width_mult is not None:
        if int(width_mult) < 1:
            raise ValueError(f"--width-mult must be >= 1; got {width_mult}.")
        tcfg["width_mult"] = int(width_mult)
    if p_full is not None:
        if not 0.0 <= float(p_full) <= 1.0:
            raise ValueError(f"--p-full must be in [0, 1]; got {p_full}.")
        tcfg["p_full"] = float(p_full)
    return tcfg


def main(argv=None) -> int:
    p = build_parser()
    a = p.parse_args(argv)
    if (a.width_mult is not None or a.p_full is not None) and a.checkpoint_tag is None:
        # round 3: a non-protocol backbone never lands in checkpoints_v3/ (--epochs alone is the protocol retrain)
        p.error("--width-mult/--p-full change the protocol backbone; give --checkpoint-tag so it is written to "
                "checkpoints_v3_<tag>/")

    cfg = config.load_experiment(a.config)
    ts = int(a.train_seed)
    kind = dataset_kind(a.dataset)
    try:
        tcfg = training_cfg(cfg, kind, a.epochs, a.width_mult, a.p_full)
    except ValueError as e:
        p.error(str(e))
    paths = config.load_paths()
    config.set_seed(ts)
    torch.manual_seed(ts)

    pool = load_pool_v3(a.dataset, cfg, train_seed=ts, download=a.download)
    X_train, y_train = pool["train"]
    if a.max_train:
        X_train, y_train = X_train[: a.max_train], y_train[: a.max_train]
    device = torch.device(a.device)

    if kind == "image_patches":
        from cafa.models_v3 import MaskedPredictorV2, train_masked_predictor_v2
        model = MaskedPredictorV2(n_classes=int(pool["n_classes"]), width_mult=int(tcfg.get("width_mult", 2)))
        hist = train_masked_predictor_v2(model, X_train, y_train, epochs=int(tcfg.get("epochs", 30)),
                                         batch_size=int(tcfg.get("batch_size", 256)), lr=float(tcfg.get("lr", 1e-3)),
                                         p_full=float(tcfg.get("p_full", 0.2)), device=device, seed=ts, log_every=5)
        arch = {"name": "masked_cnn_v2", "width_mult": int(tcfg.get("width_mult", 2)), "n_classes": int(pool["n_classes"])}
        full_mask = np.ones((min(2000, X_train.shape[0]), X_train.shape[1]), dtype=np.float32)
        full_acc = float((model.predict_proba(X_train[:2000], full_mask, device=device).argmax(1) == y_train[:2000]).mean())
    elif kind == "image_rgb":
        from cafa.models_v3 import ResNetPatchPredictor, train_resnet_patch_predictor
        model = ResNetPatchPredictor(n_classes=int(pool["n_classes"]), patch_grid=pool["patch_grid"],
                                     img_size=int(pool["img_size"]), pretrained=bool(tcfg.get("pretrained", True)))
        hist = train_resnet_patch_predictor(model, X_train, y_train, epochs=int(tcfg.get("epochs", 12)),
                                            batch_size=int(tcfg.get("batch_size", 64)), lr=float(tcfg.get("lr", 3e-4)),
                                            p_full=float(tcfg.get("p_full", 0.2)), device=device, seed=ts, log_every=1)
        arch = {"name": "resnet18_patch", "patch_grid": list(pool["patch_grid"]), "img_size": int(pool["img_size"]),
                "n_classes": int(pool["n_classes"]), "pretrained": bool(tcfg.get("pretrained", True))}
        n_eval = min(512, X_train.shape[0])
        probs = []
        for s in range(0, n_eval, 64):
            xb = X_train[s:min(s + 64, n_eval)]
            probs.append(model.predict_proba(xb, np.ones((xb.shape[0], model.n_patches), np.float32), device=device))
        full_acc = float((np.concatenate(probs).argmax(1) == y_train[:n_eval]).mean())
    else:
        from cafa.models import TabularMaskedPredictor, train_tabular_predictor
        hidden = int(tcfg.get("hidden", 256))
        model = TabularMaskedPredictor(n_cols=int(pool["n_cols"]), n_classes=int(pool["n_classes"]), hidden=hidden)
        hist = train_tabular_predictor(model, X_train, y_train, pool["feature_groups"],
                                       epochs=int(tcfg.get("epochs", 40)), batch_size=int(tcfg.get("batch_size", 256)),
                                       lr=float(tcfg.get("lr", 1e-3)), device=device, seed=ts, log_every=10)
        arch = {"name": "masked_mlp", "hidden": hidden, "n_cols": int(pool["n_cols"]), "n_classes": int(pool["n_classes"])}
        full_mask = np.ones((min(5000, X_train.shape[0]), X_train.shape[1]), dtype=np.float32)
        full_acc = float((model.predict_proba(X_train[:5000], full_mask, device=device).argmax(1) == y_train[:5000]).mean())

    out_dir = Path(paths.results_root) / checkpoint_dir_name(a.checkpoint_tag)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{dsname_of(a.dataset)}_ts{ts}.pt"
    meta = {"pipeline": "v3", "dataset": a.dataset, "dsname": dsname_of(a.dataset), "train_seed": ts,
            "arch": arch, "training": tcfg, "split_digest": pool["split_digest"],
            "final_masked_train_acc": float(hist["epoch_acc"][-1]), "full_obs_train_acc": full_acc,
            "feature_costs_by_scheme": {k: np.asarray(v).tolist() for k, v in pool["feature_costs_by_scheme"].items()},
            "created": datetime.now(timezone.utc).isoformat(), "torch_version": torch.__version__}
    if a.checkpoint_tag:                      # round 3: untagged checkpoints keep the round-2 meta keys
        meta["checkpoint_tag"] = a.checkpoint_tag
    torch.save({"state_dict": model.state_dict(), "meta": meta}, out)
    print(f"[train_v3] {a.dataset} ts{ts}: masked_acc={meta['final_masked_train_acc']:.4f} "
          f"full_obs_acc={full_acc:.4f} -> {out} (sha256 {file_sha256(out)[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
