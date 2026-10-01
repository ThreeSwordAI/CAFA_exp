#!/usr/bin/env python
"""v3 -- calibration-pool vs test-split balance of one pool cache (torch-free, small output).

Reports, for the fixed v3 split of a cache: overall full-acquisition error on calpool and test,
the class counts of each, and the per-class full-acquisition error, with a two-proportion z
statistic for the overall error difference.  Used to explain cells whose test stratum risks sit
systematically above their calibration-pool risks (instruction 4.4 diagnosis).

    python scripts/split_balance_v3.py --dataset fashionmnist --policy greedy_entropy --train-seed 0 --output results_v3/diagnostics/fashionmnist_ts0_split_balance.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))
from cafa.pool import load_pool_cache  # noqa: E402
from cafa.splits_v3 import v3_positions  # noqa: E402
from commit_v3 import dsname_of  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--policy", default="greedy_entropy")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--output", default=None)
    a = p.parse_args(argv)
    dsn = dsname_of(a.dataset)
    c = load_pool_cache(Path(os.environ["RESULTS_ROOT"]) / "pool_v3" / f"{dsn}_ts{a.train_seed}_{a.policy}_softmax.npz")
    err = 1.0 - np.asarray(c["correct"])[:, -1]
    y = np.asarray(c["y"]).astype(int)
    pos = v3_positions(err.size)
    out = {"dataset": a.dataset, "policy": a.policy, "train_seed": a.train_seed, "splits": {}}
    for nm in ("calpool", "test"):
        ix = pos[nm]
        classes = np.unique(y)
        out["splits"][nm] = {"n": int(ix.size), "full_acq_error": float(err[ix].mean()),
                             "class_counts": {int(k): int((y[ix] == k).sum()) for k in classes},
                             "class_full_acq_error": {int(k): float(err[ix][y[ix] == k].mean()) for k in classes}}
    e1, n1 = out["splits"]["calpool"]["full_acq_error"], out["splits"]["calpool"]["n"]
    e2, n2 = out["splits"]["test"]["full_acq_error"], out["splits"]["test"]["n"]
    pp = (e1 * n1 + e2 * n2) / (n1 + n2)
    out["z_test_minus_calpool"] = float((e2 - e1) / np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2)))
    print(f"[balance] {dsn} ts{a.train_seed} {a.policy}: full-acq error calpool {e1:.4f} (n {n1}) test {e2:.4f} (n {n2}) "
          f"z={out['z_test_minus_calpool']:+.2f}")
    for k in out["splits"]["test"]["class_counts"]:
        cc, tt = out["splits"]["calpool"], out["splits"]["test"]
        print(f"  class {k}: n calpool {cc['class_counts'][k]} test {tt['class_counts'][k]} | error calpool "
              f"{cc['class_full_acq_error'][k]:.4f} test {tt['class_full_acq_error'][k]:.4f}")
    if a.output:
        Path(a.output).write_text(json.dumps(out, indent=1))
        print(f"[balance] wrote {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
