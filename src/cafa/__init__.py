"""CAFA -- Conformal Active Feature Acquisition (core package).

Step 1 exposed the pure risk-control method, the synthetic generator, and the
metric/config helpers.  Step 2 adds the real machinery that produces the
selector's input arrays on MNIST: a masked predictor (:mod:`cafa.models`), an
acquisition policy + rollout (:mod:`cafa.acquisition`), readiness scores
(:mod:`cafa.scores`), and an MNIST patch loader (:func:`cafa.data.load_mnist_afa`).

The pure path (risk control, synthetic data, metrics, scores, config) imports
without torch.  The deep-learning pieces (``models``, ``acquisition``) depend on
torch and are imported lazily on first access, so ``import cafa`` works in a
torch-free environment (e.g. the G1 gate) and only pays for torch when the
model/rollout machinery is actually used.
"""

from __future__ import annotations

from . import config, metrics, scores
from .data import (
    load_mnist_afa,
    make_observed_tensors,
    make_synthetic_afa,
    make_synthetic_mondrian,
    patchify_images,
    risk_curve,
)
from .risk_control import (
    MondrianResult,
    SelectionResult,
    hoeffding_bentkus_pvalue,
    ltt_select,
    mondrian_select,
    weighted_ltt_select,
)
from .metrics import (
    per_bucket_cost,
    per_bucket_risk,
    quantile_bucket_edges,
    reference_buckets,
    reference_depth,
    stops_from_grid_np,
)
from .scores import get_score_fn

__all__ = [
    # --- pure risk-control core (Step 1) ---
    "hoeffding_bentkus_pvalue",
    "ltt_select",
    "SelectionResult",
    "mondrian_select",
    "MondrianResult",
    "weighted_ltt_select",
    # --- per-bucket (Mondrian) helpers (Step 3; numpy-only) ---
    "stops_from_grid_np",
    "reference_depth",
    "reference_buckets",
    "quantile_bucket_edges",
    "per_bucket_risk",
    "per_bucket_cost",
    # --- synthetic + MNIST data ---
    "make_synthetic_afa",
    "make_synthetic_mondrian",
    "risk_curve",
    "load_mnist_afa",
    "patchify_images",
    "make_observed_tensors",
    # --- readiness scores ---
    "scores",
    "get_score_fn",
    # --- helpers / config ---
    "metrics",
    "config",
    # --- deep-learning machinery (lazy; require torch) ---
    "models",
    "acquisition",
    "MaskedPredictor",
    "rollout",
    "stops_from_grid",
    "Trajectories",
    "get_policy",
]

# Lazily expose the torch-dependent modules and their key names so that simply
# importing :mod:`cafa` does not require torch, while ``cafa.models`` /
# ``cafa.rollout`` / etc. still resolve on demand (PEP 562).
_LAZY_MODULES = {"models", "acquisition"}
_LAZY_ATTRS = {
    "MaskedPredictor": ("models", "MaskedPredictor"),
    "rollout": ("acquisition", "rollout"),
    "stops_from_grid": ("acquisition", "stops_from_grid"),
    "Trajectories": ("acquisition", "Trajectories"),
    "get_policy": ("acquisition", "get_policy"),
}


def __getattr__(name):  # noqa: D401  (module-level lazy attribute hook)
    import importlib

    if name in _LAZY_MODULES:
        return importlib.import_module(f".{name}", __name__)
    if name in _LAZY_ATTRS:
        mod_name, attr = _LAZY_ATTRS[name]
        mod = importlib.import_module(f".{mod_name}", __name__)
        return getattr(mod, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")