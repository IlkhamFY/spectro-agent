# An open multimodal benchmark for LLM molecular structure elucidation reveals a recall-bound bottleneck that forward verification exploits

**Ilkham F.**¹ *(corresponding: ilkhamfy@gmail.com)*
¹ Affiliation TBD

*Manuscript draft prepared for Digital Discovery (RSC).*

---

## Abstract

Large language models (LLMs) have recently been shown to predict NMR spectra and
propose molecular structures from them, but the supporting evaluations are small,
curated, NMR-only, and hinted — leaving the real-world question unanswered: given
an unfiltered experimental spectrum from the literature, how often does a frontier
LLM recover the correct structure? We address this with three contributions.
First, **IRexp**, the largest open dataset of *experimental* infrared spectra —
121,233 records mined from open-access full text, of which **42,842 are linked to
a resolved 2D structure** and **40,491 are full IR + ¹H + ¹³C + structure
quadruples** — assembled by a browser-free literature-mining agent and released
under permissive licences. Second, **IRSpectra-Bench**, an open, blind,
mechanically scored benchmark of **194 spectrally-validated compounds** for
spectrum→structure elucidation, stratified across molecular complexity. We find
that a frontier LLM (Claude Opus), given molecular formula + IR + ¹H + ¹³C,
recovers the exact constitution of **28.4%** of real compounds (95% CI 22–35;
33.5% within three candidates), with a sharp, tight gradient — 48% on simple
molecules versus 8% on complex ones, and 60% for small (≤15 heavy atoms) versus
7% for large (>25). This sits far below the ~100% implied by curated evaluations,
a gap fully explained by compound difficulty, candidate ranking, and hints.
A within-compound control shows that **solving each compound in an independent
context with tool access roughly triples accuracy over a single fatigued pass
(5%→15%)**, i.e. methodology, not raw capability, dominates reported numbers.
Third, we introduce **forward-verification elucidation**: candidates proposed by
the (hard) inverse direction are re-ranked by
forward-predicting each one's ¹³C spectrum and matching it to the observed
spectrum. This exploits the generator–verifier gap — *when the true structure is
among the candidates, forward verification selects it 84% of the time, versus 73%
for the model's own ranking*. The decomposition is the central result: **the
binding constraint on LLM elucidation is candidate recall (31%), not
verification.** Acting on it — generating six regiochemistry-aware candidates per
compound and forward-verifying — lifts measured exact top-1 from 23% to **30%**
(recall 41%), while exposing a recall/precision tension that caps the training-free
approach below the naïve extrapolation. We then stress-test the finding in a
**battery-electrolyte domain** — a curated subset (48 compounds, 46 scored) spanning
the carbonate, sulfonyl, nitrile, fluorinated, phosphoryl, and glyme functional
classes central to electrolyte chemistry — where accuracy holds at the same level
(**26% top-1**) along
a chemically interpretable gradient (sp³-C–F easiest at 50%; sulfonyl and nitrile
hardest at 12%), and we cast forward-verification as the training-free analog of the
computational-NMR / NMR-crystallography validation that chemists already trust. All
experiments run with no model training
and no paid API, using LLM agents under a standard subscription, and all data,
predictions, and code are released.

---

## 1. Introduction

Determining a molecule's structure from its spectra is a central, time-consuming
task in synthetic and analytical chemistry. The dominant machine-learning approach
trains specialised encoder–decoder models to map spectra to structures; the recent
*Spectro* model, for example, learns ¹H/¹³C/IR → SELFIES from a corpus of 6,833
molecules.¹ In parallel, general-purpose LLMs have been reported to perform the
same task off-the-shelf: a 2026 study found that Claude Opus matched or beat
commercial NMR-prediction software in the forward direction (structure→spectrum,
±0.08 ppm ¹H) and "recovered all eight simpler structures on every attempt" in the
inverse direction (spectrum→structure).²

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
regiochemistry), and use it to localise the bottleneck. **Figure 1** summarises the
end-to-end design. Throughout, the solver and verifier are LLM agents run under a
consumer subscription — no fine-tuning, no API spend — making every experiment cheaply
reproducible.

**Contributions.**
1. **IRexp** — the largest open experimental-IR dataset (121,233 records; 42,842
   structure-linked; 40,491 IR+¹H+¹³C+structure), with a reproducible mining
   pipeline.
2. An **open multimodal benchmark** and the first blind, mechanically scored,
   complexity-stratified evaluation of LLM structure elucidation on real data,
   reconciling the gap to optimistic prior reports.
3. **Forward-verification elucidation**, a training-free generator–verifier method,
   and the finding that **recall, not verification, bounds current performance**.

### 1.1 Related work

**Trained spectra→structure models.** The dominant line trains sequence or graph
decoders to emit structures from spectra: *Spectro* (¹H/¹³C/IR→SELFIES)¹, the
multitask CNN+transformer of routine 1D-NMR¹¹, and set/graph transformers such as
NMRTrans¹². These reach high accuracy *in-distribution* but require a labelled
spectra→structure corpus, which is exactly the scarce resource our IRexp pipeline
targets, and they are retrained per modality. Closest in spirit to our multimodal
setting is **NMIRacle**¹³, a generative model conditioned jointly on IR + ¹H + ¹³C;
it is a strong trained baseline, whereas our contribution is the *open experimental-IR
data it (and others) can train on*, plus a *training-free* protocol and a blind
benchmark to measure it.

**LLMs as elucidators.** General-purpose LLMs have been applied off-the-shelf —
Anthropic's forward/inverse study², SpectraLLM and MolSpectLLM (multimodal LLMs over
multi-spectral input)¹⁴, and knowledge-enhanced tree-search reasoning¹⁵.
Contemporary multimodal *benchmarks* have also begun to appear. Our evaluation
differs in being built on **real, literature-mined experimental spectra** (not
simulated or curated puzzle sets), **blind and mechanically scored** with bootstrap
CIs, **complexity-stratified**, and explicitly **reconciled** against the optimistic
prior report it most resembles² — and in isolating *where* performance is lost
(recall vs. verification) rather than reporting a single aggregate.

**Computational NMR for structure validation.** Our forward-verification method is
the LLM analog of a workflow chemists already trust: assign a structure by computing
the spectrum each candidate *would* give and matching it to experiment. In solution,
this is the DP4 / DP4+ probabilistic framework over GIAO-DFT shifts¹⁶ ¹⁷; in the
solid state it is **NMR crystallography**, where GIPAW-computed shifts adjudicate
between candidate structures¹⁸ ¹⁹. We replace the quantum-chemical predictor with a
forward LLM, trading accuracy for zero setup cost, and inherit the same core
principle — *verification by forward prediction is easier than inverse generation*.

---

## 2. The IRexp dataset

### 2.1 Motivation

Open experimental IR is scarce: the largest freely available collections are the
NIST WebBook⁸ (~16k gas-phase spectra) and the Chemotion electronic-lab-notebook⁷
deposit (~2k). Commercial libraries (e.g. Wiley KnowItAll, ~10⁵ spectra) are large
but closed and unusable for open model development. NMR is comparatively abundant,
but IR — which directly encodes functional groups complementary to NMR — has no
large open, structure-linked, ML-ready resource. IRexp fills this gap.

### 2.2 Construction

A per-compound IR band list, together with co-reported ¹H/¹³C NMR, follows a
remarkably stable textual convention in the experimental sections of organic
chemistry papers. We exploit this with a browser-free harvesting agent:

- **Discovery.** Open-access primary literature is enumerated through the NCBI
  E-utilities and harvested in bulk from the PMC Open-Access Subset⁶ on AWS S3
  (plain HTTPS, no anti-bot, fully redistributable CC-BY content), supplemented by
  the Chemotion FT-IR deposit (RADAR4Chem, CC-BY-SA-4.0).
- **Extraction.** A deterministic parser segments experimental text into
  per-compound records and extracts IR wavenumbers and ¹H/¹³C shift lists, with
  quality gates that reject instrument scan-range artefacts and prose
  false-positives (band-list density, ≥4 bands, plausible 400–4000 cm⁻¹ window).
- **Structure resolution.** In-text IUPAC names are converted to SMILES with OPSIN³,
  canonicalised with RDKit⁴ (InChIKey, SELFIES⁵), with a PubChem fallback for
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

| field | value |
|---|--:|
| experimental IR records | **121,233** |
| …co-reporting ¹H and/or ¹³C NMR | 87,075 (72%) |
| …with a resolved 2D structure | **42,842 (35%)** |
| full IR + ¹H + ¹³C + structure quadruples | **40,491** |

A structure-complete split, **`irexp_resolved`** (42,842 records, 100%
structure-linked), is the training-/benchmark-ready subset and is ~6× the
6,833-molecule set used to train Spectro¹ (Fig. 2). Provenance is 119,345 PMC-OA records
(CC-BY) plus 1,888 Chemotion records (CC-BY-SA); the two licences are kept as
separable pools. Each record is DOI-/accession-traceable. Re-resolution is additive
and content-keyed, so the dataset can be re-enriched without re-mining.

---

## 3. Benchmark design (IRSpectra-Bench)

From `irexp_resolved` we draw **IRSpectra-Bench**, 194 blind elucidation problems.
Each problem presents the **molecular formula** (as from HRMS), the **IR band
list**, and the **¹H and ¹³C shift lists** (with multiplicities and J-couplings
where reported), and asks for the structure. No name, SMILES, or hint is given.
Every ground-truth structure is **spectrally validated** by an automated RDKit
consistency check (¹³C peak count vs symmetry-unique carbons, molecular-formula
match, SELFIES round-trip), excluding records with merged or incomplete spectra
(6/140 in the main round). Problems are stratified into **simple** (single ring,
or two separate ring fragments; ≤22 heavy atoms) and **complex** (fused/spiro/
bridged rings, or >24 heavy atoms) by RDKit ring analysis (98 simple / 96 complex),
with InChIKey de-duplication across all rounds to prevent leakage.

**Scoring is mechanical.** A prediction is *correct* if its RDKit InChIKey
connectivity layer matches the reference (constitution; stereochemistry is reported
separately). We also report Morgan(2, 2048)⁹ Tanimoto to the reference as a graded
"right scaffold/family" signal, and, where multiple ranked candidates are allowed,
*recovered* = the reference appears among them (matching the protocol of ref. 2).

**Solvers are LLM agents run under a consumer subscription.** A frontier LLM (Claude
Opus) is invoked as an independent sub-agent per batch of problems; agents are
closed-book (transcript-audited for zero web access and zero ground-truth access)
and may use RDKit only to check a candidate's molecular formula. This makes the
benchmark free to run and reproducible without API credits.

---

## 4. How well do LLMs elucidate real structures?

### 4.1 Headline performance

Decoupled per-compound agents solve each problem in an independent context
(formula + IR + ¹H + ¹³C, blind, up to three ranked candidates). Over the full
**194-compound benchmark** (134 spectrally-validated compounds + the 60 from the
controlled rounds), with bootstrap 95% confidence intervals:

| metric | overall (n=194) | simple (n=98) | complex (n=96) |
|---|--:|--:|--:|
| top-1 exact constitution | **28.4%** [22–35] | 48.0% [39–57] | 8.3% [3–15] |
| recovered (within top-3) | 33.5% [27–40] | 54.1% [44–63] | 12.5% [6–20] |
| mean best Tanimoto | 0.59 | 0.73 | 0.45 |

The gradient is sharp and the intervals are tight. The 48%→8% simple→complex
separation (Fig. 3) confirms the benchmark is discriminating across a realistic
difficulty range, and accuracy falls monotonically with molecular size in step with
it — top-1 **60.5%** for ≤15 heavy atoms, 28.3% for 16–25, and **7.0%** above 25
(Fig. 4). The model reliably recovers molecular formula, functional groups, and
scaffold, but the exact constitution far less often, failing predominantly on
**regiochemistry** — *which* position a substituent occupies. This is consistent
with an information limit of 1D data: many regioisomers have similar ¹H/¹³C shifts,
which is precisely why 2D experiments (HMBC, NOESY) exist.

### 4.2 Reconciling with prior reports

Our 28% top-1 sits far below the ~100% on "simple" molecules reported for the same
model class.² The gap is fully attributable to methodology, not capability:

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
experimental¹; and NMIRacle, which like us conditions jointly on IR+¹H+¹³C with *no*
hints, reports 48% top-1 / 66% top-15 exact-SMILES recovery — again on held-out
molecules from a *simulated* corpus drawn from the training distribution¹³. We measure
28.4% top-1 (33.5% top-3; 30% with forward verification) on **blind, real,
literature-mined experimental** spectra of out-of-distribution compounds. These are
not comparable as a leaderboard; read as a *bound on the simulated-to-real gap*, the
contrast suggests that high in-distribution accuracies substantially overstate
real-world performance — the same gap we document for the LLM above. The instability
of the metric itself reinforces the caution: on the MolPuzzle benchmark (IR+MS+¹H+¹³C
with the molecular formula given), reported exact-match accuracy for a single model
(GPT-4o) ranges from 1.4%²⁰ to 27.8%¹⁵ depending only on the scoring harness — a ~20×
swing that is itself the argument for the single, fully specified, mechanically scored
protocol we adopt.

### 4.3 Methodology dominates: a within-compound control

The same 20 molecules were solved two ways: (a) by a single LLM context handling
all of them sequentially with no tools, and (b) by independent per-compound agents
with RDKit formula-checking. On the *identical* compounds, recovery rose from
**5% to 15%**, and top-1 from 0% to 15% — a 3× methodology effect with zero sample
confound. Small rounds also swing widely (15–40% across n=20–40 draws), which is
why the headline is the full **194-compound** figure (28.4% top-1, 95% CI 22–35)
rather than any single round. The practical lesson — fresh per-compound context
plus tool access roughly triples apparent performance — also explains part of the
gap to
optimistic prior reports, whose per-problem API calls implicitly used method (b).

### 4.4 Model comparison: the benchmark discriminates capability

A benchmark is only useful if it separates models. On a fixed 24-compound subset
solved blind by four Claude models — spanning a wide capability range, including the
newest (Fable 5) — under the identical protocol (Fig. 5):

| model | top-1 | recovered |
|---|--:|--:|
| Claude Fable 5 | **45%** | 54% |
| Claude Opus | 25% | 29% |
| Claude Sonnet | 20% | 25% |
| Claude Haiku | **0%** | 4% |

Three signals matter here. First, the four models rank in **monotonic capability
order** (Fable ≫ Opus > Sonnet ≫ Haiku), and the smallest is **floored at 0% exact**
(4% recovered) on the same problems — so the benchmark is **capability-sensitive**
and not a coin-flip. Second, two mid-tier frontier models agree closely (Opus 25%,
Sonnet 20%), so the recall-bound ~25% regime of §4.1 is **not an artefact of a single
model**. Third, the newest model nearly **doubles** the next-best top-1 (45% vs 25%
on identical compounds) yet still misses the majority — IRSpectra-Bench is **hard and
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

Performance lands in the **same regime as the headline benchmark** — overall
**top-1 26%, recovered 28%** (12/46 and 13/46; two compounds received no
parseable candidate) — confirming that the bottleneck is a property of the
elucidation task, not of any one chemical neighbourhood. The per-class
breakdown (Fig. 6) is itself informative:

| electrolyte class | n | top-1 | recovered (top-3) |
|---|--:|--:|--:|
| sp³-C–F | 8 | **50%** | 50% |
| carbonate | 7 | 29% | 43% |
| phosphoryl | 8 | 25% | 25% |
| glyme / oligoether | 7 | 29% | 29% |
| sulfonyl / sulfonate | 8 | **12%** | 12% |
| nitrile | 8 | **12%** | 12% |

The gradient is chemically legible. **sp³-C–F** centres are the easiest:
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
the one observed — is the inverse-problem analog of computational-NMR /
NMR-crystallography structure validation that the magnetic-resonance community
already trusts. The subset, its per-class answers, and the scorer are released
with the benchmark.

---

## 5. Forward-verification elucidation

### 5.1 Method

The inverse direction is the model's hard, isomer-blind direction; the **forward**
direction (structure→spectrum) is its easy, accurate one.² Regioisomers, crucially,
have *different* forward-predicted ¹³C shifts. We therefore close a generator–
verifier loop:

> **generate** candidate structures (inverse) → **forward-predict** each candidate's
> ¹³C spectrum, blind to the observed spectrum → **re-rank** candidates by the
> distance between predicted and observed ¹³C → return the best match.

This mirrors how a chemist confirms a structure ("if it were that isomer, C-3 would
be at ~120 ppm; we observe 135, so it is the other"), exploits the standard
principle that verification is easier than generation, and requires no training.
**Figure 7** shows the mechanism on a real benchmark pair — the picolinamide /
nicotinamide regioisomers, which the inverse task cannot separate but whose
forward-predicted ¹³C spectra match the observed one at 0.42 vs 1.30 ppm. We
implemented the verifier as independent LLM agents that predict ¹³C shift lists from
SMILES alone (candidates shuffled and anonymised so isomers of one target never
co-occur; pure reasoning, no tools), and matched predicted to observed ¹³C with a
symmetric chamfer distance over peak sets.

Conceptually this is **NMR-crystallography logic with an LLM in place of the quantum
chemistry**: where DP4/DP4+ rank candidates by GIAO-DFT shifts¹⁶ ¹⁷ and NMR
crystallography adjudicates polymorphs and connectivity by GIPAW-computed shifts¹⁸ ¹⁹,
we rank by the shifts a forward LLM predicts. The trade is deliberate — we forgo the
≈1–2 ppm accuracy and rigorous error model of DFT for a predictor that runs in
seconds at zero setup, and we quantify below exactly how far that cheaper verifier
carries the inverse problem.

### 5.2 Result

On the 60 benchmark compounds (126 candidate structures from the solver agents):

| | value |
|---|--:|
| generation recall (true structure among candidates) | **31%** |
| top-1, solver self-ranking | 23% |
| top-1, **forward-verified re-ranking** | 26% |
| **conditional on recall — self-ranking** | 14/19 (**73%**) |
| **conditional on recall — forward-verification** | 16/19 (**84%**) |

The decomposition is the finding. **When the true structure is among the
candidates, forward verification selects it 84% of the time, versus 73% for the
model's own ranking (+11 points)** — a real, exploitable generator–verifier gap.
The overall top-1 moves only 23%→26% because the binding constraint is **generation
recall**: the true structure was never proposed for 41 of 60 compounds, which no
re-ranking can repair.

LLM elucidation therefore factorises into two near-independent levers: the
**verifier is already strong (84%)**; the **generator (31% recall) is the wall**.

### 5.3 Generate-wide: testing the recipe

The decomposition implies a recipe — *generate wide, verify by forward prediction*.
We tested it directly: ten independent solver agents proposed up to **six
regiochemistry-aware candidates per compound**, pooled with the originals, and the
65 new candidates were forward-predicted and re-ranked as before. The measured
result:

| | original | generate-wide |
|---|--:|--:|
| recall (true structure among candidates) | 31% | **41%** |
| forward-verified top-1 | 26% | **30%** |
| verification precision (conditional on recall) | 84% | 72% |

Wide generation lifts recall +10 points and exact top-1 +7 points (23%→30% over the
self-ranking baseline on the same 60 compounds; Fig. 8) — a real, measured gain with
no training. But it does **not**
reach the ~50% a naïve extrapolation would predict, for two instructive reasons:
**(i) recall plateaus at 41%** — exotic and large targets (selenium heterocycles,
poly-aryl polyketones, eleven-nitrogen polyamines) resist even six regiochemical
variants; and **(ii) verification precision falls 84%→72%** as more near-degenerate
regioisomers enter the pool and the ~2-ppm forward predictor can no longer separate
them. This recall/precision tension is the honest ceiling of the training-free
approach: the recall-bound diagnosis stands, and closing the gap further requires
either sharper verification or 2D-NMR constraints, not merely more candidates.

### 5.4 Does a deterministic verifier help? A HOSE-code ablation

§5.3 and a natural reading of the verifier-precision story suggest an obvious fix:
swap the LLM forward-predictor for a *deterministic* ¹³C predictor with a rigorous
error model. We tested the canonical choice — a **HOSE-code-style lookup trained on
nmrshiftdb2** (RDKit radial-environment bins, spheres r=4→1 with a hybridisation
prior fallback; 31,000 molecules, 332,595 assigned carbons; held-out **MAE 3.23 ppm,
median 1.73 ppm**) — as a drop-in replacement for the verifier, re-ranking the same
§5.2 candidates.

It does **not** help. The HOSE verifier recovers **14/19 (73%)** of the in-set
compounds — identical to the solver's own ranking and *below* the LLM verifier's
**16/19 (84%)** on the same set. The reason is coverage, not the method: of the 2,244
candidate carbons, only **2%** match a training environment at the most specific
sphere (r=4) and **67%** resolve only at coarse spheres (r≤2), because the benchmark's
exotic chemistry (selenium heterocycles, polyaryl ketones, large polyamines) is
under-represented in nmrshiftdb2. A coarse environment cannot separate the regioisomers
the verifier exists to separate, so the deterministic predictor degrades to the
self-rank baseline exactly where discrimination is needed — whereas the LLM
forward-predictor generalises across novel scaffolds. The practical lesson is the
opposite of the naïve one: on hard, real chemistry the LLM's *breadth* is an asset for
verification, and the genuine fix is sharper still — **compound-specific (DFT-level)
shift accuracy or orthogonal 2D-NMR constraints**, not a generic lookup table.

---

## 6. Discussion

LLMs are not "solving structure elucidation" on realistic 1D data, but neither are
they failing: they are reliable **scaffold-level** elucidators (mean best Tanimoto 0.59; 0.73 on
simple molecules) and good **verifiers** (84% conditional), with exact recovery
throttled by candidate recall
and by the regiochemical underdetermination intrinsic to 1D NMR. This reframes the
engineering problem. Rather than training a bespoke spectra→structure model — a
target the frontier already meets at the scaffold level and that ages out each model
generation — the durable levers are (i) **open, hard, honestly scored benchmarks**
that expose specific failure modes (here, regiochemistry and recall), and (ii)
**inference-time scaffolding** (decoupled solving, generate-and-verify) that needs no
training and improves with each model. IRexp's IR modality and 2D-NMR-ready
provenance position it for the obvious next step: supplying the HMBC/COSY/NOESY
constraints that would attack regiochemistry at the source.

That the bottleneck reproduces almost exactly inside a single application domain
(§4.5: 26% top-1 on battery-electrolyte chemistry, against 28% overall) is itself
evidence that it is structural rather than incidental — and it makes the
forward-verification recipe directly relevant to the magnetic-resonance workflows
(electrolyte-decomposition assignment, NMR crystallography) where computing a
candidate's spectrum to confirm it is already standard practice.

For practitioners, two operational findings transfer immediately: solve each problem
in a fresh context with tool access (≈3× over a single long context), and trust a
proposed structure in proportion to how well its forward-predicted spectrum matches
the observed one — while remembering the abstention caveat below.

---

## 7. Limitations

Several limitations of earlier drafts are now resolved with controlled experiments;
we state what remains plainly.

*Resolved.* **Extraction noise:** an RDKit self-consistency audit¹⁰ (¹³C peak count vs
symmetry-unique carbons, formula, SELFIES round-trip) finds **57/60 ground truths
spectrally clean**, and all headline metrics are unchanged on that clean subset
(top-1 24% vs 23%, recall 33% vs 31%) — the conclusions are not driven by scraping
artefacts. **Verifier precision / abstention:** the generate-wide experiment (§5.3)
quantifies the recall/precision tension directly — verification precision is
72–84% conditional on recall and degrades as near-degenerate regioisomers
accumulate, so forward-match distance is a strong *re-ranker* but a soft
*confidence* gauge. We further tested the obvious deterministic fix (§5.4): a
nmrshiftdb2-trained HOSE-code ¹³C predictor does **not** beat the LLM verifier
(73% vs 84% conditional), because its specific-environment coverage collapses on the
benchmark's exotic chemistry — so the identified fix is compound-specific DFT-level
accuracy or 2D-NMR constraints, not a generic lookup. **Projection:** §5.2's
extrapolation is replaced by the **measured** §5.3
result (top-1 30%, recall 41%) — and is honestly below the optimistic estimate.

*Independence checks.* Scoring throughout is mechanical RDKit (not LLM-judged), and
all solver/verifier transcripts are audited for zero web access and zero
ground-truth access. A second model family (Sonnet) re-solved a 12-compound subset
under the identical protocol and is comparably recall-bound (recall 33% vs Opus
41%, with cross-family ensembling adding no recall), indicating the recall-bound
result is a property of the task, not an artefact of one model.

*Remaining.* **(i) Human audit:** solver and verifier are both LLMs; the one check we
cannot perform ourselves is an expert-chemist review of a sample of elucidations and
forward predictions, which is required before deployment-grade claims. **(ii)
Single vendor:** the headline uses one frontier model (Claude Opus) and the
cross-model comparison spans **four Claude-family models** (§4.4: Fable 5 45% ≫ Opus
25% > Sonnet 20% ≫ Haiku 0% on a common 24-compound subset); a true cross-*vendor*
sweep (GPT-class, Gemini-class, open models) needs API access we deliberately did
without, but the large, monotonic capability spread within one family makes it
unlikely the recall-bound, complexity-graded pattern is specific to one model
lineage. **(iii) Domain-subset scope:** the
battery-electrolyte case study (§4.5) comprises *literature compounds bearing
electrolyte-relevant functional chemistry* drawn from the open corpus — not operando
or in-cell decomposition spectra — so it demonstrates functional-class transfer of
the elucidation bottleneck, not direct assignment of authentic interphase/degradation
products, which would require a dedicated operando spectral set.

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
transcript grep for zero web/answer access. Scoring used RDKit InChIKey-connectivity
matching and Morgan(2, 2048) Tanimoto; forward-verification used a symmetric chamfer
distance over ¹³C peak sets. No model was trained or fine-tuned; no paid API was
used.

**Reproducibility.** Every round is frozen: questions, ground-truth answers,
per-agent raw outputs, predictions, and scorer outputs are released, and the sampler,
scorer, and forward-verification harness are scripted end-to-end.

---

## Figures

- **Fig. 1** (`docs/figures/fig0_overview.png`) — study design: open multimodal data
  (IRexp) → blind, complexity-stratified benchmark → decoupled blind solving →
  forward-verification re-ranking; training-free throughout.
- **Fig. 2** (`docs/figures/fig4_dataset.png`) — IRexp composition: IR records →
  NMR-paired → structure-linked → full IR+¹H+¹³C+structure quadruples.
- **Fig. 3** (`docs/figures/fig1_difficulty.png`) — top-1 and recovered accuracy on
  IRSpectra-Bench by difficulty (all / simple / complex, n=194) with bootstrap 95% CIs.
- **Fig. 4** (`docs/figures/fig2_size.png`) — accuracy vs molecular size (heavy-atom
  bucket); the monotonic 60%→7% top-1 gradient.
- **Fig. 5** (`docs/figures/fig5_models.png`) — four-model comparison on a 24-compound
  subset: Fable 5 45% ≫ Opus 25% > Sonnet 20% ≫ Haiku 0% top-1; the benchmark
  discriminates capability monotonically and is far from saturated even for the
  newest model.
- **Fig. 6** (`docs/figures/fig6_electrolyte.png`) — top-1 and recovered accuracy on
  IRSpectra-Bench-Electrolyte by battery-electrolyte chemical class (n=46): sp³-C–F
  easiest (50%), sulfonyl and nitrile hardest (12%); overall 26%/28%, the same
  regime as the headline benchmark.
- **Fig. 7** (`docs/figures/fig_mechanism.png`) — forward-verification on a real
  benchmark regioisomer pair (picolinamide vs nicotinamide): forward-predicted ¹³C
  matches the true isomer (chamfer 0.42 vs 1.30 ppm), the LLM analog of
  NMR-crystallography.
- **Fig. 8** (`docs/figures/fig3_method.png`) — inference-time methodology ladder:
  single-pass → decoupled agents → generate-wide + forward-verify (5%→23%→30%).

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
mining/resolution pipeline
(`scripts/`). Companion technical notes: `docs/BENCHMARK.md`, `docs/BENCHMARK_v2.md`,
`docs/BENCHMARK_v3.md`, `docs/FORWARD_VERIFY.md`, and `data/SPECTRO_TRAINING_DATA.md`.

## References

1. *Spectro: transformer-based molecular structure elucidation from spectra.*
   ChemRxiv, 2024, doi:10.26434/chemrxiv-2024-37v2j.
2. Anthropic. *Making Claude a Chemist.* 2026.
   anthropic.com/research/making-claude-a-chemist.
3. Lowe, D. M. et al. *Name to Structure (OPSIN).* J. Chem. Inf. Model. 2011, 51, 739.
4. Landrum, G. *RDKit: Open-source cheminformatics.* rdkit.org.
5. Krenn, M. et al. *SELFIES.* Mach. Learn.: Sci. Technol. 2020, 1, 045024.
6. *NCBI PMC Open Access Subset.* National Library of Medicine.
7. *Chemotion repository / RADAR4Chem*, doi:10.22000/OGoEQGlsZGElrgst.
8. *NIST Chemistry WebBook*, SRD 69.
9. Rogers, D.; Hahn, M. *Extended-connectivity fingerprints.* J. Chem. Inf. Model.
   2010, 50, 742.
10. Wang, X. et al. *Self-consistency improves chain-of-thought reasoning.* ICLR 2023.
11. *Accurate and efficient structure elucidation from routine one-dimensional NMR
    spectra using multitask machine learning.* arXiv:2408.08284, 2024.
12. *NMRTrans: structure elucidation from experimental NMR spectra via set
    transformers.* arXiv:2602.10158, 2026.
13. Ottomano, F.; Li, Y.; Ganose, A. M. *NMIRacle: multi-modal generative molecular
    elucidation from IR and NMR spectra.* arXiv:2512.19733, 2025.
14. *SpectraLLM / MolSpectLLM: multimodal language models for molecular structure
    elucidation from multi-spectral input.* arXiv:2508.08441; arXiv:2509.21861, 2025.
15. *Boosting LLM molecular structure elucidation with knowledge-enhanced tree-search
    reasoning.* arXiv:2506.23056, 2025.
16. Smith, S. G.; Goodman, J. M. *Assigning stereochemistry to single diastereoisomers
    by GIAO NMR calculation: the DP4 probability.* J. Am. Chem. Soc. 2010, 132, 12946.
17. Grimblat, N.; Zanardi, M. M.; Sarotti, A. M. *Beyond DP4: an improved probability
    for the stereochemical assignment of isomeric compounds (DP4+).* J. Org. Chem.
    2015, 80, 12526.
18. Pickard, C. J.; Mauri, F. *All-electron magnetic response with pseudopotentials:
    NMR chemical shifts (GIPAW).* Phys. Rev. B 2001, 63, 245101.
19. Ashbrook, S. E.; McKay, D. *Combining solid-state NMR spectroscopy with
    first-principles calculations — a guide to NMR crystallography.* Chem. Commun.
    2016, 52, 7186.
20. Guo, K. et al. *MolPuzzle: a benchmark for molecular structure elucidation with
    multimodal large language models.* NeurIPS 2024 (Datasets and Benchmarks Track).
