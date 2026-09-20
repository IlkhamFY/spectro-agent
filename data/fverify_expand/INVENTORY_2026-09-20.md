# fverify +106 inventory — 2026-09-20

Blind ¹³C gap on the Opus +106 expansion
(`data/benchmark_expand/predictions2.jsonl`). Counts come from
`scripts/inventory_fverify_expand.py`. No answer key was read.

A SMILES “already exists” only if it is in that path’s `anon_map` **and**
`raw/*.json` has a non-empty numeric ¹³C list for its anon id.

## +106 source (predictions only)

| | count |
|---|---:|
| compounds (`questions2.jsonl` ∩ `predictions2.jsonl`) | **106** |
| raw top-3 candidate slots | **302** |
| kept rows (RDKit-canonical, per-qid dups dropped) | **301** |
| unique canonical SMILES | **301** |
| dropped | **1** |

Candidates per qid: 1 → 0; 2 → 17; 3 → 89.

Dropped rows:

| qid | rank | reason |
|---|---:|---|
| R83 | 1 | per-qid-dup |

## Existing `data/fverify*` paths

| dir | anon_map | candidates | pred ids | raw files | +106 in map | +106 with ¹³C |
|---|---:|---:|---:|---:|---:|---:|
| `data/fverify` | 126 | 126 | 126 | 8 | 0 | 0 |
| `data/fverify2` | 65 | 0 | 65 | 4 | 0 | 0 |
| `data/fverify_expand` | 0 | 0 | 0 | 0 | 0 | 0 |
| `data/fverify_expand_500` | 681 | 681 | 681 | 41 | 0 | 0 |
| `data/fverify_gen` | 201 | 201 | 75 | 5 | 0 | 0 |
| `data/fverify_gw` | 152 | 0 | 152 | 9 | 0 | 0 |
| `data/fverify_main` | 247 | 247 | 247 | 15 | 0 | 0 |

`data/fverify_expand/` (this campaign) exists: **true**.
Own raw files: **0**. Own +106 SMILES with ¹³C: **0**.
fbatch files present: **0**.

## Remaining work

| | count |
|---|---:|
| unique SMILES that need a blind ¹³C list | **301** |
| already have ¹³C under any `fverify*` | **0** |
| already have ¹³C under any `fverify_expand*` | **0** |
| already in any `fverify*` anon_map | **0** |
| **still need a new ¹³C prediction** | **301** |
| qids with every candidate already covered (any path) | **0** |
| qids with partial coverage (any path) | **0** |
| qids with zero coverage (any path) | **106** |

`data/fverify_n500/WALL_n500.md` exists: **false**.
The paper may cite an n=500 fverify wall only after that file exists and
is written by a script from scored arms.

## Do not

- invent coverage numbers
- restore `answers2.jsonl` into the tree
- treat this inventory as a verification-precision result
