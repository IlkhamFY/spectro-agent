# IRexp: A database of experimental infrared band lists from open literature

**Ilkham Yabbarov**^1,†^, **Rodrigo A. Vargas-Hernández**^1,2,3,†^

^1^ Department of Chemistry and Chemical Biology, McMaster University, Hamilton, Ontario L8S 4L8, Canada.  
^2^ Brockhouse Institute for Materials Research, McMaster University, Hamilton, Ontario L8S 4L8, Canada.  
^3^ School of Computational Science and Engineering, McMaster University, Hamilton, Ontario L8S 4L8, Canada.

† Corresponding authors. E-mail: yabbaroi@mcmaster.ca, vargashr@mcmaster.ca  
(No equal-contribution footnote — distinct roles; both corresponding.)

<!-- ORCID / funding — human blockers; do not invent values.
       Sci Data authors: I.Y. + R.A.V.-H. only (R. Sondhi → IRSpectra-Bench companion).
       I. Yabbarov            ORCID: [TODO: confirm]
       R. A. Vargas-Hernández ORCID: 0000-0002-5559-6521
-->

## Abstract

IRexp is a redistributable collection of **experimental infrared band lists** (cm⁻¹ peak positions) mined from open chemistry literature, optionally with **author-reported** ¹H/¹³C NMR strings and resolved structures. The release holds **121,233** records (119,345 PMC OA; 1,888 Chemotion/RADAR4Chem), with **43,060** structure-linked and **33,201** full IR + ¹H + ¹³C + structure quadruples. IRexp stores **numeric band lists**, not absorbance traces. Records carry `source_doi` and stamped `license` / `license_pool`. Licensing is **mixed**: Europe PMC join yields **87,617** commercial (CC-BY/CC0), **20,938** non-commercial (NC*), **10,781** empty/unknown (excluded from commercial Zenodo), and **1,897** ShareAlike (Chemotion + rare PMC SA) — see `docs/scientific_data/LICENCE_REMEDIATION.md`. Reuse: multimodal training, retrieval, and tool-input for spectroscopic agents. Technical validation covers automated transcription and consistency checks; it does not match expert-scale manual audits of larger NMR list peers. Complementary elucidation benchmarks are described in a companion research manuscript and are not analysed here. Data: Hugging Face `ilkhamfy/IRexp`; Zenodo `[TODO: 10.5281/zenodo.XXXXXXX]` (data-only deposit). Code is MIT-licensed.

<!-- Abstract word count target ≤170. Count on edit before submission. -->

## Background & Summary

Infrared (IR) spectroscopy is routine in organic characterisation, yet **open, redistributable** collections of *experimental* IR data remain sparse relative to modern machine-learning and agentic tool-use needs. Digitised absorbance libraries such as the NIST Chemistry WebBook[@nist_webbook] and AIST SDBS[@sdbs] are valuable but either modest in size or **view-only** (no bulk redistribution). Computational IR–NMR resources published in *Scientific Data* expand multimodal coverage with simulated spectra[@zipoli2025uspto], while large literature mines for **NMR** peak lists (notably NMRexp[@wang2025nmrexp]) demonstrate that peer-reviewed experimental spectral *lists* with DOI traceability are in scope for this journal. Concurrent literature corpora that include IR among other modalities (for example NMRSpec/NMRTrans[@yang2026nmrtrans]) further motivate an **IR-focused, redistributable** band-list resource rather than another closed spectrum archive.

**Relation to NMRexp and other peers.** NMRexp is the natural comparator: ~3.3 million experimental NMR records mined from supporting-information PDFs, with expert-scale manual checks and replicate consistency metrics. IRexp is *not* an NMR database, does not claim size superiority, and is orders of magnitude smaller. Its contribution is complementary: redistributable **IR band lists** (cm⁻¹ positions only) from PMC Open Access full text plus a Chemotion ELN deposit, with per-record licence pools suitable for commercial vs non-commercial reuse. Absorbance-curve libraries (NIST, SDBS) remain the right choice when full digitised spectra are required; computational IR–NMR sets remain the right choice when simulated multimodal coverage is required.

In 2025–26, spectroscopic AI agents and autonomous chemistry workflows increasingly consume *structured* experimental peak lists as tool inputs and retrieval substrates — not paywalled PDF prose and not view-only web UIs. Agents that plan characterisation, call spectrum tools, or train IR→structure models need redistributable numeric lists with DOI attribution and explicit licence pools (commercial vs non-commercial vs ShareAlike). IRexp is designed as that substrate: training / retrieval / tool-input material for literature-grounded spectroscopic agents, without embedding diagnosis benchmarks or model leaderboards in this Descriptor.

IRexp fills a specific wedge. Experimental sections of chemistry papers conventionally report per-compound **IR band lists** (wavenumbers in cm⁻¹) together with ¹H/¹³C NMR shift lists. That textual convention is the object language models and many elucidation pipelines consume, and it is a **different object** from a digitised spectrum. IRexp therefore:

1. Harvests open-access full text from the **PMC Open Access Subset** bulk S3 mirror and peak lists from the **Chemotion** FT-IR deposit.
2. Extracts deterministic numeric IR band lists (and co-reported NMR strings where present).
3. Resolves compound names to canonical structures with OPSIN[@lowe2011opsin], RDKit[@landrum_rdkit], and SELFIES[@krenn2020selfies] where possible.
4. Releases **extracted numbers only** — no PDFs, figures, or article full text — with source accessions for attribution.

Among openly redistributable *text-derived IR band lists*, IRexp is large by record count (121,233). It does not claim to replace SDBS or NIST absorbance libraries; SDBS alone holds more structure-linked *spectra* than IRexp holds structure-linked band lists. The scientific contribution of this Descriptor is the curated dataset, harvest provenance, licence segregation, and validation artefacts — **not** elucidation accuracy claims. The intended reuse is multimodal pretraining, supervised IR→structure modelling on `irexp_resolved`, and as the literature substrate for complementary elucidation benchmarks described elsewhere (forthcoming ICLR manuscript on IRSpectra-Bench; cite that work for protocol and model results — **not** reproduced here).

**What this Data Descriptor does not contain.** No hypothesis tests, no large-language-model accuracy tables, and no stage-decomposition of elucidation performance. Those belong in the complementary research paper.

## Methods

### Source corpora

**PMC Open Access Subset.** Primary harvest uses the NCBI PMC OA bulk distribution on Amazon S3 (`s3://pmc-oa-opendata`, HTTPS endpoint `https://pmc-oa-opendata.s3.amazonaws.com`)[@pmc_oa]. **Harvest window (recoverable from git snapshots):** the bulk S3 IR crawl and `seen_papers` / `ir_harvest_snapshot` artefacts were produced on **2026-06-07 (UTC)** (`scripts/s3_ir_harvest.py`; incremental auto-snapshots that day through ~134,893 raw IR rows). Chemotion was ingested the same day. A harvest snapshot records **188,016** distinct PMC identifiers scanned (`data/irexp/seen_papers.txt.gz`). The released corpus retains records from **15,416** unique `PMC:*` accessions. Extraction operates on open-access **plain text** objects at flat S3 keys `PMC{id}.{v}/PMC{id}.{v}.txt` (not a directory walk of the commercial / non-commercial / other package trees). Europe PMC full-text XML is used for some validation re-fetches. The **released** IRexp DOIs are exclusively `PMC:*` accessions or the Chemotion deposit DOI; no paywalled publisher DOI appears in the 121,233-record file.

**Discovery vs `oa_comm` / `oa_noncomm` packages.** Identifier discovery used NCBI E-utilities `esearch` over PMC with an IR-characterisation query **and** `open access[filter]` (`scripts/s3_ir_harvest.py`), then fetched matching IDs from the flat S3 text layout. The harvest therefore did **not** pre-filter by walking the PMC OA Subset’s `oa_comm` vs `oa_noncomm` vs other package directories. PMC OA is still **not** a single licence[@pmc_oa]. Licence truth for redistribution is applied **post-hoc**: every unique PMCID in IRexp (15,416) was joined to Europe PMC `license` metadata (`scripts/join_pmc_licences.py`); each record carries `license` / `license_pool`. Commercial-use (CC-BY/CC0) rows form the Zenodo / Sci Data primary pool; NC* are held aside; empty/unknown are **excluded** from the commercial deposit — aligning redistributable intent with the OA commercial/non-commercial distinction via article-level licences rather than S3 package paths (`data/NOTICE`; `docs/scientific_data/LICENCE_REMEDIATION.md`).

**Reproducibility of discovery.** Re-running live `esearch` will drift as PMC grows. The frozen discovery set for this release is `data/irexp/seen_papers.txt.gz` (188,016 PMC identifiers); the curated release retains 15,416 of those accessions. Third parties should treat `seen_papers` + the released JSONL as the reproducible snapshot, not a fresh API crawl.

**Chemotion / RADAR4Chem.** **1,888** records come from the Chemotion Repository FT-IR collection deposited at RADAR4Chem (DOI `10.22000/OGoEQGlsZGElrgst`)[@chemotion2024], licensed **CC-BY-SA-4.0**. Ingest (`scripts/chemotion_to_irexp.py`, 2026-06-07): download the MD5-verified deposit; for each of **2,116** ATR-IR analyses, flatten the Quill-delta `content` field to plain text; parse an **author-curated** IR band list with the **same** regex extractor and quality gates as the PMC path; resolve the deposit’s canonical SMILES with RDKit → InChIKey + SELFIES; keep the richest band list per InChIKey; drop the **8** molecules already present in the PMC pool → **+1,888** new structure-resolved rows. All 1,888 Chemotion rows are structure-linked (`has_structure=true`; `inchikey` equals the record `id`). These are **not** algorithmic peak-picks from absorbance curves; they are author-entered experimental band lists from the ELN deposit, denser than typical paper prose (median **39** bands vs **9** for PMC). Rows carry `license=CC-BY-SA-4.0`, `source=Chemotion`, and `source_doi` equal to the deposit DOI.

**Excluded.** AIST SDBS (view-only; no bulk export)[@sdbs]; NIST WebBook join code exists in the repository but contributes **0** records to the released IRexp (`ir_source` is always `experimental` for released rows).

### Discovery and fetch (released corpus)

1. Discover IR-reporting OA PMCIDs via NCBI `esearch` (`open access[filter]` + characterisation-format IR query; year/month sliced).
2. Fetch OA full text from PMC-OA S3 plain-text objects (`PMC{id}.{v}.txt`).
3. Ingest Chemotion deposit author-curated band lists + structures (`scripts/chemotion_to_irexp.py`).
4. Persist harvest provenance in `seen_papers.txt.gz` and optional rawer rows in `ir_harvest_snapshot.jsonl.gz` (134,893 rows including intermediate prose fields used to diagnose materials-text false positives; the curated release is `irexp.jsonl.gz`).

**Non-OA / Scrapling fence.** Development adapters for ChemRxiv, Beilstein, and generic publisher pages (`spectro_scraper/fetch.py` Scrapling / StealthyFetcher TLS-impersonation stack; `spectro_scraper/sources/*`) exist for exploration. They are **outside the construction path of the released dataset** and are an optional dependency. **No released `source_doi` is a paywalled publisher DOI.** Methods for IRexp as published here cite only **PMC-OA S3 + Chemotion**.

### Extraction (band lists, not spectra)

A deterministic regular-expression pipeline (`spectro_scraper/extract.py`) segments experimental text per compound and extracts:

- IR wavenumbers → `ir_bands_cm-1` (list of floats, cm⁻¹);
- ¹H and ¹³C payloads → `h_nmr` / `c_nmr` (author strings, when present).

Gates reject scan-range artefacts and common prose false positives (for example hydrogel / materials narrative mistaken for IR lists). **No curve digitisation** is performed: figures are not traced; JCAMP-DX is not stored.

### Structure resolution

Where an IUPAC or systematic name is available, names are converted with OPSIN (py2opsin)[@lowe2011opsin], canonicalised with RDKit[@landrum_rdkit], and encoded as InChIKey and SELFIES[@krenn2020selfies]. An optional PubChem[@kim2023pubchem] name fallback (`USE_PUBCHEM`) handles trivial names. Name→structure failures are expected for trade names, mixtures, and non-IUPAC prose; unresolved rows keep `has_structure=false`. Structure coverage of the full release is **35.5%** (43,060 / 121,233). The structure-complete split is shipped as `irexp_resolved`.

### Licence handling

| Pool | Records | Stamp |
|---|---:|---|
| commercial (CC-BY + CC0) | **87,617** | `license_pool=commercial` — Zenodo / Sci Data primary |
| non_commercial (CC-BY-NC*) | 20,938 | held aside |
| sharealike (Chemotion + rare PMC SA) | 1,897 | CC-BY-SA / CC-BY-SA-4.0 |
| empty_unknown | 10,781 | excluded from commercial deposit |

`scripts/join_pmc_licences.py` stamps every row; `scripts/split_license_pools.py` reports provenance (`pool_of`) and materialises pool files under `data/irexp/licence_pools/`. Narrative and policy: `docs/scientific_data/LICENCE_REMEDIATION.md`.

### Quality tooling

Optional physics gates live in `spectro_scraper/quality.py` (¹³C peak count ≤ carbon count; ¹H integration vs formula; IR wavenumber windows). They were **not** applied as a hard filter at harvest; Technical Validation reports a full-corpus post-hoc quarantine on `irexp_resolved` (`scripts/quarantine_structure_nmr.py` → `data/audit/structure_nmr_quarantine.jsonl.gz`). Transcription and recall-proxy scripts: `scripts/audit_extraction.py`, `scripts/audit_extraction_recall.py`.

## Data Records

### Object definition

Each IRexp record is a JSON object. Required chemistry fields for an IR entry:

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable record id (InChIKey when resolved, else internal) |
| `ir_bands_cm-1` | float list | Experimental IR peak positions (cm⁻¹) |
| `ir_source` | string | `experimental` for all released rows |
| `source_doi` | string | `PMC:<pmcid>` or Chemotion deposit DOI |
| `pmcid` | string or null | PMC accession when PMC-sourced |
| `h_nmr` / `c_nmr` | string or null | Author-reported NMR shift *strings* (not parsed peak tables) |
| `smiles` / `selfies` / `inchikey` | string or null | Resolved structure encodings |
| `has_structure` | bool | Convenience flag (true when SMILES present) |
| `license` / `license_pool` | string | Per-article stamp (Europe PMC join or Chemotion) |
| `license_raw` / `license_source` | string | Upstream licence token + join provenance |
| `source` | string (Chemotion) | Present on Chemotion rows (`Chemotion`) |

**Not included:** absorbance traces, intensities, instrument metadata beyond what appears in source text, PDFs, figures, or full article bodies. Frozen counts: `docs/scientific_data/qc_structure_nmr.json`.

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
| `data/irexp/licence_pools/irexp_commercial.jsonl.gz` | 87,617 | CC-BY + CC0 (Zenodo/Sci Data primary) |
| `data/irexp/licence_pools/irexp_non_commercial.jsonl.gz` | 20,938 | NC* held aside |
| `data/irexp/licence_pools/irexp_sharealike.jsonl.gz` | 1,897 | Chemotion + rare PMC SA |
| `data/irexp/licence_pools/irexp_empty_unknown.jsonl.gz` | 10,781 | Excluded from commercial |

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

**Licence-pool counts (confirmed Track 1 join, 2026-08-26).** Lookup over **15,416** unique PMCIDs; stamped pool files under `data/irexp/licence_pools/` (see `docs/scientific_data/LICENCE_REMEDIATION.md`, `data/irexp/pmc_licence_summary.json`). Sum of pools = **121,233** (unchanged).

| Pool file | Count | Notes |
|---|---:|---|
| `irexp_commercial.jsonl.gz` | **87,617** | CC-BY / CC0 — **Zenodo primary** |
| `irexp_non_commercial.jsonl.gz` | **20,938** | CC-BY-NC* held aside |
| `irexp_empty_unknown.jsonl.gz` | **10,781** | empty / unresolved — **excluded** from commercial deposit |
| `irexp_other.jsonl.gz` | **0** | reserved (e.g. CC-BY-ND) |
| `irexp_sharealike.jsonl.gz` | **1,897** | Chemotion CC-BY-SA-4.0 (1,888) + rare PMC SA |

The full `irexp.jsonl.gz` remains multi-licence on disk; commercial redistribution must use the commercial pool (or `license_pool == "commercial"`). Hugging Face was re-issued with stamped pools and honest card text (`scripts/publish_hf.py`, 2026-08-26). Chemotion rows were schema-backfilled with `inchikey` / `has_structure` (2026-08-27).

Median bands: **9** (PMC), **39** (Chemotion). All **1,360,866** released IR band values fall inside 350–4000 cm⁻¹ (full-corpus range check; Technical Validation).

### Access

- **Hugging Face:** https://huggingface.co/datasets/ilkhamfy/IRexp (public mirror with commercial / NC / SA / empty_unknown configs — see `LICENCE_REMEDIATION.md`).
- **GitHub development mirror:** https://github.com/IlkhamFY/spectro-agent
- **Zenodo archival snapshot:** `[TODO: 10.5281/zenodo.XXXXXXX]` — mint a **data-only** deposit (commercial primary + SA companion); do not reuse the combined IRSpectra-Bench `.zenodo.json` as the Sci Data archival record.

## Technical Validation

Machine-readable package: `docs/scientific_data/qc_structure_nmr.json` (and artefacts under `data/audit/`). Numbers below are descriptive fidelity / consistency checks (fixed seeds); we do not report confidence intervals or claim NMRexp-parity expert audits.

### Transcription fidelity (PMC)

On a seed-fixed random sample of **60** PMC-sourced records (`scripts/audit_extraction.py --n 60 --seed 0`), each article was re-fetched from Europe PMC and every recorded wavenumber was checked against the source text (±1 cm⁻¹ integer match). Result: **560/560 bands** and **60/60 records** confirmed. Enlarged sample **n=200** (same script/seed family, `data/audit/extraction_audit_n200.json`): **2,250/2,261 bands (99.51%)** and **196/200 records (98.0%)** fully confirmed. The four incomplete records (PMCIDs 5713685, 4189708, 12202350, 6259152) missed 11 bands total on re-fetch match — consistent with plain-text / formatting drift, not wholesale hallucination. This bounds **automated** transcription error; it is not a human PDF mark-up of the kind reported for NMRexp.

### Extraction-recall proxy (PMC, harvest path)

A human mark-up of every IR string in every paper remains the gold standard. As an automatic **proxy** on the actual harvest path (`scripts/audit_extraction_recall.py --n 40 --seed 0`): re-fetch PMC-OA S3 plain text for **40** distinct source PMCIDs; re-run `extract_records`; compare band-sets to released rows (±1 cm⁻¹). Result: **2,640/2,640** released bands confirmed in re-extract; **248/248** released IR lists recovered (list-level recall proxy **1.0**; 40/40 papers). Of **258** re-extracted IR lists, **244** matched a released list (0.9457); **4/40** papers yielded *extra* re-extracted lists relative to the curated release (parser over-fire vs post-harvest dedup/curation, not missed released compounds). Summary: `data/audit/extraction_recall_proxy.json`. This is **not** a substitute for expert human recall.

### Structure–NMR consistency and quarantine (resolved)

**Sample (prior).** On **500** `irexp_resolved` records with ¹³C text (seed 0): **17/500 (3.4%)** listed more peaks than carbons. On **500** with ¹H text: integrals > formula H+2 in **17/497 (3.4%)**.

**Full resolved corpus.** `scripts/quarantine_structure_nmr.py` applied the same physics gates to all **43,060** structure-linked rows. **1,882 (4.37%)** fail ≥1 hard check and are listed in `data/audit/structure_nmr_quarantine.jsonl.gz` (diagnostic only — release files unchanged). Among rows with the relevant modality: ¹³C peaks > carbons **1,194/34,231 (3.49%)**; ¹H integral > formula+2 **1,141/39,672 (2.88%)**; IR out-of-range **0**; unparseable SMILES **0**. Sample rates and full-corpus rates agree closely. Re-users should **drop** quarantined IDs by default before supervised training. These rates are integrity diagnostics, **not** an expert skeleton audit (NMRexp-scale n≈300 manual checks remain optional future work).

### IR physical window

Every band in the full 121,233-record release lies in **[350, 4000] cm⁻¹** (0 / 1,360,866 out of range). This is a necessary range gate only: IRexp does not store intensities, solvents, or ATR vs transmission metadata.

### QC status

| Check | Status |
|---|---|
| Per-PMCID licence join + pool counts | **Done** — commercial 87,617 |
| Transcription fidelity n=60 and n=200 | **Done** (automated re-fetch) |
| Extraction-recall automatic proxy (n=40 papers, S3 path) | **Done** (human recall still optional) |
| Full-corpus structure–NMR quarantine | **Done** — 1,882 / 43,060 flagged |
| Expert structure spot-check (n≥100) | Optional / deferred |
| NMRexp-style replicate MAE for IR lists | Not applicable / not claimed |

## Usage Notes

- **Band lists ≠ spectra.** Do not evaluate models trained on IRexp as if they had seen full absorbance curves.
- **AI agents / LLM tool-use.** Prefer JSON band-list fields and `source_doi`; filter by `license_pool` rather than treating the full dump as a single licence.
- **Separate pools by density and licence.** PMC (sparse) vs Chemotion (denser ELN lists). Higher median band count ≠ more complete vibrational assignment. Combined redistribution of Chemotion-derived rows must honour CC-BY-SA-4.0; do not relicence SA rows as CC-BY.
- **Do not assume PMC = CC-BY-4.0.** Filter to `license_pool == "commercial"` (or use `irexp_commercial.jsonl.gz`) for commercial redistribution; attribute via `source_doi` / `pmcid`.
- **Structure–NMR quarantine.** Before supervised training on `irexp_resolved`, **drop** IDs in `data/audit/structure_nmr_quarantine.jsonl.gz` by default (~4.4% of resolved rows) unless a noisier set is intentional.
- **Training without benchmark leakage.** If using complementary IRSpectra-Bench problems, fine-tune from `train_no_bench.jsonl.gz` (or rebuild with `scripts/build_train_no_bench.py`). Protocol and model results live only in the companion manuscript.
- **Structure coverage.** Prefer `irexp_resolved` for supervised structure tasks; 64.5% of records lack SMILES.
- **Attribution.** Cite this Data Descriptor / Zenodo DOI (when minted) and attribute originating articles through each record’s `source_doi`.

### Limitations

- **Object.** Band-list corpus — not an absorbance-spectrum library and not an NMR resource comparable to NMRexp in scale or annotation richness.
- **Technical Validation depth.** Automated transcription (n=200) and harvest-path recall proxies (n=40 papers) are weaker evidence than NMRexp’s manual n≈300 PDF checks and replicate MAE analyses. No expert molecular-skeleton audit has been completed for IRexp.
- **Metadata sparsity.** Intensities, solvents, and instrument modes are generally absent; the IR window check is necessary but narrow.
- **Structure coverage and name resolution.** Only 35.5% of records are structure-linked; OPSIN/PubChem failures leave many IR lists without SMILES.
- **Licence mix.** The full `irexp.jsonl.gz` is multi-licence; commercial Zenodo/Sci Data redistribution is the commercial pool only.
- **Scope of this paper.** Elucidation benchmarks and model results are out of scope; cite the companion research manuscript for those claims.

## Data Availability

IRexp numeric extracts are available at:

- Hugging Face Datasets: https://huggingface.co/datasets/ilkhamfy/IRexp  
- GitHub: https://github.com/IlkhamFY/spectro-agent (`data/irexp/`, `data/irexp_resolved/`, `data/irexp_release/`)  
- Zenodo: `[TODO: 10.5281/zenodo.XXXXXXX]` (archival DOI at proof; **data-only** deposit — primary artifact = commercial pool, `cc-by-4.0` metadata + SA companion; do not reuse the combined IRSpectra-Bench `.zenodo.json`)

Licensing summary (honest):

- **Chemotion (1,888):** CC-BY-SA-4.0[@chemotion2024].  
- **PMC (119,345):** mixed Creative Commons — stamped per article; commercial redistributable **87,617** (CC-BY/CC0); NC* **20,938** held aside; empty/unknown **10,781** excluded from commercial Zenodo (`LICENCE_REMEDIATION.md`).  
- Only extracted numeric fields and identifiers are redistributed; source full texts are not.

## Code Availability

Harvesting, extraction, structure resolution, licence pool splitting, and validation scripts are in https://github.com/IlkhamFY/spectro-agent under the **MIT License** (`LICENSE`). Principal modules: `spectro_scraper/` (`extract.py`, `normalize.py`, `pipeline.py`, `quality.py`); release harvest `scripts/s3_ir_harvest.py`, `scripts/chemotion_to_irexp.py`; licence join `scripts/join_pmc_licences.py`; validation `scripts/audit_extraction.py`, `scripts/audit_extraction_recall.py`, `scripts/quarantine_structure_nmr.py`; pool split `scripts/split_license_pools.py`. The version corresponding to this Descriptor will be tagged at Zenodo deposit time.

## Author contributions

**I.Y.:** conceptualization, methodology, software, data curation, validation, writing — original draft.  
**R.A.V.-H.:** conceptualization, supervision, writing — review and editing.

R. Sondhi contributed to the companion IRSpectra-Bench / elucidation diagnosis manuscript and is not an author on this Data Descriptor.

## Competing interests

The authors declare no competing interests.

## Acknowledgements

<!-- Funding and institutional support — AUTHORS / PI — human blocker; do not invent -->

Funding and institutional support will be confirmed by the authors at submission / proof.

## References

References are maintained in `docs/scientific_data/references.bib` (pandoc/CSL build) and overlap the project bibliography where shared.
