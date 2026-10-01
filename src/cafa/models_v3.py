"""v3 -- stronger masked predictors (torch) with the v2 predictor interface.

``MaskedPredictorV2``   -- deeper BN-CNN for 28x28 patchified images (MNIST /
                           FashionMNIST); same surface as :class:`cafa.models.MaskedPredictor`
                           (``forward([B,2,28,28])``, ``logits_from_patches``,
                           ``predict_proba``), so every v2 policy / rollout works unchanged.
``train_masked_predictor_v2`` -- random-mask training with a ``p_full`` share of
                           full-observation samples (the AAAI backbones underweighted
                           full acquisition: 1/50 of the mask-size distribution) and
                           a cosine schedule.
``ResNetPatchPredictor`` -- ResNet-18 (4-channel input: masked RGB + pixel mask)
                           over a 7x7 patch grid for Imagenette; ``predict_proba``
                           takes uint8 images ``[B,3,H,W]`` + patch masks ``[B,P]``.
``GreedyEntropyImagePolicy`` -- mean-imputation greedy policy for RGB patch images
                           (hypothetical reveal with the per-patch training mean).
``train_resnet_patch_predictor`` -- fine-tuning loop with random patch masks.

The tabular predictor is unchanged (``cafa.models.TabularMaskedPredictor``,
width set from config).
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .data_v3 import IMAGENET_MEAN, IMAGENET_STD
from .models import N_CLASSES, build_inputs, random_patch_masks

__all__ = [
    "MaskedPredictorV2",
    "train_masked_predictor_v2",
    "ResNetPatchPredictor",
    "GreedyEntropyImagePolicy",
    "RandomImagePolicy",
    "train_resnet_patch_predictor",
    "patch_mask_to_pixel_mask",
]

_EPS = 1e-12


# --------------------------------------------------------------------------- #
# 28x28 patch images
# --------------------------------------------------------------------------- #
class MaskedPredictorV2(nn.Module):
    """Deeper 2-channel BN-CNN over observed patch subsets (``[B, 2, 28, 28]`` -> logits)."""

    def __init__(self, n_classes: int = N_CLASSES, width_mult: int = 2, dropout: float = 0.3):
        super().__init__()
        self.n_classes = int(n_classes)
        w = 32 * int(width_mult)

        def block(cin, cout):
            return nn.Sequential(
                nn.Conv2d(cin, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
                nn.Conv2d(cout, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
            )

        self.features = nn.Sequential(
            block(2, w), nn.MaxPool2d(2),            # 28 -> 14
            block(w, 2 * w), nn.MaxPool2d(2),        # 14 -> 7
            block(2 * w, 4 * w),
        )
        self.head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(4 * w, 256), nn.ReLU(inplace=True), nn.Dropout(dropout),
            nn.Linear(256, self.n_classes),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        if inputs.dim() != 4 or inputs.shape[1] != 2:
            raise ValueError(f"expected inputs [B, 2, H, W]; got {tuple(inputs.shape)}.")
        return self.head(self.features(inputs))

    def logits_from_patches(self, patches: torch.Tensor, patch_mask: torch.Tensor) -> torch.Tensor:
        return self.forward(build_inputs(patches, patch_mask))

    @torch.no_grad()
    def predict_proba(self, images, masks, device=None) -> np.ndarray:
        was_training = self.training
        self.eval()
        if device is None:
            device = next(self.parameters()).device
        images = torch.as_tensor(images, dtype=torch.float32, device=device)
        masks = torch.as_tensor(masks, dtype=torch.float32, device=device)
        probs = F.softmax(self.logits_from_patches(images, masks), dim=1)
        if was_training:
            self.train()
        return probs.detach().cpu().numpy()


def train_masked_predictor_v2(model, X_train, y_train, *, epochs=30, batch_size=256, lr=1e-3,
                              p_full=0.2, weight_decay=1e-4, device="cpu", seed=0, log_every=0) -> dict:
    """Random-mask training with a ``p_full`` share of full-observation samples."""
    device = torch.device(device)
    model.to(device)
    model.train()
    X = torch.as_tensor(np.asarray(X_train), dtype=torch.float32)
    y = torch.as_tensor(np.asarray(y_train), dtype=torch.long)
    N, P = X.shape[0], X.shape[1]
    opt = torch.optim.AdamW(model.parameters(), lr=float(lr), weight_decay=float(weight_decay))
    steps = int(epochs) * int(np.ceil(N / batch_size))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=float(lr), total_steps=max(steps, 1))
    loss_fn = nn.CrossEntropyLoss()
    cpu_gen = torch.Generator(device="cpu").manual_seed(int(seed))
    mask_gen = torch.Generator(device=device).manual_seed(int(seed) + 1)
    history = {"epoch_loss": [], "epoch_acc": []}
    for epoch in range(int(epochs)):
        perm = torch.randperm(N, generator=cpu_gen)
        run_loss, run_correct, seen = 0.0, 0, 0
        for start in range(0, N, batch_size):
            idx = perm[start:start + batch_size]
            xb, yb = X[idx].to(device), y[idx].to(device)
            B = xb.shape[0]
            mb = random_patch_masks(B, mask_gen, device, mask_min=0, mask_max=P)
            full = torch.rand(B, generator=mask_gen, device=device) < float(p_full)
            mb = torch.where(full[:, None], torch.ones_like(mb), mb)
            logits = model(build_inputs(xb, mb))
            loss = loss_fn(logits, yb)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
            run_loss += float(loss.item()) * B
            run_correct += int((logits.argmax(1) == yb).sum().item())
            seen += B
        history["epoch_loss"].append(run_loss / max(seen, 1))
        history["epoch_acc"].append(run_correct / max(seen, 1))
        if log_every and (epoch % log_every == 0 or epoch == epochs - 1):
            print(f"[train v2] epoch {epoch + 1:>3}/{epochs} loss={history['epoch_loss'][-1]:.4f} "
                  f"masked_acc={history['epoch_acc'][-1]:.4f}", flush=True)
    return history


# --------------------------------------------------------------------------- #
# RGB patch images (Imagenette)
# --------------------------------------------------------------------------- #
def patch_mask_to_pixel_mask(patch_mask: torch.Tensor, patch_grid, img_size: int) -> torch.Tensor:
    """``[B, P]`` patch mask -> ``[B, 1, S, S]`` pixel mask (row-major patches)."""
    gh, gw = int(patch_grid[0]), int(patch_grid[1])
    B = patch_mask.shape[0]
    m = patch_mask.view(B, 1, gh, gw)
    return F.interpolate(m, size=(int(img_size), int(img_size)), mode="nearest")


class ResNetPatchPredictor(nn.Module):
    """ResNet-18 over masked RGB images with a pixel-mask channel."""

    def __init__(self, n_classes: int = 10, patch_grid=(7, 7), img_size: int = 224, pretrained: bool = True):
        super().__init__()
        import torchvision

        self.n_classes = int(n_classes)
        self.patch_grid = (int(patch_grid[0]), int(patch_grid[1]))
        self.img_size = int(img_size)
        self.n_patches = self.patch_grid[0] * self.patch_grid[1]
        weights = torchvision.models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        net = torchvision.models.resnet18(weights=weights)
        old = net.conv1
        conv1 = nn.Conv2d(4, old.out_channels, kernel_size=old.kernel_size, stride=old.stride,
                          padding=old.padding, bias=False)
        with torch.no_grad():
            conv1.weight.zero_()
            conv1.weight[:, :3] = old.weight
        net.conv1 = conv1
        net.fc = nn.Linear(net.fc.in_features, self.n_classes)
        self.net = net
        self.register_buffer("mean", torch.tensor(IMAGENET_MEAN).view(1, 3, 1, 1))
        self.register_buffer("std", torch.tensor(IMAGENET_STD).view(1, 3, 1, 1))

    def normalize(self, images_uint8_or_float: torch.Tensor) -> torch.Tensor:
        x = images_uint8_or_float
        if x.dtype == torch.uint8:
            x = x.float() / 255.0
        return (x - self.mean) / self.std

    def build_inputs(self, images_norm: torch.Tensor, patch_mask: torch.Tensor) -> torch.Tensor:
        pm = patch_mask_to_pixel_mask(patch_mask.float(), self.patch_grid, self.img_size)
        return torch.cat([images_norm * pm, pm], dim=1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.net(inputs)

    def logits_from_images(self, images_norm: torch.Tensor, patch_mask: torch.Tensor) -> torch.Tensor:
        return self.forward(self.build_inputs(images_norm, patch_mask))

    @torch.no_grad()
    def predict_proba(self, images, masks, device=None) -> np.ndarray:
        """``images``: uint8 or float ``[B,3,S,S]`` (numpy or tensor); ``masks``: ``[B, P]``."""
        was_training = self.training
        self.eval()
        if device is None:
            device = next(self.parameters()).device
        x = torch.as_tensor(images, device=device)
        x = self.normalize(x)
        m = torch.as_tensor(masks, dtype=torch.float32, device=device)
        probs = F.softmax(self.logits_from_images(x, m), dim=1)
        if was_training:
            self.train()
        return probs.detach().cpu().numpy()


class GreedyEntropyImagePolicy:
    """Myopic mean-imputation greedy acquisition for RGB patch images.

    ``mean_image`` is the per-pixel training mean (uint8 or float ``[3, S, S]``);
    a hypothetical reveal of patch ``a`` fills patch ``a`` with the mean pixels.
    ``select_next(predictor, X_norm, observed, device)`` mirrors the MNIST policy
    (``X_norm`` normalised float images ``[B,3,S,S]``; ``observed`` ``[B, P]``).
    """

    name = "greedy_entropy"

    def __init__(self, mean_image: np.ndarray, patch_grid=(7, 7), img_size: int = 224, cand_chunk: int = 4):
        self.mean_image = np.asarray(mean_image, dtype=np.float32)
        self.patch_grid = (int(patch_grid[0]), int(patch_grid[1]))
        self.img_size = int(img_size)
        self.cand_chunk = int(cand_chunk)

    @classmethod
    def from_training_data(cls, X_train_uint8: np.ndarray, patch_grid=(7, 7), img_size: int = 224,
                           max_images: int = 2000):
        X = np.asarray(X_train_uint8)
        sel = X[: int(max_images)]
        return cls(sel.astype(np.float32).mean(axis=0) / 255.0, patch_grid, img_size)

    @torch.no_grad()
    def select_next(self, predictor, X_norm: torch.Tensor, observed: torch.Tensor, device) -> torch.Tensor:
        B, _, S, _ = X_norm.shape
        P = self.patch_grid[0] * self.patch_grid[1]
        mean = torch.as_tensor(self.mean_image, device=device)[None]              # [1,3,S,S] in [0,1]
        mean_norm = predictor.normalize(mean)                                     # [1,3,S,S]
        ent = torch.full((B, P), float("inf"), device=device)
        for c0 in range(0, P, self.cand_chunk):
            cands = list(range(c0, min(c0 + self.cand_chunk, P)))
            kc = len(cands)
            msk = observed.unsqueeze(1).expand(B, kc, P).clone()                  # [B,kc,P]
            for j, a in enumerate(cands):
                msk[:, j, a] = 1.0
            flat_msk = msk.reshape(B * kc, P)
            pm = patch_mask_to_pixel_mask(flat_msk, self.patch_grid, S)            # [B*kc,1,S,S]
            # candidate-only pixel mask -> where the candidate patch sits, use the mean
            cand_only = torch.zeros(B, kc, P, device=device)
            for j, a in enumerate(cands):
                cand_only[:, j, a] = 1.0
            pm_c = patch_mask_to_pixel_mask(cand_only.reshape(B * kc, P), self.patch_grid, S)
            x = X_norm.unsqueeze(1).expand(B, kc, 3, S, S).reshape(B * kc, 3, S, S)
            x = torch.where(pm_c > 0.5, mean_norm.expand_as(x), x)
            inputs = torch.cat([x * pm, pm], dim=1)
            probs = F.softmax(predictor(inputs), dim=1)
            e = -(probs * torch.log(probs.clamp_min(_EPS))).sum(dim=1)
            ent[:, c0:c0 + kc] = e.view(B, kc)
        ent = ent.masked_fill(observed > 0.5, float("inf"))
        return ent.argmin(dim=1)


class RandomImagePolicy:
    name = "random"

    def __init__(self, seed: int = 0):
        self.gen = torch.Generator(device="cpu").manual_seed(int(seed))

    @torch.no_grad()
    def select_next(self, predictor, X_norm, observed, device) -> torch.Tensor:
        keys = torch.rand(observed.shape, generator=self.gen).to(device)
        keys = keys.masked_fill(observed > 0.5, -1.0)
        return keys.argmax(dim=1)


def train_resnet_patch_predictor(model, X_uint8, y, *, epochs=12, batch_size=64, lr=3e-4, p_full=0.2,
                                 weight_decay=1e-4, device="cpu", seed=0, log_every=1) -> dict:
    """Fine-tune with random patch masks (``mask size ~ U{0..P}``, ``p_full`` full) and flips."""
    device = torch.device(device)
    model.to(device)
    model.train()
    X = np.asarray(X_uint8)
    yt = torch.as_tensor(np.asarray(y), dtype=torch.long)
    N, P = X.shape[0], model.n_patches
    opt = torch.optim.AdamW(model.parameters(), lr=float(lr), weight_decay=float(weight_decay))
    steps = int(epochs) * int(np.ceil(N / batch_size))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=float(lr), total_steps=max(steps, 1))
    loss_fn = nn.CrossEntropyLoss()
    cpu_gen = torch.Generator(device="cpu").manual_seed(int(seed))
    mask_gen = torch.Generator(device=device).manual_seed(int(seed) + 1)
    history = {"epoch_loss": [], "epoch_acc": []}
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    for epoch in range(int(epochs)):
        perm = torch.randperm(N, generator=cpu_gen).numpy()
        run_loss, run_correct, seen = 0.0, 0, 0
        for start in range(0, N, batch_size):
            idx = perm[start:start + batch_size]
            xb = torch.as_tensor(X[idx], device=device)
            yb = yt[idx].to(device)
            B = xb.shape[0]
            flip = torch.rand(B, generator=mask_gen, device=device) < 0.5
            xb = torch.where(flip[:, None, None, None], xb.flip(-1), xb)
            mb = _random_masks(B, P, mask_gen, device)
            full = torch.rand(B, generator=mask_gen, device=device) < float(p_full)
            mb = torch.where(full[:, None], torch.ones_like(mb), mb)
            with torch.autocast(device_type=device.type, enabled=use_amp):
                logits = model.logits_from_images(model.normalize(xb), mb)
                loss = loss_fn(logits, yb)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            run_loss += float(loss.item()) * B
            run_correct += int((logits.argmax(1) == yb).sum().item())
            seen += B
        history["epoch_loss"].append(run_loss / max(seen, 1))
        history["epoch_acc"].append(run_correct / max(seen, 1))
        if log_every and (epoch % log_every == 0 or epoch == epochs - 1):
            print(f"[train resnet] epoch {epoch + 1:>3}/{epochs} loss={history['epoch_loss'][-1]:.4f} "
                  f"masked_acc={history['epoch_acc'][-1]:.4f}", flush=True)
    return history


def _random_masks(B: int, P: int, gen, device) -> torch.Tensor:
    """Per-sample random patch masks with observed count ``~ U{0..P}`` (generic P)."""
    k = torch.randint(0, P + 1, (B,), generator=gen, device=device)
    keys = torch.rand(B, P, generator=gen, device=device)
    ranks = keys.argsort(dim=1).argsort(dim=1)
    return (ranks < k[:, None]).float()
