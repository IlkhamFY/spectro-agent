# IRexp Technical Validation + scale pass (2026-08-27)

**Branch:** `cursor/scidata-accept-ready-9a67`  
**PR:** https://github.com/IlkhamFY/spectro-agent/pull/29  
**Title decision:** keep `IRexp: A database of experimental infrared band lists from open literature` (no count in title; scale deltas go in abstract / Data Records).

---

## Part A — Technical Validation vs NMRexp

NMRexp bar: >99% manual metadata, ~98% skeleton (n≈300), replicate MAE.  
IRexp package: strongest **honest automated** package without fabricating chemist signatures.

### Metrics table

| Check | n | Rate | Automated vs human | Artefact |
|---|---:|---|---|---|
| Transcription fidelity (EPMC re-fetch) | 60 records | 560/560 bands; 60/60 records | **Automated** | `data/audit/extraction_audit.json` |
| Transcription fidelity (enlarged) | 200 records | 2,250/2,261 bands (99.51%); 196/200 records (98.0%) | **Automated** | `data/audit/extraction_audit_n200.json` |
| Extraction-recall proxy (harvest path) | **120** papers | Band confirm 7,981/8,059 (**0.9903**; Wilson [0.9879, 0.9922]); list recall **0.9848** (845/858; Wilson [0.9743, 0.9911]); papers fully recovered 115/120 (0.9583; Wilson [0.9062, 0.9821]) | **Automated** surrogate (not human mark-up) | `data/audit/extraction_recall_proxy_n120.json` |
| Prior recall proxy (archived) | 40 papers | list recall 1.0 | Automated | `data/audit/extraction_recall_proxy.json` |
| Stratified chemist-proxy (joint checks) | **280** | **271/280 (0.9679)**; Wilson [0.9401, 0.9830] | **Automated** chemist-proxy — **not** human expert | `data/audit/chemist_proxy_audit.json` |
| … Chemotion stratum | 42 | 42/42 (1.0) | Automated | same |
| … PMC IR-only | 98 | 97/98 (0.9898) | Automated | same |
| … PMC structure commercial | 98 | 92/98 (0.9388) | Automated | same |
| … PMC structure other licence | 42 | 40/42 (0.9524) | Automated | same |
| … Transcription within proxy sample | 238 PMC records / 2,508 bands | 2,500/2,508 (0.9968); 236/238 records | Automated | same |
| … Structure-physics (RDKit formula gates) | 182 structure-linked | **177/182 (0.9725)** | Automated skeleton-proxy | same |
| Full-corpus quarantine (`irexp_resolved`) | 43,060 | 1,882 flagged (4.37%) | Automated | `data/audit/structure_nmr_quarantine_*` |
| IR window full release | 1,360,866 bands | 0 OOR | Automated | `qc_structure_nmr.json` |
| Human molecular-skeleton audit | — | **Not done** | Human deferred | — |
| Human recall mark-up | — | **Not done** | Human deferred | — |

### Chemist-proxy protocol (summary)

- Script: `scripts/audit_chemist_proxy.py`
- Stratified draw seed=0 over full `irexp.jsonl.gz`: structure-linked commercial / other licence / IR-only / Chemotion.
- Checks: IR window + band-list sanity; RDKit C/H vs ¹³C peak count / ¹H integral; PMC Europe PMC + S3 transcription (±1 cm⁻¹).
- Explicit MS wording: automated ≠ NMRexp human skeleton audit.

### Prior human artefacts

- `data/audit/` expert-elucidation kit + `responses/r-sondhi.json` belong to the **IRSpectra-Bench elucidation** protocol (`docs/EXPERT_AUDIT_PROTOCOL.md`), not IRexp Data Descriptor skeleton audits — cited only as existing human-facing machinery, **not** as IRexp TV rates.

---

## Part B — Scale investigation

| Avenue | Decision | Evidence |
|---|---|---|
| Full PMC re-harvest | **Deferred** | Harvest freeze 2026-06-07; `seen_papers` 188k; live re-esearch drifts. Wall-clock / volume too heavy for this pass without a planned re-cut. |
| Empty→licence recovery via Crossref / late EPMC | **Implemented** | 146 PMCIDs / **1,818** rows promoted; commercial **+928** |
| Chemotion expansion | **No ROI** | Deposit already fully ingested (2,116 → 1,888 after dedup) |
| Snapshot→release drop (~13.6k) | **Not reversed** | Quality/dedup gates; relaxing would add junk |
| SDBS/NIST bulk | **Rejected** | View-only; not redistributable IRexp rows |
| Title count (NMRexp-style) | **Keep current title** | Total still 121,233; commercial +1.1% is valuable but not title-worthy |

### Scale before → after

| Quantity | Before | After | Δ |
|---|---:|---:|---:|
| Total records | 121,233 | 121,233 | 0 |
| PMC / Chemotion | 119,345 / 1,888 | same | 0 |
| Structure-linked | 43,060 | 43,060 | 0 |
| Full IR+¹H+¹³C+structure quadruples | 33,201 | 33,201 | 0 |
| **commercial** | **87,617** | **88,545** | **+928** |
| non_commercial | 20,938 | 21,823 | +885 |
| empty_unknown | 10,781 | 8,963 | −1,818 |
| other (ND) | 0 | 5 | +5 |
| sharealike | 1,897 | 1,897 | 0 |

Policy: promote empty/unknown **only** on explicit CC / ACS AuthorChoice Crossref URLs or non-empty Europe PMC licence; ignore TDM-only links (`data/audit/empty_licence_recovery_summary.json`).

Scripts: `scripts/apply_crossref_licence_recovery.py` (probe JSON already under `data/audit/`).

---

## Part C — Accept strengthening extras

- Overview figure shipped (`fig_irexp_overview`; provenance / pools / composition).
- Counts synced across TeX / MD / NOTICE / HF README / `pmc_licence_summary.json` / `qc_structure_nmr.json`.
- Dual-publication fence clarified in Limitations (Descriptor ≠ companion ICLR results).
- Usage Notes: FAIR reuse example (commercial filter + quarantine drop + attribution).
- Keywords already scrubbed (band lists / FAIR / licence pools).

---

## Remaining human blockers

1. Zenodo **data-only** DOI mint (commercial primary + SA companion) — see `ZENODO_DATA_ONLY_CHECKLIST.md`.  
2. ORCID (esp. Yabbarov) — see `HUMAN_SUBMISSION_CHECKLIST.md`.  
3. Funding / Acknowledgements text.  
4. Optional: true human skeleton audit n≥100; human recall mark-up.

**Closed this finish pass:** HF remirror (commercial 88,545 on Hub); overview figure; stale 87,617 note in `irexp_stats.json`; NOTICE other=5.

---

## PDF

Rebuild: `python3 scripts/build_scientific_data_pdf.py`  
Confirm: title contains **IRexp**; **no** equal-contribution footnote.
