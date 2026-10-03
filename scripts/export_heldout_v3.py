#!/usr/bin/env python
"""v3 -- export the heldout feature matrix for an EXTERNAL policy environment.

Writes ``{out}``: ``X_heldout`` float32 ``[n, d]`` (tabular, our encoding),
``y_heldout``, ``heldout_digest`` and ``feature_names`` so that
``scripts/afabench_export_orders.py`` (run inside the AFABench environment) can
replay a trained AFABench method on exactly our heldout rows and return a
frozen order matrix for ``run_pool_rollout_v3.py --orders-file``.

    python scripts/export_heldout_v3.py --dataset csv:physionet --train-seed 0
        # -> ${RESULTS_ROOT}/orders_v3/csv-physionet_ts0_heldout.npz (default; feature arrays stay out of the repo)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402
from cafa.data_v3 import dataset_kind, load_pool_v3  # noqa: E402
from cafa.splits import split_digest  # noqa: E402


def default_out(dataset: str, train_seed: int) -> Path:
    """``${RESULTS_ROOT}/orders_v3/{dsname}_ts{ts}_heldout.npz`` (outside the repo: the file holds feature arrays)."""
    dsname = dataset
    for prefix in ("tabular:", "csv:", "image:"):
        if dataset.startswith(prefix):
            dsname = prefix[:-1] + "-" + dataset.split(":", 1)[1]
    return Path(config.load_paths().results_root) / "orders_v3" / f"{dsname}_ts{int(train_seed)}_heldout.npz"


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--out", default=None, help="default ${RESULTS_ROOT}/orders_v3/{dsname}_ts{ts}_heldout.npz")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    a = p.parse_args(argv)
    cfg = config.load_experiment(a.config)
    kind = dataset_kind(a.dataset)
    if kind not in ("tabular_openml", "tabular_csv", "synthetic_cube"):
        raise SystemExit("external policies are integrated for tabular datasets only")
    pool = load_pool_v3(a.dataset, cfg, train_seed=a.train_seed)
    X, y = pool["heldout"]
    Xtr, ytr = pool["train"]
    out = Path(a.out) if a.out else default_out(a.dataset, a.train_seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, X_heldout=X.astype(np.float32), y_heldout=y.astype(np.int64),
                        X_train=Xtr.astype(np.float32), y_train=ytr.astype(np.int64),
                        heldout_digest=split_digest(pool["heldout_index"]),
                        meta_json=json.dumps({"dataset": a.dataset, "train_seed": int(a.train_seed),
                                              "n_features": int(pool["n_features"]),
                                              "n_classes": int(pool["n_classes"]),
                                              "split_digest": pool["split_digest"]}))
    print(f"wrote {out}: X_heldout {X.shape}, X_train {Xtr.shape}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
