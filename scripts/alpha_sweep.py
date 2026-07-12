#!/usr/bin/env python
"""Alpha-sweep (post-hoc on cached rollouts) -- Phase-5 corrected version.

For each dataset (backbone train_seed ts, honest greedy, primary cost scheme)
sweep the risk target alpha over a grid anchored to the COMMITTED probe floor.
Everything is post-hoc on the frozen pool cache and the pre-committed stratum
edges -- no retraining, no re-rollout.

Phase-5 corrections (Task 1):
  * --include-committed-alpha : each dataset's committed alpha is an EXPLICIT
    grid point, so the committed target is MEASURED, never interpolated (the
    MiniBooNE contradiction in the first frozen file came from inferring the
    committed target's side from the nearest grid point).
  * --bracket : after the coarse pass, bisect (3 refinement points) between
    the last unsafe and first safe alpha, so the reported transition carries a
    stated resolution, e.g. "transition in (0.140, 0.150], resolution 0.010".
  * automated H2 cross-check: the plugin violation measured at the committed
    alpha must EQUAL the plugin violation in the metrics JSON (H2) for the
    same cell -- asserted per dataset and written into the transitions CSV so
    the two tables can never silently diverge again.

Per alpha, over the n_resplits cal/test resplits: plugin violation (Wilson
95% CI); cafa_marginal violation/abstention/cost ratio; oracle-cheapest cost;
CAFA-IUT abstention + cost premium; number of alpha-infeasible strata at
lambda_ref = 0.9.

Outputs: analysis_v2/alpha_sweep.csv (one row per evaluated alpha, with
is_committed / is_bracket flags), analysis_v2/alpha_sweep_transitions.csv
(one row per dataset: measured verdict at the committed alpha + bracketed
transition + H2 cross-check), analysis_v2/ALPHA_SWEEP.md, figures_v2/F5_<ds>.*

ENVIRONMENT RULE: anchor to the committed floor the run sees -- cluster
anchors for canonical numbers; local sweeps are development artifacts.

Usage:
    python scripts/alpha_sweep.py --all --grid-from-floor \
        --include-committed-alpha --bracket [--metrics-dir results_committed/metrics]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from cafa import config  # noqa: E402
from cafa.baselines import oracle_cheapest_valid_select, plugin_threshold_select  # noqa: E402
from cafa.metrics import reference_buckets  # noqa: E402
from cafa.pool import cum_cost_from_order, load_pool_cache  # noqa: E402
from cafa.risk_control import ltt_select  # noqa: E402
from cafa.risk_control_ext import iut_select  # noqa: E402
from cafa.splits import probe_eval_split, resplit_cal_test  # noqa: E402

_DATASETS = ["mnist", "tabular:adult", "tabular:MiniBooNE", "tabular:spambase"]
_DEFAULT_OFFSETS = (0.02, 0.05, 0.08, 0.11, 0.15, 0.20)
_LR_STRATA = "0.9"
_Z = 1.96
_BISECT_STEPS = 3


def dsname_of(dataset: str) -> str:
    if dataset.startswith("tabular:"):
        return "tabular-" + dataset.split(":", 1)[1]
    return dataset


def wilson(k: int, n: int, z: float = _Z):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def cp_lcb(k: int, n: int) -> float:
    from scipy.stats import beta
    return 0.0 if k == 0 else float(beta.ppf(0.05, int(k), int(n) - int(k) + 1))


def stop_index_matrix(scores, grid):
    scores = np.asarray(scores, dtype=float)
    grid = np.asarray(grid, dtype=float)
    T = scores.shape[1] - 1
    crossed = scores[:, :, None] >= grid[None, None, :]
    any_cross = crossed.any(axis=1)
    first = crossed.argmax(axis=1)
    return np.where(any_cross, first, T).astype(int)


def _fmt(x, nd=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "n/a"
    return f"{x:.{nd}f}"


def h2_plugin_violation(metrics_dir: Path, dsname: str, ts: int, policy: str,
                        alpha: float) -> "float | None":
    """Plugin violation in the metrics JSON (H2), lambda_ref block 0.9, primary scheme."""
    p = Path(metrics_dir) / f"{dsname}_ts{ts}_{policy}.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    blk = data["lambda_refs"].get(_LR_STRATA)
    if blk is None:
        return None
    scheme = "inverse_info" if "inverse_info" in data["meta"]["schemes"] else "uniform"
    risks = [r["schemes"][scheme]["plugin"]["realized_risk"] for r in blk["resplits"]]
    return float(np.mean([1.0 if (x is not None and x > alpha) else 0.0 for x in risks]))


def sweep_one(dataset: str, train_seed: int, policy: str, offsets, cfg, paths,
              include_committed: bool, bracket: bool, metrics_dir: Path):
    """Sweep one dataset; returns (rows sorted by alpha, transition record)."""
    ts = int(train_seed)
    dsname = dsname_of(dataset)
    method_cfg = cfg["method"]
    g = method_cfg.get("grid", {"g_min": 0.0, "g_max": 1.0, "n": 100})
    grid = np.linspace(float(g["g_min"]), float(g["g_max"]), int(g["n"]))
    delta = float(method_cfg.get("delta", 0.10))
    procedure = method_cfg.get("procedure", "fixed_sequence")
    score = method_cfg.get("procedure_score", "softmax")
    pv = cfg.get("protocol_v2", {})
    probe_frac = float(pv.get("probe_frac", 0.10))
    probe_seed = int(pv.get("probe_seed", 777))
    n_resplits = int(pv.get("n_resplits", 100))
    cal_frac = float(pv.get("cal_frac_of_eval", 0.5))

    committed_path = Path("configs") / f"committed_v2_{dsname}_ts{ts}.json"
    committed = json.loads(committed_path.read_text())
    floor = float(committed["floor"]["estimate"])
    committed_alpha = float(committed["alpha"])
    feature_costs_by_scheme = {
        s: np.asarray(v, dtype=float) for s, v in committed["feature_costs_by_scheme"].items()
    }
    primary_scheme = "inverse_info" if "inverse_info" in feature_costs_by_scheme else "uniform"

    cache_path = Path(paths.results_root) / "pool_v2" / f"{dsname}_ts{ts}_{policy}_{score}.npz"
    cache = load_pool_cache(cache_path)
    n_pool = cache["scores"].shape[0]
    _, eval_pos = probe_eval_split(np.arange(n_pool), probe_frac, probe_seed)
    scores_e = np.asarray(cache["scores"])[eval_pos]
    correct_e = np.asarray(cache["correct"])[eval_pos]
    order_e = np.asarray(cache["order"])[eval_pos]
    n_eval, Tp1 = scores_e.shape
    T = Tp1 - 1

    s_full = stop_index_matrix(scores_e, grid)
    rows_ix = np.arange(n_eval)[:, None]
    losses_full = 1.0 - correct_e[rows_ix, s_full]
    cc = cum_cost_from_order(order_e, feature_costs_by_scheme[primary_scheme])
    costs_full = cc[rows_ix, s_full]
    full_acq_loss = 1.0 - correct_e[:, T]
    full_cost = float(cc[:, T].mean())

    q5 = committed["edges"].get(policy, {}).get(_LR_STRATA, {}).get("quantile", {}).get("5", [])
    bucket_full, _ = reference_buckets(scores_e, float(_LR_STRATA), 5, 50,
                                       edges=np.asarray(q5, dtype=float))
    stratum_stats = []
    for k in np.unique(bucket_full):
        mask = bucket_full == k
        n_k = int(mask.sum())
        err = int(round(float(np.sum(full_acq_loss[mask]))))
        stratum_stats.append((n_k, err))

    resplit_ix = [resplit_cal_test(np.arange(n_eval), rs, cal_frac) for rs in range(n_resplits)]

    def eval_alpha(alpha: float) -> dict:
        n_infeasible = sum(1 for n_k, err in stratum_stats if n_k > 0 and cp_lcb(err, n_k) > alpha)
        marg_viol = marg_abst = plug_viol = iut_abst = 0
        marg_costs, plug_costs, iut_costs, oracle_costs = [], [], [], []
        for cal_local, test_local in resplit_ix:
            lc, lt = losses_full[cal_local], losses_full[test_local]
            cc_, ct = costs_full[cal_local], costs_full[test_local]
            fat = full_acq_loss[test_local]
            full_ct = float(cc[test_local][:, T].mean())

            sel = ltt_select(lc, cc_, grid, alpha, delta, procedure=procedure)
            if sel.lambda_idx is None:
                marg_abst += 1
                m_risk, m_cost = float(fat.mean()), full_ct
            else:
                m_risk = float(lt[:, sel.lambda_idx].mean())
                m_cost = float(ct[:, sel.lambda_idx].mean())
            if m_risk > alpha:
                marg_viol += 1
            marg_costs.append(m_cost)

            plug = plugin_threshold_select(lc, cc_, grid, alpha)
            if plug is None:
                p_risk, p_cost = float(fat.mean()), full_ct
            else:
                p_risk = float(lt[:, plug].mean())
                p_cost = float(ct[:, plug].mean())
            if p_risk > alpha:
                plug_viol += 1
            plug_costs.append(p_cost)

            iut = iut_select(lc, cc_, grid, alpha, delta, bucket_full[cal_local],
                             procedure=procedure)
            if iut.lambda_idx is None:
                iut_abst += 1
                iut_costs.append(full_ct)
            else:
                iut_costs.append(float(ct[:, iut.lambda_idx].mean()))

            oc = oracle_cheapest_valid_select(lt, ct, grid, alpha)
            oracle_costs.append(full_ct if oc is None else float(ct[:, oc].mean()))

        n = n_resplits
        pv_, plo, phi = wilson(plug_viol, n)
        mv_, mlo, mhi = wilson(marg_viol, n)
        marg_cost = float(np.mean(marg_costs))
        iut_cost = float(np.mean(iut_costs))
        return {
            "dataset": dsname, "train_seed": ts, "policy": policy,
            "scheme": primary_scheme, "floor": floor, "committed_alpha": committed_alpha,
            "alpha": round(alpha, 4), "alpha_minus_floor": round(alpha - floor, 4),
            "is_committed": int(abs(alpha - committed_alpha) < 1e-9),
            "is_bracket": 0,
            "plugin_viol": pv_, "plugin_lo": plo, "plugin_hi": phi,
            "marg_viol": mv_, "marg_lo": mlo, "marg_hi": mhi,
            "marg_abstain": marg_abst / n,
            "marg_cost": marg_cost, "marg_cost_ratio_full": marg_cost / full_cost,
            "oracle_cost": float(np.mean(oracle_costs)),
            "iut_abstain": iut_abst / n, "iut_cost": iut_cost,
            "iut_cost_ratio_full": iut_cost / full_cost,
            "iut_premium_vs_marginal": (iut_cost / marg_cost) if marg_cost else float("nan"),
            "n_infeasible_strata_lr0.9": n_infeasible,
            "delta": delta, "n_resplits": n,
        }

    alphas = {round(min(0.999, floor + float(o)), 4) for o in offsets}
    if include_committed:
        alphas.add(round(committed_alpha, 4))
    rows = {}
    for a in sorted(alphas):
        rows[a] = eval_alpha(a)
        r = rows[a]
        print(f"[alpha-sweep] {dsname} alpha={a:.3f} (floor+{a - floor:.3f})"
              f"{' [committed]' if r['is_committed'] else ''}: "
              f"plugin_viol={r['plugin_viol']:.2f} marg_viol={r['marg_viol']:.2f} "
              f"iut_abstain={r['iut_abstain']:.2f} infeasible@0.9={r['n_infeasible_strata_lr0.9']}",
              flush=True)

    # ---- bracket the plugin transition (safe := plugin_viol <= delta) ----
    delta_v = rows[next(iter(rows))]["delta"]
    transition_lo = transition_hi = None
    if bracket:
        srt = sorted(rows)
        first_safe = next((i for i, a in enumerate(srt) if rows[a]["plugin_viol"] <= delta_v), None)
        if first_safe is None:
            transition_lo, transition_hi = srt[-1], None       # never safe in range
        elif first_safe == 0:
            transition_lo, transition_hi = None, srt[0]        # safe from the smallest alpha
        else:
            lo, hi = srt[first_safe - 1], srt[first_safe]
            for _ in range(_BISECT_STEPS):
                mid = round((lo + hi) / 2.0, 4)
                if mid in rows or mid in (lo, hi):
                    break
                r = eval_alpha(mid)
                r["is_bracket"] = 1
                rows[mid] = r
                print(f"[alpha-sweep] {dsname} bracket alpha={mid:.4f}: "
                      f"plugin_viol={r['plugin_viol']:.2f}", flush=True)
                if r["plugin_viol"] <= delta_v:
                    hi = mid
                else:
                    lo = mid
            transition_lo, transition_hi = lo, hi

    # ---- measured verdict at the committed alpha + H2 cross-check ----
    committed_key = round(committed_alpha, 4)
    crow = rows.get(committed_key)
    h2_v = h2_plugin_violation(metrics_dir, dsname, ts, policy, committed_alpha)
    crosscheck = None
    if crow is not None and h2_v is not None:
        crosscheck = abs(crow["plugin_viol"] - h2_v) < 1e-9
        status = "PASS" if crosscheck else "FAIL"
        print(f"[alpha-sweep] {dsname} H2 cross-check: sweep plugin viol at committed "
              f"alpha = {crow['plugin_viol']:.3f}, H2 = {h2_v:.3f} -> {status}", flush=True)
        assert crosscheck, (
            f"CROSS-TABLE INCONSISTENCY on {dsname}: alpha-sweep plugin violation at the "
            f"committed alpha ({crow['plugin_viol']:.4f}) != H2 table ({h2_v:.4f})."
        )

    transition = {
        "dataset": dsname, "train_seed": ts, "floor": floor,
        "committed_alpha": committed_alpha,
        "plugin_viol_at_committed": None if crow is None else crow["plugin_viol"],
        "plugin_lo_at_committed": None if crow is None else crow["plugin_lo"],
        "plugin_hi_at_committed": None if crow is None else crow["plugin_hi"],
        "verdict_at_committed": (None if crow is None else
                                 ("SAFE" if crow["plugin_viol"] <= delta_v else "UNSAFE")),
        "transition_lo": transition_lo, "transition_hi": transition_hi,
        "resolution": (None if (transition_lo is None or transition_hi is None)
                       else round(transition_hi - transition_lo, 4)),
        "h2_plugin_viol": h2_v,
        "h2_crosscheck": ("PASS" if crosscheck else
                          ("FAIL" if crosscheck is not None else "n/a")),
        "delta": delta_v,
    }
    return [rows[a] for a in sorted(rows)], transition


def make_f5(rows_by_ds, transitions, fig_dir: Path):
    for dsname, rows in rows_by_ds.items():
        rows = sorted(rows, key=lambda r: r["alpha"])
        a = [r["alpha"] for r in rows]
        delta = rows[0]["delta"]
        committed_alpha = rows[0]["committed_alpha"]
        floor = rows[0]["floor"]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

        pv = [r["plugin_viol"] for r in rows]
        perr = [[r["plugin_viol"] - r["plugin_lo"] for r in rows],
                [r["plugin_hi"] - r["plugin_viol"] for r in rows]]
        mv = [r["marg_viol"] for r in rows]
        merr = [[r["marg_viol"] - r["marg_lo"] for r in rows],
                [r["marg_hi"] - r["marg_viol"] for r in rows]]
        ax1.errorbar(a, pv, yerr=perr, marker="o", capsize=3, label="plugin")
        ax1.errorbar(a, mv, yerr=merr, marker="s", capsize=3, label="cafa_marginal")
        crow = next((r for r in rows if r["is_committed"]), None)
        if crow is not None:
            ax1.scatter([crow["alpha"]], [crow["plugin_viol"]], marker="*", s=200,
                        zorder=5, label="plugin AT committed alpha (measured)")
        tr = transitions.get(dsname, {})
        if tr.get("transition_lo") is not None and tr.get("transition_hi") is not None:
            ax1.axvspan(tr["transition_lo"], tr["transition_hi"], alpha=0.15, color="orange",
                        label=f"transition bracket (res {tr['resolution']:g})")
        ax1.axhline(delta, linestyle="--", color="k", label=f"delta={delta:g}")
        ax1.axvline(committed_alpha, linestyle=":", color="gray",
                    label=f"committed alpha={committed_alpha:g}")
        ax1.axvline(floor, linestyle="-", color="gray", linewidth=0.8, label=f"floor={floor:.3f}")
        ax1.set_xlabel("alpha"); ax1.set_ylabel("violation rate (Wilson 95%)")
        ax1.set_title("safe/unsafe transition (measured)")
        ax1.legend(fontsize=6)

        ab = [r["iut_abstain"] for r in rows]
        pr = [r["iut_premium_vs_marginal"] for r in rows]
        ax2.plot(a, ab, marker="o", label="IUT abstention rate")
        ax2.set_xlabel("alpha"); ax2.set_ylabel("IUT abstention rate")
        ax2b = ax2.twinx()
        ax2b.plot(a, pr, marker="^", color="tab:red", label="IUT cost premium (x marginal)")
        ax2b.set_ylabel("IUT cost premium (x marginal)")
        ax2.axvline(committed_alpha, linestyle=":", color="gray")
        h1, l1 = ax2.get_legend_handles_labels()
        h2, l2 = ax2b.get_legend_handles_labels()
        ax2.legend(h1 + h2, l1 + l2, fontsize=7)
        ax2.set_title("price of honesty")

        fig.suptitle(f"F5 alpha-sweep -- {dsname} ts{rows[0]['train_seed']} "
                     f"({rows[0]['policy']}, {rows[0]['scheme']})")
        fig.tight_layout()
        fig.savefig(fig_dir / f"F5_{dsname}.pdf")
        fig.savefig(fig_dir / f"F5_{dsname}.png", dpi=150)
        plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAFA v2 alpha-sweep (post-hoc, corrected).")
    ap.add_argument("--dataset", default=None, help="mnist | tabular:<name>")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--train-seed", type=int, default=0)
    ap.add_argument("--policy", default="greedy_entropy")
    ap.add_argument("--grid-from-floor", action="store_true",
                    help="anchor the alpha grid to the committed probe floor (required mode).")
    ap.add_argument("--include-committed-alpha", action="store_true",
                    help="measure at the committed alpha explicitly (Phase-5 correction).")
    ap.add_argument("--bracket", action="store_true",
                    help="bisect the plugin transition to a stated resolution.")
    ap.add_argument("--offsets", default=",".join(str(o) for o in _DEFAULT_OFFSETS))
    ap.add_argument("--metrics-dir", default="metrics_v2",
                    help="metrics JSONs for the H2 cross-check (use results_committed/metrics "
                         "on the cluster).")
    ap.add_argument("--out", default="analysis_v2")
    ap.add_argument("--figures", default="figures_v2")
    args = ap.parse_args(argv)

    if not args.grid_from_floor:
        print("ERROR: only --grid-from-floor mode is supported.", file=sys.stderr)
        return 1
    datasets = _DATASETS if args.all else ([args.dataset] if args.dataset else [])
    if not datasets:
        print("ERROR: provide --dataset or --all.", file=sys.stderr)
        return 1
    offsets = [float(x) for x in args.offsets.split(",") if x.strip()]

    cfg = config.load_experiment()
    paths = config.load_paths()
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = Path(args.figures); fig_dir.mkdir(parents=True, exist_ok=True)

    all_rows, rows_by_ds, transitions = [], {}, {}
    for ds in datasets:
        rows, tr = sweep_one(ds, args.train_seed, args.policy, offsets, cfg, paths,
                             args.include_committed_alpha, args.bracket,
                             Path(args.metrics_dir))
        all_rows.extend(rows)
        rows_by_ds[dsname_of(ds)] = rows
        transitions[dsname_of(ds)] = tr

    with open(out_dir / "alpha_sweep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader(); w.writerows(all_rows)
    with open(out_dir / "alpha_sweep_transitions.csv", "w", newline="") as f:
        trs = list(transitions.values())
        w = csv.DictWriter(f, fieldnames=list(trs[0].keys()))
        w.writeheader(); w.writerows(trs)

    # ---- markdown report ----
    n_unsafe = sum(1 for t in transitions.values() if t["verdict_at_committed"] == "UNSAFE")
    lines = ["# CAFA v2 -- ALPHA SWEEP (corrected: measured at the committed alpha)\n",
             "_Grid anchored to the committed probe floor, with the committed alpha as an "
             "explicit MEASURED grid point and the plugin transition bracketed by bisection. "
             "The verdict at the committed target is by measurement, never inference; the "
             "plugin violation at the committed alpha is asserted equal to the H2 table "
             f"(cross-check column). delta = {all_rows[0]['delta']:g}; n_resplits = "
             f"{all_rows[0]['n_resplits']}._\n"]
    for dsname, rows in rows_by_ds.items():
        rows = sorted(rows, key=lambda r: r["alpha"])
        tr = transitions[dsname]
        lines.append(f"## {dsname} (ts{rows[0]['train_seed']}, {rows[0]['policy']}, "
                     f"{rows[0]['scheme']}; floor = {_fmt(rows[0]['floor'])}, "
                     f"committed alpha = {rows[0]['committed_alpha']:g})\n")
        lines.append("| alpha | note | plugin viol [95% CI] | marginal viol [95% CI] | "
                     "marg abstain | marg cost/full | IUT abstain | IUT cost/full | "
                     "infeasible strata @0.9 |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            note = "COMMITTED" if r["is_committed"] else ("bracket" if r["is_bracket"] else "")
            lines.append(
                f"| {r['alpha']:.4f} | {note} | "
                f"{_fmt(r['plugin_viol'], 2)} [{_fmt(r['plugin_lo'], 2)}, {_fmt(r['plugin_hi'], 2)}] | "
                f"{_fmt(r['marg_viol'], 2)} [{_fmt(r['marg_lo'], 2)}, {_fmt(r['marg_hi'], 2)}] | "
                f"{_fmt(r['marg_abstain'], 2)} | {_fmt(r['marg_cost_ratio_full'], 3)} | "
                f"{_fmt(r['iut_abstain'], 2)} | {_fmt(r['iut_cost_ratio_full'], 3)} | "
                f"{r['n_infeasible_strata_lr0.9']} |")
        lines.append("")
        if tr["transition_hi"] is None:
            tr_txt = f"plugin never becomes safe in the swept range (last point {tr['transition_lo']:.4f})"
        elif tr["transition_lo"] is None:
            tr_txt = f"plugin already safe at the smallest swept alpha ({tr['transition_hi']:.4f}); transition below the range"
        else:
            tr_txt = (f"transition in ({tr['transition_lo']:.4f}, {tr['transition_hi']:.4f}], "
                      f"resolution {tr['resolution']:g}")
        lines.append(f"- MEASURED at the committed alpha {tr['committed_alpha']:g}: plugin "
                     f"violation {_fmt(tr['plugin_viol_at_committed'], 3)} "
                     f"[{_fmt(tr['plugin_lo_at_committed'], 3)}, {_fmt(tr['plugin_hi_at_committed'], 3)}] "
                     f"-> **{tr['verdict_at_committed']}**; {tr_txt}; H2 cross-check: "
                     f"{tr['h2_crosscheck']} (H2 value {_fmt(tr['h2_plugin_viol'], 3)}).")
        lines.append("")
    lines.append(f"**Corrected headline: the alpha at which the uncorrected heuristic flips "
                 f"from safe to unsafe lands at a different, a-priori unknowable offset on "
                 f"each dataset, and the principled fixed rule lands inside the UNSAFE regime "
                 f"on {n_unsafe} of {len(transitions)} datasets (by measurement).**")
    (out_dir / "ALPHA_SWEEP.md").write_text("\n".join(lines))

    make_f5(rows_by_ds, transitions, fig_dir)
    print(f"[alpha-sweep] wrote ALPHA_SWEEP.md, alpha_sweep.csv, "
          f"alpha_sweep_transitions.csv, F5_* (committed-target UNSAFE on "
          f"{n_unsafe}/{len(transitions)}).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
