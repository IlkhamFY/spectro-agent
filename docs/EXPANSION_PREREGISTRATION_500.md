# Pre-registration — IRSpectra-Bench expansion toward n=500

Written and committed **before** the draw was run and before any prediction existed.
The +106 expansion round (`docs/EXPANSION_PREREGISTRATION.md`, seed 2026) used this
discipline; this round uses it again. The size audit
(`docs/IRSPECTRA_BENCH_SIZE_AUDIT.md`, §6) names pre-registration as the honest path
past a frozen headline: new blind inference on held-out compounds, parameters fixed
before the sampler runs.

Nothing below may be changed after the draw. If a parameter turns out to be wrong, the
round is discarded and re-drawn under a new pre-registration with a new seed, and both
documents stay in the history. Deviations after the freeze line are logged, not written
back into the plan.

## Why this round

Locked headline today is **n=295** = 194 (main + controls) + 101 validate-clean from
the Opus +106 expansion (5 of 106 flagged 13C-overread and excluded). Reaching n=500
needs about **205** additional spectrally-clean compounds. This draw requests **230**
so that a ~5% 13C-overread flag rate (5/106 in the previous expansion) still leaves
margin: 230 × 0.95 ≈ 218 clean → 295 + 218 ≈ 513.

`scripts/score_main.py` remains the n=194 lock. The ICLR / IRSpectra-Bench paper stays
at **n=295** until this round is 100% deposited, validated, and scored. Partial subsets
are **not scored** and are **not** written into the paper.

## Draw

| parameter | value |
|---|---|
| round directory | `data/benchmark_expand_500/` |
| sampler | `scripts/benchmark_v2.py sample2` (unchanged) |
| n requested | 230 |
| seed | 2026500 |
| strata | `n // 2` per stratum — 115 simple, 115 complex, by the RDKit ring/heavy-atom rule already used |
| target cohort after merge | 295 + validate-clean of these 230, aiming at ~500 |

Command (run only after this document is committed):

```
python scripts/benchmark_v2.py sample2 --n 230 --seed 2026500 --outdir data/benchmark_expand_500
```

Only `questions2.jsonl` is committed. The answer key is withheld before any solver
runs (see Blindness).

## Eligibility — unchanged from the existing rounds

Parseable SMILES; IR, ¹H and ¹³C on one record; 8–60 heavy atoms; at least three
parenthesised entries in each NMR string; the raw ¹H payload with *J* values recoverable
verbatim from the PMC-OA full text of the source article.

## Exclusion

Every InChIKey-14 appearing in any `data/benchmark*/answers*.jsonl` is excluded before
the draw, which is the sampler's existing behaviour. That covers the 194 headline
compounds and every compound revealed in the pilot, electrolyte, and control rounds.

**The +106 expansion key is currently withheld** from the tree (Fable arm on that
round is still incomplete; that round's addendum forbids restoring the key into the
tracked tree until Fable predictions are committed). Before this draw, that key is
**restored locally and not committed**, so those 106 InChIKey-14s sit in the
sampler's exclusion set. After the draw, both the +106 key and this round's key are
re-withheld.

If the local vault at `/tmp/blind/_key/benchmark_expand.answers2.jsonl.withheld` is
empty, the +106 key is reconstructed by unique match of each committed
`data/benchmark_expand/questions2.jsonl` row (formula, IR band list, ¹³C string)
against `data/irexp_resolved/irexp_resolved.jsonl.gz` — the same lost-vault recovery
already recorded as deviation 4 of the +106 round. Reconstruction is used only when
it is 106/106 unique; otherwise this draw does not run.

After the draw, a collision check confirms no InChIKey-14 in
`data/benchmark_expand_500/answers2.jsonl` matches any prior round, including the
+106 expansion. A collision aborts the round (discard, new pre-registration, new
seed).

The eligible held-out pool after those exclusions is the rest of the sampler's
8–60-heavy-atom, J-recoverable quadruples (~28k). This round does not relax
eligibility to enlarge the pool.

## Protocol for the new compounds

Solver agents work blind from formula + IR + ¹H + ¹³C and return **up to three ranked
candidate SMILES**, best first. No tools beyond an RDKit formula and parse check. No
ground truth in context. One batch per agent, reset between batches.

**Headline arm (the only arm that may later pool).** Solver is Claude Opus 5,
served as Cursor Task agents with slug `claude-opus-5-thinking-high` — the same
model family that finished the +106 round. No other model is deposited into
`data/benchmark_expand_500/raw/` or `predictions2.jsonl`.

**Batch size.** Single-compound batches (`scripts/export_round.py --batch 1`). The
+106 round's six-compound batches died on the 64 000 output-token ceiling; halves of
three and then singles finished that round. This round starts at singles so that
failure mode is not re-imported. Context size 1 is inside the 2–12 envelope the
main round already used. A single that itself times out is retried as a single;
it is not enlarged. Provenance records the Cursor agent id per qid.

**No Fable (or any other model) in this headline arm.** A later cross-model
addendum may be written, before that other solver is invoked, and must deposit
apart from `raw/` exactly as the +106 Fable addendum did. Incomplete Fable is
never merged into the headline.

## Blindness

**Blindness is enforced structurally, not by instruction.** Tracked
`data/benchmark*/answers2.jsonl` files are readable by any agent with workspace
access — the contamination vector this paper documents in its own Limitations.
Therefore:

1. Prompts are exported **outside** the repository with `scripts/export_round.py`
   before any solver is invoked.
2. The answer key is moved to a separate vault (`/tmp/blind/_key/`), not beside
   the batches.
3. Solvers are given only the exported prompt text. They are not pointed at the
   working tree, the vault, or any `answers2.jsonl`.
4. `answers2.jsonl` for this round is **not committed** while any arm is
   incomplete. It is not restored into the tracked tree for a convenience score.

## Scoring — unchanged, and not on partials

A prediction is correct if its RDKit InChIKey connectivity layer (first 14
characters) matches the reference. Top-1 is the first candidate; recall is the
true structure appearing anywhere in the emitted list.

`scripts/benchmark_v2.py score2 --outdir data/benchmark_expand_500` scores this
round in isolation. `scripts/validate_benchmark.py` flags 13C-overread (and the
other integrity checks) **before** any clean-subset total is computed.

**Do not score a partial subset.** `scripts/collect_round.py` writes
`predictions2.jsonl` only at 100% deposit; `--partial` banks `raw/` only. No
top-1 / recall number for this round exists until every drawn compound has a
response. No partial number is written into the ICLR paper, `STATUS.md` score
tables, or `scripts/score_main.py`.

Pooling into n≈500 is a **separate step after** 100% deposit + validate + score2,
via `scripts/score_pooled.py`. That script does not rewrite `score_main.py`
(n=194). It does not run against an unfinished `raw/` tree. It does not invent
CIs. Until it has been run on a complete round, the paper headline stays n=295.

## What is *not* pre-registered, and why

No hypothesis about the result. This round exists to enlarge the cohort, not to
test a new claim. If the new compounds behave differently from the existing 194
or from the +106 expansion, that difference is reported as found.

Forward-verification (`scripts/forward_verify_main.py`) is a separate blind
¹³C-prediction campaign. It is not part of this draw, and no verification-precision
number for this round is registered or will be invented.

## Stopping rule

The round is complete when every drawn compound has a solver response. Compounds
whose ground truth fails `scripts/validate_benchmark.py` are reported and excluded
from the headline cohort exactly as the six main-round exclusions and the five
+106 expansion flags were — flagged before scoring, not after seeing whether they
were solved.

If a run cannot finish all 230 solves, it deposits what it has, leaves an exact
outstanding-qid list, and stops. That is an unfinished round, not a result.

---

## Deviations log

*Appended after the draw. Everything above this line is the pre-registration as
committed and is not edited; deviations are recorded here instead of being written
back into the plan.*
