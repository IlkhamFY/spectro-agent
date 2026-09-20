# Night pool — 2026-09-20

Honest numbers only. Every accuracy figure below is copied from a script
that ran on this VM after a lost-vault key reconstruction. Keys were
restored into the working tree only for that pass, then deleted again.
`answers2.jsonl` is **not** in the tree and is **not** in `git ls-files`
for `data/benchmark_expand/` or `data/benchmark_expand_500/`.

Companion inventory: `data/fverify_expand_500/INVENTORY_2026-09-20.md`.

**Paper headline stays n=300** (locked 194 + all Opus +106). This
expand-500 round is now scored, but it is **not** written into the paper
headline. No CIs. fverify coverage **41/41, 681/681**; score in the
fverify section below.

## What ran (and what did not)

| step | ran? |
|---|---|
| reconstruct expand-500 key, unique (formula, IR, ¹³C) vs `irexp_resolved.jsonl.gz` | yes — **230/230** unique, 0 prior-round InChIKey-14 collisions |
| reconstruct +106 key, same rule | yes — **106/106** unique, 0 collisions; `score2` reproduced the committed +106 table (63/106 top-1, 68/106 recall) |
| `python scripts/benchmark_v2.py score2 --outdir data/benchmark_expand_500` | yes |
| `python scripts/score_pooled.py --expand --expand-500` | yes (validate-clean path only) |
| extra all-deposited pools (same InChIKey-14 rule as `score_pooled.py`) | yes |
| `scripts/validate_benchmark.py` | **no** — would rewrite committed `clean_qids.json`; used the existing 224-qid snapshot |
| `collect_round.py` | **no** — 230 `raw/single_R*.json` left untouched |
| `forward_verify_main.py score` | **yes** — official `score()` on the deposited 230-qid bundle (is_true filled under `/tmp`; prep not run) |
| `--ci` / bootstrap | **no** — do not invent CIs |
| merge PR #18 | **no** |

Key restore for scoring:

```
# vault only; never committed
/tmp/blind/_key/benchmark_expand_500.answers2.jsonl.withheld
/tmp/blind/_key/benchmark_expand.answers2.jsonl.withheld
python scripts/benchmark_v2.py score2 --outdir data/benchmark_expand_500
python scripts/score_pooled.py --expand --expand-500
# then rm the two answers2.jsonl copies from the working tree
```

## Pool n options

| n | composition | role |
|---:|---|---|
| **300** | locked 194 + all Opus +106 | **IRSpectra-Bench paper headline** (do not replace with expand-500) |
| **524** | 194 + all-106 + expand-500 validate-clean 224 | largest clean-on-this-round pool that still keeps all +106 |
| **519** | 194 + +106 validate-clean 101 + expand-500 validate-clean 224 | what `score_pooled.py --expand --expand-500` prints (both expansions clean-filtered) |
| 530 | 194 + all-106 + expand-500 all 230 | all deposited, including 6 expand-500 13C-overread flags |
| 295 | 194 + +106 validate-clean 101 | older “n=295” lock = 194+101; **not** the paper n |

Flagged expand-500 qids (in the all-230 row, out of the clean-224 row):
**R26, R31, R102, R105, R107, R138**. Snapshot: `clean_qids.json`.

## expand-500 generation (`score2`)

Verbatim footer of `python scripts/benchmark_v2.py score2 --outdir data/benchmark_expand_500`:

```
overall recovered (top-3): 138/230 (60%)   top-1 exact: 129/230 (56%)
  simple  : recovered 87/115 (76%)  top1 82/115 (71%)  meanBestTani 0.863
  complex : recovered 51/115 (44%)  top1 47/115 (41%)  meanBestTani 0.645
```

| set | n | top-1 | recall (top-3) |
|---|---:|---|---|
| all deposited Opus | 230 | **129/230 (56.1%)** | **138/230 (60.0%)** |
| validate-clean subset | 224 | **127/224 (56.7%)** | **135/224 (60.3%)** |

Strata (all 230; 115/115 as drawn) from the extra-pool script (same InChIKey-14 rule):

```
=== expand_500 ALL deposited (230)  n=230  (InChIKey-14 constitution) ===
  top-1  129/230 (56.1%)
  recall 138/230 (60.0%)
  simple   n=115  top-1 82/115 (71%)  recall 87/115 (76%)
  complex  n=115  top-1 47/115 (41%)  recall 51/115 (44%)

=== expand_500 validate-clean (224)  n=224  (InChIKey-14 constitution) ===
  top-1  127/224 (56.7%)
  recall 135/224 (60.3%)
  simple   n=110  top-1 81/110 (74%)  recall 85/110 (77%)
  complex  n=114  top-1 46/114 (40%)  recall 50/114 (44%)
```

## Official `score_pooled.py --expand --expand-500`

Validate-clean expansions only. Verbatim:

```
=== locked n=194 (score_main cohort)  n=194  (InChIKey-14 constitution) ===
  top-1  55/194 (28.4%)
  recall 65/194 (33.5%)
  simple   n= 98  top-1 47/98 (48%)  recall 53/98 (54%)
  complex  n= 96  top-1 8/96 (8%)  recall 12/96 (12%)

=== expand +106  validate-clean 101/106  n=101  (InChIKey-14 constitution) ===
  top-1  61/101 (60.4%)
  recall 65/101 (64.4%)
  simple   n= 49  top-1 40/49 (82%)  recall 41/49 (84%)
  complex  n= 52  top-1 21/52 (40%)  recall 24/52 (46%)

=== pooled n=194 + expand-clean  n=295  (InChIKey-14 constitution) ===
  top-1  116/295 (39.3%)
  recall 130/295 (44.1%)
  simple   n=147  top-1 87/147 (59%)  recall 94/147 (64%)
  complex  n=148  top-1 29/148 (20%)  recall 36/148 (24%)

=== expand_500  validate-clean 224/230  n=224  (InChIKey-14 constitution) ===
  top-1  127/224 (56.7%)
  recall 135/224 (60.3%)
  simple   n=110  top-1 81/110 (74%)  recall 85/110 (77%)
  complex  n=114  top-1 46/114 (40%)  recall 50/114 (44%)

=== pooled headline (194 + included expansions, validate-clean)  n=519  (InChIKey-14 constitution) ===
  top-1  243/519 (46.8%)
  recall 265/519 (51.1%)
  simple   n=257  top-1 168/257 (65%)  recall 179/257 (70%)
  complex  n=262  top-1 75/262 (29%)  recall 86/262 (33%)
```

## All-deposited pools (same rule; not what `score_pooled.py` prints)

```
=== POOL n=300 = 194 + all-106  n=300  (InChIKey-14 constitution) ===
  top-1  118/300 (39.3%)
  recall 133/300 (44.3%)
  simple   n=151  top-1 88/151 (58%)  recall 96/151 (64%)
  complex  n=149  top-1 30/149 (20%)  recall 37/149 (25%)

=== POOL n=524 = 194 + all-106 + expand500-clean-224  n=524  (InChIKey-14 constitution) ===
  top-1  245/524 (46.8%)
  recall 268/524 (51.1%)
  simple   n=261  top-1 169/261 (65%)  recall 181/261 (69%)
  complex  n=263  top-1 76/263 (29%)  recall 87/263 (33%)

=== POOL n=530 = 194 + all-106 + expand500-all-230  n=530  (InChIKey-14 constitution) ===
  top-1  247/530 (46.6%)
  recall 271/530 (51.1%)
  simple   n=266  top-1 170/266 (64%)  recall 183/266 (69%)
  complex  n=264  top-1 77/264 (29%)  recall 88/264 (33%)
```

+106 all-deposited (sanity vs committed `data/benchmark_expand/STATUS.md`):

```
=== expand +106 ALL deposited  n=106  (InChIKey-14 constitution) ===
  top-1  63/106 (59.4%)
  recall 68/106 (64.2%)
```

That matches the committed +106 `score2` footer (63/106, 68/106).

## fverify (coverage + official score)

See `data/fverify_expand_500/INVENTORY_2026-09-20.md` and
`data/fverify_expand_500/STATUS.md`.

- present: **f1–f41** (41/41)
- missing: **none**
- unique SMILES: **681/681 (100%)**
- qids fully covered: **230/230**

Key reconstructed again (230/230 unique; 0 prior-round InChIKey-14
collisions) and written only to
`/tmp/blind/_key/benchmark_expand_500.answers2.jsonl.withheld`. Generation
sanity on that key: 129/230 top-1, 138/230 recall (matches committed
`score2`). Official `prep` was not run. `score()` used a `/tmp` candidates
copy with `is_true` filled; committed `candidates.jsonl` still omits it.

Verbatim `scripts/forward_verify_main.py score()` footer (230 qids):

```
forward predictions loaded: 681/681 unique SMILES
compounds: 230
  recall (true in candidate set): 138/230 (60%)
  top-1, solver self-rank:        129/230 (56%)
  top-1, forward-verified rerank: 103/230 (45%)
  conditional on recall (n=138): self 129/138 (93%) | verify 103/138 (75%)
  multi-candidate only  (n=137): self 128/137 | verify 102/137
```

| set | n | recall | self top-1 | verify top-1 | verify \| recall |
|---|---:|---|---|---|---|
| all deposited | 230 | **138/230 (60.0%)** | **129/230 (56.1%)** | **103/230 (44.8%)** | **103/138 (74.6%)** |
| validate-clean | 224 | **135/224 (60.3%)** | **127/224 (56.7%)** | **103/224 (46.0%)** | **103/135 (76.3%)** |

Verify does not beat self-rank on this arm. `forward_verify_all.py` not
run. No CIs.

## Artifact paths

| path | what |
|---|---|
| `data/fverify_expand_500/INVENTORY_2026-09-20.md` | f1–f41 all present; 681/681 |
| `data/benchmark_expand_500/NIGHT_POOL_2026-09-20.md` | this file |
| `data/benchmark_expand_500/STATUS.md` | live status |
| `data/benchmark_expand_500/predictions2.jsonl` | 230 lines, 690 candidates |
| `data/benchmark_expand_500/clean_qids.json` | 224 validate-clean qids |
| `data/benchmark_expand_500/raw/single_R*.json` | 230 provenance files (untouched tonight) |
| `data/fverify_expand_500/raw/f1.json`…`f41.json` | 41 deposited ¹³C batches |
| `data/fverify_expand_500/STATUS.md` | coverage + official score |
| `data/fverify_expand_500/results.txt` | verbatim `score()` footer |
| `data/fverify_expand_500/fbatch_*.txt` | 41 keyless prompts |
| `/tmp/night_score/score2_expand500.txt` | local `score2` transcript (not in tree) |
| `/tmp/night_score/score_pooled.txt` | local pooled transcript (not in tree) |
| `/tmp/night_score/extra_pools.txt` | local all-deposited pool transcript (not in tree) |
