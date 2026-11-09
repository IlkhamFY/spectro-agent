# Ask-for-50 on the lists that returned

Solver: `claude-opus-5-5-high` (Claude Opus 5.5, high thinking). One fresh context per batch of six compounds. The prompt is the ask-for-ten peak-list prompt with the requested budget set to 50 distinct constitutions, best first. Fewer are allowed. Padding is not allowed. Fields in the prompt are the compound id, molecular formula, IR band list, and printed 1H and 13C lists. Gold SMILES and InChIKey are not features. The leak check on the nested prompts passed before solving: 60 keys and 60 SMILES scanned, 0 hits.

Scoring uses InChIKey connectivity (first 14 characters). A constitution is the first formula-matching SMILES of each key, in the order the model wrote it. A shorter list contributes the constitutions it has. Empty lists stay in the denominator. This file has no empty lists (`0/54`). The same fractions were recomputed from the raw strings against the frozen answer keys, and again against the CASE-lite `gold_ik` column. The two key tables agree on all 54 finished rows, and the independent rescore matches the summary. The locked k≤3 deposits were not edited.

## What was scored

Returned nested batches: 01, 02, 03, 04, 06, 07, 08, 09, 10. That is 54 lists. Batch 05 did not return (6 compounds). It was not replaced and those compounds are not in the denominator. `simple60` and `rest380` were not solved. Every rate below uses 54.

## Prefixes

Own-order top-1 is the first unique constitution. Generation misses are lists whose prefix does not contain the gold key. `n_lists_ge_k` is how many of the 54 lists have at least k distinct constitutions.

| k | recall | top-1 | generation misses | n_lists with length ≥ k |
|---:|---:|---:|---:|---:|
| 1 | 45/54 | 45/54 | 9/54 | 54/54 |
| 3 | 47/54 | 45/54 | 7/54 | 53/54 |
| 5 | 48/54 | 45/54 | 6/54 | 53/54 |
| 10 | 48/54 | 45/54 | 6/54 | 33/54 |
| 20 | 49/54 | 45/54 | 5/54 | 6/54 |
| 50 | 49/54 | 45/54 | 5/54 | 0/54 |

## Lengths

Mean length 663/54 (12.2778). Median 12. Maximum 28. Lists that reach 20: 6/54. Lists that reach 50: 0/54. Lists longer than the request: 0/54.

Recall moves from 45/54 at k=1 to 47/54 at k=3 to 48/54 at k=5, and it stays 48/54 at k=10. It still moves after k=10: k=20 is 49/54, one more hit than k=10 (delta 1/54). It does not move after k=20 (49/54 at k=20 and at k=50, delta 0/54). It does not move after k=50: the request stops at 50, and the longest returned list has length 28.

## Files

- `predictions/claude-opus-5-5-high_nested_returned_k50.jsonl`
- `summary_nested_returned.json`
- `summary_nested_returned.csv`
- `replies/nested_returned/`
