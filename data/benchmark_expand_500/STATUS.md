# n=500 expansion round — status

Pre-registration (frozen above the deviations line):
`docs/EXPANSION_PREREGISTRATION_500.md`.

**Opus deposits: 0/230.** Questions committed. Answer key withheld. No
`predictions2.jsonl`. **Do not score a partial. Do not write a top-1 / recall
number for this round into the ICLR paper.** Headline stays **n=295** until
this round is 100% deposited, validated (already snapshotted), and scored.

This branch is an independent pre-registered expansion, not a silent
replacement of n=194 or n=295. Pooling via `scripts/score_pooled.py --expand
--expand-500` is licensed by the pre-registration only after 230/230 Opus
responses exist.

## Draw (fixed before it ran)

| parameter | value |
|---|---|
| directory | `data/benchmark_expand_500/` |
| sampler | `scripts/benchmark_v2.py sample2` (unchanged) |
| n | 230 |
| seed | 2026500 |
| strata as drawn | 115 simple / 115 complex |
| exclusion set | 375 unique prior InChIKey-14s (all `data/benchmark*/answers*.jsonl`, including a local restore of the withheld +106 key) |
| InChIKey-14 collisions with any prior round | **0** |
| (formula, IR, ¹³C) collisions with any prior `questions*.jsonl` | **0** |
| J in every committed ¹H | yes |

`answers2.jsonl` is **not** in the tree. The +106 expansion key was restored
locally for the exclusion pass, then deleted from the working tree again.

## Ground-truth audit (before any prediction)

`python scripts/validate_benchmark.py` was run on this round **before** any
solver was invoked, so 13C-overread flags cannot depend on whether a compound
was solved.

| | count |
|---|---:|
| drawn | 230 |
| spectrally clean | **224** |
| flagged 13C-overread | **6** |

Flagged qids (still **must be solved**; excluded only from a later headline
pool): **R26, R31, R102, R105, R107, R138**. Snapshot: `clean_qids.json`.

Clean strata: 110 simple / 114 complex. If 224/224 of those later have Opus
responses, 295 + 224 = **519** (above 500). Do not treat 519 as a result; it
is the arithmetic of the draw + this audit, not a score.

## Collected

| arm | solver | compounds with a blind response | of 230 |
|---|---|---:|---:|
| expansion toward 500 | `claude-opus-5` | **0** | 0% |

**230** Opus qids outstanding: `outstanding_opus.txt`.

No Fable (or any other) arm is registered on this draw.

## Scoring (not done; do not invent)

| item | status |
|---|---|
| Opus deposits | 0/230 |
| `predictions2.jsonl` | not written (`collect_round.py` writes it only at 100%) |
| `score2` / top-1 / recall | **not run** — partial subsets are not scored |
| `scripts/score_main.py` n=194 | **untouched** |
| paper headline | **n=295** until 100% deposited + scored |
| `scripts/score_pooled.py --expand-500` | **illegal** until 230/230 |
| Fable | not part of this round |
| `forward_verify_main.py` | not run; no verification-precision number exists |

## Key handling

After the draw and the validate snapshot, `answers2.jsonl` was moved to
`/tmp/blind/_key/benchmark_expand_500.answers2.jsonl.withheld` and deleted
from the working tree. Restore for a **complete-round** scoring pass with:

```
python scripts/export_round.py --restore data/benchmark_expand_500 /tmp/blind
```

Confirm before any merge:

```
git ls-files data/benchmark_expand_500/answers2.jsonl   # must be empty
git ls-files data/benchmark_expand/answers2.jsonl       # must be empty
```

## How to deposit (follow-up Cursor runs)

1. Solver sees only the exported prompt under `/tmp/blind/benchmark_expand_500/`
   (or the same text inlined). RDKit formula/parse check only. Model:
   `claude-opus-5-thinking-high`. One compound per agent.
2. Write the reply as `/tmp/blind/replies_500/single_<qid>.json`, shape
   `{"R01": ["SMILES", "...", "..."]}` or `[{"qid":"R01","candidates":[...]}]`.
3. Bank without scoring:

```
python scripts/collect_round.py data/benchmark_expand_500 /tmp/blind/replies_500 --partial
```

4. Append a provenance row. Commit `raw/` + STATUS + outstanding list. Do
   **not** add `answers2.jsonl`. Do **not** run `score2` until 230/230.
5. After each bank, rewrite `outstanding_opus.txt` as the qids in
   `questions2.jsonl` that are not yet in `raw/`.

## How to pool (only at 100%)

```
python scripts/export_round.py --restore data/benchmark_expand_500 /tmp/blind
python scripts/validate_benchmark.py          # should match the committed clean snapshot
python scripts/benchmark_v2.py score2 --outdir data/benchmark_expand_500
python scripts/score_pooled.py --expand --expand-500
```

`score_pooled.py` refuses a missing `predictions2.jsonl` or a withheld key.
It does not rewrite `score_main.py`. Re-withhold the key after the score.

## Overnight / follow-up handoff

**Draw committed. Key withheld. 0/230 Opus. Outstanding: all 230 qids in
`outstanding_opus.txt`. No scores. Do not merge. Paper stays n=295.**
