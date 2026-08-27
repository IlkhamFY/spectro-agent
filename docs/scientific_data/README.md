# Scientific Data manuscript (Track 2)

**Overleaf source of truth:** [`scientific_data.tex`](scientific_data.tex)  
Markdown [`SCIENTIFIC_DATA.md`](SCIENTIFIC_DATA.md) remains working notes only.

Do **not** edit `docs/archive/`, `docs/PAPER.md`, `docs/paper.tex`, or `scripts/build_pdf.py`.  
See `docs/SPLIT_ORCHESTRATION.md`, `docs/OVERLEAF.md`, and `docs/irexp_scientific_data_audit.md`.

## Overleaf

1. Open / sync the repo (or upload `docs/scientific_data/` plus `docs/figures/`).
2. Set the **main document** to `docs/scientific_data/scientific_data.tex`.
3. Compiler: **XeLaTeX** (or pdfLaTeX) + **BibTeX**. Bibliography: `references.bib`.
4. Figures resolve via `\graphicspath{{figures/}{../figures/}}` (symlink or copy `docs/figures`).

**Class choice:** clean single-column `article` (11pt, A4, 1-inch margins)
approximating a Nature *Scientific Data* Data Descriptor section order.
The official Springer Nature **`sn-article`** / *Scientific Data* LaTeX template is
**not** vendored here — download from Springer Nature when preparing the final
submission package and re-wrap this content. Until then this file is for Overleaf
reading copies and internal review.

## Files

| Path | Role |
|---|---|
| `scientific_data.tex` | **Overleaf / PDF source of truth** |
| `SCIENTIFIC_DATA.md` | Working notes (same content; not for Overleaf) |
| `references.bib` | Bibliography (`\bibliography{references}`) |
| `LICENCE_REMEDIATION.md` | Track 1 Europe PMC join narrative + pool counts |
| `qc_structure_nmr.json` | Frozen Technical Validation numbers |
| `scientific_data.pdf` | Local render (`scripts/build_scientific_data_pdf.py`) |
| `README.md` | This file |

Licence pool artefacts: `data/irexp/licence_pools/`, `data/irexp/pmc_licence_summary.json`.

## Outline (Data Descriptor)

1. Title / authors (daggers for corresponding emails — match combined `paper.tex`)
2. Abstract (data + reuse only; no LLM bench)
3. Background & Summary
4. Methods
5. Data Records (commercial **87,617** primary)
6. Technical Validation
7. Usage Notes
8. Data / Code Availability
9. Author contributions, Competing interests, Acknowledgements, References

## Build PDF

```bash
python3 scripts/build_scientific_data_pdf.py
```

Compiles **`.tex` → PDF** with tectonic (or xelatex+bibtex). Does **not** touch
`docs/paper.pdf` or `scripts/build_pdf.py`.

## Cross-track rules

- No LLM diagnosis / IRSpectra-Bench accuracy / recall–verification claims here.
- Cross-cite the forthcoming ICLR research paper for benchmark protocol and results.
- Cite NMRexp and computational IR–NMR *Scientific Data* peers; foreground band lists.
