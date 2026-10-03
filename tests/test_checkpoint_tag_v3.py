"""v3 round 3 (Task L) -- the checkpoint tag of the FashionMNIST predictor-upgrade repair.

* drive_v3 helpers: ``--checkpoint-tag TAG`` changes only the checkpoint folder (``checkpoints_v3_TAG``) and the cache
  token suffix (``{policy}-TAG``); untagged paths are the round-2 ones; tags are letters, digits, underscore; an
  explicitly EMPTY tag is a usage error in every parser (drive_v3, train_backbone_v3, run_pool_rollout_v3,
  run_repairs_v3), never a silent "untagged";
* train_backbone_v3: ``--width-mult`` / ``--p-full`` overrides (image_patches only) in the recorded training cfg, the
  config cfg unchanged without them; the overrides without ``--checkpoint-tag`` are a usage error (the protocol
  checkpoint is untouched), ``--epochs`` alone still retrains the protocol backbone; a tiny CPU run writes the tagged
  checkpoint, and the tagged rollout reads it
  and writes the tagged cache with ``checkpoint_tag`` / ``checkpoint_dir`` in its meta (synthetic pool, tmp roots);
* commit_v3.find_policy_caches skips tagged caches, and commit() commits the same JSON with or without them;
* check_caches_v3 checks a tagged greedy / random pair as its own group;
* drive_v3 --dry-run --checkpoint-tag shows the tagged paths and passes the flag; commit / sweep reject it;
* run_repairs_v3 --repair-tag lists exactly the two tagged predictor-upgrade jobs.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_caches_v3  # noqa: E402
import commit_v3  # noqa: E402
import drive_v3  # noqa: E402
import make_synthetic_pool_cache  # noqa: E402
import run_repairs_v3  # noqa: E402
from cafa import config  # noqa: E402
from cafa.pool import load_pool_cache, save_pool_cache  # noqa: E402

CFG_PATH = str(REPO / "configs" / "experiment_v3.yaml")
VOLATILE = {"/created", "/pool_dir", "/cache_meta/created"}
OVERRIDES = "--epochs 60 --width-mult 4 --p-full 0.3"


def _roots(monkeypatch, tmp_path):
    monkeypatch.setenv("RESULTS_ROOT", str(tmp_path / "rr"))
    monkeypatch.setenv("DATA_ROOT", str(tmp_path / "dr"))
    monkeypatch.chdir(REPO)                       # drive_v3 / run_repairs_v3 chdir to the repo; restored afterwards
    return tmp_path / "rr"


# --------------------------------------------------------------------------- #
# helper rules
# --------------------------------------------------------------------------- #
def test_tag_helpers():
    assert drive_v3.validate_checkpoint_tag(None) is None and drive_v3.validate_checkpoint_tag("") is None
    for ok in ("repair", "r3_L", "W4", "0"):
        assert drive_v3.validate_checkpoint_tag(ok) == ok
    for bad in ("re-pair", "a b", "a/b", "..", "x.y", "r" + chr(233) + "pair", "repair\n"):
        with pytest.raises(ValueError, match="letters, digits and underscore"):
            drive_v3.validate_checkpoint_tag(bad)
        with pytest.raises(argparse.ArgumentTypeError):
            drive_v3.checkpoint_tag_arg(bad)
    # the argparse type rejects an explicit empty tag; only an omitted flag means untagged
    assert drive_v3.checkpoint_tag_arg("repair") == "repair"
    with pytest.raises(argparse.ArgumentTypeError, match="empty tag: omit the flag for the untagged protocol paths"):
        drive_v3.checkpoint_tag_arg("")
    rr = Path("R")
    assert drive_v3.checkpoint_dir_name() == "checkpoints_v3" and drive_v3.checkpoint_dir_name("repair") == "checkpoints_v3_repair"
    assert drive_v3.checkpoint_path(rr, "fashionmnist", 0) == rr / "checkpoints_v3" / "fashionmnist_ts0.pt"
    assert drive_v3.checkpoint_path(rr, "fashionmnist", 0, "repair") == rr / "checkpoints_v3_repair" / "fashionmnist_ts0.pt"
    assert drive_v3.pool_cache_path(rr, "fashionmnist", 0, "greedy_entropy") == rr / "pool_v3" / "fashionmnist_ts0_greedy_entropy_softmax.npz"
    assert (drive_v3.pool_cache_path(rr, "fashionmnist", 0, "greedy_entropy", "softmax", "repair").name
            == "fashionmnist_ts0_greedy_entropy-repair_softmax.npz")
    assert drive_v3.tagged_policy_token("random", "repair") == "random-repair"
    assert drive_v3.split_policy_token("random-repair") == ("random", "repair")
    # every untagged token of the campaign (v2 and v3 caches, external orders) is free of the tag separator
    for tok in ("greedy_entropy", "random", "eps_greedy_eps0.25", "eps_greedy_eps0.5", "afabench_gdfs", "afabench_aaco"):
        assert drive_v3.tagged_policy_token(tok) == tok and drive_v3.split_policy_token(tok) == (tok, None)


# --------------------------------------------------------------------------- #
# train_backbone_v3 / run_pool_rollout_v3 arguments
# --------------------------------------------------------------------------- #
def test_train_backbone_overrides_and_parser(capsys):
    pytest.importorskip("torch")
    import train_backbone_v3 as tb
    cfg = config.load_experiment(CFG_PATH)
    base = cfg["training_v3"]["image_patches"]
    a = tb.build_parser().parse_args(["--dataset", "fashionmnist"])
    assert (a.checkpoint_tag, a.width_mult, a.p_full, a.epochs) == (None, None, None, None)
    # no override -> exactly the config dict (same keys, order and values as before round 3)
    assert list(tb.training_cfg(cfg, "image_patches").items()) == list(base.items())
    a = tb.build_parser().parse_args(["--dataset", "fashionmnist", "--checkpoint-tag", "repair"] + OVERRIDES.split())
    assert a.checkpoint_tag == "repair"
    t = tb.training_cfg(cfg, "image_patches", a.epochs, a.width_mult, a.p_full)
    assert t == dict(base, epochs=60, width_mult=4, p_full=0.3) and list(t) == list(base)
    assert tb.training_cfg(cfg, "tabular_csv", epochs=7) == dict(cfg["training_v3"]["tabular"], epochs=7)
    for kind, kw in (("tabular_csv", {"width_mult": 4}), ("image_rgb", {"p_full": 0.3}), ("synthetic_cube", {"width_mult": 1})):
        with pytest.raises(ValueError, match="image_patches"):
            tb.training_cfg(cfg, kind, **kw)
    with pytest.raises(ValueError, match=">= 1"):
        tb.training_cfg(cfg, "image_patches", width_mult=0)
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        tb.training_cfg(cfg, "image_patches", p_full=1.5)
    # main: a usage error before any data or root is touched (untagged override first, then the kind check)
    capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        tb.main(["--dataset", "csv:physionet", "--width-mult", "4", "--config", CFG_PATH])
    assert e.value.code == 2 and "give --checkpoint-tag" in capsys.readouterr().err
    with pytest.raises(SystemExit) as e:
        tb.main(["--dataset", "csv:physionet", "--checkpoint-tag", "repair", "--width-mult", "4", "--config", CFG_PATH])
    assert e.value.code == 2 and "image_patches" in capsys.readouterr().err
    with pytest.raises(SystemExit) as e:
        tb.build_parser().parse_args(["--dataset", "fashionmnist", "--checkpoint-tag", "re-pair"])
    assert e.value.code == 2
    for empty in (["--checkpoint-tag", ""], ["--checkpoint-tag="]):
        with pytest.raises(SystemExit) as e:
            tb.build_parser().parse_args(["--dataset", "fashionmnist"] + empty)
        assert e.value.code == 2 and "empty tag" in capsys.readouterr().err


def test_rollout_parser(capsys):
    pytest.importorskip("torch")
    import run_pool_rollout_v3 as rp
    assert rp.build_parser().parse_args(["--dataset", "fashionmnist"]).checkpoint_tag is None
    assert rp.build_parser().parse_args(["--dataset", "fashionmnist", "--checkpoint-tag", "repair"]).checkpoint_tag == "repair"
    with pytest.raises(SystemExit):
        rp.build_parser().parse_args(["--dataset", "fashionmnist", "--checkpoint-tag", "a/b"])
    capsys.readouterr()
    for empty in (["--checkpoint-tag", ""], ["--checkpoint-tag="]):
        with pytest.raises(SystemExit) as e:
            rp.build_parser().parse_args(["--dataset", "fashionmnist"] + empty)
        assert e.value.code == 2 and "empty tag" in capsys.readouterr().err


def test_train_backbone_overrides_need_tag(monkeypatch, tmp_path, capsys):
    """--width-mult / --p-full without --checkpoint-tag (or with an empty one) never touch checkpoints_v3/: a usage
    error before any data is loaded.  --epochs alone is the protocol retrain override (CUBE / MiniBooNE) and still
    writes checkpoints_v3/ (tiny CPU run, tmp root)."""
    torch = pytest.importorskip("torch")
    import train_backbone_v3 as tb
    rr = _roots(monkeypatch, tmp_path)
    protocol = rr / "checkpoints_v3" / "fashionmnist_ts0.pt"
    protocol.parent.mkdir(parents=True)
    protocol.write_bytes(b"protocol backbone")
    loads = []
    pool = _tiny_patch_pool()
    monkeypatch.setattr(tb, "load_pool_v3", lambda *a, **k: loads.append(a) or pool)
    common = ["--dataset", "fashionmnist", "--train-seed", "0", "--device", "cpu", "--config", CFG_PATH]
    capsys.readouterr()
    no_tag = ("--width-mult/--p-full change the protocol backbone; give --checkpoint-tag so it is written to "
              "checkpoints_v3_<tag>/")
    for extra, msg in ((["--width-mult", "4"], no_tag),
                       (["--p-full", "0.3"], no_tag),
                       (OVERRIDES.split(), no_tag),
                       # the review's reproduction: an empty tag (unset shell variable) plus the overrides
                       (["--checkpoint-tag", "", "--width-mult", "1", "--p-full", "0.3", "--epochs", "1"],
                        "argument --checkpoint-tag: empty tag: omit the flag for the untagged protocol paths")):
        with pytest.raises(SystemExit) as e:
            tb.main(common + extra)
        err = capsys.readouterr().err
        assert e.value.code == 2 and msg in err, (extra, err)
    assert loads == [] and protocol.read_bytes() == b"protocol backbone"
    assert sorted(p.name for p in rr.iterdir()) == ["checkpoints_v3"]
    # --epochs alone: the documented protocol retrain, untagged, config width / p_full
    assert tb.main(common + ["--epochs", "1", "--max-train", "16"]) == 0
    assert len(loads) == 1 and sorted(p.name for p in rr.glob("checkpoints_v3*")) == ["checkpoints_v3"]
    assert sorted(p.name for p in protocol.parent.iterdir()) == [protocol.name]
    meta = torch.load(protocol, map_location="cpu", weights_only=False)["meta"]
    base = config.load_experiment(CFG_PATH)["training_v3"]["image_patches"]
    assert "checkpoint_tag" not in meta and meta["training"] == dict(base, epochs=1)
    assert meta["arch"]["width_mult"] == int(base.get("width_mult", 2))


def _tiny_patch_pool(n_train=64, n_held=12, seed=0):
    rng = np.random.default_rng(seed)
    X = lambda n: rng.random((n, 49, 16), dtype=np.float32)  # noqa: E731   (7 x 7 patches of 4 x 4 pixels)
    return {"train": (X(n_train), rng.integers(0, 10, n_train)), "heldout": (X(n_held), rng.integers(0, 10, n_held)),
            "heldout_index": np.arange(1000, 1000 + n_held), "n_classes": 10, "n_patches": 49,
            "split_digest": {"train": "t", "probe": "p", "eval": "e"},
            "feature_costs_by_scheme": {"uniform": [1.0] * 49}}


def test_tagged_backbone_and_rollout_tiny_cpu(monkeypatch, tmp_path):
    torch = pytest.importorskip("torch")
    import run_pool_rollout_v3 as rp
    import train_backbone_v3 as tb
    from cafa.repro_utils import file_sha256
    rr = _roots(monkeypatch, tmp_path)
    pool = _tiny_patch_pool()
    monkeypatch.setattr(tb, "load_pool_v3", lambda *a, **k: pool)
    monkeypatch.setattr(rp, "load_pool_v3", lambda *a, **k: pool)
    common = ["--dataset", "fashionmnist", "--train-seed", "0", "--device", "cpu", "--config", CFG_PATH]
    # width 1 (config: 2) keeps the CPU run short and shows that the override reaches the model and the meta
    assert tb.main(common + ["--checkpoint-tag", "repair", "--epochs", "1", "--width-mult", "1", "--p-full", "0.3"]) == 0
    ckpt = rr / "checkpoints_v3_repair" / "fashionmnist_ts0.pt"
    assert ckpt.exists() and not (rr / "checkpoints_v3" / "fashionmnist_ts0.pt").exists()
    meta = torch.load(ckpt, map_location="cpu", weights_only=False)["meta"]
    assert meta["checkpoint_tag"] == "repair" and meta["arch"]["width_mult"] == 1
    assert meta["training"]["width_mult"] == 1 and meta["training"]["p_full"] == 0.3 and meta["training"]["epochs"] == 1

    with pytest.raises(FileNotFoundError, match=r"checkpoints_v3[\\/]fashionmnist_ts0\.pt"):  # untagged: protocol path
        rp.main(common + ["--policy", "random"])
    assert rp.main(common + ["--policy", "random", "--checkpoint-tag", "repair"]) == 0
    out = rr / "pool_v3" / "fashionmnist_ts0_random-repair_softmax.npz"
    assert sorted(p.name for p in (rr / "pool_v3").iterdir()) == [out.name]
    c = load_pool_cache(out)
    assert c["meta"]["checkpoint_tag"] == "repair" and c["meta"]["checkpoint_dir"] == "checkpoints_v3_repair"
    assert c["meta"]["policy"] == "random" and c["meta"]["checkpoint"] == "fashionmnist_ts0.pt"
    assert c["meta"]["checkpoint_sha256"] == file_sha256(ckpt) and c["scores"].shape == (12, 50)


# --------------------------------------------------------------------------- #
# commit_v3 / check_caches_v3 on synthetic caches
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    root = tmp_path_factory.mktemp("ckpt_tag")
    pool = root / "pool_v3"
    assert make_synthetic_pool_cache.main(["--pool-dir", str(pool), "--n", "3000", "--scenario", "typeII"]) == 0
    return {"root": root, "pool": pool, "cfg": config.load_experiment(CFG_PATH)}


def test_commit_ignores_tagged_caches(synth, capsys):
    pool, cfg, root = synth["pool"], synth["cfg"], synth["root"]
    a, b = root / "committed_untagged.json", root / "committed_with_tagged.json"
    assert commit_v3.commit(dataset="synthetic-planted", train_seed=0, score="softmax", pool_dir=pool,
                            out_path=a, cfg=cfg, force=True) == 0
    with_tag = root / "pool_with_tagged"
    shutil.copytree(pool, with_tag)
    for pol in ("greedy_entropy", "random"):
        shutil.copy(pool / f"synthetic-planted_ts0_{pol}_softmax.npz", with_tag / f"synthetic-planted_ts0_{pol}-repair_softmax.npz")
    capsys.readouterr()
    found = commit_v3.find_policy_caches(with_tag, "synthetic-planted", 0, "softmax")
    assert sorted(found) == ["greedy_entropy", "random"]
    notes = [l for l in capsys.readouterr().out.splitlines() if "ignoring tagged cache" in l]
    assert len(notes) == 2 and all("'repair'" in l for l in notes)
    assert commit_v3.commit(dataset="synthetic-planted", train_seed=0, score="softmax", pool_dir=with_tag,
                            out_path=b, cfg=cfg, force=True) == 0
    ca, cb = json.loads(a.read_text()), json.loads(b.read_text())
    assert sorted(cb["lambda_refs"]) == sorted(ca["lambda_refs"]) == ["greedy_entropy", "random"]
    assert [d for d in commit_v3.diff_commits(ca, cb) if d not in VOLATILE] == []


def _write(path, src, **meta):
    save_pool_cache(path, scores=src["scores"], correct=src["correct"], order=src["order"], y=src["y"],
                    row_pos=src["row_pos"], meta=dict(src["meta"], **meta))


@pytest.fixture()
def check_dir(synth, tmp_path):
    """Untagged pair = one synthetic population (greedy = random by construction); tagged pair = the other one
    (a different full-acquisition accuracy), so mixing the two groups would fail."""
    d = tmp_path / "pool_v3"
    d.mkdir()
    g = load_pool_cache(synth["pool"] / "synthetic-planted_ts0_greedy_entropy_softmax.npz")
    r = load_pool_cache(synth["pool"] / "synthetic-planted_ts0_random_softmax.npz")
    assert abs(np.mean(g["correct"][:, -1]) - np.mean(r["correct"][:, -1])) > 1e-6
    for pol in ("greedy_entropy", "random"):
        _write(d / f"synthetic-planted_ts0_{pol}_softmax.npz", g)
        _write(d / f"synthetic-planted_ts0_{pol}-repair_softmax.npz", r, checkpoint_tag="repair",
               checkpoint_dir="checkpoints_v3_repair")
    return d, g, r


def test_check_caches_groups_tagged_pair(check_dir, tmp_path, capsys):
    d, g, _ = check_dir
    v2 = tmp_path / "pool_v2"
    v2.mkdir()
    _write(v2 / "synthetic-planted_ts0_greedy_entropy_softmax.npz", g)
    out_csv = tmp_path / "caches.csv"
    assert check_caches_v3.main(["--pool-dir", str(d), "--v2-dir", str(v2), "--csv", str(out_csv)]) == 0
    out = capsys.readouterr().out
    pairs = [l for l in out.splitlines() if "greedy vs random" in l]
    assert len(pairs) == 2 and all(l.endswith("-> PASS") for l in pairs)
    assert pairs[0].startswith("[check_v3] synthetic-planted ts0: ") and "ts0 [repair]: " in pairs[1]
    assert sum("v2 vs v3" in l for l in out.splitlines()) == 1                  # the untagged greedy cache only
    pols = [l.split(",")[2] for l in out_csv.read_text().splitlines()[1:]]
    assert sorted(pols) == ["greedy_entropy", "greedy_entropy-repair", "random", "random-repair"]


def test_check_caches_tagged_pair_fails_alone(check_dir, capsys):
    d, g, r = check_dir
    _write(d / "synthetic-planted_ts0_random-repair_softmax.npz", g, checkpoint_tag="repair")   # != tagged greedy
    assert check_caches_v3.main(["--pool-dir", str(d)]) == 1
    pairs = [l for l in capsys.readouterr().out.splitlines() if "greedy vs random" in l]
    assert pairs[0].endswith("-> PASS") and "[repair]" in pairs[1] and pairs[1].endswith("-> FAIL")
    _write(d / "synthetic-planted_ts0_random-repair_softmax.npz", r)                              # meta lacks the tag
    assert check_caches_v3.main(["--pool-dir", str(d)]) == 1
    assert "does not match the file name -> FAIL" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# drive_v3 / run_repairs_v3 (dry runs, tmp roots)
# --------------------------------------------------------------------------- #
def test_drive_paths_for_untagged_unchanged(tmp_path):
    rr = tmp_path
    out, pre = drive_v3.paths_for("rollouts", "fashionmnist", "random", 0, rr)
    assert out == rr / "pool_v3" / "fashionmnist_ts0_random_softmax.npz" and pre == [rr / "checkpoints_v3" / "fashionmnist_ts0.pt"]
    out, pre = drive_v3.paths_for("rollouts", "fashionmnist", "random", 0, rr, checkpoint_tag="repair")
    assert out == rr / "pool_v3" / "fashionmnist_ts0_random-repair_softmax.npz"
    assert pre == [rr / "checkpoints_v3_repair" / "fashionmnist_ts0.pt"]
    assert drive_v3.paths_for("backbones", "fashionmnist", None, 0, rr, checkpoint_tag="repair")[0] == \
        rr / "checkpoints_v3_repair" / "fashionmnist_ts0.pt"


def test_drive_dry_run_checkpoint_tag(monkeypatch, tmp_path, capsys):
    rr = _roots(monkeypatch, tmp_path)
    (rr / "checkpoints_v3").mkdir(parents=True)
    (rr / "checkpoints_v3" / "fashionmnist_ts0.pt").write_bytes(b"")          # the protocol backbone exists
    base = ["--seeds", "0", "--datasets", "fashionmnist", "--dry-run"]
    assert drive_v3.main(["--phase", "backbones"] + base) == 0
    assert "skip (exists) backbones:fashionmnist:na:ts0" in capsys.readouterr().out
    assert drive_v3.main(["--phase", "backbones", "--checkpoint-tag", "repair", f"--extra-args={OVERRIDES}"] + base) == 0
    would = [l for l in capsys.readouterr().out.splitlines() if "would run" in l]
    assert len(would) == 1 and "backbones:fashionmnist:na-repair:ts0" in would[0]
    assert "scripts/train_backbone_v3.py --dataset fashionmnist --train-seed 0 --device cuda --checkpoint-tag repair " \
           + OVERRIDES in would[0]
    assert str(rr / "checkpoints_v3_repair" / "fashionmnist_ts0.pt") in would[0]
    assert drive_v3.main(["--phase", "rollouts", "--checkpoint-tag", "repair"] + base) == 0
    would = [l for l in capsys.readouterr().out.splitlines() if "would run" in l]
    assert len(would) == 2 and all("--checkpoint-tag repair" in l for l in would)
    assert all("[prerequisite missing now: checkpoints_v3_repair/fashionmnist_ts0.pt]" in l for l in would)
    assert {p for l in would for p in ("greedy_entropy-repair_softmax.npz", "random-repair_softmax.npz") if p in l} == \
        {"greedy_entropy-repair_softmax.npz", "random-repair_softmax.npz"}
    for phase in ("commit", "sweep"):                                            # rejected, not ignored
        with pytest.raises(SystemExit) as e:
            drive_v3.main(["--phase", phase, "--checkpoint-tag", "repair"] + base)
        assert e.value.code == 2
    with pytest.raises(SystemExit):
        drive_v3.main(["--phase", "backbones", "--checkpoint-tag", "re-pair"] + base)


def test_run_repairs_repair_tag_dry_run(monkeypatch, tmp_path, capsys):
    rr = _roots(monkeypatch, tmp_path)
    (rr / "pool_v3").mkdir(parents=True)
    for tok in ("greedy_entropy", "random", "greedy_entropy-repair", "random-repair"):
        (rr / "pool_v3" / f"fashionmnist_ts0_{tok}_softmax.npz").write_bytes(b"")
    for tok in ("greedy_entropy", "random"):                                    # mnist: no tagged caches
        (rr / "pool_v3" / f"mnist_ts0_{tok}_softmax.npz").write_bytes(b"")
    assert (REPO / "configs" / "committed_v3_fashionmnist_ts0.json").exists()
    # --force: list the jobs even after the real repair JSONs exist
    assert run_repairs_v3.main(["--seeds", "0", "--datasets", "fashionmnist", "mnist", "--repair-tag", "repair",
                                "--tag", "r3L", "--dry-run", "--force"]) == 0
    out = capsys.readouterr().out.splitlines()
    would = [l for l in out if "would run" in l]
    assert len(would) == 2
    pool = str(rr / "pool_v3").replace("\\", "/")
    for line, pol, label in zip(would, ("greedy_entropy", "random"), ("predictor_upgrade", "predictor_upgrade_random")):
        assert f"r3L:repair:fashionmnist:{label}:ts0" in line
        assert (f"--before-cache {pool}/fashionmnist_ts0_{pol}_softmax.npz "
                f"--after-cache {pool}/fashionmnist_ts0_{pol}-repair_softmax.npz "
                f"--committed configs/committed_v3_fashionmnist_ts0.json --policy {pol} --label {label}") in line
    skips = [l for l in out if "skip (missing prerequisite)" in l]
    assert len(skips) == 2 and all("repair:mnist:predictor_upgrade" in l and "-repair_softmax.npz" in l for l in skips)
    # without --repair-tag the job list is the round-2 one
    labels = [(ds, lab) for ds, _, lab, _ in run_repairs_v3.jobs([0], ["fashionmnist", "mnist"],
                                                                 ["predictor_upgrade", "policy_change"], rr)]
    assert labels == [("fashionmnist", "policy_change"), ("mnist", "predictor_upgrade"), ("mnist", "policy_change")]


def test_empty_tag_is_a_usage_error(monkeypatch, tmp_path, capsys):
    """An explicit empty ``--checkpoint-tag`` / ``--repair-tag`` (e.g. an unset shell variable) is a usage error, never
    the untagged protocol paths (drive_v3) nor the round-2 job list (run_repairs_v3, which would overwrite
    results_v3/repair/fashionmnist_ts0_policy_change.json)."""
    rr = _roots(monkeypatch, tmp_path)
    (rr / "pool_v3").mkdir(parents=True)
    for tok in ("greedy_entropy", "random"):
        (rr / "pool_v3" / f"fashionmnist_ts0_{tok}_softmax.npz").write_bytes(b"")
    msg = "empty tag: omit the flag for the untagged protocol paths"
    base = ["--seeds", "0", "--datasets", "fashionmnist", "--dry-run"]
    capsys.readouterr()
    for phase in ("backbones", "rollouts"):
        for empty in (["--checkpoint-tag", ""], ["--checkpoint-tag="]):
            with pytest.raises(SystemExit) as e:
                drive_v3.main(["--phase", phase] + empty + base)
            out = capsys.readouterr()
            assert e.value.code == 2 and f"argument --checkpoint-tag: {msg}" in out.err and "[drive_v3]" not in out.out
    for empty in (["--repair-tag", ""], ["--repair-tag="]):
        with pytest.raises(SystemExit) as e:
            run_repairs_v3.main(base + ["--force"] + empty)
        out = capsys.readouterr()
        assert e.value.code == 2 and f"argument --repair-tag: {msg}" in out.err and "[repairs]" not in out.out
    # the same call without the flag is the round-2 policy_change job (proves the error is not a missing prerequisite)
    assert run_repairs_v3.main(base + ["--force"]) == 0
    assert "would run repair:fashionmnist:policy_change:ts0" in capsys.readouterr().out
