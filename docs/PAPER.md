# Recall, not verification, is the bottleneck when frontier LLMs elucidate molecular structures from real spectra

**Ilkham Yabbarov**¹ *(corresponding: ilkhamfy@gmail.com)*, **Rudra Sondhi**¹, **Rodrigo A. Vargas-Hernández**¹
¹ Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario, Canada

---

## Abstract

Given the molecular formula together with the infrared band list and ¹H/¹³C shift
lists exactly as reported in an open-access paper, how often does a frontier large
language model (here, Claude) recover the correct molecular *constitution*? We find:
**28% of the time** (top-1, n=194; 95% CI 22–35) — far below the near-100% implied by
curated demonstrations. The bottleneck is not the model's judgment but its *proposal*:
on a 60-compound forward-verification subset the model proposes the true structure for
only **19 of 60** compounds (31%, 95% CI 21–44), and where it does, forward-verification
selects it in **16 of 19** (84%, 95% CI 62–94, against a 66% derangement floor, §5.5).
**Recall, not verification, is the wall.** We establish this with three contributions.
First, **IRexp** — the largest openly redistributable collection of *experimental*
infrared **band lists** (121,233 records, a third structure-linked), mined from
open-access literature and released with its mining pipeline (§2). Second,
**IRSpectra-Bench** — an open, blind, mechanically scored benchmark of 194 compounds on
which accuracy splits sharply by structural complexity, and a within-compound control
showing that reported numbers are sensitive to how a problem is posed, not to raw
capability alone (§3–§4). Third, a training-free **forward-verification** method that
acts on the diagnosis: generating regiochemistry-aware candidates and re-ranking them by
predicted-versus-observed ¹³C raises both candidate recall and top-1, though at this
sample size the top-1 gain is directional rather than resolved (§5.3). The gain is real
but bounded, because within the training-free regime accuracy is capped by the product of
generation recall and verification precision. That ceiling is a property of training-free
elicitation rather than an established limit of the task: a small generator fine-tuned on
IRexp lifts recall substantially and gives the highest full-benchmark accuracy we report
(§5.6). But the wall moves rather than falls — the true structure remains outside the
candidate pool for roughly half of compounds, and verification precision is untouched.
The recall-bound regime reproduces in a battery-electrolyte domain (§4.5). A formula-only control confirms the
spectra are doing the work: masking them drops top-1 from 23% to 5% on the same
compounds, with every formula-only success also solved from spectra and none the reverse
(§4.6). Every result is single-vendor (Claude); a cross-vendor test is the key open
question. The core protocol
uses no model training and no paid API — two clearly-fenced probes (§5.4, §5.6) are the
only exceptions — and all data, predictions, and code are released.

---

## 1. Introduction

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

We provide all three. We build IRexp (§2), a literature-mined dataset that supplies
the IR modality absent from prior LLM evaluations alongside paired NMR and resolved
structures. We define a blind benchmark on it (§3) and measure inverse-elucidation
performance under matched and mismatched methodologies (§4), isolating a large
solver-methodology effect with a within-compound control. We then introduce
forward-verification elucidation (§5), a training-free method that turns the model's
*strong* direction (forward prediction) against its *weak* one (inverse
regiochemistry), and use it to localise the bottleneck. The central finding is a sharp asymmetry:
given a candidate set that contains it, the model *verifies* the correct structure 84% of the time,
yet *proposes* it for only 31% of compounds — recall, not verification, is the wall
(Fig. 1). The end-to-end study design is summarised in Fig. S1. Throughout, the
solver and verifier are LLM agents run under a
consumer subscription — no fine-tuning, no API spend. That makes the protocol cheap to
*re-run*, but cheap is not the same as reproducible: the subscription harness pins no model
snapshot, exposes no temperature or seed, and carries an undisclosed product system prompt,
so an outside group reproduces it distributionally rather than exactly (§8). What *is*
exactly reproducible is the scoring — all predictions, ground truth and scorers are
released, so every number in this paper regenerates from the released artifacts. Two
trained probes (§5.6, §5.7) are reported separately as fenced complements.
By construction this is an open-resource contribution in the remit of *Digital Discovery*:
an openly licensed, structure-linked spectral dataset; a pre-registered, mechanically scored
benchmark with released ground truth and scorer; and a training-free, zero-paid-API core
pipeline (with two trained probes fenced in the SI) in which every figure regenerates from the
released code and predictions. We prioritise an honest, reusable measurement of where current
models stand over a leaderboard-topping number.

**Contributions.**
1. **IRexp** — the largest openly *redistributable* experimental-IR dataset (121,233
   records; 43,060 structure-linked; 33,201 IR+¹H+¹³C+structure): larger by raw record
   count than any prior collection and uniquely released under permissive licences for
   bulk model development (view-only resources such as SDBS are larger in
   structure-linked spectra but are not redistributable; §2.1), with a reproducible
   mining pipeline.
2. An **open multimodal benchmark** and the first blind, mechanically scored,
   complexity-stratified evaluation of frontier-LLM structure elucidation on real data
   — measured in depth on one model family (Claude) — reconciling the gap to optimistic
   prior reports. Crucially, the ground truth is experimental structures from the
   published literature, resolved deterministically (OPSIN/RDKit) and expert-audited:
   no LLM curates the labels or scores the predictions. The model is the system under
   test, not the source of its own answers.
3. A **diagnostic decomposition** of LLM elucidation into recall and verification,
   showing that **recall — not verification — bounds current performance**, obtained via
   a training-free forward-verification probe that yields a bounded improvement (top-1
   23%→30%) but, by our own measurements, cannot exceed a recall/precision ceiling
   without sharper verification or 2D-NMR data.

### 1.1 Related work

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

**LLMs as elucidators, and how this work differs.** General-purpose LLMs have been
applied off-the-shelf — Anthropic's forward/inverse white paper[@kamber2026chemist],
SpectraLLM and MolSpectLLM (multimodal LLMs over multi-spectral
input)[@su2025spectrallm; @shen2025molspectllm], and knowledge-enhanced tree-search reasoning[@zhuang2025treesearch] — and dedicated multimodal
*benchmarks* now exist, most prominently **MolPuzzle**[@guo2024molpuzzle] (IR+MS+¹H+¹³C elucidation
puzzles with the molecular formula supplied). These establish that the task is worth
benchmarking and that LLMs can be scored on multi-spectral input; we claim priority on
neither. What is new here is three things that, to our knowledge, no prior benchmark
combines. **(i) Real, literature-mined experimental spectra at scale:** prior
multimodal benchmarks and trained baselines[@chacko2024spectro; @ottomano2025nmiracle; @alberts2024ir] rely on simulated, software-predicted,
or hand-curated puzzle spectra, whereas IRSpectra-Bench is drawn from IRexp's
experimental IR + ¹H + ¹³C of out-of-distribution compounds, so it measures the
simulated-to-real gap rather than in-distribution skill. The closest trained precedent,
Alberts et al.[@alberts2024ir], learns an IR→structure transformer from ~635k *simulated* spectra with
a 3,453-spectrum experimental fine-tune (top-1 44% on 6–13 heavy atoms); IRexp instead
releases experimental IR at scale as an open, redistributable resource and pairs it with
a blind LLM benchmark. **(ii) Blind, fully specified, mechanical scoring:** reported
accuracies on the same task vary enormously with inference method and scoring harness —
GPT-4o on MolPuzzle ranges from 1.4%[@guo2024molpuzzle] to 27.8%[@zhuang2025treesearch], the latter using knowledge-enhanced
tree-search reasoning[@zhuang2025treesearch] — so numbers across papers are not directly comparable; we
therefore fix and release a single, pre-registered, RDKit-InChIKey protocol with
bootstrap CIs. **(iii) A recall/verification
decomposition:** existing benchmarks report a single aggregate score, whereas we factor
performance into generation recall and verification precision and show *where* the task
is lost — the result that transfers across models, domains, and verifier choices.

**Computational NMR for structure validation.** Our forward-verification method is
the LLM analog of a workflow chemists already trust: assign a structure by computing
the spectrum each candidate *would* give and matching it to experiment. In solution,
this is the DP4 / DP4+ probabilistic framework over GIAO-DFT shifts[@smith2010dp4; @grimblat2015dp4plus]; in the
solid state it is **NMR crystallography**, where GIPAW-computed shifts adjudicate
between candidate structures[@pickard2001gipaw; @ashbrook2016nmrcryst]. We replace the quantum-chemical predictor with a
forward LLM, trading accuracy for zero setup cost, and inherit the same core
principle — *verification by forward prediction is easier than inverse generation*.

---

## 2. The IRexp dataset

### 2.1 Motivation

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

### 2.2 Construction

A per-compound IR band list, together with co-reported ¹H/¹³C NMR, follows a
remarkably stable textual convention in the experimental sections of organic
chemistry papers. We exploit this with a browser-free harvesting agent:

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

### 2.3 Contents and licensing

**Table 1. IRexp dataset contents and provenance.**

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
39. Users training on band density should treat the pools separately (the `ir_source` and
`license` fields distinguish them).

**Extraction fidelity is measured, not assumed.** Because every record cites its source
accession and PMC is open, transcription can be checked directly. On a seed-fixed random
sample of 60 PMC-sourced records (`scripts/audit_extraction.py --n 60 --seed 0`), we
re-fetched each source article and asked whether every recorded wavenumber appears in that
article's text: **560/560 bands and 60/60 records were confirmed** (Wilson 95% CI 99.3–100%
and 94–100% respectively). This bounds *transcription* error — hallucinated, mis-parsed or
unit-mangled values — at under 1% of bands. It does **not** measure whether the parser
found every IR string in every paper, which is a recall question that requires human
reading; that manual audit is prepared but not yet run (§7). The audit record is released
at `data/audit/extraction_audit.json`.

A structure-complete split, **`irexp_resolved`** (43,060 records, 100%
structure-linked), is the training-/benchmark-ready subset and is ~6× the
6,833-molecule set used to train Spectro[@chacko2024spectro] (Fig. S2). Provenance is 119,345 PMC-OA records
(CC-BY) plus 1,888 Chemotion records (CC-BY-SA); the two licences are kept as
separable pools. Each record is DOI-/accession-traceable. Re-resolution is additive
and content-keyed, so the dataset can be re-enriched without re-mining.

---

## 3. Benchmark design (IRSpectra-Bench)

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
headline number is reproducible rather than a shipped artifact. The 60 compounds of the controlled rounds are
retained as fixed, pre-registered sets for the difficulty and within-compound controls,
with the same self-consistency audit reported separately rather than used to exclude
(57/60 pass; §7). Problems are stratified by RDKit ring analysis: a compound is **simple** iff it has at
most two rings (single ring or two separate ring fragments), no fused/spiro/bridgehead
system, and ≤22 heavy atoms; every other compound — any fused/spiro/bridged or ≥3-ring
system, **or** more than 22 heavy atoms — is **complex** (98 simple / 96 complex). This
binary difficulty axis is distinct from the continuous size gradient in §4.1, which bins
by heavy-atom count (≤15 / 16–25 / >25). The
criterion is therefore exhaustive (the 23–24-atom band, 13 compounds, is classed
complex by size). InChIKey de-duplication is applied across all rounds to prevent
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
is always reporting another study's metric under that study's own name; our two
quantities are always **recovered (top-3)** and **generation recall**, which are
different denominators and are never used interchangeably. **Generation recall** is the fraction for which the
reference is present in the candidate pool *before* re-ranking — the ceiling any
verifier can reach. **Conditional-on-recall precision** is the verifier's hit rate over
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
predictions). Adherence to the supplied formula is high but imperfect: 91.3% (115/126)
of forward-verification candidates match the given molecular formula exactly (100% of
true structures, 89.6% of decoys), and 76.6% across the full top-3 pool — a residual
generator error orthogonal to regiochemistry. This makes the benchmark free to run and
reproducible without API credits.

---

## 4. How well do LLMs elucidate real structures?

### 4.1 Headline performance

Solver agents work blind from formula + IR + ¹H + ¹³C and return up to three ranked
candidates. Each agent handles a small batch of problems in a bounded context that is
reset between batches (2–12 compounds per context in the released run; see
`data/benchmark_main/raw/`), rather than one long context over the whole benchmark —
the arm §4.3 shows matters. Over the full
**194-compound benchmark** (134 spectrally-validated compounds + the 60 from the
controlled rounds), with bootstrap 95% confidence intervals:

**Table 2. Headline elucidation performance on IRSpectra-Bench (n=194)**, overall and by difficulty stratum, with bootstrap 95% CIs.

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
separation (Fig. 2) confirms the benchmark is discriminating across a realistic
difficulty range, and accuracy falls monotonically with molecular size in step with
it — top-1 **60.5%** for ≤15 heavy atoms, 28.3% for 16–25, and **7.0%** above 25
(Fig. S3). The model recovers molecular formula and functional groups reliably and the
scaffold often (best Tanimoto ≥ 0.45 for 56% of compounds), but the exact constitution
far less often, failing predominantly on **regiochemistry** — *which* position a
substituent occupies. This is consistent
with an information limit of 1D data: many regioisomers have similar ¹H/¹³C shifts,
which is precisely why 2D experiments (HMBC, NOESY) exist.

### 4.2 Reconciling with prior reports

Our 28% top-1 sits far below the ~100% on "simple" molecules reported, in a
non-peer-reviewed company white paper, for the same model class.[@kamber2026chemist] Because that figure
has not been independently scored, we reconcile it against the *peer-reviewed* record
(the MolPuzzle benchmark[@guo2024molpuzzle] and its re-scorings[@zhuang2025treesearch], and the trained baselines[@chacko2024spectro; @ottomano2025nmiracle]) rather
than treating it as settled. The gap is largely attributable to methodology and scoring
choices, not raw capability:

- **Difficulty.** "Single ring" by ring-count is not "easy": our simple stratum
  includes, e.g., a hexasubstituted benzene whose regiochemistry has many
  realisations. Ring count is a poor proxy for elucidation difficulty.
- **Scoring.** Prior work counts a recovery if the reference appears among three
  ranked candidates over three independent runs; we report single-run top-1 and
  top-3.
- **Hints.** Prior hard targets received the starting-material SMILES, which fixes
  most of the scaffold; we give none.
- **Curation.** Prior compounds were hand-selected; ours are scraped and unfiltered
  for solvability.

On a like-for-like easy/hinted/lenient setup the numbers rise; on the realistic,
hint-free, scraped regime, ~28% is the honest figure.

**Versus trained models — a bound, not a leaderboard.** A like-for-like comparison
against specialised trained models is not available: no system has been scored on an
identical test set, and published numbers differ in the three respects that most move
the score — spectrum realism (simulated/curated vs. real), hints, and how "exact
match" is defined. The strongest trained baselines report their accuracy
*in-distribution on simulated spectra*. Spectro (¹H/¹³C/IR→SELFIES, 6,833 training
molecules) reaches ~90% top-1 exact recovery — but on a 1,366-molecule held-out split
whose IR is plotted from reference data and whose NMR is software-*predicted*, not
experimental[@chacko2024spectro]; and NMIRacle, which like us conditions jointly on IR+¹H+¹³C with *no*
hints, reports 48% top-1 / 66% top-15 exact-SMILES recovery — again on held-out
molecules from a *simulated* corpus drawn from the training distribution[@ottomano2025nmiracle]. We measure
28.4% top-1 (33.5% top-3) on the full n=194 benchmark — rising to 30% with forward
verification on the n=60 forward-verify set (§5) — on **blind, real,
literature-mined experimental** spectra of out-of-distribution compounds. These are
not comparable as a leaderboard; read as a *bound on the simulated-to-real gap*, the
contrast suggests that high in-distribution accuracies substantially overstate
real-world performance — the same gap we document for the LLM above. The instability
of the metric itself reinforces the caution: the same ~20× MolPuzzle swing documented in
§1.1 (GPT-4o: 1.4%[@guo2024molpuzzle]–27.8%[@zhuang2025treesearch], method- and harness-dependent) bounds how much weight any
single unaudited near-100% claim[@kamber2026chemist] can bear.

### 4.3 Methodology dominates: a within-compound control

The same 20 molecules were solved two ways: (a) by a single LLM context handling
all of them sequentially with no tools, and (b) by four independent agents of five
compounds each, with RDKit formula-checking — i.e. bounded, reset contexts. On the *identical* compounds, **recovered (top-3)** rose from
**5% to 15%** (1/20 → 3/20) and top-1 from 0% to 15% (0/20 → 3/20) — a 3× methodology
effect with zero sample confound, though on a small set (the 15% point estimate carries
a Wilson 95% CI of roughly 5–36%), so it is read as a directional within-compound
demonstration rather than a precise multiplier. Small rounds also swing widely (15–40% across n=20–40 draws), which is
why the headline is the full **194-compound** figure (28.4% top-1, 95% CI 22–35)
rather than any single round. The practical lesson — fresh per-compound context
plus tool access roughly triples apparent performance — also explains part of the
gap to
optimistic prior reports, whose per-problem API calls implicitly used method (b).

### 4.4 Model comparison: the benchmark ranks capability (and separates the extremes)

A benchmark is only useful if it separates models. On a fixed 24-compound subset
solved blind by four Claude models — spanning a wide capability range, including the
newest (Fable 5) — under the identical protocol (Fig. 3):

One asymmetry must be disclosed, because §4.3 shows the variable it concerns has a
large effect. The three comparison models each solved the 24 compounds as four
six-compound contexts, whereas the Opus column reuses the headline run, in which those
same 24 items were packed as one six-compound and two twelve-compound contexts. Context
packing is exactly the factor §4.3 measures at 5%→15%, so the Opus point estimate is not
strictly protocol-matched to the other three and, if anything, is the arm handicapped by
longer contexts. This does not affect the nesting or the Fable-vs-Haiku contrast, but a
clean re-run of the Opus arm under four six-compound contexts is the right fix and is
listed as outstanding in `docs/MODELS.md`.

**Table 3. Four-model comparison on a fixed 24-compound subset** under the identical blind protocol.

| model | top-1 | recovered | top-1 95% CI |
|---|--:|--:|--:|
| Claude Fable 5 | **45%** | 54% | [25, 67] |
| Claude Opus | 25% | 29% | [8, 42] |
| Claude Sonnet | 20% | 25% | [8, 38] |
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
closely (Opus 25%, Sonnet 20%), so the recall-bound regime of §4.1 (top-1 in the
high-20s%) is **not an artefact of a single model**. Third, the newest model nearly **doubles** the
next-best top-1 (45% vs 25% on identical compounds; a large but, at this n,
not-yet-significant gap) yet still misses the majority — IRSpectra-Bench is **hard and
far from saturated even for the strongest model available**, with clear headroom. We
ran four Claude-family models because they are callable for free under one
subscription; a true cross-vendor sweep (GPT-, Gemini-class, open models) needs API
access we deliberately did without, but the monotonic, large capability spread makes
it unlikely the recall-bound pattern is specific to one model lineage. This is the
behaviour a benchmark needs to remain informative as models improve.

### 4.5 Domain case study: battery-electrolyte chemistry

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
of any one chemical neighbourhood. The per-class
breakdown (Fig. S4) is itself informative:

**Table 4. Per-class performance on IRSpectra-Bench-Electrolyte (n=46).**

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
underdetermine. This is the recall-bound failure of §4.1 reappearing in a
domain-specific guise, and it is precisely where the **forward-verification**
recipe of §5 — compute the spectrum each candidate *would* give and match it to
the one observed — plays a role *analogous* to (not a replacement for) computational-NMR
/ NMR-crystallography structure validation, sharing its forward-prediction logic while
trading DFT's calibrated accuracy for zero setup cost. The subset, its per-class answers, and the scorer are released
with the benchmark.

### 4.6 Is the model reading the spectra? A formula-only control

Because every benchmark compound is mined from open-access literature, a frontier model
may have encountered it during pretraining. The cheapest decisive test of whether that
explains the headline number is to take the spectra away. We re-ran the identical blind
protocol with every spectral channel masked, so the solver receives the molecular formula
and nothing else (`scripts/modality_ablation.py`, condition `formulaonly`; solvers were
barred from reading any repository file or searching the web, and RDKit was permitted only
to check that a proposed SMILES parses and matches the formula). A molecular formula does
not determine constitution, so accuracy materially above the floor would indicate recall
rather than reasoning.

**Table 5. Formula-only control**, paired on the same 60 compounds as §5.

| condition | top-1 | recovered (top-3) |
|---|--:|--:|
| formula only | **3/60 (5%)** | 3/60 (5%) |
| formula + IR + ¹H + ¹³C | **14/60 (23%)** | 19/60 (32%) |

The outcomes are perfectly nested: **eleven** compounds are solved with the spectra and
not without, and **none** the other way round (McNemar exact p=0.001). Removing the
spectra removes the result.

The 5% is not zero, and it is worth saying what those three compounds are rather than
rounding them away: a 2-(trimethylsilyl)aryl sulfonate, whose Si/S/Cl/F₂ composition is a
near-unique benzyne-precursor signature; N-tosyl leucine; and a vanillyl alkanone. In each
case an unusual element combination or a very common derivative class makes the formula
close to determining, which is chemical inference from composition rather than evidence of
having memorised this benchmark — though this experiment cannot separate the two. What it
does establish is a bound: formula-level recall accounts for at most about a fifth of the
headline accuracy on this set. It does not exclude memorisation contributing to the
remainder (§7). The control record is released at
`data/modality/formulaonly_control.json`.

---

## 5. Forward-verification elucidation

### 5.1 Method

The inverse direction is the model's hard, isomer-blind direction; the **forward**
direction (structure→spectrum) is its easy, accurate one.[@kamber2026chemist] Regioisomers, crucially,
have *different* forward-predicted ¹³C shifts. We therefore close a generator–
verifier loop:

> **generate** candidate structures (inverse) → **forward-predict** each candidate's
> ¹³C spectrum, blind to the observed spectrum → **re-rank** candidates by the
> distance between predicted and observed ¹³C → return the best match.

This mirrors how a chemist confirms a structure ("if it were that isomer, C-3 would
be at ~120 ppm; we observe 135, so it is the other"), exploits the standard
principle that verification is easier than generation, and requires no training.
**Fig. 4** shows the mechanism on a real benchmark pair — the picolinamide /
nicotinamide regioisomers, which the inverse task cannot separate but whose
forward-predicted ¹³C spectra match the observed one at 0.42 vs 1.30 ppm. We
implemented the verifier as independent LLM agents that predict ¹³C shift lists from
SMILES alone, using pure reasoning with no tools; candidates were shuffled and anonymised
so that isomers of one target never co-occur. Predicted and observed ¹³C peak sets were
then compared with a symmetric chamfer distance.

For balance — and because conditional precision is 72–84%, not 100% — the verifier also
produces clear **false positives** on near-degenerate pairs. On the
2-(nitrophenyl)-2,3-dihydroquinazolin-4(1*H*)-one targets (C₁₄H₁₁N₃O₃), the forward
predictor cannot separate the *ortho*- and *meta*-nitrophenyl regioisomers: their
predicted ¹³C lie within its ~2 ppm error, and it ranks the wrong (2-nitrophenyl) isomer
first by a chamfer of 1.35 ppm versus 1.36 ppm for the true (3-nitrophenyl) one — a
0.01 ppm margin, i.e. effectively a coin flip. This is the precision-loss mechanism of
§5.3 made concrete: when candidates are near-degenerate the cheap predictor cannot
resolve them, and it is exactly these cases — not generation failures — that a sharper
(DFT-level) or 2D-NMR-grounded verifier would need to fix.

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

### 5.2 Result

On the 60 benchmark compounds (126 candidate structures from the solver agents):

**Table 6. Forward-verification decomposition** on the 60 forward-verify compounds.

| | value |
|---|--:|
| generation recall (true structure among candidates) | **31%** |
| top-1, solver self-ranking | 23% |
| top-1, **forward-verified re-ranking** | 26% |
| **conditional on recall — self-ranking** | 14/19 (**73%**) |
| **conditional on recall — forward-verification** | 16/19 (**84%**) |

The decomposition is the finding. **When the true structure is among the
candidates, forward verification selects it in 16 of 19 cases (84%)** — high in
absolute terms and ~18 points above the 66% derangement chance floor of §5.5 (given how
few and near-degenerate the recall-positive candidate sets are). It also edges the
model's own self-ranking (14/19, 73%), but that +11-point margin is a two-compound
difference at n=19 and is **not** statistically significant (McNemar exact p≈0.63); the
load-bearing claim is that verification precision is high in absolute terms while recall
binds — not that forward-verification beats self-ranking.
The overall top-1 moves only 23%→26% because the binding constraint is **generation
recall**: the true structure was never proposed for 41 of 60 compounds, which no
re-ranking can repair.

LLM elucidation therefore factorises into two near-independent levers: the
**verifier is already strong (84%)**; the **generator (31% recall) is the wall**
(Fig. 1).

### 5.3 Generate-wide: testing the recipe

The decomposition implies a recipe — *generate wide, verify by forward prediction* — a
chemistry analog of self-consistency sampling, where many independent generations are
pooled and the answer is chosen by agreement rather than from a single pass.[@wang2023selfconsistency] We
tested it directly: ten independent solver agents proposed up to **six
regiochemistry-aware candidates per compound**, pooled with the originals, and the
65 new candidates were forward-predicted and re-ranked as before. The measured
result:

**Table 7. Generate-wide vs original** on the same 60 compounds.

| | original | generate-wide |
|---|--:|--:|
| recall (true structure among candidates) | 31% | **41%** |
| forward-verified top-1 | 26% | **30%** |
| verification precision (conditional on recall) | 84% | 72% |

Wide generation lifts recall +10 points (31%→41%, i.e. 19/60→25/60) and exact top-1
+7 points over the self-ranking baseline (23%→30%, 14/60→18/60) — equivalently +4 over
the original forward-verified top-1 (26%→30%, 16/60→18/60, Table 7) — on the same 60
compounds (Fig. 5), with no training. Table 7 regenerates from the released artifacts via
`scripts/score_generate_wide.py`. **These top-1 differences are directional, not
statistically resolved at n=60:** the 14/60→18/60 improvement is a four-compound
difference, which reaches only McNemar exact p=0.125 even under the most favourable
assumption that the stages are perfectly nested (no compound lost); the 16/60→18/60
step reaches p=0.5. The recall gain is the better-supported effect. We therefore read
the ladder as a demonstration that the *mechanism* works and that recall is the movable
factor, not as a precise measurement of the size of the top-1 gain. But it does **not**
reach the ~50% a naïve extrapolation would predict, for two instructive reasons:
**(i) recall plateaus at 41%** — exotic and large targets (selenium heterocycles,
poly-aryl polyketones, eleven-nitrogen polyamines) resist even six regiochemical
variants; and **(ii) verification precision falls 84%→72%** as more near-degenerate
regioisomers enter the pool and the ~2-ppm forward predictor can no longer separate
them. This recall/precision tension is the honest ceiling of the training-free
approach: the recall-bound diagnosis stands, and closing the gap further requires
either sharper verification or 2D-NMR constraints, not merely more candidates.

### 5.4 Non-LLM verifiers: a deterministic lookup and a learned model

§5.3 suggests an obvious fix: swap the LLM forward-predictor for a non-LLM ¹³C predictor
with a rigorous error model. We test two, both trained on the **same nmrshiftdb2
dump**[@kuhn2015nmrshiftdb2] and both dropped into the verifier slot on the **same §5.2
candidate set**, so that only the predictor changes.

The first is the canonical choice: a **HOSE-code[@bremser1978hose]-style lookup** (RDKit
radial-environment bins, spheres r=4→1 with a hybridisation prior fallback; 31,000
molecules, 332,595 assigned carbons; held-out MAE 3.23 ppm, median 1.73). The second is a
small **message-passing GNN** (4 layers, per-carbon ¹³C regression) trained on the identical
dump, which reaches held-out MAE 1.70 ppm (median 1.02) — roughly twice as sharp, and an
independently competent predictor.

**Table 8. Verifier comparison, conditional on recall (n=19), on the identical §5.2 set.**

| verifier | top-1 \| recall | held-out ¹³C MAE |
|---|--:|--:|
| solver self-ranking | 14/19 (73%) | — |
| deterministic HOSE *lookup* | 14/19 (73%) | 3.23 ppm |
| **learned GNN (same data)** | **16/19 (84%)** | **1.70 ppm** |
| LLM forward-verifier (§5.2) | 16/19 (84%) | — |

The lookup does not help: it matches the solver's own ranking and sits below the LLM
verifier. Its diagnosis is coverage — of the 2,244 candidate carbons, only **2%** match a
training environment at the most specific sphere (r=4) and **67%** resolve only at coarse
spheres (r≤2), because the benchmark's exotic chemistry (selenium heterocycles, polyaryl
ketones, large polyamines) is under-represented in nmrshiftdb2. A coarse environment
cannot separate the regioisomers the verifier exists to separate.

The learned model, on the same data, reaches the LLM verifier's 84% (Fig. S6). **That is a
two-compound difference at n=19 and is not statistically resolved** (McNemar exact p=0.5
even under the most favourable nesting assumption) — the same standard by which §5.2
declines to separate its own adjacent conditions. Taken together the two rows are
*suggestive and directional*: they are consistent with the lookup's failure being
substantially **method** — an inability to generalise across novel environments — rather
than coverage alone, and with a cheap learned predictor being sufficient to match the LLM
without compound-specific DFT accuracy or 2D-NMR. They do not establish it, and the
coverage reading is not excluded; separating the two would need a substantially larger
conditional-on-recall set. What none of these reach is the near-degenerate-regioisomer
precision ceiling (§5.3/§5.5), where DFT-level accuracy or orthogonal 2D-NMR constraints
remain the genuine fix.

The GNN and the LLM reach 84% on *partly different* compounds (two independent verifiers
concurring, not one), and the result is **generalisation, not memorisation**:
candidate–training overlap is **0/126** by InChIKey-14 (zero overlap against the entire
nmrshiftdb2 database; every true structure and all three GNN-wins absent),
Morgan-Tanimoto nearest-neighbour to training is a modest 0.44 median with the wins
sitting *at* — not above — the median, and a Y-randomisation control (1,000 derangements)
places the real 84% above the 97.5th percentile of the chance distribution (mean 58.6%,
95% range 42.1–73.7%; one-sided p<0.05). The margins are thin (one decisive win at
0.79 ppm, two tight, one 0.08-ppm coin-flip loss), so the +2 is confirmatory of the LLM
number rather than a precise quantitative gain. Like §5.6, the learned verifier is a
**trained complement**, reported outside the training-free protocol. Artifacts and both
leakage checks are released (`scripts/gnn_predict.py`, `data/fverify/gnn_results.txt`,
`data/nmrshiftdb/gnn_c13.pt`; `docs/VERIFIER_PROBE.md`).

### 5.5 Negative control

**Permutation negative control (Y-randomisation analog).** A re-ranker earns the
interpretation that it exploits genuine predicted-vs-observed ¹³C agreement only if
that agreement is destroyed when the pairing is broken. Borrowing the Y-randomisation
discipline of QSAR validation, we re-paired — as a *derangement*, so no compound keeps
its own spectrum — which observed ¹³C spectrum each candidate set is scored against,
and re-ran the verifier 1,000 times. Conditional-on-recall precision falls from the
true **84.2% (16/19)** to a permuted mean of **66.4%** (95% range 52.6–78.9%; one-sided
empirical p=0.019, two-sided p=0.038) — the verifier acts on real spectral
agreement, not a candidate-list artefact. The honest caveat is the height of the chance
floor: because recall-positive compounds carry few and near-identical (regioisomeric)
candidates, even a random pairing lands on the correct structure ~66% of the time, so
the verifier's genuine margin over chance is **~18 points**, not the full 84% — real and
significant, but to be read against this high baseline.

**Confidence calibration (a negative result).** We also asked whether the chamfer
match-distance doubles as a confidence signal that would support selective prediction.
It does not. Ranking the 48 multi-candidate compounds by their chamfer margin (the gap
between the best and second-best predicted-vs-observed distance) and answering only the
most-confident fraction leaves top-1 essentially flat and non-monotonic with coverage
(≈21% overall, neither rising nor falling reliably as the threshold tightens).
Compounds with a single proposed candidate have no margin at all and must be excluded;
an earlier analysis that retained them produced a spurious "improvement" that was
entirely an artefact of those trivial cases. We therefore do **not** claim the verifier
distance as a calibrated abstention gauge — a sharper, DFT/2D-NMR-grounded confidence
estimate (§5.4) remains the route to reliable selective prediction.

### 5.6 Is the recall wall task-intrinsic? A trained-generator probe

The ceiling above is a property of *training-free LLM elicitation*; it leaves open
whether the ~41% recall plateau is intrinsic to 1D-data elucidation or specific to how
LLMs are elicited. We test this with a complementary probe — a small (~16M-parameter)
¹H/¹³C→SMILES transformer (simulated-spectra pretraining, then fine-tuned on IRexp;
ensemble of four), held **deliberately separate from the training-free protocol**. Its
candidates are filtered to the given molecular formula, pooled with Claude's, and
re-ranked by the same verifiers.

The generator supplies candidates enumeration cannot. On the 194-compound benchmark the
true structure enters the candidate pool for **54.1%** of compounds (versus 41.8% for
scaffold enumeration and 33.5% for Claude alone). Crucially, where enumeration's
near-degenerate regioisomers *collapse* the deterministic HOSE verifier
(top-1 28.4%→16.0%, the §5.3 precision-loss mechanism), the generator's formula-correct,
¹³C-separable candidates **convert**: HOSE top-1 rises **28.4%→35.1%** (McNemar exact
p=0.015; +6.7 points, 95% CI [+2.1, +11.9]; Fig. S5). With the stronger LLM
forward-prediction verifier on the 60 forward-verify compounds, recall rises 41%→**56%**;
the corresponding forward-verified top-1 (measured at **41%**, precision 72%→73%) was
obtained with blind in-house prediction agents and is reported as **provisional** pending
deposit of those forward-prediction outputs and a re-run under the pinned model snapshot
(the released `forward_verify_gen.py` reproduces the recall arm and the deterministic
HOSE re-rank; the LLM forward-prediction JSONs are not yet in the bundle).

Two controls guard against memorisation, both reproducible from the released bundle
(`contrib/generator_probe`): (i) the fine-tuning split removes every benchmark
InChIKey-14 (train∩benchmark = 0, val∩benchmark = 0), and **none of the 40
newly-recovered compounds appear in either training stage** (0/40 in simulated
pretraining, 0/40 in fine-tuning); (ii) the simulated-pretrained model alone recovers
**0/248** benchmark structures zero-shot, rising to 25% only after IRexp fine-tuning.
The IRexp data — not the architecture — is the active ingredient, and the recall ceiling
is therefore **elicitation-specific, not task-intrinsic**. We report this as a probe,
not part of the headline training-free protocol; it answers whether the wall is
breakable, not whether to abandon training-free methods. (The released public split
`irexp_release/train` does *not* hold out the benchmark — it overlaps it by 117/200
InChIKey-14 — so downstream users must de-leak as in `build_exp_manifest.py`; see Data
and code availability.)



---

## 6. Discussion

The frontier LLMs we tested (the Claude family) are neither "solving structure elucidation"
on realistic 1D data nor failing at it. They are reliable **scaffold-level**
elucidators (best-candidate Tanimoto ≥ 0.45 for 56% of compounds, 73% of simple ones; mean
best Tanimoto 0.59) and good **verifiers** (84% conditional on recall). Exact top-1 is
throttled by candidate recall and by the regiochemical underdetermination intrinsic to 1D NMR.
The contribution of this paper is therefore best read as a **diagnosis with a bounded,
training-free improvement attached**, not as a method that solves the task. The
diagnostic result is the durable take-away: across models, domains, and verifiers, the
wall is **generation recall**, not verification. The accompanying improvement is real but
deliberately modest — forward verification with wide generation lifts top-1 from 23% to
30%, and we show by direct measurement (§5.3) that this stays *below its own ceiling*
(recall plateaus at 41%; verification precision falls to 72% as near-degenerate
regioisomers accumulate), while the match distance fails as a confidence gauge for
selective prediction (§5.5, a reported null result). This reframes the
engineering problem. Rather than training a bespoke spectra→structure model — a
target the frontier already meets at the scaffold level and that ages out each model
generation — the durable levers are (i) **open, hard, honestly scored benchmarks**
that expose specific failure modes (here, regiochemistry and recall), and (ii)
**inference-time scaffolding** (decoupled solving, generate-and-verify) that needs no
training and improves with each model. IRexp's IR modality and 2D-NMR-ready
provenance position it for the obvious next step: supplying the HMBC/COSY/NOESY
constraints that would attack regiochemistry at the source. Our trained-generator probe
(§5.6) sharpens the point: the recall wall is *elicitation-specific, not task-intrinsic*
— a small generator fine-tuned on IRexp lifts it (recall 41→56%) — and because that gain
comes entirely from the released data (0→25% with fine-tuning, 0/248 without), it is the
**open dataset**, not a bespoke architecture, that does the work when training does help.

**Protocol is a lever of the same order as capability.** How a problem is posed and
verified — bounded, reset contexts with tool access; generate-and-verify — moves accuracy
enough that it must be reported alongside any capability claim. We do *not* claim it
dominates capability: on the fixed 24-compound subset the model axis spans 0% to 45%
top-1 (Table 3), a wider range than the 5%→15% protocol effect in §4.3, and the two are
measured on different sets. The point is that a number quoted without its protocol is
uninterpretable, which echoes a recurring lesson across cheminformatics: careful pipeline
and protocol design competes with the fashionable component. The same pattern appears in
molecular property prediction, where a recent systematic benchmark reports that
learned, pretrained molecular embeddings rarely outperform classical ECFP
fingerprints once evaluation is controlled[@praski2025embeddings] — the modelling fashion underperforms the
well-engineered baseline. We read our within-compound control (§4.3) and
forward-verification recipe (§5) in the same light: the durable gains in LLM
elucidation come from honest benchmarking and inference-time scaffolding rather than
from waiting on the next, larger model. We draw this parallel narrowly and claim no
formal equivalence between the two settings.

That the bottleneck reproduces inside a single application domain
(§4.5: 26% top-1 on battery-electrolyte chemistry, n=46, against 28% overall) is
consistent with it being structural rather than incidental — and it makes the
forward-verification recipe directly relevant to the magnetic-resonance workflows
(electrolyte-decomposition assignment, NMR crystallography) where computing a
candidate's spectrum to confirm it is already standard practice.

For practitioners, two operational findings transfer immediately: solve each problem
in bounded, frequently-reset contexts with tool access (5%→15%, 1/20→3/20,
directional at n=20, §4.3), and use forward-predicted-vs-observed
¹³C agreement to *re-rank* candidates, not to decide whether to trust the winner. §5.5
is explicit on this: match distance is a strong relative re-ranker but failed as an
absolute confidence gauge in our selective-prediction test, so it does not support
abstention thresholds.

---

## 7. Limitations

Several limitations of earlier drafts are now resolved with controlled experiments;
we state what remains plainly.

*Resolved.* **Extraction noise:** an RDKit self-consistency audit (¹³C peak count vs
symmetry-unique carbons, formula, SELFIES round-trip) finds **57/60 ground truths
spectrally clean**, and the metrics are unchanged on that clean subset
(self-ranking top-1 24% vs 23%, recall 33% vs 31% on the n=60 forward-verify set) — the
conclusions are not driven by scraping artefacts. **Verifier precision / abstention:** the generate-wide experiment (§5.3)
quantifies the recall/precision tension directly — verification precision is
72–84% conditional on recall and degrades as near-degenerate regioisomers
accumulate, so forward-match distance is a strong *re-ranker* but a soft
*confidence* gauge. We further tested non-LLM verifiers (§5.4): a
nmrshiftdb2-trained HOSE-code *lookup* does **not** beat the LLM verifier (73% vs 84%
conditional), while a *learned* GNN on the same data reaches 84% — a
two-compound difference at n=19 that is directional only (p=0.5), so it is suggestive
that the deterministic failure was method rather than coverage alone, not a
demonstration of it. What remains beyond all of
them is the near-degenerate-regiochemistry precision ceiling, where DFT-level accuracy or
2D-NMR constraints are still the genuine fix. **Projection:** §5.2's
extrapolation is replaced by the **measured** §5.3
result (top-1 30%, recall 41%) — and is honestly below the optimistic estimate.

*Independence checks.* Scoring throughout is mechanical RDKit (not LLM-judged), and
all solver/verifier runs were transcript-audited *at generation time* for zero web and
zero ground-truth access; the committed artefacts are the parsed per-compound
predictions, and the underlying transcripts are available on request. To confirm that
the forward-verifier's measured advantage
reflects real predicted-vs-observed spectral agreement rather than leakage or a
candidate-list artefact, we ran a permutation negative control (Y-randomisation
analog, §5.5): re-pairing — as a derangement — which observed ¹³C spectrum each
candidate set is scored against, over 1,000 permutations, collapses conditional-on-recall
precision from 84.2% to a chance mean of 66.4% (two-sided p=0.038) — the signal weakens
to the chance floor under label-shuffle, as a correctly isolated blind evaluation requires. A second Claude model (Sonnet)
re-solved a 12-compound subset under the identical generate-wide protocol and was comparably
recall-bound (recall 33% vs Opus 41% on those compounds), consistent with the recall bound
being a property of the task rather than of one model. As this is within the Claude family,
it speaks to model-instance robustness, not cross-vendor generality.

*Remaining.* **(i) Pretraining contamination is bounded, not excluded.** Every benchmark
compound was mined from open-access literature, so a frontier model may have encountered
it in training. The formula-only control (§4.6) bounds how much of the headline number
pure recall can explain — masking the spectra drops top-1 from 23% to 5%, perfectly
nested, McNemar exact p=0.001 — and the three formula-only successes are all compounds
whose composition is close to determining. That bounds the effect; it does not exclude
memorisation contributing to the remainder. A per-compound comparison of source
publication dates against model training cutoffs, and a replication on compounds
published after the cutoff, are the natural next controls and are not run here.

**(ii) Human audit — prepared but not yet run.** This covers two things we have not
validated by hand: the elucidation and forward-prediction outputs, and the *recall* side
of dataset extraction (whether the parser found every IR string in every source paper).
Transcription fidelity of the records we do hold is measured and high (§2.3), but record-level
recall is not, and only reading papers can settle it. Solver and verifier are
both LLMs, so the one validation we cannot perform ourselves is an expert-chemist review
of a sample of elucidations and forward predictions. We have therefore **built and
frozen** a blinded, pre-registered audit package — a difficulty-stratified 30-compound
sample (9 recall-positive), rendered candidate structures, a separate withheld answer
key, and a mechanical scoring sheet — released at `data/audit/` with its protocol at
`docs/EXPERT_AUDIT_PROTOCOL.md` (regenerable via `scripts/make_audit_sample.py`),
designed to test the two load-bearing claims (misses are predominantly consistent
regioisomers, §4; forward verification is a trustworthy re-ranker, §5). **We have not
yet run the panel**; until expert results are in, those claims should be read as
machine-validated (RDKit InChIKey) but not yet human-validated.

**(iii) Single vendor and an underpowered cross-model comparison.** Every number comes
from one vendor's models. The headline (28.4% top-1) is a single frontier model (Claude
Opus), and the cross-model evidence (§4.4) is four **Claude-family** models on a shared
**24-compound** subset. As §4.4 sets out, that comparison is underpowered: the
ranking is robust (strictly nested, weakest floored at 0%) but no adjacent gap is
established at n=24. Quantitative claims should therefore be read as holding **for the Claude family**,
and a true cross-**vendor** sweep (GPT-, Gemini-class, open-weight models) — the test of
whether the pattern is a property of the task rather than one lineage — was forgone
because it needs paid API access incompatible with our zero-cost protocol; we flag it as
the most important external-validity experiment left open.

**(iv) Domain-subset scope:** the battery-electrolyte case study (§4.5) comprises
*literature compounds bearing electrolyte-relevant functional chemistry* drawn from the
open corpus — not operando or in-cell decomposition spectra — so it demonstrates
functional-class transfer of the elucidation bottleneck, not direct assignment of
authentic interphase/degradation products, which would require a dedicated operando set.

**(v) Constitution-only scoring:** correctness is judged on InChIKey connectivity, so a
correct-constitution / wrong-stereochemistry prediction is counted correct. Scoring the
full InChIKey instead gives 21.1% top-1 (§3), 7.3 points lower, so the headline should be
read as an upper bound on full-stereochemistry accuracy. We keep constitution as the
headline because 1D NMR/IR rarely determines absolute configuration — the 10.3% (20/194)
of targets with a defined stereocentre would be penalised for information the prompt
never carried — but a stereochemistry-sensitive benchmark would need 2D/chiroptical data.

**(vi) Single-sample scoring:** each headline compound is scored from one solver
prediction set (one decoupled run), so reported top-1/recall carry no run-to-run
(LLM-sampling) variance estimate — the bootstrap CIs reflect compound sampling only. The
generate-wide experiment (§5.3) pools ten independent generation passes (recall
31%→41%), indicating generator stochasticity that single-pass scoring understates.

**(vii) Chemical-space coverage:** the benchmark is drawn from open-access organic
methodology and total-synthesis literature, covering small-to-medium drug-like and
synthetic-organic space; it is **not** representative of organometallic/coordination
compounds, large biomolecules (peptides, oligonucleotides, oligosaccharides), or
stereochemistry-heavy targets, and our results should not be extrapolated to them.

---

## 8. Methods

**Mining and resolution.** PMC-OA full text was fetched from `s3://pmc-oa-opendata`;
records were extracted with a deterministic parser and resolved with OPSIN, RDKit,
and SELFIES, with an optional cached PubChem fallback. Durable content-keyed caches
make resolution additive and restart-safe.

**Benchmark and agents.** Problems were sampled from `irexp_resolved`, stratified by
RDKit ring analysis, with cross-round de-duplication by InChIKey. The
battery-electrolyte subset (§4.5) was drawn from the same corpus by SMARTS
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
the two trained probes — the §5.6 generator and the §5.4 learned ¹³C verifier — are the
only separately-trained exceptions, each reported as a complement and fenced from the
headline results.

*Models and versions.* All experiments used Anthropic Claude models via the consumer
subscription (claude.ai). The §4.4 comparison spanned, in capability
order, Claude Haiku, Claude Sonnet, Claude Opus, and Claude Fable 5; the headline
benchmark (§4.1) and forward-verification (§5) used Claude Opus. `docs/MODELS.md`
records, for each experiment, the model used, its data directory, the collection date,
the harness and tool access, and the scoring code path; all LLM predictions were
collected between 2026-06-09 and 2026-06-11 (UTC). Decoding parameters are not exposed
by the subscription harness and were neither set nor recorded, so re-running reproduces
the protocol distributionally rather than exactly; the dated model snapshot identifiers
are listed there as the outstanding items to be pinned on submission.

**Reproducibility.** Every round is frozen: questions, ground-truth answers,
per-agent raw outputs, predictions, and scorer outputs are released, and the sampler,
scorer, and forward-verification harness are scripted end-to-end.

---

## Figures (main text)

- **Fig. 1** (`docs/figures/fig_wall.png`) — the diagnosis in one glance, as a
  part-to-whole bar of the 60 forward-verify compounds: 16 verified top-1, 3 recalled
  but mis-ranked, 41 never proposed — *the wall*, 68% of the bar. Generation recall is
  19/60 (31%); conditional verification precision is 16/19 (84%); their product is the
  26% end-to-end top-1. The two rates have different denominators and are not
  differenced.
- **Fig. 2** (`docs/figures/fig1_difficulty.png`) — top-1 and recovered accuracy on
  IRSpectra-Bench by difficulty (all / simple / complex, n=194) with bootstrap 95% CIs.
- **Fig. 3** (`docs/figures/fig5_models.png`) — four-model comparison on a 24-compound
  subset: Fable 5 45% > Opus 25% > Sonnet 20% > Haiku 0% top-1 (strictly nested);
  capability-sensitive but underpowered to separate adjacent models at n=24.
- **Fig. 4** (`docs/figures/fig_mechanism.png`) — forward-verification on a real
  benchmark regioisomer pair (picolinamide vs nicotinamide): forward-predicted ¹³C
  matches the true isomer (chamfer 0.42 vs 1.30 ppm), an analog of NMR-crystallography.
- **Fig. 5** (`docs/figures/fig3_method.png`) — forward-verification inference ladder
  on the same 60 compounds: solver self-ranking → + forward-verify → + generate-wide
  (23%/26%/30% top-1).

## Supporting Information figures

- **Fig. S1** (`docs/figures/fig0_overview.png`) — study design: open multimodal data
  (IRexp) → blind, complexity-stratified benchmark → decoupled blind solving →
  forward-verification re-ranking; training-free core pipeline.
- **Fig. S2** (`docs/figures/fig4_dataset.png`) — IRexp composition: IR records →
  NMR-paired → structure-linked → full IR+¹H+¹³C+structure quadruples.
- **Fig. S3** (`docs/figures/fig2_size.png`) — accuracy vs molecular size (heavy-atom
  bucket); the monotonic 60%→7% top-1 gradient.
- **Fig. S4** (`docs/figures/fig6_electrolyte.png`) — top-1 and recovered accuracy on
  IRSpectra-Bench-Electrolyte by battery-electrolyte chemical class (n=46): sp³-C–F
  easiest (50%), sulfonyl and nitrile hardest (12%); overall 26%/28%.
- **Fig. S5** (`docs/figures/fig_generator_probe.png`) — trained-generator probe (§5.6;
  a complement, not part of the training-free protocol): candidate recall and
  deterministic-HOSE top-1 on the 194-compound benchmark for Claude / + scaffold
  enumeration / + trained generator. Enumeration's near-degenerate isomers collapse the
  verifier (28.4→16.0%) while the generator's formula-correct candidates convert
  (28.4→35.1%).
- **Fig. S6** (`docs/figures/fig_verifier.png`) — learned-verifier probe (§5.4; a
  complement, not part of the training-free protocol). (A) Conditional-on-recall top-1
  (n=19) for the four verifiers: a GNN trained on the same nmrshiftdb2 data as the HOSE
  lookup recovers the LLM verifier's 84% that the lookup (73%) could not. (B) Why: held-out
  ¹³C MAE — the learned model is ~2× sharper (1.70 vs 3.23 ppm).

---

## Data and code availability

All data and code are released in the project repository:
IRexp and the `irexp_resolved` split (`data/irexp/`, `data/irexp_resolved/`); the
benchmark rounds and within-compound control (`data/benchmark*/`, scored by
`scripts/benchmark_v2.py`); the battery-electrolyte case-study subset
(`data/benchmark_electrolyte/`, built by `scripts/build_electrolyte_bench.py`,
scored by `scripts/score_electrolyte.py`); the ground-truth integrity audit
(`scripts/validate_benchmark.py`, `data/benchmark*/clean_qids.json`); the
forward-verification and generate-wide experiments (`data/fverify/`, `data/gw/`,
`data/fverify2/`, `scripts/forward_verify.py`); the deterministic HOSE-code verifier
ablation (`scripts/hose_predict.py`, `data/fverify/hose_results.txt`); and the
dataset-mining pipeline (`spectro_scraper/`). Companion technical notes:
`docs/BENCHMARK.md` and `docs/FORWARD_VERIFY.md`.
The verifier negative-control and selective-prediction analyses
(`scripts/verifier_diagnostics.py`), the recall-headroom and scaffold-enumeration
study (`scripts/analyze_recall_headroom.py`, `scripts/enumerate_isomers.py`,
`scripts/closing_the_gap.py`), the modality-ablation harness
(`scripts/modality_ablation.py`, `docs/MODALITY_ABLATION.md`), and the blinded
expert-audit package (`data/audit/`, `docs/EXPERT_AUDIT_PROTOCOL.md`) are released
likewise. The §5.6 trained-generator probe ships as a self-contained bundle
(`contrib/generator_probe/`): generator candidates, the de-leaked split with its
InChIKey-14 manifest, and the verification scripts
(`scripts/closing_the_gap_gen.py`, `scripts/forward_verify_gen.py`,
`scripts/verify_leakage_exact40.py`); model checkpoints are deposited on Zenodo.
Downstream note: the public `irexp_release/train` split does **not** hold out
IRSpectra-Bench (117/200 InChIKey-14 overlap); de-leak with
`contrib/generator_probe/build_exp_manifest.py` before training models that will be
evaluated on the benchmark. The §5.4 learned-verifier probe ships its full reproducer —
`scripts/gnn_predict.py` (extract/train/score/control), the trained model
`data/nmrshiftdb/gnn_c13.pt`, per-compound results and both leakage checks
(`data/fverify/gnn_results.txt`), and the write-up `docs/VERIFIER_PROBE.md`; the GNN
trains on the same nmrshiftdb2 dump as the §5.4 HOSE lookup. **Archival deposit:** a complete frozen snapshot (dataset, benchmark, answer
keys, predictions, scripts, figure-regeneration, and the expert-audit package) will be
archived on Zenodo under DOI **[TODO: 10.5281/zenodo.XXXXXXX — mint on submission]**;
the GitHub repository is the development mirror and the Zenodo record the citable
version of record. (The held-out answer keys `data/audit/key.jsonl` and
`data/modality/key.json` are deposited but flagged "withhold from blinded reviewers".)

## Licensing and attribution

IRexp is derived from two open-access source pools and redistributed under terms
compatible with each (see `data/NOTICE`). **(a) Redistribution:** we release only
*extracted numeric data* — IR band lists, ¹H/¹³C shift lists, and resolved structures
(SMILES/SELFIES/InChIKey) — plus each record's source DOI/accession, not source full
text, figures, or PDFs. **(b) Two separable pools:** 119,345 records derive from the PMC
Open-Access Subset (**CC-BY-4.0**) and 1,888 from the Chemotion RADAR4Chem FT-IR deposit
(**CC-BY-SA-4.0**); the pools are kept separate and individually labelled, so users may
take the CC-BY pool alone, while any combined or Chemotion-derived release carries
CC-BY-SA-4.0 to honour the ShareAlike term. Code is released under the MIT License. **(c) Attribution:** re-users must cite
this dataset (Zenodo DOI above) and attribute the original publications via each record's
`source_doi`.

## Author Contributions

**I.Y.:** conceptualization, methodology,
software, formal analysis, investigation, data curation, visualization, writing —
original draft. **R.S.:** methodology, software, formal analysis, investigation,
validation (trained-generator and learned-verifier probes, §5.4 and §5.6), writing —
review and editing. **R.A.V.-H.:** conceptualization, methodology, supervision,
writing — review and editing.

## Conflicts of Interest

The authors declare no competing interests.

## Use of AI tools

This work studies a large language model, and LLMs were also used as instruments and as
writing aids; we state both roles explicitly. **As an object of study:** all reported
elucidation, forward-prediction and verification results were produced by Claude models
invoked under the protocol of §3 and §8 — these are the measurements the paper reports,
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
     Chemistry CSL style (docs/rsc.csl). Do not hand-number: cite with [@key] in the text
     and the list below is built automatically, in citation order. -->

::: {#refs}
:::
