# Scientific Data manuscript (Track 2)

**Overleaf source of truth:** [`scientific_data.tex`](scientific_data.tex)  
Markdown [`SCIENTIFIC_DATA.md`](SCIENTIFIC_DATA.md) remains working notes only.

Do **not** edit `docs/archive/`, `docs/PAPER.md`, `docs/paper.tex`, or `scripts/build_pdf.py`.  
See `docs/SPLIT_ORCHESTRATION.md`, `docs/OVERLEAF.md`, and `docs/irexp_scientific_data_audit.md`.

## Overleaf

1. Open / sync the repo (or upload `docs/scientific_data/` plus `docs/figures/`).
2. Set the **main document** to `docs/scientific_data/scientific_data.tex`.
3. Compiler: **pdfLaTeX** (preferred; matches `\documentclass[pdflatex,sn-nature]{sn-jnl}`) or XeLaTeX + **BibTeX**.
4. Bibliography: `references.bib` (Nature-style via vendored `sn-nature.bst`).
5. Figures resolve via `\graphicspath{{figures/}{../figures/}}` (copy `docs/figures` if needed; no symlinks).

**Class:** official Springer Nature journal authoring template **`sn-jnl`**
(December 2024 package), option **`sn-nature`** (Nature Portfolio numbered refs).
Class + `.bst` files are vendored next to this manuscript and under
[`sn-article/`](sn-article/) (see [`sn-article/SOURCE.md`](sn-article/SOURCE.md)).

**Sci Data policy note:** the journal does not require templates at eJP upload and
may ask for a standalone `.tex` at revision. This package is for authoring /
Overleaf review PDFs that match Springer Nature authoring guidance.

## Files

| Path | Role |
|---|---|
| `scientific_data.tex` | **Overleaf / PDF source of truth** (`sn-jnl`) |
| `sn-jnl.cls` + `*.bst` | Vendored Springer Nature class + bibliography styles |
| `sn-article/` | Full Dec 2024 package provenance + sample |
| `SCIENTIFIC_DATA.md` | Working notes (same content; not for Overleaf) |
| `references.bib` | Bibliography (`\bibliography{references}`) |
| `LICENCE_REMEDIATION.md` | Track 1 Europe PMC join narrative + pool counts |
| `qc_structure_nmr.json` | Frozen Technical Validation numbers |
| `scientific_data.pdf` | Local render (`scripts/build_scientific_data_pdf.py`) |
| `PEER_REVIEW_SIMULATION.md` | Simulated Sci Data peer review + remediation checklist |
| `README.md` | This file |

Licence pool artefacts: `data/irexp/licence_pools/`, `data/irexp/pmc_licence_summary.json`.

## Outline (Data Descriptor)

1. Title / authors (both corresponding; no equal-contribution footnote)
2. Abstract (data + reuse only; no LLM bench; ≤~170 words)
3. Background & Summary (NMRexp complementary positioning; agentic reuse)
4. Methods
5. Data Records (commercial **88,545** primary)
6. Technical Validation (+ honest Limitations)
7. Usage Notes
8. Data / Code Availability
9. Author contributions, Competing interests, Acknowledgements, References

Peer-review simulation: [`PEER_REVIEW_SIMULATION.md`](PEER_REVIEW_SIMULATION.md).

## Build PDF

```bash
python3 scripts/build_scientific_data_pdf.py
```

Compiles **`.tex` → PDF** with tectonic (or pdflatex/xelatex + bibtex). Does **not**
touch `docs/paper.pdf` or `scripts/build_pdf.py`.

## Cross-track rules

- No LLM diagnosis / IRSpectra-Bench accuracy / recall–verification claims here.
- Cross-cite the forthcoming ICLR research paper for benchmark protocol and results.
- Cite NMRexp and computational IR–NMR *Scientific Data* peers; foreground band lists.
