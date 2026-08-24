# Cover letter — *Digital Discovery* (RSC)

**Re: Submission of "Candidate recall, not verification, limits LLM structure
elucidation from real experimental IR and NMR"**

Dear Editor,

We submit the enclosed manuscript for consideration as an Article in *Digital
Discovery*. It asks a question of immediate interest to this readership — *how well do
frontier large language models actually recover molecular structure from real
experimental spectra?* — and answers it with open data, a blind benchmark and a
training-free method rather than with a curated demonstration.

Given the molecular formula, the IR band list and the ¹H/¹³C shifts exactly as reported
in an open-access paper, a frontier model recovers the correct constitution for 28.4% of
194 compounds (95% CI 22–35), or 15.2% once reweighted to the corpus from which the
benchmark was drawn — far below the near-100% implied by prior curated
evaluations. We reconcile that gap quantitatively — difficulty, scoring, hints, curation
— and show with a within-compound control that reported numbers are sensitive to how the
problem is posed, not to raw capability alone.

The central result is a decomposition: **candidate recall (65/194, 34%), not
verification (58/65, 89% conditional on recall), is what bounds performance**, measured
over every compound in the benchmark rather than a subset. Acting on that diagnosis by
generating wider moves top-1 from 23% to 30% on the arm where it was run — a real but
bounded gain, reported as directional rather than statistically resolved. The split is
not confined to one lineage: Grok 4.6, Gemini 3.7 Flash and GPT-5.6 Sol all verify
better than they generate on the same 60 compounds.

Concurrent work sharpens the same diagnosis without overlapping our claims. Espejo
Morales *et al.* (arXiv:2607.19406) frame NMR elucidation as agentic search without a
learned simulator and reach 71.1% top-1 versus 66.7% for graduate students on 15
molecules, yet 20.6% on 34 industrial samples — independent support that proposal supply
binds and that curated versus real spectra collapse. We claim the decomposition at scale
across four model families and verifiers, not their architectural frame. Complementary
industry evidence comes from Wagen (Rowan Scientific), who looped a frontier LLM with
MagNET, an external ¹³C predictor, on eight corrected misassignments: connectivity moves
46.4% to 55.4%, while exact-SMILES scoring including stereochemistry moves 21.4% to
51.8% — consistent with a sharper verifier helping most where stereochemistry is scored,
without over-reading a preliminary n=8 study.

We claim the decomposition, not the loop. NMR-Solver (Jin *et al.*, 2025) implements the
same generate-and-verify loop without an LLM and reports higher accuracy with a sharper
shift predictor; we cite it as the clearest external support for our mechanistic claim,
since we measure predictor resolution as the binding constraint and they convert a
twice-sharper predictor into roughly twice the top-1.

Alongside the analysis we release **IRexp**, to our knowledge the largest permissively
licensed, redistributable collection of *experimental* infrared band lists by record
count (121,233 records; 43,060 structure-linked; 33,201 full IR + ¹H + ¹³C + structure
quadruples), and **IRSpectra-Bench**, the blind, mechanically scored, complexity-
stratified benchmark built from it. Larger view-only databases exist, but open,
structure-linked, ML-ready experimental IR has been a standing gap. The diagnosis and
open corpus may also interest practitioners beyond digital chemistry who assign
structures from literature spectra daily.

The core protocol uses no model training and no paid API. Two probes are clearly fenced
as complements rather than as part of it: a small generator fine-tuned on IRexp,
which establishes that the recall wall is elicitation-specific rather than
task-intrinsic, and a learned ¹³C verifier. All data, predictions, figures and code are
released, both probes included with their reproducers; solver transcripts are available
on request.

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
