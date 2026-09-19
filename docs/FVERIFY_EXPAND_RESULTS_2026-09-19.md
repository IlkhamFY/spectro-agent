# Forward Verification — Expansion Round Results

**Date:** 2026-09-19
**Model:** Claude Opus 4.6, thinking=false, effort=medium
**Method:** LLM forward-verification (heuristic 13C shift prediction from SMILES alone, no GNN, no spectrum lookup)

## Protocol

Blind 13C chemical shift predictions were made for 286 unique candidate SMILES
across 101 expansion-round compounds. Candidates were anonymised and shuffled
(seed=11); the predictor saw only the SMILES structure, never the observed
spectrum, compound identity, or which candidates belong together.

Reranking was performed by chamfer distance between predicted and observed 13C
shifts, following the identical protocol as the original forward-verification arm
(§5.2).

## Results

| Metric | Count | Rate |
|---|---|---|
| Compounds scored | 101 | — |
| Recall (true answer in candidate set) | 65/101 | 64% |
| Top-1, solver self-rank | 61/101 | 60% |
| Top-1, forward-verified rerank | 52/101 | 51% |

### Conditional on recall (n=65)

| Metric | Count | Rate |
|---|---|---|
| Self-rank correct | 61/65 | 94% |
| Forward-verified correct | 52/65 | 80% |

### Breakdown

- **Verified (forward-verify agrees with truth):** 52
- **Misranked (true candidate present but not top-ranked by fverify):** 13
- **Never-proposed (true answer absent from candidate set):** 36

### Conditional precision

Forward-verified conditional precision (among compounds where the true answer
was in the candidate set): **80%** (52/65).

## Notes

- This is an LLM-based forward verification, not a GNN prediction.
- 286 unique SMILES were predicted across 17 batch files (f1.json–f17.json).
- The heuristic predictor uses functional-group-based 13C shift estimation rules
  applied to each carbon atom in the molecule.
- The self-rank baseline (solver's original ranking) achieves 94% conditional
  precision, while the forward-verification reranking achieves 80% — the gap
  reflects the coarseness of the heuristic shift estimator compared to the
  solver's domain-specific ranking.
