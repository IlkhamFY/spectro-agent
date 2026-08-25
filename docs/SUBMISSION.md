# Submission checklist

Everything the repository can verify about this manuscript is verified and gated. This
file is the short list of what it cannot — the items that need a human, with enough
context to act on each without reconstructing how we got here.

Run this first; it re-checks the whole manuscript and prints the outstanding items:

```
python scripts/check_manuscript.py     # gates A–M, then the pending list below
python scripts/verify_statistics.py    # every hand-rolled statistic vs SciPy
python scripts/crossref.py docs/PAPER.md   # every figure/table/section reference resolves
python scripts/build_pdf.py            # docs/paper.pdf, docs/paper.tex, docs/paper_esi.pdf
python scripts/check_layout.py         # typographic layout gate (margins, orphans, table splits)
python scripts/make_all_figures.sh     # regenerate every figure plate (PNG + PDF)
```

`build_pdf.py` writes a **reading copy by default** (no line numbers). Set `LINENOS=1`
for a referee PDF when a journal asks for continuous line numbers at peer review —
they are not part of the printed article and should not be on the author PDF you
iterate against.

**Venue.** ChemRxiv first (deposit venue only — the PDF is a clean two-column article
with no ChemRxiv or journal chrome), then a journal with the PI (R. A. Vargas-Hernández).
The abstract is a single paragraph (~204 words). Keywords (for the ChemRxiv deposit form,
not printed in the PDF): structure elucidation; NMR spectroscopy; infrared spectroscopy;
large language models; chemical information; benchmark. Graphical abstract:
`docs/figures/graphical_abstract.png`.

---

## 1. Items only the authors can supply

None of these can be guessed, and a wrong one is worse for a reader than an
acknowledged gap — an ORCID belongs to a specific person and a DOI either resolves or
it does not.

| # | item | where it goes | note |
|---|---|---|---|
| 1 | **ORCID iDs**, all three authors | `docs/PAPER.md`, author block (visible `[TODO: 0000-…]` placeholders) | corresponding author's ORCID is typically required at submission |
| 2 | **Zenodo DOI** for the data/code deposit | `docs/PAPER.md`, Data and code availability (`[TODO: 10.5281/zenodo.XXXXXXX]`) | mint at submission; the Licensing section points re-users at it for attribution |
| 3 | **Funding sources and acknowledgements** | `docs/PAPER.md`, Acknowledgements (marked `— AUTHORS`) | currently the only empty section |
| 4 | **Target journal** | cover letter + submission metadata | decide with PI before finalising house style / cover letter |

### Not on this list any more: model snapshot identifiers

These were listed here until the authors confirmed the consumer harness never exposed
them. It does not hand the caller a checkpoint identifier, announce build changes, or
record which build served a request, so no snapshot can be reported and none can be
obtained after the fact. `docs/PAPER.md` §8 and `docs/MODELS.md` §6 now say that outright
instead of promising a value that cannot arrive, and state the two consequences: a
mid-window build change cannot be excluded, and a reader repeating the work will be served
a different build, so agreement is distributional rather than exact. Gate check J fails if
either file drifts back to describing them as pending.

## 2. The expert-chemist audit

`docs/EXPERT_AUDIT_PROTOCOL.md`; blinded 30-compound kit frozen at `data/audit/`
(regenerate with `scripts/make_audit_sample.py`). `docs/PAPER.md` Limitations formally
**defers** it — not run; do not describe it as merely "prepared."

**Do not substitute an LLM.** The paper's guarantee is that no LLM curates the labels or
scores the predictions; having one play chemist would falsify the claim the methodology
rests on, not approximate it.

The panel's question is narrower than it was. §4 now *measures* what a miss is — 76.6%
of the 137 analysable top-1 misses are constitutional isomers, 22.6% scaffold-preserving positional
errors (`scripts/analyze_misses.py`) — so what remains is the part no fingerprint
settles: **is a formula-correct, scaffold-wrong candidate a chemically reasonable
reading of these spectra, or an implausible one?**

## 3. Five recorded gaps in what was captured

Not defects in the results — every number regenerates — but things that were never
written down at run time and so cannot be recovered now. The ESI states each one where it
bears on a claim; they are collected here so nothing depends on a reader finding them.

| # | gap | where it bites |
|---|---|---|
| 1 | The instruction dispatched to the Claude solver and forward-prediction sub-agents was not captured; only the per-compound batch data it wrapped is released. The verbatim prompts in ESI S2 are the cross-vendor harness prompts. | reproducibility of the main arms |
| 2 | No dated model snapshot for any Claude arm, and the cross-vendor reasoning-effort tier per arm was not recorded. | exactness of any re-run; disclosed and gated (check J) |
| 3 | No decoding parameters were set or recorded — temperature, top_p, top_k, max_tokens, seed, thinking budget. | same |
| 4 | Sampling seed and draw parameters for the main round (140) and the controlled v3 round (40) are recorded nowhere. Only the within-compound control (`--n 20 --seed 23`) and the pilot (`--n 21 --seed 7`) appear in code. | the released benchmark is fixed and reusable, but not exactly re-drawable |
| 5 | Transcripts of the run-time closed-book audit are not deposited (available on request). | that audit cannot be re-verified from the release |

## 4. Two things to re-check at submission

- **Spectro's split details.** We state a 1,366-molecule held-out split and describe its
  NMR as software-predicted. The 93%/82% accuracies are verified from the Crossref
  abstract; the split sizes and that characterisation sit in full text ChemRxiv serves
  only behind a 403. **Two co-authors wrote Spectro** — please confirm both.
- **NMRArena** (github.com/odanchem/NMRArena) benchmarks six general LLMs — Claude Opus
  4.8 among them — on 105 molecules with experimental ¹H/¹³C. Its citation is still a
  placeholder, so it is concurrent unpublished work and is deliberately uncited. The
  absolute-first hedge on IRSpectra-Bench was softened (2026-08-25 audit) to name concurrent
  suites without claiming priority over unpublished benches; re-cite NMRArena if it appears
  before submission.

---

## 4b. Limitations locked from peer-review audit (2026-08-25)

`docs/PAPER.md` Limitations rewritten from the inspiro/peer-review audit: consumer-harness
non-reproducibility, uncaptured main-arm prompts, constitution/formula/object-type honesty,
statistical non-claims (p=0.55 / p=0.34 / n=24), missing on-bench baselines, candidate-budget
inequality, formally deferred expert audit, abandoned leave-one-modality arm. Author TODOs
(ORCID/Zenodo/funding) stay in this file, not in Limitations.

## 5. What is already verified (so you needn't re-do it)

Gates A–M in `check_manuscript.py`, all negative-tested — a deliberately injected defect
of each class fails the gate:

- dataset counts against the released files (121,233 / 43,060 / 33,201; licence pools
  119,345 / 1,888)
- every `a/b (c%)` internally consistent
- citations resolve both ways; every referenced script, figure and data path exists
- "never run" disclosures agree with what is on disk
- companion documents carry the same numbers as the paper
- every CI contains its point estimate
- all 242 ground-truth structures reproduce the formula the solver was given
- hardcoded figure values still match the scorers
- every correction propagated to every file that made the claim
- the unobtainable-snapshot disclosure is intact and consistent
- reader-facing numbers inside scripts match the paper
- cross-references derive from position, none typed by hand (`scripts/crossref.py`)
- companion documents point only at sections the paper actually has

Plus: every hand-rolled statistic agrees with SciPy (McNemar, Fisher, Wilson,
point-biserial, CMH); **zero answer leaks** across 3,604 prompt/answer pairs; and every
number attributed to another paper checked against a primary source, with the results —
including what could not be verified — tabulated at the end of `docs/MODELS.md`.

## 6. Editorial cuts applied

Agreed length cuts on `docs/PAPER.md` (main text only; ESI retained displaced detail):

| # | cut | status |
|---|---|---|
| (1) | SI figure catalogue → one ESI pointer | applied |
| (2) | artefacts table → ~10 headline rows | applied |
| (3) | Discussion diagnosis-only (concurrent systems stay in Related work) | applied |
| (4) | intro contribution bullets → one sentence | applied |
| (5) | formula-adherence paragraph (benchmark design) → ESI | applied |
| (6) | “Reconciling with prior reports” → 2–3 sentences | applied |
| (7) | within-compound control (n=20, p=0.25) → one sentence | applied |
| (8) | ECFP aside in Discussion | applied (with (3); Praski bib dropped) |

## 8. Combined figure plates (2026-08-25)

Nature-style multi-panel figures where panels share one claim:

| Plate | Status | Notes |
|---|---|---|
| `fig_robustness` | kept | contamination + cross-vendor (a–d); panel-b stats in caption, dashed line labelled “pooled” |
| `fig_forward_verify` | **reverted** | mechanism + ladder forced spectral panels into a squeezed column; restored separate `fig_mechanism` and `fig3_method` |

Main-text figures: wall, difficulty, models, robustness, mechanism, method ladder (+ graphical abstract).

## 7. Front-matter typography (2026-08-25 audit)

### Email and affiliation placement

**Decision: (b) — numbered affiliations below the author line; corresponding-author
email on the next line, before the abstract.** Not page-footnote affiliations (RSC
Medicinal Chemistry template), not after the abstract, not in the running footer.

| Option | Verdict |
|---|---|
| (a) Footnote with dagger at page bottom | RSC house style (see ParetoMol reference manuscript). Fine at journal transfer; footnotes fight ChemRxiv’s full-width title band and push contact detail off-screen on narrow previews. |
| **(b) Inline affiliations + email before abstract** | **Chosen.** Matches ChemRxiv deposit layout, NeurIPS/arXiv cs.LG preprint convention, and Digital Discovery reading-copy practice: contact block stays with the title, abstract remains unlabelled. |
| (c) After abstract | Splits the title block; email is harder to find in PDF thumbnails. |
| (d) Page footer | Non-standard for chemistry/ML venues; conflicts with page-number footer. |

Corresponding author: dagger (\\dag) on the author name **and** on the email line —
same pairing as the authors’ RSC article (`$^{a,\\dag}$` + footnote). Rodrigo’s
cross-affiliations render as italic superscripts **2,1,3** (Brockhouse, Chemistry,
Computational Science).

### Font stack (PDF pipeline)

Built by `scripts/build_pdf.py` → pandoc → tectonic (XeTeX), 10 pt `article`, A4
two-column (`columnsep=0.65 cm`, `microtype`, `titlesec`, `caption`, `fancyhdr`).

| Element | Family | Size (pt) | Notes |
|---|---|---|---|
| Title | Liberation Sans Bold | ~15 | `\LARGE\bfseries`, sans title band |
| Authors | Liberation Sans | ~12.5 | `\Large`, italic superscript markers |
| Affiliations | Liberation Sans | 10 | explicit `\fontsize{10}{12}` — overrides `Scale=MatchLowercase` shrink |
| Corresponding email | Liberation Sans Italic label | 10 | `\dag\ \textit{E-mail:}` |
| Abstract | Liberation Serif | ~10 | `\rmfamily\raggedright`; **no “Abstract.” label** |
| Body | Liberation Serif | ~10 | indented paragraphs, `\frenchspacing` |
| § heading | Liberation Serif Bold | ~12 | `\large\bfseries\raggedright` |
| §§ / §§§ | Liberation Serif Bold | ~10 | `\normalsize\bfseries\raggedright` |
| Figure caption | Liberation Serif Bold label + Serif text | ~9 | `caption` `font=small`, `Fig.` prefix |
| Table caption | Liberation Serif Bold + Serif | ~9 | markdown `\textbf{Table N.}` in `\caption*` |
| Table body | Liberation Serif | ~9 | `\small` inside `table*` |
| Page number | Liberation Sans | ~8 | `\fancyfoot[C]{\small\thepage}` |
| Verbatim / code | LM Mono 10 / 9 | ~10 / ~9 | `fvextra` breakable `verbatim` |
| Math | Latin Modern Math | varies | unicode-math fallback for Greek, relations |

Liberation Serif/Sans stand in for Times/Helvetica (metric-compatible open fonts).
The old RSC ParetoMol manuscript used `mathptmx` + Charter (`bch`); this reading copy
keeps the sans title band but uses Liberation for the body — appropriate for ChemRxiv
and journal-agnostic submission.

### Spacing rhythm (title block)

`1 em` top pad → title → `0.5 cm` → authors → `0.35 em` → affiliations → `0.3 em`
→ email → `0.5 cm` → abstract → `1.0 cm` → two-column body. Section/float spacing
unchanged from the typographic-perfection pass (`titlespacing`, `\textfloatsep` 14 pt).

### Audit outcome (2026-08-25)

`check_manuscript.py` and `check_layout.py` pass on the rebuilt PDF. Visual scan: pages
1–3 (front matter, §2), 8 (Discussion/Limitations), 10 (back matter) — no regressions
to editorial cuts (1)–(8) or §2 orphan/layout fixes. Fixes applied in this audit:
affiliation/email band set to true 10 pt sans; corresponding-author asterisk upgraded
to dagger with matching author-mark.

### Title-block fontspec leak (2026-08-25)

Do not put `\fontspec[...]{...}` (or any `[...]` with a closing `]`) inside
`\twocolumn[{...}]`: TeX ends the optional argument at the first `]`, which leaked
`Liberation Sans[Scale=1.0]` as visible page-1 text. Affiliations/email use the
outer `\sffamily` group plus `\fontsize{10}{12}\selectfont` only. Abstract body is
`\raggedright` (scoped to the title-block group).
