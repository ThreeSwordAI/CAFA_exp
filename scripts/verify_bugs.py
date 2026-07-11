#!/usr/bin/env python
"""WO-6 -- verification-first bug script (torch-free; runnable on a login node).

Three sections, each printing PASS/FAIL; exit code is nonzero if ANY section
fails.  The operator appends this script's output to repro/BUGLOG.md.

  1. C1 honesty probe (post-fix regression): a candidate's TRUE value never
     reaches the predictor before acquisition (mean-imputation only).
  2. C2 legacy-leak demonstration + v2 guarantee: the legacy per-seed reshuffle
     leaks ~60% of cal/test into train_0; the v2 splits have zero such overlap.
  3. Freeze check: sha256 of the frozen files vs repro/MANIFEST.sha256.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa.data import _disjoint_split_indices  # noqa: E402
from cafa.repro_utils import file_sha256  # noqa: E402
from cafa.splits import fixed_train_heldout, probe_eval_split, resplit_cal_test  # noqa: E402
from cafa.tabular import TabularGreedyEntropyPolicy  # noqa: E402

_REPO = Path(__file__).resolve().parents[1]


class _RecordingPredictor:
    """Dummy predictor that records every X it is asked to score; returns uniform probs."""

    def __init__(self):
        self.calls = []

    def predict_proba(self, X, mask, device=None):
        X = np.asarray(X, dtype=float)
        self.calls.append(X.copy())
        return np.full((X.shape[0], 2), 0.5, dtype=float)


def section_c1() -> bool:
    print("=== C1: tabular greedy honesty (mean-imputation, no clairvoyance) ===")
    X = np.array([[7.0, -3.0, 2.5]], dtype=np.float32)
    feature_groups = [np.array([0]), np.array([1]), np.array([2])]
    observed = np.zeros((1, 3), dtype=np.float32)
    means = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    pol = TabularGreedyEntropyPolicy(col_means=means)
    rec = _RecordingPredictor()
    pol.select_next(rec, X, observed, feature_groups, device="cpu")

    ok = True
    if len(rec.calls) != 3:
        print(f"  FAIL: expected 3 candidate evaluations, got {len(rec.calls)}")
        ok = False
    for a in range(min(3, len(rec.calls))):
        seen = float(rec.calls[a][0, a])
        true_val = float(X[0, a])
        print(f"  candidate col {a}: value reaching predictor = {seen} (true value = {true_val})")
        if abs(seen - 0.5) > 1e-9:
            print(f"  FAIL: candidate col {a} reached predictor as {seen}, expected mean 0.5")
            ok = False
        if abs(seen - true_val) < 1e-9:
            print(f"  FAIL: candidate col {a} leaked its TRUE value {true_val}")
            ok = False
    print(f"  C1 {'PASS' if ok else 'FAIL'}\n")
    return ok


def section_c2() -> bool:
    print("=== C2: legacy per-seed reshuffle leak vs v2 disjoint guarantee ===")
    n_total = 70_000
    fractions = {"train": 0.6, "cal": 0.2, "test": 0.2}
    train0, _, _ = _disjoint_split_indices(n_total, fractions, 0)
    train0_set = set(train0.tolist())

    print("  legacy leak (|cal_s U test_s intersect train_0| / |cal_s U test_s|):")
    ok = True
    for s in range(20):
        _, cal_s, test_s = _disjoint_split_indices(n_total, fractions, s)
        union = np.union1d(cal_s, test_s)
        overlap = sum(1 for i in union.tolist() if i in train0_set) / max(union.size, 1)
        if s in (0, 1, 2, 19):
            print(f"    seed {s:>2}: leak = {overlap:.3f}")
        if s == 0 and overlap > 1e-9:
            print(f"  FAIL: legacy seed 0 should be disjoint from train_0 (got {overlap:.3f})")
            ok = False
        if s != 0 and overlap < 0.4:
            print(f"  WARN: legacy seed {s} leak {overlap:.3f} lower than the ~0.60 expectation")

    # v2 splits: fixed train / probe / resplit; every cal/test disjoint from
    # train and probe.
    train_idx, heldout_idx = fixed_train_heldout(n_total, 0.6, 0)
    probe_pos, eval_pos = probe_eval_split(np.arange(heldout_idx.size), 0.10, 777)
    global_probe = heldout_idx[probe_pos]
    global_eval = heldout_idx[eval_pos]
    train_set = set(train_idx.tolist())
    probe_set = set(global_probe.tolist())
    for rs in (0, 1, 57, 99):
        cal_local, test_local = resplit_cal_test(np.arange(eval_pos.size), rs)
        global_cal = global_eval[cal_local]
        global_test = global_eval[test_local]
        for name, arr in (("cal", global_cal), ("test", global_test)):
            a = set(arr.tolist())
            if a & train_set:
                print(f"  FAIL: v2 resplit {rs} {name} overlaps train ({len(a & train_set)} rows)")
                ok = False
            if a & probe_set:
                print(f"  FAIL: v2 resplit {rs} {name} overlaps probe ({len(a & probe_set)} rows)")
                ok = False
    print(f"  v2 splits: cal/test disjoint from train and probe for seeds {{0,1,57,99}}")
    print(f"  C2 {'PASS' if ok else 'FAIL'}\n")
    return ok


def section_freeze() -> bool:
    print("=== Freeze check: sha256 vs repro/MANIFEST.sha256 ===")
    manifest = _REPO / "repro" / "MANIFEST.sha256"
    if not manifest.exists():
        print("  FAIL: repro/MANIFEST.sha256 not found. Run `bash repro/make_manifest.sh` first "
              "(once, at the pre-fix commit).")
        print("  Freeze FAIL\n")
        return False
    expected = {}
    for line in manifest.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        # sha256sum may prefix the name with '*' (binary mode, e.g. on Git Bash).
        name = parts[-1].lstrip("*")
        expected[name] = parts[0]
    ok = True
    for rel in ("src/cafa/risk_control.py", "tests/test_risk_control.py"):
        actual = file_sha256(_REPO / rel)
        want = expected.get(rel) or expected.get(rel.replace("/", "\\"))
        match = (want is not None and actual == want)
        print(f"  {rel}: {'match' if match else 'MISMATCH'} ({actual[:12]}...)")
        if not match:
            ok = False
    print(f"  Freeze {'PASS' if ok else 'FAIL'}\n")
    return ok


def main() -> int:
    results = [section_c1(), section_c2(), section_freeze()]
    all_ok = all(results)
    print(f"OVERALL: {'ALL PASS' if all_ok else 'SOME FAILED'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
