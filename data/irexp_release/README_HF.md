---
language:
  - en
license:
  - cc-by-4.0
  - cc-by-sa-4.0
tags:
  - chemistry
  - spectroscopy
  - infrared
  - nmr
  - structure-elucidation
  - cheminformatics
size_categories:
  - 100K<n<1M
pretty_name: IRexp
dataset_info:
  features:
    - name: id
      dtype: string
      description: InChIKey (full)
    - name: inchikey
      dtype: string
    - name: smiles
      dtype: string
    - name: selfies
      dtype: string
    - name: ir_bands_cm-1
      sequence: float64
      description: Experimental IR wavenumbers (cm⁻¹), author-transcribed or peak-picked
    - name: h_nmr
      dtype: string
      description: ¹H shift list as printed in the source paper
    - name: c_nmr
      dtype: string
      description: ¹³C shift list as printed in the source paper
    - name: ir_source
      dtype: string
      description: Always "experimental"
    - name: source_doi
      dtype: string
      description: DOI or accession of the source publication
    - name: license
      dtype: string
      description: CC-BY-4.0 (PMC) or CC-BY-SA-4.0 (Chemotion)
---

# IRexp — experimental IR band lists from open-access literature

**Paper:** [IRSpectra-Bench and IRexp: candidate recall, not verification, limits LLM elucidation from real experimental IR and NMR](https://github.com/IlkhamFY/spectro-agent) (*Digital Discovery*, 2026)

IRexp is the largest **openly redistributable** collection of **experimental infrared band lists** mined from open-access chemistry papers, often with co-reported ¹H/¹³C shift lists and resolved structures.

> **Important:** IRexp contains **band lists** (peak positions in cm⁻¹), not digitised absorbance traces. This is the form reported in publication text — the regime IRSpectra-Bench evaluates — and is not directly comparable to SDBS or NIST full spectra.

## Dataset summary

| Split / file | Records | Description |
|---|---:|---|
| `irexp.jsonl.gz` | 121,233 | All IR band-list records |
| `irexp_resolved.jsonl.gz` | 43,060 | Structure-linked (100%) |
| … full IR + ¹H + ¹³C + structure | 33,201 | Multimodal quadruples |
| `train_no_bench.jsonl.gz` | 42,808 | **Recommended for training** — `irexp_resolved` minus all IRSpectra-Bench InChIKey-14 |
| `train_no_bench_nmr.jsonl.gz` | 32,949 | Same, requiring both ¹H and ¹³C |

**Provenance:** 119,345 records from PMC Open-Access (CC-BY-4.0); 1,888 from Chemotion/RADAR4Chem (CC-BY-SA-4.0). Use `scripts/split_license_pools.py` to separate pools.

**Companion benchmark:** [IRSpectra-Bench](https://github.com/IlkhamFY/spectro-agent/blob/main/docs/LEADERBOARD.md) — 194 blind elucidation problems built from IRexp; score submissions with `scripts/score_submission.py`.

## Load in three lines

```python
from datasets import load_dataset

# Full structure-linked corpus (43,060 records)
ds = load_dataset("IlkhamFY/IRexp", data_files="irexp_resolved.jsonl.gz", split="train")

row = ds[0]
print(row["ir_bands_cm-1"][:5], row["smiles"][:40])
```

For **fine-tuning without benchmark leakage**, use `train_no_bench.jsonl.gz` (not the legacy `irexp_release/train.jsonl.gz`, which overlaps 117/200 benchmark compounds):

```python
ds = load_dataset("IlkhamFY/IRexp", data_files="train_no_bench.jsonl.gz", split="train")
```

Or clone the GitHub repo / Zenodo deposit and read locally:

```python
import gzip, json

with gzip.open("irexp_resolved.jsonl.gz", "rt") as f:
    row = json.loads(f.readline())
```

## Record schema

Each JSONL row:

```json
{
  "id": "AJCQUIFRMABSOZ-UHFFFAOYSA-N",
  "inchikey": "AJCQUIFRMABSOZ-UHFFFAOYSA-N",
  "smiles": "Cc1ccccc1NC(=O)Cn1cc...",
  "selfies": "[C][C][=C]...",
  "ir_bands_cm-1": [3318.0, 3146.0, 1704.0],
  "h_nmr": "9.79 (s, 1H, NH-amide), ...",
  "c_nmr": "164.87, 161.57, ...",
  "ir_source": "experimental",
  "source_doi": "10.1038/..."
}
```

## Training vs benchmarking

| Use case | File | Benchmark overlap |
|---|---|---|
| Pretrain IR encoder | `pretrain_ir.jsonl.gz` or all `ir_bands_cm-1` | N/A (mostly unlabeled) |
| Supervised IR→structure | `train_no_bench.jsonl.gz` | **None** (248 IK-14 held out) |
| Evaluate elucidation | [IRSpectra-Bench](https://github.com/IlkhamFY/spectro-agent/blob/main/docs/LEADERBOARD.md) | — |
| ⚠️ Legacy split | `irexp_release/train.jsonl.gz` | **117/200 IK-14 overlap** — do not use for benchmark evaluation |

Rebuild the held-out training pool:

```bash
python scripts/build_train_no_bench.py              # 42,808 rows
python scripts/build_train_no_bench.py --require-nmr  # 32,949 rows (H+C required)
```

## Limitations (read before citing)

- **Band lists, not spectra** — median 9 bands (PMC) vs 39 (Chemotion peak-picked).
- **Literature-transcribed** — heterogeneous labs/instruments; not raw `.jdx` files.
- **Structure resolution 35%** of all records; use `irexp_resolved` for supervised tasks.
- **Extraction recall** of IR strings per paper not yet human-audited (transcription fidelity audited: 560/560 bands on n=60).

## Citation

```bibtex
@article{yabbarov2026irspectra,
  title   = {IRSpectra-Bench and {IRexp}: candidate recall, not verification,
             limits {LLM} elucidation from real experimental {IR} and {NMR}},
  author  = {Yabbarov, Ilkham and Sondhi, Rudra and Vargas-Hern{\'a}ndez, Rodrigo A.},
  journal = {Digital Discovery},
  year    = {2026},
  note    = {Zenodo DOI to be assigned at publication}
}
```

## Links

- **Code & benchmark:** https://github.com/IlkhamFY/spectro-agent
- **Leaderboard:** https://github.com/IlkhamFY/spectro-agent/blob/main/docs/LEADERBOARD.md
- **Zenodo:** DOI minted at publication
- **Licence details:** `data/NOTICE` in the repository

When uploading to Hugging Face, copy this file to `README.md` in the dataset repository root.
