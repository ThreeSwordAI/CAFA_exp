"""WO-7 -- small reproducibility helpers (torch-free).

A single shared ``file_sha256`` used by the backbone trainer and the pool runner
to fingerprint checkpoints and embed the hash in cache provenance.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

__all__ = ["file_sha256"]


def file_sha256(path, chunk_size: int = 1 << 20) -> str:
    """Return the hex sha256 of a file's bytes, streamed in ``chunk_size`` chunks."""
    h = hashlib.sha256()
    p = Path(path)
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(int(chunk_size)), b""):
            h.update(chunk)
    return h.hexdigest()
