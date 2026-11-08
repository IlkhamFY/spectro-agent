# Constraint funnel on the locked IRSpectra-Bench n=500 roster

Offline diagnostics only. No model was called. The locked generation outcome is unchanged:

- 227 exact top-1
- 22 in the k≤3 pool but not top-1
- 251 never proposed at k≤3

Recall at k≤3 is 249/500 (227 + 22). These three integers are the generation wall, not the forward-verify chamfer classes (204 verified, 45 mis-ranked, 251 never proposed). This directory does not replace either set.

A rescore of the deposited rank lists against the offline structures reproduced every locked slice total before any isomer count was interpreted: 55/194, 63/106, and 109/200 top-1; 65/194, 68/106, and 116/200 recall; simple 161/248 and 172/248; complex 66/252 and 77/252.

## Roster

Source commit for the two expansion arms: `48fcd30153df5e331fab43cfa514763db8ee3891`.

The 500 problems are the locked `score_main` 194 (clean main + all of benchmark_v3 + all of benchmark_v2_ctrl), plus all 106 deposited Opus answers of the first expansion, plus the first 200 validate-clean expand-500 qids in `headline500_expand200_qids.json` (R01 through R75 in that file's sort). Sensitivity pools n=524 and n=530 are not in this roster.

Gold structures were recovered by the same unique (formula, IR, 13C) join used when those arms were scored. On the 194, the join InChIKey-14 matches the committed answer key. Gold SMILES were not an input to surge and were not a filter. They are attached afterwards as the wall label, and separately as a post-hoc check of whether the true structure would have survived the rules.

## A. Printed-list completeness

Counts are taken from the printed question fields.

- `n_C` and `n_H` are atom counts in the printed molecular formula. Three formulas carry a trailing charge (`C11H16NO3S2-`, `C13H7O2S2-`, `C32H48NO4-`). The charge is recorded and is not added to the hydrogen count.
- `n_13C` is the number of 13C chemical-shift signals after a top-level comma/semicolon split. A hyphenated range is one signal. Every one of the 500 stored 13C strings labels each signal `(1C, ...)`, and that parenthetical is 1 for every signal, so it is not an independent carbon integration. It is not summed as a measured carbon count.
- `n_ir` is the length of the printed IR list, including any repeated wavenumbers.
- `n_1H_env` is the number of 1H signals. The string is cut at the first `13C`, `MS`, `HRMS`, `ESI`, or `Anal` token (75/500 fields continue into a later section). A hyphenated range is one signal. A missing comma between two signals is split. One missing opening parenthesis (locked-main R127) is repaired before the count. expand500 R224 stays unbalanced; its seven environments are counted and its integrals are not treated as complete.
- The summed proton count is reported only when every environment has one integral. Fractional integrals (`0.5H`) are summed and then excluded from the integer hydrogen filter.

On all 500: median n_C 16.0, median n_H 17.0, median n_13C 13.0, median n_IR 10.0, median 1H environments 8.0, median n_13C/n_C 0.8333.

13C signal count versus formula carbons: 96/500 equal, 397/500 fewer signals than carbons, 7/500 more signals than carbons.

1H integrals parse for every environment in 471/500 problems (465 of those sums are integers; the rest contain a fractional integral). Among the parsed sums, 358 equal n_H, 85 are below n_H, and 28 exceed n_H.

Section cuts in the 1H field: 75/500.

By locked wall class (denominators are the locked class sizes):

| wall class | n | n_13C = n_C | n_13C < n_C | n_13C > n_C | median n_13C/n_C | 1H integrals complete | sum = n_H |
|---|---:|---:|---:|---:|---:|---:|---:|
| exact top-1 | 227 | 40 | 185 | 2 | 0.8182 | 217 | 166 |
| in pool, not top-1 | 22 | 4 | 17 | 1 | 0.8787 | 21 | 19 |
| never proposed at k<=3 | 251 | 52 | 195 | 4 | 0.8529 | 233 | 173 |

By the simple/complex label already stored on the questions (248 simple, 252 complex):

| stratum | n | n_13C = n_C | n_13C < n_C | n_13C > n_C | median n_13C/n_C | median n_IR | median 1H environments | top-1 | recall k≤3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| simple | 248 | 54 | 189 | 5 | 0.8333 | 10.0 | 7.0 | 161/248 | 172/248 |
| complex | 252 | 42 | 208 | 2 | 0.8367 | 9.0 | 10.0 | 66/252 | 77/252 |

The stratum top-1 and recall cells are the locked 161/248, 66/252, 172/248, and 77/252. They are reprinted so the completeness columns sit next to them.

### Suggested figure

`fig_completeness_vs_outcome.png` has two panels. The left panel is n_13C/n_C by the three locked wall classes, including the lists with more signals than carbons. The right panel is top-1 and recall at k≤3 inside bins of that ratio. Dashed lines are the locked rates 227/500 and 249/500. Bin counts:

| bin of n_13C/n_C | n | top-1 | recall k≤3 | in pool, not top-1 | never proposed |
|---|---:|---:|---:|---:|---:|
| n_13C > n_C | 7 | 2 | 3 | 1 | 4 |
| n_13C = n_C | 96 | 40 | 44 | 4 | 52 |
| 0.80-0.99 | 214 | 89 | 98 | 9 | 116 |
| 0.60-0.79 | 147 | 81 | 89 | 8 | 58 |
| 0.40-0.59 | 29 | 11 | 11 | 0 | 18 |
| <0.40 | 7 | 4 | 4 | 0 | 3 |

The top-1 column sums to 227 and the recall column sums to 249. This is a stratification of the locked outcome, not a new score.

## B. Constraint funnel

### IR rule table

Rules fire on presence only. A missing band does not exclude a functional group, because the completeness counts above show that the printed lists are not full spectra.

| rule | window (cm-1) | required substructure | problems triggered |
|---|---|---|---:|
| carbonyl_1650_1850 | 1650-1850 | `[#6]=[#8]` | 321/500 |
| oh_nh_3200_3600 | 3200-3600 | `[#8,#7;!H0]` | 271/500 |
| triple_or_cumulative_2100_2260 | 2100-2260 | alkyne, nitrile, isocyanate, isothiocyanate, or azide | 48/500 |

No nitro two-band rule is applied. The fingerprint pair is not specific on a short peak list. Full SMARTS and the boundary notes are in `ir_rule_table.csv`.

### Isomer generator

Constitutional isomers were counted with surge 2.0 (`-R`, aromaticity filter on) built against nauty 2.9.3. Self-checks, computed here, match the generator's known counts: C4H10 = 2, C2H6O = 2, C6H6 = 217, C10H16O = 452458, C8H10 = 4678 under `-R`, C4H12Sn = 9 with `-ESn4`.

Valence model, summed as disjoint surge element types: C 4, O 2, H 1, F/Cl/Br/I 1, Si 4, B 3, Sn 4 (`-ESn4`), N 3 or 5 (`N`/`Nx`), S 2, 4, or 6 (`S`/`Sx`/`Sy`), Se 2, 4, or 6 (`-ESe2`/`-ESfSe4`/`-ESgSe6`), P 3 or 5 (`P`/`Px`). Lowest-valence parity failure is the same parity for every higher state that adds an even number of valence units. A formula is the sum of those states.

Count mode is `surge -u -R`. The first budget is 40 s at or below 12 heavy atoms, 15 s at or below 15, 8 s at or below 20, and 5 s above that. When count mode does not finish, SMILES are streamed with a cap of 50,000. Hitting the cap proves N ≥ 50,000 for that state and therefore for the formula. It is not an exact count. Formulas that still emit nothing get one more stream of the lowest-valence state: 24 s, 14 s, or 8 s on the same heavy-atom cuts. The filters below are applied only when the summed count is exact and below 50,000, as requested.

Unique formulas in the 500: 484. Exact count: 30. Proved at least 50,000 without an exact total: 116. Not finished inside the time budget: 335. Charged formulas surge will not take: 3. Exact and below 50,000, so the filters were run: 5.

Those exact counts below 50,000, and the filters, are:

| problem | wall class | formula | N_formula | parsed | N after IR | N after IR and carbon | hydrogen filter | N_after_filters |
|---|---|---|---:|---:|---:|---:|---|---:|
| expand500:R190 | exact top-1 | C11H24O | 2426 | 2426 | 1238 | 986 | yes | 985 |
| expand500:R110 | exact top-1 | C6H8O2 | 10893 | 10872 | 849 | 696 | yes | 529 |
| locked-main:R56 | exact top-1 | C7H18Sn | 96 | 96 | 0 | 0 | yes | 0 |
| expand500:R187 | exact top-1 | C8H17BrO | 1157 | 1157 | 555 | 248 | yes | 217 |
| locked-main:R60 | exact top-1 | C9H16O | 29172 | 29172 | 29172 | 14531 | yes | 12328 |

locked-main:R56 (C7H18Sn) is the zero. Printed bands fire triple_or_cumulative_2100_2260. The true structure satisfies that IR test: no. k/N is left blank when the remaining count is 0.

Three charged formulas are outside surge's neutral graph model (`unsupported_charge`). Their completeness rows are present. Their isomer counts are blank, not guessed.

A blank count is not a large count. Median heavy-atom counts by generator status:

| status | formulas | median heavy atoms |
|---|---:|---:|
| exact | 30 | 12 |
| ge_50000 | 116 | 15 |
| unavailable | 335 | 24 |
| unsupported_charge | 3 | 16 |

Formulas that finished, or that were proved to be at least 50,000, are the smaller ones. The unfinished formulas are heavier. That split follows the time budget, not a measured isomer total, so it is not used as a log10.

### Carbon-count and hydrogen-count filters

Applied only inside an exact formula with N < 50,000, and only to RDKit-parsed surge SMILES.

- Carbon: the number of symmetry-distinct carbons (RDKit `CanonicalRankAtoms`, stereochemistry removed) is at least the printed 13C signal count. Accidental overlap and missing signals both make the structure have more distinct carbons than observed signals, so the inequality is the direction that stays valid. Equality is not required. If the printed list has more signals than formula carbons, no isomer passes.
- Hydrogen: applied only when every 1H environment has one positive integer integral and the sum is at most n_H. Each constitutional proton class (equivalent atoms times hydrogens on each) must be used whole. Classes may combine into one observed integral. Classes may be left unused when the integral sum is below n_H. Classes are not split, so a diastereotopic CH2 counted as one 2H class will fail a spectrum that shows two 1H signals. That limitation is measured by the gold audit rather than patched against the answers.
- IR rules that fired are required as well. A problem with no band inside the three windows has no IR constraint.

`N_after_filters` is the number of parsed isomers that pass the fired IR rules, the carbon inequality, and the hydrogen partition when that partition is applicable. Unparsed surge SMILES, which are concentrated in the pentavalent-nitrogen drawings, are counted beside this number and are not called passes. If any hydrogen search is undecided, `N_after_filters` is left blank.

Problems with a filter result: 5/500.

### log10(N) against the wall classes

Exact log10 values are reported only for exact positive counts. A formula proved only to be at least 50,000 is censored and is not entered as log10(50000).

Formula-count category by wall class (each problem once; shared formulas are not reweighted):

| group | n | exact <1000 | 1000-9999 | 10000-49999 | exact ≥50000 | censored ≥50000 | charge | unavailable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 500 | 1 | 2 | 2 | 25 | 123 | 3 | 344 |
| top1 | 227 | 1 | 2 | 2 | 15 | 93 | 1 | 113 |
| in_pool | 22 | 0 | 0 | 0 | 2 | 5 | 0 | 15 |
| never | 251 | 0 | 0 | 0 | 8 | 25 | 2 | 216 |

log10 of exact N_formula, problems whose formula count finished and is positive:

- all: n=30, median 6.259, IQR 5.518 to 7.585, range 1.982 to 8.093
- top1: n=20, median 5.998, IQR 5.170 to 6.870, range 1.982 to 7.985
- in_pool: n=2, median 7.596, IQR 7.588 to 7.605, range 7.579 to 7.613
- never: n=8, median 7.104, IQR 6.111 to 7.731, range 4.784 to 8.093

log10 of N_after_filters, only where the filter ran and the remaining count is positive:

- all: n=4, median 2.858, IQR 2.627 to 3.268, range 2.336 to 4.091
- top1: n=4, median 2.858, IQR 2.627 to 3.268, range 2.336 to 4.091
- in_pool: n=0
- never: n=0

### Chance baseline

For each problem the denominator is N_after_filters when that count exists, otherwise the exact N_formula. k/N is reported at k=3 and k=10. Censored and unavailable denominators are left blank. They are not replaced by 50,000. Where a denominator exists and is positive, the mean of the 3/N values is a property of that subset only.

Problems with an exact positive chance denominator: 29/500.
Of those, the denominator is N_after_filters for 4 and N_formula for 25.

- all: n=29, median 3/N = 1.299e-06, mean 3/N = 7.891e-04
- top1: n=19, median 3/N = 2.964e-06, mean 3/N = 1.202e-03
- in_pool: n=2, median 3/N = 7.607e-08, mean 3/N = 7.607e-08
- never: n=8, median 3/N = 3.978e-07, mean 3/N = 6.938e-06

### Post-hoc gold audit

This section uses the true structure after N was computed. It does not remove isomers and it was not used to choose the windows.

Where a carbonyl-window band is printed (321 problems), the true structure contains `[#6]=[#8]` in 293 cases.
Where a 3200-3600 band is printed (271 problems), the true structure has an O-H or N-H in 233 cases.
Where a 2100-2260 band is printed (48 problems), the true structure matches the triple-bond or cumulative-bond SMARTS in 43 cases.
Carbon inequality on the true structure: 448/500.
Hydrogen partition, on the 438 problems where the integer filter applies: pass 334, fail 104.

Fails are expected when a printed band is not the functional group the window names (alkyne C-H inside 3200-3600, an overtone, a solvent band) or when diastereotopic protons split a CH2. Those fails are why absence rules were not added, and why N_after_filters should be read as the size of this explicit constraint set rather than as the size of the true spectroscopic preimage.

## Files

- `completeness_by_item.csv` — one row per problem, printed counts and the locked wall class
- `completeness_by_group.csv` — the citation table for wall class and stratum
- `figure_completeness_bins.csv` — the figure's exact bin counts
- `fig_completeness_vs_outcome.png` and `.pdf`
- `ir_rule_table.csv`
- `formula_counts.jsonl` — per-formula surge record, including every valence state
- `isomer_counts_by_formula.csv`
- `funnel_by_item.csv` — N_formula, N_after_filters, and k/N
- `formula_count_by_wall.csv`
- `posthoc_gold_audit.csv`
- `summary.json`

## Reproduce

surge 2.0 was built from https://github.com/StructureGenerator/surge against nauty 2.9.3. The binary used here is `/tmp/surge/src/surge` (override with `SURGE`). RDKit parses SMILES for the filters. Gold comes from `data/irexp_resolved/irexp_resolved.jsonl.gz` on this checkout. Expansion questions and predictions are read with `git show` from the pinned commit and are not copied into this branch.

```
python3 analysis/iclr_rebuttal_nov2026/constraint_funnel/run_analysis.py
```

A formula already present in `formula_counts.jsonl` with this model id is reused. Delete that file to rerun surge.

