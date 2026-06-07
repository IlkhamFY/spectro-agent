# IRexp — open experimental IR dataset (+ NMRexp NMR backbone)

**IRexp**: the first open, NMR-paired, **experimental** IR dataset scraped from
the literature — the IR analog of NMRexp (NMR-only) and the open counterpart to
Wiley KnowItAll (closed, IR-only). No synthetic/computed IR; every band list is
what a chemist reported.

## Datasets (gzipped; `gunzip` to use)

| dataset | file | records | IR | NMR | structure |
|---|---|--:|:--:|:--:|:--:|
| **IRexp** | `data/irexp/irexp.jsonl.gz` | **119,345** | real | 87,075 | 28,088 |
| NMRexp backbone | `data/training_nmrexp/train.jsonl.gz` | 100,000 | - | yes | yes |

IRexp schema: { id, ir_bands_cm-1 (real), ir_source:"experimental", h_nmr, c_nmr,
smiles, selfies, inchikey, has_structure, source_doi }.

## Provenance & quality
- Scraped from PMC Open-Access full text (via the AWS PMC-OA S3 bucket) + the
  earlier paper crawl; deduped; quality-gated (band-list density gate drops prose
  false-positives; instrument-range filter; >=4 bands).
- 119,345 real experimental IR band lists; 73% co-report NMR; 28,088 resolved to
  structure (OPSIN from in-text names).

## How it compares
- vs NMRexp (3.37M, NMR-only): IRexp is the missing IR modality, NMR-paired.
- vs Wiley KnowItAll (250-300k, closed, IR-only): IRexp is ~half the size but
  OPEN, ML-ready, DOI-traceable, and paired with NMR + structure -- usable for
  open multimodal models, which a closed library is not.
- Largest OPEN experimental IR set (closest prior open source: NIST ~16k).

## Honest ceiling
The high-yield characterization corpus (papers reporting "IR (KBr)/FT-IR(/νmax")
yields ~0.58 clean IR/paper and is mined out at ~119k. The broader cm-1/infrared
corpus (~300-580k papers) is largely materials/physics prose that yields ~0 real
per-compound IR after filtering. So ~120k is the practical open text-extractable
ceiling; reaching 250k would require SI-spectra image-OCR (curves, multi-week) or
licensed data -- not open text-extractable IR.

## Reproduce
  python scripts/s3_ir_harvest.py --target 250000 --out data/irexp   # PMC-OA S3 crawl
  python scripts/build_irexp.py --sources data/bulk/spectra.jsonl data/irexp/ir.jsonl --out data/irexp
