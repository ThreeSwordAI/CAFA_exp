#!/usr/bin/env python
"""v3 -- portable, resumable cell driver for Phases 1 and 3 (Windows-safe; no shell loops).

Cells are datasets x policies x seeds from ``configs/experiment_v3.yaml``
(``datasets_v3`` / ``policies_v3`` / ``protocol_v3.train_seeds``); datasets run in the
priority order of the campaign instructions (cheap, decision-relevant cells first,
Imagenette last).  Each cell runs as a subprocess; its stdout/stderr go to
``results_v3/logs/{phase}_{dsname}_{pol}_ts{ts}.log`` and one JSON line
``{cell, command, start, end, seconds, returncode, output_path}`` is appended to
``results_v3/run_log.jsonl``.  A cell whose output already exists is skipped, so a
rerun resumes; a cell whose prerequisite is missing is skipped with a warning; a
non-zero return code stops the loop.

    python scripts/drive_v3.py --phase backbones --seeds 0 --datasets csv:physionet cube
    python scripts/drive_v3.py --phase rollouts  --seeds 0 --dry-run
    python scripts/drive_v3.py --phase rollouts  --seeds 0 --datasets image:imagenette --extra-args="--batch-size 16"
    python scripts/drive_v3.py --phase commit    --seeds 0
    python scripts/drive_v3.py --phase sweep     --seeds 0
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from commit_v3 import dsname_of  # noqa: E402

PRIORITY = ["csv:physionet", "cube", "tabular:adult", "csv:diabetes", "tabular:MiniBooNE",
            "mnist", "fashionmnist", "image:imagenette"]
SCRIPT = {"backbones": "train_backbone_v3.py", "rollouts": "run_pool_rollout_v3.py",
          "commit": "commit_v3.py", "sweep": "run_cascade_sweep.py"}
TAGS = ("[train_v3]", "[rollout_v3]", "[commit_v3]", "[cascade]", "Traceback", "Error", "ERROR", "epoch")


def cells(cfg: dict, phase: str, seeds, datasets, policies):
    ds_cfg = [d["name"] for d in cfg["datasets_v3"]]
    ds_all = [d for d in PRIORITY if d in ds_cfg] + [d for d in ds_cfg if d not in PRIORITY]
    ds_sel = [d for d in ds_all if not datasets or d in datasets]
    unknown = sorted(set(datasets or []) - set(ds_all))
    if unknown:
        raise SystemExit(f"unknown dataset(s) {unknown}; known: {ds_all}")
    pols = policies or list(cfg["policies_v3"])
    for ts in seeds:
        for ds in ds_sel:
            for pol in (pols if phase in ("rollouts", "sweep") else [None]):
                yield ds, pol, int(ts)


def paths_for(phase: str, ds: str, pol, ts: int, rr: Path, policies=("greedy_entropy", "random")):
    """(output path, list of prerequisite paths) for one cell.  A commit waits for the caches of
    ALL policies (commit_v3 commits every cache present; a policy cache that appears later
    would be missing from the one-time commit)."""
    dn = dsname_of(ds)
    ckpt = rr / "checkpoints_v3" / f"{dn}_ts{ts}.pt"
    cache = lambda p: rr / "pool_v3" / f"{dn}_ts{ts}_{p}_softmax.npz"  # noqa: E731
    committed = REPO / "configs" / f"committed_v3_{dn}_ts{ts}.json"
    if phase == "backbones":
        return ckpt, []
    if phase == "rollouts":
        return cache(pol), [ckpt]
    if phase == "commit":
        return committed, [cache(p) for p in policies]
    return rr / "metrics_v3" / f"{dn}_ts{ts}_{pol}_softmax.json", [committed, cache(pol)]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3 resumable cell driver")
    p.add_argument("--phase", required=True, choices=sorted(SCRIPT))
    p.add_argument("--seeds", nargs="+", type=int, default=None, help="default: protocol_v3.train_seeds")
    p.add_argument("--datasets", nargs="+", default=None)
    p.add_argument("--policies", nargs="+", default=None)
    p.add_argument("--device", default="cuda", help="passed to backbones/rollouts")
    p.add_argument("--extra-args", default="", help='appended to every command, e.g. "--batch-size 16"')
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    p.add_argument("--tag", default="", help='label for smoke runs, e.g. "smoke": logs/{tag}_{phase}_..., cell "{tag}:..."')
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)

    os.chdir(REPO)
    for var in ("DATA_ROOT", "RESULTS_ROOT"):
        if not os.environ.get(var):
            raise SystemExit(f"{var} is not set (source set_env.ps1).")
    rr = Path(os.environ["RESULTS_ROOT"])
    cfg = yaml.safe_load(open(a.config, "r"))
    seeds = a.seeds if a.seeds is not None else cfg["protocol_v3"]["train_seeds"]
    logs = REPO / "results_v3" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    ledger = REPO / "results_v3" / "run_log.jsonl"
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")

    n_run = n_skip = n_prereq = 0
    for ds, pol, ts in cells(cfg, a.phase, seeds, a.datasets, a.policies):
        out, prereqs = paths_for(a.phase, ds, pol, ts, rr, tuple(a.policies or cfg["policies_v3"]))
        cell = (f"{a.tag}:" if a.tag else "") + f"{a.phase}:{ds}:{pol or 'na'}:ts{ts}"
        if out.exists():
            print(f"[drive_v3] skip (exists) {cell} -> {out}")
            n_skip += 1
            continue
        missing = [str(q) for q in prereqs if not q.exists()]
        if missing:
            print(f"[drive_v3] skip (missing prerequisite) {cell}: {missing}")
            n_prereq += 1
            continue
        cmd = [sys.executable, f"scripts/{SCRIPT[a.phase]}", "--dataset", ds, "--train-seed", str(ts)]
        if pol is not None:
            cmd += ["--policy", pol]
        if a.phase in ("backbones", "rollouts"):
            cmd += ["--device", a.device]
        cmd += shlex.split(a.extra_args)
        shown = " ".join(["python"] + [shlex.quote(c) for c in cmd[1:]])
        if a.dry_run:
            print(f"[drive_v3] would run {cell}: {shown}")
            continue
        log_path = logs / ((f"{a.tag}_" if a.tag else "") + f"{a.phase}_{dsname_of(ds)}_{pol or 'na'}_ts{ts}.log")
        print(f"[drive_v3] run {cell}: {shown}  (log {log_path.relative_to(REPO)})", flush=True)
        start, t0 = datetime.now(timezone.utc).isoformat(), time.time()
        with open(log_path, "w", encoding="utf-8") as lf:
            lf.write(f"# {shown}\n# start {start}\n")
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                                    text=True, encoding="utf-8", errors="replace", bufsize=1)
            for line in proc.stdout:
                lf.write(line)
                lf.flush()
                if any(t in line for t in TAGS):
                    print("    " + line.rstrip(), flush=True)
            rc = proc.wait()
            lf.write(f"# returncode {rc}\n")
        end, secs = datetime.now(timezone.utc).isoformat(), round(time.time() - t0, 1)
        rec = {"cell": cell, "command": shown, "start": start, "end": end, "seconds": secs,
               "returncode": rc, "output_path": str(out), "log": str(log_path.relative_to(REPO))}
        with open(ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        n_run += 1
        print(f"[drive_v3] done {cell}: rc={rc} in {secs}s", flush=True)
        if rc != 0:
            print(f"[drive_v3] STOP: non-zero return code in {cell}; see {log_path}", flush=True)
            return rc
    print(f"[drive_v3] {a.phase}: ran {n_run}, skipped {n_skip} existing, {n_prereq} missing prerequisites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
