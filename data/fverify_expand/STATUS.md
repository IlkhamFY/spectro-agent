# fverify +106 — status

Blind ¹³C forward-verification of the Opus +106 expansion
(`data/benchmark_expand/`). Prep is keyless (`PREP_NOTE.md` once written).
The answer key is **not** in the tree.

**This is the remaining hole for a scored+fverify n=500 corpus.**
Locked n=194 wall is 58/7/129. expand-500 fverify is 681/681 and scored.
+106 fverify was never run for the paper.

Counts below are from `scripts/inventory_fverify_expand.py`
(2026-09-20). Companion: `INVENTORY_2026-09-20.md`.

## Coverage (deposits)

| | count |
|---|---:|
| compounds | **106** |
| unique SMILES (target) | **301** |
| kept candidate rows | **301** |
| already have ¹³C under any `fverify*` / any `fverify_expand*` | **0** / **0** |
| **still need blind ¹³C** | **301** |
| `raw/f*.json` in this directory | **0** |
| fbatch files | **18** |
| qids with every candidate covered | **0** / 106 |

## In flight (2026-09-20)

Two careful Opus waves (direct push to this branch, no extra PRs):

| wave | batches | SMILES | agent |
|---|---|---:|---|
| 1 | f1–f5 | 85 | [bc-fe78d6bd](https://cursor.com/agents/bc-fe78d6bd-ce27-5a32-9817-9a3aa5687fef) |
| 2 | f6–f10 | 85 | [bc-f8ee2653](https://cursor.com/agents/bc-f8ee2653-0b40-5c71-96af-c331a32159e4) |

Not launched: f11–f18 (**131** SMILES). After these two waves deposit, **131** SMILES still need ¹³C. Until they land, **301** remain.

## What is not done

| item | status |
|---|---|
| keyless prep (`anon_map` + `fbatch_*.txt`) | present |
| Opus ¹³C deposits | **0/301** |
| official chamfer score (`is_true` from /tmp key only) | not run |
| `data/fverify_n500/WALL_n500.md` | absent — paper must not cite n=500 fverify wall |

## Do not

- commit `answers2.jsonl` or write `is_true` into `candidates.jsonl`
- run official `forward_verify_main.py prep` against this directory (would
  need the key and would rewrite the keyless map)
- run `forward_verify_all.py` (would rewrite the n=194 `diagnosis.json`)
- invent wall integers
- merge PR #18
