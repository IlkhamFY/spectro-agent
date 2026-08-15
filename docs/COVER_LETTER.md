# Cover letter — *Digital Discovery* (RSC)

**Re: Submission of "Recall, not verification, is the bottleneck when frontier LLMs
elucidate molecular structures from real spectra"**

Dear Editor,

We submit the enclosed manuscript for consideration as an Article in *Digital
Discovery*. It addresses a question of immediate interest to the cheminformatics and
AI-for-chemistry community — *how well do frontier large language models actually
recover molecular structure from real experimental spectra?* — and answers it with
open data, a blind benchmark, and a training-free method, rather than with a curated
demonstration.

**What is new.**

1. **IRexp** — to our knowledge the largest *permissively-licensed, redistributable*
   collection of *experimental* infrared **band lists** by record count (121,233 records; 43,060
   structure-linked; 33,201 full IR + ¹H + ¹³C + structure quadruples), mined from
   open-access literature by a browser-free agent and released under permissive
   licences. Larger view-only databases exist (AIST SDBS, ~54k FT-IR, all
   structure-linked) but are not bulk-downloadable or redistributable; *open,
   structure-linked, ML-ready* experimental IR has been a standing gap. IRexp is
   directly reusable for training the multimodal models that motivate this area
   (e.g. NMIRacle).

2. **IRSpectra-Bench** — an open, blind, mechanically scored, complexity-stratified
   benchmark of 194 compounds (134 spectrally-validated main-round compounds plus 60
   pre-registered controlled-round compounds). Under it, a frontier LLM (Claude Opus)
   recovers the exact constitution of 28.4% of real compounds (n=194; 95% CI 22–35),
   far below the near-100% implied by prior curated evaluations — a gap we *reconcile*
   quantitatively (difficulty, scoring, hints, curation) and probe with a
   within-compound control: on the identical 20 molecules, solving in bounded,
   frequently-reset contexts with tool access roughly triples recovery, 5%→15%
   (1/20→3/20, directional at n=20), so reported numbers are sensitive to methodology,
   not to raw capability alone.

3. **A recall/verification decomposition**, obtained with a training-free
   generator–verifier probe that re-ranks candidate structures by forward-predicting
   each one's ¹³C spectrum and matching it to experiment. We claim the decomposition,
   not the loop: NMR-Solver (Jin *et al.*, 2025) implements the same loop without an
   LLM and reports higher accuracy with a sharper shift predictor, and we cite it as
   such — its result is in fact the clearest external support for our mechanistic
   claim, since we measure the ~2 ppm resolution of the LLM predictor as the binding
   constraint and they convert a twice-sharper predictor into roughly twice the top-1.
   The decomposition is the paper's central result:
   **candidate recall (65/194, 34%), not verification (58/65, 89% conditional on
   recall), bounds performance** — measured over every compound in the benchmark, not a
   subset. Acting on that diagnosis with wide generation moves
   top-1 from 23% to 30% (14/60→18/60) on the arm where it was run — a real but bounded
   gain, which we report as directional rather than resolved. We frame the method explicitly as the LLM
   analog of computational-NMR / NMR-crystallography structure validation (DP4/GIPAW),
   the inverse-problem workflow already trusted in the magnetic-resonance community —
   an analogy, not an equivalence: we trade DFT's calibrated error model for zero setup
   cost.

4. **A battery-electrolyte domain case study** showing the bottleneck reproduces
   inside a single application area (26% top-1, n=46, across carbonate, sulfonyl,
   nitrile, fluorinated, phosphoryl, and glyme functional classes) with a chemically
   legible per-class pattern — consistent with a structural bottleneck, and a concrete
   bridge to electrolyte/interphase spectral assignment.

**Fit and reproducibility.** The core protocol runs with no model training and no paid
API — only LLM agents under a standard subscription. Two clearly fenced probes are the
stated exceptions, reported as labelled complements rather than as part of that
protocol: a small generator fine-tuned on IRexp (§5.6), which establishes that the
recall wall is elicitation-specific rather than task-intrinsic and delivers our highest
full-benchmark accuracy (top-1 28.4%→35.1%, n=194, McNemar exact p=0.015), and a
learned ¹³C verifier (§5.4). Every result is single-vendor (the Claude family), which
we state plainly and name as the key open question. All data, agent transcripts,
predictions, figures, and scoring/mining code are released, both probes included with
their reproducers. This matches *Digital Discovery*'s emphasis on open, reproducible computational methodology, and we
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
Ilkham Yabbarov (corresponding author), Rudra Sondhi, and Rodrigo A. Vargas-Hernández
Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario, Canada
ilkhamfy@gmail.com

---

## Significance statement (for the field)

Claims that large language models can "read" spectra and name molecules have outpaced
the evidence, which rests on small, curated, hinted, NMR-only tests. This work
supplies what was missing: the largest permissively-licensed, redistributable
collection of experimental-IR band lists by record count (121,233 records, 43,060
structure-linked), a
blind and mechanically scored benchmark on real literature spectra, and an honest
accounting that explains the gap between optimistic demonstrations and realistic
performance. Its central finding — that the binding constraint is *candidate recall*
(65/194), not verification (58/65 conditional on recall), and that a training-free
forward-verification step (the LLM analog of NMR-crystallography) exploits this for a
real but bounded gain — redirects effort from bespoke architectures toward open data,
open benchmarks, and inference-time methods that improve with each model generation.
A battery-electrolyte case study shows the diagnosis transfers to a domain where
structure-from-spectrum assignment is daily practice.
