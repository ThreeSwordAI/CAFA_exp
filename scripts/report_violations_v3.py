#!/usr/bin/env python
"""v3 round 2 -- per-cell violation report over the multi-split protocol (torch-free; for handoff.md).

For every metrics JSON in ``--metrics-dir`` and one lambda_ref key / cost scheme: certified deployment, the
raw test stratum-violation rate pooled and per split, the certified-violation rate pooled and per split,
and ``max_excess_se`` (mean, q90, per-split means), plus the Task-C acceptance checks
(certified deployment ~ 1.00; certified violation <= delta + 0.05; mean max_excess_se <= 0).  Cells listed
with ``--focus`` (e.g. the cells that were over delta in round 1) are flagged.

    python scripts/report_violations_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 --lambda-ref-key dep \
        --focus fashionmnist:greedy_entropy fashionmnist:random tabular-MiniBooNE:greedy_entropy tabular-MiniBooNE:random \
        --output results_v3/diagnostics/r2_violations_dep.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def f3(v):
    return "" if v is None else f"{v:.3f}"


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics-dir", required=True)
    p.add_argument("--lambda-ref-key", default="dep")
    p.add_argument("--scheme", default="uniform")
    p.add_argument("--focus", nargs="*", default=[], help="dsname:policy cells to flag")
    p.add_argument("--output", default=None)
    a = p.parse_args(argv)
    focus = set(a.focus)
    rows, fails = [], []
    hdr = ("| cell | focus | cert. deployment | raw viol pooled | raw by split | certified viol | certified by split "
           "| max_excess_se mean | q90 | by split (means) | certified ≤ δ+0.05 | mean excess ≤ 0 |")
    lines = [hdr, "|" + "---|" * 12]
    for jp in sorted(Path(a.metrics_dir).glob("*.json")):
        d = json.loads(jp.read_text())
        m = d["meta"]
        blk = d["lambda_refs"].get(a.lambda_ref_key)
        if blk is None or a.scheme not in blk["schemes"]:
            continue
        s = blk["schemes"][a.scheme]["summary"]
        if "by_split" not in s:
            continue
        cell = f"{m['dsname']}:{m['policy']}:ts{m['train_seed']}"
        bs = s["by_split"]
        raw = [bs[k]["cascade_violation_rate"] for k in sorted(bs)]
        cer = [bs[k]["cascade_certified_violation_rate"] for k in sorted(bs)]
        exs = [bs[k]["cascade_max_excess_se_mean"] for k in sorted(bs)]
        ok_c = s["cascade_certified_violation_rate"] <= d["delta"] + 0.05 + 1e-12
        ok_e = s["cascade_max_excess_se_mean"] is None or s["cascade_max_excess_se_mean"] <= 0
        if not ok_c or not ok_e:
            fails.append(cell)
        rows.append({"cell": cell, "certified_deployment": s["certified_deployment_rate"],
                     "raw": s["cascade_violation_rate"], "raw_by_split": dict(zip(sorted(bs), raw)),
                     "certified": s["cascade_certified_violation_rate"], "certified_by_split": dict(zip(sorted(bs), cer)),
                     "max_excess_se_mean": s["cascade_max_excess_se_mean"], "max_excess_se_q90": s["cascade_max_excess_se_q90"],
                     "max_excess_se_by_split": dict(zip(sorted(bs), exs)), "ok_certified": ok_c, "ok_excess": ok_e})
        is_focus = "yes" if f"{m['dsname']}:{m['policy']}" in focus else ""
        lines.append(f"| {cell} | {is_focus} | {s['certified_deployment_rate']:.2f} | "
                     f"{s['cascade_violation_rate']:.3f} | {' '.join(f3(x) for x in raw)} | {s['cascade_certified_violation_rate']:.3f} | "
                     f"{' '.join(f3(x) for x in cer)} | {f3(s['cascade_max_excess_se_mean'])} | {f3(s['cascade_max_excess_se_q90'])} | "
                     f"{' '.join(f3(x) for x in exs)} | {'pass' if ok_c else 'FAIL'} | {'pass' if ok_e else 'FAIL'} |")
    text = (f"Metrics: {a.metrics_dir}; lambda_ref key {a.lambda_ref_key}; scheme {a.scheme}; by-split columns in test-seed "
            f"order {sorted(bs) if rows else []}.\n\n" + "\n".join(lines) +
            f"\n\nCells failing an acceptance check: {', '.join(fails) if fails else 'none'}\n")
    print(text)
    if a.output:
        out = Path(a.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("# Violation report (round 2)\n\n" + text, encoding="utf-8")
        out.with_suffix(".json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
