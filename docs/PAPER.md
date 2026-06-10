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
under permissive licences. Second, an **open, blind, mechanically scored
benchmark** for spectrum→structure elucidation built on IRexp, deliberately
spanning molecular complexity. We find that a frontier LLM (Claude Opus), given
molecular formula + IR + ¹H + ¹³C, recovers the exact constitution of **~31%** of
real compounds (23% top-1; up to 55% on simpler molecules) — far below the ~100%
implied by curated evaluations, with the gap fully explained by compound
difficulty, candidate ranking, and hints. A within-compound control shows that
**solving each compound in an independent context with tool access roughly triples
accuracy over a single fatigued pass (5%→15%)**, i.e. methodology, not raw
capability, dominates reported numbers. Third, we introduce **forward-verification
elucidation**: candidates proposed by the (hard) inverse direction are re-ranked by
forward-predicting each one's ¹³C spectrum and matching it to the observed
spectrum. This exploits the generator–verifier gap — *when the true structure is
among the candidates, forward verification selects it 84% of the time, versus 73%
for the model's own ranking*. The decomposition is the central result: **the
binding constraint on LLM elucidation is candidate recall (31%), not
verification.** Acting on it — generating six regiochemistry-aware candidates per
compound and forward-verifying — lifts measured exact top-1 from 23% to **30%**
(recall 41%), while exposing a recall/precision tension that caps the training-free
approach below the naïve extrapolation. All experiments run with no model training
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
regiochemistry), and use it to localise the bottleneck. Throughout, the solver and
verifier are LLM agents run under a consumer subscription — no fine-tuning, no API
spend — making every experiment cheaply reproducible.

**Contributions.**
1. **IRexp** — the largest open experimental-IR dataset (121,233 records; 42,842
   structure-linked; 40,491 IR+¹H+¹³C+structure), with a reproducible mining
   pipeline.
2. An **open multimodal benchmark** and the first blind, mechanically scored,
   complexity-stratified evaluation of LLM structure elucidation on real data,
   reconciling the gap to optimistic prior reports.
3. **Forward-verification elucidation**, a training-free generator–verifier method,
   and the finding that **recall, not verification, bounds current performance**.

---

## 2. The IRexp dataset

### 2.1 Motivation

Open experimental IR is scarce: the largest freely available collections are the
NIST WebBook (~16k gas-phase spectra) and the Chemotion electronic-lab-notebook
deposit (~2k). Commercial libraries (e.g. Wiley KnowItAll, ~10⁵ spectra) are large
but closed and unusable for open model development. NMR is comparatively abundant,
but IR — which directly encodes functional groups complementary to NMR — has no
large open, structure-linked, ML-ready resource. IRexp fills this gap.

### 2.2 Construction

A per-compound IR band list, together with co-reported ¹H/¹³C NMR, follows a
remarkably stable textual convention in the experimental sections of organic
chemistry papers. We exploit this with a browser-free harvesting agent:

- **Discovery.** Open-access primary literature is enumerated through the NCBI
  E-utilities and harvested in bulk from the PMC Open-Access Subset on AWS S3
  (plain HTTPS, no anti-bot, fully redistributable CC-BY content), supplemented by
  the Chemotion FT-IR deposit (RADAR4Chem, CC-BY-SA-4.0).
- **Extraction.** A deterministic parser segments experimental text into
  per-compound records and extracts IR wavenumbers and ¹H/¹³C shift lists, with
  quality gates that reject instrument scan-range artefacts and prose
  false-positives (band-list density, ≥4 bands, plausible 400–4000 cm⁻¹ window).
- **Structure resolution.** In-text IUPAC names are converted to SMILES with OPSIN,
  canonicalised with RDKit (InChIKey, SELFIES), with a PubChem fallback for
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
6,833-molecule set used to train Spectro.¹ Provenance is 119,345 PMC-OA records
(CC-BY) plus 1,888 Chemotion records (CC-BY-SA); the two licences are kept as
separable pools. Each record is DOI-/accession-traceable. Re-resolution is additive
and content-keyed, so the dataset can be re-enriched without re-mining.

---

## 3. Benchmark design

From `irexp_resolved` we draw blind elucidation problems. Each problem presents the
**molecular formula** (as from HRMS), the **IR band list**, and the **¹H and ¹³C
shift lists** (with multiplicities and J-couplings where reported), and asks for the
structure. No name, SMILES, or hint is given. Problems are stratified into **simple**
(single ring, or two separate ring fragments; ≤22 heavy atoms) and **complex**
(fused/spiro/bridged rings, or >24 heavy atoms) by RDKit ring analysis. Compounds
seen in any earlier round are excluded from later rounds to prevent leakage.

**Scoring is mechanical.** A prediction is *correct* if its RDKit InChIKey
connectivity layer matches the reference (constitution; stereochemistry is reported
separately). We also report Morgan(2, 2048) Tanimoto to the reference as a graded
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
(formula + IR + ¹H + ¹³C, blind, up to three ranked candidates). On the richest
single round (40 fresh compounds):

| metric | overall | simple | complex |
|---|--:|--:|--:|
| recovered (within top-3) | 40% | 55% | 25% |
| top-1 exact constitution | 27% | 40% | 15% |
| right scaffold (Tanimoto ≥ 0.45) | 67% | — | — |
| mean best Tanimoto | 0.66 | 0.80 | 0.52 |

Pooling this round with a second decoupled round on 20 further compounds (§4.3)
gives the variance-corrected estimate over 60 compounds: **31% recovered / 23%
top-1**. The model reliably recovers molecular formula, functional groups, and
scaffold (67% scaffold-level), but the exact constitution far less often, failing
predominantly on **regiochemistry** — *which* position a substituent occupies. This
is consistent with an information limit of 1D data: many regioisomers have similar
¹H/¹³C shifts, which is precisely why 2D experiments (HMBC, NOESY) exist. The strong
simple→complex gradient (40%→15% top-1) confirms the benchmark is discriminating.

### 4.2 Reconciling with prior reports

Our 23–31% sits far below the ~100% on "simple" molecules reported for the same
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
hint-free, scraped regime, ~30% is the honest figure.

### 4.3 Methodology dominates: a within-compound control

The same 20 molecules were solved two ways: (a) by a single LLM context handling
all of them sequentially with no tools, and (b) by independent per-compound agents
with RDKit formula-checking. On the *identical* compounds, recovery rose from
**5% to 15%**, and top-1 from 0% to 15% — a 3× methodology effect with zero sample
confound. A different, easier 40-compound draw scored 40% under method (b),
demonstrating that single small benchmarks (n = 20–40) swing widely (15–40%); the
**pooled** decoupled estimate (n = 60) is 31% recovered / 23% top-1, which we take
as the robust figure. The practical lesson — fresh per-compound context plus tool
access roughly triples apparent performance — also explains part of the gap to
optimistic prior reports, whose per-problem API calls implicitly used method (b).

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
principle that verification is easier than generation, and requires no training. We
implemented the verifier as independent LLM agents that predict ¹³C shift lists from
SMILES alone (candidates shuffled and anonymised so isomers of one target never
co-occur; pure reasoning, no tools), and matched predicted to observed ¹³C with a
symmetric chamfer distance over peak sets.

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
single-pass baseline) — a real, measured gain with no training. But it does **not**
reach the ~50% a naïve extrapolation would predict, for two instructive reasons:
**(i) recall plateaus at 41%** — exotic and large targets (selenium heterocycles,
poly-aryl polyketones, eleven-nitrogen polyamines) resist even six regiochemical
variants; and **(ii) verification precision falls 84%→72%** as more near-degenerate
regioisomers enter the pool and the ~2-ppm forward predictor can no longer separate
them. This recall/precision tension is the honest ceiling of the training-free
approach: the recall-bound diagnosis stands, and closing the gap further requires
either sharper verification (a deterministic HOSE-code/DFT ¹³C predictor) or 2D-NMR
constraints, not merely more candidates.

---

## 6. Discussion

LLMs are not "solving structure elucidation" on realistic 1D data, but neither are
they failing: they are reliable **scaffold-level** elucidators (67%) and good
**verifiers** (84% conditional), with exact recovery throttled by candidate recall
and by the regiochemical underdetermination intrinsic to 1D NMR. This reframes the
engineering problem. Rather than training a bespoke spectra→structure model — a
target the frontier already meets at the scaffold level and that ages out each model
generation — the durable levers are (i) **open, hard, honestly scored benchmarks**
that expose specific failure modes (here, regiochemistry and recall), and (ii)
**inference-time scaffolding** (decoupled solving, generate-and-verify) that needs no
training and improves with each model. IRexp's IR modality and 2D-NMR-ready
provenance position it for the obvious next step: supplying the HMBC/COSY/NOESY
constraints that would attack regiochemistry at the source.

For practitioners, two operational findings transfer immediately: solve each problem
in a fresh context with tool access (≈3× over a single long context), and trust a
proposed structure in proportion to how well its forward-predicted spectrum matches
the observed one — while remembering the abstention caveat below.

---

## 7. Limitations

Several limitations of earlier drafts are now resolved with controlled experiments;
we state what remains plainly.

*Resolved.* **Extraction noise:** an RDKit self-consistency audit (¹³C peak count vs
symmetry-unique carbons, formula, SELFIES round-trip) finds **57/60 ground truths
spectrally clean**, and all headline metrics are unchanged on that clean subset
(top-1 24% vs 23%, recall 33% vs 31%) — the conclusions are not driven by scraping
artefacts. **Verifier precision / abstention:** the generate-wide experiment (§5.3)
quantifies the recall/precision tension directly — verification precision is
72–84% conditional on recall and degrades as near-degenerate regioisomers
accumulate, so forward-match distance is a strong *re-ranker* but a soft
*confidence* gauge; a deterministic HOSE-code/DFT ¹³C verifier is the identified
fix. **Projection:** §5.2's extrapolation is replaced by the **measured** §5.3
result (top-1 30%, recall 41%) — and is honestly below the optimistic estimate.

*Independence checks.* Scoring throughout is mechanical RDKit (not LLM-judged), and
all solver/verifier transcripts are audited for zero web access and zero
ground-truth access; a second model family (Sonnet) is included as an independent
cross-model solver to test that the recall-bound result is not specific to one model.

*Remaining.* **(i) Human audit:** solver and verifier are both LLMs; the one check we
cannot perform ourselves is an expert-chemist review of a sample of elucidations and
forward predictions, which is required before deployment-grade claims. **(ii) Scale:**
the controlled rounds are n = 60 with demonstrated sample variance; a larger
(n ≈ 150) benchmark would tighten the estimates, and the free agent harness makes it
feasible.

---

## 8. Methods

**Mining and resolution.** PMC-OA full text was fetched from `s3://pmc-oa-opendata`;
records were extracted with a deterministic parser and resolved with OPSIN, RDKit,
and SELFIES, with an optional cached PubChem fallback. Durable content-keyed caches
make resolution additive and restart-safe.

**Benchmark and agents.** Problems were sampled from `irexp_resolved`, stratified by
RDKit ring analysis, with cross-round de-duplication by InChIKey. Solver and
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

## Data and code availability

All data and code are released in the project repository:
IRexp and the `irexp_resolved` split (`data/irexp/`, `data/irexp_resolved/`); the
benchmark rounds and within-compound control (`data/benchmark*/`, scored by
`scripts/benchmark_v2.py`); the ground-truth integrity audit
(`scripts/validate_benchmark.py`, `data/benchmark*/clean_qids.json`); the
forward-verification and generate-wide experiments (`data/fverify/`, `data/gw/`,
`data/fverify2/`, `scripts/forward_verify.py`); and the mining/resolution pipeline
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
