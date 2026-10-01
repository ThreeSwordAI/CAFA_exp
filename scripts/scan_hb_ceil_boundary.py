#!/usr/bin/env python
"""Prevalence of the ceil(n * r_hat) off-by-one in the frozen Hoeffding-Bentkus p-value (diagnostic only).

For every n in a grid and every error count k with k/n < alpha, compute r_hat the two ways the code
base does -- ``mean(loss)`` (= sum/n, used by ltt_select / iut on loss matrices) and
``1 - mean(correct)`` (used by cafa.cascade.selective_pvalues, tier 3) -- and count how often
``ceil(n * r_hat) != k`` and how often the frozen p-value then differs from the exact-count p-value
by more than 1 % (relative).  Nothing in the frozen file is changed; the exact value is recomputed here.

    python scripts/scan_hb_ceil_boundary.py --output results_v3/diagnostics/hb_ceil_boundary_scan.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cafa.risk_control import hoeffding_bentkus_pvalue  # noqa: E402


def exact(k: int, n: int, alpha: float) -> float:
    r = k / n
    kl = (r * math.log(r / alpha) if r > 0 else 0.0) + (1 - r) * math.log((1 - r) / (1 - alpha))
    return max(min(1.0, math.exp(-n * kl), math.e * float(binom.cdf(k, n, alpha))), 1e-300)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--alphas", default="0.10,0.15,0.20,0.25")
    p.add_argument("--n-values", default="50,100,197,250,500,1000,2000,3000,5000")
    p.add_argument("--output", default=None)
    a = p.parse_args(argv)
    out = {"what": "off-by-one of ceil(n*r_hat) in risk_control._hb_pvalue_array", "rows": []}
    for alpha in [float(x) for x in a.alphas.split(",")]:
        for n in [int(x) for x in a.n_values.split(",")]:
            ks = [k for k in range(0, n) if k / n < alpha]
            rec = {"alpha": alpha, "n": n, "n_k": len(ks)}
            for name in ("mean_loss", "one_minus_mean_correct"):
                off, big = 0, 0
                for k in ks:
                    v = np.zeros(n)
                    if name == "mean_loss":
                        v[:k] = 1.0
                        r = float(v.mean())
                    else:
                        v[k:] = 1.0
                        r = 1.0 - float(v.mean())
                    if math.ceil(n * r) != k:
                        off += 1
                        pe, pf = exact(k, n, alpha), hoeffding_bentkus_pvalue(r, n, alpha)
                        if abs(pf - pe) > 0.01 * pe:
                            big += 1
                rec[name] = {"ceil_off_by_one": off, "p_differs_gt_1pct": big}
            out["rows"].append(rec)
            print(f"alpha={alpha:.2f} n={n:5d} k-values={len(ks):5d} | mean(loss): off-by-one {rec['mean_loss']['ceil_off_by_one']:4d}"
                  f" (p differs >1%: {rec['mean_loss']['p_differs_gt_1pct']:4d}) | 1-mean(correct): off-by-one "
                  f"{rec['one_minus_mean_correct']['ceil_off_by_one']:4d} (p differs >1%: {rec['one_minus_mean_correct']['p_differs_gt_1pct']:4d})")
    tot = {nm: {kk: sum(r[nm][kk] for r in out["rows"]) for kk in ("ceil_off_by_one", "p_differs_gt_1pct")}
           for nm in ("mean_loss", "one_minus_mean_correct")}
    out["totals"] = dict(tot, n_pairs=sum(r["n_k"] for r in out["rows"]))
    print("totals:", out["totals"])
    if a.output:
        Path(a.output).write_text(json.dumps(out, indent=1))
        print(f"wrote {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
