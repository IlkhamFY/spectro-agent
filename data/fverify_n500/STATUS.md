# fverify n=500 — status

Unified wall for headline n=500 = locked 194 + all Opus +106 + expand-500
200-qid cut (`data/benchmark_expand_500/headline500_expand200_qids.json`).

**`WALL_n500.md` does not exist yet.** The paper may cite an n=500
fverify wall only after that file is written by a script from scored
arms. Do not invent the integers.

## Arms

| arm | n | generation score | fverify ¹³C | wall class |
|---|---:|---|---|---|
| locked 194 | 194 | 55/194 top-1, 65/194 recall | complete (`diagnosis.json` 58/7/129) | locked |
| Opus +106 | 106 | 63/106 top-1, 68/106 recall | **gap** — see `data/fverify_expand/` | blocked |
| expand-500 200-cut | 200 | 109/200 top-1, 116/200 recall | 681/681 on the parent 230; 200-cut wall not yet decomposed here | waiting on +106 |

Addition check for generation (already committed, not fverify):
55+63+109 = 227/500 top-1; 65+68+116 = 249/500 recall.
Those are InChIKey-14 generation numbers, not the fverify wall.

## In flight (2026-09-20)

+106 waves f1–f5 and f6–f10 (85 SMILES each) launched as Opus cloud
agents on `cursor/fverify-n500-unify-629c`. Remaining after those
deposit: **131** SMILES (f11–f18). Until deposits land, **301** SMILES
still need a ¹³C list.

## Blocker

`scripts/inventory_fverify_expand.py` on 2026-09-20: **301** unique +106
SMILES, **0** already have a ¹³C list under any `data/fverify*` path.

## Do not

- invent `WALL_n500.md` integers
- merge PR #18
- restore `answers2.jsonl` into the tree
- rewrite n=194 `diagnosis.json` via `forward_verify_all.py`
