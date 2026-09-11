# IRexp Sci Data — TikZ Nature Figure Competition

Produce **Nature Portfolio / Scientific Data** submission-quality figures in **pure TeX (TikZ + PGFPlots)**.

## Deliverables (each agent)

Write under your assigned directory only:

| File | Role |
|------|------|
| `fig_irexp_positioning.tex` | standalone figure (Fig 1) |
| `fig_irexp_pipeline.tex` | standalone figure (Fig 2) |
| `fig_irexp_distribution.tex` | standalone figure (Fig 3) |
| `build.sh` | compiles all three → PDF + PNG @ 600 dpi |
| `NOTES.md` | design rationale + self-score /10 |

Shared assets (do not modify):
- `../nature_style.tex` — palette, fonts, axis styles
- `../frozen_plot_data.json` — **all counts must match this file**

Compile pattern for each figure:
```tex
\documentclass[border=0pt,tikz]{standalone}
\input{../nature_style.tex}  % or correct relative path
\begin{document}\NatureFont
\begin{tikzpicture}...
\end{tikzpicture}
\end{document}
```

Export: `pdflatex` → `pdftoppm -png -r 600`.

## Canvas & type

- Width **183 mm** (Nature double-column). Height ≤ 247 mm.
- Sans-serif Helvetica (`phv` via helvet). Body **7 pt**, panel letters **8 pt bold uppercase**.
- Axes **0.5 pt**; data **0.8–1.0 pt**. Paul Tol / NMRexp blues only (see `nature_style.tex`).
- Vector PDF primary; no raster embeds except optional tiny icons drawn in TikZ.

## Figure jobs

### Fig 1 — Positioning (`fig_irexp_positioning`)
Compare SDBS (~54.1k view-only), NIST (~17k view-only), NMRexp (3,370,987 open-access), IRexp (121,233 this work) with stacks for IRexp: Total / Structure-linked 43,060 / CC-BY/CC0 88,545.
- Prefer **honest linear scale** with callout inset OR break-free design that keeps small bars readable (e.g. log y with clear annotation, or dual encoding).
- Sidebar callout: Large / Redistributable / Traceable.
- Footnote: band lists ≠ absorbance traces.
- Star / “This Work” on IRexp.

### Fig 2 — Pipeline (`fig_irexp_pipeline`)
**(A)** L→R workflow: PMC OA (188,016) → IR extract → Structure resolve → Licence join → Release pools → Final IRexp (121,233 / 43,060). Chemotion (1,888) merges into extract. Cleaning rules inset. JSON snippet on final box.
**(B)** Three QC rejection examples with red highlights (as in manuscript caption / existing SVG).

### Fig 3 — Distribution (`fig_irexp_distribution`)
Panels **a–f** using `frozen_plot_data.json`:
- a Source, b Licence pool, c Modality linkage (hbar)
- d Band-count histogram + PMC median 9
- e Elemental distribution (two-column hbars)
- f 2×2 validation histograms with median + aggregate elbows; watermark “automated checks only”

## Hard honesty rules

- Never call band lists “spectra”.
- Never imply human expert audits.
- Numbers only from `frozen_plot_data.json`.

## Rubric (judge will score)

1. Nature art-desk first impression (typography, whitespace, line weights)
2. Editorial clarity of the single job
3. Data fidelity
4. Print readability at 183 mm and when scaled to 89 mm
5. TeX craft (no overfull boxes, clean code, reproducible build)

Target: **≥ 9/10** programmatic Nature quality.
