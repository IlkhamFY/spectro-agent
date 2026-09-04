#!/usr/bin/env bash
# Rebuild winning TikZ Sci Data figures → docs/scientific_data/figures/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIN="$ROOT/docs/scientific_data/figures/tikz/winning"
OUT="$ROOT/docs/scientific_data/figures"
COMP="$ROOT/docs/scientific_data/figures/competition"

# Prefer winning/ sources; fall back to competition dirs
build_one() {
  local name="$1" srcdir="$2"
  local tex="$srcdir/${name}.tex"
  if [[ ! -f "$tex" ]]; then
    echo "missing $tex" >&2
    return 1
  fi
  echo "=== $name ($srcdir) ==="
  (
    cd "$srcdir"
    pdflatex -interaction=nonstopmode -halt-on-error "${name}.tex" >/tmp/tikz_${name}.log
    pdftoppm -png -r 600 "${name}.pdf" "/tmp/${name}_exp"
    mv -f "/tmp/${name}_exp-1.png" "$OUT/${name}.png"
    cp -f "${name}.pdf" "$OUT/${name}.pdf"
  )
  ls -lh "$OUT/${name}.pdf" "$OUT/${name}.png"
}

# Ensure plot macros exist
python3 "$ROOT/scripts/emit_tikz_plot_data.py"

build_one fig_irexp_positioning "$WIN"
build_one fig_irexp_pipeline "$WIN"
build_one fig_irexp_distribution "$WIN"
echo "DONE — promoted TikZ winners to $OUT"
