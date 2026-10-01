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


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--device", default="cpu")
    p.add_argument("--download", action="store_true")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    p.add_argument("--epochs", type=int, default=None, help="override the config epochs (smoke tests)")
    p.add_argument("--max-train", type=int, default=None, help="subsample the train split (smoke tests)")
    a = p.parse_args(argv)

    cfg = config.load_experiment(a.config)
    paths = config.load_paths()
    ts = int(a.train_seed)
    kind = dataset_kind(a.dataset)
    tcfg = dict(cfg.get("training_v3", {}).get("tabular" if kind.startswith(("tabular", "synthetic")) else kind, {}))
    if a.epochs is not None:
        tcfg["epochs"] = int(a.epochs)
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

    out_dir = Path(paths.results_root) / "checkpoints_v3"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{dsname_of(a.dataset)}_ts{ts}.pt"
    meta = {"pipeline": "v3", "dataset": a.dataset, "dsname": dsname_of(a.dataset), "train_seed": ts,
            "arch": arch, "training": tcfg, "split_digest": pool["split_digest"],
            "final_masked_train_acc": float(hist["epoch_acc"][-1]), "full_obs_train_acc": full_acc,
            "feature_costs_by_scheme": {k: np.asarray(v).tolist() for k, v in pool["feature_costs_by_scheme"].items()},
            "created": datetime.now(timezone.utc).isoformat(), "torch_version": torch.__version__}
    torch.save({"state_dict": model.state_dict(), "meta": meta}, out)
    print(f"[train_v3] {a.dataset} ts{ts}: masked_acc={meta['final_masked_train_acc']:.4f} "
          f"full_obs_acc={full_acc:.4f} -> {out} (sha256 {file_sha256(out)[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
