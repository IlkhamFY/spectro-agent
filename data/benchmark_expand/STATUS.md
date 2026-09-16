# Expansion round — status

**Opus deposits are complete (106/106).** Predictions are written. The answer key is
still withheld (`scripts/export_round.py --restore` puts it back), so no ground-truth
audit has run and **no accuracy number exists yet**. Do not invent one.

## Collected

Reconciled 2026-09-16 06:29 UTC against `questions2.jsonl` vs `raw/` (and `raw_fable/`
for the cross-model row only). No scores.

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **106** | 100% |
| cross-model arm | `claude-fable-5-1` | 68 | 64% |

**0** Opus qids outstanding.

R39 (formula `C24H21N3S3`) banked from the eighth Cursor Task launch
[bc-0a25b5b0](https://cursor.com/agents/bc-0a25b5b0-4fb3-5564-9bbe-6a9c9b750304)
(`claude-opus-5-thinking-high`; deviation 3). All three candidates RDKit
formula-OK. Seven prior launches on this qid died with empty activity-task
timeouts (`{"messages":[]}`, 21 bytes) — not an API/model-quota blocker.

`collect_round.py` (no `--partial`) wrote `predictions2.jsonl`: 106/106 compounds,
302 candidates. One already-banked candidate is off-formula and was kept (R03:
`C10H13N5O2 != C9H11N5O2`); that is a solver miss, not a repair.

Every deposited batch was checked against its agent transcript (Claude Code deposits)
or against the Cursor Task serving slug (post-pause singles; deviation 3) and served
by the Opus 5 family the pre-registration names; `PROVENANCE.md` carries the per-batch
record.

## Scoring gate

The pre-registered stopping rule (every drawn compound has a response) is met.
Scoring still waits on restoring `answers2.jsonl`. The vault
`/tmp/blind/_key/benchmark_expand.answers2.jsonl.withheld` is empty on this VM, and
the key was never committed. After `predictions2.jsonl` is on the branch, restore
the key (vault copy, or a questions-identical `sample2 --n 106 --seed 2026`
regeneration), then:

    python scripts/validate_benchmark.py
    python scripts/benchmark_v2.py score2 --outdir data/benchmark_expand
    python scripts/forward_verify_main.py prep --round data/benchmark_expand --out data/fverify_expand --prefix expand

Do **not** score the Fable arm here. Do **not** merge. Do **not** pool Fable into
`raw/` or `predictions2.jsonl`.

## Overnight handoff (2026-09-16 06:29 UTC)

**Opus headline: 106/106 deposited. `predictions2.jsonl` written. Not scored. Key
still withheld.**

In flight: none.
