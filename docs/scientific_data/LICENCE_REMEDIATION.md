# IRexp licence remediation (Track 1)

**Date:** 2026-08-26  
**Branch:** `cursor/irexp-licence-remediation-9a67`  
**Audit:** `docs/irexp_scientific_data_audit.md` (§C)

## Problem

PMC Open Access is **not** uniformly CC-BY. A prior blanket CC-BY claim (~19% NC/empty in a 200-PMCID sample) was incorrect for NOTICE / README / HF / Zenodo framing. Chemotion CC-BY-SA-4.0 was already correct.

## What we did

1. **`scripts/join_pmc_licences.py`** — extract unique `PMC:*` accessions from `data/irexp/irexp.jsonl.gz`, batch-query Europe PMC (`resultType=core` → `license`), cache hits, classify, stamp every record, write segregated pools.
2. **`scripts/split_license_pools.py`** — uses stamped `license_pool` / `license` (not DOI-prefix → CC-BY). Keeps `pool_of()` as provenance-only (`pmc` vs `chemotion`) for manuscript gate A.
3. Stamped full corpus + pool files under `data/irexp/`.
4. Honest updates: `data/NOTICE`, `README.md`, `.zenodo.json`, `data/irexp_release/README_HF.md`, minimal `docs/PAPER.md`.

## Classification policy

| Europe PMC / Chemotion | `license` | `license_pool` | Zenodo / Sci Data |
|---|---|---|---|
| `cc by`, versioned BY | CC-BY | **commercial** | **Primary redistributable** |
| `cc0` / public domain | CC0 | **commercial** | Primary |
| `cc by-nc`, `cc by-nc-nd`, `cc by-nc-sa` | CC-BY-NC* | **non_commercial** | Held-aside file |
| `cc by-sa` (PMC) | CC-BY-SA | **sharealike** | With Chemotion SA file |
| Chemotion RADAR4Chem | CC-BY-SA-4.0 | **sharealike** | SA file |
| `cc by-nd` | CC-BY-ND | **other** | Held aside (ND vs derived extracts) |
| Missing `license` field | EMPTY | **empty_unknown** | **Exclude from commercial pool** |
| No EPMC hit | UNKNOWN | **empty_unknown** | **Exclude from commercial pool** |

**Recommendation (implemented):** ship Sci Data / Zenodo **commercial-use pool** as the primary artifact; keep NC in a clearly labelled file; exclude empty/unknown from the commercial deposit; keep Chemotion (+ rare PMC SA) as a separate ShareAlike file.

## Counts (Europe PMC join, 2026-08-26)

### Records (n = 121,233)

| Pool | Records | % of corpus |
|---|---:|---:|
| **commercial** (CC-BY + CC0) | **87,617** | 72.3% |
| non_commercial (NC*) | 20,938 | 17.3% |
| sharealike (Chemotion 1,888 + PMC SA 9) | 1,897 | 1.6% |
| empty_unknown | 10,781 | 8.9% |
| other | 0 | 0.0% |
| **Total** | **121,233** | 100% |

### By `license` label (records)

| license | Records |
|---|---:|
| CC-BY | 87,588 |
| EMPTY | 10,664 |
| CC-BY-NC | 10,546 |
| CC-BY-NC-ND | 9,663 |
| CC-BY-SA-4.0 (Chemotion) | 1,888 |
| CC-BY-NC-SA | 729 |
| UNKNOWN | 117 |
| CC0 | 29 |
| CC-BY-SA (PMC) | 9 |

### Unique PMCIDs (15,416 articles)

| license | Articles |
|---|---:|
| CC-BY | 11,967 |
| CC-BY-NC | 1,235 |
| CC-BY-NC-ND | 1,190 |
| EMPTY | 864 |
| CC-BY-NC-SA | 134 |
| UNKNOWN | 21 |
| CC0 | 4 |
| CC-BY-SA | 1 |

Provenance totals unchanged: **119,345** PMC-sourced + **1,888** Chemotion.

## Artefacts

| Path | Role |
|---|---|
| `scripts/join_pmc_licences.py` | Join + stamp + write pools |
| `scripts/split_license_pools.py` | Report / re-materialise from stamps |
| `data/irexp/irexp.jsonl.gz` | Full corpus **with** `license*` fields |
| `data/irexp/pmc_licence_lookup.jsonl.gz` | Per-PMCID cache |
| `data/irexp/pmc_licence_summary.json` | Machine-readable counts |
| `data/irexp/licence_pools/irexp_commercial.jsonl.gz` | Zenodo primary (87,617) |
| `data/irexp/licence_pools/irexp_non_commercial.jsonl.gz` | NC held aside |
| `data/irexp/licence_pools/irexp_sharealike.jsonl.gz` | Chemotion + PMC SA |
| `data/irexp/licence_pools/irexp_empty_unknown.jsonl.gz` | Excluded from commercial |
| `data/irexp/licence_pools/irexp_other.jsonl.gz` | Empty placeholder (0 rows) |

Re-run:

```bash
python scripts/join_pmc_licences.py          # network; resumable via cache
python scripts/split_license_pools.py        # report
```

## Hugging Face re-upload (no credentials in-repo)

Public dataset: https://huggingface.co/datasets/ilkhamfy/IRexp  

Previous card/tags overclaimed PMC as CC-BY. After this branch merges:

1. Ensure `HF_TOKEN` with write access to `ilkhamfy/IRexp` (or a staging fork).
2. Update local card: `data/irexp_release/README_HF.md` (already multi-licence).
3. Upload stamped files + commercial primary, e.g.:

```bash
# Preferred: repo helper (requires HF_TOKEN)
HF_TOKEN=hf_... python scripts/publish_hf.py

# Or huggingface-cli
huggingface-cli upload ilkhamfy/IRexp \
  data/irexp/licence_pools/irexp_commercial.jsonl.gz \
  data/irexp_commercial.jsonl.gz
huggingface-cli upload ilkhamfy/IRexp \
  data/irexp/irexp.jsonl.gz data/irexp.jsonl.gz
huggingface-cli upload ilkhamfy/IRexp \
  data/irexp_release/README_HF.md README.md
```

4. Set dataset card `license` list to reflect **cc-by-4.0** (commercial primary) **and** **cc-by-sa-4.0** (Chemotion/SA pool); document NC/empty as non-redistributed or separate configs.
5. Add a card warning: full `irexp.jsonl.gz` is multi-licence; commercial training should use `license_pool == "commercial"` or the commercial file only.

If `HF_TOKEN` is unavailable in this environment, ship the files above and run the upload from a machine with Hub credentials.

## Zenodo

`.zenodo.json` describes a **multi-licence** deposit: primary file = commercial CC-BY pool; Chemotion/SA as a second file under CC-BY-SA-4.0; NC and empty/unknown not in the commercial artifact (may be uploaded as restricted/supplementary with clear labels). Zenodo’s single `license` metadata field is set to `cc-by-4.0` for the **primary** commercial artifact; description text states the SA companion and exclusions.

## Manuscript / gates

- Full corpus count remains 121,233; PMC/Chemotion provenance counts unchanged → `check_manuscript.py` gate A still passes via `pool_of` provenance split.
- Filter commercial rows at release time; do not shrink the on-disk research corpus.
- `docs/paper.tex` intentionally untouched (Track 1 rule).
