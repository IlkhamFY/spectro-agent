# Expert-chemist audit protocol (to close the §7 human-validation gap)

The single largest credibility gap versus a top-tier evaluation paper (cf. the
Nature Medicine clinical-AI study, which rests on 12 blinded clinicians) is that our
solver and verifier are both LLMs and **no human expert has reviewed the outputs**.
This protocol is designed so a small panel can close that gap with ~3–4 person-hours
each, producing two tables that slot directly into §4 and §5. It is deliberately
blinded, pre-registered, and mechanically scorable.

## Panel and scope

This protocol is **generated and frozen** — run `python scripts/make_audit_sample.py`
to (re)produce the blinded package under `data/audit/` (`sample.jsonl`, the separate
`key.jsonl`, rendered `structures/`, and `scoring_sheet.md`); see
[`data/audit/README.md`](../data/audit/README.md).

- **Reviewers:** 3 synthetic/analytical chemists (PhD-level), independent, no prior
  exposure to the benchmark answers.
- **Sample:** 30 compounds drawn stratified (15 simple, 15 complex; seed = 0) from the
  60-compound forward-verification set — the split that carries both the model's ranked
  candidates and the observed spectra — released as `data/audit/sample.jsonl`, so the
  draw is reproducible and pre-registered, not cherry-picked. Of the 30, **9 are
  recall-positive** (true structure among the candidates) and feed Task 2; the full
  set offers 19 recall-positive compounds for a higher-power panel.
- **Per compound, each reviewer sees:** formula + IR + ¹H + ¹³C (the exact solver
  prompt) and the model's **top-ranked candidate rendered as a 2D structure**,
  with model identity and the ground truth hidden (`key.jsonl` withheld).

## Task 1 — elucidation correctness (validates §4)

For each (compound, top-1 candidate), the reviewer answers, blind to the key:

1. **Consistency** (1–5): is the proposed structure consistent with *all* provided
   spectra? (5 = fully; 1 = contradicted.)
2. **Verdict** (correct / wrong-regiochemistry / wrong-scaffold / uninterpretable):
   their best categorical judgement of the failure mode, if any.
3. **Free-text:** the single most diagnostic peak that supports or refutes it.

*Read-out:* (a) inter-rater agreement (Fleiss' κ on the verdict); (b) the human
verdict distribution vs. the mechanical InChIKey score — in particular, **what
fraction of mechanically-"wrong" top-1s are judged "spectrally consistent but a
different regioisomer"**, which directly substantiates the paper's central
regiochemistry-bottleneck claim with human judgement rather than only string match.

## Task 2 — verifier calibration (validates §5)

For the recall-positive compounds (9 in the frozen sample; up to 19 across the full
forward-verify set), present the reviewer with the **candidate set**
(true + distractors, shuffled, unlabelled) and ask them to rank by spectral fit, then
compare:

- reviewer top-1 pick vs. the LLM forward-verifier's pick vs. the HOSE predictor's
  pick (§5.4), all on the identical candidate sets;
- whether the cases the forward-verifier gets right/wrong are the same ones humans
  find easy/hard (does the chamfer distance track human confidence?).

*Read-out:* a 3-way concordance table (human / LLM-verify / HOSE-verify) and the
human-vs-machine agreement conditional on recall — turning the 84% verifier-precision
number into a human-anchored claim.

## Reporting (drop-in tables)

> **Table A.** Human audit of top-1 elucidations (n=30, 3 reviewers, blinded). Mean
> consistency score; verdict distribution; Fleiss' κ; fraction of InChIKey-misses
> judged "consistent regioisomer."
>
> **Table B.** Verifier concordance on recall-positive compounds (n=19): human vs.
> LLM-forward vs. HOSE re-ranking; agreement conditional on recall.

## Integrity controls

- Reviewers are blind to model identity and ground truth throughout.
- The 30-compound sample, the rendered structures, and the scoring sheet are frozen
  and released under `data/audit/` *before* review begins.
- Scoring of the completed sheets is mechanical (no further model involvement).
- Pre-register the two read-out hypotheses (regiochemistry dominates misses;
  forward-match distance tracks human confidence) so the audit can disconfirm them.

## What this buys the paper

It converts the two load-bearing claims — *"misses are predominantly consistent
regioisomers"* and *"forward verification is a trustworthy re-ranker"* — from
machine-only evidence into human-validated findings, which is the standard a
Nature-tier evaluation paper is held to. It is the one experiment we cannot run
ourselves; everything needed to run it (sample, renders, sheets, scorer) can be
generated from the existing pipeline on request.
