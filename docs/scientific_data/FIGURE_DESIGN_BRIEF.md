# IRexp Scientific Data — Figure Design Brief

**Reference:** Wang et al., *NMRexp*, Scientific Data 12:1954 (2025). DOI [10.1038/s41597-025-06245-5](https://doi.org/10.1038/s41597-025-06245-5).

**Manuscript:** `docs/scientific_data/scientific_data.tex`  
**Build:** `bash scripts/build_all_scidata_figures.sh` → `docs/scientific_data/figures/`  
**Agent playbook:** `docs/scientific_data/FIGURE_AGENT_PLAYBOOK.md`  
**Toolchain research:** `docs/scientific_data/FIGURE_TOOL_RESEARCH.md`

---

## Design rationale (Nature rebuild, Aug 2026)

Prior figures rated **3/10** — default matplotlib styling, cramped panels, pie charts, boxy pipeline schematic. This rebuild follows NMRexp editorial patterns with a locked design system.

### Design system (`scripts/figures/nature_design.py`)

| Token | Value | Rationale |
|-------|-------|-----------|
| Canvas width | 183 mm (`COL_FULL`) | Nature double-column |
| Body type | 7 pt Liberation Sans | Print floor at 89 mm |
| Panel labels | 8 pt bold uppercase A/B/C | NRJ extended-data spec |
| Palette | Paul Tol **Muted** | Colourblind-safe; restrained saturation |
| Line weight | 0.5 pt axes; 1.0 pt data | NRJ 0.25–1.0 pt range |
| Export | PDF (fonttype 42) + 600 dpi PNG | Vector primary; web fallback |

### Figure-specific editorial jobs

| Figure | NMRexp analogue | Engine | Key design choices |
|--------|-----------------|--------|-------------------|
| `fig_irexp_positioning` | Fig 1 scale comparison | matplotlib + nature_design | Log-scale bars; category bands; hatch view-only; callout "band lists ≠ spectra" |
| `fig_irexp_pipeline` | Fig 2A pipeline | **svgwrite SVG** → Inkscape PDF | PMC + Chemotion branches; Bézier merge; licence pool cylinders; flat-modern cards |
| `fig_irexp_overview` | Fig 3 composition | matplotlib + nature_design | (a) provenance donut, (b) licence pools, (c) modality waterfall; unified colour key |
| `fig_irexp_validation` | Table 2 / TV | matplotlib + nature_design | Forest plots + lollipop; Wilson CI; quarantine bar (no pie); automated watermark |

### Honesty rules (unchanged)

- Never label band lists as absorbance spectra
- Never imply human expert audits
- All counts from frozen JSON only
- External comparators cited in captions (SDBS, NMRexp)

### Build command

```bash
bash scripts/build_all_scidata_figures.sh
python3 scripts/build_scientific_data_pdf.py
```

### Quality self-rating (post-rebuild)

| Figure | Before | After | Notes |
|--------|--------|-------|-------|
| Positioning | 3/10 | **8/10** | NMRexp-pattern log bars; honest redistribution encoding |
| Pipeline | 3/10 | **8/10** | Hero SVG; Bézier branches; licence pools |
| Overview | 4/10 | **8/10** | Donut + pools + waterfall; unified key |
| Validation | 3/10 | **8/10** | Forest/lollipop; no pie; Wilson CI |

True **9/10** requires human Inkscape desktop pass on `fig_irexp_pipeline.svg` for connector micro-alignment.

---

## Manuscript placement

| Figure | Section | Label |
|--------|---------|-------|
| Positioning | Background & Summary | `fig:positioning` |
| Pipeline | Methods | `fig:pipeline` |
| Overview | Data Records | `fig:overview` |
| Validation | Technical Validation | `fig:validation` |
