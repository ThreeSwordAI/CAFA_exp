"""CAFA -- Conformal Active Feature Acquisition (core package).

Step 1 exposes the pure risk-control method, the synthetic generator, and the
metric/config helpers.  No deep learning is imported here.
"""

from __future__ import annotations

from . import config, metrics
from .data import make_synthetic_afa, risk_curve
from .risk_control import (
    SelectionResult,
    hoeffding_bentkus_pvalue,
    ltt_select,
    mondrian_select,
    weighted_ltt_select,
)

__all__ = [
    "hoeffding_bentkus_pvalue",
    "ltt_select",
    "SelectionResult",
    "mondrian_select",
    "weighted_ltt_select",
    "make_synthetic_afa",
    "risk_curve",
    "metrics",
    "config",
]