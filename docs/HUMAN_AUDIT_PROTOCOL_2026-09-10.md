# Human audit protocol — IRexp F1 / data quality (2026-09-10)

**Status:** scaffold only. **No audits completed.** Do not cite completion rates,
κ, or pass/fail fractions until Ilkham/Rudra finish scoring and the sheets are
checked in under `data/audit_irexp_f1_20260910/` (to be created when sampling runs).

Audience: **Ilkham Yabbarov** and **Rudra** (independent double-read where noted).
Scope: staged rebuild `data/irexp_rebuild_20260910/` (+ refetch merge outputs),
not the live HF publish.

Related: `docs/REFEREE_F1_REBUILD_2026-09-10.md`, `docs/EXPERT_AUDIT_PROTOCOL.md`
(solver/verifier panel — separate from this dataset audit).

---

## 1. Goals

Close the referee-facing gap on **experimental IR value quality** after the
thousands-separator fix and targeted PMC re-fetch:

1. **Value correctness** — do listed `ir_bands_cm-1` match the source paper’s
   reported IR peaks (within rounding / subset policy)?
2. **Pairing** — is the IR block attached to the correct compound (name / NMR /
   InChIKey), not a neighbour in the SI?
3. **Completeness** — are major reported bands present (esp. ≥1500 cm⁻¹ X–H / C=O),
   or is the row a truncated / fingerprint-only remnant?
4. **Name → structure** — when `smiles` / `inchikey` / `has_structure` is set, does
   the structure match the named compound in the paper (OPSIN/PubChem-level)?
5. **True recall (paper-level)** — on a held-out paper set, what fraction of
   *IR-characterized compounds in the SI* appear as rows in IRexp?

---

## 2. Stratified row audit (n ≈ 200)

### 2.1 Sample design (pre-register before drawing)

| Stratum | Target n | Sampling frame (staged rebuild) | Why |
|---------|----------|----------------------------------|-----|
| A. Thousands-fixed / changed bands | 40 | Rows with `ir_bands_cm-1` ≠ `ir_bands_old_cm-1` after rebuild | F1 remediation check |
| B. Residual `max(band)<1000` | 30 | `max(ir_bands)<1000` on `irexp_reparsed_refetch` | Truncation vs true far-IR / junk |
| C. Refetch-updated | 20 | `ir_refetch_merged=true` | Merge/join correctness |
| D. Refetch-confirmed | 20 | `ir_refetch_confirmed=true` | Confirm “already OK” claim |
| E. Unmatched Chemotion (no PMC) | 30 | `source_doi` Chemotion / empty `pmcid`, sharealike | Non-PMC residual |
| F. Unmatched PMC still unresolved | 20 | Unmatched ∩ not confirmed/merged after refetch | Hard cases |
| G. F2 shared-IR flag | 20 | `ir_shared_in_paper` from quality sidecar | Pairing risk |
| H. F3 table-flatten suspect | 20 | `ir_table_flatten_suspect` | Completeness / order |
| **Total** | **200** | Disjoint as far as possible; if overlap, keep in first stratum listed | |

Suggested seed: `20260910`. Record exact IDs in
`data/audit_irexp_f1_20260910/sample_ids.json` when drawn (script TBD;
do **not** hand-pick).

Balancing constraints (soft): ≥40% `license_pool=commercial`; ≥40%
`has_structure=true`; mix of PMCIDs (≤5 rows/paper in A–D).

### 2.2 Per-row checklist (score sheet columns)

For each sampled `id`, auditor opens the source (PMC HTML/PDF or Chemotion
record) and fills:

| Field | Values | Notes |
|-------|--------|-------|
| `auditor` | Ilkham / Rudra | |
| `source_found` | Y / N / partial | N → stop, mark `block_reason` |
| `bands_match` | exact / subset_ok / mismatch / cannot_tell | subset_ok = all listed bands in paper, paper may list more |
| `truncation_artifact` | Y / N / NA | Y if paper has ≥1000 cm⁻¹ peaks missing because of thousands commas |
| `pairing_ok` | Y / N / unsure | IR belongs to this compound |
| `completeness` | full / major_missing / fingerprint_only / prose_not_list | |
| `name_structure_ok` | Y / N / NA / unsure | NA if no structure fields |
| `severity` | 1–5 | |
| `notes` | free text | cite page/compound label |

**Pass rule (row):** `source_found=Y` AND `bands_match∈{exact,subset_ok}` AND
`pairing_ok=Y` AND (`name_structure_ok∈{Y,NA}`).

Double-read: ≥40/200 rows scored by both auditors; resolve conflicts in a short
reconciliation log (no silent overwrite).

### 2.3 Reporting (fill only after scoring)

> **Table H1.** Stratified IRexp audit (n=200). Pass rate overall and by stratum;
> truncation_artifact rate in B; name→structure error rate in structured subset;
> Cohen’s κ on double-read fields (`bands_match`, `pairing_ok`).
>
> *Numbers intentionally blank until the audit is done.*

---

## 3. True recall on ~50 papers (outline)

### 3.1 Paper draw

- Frame: OA PMCs that contribute ≥1 row to staged `irexp_reparsed` **or** appear
  in `unmatched_priority_pmcids.txt`, year ≥2015, experimental organic/medchem SI
  preferred.
- n ≈ **50** papers, stratified: 20 high-yield (≥10 IRexp rows), 15 medium (3–9),
  15 low/unmatched-heavy (including some zero-IR refetch PMCs).
- Seed `20260910-papers`. Freeze list in `paper_ids.txt` before reading.

### 3.2 Protocol (per paper)

1. Open PMC full text + SI.
2. Enumerate **IR-characterized compounds** (explicit IR / FT-IR / νmax band list
   for a named product). Exclude materials/polymer kinetics prose without a
   compound header.
3. For each such compound, record: label/name, ~3 diagnostic bands, whether an
   IRexp row exists (match by PMC + bands within ±2 cm⁻¹ or documented name).
4. Outcomes: `recalled` / `missed` / `partial` (row exists but wrong pairing or
   badly truncated).

### 3.3 Read-outs (after completion)

- Paper-level recall: mean fraction recalled; micro-averaged compound recall.
- Miss taxonomy: not harvested / extract regex miss / join drop / license filter /
  duplicate collapse.
- Link misses back to extractor follow-ups (ῡ header, spaced thousands, etc.).

> **Table H2.** True recall on n≈50 OA papers — *blank until scored.*

---

## 4. Integrity

- No cherry-picking after seeing outcomes; seed and frames frozen first.
- Auditors must not edit staged jsonl during scoring; notes go in the sheet only.
- Do **not** mark this protocol or the referee rebuild doc as “audit complete”
  without checked-in score sheets.
- No HF / Zenodo publish gated on this audit unless Ilkham explicitly OKs.

## 5. Checklist for kickoff (unchecked)

- [ ] Create `data/audit_irexp_f1_20260910/`
- [ ] Implement `scripts/make_irexp_f1_audit_sample.py` (strata + seed)
- [ ] Draw n≈200 row sample + n≈50 paper list; commit ID lists only
- [ ] Blank Google/Excel/`scoring_sheet.csv` from §2.2 columns
- [ ] Ilkham + Rudra score; reconcile double-read
- [ ] Fill Tables H1/H2; link from `REFEREE_F1_REBUILD_2026-09-10.md`
