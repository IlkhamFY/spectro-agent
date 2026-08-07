# Draft subsection — "A learned ¹³C verifier closes the §5.4 gap" (extends/answers §5.4)

> **Status: superseded and merged.** This draft is kept as the working record of how the
> learned-verifier arm was designed and first measured. Its content now lives in §5.4 of
> `PAPER.md`, and the experiment has since been **extended from the 60-compound arm
> (n=19 conditional) to the whole 194-compound benchmark (n=65)**. Every number below is
> the original n=19 measurement and reproduces exactly
> (`python scripts/verifier_table.py`), but the paper reports the n=65 column:
> self-ranking 55/65 (85%), HOSE lookup 55/65 (85%), learned GNN 59/65 (91%), LLM
> verifier 58/65 (89%). See `data/fverify/verifier_table_results.txt`.

*Proposed addition for author review. This is the learned-predictor arm of the §5.4
HOSE ablation: same nmrshiftdb2 training data, same §5.2 candidate set, only the method
changes (learned-generalising GNN vs deterministic lookup). It directly revises §5.4's
conclusion ("not a generic lookup table … the LLM's breadth is the asset") and should be
read alongside it. Like §5.6, it is a *trained* complement to the training-free protocol —
positioning is the authors' call.*

---

## 5.7 The verifier gap is method, not just coverage: a learned ¹³C model closes it

§5.4 swaps the LLM forward-predictor for a *deterministic* HOSE-code lookup and finds it
does **not** help (14/19, 73%, *below* the LLM verifier's 16/19, 84%), attributing the
failure to **coverage, not method**: the benchmark's exotic chemistry is under-represented
in nmrshiftdb2, so a lookup degrades to coarse environment spheres exactly where
regiochemistry must be resolved. That diagnosis invites one obvious test it does not run:
the HOSE predictor is a *lookup*; would a *learned* model — trained on the **same data** —
generalise across those under-represented environments where the lookup cannot?

**Setup.** We train a small message-passing GNN (4 layers, hidden 256, GRU node update,
bond features; per-carbon ¹³C regression) on the **identical nmrshiftdb2 dump** that builds
the §5.4 HOSE table — 32,647 molecules / 350,313 assigned carbons (the §5.4 figures,
"31,000 / 332,595", are this set minus its random 5% held-out split). On a held-out test
split the GNN predicts ¹³C at **MAE 1.70 ppm (median 1.02)**, versus the HOSE lookup's
3.23 / 1.73 — an independently-competent predictor, so a benchmark result is interpretable
rather than an undertraining artefact. We then drop it into the verifier slot on the
**same §5.2 candidate set** (60 compounds, 126 candidates) and re-rank by the same
predicted-vs-observed ¹³C chamfer distance, holding training data and evaluation fixed.

**Result — a learned predictor recovers the full LLM-verifier precision the lookup could
not.** Conditional on recall (n=19), all four verifiers on the identical set:

| verifier (conditional on recall, n=19) | top-1 | held-out ¹³C MAE |
|---|--:|--:|
| solver self-ranking | 14/19 (73%) | — |
| deterministic HOSE lookup (§5.4) | 14/19 (73%) | 3.23 ppm |
| **learned GNN (same data)** | **16/19 (84%)** | **1.70 ppm** |
| LLM forward-verifier (§5.2) | 16/19 (84%) | — |

Holding the training data and the eval set fixed, swapping **lookup → learned** closes the
entire 73→84% gap and matches the LLM verifier (top-1 over all 60 rises 23→26%, as §5.4).
The §5.4 reading is therefore too strong: the deterministic verifier's failure was
substantially **method** (generalisation across novel environments), not only coverage. The
"genuine fix" §5.4 reaches for — *compound-specific DFT-level accuracy or 2D-NMR* — is not
required to match the LLM here; a generic learned model on the same lookup data suffices, at
no LLM cost and full reproducibility. The GNN and the LLM both score 84% but on *partly
different* compounds (the GNN wins R20/R21/R25; the LLM wins R22/R28), i.e. two independent
verifiers concurring on the precision rather than one.

**This is generalisation, not memorisation** (the decisive control for a learned verifier — a
GNN can memorise a specific molecule's spectrum where a HOSE bin-average cannot). Exact
overlap is **0/126** candidates by InChIKey-14, including every true structure and all three
GNN-beats-HOSE wins. Analog overlap is also absent: Morgan(2,2048) Tanimoto nearest-neighbour
to training has median 0.44, max 0.87, **0 identical**, and the three wins sit *at* the median
(NN 0.45–0.47), not elevated — were the wins driven by training proximity they would be the
high-similarity cases. GNN failures, conversely, are not the low-similarity (out-of-
distribution) compounds — R28 (NN 0.56) fails while R21 (0.46) succeeds — so failures track
near-degenerate regiochemistry (the §5.3/§5.5 precision mechanism), not training distance.

**Negative control (§5.5 Y-randomisation).** Re-pairing each candidate set with a deranged
observed spectrum (1000 permutations) collapses the GNN's conditional precision to a chance
mean of 58.6% (95% range 42.1–73.7%); the real 84% lies above the 97.5th percentile
(one-sided p < 0.05), so the re-ranker acts on genuine spectral agreement. (The chance floor
differs from §5.5's 66.4% because it is predictor-dependent — it reflects how each predictor's
shifts spread across the near-degenerate candidates.)

**Scope and honesty.** (i) A *trained* complement, reported alongside — not in place of — the
training-free protocol, exactly as §5.6. (ii) The decisive comparison is n=19; the +2 over HOSE
is **confirmatory of the LLM number**, not a precise quantitative gain — one win is decisive
(R21, 0.79 ppm margin), two are tight (0.21/0.33 ppm), and the lone loss (R26) was a 0.08 ppm
coin-flip. Near-degenerate regioisomers (R22/R26/R28) remain unresolved at ~1–2 ppm forward
accuracy, so the recall/precision ceiling of §5.3/§5.5 stands — the GNN reaches the LLM
verifier's quality cheaply, it does not break that ceiling. (iii) Single ¹³C modality, as the
HOSE arm.

*Artifacts:* `scripts/gnn_predict.py` (`extract`/`train`/`score`/`control`),
`data/fverify/gnn_results.txt` (full numbers + per-compound margins + both leakage checks),
`data/nmrshiftdb/gnn_c13.pt` (trained model). Same `data/fverify/candidates.jsonl` and
nmrshiftdb2 dump as §5.4.
