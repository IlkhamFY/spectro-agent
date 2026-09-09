# Inventory — what belongs where

## Repo A — IRexp / Scientific Data (data paper only)

| Include | Source in spectro-agent |
|---|---|
| Manuscript TeX + bib + sn-jnl | `docs/scientific_data/scientific_data.tex`, `references.bib`, class/bst |
| Sci Data figures | `docs/scientific_data/figures/fig_irexp_{positioning,pipeline,distribution}.*` |
| Human checklists / licence narrative | `HUMAN_SUBMISSION_CHECKLIST.md`, `LICENCE_REMEDIATION.md`, `ZENODO_DATA_ONLY_CHECKLIST.md` |
| Data manifests + NOTICE | `data/NOTICE`, licence/release **stats JSON**, HF README |
| Build script | adapted `scripts/build_scientific_data_pdf.py` |

| Exclude | Reason |
|---|---|
| Full `*.jsonl.gz` dumps | Size; point to HF `ilkhamfy/IRexp` + Zenodo (DOI TBD) |
| `PEER_REVIEW_SIMULATION.md`, figure-agent playbooks | Agent meta |
| ICLR tex / bench diagnosis tables | Fence |

## Repo B — IRSpectra-Bench / ICLR (research paper only)

| Include | Source in spectro-agent |
|---|---|
| Manuscript TeX + ICLR style | `docs/iclr/*` |
| Cited figures | `docs/figures/` stems used in `iclr_paper.tex` |
| Bench docs | `docs/LEADERBOARD.md`, `BENCHMARK.md`, `SUBMISSION.md` |
| Build script | adapted `scripts/build_iclr_pdf.py` |

| Exclude | Reason |
|---|---|
| Sci Data sn-jnl / licence pools | Fence |
| Combined ChemRxiv `paper.tex` | Archive only in monorepo |

## Identity notes

- GitHub owner: **IlkhamFY** (`https://github.com/IlkhamFY/spectro-agent`)
- Human commit emails seen: `ilkhamfy@gmail.com`, `122471854+IlkhamFY@users.noreply.github.com`
- Pack commits authored as: **Ilkham Yabbarov \<ilkhamfy@gmail.com\>**
- Agent/`gh` token cannot create new repos or call `GET /user` (403); push instructions left for the human account
