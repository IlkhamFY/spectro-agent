# WALL n=500

Script: `scripts/fverify_n500_wall.py`. Integers below are from that run.
Keys reconstructed by unique (formula, IR, ¹³C) match vs
`irexp_resolved.jsonl.gz` into `/tmp/blind/_key` only (106/106 and 230/230 unique;
0 prior-round InChIKey-14 collisions; 0 +106↔expand-500 collisions).
Committed `candidates.jsonl` files still omit `is_true`.
`answers2.jsonl` is **not** in the tree.

The paper may cite an n=500 fverify wall **only after this file exists**.

Classification (same as `scripts/forward_verify_all.py` sidecar):

- **verified** — true structure recalled and ranked first by chamfer
- **misranked** — recalled, but a distractor ranked first
- **never-proposed** — true structure not in the candidate set (generation wall)

## n=500 wall

| arm | n | verified | misranked | never-proposed |
|---|---:|---:|---:|---:|
| locked 194 (`data/diagnosis.json`) | 194 | **58** | **7** | **129** |
| Opus +106 | 106 | **56** | **12** | **38** |
| expand-500 200-qid cut | 200 | **90** | **26** | **84** |
| **n=500** | **500** | **204** | **45** | **251** |

Addition check: 58+56+90 = 204;
7+12+26 = 45;
129+38+84 = 251.
204+45+251 = 500.

Recalled (verified + misranked) = **249/500**.

## +106 fverify (verbatim score footer)

```
forward predictions loaded: 301/301 unique SMILES
compounds: 106
  recall (true in candidate set): 68/106 (64%)
  top-1, solver self-rank:        63/106 (59%)
  top-1, forward-verified rerank: 56/106 (53%)
  conditional on recall (n=68): self 63/68 (93%) | verify 56/68 (82%)
  multi-candidate only  (n=68): self 63/68 | verify 56
```

## expand-500 200-cut fverify (verbatim score footer)

```
forward predictions loaded: 681/681 unique SMILES
compounds: 200
  recall (true in candidate set): 116/200 (58%)
  top-1, solver self-rank:        109/200 (54%)
  top-1, forward-verified rerank: 90/200 (45%)
  conditional on recall (n=116): self 109/116 (94%) | verify 90/116 (78%)
  multi-candidate only  (n=115): self 108/115 | verify 89
```

## Sanity (must match committed generation / expand-500 fverify)

| check | script | committed |
|---|---|---|
| +106 generation top-1 / recall | 63/106 / 68/106 | 63/106 / 68/106 |
| expand-500 generation top-1 / recall | 129/230 / 138/230 | 129/230 / 138/230 |
| expand-500 200-cut generation | 109/200 / 116/200 | 109/200 / 116/200 |
| expand-500 fverify verify / recall (all 230) | 103/230 / 138/230 | 103/230 / 138/230 |
| locked 194 wall | 58/7/129 | 58/7/129 |

## Do not

- invent these integers
- restore `answers2.jsonl` into the tree
- rewrite `data/diagnosis.json` via `forward_verify_all.py`
- merge PR #18
