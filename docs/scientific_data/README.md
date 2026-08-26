# Scientific Data manuscript (Track 2)

**Owned by T2.** Primary source: `SCIENTIFIC_DATA.md`.

Do **not** edit `docs/archive/`, `docs/PAPER.md`, `docs/paper.tex`, or `scripts/build_pdf.py`.  
See `docs/SPLIT_ORCHESTRATION.md` and `docs/irexp_scientific_data_audit.md`.

## Files

| Path | Role |
|---|---|
| `SCIENTIFIC_DATA.md` | Nature *Scientific Data* Data Descriptor (authoring source) |
| `LICENCE_REMEDIATION.md` | Track 1 Europe PMC join narrative, policy, confirmed pool counts |
| `references.bib` | Bibliography for this Descriptor |
| `qc_structure_nmr.json` | Frozen Technical Validation numbers (structure–NMR + IR window) |
| `scientific_data.pdf` | Optional local render |
| `README.md` | This file |

Licence pool artefacts (repo data, not under this dir): `data/irexp/licence_pools/`, `data/irexp/pmc_licence_summary.json`.

## Outline

1. Title (≤110 chars; no colon spam; no “AI-ready”)
2. Abstract (≤170 words; data + reuse only)
3. Background & Summary
4. Methods (PMC-OA S3 + Chemotion; band lists; OPSIN; provenance; confirmed licence pools)
5. Data Records (schema, files, counts; commercial **87,617** primary)
6. Technical Validation (transcription 560/560 n=60; structure–NMR sample; IR window)
7. Usage Notes
8. Data Availability (HF + Zenodo TODO)
9. Code Availability

## Track 1 status (done on `main`)

Confirmed pool counts (total 121,233 unchanged):

| Pool | Records | Role |
|---|---:|---|
| commercial (CC-BY + CC0) | **87,617** | Zenodo / Sci Data primary |
| non_commercial (NC*) | 20,938 | held aside |
| sharealike | 1,897 | Chemotion + rare PMC SA |
| empty_unknown | 10,781 | excluded from commercial |

Detail: `LICENCE_REMEDIATION.md` · pools: `data/irexp/licence_pools/`.

## Remaining (not T2 manuscript blockers)

- Hugging Face remirror (`HF_TOKEN` + `scripts/publish_hf.py`)
- Zenodo DOI mint (human)
- ORCID / funding (human)
- Light polish before submission

## Build PDF (optional)

```bash
python3 scripts/build_scientific_data_pdf.py
```

Does **not** touch `docs/paper.pdf` or `scripts/build_pdf.py`.

## Cross-track rules

- No LLM diagnosis / IRSpectra-Bench accuracy / recall–verification claims here.
- Cross-cite the forthcoming ICLR research paper for benchmark protocol and results.
- Cite NMRexp and computational IR–NMR *Scientific Data* peers; foreground band lists.
