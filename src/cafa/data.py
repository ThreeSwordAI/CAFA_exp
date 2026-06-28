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