# ICLR track (T3) — IRSpectra-Bench + recall/verification diagnosis

**Overleaf source of truth:** [`iclr_paper.tex`](iclr_paper.tex)  
Markdown [`ICLR_PAPER.md`](ICLR_PAPER.md) remains working notes only.

This directory holds the **ICLR-facing research paper** (**Track 3** in
`docs/SPLIT_ORCHESTRATION.md`). It is **not** a Data Descriptor and does not replace
`docs/PAPER.md` or `docs/paper.tex`. See also `docs/OVERLEAF.md`.

## Overleaf

1. Open / sync the repo (or upload `docs/iclr/` plus `docs/figures/`).
2. Set the **main document** to `docs/iclr/iclr_paper.tex`.
3. Compiler: **pdfLaTeX** or **XeLaTeX** + **BibTeX**.
4. Style: vendored `iclr2026_conference.sty` (+ `fancyhdr.sty`, `natbib.sty`,
   `iclr2026_conference.bst`) from the [ICLR Master-Template](https://github.com/ICLR/Master-Template).
5. Keep `\iclrfinalcopy` **commented** for anonymous review; uncomment for camera-ready.
6. Figures: `\graphicspath{{figures/}{../figures/}}` (symlink `figures → ../figures` in this dir).

| file | role |
|---|---|
| [`iclr_paper.tex`](iclr_paper.tex) | **Overleaf / PDF source of truth** |
| [`ICLR_PAPER.md`](ICLR_PAPER.md) | Working notes draft |
| `references.bib` | Track bibliography (includes Sci Data companion cite) |
| `iclr2026_conference.sty` / `.bst` | ICLR 2026 conference style |
| `fancyhdr.sty`, `natbib.sty` | Style dependencies (vendored) |
| `iclr_paper.pdf` | Local render (`scripts/build_iclr_pdf.py`) |
| `../archive/combined_PAPER.md` | Frozen pre-split combined paper (T0; read-only) |
| `../PAPER.md` / `../paper.tex` | Live combined archive — **do not edit** for this track |
| `../scientific_data/` | Sci Data Data Descriptor (T2) |

**Venue plan:** *Scientific Data* (IRexp Data Descriptor) + **ICLR** (this paper). Prefer
Sci Data first (or simultaneous), then ICLR citing the Sci Data / Zenodo / HF identifier.
See `docs/SUBMISSION.md`.

## Build PDF

```bash
python3 scripts/build_iclr_pdf.py
```

Compiles **`.tex` → PDF**. Does **not** touch `docs/paper.pdf`.

## Section outline

1. Abstract — IRSpectra-Bench; 28% / 15% reweighted; recall 34% vs precision 89%
2. §1 Introduction — factorisation; contributions; short IRexp pointer
3. §2 Related work
4. §3 IRSpectra-Bench — task, difficulty, scoring contract
5. §4 Experimental setup
6. §5 Results (headline, contamination, cross-vendor, forward-verify, literature decomp)
7. §6 Discussion — reporting contract
8. §7 Limitations
9. §8 Conclusion
10. Reproducibility / Ethics
11. Appendix — IRexp pointer + shared figure list

## Dual-publication boundary (summary)

**ICLR owns:** bench protocol, diagnosis numbers, contamination/cross-vendor, forward-verify.  
**Sci Data owns:** IRexp Methods / Data Records / Technical Validation / licence pools.  
**Allowed pointer:** cite companion Data Descriptor~\citep{yabbarov2026irexp}; record counts + HF.

### Must **not** happen

- Identical abstract/title across Sci Data and ICLR
- Sci Data paper that rehashes LLM diagnosis tables
- ICLR paper that embeds full mining Methods / Data Records

## Source & editing rules

- **Write** under `docs/iclr/` (plus light `docs/SUBMISSION.md` / `docs/OVERLEAF.md` notes).
- **Do not edit** `docs/paper.tex` or gut `docs/PAPER.md`.
- **Do not delete** `docs/PAPER.md` or `docs/archive/combined_PAPER.md`.
