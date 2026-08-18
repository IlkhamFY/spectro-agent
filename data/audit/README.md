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
| compounds in sample | **30** (15 simple / 15 complex) |
| recall-positive (true structure among candidates) | **9** |
| …of those, carrying more than one distinct candidate → **Task 2** | **6** |
| model top-1 exact (kept in `key.jsonl` only) | 7/30 (23%) |

Three recall-positive compounds (A19, A21, A30) carry a single candidate and are
**excluded from Task 2**: there is nothing to rank, and because this kit states that
Task 2 appears only on recall-positive compounds, a lone candidate would tell a
reviewer it is the true structure — and hence that the model's Task 1 answer was
correct — with no chemistry involved.

Completed sheets are scored by `scripts/score_audit.py`, which defines the submission
format (one TSV per reviewer) and reports Fleiss' kappa, agreement with the mechanical
InChIKey scoring, and the Task-2 panel ranking.

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
- Scoring of completed sheets is mechanical (no further model involvement).
