#!/usr/bin/env python
"""v3 -- replay a trained AFABench method on our heldout rows -> frozen order matrix.

RUN THIS INSIDE THE AFABench ENVIRONMENT (``uv run python ...`` from the
AFA-Benchmark checkout; Python 3.12), NOT in the CAFA environment.  It imports
only AFABench + numpy/torch and writes the ``.npz`` consumed by
``scripts/run_pool_rollout_v3.py --orders-file`` (format of
:mod:`cafa.external_orders`; no cafa import needed here).

Inputs
------
``--heldout``  the file written by ``scripts/export_heldout_v3.py`` (our heldout
               features, OUR train-only standardisation);
``--bundle``   a trained AFABench method bundle (``*.bundle`` directory), e.g.
               a GDFS or AACO method trained by AFABench's ``scripts/train_method``
               on the matching dataset.  Train it on OUR train split for a clean
               protocol: ``X_train`` / ``y_train`` are included in the heldout
               file for that purpose (write a small AFADataset wrapper around
               them, or accept the AFABench split and report the mismatch).

Protocol
--------
For every heldout row the method is asked ``T`` times for its next selection;
a stop action (0) is overridden by the first available selection (AFABench's
own hard-budget override), so each row yields a full permutation.  Only the
ORDER is kept; our frozen predictor supplies readiness and correctness later.

    uv run python /path/to/CAFA_exp/scripts/afabench_export_orders.py \
        --heldout orders/physionet_ts0_heldout.npz \
        --bundle extra/output/methods/gdfs/physionet/seed0.bundle \
        --policy afabench_gdfs --out orders/physionet_ts0_afabench_gdfs.npz

VALIDATE in the AFABench env before trusting the output: the API below follows
afabench/core/types.py (AFAMethod.act: 1-indexed selection, 0 = stop) and
afabench/core/bundle_system/bundle.py (load_bundle) at commit 8ebf5e9; check
the signatures if the benchmark has moved.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch


def override_stop(action: torch.Tensor, selection_mask: torch.Tensor) -> torch.Tensor:
    first_free = (~selection_mask).int().argmax(dim=1)
    stop = (action == 0).squeeze(-1)
    out = action.clone()
    out[stop] = (first_free[stop] + 1).unsqueeze(-1)
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--heldout", required=True)
    p.add_argument("--bundle", required=True)
    p.add_argument("--policy", required=True, help="cache token, e.g. afabench_gdfs / afabench_aaco")
    p.add_argument("--out", required=True)
    p.add_argument("--device", default="cpu")
    p.add_argument("--batch-size", type=int, default=256)
    a = p.parse_args(argv)

    from afabench.core.bundle_system.bundle import load_bundle  # type: ignore

    z = np.load(a.heldout, allow_pickle=False)
    X = torch.as_tensor(z["X_heldout"], dtype=torch.float32)
    meta = json.loads(str(z["meta_json"]))
    n, d = X.shape
    device = torch.device(a.device)
    method, manifest = load_bundle(Path(a.bundle), device=device)
    if hasattr(method, "force_acquisition"):
        method.force_acquisition = True
    method.set_seed(0)

    orders = np.zeros((n, d), dtype=np.int64)
    feature_shape = torch.Size([d])
    for start in range(0, n, a.batch_size):
        stop = min(start + a.batch_size, n)
        xb = X[start:stop].to(device)
        B = xb.shape[0]
        feature_mask = torch.zeros((B, d), dtype=torch.bool, device=device)
        selection_mask = torch.zeros((B, d), dtype=torch.bool, device=device)
        for t in range(d):
            masked = xb * feature_mask.float()
            with torch.no_grad():
                action = method.act(masked, feature_mask, selection_mask, label=None, feature_shape=feature_shape)
            action = override_stop(action.view(B, 1).to(device), selection_mask)
            sel = (action.view(B) - 1).long()
            assert not selection_mask[torch.arange(B, device=device), sel].any(), "method re-selected a feature"
            orders[start:stop, t] = sel.cpu().numpy()
            feature_mask[torch.arange(B, device=device), sel] = True
            selection_mask[torch.arange(B, device=device), sel] = True
        print(f"  {stop}/{n}", flush=True)

    sorted_rows = np.sort(orders, axis=1)
    assert np.array_equal(sorted_rows, np.tile(np.arange(d), (n, 1))), "orders are not permutations"
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, orders=orders, policy=str(a.policy), dataset=str(meta["dataset"]),
                        heldout_digest=str(z["heldout_digest"]),
                        meta_json=json.dumps({"bundle": str(a.bundle), "manifest": manifest,
                                              "train_seed": meta["train_seed"]}, default=str))
    print(f"wrote {out}: orders {orders.shape}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
