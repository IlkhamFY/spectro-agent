# IRexp and IRSpectra-Bench: redistributable experimental IR band lists, a blind peak-list benchmark, and a recall-bound diagnosis of LLM elucidation

**Ilkham Yabbarov**^1^ *(corresponding author: yabbaroi@mcmaster.ca)*, **Rudra Sondhi**^1^, **Rodrigo A. Vargas-Hernández**^2,1,3^

^1^ Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario L8S 4L8, Canada.
^2^ Brockhouse Institute for Materials Research, McMaster University, Hamilton, Ontario L8S 4L8, Canada.
^3^ School of Computational Science and Engineering, McMaster University, Hamilton, Ontario L8S 4L8, Canada.

<!-- AUTHORS — name forms and ORCID iDs below are taken from each author's own published
     bylines and ORCID record, not guessed. Many journals link iDs through the submission
     system rather than printing them in the manuscript body, so they are recorded here.
       I. Yabbarov            ORCID: [TODO: 0000-0000-0000-0000]
                              (corresponding; yabbaroi@mcmaster.ca)
       R. Sondhi              ORCID: 0009-0003-3034-7347
                              verified: https://orcid.org/0009-0003-3034-7347
                              name form identical across every byline he has;
                              no email found in any public source — ask him
       R. A. Vargas-Hernández ORCID: 0000-0002-5559-6521
                              verified: https://orcid.org/0000-0002-5559-6521
                              email vargashr@mcmaster.ca (corresponding-author
                              footnote, arXiv:2509.13504)
                              accented surname with middle initial is the form on every
                              2025–26 byline;
                              he also carries two further McMaster affiliations (School of
                              Computational Science and Engineering; Brockhouse Institute
                              for Materials Research) — ask whether he wants them listed
     `python scripts/check_manuscript.py` lists every outstanding item of this kind. -->

## Abstract

We release *IRexp* and *IRSpectra-Bench* as chemical-information resources: the largest
openly redistributable collection of experimental infrared *band lists* (121,233 records;
43,060 structure-linked; 33,201 full IR + ¹H + ¹³C + structure quadruples), a blind
mechanically scored peak-list benchmark of 194 compounds, a fixed RDKit InChIKey-connectivity
scoring contract, and decomposable generation-recall / verification-precision metrics others
can report. On IRSpectra-Bench, given the molecular formula and peak lists exactly as
reported in open-access papers, a frontier large language model recovers the correct
constitution for 28% (top-1; 95% CI 22–35), or 15% once reweighted to the corpus composition
— far below the near-100% implied by curated demonstrations. The bottleneck is candidate
proposal, not verification: the true structure enters the pool for only 34% of compounds,
and where it does, training-free forward-verification selects it 89% of the time (58/65; 81%
on the 37 compounds where a ranker had a choice). Recovered from published top-*k* figures,
the same split carries 68–83% of the accuracy collapse when three systems move from curated
or simulated data to real heterogeneous spectra. Generating wider lifts recall 32% → 42% and
top-1 23% → 30% on 60 compounds; verification itself moves whole-benchmark top-1 only
28% → 30%. Masking the spectra drops top-1 from 23% to 5%, and Grok 4.6, Gemini 3.7 Flash
and GPT-5.6 Sol all verify better than they generate. Frozen predictions, scorers and code
are released for mechanical re-evaluation.

## Introduction {#sec:introduction}

Open experimental infrared data usable for machine learning remain a chemical-information
bottleneck. View-only archives such as AIST SDBS[@sdbs] hold more structure-linked *spectra*
than any redistributable corpus, yet forbid bulk reuse; most public elucidation suites train
or evaluate on simulated or single-instrument spectra. Determining structure from spectra is
nonetheless central to synthetic and analytical chemistry. Machine learning uses
encoder–decoder models on paired corpora; *Spectro*, for one, learns ¹H/¹³C/IR → SELFIES
from 6,833 molecules[@chacko2024spectro]. General-purpose LLMs are now reported
off-the-shelf: a non-peer-reviewed 2026 industrial white paper found Claude Opus matching or
beating commercial NMR-prediction software forward (structure → spectrum, ±0.08 ppm ¹H) and
"recovering all eight simpler structures on every attempt" in the
inverse[@kamber2026chemist]. We treat those numbers as a claim to test, not an established
baseline.

That evaluation is narrow: 15 inverse problems on curated single-ring or two-fragment
molecules, NMR only, seven given the *starting-material structure* as a hint, and "recovery"
scored leniently over three runs and three ranked candidates. The chemist's question —
*take an arbitrary experimental spectrum from a paper and recover the structure* — remains
open. It needs open experimental data at scale, a blind benchmark with a fixed molecular-
representation scoring contract, and honest accounting of which stage of elucidation binds.

We provide all three as reusable chemical-information objects. *IRexp*
([@sec:irexp-dataset]) is, to our knowledge, the largest openly *redistributable* collection
of experimental IR *band lists* (121,233 records; 43,060 structure-linked; 33,201 IR + ¹H +
¹³C + structure); SDBS remains larger for view-only structure-linked spectra but cannot be
redistributed ([@sec:motivation]). *IRSpectra-Bench*
([@sec:benchmark-design-irspectra-bench]) is the blind, mechanically scored peak-list
benchmark built from it — 194 compounds, complexity-stratified, multimodal IR + ¹H + ¹³C —
with RDKit InChIKey-connectivity scoring and decomposable generation-recall /
verification-precision metrics. Concurrent 2026 suites bound related tasks (MolQuest scores
530 post-2025 compounds by exact canonical SMILES[@han2026molquest]; SpecX[@xiang2026specx];
NMRGym[@fang2026nmrgym]); ours is an openly redistributable suite on literature-reported peak
lists with a stage decomposition measured on Claude, replicated across three other model
families ([@sec:diagnosis-hold-outside-one]), with a within-compound solver-methodology
control ([@sec:well-llms-elucidate-real]). Ground truth is literature structures resolved
deterministically (OPSIN/RDKit) and checked mechanically (560/560 bands on a seed-fixed
sample, [@sec:contents-licensing]; expert-chemist review of elucidation outputs is formally
deferred, [@sec:limitations]); no LLM curates labels or scores predictions. Priessner *et
al.*[@priessner2026reasoning] already note that re-ranking cannot recover a missing
candidate; we supply the missing measurement infrastructure at scale.

Forward-verification elucidation ([@sec:forward-verification-elucidation]) turns the
model's *strong* direction (forward prediction) against its *weak* one (inverse
regiochemistry); the loop is prior art ([@sec:related-work]), the decomposition ours, run
training-free on every compound. The finding is sharp asymmetry: given a candidate set
containing it, the model *verifies* the correct structure 89% of the time yet *proposes* it
for only 34%, so generation binds the result ([@fig:fig-wall]). Gain is bounded (top-1
28% → 30% on n=194; 23% → 30% on the 60-compound arm where wide generation was also tested)
and, by our own measurements, cannot exceed a recall/precision ceiling without sharper
verification or 2D-NMR data.

**Contribution.** We release IRexp and IRSpectra-Bench — redistributable experimental band
lists, a fixed blind peak-list protocol, and decomposable recall/verification metrics others
can report on a shared InChIKey scorer — measured on every compound (34% proposed; 89%
selected once proposed), with a four-vendor replication of that split. The paper fills an
infrastructure and accounting gap in cheminformatics: it diagnoses where elucidation binds;
it does not claim a solved elucidator.

![Diagnosis on IRSpectra-Bench (n=194): generation recall, not verification, is the bottleneck. Where the true structure is never proposed, no ranker can recover it; where it is proposed, verification usually selects it. End-to-end top-1 is the product of those two rates, which have different denominators and are not differenced.](docs/figures/fig_wall.png){#fig:fig-wall}

Solver and verifier ([@sfig:overview]) are LLM agents on a consumer subscription, with no
fine-tuning and no API spend. Inference is not exactly reproducible — no pinned snapshot,
temperature or seed ([@sec:methods]) — but scoring is: predictions, ground truth and scorers
are released, and every training-free number regenerates from them. The HOSE lookup, GNN
([@sec:non-llm-verifiers-deterministic]) and trained generator ([@sec:recall-wall-task-intrinsic])
are fenced complements.

### Related work {#sec:related-work}

Four camps surround this work; IRexp/IRSpectra-Bench occupy a distinct wedge —
*redistributable experimental IR band lists*, a *blind literature peak-list protocol*, and
*stage-decomposed metrics* — rather than a claim to state-of-the-art agent accuracy.

**Trained spectra → structure models.** Sequence and graph decoders on paired corpora —
*Spectro*[@chacko2024spectro], multitask 1D-NMR models[@hu2024multitask],
NMRTrans/NMRSpec[@yang2026nmrtrans], *NMIRacle* (IR + ¹H + ¹³C)[@ottomano2025nmiracle],
Alberts IR transformers[@alberts2024ir; @alberts2025benchmarks] — are accurate
in-distribution but retrained per modality and typically scored end-to-end. IRexp
([@sec:contents-licensing]) complements NMRSpec with redistributable IR band lists; neither
corpus alone is multimodal. Upstream IR work from our group
(*vIR-OLO*[@garcilazocruz2026virolo], *j-IR-vis*[@sondhi2025jirvis]) identifies functional
groups but does not generate candidate structures. We do not score Spectro, NMIRacle or CASE
on IRSpectra-Bench ([@sec:limitations]); the resource is designed so those baselines can be
added under one scorer.

**LLM agents and puzzle benches.** LLM agents already plan syntheses
(ChemCrow[@mbran2024chemcrow], Coscientist[@boiko2023coscientist]) and call elucidation
routines; we measure what one returns. Off-the-shelf and multimodal LLMs[@kamber2026chemist;
@su2025spectrallm; @shen2025specmol; @zhuang2025treesearch], puzzle benchmarks
(MolPuzzle[@guo2024molpuzzle]), and agentic IR interpreters (IR-Agent[@noh2025iragent];
Priessner *et al.*[@priessner2026reasoning]) improve *how* a model reads spectra or re-ranks
a fixed pool. Cross-paper numbers swing with harness: GPT-4o scores 1.4% on
MolPuzzle[@guo2024molpuzzle], 27.8% with chain-of-thought, 57.8% with
tree-search[@zhuang2025treesearch]. We fix one pre-registered RDKit-InChIKey protocol with
bootstrap CIs and ask which stage binds once the spectra have been read.

**Contamination-aware and heterogeneous-data benches.** Most prior suites use simulated or
single-instrument spectra[@chacko2024spectro; @ottomano2025nmiracle; @alberts2024ir;
@alberts2025benchmarks]. IRSpectra-Bench uses literature-reported peak lists across
thousands of laboratories and reports formula-only and recency controls
([@sec:model-reading-spectra-formula]). Espejo Morales *et al.* frame agentic search on raw
instrument files: 80.9% on education spectra, 20.6% on 34 industrial
samples[@espejo2026agentic] — they ask which architecture; we ask which stage binds on
published reports ([@sec:limitations]).

**Forward verification, CASE and prior loops.** Matching predicted to observed shifts —
DP4[@smith2010dp4; @grimblat2015dp4plus], NMR crystallography[@pickard2001gipaw;
@ashbrook2016nmrcryst], CASE[@elyashberg2012case; @elyashberg2015case] — is easier than
inverse generation. CASE enumerators have exhaustive recall by construction; the LLM
literature almost never reports whether the true structure was proposed at all
([@sec:literature-decomposition]). *NMR-Solver*[@jin2025nmrsolver] runs the same
generate-and-verify loop without an LLM (52.9% top-1 on literature ¹H/¹³C, formula
supplied; 31.6% with stereochemistry). We decompose error rather than beat that score.
*NMRAgent*[@fang2026nmragent] is a complementary best-effort system. Kliuev *et al.* place
the best of six LLMs at 24% on 105 peak lists[@kliuev2026canai]. Priessner *et al.* already
state that re-ranking cannot recover a missing candidate[@priessner2026reasoning]. We add
measurement at scale: the split on 194 compounds across four model families and four
verifiers, recovered from published top-*k* figures ([@sec:literature-decomposition]).

## The IRexp dataset {#sec:irexp-dataset}

### Motivation {#sec:motivation}

An IRexp record is a *band list* — peak positions in cm⁻¹ transcribed by an author into
a paper's text — with co-reported ¹H/¹³C shift lists and, where resolvable, the 2D
structure. IRexp contains no absorbance traces. That is the published form a language
model consumes, but a different object from a digitised spectrum, and the two should
not be counted against one another.

Among *digitised spectra*, free downloads run to the NIST WebBook[@nist_webbook] (≈16k)
and the Chemotion ELN deposit[@chemotion2024] (≈2k). AIST SDBS[@sdbs] is larger (≈54k
FT-IR, all structure-linked) but *view-only* (50 spectra/day, no bulk export), so IRexp
does not compete there: SDBS alone holds more structure-linked spectra than IRexp holds
structure-linked band lists. Among text-derived *band lists* IRexp is the largest
*openly redistributable* collection by record count — deliberately scoped to that object
type.

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

[@tab:irexp-dataset-contents-provenance] summarises contents and provenance.

**Table {#tab:irexp-dataset-contents-provenance}. IRexp dataset contents and provenance.**

| field | value |
|---|--:|
| experimental IR band-list records | **121,233** |
| …co-reporting ¹H and/or ¹³C NMR | 87,075 (72%) |
| …with a resolved 2D structure | 43,060 (35.5%) |
| …of these, with ¹H and/or ¹³C NMR | 40,702 |
| …of these, with both ¹H and ¹³C (full quadruples) | 33,201 |
| | |
| *by provenance:* author-transcribed from PMC-OA text (mixed CC terms; see Licensing) | 119,345 |
| *by provenance:* peak-picked from Chemotion ELN deposits (CC-BY-SA) | 1,888 |

The pools differ: PMC records are author-transcribed (median 9 bands), Chemotion records
peak-picked from deposited spectra (median 39); users training on band density should
treat them apart. `scripts/split_license_pools.py` reports provenance (`source_doi`) and
stamped `license_pool` splits. **Licensing.** A Europe PMC join over all 15,416 unique
IRexp PMCIDs stamps every record (`scripts/join_pmc_licences.py`): **87,617** commercial
(CC-BY/CC0), **20,938** CC-BY-NC*, **1,897** ShareAlike (Chemotion + rare PMC SA), and
**10,781** empty/unknown (excluded from the commercial Zenodo pool). Chemotion records
are CC-BY-SA-4.0. Do not treat the undivided PMC provenance slice as a single CC-BY-4.0
redistribution — use `license_pool == "commercial"` (or `data/irexp/licence_pools/`).

**Extraction fidelity is measured.** On a seed-fixed random sample of 60
PMC-sourced records (`scripts/audit_extraction.py --n 60 --seed 0`) we re-fetched each
article and checked every recorded wavenumber against its text: 560/560 bands and 60/60
records were confirmed (Wilson 95% CI 99.3–100% and 94–100%). This bounds *transcription*
error — hallucinated, mis-parsed or unit-mangled values — below 1% of bands. It does
not measure whether the parser found every IR string in every paper — a recall question
requiring human reading; that extraction-recall audit is formally deferred
([@sec:limitations]).

`irexp_resolved` (43,060 records, 100% structure-linked) is the benchmark-ready split,
≈6× the 6,833-molecule set used to train Spectro[@chacko2024spectro] ([@sfig:dataset]).

**Reuse.** Each record carries `source_doi`, stamped `license` / `license_pool`, and,
where resolved, molecular representations (canonical SMILES, InChIKey, SELFIES).
Fine-tuning against IRSpectra-Bench should use `data/train_no_bench.jsonl.gz` (or rebuild
with `contrib/generator_probe/build_exp_manifest.py`) so benchmark InChIKeys are withheld.
Commercial redistribution should use the commercial pool; Chemotion/SA rows remain
CC-BY-SA-4.0. Cite the Zenodo deposit once minted and attribute sources via each record’s
`source_doi` (see Data availability; Hugging Face mirror `ilkhamfy/IRexp`).

## Benchmark design (IRSpectra-Bench) {#sec:benchmark-design-irspectra-bench}

From `irexp_resolved` we draw *IRSpectra-Bench*, 194 blind elucidation problems, each
giving the *molecular formula* (as from HRMS), the *IR band list* and the *¹H and ¹³C
shift lists*; no name, SMILES or scaffold hint. In 10 of the 194 the authors' peak
assignments name a ring system (`2CH2·pyrrolidine`, `pyridazinone H5`). Those compounds
are solved 1/10 against 54/184 (29.3%) for the rest (`scripts/prompt_leakage.py`), so
the annotation does not carry the headline; we keep them rather than drop them.
Main-round ground truths are spectrally validated by an automated RDKit check (¹³C peaks
vs symmetry-unique carbons, formula match, SELFIES round-trip) excluding merged or
incomplete spectra — 6/140, leaving 134; `scripts/validate_benchmark.py` applies the same
filter to all three rounds, regenerating every `clean_qids.json` from the released
questions and answers.

The filter does not gate on ¹H. In 13 of the 194 retained records the reported ¹H
integral exceeds the reference structure's hydrogen count — residual solvent, water,
exchangeable protons, or a rotamer mixture — printed as a diagnostic, not excluded; the
cohort was fixed in advance, and re-filtering post hoc on a criterion chosen after seeing
results is a degree of freedom a benchmark should not take. We report the sensitivity
instead: dropping all 13 moves the headline from 28.4% to 29.3% (53/181), +0.9 points,
leaving every conclusion unchanged. The controlled rounds' 60 compounds
are fixed, pre-registered sets, audited the same way but reported rather than filtered
(57/60 pass; [@sec:limitations]).

**Difficulty is declared in advance, as a property of the compound.** By RDKit ring
analysis a compound is *simple* iff it has at most two rings, no fused/spiro/bridgehead
system and ≤22 heavy atoms; all others are *complex* (98 simple / 96 complex). The
threshold is not load-bearing: sweeping it from 18 to 26 leaves the simple-minus-complex
top-1 gap inside a 36–40-point band throughout (36.1 at the narrowest, 39.6 as released;
`scripts/difficulty_sensitivity.py`). This axis is distinct from the continuous size
gradient of [@sec:headline-performance] (≤15 / 16–25 / >25 heavy atoms), and InChIKey
de-duplication across rounds prevents leakage.

**The 50/50 balance is by design.** The sampler fills each difficulty stratum to half the
round; the eligible corpus is 17.5% simple / 82.5% complex. Reweighted to that composition,
top-1 falls 28.4% → 15.2% [10.6–20.4] and recall 33.5% → 19.8% [14.4–25.8]; verification
precision must be reweighted too (89.2% → 71.5% [50.2–92.5]). We report the benchmark figure
as released and the reweighted figure as the better estimate on an arbitrary paper.

**Scoring is mechanical (the leaderboard contract).** A prediction is *correct* if its RDKit
InChIKey connectivity layer (first 14 characters) matches the reference: we score
*constitution*, so correct constitution with wrong stereochemistry counts as correct. The
*full*, stereochemistry-sensitive InChIKey gives 21.1% top-1 and 25.8% recovered (41/194 and
50/194) against 28.4% / 33.5% — 7.3 points lower on top-1 and 7.7 on recovered — so the
constitution figure is an upper bound on full-stereochemistry accuracy. Constitution is
the headline because 1D ¹H/¹³C/IR rarely fixes absolute configuration: only 10.3%
(20/194) of answers carry a *defined* (assigned R/S) stereocentre, and a model is
penalised there for information the prompt never contained (`scripts/score_main.py
--stereo`). External submissions follow the same contract via
`scripts/score_submission.py` and the protocol in `docs/LEADERBOARD.md`: up to three ranked
SMILES per `qid`, no structure hints, document model version and tool access.

**Metrics.** *Top-1 (exact constitution)*: best-ranked candidate matches at the
connectivity layer; *recovered (top-3)*: reference among up to three returned candidates,
the lenient "recovery" protocol of ref. [@kamber2026chemist]. *Generation recall*:
reference in the candidate pool *before* re-ranking, the ceiling any verifier can reach
(coincides with recovered except in [@sec:generate-wide-testing-recipe], where the pool
is larger). *Verification precision (conditional on recall)* over recall-positive
compounds isolates verification from generation. The forward-verifier ranks by symmetric
*chamfer distance* between predicted and observed ¹³C peak sets (lower is better);
Morgan(2, 2048) Tanimoto[@rogers2010ecfp] gives a graded scaffold-family signal. CIs are
bootstrap 95%; model-vs-model differences use McNemar's exact test[@mcnemar1947] with
Holm correction[@holm1979]. Reports on IRSpectra-Bench should quote all three primary
numbers — top-1, generation recall, and verification precision | recall — not top-1 alone.

Solvers are frontier LLM agents (Claude Opus), one sub-agent per batch, closed-book under
a consumer subscription: no tools beyond an RDKit formula check, no ground truth, verified
by grep-auditing transcripts. Formula-adherence rates by round are reported in the
Electronic Supplementary Information.

## How well do LLMs elucidate real structures? {#sec:well-llms-elucidate-real}

Having defined IRexp and IRSpectra-Bench as reusable data objects, we next report the
decomposable metrics they enable — top-1 constitution, generation recall, and verification
precision — rather than a single end-to-end accuracy claim.

### Headline performance {#sec:headline-performance}

Solver agents work blind from formula + IR + ¹H + ¹³C, returning up to three ranked
candidates in bounded contexts reset every 2–12 compounds rather than one long context —
the variable [@sec:methodology-dominates-within-compound] shows what matters. The benchmark comprises all
194 compounds (134 spectrally-validated + 60 controlled-round;
`data/benchmark_main/raw/`).

**Table {#tab:headline-elucidation-performance-irspectra}. Headline elucidation performance on IRSpectra-Bench (n=194).** Overall and by difficulty stratum, with bootstrap 95% CIs.

| metric | overall (n=194) | simple (n=98) | complex (n=96) |
|---|--:|--:|--:|
| top-1 exact constitution | **28.4%** [22–35] | 48.0% [39–57] | 8.3% [3–15] |
| recovered (top-3) | 33.5% [27–40] | 54.1% [44–63] | 12.5% [6–20] |
| scaffold-level (best Tanimoto ≥ 0.45) | 56% | 73% | 39% |
| mean best Tanimoto | 0.59 | 0.73 | 0.45 |

A strictly-validated subset (134 main-clean + 57 controlled-clean = 191) reproduces this within ≈1 point on every
metric — top-1 28.8%, 95% CI 23–36; recall 34.0%; simple 49.0% / complex 8.4% — so the
asymmetric inclusion of pre-registered controlled sets does not drive it. The deliberate 50/50 difficulty balance does: reweighted to the
17.5%-simple composition of the eligible corpus, top-1 is 15.2% [10.6–20.4] and
recall 19.8% [14.4–25.8]
([@sec:benchmark-design-irspectra-bench]). Per-stratum figures are unchanged; the reweighted number is what to read as
performance on an arbitrary paper.
Accuracy falls monotonically with size ([@fig:fig1-difficulty]): 60.5% top-1 at ≤15 heavy atoms, 28.3% at 16–25, 7.0%
above 25 ([@sfig:size]).

![Top-1 and recovered accuracy on IRSpectra-Bench by difficulty (all / simple / complex, n=194), with bootstrap 95% confidence intervals. The benchmark separates a realistic difficulty range: simple targets are solved four to six times as often as complex ones on both metrics.](docs/figures/fig1_difficulty.png){#fig:fig1-difficulty}

Of the 137 analysable top-1 misses (139 in all; two predictions did not parse;
`scripts/analyze_misses.py`), 76.6% are constitutional isomers
of the true structure against 23.4% with the wrong formula — not mostly
regiochemistry: only 22.6% share the true Murcko scaffold, 2.9% reach Tanimoto ≥ 0.85, and the median
isomeric-miss Tanimoto is 0.39. Strict regiochemistry accounts for a fifth of failures;
most misses are larger rearrangements of the same atoms. Near-degenerate ¹H/¹³C
shifts under-determine connectivity; the misses show *wrong
connectivity at the right composition*.

### Reconciling with prior reports {#sec:reconciling-prior-reports}

Our 28% top-1 sits far below curated NMR-only demos[@kamber2026chemist] and below
in-distribution trained baselines (48–94%)[@chacko2024spectro; @ottomano2025nmiracle;
@alberts2025benchmarks]: difficulty, scoring leniency, starting-material hints and hand
curation inflate those reports, while settings differ on every axis from our blind
literature spectra. The ≈40× MolPuzzle swing for one model ([@sec:related-work]) bounds
what unaudited near-100% claims can bear.

### Methodology dominates: a within-compound control {#sec:methodology-dominates-within-compound}

On the same 20 molecules, recovered rose 5% → 15% (and top-1 0% → 15%; McNemar p=0.25)
when four bounded, tool-using agents replaced one long context — directional only.

### Model comparison: the benchmark orders capability but separates only the extremes {#sec:model-comparison-benchmark-ranks}

We solved a fixed 24-compound subset blind with four Claude models spanning a wide
capability range, including the newest (Fable 5), under one prompt, one scorer and one
candidate budget ([@fig:fig5-models], [@tab:four-model-comparison-fixed]).

One protocol asymmetry must be disclosed: the three comparison models solved the 24
compounds as four six-compound contexts each, whereas the Opus column reuses the headline
run, where those items sat in one six-compound and two twelve-compound contexts — the
variable that
[@sec:methodology-dominates-within-compound] measures at 5% → 15%. The Opus estimate is
therefore not protocol-matched and, if anything, handicapped by the longer contexts; this
touches neither the nesting nor the Fable-vs-Haiku contrast, and a clean re-run is
outstanding in `docs/MODELS.md`.

![Four-model comparison on a fixed 24-compound subset, solved blind under one protocol. Outcomes are strictly nested — each stronger model solves a superset of the weaker one's compounds — so the benchmark is capability-sensitive, but at n=24 it is underpowered to separate adjacent models ([@sec:model-comparison-benchmark-ranks]).](docs/figures/fig5_models.png){#fig:fig5-models}

**Table {#tab:four-model-comparison-fixed}. Four-model comparison on a fixed 24-compound subset.** All four models ran the identical blind protocol.

| model | top-1 | recovered | top-1 95% CI |
|---|--:|--:|--:|
| Claude Fable 5 | **46%** | 54% | [25–67] |
| Claude Opus | 25% | 29% | [8–42] |
| Claude Sonnet | 21% | 25% | [8–38] |
| Claude Haiku | 0% | 4% | [0–14] |

CIs are bootstrap except Haiku's: Clopper–Pearson exact for 0/24, where the percentile
bootstrap is degenerate.

Outcomes are strictly nested (Haiku ⊂ Sonnet ⊂ Opus ⊂ Fable); only Fable-vs-Haiku reaches
significance (Holm p=0.006). Opus headline runs used longer contexts than the comparison
models ([@sec:methodology-dominates-within-compound]).

### Domain case study: battery-electrolyte chemistry {#sec:domain-case-study-battery}

*IRSpectra-Bench-Electrolyte* (46 scored compounds across six electrolyte functional
classes, held out and solved blind) matches the headline regime: top-1 26%, recovered 28%;
the true structure enters the pool for 13/46 and ranks first in 12/13 — recall-bound, not
domain-specific ([@sfig:electrolyte], [@tab:per-class-performance-irspectra]). Per-class
intervals overlap (χ² p≈0.56); sp³-C–F reaches 50%, sulfonyl and nitrile 12%.

**Table {#tab:per-class-performance-irspectra}. Per-class performance on IRSpectra-Bench-Electrolyte (n=46).**

| electrolyte class | n | top-1 | 95% CI | recovered (top-3) | 95% CI |
|---|--:|--:|--:|--:|--:|
| sp³-C–F | 8 | **50%** | [22–78] | 50% | [22–78] |
| carbonate | 7 | 29% | [8–64] | 43% | [16–75] |
| phosphoryl | 8 | 25% | [7–59] | 25% | [7–59] |
| glyme / oligoether | 7 | 29% | [8–64] | 29% | [8–64] |
| sulfonyl / sulfonate | 8 | 12% | [2–47] | 12% | [2–47] |
| nitrile | 8 | 12% | [2–47] | 12% | [2–47] |

Intervals overlap throughout (six-class χ² p≈0.56; best-vs-worst Fisher exact p≈0.28), so
the ordering is hypothesis-generating, not established — C–F couplings pin sp³-C–F
regiochemistry, while sulfonyl and nitrile targets turn on oxidation-state ambiguity and
heteroaromatic substitution that ¹H/¹³C shifts underdetermine. It is the recall-bound
failure of [@sec:headline-performance] in a domain-specific guise, and it is where
[@sec:forward-verification-elucidation]'s *forward-verification* recipe plays a role
*analogous* to (not a replacement for) computational-NMR validation.

### Is the model reading the spectra? A formula-only control {#sec:model-reading-spectra-formula}

We reran the blind protocol with spectra masked, leaving only the formula
([@xu2024contamination]).

**Table {#tab:formula-only-control}. Formula-only control.** Paired on the same 60 compounds as [@sec:forward-verification-elucidation].

| condition | top-1 | recovered (top-3) |
|---|--:|--:|
| formula only | **3/60 (5%)** | 3/60 (5%) |
| formula + IR + ¹H + ¹³C | 14/60 (23%) | 19/60 (32%) |

Outcomes are perfectly nested (McNemar p=0.001). Accuracy is flat in source-paper year
across all 194 (r=−0.007; panel b of [@fig:fig-robustness]), bounding pretraining recall. We claim
a strong bound, not exclusion ([@sec:limitations]).

### Does the diagnosis hold outside one vendor? A four-vendor replication {#sec:diagnosis-hold-outside-one}

Grok 4.6, Gemini 3.7 Flash and GPT-5.6 Sol solved the same 60-compound arm under the
identical protocol ([@tab:cross-vendor-decomposition-60]). Verification precision exceeds
generation recall in every arm (panels c–d of [@fig:fig-robustness]); bootstrapping separates the
paired gap for Claude (+52.5 points), GPT-5.6 Sol (+26.3) and Gemini (+23.3); Grok's gap
(+9.2) is directional. Three models beat Claude on recall; candidate budgets differ (ours
2.20 vs 3.00 per compound), so recall rankings are approximate. A clean-clone control for
Grok (recall 28/60 vs 32/60, McNemar p=0.39) bounds key leakage. Models ran through a
coding-assistant harness with undisclosed reasoning tiers ([@sec:limitations]).

**Table {#tab:cross-vendor-decomposition-60}. Cross-vendor decomposition on the 60-compound arm.** Recall and precision have
different denominators, so the criterion is the inequality rather than a difference.

| model | generation recall | verification precision \| recall | multi-candidate only |
|---|--:|--:|--:|
| Claude Opus ([@tab:forward-verification-decomposition]) | 19/60 = 32% [21–44] | 16/19 = 84% [62–94] | 10/13 = 77% |
| Grok 4.6 | 32/60 = 53% [41–65] | 20/32 = 62% [45–77] | 20/32 = 62% |
| Gemini 3.7 Flash | 30/60 = 50% [38–62] | 22/30 = 73% [56–86] | 22/30 = 73% |
| GPT-5.6 Sol | 25/60 = 42% [30–54] | 17/25 = 68% [48–83] | 16/24 = 67% |

![Robustness of the recall-bound diagnosis. (**a**) Formula-only vs full modality on 60 compounds. (**b**) Accuracy vs source-paper year (n=194; point-biserial r=−0.007; dashed line = pooled 28%). (**c**) Generation recall by model on the 60-compound arm (orange = Claude Opus headline; grey = below formula-adherence gate). (**d**) Verification precision vs generation recall (numbered key; [@sec:diagnosis-hold-outside-one]).](docs/figures/fig_robustness.png){#fig:fig-robustness}

## Forward-verification elucidation {#sec:forward-verification-elucidation}

### Method {#sec:method}

The inverse direction is the model's hard, isomer-blind direction; the forward
direction (structure → spectrum) is its easy, accurate one[@kamber2026chemist]. We close a
training-free generator–verifier loop:

> *generate* candidate structures (inverse) → *forward-predict* each candidate's
> ¹³C spectrum, blind to the observed spectrum → *re-rank* candidates by the
> distance between predicted and observed ¹³C → return the best match.

The inverse solver's 373 deduplicated candidates across 194 targets are forward-predicted
in shuffled, anonymised batches, blind to the observed spectrum and target identity.
Predicted and observed ¹³C peak sets are compared by symmetric chamfer distance
([@fig:fig-mechanism]).

![Forward-verification on a benchmark regioisomer pair: picolinamide and nicotinamide are indistinguishable to the inverse task, but forward-predicted ¹³C sticks separate the true isomer from the alternative ([@sec:method]).](docs/figures/fig_mechanism.png){#fig:fig-mechanism}

Regioisomers separate by a median 1.21 ppm in forward prediction, but 82% lie within the
predictor's ≈2 ppm error — a thin margin confirmed against a derangement null at p=0.001
([@sec:negative-control]). Sharper predictors (GNN, DFT-coupled models[@williamson2024mpnn;
[@han2024dftgnn; @cohen2023delta50]) would move the verification ceiling, not search.

### Result {#sec:result}

The first column below is the 60-compound arm (v3 + v2-control) on which
[@sec:generate-wide-testing-recipe]–[@sec:negative-control] build; the second, the full
benchmark. All 373 candidates were forward-predicted — nothing here is a lower bound;
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
of 65 cases (89%). Of the 65, 28 had a single candidate — scored by construction by any
ranker — so the pooled figure is not the verifier's margin over chance. Where a choice
existed (n=37), forward-verification gets 30/37 (81%) against a 54.0% derangement floor
([@sec:negative-control]) — +27.1 points; self-ranking 27/37 (73%).

The margin over self-ranking remains small and unresolved: seven compounds gained, four
lost, McNemar exact p=0.55. We do not claim it. Precision is high in absolute terms while
recall binds: top-1 moves only 28% → 30% because the true structure was never proposed for
129 of 194 compounds, which no re-ranking can repair. The verifier converts recall almost
completely on *simple* targets (50/53, 94%) and ties self-ranking on *complex* ones
(8/12, 67%). Elucidation factorises into two near-independent levers: a strong verifier
and a generator at 34% recall that is the wall ([@fig:fig-wall]).

### Generate-wide: testing the recipe {#sec:generate-wide-testing-recipe}

The decomposition implies *generate wide, verify by forward prediction* — a chemistry
analog of self-consistency sampling[@wang2023selfconsistency]. Ten solver agents proposed
up to six regiochemistry-aware candidates per compound, pooled with the originals and
re-ranked.

**Table {#tab:generate-wide-vs-original}. Generate-wide vs original.** On the 60-compound arm only, since wide generation was run there; the "original" column is [@tab:forward-verification-decomposition]'s first.

| | original (60-compound arm) | generate-wide |
|---|--:|--:|
| generation recall (true structure among candidates) | 32% | **42%** |
| forward-verified top-1 | 27% | 30% |
| verification precision (conditional on recall) | 84% | 72% |

Wide generation lifts recall 32% → 42% and top-1 23% → 30% (McNemar p=0.34;
[@fig:fig3-method]). Recall plateaus at 42% on polycyclic targets; verification precision
falls 84% → 72% — the training-free ceiling. Roughly a third of misses need only
regiochemistry around a correct scaffold; two thirds need a scaffold never proposed.

![Forward-verification inference ladder on the 60-compound arm ([@sec:generate-wide-testing-recipe]). Each stage adds a check on the same compounds; the hero bar is generate-wide top-1.](docs/figures/fig3_method.png){#fig:fig3-method}

### Non-LLM verifiers: a deterministic lookup and a learned model {#sec:non-llm-verifiers-deterministic}

[@sec:generate-wide-testing-recipe] suggests replacing the verifier with a non-LLM ¹³C predictor. We tested a HOSE-code[@bremser1978hose]-style lookup and a small message-passing GNN, both trained on the same nmrshiftdb2 dump[@kuhn2015nmrshiftdb2] and applied to the same [@sec:result] candidate sets so only the predictor changes. The GNN is deliberately modest; sharper purpose-built ¹³C models exist[@williamson2024mpnn; @han2024dftgnn; @xu2025nmrbench].

**Table {#tab:verifier-comparison-conditional-recall}. Verifier comparison, conditional on recall.**

| verifier | 60-compound arm (n=19) | full benchmark (n=65) | held-out ¹³C MAE |
|---|--:|--:|--:|
| solver self-ranking | 14/19 (74%) | 55/65 (85%) | — |
| deterministic HOSE *lookup* | 14/19 (74%) | 55/65 (85%) | 3.23 ppm |
| learned GNN (same data) | 16/19 (84%) | **59/65 (91%)** | 1.70 ppm |
| LLM forward-verifier ([@sec:result]) | 16/19 (84%) | 58/65 (89%) | — |

The HOSE lookup ties self-ranking; the GNN reaches 59/65 (91%) vs the LLM's 58/65 (89%),
directionally ([@tab:verifier-comparison-conditional-recall], [@sfig:verifier]). Wagen's
MagNET-in-the-loop study[@wagen2026simtools; @adams2026magnet; @novitskiy2022peculiar] moves
connectivity 46.4% → 55.4% on eight problems — same order as our ladder, underpowered at n=8.

### Negative control {#sec:negative-control}

Deranging observed ¹³C pairings collapses verification precision 89.2% → 73.8% mean
(one-sided p=0.001); on multi-candidate sets alone, 81.1% vs a 54.0% floor (+27.1
points). Chamfer margin does not support selective prediction (flat top-1 across coverage
fractions) — a reported null.

### Is the recall wall task-intrinsic? A trained-generator probe {#sec:recall-wall-task-intrinsic}

That ceiling is a property of training-free LLM elicitation, not the task. Pooling a small
IRexp-fine-tuned ¹H/¹³C → SMILES generator with Claude's candidates lifts recall 33.5% → 54.1%
and top-1 28.4% → 35.1% (McNemar p=0.015; [@sfig:generator-probe]). Zero-shot without IRexp
fine-tuning recovers 0/248; with it, 25%. NMR-Solver (52.9%)[@jin2025nmrsolver] and trained
IR transformers (63.8%)[@alberts2025benchmarks] confirm the task is not bound at 28–30%.

```{=latex}
\needspace{8\baselineskip}
```

## The decomposition across the published literature {#sec:literature-decomposition}

The split measured above applies to any system reporting top-1 = *a* and top-*k* = *b*:
recall ≥ *b*, conditional precision ≤ *a*/*b*. [@tab:literature-decomposition] applies this
to every system we could read in full (`scripts/literature_decomposition.py`).

**Table {#tab:literature-decomposition}.** Recall and ranking loss from published top-*k*
figures. Rows are comparable only within a correctness criterion; stereochemistry-strict and
connectivity figures differ by 21 points on NMR-Solver's identical predictions. Candidate
budgets are given because recall over three candidates is mechanically smaller than over ten.

| system | data (*n*) | top-1 | top-*k* (*k*) | recall | prec. |
|---|---|--:|--:|--:|--:|
| ***scored on connectivity*** | | | | | |
| this work, solver alone | literature (194) | 28.4% | 33.5% (3) | 33.5% | 84.6% |
| this work, + forward-verification | literature (194) | 29.9% | 33.5% (3) | 33.5% | **89.2%** |
| NMR-Solver[@jin2025nmrsolver] | literature (450) | 52.9% | 67.3% (10) | ≥ 67.3% | ≤ 78.6% |
| NMRAgent[@fang2026nmragent] | literature (450) | 61.6% | 70.0% (10) | ≥ 70.0% | ≤ 88.0% |
| ***scored with stereochemistry*** | | | | | |
| this work | literature (194) | 21.1% | 25.8% (3) | ≥ 25.8% | ≤ 81.8% |
| NMR-Solver[@jin2025nmrsolver] | simulated (1,000) | 66.9% | 89.9% (10) | ≥ 89.9% | ≤ 74.4% |
| NMR-Solver[@jin2025nmrsolver] | literature (450) | 31.6% | 53.8% (10) | ≥ 53.8% | ≤ 58.7% |
| Espejo Morales[@espejo2026agentic] | education (236) | 80.9% | 90.0% (5) | ≥ 90.0% | ≤ 89.9% |
| Espejo Morales[@espejo2026agentic] | industrial (34) | 20.6% | 29.1% (5) | ≥ 29.1% | ≤ 70.9% |
| ***exact match, stereo handling not stated*** | | | | | |
| Alberts, 6–13 atoms[@alberts2025benchmarks] | NIST IR (3,455) | 63.8% | 84.0% (10) | 84.0% | 75.9% |
| Alberts, 5–35 atoms[@alberts2025benchmarks] | NIST IR (5,024) | 59.9% | 78.5% (10) | 78.5% | 76.4% |
| SpecX, random split[@xiang2026specx] | simulated (99,439) | 59.0% | 81.8% (10) | 81.8% | 72.2% |
| SpecX, scaffold split[@xiang2026specx] | simulated (99,439) | 29.7% | 50.6% (10) | 50.6% | 58.7% |
| IR-Agent[@noh2025iragent] | NIST IR (905) | 10.3% | 21.6% (10) | 21.6% | 47.7% |
| ***criterion not stated*** | | | | | |
| Priessner[@priessner2026reasoning] | experimental (34) | 20.6% | — | 26.5% | 77.8% |

**Three groups changed only the data** and recall carried 68% (NMR-Solver simulated → real),
70% (SpecX random → scaffold) and 83% (Espejo education → industrial) of each collapse. Published
gains come mainly from candidate supply (NMRAgent ablation[@fang2026nmragent], NMRGym formula
ablation[@fang2026nmrgym]). Recall binds where spectra are real and heterogeneous (87–91% of
our loss); ranking dominates on simulated or single-library data (38–39%). The field almost
never reports whether the true structure was proposed at all
([@priessner2026reasoning] excepted).

## Discussion {#sec:discussion}

Frontier LLMs are good verifiers (89% conditional precision) and weak proposers (34%
recall) on real literature spectra. The primary contribution is chemical-information
infrastructure — IRexp, IRSpectra-Bench, frozen predictions and a decomposable scorer —
with a diagnosis and a bounded, training-free improvement attached; not a solved
elucidator ([@sec:limitations]).

That split held across four Claude models, a battery-electrolyte subset, four verifiers and
four vendor families ([@sec:literature-decomposition]); concurrent systems that move the
same levers are surveyed in [@sec:related-work].

**Reporting on IRSpectra-Bench.** External work should deposit ranked SMILES under the
released protocol (`docs/LEADERBOARD.md`; `scripts/score_submission.py`) and report, at
minimum: (i) top-1 constitution (InChIKey connectivity), (ii) generation recall (true
structure in the candidate pool before re-ranking), and (iii) verification precision
conditional on recall, with bootstrap CIs and candidate budget. Top-1 alone conflates the
two stages this paper separates. Nonsignificant ladder gains (forward-verification vs
self-ranking, McNemar p=0.55; generate-wide top-1, p=0.34) should be cited as diagnostic,
not as accuracy advances. Corpus-reweighted top-1 (15.2%) is the better estimate for an
arbitrary literature draw; the released 50/50 figure remains the comparable leaderboard
number. IRexp re-users should keep PMC and Chemotion licence pools separable and de-leak
benchmark InChIKeys before training ([@sec:contents-licensing]).

Training is not foreclosed: IRexp fine-tuning lifts recall to 54%
([@sec:recall-wall-task-intrinsic]). What compounds is open experimental data, honest
benchmarks, and inference scaffolding that rides each new model. Two practical findings:
bounded contexts with tool access may help
([@sec:methodology-dominates-within-compound]); use forward-predicted ¹³C agreement to
re-rank, not as an abstention gauge ([@sec:negative-control]).

## Limitations {#sec:limitations}

Scoring is mechanical; solver runs were transcript-audited for zero ground-truth access
(transcripts on request). **(i) Consumer harness.** Runs used a consumer subscription that
exposes no model snapshot, temperature, seed or thinking tier; exact inference is not
reproducible. Scoring is: frozen predictions, ground truth and mechanical scorers regenerate
every training-free number. The instruction text wrapping Claude solver and
forward-prediction batches was not captured — only per-compound payloads are released —
so the verbatim prompts in the ESI are the cross-vendor harness prompts.
**(ii) Pretraining contamination** is bounded by formula-only (23% → 5%) and flat recency
controls ([@sec:model-reading-spectra-formula]) but not excluded; verbatim spectral strings
from PMC in the prompt remain a retrieval confound.
**(iii) Object type, formula and scoring.** Inputs are author-transcribed band and shift
lists, not raw absorbance traces or FIDs — a different object from digitised spectra and
from Espejo *et al.*[@espejo2026agentic]. The molecular formula is supplied (as from HRMS);
systems such as NMIRacle[@ottomano2025nmiracle] that take no formula solve a harder prior,
so absolute accuracies are not interchangeable. Headline metrics score constitution
(InChIKey connectivity); with stereochemistry, top-1 is 21.1%.
**(iv) Statistical honesty.** Forward-verification vs self-ranking is unresolved (McNemar
p=0.55); generate-wide top-1 likewise (p=0.34). The four-model comparison at n=24 is
underpowered for adjacent ranks and carries a disclosed protocol asymmetry
([@sec:model-comparison-benchmark-ranks]). The inference ladder diagnoses a bottleneck; it
is not a demonstrated accuracy advance.
**(v) Missing on-bench cheminformatics baselines.** Spectro, NMIRacle, Alberts IR
transformers and CASE were not scored on IRSpectra-Bench, so the LLM recall wall is not
cleanly separated from harness or modality choice — left to future leaderboard work under
the released InChIKey scorer.
**(vi) Cross-vendor scope.** Headline n=194 is Claude Opus; the four-vendor replication is
on 60 compounds. Candidate budgets differ across vendors (Claude mean 2.20 vs 3.00), so
recall rankings are approximate ([@sec:diagnosis-hold-outside-one]).
**(vii) Deferred and abandoned arms.** The expert-chemist audit of elucidation outputs is
frozen at `data/audit/` and formally deferred — not run. Leave-one-modality-out ablation
(`noIR`/`noH`/`noC`) was specified and never completed; it is abandoned for this manuscript
(`docs/MODELS.md`; ESI). The extraction-recall human audit of parser coverage
([@sec:contents-licensing]) is likewise deferred.
**(viii) Scope.** Battery subset uses literature electrolyte chemistry, not operando
spectra. Single-sample scoring per compound (bootstrap CIs reflect compound sampling only).
Organic literature bias of PMC-OA sources.

## Methods {#sec:methods}

**Mining and resolution.** PMC-OA full text was fetched from `s3://pmc-oa-opendata`,
parsed deterministically, and resolved with OPSIN, RDKit and SELFIES, with an optional
cached PubChem fallback.

**Benchmark and agents.** Problems were sampled from `irexp_resolved`, stratified by RDKit
ring analysis, and de-duplicated across rounds by InChIKey. A compound was admitted only if
its raw ¹H payload — multiplicities and *J* values as printed — could be re-extracted
verbatim from the PMC-OA full text of its source article (`benchmark_v2.raw_1h_for`), which
puts genuine coupling information in the prompt and, unavoidably, the source article's
exact string ([@sec:limitations]). The battery-electrolyte subset
([@sec:domain-case-study-battery]) was drawn by SMARTS filters for six electrolyte
functional classes (carbonate, sulfonyl/sulfonate, nitrile, sp³-C–F, phosphoryl,
glyme/oligoether), balanced to eight compounds per class (48 curated; 46 scored after two
yielded no parseable candidate), excluding compounds used elsewhere; it was *J*-enriched
and spectrally validated. Solver and
forward-prediction agents were independent Claude-Opus sub-agents under the same
subscription, instructed closed-book and audited for zero web/answer access. Scoring used
RDKit InChIKey-connectivity match; similarity Morgan(2, 2048) Tanimoto; forward-verification
a symmetric chamfer distance over ¹³C peak sets. The core protocol trains no model and uses
no paid API; the [@sec:recall-wall-task-intrinsic] generator and the
[@sec:non-llm-verifiers-deterministic] learned ¹³C verifier are the only trained components,
reported as complements and fenced from the headline results.

**Models and versions.** Headline runs used Claude Opus via consumer subscription
(2026-06-09–11); formula-only control 2026-07-28; forward-prediction extension
2026-08-07. No model snapshot or decoding parameters can be reported — the harness exposes
neither ([@sec:methods]). Fixed are frozen per-compound outputs and mechanical scorers
(`docs/MODELS.md`).

**Reproducibility.** Every round is frozen: questions, ground-truth answers, per-agent
raw outputs, predictions and scorer outputs are released; the sampler, scorer and
forward-verification harness are scripted end-to-end.

## Supporting Information

Supplementary figures and extended methods appear in the Electronic Supplementary
Information (`docs/paper_esi.pdf`).

## Author contributions

**I.Y.:** conceptualization, methodology, software, formal analysis, investigation,
data curation, visualization, writing — original draft.

**R.S.:** methodology, software, formal analysis, investigation, validation
(trained-generator and learned-verifier probes, [@sec:non-llm-verifiers-deterministic]
and [@sec:recall-wall-task-intrinsic]), writing — review and editing.

**R.A.V.-H.:** conceptualization, methodology, supervision, writing — review and editing.

## Conflicts of interest

There are no conflicts to declare.

## Data availability

Data, frozen predictions, scoring scripts and figure regeneration are in the project
repository ([github.com/IlkhamFY/spectro-agent](https://github.com/IlkhamFY/spectro-agent));
[@tab:artefacts] lists each component. A frozen archival snapshot will be deposited on
Zenodo ([TODO: 10.5281/zenodo.XXXXXXX]; DOI at proof); GitHub remains the development
mirror. IRexp is also mirrored at
[huggingface.co/datasets/ilkhamfy/IRexp](https://huggingface.co/datasets/ilkhamfy/IRexp)
(use `data/train_no_bench.jsonl.gz` for fine-tuning without benchmark leakage). Leaderboard
submissions follow `docs/LEADERBOARD.md`.

<!-- ZENODO: mint the deposit and substitute its DOI for "DOI at proof" / the TODO above.
     Reserve it at 10.5281/zenodo.XXXXXXX; `python scripts/check_manuscript.py` lists this
     until it is done. -->

**Table {#tab:artefacts}. Headline released artefacts.** Script-level inventory lives in the
repository README.

| component | data and code |
|:---|:---|
| IRexp / `irexp_resolved` | `data/irexp/`, `data/irexp_resolved/` |
| benchmark + within-compound control | `data/benchmark*/` — `scripts/benchmark_v2.py` |
| headline scoring ([@tab:headline-elucidation-performance-irspectra]) | `scripts/score_main.py` |
| forward-verification (+ full-bench extension) | `data/fverify/`, `data/fverify_main/` — `scripts/forward_verify.py`, `scripts/forward_verify_main.py` |
| generate-wide ([@sec:generate-wide-testing-recipe]) | `data/gw/`, `data/fverify2/`, `data/fverify_gw/` — `scripts/score_generate_wide.py` |
| cross-vendor ([@sec:diagnosis-hold-outside-one]) | `data/cross_vendor/` — `scripts/cross_vendor_budget.py`, `scripts/cross_vendor_gap.py` |
| contamination / recency ([@sec:model-reading-spectra-formula]) | `data/modality/`, `data/audit/recency_control.json` — `scripts/modality_ablation.py`, `scripts/contamination_recency.py` |
| figures | `docs/figures/` — `scripts/make_all_figures.sh` |
| trained generator + GNN verifier | `contrib/generator_probe/`, `data/fverify_gen/` — `scripts/gnn_predict.py`, `data/nmrshiftdb/gnn_c13.pt` |
| integrity gates | `scripts/check_manuscript.py`, `scripts/check_layout.py` |

IRexp redistributes extracted numeric data only (band lists, shifts, structures, source
DOIs) from the PMC Open Access Subset and Chemotion, with per-record `license` /
`license_pool` stamps (commercial CC-BY/CC0 primary pool 87,617; NC* held aside;
Chemotion CC-BY-SA-4.0; empty/unknown excluded from commercial Zenodo —
`scripts/join_pmc_licences.py`, `scripts/split_license_pools.py`). Code is MIT. Cite the
Zenodo deposit and attribute sources via each record’s `source_doi`. De-leak with
`contrib/generator_probe/build_exp_manifest.py` before training against the benchmark;
withhold `data/audit/key.jsonl` and `data/modality/key.json` from blinded reviewers.

## Acknowledgements

<!-- ACKNOWLEDGEMENTS — funding sources and institutional support — AUTHORS -->

Funding and institutional support will be added at proof.

## References

<!-- Generated by pandoc --citeproc from docs/references.bib using the Royal Society of
     Chemistry CSL style (docs/rsc.csl). Do not hand-number: cite with the bracketed
     at-key syntax in the text and the list below is built automatically, in citation
     order. NOTE: do not write a literal example of that syntax here -- pandoc parses
     citations inside HTML comments and it becomes a phantom empty reference. -->

::: {#refs}
:::

