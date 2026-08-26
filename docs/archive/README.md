# Frozen combined manuscript (Track 0)

Snapshot of the pre-split JCIM-shaped **combined** paper (IRexp + IRSpectra-Bench + LLM diagnosis), frozen when the Sci Data / ICLR split started.

| Path | Source | Role |
|------|--------|------|
| `combined_PAPER.md` | `docs/PAPER.md` at freeze | Authoring source |
| `combined_paper.tex` | `docs/paper.tex` at freeze | Pandoc TeX reading copy |
| `../paper.pdf` | live path, unchanged | Combined reading-copy PDF (still built from `docs/PAPER.md` via `scripts/build_pdf.py`) |

**Rules for other tracks**

- Treat this directory as **read-only archive**. Do not edit these files.
- Do not edit `docs/PAPER.md`, `docs/paper.tex`, or repoint `scripts/build_pdf.py` as part of the split manuscripts.
- New manuscripts live under `docs/scientific_data/` (T2) and `docs/iclr/` (T3).
- See `docs/SPLIT_ORCHESTRATION.md` for the multi-agent plan.

Freeze commit / branch: `cursor/split-orchestration-9a67` (Track 0).
