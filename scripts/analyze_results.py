#!/usr/bin/env python
"""WO-11 -- analysis: metrics_v2/*.json -> analysis_v2/RESULTS.md + CSVs.

Torch-free, no plotting.  Reads every ``metrics_v2/*.json`` produced by the eval
sweep and emits the reviewer-facing RESULTS.md plus machine-readable CSVs.  All
numbers are computed from the metrics files (and, for the binning ablation, the
pool caches under ``${RESULTS_ROOT}/pool_v2``); nothing is invented.

Usage
-----
    python scripts/analyze_results.py [--metrics-dir metrics_v2] [--out analysis_v2]

Sections: header; H2 validity/efficiency table (Wilson 95% CIs); per-stratum
audit table with three-way verdicts; deployable IUT-vs-marginal comparison; fork
metrics (strata counts, depth concentration, detection outcome); binning
ablation (25-resplit subset); detection-power scatter CSV; GATES block.
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

from cafa import config  # noqa: E402
from cafa.metrics import per_bucket_risk, reference_buckets, reference_depth  # noqa: E402
from cafa.risk_control import mondrian_select  # noqa: E402

_Z = 1.96
_ABLATION_SUBSET = 25   # resplit seeds used for the binning ablation (stated in RESULTS.md)


def wilson(k: int, n: int, z: float = _Z):
    """Wilson score interval; returns (p_hat, lower, upper)."""
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def cp_bounds(k: int, n: int):
    from scipy.stats import beta
    k = int(k); n = int(n)
    if n == 0:
        return 0.0, 1.0
    lcb = 0.0 if k == 0 else float(beta.ppf(0.05, k, n - k + 1))
    ucb = 1.0 if k == n else float(beta.ppf(0.95, k + 1, n - k))
    return lcb, ucb


def verdict_of(lcb, ucb, alpha):
    if lcb > alpha:
        return "infeasible"
    if ucb < alpha:
        return "feasible"
    return "undetermined"


def stop_index_matrix(scores, grid):
    scores = np.asarray(scores, dtype=float)
    grid = np.asarray(grid, dtype=float)
    n, Tp1 = scores.shape
    T = Tp1 - 1
    crossed = scores[:, :, None] >= grid[None, None, :]
    any_cross = crossed.any(axis=1)
    first = crossed.argmax(axis=1)
    return np.where(any_cross, first, T).astype(int)


def _nanmean(xs):
    arr = np.asarray([x for x in xs if x is not None], dtype=float)
    arr = arr[~np.isnan(arr)]
    return float(arr.mean()) if arr.size else float("nan")


def _fmt(x, nd=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "n/a"
    return f"{x:.{nd}f}"


def load_metrics(metrics_dir: Path):
    out = []
    for p in sorted(metrics_dir.glob("*.json")):
        try:
            out.append((p, json.loads(p.read_text())))
        except json.JSONDecodeError:
            print(f"[warn] skipping unparseable {p}", file=sys.stderr)
    return out


# --------------------------------------------------------------------------- #
# H2 validity / efficiency
# --------------------------------------------------------------------------- #
def h2_rows_for(data, scheme, lr_key, alpha):
    """Per-method aggregates over resplits at a primary lambda_ref, one cost scheme."""
    resplits = data["lambda_refs"][lr_key]["resplits"]
    if not resplits:
        return {}
    method_names = list(resplits[0]["schemes"][scheme].keys())
    full_costs = [r["schemes"][scheme]["oracle_full"]["realized_cost"] for r in resplits]
    mean_full = _nanmean(full_costs)

    rows = {}
    for m in method_names:
        risks, costs, abst = [], [], []
        for r in resplits:
            rec = r["schemes"][scheme][m]
            risks.append(rec.get("realized_risk"))
            costs.append(rec.get("realized_cost"))
            abst.append(bool(rec.get("abstained", False)))
        n = len(resplits)
        viol_k = sum(1 for x in risks if x is not None and x > alpha)
        p, lo, hi = wilson(viol_k, n)
        mc = _nanmean(costs)
        rows[m] = {
            "violation_frac": p, "wilson_lo": lo, "wilson_hi": hi,
            "abstain_rate": (sum(abst) / n if n else 0.0),
            "mean_risk": _nanmean(risks), "mean_cost": mc,
            "cost_ratio_full": (mc / mean_full if (mean_full and not math.isnan(mean_full)) else float("nan")),
        }
    return rows


# --------------------------------------------------------------------------- #
# Binning ablation (needs pool caches)
# --------------------------------------------------------------------------- #
def ablation_verdicts(dsname, policy_token, score, ts, committed, cfg, paths, alpha):
    """Recompute per-stratum verdicts + mondrian rates under alt binnings.

    Post-hoc from committed edges + the pool cache; mondrian rates over the first
    _ABLATION_SUBSET resplit seeds.  Returns None if the pool cache is absent.
    """
    from cafa.pool import load_pool_cache
    from cafa.splits import probe_eval_split, resplit_cal_test

    cache_path = Path(paths.results_root) / "pool_v2" / f"{dsname}_ts{ts}_{policy_token}_{score}.npz"
    if not cache_path.exists():
        return None
    cache = load_pool_cache(cache_path)
    method_cfg = cfg["method"]
    g = method_cfg.get("grid", {"g_min": 0.0, "g_max": 1.0, "n": 100})
    grid = np.linspace(float(g["g_min"]), float(g["g_max"]), int(g["n"]))
    delta = float(method_cfg.get("delta", 0.10))
    procedure = method_cfg.get("procedure", "fixed_sequence")
    pv = cfg.get("protocol_v2", {})
    probe_frac = float(pv.get("probe_frac", 0.10)); probe_seed = int(pv.get("probe_seed", 777))
    cal_frac = float(pv.get("cal_frac_of_eval", 0.5))
    lambda_refs = list(cfg.get("mondrian_v2", {}).get("lambda_refs", [0.5, 0.7, 0.9]))

    n_pool = cache["scores"].shape[0]
    _, eval_pos = probe_eval_split(np.arange(n_pool), probe_frac, probe_seed)
    scores = np.asarray(cache["scores"])[eval_pos]
    correct = np.asarray(cache["correct"])[eval_pos]
    n_eval, Tp1 = scores.shape
    T = Tp1 - 1
    s_full = stop_index_matrix(scores, grid)
    rows = np.arange(n_eval)[:, None]
    losses_full = 1.0 - correct[rows, s_full]
    full_acq_loss = 1.0 - correct[:, T]

    edge_kinds = [("quantile", "3"), ("quantile", "8"),
                  ("equal_width_merged", "5x25"), ("equal_width_merged", "5x50"),
                  ("equal_width_merged", "5x100")]
    out = {}
    for lr in lambda_refs:
        lr_key = str(float(lr))
        for kind, key in edge_kinds:
            edges = np.asarray(
                committed["edges"].get(policy_token, {}).get(lr_key, {}).get(kind, {}).get(key, []),
                dtype=float,
            )
            bucket_full, _ = reference_buckets(scores, float(lr), 5, 50, edges=edges)
            per_stratum = {}
            for k in np.unique(bucket_full):
                mask = bucket_full == k
                n_k = int(mask.sum())
                err = int(round(float(np.sum(full_acq_loss[mask]))))
                lcb, ucb = cp_bounds(err, n_k)
                per_stratum[int(k)] = {"n": n_k, "verdict": verdict_of(lcb, ucb, alpha)}
            # mondrian cert/abstain over the subset.
            cert = {int(k): 0 for k in np.unique(bucket_full)}
            abst = {int(k): 0 for k in np.unique(bucket_full)}
            n_sub = min(_ABLATION_SUBSET, int(pv.get("n_resplits", 100)))
            for rs in range(n_sub):
                cal_local, _ = resplit_cal_test(np.arange(n_eval), rs, cal_frac)
                cal_bid = bucket_full[cal_local]
                mond = mondrian_select(losses_full[cal_local], losses_full[cal_local], grid,
                                       alpha, delta, cal_bid, procedure=procedure, joint=False)
                for k, idx in mond.lambda_idx_by_bucket.items():
                    if k in cert:
                        if idx is None:
                            abst[k] += 1
                        else:
                            cert[k] += 1
            out[(lr_key, kind, key)] = {
                "per_stratum": per_stratum,
                "cert_rate": {k: (cert[k] / n_sub if n_sub else 0.0) for k in cert},
                "abstain_rate": {k: (abst[k] / n_sub if n_sub else 0.0) for k in abst},
                "n_subset": n_sub,
            }
    return out


# --------------------------------------------------------------------------- #
# Main report
# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAFA v2 analysis -> RESULTS.md + CSVs.")
    ap.add_argument("--metrics-dir", default="metrics_v2")
    ap.add_argument("--out", default="analysis_v2")
    args = ap.parse_args(argv)

    cfg = config.load_experiment()
    try:
        paths = config.load_paths()
    except RuntimeError:
        paths = None

    metrics_dir = Path(args.metrics_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = load_metrics(metrics_dir)
    if not metrics:
        print(f"ERROR: no metrics JSONs under {metrics_dir}.", file=sys.stderr)
        return 2

    lines = []
    lines.append("# CAFA v2 -- RESULTS\n")
    lines.append("_Generated by scripts/analyze_results.py from metrics_v2/*.json. "
                 "All values computed from data; no invented numbers._\n")

    # ---- (1) header ----
    lines.append("## 1. Header\n")
    lines.append("| dataset | policy | train_seed | alpha | delta | n_resplits | backbone sha256 |")
    lines.append("|---|---|---|---|---|---|---|")
    by_ds_policy = {}
    for p, data in metrics:
        meta = data["meta"]
        sha = str(meta.get("cache_meta", {}).get("checkpoint_sha256", ""))[:12]
        lines.append(f"| {meta['dataset']} | {meta['policy']} | {meta['train_seed']} | "
                     f"{_fmt(data['alpha'])} | {_fmt(data['delta'])} | {meta['n_resplits']} | {sha} |")
        by_ds_policy[(meta["dsname"], meta["policy"], int(meta["train_seed"]))] = (p, data)
    lines.append("")

    # ---- (2) H2 table ----
    lines.append("## 2. H2 validity + efficiency (per dataset, policy, cost scheme)\n")
    lines.append("_Primary lambda_ref for this table = the largest configured value. "
                 "violation_frac carries a Wilson 95% CI._\n")
    lines.append("> Footnote: Resplits share a finite eval pool; intervals are heuristic "
                 "under dependence.\n")
    h2_csv = [("dataset", "policy", "scheme", "method", "violation_frac", "wilson_lo",
               "wilson_hi", "abstain_rate", "mean_risk", "mean_cost", "cost_ratio_full")]
    for (dsname, policy, ts), (p, data) in sorted(by_ds_policy.items()):
        alpha = float(data["alpha"])
        lr_keys = list(data["lambda_refs"].keys())
        primary_lr = lr_keys[-1] if lr_keys else None
        if primary_lr is None:
            continue
        for scheme in data["meta"]["schemes"]:
            rows = h2_rows_for(data, scheme, primary_lr, alpha)
            lines.append(f"### {dsname} / {policy} / {scheme}  (alpha={_fmt(alpha)}, "
                         f"lambda_ref={primary_lr})\n")
            lines.append("| method | violation_frac [95% CI] | abstain | mean_risk | mean_cost | cost/full |")
            lines.append("|---|---|---|---|---|---|")
            for m, r in rows.items():
                ci = f"{_fmt(r['violation_frac'],3)} [{_fmt(r['wilson_lo'],3)}, {_fmt(r['wilson_hi'],3)}]"
                lines.append(f"| {m} | {ci} | {_fmt(r['abstain_rate'],3)} | {_fmt(r['mean_risk'])} | "
                             f"{_fmt(r['mean_cost'])} | {_fmt(r['cost_ratio_full'],3)} |")
                h2_csv.append((dsname, policy, scheme, m, r["violation_frac"], r["wilson_lo"],
                               r["wilson_hi"], r["abstain_rate"], r["mean_risk"], r["mean_cost"],
                               r["cost_ratio_full"]))
            lines.append("")

    # ---- (3) audit table + (7) detection scatter ----
    lines.append("## 3. Per-stratum audit (per dataset, policy, lambda_ref)\n")
    audit_csv = [("dataset", "policy", "lambda_ref", "stratum", "eval_n",
                  "marg_risk_mean", "marg_risk_sd", "mond_cert_rate", "mond_abstain_rate",
                  "jointmond_cert_rate", "jointmond_abstain_rate", "R_full", "R_full_lcb95",
                  "R_full_ucb95", "verdict")]
    detect_csv = [("dataset", "policy", "lambda_ref", "stratum", "n_cal_q", "q",
                   "delta_hat", "detected", "n_req_heuristic")]
    for (dsname, policy, ts), (p, data) in sorted(by_ds_policy.items()):
        alpha = float(data["alpha"])
        delta = float(data["delta"])
        pv = cfg.get("protocol_v2", {})
        cal_frac = float(pv.get("cal_frac_of_eval", 0.5))
        for lr_key, blk in data["lambda_refs"].items():
            pop = blk["population"]
            resplits = blk["resplits"]
            strata = sorted(int(k) for k in pop["per_stratum_full"].keys())
            n_eval = int(pop["eval_n"])
            lines.append(f"### {dsname} / {policy} / lambda_ref={lr_key}\n")
            lines.append("| stratum | eval_n | marg risk (mean+/-sd) | mond cert/abstain | "
                         "joint cert/abstain | R_full [LCB, UCB] | verdict |")
            lines.append("|---|---|---|---|---|---|---|")
            for k in strata:
                ks = str(k)
                marg_vals = [r["marginal_per_stratum_risk"].get(ks) for r in resplits]
                marg_arr = np.asarray([v for v in marg_vals if v is not None], dtype=float)
                marg_arr = marg_arr[~np.isnan(marg_arr)]
                mmean = float(marg_arr.mean()) if marg_arr.size else float("nan")
                msd = float(marg_arr.std()) if marg_arr.size else float("nan")
                # mondrian cert/abstain rates over resplits for this stratum.
                cnt = {"cf": 0, "ca": 0, "jf": 0, "ja": 0, "nf": 0, "nj": 0}
                for r in resplits:
                    jfd = r["mondrian_audit"]["joint_false"]["lambda_idx_by_bucket"]
                    jtd = r["mondrian_audit"]["joint_true"]["lambda_idx_by_bucket"]
                    if ks in jfd:
                        cnt["nf"] += 1
                        cnt["ca" if jfd[ks] is None else "cf"] += 1
                    if ks in jtd:
                        cnt["nj"] += 1
                        cnt["ja" if jtd[ks] is None else "jf"] += 1
                cert_r = (cnt["cf"] / cnt["nf"]) if cnt["nf"] else 0.0
                abst_r = (cnt["ca"] / cnt["nf"]) if cnt["nf"] else 0.0
                jcert_r = (cnt["jf"] / cnt["nj"]) if cnt["nj"] else 0.0
                jabst_r = (cnt["ja"] / cnt["nj"]) if cnt["nj"] else 0.0
                info = pop["per_stratum_full"][ks]
                verdict = info["verdict"]
                vtxt = f"**{verdict}**" if verdict == "infeasible" else verdict
                lines.append(
                    f"| {k} | {info['n']} | {_fmt(mmean)}+/-{_fmt(msd)} | "
                    f"{_fmt(cert_r,2)}/{_fmt(abst_r,2)} | {_fmt(jcert_r,2)}/{_fmt(jabst_r,2)} | "
                    f"{_fmt(info['risk'])} [{_fmt(info['cp_lcb95'])}, {_fmt(info['cp_ucb95'])}] | {vtxt} |"
                )
                audit_csv.append((dsname, policy, lr_key, k, info["n"], mmean, msd, cert_r, abst_r,
                                  jcert_r, jabst_r, info["risk"], info["cp_lcb95"], info["cp_ucb95"],
                                  verdict))
                # detection scatter row
                q = info["n"] / n_eval if n_eval else 0.0
                n_cal_q = info["n"] * cal_frac
                lcb = info["cp_lcb95"] if info["cp_lcb95"] is not None else 0.0
                delta_hat = float(lcb) - alpha
                detected = 1 if verdict == "infeasible" else 0
                n_req = (math.log(1.0 / delta) / (2.0 * delta_hat * delta_hat)) if delta_hat > 0 else float("nan")
                detect_csv.append((dsname, policy, lr_key, k, n_cal_q, q, delta_hat, detected, n_req))
            lines.append("")

    # ---- (4) deployable IUT vs marginal ----
    lines.append("## 4. Deployable comparison: IUT vs marginal\n")
    for (dsname, policy, ts), (p, data) in sorted(by_ds_policy.items()):
        alpha = float(data["alpha"])
        for lr_key, blk in data["lambda_refs"].items():
            resplits = blk["resplits"]
            if not resplits:
                continue
            for scheme in data["meta"]["schemes"]:
                marg_c = _nanmean([r["schemes"][scheme]["cafa_marginal"]["realized_cost"] for r in resplits])
                iut_c = _nanmean([r["schemes"][scheme]["cafa_iut"]["realized_cost"] for r in resplits])
                iut_abst = float(np.mean([bool(r["iut_abstained"]) for r in resplits]))
                premium = (iut_c / marg_c) if (marg_c and not math.isnan(marg_c)) else float("nan")
                lines.append(f"- {dsname}/{policy}/{scheme} lr={lr_key}: uniform per-stratum "
                             f"validity costs {_fmt(premium,3)}x the marginal certificate on "
                             f"{dsname} (IUT abstention rate {_fmt(iut_abst,3)}).")
    lines.append("")

    # ---- (5) fork metrics ----
    lines.append("## 5. Fork metrics (D9)\n")
    lines.append("### 5a. Populated-strata count (lambda_ref x policy; marginal counted once)\n")
    lines.append("| dataset | policy | lambda_ref | populated_strata |")
    lines.append("|---|---|---|---|")
    fork_csv = [("dataset", "policy", "lambda_ref", "populated_strata", "depth_iqr", "norm_entropy")]
    for (dsname, policy, ts), (p, data) in sorted(by_ds_policy.items()):
        for lr_key, blk in data["lambda_refs"].items():
            pop = blk["population"]
            n_strata = sum(1 for v in pop["bucket_sizes"].values() if int(v) > 0)
            dc = pop["depth_concentration"]
            lines.append(f"| {dsname} | {policy} | {lr_key} | {n_strata} |")
            fork_csv.append((dsname, policy, lr_key, n_strata, dc["iqr"], dc["norm_entropy"]))
    lines.append("")
    lines.append("### 5b. Depth concentration (IQR, normalized entropy) per policy\n")
    lines.append("| dataset | policy | lambda_ref | depth_IQR | norm_entropy |")
    lines.append("|---|---|---|---|---|")
    for row in fork_csv[1:]:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {_fmt(row[4])} | {_fmt(row[5])} |")
    lines.append("")
    lines.append("### 5c. Detection outcome per (dataset, policy)\n")
    for (dsname, policy, ts), (p, data) in sorted(by_ds_policy.items()):
        alpha = float(data["alpha"])
        flagged = []
        for lr_key, blk in data["lambda_refs"].items():
            for ks, info in blk["population"]["per_stratum_full"].items():
                if info["verdict"] == "infeasible":
                    flagged.append((lr_key, ks))
        min_lr = min((float(lr) for lr, _ in flagged), default=None)
        lines.append(f"- {dsname}/{policy}: flagged-infeasible strata = {flagged or 'none'}; "
                     f"detection requires lambda_ref >= {min_lr if min_lr is not None else 'n/a'}.")
    lines.append("")

    # ---- (6) binning ablation ----
    lines.append("## 6. Binning ablation (verdicts under alt edges)\n")
    lines.append(f"_Mondrian cert/abstain rates computed on the first {_ABLATION_SUBSET} resplit "
                 "seeds to bound runtime; verdicts on the full eval pool._\n")
    if paths is None:
        lines.append("_Pool caches unavailable (RESULTS_ROOT not resolved); ablation skipped._\n")
    else:
        any_ablation = False
        for (dsname, policy, ts), (p, data) in sorted(by_ds_policy.items()):
            committed_path = Path("configs") / f"committed_v2_{dsname}_ts{ts}.json"
            if not committed_path.exists():
                continue
            committed = json.loads(committed_path.read_text())
            score = data["meta"].get("score", "softmax")
            abl = ablation_verdicts(dsname, policy, score, ts, committed, cfg, paths, float(data["alpha"]))
            if abl is None:
                continue
            any_ablation = True
            lines.append(f"### {dsname} / {policy}\n")
            lines.append("| lambda_ref | edge scheme | stratum verdicts |")
            lines.append("|---|---|---|")
            for (lr_key, kind, key), v in abl.items():
                verd = ", ".join(f"{k}:{d['verdict']}" for k, d in sorted(v["per_stratum"].items()))
                lines.append(f"| {lr_key} | {kind}:{key} | {verd} |")
            lines.append("")
        if not any_ablation:
            lines.append("_No pool caches found under pool_v2/; ablation skipped._\n")

    # ---- (8) GATES ----
    lines.append("## GATES\n")
    lines.append("| dataset | marginal violation_frac [Wilson UB] | gate | IUT any-stratum viol [Wilson UB] | gate |")
    lines.append("|---|---|---|---|---|")
    for (dsname, policy, ts), (p, data) in sorted(by_ds_policy.items()):
        alpha = float(data["alpha"]); delta = float(data["delta"])
        # marginal: pool all resplits across lambda_ref (scheme 0; risk scheme-invariant).
        scheme0 = data["meta"]["schemes"][0]
        marg_k = marg_n = 0
        iut_k = iut_n = 0
        for lr_key, blk in data["lambda_refs"].items():
            for r in blk["resplits"]:
                mr = r["schemes"][scheme0]["cafa_marginal"]["realized_risk"]
                marg_n += 1
                if mr is not None and mr > alpha:
                    marg_k += 1
                # IUT any-stratum violation this resplit. Global abstention makes
                # no claim (deploys full acquisition), so it never counts as a
                # violation of the certified-lambda guarantee.
                iut_n += 1
                if not r.get("iut_abstained", False):
                    ips = [v for v in r["iut_per_stratum_risk"].values() if v is not None]
                    if ips and max(ips) > alpha:
                        iut_k += 1
        _, _, m_ub = wilson(marg_k, marg_n)
        _, _, i_ub = wilson(iut_k, iut_n)
        m_gate = "PASS" if m_ub <= delta else "FAIL"
        i_gate = "PASS" if i_ub <= delta else "FAIL"
        lines.append(f"| {dsname}/{policy} | {_fmt(marg_k / marg_n if marg_n else 0,3)} "
                     f"[{_fmt(m_ub,3)}] | {m_gate} | {_fmt(iut_k / iut_n if iut_n else 0,3)} "
                     f"[{_fmt(i_ub,3)}] | {i_gate} |")
    lines.append("")
    lines.append("_Freeze sha check delegated: run `bash repro/verify_freeze.sh`._\n")

    (out_dir / "RESULTS.md").write_text("\n".join(lines))

    def _write_csv(name, rows):
        with open(out_dir / name, "w", newline="") as f:
            csv.writer(f).writerows(rows)

    _write_csv("h2_table.csv", h2_csv)
    _write_csv("audit_table.csv", audit_csv)
    _write_csv("fork_strata.csv", fork_csv)
    _write_csv("detection_scatter.csv", detect_csv)

    print(f"[analyze] wrote {out_dir / 'RESULTS.md'} + 4 CSVs.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
