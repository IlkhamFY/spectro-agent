# Cover letter — *Digital Discovery* (RSC)

**Re: Submission of "Recall, not verification, is the bottleneck when frontier LLMs
elucidate molecular structures from real spectra"**

Dear Editor,

We submit the enclosed manuscript for consideration as an Article in *Digital
Discovery*. It asks a question of immediate interest to this readership — *how well do
frontier large language models actually recover molecular structure from real
experimental spectra?* — and answers it with open data, a blind benchmark and a
training-free method rather than with a curated demonstration.

Given the molecular formula, the IR band list and the ¹H/¹³C shifts exactly as reported
in an open-access paper, a frontier model recovers the correct constitution for 28.4% of
194 compounds (95% CI 22–35), far below the near-100% implied by prior curated
evaluations. We reconcile that gap quantitatively — difficulty, scoring, hints, curation
— and show with a within-compound control that reported numbers are sensitive to how the
problem is posed, not to raw capability alone.

The paper's central result is a decomposition: **candidate recall (65/194, 34%), not
verification (58/65, 89% conditional on recall), is what bounds performance**, measured
over every compound in the benchmark rather than a subset. Acting on that diagnosis by
generating wider moves top-1 from 23% to 30% on the arm where it was run — a real but
bounded gain, which we report as directional rather than statistically resolved. The
decomposition is not confined to one lineage: Grok 4.6, Gemini 3.7 Flash and GPT-5.6 Sol
all verify better than they generate on the same 60 compounds (§4.7).

Alongside the analysis we release **IRexp**, to our knowledge the largest permissively
licensed, redistributable collection of *experimental* infrared band lists by record
count (121,233 records; 43,060 structure-linked; 33,201 full IR + ¹H + ¹³C + structure
quadruples), and **IRSpectra-Bench**, the blind, mechanically scored, complexity-
stratified benchmark built from it. Larger view-only databases exist, but open,
structure-linked, ML-ready experimental IR has been a standing gap.

We claim the decomposition, not the loop. NMR-Solver (Jin *et al.*, 2025) implements the
same generate-and-verify loop without an LLM and reports higher accuracy with a sharper
shift predictor; we cite it as the clearest external support for our mechanistic claim,
since we measure predictor resolution as the binding constraint and they convert a
twice-sharper predictor into roughly twice the top-1.

The core protocol uses no model training and no paid API. Two probes are clearly fenced
as complements rather than as part of it: a small generator fine-tuned on IRexp (§5.6),
which establishes that the recall wall is elicitation-specific rather than
task-intrinsic, and a learned ¹³C verifier (§5.4). All data, agent transcripts,
predictions, figures and code are released, both probes included with their reproducers.

The work is original, not under consideration elsewhere, and all authors approve the
submission. We have no competing interests to declare, and would be glad to suggest
referees with expertise in spectral machine learning, NMR/IR structure elucidation and
LLM evaluation.

Thank you for your consideration.

Sincerely,
Ilkham Yabbarov (corresponding author), Rudra Sondhi, and Rodrigo A. Vargas-Hernández
Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario, Canada
yabbaroi@mcmaster.ca

---

## Significance statement (for the field)

Claims that large language models can "read" spectra and name molecules have outpaced
the evidence, which rests on small, curated, hinted, NMR-only tests. This work supplies
what was missing: the largest permissively licensed, redistributable collection of
experimental-IR band lists by record count (121,233 records, 43,060 structure-linked), a
blind and mechanically scored benchmark on real literature spectra, and an honest
accounting of the gap between optimistic demonstrations and realistic performance. Its
central finding — that the binding constraint is *candidate recall* (65/194), not
verification (58/65 conditional on recall), and that a training-free forward-verification
step exploits this for a real but bounded gain — redirects effort from bespoke
architectures toward open data, open benchmarks, and inference-time methods that improve
with each model generation. A battery-electrolyte case study shows the diagnosis
transfers to a domain where structure-from-spectrum assignment is daily practice.
