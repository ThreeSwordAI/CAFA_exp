"""pytest bootstrap (v3): put ``src/`` on ``sys.path`` so ``import cafa`` works.

The v2 tests insert the path themselves; the nine v3 test files do not, so run
in isolation (``pytest tests/test_cascade.py ...``) they failed to collect with
``ModuleNotFoundError: No module named 'cafa'``.  This file only adds the path.
"""

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
