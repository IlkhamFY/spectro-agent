# IRexp Scientific Data — Figure Design Brief

**Reference:** Wang et al., *NMRexp: A database of 3.3 million experimental NMR spectra*, Scientific Data 12, 1954 (2025). DOI [10.1038/s41597-025-06245-5](https://doi.org/10.1038/s41597-025-06245-5).

**Manuscript:** `docs/scientific_data/scientific_data.tex`  
**Build:** `bash scripts/build_all_scidata_figures.sh` → `docs/scientific_data/figures/` (real files, no symlinks)  
**Toolchain research:** `docs/scientific_data/FIGURE_TOOL_RESEARCH.md`

---

## 1. NMRexp figure inventory

| Fig | Caption (abridged) | Editorial job | What works |
|-----|-------------------|---------------|------------|
| **1** | Summary of major large NMR databases | **Scale / positioning** — places NMRexp 1–2 orders of magnitude above open NMR peers; implicit novelty claim | Log-scale bar chart; immediate “why this resource matters”; comparator set is explicit |
| **2** | Workflow of Data Extraction and Examples of Cleaning (A pipeline, B removed examples) | **Provenance / methods trust** — shows SI PDF → layout → OCSR → regex/LLM → validation | Two-panel: schematic + concrete failure examples; anchors Methods section visually |
| **3** | Data Distribution Analysis (A nuclei, B solvent, C frequency, D MW vs NMRBank, E elements) + **Table 2** extraction accuracy | **Corpus characterisation + TV headline** — diversity panels plus manual audit table | Multi-panel distribution grid; Table 2 gives reviewer-friendly accuracy numbers |
| **4** | Error analysis across studies and solvents (A–C intra-solvent MAE, D–F cross-solvent) | **Replicate consistency / quality depth** — MAE histograms justify experimental noise model | Only possible at NMRexp scale; strong acceptance signal for ML audience |

**NMRexp figure philosophy:** four figures, each with a single editorial job — positioning, pipeline, corpus shape, replicate error. No decorative charts; every panel answers a reviewer question.

---

## 2. What to adapt for IRexp

| NMRexp pattern | IRexp adaptation | Our figure |
|----------------|------------------|------------|
| Fig 1 database comparison | Honest positioning: **band lists ≠ spectra**; emphasise **redistributability** gap vs SDBS/NIST; NMRexp as modality peer not size competitor | `fig_irexp_positioning` |
| Fig 2 pipeline schematic | PMC-OA S3 plain text + Chemotion ELN → regex extract → OPSIN/RDKit → Europe PMC licence join → pools → release | `fig_irexp_pipeline` |
| Fig 3 composition / pools | Provenance, licence pools, modality cascade (IR → NMR → structure → quadruples) | `fig_irexp_overview` (upgrade) |
| Fig 3 Table 2 + Fig 4 TV | Automated TV only — transcription, recall proxy, chemist-proxy, quarantine; **no fabricated human audits** | `fig_irexp_validation` |

---

## 3. What to skip (NMR-specific or inapplicable)

| NMRexp element | Skip because |
|----------------|--------------|
| Nucleus / solvent / instrument frequency panels | IRexp stores sparse band positions only; no solvent or instrument metadata at scale |
| Replicate MAE histograms (Fig 4) | Sparse IR band lists lack NMR-style replicate density; not claimed |
| OCSR / layout-detection schematic detail | IRexp uses plain-text regex on PMC `.txt`, not SI PDF OCR |
| Human skeleton accuracy table rows | No human expert audit completed; chemist-proxy is automated only |
| Heteronuclei breakdown | NMR modality; IRexp co-reports ¹H/¹³C strings but is IR-first |

---

## 4. IRexp figure plan (shipped set)

### Fig 1 — `fig_irexp_positioning` (Background)

**Job:** Position IRexp in the open IR data landscape without overselling scale.

- Log-scale horizontal bars, grouped by **object type** (band list vs absorbance spectrum vs NMR list).
- Colour: IRexp hero (blue); SDBS/NIST muted + hatch (view-only); NMRexp sky (modality peer).
- Annotations: “bulk redistributable” vs “view-only”; “band lists (cm⁻¹ positions)” vs “absorbance spectra”.
- Numbers: IRexp 121,233 / commercial 88,545 from `irexp_stats.json`; NMRexp 3,370,987 from Wang 2025; SDBS FT-IR ≈54,100 from AIST SDBS introduction (May 2015; approximate).

### Fig 2 — `fig_irexp_pipeline` (Methods)

**Job:** Reproducible provenance flow (NMRexp Fig 2A analogue).

- Six-stage horizontal schematic: Discover → Fetch S3 text → Extract band lists → Resolve structure → Licence join → Pool & release.
- Side branch: Chemotion RADAR4Chem ingest.
- No fake accuracy percentages on the schematic.

### Fig 3 — `fig_irexp_overview` (Data Records)

**Job:** Resource map at a glance (NMRexp Fig 3 composition analogue).

- **(a)** Provenance: PMC OA vs Chemotion.
- **(b)** Licence pools after Crossref recovery (horizontal bars, colour-coded).
- **(c)** Composition cascade: all records → co-reported NMR → structure-linked → full quadruples.
- Data loaded from `data/irexp/irexp_stats.json` + `pmc_licence_summary.json`.

### Fig 4 — `fig_irexp_validation` (Technical Validation)

**Job:** Visual TV summary replacing table-only presentation (NMRexp Table 2 analogue).

- **(a)** Transcription fidelity: band-level and record-level rates (n=60, n=200).
- **(b)** Harvest-path recall proxy (n=120 papers): band confirm, list recall, paper recovery with Wilson 95% CI error bars.
- **(c)** Stratified chemist-proxy pass rates (n=280) by stratum.
- **(d)** Full-corpus quarantine on `irexp_resolved` (43,060 rows).
- Footer note: all checks automated; not NMRexp-parity human audits.
- Data from `docs/scientific_data/qc_structure_nmr.json` and `data/audit/*.json`.

---

## 5. Design system

- **Palette:** `scripts/figstyle.py` (Paul Tol Vibrant; colourblind-safe).
- **Theme:** `scripts/figures/scidata_theme.py` — Scientific Data refinements (panel halos, category bands, donut charts).
- **Export:** `scripts/figures/scidata_export.py` — 600 dpi PNG + vector PDF; Inkscape CLI for SVG schematics.
- **Pipeline schematic:** `scripts/figures/pipeline_svg.py` — programmatic SVG (not matplotlib boxes).
- **Typography:** Liberation Sans (Helvetica-compatible); panel letters 12 pt bold uppercase; body 8 pt.
- **Output:** Vector PDF primary + 600 dpi PNG fallback; pipeline also ships editable `.svg`.
- **Width:** `COL2` (6.30 in) full text width for multi-panel figures.
- **Honesty rules:** never label band lists as spectra; never imply human expert audits; cite external comparator sources in captions.

### Build command

```bash
bash scripts/build_all_scidata_figures.sh
```

Optional human polish: open `fig_irexp_pipeline.svg` in Inkscape desktop for final micro-adjustments.

---

## 6. Manuscript placement

| Figure | Section | Label |
|--------|---------|-------|
| Positioning | Background & Summary (after NMRexp paragraph) | `fig:positioning` |
| Pipeline | Methods (after Discovery and fetch) | `fig:pipeline` |
| Overview | Data Records (existing location, upgraded) | `fig:overview` |
| Validation | Technical Validation (opening) | `fig:validation` |

---

## 7. NMRexp → IRexp mapping (summary)

| NMRexp | IRexp | Status |
|--------|-------|--------|
| Fig 1 scale comparison | `fig_irexp_positioning` | **New** — honest IR gap + redistributability |
| Fig 2 pipeline | `fig_irexp_pipeline` | **New** — PMC S3 + Chemotion path |
| Fig 3 distributions | `fig_irexp_overview` | **Upgraded** — pools + composition |
| Fig 3 Table 2 / Fig 4 MAE | `fig_irexp_validation` | **New** — automated TV only |
| SI cleaning examples | — | **Skipped** — no equivalent visual artefact |
| Replicate MAE | — | **Skipped** — not applicable |

---

## 8. Before / after assessment

| Aspect | Before (default matplotlib) | After (premium toolchain) |
|--------|----------------------------|---------------------------|
| Figure count | 4 basic matplotlib scripts | 4 publication-quality figures |
| Pipeline schematic | matplotlib FancyBboxPatch boxes | **svgwrite SVG** → Inkscape PDF (designed layout) |
| Data charts | Default bar styling | Category bands, bold value labels, waterfall cascade |
| Validation | Basic pie chart | Donut with centre annotation; Wilson CI error bars |
| Typography | Liberation Sans, minimal polish | Panel halos, uppercase letters, restrained grid |
| Export | matplotlib savefig only | PDF + 600 dpi PNG; SVG source for pipeline |
| Headless CI | matplotlib Agg only | Inkscape CLI + cairosvg fallback |
| Reviewer risk | Figures weak / default matplotlib | NMRexp-pattern editorial quality |
| Reproducibility | Four loose scripts | `build_all_scidata_figures.sh` + `scripts/figures/` module |
