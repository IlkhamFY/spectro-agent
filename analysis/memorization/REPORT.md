# Memorization proxy for the locked n=500 set

This note compares the locked IRSpectra-Bench headline set with public chemical databases. The benchmark models were not trained here. ChEMBL and PubChem are proxies for molecules a general LLM is likely to have seen, in the same spirit as the Tanimoto-to-training plot in ChefNMR2 (bioRxiv 2026.10.29.762711).

## Findings

- Claude Opus on the locked set is 227/500 top-1 (45.4% [41.1-49.8]) and 249/500 top-3 (49.8% [45.4-54.2]). The script stops if those integers move.
- ChEMBL 37 contains the connectivity of 46/500 molecules (median max Tanimoto 0.58). Opus top-1 by bin: <0.4 19.4% [9.8-35.0] (n=36); 0.4-0.6 38.7% [32.8-44.9] (n=243); 0.6-0.8 53.1% [45.0-60.9] (n=147); >=0.8 57.1% [39.1-73.5] (n=28); exact 69.6% [55.2-80.9] (n=46).
- Top-1 is 69.6% [55.2-80.9] on molecules whose connectivity is in ChEMBL and 36.2% [30.8-42.0] when the nearest ChEMBL neighbor has Tanimoto below 0.6. The Wilson intervals do not overlap.
- PubChem contains the connectivity of 214/500 molecules. Opus top-1 is 65.9% [59.3-71.9] on those and 30.1% [25.0-35.6] on the rest. The Wilson intervals do not overlap. 15/500 have a short common-name title. Median synonym count is 0 on the full set and 2 among molecules in PubChem. The famous flag (a short PubChem title and at least 15 synonyms) is on for 10/500 molecules, with top-1 90.0% [59.6-98.2] against 44.5% [40.1-48.9] when it is off. A count-only cut at 30 synonyms covers 21 molecules (90.5% [71.1-97.3]). Neither cut is large enough to be the headline.
- Deposited answers are ranked SMILES. No reasoning trace is stored in the prediction files. A scan of those strings for the PubChem common name found 0/500 mentions, so an accuracy split by naming is empty on one side. Source-paper years were found for 499/500 molecules (median 2020, range 2005 to 2026). Top-1 by year is 2005 to 2015 54.9% [44.1-65.2] (n=82); 2016 to 2019 40.8% [32.7-49.4] (n=130); 2020 to 2022 41.7% [34.5-49.2] (n=168); 2023 to 2026 48.7% [39.9-57.6] (n=119). There is no cliff at recent years. Of 473 molecules with a ring scaffold, 333 (70.4%) have that Bemis-Murcko scaffold in ChEMBL. Median MCES atom-Tanimoto to the nearest ChEMBL neighbor is 0.69.

## Rebuttal paragraph

We did not train on this benchmark. As a public proxy for structures a frontier model is likely to have seen, we scored the locked n=500 set against ChEMBL 37 (Morgan radius 2, 2048 bits, no stereochemistry) and against PubChem. Claude Opus is 227/500 top-1 (45.4% [41.1-49.8]) and 249/500 top-3. Top-1 is 69.6% [55.2-80.9] on molecules whose connectivity is in ChEMBL and 36.2% [30.8-42.0] when the nearest ChEMBL neighbor has Tanimoto below 0.6. The Wilson intervals do not overlap. PubChem contains the connectivity of 214/500 molecules. Opus top-1 is 65.9% [59.3-71.9] on those and 30.1% [25.0-35.6] on the rest. The Wilson intervals do not overlap. The famous flag (a short PubChem title and at least 15 synonyms) is on for 10/500 molecules, with top-1 90.0% [59.6-98.2] against 44.5% [40.1-48.9] when it is off. A count-only cut at 30 synonyms covers 21 molecules (90.5% [71.1-97.3]). Neither cut is large enough to be the headline. Deposited answers are ranked SMILES. No reasoning trace is stored in the prediction files. A scan of those strings for the PubChem common name found 0/500 mentions, so an accuracy split by naming is empty on one side. ChEMBL and PubChem are not the training corpus of any model here, so overlap is evidence of public availability rather than proof of memorization. The drop on dissimilar molecules is a real limit. It does not turn the whole headline into exact recall of public structures, because most of the set is not an exact copy and that majority is still partly solved.

## What was scored

The locked set is the n=194 cohort from `scripts/score_main.py`, plus all 106 deposited Opus answers in `data/benchmark_expand`, plus the first 200 validate-clean qids of `data/benchmark_expand_500` after a string sort (`headline500_expand200_qids.json`). That is the cut in `HEADLINE_n500_2026-09-20.md` on commit `48fcd30153df`. Scoring is InChIKey connectivity, first 14 characters. Top-1 is the first candidate. Top-3 is the locked recall@3. Gold SMILES for the expansion rounds were rebuilt by an exact (13C text, IR band) match to `data/irexp_resolved/irexp_resolved.jsonl.gz`. The match is unique on this set. The script checks 227/500 and 249/500 before it writes figures.

Other deposited models are scored only where they have a complete protocol. Claude Fable, Sonnet, and Haiku cover the fixed 24-compound ladder inside the main round. Grok 4.6, Gemini 3.7 Flash, and GPT-5.6 Sol cover the 60-compound vendor arm (`benchmark_v3` plus `benchmark_v2_ctrl`), with ids matched to `sweep_prompts/solve_01.md`. An unfinished Fable deposit on the +106 round is not scored. The locked pooler also ignores that tree.

Coverage:

- Claude Opus: n=500 (n194, plus106, plus200), top-1 45.4% [41.1-49.8], top-3 49.8% [45.4-54.2].
- Claude Fable: n=24 (n194), top-1 45.8% [27.9-64.9], top-3 54.2% [35.1-72.1].
- Claude Sonnet: n=24 (n194), top-1 20.8% [9.2-40.5], top-3 25.0% [12.0-44.9].
- Claude Haiku: n=24 (n194), top-1 0.0% [0.0-13.8], top-3 4.2% [0.7-20.2].
- Grok 4.6: n=60 (n194), top-1 38.3% [27.1-51.0], top-3 53.3% [40.9-65.4].
- Gemini 3.7 Flash: n=60 (n194), top-1 38.3% [27.1-51.0], top-3 50.0% [37.7-62.3].
- GPT-5.6 Sol: n=60 (n194), top-1 35.0% [24.2-47.6], top-3 41.7% [30.1-54.3].

## Proxies

ChEMBL file: `chembl_37_chemreps.txt.gz` (2897804 fingerprinted rows, 2756580 connectivity keys). Fingerprints are Morgan radius 2, 2048 bits, stereochemistry removed, the same setting as ChefNMR2. Exact means the gold connectivity key is in the ChEMBL file. The bins are exact, then >=0.8, 0.6-0.8, 0.4-0.6, and <0.4, and exact rows are not also placed in >=0.8. Bemis-Murcko scaffolds use RDKit canonical SMILES. MCES is the atom Tanimoto of a maximum common substructure against the nearest fingerprint neighbor, with a one-second cap. A neighbor with the same connectivity key is recorded as 1.

PubChem uses PUG REST on the connectivity InChIKey. The parent record is the lowest CID. The famous flag requires a short non-systematic title and at least 15 synonyms. A separate row uses a synonym count of at least 30 with no name filter. Source year is the Europe PMC `pubYear` for the PMCID on the gold record. Intervals are 95% Wilson intervals. Counts are in `tables/`.

## Figures

`figures/fig_similarity` is Claude Opus on the full set. Panel a is top-1 and top-3 by ChEMBL bin. Panel b is the famous flag. Bar labels are the percent. Whiskers are Wilson intervals. The count under each bin is n.

`figures/fig_heatmap` is Opus top-1 by heavy atoms and ChEMBL bin. Each cell shows the percent, the Wilson interval, and n.

`figures/fig_models` is top-1 with Wilson intervals for every deposited model, split at Tanimoto 0.6. Opus on the other models' own molecules is drawn in the same accent so those rows share a denominator. Grey rows are the other models. Sets are not the same size. The full bin table is `tables/accuracy_by_similarity.md`.

## Limits

ChEMBL and PubChem are not the training set of Claude, Grok, Gemini, or GPT. Presence is a public-availability proxy. Absence is not proof the molecule was unseen. Novel papers can describe molecules that are still one edit from a ChEMBL neighbor. The famous threshold is a choice. The synonym counts and the common-name bit are in the tables so the cut can be moved. Reasoning traces were not stored with the deposits, so the name probe only sees the saved answer strings. No NIST spectra and no CC BY-NC dump are included. Locked benchmark files were not modified.
