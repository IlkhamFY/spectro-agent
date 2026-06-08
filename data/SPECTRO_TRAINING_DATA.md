# IRexp — open experimental IR dataset (+ NMRexp NMR backbone)

**IRexp**: the first open, NMR-paired, **experimental** IR dataset scraped from
the literature — the IR analog of NMRexp (NMR-only) and the open counterpart to
Wiley KnowItAll (closed, IR-only). No synthetic/computed IR; every band list is
what a chemist reported.

## Datasets (gzipped; `gunzip` to use)

| dataset | file | records | IR | NMR | structure |
|---|---|--:|:--:|:--:|:--:|
| **IRexp** | `data/irexp/irexp.jsonl.gz` | **121,233** | real | 87,075 | **42,842** |
| NMRexp backbone | `data/training_nmrexp/train.jsonl.gz` | 100,000 | - | yes | yes |

IRexp schema: { id, ir_bands_cm-1 (real), ir_source:"experimental", h_nmr, c_nmr,
smiles, selfies, inchikey, has_structure, source_doi }.

**40,491 records are full multimodal elucidation triples** (IR + NMR + resolved
structure) — ~6× the entire 6,833-molecule set Spectro was trained on.

## Provenance & quality
- **119,345** records scraped from PMC Open-Access full text (via the AWS PMC-OA
  S3 bucket) + the earlier paper crawl (all **CC-BY**); deduped; quality-gated
  (band-list density gate drops prose false-positives; instrument-range filter;
  >=4 bands). 72% co-report NMR.
- **Structure resolution: 42,842 (35%)**, up from 24%. The bulk corpus is PMC
  *main-text* experimental sections, which label compounds with letter-prefixed
  series labels ("…carbothioamide **(B1)**:") rather than the digit-first "(3a)"
  of SI sections; capturing those labels + cleaning narrative lead-ins/PDF
  artefacts before OPSIN (`scripts/reresolve_structures.py`) lifted resolution
  ~11 points (OPSIN resolved 41,349/55,868 unique in-text names). Re-resolution
  is additive — it matches existing records on the stable content key
  (h_nmr, c_nmr, ir_bands) and only fills smiles/selfies/inchikey.
- **+1,888** records from the **Chemotion FT-IR deposit** (RADAR4Chem, DOI
  `10.22000/OGoEQGlsZGElrgst`, **CC-BY-SA-4.0**) — open electronic-lab-notebook
  spectra: real ATR-IR with author-curated band lists (avg 38 bands) and a
  canonical SMILES, every one structure-resolved. Parsed with the *same*
  extractor + gate as the paper path (`scripts/chemotion_to_irexp.py`), deduped
  by InChIKey (only 8 overlapped the paper corpus). **License note:** these
  carry CC-BY-SA-4.0, distinct from the CC-BY paper core, so they are an additive
  pool here and are **not** blended into the CC-BY release split in
  `data/irexp_release/`.

## How it compares
- vs NMRexp (3.37M, NMR-only): IRexp is the missing IR modality, NMR-paired.
- vs Wiley KnowItAll (250-300k, closed, IR-only): IRexp is ~half the size but
  OPEN, ML-ready, DOI-traceable, and paired with NMR + structure -- usable for
  open multimodal models, which a closed library is not.
- Largest OPEN experimental IR set (closest prior open sources: NIST ~16k,
  Chemotion ~2k — the latter now folded in).

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
  # Chemotion FT-IR deposit (47MB, CC-BY-SA-4.0) -> +1,888 unique molecules:
  #   download DOI 10.22000/OGoEQGlsZGElrgst, extract, then:
  python scripts/chemotion_to_irexp.py   # parses + resolves -> data/chemotion/chemotion_ir.jsonl
