#!/usr/bin/env python
"""v3 round 2 -- the multi-split sweep reproduces the single-split sweep on a single-split commit.

Compares two metrics JSONs of the same cell made with the same commit and the same single split
(round-1 protocol: test seed 778, draw ids 0..n-1): every field the OLD file has -- per draw (cascade,
marginal, baselines), per summary, the audit, strata sizes, full-acquisition risks -- must be equal in
the NEW file (exact equality of the JSON values).  Fields only the new file has (the round-2 noise-aware
metrics, by_split, audit_by_split, ...) are ignored.  Exit code 1 on any difference.

    python scripts/check_sweep_equivalence_v3.py OLD.json NEW.json [OLD2.json NEW2.json ...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def missing_or_different(old, new, path="") -> list:
    """Leaves of ``old`` that are absent from or different in ``new``."""
    if isinstance(old, dict):
        if not isinstance(new, dict):
            return [path]
        out = []
        for k, v in old.items():
            out += [f"{path}/{k} (missing)"] if k not in new else missing_or_different(v, new[k], f"{path}/{k}")
        return out
    if isinstance(old, list):
        if not isinstance(new, list) or len(old) != len(new):
            return [path]
        out = []
        for i, (a, b) in enumerate(zip(old, new)):
            out += missing_or_different(a, b, f"{path}[{i}]")
        return out
    return [] if old == new else [path]


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or len(args) % 2:
        raise SystemExit(__doc__)
    bad = 0
    for jo, jn in zip(args[0::2], args[1::2]):
        old, new = json.loads(Path(jo).read_text()), json.loads(Path(jn).read_text())
        for d in (old, new):
            d["meta"].pop("cache_meta", None)     # identical cache; dropped only to keep the report short
        diffs = missing_or_different(old, new)
        n_draws = sum(len(s["draws"]) for b in old["lambda_refs"].values() for s in b["schemes"].values())
        print(f"{Path(jo).name}: {n_draws} draw records x all round-1 fields -> "
              f"{'IDENTICAL' if not diffs else f'{len(diffs)} DIFFERENCES, e.g. {diffs[:5]}'}")
        bad += bool(diffs)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
