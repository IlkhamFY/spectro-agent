This document records the operational detail behind the article: which model answered which
arm and when ([@sec:esi-models]), the prompts and agent protocol ([@sec:esi-prompts]), how
the benchmark was assembled ([@sec:esi-benchmark]), what the correctness criterion accepts
and rejects ([@sec:esi-scoring]), the construction of the forward-verification arm
([@sec:esi-forward]) and of the two non-LLM verifiers ([@sec:esi-verifiers]), the
four-vendor replication ([@sec:esi-cross-vendor]), the contamination controls
([@sec:esi-ablation]) and the frozen expert-audit package ([@sec:esi-audit]). Where the
repository does not pin a value it says so rather than supplying one, and every number is
copied from a released artifact or from a companion note issued with the manuscript
(`docs/MODELS.md`, `docs/BENCHMARK.md`, `docs/FORWARD_VERIFY.md`, `docs/CROSS_VENDOR.md`,
`docs/VERIFIER_PROBE.md`, `docs/MODALITY_ABLATION.md`, `docs/EXPERT_AUDIT_PROTOCOL.md`).

## Models, versions and collection windows {#sec:esi-models}

Every LLM result in the article was produced by Anthropic Claude models invoked as
independent sub-agents through the Agent tool under a single consumer claude.ai
subscription: no paid API, no fine-tuning, no model training in the core protocol. The two
trained probes — the learned ¹³C verifier of [@sec:non-llm-verifiers-deterministic]
([@sec:esi-verifiers]) and the generator of [@sec:recall-wall-task-intrinsic]
(`contrib/generator_probe/`) — are not Claude models.

**Table {#tab:esi-runs}. Which model answered which arm, and when.** "Collected" is the UTC
author-date of the commit that first added the prediction artifact. Each raw agent-output
file was committed once, in the session that produced it, so first-add is the best
available proxy for collection time — a proxy, not a harness timestamp.

| arm | model | data directory | collected (UTC) |
|--------------------------------------------------|-------------|------------------------------|------------------|
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

Invocations fall into three dated windows, not one. 2026-06-09 to 2026-06-11 produced
every candidate structure behind the headline results and behind the pools all of
[@sec:forward-verification-elucidation] re-ranks. 2026-07-28 is the formula-only
control, which generates its own candidates (3/60 correct) by design, a masked-input
control being meaningful only as a fresh run. 2026-08-07 carries three
forward-prediction collections that predict ¹³C for candidates the June solver had already
produced, so none introduces a new candidate or moves a recall number. All later commits
re-score frozen outputs and re-query no model.

### Version strings, snapshots and decoding parameters {#sec:esi-versions}

[@sec:methods] states what can and cannot be reported about the model builds; this section
is the evidence behind it. `Claude Opus 4.8` is the only Claude version string anywhere in
the repository, and it is evidenced only for the 2026-06-09 pilot (`docs/BENCHMARK.md`). It
is a display version, not a snapshot identifier: it pins no checkpoint. `Fable 5` appears as
a display name; **no version number of any kind appears for Claude Sonnet or Claude
Haiku**, and no dated snapshot identifier exists for any of the four, because the consumer
harness exposes no checkpoint identifier, announces no build change, and records nothing
about which build served a request. Two numbers from one window are therefore known to
share a window and *not* known to share a build. **No sampling parameters were set for any
run and none are recorded** — no temperature, `top_p`, `top_k`, `max_tokens`, generation
seed or thinking budget appears in any script, document, config or artifact; the `seed=`
values in the repository are for analysis determinism only.

One protocol asymmetry belongs here, because
[@sec:methodology-dominates-within-compound] measures a large effect of the variable it
concerns. The Opus column of the four-model comparison is not a fresh 24-compound run: it
re-scores the main-round predictions on that subset (the `SRC` map in
`scripts/score_models.py`), whose 24 items came from one 6-compound and two 12-compound
contexts (`raw/b1.json`, `raw/redo_b23.json`, `raw/redo_b45.json`) where Sonnet, Haiku and
Fable each saw four 6-compound contexts. Prompts and compounds are identical; context
packing is not.

## Prompts and agent protocol {#sec:esi-prompts}

**What the solver was shown:** the molecular formula (as from HRMS), the IR band list, and
the ¹H and ¹³C shift lists with multiplicities and J-couplings where the source paper
reported them. **What it was not shown:** the compound name, any SMILES, any starting
material or scaffold hint, the ground truth, and any other benchmark record. Solver agents
were closed-book — no web access, no ground-truth access, no tools beyond an RDKit
formula/parse check — except the arm (a) baseline of
[@sec:methodology-dominates-within-compound], which had no tools at all, that being the
variable it isolates. Closed-book status was grep-audited over the task transcripts at run
time; the transcripts are not committed ([@sec:limitations]).

One exception to the blinding sits in the data rather than in the instruction, and is
measured rather than removed: in 10 of the 194 records the source paper's own peak
assignments name a ring system, so the shift string a solver was handed carries a partial
structural hint the prompt never gave it ([@sec:benchmark-design-irspectra-bench]).

**Candidate budget:** up to **three ranked candidate SMILES per compound**, best first, in
every arm except generate-wide, where ten independent solver agents each proposed up to
**six regiochemistry-aware candidates** and the pools were merged. Scoring reads the first
three for top-1 and recovered (top-3); generation recall reads the whole pool.

**Context discipline:** one small batch per agent, in a context reset between batches —
6 compounds per released batch file (`data/benchmark_main/batch_*.txt`, 23 files: 22 of six
plus one of two = the 134 spectrally-validated problems), some batch pairs merged into a
single 12-compound context (`data/benchmark_main/raw/redo_*.json`). Range released: **2–12
compounds per context**.

**Forward-prediction agents** had **zero tools**, pure reasoning, and were blind:
anonymised SMILES only, pooled across compounds, canonicalised, de-duplicated, shuffled and
re-labelled, in fixed batches of 17. They saw neither the observed spectrum, nor the
compound's identity, nor which candidates belong to one target. Shuffling does not keep a
target's own candidates in separate batches — in the [@sec:result] arm, 5 of the 8 batches
held two candidates for a single compound — but with no observed spectrum in hand there is
nothing for that to leak: at most a predictor notices that two structures are isomers,
evident from either alone.

[@sfig:overview] draws the protocol end to end, and the join between the two stages is the
part to read: the solver's context closes before the predictor's opens, and no observed
spectrum ever reaches the predictor. That separation is what lets the recall and
conditional-precision rows of [@tab:forward-verification-decomposition] be read as
independent measurements rather than as two views of one ranking — and it is why nothing
downstream of the join can lift recall, the candidate pool being fixed before any
re-ranking is computed.

**Verbatim prompts, and what they are not.** The prompts below are committed
(`sweep_prompts/solve_01.md` … `solve_10.md`, `sweep_prompts/verify/`) and emitted by
`scripts/cross_vendor_sweep.py`. They are the harness prompts for the cross-vendor
replication ([@sec:esi-cross-vendor]). The instruction text dispatched to the Claude
solver and forward-prediction sub-agents in the main rounds was **not captured** — only the
per-compound batch data it wrapped is released — so the prompts below state the task as
posed, but are not a transcript of the main arms. This is a reproducibility gap and we
name it rather than let the committed files stand in for something they are not. The
elucidation header:

```{=latex}
\begingroup\footnotesize
```

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

```{=latex}
\endgroup
```

The forward-prediction header:

```{=latex}
\begingroup\footnotesize
```

```
# Forward 13C prediction task

For each candidate structure below (given as SMILES), predict its 13C NMR chemical
shift list (in ppm) from the structure alone. This is the forward direction only:
you are NOT given any observed spectrum and must not assume one.

Return ONLY a JSON object mapping each id to a list of predicted 13C shifts (numbers
in ppm), e.g.: {"P001": [21.0, 60.5, 171.2], "P002": [...], ...}

Candidates:
```

```{=latex}
\endgroup
```

Each compound follows as one block in exactly this form, the NMR strings being the source
paper's own text reproduced unedited (hence the chemical-shift symbol and whatever
assignment annotations the authors wrote):

```{=latex}
\begingroup\footnotesize
```

    ### M001
    Molecular formula: <formula>
    IR bands (cm-1): <list of wavenumbers>
    1H NMR: <string as reported>
    13C NMR: <string as reported>

```{=latex}
\endgroup
```

The real blocks are released per arm:

- solving — `data/benchmark_main/batch_*.txt`, `data/gw/batch_*.txt`
- forward prediction — `data/fverify_main/fbatch_*.txt`, `data/fverify_gw/gbatch_*.txt`
- contamination control — `data/modality/prompt_*.txt`

**One gap, stated rather than papered over.** The wording above is the harness prompt used
verbatim for the four-vendor replication, and it is the only instruction text committed in
the repository. The Claude sub-agents behind the headline arms were dispatched through the
Agent tool with their instruction supplied at dispatch, and **that instruction text was not
captured**. What is released for those arms is the per-compound data exactly as the agents
received it, plus the candidate budget, tool policy and context sizes above.

## Benchmark construction {#sec:esi-benchmark}

IRSpectra-Bench is drawn from `irexp_resolved`, the 43,060-record structure-complete split
of IRexp. A record enters the sampling pool only if it carries an IR band list, a ¹H and a
¹³C shift list and a resolved structure; the structure has **8–60 heavy atoms**; each NMR
string carries at least three parenthesised entries; and the raw ¹H string, re-fetched from
the source article, contains genuine J information. Draws are balanced between the
difficulty strata, and every compound revealed in a prior round is excluded by InChIKey-14
beforehand, so none appears twice (`scripts/benchmark_v2.py`). [@sfig:dataset] shows why
that pool is so much smaller than the corpus it is drawn from: the attrition is not at the
IR stage but at the two joins after it — resolving a structure, then demanding both nuclei
on the same record — so what caps benchmark size is provenance and linkage, not spectral
coverage.

**Table {#tab:esi-cohort}. Rounds behind the n=194 cohort.**

| round | data directory | problems | in the cohort | role |
|-------------------------|-------------------------------|---------:|--------------:|---------------------------------------|
| main | `data/benchmark_main/` | 140 | 134 | headline, spectrally validated |
| controlled v3 | `data/benchmark_v3/` | 40 | 40 | difficulty control, pre-registered |
| within-compound control | `data/benchmark_v2_ctrl/` | 20 | 20 | context/tooling control, pre-registered |
| electrolyte case study | `data/benchmark_electrolyte/` | 48 | — | domain subset, 46 scored, held apart |

**What was excluded, and why.** Every main-round ground truth passes an automated
RDKit[@landrum_rdkit] self-consistency check — ¹³C peak count against symmetry-unique
carbons, formula match, SELFIES[@krenn2020selfies] round-trip — which excluded 6 of 140:
five report more ¹³C peaks than the structure has carbons (R03 28>24, R14 11>8, R65 26>18,
R67 23>16, R131 34>17: merged or contaminated spectra) and one is too sparse to constrain
(R82, 5 peaks for 22 symmetry-unique carbons).
The two controlled rounds are used **whole**, being fixed and pre-registered as controls
before the audit existed; the same audit is reported on them rather than applied (57/60
pass), and [@sec:headline-performance] gives the strictly-validated 191-compound cohort as
a robustness check. The filter itself is `scripts/validate_benchmark.py`, which regenerates
every `clean_qids.json` from the released questions and answers; it tests ¹³C against the
carbon count and does not gate on ¹H at all. [@sec:benchmark-design-irspectra-bench]
reports what that leaves standing and how much the headline moves if it is dropped.

**Complexity stratification, and when it was defined.** Difficulty is a declared property
of the compound, assigned by RDKit ring analysis at sampling time — before anything was
solved — and exhaustive by construction, so nothing falls between the classes. A compound
is **complex** if it has a spiro atom, a bridgehead atom, three or more rings, any fused
ring system, **or** more than 24 heavy atoms; **simple** if it has at most two rings and at
most 22 heavy atoms; anything else (the 23–24-heavy-atom band, 13 compounds) is complex on
size alone. The cohort splits 98 simple / 96 complex. What the 22-atom boundary is worth is
measured rather than asserted: `scripts/difficulty_sensitivity.py` re-runs the whole split
across a range of thresholds, and [@sec:benchmark-design-irspectra-bench] reports the
result. This axis is distinct from
the heavy-atom bands (≤15 / 16–25 / >25) of [@sec:headline-performance] and [@sfig:size].

The battery-electrolyte subset ([@sec:domain-case-study-battery]) came from the same corpus
by SMARTS filters for six electrolyte functional classes, eight per class (48 curated, 46
scored), J-enriched and spectrally validated identically to the main rounds and excluding
every compound used elsewhere. [@sfig:electrolyte] breaks that subset down class by class,
pairing exact top-1 against recovered. It carries no intervals and is not a ranking — with
eight compounds per class, the spread is within sampling noise
([@sec:domain-case-study-battery]) — but the paired bars show the shape of the failure
plainly: in most classes recovered barely clears top-1, so what the subset is short of is
candidates, not a way to choose between them.

## Scoring: what the criterion accepts and rejects {#sec:esi-scoring}

A prediction is **correct** if the first 14 characters of the RDKit InChIKey computed from
its SMILES equal those of the reference — the InChIKey **connectivity layer**, which hashes
the molecular skeleton; the later blocks, carrying stereochemistry, isotopic substitution
and protonation state, are not compared. Top-1 asks this of the first-ranked candidate,
recovered (top-3) of the up-to-three returned — the lenient recovery protocol of ref.
[@kamber2026chemist] — and generation recall of the whole pool. Nothing
is model-mediated: RDKit only, in `scripts/score_main.py` and `scripts/specmetrics.py`.
Morgan(2, 2048) Tanimoto[@rogers2010ecfp] is reported alongside as a graded signal, 0.45
being the scaffold-level threshold; intervals are bootstrap 95% over compounds (2,000
resamples, analysis seed 0), model comparisons McNemar exact[@mcnemar1947] with Holm
correction[@holm1979].

**What it accepts.** A candidate with the right constitution and the wrong stereochemistry
scores correct. This is a deliberate floor whose cost is measured rather than assumed:
re-scoring the *full* InChIKey gives **21.1% top-1 and 25.8% recovered (41/194 and
50/194)** against 28.4% / 33.5% at the connectivity layer, so fourteen top-1 answers are
accepted here that a stereochemistry-sensitive scorer rejects. The floor exists because 1D
¹H/¹³C/IR rarely fixes absolute configuration and only 10.3% (20/194) of answers carry a
defined (assigned R/S) stereocentre. Worked cases of acceptance come from the cross-vendor
arm: on structures those models got constitutionally right whose reference carries assigned
stereocentres, Grok 4.6 reproduced 0/3 correct descriptors, Gemini 3.7 Flash 0/2 and
GPT-5.6 Sol 0/2 — all scored correct here.

**What it rejects:** every constitutional isomer, however close, and every structure of the
wrong composition. Three worked cases, all from released artifacts:

- *A regioisomer the verifier separates.* Picolinamide and nicotinamide differ only in
  which ring position bears the carboxamide, so they have different connectivity layers and
  proposing one for the other scores zero; forward-predicted ¹³C separates them at a
  chamfer of 0.42 ppm against 1.30 ppm ([@fig:fig-mechanism]).
- *A regioisomer it does not.* On the 2-(nitrophenyl)-2,3-dihydroquinazolin-4(1*H*)-one
  targets (C₁₄H₁₁N₃O₃) the predictor cannot resolve the *ortho*- and *meta*-nitrophenyl
  isomers: it ranks the 2-nitrophenyl isomer first at a chamfer of 1.35 ppm against
  1.36 ppm for the true 3-nitrophenyl one, a 0.01 ppm margin. The answer is rejected, as it
  must be.
- *A pilot miss of the same kind.* The n=21 pilot returned the right
  hydrazinecarbothioamide skeleton with the **3-pyridyl** isomer where the truth is
  **2-pyridyl** (`docs/BENCHMARK.md`): right formula, right scaffold, rejected.

That is the dominant shape of failure: of the 137 analysable top-1 misses (139 in all; two
predictions did not parse), **76.6% are constitutional isomers** of the true structure and
23.4% have the wrong formula outright, 22.6% share the true Murcko scaffold, and the median
isomeric-miss Tanimoto is 0.39 (`scripts/analyze_misses.py`). Formula adherence is not
part of the criterion at all — a wrong-composition answer is scored as a miss, not as a
separate class of error — and its variation across rounds is reported in
[@sec:benchmark-design-irspectra-bench].

## Forward-verification detail {#sec:esi-forward}

**The distance.** Candidates are ranked by a symmetric chamfer distance between the
forward-predicted and observed ¹³C peak sets: a mean of two nearest-neighbour means, so no
equal-count requirement is imposed and lower is better. The implementation is the single
source of truth for every scorer (`scripts/specmetrics.py`):

```{=latex}
\begingroup\footnotesize
```

```
def chamfer(pred, obs):
    """Symmetric chamfer distance between predicted and observed 13C shift lists."""
    if not pred or not obs:
        return 999.0
    a = sum(min(abs(x - y) for y in obs) for x in pred) / len(pred)
    b = sum(min(abs(y - x) for x in pred) for y in obs) / len(obs)
    return (a + b) / 2
```

```{=latex}
\endgroup
```

**The re-ranking.** Within a compound, the candidate of smallest chamfer becomes the top-1
answer and the solver's own ordering is discarded. The sentinel matters: a candidate with no
forward prediction takes 999.0, effectively infinite, and can never be selected, so an arm
with unpredicted candidates reports a lower bound on verified top-1 rather than a
measurement — which is why the generate-wide arm was re-run to completion.

**Table {#tab:esi-coverage}. Forward-prediction coverage, by arm.** Batch size is 17
anonymised SMILES throughout. The candidate count is what each pass was responsible for
rather than a cumulative pool: candidates new to the pool for the widened arm, and
candidates still outstanding — proposed earlier but never predicted — for the two closure
arms.

| arm | data directory | candidates | forward-predicted | agents |
|------------------------------------|--------------------------|-----------:|------------------:|-------:|
| original 60-compound arm | `data/fverify/` | 126 | 126 | 8 |
| widened candidate pool | `data/fverify2/` | 65 | 65 | 4 |
| extension to the whole benchmark | `data/fverify_main/` | 247 | 247 | 15 |
| generate-wide coverage-gap closure | `data/fverify_gw/` | 152 | 152 | 9 |
| trained-generator arm, re-run | `data/fverify_gen/` | 75 | 75 | 5 |

Across the whole benchmark that is **373 of 373** candidates forward-predicted by 23
independent agents over 194 targets — the first and third rows of the table above, 126 and
247 candidates over 8 and 15 agents; the remaining three rows re-rank the widened
generate-wide pool and the generator probe, which the decomposition does not draw on — so
nothing in [@tab:forward-verification-decomposition] is a lower bound. In the generate-wide arm, all
**217 of 217** distinct new candidates are now predicted where the original pass had
predicted 65, and **not one number moves**: recall 42%, forward-verified top-1 30%,
precision 72%. The added coverage buys a direct view of the mechanism — on **18 of the 60**
compounds the verifier abandons its previous pick for a newly-selectable candidate, and in
**not one** does the outcome change; every switch is wrong structure to wrong structure.

**The margin the method works on.** Taking the chamfer between the *predicted* spectra of
every pair of candidates proposed for one target (`scripts/isomer_separability.py`),
isomeric pairs sit at a median separation of **1.21 ppm** (quartiles 0.84 and 1.78) and
**82% are predicted closer together than the predictor's own ≈2 ppm error** — usually
within the noise. What shows that a ranking on so thin a margin is nonetheless real is the
derangement control of [@sec:negative-control]: over 1,000 permutations of which observed spectrum each candidate
set is scored against, conditional-on-recall precision falls from **89.2% (58/65)** to a
permuted mean of **73.8%** (one-sided p=0.001). The floor sits high because recall-positive
compounds carry few, near-identical candidates.

The same distance fails as an absolute confidence gauge — ranked by chamfer margin, the 138
multi-candidate compounds give top-1 22% / 24% / 28% / 24% at 100%, 75%, 50% and 25%
coverage — which is why the article claims it only as a re-ranker
([@sec:negative-control]).

## Non-LLM verifiers: a deterministic lookup and a learned model {#sec:esi-verifiers}

Both non-LLM ¹³C predictors are built from the **same nmrshiftdb2 dump**[@kuhn2015nmrshiftdb2]
and dropped into the verifier slot on the **same candidate sets**, so only the predictor
changes.

**The deterministic lookup** realises the HOSE-code idea[@bremser1978hose] natively in
RDKit: the Morgan per-atom identifier at radius r hashes an atom's environment out to r
bonds, so a (radius, identifier) bin groups carbons with identical local environments. The
mean assigned shift per bin is learned from nmrshiftdb2, and prediction walks the deepest
sphere holding at least 3 samples, r=4 → 3 → 2 → 1, falling back to a hybridisation prior.
Training used **31,000 molecules, 332,595 assigned carbons and 263,366 environment bins**,
held-out **MAE 3.23 ppm (median 1.73)** over 17,456 carbons of 1,647 molecules
(`scripts/hose_predict.py`).

**The learned model** is a message-passing GNN — 4 layers, hidden width 256, GRU node
update, bond features, per-carbon ¹³C regression — trained on the identical dump: 32,647
molecules and 350,313 assigned carbons, split by molecule into 29,383 train / 1,632
validation / 1,632 test at seed 5 (the lookup's figures above are this set minus its random
5% held-out split). Optimisation is Adam at learning rate 1e-3, weight decay 1e-5, batch
size 64, smooth-L1 loss, plateau learning-rate halving, early stopping. Held-out **MAE
1.70 ppm (median 1.02)**, roughly twice as sharp as the lookup (`scripts/gnn_predict.py`,
`data/nmrshiftdb/gnn_c13.pt`). It is deliberately modest — purpose-built ¹³C models reach
≈1 ppm[@williamson2024mpnn] and 0.94 ppm coupled to DFT shielding tensors[@han2024dftgnn] —
the question being only whether the predictor slot is where the leverage sits.

**Held-out error against benchmark behaviour.** [@tab:verifier-comparison-conditional-recall]
gives the four verifiers conditional on recall. The lookup's tie with self-ranking there is
not agreement: at n=65 it **gains seven compounds and loses seven** (McNemar b=c=7,
p=1.00), reshuffling energetically while carrying no net discriminative signal. Its coverage
diagnosis is that of the **6,360 candidate carbons, only 2.1% match a training environment at
the most specific sphere (r=4)**, 71% resolving only at r≤2 or falling through to the prior.
The GNN's margins are directional and none reaches significance (against the lookup p=0.34,
against self-ranking p=0.22, against the LLM verifier p=1.00). [@sfig:verifier] sets those
two things side by side — the conditional-on-recall accuracies in one panel, the held-out
¹³C errors in the other — and the point to take is how little of the second survives into
the first: roughly halving the prediction error buys parity with the LLM verifier and no
more, while the lookup, at twice the error, does not move off the solver's own ranking at
all. On this sample the verifier slot is not where the remaining leverage sits.

**Leakage analysis** is the decisive control for a *learned* verifier, which can memorise a
molecule's spectrum where a bin average cannot. Exact overlap with the whole nmrshiftdb2
database is **2 of 364** distinct candidate structures by InChIKey-14 — both
wrong candidates on recall-negative compounds, which never enter the conditional analysis —
and **no benchmark answer appears in the database at all** (0/373; the 60-compound arm is
0/126). Analog overlap is likewise absent: median Morgan(2, 2048) Tanimoto to the nearest
training molecule is **0.44**, three candidates above 0.80, and over the **65 true
structures the verifier must identify**, the nearest training analog has median Tanimoto
**0.50** and maximum **0.81** — no compound that the conditional analysis scores has a
near-duplicate in training. A Y-randomisation control (1,000 derangements) was run on the
60-compound arm rather than the whole benchmark, and places the learned verifier above the
97.5th percentile of chance (n=19: real 16/19 = 84% against a permuted mean of 58.6%,
95% range 42.1–73.7%, one-sided p<0.05); that chance floor is
predictor-dependent, so it is not the derangement floor quoted for the LLM verifier in
[@sec:esi-forward] (`docs/VERIFIER_PROBE.md`). Both checks regenerate via
`scripts/verifier_leakage.py`; neither predictor is redistributable end-to-end, the
nmrshiftdb2 dump being one a reader must supply.

[@sfig:generator-probe] is the complementary experiment, and belongs here because the
verifier it holds fixed is the deterministic lookup described above: only the source of
candidates changes. It shows that the lookup's coverage problem is a property of what it is
asked to separate rather than of the predictor — scaffold enumeration raises recall while
filling the pool with near-degenerate isomers, and top-1 falls; the trained generator
raises recall with formula-correct candidates, and top-1 rises. A verifier is only as
useful as the candidates are distinguishable.

## Cross-vendor replication {#sec:esi-cross-vendor}

Non-Claude models were run through `scripts/cross_vendor_sweep.py` on the `fverify60` arm —
the same 60 compounds as the first column of [@tab:forward-verification-decomposition] —
between 2026-08-13 and 2026-08-17. Two arms went through OpenRouter
(`scripts/openrouter_run.py`); the rest were driven by cloud coding agents against the
committed `sweep_prompts/`, one fresh subagent per batch, at no API cost. Raw replies are in
`sweep_out/`.

**Table {#tab:esi-vendor-generation}. Generation stage, every model run on the 60-compound
arm**, with the article's Claude Opus arm for reference. *Formula* is the share of returned
candidates whose composition matches the molecular formula the solver was given.

| model | route | answered | recall | top-1 | parse | formula |
|---------------------------------|--------------|---------:|-------:|------:|------:|--------:|
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
answered 18 of 60 compounds, having exhausted its token ceiling on most batches without
emitting an answer.

**Matched across arms:** the compounds, the two-stage protocol, the three-candidate budget,
the context packing (six compounds per fresh context), the closed-book instruction, the
anonymised blind forward-prediction stage, the scorer. **Not matched:** verification ran
only for the three models whose output contract justified it, Composer 2.5 and GPT-5.6 Luna
being excluded at 67% and 76% formula adherence.

**Table {#tab:esi-vendor-decomposition}. Decomposition, the three replicated arms.** Recall
and precision have different denominators, so the criterion is the inequality, not a
difference.

| model | generation recall | verification precision given recall | multi-candidate only |
|-------------------------------|------------------:|------------------------------------:|---------------------:|
| *Claude Opus (reference arm)* | *19/60 = 32%* [21–44] | *16/19 = 84%* [62–94] | *10/13 = 77%* |
| `grok-4.6` | 32/60 = 53% [41–65] | 20/32 = 62% [45–77] | 20/32 = 62% |
| `gemini-3.7-flash` | 30/60 = 50% [38–62] | 22/30 = 73% [56–86] | 22/30 = 73% |
| `gpt-5.6-sol` | 25/60 = 42% [30–54] | 17/25 = 68% [48–83] | 16/24 = 67% |

**Two corrections the marginal intervals above do not show.** Recall and precision are
measured on the same compounds, so the inequality belongs to the *paired* difference, not
to whether two intervals overlap. Bootstrapping compounds
(`scripts/cross_vendor_gap.py`) resolves three of the four arms — Claude
+52.5 points [+31.2 to +71.7], GPT-5.6 Sol +26.3 [+4.5 to +48.6], Gemini +23.3
[+3.2 to +44.3] — and leaves Grok +9.2 [−11.7 to +30.0] directional. Claude's is the
widest and the least informative: its singleton-heavy candidate sets inflate it. The recall column is not budget-matched: the
reference arm holds 2.20 candidates per compound against exactly 3.00 for every comparison
model (Composer 2.82), and a longer list can only raise recall. At one candidate, the only
budget every model met, recall is 14/60 = 23% for Claude, 23/60 = 38% for Grok, 23/60 = 38%
for Gemini and 21/60 = 35% for GPT-5.6 Sol (`scripts/cross_vendor_budget.py`); the ordering
is unchanged and Grok's margin is 15 points rather than 21.

**What these identifiers name.** The models are as served by the coding-agent harness, not
stock vendor endpoints, and the harness supplies its own agent system prompt above the task
text. Its allowlist reads `gpt-5.6-sol-xhigh`, `gpt-5.6-sol-high`, `gpt-5.6-luna-high`,
`gemini-3.7-flash-high`, `cursor-grok-4.6-high-fast`, `composer-2.5` — every identifier but
the last carries a **reasoning-effort suffix**, a decoding parameter the Claude reference
arm never had ([@sec:esi-versions]). **The tier used for each arm is not recorded**, because
the run did not report which allowlist entry it selected; a run at `-xhigh` is not the same
measurement as one at `-high`, which is why the article reports these as vendor-family
results.

**Contamination control.** The cloud agents cloned the whole repository and the answer files
for these 60 compounds are tracked, so blindness rested on an instruction that nothing verifies
after the fact. The control is a re-solve with those files out of the workspace: Grok 4.6
re-ran all ten batches from a clean clone (`sweep_out/grok-4.6-clean/`).

**Table {#tab:esi-clean-clone}. Clean-clone contamination control, Grok 4.6.**

| arm | recall | 95% CI | parse | formula match |
|-----------------------------------|-------------:|--------:|--------:|--------------:|
| original (answer files present) | 32/60 = 53% | [41–65] | 179/180 | 171/180 |
| clean clone (answer files absent) | 28/60 = 47% | [35–59] | 176/180 | 174/180 |

Paired, that is **b=8, c=4, McNemar exact p=0.39**. The decisive detail is the asymmetry
rather than the totals: a model reading the key would solve a superset, and instead **four
compounds were solved only in the arm that had no key**, with 24 of the 60 solved by both,
while formula adherence did not degrade (174/180 candidates in the clean arm against
171/180 in the original). The control covers Grok alone; Gemini 3.7
Flash and GPT-5.6 Sol rest on the shared instruction and the stereochemistry evidence of
[@sec:esi-scoring].

## Modality ablation and contamination controls {#sec:esi-ablation}

**The leave-one-modality-out ablation was specified and never run, and no leave-one-out
result appears in the article.** The staged prompts `prompt_noIR.txt`, `prompt_noH.txt` and
`prompt_noC.txt` sit under `data/modality/` (2026-06-16) with no corresponding
`out_*.json`. Two attempts were discarded, and why is instructive. The first used one
solver agent per condition, so agent quality was a single draw that swamped the modality
effect: full modality came out worst at 3/16, −IR best at 8/16. The second ran a fresh −IR
arm against the *archived* benchmark predictions as its control, giving full 10/30, −IR
22/30 and formula-only 2/30 on the simple stratum — −IR beating full modality by 40 points,
McNemar p=0.004, impossible on the modality reading and diagnostic of the confound. The
rule this yielded: every arm of an ablation must be generated in one campaign, the control
included (`docs/MODALITY_ABLATION.md`).

**The formula-only control shares that structure and is not impugned by it**, because the
confound runs against the finding: only the formula-only arm was freshly generated
(2026-07-28), its comparison arm re-using the archived June predictions (whose 60 top-1
answers are byte-identical to that run), and fresh agents reason harder per compound, so the
bias favours the formula-only arm — which still collapsed. That solver received the formula
and nothing else, was barred from reading any repository file or searching the web, and was
allowed RDKit only to check that a proposed SMILES parses and matches the formula. The
outcomes are perfectly nested: **eleven** compounds are solved with the spectra and not
without, **none** the other way round (b=11, c=0, McNemar exact p=0.001), for 3/60 against
14/60 top-1 and 3/60 against 19/60 recovered ([@tab:formula-only-control]).

The three formula-only successes are named rather than rounded away, because they do not
all support one reading: **C₁₅H₁₅ClF₂O₃SSi**, a 2-(trimethylsilyl)aryl sulfonate whose
composition is a near-unique benzyne-precursor signature and which is absent from
PubChem[@kim2023pubchem], so the formula is close to determining; **C₁₃H₁₉NO₄S**,
*N*-tosyl-leucine (CAS 67368-40-5), where inference and recall are both available; and
**C₁₇H₂₆O₃**, [6]-paradol (CAS 27113-22-0), a catalogued natural product that composition alone constrains very little.

**The recency control** is independent and agrees. It addresses the pretraining-exposure
hazard[@xu2024contamination] head-on rather than by masking: publication years were
resolved for all 194 compounds from their accessions (`scripts/contamination_recency.py`)
and span 2008–2026. Accuracy is flat: **28.6%** for the older half (≤2020, n=112) against
**28.0%** for the newer (n=82), point-biserial r between year and correctness of **−0.007**; the most
recent bucket (≥2024, n=25) is in fact highest at 40% [23–59]. The raw split is biased against
the newer half, since newer papers skew larger (median 22 heavy atoms against 20) and size
dominates accuracy; stratifying by heavy-atom band removes that (newer against older —
≤15: 64% against 58%; 16–25: 34% against 25%; >25: 6% against 8%). The size-adjusted
older-minus-newer difference
is **−5.1 points, 95% CI [−17.2 to +7.0]** (Cochran–Mantel–Haenszel χ²=0.42, p=0.51,
continuity-corrected) — a bound on any recency effect, not a reversed one.

## Human-expert audit: protocol and status {#sec:esi-audit}

Solver and verifier are both LLMs, so the one validation the authors cannot perform
themselves is an expert-chemist review of the outputs. The audit package is blinded,
pre-registered and **frozen** before any review, and regenerates deterministically at seed 0
from `scripts/make_audit_sample.py` into `data/audit/`.

The panel comprises three independent PhD-level synthetic or analytical chemists with no prior
exposure to the benchmark answers, at roughly 3–4 person-hours each. The sample is a
difficulty-stratified draw (15 simple, 15 complex) from the 60-compound
forward-verification set, the only split carrying both the ranked candidates and the
observed spectra. Per compound, a reviewer sees the exact solver prompt — formula, IR, ¹H,
¹³C — and the model's top-ranked candidate rendered as a 2D structure, with model identity
and ground truth hidden.

**Table {#tab:esi-audit-kit}. Composition of the frozen audit kit.**

| item | count |
|--------------------------------------------------------------------|------:|
| compounds in the kit | 37 |
| Task 1 panel (unbiased stratified draw) | 30 |
| Task 2 ranking items | 37 |
| …carrying the true structure and a real choice, scoring precision | 13 |
| …carrying the true structure but a single candidate, excluded | 3 |
| …carrying no correct candidate, measuring expert calibration | 21 |
| model top-1 exact on the Task 1 panel (held in the withheld key only) | 7/30 |

Task 1 scores the model's top-1 for consistency with all provided spectra (1–5), gives a
categorical verdict (correct / wrong-regiochemistry / wrong-scaffold / uninterpretable) and
names the single most diagnostic peak; the read-outs are inter-rater agreement and the
fraction of mechanically-wrong top-1 answers judged spectrally consistent but as a different
regioisomer. Task 2 presents the shuffled, unlabelled candidate set for ranking by spectral
fit, against the LLM forward-verifier's and the deterministic lookup's picks on identical
sets. Task 2 is shown on **every** compound, so its presence signals nothing: an
earlier version showed it only on recall-positive compounds, which leaked Task 1 twice over
and moved the apparent rate of correct answers from 12% to 67%. The seven extra compounds
carry Task 2 only, because a correct top-1 is recall-positive by definition, so enriching
the Task 1 draw for recall-positive compounds would raise the very rate Task 1 judges.

**Status.** The panel has not been run and the article reports no audit result
([@sec:limitations]). One reviewer file is deposited at `data/audit/responses/` (submitted
2026-08-18 UTC), incomplete against the 37-item kit. **It is from a co-author of this
article**, recorded while testing that the worksheet and the scorer work end to end, and it
is therefore not a panel response: the panel is defined as three chemists independent of the
authors, and no reported number will draw on this file. A single partial reviewer would
support neither read-out in any case, inter-rater agreement needing at least two reviewers
and the pre-registered panel being three. Scoring is mechanical (`scripts/score_audit.py`); the
three Task 2 sets holding a single candidate (A19, A21, A30) cannot be ranked, so the
scorer excludes and flags them. Until expert results are in, the
two claims the panel targets — what a miss actually is ([@sec:well-llms-elucidate-real]),
and whether forward verification is a trustworthy re-ranker
([@sec:forward-verification-elucidation]) — should be read as machine-validated (RDKit
InChIKey) but not yet human-validated.

## References

::: {#refs}
:::

```{=latex}
\clearpage
```

<!-- GAP: the instruction text dispatched to the Claude solver and forward-prediction
     sub-agents is not committed anywhere in the repository; only the per-compound batch
     data files are released. The prompts quoted verbatim in S2 are the cross-vendor
     harness prompts (scripts/cross_vendor_sweep.py, sweep_prompts/), which the Claude arms
     were not run from. -->
<!-- GAP: no dated model snapshot identifier exists for any Claude arm and the harness
     exposes none; the reasoning-effort tier used for each cross-vendor arm was likewise
     not recorded. Neither can be supplied after the fact. -->
<!-- GAP: no decoding parameters (temperature, top_p, top_k, max_tokens, generation seed,
     thinking budget) were set or recorded for any run. -->
<!-- GAP: the sampling seed and draw parameters for the main round (140 problems) and the
     controlled v3 round (40 problems) are not recorded in any document or artifact; only
     the within-compound control's defaults (--n 20 --seed 23) and the pilot's
     (--n 21 --seed 7) appear in the released code. The cohorts are reproducible, since
     questions2.jsonl / answers2.jsonl are released, but the draws are not re-runnable
     from recorded parameters. -->
<!-- GAP: transcripts of the run-time closed-book audit are not deposited, so that audit
     cannot be re-verified from the release; the article states this. -->

<!-- TO-PAPER: two passages below are results, not operational detail. They are left in
     place because docs/PAPER.md is owned by another editor; both should move, and the ESI
     copy should then be cut to a pointer.

     1. From the forward-verification-detail section, the paragraph on the widened pool:

        "The added coverage buys a direct view of the mechanism — on **18 of the 60**
        compounds the verifier abandons its previous pick for a newly-selectable
        candidate, and in **not one** does the outcome change; every switch is wrong
        structure to wrong structure."

        Belongs in [@sec:generate-wide-testing-recipe], next to the statement that no
        number moves when coverage is completed: it is the reason no number moves, and it
        is the strongest direct evidence in the manuscript that the ceiling is recall
        rather than ranking.

     2. From the non-LLM-verifier section, on the deterministic lookup:

        "The lookup's tie with self-ranking there is not agreement: at n=65 it **gains
        seven compounds and loses seven** (McNemar b=c=7, p=1.00), reshuffling
        energetically while carrying no net discriminative signal."

        Belongs in [@sec:non-llm-verifiers-deterministic], where the lookup's tie with
        self-ranking is reported: the tie is currently readable as the lookup agreeing
        with the solver, and b=c=7 says the opposite. -->
