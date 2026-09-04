#!/usr/bin/env bash
# Regenerate all IRexp Scientific Data figures (NMRexp-quality toolchain).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== IRexp Scientific Data figures (TikZ Nature winners preferred) ==="
if [[ -f scripts/build_tikz_scidata_figures.sh ]]; then
  bash scripts/build_tikz_scidata_figures.sh
else
  python3 scripts/make_fig_irexp_positioning.py
  python3 scripts/make_fig_irexp_pipeline.py
  python3 scripts/make_fig_irexp_distribution.py
fi

echo ""
echo "Output:"
ls -lh docs/scientific_data/figures/fig_irexp_*.{pdf,png,svg} 2>/dev/null || ls -lh docs/scientific_data/figures/
