# CASE-lite on the locked n=500 roster

Formula-constrained constitutional-isomer enumeration, ranked by the
repository's HOSE-style 13C lookup. No language model proposes or ranks
structures in this diagnostic. Gold is applied only after the pool is built,
to read off rank.

## Method

The roster is the locked headline of 500: the validated main round, all of
`benchmark_v3`, all of `benchmark_v2_ctrl`, every compound in
`data/benchmark_expand` at `48fcd30153df5e331fab43cfa514763db8ee3891`, and the
committed 200-qid cut `headline500_expand200_qids.json`. Expansion gold is the
unique `(formula, IR, 13C)` join to `data/irexp_resolved` used by the locked
rescore. The loader checks the generation wall before any enumeration:
227 top-1, 22 proposed at k≤3 but not rank 1, and 251 never proposed.
Those three labels are the 227/22/251 wall. A molecule was proposed at k≤3
when its label is top-1 or proposed-not-top-1.

The enumerator is surge 2.0
(`https://github.com/StructureGenerator/surge/releases/download/v2.0/surge-linux-x86_64.tar.gz`, sha256 `0910de00e9b7373184a62914e1c34bf26b5fefce4f487a4088b938c0c410e9c2`),
invoked as `surge -u -R <formula>` for the count and `surge -S -R` for SMILES.
`-R` collapses Kekulé duplicates of one aromatic constitution. Valences are
surge's lowest defaults (C 4, N 3, O 2, S 2, P 3, halogen 1, Si 4). Se and Sn,
which surge does not enable by default, are passed as `-ESe2` and `-ESn4`.
The printed formula is the only structural input. Gold SMILES are not passed
to surge and are not used to choose a valence, a badlist, or a filter.

`N_iso` is the integer on surge's final `>Z generated` record. Formulas with
`N_iso` ≤ 5000 were the starting set. The cutoff was expanded to
20000 because every formula whose count finished at or below
20000 was generated and ranked. The chosen cutoff is 20000.
A formula whose count did not finish is not given an exact `N_iso` and is not
called enumerable. Exact-count timeouts were 4 s for every formula, then 20 s
for any still unfinished formula with ≤18 heavy atoms, then 45 s for any still
unfinished formula with ≤14 heavy atoms. Formulas that still had no exact count
were streamed with unbuffered `surge -S -R` until 20001 structures or 12 seconds.
Emitting 20001 structures proves `N_iso` > 20000. It is not an exact count, and
those molecules stay outside the ranked set. A formula that emits nothing in
that window stays unfinished, and no `N_iso` is stated for it. Self-checks
before the roster run: `C6H6` = 217, `C4H10O` = 7, `C8H18` = 18, all with `-R`.

Each generated SMILES is parsed with RDKit and keyed by the first 14
characters of the standard InChIKey, the same connectivity key as the
benchmark. Rank uses one structure per key. The ranker is
`scripts/hose_predict.py`: Morgan spheres r = 4…1, minimum bin count 3,
hybridisation prior as the fallback. The table was rebuilt from
`nmrshiftdb2withsignals.sd` with `random.seed(7)`. Held-out 13C MAE is
3.23 ppm (median 1.73 ppm), the published gate.
Distance to the printed 13C list is the symmetric chamfer in
`hose_predict.chamfer`. Printed shifts are the assignment-parenthesis
numbers used by the locked join, made unique after rounding to 0.01 ppm.
Gold rank is 1 plus the number of other constitutions with a strictly
smaller chamfer. Ties keep the best rank.

An optional filter, reported separately from the headline rank, keeps a
candidate when its symmetry-distinct carbon count (RDKit canonical ranks,
ties not broken) is at least the number of distinct printed 13C shifts, and
when a printed IR band in [1650, 1820] cm⁻¹ requires a carbonyl, a band in
[2200, 2280] requires a nitrile, and a band in both [1480, 1570] and
[1300, 1390] requires a nitro group. Absence of a band eliminates nothing.

A printed list is counted as incompatible with the gold constitution when
the number of distinct printed 13C shifts exceeds the carbon count in the
formula, or exceeds the number of symmetry-distinct carbons in gold. That
test is applied only at scoring time. It is the meaning of "the printed
lists themselves poorly identify the constitution" in the table below.
Separately, gold chamfer is compared with the lookup MAE of 3.23 ppm.
A chamfer above that line means the printed shifts disagree with the shifts
the lookup predicts for gold; a chamfer on or below it means the list matches
gold within the lookup's own error and the rank is carried by other isomers
that match at least as well.

Higher valences are not in the headline `N_iso`. For every formula whose
default `N_iso` is ≤ 20000 and that contains N, S, or P, the run
also counts N-valence-5, S-valence-4, S-valence-6, and P-valence-5
assignments. When every assignment finishes and the sum is still ≤
20000, that union is enumerated and ranked as a sensitivity.

## How many of the 500 were enumerable

Of the 500 molecules, 3/500 have a finished default-valence
`N_iso` ≤ 5000, and 4/500 have a finished
default-valence `N_iso` ≤ 20000.
The chosen cutoff is 20000, so the enumerable set is 4/500.
Finished exact counts above 20000: 38/500.
Proved `N_iso` > 20000 by streaming 20001 structures, without an exact count: 105/500.
Counts still unfinished after that stream: 350/500.
Of those, 350/350 emitted 0 structures before the clock.
The smallest unfinished formula has 15 heavy atoms.
Surge rejected the formula: 3/500.
All 3 rejected formulas end in a charge mark that surge does not parse.
These categories partition the roster: 4 enumerable + 38 exact counts above the cutoff + 105 proved above the cutoff + 350 unfinished + 3 rejected = 500.
The smallest finished exact count above 20000 is 23946 (C6H13NO2, 1/500).
Gold's connectivity key is in the generated pool for 4/4 enumerable
molecules and absent for 0/4.
Ranks below use the molecules whose gold key is in the pool.

## Distribution of gold spectroscopic rank

Denominator: 4 molecules with gold in the surge pool.

| gold rank | count | fraction of ranked |
|---:|---:|---:|
| ≤ 1 | 1 | 1/4 |
| ≤ 3 | 1 | 1/4 |
| ≤ 10 | 2 | 2/4 |
| ≤ 50 | 3 | 3/4 |
| ≤ 100 | 4 | 4/4 |
| ≤ 500 | 4 | 4/4 |
| ≤ 1000 | 4 | 4/4 |
| ≤ 5000 | 4 | 4/4 |
| ≤ 20000 | 4 | 4/4 |

Top 3: 1/4.
Top 10: 2/4.
Top 50: 3/4.
Median gold rank: 9.5.
Best rank: 1. Worst rank: 61.

## Generation miss where the ranker already places gold in the top 10

Among molecules with gold rank ≤ 10, the locked deposit never proposed gold
at k≤3 in 0/2.
On the same 2 molecules the deposit's label is top-1 in 2/2
and proposed-but-not-top-1 in 0/2.
On this slice the deposit already proposed gold at k≤3 whenever the
HOSE chamfer placed gold at rank ≤ 10. The conditional generation-miss
count is 0/2.

## Printed lists on molecules with gold rank worse than 50

Among molecules with gold rank > 50, the printed 13C list is incompatible
with the gold constitution in 0/1.
The list is compatible with gold's carbon count and symmetry, and more than
50 other constitutions still match it at least as well, in 1/1.
Gold chamfer is above the HOSE MAE (3.23 ppm) in 1/1
and at or below that MAE in 0/1.
Incompatible means the printed shift count exceeds the formula's carbon
count or gold's symmetry-distinct carbon count. The complementary count is
ambiguity: the list fits gold's carbon count and symmetry, and it fits more
than 50 other constitutions of the same formula at least as well.
For locked-main:R56 (C7H18Sn), the matched constitution resolves
r=2 2, r=1 5 of its 7 carbons. Gold chamfer is 4.930 ppm
and the best other chamfer is 2.063 ppm.

## Optional printed-list filter

The peak-count and IR rules reject gold in 1/4 ranked molecules.
The kept pool is empty for 1/4 (locked-main:R56): every constitution fails a printed-list rule, so the filter has no ranking left.
Where gold survives the filter (3/4), filtered gold
rank is ≤ 3 in 2/3,
≤ 10 in 3/3, and
≤ 50 in 3/3.
Headline ranks above are the unfiltered chamfer ranks.

## Higher-valence sensitivity

Formulas with default `N_iso` ≤ 20000 that contain N, S, or P:
0.
Unions that finished with `N_iso` ≤ 20000: 0.
Unions over the cutoff: 0.
Unions that did not finish: 0.
No higher-valence union stayed inside the cutoff, so there is no second rank table.

## Reading

The oracle proposer in this diagnostic is exhaustive only inside the cutoff.
That set is 4/500. On it, gold is in the surge pool for 4/4.
Where the HOSE chamfer already places gold at rank ≤ 10, the locked deposit
never proposed gold at k≤3 in 0/2.
Where gold rank is worse than 50, the printed 13C list is incompatible with
the gold constitution in 0/1, and gold's chamfer is above
the lookup MAE in 1/1.
Molecules outside the cutoff are not given a spectroscopic rank. An unfinished
count is not treated as a small `N_iso`.

## Enumerable molecules

| uid | formula | N_iso | pool | gold in pool | gold rank | ≤3 | ≤10 | ≤50 | LLM label | list incompatible | gold chamfer |
|---|---|---:|---:|---|---:|---|---|---|---|---|---:|
| locked-main:R56 | C7H18Sn | 96 | 96 | yes | 61 | no | no | no | top1 | no | 4.930 |
| expand500:R187 | C8H17BrO | 1157 | 1157 | yes | 15 | no | no | yes | top1 | no | 1.023 |
| expand500:R190 | C11H24O | 2426 | 2426 | yes | 1 | yes | yes | yes | top1 | no | 0.308 |
| expand500:R110 | C6H8O2 | 10893 | 10872 | yes | 4 | no | yes | yes | top1 | no | 3.561 |

Pool is the number of distinct connectivity keys ranked. `N_iso` is surge's
count before RDKit parsing. LLM label is the locked deposit: `top1`,
`proposed_not_top1`, or `never`.

## Files

- `roster.py` loads the 500 and checks 227/22/251.
- `run.py` counts, enumerates, ranks, and writes this report.
- `outputs/per_molecule.csv` and `outputs/summary.json` are the numeric source
  of every fraction above.

