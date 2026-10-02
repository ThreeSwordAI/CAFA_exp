#!/usr/bin/env python
"""v3 -- one-to-one decision comparison of two sweeps of the same cells (torch-free; round 2, Task A.6).

For every metrics JSON present in both ``--old-dir`` and ``--new-dir`` (same file name = same dataset,
policy, seed), every lambda_ref key and every cost scheme present in both, the draws are matched by
their draw id (the sweeps must use the same protocol: same splits, same draw ids) and the script counts
the draws whose DEPLOYED decision ``(tier, rule, parameter)`` differs.  It also reports the tier shares,
the certified-deployment rate and the raw test stratum-violation rate of both sweeps, and, when
``--old-commits`` / ``--new-commits`` are given, whether the committed tier-3 escalation order (and its
first level) changed for that (policy, lambda_ref key).

Used for the HB boundary fix (round-1 sweeps, defect present, vs. the same protocol with the fix):

    python scripts/compare_decisions_v3.py --old-dir $RESULTS_ROOT/metrics_v3_round1 \
        --new-dir $RESULTS_ROOT/metrics_v3_hbfix_single --old-commits results_v3/round1/configs \
        --new-commits configs --output results_v3/diagnostics/r2_hbfix_decision_flips
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

KEYS_ORDER = ("0.5", "0.7", "0.9", "dep")


def diff_commits(old, new, path: str = "") -> list:
    """Paths of the leaves that differ between two committed JSONs (added / removed keys suffixed)."""
    if isinstance(old, dict) and isinstance(new, dict):
        out = []
        for k in sorted(set(old) | set(new), key=str):
            if k not in new:
                out.append(f"{path}/{k} (removed)")
            elif k not in old:
                out.append(f"{path}/{k} (added)")
            else:
                out += diff_commits(old[k], new[k], f"{path}/{k}")
        return out
    return [] if old == new else [path]


def decision(rec: dict):
    c = rec["cascade"]
    return int(c["tier"]), c["rule"], (None if c["param"] is None else float(c["param"]))


def tiers_str(summ: dict) -> str:
    return "/".join(f"{summ['tier_share'][t]:.2f}" for t in ("1", "2", "3", "0"))


def compare_cell(old: dict, new: dict, scheme_filter=None) -> list:
    rows = []
    keys = [k for k in KEYS_ORDER if k in old["lambda_refs"] and k in new["lambda_refs"]]
    keys += sorted(set(old["lambda_refs"]) & set(new["lambda_refs"]) - set(keys))
    for key in keys:
        bo, bn = old["lambda_refs"][key], new["lambda_refs"][key]
        for scheme in sorted(set(bo["schemes"]) & set(bn["schemes"])):
            if scheme_filter and scheme not in scheme_filter:
                continue
            do = {r["draw"]: r for r in bo["schemes"][scheme]["draws"]}
            dn = {r["draw"]: r for r in bn["schemes"][scheme]["draws"]}
            if set(do) != set(dn):
                raise SystemExit(f"draw ids differ for key {key} scheme {scheme}: not the same protocol")
            flips = [d for d in sorted(do) if decision(do[d]) != decision(dn[d])]
            tier_changes = sum(decision(do[d])[0] != decision(dn[d])[0] for d in flips)
            so, sn = bo["schemes"][scheme]["summary"], bn["schemes"][scheme]["summary"]
            rows.append({"lambda_ref_key": key, "scheme": scheme, "n_draws": len(do), "flips": len(flips),
                         "flips_tier_changed": int(tier_changes), "flipped_draws": flips,
                         "tiers_old": tiers_str(so), "tiers_new": tiers_str(sn),
                         "cert_old": so["certified_deployment_rate"], "cert_new": sn["certified_deployment_rate"],
                         "viol_old": so["cascade_violation_rate"], "viol_new": sn["cascade_violation_rate"]})
    return rows


def order_changes(old_c: dict, new_c: dict) -> dict:
    out = {}
    for pol, keys in old_c.get("escalation", {}).items():
        for key, eo in keys.items():
            en = new_c.get("escalation", {}).get(pol, {}).get(key)
            if en is None:
                continue
            out[(pol, key)] = {"order_changed": eo["order"] != en["order"],
                               "start_changed": eo["order"][0] != en["order"][0],
                               "start_old": round(eo["fractions_desc"][eo["order"][0]], 3),
                               "start_new": round(en["fractions_desc"][en["order"][0]], 3)}
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--old-dir", required=True)
    p.add_argument("--new-dir", required=True)
    p.add_argument("--old-commits", default=None, help="dir with the old committed_v3_*.json")
    p.add_argument("--new-commits", default=None, help="dir with the new committed_v3_*.json")
    p.add_argument("--schemes", default="uniform", help="comma list, or 'all'")
    p.add_argument("--output", default=None, help="writes <output>.json and <output>.md")
    a = p.parse_args(argv)
    schemes = None if a.schemes == "all" else set(a.schemes.split(","))

    table, commits = [], {}
    for jo in sorted(Path(a.old_dir).glob("*.json")):
        jn = Path(a.new_dir) / jo.name
        if not jn.exists():
            continue
        old, new = json.loads(jo.read_text()), json.loads(jn.read_text())
        m = new["meta"]
        oc = {}
        if a.old_commits and a.new_commits:
            nm = f"committed_v3_{m['dsname']}_ts{m['train_seed']}.json"
            co, cn = Path(a.old_commits) / nm, Path(a.new_commits) / nm
            if co.exists() and cn.exists():
                cold, cnew = json.loads(co.read_text()), json.loads(cn.read_text())
                oc = order_changes(cold, cnew)
                commits[nm] = [d for d in diff_commits(cold, cnew) if not d.endswith("/order") and d != "/created"]
        for r in compare_cell(old, new, schemes):
            o = oc.get((m["policy"], r["lambda_ref_key"]), {})
            table.append({"dataset": m["dsname"], "policy": m["policy"], "seed": m["train_seed"], **r,
                          "order_changed": o.get("order_changed"), "start_changed": o.get("start_changed"),
                          "start_old": o.get("start_old"), "start_new": o.get("start_new")})

    hdr = ("| dataset | policy | λ_ref | draws | flips | of which tier changed | tiers 1/2/3/none old → new "
           "| cert old → new | raw viol old → new | tier-3 order changed (start level old → new) |")
    lines = [hdr, "|" + "---|" * 10]
    for r in table:
        st = "" if r["order_changed"] is None else (
            ("yes" if r["order_changed"] else "no") + (f" ({r['start_old']:.3f} → {r['start_new']:.3f})" if r["start_changed"] else ""))
        lines.append(f"| {r['dataset']} | {r['policy']} | {r['lambda_ref_key']} | {r['n_draws']} | {r['flips']} | "
                     f"{r['flips_tier_changed']} | {r['tiers_old']} → {r['tiers_new']} | {r['cert_old']:.2f} → {r['cert_new']:.2f} | "
                     f"{r['viol_old']:.3f} → {r['viol_new']:.3f} | {st} |")
    tot = sum(r["flips"] for r in table)
    n_tot = sum(r["n_draws"] for r in table)
    cells_flip = sum(r["flips"] > 0 for r in table)
    lines.append("")
    lines.append(f"Total: {tot} of {n_tot} (cell, λ_ref, draw) decisions changed; {cells_flip} of {len(table)} "
                 f"(cell, λ_ref) rows have at least one change.")
    if commits:
        bad = {k: v for k, v in commits.items() if v}
        lines.append("Commit diffs other than `created` and `escalation.*.order`: "
                     + ("none" if not bad else json.dumps(bad)))
    text = "\n".join(lines)
    print(text)
    if a.output:
        out = Path(a.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.with_suffix(".json").write_text(json.dumps({"old_dir": a.old_dir, "new_dir": a.new_dir, "rows": table,
                                                        "total_flips": tot, "total_decisions": n_tot,
                                                        "commit_other_diffs": commits}, indent=1), encoding="utf-8")
        out.with_suffix(".md").write_text(f"# Decision flips: {a.old_dir} -> {a.new_dir} (schemes: {a.schemes})\n\n"
                                          + text + "\n", encoding="utf-8")
        print(f"wrote {out.with_suffix('.json')} and {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
