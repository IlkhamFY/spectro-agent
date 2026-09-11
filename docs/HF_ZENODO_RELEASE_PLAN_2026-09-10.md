# HF + Zenodo release plan — referee M1 (2026-09-10)

**Status:** plan only. **Do not publish** to Hugging Face or Zenodo until Ilkham OK.
**Related:** docs/REFEREE_F1_REBUILD_2026-09-10.md, docs/HUMAN_AUDIT_PROTOCOL_2026-09-10.md,
docs/scientific_data/LICENCE_REMEDIATION.md, docs/scientific_data/ZENODO_DATA_ONLY_CHECKLIST.md.

Code/rebuild staging root (gitignored local): data/irexp_rebuild_20260910/.

---

## 1. Dataset of record

**Primary redistributable artifact** = commercial CC-BY / CC0 pool
(license_pool == "commercial") **after F1 rebuild + targeted PMC refetch merge**.

| Policy | Value |
|--------|-------|
| Full research corpus on disk | keep 
=121233 (multi-licence, stamped) |
| Zenodo / Sci Data primary | commercial pool only |
| ShareAlike companion | Chemotion + rare PMC SA (sharealike) |
| NC* | separate labelled file; **not** in commercial deposit |
| empty / unknown / other(ND) | exclude from commercial; optional labelled files |

F1 changes band lists only; licence stamps are unchanged by the rebuild. Pool sizes
below are **real counts** from staged irexp_reparsed_refetch.jsonl.gz
(dry-run JSON: data/irexp_rebuild_20260910/commercial_pool_dryrun_20260910.json).

| Pool | Records |
|------|--------:|
| **commercial** | **88545** |
| non_commercial | 21823 |
| sharealike | 1897 |
| empty_unknown | 8963 |
| other (CC-BY-ND) | 5 |
| **total** | **121233** |

Commercial structure-linked (irexp_resolved_reparsed_refetch): **28899** / 43060.

---

## 2. Stage paths (data/irexp_rebuild_20260910/)

| Artifact | Role |
|----------|------|
| irexp_reparsed_refetch.jsonl.gz | curated corpus after F1 + refetch merge (**publish source**) |
| irexp_resolved_reparsed_refetch.jsonl.gz | structure-linked |
| 
elease_{train,pretrain_ir}_reparsed_refetch.jsonl.gz | release splits (bands updated; **no** license* columns — join via id) |
| 
elease_{test,train_no_bench}_reparsed.jsonl.gz | release splits (no refetch delta) |
| *_ir_quality_flags.jsonl.gz | F2/F3 sidecars (flag-only tonight) |
| 
ebuild_stats.json, 
efetch/merge_stats*.json | machine stats |
| unmatched_* | residual inventory |
| commercial_pool_dryrun_20260910.json | this session’s pool counts |

**Before HF:** materialise licence pools from the refetch curated file (same
scripts/split_license_pools.py / join pattern as data/irexp/licence_pools/),
writing e.g. licence_pools_f1/ under the stage root — do **not** overwrite
live data/irexp/licence_pools/ until publish gate.

Release configs that lack license_pool must either (a) re-stamp from curated
by id, or (b) document that commercial filtering uses the commercial pool file,
not the raw release JSONL.

---

## 3. Hugging Face publish steps (Ilkham; no auto-publish)

Target: https://huggingface.co/datasets/ilkhamfy/IRexp

1. Freeze stage SHA / tag that matches uploaded bytes.
2. Rebuild pool gzips from irexp_reparsed_refetch.jsonl.gz (commercial / NC / SA / empty / other).
3. Rebuild irexp_resolved (+ optional 	rain_no_bench* if bands must match F1).
4. Upload via scripts/publish_hf.py **or** huggingface-cli upload (needs HF_TOKEN locally; never commit token).
5. **Keep licence fields** on every row (license, license_pool, source_doi / pmcid).
6. **Separate configs** for NC and empty/unknown (already in data/irexp_release/README_HF.md); do not fold them into commercial.
7. **Fix card** (README_HF.md → Hub README.md):
   - YAML license: keep cc-by-4.0 **and** cc-by-sa-4.0.
   - Tables: commercial **88545** (post-F1 same pool size; bands updated).
   - Warn: ll / full irexp.jsonl.gz is multi-licence; training default = commercial.
   - Note F1 thousands-separator rebuild + refetch merge date; link referee rebuild doc.
   - Add F2/F3 policy sentence once chosen (§5).
   - Zenodo DOI line: leave TODO until PI mint (§4) — **no invented DOI**.
8. Smoke-load: load_dataset("ilkhamfy/IRexp", "commercial") length == 88545.

**Do not** overwrite production Hub until card + pool files reviewed.

---

## 4. Zenodo deposit checklist (PI mint; no DOI invented)

Use **data-only** Sci Data deposit — **not** repo-root .zenodo.json combined archive.
Follow docs/scientific_data/ZENODO_DATA_ONLY_CHECKLIST.md.

- [ ] Creators / affiliations / ORCID confirmed by PI
- [ ] Title stub: IRexp: experimental infrared band lists from open literature (data release)
- [ ] Primary file: F1 commercial pool gzip; metadata license=cc-by-4.0
- [ ] Companion: ShareAlike file; description states CC-BY-SA-4.0
- [ ] NC / empty / other: omit from commercial artifact **or** labelled optional files only
- [ ] Upload NOTICE, LICENCE_REMEDIATION.md, pool summary JSON
- [ ] Related identifiers: GitHub IlkhamFY/spectro-agent; HF ilkhamfy/IRexp; forthcoming Sci Data descriptor
- [ ] **Mint DOI** (PI) → paste into TeX / MD / CITATION.cff / HF card
- [ ] Tag git commit matching uploaded bytes
- [ ] Do **not** upload IRSpectra-Bench predictions / leaderboards into this deposit

.zenodo.json description still cites stale combined-archive pool numbers in places
(e.g. 87617); refresh on next metadata edit to **88545 / 21823 / 1897 / 8963**
(aligned with LICENCE_REMEDIATION.md).

---

## 5. F2 / F3 flag drop policy (options)

Sidecars: ir_shared_in_paper (F2), ir_table_flatten_suspect (F3).
Tonight’s rebuild keeps **all rows**; flags only.

Counts on staged curated (irexp_reparsed flags × refetch commercial):

| Scope | F2 | F3 | F2∨F3 |
|-------|---:|---:|------:|
| all curated (121233) | 20666 | 6086 | — |
| commercial (88545) | 18651 | 3154 | 21075 |

| Option | Behaviour | Commercial n if applied now | Notes |
|--------|-----------|----------------------------:|-------|
| **A. Flag only (default)** | ship all rows; document sidecars / columns | 88545 | reversible; preferred until human audit |
| **B. Exclude F2∨F3 from commercial publish** | drop flagged from commercial file only | 67470 | aggressive; keep full corpus + flagged file |
| **C. Exclude F3 only** | drop table-flatten suspects | 88545−3154 = 85391 | milder completeness filter |
| **D. Exclude F2 only** | drop shared-IR-in-paper | 88545−18651 = 69894 | pairing-risk filter |

Recommendation: **A** until HUMAN_AUDIT_PROTOCOL strata G/H scored; then choose B–D
with audited FP rates. Never silently drop without manuscript + card note.

---

## 6. Manuscript counts that wait on HF publish

Do **not** edit TeX/MD headline numbers until Hub (and Zenodo, if cited) match staged bytes.

| Count / claim | Waits on | Notes |
|---------------|----------|-------|
| Commercial pool **88545** (and NC/SA/empty) | HF commercial config (+ Zenodo primary) | already true in LICENCE_REMEDIATION / README_HF; confirm post-F1 upload |
| Band-quality claims (max&lt;1000 residual, PMC6268696, rows changed) | HF files that include F1 bands | cite rebuild_stats / merge_stats after publish |
| Structure-linked / quadruple / train_no_bench sizes if bands-only change | HF resolved + release configs | sizes unchanged; values change |
| F2/F3 rates or “filtered commercial n” | chosen §5 policy **and** matching Hub file | blank in manuscript until policy locked |
| Zenodo DOI / Data Availability | PI mint | CITATION.cff DOI still TODO |
| Human-audit pass rates / κ / true recall | audit sheets checked in | protocol scaffold only |
| .zenodo.json stale 87617-style copy | metadata refresh (optional with mint) | not a manuscript blocker alone |

Gate A provenance (119345 PMC + 1888 Chemotion) is licence-join invariant — not blocked on F1 HF.

---

## 7. Explicit non-actions (this session)

- No HF upload / no Hub overwrite
- No Zenodo mint / no invented DOI
- No production overwrite of data/irexp/*.jsonl.gz or licence_pools/
- HUMAN_AUDIT + REFEREE F1 docs remain scaffold / rebuild record only
