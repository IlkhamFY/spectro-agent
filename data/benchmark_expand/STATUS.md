# Expansion round — status

**The round is still incomplete. Nothing here is scored, and it must not be scored as it
stands.** The answer key is still withheld (`scripts/export_round.py --restore` puts it
back), so no ground-truth audit has run and no accuracy number exists for these compounds.

## Collected

Reconciled 2026-09-16 05:18 UTC against `questions2.jsonl` vs `raw/` (and `raw_fable/`
for the cross-model row only). No scores.

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **105** | 99% |
| cross-model arm | `claude-fable-5-1` | 68 | 64% |

**1** Opus qid still outstanding:

R39

Every deposited batch was checked against its agent transcript (Claude Code deposits) or
against the Cursor Task serving slug (post-pause singles; deviation 3) and served by the
Opus 5 family the pre-registration names; `PROVENANCE.md` carries the per-batch record.

## Why the solved subset must not be scored on its own

The pre-registered stopping rule is that **every** drawn compound has a response. It is not
met. Failure mode 2 (64k output-token ceiling) selects against compounds whose elucidation
takes the most reasoning. Scoring the solved subset would report an accuracy inflated by
the exclusion of compounds the solver could not finish thinking about.

## Overnight handoff (2026-09-16 05:18 UTC)

**Opus headline: 105/106. Not scored. Key withheld. `predictions2.jsonl` not written.**

R39 is the only outstanding qid. Fifth launch
[bc-c099a3e6](https://cursor.com/agents/bc-c099a3e6-388a-5ead-841d-d4efc3b41aaa)
ended ERROR after ~30 min with empty transcript `{"messages":[]}` (21 bytes) — five
consecutive empty activity-task timeouts on this qid (same leftover failure mode as
R79/R69 empties, which later deposited on retry). Not an Opus API or model-quota
blocker; the `claude-opus-5-thinking-high` slug still serves. Do **not** score this
105-compound subset. Do **not** fill R39 with another model.

Sixth launch in flight (JSON-only prompt; retry 5):

**In flight (do not double-launch):**

| qid | agent | started UTC |
|---|---|---|
| R39 | [Solve R39 blind Opus](https://cursor.com/agents/bc-88fa27ec-2283-5f7c-b55f-cd004f296eb0) | 05:18 (retry 5) |

**Need a free slot:** none — the only remaining qid is in flight.

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
