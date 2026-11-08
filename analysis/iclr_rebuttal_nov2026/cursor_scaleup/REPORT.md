# Closed-book candidate budget: claude-opus-5-5-high

This deposit is a second Cursor-subagent elucidator for the ICLR 2027 IRSpectra-Bench rebuttal. It does not replace the locked Claude headline on the full 500 (top-1 227/500, recall 249/500, self-rank precision|recall 227/249). Those integers are not recomputed here and no file that holds them is edited. The grok-4.7-high-fast arm is a different model and is not re-run. This branch does not contain that arm's prediction files.

## Model and request

Solver model id, recorded in every deposit filename: `claude-opus-5-5-high`.

It is a Claude-family Cursor subagent, the closest available analogue of the paper's Claude Opus system. It is not `grok-4.7-high-fast`. No personal Anthropic or OpenAI key was called. NMR-Solver was not downloaded.

Requested budget: up to 10 distinct constitutions, best first. The prompt says to return fewer when fewer can be defended, and not to pad. A requested-k=20 arm was not run. No list came back longer than the request: on both finished sets the longest unique-constitution list has length 9, and `n_longer_than_requested` is 0. k=50 was not run. Rows for k=10, 20, and 50 are written with `identified = false` and blank rates. The k=9 rate is not copied into them.

Generation conditions held fixed inside each arm: one fresh subagent per batch, six compounds per batch, the same prompt text, requested k=10. Prefixes are cuts of that single list. They are not separate generations at each k.

## What the solver was given

Each solver context was instructed to read only its batch markdown file. The file contains the compound id, molecular formula, IR band list, printed 1H list, and printed 13C list. It does not contain a name, a SMILES, an InChI, an InChIKey, or a DOI. RDKit was allowed only after a candidate had been written, and only to test that the SMILES parses and matches the formula. Failures are dropped and do not occupy a rank. RDKit was not used to generate structures.

Identity is the InChIKey connectivity block from `scripts/specmetrics.ik14` (first 14 characters). Unique-constitution prefixes keep the first SMILES of each block, in the order the model wrote them. A repeated constitution is one slot, not two.

The scorer was checked against the deposited ≤3 lists on the nested 60. It returns self-rank top-1 14/60 and recall 19/60, which is the published original-pool endpoint.

## Closed-book caveat

The harness cannot prove that a subagent never used a structure it already knew, and it cannot see unlogged reasoning. What was checked is narrower.

- `closed_book.py check` scans every solver prompt for gold InChIKeys and gold SMILES after the prompts are written. Both arms passed: 60 keys and 60 smiles scanned, 0 InChIKey-pattern hits, 0 key leaks, 0 SMILES leaks (`checks_claude-opus-5-5-high_n60.json`, `checks_claude-opus-5-5-high_n500.json`).
- Tool logs for all 10 nested-60 contexts and all 10 continuation contexts show one read, of the assigned `/tmp` batch file, plus an RDKit parse-and-formula check. No answer file, repository search, or web retrieval was recorded in those logs.

That is an audit of recorded tool calls and of the prompt text. It is not a proof that the model answered from the spectrum alone.

## Nested n=60

Roster: all 40 `benchmark_v3` questions and all 20 `benchmark_v2_ctrl` questions. This is the 60-compound vendor / generate-wide arm. Finished: 60. Empty lists: 0. Every returned string parsed and matched the formula (333 strings, 333 unique constitutions). No list reached length 10.

Unique-constitution prefixes. `n` is the finished count. `n_lists_ge_k` is how many of those lists have at least k distinct constitutions. Top-1 is the gold key in position 0. Recall is the gold key anywhere in the prefix. Precision|recall is top-1 divided by recall.

| k | n | n_lists_ge_k | top-1 | recall | precision\|recall | identified |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 60 | 60 | 43/60 | 43/60 | 43/43 | yes |
| 2 | 60 | 59 | 43/60 | 45/60 | 43/45 | yes |
| 3 | 60 | 58 | 43/60 | 47/60 | 43/47 | yes |
| 4 | 60 | 55 | 43/60 | 47/60 | 43/47 | yes |
| 5 | 60 | 42 | 43/60 | 47/60 | 43/47 | yes |
| 6 | 60 | 33 | 43/60 | 47/60 | 43/47 | yes |
| 7 | 60 | 15 | 43/60 | 47/60 | 43/47 | yes |
| 8 | 60 | 9 | 43/60 | 47/60 | 43/47 | yes |
| 9 | 60 | 2 | 43/60 | 47/60 | 43/47 | yes |
| 10 | 60 | 0 |  |  |  | no |
| 20 | 60 | 0 |  |  |  | no |
| 50 | 60 | 0 |  |  |  | no |

Unique-length histogram: 1 (1 list), 2 (1), 3 (3), 4 (13), 5 (9), 6 (18), 7 (6), 8 (7), 9 (2). Recall moves from 43/60 at k=1 to 45/60 at k=2 to 47/60 at k=3, and it stays 47/60 through the longest stored prefix. Top-1 stays 43/60. Extra slots past the third constitution did not add a gold key on this set.

## Continuation into the n=500 roster

Finished items: 60. Denominator: 60. The other 440 roster items were not run and are not counted as misses.

Selection, also in `selection_claude-opus-5-5-high_n500.json`: after removing the nested 60, and after leaving full-roster positions 1–132 to the grok arm (batches 01–22, already dispatched when this slice was chosen), this arm solved the last 60 remaining non-nested items. Those are full-roster indices 410–469, every one `benchmark_main`, from `benchmark_main:R11` through `benchmark_main:R99`.

Empty lists: 0. Returned strings: 294. Formula matches: 294. Unique constitutions: 293. The difference of 1 is a repeated constitution, not a formula failure. No raw list had length 10. Longest unique list: 9.

| k | n | n_lists_ge_k | top-1 | recall | precision\|recall | identified |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 60 | 60 | 53/60 | 53/60 | 53/53 | yes |
| 2 | 60 | 60 | 53/60 | 55/60 | 53/55 | yes |
| 3 | 60 | 57 | 53/60 | 55/60 | 53/55 | yes |
| 4 | 60 | 49 | 53/60 | 55/60 | 53/55 | yes |
| 5 | 60 | 33 | 53/60 | 55/60 | 53/55 | yes |
| 6 | 60 | 20 | 53/60 | 55/60 | 53/55 | yes |
| 7 | 60 | 8 | 53/60 | 55/60 | 53/55 | yes |
| 8 | 60 | 4 | 53/60 | 55/60 | 53/55 | yes |
| 9 | 60 | 2 | 53/60 | 55/60 | 53/55 | yes |
| 10 | 60 | 0 |  |  |  | no |
| 20 | 60 | 0 |  |  |  | no |
| 50 | 60 | 0 |  |  |  | no |

Unique-length histogram: 2 (3 lists), 3 (8), 4 (16), 5 (13), 6 (12), 7 (4), 8 (2), 9 (2).

On these same 60 compounds, the deposited Opus lists (stored length at most 3, scored with the same InChIKey-14 rule) are top-1 31/60 and recall 33/60. The new lists are a different model under a request for 10, not a rescoring of those deposits. The 53/60 figure is the new top-1. It is not a 53/500 figure.

## Files

- `predictions/cursor_claude-opus-5-5-high_n60_k10.jsonl`
- `predictions/cursor_claude-opus-5-5-high_n500_k10.jsonl`
- `scores_claude-opus-5-5-high_n60.csv`
- `scores_claude-opus-5-5-high_n500.csv`
- `lengths_claude-opus-5-5-high_n60.json`
- `lengths_claude-opus-5-5-high_n500.json`
- `checks_claude-opus-5-5-high_n60.json`
- `checks_claude-opus-5-5-high_n500.json`
- `prompts/claude-opus-5-5-high/` (the batch files the solvers were given)
- `replies/claude-opus-5-5-high/` (raw JSON before the formula filter)
- `closed_book.py` (`export`, `check`, `collect`, `score`, `selftest`)

`python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/closed_book.py selftest` passed. It checks deduplication, prefix arithmetic, and rejection of an InChIKey inside a prompt.

## Leftover of the locked n=500 roster

This section is a later run. It does not replace the nested n=60 table or the 60-item continuation table above, and it does not replace the locked Claude headline (top-1 227/500, recall 249/500, self-rank precision|recall 227/249). The denominator below is 380. It is not a 500-wide rate, and it is not a rescaling of 53/60.

### Which 380

`closed_book.py roster('n500')` is 500 questions. The nested n=60 is inside that roster: all 40 `benchmark_v3` and all 20 `benchmark_v2_ctrl`, in two blocks, 1-based positions 223–252 and 471–500. The two sets are disjoint from each other.

The 60-item continuation already on disk is `predictions/cursor_claude-opus-5-5-high_n500_k10.jsonl`. Its qids are `benchmark_main:R11` through `benchmark_main:R99`. That file matches 1-based full-roster positions 411–470 (0-based slice `[410:470]`), which is also what the earlier manifest recorded: `exclude_arm=n60`, `skip=380`, `limit=60`. The prose in the previous section, and in `selection_claude-opus-5-5-high_n500.json`, says indices 410–469. That window is one position earlier. It would include `benchmark_main:R108` and exclude `benchmark_main:R99`. The deposited qids were not redone. `benchmark_main:R108` is in this leftover file. `benchmark_main:R99` stays in the earlier file.

After those two exclusions the leftover is 380, in 1-based positions 1–222 (222) and 253–410 (158). The same 380 is `export --arm n500 --exclude-arm n60 --skip 0 --limit 380`, because the deposited slice is the last 60 of the 440 non-nested items. Pairwise overlap of the three qid sets is 0. Their union is the 500. A sum of the three files would be a post-hoc sum of complementary files, and it would count each roster item once only under this qid definition. This report does not add those numerators.

### Composition

| difficulty | cohort | n |
|---|---|---:|
| complex | benchmark_expand | 53 |
| complex | benchmark_expand_500 | 103 |
| complex | benchmark_main | 66 |
| simple | benchmark_expand | 53 |
| simple | benchmark_expand_500 | 97 |
| simple | benchmark_main | 8 |
| complex | total | 222 |
| simple | total | 158 |

Cohort totals: `benchmark_expand_500` 200, `benchmark_expand` 106, `benchmark_main` 74. No `benchmark_v3` and no `benchmark_v2_ctrl`. The eight simple `benchmark_main` qids are R04, R10, R100, R101, R102, R106, R107, R108.

### Protocol

Same harness as the sections above (`closed_book.py` export, check, collect, score, lengths). Solver model id: `claude-opus-5-5-high`. Sixty-four fresh contexts, one per batch, six compounds except the last batch (two). Requested budget: up to 10 distinct constitutions, best first, no padding. Each context was told to read only its batch file and to use RDKit only to test a SMILES it had already written. This run does not have a recorded tool-call log for those 64 contexts, so it does not repeat the tool-log claim from the earlier sections.

Identity is `scripts/specmetrics.ik14`: `Chem.MolToInchiKey` truncated to 14 characters. Empty lists stay in the denominator. Prefixes are cuts of the single list. k=20 and k=50 were not run.

### Leak scan

`checks_claude-opus-5-5-high_n500_leftover.json`: 64 prompts, 380 qids, 380 gold keys, 380 gold SMILES, 0 InChIKey-pattern hits, 0 key leaks, 0 SMILES leaks. The check passed.

### Scores

Finished: 380. Empty lists: 3 (`benchmark_expand:R102`, `benchmark_expand_500:R121`, `benchmark_main:R124`). Returned strings: 1610. Parseable: 1610. Formula matches: 1610. Unique constitutions: 1598. The difference of 12 is repeated constitutions, not formula failures. No list is longer than the request. Three lists have 10 unique constitutions, so the k=10 row is identified. An independent recount of the same prediction file with `ik14` and `prefix_counts` reproduced the table.

| k | n | n_lists_ge_k | top-1 | recall | precision\|recall | identified |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 380 | 377 | 257/380 | 257/380 | 257/257 | yes |
| 2 | 380 | 359 | 257/380 | 272/380 | 257/272 | yes |
| 3 | 380 | 315 | 257/380 | 275/380 | 257/275 | yes |
| 4 | 380 | 239 | 257/380 | 280/380 | 257/280 | yes |
| 5 | 380 | 142 | 257/380 | 280/380 | 257/280 | yes |
| 6 | 380 | 97 | 257/380 | 284/380 | 257/284 | yes |
| 7 | 380 | 48 | 257/380 | 284/380 | 257/284 | yes |
| 8 | 380 | 13 | 257/380 | 284/380 | 257/284 | yes |
| 9 | 380 | 5 | 257/380 | 284/380 | 257/284 | yes |
| 10 | 380 | 3 | 257/380 | 285/380 | 257/285 | yes |
| 20 | 380 | 0 |  |  |  | no |
| 50 | 380 | 0 |  |  |  | no |

Unique-length histogram: 0 (3 lists), 1 (18), 2 (44), 3 (76), 4 (97), 5 (45), 6 (49), 7 (35), 8 (8), 9 (2), 10 (3). Top-1 stays 257/380. Recall moves from 257/380 at k=1 to 285/380 at k=10. The raw-unique table, which keeps a wrong-formula constitution if one had parsed, is identical at every k, which matches the formula-match count of 1610/1610.

### Files added for this leftover run

- `predictions/cursor_claude-opus-5-5-high_n500_leftover_k10.jsonl`
- `scores_claude-opus-5-5-high_n500_leftover.csv`
- `lengths_claude-opus-5-5-high_n500_leftover.json`
- `checks_claude-opus-5-5-high_n500_leftover.json`
- `selection_claude-opus-5-5-high_n500_leftover.json`
- `prompts/claude-opus-5-5-high/n500_k10_leftover/`
- `replies/claude-opus-5-5-high/n500_k10_leftover/`
