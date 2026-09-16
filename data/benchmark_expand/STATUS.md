# Expansion round — status

**The round is still incomplete. Nothing here is scored, and it must not be scored as it
stands.** The answer key is still withheld (`scripts/export_round.py --restore` puts it
back), so no ground-truth audit has run and no accuracy number exists for these compounds.

## Collected

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **91** | 86% |
| cross-model arm | `claude-fable-5-1` | 40 | 38% |

`outstanding_opus.txt` was stale at the pause (listed 44). Reconciled against
`questions2.jsonl` vs `raw/`. **15** still outstanding:

R39 R62 R63 R69 R71 R73 R76 R79 R80 R91 R92 R93 R94 R97 R102

Every deposited batch was checked against its agent transcript (Claude Code deposits) or
against the Cursor Task serving slug (post-pause singles; deviation 3) and served by the
Opus 5 family the pre-registration names; `PROVENANCE.md` carries the per-batch record.

## Why the solved subset must not be scored on its own

The pre-registered stopping rule is that **every** drawn compound has a response. It is not
met. Failure mode 2 (64k output-token ceiling) selects against compounds whose elucidation
takes the most reasoning. Scoring the solved subset would report an accuracy inflated by
the exclusion of compounds the solver could not finish thinking about.

## Overnight handoff (2026-09-16 ~02:30 UTC)

Not a model/API blocker: Cursor Task `claude-opus-5-thinking-high` is serving deposits.
Hard cap this session: **10 concurrent async subagents**. New launches return
`Async subagent limit of 10 reached` until in-flight solvers finish.

**Not yet launched this resume** (need a free slot):  
R73 R74 R76 R80 R92 R97 R102

**In flight** (do not double-launch): R39 R62 R63 R69 R71 R77 R79 R91 R93 R94

Bank with `/tmp/blind/bank_one.sh Rxx` (or `scripts/collect_round.py` + provenance row).
Do **not** restore the key or write `predictions2.jsonl` until 106/106.

## To resume

Outstanding prompts are regenerable from the committed `questions2.jsonl`:

    python scripts/export_round.py data/benchmark_expand /tmp/blind --batch 6
    python scripts/split_batch.py /tmp/blind/benchmark_expand/batch_NN.txt   # halves

Solve remaining qids as **singles**, bank each through `scripts/collect_round.py` /
`scripts/bank_batch.sh`, and only once all 106 are in: drop `--partial` to write
`predictions2.jsonl`, commit the predictions, **then** restore the key, run
`scripts/validate_benchmark.py`, and score.
