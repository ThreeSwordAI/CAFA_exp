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

Round-2 options (reruns and ablations go through the same ledger):
  --force                 commit phase: re-commit even if the committed JSON exists (passes --force; the
                          reason goes into handoff.md, instruction rule 4)
  --metrics-dir-name D    sweep phase: write to ${RESULTS_ROOT}/D instead of metrics_v3 (passes --out-dir)
  --commit-prefix P       commit / sweep phase: committed JSON configs/P_{dsname}_ts{ts}.json instead of
                          committed_v3_... (passes --out-path to commit_v3, --committed to the sweep)
  --tag T                 labels the run: logs/T_{phase}_..., ledger cell "T:..." (smoke runs, round-2 reruns)

Round-3 option (Task L, a second backbone of the same (dataset, seed) next to the protocol one):
  --checkpoint-tag TAG    backbones / rollouts phase only (the commit and sweep phases REJECT it: a tagged cache
                          is never committed or swept; it enters only the E7 repair, run_repairs_v3.py --repair-tag).
                          The checkpoint is ${RESULTS_ROOT}/checkpoints_v3_TAG/{dsname}_ts{ts}.pt and the cache
                          pool_v3/{dsname}_ts{ts}_{policy}-TAG_{score}.npz (helpers below, shared with
                          train_backbone_v3 / run_pool_rollout_v3 / check_caches_v3 / run_repairs_v3); the flag is
                          passed through to the script, and the ledger cell / log name carry "{policy or na}-TAG".
                          TAG: letters, digits, underscore; an empty TAG is a usage error (omit the flag for the
                          untagged protocol paths).  The dry run also prints the tagged output path.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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


# --------------------------------------------------------------------------- #
# Checkpoint-tag rules (round 3, Task L).  A tag changes ONLY the checkpoint folder and the cache token suffix;
# no tag = the protocol paths, unchanged.  Torch-free, imported by the training / rollout / check / repair scripts.
# --------------------------------------------------------------------------- #
TAG_SEP = "-"                                   # never part of an untagged policy token (eps_greedy_eps0.25, ...)
_TAG_RE = re.compile(r"[A-Za-z0-9_]+")        # used with fullmatch ("$" would accept a trailing newline)


def validate_checkpoint_tag(tag):
    """``None`` / ``""`` -> ``None`` (untagged); a valid tag is returned unchanged; anything else -> ValueError."""
    if tag is None or tag == "":
        return None
    if not _TAG_RE.fullmatch(str(tag)):
        raise ValueError(f"invalid checkpoint tag {tag!r}: letters, digits and underscore only.")
    return str(tag)


def checkpoint_tag_arg(s: str) -> str:
    """argparse ``type=`` for ``--checkpoint-tag`` / ``--repair-tag`` (a clear usage error on a bad tag).

    An explicitly given EMPTY tag is a usage error too (e.g. ``--checkpoint-tag "$TAG"`` with ``TAG`` unset): only an
    omitted flag means the untagged protocol paths.  Internal callers keep ``validate_checkpoint_tag(None) -> None``."""
    if s == "":
        raise argparse.ArgumentTypeError("empty tag: omit the flag for the untagged protocol paths")
    try:
        return validate_checkpoint_tag(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e)) from None


def checkpoint_dir_name(tag=None) -> str:
    """``checkpoints_v3`` (untagged) or ``checkpoints_v3_{tag}``."""
    tag = validate_checkpoint_tag(tag)
    return "checkpoints_v3" if tag is None else f"checkpoints_v3_{tag}"


def checkpoint_path(results_root, dsname: str, ts: int, tag=None) -> Path:
    return Path(results_root) / checkpoint_dir_name(tag) / f"{dsname}_ts{int(ts)}.pt"


def tagged_policy_token(policy_token: str, tag=None) -> str:
    """Cache token: ``{policy_token}`` (untagged) or ``{policy_token}-{tag}``."""
    tag = validate_checkpoint_tag(tag)
    return policy_token if tag is None else f"{policy_token}{TAG_SEP}{tag}"


def split_policy_token(token: str):
    """Inverse of :func:`tagged_policy_token`: ``(policy_token, tag or None)``."""
    base, sep, tag = str(token).rpartition(TAG_SEP)
    return (base, tag) if sep else (str(token), None)


def pool_cache_path(results_root, dsname: str, ts: int, policy_token: str, score: str = "softmax", tag=None) -> Path:
    return Path(results_root) / "pool_v3" / f"{dsname}_ts{int(ts)}_{tagged_policy_token(policy_token, tag)}_{score}.npz"


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


def paths_for(phase: str, ds: str, pol, ts: int, rr: Path, policies=("greedy_entropy", "random"),
              metrics_dir_name: str = "metrics_v3", commit_prefix: str = "committed_v3", checkpoint_tag=None):
    """(output path, list of prerequisite paths) for one cell.  A commit waits for the caches of
    ALL policies (commit_v3 commits every cache present; a policy cache that appears later
    would be missing from the one-time commit).  ``checkpoint_tag`` (backbones / rollouts only):
    the tagged checkpoint folder and cache token."""
    dn = dsname_of(ds)
    ckpt = checkpoint_path(rr, dn, ts, checkpoint_tag)
    cache = lambda p: pool_cache_path(rr, dn, ts, p, "softmax", checkpoint_tag)  # noqa: E731
    committed = REPO / "configs" / f"{commit_prefix}_{dn}_ts{ts}.json"
    if phase == "backbones":
        return ckpt, []
    if phase == "rollouts":
        return cache(pol), [ckpt]
    if phase == "commit":
        return committed, [cache(p) for p in policies]
    return rr / metrics_dir_name / f"{dn}_ts{ts}_{pol}_softmax.json", [committed, cache(pol)]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3 resumable cell driver")
    p.add_argument("--phase", required=True, choices=sorted(SCRIPT))
    p.add_argument("--seeds", nargs="+", type=int, default=None, help="default: protocol_v3.train_seeds")
    p.add_argument("--datasets", nargs="+", default=None)
    p.add_argument("--policies", nargs="+", default=None)
    p.add_argument("--device", default="cuda", help="passed to backbones/rollouts")
    p.add_argument("--extra-args", default="", help='appended to every command, e.g. "--batch-size 16"')
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    p.add_argument("--tag", default="", help='run label, e.g. "smoke" or "r2": logs/{tag}_{phase}_..., cell "{tag}:..."')
    p.add_argument("--force", action="store_true", help="commit phase: re-commit existing JSONs (passes --force)")
    p.add_argument("--metrics-dir-name", default="metrics_v3", help="sweep phase: output dir under RESULTS_ROOT")
    p.add_argument("--commit-prefix", default="committed_v3",
                   help="commit/sweep phase: configs/{prefix}_{dsname}_ts{ts}.json (ablation commits)")
    p.add_argument("--checkpoint-tag", type=checkpoint_tag_arg, default=None,
                   help="backbones/rollouts phase: checkpoints_v3_TAG and cache token {policy}-TAG (round 3, Task L)")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    ctag = a.checkpoint_tag
    if ctag and a.phase not in ("backbones", "rollouts"):
        p.error(f"--checkpoint-tag applies to the backbones and rollouts phases only (got --phase {a.phase}); "
                "tagged caches enter the E7 repair via run_repairs_v3.py --repair-tag")

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
        out, prereqs = paths_for(a.phase, ds, pol, ts, rr, tuple(a.policies or cfg["policies_v3"]),
                                 a.metrics_dir_name, a.commit_prefix, ctag)
        pol_label = tagged_policy_token(pol or "na", ctag)        # "na" / policy, + "-TAG" for a tagged backbone
        cell = (f"{a.tag}:" if a.tag else "") + f"{a.phase}:{ds}:{pol_label}:ts{ts}"
        if out.exists() and not (a.force and a.phase == "commit"):
            print(f"[drive_v3] skip (exists) {cell} -> {out}")
            n_skip += 1
            continue
        missing = [str(q) for q in prereqs if not q.exists()]
        if missing and not a.dry_run:
            print(f"[drive_v3] skip (missing prerequisite) {cell}: {missing}")
            n_prereq += 1
            continue
        cmd = [sys.executable, f"scripts/{SCRIPT[a.phase]}", "--dataset", ds, "--train-seed", str(ts)]
        if pol is not None:
            cmd += ["--policy", pol]
        if a.phase in ("backbones", "rollouts"):
            cmd += ["--device", a.device]
            if ctag:
                cmd += ["--checkpoint-tag", ctag]
        if a.phase == "commit":
            if a.force:
                cmd += ["--force"]
            if a.commit_prefix != "committed_v3":
                cmd += ["--out-path", str(out.relative_to(REPO)).replace("\\", "/")]
        if a.phase == "sweep":
            if a.metrics_dir_name != "metrics_v3":
                cmd += ["--out-dir", str(out.parent).replace("\\", "/")]
            if a.commit_prefix != "committed_v3":
                cmd += ["--committed", str(prereqs[0].relative_to(REPO)).replace("\\", "/")]
        cmd += shlex.split(a.extra_args)
        shown = " ".join(["python"] + [shlex.quote(c) for c in cmd[1:]])
        if a.dry_run:
            # round 2: show the command even when a prerequisite is missing now (e.g. the cluster dry run of
            # seeds 1-2, whose checkpoints do not exist on this machine), and say what is missing
            # round 3: a tagged cell also names the folders (checkpoints_v3_TAG/...) and its output path
            name = (lambda q: f"{Path(q).parent.name}/{Path(q).name}") if ctag else (lambda q: Path(q).name)
            note = f"  [prerequisite missing now: {', '.join(name(m) for m in missing)}]" if missing else ""
            note += f"  [output: {out}]" if ctag else ""
            print(f"[drive_v3] would run {cell}: {shown}{note}")
            n_prereq += bool(missing)
            continue
        log_path = logs / ((f"{a.tag}_" if a.tag else "") + f"{a.phase}_{dsname_of(ds)}_{pol_label}_ts{ts}.log")
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
