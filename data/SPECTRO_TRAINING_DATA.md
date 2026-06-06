# Spectro training data — 100k NMR + IR (data card)

All in Spectro's exact input format; gzipped in the repo (`gunzip` to use).

| dataset | file | records | NMR | IR | structure |
|---|---|--:|:--:|:--:|:--:|
| **FULL — every record NMR+IR** | `data/training_full/train.jsonl.gz` | **100,000** | ✅ ¹H+¹³C | ✅ all | ✅ |
| NMRexp backbone (NMR only) | `data/training_nmrexp/train.jsonl.gz` | 100,000 | ✅ | ✗ | ✅ |
| IR triples (experimental IR) | `data/training_ir/train.jsonl.gz` | 6,981 | ✅ | ✅ real | ✅ |

**`training_full` is the headline: 100,000 records that each carry NMR *and* IR
*and* a structure label** — directly usable for supervised `(NMR,IR) → structure`.
Audit: 100% with NMR+IR, 100% IR bands in 400–4000 cm⁻¹, **100% SELFIES↔SMILES
round-trip**, median 16 IR bands/record.

### Where the IR comes from (`ir_source` field — be precise about this)

| `ir_source` | records | what it is |
|---|--:|---|
| `experimental` | 40 | real IR from the paper crawl, matched to an NMRexp molecule by InChIKey |
| `computed_fg` | 99,960 | **functional-group-computed** IR (RDKit SMARTS → characteristic bands) |

Experimental IR paired with structure is genuinely scarce (NMRexp, like all large
NMR corpora, has none), so the backbone IR is **computed** — the same route the
177K-patent IR–NMR dataset took. This is well-aligned with Spectro: its
`j-IR-vis` is *pretrained to detect functional-group peaks*, which is exactly what
these bands encode. For the experimental IR-paired subset, see the 6,981 triples.

## Row schema (identical for both)

```json
{
  "id":      "InChIKey",
  "smiles":  "Cc1ccccc1NC(=O)Cn1cc(...)nn1",   // RDKit-canonical
  "selfies": "[C][C][=C]...",                   // ← MODEL TARGET (decoder)
  "h_nmr":   "δ 9.79 (1H, s), 9.17 (1H, br.s), ...",   // ¹H text → LLM2Vec
  "c_nmr":   "δ 164.87 (1C, s), 161.57 (1C, s), ...",  // ¹³C text → LLM2Vec
  "ir_bands_cm-1": [3318, 3146, 1704, ...] | null,     // ← IR (see below)
  "source_doi": "10.xxxx/...", "source": "NMRexp" | "paper-crawl"
}
```

## Provenance & quality

* **NMRexp** — pivoted from [NMRexp](https://doi.org/10.5281/zenodo.17296666)
  (3.37M experimental NMR records / 1.24M molecules with both ¹H+¹³C; Sci Data
  2025, peer-reviewed >99% metadata accuracy). We use NMRexp's **own validated
  peak parse** (`NMR_processed`), so δ-strings are theirs, not re-parsed.
  Audit on our 100k: 0% parse artifacts, 3000/3000 valid SMILES, **¹³C≤carbon
  count 99.7%**, **SELFIES↔SMILES round-trip 100%**.
* **IR triples** — this repo's crawl of open-access papers, taking records that
  report **NMR and IR for the same compound**, with structures resolved by OPSIN.
  Audit: 100% IR bands in 400–4000 cm⁻¹, **100% SELFIES round-trip**, 86% with
  both nuclei. This is *real experimental* IR.

## The IR reality (read this)

Spectro needs NMR **and** IR, but **experimental IR paired with structure is
scarce** — which is exactly why NMRexp (and most large NMR corpora) are NMR-only.
So:

* The **100k backbone is NMR-only**; it trains the NMR encoder + decoder and is
  most of Spectro's signal.
* The **6,981 triples carry real IR** — use them for the IR pathway (j-IR-vis)
  and joint NMR+IR training. Note IR here is a **band list**, not a curve, so
  either featurize the bands (≈ the functional-group vector j-IR-vis predicts),
  synthesize Lorentzian curves, or pull NIST JDX curves
  (`scripts/nist_ir_demo.py`) for the common-molecule slice.
* To scale IR further: **compute it** for the NMRexp molecules (the route the
  177K-patent IR–NMR dataset took), or harvest more IR-reporting papers.

## Reproduce

```bash
# NMR backbone (downloads the 661MB NMRexp parquet from Zenodo):
python scripts/nmrexp_to_spectro.py --out data/training_nmrexp --target 100000
# IR triples (from the paper crawl in data/bulk):
python scripts/build_ir_triples.py
```

## Suggested use for Spectro

1. Pretrain the NMR text encoder on all 107k δ-strings (no labels needed).
2. Supervised `(¹H,¹³C) → SELFIES` on the 100k NMRexp set (largest, labeled).
3. Add the IR pathway on the 6,981 triples (real IR), with one of the band
   representations above.
