# Scientific Data Figure Toolchain Research (2025–2026)

Research for upgrading IRexp Scientific Data figures from default matplotlib to
Nature Portfolio / *Scientific Data* production quality. Conducted August 2026 for
the IlkhamFY/spectro-agent repository.

---

## 1. Publisher requirements (Nature Portfolio / Scientific Data)

### Vector vs raster

| Content type | Required format | Resolution |
|--------------|-----------------|------------|
| Line art, graphs, schematics | **Vector** (AI, EPS, PDF) | Resolution-independent |
| Photographs, complex renders | Bitmap (TIFF preferred) | ≥ 300 DPI at final size |
| Combination (photo + line art) | Mixed; line elements as vectors | Bitmap ≥ 500 DPI |

Sources: [Nature artwork guide (NRJ)](https://www.nature.com/documents/NRJs-guide-to-preparing-final-artwork.pdf), [Nature Reviews figure guidelines](https://www.nature.com/documents/natrev-figure-guidelines-v1.pdf).

### Typography

- **Sans-serif** preferred: Helvetica, Arial, or metric-compatible substitutes (Liberation Sans).
- **5–8 pt** at final printed width; *Scientific Data* two-column text width ≈ 183 mm (6.3 in).
- Panel labels: **bold uppercase** (A, B, C), top-left, ≥ 8 pt.
- Text must remain **editable** in vector files — do not flatten to paths unless exporting a raster fallback.
- Matplotlib: `pdf.fonttype = 42` (TrueType embedding) for Illustrator/Inkscape compatibility.

### Colour

- Colourblind-safe palettes (Paul Tol, Wong 2011).
- Restrained saturation; avoid default matplotlib tab10.
- Accessible contrast (WCAG AA for text on coloured fills).

### Figure dimensions

| Layout | Width |
|--------|-------|
| Single column | 89 mm (3.5 in) |
| 1.5 column | 120 mm |
| Full text width | 183 mm (6.3 in) |
| Max height | 247 mm |

---

## 2. Tool survey

### Desktop / GUI tools

| Tool | Strengths | Weaknesses | Headless Linux VM |
|------|-----------|------------|-------------------|
| **Adobe Illustrator** | Industry standard; precise typography; Nature production | Expensive; macOS/Win GUI | ❌ No |
| **Inkscape** | Free; SVG-native; CLI export (`--export-type=pdf`); path ops | GUI for final polish; font management | ✅ CLI only |
| **Affinity Designer** | Illustrator alternative; one-time purchase | No Linux; no CLI | ❌ No |
| **BioRender** | Biomedical icon library; polished schematics | Subscription; no API without account; export limits | ❌ No |
| **Figma** | Collaborative; component libraries | Web/GUI; not reproducible from scripts | ❌ No |
| **GraphPad Prism** | Statistics + publication charts; Wilson CI built-in | Windows/macOS GUI; not scriptable in CI | ❌ No |

### Programmatic / reproducible tools

| Tool | Strengths | Weaknesses | Headless VM |
|------|-----------|------------|-------------|
| **matplotlib + custom rcParams** | Already in repo; PDF/SVG export; full control | Schematics look "boxy" without heavy customization | ✅ Yes |
| **plotnine (ggplot2)** | Grammar of graphics; clean defaults; SVG with `svg_usefonts` | Extra dependency; still matplotlib backend | ✅ Yes |
| **Plotly + Kaleido** | Interactive; web-quality defaults | Raster-first export; less print control | ✅ Yes (Kaleido) |
| **R ggplot2** | Gold standard for stat figures | R runtime; mixed stack with Python repo | ✅ Yes (if R installed) |
| **svgwrite / drawsvg** | Native SVG schematics; crisp arrows/boxes | No chart primitives; manual layout | ✅ Yes |
| **TikZ / PGF** | LaTeX-native vector; perfect typography | Slow iteration; steep learning curve | ✅ Yes |

### Export helpers

| Tool | Role |
|------|------|
| **Inkscape CLI** | SVG → PDF/PNG batch; font subsetting; path simplification |
| **cairosvg** | Pure-Python SVG → PNG/PDF (no Inkscape required) |
| **librsvg (`rsvg-convert`)** | Fast SVG → PNG rasterisation |

---

## 3. What NMRexp and peer Sci Data papers actually use

### NMRexp (Wang et al. 2025, *Scientific Data* 12:1954)

- **Fig 1** — log-scale database comparison bar chart (vector).
- **Fig 2** — multi-stage pipeline schematic + cleaning examples (vector diagram + panels).
- **Fig 3** — multi-panel distribution grid (nuclei, solvent, frequency, MW).
- **Fig 4** — replicate MAE histograms.

Editorial characteristics observed in the published PDF:

- Clean sans-serif throughout; consistent 8 pt axis labels.
- Restrained blue/teal/grey palette; no chartjunk.
- Pipeline schematic uses **designed boxes with numbered stages**, not matplotlib defaults.
- All figures are **vector** in the PDF (text selectable, lines crisp at any zoom).
- No evidence of BioRender; schematic style is custom Illustrator/Inkscape-class layout.

Comparable Sci Data resource papers (NMRBank, MassBank, PubChem subsets) follow the same pattern: **vector PDF primary**, 300+ DPI PNG for web previews, Helvetica-class fonts.

---

## 4. Headless vs GUI in this Linux cloud VM

| Capability | Available | Notes |
|------------|-----------|-------|
| matplotlib Agg backend | ✅ | Primary chart engine |
| Liberation Sans (Helvetica-compatible) | ✅ | System font |
| Inkscape 1.2 CLI | ✅ | `inkscape --export-type=pdf` |
| cairosvg | ✅ | pip-installed; SVG→PNG/PDF fallback |
| plotnine | ❌ (optional) | Not installed; matplotlib sufficient with theme |
| BioRender / Illustrator / Prism | ❌ | GUI-only; not reproducible |
| Inkscape GUI polish | ❌ | Human opens SVG locally for final 1% tweaks |

**Realistic workflow for CI / cloud agents:**

1. Python scripts generate SVG (schematics) or PDF (charts) programmatically.
2. Inkscape CLI or cairosvg batch-export PNG at 600 DPI.
3. Real files committed to `docs/scientific_data/figures/` (Overleaf-safe).
4. Optional human pass: open `.svg` in Inkscape desktop for micro-adjustments.

---

## 5. Recommended stack for spectro-agent

```
┌─────────────────────────────────────────────────────────────┐
│  Frozen JSON counts (irexp_stats.json, qc_*.json)           │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
  matplotlib +        svgwrite           figstyle.py
  scidata_theme       pipeline_svg       (Paul Tol palette)
  (data charts)       (flow schematic)
         │                 │
         └────────┬────────┘
                  ▼
         scidata_export.py
         (PDF + 600 dpi PNG)
                  │
         ┌────────┴────────┐
         ▼                 ▼
   optional Inkscape   cairosvg fallback
   CLI optimise        (PNG raster)
         │
         ▼
  docs/scientific_data/figures/
  fig_irexp_*.{pdf,png,svg}
```

### Rationale

| Figure | Engine | Why |
|--------|--------|-----|
| `fig_irexp_positioning` | matplotlib + scidata_theme | Log-scale bars; direct labels; proven pattern |
| `fig_irexp_pipeline` | **svgwrite → SVG** | Designed schematic; beats matplotlib boxes |
| `fig_irexp_overview` | matplotlib + scidata_theme | Multi-panel bar charts; shared theme |
| `fig_irexp_validation` | matplotlib + scidata_theme | Error bars, donut; 2×2 grid |

### Build entry point

```bash
bash scripts/build_all_scidata_figures.sh
```

Regenerates all four figures + optional Inkscape PNG pass.

---

## 6. Quality checklist (applied to IRexp figures)

- [x] Vector PDF primary (`pdf.fonttype=42`)
- [x] 600 DPI PNG fallback (≥ 300 DPI requirement)
- [x] Liberation Sans / Helvetica-compatible typography
- [x] Paul Tol Vibrant palette (colourblind-safe)
- [x] Panel letters bold, outside axes
- [x] No chartjunk; whisper-faint grids on value axis only
- [x] Real counts from frozen JSON only
- [x] Honest modality labels (band lists ≠ spectra)
- [x] Pipeline schematic as designed SVG, not matplotlib patches
- [x] Reproducible scripts committed to repo

---

## 7. References

- Nature artwork guide: https://www.nature.com/documents/NRJs-guide-to-preparing-final-artwork.pdf
- Scientific Data author instructions: https://www.nature.com/sdata/submit-guidelines
- NMRexp paper: https://doi.org/10.1038/s41597-025-06245-5
- Paul Tol palettes: https://personal.sron.nl/~pault/
- Inkscape CLI: https://wiki.inkscape.org/wiki/Using_the_Command_Line
- plotnine SVG fonts: https://plotnine.org/reference/svg_usefonts.html
