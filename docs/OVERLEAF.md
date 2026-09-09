# Overleaf manuscripts

Overleaf does not usefully treat Markdown. **Submit / compile `.tex` → PDF.**

## Preferred: clean single-paper repos

Use the dedicated repositories (see `docs/paper_repos/`) once pushed:

| Paper | Suggested GitHub repo | Main TeX | Compiler | Overleaf zip |
|---|---|---|---|---|
| Scientific Data (IRexp) | `IlkhamFY/IRexp` | `scientific_data.tex` | pdfLaTeX | `artifacts/paper_repos/IRexp-overleaf.zip` |
| ICLR (IRSpectra-Bench) | `IlkhamFY/IRSpectra-Bench` | `iclr_paper.tex` | pdfLaTeX | `artifacts/paper_repos/IRSpectra-Bench-overleaf.zip` |

**Setup (each paper):** New Project → Import from GitHub (preferred) or zip upload → set Main document → pdfLaTeX.  
No git symlinks in the clean packs. Do not upload large `jsonl.gz` dumps to Overleaf.

Details: `docs/paper_repos/README.md`, `docs/paper_repos/PUSH_INSTRUCTIONS.md`, and each pack’s `OVERLEAF.md`.

## Legacy: this monorepo (`spectro-agent`)

Still works if you sync the full repo; prefer the clean repos for tidy Overleaf projects.

| Track | Main TeX (open this in Overleaf) | Template | PDF build |
|---|---|---|---|
| Scientific Data | [`docs/scientific_data/scientific_data.tex`](scientific_data/scientific_data.tex) | Official Springer Nature **`sn-jnl`** (`[pdflatex,sn-nature]`; class + `.bst` vendored in `docs/scientific_data/`) | `python3 scripts/build_scientific_data_pdf.py` |
| ICLR | [`docs/iclr/iclr_paper.tex`](iclr/iclr_paper.tex) | Official **ICLR 2026** (`iclr2026_conference.sty` + `.bst`, vendored) | `python3 scripts/build_iclr_pdf.py` |
| Combined archive | [`docs/paper.tex`](paper.tex) | Custom two-column ChemRxiv-style (`scripts/build_pdf.py`) | `python3 scripts/build_pdf.py` |

### Quick Overleaf setup (monorepo)

1. New project from GitHub (`IlkhamFY/spectro-agent`) or zip upload of the relevant `docs/` subtree.
2. Menu → **Main document** → the `.tex` path in the table above.
3. **Scientific Data:** pdfLaTeX (preferred) or XeLaTeX + BibTeX; uses vendored
   `sn-jnl.cls` and `sn-nature.bst` in `docs/scientific_data/` (see
   `docs/scientific_data/sn-article/SOURCE.md`). *Scientific Data* does not
   require this template at eJP upload — use for authoring/review; flatten to a
   standalone `.tex` at revision if the journal requests it.
4. **ICLR:** pdfLaTeX/XeLaTeX + BibTeX; uses vendored `iclr2026_conference.sty`.
5. Figures live in `docs/figures/` only (no symlinks — Overleaf rejects them). Both
   manuscripts set `\graphicspath{{../figures/}{figures/}}` so compiles work from
   `docs/scientific_data/` or `docs/iclr/` when the full repo is synced.

Do **not** overwrite the combined archive (`docs/paper.tex` / `docs/PAPER.md`) when editing the split tracks.
