# Expansion round — status

**The round is still incomplete. Nothing here is scored, and it must not be scored as it
stands.** The answer key is still withheld (`scripts/export_round.py --restore` puts it
back), so no ground-truth audit has run and no accuracy number exists for these compounds.

## Collected

Reconciled 2026-09-16 02:56 UTC against `questions2.jsonl` vs `raw/` (and `raw_fable/`
for the cross-model row only). No scores.

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **92** | 87% |
| cross-model arm | `claude-fable-5-1` | 68 | 64% |

**14** Opus qids still outstanding:

R39 R62 R63 R69 R71 R76 R79 R80 R91 R92 R93 R94 R97 R102

Every deposited batch was checked against its agent transcript (Claude Code deposits) or
against the Cursor Task serving slug (post-pause singles; deviation 3) and served by the
Opus 5 family the pre-registration names; `PROVENANCE.md` carries the per-batch record.

## Why the solved subset must not be scored on its own

The pre-registered stopping rule is that **every** drawn compound has a response. It is not
met. Failure mode 2 (64k output-token ceiling) selects against compounds whose elucidation
takes the most reasoning. Scoring the solved subset would report an accuracy inflated by
the exclusion of compounds the solver could not finish thinking about.

## Overnight handoff (2026-09-16 02:56 UTC)

**Opus headline: 92/106. Not scored. Key withheld. `predictions2.jsonl` not written.**

Timeouts with empty transcripts (not banked): first R69 and first R93. Both relaunched.
No Opus API/model blocker. Hard cap: **10 concurrent async subagents**.

**In flight (do not double-launch):**

| qid | agent | started UTC |
|---|---|---|
| R63 | [Solve R63 blind Opus](https://cursor.com/agents/bc-e43d9303-d942-5ffd-8621-113c2391a1ac) | 02:28 |
| R91 | [Solve R91 blind Opus](https://cursor.com/agents/bc-f2989e74-aa33-5d96-a10d-859719d9c170) | 02:28 |
| R94 | [Solve R94 blind Opus](https://cursor.com/agents/bc-a163ce61-9aef-5190-b0df-0f06a0e1be26) | 02:28 |
| R71 | [Solve R71 blind Opus](https://cursor.com/agents/bc-b46f67c2-d513-54f7-b755-f1599e355cfc) | 02:28 |
| R62 | [Solve R62 blind Opus](https://cursor.com/agents/bc-4703088a-56c4-56c1-8b82-e30608e9bc13) | 02:30 |
| R79 | [Solve R79 blind Opus](https://cursor.com/agents/bc-f7167d69-0557-504d-9c08-f99ae2d1a65c) | 02:37 |
| R97 | [Solve R97 blind Opus](https://cursor.com/agents/bc-ea0efdf1-11d9-5988-9192-5d2f1d5bee0c) | 02:40 |
| R39 | [Solve R39 blind Opus](https://cursor.com/agents/bc-bee7fb47-d918-5673-8c94-b49002770c7a) | 02:44 |
| R69 | [Solve R69 blind Opus](https://cursor.com/agents/bc-13df7926-9063-5ef3-8029-1679d7b0d7a6) | 02:54 (retry) |
| R93 | [Solve R93 blind Opus](https://cursor.com/agents/bc-b02f0154-0b15-5e96-a2f7-b353ce281669) | 02:56 (retry) |

**Need a free slot:** R76 R80 R92 R102

On any in-flight completion: formula-check the JSON, `/tmp/blind/bank_one.sh Rxx`, then
immediately launch one waiting qid into the freed slot. Prompts are at
`/tmp/blind/prompts/Rxx.md` (regenerable from `questions2.jsonl`).

Do **not** restore the key or write `predictions2.jsonl` until 106/106.

## To resume

Outstanding prompts are regenerable from the committed `questions2.jsonl`:

    python scripts/export_round.py data/benchmark_expand /tmp/blind --batch 6
    python scripts/split_batch.py /tmp/blind/benchmark_expand/batch_NN.txt   # halves

Solve remaining qids as **singles**, bank each through `scripts/collect_round.py` /
`scripts/bank_batch.sh`, and only once all 106 are in: drop `--partial` to write
`predictions2.jsonl`, commit the predictions, **then** restore the key, run
`scripts/validate_benchmark.py`, and score.
