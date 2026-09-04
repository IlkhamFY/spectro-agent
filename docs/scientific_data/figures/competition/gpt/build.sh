#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

figures=(
  fig_irexp_positioning
  fig_irexp_pipeline
  fig_irexp_distribution
)

for figure in "${figures[@]}"; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error "${figure}.tex"
  pdftoppm -png -singlefile -r 600 "${figure}.pdf" "${figure}"
done

rm -f -- *.aux *.log
printf 'Built %s figures as PDF and 600 dpi PNG.\n' "${#figures[@]}"
