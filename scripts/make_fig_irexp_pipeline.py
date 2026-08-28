#!/usr/bin/env python3
"""IRexp harvest provenance pipeline (NMRexp Fig. 2A analogue).

SVG schematic → PDF + PNG via Inkscape/cairosvg.
Output: docs/scientific_data/figures/fig_irexp_pipeline.{svg,pdf,png}
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "figures"))

from pipeline_svg import build_svg  # noqa: E402
from scidata_export import save_svg_bundle  # noqa: E402

OUT_DIR = ROOT / "docs/scientific_data/figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

svg_path = OUT_DIR / "fig_irexp_pipeline.svg"
build_svg(svg_path)
save_svg_bundle(svg_path)
print(f"wrote {svg_path} (+ pdf/png)")
