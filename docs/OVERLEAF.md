# Overleaf manuscripts

Overleaf does not usefully treat Markdown. **Submit / compile `.tex` → PDF.**

| Track | Main TeX (open this in Overleaf) | PDF build | Working notes |
|---|---|---|---|
| Scientific Data (IRexp Data Descriptor) | [`docs/scientific_data/scientific_data.tex`](scientific_data/scientific_data.tex) | `python3 scripts/build_scientific_data_pdf.py` | `SCIENTIFIC_DATA.md` |
| ICLR (IRSpectra-Bench + diagnosis) | [`docs/iclr/iclr_paper.tex`](iclr/iclr_paper.tex) | `python3 scripts/build_iclr_pdf.py` | `ICLR_PAPER.md` |
| Combined archive (do not gut) | [`docs/paper.tex`](paper.tex) | `python3 scripts/build_pdf.py` | `PAPER.md` |

## Quick Overleaf setup

1. New project from GitHub (`IlkhamFY/spectro-agent`) or zip upload of the relevant `docs/` subtree.
2. Menu → **Main document** → the `.tex` path in the table above.
3. **Scientific Data:** XeLaTeX + BibTeX; class is clean `article` (Springer `sn-article` not vendored — see that folder’s README).
4. **ICLR:** pdfLaTeX/XeLaTeX + BibTeX; uses vendored `iclr2026_conference.sty`.
5. Figures live in `docs/figures/`; both manuscripts set `\graphicspath{{figures/}{../figures/}}`.

Do **not** overwrite the combined archive (`docs/paper.tex` / `docs/PAPER.md`) when editing the split tracks.
