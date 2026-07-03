#!/bin/bash
# WO-17 -- record the sha256 of the byte-frozen files.
# Run ONCE at the pre-fix commit (the frozen files are never edited by the v2
# work, so their hashes are canonical); do NOT re-run afterwards.
set -euo pipefail
cd "$(dirname "$0")/.."
sha256sum src/cafa/risk_control.py tests/test_risk_control.py > repro/MANIFEST.sha256
echo "wrote repro/MANIFEST.sha256:"
cat repro/MANIFEST.sha256
