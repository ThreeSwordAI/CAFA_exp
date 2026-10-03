#!/usr/bin/env python
"""v3 -- certifiability-margin analysis (E10) and the calibration-size table (E11), torch-free.

Question: is the tier-1 outcome of the certify-or-route cascade predicted by the deepest stratum's
margin at full information?  Tier 1 (CAFA-IUT, :func:`cafa.cascade.tier_threshold`) walks the threshold
grid from the top (lambda = 1, ~ full information) at level ``delta_1 = delta * delta_weights[0]`` and
certifies nothing unless the top of the grid passes in every stratum; the deepest stratum is the one
most likely to block it.  This script predicts the tier-1 share from that stratum's full-information
risk and calibration count alone, and compares the prediction with the observed share.

Points: one per (dataset, policy, train seed, lambda_ref key, split s) over every metrics JSON in
``--metrics-dir`` (``scripts/run_cascade_sweep.py`` layout; every seed present is used).  Per point:

  * ``k_star``        deepest populated stratum of ``audit_by_split[s]`` (max int key; the audit runs on
                      the split's WHOLE calibration pool);  ``r_full``, ``rmin_thr``, ``rmin_depth`` and
                      ``n_k_calpool`` (= the record's ``n_k``) from ``audit_by_split[s][k_star]``;
  * ``n_k``           expected calibration-draw count of ``k_star``:
                      ``commit["edges"][policy][key]["expected_cal_counts"][k_star]`` (default commit
                      ``configs/committed_v3_{dsname}_ts{ts}.json``), times ``cal_frac / cal_frac_of_pool``
                      for cal_frac runs, rounded to the nearest integer;
  * ``alpha`` = ``d["alpha"]``;  ``delta_1`` = ``d["delta"] * d["delta_weights"][0]`` (0.05);
  * ``margin`` = alpha - r_full;  ``z`` = margin * sqrt(n_k / (alpha (1 - alpha)));
  * ``k_max``         largest error count k in 0..n_k with
                      ``hoeffding_bentkus_pvalue(k / n_k, n_k, alpha) <= delta_1`` (-1 if none; the frozen
                      p-value is nondecreasing in k, so a binary search is used);
  * ``pred_tier1``    = P(Bin(n_k, r_full) <= k_max) (0 when k_max < 0): the probability that a
                      Hoeffding-Bentkus certificate at level delta_1 is issued for a rule whose true stratum
                      risk is r_full;  ``pred_tier1_thr`` = the same with ``rmin_thr`` (the best threshold
                      rule in that stratum; optimistic).  The binomial treats the calibration draw as fresh
                      rows from a population of risk r_full, i.e. it is the UNCONDITIONAL prediction (over
                      resampling of the calibration pool);
  * ``pred_tier1_hyper`` (sensitivity)  the same certificate probability CONDITIONAL on the split's
                      calibration pool, whose draws are taken without replacement
                      (:func:`cafa.splits_v3.calibration_draw`):
                      sum over n_d of Hypergeom(N_pool, N_k, n_cal).pmf(n_d) * Hypergeom(N_k, E_k, n_d).cdf(k_max(n_d))
                      with N_pool = ``meta["n_calpool"]`` (else the commit's ``split["n_calpool"]``), N_k =
                      ``n_k_calpool``, E_k = round(r_full N_k) and
                      n_cal = round(cal_frac N_pool) (:func:`pred_certify_hyper`); at cal_frac 1.0 it is the
                      deterministic indicator 1[E_k <= k_max(N_k)];
  * ``obs_tier1`` / ``tier3_share``  share of the split's draws (``schemes[--scheme]["draws"]`` with
                      ``split_seed == s``) deployed at tier 1 / tier 3;  ``n_draws_split``.

The metrics file is cross-checked against the commit (alpha, and per (policy, key) the committed stratum edges
-- shape first, then values -- and G = the commit's ``G`` = ``len(expected_cal_counts)``), so a commit of another
alpha rule (``--commit-prefix committed_v3_am02_``) or another stratification cannot be mixed in silently.  A key
whose block lacks ``--scheme`` (image cells are uniform-only) is skipped with a message and recorded as ``n/a``.

Calibration-size curve (Task K2): ``--calfrac-dir CF PATH`` (repeatable) adds metrics directories swept with
``run_cascade_sweep.py --cal-frac CF`` (same layout, ``meta["cal_frac"]``; it must equal CF when present).
Their points get ``n_k`` scaled by ``CF / cal_frac_of_pool`` and enter F7 (open markers) and the summary
statistics separately from the main points.

Outputs (``--output-dir``, default results_v3/tables; ``--figure``, default results_v3/figures/F7_margin.pdf)
  * TABLE_E10_margin.md / .csv     one row per main point: dataset, policy, seed, key, split, k_star, n_k,
                                   n_k_calpool, r_full, rmin_thr, rmin_depth, alpha, margin, z, k_max,
                                   pred_tier1, pred_tier1_thr, obs_tier1, tier3_share, n_draws_split
                                   (the CSV also carries the sensitivity columns ``pred_tier1_nk_calpool``:
                                   pred_tier1 with n_k = round(cal_frac * n_k_calpool), the split's own expected
                                   draw count -- a check of the commit's probe-based n_k -- and
                                   ``pred_tier1_hyper``, the prediction conditional on the split's pool);
  * TABLE_E10_margin_calfrac.csv   the cal_frac points (same columns + ``cal_frac``; only with --calfrac-dir);
  * TABLE_E10_margin_summary.json / .md   n_points; per predictor (pred_tier1, pred_tier1_thr, and the
                                   sensitivities pred_tier1_nk_calpool / pred_tier1_hyper in the JSON / the main
                                   rows of the md): Spearman rho
                                   and p-value of obs_tier1 vs the prediction (scipy.stats.spearmanr; None when
                                   either side is constant), the fraction / number of points with
                                   |obs - pred| <= --tol (0.2) and the mean absolute error; for all main
                                   points (``main``), key dep only (``main_dep``), per dataset
                                   (``by_dataset``), per cal_frac (``calfrac``) and main + cal_frac together
                                   (``all_with_calfrac``);
  * TABLE_E11_calfrac.md / .csv    one row per cell (dataset, policy, seed) at ``--e11-key`` (dep): for cal_frac
                                   0.25 / 0.5 (main) / 1.0 (``--e11-calfracs`` plus any --calfrac-dir):
                                   n_draws, n_k (mean over splits of the point n_k), pred_tier1 and
                                   pred_tier1_hyper (means over the splits), tier1 (pooled ``tier_share["1"]``),
                                   cost_over_T (``cascade_mean_test_cost / meta T``), certified_violation
                                   (``cascade_certified_violation_rate``); columns ``{metric}_cf{CF}``; a missing
                                   cal_frac file gives ``TBD-RUN`` in that cell's CF columns, a file whose key
                                   lacks ``--scheme`` gives ``n/a (no scheme)``;
  * F7_margin.pdf (+ .png with --png)  (a) obs_tier1 vs z (symlog x), colour = dataset, marker = lambda_ref
                                   key, with pred_tier1(z) at the median n_k / alpha (faint: 10 % / 90 % n_k
                                   quantiles); (b) obs_tier1 vs pred_tier1 with the diagonal and a +-tol band.
                                   Cal_frac points are open markers (small: CF < main, large: CF > main).

Usage
-----
    python scripts/margin_analysis_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3
    python scripts/margin_analysis_v3.py --metrics-dir $RESULTS_ROOT/metrics_v3 \\
        --calfrac-dir 0.25 $RESULTS_ROOT/metrics_v3_calfrac025 --calfrac-dir 1.0 $RESULTS_ROOT/metrics_v3_calfrac100
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullLocator  # noqa: E402
from scipy.stats import binom, hypergeom, spearmanr  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cafa.risk_control import hoeffding_bentkus_pvalue  # noqa: E402

KEYS = ("0.5", "0.7", "0.9", "dep")
MARKERS = {"0.5": "o", "0.7": "s", "0.9": "^", "dep": "D"}
# categorical slots in fixed order (dataviz reference palette, validated: CVD / normal-vision floors pass);
# colour follows the dataset, never its rank in the current file set
PALETTE = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948")
DATASET_ORDER = ("mnist", "fashionmnist", "image-imagenette", "tabular-adult", "tabular-MiniBooNE",
                 "csv-diabetes", "csv-physionet", "cube")
E10_COLS = ("dataset", "policy", "seed", "key", "split", "k_star", "n_k", "n_k_calpool", "r_full", "rmin_thr",
            "rmin_depth", "alpha", "margin", "z", "k_max", "pred_tier1", "pred_tier1_thr", "obs_tier1",
            "tier3_share", "n_draws_split")
E10_DEC = {"r_full": 4, "rmin_thr": 4, "rmin_depth": 4, "alpha": 4, "margin": 4, "z": 2, "pred_tier1": 3,
           "pred_tier1_thr": 3, "obs_tier1": 3, "tier3_share": 3, "pred_tier1_nk_calpool": 3, "pred_tier1_hyper": 3}
E11_METRICS = ("n_draws", "n_k", "pred_tier1", "pred_tier1_hyper", "tier1", "cost_over_T", "certified_violation")
PREDICTORS = ("pred_tier1", "pred_tier1_thr")
# sensitivity predictors (CSV + summary statistics): n_k = round(cal_frac * n_k_calpool) instead of the commit's
# count; the certificate probability conditional on the split's calibration pool (draws without replacement)
SENSITIVITY = ("pred_tier1_nk_calpool", "pred_tier1_hyper")
HYPER_TAIL = 1e-12          # pred_certify_hyper sums over the n_d with Hypergeom pmf > HYPER_TAIL
TBD = "TBD-RUN"             # no metrics file / directory for that cell at that cal_frac (not run)
NA = "n/a"                  # by_key value of a key whose block lacks the requested cost scheme
NA_E11 = "n/a (no scheme)"  # its TABLE_E11 entry


def f(v, d=3):
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        return f"{float(v):.{d}f}" if math.isfinite(v) else str(float(v))
    return str(v)


def cf_label(cf: float) -> str:
    """``0.25 -> "0.25"``, ``0.5 -> "0.5"``, ``1 -> "1.0"`` (column suffix ``_cf{label}``)."""
    return str(float(cf))


# --------------------------------------------------------------------------- #
# The prediction
# --------------------------------------------------------------------------- #
_KMAX: dict = {}          # (n, alpha, level) -> k_max: memo of k_max_certifiable (shared by every prediction)


def k_max_certifiable(n: int, alpha: float, level: float, hint=None) -> int:
    """Largest error count ``k`` in ``0..n`` with ``hoeffding_bentkus_pvalue(k / n, n, alpha) <= level``; -1 if none.

    The frozen p-value is nondecreasing in ``k`` (both the Hoeffding and the Bentkus term are; min and clip
    keep it), so the certifiable counts are a prefix ``0..k_max`` and a binary search finds its end
    (tests/test_margin_analysis_v3.py checks monotonicity and the boundary by brute force).  Memoised per
    ``(n, alpha, level)``.  ``hint`` (optional, e.g. k_max at n - 1) only narrows the search bracket -- an
    upward gallop from ``hint`` when it is certifiable, else a search below it -- so the result is the same
    with or without it."""
    n, alpha, level = int(n), float(alpha), float(level)
    key = (n, alpha, level)
    km = _KMAX.get(key)
    if km is None:
        km = _KMAX[key] = _k_max_search(n, alpha, level, hint)
    return km


def _k_max_search(n: int, alpha: float, level: float, hint=None) -> int:
    def ok(k):
        return hoeffding_bentkus_pvalue(k / n, n, alpha) <= level

    if n <= 0 or not ok(0):
        return -1
    lo, hi = 0, n          # invariant: p(lo) <= level; every k > hi has p(k) > level
    if hint is not None and 0 < int(hint) <= n:
        h = int(hint)
        if ok(h):
            lo, step = h, 1
            while lo + step <= n and ok(lo + step):
                lo, step = lo + step, 2 * step
            hi = min(n, lo + step - 1)
        else:
            hi = h - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


def pred_certify(n: int, risk: float, alpha: float, level: float) -> float:
    """P(Bin(n, risk) <= k_max(n, alpha, level)): probability that the HB certificate is issued at level ``level``
    for a rule whose true stratum risk is ``risk`` on ``n`` calibration rows (0 when nothing is certifiable)."""
    km = k_max_certifiable(int(n), float(alpha), float(level))
    if km < 0:
        return 0.0
    return float(binom.cdf(km, int(n), min(1.0, max(0.0, float(risk)))))


def pred_certify_hyper(n_pool: int, n_k_pool: int, e_k: int, n_cal: int, alpha: float, level: float) -> float:
    """Probability that the HB certificate at level ``level`` is issued for stratum k, CONDITIONAL on the pool.

    The calibration draw takes ``n_cal`` of the ``n_pool`` pool rows without replacement; ``n_k_pool`` of them
    lie in stratum k and ``e_k`` of those are errors.  So the draw's stratum count is
    n_d ~ Hypergeom(n_pool, n_k_pool, n_cal), its error count given n_d is Hypergeom(n_k_pool, e_k, n_d), and

        P = sum_{n_d} Hypergeom(n_pool, n_k_pool, n_cal).pmf(n_d) * Hypergeom(n_k_pool, e_k, n_d).cdf(k_max(n_d))

    over the support of n_d with pmf > ``HYPER_TAIL`` (k_max(n_d) from :func:`k_max_certifiable`, memoised per
    (n, alpha, level); k_max = -1 contributes 0).  At ``n_cal = n_pool`` (cal_frac 1.0) n_d = n_k_pool and the
    error count = e_k surely, so P is the indicator 1[e_k <= k_max(n_k_pool)]."""
    n_pool, n_k_pool, n_cal = int(n_pool), int(n_k_pool), int(n_cal)
    e_k = min(max(int(e_k), 0), n_k_pool)
    if n_k_pool <= 0 or n_cal <= 0:
        return 0.0
    s_lo, s_hi = max(0, n_cal - (n_pool - n_k_pool)), min(n_k_pool, n_cal)      # support of n_d
    # the pmf is unimodal (mode ~ mean): evaluate it on a window around the mean, widened until both ends are
    # <= HYPER_TAIL or at the support bounds -- then every n_d with pmf > HYPER_TAIL lies inside (the full-support
    # pmf is slow for pools of ~10^4 rows)
    mu = n_cal * n_k_pool / n_pool
    sd = math.sqrt(max(mu * (1.0 - n_k_pool / n_pool) * (n_pool - n_cal) / max(n_pool - 1, 1), 0.0))
    half = int(math.ceil(8.0 * sd)) + 8
    while True:
        a, b = max(s_lo, int(math.floor(mu)) - half), min(s_hi, int(math.ceil(mu)) + half)
        nd = np.arange(a, b + 1)
        w = hypergeom.pmf(nd, n_pool, n_k_pool, n_cal)
        if (a == s_lo or w[0] <= HYPER_TAIL) and (b == s_hi or w[-1] <= HYPER_TAIL):
            break
        half *= 2
    keep = w > HYPER_TAIL
    nd, w = nd[keep], w[keep]
    km, prev = np.empty(nd.size, dtype=int), None
    for i, n in enumerate(nd):          # ascending n_d: the previous k_max is a search hint
        km[i] = prev = k_max_certifiable(int(n), alpha, level, hint=prev)
    ok = km >= 0
    if not ok.any():
        return 0.0
    c = hypergeom.cdf(km[ok], n_k_pool, e_k, nd[ok])
    return float(min(1.0, np.sum(w[ok] * c)))


# --------------------------------------------------------------------------- #
# Reading metrics + commits
# --------------------------------------------------------------------------- #
def commit_path(commits_dir: Path, prefix: str, dsname: str, ts: int) -> Path:
    return Path(commits_dir) / f"{prefix}{dsname}_ts{int(ts)}.json"


def read_cell(jp: Path, d: dict, commit: dict, cpath: Path, *, scheme: str, keys, cal_frac=None) -> dict:
    """Points and per-key summaries of one metrics JSON ``d`` (already loaded from ``jp``).

    ``cal_frac`` is the expected calibration fraction of a ``--calfrac-dir`` file (None for the main dir, whose
    fraction is ``meta["cal_frac"]`` or else the commit's ``cal_frac_of_pool``).  Raises ValueError when alpha,
    the stratum edges (shape, then values) or G of a key disagree with the commit.  ``by_key[key]`` is ``NA``
    ("n/a") for a key whose block lacks ``scheme``; a key without a block in the file is left out."""
    m = d["meta"]
    pol, ts = m["policy"], int(m["train_seed"])
    base = float(commit["split"]["cal_frac_of_pool"])
    mcf = m.get("cal_frac")
    if cal_frac is not None:
        if mcf is not None and abs(float(mcf) - float(cal_frac)) > 1e-9:
            raise ValueError(f"{jp}: meta cal_frac = {mcf} but the file was given as --calfrac-dir {cal_frac}.")
        cf = float(cal_frac)
    else:
        cf = float(mcf) if mcf is not None else base
    scale = cf / base
    alpha = float(d["alpha"])
    if abs(alpha - float(commit["alpha"])) > 1e-12:
        raise ValueError(f"{jp}: alpha {alpha} differs from {cpath} (alpha {commit['alpha']}); wrong --commit-prefix?")
    level = float(d["delta"]) * float(d["delta_weights"][0])
    T = int(m["T"])
    n_pool = int(m["n_calpool"] if m.get("n_calpool") is not None else commit["split"]["n_calpool"])
    n_cal = int(round(cf * n_pool))          # = splits_v3.calibration_draw's draw size
    cell = {"dataset": m["dsname"], "policy": pol, "seed": ts, "cal_frac": cf, "path": str(jp), "T": T,
            "points": [], "by_key": {}}
    for key in keys:
        blk = d["lambda_refs"].get(key)
        if blk is None:
            continue
        ce = commit["edges"][pol][key]
        # shape before values (np.allclose broadcasts: [] vs [x] or [x, x] vs [x] would pass), then G
        e_m, e_c = np.asarray(blk["edges"], float), np.asarray(ce["edges"], float)
        g_m, g_c, n_exp = blk.get("G"), ce.get("G"), len(ce["expected_cal_counts"])
        if (e_m.shape != e_c.shape or not np.allclose(e_m, e_c)
                or (g_m is not None and int(g_m) != n_exp) or (g_c is not None and int(g_c) != n_exp)):
            raise ValueError(f"{jp}: lambda_ref {key} stratum edges / G differ from {cpath} (metrics edges "
                             f"{e_m.tolist()}, G {g_m}; commit edges {e_c.tolist()}, G {g_c}, {n_exp} "
                             "expected_cal_counts); the metrics were not swept with this commit (wrong "
                             "--commits-dir / --commit-prefix?).")
        sch = blk["schemes"].get(scheme)
        if sch is None:  # no silent fallback to another cost scheme (image cells are uniform-only)
            print(f"[margin] skip {jp.name} lambda_ref {key}: no cost scheme {scheme!r} (has {sorted(blk['schemes'])})")
            cell["by_key"][key] = NA
            continue
        aud_by = blk.get("audit_by_split") or {str(m["primary_test_seed"]): blk["audit"]}  # round-1 files
        splits = [str(s) for s in m.get("test_seeds", sorted(aud_by, key=int)) if str(s) in aud_by]
        tiers_by = {}
        for r in sch["draws"]:
            tiers_by.setdefault(str(r["split_seed"]), []).append(int(r["cascade"]["tier"]))
        pts = []
        for s in splits:
            aud = aud_by[s]
            ks = max(int(k) for k in aud)
            rec = aud[str(ks)]
            exp = ce["expected_cal_counts"]
            if ks >= len(exp):
                raise ValueError(f"{jp}: deepest stratum {ks} of split {s} is not committed in {cpath} (G = {len(exp)}).")
            n_k = int(round(float(exp[ks]) * scale))
            n_cp = int(rec["n_k"])
            r_full, r_thr = float(rec["r_full"]), float(rec["rmin_thr"])
            margin = alpha - r_full
            tiers = np.asarray(tiers_by.get(s, []))
            pts.append({
                "dataset": m["dsname"], "policy": pol, "seed": ts, "key": key, "split": int(s), "k_star": ks,
                "n_k": n_k, "n_k_calpool": n_cp, "r_full": r_full, "rmin_thr": r_thr,
                "rmin_depth": float(rec["rmin_depth"]), "alpha": alpha, "margin": margin,
                "z": margin * math.sqrt(n_k / (alpha * (1.0 - alpha))),
                "k_max": k_max_certifiable(n_k, alpha, level),
                "pred_tier1": pred_certify(n_k, r_full, alpha, level),
                "pred_tier1_thr": pred_certify(n_k, r_thr, alpha, level),
                "obs_tier1": float(np.mean(tiers == 1)) if tiers.size else None,
                "tier3_share": float(np.mean(tiers == 3)) if tiers.size else None,
                "n_draws_split": int(tiers.size),
                "pred_tier1_nk_calpool": pred_certify(int(round(cf * n_cp)), r_full, alpha, level),
                "pred_tier1_hyper": pred_certify_hyper(n_pool, n_cp, int(round(r_full * n_cp)), n_cal, alpha, level),
                "cal_frac": cf, "delta_1": level})
        summ = sch["summary"]
        cell["points"] += pts
        cell["by_key"][key] = {
            "n_draws": int(summ["n_draws"]),
            "n_k": float(np.mean([p["n_k"] for p in pts])) if pts else None,
            "pred_tier1": float(np.mean([p["pred_tier1"] for p in pts])) if pts else None,
            "pred_tier1_hyper": float(np.mean([p["pred_tier1_hyper"] for p in pts])) if pts else None,
            "tier1": float(summ["tier_share"]["1"]),
            "cost_over_T": float(summ["cascade_mean_test_cost"]) / T,
            "certified_violation": summ.get("cascade_certified_violation_rate")}
    return cell


def scan(metrics_dir: Path, *, commits_dir: Path, prefix: str, scheme: str, keys, cal_frac=None) -> list:
    """Every metrics JSON of ``metrics_dir`` -> list of :func:`read_cell` dicts (files are read one at a time)."""
    cells, commits = [], {}
    for jp in sorted(Path(metrics_dir).glob("*.json")):
        d = json.loads(jp.read_text())
        if "meta" not in d or "lambda_refs" not in d:
            print(f"[margin] skip {jp.name}: not a run_cascade_sweep metrics file")
            continue
        m = d["meta"]
        cp = commit_path(commits_dir, prefix, m["dsname"], m["train_seed"])
        if cp not in commits:
            if not cp.exists():
                raise FileNotFoundError(f"{cp} (commit of {jp.name}) not found; see --commits-dir / --commit-prefix.")
            commits[cp] = json.loads(cp.read_text())
        cells.append(read_cell(jp, d, commits[cp], cp, scheme=scheme, keys=keys, cal_frac=cal_frac))
    return cells


# --------------------------------------------------------------------------- #
# Statistics
# --------------------------------------------------------------------------- #
def agreement(points: list, tol: float) -> dict:
    """``{"n", pred: {spearman_rho, spearman_p, frac_within_tol, n_within_tol, mean_abs_err}}`` of obs_tier1 vs
    each predictor (points without an observed share are left out; rho is None when either side is constant)."""
    pts = [p for p in points if p.get("obs_tier1") is not None]
    out = {"n": len(pts)}
    obs = np.asarray([p["obs_tier1"] for p in pts], dtype=float)
    for name in PREDICTORS + SENSITIVITY:
        pr = np.asarray([p[name] for p in pts], dtype=float)
        st = {"spearman_rho": None, "spearman_p": None, "frac_within_tol": None, "n_within_tol": 0,
              "mean_abs_err": None}
        if pts:
            within = np.abs(obs - pr) <= tol + 1e-12
            st.update(frac_within_tol=float(within.mean()), n_within_tol=int(within.sum()),
                      mean_abs_err=float(np.abs(obs - pr).mean()))
            if len(pts) >= 3 and np.ptp(obs) > 0 and np.ptp(pr) > 0:
                rho, pv = spearmanr(obs, pr)
                st.update(spearman_rho=float(rho), spearman_p=float(pv))
        out[name] = st
    return out


def summarize_points(main_pts: list, cf_pts: dict, tol: float) -> dict:
    out = {"n_points": len(main_pts), "tol": tol,
           "main": agreement(main_pts, tol),
           "main_dep": agreement([p for p in main_pts if p["key"] == "dep"], tol),
           "by_dataset": {ds: agreement([p for p in main_pts if p["dataset"] == ds], tol)
                          for ds in sorted({p["dataset"] for p in main_pts})},
           "by_key": {k: agreement([p for p in main_pts if p["key"] == k], tol)
                      for k in KEYS if any(p["key"] == k for p in main_pts)}}
    if cf_pts:
        out["calfrac"] = {cf_label(cf): agreement(pts, tol) for cf, pts in sorted(cf_pts.items())}
        out["all_with_calfrac"] = agreement(main_pts + [p for pts in cf_pts.values() for p in pts], tol)
    return out


def headline(label: str, st: dict) -> str:
    def one(name):
        s = st[name]
        rho = "n/a" if s["spearman_rho"] is None else f"{s['spearman_rho']:.3f} (p = {s['spearman_p']:.2e})"
        fr = "n/a" if s["frac_within_tol"] is None else f"{s['frac_within_tol']:.3f} ({s['n_within_tol']}/{st['n']})"
        return f"{name}: Spearman rho = {rho}, within tol = {fr}"
    return (f"[margin] {label:<22s} n={st['n']:4d} | {one('pred_tier1')} | {one('pred_tier1_thr')} | "
            f"{one('pred_tier1_hyper')}")


# --------------------------------------------------------------------------- #
# Writing
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list, cols) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cols), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def md_table(rows: list, cols, dec: dict) -> list:
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(f(r.get(c), dec.get(c, 3)) for c in cols) + " |")
    return lines


def summary_md(summ: dict, inputs: str) -> str:
    cols = ("subset", "predictor", "n", "spearman_rho", "spearman_p", "frac_within_tol", "n_within_tol", "mean_abs_err")
    rows = []

    def add(label, st, names=PREDICTORS):
        for name in names:
            s = st[name]
            rows.append({"subset": label, "predictor": name, "n": st["n"], "spearman_rho": s["spearman_rho"],
                         "spearman_p": None if s["spearman_p"] is None else f"{s['spearman_p']:.2e}",
                         "frac_within_tol": s["frac_within_tol"], "n_within_tol": s["n_within_tol"],
                         "mean_abs_err": s["mean_abs_err"]})
    add("main (all keys)", summ["main"], PREDICTORS + SENSITIVITY)
    add("main, key dep", summ["main_dep"], PREDICTORS + SENSITIVITY)
    for k, st in summ["by_key"].items():
        if k != "dep":
            add(f"main, key {k}", st)
    for ds, st in summ["by_dataset"].items():
        add(f"main, {ds}", st)
    for cf, st in summ.get("calfrac", {}).items():
        add(f"cal_frac {cf}", st)
    if "all_with_calfrac" in summ:
        add("main + cal_frac", summ["all_with_calfrac"])
    head = (f"# TABLE_E10_margin_summary -- obs_tier1 vs the margin predictions (E10)\n\n"
            f"{inputs}\n\nn_points (main) = {summ['n_points']}; tol = {summ['tol']}.  spearman_rho / spearman_p: "
            "scipy.stats.spearmanr of obs_tier1 vs the predictor (empty when either side is constant); "
            "frac_within_tol: share of points with |obs_tier1 - prediction| <= tol; mean_abs_err: mean "
            "|obs_tier1 - prediction|.  pred_tier1 uses the deepest stratum's full-information risk r_full, "
            "pred_tier1_thr its best threshold-rule risk rmin_thr (optimistic); pred_tier1_nk_calpool (sensitivity) "
            "uses n_k = round(cal_frac * n_k_calpool), the split's own expected draw count, instead of the commit's "
            "probe-based count.  pred_tier1 (the specified predictor) is the unconditional binomial prediction (the "
            "calibration draw as fresh rows of risk r_full, i.e. over resampling of the calibration pool); "
            "pred_tier1_hyper (sensitivity) is the prediction conditional on the split's calibration pool (draws "
            "without replacement): sum over n_d of Hypergeom(N_pool, N_k, n_cal).pmf(n_d) * Hypergeom(N_k, E_k, "
            "n_d).cdf(k_max(n_d)) with N_pool = meta n_calpool, N_k = n_k_calpool, E_k = round(r_full N_k), n_cal = "
            "round(cal_frac N_pool) (the indicator 1[E_k <= k_max(N_k)] at cal_frac 1.0).  Explanatory analysis, "
            "not a selection step.\n\n")
    return head + "\n".join(md_table(rows, cols, {"spearman_rho": 3, "frac_within_tol": 3, "mean_abs_err": 3})) + "\n"


def e11_rows(main_cells: list, cf_cells: dict, main_cf: float, cfs: list, key: str) -> list:
    """One row per cell (dataset, policy, seed) with ``{metric}_cf{CF}`` columns; missing runs -> TBD-RUN, a key
    whose metrics block lacks the cost scheme (``by_key`` value ``NA``) -> ``NA_E11`` ("n/a (no scheme)")."""
    by = {cf: {(c["dataset"], c["policy"], c["seed"]): c for c in cells} for cf, cells in cf_cells.items()}
    by[main_cf] = {(c["dataset"], c["policy"], c["seed"]): c for c in main_cells}
    ids = sorted({i for v in by.values() for i in v})
    rows = []
    for ds, pol, ts in ids:
        row = {"dataset": ds, "policy": pol, "seed": ts, "key": key}
        for metric in E11_METRICS:
            for cf in cfs:
                c = by.get(cf, {}).get((ds, pol, ts))
                v = c["by_key"].get(key) if c else None
                row[f"{metric}_cf{cf_label(cf)}"] = TBD if v is None else NA_E11 if v == NA else v[metric]
        rows.append(row)
    return rows


def dataset_colors(names) -> dict:
    """Fixed palette slot per known dataset (DATASET_ORDER); unknown datasets take the unused slots, then gray."""
    known = dict(zip(DATASET_ORDER, PALETTE))
    free = [c for c in PALETTE if c not in {known[n] for n in names if n in known}]
    out = {}
    for n in [n for n in DATASET_ORDER if n in names] + sorted(n for n in names if n not in known):
        out[n] = known.get(n) or (free.pop(0) if free else "#7f7f7f")
    return out


def fig_margin(main_pts: list, cf_pts: dict, main_cf: float, out: Path, tol: float, summ: dict, png: bool) -> None:
    pts_all = main_pts + [p for v in cf_pts.values() for p in v]
    pts_all = [p for p in pts_all if p["obs_tier1"] is not None]
    if not pts_all:
        return
    colors = dataset_colors({p["dataset"] for p in pts_all})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.8))

    keys_present = sorted({p["key"] for p in pts_all}, key=lambda k: (KEYS.index(k) if k in KEYS else 99, k))
    marker = {k: MARKERS.get(k, "X") for k in keys_present}

    def scatter(ax, pts, xkey, open_=False, size=26):
        for ds in colors:
            for key, mk in marker.items():
                sel = [p for p in pts if p["dataset"] == ds and p["key"] == key and p["obs_tier1"] is not None]
                if not sel:
                    continue
                x = [p[xkey] for p in sel]
                y = [p["obs_tier1"] for p in sel]
                if open_:
                    ax.scatter(x, y, s=size, marker=mk, facecolors="none", edgecolors=colors[ds], linewidths=1.0,
                               alpha=0.9, zorder=3)
                else:
                    ax.scatter(x, y, s=size, marker=mk, c=colors[ds], edgecolors="#333333", linewidths=0.3,
                               alpha=0.8, zorder=4)

    cf_size = {cf: (14 if cf < main_cf else 44) for cf in cf_pts}
    # (a) obs vs z with the predicted curve at the median n_k / alpha / delta_1 of the main points
    base = [p for p in main_pts if p["obs_tier1"] is not None] or pts_all
    n_med = int(round(float(np.median([p["n_k"] for p in base]))))
    a_med = float(np.median([p["alpha"] for p in base]))
    d_med = float(np.median([p["delta_1"] for p in base]))
    zs = np.array([p["z"] for p in pts_all])
    zlo, zhi = min(-6.0, float(zs.min()) * 1.3), max(8.0, float(zs.max()) * 1.3)   # padding on the log part
    zg = np.unique(np.concatenate([np.linspace(zlo, zhi, 800), np.linspace(-6, 8, 800)]))

    def curve(n):
        sd = math.sqrt(a_med * (1.0 - a_med) / n)
        return np.array([pred_certify(n, a_med - z * sd, a_med, d_med) for z in zg])

    h_cur = [Line2D([], [], color="#0b0b0b", lw=1.6, label=f"pred_tier1(z), n_k = {n_med} (median)")]
    for q, ls in ((0.1, ":"), (0.9, "--")):
        nq = int(round(float(np.quantile([p["n_k"] for p in base], q))))
        if nq > 0 and nq != n_med:
            a1.plot(zg, curve(nq), color="#888888", lw=0.9, ls=ls, zorder=2)
            h_cur.append(Line2D([], [], color="#888888", lw=0.9, ls=ls, label=f"same, n_k = {nq} ({q:.0%} quantile)"))
    a1.plot(zg, curve(n_med), color="#0b0b0b", lw=1.6, zorder=5)
    scatter(a1, main_pts, "z")
    for cf, pts in sorted(cf_pts.items()):
        scatter(a1, pts, "z", open_=True, size=cf_size[cf])
    a1.set_xscale("symlog", linthresh=4.0, linscale=1.0)
    a1.set_xticks([t for t in (-100, -30, -10, -4, -2, 0, 2, 4, 10, 30, 100) if zlo <= t <= zhi])
    a1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    a1.xaxis.set_minor_locator(NullLocator())
    a1.axvline(0.0, color="#bbbbbb", lw=0.6, zorder=1)
    a1.set_xlim(zlo, zhi)
    a1.set_ylim(-0.04, 1.04)
    a1.set_xlabel("z = (alpha - r_full) sqrt(n_k / (alpha(1 - alpha)))  [symlog, linear |z| < 4]", fontsize=7)
    a1.set_ylabel("observed tier-1 share (per split)", fontsize=8)
    a1.set_title("(a) tier-1 share vs deepest-stratum margin", fontsize=8)
    a1.tick_params(labelsize=7)
    a1.grid(True, color="#e6e6e6", lw=0.5, zorder=0)

    # (b) obs vs pred with the diagonal and a +-tol band
    xg = np.linspace(0, 1, 101)
    a2.fill_between(xg, np.clip(xg - tol, 0, 1), np.clip(xg + tol, 0, 1), color="#ececec", zorder=1, lw=0)
    a2.plot([0, 1], [0, 1], color="#0b0b0b", lw=1.0, zorder=2)
    scatter(a2, main_pts, "pred_tier1")
    for cf, pts in sorted(cf_pts.items()):
        scatter(a2, pts, "pred_tier1", open_=True, size=cf_size[cf])
    st = summ["main"]["pred_tier1"]
    txt = [f"main points: n = {summ['main']['n']}"]
    if st["spearman_rho"] is not None:
        txt.append(f"Spearman rho = {st['spearman_rho']:.2f}")
    if st["frac_within_tol"] is not None:
        txt.append(f"within ±{tol:g}: {st['n_within_tol']}/{summ['main']['n']} ({st['frac_within_tol']:.2f})")
    a2.text(0.03, 0.97, "\n".join(txt), transform=a2.transAxes, va="top", ha="left", fontsize=7,
            bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": "#cccccc", "lw": 0.5}, zorder=6)
    a2.set_xlim(-0.04, 1.04)
    a2.set_ylim(-0.04, 1.04)
    a2.set_xlabel("predicted tier-1 share  P(Bin(n_k, r_full) <= k_max)", fontsize=7)
    a2.set_ylabel("observed tier-1 share (per split)", fontsize=8)
    a2.set_title(f"(b) observed vs predicted (band: ±{tol:g})", fontsize=8)
    a2.tick_params(labelsize=7)
    a2.grid(True, color="#e6e6e6", lw=0.5, zorder=0)

    # legends below the panels: datasets (colour), lambda_ref keys (marker), curves and cal_frac markers
    h_ds = [Line2D([], [], ls="", marker="o", ms=5, mfc=c, mec="#333333", mew=0.3, label=ds) for ds, c in colors.items()]
    h_key = [Line2D([], [], ls="", marker=marker[k], ms=5, mfc="#9a9a9a", mec="#333333", mew=0.3,
                    label=f"lambda_ref {k}") for k in keys_present]
    h_cf = [Line2D([], [], ls="", marker="o", ms=4.5, mfc="#9a9a9a", mec="#333333", mew=0.3,
                   label=f"cal_frac {cf_label(main_cf)} (main)")]
    for cf in sorted(cf_pts):
        h_cf.append(Line2D([], [], ls="", marker="o", ms=math.sqrt(cf_size[cf]), mfc="none", mec="#333333", mew=1.0,
                           label=f"cal_frac {cf_label(cf)} (open)"))
    lk = {"loc": "upper left", "fontsize": 6.5, "frameon": False, "title_fontsize": 6.5, "columnspacing": 1.0,
          "handletextpad": 0.4, "alignment": "left"}
    groups = [(0.01, h_ds, "dataset (colour)", 2), (0.34, h_key, "lambda_ref (marker)", 1)]
    if cf_pts:
        groups.append((0.485, h_cf, "calibration fraction", 1))
    groups.append((0.655 if cf_pts else 0.52, h_cur,
                   f"curve in (a): alpha = {a_med:g} (median), delta_1 = {d_med:g}", 1))
    for x0, hs, title, nc in groups:
        fig.add_artist(fig.legend(handles=hs, bbox_to_anchor=(x0, 0.195), title=title, ncol=nc, **lk))
    fig.tight_layout(rect=(0, 0.21, 1, 1))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    if png:
        fig.savefig(out.with_suffix(".png"), dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3 certifiability-margin analysis (E10) and calibration-size table (E11)")
    p.add_argument("--metrics-dir", required=True, help="the main metrics (e.g. $RESULTS_ROOT/metrics_v3)")
    p.add_argument("--commits-dir", default=str(REPO / "configs"))
    p.add_argument("--commit-prefix", default="committed_v3_", help="commit = {commits-dir}/{prefix}{dsname}_ts{ts}.json")
    p.add_argument("--scheme", default="uniform")
    p.add_argument("--keys", default=",".join(KEYS), help="lambda_ref keys (default 0.5,0.7,0.9,dep)")
    p.add_argument("--calfrac-dir", nargs=2, action="append", default=[], metavar=("CF", "PATH"),
                   help="metrics swept with --cal-frac CF (repeatable)")
    p.add_argument("--e11-key", default="dep")
    p.add_argument("--e11-calfracs", default="0.25,1.0",
                   help="cal_frac columns of TABLE_E11 besides the main one (missing runs -> TBD-RUN)")
    p.add_argument("--tol", type=float, default=0.2)
    p.add_argument("--output-dir", default="results_v3/tables")
    p.add_argument("--figure", default="results_v3/figures/F7_margin.pdf")
    p.add_argument("--png", action="store_true", help="also write the figure as PNG (same stem)")
    a = p.parse_args(argv)
    t0 = time.time()
    keys = [k.strip() for k in a.keys.split(",") if k.strip()]
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    kw = {"commits_dir": Path(a.commits_dir), "prefix": a.commit_prefix, "scheme": a.scheme, "keys": keys}

    main_cells = scan(Path(a.metrics_dir), **kw)
    if not main_cells:
        print(f"[margin] no metrics JSON in {a.metrics_dir}", file=sys.stderr)
        return 2
    main_cfs = sorted({c["cal_frac"] for c in main_cells})
    if len(main_cfs) != 1:
        raise ValueError(f"{a.metrics_dir} mixes calibration fractions {main_cfs}.")
    main_cf = main_cfs[0]
    cf_cells, cf_dirs = {}, {}
    for cf_s, path in a.calfrac_dir:
        cf = float(cf_s)
        if abs(cf - main_cf) < 1e-12 or cf in cf_cells:
            raise ValueError(f"--calfrac-dir {cf_s}: duplicate calibration fraction (main = {main_cf}).")
        cf_dirs[cf] = path
        if not Path(path).is_dir():
            print(f"[margin] WARNING: --calfrac-dir {cf_s} {path} does not exist: its cells are {TBD}")
            cf_cells[cf] = []
            continue
        cf_cells[cf] = scan(Path(path), cal_frac=cf, **kw)

    main_pts = [pt for c in main_cells for pt in c["points"]]
    cf_pts = {cf: [pt for c in cells for pt in c["points"]] for cf, cells in cf_cells.items() if cells}
    order = {k: i for i, k in enumerate(KEYS)}

    def sort_key(pt):
        return (pt["dataset"], pt["policy"], pt["seed"], order.get(pt["key"], 99), pt["key"], pt["split"])

    main_pts.sort(key=sort_key)
    for v in cf_pts.values():
        v.sort(key=sort_key)
    summ = summarize_points(main_pts, cf_pts, a.tol)

    cdir = Path(a.commits_dir).resolve()
    cdir = cdir.relative_to(REPO) if cdir.is_relative_to(REPO) else cdir      # repo-relative when inside the repo
    cpat = f"{cdir.as_posix()}/{a.commit_prefix}{{dsname}}_ts{{ts}}.json"
    inputs = (f"Inputs: metrics `{Path(a.metrics_dir).as_posix()}/*.json` ({len(main_cells)} files, scheme "
              f"`{a.scheme}`, cal_frac {cf_label(main_cf)}); commits `{cpat}`"
              + "".join(f"; cal_frac {cf_label(cf)}: `{Path(pth).as_posix()}`" for cf, pth in sorted(cf_dirs.items())) + ".")
    summ["inputs"] = {"metrics_dir": str(a.metrics_dir), "n_files": len(main_cells), "scheme": a.scheme,
                      "keys": keys, "commits": cpat, "main_cal_frac": main_cf,
                      "calfrac_dirs": {cf_label(cf): pth for cf, pth in sorted(cf_dirs.items())},
                      "files": [c["path"] for c in main_cells]}
    summ["what"] = ("E10: observed tier-1 share per (dataset, policy, seed, lambda_ref key, split) vs the exact "
                    "binomial probability that the deepest stratum's Hoeffding-Bentkus certificate at level delta_1 "
                    "is issued at full information (pred_tier1) / at its best threshold rule (pred_tier1_thr); the "
                    "binomial is the unconditional prediction (over resampling of the calibration pool), "
                    "pred_tier1_hyper the hypergeometric one conditional on the split's calibration pool.")

    # ---- E10 table + summary ----
    write_csv(out / "TABLE_E10_margin.csv", main_pts, E10_COLS + SENSITIVITY)
    defs = ("One row per (dataset, policy, seed, lambda_ref key, split).  k_star = deepest populated stratum of the "
            "split's whole-calibration-pool audit (audit_by_split); n_k = expected calibration-draw count of k_star "
            "(commit edges[policy][key].expected_cal_counts, nearest integer); n_k_calpool = rows of k_star in the "
            "split's calibration pool; r_full / rmin_thr / rmin_depth = its full-information / best-threshold / "
            "best-depth risk on the calibration pool; margin = alpha - r_full; z = margin sqrt(n_k / (alpha (1 - "
            "alpha))); k_max = largest error count with hoeffding_bentkus_pvalue(k / n_k, n_k, alpha) <= delta_1 = "
            "delta * delta_weights[0] (-1: none); pred_tier1 = P(Bin(n_k, r_full) <= k_max); pred_tier1_thr = the "
            "same with rmin_thr; obs_tier1 / tier3_share = share of the split's n_draws_split calibration draws "
            "deployed at tier 1 / tier 3.  Tier 1 needs every stratum certified at the top of the grid; the "
            "prediction looks at k_star only.  pred_tier1 (the specified predictor) is the unconditional binomial "
            "prediction: it treats the calibration draw as fresh rows of risk r_full, i.e. it averages over "
            "resampling of the calibration pool.  The CSV also has two sensitivity columns: pred_tier1_nk_calpool "
            "(n_k = round(cal_frac * n_k_calpool)) and pred_tier1_hyper, the prediction CONDITIONAL on the split's "
            "calibration pool (the draw takes n_cal = round(cal_frac N_pool) of its N_pool = meta n_calpool rows "
            "without replacement): sum over n_d of Hypergeom(N_pool, N_k, n_cal).pmf(n_d) * Hypergeom(N_k, E_k, "
            "n_d).cdf(k_max(n_d)) with N_k = n_k_calpool, E_k = round(r_full N_k) and k_max(n_d) as above (n_d "
            "with pmf > 1e-12); at cal_frac 1.0 it is the deterministic indicator 1[E_k <= k_max(N_k)].")
    (out / "TABLE_E10_margin.md").write_text(
        f"# TABLE_E10_margin -- deepest-stratum certifiability margin vs observed tier-1 share (E10)\n\n{inputs}\n\n"
        f"{defs}\n\n{len(main_pts)} points.\n\n" + "\n".join(md_table(main_pts, E10_COLS, E10_DEC)) + "\n",
        encoding="utf-8")
    if cf_pts:
        write_csv(out / "TABLE_E10_margin_calfrac.csv", [pt for _, v in sorted(cf_pts.items()) for pt in v],
                  ("cal_frac",) + E10_COLS + SENSITIVITY)
    (out / "TABLE_E10_margin_summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    (out / "TABLE_E10_margin_summary.md").write_text(summary_md(summ, inputs), encoding="utf-8")

    # ---- E11 calibration-size table ----
    cfs = sorted({main_cf, *cf_cells, *(float(x) for x in a.e11_calfracs.split(",") if x.strip())})
    rows = e11_rows(main_cells, cf_cells, main_cf, cfs, a.e11_key)
    cols = ["dataset", "policy", "seed", "key"] + [f"{m}_cf{cf_label(cf)}" for m in E11_METRICS for cf in cfs]
    write_csv(out / "TABLE_E11_calfrac.csv", rows, cols)
    dec = {c: (1 if c.startswith("n_k_") else 3) for c in cols}
    (out / "TABLE_E11_calfrac.md").write_text(
        f"# TABLE_E11_calfrac -- tier-1 share, cost and certified violation vs calibration size (lambda_ref key = "
        f"{a.e11_key}, scheme = {a.scheme})\n\n{inputs}\n\nOne row per cell; columns `{{metric}}_cf{{cal_frac}}` for "
        f"cal_frac in {', '.join(cf_label(cf) for cf in cfs)} (the calibration draw's fraction of the split's calibration "
        f"pool; {main_cf:g} = the protocol, the main metrics).  n_draws = calibration draws of the cell; n_k = mean over "
        "the splits of the expected calibration-draw count of the deepest stratum (commit expected_cal_counts x "
        f"cal_frac / {main_cf:g}, nearest integer); pred_tier1 = mean over the splits of the E10 prediction at that n_k "
        "(the unconditional binomial prediction, over resampling of the calibration pool); pred_tier1_hyper = mean over "
        "the splits of the E10 sensitivity conditional on the split's calibration pool (hypergeometric, draws without "
        "replacement; at cal_frac 1.0 the deterministic indicator 1[E_k <= k_max(N_k)]); "
        "tier1 = pooled tier-1 share; cost_over_T = deployed (cascade) mean test cost / T; certified_violation = share of "
        "draws whose exact one-sided binomial test-split p-value is <= 0.05 in some K_cal stratum.  At cal_frac 1.0 the "
        "calibration draw is the whole calibration pool, so the 20 draws of a split coincide: 1 draw per split (5 per "
        f"cell) was run.  {TBD}: no metrics file for that cell at that cal_frac; {NA_E11}: the metrics file exists "
        f"but its lambda_ref {a.e11_key} block has no cost scheme {a.scheme} (image cells are uniform-only).\n\n"
        + "\n".join(md_table(rows, cols, dec)) + "\n", encoding="utf-8")

    # ---- F7 ----
    fig_margin(main_pts, cf_pts, main_cf, Path(a.figure), a.tol, summ, a.png)

    print(f"[margin] E10: {len(main_pts)} points from {len(main_cells)} metrics files in {a.metrics_dir} "
          f"(cal_frac {cf_label(main_cf)})" + "".join(f"; cal_frac {cf_label(cf)}: {len(v)} points" for cf, v in sorted(cf_pts.items())))
    print(headline("main (all keys)", summ["main"]))
    print(headline("main, key dep", summ["main_dep"]))
    for cf, st in summ.get("calfrac", {}).items():
        print(headline(f"cal_frac {cf}", st))
    if "all_with_calfrac" in summ:
        print(headline("main + cal_frac", summ["all_with_calfrac"]))
    print(f"[margin] wrote TABLE_E10_margin.{{md,csv}}, TABLE_E10_margin_summary.{{json,md}}, TABLE_E11_calfrac.{{md,csv}}"
          f"{', TABLE_E10_margin_calfrac.csv' if cf_pts else ''} to {out}; figure {a.figure} "
          f"({time.time() - t0:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
