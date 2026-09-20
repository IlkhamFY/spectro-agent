# Keyless forward-verify prep — +106 expansion

This directory is a **keyless** prep so Opus agents can fill `raw/f*.json`
without anyone restoring `answers2.jsonl`.

Official score path:

```
python scripts/forward_verify_main.py prep --round data/benchmark_expand --out data/fverify_expand
```

needs the withheld key **only** to set `is_true`. Do not restore the key for
this campaign. Do not run official `prep` against this bundle (it would
rewrite `anon_map.json` / `fbatch_*.txt`). Score later with the key only
under `/tmp`, filling `is_true` on a `/tmp` candidates copy.

## What this prep is

| | |
|---|---|
| source | `data/benchmark_expand/predictions2.jsonl` + `questions2.jsonl` (raw/ not used; singles live only in predictions2) |
| answer key | **not read** (`is_true` absent from every candidates row) |
| compounds | **106** deposits (all of them; not the clean-101 subset) |
| candidate rows | **301** (top-3 SMILES / qid, RDKit-canonical, per-qid dups dropped) |
| unparseable / per-qid dup dropped | 1 |
| unique SMILES | **301** (anon ids Q000…Q300) |
| batches | **18** (`fbatch_1.txt`…`fbatch_18.txt`, seed 11; sizes [17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 16, 16, 16, 16, 16]) |
| sibling split | qid-mates packed into different batches when a free slot exists; 0 leftover co-batch sibling(s) |
| `raw/` | empty on purpose — Opus writes `f1.json`… here |

`anon_map.json` is smiles → anon_id only, matching `data/fverify_main/anon_map.json`.
There is no reverse map.

`candidates.jsonl` rows carry `qid`, `smiles`, `anon_id`, `self_rank`, plus the
official-shape fields that do **not** need the key (`cid`, `dir`, `obs_c13`
from the question ¹³C string, `difficulty` from `questions2.jsonl`). `is_true`
is omitted. Never invent it.

## Clean-101 (no key required)

`data/benchmark_expand/clean_qids.json` already lists the **101** spectrally-clean qids from
the pre-solver ¹³C-overread audit (STATUS.md). Flagged, still solved, excluded
only from a later validate-clean pool: R12, R22, R25, R82, R91.

This bundle includes **all 106** deposits so the blind ¹³C campaign covers
every Opus candidate. Headline n=500 keeps all 106 (same convention as
locked n=300). Official `forward_verify_main.py prep` would later restrict
to `clean_qids.json` when the key is restored for a clean-only score.

## Wave plan (budget)

Max 2 parallel Opus waves of ~5 fbatch files. First two waves: **f1–f5**
and **f6–f10**. Remaining after those deposit: f11–f18.

## Do not

- restore `answers2.jsonl` onto this branch
- run official `prep` against this directory (would rewrite the keyless
  `anon_map` / `fbatch_*.txt`)
- run `forward_verify_all.py` (would rewrite the n=194 `diagnosis.json`)
- write `is_true` into committed `candidates.jsonl`
- cite an n=500 fverify wall until `data/fverify_n500/WALL_n500.md` exists
