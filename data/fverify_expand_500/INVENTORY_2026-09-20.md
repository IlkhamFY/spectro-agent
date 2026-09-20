# fverify expand-500 inventory — 2026-09-20

Blind ¹³C campaign over the 681 unique candidate SMILES prepared by
`scripts/forward_verify_expand500_keyless.py` (`PREP_NOTE.md`). This file
counts deposits only. **No verification-precision number exists** —
`forward_verify_main.py score` was not run (`is_true` is still absent;
16 batches have no `raw/f*.json`).

Source of the counts: listing `data/fverify_expand_500/raw/f*.json`
against `fbatch_1.txt`…`fbatch_41.txt`, `anon_map.json` (681 smiles → Q000…Q680),
and `candidates.jsonl` (681 rows).

## Coverage

| | count |
|---|---:|
| prep unique SMILES (target) | **681** |
| fbatch files present | **41/41** |
| `raw/f*.json` present | **31/41** |
| unique SMILES with a non-empty numeric ¹³C list | **516/681 (75.77%)** |
| unique SMILES still missing a ¹³C list | **165** |
| existing batches that are complete vs their fbatch | **31/31** |
| qids with every candidate SMILES covered | 129/230 |
| qids with at least one candidate covered | 230/230 |

Sibling packing in the keyless prep put a qid's three candidates in
different batches, so a hole in `f16–f20` / `f31–f35` still leaves every
qid with at least one covered SMILES.

## Existing ids (`raw/fN.json`)

**f1–f15, f21–f30, f36–f41** (31 files). Each matches its `fbatch_N.txt` 1:1
(f1–f25 are 17 SMILES; f26–f41 are 16). All present files are complete.
f36–f41 landed on this branch as `ee4a771` while the night score ran.

| ids | files | SMILES / file | SMILES covered |
|---|---:|---:|---:|
| f1–f15 | 15 | 17 | 255 |
| f21–f25 | 5 | 17 | 85 |
| f26–f30 | 5 | 16 | 80 |
| f36–f41 | 6 | 16 | 96 |
| **present** | **31** | | **516** |

## Missing ids

**f16–f20, f31–f35** (10 files).

| ids | files | SMILES / file | SMILES missing |
|---|---:|---:|---:|
| f16–f20 | 5 | 17 | 85 |
| f31–f35 | 5 | 16 | 80 |
| **missing** | **10** | | **165** |

Missing fbatch list: **f16, f17, f18, f19, f20, f31, f32, f33, f34, f35**.

Do not invent `f16.json`…`f41.json`. Those are Opus ¹³C replies, not
something a night coding pass should fabricate.

## What this is not

- Not a `forward_verify_main.py` score
- Not verification precision / recall
- Not a reason to restore `answers2.jsonl` onto the branch
