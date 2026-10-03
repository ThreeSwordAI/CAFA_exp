#!/usr/bin/env python
"""v3 -- E9 alpha-rule sensitivity summary (torch-free): TABLE_E9_alpha_margin.md / .csv.

One row per cell (dataset, policy) of the PRIMARY metrics dir at train seed ``--train-seed`` (lambda_ref key
``--lambda-ref-key``, default dep; cost scheme ``--scheme``, default uniform), one column per alpha-rule margin
(alpha = ceil-to-grid(probe floor + margin), :func:`commit_v3.alpha_from_floor`):

  tag   margin  grid   metrics dir (default)                         commit file (default)
  am02  0.02    0.01   ${RESULTS_ROOT}/metrics_v3_alpha_margin02     configs/committed_v3_am02_{dsname}_ts{ts}.json
  am05  0.05    0.05   ${RESULTS_ROOT}/metrics_v3 (primary rule)     configs/committed_v3_{dsname}_ts{ts}.json
  am10  0.10    0.05   ${RESULTS_ROOT}/metrics_v3_alpha_margin10     configs/committed_v3_am10_{dsname}_ts{ts}.json

The metrics file of a margin is the primary file's basename in that margin's dir.  Per (cell, margin) the status is

  ok                       metrics file present: alpha, tier-1 / tier-3 share, certified-deployment rate and
                           deployed cost / T (T = meta.T) from its pooled summary; lambda_ref and G of its block
  refused                  no commit file and alpha_from_floor(primary commit floor, margin, grid) <= the primary
                           commit's design margin (0.05): commit_v3 refuses (rc 7), there is nothing to sweep
  TBD-RUN (not committed)  no commit file and the rule's alpha is above the design margin: not committed yet
  TBD-RUN                  commit file present, metrics file missing: committed, not swept

Outputs (``--output-dir``, default results_v3/tables): TABLE_E9_alpha_margin.md -- one compact text per margin,
e.g. "alpha 0.15: tier1 0.12, tier3 0.88, cert 1.00, cost/T 0.93"; TABLE_E9_alpha_margin.csv -- numeric columns
per margin, prefixed with the tag: ``{tag}_status``, ``{tag}_alpha``, ``{tag}_tier1``, ``{tag}_tier3``,
``{tag}_certified_deployment``, ``{tag}_deployed_cost_over_T``, ``{tag}_lambda_ref``, ``{tag}_G``.

    python scripts/alpha_margin_summary_v3.py [--train-seed 0] [--output-dir results_v3/tables]
        # every dir / commit prefix / grid has a flag: --{tag}-metrics-dir, --{tag}-commit-prefix, --{tag}-grid
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commit_v3 import alpha_from_floor  # noqa: E402

# (tag, alpha-rule margin, alpha grid, metrics dir under RESULTS_ROOT, commit-file prefix); am05 is the primary rule
MARGINS = (("am02", 0.02, 0.01, "metrics_v3_alpha_margin02", "committed_v3_am02_"),
           ("am05", 0.05, 0.05, "metrics_v3", "committed_v3_"),
           ("am10", 0.10, 0.05, "metrics_v3_alpha_margin10", "committed_v3_am10_"))
PRIMARY = "am05"
FIELDS = ("status", "alpha", "tier1", "tier3", "certified_deployment", "deployed_cost_over_T", "lambda_ref", "G")


def margin_cell(metrics_path: Path, commit_path: Path, primary_commit: "dict | None", margin: float, grid: float,
                key: str, scheme: str) -> dict:
    """One (cell, margin) entry: the FIELDS plus ``text`` (the md cell)."""
    out = dict.fromkeys(FIELDS)
    if metrics_path.exists():
        d = json.loads(metrics_path.read_text())
        blk = d["lambda_refs"].get(key)
        sch = (blk or {}).get("schemes", {}).get(scheme)
        if sch is None:
            out.update(status="n/a", text=f"n/a: no lambda_ref {key} / scheme {scheme} in {metrics_path.name}")
            return out
        s = sch["summary"]
        if commit_path.exists():
            ca = json.loads(commit_path.read_text())["alpha"]
            if float(ca) != float(d["alpha"]):
                print(f"WARNING: {metrics_path} alpha {d['alpha']} != {commit_path} alpha {ca}", file=sys.stderr)
        out.update(status="ok", alpha=d["alpha"], tier1=s["tier_share"]["1"], tier3=s["tier_share"]["3"],
                   certified_deployment=s["certified_deployment_rate"],
                   deployed_cost_over_T=s["cascade_mean_test_cost"] / d["meta"]["T"],
                   lambda_ref=blk["lambda_ref"], G=blk["G"])
        out["text"] = (f"alpha {out['alpha']:.2f}: tier1 {out['tier1']:.2f}, tier3 {out['tier3']:.2f}, "
                       f"cert {out['certified_deployment']:.2f}, cost/T {out['deployed_cost_over_T']:.2f}")
        return out
    if commit_path.exists():
        out.update(status="TBD-RUN", alpha=json.loads(commit_path.read_text())["alpha"])
        out["text"] = f"TBD-RUN: committed alpha = {out['alpha']:.2f}, not swept"
        return out
    if primary_commit is None:
        out.update(status="TBD-RUN (not committed)", text="TBD-RUN (not committed): no primary commit (floor unknown)")
        return out
    alpha = alpha_from_floor(primary_commit["floor"]["estimate"], margin, grid)
    dm = float(primary_commit.get("design_margin", 0.05))
    out["alpha"] = alpha
    if alpha <= dm:
        out.update(status="refused", text=f"refused: alpha = {alpha:.2f} <= design margin {dm:g} (commit_v3 rc 7)")
    else:
        out.update(status="TBD-RUN (not committed)", text=f"TBD-RUN (not committed): alpha = {alpha:.2f} by the rule")
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3 E9 alpha-margin summary (TABLE_E9_alpha_margin)")
    p.add_argument("--results-root", default=os.environ.get("RESULTS_ROOT"),
                   help="default ${RESULTS_ROOT}; base of the default metrics dirs")
    p.add_argument("--configs-dir", default="configs", help="where the committed_v3_* JSONs live")
    for tag, mg, gr, sub, prefix in MARGINS:
        p.add_argument(f"--{tag}-metrics-dir", default=None, help=f"margin {mg}: default ${{RESULTS_ROOT}}/{sub}")
        p.add_argument(f"--{tag}-commit-prefix", default=prefix, help=f"margin {mg}: commit file prefix ({prefix})")
        p.add_argument(f"--{tag}-grid", type=float, default=gr, help=f"margin {mg}: alpha grid ({gr})")
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--lambda-ref-key", default="dep")
    p.add_argument("--scheme", default="uniform")
    p.add_argument("--output-dir", default="results_v3/tables")
    a = p.parse_args(argv)
    ts = int(a.train_seed)
    margins = []
    for tag, mg, _gr, sub, _prefix in MARGINS:
        md_ = getattr(a, f"{tag}_metrics_dir")
        if md_ is None:
            if not a.results_root:
                p.error(f"RESULTS_ROOT is not set: give --results-root or --{tag}-metrics-dir")
            md_ = str(Path(a.results_root) / sub)
        margins.append((tag, mg, getattr(a, f"{tag}_grid"), Path(md_), getattr(a, f"{tag}_commit_prefix")))
    by_tag = {m[0]: m for m in margins}
    cfg_dir = Path(a.configs_dir)

    rows = []
    for jp in sorted(by_tag[PRIMARY][3].glob("*.json")):
        meta = json.loads(jp.read_text())["meta"]
        if int(meta["train_seed"]) != ts:
            continue
        dsname = meta["dsname"]
        pc_path = cfg_dir / f"{by_tag[PRIMARY][4]}{dsname}_ts{ts}.json"
        primary_commit = json.loads(pc_path.read_text()) if pc_path.exists() else None
        row = {"dataset": dsname, "policy": meta["policy"], "seed": ts}
        for tag, mg, gr, mdir, prefix in margins:
            e = margin_cell(mdir / jp.name, cfg_dir / f"{prefix}{dsname}_ts{ts}.json", primary_commit, mg, gr,
                            a.lambda_ref_key, a.scheme)
            row.update({f"{tag}_{k}": e[k] for k in FIELDS})
            row[f"{tag}_text"] = e["text"]
        rows.append(row)
    if not rows:
        print(f"no ts{ts} metrics in {by_tag[PRIMARY][3]}; nothing written")
        return 1

    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    keys = ["dataset", "policy", "seed"] + [f"{t}_{k}" for t, *_ in margins for k in FIELDS]
    with open(out / "TABLE_E9_alpha_margin.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    heads = [f"margin {mg:.2f} (grid {gr:g}{', primary' if tag == PRIMARY else ''})" for tag, mg, gr, *_ in margins]
    lines = ["| dataset | policy | " + " | ".join(heads) + " |", "|" + "---|" * (2 + len(margins))]
    lines += ["| " + " | ".join([r["dataset"], r["policy"]] + [r[f"{t}_text"] for t, *_ in margins]) + " |" for r in rows]
    src = "\n".join(f"- margin {mg:.2f} (grid {gr:g}): metrics `{mdir}`, commits `{cfg_dir / prefix}{{dsname}}_ts{ts}.json`"
                    for tag, mg, gr, mdir, prefix in margins)
    (out / "TABLE_E9_alpha_margin.md").write_text(
        f"# TABLE_E9_alpha_margin (train seed {ts}, lambda_ref key = {a.lambda_ref_key}, scheme = {a.scheme})\n\n"
        "alpha = ceil-to-grid(probe floor + margin); per margin: alpha, tier-1 / tier-3 share, certified-deployment "
        "rate (cert) and deployed cost / T of the cascade (pooled over all draws).  \"refused\": commit_v3 refuses "
        "alpha <= design margin (rc 7); \"TBD-RUN (not committed)\": no commit yet (alpha from the rule); "
        "\"TBD-RUN\": committed, not swept.  lambda_ref and G per margin are in the csv.\n\n"
        f"Sources:\n{src}\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote TABLE_E9_alpha_margin for {len(rows)} cells to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
