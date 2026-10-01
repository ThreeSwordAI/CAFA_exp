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


def _reference_select_next(pol, predictor, X_norm, observed):
    """The shipped (pre-fix) select_next: scores ALL P patches each step, masks observed after."""
    import torch.nn.functional as F
    B, _, S, _ = X_norm.shape
    P = pol.patch_grid[0] * pol.patch_grid[1]
    mean_norm = predictor.normalize(torch.as_tensor(pol.mean_image)[None])
    ent = torch.full((B, P), float("inf"))
    for c0 in range(0, P, pol.cand_chunk):
        cands = list(range(c0, min(c0 + pol.cand_chunk, P)))
        kc = len(cands)
        msk = observed.unsqueeze(1).expand(B, kc, P).clone()
        cand_only = torch.zeros(B, kc, P)
        for j, a in enumerate(cands):
            msk[:, j, a] = 1.0
            cand_only[:, j, a] = 1.0
        pm = patch_mask_to_pixel_mask(msk.reshape(B * kc, P), pol.patch_grid, S)
        pm_c = patch_mask_to_pixel_mask(cand_only.reshape(B * kc, P), pol.patch_grid, S)
        x = X_norm.unsqueeze(1).expand(B, kc, 3, S, S).reshape(B * kc, 3, S, S)
        x = torch.where(pm_c > 0.5, mean_norm.expand_as(x), x)
        probs = F.softmax(predictor(torch.cat([x * pm, pm], dim=1)), dim=1)
        ent[:, c0:c0 + kc] = (-(probs * torch.log(probs.clamp_min(1e-12))).sum(1)).view(B, kc)
    return ent.masked_fill(observed > 0.5, float("inf")).argmin(dim=1)


def test_greedy_image_policy_matches_reference_and_counts_passes():
    """v3 fix: select_next evaluates only unobserved candidates (P(P+1)/2 passes per rollout, as
    documented) and returns exactly the picks of the shipped all-P implementation."""
    torch.manual_seed(0)
    model = ResNetPatchPredictor(n_classes=10, patch_grid=(4, 4), img_size=32, pretrained=False).eval()
    rng = np.random.default_rng(1)
    imgs = rng.integers(0, 256, size=(5, 3, 32, 32), dtype=np.uint8)
    x_norm = model.normalize(torch.as_tensor(imgs))
    P = 16
    for chunk in (1, 4, 5, 16, 49):
        pol = GreedyEntropyImagePolicy.from_training_data(imgs, (4, 4), 32, cand_chunk=chunk)
        assert pol.cand_chunk == chunk and pol.amp is False
        for trial in range(4):
            counts = rng.integers(0, P, size=5)           # unequal numbers observed per row (0 .. P-1)
            counts[0], counts[1] = 0, P - 1
            observed = torch.zeros(5, P)
            for i, c in enumerate(counts):
                observed[i, torch.as_tensor(rng.permutation(P)[:c])] = 1.0
            new = pol.select_next(model, x_norm, observed, torch.device("cpu"))
            ref = _reference_select_next(pol, model, x_norm, observed)
            assert torch.equal(new, ref), (chunk, trial, new, ref)
            assert not bool(observed[torch.arange(5), new].any())
    # forward-pass count over a full rollout: sum_t (P - t) = P (P + 1) / 2 candidate images per row
    seen = []
    orig_forward = model.forward
    model.forward = lambda inp: (seen.append(int(inp.shape[0])), orig_forward(inp))[1]
    pol = GreedyEntropyImagePolicy.from_training_data(imgs, (4, 4), 32, cand_chunk=4)
    observed = torch.zeros(2, P)
    for t in range(P):
        nxt = pol.select_next(model, x_norm[:2], observed, torch.device("cpu"))
        observed = observed.clone()
        observed[torch.arange(2), nxt] = 1.0
    assert bool((observed == 1).all())
    assert sum(seen) == 2 * P * (P + 1) // 2
