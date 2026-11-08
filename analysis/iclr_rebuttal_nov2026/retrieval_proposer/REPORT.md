# IRexp library-search baseline on the locked n=500 roster

This is nearest-neighbour lookup in the public IRexp corpus. The search uses the printed Hill formula and the printed peak lists. It is library search. It is not a trained elucidator, and it is not a replacement of the locked closed-book result 227/500.

## Headline

The locked generation wall on the deposited Claude lists was recomputed before retrieval and matched the published integers: 227/500 exact top-1, 22/500 in the k≤3 pool but not top-1, 251/500 never proposed at k≤3. Recall at k≤3 is 249/500.

Protocol A leaves out the query record only. Recall of the gold InChIKey-14 is 3/500 at k=1, 3/500 at k=3, and 3/500 at k=10. Top-1 is the k=1 rate. Empty proposal lists stay in the denominator.

On the 251 constitutions the closed-book harness never proposed, Protocol A recall is 1/251 at k=1, 1/251 at k=3, and 1/251 at k=10.

After the query row is removed, the formula gallery is empty for 190/500 of all queries and 97/251 of the 251. An empty list is a miss and stays in the denominator.

A second index row with the same gold InChIKey-14 remains inside that formula gallery for 3/500 of all queries and 1/251 of the 251. The same count anywhere in the index, ignoring formula, is 3/500. No second copy lies under a different Hill formula (0 rows). Exact recovery cannot exceed the in-gallery count. Where a second copy is in the gallery (3 queries), it is ranked first for 3/3. 2/3 of those galleries also contain a different constitution; 1/3 contain only the second record.

Protocol B also removes every row of the gold molecule. The formula-matched gallery has size n=500, median 1, quartiles 0 and 3, range 0 to 16 on all 500 and n=251, median 1, quartiles 0 and 2, range 0 to 16 on the 251 (zeros included). A neighbour exists for 309/500 of all queries and 154/251 of the 251. Morgan r=2 Tanimoto of that neighbour versus gold, on queries that have a neighbour, is n=309, median 0.2449, quartiles 0.1486 and 0.6379, range 0.0484 to 0.9545 for the full roster and n=154, median 0.3898, quartiles 0.1564 and 0.7217, range 0.0725 to 0.9545 for the 251.

## Roster and the generation wall

The 500 problems are the locked score_main 194 (clean `benchmark_main` plus every `benchmark_v3` question plus every `benchmark_v2_ctrl` question), plus all 106 deposited Opus answers of the first expansion, plus the first 200 validate-clean expand-500 qids in `headline500_expand200_qids.json` (commit `48fcd30153df5e331fab43cfa514763db8ee3891`). Sensitivity pools n=524 and n=530 are not included.

Gold InChIKey-14 is the unique (Hill formula, IR rounded to 0.1 cm^-1, 13C rounded to 0.01 ppm) join into `data/irexp_resolved/irexp_resolved.jsonl.gz`. On the 194, that join matches the committed answer key. Wall labels use the deposited rank lists at k≤3: raw `M-<qid>` files for the clean main set, `predictions2.jsonl` for v3, v2_ctrl, expand, and expand-500. The rescore reproduced 55/194, 63/106, and 109/200 top-1, and 65/194, 68/106, and 116/200 recall, plus the simple/complex locks 161/248, 66/252, 172/248, and 77/252. Those checks abort the script on failure.

## Index

Source file: `data/irexp_resolved/irexp_resolved.jsonl.gz`, git blob `8115a3c51c0fc7fd780b60c4fd95ae1aba471ae1`. This checkout already contained the structure-linked file, so the public Hugging Face mirror was not re-downloaded. The filter keeps a row when RDKit parses the SMILES, `CalcMolFormula` returns a Hill formula, and at least one of the IR list, the parsed 13C list, or the parsed 1H list is non-empty.

Rows read 43060. Kept 43060. Dropped unparsed SMILES 0, empty formula 0, no comparable peak list 0. Kept rows with IR 43060, with 13C 34147, with parsed 1H 39671. Non-empty 1H fields 39672, of which 1 did not yield a centre inside [-2, 16] ppm (a carbon list stored in the 1H field falls here). Record ids that occur more than once: 0. Stored InChIKey-14 disagrees with RDKit on 0 kept rows. Identity uses the stored key when it is present.

The query row was present in the index for 500/500 queries and was removed before ranking. Protocol A galleries that still contain the query id: 0/500. Protocol A top-1 records equal to the query id: 0/500.

## Distance

Monotone sorted L1 (rectangular Hungarian optimum on the line) of band positions in cm^-1, mean over the shorter list. No intensities.

Symmetric chamfer in ppm, hose_predict.chamfer / specmetrics.chamfer.

Symmetric chamfer on parsed ppm centres. Parsed on 500/500 queries.

Mean of per-channel competition ranks inside the formula-matched gallery. Ties share the minimum rank. Channels with no comparable candidate are dropped. Gold SMILES is not a feature.

The printed 1H string and the IRexp `h_nmr` field are not the same transcription. Where both sides yielded a 1H list (500/500), the query-to-its-own-row 1H chamfer was 0 for 358/500. IR and 13C distances to that same row are 0 by the join, which is why exclusion is by record id rather than by a distance threshold. Gold SMILES is used only to name the InChIKey-14 label and, in Protocol B, to compute Tanimoto after the neighbour has been chosen.

## Protocol A

Hard filter: same Hill formula. Then rank by the mean channel rank. Propose the first k distinct InChIKey-14 values. k is 1, 3, and 10.

| wall class | n | recall@1 | recall@3 | recall@10 | another same InChIKey-14 still in the gallery |
|---|---:|---:|---:|---:|---:|
| all | 500 | 3/500 | 3/500 | 3/500 | 3/500 |
| exact top-1 | 227 | 2/227 | 2/227 | 2/227 | 2/227 |
| in pool, not top-1 | 22 | 0/22 | 0/22 | 0/22 | 0/22 |
| never proposed at k≤3 | 251 | 1/251 | 1/251 | 1/251 | 1/251 |

Cohort slices of the same Protocol A run, not a separate experiment: locked 194 recall@1/@3/@10 1/194, 1/194, 1/194; expand 106 0/106, 0/106, 0/106; expand-500 200-cut 2/200, 2/200, 2/200.

### Same paper or a different paper

Paper identity is the PMC id when `pmcid` or `source_doi` carries one, otherwise the source string. The comparison is between the query row's paper and the paper of the retrieved record.

| retrieved hit | n | same paper | different paper | identifier missing |
|---|---:|---:|---:|---:|
| Protocol A top-1 record, whether or not it is gold | 310 | 122/310 | 188/310 | 0/310 |
| Protocol A top-1 record when it is the gold InChIKey-14 | 3 | 2/3 | 1/3 | 0/3 |
| First gold InChIKey-14 inside the top 10 | 3 | 2/3 | 1/3 | 0/3 |
| Never-proposed query whose k=1 hit is gold | 1 | 1/1 | 0/1 | 0/1 |
| Protocol A top-1 record when it is not gold | 307 | 120/307 | 187/307 | 0/307 |

The top-1 row that is not gold counts formula isomers. A shared paper id on that row is a co-extracted isomer from the query article, not a second copy of the gold constitution. The gold rows are the separate lines above.

A different IRexp record of the same molecule is a real library hit, including a different extraction from the same paper and a later paper that reports the same constitution. That is duplicate publication in the corpus, which library search is supposed to find. It is not evidence that a closed-book generator proposed the structure.

## Protocol B

Every index row with the gold InChIKey-14 is removed, so the gold constitution is absent. The gallery size is the number of remaining formula-matched rows. The neighbour is the best-ranked remaining structure. Tanimoto is Morgan radius 2, 2048 bits, chirality off, between that structure and the gold structure.

| group | n | empty gallery | gallery rows | unique InChIKey-14 in the gallery | neighbour Tanimoto |
|---|---:|---:|---|---|---|
| all | 500 | 191/500 | n=500, median 1, quartiles 0 and 3, range 0 to 16 | n=500, median 1, quartiles 0 and 3, range 0 to 16 | n=309, median 0.2449, quartiles 0.1486 and 0.6379, range 0.0484 to 0.9545 |
| exact top-1 | 227 | 87/227 | n=227, median 1, quartiles 0 and 3, range 0 to 16 | n=227, median 1, quartiles 0 and 3, range 0 to 16 | n=140, median 0.2058, quartiles 0.1385 and 0.4511, range 0.0484 to 0.9091 |
| in pool, not top-1 | 22 | 7/22 | n=22, median 2.5, quartiles 0 and 4, range 0 to 8 | n=22, median 2.5, quartiles 0 and 4, range 0 to 8 | n=15, median 0.3585, quartiles 0.1518 and 0.6386, range 0.0755 to 0.7805 |
| never proposed at k≤3 | 251 | 97/251 | n=251, median 1, quartiles 0 and 2, range 0 to 16 | n=251, median 1, quartiles 0 and 2, range 0 to 16 | n=154, median 0.3898, quartiles 0.1564 and 0.7217, range 0.0725 to 0.9545 |

Quartiles use queries with a neighbour. Empty galleries stay in the gallery-size distribution as 0 and are omitted from the Tanimoto quartiles.

Quartiles use `statistics.quantiles(n=4, method="inclusive")`. The median uses `statistics.median`.

## Leakage

The 500 roster was sampled from IRexp, so a search that leaves the query row in the index retrieves that row and calls it a success. Protocol A removes the query record id. It does not remove other records of the same InChIKey-14. Those remaining records are why exact recovery is possible at all. Where the coverage row above is 0, Protocol A recall is 0 for that query. Protocol B removes the molecule as well and therefore cannot report exact recovery. The two protocols answer different questions and their rates are not interchangeable.

## Paragraph for the paper

As a post-hoc library-search baseline, not a trained model and not a replacement of the closed-book 227/500, we looked up each of the 500 printed formulas in the structure-linked IRexp index and ranked the other records by peak-list distance (43060 rows after the filter; the query row itself was excluded). The gold InChIKey-14 was retrieved for 3/500 at k=1, 3/500 at k=3, and 3/500 at k=10. Of the 251 constitutions the locked harness never proposed, the same lookup recovered 1/251, 1/251, and 1/251. That ceiling is coverage, not rank: a second record of the gold molecule remains in the formula gallery for 3/500 of queries and 1/251 of the 251, and the formula gallery is empty for 190/500. Among the gold top-1 hits, 2/3 share the query's source paper and 1/3 come from a different paper. Holding the gold molecule out, the formula-matched gallery has median size 1 (quartiles 0 and 3; empty galleries included) and the top neighbour's Morgan fingerprint Tanimoto (radius 2) has median 0.2449 on the 309/500 queries that still have a neighbour (n=154, median 0.3898, quartiles 0.1564 and 0.7217, range 0.0725 to 0.9545 on the never-proposed queries that have a neighbour). These figures measure corpus lookup and analog proximity.

## Figure

`fig_recall_at_k.png` plots Protocol A recall@1, @3, and @10 for all 500 and for the 251. Bar labels are the same n/N counts as the table.

## Files

- `run_retrieval.py` — index, both protocols, this report
- `protocol_a_per_query.csv` — one row per query, recall flags, papers
- `protocol_b_per_query.csv` — gallery size and neighbour Tanimoto
- `summary.json` — the integers behind this report
- `fig_recall_at_k.png` and `fig_recall_at_k.pdf`
- `vendor/` — expansion questions, predictions, and the 200-qid cut, pinned to the commit above

## Reproduce

```
python3 analysis/iclr_rebuttal_nov2026/retrieval_proposer/run_retrieval.py
```

Requires RDKit and matplotlib. No network call, no CASE/Surge run, and no paid model API. The script exits before writing scores if the locked wall is not 227/22/251.
