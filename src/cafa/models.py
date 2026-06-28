"""Masked predictor for patch-wise active feature acquisition on MNIST.

An MNIST image is treated as a ``7 x 7`` grid of ``4 x 4`` patches (49 patch
"features").  A :class:`MaskedPredictor` maps *(image with unobserved patches
zeroed, patch mask)* to class logits over the 10 digits, and must predict from
**any** observed subset -- including the empty set (a marginal prior) and the
full set (full information).  It is trained with **random patch masking** so
that every observed-set size ``k in {0, ..., 49}`` is a well-calibrated target.

The module owns the patch geometry (``patches_to_image``, ``expand_patch_mask``)
so the data loader, the greedy policy, and the rollout all share one convention:

* ``X`` (patchified) has shape ``[N, P, D]`` -- ``P = 49`` patches of ``D = 16``
  pixels each, in **row-major patch order** (patch ``r*7 + c`` covers image rows
  ``4r:4r+4`` and cols ``4c:4c+4``).
* a patch mask has shape ``[N, P]`` with ``1.0`` for observed patches.
* the predictor input is two ``28 x 28`` channels: the masked image and the
  mask broadcast to pixels.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

__all__ = [
    "PATCH_GRID",
    "PATCH_SIZE",
    "N_PATCHES",
    "PATCH_DIM",
    "IMG_SIZE",
    "N_CLASSES",
    "patches_to_image",
    "expand_patch_mask",
    "build_inputs",
    "MaskedPredictor",
]

# --------------------------------------------------------------------------- #
# Patch geometry (single source of truth shared across the package)
# --------------------------------------------------------------------------- #
PATCH_GRID = (7, 7)          # (rows, cols) of patches
PATCH_SIZE = 4               # each patch is PATCH_SIZE x PATCH_SIZE pixels
N_PATCHES = PATCH_GRID[0] * PATCH_GRID[1]      # 49 features
PATCH_DIM = PATCH_SIZE * PATCH_SIZE            # 16 pixels per patch
IMG_SIZE = PATCH_GRID[0] * PATCH_SIZE          # 28
N_CLASSES = 10


def patches_to_image(patches: torch.Tensor) -> torch.Tensor:
    """Reassemble patchified pixels ``[B, P, D]`` into images ``[B, 1, H, W]``.

    Patch ``p = r*cols + c`` (row-major) is placed at image rows
    ``r*PATCH_SIZE : (r+1)*PATCH_SIZE`` and cols ``c*PATCH_SIZE : (c+1)*PATCH_SIZE``.
    """
    if patches.dim() != 3:
        raise ValueError(f"patches must be [B, P, D]; got {tuple(patches.shape)}.")
    B, P, D = patches.shape
    rows, cols = PATCH_GRID
    if P != N_PATCHES or D != PATCH_DIM:
        raise ValueError(f"expected P={N_PATCHES}, D={PATCH_DIM}; got P={P}, D={D}.")
    # [B, P, D] -> [B, rows, cols, ps, ps] -> [B, rows, ps, cols, ps] -> [B, H, W]
    x = patches.view(B, rows, cols, PATCH_SIZE, PATCH_SIZE)
    x = x.permute(0, 1, 3, 2, 4).contiguous()
    x = x.view(B, 1, rows * PATCH_SIZE, cols * PATCH_SIZE)
    return x


def expand_patch_mask(patch_mask: torch.Tensor) -> torch.Tensor:
    """Broadcast a per-patch mask ``[B, P]`` to a per-pixel mask ``[B, 1, H, W]``.

    Each patch's scalar (1.0 observed / 0.0 hidden) is repeated over its
    ``PATCH_SIZE x PATCH_SIZE`` pixel block.
    """
    if patch_mask.dim() != 2:
        raise ValueError(f"patch_mask must be [B, P]; got {tuple(patch_mask.shape)}.")
    B, P = patch_mask.shape
    rows, cols = PATCH_GRID
    if P != N_PATCHES:
        raise ValueError(f"expected P={N_PATCHES}; got P={P}.")
    m = patch_mask.view(B, rows, cols)
    m = m.repeat_interleave(PATCH_SIZE, dim=1).repeat_interleave(PATCH_SIZE, dim=2)
    return m.view(B, 1, rows * PATCH_SIZE, cols * PATCH_SIZE)


def build_inputs(patches: torch.Tensor, patch_mask: torch.Tensor) -> torch.Tensor:
    """Build the 2-channel predictor input from patches and a patch mask.

    Unobserved patches are zeroed in the image channel; the second channel is
    the mask broadcast to pixels.  Returns ``[B, 2, H, W]``.
    """
    pixel_mask = expand_patch_mask(patch_mask)            # [B, 1, H, W]
    image = patches_to_image(patches)                     # [B, 1, H, W]
    masked_image = image * pixel_mask                     # zero the hidden pixels
    return torch.cat([masked_image, pixel_mask], dim=1)   # [B, 2, H, W]


# --------------------------------------------------------------------------- #
# The masked predictor
# --------------------------------------------------------------------------- #
class MaskedPredictor(nn.Module):
    """A small 2-channel CNN classifier over observed patch subsets.

    Input  : ``[B, 2, 28, 28]`` -- (masked image, pixel mask).
    Output : class logits ``[B, 10]``.

    The architecture is intentionally small (two conv blocks + a small head);
    MNIST at patch granularity needs no more.  The mask channel lets the network
    distinguish "pixel is truly 0" from "pixel is unobserved", which is what
    makes empty-set and full-set predictions both meaningful.
    """

    def __init__(self, n_classes: int = N_CLASSES):
        super().__init__()
        self.n_classes = int(n_classes)
        self.features = nn.Sequential(
            nn.Conv2d(2, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                       # 28 -> 14
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                       # 14 -> 7
        )
        self.head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),               # [B, 64, 1, 1]
            nn.Flatten(),
            nn.Linear(64, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(128, self.n_classes),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """``inputs`` are the 2-channel tensors from :func:`build_inputs`."""
        if inputs.dim() != 4 or inputs.shape[1] != 2:
            raise ValueError(
                f"expected inputs [B, 2, H, W]; got {tuple(inputs.shape)}."
            )
        return self.head(self.features(inputs))

    def logits_from_patches(
        self, patches: torch.Tensor, patch_mask: torch.Tensor
    ) -> torch.Tensor:
        """Class logits ``[B, 10]`` from patchified pixels and a patch mask."""
        return self.forward(build_inputs(patches, patch_mask))

    @torch.no_grad()
    def predict_proba(
        self,
        images: torch.Tensor,
        masks: torch.Tensor,
        device: "torch.device | str | None" = None,
    ) -> np.ndarray:
        """Softmax probabilities ``[B, 10]`` for the policy / scores / rollout.

        Parameters
        ----------
        images : torch.Tensor, shape ``[B, P, D]``
            Patchified pixels (true values; hidden patches are zeroed internally
            via ``masks``).
        masks : torch.Tensor, shape ``[B, P]``
            Per-patch observed mask (1.0 = observed).

        Returns a **numpy** array so downstream readiness scores (numpy) and the
        frozen array-based selector compose without device juggling.
        """
        was_training = self.training
        self.eval()
        if device is None:
            device = next(self.parameters()).device
        images = torch.as_tensor(images, dtype=torch.float32, device=device)
        masks = torch.as_tensor(masks, dtype=torch.float32, device=device)
        logits = self.logits_from_patches(images, masks)
        probs = F.softmax(logits, dim=1)
        if was_training:
            self.train()
        return probs.detach().cpu().numpy()


# --------------------------------------------------------------------------- #
# Training entry (used by scripts/train_backbone.py)
# --------------------------------------------------------------------------- #
def random_patch_masks(
    batch_size: int,
    generator: torch.Generator,
    device: "torch.device | str",
    mask_min: int = 0,
    mask_max: int = N_PATCHES,
) -> torch.Tensor:
    """Draw per-sample random patch masks ``[B, P]`` for masked training.

    For each sample draw ``k ~ Uniform{mask_min, ..., mask_max}`` observed
    patches (inclusive of ``0`` and ``49``) and mark a random ``k``-subset as
    observed.  Vectorized via per-row random keys + thresholding so the whole
    batch is built without a Python loop.
    """
    P = N_PATCHES
    lo, hi = int(mask_min), int(mask_max)
    # k[i] in [lo, hi] inclusive.
    k = torch.randint(lo, hi + 1, (batch_size, 1), generator=generator, device=device)
    keys = torch.rand(batch_size, P, generator=generator, device=device)
    # Observed = the k smallest keys per row: rank via argsort of argsort.
    ranks = keys.argsort(dim=1).argsort(dim=1)        # 0..P-1 per row
    mask = (ranks < k).to(torch.float32)
    return mask


def train_masked_predictor(
    model: MaskedPredictor,
    X_train: np.ndarray,
    y_train: np.ndarray,
    *,
    epochs: int = 15,
    batch_size: int = 256,
    lr: float = 1e-3,
    mask_min: int = 0,
    mask_max: int = N_PATCHES,
    device: "torch.device | str" = "cpu",
    seed: int = 0,
    log_every: int = 0,
) -> dict:
    """Train ``model`` in place with random patch masking; return a small history.

    Parameters
    ----------
    X_train : np.ndarray, shape ``[N, P, D]``
        Patchified training images.
    y_train : np.ndarray, shape ``[N]``
        Integer class labels.

    Each minibatch draws a fresh random mask per sample (so the model sees every
    observed-set size), zeroes the hidden patches via the mask channel, and
    minimizes cross-entropy.  All randomness (shuffling + masks) is seeded.
    """
    device = torch.device(device)
    model.to(device)
    model.train()

    X = torch.as_tensor(np.asarray(X_train), dtype=torch.float32)
    y = torch.as_tensor(np.asarray(y_train), dtype=torch.long)
    N = X.shape[0]

    opt = torch.optim.Adam(model.parameters(), lr=float(lr))
    loss_fn = nn.CrossEntropyLoss()

    # Separate, seeded generators for CPU shuffling and (device) mask draws.
    cpu_gen = torch.Generator(device="cpu").manual_seed(int(seed))
    mask_gen = torch.Generator(device=device).manual_seed(int(seed) + 1)

    history: dict[str, list] = {"epoch_loss": [], "epoch_acc": []}
    for epoch in range(int(epochs)):
        perm = torch.randperm(N, generator=cpu_gen)
        running_loss, running_correct, seen = 0.0, 0, 0
        for start in range(0, N, batch_size):
            idx = perm[start : start + batch_size]
            xb = X[idx].to(device)
            yb = y[idx].to(device)
            mb = random_patch_masks(
                xb.shape[0], mask_gen, device, mask_min=mask_min, mask_max=mask_max
            )
            inputs = build_inputs(xb, mb)
            logits = model(inputs)
            loss = loss_fn(logits, yb)

            opt.zero_grad()
            loss.backward()
            opt.step()

            running_loss += float(loss.item()) * xb.shape[0]
            running_correct += int((logits.argmax(1) == yb).sum().item())
            seen += xb.shape[0]

        epoch_loss = running_loss / max(seen, 1)
        epoch_acc = running_correct / max(seen, 1)
        history["epoch_loss"].append(epoch_loss)
        history["epoch_acc"].append(epoch_acc)
        if log_every and (epoch % log_every == 0 or epoch == epochs - 1):
            print(
                f"[train] epoch {epoch + 1:>3}/{epochs}  "
                f"loss={epoch_loss:.4f}  masked_train_acc={epoch_acc:.4f}",
                flush=True,
            )
    return history