"""Round 3b: markdown blocks for handoff.md section 13.8, generated from the committed tables / logs (run after
results_v3/logs/r3J_postrun.sh).  Output: results_v3/logs/r3J_handoff_blocks.md (every number there comes from the
file named in its block header).

    .venv/Scripts/python.exe results_v3/logs/r3J_handoff_blocks.py
"""
import csv
import glob
import re
from pathlib import Path

OUT = Path("results_v3/logs/r3J_handoff_blocks.md")


def rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def ms(r, c, d=3):
    m, s = r.get(c + "_mean"), r.get(c + "_sd")
    if m in (None, ""):
        return ""
    return f"{float(m):.{d}f}" + (f" ± {float(s):.{d}f}" if s not in (None, "") else "")


lines = []
src = "results_v3/tables/TABLE_E4_cascade_seeds.csv"
lines += [f"#### Seed-aggregated headline (`{src}`; λ_ref `dep`, uniform costs; mean ± sample sd over seeds 0, 1, 2)", ""]
cols = [("tier1", "tier 1"), ("tier3", "tier 3"), ("none", "none"), ("certified_deployment", "cert. deployment"),
        ("deployed_cost_over_T", "cost / T"), ("cost_premium", "cost premium"),
        ("test_stratum_violation", "raw violation"), ("certified_violation", "certified violation"),
        ("max_excess_se", "max_excess_se"), ("cascade_over_safe_oracle", "cascade / safe oracle")]
lines.append("| dataset | policy | n | " + " | ".join(h for _, h in cols) + " |")
lines.append("|---|---|---|" + "---|" * len(cols))
for r in rows(src):
    lines.append(f"| {r['dataset']} | {r['policy']} | {r['n_seeds']} | " + " | ".join(ms(r, c, 2 if c == 'max_excess_se' else 3) for c, _ in cols) + " |")

src = "results_v3/tables/TABLE_E4_seed_flags.csv"
lines += ["", f"#### Seed consistency (`{src}`; values per seed 0 / 1 / 2)", ""]
lines.append("| dataset | policy | α | tier 1 | tier 3 | tier-1 range | flag | deepest k | r_full | verdict |")
lines.append("|---|---|---|---|---|---|---|---|---|---|")
for r in rows(src):
    lines.append(f"| {r['dataset']} | {r['policy']} | {r['alpha']} | {r['tier1']} | {r['tier3']} | {float(r['tier1_range']):.3f} | "
                 f"{r['flag']} | {r['deepest_k']} | {r['r_full']} | {r['deepest_verdict']} |")

lines += ["", "#### E7 repairs, seeds 1-2 (`results_v3/logs/r3J_repair_*_ts{1,2}.log`, lambda_ref `dep` line)", "", "```"]
for f in sorted(glob.glob("results_v3/logs/r3J_repair_*_ts[12].log")):
    name = re.match(r".*r3J_repair_(.+)\.log$", f.replace("\\", "/")).group(1)
    dep = [ln.strip() for ln in open(f, encoding="utf-8") if "lr[dep]" in ln]
    lines.append(f"{name}  {dep[0] if dep else '(no dep line)'}")
lines.append("```")

lines += ["", "#### E9 α margin over seeds (`results_v3/tables/TABLE_E9_alpha_margin.csv` (seed 0), "
          "`results_v3/tables_e9_alpha_margin_ts{1,2}/TABLE_E9_alpha_margin.csv`): tier-1 share at margin 0.02 / 0.05 / 0.10", ""]
lines.append("| dataset | policy | seed 0 | seed 1 | seed 2 |")
lines.append("|---|---|---|---|---|")
per = {}
for ts, p in ((0, "results_v3/tables/TABLE_E9_alpha_margin.csv"), (1, "results_v3/tables_e9_alpha_margin_ts1/TABLE_E9_alpha_margin.csv"),
              (2, "results_v3/tables_e9_alpha_margin_ts2/TABLE_E9_alpha_margin.csv")):
    for r in rows(p):
        cell = []
        for tag in ("am02", "am05", "am10"):
            st, t1, al = r[f"{tag}_status"], r[f"{tag}_tier1"], r[f"{tag}_alpha"]
            if st == "ok":
                cell.append(f"{float(t1):.2f} (α {float(al):g})")
            elif st.startswith("refused"):
                cell.append(f"refused (α {float(al):g})" if al else "refused")
            else:
                cell.append(st)
        per.setdefault((r["dataset"], r["policy"]), {})[ts] = " / ".join(cell)
for (ds, pol), v in sorted(per.items()):
    lines.append(f"| {ds} | {pol} | " + " | ".join(v.get(t, "") for t in (0, 1, 2)) + " |")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(lines)} lines)")
