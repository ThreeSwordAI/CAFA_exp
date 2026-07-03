#!/bin/bash
# WO-17 -- verify the byte-frozen files still match repro/MANIFEST.sha256.
set -euo pipefail
cd "$(dirname "$0")/.."
sha256sum -c repro/MANIFEST.sha256
