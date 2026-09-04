# IRexp Sci Data — TeX figure competition judgment

Four entries competed (Opus, GPT, Sonnet, Curator) on Nature Portfolio TikZ/PGFPlots figures.

## Rubric (each /10)

| Criterion | Weight |
|-----------|--------|
| Nature art-desk first impression | 25% |
| Editorial clarity of the single job | 20% |
| Data fidelity (frozen JSON) | 25% |
| Print readability @ 183 mm / 89 mm | 15% |
| TeX craft / reproducibility | 15% |

## Scores

| Figure | Opus | GPT | Sonnet | Curator | **Winner** |
|--------|------|-----|--------|---------|------------|
| Positioning (Fig 1) | **9.2** | 8.6 | 7.0 | 8.4 | **Opus** — 3D overview + linear zoom inset solves NMRexp-scale honesty |
| Pipeline (Fig 2) | — | **9.1** | — | 7.8 | **GPT** — numbered stages, Chemotion merge, clean QC cards |
| Distribution (Fig 3) | — | **9.0** | — | 7.5 | **GPT** — colour-encoded panels, log licence bars, watermark |

Sonnet positioning was conceptually strong (log lollipops) but sidebar typography collided.
Curator was solid data-faithful baseline; lost on pipeline packing and hist rendering.
Opus/Sonnet had not finished Figs 2–3 at judgment time.

## Production promotion

| Output | Source |
|--------|--------|
| `figures/fig_irexp_positioning.{pdf,png}` | `competition/opus/` |
| `figures/fig_irexp_pipeline.{pdf,png}` | `competition/gpt/` |
| `figures/fig_irexp_distribution.{pdf,png}` | `competition/gpt/` |

TeX sources archived under `figures/tikz/winning/`.
Rebuild: `bash scripts/build_tikz_scidata_figures.sh`
