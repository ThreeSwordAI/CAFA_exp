#!/usr/bin/env python
"""v3 -- build a pool cache from the planted synthetic generator (smoke tests).

Writes ``{pool_dir}/synthetic-planted_ts{ts}_{policy}_softmax.npz`` in the exact
format of :mod:`cafa.pool` so that commit_v3 / run_cascade_sweep / audit scripts
can be exercised end-to-end on CPU in seconds (the v3 "Tier A" check).

    python scripts/make_synthetic_pool_cache.py --pool-dir /tmp/pool_v3 --n 8000 --scenario feasible
    python scripts/make_synthetic_pool_cache.py --pool-dir /tmp/pool_v3 --n 8000 --scenario typeII
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa.pool import save_pool_cache  # noqa: E402
from cafa.synthetic_planted import default_strata, make_planted_population  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pool-dir", required=True)
    p.add_argument("--n", type=int, default=8000)
    p.add_argument("--T", type=int, default=30)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--scenario", choices=["feasible", "typeII", "typeI"], default="feasible")
    p.add_argument("--policies", default="greedy_entropy,random")
    a = p.parse_args(argv)

    strata = default_strata(G=4)
    if a.scenario == "typeII":
        strata[3].update({"r_easy": 0.05, "r_hard": 0.60, "h": 0.35, "s_cap_hard": 0.6})
    elif a.scenario == "typeI":
        strata[3].update({"r_easy": 0.02, "overconfident_from_t": 1})
    pool_dir = Path(a.pool_dir)
    pool_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.train_seed)
    for i, pol in enumerate(a.policies.split(",")):
        pop = make_planted_population(a.n, a.T, strata, seed=10 * a.train_seed + i)
        order = np.stack([rng.permutation(a.T) for _ in range(a.n)]).astype(np.int64)
        meta = {"dataset": "synthetic-planted", "policy": pol, "score": "softmax",
                "train_seed": a.train_seed, "T": a.T, "n": a.n, "scenario": a.scenario,
                "feature_costs_by_scheme": {"uniform": [1.0] * a.T},
                "created": datetime.now(timezone.utc).isoformat()}
        path = pool_dir / f"synthetic-planted_ts{a.train_seed}_{pol}_softmax.npz"
        save_pool_cache(path, scores=pop["scores"], correct=pop["correct"], order=order,
                        y=pop["y"], row_pos=np.arange(a.n), meta=meta)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
