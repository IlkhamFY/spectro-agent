This document records the operational detail behind the article: which model answered
which experimental arm and when ([@sec:esi-models]), the prompts and agent protocol
([@sec:esi-prompts]), how the 194-compound benchmark was assembled ([@sec:esi-benchmark]),
what the correctness criterion accepts and rejects ([@sec:esi-scoring]), the construction
of the forward-verification arm ([@sec:esi-forward]) and of the two non-LLM verifiers
([@sec:esi-verifiers]), the four-vendor replication ([@sec:esi-cross-vendor]), the
contamination controls ([@sec:esi-ablation]), and the frozen human-expert audit package
([@sec:esi-audit]). Where the repository does not pin a value, this document says so
rather than supplying one. It condenses the companion technical notes released with the
manuscript — `docs/MODELS.md`, `docs/BENCHMARK.md`, `docs/FORWARD_VERIFY.md`,
`docs/CROSS_VENDOR.md`, `docs/VERIFIER_PROBE.md`, `docs/MODALITY_ABLATION.md` and
`docs/EXPERT_AUDIT_PROTOCOL.md` — and every number in it is copied from one of them or
from a released data file.

## Models, versions and collection windows {#sec:esi-models}

Every LLM result in the article was produced by Anthropic Claude models invoked as
independent sub-agents through the Agent tool under a single consumer claude.ai
subscription: no paid API, no fine-tuning, and no model training in the core protocol.
The two trained probes — the learned ¹³C verifier of [@sec:non-llm-verifiers-deterministic]
and the generator of [@sec:recall-wall-task-intrinsic] — are not Claude models and are
described in [@sec:esi-verifiers] and in `contrib/generator_probe/`.

**Table {#tab:esi-runs}. Which model answered which arm, and when.** "Collected" is the
UTC author-date of the commit that first added the prediction artifact; the history is
linear and each raw agent-output file was committed once, in the session that produced
it, so first-add is the best available proxy for collection time. It is a proxy, not a
timestamp emitted by the harness.

| arm | model | data directory | collected (UTC) |
|--------------------------------------------|-------------|-------------------------------|--------------------|
| pilot, n=21, single context, no tools | Claude Opus 4.8 | `data/benchmark/` | 2026-06-09 04:40 |
| within-compound control, arm (a): n=20, one context, no tools | Claude Opus | `data/benchmark_v2/` | 2026-06-09 06:28 |
| controlled round v3, n=40, decoupled agents | Claude Opus | `data/benchmark_v3/` | 2026-06-09 06:47–07:37 |
| within-compound control, arm (b): same n=20, 4 agents of 5 compounds, RDKit formula check | Claude Opus | `data/benchmark_v2_ctrl/` | 2026-06-09 17:43 |
| forward verification: 8 blind forward-prediction agents, 126 candidates, 60 compounds | Claude Opus | `data/fverify/` | 2026-06-09 19:51 |
| generate-wide: 10 solver agents, 6 compounds each, up to 6 candidates per compound | Claude Opus | `data/gw/` | 2026-06-10 18:15 |
| forward verification of the widened pool: 4 agents, 65 new candidates | Claude Opus | `data/fverify2/` | 2026-06-10 18:19 |
| cross-model recall check on V3-R01…R12 (n=12), identical blind 6-candidate protocol | Claude Sonnet | `data/gw/raw/sonnet_b1.json`, `sonnet_b2.json` | 2026-06-10 18:33–18:38 |
| headline main round, 140 problems (134 spectrally validated), decoupled agents | Claude Opus | `data/benchmark_main/raw/` | 2026-06-11 06:48–09:16 |
| four-model comparison, fixed 24-compound subset | Claude Haiku | `data/benchmark_main/haiku/` | 2026-06-11 16:16 |
| four-model comparison, same subset | Claude Sonnet | `data/benchmark_main/sonnet/` | 2026-06-11 16:41–17:10 |
| electrolyte subset, 48 curated / 46 scored, 8 batches | Claude Opus | `data/benchmark_electrolyte/` | 2026-06-11 18:29–18:43 |
| four-model comparison, same subset | Claude Fable 5 | `data/benchmark_main/fable/` | 2026-06-11 23:06–23:32 |
| formula-only contamination control, same 60 compounds, spectra masked | Claude Opus | `data/modality/` | 2026-07-28 18:37 |
| forward verification extended to the whole benchmark: 15 agents, 247 main-round candidates | Claude Opus | `data/fverify_main/` | 2026-08-07 02:45–02:53 |
| generate-wide coverage gap closed: 9 agents, the 152 wide candidates that had no prediction | Claude Opus | `data/fverify_gw/` | 2026-08-07 03:20–03:30 |
| trained-generator arm re-run: 5 agents, 75 outstanding candidates | Claude Opus | `data/fverify_gen/` | 2026-08-07 03:55–04:05 |
| cross-vendor sweep, non-Claude models ([@sec:esi-cross-vendor]) | see [@tab:esi-vendor-generation] | `sweep_out/` | 2026-08-13 to 2026-08-17 |

### Access windows {#sec:esi-windows}

Claude invocations fall into three dated windows, listed separately because no single
window covers them.

1. **Main solver window, 2026-06-09 to 2026-06-11 (UTC).** Every candidate structure
   behind the headline results — [@sec:headline-performance] top-1 and recall,
   [@sec:methodology-dominates-within-compound], [@sec:model-comparison-benchmark-ranks],
   [@sec:domain-case-study-battery], and the candidate pools that all of
   [@sec:forward-verification-elucidation] re-ranks — was generated here. No headline
   elucidation artifact exists outside it.
2. **Formula-only contamination control, 2026-07-28.** This arm re-solves the same 60
   compounds with the spectra masked, so it does generate new candidate structures (3/60
   correct) outside window 1 — by design, since the control only means anything as a
   fresh run. It affects [@sec:model-reading-spectra-formula] and
   [@tab:formula-only-control] alone and changes no headline number.
3. **Forward-prediction additions, 2026-08-07.** Three of them: the
   [@sec:result] extension to all 194 compounds, the
   [@sec:generate-wide-testing-recipe] coverage-gap closure, and the
   [@sec:recall-wall-task-intrinsic] re-run whose original outputs were lost. These
   predict ¹³C for candidates the June solver had already produced; none introduces a new
   candidate structure or moves a recall number. The
   [@sec:recall-wall-task-intrinsic] re-run does change that arm's verified top-1, because
   the number it replaces was never reproducible.

All other later commits re-score frozen outputs and re-query no model.

### Version strings, snapshots and decoding parameters {#sec:esi-versions}

`Claude Opus 4.8` is the only Claude version string anywhere in the repository, and it is
evidenced only for the 2026-06-09 pilot (`docs/BENCHMARK.md`). It is a display version,
not a snapshot identifier: it does not pin a checkpoint. `Fable 5` appears as a display
name for the strongest comparison model. **No version number of any kind appears for
Claude Sonnet or Claude Haiku**, and no dated snapshot identifier exists for any of the
four: the consumer harness exposes no checkpoint identifier to the caller, announces no
build changes, and records nothing about which build served a given request. Consequently
two numbers drawn from the same window are known to come from the same window and *not*
known to come from the same build — **a mid-window build change cannot be excluded**, and
the article does not claim the pilot build served the main round two days later.

**No sampling parameters were set for any run, and none are recorded.** There is no
temperature, `top_p`, `top_k`, `max_tokens`, seed or thinking-budget value in any script,
document, config or committed artifact. The `seed=` values that do appear are for analysis
determinism only — bootstrap resampling, benchmark sampling, audit-sample selection — not
for generation. Reproduction is therefore distributional, not exact.

One protocol asymmetry follows from how the arms were assembled and is stated here because
[@sec:methodology-dominates-within-compound] measures a large effect of exactly that
variable. The Opus column of the four-model comparison is **not a fresh 24-compound run**:
it re-scores the main-round Opus predictions on the fixed subset (the `SRC` map in
`scripts/score_models.py`), and those 24 items came from one 6-compound context
(`raw/b1.json`) and two 12-compound contexts (`raw/redo_b23.json`, `raw/redo_b45.json`),
whereas Sonnet, Haiku and Fable each saw four 6-compound contexts. The prompts and the
compound set are identical; the context packing is not.

## Prompts and agent protocol {#sec:esi-prompts}

**What the solver was shown.** The molecular formula (as from HRMS), the IR band list, and
the ¹H and ¹³C shift lists with multiplicities and J-couplings where the source paper
reported them. **What it was not shown:** the compound name, any SMILES, any starting
material or scaffold hint, the ground truth, and any other benchmark record. Solver agents
were closed-book: no web access, no ground-truth access, and no tools beyond an RDKit
molecular-formula/parse check. The arm (a) baseline of
[@sec:methodology-dominates-within-compound] had no tools at all — that is the variable it
isolates. Closed-book status was audited by grep over the task transcripts at run time;
the transcripts themselves are not committed, so a reader cannot re-verify that audit from
the release, and the article says so ([@sec:limitations]).

**Candidate budget.** Up to **three ranked candidate SMILES per compound**, best first, in
every arm except generate-wide, where ten independent solver agents each proposed up to
**six regiochemistry-aware candidates per compound** and the pools were merged. Scoring
reads at most the first three candidates for top-1 and recovered (top-3); generation
recall reads the whole pool ([@sec:esi-scoring]).

**Context discipline.** Each solver agent handled one small batch in a bounded context
that was reset between batches: 6 compounds per released batch file
(`data/benchmark_main/batch_*.txt`, 23 files, 22 of 6 compounds plus 1 of 2 = the 134
spectrally-validated problems), with some batch pairs merged into a single 12-compound
context (`data/benchmark_main/raw/redo_*.json`). The range actually released is **2–12
compounds per context**.

**Forward-prediction (verifier) agents** had **zero tools**, pure reasoning, and were
blind: anonymised SMILES only, pooled across compounds, canonicalised, de-duplicated,
shuffled and re-labelled, in fixed batches of 17. They never saw the observed spectrum,
the compound's identity, or which candidates belong to the same target. Shuffling does not
keep a target's own candidates in separate batches — in the [@sec:result] arm 7 of 8
batches held two candidates for some one compound — but with no observed spectrum in hand
there is nothing for that to leak; at most a predictor can notice that two structures are
isomers, which is evident from either alone.

**Verbatim prompts.** The blind elucidation prompt and the forward-prediction prompt are
committed as `sweep_prompts/solve_01.md` … `solve_10.md` and `sweep_prompts/verify/`, and
are emitted by `scripts/cross_vendor_sweep.py`. The elucidation header, verbatim:

```
# Blind structure-elucidation task

You are given real experimental spectra (from the published literature) for a set of
organic molecules. For EACH compound you are given the molecular formula (from HRMS),
the IR band list, and the 1H and 13C NMR shift lists. No name, SMILES, or hint is given.

For each compound, propose the 3 most likely structures, best first, as SMILES.

Rules:
  - Use only the spectra provided. Do not use external lookups or tools.
  - Candidates must match the given molecular formula exactly.
  - Order candidates by your own confidence (most likely first).

Return ONLY a JSON object mapping each id to a list of 3 SMILES strings, e.g.:
  {"M001": ["CCO", "COC", "..."], "M002": ["...", "...", "..."], ...}

Compounds:
```

The forward-prediction header, verbatim:

```
# Forward 13C prediction task

For each candidate structure below (given as SMILES), predict its 13C NMR chemical
shift list (in ppm) from the structure alone. This is the forward direction only:
you are NOT given any observed spectrum and must not assume one.

Return ONLY a JSON object mapping each id to a list of predicted 13C shifts (numbers
in ppm), e.g.: {"P001": [21.0, 60.5, 171.2], "P002": [...], ...}

Candidates:
```

Each compound then appears as one block, in this exact form (the NMR strings are the
source paper's own text, reproduced unedited, which is why the ¹³C field carries the
chemical-shift symbol and any assignment annotations the authors wrote):

```
### M001
Molecular formula: <formula>
IR bands (cm-1): <list of wavenumbers>
1H NMR: <string as reported>
13C NMR: <string as reported>
```

The released per-arm batch files carry the real blocks: `data/benchmark_main/batch_*.txt`
and `data/gw/batch_*.txt` for solving, `data/fverify_main/fbatch_*.txt` and
`data/fverify_gw/gbatch_*.txt` for forward prediction, and
`data/modality/prompt_full.txt` and `prompt_formulaonly.txt` for the contamination control
(whose blocks carry the formula line alone).

**One gap, stated rather than papered over.** The wording above is the harness prompt used
verbatim for the four-vendor replication ([@sec:esi-cross-vendor]) and it is the only
instruction text committed in the repository. The Claude sub-agents of the headline arms
were dispatched through the Agent tool with their instruction supplied at dispatch, and
**that instruction text was not captured**. What is released for those arms is the
per-compound data exactly as the agents received it, the candidate budget, the tool
policy and the context sizes given above.

## Benchmark construction {#sec:esi-benchmark}

IRSpectra-Bench is drawn from `irexp_resolved`, the 43,060-record structure-complete split
of IRexp. A record enters the sampling pool only if it carries an IR band list, a ¹H shift
list, a ¹³C shift list and a resolved structure; the structure has **8–60 heavy atoms**;
each NMR string carries at least three parenthesised entries; and the raw ¹H string,
re-fetched from the source article, contains genuine J information. Sampling is balanced
between the two difficulty strata, and every compound already revealed in any prior round
is excluded by InChIKey-14 before the draw, so no compound appears in two rounds
(`scripts/benchmark_v2.py`).

**Table {#tab:esi-cohort}. Rounds behind the n=194 cohort.**

| round | data directory | problems | in the cohort | role |
|-------------------|-------------------------------|---------:|--------------:|--------------------------------------|
| main | `data/benchmark_main/` | 140 | 134 | headline, spectrally validated |
| controlled v3 | `data/benchmark_v3/` | 40 | 40 | difficulty control, pre-registered |
| within-compound control | `data/benchmark_v2_ctrl/` | 20 | 20 | context/tooling control, pre-registered |
| electrolyte case study | `data/benchmark_electrolyte/` | 48 | — | domain subset, 46 scored, held apart |

**What was excluded, and why.** Every main-round ground truth passes an automated RDKit
self-consistency check — ¹³C peak count against symmetry-unique carbons, molecular-formula
match, SELFIES round-trip — which excluded 6 of 140 records: five report more ¹³C peaks
than the structure has carbons (R03 28>24, R14 11>8, R65 26>18, R67 23>16, R131 34>17,
i.e. merged or contaminated spectra) and one is too sparse to constrain (R82, 5 peaks for
22 symmetry-unique carbons). The two controlled rounds are used **whole**, because they
were fixed and pre-registered as controls before the audit existed; the same audit is
reported on them rather than applied (57/60 pass). This asymmetry is deliberate, and
[@sec:headline-performance] reports the strictly-validated 191-compound cohort as a
robustness check. The filter runs over all three rounds in
`scripts/validate_benchmark.py`, which regenerates every `clean_qids.json` from the
released questions and answers.

The filter tests ¹³C against the carbon count and does not gate on ¹H. In **13 of the 194**
retained records the total reported ¹H integral exceeds the hydrogen count of the reference
structure — residual solvent, water, exchangeable protons or a reported rotamer mixture.
These are printed as a diagnostic rather than excluded, because the cohort was fixed in
advance; dropping all 13 moves the headline from 28.4% to 29.3% (53/181).

**Complexity stratification, and when it was defined.** Difficulty is a declared property
of the compound, assigned by RDKit ring analysis at sampling time — before any structure
was solved — and it is exhaustive by construction, so nothing falls between the classes. A
compound is **complex** if it has a spiro atom, a bridgehead atom, three or more rings, any
fused ring system, **or** more than 24 heavy atoms; it is **simple** if it has at most two
rings and at most 22 heavy atoms; anything else (the 23–24 heavy-atom band, 13 compounds)
is complex on size alone. The cohort splits 98 simple / 96 complex. The 22-atom threshold
is not load-bearing: sweeping it from 18 to 26 moves the simple-minus-complex top-1 gap
only between 36 and 40 points, against 39.6 at the released value
(`scripts/difficulty_sensitivity.py`). This binary axis is distinct from the continuous
heavy-atom bands (≤15 / 16–25 / >25) used in [@sec:headline-performance] and [@sfig:size].

The battery-electrolyte subset ([@sec:domain-case-study-battery]) was drawn from the same
corpus by SMARTS substructure filters for six electrolyte functional classes, balanced to
eight compounds per class (48 curated; 46 scored after two yielded no parseable candidate),
J-enriched and spectrally validated identically to the main rounds, and excluding every
compound used elsewhere in the paper.

## Scoring: what the correctness criterion accepts and rejects {#sec:esi-scoring}

A prediction is **correct** if the first 14 characters of the RDKit InChIKey computed from
its SMILES equal those of the reference — the InChIKey **connectivity layer**. That block
hashes the molecular skeleton: which atoms are bonded to which. The later blocks, which
carry stereochemistry, isotopic substitution and protonation state, are not compared.
Top-1 asks this of the first-ranked candidate; recovered (top-3) asks it of the up-to-three
returned; generation recall asks it of the whole candidate pool. Nothing in the criterion
is model-mediated: it is RDKit only, in `scripts/score_main.py` and
`scripts/specmetrics.py`. Alongside it we report Morgan(2, 2048) Tanimoto as a graded
"right family" signal, with 0.45 as the scaffold-level threshold; confidence intervals are
bootstrap 95% over compounds (2,000 resamples, analysis seed 0) and model-vs-model
comparisons use McNemar's exact test with Holm correction.

**What it accepts.** A candidate with the correct constitution and the wrong
stereochemistry is scored correct. This is a deliberate floor rather than an assumption
that stereochemistry is immaterial, and the article measures the cost: re-scoring the
*full* InChIKey gives **21.1% top-1 and 25.8% recovered (41/194 and 50/194)** against
28.4% / 33.5% at the connectivity layer, so 14 top-1 answers are accepted here that a
stereochemistry-sensitive scorer rejects. The reason for the floor is that 1D ¹H/¹³C/IR
rarely fixes absolute configuration and only 10.3% (20/194) of the answers carry a defined
(assigned R/S) stereocentre, so a model would be penalised for information the prompt never
contained. The cross-vendor arm shows what this looks like per compound: on structures
those models got constitutionally right whose reference carries assigned stereocentres,
Grok 4.6 reproduced 0/3 correct descriptors, Gemini 3.7 Flash 0/2 and GPT-5.6 Sol 0/2 —
each of them an accepted answer at the connectivity layer.

**What it rejects.** Every constitutional isomer, however close, and every structure of the
wrong composition. Three worked cases, all from the released artifacts:

- *A regioisomer the verifier separates.* Picolinamide and nicotinamide differ only in
  which ring position bears the carboxamide. They have different connectivity layers, so
  proposing one for the other scores zero, and forward-predicted ¹³C separates them at a
  chamfer of 0.42 ppm against 1.30 ppm ([@sec:method], [@fig:fig-mechanism]).
- *A regioisomer it does not.* On the 2-(nitrophenyl)-2,3-dihydroquinazolin-4(1*H*)-one
  targets (C₁₄H₁₁N₃O₃) the forward predictor cannot resolve the *ortho*- and
  *meta*-nitrophenyl isomers: it ranks the 2-nitrophenyl isomer first at a chamfer of
  1.35 ppm against 1.36 ppm for the true 3-nitrophenyl one, a 0.01 ppm margin. The answer
  is rejected, as it must be.
- *A pilot miss of the same kind.* The n=21 pilot returned the correct
  *N*-allyl-2-(pyridinecarbonyl)hydrazinecarbothioamide skeleton with the **3-pyridyl**
  isomer where the truth is **2-pyridyl** (`docs/BENCHMARK.md`, Q21): right formula, right
  scaffold, rejected.

This is the dominant shape of failure rather than an edge case. Over all 139 top-1 misses,
**76.6% are constitutional isomers of the true structure** and 23.4% have the wrong
molecular formula outright; 22.6% share the true Murcko scaffold, 2.9% reach Tanimoto
≥ 0.85, and the median Tanimoto between an isomeric miss and the truth is 0.39
(`scripts/analyze_misses.py`). Formula adherence is not part of the criterion — an answer
of the wrong composition is simply a miss — and it is not uniform across rounds: on top-1
answers it is 95.0% (38/40) in the v3 round, 90.0% (18/20) in the within-compound control
and 77.6% (104/134) in the headline main round.

## Forward-verification detail {#sec:esi-forward}

**The distance.** Candidates are ranked by a symmetric chamfer distance between the
forward-predicted and the observed ¹³C peak sets. It is a mean of two nearest-neighbour
means, so it imposes no equal-count requirement between predicted and observed peaks, and
lower is better. The implementation is nine lines and is the single source of truth for
every scorer and diagnostic (`scripts/specmetrics.py`):

```
def chamfer(pred, obs):
    """Symmetric chamfer distance between predicted and observed 13C shift lists."""
    if not pred or not obs:
        return 999.0
    a = sum(min(abs(x - y) for y in obs) for x in pred) / len(pred)
    b = sum(min(abs(y - x) for x in pred) for y in obs) / len(obs)
    return (a + b) / 2
```

**The re-ranking.** Within a compound, the candidate with the smallest chamfer becomes the
top-1 answer; the solver's own ordering is discarded. The sentinel matters: a candidate
with no forward prediction is assigned 999.0, i.e. effectively infinite, and can never be
selected. Prediction coverage is therefore not a detail but a precondition — an arm with
unpredicted candidates reports a lower bound on verified top-1, not a measurement, which is
exactly why the generate-wide arm was re-run to completion.

**Coverage.** Every candidate the verifier could rank was ranked.

**Table {#tab:esi-coverage}. Forward-prediction coverage, by arm.** Batch size is 17
anonymised SMILES throughout.

| arm | data directory | candidates | forward-predicted | agents |
|--------------------------------------|-------------------------|-----------:|------------------:|-------:|
| original 60-compound arm | `data/fverify/` | 126 | 126 | 8 |
| widened candidate pool | `data/fverify2/` | 65 new | 65 | 4 |
| extension to the whole benchmark | `data/fverify_main/` | 247 | 247 | 15 |
| generate-wide coverage-gap closure | `data/fverify_gw/` | 152 outstanding | 152 | 9 |
| trained-generator arm, re-run | `data/fverify_gen/` | 75 outstanding | 75 | 5 |

Across the whole benchmark that is **373 of 373** candidates forward-predicted by 23
independent agents over all 194 targets, so nothing in [@tab:forward-verification-decomposition]
is a lower bound. In the generate-wide arm all **217 of 217** distinct new candidates are
now predicted, where the original pass had predicted 65; **not one number moves** — recall
42%, forward-verified top-1 30%, precision 72%, identical to three significant figures. The
added coverage does buy a direct view of the mechanism: on **18 of the 60** compounds the
verifier abandons its previous pick for a newly-selectable candidate, and in **not one** of
those 18 does the outcome change — every switch is from one wrong structure to another
([@sec:generate-wide-testing-recipe]).

**The margin the method works on.** Measuring the chamfer between the *predicted* spectra
of every pair of candidates proposed for the same target
(`scripts/isomer_separability.py`), isomeric pairs — the ones the verifier exists to
separate — sit at a median separation of **1.21 ppm** (quartiles 0.84 and 1.78), and **82%
of them are predicted closer together than the predictor's own ~2 ppm error**. Non-isomeric
pairs separate better but not dramatically: median 1.90 ppm, 53% inside the error. The
ranking nevertheless recovers the right structure 89% of the time it is present, which is
why the permutation control matters: re-pairing, as a derangement, which observed spectrum
each candidate set is scored against, over 1,000 permutations, drops conditional-on-recall
precision from **89.2% (58/65)** to a permuted mean of **73.8%** (95% range 66.2–81.5%;
one-sided p=0.001, two-sided p=0.002). On the 60-compound arm alone the same control gives
84.2% against 66.4% (one-sided p=0.019). The chance floor sits high because recall-positive
compounds carry few and near-identical candidates, so the genuine margin over chance is
~15 points ([@sec:negative-control]).

**A negative result on calibration.** Ranking the 138 multi-candidate compounds by their
chamfer margin (best minus second-best distance) and answering only the most-confident
fraction leaves top-1 flat and non-monotonic with coverage: 22% at full coverage, 24% at
75%, 28% at 50%, 24% at 25%. Compounds with a single candidate have no margin and must be
excluded; an earlier analysis that retained them produced a spurious improvement that was
entirely an artefact of those trivial cases. The match distance is a re-ranker, not an
abstention gauge.

## Non-LLM verifiers: a deterministic lookup and a learned model {#sec:esi-verifiers}

Both non-LLM ¹³C predictors are built from the **same nmrshiftdb2 dump**[@kuhn2015nmrshiftdb2]
and dropped into the verifier slot on the **same candidate sets**, so that only the
predictor changes.

**The deterministic lookup** realises the HOSE-code idea[@bremser1978hose] natively in
RDKit: the Morgan per-atom identifier at radius r is a canonical hash of an atom's
environment out to r bonds, so a (radius, identifier) bin groups carbons with identical
local environments. The mean assigned shift per bin is learned from nmrshiftdb2, and
prediction walks the deepest sufficiently-populated sphere, r=4 → 3 → 2 → 1, falling back
to a hybridisation prior; a bin needs at least 3 samples to be trusted. Training used
**31,000 molecules, 332,595 assigned carbons and 263,366 environment bins**, with a held-out
**MAE of 3.23 ppm (median 1.73)** over 17,456 carbons of 1,647 molecules
(`scripts/hose_predict.py`).

**The learned model** is a message-passing GNN — 4 layers, hidden width 256, GRU node
update, bond features, per-carbon ¹³C regression — trained on the identical dump: 32,647
molecules and 350,313 assigned carbons, split by molecule into 29,383 train / 1,632
validation / 1,632 test with seed 5 (the lookup's figures above are this set minus its
random 5% held-out split). Optimisation is Adam at learning rate 1e-3 with weight decay
1e-5, batch size 64, smooth-L1 loss, plateau learning-rate halving and early stopping. On
the held-out test split it reaches **MAE 1.70 ppm (median 1.02)**, roughly twice as sharp
as the lookup (`scripts/gnn_predict.py`, `data/nmrshiftdb/gnn_c13.pt`). It is deliberately
modest rather than state of the art: purpose-built ¹³C models reach ~1 ppm from
message-passing ensembles[@williamson2024mpnn] and 0.94 ppm when a graph network is coupled
to DFT shielding tensors[@han2024dftgnn], on benchmarks now standardised for the
comparison[@xu2025nmrbench]. The question here is whether the predictor slot is where the
leverage sits, which needs a predictor differing from the lookup in *method* while holding
data and evaluation fixed.

**Held-out error against benchmark behaviour.** [@tab:verifier-comparison-conditional-recall]
gives the four verifiers conditional on recall. Two further readings belong here. The
lookup's tie with self-ranking is not agreement: at n=65 it **gains seven compounds and
loses seven** (McNemar b=c=7, p=1.00), reshuffling the ranking energetically while carrying
no net discriminative signal. Its coverage diagnosis is that of the **6,360 candidate
carbons only 2.1% match a training environment at the most specific sphere (r=4)** and 71%
resolve only at r≤2 or fall through to the prior, because the benchmark's exotic chemistry
is under-represented in nmrshiftdb2. The GNN's margins are directional in every pairwise
comparison and none reaches significance: against the lookup seven gained and three lost
(p=0.34), against self-ranking five gained and one lost (p=0.22), and against the LLM
verifier the two land within one compound of each other while disagreeing on nine
(b=5, c=4, p=1.00).

**Leakage analysis.** For a *learned* verifier this is the decisive control, since a GNN
can memorise a molecule's spectrum where a bin average cannot. Exact overlap with the
entire nmrshiftdb2 database is **2 of 364** distinct candidate structures by InChIKey-14 —
both of them wrong candidates on recall-negative compounds, which never enter the
conditional analysis — and **no benchmark answer appears in the database at all** (0/373;
the 60-compound arm is 0/126). Analog overlap is likewise absent: the median Morgan(2, 2048)
Tanimoto to the nearest training molecule is **0.44**, with only three candidates above
0.80. The load-bearing figure is the last: over the **65 true structures the verifier
actually has to identify**, the nearest training analog has median Tanimoto **0.50** and
maximum **0.81**, so not one compound the conditional analysis scores has a near-duplicate
in the training set. A Y-randomisation control (1,000 derangements) places the learned
verifier's result above the 97.5th percentile of the chance distribution (n=19: real 84%
against a permuted mean of 58.6%, 95% range 42.1–73.7%, one-sided p<0.05). Both checks
regenerate via `scripts/verifier_leakage.py`.

Neither predictor is redistributable end-to-end: the nmrshiftdb2 dump cannot be
redistributed with the manuscript, so these two rows regenerate only once a reader supplies
the same dump ([@sec:limitations]).

## Cross-vendor replication {#sec:esi-cross-vendor}

Non-Claude models were run through `scripts/cross_vendor_sweep.py` on the `fverify60` arm —
the same 60 compounds as the first column of [@tab:forward-verification-decomposition] —
between 2026-08-13 and 2026-08-17. Two arms were driven through OpenRouter
(`scripts/openrouter_run.py`); the rest were driven by cloud coding agents against the
committed `sweep_prompts/`, one fresh subagent per batch, at no API cost. Raw replies are
released in `sweep_out/`.

**Table {#tab:esi-vendor-generation}. Generation stage, all models run on the 60-compound arm.**
Claude Opus is shown for reference from the article's own arm.

| model | route | answered | recall | top-1 | parse | matches the given formula |
|-------------------------------------|------------|---------:|-------:|------:|------:|--------------------------:|
| `grok-4.6` | cloud agent | 60/60 | **53%** | 38% | 99% | 95% |
| `gemini-3.7-flash` | cloud agent | 60/60 | **50%** | 38% | 98% | 94% |
| `gpt-5.6-sol` | cloud agent | 60/60 | **42%** | 35% | 100% | **100%** |
| *Claude Opus (reference arm)* | subscription | 60/60 | *32%* | *23%* | — | *78–95%* |
| `composer-2.5` | cloud agent | 57/60 | 20% | 17% | 95% | 67% |
| `gpt-5.6-luna` | cloud agent | 60/60 | 15% | 10% | 90% | 76% |
| `deepseek/deepseek-v4-pro-0813` | OpenRouter | 18/60 | 13% | 12% | 94% | 94% |
| `nvidia/nemotron-3.5-lightning` | OpenRouter | 60/60 | 0% | 0% | 61% | **2%** |

Read the formula-adherence column first: nemotron's zero is not a chemistry result but a
model that could not return a structure of the requested composition, and the deepseek arm
answered 18 of 60 compounds — a reasoning model that exhausted its token ceiling without
emitting an answer on most batches, where an unanswered compound scores exactly like a
wrong one.

**What was matched across arms.** The compounds, the two-stage protocol, the candidate
budget of three, the context packing (six compounds per fresh context), the closed-book
instruction, the anonymised blind forward-prediction stage, and the scorer. **What was
not.** Verification was run only for the three models whose output contract justified it;
Composer 2.5 and GPT-5.6 Luna were left out at 67% and 76% formula adherence.

**Table {#tab:esi-vendor-decomposition}. Decomposition, the three replicated arms.**
Recall and precision have different denominators, so the criterion is the inequality, not a
difference.

| model | generation recall | verification precision given recall | multi-candidate only |
|-------------------------------|------------------:|------------------------------------:|---------------------:|
| *Claude Opus (reference arm)* | *19/60 = 32%* [21, 44] | *16/19 = 84%* [62, 94] | *10/13 = 77%* |
| `grok-4.6` | 32/60 = 53% [41, 65] | 20/32 = 62% [45, 77] | 20/32 = 62% |
| `gemini-3.7-flash` | 30/60 = 50% [38, 62] | 22/30 = 73% [56, 86] | 22/30 = 73% |
| `gpt-5.6-sol` | 25/60 = 42% [30, 54] | 17/25 = 68% [48, 83] | 16/24 = 67% |

**What these identifiers name.** The models are as served by the coding-agent harness, not
stock vendor endpoints. That harness's allowlist reads `gpt-5.6-sol-xhigh`,
`gpt-5.6-sol-high`, `gpt-5.6-luna-high`, `gemini-3.7-flash-high`,
`cursor-grok-4.6-high-fast`, `composer-2.5` — every identifier but the last carries a
**reasoning-effort suffix**, which is a decoding parameter the Claude reference arm never
had ([@sec:esi-versions]), and the harness supplies its own agent system prompt above the
task text. **The effort tier actually used for each arm is not recorded**, because the run
did not report which allowlist entry it selected; a run at `-xhigh` is not the same
measurement as one at `-high`, and the article reports these as vendor-family results
accordingly. `GPT-5.6 Terra` and `GLM 5.2` were attempted and rejected: neither is in the
agent's allowlist.

**Contamination control.** The cloud agents cloned the whole repository, and the answer
files for these 60 compounds are tracked, so blindness rested on an instruction that
nothing verifies after the fact. The control is a re-solve with those files physically out
of the workspace: Grok 4.6 re-ran all ten batches from a clean clone
(`sweep_out/grok-4.6-clean/`).

**Table {#tab:esi-clean-clone}. Clean-clone contamination control, Grok 4.6.**

| arm | recall | 95% CI | parse | formula match |
|------------------------------------|---------------:|--------:|----------:|--------------:|
| original (answer files present) | 32/60 = 53% | [41, 65] | 179/180 | 171/180 |
| clean clone (answer files absent) | 28/60 = 47% | [35, 59] | 176/180 | 174/180 |

Paired, that is **b=8, c=4, McNemar exact p=0.39**. The decisive detail is the asymmetry
rather than the totals: a model reading the key would solve a superset, and instead **four
compounds were solved only in the arm that had no key**, with 24 of the 60 solved by both.
Formula adherence held at 97% against 98%, where a model that had lost a crib would be
expected to degrade. The control covers Grok; Gemini 3.7 Flash and GPT-5.6 Sol rest on the
shared instruction and on the stereochemistry evidence of [@sec:esi-scoring].

## Modality ablation and contamination controls {#sec:esi-ablation}

**The leave-one-modality-out ablation was specified and never run, and no leave-one-out
result appears in the article.** The staged prompts `prompt_noIR.txt`, `prompt_noH.txt` and
`prompt_noC.txt` exist under `data/modality/` (2026-06-16) with no corresponding
`out_*.json`. The reason is instructive. Two attempts were discarded. The first ran one
solver agent per condition, so agent quality was a single draw per condition and swamped
the modality effect: full modality came out worst at 3/16 while −IR came out best at 8/16,
and −IR solved compounds the full-information run missed. The second ran a fresh −IR arm
against the *archived* benchmark predictions as its control and produced full 10/30, −IR
22/30, formula-only 2/30 on the simple stratum — −IR beating full modality by 40 points,
McNemar p=0.004, which is impossible and identifies the confound rather than a modality
effect. The rule this yielded is that every arm of an ablation must be generated in one
campaign with the same agent configuration, batch size and model, the control included
(`docs/MODALITY_ABLATION.md`).

**The formula-only control shares that structure and is not impugned by it**, because the
direction of the confound runs against the finding. Only the formula-only arm was freshly
generated (2026-07-28); the full-modality comparison arm re-uses the archived June
predictions, whose 60 top-1 answers are byte-identical to that run. Fresh agents reason
harder per compound than the archived batched run, so the bias favours the formula-only
arm — and it still collapsed. The solver received the molecular formula and nothing else,
was barred from reading any repository file or searching the web, and was allowed RDKit
only to check that a proposed SMILES parses and matches the formula. The outcome is
perfectly nested: **eleven** compounds are solved with the spectra and not without, and
**none** the other way round (b=11, c=0, McNemar exact p=0.001), for 3/60 against 14/60
top-1 and 3/60 against 19/60 recovered ([@tab:formula-only-control]).

The three formula-only successes are named rather than rounded away, because they do not
all support the same reading: **C₁₅H₁₅ClF₂O₃SSi**, a 2-(trimethylsilyl)aryl sulfonate whose
Si/S/Cl/F₂ composition is a near-unique benzyne-precursor signature and which is absent
from PubChem, so the formula is close to determining; **C₁₃H₁₉NO₄S**, *N*-tosyl-leucine
(CAS 67368-40-5), where inference and recall are both available; and **C₁₇H₂₆O₃**,
[6]-paradol (CAS 27113-22-0), a catalogued ginger natural product that composition alone
constrains very little. One is clean chemical inference; one or two are consistent with
memorisation. The bound is unaffected either way.

**The recency control** is independent of the first and agrees with it. Publication years
were resolved for all 194 compounds from their accessions
(`scripts/contamination_recency.py`); they span 2008–2026. Accuracy is flat: **28.6%** for
the older half (≤2020, n=112) against **28.0%** for the newer (n=82), a point-biserial
correlation between publication year and correctness of **r = −0.007**, and the most recent
bucket (≥2024, n=25) is in fact the highest at 40% [23, 59]. The raw split is biased
against the newer half, since newer papers skew larger (median 22 heavy atoms against 20)
and size dominates accuracy; stratifying by heavy-atom band removes that, and newer
compounds lead in the two bands carrying most of the accuracy (≤15: 64% against 58%;
16–25: 34% against 25%) and trail slightly in the largest, where both are near the floor
(>25: 6% against 8%). The size-adjusted older-minus-newer difference is **−5.1 points, 95%
CI [−17.2, +7.0]** (Cochran–Mantel–Haenszel χ²=0.42, p=0.51, continuity-corrected) — a
bound on any recency effect, not a demonstration of a reversed one. Neither control is
randomised, so the article claims a strong bound rather than exclusion, and it does not
anchor the recency test to a training cutoff, because the harness discloses none.

## Human-expert audit: protocol and status {#sec:esi-audit}

Solver and verifier are both LLMs, so the one validation the authors cannot perform
themselves is an expert-chemist review of the outputs. The audit package is therefore
**built, blinded, pre-registered and frozen** before any review, and regenerates
deterministically at seed 0 from `scripts/make_audit_sample.py` into `data/audit/`.

The panel is three PhD-level synthetic or analytical chemists, independent, with no prior
exposure to the benchmark answers, at roughly 3–4 person-hours each. The sample is a
difficulty-stratified draw (15 simple, 15 complex) from the 60-compound
forward-verification set, the only split carrying both the ranked candidates and the
observed spectra. Per compound a reviewer sees the exact solver prompt — formula, IR, ¹H,
¹³C — and the model's top-ranked candidate rendered as a 2D structure, with model identity
and ground truth hidden.

**Table {#tab:esi-audit-kit}. Composition of the frozen audit kit.**

| item | count |
|-----------------------------------------------------------------|------:|
| compounds in the kit | 37 |
| Task 1 panel (unbiased stratified draw) | 30 |
| Task 2 ranking items | 37 |
| …carrying the true structure and a real choice, scoring precision | 13 |
| …carrying the true structure but a single candidate, excluded | 3 |
| …carrying no correct candidate, measuring expert calibration | 21 |
| model top-1 exact on the Task 1 panel (held in the key only) | 7/30 |

Task 1 scores the model's top-1 for consistency with all provided spectra (1–5), gives a
categorical verdict (correct / wrong-regiochemistry / wrong-scaffold / uninterpretable),
and names the single most diagnostic peak; the read-outs are inter-rater agreement and the
fraction of mechanically-wrong top-1 answers judged spectrally consistent but a different
regioisomer. Task 2 presents the shuffled, unlabelled candidate set for ranking by spectral
fit, and is compared against the LLM forward-verifier's pick and the deterministic
lookup's pick on identical candidate sets.

Two design decisions are worth recording because both were mistakes first. Task 2 is shown
on **every** compound, so its presence signals nothing: an earlier version showed it only
on recall-positive compounds, which leaked Task 1 twice over and moved the apparent rate of
correct answers from 12% to 67% — a five-fold prior available without reading a spectrum.
And the seven extra compounds carry Task 2 only: recall-positive compounds could not be
added to the Task 1 draw, because a correct top-1 is recall-positive by definition and
enriching for them would raise the very rate Task 1 exists to judge.

**Status.** The panel has not been run, and the article reports no audit result
([@sec:limitations]). One reviewer file is deposited at `data/audit/responses/`
(submitted 2026-08-18 UTC) and is incomplete against the 37-item kit; a single partial
reviewer supports neither read-out, since inter-rater agreement needs at least two and the
pre-registered panel is three. Scoring of completed sheets is mechanical
(`scripts/score_audit.py`) with no further model involvement. Three Task 2 sets
(A19, A21, A30) hold a single candidate, which cannot be ranked; the scorer excludes and
flags them. Until expert results are in, the two load-bearing claims the panel targets —
what a miss actually is ([@sec:well-llms-elucidate-real]) and whether forward verification
is a trustworthy re-ranker ([@sec:forward-verification-elucidation]) — should be read as
machine-validated (RDKit InChIKey) but not yet human-validated.

<!-- GAP: the instruction text dispatched to the Claude solver and forward-prediction
     sub-agents is not committed anywhere in the repository. Only the per-compound batch
     data files are released. The prompts quoted verbatim in S2 are the cross-vendor
     harness prompts (scripts/cross_vendor_sweep.py, sweep_prompts/), which the Claude
     arms were not run from. -->
<!-- GAP: no dated model snapshot identifier exists for any Claude arm, and the harness
     exposes none; the reasoning-effort tier used for each cross-vendor arm was likewise
     not recorded. Neither can be supplied after the fact. -->
<!-- GAP: no decoding parameters (temperature, top_p, top_k, max_tokens, generation seed,
     thinking budget) were set or recorded for any run. -->
<!-- GAP: the sampling seed and draw size for the main round (140 problems) and for the
     controlled v3 round (40 problems) are not recorded in any document or artifact; only
     the within-compound control's defaults (--n 20 --seed 23) and the pilot's
     (--n 21 --seed 7) appear in the released code. The rounds are still reproducible as
     cohorts, since questions2.jsonl / answers2.jsonl are released, but the draw is not
     re-runnable from the recorded parameters. -->
<!-- GAP: docs/MODELS.md prose says "Six non-Claude models were run" while its own
     generation table carries seven non-Claude rows (the seventh, deepseek-v4-pro-0813,
     answered 18/60 compounds). Table S5 here reproduces all rows; the count in the prose
     needs reconciling by the authors. -->
<!-- GAP: HOSE coverage on the 60-compound arm is reported as 70% resolving at r<=2 in
     the article and as 67% in the released artifact data/fverify/hose_results.txt (the
     whole-benchmark figures, 2.1% at r=4 and 71% at r<=2 or fallback, agree between the
     two). Only the whole-benchmark figures are quoted here; the authors should re-run
     scripts/hose_predict.py coverage on the 60-compound arm and reconcile. -->
<!-- GAP: transcripts of the run-time closed-book audit are not deposited, so the audit
     itself cannot be re-verified from the release; the article states this. -->
