#!/usr/bin/env bash
# =====================================================================
#  Build the OPUS competition figures for the IRexp Scientific Data
#  manuscript: pure TeX sources -> vector PDF -> 600 dpi PNG.
#
#  Usage:  bash build.sh            # build all three figures
#          bash build.sh fig_irexp_pipeline
#
#  Requirements: pdflatex (TeX Live 2023+, pgfplots >= 1.18) and
#  pdftoppm (poppler-utils).  No network access, no fonts to install:
#  Helvetica comes from URW Nimbus Sans via the psnfss `helvet` package.
# =====================================================================
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FIGURES=(fig_irexp_positioning fig_irexp_pipeline fig_irexp_distribution)
if [[ $# -gt 0 ]]; then
  FIGURES=("$@")
fi

DPI=600

command -v pdflatex >/dev/null || { echo "error: pdflatex not found" >&2; exit 1; }
command -v pdftoppm >/dev/null || { echo "error: pdftoppm not found" >&2; exit 1; }

for fig in "${FIGURES[@]}"; do
  echo "=== ${fig} ==============================================="

  # Two passes: the first resolves node names used by later coordinates,
  # the second settles every reference.  -halt-on-error keeps a broken
  # figure from silently shipping a stale PDF.
  for pass in 1 2; do
    pdflatex -interaction=nonstopmode -halt-on-error \
             -file-line-error "${fig}.tex" > "${fig}.pass${pass}.log" 2>&1 \
      || { echo "error: pdflatex pass ${pass} failed for ${fig}" >&2
           grep -E "^.*:[0-9]+:|^!" "${fig}.pass${pass}.log" | head -20 >&2
           exit 1; }
  done

  # Fail loudly on boxes that would betray sloppy typesetting in print.
  if grep -qE "^(Overfull|Underfull)" "${fig}.pass2.log"; then
    echo "warning: over/underfull boxes in ${fig}" >&2
    grep -E "^(Overfull|Underfull)" "${fig}.pass2.log" >&2
  fi

  pdftoppm -png -r "${DPI}" -singlefile "${fig}.pdf" "${fig}"

  size=$(pdfinfo "${fig}.pdf" | sed -n 's/^Page size: *//p')
  echo "    ${fig}.pdf  ${size}"
  echo "    ${fig}.png  $(identify -format '%wx%h' "${fig}.png" 2>/dev/null \
        || python3 -c "import struct,sys;d=open('${fig}.png','rb').read(33);print('%dx%d'%struct.unpack('>II',d[16:24]))")  @ ${DPI} dpi"

  rm -f "${fig}.aux" "${fig}.pass1.log" "${fig}.pass2.log" "${fig}.log"
done

echo
echo "done: $(ls -1 fig_irexp_*.pdf fig_irexp_*.png | tr '\n' ' ')"
