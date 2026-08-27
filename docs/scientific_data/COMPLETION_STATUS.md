# IRexp split completion status — honest audit

**Repo:** IlkhamFY/spectro-agent  
**Verified against:** branch `cursor/scidata-accept-ready-9a67` (peer-review remediation 2026-08-27)  
**Audit source:** `docs/irexp_scientific_data_audit.md`  
**Peer review:** `docs/scientific_data/PEER_REVIEW_SIMULATION.md`  
**Date of this status:** 2026-08-27  
**Mode:** accept-ready pass — agent-addressable peer-review findings fixed; human-only leftovers called out

---

## Blunt answers

| # | Ask | Verdict | One-line why |
|---|---|---|---|
| **(1)** Per-article licence join + NC segregation + HF/NOTICE correction | **DONE** | Disk stamps/pools/NOTICE/HF remirror honest; commercial 87,617 primary |
| **(2)** Technical Validation pack | **DONE** (agent scope) | n=200 transcription; recall proxy; full quarantine; Limitations vs NMRexp explicit. Expert human audits still optional |
| **(3)** Sci Data manuscript | **DONE** (near submit) / **not fully submission-ready** | Peer-review remediation applied in TeX+MD. Zenodo DOI, ORCID, funding remain human |
| **(4)** ICLR-facing cut + cross-cite | **DONE** (draft) | No bench results in Descriptor; companion cite only |

**Has everything actionable been addressed?** Agent-addressable peer-review Majors/Minors: **yes** (see `PEER_REVIEW_SIMULATION.md` post-remediation). Human-only: Zenodo mint (data-only deposit), ORCID (esp. Yabbarov), funding/acks. Optional: expert structure n≥100; human recall mark-up.

---

## Remaining blockers (honest)

### Critical — human only

1. **Zenodo DOI mint** for a **data-only** IRexp deposit (commercial primary + SA companion). Do **not** reuse the combined IRSpectra-Bench `.zenodo.json` as the Sci Data archival record.
2. **ORCID** — especially corresponding author I. Yabbarov (Vargas-Hernández ORCID known in MD notes: `0000-0002-5559-6521`).
3. **Acknowledgements / funding** text confirmation.

### Optional polish (not submit-blocking if Limitations stay honest)

4. Expert structure spot-check n≥100; true human extraction-recall mark-up.  
5. Dedicated overview figure (tables currently carry composition).  
6. Remirror HF after Chemotion `inchikey`/`has_structure` schema backfill (local release files updated 2026-08-27).

---

## Peer-review remediation summary (2026-08-27)

Fixed in-tree: Limitations section; NMRexp complementary positioning; schema fields; Chemotion `inchikey`/`has_structure` backfill; recall-proxy wording vs QC JSON; keywords scrub; README equal-contrib leftover; Usage Notes (quarantine default, SA remix); discovery freeze note; Code Availability join script; data-only Zenodo guidance.

**Still deferred:** Zenodo DOI, ORCID, funding; optional expert audits.

---

## Bottom line

Agent-addressable Sci Data accept-ready remediation is **complete** on this branch. Submit-blocking leftovers are **Zenodo (data-only) + ORCID + funding** (humans at submission).
