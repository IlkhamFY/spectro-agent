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
| already have ¹³C under any `fverify*` / any `fverify_expand*` | **85** / **85** |
| **still need blind ¹³C** | **216** |
| `raw/f*.json` in this directory | **5** |
| fbatch files | **18** |
| qids with every candidate covered | **0** / 106 |

Deposited `raw/fN.json`: f1, f2, f3, f4, f5.
Missing: f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17, f18.

## What is not done

| item | status |
|---|---|
| keyless prep (`anon_map` + `fbatch_*.txt`) | present |
| Opus ¹³C deposits | **85/301** |
| official chamfer score (`is_true` from /tmp key only) | not run |
| `data/fverify_n500/WALL_n500.md` | absent — paper must not cite n=500 fverify wall |

## Do not

- commit `answers2.jsonl` or write `is_true` into `candidates.jsonl`
- run official `forward_verify_main.py prep` against this directory (would
  need the key and would rewrite the keyless map)
- run `forward_verify_all.py` (would rewrite the n=194 `diagnosis.json`)
- invent wall integers
- merge PR #18
