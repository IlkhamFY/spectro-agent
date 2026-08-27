# Simulated Nature Scientific Data peer review — IRexp Data Descriptor

**Manuscript:** `docs/scientific_data/scientific_data.tex`  
**Working notes:** `SCIENTIFIC_DATA.md`, `COMPLETION_STATUS.md`, `LICENCE_REMEDIATION.md`  
**Prior audit:** `docs/irexp_scientific_data_audit.md`  
**Review date:** 2026-08-27  
**Title under review:** *IRexp: A database of experimental infrared band lists from open literature*  
**Mode:** Full simulated desk screen + three reviewers + statistical/TV auditor  
**NMRexp comparator:** Wang et al., *Sci. Data* 12, 1956 (2025), doi:10.1038/s41597-025-06245-5  

Severity legend: **Blocker** (reject / hold until fixed) · **Major** (must address for acceptance) · **Minor** (should fix) · **Nit** (polish).

Status column after remediation pass: **Fixed** / **Deferred (human)** / **Accepted risk** / **Won’t fix**.

---

## Overall editorial recommendation (synthesis)

**Decision if submitted today:** *Major revision required* (not desk-reject).

**Scope fit:** Strong as a Data Descriptor of redistributable **experimental IR band lists** (not absorbance traces), with multimodal optional NMR strings and partial structure linkage. Closest peers (NMRexp; USPTO computational IR–NMR) establish journal appetite for spectral *list* resources. IRexp’s wedge is IR-focused, PMC-OA + Chemotion provenance, and explicit commercial / NC / SA licence pools.

**Why not accept yet:** (1) no persistent archival DOI (Zenodo pending); (2) Technical Validation is honest but clearly below NMRexp’s manual n≈300 + replicate MAE bar — Limitations must say so without apology-by-omission; (3) ORCID / funding incomplete; (4) several schema / docs inconsistencies (Chemotion missing `inchikey`/`has_structure` fields; README still says equal contribution; Data Records omits stamped licence provenance fields present on disk).

**Dual-publication:** Companion ICLR diagnosis manuscript is appropriately excluded from analyses here. Risk remains if Zenodo/HF marketing still bundles IRSpectra-Bench model results into the *same* Sci Data archival story without a data-only deposit narrative.

---

## 1. Editor-in-Chief / handling editor — desk screen

### Scope & article type

| ID | Severity | Finding | Location | Recommended fix | Status |
|---|---|---|---|---|---|
| E1 | — | Object (band lists from OA literature + ELN) fits Data Descriptor; no hypothesis tests / LLM tables in TeX body. | Whole MS | Keep fence; do not import IRSpectra-Bench results. | OK |
| E2 | Major | Persistent identifier for the dataset is still “DOI pending / at proof”. Sci Data expects a resolvable repository DOI (or clear review-access plan) at or before acceptance. | `scientific_data.tex` Data Availability / Access (~L379–385, L493–502); MD TODO placeholders | Mint Zenodo (commercial primary + SA companion); replace TODOs. **Human-only.** | Deferred (human) |
| E3 | Major | Acknowledgements are placeholder (“will be added at proof”). Editors often bounce incomplete funding statements. | TeX L541–543; MD Acknowledgements | Authors confirm funding / institutional text. **Human-only.** | Deferred (human) |
| E4 | Major | ORCID not present in TeX author block (esp. Yabbarov TODO in MD). | MD HTML comment L11–15; TeX authors L36–37 | Add ORCIDs at submission. **Human-only.** | Deferred (human) |
| E5 | Minor | Title follows NMRexp pattern and stays ≤110 chars (74); “agentic” correctly kept out of title. | TeX L28–32 | Retain. | OK |
| E6 | Minor | Abstract (~139 words) is data-centric; mentions companion manuscript without results — good. Could explicitly name **limitations of TV vs full absorbance libraries**. | TeX abstract L49–67 | One clause on band-list / TV scope. | Fixed |
| E7 | Minor | Keywords include “experimental spectra”, which invites absorbance-spectrum misreading. | TeX L69–70 | Prefer “band lists”, “peak lists”, “FAIR”, “licence pools”. | Fixed |
| E8 | Major | README outline still says “equal contribution” though TeX correctly dropped that footnote. | `README.md` L44 | Align with TeX (both corresponding; no equal-contrib). | Fixed |
| E9 | Minor | No manuscript figures (composition / pipeline). Sci Data peers usually ship ≥1 overview figure. Not a hard desk reject if tables carry the load, but weakens first impression. | TeX (no `\includegraphics`) | Optional composition figure from frozen counts; or accept table-only with Usage Notes clarity. | Fixed (`fig_irexp_overview`) |
| E10 | Major | `.zenodo.json` at repo root still describes combined IRexp **+** IRSpectra-Bench diagnosis deposit and lists three creators including Sondhi. If used as the Sci Data archival record, that conflates tracks. | `.zenodo.json` | Sci Data deposit must be **data-only** metadata; document human mint path; do not fabricate DOI. | Fixed (docs) / Deferred (human mint) |

**Desk verdict:** Send out after confirming licence honesty (already remediated in body) and with explicit note that Zenodo/ORCID/funding are author actions at submission.

---

## 2. Reviewer 1 — spectroscopy / cheminformatics domain expert

| ID | Severity | Finding | Location | Recommended fix | Status |
|---|---|---|---|---|---|
| R1-1 | — | Clear positioning vs NIST/SDBS (absorbance / view-only) and vs computational USPTO IR–NMR. | Background L74–90 | Keep. | OK |
| R1-2 | Major | Positioning vs NMRexp undersells *difference of object* (IR band lists; smaller scale; no SI-PDF OCR pipeline) and underspecifies *why IR lists still matter* for agents without sounding like size competition. | Background L83–100 vs NMRexp 3.3M | Tighten: complementary modality; not a size claim; agent tool-input use case already present — add explicit “orders of magnitude smaller; different object” sentence. | Fixed |
| R1-3 | Major | Chemotion Methods claim RDKit → InChIKey + SELFIES, but released Chemotion JSON rows use InChIKey only as `id` and lack `inchikey` / `has_structure` keys (PMC rows have both). Interoperability footgun. | Methods L178–184; Data Records table L282–298; on-disk Chemotion rows | Backfill `inchikey` (=`id`) and `has_structure=true` on Chemotion rows; document `license_*` / `pmcid` / `source` fields. | Fixed |
| R1-4 | Minor | Structure coverage 35.5% is fine if Usage Notes insist on `irexp_resolved` for supervised tasks — already present; strengthen that OPSIN failures are expected for trivial/trade names. | Structure resolution L231–239; Usage Notes | One sentence on name→structure failure modes. | Fixed |
| R1-5 | Major | Technical Validation has **no expert structure audit** (NMRexp: 98% skeleton correct on n=300 manual). Quarantine rates (~4.4%) are physics-consistency flags, not structure truth. | TV L419–436; QC table L445–458 | Add explicit Limitations subsection; keep “Optional / deferred” but elevate as known gap vs NMRexp. | Fixed |
| R1-6 | Minor | Median bands 9 (PMC) vs 39 (Chemotion) needs one caution: denser ≠ more complete vibrational assignment; Chemotion is author-curated ELN lists. | Data Records L375–377 | Clarify in Usage Notes. | Fixed |
| R1-7 | Minor | IR window [350, 4000] cm⁻¹ is a necessary but weak physical check (no intensity, no solvent, no ATR vs transmission metadata). | TV L438–441 | State as limitation. | Fixed |
| R1-8 | Nit | Citation `yabbarov2026irspectra` is “ICLR … in preparation” — acceptable if no results leaked. | `references.bib` | Keep; ensure no accuracy numbers appear in Descriptor. | OK |
| R1-9 | Minor | Abstract says “optionally with ¹H/¹³C NMR shifts” — NMR fields are author *strings*, not parsed peak tables like NMRexp. | Abstract; Data Records | Say “author-reported NMR strings” once in Abstract or Data Records. | Fixed |

---

## 3. Reviewer 2 — FAIR / licence / repository / reproducibility

| ID | Severity | Finding | Location | Recommended fix | Status |
|---|---|---|---|---|---|
| R2-1 | — | Licence remediation narrative is now honest: commercial 88,545 / NC 21,823 / SA 1,897 / empty 8,963 / other 5; pools sum to 121,233. Matches `pmc_licence_summary.json` (Crossref recovery). | Tables; LICENCE_REMEDIATION.md | Keep; do not re-blanket CC-BY. | OK |
| R2-2 | Blocker | No minted dataset DOI. Findability (F in FAIR) incomplete for journal archival. | Data Availability | Human Zenodo mint with multi-licence description. | Deferred (human) |
| R2-3 | Major | Data Records field table omits `pmcid`, `license_raw`, `license_source`, `source` (Chemotion), which exist on disk and matter for provenance joins. | TeX table `tab:fields` | Extend schema table. | Fixed |
| R2-4 | Major | Harvest reproducibility: date 2026-06-07 and S3 flat keys documented; good. Still missing explicit **esearch query string** (or pointer to frozen query file) so a third party can re-discover the PMCID set. | Methods Discovery L157–172, L196–209 | Cite script + note that `seen_papers.txt.gz` is the frozen discovery set (re-running esearch will drift). | Fixed |
| R2-5 | Minor | Code Availability lists scripts but not `join_pmc_licences.py` in the principal list (mentioned in Methods). | Code Availability L515–527 | Add join script to the principal list. | Fixed |
| R2-6 | Major | HF path claimed public with stamped pools — accept as done per COMPLETION_STATUS; re-users still need clear “full dump ≠ single licence” warning in Usage Notes (partially present). | Usage Notes L461–491 | Strengthen agentic licence-filter bullet (already started). | Fixed |
| R2-7 | Minor | Interoperability: JSONL + SMILES/SELFIES/InChIKey is fine; no JSON Schema / frictionless datapackage checked into `docs/scientific_data/`. | Data Records | Optional schema note pointing at field table + example row in QC pack. | Fixed (example fields + note) |
| R2-8 | Nit | Overleaf-safe: no symlinks under `docs/scientific_data/` — confirmed. | Tree | Keep. | OK |
| R2-9 | Major | Commercial vs NC vs SA pools: table is clear; Usage Notes must forbid treating ShareAlike Chemotion rows as CC-BY when combining corpora. Present but can be bolder. | Usage Notes | Bold SA remix rule. | Fixed |

---

## 4. Reviewer 3 — adversarial skeptic (NMRexp comparison)

**NMRexp bar (published):** ~3.3M experimental NMR records from ~200k SI PDFs (2010–2024); manual n=300 (metadata ~100%, skeleton 98%); heteronuclei extra n=200; replicate MAE ~0.026 ppm (¹H) / ~0.206 ppm (¹³C); Zenodo DOI; rich spectral annotations (multiplicities, *J*, solvent).

| ID | Severity | Finding | Location | Recommended fix | Status |
|---|---|---|---|---|---|
| R3-1 | Major | Scale disparity will be used as a novelty attack. Manuscript already avoids “largest IR DB” claims — good — but must **explicitly** say IRexp is not competing with NMRexp on size and is not an NMR resource. | Background | Add comparative paragraph: complementary IR band-list niche; NMRexp remains the NMR list peer. | Fixed |
| R3-2 | Blocker (perception) / Major (substance) | TV strength gap is the real acceptance risk: transcription n=200 automatic re-fetch ≠ NMRexp’s human PDF cross-check; recall is automatic proxy n=40; no skeleton audit; no replicate MAE analogue for IR (harder for sparse band lists). | TV entire section | Honest Limitations; do not inflate proxy metrics; optional human audits remain deferred. | Fixed (Limitations) / Deferred (human audits) |
| R3-3 | Major | “Spectra” wording anywhere (keywords, casual prose) will be attacked given title “band lists”. | Keywords; audit Chemotion historical wording | Scrub misleading “spectra” where it means absorbance curves. | Fixed |
| R3-4 | Major | Dual-publication / salami risk with ICLR companion: Descriptor correctly excludes results, but citing “forthcoming ICLR” plus shipping `train_no_bench` invites “is the interesting science elsewhere?” defense. | Background L124–133; Usage Notes | Keep; add one sentence that Descriptor’s contribution is the **dataset + provenance + licence pools**, not elucidation claims. | Fixed |
| R3-5 | Minor | Chemotion 1,888 is small; adversarial view: “ELN garnish”. Methods already justify denser lists — keep and note they are 100% structure-resolved. | Chemotion paragraph | Note all Chemotion rows are structure-linked. | Fixed |
| R3-6 | Nit | Title parallel to NMRexp invites direct comparison — intentional and locked; ensure abstract never claims superiority. | Title | Locked; OK. | OK |

**Adversarial bottom line:** Acceptable niche if Limitations are blunt and Zenodo exists. Without DOI + Limitations, expect “revise to match Sci Data TV culture” or reject-after-review.

---

## 5. Statistical / Technical Validation auditor

| ID | Severity | Finding | Location | Recommended fix | Status |
|---|---|---|---|---|---|
| S1 | — | Counts consistent across TeX, MD, `qc_structure_nmr.json`, `pmc_licence_summary.json` (121,233; pools; 43,060; 1,882 quarantine). | Multiple | Keep gated. | OK |
| S2 | Minor | Transcription n=200: 2,250/2,261 bands (99.51%), 196/200 records (98%). Report **what failed** (4 records / 11 bands) at least qualitatively if artefacts exist. | TV; `extraction_audit_n200.json` | Summarize failure mode if available in audit JSON. | Fixed (if present) / note unknown |
| S3 | Major | Recall proxy: list-level recall 1.0 on released lists, but 4/40 papers show *extra* re-extracted lists (258 re-extract vs 248 released matched 244). This is curation/dedup, not pure recall — wording must stay careful (already mostly careful). | TV L405–417; `qc_structure_nmr.json` | Align TeX with JSON (`reextract_lists_matched` 244/258) explicitly. | Fixed |
| S4 | Major | Quarantine 1,882/43,060 is diagnostic-only; release not filtered. Usage Notes say “optionally drop” — for supervised IR→structure, recommend **default drop** unless user accepts noise. | Usage Notes L478–481 | Strengthen recommendation. | Fixed |
| S5 | Minor | Sample n=500 rates (3.4%) ≈ full-corpus rates (3.49% / 2.88%) — good internal consistency; state that explicitly. | TV | One sentence. | Fixed |
| S6 | Major | No confidence intervals / power discussion for n=200 transcription — optional for Sci Data but adversarial reviewers may ask. | TV | State seed and that CI not claimed; descriptive fidelity only. | Fixed |
| S7 | — | IR OOR 0/1,360,866 — strong, narrow check. | TV | Keep + Limitations. | OK |
| S8 | Minor | `qc_structure_nmr.json` is the machine-readable pack — cite it as the frozen numbers source of truth for the Descriptor. | TV intro | Already cited; reinforce in Limitations. | Fixed |

---

## Cross-cutting factual inconsistencies (pre-fix)

| ID | Severity | Inconsistency | Fix | Status |
|---|---|---|---|---|
| X1 | Major | README “equal contribution” vs TeX no equal-contrib | Fix README | Fixed |
| X2 | Major | Chemotion rows lack `inchikey`/`has_structure` vs Methods/Data Records | Backfill + schema table | Fixed |
| X3 | Minor | MD Background thinner on agentic framing than TeX (TeX L92–100) | Sync MD | Fixed |
| X4 | Minor | MD Abstract still has Zenodo TODO bracket — OK if marked human | Keep TODO; COMPLETION_STATUS honest | Fixed (status) |
| X5 | Major | Field table incomplete vs on-disk keys | Extend table | Fixed |
| X6 | Nit | `references.bib` includes ChemDataExtractor unused in TeX | Leave (harmless) or drop | Nit accepted |

---

## Sci Data acceptance criteria scorecard

| Criterion | Assessment |
|---|---|
| Novelty / need vs NIST, SDBS, NMRexp, computational IR–NMR | **Pass with revision** — niche clear if NMRexp comparison tightened |
| Object clarity: band lists ≠ absorbance spectra | **Pass** — strengthen keywords / Limitations |
| Section completeness (B&S, Methods, Data Records, TV, Usage, Code, Data Avail.) | **Pass** — add Limitations (under Usage or TV) |
| FAIR (F/A/I/R) | **Partial** — F blocked on Zenodo DOI; A/I/R largely OK after schema fix |
| Licence clarity (commercial / NC / SA) | **Pass** after Track 1 remediation |
| Provenance / harvest reproducibility | **Pass with minor** — freeze `seen_papers` as discovery truth |
| TV vs NMRexp | **Below bar; honest Limitations required** |
| Overclaim / dual-publication | **Manageable** if data-only Zenodo + no bench results |
| Abstract / title / keywords | **Title OK; keywords need scrub** |
| Figures / tables | **Tables strong; figures weak** |
| Reproducibility of scripts | **Pass** (MIT repo) |
| Count consistency | **Pass** |

---

## Prioritized remediation checklist

### P0 — Blockers (human unless noted)

1. **[Human]** Mint Zenodo DOI for **data-only** IRexp deposit (commercial primary + SA companion; NC/empty labelled). Update TeX/MD Access + Data Availability.  
2. **[Human]** Confirm ORCID (Yabbarov) + Vargas-Hernández ORCID in submission metadata.  
3. **[Human]** Replace Acknowledgements placeholder with real funding text.

### P1 — Majors (agent-addressable)

4. Add **Limitations** subsection (TV vs NMRexp; no expert skeleton audit; band lists ≠ spectra; sparse metadata; structure coverage; licence mix).  
5. Strengthen Background NMRexp / novelty positioning (complementary, not larger).  
6. Extend Data Records schema (`pmcid`, `license_raw`, `license_source`, `source`; Chemotion heterogeneity).  
7. Backfill Chemotion `inchikey` + `has_structure` for schema uniformity.  
8. Align recall-proxy wording with `qc_structure_nmr.json` (244/258 matched lists).  
9. Fix README equal-contribution leftover; sync SCIENTIFIC_DATA.md; update COMPLETION_STATUS.  
10. Keywords scrub “experimental spectra”; abstract NMR-strings wording.  
11. Document Sci Data Zenodo must not reuse combined IRSpectra-Bench `.zenodo.json` as-is.

### P2 — Minors

12. Discovery reproducibility note (`seen_papers` freeze).  
13. Code Availability: add `join_pmc_licences.py`.  
14. Usage Notes: default-recommend quarantine filter; SA remix; Chemotion density caveat; OPSIN failure modes.  
15. TV: sample≈full-corpus consistency sentence; descriptive (non-CI) fidelity note.  
16. Rebuild PDF; verify title IRexp + no equal-contrib footnote.

### P3 — Deferred / accepted risk

17. Expert structure spot-check n≥100 (optional human).  
18. True human extraction-recall mark-up (optional human).  
19. Dedicated graphical overview figure (nice-to-have; tables carry counts).  
20. Do not edit frozen `docs/paper.tex` / `docs/PAPER.md` as Sci Data SoT.

---

## Finding counts (this simulation)

| Severity | Count |
|---|---:|
| Blocker | 3 (all human: Zenodo, ORCID-as-submission-meta, funding — ORCID/funding often treated Major at desk; listed Blocker for submit-ready bar) |
| Major | 18 |
| Minor | 14 |
| Nit | 4 |

*Post-remediation accounting appears at the end of this file after the fix pass.*

---

## Post-remediation status (updated after Phase 2)

| Bucket | Count | Notes |
|---|---:|---|
| Blocker fixed by agent | 0 | Cannot mint DOI / invent ORCID / invent funding |
| Blocker deferred (human) | 3 | Zenodo DOI; ORCID (esp. Yabbarov); Acknowledgements/funding |
| Major fixed | 15 | Limitations, NMRexp positioning, schema, Chemotion backfill, recall wording, README, keywords, Usage Notes, Zenodo-track docs, etc. |
| Major deferred (human audits) | 3 | Expert skeleton audit; human recall mark-up; actual Zenodo mint (also Blocker) |
| Minor fixed | 12 | |
| Minor accepted / deferred | 2 | Full graphical plate optional; unused bib entry |
| Nit addressed or accepted | 4 | |

**PDF rebuilt:** yes (`scripts/build_scientific_data_pdf.py`).  
**Title still contains IRexp:** yes.  
**Equal-contribution footnote:** still absent.
