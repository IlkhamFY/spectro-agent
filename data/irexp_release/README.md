# IRexp release — open experimental IR for training

Built from IRexp (119,345 unique real experimental IR records scraped from
open-access papers; no synthetic/computed IR). Gzipped; `gunzip` to use.

| file | rows | use |
|---|--:|---|
| **train_no_bench.jsonl.gz** | **42,808** | **recommended supervised pool** — structure-linked, benchmark IK-14 held out |
| train_no_bench_nmr.jsonl.gz | 32,949 | same, requiring both ¹H and ¹³C |
| train.jsonl.gz / test.jsonl.gz | 25,280 / 2,808 | legacy 90/10 split — **overlaps benchmark (117/200 IK-14)** |
| pretrain_ir.jsonl.gz | 119,345 | IR-encoder pretraining (all IR, label-free) |

Rebuild held-out splits:

```bash
python scripts/build_train_no_bench.py
python scripts/build_train_no_bench.py --require-nmr
```

**Hugging Face dataset card:** see [`README_HF.md`](README_HF.md) — copy to `README.md` when
uploading to Hugging Face.

Tiers within IRexp:
- **27,856 full multimodal** (IR + NMR + structure) -- directly-trainable Spectro samples
- 28,088 IR + structure (supervised IR->molecule)
- 87,075 IR + NMR paired

Row: { id(InChIKey), smiles, selfies, ir_bands_cm-1 (real experimental),
h_nmr, c_nmr, ir_source:"experimental", source_doi }

## Honest scope
The 250k target was not reached: the open, text-extractable, real-IR corpus is
bounded. PMC-OA characterization papers yield ~0.58 clean IR/paper and are mined
out at 119,345; the broader cm-1 corpus is materials/physics prose (~0 real
per-compound IR); SI is spectra images (not text); OpenAlex/Semantic-Scholar are
IP-blocked from this environment; CrossRef full-text is paywalled. So 119,345 is
the genuine open-text ceiling reachable here. Routes beyond it (SI-image curve
digitization, or licensed libraries like Wiley) trade away either fidelity or
openness. This release is the real, defensible maximum.
