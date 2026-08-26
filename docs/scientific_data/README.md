# Scientific Data manuscript (Track 2)

**Owned by T2.** Primary source: `SCIENTIFIC_DATA.md`.

Do **not** edit `docs/archive/`, `docs/PAPER.md`, `docs/paper.tex`, or `scripts/build_pdf.py`.  
See `docs/SPLIT_ORCHESTRATION.md` and `docs/irexp_scientific_data_audit.md`.

## Files

| Path | Role |
|---|---|
| `SCIENTIFIC_DATA.md` | Nature *Scientific Data* Data Descriptor (authoring source) |
| `LICENCE_REMEDIATION.md` | Track 1 Europe PMC join, counts, HF/Zenodo policy |
| `references.bib` | Bibliography for this Descriptor |
| `qc_structure_nmr.json` | Frozen Technical Validation numbers (structure–NMR + IR window) |
| `scientific_data.pdf` | Optional local render |
| `README.md` | This file |

## Outline

1. Title (≤110 chars; no colon spam; no “AI-ready”)
2. Abstract (≤170 words; data + reuse only)
3. Background & Summary
4. Methods (PMC-OA S3 + Chemotion; band lists; OPSIN; provenance; licence stamps)
5. Data Records (schema, files, counts; licence pools)
6. Technical Validation (transcription 560/560 n=60; structure–NMR sample; IR window)
7. Usage Notes
8. Data Availability (HF + Zenodo TODO)
9. Code Availability

## Track 1 licence remediation — landed

- Per-PMCID Europe PMC join stamped into `data/irexp/irexp.jsonl.gz`
- Segregated pools under `data/irexp/licence_pools/` (commercial 87,617 / NC 20,938 / empty 10,781 / SA 1,897)
- Details: `LICENCE_REMEDIATION.md`

## Build PDF (optional)

```bash
python3 scripts/build_scientific_data_pdf.py
```

Does **not** touch `docs/paper.pdf` or `scripts/build_pdf.py`.

## Cross-track rules

- No LLM diagnosis / IRSpectra-Bench accuracy / recall–verification claims here.
- Cross-cite the forthcoming ICLR research paper for benchmark protocol and results.
- Cite NMRexp and computational IR–NMR *Scientific Data* peers; foreground band lists.
