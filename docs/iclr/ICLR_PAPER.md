# Generation Recall, Not Verification, Binds LLM Structure Elucidation from Literature Spectra

<!-- ICLR track draft (anonymous-ready). Source: docs/archive/combined_PAPER.md
     (snapshot of the combined JCIM-shaped manuscript). Do not edit docs/paper.tex
     or treat this file as a replacement for docs/PAPER.md.
     Companion Data Descriptor: Scientific Data manuscript (in prep) for IRexp.
     Figure paths still point at docs/figures/* pending a dedicated ICLR figure pack. -->

**Anonymous authors**

Paper under double-blind review. Code, frozen predictions, and scoring scripts will be
released with the camera-ready version. Dataset: Hugging Face mirror
[`ilkhamfy/IRexp`](https://huggingface.co/datasets/ilkhamfy/IRexp); full Data Descriptor
for the corpus is a companion *Scientific Data* manuscript (in preparation).

---

## Abstract

Frontier large language models are often presented as near-solved structure elucidators on
curated spectra. We ask a harder, more operational question: given the molecular formula and
**literature-reported** IR / ¹H / ¹³C **peak lists** — not digitised traces — can an
off-the-shelf LLM recover the correct constitution, and **which stage fails** when it does
not?

We introduce **IRSpectra-Bench**, a blind, mechanically scored peak-list benchmark of 194
compounds drawn from redistributable experimental band lists (**IRexp**; companion Data
Descriptor), with a fixed RDKit InChIKey-connectivity scoring contract and decomposable
**generation recall** / **verification precision** metrics. On IRSpectra-Bench, a frontier
LLM recovers the correct constitution for **28%** top-1 (95% CI 22–35), or **15%** once
reweighted to corpus composition. The bottleneck is **candidate proposal, not
verification**: the true structure enters the pool for only **34%** of compounds, and where
it does, training-free forward-verification selects it **89%** of the time (58/65). The same
recall ≪ precision asymmetry replicates across **four vendor families**. A formula-only
control drops top-1 from 23% → 5%; accuracy is flat in source-paper year. Generating wider
lifts recall 32% → 42% and top-1 23% → 30% on 60 compounds, while verification alone moves
whole-benchmark top-1 only 28% → 30%. Recovered from published top-*k* figures, recall
carries **68–83%** of the accuracy collapse when systems move from curated or simulated data
to real heterogeneous spectra. Frozen predictions, scorers and code are released for
mechanical re-evaluation.

---

## 1. Introduction {#sec:introduction}

Structure elucidation from spectra sits at the centre of synthetic and analytical chemistry,
and machine learning increasingly treats it as a sequence or agent task. Encoder–decoder
models train on paired corpora [@chacko2024spectro; @ottomano2025nmiracle; @alberts2024ir];
LLM agents and puzzle benches report high recovery on curated or education spectra
[@kamber2026chemist; @guo2024molpuzzle; @zhuang2025treesearch; @espejo2026agentic]. Cross-
paper numbers swing wildly with harness (e.g. GPT-4o from 1.4% to 57.8% on MolPuzzle under
different prompting [@guo2024molpuzzle; @zhuang2025treesearch]). What remains under-
measured is the chemist's operational setting: **take peak lists as printed in open-
access papers and recover constitution**, with a fixed molecular-representation scoring
contract and an honest account of **which stage of elucidation binds**.

We argue that end-to-end top-1 alone is the wrong reporting primitive. Any system that
returns a ranked candidate list factorises as

\[
\text{top-1} \;=\; \underbrace{P(\text{true} \in \text{pool})}_{\text{generation recall}}
\times
\underbrace{P(\text{rank}=1 \mid \text{true} \in \text{pool})}_{\text{verification precision}}.
\]

These rates have different denominators and must not be differenced. Prior work already
notes that re-ranking cannot recover a missing candidate [@priessner2026reasoning]; we
supply the missing **measurement infrastructure at scale**.

**Contributions.**

1. **IRSpectra-Bench** — a blind, complexity-stratified peak-list benchmark (n=194) with a
   pre-registered InChIKey-connectivity scorer and community reporting contract (top-1,
   generation recall, verification precision | recall).
2. **A recall-bound diagnosis** on a frontier LLM: 34% proposed; 89% selected once proposed;
   top-1 moves only 28% → 30% under training-free forward-verification.
3. **Contamination and cross-vendor controls** — formula-only and recency bounds;
   four-vendor replication of recall ≪ precision.
4. **A literature decomposition** that recovers the same split from published top-*k*
   figures, showing recall carries most of the collapse on real heterogeneous data.

**Dataset pointer (not this paper's primary object).** Experimental band lists come from
**IRexp** (121,233 records; 43,060 structure-linked; 33,201 full IR+¹H+¹³C+structure
quadruples), released on Hugging Face (`ilkhamfy/IRexp`). Construction, licensing, and
technical validation of the corpus are the subject of a companion *Scientific Data*
manuscript (in preparation). This ICLR paper **cites** that resource and does not re-present
a Data Descriptor.

![Diagnosis on IRSpectra-Bench (n=194): generation recall, not verification, is the bottleneck. Where the true structure is never proposed, no ranker can recover it; where it is proposed, verification usually selects it.](docs/figures/fig_wall.png){#fig:fig-wall}

---

## 2. Related work {#sec:related-work}

**Trained spectra → structure models.** Sequence and graph decoders on paired corpora
[@chacko2024spectro; @hu2024multitask; @yang2026nmrtrans; @ottomano2025nmiracle;
@alberts2024ir; @alberts2025benchmarks] are accurate in-distribution but typically scored
end-to-end. We do not claim to beat them on IRSpectra-Bench; Spectro, NMIRacle, Alberts IR
transformers and CASE are **not yet scored** on our bench ([@sec:limitations]) — a gap we
state honestly and leave to the released scorer.

**LLM agents and puzzle benches.** ChemCrow [@mbran2024chemcrow], Coscientist
[@boiko2023coscientist], SpectralLM [@su2025spectrallm], SpecMol [@shen2025specmol],
tree-search elucidation [@zhuang2025treesearch], IR-Agent [@noh2025iragent] and Priessner *et
al.* [@priessner2026reasoning] improve *how* a model reads spectra or re-ranks a fixed pool.
We fix one protocol and ask **which stage binds** once the spectra have been read.

**Contamination-aware and heterogeneous-data benches.** Most prior suites use simulated or
single-instrument spectra. IRSpectra-Bench uses literature-reported peak lists across
thousands of laboratories and reports formula-only and recency controls
([@sec:contamination]). Espejo Morales *et al.* [@espejo2026agentic] compare education vs
industrial *instrument files* (80.9% → 20.6%); they ask which architecture, we ask which
stage binds on **published reports**.

**Forward verification and CASE.** Matching predicted to observed shifts — DP4
[@smith2010dp4], CASE [@elyashberg2012case], NMR-Solver [@jin2025nmrsolver], NMRAgent
[@fang2026nmragent] — is easier than inverse generation. CASE enumerators have exhaustive
recall by construction; the LLM literature almost never reports whether the true structure
was proposed at all. We decompose error rather than chase a single top-1.

**Positioning.** Concurrent 2026 suites (MolQuest [@han2026molquest], SpecX
[@xiang2026specx], NMRGym [@fang2026nmrgym]) bound related tasks. Ours is an openly
redistributable suite on literature peak lists with a **stage decomposition** measured on
Claude and replicated across three other model families.

---

## 3. IRSpectra-Bench {#sec:benchmark}

### 3.1 Task and inputs

Each of 194 problems supplies the **molecular formula** (as from HRMS), the **IR band
list** (cm⁻¹), and **¹H / ¹³C shift lists** — exactly the textual form reported in open-
access papers. No name, SMILES or scaffold hint. Inputs are author-transcribed **band and
shift lists**, not absorbance traces or FIDs: a different object from digitised-spectrum
benchmarks [@espejo2026agentic], and one that matches how language models consume
literature.

Problems are drawn from the structure-complete split of IRexp (`irexp_resolved`; see
companion Data Descriptor / HF card). In 10/194, author peak assignments name a ring system;
those are solved 1/10 vs 54/184 for the rest, so annotation does not carry the headline.

### 3.2 Difficulty, balance, and scoring contract

**Difficulty** is declared *a priori* by RDKit ring analysis: *simple* iff ≤2 rings, no
fused/spiro/bridgehead system, ≤22 heavy atoms; else *complex* (98/96). The released
benchmark is **50/50 by design**; the eligible corpus is 17.5% simple / 82.5% complex.
Reweighted to corpus composition, top-1 falls 28.4% → **15.2%** and recall 33.5% →
**19.8%**. We report both; the reweighted figure is the better estimate for an arbitrary
paper, the 50/50 figure the comparable leaderboard number.

**Scoring.** A prediction is correct if RDKit InChIKey **connectivity** (first 14
characters) matches — we score *constitution*. Full stereo-sensitive InChIKey gives 21.1%
top-1 vs 28.4% constitution. External submissions: up to three ranked SMILES per `qid`, no
structure hints (`docs/LEADERBOARD.md`; `scripts/score_submission.py`).

**Primary metrics (report all three).**

| metric | definition |
|---|---|
| **Top-1** | best-ranked candidate matches at connectivity layer |
| **Generation recall** | reference in the candidate pool *before* re-ranking |
| **Verification precision \| recall** | correct top-1 among recall-positive compounds |

CIs are bootstrap 95%; paired model differences use McNemar with Holm correction.

![Top-1 and recovered accuracy by difficulty (n=194), with bootstrap 95% CIs.](docs/figures/fig1_difficulty.png){#fig:fig1-difficulty}

---

## 4. Experimental setup {#sec:setup}

**Solver.** Frontier LLM agent (Claude Opus via consumer subscription), closed-book, one
sub-agent per batch, up to three ranked candidates, RDKit formula check only. No fine-
tuning, no paid API for the core protocol. Inference is **not** exactly reproducible (no
pinned snapshot, temperature or seed — [@sec:limitations]); **scoring is**: frozen
predictions, ground truth and scorers regenerate every training-free number.

**Forward-verification loop** ([@sec:forward-verify]). Generate candidates → forward-predict
each candidate's ¹³C (blind to observed spectrum) → re-rank by symmetric chamfer distance
between predicted and observed ¹³C peak sets.

**Controls and probes.** Formula-only / recency ([@sec:contamination]); four-vendor
replication on a 60-compound arm ([@sec:cross-vendor]); generate-wide sampling; HOSE lookup
and GNN ¹³C verifiers; small IRexp-fine-tuned generator probe (fenced from headline
claims).

---

## 5. Results {#sec:results}

### 5.1 Headline performance {#sec:headline}

**Table {#tab:headline}. Headline elucidation on IRSpectra-Bench (n=194).**

| metric | overall (n=194) | simple (n=98) | complex (n=96) |
|---|--:|--:|--:|
| top-1 exact constitution | **28.4%** [22–35] | 48.0% [39–57] | 8.3% [3–15] |
| recovered (top-3) | 33.5% [27–40] | 54.1% [44–63] | 12.5% [6–20] |
| scaffold-level (best Tanimoto ≥ 0.45) | 56% | 73% | 39% |
| mean best Tanimoto | 0.59 | 0.73 | 0.45 |

Accuracy falls with size: 60.5% top-1 at ≤15 heavy atoms, 28.3% at 16–25, 7.0% above 25.
Of 137 analysable top-1 misses, **76.6%** are constitutional isomers of the true structure;
only **22.6%** share the true Murcko scaffold — wrong connectivity at the right composition,
not mostly fine regiochemistry.

A 24-compound four-model Claude comparison is capability-sensitive (strict nesting Haiku ⊂
Sonnet ⊂ Opus ⊂ Fable) but underpowered for adjacent ranks and carries a disclosed protocol
asymmetry ([@sec:limitations]). A battery-electrolyte subset (n=46) matches the headline
regime (26% top-1; recall-bound).

### 5.2 Is the model reading the spectra? {#sec:contamination}

**Table {#tab:formula-only}. Formula-only control (paired, n=60).**

| condition | top-1 | recovered (top-3) |
|---|--:|--:|
| formula only | **3/60 (5%)** | 3/60 (5%) |
| formula + IR + ¹H + ¹³C | 14/60 (23%) | 19/60 (32%) |

Outcomes are perfectly nested (McNemar p=0.001). Accuracy is flat in source-paper year
across all 194 (r=−0.007), bounding pretraining recall of specific papers. We claim a
**strong bound, not exclusion** of contamination ([@sec:limitations]).

![Robustness of the recall-bound diagnosis: formula-only vs full modality; accuracy vs year; cross-vendor recall and precision.](docs/figures/fig_robustness.png){#fig:fig-robustness}

### 5.3 Cross-vendor replication {#sec:cross-vendor}

Grok 4.6, Gemini 3.7 Flash and GPT-5.6 Sol solved the same 60-compound arm under the
identical protocol. **Verification precision exceeds generation recall in every arm**;
bootstrapping separates the paired gap for Claude (+52.5 points), GPT-5.6 Sol (+26.3) and
Gemini (+23.3); Grok's gap (+9.2) is directional.

**Table {#tab:cross-vendor}. Cross-vendor decomposition (n=60).** Recall and precision have
different denominators — the claim is the inequality, not a difference.

| model | generation recall | verification precision \| recall | multi-candidate only |
|---|--:|--:|--:|
| Claude Opus | 19/60 = 32% | 16/19 = 84% | 10/13 = 77% |
| Grok 4.6 | 32/60 = 53% | 20/32 = 62% | 20/32 = 62% |
| Gemini 3.7 Flash | 30/60 = 50% | 22/30 = 73% | 22/30 = 73% |
| GPT-5.6 Sol | 25/60 = 42% | 17/25 = 68% | 16/24 = 67% |

Candidate budgets differ (Claude mean 2.20 vs others 3.00), so recall rankings are
approximate. A clean-clone control for Grok bounds key leakage (McNemar p=0.39).

### 5.4 Forward-verification decomposition {#sec:forward-verify}

![Forward-verification on a regioisomer pair: inverse task is ambiguous; forward-predicted ¹³C separates isomers.](docs/figures/fig_mechanism.png){#fig:fig-mechanism}

**Table {#tab:fverify}. Forward-verification decomposition.**

| | 60-compound arm | full benchmark (n=194) |
|---|--:|--:|
| generation recall | 19/60 (32%) | 65/194 (34%) |
| top-1, solver self-ranking | 14/60 (23%) | 55/194 (28%) |
| top-1, forward-verified re-ranking | 16/60 (27%) | 58/194 (30%) |
| precision \| recall — forward-verification | 16/19 (84%) | 58/65 (**89%**) |
| multi-candidate only — forward-verification | 10/13 (77%) | 30/37 (81%) |

When the true structure is among the candidates, forward-verification selects it in 58/65
cases (89%). Where a choice existed (n=37), it gets 30/37 (81%) against a 54.0% derangement
floor (+27.1 points). The margin over self-ranking is **small and unresolved** (seven
gained, four lost; McNemar p=0.55) — we do **not** claim an accuracy advance. Precision is
high while recall binds: no re-ranking repairs the 129/194 compounds where the true
structure was never proposed ([@fig:fig-wall]).

**Generate-wide.** Ten solver agents, up to six candidates each, pooled and re-ranked on
the 60-compound arm: recall 32% → **42%**, top-1 23% → **30%** (McNemar p=0.34);
verification precision falls 84% → 72%. The training-free ceiling remains recall-limited.

![Forward-verification inference ladder on the 60-compound arm.](docs/figures/fig3_method.png){#fig:fig3-method}

**Non-LLM verifiers.** On the same candidate sets, a HOSE-style lookup ties self-ranking; a
modest GNN reaches 59/65 (91%) vs the LLM verifier's 58/65 (89%) — directional. Deranging
observed ¹³C pairings collapses precision (p=0.001). A small IRexp-fine-tuned generator
pooled with Claude lifts recall 33.5% → 54.1% and top-1 28.4% → 35.1% (McNemar p=0.015),
showing the wall is a property of **training-free elicitation**, not of the task.

### 5.5 Decomposition across published literature {#sec:literature}

Any system reporting top-1 = *a* and top-*k* = *b* implies recall ≥ *b* and conditional
precision ≤ *a*/*b*. Applying this to published figures
(`scripts/literature_decomposition.py`):

**Table {#tab:lit-decomp}.** Selected rows (connectivity-scored or as published). Full table
in the repository / ESI of the combined archive.

| system | data (n) | top-1 | top-*k* (k) | recall | prec. |
|---|---|--:|--:|--:|--:|
| this work, solver alone | literature (194) | 28.4% | 33.5% (3) | 33.5% | 84.6% |
| this work + forward-verify | literature (194) | 29.9% | 33.5% (3) | 33.5% | **89.2%** |
| NMR-Solver [@jin2025nmrsolver] | literature (450) | 52.9% | 67.3% (10) | ≥ 67.3% | ≤ 78.6% |
| NMRAgent [@fang2026nmragent] | literature (450) | 61.6% | 70.0% (10) | ≥ 70.0% | ≤ 88.0% |
| Espejo Morales [@espejo2026agentic] | education (236) | 80.9% | 90.0% (5) | ≥ 90.0% | ≤ 89.9% |
| Espejo Morales [@espejo2026agentic] | industrial (34) | 20.6% | 29.1% (5) | ≥ 29.1% | ≤ 70.9% |
| Alberts, 6–13 atoms [@alberts2025benchmarks] | NIST IR (3,455) | 63.8% | 84.0% (10) | 84.0% | 75.9% |
| SpecX, scaffold split [@xiang2026specx] | simulated (99,439) | 29.7% | 50.6% (10) | 50.6% | 58.7% |

**Three groups changed only the data**, and recall carried **68%** (NMR-Solver simulated →
real), **70%** (SpecX random → scaffold) and **83%** (Espejo education → industrial) of each
collapse. Recall binds where spectra are real and heterogeneous; ranking dominates on
simulated or single-library data. The field almost never reports whether the true structure
was proposed at all.

---

## 6. Discussion {#sec:discussion}

Frontier LLMs are **good verifiers** (≈89% conditional precision) and **weak proposers**
(≈34% recall) on real literature peak lists. The primary research contribution of this paper
is the **benchmark + stage decomposition + contamination/cross-vendor diagnosis**, not a
solved elucidator and not a Data Descriptor for IRexp.

**Reporting contract.** External work on IRSpectra-Bench should deposit ranked SMILES under
the released protocol and report, at minimum: (i) top-1 constitution, (ii) generation
recall, (iii) verification precision | recall, with bootstrap CIs and candidate budget.
Top-1 alone conflates the two stages. Nonsignificant ladder gains (forward-verification vs
self-ranking, p=0.55; generate-wide top-1, p=0.34) should be cited as **diagnostic**, not as
accuracy advances. Corpus-reweighted top-1 (**15.2%**) is the better estimate for an
arbitrary literature draw.

Training is not foreclosed: IRexp fine-tuning lifts recall to 54%. What compounds is open
experimental data, honest benchmarks, and inference scaffolding that rides each new model.

---

## 7. Limitations {#sec:limitations}

Scoring is mechanical; solver runs were transcript-audited for zero ground-truth access.
**(i) Consumer harness.** No model snapshot, temperature, seed or thinking tier; exact
inference is not reproducible. Scoring is. Instruction text wrapping Claude batches was not
captured — only per-compound payloads are released.
**(ii) Pretraining contamination** is bounded by formula-only (23% → 5%) and flat recency
but **not excluded**; verbatim spectral strings from PMC in the prompt remain a retrieval
confound.
**(iii) Object type, formula and scoring.** Band/shift lists, not raw traces; formula
supplied (as from HRMS) — absolute accuracies are not interchangeable with no-formula
systems. Headline metrics score constitution; with stereochemistry, top-1 is 21.1%.
**(iv) Statistical honesty.** Forward-verification vs self-ranking unresolved (p=0.55);
generate-wide top-1 likewise (p=0.34). Four-model comparison at n=24 underpowered for
adjacent ranks with disclosed protocol asymmetry. The inference ladder **diagnoses a
bottleneck**; it is not a demonstrated accuracy advance.
**(v) Missing on-bench cheminformatics baselines.** Spectro, NMIRacle, Alberts IR
transformers and CASE were **not scored** on IRSpectra-Bench — the LLM recall wall is not
cleanly separated from harness or modality choice.
**(vi) Cross-vendor scope.** Headline n=194 is Claude Opus; four-vendor replication is on
60 compounds; candidate budgets differ.
**(vii) Deferred arms.** Expert-chemist audit of elucidation outputs formally deferred
(not run). Leave-one-modality-out ablation abandoned for this manuscript. Extraction-recall
human audit of the mining parser is deferred to the *Scientific Data* companion.
**(viii) Scope.** Battery subset uses literature electrolyte chemistry, not operando
spectra; single-sample scoring per compound; organic literature bias of PMC-OA sources.

---

## 8. Conclusion {#sec:conclusion}

IRSpectra-Bench makes LLM structure elucidation from literature peak lists **measurable and
decomposable**. On that protocol, generation recall — not verification — binds end-to-end
accuracy; the diagnosis replicates across vendors and recovers from published top-*k*
figures. We release frozen predictions and a mechanical scorer so others can report the same
three numbers. The redistributable experimental band-list corpus behind the bench is
documented separately as a *Scientific Data* Data Descriptor (in prep.) and mirrored at
`ilkhamfy/IRexp`.

---

## Reproducibility statement

Every training-free number regenerates from released questions, answers, frozen predictions
and scripts in the project repository. The sampler, InChIKey scorer and forward-verification
harness are scripted end-to-end. Consumer-harness inference cannot be bit-exact replayed
([@sec:limitations]); distributional agreement is the intended claim. Fine-tuning against
the bench should use `data/train_no_bench.jsonl.gz` so benchmark InChIKeys are withheld.

---

## Ethics statement

This work evaluates publicly available open-access literature peak lists and commercial LLM
APIs under consumer terms. No human-subject data. We do not claim clinical or regulatory
readiness for automated elucidation. Licensing of redistributed numeric extractions is
documented in the companion Data Descriptor and dataset notices (PMC-OA terms are mixed —
not uniformly CC-BY; Chemotion is CC-BY-SA).

---

## References

Citations use the shared bibliography `docs/references.bib` (pandoc `--citeproc`). For this
markdown draft, keys match the combined archive; a camera-ready ICLR TeX build will switch
to the conference style file.

::: {#refs}
:::

---

## Appendix A — Dataset pointer (IRexp)

IRexp is **not** re-described here as a Data Descriptor. For counts, provenance, licensing
caveats, transcription audit (560/560 bands on n=60), and file schema, see:

- Hugging Face: https://huggingface.co/datasets/ilkhamfy/IRexp
- Companion manuscript: *Scientific Data* Data Descriptor (in preparation)
- Combined archive (pre-split JCIM-shaped paper): `docs/archive/combined_PAPER.md`
- Feasibility audit: `docs/irexp_scientific_data_audit.md`

Benchmark construction details beyond §3 (spectral validation filters, prompt-leakage
audit, electrolyte SMARTS) live in `docs/BENCHMARK.md` and the Electronic Supplementary
Information of the combined archive.

## Appendix B — Extended tables and figures

Supplementary figures currently shared with the combined manuscript under `docs/figures/`:
`fig0_overview`, `fig2_size`, `fig4_dataset`, `fig5_models`, `fig6_electrolyte`,
`fig7_crossvendor`, `fig_contamination`, `fig_generator_probe`, `fig_verifier`. Full
artefact inventory: repository README / `docs/archive/combined_PAPER.md` Data availability.
