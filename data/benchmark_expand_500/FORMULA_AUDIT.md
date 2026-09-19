# Formula audit of the n=500 expansion deposits

Run on the deposits in `raw/` against the formulas in `questions2.jsonl`:

```
python scripts/audit_expand500_formulas.py data/benchmark_expand_500
```

This is **not** a scoring pass. It uses no answer key and says nothing about
whether a candidate is *right*. It only asks whether the solver answered the
question it was asked.

A deposit is **BAD** when *none* of its three candidate SMILES reproduces the
molecular formula stated in the question. Charge bookkeeping is normalised:
a candidate also counts as matching when its heavy-atom counts agree and its
hydrogen count differs only by the charge it carries, so a question quoting an
anion (`C11H16NO3S2-`) is answered by either the anion or its neutral acid.
Three candidates that all have the wrong formula carry no information about the
model's chemistry, so such a deposit has to be re-solved rather than scored as
a miss. The script exits non-zero when the BAD list is non-empty, so it can be
wired into a pre-merge check.

## Current result

| | count |
|---|---:|
| deposits audited | **230** |
| deposits with at least one formula-matching candidate (`n_ok`) | **230** |
| deposits with no formula-matching candidate (`n_bad`) | **0** |
| candidates that fail to parse in RDKit | 0 |
| deposits carrying fewer than 3 candidates | 0 |

**`n_bad == 0`. No qid remains bad.** Every one of the 230 deposits answers the
compound its question asks about.

## What the first run found

The first pass over this round flagged **18** BAD deposits:

```
R74, R80, R81, R82, R83, R84, R91, R92, R93, R94,
R95, R96, R97, R98, R99, R100, R101, R102
```

All 18 were byte-identical to the corresponding entries in
`data/benchmark_expand/predictions2.jsonl` — the **n=106 expansion round**, a
different draw that reuses the same `R<nn>` qid namespace. Their formulas
matched that round's `questions2.jsonl` exactly, not this round's:

| qid | formula in this round's question | formula the deposit answered (n=106 round) |
|---|---|---|
| R74 | C15H19FN4O | C17H18ClNO5 |
| R80 | C15H21N3O6S3 | C24H16N2O |
| R81 | C19H26O3 | C14H14S4 |
| R82 | C16H20O6 | C14H12FNO2 |
| R83 | C21H42O4 | C10H11ClN4S |
| R84 | C24H25N5O2S2 | C14H20O2 |
| R91 | C11H12O2 | C12H11BrFN3OSe |
| R92 | C27H30N2O | C24H28N2O |
| R93 | C12H17BFNO2 | C14H15NO4 |
| R94 | C15H10FN3O2S2 | C17H13N3O2S |
| R95 | C19H17N3O | C10H7Br2FO |
| R96 | C12H14N4O2S | C11H9FN4O3 |
| R97 | C17H17N3OS | C33H27N9O8 |
| R98 | C18H30N2O3 | C9H10O3 |
| R99 | C10H7N7 | C21H38O |
| R100 | C20H21N3O5 | C12H11N3O5 |
| R101 | C11H10Br2O2 | C17H18N4O2 |
| R102 | C16H20O4 | C32H45N9O6 |

`STATUS.md` records this batch as "originally written to
`data/benchmark_expand/raw/` by mistake and relocated to this round's `raw/`".
The relocation was the mistake: those replies were answers to the n=106
questions and belonged where they were. Moving them here did not lose the n=106
round's data — it is intact in that round's `predictions2.jsonl` — but it left
this round with 18 deposits answering the wrong compounds. R55 and R78 were
moved in the same batch but are genuine answers to this round's questions and
passed the audit unchanged.

## Repair

Each of the 18 was re-solved blind from `questions2.jsonl` alone — spectra and
formula only, no key, one compound per agent, `claude-opus-5-thinking-high`,
three candidates each, RDKit formula check in-solver — and the deposit in
`raw/single_<qid>.json` was overwritten. No scoring was run and
`answers2.jsonl` remains withheld.

A cross-check confirms none of the 230 deposits is still a verbatim copy of an
`data/benchmark_expand/predictions2.jsonl` entry.

## Re-running

Re-run after any further deposit:

```
python scripts/audit_expand500_formulas.py data/benchmark_expand_500
```
