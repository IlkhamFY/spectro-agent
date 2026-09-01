# Pre-registration — IRSpectra-Bench expansion round

Written and committed **before** the draw was run and before any prediction existed. The
size audit (`docs/IRSPECTRA_BENCH_SIZE_AUDIT.md`, §6) names pre-registration as the
discipline the original 140-compound round lacked; this round is drawn under it.

Nothing below may be changed after the draw. If a parameter turns out to be wrong, the
round is discarded and re-drawn under a new pre-registration with a new seed, and both
documents stay in the history.

## Draw

| parameter | value |
|---|---|
| round directory | `data/benchmark_expand/` |
| sampler | `scripts/benchmark_v2.py sample2` (unchanged) |
| n requested | 106 |
| seed | 2026 |
| strata | `n // 2` per stratum — 53 simple, 53 complex, by the RDKit ring/heavy-atom rule already used |
| target cohort after merge | 194 + up to 106 = up to 300 |

## Eligibility — unchanged from the existing rounds

Parseable SMILES; IR, ¹H and ¹³C on one record; 8–60 heavy atoms; at least three
parenthesised entries in each NMR string; the raw ¹H payload with *J* values recoverable
verbatim from the PMC-OA full text of the source article.

## Exclusion

Every InChIKey-14 appearing in any `data/benchmark*/answers*.jsonl` is excluded before the
draw, which is the sampler's existing behaviour. That covers all 194 headline compounds and
every compound revealed in the pilot, electrolyte and control rounds.

## Protocol for the new compounds — unchanged from the main round

Solver agents work blind from formula + IR + ¹H + ¹³C and return **up to three ranked
candidate SMILES**, best first. Bounded contexts, one batch per agent, reset between
batches. No tools beyond an RDKit formula and parse check. No ground truth in context.

**Blindness is enforced structurally, not by instruction.** `data/benchmark*/answers2.jsonl`
are tracked files, so an agent with workspace access can read them — the contamination
vector this paper documents in its own Limitations. Prompts are therefore exported outside
the repository with `scripts/manual_collect.py export` before any solver is invoked, and
solvers are given only the exported prompt text.

## Scoring — unchanged

A prediction is correct if its RDKit InChIKey connectivity layer (first 14 characters)
matches the reference. Top-1 is the first candidate; recall is the true structure appearing
anywhere in the emitted list. `scripts/score_main.py` and `scripts/forward_verify_main.py`
are used as they stand.

## What is *not* pre-registered, and why

No hypothesis about the result. This round exists to enlarge the cohort, not to test a new
claim, and the diagnosis it feeds — how often the true structure is proposed at all — is a
proportion rather than a contrast. If the new compounds behave differently from the
existing 194, that difference is reported as found.

## Stopping rule

The round is complete when every drawn compound has a solver response. Compounds whose
ground truth fails `scripts/validate_benchmark.py` are reported and excluded from the
headline cohort exactly as the six main-round exclusions were — flagged before scoring, not
after seeing whether they were solved.

---

## Deviations log

*Appended after the draw. Everything above this line is the pre-registration as committed
in 3e35a3a and is not edited; deviations are recorded here instead of being written back
into the plan.*

| # | date | deviation | why it does not change the design |
|---|---|---|---|
| 1 | 2026-08-31 | The protocol section names `scripts/manual_collect.py export` as the export step. The round was exported with a purpose-built `scripts/export_round.py` instead. | The binding requirement — prompts leave the repository, and the key is withheld, before any solver runs — is what was carried out, and more strictly than planned: `export_round.py` moves the key to a separate vault rather than leaving it in the round directory, so a solver told to read one batch cannot reach the key by listing the directory it sits in. `manual_collect.py` exports the *main* round's prompts and has no notion of an arbitrary round directory. No draw, eligibility, exclusion, scoring or stopping parameter is affected. |

---

## Addendum — cross-model arm on the same draw

*Written and committed before any Fable solver was invoked. This is an additional arm, not
a change to the expansion round above, which stays on the main-round solver so that its
compounds can be pooled with the 194.*

| parameter | value |
|---|---|
| compounds | the same 106 drawn above, all of them |
| solver | Claude Fable 5.1 (`claude-fable-5-1`), one batch of 6 per fresh context |
| prompt | verbatim the prompt used for the expansion round's solvers |
| tools | RDKit formula and parse check only; no repository access; no web |
| key | withheld throughout, exactly as for the expansion round |
| deposit | `data/benchmark_expand/raw_fable/`, `predictions2_fable.jsonl` — kept apart from `raw/` so nothing from this arm can be pooled with the Opus cohort by accident |
| scoring | unchanged: InChIKey-14 connectivity; top-1 is the first candidate, recall is anywhere in the list |
| reported as | a cross-model replication on post-registration compounds, in the cross-vendor section. **Never** as part of the headline cohort. |

**Why this arm exists.** The manuscript's diagnosis — recall, not verification, is the wall —
is argued to be model-general, and its cross-vendor section rests on compounds drawn before
some of those vendors' training cutoffs. This arm gives one frontier model a draw it
provably could not have seen at benchmark construction time, since the draw postdates
the pre-registration commit. No hypothesis about the result is registered; whatever the
recall/precision decomposition looks like on this model is reported as found.

**What would be a violation.** Pooling any Fable answer into the expansion cohort; re-running
a Fable batch after seeing its score; restoring the key before both arms' predictions are
committed.
