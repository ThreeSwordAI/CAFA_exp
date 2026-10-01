#!/usr/bin/env python
"""v3 -- markdown tables for handoff.md, generated from files only (torch-free, no large printing).

  --backbones : one row per backbone run in results_v3/run_log.jsonl (phase backbones), with the
                [train_v3] console line of its log (masked / full-observation train accuracy),
                duration, checkpoint path, acceptance target, pass/miss.
  --caches    : one row per pool_v3 cache: n, T, heldout full-acquisition accuracy, duration of the
                rollout from run_log.jsonl, greedy-vs-random equality.
  --commits   : one row per configs/committed_v3_*.json: alpha, floor, G and lambda_ref per key and
                policy, tier-3 start level (answered fraction of the first level in the order).

    python scripts/report_v3.py --backbones --caches --commits
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from cafa.pool import load_pool_cache  # noqa: E402

TARGET = {"mnist": 0.995, "fashionmnist": 0.93, "image-imagenette": 0.95, "tabular-MiniBooNE": 0.93,
          "csv-physionet": 0.86, "csv-diabetes": 0.85, "cube": 0.98, "tabular-adult": 0.85}
_TRAIN = re.compile(r"\[train_v3\] (\S+) ts(\d+): masked_acc=([\d.]+) full_obs_acc=([\d.]+) -> (\S+)")


def ledger():
    p = REPO / "results_v3" / "run_log.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def backbones():
    print("| cell | epochs | masked train acc | full-obs train acc | target | pass | seconds | log |")
    print("|---|---|---|---|---|---|---|---|")
    for r in ledger():
        if ":backbones:" not in f":{r['cell']}" or r["cell"].startswith("smoke"):
            continue
        log = REPO / r["log"].replace("\\", "/")
        m = _TRAIN.search(log.read_text(encoding="utf-8", errors="replace")) if log.exists() else None
        ep = re.search(r"--epochs (\d+)", r["command"])
        if not m:
            print(f"| {r['cell']} | | | | | | {r['seconds']} | `{r['log']}` (rc {r['returncode']}) |")
            continue
        dsn = os.path.basename(m.group(5)).rsplit("_ts", 1)[0]
        full = float(m.group(4))
        tgt = TARGET.get(dsn)
        print(f"| {r['cell']} | {ep.group(1) if ep else 'config'} | {m.group(3)} | {m.group(4)} | {tgt} | "
              f"{'pass' if tgt is not None and full >= tgt else 'miss'} | {r['seconds']} | `{r['log']}` |")


def caches():
    secs = {r["output_path"]: r["seconds"] for r in ledger() if ":rollouts:" in f":{r['cell']}" and not r["cell"].startswith("smoke")}
    pool = Path(os.environ["RESULTS_ROOT"]) / "pool_v3"
    groups = {}
    for f in sorted(pool.glob("*_softmax.npz")):
        dsn, rest = f.name.rsplit("_ts", 1)
        ts, pol = rest[: -len("_softmax.npz")].split("_", 1)
        groups.setdefault((dsn, int(ts)), {})[pol] = f
    print("| dataset | seed | policy | n | T | heldout full-acq acc | rollout seconds | greedy = random (1e-12) | cache |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (dsn, ts), pols in sorted(groups.items()):
        acc = {}
        for pol in sorted(pols):
            c = load_pool_cache(pols[pol])
            acc[pol] = float(np.mean(c["correct"][:, -1]))
            eq = ""
            if pol == "random" and "greedy_entropy" in acc:
                eq = "yes" if abs(acc["greedy_entropy"] - acc["random"]) <= 1e-12 else f"NO ({abs(acc['greedy_entropy'] - acc['random']):.2e})"
            print(f"| {dsn} | {ts} | {pol} | {c['scores'].shape[0]} | {c['order'].shape[1]} | {acc[pol]:.6f} | "
                  f"{secs.get(str(pols[pol]), '')} | {eq} | `pool_v3/{pols[pol].name}` |")


def commits():
    print("| commit | alpha | probe floor | n_cal expected | n_min tier1 | policy | G (0.5 / 0.7 / 0.9 / dep) | lambda_ref dep | tier-3 start (dep, answered frac.) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for f in sorted((REPO / "configs").glob("committed_v3*_ts*.json")):
        d = json.loads(f.read_text())
        for pol in sorted(d["lambda_refs"]):
            G = " / ".join(str(d["edges"][pol][k]["G"]) for k in ("0.5", "0.7", "0.9", "dep"))
            esc = d["escalation"][pol]["dep"]
            start = esc["fractions_desc"][esc["order"][0]] if esc["order"] else None
            print(f"| `{f.name}` | {d['alpha']} | {d['floor']['estimate']} | {d['split']['n_cal_expected']} | "
                  f"{d['edges'][pol]['dep']['n_min_tier1']} | {pol} | {G} | {d['lambda_refs'][pol]['dep']:.4f} | "
                  f"{'' if start is None else f'{start:.3f}'} |")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--backbones", action="store_true")
    p.add_argument("--caches", action="store_true")
    p.add_argument("--commits", action="store_true")
    a = p.parse_args(argv)
    if a.backbones:
        backbones()
    if a.caches:
        caches()
    if a.commits:
        commits()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
