# Recall, not verification, is the bottleneck when frontier LLMs elucidate molecular structures from real spectra

**Ilkham Yabbarov**^a^ *(corresponding author: ilkhamfy@gmail.com)*, **Rudra Sondhi**^a^, **Rodrigo A. Vargas-Hernández**^a^

*^a^ Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario L8S 4L8, Canada.*

<!-- AUTHORS — ORCID iDs are required by RSC for the corresponding author and requested
     for all co-authors. Fill these in before submission; they are deliberately left as
     visible placeholders rather than omitted, so nothing is silently missing:
       I. Yabbarov            ORCID: [TODO: 0000-0000-0000-0000]
       R. Sondhi              ORCID: [TODO: 0000-0000-0000-0000]
       R. A. Vargas-Hernández ORCID: [TODO: 0000-0000-0000-0000]
     `python scripts/check_manuscript.py` lists every outstanding item of this kind. -->

---

## Abstract

Given the molecular formula together with the infrared band list and ¹H/¹³C shift lists
exactly as reported in an open-access paper, how often does a frontier large language model
(here, Claude) recover the correct molecular *constitution*? We find **28%** (top-1, n=194;
95% CI 22–35) — far below the near-100% implied by curated demonstrations.

The bottleneck is not the model's judgment but its *proposal*. Across the whole benchmark
the model proposes the true structure for only **34%** of compounds; where it does,
forward-verification — predicting each candidate's ¹³C spectrum and re-ranking by agreement
with the observed one — selects it **89%** of the time (58/65; 81% on the 37 where more than
one candidate existed, [@sec:result]). **Recall, not verification, is the wall.**

We contribute three things. **IRexp**, the largest openly redistributable collection of
*experimental* infrared band lists (121,233 records, a third structure-linked), mined from
open-access literature and released with its pipeline. **IRSpectra-Bench**, an open, blind,
mechanically scored benchmark of 194 compounds on which accuracy splits sharply with
structural complexity, and where a within-compound control shows reported numbers are
sensitive to how a problem is posed. And a training-free **forward-verification** recipe,
run over every benchmark compound. The two levers are distinct and we keep them apart:
verification re-ranks a fixed candidate set and lifts top-1 from 28% to 30%, while
*generating wider* is what moves recall — 32% to 42%, carrying top-1 from 23% to 30% on the
arm where both were tested. Every top-1 step is directional rather than statistically
resolved ([@sec:result], [@sec:generate-wide-testing-recipe]); the recall gain is the better-supported effect.

Those gains stop short of a ceiling, and the ceiling belongs to training-free elicitation
rather than to the task: a small generator fine-tuned on IRexp lifts recall substantially
and gives the highest full-benchmark accuracy we report ([@sec:recall-wall-task-intrinsic]). But the wall moves rather
than falls — the true
structure stays outside the candidate pool for roughly half of compounds. Two independent
contamination controls confirm the spectra do the work: masking them drops top-1 from 23%
to 5% on the same compounds, and accuracy is flat in the publication year of the source
paper ([@sec:model-reading-spectra-formula]). The decomposition is not confined to one lineage: on the same 60 compounds,
Grok 4.6, Gemini 3.7 Flash and GPT-5.6 Sol all verify better than they generate, and three
of six non-Claude models exceed our headline model's recall ([@sec:diagnosis-hold-outside-one]). The core protocol uses no model training and no paid API — two clearly-fenced
probes ([@sec:non-llm-verifiers-deterministic], [@sec:recall-wall-task-intrinsic]) are the only exceptions — and all data, predictions, and code are
released.

---

## Introduction {#sec:introduction}

Determining a molecule's structure from its spectra is a central, time-consuming
task in synthetic and analytical chemistry. The dominant machine-learning approach
trains specialised encoder–decoder models to map spectra to structures; the recent
*Spectro* model, for example, learns ¹H/¹³C/IR → SELFIES from a corpus of 6,833
molecules.[@chacko2024spectro] In parallel, general-purpose LLMs have been reported to perform the
same task off-the-shelf: a 2026 industrial white paper (a non-peer-reviewed company
report) found that Claude Opus matched or beat commercial NMR-prediction software in
the forward direction (structure→spectrum, ±0.08 ppm ¹H) and "recovered all eight
simpler structures on every attempt" in the inverse direction (spectrum→structure).[@kamber2026chemist]
We treat its numbers as a motivating claim to be tested against peer-reviewed
benchmarks, not as an established baseline.

These results are striking, but the evaluation that supports them is narrow: 15
inverse problems on curated single-ring or two-fragment molecules, NMR only, with
the seven harder targets additionally given the *starting-material structure* as a
hint, and "recovery" scored leniently over three runs and three ranked candidates.
The question a practising chemist actually faces — *take an arbitrary experimental
spectrum from a paper and recover the structure* — is left open. Answering it
requires (i) a large, diverse, real benchmark; (ii) a blind, reproducible scoring
protocol; and (iii) honest accounting for the methodological choices that inflate
or deflate the apparent score.

We provide all three. We build IRexp ([@sec:irexp-dataset]), a literature-mined dataset that supplies
the IR modality absent from prior LLM evaluations alongside paired NMR and resolved
structures. We define a blind benchmark on it ([@sec:benchmark-design-irspectra-bench]) and measure inverse-elucidation
performance under matched and mismatched methodologies ([@sec:well-llms-elucidate-real]), isolating a large
solver-methodology effect with a within-compound control. We then introduce
forward-verification elucidation ([@sec:forward-verification-elucidation]), a training-free method that turns the model's
*strong* direction (forward prediction) against its *weak* one (inverse
regiochemistry), and use it to localise the bottleneck. The central finding is a sharp asymmetry:
given a candidate set that contains it, the model *verifies* the correct structure 89% of the time,
yet *proposes* it for only 34% of compounds — recall, not verification, is the wall
([@fig:fig-wall]).

![The diagnosis in one glance: all 194 benchmark compounds as a single part-to-whole bar. The true structure is verified top-1 for 58 (green), recalled but mis-ranked for 7 (vermilion), and never proposed for 129 (grey) — *the wall*, 66% of the bar. Generation recall is 65/194 = 34%; conditional verification precision is 58/65 = 89%; their product is the 30% end-to-end top-1. The two rates have different denominators and are not differenced.](docs/figures/fig_wall.png){#fig:fig-wall}

The end-to-end study design is summarised in [@sfig:overview]. Throughout, the
solver and verifier are LLM agents run under a
consumer subscription — no fine-tuning, no API spend. That makes the protocol cheap to
*re-run*, but cheap is not the same as reproducible: the subscription harness pins no model
snapshot, exposes no temperature or seed, and carries an undisclosed product system prompt,
so an outside group reproduces it distributionally rather than exactly ([@sec:methods]). What *is*
exactly reproducible is the scoring — all predictions, ground truth and scorers are
released, so every number in the training-free core ([@sec:benchmark-design-irspectra-bench]–[@sec:generate-wide-testing-recipe], [@sec:model-reading-spectra-formula]) regenerates from the
released artifacts. Two rows are the exception: [@sec:non-llm-verifiers-deterministic]'s HOSE lookup and GNN are built from
an nmrshiftdb2 dump we cannot redistribute, so they regenerate only once a reader supplies
the same dump (see *Data and code availability*). The two trained probes — that GNN
verifier and the [@sec:recall-wall-task-intrinsic] generator — are reported separately, as fenced complements to the
training-free protocol rather than part of it.
By construction this is an open-resource contribution in the remit of *Digital Discovery*:
an openly licensed, structure-linked spectral dataset; a pre-registered, mechanically scored
benchmark with released ground truth and scorer; and a training-free, zero-paid-API core
pipeline (with two trained probes fenced in the SI) in which every main-text figure regenerates from the
released code and predictions. We prioritise an honest, reusable measurement of where current
models stand over a leaderboard-topping number.

**Contributions.**

1. **IRexp** — to our knowledge the largest openly *redistributable* collection of
   experimental IR **band lists** (121,233 records; 43,060 structure-linked; 33,201
   IR+¹H+¹³C+structure), released under permissive licences for bulk model development
   with a reproducible mining pipeline. The claim is scoped to that object type
   deliberately: view-only libraries such as SDBS hold more structure-linked *spectra*,
   and commercial libraries are larger still — neither is redistributable, and neither is
   what IRexp competes with ([@sec:motivation]).
2. An **open multimodal benchmark** — to our knowledge the first blind, mechanically
   scored, complexity-stratified evaluation of frontier-LLM structure elucidation on real
   spectra — measured in depth on one model family (Claude) and replicated across three
   others ([@sec:diagnosis-hold-outside-one]), which reconciles the gap to optimistic prior reports. Crucially, the ground truth is experimental
   structures from the published literature, resolved deterministically (OPSIN/RDKit) and
   checked against the source articles mechanically (560/560 bands confirmed on a
   seed-fixed sample, [@sec:contents-licensing]; the *expert-chemist* review is prepared but not yet run, [@sec:limitations]):
   no LLM curates the labels or scores the predictions. The model is the system under
   test, not the source of its own answers.
3. A **diagnostic decomposition** of LLM elucidation into recall and verification,
   showing that **recall — not verification — bounds current performance**, obtained via
   a training-free forward-verification probe run over **every** benchmark compound. The
   generate-and-forward-verify loop itself is prior art — NMR-Solver[@jin2025nmrsolver]
   implements it without an LLM and reports higher accuracy with a sharper predictor
   ([@sec:related-work]); what is ours is the decomposition it enables, not the loop. It
   yields a bounded improvement (top-1 28%→30% on n=194; 23%→30% on the 60-compound arm
   where wide generation was also tested) but, by our own measurements, cannot exceed a
   recall/precision ceiling without sharper verification or 2D-NMR data.

### Related work {#sec:related-work}

**Trained spectra→structure models.** The dominant line trains sequence or graph
decoders to emit structures from spectra: *Spectro* (¹H/¹³C/IR→SELFIES)[@chacko2024spectro], the
multitask CNN+transformer of routine 1D-NMR[@hu2024multitask], and set/graph transformers such as
NMRTrans[@yang2026nmrtrans]. These reach high accuracy *in-distribution* but require a labelled
spectra→structure corpus, which is exactly the scarce resource our IRexp pipeline
targets, and they are retrained per modality. Closest in spirit to our multimodal
setting is **NMIRacle**[@ottomano2025nmiracle], a generative model conditioned jointly on IR + ¹H + ¹³C;
it is a strong trained baseline, whereas our contribution is the *open experimental-IR
data it (and others) can train on*, plus a *training-free* protocol and a blind
benchmark to measure it.

**LLMs as elucidators, and how this work differs.** The wider setting is by now
established: LLMs orchestrating chemistry tools plan and execute real syntheses
(ChemCrow[@mbran2024chemcrow], Coscientist[@boiko2023coscientist]), which is what makes
the narrower question here worth asking — those systems *call* an elucidation routine,
and this paper measures what such a routine can be expected to return. General-purpose
LLMs have been
applied off-the-shelf — Anthropic's forward/inverse white paper[@kamber2026chemist],
SpectraLLM and SpecMol (multimodal LLMs over multi-spectral
input)[@su2025spectrallm; @shen2025specmol], and knowledge-enhanced tree-search reasoning[@zhuang2025treesearch] — and dedicated multimodal
*benchmarks* now exist, most prominently **MolPuzzle**[@guo2024molpuzzle] (IR+MS+¹H+¹³C elucidation
puzzles with the molecular formula supplied). Closest to the present method,
**IR-Agent**[@noh2025iragent] introduces a multi-agent LLM framework that emulates expert IR
interpretation and evaluates on experimental infrared spectra. These establish that the
task is worth benchmarking, that LLMs can be scored on multi-spectral input, and that
agentic decomposition of the interpretation helps; we claim priority on none of them.
Our contribution is orthogonal to IR-Agent's: where it improves *how the model reads a
spectrum*, we ask what limits the outcome once it has, and answer with a measured
decomposition — generation recall versus verification precision — plus the blind benchmark
and open dataset needed to measure either honestly. What is new here is three things that, to our knowledge, no prior benchmark
combines. **(i) Real, literature-mined experimental spectra at scale:** prior multimodal
benchmarks and trained baselines evaluate either on simulated or software-predicted
spectra[@chacko2024spectro; @ottomano2025nmiracle] or on *curated single-instrument*
libraries — Alberts et al. use NIST gas-phase IR[@alberts2024ir; @alberts2025benchmarks] —
whereas IRSpectra-Bench is drawn from IRexp's
experimental IR + ¹H + ¹³C **as reported by the authors of the source papers**, across
thousands of laboratories and instruments, for out-of-distribution compounds. The
contrast we can draw is therefore between literature-reported heterogeneity and both
simulation *and* curated uniformity, not between simulated and real alone. The closest trained precedent,
Alberts et al.[@alberts2024ir], learns an IR→structure transformer from ~635k *simulated* spectra with
a 3,453-spectrum experimental fine-tune (top-1 44% on 6–13 heavy atoms), since improved
by the same group to **63.8% top-1 / 84.0% top-10 on experimental NIST gas-phase spectra**
given the formula, pretraining on 1,399,806 simulated spectra[@alberts2025benchmarks]. That line is
the state of the art for *trained, formula-conditioned IR* elucidation. Its evaluation is
restricted to **6–13 heavy atoms**, which is the size range where our own accuracy is
highest — 60.5% top-1 for ≤15 heavy atoms ([@sec:headline-performance]) — so on comparable molecules the
training-free LLM and the purpose-trained transformer are closer than the headline
numbers suggest; the gap our benchmark exposes opens up at the *larger* sizes their
evaluation excludes (7.0% above 25 heavy atoms). IRexp instead
releases experimental IR at scale as an open, redistributable resource and pairs it with
a blind LLM benchmark. The two are complements rather than competitors — their models
need exactly the kind of experimental data IRexp exists to supply, and neither their
setting (single modality, gas-phase NIST, formula-constrained decoding) nor ours bounds
the other. **(ii) Blind, fully specified, mechanical scoring:** reported
accuracies on the same task vary enormously with inference method and scoring harness —
the *same model* on the *same benchmark* spans a factor of forty. GPT-4o is reported at
**1.4%** on MolPuzzle by the benchmark's own authors[@guo2024molpuzzle], at **27.8%**
under a plain chain-of-thought harness by Zhuang et al., and at **57.8%** when the latter
add knowledge-enhanced tree-search reasoning[@zhuang2025treesearch] — so numbers across papers are not directly comparable; we
therefore fix and release a single, pre-registered, RDKit-InChIKey protocol with
bootstrap CIs. **(iii) A recall/verification
decomposition:** existing *LLM* benchmarks report a single aggregate score, whereas we
factor performance into generation recall and verification precision and show *where* the
task is lost. The idea of separating these two stages is not new — it is structural to
CASE, where the generator's output set and the ranker's ability to order it have always
been distinct objects[@elyashberg2015case] — and that is the point of importing it: it is
the natural frame for a system whose generator is a language model rather than an
exhaustive enumerator, and no LLM elucidation benchmark had applied it. What we find is
that the decomposition is stable under every perturbation we could run: four Claude
models, a second chemical domain, and four different verifiers all stay recall-bound
([@sec:model-comparison-benchmark-ranks], [@sec:domain-case-study-battery], [@sec:non-llm-verifiers-deterministic]). It is not tested outside the Claude family ([@sec:limitations]).

**Computational NMR for structure validation.** Our forward-verification method is
the LLM analog of a workflow chemists already trust: assign a structure by computing
the spectrum each candidate *would* give and matching it to experiment. In solution,
this is the DP4 / DP4+ probabilistic framework over GIAO-DFT shifts[@smith2010dp4; @grimblat2015dp4plus]; in the
solid state it is **NMR crystallography**, where GIPAW-computed shifts adjudicate
between candidate structures[@pickard2001gipaw; @ashbrook2016nmrcryst]. We replace the quantum-chemical predictor with a
forward LLM, trading accuracy for zero setup cost, and inherit the same core
principle — *verification by forward prediction is easier than inverse generation*.

The loop is older than either. **Computer-assisted structure elucidation** (CASE) has
generated candidates from spectral constraints and ranked them by predicted-versus-observed
agreement since the 1990s, and it works: expert systems of this kind have resolved
structures their authors called undecipherable and have overturned published
assignments.[@elyashberg2012case; @elyashberg2015case] Our decomposition is best read as
asking where an LLM sits inside a workflow chemists have used for thirty years — the
generator, in CASE, is a strict structure enumerator whose recall is exhaustive by
construction, which is exactly the axis on which we find the LLM weak.

**The generate-and-forward-verify loop is not ours, and its best instantiation
corroborates our diagnosis.** **NMR-Solver**[@jin2025nmrsolver] builds the same loop
without any LLM: it retrieves and fragment-recombines candidates, then ranks them by
¹H/¹³C shifts forward-predicted with NMRNet (¹³C MAE 1.098 ppm) against the observed
spectrum. On ~450 experimental literature spectra with the formula supplied it reports
**52.89% top-1**, well above our 28.4%. We do not claim the loop as a contribution;
[@sec:forward-verification-elucidation] asks a different question — *how much of the remaining error is generation and how
much is verification* — and answers it by decomposition ([@sec:result]) rather than by building
a better solver. The comparison is in fact the sharpest external evidence for our
central mechanistic claim: NMR-Solver's predictor is roughly twice as sharp as the
~2 ppm LLM forward-predictor whose resolution [@sec:method] identifies as the binding
constraint, and it converts that sharpness into roughly twice the top-1. That is what
our [@sec:non-llm-verifiers-deterministic] ablation predicts and what [@sec:method]'s separability measurement implies.
**NMRAgent**[@fang2026nmragent] is the closest LLM-agent counterpart, coupling spectral
tools to a knowledge graph and validating on newly isolated natural products; it is
complementary to our aim, which is measurement of an off-the-shelf model rather than a
best-effort system.

---

## The IRexp dataset {#sec:irexp-dataset}

### Motivation {#sec:motivation}

**What an IRexp record is.** Each record is a **band list** — the peak positions in cm⁻¹
that an author transcribed into the text of a paper (e.g. "IR (KBr): 3373, 3045, 2914,
1664 cm⁻¹") — together with the ¹H/¹³C shift lists reported alongside it and, where
resolvable, the compound's 2D structure. **IRexp contains no absorbance traces.** This is
the form in which experimental IR is overwhelmingly *published*, and it is the form a
language model consumes, but it is a different object from a digitised spectrum and the
two should not be counted against one another.

Open experimental IR is scarce *in a redistributable, ML-ready form*, and the existing
resources divide into two kinds that are not directly comparable.

*Digitised spectra (absorbance traces).* The largest freely downloadable collections are
the NIST WebBook[@nist_webbook] (~16k IR spectra) and the Chemotion electronic-lab-notebook
deposit[@chemotion2024] (~2k). The AIST SDBS[@sdbs] is larger (~54k FT-IR, all
structure-linked) but is *view-only*: it caps downloads at 50 spectra/day, forbids
commercial use, and ships no permissive licence or bulk export, so it cannot be used to
train or redistribute open models at scale. Commercial libraries (e.g. Wiley KnowItAll,
~10⁵ spectra) are larger still but closed. **On this axis IRexp is not the largest
resource, and does not compete: SDBS alone holds more structure-linked spectra than IRexp
holds structure-linked band lists.**

*Band lists.* Against text-derived peak-list resources, no large, permissively-licensed,
structure-linked, bulk-reusable IR collection existed. IRexp fills that gap, and to our
knowledge is the largest *openly redistributable* collection of experimental IR **band
lists** by record count. The claim is scoped to that object type deliberately; the
contribution is redistributable scale in the published-data modality, not a spectral
library.

### Construction {#sec:construction}

A per-compound IR band list, together with co-reported ¹H/¹³C NMR, follows a
remarkably stable textual convention in the experimental sections of organic
chemistry papers. Mining that convention is a mature idea — ChemDataExtractor
established the general toolkit for pulling chemical records out of primary
literature[@swain2016chemdataextractor] — and what we add is a pipeline specialised to
the *IR band list*, the modality those tools have largely passed over, together with
the paired NMR and a resolved structure. We exploit this with a browser-free
harvesting agent:

- **Discovery.** Open-access primary literature is enumerated through the NCBI
  E-utilities and harvested in bulk from the PMC Open-Access Subset[@pmc_oa] on AWS S3
  (plain HTTPS, no anti-bot, fully redistributable CC-BY content), supplemented by
  the Chemotion FT-IR deposit (RADAR4Chem, CC-BY-SA-4.0).
- **Extraction.** A deterministic parser segments experimental text into
  per-compound records and extracts IR wavenumbers and ¹H/¹³C shift lists, with
  quality gates that reject instrument scan-range artefacts and prose
  false-positives (band-list density, ≥4 bands, plausible 400–4000 cm⁻¹ window).
- **Structure resolution.** In-text IUPAC names are converted to SMILES with OPSIN[@lowe2011opsin],
  canonicalised with RDKit[@landrum_rdkit] (InChIKey, SELFIES[@krenn2020selfies]), with a PubChem[@kim2023pubchem] fallback for
  trivial/natural-product names. A key engineering finding was that the dominant
  open-access main-text convention labels compounds with *letter-prefixed* series
  labels (e.g. "…carbothioamide **(B1)**:") rather than the digit-first "(3a)" of
  supporting-information sections; capturing these and cleaning narrative/PDF
  artefacts before resolution raised structure coverage from 24% to **35%**.

The pipeline is browser-free by design. This is not an anti-bot bypass — the bulk
corpus is fully open — but a throughput choice: plain HTTP from a bulk corpus
parses at hundreds of papers per second, which is what makes a 10⁵-scale harvest
feasible where a per-page browser driver (as used to build prior 10³-scale sets)
is not.

### Contents and licensing {#sec:contents-licensing}

**Table {#tab:irexp-dataset-contents-provenance}. IRexp dataset contents and provenance.**

| field | value |
|---|--:|
| experimental IR band-list records | **121,233** |
| …co-reporting ¹H and/or ¹³C NMR | 87,075 (72%) |
| …with a resolved 2D structure | **43,060 (35.5%)** |
| …of these, with ¹H and/or ¹³C NMR | **40,702** |
| …of these, with both ¹H and ¹³C (full quadruples) | **33,201** |
| | |
| *by provenance:* author-transcribed from PMC-OA text (CC-BY) | 119,345 |
| *by provenance:* peak-picked from Chemotion ELN deposits (CC-BY-SA) | 1,888 |

Both pools are stored in the same band-list form, but they are not the same object and
we keep them separable. The PMC pool is transcribed from the experimental section of a
paper and carries a median of 9 bands per record; the Chemotion pool derives from
deposited spectra and, being peak-picked rather than author-selected, carries a median of
39. Users training on band density should treat the pools separately. The discriminator is
each record's `source_doi`: Chemotion records carry the RADAR4Chem prefix `10.22000`, PMC
records a `PMC:` accession. The released file has no separate `license` column, so
`scripts/split_license_pools.py` performs the split and stamps each record with its
licence.

**Extraction fidelity is measured, not assumed.** Because every record cites its source
accession and PMC is open, transcription can be checked directly. On a seed-fixed random
sample of 60 PMC-sourced records (`scripts/audit_extraction.py --n 60 --seed 0`), we
re-fetched each source article and asked whether every recorded wavenumber appears in that
article's text: **560/560 bands and 60/60 records were confirmed** (Wilson 95% CI 99.3–100%
and 94–100% respectively). This bounds *transcription* error — hallucinated, mis-parsed or
unit-mangled values — at under 1% of bands. It does **not** measure whether the parser
found every IR string in every paper, which is a recall question that requires human
reading; that manual audit is prepared but not yet run ([@sec:limitations]). The audit record is released
at `data/audit/extraction_audit.json`.

A structure-complete split, **`irexp_resolved`** (43,060 records, 100%
structure-linked), is the training-/benchmark-ready subset and is ~6× the
6,833-molecule set used to train Spectro[@chacko2024spectro] ([@sfig:dataset]). Every record is
DOI-/accession-traceable, and re-resolution is additive and content-keyed, so the dataset
can be re-enriched with better name-to-structure tooling without re-mining the literature.

---

## Benchmark design (IRSpectra-Bench) {#sec:benchmark-design-irspectra-bench}

From `irexp_resolved` we draw **IRSpectra-Bench**, 194 blind elucidation problems.
Each problem presents the **molecular formula** (as from HRMS), the **IR band
list**, and the **¹H and ¹³C shift lists** (with multiplicities and J-couplings
where reported), and asks for the structure. No name, SMILES, or hint is given.
Every main-round ground-truth structure is **spectrally validated** by an automated RDKit
consistency check (¹³C peak count vs symmetry-unique carbons, molecular-formula
match, SELFIES round-trip), excluding records with merged or incomplete spectra
(6/140 in the main round, leaving 134). The exclusions are itemised rather than asserted:
five report more ¹³C peaks than the structure has carbons (R03 28>24, R14 11>8, R65 26>18,
R67 23>16, R131 34>17 — merged or contaminated spectra) and one is too sparse to
constrain (R82, 5 peaks for 22 symmetry-unique carbons). The filter is deterministic and
runs over all three rounds in `scripts/validate_benchmark.py`, which regenerates every
`clean_qids.json` from the released questions and answers, so the cohort behind the
headline number is reproducible rather than a shipped artifact.

The filter tests ¹³C against the carbon count but does not gate on ¹H, and we report what
that leaves. In **13 of the 194** retained records the total reported ¹H integral exceeds
the hydrogen count of the reference structure — extra signal from residual solvent,
water, exchangeable protons or a reported rotamer mixture. The audit prints these as a
diagnostic rather than excluding them, because the cohort was fixed in advance and
re-filtering it post hoc on a criterion chosen after seeing the results is precisely the
degree of freedom a benchmark should not take. Instead we report the sensitivity: dropping
all 13 moves the headline from **28.4% to 29.3%** (53/181), a shift of +0.9 points that
leaves every conclusion in this paper unchanged. Readers who prefer the stricter cohort can
regenerate it from the diagnostic. The 60 compounds of the controlled rounds are
retained as fixed, pre-registered sets for the difficulty and within-compound controls,
with the same self-consistency audit reported separately rather than used to exclude
(57/60 pass; [@sec:limitations]).

**Difficulty is a declared property of the compound, not a post-hoc label.** Problems are
stratified by RDKit ring analysis: a compound is **simple** iff it has at most two rings
(a single ring or two separate ring fragments), no fused/spiro/bridgehead system, and ≤22
heavy atoms; every other compound — any fused/spiro/bridged or ≥3-ring system, **or** more
than 22 heavy atoms — is **complex** (98 simple / 96 complex). The criterion is exhaustive
by construction: nothing falls between the two classes, and the 23–24-atom band (13
compounds) is classed complex on size alone. Nor is the 22-atom threshold load-bearing —
sweeping it from 18 to 26 moves the simple-minus-complex top-1 gap only between 36 and 40
points (39.6 at the released value), so the separation is a property of the compounds
rather than of where the line was drawn (`scripts/difficulty_sensitivity.py`). This binary
axis is distinct from the continuous size gradient of [@sec:headline-performance], which bins by heavy-atom count
(≤15 / 16–25 / >25). InChIKey de-duplication is applied across all rounds to prevent
leakage.

**Scoring is mechanical.** A prediction is *correct* if its RDKit InChIKey
connectivity layer (first 14 characters) matches the reference — i.e. we score
*constitution* (atom-and-bond connectivity); stereochemistry is reported separately.
This is a deliberate floor: a candidate with the correct constitution but wrong
stereochemistry counts as correct. We report the strict alternative rather than assert
it is immaterial. Scoring the *full* InChIKey (stereochemistry-sensitive) gives
**21.1% top-1 and 25.8% recovered** (41/194 and 50/194), against 28.4% / 33.5% at the
connectivity layer — 7.3 points lower, so the choice of layer is not immaterial and the
constitution figure should be read as an upper bound on full-stereochemistry accuracy.
We nevertheless take constitution as the headline metric because 1D ¹H/¹³C/IR rarely
fixes absolute configuration, so a stereochemistry-aware score is not well-posed from
the given data: only 10.3% (20/194) of benchmark answers carry a *defined* (assigned
R/S) stereocentre, and a model is penalised there for information the prompt never
contained. Both numbers are produced by `scripts/score_main.py --stereo`.

**Metrics.** We report five quantities. **Top-1 (exact constitution)** is the fraction
of compounds whose single best-ranked candidate matches the reference at the InChIKey
connectivity layer. **Recovered (top-3)** is the fraction for which the reference
appears among the up-to-three ranked candidates returned (matching the lenient
"recovery" protocol of ref. [@kamber2026chemist]). Where this paper writes *recovery* it
is always reporting another study's metric under that study's own name; our own quantities
are always named **recovered (top-3)**, **generation recall** and
**conditional-on-recall precision**. **Generation recall** is the fraction for which the
reference is present in the candidate pool *before* re-ranking — the ceiling any verifier
can reach. Recovered (top-3) and generation recall share the same denominator (all
compounds) and differ only in which candidate set is searched: the up-to-three returned,
versus the full pool. They therefore coincide wherever the pool is the returned three,
which is everywhere except the generate-wide arm of [@sec:generate-wide-testing-recipe], where the pool is larger. The
denominator changes only for conditional-on-recall precision, which is taken over
recall-positive compounds alone. **Conditional-on-recall precision** is the verifier's hit rate over
recall-positive compounds only, isolating verification quality from generation. The
forward verifier ranks candidates by a symmetric **chamfer distance** between predicted
and observed ¹³C peak sets (for each predicted peak, the distance to its nearest
observed peak, summed, and symmetrically for each observed peak; lower is better, with
no equal-count requirement). We also report Morgan(2, 2048)[@rogers2010ecfp] Tanimoto as a graded
"right scaffold/family" signal. CIs are bootstrap 95% over compounds; model-vs-model
differences use McNemar's exact test with Holm correction.

**Solvers are LLM agents run under a consumer subscription.** A frontier LLM (Claude
Opus) is invoked as an independent sub-agent per batch of problems; agents are
closed-book — configured with no web/tool access beyond an RDKit formula check and no
access to ground truth, verified by grep-auditing their task transcripts at run time
(audit logs available on request; the committed artefacts are the parsed per-compound
predictions). Running under a subscription rather than a metered API is what makes the
benchmark free to re-run: reproducing the headline number costs no API credits.

Adherence to the supplied formula is high but imperfect: 91.3% (115/126)
of forward-verification candidates match the given molecular formula exactly (100% of
true structures, 89.6% of decoys), and 76.6% across the full top-3 pool — a residual
generator error orthogonal to regiochemistry.

That adherence is **not uniform across rounds**, and the two figures above come from the
better-behaved ones, so we give the breakdown rather than let a reader carry either
number across. On top-1 answers it is 95.0% (38/40) in the v3 round and 90.0% (18/20) in
the v2-control, but **77.6% (104/134) in the headline main round** — which is to say the
solver returns a structure of the wrong composition, in violation of a constraint it was
explicitly handed, for about one main-round compound in five. Those answers are scored as
misses like any other, so this inflates nothing; it does mean the formula check described
above was not equally effective in every round, and the main-round arm should be read as
the weakest-constrained one. `scripts/analyze_misses.py` regenerates the breakdown.

---

## How well do LLMs elucidate real structures? {#sec:well-llms-elucidate-real}

### Headline performance {#sec:headline-performance}

Solver agents work blind from formula + IR + ¹H + ¹³C and return up to three ranked
candidates. Each agent handles a small batch of problems in a bounded context that is
reset between batches (2–12 compounds per context in the released run; see
`data/benchmark_main/raw/`), rather than one long context over the whole benchmark —
the arm [@sec:methodology-dominates-within-compound] shows matters. Over the full
**194-compound benchmark** (134 spectrally-validated compounds + the 60 from the
controlled rounds), with bootstrap 95% confidence intervals:

**Table {#tab:headline-elucidation-performance-irspectra}. Headline elucidation performance on IRSpectra-Bench (n=194)**, overall and by difficulty stratum, with bootstrap 95% CIs.

| metric | overall (n=194) | simple (n=98) | complex (n=96) |
|---|--:|--:|--:|
| top-1 exact constitution | **28.4%** [22–35] | 48.0% [39–57] | 8.3% [3–15] |
| recovered (within top-3) | 33.5% [27–40] | 54.1% [44–63] | 12.5% [6–20] |
| scaffold-level (best Tanimoto ≥ 0.45) | 56% | 73% | 39% |
| mean best Tanimoto | 0.59 | 0.73 | 0.45 |

As a cohort-robustness check, restricting the controlled rounds to their spectrally-clean
subsets as well (134 main-clean + 57 controlled-clean = 191 strictly-validated compounds)
leaves the headline unchanged: top-1 **28.8%** (95% CI 23–36), recall 34.0%, with simple
49.0% / complex 8.4% — within ~1 point of the n=194 figures on every metric shown, with
fully overlapping intervals, so the asymmetric inclusion of the pre-registered controlled sets does not
drive the result.

The gradient is sharp and the intervals are tight. The 48%→8% simple→complex
separation ([@fig:fig1-difficulty]) confirms the benchmark is discriminating across a realistic
difficulty range, and accuracy falls monotonically with molecular size in step with
it — top-1 **60.5%** for ≤15 heavy atoms, 28.3% for 16–25, and **7.0%** above 25
([@sfig:size]). The model recovers molecular formula and functional groups reliably and the
scaffold often (best Tanimoto ≥ 0.45 for 56% of compounds), but the exact constitution
far less often.

![Top-1 and recovered accuracy on IRSpectra-Bench by difficulty (all / simple / complex, n=194), with bootstrap 95% confidence intervals. The benchmark separates a realistic difficulty range: simple targets are solved four to six times as often as complex ones on both metrics.](docs/figures/fig1_difficulty.png){#fig:fig1-difficulty}

What a failure actually looks like is measurable rather than a matter of impression, so
we measured it over all 139 top-1 misses (`scripts/analyze_misses.py`). **76.6% are
constitutional isomers of the true structure** — exactly the right atoms, assembled
wrongly — against 23.4% with the wrong molecular formula outright. The composition is
usually right; the connectivity is not.

It is tempting to compress that into "the model gets the regiochemistry wrong", and the
data do not support the compression. Only **22.6%** of misses
share the true Murcko scaffold, i.e. are genuine positional errors of the kind "*which*
ring position the substituent occupies", and just 2.9% reach Tanimoto ≥ 0.85; the median
Tanimoto between an isomeric miss and the truth is 0.39. So regiochemistry in the strict
sense accounts for roughly a fifth of failures, not the bulk of them — most isomeric
misses are more substantial rearrangements of the same atoms. Both facts point the same
way about 1D data (near-degenerate ¹H/¹³C shifts under-determine connectivity, which is
why 2D experiments such as HMBC and NOESY exist), but the honest statement is *wrong
connectivity at the right composition*, with strict regiochemistry a well-defined
minority of it.

### Reconciling with prior reports {#sec:reconciling-prior-reports}

Our 28% top-1 sits far below the ~100% on "simple" molecules reported, in a
non-peer-reviewed company white paper, for the same model class.[@kamber2026chemist] Because that figure
has not been independently scored, we reconcile it against the *peer-reviewed* record
(the MolPuzzle benchmark[@guo2024molpuzzle] and its re-scorings[@zhuang2025treesearch], and the trained baselines[@chacko2024spectro; @ottomano2025nmiracle]) rather
than treating it as settled. Three methodology and scoring choices differ between that
report and ours, each in the direction that would raise a reported number; we can name
them but not apportion the gap between them, so we do not claim a decomposition:

- **Difficulty.** "Single ring" by ring-count is not "easy": our simple stratum
  includes, e.g., a hexasubstituted benzene whose regiochemistry has many
  realisations. A low ring count is therefore no guarantee of an easy problem — though
  a high one is a strong difficulty signal, since ≥4 rings appear in 38% of
  recall-negative compounds against 3% of recall-positive ([@sec:generate-wide-testing-recipe]). Ring count bounds
  difficulty from below, it does not proxy for it.
- **Scoring.** Prior work counts a recovery if the reference appears among three
  ranked candidates over three independent runs; we report single-run top-1 and
  top-3.
- **Hints.** Prior hard targets received the starting-material SMILES, which fixes
  most of the scaffold; we give no starting material. We do supply the molecular
  formula, which is itself a real constraint — [@sec:model-reading-spectra-formula] measures what it is worth alone
  (5% top-1 with the spectra masked) — so our setting is *less* hinted than that
  comparison but more hinted than the formula-free generative baselines discussed
  below.
- **Curation.** Prior compounds were hand-selected; ours are scraped and unfiltered
  for solvability.

On a like-for-like easy/hinted/lenient setup the numbers rise; on the realistic,
hint-free, scraped regime, ~28% is the honest figure.

**Versus trained models — a bound, not a leaderboard.** A like-for-like comparison
against specialised trained models is not available: no system has been scored on an
identical test set, and published numbers differ in the three respects that most move
the score — spectrum realism (simulated/curated vs. real), hints, and how "exact
match" is defined. Most trained baselines report their accuracy
*in-distribution on simulated spectra*, though not all: Alberts et al. reach 63.8% top-1
on **experimental** NIST gas-phase IR with the formula supplied[@alberts2025benchmarks],
a genuinely real-spectrum result we do not discount — its test set is a curated
single-instrument gas-phase library of **6–13-heavy-atom** molecules rather than
heterogeneous literature-reported band lists, and its input is IR alone,
but it is experimental data and the number stands. The two evaluations barely overlap:
our compounds span 8–60 heavy atoms (median 20) and only **15 of 194 (8%)** fall inside
their 6–13 window. Against our own ≤15-heavy-atom stratum (60.5%) their 63.8% is a
near-tie; the divergence is a property of molecular size, which is exactly what [@sec:headline-performance]
measures and what an evaluation capped at 13 heavy atoms cannot see.

The multimodal systems — those conditioning on IR *and* NMR, as we do — report higher
numbers still, and each on data of its own making. Spectro (¹H/¹³C/IR→SELFIES, 6,833 molecules)
reports **93%** overall test accuracy trained jointly with its IR vision model and
**82%** with fixed embeddings — but on a 1,366-molecule held-out split
whose IR is plotted from reference data and whose NMR is software-*predicted*, not
experimental[@chacko2024spectro]; and NMIRacle, which conditions jointly on IR+¹H+¹³C,
reports 48% top-1 / 66% top-15 exact-SMILES recovery — again on held-out
molecules from a *simulated* corpus drawn from the training distribution (an 8:1:1
split of the ~790k-molecule simulated set of Alberts et al.), a limitation its authors
state themselves[@ottomano2025nmiracle]. We measure
28.4% top-1 (33.5% top-3) on the full n=194 benchmark — rising to 29.9% with forward
verification over that same full benchmark ([@sec:forward-verification-elucidation]) — on **blind, real,
literature-mined experimental** spectra of out-of-distribution compounds.

One asymmetry runs the other way and must be stated, because it cuts against us.
NMIRacle takes **no molecular formula**; its authors explicitly count "assumptions of
strong prior information, such as chemical formula or molecular scaffold" among the
limitations of prior work. We *do* supply the formula ([@sec:benchmark-design-irspectra-bench]), which is a substantial
constraint — it fixes composition and, as [@sec:model-reading-spectra-formula] shows, alone accounts for 5% top-1. So
the two settings differ on two axes at once and in opposite directions: our spectra are
real and out-of-distribution where theirs are simulated and in-distribution, but their
input is strictly harder than ours. Neither number bounds the other. These are
not comparable as a leaderboard; read only as a *bound on the simulated-to-real gap*, the
contrast suggests that high in-distribution accuracies substantially overstate
real-world performance — the same gap we document for the LLM above. The instability
of the metric itself reinforces the caution: the same ~40× MolPuzzle swing documented in
[@sec:related-work] (GPT-4o: 1.4%[@guo2024molpuzzle] to 27.8% to 57.8%[@zhuang2025treesearch], method- and harness-dependent) bounds how much weight any
single unaudited near-100% claim[@kamber2026chemist] can bear.

### Methodology dominates: a within-compound control {#sec:methodology-dominates-within-compound}

The same 20 molecules were solved two ways: (a) by a single LLM context handling
all of them sequentially with no tools, and (b) by four independent agents of five
compounds each, with RDKit formula-checking — i.e. bounded, reset contexts. On the *identical* compounds, **recovered (top-3)** rose from
**5% to 15%** (1/20 → 3/20) and top-1 from 0% to 15% (0/20 → 3/20), with zero sample
confound. Because [@sec:benchmark-design-irspectra-bench] pins McNemar's exact test for paired comparisons we apply it here
too, and it does not reach significance: the top-1 arm is necessarily nested (arm (a)
solved none) at b=0, c=3, giving **p=0.25**, and the recovered arm reaches at best
**p=0.5**. The 15% point estimate carries a Wilson 95% CI of roughly 5–36%. This is
therefore a directional within-compound demonstration, not an established multiplier, and
we do not claim the 3× as a measured effect size. Small rounds also swing widely (15–40% across n=20–40 draws), which is
why the headline is the full **194-compound** figure (28.4% top-1, 95% CI 22–35)
rather than any single round. The practical lesson has to be stated at the strength the
evidence supports, which is weaker than the point estimate invites: bounded,
frequently-reset contexts with tool access appear to raise measured performance, in a
direction consistent across both arms but **not established in size** at n=20 (p=0.25).
Read that way it still plausibly explains *part* of the gap to optimistic prior reports,
whose per-problem API calls implicitly used method (b) — but it is a hypothesis about
that gap, not a quantified contribution to it.

### Model comparison: the benchmark ranks capability (and separates the extremes) {#sec:model-comparison-benchmark-ranks}

A benchmark is only useful if it separates models. We therefore solved a fixed
24-compound subset blind with four Claude models spanning a wide capability range,
including the newest (Fable 5), under one prompt, one scorer and one candidate budget
([@fig:fig5-models], [@tab:four-model-comparison-fixed]).

One asymmetry in that protocol must be disclosed, because [@sec:methodology-dominates-within-compound] shows the variable it
concerns has a large effect. The three comparison models each solved the 24 compounds as
four six-compound contexts, whereas the Opus column reuses the headline run, in which
those same 24 items were packed as one six-compound and two twelve-compound contexts.
Context packing is exactly the factor [@sec:methodology-dominates-within-compound] measures at 5%→15%, so the Opus point estimate
is not strictly protocol-matched to the other three and, if anything, is the arm
handicapped by longer contexts. This does not affect the nesting or the Fable-vs-Haiku
contrast, but a clean re-run of the Opus arm under four six-compound contexts is the right
fix and is listed as outstanding in `docs/MODELS.md`.

![Four-model comparison on a fixed 24-compound subset, solved blind under one protocol: Fable 5 46% > Opus 25% > Sonnet 21% > Haiku 0% top-1. The outcomes are strictly nested — each stronger model solves a superset of the weaker one's compounds — so the benchmark is capability-sensitive, but at n=24 it is underpowered to separate adjacent models ([@sec:model-comparison-benchmark-ranks]).](docs/figures/fig5_models.png){#fig:fig5-models}

**Table {#tab:four-model-comparison-fixed}. Four-model comparison on a fixed 24-compound subset** under the identical blind protocol.

| model | top-1 | recovered | top-1 95% CI |
|---|--:|--:|--:|
| Claude Fable 5 | **46%** | 54% | [25, 67] |
| Claude Opus | 25% | 29% | [8, 42] |
| Claude Sonnet | 21% | 25% | [8, 38] |
| Claude Haiku | **0%** | 4% | [0, 14] |

CIs are bootstrap except Haiku's, which is the Clopper–Pearson exact interval for 0/24
(the percentile bootstrap is degenerate at a boundary count of zero).

Three signals matter here. First, the four models rank in **monotonic capability
order**, and the outcomes are **strictly nested** (Haiku ⊂ Sonnet ⊂ Opus ⊂ Fable —
each stronger model solves a superset of the compounds the weaker one does), with the
smallest **floored at 0% exact** (4% recovered) on the same problems — so the
benchmark is **capability-sensitive** and not a coin-flip. The nesting makes the
*ranking* robust, but at n=24 the subset is **underpowered to separate adjacent
models**: by McNemar's exact test only the Fable-vs-Haiku gap survives
multiple-comparison correction (Holm-adjusted p=0.006); the Fable-vs-Opus gap is not
significant (uncorrected p=0.063, Holm-adjusted p=0.19), and Opus vs Sonnet are
statistically indistinguishable — the
bootstrap CIs above overlap accordingly. Second, two mid-tier frontier models agree
closely (Opus 25%, Sonnet 21%), so the recall-bound regime of [@sec:headline-performance] (top-1 in the
high-20s%) is **not an artefact of a single model**. Third, the newest model nearly **doubles** the
next-best top-1 (46% vs 25% on identical compounds; a large but, at this n,
not-yet-significant gap) yet still misses the majority — IRSpectra-Bench is **hard and
far from saturated even for the strongest model available**, with clear headroom. We
ran four Claude-family models because they are callable for free under one
subscription; a true cross-vendor sweep (GPT-, Gemini-class, open models) needs API
access we deliberately did without, but the monotonic, large capability spread makes
it unlikely the recall-bound pattern is specific to one model lineage. This is the
behaviour a benchmark needs to remain informative as models improve.

### Domain case study: battery-electrolyte chemistry {#sec:domain-case-study-battery}

Structure elucidation from spectra is the daily inverse problem of the
electrolyte-and-interphase community: the soluble decomposition products of
carbonate and sulfone electrolytes, the additives that build the
solid-electrolyte interphase, and the fluorophosphate/fluorosulfonyl species
that NMR is routinely used to assign are exactly the molecules whose
constitution must be read back out of IR and multinuclear NMR. To test whether
the recall-bound regime above holds for *this* chemistry — rather than for
organic molecules at large — we curated **IRSpectra-Bench-Electrolyte**, a
48-compound subset (eight per class as curated; two later yielded no parseable
candidate, leaving **46 scored**) of structure-resolved IRexp records selected
by substructure for the six functional families that dominate lithium- and
sodium-battery electrolytes and their breakdown products: **carbonate**
(linear/cyclic, the EC/DMC backbone), **sulfonyl/sulfonate** (sulfones,
sulfonamides, the −SO₂CF₃ motif of imide salts), **nitrile** (acetonitrile- and
adiponitrile-type high-voltage additives), **sp³-C–F** (fluorinated solvents
and additives), **phosphoryl** (phosphates/phosphonates, the LiPF₆-derived
OPF chemistry), and **glyme/oligoether** (the ether solvents and PEG linkers).
These are literature compounds bearing the *functional chemistry* of
electrolytes, drawn from the open corpus; they are **not** operando or in-cell
degradation spectra, and we make no claim that they are. They are excluded from
every other split in this paper. Each compound was solved blind under the
identical decoupled-agent protocol (Opus, closed-book, up to three ranked
candidates, RDKit only for formula/parse checks).

Performance lands in the **same broad regime as the headline benchmark** — overall
**top-1 26%, recovered 28%** (12/46 and 13/46; two compounds received no
parseable candidate; at n=46 the 95% CI is wide and overlaps the headline) —
consistent with the bottleneck being a property of the elucidation task rather than
of any one chemical neighbourhood. The recall-bound *signature* is present in the same
form: the true structure enters the candidate set for only 13 of 46 compounds, and of
those 13 the solver already ranks it first in 12, so ranking is not what limits this
subset either. We did **not** run forward-verification here, so this reproduces the
recall-bound pattern under the solver's own ranking; it does not independently reproduce
the [@sec:forward-verification-elucidation] verification-precision measurement. The per-class
breakdown ([@sfig:electrolyte]) is itself informative:

**Table {#tab:per-class-performance-irspectra}. Per-class performance on IRSpectra-Bench-Electrolyte (n=46).**

| electrolyte class | n | top-1 | 95% CI | recovered (top-3) | 95% CI |
|---|--:|--:|--:|--:|--:|
| sp³-C–F | 8 | **50%** | [22, 78] | 50% | [22, 78] |
| carbonate | 7 | 29% | [8, 64] | 43% | [16, 75] |
| phosphoryl | 8 | 25% | [7, 59] | 25% | [7, 59] |
| glyme / oligoether | 7 | 29% | [8, 64] | 29% | [8, 64] |
| sulfonyl / sulfonate | 8 | **12%** | [2, 47] | 12% | [2, 47] |
| nitrile | 8 | **12%** | [2, 47] | 12% | [2, 47] |

Intervals are Wilson score intervals for a binomial proportion, appropriate at these
counts where the percentile bootstrap is degenerate. They overlap almost completely.

At n=7–8 per class these per-class differences are within sampling noise (six-class
χ² p≈0.56; best-vs-worst Fisher exact p≈0.28), so the ordering is a hypothesis-generating
pattern rather than an established ranking. Read that way, it is chemically legible.
**sp³-C–F** centres are the easiest:
a C–F coupling fingerprint (the large ¹J/²J(C,F) splittings) localises the
fluorine and pins regiochemistry, removing exactly the degeneracy that defeats
elucidation elsewhere. **Sulfonyl** and **nitrile** are the hardest, for two
distinct reasons that recur in real electrolyte analysis: sulfur/phosphorus
**oxidation-state ambiguity** — sulfide vs. sulfoxide vs. sulfone, −SCF₃ vs.
−SO₂CF₃, the very distinctions an interphase study must make — is poorly
constrained by ¹H/¹³C shifts alone (it lives in the IR and in heteronuclei the
benchmark does not score); and nitrile-bearing targets in the corpus sit on
heavily substituted heteroaromatic cores whose regiochemistry the 1D spectra
underdetermine. This is the recall-bound failure of [@sec:headline-performance] reappearing in a
domain-specific guise, and it is precisely where the **forward-verification**
recipe of [@sec:forward-verification-elucidation] — compute the spectrum each candidate *would* give and match it to
the one observed — plays a role *analogous* to (not a replacement for) computational-NMR
/ NMR-crystallography structure validation, sharing its forward-prediction logic while
trading DFT's calibrated accuracy for zero setup cost. The subset, its per-class answers, and the scorer are released
with the benchmark.

### Is the model reading the spectra? A formula-only control {#sec:model-reading-spectra-formula}

Because every benchmark compound is mined from open-access literature, a frontier model
may have encountered it during pretraining. Benchmark contamination of this kind is a
general and well-documented hazard for LLM evaluation,[@xu2024contamination] and it is
the objection any literature-mined benchmark must answer first. The cheapest decisive
test of whether it explains the headline number is to take the spectra away. We ran the identical blind
protocol with every spectral channel masked, so the solver receives the molecular formula
and nothing else (`scripts/modality_ablation.py`, condition `formulaonly`; solvers were
barred from reading any repository file or searching the web, and RDKit was permitted only
to check that a proposed SMILES parses and matches the formula). A molecular formula does
not determine constitution, so accuracy materially above the floor would indicate recall
rather than reasoning.

The two arms were not generated at the same time, which we disclose because a companion
experiment shows this exact structure can manufacture a large spurious effect. Only the
**formula-only** arm was
freshly generated (2026-07-28); the **full-modality** comparison arm re-uses the
archived June predictions — all 60 of its top-1 answers are byte-identical to that run.
An earlier leave-one-out attempt built the same way (fresh ablated arm against archived
control) produced −IR *beating* full modality by 40 points, which is impossible and was
discarded (`docs/MODALITY_ABLATION.md`). The reason that failure does not impugn this
control is the **direction**: fresh agents reasoned harder per compound than the archived
batched run, so the bias runs *toward* the formula-only arm, and it still collapsed to
5%. A confound that works against the finding cannot manufacture it. We nonetheless flag
it, and the rule the discarded arm yielded — every condition must be generated in one
campaign, control included — is why no leave-one-out modality result appears in this paper.

**Table {#tab:formula-only-control}. Formula-only control**, paired on the same 60 compounds as [@sec:forward-verification-elucidation].

| condition | top-1 | recovered (top-3) |
|---|--:|--:|
| formula only | **3/60 (5%)** | 3/60 (5%) |
| formula + IR + ¹H + ¹³C | **14/60 (23%)** | 19/60 (32%) |

The outcomes are perfectly nested: **eleven** compounds are solved with the spectra and
not without, and **none** the other way round (McNemar exact p=0.001). Removing the
spectra removes the result.

**A second, independent control: publication recency.** The formula-only arm shows the
spectra carry the signal, but not whether memorisation contributes to the part the spectra
explain. A model can only have memorised a compound whose source paper was in its training
corpus, and older papers have had longer in more corpora — so if recall drove the headline
number, accuracy should fall with publication recency. We resolved the publication year of
the source paper for **all 194** benchmark compounds from their accessions
(`scripts/contamination_recency.py`); they span 2008–2026. Accuracy is flat: **28.6%** for
the older half (≤2020, n=112) against **28.0%** for the newer (n=82), a point-biserial
correlation between publication year and correctness of **r = −0.007**, and no monotone
trend across year buckets ([@fig:fig-contamination]b). The most recent bucket (≥2024, n=25) is in fact the
highest at 40% [23, 59].

![Two contamination controls. (**a**) Removing the spectra: with only the molecular formula the solver reaches 3/60, against 14/60 with IR + ¹H + ¹³C on the same compounds. The outcomes are nested — 11 compounds are solved only with the spectra and none only without (McNemar exact p=0.001). (**b**) Accuracy against the publication year of the source paper (n=194, Wilson 95% CIs): flat, point-biserial r = −0.007. Recall out of pretraining would predict a decline with recency; none is observed.](docs/figures/fig_contamination.png){#fig:fig-contamination}

The raw split is if anything biased *against* the newer half, because newer papers skew to
larger molecules (median 22 heavy atoms against 20) and size is the dominant driver of
lower accuracy ([@sec:headline-performance]). Stratifying by heavy-atom band removes that confound. Newer
compounds lead in the two bands that carry most of the accuracy (≤15: 64% vs 58%; 16–25:
34% vs 25%) and trail slightly in the largest band, where both are near the floor (>25:
6% vs 8%). The size-adjusted older-minus-newer difference is **−5.1 points, 95% CI [−17.2, +7.0]**
(Cochran–Mantel–Haenszel χ²=0.42, p=0.51, continuity-corrected). Its point estimate has the
opposite sign from what recall out of pretraining would produce, but the interval
comfortably includes zero — so this **bounds** any recency effect rather than demonstrating
a reversed one, and by the same standard [@sec:generate-wide-testing-recipe] applies to its own adjacent conditions we do
not read it as directional.

The 5% is not zero, and the three compounds are worth naming rather than rounding away —
individually, they do not all support the same reading:

- **C₁₅H₁₅ClF₂O₃SSi**, a 2-(trimethylsilyl)aryl sulfonate. The Si/S/Cl/F₂ composition is
  a near-unique benzyne-precursor signature and the compound is **absent from PubChem**,
  so recognition is implausible: here the formula really is close to determining.
- **C₁₃H₁₉NO₄S**, *N*-tosyl-leucine (CAS 67368-40-5). The formula strongly suggests
  tosyl + leucine, but the compound is also catalogued and common; inference and
  recall are both available.
- **C₁₇H₂₆O₃**, **[6]-paradol** (CAS 27113-22-0), a ginger natural product. This formula
  constrains very little by itself — a named natural product recovered from composition
  alone is more plausibly recognised than deduced.

So one of the three is clean chemical inference and one or two are consistent with
memorisation. We say so because the arm exists to make such cases visible, not to argue
them away, and because the bound is unaffected either way: formula-level recall accounts
for at most about a fifth of the headline accuracy on this set. Together with the recency
result, the two controls are independent and agree. Neither is a randomised experiment —
publication year is observational and the formula-only arm cannot distinguish memorisation
from inference on a near-determining formula — so we claim a strong bound rather than
exclusion ([@sec:limitations]). The control record is released at
`data/modality/formulaonly_control.json`.


### Does the diagnosis hold outside one vendor? A four-vendor replication {#sec:diagnosis-hold-outside-one}

Every number so far comes from one lineage, which [@sec:limitations] (iii) named as the most important
external-validity gap in this work. We closed it. Six non-Claude models were run over the
same 60 compounds as [@tab:forward-verification-decomposition]'s first column, under the identical blind protocol — one
fresh context per six compounds, closed-book, three ranked candidates — and the three
whose output was well-formed enough to justify it were carried through forward
verification as well.

**Table {#tab:cross-vendor-decomposition-60}. Cross-vendor decomposition on the 60-compound arm.** Recall and precision have
different denominators, so the criterion is the inequality, not a difference.

| model | generation recall | verification precision \| recall | multi-candidate only |
|---|--:|--:|--:|
| Claude Opus ([@tab:forward-verification-decomposition]) | 19/60 = 32% [21, 44] | 16/19 = **84%** [62, 94] | 10/13 = 77% |
| Grok 4.6 | 32/60 = **53%** [41, 65] | 20/32 = 62% [45, 77] | 20/32 = 62% |
| Gemini 3.7 Flash | 30/60 = **50%** [38, 62] | 22/30 = 73% [56, 86] | 22/30 = 73% |
| GPT-5.6 Sol | 25/60 = **42%** [30, 54] | 17/25 = 68% [48, 83] | 16/24 = 67% |

**The inequality holds in every arm.** Verification precision exceeds generation recall
for four independent model families, which is the decomposition this paper rests on
reproducing outside the family it was measured in. Only Claude's gap is interval-disjoint;
at n=60 the other three are directional rather than separated, and we report them as such.

Two findings sit underneath that headline and matter more than it does.

**Our own 84% was partly composition, and the cross-vendor data exposes it.** Six of
Claude's nineteen recall-positive compounds carried a single candidate, so nothing was
ranked and any verifier scores them by construction — [@sec:result] says so, but only against
itself. The newer models return three distinct candidates almost always (0–1 singletons).
Restricted to compounds where a choice actually existed, the four precisions fall in a
band: 77%, 73%, 67%, 62%. The apparent Claude advantage largely dissolves.

**Verification looks vendor-independent where generation does not.** Precision on
multi-candidate sets spans 62–77% across four families; recall spans 32–53%. That is a
sharper statement of this paper's claim than we could make from one vendor: the wall is
the generator, and the verifier is worth about the same wherever it is taken from. The
ordering also reproduces [@sec:generate-wide-testing-recipe]'s precision-loss mechanism across vendors — Grok proposes
the most candidates (32 recall-positive) and ranks them worst (62%), exactly as widening
a candidate pool costs precision within a single model.

Three of the six models beat our headline model on generation recall, Grok by 21 points.
That is not a defeat for the diagnosis; it is the diagnosis working. Recall is the movable
factor, and models a generation newer move it — while verification, the part we showed was
already strong, stays where it was.

The three weaker models are reported for completeness and excluded from the
decomposition: Composer 2.5 (20% recall) and GPT-5.6 Luna (15%) return candidates matching
the given formula only 67% and 76% of the time, and `nvidia/nemotron-3.5-lightning`
managed 2%. A recall figure from a model that cannot emit a structure of the requested
composition is not a statement about chemistry, and [@sec:headline-performance]'s scorer now prints
formula adherence beside recall so that this cannot be misread.

**Contamination was controlled, not assumed.** These runs were driven by cloud agents with
repository access, and the answer keys for these 60 compounds are tracked files. Blindness
therefore rested on an instruction. To test it, Grok re-solved all ten batches from a clone
with the answer files physically removed: recall 28/60 against 32/60, paired McNemar
**p=0.39**, formula adherence 98% against 97%. The decisive detail is not the totals but
the asymmetry — a model reading the key would solve a *superset*, and instead **four
compounds were solved only in the arm that had no key**, with 24 of 60 solved by both.
That is sampling noise between two runs of one model, not copying. Independently, on
structures the models got constitutionally right whose reference carries assigned
stereocentres — information 1D spectra cannot supply — Grok reproduced 0/3 correct
descriptors, Gemini 0/2 and GPT-5.6 Sol 0/2, where a key-reader would have copied them.

Two limits are worth stating plainly. The models were reached through a coding-assistant
harness that exposes reasoning-effort tiers, a decoding control the Claude arm never had
([@sec:methods]), so these are measurements of a model *as served* rather than of a bare endpoint —
the same class of object [@sec:methods] already concedes for our own runs. And the clean-clone control
covers Grok; Gemini and GPT-5.6 Sol rest on the stereochemistry argument and the shared
protocol. Per-model identifiers, raw replies and the control are released in
`docs/MODELS.md` and `sweep_out/`.


---

## Forward-verification elucidation {#sec:forward-verification-elucidation}

### Method {#sec:method}

The inverse direction is the model's hard, isomer-blind direction; the **forward**
direction (structure→spectrum) is its easy, accurate one.[@kamber2026chemist] Regioisomers,
crucially, have *different* forward-predicted ¹³C shifts — though, as we quantify at the
end of this subsection, by a margin far thinner than that framing suggests. We therefore
close a generator–verifier loop:

> **generate** candidate structures (inverse) → **forward-predict** each candidate's
> ¹³C spectrum, blind to the observed spectrum → **re-rank** candidates by the
> distance between predicted and observed ¹³C → return the best match.

This mirrors how a chemist confirms a structure ("if it were that isomer, C-3 would
be at ~120 ppm; we observe 135, so it is the other"), exploits the standard
principle that verification is easier than generation, and requires no training.
**[@fig:fig-mechanism]** shows the mechanism on a real benchmark pair — the picolinamide /
nicotinamide regioisomers, which the inverse task cannot separate but whose
forward-predicted ¹³C spectra match the observed one at 0.42 vs 1.30 ppm.

![Forward-verification on a real benchmark regioisomer pair. Picolinamide and nicotinamide are indistinguishable to the inverse task, but their forward-predicted ¹³C spectra are not: the true isomer matches the observed spectrum at a chamfer of 0.42 ppm against 1.30 ppm for the alternative. This is the LLM analog of the DP4 / NMR-crystallography logic, with a forward language model in place of the quantum chemistry ([@sec:method]).](docs/figures/fig_mechanism.png){#fig:fig-mechanism}

We implemented the verifier as independent LLM agents that predict ¹³C shift lists from
SMILES alone, using pure reasoning with no tools. All candidates from all compounds were
pooled, canonicalised, shuffled and anonymised, then split into fixed-size batches, so a
predictor sees neither the observed spectrum, nor the target's identity, nor which
candidates belong to the same target. Batching does not separate a target's own
candidates — in the [@sec:result] arm, 7 of 8 batches contained two candidates for some one
compound — but because the predictor never sees an observed spectrum, co-occurrence
carries no information about which candidate is correct; it can at most let the predictor
notice that two structures are isomers, which is already evident from either alone.
Predicted and observed ¹³C peak sets were then compared with a symmetric chamfer distance.

Conditional precision is 72–89%, not 100%, so the verifier also produces clear **false
positives**, and one is worth showing at the same resolution as the success. On the
2-(nitrophenyl)-2,3-dihydroquinazolin-4(1*H*)-one targets (C₁₄H₁₁N₃O₃), the forward
predictor cannot separate the *ortho*- and *meta*-nitrophenyl regioisomers: their
predicted ¹³C lie within its ~2 ppm error, and it ranks the wrong (2-nitrophenyl) isomer
first by a chamfer of 1.35 ppm versus 1.36 ppm for the true (3-nitrophenyl) one — a
0.01 ppm margin, i.e. effectively a coin flip. This is the precision-loss mechanism of
[@sec:generate-wide-testing-recipe] made concrete: when candidates are near-degenerate the cheap predictor cannot
resolve them, and it is exactly these cases — not generation failures — that a sharper
(DFT-level) or 2D-NMR-grounded verifier would need to fix.

**How thin is the margin the method works on?** The premise above deserves a
distribution rather than a worked example, so we measured the chamfer between the
*predicted* spectra of every pair of candidates proposed for the same target
(`scripts/isomer_separability.py`). For isomeric pairs — the regioisomer-like ones the
verifier exists to separate — the median separation is **1.21 ppm** (quartiles 0.84 and
1.78), and **82% of such pairs are predicted closer together than the predictor's own
~2 ppm error**. Non-isomeric pairs separate better but not dramatically (median 1.90 ppm,
53% inside the error). So the honest form of the premise is not that regioisomers are
predicted far apart; it is that they are predicted *slightly* apart, usually within the
noise, and that the ranking nevertheless recovers the right one 89% of the time when it
is present ([@sec:result]) — a real effect on a thin margin, confirmed against a derangement null
at p=0.001 ([@sec:negative-control]).

This single measurement is the quantitative root of three limits the rest of [@sec:forward-verification-elucidation] reports
separately: precision falling 84%→72% as more near-degenerate isomers enter the pool
([@sec:generate-wide-testing-recipe]), the 74% derangement chance floor ([@sec:negative-control]), and the near-degenerate ceiling that
neither the HOSE lookup nor the GNN escapes ([@sec:non-llm-verifiers-deterministic]). All three are the same fact seen from
different angles — the predictor's resolution and the isomers' spacing are of the same
order, so a sharper predictor, not a better search, is what would move them.

That is a concrete, checkable prescription rather than a gesture, because predictors of
the required sharpness already exist. Message-passing ensembles trained on large
assigned-shift corpora reach ~1 ppm on ¹³C,[@williamson2024mpnn] and coupling a graph
network to DFT-computed shielding tensors reaches 0.94 ppm[@han2024dftgnn] — roughly half
the 1.21 ppm median spacing we measure between competing candidates, where our LLM
predictor sits at or above it. A community benchmark now exists to compare such models on
common ground,[@xu2025nmrbench] alongside curated experimental shift sets for calibrating
them.[@cohen2023delta50] Dropping one into the verifier slot is the single change most
likely to move [@sec:result]'s 89%, and [@sec:non-llm-verifiers-deterministic] takes a first step in exactly that direction with a
model we train ourselves.

Conceptually this is **analogous to NMR-crystallography logic, with an LLM in place of
the quantum chemistry** — an analogy, not an equivalence: where DP4/DP4+ rank candidates
by GIAO-DFT shifts[@smith2010dp4; @grimblat2015dp4plus] and NMR crystallography adjudicates polymorphs and connectivity
by GIPAW-computed shifts[@pickard2001gipaw; @ashbrook2016nmrcryst], we rank by the shifts a forward LLM predicts. The shared
principle is *verification by forward prediction*; what we do **not** inherit is DFT's
calibrated error model. The trade is deliberate — we forgo the ≈1–2 ppm accuracy and the
rigorous, probabilistic error model of DFT (the very thing that lets DP4 emit a
posterior probability) for a predictor that runs in seconds at zero setup, and we
quantify below exactly how far that cheaper, uncalibrated verifier carries the inverse
problem.

### Result {#sec:result}

We ran the verifier over **every compound in the benchmark**: 373 deduplicated candidate
structures across all 194 targets, all of them forward-predicted blind, in shuffled and
anonymised batches, by 23 independent agents.
The first column below is the original 60-compound arm (v3 + v2-control), on which
[@sec:generate-wide-testing-recipe]–[@sec:negative-control] build; the second is the full benchmark, where the recall-conditional claim
actually lives.

**Table {#tab:forward-verification-decomposition}. Forward-verification decomposition**, on the original arm and on the whole benchmark.

| |  60-compound arm | **full benchmark (n=194)** |
|:------------------------------------------------|-----------------:|---------------------------:|
| generation recall | 19/60 (32%) | **65/194 (34%)** |
| top-1, solver self-ranking | 14/60 (23%) | 55/194 (28%) |
| top-1, **forward-verified re-ranking** | 16/60 (27%) | **58/194 (30%)** |
| | | |
| *conditional on recall* — self-ranking | 14/19 (74%) | 55/65 (**85%**) |
| *conditional on recall* — **forward-verification** | 16/19 (**84%**) | 58/65 (**89%**) |
| …single-candidate compounds within that set | 6/19 | 28/65 |
| | | |
| *multi-candidate only* — self-ranking | 8/13 (62%) | 27/37 (73%) |
| *multi-candidate only* — **forward-verification** | 10/13 (77%) | **30/37 (81%)** |

Two facts make the full-benchmark column trustworthy before its content is read. Its
self-ranking row is derived, by an independent script over the released candidate files,
from the same solver output as [@sec:well-llms-elucidate-real], and it lands on [@tab:headline-elucidation-performance-irspectra] exactly: 55/194 = **28.4%**
top-1 and 65/194 = **33.5%** recall, and the same in both strata (simple 48.0% / 54.1%,
complex 8.3% / 12.5%) — all six headline numbers re-derived, digit for digit, through a
separate code path. And of the 373 candidates, **373 were forward-predicted**: every
candidate the verifier could rank was rankable, so nothing here is a lower bound. (The
same is now true of [@sec:generate-wide-testing-recipe], whose coverage gap we also closed.)

The decomposition is the finding. **When the true structure is among the candidates,
forward verification selects it in 58 of 65 cases (89%)** — high in absolute terms and
~15 points above the 74% chance floor that [@sec:negative-control] establishes by derangement, a floor that
sits so high because the recall-positive candidate sets are small. Extending the arm from 19
recall-positive compounds to 65 did not soften the claim; it firmed it, and it moved the
[@sec:negative-control] permutation control from marginal (one-sided p=0.019) to unambiguous (**p=0.001**).

One composition detail must be stated, because it inflates every ranker equally and [@sec:negative-control]
excludes exactly these cases from its own analysis. Of the 65 recall-positive compounds,
**28 had a single candidate**, so the verifier faced no choice and any ranker — ours, the
solver's, a coin — scores them by construction. On the **37 compounds where a choice
actually existed**, forward-verification selects the true structure in **30/37 (81%)** and
the solver's own self-ranking in **27/37 (73%)**. The asymmetry the paper rests on is
unaffected: 34% generation recall against 81% verification precision is the same wall. We
report both denominators throughout and treat the 37-compound figure as the one that
measures verification.

Pooling the two arms is licensed rather than assumed. They agree on every quantity the
pooled column reports — verification precision conditional on recall (42/46 vs 16/19,
Fisher exact p=0.41), the same restricted to multi-candidate compounds (20/24 vs 10/13,
p=0.68), self-ranking on that subset (19/24 vs 8/13, p=0.28) — and even on the composition
detail above, the single-candidate fraction (22/46 vs 6/19, p=0.28). [@tab:forward-verification-decomposition] keeps them in
separate columns anyway, so a reader who prefers the original arm can read it unpooled.

Either way the margin over self-ranking remains a small, unresolved difference: seven
compounds gained and four lost, McNemar exact **p=0.55**. Quadrupling the
conditional-on-recall set did not turn it significant, and we do not claim it. The
load-bearing claim is that verification precision is high **in absolute terms** while
recall binds — not that forward-verification beats self-ranking.
The overall top-1 moves only 28%→30% because the binding constraint is **generation
recall**: the true structure was never proposed for 129 of 194 compounds, which no
re-ranking can repair.

The difficulty split sharpens where the verifier earns its keep and where it does not. On
*simple* targets the verifier converts recall almost completely (50/53, **94%**, against
self-ranking's 47/53); on *complex* targets it converts 8/12 (67%) and is **exactly tied**
with self-ranking, gaining two compounds and losing two. The ~2 ppm forward predictor
resolves the regiochemistry of tractable targets and cannot resolve the near-degenerate
alternatives that hard targets generate — the same precision ceiling [@sec:generate-wide-testing-recipe] hits from the
other direction, here visible as a clean stratification rather than an aggregate.

LLM elucidation therefore factorises into two near-independent levers: the
**verifier is already strong (89%)**; the **generator (34% recall) is the wall**
([@fig:fig-wall]). [@tab:forward-verification-decomposition] regenerates from the released artifacts via
`scripts/forward_verify_all.py`.

### Generate-wide: testing the recipe {#sec:generate-wide-testing-recipe}

The decomposition implies a recipe — *generate wide, verify by forward prediction* — a
chemistry analog of self-consistency sampling, where many independent generations are
pooled and the answer is chosen by agreement rather than from a single pass.[@wang2023selfconsistency] We
tested it directly: ten independent solver agents proposed up to **six
regiochemistry-aware candidates per compound**, pooled with the originals, and the
65 new candidates were forward-predicted and re-ranked as before. The measured
result:

**Table {#tab:generate-wide-vs-original}. Generate-wide vs original**, both on the 60-compound arm. The "original"
column is [@tab:forward-verification-decomposition]'s first column, not its full-benchmark one; wide generation was run on
this arm only, so the comparison is held to it.

| | original (60-compound arm) | generate-wide |
|---|--:|--:|
| recall (true structure among candidates) | 32% | **42%** |
| forward-verified top-1 | 27% | **30%** |
| verification precision (conditional on recall) | 84% | 72% |

Wide generation lifts recall +10 points (32%→42%, i.e. 19/60→25/60) and exact top-1
+7 points over the self-ranking baseline (23%→30%, 14/60→18/60) — equivalently +3 over
the original forward-verified top-1 (27%→30%, 16/60→18/60, [@tab:generate-wide-vs-original]) — on the same 60
compounds ([@fig:fig3-method]), with no training.

![The forward-verification inference ladder on the 60-compound arm: solver self-ranking → + forward-verification → + generate-wide, at 23% / 27% / 30% top-1. Each rung is a training-free change to inference alone. The steps are directional rather than individually resolved at this sample size — the paired tests are in [@sec:generate-wide-testing-recipe].](docs/figures/fig3_method.png){#fig:fig3-method}

The arm originally forward-predicted only **65 of
the 217** distinct new candidates, which made its top-1 a lower bound rather than a
measurement: an unpredicted candidate is assigned an infinite match distance and can
never be selected, so recall could count every candidate while top-1 benefited only from
the predicted subset. **We have since predicted all 217, and not one number moves** —
recall 42%, forward-verified top-1 30%, precision 72%, identical to three significant
figures. The bound was tight.

What the added coverage does buy is a direct view of the mechanism. On **18 of the 60
compounds the verifier abandons its previous pick for a newly-selectable candidate** — so
the extra candidates genuinely compete, and often win on chamfer distance — yet in **not
one** of those 18 does the outcome change: every switch is from one wrong structure to
another. The wide pass supplies more near-degenerate alternatives, the ~2 ppm predictor
prefers some of them, and it cannot tell them from the truth. That is the precision
ceiling of the paragraph below observed directly rather than inferred, and it is why
recall — not verification, and not prediction coverage — remains the binding constraint.
[@tab:generate-wide-vs-original] and this coverage analysis regenerate from the released artifacts via
`scripts/score_generate_wide.py` and `scripts/forward_verify_gw.py`
(`data/fverify_gw/results.txt`).

**These top-1 differences are directional, not statistically resolved at n=60.** The
14/60→18/60 improvement is a four-compound difference, and the stages are **not** nested:
going from self-ranking to generate-wide gains seven compounds and loses three, so the
paired test is McNemar exact **p=0.34** (b=3, c=7). The intermediate steps are weaker
still — self-rank→forward-verify p=0.63 (b=1, c=3) and forward-verify→generate-wide p=0.69
(b=2, c=4). Discordant counts are computed from the released per-compound outcomes by
`scripts/ladder_significance.py`. The recall gain is the better-supported effect. We
therefore read the ladder as a demonstration that the *mechanism* works and that recall is
the movable factor, not as a precise measurement of the size of the top-1 gain.

Sustaining the ladder's first step would have been worth far more than it delivers. Had
recall kept climbing at the rate the first widening bought (+10 points) while precision
held at 84%, a second and third round would put top-1 near 50%. It does not, for two
instructive reasons.
**(i) Recall plateaus at 42%** — and the compounds it plateaus on are characterised by
size and ring count rather than by exotic elements. Comparing the 65 recall-positive
against the 129 recall-negative compounds: median heavy atoms 16 vs 23, median ring count
1 vs 3, and **≥4 rings in 3.1% of recalled compounds against 38.0% of missed ones**;
nitrogen density separates them too (≥4 N: 4.6% vs 17.1%). Selenium heterocycles and the
like are memorable but marginal — Se appears in 2.3% of misses and none of the hits, and
S, F, Cl and P show no separation whatsoever. Polycyclic, nitrogen-rich, large targets
resist even six regiochemical variants; that is the pattern, and it is a mundane one
(`scripts/analyze_misses.py`). **(ii) Verification precision falls 84%→72%** as more near-degenerate
regioisomers enter the pool and the ~2-ppm forward predictor can no longer separate
them. This recall/precision tension is the honest ceiling of the training-free
approach: the recall-bound diagnosis stands, and closing the gap further requires
either sharper verification or 2D-NMR constraints, not merely more candidates.

### Non-LLM verifiers: a deterministic lookup and a learned model {#sec:non-llm-verifiers-deterministic}

[@sec:generate-wide-testing-recipe] suggests an obvious fix: swap the LLM forward-predictor for a non-LLM ¹³C predictor
with a rigorous error model. We test two, both trained on the **same nmrshiftdb2
dump**[@kuhn2015nmrshiftdb2] and both dropped into the verifier slot on the **same [@sec:result]
candidate sets** — the 60-compound arm and the full benchmark — so that only the
predictor changes.

The first is the canonical choice: a **HOSE-code[@bremser1978hose]-style lookup** (RDKit
radial-environment bins, spheres r=4→1 with a hybridisation prior fallback; 31,000
molecules, 332,595 assigned carbons; held-out MAE 3.23 ppm, median 1.73). The second is a
small **message-passing GNN** (4 layers, per-carbon ¹³C regression) trained on the identical
dump, which reaches held-out MAE 1.70 ppm (median 1.02) — roughly twice as sharp, and an
independently competent predictor. It is not a state-of-the-art one, and we do not present
it as such: purpose-built ¹³C models reach ~1 ppm from message-passing
ensembles[@williamson2024mpnn] and 0.94 ppm when a graph network is coupled to DFT
shielding tensors,[@han2024dftgnn] on benchmarks now standardised for the
comparison.[@xu2025nmrbench] Ours is deliberately modest, because the question here is
*whether the predictor slot is where the leverage sits*, and answering that needs a
predictor that differs from the lookup in method while holding data and evaluation fixed —
not the best model available.

**Table {#tab:verifier-comparison-conditional-recall}. Verifier comparison, conditional on recall**, on identical candidate sets.
Only the ¹³C predictor changes between rows.

| verifier | 60-compound arm (n=19) | full benchmark (n=65) | held-out ¹³C MAE |
|---|--:|--:|--:|
| solver self-ranking | 14/19 (74%) | 55/65 (85%) | — |
| deterministic HOSE *lookup* | 14/19 (74%) | 55/65 (85%) | 3.23 ppm |
| **learned GNN (same data)** | 16/19 (84%) | **59/65 (91%)** | **1.70 ppm** |
| LLM forward-verifier ([@sec:result]) | 16/19 (84%) | 58/65 (89%) | — |

The lookup does not help, and quadrupling the evaluation set did not rescue it: it lands
on exactly the solver's own score at both sample sizes. That tie is not agreement — at
n=65 the lookup **gains seven compounds and loses seven** against self-ranking (McNemar
b=c=7, p=1.00). It reshuffles the ranking energetically and carries no net discriminative
signal. Its diagnosis is coverage — of the 6,360 candidate carbons, only **2%** match a
training environment at the most specific sphere (r=4) and **71%** resolve only at coarse
spheres (r≤2) or fall through to the hybridisation prior, because the benchmark's exotic
chemistry (selenium heterocycles, polyaryl ketones, large polyamines) is under-represented
in nmrshiftdb2. A coarse environment cannot separate the regioisomers the verifier exists
to separate. (The same diagnostic on the 60-compound arm gives 2% and 70% over its 2,244
carbons; both regenerate via `scripts/hose_predict.py coverage`.)

The learned model, on the same data, matches and slightly exceeds the LLM verifier —
59/65 against 58/65 ([@sfig:verifier]). Its margins over the two baselines survive the larger set
and grow more credible without reaching significance: against the lookup, seven compounds
gained and three lost (McNemar exact p=0.34, from p=0.63 at n=19); against self-ranking,
five gained and one lost (p=0.22, from p=0.50). We therefore keep the same reading the
smaller set supported, now on four times the evidence and with the direction unchanged in
every pair: the two rows are *suggestive and directional*, consistent with the lookup's
failure being substantially **method** — an inability to generalise across novel
environments — rather than coverage alone, and with a cheap learned predictor being
sufficient to match the LLM without compound-specific DFT accuracy or 2D-NMR. They do not
establish it. What none of these reach is the near-degenerate-regioisomer
precision ceiling ([@sec:generate-wide-testing-recipe]/[@sec:negative-control]), where DFT-level accuracy or orthogonal 2D-NMR constraints
remain the genuine fix.

The GNN and the LLM land within one compound of each other while **disagreeing on nine**
(b=5, c=4, p=1.00) — two verifiers built on unrelated evidence, concurring in aggregate
rather than one echoing the other. The result is **generalisation, not memorisation**, and
we can now say so on the whole candidate pool rather than a sixth of it. *Exact* overlap
with the entire nmrshiftdb2 database is **2 of 364** distinct candidate structures by
InChIKey-14 — both of them *wrong* candidates on *recall-negative* compounds that never
enter the conditional analysis — and **no benchmark answer appears in the database at
all** (0/373; the 60-compound arm is 0/126, as previously reported). *Analog* overlap,
which exact matching would miss, is likewise absent: the median Morgan(2, 2048) Tanimoto
to the nearest training molecule is **0.44** and only three candidates exceed 0.80. The
load-bearing number is the last one: over the **65 true structures the verifier actually
has to identify**, the nearest training analog has median Tanimoto **0.50** and maximum
**0.81** — not one of the compounds the conditional analysis scores has a near-duplicate
in the training set. A Y-randomisation control (1,000 derangements)
places the real result above the 97.5th percentile of the chance distribution (n=19: real
84% vs mean 58.6%, 95% range 42.1–73.7%, one-sided p<0.05). Like [@sec:recall-wall-task-intrinsic], the learned
verifier is a **trained complement**, reported outside the training-free protocol.
[@tab:verifier-comparison-conditional-recall] and both leakage checks regenerate from the released artifacts
(`scripts/verifier_table.py`, `scripts/verifier_leakage.py`,
`data/fverify/verifier_table_results.txt`, `data/nmrshiftdb/gnn_c13.pt`;
`docs/VERIFIER_PROBE.md`).

### Negative control {#sec:negative-control}

**Permutation negative control (Y-randomisation analog).** A re-ranker earns the
interpretation that it exploits genuine predicted-vs-observed ¹³C agreement only if
that agreement is destroyed when the pairing is broken. Borrowing the Y-randomisation
discipline of QSAR validation, we re-paired — as a *derangement*, so no compound keeps
its own spectrum — which observed ¹³C spectrum each candidate set is scored against,
and re-ran the verifier 1,000 times. On the full benchmark, conditional-on-recall
precision falls from the true **89.2% (58/65)** to a permuted mean of **73.8%** (95% range
66.2–81.5%; one-sided empirical p=0.001, two-sided p=0.002) — the verifier acts on real
spectral agreement, not a candidate-list artefact. The same control on the 60-compound arm
alone gives 84.2% against a permuted 66.4% (one-sided p=0.019) — the same effect, and the
full-benchmark run establishes it on four times as many recall-positive compounds. The
honest caveat is the height of the chance floor: because
recall-positive compounds carry few and near-identical (regioisomeric) candidates, even a
random pairing lands on the correct structure ~74% of the time, so the verifier's genuine
margin over chance is **~15 points**, not the full 89% — real and significant, but to be
read against this high baseline.

**Confidence calibration (a negative result).** We also asked whether the chamfer
match-distance doubles as a confidence signal that would support selective prediction.
It does not. Ranking the 138 multi-candidate compounds by their chamfer margin (the gap
between the best and second-best predicted-vs-observed distance) and answering only the
most-confident fraction leaves top-1 essentially flat and non-monotonic with coverage
(22% at full coverage, 24% at 75%, 28% at 50%, 24% at 25% — neither rising nor falling
reliably as the threshold tightens).
Compounds with a single proposed candidate have no margin at all and must be excluded;
an earlier analysis that retained them produced a spurious "improvement" that was
entirely an artefact of those trivial cases. We therefore do **not** claim the verifier
distance as a calibrated abstention gauge — a sharper, DFT/2D-NMR-grounded confidence
estimate ([@sec:non-llm-verifiers-deterministic]) remains the route to reliable selective prediction.

Both controls in this section regenerate via `scripts/verifier_diagnostics.py --all`
(the full benchmark, as reported here); omitting `--all` reproduces the 60-compound arm's
figures instead.

### Is the recall wall task-intrinsic? A trained-generator probe {#sec:recall-wall-task-intrinsic}

The ceiling above is a property of *training-free LLM elicitation*; it leaves open
whether the ~42% recall plateau is intrinsic to 1D-data elucidation or specific to how
LLMs are elicited. We test this with a complementary probe — a small (~16M-parameter)
¹H/¹³C→SMILES transformer (simulated-spectra pretraining, then fine-tuned on IRexp;
ensemble of four), held **deliberately separate from the training-free protocol**. Its
candidates are filtered to the given molecular formula, pooled with Claude's, and
re-ranked by the same verifiers.

The generator supplies candidates enumeration cannot. On the 194-compound benchmark the
true structure enters the candidate pool for **54.1%** of compounds (versus 41.8% for
scaffold enumeration and 33.5% for Claude alone). Crucially, where enumeration's
near-degenerate regioisomers *collapse* the deterministic HOSE verifier
(top-1 28.4%→16.0%, the [@sec:generate-wide-testing-recipe] precision-loss mechanism), the generator's formula-correct,
¹³C-separable candidates **convert**: HOSE top-1 rises **28.4%→35.1%** (McNemar exact
p=0.015; +6.7 points, 95% CI [+2.1, +11.9]; [@sfig:generator-probe]). With the stronger LLM
forward-prediction verifier on the 60 forward-verify compounds, recall rises 42%→**57%**
(34/60) and forward-verified top-1 reaches **47%** (28/60), at 82% precision conditional
on recall (28/34).

Those last two figures are a **re-run, not a reproduction**, and the distinction matters.
An earlier pass reported 41% top-1 at 73% precision, but its forward-prediction outputs
were never deposited, so that number was unverifiable and we do not stand behind it. We
therefore re-ran the arm from scratch under the identical blind protocol — the 75
outstanding candidates forward-predicted by agents that saw the anonymised SMILES and
nothing else — and **released every prediction** (`data/fverify_gen/raw/`), so
`scripts/forward_verify_gen.py score` now regenerates all three numbers from the bundle
with no missing predictions. The re-run lands *above* the figure it replaces (47% vs 41%
top-1, 82% vs 73% precision); we report the reproducible one and flag that it was
collected later than the June solver runs (`docs/MODELS.md`). The recall arm and the
deterministic-HOSE re-rank were reproducible throughout and are unchanged.

Two controls guard against memorisation, both reproducible from the released bundle
(`contrib/generator_probe`): (i) the fine-tuning split removes every benchmark
InChIKey-14 (train∩benchmark = 0, val∩benchmark = 0), and **none of the 40
newly-recovered compounds appear in either training stage** (0/40 in simulated
pretraining, 0/40 in fine-tuning); (ii) the simulated-pretrained model alone recovers
**0/248** benchmark structures zero-shot, rising to 25% only after IRexp fine-tuning.
The IRexp data — not the architecture — is the active ingredient, and the recall ceiling
is therefore **elicitation-specific, not task-intrinsic**. We report this as a probe,
not part of the headline training-free protocol; it answers whether the wall is
breakable, not whether to abandon training-free methods.

Two published systems make this point far more strongly than our 16M-parameter probe
can, and we would rather lean on them than on ourselves. NMR-Solver reaches 52.9% top-1
on experimental literature ¹H/¹³C with the formula supplied, using a purpose-trained
shift predictor inside the same generate-and-verify loop[@jin2025nmrsolver]; and a
purpose-trained IR transformer reaches 63.8% top-1 on experimental NIST spectra in the
6–13-heavy-atom range[@alberts2025benchmarks]. Whatever bounds a training-free LLM at
28–30%, it is plainly not the task. Our probe adds one thing those results do not: it
isolates the *data* as the active ingredient (0→25% with IRexp fine-tuning, 0/248
without), which is the claim IRexp itself has to earn. (The released public split
`irexp_release/train` does *not* hold out the benchmark — it overlaps it by 117/200
InChIKey-14 — so downstream users must de-leak as in `build_exp_manifest.py`; see Data
and code availability.)



---

## Discussion {#sec:discussion}

The frontier LLMs we tested (the Claude family) are neither "solving structure elucidation"
on realistic 1D data nor failing at it. They are reliable **scaffold-level**
elucidators (best-candidate Tanimoto ≥ 0.45 for 56% of compounds, 73% of simple ones; mean
best Tanimoto 0.59) and good **verifiers** (89% conditional on recall). Exact top-1 is
throttled by candidate recall and by the regiochemical underdetermination intrinsic to 1D NMR.
The contribution of this paper is therefore best read as a **diagnosis with a bounded,
training-free improvement attached**, not as a method that solves the task.

The diagnosis is the durable half, and it held under every perturbation we were able to
apply — four Claude models, a second chemical domain, four different verifiers: the wall
is **generation recall**, not verification. Whether it holds outside the Claude family is
the open question, not a settled one ([@sec:limitations]). The improvement attached to it is real but
deliberately modest, and we measured its ceiling rather than projecting past it. Forward
verification alone moves top-1 from 28% to 30% across the whole benchmark ([@sec:result]), and
adding wide generation takes 23% to 30% on the 60-compound arm where that was run — yet
recall plateaus at 42%, verification precision falls to 72% as near-degenerate
regioisomers accumulate ([@sec:generate-wide-testing-recipe]), and the match distance fails outright as a confidence
gauge for selective prediction ([@sec:negative-control], a reported null result).

This reframes the engineering problem. Rather than training a bespoke spectra→structure model — a
target the frontier already meets at the scaffold level and that ages out each model
generation — the durable levers are (i) **open, hard, honestly scored benchmarks**
that expose specific failure modes (here, regiochemistry and recall), and (ii)
**inference-time scaffolding** (decoupled solving, generate-and-verify) that needs no
training and improves with each model. IRexp's IR modality and 2D-NMR-ready
provenance position it for the obvious next step: supplying the HMBC/COSY/NOESY
constraints that would attack regiochemistry at the source. Our trained-generator probe
([@sec:recall-wall-task-intrinsic]) sharpens the point: the recall wall is *elicitation-specific, not task-intrinsic*
— a small generator fine-tuned on IRexp lifts it (recall 42→57%) — and because that gain
comes entirely from the released data (0→25% with fine-tuning, 0/248 without), it is the
**open dataset**, not a bespoke architecture, that does the work when training does help.

**Protocol is a lever of the same order as capability.** How a problem is posed and
verified — bounded, reset contexts with tool access; generate-and-verify — moves accuracy
enough that it must be reported alongside any capability claim. We do *not* claim it
dominates capability: on the fixed 24-compound subset the model axis spans 0% to 46%
top-1 ([@tab:four-model-comparison-fixed]), a wider range than the 5%→15% protocol effect in [@sec:methodology-dominates-within-compound], and the two are
measured on different sets. The point is that a number quoted without its protocol is
uninterpretable, which echoes a recurring lesson across cheminformatics: careful pipeline
and protocol design competes with the fashionable component. The same pattern appears in
molecular property prediction, where a recent systematic benchmark reports that
learned, pretrained molecular embeddings rarely outperform classical ECFP
fingerprints once evaluation is controlled[@praski2025embeddings] — the modelling fashion underperforms the
well-engineered baseline. We read our within-compound control ([@sec:methodology-dominates-within-compound]) and
forward-verification recipe ([@sec:forward-verification-elucidation]) in the same light: the durable gains in LLM
elucidation come from honest benchmarking and inference-time scaffolding rather than
from waiting on the next, larger model. We draw this parallel narrowly and claim no
formal equivalence between the two settings.

That the bottleneck reproduces inside a single application domain
([@sec:domain-case-study-battery]: 26% top-1 on battery-electrolyte chemistry, n=46, against 28% overall) is
consistent with it being structural rather than incidental — and it makes the
forward-verification recipe directly relevant to the magnetic-resonance workflows
(electrolyte-decomposition assignment, NMR crystallography) where computing a
candidate's spectrum to confirm it is already standard practice.

For practitioners, two operational findings transfer immediately: solve each problem
in bounded, frequently-reset contexts with tool access (5%→15%, 1/20→3/20,
directional at n=20, McNemar p≥0.25, [@sec:methodology-dominates-within-compound]), and use forward-predicted-vs-observed
¹³C agreement to *re-rank* candidates, not to decide whether to trust the winner. [@sec:negative-control]
is explicit on this: match distance is a strong relative re-ranker but failed as an
absolute confidence gauge in our selective-prediction test, so it does not support
abstention thresholds.

---

## Limitations {#sec:limitations}

Several limitations of earlier drafts are now resolved with controlled experiments;
we state what remains plainly.

*Resolved.* **Extraction noise:** an RDKit self-consistency audit (¹³C peak count vs
symmetry-unique carbons, formula, SELFIES round-trip) finds **57/60 ground truths
spectrally clean**, and the metrics are unchanged on that clean subset
(self-ranking top-1 25% vs 23%, recall 33% vs 32% on the n=60 forward-verify set) — the
conclusions are not driven by scraping artefacts. **Verifier sample size:** forward
verification now runs over **all 194 compounds**, not a 60-compound subset, so the
recall-conditional claim rests on n=65 rather than n=19 and the [@sec:negative-control] permutation control
tightens from one-sided p=0.019 to p=0.001 ([@sec:result]). **Verifier precision / abstention:** the generate-wide experiment ([@sec:generate-wide-testing-recipe])
quantifies the recall/precision tension directly — verification precision is
72–89% conditional on recall and degrades as near-degenerate regioisomers
accumulate, so forward-match distance is a strong *re-ranker* but a soft
*confidence* gauge. We further tested non-LLM verifiers ([@sec:non-llm-verifiers-deterministic]), on the same extended set: a
nmrshiftdb2-trained HOSE-code *lookup* does **not** beat the LLM verifier (85% vs 89%
conditional at n=65) and ties self-ranking by exchanging seven compounds for seven, while
a *learned* GNN on the same data reaches 91% — directional in every pairwise comparison
but still not statistically resolved at n=65 (p=0.34 vs the lookup, p=0.22 vs
self-ranking), so it is suggestive
that the deterministic failure was method rather than coverage alone, not a
demonstration of it. What remains beyond all of
them is the near-degenerate-regiochemistry precision ceiling, where DFT-level accuracy or
2D-NMR constraints are still the genuine fix. **Projection:** where an earlier draft
estimated what generate-and-verify *would* reach, [@sec:generate-wide-testing-recipe] now runs it — and the measurement
(top-1 30%, recall 42%) came in below the estimate it replaces, which is reported as
found rather than adjusted.

*Independence checks.* Scoring throughout is mechanical RDKit (not LLM-judged), and
all solver/verifier runs were transcript-audited *at generation time* for zero web and
zero ground-truth access. That audit is the one part of the pipeline a reader **cannot
re-verify from the release**: the committed artefacts are the parsed per-compound
predictions, and the transcripts themselves are not deposited (they are available on
request). We state this rather than let "transcript-audited" imply an independently
checkable artefact, and note that the *outcome* of closed-book solving is separately
testable from what is released — the formula-only control ([@sec:model-reading-spectra-formula]) removes the spectra and
accuracy collapses, which no amount of web access would produce. To confirm that
the forward-verifier's measured advantage
reflects real predicted-vs-observed spectral agreement rather than leakage or a
candidate-list artefact, we ran a permutation negative control (Y-randomisation
analog, [@sec:negative-control]): re-pairing — as a derangement — which observed ¹³C spectrum each
candidate set is scored against, over 1,000 permutations, collapses conditional-on-recall
precision from 89.2% to a chance mean of 73.8% (two-sided p=0.002 on the full benchmark;
p=0.038 on the 60-compound arm alone) — the signal weakens
to the chance floor under label-shuffle, as a correctly isolated blind evaluation requires. A second Claude model (Sonnet)
re-solved a 12-compound subset under the identical generate-wide protocol and was comparably
recall-bound (recall 33% vs Opus 42% on those compounds), consistent with the recall bound
being a property of the task rather than of one model. As this is within the Claude family,
it speaks to model-instance robustness, not cross-vendor generality.

*Remaining.* **(i) Pretraining contamination is bounded, not excluded.** Every benchmark
compound was mined from open-access literature, so a frontier model may have encountered
it in training. The formula-only control ([@sec:model-reading-spectra-formula]) bounds how much of the headline number
pure recall can explain — masking the spectra drops top-1 from 23% to 5%, perfectly
nested, McNemar exact p=0.001. [@sec:model-reading-spectra-formula] examines the three formula-only successes one by
one rather than explaining them away collectively: only one (an unlisted silyl aryl
sulfonate) has a genuinely determining composition, while the other two — *N*-tosyl-leucine
and the natural product [6]-paradol — are catalogued compounds for which recall is a live
explanation. That is the control working as intended, and it leaves the bound unchanged. The second control ([@sec:model-reading-spectra-formula]) resolves the source
publication year for all 194 compounds and finds accuracy flat in it (r=−0.007), with the
size-adjusted older-versus-newer difference bounded at −5.1 points, 95% CI [−17.2, +7.0].

Two things these controls do not do. Neither is randomised: publication year is
observational, and the formula-only arm cannot separate memorisation from inference on a
near-determining formula. And we do not anchor the recency test to a *known* training
cutoff — the subscription harness does not disclose one ([@sec:methods]), so we test recency as a
continuous proxy rather than partitioning at a cutoff date. A replication restricted to
compounds published after a disclosed cutoff would settle what these bound, and remains
open.

**(ii) Human audit — prepared but not yet run.** This covers two things we have not
validated by hand: the elucidation and forward-prediction outputs, and the *recall* side
of dataset extraction (whether the parser found every IR string in every source paper).
Transcription fidelity of the records we do hold is measured and high ([@sec:contents-licensing]), but record-level
recall is not, and only reading papers can settle it. Solver and verifier are
both LLMs, so the one validation we cannot perform ourselves is an expert-chemist review
of a sample of elucidations and forward predictions. We have therefore **built and
frozen** a blinded, pre-registered audit package — a difficulty-stratified 30-compound
elucidation panel plus seven ranking-only compounds (13 of which carry the true structure
alongside a real choice), rendered candidate structures, a separate withheld answer
key, and a mechanical scoring sheet — released at `data/audit/` with its protocol at
`docs/EXPERT_AUDIT_PROTOCOL.md` (regenerable via `scripts/make_audit_sample.py`),
designed to test the two load-bearing claims (what a miss actually is, [@sec:well-llms-elucidate-real]; forward
verification is a trustworthy re-ranker, [@sec:forward-verification-elucidation]). **We have not yet run the panel**; until
expert results are in, those claims should be read as machine-validated (RDKit
InChIKey) but not yet human-validated.

The panel's first question has since been narrowed by measurement rather than left to
judgement. [@sec:well-llms-elucidate-real] now reports the composition of all 139 misses mechanically — 76.6%
constitutional isomers, 22.6% scaffold-preserving positional errors — which replaces the
impressionistic claim the audit was built to check and, in doing so, corrected it: the
failures are predominantly *wrong connectivity at the right composition*, and strict
regiochemistry is a minority of them. What remains for a chemist is the part no
fingerprint settles: whether a formula-correct, scaffold-wrong candidate is a
*chemically reasonable* reading of the spectra or an implausible one. That is a narrower
and better-posed question than the one we started with.

**(iii) Single vendor and an underpowered cross-model comparison.** Every number comes
from one vendor's models. The headline (28.4% top-1) is a single frontier model (Claude
Opus), and the cross-model evidence ([@sec:model-comparison-benchmark-ranks]) is four **Claude-family** models on a shared
**24-compound** subset. As [@sec:model-comparison-benchmark-ranks] sets out, that comparison is underpowered: the
ranking is robust (strictly nested, weakest floored at 0%) but no adjacent gap is
established at n=24. Quantitative claims should therefore be read as holding **for the Claude family**,
The cross-**vendor** question this raised is no longer open: [@sec:diagnosis-hold-outside-one] reports the same
decomposition for Grok 4.6, Gemini 3.7 Flash and GPT-5.6 Sol on the 60-compound arm, and
verification precision exceeds generation recall in all three, as it does for Claude. What
remains is weaker than the original gap but real. Only Claude's inequality is
interval-disjoint at n=60; the other three are directional. Those models were reached
through a coding-assistant harness exposing reasoning-effort tiers, a decoding control our
own arm never had, so they measure a model as served rather than a bare endpoint. The
clean-clone contamination control was run for Grok alone. And the *headline* number
(28.4% top-1, n=194) is still a single frontier model on the full benchmark; the
cross-vendor arms cover 60 compounds.

**(iv) Domain-subset scope:** the battery-electrolyte case study ([@sec:domain-case-study-battery]) comprises
*literature compounds bearing electrolyte-relevant functional chemistry* drawn from the
open corpus — not operando or in-cell decomposition spectra — so it demonstrates
functional-class transfer of the elucidation bottleneck, not direct assignment of
authentic interphase/degradation products, which would require a dedicated operando set.

**(v) Constitution-only scoring:** correctness is judged on InChIKey connectivity, so a
correct-constitution / wrong-stereochemistry prediction is counted correct. Scoring the
full InChIKey instead gives 21.1% top-1 ([@sec:benchmark-design-irspectra-bench]), 7.3 points lower, so the headline should be
read as an upper bound on full-stereochemistry accuracy. We keep constitution as the
headline because 1D NMR/IR rarely determines absolute configuration — the 10.3% (20/194)
of targets with a defined stereocentre would be penalised for information the prompt
never carried — but a stereochemistry-sensitive benchmark would need 2D/chiroptical data.

**(vi) Single-sample scoring:** each headline compound is scored from one solver
prediction set (one decoupled run), so reported top-1/recall carry no run-to-run
(LLM-sampling) variance estimate — the bootstrap CIs reflect compound sampling only. The
generate-wide experiment ([@sec:generate-wide-testing-recipe]) pools ten independent generation passes (recall
32%→42%), indicating generator stochasticity that single-pass scoring understates.

**(vii) Chemical-space coverage:** the benchmark is drawn from open-access organic
methodology and total-synthesis literature, covering small-to-medium drug-like and
synthetic-organic space; it is **not** representative of organometallic/coordination
compounds, large biomolecules (peptides, oligonucleotides, oligosaccharides), or
stereochemistry-heavy targets, and our results should not be extrapolated to them.

---

## Methods {#sec:methods}

**Mining and resolution.** PMC-OA full text was fetched from `s3://pmc-oa-opendata`;
records were extracted with a deterministic parser and resolved with OPSIN, RDKit,
and SELFIES, with an optional cached PubChem fallback. Durable content-keyed caches
make resolution additive and restart-safe.

**Benchmark and agents.** Problems were sampled from `irexp_resolved`, stratified by
RDKit ring analysis, with cross-round de-duplication by InChIKey. The
battery-electrolyte subset ([@sec:domain-case-study-battery]) was drawn from the same corpus by SMARTS
substructure filters for six electrolyte functional classes (carbonate,
sulfonyl/sulfonate, nitrile, sp³-C–F, phosphoryl, glyme/oligoether), balanced to
eight compounds per class (48 curated; 46 scored after two yielded no parseable
candidate), excluding every compound used elsewhere, and J-enriched and spectrally
validated identically to the main rounds. Solver and
forward-prediction agents were independent Claude-Opus sub-agents invoked under a
consumer subscription; agents were instructed closed-book and audited via
automated transcript search for zero web/answer access. Scoring used RDKit InChIKey-connectivity
matching and Morgan(2, 2048) Tanimoto; forward-verification used a symmetric chamfer
distance over ¹³C peak sets. The core protocol trains no model and uses no paid API;
the two trained probes — the [@sec:recall-wall-task-intrinsic] generator and the [@sec:non-llm-verifiers-deterministic] learned ¹³C verifier — are the
only separately-trained exceptions, each reported as a complement and fenced from the
headline results.

*Models and versions.* All experiments used Anthropic Claude models via the consumer
subscription (claude.ai). The [@sec:model-comparison-benchmark-ranks] comparison spanned, in capability
order, Claude Haiku, Claude Sonnet, Claude Opus, and Claude Fable 5; the headline
benchmark ([@sec:headline-performance]) and forward-verification ([@sec:forward-verification-elucidation]) used Claude Opus. `docs/MODELS.md`
records, for each experiment, the model used, its data directory, the collection date,
the harness and tool access, and the scoring code path. Model invocations fall into three
dated windows, listed separately there because no single window covers them. Every
candidate structure behind the **headline** results — [@sec:headline-performance], [@sec:methodology-dominates-within-compound]–[@sec:domain-case-study-battery], and the candidate
pools all of [@sec:forward-verification-elucidation] re-ranks — was generated between **2026-06-09 and 2026-06-11** (UTC). The
formula-only contamination control ([@sec:model-reading-spectra-formula]) is a deliberate exception: it re-solves the same
60 compounds with the spectra masked on **2026-07-28**, generating its own candidates,
because a masked-input control is only meaningful as a fresh run; it touches [@tab:formula-only-control] alone.
Three **2026-08-07** collections forward-predict ¹³C for candidates the June run had
already produced (the [@sec:result] extension to all 194 compounds, the [@sec:generate-wide-testing-recipe] coverage-gap closure,
and the [@sec:recall-wall-task-intrinsic] re-run); none introduces a new candidate structure, and no recall number in
the paper changes. One *verified* number does: the [@sec:recall-wall-task-intrinsic] re-run supersedes a top-1 whose
original forward-prediction outputs were never deposited and are lost, and it does not
agree with the figure it replaces (47% against 41%). [@sec:recall-wall-task-intrinsic] reports the reproducible one
and says plainly that it is a re-run rather than a reproduction.
Decoding parameters are not exposed
by the subscription harness and were neither set nor recorded, so re-running reproduces
the protocol distributionally rather than exactly.

**No model snapshot can be reported, and this is a property of the protocol rather than
an omission.** The consumer harness exposes no checkpoint identifier to the caller,
announces no build changes, and records nothing about which build served a given request;
no work after the fact recovers that. Two consequences follow. `Claude Opus 4.8` is
evidenced only for the 2026-06-09 pilot, so **a mid-window build change cannot be
excluded** and we do not claim the same build served the main round two days later. And a
reader repeating these experiments will be served whatever build is then current, so
distributional agreement is the most that can be expected — exact agreement is not a
meaningful target here and we do not offer it as one. What stands in place of a pin is
everything that *is* fixed: the dated collection windows above, the frozen per-compound
outputs, and mechanical scorers that regenerate every number from them. That is the
boundary of a zero-cost subscription protocol: it buys exact reproducibility of scoring
and analysis, not of inference (`docs/MODELS.md` [@sec:discussion]).

**Reproducibility.** Every round is frozen: questions, ground-truth answers,
per-agent raw outputs, predictions, and scorer outputs are released, and the sampler,
scorer, and forward-verification harness are scripted end-to-end.

---

## Supporting Information figures

These are supplied as a separate Electronic Supplementary Information document
(`docs/paper_esi.pdf`, built by `scripts/build_pdf.py`), as RSC requires; they are listed
here for reference.

- **[@sfig:overview]** (`docs/figures/fig0_overview.png`) — study design: open multimodal data
  (IRexp) → blind, complexity-stratified benchmark → decoupled blind solving →
  forward-verification re-ranking; training-free core pipeline.
- **[@sfig:dataset]** (`docs/figures/fig4_dataset.png`) — IRexp composition: IR records →
  NMR-paired → structure-linked → full IR+¹H+¹³C+structure quadruples.
- **[@sfig:size]** (`docs/figures/fig2_size.png`) — accuracy vs molecular size (heavy-atom
  bucket); the monotonic 60%→7% top-1 gradient.
- **[@sfig:electrolyte]** (`docs/figures/fig6_electrolyte.png`) — top-1 and recovered accuracy on
  IRSpectra-Bench-Electrolyte by battery-electrolyte chemical class (n=46): sp³-C–F
  easiest (50%), sulfonyl and nitrile hardest (12%); overall 26%/28%.
- **[@sfig:generator-probe]** (`docs/figures/fig_generator_probe.png`) — trained-generator probe ([@sec:recall-wall-task-intrinsic];
  a complement, not part of the training-free protocol): candidate recall and
  deterministic-HOSE top-1 on the 194-compound benchmark for Claude / + scaffold
  enumeration / + trained generator. Enumeration's near-degenerate isomers collapse the
  verifier (28.4→16.0%) while the generator's formula-correct candidates convert
  (28.4→35.1%).
- **[@sfig:verifier]** (`docs/figures/fig_verifier.png`) — learned-verifier probe ([@sec:non-llm-verifiers-deterministic]; a
  complement, not part of the training-free protocol). (A) Conditional-on-recall top-1
  (n=65, whole benchmark) for the four verifiers: a GNN trained on the same nmrshiftdb2
  data as the HOSE lookup reaches the LLM verifier's level (91% vs 89%) where the lookup
  (85%) does not move off the solver's own ranking. (B) Why: held-out
  ¹³C MAE — the learned model is ~2× sharper (1.70 vs 3.23 ppm).

---

## Data and code availability

Everything below is in the project repository. The archival deposit — a complete frozen
snapshot of dataset, benchmark, answer keys, predictions, scripts, figure regeneration and
the expert-audit package — will carry DOI **[TODO: 10.5281/zenodo.XXXXXXX — mint on
submission]**; GitHub is the development mirror and the Zenodo record the citable version.

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
| manuscript integrity gates | — | `scripts/check_manuscript.py`, `scripts/verify_statistics.py` |

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

**Two cautions for re-users.** The public `irexp_release/train` split does **not** hold
out IRSpectra-Bench — it overlaps by 117/200 InChIKey-14 — so de-leak with
`contrib/generator_probe/build_exp_manifest.py` before training anything that will be
evaluated on the benchmark. And the held-out answer keys `data/audit/key.jsonl` and
`data/modality/key.json` are deposited but flagged *withhold from blinded reviewers*.

## Licensing and attribution

IRexp is derived from two open-access source pools and redistributed under terms
compatible with each (see `data/NOTICE`). **(a) Redistribution:** we release only
*extracted numeric data* — IR band lists, ¹H/¹³C shift lists, and resolved structures
(SMILES/SELFIES/InChIKey) — plus each record's source DOI/accession, not source full
text, figures, or PDFs. **(b) Two separable pools:** 119,345 records derive from the PMC
Open-Access Subset (**CC-BY-4.0**) and 1,888 from the Chemotion RADAR4Chem FT-IR deposit
(**CC-BY-SA-4.0**). The two are separable losslessly by `source_doi` — Chemotion records
carry the `10.22000` prefix — and `scripts/split_license_pools.py` materialises them as
two files with each record stamped `license`, so users may take the CC-BY pool alone;
any combined or Chemotion-derived release carries CC-BY-SA-4.0 to honour the ShareAlike
term. Code is released under the MIT License. **(c) Attribution:** re-users must cite
this dataset (Zenodo DOI above) and attribute the original publications via each record's
`source_doi`.

## Author Contributions

**I.Y.:** conceptualization, methodology,
software, formal analysis, investigation, data curation, visualization, writing —
original draft. **R.S.:** methodology, software, formal analysis, investigation,
validation (trained-generator and learned-verifier probes, [@sec:non-llm-verifiers-deterministic] and [@sec:recall-wall-task-intrinsic]), writing —
review and editing. **R.A.V.-H.:** conceptualization, methodology, supervision,
writing — review and editing.

## Conflicts of Interest

The authors declare no competing interests.

## Use of AI tools

This work studies a large language model, and LLMs were also used as instruments and as
writing aids; we state both roles explicitly. **As an object of study:** all reported
elucidation, forward-prediction and verification results were produced by Claude models
invoked under the protocol of [@sec:benchmark-design-irspectra-bench] and [@sec:methods] — these are the measurements the paper reports,
not assistance in producing it. **As a writing aid:** the authors used an LLM-based
coding assistant for figure generation, analysis scripting, manuscript copy-editing, and
for the internal review pass that produced several of the corrections recorded in the
repository history. **No text, number, figure or citation in this manuscript was accepted
without author verification against the released data and code**; every quantitative claim
regenerates from the scripts in `scripts/`. The authors take full responsibility for the
content.

## Acknowledgements

*(To be completed before submission: funding sources, compute/infrastructure, and any
individual acknowledgements. — AUTHORS)*

## References

<!-- Generated by pandoc --citeproc from docs/references.bib using the Royal Society of
     Chemistry CSL style (docs/rsc.csl). Do not hand-number: cite with the bracketed
     at-key syntax in the text and the list below is built automatically, in citation
     order. NOTE: do not write a literal example of that syntax here -- pandoc parses
     citations inside HTML comments and it becomes a phantom empty reference. -->

::: {#refs}
:::
