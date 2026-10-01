#!/usr/bin/env python
"""v3 -- one-time data fetch for the AISTATS suite (run once, login node / laptop).

    python scripts/download_data_v3.py --all
    python scripts/download_data_v3.py --mnist --fashionmnist --csv          # small (~130 MB)
    python scripts/download_data_v3.py --imagenette                           # ~330 MB archive + cache
    python scripts/download_data_v3.py --openml                               # MiniBooNE (+ adult) via sklearn

Everything lands under ``${DATA_ROOT}``:
  MNIST/ FashionMNIST/           torchvision archives
  imagenette2-320/ + imagenette_cache/imagenette_224.npz   (built on first load)
  afabench/physionet.csv, afabench/diabetes.csv   (AFABench CSVs, MIT licence,
      from github.com/Linusaronsson/AFA-Benchmark, extra/data/misc/)
  OpenML cache (sklearn)         MiniBooNE / adult
CUBE is generated on the fly (seeded) and needs no download.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa import config  # noqa: E402

_AFABENCH_RAW = "https://raw.githubusercontent.com/Linusaronsson/AFA-Benchmark/main/extra/data/misc/"
_CSVS = ("physionet.csv", "diabetes.csv")


def fetch_csvs(data_root: Path) -> None:
    out_dir = data_root / "afabench"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in _CSVS:
        dst = out_dir / name
        if dst.exists():
            print(f"[csv] {dst} exists; skipping")
            continue
        url = _AFABENCH_RAW + name
        print(f"[csv] fetching {url} -> {dst}", flush=True)
        urllib.request.urlretrieve(url, dst)  # noqa: S310
        print(f"[csv] {name}: {dst.stat().st_size / 1e6:.1f} MB")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true")
    p.add_argument("--mnist", action="store_true")
    p.add_argument("--fashionmnist", action="store_true")
    p.add_argument("--imagenette", action="store_true")
    p.add_argument("--csv", action="store_true")
    p.add_argument("--openml", action="store_true")
    p.add_argument("--config", default="configs/experiment_v3.yaml")
    a = p.parse_args(argv)
    paths = config.load_paths()
    cfg = config.load_experiment(a.config)
    root = Path(paths.data_root)
    root.mkdir(parents=True, exist_ok=True)

    if a.all or a.csv:
        fetch_csvs(root)
    if a.all or a.mnist:
        import torchvision
        torchvision.datasets.MNIST(str(root), train=True, download=True)
        torchvision.datasets.MNIST(str(root), train=False, download=True)
        print("[mnist] ok")
    if a.all or a.fashionmnist:
        import torchvision
        torchvision.datasets.FashionMNIST(str(root), train=True, download=True)
        torchvision.datasets.FashionMNIST(str(root), train=False, download=True)
        print("[fashionmnist] ok")
    if a.all or a.imagenette:
        from cafa.data_v3 import load_imagenette_pool
        pool = load_imagenette_pool(cfg, train_seed=0, download=True)
        print(f"[imagenette] cached {pool['train'][0].shape[0] + pool['heldout'][0].shape[0]} images "
              f"at {pool['img_size']}px")
    if a.all or a.openml:
        from cafa.data import load_tabular_pool
        for name in ("MiniBooNE", "adult"):
            pool = load_tabular_pool(name, cfg, train_seed=0, download=True)
            print(f"[openml] {name}: n_train={pool['train'][0].shape[0]} d={pool['n_features']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
