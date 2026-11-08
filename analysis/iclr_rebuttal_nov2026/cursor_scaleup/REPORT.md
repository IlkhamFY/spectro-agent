# Cursor-scale arm on IRSpectra-Bench

This file is an additional system. It does not replace the locked Claude headline.

Model id: `grok-4.7-high-fast`. That is `originalModelName` on cloud run `bc-7b28bf66-ffdb-5c8e-a63f-1fc38e11fc5a`. Each batch was a fresh subagent of that run. No external vendor API key was present, so no other model was called.

Request: up to 10 distinct constitutions, best first. Closed book. The prompt fields were molecular formula, IR band list, printed 1H, and printed 13C. Gold SMILES and InChIKey were not in the prompt. `export` does not open an answer file.

Scoring is RDKit InChIKey connectivity (first 14 characters), offline, after the prediction JSONL was written. `list_kind=unique_constitutions` keeps the first parseable SMILES of each connectivity and drops later duplicates. Unparseable strings are dropped rather than promoted. Fractions below are copied from `scores_n60.csv`, `scores_n500.csv`, `scores_n218.csv`, `scores_posthoc_sum500.csv`, `inventory.csv`, and `prefix_scores.csv`.

## Locked Claude headline, unchanged

Recomputed from the deposited Claude lists by `inventory.py`. These integers matched the lock, and this arm does not edit them.

| quantity | fraction |
|---|---|
| self-rank top-1 | 227/500 |
| recall at the stored lists (maximum length 3) | 249/500 |
| precision given recall | 227/249 |

Arithmetic from those fractions: generation misses are 251/500, because 500 − 249 = 251, and self-rank misses among the recalled items are 22/249, because 249 − 227 = 22. The forward-verify wall was not refit in this directory. No Cursor number is substituted for 227/500.

`checks.json` records the same lock, plus the n=60 Claude original arm 14/60 top-1 and 19/60 recall, and the stored generate-wide union recall 25/60:

```json
{
  "locked_top1": "227/500",
  "locked_recall": "249/500",
  "locked_precision_given_recall": "227/249",
  "n60_original_top1": "14/60",
  "n60_original_recall": "19/60",
  "wide_union_recall": "25/60",
  "n_deposits": 26,
  "n_prefix_rows": 83,
  "n_prefix_rows_k_ge_4": 11,
  "max_k_scored": 9,
  "generator_unordered_recall": "94/248",
  "generator_file_keys": 248,
  "generator_max_stored": 40,
  "missing_wide_keys": [
    "V3-R27"
  ],
  "expand_sha": "48fcd30153df5e331fab43cfa514763db8ee3891"
}
```

## What was already on disk

Every generation deposit found in this checkout, plus the expansion lists at `48fcd30153df5e331fab43cfa514763db8ee3891` and the partial Fable lists at `473030fb9d046548ff1ad06d04d20915fc2943d2`. Top-1 and recall are the full stored raw list. `analysis/iclr_rebuttal_nov2026/` on current `main` had no prediction JSONL; the three notes on other branches are prose, not extra candidate lists.

| model | subset | n | max_stored_raw | max_stored_unique | top1 | recall | precision_given_recall | path |
|---|---|---|---|---|---|---|---|---|
| Claude Opus 4.8 (pilot, one context) | n21 | 21 | 1 | 1 | 1/21 | 1/21 | 1/1 | data/benchmark/predictions.jsonl |
| Claude Opus (one long context) | n20-long-context | 20 | 3 | 3 | 0/20 | 1/20 | 0/1 | data/benchmark_v2/predictions2.jsonl |
| Claude Opus (original ≤3) | n60 | 60 | 3 | 3 | 14/60 | 19/60 | 14/19 | data/benchmark_v3/predictions2.jsonl + data/benchmark_v2_ctrl/predictions2.jsonl |
| Claude Opus generate-wide | n60 | 60 | 6 | 6 | 13/60 | 24/60 | 13/24 | data/gw/raw/g1.json–g10.json |
| Claude Opus original then generate-wide | n60 | 60 | 9 | 9 | 14/60 | 25/60 | 14/25 | data/benchmark_v3 + data/benchmark_v2_ctrl predictions, then data/gw/raw/g*.json |
| Claude Sonnet generate-wide | n12 | 12 | 5 | 5 | 2/12 | 4/12 | 2/4 | data/gw/raw/sonnet_b1.json + sonnet_b2.json |
| grok-4.6 | n60 | 60 | 3 | 3 | 23/60 | 32/60 | 23/32 | sweep_out/grok-4.6 |
| grok-4.6-clean | n60 | 60 | 3 | 3 | 19/60 | 28/60 | 19/28 | sweep_out/grok-4.6-clean |
| gemini-3.7-flash | n60 | 60 | 3 | 3 | 23/60 | 30/60 | 23/30 | sweep_out/gemini-3.7-flash |
| gpt-5.6-sol | n60 | 60 | 3 | 3 | 21/60 | 25/60 | 21/25 | sweep_out/gpt-5.6-sol |
| gpt-5.6-luna | n60 | 60 | 3 | 3 | 6/60 | 9/60 | 6/9 | sweep_out/gpt-5.6-luna |
| composer-2.5 | n60 | 60 | 3 | 3 | 10/60 | 12/60 | 10/12 | sweep_out/composer-2.5 |
| Claude Opus modality full | n60 | 60 | 3 | 3 | 14/60 | 19/60 | 14/19 | data/modality/out_full.json |
| Claude Opus formula-only | n60 | 60 | 3 | 3 | 3/60 | 3/60 | 3/3 | data/modality/out_formulaonly.json |
| Claude Opus | main-clean | 134 | 3 | 3 | 41/134 | 46/134 | 41/46 | data/benchmark_main/raw/*.json |
| Claude Sonnet | main24 | 24 | 3 | 3 | 5/24 | 6/24 | 5/6 | data/benchmark_main/sonnet/*.json |
| Claude Haiku | main24 | 24 | 2 | 2 | 0/24 | 1/24 | 0/1 | data/benchmark_main/haiku/*.json |
| Claude Fable 5 | main24 | 24 | 3 | 3 | 11/24 | 13/24 | 11/13 | data/benchmark_main/fable/*.json |
| Claude Opus (rescored main-round lists) | main24 | 24 | 3 | 3 | 6/24 | 7/24 | 6/7 | data/benchmark_main/raw/*.json |
| Claude Opus | electrolyte | 46 | 3 | 3 | 12/46 | 13/46 | 12/13 | data/benchmark_electrolyte/raw/*.json |
| Claude Opus (expand +106) | n106 | 106 | 3 | 3 | 63/106 | 68/106 | 63/68 | 48fcd30153df5e331fab43cfa514763db8ee3891:data/benchmark_expand/predictions2.jsonl |
| Claude Opus 5 thinking-high (expand-500, 200-cut) | n200 | 200 | 3 | 3 | 109/200 | 116/200 | 109/116 | 48fcd30153df5e331fab43cfa514763db8ee3891:data/benchmark_expand_500/predictions2.jsonl |
| Claude Opus 5 thinking-high (expand-500, all 230) | n230 | 230 | 3 | 3 | 129/230 | 138/230 | 129/138 | 48fcd30153df5e331fab43cfa514763db8ee3891:data/benchmark_expand_500/predictions2.jsonl |
| Claude Opus family (locked headline, self-rank) | n500 | 500 | 3 | 3 | 227/500 | 249/500 | 227/249 | main raw + v3 + v2_ctrl + expand 106 + expand-500 200-cut |
| Claude Fable (partial +106) | n68 | 68 | 3 | 3 | 56/68 | 57/68 | 56/57 | 473030fb9d046548ff1ad06d04d20915fc2943d2:data/benchmark_expand/raw_fable/ |
| trained SELFIES generator (4-config ensemble) | n248 | 248 | 40 | 40 |  | 94/248 |  | contrib/generator_probe/artifacts/gen_candidates.jsonl |

## Prefixes that were actually stored

A prefix row exists only for k = 1 … max unique constitutions in that deposit. k = 10, 20, and 50 were not written for these old logs. The longest stored LLM pool is the original-then-generate-wide union, max unique 9, and only one of 60 lists reaches 9. Copying 25/60 into a k = 10, 20, or 50 column would invent the curve. The trained generator file is sorted canonical SMILES (248 keys, unordered full-pool recall 94/248). That recall is not formula-filtered and is not a ranked prefix, so it has no k row.

Rows with k ≥ 4, which the ≤3 protocol did not score. `n_lists_ge_k` is how many lists actually contain at least k unique constitutions. Shorter lists contribute the list they have. Forward-verify is blank where no 13C prediction map was stored.

| model | subset | k | n | n_lists_ge_k | top1_self | recall | precision_given_recall | top1_forward_verify |
|---|---|---|---|---|---|---|---|---|
| Claude Opus generate-wide | n60 | 4 | 60 | 35 | 13/60 | 24/60 | 13/24 | 18/60 |
| Claude Opus generate-wide | n60 | 5 | 60 | 25 | 13/60 | 24/60 | 13/24 | 18/60 |
| Claude Opus generate-wide | n60 | 6 | 60 | 9 | 13/60 | 24/60 | 13/24 | 18/60 |
| Claude Opus original then generate-wide | n60 | 4 | 60 | 46 | 14/60 | 22/60 | 14/22 | 17/60 |
| Claude Opus original then generate-wide | n60 | 5 | 60 | 40 | 14/60 | 24/60 | 14/24 | 18/60 |
| Claude Opus original then generate-wide | n60 | 6 | 60 | 28 | 14/60 | 25/60 | 14/25 | 18/60 |
| Claude Opus original then generate-wide | n60 | 7 | 60 | 20 | 14/60 | 25/60 | 14/25 | 18/60 |
| Claude Opus original then generate-wide | n60 | 8 | 60 | 6 | 14/60 | 25/60 | 14/25 | 18/60 |
| Claude Opus original then generate-wide | n60 | 9 | 60 | 1 | 14/60 | 25/60 | 14/25 | 18/60 |
| Claude Sonnet generate-wide | n12 | 4 | 12 | 5 | 2/12 | 4/12 | 2/4 |  |
| Claude Sonnet generate-wide | n12 | 5 | 12 | 2 | 2/12 | 4/12 | 2/4 |  |

On the original-then-wide pool, forward-verify top-1 is 18/60 at k = 3, 17/60 at k = 4, and 18/60 from k = 5 through k = 9. Recall reaches 25/60 at k = 6 and stays 25/60 through k = 9, with `n_lists_ge_k` falling from 28 to 1. That plateau is the measured prefix of lists that end, not a filled-in k = 10.

## New arm: nested n = 60, requested k = 10

Finished 60/60. File: `predictions/cursor_n60_k10.jsonl`. Raw replies, unmodified, are in `raw_replies/n60/`. Empty lists, kept in the denominator: `benchmark_v3:R33`. Rank-1 formula match on the raw first string is 58/60. Rank-1 parseable is 59/60.

Unique-constitution prefixes. This is the curve to cite for this arm.

| k | n | n_lists_ge_k | top1 | recall | precision_given_recall |
|---|---|---|---|---|---|
| 1 | 60 | 59 | 28/60 | 28/60 | 28/28 |
| 2 | 60 | 52 | 28/60 | 33/60 | 28/33 |
| 3 | 60 | 45 | 28/60 | 36/60 | 28/36 |
| 4 | 60 | 35 | 28/60 | 36/60 | 28/36 |
| 5 | 60 | 30 | 28/60 | 36/60 | 28/36 |
| 6 | 60 | 26 | 28/60 | 37/60 | 28/37 |
| 7 | 60 | 20 | 28/60 | 37/60 | 28/37 |
| 8 | 60 | 18 | 28/60 | 37/60 | 28/37 |
| 9 | 60 | 10 | 28/60 | 37/60 | 28/37 |
| 10 | 60 | 6 | 28/60 | 37/60 | 28/37 |

At the reviewers' marks: k = 3 is top-1 28/60, recall 36/60, precision given recall 28/36, n_lists_ge_k 45/60. k = 5 is top-1 28/60, recall 36/60, precision given recall 28/36, n_lists_ge_k 30/60. k = 10 is top-1 28/60, recall 37/60, precision given recall 28/37, n_lists_ge_k 6/60. k = 20 and k = 50 were not requested in this arm, and no row is filled for them.

k = 1 is 28/60 top-1, which equals recall because a one-constitution prefix cannot be misranked. From k = 6 through k = 10, unique recall stays 37/60. That is a measured plateau: n_lists_ge_k falls from 26 at k = 6 to 6 at k = 10, and the extra stored slots did not add a hit. It is not a copy of a shorter budget into an unasked column.

Raw-slot prefixes are in the same CSV (`list_kind=raw_slots`). They match the unique curve except at k = 2, where raw recall is 32/60 and unique recall is 33/60. Dropping an unparseable or duplicate string moves one true constitution into the length-2 prefix. Both rows are stored.

These 60 are the vendor-comparison arm (`benchmark_v3` 40 plus `benchmark_v2_ctrl` 20), nested inside the locked 500. They are not a new 500-wide headline. Claude's own lists on this same 60 remain 14/60 top-1 and 19/60 recall at the stored ≤3 budget.

## New arm: n = 500 roster, requested k = 10, partial

Finished items in `predictions/cursor_n500_k10.jsonl`: 222. Denominator is 222, the finished count. The other roster items are not scored and are not counted as misses. This is not a 500-wide rate.

The nested 60 are not repeated in that file and were not re-solved. Batches 01–37 of the n=500 prompt manifest are disjoint from those 60 and contain 222 compounds. All 37 replies were present at scoring time, so this file is that whole disjoint block, not a sample inside it. From batch 38 that manifest overlaps the nested 60, so those prompts were not relaunched. This denominator stays 222. The non-nested simple items are scored in their own file and are not written into these fractions.

Empty lists inside this partial file, kept in its denominator: `benchmark_expand:R102`, `benchmark_expand:R97`, `benchmark_main:R112`, `benchmark_main:R124`.

Longest stored list among the finished 222 is 10. At k = 10, top-1 is 53/222, recall is 72/222, precision given recall is 53/72, and n_lists_ge_k is 10/222. Lists shorter than 10 contribute the constitutions they have. k = 20 and k = 50 are not filled from this ask.

| k | n | n_lists_ge_k | top1 | recall | precision_given_recall |
|---|---|---|---|---|---|
| 1 | 222 | 218 | 53/222 | 53/222 | 53/53 |
| 2 | 222 | 208 | 53/222 | 61/222 | 53/61 |
| 3 | 222 | 187 | 53/222 | 65/222 | 53/65 |
| 4 | 222 | 159 | 53/222 | 69/222 | 53/69 |
| 5 | 222 | 137 | 53/222 | 71/222 | 53/71 |
| 6 | 222 | 111 | 53/222 | 71/222 | 53/71 |
| 7 | 222 | 73 | 53/222 | 71/222 | 53/71 |
| 8 | 222 | 55 | 53/222 | 71/222 | 53/71 |
| 9 | 222 | 20 | 53/222 | 72/222 | 53/72 |
| 10 | 222 | 10 | 53/222 | 72/222 | 53/72 |

## New arm: non-nested simple n = 218, requested k = 10

Finished 218/218. File: `predictions/cursor_n218_k10.jsonl`. Raw replies are in `raw_replies/n218/`. This block is every simple item in the n=500 roster outside the nested 60 (248 simple − 30 nested simple). `composition_n218.json` records n=218, n_simple=218, overlap with the nested 60 = 0, overlap with the finished complex file = 0, union of the three files = 500. The block is contiguous in the difficulty-then-qid roster, indices 252 through 469. Cohorts: `benchmark_expand` 53, `benchmark_expand_500` 97, `benchmark_main` 68. The nested 60 and the 222 were not re-solved.

Empty lists, kept in the denominator: none. Rank-1 formula match on the raw first string is 218/218. Rank-1 parseable is 218/218.

Unique-constitution prefixes. This is the curve to cite for this arm. Shorter lists contribute the constitutions they have. k = 20 and k = 50 were not requested.

| k | n | n_lists_ge_k | top1 | recall | precision_given_recall |
|---|---|---|---|---|---|
| 1 | 218 | 218 | 154/218 | 154/218 | 154/154 |
| 2 | 218 | 136 | 154/218 | 170/218 | 154/170 |
| 3 | 218 | 84 | 154/218 | 173/218 | 154/173 |
| 4 | 218 | 54 | 154/218 | 173/218 | 154/173 |
| 5 | 218 | 38 | 154/218 | 173/218 | 154/173 |
| 6 | 218 | 24 | 154/218 | 174/218 | 154/174 |
| 7 | 218 | 9 | 154/218 | 174/218 | 154/174 |
| 8 | 218 | 4 | 154/218 | 174/218 | 154/174 |
| 9 | 218 | 1 | 154/218 | 174/218 | 154/174 |
| 10 | 218 | 0 | 154/218 | 174/218 | 154/174 |

At k = 10, top-1 is 154/218, recall is 174/218, precision given recall is 154/174, and n_lists_ge_k is 0/218.
No returned list contains 10 unique constitutions, so n_lists_ge_k at k = 10 is 0. The k = 10 prefix is the stored list. No SMILES was added to fill a tenth slot.

## Post-hoc sum of three complementary finished files

Label: post-hoc sum of three complementary finished files of `grok-4.7-high-fast` under the same closed-book k=10 protocol. The files are the nested n=60 arm, the non-nested complex n=222 arm, and this non-nested simple n=218 arm. Their qids are disjoint and their union has 500 items. This is not a single 500-item run. No partial rate is scaled to 500. The locked Claude headline remains the deposited self-rank 227/500 top-1 and 249/500 recall at stored lists of maximum length 3.

| k | n | n_lists_ge_k | top1 | recall | precision_given_recall |
|---|---|---|---|---|---|
| 1 | 500 | 495 | 235/500 | 235/500 | 235/235 |
| 2 | 500 | 396 | 235/500 | 264/500 | 235/264 |
| 3 | 500 | 316 | 235/500 | 274/500 | 235/274 |
| 4 | 500 | 248 | 235/500 | 278/500 | 235/278 |
| 5 | 500 | 205 | 235/500 | 280/500 | 235/280 |
| 6 | 500 | 161 | 235/500 | 282/500 | 235/282 |
| 7 | 500 | 102 | 235/500 | 282/500 | 235/282 |
| 8 | 500 | 77 | 235/500 | 282/500 | 235/282 |
| 9 | 500 | 31 | 235/500 | 283/500 | 235/283 |
| 10 | 500 | 16 | 235/500 | 283/500 | 235/283 |

## Closed-book caveat

Each solver was instructed to read only its batch markdown, to skip the web, the repository, gold files, isomer databases, and NMR-Solver, and to use RDKit only after a proposal, to check that the SMILES parses and matches the formula. The same limit is stated in `scripts/manual_collect.py`: the harness cannot prove a solver obeyed it. Predictions were written before scoring. Collected SMILES were not edited by hand. `cursor_n60_k10.jsonl` matches `raw_replies/n60/` after whitespace stripping, 0 mismatches. `cursor_n218_k10.jsonl` matches `raw_replies/n218/` after whitespace stripping, 0 mismatches. The only metadata change after collection was the model string, set to `grok-4.7-high-fast`.

Prompt leak scan on the 218 exported prompts (`leak_scan_n218.json`): InChIKey pattern matches 0, gold SMILES token matches 0, gold InChIKey matches 0, gold InChIKey-14 matches 0, banned-token counts {"true_smiles": 0, "inchikey": 0, "is_true": 0, "answers2": 0}. The prompt template uses the word SMILES as the requested output format. `export` does not open an answer file. Re-export of the existing n=60 and n=500 batch 01 prompts reproduced the deposited sha256 values in `renderer_check.json`.

## What is still unidentified

- k = 20 and k = 50, on this model and on the deposited Claude lists. Not requested on this arm, and not stored in the old logs.
- A single 500-item Cursor run. The post-hoc table is the sum of three finished files. The 222 file is not scaled to 500.
- Forward-verify of the new Cursor lists. No blind 13C prediction pass was run, so precision given recall here is self-rank, not chamfer.

