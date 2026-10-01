"""v3 -- torch models (skipped without torch; part of the local Phase-0 run)."""

from __future__ import annotations

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from cafa.models_v3 import (  # noqa: E402
    GreedyEntropyImagePolicy,
    MaskedPredictorV2,
    RandomImagePolicy,
    ResNetPatchPredictor,
    _random_masks,
    patch_mask_to_pixel_mask,
    train_masked_predictor_v2,
)


def test_masked_predictor_v2_interface_and_training():
    rng = np.random.default_rng(0)
    X = rng.uniform(size=(64, 49, 16)).astype(np.float32)
    y = rng.integers(0, 10, size=64)
    model = MaskedPredictorV2(n_classes=10, width_mult=1)
    probs = model.predict_proba(X[:8], np.ones((8, 49), np.float32))
    assert probs.shape == (8, 10) and np.allclose(probs.sum(1), 1.0, atol=1e-5)
    hist = train_masked_predictor_v2(model, X, y, epochs=1, batch_size=32, lr=1e-3, p_full=0.5, seed=0)
    assert len(hist["epoch_loss"]) == 1 and np.isfinite(hist["epoch_loss"][0])


def test_pixel_mask_layout_and_random_masks():
    pm = torch.zeros(1, 4)
    pm[0, 1] = 1.0                     # patch (row 0, col 1) of a 2x2 grid
    px = patch_mask_to_pixel_mask(pm, (2, 2), 8)
    assert px.shape == (1, 1, 8, 8)
    assert px[0, 0, :4, 4:].sum() == 16 and px.sum() == 16
    gen = torch.Generator(device="cpu").manual_seed(0)
    m = _random_masks(50, 13, gen, torch.device("cpu"))
    assert m.shape == (50, 13) and set(m.unique().tolist()) <= {0.0, 1.0}


def test_resnet_patch_predictor_and_image_policies():
    model = ResNetPatchPredictor(n_classes=10, patch_grid=(4, 4), img_size=64, pretrained=False).eval()
    imgs = np.random.default_rng(0).integers(0, 256, size=(3, 3, 64, 64), dtype=np.uint8)
    probs = model.predict_proba(imgs, np.ones((3, 16), np.float32))
    assert probs.shape == (3, 10)
    x_norm = model.normalize(torch.as_tensor(imgs))
    observed = torch.zeros(3, 16)
    observed[:, 0] = 1.0
    pol = GreedyEntropyImagePolicy.from_training_data(imgs, (4, 4), 64)
    nxt = pol.select_next(model, x_norm, observed, torch.device("cpu"))
    assert nxt.shape == (3,) and (nxt != 0).all()
    rnd = RandomImagePolicy(seed=0).select_next(model, x_norm, observed, torch.device("cpu"))
    assert rnd.shape == (3,) and (rnd != 0).all()
