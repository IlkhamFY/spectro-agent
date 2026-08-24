# Expert-audit package (frozen, blinded)

This directory is the **runnable instance** of the protocol in
[`docs/EXPERT_AUDIT_PROTOCOL.md`](../../docs/EXPERT_AUDIT_PROTOCOL.md). It lets a
panel of chemists validate the two load-bearing claims of the paper —
*misses are predominantly consistent regioisomers* (§4) and *forward verification
is a trustworthy re-ranker* (§5) — without seeing the ground truth.

Regenerate everything deterministically (seed = 0):

```bash
python scripts/make_audit_sample.py
```

## Sample

A difficulty-stratified draw from the 60-compound forward-verification set
(`data/fverify`), the only split that carries both the model's ranked candidates
(`self_rank`, `is_true`) and the observed spectra.

| | count |
|---|--:|
| compounds in kit | **37** (30 carry Task 1) |
| Task 1 panel (stratified draw, unbiased) | **30** |
| Task 2 items — every compound, so its presence signals nothing | **37** |
| …carrying the true structure **and** a real choice → verifier precision | **13** |
| …carrying the true structure but one candidate → excluded from precision | **3** |
| …carrying no correct candidate → expert calibration | **21** |
| model top-1 exact (kept in `key.jsonl` only) | 7/30 (23%) |

**Task 2 appears on every compound, and that is deliberate.** An earlier version showed
it only on recall-positive compounds, which leaked Task 1 twice over. In the extreme, a
recall-positive compound with a single candidate told the reviewer that candidate was the
true structure — and since the Task 1 image is one of the Task 2 candidates, that the
model's answer was correct: three of thirty verdicts, every one toward "correct". Less
obviously, the mere presence of a Task 2 block marked a compound as recall-positive, and a
correct top-1 is recall-positive by definition; across the panel that moved the rate of
correct answers from 12% to 67%, a five-fold prior available without reading a spectrum.
Restricting Task 2 to multi-candidate compounds only inverted the signal, because
answering with a single structure also correlates with being right. Showing it everywhere
removes the signal entirely.

Seven compounds (A31–A37) carry **Task 2 only** and no Task 1 item. Recall-positive
compounds could not simply be added to the Task 1 draw — a correct top-1 is recall-positive
by definition, so enriching for them would raise the very rate Task 1 exists to judge. The
Task 1 panel is therefore the original unbiased 30, and the extra compounds contribute
ranking data alone.

Completed sheets are scored by `scripts/score_audit.py`, which defines the submission
format (one TSV per reviewer) and reports Fleiss' kappa, agreement with the mechanical
InChIKey scoring, the Task-2 panel ranking, and expert confidence on the sets where
nothing on offer is correct.

The full forward-verify set has 19 recall-positive compounds; raise
`N_PER_STRATUM` (or score all of `data/fverify`) for a higher-power Task 2 panel.

## Files

- **`sample.jsonl`** — the BLIND reviewer input: per compound, the exact spectra
  shown to the model (formula, IR, ¹H, ¹³C), the model's top-1 SMILES, and — for
  recall-positive compounds — the full candidate set **shuffled and unlabelled**.
  Contains **no** ground truth and no `is_true` flags.
- **`key.jsonl`** — the SEPARATE answer key (true SMILES/InChIKey, whether the
  model's top-1 is correct, which shuffled candidate label is the true one). Do not
  show this to reviewers until scoring is complete.
- **`structures/`** — RDKit renders. `A{nn}_top1.png` is the model's pick (Task 1);
  `A{nn}_cand{A,B,…}.png` are the shuffled candidates (Task 2, recall-positive only).
- **`scoring_sheet.md`** — printable per-compound form (Task 1 + Task 2).
- **`worksheet.html`** — the same form as a self-contained local page: spectra and
  rendered structures inline, answers saved as you go, and an export that
  `scripts/score_audit.py` scores without re-typing. Open it from inside this
  directory (no server, no network). Regenerate with
  `python3 scripts/make_audit_worksheet.py`; it reads `sample.jsonl` and adds
  nothing, so the seed=0 content-key of the package still holds.
- **`responses/`** — completed reviewer files, one JSON each. See
  [`responses/README.md`](responses/README.md) for the schema.

## Tasks (see the protocol doc for the full rubric)

- **Task 1 — elucidation correctness.** For each compound, score the model's top-1
  for consistency with all spectra (1–5), give a categorical verdict
  (correct / wrong-regiochemistry / wrong-scaffold / uninterpretable), and name the
  single most diagnostic peak. Read-out: human verdict vs. the mechanical InChIKey
  score, and the fraction of mechanical misses judged "consistent regioisomer."
- **Task 2 — verifier calibration.** On recall-positive compounds, rank the
  shuffled candidates by spectral fit. Read-out: human top-1 vs. the LLM
  forward-verifier vs. the HOSE predictor on the identical candidate sets.

## Integrity controls

- Reviewers are blind to model identity and to ground truth (`key.jsonl` withheld).
- The sample, renders, and scoring sheet are frozen and content-keyed (seed = 0),
  so this package is fixed *before* review begins and is byte-reproducible.
- Scoring of completed sheets is mechanical (no further model involvement):
  `python3 scripts/score_audit.py` emits Table A and Table B from the committed
  responses plus the withheld key.
- Three Task-2 sets (**A19, A21, A30**) hold a single candidate. Nothing there can be
  ranked, and because Task 2 is shown only on recall-positive compounds, a lone
  candidate is necessarily the true structure — which also discloses that compound's
  Task-1 answer. The scorer excludes them from Table B and flags them; treat their
  Task 1 as unblinded until the sample is redrawn.
