#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for fig in fig_irexp_positioning fig_irexp_pipeline fig_irexp_distribution; do
  echo "=== $fig ==="
  pdflatex -interaction=nonstopmode -halt-on-error "$fig.tex" | tail -20
  pdftoppm -png -r 600 "$fig.pdf" "$fig"
  # pdftoppm adds -1 suffix for single page
  if [[ -f "${fig}-1.png" ]]; then mv "${fig}-1.png" "${fig}.png"; fi
  ls -lh "$fig.pdf" "$fig.png"
done
echo DONE
