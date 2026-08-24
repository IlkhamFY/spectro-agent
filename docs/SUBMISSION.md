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
```

`build_pdf.py` writes line numbers by default, which is what RSC asks for under review;
set `LINENOS=0` for a reading copy.

**Venue.** *Digital Discovery* (RSC) Article. The abstract is a single paragraph of 232
words (RSC: 50–250, one paragraph). Suggested submission-system keywords: structure
elucidation; NMR spectroscopy; infrared spectroscopy; large language models; chemical
information; benchmark. Graphical abstract: `docs/figures/graphical_abstract.png` plus
the ≤250-character TOC text that `scripts/build_pdf.py` appends.

---

## 1. Three values only the authors can supply

None of these can be guessed, and a wrong one is worse for a reader than an
acknowledged gap — an ORCID belongs to a specific person and a DOI either resolves or
it does not.

| # | item | where it goes | note |
|---|---|---|---|
| 1 | **ORCID iDs**, all three authors | `docs/PAPER.md`, author block (visible `[TODO: 0000-…]` placeholders) | RSC requires the corresponding author's; co-authors' are requested |
| 2 | **Zenodo DOI** for the data/code deposit | `docs/PAPER.md`, Data and code availability (`[TODO: 10.5281/zenodo.XXXXXXX]`) | mint at submission; the Licensing section points re-users at it for attribution |
| 3 | **Funding sources and acknowledgements** | `docs/PAPER.md`, Acknowledgements (marked `— AUTHORS`) | currently the only empty section |

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
(regenerate with `scripts/make_audit_sample.py`). §7 reports it as prepared but not run.

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
  placeholder, so it is concurrent unpublished work and is deliberately uncited. It
  bears on Contribution 2's "to our knowledge the first of its kind"; if it has appeared
  by submission, cite it and re-check that hedge.

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
