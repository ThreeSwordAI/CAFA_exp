#!/usr/bin/env python
"""v3 -- full-acquisition stratum risk on the calibration pool vs the test split, every metrics JSON.

Reads ``audit[k].r_full`` (calibration pool) and ``full_acq_test_stratum_risk[k]`` (test split) for every
lambda_ref key of every ``{dsname}_ts{ts}_*_softmax.json`` and counts the sign of the difference.

    python scripts/calpool_vs_test_v3.py --train-seed 0 --output results_v3/diagnostics/calpool_vs_test_full_acq_ts0.json
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics-dir", default=None, help="default ${RESULTS_ROOT}/metrics_v3")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--output", required=True)
    a = p.parse_args(argv)
    md = Path(a.metrics_dir or Path(os.environ["RESULTS_ROOT"]) / "metrics_v3")
    rows = []
    for f in sorted(md.glob(f"*_ts{a.train_seed}_*_softmax.json")):
        d = json.loads(f.read_text())
        m = d["meta"]
        for key, b in d["lambda_refs"].items():
            for k, au in b["audit"].items():
                t = b["full_acq_test_stratum_risk"][k]
                rows.append({"dsname": m["dsname"], "policy": m["policy"], "lambda_ref_key": key, "stratum": int(k),
                             "n_k_calpool": au["n_k"], "r_full_calpool": au["r_full"], "r_full_test": t,
                             "test_minus_calpool": t - au["r_full"]})
    cells = sorted({(r["dsname"], r["policy"]) for r in rows})
    out = {"what": "full-acquisition stratum risk on the calibration pool (audit r_full) vs the test split "
                   "(full_acq_test_stratum_risk), all metrics JSONs of the seed", "train_seed": a.train_seed,
           "cells": [list(c) for c in cells], "n": len(rows),
           "n_test_gt_calpool": sum(r["test_minus_calpool"] > 0 for r in rows),
           "n_test_lt_calpool": sum(r["test_minus_calpool"] < 0 for r in rows), "rows": rows}
    Path(a.output).write_text(json.dumps(out, indent=1))
    print(f"[calpool_vs_test] {len(cells)} cells, {out['n']} strata rows: test>calpool {out['n_test_gt_calpool']}, "
          f"test<calpool {out['n_test_lt_calpool']} -> {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
