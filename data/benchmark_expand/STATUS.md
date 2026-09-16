# Expansion round — status

**The round is still incomplete. Nothing here is scored, and it must not be scored as it
stands.** The answer key is still withheld (`scripts/export_round.py --restore` puts it
back), so no ground-truth audit has run and no accuracy number exists for these compounds.

## Collected

Reconciled 2026-09-16 03:35 UTC against `questions2.jsonl` vs `raw/` (and `raw_fable/`
for the cross-model row only). No scores.

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **104** | 98% |
| cross-model arm | `claude-fable-5-1` | 68 | 64% |

**2** Opus qids still outstanding:

R39 R79

Every deposited batch was checked against its agent transcript (Claude Code deposits) or
against the Cursor Task serving slug (post-pause singles; deviation 3) and served by the
Opus 5 family the pre-registration names; `PROVENANCE.md` carries the per-batch record.

## Why the solved subset must not be scored on its own

The pre-registered stopping rule is that **every** drawn compound has a response. It is not
met. Failure mode 2 (64k output-token ceiling) selects against compounds whose elucidation
takes the most reasoning. Scoring the solved subset would report an accuracy inflated by
the exclusion of compounds the solver could not finish thinking about.

## Overnight handoff (2026-09-16 03:35 UTC)

**Opus headline: 104/106. Not scored. Key withheld. `predictions2.jsonl` not written.**

R69 third launch banked (formula OK). Two remaining, both in flight. No Opus API/model blocker.

**In flight (do not double-launch):**

| qid | agent | started UTC |
|---|---|---|
| R79 | [Solve R79 blind Opus](https://cursor.com/agents/bc-792069e7-4c63-545a-b6a5-05379cec7dfb) | 03:07 (retry) |
| R39 | [Solve R39 blind Opus](https://cursor.com/agents/bc-bd9831e7-c087-524b-a50d-4f0f82ed7cfe) | 03:14 (retry) |

**Need a free slot:** none — every remaining qid is in flight.

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
