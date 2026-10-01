#!/usr/bin/env python
"""v3 -- exact Bayes accuracy of the CUBE generator (explains the CUBE full-observation target miss).

The class-conditional law of ``cafa.data_v3.generate_cube`` is known: cube positions ``y, y+1, y+2`` are
N(code_y, 0.1) and every other feature N(0.5, 0.3); classes are uniform.  The Bayes classifier is the
argmax of the Gaussian log-likelihoods; its accuracy on the generated rows bounds what any backbone
can reach.

    python scripts/cube_bayes_v3.py --output results_v3/diagnostics/cube_bayes_accuracy.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cafa.data_v3 import generate_cube  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--n-samples", type=int, default=20000)
    p.add_argument("--seed", type=int, default=123)
    p.add_argument("--output", required=True)
    a = p.parse_args(argv)
    X, y = generate_cube(a.n_samples, a.seed)
    codes = np.array([[int(b) for b in format(i, "03b")][::-1] for i in range(8)], float)
    ll = np.zeros((X.shape[0], 8))
    for c in range(8):
        mu, sd = np.full(20, 0.5), np.full(20, 0.3)
        mu[[c, c + 1, c + 2]], sd[[c, c + 1, c + 2]] = codes[c], 0.1
        ll[:, c] = norm.logpdf(X, mu, sd).sum(1)
    acc = float((ll.argmax(1) == y).mean())
    out = {"what": "exact Bayes classifier of cafa.data_v3.generate_cube (class-conditional Gaussian likelihoods, "
                   "uniform prior) on all generated rows", "n_samples": a.n_samples, "seed": a.seed,
           "bayes_accuracy": acc, "bayes_error": 1 - acc, "target_full_obs_acc": 0.98}
    Path(a.output).write_text(json.dumps(out, indent=1))
    print(f"[cube_bayes] Bayes accuracy {acc:.5f} -> {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
