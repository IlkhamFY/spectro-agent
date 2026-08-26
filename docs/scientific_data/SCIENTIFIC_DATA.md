# IRexp experimental infrared band lists from the PMC Open Access Subset and Chemotion

**Ilkham Yabbarov**^1^ *(corresponding author: yabbaroi@mcmaster.ca)*, **Rudra Sondhi**^1^, **Rodrigo A. Vargas-Hernández**^2,1,3^

^1^ Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario L8S 4L8, Canada.  
^2^ Brockhouse Institute for Materials Research, McMaster University, Hamilton, Ontario L8S 4L8, Canada.  
^3^ School of Computational Science and Engineering, McMaster University, Hamilton, Ontario L8S 4L8, Canada.

<!-- ORCID / funding — human blockers; do not invent values.
       I. Yabbarov            ORCID: [TODO: confirm]
       R. Sondhi              ORCID: 0009-0003-3034-7347
       R. A. Vargas-Hernández ORCID: 0000-0002-5559-6521
-->

## Abstract

IRexp is a redistributable collection of **experimental infrared band lists** (cm⁻¹ peak positions) mined from open chemistry literature, optionally with ¹H/¹³C shifts and resolved structures. The release holds **121,233** records (119,345 PMC OA; 1,888 Chemotion/RADAR4Chem), with **43,060** structure-linked and **33,201** full IR + ¹H + ¹³C + structure quadruples. IRexp stores **numeric band lists**, not absorbance traces. Records carry `source_doi` and stamped `license` / `license_pool`. Licensing is **mixed**: Europe PMC join yields **87,617** commercial (CC-BY/CC0), **20,938** non-commercial (NC*), **10,781** empty/unknown (excluded from commercial Zenodo), and **1,897** ShareAlike (Chemotion + rare PMC SA) — see `docs/scientific_data/LICENCE_REMEDIATION.md`. Reuse: multimodal training and complementary elucidation benchmarks citing this Descriptor. Data: Hugging Face `ilkhamfy/IRexp`; Zenodo `[TODO: 10.5281/zenodo.XXXXXXX]`. Code is MIT-licensed.

<!-- Abstract word count target ≤170. Count on edit before submission. -->

## Background & Summary

Infrared (IR) spectroscopy is routine in organic characterisation, yet **open, redistributable** collections of *experimental* IR data remain sparse relative to modern machine-learning needs. Digitised absorbance libraries such as the NIST Chemistry WebBook[@nist_webbook] and AIST SDBS[@sdbs] are valuable but either modest in size or **view-only** (no bulk redistribution). Computational IR–NMR resources published in *Scientific Data* expand multimodal coverage with simulated spectra[@zipoli2025uspto], while large literature mines for **NMR** peak lists (notably NMRexp[@wang2025nmrexp]) demonstrate that peer-reviewed experimental spectral *lists* with DOI traceability are in scope for this journal. Concurrent literature corpora that include IR among other modalities (for example NMRSpec/NMRTrans[@yang2026nmrtrans]) further motivate an **IR-focused, redistributable** band-list resource rather than another closed spectrum archive.

IRexp fills a specific wedge. Experimental sections of chemistry papers conventionally report per-compound **IR band lists** (wavenumbers in cm⁻¹) together with ¹H/¹³C NMR shift lists. That textual convention is the object language models and many elucidation pipelines consume, and it is a **different object** from a digitised spectrum. IRexp therefore:

1. Harvests open-access full text from the **PMC Open Access Subset** bulk S3 mirror and peak lists from the **Chemotion** FT-IR deposit.
2. Extracts deterministic numeric IR band lists (and co-reported NMR strings where present).
3. Resolves compound names to canonical structures with OPSIN[@lowe2011opsin], RDKit[@landrum_rdkit], and SELFIES[@krenn2020selfies] where possible.
4. Releases **extracted numbers only** — no PDFs, figures, or article full text — with source accessions for attribution.

Among openly redistributable *text-derived IR band lists*, IRexp is large by record count (121,233). It does not claim to replace SDBS or NIST absorbance libraries; SDBS alone holds more structure-linked *spectra* than IRexp holds structure-linked band lists. The intended reuse is multimodal pretraining, supervised IR→structure modelling on `irexp_resolved`, and as the literature substrate for complementary elucidation benchmarks described elsewhere (forthcoming ICLR manuscript on IRSpectra-Bench; cite that work for protocol and model results — **not** reproduced here).

**What this Data Descriptor does not contain.** No hypothesis tests, no large-language-model accuracy tables, and no stage-decomposition of elucidation performance. Those belong in the complementary research paper.

## Methods

### Source corpora

**PMC Open Access Subset.** Primary harvest uses the NCBI PMC OA bulk distribution on Amazon S3 (`s3://pmc-oa-opendata`, HTTPS endpoint `https://pmc-oa-opendata.s3.amazonaws.com`)[@pmc_oa]. A harvest snapshot records **188,016** distinct PMC identifiers scanned (`data/irexp/seen_papers.txt.gz`). The released corpus retains records from **15,416** unique `PMC:*` accessions. Extraction operates on open-access plain text / JATS available through that OA path (and Europe PMC full-text XML for validation re-fetches). The **released** IRexp DOIs are exclusively `PMC:*` accessions or the Chemotion deposit DOI; no paywalled publisher DOI appears in the 121,233-record file.

PMC OA is **not** a single licence. The subset is partitioned into commercial-use, non-commercial, and other packages[@pmc_oa]. Every unique PMCID in IRexp (15,416) was joined to Europe PMC `license` metadata (`scripts/join_pmc_licences.py`); each record carries `license` / `license_pool`. Empty/unknown licences are **excluded** from the commercial Zenodo pool (`data/NOTICE`; `docs/scientific_data/LICENCE_REMEDIATION.md`).

**Chemotion / RADAR4Chem.** **1,888** records come from the Chemotion Repository FT-IR collection deposited at RADAR4Chem (DOI `10.22000/OGoEQGlsZGElrgst`)[@chemotion2024], licensed **CC-BY-SA-4.0**. These rows are **peak lists derived from deposited experimental FT-IR spectra** (not author-transcribed experimental-section prose). They carry a stamped `license=CC-BY-SA-4.0` and `source_doi` equal to the deposit DOI. Median band count is **39** versus **9** for PMC-transcribed lists; users modelling band density should treat the pools separately.

**Excluded.** AIST SDBS (view-only; no bulk export)[@sdbs]; NIST WebBook join code exists in the repository but contributes **0** records to the released IRexp (`ir_source` is always `experimental` for released rows).

### Discovery and fetch (released corpus)

1. Enumerate PMC OA identifiers / packages from the S3 OA mirror.
2. Fetch OA full text for experimental-section mining.
3. Ingest Chemotion deposit peak lists with structure metadata from the RADAR4Chem release.
4. Persist harvest provenance in `seen_papers.txt.gz` and optional rawer rows in `ir_harvest_snapshot.jsonl.gz` (134,893 rows including intermediate prose fields used to diagnose materials-text false positives; the curated release is `irexp.jsonl.gz`).

Development adapters for additional publishers exist in the codebase for exploration; they are **outside the construction path of the released dataset**. Methods for IRexp as published here are restricted to **PMC-OA S3 + Chemotion**.

### Extraction (band lists, not spectra)

A deterministic regular-expression pipeline (`spectro_scraper/extract.py`) segments experimental text per compound and extracts:

- IR wavenumbers → `ir_bands_cm-1` (list of floats, cm⁻¹);
- ¹H and ¹³C payloads → `h_nmr` / `c_nmr` (author strings, when present).

Gates reject scan-range artefacts and common prose false positives (for example hydrogel / materials narrative mistaken for IR lists). **No curve digitisation** is performed: figures are not traced; JCAMP-DX is not stored.

### Structure resolution

Where an IUPAC or systematic name is available, names are converted with OPSIN (py2opsin)[@lowe2011opsin], canonicalised with RDKit[@landrum_rdkit], and encoded as InChIKey and SELFIES[@krenn2020selfies]. An optional PubChem[@kim2023pubchem] name fallback (`USE_PUBCHEM`) handles trivial names. Structure coverage of the full release is **35.5%** (43,060 / 121,233). The structure-complete split is shipped as `irexp_resolved`.

### Licence handling

| Pool | Records | Stamp |
|---|---:|---|
| commercial (CC-BY + CC0) | 87,617 | `license_pool=commercial` — Zenodo primary |
| non_commercial (CC-BY-NC*) | 20,938 | held aside |
| sharealike (Chemotion + rare PMC SA) | 1,897 | CC-BY-SA / CC-BY-SA-4.0 |
| empty_unknown | 10,781 | excluded from commercial deposit |

`scripts/join_pmc_licences.py` stamps every row; `scripts/split_license_pools.py` reports provenance (`pool_of`) and real `license_pool` files under `data/irexp/licence_pools/`.

### Quality tooling

Optional physics gates live in `spectro_scraper/quality.py` (¹³C peak count ≤ carbon count; ¹H integration vs formula; IR wavenumber windows). They were **not** applied as a hard filter to every released row at harvest; Technical Validation reports post-hoc checks below. Transcription fidelity uses `scripts/audit_extraction.py`.

## Data Records

### Object definition

Each IRexp record is a JSON object. Required chemistry fields for an IR entry:

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable record id (InChIKey when resolved, else internal) |
| `ir_bands_cm-1` | float list | Experimental IR peak positions (cm⁻¹) |
| `ir_source` | string | `experimental` for all released rows |
| `source_doi` | string | `PMC:<pmcid>` or Chemotion deposit DOI |
| `h_nmr` / `c_nmr` | string or null | Author-reported shift lists |
| `smiles` / `selfies` / `inchikey` | string or null | Resolved structure encodings |
| `has_structure` | bool | Convenience flag |
| `license` / `license_pool` | string | Per-article stamp (Europe PMC join or Chemotion) |

**Not included:** absorbance traces, intensities, instrument metadata beyond what appears in source text, PDFs, figures, or full article bodies.

### Files and counts

Paths relative to the project repository / Hugging Face mirror.

| File | Records | Description |
|---|---:|---|
| `data/irexp/irexp.jsonl.gz` | 121,233 | Full curated release |
| `data/irexp_resolved/irexp_resolved.jsonl.gz` | 43,060 | 100% structure-linked |
| `data/irexp_release/train_no_bench.jsonl.gz` | 42,808 | Resolved minus IRSpectra-Bench InChIKeys |
| `data/irexp_release/train_no_bench_nmr.jsonl.gz` | 32,949 | Same with both ¹H and ¹³C |
| `data/irexp_release/pretrain_ir.jsonl.gz` | 119,345 | PMC-only IR pretrain pool |
| `data/irexp/seen_papers.txt.gz` | 188,016 lines | PMC IDs scanned at harvest |
| `data/irexp/ir_harvest_snapshot.jsonl.gz` | 134,893 | Intermediate harvest snapshot |

**Composition of `irexp.jsonl.gz`:**

| Slice | Count |
|---|---:|
| All IR band-list records | 121,233 |
| With ¹H and/or ¹³C NMR | 87,075 (72%) |
| With resolved structure | 43,060 (35.5%) |
| Structure + any NMR | 40,702 |
| Full IR + ¹H + ¹³C + structure | 33,201 |
| PMC OA provenance | 119,345 |
| Chemotion provenance | 1,888 |
| Unique PMC accessions | 15,416 |

**Licence-pool counts (Europe PMC join, 2026-08-26).** Lookup over **15,416** unique PMCIDs; stamped pool files under `data/irexp/licence_pools/` (see `LICENCE_REMEDIATION.md`). Sum of pools = 121,233.

| Pool file | Count | Notes |
|---|---:|---|
| `irexp_commercial.jsonl.gz` | **87,617** | CC-BY / CC0 — **Zenodo primary** |
| `irexp_non_commercial.jsonl.gz` | **20,938** | CC-BY-NC* held aside |
| `irexp_empty_unknown.jsonl.gz` | **10,781** | empty / unresolved — **excluded** from commercial deposit |
| `irexp_other.jsonl.gz` | **0** | reserved (e.g. CC-BY-ND) |
| `irexp_sharealike.jsonl.gz` | **1,897** | Chemotion CC-BY-SA-4.0 (1,888) + rare PMC SA |

The full `irexp.jsonl.gz` remains multi-licence on disk; commercial redistribution must use the commercial pool (or `license_pool == "commercial"`). Hugging Face should be re-issued with these files (`scripts/publish_hf.py`).

Median bands: **9** (PMC), **39** (Chemotion). All **1,360,866** released IR band values fall inside 350–4000 cm⁻¹ (full-corpus range check; Technical Validation).

### Access

- **Hugging Face:** https://huggingface.co/datasets/ilkhamfy/IRexp (public mirror; re-issue with stamped pools — see `LICENCE_REMEDIATION.md`).
- **GitHub development mirror:** https://github.com/IlkhamFY/spectro-agent
- **Zenodo archival snapshot:** `[TODO: 10.5281/zenodo.XXXXXXX]` (mint after honest multi-licence metadata).

## Technical Validation

### Transcription fidelity (PMC)

On a seed-fixed random sample of **60** PMC-sourced records (`scripts/audit_extraction.py --n 60 --seed 0`), each article was re-fetched from Europe PMC and every recorded wavenumber was checked against the source text (±1 cm⁻¹ integer match). Result: **560/560 bands** and **60/60 records** confirmed (Wilson 95% CI ≈ 99.3–100% for bands; ≈ 94–100% for records). Frozen machine-readable summary: `data/audit/extraction_audit.json`.

This bounds **transcription** error (hallucinated, mis-parsed, or unit-mangled values). It does **not** measure extraction **recall** (whether every IR string in every paper was found) — that requires human reading of full experimental sections and remains planned (see below).

### Structure–NMR consistency (resolved sample)

On a random sample of **500** `irexp_resolved` records with ¹³C text (seed 0), comma-separated ¹³C peaks were counted against RDKit carbon counts: **17/500 (3.4%)** listed more peaks than carbons (physically impossible → name/structure assignment or parse error). On **500** records with ¹H text, summed reported integrals exceeded formula hydrogens by more than 2 in **17/497** scored rows (**3.4%**; 3 lacked parseable integrals). Reproducible summary: `docs/scientific_data/qc_structure_nmr.json`.

These rates are reported as integrity diagnostics for re-users (quarantine or filter before supervised training). They are **not** claimed as a full expert structure audit; NMRexp-scale manual skeleton checks (n≈300) remain future work.

### IR physical window

Every band in the full 121,233-record release lies in **[350, 4000] cm⁻¹** (0 / 1,360,866 out of range).

### Planned / deferred QC

| Check | Status |
|---|---|
| Per-PMCID licence join + pool counts | **Done** — `LICENCE_REMEDIATION.md`; commercial 87,617 |
| Extraction-recall human audit (papers, not bands) | Planned (n≥30–50 papers) |
| Larger transcription sample (n≥200) | Planned |
| Full-corpus `quality.py` quarantine pass | Planned |
| Expert structure spot-check (n≥100) | Optional / deferred |

## Usage Notes

- **Band lists ≠ spectra.** Do not evaluate models trained on IRexp as if they had seen full absorbance curves.
- **Separate pools by density and licence.** PMC (sparse, author-transcribed) vs Chemotion (denser, deposit peak-picked). Keep Chemotion ShareAlike constraints in mind when combining pools; combined redistribution of Chemotion-derived rows must honour CC-BY-SA-4.0.
- **Do not assume PMC = CC-BY-4.0.** Filter to `license_pool == "commercial"` (or use `irexp_commercial.jsonl.gz`) for commercial redistribution; attribute via `source_doi` / `pmcid`.
- **Training without benchmark leakage.** If using the complementary IRSpectra-Bench problems, fine-tune from `train_no_bench.jsonl.gz` (or rebuild with `scripts/build_train_no_bench.py`) so benchmark InChIKeys are withheld.
- **Structure coverage.** Prefer `irexp_resolved` for supervised structure tasks; 64.5% of records lack SMILES.
- **Attribution.** Cite this Data Descriptor / Zenodo DOI and attribute originating articles through each record’s `source_doi`.

## Data Availability

IRexp numeric extracts are available at:

- Hugging Face Datasets: https://huggingface.co/datasets/ilkhamfy/IRexp  
- GitHub: https://github.com/IlkhamFY/spectro-agent (`data/irexp/`, `data/irexp_resolved/`, `data/irexp_release/`)  
- Zenodo: `[TODO: 10.5281/zenodo.XXXXXXX]` (archival DOI at proof; primary artifact = commercial pool, `cc-by-4.0` metadata + SA companion)

Licensing summary (honest):

- **Chemotion (1,888):** CC-BY-SA-4.0[@chemotion2024].  
- **PMC (119,345):** mixed Creative Commons — stamped per article; commercial redistributable **87,617** (CC-BY/CC0); NC* **20,938** held aside; empty/unknown **10,781** excluded from commercial Zenodo (`LICENCE_REMEDIATION.md`).  
- Only extracted numeric fields and identifiers are redistributed; source full texts are not.

## Code Availability

Harvesting, extraction, structure resolution, licence pool splitting, and validation scripts are in https://github.com/IlkhamFY/spectro-agent under the **MIT License** (`LICENSE`). Principal modules: `spectro_scraper/` (`extract.py`, `normalize.py`, `pipeline.py`, `quality.py`); validation `scripts/audit_extraction.py`; pool split `scripts/split_license_pools.py`. The version corresponding to this Descriptor will be tagged at Zenodo deposit time.

## Author contributions

**I.Y.:** conceptualization, methodology, software, data curation, validation, writing — original draft.  
**R.S.:** methodology, software, validation, writing — review and editing.  
**R.A.V.-H.:** conceptualization, supervision, writing — review and editing.

## Competing interests

The authors declare no competing interests.

## Acknowledgements

<!-- Funding and institutional support — AUTHORS / PI -->

Funding and institutional support will be added at proof.

## References

References are maintained in `docs/scientific_data/references.bib` (pandoc/CSL build) and overlap the project bibliography where shared.
