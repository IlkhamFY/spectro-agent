# IRexp structure resolution, pass 2 (2026-09-21)

**Result:** structure-linked IRexp records **43,060 → 57,646** (35.5% → 47.5% of 121,233).
Commercial pool structure-linked **28,899 → 40,117**. No record was added, dropped,
re-extracted or had any non-structure field changed; the pass only fills
`smiles` / `selfies` / `inchikey` / `has_structure` on records that had none.

| | before | after | Δ |
|---|--:|--:|--:|
| IRexp records | 121,233 | 121,233 | 0 |
| with structure (`irexp_resolved`) | 43,060 | **57,646** | +14,586 |
| unique InChIKey among structure-linked | — | 54,985 | (12,106 InChIKeys not previously in the corpus) |
| structure-linked with NMR | 40,702 | 47,521 | +6,819 |
| IR + ¹H + ¹³C + structure quadruples | 33,201 | 39,118 | +5,917 |
| structure-linked, commercial pool | 29,263 | 40,117 | +10,854 |
| structure-linked, non-commercial | 7,967 | 10,935 | +2,968 |
| structure-linked, empty/unknown | 3,941 | 4,704 | +763 |
| structure-linked, sharealike | 1,889 | 1,890 | +1 |

Per-pool "before" counts are from the tracked corpus at the parent commit. The Hub's
`resolved_commercial` config showed 28,899 rather than 29,263 because 364 rows that
carry a structure in the Hub `irexp_commercial` file were missing from that config;
the staged `resolved_commercial` below is exactly the rows with an InChIKey (40,117).

## Why pass 1 stopped at 43,060

Pass 1 (`maximize_resolution.py`, Aug 2026) named a record only when the text carried the
SI convention `<IUPAC name> (<label>).` directly before an NMR cluster. 10,065 of the
15,416 source papers had **zero** resolved records although they contribute 51k
IR records: main-text conventions such as `2.2.1. <name> Yield: 78%`,
`<name> 8d White solid`, `<name>, 3ce, was synthesized`, `<name> (trivial name, 1):`
were never captured, and IR-only records (no NMR cluster) were never named at all.
In addition, 14,282 captured names failed OPSIN, mostly for fixable reasons
(locant spaces, glued reference numbers, `(1R*,2R*)` relative stereo).

## What pass 2 does (`scripts/extend_structure_resolution.py`)

1. **Locate** each unresolved record's own data block in the PMC OA S3 plain text
   (`data/cache/pmc_text/`, 13,919 papers): the first 4 shift values of its ¹H/¹³C
   list in order and/or its exact IR band list (F1 bands from the HF file are tried
   too). A band list shared by several blocks or records in the paper is not used.
2. **Search backwards** (≤ 1,500 chars, bounded by the previous record's block) with
   four header patterns — `hdr` (`name (label)`, extended labels such as `5c1`,
   `TD7-Br`, `28-Ts`, `(trivial, 1)`), `lbl` (`name label Yield/colour/mp…`),
   `sec` (numbered heading + name), `was` (`name, label, was synthesized`) — plus the
   names pass 1 had already captured (`ckh`) and the harvest-snapshot names (`snap`).
   A candidate is discarded if another compound's NMR or IR data lies between it and
   the record's block.
3. **Validate**: every candidate string (plus cleaned variants) goes through OPSIN 2.9
   (`allow_acid`, `allow_bad_stereo`; **no** `allow_radicals`). Structures are rejected
   if they contain radicals, isotopes, wildcards, a nonzero net charge, fewer than 5
   heavy atoms, or an extra fragment larger than a simple counter-ion (this catches
   `X diacetate` being read as X + 2 acetic acid).
4. **Gate** against the record's own NMR with the same physics gates as
   `scripts/quarantine_structure_nmr.py` (¹³C peak count ≤ carbons; ¹H integral ≤ H + 2).
   Nearest candidate that parses and passes wins. IR-only records (no NMR to gate
   against) only accept a header-style candidate within 400 chars of the IR block.
5. **Write** an id-keyed sidecar with full provenance, then apply it.

Sentence-chunk fallbacks were implemented, measured (0% precision) and are not shipped.

## Precision check (`structure_additions_2026-09-21.eval.json`)

The finder was run on the 26,810 records that pass 1 had already resolved (papers
with cached text) and its choice compared with the existing InChIKey-14:

| pattern class | chosen | agree (IK-14) |
|---|--:|--:|
| `hdr` | 21,379 | 97.7% |
| `sec` | 1,100 | 97.9% |
| `ckh` (pass-1 names) | 19,742 | 98.9% |
| `snap` (harvest names) | 14,942 | 99.7% |
| all classes, nearest-first | 24,745 | **98.6%** |
| IR-only records (`hdr`) | 119 | 86.6% |

Manual inspection of the disagreements shows the "known" label is itself often wrong:
in the IR-only set 13 of 14 inspected disagreements were pass-1 assigning the *previous*
compound's name to an IR block (e.g. PMC2705134, PMC6259205), which pass 2 gets right.
`lbl` and `was` cannot be measured this way (pass-1 records almost never use those
conventions). Random picks from the new additions were read against the paper text
(two rounds of 16 per class): `lbl` 31/32 correct (the miss was an OPSIN charge artefact
that the validity rules now reject), IR-only 31/32 correct plus 1 plausible but not
verifiable from the text, `sec` 18/18 after the label/salt/IR-guard fixes (4/16 before
them), `hdr` 18/18. These are estimates from reading, not measurements; the IR-only
class in particular has no NMR gate behind it.

Physics gates on the released split: pass-1 rows 1,882/43,060 flagged (4.37%);
pass-2 rows 0/14,586 (gated by construction). 547 + 275 candidates were rejected by
the gates during the run.

## Files

| path | role |
|---|---|
| `scripts/extend_structure_resolution.py` | `eval` / `find` / `apply` sub-commands (this document's numbers) |
| `data/irexp/structure_additions_2026-09-21.jsonl.gz` | **id-keyed sidecar**, 14,586 rows: `id, pmcid, license_pool, smiles, inchikey, selfies, name_raw, name_used, pattern, label, dist_chars, ir_only, location, opsin, gates, rejected_before` — apply to any copy of the corpus by `id` |
| `data/irexp/structure_additions_2026-09-21.eval.json` | precision table above |
| `data/irexp/name_struct_cache_v2.jsonl.gz` | OPSIN results for every candidate string (reruns are offline) |
| `data/irexp/irexp.jsonl.gz`, `irexp_stats.json` | corpus with structures filled |
| `data/irexp_resolved/` | regenerated 100%-structure-linked split (57,646) |
| `data/irexp/licence_pools/` | regenerated via `scripts/split_license_pools.py --write` |
| `data/irexp_rebuild_20260921/hf_publish/` (gitignored, local) | HF commercial files built from the **live Hub files** (F1 bands + F2/F3 flags preserved): `irexp_commercial` 88,545, `irexp_resolved_commercial` 40,117, `train_no_bench_commercial` 39,958 (159 benchmark IK-14 rows excluded), `build_stats.json`, proposed `README.md` |

**Inputs pulled from the Hub** (`ilkhamfy/IRexp`, revision `8db58466e3ddfd2fbe09bd47fdd5eb4cfc3e1975`,
last modified 2026-09-14): `data/irexp_commercial.jsonl.gz` (88,545), `data/irexp_resolved_commercial.jsonl.gz`
(28,899), `data/train_no_bench_commercial.jsonl.gz` (28,753), `README.md`, `NOTICE`,
`LICENCE_REMEDIATION.md`, `data/f1_commercial_build_stats.json`. Kept locally under
`data/cache/hf_irexp_8db58466/` (gitignored). Every Hub id exists in the tracked corpus;
7,622 rows differ only in F1-corrected bands, none in structure.

Reproduce: `python scripts/extend_structure_resolution.py find --hf-commercial data/cache/hf_irexp_8db58466/irexp_commercial.jsonl.gz`
then `apply --sidecar data/irexp/structure_additions_2026-09-21.jsonl.gz --hf-commercial … --hf-revision 8db58466e3ddfd2fbe09bd47fdd5eb4cfc3e1975`.
PMC texts were fetched on 2026-09-20 with S3 version fallback v1→v2→v3 and cached; the
sidecar's `text_version` is therefore `cache` for every row (the exact S3 version was not
recorded). Missing texts are fetched from S3 on demand.

## Not done here (needs Ilkham)

- **Hugging Face upload.** The staged files are not uploaded; `ilkhamfy/IRexp` is Ilkham's.
  The sidecar applies by `id` to his local F1 staging copy too.
- **Manuscript counts.** `scripts/check_manuscript.py` now fails gate A: `docs/PAPER.md`,
  `docs/scientific_data/scientific_data.tex`, `docs/COVER_LETTER.md`, `docs/ESI.md`,
  `README.md` and the Sci Data QC tables cite 43,060 / 40,702 / 33,201 / 28,899.
  Only `README.md` and `data/irexp_release/README_HF.md` were updated here.
- **`data/irexp_release/train|test`** and `train_no_bench*.jsonl.gz` (non-HF) were left
  as released; regenerating them changes benchmark-contamination bookkeeping.
- **Pass-1 IR-only assignments.** The eval suggests some pass-1 IR-only rows carry the
  previous compound's structure (off-by-one IR attachment). Worth a targeted audit.
- 6 pass-1 rows (hypervalent-iodine compounds) have `selfies: null`; unchanged.
