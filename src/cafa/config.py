"""Configuration: environment-driven path resolution, experiment config, seeding.

No machine-specific paths live in the repo.  Roots are resolved from the
environment variables ``DATA_ROOT`` / ``RESULTS_ROOT`` / ``SCRATCH`` first, then
from a local (gitignored) ``configs/paths.yaml`` with ``${VAR}`` /
``${VAR:-default}`` expansion; otherwise a clear error names the missing vars.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

__all__ = ["Paths", "load_paths", "load_experiment", "set_seed"]

_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
_RESULT_SUBDIRS = ("checkpoints", "metrics", "figures", "logs")


@dataclass
class Paths:
    """Resolved repository roots."""

    data_root: Path
    results_root: Path
    scratch_root: Path


def _expand_vars(value: str) -> str:
    """Expand ``${VAR}`` and ``${VAR:-default}`` against the environment.

    Unset variables with no default expand to the empty string (treated as
    unresolved upstream).
    """

    def repl(match: "re.Match[str]") -> str:
        var, default = match.group(1), match.group(2)
        return os.environ.get(var, default if default is not None else "")

    return _VAR_PATTERN.sub(repl, value)


def load_paths(paths_yaml: str = "configs/paths.yaml", create: bool = True) -> Paths:
    """Resolve ``data_root`` / ``results_root`` / ``scratch_root``.

    Order of precedence, per key: environment variable, then ``configs/paths.yaml``.
    ``scratch_root`` defaults to ``$SCRATCH`` or ``/tmp``.  ``data_root`` and
    ``results_root`` are required; if neither the environment nor the YAML
    supplies them, a clear error names the missing variables.

    When ``create`` is True, ``results_root/{checkpoints,metrics,figures,logs}``
    are created.
    """
    resolved: dict[str, str] = {}
    env = {
        "data_root": os.environ.get("DATA_ROOT"),
        "results_root": os.environ.get("RESULTS_ROOT"),
        "scratch_root": os.environ.get("SCRATCH"),
    }
    for key, val in env.items():
        if val:
            resolved[key] = val

    # Fall back to a local (gitignored) YAML for anything still missing.
    if any(k not in resolved for k in ("data_root", "results_root", "scratch_root")):
        p = Path(paths_yaml)
        if p.is_file():
            with open(p, "r") as f:
                raw = yaml.safe_load(f) or {}
            for key in ("data_root", "results_root", "scratch_root"):
                if key not in resolved and raw.get(key) is not None:
                    expanded = _expand_vars(str(raw[key])).strip()
                    if expanded:
                        resolved[key] = expanded

    # scratch is optional -> default to $SCRATCH or /tmp
    if "scratch_root" not in resolved:
        resolved["scratch_root"] = os.environ.get("SCRATCH", "/tmp")

    missing = [k for k in ("data_root", "results_root") if k not in resolved]
    if missing:
        env_names = {"data_root": "DATA_ROOT", "results_root": "RESULTS_ROOT"}
        names = ", ".join(env_names[k] for k in missing)
        raise RuntimeError(
            f"Could not resolve required path(s): {missing}. "
            f"Set the environment variable(s) {names}, or create "
            f"'{paths_yaml}' (copy from 'configs/paths.template.yaml')."
        )

    paths = Paths(
        data_root=Path(resolved["data_root"]),
        results_root=Path(resolved["results_root"]),
        scratch_root=Path(resolved["scratch_root"]),
    )

    if create:
        for sub in _RESULT_SUBDIRS:
            (paths.results_root / sub).mkdir(parents=True, exist_ok=True)

    return paths


def load_experiment(path: str = "configs/experiment.yaml") -> dict:
    """Load the experiment config YAML into a dict."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def set_seed(seed: int) -> np.random.Generator:
    """Seed numpy's legacy global RNG and return a fresh ``Generator``."""
    np.random.seed(int(seed))
    return np.random.default_rng(int(seed))