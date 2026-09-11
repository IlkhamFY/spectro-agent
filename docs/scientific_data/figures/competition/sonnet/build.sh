#!/usr/bin/env bash
# Build script for the SONNET entry: IRexp Fig 1/2/3 (pure TikZ/PGFPlots).
#
# Compiles every fig_irexp_*.tex in this directory with pdflatex (run twice
# for stable cross-references / bounding boxes), then rasterises each PDF to
# a 600 dpi PNG via pdftoppm. Intermediate LaTeX build artefacts (.aux/.log/
# .out) are removed; the .pdf and .png deliverables are kept alongside the
# .tex sources.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

FIGS=(
  fig_irexp_positioning
  fig_irexp_pipeline
  fig_irexp_distribution
)

echo "== SONNET figure build =="
for f in "${FIGS[@]}"; do
  tex="${f}.tex"
  if [[ ! -f "$tex" ]]; then
    echo "!! missing $tex, skipping" >&2
    continue
  fi
  echo "-- compiling $tex"
  pdflatex -interaction=nonstopmode -halt-on-error "$tex" > "${f}.compile.log" 2>&1 \
    || { echo "!! pdflatex failed for $tex -- see ${f}.compile.log"; tail -n 40 "${f}.compile.log"; exit 1; }
  # second pass keeps pgfplots/standalone bounding boxes stable
  pdflatex -interaction=nonstopmode -halt-on-error "$tex" >> "${f}.compile.log" 2>&1 \
    || { echo "!! pdflatex (pass 2) failed for $tex -- see ${f}.compile.log"; exit 1; }

  echo "-- rasterising ${f}.pdf -> ${f}.png (600 dpi)"
  pdftoppm -png -r 600 -singlefile "${f}.pdf" "${f}"

  rm -f "${f}.aux" "${f}.log" "${f}.out" "${f}.compile.log"
  echo "-- done: ${f}.pdf, ${f}.png"
done

echo "== build complete =="
ls -la fig_irexp_*.pdf fig_irexp_*.png
