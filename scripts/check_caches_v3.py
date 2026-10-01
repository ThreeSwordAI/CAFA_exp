#!/usr/bin/env python
"""v3 -- Phase-1 acceptance summary of the pool caches (torch-free; no large printing).

For every (dsname, train_seed) with caches in ``${RESULTS_ROOT}/pool_v3`` it prints one
line per policy (n, T, full-acquisition accuracy on heldout, checkpoint sha256 prefix,
heldout digest) and checks that the greedy and random caches of the same cell give the
same full-acquisition accuracy to 1e-12 (same predictor, same final observed set) and
identical ``correct[:, T]`` / ``y`` vectors.  With ``--v2-dir`` it also checks that the
v3 cache covers the same heldout rows in the same order as the v2 cache (``y`` equal,
same n) -- the E7 prerequisite.  Optionally writes a CSV.

    python scripts/check_caches_v3.py
    python scripts/check_caches_v3.py --v2-dir F:/CAFA_results/pool_v2 --csv results_v3/phase1_caches.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cafa.pool import load_pool_cache  # noqa: E402

_PAT = re.compile(r"^(?P<ds>.+)_ts(?P<ts>\d+)_(?P<pol>.+)_(?P<score>softmax|margin)\.npz$")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pool-dir", default=None, help="default ${RESULTS_ROOT}/pool_v3")
    p.add_argument("--v2-dir", default=None, help="v2 pool dir for the same-rows check (E7)")
    p.add_argument("--csv", default=None)
    a = p.parse_args(argv)
    pool_dir = Path(a.pool_dir or Path(os.environ["RESULTS_ROOT"]) / "pool_v3")
    groups: dict = {}
    for f in sorted(pool_dir.glob("*.npz")):
        m = _PAT.match(f.name)
        if m:
            groups.setdefault((m["ds"], int(m["ts"]), m["score"]), {})[m["pol"]] = f
    rows, ok_all = [], True
    for (ds, ts, score), pols in sorted(groups.items()):
        loaded = {pol: load_pool_cache(path) for pol, path in pols.items()}
        accs = {}
        for pol, c in loaded.items():
            T = int(c["correct"].shape[1] - 1)
            acc = float(np.mean(c["correct"][:, T]))
            accs[pol] = acc
            meta = c["meta"]
            row = {"dsname": ds, "train_seed": ts, "policy": pol, "score": score, "n": int(c["scores"].shape[0]),
                   "T": T, "full_acq_acc": acc, "acc_depth0": float(np.mean(c["correct"][:, 0])),
                   "checkpoint_sha256": str(meta.get("checkpoint_sha256", ""))[:12],
                   "heldout_digest": str(meta.get("heldout_digest", ""))[:12], "path": str(pols[pol])}
            rows.append(row)
            print(f"[check_v3] {ds} ts{ts} {pol:>15s}: n={row['n']} T={T} full-acq acc={acc:.6f} "
                  f"depth0 acc={row['acc_depth0']:.4f} ckpt={row['checkpoint_sha256']}")
        if "greedy_entropy" in loaded and "random" in loaded:
            g, r = loaded["greedy_entropy"], loaded["random"]
            same_y = bool(np.array_equal(g["y"], r["y"]))
            same_c = bool(np.array_equal(g["correct"][:, -1], r["correct"][:, -1]))
            diff = abs(accs["greedy_entropy"] - accs["random"])
            ok = same_y and diff <= 1e-12
            ok_all &= ok
            print(f"[check_v3] {ds} ts{ts}: greedy vs random |d full-acq acc|={diff:.3e} same_y={same_y} "
                  f"same_correct_T={same_c} -> {'PASS' if ok else 'FAIL'}")
        if a.v2_dir and "greedy_entropy" in loaded:
            v2p = Path(a.v2_dir) / f"{ds}_ts{ts}_greedy_entropy_{score}.npz"
            if v2p.exists():
                v2 = load_pool_cache(v2p)
                g = loaded["greedy_entropy"]
                same = v2["y"].shape == g["y"].shape and bool(np.array_equal(v2["y"], g["y"]))
                # the split digests (sha256 of the train / probe / eval index sets) identify the rows
                same_split = v2["meta"].get("split_digest") == g["meta"].get("split_digest")
                ok_all &= same and same_split
                print(f"[check_v3] {ds} ts{ts}: v2 vs v3 heldout rows n_v2={v2['y'].shape[0]} "
                      f"n_v3={g['y'].shape[0]} same_y_order={same} same_split_digest={same_split} | v2 full-acq acc="
                      f"{float(np.mean(v2['correct'][:, -1])):.6f}")
    if a.csv:
        Path(a.csv).parent.mkdir(parents=True, exist_ok=True)
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["dsname"])
            w.writeheader()
            w.writerows(rows)
        print(f"[check_v3] wrote {a.csv}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
