# Zenodo data-only mint checklist (human)

**Do not invent a DOI.** Fill this after minting; then replace `[TODO: 10.5281/zenodo.XXXXXXX]` in `scientific_data.tex` / `SCIENTIFIC_DATA.md`.

## Why a separate deposit

Repo-root `.zenodo.json` describes a **combined** research archive (IRexp **+** IRSpectra-Bench + model artefacts). Scientific Data archival must be a **data-only** IRexp deposit. Do **not** reuse that combined metadata as the Sci Data record.

## Files to upload

| Priority | File | Licence metadata | Notes |
|---|---|---|---|
| Primary | `data/irexp/licence_pools/irexp_commercial.jsonl.gz` (88,545) | `cc-by-4.0` (deposit metadata) | Zenodo / Sci Data primary artifact |
| Companion | `data/irexp/licence_pools/irexp_sharealike.jsonl.gz` (1,897) | CC-BY-SA-4.0 | Chemotion + rare PMC SA; description must say ShareAlike |
| Optional / labelled | `irexp_non_commercial.jsonl.gz` (21,823) | NC* — not commercial | Hold aside; clear label |
| Optional / labelled | `irexp_empty_unknown.jsonl.gz` (8,963) | unresolved | Excluded from commercial primary |
| Optional / labelled | `irexp_other.jsonl.gz` (5) | CC-BY-ND | Held aside |
| Docs | `data/NOTICE`, `docs/scientific_data/LICENCE_REMEDIATION.md`, `pmc_licence_summary.json` | — | Provenance |

Do **not** upload IRSpectra-Bench predictions, leaderboards, or model-result tables into this Sci Data deposit.

## Suggested title / description stubs

- **Title:** `IRexp: experimental infrared band lists from open literature (data release)`
- **Creators:** Ilkham Yabbarov; Rodrigo A. Vargas-Hernández (ORCID when confirmed)
- **Description (skeleton):** Redistributable experimental IR **band lists** (cm⁻¹), not absorbance traces. Full research corpus is multi-licence; this deposit’s primary file is the commercial CC-BY/CC0 pool (88,545). ShareAlike companion is separate. NC* and empty/unknown are excluded from the commercial artifact (optional labelled files only). See LICENCE_REMEDIATION.md. Companion ICLR/IRSpectra-Bench results are **out of scope**.
- **Related identifiers:** GitHub `IlkhamFY/spectro-agent`; HF `ilkhamfy/IRexp`; forthcoming Sci Data Data Descriptor; companion research manuscript (cross-cite, no results).

## After mint

1. Paste DOI into TeX Access + Data Availability and MD TODOs.  
2. Tag the Git commit that matches the uploaded files.  
3. Update HF card Zenodo line if desired.  
4. Tick the matching row in `HUMAN_SUBMISSION_CHECKLIST.md`.
