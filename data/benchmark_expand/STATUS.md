# Expansion round — status at the pause

**The round is paused incomplete. Nothing here is scored, and it must not be scored as it
stands.** The answer key is still withheld (`scripts/export_round.py --restore` puts it
back), so no ground-truth audit has run and no accuracy number exists for these compounds.

## Collected

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **62** | 58% |
| cross-model arm | `claude-fable-5-1` | 40 | 38% |
| both arms | — | 35 | 33% |

Every deposited batch was checked against its agent transcript and served end to end by the
model its pre-registration names; `PROVENANCE.md` carries the per-batch record.

## Why it stopped

Two independent limits, neither of them the chemistry:

1. **Session quota.** Each window admitted a handful of batches and then returned 429 for
   the rest. Agents in flight when the container was reclaimed were lost outright.
2. **Output-token ceiling.** Long solver reasoning overran the 64 000-token maximum and the
   agent died with nothing to deposit. Batches were cut to three compounds and then to one
   (deviation 2 in the pre-registration); some single compounds still overran.

## Why the 62 must not be scored on their own

The pre-registered stopping rule is that **every** drawn compound has a response. It is not
met, and the shortfall is not random: failure mode 2 selects against compounds whose
elucidation takes the most reasoning. The unsolved 44 are measurably the harder half —

| | n | simple / complex | median heavy atoms |
|---|---:|---|---:|
| solved | 62 | 32 / 30 | 20 |
| unsolved | 44 | 21 / 23 | 22 |

Scoring the solved subset would report an accuracy inflated by the exclusion of compounds
the solver could not finish thinking about. That is exactly the post-hoc cohort selection
the pre-registration exists to prevent.

## To resume

Outstanding batches are regenerable from the committed `questions2.jsonl`:

    python scripts/export_round.py data/benchmark_expand /tmp/blind --batch 6
    python scripts/split_batch.py /tmp/blind/benchmark_expand/batch_NN.txt   # halves

Solve the outstanding qids, bank each with
`scripts/bank_batch.sh <arm> <tag> <agent-id> <qid range>` (it refuses a batch served by a
fallback model), and only once all 106 are in: drop `--partial` to write
`predictions2.jsonl`, commit the predictions, **then** restore the key, run
`scripts/validate_benchmark.py`, and score.
