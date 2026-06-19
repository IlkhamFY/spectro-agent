# Cover letter — *Digital Discovery* (RSC)

**Re: Submission of "An open multimodal benchmark for LLM molecular structure
elucidation reveals a recall-bound bottleneck that forward verification exploits"**

Dear Editor,

We submit the enclosed manuscript for consideration as an Article in *Digital
Discovery*. It addresses a question of immediate interest to the cheminformatics and
AI-for-chemistry community — *how well do frontier large language models actually
recover molecular structure from real experimental spectra?* — and answers it with
open data, a blind benchmark, and a training-free method, rather than with a curated
demonstration.

**What is new.**

1. **IRexp** — to our knowledge the largest *permissively-licensed, redistributable*
   dataset of *experimental* infrared spectra (121,233 records; 42,842 structure-linked;
   40,491 full IR + ¹H + ¹³C + structure quadruples), mined from open-access literature
   by a browser-free agent and released under permissive licences. Larger view-only
   databases exist (AIST SDBS, ~54k FT-IR) but are not bulk-downloadable or
   redistributable; *open, structure-linked, ML-ready* experimental IR has been a
   standing gap. IRexp is directly reusable for training the multimodal models that
   motivate this area (e.g. NMIRacle).

2. **IRSpectra-Bench** — an open, blind, mechanically scored, complexity-stratified
   benchmark of 194 spectrally-validated compounds. Under it, a frontier LLM recovers
   the exact constitution of 28.4% of real compounds (95% CI 22–35), far below the
   near-perfect recovery implied by prior curated evaluations — a gap we *reconcile*
   quantitatively (difficulty, candidate ranking, hints) and trace to a single cause
   with a within-compound control: solving each compound in an independent context
   roughly triples accuracy, so methodology, not raw capability, dominates published
   numbers.

3. **Forward-verification elucidation** — a training-free generator–verifier method
   that re-ranks candidate structures by forward-predicting each one's ¹³C spectrum
   and matching it to experiment. Its decomposition is the paper's central result:
   **candidate recall (31%), not verification (84% conditional), bounds performance.**
   We frame this explicitly as the LLM analog of computational-NMR / NMR-crystallography
   structure validation (DP4/GIPAW), the inverse-problem workflow already trusted in
   the magnetic-resonance community.

4. **A battery-electrolyte domain case study** showing the bottleneck reproduces
   inside a single application area (26% top-1 across carbonate, sulfonyl, nitrile,
   fluorinated, phosphoryl, and glyme functional classes) with a chemically
   interpretable gradient — evidence the bottleneck is structural, and a concrete
   bridge to electrolyte/interphase spectral assignment.

**Fit and reproducibility.** Every experiment runs with no model training and no paid
API — only LLM agents under a standard subscription — and all data, agent
transcripts, predictions, figures, and scoring/mining code are released. This matches
*Digital Discovery*'s emphasis on open, reproducible computational methodology, and we
believe the combination of an open dataset, an honestly-scored benchmark that
reconciles an optimistic but non-peer-reviewed industrial report against the
peer-reviewed benchmark record, and a training-free method with a clear,
actionable diagnosis will be of broad interest to your readership.

The work is original, not under consideration elsewhere, and all authors approve the
submission. We have no competing interests to declare. We would be glad to suggest
referees with expertise in spectral machine learning, NMR/IR structure elucidation,
and LLM evaluation upon request.

Thank you for your consideration.

Sincerely,
Ilkham Yabbarov (corresponding author) and Rodrigo A. Vargas-Hernández
Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario, Canada
ilkhamfy@gmail.com

---

## Significance statement (for the field)

Claims that large language models can "read" spectra and name molecules have outpaced
the evidence, which rests on small, curated, hinted, NMR-only tests. This work
supplies what was missing: the largest permissively-licensed, redistributable
experimental-IR dataset, a blind and
mechanically scored benchmark on real literature spectra, and an honest accounting
that explains the gap between optimistic demonstrations and realistic performance. Its
central finding — that the binding constraint is *candidate recall*, not verification,
and that a training-free forward-verification step (the LLM analog of
NMR-crystallography) measurably exploits this — redirects effort from training
ever-larger bespoke models toward open benchmarks and inference-time methods that
improve with each model generation. A battery-electrolyte case study shows the
diagnosis transfers to a domain where structure-from-spectrum assignment is daily
practice.
