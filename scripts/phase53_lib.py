"""Phase 5.3 -- shared helpers for the final claim-validity pass.

Torch-free; reads only canonical inputs (metrics JSONs, pool caches,
committed configs). Every derived quantity is recomputed from the cached
`scores`/`correct`/`order` arrays and the probe-committed edges -- nothing is
re-trained, re-rolled, or re-committed.

Estimand conventions used across the Phase-5.3 scripts:
  * pool risk at a threshold j: mean over ALL eval rows of
    1{argmax prediction at the first grid[j]-crossing is wrong} -- exact on
    the fixed evaluation pool (the population for this experiment).
  * per-stratum pool risk: same, restricted to a probe-committed
    reference-depth bucket (fixed across resplits; never refit on cal).
  * forced-depth risk: mean over stratum rows of 1 - correct[:, t].
  * family-wide (intersection-union) p-value: max over the family of exact
    one-sided binomial upper-tail p-values P(Bin(n_k, alpha) >= s).
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta, binom

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "src"))

from cafa import config  # noqa: E402
from cafa.pool import cum_cost_from_order, load_pool_cache  # noqa: E402
from cafa.splits import probe_eval_split, resplit_cal_test  # noqa: E402

_Z = 1.96


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #
def wilson(k: int, n: int, z: float = _Z):
    """Wilson score interval; returns (p_hat, lo, hi)."""
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def binom_upper_p(s, n: int, alpha: float):
    """Exact one-sided binomial upper-tail p-value P(Bin(n, alpha) >= s).

    Vectorized over s. This is the p-value for H0: R <= alpha against R > alpha.
    Clipped to [0, 1].
    """
    s = np.asarray(s, dtype=float)
    p = binom.sf(s - 1.0, int(n), float(alpha))
    return np.clip(p, 0.0, 1.0)


def cp_lower_onesided(s: int, n: int, gamma: float = 0.05) -> float:
    """One-sided (1-gamma) Clopper-Pearson LOWER bound for a Bin(n, p) count s."""
    s = int(s)
    n = int(n)
    if s == 0:
        return 0.0
    return float(beta.ppf(gamma, s, n - s + 1))


def fmt(x, nd: int = 4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "n/a"
    return f"{x:.{nd}f}"


# --------------------------------------------------------------------------- #
# cached-array plumbing
# --------------------------------------------------------------------------- #
def stop_index_matrix(scores: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """First-crossing stop index s[n, G] (== T if the score never crosses)."""
    scores = np.asarray(scores, dtype=float)
    grid = np.asarray(grid, dtype=float)
    T = scores.shape[1] - 1
    crossed = scores[:, :, None] >= grid[None, None, :]
    any_cross = crossed.any(axis=1)
    first = crossed.argmax(axis=1)
    return np.where(any_cross, first, T).astype(int)


def load_cells(metrics_dir: Path) -> list:
    """One record per canonical metrics JSON."""
    cells = []
    for p in sorted(Path(metrics_dir).glob("*.json")):
        data = json.loads(p.read_text())
        meta = data["meta"]
        score = meta.get("score", "softmax")
        label = f"{meta['dsname']}/{meta['policy']}/ts{meta['train_seed']}" + \
                (f"[{score}]" if score != "softmax" else "")
        cells.append({
            "path": p, "data": data, "meta": meta, "label": label,
            "dsname": meta["dsname"], "ts": int(meta["train_seed"]),
            "policy": meta["policy"], "score": score,
            "alpha": float(data["alpha"]), "delta": float(data["delta"]),
            "grid": np.asarray(data["grid"], dtype=float),
        })
    return cells


def load_eval_arrays(cell: dict, cfg: dict, pool_dir: Path) -> dict:
    """Eval-row scores/correct/order for a cell, from the canonical pool cache."""
    meta = cell["meta"]
    cache_path = Path(pool_dir) / (
        f"{meta['dsname']}_ts{meta['train_seed']}_{meta['policy']}_{meta['score']}.npz")
    cache = load_pool_cache(cache_path)
    pv = cfg.get("protocol_v2", {})
    n_pool = cache["scores"].shape[0]
    _, eval_pos = probe_eval_split(np.arange(n_pool), float(pv.get("probe_frac", 0.10)),
                                   int(pv.get("probe_seed", 777)))
    out = {
        "scores": np.asarray(cache["scores"])[eval_pos],
        "correct": np.asarray(cache["correct"])[eval_pos],
        "order": np.asarray(cache["order"])[eval_pos],
        "cache_meta": cache["meta"],
    }
    out["n_eval"] = out["scores"].shape[0]
    out["T"] = out["scores"].shape[1] - 1
    assert out["n_eval"] == int(meta["n_eval"]), (
        f"eval-pool size mismatch for {cell['label']}: cache {out['n_eval']} "
        f"!= metrics {meta['n_eval']}")
    return out


def losses_costs(evald: dict, grid: np.ndarray, scheme: str):
    """(losses_full [n,G], costs_full [n,G], cc [n,T+1], s_full) for a cost scheme."""
    s_full = stop_index_matrix(evald["scores"], grid)
    n = evald["n_eval"]
    rows = np.arange(n)[:, None]
    losses_full = 1.0 - evald["correct"][rows, s_full]
    fc = np.asarray(evald["cache_meta"]["feature_costs_by_scheme"][scheme], dtype=float)
    cc = cum_cost_from_order(evald["order"], fc)
    costs_full = cc[rows, s_full]
    return losses_full, costs_full, cc, s_full


def primary_scheme(meta: dict) -> str:
    return "inverse_info" if "inverse_info" in meta["schemes"] else "uniform"


def committed_for(dsname: str, ts: int) -> dict:
    p = _REPO / "configs" / f"committed_v2_{dsname}_ts{ts}.json"
    return json.loads(p.read_text())


def edges_for(committed: dict, policy: str, score: str, lr_key: str) -> np.ndarray:
    """Probe-committed quantile-5 edges for (policy, score, lambda_ref)."""
    base = committed.get("score", "softmax")
    key = policy if score == base else f"{policy}@{score}"
    e = committed["edges"][key][lr_key]["quantile"]["5"]
    return np.asarray(e, dtype=float)


def bucket_ids(scores_eval: np.ndarray, lr: float, edges: np.ndarray) -> np.ndarray:
    """Probe-committed reference-depth bucket per eval row (never refit)."""
    from cafa.metrics import reference_buckets
    b, _ = reference_buckets(scores_eval, float(lr), 5, 50, edges=edges)
    return b


def deepest_nonempty(bucket: np.ndarray) -> int:
    """The deepest (largest-label) precommitted nonempty bucket -- label-free."""
    labels, counts = np.unique(bucket, return_counts=True)
    return int(labels[counts > 0].max())


def resplit_ix(n_eval: int, n_resplits: int, cal_frac: float):
    return [resplit_cal_test(np.arange(n_eval), rs, cal_frac) for rs in range(n_resplits)]


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=_REPO, check=True).stdout.strip()
    except Exception:
        return "unknown"


def default_pool_dir() -> Path:
    paths = config.load_paths()
    return Path(paths.results_root) / "pool_v2"


def provenance_header(extra: dict | None = None) -> dict:
    import platform
    from datetime import datetime, timezone
    h = {"generated": datetime.now(timezone.utc).isoformat(),
         "host": platform.node(), "git_commit": git_sha(),
         "numpy": np.__version__}
    if extra:
        h.update(extra)
    return h
