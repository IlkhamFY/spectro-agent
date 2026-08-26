# IRexp → Nature Scientific Data: hard-nosed fitness & provenance audit

**Audience:** Rodrigo A. Vargas-Hernández (PI)  
**Repo:** IlkhamFY/spectro-agent (`/workspace`)  
**Date:** 2026-08-26  
**Branch for factual licensing notes:** `cursor/irexp-scidata-audit-9a67`  
**Question:** Can we publish IRexp in *Scientific Data* — and will how we obtained the data raise editorial/legal/ethical questions?

---

## Executive verdict (read this first)

| # | Answer |
|---|---|
| **1. Can we publish IRexp in Scientific Data?** | **Yes with conditions — currently Risky until licensing is fixed.** Fit as a Data Descriptor is real (band-list multimodal corpus; analogues exist). The **blanket “PMC-OA = CC-BY-4.0” claim is false** and would not survive Nature legal / editor scrutiny. |
| **2. Top 3 issues that will raise questions** | (i) **PMC licence mix mislabelled as all CC-BY** (~19% NC/empty in a 200-PMCID sample). (ii) **Provenance honesty:** Scrapling/Cloudflare-bypass scraper exists alongside the claimed `s3://pmc-oa-opendata` path; release does not stamp per-article licences. (iii) **Technical Validation thinner than recent Sci Data peers** (transcription n=60 only; extraction recall deferred; structure–spectrum mismatches ~5–6% on a resolved sample; expert audit not run). |
| **3. Minimum work before Sci Data submission** | Per-article PMC licence join → drop or segregate NC/Other; stamp licences on disk; Zenodo DOI with honest multi-licence; rewrite Data Descriptor (Methods / Data Records / Technical Validation / Usage Notes); enlarge QC (structure audit + extraction-recall sample); retire or fence Scrapling narrative for non-OA. |
| **4. Two-paper split (Sci Data + ICLR)** | **Complementary Data Descriptor + research paper is allowed by Sci Data** if overlap is transparent. **ICLR forbids substantially similar dual submission.** Order and content split matter: Sci Data = data object only; ICLR = diagnosis/benchmark/methods. **Do not first publish a JCIM “resource+benchmark+diagnosis” that already discloses the dataset DOI**, or Sci Data may reject for insufficient new content. Scoop risk from NMRexp / NMRSpec-style literature mines is real but surmountable if IR band-list niche is clear. |

**Odds (data-descriptor-only, after licence remediation):** **Medium.**  
**Odds (as currently framed / licensed):** **Low–Medium** — licence claim is a blocker, not a polish item.

---

## A. Scientific Data fit

### What a Data Descriptor requires

From [Scientific Data submission guidelines](https://www.nature.com/sdata/publish/submission-guidelines) and [editorial policies](https://www.nature.com/sdata/policies/editorial-and-publishing-policies):

| Section | Expectation | IRexp status today |
|---|---|---|
| **Title** | ≤110 chars; no brandy claims (“novel”, “AI-ready”, “open” as advertising); no colons | Current title is JCIM-style with colons / product names — **must be rewritten** for Sci Data |
| **Abstract** | ≤~170 words; describe data + reuse; **no scientific findings** | Current abstract is diagnosis-heavy — **rewrite** |
| **Background & Summary** | Motivation + reuse value; cite prior related publications | Partial in `docs/PAPER.md` § Motivation |
| **Methods** | Full pipeline; for secondary/mined data, **exact input sources** so others can recreate | Partial; S3 path claimed; licence filtering **not** documented |
| **Data Records** | Repo, files, formats, schema; **no summary stats** here | Files exist; schema documented in HF card; Sci Data section not written |
| **Technical Validation** | Experiments/checks supporting integrity | Transcription audit (560/560, n=60) only; recall deferred |
| **Usage Notes** | How to reuse (optional) | Split pools / `train_no_bench` exist |
| **Data Availability** | Persistent repo (DOI); anonymous review access | HF public; **Zenodo DOI still TODO** |
| **Code Availability** | Required | MIT code in repo |

Data Descriptors **must not** present hypothesis tests / in-depth analyses. The current manuscript is a **JCIM resource + benchmark + LLM diagnosis** (`docs/SUBMISSION.md`). That is **not** a Sci Data Data Descriptor as-is — it must be split/rewritten.

### Analogous published Scientific Data papers

| Paper | Object | Relevance |
|---|---|---|
| **NMRexp** (*Sci. Data* 2025, [s41597-025-06245-5](https://www.nature.com/articles/s41597-025-06245-5)) | 3.3M **experimental** NMR peak records from ~200k **freely accessible SI PDFs** (ACS/Wiley/RSC/etc.) | Closest peer: literature-mined **experimental** spectral *lists*, DOI traceability, heavy Technical Validation (n=300 manual, replicate MAE). Shows Sci Data accepts mined experimental spectroscopy. Also shows bar for QC. |
| **USPTO-Spectra / IR–NMR multimodal computational** (*Sci. Data* 2025, [s41597-025-05729-8](https://www.nature.com/articles/s41597-025-05729-8)) | 177k **computed** IR + NMR for patent molecules | Sci Data accepts multimodal IR+NMR *datasets*; computational not experimental. |
| Related context (not all Sci Data): **NMRSpec** / NMRTrans arXiv corpus (~2.1M spectroscopic records incl. ~12% IR from literature 2013–2025) | Concurrent literature-mine competition | Scoop / “already done” risk for *general* mined spectra; IRexp’s wedge is **redistributable experimental IR band lists + multimodal pairing**. |

**Fit of IRexp’s object type:** Strong — Sci Data already published experimental literature-mined NMR (NMRexp) and multimodal IR/NMR resources. **Band lists (not absorbance traces)** are honest and should be foregrounded (paper already does this vs SDBS/NIST). Editors will not reject for “not full spectra” if the Data Records section is unambiguous.

**Odds:**

| Path | Odds | Why |
|---|---|---|
| Data Descriptor only, after licence + QC remediation | **Medium** | Object fits; QC below NMRexp bar but salvageable |
| Data Descriptor with current licence claims | **Low** | Factual licence error is editorial/legal risk |
| Need “more QC” vs descriptor-only | Not “more science” — **need stronger Technical Validation + licence provenance**, not new ML results |

---

## B. Provenance — HOW was IRexp obtained? (chain of custody)

### What is stored (confirmed on disk)

| Artefact | Path | Contents |
|---|---|---|
| Full corpus | `data/irexp/irexp.jsonl.gz` | **121,233** records: `ir_bands_cm-1` (floats), optional `h_nmr`/`c_nmr` strings, optional `smiles`/`selfies`/`inchikey`, `source_doi`, `ir_source=experimental` |
| Structure-linked | `data/irexp_resolved/irexp_resolved.jsonl.gz` | **43,060** (100% SMILES) |
| Training release | `data/irexp_release/*.jsonl.gz` | `train_no_bench` 42,808; `pretrain_ir` 119,345 (PMC only) |
| Harvest snapshot | `data/irexp/ir_harvest_snapshot.jsonl.gz` | 134,893 rawer rows (includes `ir_raw` prose — shows materials-prose false-positive risk) |
| Seen papers | `data/irexp/seen_papers.txt.gz` | **188,016** PMC IDs scanned |
| Unique PMC sources in release | — | **15,416** distinct `PMC:*` accessions |
| Chemotion | all `source_doi=10.22000/OGoEQGlsZGElrgst` | **1,888** records |

**Not stored in IRexp release:** full absorbance traces, JCAMP-DX, PDFs, figures, article full text.  
**NIST IR join** exists in code (`spectro_scraper/pipeline.py::join_nist_ir`, `sources/nist.py`) but **0 NIST-joined records** in the released IRexp (`ir_source` always `experimental`).

Counts claimed in `docs/PAPER.md` **match disk** (gated by `scripts/check_manuscript.py`): 121,233 / 87,075 NMR / 43,060 structure / 33,201 full quadruples / 119,345 PMC / 1,888 Chemotion.

### Pipeline (scripts & modules)

```
Discovery
  ├─ Claimed (Methods): bulk PMC-OA from s3://pmc-oa-opendata
  │    evidence: scripts/benchmark_v2.py S3 = https://pmc-oa-opendata.s3.amazonaws.com
  │              data/irexp/seen_papers.txt.gz (188k PMC IDs)
  ├─ Also in code: CrossRef / EuropePMC / NCBI esearch
  │    spectro_scraper/discover.py
  └─ Chemotion: RADAR4Chem deposit DOI 10.22000/OGoEQGlsZGElrgst (resolves; CC BY-SA 4.0)

Fetch
  ├─ PMC path: S3 plain-text / PMC OAI JATS (europepmc adapter)
  └─ Alternate scraper path: Scrapling TLS-impersonation + StealthyFetcher
       (spectro_scraper/fetch.py) — Cloudflare bypass for publisher PDFs
       adapters: chemrxiv, beilstein, europepmc, generic
       ⚠️ ethical/editorial optics even if final release is OA-only

Extract
  └─ spectro_scraper/extract.py — deterministic regex on experimental text
       → IR wavenumber lists + ¹H/¹³C strings (not digitised curves)

Resolve structures
  └─ spectro_scraper/normalize.py
       IUPAC name → OPSIN (py2opsin) → RDKit canonical SMILES / InChIKey
       → SELFIES; optional PubChem name fallback (USE_PUBCHEM flag)

Quality (optional at harvest)
  └─ spectro_scraper/quality.py — physics gates; CLI --quality-gate
       Not evidenced as applied to the full released corpus

Licence pools
  └─ scripts/split_license_pools.py — splits ONLY by DOI prefix
       Chemotion (10.22000*) vs everything else labelled “PMC CC-BY-4.0”
       ⚠️ No per-article PMC licence lookup

Release / mirror
  ├─ scripts/build_train_no_bench.py
  ├─ scripts/publish_hf.py → huggingface.co/datasets/ilkhamfy/IRexp (public)
  └─ .zenodo.json — deposit metadata; DOI still TODO in PAPER.md
```

### Source corpora — what was / was not used

| Source | In released IRexp? | Notes |
|---|---|---|
| **PMC Open Access Subset** (S3 / OAI) | **Yes — 119,345** | Primary. Methods claim this path. |
| **Chemotion / RADAR4Chem** | **Yes — 1,888** | Peak-picked from deposited spectra; median 39 bands vs PMC median 9 |
| NIST WebBook | Code only | Join path exists; **not in release** |
| AIST SDBS | Explicitly excluded | View-only; paper correctly contrasts |
| Publisher paywalled PDFs / SI | Scraper *capable*; release DOIs are all PMC or Chemotion | No non-PMC publisher DOI in release (`other=0`) |
| Patents | No | — |

### Scraping of non-OA content?

- **Released IRexp DOIs are 100% PMC:* or Chemotion.** No paywalled publisher DOI appears in the 121k file.
- **Codebase includes** Cloudflare-impersonating fetchers and ChemRxiv/Beilstein PDF/SI adapters (`spectro_scraper/fetch.py`, `sources/*`). Seeds (`data/seeds.yaml`) target gold-OA journals.
- **Editorial risk:** reviewers reading `spectro_scraper/` will ask whether bulk harvest ever hit non-OA. Mitigation: document that the **released corpus is PMC-OA + Chemotion only**, and move/retire non-OA fetch paths from the “IRexp construction” narrative — or prove they were never used for the release.

### Structure assignment path

OPSIN → RDKit → InChIKey/SELFIES; PubChem fallback for trivial names. Structure coverage **35.5%** (43,060/121,233). Name→structure errors are a known failure mode (see §D).

---

## C. Licensing & redistributability — WILL EDITORS ASK HARD QUESTIONS?

**Yes. This is the highest-severity issue.**

### What the project claims

| Location | Claim |
|---|---|
| `LICENSE` | Code MIT; datasets under source licences — see `data/NOTICE` |
| `data/NOTICE` | PMC pool **CC-BY-4.0** (119,345); Chemotion **CC-BY-SA-4.0** (1,888); numeric extracts only |
| `docs/PAPER.md` § Contents and licensing / Data availability | Same; “Each record carries … **licence stamp**” |
| `README.md`, `.zenodo.json`, HF card | Same dual-licence story; Zenodo metadata lists **only** `cc-by-4.0` |
| HF `ilkhamfy/IRexp` | Public; tags `cc-by-4.0` + `cc-by-sa-4.0`; preview rows show PMC as `license=CC-BY-4.0`, `source=pmc_oa` |

### What is actually on disk

| Pool | `license` field | Reality |
|---|---|---|
| Chemotion (1,888) | `CC-BY-SA-4.0` stamped | DOI resolves; landing page **CC BY-SA 4.0** — OK |
| PMC (119,345) | **`null` / NONE** | **Not stamped.** `split_license_pools.py` *assumes* all non-Chemotion = CC-BY-4.0 |

`data/NOTICE` itself still has a **TODO**: add per-record licence or ship physically separate pools — acknowledging the claim is incomplete.

### PMC OA is **not** all CC-BY (empirical)

PMC Open Access Subset is split into commercial / non-commercial / other ([PMC OA Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/)).  
Europe PMC `license` field on a **random sample of 200 unique PMCIDs from IRexp**:

| Licence (Europe PMC) | Count | % |
|---|---:|---:|
| `cc by` | 146 | 73.0% |
| `cc by-nc-nd` | 22 | 11.0% |
| `cc by-nc` | 15 | 7.5% |
| `cc by-nc-sa` | 1 | 0.5% |
| EMPTY / no field | 15 | 7.5% |
| NO_RESULT | 1 | 0.5% |

**≈19% of sampled source articles are NC or empty — yet redistributed under a blanket CC-BY-4.0 claim.**  
That is a **factual error** in PAPER.md / NOTICE / README / HF / Zenodo framing.

HF preview showing `CC-BY-4.0` on PMC rows is consistent with **blanket stamping**, not per-article verification (local git still has PMC `license=null`).

### Upstream compatibility (derived band lists)

| Issue | Assessment |
|---|---|
| Extracting **numeric** peak lists / shifts from CC-BY text | Generally OK under CC-BY with attribution |
| Same from **CC-BY-NC** / **NC-ND** | Redistributing a derived dataset **as CC-BY for commercial ML reuse** is **not** compatible; NC must stay NC or be excluded from commercial pool |
| CC-BY-SA Chemotion | ShareAlike applies to adaptations; mixing into a single CC-BY release without separation is problematic — paper’s separable-pools idea is correct **if executed** |
| Copyright in figures/spectra-as-numbers | Low risk for author-transcribed band lists in text; higher if digitising figure curves (IRexp does not) |
| SDBS | Correctly excluded |
| Publisher TDM / SI scraping (NMRexp style) | IRexp’s PMC-OA path is cleaner *if* restricted to commercial-use OA; NMRexp mined free SI from many publishers — Sci Data accepted it, but licence of *that* dataset is a separate debate |

### Public status

| Channel | Status |
|---|---|
| **Hugging Face** `ilkhamfy/IRexp` | **Public** (created ~2026-08-24; ~32 downloads) |
| **Zenodo** | **Not minted** (`[TODO: 10.5281/zenodo.XXXXXXX]`) |
| **GitHub** | Public development mirror with full `data/irexp*` |

**Gray area Nature legal would flag:** “We extracted from papers and release as CC-BY” without article-level licence filtering — especially after HF already published under that claim.

### Factual corrections needed (licensing)

1. Stop claiming all PMC-OA records are CC-BY-4.0.  
2. Join each `PMC:` accession to its machine-readable licence; segregate commercial / NC / other.  
3. Stamp `license` on every record; ship separate files or enforce `split_license_pools` on real licences.  
4. Fix Zenodo metadata (cannot be only `cc-by-4.0` while Chemotion is SA and PMC is mixed).  
5. Soften PAPER “licence stamp” sentence until stamps exist for PMC.  
6. Re-issue HF card after remediation (current public mirror inherits the overclaim).

---

## D. Quality / Technical Validation readiness

### What exists today

| Check | Evidence | Scope |
|---|---|---|
| **Transcription fidelity** | `scripts/audit_extraction.py --n 60 --seed 0` → `data/audit/extraction_audit.json`: **560/560 bands, 60/60 records** | PMC only; re-fetch EuropePMC full text; ±1 cm⁻¹ match |
| **Licence pool counts** | `scripts/split_license_pools.py` + `check_manuscript.py` gate A | Count integrity, not licence truth |
| **Benchmark spectral validation** | `scripts/validate_benchmark.py`; formula match on 242 GT structures | Bench only, not full IRexp |
| **Leakage / contamination** | `prompt_leakage.py`, `train_no_bench`, recency control, verifier leakage scripts | Strong for *benchmark*; not dataset QC |
| **Physics quality module** | `spectro_scraper/quality.py` | Available; not shown run on full release |

### Prepared but not run / deferred

| Item | Status |
|---|---|
| Expert-chemist audit of elucidation outputs | Frozen kit `data/audit/`; **formally deferred** (`docs/EXPERT_AUDIT_PROTOCOL.md`, SUBMISSION.md) — more relevant to ICLR/JCIM than Sci Data |
| **Extraction-recall** human audit (did parser find every IR string?) | Explicitly deferred in PAPER Limitations |
| Leave-one-modality ablation | Abandoned |

### Spot check: structure–spectrum consistency (this audit)

On a random sample of **500** `irexp_resolved` records with ¹³C text: **28/500 (5.6%)** had more parsed ¹³C peaks than carbons in the SMILES (physically impossible → name/structure or parse error).  
¹H integration > formula+2: **18/468 (~3.8%)**.

Comparable Sci Data peer **NMRexp** reported: n=300 manual audit, >99% metadata accuracy, **98% skeleton correctness**, plus replicate MAE analyses. IRexp’s n=60 transcription-only audit is **below that bar**.

### What Sci Data reviewers will demand that you lack

1. **Per-source licence accounting** (and NC handling).  
2. **Larger Technical Validation**: structure assignment accuracy (OPSIN/OCR-analogue), extraction recall estimate, false-positive IR-from-prose rate (snapshot shows materials hydrogel prose risk).  
3. **Clear Data Records** file inventory with schema (Zenodo), not only GitHub paths.  
4. **Methods exactness:** which PMC OA subset directories (`oa_comm` vs `oa_noncomm`)? Version/date of S3 harvest?  
5. Possibly: Chemotion peak-picking method details (how 1,888 lists were derived from ELN deposits).

---

## E. Risk register

| Risk | Severity | Evidence | Mitigation for Sci Data |
|---|---|---|---|
| **Legal redistributability (PMC NC labelled CC-BY)** | **Critical** | EuropePMC sample ~19% NC/empty; NOTICE/PAPER blanket CC-BY; HF public | Licence join; drop or segregate NC; re-release; correct all docs; counsel if needed |
| **Ethical scraping optics (Scrapling / stealth)** | **High** | `fetch.py` Cloudflare impersonation; StealthyFetcher | Released DOIs are PMC/Chemotion only — document that; fence scraper as legacy/dev; Methods cite only S3 PMC-OA + Chemotion |
| **Incomplete provenance / licence stamps** | **High** | PMC `license=null` on disk; NOTICE TODO; Methods omit licence filter | Stamp records; separate files; Methods subsection “Licence filtering” |
| **Band lists misrepresented as spectra** | **Medium (managed)** | Paper already clear; HF warning box; SDBS contrast | Keep foregrounded in Sci Data title/abstract/Data Records; avoid “spectra database” wording |
| **Formula/structure errors** | **High for Technical Validation** | ~5.6% C-count impossibilities in n=500 resolved sample; 35% structure coverage | Run full `quality.py` audit; quarantine failures; report rates; optional human structure audit n≥100–300 |
| **Concurrent datasets (scoop)** | **Medium** | NMRexp (NMR), NMRSpec (incl. IR), computational IR–NMR Sci Data papers | Position IRexp as **largest redistributable experimental IR band-list + multimodal** resource; cite peers; don’t claim “first spectra database” |
| **Split with ICLR / dual publication** | **Medium–High if mishandled** | Sci Data allows complementary papers; ICLR forbids substantially similar dual sub; JCIM manuscript already frames resource+bench+diagnosis | See §F.4; publish Sci Data as data-only **before or with clear separation from** ICLR; do not let JCIM burn the dataset DOI first without Sci Data plan |
| **Zenodo / HF licence metadata wrong** | **High** | `.zenodo.json` licence `cc-by-4.0` only; HF stamps CC-BY on PMC | Fix before archival DOI |
| **Chemotion ShareAlike contamination** | **Medium** | 1,888 SA records mixed in combined file | Physical split files; Usage Notes: combined redistribution → CC-BY-SA |

---

## F. Verdict for Rodrigo

### 1. Can we publish IRexp in Scientific Data?

**Yes with conditions — Risky as currently shipped.**

- **Scientific fit:** Yes — experimental literature-mined multimodal spectral *lists* are in scope (NMRexp precedent).  
- **Legal/editorial readiness:** **Not yet** — the CC-BY-overclaim is a submit-blocking defect once Nature checks PMC licence diversity.  
- **Current JCIM-shaped manuscript:** Wrong article type; must be rewritten as a Data Descriptor (no LLM diagnosis results).

### 2. Top 3 issues that will raise questions

1. **“All PMC-OA is CC-BY-4.0”** — empirically false (~19% NC/empty in sample); HF already public under that claim.  
2. **How data were obtained** — Scrapling anti-bot stack in-repo vs Methods’ clean S3 story; need one honest, narrow provenance narrative.  
3. **Technical Validation depth** — n=60 transcription only; deferred recall; structure error rate not reported; far thinner than NMRexp.

### 3. Minimum work before submission

**Must (blocker):**

1. Join all 15,416 PMCIDs → licence; build `oa_comm` / `oa_noncomm` / `other` pools; **exclude NC from any CC-BY commercial release** (or release NC under NC with clear tagging).  
2. Correct PAPER / NOTICE / README / HF / Zenodo licence language; stamp every record.  
3. Mint Zenodo with honest multi-licence + file inventory.  
4. Write a true Data Descriptor (Background, Methods, Data Records, Technical Validation, Usage Notes) — strip diagnosis.

**Should (reviewer survival):**

5. Run corpus-wide structure–NMR consistency audit; report & quarantine.  
6. Extraction-recall audit on a human-readable paper sample (even n=30–50 papers).  
7. Document Chemotion peak-picking.  
8. Enlarge transcription audit (e.g. n≥200) or add field-level error taxonomy.

**Nice (credibility):**

9. Expert structure spot-check n≥100.  
10. Compare explicitly to NMRexp / computational IR–NMR Sci Data sets in Background.

### 4. Two-paper split: Sci Data + ICLR — dual publication / scoop?

| Concern | Assessment |
|---|---|
| **Sci Data ↔ research paper dual publication** | **Allowed** if Data Descriptor is complementary and does not merely rehash a prior paper that already published the dataset identifier. Cite and disclose related ICLR/JCIM manuscript; use Sci Data complementary checklist. |
| **Order** | Prefer **Sci Data first** (or simultaneous), then ICLR diagnosis citing the Sci Data DOI. If a **JCIM resource paper publishes the Zenodo DOI first**, Sci Data may say users already have access via that paper → reject or demand substantial new validation content. |
| **ICLR dual submission** | ICLR forbids identical/substantially similar concurrent submissions. A **data-only Sci Data** + an **ICLR diagnosis/benchmark** paper is usually fine **if** the ICLR paper does not paste the Data Descriptor and Sci Data does not paste the LLM results. Cross-cite; different titles/abstracts/contributions. |
| **Scoop** | NMRexp owns large experimental NMR. IRexp’s differentiator is **IR band lists + open redistribution + multimodal**. Concurrent NMRSpec-style IR-in-literature mines: cite and differentiate (licence, IR focus, band-list object, benchmark coupling). |
| **Current SUBMISSION.md** | Still targets **JCIM** as primary. The two-paper split is a **strategy change** — align venue plan before burning ChemRxiv/JCIM framing that makes Sci Data “prior disclosure of the same dataset.” |

---

## Appendix — key file paths

| Role | Path |
|---|---|
| Manuscript (JCIM-shaped) | `docs/PAPER.md` |
| Submission checklist | `docs/SUBMISSION.md` |
| Data licence notice | `data/NOTICE` |
| Code licence | `LICENSE` (MIT) |
| Corpus | `data/irexp/irexp.jsonl.gz` |
| Resolved | `data/irexp_resolved/irexp_resolved.jsonl.gz` |
| Licence split script | `scripts/split_license_pools.py` |
| Transcription audit | `scripts/audit_extraction.py`, `data/audit/extraction_audit.json` |
| Mining package | `spectro_scraper/` (`pipeline.py`, `extract.py`, `normalize.py`, `fetch.py`, `discover.py`, `quality.py`) |
| HF publish | `scripts/publish_hf.py`, `data/irexp_release/README_HF.md` |
| Zenodo metadata | `.zenodo.json` |
| Expert audit (deferred) | `docs/EXPERT_AUDIT_PROTOCOL.md`, `data/audit/` |

---

## Bottom line for the PI discussion

IRexp **can** be a Scientific Data paper: the object is right, analogues exist, counts are real, and the band-list honesty vs SDBS is a strength.  

What will get you in trouble is not “literature mining” per se — NMRexp did that at larger scale — but **overclaiming permissive licences on a mixed PMC-OA pool that is already public on Hugging Face as CC-BY**, plus a **thinner validation story** and a **messy scraper narrative**. Fix licence truth first; then rewrite as a Data Descriptor; only then is the Sci Data + ICLR split clean.
