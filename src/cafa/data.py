"""Synthetic active-feature-acquisition (AFA) generator with a *known* true
risk curve, so the finite-sample guarantee can be checked exactly (G1 gate).

This module is synthetic-only: no datasets, no models.  It returns
``(losses, costs, true_risk_curve)`` where ``true_risk_curve`` is the exact
risk ``r(lambda)`` used to draw the losses, letting a test check the *true*
risk at the selected threshold.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "make_synthetic_afa",
    "make_synthetic_mondrian",
    "risk_curve",
    "load_mnist_afa",
    "patchify_images",
    "make_observed_tensors",
    "PATCH_GRID",
    "PATCH_SIZE",
    "N_PATCHES",
    "PATCH_DIM",
]

# Patch geometry for the MNIST-as-AFA setup: a 28x28 image is a 7x7 grid of
# 4x4 patches = 49 patch-features, each revealing 16 pixels.  These mirror the
# constants in :mod:`cafa.models` (kept here too so the data path is usable
# without importing torch).
PATCH_GRID = (7, 7)
PATCH_SIZE = 4
N_PATCHES = PATCH_GRID[0] * PATCH_GRID[1]   # 49
PATCH_DIM = PATCH_SIZE * PATCH_SIZE         # 16
_IMG_SIZE = PATCH_GRID[0] * PATCH_SIZE      # 28


def risk_curve(grid: np.ndarray, true_risk: str = "monotone", alpha: float = 0.1) -> np.ndarray:
    """Exact true risk ``r(lambda)`` on ``grid``, clipped to [0, 1].

    ``"monotone"``
        Decreasing curve ``r(lambda) = 0.5 * (1 - lambda)`` that crosses
        ``alpha`` inside the grid (at ``lambda = 1 - 2*alpha``; e.g. 0.8 for
        alpha=0.1).

    ``"nonmonotone"``
        Two low-risk valleys (deep below alpha) separated by a high-risk wall,
        so the risk-valid lambda are **scattered** into two disjoint intervals.
        A fixed-sequence test (contiguous from the top) can certify only the
        upper valley, whereas Bonferroni recovers both -- the power note in the
        G1 gate.
    """
    grid = np.asarray(grid, dtype=float)
    if true_risk == "monotone":
        r = 0.5 * (1.0 - grid)
    elif true_risk == "nonmonotone":
        r_high = 0.40
        valley_lo = 0.40 * np.exp(-((grid - 0.62) / 0.12) ** 2)  # lower valley ~[0.56, 0.68]
        valley_hi = 0.40 * np.exp(-((grid - 1.00) / 0.10) ** 2)  # upper valley ~[0.95, 1.00]
        r = r_high - valley_lo - valley_hi
    else:
        raise ValueError(f"unknown true_risk {true_risk!r}; expected 'monotone' or 'nonmonotone'.")
    return np.clip(r, 0.0, 1.0)


def make_synthetic_afa(
    n: int,
    grid: np.ndarray,
    true_risk: str = "monotone",
    alpha: float = 0.1,
    seed: int = 0,
    coupling: bool = True,
):
    """Draw a synthetic calibration set with known true risk.

    Parameters
    ----------
    n : int
        Number of calibration instances.
    grid : np.ndarray, shape [G]
        Candidate thresholds ``lambda`` (ascending).
    true_risk : {"monotone", "nonmonotone"}
        Shape of the true risk curve (see :func:`risk_curve`).
    alpha : float
        Target risk level (controls where the monotone curve crosses).
    seed : int
        Seed for all randomness.
    coupling : bool
        If ``True`` (realistic, nested across lambda): draw a single
        ``u_i ~ Uniform(0,1)`` per instance and set
        ``losses[i, j] = 1 if u_i < r(lambda_j) else 0`` -- so each column has
        ``P(loss=1) = r(lambda_j)`` and the losses are coupled across
        thresholds.  If ``False``: independent ``Bernoulli(r(lambda_j))`` per
        cell.

    Returns
    -------
    losses : np.ndarray, shape [n, G], in {0, 1}
    costs  : np.ndarray, shape [n, G], = lambda (increasing in lambda, >= 0)
    true_risk_curve : np.ndarray, shape [G]
        The exact ``r(lambda)`` used to draw the losses.
    """
    grid = np.asarray(grid, dtype=float)
    G = grid.shape[0]
    r = risk_curve(grid, true_risk=true_risk, alpha=alpha)  # [G]
    rng = np.random.default_rng(seed)

    if coupling:
        u = rng.uniform(0.0, 1.0, size=(n, 1))          # one latent per instance
        losses = (u < r[None, :]).astype(float)         # P(loss=1) = r(lambda_j)
    else:
        draws = rng.uniform(0.0, 1.0, size=(n, G))      # independent per cell
        losses = (draws < r[None, :]).astype(float)

    costs = np.tile(grid[None, :], (n, 1)).astype(float)  # c(lambda) = lambda >= 0
    return losses, costs, r

# --------------------------------------------------------------------------- #
# MNIST as a patch-wise AFA problem (additive; synthetic code above is intact)
# --------------------------------------------------------------------------- #
def patchify_images(images: np.ndarray) -> np.ndarray:
    """Turn ``[N, 28, 28]`` images into patchified pixels ``[N, P, D]``.

    Patch ``p = r*cols + c`` (row-major) holds the flattened ``4x4`` block at
    image rows ``4r:4r+4`` and cols ``4c:4c+4`` -- the exact convention used by
    :func:`cafa.models.patches_to_image` to invert this.  Values are passed
    through unchanged (callers scale to ``[0, 1]``).
    """
    X = np.asarray(images, dtype=np.float32)
    if X.ndim != 3 or X.shape[1:] != (_IMG_SIZE, _IMG_SIZE):
        raise ValueError(f"images must be [N, {_IMG_SIZE}, {_IMG_SIZE}]; got {X.shape}.")
    N = X.shape[0]
    rows, cols = PATCH_GRID
    # [N, rows, ps, cols, ps] -> [N, rows, cols, ps, ps] -> [N, P, D]
    X = X.reshape(N, rows, PATCH_SIZE, cols, PATCH_SIZE)
    X = X.transpose(0, 1, 3, 2, 4)
    return np.ascontiguousarray(X.reshape(N, N_PATCHES, PATCH_DIM))


def make_observed_tensors(X_patched: np.ndarray, observed_sets):
    """Build ``(images, masks)`` arrays for a list/array of observed patch sets.

    Parameters
    ----------
    X_patched : np.ndarray [N, P, D]
    observed_sets : iterable of length N
        ``observed_sets[i]`` is an iterable of observed patch indices for image
        ``i`` (possibly empty).

    Returns ``(images[N, P, D], masks[N, P])`` ready for
    :meth:`cafa.models.MaskedPredictor.predict_proba`.  ``images`` is the true
    patch tensor (hidden patches are zeroed by the predictor via ``masks``).
    """
    X = np.asarray(X_patched, dtype=np.float32)
    N, P, _ = X.shape
    masks = np.zeros((N, P), dtype=np.float32)
    for i, obs in enumerate(observed_sets):
        for a in obs:
            masks[i, int(a)] = 1.0
    return X, masks


def _disjoint_split_indices(n_total: int, fractions: dict, seed: int):
    """Pairwise-disjoint train/cal/test index sets from a shuffled permutation.

    ``train`` uses ``fractions['train']`` of the pool; the remainder is split
    into ``cal`` and ``test`` in proportion to their fractions, with the seed
    permuting which examples land where (so each protocol seed gives a fresh
    disjoint cal/test partition of the held-out pool).
    """
    rng = np.random.default_rng(int(seed))
    perm = rng.permutation(int(n_total))
    f_train = float(fractions.get("train", 0.6))
    f_cal = float(fractions.get("cal", 0.2))
    f_test = float(fractions.get("test", 0.2))

    n_train = int(round(f_train * n_total))
    rest = n_total - n_train
    denom = f_cal + f_test if (f_cal + f_test) > 0 else 1.0
    n_cal = int(round(rest * (f_cal / denom)))
    n_cal = max(0, min(n_cal, rest))

    train_idx = perm[:n_train]
    cal_idx = perm[n_train : n_train + n_cal]
    test_idx = perm[n_train + n_cal :]
    return train_idx, cal_idx, test_idx


def load_mnist_afa(cfg: dict, seed: int, download: bool = False) -> dict:
    """Load patchified MNIST with disjoint splits and per-feature costs.

    Returns a dict::

        train: (X_train, y_train)   # for fitting the masked predictor
        cal:   (X_cal,   y_cal)     # calibration pool for THIS seed
        test:  (X_test,  y_test)    # evaluation pool for THIS seed
        feature_costs: np.ndarray [49]   (uniform ones)
        patch_grid:  (7, 7)
        n_patches:   49
        patch_dim:   16
        n_classes:   10
        seed:        seed

    ``X`` is the patchified representation ``[N, P, D]``; build ``(image, mask)``
    tensors for a given observed set with :func:`make_observed_tensors`.

    The held-out pool (everything not in ``train``) is partitioned freshly per
    seed into disjoint ``cal`` / ``test``; the three index sets are asserted
    pairwise disjoint to protect the exchangeability premise.  ``cfg`` is the
    loaded experiment config (uses ``protocol.split_fractions``); paths come
    from :func:`cafa.config.load_paths`.
    """
    # Lazy imports so the synthetic path (above) stays torch-free.
    import torchvision  # noqa: WPS433

    from .config import load_paths

    paths = load_paths()
    data_root = str(paths.data_root)

    protocol = (cfg or {}).get("protocol", {})
    fractions = protocol.get("split_fractions", {"train": 0.6, "cal": 0.2, "test": 0.2})

    train_ds = torchvision.datasets.MNIST(data_root, train=True, download=download)
    test_ds = torchvision.datasets.MNIST(data_root, train=False, download=download)

    # Pool the official train+test, then make our own disjoint protocol splits
    # (the masked predictor trains once on `train`; cal/test are reshuffled per
    # seed from the held-out pool).
    imgs = np.concatenate(
        [train_ds.data.numpy().astype(np.float32), test_ds.data.numpy().astype(np.float32)],
        axis=0,
    )
    labels = np.concatenate(
        [train_ds.targets.numpy().astype(np.int64), test_ds.targets.numpy().astype(np.int64)],
        axis=0,
    )
    imgs = imgs / 255.0  # scale to [0, 1]

    train_idx, cal_idx, test_idx = _disjoint_split_indices(imgs.shape[0], fractions, seed)

    # ASSERT pairwise disjoint (exchangeability premise).
    s_tr, s_ca, s_te = set(train_idx.tolist()), set(cal_idx.tolist()), set(test_idx.tolist())
    assert s_tr.isdisjoint(s_ca), "train/cal index sets overlap"
    assert s_tr.isdisjoint(s_te), "train/test index sets overlap"
    assert s_ca.isdisjoint(s_te), "cal/test index sets overlap"

    X_all = patchify_images(imgs)

    out = {
        "train": (X_all[train_idx], labels[train_idx]),
        "cal": (X_all[cal_idx], labels[cal_idx]),
        "test": (X_all[test_idx], labels[test_idx]),
        "feature_costs": np.ones(N_PATCHES, dtype=float),
        "patch_grid": PATCH_GRID,
        "n_patches": N_PATCHES,
        "patch_dim": PATCH_DIM,
        "n_classes": 10,
        "seed": int(seed),
    }
    return out

def make_synthetic_mondrian(
    n: int,
    T: int,
    alpha: float = 0.10,
    gamma: float = 0.0,
    lambda_ref: float = 0.5,
    n_buckets: int = 5,
    min_per_bucket: int = 50,
    seed: int = 0,
) -> dict:
    """Synthetic AFA trajectories with *bucket-dependent* miscalibration.

    Builds a population whose stopping score rises at an instance-specific rate
    and whose *true* accuracy is depressed, near the start of acquisition, by a
    bucket-correlated amount ``gamma``.  This makes a single marginal threshold
    under-cover the fastest-rising ("cheap") instances while over-covering the
    rest -- the exact heterogeneity that per-bucket (Mondrian) control is meant
    to fix.  Because the true accuracy is known, the *true* per-bucket risk at
    any threshold can be computed exactly (no held-out estimation noise).

    Construction (``s = 0 .. T``)::

        beta_i        ~ Uniform(0.05, 0.5)                  # rise rate
        scores[i, s]  = 1 - exp(-beta_i * s)                # in [0, 1), increasing
        true_acc[i,s] = clip(scores[i,s] - gamma*(1 - s/T), 0, 1)
        correct[i,s]  ~ Bernoulli(true_acc[i, s])
        cum_cost[i,s] = s                                   # one unit per step

    At ``gamma = 0`` the score *is* the true accuracy (perfectly calibrated, no
    heterogeneity).  As ``gamma`` grows the penalty ``gamma*(1 - s/T)`` is
    largest at shallow depth ``s`` -- so instances that cross ``lambda_ref``
    early (low reference depth, the cheap bucket) are the most over-confident,
    and a marginal threshold calibrated on the mixture fails them.

    Buckets are assigned by reference depth at ``lambda_ref`` using the
    equal-width default of :func:`cafa.metrics.reference_buckets`; pass the
    returned ``scores`` to :func:`cafa.metrics.quantile_bucket_edges` instead if
    an equal-mass partition is wanted (the cheap stratum is then a clean
    minority).

    Returns
    -------
    dict with keys
        ``scores``   : [n, T+1] float, stopping scores in ``[0, 1)``
        ``true_acc`` : [n, T+1] float, exact accuracy used to draw ``correct``
        ``correct``  : [n, T+1] float in {0, 1}
        ``cum_cost`` : [n, T+1] float, ``cum_cost[i, s] = s``
        ``bucket_id``: [n] int, reference-depth bucket (equal-width default)
        ``edges``    : interior depth edges applied by ``reference_buckets``
        ``gamma``, ``T``, ``alpha`` : the inputs, echoed for bookkeeping
    """
    from .metrics import reference_buckets  # local import: avoid load-order coupling

    rng = np.random.default_rng(seed)
    s = np.arange(int(T) + 1, dtype=float)[None, :]          # [1, T+1]
    beta = rng.uniform(0.05, 0.5, size=(int(n), 1))          # [n, 1]

    scores = 1.0 - np.exp(-beta * s)                         # [n, T+1]
    frac_remaining = 1.0 - s / float(T)                      # [1, T+1], 1 at s=0 -> 0 at s=T
    true_acc = np.clip(scores - float(gamma) * frac_remaining, 0.0, 1.0)
    correct = (rng.uniform(0.0, 1.0, size=scores.shape) < true_acc).astype(float)
    cum_cost = np.tile(s, (int(n), 1)).astype(float)         # cum_cost[i, s] = s

    bucket_id, edges = reference_buckets(
        scores, lambda_ref=lambda_ref, n_buckets=n_buckets, min_per_bucket=min_per_bucket
    )

    return {
        "scores": scores,
        "true_acc": true_acc,
        "correct": correct,
        "cum_cost": cum_cost,
        "bucket_id": bucket_id,
        "edges": edges,
        "gamma": float(gamma),
        "T": int(T),
        "alpha": float(alpha),
    }

# --------------------------------------------------------------------------- #
# Step 4 -- cost-heterogeneous tabular AFA (additive; MNIST/synthetic above
# are byte-identical).  A "feature" is one acquirable original column; one-hot
# categoricals occupy a contiguous block of encoded columns (a feature reveals
# its whole block).  These loaders return the encoded matrix + feature_groups
# consumed by :func:`cafa.tabular.tabular_rollout`.
# --------------------------------------------------------------------------- #
__all__ += ["assign_feature_costs", "load_tabular_afa", "make_synthetic_tabular_afa"]


def assign_feature_costs(
    X_train: np.ndarray,
    y_train: np.ndarray,
    scheme: str,
    feature_groups=None,
    seed: int = 0,
) -> np.ndarray:
    """Per-feature acquisition costs ``[d]`` under a chosen cost scheme.

    A cost scheme is a **modeling choice** reported transparently (run >= 2 for
    robustness).  ``X_train`` is the *encoded* training matrix ``[N, n_cols]``;
    ``feature_groups`` maps each feature to its encoded columns (``None`` ->
    identity, one column per feature).

    Schemes
    -------
    ``inverse_info`` (default, the interesting one)
        Per-feature informativeness via ``mutual_info_classif`` on **train only**
        (aggregated across a feature's one-hot columns by the max), normalised to
        ``[0, 1]``, then ``cost = 1 + 9 * (1 - MI_norm) in [1, 10]`` -- informative
        features are **expensive**, uninformative are **cheap**.  This makes
        low-information stopping cheap-in-count and creates the regime where the
        cheap-bucket over-promise *can* appear.
    ``random``
        Costs ``~ Uniform{1..10}`` (integer), seeded.
    ``uniform``
        All costs ``= 1`` (control; matches the image setting).
    """
    X_train = np.asarray(X_train, dtype=float)
    n_cols = X_train.shape[1]
    if feature_groups is None:
        feature_groups = [np.array([j], dtype=int) for j in range(n_cols)]
    d = len(feature_groups)
    scheme = str(scheme).lower()

    if scheme == "uniform":
        return np.ones(d, dtype=float)

    if scheme == "random":
        rng = np.random.default_rng(int(seed))
        return rng.integers(1, 11, size=d).astype(float)

    if scheme == "inverse_info":
        from sklearn.feature_selection import mutual_info_classif  # lazy import

        mi_cols = mutual_info_classif(
            X_train, np.asarray(y_train).ravel(), random_state=int(seed)
        )
        # Aggregate per feature (max over its encoded columns).
        mi_feat = np.array([float(np.max(mi_cols[g])) for g in feature_groups])
        rng_span = mi_feat.max() - mi_feat.min()
        if rng_span <= 0:
            mi_norm = np.zeros(d, dtype=float)
        else:
            mi_norm = (mi_feat - mi_feat.min()) / rng_span
        return 1.0 + 9.0 * (1.0 - mi_norm)

    raise ValueError(
        f"unknown cost scheme {scheme!r}; expected 'inverse_info', 'random', 'uniform'."
    )


def load_tabular_afa(
    name: str,
    cfg: dict,
    seed: int,
    cost_scheme: str = "inverse_info",
    download: bool = False,
) -> dict:
    """Load an OpenML tabular classification dataset as an AFA problem.

    Standardises numeric columns and one-hot-encodes categoricals (fit on the
    **train** split only), so a "feature" = one original column and acquiring a
    categorical reveals its whole one-hot block.  Splits are disjoint
    ``train`` / ``cal`` / ``test`` (asserted), reusing the same seeded partition
    logic as :func:`load_mnist_afa`.

    Returns a dict::

        train / cal / test : (X_encoded [n, n_cols], y [n])
        feature_costs : np.ndarray [d]         # per the cost scheme, on train
        feature_groups : list[np.ndarray]      # encoded columns per feature
        n_features : d   n_cols : int   n_classes : int
        cost_scheme : str   name : str   seed : int

    Paths come from :func:`cafa.config.load_paths` (``DATA_ROOT``).  ``download``
    is passed through to ``fetch_openml``'s cache; pre-download on a login node.
    """
    from sklearn.datasets import fetch_openml
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    from .config import load_paths

    paths = load_paths()
    data_home = str(paths.data_root)

    ds = fetch_openml(name, version=2, data_home=data_home, as_frame=True)
    frame = ds.frame.copy()
    target_col = ds.target.name
    y_raw = frame[target_col]
    X_df = frame.drop(columns=[target_col])

    # Encode labels to integers.
    y_cats = y_raw.astype("category")
    y = y_cats.cat.codes.to_numpy().astype(np.int64)
    n_classes = int(y.max()) + 1

    # Drop rows with missing values (keeps the AFA semantics clean).
    keep = ~(X_df.isna().any(axis=1).to_numpy())
    X_df = X_df.loc[keep].reset_index(drop=True)
    y = y[keep]

    num_cols = list(X_df.select_dtypes(include=["number"]).columns)
    cat_cols = [c for c in X_df.columns if c not in num_cols]

    protocol = (cfg or {}).get("protocol", {})
    fractions = protocol.get("split_fractions", {"train": 0.6, "cal": 0.2, "test": 0.2})
    n_total = X_df.shape[0]
    train_idx, cal_idx, test_idx = _disjoint_split_indices(n_total, fractions, seed)

    s_tr, s_ca, s_te = set(train_idx.tolist()), set(cal_idx.tolist()), set(test_idx.tolist())
    assert s_tr.isdisjoint(s_ca) and s_tr.isdisjoint(s_te) and s_ca.isdisjoint(s_te), \
        "train/cal/test index sets overlap"

    # Fit transformers on TRAIN only; the encoded column layout is fixed by the
    # fitted transformers and reused on cal/test.
    scaler = StandardScaler()
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # older sklearn
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)

    blocks = []            # list of (kind, original_col_name, encoded-width)
    if num_cols:
        scaler.fit(X_df.loc[train_idx, num_cols].to_numpy(dtype=float))
    if cat_cols:
        ohe.fit(X_df.loc[train_idx, cat_cols].astype(str).to_numpy())

    def _encode(rows_idx):
        parts = []
        if num_cols:
            parts.append(scaler.transform(X_df.loc[rows_idx, num_cols].to_numpy(dtype=float)))
        if cat_cols:
            parts.append(ohe.transform(X_df.loc[rows_idx, cat_cols].astype(str).to_numpy()))
        return np.hstack(parts).astype(np.float32) if parts else np.zeros((len(rows_idx), 0), np.float32)

    # Build feature_groups: numerics = 1 column each; each categorical = its block.
    feature_groups = []
    col = 0
    for _ in num_cols:
        feature_groups.append(np.array([col], dtype=int)); col += 1
    if cat_cols:
        cat_widths = [len(cats) for cats in ohe.categories_]
        for w in cat_widths:
            feature_groups.append(np.arange(col, col + w, dtype=int)); col += int(w)
    n_cols = col

    X_train = _encode(train_idx); X_cal = _encode(cal_idx); X_test = _encode(test_idx)
    feature_costs = assign_feature_costs(
        X_train, y[train_idx], cost_scheme, feature_groups=feature_groups, seed=seed
    )

    return {
        "train": (X_train, y[train_idx]),
        "cal": (X_cal, y[cal_idx]),
        "test": (X_test, y[test_idx]),
        "feature_costs": feature_costs,
        "feature_groups": feature_groups,
        "n_features": len(feature_groups),
        "n_cols": int(n_cols),
        "n_classes": n_classes,
        "cost_scheme": str(cost_scheme),
        "name": str(name),
        "seed": int(seed),
    }


def make_synthetic_tabular_afa(
    n: int, d: int = 8, n_classes: int = 2, n_informative: int = 3, seed: int = 0
) -> dict:
    """Small in-code synthetic tabular classifier (no download) for tests/smoke.

    A linear-logit generator: the first ``n_informative`` features carry class
    signal (decreasing weight), the rest are noise -- so mutual-information costs
    are meaningful (informative features expensive under ``inverse_info``).  All
    features are numeric (identity ``feature_groups``).

    Returns ``dict(X [n, d], y [n], feature_groups=None, n_classes)``.
    """
    rng = np.random.default_rng(int(seed))
    X = rng.standard_normal((int(n), int(d))).astype(np.float32)
    n_informative = int(min(n_informative, d))
    W = np.zeros((d, int(n_classes)), dtype=float)
    for c in range(int(n_classes)):
        w = rng.standard_normal(n_informative) * (1.0 / (1.0 + np.arange(n_informative)))
        W[:n_informative, c] = w
    logits = X @ W + 0.3 * rng.standard_normal((int(n), int(n_classes)))
    y = logits.argmax(axis=1).astype(np.int64)
    return {"X": X, "y": y, "feature_groups": None, "n_classes": int(n_classes)}