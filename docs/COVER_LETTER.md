# Cover letter — draft (ChemRxiv deposit, then *J. Chem. Inf. Model.*)

**Re: "IRexp and IRSpectra-Bench: redistributable experimental IR band lists, a blind
peak-list benchmark, and a recall-bound diagnosis of LLM elucidation"**

Dear Editor,

We enclose a manuscript for consideration as a *Journal of Chemical Information and
Modeling* chemical-information resource paper (ChemRxiv deposit first). We release
**IRexp**, the largest permissively licensed, redistributable collection of experimental
infrared band lists (121,233 records; 43,060 structure-linked; 33,201 full IR + ¹H + ¹³C +
structure quadruples), and **IRSpectra-Bench**, a blind, mechanically scored peak-list
benchmark of 194 compounds built from it — with a fixed RDKit InChIKey-connectivity scoring
contract and decomposable generation-recall / verification-precision metrics the community
can report — then ask how well frontier large language models recover constitution from the
peak lists exactly as reported in open-access papers.

Given the molecular formula, the IR band list and the ¹H/¹³C shifts exactly as reported
in an open-access paper, a frontier model recovers the correct constitution for 28.4% of
194 compounds (95% CI 22–35), or 15.2% once reweighted to the corpus from which the
benchmark was drawn — far below the near-100% implied by prior curated
evaluations. We reconcile that gap quantitatively — difficulty, scoring, hints, curation
— and show with a within-compound control that reported numbers are sensitive to how the
problem is posed, not to raw capability alone.

The diagnostic result is a decomposition: **candidate recall (65/194, 34%), not
verification (58/65, 89% conditional on recall), is what bounds performance**, measured
over every compound in the benchmark rather than a subset. Acting on that diagnosis by
generating wider moves top-1 from 23% to 30% on the arm where it was run — a real but
bounded gain, reported as directional rather than statistically resolved. The split is
not confined to one lineage: Grok 4.6, Gemini 3.7 Flash and GPT-5.6 Sol all verify
better than they generate on the same 60 compounds.

We position the work as cheminformatics infrastructure relative to trained spectra→structure
models (Spectro, NMIRacle, Alberts), LLM agents and puzzle benches (MolPuzzle, IR-Agent,
Priessner *et al.*), and generate-and-verify systems (NMR-Solver): what is new is the
*redistributable experimental IR band-list corpus*, the *blind literature peak-list
protocol*, and the *stage-decomposed metrics*, not a claim to state-of-the-art agent
accuracy. Concurrent work sharpens related diagnoses without overlapping that resource
claim. Espejo Morales *et al.* (arXiv:2607.19406) frame NMR elucidation as agentic search
and reach 20.6% on 34 industrial samples — independent support that proposal supply binds
on heterogeneous data. Wagen (Rowan Scientific) looped a frontier LLM with MagNET on eight
corrected misassignments (connectivity 46.4% → 55.4%) — consistent with a sharper verifier
helping most where stereochemistry is scored, without over-reading a preliminary n=8 study.
NMR-Solver (Jin *et al.*, 2025) implements the same generate-and-verify loop without an LLM
at higher accuracy; we cite it as external support for the mechanistic claim, since we
measure predictor resolution as a binding constraint and they convert a sharper predictor
into higher top-1.

Larger view-only databases exist (notably SDBS), but open, structure-linked, ML-ready
experimental IR band lists have been a standing gap. The core protocol uses no model
training and no paid API. Two probes are clearly fenced as complements: a small generator
fine-tuned on IRexp, which establishes that the recall wall is elicitation-specific rather
than task-intrinsic, and a learned ¹³C verifier. All data, frozen predictions, figures and
code are released; solver transcripts are available on request. Spectro, NMIRacle and CASE
are not yet scored on IRSpectra-Bench — an honesty we state in Limitations and leave to the
released leaderboard scorer.

The work is original, not under consideration elsewhere, and all authors approve the
submission. We have no competing interests to declare, and would be glad to suggest
referees with expertise in cheminformatics datasets and benchmarks, spectral machine
learning, NMR/IR structure elucidation and LLM evaluation.

Thank you for your consideration.

Sincerely,
Ilkham Yabbarov (corresponding author), Rudra Sondhi, and Rodrigo A. Vargas-Hernández
Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario, Canada
yabbaroi@mcmaster.ca

---

## Significance statement (for the field)

Open experimental IR for machine learning has lagged NMR: view-only archives such as SDBS
cannot be redistributed, and most elucidation benchmarks use simulated or single-instrument
spectra. This work releases **IRexp** (121,233 literature-mined band lists) and
**IRSpectra-Bench** (194 blind, mechanically scored compounds) as citable cheminformatics
infrastructure — with a fixed InChIKey scorer and decomposable recall/verification metrics —
then uses them to show where frontier LLMs actually fail on real peak lists: not near 100%
on curated demos, but 28% top-1 (15% corpus-reweighted). The binding constraint is
*candidate recall* (34%), not verification (89% conditional on recall): effort should
shift toward open data, wider generation, and inference-time methods that improve with
each model generation, not toward bespoke architectures alone.
