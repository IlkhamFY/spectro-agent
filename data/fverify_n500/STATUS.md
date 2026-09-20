# fverify n=500 — status

Unified wall for headline n=500 = locked 194 + all Opus +106 + expand-500
200-qid cut (`data/benchmark_expand_500/headline500_expand200_qids.json`).

**`WALL_n500.md` exists.** Integers are from `scripts/fverify_n500_wall.py`.
The paper may cite an n=500 fverify wall now that this file is present.
Do not invent other integers.

## n=500 wall (`WALL_n500.md`)

| arm | n | verified | misranked | never-proposed |
|---|---:|---:|---:|---:|
| locked 194 | 194 | 58 | 7 | 129 |
| Opus +106 | 106 | 56 | 12 | 38 |
| expand-500 200-cut | 200 | 90 | 26 | 84 |
| **n=500** | **500** | **204** | **45** | **251** |

Recalled = 204+45 = **249/500** (matches committed generation recall
65+68+116).

## Arms

| arm | n | generation score | fverify ¹³C | wall class |
|---|---:|---|---|---|
| locked 194 | 194 | 55/194 top-1, 65/194 recall | complete (`diagnosis.json` 58/7/129) | locked |
| Opus +106 | 106 | 63/106 top-1, 68/106 recall | **301/301**; score in `data/fverify_expand/results.txt` | 56/12/38 |
| expand-500 200-cut | 200 | 109/200 top-1, 116/200 recall | parent 681/681; 200-cut in `WALL_n500.md` | 90/26/84 |

## Do not

- invent `WALL_n500.md` integers (re-run the script)
- merge PR #18
- restore `answers2.jsonl` into the tree
- rewrite n=194 `diagnosis.json` via `forward_verify_all.py`
