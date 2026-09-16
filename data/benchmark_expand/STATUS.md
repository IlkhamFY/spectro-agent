# Expansion round — status

**Do not merge this branch (PR #18) until Ilkham reviews.** Opus deposits are
complete; the round is an **independent pre-registered replication**, not a silent
replacement of the n=194 headline. Pooling to ~300 is licensed by the
pre-registration *after* the round is complete, and is a **morning decision**, not
an overnight merge.

**Opus deposits: 106/106.** `predictions2.jsonl` is committed. Scored locally under
the pre-registered InChIKey-14 rule. `answers2.jsonl` is **not** in the tree (Fable
arm still incomplete; addendum forbids restoring the key before that arm's
predictions are committed).

Source of the numbers below: committed `STATUS.md` / `score2` / `validate_benchmark.py`
on 2026-09-16. **Do not invent CIs, vendor numbers, or pooled-cohort metrics.**

Companion write-up: `docs/EXPANSION_RESULTS_2026-09-16.md`.
Pre-registration (frozen above the deviations line): `docs/EXPANSION_PREREGISTRATION.md`.

## Collected

Reconciled 2026-09-16 06:32 UTC against `questions2.jsonl` vs `raw/` (and `raw_fable/`
for the cross-model row only).

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **106** | 100% |
| cross-model arm | `claude-fable-5-1` | 68 | 64% |

**0** Opus qids outstanding. Fable remaining qids: `outstanding_fable.txt` (38/106).

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

| set | n | top-1 | recall (top-3) | simple top-1 | complex top-1 |
|---|---:|---|---|---|---|
| all deposited Opus | 106 | **63/106 (59%)** | **68/106 (64%)** | 41/53 (77%) | 22/53 (42%) |
| validate-clean subset | 101 | **61/101 (60%)** | **65/101 (64%)** | 40/49 (82%) | 21/52 (40%) |

Same InChIKey-14 counters on the validate clean set (n=101; flags were set by
validate before these subset totals were computed):

```
overall recovered (top-3): 65/101 (64%)   top-1 exact: 61/101 (60%)
  simple  : recovered 41/49 (84%)  top1 40/49 (82%)  meanBestTani 0.920
  complex : recovered 24/52 (46%)  top1 21/52 (40%)  meanBestTani 0.663
```

Flagged 13C-overread (excluded from the clean subset, **not** from the all-106
row): **R12, R22, R25, R82, R91**.

`scripts/score_main.py` still reports the existing n=194 headline and was not
edited. Fable was not scored. `scripts/forward_verify_main.py` was not run
(that is a separate blind ¹³C-prediction campaign).

## Deviations (see pre-registration log)

| # | what happened | consequence for morning review |
|---|---|---|
| 3 | Remaining Opus compounds, including **R39 on the eighth launch**, solved as single-compound Cursor Task agents served as `claude-opus-5-thinking-high`. Seven prior R39 launches died empty. | Same model family, prompt, tools, key withholding, InChIKey-14 scoring. Context size 1 is inside the 2–12 envelope. |
| 4 | After `predictions2.jsonl` was committed, the withheld key was **reconstructed** by unique (formula, IR, ¹³C) match against `irexp_resolved.jsonl.gz` because `/tmp/blind/_key` was empty on this VM. `validate` + `score2` were run locally. The key was then **re-withheld** (`answers2.jsonl` deleted from the working tree; not committed). | Draw / scoring rule unchanged. 106/106 unique matches, strata 53/53, no prior-round InChIKey-14 collision. Fable addendum still forbids restoring the key into the tree. |

Deviations 1–2 (export script; batch halves) are historical and already in
`docs/EXPANSION_PREREGISTRATION.md`.

## Key handling

After scoring, `answers2.jsonl` was moved to
`/tmp/blind/_key/benchmark_expand.answers2.jsonl.withheld` and deleted from the
working tree. Restore for a later Fable-complete scoring pass with:

    python scripts/export_round.py --restore data/benchmark_expand /tmp/blind

Do **not** merge. Do **not** pool Fable into `raw/` or `predictions2.jsonl`.
Do **not** commit `answers2.jsonl`. Confirm `git ls-files data/benchmark_expand/answers2.jsonl`
is empty before any merge.

## What is not done (do not invent)

| item | status |
|---|---|
| Opus deposits | **106/106** committed |
| Opus InChIKey-14 score2 | **done** (tables above) |
| validate_benchmark.py | **done** (101/106 clean) |
| Fable deposits | 68/106; **not scored** |
| `forward_verify_main.py` on expansion | **not run** |
| pooled cohort ~300 / `score_main.py` n=194 | **untouched**; pool is a review decision |
| figure rebuilds (`fig_wall`, diagnosis.json) | **not done**; need forward-verify + Ilkham OK |
| CIs on the 106 | **not computed**; do not invent |

## Pooling policy (pre-reg)

The pre-registration licenses a pooled cohort of **up to 300** (194 + up to 106)
**after** the expansion round is complete. Report the 106 as an **independent
replication first**. Do not rewrite headline n=194 tables, CIs, or figures until
forward-verification of the expansion round has been run **and** Ilkham signs off
on pooling.

## Morning checklist (2026-09-16)

Ilkham is reviewing; nothing below is overnight-mandatory except the first two.

1. **Do not merge PR #18.** Key is out of tree; Fable arm incomplete; pool not decided.
2. Confirm `answers2.jsonl` is still absent from `data/benchmark_expand/` and from `git ls-files`.
3. **Fable finish — optional.** Remaining 38 qids in `outstanding_fable.txt`. Do not restore the key until `predictions2_fable.jsonl` is committed. Do not pool Fable into the Opus cohort.
4. **Forward-verify** the expansion Opus candidates (`scripts/forward_verify_main.py` generalised to this round). This is a separate blind ¹³C-prediction campaign; it has **not** been run. No expansion verification-precision number exists yet.
5. **Pool decision (Ilkham).** After (4), decide whether to fold validate-clean expansion compounds into the headline cohort (up to ~300) and rebuild `fig_wall` / diagnosis sidecars / manuscript n=194 tables. Until that OK, keep n=194 as the headline and the 106 as replication.
6. Manuscript draft lives on IRSpectra-Bench (separate PR): expansion numbers as independent round only; double-blind locks stay on; no invented CIs.

## Overnight handoff (2026-09-16)

**Opus headline: 106/106 deposited. `predictions2.jsonl` committed. Scored locally.
Key re-withheld. Fable 68/106 unscored. n=194 untouched. Do not merge.**

In flight: none.
