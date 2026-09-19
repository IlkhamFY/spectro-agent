# Keyless forward-verify prep — expand-500

This directory is a **keyless** prep so Opus agents can fill `raw/f*.json`
without anyone restoring `answers2.jsonl`.

Official score path:

```
python scripts/forward_verify_main.py prep --round data/benchmark_expand_500 --out data/fverify_expand_500
```

needs the withheld key **only** to set `is_true`. Do not restore the key for
this campaign. Do not run `prep` or `score` against this bundle until the key
is later available and `is_true` can be filled from it.

## What this prep is

| | |
|---|---|
| source | `data/benchmark_expand_500/raw/*.json` (fallback `data/benchmark_expand_500/predictions2.jsonl`) + `questions2.jsonl` |
| answer key | **not read** (`is_true` absent from every candidates row) |
| compounds | **230** deposits (all of them; not the clean-224 subset) |
| candidate rows | **681** (top-3 SMILES / qid, RDKit-canonical, per-qid dups dropped) |
| unparseable / per-qid dup dropped | 9 |
| unique SMILES | **681** (anon ids Q000…Q680) |
| batches | **41** × ~17 (`fbatch_1.txt`…`fbatch_41.txt`, seed 11) |
| sibling split | qid-mates packed into different batches when a free slot exists; 0 leftover co-batch sibling(s) |
| `raw/` | empty on purpose — Opus writes `f1.json`… here |

`anon_map.json` is smiles → anon_id only, matching `data/fverify_main/anon_map.json`.
There is no reverse map.

`candidates.jsonl` rows carry `qid`, `smiles`, `anon_id`, `self_rank`, plus the
official-shape fields that do **not** need the key (`cid`, `dir`, `obs_c13`
from the question ¹³C string, `difficulty` from `questions2.jsonl`). `is_true`
is omitted. Never invent it.

## Clean-224 (no key required)

`data/benchmark_expand_500/clean_qids.json` already lists the **224** spectrally-clean qids from
the pre-solver ¹³C-overread audit (STATUS.md). Flagged, still solved, excluded
only from a later headline pool: R26, R31, R102, R105, R107, R138.

This bundle includes **all 230** deposits so the blind ¹³C campaign covers
every Opus candidate. Official `forward_verify_main.py prep` would later
restrict to `clean_qids.json` when the key is restored for scoring.

## Do not

- restore `answers2.jsonl` onto this branch
- run `forward_verify_main.py score` or `forward_verify_all.py` against this
  bundle (score needs `is_true` and the key)
- treat anything here as a verification-precision number
