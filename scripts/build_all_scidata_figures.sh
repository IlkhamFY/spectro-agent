#!/usr/bin/env bash
# Regenerate all IRexp Scientific Data figures (premium toolchain).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== IRexp Scientific Data figures ==="
python3 scripts/make_fig_irexp_positioning.py
python3 scripts/make_fig_irexp_pipeline.py
python3 scripts/make_fig_irexp_overview.py
python3 scripts/make_fig_irexp_validation.py

echo ""
echo "Output:"
ls -lh docs/scientific_data/figures/fig_irexp_*.{pdf,png,svg} 2>/dev/null || ls -lh docs/scientific_data/figures/
