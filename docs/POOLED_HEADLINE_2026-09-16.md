# Pooled IRSpectra-Bench headline — 2026-09-16

Paper-facing headline is the **pooled generation cohort**, not n=194 with
expansion as a side note. Every count below is regenerated from disk by
`python scripts/score_pooled.py` (which calls `scripts/score_main.py` for the
locked 194 and the same InChIKey-14 rule as `benchmark_v2.py score2` for the
expansion). Bootstrap 95% CIs use `score_main.boot` (seed 0, 2000 resamples),
the same interval the n=194 tables already used.

**Headline: n=295** = 194 locked + **101 validate-clean** expansion compounds.
The five ¹³C-overread flags are **excluded** from the headline, matching the
pre-registration stopping rule (same treatment as the six main-round exclusions).
n=300 (194+all 106) is reported as a sensitivity row, not the headline.

Forward-verification has **not** been run on the expansion. Pooled numbers are
**generation top-1 / recall only**. Do not invent a pooled `fig_wall` or a
pooled verification-precision.

## Reproduce

```
python scripts/score_pooled.py            # constitution; writes data/pooled_headline.json
python scripts/score_pooled.py --stereo   # full InChIKey; writes data/pooled_headline_stereo.json
git ls-files data/benchmark_expand/answers2.jsonl   # must be empty
```

The expansion key is reconstructed only under `/tmp/blind/_key/` by unique
(formula, IR band list, ¹³C) match against `irexp_resolved.jsonl.gz` (deviation 4).
This scorer refuses to run if `data/benchmark_expand/answers2.jsonl` is in the
working tree. Fable is not scored and is not pooled.

## Headline (n=295, five flags excluded)

| metric | overall (n=295) | simple (n=147) | complex (n=148) |
|---|---|---|---|
| top-1 exact constitution | **116/295 (39.3%)** [34–45] | 87/147 (59.2%) [51–67] | 29/148 (19.6%) [14–26] |
| recovered / generation recall (top-3) | **130/295 (44.1%)** [39–49] | 94/147 (63.9%) [56–71] | 36/148 (24.3%) [17–31] |
| scaffold-level (best Tanimoto ≥0.45) | 64% | 80% | 48% |
| mean best Tanimoto | 0.66 | 0.79 | 0.53 |

Self-ranking precision | recall on this generation pool: **116/130 (89.2%)**.
That is *not* forward-verification precision.

By size (headline n=295):

| heavy atoms | n | top-1 | recall |
|---|---:|---|---|
| ≤15 | 53 | 36/53 (67.9%) | 39/53 (73.6%) |
| 16–25 | 152 | 65/152 (42.8%) | 75/152 (49.3%) |
| >25 | 90 | 15/90 (16.7%) | 16/90 (17.8%) |

Corpus-reweighted (frozen 17.5% simple / 82.5% complex from
`scripts/corpus_reweight.py`; bootstrap the pooled stratum rates, then apply
those weights): top-1 **26.5% [21–32]**, recall **31.3% [25–37]**.

Full InChIKey (stereo) on the same 295: top-1 **93/295 (31.5%)** [26–37],
recall 108/295 (36.6%) [31–42]. Locked n=194 stereo remains 41/194 (21.1%).

## How 295 is built (slices)

| set | n | top-1 | recall | simple top-1 | complex top-1 |
|---|---:|---|---|---|---|
| locked rounds (main clean 134 + v3 40 + v2_ctrl 20) | 194 | 55/194 (28.4%) [22–35] | 65/194 (33.5%) [27–40] | 47/98 (48.0%) | 8/96 (8.3%) |
| expansion, all deposited Opus | 106 | 63/106 (59.4%) [50–69] | 68/106 (64.2%) [56–73] | 41/53 (77.4%) | 22/53 (41.5%) |
| expansion, validate-clean | 101 | 61/101 (60.4%) [50–69] | 65/101 (64.4%) [54–73] | 40/49 (81.6%) | 21/52 (40.4%) |
| **headline pool (194+101)** | **295** | **116/295 (39.3%)** | **130/295 (44.1%)** | 87/147 (59.2%) | 29/148 (19.6%) |
| sensitivity (194+all 106) | 300 | 118/300 (39.3%) [34–45] | 133/300 (44.3%) [39–50] | 88/151 (58.3%) | 30/149 (20.1%) |

Expansion integer percents previously frozen in
`docs/EXPANSION_RESULTS_2026-09-16.md` (59% / 64%) are `round(100*k/n)` from
`score2`. The one-decimal figures here are the `score_main` convention (28.4%
for 55/194). Counts are identical: 63/106, 68/106, 61/101, 65/101.

The expansion slice is substantially easier for this solver than the locked 194
(59.4% vs 28.4% top-1). That difference is a **result**, not a reason to keep
n=194 as the paper headline. The pooled number is the size-weighted mix.

## Five flagged compounds — excluded from headline

| | |
|---|---|
| qids | **R12, R22, R25, R82, R91** |
| reason | ¹³C-overread (`scripts/validate_benchmark.py`); snapshot `data/benchmark_expand/clean_qids.json` |
| when flagged | before these subset totals were computed (stopping rule) |
| excluded from headline? | **yes** (n=295, not n=300) |
| effect vs including them | 2 extra top-1 hits and 3 extra recall hits → 118/300 and 133/300 |

Including the five does not move the one-decimal headline (both 39.3% top-1).
They are still excluded because the pre-reg says to, not because of the score.

## Forward-verify — still n=194 only

| item | status |
|---|---|
| `data/fverify/` + `data/fverify_main/` | complete; `data/diagnosis.json` n=194 |
| generation recall | 65/194 (33.5%) |
| top-1, solver self-ranking | 55/194 (28.4%) |
| top-1, forward-verified | 58/194 (29.9%) |
| precision \| recall (fverify) | **58/65 (89%)** |
| mis-ranked / never proposed | 7 / 129 |
| `scripts/forward_verify_main.py` on expansion | **not run** |
| expansion verification precision | **does not exist** |
| Fable expansion | 68/106 deposits; **not scored**; **not pooled** |

`scripts/forward_verify_all.py` will pick up an expansion arm automatically
*if* `data/fverify_expand*/` contains `candidates.jsonl` and the matching
`data/benchmark_expand/` roster. That directory is absent. Until it exists,
any pooled verified / mis-ranked / wall triple would be invented.

## Figures that cannot be rebuilt yet

| artefact | script | why it stays n=194 | what regenerates it |
|---|---|---|---|
| `docs/figures/fig_wall.png` | `scripts/make_fig_wall.py` | reads `data/diagnosis.json` written by `forward_verify_all.py` (58/7/129 on n=194). No expansion fverify bundle. | Run expansion `forward_verify_main.py` → deposit `data/fverify_expand/` → `forward_verify_all.py` → `make_fig_wall.py` |
| `data/diagnosis.json` | `scripts/forward_verify_all.py` | same | same |
| `docs/figures/fig1_difficulty.png` | `scripts/make_figures.py` | calls `score_main.load()`, which is still the 134+40+20 union and has **no pooled switch** | Teach `score_main.load()` to include expansion (key must be present), then re-run `make_figures.py` |
| `fig2_size`, recency panel, miss-isomer 76.6% (137 misses), named-ring 10/194 | various | those analyses were never written against the expansion roster | re-run the named script with the pooled load; do not scale n=194 counts |

Paper should keep Figure 1 as the **n=194 forward-verified diagnosis** and say
so in the caption, while Table 1 / abstract headline n is **295 generation**.
Do not draw a pooled wall from self-ranking and label it forward-verify.

## What this does not change

- `scripts/score_main.py` default remains n=194 (manuscript gate / combined
  `docs/PAPER.md` still quote that cohort). Pooled scoring is
  `scripts/score_pooled.py`.
- spectro-agent PR **#18** still has an incomplete Fable arm and a withheld
  expansion key. **Do not merge #18 to main** for that reason. These pooled
  numbers can land on `claude/funny-maxwell-u5S31` without that merge.
- No vendor numbers, no expansion fverify rates, no new isomer-miss audit.

## Locked facts (do not drift)

| item | value |
|---|---|
| headline n | **295** (194+101; flags excluded) |
| headline top-1 / recall | **116/295 (39.3%) [34–45] / 130/295 (44.1%) [39–49]** |
| corpus-reweighted top-1 / recall | 26.5% [21–32] / 31.3% [25–37] |
| sensitivity n=300 top-1 / recall | 118/300 (39.3%) / 133/300 (44.3%) |
| expansion all / clean | 63/106 (59.4%) / 61/101 (60.4%) top-1 |
| flagged | R12, R22, R25, R82, R91 — excluded from headline |
| fverify / fig_wall | n=194, 58/7/129; expansion **pending** |
| Fable | 68/106; not in the pool |
| answers2.jsonl | re-withheld; do not commit |

Source sidecar: `data/pooled_headline.json`.
