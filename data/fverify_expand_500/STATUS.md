# fverify expand-500 — status

Blind ¹³C forward-verification of the expand-500 Opus candidates.
Prep is keyless (`PREP_NOTE.md`). The answer key is **not** in the tree.

**Coverage: 41/41 batches, 681/681 unique SMILES (100%).** Official
chamfer score ran 2026-09-20. Paper headline stays **n=300**. This arm
is not written into the paper.

Companion files: `INVENTORY_2026-09-20.md`, `results.txt`,
`data/benchmark_expand_500/NIGHT_POOL_2026-09-20.md`.

## Coverage (deposits)

| | count |
|---|---:|
| unique SMILES (anon Q000…Q680) | **681** |
| `raw/f1.json`…`f41.json` | **41/41** |
| non-empty numeric ¹³C lists | **681/681** |
| qids with every candidate covered | **230/230** |

f1–f25 = 17 SMILES each; f26–f41 = 16. Every file matches its `fbatch_N.txt`.

## Official score (2026-09-20)

`scripts/forward_verify_main.py score()` arithmetic — same chamfer, same
self-rank vs min-chamfer rerank. Official `prep` was **not** run: it would
rewrite `anon_map.json` / `fbatch_*.txt` (plain seed-11 shuffle, clean-224
only) and break the deposited `raw/f*.json` mapping. `is_true` was filled
from a `/tmp` key onto a `/tmp` candidates copy. Committed
`candidates.jsonl` still omits `is_true`.

Key: unique (formula, IR, ¹³C) match vs `irexp_resolved.jsonl.gz` →
**230/230** unique, 0 prior-round InChIKey-14 collisions. Generation
sanity on that key reproduced the committed `score2` footer
(129/230 top-1, 138/230 recall). Key path:
`/tmp/blind/_key/benchmark_expand_500.answers2.jsonl.withheld`. Then
re-withheld (`git ls-files …/answers2.jsonl` empty).

Verbatim `score()` footer on the deposited 230-qid bundle:

```
forward predictions loaded: 681/681 unique SMILES
compounds: 230
  recall (true in candidate set): 138/230 (60%)
  top-1, solver self-rank:        129/230 (56%)
  top-1, forward-verified rerank: 103/230 (45%)
  conditional on recall (n=138): self 129/138 (93%) | verify 103/138 (75%)
  multi-candidate only  (n=137): self 128/137 | verify 102/137
```

| set | n | generation recall | self top-1 | verify top-1 | verify \| recall |
|---|---:|---|---|---|---|
| all deposited (keyless bundle) | 230 | **138/230 (60.0%)** | **129/230 (56.1%)** | **103/230 (44.8%)** | **103/138 (74.6%)** |
| validate-clean (official-prep subset) | 224 | **135/224 (60.3%)** | **127/224 (56.7%)** | **103/224 (46.0%)** | **103/135 (76.3%)** |

Multi-candidate only: all-230 self 128/137, verify 102/137; clean-224
self 126/134, verify 102/134.

Forward-verify **does not beat** solver self-rank on this arm
(103 vs 129 top-1). That is the script output, not a paper claim.

`forward_verify_all.py` was **not** run (`data/diagnosis.json` / n=194
sidecar untouched). No CIs.

## Do not

- commit `answers2.jsonl` or write `is_true` into `candidates.jsonl`
- re-run official `prep` against this directory
- promote these numbers into the paper headline
