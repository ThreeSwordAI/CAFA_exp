"""v3 round 2 (Task F) -- cluster package and the two latent fixes.

* make_tables_v3.seed_summary: mean +- sample sd over seeds per (dataset, policy) (TABLE_E4_cascade_seeds);
* run_pool_rollout_v3 --orders-file passes the pool's heldout digest to load_orders, so an orders file exported
  from another split is refused (was heldout_digest=None);
* export_heldout_v3 writes under ${RESULTS_ROOT}/orders_v3 by default (feature arrays never land in the repo);
* drive_v3 --dry-run prints the command of a cell whose prerequisite is missing (cluster dry run of seeds 1-2);
* hpc/dry_run_v3.sh runs the real batch scripts for all 24 + 48 array indices; with empty roots every task
  would run, with the documented flags.

Round 3 (Task L): the two README lines of the FashionMNIST predictor upgrade (backbone task 6 with
CAFA_EXTRA="--epochs 60 --width-mult 4 --p-full 0.3", rollout lines 12 / 13, both with the driver flag
--checkpoint-tag repair) dry-run through the same batch scripts (BB_EXTRA / DRY_DRIVER_FLAGS of dry_run_v3.sh).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import drive_v3  # noqa: E402
import export_heldout_v3  # noqa: E402
import make_tables_v3  # noqa: E402


def test_seed_summary_mean_sd():
    rows = [{"dataset": "d", "policy": "p", "seed": s, "tier1": t, "certified_violation": c}
            for s, t, c in ((0, 0.2, 0.0), (1, 0.4, 0.01), (2, 0.9, None))]
    rows.append({"dataset": "e", "policy": "p", "seed": 0, "tier1": 1.0, "certified_violation": 0.0})
    md, cs = make_tables_v3.seed_summary(rows)
    d = next(r for r in cs if r["dataset"] == "d")
    assert d["n_seeds"] == 3 and d["seeds"] == "0 1 2"
    assert d["tier1_mean"] == pytest.approx(0.5) and d["tier1_sd"] == pytest.approx(np.std([0.2, 0.4, 0.9], ddof=1))
    assert d["certified_violation_mean"] == pytest.approx(0.005)                  # None ignored ...
    assert next(r for r in md if r["dataset"] == "d")["certified_violation"].endswith("(n=2)")   # ... and flagged
    e = next(r for r in cs if r["dataset"] == "e")
    assert e["tier1_sd"] is None and next(r for r in md if r["dataset"] == "e")["tier1"] == "1.000"


def test_export_heldout_default_out(monkeypatch, tmp_path):
    monkeypatch.setenv("RESULTS_ROOT", str(tmp_path / "rr"))
    monkeypatch.setenv("DATA_ROOT", str(tmp_path / "dr"))
    assert export_heldout_v3.default_out("csv:physionet", 0) == tmp_path / "rr" / "orders_v3" / "csv-physionet_ts0_heldout.npz"
    assert export_heldout_v3.default_out("tabular:adult", 2).name == "tabular-adult_ts2_heldout.npz"


def test_rollout_orders_file_checks_heldout_digest(monkeypatch, tmp_path):
    pytest.importorskip("torch")
    import run_pool_rollout_v3 as rp
    from cafa.external_orders import save_orders
    from cafa.splits import split_digest
    n, d = 40, 5
    rng = np.random.default_rng(0)
    pool = {"heldout": (rng.normal(size=(n, d)).astype(np.float32), rng.integers(0, 2, n)),
            "train": (rng.normal(size=(10, d)).astype(np.float32), rng.integers(0, 2, 10)),
            "heldout_index": np.arange(100, 100 + n), "n_features": d, "n_classes": 2,
            "split_digest": {"train": "t", "probe": "p", "eval": "e"}}
    monkeypatch.setenv("RESULTS_ROOT", str(tmp_path))
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    (tmp_path / "checkpoints_v3").mkdir()
    (tmp_path / "checkpoints_v3" / "csv-physionet_ts0.pt").write_bytes(b"")
    monkeypatch.setattr(rp, "load_pool_v3", lambda *a, **k: pool)
    monkeypatch.setattr(rp, "load_backbone", lambda *a, **k: (None, {}))

    class Reached(Exception):
        pass

    def stop(*a, **k):
        raise Reached
    monkeypatch.setattr(rp, "rollout_replay", stop)
    orders = np.stack([rng.permutation(d) for _ in range(n)])
    wrong, right = tmp_path / "wrong.npz", tmp_path / "right.npz"
    save_orders(wrong, orders, policy="x", dataset="csv:physionet", heldout_digest=split_digest(np.arange(n)))
    save_orders(right, orders, policy="x", dataset="csv:physionet", heldout_digest=split_digest(pool["heldout_index"]))
    args = ["--dataset", "csv:physionet", "--train-seed", "0", "--device", "cpu", "--policy-token", "x",
            "--config", str(REPO / "configs" / "experiment_v3.yaml")]
    with pytest.raises(ValueError, match="heldout_digest"):
        rp.main(args + ["--orders-file", str(wrong)])
    with pytest.raises(Reached):                                                  # the right file passes the check
        rp.main(args + ["--orders-file", str(right)])


def test_driver_dry_run_prints_cells_with_missing_prerequisites(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("RESULTS_ROOT", str(tmp_path))
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    assert drive_v3.main(["--phase", "rollouts", "--seeds", "1", "--datasets", "image:imagenette", "--dry-run",
                          "--extra-args=--batch-size 32 --policy-amp"]) == 0
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "would run" in l]
    assert len(lines) == 2 and all("--batch-size 32 --policy-amp" in l and "prerequisite missing now" in l for l in lines)


# resolve bash via PATH (on Windows a bare "bash" in subprocess finds the WSL launcher in System32 first)
BASH = shutil.which("bash")


@pytest.mark.skipif(BASH is None or "system32" in BASH.lower(), reason="no POSIX bash on PATH")
def test_hpc_dry_run_all_array_indices(tmp_path):
    # representative indices (the full 24 + 48 run is results_v3/logs/hpc_dry_run.log): seed-0 / ts1 / ts2 backbones
    # incl. the --epochs 60 tasks, every Imagenette rollout, and plain rollouts of each seed
    env = dict(os.environ, DATA_ROOT=str(tmp_path / "d"), RESULTS_ROOT=str(tmp_path / "r"), PYTHON=sys.executable,
               BB_INDICES="1 9 12 15 17 20 23", RO_INDICES="0 14 15 16 29 30 31 32 45 46 47")
    out = subprocess.run([BASH, str(REPO / "hpc" / "dry_run_v3.sh")], capture_output=True, text=True, env=env,
                         cwd=REPO, timeout=900).stdout
    would = [l for l in out.splitlines() if "would run" in l]
    assert "# array tasks without driver output: 0" in out
    assert len(would) == 7 + 11                                                   # empty roots: every task would run
    bb = [l for l in would if "train_backbone_v3.py" in l]
    assert sum("--epochs 60" in l for l in bb) == 4                               # cube / MiniBooNE ts1, ts2 (9 12 17 20)
    assert [l for l in bb if "--dataset cube --train-seed 0" in l and "--epochs" not in l]   # seed 0 (local) untouched
    ro = [l for l in would if "run_pool_rollout_v3.py" in l and "image:imagenette" in l]
    assert len(ro) == 6 and all("--batch-size 32" in l for l in ro)
    assert sum("--policy-amp" in l for l in ro) == 3 and all(("--policy-amp" in l) == ("greedy_entropy" in l) for l in ro)
    assert not [l for l in would if "run_pool_rollout_v3.py" in l and "image:imagenette" not in l and "--batch-size" in l]


@pytest.mark.skipif(BASH is None or "system32" in BASH.lower(), reason="no POSIX bash on PATH")
def test_hpc_dry_run_task_l_lines(tmp_path):
    # hpc/README_v3.md section 8: the flags reach the driver through CAFA_EXTRA / CAFA_DRIVER_FLAGS of the real scripts
    env = dict(os.environ, DATA_ROOT=str(tmp_path / "d"), RESULTS_ROOT=str(tmp_path / "r"), PYTHON=sys.executable,
               BB_INDICES="6", RO_INDICES="12 13", BB_EXTRA="--epochs 60 --width-mult 4 --p-full 0.3",
               DRY_DRIVER_FLAGS="--checkpoint-tag repair")
    out = subprocess.run([BASH, str(REPO / "hpc" / "dry_run_v3.sh")], capture_output=True, text=True, env=env,
                         cwd=REPO, timeout=300).stdout
    would = [l for l in out.splitlines() if "would run" in l]
    assert "# array tasks without driver output: 0" in out and len(would) == 3
    bb, ro = would[0], would[1:]
    assert "backbones:fashionmnist:na-repair:ts0" in bb
    assert ("scripts/train_backbone_v3.py --dataset fashionmnist --train-seed 0 --device cuda --checkpoint-tag repair "
            "--epochs 60 --width-mult 4 --p-full 0.3") in bb
    assert "checkpoints_v3_repair" in bb and bb.rstrip().endswith("fashionmnist_ts0.pt]")      # the tagged output path
    for line, pol in zip(ro, ("greedy_entropy", "random")):
        assert f"rollouts:fashionmnist:{pol}-repair:ts0" in line
        assert f"--dataset fashionmnist --train-seed 0 --policy {pol} --device cuda --checkpoint-tag repair" in line
        assert "[prerequisite missing now: checkpoints_v3_repair/fashionmnist_ts0.pt]" in line
        assert f"fashionmnist_ts0_{pol}-repair_softmax.npz" in line and "--epochs" not in line
