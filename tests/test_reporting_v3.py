"""v3 round 3 (Task I) -- reporting additions, on hand-built metrics JSONs (only the keys the scripts read).

* make_tables_v3: the appended E4 columns (cost / T of the cascade, marginal CAFA and the Mondrian oracle,
  ``tier2_would_certify`` counted from the draw records, ``escalated_fraction``; the Task-K oracle columns empty
  for round-2 metrics), E6 ``feasible_rate``, TABLE_E4_cost_gap (label rule at its 0.9 / 1.6 boundaries, on the
  oracle / full-acquisition cost, and at a zero-cost oracle; ``label_note`` / ``n_splits_finite``; per-split k*, the
  median over feasible draws, n_needed against kl_bernoulli incl. the inf cases, cal_frac), and
  TABLE_E4_cascade_seeds still written with the new columns;
* make_figures_v3: F3's cost panel is in cost / T and prints the E2 worst-stratum risk / alpha under each bar; one
  bar per cell with one seed per (dataset, policy), one bar per (dataset, policy) (seed means) with several;
* alpha_margin_summary_v3: ok / refused (incl. alpha exactly at the design margin) / TBD-RUN / TBD-RUN (not
  committed) cells of TABLE_E9_alpha_margin.

Several fixtures have a full-acquisition cost != T (T = 20, full cost 30 or 40, as under inverse_info), so that
every "cost / T" column is told apart from cost / full acquisition and ``oracle_safe_over_full`` from cost / T.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import alpha_margin_summary_v3  # noqa: E402
import make_figures_v3  # noqa: E402
import make_tables_v3  # noqa: E402
from cafa.commit_rules import kl_bernoulli  # noqa: E402

SPLITS = ("778", "779", "780", "781", "782")
TYPE_I = {"threshold": False, "budget": True, "escalation": True}


def _bl(cost, **kw):
    return {"mean_test_risk": 0.05, "mean_test_cost": cost, "stratum_violation_rate": 0.0,
            "aggregate_violation_rate": 0.0, "n": 100, "stratum_certified_violation_rate": 0.0, **kw}


def _summary(cost, *, answered=1.0, tier=(0.0, 1.0, 0.0, 0.0), marg_cost=5.0, mon_cost=8.0, full_cost=20.0,
             e2=1.5, extra_bl=None, **kw):
    s = {"tier_share": dict(zip("0123", tier)), "certified_deployment_rate": 1.0 - tier[0],
         "cascade_mean_test_cost": cost, "cascade_mean_answered_fraction": answered,
         "cascade_violation_rate": 0.0, "cascade_certified_violation_rate": 0.0, "cascade_max_excess_se_mean": -2.0,
         "cost_premium_cascade_over_marginal": cost / marg_cost,
         "marginal_mean_test_cost": marg_cost, "marginal_mean_test_risk": 0.08,
         "marginal_aggregate_violation_rate": 0.0, "marginal_max_stratum_over_alpha_mean": e2,
         "marginal_hidden_stratum_violation_rate": 0.5, "marginal_hidden_certified_violation_rate": 0.1,
         "baselines": {"full_acquisition": _bl(full_cost), "mondrian_oracle": _bl(mon_cost), **(extra_bl or {})},
         "by_split": {sp: {"cascade_violation_rate": 0.0} for sp in SPLITS}}
    s.update(kw)
    return s


def _audit(kmax, n_k=400):
    return {str(k): {"k": k, "n_k": n_k if k == kmax else 1000, "rmin_thr": 0.05, "rmin_depth": 0.05,
                     "r_full": 0.05, "p_thr": 0.01, "p_depth": 0.01, "verdict": "feasible"} for k in range(kmax + 1)}


def _draw(split, tc=None, oracle=None):
    tc = tc or {"threshold": True}
    tier = 1 if tc.get("threshold") else 2 if tc.get("budget") else 3 if tc.get("escalation") else 0
    rec = {"draw": 0, "split_seed": int(split), "split_index": SPLITS.index(split),
           "cascade": {"tier": tier, "tiers_certified": tc}, "baselines": {}}
    if oracle is not None:
        rec["baselines"]["oracle_stratum_safe"] = oracle
    return rec


def _oracle(risk=None):
    """A Task-K oracle_stratum_safe draw record: feasible with the given calibration-pool stratum risks, else not."""
    if risk is None:
        return {"feasible": False, "lambda": None, "calpool_stratum_risk": None, "test_cost": 20.0}
    return {"feasible": True, "lambda": 0.5, "calpool_stratum_risk": risk, "test_cost": 10.0}


def _metrics(dsname, policy="greedy_entropy", *, seed=0, T=20, alpha=0.1, summary, draws, audit_by_split=None,
             cal_frac=None, lambda_ref=0.8, G=3):
    abs_ = audit_by_split or {sp: _audit(2) for sp in SPLITS}
    meta = {"dsname": dsname, "policy": policy, "train_seed": seed, "T": T,
            "test_seeds": [int(x) for x in SPLITS], "primary_test_seed": 778}
    if cal_frac is not None:
        meta["cal_frac"] = cal_frac
    blk = {"lambda_ref": lambda_ref, "G": G, "edges": [1.0, 2.0], "audit": abs_["778"], "audit_by_split": abs_,
           "deepest_verdict_agreement": 5, "n_splits": 5, "schemes": {"uniform": {"summary": summary, "draws": draws}}}
    return {"meta": meta, "alpha": alpha, "delta": 0.1, "delta_weights": [0.5, 0.25, 0.25], "lambda_refs": {"dep": blk}}


def _write(dirpath: Path, d: dict) -> Path:
    dirpath.mkdir(parents=True, exist_ok=True)
    m = d["meta"]
    p = dirpath / f"{m['dsname']}_ts{m['train_seed']}_{m['policy']}_softmax.json"
    p.write_text(json.dumps(d))
    return p


def _rows(path: Path) -> list:
    return list(csv.DictReader(open(path, encoding="utf-8")))


def _n(r, alpha=0.1, delta_1=0.05):
    return math.log(1.0 / delta_1) / kl_bernoulli(r, alpha)


# ---- the synthetic metrics dir -------------------------------------------------------------------------------------

def _round2_draws():
    # 3 Type-I draws (budget certifies, threshold does not), 2 threshold + budget, 1 threshold only (no budget key),
    # 4 escalation only -> tier2_would_certify = 0.3
    tcs = ([TYPE_I] * 3 + [{"threshold": True, "budget": True, "escalation": True}] * 2 + [{"threshold": True}]
           + [{"threshold": False, "budget": False, "escalation": True}] * 4)
    return [_draw(SPLITS[i % 5], tc) for i, tc in enumerate(tcs)]


def _gap_draws():
    """Per split: 778 feasible r(k*=2) 0.04 / 0.05 / 0.07 + one infeasible (median 0.05); 779 infeasible only (inf);
    780 k* = 1 (r 0.02; r of stratum 2 is 0.5 and must not be used); 781 r = alpha (inf); 782 r = 0.03."""
    dr = [_draw("778", oracle=_oracle({"0": 0.01, "2": r})) for r in (0.04, 0.05, 0.07)]
    dr += [_draw("778", oracle=_oracle()), _draw("779", oracle=_oracle()), _draw("779", oracle=_oracle())]
    dr += [_draw("780", oracle=_oracle({"1": 0.02, "2": 0.5})), _draw("781", oracle=_oracle({"2": 0.1})),
           _draw("782", oracle=_oracle({"2": 0.03}))]
    return dr


def _oracle_bl(cost, rate=0.6, mon_cost=6.0):
    return {"oracle_stratum_safe": _bl(cost, feasible_rate=rate),
            "oracle_stratum_safe_mondrian": _bl(mon_cost, feasible_rate=1.0, abstained_fraction=0.0)}


@pytest.fixture()
def mdir(tmp_path):
    d = tmp_path / "metrics_v3"
    gap_abs = {sp: _audit(1 if sp == "780" else 2) for sp in SPLITS}
    # round-2 cell (no Task-K fields), seeds 0 and 1; full acquisition 30 != T = 20 (as under inverse_info)
    _write(d, _metrics("dsA", summary=_summary(15.0, answered=0.8, e2=2.2, full_cost=30.0), draws=_round2_draws()))
    _write(d, _metrics("dsA", seed=1, summary=_summary(17.0, answered=0.8, full_cost=30.0), draws=_round2_draws()))
    # Task-K cells: sample-limited exactly at 1.6, near-oracle just below, intrinsic exactly at 0.9 of the full
    # acquisition (cal_frac 1.0), and a zero-cost oracle with a zero-cost cascade (ratio None) -- full acquisition = T
    _write(d, _metrics("dsK", "sl", summary=_summary(16.0, extra_bl=_oracle_bl(10.0), cascade_cost_over_oracle=1.6,
                                                     cascade_cost_over_oracle_feasible=1.25),
                       draws=_gap_draws(), audit_by_split=gap_abs))
    _write(d, _metrics("dsK", "near", summary=_summary(16.0, extra_bl=_oracle_bl(17.99),
                                                       cascade_cost_over_oracle=1.5999), draws=_gap_draws()))
    _write(d, _metrics("dsK", "intr", cal_frac=1.0,
                       summary=_summary(19.0, extra_bl=_oracle_bl(18.0), cascade_cost_over_oracle=19 / 18),
                       draws=[_draw(sp, oracle=_oracle({"2": 0.05})) for sp in SPLITS]))
    _write(d, _metrics("dsZ", summary=_summary(0.0, extra_bl=_oracle_bl(0.0), cascade_cost_over_oracle=None),
                       draws=[_draw(sp, oracle=_oracle({"2": 0.0})) for sp in SPLITS]))
    # non-uniform costs: full acquisition 40 != T = 20; the oracle needs T (cost / T 1.0) but only half the full
    # acquisition -> not intrinsic (cascade / oracle 1.2 -> near-oracle); oracle feasible in every split, r = alpha
    # in split 781 (n_needed inf there only)
    _write(d, _metrics("dsK", "inv", summary=_summary(24.0, marg_cost=6.0, mon_cost=10.0, full_cost=40.0,
                                                      extra_bl=_oracle_bl(20.0, rate=1.0), cascade_cost_over_oracle=1.2),
                       draws=[_draw(sp, oracle=_oracle({"2": 0.1 if sp == "781" else 0.05})) for sp in SPLITS]))
    return d


# ---- make_tables_v3 ------------------------------------------------------------------------------------------------

def test_e4_new_columns_and_e6_feasible_rate(mdir, tmp_path):
    out = tmp_path / "tables"
    assert make_tables_v3.main(["--metrics-dir", str(mdir), "--output-dir", str(out)]) == 0
    e4 = _rows(out / "TABLE_E4_cascade.csv")
    cols = list(e4[0])
    assert cols[-8:] == ["deployed_cost_over_T", "marginal_cost_over_T", "mondrian_cost_over_T", "tier2_would_certify",
                         "escalated_fraction", "oracle_safe_cost_over_T", "oracle_safe_feasible_rate",
                         "cascade_over_safe_oracle"]
    assert cols[:3] == ["dataset", "policy", "seed"] and cols[-9] == "verdict_agreement"   # round-2 columns first
    a = next(r for r in e4 if r["dataset"] == "dsA" and r["seed"] == "0")
    # divided by T = 20, not by the full-acquisition cost 30 (0.5 / 0.167 / 0.267)
    assert float(a["deployed_cost_over_T"]) == pytest.approx(0.75)
    assert float(a["marginal_cost_over_T"]) == pytest.approx(0.25)
    assert float(a["mondrian_cost_over_T"]) == pytest.approx(0.4)
    inv = next(r for r in e4 if r["policy"] == "inv")        # T = 20, full acquisition 40
    assert float(inv["deployed_cost_over_T"]) == pytest.approx(1.2)
    assert float(inv["marginal_cost_over_T"]) == pytest.approx(0.3)
    assert float(inv["mondrian_cost_over_T"]) == pytest.approx(0.5)
    assert float(inv["oracle_safe_cost_over_T"]) == pytest.approx(1.0)
    assert float(a["tier2_would_certify"]) == pytest.approx(0.3)
    assert float(a["escalated_fraction"]) == pytest.approx(0.2)
    assert a["oracle_safe_cost_over_T"] == a["oracle_safe_feasible_rate"] == a["cascade_over_safe_oracle"] == ""
    k = next(r for r in e4 if r["policy"] == "sl")
    assert float(k["oracle_safe_cost_over_T"]) == pytest.approx(0.5)
    assert float(k["oracle_safe_feasible_rate"]) == pytest.approx(0.6)
    assert float(k["cascade_over_safe_oracle"]) == pytest.approx(1.6)
    assert float(k["tier2_would_certify"]) == 0.0
    e6 = _rows(out / "TABLE_E6_baselines.csv")
    assert list(e6[0])[-1] == "feasible_rate"
    kk = {r["baseline"]: r for r in e6 if r["policy"] == "sl"}
    assert float(kk["oracle_stratum_safe"]["feasible_rate"]) == pytest.approx(0.6)
    assert float(kk["oracle_stratum_safe_mondrian"]["feasible_rate"]) == 1.0
    assert kk["mondrian_oracle"]["feasible_rate"] == ""
    assert not [r for r in e6 if r["dataset"] == "dsA" and r["baseline"].startswith("oracle_stratum_safe")]
    # seeds table still written, with the new numeric columns (mean +- sd over the two dsA seeds)
    seeds = {r["dataset"]: r for r in _rows(out / "TABLE_E4_cascade_seeds.csv")}
    assert float(seeds["dsA"]["deployed_cost_over_T_mean"]) == pytest.approx(0.8)
    assert float(seeds["dsA"]["deployed_cost_over_T_sd"]) == pytest.approx(np.std([0.75, 0.85], ddof=1))
    assert seeds["dsA"]["oracle_safe_cost_over_T_mean"] == ""
    assert "deployed_cost_over_T" in (out / "TABLE_E4_cascade_seeds.md").read_text(encoding="utf-8")


def test_cost_gap_table(mdir, tmp_path):
    out = tmp_path / "tables"
    assert make_tables_v3.main(["--metrics-dir", str(mdir), "--output-dir", str(out)]) == 0
    rows = _rows(out / "TABLE_E4_cost_gap.csv")
    cols = list(rows[0])
    assert cols[cols.index("oracle_safe_cost_over_T") + 1] == "oracle_safe_over_full"
    assert cols[cols.index("label") + 1] == "label_note"
    assert cols[cols.index("n_needed_range") + 1] == "n_splits_finite"
    assert cols[cols.index("cascade_over_safe_oracle") + 1] == "cascade_over_safe_oracle_feasible"
    gap = {(r["dataset"], r["policy"]): r for r in rows}
    # the feasible-draws-only ratio is the summary's cascade_cost_over_oracle_feasible (empty where absent)
    assert float(gap["dsK", "sl"]["cascade_over_safe_oracle_feasible"]) == pytest.approx(1.25)
    assert gap["dsK", "near"]["cascade_over_safe_oracle_feasible"] == ""
    assert set(gap) == {("dsK", "sl"), ("dsK", "near"), ("dsK", "intr"), ("dsK", "inv"),
                        ("dsZ", "greedy_entropy")}  # no dsA
    assert gap["dsK", "sl"]["label"] == "sample-limited"            # ratio exactly 1.6
    assert gap["dsK", "near"]["label"] == "near-oracle"             # 1.5999, oracle 0.8995 of the full acquisition
    assert gap["dsK", "intr"]["label"] == "intrinsic"               # oracle exactly 0.9 of the full acquisition
    assert float(gap["dsK", "intr"]["oracle_safe_over_full"]) == pytest.approx(0.9)
    assert gap["dsZ", "greedy_entropy"]["label"] == "near-oracle"   # zero-cost oracle and cascade: ratio empty
    assert gap["dsZ", "greedy_entropy"]["cascade_over_safe_oracle"] == ""
    # full acquisition 40 != T 20: oracle / full = 0.5 (not intrinsic) although oracle / T = 1.0 >= 0.9
    inv = gap["dsK", "inv"]
    assert float(inv["oracle_safe_over_full"]) == pytest.approx(0.5)
    assert float(inv["oracle_safe_cost_over_T"]) == pytest.approx(1.0)
    assert float(inv["deployed_cost_over_T"]) == pytest.approx(1.2)
    assert inv["label"] == "near-oracle"
    # label_note / n_splits_finite: empty only when the oracle is feasible and n_needed finite in every split
    reason = "(r_cal(lambda*) >= alpha or no feasible draw)"
    assert gap["dsK", "sl"]["label_note"] == f"oracle infeasible in 1/5 splits; n_needed inf in 2/5 splits {reason}"
    assert gap["dsK", "sl"]["n_splits_finite"] == "3/5"
    assert gap["dsK", "near"]["label_note"] == f"oracle infeasible in 1/5 splits; n_needed inf in 3/5 splits {reason}"
    assert gap["dsK", "near"]["n_splits_finite"] == "2/5"           # k* = 2 in 780 too (r 0.5)
    assert inv["label_note"] == f"n_needed inf in 1/5 splits {reason}" and inv["n_splits_finite"] == "4/5"
    assert gap["dsK", "intr"]["label_note"] == gap["dsZ", "greedy_entropy"]["label_note"] == ""
    assert gap["dsK", "intr"]["n_splits_finite"] == gap["dsZ", "greedy_entropy"]["n_splits_finite"] == "5/5"
    sl = gap["dsK", "sl"]
    assert sl["k_star"] == "2" and float(sl["n_k_cal"]) == pytest.approx(200.0)   # 0.5 * n_k(k*) of split 778
    assert float(sl["r_cal_at_oracle"]) == pytest.approx(0.05)     # median of the feasible draws; infeasible skipped
    # splits: 778 n(0.05), 779 inf (no feasible draw), 780 n(0.02) at k* = 1, 781 inf (r = alpha), 782 n(0.03)
    assert float(sl["n_needed"]) == pytest.approx(_n(0.05))
    assert sl["n_needed_range"] == f"{_n(0.02):.0f}–inf"
    assert float(sl["n_needed_over_n_k"]) == pytest.approx(_n(0.05) / 200.0)
    assert float(sl["safe_mondrian_cost_over_T"]) == pytest.approx(0.3)
    intr = gap["dsK", "intr"]
    assert float(intr["n_k_cal"]) == pytest.approx(400.0)          # meta cal_frac 1.0
    assert intr["n_needed_range"] == f"{_n(0.05):.0f}–{_n(0.05):.0f}"
    md = (out / "TABLE_E4_cost_gap.md").read_text(encoding="utf-8")
    assert "ln(1/delta_1) / kl(r_cal(s) || alpha)" in md and f"| {_n(0.02):.0f}–inf | 3/5 |" in md
    assert "\"intrinsic\" if oracle_safe_over_full >= 0.9" in md
    assert "The label uses the pooled costs only" in md and "`label_note` qualifies it" in md
    # round-2 metrics only: no cost-gap table
    only_r2 = tmp_path / "r2"
    only_r2.mkdir()
    for p in mdir.glob("dsA_*.json"):
        (only_r2 / p.name).write_text(p.read_text())
    assert make_tables_v3.main(["--metrics-dir", str(only_r2), "--output-dir", str(tmp_path / "t2")]) == 0
    assert (tmp_path / "t2" / "TABLE_E4_cascade.csv").exists() and not (tmp_path / "t2" / "TABLE_E4_cost_gap.csv").exists()


def test_cost_gap_label_and_n_needed_rules():
    lab = make_tables_v3.cost_gap_label
    assert lab(0.9, None) == lab(0.95, 1.0) == "intrinsic"
    assert lab(0.8999, 1.6) == lab(0.1, math.inf) == "sample-limited"
    assert lab(0.8999, 1.5999) == lab(0.0, 1.0) == "near-oracle"
    assert lab(None, 3.0) is None and lab(0.5, None) is None
    note = make_tables_v3.label_note
    assert note(0, 0, 5) == ""
    assert note(3, 4, 5) == ("oracle infeasible in 3/5 splits; n_needed inf in 4/5 splits "
                             "(r_cal(lambda*) >= alpha or no feasible draw)")
    nn = make_tables_v3.n_needed
    assert nn(0.05, 0.1, 0.05) == pytest.approx(math.log(20.0) / kl_bernoulli(0.05, 0.1))
    assert nn(0.0, 0.1, 0.05) == pytest.approx(math.log(20.0) / math.log(1.0 / 0.9))
    assert math.isinf(nn(0.1, 0.1, 0.05)) and math.isinf(nn(0.2, 0.1, 0.05)) and math.isinf(nn(None, 0.1, 0.05))
    assert make_tables_v3.tier2_would_certify(_round2_draws()) == pytest.approx(0.3)
    assert make_tables_v3.tier2_would_certify([]) is None


# ---- make_figures_v3 -----------------------------------------------------------------------------------------------

def _record_figures(monkeypatch) -> dict:
    """Patch Figure.savefig to remember each saved figure by file name (the figure itself, not the PDF)."""
    from matplotlib.figure import Figure
    saved, orig = {}, Figure.savefig

    def rec(self, fname, *a, **k):
        saved[Path(fname).name] = self
        return orig(self, fname, *a, **k)
    monkeypatch.setattr(Figure, "savefig", rec)
    return saved


def test_f3_cost_over_T_with_e2_under_bars(mdir, tmp_path, monkeypatch):
    from matplotlib.container import ErrorbarContainer
    saved = _record_figures(monkeypatch)
    one = tmp_path / "one_seed"                     # one train seed per (dataset, policy): one bar per cell
    one.mkdir()
    for p in mdir.glob("*.json"):
        if "_ts1_" not in p.name:
            (one / p.name).write_text(p.read_text())
    out = tmp_path / "figs"
    assert make_figures_v3.main(["--metrics-dir", str(one), "--output-dir", str(out)]) == 0
    assert (out / "F3_cascade.pdf").stat().st_size > 0
    ax = saved["F3_cascade.pdf"].axes[1]
    assert ax.get_ylabel() == "cost / T"
    cells = make_figures_v3.load_cells(one, "dep", "uniform")
    rows = make_figures_v3.f3_rows(cells)
    assert len(rows) == len(cells) == 6
    # cost / T: divided by T = 20 even where the full-acquisition cost is 30 (dsA) or 40 (inv)
    want = [s["cascade_mean_test_cost"] / m["T"] for m, a, dl, b, s in cells]
    assert [r["dep"] for r in rows] == pytest.approx(want) and [p.get_height() for p in ax.patches] == pytest.approx(want)
    by = {r["name"]: r for r in rows}
    assert by["dsA greedy s0"]["dep"] == pytest.approx(0.75) and by["dsA greedy s0"]["marg"] == pytest.approx(0.25)
    assert by["dsA greedy s0"]["mon"] == pytest.approx(0.4) and by["dsA greedy s0"]["full"] == pytest.approx(1.5)
    assert by["dsK inv s0"]["dep"] == pytest.approx(1.2) and by["dsK inv s0"]["full"] == pytest.approx(2.0)
    assert all(r["n_seeds"] == 1 and r["dep_lo"] == r["dep_hi"] == r["dep"] for r in rows)
    assert [t.get_text() for t in ax.get_xticklabels()] == [r["name"] for r in rows]
    # full acquisition != T in some cells: the gray full-acquisition marks are drawn, at full / T
    full = [ln for ln in ax.lines if ln.get_label() == "full acquisition"]
    assert len(full) == 1 and list(full[0].get_ydata()) == pytest.approx([r["full"] for r in rows])
    assert not [c for c in ax.containers if isinstance(c, ErrorbarContainer)]       # no seed error bars
    e2 = [t.get_text() for t in ax.texts]
    assert e2 == [f"{s['marginal_max_stratum_over_alpha_mean']:.2f}" for *_, s in cells] and "2.20" in e2
    assert "E2" in ax.get_xlabel() and "mean over seeds" not in ax.get_xlabel()


def test_f3_seed_means(mdir, tmp_path, monkeypatch):
    from matplotlib.container import ErrorbarContainer
    saved = _record_figures(monkeypatch)
    d = tmp_path / "seeds3"
    # 2 datasets x 2 policies x 3 seeds; T = 20, full acquisition 30 (!= T)
    for ds in ("dsP", "dsQ"):
        for pol in ("greedy_entropy", "random"):
            for seed in (0, 1, 2):
                c = 10.0 + 2.0 * seed + (4.0 if ds == "dsQ" else 0.0) + (1.0 if pol == "random" else 0.0)
                _write(d, _metrics(ds, pol, seed=seed, summary=_summary(
                    c, tier=(0.0, 1.0 - 0.1 * seed, 0.0, 0.1 * seed), marg_cost=4.0 + seed, full_cost=30.0,
                    e2=1.0 + 0.3 * seed), draws=[]))
    cells = make_figures_v3.load_cells(d, "dep", "uniform")
    assert len(cells) == 12
    rows = make_figures_v3.f3_rows(cells)
    assert [r["name"] for r in rows] == ["dsP greedy (3 seeds)", "dsP random (3 seeds)", "dsQ greedy (3 seeds)",
                                         "dsQ random (3 seeds)"]
    p = rows[0]                                       # dsP greedy: costs 10 / 12 / 14 over T = 20
    assert p["n_seeds"] == 3
    assert (p["dep"], p["dep_lo"], p["dep_hi"]) == pytest.approx((0.6, 0.5, 0.7))
    assert p["marg"] == pytest.approx(0.25) and p["mon"] == pytest.approx(0.4) and p["full"] == pytest.approx(1.5)
    assert p["tiers"]["1"] == pytest.approx(0.9) and p["tiers"]["3"] == pytest.approx(0.1)
    assert p["e2"] == pytest.approx(1.3)
    out = tmp_path / "figs"
    assert make_figures_v3.main(["--metrics-dir", str(d), "--output-dir", str(out)]) == 0
    assert (out / "F3_cascade.pdf").stat().st_size > 0
    a1, a2 = saved["F3_cascade.pdf"].axes
    assert len(a2.patches) == len(rows) == 4          # one bar per (dataset, policy), not per cell
    assert len(a1.patches) == 4 * 4                   # 4 stacked tiers per bar
    assert [x.get_height() for x in a2.patches] == pytest.approx([r["dep"] for r in rows])
    assert [t.get_text() for t in a2.get_xticklabels()] == [r["name"] for r in rows]
    assert [t.get_text() for t in a2.texts] == ["1.30"] * 4
    assert len([c for c in a2.containers if isinstance(c, ErrorbarContainer)]) == 1
    assert "mean over seeds" in a2.get_xlabel()
    # mixed: dsA has two seeds in mdir, the others one -> one bar per (dataset, policy) throughout
    mixed = make_figures_v3.f3_rows(make_figures_v3.load_cells(mdir, "dep", "uniform"))
    assert len(mixed) == 6 and mixed[0]["name"] == "dsA greedy (2 seeds)"
    assert (mixed[0]["dep"], mixed[0]["dep_lo"], mixed[0]["dep_hi"]) == pytest.approx((0.8, 0.75, 0.85))
    assert mixed[0]["e2"] == pytest.approx((2.2 + 1.5) / 2)
    assert {r["name"] for r in mixed[1:]} == {"dsK sl (1 seed)", "dsK near (1 seed)", "dsK intr (1 seed)",
                                              "dsK inv (1 seed)", "dsZ greedy (1 seed)"}


# ---- alpha_margin_summary_v3 ---------------------------------------------------------------------------------------

def test_alpha_margin_summary(tmp_path, monkeypatch):
    rr, cfg, out = tmp_path / "rr", tmp_path / "configs", tmp_path / "tables"
    cfg.mkdir()
    prim, am02 = rr / "metrics_v3", rr / "metrics_v3_alpha_margin02"
    # full acquisition 30 / 40 != T = 20: deployed_cost_over_T must divide by T
    _write(prim, _metrics("dsA", alpha=0.15, T=20, summary=_summary(15.0, tier=(0.0, 0.25, 0.0, 0.75), full_cost=30.0),
                          draws=[], lambda_ref=0.7, G=4))
    _write(prim, _metrics("dsB", alpha=0.1, summary=_summary(4.0), draws=[]))
    _write(prim, _metrics("dsC", alpha=0.1, summary=_summary(6.0), draws=[]))
    _write(prim, _metrics("dsA", seed=1, alpha=0.15, summary=_summary(15.0), draws=[]))   # other seed: not a row
    _write(am02, _metrics("dsA", alpha=0.08, summary=_summary(20.0, tier=(0.1, 0.0, 0.0, 0.9), full_cost=40.0),
                          draws=[]))
    (cfg / "committed_v3_dsA_ts0.json").write_text(json.dumps({"alpha": 0.15, "floor": {"estimate": 0.06},
                                                               "design_margin": 0.05}))
    (cfg / "committed_v3_dsB_ts0.json").write_text(json.dumps({"alpha": 0.1, "floor": {"estimate": 0.004},
                                                               "design_margin": 0.05}))
    # dsC: the refusal boundary (the real Imagenette am02 case): alpha_from_floor(0.0299, 0.02, 0.01) = 0.05, exactly
    # the design margin -> refused (commit_v3: alpha <= margin -> rc 7)
    (cfg / "committed_v3_dsC_ts0.json").write_text(json.dumps({"alpha": 0.1, "floor": {"estimate": 0.0299},
                                                               "design_margin": 0.05}))
    (cfg / "committed_v3_am02_dsA_ts0.json").write_text(json.dumps({"alpha": 0.08}))
    (cfg / "committed_v3_am10_dsA_ts0.json").write_text(json.dumps({"alpha": 0.2}))
    monkeypatch.setenv("RESULTS_ROOT", str(rr))
    assert alpha_margin_summary_v3.main(["--configs-dir", str(cfg), "--output-dir", str(out)]) == 0
    rows = {r["dataset"]: r for r in _rows(out / "TABLE_E9_alpha_margin.csv")}
    assert set(rows) == {"dsA", "dsB", "dsC"}
    a, b, c = rows["dsA"], rows["dsB"], rows["dsC"]
    assert (a["am02_status"], a["am05_status"], a["am10_status"]) == ("ok", "ok", "TBD-RUN")
    assert float(a["am05_tier1"]) == 0.25 and float(a["am05_tier3"]) == 0.75
    assert float(a["am05_deployed_cost_over_T"]) == pytest.approx(0.75)      # 15 / T = 20, not 15 / 30
    assert float(a["am02_deployed_cost_over_T"]) == pytest.approx(1.0)       # 20 / T = 20, not 20 / 40
    assert float(a["am05_lambda_ref"]) == 0.7 and a["am05_G"] == "4"
    assert float(a["am02_alpha"]) == 0.08 and float(a["am02_certified_deployment"]) == pytest.approx(0.9)
    assert float(a["am10_alpha"]) == 0.2 and a["am10_tier1"] == ""
    # dsB: no am02 commit and alpha_from_floor(0.004, 0.02, 0.01) = 0.03 <= 0.05 -> refused; no am10 commit and
    # alpha_from_floor(0.004, 0.10, 0.05) = 0.15 > 0.05 -> not committed yet
    assert (b["am02_status"], b["am05_status"], b["am10_status"]) == ("refused", "ok", "TBD-RUN (not committed)")
    assert float(b["am02_alpha"]) == pytest.approx(0.03) and float(b["am10_alpha"]) == pytest.approx(0.15)
    # dsC: alpha 0.05 == design margin 0.05 -> refused, not "TBD-RUN (not committed)"
    assert (c["am02_status"], c["am05_status"], c["am10_status"]) == ("refused", "ok", "TBD-RUN (not committed)")
    assert float(c["am02_alpha"]) == 0.05 and float(c["am10_alpha"]) == pytest.approx(0.15)
    md = (out / "TABLE_E9_alpha_margin.md").read_text(encoding="utf-8")
    assert "refused: alpha = 0.03 <= design margin 0.05 (commit_v3 rc 7)" in md
    assert "| dsC | greedy_entropy | refused: alpha = 0.05 <= design margin 0.05 (commit_v3 rc 7) |" in md
    assert "TBD-RUN (not committed): alpha = 0.15 by the rule" in md
    assert "TBD-RUN: committed alpha = 0.20, not swept" in md
    assert "alpha 0.15: tier1 0.25, tier3 0.75, cert 1.00, cost/T 0.75" in md
    # without RESULTS_ROOT and without the dir flags the script refuses to guess
    monkeypatch.delenv("RESULTS_ROOT")
    with pytest.raises(SystemExit):
        alpha_margin_summary_v3.main(["--configs-dir", str(cfg), "--output-dir", str(out)])


def test_seed_flags_flags_tier1_range_above_quarter(tmp_path):
    """TABLE_E4_seed_flags (round 3b, Task J.3): a (dataset, policy) is flagged when its tier-1 share differs across
    seeds by more than 0.25; per-seed r_full comes from the E3 audit rows; single-seed cells get no row."""
    def e4(ds, seed, t1):
        return {"dataset": ds, "policy": "greedy_entropy", "seed": seed, "alpha": 0.15, "tier1": t1, "tier3": 1 - t1}

    def e3(ds, seed, r):
        return {"dataset": ds, "policy": "greedy_entropy", "seed": seed, "k": 2, "n_k": 900, "r_full": r,
                "rmin_thr": r - 0.01, "verdict": "feasible"}

    rows = make_tables_v3.seed_flags(
        [e4("dsF", 0, 0.12), e4("dsF", 1, 0.40), e4("dsF", 2, 0.05), e4("dsQ", 0, 0.50), e4("dsQ", 2, 0.75),
         e4("dsS", 0, 1.0)],
        [e3("dsF", 0, 0.133), e3("dsF", 1, 0.121), e3("dsF", 2, 0.140), e3("dsQ", 0, 0.1), e3("dsQ", 2, 0.1)])
    by = {r["dataset"]: r for r in rows}
    assert set(by) == {"dsF", "dsQ"}                                   # dsS has one seed only
    assert by["dsF"]["flag"] == "FLAG" and by["dsF"]["tier1_range"] == pytest.approx(0.35)
    assert by["dsF"]["seeds"] == "0 / 1 / 2" and by["dsF"]["r_full"] == "0.133 / 0.121 / 0.140"
    assert by["dsQ"]["flag"] == "" and by["dsQ"]["tier1_range"] == pytest.approx(0.25)   # exactly 0.25: not flagged


def test_seed_groups_for_f2_f6(mdir, tmp_path):
    """F2 / F6 (round 3b): one bar per cell while every (dataset, policy) has one seed (names unchanged), one bar per
    (dataset, policy) with seed means once any has several; both figures are written in either mode."""
    cells = make_figures_v3.load_cells(mdir, "dep", "uniform")
    groups, multi = make_figures_v3.seed_groups(cells)
    assert multi                                                       # dsA has seeds 0 and 1
    names = [n for n, _ in groups]
    assert "dsA\ngreedy_entropy (2 seeds)" in names and len(names) == len({(c[0]["dsname"], c[0]["policy"]) for c in cells})
    single = [c for c in cells if c[0]["dsname"] != "dsA"]
    g1, multi1 = make_figures_v3.seed_groups(single)
    assert not multi1 and [n for n, _ in g1] == [f"{c[0]['dsname']}\n{c[0]['policy']} s{c[0]['train_seed']}" for c in single]
    for cs, sub in ((cells, "multi"), (single, "single")):
        out = tmp_path / sub
        out.mkdir()
        make_figures_v3.fig_blindness(cs, out)
        make_figures_v3.fig_violations(cs, out)
        assert (out / "F2_blindness.pdf").exists() and (out / "F6_violations.pdf").exists()
