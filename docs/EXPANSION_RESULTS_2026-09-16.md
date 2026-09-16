# Expansion round results — 2026-09-16

**Paper-facing pooled headline (n=295 generation) is
`docs/POOLED_HEADLINE_2026-09-16.md`.** This file stays the frozen expansion-round
snapshot (106/106 Opus, score2, validate flags). It is not the ICLR headline.

Frozen snapshot of the pre-registered IRSpectra-Bench expansion round
(`data/benchmark_expand/`), written after Opus 106/106 deposits were scored.
**Every count below is copied from committed `data/benchmark_expand/STATUS.md`
and the `validate_benchmark.py` / `benchmark_v2.py score2` output recorded
there.** No confidence intervals, vendor numbers, pooled-cohort metrics, or
forward-verification rates are invented.

Pre-registration (draw, eligibility, scoring, stopping rule; deviations appended
below the freeze line): `docs/EXPANSION_PREREGISTRATION.md`.
Live status file: `data/benchmark_expand/STATUS.md`.
spectro-agent PR: **#18** on `claude/funny-maxwell-u5S31` — **do not merge**
until Ilkham reviews.

## How to read this round

Report the 106 as an **independent pre-registered replication** of the n=194
headline. The pre-registration licenses pooling into a cohort of **up to 300**
(194 + up to 106) *after* the round is complete; that pool, and any figure
rebuild, waits on expansion forward-verification **and** Ilkham's OK. Existing
`scripts/score_main.py` n=194 numbers were not edited.

## Collection

Reconciled 2026-09-16 06:32 UTC against `questions2.jsonl`.

| arm | solver | compounds with a blind response | of 106 |
|---|---|---:|---:|
| expansion round | `claude-opus-5` | **106** | 100% |
| cross-model arm | `claude-fable-5-1` | 68 | 64% |

`predictions2.jsonl` is committed: 106/106 compounds, 302 candidates.
Fable deposits stay in `raw_fable/`; they are **not** pooled into `raw/` or
`predictions2.jsonl`. Fable is **not scored**.

## Opus InChIKey-14 scores (`score2`)

Scoring rule (pre-registered, unchanged): RDKit InChIKey connectivity layer
(first 14 characters). Top-1 is the first candidate; recall is the true
structure anywhere in the emitted list.

| set | n | top-1 | recall (top-3) |
|---|---:|---|---|
| all deposited Opus | 106 | **63/106 (59%)** | **68/106 (64%)** |
| validate-clean subset | 101 | **61/101 (60%)** | **65/101 (64%)** |

By stratum (all 106; 53/53 as drawn):

| stratum | n | top-1 | recall (top-3) | mean best Tanimoto |
|---|---:|---|---|---:|
| simple | 53 | 41/53 (77%) | 43/53 (81%) | 0.901 |
| complex | 53 | 22/53 (42%) | 25/53 (47%) | 0.670 |

By stratum (validate-clean n=101; flags set by validate *before* these subset
totals were computed):

| stratum | n | top-1 | recall (top-3) | mean best Tanimoto |
|---|---:|---|---|---:|
| simple | 49 | 40/49 (82%) | 41/49 (84%) | 0.920 |
| complex | 52 | 21/52 (40%) | 24/52 (46%) | 0.663 |

Script transcript as committed:

```
overall recovered (top-3): 68/106 (64%)   top-1 exact: 63/106 (59%)
  simple  : recovered 43/53 (81%)  top1 41/53 (77%)  meanBestTani 0.901
  complex : recovered 25/53 (47%)  top1 22/53 (42%)  meanBestTani 0.670

overall recovered (top-3): 65/101 (64%)   top-1 exact: 61/101 (60%)
  simple  : recovered 41/49 (84%)  top1 40/49 (82%)  meanBestTani 0.920
  complex : recovered 24/52 (46%)  top1 21/52 (40%)  meanBestTani 0.663
```

No bootstrap CIs were computed for this round. Do not fill them in from the
n=194 intervals.

## Ground-truth audit (`validate_benchmark.py`)

| | count |
|---|---:|
| drawn | 106 |
| spectrally clean | **101** |
| flagged 13C-overread | **5** |

Flagged qids: **R12, R22, R25, R82, R91**. Snapshot: `clean_qids.json`.

Stopping rule (pre-reg): compounds whose ground truth fails validate are
reported and excluded from a *headline* cohort exactly as the six main-round
exclusions were — flagged before scoring, not after seeing whether they were
solved. The all-106 row above is the deposited-round score; the n=101 row is
the clean subset.

## What was not run

| item | status |
|---|---|
| Fable scoring | not scored (68/106 deposits only) |
| `scripts/forward_verify_main.py` on this round | **not run** |
| expansion verification precision \| recall | **does not exist yet** |
| `scripts/score_main.py` headline | still n=194 |
| pooled n≈300 tables / `fig_wall` rebuild | **not done** |

## Deviations (do not rewrite the pre-reg body)

Copied from the deviations log in `docs/EXPANSION_PREREGISTRATION.md` and the
STATUS narrative. The freeze line in the pre-registration is not edited.

| # | date | deviation | why the design is unchanged |
|---|---|---|---|
| 1 | 2026-08-31 | Export used `scripts/export_round.py` rather than `manual_collect.py export`. | Prompts left the repo; key withheld in a separate vault. |
| 2 | 2026-09-09 | Some six-compound batches re-exported as halves of three (`batch_NNa`/`NNb`). | Context size stays inside the 2–12 envelope already used on the headline cohort. |
| 3 | 2026-09-16 | Remaining Opus compounds solved as single-compound Cursor Task agents served as `claude-opus-5-thinking-high`. **R39** (`C24H21N3S3`) banked on the **eighth** launch (`bc-0a25b5b0`); seven prior launches died with empty activity-task timeouts. All three R39 candidates RDKit formula-OK. | Same model family, prompt, tools (RDKit formula/parse only), key withholding, InChIKey-14 scoring. Context size 1 is inside the existing envelope. |
| 4 | 2026-09-16 | After Opus `predictions2.jsonl` was committed, the withheld key was **reconstructed** by unique match of each committed question (formula, IR band list, ¹³C string) against `data/irexp_resolved/irexp_resolved.jsonl.gz`, because `/tmp/blind/_key` was empty on this VM. `validate_benchmark.py` and `score2` were run locally. `answers2.jsonl` was then **re-withheld** (not committed): the Fable addendum forbids restoring the key into the tree before that arm's predictions are committed (Fable is still 68/106). | Lost-vault recovery, not a re-draw: 106/106 unique matches, strata 53/53, no prior-round InChIKey-14 collision. Key remains outside the working tree. |

One already-banked candidate is off-formula and was kept (R03:
`C10H13N5O2 != C9H11N5O2`).

## Key handling (merge-blocking)

`answers2.jsonl` is **not** in the working tree. Restore only for a
Fable-complete scoring pass:

```
python scripts/export_round.py --restore data/benchmark_expand /tmp/blind
```

Confirm before any merge:

```
git ls-files data/benchmark_expand/answers2.jsonl   # must be empty
```

## Morning checklist

1. **Do not merge spectro-agent PR #18** until Ilkham reviews.
2. Confirm the expansion key is still withheld.
3. **Fable finish — optional.** 38 qids remain (`outstanding_fable.txt`). Do not
   restore the key until Fable predictions are committed. Never pool Fable into
   the Opus expansion cohort.
4. **Forward-verify** expansion Opus candidates. No verification-precision
   number for this round exists until that campaign finishes.
5. **Pool decision (Ilkham).** Only after (4): whether to fold validate-clean
   expansion compounds into the headline (up to ~300) and rebuild figures /
   n=194 tables / CIs together. Until then, keep n=194 as the manuscript
   headline and this 106 as independent replication.
6. ICLR draft (IRSpectra-Bench, separate PR) may cite the tables above as a
   replication subsection. It must not replace headline n=194, invent CIs, or
   break double-blind locks.

## Locked facts (do not drift)

| item | value |
|---|---|
| Opus deposits | 106/106 |
| `predictions2.jsonl` | committed |
| top-1 / recall (all 106) | 63/106 (59%) / 68/106 (64%) |
| simple / complex top-1 | 41/53 (77%) / 22/53 (42%) |
| validate clean | 101/106; flags R12, R22, R25, R82, R91 |
| clean top-1 / recall | 61/101 (60%) / 65/101 (64%) |
| Fable | 68/106 deposits; not scored |
| forward-verify (expansion) | not run |
| `score_main.py` headline | n=194, untouched |
| answers2.jsonl | re-withheld; do not restore for merge |
| PR #18 | open; do not merge overnight |
