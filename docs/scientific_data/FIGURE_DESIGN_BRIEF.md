# IRexp Scientific Data — Figure Design Brief

**Reference:** Wang et al., *NMRexp*, Scientific Data 12:1954 (2025). DOI [10.1038/s41597-025-06245-5](https://doi.org/10.1038/s41597-025-06245-5).

**Manuscript:** `docs/scientific_data/scientific_data.tex`  
**Build:** `bash scripts/build_tikz_scidata_figures.sh` (TikZ winners) or `bash scripts/build_all_scidata_figures.sh`  
**Agent playbook:** `docs/scientific_data/FIGURE_AGENT_PLAYBOOK.md`  
**Toolchain research:** `docs/scientific_data/FIGURE_TOOL_RESEARCH.md`  
**Competition judgment:** `docs/scientific_data/figures/tikz/JUDGMENT.md`

---

## Design rationale (TikZ Nature rebuild)

Multi-agent TeX competition (Opus / GPT / Sonnet / Curator). Production figures are pure TikZ/PGFPlots vector PDFs at 183 mm with Helvetica-class type and Paul Tol / NMRexp palette.

| Figure | Winner | Engine | Key design choices |
|--------|--------|--------|-------------------|
| `fig_irexp_positioning` | Opus | TikZ | 3D overview + linear zoom inset; honest small-bar readability |
| `fig_irexp_pipeline` | GPT | TikZ | Numbered stage badges; Chemotion merge; schematic QC cards |
| `fig_irexp_distribution` | GPT | TikZ | Colour-encoded a–f grid; log licence bars; automated watermark |

Legacy matplotlib/svg generators remain under `scripts/make_fig_irexp_*.py` for reference.

---

## Manuscript placement

| Figure | Section | Label |
|--------|---------|-------|
| Positioning | Background & Summary | `fig:positioning` |
| Pipeline | Methods | `fig:pipeline` |
| Overview | Data Records | `fig:overview` |
| Validation | Technical Validation | `fig:validation` |
