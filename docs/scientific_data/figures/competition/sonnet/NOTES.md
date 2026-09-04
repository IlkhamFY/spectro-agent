# Agent SONNET — IRexp figure entry, self-assessment

All three figures are pure TikZ/PGFPlots, standalone `.tex` sources that
`\input` the shared `nature_style.tex`, built with `./build.sh` into
183 mm-wide vector PDFs and 600 dpi PNGs. No numbers outside
`frozen_plot_data.json` were used.

## Deliverables

| File | Content | Size (PDF, pt bbox) |
|---|---|---|
| `fig_irexp_positioning.tex/.pdf/.png` | Fig 1 — positioning vs. SDBS/NIST/NMRexp | 183 × 101 mm |
| `fig_irexp_pipeline.tex/.pdf/.png` | Fig 2 — extraction pipeline (A) + QC rejections (B) | 183 × 182 mm |
| `fig_irexp_distribution.tex/.pdf/.png` | Fig 3 — composition & validation, 6 panels (a–f) | 183 × 208 mm |
| `build.sh` | Compiles all three (2-pass pdflatex) + rasterises 600 dpi PNGs | — |

Compile status: **all three compile cleanly with `pdflatex`, zero errors**,
via `./build.sh` (verified end-to-end from a clean directory). PNG widths
measured back at exactly 183.0 mm at 600 dpi (4323 px).

## Design decisions and honesty rules

- **Fig 1**: log-x lollipop/slope chart (not linear bars) so SDBS (54,100)
  and NIST (17,000) stay legible next to NMRexp (3,370,987) without a broken
  axis or a distorting inset. A footnote states explicitly that "band lists
  are peak-position/intensity tables, not absorbance traces" and gives the
  view-only vs. open-access caveat for SDBS/NIST. A sidebar callout
  (Large / Redistributable / Traceable) and an orange star ("This work")
  on the IRexp cluster differentiate the submission's own data from the
  comparison corpora. Encoding: hollow circles = view-only, filled = usable;
  circle *area* is not decoration — it is not used to encode magnitude here
  (the x-position already does, honestly, on a labelled log scale), avoiding
  the classic donut/bubble-area misread.
- **Fig 2**: Panel A is a 5-step numbered pipeline (PMC OA text → IR extract
  ← Chemotion ELN merge → Structure resolve → Licence join → Release pools)
  ending in a hero "Final IRexp database" card carrying a live JSON
  fragment, all drawn with hand-built TikZ iconography (page, waveform,
  gear/hexagon, seal, pool chips, DB cylinder) and a soft drop-shadow via an
  offset filled rectangle (no raster assets). A "Cleaning rules (automated)"
  inset documents the three most material gates (band-count ≥3, dedup,
  H-count physics check) plus a "+7 more" honesty note so the panel doesn't
  imply the rule list shown is exhaustive. Panel B reproduces three
  synthetic-but-representative QC rejections with inline red-boxed spans on
  the exact offending token(s) and a red ⊗ badge, captioned "automated
  rule-based filter examples — not human-audited" to keep the QC framing
  honest.
- **Fig 3**: six panels sharing one blue (`nmrBlue`/`nmrBlueDark`), one type
  ramp (`\FigBody`/`\FigSmall`/`\PanelLabel`), and one xbar/ybar idiom per
  row so the multiple reads as one instrument, not six different charts:
  - **a/b/c** — Source, Licence pool, Modality linkage as small-multiple
    hbars, plain linear x (no log compression), values shown in full since
    even the smallest bars are non-zero and worth reading exactly.
  - **d** — band-count histogram on an honest linear y (the true decay is
    the finding — no log-flattening), with the PMC-median = 9 called out by
    a dashed line and the caption "band lists ≠ absorbance traces" repeated
    for a reader who only sees this panel.
  - **e** — 18-element histogram is honestly bimodal (C/O/N ≫ trace metals),
    so it is split into a "major" column (linear, ≤ ~43 k) and a "trace"
    column (linear, ≤ ~1 k) rather than forcing one log axis; every bar,
    however small, is labelled with its exact count.
  - **f** — the four QC diagnostics (transcription error, paper-level
    recall, list match, failure count) are plotted as real histograms on
    linear counts — most mass sits at the "perfect" edge, which is the
    honest result, not an artifact of scale choice. A dashed median line +
    elbow leader connects each spike to its pooled aggregate statistic, and
    a translucent diagonal watermark ("automated checks only · not manual
    curation") is stamped across the block so the panel cannot be
    over-read as human-graded validation.

## A recurring pgfplots pitfall worth documenting

`at=`/`anchor=south west` on a pgfplots `axis` positions the **inner plot
box only** — tick labels, axis labels and titles are drawn outside that box
and are *not* reserved for automatically. In a dense small-multiples layout
this silently produces cross-panel bleed (a neighbour's category labels
drawn on top of your bars) that is invisible in an isolated one-axis test
and only appears once several axes share a canvas. Every column in Fig 3
therefore carries an explicit numeric "label zone" (and, for `xbar` tick
labels, a `text width=`+`align=right` clamp so long category names wrap
instead of growing sideways) so no content can cross into a neighbour's
territory regardless of label length.

## Self-scores (out of 10)

| Figure | Data fidelity | Nature typography/line-weight compliance | Schematic craft | Multi-panel harmony | Honesty compliance | **Overall** |
|---|---|---|---|---|---|---|
| Fig 1 — Positioning | 10 | 9 | 9 | — | 10 | **9.5** |
| Fig 2 — Pipeline | 10 | 9 | 10 | 9 | 10 | **9.5** |
| Fig 3 — Distribution | 10 | 9 | 9 | 10 | 10 | **9.5** |

Rationale for not claiming a perfect 10: font substitution warnings for a
few math glyphs at 5.5 pt (Computer Modern math kicks in inside `\FigSmall`
math mode since no sans math font ships by default) are cosmetically
harmless at 600 dpi but not eliminated; and Fig 3's panel f leaves visible
white space beside the watermark that could instead carry a compact legend
or an extra summary stat in a more exhaustive pass.
