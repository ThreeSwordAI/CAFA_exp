#!/usr/bin/env python
"""v3 -- run the E7 audit-guided repairs for one or more seeds, with the driver's ledger (torch-free).

Pairs (as in round 1, handoff.md section 10 step 5):
  * predictor_upgrade  BEFORE = AAAI v2 greedy cache + its v2-based commit ``configs/committed_v3before_{ds}_ts{ts}.json``;
                       AFTER = the v3 greedy cache on the BEFORE strata.  Only datasets with a v2 cache
                       (mnist, tabular:MiniBooNE, tabular:adult).
  * policy_change      BEFORE = the v3 random cache on the main commit (``--policy random``); AFTER = the v3 greedy
                       cache.  Every dataset whose two v3 caches and main commit exist.

Each run writes ``results_v3/repair/{dsname}_ts{ts}_{label}.json`` (skipped if present unless ``--force``), logs to
``results_v3/logs/{tag}_repair_{dsname}_{label}_ts{ts}.log`` and appends one ledger line to ``results_v3/run_log.jsonl``.

    python scripts/run_repairs_v3.py --seeds 0 --tag r2 --force
    python scripts/run_repairs_v3.py --seeds 1 2 --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from commit_v3 import dsname_of  # noqa: E402
from drive_v3 import PRIORITY  # noqa: E402

UPGRADE = ("mnist", "tabular:MiniBooNE", "tabular:adult")


def jobs(seeds, datasets, labels, rr: Path):
    for ts in seeds:
        for ds in datasets:
            dn = dsname_of(ds)
            pool = lambda d, p: rr / d / f"{dn}_ts{ts}_{p}_softmax.npz"  # noqa: E731
            if "predictor_upgrade" in labels and ds in UPGRADE:
                yield ds, ts, "predictor_upgrade", [
                    "--before-cache", pool("pool_v2", "greedy_entropy"), "--after-cache", pool("pool_v3", "greedy_entropy"),
                    "--committed", Path("configs") / f"committed_v3before_{dn}_ts{ts}.json"]
            if "policy_change" in labels:
                yield ds, ts, "policy_change", [
                    "--before-cache", pool("pool_v3", "random"), "--after-cache", pool("pool_v3", "greedy_entropy"),
                    "--committed", Path("configs") / f"committed_v3_{dn}_ts{ts}.json", "--policy", "random"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="E7 repairs with ledger")
    p.add_argument("--seeds", nargs="+", type=int, default=[0])
    p.add_argument("--datasets", nargs="+", default=PRIORITY)
    p.add_argument("--labels", nargs="+", default=["predictor_upgrade", "policy_change"])
    p.add_argument("--tag", default="")
    p.add_argument("--force", action="store_true", help="rerun even if the repair JSON exists")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    os.chdir(REPO)
    rr = Path(os.environ["RESULTS_ROOT"])
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    n_run = n_skip = 0
    for ds, ts, label, extra in jobs(a.seeds, a.datasets, a.labels, rr):
        dn = dsname_of(ds)
        out = REPO / "results_v3" / "repair" / f"{dn}_ts{ts}_{label}.json"
        cell = (f"{a.tag}:" if a.tag else "") + f"repair:{ds}:{label}:ts{ts}"
        missing = [str(x) for x in extra if isinstance(x, Path) and not x.exists()]
        if missing:
            print(f"[repairs] skip (missing prerequisite) {cell}: {missing}")
            n_skip += 1
            continue
        if out.exists() and not a.force:
            print(f"[repairs] skip (exists) {cell} -> {out}")
            n_skip += 1
            continue
        cmd = [sys.executable, "scripts/repair_experiment.py", "--dataset", ds, "--train-seed", str(ts),
               *[str(x).replace("\\", "/") for x in extra], "--label", label]
        shown = " ".join(["python"] + cmd[1:])
        if a.dry_run:
            print(f"[repairs] would run {cell}: {shown}")
            continue
        log = REPO / "results_v3" / "logs" / ((f"{a.tag}_" if a.tag else "") + f"repair_{dn}_{label}_ts{ts}.log")
        start, t0 = datetime.now(timezone.utc).isoformat(), time.time()
        with open(log, "w", encoding="utf-8") as lf:
            lf.write(f"# {shown}\n# start {start}\n")
            lf.flush()
            rc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, env=env).returncode
            lf.write(f"# returncode {rc}\n")
        secs = round(time.time() - t0, 1)
        with open(REPO / "results_v3" / "run_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"cell": cell, "command": shown, "start": start,
                                "end": datetime.now(timezone.utc).isoformat(), "seconds": secs, "returncode": rc,
                                "output_path": str(out), "log": str(log.relative_to(REPO))}) + "\n")
        print(f"[repairs] done {cell}: rc={rc} in {secs}s", flush=True)
        n_run += 1
        if rc != 0:
            print(f"[repairs] STOP: non-zero return code in {cell}; see {log}")
            return rc
    print(f"[repairs] ran {n_run}, skipped {n_skip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
