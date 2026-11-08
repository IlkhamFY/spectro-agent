# What else can be scored on printed IR + ¹H + ¹³C lists

Date of the runs below: 2026-11-08. This note extends the exclusion table in `analysis/iclr_rebuttal_nov2026/specialized_methods/REPORT.md` (pull request 144). It does not repeat that table. It records solvers that can take the frozen printed lists, and the InChIKey-14 scores from the runs that finished here.

No runner was given the gold SMILES or the gold InChIKey. Scoring reads the answer key only after the ranked list is written. IR bands are present on every question and were not passed to any runner below: none of these systems has a band-list IR channel.

## Contract

A prediction is a top-1 hit when the first ranked structure has the same RDKit InChIKey connectivity block (characters 1–14) as the answer key. Recall means that key appears anywhere in the list that runner emitted. The list length is in the notes. Invalid SMILES do not match.

The n=60 arm is `data/benchmark_v3` (40) plus `data/benchmark_v2_ctrl` (20), the forward-verify slice. The n=194 arm adds the clean locked main round (134). The n=500 headline adds the 106-question expansion and the 200-question cut of `benchmark_expand_500` at git `48fcd30153df5e331fab43cfa514763db8ee3891`. Expansion keys are the unique `(formula, IR, ¹³C)` join used when that headline was scored. The join is not an input.

## Scores

| Method | Input it needs | Runnable on printed lists | n scored | Top-1 | Recall | Notes |
|---|---|---|---|---|---|---|
| NMRTrans (Yang et al., already scored) | Formula plus unordered ¹H and ¹³C peak sets | Yes. No IR channel | 500 | 79/500 | 102/500 | Not re-run. Beam 3, offline, from the submitted SI. Nine gold keys sit in its released training split. Listed so this table has the one trained model already on the roster. |
| ChefNMR2 (Xiong et al., bioRxiv 2026, doi 10.64898/2026.10.29.762711) | Formula (with H) plus a ¹H list `(shift, integral, multiplicity)` and a ¹³C shift list | Yes. IR is not an input | 60 | 28/60 | 35/60 | Public weights `ziyux123/chefnmr2` revision `38a741c`, ten checkpoints, code `ml-struct-bio/chefnmr2`. CPU only. Budget is 10 draws total, one from each checkpoint, seed 0, 50 diffusion steps. That is the README's fixed budget with `n_samples=10`, not the paper's adaptive 100 / 1,000 / 3,000. All 60 calls returned `ok`. Recall is the vote-ranked list (mean length 3.3); 32/60 are inside the top 3. Simple 22/30 top-1 and 25/30 recall; complex 6/30 and 10/30. Molecule time sums to 4,212 s (median 34 s; v2ctrl:R20 took 983 s). One question (v2ctrl:R04) had no parsed integral and was scored from formula + ¹³C; it missed. |
| NMR2Struct, ¹³C-only checkpoint (Hu et al. 2024) | Comma-separated ¹³C ppm list, discretized on the published 80-bin grid | Yes for the carbon list. The proton channel is the published `hnmr_file=None` zero vector. Formula and IR are not inputs | 60 | 1/60 | 1/60 | `cnmr_only_checkpoint.pt`. Fifteen samples, top-5 sampling, ranked by log-probability. Recall is inside those 15. Every hit has ≤19 heavy atoms (the paper's stated domain): 1/22 top-1 and 1/22 recall at ≤19, 0/38 above. Rank-1 formula matched the given formula on 1/60. |
| NMR2Struct, ¹³C-only, same protocol | Same | Same | 194 | 3/194 | 5/194 | Same checkpoint and 15 samples. Hits: main 2/134 top-1 and 4/134 recall, v3 1/40 and 1/40, v2-control 0/20 and 0/20. All five recalls have ≤19 heavy atoms (3/85 top-1 and 5/85 recall in that slice, 0/109 above). Rank-1 formula matched on 4/194. |
| NMR2Struct, ¹³C-only, same protocol | Same | Same | 500 | 8/500 | 16/500 | 194 plus the 306 headline-expansion questions. Expansion alone is 5/306 top-1 and 11/306 recall. All 16 recalls have ≤19 heavy atoms: 8/207 top-1 and 16/207 recall in that slice, 0/293 above. This is a ¹³C-list result. It is not an IR+¹H+¹³C score, and it is not the paper's ¹H+¹³C top-15 figure. |
| NMR2Struct, joint ¹H+¹³C checkpoint | ¹H file of `(ppm, intensity)` pairs plus the ¹³C list | No | 0 | — | — | The bench ¹H field is a multiplet table. Building an intensity trace was not done. |
| Regioisomer enumeration + GNN ¹³C rank | A seed SMILES pool, the formula those seeds already have, and the printed ¹³C list as the ranking target | Yes, as a way to enlarge *k*. It is not de novo from the lists | 60 | 17/60 | 29/60 | Seeds are the frozen `data/fverify/candidates.jsonl` SMILES (126 candidates). `is_true` was ignored and the gold structure was not inserted. `scripts/enumerate_isomers.py` (cap 300 per seed) grew 52/60 pools; median size 27. Recall 29/60 is membership in that pool. The GNN order places 27/60 inside its top 3 and 17/60 at rank 1. The un-enlarged GNN re-rank reproduces the stored result: top-1 16/60, recall 19/60 (`data/fverify/gnn_results.txt`). Enumeration added 10 truths and one top-1. |
| SURGE 2.0 formula enumeration, then a ¹³C ranker | Molecular formula, then a ranker against the ¹³C list | The generator runs. Ranking the finished spaces does not, on this arm | 0 | — | — | Built-in elements are C, B, N, P, O, S, H, Cl, F, Br, I. Six of 60 formulas contain Si or Se and were not generated. Of the rest, an 8 s count finished for two formulas: C9H9BrO = 4,178,414 isomers (0.62 s) and C9H10N2 = 46,004,495 (3.99 s). C8H7NOS, the smallest heavy-atom count on the arm (11), finishes in 8.12 s at 95,345,914 isomers. Fifty-one other formulas did not finish the count in 8 s. No space was ranked. MAYGEN is the same task and was not run separately. |
| HOSE / increment ¹³C lookup (`scripts/hose_predict.py`, nmrshiftdb2 `predictorc.jar`, CDK casekit) | A candidate structure, plus the HOSE table built from nmrshiftdb2 | The ranker code is in-tree. The table is not | 0 | — | — | `nmrshiftdb2.sd` (138 MB) and `predictorc.jar` (36 MB) are the public files. SourceForge returned HTTP 403 from this environment. `data/nmrshiftdb/hose_c13.json.gz` is gitignored and absent, so the table was not rebuilt. The stored n=60 re-rank of an existing pool remains top-1 14/60, recall 19/60 (`data/fverify/hose_results.txt`). That is not a new de novo run. |
| SpecMol / MolSpectLLM (Shen et al., arXiv 2509.21861) | Text spectra. ¹H and ¹³C are close to these lists. IR is frequency–intensity pairs and MS is `m/z`:abundance | No | 0 | — | — | `Eurekashen/SpecMol` has no checkpoint, safetensors, or `.pt` file on `main`. A Hub search under `Eurekashen` returned no model or dataset repos. The ¹H+¹³C prompt still cannot be scored. |
| NMR-Solver | Literature-style ¹H/¹³C paragraphs, plus the SimNMR-PubChem retrieval index | The text format matches. The index was not fetched | 0 | — | — | The index is on the order of 500 GB (about 373 GB plus a 128 GB index in the earlier note). It was not downloaded. A blind run must also take the element set from the formula and must not pass the gold SMILES into the released `run.py`. |
| MMST | ¹H, ¹³C, HSQC, COSY, an IR intensity vector, and MS; ranking uses HSQC | No | 0 | — | — | The roster has no HSQC, COSY, or MS, and the IR field has no intensities. Not an adapted run, and not a comparable IR+¹H+¹³C number. |
| SECS | A length-10,000 ¹H intensity vector, or JCAMP-DX / Bruker / Varian files | No | 0 | — | — | Printed peak lists are the representation SECS distinguishes itself from. No trace was synthesized. Not a comparable number. |

## How the new runs were kept off the answer key

- NMR2Struct reads a text file of ¹³C ppm values. The driver writes that file from `parse_c` of `c_nmr` and passes `hnmr_file=None`. The formula, the IR list, and the answer key are not arguments.
- ChefNMR2 receives `formula`, `parse_h(h_nmr)`, and `parse_c(c_nmr)`. The parser is in `peaks.py`. On the n=60 arm, 52/60 parsed integrals fall within 1 H of the formula hydrogen count. The other eight are short printed lists or position-label notation (`5H d`, `2H′`); those peaks are dropped rather than filled in as 1 H. `parse_c` matches the ¹³C shifts already stored on `data/fverify/candidates.jsonl` for all 60 questions.
- The regioisomer runner seeds only the deposited candidate SMILES. The GNN then ranks by symmetric chamfer of predicted versus printed ¹³C shifts.
- SURGE receives the formula string and nothing else.
- The expansion answer keys are built by the corpus join after the predictions exist. A question with not exactly one hit aborts the loader. All 306 expansion questions had one hit.

## What this does not support

The harness headline on the full three-list input stays the submitted figure: top-1 227/500, recall 249/500. NMRTrans remains the only trained model in that comparison that was scored on all 500, and it does not read IR.

On this same n=60 arm the frozen harness pool is generation recall 19/60, self-rank top-1 14/60, forward-verified top-1 16/60 (`data/fverify/results.txt`). That pool is at most three proposals and it does see the IR list. ChefNMR2's 28/60 and 35/60 are ten draws from formula + printed NMR only. The two protocols are not interchangeable, and neither number is an n=500 IR+¹H+¹³C score.

NMR2Struct's 8/500 is a ¹³C-list sample of 15, and every hit has at most 19 heavy atoms. MMST and SECS are not given a score.

## Files

Runners live in this directory. Prediction files are under `outputs/`. Third-party checkouts and weights were not committed.

```bash
# n=60 / n=194 / the 306-question expansion piece of n=500
NMR2STRUCT_ROOT=/path/to/NMR2Struct \
  python analysis/iclr_rebuttal_nov2026/extra_solvers/run_nmr2struct_c.py \
  --arm 60 --out analysis/iclr_rebuttal_nov2026/extra_solvers/outputs/nmr2struct_c.jsonl

python analysis/iclr_rebuttal_nov2026/extra_solvers/score_predictions.py \
  --arm 60 --pred analysis/iclr_rebuttal_nov2026/extra_solvers/outputs/nmr2struct_c.jsonl \
  --out analysis/iclr_rebuttal_nov2026/extra_solvers/outputs/nmr2struct_c_score.json

python analysis/iclr_rebuttal_nov2026/extra_solvers/run_regio_gnn.py

CHEFNMR2_CKPT=/path/to/ziyux123-chefnmr2 \
  python analysis/iclr_rebuttal_nov2026/extra_solvers/run_chefnmr2.py \
  --arm 60 --n-samples 10 --seed 0 \
  --out analysis/iclr_rebuttal_nov2026/extra_solvers/outputs/chefnmr2_arm60_n10.jsonl
```

The committed NMR2Struct files are the four shards for each arm. `score_predictions.py` accepts several `--pred` paths. n=500 is the sum of the n=194 score and the 306-question score (8/500 top-1, 16/500 recall).
