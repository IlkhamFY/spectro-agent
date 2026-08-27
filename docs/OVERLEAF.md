# Overleaf manuscripts

Overleaf does not usefully treat Markdown. **Submit / compile `.tex` → PDF.**

| Track | Main TeX (open this in Overleaf) | Template | PDF build |
|---|---|---|---|
| Scientific Data | [`docs/scientific_data/scientific_data.tex`](scientific_data/scientific_data.tex) | Clean `article` (section order only). **Not** official Springer `sn-article` — swap at submission. | `python3 scripts/build_scientific_data_pdf.py` |
| ICLR | [`docs/iclr/iclr_paper.tex`](iclr/iclr_paper.tex) | Official **ICLR 2026** (`iclr2026_conference.sty` + `.bst`, vendored) | `python3 scripts/build_iclr_pdf.py` |
| Combined archive | [`docs/paper.tex`](paper.tex) | Custom two-column ChemRxiv-style (`scripts/build_pdf.py`) | `python3 scripts/build_pdf.py` |

## Quick Overleaf setup

1. New project from GitHub (`IlkhamFY/spectro-agent`) or zip upload of the relevant `docs/` subtree.
2. Menu → **Main document** → the `.tex` path in the table above.
3. **Scientific Data:** XeLaTeX + BibTeX; class is clean `article` (Springer `sn-article` not vendored — see that folder’s README).
4. **ICLR:** pdfLaTeX/XeLaTeX + BibTeX; uses vendored `iclr2026_conference.sty`.
5. Figures live in `docs/figures/` only (no symlinks — Overleaf rejects them). Both
   manuscripts set `\graphicspath{{../figures/}{figures/}}` so compiles work from
   `docs/scientific_data/` or `docs/iclr/` when the full repo is synced.

Do **not** overwrite the combined archive (`docs/paper.tex` / `docs/PAPER.md`) when editing the split tracks.
