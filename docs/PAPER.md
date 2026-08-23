# Recall, not verification, is the bottleneck when frontier LLMs elucidate molecular structures from real spectra

**Ilkham Yabbarov**^a^ *(corresponding author: yabbaroi@mcmaster.ca)*, **Rudra Sondhi**^a^, **Rodrigo A. Vargas-Hernández**^a^

*^a^ Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario L8S 4L8, Canada.*

<!-- AUTHORS — name forms and ORCID iDs below are taken from each author's own published
     bylines and ORCID record, not guessed. RSC links iDs through the submission system
     rather than printing them in the manuscript body, so they are recorded here.
       I. Yabbarov            ORCID: [TODO: 0000-0000-0000-0000]
                              (corresponding; yabbaroi@mcmaster.ca)
       R. Sondhi              ORCID: 0009-0003-3034-7347
                              verified: https://orcid.org/0009-0003-3034-7347
                              name form identical across every byline he has;
                              no email found in any public source — ask him
       R. A. Vargas-Hernández ORCID: 0000-0002-5559-6521
                              verified: https://orcid.org/0000-0002-5559-6521
                              email vargashr@mcmaster.ca (his own corresponding-author
                              footnote, arXiv:2509.13504 / Digital Discovery 2026)
                              accented surname with middle initial is the form on every
                              2025–26 byline, including his own Digital Discovery paper;
                              he also carries two further McMaster affiliations (School of
                              Computational Science and Engineering; Brockhouse Institute
                              for Materials Research) — ask whether he wants them listed
     `python scripts/check_manuscript.py` lists every outstanding item of this kind. -->

---

## Abstract

Given the molecular formula together with the infrared band list and ¹H/¹³C shift lists
exactly as reported in an open-access paper, how often does a frontier large language model
(here, Claude) recover the correct molecular *constitution*? We find 28% (top-1, n=194;
95% CI 22–35) — far below the near-100% implied by curated demonstrations, and 15% once
the benchmark's deliberate 50/50 difficulty balance is reweighted to the composition of the
corpus it was drawn from ([@sec:benchmark-design-irspectra-bench]).

The bottleneck lies in the model's *proposal* rather than its judgment. The model proposes
the true structure for only 34% of compounds; where it does, forward-verification —
predicting each candidate's ¹³C spectrum and re-ranking by agreement with the observed one
— selects it 89% of the time (58/65, and 81% on the 37 where more than one candidate
existed and a ranker had something to do). Recall, not verification, is the wall.

We release three things: *IRexp*, the largest openly redistributable collection of
*experimental* infrared band lists (121,233 records, a third structure-linked);
*IRSpectra-Bench*, a blind, mechanically scored benchmark of 194 compounds; and a
training-free *forward-verification* recipe. The two levers are distinct. Verification
re-ranks a fixed candidate set and lifts top-1 from 28% to 30% over all 194 compounds.
*Generating wider* moves recall from 32% to 42% and carries top-1 from 23% to 30% over the
60 compounds of the two controlled rounds, where wide generation was run ([@sec:result],
[@sec:generate-wide-testing-recipe]). Both of those top-1 steps are directional rather than
statistically resolved, and the recall gain is the better-supported effect. Fine-tuning a small generator on IRexp moves the recall bound rather than removing it
([@sec:recall-wall-task-intrinsic]). Two contamination controls agree: masking the spectra
drops top-1 from 23% to 5% on those same 60 compounds, and accuracy is flat in the source
paper's publication year ([@sec:model-reading-spectra-formula]). The diagnosis also holds
outside one vendor: Grok 4.6, Gemini 3.7 Flash and GPT-5.6 Sol all verify better than they
generate ([@sec:diagnosis-hold-outside-one]). All data, predictions and code are released.

---

## Introduction {#sec:introduction}

Determining a molecule's structure from its spectra is a central, time-consuming task in
synthetic and analytical chemistry. Machine learning attacks it with encoder–decoder
models trained on paired corpora; *Spectro*, for one, learns ¹H/¹³C/IR → SELFIES from
6,833 molecules[@chacko2024spectro]. General-purpose LLMs are now reported to do it
off-the-shelf: a non-peer-reviewed 2026 industrial white paper found that Claude Opus
matched or beat commercial NMR-prediction software in the forward direction
(structure→spectrum, ±0.08 ppm ¹H) and "recovered all eight simpler structures on every
attempt" in the inverse.[@kamber2026chemist] We treat those numbers as a motivating claim
to test against peer-reviewed benchmarks, not as an established baseline.

That evaluation is narrow: 15 inverse problems on curated single-ring or two-fragment
molecules, NMR only, seven of them given the *starting-material structure* as a hint, and
"recovery" scored leniently over three runs and three ranked candidates. The question a
chemist actually faces — *take an arbitrary experimental spectrum from a paper and
recover the structure* — is left open. It needs a large, diverse, real benchmark; blind,
reproducible scoring; and honest accounting for the methodological choices that inflate
or deflate the apparent score.

We provide all three. *IRexp* ([@sec:irexp-dataset]) is, to our knowledge, the largest
openly *redistributable* collection of experimental IR *band lists* (121,233 records;
43,060 structure-linked; 33,201 IR + ¹H + ¹³C + structure); the superlative is scoped to that
object type, since view-only libraries such as SDBS and commercial libraries hold more
structure-linked *spectra* but cannot be redistributed ([@sec:motivation]). On it,
*IRSpectra-Bench* ([@sec:benchmark-design-irspectra-bench]) is, to our knowledge, the
first blind, mechanically scored, complexity-stratified evaluation of frontier-LLM
elucidation on real spectra: measured in depth on Claude, replicated across three other
model families ([@sec:diagnosis-hold-outside-one]), and isolating a large
solver-methodology effect with a within-compound control ([@sec:well-llms-elucidate-real]).
Its ground truth is literature structures resolved deterministically (OPSIN/RDKit) and
checked mechanically against the source articles (560/560 bands on a seed-fixed sample,
[@sec:contents-licensing]; the *expert-chemist* review is prepared but not yet run,
[@sec:limitations]); no LLM curates labels or scores predictions.

Forward-verification elucidation ([@sec:forward-verification-elucidation]) turns the
model's *strong* direction (forward prediction) against its *weak* one (inverse
regiochemistry); the loop is prior art ([@sec:related-work]), the decomposition it enables
is ours, run training-free over every benchmark compound. The finding is a sharp
asymmetry: given a candidate set containing it, the model *verifies* the correct structure
89% of the time, yet *proposes* it for only 34% of compounds, so generation is what binds
the result ([@fig:fig-wall]). The gain is bounded (top-1 28%→30% on n=194; 23%→30% on the
60-compound arm, the two pre-registered controlled rounds on which wide generation was
also tested) and, by our own measurements,
cannot exceed a recall/precision ceiling without sharper verification or 2D-NMR data.

![All 194 benchmark compounds as a single part-to-whole bar. The true structure is verified top-1 for 58 (green), recalled but mis-ranked for 7 (vermilion), and never proposed for 129 (grey): *the wall*, 66% of the bar. Generation recall (the fraction of compounds whose true structure appears anywhere in the solver's candidate list) is 65/194 = 34%. Of those 65, forward-verification then ranks 58 first: verification precision (conditional on recall) is 58/65 = 89%. Their product is the 30% end-to-end top-1. The two rates have different denominators and are not differenced.](docs/figures/fig_wall.png){#fig:fig-wall}

Solver and verifier ([@sfig:overview]) are LLM agents on a consumer subscription, with no
fine-tuning and no API spend. They are cheap to *re-run* but not reproducible: the harness
pins no model snapshot, exposes no temperature or seed, and carries an undisclosed product
system prompt. Our own dispatch instruction for the main rounds was also not captured,
only the per-compound data it wrapped, so an outside group reproduces this
distributionally rather than exactly ([@sec:methods]). Scoring is exactly reproducible:
predictions, ground truth and scorers are released, and every number in the training-free
core ([@sec:benchmark-design-irspectra-bench]–[@sec:generate-wide-testing-recipe], [@sec:model-reading-spectra-formula])
regenerates from them. The two exceptions are [@sec:non-llm-verifiers-deterministic]'s HOSE
lookup and GNN, which need an nmrshiftdb2 dump we cannot redistribute (see *Data
availability*); that GNN and the [@sec:recall-wall-task-intrinsic] generator are trained
probes, fenced as complements to the training-free core.

### Related work {#sec:related-work}

**Trained spectra→structure models.** The dominant line trains sequence or graph decoders
on spectra: *Spectro*[@chacko2024spectro], a multitask CNN+transformer for routine
1D-NMR[@hu2024multitask], set/graph transformers such as NMRTrans[@yang2026nmrtrans], and
— closest to our multimodal setting — *NMIRacle*[@ottomano2025nmiracle], conditioned
jointly on IR + ¹H + ¹³C. They are accurate *in-distribution* but retrained per modality
and dependent on a labelled spectra→structure corpus. That resource is scarce rather than
absent, and one concurrent effort attacks it the same way we do: NMRTrans builds NMRSpec,
a literature-mined corpus of experimental ¹H/¹³C spectra[@yang2026nmrtrans]. IRexp is the
complement rather than the competitor — infrared band lists, released under permissive
licences for redistribution ([@sec:contents-licensing]) — and the two together are the
open, experimental, multimodal corpus neither supplies alone.

**LLMs as elucidators, and how this work differs.** LLM-orchestrated tools already plan
and execute real syntheses (ChemCrow[@mbran2024chemcrow],
Coscientist[@boiko2023coscientist]); such systems *call* an elucidation routine, and this
paper measures what one returns. General-purpose LLMs have been applied
off-the-shelf[@kamber2026chemist], as have multimodal models over multi-spectral input
(SpectraLLM, SpecMol)[@su2025spectrallm; @shen2025specmol] and knowledge-enhanced
tree-search reasoning[@zhuang2025treesearch]; *MolPuzzle*[@guo2024molpuzzle] supplies
IR+MS+¹H+¹³C puzzles with the formula given, and *IR-Agent*[@noh2025iragent] emulates
expert IR interpretation on experimental spectra with a multi-agent framework. We claim
priority on none of them: IR-Agent improves *how the model reads a spectrum*, where we ask
what limits the outcome once it has.

Prior benchmarks and trained baselines evaluate on simulated or software-predicted
spectra[@chacko2024spectro; @ottomano2025nmiracle] or on curated single-instrument
libraries — Alberts et al. use NIST gas-phase IR[@alberts2024ir; @alberts2025benchmarks] —
where IRSpectra-Bench uses spectra as reported by the authors of the source papers,
across thousands of laboratories and instruments; the contrast is with both simulation
*and* curated uniformity. That line is also the state of the art for *trained,
formula-conditioned IR* elucidation — an IR→structure transformer[@alberts2024ir] now at
63.8% top-1 / 84.0% top-10 on experimental NIST gas-phase spectra given the formula,
pretrained on 1,399,806 simulated spectra[@alberts2025benchmarks]. That headline is on a
6–13-heavy-atom subset, the range where our own accuracy is highest (60.5% top-1 for
≤15 heavy atoms, [@sec:headline-performance]), so on comparable molecules the training-free
LLM and the purpose-trained transformer are closer than the headline numbers suggest. Size
is not the whole story, though, and we do not claim it is: the same work reports 59.94%
on a 5–35-heavy-atom set (n=5,024), which spans most of our range and falls only four
points. What differs there is the data rather than the size: a single-instrument gas-phase
library against heterogeneous literature-reported band lists. Neither setting bounds the
other. Reported accuracies also swing
with inference method and scoring harness: GPT-4o is scored at 1.4% on MolPuzzle by
the benchmark's own authors[@guo2024molpuzzle], at 27.8% under a plain
chain-of-thought harness, and at 57.8% with knowledge-enhanced tree-search
reasoning[@zhuang2025treesearch] — a factor of forty for one model on one benchmark.
Cross-paper numbers are therefore not comparable, and we fix and release a single
pre-registered RDKit-InChIKey protocol with bootstrap CIs.

**Computational NMR for structure validation.** Forward-verification is the LLM analog of
a workflow chemists already trust — compute the spectrum each candidate *would* give and
match it to experiment: DP4 / DP4+ over GIAO-DFT shifts in
solution[@smith2010dp4; @grimblat2015dp4plus], *NMR crystallography* with GIPAW shifts
in the solid state[@pickard2001gipaw; @ashbrook2016nmrcryst]. We swap the quantum-chemical
predictor for a forward LLM, trading accuracy for zero setup cost, and inherit the
principle that *verification by forward prediction is easier than inverse generation*.
*Computer-assisted structure elucidation* (CASE) has run the loop since the 1990s and
overturned published assignments[@elyashberg2012case; @elyashberg2015case]; its generator
is a strict enumerator with exhaustive recall by construction[@elyashberg2015case] — the axis
on which we find the LLM weak, and the axis existing LLM benchmarks leave unmeasured by
reporting a single aggregate score. The decomposition is stable under every perturbation
we could run — four Claude models, a second chemical domain, four verifiers, all
recall-bound ([@sec:model-comparison-benchmark-ranks], [@sec:domain-case-study-battery],
[@sec:non-llm-verifiers-deterministic]) — but is not tested outside the Claude family
([@sec:limitations]).

**The generate-and-forward-verify loop is not ours.** *NMR-Solver*[@jin2025nmrsolver]
builds it without an LLM, retrieving and fragment-recombining candidates and ranking them
by ¹H/¹³C shifts forward-predicted with NMRNet (¹³C MAE 1.098 ppm); on ≈450 experimental
literature spectra with the formula supplied it reports 52.89% top-1, well above our
28.4%. [@sec:forward-verification-elucidation] asks a different question — *how much of
the remaining error is generation and how much is verification* — answered by
decomposition ([@sec:result]) rather than by a better solver. Its predictor is roughly
twice as sharp as the ≈2 ppm LLM forward-predictor that [@sec:method] identifies as the
binding constraint, and it delivers roughly twice the top-1. That is what our
[@sec:non-llm-verifiers-deterministic] ablation predicts and what [@sec:method]'s
separability measurement implies. *NMRAgent*[@fang2026nmragent] couples spectral tools to a knowledge
graph and validates on newly isolated natural products; it is complementary — a
best-effort system, where we measure an off-the-shelf model.

---

## The IRexp dataset {#sec:irexp-dataset}

### Motivation {#sec:motivation}

An IRexp record is a *band list* — peak positions in cm⁻¹ transcribed by an author into
a paper's text — with co-reported ¹H/¹³C shift lists and, where resolvable, the 2D
structure. IRexp contains no absorbance traces. That is the published form, and what a
language model consumes, but it is a different object from a digitised spectrum and the
two should not be counted against one another.

Among *digitised spectra*, free downloads run to the NIST WebBook[@nist_webbook] (≈16k)
and the Chemotion ELN deposit[@chemotion2024] (≈2k). AIST SDBS[@sdbs] is larger (≈54k
FT-IR, all structure-linked) but *view-only* (50 spectra/day, no bulk export), so IRexp
does not compete there: SDBS alone holds more structure-linked spectra than IRexp holds
structure-linked band lists. Among text-derived *band lists* IRexp is the largest
*openly redistributable* collection by record count, a claim deliberately scoped to that
object type.

### Construction {#sec:construction}

Experimental sections report per-compound IR band lists with co-reported ¹H/¹³C NMR in a
stable textual convention. Mining it is mature[@swain2016chemdataextractor]; we add a
pipeline specialised to the *IR band list*, the modality those tools passed over.

- **Discovery.** Open-access literature is harvested in bulk from the PMC Open-Access
  Subset[@pmc_oa] and the Chemotion FT-IR deposit (RADAR4Chem).
- **Extraction.** A deterministic parser segments experimental text per compound and
  extracts IR wavenumbers and ¹H/¹³C shifts, gated against scan-range artefacts and prose
  false-positives.
- **Resolution.** IUPAC names go to SMILES with OPSIN[@lowe2011opsin] and
  RDKit[@landrum_rdkit] canonicalisation (InChIKey, SELFIES[@krenn2020selfies]), with a
  PubChem[@kim2023pubchem] fallback for trivial names; handling open-access label
  conventions and narrative artefacts raised structure coverage from 24% to 35%.

### Contents and licensing {#sec:contents-licensing}

[@tab:irexp-dataset-contents-provenance] gives what the release holds and where each part
came from.

**Table {#tab:irexp-dataset-contents-provenance}. IRexp dataset contents and provenance.**

| field | value |
|---|--:|
| experimental IR band-list records | **121,233** |
| …co-reporting ¹H and/or ¹³C NMR | 87,075 (72%) |
| …with a resolved 2D structure | 43,060 (35.5%) |
| …of these, with ¹H and/or ¹³C NMR | 40,702 |
| …of these, with both ¹H and ¹³C (full quadruples) | 33,201 |
| | |
| *by provenance:* author-transcribed from PMC-OA text (CC-BY) | 119,345 |
| *by provenance:* peak-picked from Chemotion ELN deposits (CC-BY-SA) | 1,888 |

The pools differ: PMC records are author-transcribed (median 9 bands), Chemotion records
peak-picked from deposited spectra (median 39), so users training on band density should
treat them apart. `scripts/split_license_pools.py` separates them on `source_doi` and
stamps each record's licence.

**Extraction fidelity is measured.** On a seed-fixed random sample of 60
PMC-sourced records (`scripts/audit_extraction.py --n 60 --seed 0`) we re-fetched each
article and checked every recorded wavenumber against its text: 560/560 bands and 60/60
records were confirmed (Wilson 95% CI 99.3–100% and 94–100%). This bounds *transcription*
error — hallucinated, mis-parsed or unit-mangled values — below 1% of bands. It does
not measure whether the parser found every IR string in every paper, a recall question
requiring human reading; that audit is prepared but not yet run ([@sec:limitations]).

`irexp_resolved` (43,060 records, 100% structure-linked) is the benchmark-ready split,
≈6× the 6,833-molecule set used to train Spectro[@chacko2024spectro] ([@sfig:dataset]).

---

## Benchmark design (IRSpectra-Bench) {#sec:benchmark-design-irspectra-bench}

From `irexp_resolved` we draw *IRSpectra-Bench*, 194 blind elucidation problems, each
giving the *molecular formula* (as from HRMS), the *IR band list* and the *¹H and ¹³C
shift lists*; no name, SMILES or scaffold hint. One exception is measured rather than assumed: the shift strings are the source paper's, and in 10 of the 194 the authors' peak assignments name a ring system (`2CH2·pyrrolidine`, `pyridazinone H5`). Those compounds are solved 1/10 against 54/184 (29.3%) for the rest (`scripts/prompt_leakage.py`), so the annotation does not carry the headline — they are harder than average, which is presumably why their authors annotated them. We keep them rather than drop them. Main-round ground truths are spectrally
validated by an automated RDKit check (¹³C peaks vs symmetry-unique carbons, formula
match, SELFIES round-trip) excluding merged or incomplete spectra — 6/140, leaving 134.
`scripts/validate_benchmark.py` runs the deterministic filter over all three rounds,
regenerating every `clean_qids.json` from the released questions and answers.

The filter does not gate on ¹H, and we report what that leaves. In 13 of the 194
retained records the reported ¹H integral exceeds the reference structure's hydrogen count
— residual solvent, water, exchangeable protons, or a rotamer mixture. They are printed as
a diagnostic, not excluded: the cohort was fixed in advance, and re-filtering post hoc on a
criterion chosen after seeing results is a degree of freedom a benchmark should not take.
We report the sensitivity instead: dropping all 13 moves the headline from 28.4% to
29.3% (53/181), +0.9 points, leaving every conclusion unchanged. The controlled rounds'
60 compounds are fixed, pre-registered sets, audited the same way but reported rather than
filtered (57/60 pass; [@sec:limitations]).

**Difficulty is declared in advance, as a property of the compound.** By RDKit ring
analysis a compound is *simple* iff it has at most two rings, no fused/spiro/bridgehead
system and ≤22 heavy atoms; all others are *complex* (98 simple / 96 complex), so the
split is exhaustive. The threshold is not load-bearing: sweeping it from 18 to 26 moves
the simple-minus-complex top-1 gap only between 36 and 40 points (39.6 as released;
`scripts/difficulty_sensitivity.py`). This axis is distinct from the continuous size
gradient of [@sec:headline-performance] (≤15 / 16–25 / >25 heavy atoms), and InChIKey
de-duplication across rounds prevents leakage.

**The 50/50 balance is by design, and the corpus is not balanced.** The sampler fills each
stratum to half the round, so "98 simple / 96 complex" is a property of the draw and not an
observation about the literature. Under the same eligibility filters the eligible corpus is
17.5% simple and 82.5% complex (5,059 / 23,929 of 28,988; median 26 heavy atoms against
the benchmark's 20), so simple compounds are enriched 2.9×
(`scripts/corpus_reweight.py`). Balancing is the right choice for measuring a gradient —
an unbalanced draw would put almost no mass in the stratum where the model succeeds — but
it means the headline is a weighted average under weights we chose. Reweighted to the
corpus, top-1 falls from 28.4% to 15.2% [10.7–20.4] and recall from 33.5% to
19.8% [14.3–25.7], on bootstrap 95% CIs. We report
the benchmark figure as the headline because it is the one the released set reproduces, and
the reweighted figure as the better estimate of what a chemist meets on an arbitrary paper.
The reweighting assumes the one sampler filter it cannot apply — recovery of the raw ¹H
string, which needs a network fetch per record — is independent of difficulty.

**Scoring is mechanical.** A prediction is *correct* if its RDKit InChIKey connectivity
layer (first 14 characters) matches the reference: we score *constitution*, so correct
constitution with wrong stereochemistry counts as correct. We report the strict
alternative rather than assert it is immaterial — the *full*, stereochemistry-sensitive
InChIKey gives 21.1% top-1 and 25.8% recovered (41/194 and 50/194) against 28.4% /
33.5%, 7.3 points lower, so the constitution figure is an upper bound on
full-stereochemistry accuracy. Constitution is the headline because 1D ¹H/¹³C/IR rarely
fixes absolute configuration: only 10.3% (20/194) of answers carry a *defined* (assigned
R/S) stereocentre, and a model is penalised there for information the prompt never
contained (`scripts/score_main.py --stereo`).

**Metrics.** *Top-1 (exact constitution)* is the fraction whose best-ranked candidate
matches at the connectivity layer; *recovered (top-3)* the fraction whose reference
appears among the up-to-three returned candidates, the lenient "recovery" protocol of ref.
[@kamber2026chemist] — their metric, under their name. *Generation recall* is the
fraction whose reference is in the candidate pool *before* re-ranking, the ceiling any
verifier can reach; it coincides with recovered (top-3) except in the generate-wide arm of
[@sec:generate-wide-testing-recipe], where the pool is larger. *Verification
precision (conditional on recall)*, measured over recall-positive compounds alone, isolates
verification from generation.
The forward-verifier ranks by a symmetric *chamfer distance* between predicted and
observed ¹³C peak sets (lower is better, no equal-count requirement); Morgan(2, 2048)[@rogers2010ecfp] Tanimoto gives a graded scaffold-family signal. CIs are bootstrap
95%; model-vs-model differences use McNemar's exact test[@mcnemar1947] with Holm
correction[@holm1979].

Solvers are frontier LLM agents (Claude Opus), one sub-agent per batch, closed-book under
a consumer subscription: no tools beyond an RDKit formula check, no ground truth, verified
by grep-auditing transcripts.

Formula adherence is high but imperfect. Of the 126 candidates carried through
forward-verification on the original arm ([@sec:result]), 91.3% (115/126) match the given
formula exactly, and 76.6% do across the full top-3 pool. Adherence is also not uniform
across rounds: on top-1 answers it is 95.0% (38/40) in v3 and 90.0% (18/20) in the
v2-control — the two pre-registered controlled rounds, 60 compounds between them — against
77.6% (104/134) in the headline main round. That is a structure of the wrong composition,
in violation of a constraint the solver was explicitly handed, for about one main-round
compound in five. Such answers score as misses, so this inflates nothing, but the
main-round arm is the weakest-constrained (`scripts/analyze_misses.py`).

---

## How well do LLMs elucidate real structures? {#sec:well-llms-elucidate-real}

### Headline performance {#sec:headline-performance}

Solver agents work blind from formula + IR + ¹H + ¹³C and return up to three ranked
candidates, in bounded contexts reset every 2–12 compounds rather than one long context —
the variable that [@sec:methodology-dominates-within-compound] shows matters. The benchmark is all
194 compounds (134 spectrally-validated + 60 controlled-round;
`data/benchmark_main/raw/`).

**Table {#tab:headline-elucidation-performance-irspectra}. Headline elucidation performance on IRSpectra-Bench (n=194).** Overall and by difficulty stratum, with bootstrap 95% CIs.

| metric | overall (n=194) | simple (n=98) | complex (n=96) |
|---|--:|--:|--:|
| top-1 exact constitution | **28.4%** [22–35] | 48.0% [39–57] | 8.3% [3–15] |
| recovered (within top-3) | 33.5% [27–40] | 54.1% [44–63] | 12.5% [6–20] |
| scaffold-level (best Tanimoto ≥ 0.45) | 56% | 73% | 39% |
| mean best Tanimoto | 0.59 | 0.73 | 0.45 |

A strictly-validated subset with the controlled rounds restricted to their clean parts too
(134 main-clean + 57 controlled-clean = 191) reproduces this within ≈1 point on every
metric — top-1 28.8%, 95% CI 23–36; recall 34.0%; simple 49.0% / complex 8.4% — so the
asymmetric inclusion of the pre-registered controlled sets does not drive it. What does
move the overall figure is the deliberate 50/50 difficulty balance: reweighted to the
17.5%-simple composition of the eligible corpus, top-1 is 15.2% [10.7–20.4] and
recall 19.8% [14.3–25.7]
([@sec:benchmark-design-irspectra-bench]). The per-stratum figures are unaffected — only
the weights change — and the reweighted number is the one to read as
performance on an arbitrary paper.
Accuracy falls monotonically with size in step with the difficulty gradient
([@fig:fig1-difficulty]): 60.5% top-1 at ≤15 heavy atoms, 28.3% at 16–25, 7.0%
above 25 ([@sfig:size]).

![Top-1 and recovered accuracy on IRSpectra-Bench by difficulty (all / simple / complex, n=194), with bootstrap 95% confidence intervals. The benchmark separates a realistic difficulty range: simple targets are solved four to six times as often as complex ones on both metrics.](docs/figures/fig1_difficulty.png){#fig:fig1-difficulty}

Of the 137 analysable top-1 misses (139 in all; two predictions did not parse;
`scripts/analyze_misses.py`), 76.6% are constitutional isomers
of the true structure against 23.4% with the wrong formula. That is not mostly
regiochemistry: only 22.6% share the true Murcko scaffold, 2.9% reach Tanimoto ≥ 0.85, and the median
isomeric-miss Tanimoto is 0.39. Strict regiochemistry accounts for a fifth of failures;
most misses are larger rearrangements of the same atoms. Near-degenerate ¹H/¹³C
shifts under-determine connectivity, hence HMBC and NOESY; what the misses show is *wrong
connectivity at the right composition*.

### Reconciling with prior reports {#sec:reconciling-prior-reports}

Our 28% top-1 sits far below the ≈100% on "simple" molecules reported for the same model
class in a non-peer-reviewed company white paper.[@kamber2026chemist] Unscored
independently, it is best read against the *peer-reviewed* record:
MolPuzzle[@guo2024molpuzzle] and its re-scorings[@zhuang2025treesearch], and the trained
baselines[@chacko2024spectro; @ottomano2025nmiracle]. Four methodology and scoring
choices differ, each in the direction that raises a reported number; we name them without
apportioning the gap. **Difficulty:** ring count bounds difficulty from below rather than
proxying for it — our simple stratum includes a hexasubstituted benzene, while ≥4 rings
mark 38% of recall-negative compounds (those whose true structure the solver never
proposed) against 3% of recall-positive ones ([@sec:generate-wide-testing-recipe]). **Scoring:** prior work counts a recovery if the
reference appears among three ranked candidates over three independent runs; we report
single-run top-1 and top-3. **Hints:** prior hard targets got the starting-material SMILES
and we give none, though the formula we do give is worth 5% top-1 alone with the spectra
masked ([@sec:model-reading-spectra-formula]). **Curation:** prior compounds were
hand-selected; ours scraped, unfiltered for solvability.

**Versus trained models: a bound on the gap.** No system has been scored on our
test set, and published numbers differ in the three respects that most move the score:
spectrum realism, hints, exact-match definition. That is a reason not to read the
comparisons below as a ranking; it is not a reason no baseline was run, and none was. We
built and released the benchmark, so running an existing open elucidator on it is possible
and is the obvious next comparison — it needs a system whose weights and inference code are
public and that accepts IR + ¹H + ¹³C with a supplied formula, which we did not have. The
nearest thing here is the trained generator of [@sec:recall-wall-task-intrinsic], and it is
ours, not independent. Most trained baselines report
in-distribution accuracy on simulated spectra; Alberts et al. do not — 63.8% top-1 from IR
alone, formula supplied, on experimental NIST gas-phase spectra of a curated
single-instrument library of 6–13-heavy-atom molecules[@alberts2025benchmarks]. Ours
span 8–60 heavy atoms (median 20), only 15 of 194 (8%) in that window; against our
≤15-heavy-atom stratum (60.5%) their 63.8% is a near-tie. Size alone does not explain the
rest: the same work reports 59.94% over 5–35 heavy atoms (n=5,024), a range that covers
most of ours. The remaining difference is what the spectra are — one gas-phase instrument
against thousands of laboratories — and the comparison bounds the gap between those
regimes rather than ranking the two systems. Multimodal
systems report more still, on data of their own making: Spectro 93% (82% with
fixed embeddings) on a split whose IR is plotted from reference data and whose NMR is
software-*predicted*[@chacko2024spectro]; NMIRacle 48% top-1 / 66% top-15 on molecules
held out from a *simulated* corpus inside its own training distribution, as its authors
note[@ottomano2025nmiracle]. Ours is 28.4% top-1 (33.5% top-3), 29.9% with forward
verification ([@sec:forward-verification-elucidation]), on blind, real, literature-mined
experimental spectra of out-of-distribution compounds.

One asymmetry cuts against us: NMIRacle takes no molecular formula where we supply it
([@sec:benchmark-design-irspectra-bench]), so the settings differ on opposite axes — our
spectra real and out-of-distribution against their simulated and in-distribution, their
input strictly harder — and neither number bounds the other. Read only as a *bound on the
simulated-to-real gap*, the contrast suggests high in-distribution accuracies substantially
overstate real-world performance. Metric instability reinforces the caution: the ≈40×
MolPuzzle swing in [@sec:related-work] (GPT-4o: 1.4%[@guo2024molpuzzle] to 27.8% to
57.8%[@zhuang2025treesearch], method- and harness-dependent) bounds the weight any
unaudited near-100% claim[@kamber2026chemist] can bear.

### Methodology dominates: a within-compound control {#sec:methodology-dominates-within-compound}

The same 20 molecules were solved two ways: (a) one LLM context handling all sequentially
with no tools, (b) four independent agents of five compounds each with RDKit
formula-checking. Recovered (top-3) rose from 5% to 15% (1/20 → 3/20) and top-1
from 0% to 15% (0/20 → 3/20). McNemar's exact test
([@sec:benchmark-design-irspectra-bench]) does not reach significance, and at this size it
could not have: the exact test conditions on the discordant pairs, of which the top-1 arm
has three (b=0, c=3, p=0.25) and the recovered arm four (b=1, c=3, p=0.625). Below
six discordant pairs the smallest attainable two-sided p is above 0.05, so "not
significant" here reports the design, not the data. The 15% carries a Wilson 95% CI of
roughly 5–36%. Bounded, frequently-reset contexts with tool access therefore appear to
raise measured performance, consistent in direction but not established in size at n=20
(p=0.25): a directional within-compound demonstration, and it does not measure a 3× effect. Small
rounds swing widely (15–40% across n=20–40 draws), hence the full 194-compound
headline. It plausibly explains *part* of the gap to optimistic prior reports, whose
per-problem API calls implicitly used method (b) — a hypothesis, not a quantified
contribution.

### Model comparison: the benchmark orders capability but separates only the extremes {#sec:model-comparison-benchmark-ranks}

We solved a fixed 24-compound subset blind with four Claude models spanning a wide
capability range, including the newest (Fable 5), under one prompt, one scorer and one
candidate budget ([@fig:fig5-models], [@tab:four-model-comparison-fixed]).

One protocol asymmetry must be disclosed: the three comparison models solved the 24
compounds as four six-compound contexts each, whereas the Opus column reuses the headline
run, where those items sat in one six-compound and two twelve-compound contexts — the
variable that
[@sec:methodology-dominates-within-compound] measures at 5%→15%. The Opus estimate is
therefore not protocol-matched and, if anything, handicapped by the longer contexts; this
touches neither the nesting nor the Fable-vs-Haiku contrast, and a clean re-run is
outstanding in `docs/MODELS.md`.

![Four-model comparison on a fixed 24-compound subset, solved blind under one protocol: Fable 5 46% > Opus 25% > Sonnet 21% > Haiku 0% top-1. The outcomes are strictly nested — each stronger model solves a superset of the weaker one's compounds — so the benchmark is capability-sensitive, but at n=24 it is underpowered to separate adjacent models ([@sec:model-comparison-benchmark-ranks]).](docs/figures/fig5_models.png){#fig:fig5-models}

**Table {#tab:four-model-comparison-fixed}. Four-model comparison on a fixed 24-compound subset.** All four models ran the identical blind protocol.

| model | top-1 | recovered | top-1 95% CI |
|---|--:|--:|--:|
| Claude Fable 5 | **46%** | 54% | [25–67] |
| Claude Opus | 25% | 29% | [8–42] |
| Claude Sonnet | 21% | 25% | [8–38] |
| Claude Haiku | 0% | 4% | [0–14] |

CIs are bootstrap except Haiku's: Clopper–Pearson exact for 0/24, where the percentile
bootstrap is degenerate.

The models rank in monotonic capability order with strictly nested outcomes (Haiku
⊂ Sonnet ⊂ Opus ⊂ Fable), so the benchmark is capability-sensitive. The nesting makes the
*ranking* robust, but at n=24 the subset is underpowered to separate adjacent models. By
McNemar's exact test only Fable-vs-Haiku survives multiple-comparison correction
(Holm-adjusted p=0.006). Fable-vs-Opus does not: uncorrected p=0.063, which is the *floor*
for its five discordant pairs, so the comparison had no way to reach 0.05 (Holm-adjusted
p=0.19). Opus and Sonnet are indistinguishable. Two mid-tier models agreeing closely puts the recall-bound regime of
[@sec:headline-performance] beyond a single model; the newest nearly doubles the
next-best top-1 yet still misses the majority, leaving the benchmark far from saturated. We
used Claude-family models because they are callable for free under one subscription; a
cross-vendor sweep needs API access we did without, though the large monotonic spread makes
it unlikely the pattern is lineage-specific.

### Domain case study: battery-electrolyte chemistry {#sec:domain-case-study-battery}

To test the recall-bound regime on battery-electrolyte chemistry rather than on organic
molecules at large, we curated *IRSpectra-Bench-Electrolyte*: a 48-compound subset of
IRexp records across the six functional families that dominate lithium- and sodium-battery
electrolytes, eight compounds per class, held out of every other split and solved blind
under the identical protocol. Two yielded no parseable candidate, leaving 46 scored. These are
literature compounds, not operando or in-cell spectra, and we make no claim that they
are.

Performance lands in the same broad regime as the headline benchmark — top-1 26%,
recovered 28% (12/46 and 13/46; at n=46 the 95% CI is wide and overlaps the headline),
scored over the 46 that yielded a parseable candidate — consistent with a bottleneck in
the elucidation task rather than in any one chemical neighbourhood. The main round instead
scores an unparseable answer as a miss, and on that rule this arm reads 12/48 = 25%; we
report both rather than let two denominators sit unexplained. The true structure enters the candidate set for only 13 of 46 compounds and
ranks first in 12 of those 13. Forward-verification was not run here, so this is the
recall-bound pattern under the solver's own ranking rather than the
[@sec:forward-verification-elucidation] measurement ([@sfig:electrolyte]).
The per-class breakdown is [@tab:per-class-performance-irspectra]; at eight compounds a
class the intervals overlap throughout.

**Table {#tab:per-class-performance-irspectra}. Per-class performance on IRSpectra-Bench-Electrolyte (n=46).**

| electrolyte class | n | top-1 | 95% CI | recovered (top-3) | 95% CI |
|---|--:|--:|--:|--:|--:|
| sp³-C–F | 8 | **50%** | [22–78] | 50% | [22–78] |
| carbonate | 7 | 29% | [8–64] | 43% | [16–75] |
| phosphoryl | 8 | 25% | [7–59] | 25% | [7–59] |
| glyme / oligoether | 7 | 29% | [8–64] | 29% | [8–64] |
| sulfonyl / sulfonate | 8 | 12% | [2–47] | 12% | [2–47] |
| nitrile | 8 | 12% | [2–47] | 12% | [2–47] |

The intervals overlap almost completely and the spread is within sampling noise (six-class
χ² p≈0.56; best-vs-worst Fisher exact p≈0.28), so the ordering is hypothesis-generating
rather than an established ranking, though chemically legible: C–F couplings pin sp³-C–F
regiochemistry, while sulfonyl and nitrile targets turn on oxidation-state ambiguity and
heteroaromatic substitution that ¹H/¹³C shifts underdetermine. It is the recall-bound
failure of [@sec:headline-performance] in a domain-specific guise, and it is where
[@sec:forward-verification-elucidation]'s *forward-verification* recipe plays a role
*analogous* to (not a replacement for) computational-NMR validation.

### Is the model reading the spectra? A formula-only control {#sec:model-reading-spectra-formula}

Every benchmark compound is mined from open-access literature, so a frontier model may have
met it in pretraining, a well-documented hazard for LLM evaluation.[@xu2024contamination]
We reran the identical blind protocol with every spectral channel masked, leaving the
solver the molecular formula and nothing else. A formula does not determine constitution,
so accuracy materially above the floor would indicate recall rather than reasoning.

The arms were not generated together: the *formula-only* arm was fresh (2026-07-28), the
*full-modality* arm archived from June. The bias therefore runs *toward* formula-only —
fresh agents reason harder per compound than the archived batched run — and it still
collapsed to 5%; a confound that works against the finding cannot manufacture it.

**Table {#tab:formula-only-control}. Formula-only control.** Paired on the same 60 compounds as [@sec:forward-verification-elucidation].

| condition | top-1 | recovered (top-3) |
|---|--:|--:|
| formula only | **3/60 (5%)** | 3/60 (5%) |
| formula + IR + ¹H + ¹³C | 14/60 (23%) | 19/60 (32%) |

The outcomes are perfectly nested: eleven compounds are solved with the spectra and not
without, and none the other way round (McNemar exact p=0.001). Removing the spectra
removes the result.

**A second, independent control: publication recency.** The formula-only arm shows the
spectra carry the signal, not whether memorisation contributes to the part they explain; if
recall drove the headline number, accuracy should fall with recency. Across all 194
compounds, source papers spanning 2008–2026, accuracy is flat: 28.6% for the older half
(≤2020, n=112) against 28.0% for the newer (n=82), a point-biserial year–correctness
correlation of r=−0.007, and no monotone trend across buckets
([@fig:fig-contamination]b), the most recent (≥2024, n=25) being highest at 40% [23–59].

![Two contamination controls. (**a**) The solver reaches 3/60 on formula alone against 14/60 with IR + ¹H + ¹³C, nested outcomes: 11 solved only with the spectra, none only without (McNemar exact p=0.001). (**b**) Accuracy against source-paper year (n=194, Wilson 95% CIs) is flat, point-biserial r=−0.007, where pretraining recall predicts a decline.](docs/figures/fig_contamination.png){#fig:fig-contamination}

Newer papers skew larger (median 22 heavy atoms against 20) and size dominates accuracy,
biasing the raw split *against* them ([@sec:headline-performance]); size-adjusted, the
older-minus-newer difference is −5.1 points, 95% CI [−17.2 to +7.0]
(Cochran–Mantel–Haenszel χ²=0.42, p=0.51, continuity-corrected). Its sign is opposite to
what pretraining recall would produce, but the interval comfortably includes zero, so this
bounds any recency effect rather than demonstrating a reversed one, and by the standard that
[@sec:generate-wide-testing-recipe] applies to its own adjacent conditions we do not read it
as directional.

The 5% is not zero, and its three compounds do not all read the same way: one is absent
from PubChem and near-determined by its benzyne-precursor composition, while a catalogued
sulfonamide and a named natural product are as consistent with recognition as with
inference. Either way, formula-level recall
accounts for at most about a fifth of the headline accuracy on this set. The two controls
are independent and agree, but neither is randomised — publication year is observational,
and the formula-only arm cannot distinguish memorisation from inference on a near-determining
formula — so we claim a strong bound rather than exclusion ([@sec:limitations]). Nor can
either control address retrieval on the spectral string itself, which the prompt carries
verbatim from the source article; [@sec:limitations] states that objection and names the
control that would settle it.


### Does the diagnosis hold outside one vendor? A four-vendor replication {#sec:diagnosis-hold-outside-one}

Every number so far comes from one lineage, the external-validity gap [@sec:limitations]
(iii) named as most important. Three terms carry the table below, and
[@sec:forward-verification-elucidation] treats them in full. *Forward-verification*
re-ranks a solver's candidate structures by predicting each one's ¹³C spectrum and matching
it against the observed spectrum. *Generation recall* is the fraction of compounds whose
true structure the solver proposed at all, and *verification precision (conditional on
recall)* is the fraction of those recalled compounds that the re-ranking then puts first.
The *60-compound arm* is the two pre-registered controlled rounds, v3 and v2-control, on
which the original decomposition was run ([@tab:forward-verification-decomposition]'s first
column). One artefact of precision is worth naming in advance: a compound for which the
solver returned a single candidate is scored correct by any re-ranker, so a candidate set
rich in singletons inflates precision by construction, which is why the last column repeats
it over the compounds where more than one candidate existed.

Six non-Claude models solved the same 60 compounds as
[@tab:forward-verification-decomposition]'s first column under the identical blind protocol;
the three whose output was well-formed enough were carried through forward-verification
([@tab:cross-vendor-decomposition-60]).

**Table {#tab:cross-vendor-decomposition-60}. Cross-vendor decomposition on the 60-compound arm.** Recall and precision have
different denominators, so the criterion is the inequality rather than a difference.

| model | generation recall | verification precision \| recall | multi-candidate only |
|---|--:|--:|--:|
| Claude Opus ([@tab:forward-verification-decomposition]) | 19/60 = 32% [21–44] | 16/19 = 84% [62–94] | 10/13 = 77% |
| Grok 4.6 | 32/60 = 53% [41–65] | 20/32 = 62% [45–77] | 20/32 = 62% |
| Gemini 3.7 Flash | 30/60 = 50% [38–62] | 22/30 = 73% [56–86] | 22/30 = 73% |
| GPT-5.6 Sol | 25/60 = 42% [30–54] | 17/25 = 68% [48–83] | 16/24 = 67% |

The inequality holds in every arm ([@fig:fig7-crossvendor]): verification precision
exceeds generation recall for four independent model families. Recall and precision are
measured on the same compounds, so what carries the claim is the paired difference rather than
whether two marginal intervals overlap. Bootstrapping compounds
(`scripts/cross_vendor_gap.py`) resolves three of the four: Claude, Gemini +23.3 points
[+2.9 to +44.3] and GPT-5.6 Sol +26.3 [+4.2 to +49.0] all exclude zero. Grok does not —
+9.2 [−10.7 to +30.3] — and we report its gap as directional.

Two findings sit underneath. Six of Claude's nineteen recall-positive compounds carried one
candidate, so nothing was ranked and any verifier scores them by construction; [@sec:result]
makes that point about the full benchmark, and here it inflates Claude's own precision
alone. The newer models almost always return three candidates (0–1 singletons), and where a
choice existed the four precisions fall in a band that dissolves the apparent Claude
advantage. Verification also looks vendor-independent where generation does not, precision
on multi-candidate sets spanning 62–77% while recall spans 32–53%: the limiting factor is
the generator. Three models beat ours on generation recall, which is the diagnosis working:
recall is the movable factor.

**The candidate budget is not matched, and the correction runs both ways.** Recall above
asks whether the true structure is anywhere in the candidate list, and the lists differ in
length: ours holds 2.20 candidates per compound on this arm against exactly 3.00 for
every comparison model (Composer 2.82). A longer list can only raise recall, so the
comparison is tilted toward the other vendors — the mirror of the singleton effect we
correct on the precision side. At one candidate, the only budget every model met, recall
is 14/60 = 23% for ours against 23/60 = 38% for Grok, 23/60 = 38% for Gemini and 21/60 = 35%
for GPT-5.6 Sol (`scripts/cross_vendor_budget.py`). The ordering survives and three models
still lead ours, but Grok's margin is 15 points. The 21-point figure is not one a
budget-matched comparison supports.

Three weaker models are excluded from the decomposition: Composer 2.5 (20% recall) and
GPT-5.6 Luna (15%) match the given formula only 67% and 76% of the time, and
`nvidia/nemotron-3.5-lightning` managed 2%. [@sec:headline-performance]'s scorer now prints
formula adherence beside recall. A seventh arm, DeepSeek V4 Pro, returned answers for only
18 of 60 compounds before the run ended; the true structure appears for 8 of those, so
its recall is a lower bound and it is excluded from the comparison rather than from the
release — both its solve and verify files are deposited.

![Every model measured on the 60-compound arm. (**a**) Generation recall, each model at the candidate budget it used: 3.00 candidates per compound for all but ours (2.20) and Composer (2.82). That axis therefore favours the models that always returned three. Grey marks models below the formula-adherence floor, whose recall is not a chemistry result. (**b**) The claim itself: verification precision against generation recall, with the diagonal. Every model sits above the line, so verification is better than generation for all four families; hollow marks an incomplete arm, where recall is a lower bound. The four Claude models of [@sec:model-comparison-benchmark-ranks] are deliberately absent: they ran a different 24-compound subset, and putting them here would imply a comparison that was never made.](docs/figures/fig7_crossvendor.png){#fig:fig7-crossvendor}

**Contamination was controlled.** Blindness rested on an instruction: these
runs used cloud agents with repository access to tracked answer keys. Grok re-solved all ten
batches from a clone with the answer files removed: recall 28/60 against 32/60, paired
McNemar p=0.39, formula adherence 97% against 95% of candidates (`scripts/cross_vendor_sweep.py`). The asymmetry is decisive — a
key-reader would solve a *superset*, yet four compounds were solved only in the arm that
had no key, with 24 of 60 solved by both, which is sampling noise rather than copying. And on
constitutionally correct structures whose reference carries assigned stereocentres, which 1D
spectra cannot supply, Grok reproduced 0/3 correct descriptors, Gemini 0/2 and GPT-5.6 Sol
0/2.

Two limits. The models were reached through a coding-assistant harness exposing
reasoning-effort tiers, a decoding control the Claude arm never had ([@sec:methods]), so
these measure a model *as served*, not a bare endpoint — and which tier served each arm
was not recorded. The harness allowlist carries both `gpt-5.6-sol-xhigh` and
`gpt-5.6-sol-high`, and the run did not report its selection, so the arms are not
demonstrably matched to one another either. That bounds what this section can claim, and
the bound falls unevenly. Recall and precision within an arm come from the same run at the
same tier, whichever it was, so the inequality — the result — is internally valid in
every arm. A recall *ranking between named models* is not: it orders models at unknown
effort, and the 15-point margin above should be read as such. The other limit is that the
clean-clone control covers only Grok; Gemini and GPT-5.6 Sol rest on the stereochemistry
argument and the shared protocol.


---

## Forward-verification elucidation {#sec:forward-verification-elucidation}

### Method {#sec:method}

The inverse direction is the model's hard, isomer-blind direction; the forward
direction (structure→spectrum) is its easy, accurate one.[@kamber2026chemist] We close a
training-free generator–verifier loop:

> *generate* candidate structures (inverse) → *forward-predict* each candidate's
> ¹³C spectrum, blind to the observed spectrum → *re-rank* candidates by the
> distance between predicted and observed ¹³C → return the best match.

Candidates are the inverse solver's proposals: 373 deduplicated structures across the 194
targets, forward-predicted in shuffled, anonymised batches, blind to the observed spectrum
and the target's identity. Predicted and observed ¹³C peak sets are then compared by
symmetric chamfer distance ([@fig:fig-mechanism]).

![Forward-verification on a benchmark regioisomer pair: picolinamide and nicotinamide are indistinguishable to the inverse task, but the true isomer's forward-predicted ¹³C spectrum matches the observed one at a chamfer of 0.42 ppm against 1.30 ppm for the alternative ([@sec:method]).](docs/figures/fig_mechanism.png){#fig:fig-mechanism}

Regioisomers have *different* forward-predicted shifts, but the margin is thin: isomeric
candidate pairs for the same target separate by a median 1.21 ppm (quartiles 0.84 and
1.78), and 82% are predicted closer together than the predictor's own ≈2 ppm error —
usually within the noise. The ranking nevertheless recovers the right one 89% of the time
when it is present ([@sec:result]), a real effect on a thin margin, confirmed against a
derangement null, in which every candidate set is re-scored against another compound's
observed spectrum so that none keeps its own, at p=0.001 ([@sec:negative-control]).

Verification precision runs 72–89% rather than 100%: near-degenerate candidates the
predictor cannot resolve are its false positives. The same spacing sets the limits that
[@sec:forward-verification-elucidation] reports separately: the 54.0% derangement chance
floor on multi-candidate compounds ([@sec:negative-control]) and the ceiling neither the HOSE lookup nor the GNN
escapes ([@sec:non-llm-verifiers-deterministic]). Sharper predictors would move them, and better search would not; they exist: ≈1 ppm message-passing ensembles[@williamson2024mpnn], a
DFT-coupled graph network at 0.94 ppm[@han2024dftgnn], a community
benchmark[@xu2025nmrbench] and curated shift sets[@cohen2023delta50] for calibration.

The scheme is an analogy to DP4[@smith2010dp4; @grimblat2015dp4plus] and NMR
crystallography[@pickard2001gipaw; @ashbrook2016nmrcryst], not an equivalence: we forgo
DFT's ≈1–2 ppm accuracy and its calibrated, probabilistic error model for a predictor
that runs in seconds.

### Result {#sec:result}

We ran the verifier over every compound in the benchmark. The first column below is
the 60-compound arm (v3 + v2-control) on which
[@sec:generate-wide-testing-recipe]–[@sec:negative-control] build; the second is the full
benchmark. All 373 candidates were forward-predicted, so nothing here is a lower bound;
the self-ranking row re-derives [@tab:headline-elucidation-performance-irspectra] from
[@sec:well-llms-elucidate-real]'s output.

**Table {#tab:forward-verification-decomposition}. Forward-verification decomposition.** Original arm and full benchmark.

| |  60-compound arm | full benchmark (n=194) |
|:------------------------------------------------|-----------------:|---------------------------:|
| generation recall | 19/60 (32%) | 65/194 (34%) |
| top-1, solver self-ranking | 14/60 (23%) | 55/194 (28%) |
| top-1, forward-verified re-ranking | 16/60 (27%) | 58/194 (30%) |
| | | |
| *conditional on recall* — self-ranking | 14/19 (74%) | 55/65 (85%) |
| *conditional on recall* — forward-verification | 16/19 (84%) | 58/65 (**89%**) |
| …single-candidate compounds within that set | 6/19 | 28/65 |
| | | |
| *multi-candidate only* — self-ranking | 8/13 (62%) | 27/37 (73%) |
| *multi-candidate only* — forward-verification | 10/13 (77%) | 30/37 (81%) |

When the true structure is among the candidates, forward-verification selects it in 58
of 65 cases (89%). Of the 65, 28 had a single candidate, which any ranker scores by
construction, so that pooled figure is not the verifier's margin over chance. On the
37 where a choice existed, forward-verification gets 30/37 (81%) against a 54.0%
derangement floor ([@sec:negative-control]) — +27.1 points; self-ranking
27/37 (73%); we treat the 37 as the denominator that measures verification.

The margin over self-ranking remains small and unresolved: seven compounds gained, four
lost, McNemar exact p=0.55. We do not claim it. The load-bearing claim is that
precision is high in absolute terms while recall binds: top-1 moves only 28%→30%
because the true structure was never proposed for 129 of 194 compounds, which no
re-ranking can repair. The verifier converts recall almost completely on *simple* targets
(50/53, 94%) and is exactly tied with self-ranking on *complex* ones (8/12, 67%).
Elucidation factorises into two near-independent levers: the verifier is already strong
(89%); the generator (34% recall) is the wall ([@fig:fig-wall]).

### Generate-wide: testing the recipe {#sec:generate-wide-testing-recipe}

The decomposition implies a recipe: *generate wide, verify by forward prediction* — a
chemistry analog of self-consistency sampling.[@wang2023selfconsistency] Ten solver agents
proposed up to six regiochemistry-aware candidates per compound, pooled with the
originals and re-ranked as before.

**Table {#tab:generate-wide-vs-original}. Generate-wide vs original.** On the 60-compound arm only, since wide generation was run there; the "original" column is [@tab:forward-verification-decomposition]'s first.

| | original (60-compound arm) | generate-wide |
|---|--:|--:|
| generation recall (true structure among candidates) | 32% | **42%** |
| forward-verified top-1 | 27% | 30% |
| verification precision (conditional on recall) | 84% | 72% |

Wide generation lifts recall +10 points (32%→42%, 19/60→25/60) and top-1 +7 over the
self-ranking baseline (23%→30%, 14/60→18/60), i.e. +3 over the forward-verified top-1
(27%→30%, 16/60→18/60, [@tab:generate-wide-vs-original]), on the same 60 compounds
([@fig:fig3-method]) with no training.

![The forward-verification inference ladder on the 60-compound arm: solver self-ranking → + forward-verification → + generate-wide, at 23% / 27% / 30% top-1. Each rung is a training-free change to inference alone, directional rather than individually resolved at this sample size ([@sec:generate-wide-testing-recipe]).](docs/figures/fig3_method.png){#fig:fig3-method}

**These top-1 differences are directional; at n=60 they are not statistically resolved.** The
stages are not nested: self-ranking to generate-wide gains seven compounds and loses
three, McNemar exact p=0.34 (b=3, c=7). The recall gain is the better-supported
effect: the ladder shows the *mechanism* works and recall is the movable factor; it does not fix
how large the top-1 gain is.

The ladder does not extend. (i) Recall plateaus at 42%, on large polycyclic targets
rather than exotic ones — ≥4 rings in 3.1% of recalled compounds against 38.0% of
missed ones. (ii) Verification precision falls 84%→72% as more near-degenerate
regioisomers enter the pool. This recall/precision tension is the ceiling of the
training-free approach: closing the gap requires sharper verification or 2D-NMR
constraints, not merely more candidates.

### Non-LLM verifiers: a deterministic lookup and a learned model {#sec:non-llm-verifiers-deterministic}

[@sec:generate-wide-testing-recipe] suggests an obvious fix: a non-LLM ¹³C predictor in the
verifier slot. We tested a HOSE-code[@bremser1978hose]-style lookup and a small
message-passing GNN, both trained on the same nmrshiftdb2 dump[@kuhn2015nmrshiftdb2] and
applied to the same [@sec:result] candidate sets, so that only the predictor changes. The
GNN is deliberately modest; sharper purpose-built ¹³C models
exist.[@williamson2024mpnn][@han2024dftgnn][@xu2025nmrbench]

**Table {#tab:verifier-comparison-conditional-recall}. Verifier comparison, conditional on recall.**

| verifier | 60-compound arm (n=19) | full benchmark (n=65) | held-out ¹³C MAE |
|---|--:|--:|--:|
| solver self-ranking | 14/19 (74%) | 55/65 (85%) | — |
| deterministic HOSE *lookup* | 14/19 (74%) | 55/65 (85%) | 3.23 ppm |
| learned GNN (same data) | 16/19 (84%) | **59/65 (91%)** | 1.70 ppm |
| LLM forward-verifier ([@sec:result]) | 16/19 (84%) | 58/65 (89%) | — |

The lookup ties the solver's own score at both sample sizes
([@tab:verifier-comparison-conditional-recall]). Coverage explains it: of the 6,360 candidate
carbons, only 2% match a training environment at r=4 and 71% resolve at r≤2 or the
hybridisation prior, too coarse to separate regioisomers.

The GNN matches and slightly exceeds the LLM verifier, 59/65 against 58/65
([@sfig:verifier]), though not significantly: *suggestive and directional*, consistent with
the lookup's failure being substantially method rather than coverage alone, but not
established. Neither predictor reaches the near-degenerate-regioisomer precision ceiling
([@sec:generate-wide-testing-recipe]/[@sec:negative-control]), where DFT-level accuracy or
orthogonal 2D-NMR constraints remain the genuine fix.

Leakage is slight — no benchmark answer appears in nmrshiftdb2 at all (0/373) — and a
Y-randomisation control (1,000 derangements) places the real result above the 97.5th
percentile of chance (n=19: real 84% vs mean 58.6%, one-sided p<0.05). Like
[@sec:recall-wall-task-intrinsic], the learned verifier is a trained complement, reported
outside the training-free protocol.

### Negative control {#sec:negative-control}

**Permutation negative control (Y-randomisation analog).** A re-ranker exploiting genuine
predicted-vs-observed ¹³C agreement must lose it when the pairing is broken. We re-paired
which observed ¹³C spectrum each candidate set is scored against — a *derangement*, so no
compound keeps its own spectrum — and re-ran the verifier 1,000 times.
Verification precision falls from the true 89.2% (58/65) to a permuted mean of
73.8% (95% range 66.2–81.5%; one-sided empirical p=0.001, two-sided p=0.002). The
verifier acts on real spectral agreement rather than a candidate-list artefact. That floor is high
because 28 of the 65 recall-positive compounds carry a single scorable candidate, and a
compound with nothing to rank is scored correct under *every* pairing. Those compounds
enter the permuted score as guaranteed hits while carrying no verification signal, so the
control was partly measuring the composition of the recall-positive set. On the 37
multi-candidate compounds — the set that [@sec:result] calls the one that measures verification —
the floor falls to 54.0% and the real value is 81.1% (30/37), a margin of +27.1
points rather than +15.4, at the same one-sided p=0.001. We report the restricted figure
as the verifier's margin over chance and the pooled one for continuity with
[@sec:result]'s denominator.

**Confidence calibration (a negative result).** Ranking the 138 multi-candidate compounds by
chamfer margin and answering only the most-confident fraction leaves top-1 flat and
non-monotonic with coverage (22% at full coverage, 24% at 75%, 28% at 50%, 24% at 25%).
Single-candidate compounds, which have no margin, must be excluded; retaining them in an
earlier analysis produced a spurious "improvement". We therefore do not claim the
verifier distance as a calibrated abstention gauge ([@sec:non-llm-verifiers-deterministic]).
This does not contradict the chamfer distance being informative in aggregate
([@sec:result]): the *absolute* distance separates right from wrong answers across
compounds, while the *within-compound margin* between best and second-best does not rank
one compound's confidence against another's. Selecting which questions to answer needs the
second, and only the first is established here.

### Is the recall wall task-intrinsic? A trained-generator probe {#sec:recall-wall-task-intrinsic}

The ceiling above is a property of *training-free LLM elicitation*; whether the ≈42% recall
plateau is intrinsic to 1D-data elucidation is a separate question. We probed it by
substituting a small (≈16M-parameter) ¹H/¹³C→SMILES transformer for the enumerator; its
candidates were pooled with Claude's and re-ranked by the same verifiers.

On the 194-compound benchmark the true structure enters the candidate pool for 54.1% of
compounds, versus 41.8% for scaffold enumeration and 33.5% for Claude alone. Neither of the
first two is an independent elucidator, and the comparison should not be read as one:
enumeration relocates substituents *on a model candidate* (`scripts/enumerate_isomers.py`),
so it is Claude-seeded, and the generator's candidates are pooled with Claude's. All three
rows measure what is added to the LLM's pool rather than what a system reaches on its own. Where
enumeration's near-degenerate regioisomers *collapse* the HOSE verifier (top-1 28.4%→16.0%,
the [@sec:generate-wide-testing-recipe] precision-loss mechanism), the generator's
formula-correct, ¹³C-separable candidates convert: top-1 rises 28.4%→35.1% (McNemar
exact p=0.015; +6.7 points, 95% CI [+2.1 to +11.9]; [@sfig:generator-probe]). The family this
is corrected over is the probe's own three arms — Claude alone, plus enumeration, plus
generator — where it survives Holm (0.029) and Benjamini–Hochberg (0.022). It would not
survive a correction taken over every p-value in the paper, and we name the family rather
than leave the scope to be guessed. With the LLM
forward-verifier on the 60 forward-verify compounds, recall rises 42%→57% (34/60) and
top-1 reaches 47% (28/60), at 82% verification precision (28/34). Those two
figures come from a re-run rather than a reproduction: the earlier pass reported 41% top-1 at 73%
precision but deposited no outputs, so we do not stand behind it, and the re-run lands
above it.

Two controls guard against memorisation: the fine-tuning split removes every benchmark
InChIKey-14 (train∩benchmark = 0, val∩benchmark = 0), with none of the 40 newly-recovered
compounds in either training stage (0/40 in simulated pretraining, 0/40 in fine-tuning);
and the simulated-pretrained model alone recovers 0/248 benchmark structures zero-shot,
rising to 25% only after IRexp fine-tuning. The IRexp data, rather than the architecture,
is the active ingredient, so the recall ceiling is elicitation-specific rather than
task-intrinsic. We
report this as a probe, not part of the headline training-free protocol.

Purpose-trained systems make the point more strongly: NMR-Solver reaches 52.9% top-1 on
experimental literature ¹H/¹³C with the formula supplied[@jin2025nmrsolver], and a
purpose-trained IR transformer 63.8% top-1 on experimental NIST
spectra[@alberts2025benchmarks]. Whatever bounds a
training-free LLM at 28–30%, it is plainly not the task. The public split
`irexp_release/train` does *not* hold out the benchmark (117/200 InChIKey-14 overlap), so
downstream users must de-leak; see *Data availability*.

---

## Discussion {#sec:discussion}

The Claude-family models we tested are reliable scaffold-level elucidators and good
*verifiers* (verification precision 89%); exact top-1 is throttled by generation recall
and by the regiochemical underdetermination intrinsic to 1D NMR. The contribution is a
diagnosis with a bounded, training-free improvement attached, not a method that
solves the task.

The diagnosis held under every perturbation we were able to apply — four Claude models,
a second chemical domain, four verifiers — and reproduces inside a single application
domain ([@sec:domain-case-study-battery]): the binding constraint is *generation recall*,
consistent with the bottleneck being structural rather than incidental.
Whether it holds outside the Claude family is the open question, not a settled one
([@sec:limitations]). We measured the improvement's ceiling rather than projecting past
it: forward-verification moves top-1 from 28% to 30% across the whole benchmark
([@sec:result]), while recall plateaus at 42% ([@sec:generate-wide-testing-recipe]).

This reframes the engineering problem, and not in the direction of "do not train a model".
Purpose-trained systems win on this task today and we report it: NMR-Solver at 52.9% and a
trained IR transformer at 63.8% against a training-free 28–30%, and our own 16M-parameter
generator lifts pooled recall to 54.1% and top-1 to 35.1%
([@sec:recall-wall-task-intrinsic]). The claim is narrower and survives that. What ages out
each model generation is a *particular* trained artefact; what compounds is the open,
experimental data any such artefact needs, and a benchmark honest enough to tell whether it
worked. The probe is the evidence: the same architecture recovers 0/248 structures
without IRexp and 25% with it, so the released data, rather than the architecture, is the active
ingredient. Inference-time scaffolding is the second durable lever for the same reason — it
needs no training, so it rides each new model rather than being replaced by it.

Protocol is a lever of the same order as capability: a number quoted without its
protocol is uninterpretable. We do *not* claim protocol dominates capability — the model
axis spans 0% to 46% top-1 on the fixed 24-compound subset
([@tab:four-model-comparison-fixed]), wider than the 5%→15% protocol effect in
[@sec:methodology-dominates-within-compound], and the two are measured on different
sets. In molecular property prediction, a systematic benchmark reports that learned,
pretrained molecular embeddings rarely outperform classical ECFP fingerprints once
evaluation is controlled[@praski2025embeddings]; we read our forward-verification recipe
([@sec:forward-verification-elucidation]) in that light, and draw the parallel narrowly.

Two findings transfer to practice: solve each problem in bounded, frequently-reset
contexts with tool access (5%→15%, 1/20→3/20, directional at n=20, McNemar p≥0.25,
[@sec:methodology-dominates-within-compound]); and use forward-predicted-vs-observed ¹³C
agreement to *re-rank* candidates rather than to decide whether to trust the winner. Match
distance failed as an absolute confidence gauge in our selective-prediction test
([@sec:negative-control], a reported null result), so it does not support abstention
thresholds.

---

## Limitations {#sec:limitations}

Several limitations of earlier drafts are now resolved; we state what remains plainly.

*Resolved.* **Extraction noise:** an RDKit self-consistency audit finds 57/60 ground
truths spectrally clean, with metrics unchanged on that subset. **Verifier sample
size:** forward-verification now runs over all 194 compounds, so the
recall-conditional claim rests on n=65 rather than n=19 ([@sec:result]). **Verifier
precision:** precision degrades as near-degenerate regioisomers accumulate
([@sec:generate-wide-testing-recipe]), so forward-match distance is a strong *re-ranker*
but a soft *confidence* gauge. **Non-LLM verifiers**
([@sec:non-llm-verifiers-deterministic]): a HOSE-code *lookup* does not beat the LLM
verifier (verification precision 85% against 89% at n=65) and a *learned* GNN reaches 91% — directional
but not statistically resolved at n=65, so it is suggestive that the deterministic
failure was method rather than coverage alone, not a demonstration of it. Beyond all of
them lies the near-degenerate-regiochemistry precision ceiling, where DFT-level accuracy
or 2D-NMR constraints are the genuine fix. **Projection:**
[@sec:generate-wide-testing-recipe] now measures what an earlier draft estimated: top-1
30%, recall 42%, below the estimate it replaces, reported as found rather than adjusted.

*Independence checks.* Scoring is mechanical RDKit rather than LLM-judged, and all
solver/verifier runs were transcript-audited *at generation time* for zero web and zero
ground-truth access. That audit is the one part of the pipeline a reader cannot
re-verify from the release: the committed artefacts are the parsed per-compound
predictions, and the transcripts are not deposited (they are available on request). The
*outcome* of closed-book solving is separately testable: the formula-only control
([@sec:model-reading-spectra-formula]) removes the spectra and accuracy collapses, and a
permutation negative control ([@sec:negative-control]) collapses verification
precision from 89.2% to a chance mean of 73.8% (two-sided p=0.002 on the full
benchmark), as a correctly isolated blind evaluation requires. A second Claude model
(Sonnet) was comparably recall-bound on a 12-compound subset (recall 33% vs Opus 42% on
those compounds), consistent with the recall bound being a property of the task rather
than of one model — but within the Claude family, so it speaks to model-instance
robustness, not cross-vendor generality.

*Remaining.* **(i) Pretraining contamination is bounded; we cannot exclude it.** Every benchmark
compound was mined from open-access literature, so a frontier model may have encountered
it in training. The formula-only control ([@sec:model-reading-spectra-formula]) bounds
how much of the headline number pure recall can explain: masking the spectra drops top-1
from 23% to 5%, perfectly nested, McNemar exact p=0.001. It examines the three
formula-only successes individually rather than collectively — only one (an unlisted
silyl aryl sulfonate) has a genuinely determining composition, while *N*-tosyl-leucine
and [6]-paradol are catalogued compounds for which recall is a live explanation — which
leaves the bound unchanged. A second control finds accuracy flat in source publication
year across all 194 compounds (r=−0.007), the size-adjusted older-versus-newer
difference bounded at −5.1 points, 95% CI [−17.2 to +7.0]. Neither control is randomised:
publication year is observational, and the formula-only arm cannot separate memorisation
from inference on a near-determining formula. Nor is the recency test anchored to a
*known* training cutoff, since the harness does not disclose one ([@sec:methods]); we
test recency as a continuous proxy. A replication restricted to compounds published
after a disclosed cutoff remains open.

The sharper form of this objection is one neither control addresses, and we state it
plainly because a reader is entitled to weigh it. The prompt carries the spectral strings
*exactly as printed in the source article*, down to its own typography, because the sampler
keeps a compound only when the raw ¹H payload can be recovered verbatim from the
open-access full text ([@sec:methods]). Every benchmark compound therefore has its spectrum
present verbatim in a document the model may have read, and that string is a high-entropy
fingerprint of the document. Masking the spectra therefore removes the chemistry and a
retrieval key together: a collapse from 23% to 5% is what reading predicts, and also what
retrieval predicts. Recency cannot separate them either, for the reason just given. The
experiment that would is a spectrum meaning the same thing and reading differently —
shifts perturbed within reporting precision and typography normalised, so the chemistry is
untouched and no verbatim string survives. `scripts/jitter_control.py` builds that set from
the released benchmark; running it is the obvious next control and we have not run it. It
would bound verbatim retrieval only, not recognition from approximate shift patterns.

**(ii) Human audit — prepared but not yet run.** Two things are unvalidated by hand: the
elucidation and forward-prediction outputs, and the *recall* side of dataset extraction
(whether the parser found every IR string in every source paper). Transcription fidelity
of the records we hold is measured and high ([@sec:contents-licensing]); record-level
recall is not, and only reading papers can settle it. Solver and verifier are both LLMs,
so the one validation we cannot perform ourselves is expert-chemist review. We have
therefore built and frozen a blinded, pre-registered audit package at `data/audit/`,
protocol at `docs/EXPERT_AUDIT_PROTOCOL.md`: a difficulty-stratified 30-compound
elucidation panel plus seven ranking-only compounds, with a withheld answer key, testing
what a miss actually is ([@sec:well-llms-elucidate-real]) and whether forward
verification is a trustworthy re-ranker ([@sec:forward-verification-elucidation]). We
have not yet run the panel; until expert results are in, those claims should be read
as machine-validated (RDKit InChIKey) but not yet human-validated.
[@sec:well-llms-elucidate-real] has since narrowed its first question by reporting all
137 analysable misses mechanically (76.6% constitutional isomers, 22.6% scaffold-preserving
positional errors), correcting the impressionistic claim the audit was built to check;
what remains for a chemist is whether a formula-correct, scaffold-wrong candidate is a
*chemically reasonable* reading of the spectra.

**(iii) Single vendor and an underpowered cross-model comparison.** The headline (28.4%
top-1, n=194) is a single frontier model (Claude Opus) on the full benchmark, and the
cross-model evidence ([@sec:model-comparison-benchmark-ranks]) is four Claude-family
models on a shared 24-compound subset. That comparison is underpowered: the ranking is
robust (strictly nested, weakest floored at 0%) but no adjacent gap is established at
n=24, so quantitative claims should be read as holding for the Claude family. The
cross-vendor question is no longer open: [@sec:diagnosis-hold-outside-one] finds
verification precision exceeding generation recall for Grok 4.6, Gemini 3.7 Flash and
GPT-5.6 Sol on the 60-compound arm, as for Claude. What remains is weaker than the
original gap but real. Bootstrapping the paired difference resolves three of the four
arms and leaves Grok's directional at n=60. Those models were reached through a
coding-assistant harness exposing reasoning-effort tiers, a decoding control our own arm
never had — and the tier serving each arm was not recorded, so the arms are not
demonstrably matched to each other either, which bounds the recall *ranking* while leaving
each arm's inequality internally valid ([@sec:diagnosis-hold-outside-one]). The clean-clone
contamination control was run for Grok alone, and the cross-vendor arms cover 60 compounds.

**(iv) Domain-subset scope:** the battery-electrolyte case study
([@sec:domain-case-study-battery]) uses *literature compounds bearing
electrolyte-relevant functional chemistry*, not operando or in-cell decomposition
spectra, so it demonstrates functional-class transfer of the elucidation bottleneck, not
direct assignment of authentic interphase/degradation products, which would require a
dedicated operando set.

**(v) Constitution-only scoring:** correctness is judged on InChIKey connectivity, so a
correct-constitution / wrong-stereochemistry prediction counts as correct. Scoring the
full InChIKey gives 21.1% top-1 ([@sec:benchmark-design-irspectra-bench]), 7.3 points
lower, so the headline should be read as an upper bound on full-stereochemistry
accuracy. We keep constitution because 1D NMR/IR rarely determines absolute
configuration — the 10.3% (20/194) of targets with a defined stereocentre would be
penalised for information the prompt never carried — but a stereochemistry-sensitive
benchmark would need 2D/chiroptical data.

**(vi) Single-sample scoring:** each headline compound is scored from one solver
prediction set, so reported top-1/recall carry no run-to-run (LLM-sampling) variance
estimate; the bootstrap CIs reflect compound sampling only.
[@sec:generate-wide-testing-recipe] pools ten independent generation passes (recall
32%→42%), indicating generator stochasticity that single-pass scoring understates.

**(vii) Chemical-space coverage:** the benchmark is drawn from open-access organic
methodology and total-synthesis literature; it is not representative of
organometallic/coordination compounds, large biomolecules (peptides, oligonucleotides,
oligosaccharides), or stereochemistry-heavy targets, and our results should not be
extrapolated to them.

---

## Methods {#sec:methods}

**Mining and resolution.** PMC-OA full text was fetched from `s3://pmc-oa-opendata`,
parsed deterministically, and resolved with OPSIN, RDKit and SELFIES, with an optional
cached PubChem fallback.

**Benchmark and agents.** Problems were sampled from `irexp_resolved`, stratified by
RDKit ring analysis to half the round per stratum, and de-duplicated across rounds by
InChIKey. A compound was admitted only if its raw ¹H payload — multiplicities and *J*
values as printed — could be re-extracted verbatim from the PMC-OA full text of its source
article (`benchmark_v2.raw_1h_for`), which is what puts genuine coupling information in the
prompt and, unavoidably, puts the source article's exact string there too
([@sec:limitations]). The battery-electrolyte
subset ([@sec:domain-case-study-battery]) was drawn from the same corpus by SMARTS filters
for six electrolyte functional classes (carbonate, sulfonyl/sulfonate, nitrile, sp³-C–F,
phosphoryl, glyme/oligoether), balanced to eight compounds per class (48 curated; 46
scored after two yielded no parseable candidate) and excluding every compound used
elsewhere. It was *J*-enriched — the raw ¹H string keeps its multiplicities and *J* values
— and spectrally validated, as in the main rounds. Solver and
forward-prediction agents were independent Claude-Opus sub-agents under the same
subscription, instructed closed-book and audited by automated transcript search for zero
web/answer access. A prediction was scored correct on RDKit InChIKey-connectivity match;
similarity used Morgan(2, 2048) Tanimoto, and forward-verification a symmetric chamfer
distance over ¹³C peak sets. The core protocol trains no model and uses no paid API; the
[@sec:recall-wall-task-intrinsic] generator and the [@sec:non-llm-verifiers-deterministic]
learned ¹³C verifier are the only two trained components, reported as complements and
fenced from the headline results.

*Models and versions.* All experiments used Anthropic Claude models via the consumer
subscription (claude.ai). The [@sec:model-comparison-benchmark-ranks] comparison spanned,
in capability order, Claude Haiku, Claude Sonnet, Claude Opus and Claude Fable 5; the
headline benchmark ([@sec:headline-performance]) and forward-verification
([@sec:forward-verification-elucidation]) used Claude Opus. `docs/MODELS.md` records, per
experiment, the model, data directory, collection date, harness and tool access, and
scoring code path, across three dated windows:

- **2026-06-09 to 2026-06-11** (UTC) — every candidate structure behind the headline
  results: [@sec:headline-performance],
  [@sec:methodology-dominates-within-compound]–[@sec:domain-case-study-battery], and the
  candidate pools all of [@sec:forward-verification-elucidation] re-ranks.
- **2026-07-28** — the formula-only contamination control
  ([@sec:model-reading-spectra-formula]), re-solving the same 60 compounds with spectra
  masked and generating its own candidates; it touches [@tab:formula-only-control] alone.
- **2026-08-07** — three collections forward-predicting ¹³C for candidates the June run
  had already produced (the [@sec:result] extension to all 194 compounds, the
  [@sec:generate-wide-testing-recipe] coverage-gap closure, and the
  [@sec:recall-wall-task-intrinsic] re-run); none introduced a new candidate structure,
  and no recall number in the paper changes.

One *verified* number does: the [@sec:recall-wall-task-intrinsic] re-run supersedes a
top-1 whose original forward-prediction outputs were never deposited and are lost,
disagreeing with the figure it replaces (47% against 41%);
[@sec:recall-wall-task-intrinsic] reports it as a re-run rather than a reproduction.

**No model snapshot can be reported.** The consumer harness exposes no checkpoint
identifier and records nothing about which build served a given request. It exposes no
decoding parameters either, and none were set or recorded. `Claude Opus 4.8` is evidenced
only for the 2026-06-09 pilot, so a mid-window build change cannot be excluded, and we
do not claim the same build served the main round two days later. Re-running reproduces
the protocol distributionally rather than exactly, and exact agreement is not offered as a
target. Fixed are the dated collection windows, the frozen per-compound outputs, and
mechanical scorers that regenerate every number from them: exact reproducibility of
scoring and analysis, not of inference (`docs/MODELS.md` [@sec:discussion]).

**Reproducibility.** Every round is frozen: questions, ground-truth answers, per-agent
raw outputs, predictions and scorer outputs are released; the sampler, scorer and
forward-verification harness are scripted end-to-end.

---

## Supporting Information figures

These are supplied as a separate Electronic Supplementary Information document
(`docs/paper_esi.pdf`, built by `scripts/build_pdf.py`), as RSC requires; they are listed
here for reference.

- **[@sfig:overview]** (`docs/figures/fig0_overview.png`) — study design: open multimodal data
  (IRexp) → blind, complexity-stratified benchmark → decoupled blind solving →
  forward-verification re-ranking; training-free core pipeline.
- **[@sfig:dataset]** (`docs/figures/fig4_dataset.png`) — IRexp composition: IR records →
  NMR-paired → structure-linked → full IR + ¹H + ¹³C + structure quadruples.
- **[@sfig:size]** (`docs/figures/fig2_size.png`) — accuracy vs molecular size (heavy-atom
  bucket); the monotonic 60%→7% top-1 gradient.
- **[@sfig:electrolyte]** (`docs/figures/fig6_electrolyte.png`) — top-1 and recovered accuracy on
  IRSpectra-Bench-Electrolyte by battery-electrolyte chemical class (n=46): sp³-C–F
  easiest (50%), sulfonyl and nitrile hardest (12%); overall 26%/28%.
- **[@sfig:generator-probe]** (`docs/figures/fig_generator_probe.png`) — trained-generator probe ([@sec:recall-wall-task-intrinsic];
  a complement, not part of the training-free protocol): generation recall and
  deterministic-HOSE top-1 on the 194-compound benchmark for Claude / + scaffold
  enumeration / + trained generator. Enumeration's near-degenerate isomers collapse the
  verifier (28.4→16.0%) while the generator's formula-correct candidates convert
  (28.4→35.1%).
- **[@sfig:verifier]** (`docs/figures/fig_verifier.png`) — learned-verifier probe ([@sec:non-llm-verifiers-deterministic]; a
  complement, not part of the training-free protocol). (A) Conditional-on-recall top-1
  (n=65, whole benchmark) for the four verifiers: a GNN trained on the same nmrshiftdb2
  data as the HOSE lookup reaches the LLM verifier's level (91% vs 89%) where the lookup
  (85%) does not move off the solver's own ranking. (B) Why: held-out
  ¹³C MAE — the learned model is ≈2× sharper (1.70 vs 3.23 ppm).

---

## Author contributions

**I.Y.:** conceptualization, methodology,
software, formal analysis, investigation, data curation, visualization, writing —
original draft. **R.S.:** methodology, software, formal analysis, investigation,
validation (trained-generator and learned-verifier probes, [@sec:non-llm-verifiers-deterministic] and [@sec:recall-wall-task-intrinsic]), writing —
review and editing. **R.A.V.-H.:** conceptualization, methodology, supervision,
writing — review and editing.

## Conflicts of interest

There are no conflicts to declare.

## Data availability

[@tab:artefacts] lists every released component and the script that regenerates it, all of
them in the project repository. The archival deposit — a complete frozen
snapshot of dataset, benchmark, answer keys, predictions, scripts, figure regeneration and
the expert-audit package — will carry DOI [TODO: 10.5281/zenodo.XXXXXXX — mint on
submission]; GitHub is the development mirror and the Zenodo record the citable version.

**Table {#tab:artefacts}. Released artefacts and what regenerates each one.**

| component | data | regenerated by |
|:--------------------------------|:-------------------------------|:----------------------------|
| IRexp and its structure-complete split | `data/irexp/`, `data/irexp_resolved/` | `spectro_scraper/` (mining pipeline) |
| benchmark rounds and the within-compound control | `data/benchmark*/` | `scripts/benchmark_v2.py` |
| ground-truth integrity audit | `data/benchmark*/clean_qids.json` | `scripts/validate_benchmark.py` |
| headline accuracy ([@tab:headline-elucidation-performance-irspectra]) | — | `scripts/score_main.py` |
| battery-electrolyte subset ([@sec:domain-case-study-battery]) | `data/benchmark_electrolyte/` | `scripts/build_electrolyte_bench.py`, `scripts/score_electrolyte.py` |
| formula-only contamination control ([@sec:model-reading-spectra-formula]) | `data/modality/` | `scripts/modality_ablation.py` |
| publication-recency control ([@sec:model-reading-spectra-formula]) | `data/audit/recency_control.json` | `scripts/contamination_recency.py` |
| forward-verification, original arm ([@sec:result]) | `data/fverify/` | `scripts/forward_verify.py` |
| …extended to all 194 compounds | `data/fverify_main/` | `scripts/forward_verify_main.py`, `scripts/forward_verify_all.py` |
| generate-wide arm ([@sec:generate-wide-testing-recipe]) | `data/gw/`, `data/fverify2/` | `scripts/score_generate_wide.py`, `scripts/ladder_significance.py` |
| …its coverage gap, closed | `data/fverify_gw/` | `scripts/forward_verify_gw.py` |
| non-LLM verifier comparison ([@tab:verifier-comparison-conditional-recall]) | `data/fverify/hose_results.txt`, `data/fverify/verifier_table_results.txt` | `scripts/hose_predict.py` (incl. `coverage`), `scripts/verifier_table.py`, `scripts/verifier_leakage.py` |
| negative control and selective prediction ([@sec:negative-control]) | — | `scripts/verifier_diagnostics.py` |
| what a miss is, and isomer separability ([@sec:headline-performance], [@sec:method]) | — | `scripts/analyze_misses.py`, `scripts/isomer_separability.py` |
| difficulty-threshold sensitivity ([@sec:benchmark-design-irspectra-bench]) | — | `scripts/difficulty_sensitivity.py` |
| licence-pool split ([@sec:motivation]) | — | `scripts/split_license_pools.py` |
| recall headroom and scaffold enumeration | — | `scripts/analyze_recall_headroom.py`, `scripts/enumerate_isomers.py`, `scripts/closing_the_gap.py` |
| blinded expert-audit package ([@sec:limitations]) | `data/audit/` | `scripts/make_audit_sample.py` |
| corpus reweighting ([@sec:benchmark-design-irspectra-bench]) | — | `scripts/corpus_reweight.py` |
| cross-vendor recall at matched budget, and the paired gap ([@sec:diagnosis-hold-outside-one]) | `data/cross_vendor/` | `scripts/cross_vendor_budget.py`, `scripts/cross_vendor_gap.py` |
| ring-system names in peak assignments ([@sec:benchmark-design-irspectra-bench]) | — | `scripts/prompt_leakage.py` |
| paraphrase-invariant benchmark, for the control not yet run ([@sec:limitations]) | — (regenerated, not deposited) | `scripts/jitter_control.py` |
| manuscript integrity gates | — | `scripts/check_manuscript.py`, `scripts/verify_statistics.py`, `scripts/check_compression.py`, `scripts/check_layout.py` |

**Trained complements**, both fenced from the training-free protocol. The [@sec:recall-wall-task-intrinsic]
generator ships as a self-contained bundle at `contrib/generator_probe/` — candidates,
the de-leaked split with its InChIKey-14 manifest, the verification scripts
(`scripts/closing_the_gap_gen.py`, `scripts/forward_verify_gen.py`,
`scripts/verify_leakage_exact40.py`) and the blind forward-prediction outputs behind its
verified top-1 (`data/fverify_gen/`), so its scorer runs with no missing predictions.
The [@sec:non-llm-verifiers-deterministic] learned verifier ships `scripts/gnn_predict.py` (extract / train / score /
control), the trained model `data/nmrshiftdb/gnn_c13.pt`, per-compound results and both
leakage checks (`data/fverify/gnn_results.txt`), and the write-up
`docs/VERIFIER_PROBE.md`. Model checkpoints are deposited on Zenodo. Both trained
predictors of [@sec:non-llm-verifiers-deterministic] need the nmrshiftdb2 dump, which we cannot redistribute; the README
gives the one-line fetch.

Companion technical notes: `docs/BENCHMARK.md`, `docs/FORWARD_VERIFY.md`,
`docs/MODALITY_ABLATION.md`, `docs/EXPERT_AUDIT_PROTOCOL.md`, `docs/MODELS.md`.

**Two cautions for re-users.** The public `irexp_release/train` split does not hold
out IRSpectra-Bench — it overlaps by 117/200 InChIKey-14 — so de-leak with
`contrib/generator_probe/build_exp_manifest.py` before training anything that will be
evaluated on the benchmark. And the held-out answer keys `data/audit/key.jsonl` and
`data/modality/key.json` are deposited but flagged *withhold from blinded reviewers*.

### Licensing and attribution

IRexp is derived from two open-access source pools and redistributed under terms
compatible with each (see `data/NOTICE`). **(a) Redistribution:** we release only
*extracted numeric data* — IR band lists, ¹H/¹³C shift lists, and resolved structures
(SMILES/SELFIES/InChIKey) — plus each record's source DOI/accession, not source full
text, figures, or PDFs. **(b) Two separable pools:** 119,345 records derive from the PMC
Open-Access Subset (CC-BY-4.0) and 1,888 from the Chemotion RADAR4Chem FT-IR deposit
(CC-BY-SA-4.0). The two are separable losslessly by `source_doi` — Chemotion records
carry the `10.22000` prefix — and `scripts/split_license_pools.py` materialises them as
two files with each record stamped `license`, so users may take the CC-BY pool alone;
any combined or Chemotion-derived release carries CC-BY-SA-4.0 to honour the ShareAlike
term. Code is released under the MIT License. **(c) Attribution:** re-users must cite
this dataset (Zenodo DOI above) and attribute the original publications via each record's
`source_doi`.

## Acknowledgements

*(To be completed before submission: funding sources, compute/infrastructure, and any
individual acknowledgements. — AUTHORS)*

### Use of AI tools

This work studies a large language model, and LLMs were also used as instruments and as
writing aids; we state both roles explicitly. **As an object of study:** all reported
elucidation, forward-prediction and verification results were produced by Claude models
invoked under the protocol of [@sec:benchmark-design-irspectra-bench] and [@sec:methods] — these are the measurements the paper reports,
not assistance in producing it. **As a writing aid:** the authors used an LLM-based
coding assistant for figure generation, analysis scripting, manuscript copy-editing, and
for the internal review pass that produced several of the corrections recorded in the
repository history. No text, number, figure or citation in this manuscript was accepted
without author verification against the released data and code; every quantitative claim
regenerates from the scripts in `scripts/`. The authors take full responsibility for the
content.

## References

<!-- Generated by pandoc --citeproc from docs/references.bib using the Royal Society of
     Chemistry CSL style (docs/rsc.csl). Do not hand-number: cite with the bracketed
     at-key syntax in the text and the list below is built automatically, in citation
     order. NOTE: do not write a literal example of that syntax here -- pandoc parses
     citations inside HTML comments and it becomes a phantom empty reference. -->

::: {#refs}
:::
