# IRSpectra-Bench: how the 500-item roster was built, and the protocol behind 227/500

Account for ICLR 2027 submission #48823 (OpenReview `k3ANnHd50t`). This note is analysis. It does not edit `docs/iclr/iclr_paper.tex` or the public manuscript. No model API was called. Generation scores below were recomputed from deposited SMILES.

The public PDF is `main.tex` in [IlkhamFY/IRSpectra-Bench](https://github.com/IlkhamFY/IRSpectra-Bench) (tip inspected: `ce5ec8b`, 2026-09-25). The deposits that produce the headline are **not** on `spectro-agent` `main` (`1a5a312`, 2026-09-10). They are on unmerged branches. A reader of `main` alone cannot rebuild the 500.

## Locked headline

These integers are the generation scores, and they reproduce.

| quantity | integer | percent | where it is defined |
|---|---:|---:|---|
| top-1 | **227/500** | **45.4%** | `data/benchmark_expand_500/HEADLINE_n500_2026-09-20.md` at `48fcd30` |
| recall @ ≤3 | **249/500** | **49.8%** | same file |
| self-rank precision \| recall | **227/249** | **91.2%** | `227/249 = 0.9116…` rounds to 91.2% |

Identity, exact rather than rounded: `227/500 = (249/500) × (227/249)`.

Addition, from the same file: locked 194 contributes 55 and 65, the full +106 contributes 63 and 68, the 200-cut contributes 109 and 116. `55+63+109 = 227` and `65+68+116 = 249`.

This note rescored the deposited candidate lists with RDKit InChIKey connectivity (first 14 characters) after a unique `(formula, IR band tuple, ¹³C)` join to `data/irexp_resolved/irexp_resolved.jsonl.gz`. The join is the one in `analysis/rebuttal_pack/cohort.py` (`_match`) on `d0fa2e6`. Result: **500/500 unique gold hits, 0 ambiguous**, and for every locked-194 item the join InChIKey-14 matched the committed answer key. Slice scores matched the lock exactly:

| slice | top-1 | recall |
|---|---|---|
| locked 194 | 55/194 | 65/194 |
| +106, all deposited | 63/106 | 68/106 |
| expand-500, first 200 validate-clean | 109/200 | 116/200 |
| **headline** | **227/500** | **249/500** |
| expand-500, all 230 | 129/230 | 138/230 |
| expand-500, validate-clean 224 | 127/224 | 135/224 |
| leftover clean 24 (R76–R99) | 18/24 | 19/24 |

The headline is not wrong. Do not replace it with `243/519` or `245/524`. Those are different cohorts (section 2.6).

The live OpenReview TL;DR that says frontier models hit **49.8% top-1** swaps the two rates. 49.8% is recall. Top-1 is 45.4%. Precision given recall is 91.2%.

`analysis/rebuttal_pack/REPORT.md` (`d0fa2e6`, branch `cursor/rebuttal-analysis-pack-783b`) puts a Wilson interval on the same lock: top-1 45.4% (227/500; 41.1 to 49.8), recall 49.8% (249/500; 45.4 to 54.2). Those intervals are compound-sampling intervals. Each compound was solved once.

## Where each piece is stored

| object | commit | branch | PR |
|---|---|---|---|
| Draw, questions, predictions, clean list, 200-cut, generation lock | `48fcd30153df5e331fab43cfa514763db8ee3891` | `cursor/expand-bench-500-b78b` | spectro-agent #41 (open) |
| Draw commit that first wrote `clean_qids.json` (224 ids), before any solve | `83e5744` (2026-09-16 19:04 UTC) | same branch | same |
| Night score of 224 and 230, paper still n=300, **no 200-cut yet** | `c6552b2` (2026-09-20 02:52 UTC) | same | same |
| 200-cut and the 227/500 table | `48fcd30` (2026-09-20 13:24 UTC) | same | same |
| Forward-verify wall 204/45/251 | `473030f` | `cursor/fverify-n500-unify-629c` | spectro-agent #68 (open) |
| Wilson intervals, paired tests | `d0fa2e6` | `cursor/rebuttal-analysis-pack-783b` | — |
| Public PDF and SI | `ce5ec8b` | `IRSpectra-Bench` `main` | — |

`answers2.jsonl` for both expansion rounds is withheld. Scoring reconstructs the key in memory. `docs/EXPANSION_PREREGISTRATION_500.md` forbids committing it while an arm is incomplete.

## 1. The sampler

Every expansion draw names `scripts/benchmark_v2.py`, function `sample2`. On the expansion branch that function is unchanged relative to `main`. The branch only adds a `--pred` flag to `score2` and teaches `scripts/validate_benchmark.py` to notice an expansion directory once `answers2.jsonl` is present.

`sample2(n, seed)` (`scripts/benchmark_v2.py`):

1. `random.seed(seed)`.
2. Exclude every InChIKey-14 already present in any `data/benchmark*/answers*.jsonl` other than the output directory.
3. Scan `data/irexp_resolved/irexp_resolved.jsonl.gz` in file order. Keep a record only if it has SMILES, ¹H, ¹³C, and an IR list; the SMILES parses; heavy-atom count is 8–60; and each NMR string contains at least three parenthesised entries. The first row for a given InChIKey-14 wins. Later duplicates in the gzip are dropped. That dedup is file order, not a random tie-break.
4. Assign difficulty with `difficulty(mol)` before any solver runs. **Complex** if the molecule has a spiro atom, a bridgehead atom, at least three rings, any fused ring, or more than 24 heavy atoms. **Simple** if it has at most two rings and at most 22 heavy atoms. Anything left (the 23–24 heavy-atom band without those ring features) is complex. The submitted PDF states the same simple rule (`main.tex`, Difficulty and scoring).
5. Shuffle each stratum. Walk the shuffled list and keep a record only when `raw_1h_for` recovers the source paper’s raw ¹H string from PMC-OA text and that string contains `"J"`. Take `n // 2` per stratum. This is a simple random sample of the J-recoverable pool, of size `n // 2` per stratum, at the given seed. It is not a sample of the larger eligible pool that lacks a recoverable J.
6. Shuffle the combined list and number questions `R01`, `R02`, … in that shuffled order (`f"R{i:02d}"`). Qid order is not difficulty order and, above `R99`, it is not integer order.

There is **no** cap on how many compounds come from one paper. There is **no** Tanimoto, Murcko, or scaffold filter at draw time. InChIKey-14 uniqueness is the only redundancy rule, and it runs before the shuffle.

The J-recoverable pool size is not tabulated. `docs/IRSPECTRA_BENCH_SIZE_AUDIT.md` (2026-08-31) counts **28,988** eligible quadruples with 8–60 heavy atoms and at least three parenthesised NMR entries, **before** the J-recovery filter. That audit’s eligible pool is 17.5% simple / 82.5% complex (`scripts/corpus_reweight.py`). The J filter is an additional screen.

## 2. The three pieces that sum to 500

The locked roster is **not** one draw of 500. It is three rounds glued together.

### 2.1 Locked 194

Documented in `docs/IRSPECTRA_BENCH_SIZE_AUDIT.md` and `docs/ESI.md` (Benchmark construction). `scripts/score_main.py` loads this union.

| round | directory | drawn | kept | role |
|---|---|---:|---:|---|
| Main | `data/benchmark_main/` | 140 | 134 | `clean_qids.json` after `scripts/validate_benchmark.py` |
| Controlled v3 | `data/benchmark_v3/` | 40 | 40 | kept whole; fixed before the spectral audit |
| Within-compound control | `data/benchmark_v2_ctrl/` | 20 | 20 | kept whole |

`134 + 40 + 20 = 194`. Strata on the 194: **98 simple / 96 complex**. Generation: **55/194 top-1, 65/194 recall**.

The six main-round exclusions (R03, R14, R65, R67, R82, R131) fail the integrity checks and have no solver entries in `data/benchmark_main/raw/`. Five have more parsed ¹³C peaks than carbons. R82 is too sparse (5 peaks for 22 symmetry-unique carbons). `validate_benchmark.py` flags a ground truth when any of these hold: parsed ¹³C count greater than the carbon count; parsed ¹³C count below `max(2, n_symmetry_unique_carbons // 2)`; RDKit formula disagrees with the question formula; SELFIES encode/decode does not round-trip. A ¹H integral above the structure’s hydrogen count is printed and **not** used as an exclusion.

**Seeds.** `docs/SUBMISSION.md` gap 4 and `docs/ESI.md` state that the sampling seed for the main round (140) and for controlled v3 (40) was **not recorded**. The released questions are fixed. They cannot be redrawn. Recorded seeds that are **not** part of the 500: pilot `scripts/benchmark_elucidation.py sample --n 21 --seed 7`; within-compound control `sample2 --n 20 --seed 23`; electrolyte `scripts/build_electrolyte_bench.py` seed 202 (held out of the headline). `data/seeds.yaml` is the IRexp harvest seed list. It is not a benchmark-draw seed.

Solver for this slice: consumer Claude, recorded in `docs/MODELS.md` as Claude Opus, with the display string **Claude Opus 4.8** evidenced only for the 2026-06-09 pilot. Collection window for the headline candidates: **2026-06-09 to 2026-06-11 UTC**. Thinking budget, temperature, `top_p`, `top_k`, `max_tokens`, and a generation seed were **not recorded** (`docs/SUBMISSION.md` gap 3; `docs/MODELS.md` §5). The submitted PDF later calls this slice “no-thinking” and calls the solver “Claude Opus 5”. The repository does not contain a snapshot id that ties the June 2026 deposits to the slug `claude-opus-5`.

Candidate lists on the 194: **423 SMILES across 194 items** (mean 2.180). On the 60-compound slice inside it (all of v3 and v2_ctrl), **132/60 = 2.20**, which is the mean quoted in the PDF.

### 2.2 The +106 round

Pre-registration, committed before the draw: `docs/EXPANSION_PREREGISTRATION.md` on the expansion branch (freeze commit named there as `3e35a3a`).

| parameter | value |
|---|---|
| directory | `data/benchmark_expand/` |
| command | `python scripts/benchmark_v2.py sample2 --n 106 --seed 2026` |
| strata | 53 simple, 53 complex (`n // 2`) |
| exclusion | every prior InChIKey-14, including the 194 |
| solver budget | up to 3 ranked SMILES |
| tools | RDKit formula and parse check only |

Deviations, appended under the freeze line rather than edited into it:

1. Export used `scripts/export_round.py` (key moved to a vault) rather than `scripts/manual_collect.py export`.
2. Some six-compound batches hit a **64,000 output-token** ceiling and were re-exported as halves of three (`scripts/split_batch.py`). Context size stays inside the 2–12 range already used on the 194.
3. After 2026-09-16, **remaining** Opus compounds were solved as single-compound Cursor Task agents with slug **`claude-opus-5-thinking-high`**. The provenance table still prints the family name `claude-opus-5`. R39 is explicitly one of these (`bc-0a25b5b0`, eighth launch). The file does **not** list how many of the 106 were in this thinking-high tail versus earlier Claude Code batches checked for the literal slug `claude-opus-5`.
4. The withheld key was reconstructed by unique `(formula, IR, ¹³C)` match (106/106 unique, 0 prior-round collisions) because the vault was empty on that machine. `answers2.jsonl` was not committed.

`scripts/validate_benchmark.py` on that key flagged **5/106** as ¹³C-overread: **R12, R22, R25, R82, R91**. Clean subset **101/106**. All-deposited generation: **63/106 top-1, 68/106 recall** (302 candidate SMILES, mean 2.849). Clean generation, from `docs/POOLED_HEADLINE_2026-09-16.md`: **61/101 and 65/101**.

The **headline 500 keeps all 106**, including the five flags. That is the opposite of the 2026-09-16 pooled headline, which was **n=295 = 194 + 101** and excluded those five (`docs/POOLED_HEADLINE_2026-09-16.md`: 116/295 top-1, 130/295 recall).

Fable (`claude-fable-5-1`) has 68/106 deposits in `raw_fable/`. It is not scored and not in the 500.

### 2.3 The expand-500 draw

Pre-registration: `docs/EXPANSION_PREREGISTRATION_500.md`, committed before the draw. Command, to be run only after that document:

```
python scripts/benchmark_v2.py sample2 --n 230 --seed 2026500 --outdir data/benchmark_expand_500
```

Strata requested: **115 simple / 115 complex**. The scored draw is 115/115 (`NIGHT_POOL_2026-09-20.md`, and this note’s rescore). The pre-registration’s target was “295 + validate-clean of these 230, aiming at ~500”, with 230 chosen so that a ~5% ¹³C-overread rate (5/106 on the previous round) would still leave about 218 clean items (`230 × 0.95 ≈ 218`, `295 + 218 ≈ 513`).

The draw commit `83e5744` (2026-09-16 19:04 UTC) wrote `questions2.jsonl` (230 lines) and `clean_qids.json` (224 ids). `git diff 83e5744 48fcd30 -- data/benchmark_expand_500/clean_qids.json` is empty. The six exclusions were frozen **before any solve**. They are labeled ¹³C-overread: **R26, R31, R102, R105, R107, R138**. The night of 2026-09-20 did **not** rerun `validate_benchmark.py`, because that would rewrite the committed snapshot (`NIGHT_POOL_2026-09-20.md`).

Solver, pre-registered for this round only: Claude Opus 5 as Cursor Task agents, slug **`claude-opus-5-thinking-high`**, one compound per agent, up to three SMILES, RDKit formula check only. `data/benchmark_expand_500/PROVENANCE.md` records `claude-opus-5` on every deposited single and says a deposit from any other model is refused. Deposits: 55/230 on 2026-09-16, then the rest on 2026-09-19 (`b756768`, 230/230). Every one of the 230 lists has **exactly 3** candidates (690 SMILES; the 200-cut is 600 of them).

Key reconstruction at scoring: 230/230 unique, 0 prior-round InChIKey-14 collisions (`HEADLINE_n500_2026-09-20.md`). This note’s join agrees: 230/230 unique.

Generation on the full draw: **129/230 top-1 (82/115 simple, 47/115 complex), 138/230 recall**. Validate-clean: **127/224 top-1 (81/110 simple, 46/114 complex), 135/224 recall**. The five simple and one complex flags account for `115−110` and `115−114`.

### 2.4 The rule that keeps 200 of 224

`HEADLINE_n500_2026-09-20.md` and the public copy `docs/HEADLINE_N500_2026-09-20.md`:

1. Start from `clean_qids.json` (224 ids). `validate_benchmark.py` writes that file with `json.dump(sorted(clean), …)`, so the file order is Python `sorted()` on the qid strings.
2. Take the first 200.
3. Write them to `headline500_expand200_qids.json`.

This note checked the file. `sorted(clean)[:200]` equals the committed 200-list, in order. First id **R01**, last id **R75**. The 24 clean ids left out are **R76–R99**. That is string order, not integer order. Integer order of the same 224 ids ends at **R206** and drops R207–R230. The lock is the string-order prefix. Qids `R100` and above sort **before** `R76` because `"R100" < "R76"`.

The 200-cut is **not** stratified. The parent draw is 115/115. The 224 clean items are 110/114. The kept 200 are **97 simple / 103 complex** (73/97 and 36/103 top-1). The dropped 24 are **13 simple / 11 complex**, and they are the easier tail: **18/24 top-1, 19/24 recall** (8/13 simple, 10/11 complex). Keeping them would move the pool from 227/500 (45.4%) to **245/524 (46.8%)** top-1 and **268/524 (51.1%)** recall. The cut does not inflate the headline. It lowers it, and it was chosen to land on the integer 500.

**Timing.** The pre-registration does not mention a 200-prefix. Its deviations log, as committed at `48fcd30`, is empty. The night-pool note at `c6552b2` (2026-09-20 02:52 UTC), written after `score2` had already produced 129/230 and 127/224, lists cohorts 300, 524, 519, 530, and 295. It does not list a 200-cut. The 200-cut appears ten hours later in `48fcd30`. The rule does not look at accuracy. It was recorded after the accuracy of the 224 was known, and it was not in the pre-registration. The PDF’s sentence that the 500 “is a pre-specified list, not an outcome-selected subset” (`main.tex`; `si/appendix_body.tex` §Stopping and pooling) is accurate for the 230-draw and for the six flags. It is not accurate, as written, for the decision to keep 200 of 224.

### 2.5 What 500 is, and what it is not

```
500 = 194 (main clean 134 + v3 40 + v2_ctrl 20)
    + 106 (every deposited Opus expansion item, including 5 flags)
    + 200 (string-sorted prefix of the 224 expand-500 clean ids)
```

Strata: **248 simple / 252 complex** (`98+53+97` and `96+53+103`). Top-1 161/248 and 66/252. Recall 172/248 and 77/252.

| cohort | composition | top-1 | recall | role |
|---|---|---|---|---|
| **500** | 194 + all 106 + 200 | **227/500 (45.4%)** | **249/500 (49.8%)** | locked generation headline |
| 300 | 194 + all 106 | 118/300 (39.3%) | 133/300 (44.3%) | former paper headline |
| 295 | 194 + clean 101 | 116/295 (39.3%) | 130/295 (44.1%) | validate-clean pool used for stereo, size bins, 26.5% reweight |
| 519 | 194 + clean 101 + clean 224 | 243/519 (46.8%) | 265/519 (51.1%) | what `scripts/score_pooled.py --expand --expand-500` prints |
| 524 | 194 + all 106 + clean 224 | 245/524 (46.8%) | 268/524 (51.1%) | sensitivity |
| 530 | 194 + all 106 + all 230 | 247/530 (46.6%) | 271/530 (51.1%) | sensitivity, includes 6 flags |

`scripts/score_main.py` still defines n=194. It was not retargeted.

InChIKey-14 overlap across the three slices of the 500 is **0**. The 500 constitutions are **500 distinct** connectivity keys.

### 2.6 Source papers and scaffolds

The sampler does not balance papers or scaffolds. Counts below were computed in this note from the same gold join (script `verify_locked_roster.py`). They are not in the PDF.

| check on the 500 | result |
|---|---|
| distinct `source_doi` | **405** papers for 500 compounds |
| papers that contribute more than one compound | **69** (164 compounds); 336 compounds are the only roster item from their paper |
| most compounds from one paper | **5** (PMC:5224347, PMC:3983340, PMC:9032987) |
| locked 194 | 167 papers, max 4 |
| +106 | 103 papers, max 2 |
| 200-cut | 184 papers, max 3 |
| distinct InChIKey-14 | **500/500** |
| Bemis–Murcko scaffolds | **342** distinct among 473 molecules with a non-empty scaffold; **27** acyclic (empty Murcko) |
| scaffolds shared by more than one compound | **44**; the largest is benzene (`c1ccccc1`), **74/500** |

Constitution is unique. Generic scaffolds are not. Benzene as a Murcko core is a property of monosubstituted and many simple aromatics, not 74 copies of one molecule. A scaffold hold-out was not applied, and the PDF says a Murcko split does not apply to a closed-book model that was not trained on this roster (`main.tex`, Scaffold splitting).

Licence pools on the joined rows: commercial 288, non-commercial 113, empty/unknown 99.

Heavy atoms on the 500, from the joined structures: minimum 8, median **21**, mean **22.75**, maximum 60. The size audit’s eligible-corpus median is **26** and its n=194 cohort median is about 20. The 500 sits toward the small side of that eligible pool. The J-recovery filter’s effect on the heavy-atom distribution is not separately tabulated.

### 2.7 What “validate-clean” means

It is a ground-truth integrity filter, applied to a round’s answer key, not a difficulty sample and not “the easy half of the 500.”

| round | filter applied to the headline 500? |
|---|---|
| Main 140 | yes, before solving: 134 kept, 6 never sent to the solver |
| v3 (40) and v2_ctrl (20) | **no**. Both rounds are inside the 194 whole. A strict alternative would be 191 (`docs/IRSPECTRA_BENCH_SIZE_AUDIT.md`: 134+39+18). The audit reports 57/60 of the controls pass |
| +106 | the filter exists (101 clean) and the **500 ignores it** |
| expand-500 | yes for membership in the 224; the 500 then keeps a string prefix of 200 |

The phrase “validate-clean subset” in the PDF (`main.tex` around the chemspace plate; `si/appendix_body.tex` §Validate-clean extras) points at **n=295 = 194 + 101**, not at a subset of the headline 500. On that 295 the SI reports full-InChIKey top-1 **93/295 (31.5%)**, corpus-reweighted top-1 **26.5% [21–32]**, recall **31.3% [25–37]**, size bins ≤15 / 16–25 / >25 of **53 / 152 / 90**, and scaffold-level recovery 64%. The paragraph in `main.tex` that states the n=500 generation result also quotes 26.5% [21–32], those size bins, and “137 analysable top-1 misses … 76.6% constitutional isomers.” Those last figures are the **n=194 / n=295** analyses (`docs/ESI.md`, `docs/POOLED_HEADLINE_2026-09-16.md`). They are not n=500 recomputations. The n=500 corpus-reweighted rate is **not in the repository**.

Using the frozen weights 17.5% simple / 82.5% complex on the locked n=500 stratum rates gives

`0.175 × (161/248) + 0.825 × (66/252) = 0.3297` (33.0% top-1)

`0.175 × (172/248) + 0.825 × (77/252) = 0.3735` (37.3% recall)

That arithmetic is computed in this note. It is not a number to paste as if the PDF had reported it. It is evidence that quoting 26.5% next to 227/500 attributes the n=295 reweight to the wrong denominator.

## 3. Why 500, and what a larger IRexp slice would change

The files give four reasons, and one accounting choice.

1. **Cost of blind inference.** The size audit’s reason for stopping at 194 was that every item needed a blind Opus batch plus forward prediction. The expand-500 pre-registration repeats that constraint and sizes the new draw (230) off the observed 5/106 flag rate so the merged cohort lands near 500.
2. **A pre-registered round rather than a relaxed filter.** The audit’s rejected shortcuts were adding the six dirty main-round items, or merging the pilot (21) or the electrolyte set (46).
3. **A balanced difficulty gradient.** The eligible pool is ~83% complex. A uniform draw of 500 would be about 88 simple and 412 complex. The roster is 248/252 by design of the three balanced draws, then slightly tilted by the string prefix (the 200-cut is 97/103, not 100/100).
4. **An exact integer.** 194+106+200 is the arithmetic that hits 500. The pre-registered merge (194+101+224 = 519, or 295+~218) was not what was locked.

Coverage, from numbers already in the repo plus the join in this note:

- 500 / 28,988 ≈ **1.7%** of the pre-J eligible quadruples. The J-recoverable denominator is smaller and unpublished.
- Simple molecules are oversampled by about **2.8×** relative to the 17.5% corpus share (`248/500` versus 0.175). The PDF’s 26.5% reweight does not correct the 500; the stratum rates on the 500 itself reweight to about 33% top-1, as computed above.
- The three slices are not exchangeable. Locked 194 is 28.4% top-1, the +106 is 59.4%, the 200-cut is 54.5%. The rebuttal pack’s Wilson intervals on those slices (22.5–35.1, 49.9–68.3, 47.6–61.3) do not overlap the 194 with either expansion. A subgroup analysis that pools them is a size-weighted mixture of two harnesses and of a harder early cohort with two easier later ones.
- Paper concentration is mild (max 5). Scaffold concentration is not: 74/500 share the benzene Murcko core. Subgroup rates for “aromatic” tasks will be repeated measures of that core.
- Median size 21 versus the audit’s corpus median 26. The benchmark’s difficulty gradient is real (`161/248` versus `66/252`) and it is not the corpus’s size mix.
- The Wilson interval on the headline top-1 is about eight points wide (41.1 to 49.8). That is wide enough that another 500-draw could move the point. It is not wide enough to meet NMRTrans on the same 500 (79/500 = 15.8% top-1; `IRSpectra-Bench/data/baseline_nmrtrans/SCORES.md`).

A larger slice of IRexp would tighten the interval and would let rare scaffolds appear more than once. It would not, by itself, turn the 50/50 roster into a corpus-weighted estimate. That estimate is the reweight, which has to be recomputed on the 500 and labeled as such.

## 4. Protocol table

Generation parameters that the cell leaves blank were not stored. “Thinking” is the manuscript’s label when no slug was stored, and the slug when one was.

| experiment | model id as recorded | thinking | n | k (budget) | prompt file | generation parameters | date / run id |
|---|---|---|---|---:|---|---|---|
| Headline slice, locked 194 | Claude Opus; pilot display string Claude Opus 4.8 only (`docs/MODELS.md`) | not recorded. PDF says none | 194 | ≤3; **423** SMILES deposited (mean 2.180) | instruction text **not captured**. Payloads: `data/benchmark_main/batch_*.txt`, `data/benchmark_v3/`, `data/benchmark_v2_ctrl/` | temperature, top_p, top_k, max_tokens, seed: **not recorded** | solver 2026-06-09–11 UTC. Commits named in `docs/MODELS.md` §1 |
| Headline slice, +106 | family `claude-opus-5`. Post-2026-09-16 remainder: slug `claude-opus-5-thinking-high` | mixed; the thinking-high count is **not tabulated** | 106 | ≤3; **302** SMILES (mean 2.849) | not captured. Export: `scripts/export_round.py` | early batches died at a **64,000 output-token** ceiling (deviation 2). No temperature or seed | draw seed **2026**. Deposits complete 2026-09-16. Provenance: `data/benchmark_expand/PROVENANCE.md` |
| Headline slice, expand-500 200-cut | `claude-opus-5-thinking-high` | thinking-high, pre-registered | 200 of 230 | ≤3; all 200 have **exactly 3** | not captured. One compound per agent | temperature, top_p, seed: **not recorded** | draw seed **2026500**. Draw `83e5744` (2026-09-16). Deposits through `b756768` (2026-09-19). Cut `48fcd30` (2026-09-20) |
| **Pooled generation headline** | the three rows above | **mixed** | **500** | ≤3; **1325** SMILES (mean 2.65) | — | — | lock file dated 2026-09-20 |
| Forward-verify wall | same candidate pools; ¹³C predictor recorded as Claude Opus, zero tools (`docs/FORWARD_VERIFY.md`, `docs/MODELS.md`) | not recorded for the predictor | 500 | same pools; does not add candidates | forward-prediction instruction **not captured** (`si/appendix_body.tex`, Forward-verify prompt) | chamfer in `scripts/specmetrics.py`. No temperature | 60-compound arm 2026-06-09 (`41df0eb`). Extension to the 194: 2026-08-07. +106 and expand-500 arms: 2026-09-20, `473030f`, `data/fverify_n500/WALL_n500.md` |
| Nested formula-only and full lists | Claude Opus, same 60 as v3+v2_ctrl | PDF: non-thinking. Slug not in the deposit | 60 | ≤3 | `data/modality/prompt_full.txt`, `data/modality/prompt_formulaonly.txt` (payloads; the wrapper is the missing headline prompt) | not recorded | 2026-07-28, commit `a98d01a`. Scores 14/60 full, 3/60 formula-only (`data/fverify/results.txt` self-rank 14/60; recall 19/60) |
| Leave-one-modality campaign | `model=claude-opus-5` in `bNN.META.md` | PDF calls this “Claude thinking”. **The META file does not say thinking, temperature, or seed** | 60 | ≤3 (table reports top-1 and top-3) | `data/modality/prompt_full.txt`, `prompt_noIR.txt`, `prompt_noH.txt`, `prompt_noC.txt`, `prompt_formulaonly.txt` | not recorded | campaign `2026-09-23`, branches `cursor/ablation-<condition>-bNN-*`, batches of 5. Full lists **35/60** top-1, **38/60** top-3 (`main.tex` Table formula-only) |
| Cross-vendor solve + chamfer | `grok-4.6`, `gemini-3.7-flash`, `gpt-5.6-sol` via Cursor. Claude column is the June Opus rescored, not a new call | not recorded (`docs/SUBMISSION.md` gap 2: reasoning-effort tier per arm not recorded) | 60 | 3 requested. Others returned **3.00**; Claude mean **2.20** | **`sweep_prompts/solve_01.md`–`solve_10.md`** (six compounds, one fresh context). Verify prompts: `sweep_prompts/verify/` | Cursor path: vendor defaults, not stored. OpenRouter path (`scripts/openrouter_run.py`) sets `max_tokens=120000` and **no** temperature; that path was used for DeepSeek and Nemotron, which are not in the PDF’s four-vendor table | 2026-08-13–17 (`docs/MODELS.md`). Recall: Grok 32/60, Gemini 30/60, GPT-5.6 Sol 25/60, Claude 19/60. Chamfer precision\|recall: 20/32, 22/30, 17/25, 16/19 |
| Claude ladder | Opus (rescore of main `raw/`), Sonnet, Haiku, Fable 5 | not recorded | 24 of the main round | ≤3 | payloads in the batch files; instruction not captured. Opus context packing differs from the other three (`docs/MODELS.md` §1) | not recorded | 2026-06-11. Rebuttal rescore: Opus 6/24, Sonnet 5/24, Haiku 0/24, Fable 11/24 |
| Generate-wide | Claude Opus, 10 agents | not recorded | 60 | **up to 6** per solver, then pooled | `data/gw/batch_*.txt` | not recorded | 2026-06-10, commit `bdb0532`. `scripts/score_generate_wide.py` on this tree: recall **19/60 → 25/60**, forward-verified top-1 **16/60 → 18/60** |
| NMRTrans | checkpoint `little1d/C-H-Formula` file `nmrtrans-c-h-nmr-formula.ckpt`, sha256 `d184e228…4fcd`. Code `little1d/NMRTrans` commit `9a72756` | n/a (beam search) | 500, same qid roster | beam **3** | no LLM prompt. IR unused. Formula vector + parsed ¹H/¹³C | `do_sample=False`, `max_length=82`, CPU | run date **not in** `data/baseline_nmrtrans/SCORES.md`. Questions pinned to `48fcd30`. Scores **79/500** top-1, **102/500** recall |

Forward-verify on the 500, from `data/fverify_n500/WALL_n500.md` (not recomputed in this note):

| arm | n | verified | misranked | never proposed |
|---|---:|---:|---:|---:|
| locked 194 | 194 | 58 | 7 | 129 |
| +106 | 106 | 56 | 12 | 38 |
| 200-cut | 200 | 90 | 26 | 84 |
| **500** | **500** | **204** | **45** | **251** |

`58+56+90 = 204`, `7+12+26 = 45`, `129+38+84 = 251`, and `204+45 = 249`. Generation recall and forward-verify recall match. Self-rank top-1 is 227. Chamfer top-1 is 204. The ranker is 23 items worse than the solver’s own order. On the expand-500 draw alone the same pattern holds: verify **103/230** versus self **129/230** (`NIGHT_POOL_2026-09-20.md`).

## 5. Settings that are not in the files

- Temperature, `top_p`, `top_k`, generation seed, and `max_tokens` for every Claude, Grok, Gemini, and GPT-5.6 Sol arm. The only stored token ceiling is the 64,000 output-token failure mode on +106 batches, and `max_tokens=120000` on the OpenRouter transport, which did not produce the headline.
- A dated model snapshot for every arm. `Claude Opus 4.8` is a display string for the pilot only.
- The headline Claude instruction text. The SI listing that begins “You are given only” is labeled as a contract, not a recovered prompt (`si/appendix_body.tex`, Headline prompt). The verbatim prompts in the repo are `sweep_prompts/solve_*.md` and the modality payloads.
- The thinking on/off bit for the 194, for the early +106 batches, and for the 2026-09-23 ablation. The PDF asserts a no-thinking versus thinking split. The deposits support that assertion for the expand-500 slug and for an untabulated tail of the +106, and they do not support it for the June 2026 runs.
- Seeds for the 140 and the 40.
- The J-recoverable pool size, so the sampling fraction inside the pool that was actually drawn from is unknown.
- Per-item token counts, dollars, and wall time (`analysis/rebuttal_pack/REPORT.md` §5).
- Any sweep of k in {5, 10, 20, 50} on the 500, and any exhaustive formula-constrained isomer enumeration plus a ranker on the 500. The only larger-budget experiment on file is generate-wide, k≤6, on the same 60 compounds: recall 19/60 to 25/60, verified top-1 16/60 to 18/60. Most of that slice is still never proposed (35/60). The generation-wall **direction** survives that increase. Its **magnitude** is budget-dependent, and the dependence was not measured on the 500. Reviewer ndRh Q4 and reviewer ebxW Q5 ask for that measurement. It is not in the repository, and this note did not run it.

A paid rerun was not launched. If one is commissioned, the smallest design that answers the reviewers’ k question without mixing harnesses is: the frozen 60 (v3 + v2_ctrl), one model id, thinking fixed, temperature fixed, the `sweep_prompts/solve_*.md` instruction, k ∈ {3, 5, 10}, one fresh context per compound. Do not mix those outputs into 227/500. The rebuttal pack’s list-price sketch for a different 256-call Opus calibration (about $15–$98 depending on output length, Anthropic card dated 7 October 2026) is the only cost figure in the tree, and it is not a quote for this k sweep.

## 6. Paste-ready comments

These are written as author replies. They use only the integers above.

### Reviewer ndRh, Q1

The integrity filter is `scripts/validate_benchmark.py`. A ground truth is removed when the parsed ¹³C count exceeds the carbon count, when the ¹³C list is sparser than half the symmetry-unique carbon count (and below 2), when the RDKit formula disagrees with the question, or when a SELFIES round-trip fails. A high ¹H integral is reported and does not remove an item.

On the original main round that filter removed 6 of 140 (R03, R14, R65, R67, R82, R131) before those six were sent to the solver. The 40- and 20-compound controls were fixed before the filter existed and stay in the cohort whole. The +106 round flagged 5 of 106 (R12, R22, R25, R82, R91). The expand-500 round flagged 6 of 230 (R26, R31, R102, R105, R107, R138); that clean list of 224 was committed with the draw on 2026-09-16, before any solve.

“Validate-clean” in the supplement is the n=295 pool (the 194 plus the 101 clean expansion items). It is the cohort behind the stereo numbers, the size bins, and the 26.5% corpus-reweighted top-1. It is not a subset we picked out of the headline 500 after seeing scores. The headline 500 is a different union: the 194, all 106 of the first expansion (the five flags included), and 200 of the 224 expand-500 clean items. We will label those two cohorts separately so the 26.5% figure is not read as a reweight of 227/500.

### Reviewer ndRh, Q2

The pooled 45.4% mixes two harnesses. The 194, and the earlier batches of the +106, have no stored thinking budget. From 2026-09-16 the remaining +106 items, and the entire expand-500 draw, were served as `claude-opus-5-thinking-high`. We do not have a count of how many of the 106 fell in that tail. The 200-cut (109/200 top-1) is the thinking-high arm. The locked 194 (55/194) is the earlier arm. Those slices differ by more than a Wilson interval, so we will stop presenting 45.4% as a single configuration.

On one common 60-compound subset (the 40 controlled items plus the 20 within-compound controls, all inside the 194) we do have both regimes, as the paper already separates them. The nested full-list run is 14/60 top-1 and 19/60 recall. The 2026-09-23 leave-one-modality campaign on the same 60, which the paper calls the thinking arm, is 35/60 top-1 and 38/60 top-3 with every list present. That campaign’s batch metadata records `claude-opus-5` and does not record a thinking budget or a temperature, so we will either attach the slug or stop calling the contrast “thinking versus non-thinking” until the slug is in the deposit. We have not rerun thinking on and off on all 500.

### Reviewer ndRh, Q3

What is frozen, and regenerates 227/500 and 249/500, is the question ids, the gold connectivity keys, the prediction JSONL, and the RDKit InChIKey-14 scorer. What was not stored is the headline instruction text, the model snapshot, the temperature, the generation seed, and the thinking budget on the June 2026 runs. The cross-vendor prompts are verbatim in `sweep_prompts/solve_01.md` through `solve_10.md`. The expand-500 solver slug is `claude-opus-5-thinking-high`, one compound per context, at most three SMILES. We cannot offer a bit-exact rerun of 227/500. A fully specified evaluation has to be a new run, on a stated subset, with the prompt, the model id, the thinking setting, and k written down before the run. We have not launched that run. The closest fully prompted comparison already in the paper is the 60-compound cross-vendor arm, and even there the Claude column is a rescore of the June deposits (mean 2.20 candidates) rather than a fresh call under the Grok/Gemini/GPT prompt.

### Reviewer ebxW, Q2

The 500 is three pre-existing rounds, not one sample of 500.

The sampler is `scripts/benchmark_v2.py`, function `sample2`. It seeds Python’s RNG, drops any InChIKey-14 used in an earlier round, keeps the first gzip row per connectivity key, and draws `n/2` simple and `n/2` complex molecules by shuffling each stratum and taking the first records whose raw ¹H, refetched from PMC-OA, still contains a J value. Simple means at most two rings, no fused, spiro, or bridgehead atom, and at most 22 heavy atoms. There is no per-paper cap and no scaffold or Tanimoto filter.

The 194 is the spectrally checked main round (134 of 140) plus two control rounds (40 and 20) that were kept whole. The seeds for the 140 and the 40 were not stored. The 20-compound control is `sample2 --n 20 --seed 23`. The next 106 were drawn with `sample2 --n 106 --seed 2026` (53/53), after excluding the 194. The last draw is `sample2 --n 230 --seed 2026500` (115/115), after excluding both earlier rounds. Six of those 230 failed the ¹³C-overread check; the 224 clean ids were fixed before solving.

The 500 keeps all 106, including five items that failed that check, and keeps 200 of the 224. The 200 are the first 200 ids in Python string order (`R01` through `R75` in that order; the ids left out are `R76`–`R99`). String order is not integer order and is not stratified: the kept 200 are 97 simple and 103 complex. We recorded that prefix on 2026-09-20, after the 224 had already been scored. The prefix does not use the scores. The 24 ids it drops are the easier group (18/24 top-1), so the prefix lowers the headline relative to keeping all 224 (245/524). InChIKey-14 collisions across the three slices are zero. Across the 500, 405 source papers appear, 69 papers contribute more than one compound, and the maximum from one paper is 5. The largest Murcko scaffold is benzene, shared by 74 compounds. We did not down-sample either concentration.

### Reviewer ebxW, Q3

Five hundred is the size at which a new blind round, drawn under a written seed and large enough to absorb about a 5% ground-truth flag rate, could be merged with the 194 and the 106 and still be fully deposited. The pre-J eligible pool in the size audit is 28,988 compounds, so 500 is about 1.7% of that pool. The pool is 17.5% simple. The roster is 248/252 simple/complex because each round was balanced, not because the literature is. The corpus-reweighted 26.5% in the paper is the n=295 validate-clean pool, not a reweight of the 500. Reweighting the 500’s own stratum rates (161/248 and 66/252) at the same 17.5/82.5 weights is a different number, and we will compute and label it rather than reuse 26.5%.

The three slices are not one population: 55/194, 63/106, and 109/200 top-1. A subgroup printed on the pooled 500 is dominated by whichever slice is larger, and the later slices were easier for this solver. Paper-level concentration is limited (maximum 5). Scaffold-level concentration is not (74 compounds share a benzene core), so aromatic subgroups are not 74 independent scaffolds. The Wilson interval on 227/500 is 41.1–49.8. That is the stability we can claim for this roster. It is not a claim about the rest of IRexp.

### Reviewer ebxW, Q4

The common subset we can point to is the 60 compounds in `data/benchmark_v3` and `data/benchmark_v2_ctrl`. The prompts for the non-Claude models are `sweep_prompts/solve_01.md`–`solve_10.md`, six compounds per fresh context, three SMILES requested, no tools. Grok 4.6, Gemini 3.7 Flash, and GPT-5.6 Sol each returned 3.00 candidates. The Claude numbers on that slice are the earlier deposits, mean 2.20 candidates, 14/60 top-1 and 19/60 recall, not a new call under that prompt. Temperature and thinking effort were not stored for any of the four. The 2026-09-23 leave-one-modality run on the same 60 (35/60 top-1 with all lists) is a second Claude configuration; its metadata records `claude-opus-5` and not a thinking budget. The headline 500 is not this protocol: 200 of its items are `claude-opus-5-thinking-high` at exactly three candidates, and the other 300 are the earlier harness at a mean below three. We will report the 60 and the 500 as different experiments.

## 7. Methods subsection draft

The text below is for the extra page. It is written so it can replace the current construction paragraph. It does not introduce a new headline.

```
\paragraph{How the 500-item roster was drawn.}
IRSpectra-Bench is three rounds from the structure-complete split of IRexp,
scored as one list. The sampler (\texttt{scripts/benchmark\_v2.py},
\texttt{sample2}) fixes a seed, removes any connectivity key used in an
earlier round, and draws an equal number of simple and complex molecules.
A molecule is simple when it has at most two rings, no fused, spiro, or
bridgehead atom, and at most 22 heavy atoms; otherwise it is complex.
Within a stratum the draw is a shuffle of the records whose raw $^1$H,
refetched from the PMC-OA full text, still contains a coupling constant.
The only deduplication is the connectivity key. The draw does not cap
compounds per paper and does not filter by scaffold similarity.

The first 194 items are a spectrally checked main round (134 of 140) plus
two control rounds (40 and 20) that were fixed before that check and are
kept whole. The seeds for the 140 and the 40 were not stored; the
20-item control is seed 23. The next 106 items are seed 2026 (53 simple,
53 complex). The last draw is seed 2026500, $n{=}230$ (115/115). Six of
those 230 list more $^{13}$C peaks than the structure has carbons
(R26, R31, R102, R105, R107, R138). That clean list of 224 was fixed
before solving. The headline keeps every one of the 106, including five
items that fail the same check, and keeps the first 200 clean ids in
Python string order (R01 through R75 in that order; R76--R99 are the
ids left out). String order is not integer order and is not stratified:
the 200 contain 97 simple and 103 complex molecules. The prefix was
applied after the 224 had been scored. It does not depend on those
scores. The 24 omitted items are solved more often (18/24 top-1) than
the 200 that were kept (109/200), so the prefix does not raise the
headline. Replacing it with all 224 clean items gives 245/524.
Across the 500, all 500 connectivity keys are distinct, 405 source
papers appear, and no paper contributes more than five compounds.
Seventy-four compounds share a benzene Murcko scaffold. We report that
concentration and we did not remove it.

The integrity filter (\texttt{scripts/validate\_benchmark.py}) drops a
ground truth when the $^{13}$C count exceeds the carbon count, when the
$^{13}$C list is too sparse to constrain the symmetry-unique carbons,
when the formula disagrees with the structure, or when a SELFIES
round-trip fails. The supplement's validate-clean cohort is
$n{=}295$ (the 194 plus 101 clean items from the first expansion).
Stereo, size bins, and the 26.5\% corpus-reweighted top-1 are
$n{=}295$ figures. They are not a reweight of the 500.

\paragraph{What was held fixed at evaluation, and what was not.}
A prediction is correct when the first 14 characters of the RDKit
InChIKey match. Top-1 reads the first SMILES. Recall reads the list,
which is at most three SMILES. Precision given recall is
$227/249 = 91.2\%$. The same lists, re-ranked by symmetric chamfer on
blind $^{13}$C predictions, give a different top-1: 204/500 verified,
45/500 recalled but ranked second or worse, 251/500 never proposed.
The ranker does not enlarge the pool, and on this pool it is 23 items
below the solver's own order.

The 500 mixes two consumer harnesses. The 194, and the earlier batches
of the 106, have no stored thinking budget, temperature, or model
snapshot. The expand-500 items, and the tail of the 106 solved after
16 September 2026, used the slug \texttt{claude-opus-5-thinking-high},
one compound per context. Mean list length is 2.180 on the 194, 2.849
on the 106, and 3 on the 200. The pooled 45.4\% is the size-weighted
mixture of those runs (55/194, 63/106, 109/200). The headline
instruction text was not captured. The cross-vendor prompts on the
shared 60-compound subset are deposited
(\texttt{sweep\_prompts/solve\_01.md}--\texttt{solve\_10.md}). On that
subset the non-Claude models returned three candidates each; the Claude
column is a rescore of the earlier lists (mean 2.20) and is 14/60
top-1. A later pass over the same 60 with all lists present is 35/60.
Those two Claude numbers are different runs. They are not a controlled
thinking ablation until the thinking slug is stored with the batch.

On this 60-compound subset, pooling ten solvers at up to six candidates
each raises recall from 19/60 to 25/60 and forward-verified top-1 from
16/60 to 18/60. Thirty-five of the 60 structures are still absent.
We have not measured recall at candidate budgets of 5, 10, 20, or 50
on the 500, and we do not claim the 251 never-proposed count is
invariant to that budget.
```

## 8. Rerun

From a checkout that can see commit `48fcd30153df5e331fab43cfa514763db8ee3891` (branch `cursor/expand-bench-500-b78b`):

```
python analysis/iclr_rebuttal_nov2026/sampling_protocol/verify_locked_roster.py
```

Requires RDKit. Reads `data/irexp_resolved/irexp_resolved.jsonl.gz` and the locked-round files on `main`. Reads expansion questions, predictions, and the 200-id list with `git show`. Does not call a model and does not write an answer key. The expected headline line is `HEADLINE n=500 top1 227/500 recall 249/500`.
