# Sci Data + ICLR split — multi-agent orchestration

**Track 0 owner:** freeze + plan (this document)  
**Repo:** IlkhamFY/spectro-agent  
**Strategy change:** stop treating the live JCIM-shaped combined manuscript as the submission target. Split into:

1. **Nature Scientific Data** — IRexp Data Descriptor (data object only)
2. **ICLR** — IRSpectra-Bench + recall/verification diagnosis (research paper)

Authoritative fitness audit (read-only context): `docs/irexp_scientific_data_audit.md`.

---

## 1. Goal

| Venue | Object | Must include | Must exclude |
|-------|--------|--------------|--------------|
| **Scientific Data** | IRexp Data Descriptor | Background & Summary, Methods, Data Records, Technical Validation, Usage Notes, honest multi-licence Data/Code Availability | LLM top-1 / recall / verification results, diagnosis narrative, “resource + bench + diagnosis” framing |
| **ICLR** | IRSpectra-Bench + diagnosis | Blind bench contract, scorer, decomposable metrics, LLM/probe results, limitations on elucidation | Full Data Descriptor Methods/Data Records rewrite; dumping the entire corpus schema |

**Order preference:** Sci Data first (or simultaneous with clear complementary disclosure), then ICLR citing the Sci Data / Zenodo DOI. Do **not** burn a JCIM “resource+benchmark+diagnosis” deposit that already publishes the dataset DOI before Sci Data is ready.

---

## 2. Track map

| Track | Name | Owns | Creates / edits | Forbidden |
|-------|------|------|-----------------|-----------|
| **T0** | Freeze / plan | This orchestration + archive | `docs/archive/*`, `docs/SPLIT_ORCHESTRATION.md`, layout stubs | Editing live combined paper as the new manuscripts |
| **T1** | Licence remediation | PMC licence truth | PMC join → NC/other segregate; stamp `license` on records; fix `data/NOTICE`, HF card, `.zenodo.json`; honest pool files / `split_license_pools` on **real** licences | Claiming all PMC-OA is CC-BY; editing T2/T3 manuscripts except to supply final counts |
| **T2** | Sci Data manuscript | Data Descriptor | **NEW files only** under `docs/scientific_data/` | `docs/archive/**`, `docs/paper.tex`, `docs/PAPER.md`, `docs/iclr/**` |
| **T3** | ICLR manuscript | Bench + diagnosis | **NEW files only** under `docs/iclr/` | `docs/archive/**`, `docs/paper.tex`, `docs/PAPER.md`, `docs/scientific_data/**` |

### T0 deliverables (done on `cursor/split-orchestration-9a67`)

- [x] Freeze `docs/archive/combined_PAPER.md` ← copy of `docs/PAPER.md`
- [x] Freeze `docs/archive/combined_paper.tex` ← copy of `docs/paper.tex`
- [x] Document that `docs/paper.pdf` remains the combined reading-copy build; `scripts/build_pdf.py` still points at `docs/PAPER.md` as archive reference
- [x] This file: `docs/SPLIT_ORCHESTRATION.md`
- [x] Empty layout dirs: `docs/scientific_data/`, `docs/iclr/`

### T1 scope (licence remediation)

Blockers before Sci Data can quote final redistributable counts:

1. Join all PMC accessions in the release to machine-readable licences (EuropePMC / PMC OA commercial vs non-commercial vs other).
2. Segregate NC / empty / other from any commercial CC-BY pool; stamp every record.
3. Update `data/NOTICE`, Hugging Face card (`data/irexp_release/README_HF.md` / publish path), `.zenodo.json` for honest multi-licence metadata (Chemotion = CC-BY-SA; PMC = mixed).
4. Physical or clearly tagged pool files; do not leave `split_license_pools.py` assuming “non-Chemotion ⇒ CC-BY”.
5. Soften or remove blanket “PMC-OA = CC-BY-4.0” language everywhere it still appears (release docs / HF — **not** by rewriting the frozen archive).

Reference: audit §B–C and §F.3 in `docs/irexp_scientific_data_audit.md`.

### T2 scope (Scientific Data)

Write a true Data Descriptor under `docs/scientific_data/`:

- Start: `docs/scientific_data/SCIENTIFIC_DATA.md`
- Later: venue TeX/PDF builds local to that directory (do not overwrite `docs/paper.pdf`)
- Sections: title (Sci Data rules), abstract (data + reuse, no findings), Background & Summary, Methods (exact sources, licence filtering, Chemotion), Data Records (schema, files, no summary-stat dumping), Technical Validation (enlarge beyond n=60 where possible), Usage Notes, Data/Code Availability
- Cite peers (NMRexp, computational IR–NMR Sci Data sets); foreground **band lists**, not full absorbance traces
- Cross-cite the forthcoming ICLR paper as complementary research; no pasted diagnosis tables

### T3 scope (ICLR)

Write the research paper under `docs/iclr/`:

- Start: `docs/iclr/ICLR_PAPER.md`
- Later: ICLR-style TeX/PDF local to that directory
- May **draft immediately** from `docs/archive/combined_PAPER.md` (and optionally `docs/paper.pdf` as visual reference)
- Keep: IRSpectra-Bench design, InChIKey scorer, recall vs verification, model results, probes, limitations
- Point dataset details at Sci Data / Zenodo / HF; do not paste the Data Descriptor
- Cross-cite Sci Data (placeholder DOI until minted)

---

## 3. Dependencies

```text
T0 (freeze + plan) ──► unblocks T1, T2, T3 in parallel on file layout

T1 (licences) ──► T2 final counts / Data Records / Usage Notes
                 └──► Zenodo / HF re-issue (human mint still required)

T3 drafts from archive ──► no wait on T1
T3 final dataset citations ──► prefer Sci Data DOI + remediated HF (T1+T2)

Neither T2 nor T3 may edit:
  docs/archive/**
  docs/PAPER.md
  docs/paper.tex
  scripts/build_pdf.py   (leave combined reading-copy pipeline alone)
```

| Agent needs | Wait for | Can start without |
|-------------|----------|-------------------|
| T2 outline / Methods draft | — | Final licence counts (use “pending remediation” placeholders) |
| T2 final numbers & Availability | **T1** | — |
| T3 full draft | Archive only | T1, T2 |
| T3 camera-ready dataset cite | T2 DOI / Zenodo | — |

---

## 4. File layout

### Frozen combined (read-only)

```text
docs/archive/
  README.md                 # freeze notes
  combined_PAPER.md         # frozen docs/PAPER.md
  combined_paper.tex        # frozen docs/paper.tex

docs/paper.pdf              # combined reading-copy PDF (live path; archive reference)
docs/PAPER.md               # DO NOT edit for split manuscripts
docs/paper.tex              # DO NOT edit for split manuscripts
scripts/build_pdf.py        # still builds combined PDF from PAPER.md
```

### New papers (write here only)

```text
docs/scientific_data/          # Track 2 ONLY
  SCIENTIFIC_DATA.md           # primary authoring source (create in T2)
  # later: scientific_data.tex, scientific_data.pdf, figures/, refs as needed

docs/iclr/                     # Track 3 ONLY
  ICLR_PAPER.md                # primary authoring source (create in T3)
  # later: iclr_paper.tex, iclr_paper.pdf, figures/, refs as needed
```

Shared supporting material (figures, ESI, protocols) may be **copied or referenced** into track dirs as needed; do not delete shared `docs/figures/` assets other tracks still need. Prefer copy-into-track for venue-specific plates.

Orchestration + audit (all tracks may read):

```text
docs/SPLIT_ORCHESTRATION.md          # this file
docs/irexp_scientific_data_audit.md  # fitness / licence / dual-pub audit
docs/SUBMISSION.md                   # historical JCIM checklist — superseded for venue plan by this split
```

---

## 5. Dual-publication rules

| Rule | Detail |
|------|--------|
| **Sci Data = data only** | No hypothesis tests, no LLM accuracy tables, no “diagnosis” abstract. Complementary research OK if disclosed. |
| **ICLR = bench + diagnosis** | Dataset is cited, not re-described as a second Data Descriptor. |
| **Cross-cite** | Each paper cites the other (or “submitted / in preparation” placeholders). Different titles, abstracts, and contribution lists. |
| **No substantial overlap** | ICLR forbids substantially similar concurrent submissions. Do not paste large Methods/Data Records blocks into ICLR or diagnosis into Sci Data. |
| **DOI order** | Prefer Sci Data / Zenodo as the canonical dataset identifier before (or with) ICLR. Avoid a prior JCIM resource paper that already exhausts the dataset story. |
| **Licence honesty** | Both papers must match T1-remediated licence language; never reassert blanket PMC CC-BY. |

---

## 6. Human blockers (cannot be invented by agents)

| Item | Needed by | Notes |
|------|-----------|-------|
| **ORCID iDs** | Both manuscripts | Placeholders remain in archive author block; authors must confirm (esp. corresponding author) |
| **Zenodo DOI mint** | Sci Data Data Availability; ICLR dataset cite | Mint after T1 licence metadata is honest; multi-licence deposit |
| **Funding / acknowledgements** | Both | Empty `— AUTHORS` section in combined paper; PI supplies text |
| **Venue confirmation** | PI | Sci Data + ICLR replaces prior JCIM-primary plan in `docs/SUBMISSION.md` |
| **Expert-chemist audit** | Optional for ICLR; not core Sci Data | Protocol frozen; formally deferred — do not claim completed |

Agents leave `[TODO: …]` markers; do not fabricate DOIs, ORCIDs, or grant numbers.

---

## 7. Success criteria checklist

**Status (2026-08-26):** **T0–T3 done** on `main`. Audit closeout (`cursor/scidata-audit-closeout-9a67`): HF remirror + TV pack + Methods exactness done. Remaining: Zenodo mint / ORCID / funding (human) + polish.

### Track 0 — done

- [x] Archive copies exist and match freeze-time `PAPER.md` / `paper.tex`
- [x] Orchestration doc committed; layout dirs present
- [x] Live combined pipeline left intact (`build_pdf.py` → `PAPER.md`)

### Track 1 — done

- [x] Per-PMCID licence join complete for release accessions
- [x] NC / other segregated; commercial pool redistributable under stated licence(s)
- [x] Every release record stamped with `license`
- [x] `data/NOTICE`, HF card, `.zenodo.json` corrected (no blanket PMC CC-BY)
- [x] Counts exportable for T2 Data Records — commercial **87,617**; NC 20,938; SA 1,897; empty/unknown 10,781; total 121,233 (`LICENCE_REMEDIATION.md`, `data/irexp/licence_pools/`)

### Track 2 — done (manuscript draft)

- [x] `docs/scientific_data/SCIENTIFIC_DATA.md` exists with full Data Descriptor sections
- [x] No diagnosis / LLM result tables in abstract or body
- [x] Final counts consistent with T1 pools
- [x] Technical Validation reports integrity checks (transcription + structure consistency and/or recall sample as agreed)
- [x] Cross-cite ICLR; Data Availability ready for Zenodo DOI when minted
- [x] Did **not** modify `docs/archive/**`, `docs/PAPER.md`, or `docs/paper.tex`

### Track 3 — done (manuscript draft)

- [x] `docs/iclr/ICLR_PAPER.md` exists with bench + diagnosis focus
- [x] Dataset described by citation to Sci Data / Zenodo / HF, not a second Data Descriptor
- [x] Metrics, scorers, and frozen predictions still mechanically checkable where claimed
- [x] Cross-cite Sci Data; no substantial text overlap with T2
- [x] Did **not** modify `docs/archive/**`, `docs/PAPER.md`, or `docs/paper.tex`

### Remaining (post-split)

- [x] Hugging Face remirror of stamped pools / card (`scripts/publish_hf.py`, 2026-08-26 on `cursor/scidata-audit-closeout-9a67`)
- [ ] Zenodo DOI mint (multi-licence deposit; commercial primary) — **human**
- [ ] Human: ORCID confirmation + funding / acknowledgements
- [x] Technical Validation pack: transcription n=200; recall proxy n=40; full-resolved quarantine
- [x] Methods exactness: S3 harvest date 2026-06-07; flat keys (not oa_comm walk); Chemotion author-curated ingest; Scrapling fence
- [ ] Polish both manuscripts before submission
- [ ] Titles and abstracts clearly disjoint (spot-check at camera-ready)
- [ ] PI aligned on Sci Data → ICLR order (or simultaneous complementary disclosure)

---

## 8. Branch conventions

| Track | Suggested branch pattern |
|-------|--------------------------|
| T0 | `cursor/split-orchestration-9a67` (this work) |
| T1 | `cursor/licence-remediation-<suffix>` |
| T2 | `cursor/scientific-data-manuscript-<suffix>` |
| T3 | `cursor/iclr-manuscript-<suffix>` |

Merge T0 to `main` early so all tracks share the archive + layout. T1/T2/T3 work on feature branches; do not force-push over the frozen archive.

---

## 9. Quick start for sibling agents

1. Read this file and `docs/irexp_scientific_data_audit.md` §F.4.
2. Confirm you are on the correct track (T1 / T2 / T3).
3. **Read** `docs/archive/combined_PAPER.md` for content; **write** only under your track directory (T1 may also touch `data/`, NOTICE, HF, Zenodo metadata, licence scripts).
4. Never edit `docs/PAPER.md`, `docs/paper.tex`, or `docs/archive/*`.
5. Leave human blockers as TODO; wire final counts from T1 into T2 before Sci Data “final” claims.
