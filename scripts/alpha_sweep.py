#!/usr/bin/env python
"""Phase 3 companion -- the alpha-sweep (post-hoc on cached rollouts; Task 2).

For each dataset (backbone train_seed ts, honest greedy, primary cost scheme)
sweep the risk target alpha over a grid anchored to the COMMITTED probe floor
(offsets above the floor). Note the committed fixed-rule alpha is
ceil_0.05(floor + 0.05), which generally sits ABOVE the +0.05 grid point; it is
marked separately in the tables and on F5.
Everything is post-hoc on the frozen pool cache and the pre-committed stratum
edges -- no retraining, no re-rollout.

Per alpha, over the n_resplits cal/test resplits:
  * plugin violation rate (Wilson 95% CI)  -- the safe/unsafe transition curve;
  * cafa_marginal violation rate (must stay <= delta everywhere), abstention,
    mean cost + cost ratio vs full;
  * oracle-cheapest cost (the floor);
  * CAFA-IUT abstention rate and cost premium vs marginal -- the
    "price of honesty" curve;
  * number of alpha-infeasible strata at lambda_ref = 0.9 (population CP LCB).

Outputs: analysis_v2/alpha_sweep.csv, analysis_v2/ALPHA_SWEEP.md (with the
sentence-ready plugin-transition statement per dataset), figures_v2/F5_<ds>.*

ENVIRONMENT RULE: the grid is anchored to the floor in the committed JSON the
run sees -- anchor to the CLUSTER floor for canonical numbers; a sweep around
a local floor is a development artifact only.

Usage:
    python scripts/alpha_sweep.py --dataset tabular:adult --grid-from-floor
    python scripts/alpha_sweep.py --all --grid-from-floor
    python scripts/alpha_sweep.py --all --grid-from-floor --offsets 0.02,0.05,0.08,0.11,0.15,0.20
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
_LR_STRATA = "0.9"      # lambda_ref used for the infeasible-strata count + IUT
_Z = 1.96


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


def sweep_one(dataset: str, train_seed: int, policy: str, offsets, cfg, paths):
    """Run the alpha-sweep for one dataset; returns per-alpha aggregate rows."""
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
    rows = np.arange(n_eval)[:, None]
    losses_full = 1.0 - correct_e[rows, s_full]
    cc = cum_cost_from_order(order_e, feature_costs_by_scheme[primary_scheme])
    costs_full = cc[rows, s_full]
    full_acq_loss = 1.0 - correct_e[:, T]
    full_cost = float(cc[:, T].mean())

    # Pre-committed quantile-5 edges at the strata lambda_ref (probe, seed 777).
    q5 = committed["edges"].get(policy, {}).get(_LR_STRATA, {}).get("quantile", {}).get("5", [])
    bucket_full, _ = reference_buckets(scores_e, float(_LR_STRATA), 5, 50,
                                       edges=np.asarray(q5, dtype=float))
    stratum_stats = []
    for k in np.unique(bucket_full):
        mask = bucket_full == k
        n_k = int(mask.sum())
        err = int(round(float(np.sum(full_acq_loss[mask]))))
        stratum_stats.append((n_k, err))

    # Pre-compute resplit index sets once (alpha-independent).
    resplit_ix = [resplit_cal_test(np.arange(n_eval), rs, cal_frac) for rs in range(n_resplits)]

    alphas = sorted({round(min(0.999, floor + float(o)), 4) for o in offsets})
    out_rows = []
    for alpha in alphas:
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
        out_rows.append({
            "dataset": dsname, "train_seed": ts, "policy": policy,
            "scheme": primary_scheme, "floor": floor, "committed_alpha": committed_alpha,
            "alpha": alpha, "alpha_minus_floor": round(alpha - floor, 4),
            "plugin_viol": pv_, "plugin_lo": plo, "plugin_hi": phi,
            "marg_viol": mv_, "marg_lo": mlo, "marg_hi": mhi,
            "marg_abstain": marg_abst / n,
            "marg_cost": marg_cost, "marg_cost_ratio_full": marg_cost / full_cost,
            "oracle_cost": float(np.mean(oracle_costs)),
            "iut_abstain": iut_abst / n, "iut_cost": iut_cost,
            "iut_premium_vs_marginal": (iut_cost / marg_cost) if marg_cost else float("nan"),
            "n_infeasible_strata_lr0.9": n_infeasible,
            "delta": delta, "n_resplits": n,
        })
        print(f"[alpha-sweep] {dsname} alpha={alpha:.3f} (floor+{alpha - floor:.3f}): "
              f"plugin_viol={pv_:.2f} marg_viol={mv_:.2f} iut_abstain={iut_abst / n:.2f} "
              f"infeasible@0.9={n_infeasible}", flush=True)
    return out_rows


def plugin_transition(rows):
    """Smallest alpha at which plugin's violation rate is <= delta (the safe onset).

    Rows must be ascending in alpha. Returns (transition_alpha, note); None if
    plugin never becomes safe in the swept range.
    """
    delta = rows[0]["delta"]
    for r in rows:
        if r["plugin_viol"] <= delta:
            return r["alpha"]
    return None


def make_f5(rows_by_ds, fig_dir: Path):
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
        ax1.axhline(delta, linestyle="--", color="k", label=f"delta={delta:g}")
        ax1.axvline(committed_alpha, linestyle=":", color="gray",
                    label=f"committed alpha={committed_alpha:g}")
        ax1.axvline(floor, linestyle="-", color="gray", linewidth=0.8,
                    label=f"floor={floor:.3f}")
        ax1.set_xlabel("alpha"); ax1.set_ylabel("violation rate (Wilson 95%)")
        ax1.set_title("safe/unsafe transition")
        ax1.legend(fontsize=7)

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
    ap = argparse.ArgumentParser(description="CAFA v2 alpha-sweep (post-hoc).")
    ap.add_argument("--dataset", default=None, help="mnist | tabular:<name>")
    ap.add_argument("--all", action="store_true", help="sweep every Phase-1 dataset.")
    ap.add_argument("--train-seed", type=int, default=0)
    ap.add_argument("--policy", default="greedy_entropy")
    ap.add_argument("--grid-from-floor", action="store_true",
                    help="anchor the alpha grid to the committed probe floor (required mode).")
    ap.add_argument("--offsets", default=",".join(str(o) for o in _DEFAULT_OFFSETS),
                    help="comma-separated offsets above the floor.")
    ap.add_argument("--out", default="analysis_v2")
    ap.add_argument("--figures", default="figures_v2")
    args = ap.parse_args(argv)

    if not args.grid_from_floor:
        print("ERROR: only --grid-from-floor mode is supported (the grid must be "
              "anchored to the committed floor).", file=sys.stderr)
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

    all_rows = []
    rows_by_ds = {}
    for ds in datasets:
        rows = sweep_one(ds, args.train_seed, args.policy, offsets, cfg, paths)
        all_rows.extend(rows)
        rows_by_ds[dsname_of(ds)] = rows

    # CSV
    fieldnames = list(all_rows[0].keys())
    with open(out_dir / "alpha_sweep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)

    # Markdown report with the sentence-ready transition statements.
    lines = ["# CAFA v2 -- ALPHA SWEEP (post-hoc on cached rollouts)\n",
             "_Grid anchored to the committed probe floor. The committed fixed-rule "
             "alpha is ceil_0.05(floor + 0.05) and generally sits above the +0.05 "
             "grid point; it is stated per dataset below and marked on F5. Same "
             "frozen trajectories, same pre-committed strata edges; delta = "
             f"{all_rows[0]['delta']:g}; n_resplits = {all_rows[0]['n_resplits']}._\n"]
    for dsname, rows in rows_by_ds.items():
        rows = sorted(rows, key=lambda r: r["alpha"])
        lines.append(f"## {dsname} (ts{rows[0]['train_seed']}, {rows[0]['policy']}, "
                     f"{rows[0]['scheme']}; floor = {_fmt(rows[0]['floor'])}, "
                     f"committed alpha = {rows[0]['committed_alpha']:g})\n")
        lines.append("| alpha | alpha-floor | plugin viol [95% CI] | marginal viol [95% CI] | "
                     "marg abstain | marg cost/full | oracle cost | IUT abstain | "
                     "IUT premium | infeasible strata @0.9 |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            lines.append(
                f"| {r['alpha']:.3f} | +{r['alpha_minus_floor']:.3f} | "
                f"{_fmt(r['plugin_viol'], 2)} [{_fmt(r['plugin_lo'], 2)}, {_fmt(r['plugin_hi'], 2)}] | "
                f"{_fmt(r['marg_viol'], 2)} [{_fmt(r['marg_lo'], 2)}, {_fmt(r['marg_hi'], 2)}] | "
                f"{_fmt(r['marg_abstain'], 2)} | {_fmt(r['marg_cost_ratio_full'], 3)} | "
                f"{_fmt(r['oracle_cost'], 2)} | {_fmt(r['iut_abstain'], 2)} | "
                f"{_fmt(r['iut_premium_vs_marginal'], 2)} | {r['n_infeasible_strata_lr0.9']} |")
        lines.append("")
        trans = plugin_transition(rows)
        ca = rows[0]["committed_alpha"]
        if trans is None:
            lines.append(f"- Plugin transition: plugin remains UNSAFE across the whole swept "
                         f"range on {dsname}; the committed alpha {ca:g} sits in the unsafe "
                         "regime -- the certificate is doing real work at the committed target.")
        else:
            margin = ca - trans
            side = "SAFE" if margin >= 0 else "UNSAFE"
            lines.append(f"- Plugin transition on {dsname}: plugin flips safe at alpha ~ "
                         f"{trans:.3f} (floor + {trans - rows[0]['floor']:.3f}); the committed "
                         f"alpha {ca:g} lands {abs(margin):.3f} {'above' if margin >= 0 else 'below'} "
                         f"the transition (committed target is in the {side} regime). The "
                         "transition point is a property of the risk-curve geometry near "
                         "alpha -- unknowable a priori, which is the argument for a "
                         "certificate over a tuned threshold.")
        lines.append("")
    (out_dir / "ALPHA_SWEEP.md").write_text("\n".join(lines))

    make_f5(rows_by_ds, fig_dir)
    print(f"[alpha-sweep] wrote {out_dir / 'ALPHA_SWEEP.md'}, alpha_sweep.csv, F5_* figures.",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
