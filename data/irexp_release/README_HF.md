---
language:
  - en
license:
  - cc-by-4.0
tags:
  - chemistry
  - spectroscopy
  - infrared
  - nmr
  - structure-elucidation
  - cheminformatics
size_categories:
  - 10K<n<100K
pretty_name: IRexp
configs:
  - config_name: commercial
    data_files: data/irexp_commercial.jsonl.gz
  - config_name: resolved_commercial
    data_files: data/irexp_resolved_commercial.jsonl.gz
  - config_name: train_no_bench_commercial
    data_files: data/train_no_bench_commercial.jsonl.gz
---

# IRexp — experimental IR band lists from open-access literature

**Paper:** [IRexp and IRSpectra-Bench: redistributable experimental IR band lists, a blind peak-list benchmark, and a recall-bound diagnosis of LLM elucidation](https://github.com/IlkhamFY/spectro-agent) (manuscript in preparation, 2026)

IRexp is an **openly redistributable** collection of **experimental infrared band lists** mined from open-access chemistry papers, often with co-reported ¹H/¹³C shift lists and resolved structures.

> **Important:** IRexp contains **band lists** (peak positions in cm⁻¹), not digitised absorbance traces. This is the form reported in publication text — the regime IRSpectra-Bench evaluates — and is not directly comparable to SDBS or NIST full spectra.

## Dataset of record (this Hub revision)

**Primary redistributable artifact** = commercial CC-BY / CC0 pool (`license_pool=commercial`) after the **F1 thousands-separator rebuild** and targeted PMC refetch merge (2026-09-10).

| Config / file | Records | Description |
|---|---:|---|
| `commercial` / `irexp_commercial.jsonl.gz` | **88,545** | **Dataset of record** — CC-BY + CC0; F1 bands; F2/F3 flags attached |
| `resolved_commercial` / `irexp_resolved_commercial.jsonl.gz` | 28,899 | Structure-linked commercial subset |
| `train_no_bench_commercial` / `train_no_bench_commercial.jsonl.gz` | 29,111 | Commercial `irexp_resolved` minus IRSpectra-Bench InChIKey-14 holdouts |

**Not in this Hub primary upload:** non-commercial (CC-BY-NC*), empty/unknown, and multi-licence full dumps. Those remain on disk for research; they are intentionally omitted from `ilkhamfy/IRexp` this round.

**Licence fields on every row:** `license`, `license_pool`, `license_raw`, `license_source` (plus `source_doi` / `pmcid` where available). Hub YAML license for the commercial DoR: **cc-by-4.0**.

**F1:** band lists re-parsed to fix thousands-separator / OCR digit artifacts (e.g. referee example PMC6268696). Pool size unchanged vs pre-F1 commercial stamp.

**F2 / F3 quality flags (kept as fields; rows NOT dropped):**
- `ir_shared_in_paper` (F2) — same IR band list shared across multiple records in one paper (pairing risk). Commercial: 18,651 true.
- `ir_table_flatten_suspect` (F3) — suspected table-flatten / column-misread band list. Commercial: 3,154 true.
- Policy: **flag-only** (Chem Partner / Ilkham). Headline commercial **n = 88,545** includes flagged rows. Filter locally if needed.

**Zenodo DOI:** pending (not minted in this revision). Do not invent a DOI.

**Companion benchmark:** [IRSpectra-Bench](https://github.com/IlkhamFY/spectro-agent/blob/main/docs/LEADERBOARD.md) — score with `scripts/score_submission.py`.

## Load in three lines

```python
from datasets import load_dataset

# Dataset of record (88,545 commercial rows)
ds = load_dataset("ilkhamfy/IRexp", "commercial", split="train")
print(len(ds), ds[0]["ir_bands_cm-1"][:5], ds[0]["license_pool"])

# Structure-linked commercial
res = load_dataset("ilkhamfy/IRexp", "resolved_commercial", split="train")

# Training without benchmark InChIKey-14 leakage (commercial)
train = load_dataset("ilkhamfy/IRexp", "train_no_bench_commercial", split="train")
```

## Record schema

Each JSONL row includes (among other fields):

```json
{
  "id": "73c2e8a41a6601afa622",
  "inchikey": null,
  "smiles": "CCOc1cccc2cc(C(C)=O)c(=O)oc12",
  "ir_bands_cm-1": [3060.0, 2976.0, 2874.0, 1730.0, 1678.0],
  "h_nmr": "...",
  "c_nmr": "...",
  "ir_source": "experimental",
  "source_doi": "PMC:6268696",
  "pmcid": "PMC6268696",
  "license": "CC-BY",
  "license_pool": "commercial",
  "license_raw": "cc by",
  "license_source": "europepmc",
  "ir_shared_in_paper": false,
  "ir_table_flatten_suspect": false
}
```

## Limitations (read before citing)

- **Band lists, not spectra** — median ~9 bands (PMC) vs denser Chemotion peak-picked lists.
- **Literature-transcribed** — heterogeneous labs/instruments; not raw `.jdx` files.
- **F2/F3 flags** are heuristic; human audit of strata is in progress — do not treat flags as ground truth exclusions unless you choose to filter.
- Manuscript totals beyond commercial **88,545** are not claimed here unless independently verified from staged rebuild files.

## Citation

```bibtex
@article{yabbarov2026irspectra,
  title   = {{IRexp} and {IRSpectra-Bench}: redistributable experimental {IR} band lists,
             a blind peak-list benchmark, and a recall-bound diagnosis of {LLM} elucidation},
  author  = {Yabbarov, Ilkham and Sondhi, Rudra and Vargas-Hern{\'a}ndez, Rodrigo A.},
  year    = {2026},
  note    = {Manuscript in preparation; Hugging Face commercial DoR n=88545 (F1 rebuild 2026-09-10)}
}
```

## Links

- **Dataset (Hugging Face):** https://huggingface.co/datasets/ilkhamfy/IRexp
- **Code & benchmark:** https://github.com/IlkhamFY/spectro-agent
- **Leaderboard:** https://github.com/IlkhamFY/spectro-agent/blob/main/docs/LEADERBOARD.md
- **Zenodo:** DOI pending (not minted)
- **Licence details:** `NOTICE` / `LICENCE_REMEDIATION.md` in this repository

When uploading to Hugging Face, this file is the repository `README.md`.
