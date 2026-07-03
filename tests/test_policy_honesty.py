"""WO-14.1 -- policy honesty: no unpaid (true) value reaches the predictor.

Targeted runtime < 5 s CPU.  The tabular probe is torch-free; the image probe
requires torch and is skipped otherwise.
"""

from __future__ import annotations

import numpy as np
import pytest

from cafa.tabular import TabularGreedyEntropyPolicy


class _RecordingTabular:
    def __init__(self):
        self.calls = []

    def predict_proba(self, X, mask, device=None):
        X = np.asarray(X, dtype=float)
        self.calls.append(X.copy())
        return np.full((X.shape[0], 2), 0.5, dtype=float)


def test_tabular_greedy_imputes_mean_never_true_value():
    X = np.array([[7.0, -3.0, 2.5]], dtype=np.float32)
    feature_groups = [np.array([0]), np.array([1]), np.array([2])]
    observed = np.zeros((1, 3), dtype=np.float32)
    pol = TabularGreedyEntropyPolicy(col_means=np.array([0.5, 0.5, 0.5], dtype=np.float32))
    rec = _RecordingTabular()
    pol.select_next(rec, X, observed, feature_groups, device="cpu")

    assert len(rec.calls) == 3
    for a in range(3):
        seen = float(rec.calls[a][0, a])
        assert abs(seen - 0.5) < 1e-9, f"candidate col {a} not mean-imputed: saw {seen}"
        assert abs(seen - float(X[0, a])) > 1e-9, f"candidate col {a} leaked its true value"


def test_tabular_constructor_requires_col_means():
    with pytest.raises(ValueError):
        TabularGreedyEntropyPolicy(col_means=np.array([]))


def test_image_greedy_candidate_pixels_equal_patch_means():
    torch = pytest.importorskip("torch")
    from cafa.acquisition import GreedyEntropyPolicy
    from cafa.models import N_PATCHES, PATCH_DIM

    class _RecordingImage:
        def __init__(self, n_classes=10):
            self.n_classes = n_classes
            self.seen = []

        def logits_from_patches(self, patches, mask):
            self.seen.append(patches.detach().cpu().numpy().copy())
            B = patches.shape[0]
            return torch.zeros((B, self.n_classes))

    # True pixels are a sentinel (999); patch means are 3.0 -- if any true pixel
    # reached the predictor it would show up as 999.
    patch_means = np.full((N_PATCHES, PATCH_DIM), 3.0, dtype=np.float32)
    X = torch.full((1, N_PATCHES, PATCH_DIM), 999.0)
    observed = torch.zeros((1, N_PATCHES))
    pol = GreedyEntropyPolicy(patch_means=patch_means)
    rec = _RecordingImage()
    pol.select_next(rec, X, observed, device="cpu")

    assert rec.seen, "predictor was never called"
    for arr in rec.seen:
        assert not np.any(np.isclose(arr, 999.0)), "true (unpaid) pixel value leaked to predictor"
        assert np.allclose(arr, 3.0), "candidate patches were not imputed at patch means"
