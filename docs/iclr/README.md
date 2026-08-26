# ICLR track (T3) — IRSpectra-Bench + recall/verification diagnosis

This directory holds the **ICLR-facing research paper** split out of the combined
JCIM-shaped manuscript (**Track 3** in `docs/SPLIT_ORCHESTRATION.md`). It is **not** a
Data Descriptor and does not replace `docs/PAPER.md` or `docs/paper.tex`.

| file | role |
|---|---|
| [`ICLR_PAPER.md`](ICLR_PAPER.md) | Full ICLR draft (anonymous-ready structure) |
| [`README.md`](README.md) | This file — dual-publication boundary + outline |
| `../archive/combined_PAPER.md` | Frozen pre-split combined paper (T0; read-only) |
| `../PAPER.md` / `../paper.tex` | Live combined archive — **do not edit** for this track |
| `../scientific_data/` | Sci Data Data Descriptor (T2) |
| `../irexp_scientific_data_audit.md` | Sci Data fitness / dual-pub audit |
| `../SPLIT_ORCHESTRATION.md` | Multi-agent split plan |

**Venue plan:** *Scientific Data* (IRexp Data Descriptor) + **ICLR** (this paper). Prefer
Sci Data first (or simultaneous), then ICLR citing the Sci Data / Zenodo / HF identifier.
See `docs/SUBMISSION.md`.

Figures currently still point at `docs/figures/*` (shared with the combined manuscript).

---

## Section outline (`ICLR_PAPER.md`)

1. **Abstract** — claims: IRSpectra-Bench; 28% / 15% reweighted; recall 34% vs precision 89%; cross-vendor; contamination; literature decomp
2. **§1 Introduction** — operational setting; recall × precision factorisation; contributions; short IRexp pointer
3. **§2 Related work** — trained models; LLM agents; contamination benches; forward-verify / CASE
4. **§3 IRSpectra-Bench** — task, difficulty, scoring contract, three primary metrics
5. **§4 Experimental setup** — solver harness; forward-verify loop; controls
6. **§5 Results**
   - 5.1 Headline performance
   - 5.2 Formula-only / recency (contamination)
   - 5.3 Cross-vendor replication
   - 5.4 Forward-verification + generate-wide + non-LLM verifiers
   - 5.5 Literature decomposition
7. **§6 Discussion** — reporting contract; not a solved elucidator
8. **§7 Limitations** — harness, contamination bound≠exclusion, missing baselines, deferred arms
9. **§8 Conclusion**
10. **Reproducibility / Ethics** statements (ICLR-style)
11. **Appendix A** — IRexp pointer only
12. **Appendix B** — shared figure list

---

## Dual-publication boundary checklist

### Stays in **ICLR** (this paper)

- [x] IRSpectra-Bench protocol, scoring contract, leaderboard metrics
- [x] Headline elucidation numbers (top-1, recall, precision | recall)
- [x] Recall-bound diagnosis / wall figure narrative
- [x] Formula-only + recency contamination controls
- [x] Four-vendor replication
- [x] Forward-verification method + decomposition tables
- [x] Generate-wide / verifier probes (as diagnostics, not SOTA claims)
- [x] Literature top-*k* decomposition
- [x] Limitations honesty (harness, unresolved McNemar, missing on-bench baselines)
- [x] Reproducibility of **scoring** from frozen predictions

### Moves to / owned by **Scientific Data** (Data Descriptor)

- [ ] Full IRexp construction Methods (discovery, extraction, resolution pipeline)
- [ ] Data Records (schema, file layout, field dictionary)
- [ ] Technical Validation of the **corpus** (transcription audit enlargement, extraction-recall, structure–spectrum consistency)
- [ ] Per-article PMC licence join / stamped redistribution terms
- [ ] Usage Notes for training (licence pools, de-leak recipes) as dataset documentation
- [ ] Comparison to NMRexp / computational IR–NMR Sci Data peers in Background & Summary

### Allowed **short pointers** in ICLR (do not paste Data Descriptor)

- [x] Record counts + HF / Zenodo / Sci Data (in prep.) citation
- [x] One-line licensing caveat (mixed PMC-OA; Chemotion CC-BY-SA)
- [x] “Drawn from `irexp_resolved`” without mining Methods dump

### Must **not** happen

- [ ] Identical abstract/title/contribution list across Sci Data and ICLR
- [ ] Sci Data paper that rehashes LLM diagnosis tables as primary content
- [ ] ICLR paper that embeds full mining Methods / Data Records
- [ ] Publishing a single JCIM “resource + benchmark + diagnosis” with dataset DOI **before** Sci Data without a complementary-content plan (burns Sci Data novelty — see audit §F.4)
- [ ] Concurrent dual submission of substantially similar PDFs to ICLR and another ML venue

### Order / disclosure

| step | action |
|---|---|
| 1 | Keep `docs/PAPER.md` + `docs/archive/combined_PAPER.md` as the combined archive |
| 2 | Sci Data track owns Data Descriptor rewrite + licence join |
| 3 | ICLR track polishes `ICLR_PAPER.md` → conference TeX (later) |
| 4 | Cross-cite: ICLR → Sci Data DOI / HF; Sci Data → ICLR as complementary research paper |
| 5 | ChemRxiv: prefer separate deposits or clear “companion” language — do not present the combined paper as the sole archival record once split |

---

## Source & editing rules

- **Source:** `docs/archive/combined_PAPER.md` if present, else `docs/PAPER.md`.
- **Write only** under `docs/iclr/` (plus light `docs/SUBMISSION.md` venue note).
- **Do not edit** `docs/paper.tex`.
- **Do not delete** `docs/PAPER.md` or `docs/archive/combined_PAPER.md`.

Optional later: `docs/iclr/build.sh` for ICLR-style PDF from markdown + `docs/references.bib`.
