# Remaining work closed — Sci Data finish pass (2026-08-27)

Branch: `cursor/scidata-accept-ready-9a67`  
Companion status: `COMPLETION_STATUS.md` · human path: `HUMAN_SUBMISSION_CHECKLIST.md`

| Was open | Outcome | Evidence / reason |
|---|---|---|
| HF remirror after Crossref (+928 commercial) | **DONE** | `scripts/publish_hf.py` 2026-08-27; Hub README + `pmc_licence_summary.json` show commercial **88,545**; NOTICE remirrored with other=5 |
| MS / release still saying commercial 87,617 | **DONE** | TeX/MD/README_HF/NOTICE/pools already 88,545; fixed stale `irexp_stats.json` note (87617→88545); PEER_REVIEW R2-1 updated |
| Overview figure missing | **DONE** | `scripts/make_fig_irexp_overview.py` → `docs/scientific_data/figures/fig_irexp_overview.{png,pdf}`; embedded in Data Records; no symlinks |
| Unfixed agent-addressable peer-review Majors | **DONE** (prior + this pass) | E9 figure now Fixed; remaining Blockers are human-only |
| Strengthen TV with more automated audits | **Deferred** | Existing pack (n=200 / n=120 / n=280 / full quarantine) is the honest ceiling without human chemist time; no fabricated expert rates |
| Dual-publication fence + honest Code/Data Availability | **DONE** (verified) | Limitations + Zenodo “data-only / not combined `.zenodo.json`” placeholders intact |
| Count consistency TeX / MD / JSON / manifests | **DONE** | Pools sum 121,233; commercial 88,545 everywhere agent-owned |
| Rebuild PDF; Overleaf-safe | **DONE** | `python3 scripts/build_scientific_data_pdf.py`; figures are real files under `docs/scientific_data/figures/` |
| Zenodo data-only DOI | **Still human** | Stub: `ZENODO_DATA_ONLY_CHECKLIST.md` — do not invent DOI |
| ORCID (esp. Yabbarov) | **Still human** | Checklist only; Vargas candidate `0000-0002-5559-6521` marked confirm |
| Funding / Acknowledgements text | **Still human** | Placeholder retained; checklist |
| Expert structure n≥100 / human recall mark-up | **Deferred (human optional)** | Limitations already state the gap vs NMRexp |
| Edit frozen `docs/paper.tex` as Sci Data SoT | **Won’t / must not** | Constraint respected |
| Put IRSpectra-Bench model results into Sci Data | **Won’t** | Fence kept |
| Reintroduce equal-contribution / drop IRexp from title | **Won’t** | Title + author block unchanged |

## Top 3 human actions left

1. Mint **data-only** Zenodo DOI (commercial primary + SA companion).  
2. Confirm ORCID for Yabbarov (+ confirm Vargas).  
3. Supply real funding / Acknowledgements text.
