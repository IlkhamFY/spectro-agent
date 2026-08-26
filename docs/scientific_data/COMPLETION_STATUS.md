# IRexp split completion status — honest audit

**Repo:** IlkhamFY/spectro-agent  
**Verified against:** `origin/main` @ `6461ae7` (2026-08-26)  
**Audit source:** `docs/irexp_scientific_data_audit.md`  
**Date of this status:** 2026-08-26  
**Mode:** report-only (no fixes applied)

---

## Blunt answers to the four user questions

| # | Ask | Verdict | One-line why |
|---|---|---|---|
| **(1)** Per-article licence join + NC segregation + HF/NOTICE correction | **PARTIAL** | Join, stamps, pools, NOTICE, Zenodo *metadata*, PAPER/README language are **done on disk**. **HF Hub is NOT remirrored** — live card still says “PMC = CC-BY-4.0”; commercial pool file **404** on Hub. |
| **(2)** Technical Validation pack | **PARTIAL** | Beyond n=60 transcription: structure–NMR sample (n=500) + full-corpus IR window exist and are reported. Extraction recall, enlarged transcription, full `quality.py` quarantine, expert structure audit: **still planned/deferred**. |
| **(3)** Sci Data manuscript skeleton | **DONE** (draft) / **not submission-ready** | Full Data Descriptor sections exist in `docs/scientific_data/SCIENTIFIC_DATA.md` (+ PDF). Zenodo DOI, ORCID, funding, and several Methods exactness / QC items remain open. |
| **(4)** ICLR-facing cut + cross-cite | **DONE** (draft) | `docs/iclr/ICLR_PAPER.md` exists with explicit Sci Data companion cross-cites and dual-pub boundary in `docs/iclr/README.md`. Not conference TeX; Sci Data DOI still “in prep.” |

**Has everything in the audit been addressed?** **No.** Licence *truth on disk* is largely fixed; public HF overclaim, Zenodo mint, and most “Should” QC items remain.

---

## (1)–(4) detail

### (1) Licence join + NC + HF/NOTICE — **PARTIAL**

| Piece | Status | Evidence |
|---|---|---|
| `scripts/join_pmc_licences.py` | **DONE** | On `main`; Europe PMC join |
| Stamps on `irexp.jsonl.gz` | **DONE** | Sampled 5k rows: `license` null = 0; pools present |
| `data/irexp/licence_pools/` | **DONE** | commercial 87,617; NC 20,938; SA 1,897; empty_unknown 10,781; other 0 |
| `pmc_licence_summary.json` | **DONE** | Counts match NOTICE |
| `data/NOTICE` | **DONE** | Honest multi-pool narrative; no blanket PMC=CC-BY |
| PAPER / README licensing | **DONE** | Corrected counts + stamps |
| `.zenodo.json` | **PARTIAL** | Multi-licence *description* + notes; single metadata `license=cc-by-4.0` for primary; **DOI not minted** |
| HF card / `publish_hf.py` | **PREPARED ONLY** | Local `README_HF.md` + script ready; **Hub lastModified 2026-08-24**; siblings lack commercial pools; live README: “119,345 … (CC-BY-4.0)”; live NOTICE still has old TODO |
| HF remirror executed | **NOT DONE** | Needs `HF_TOKEN` write upload |

### (2) Technical Validation pack — **PARTIAL**

| Check | Status |
|---|---|
| Transcription fidelity n=60 (560/560) | **DONE** (unchanged; still only n=60) |
| Structure–NMR consistency audit | **PARTIAL** — sample n=500 reported in `qc_structure_nmr.json` (¹³C 3.4%, ¹H 3.4%); **not** full-corpus quarantine |
| Extraction-recall human audit | **NOT DONE** (explicitly Planned) |
| Full-corpus `quality.py` quarantine | **NOT DONE** (Planned; module exists, not applied as release filter) |
| Enlarge transcription n≥200 | **NOT DONE** |
| Expert structure spot-check n≥100 | **NOT DONE** / deferred |
| IR physical window full corpus | **DONE** (0 / 1,360,866 OOR) |

### (3) Sci Data skeleton — **DONE as draft**

Required Descriptor sections present: Title, Abstract, Background & Summary, Methods, Data Records, Technical Validation, Usage Notes, Data/Code Availability, author contributions, competing interests. Title ≤110 chars; abstract ~130 words (data-focused). Cross-cite to ICLR; NMRexp / USPTO peers cited. Remaining: Zenodo DOI placeholders, ORCID TODO, Acknowledgements empty, Chemotion peak-picking thin, no S3 harvest date / `oa_comm` vs `oa_noncomm` package exactness.

### (4) ICLR cut + cross-cite — **DONE as draft**

`ICLR_PAPER.md` (~420 lines) keeps diagnosis/bench content; repeatedly points dataset Methods/TV to Sci Data companion; dual-pub checklist in `docs/iclr/README.md`; `docs/SUBMISSION.md` §9 adopts Sci Data + ICLR (JCIM no longer primary). No ICLR TeX build; Sci Data DOI still “in preparation.”

### Archive / Scrapling (process checks)

| Check | Status |
|---|---|
| `docs/archive/combined_PAPER.md` + `combined_paper.tex` | **DONE** (frozen at T0) |
| Live `docs/PAPER.md` / `paper.tex` “untouched” | **PARTIAL** — orchestration said don’t edit; T1 still lightly updated live PAPER (and earlier paper.tex) for licence honesty. Archive freeze itself intact. |
| Scrapling / non-OA fencing in Methods | **PARTIAL** — Sci Data Methods: released path = PMC-OA S3 + Chemotion; “development adapters … outside construction path.” Code still prominently Scrapling/StealthyFetcher; not retired/moved to legacy. |

---

## Full audit action checklist

Status key: **DONE** / **PARTIAL** / **NOT DONE**

### Minimum before submission (audit §F.3 Must)

| # | Action | Status | Notes |
|---|---|---|---|
| M1 | Join all 15,416 PMCIDs → licence; build commercial / NC / other pools; exclude NC from CC-BY commercial | **DONE** | + empty_unknown excluded |
| M2 | Correct PAPER / NOTICE / README / HF / Zenodo licence language; stamp every record | **PARTIAL** | Disk + NOTICE + PAPER + README + Zenodo JSON done; **HF Hub still overclaims** |
| M3 | Mint Zenodo with honest multi-licence + file inventory | **NOT DONE** | Metadata prepared; DOI `[TODO: 10.5281/zenodo.XXXXXXX]` |
| M4 | Write true Data Descriptor (strip diagnosis) | **DONE** (draft) | Skeleton complete; polish / human blockers remain |

### Should (reviewer survival)

| # | Action | Status |
|---|---|---|
| S5 | Corpus-wide structure–NMR consistency; report & quarantine | **PARTIAL** — sample reported; no quarantine pass |
| S6 | Extraction-recall audit n=30–50 papers | **NOT DONE** |
| S7 | Document Chemotion peak-picking method | **PARTIAL** — “derived from deposited FT-IR”; no algorithm/pipeline detail |
| S8 | Enlarge transcription audit n≥200 or error taxonomy | **NOT DONE** |

### Nice

| # | Action | Status |
|---|---|---|
| N9 | Expert structure spot-check n≥100 | **NOT DONE** |
| N10 | Compare to NMRexp / computational IR–NMR in Background | **DONE** |

### Factual corrections (audit §C)

| # | Action | Status |
|---|---|---|
| C1 | Stop claiming all PMC-OA = CC-BY-4.0 | **PARTIAL** — fixed in-repo; **not** on live HF |
| C2 | Join + segregate commercial / NC / other | **DONE** |
| C3 | Stamp `license`; separate files / real `split_license_pools` | **DONE** |
| C4 | Fix Zenodo metadata (not only cc-by-4.0 while SA/mixed) | **PARTIAL** — notes + description; single field still `cc-by-4.0` for primary |
| C5 | Soften PAPER “licence stamp” until stamps exist | **DONE** (stamps exist; language updated) |
| C6 | Re-issue HF card after remediation | **NOT DONE** |

### Risk mitigations (audit §E)

| Risk | Mitigation | Status |
|---|---|---|
| Legal redistributability | Join; segregate NC; re-release; correct docs | **PARTIAL** — re-release to HF pending |
| Scrapling optics | Document PMC/Chemotion-only; fence scraper | **PARTIAL** — narrative fenced; code not retired |
| Incomplete provenance stamps | Stamp; separate files; Methods licence subsection | **DONE** (in-repo) |
| Band lists vs spectra | Foreground in Sci Data | **DONE** |
| Formula/structure errors | quality audit; quarantine; report rates | **PARTIAL** |
| Scoop / peers | Position IR band-list niche; cite | **DONE** in draft |
| Dual publication mishandle | Sci Data data-only; ICLR diagnosis; order | **DONE** as strategy/docs |
| Zenodo/HF metadata wrong | Fix before archival DOI | **PARTIAL** / **NOT DONE** on HF |
| Chemotion SA contamination | Physical split; Usage Notes | **DONE** |

### Sci Data section expectations (audit §A)

| Section | Status |
|---|---|
| Title rewrite (Sci Data rules) | **DONE** |
| Abstract rewrite (data + reuse) | **DONE** |
| Background & Summary | **DONE** |
| Methods (exact sources + licence filter) | **PARTIAL** — sources + licence; missing harvest date / OA package dirs |
| Data Records | **DONE** |
| Technical Validation | **PARTIAL** — above peer bar than n=60-only, still below NMRexp |
| Usage Notes | **DONE** |
| Data Availability (DOI) | **PARTIAL** — HF link; Zenodo TODO |
| Code Availability | **DONE** |

### Two-paper split (audit §F.4)

| Item | Status |
|---|---|
| Complementary Sci Data + ICLR strategy | **DONE** (`SUBMISSION.md`, orchestration) |
| Prefer Sci Data first / clear separation | **DONE** (documented; not executed as pubs) |
| Cross-cite both ways | **DONE** in drafts |
| Do not burn JCIM resource+DOI before Sci Data | **DONE** as venue plan (JCIM superseded as primary) |
| ICLR ≠ paste Data Descriptor | **DONE** in draft boundary |

---

## Remaining blockers for Sci Data acceptance (by severity)

### Critical (submit-blocking if Nature/legal checks public claims)

1. **Hugging Face still publicly overclaims PMC as CC-BY-4.0** (card + NOTICE; no commercial pool file). Remirror with `scripts/publish_hf.py` + stamped pools **before** submission / review pointing at HF.
2. **Zenodo DOI not minted** — required for Data Availability / persistent archive.

### High (likely reviewer / editorial pushback)

3. **Technical Validation still thin vs NMRexp:** no extraction-recall sample; transcription still n=60; no full-corpus quality quarantine (only n=500 structure–NMR sample + IR window).
4. **Methods exactness gaps:** S3 harvest date/version; which PMC OA packages (`oa_comm` / `oa_noncomm` / other) were actually walked.
5. **Scrapling/Stealth still in-tree** without a hard “legacy / not used for release” fence in code layout — Methods prose only.

### Medium

6. Chemotion peak-picking method under-specified for “how 1,888 lists were derived.”
7. Structure error rates reported but **not quarantined** into a filtered release artifact.
8. Human blockers: ORCID (esp. corresponding author), funding/acknowledgements.
9. Zenodo single-licence metadata field vs multi-file reality — workable with notes, but editors may ask for clearer deposit packaging.

### Lower / polish

10. Sci Data draft polish (abstract word-count gate at submission, Nature template/TeX if required).
11. ICLR TeX + final Sci Data DOI fill-in after mint.
12. Optional expert structure n≥100.

---

## Bottom line

- **(1) No** — not fully done until HF is remirrored (in-repo licence work is largely done).  
- **(2) No** — partial TV pack only.  
- **(3) Yes** for skeleton draft; **No** for submission-complete Descriptor.  
- **(4) Yes** for ICLR-facing cut + cross-cite draft; **No** for camera-ready.  

**Audit fully addressed?** **No.** Highest remaining public risk: **live HF licence overclaim**.
