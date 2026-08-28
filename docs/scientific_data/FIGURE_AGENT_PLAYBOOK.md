# IRexp Figure Agent Playbook

**Purpose:** Operational guide for Nature Portfolio–grade Scientific Data figures in IlkhamFY/spectro-agent.  
**Updated:** 2026-08-28  
**Reference paper:** Wang et al., *NMRexp*, Sci Data 12:1954 (2025) — [doi:10.1038/s41597-025-06245-5](https://doi.org/10.1038/s41597-025-06245-5)

---

## 1. AI agent skills & workflows (2025–2026)

### Open standards

| Standard | URL | Role |
|----------|-----|------|
| Agent Skills (SKILL.md) | https://agentskills.io | Portable skill bundles for Claude Code, Codex, Cursor |
| Cursor Skills | https://cursor.com/docs/context/skills | Project-scoped procedural memory |
| HuggingFace Papers | https://huggingface.co/papers | Discovery of figure-generation research |

### Research-grade agent frameworks

| Framework | Source | Workflow pattern |
|-----------|--------|------------------|
| **SciFig** | HF paper 2601.04390 | Parse text → hierarchical layout → CoT visual critique loop → rubric scoring |
| **AutoFigure** | arXiv:2602.03828 | Semantic parsing → layout planning → aesthetic rendering → text refinement |
| **PaperBanana** | HF Spaces / ClawHub skill | Retriever → Planner → Stylist → Visualizer → Critic (5-agent closed loop) |
| **Academic Figure Skill** | github.com/TingxiYu/academic-figure-skill | 8-step: archetype → panel plan → style injection → 4-pass QA → vector PDF |
| **sci-figure** | github.com/xiao-yuling/sci-figure | Elsevier/SCI defaults; platform-independent SKILL.md |
| **AgentFigureGallery** | github.com/Dsadd4/AgentFigureGallery | Reference gallery → user likes → style bundle for plotting code |

### Recommended agent workflow for IRexp

```
1. LOCK DATA     → irexp_stats.json, pmc_licence_summary.json, data/audit/*.json
2. REFERENCE     → NMRexp PDF Fig 1–3 layout analysis (this playbook §4)
3. DESIGN SYSTEM → scripts/figures/nature_design.py (palette, type, export)
4. SEPARATE LAYERS
     • Data charts  → matplotlib + nature_design
     • Schematics   → hand-coded SVG (svgwrite) → Inkscape CLI PDF
5. SELF-CRITIQUE → checklist §6 before commit
6. VISUAL PROOF  → render at 89 mm width; inspect PNG at 100% zoom
7. HUMAN POLISH  → optional Inkscape desktop pass on .svg sources (final 1%)
```

### Cursor / Claude prompt patterns that work

- *"Build figure canvas at final print width (89 mm or 183 mm) before drawing."*
- *"One editorial job per figure; no decorative charts."*
- *"Panel labels: bold uppercase A/B/C, top-left, 8 pt."*
- *"Direct labels over legends; Wilson CI error bars for rates."*
- *"Never use matplotlib tab10; use locked Paul Tol Muted palette."*
- *"Schematic as editable SVG with Bézier connectors, not FancyBboxPatch."*

---

## 2. Professional tools ranked (Nature Portfolio output)

### Tier 1 — Production vector (human polish)

| Tool | Score | Strengths | Headless VM |
|------|-------|-----------|-------------|
| **Adobe Illustrator** | 10/10 | Industry standard; editable layers; precise typography | ❌ |
| **Inkscape 1.2+** | 9/10 | Free SVG-native; CLI `--export-type=pdf/png`; path ops | ✅ CLI |
| **Affinity Designer** | 8/10 | Illustrator alternative; one-time purchase | ❌ |

### Tier 2 — Programmatic charts (reproducible)

| Tool | Score | Strengths | Headless VM |
|------|-------|-----------|-------------|
| **matplotlib + nature_design** | 8/10 | Full control; PDF/SVG; CI-reproducible | ✅ |
| **R ggplot2 + patchwork** | 9/10 | Clean defaults; grammar of graphics; journal themes | ✅ (if R installed) |
| **plotnine** | 8/10 | ggplot2 port; `svg_usefonts` for editable text | ✅ |
| **Plotly + Kaleido** | 6/10 | Web-quality; raster-first; less print control | ✅ |

### Tier 3 — Schematics

| Tool | Score | Strengths | Headless VM |
|------|-------|-----------|-------------|
| **svgwrite / hand SVG** | 9/10 | Crisp arrows; Bézier paths; version-controlled | ✅ |
| **draw.io / diagrams.net** | 8/10 | Fast flowcharts; XML export → Inkscape polish | ⚠️ GUI |
| **BioRender** | 9/10 (style) | Biomedical icon library; polished look | ❌ No API |
| **Excalidraw** | 7/10 | Sketch aesthetic; not Nature-formal | ⚠️ |
| **TikZ / PGF** | 9/10 | LaTeX-native typography; slow iteration | ✅ |

### Tier 4 — Typography stacks

| Font | Role | Availability |
|------|------|--------------|
| **Helvetica / Arial** | Nature first choice | System / metric-compatible |
| **Liberation Sans** | Helvetica substitute (Linux) | ✅ installed |
| **Source Sans Pro** | Adobe open; modern | Optional apt/font |
| **IBM Plex Sans** | Technical clarity | Optional pip/font |

### BioRender mimicry (no API)

Replicate BioRender editorial style with:
- Rounded rects (rx=10–12), 1.5 pt coloured top accent bar
- Flat fills + 2 px offset shadow at 15% opacity
- Icon circles with step numbers (filled ink, white numeral)
- Restrained 4–5 colour palette; white card backgrounds
- Generous inter-box spacing (≥24 px)

---

## 3. Nature Portfolio figure specifications (exact)

Sources: [Nature final submission](https://www.nature.com/nature/for-authors/final-submission), [NRJ artwork guide](https://www.nature.com/documents/NRJs-guide-to-preparing-final-artwork.pdf), [Extended Data sizing PDF](https://www.nature.com/documents/nature-extended-data.pdf).

### Dimensions

| Layout | Width | Max height |
|--------|-------|------------|
| Single column | **89 mm** (88–90 mm) | 247 mm |
| 1.5 column | 120–136 mm | 247 mm |
| Double column | **183 mm** (180–183 mm) | 247 mm |

**Rule:** Author at target width in mm × DPI before drawing. Do not draw at screen size and downscale.

### Resolution & format

| Content | Format | Resolution |
|---------|--------|------------|
| Line art, graphs, schematics | **Vector** PDF/EPS/AI/SVG | Resolution-independent |
| Photographs | TIFF/PSD layered | ≥ 300 DPI |
| Combination | Mixed | Bitmap ≥ 500 DPI |
| Production TIFF | TIFF | 600–1200 DPI common |

### Typography

- **Sans-serif:** Helvetica, Arial, or Liberation Sans
- **Body text in figure:** 5–7 pt at final print size
- **Panel labels:** **8 pt bold uppercase** (A, B, C), top-left, upright
- **Greek:** Symbol font or mathtext
- **Editable text:** `pdf.fonttype = 42` (TrueType embedding)

### Line weights

- **Range:** 0.25–1.0 pt at final size
- **Recommended:** 0.5–0.75 pt axes; 1.0–1.5 pt schematic boxes
- **Do not rasterize** line art strokes

### Colour

- Colourblind-safe (Paul Tol Bright/Muted, Wong 2011, Okabe-Ito)
- Avoid pure red/green adjacency
- Test grayscale conversion before submit
- RGB for initial submission

---

## 4. What makes NMRexp figures work (Fig 1–4 analysis)

Re-fetched PDF + user reference PNGs (2026-08-28).

### Fig 1 — Database positioning (3D isometric + sidebar)

- **Layout:** 3D perspective grouped bars on linear scale; back-wall grid; floor perspective lines
- **Stacks:** Colour-coded sub-series per database (Total / modality / subset); legend top-left with mini 3D swatches
- **Access tags:** "Open-access" (blue) / "Commercial" or "View-only" (black) above each cluster
- **Hero callout:** Dark-blue star + bold "This Work" above hero database
- **Sidebar box:** Drop-shadow white card; navy header bar; checkmark bullets (Large / Accurate / Detailed)
- **Honest scale:** Y-axis in millions; hero bar dominates but comparators visible

**IRexp adaptation:** `draw_iso_bar()` in `nature_design.py`; stacks = Total / structure-linked / CC-BY pool; sidebar = Large / Redistributable / Traceable; footnote "band lists ≠ spectra".

### Fig 2A — Pipeline schematic

- **Layout:** Left-to-right flow inside dashed rounded boundary; downward branch for cleaning
- **Style:** Stage cards with navy header bars; PDF/DB icons; monospace extracted strings in red
- **Connectors:** Labelled arrows ("Layout Detection", "OCSR", "GPT RE" analogues)
- **Cleaning table:** 2×3 inset with navy header, light-blue cells, "+ N more rules" footer
- **Final box:** Large counts + DB icon + JSON snippet + "Well-structured" tag

**IRexp adaptation:** `pipeline_svg.py` — Panel A workflow + Panel B QC rows with red highlight boxes and ✕ marks.

### Fig 3 — Multi-panel distribution

- **Layout:** 3+2 grid; bold A–E panel letters top-left outside plot
- **Bars:** Horizontal, solid `#4A7EBB`; counts at bar ends; NO x-axis ticks; faint horizontal grid only
- **Y-axis:** Category labels right-aligned to vertical spine line
- **Panel D:** Overlaid area/histogram with labelled x-axis (MW analogue)
- **Panel E:** Two-column element bars sharing spine aesthetic

**IRexp adaptation:** `hbar_panel()` helper; panels A–E provenance / licence / modality / band-count / elements.

### Fig 4 — Error / validation histograms

- **Layout:** 2×3 grid of histograms; bold panel letters
- **Bars:** Same `#4A7EBB` blue; no y-axis labels; clean x-axis with units
- **Annotations:** Median + aggregate rate via dashed grey elbow lines to x-axis
- **No gridlines** inside histogram panels

**IRexp adaptation:** Merged into Fig 3 panel F (2×2); real audit-derived per-record/per-paper distributions — NOT synthetic beta draws.

---

## 5. Matplotlib anti-patterns (amateur tells)

| Anti-pattern | Fix |
|--------------|-----|
| Default `tab10` blue/orange | Locked Paul Tol Muted palette in `nature_design.py` |
| All four spines visible | Drop top/right; 0.5 pt left/bottom only |
| Thick spines (≥1.5 pt) | 0.5–0.6 pt ink grey `#4a4f54` |
| Legend when direct labels suffice | Bar-end value labels; inline annotations |
| `tight_layout` crop killing panel letters | Fixed `subplots_adjust` + outside panel labels |
| 12 pt labels shrunk to 5 pt | Author at 7–8 pt at final figsize |
| Pie charts for 2 categories | Dumbbell, lollipop, or horizontal bar |
| Cramped 2×2 with no `h_pad` | `h_pad≥2.0`, `w_pad≥1.5` |
| Rainbow / jet colormap | Sequential Tol colormap or discrete 5-colour max |
| Title centred over panels | Left-aligned `suptitle` or panel subtitles |
| `%` without n | Always show `rate (n=…)` |
| Fake human audit labels | "Automated" watermark on TV figures |

---

## 6. Quality gate checklist (mandatory before commit)

- [ ] Would pass Nature art department first pass?
- [ ] Vector PDF with embedded fonts (`pdf.fonttype=42`)?
- [ ] 600 DPI PNG companion?
- [ ] Panel labels consistent (8 pt bold uppercase, top-left)?
- [ ] No matplotlib default blue/orange?
- [ ] Readable at single-column width (89 mm / 3.5 in)?
- [ ] All numbers match repo JSON (irexp_stats, audit files)?
- [ ] Honest modality labels (band lists ≠ spectra)?
- [ ] No fabricated human audits?
- [ ] Visual proof screenshot at print width inspected?

### Self-rating rubric

| Score | Meaning |
|-------|---------|
| 3/10 | Default matplotlib; cramped; wrong palette |
| 5/10 | Correct data; basic theme; still "script output" |
| 7/10 | Nature-pattern layout; clean typography; minor polish gaps |
| 8–9/10 | Publication-ready programmatic; optional human SVG pass for 9.5+ |
| 10/10 | Requires professional Illustrator pass + journal art desk |

---

## 7. IRexp toolchain (this repo)

```
data/irexp/*.json  +  data/audit/*.json
         │
         ├── nature_design.py     ← locked palette, typography, export
         ├── figstyle.py          ← semantic colours (legacy compat)
         ├── scidata_theme.py     ← matplotlib helpers
         ├── pipeline_svg.py      ← hero schematic (svgwrite)
         └── scidata_export.py    ← Inkscape CLI / cairosvg
                  │
                  ▼
    docs/scientific_data/figures/fig_irexp_*.{pdf,png,svg}
```

**Build:**
```bash
bash scripts/build_all_scidata_figures.sh
python3 scripts/build_scientific_data_pdf.py
```

---

## 8. References

1. Nature NRJ artwork guide — https://www.nature.com/documents/NRJs-guide-to-preparing-final-artwork.pdf  
2. Nature extended data sizing — https://www.nature.com/documents/nature-extended-data.pdf  
3. Paul Tol colour schemes — https://personal.sron.nl/~pault/data/colourschemes.pdf  
4. Wong 2011 (colorblind) — Nature Methods 8, 441  
5. SciFig — https://huggingface.co/papers/2601.04390  
6. AutoFigure — https://arxiv.org/abs/2602.03828  
7. PaperBanana — https://github.com/duanswiyang-ux/PaperBanana  
8. Academic Figure Skill — https://github.com/TingxiYu/academic-figure-skill  
9. Inkscape CLI — https://wiki.inkscape.org/wiki/Using_the_Command_Line  
10. NMRexp — https://doi.org/10.1038/s41597-025-06245-5  
