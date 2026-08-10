# Submission checklist

Everything the repository can verify about this manuscript is verified and gated. This
file is the short list of what it cannot — the items that need a human, with enough
context to act on each without reconstructing how we got here.

Run this first; it re-checks the whole manuscript and prints the outstanding items:

```
python scripts/check_manuscript.py     # gates A–H, then the pending list below
python scripts/verify_statistics.py    # every hand-rolled statistic vs SciPy
```

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
of the 139 top-1 misses are constitutional isomers, 22.6% scaffold-preserving positional
errors (`scripts/analyze_misses.py`) — so what remains is the part no fingerprint
settles: **is a formula-correct, scaffold-wrong candidate a chemically reasonable
reading of these spectra, or an implausible one?**

## 3. Two things to re-check at submission

- **Spectro's split details.** We state a 1,366-molecule held-out split and describe its
  NMR as software-predicted. The 93%/82% accuracies are verified from the Crossref
  abstract; the split sizes and that characterisation sit in full text ChemRxiv serves
  only behind a 403. **Two co-authors wrote Spectro** — please confirm both.
- **NMRArena** (github.com/odanchem/NMRArena) benchmarks six general LLMs — Claude Opus
  4.8 among them — on 105 molecules with experimental ¹H/¹³C. Its citation is still a
  placeholder, so it is concurrent unpublished work and is deliberately uncited. It
  bears on Contribution 2's "to our knowledge the first of its kind"; if it has appeared
  by submission, cite it and re-check that hedge.

## 4. What is already verified (so you needn't re-do it)

Gates A–H in `check_manuscript.py`, all negative-tested — a deliberately injected defect
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

Plus: every hand-rolled statistic agrees with SciPy (McNemar, Fisher, Wilson,
point-biserial, CMH); **zero answer leaks** across 3,604 prompt/answer pairs; and every
number attributed to another paper checked against a primary source, with the results —
including what could not be verified — tabulated at the end of `docs/MODELS.md`.
