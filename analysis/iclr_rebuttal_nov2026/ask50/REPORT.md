# Ask-for-50 on the nested 60

Solver: `claude-opus-5-5-high` (Claude Opus 5.5, high thinking). One fresh context per batch of six compounds. The prompt is the ask-for-ten peak-list prompt with the requested budget set to 50 distinct constitutions, best first. Fewer are allowed. Padding is not allowed. Fields in the prompt are the compound id, molecular formula, IR band list, and printed 1H and 13C lists. Gold SMILES and InChIKey are not features. The leak check on the nested prompts passed before solving: 60 keys and 60 SMILES scanned, 0 hits.

Scoring uses InChIKey connectivity (first 14 characters). A constitution is the first formula-matching SMILES of each key, in the order the model wrote it. A shorter list contributes the constitutions it has. Empty lists stay in the denominator. This file has no empty lists (`0/60`). The same fractions were recomputed from the raw strings against the frozen answer keys, and again against the CASE-lite `gold_ik` column. The two key tables agree on all 60 rows, and the independent rescore matches the summary. The locked k≤3 deposits were not edited.

## What was scored

All 10 nested batches, 01 through 10. These 60 lists are the v3 + v2_ctrl nest, 1-based roster positions 223–252 and 471–500. The finished qids match that set. `simple60` and `rest380` were not solved. Every rate below uses 60.

## Prefixes

Own-order top-1 is the first unique constitution. Generation misses are lists whose prefix does not contain the gold key. `n_lists_ge_k` is how many of the 60 lists have at least k distinct constitutions.

| k | recall | top-1 | generation misses | n_lists with length ≥ k |
|---:|---:|---:|---:|---:|
| 1 | 48/60 | 48/60 | 12/60 | 60/60 |
| 3 | 51/60 | 48/60 | 9/60 | 57/60 |
| 5 | 52/60 | 48/60 | 8/60 | 57/60 |
| 10 | 52/60 | 48/60 | 8/60 | 36/60 |
| 20 | 53/60 | 48/60 | 7/60 | 6/60 |
| 50 | 53/60 | 48/60 | 7/60 | 0/60 |

## Lengths

Mean length 707/60 (11.7833). Median 12. Maximum 28. Lists that reach 20: 6/60. Lists that reach 50: 0/60. Lists longer than the request: 0/60.

Recall moves from 48/60 at k=1 to 51/60 at k=3 to 52/60 at k=5, and it stays 52/60 at k=10. It still moves after k=10: k=20 is 53/60, one more hit than k=10 (delta 1/60). It does not move after k=20 (53/60 at k=20 and at k=50, delta 0/60). It does not move after k=50: the request stops at 50, and the longest returned list has length 28.

## Files

- `predictions/claude-opus-5-5-high_nested60_k50.jsonl`
- `summary_nested60.json`
- `summary_nested60.csv`
- `replies/nested_returned/`
