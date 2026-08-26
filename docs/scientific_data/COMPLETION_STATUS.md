# IRexp split completion status — honest audit

**Repo:** IlkhamFY/spectro-agent  
**Verified against:** branch `cursor/scidata-audit-closeout-9a67` (closeout pass 2026-08-26)  
**Audit source:** `docs/irexp_scientific_data_audit.md`  
**Date of this status:** 2026-08-26  
**Mode:** closeout — agent-addressable items done; human-only leftovers called out

---

## Blunt answers to the four user questions

| # | Ask | Verdict | One-line why |
|---|---|---|---|
| **(1)** Per-article licence join + NC segregation + HF/NOTICE correction | **DONE** | Disk stamps/pools/NOTICE/PAPER/README/Zenodo metadata done; **HF remirror executed 2026-08-26** with commercial/NC/SA/empty pools + honest card |
| **(2)** Technical Validation pack | **DONE** (agent scope) | Transcription n=200; recall proxy n=40 (S3 path); full-resolved quarantine 1,882/43,060; rates in SCIENTIFIC_DATA.md + `qc_structure_nmr.json`. Expert human structure/recall still optional |
| **(3)** Sci Data manuscript skeleton | **DONE** (draft) / **not submission-ready** | Methods exactness + Chemotion + Scrapling fence + TV pack written. Zenodo DOI, ORCID, funding remain human |
| **(4)** ICLR-facing cut + cross-cite | **DONE** (draft) | Unchanged; Sci Data DOI still “in prep.” |

**Has everything in the audit been addressed?** Agent-addressable severity list (HF remirror, thicker TV, Methods exactness, Chemotion, quarantine, Scrapling fencing): **yes**. Human-only: Zenodo mint, ORCID, funding/acks.

---

## (1)–(4) detail

### (1) Licence join + NC + HF/NOTICE — **DONE**

| Piece | Status | Evidence |
|---|---|---|
| Join / stamps / pools / NOTICE / PAPER / README | **DONE** | On `main` + this branch |
| `.zenodo.json` | **PARTIAL** | Multi-licence description; DOI not minted (human) |
| HF remirror | **DONE** | `scripts/publish_hf.py` 2026-08-26; Hub has `irexp_commercial.jsonl.gz` etc.; card no longer blankets PMC as CC-BY-4.0 |

### (2) Technical Validation pack — **DONE** (agent)

| Check | Status |
|---|---|
| Transcription n=60 | **DONE** (560/560) |
| Transcription n=200 | **DONE** — 2250/2261 bands (99.51%); 196/200 records (98%) |
| Extraction-recall proxy n=40 | **DONE** — S3 path; list-level recall proxy 1.0; `data/audit/extraction_recall_proxy.json` |
| Structure–NMR sample n=500 | **DONE** (3.4% / 3.4%) |
| Full-corpus quarantine | **DONE** — 1,882/43,060 (4.37%); ¹³C 3.49%; ¹H 2.88%; `data/audit/structure_nmr_quarantine.jsonl.gz` |
| IR window full corpus | **DONE** (0 OOR) |
| Expert structure n≥100 | **NOT DONE** / deferred (optional) |
| Human recall mark-up | **NOT DONE** (proxy shipped instead) |

### (3) Sci Data skeleton — **DONE as draft**

Methods now document: harvest date **2026-06-07**, flat S3 keys (not `oa_comm` walk), post-hoc Europe PMC licence join aligned with commercial/NC intent, Chemotion author-curated Quill-delta parse (`chemotion_to_irexp.py`), Scrapling non-OA fence. Remaining human: Zenodo DOI, ORCID, Acknowledgements.

### (4) ICLR cut — **DONE as draft** (unchanged this pass)

### Archive / Scrapling

| Check | Status |
|---|---|
| Archive freeze | **DONE** |
| Scrapling fencing | **DONE** — Methods fence + `fetch.py` module docstring + optional Scrapling import (QC works without it) |

---

## Full audit action checklist

### Minimum before submission (audit §F.3 Must)

| # | Action | Status |
|---|---|---|
| M1 | Licence join + pools | **DONE** |
| M2 | Correct docs + stamp + HF | **DONE** (HF remirrored) |
| M3 | Mint Zenodo | **NOT DONE** — human |
| M4 | Data Descriptor draft | **DONE** (draft) |

### Should (reviewer survival)

| # | Action | Status |
|---|---|---|
| S5 | Corpus-wide structure–NMR; quarantine | **DONE** |
| S6 | Extraction-recall audit | **DONE** (automatic proxy n=40; human optional) |
| S7 | Chemotion method detail | **DONE** (author-curated lists; not algorithmic peak-pick) |
| S8 | Enlarge transcription n≥200 | **DONE** |

### Nice

| # | Action | Status |
|---|---|---|
| N9 | Expert structure n≥100 | **NOT DONE** |
| N10 | Peer compare in Background | **DONE** |

### Factual corrections (audit §C)

| # | Action | Status |
|---|---|---|
| C1–C3, C5 | Stop blanket CC-BY; join; stamp | **DONE** |
| C4 | Zenodo multi-licence metadata | **PARTIAL** — notes done; mint human |
| C6 | Re-issue HF | **DONE** |

---

## Remaining blockers (honest)

### Critical — human only

1. **Zenodo DOI mint** (multi-licence deposit; commercial primary).

### Medium — human only

2. ORCID (esp. corresponding author) + funding/acknowledgements.

### Optional polish

3. Expert structure spot-check n≥100; true human extraction-recall mark-up.  
4. Sci Data TeX/template polish; ICLR camera-ready after Sci Data DOI.

**No longer blockers:** live HF CC-BY overclaim; thin TV (n=60-only); missing Methods harvest/`oa_*` story; Chemotion underspecification; missing quarantine artefact; Scrapling Methods silence.

---

## Bottom line

Agent-addressable Sci Data audit closeout is **complete** on this branch. Submit-blocking leftovers are **Zenodo + ORCID/funding** (humans at submission).
