# Expansion round — status

**Opus deposits are complete (106/106).** `predictions2.jsonl` is committed. Scored
locally under the pre-registered InChIKey-14 rule. `answers2.jsonl` is **not** in
the tree (Fable arm still incomplete; addendum forbids restoring the key before
that arm's predictions are committed).

## Collected

Reconciled 2026-09-16 06:32 UTC against `questions2.jsonl` vs `raw/` (and `raw_fable/`
for the cross-model row only).

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **106** | 100% |
| cross-model arm | `claude-fable-5-1` | 68 | 64% |

**0** Opus qids outstanding.

R39 (formula `C24H21N3S3`) banked from the eighth Cursor Task launch
[bc-0a25b5b0](https://cursor.com/agents/bc-0a25b5b0-4fb3-5564-9bbe-6a9c9b750304)
(`claude-opus-5-thinking-high`; deviation 3). All three candidates RDKit
formula-OK. Seven prior launches on this qid died with empty activity-task
timeouts — not an API/model-quota blocker.

`collect_round.py` (no `--partial`) wrote `predictions2.jsonl`: 106/106 compounds,
302 candidates. One already-banked candidate is off-formula and was kept (R03:
`C10H13N5O2 != C9H11N5O2`).

## Opus scores (from the scripts; not invented)

Key reconstruction (deviation 4): 106/106 committed questions uniquely matched
`irexp_resolved.jsonl.gz` on (formula, IR bands, ¹³C). Strata 53/53. No prior-round
InChIKey-14 collision. Then:

`python scripts/validate_benchmark.py` → `data/benchmark_expand`: **101/106**
spectrally-clean ground truths; 5 flagged (13C-overread): R12, R22, R25, R82, R91.
`clean_qids.json` is the validate snapshot.

`python scripts/benchmark_v2.py score2 --outdir data/benchmark_expand` (all 106,
key present only for that local run):

```
overall recovered (top-3): 68/106 (64%)   top-1 exact: 63/106 (59%)
  simple  : recovered 43/53 (81%)  top1 41/53 (77%)  meanBestTani 0.901
  complex : recovered 25/53 (47%)  top1 22/53 (42%)  meanBestTani 0.670
```

Same InChIKey-14 counters on the validate clean set (n=101; flags were set by
validate before these subset totals were computed):

```
overall recovered (top-3): 65/101 (64%)   top-1 exact: 61/101 (60%)
  simple  : recovered 41/49 (84%)  top1 40/49 (82%)  meanBestTani 0.920
  complex : recovered 24/52 (46%)  top1 21/52 (40%)  meanBestTani 0.663
```

`scripts/score_main.py` still reports the existing n=194 headline and was not
edited. Fable was not scored. `scripts/forward_verify_main.py` was not run
(that is a separate blind ¹³C-prediction campaign).

## Key handling

After scoring, `answers2.jsonl` was moved to
`/tmp/blind/_key/benchmark_expand.answers2.jsonl.withheld` and deleted from the
working tree. Restore for a later Fable-complete scoring pass with:

    python scripts/export_round.py --restore data/benchmark_expand /tmp/blind

Do **not** merge. Do **not** pool Fable into `raw/` or `predictions2.jsonl`.

## Overnight handoff (2026-09-16 06:32 UTC)

**Opus headline: 106/106 deposited. `predictions2.jsonl` committed. Scored locally.
Key re-withheld. Fable 68/106 unscored.**

In flight: none.
