# IRexp split completion status — honest audit

**Repo:** IlkhamFY/spectro-agent  
**Verified against:** branch `cursor/scidata-accept-ready-9a67` (TV + scale pass 2026-08-27)  
**Audit source:** `docs/irexp_scientific_data_audit.md`  
**Peer review:** `docs/scientific_data/PEER_REVIEW_SIMULATION.md`  
**TV/scale methods:** `docs/scientific_data/TV_AND_SCALE_PASS.md`  
**Date of this status:** 2026-08-27  
**Mode:** TV gap close + Crossref commercial-pool recovery; human-only leftovers unchanged

---

## Blunt answers

| # | Ask | Verdict | One-line why |
|---|---|---|---|
| **(1)** Per-article licence join + NC segregation + Crossref empty recovery | **DONE** | Commercial **88,545** (+928); empty 8,963; pools sum 121,233 |
| **(2)** Technical Validation pack | **DONE** (agent scope) | n=200 transcription; recall n=120 + Wilson CIs; chemist-proxy n=280; full quarantine. Human expert audits still deferred |
| **(3)** Sci Data manuscript | **DONE** (near submit) / **not fully submission-ready** | TeX+MD synced; Zenodo DOI, ORCID, funding remain human |
| **(4)** ICLR-facing cut + cross-cite | **DONE** (draft) | Dual-publication fence restated in Limitations |

**Has everything actionable been addressed?** Agent-addressable TV/scale/peer-review items: **yes**. Human-only: Zenodo mint (data-only), ORCID, funding/acks. Optional: expert structure n≥100; human recall mark-up; HF remirror.

---

## Remaining blockers (honest)

### Critical — human only

1. **Zenodo DOI mint** for a **data-only** IRexp deposit (commercial primary + SA companion).
2. **ORCID** — especially corresponding author I. Yabbarov (Vargas-Hernández ORCID known: `0000-0002-5559-6521`).
3. **Acknowledgements / funding** text confirmation.

### Optional polish

4. Expert human structure spot-check n≥100; true human extraction-recall mark-up.  
5. HF remirror after Crossref licence stamp (local release/pools updated 2026-08-27).  
6. Dedicated overview figure (tables currently carry composition).

---

## TV headline numbers (automated)

| Metric | n | Rate |
|---|---:|---|
| Transcription (n=200) | 2,261 bands | 99.51% |
| Recall proxy list-level | 858 lists / 120 papers | 0.9848 (Wilson [0.9743, 0.9911]) |
| Chemist-proxy joint pass | 280 | 0.9679 (Wilson [0.9401, 0.9830]) |
| Structure-physics pass (within proxy) | 182 | 0.9725 |
| Quarantine (full resolved) | 43,060 | 4.37% flagged |

---

## Scale delta

Total / structure-linked / quadruples **unchanged**. Commercial pool **87,617 → 88,545** via Crossref/EPMC empty-licence recovery.

---

## Bottom line

Agent-addressable Sci Data TV + commercial-pool strengthening is **complete** on this branch. Submit-blocking leftovers remain **Zenodo (data-only) + ORCID + funding**.
