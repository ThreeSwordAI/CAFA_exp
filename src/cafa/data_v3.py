"""v3 -- dataset loaders for the AISTATS suite (AFABench-aligned).

All loaders return the v2 pool contract (see :func:`cafa.data.load_tabular_pool`
/ :func:`cafa.data.load_mnist_pool`): a FIXED train split that depends only on
``train_seed``, the heldout arrays in fixed order, probe/eval positions into
them (probe seed 777), per-scheme feature costs computed on TRAIN ONLY, and
split digests.  Every transform (NaN fill, standardisation, encoders) is fit on
the fixed train split -- never on heldout rows.

Datasets
--------
``csv:physionet`` / ``csv:diabetes``
    The AFABench CSVs (Schuetz et al., KDD 2026; MIT licence; last column is the
    label).  Place them at ``${DATA_ROOT}/afabench/physionet.csv`` and
    ``diabetes.csv`` (``scripts/download_data_v3.py`` fetches them).
``cube``
    Numpy port of AFABench's CubeDataset (20 features = 10 cube + 10 dummy; 8
    classes; the 3-bit code of label ``y`` sits at cube positions ``y, y+1,
    y+2`` with N(0, 0.1) noise, all other entries N(0.5, 0.3)).
``fashionmnist``
    Patchified exactly like MNIST (7x7 patches of 4x4 pixels, /255).
``image:imagenette``
    torchvision Imagenette (320px variant, resized to 256 / centre-cropped to
    ``img_size``), stored as uint8 ``[N, 3, H, W]``; features are the 7x7 patch
    grid (``32x32`` pixels each at 224).  Train+val pooled, then split 60/40
    by ``train_seed`` like every other dataset.
``tabular:MiniBooNE`` / ``tabular:adult``
    Unchanged (``cafa.data.load_tabular_pool``).

Torch is imported lazily; the numpy paths stay importable without it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import load_paths
from .data import assign_feature_costs, patchify_images
from .splits import assert_disjoint, fixed_train_heldout, probe_eval_split, split_digest

__all__ = [
    "dataset_kind",
    "load_csv_tabular_pool",
    "generate_cube",
    "load_cube_pool",
    "load_fashionmnist_pool",
    "load_image_patch_pool",
    "load_imagenette_pool",
    "load_pool_v3",
    "IMAGENET_MEAN",
    "IMAGENET_STD",
]

# Patch constants duplicated from cafa.models (which imports torch) so that the
# numpy loaders stay importable without torch.
PATCH_GRID = (7, 7)
PATCH_SIZE = 4
N_PATCHES = PATCH_GRID[0] * PATCH_GRID[1]
PATCH_DIM = PATCH_SIZE * PATCH_SIZE

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_SCHEMES = ("uniform", "inverse_info", "random")


def dataset_kind(dataset: str) -> str:
    """``image_patches`` | ``image_rgb`` | ``tabular_openml`` | ``tabular_csv`` | ``synthetic_cube``."""
    if dataset in ("mnist", "fashionmnist"):
        return "image_patches"
    if dataset.startswith("image:"):
        return "image_rgb"
    if dataset.startswith("tabular:"):
        return "tabular_openml"
    if dataset.startswith("csv:"):
        return "tabular_csv"
    if dataset == "cube":
        return "synthetic_cube"
    raise ValueError(f"unknown dataset {dataset!r}.")


def _protocol(cfg: dict) -> "tuple[float, float, int]":
    pv = (cfg or {}).get("protocol_v3", (cfg or {}).get("protocol_v2", {}))
    return float(pv.get("train_frac", 0.6)), float(pv.get("probe_frac", 0.10)), int(pv.get("probe_seed", 777))


def _tabular_pool_from_arrays(X_all: np.ndarray, y_all: np.ndarray, name: str, cfg: dict,
                              train_seed: int, standardize: bool = True) -> dict:
    """Shared tail of every tabular loader: fixed split, TRAIN-only preprocessing, costs."""
    X_all = np.asarray(X_all, dtype=np.float64)
    y_all = np.asarray(y_all).astype(np.int64)
    n_total, d = X_all.shape
    train_frac, probe_frac, probe_seed = _protocol(cfg)
    train_idx, heldout_idx = fixed_train_heldout(n_total, train_frac, train_seed)
    probe_pos, eval_pos = probe_eval_split(np.arange(heldout_idx.size), probe_frac, probe_seed)
    global_probe, global_eval = heldout_idx[probe_pos], heldout_idx[eval_pos]
    assert_disjoint(train=train_idx, probe=global_probe, eval=global_eval)

    Xtr = X_all[train_idx]
    col_mean = np.nanmean(Xtr, axis=0)
    col_mean = np.where(np.isfinite(col_mean), col_mean, 0.0)
    X_filled = np.where(np.isnan(X_all), col_mean[None, :], X_all)
    if standardize:
        mu = X_filled[train_idx].mean(axis=0)
        sd = X_filled[train_idx].std(axis=0)
        sd = np.where(sd > 1e-12, sd, 1.0)
        X_filled = (X_filled - mu[None, :]) / sd[None, :]
    X_f = X_filled.astype(np.float32)
    feature_groups = [np.array([j], dtype=int) for j in range(d)]
    costs = {s: assign_feature_costs(X_f[train_idx], y_all[train_idx], s, feature_groups, seed=0)
             for s in _SCHEMES}
    classes = np.unique(y_all)
    assert np.array_equal(classes, np.arange(classes.size)), "labels must be 0..C-1"
    return {
        "train": (X_f[train_idx], y_all[train_idx]),
        "heldout": (X_f[heldout_idx], y_all[heldout_idx]),
        "heldout_index": heldout_idx, "probe_pos": probe_pos, "eval_pos": eval_pos,
        "feature_costs_by_scheme": costs, "feature_groups": feature_groups,
        "n_features": d, "n_classes": int(classes.size), "n_cols": int(d),
        "name": str(name), "train_seed": int(train_seed),
        "split_digest": {"train": split_digest(train_idx), "probe": split_digest(global_probe),
                         "eval": split_digest(global_eval)},
    }


# --------------------------------------------------------------------------- #
# AFABench CSVs
# --------------------------------------------------------------------------- #
def load_csv_tabular_pool(name: str, cfg: dict, train_seed: int, csv_path=None) -> dict:
    import pandas as pd  # lazy

    paths = load_paths()
    csv_path = Path(csv_path) if csv_path else Path(paths.data_root) / "afabench" / f"{name}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} not found. Run scripts/download_data_v3.py --csv (fetches the AFABench CSVs) "
            "or copy extra/data/misc/{physionet,diabetes}.csv from the AFABench repository.")
    df = pd.read_csv(csv_path)
    X = df.iloc[:, :-1].to_numpy(dtype=np.float64)
    y_raw = df.iloc[:, -1].to_numpy()
    y = np.asarray(np.round(y_raw.astype(float)), dtype=np.int64)
    return _tabular_pool_from_arrays(X, y, f"csv:{name}", cfg, train_seed, standardize=True)


# --------------------------------------------------------------------------- #
# CUBE (AFABench CubeDataset, numpy port)
# --------------------------------------------------------------------------- #
def generate_cube(n_samples: int = 20000, seed: int = 123, non_informative_mean: float = 0.5,
                  informative_std: float = 0.1, non_informative_std: float = 0.3):
    """Numpy port of AFABench's CubeDataset (torch RNG replaced by numpy; same law)."""
    rng = np.random.default_rng(int(seed))
    n_cube, n_dummy, n_classes = 10, 10, 8
    y = rng.integers(0, n_classes, size=int(n_samples))
    codes = np.array([[int(b) for b in format(i, "03b")][::-1] for i in range(n_classes)], dtype=float)
    x_cube = rng.normal(non_informative_mean, non_informative_std, size=(int(n_samples), n_cube))
    x_dummy = rng.normal(non_informative_mean, non_informative_std, size=(int(n_samples), n_dummy))
    for i in range(int(n_samples)):
        lbl = int(y[i])
        idxs = [lbl + j for j in range(3)]
        x_cube[i, idxs] = rng.normal(0.0, informative_std, size=3) + codes[lbl]
    X = np.concatenate([x_cube, x_dummy], axis=1).astype(np.float32)
    return X, y.astype(np.int64)


def load_cube_pool(cfg: dict, train_seed: int, n_samples: int = None, seed: int = None) -> dict:
    spec = next((d for d in (cfg or {}).get("datasets_v3", []) if d.get("name") == "cube"), {})
    n_samples = int(n_samples or spec.get("n_samples", 20000))
    seed = int(seed if seed is not None else spec.get("seed", 123))
    X, y = generate_cube(n_samples, seed)
    return _tabular_pool_from_arrays(X, y, "cube", cfg, train_seed, standardize=False)


# --------------------------------------------------------------------------- #
# Patchified images: MNIST (v2 loader) and FashionMNIST
# --------------------------------------------------------------------------- #
def load_fashionmnist_pool(cfg: dict, train_seed: int, download: bool = False) -> dict:
    import torchvision  # lazy

    paths = load_paths()
    data_root = str(paths.data_root)
    train_frac, probe_frac, probe_seed = _protocol(cfg)
    tr = torchvision.datasets.FashionMNIST(data_root, train=True, download=download)
    te = torchvision.datasets.FashionMNIST(data_root, train=False, download=download)
    imgs = np.concatenate([tr.data.numpy().astype(np.float32), te.data.numpy().astype(np.float32)], axis=0) / 255.0
    labels = np.concatenate([tr.targets.numpy().astype(np.int64), te.targets.numpy().astype(np.int64)], axis=0)
    X_all = patchify_images(imgs)
    n_total = X_all.shape[0]
    train_idx, heldout_idx = fixed_train_heldout(n_total, train_frac, train_seed)
    probe_pos, eval_pos = probe_eval_split(np.arange(heldout_idx.size), probe_frac, probe_seed)
    global_probe, global_eval = heldout_idx[probe_pos], heldout_idx[eval_pos]
    assert_disjoint(train=train_idx, probe=global_probe, eval=global_eval)
    return {
        "train": (X_all[train_idx], labels[train_idx]),
        "heldout": (X_all[heldout_idx], labels[heldout_idx]),
        "heldout_index": heldout_idx, "probe_pos": probe_pos, "eval_pos": eval_pos,
        "feature_costs_by_scheme": {"uniform": np.ones(N_PATCHES, dtype=float)},
        "feature_groups": None, "n_classes": 10, "n_patches": N_PATCHES,
        "patch_grid": PATCH_GRID, "patch_dim": PATCH_DIM, "name": "fashionmnist",
        "train_seed": int(train_seed),
        "split_digest": {"train": split_digest(train_idx), "probe": split_digest(global_probe),
                         "eval": split_digest(global_eval)},
    }


def load_image_patch_pool(name: str, cfg: dict, train_seed: int, download: bool = False) -> dict:
    if name == "mnist":
        from .data import load_mnist_pool
        return load_mnist_pool(cfg, train_seed=train_seed, download=download)
    if name == "fashionmnist":
        return load_fashionmnist_pool(cfg, train_seed=train_seed, download=download)
    raise ValueError(f"unknown patch-image dataset {name!r}.")


# --------------------------------------------------------------------------- #
# Imagenette (RGB, 7x7 patch grid at 224)
# --------------------------------------------------------------------------- #
def _imagenette_arrays(data_root: str, img_size: int, download: bool) -> "tuple[np.ndarray, np.ndarray]":
    """Pool train+val Imagenette as uint8 [N, 3, S, S] + labels; cached as .npz."""
    cache = Path(data_root) / "imagenette_cache" / f"imagenette_{img_size}.npz"
    if cache.exists():
        z = np.load(cache)
        return z["images"], z["labels"]
    import torch  # noqa: F401  (lazy)
    import torchvision
    from torchvision import transforms

    tf = transforms.Compose([transforms.Resize(int(round(img_size * 256 / 224))),
                             transforms.CenterCrop(img_size), transforms.PILToTensor()])
    imgs, labels = [], []
    for split in ("train", "val"):
        ds = torchvision.datasets.Imagenette(data_root, split=split, size="320px", download=download, transform=tf)
        for i in range(len(ds)):
            x, y = ds[i]
            x = x.numpy()
            if x.shape[0] == 1:                       # rare greyscale image
                x = np.repeat(x, 3, axis=0)
            imgs.append(x.astype(np.uint8))
            labels.append(int(y))
    images = np.stack(imgs, axis=0)
    labels = np.asarray(labels, dtype=np.int64)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache, images=images, labels=labels)
    return images, labels


def load_imagenette_pool(cfg: dict, train_seed: int, download: bool = False,
                         img_size: int = None, patch_grid=None) -> dict:
    spec = next((d for d in (cfg or {}).get("datasets_v3", []) if d.get("name") == "image:imagenette"), {})
    img_size = int(img_size or spec.get("img_size", 224))
    patch_grid = tuple(patch_grid or spec.get("patch_grid", (7, 7)))
    assert img_size % patch_grid[0] == 0 and img_size % patch_grid[1] == 0, "patch grid must tile the image"
    paths = load_paths()
    images, labels = _imagenette_arrays(str(paths.data_root), img_size, download)
    n_total = images.shape[0]
    train_frac, probe_frac, probe_seed = _protocol(cfg)
    train_idx, heldout_idx = fixed_train_heldout(n_total, train_frac, train_seed)
    probe_pos, eval_pos = probe_eval_split(np.arange(heldout_idx.size), probe_frac, probe_seed)
    global_probe, global_eval = heldout_idx[probe_pos], heldout_idx[eval_pos]
    assert_disjoint(train=train_idx, probe=global_probe, eval=global_eval)
    P = int(patch_grid[0] * patch_grid[1])
    return {
        "train": (images[train_idx], labels[train_idx]),
        "heldout": (images[heldout_idx], labels[heldout_idx]),
        "heldout_index": heldout_idx, "probe_pos": probe_pos, "eval_pos": eval_pos,
        "feature_costs_by_scheme": {"uniform": np.ones(P, dtype=float)},
        "feature_groups": None, "n_classes": 10, "n_patches": P, "patch_grid": patch_grid,
        "img_size": img_size, "name": "image:imagenette", "train_seed": int(train_seed),
        "split_digest": {"train": split_digest(train_idx), "probe": split_digest(global_probe),
                         "eval": split_digest(global_eval)},
    }


# --------------------------------------------------------------------------- #
# Dispatcher
# --------------------------------------------------------------------------- #
def load_pool_v3(dataset: str, cfg: dict, train_seed: int, download: bool = False) -> dict:
    kind = dataset_kind(dataset)
    if kind == "image_patches":
        return load_image_patch_pool(dataset, cfg, train_seed, download)
    if kind == "image_rgb":
        assert dataset == "image:imagenette", f"unsupported RGB dataset {dataset!r}"
        return load_imagenette_pool(cfg, train_seed, download)
    if kind == "tabular_openml":
        from .data import load_tabular_pool
        return load_tabular_pool(dataset.split(":", 1)[1], cfg, train_seed=train_seed, download=download)
    if kind == "tabular_csv":
        return load_csv_tabular_pool(dataset.split(":", 1)[1], cfg, train_seed)
    if kind == "synthetic_cube":
        return load_cube_pool(cfg, train_seed)
    raise ValueError(kind)
