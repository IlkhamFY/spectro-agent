# Ask-for-50 on the lists that returned

Solver: `claude-opus-5-5-high` (Claude Opus 5.5, high thinking). One fresh context per batch of six compounds. The prompt is the ask-for-ten peak-list prompt with the requested budget set to 50 distinct constitutions, best first. Fewer are allowed. Padding is not allowed. Fields in the prompt are the compound id, molecular formula, IR band list, and printed 1H and 13C lists. Gold SMILES and InChIKey are not features. The leak check on the nested prompts passed before solving: 60 keys and 60 SMILES scanned, 0 hits.

Scoring uses InChIKey connectivity (first 14 characters). A constitution is the first formula-matching SMILES of each key, in the order the model wrote it. A shorter list contributes the constitutions it has. Empty lists stay in the denominator. This file has no empty lists (`0/48`). The same fractions were recomputed from the raw strings against the frozen answer keys, and again against the CASE-lite `gold_ik` column. The two key tables agree on all 48 finished rows, and the independent rescore matches the summary. The locked k≤3 deposits were not edited.

## What was scored

Returned nested batches: 02, 03, 04, 06, 07, 08, 09, 10. That is 48 lists. Batches 01 and 05 did not return (12 compounds). They were not replaced and they are not in the denominator. `simple60` and `rest380` were not solved. Every rate below uses 48.

## Prefixes

Own-order top-1 is the first unique constitution. Generation misses are lists whose prefix does not contain the gold key. `n_lists_ge_k` is how many of the 48 lists have at least k distinct constitutions.

| k | recall | top-1 | generation misses | n_lists with length ≥ k |
|---:|---:|---:|---:|---:|
| 1 | 42/48 | 42/48 | 6/48 | 48/48 |
| 3 | 44/48 | 42/48 | 4/48 | 48/48 |
| 5 | 45/48 | 42/48 | 3/48 | 48/48 |
| 10 | 45/48 | 42/48 | 3/48 | 30/48 |
| 20 | 45/48 | 42/48 | 3/48 | 4/48 |
| 50 | 45/48 | 42/48 | 3/48 | 0/48 |

## Lengths

Mean length 575/48 (11.9792). Median 12. Maximum 26. Lists that reach 20: 4/48. Lists that reach 50: 0/48. Lists longer than the request: 0/48.

Recall moves from 42/48 at k=1 to 44/48 at k=3 to 45/48 at k=5. It does not move after k=10 (45/48 at k=10 and at k=20, delta 0/48). It does not move after k=20 (45/48 at k=20 and at k=50, delta 0/48). It does not move after k=50: the request stops at 50, and the longest returned list has length 26.

## Files

- `predictions/claude-opus-5-5-high_nested_returned_k50.jsonl`
- `summary_nested_returned.json`
- `summary_nested_returned.csv`
- `replies/nested_returned/`
