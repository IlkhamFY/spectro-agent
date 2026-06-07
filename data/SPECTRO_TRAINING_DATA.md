# IRexp — open experimental IR dataset (+ NMRexp NMR backbone)

The contribution: **IRexp**, the first open, NMR-paired, **experimental** IR
dataset scraped from the literature — the IR analog of NMRexp (NMR-only) and the
open counterpart to Wiley KnowItAll (closed, IR-only). **No synthetic/computed
IR** — every band list is what a chemist reported.

## Datasets (gzipped in repo; `gunzip` to use)

| dataset | file | records | IR | NMR | structure |
|---|---|--:|:--:|:--:|:--:|
| **IRexp** (the contribution) | `data/irexp/irexp.jsonl.gz` | **46,612** | real | 46,090 | 14,357 |
| NMRexp backbone (NMR+structure) | `data/training_nmrexp/train.jsonl.gz` | 100,000 | - | yes | yes |
| IR triples (subset, fully complete) | `data/training_ir/train.jsonl.gz` | 6,981 | real | yes | yes |

### IRexp record schema
{ id, ir_bands_cm-1: [3318,1704,...] (REAL experimental), ir_source:"experimental",
  h_nmr, c_nmr, smiles, selfies, inchikey, has_structure, source_doi }

## Status & honest gaps
- 46,612 real IR, 98.9% NMR-paired. 14,357 are complete IR+NMR+structure triples
  today (names -> OPSIN).
- The remaining ~32k lack a parseable name -> need the one-time DECIMER/MolScribe
  structure-OCR pass (GPU) to read the drawn structures (the way NMRexp does),
  converting most into complete triples.
- IR is band lists (reported peak positions), not full curves. Real, peak-level.

## How it compares
- vs NMRexp (3.37M, NMR-only): IRexp is the missing IR modality, NMR-paired.
- vs Wiley KnowItAll (250-300k, closed, IR-only): IRexp is OPEN, ML-ready,
  DOI-traceable, and paired with NMR + structure -- usable for open multimodal
  models, which a closed spectral library is not. Smaller, but the only open one.

## Reproduce
  python scripts/ir_harvest.py --target 100000 --out data/irexp        # IR-first crawl
  python scripts/build_irexp.py --sources data/bulk/spectra.jsonl data/irexp/ir.jsonl --out data/irexp
  # then (GPU) structure-OCR pass on the ~32k no-name records  [DECIMER]
