# spectro-agent

**An efficient agent that harvests paired ¹H / ¹³C NMR + IR spectra from public
chemistry papers — in the exact format the [Spectro](https://chemrxiv.org/doi/full/10.26434/chemrxiv-2024-37v2j)
molecule-elucidation model consumes.**

Built on [Scrapling](https://github.com/D4Vinci/Scrapling) for Cloudflare-proof,
**browser-free** fetching, with OPSIN/RDKit/SELFIES to close the loop from a
reported compound all the way to a training-ready `(spectra → structure)` pair.

---

## 1. The problem, understood deeply

### What Spectro is
Spectro (Chacko, Sondhi, Praveen, Luska & Vargas-Hernández, ChemRxiv 2024,
`10.26434/chemrxiv-2024-37v2j`) is a **multi-modal molecule-elucidation model**.
Given a molecule's spectra it predicts the structure:

```
  IR spectrum  ──►  j-IR-vis (CNN, pretrained to detect functional-group peaks, F1≈91%)
                                   │  IR_z embedding
  ¹³C NMR text ──►  Text encoder (LLM2Vec, NMR treated as text)
  ¹H  NMR text ──►        │  NMR_z embedding
                          ▼
                   Molecule Decoder ──►  SELFIES ──► SMILES (the structure)
```

The NMR is fed **as text** — literally the chemical-shift strings chemists write
in papers:

```
¹³C NMR: δ 73.9 (1C, s), 94.8 (1C, s), 126.5 (2C, s), 127.8 (1C, s), 128.4 (2C, s), 134.6 (1C, s)
¹H  NMR: δ 5.47 (1H, s), 7.29–7.51 (5H, m)
```

### The bottleneck (and why an agent helps)
From the paper's own Methodology section:

> *"The dataset used to train Spectro and j-IR-vis was compiled from multiple
> sources. **IR spectra were downloaded from NIST as JDX files** … NMR chemical
> shift information [was scraped] **using Selenium WebDriver**."*

The whole approach was capped at **6,833 molecules** (test set 1,366) — and
assembling even that was painful: a **Selenium browser** driving one page at a
time to scrape shift lists, plus manual NIST IR downloads, hand-joined into a
YAML file.

That is exactly the bottleneck a scraping agent removes. Public chemistry papers
contain a *vast*, under-exploited reservoir of the precise data Spectro needs:
every methodology / total-synthesis paper's **Supporting Information** reports,
per compound:

```
4-phenylbutan-2-one (3a). Colourless oil (85%).
¹H NMR (400 MHz, CDCl₃) δ 7.85 (d, J = 8.0 Hz, 2H), 7.29–7.51 (m, 5H) …
¹³C NMR (101 MHz, CDCl₃) δ 208.1, 141.2, 128.5 …
IR (neat) ν 3024, 1715, 1602 cm⁻¹.  HRMS (ESI) calcd for C₁₀H₁₂O …
```

A *single* SI PDF routinely yields **30–100 compounds**, each with ¹H + ¹³C NMR
(and often IR). So the data exists — the job is to fetch and parse it
efficiently, at scale, without drowning in anti-bot walls.

---

## 2. Genius solutions

The design choices that make this fast, robust, and faithful to Spectro:

| # | Idea | Why it's a win |
|---|------|----------------|
| **1** | **TLS-impersonation instead of a browser.** `Fetcher.get(impersonate='chrome')` sends a real Chrome JA3/TLS fingerprint via curl_cffi. | ChemRxiv is behind Cloudflare — plain `curl` gets **HTTP 403**, Scrapling gets **200** (verified). No webdriver, no headful browser. **Milliseconds, not seconds; fully parallelisable.** This *replaces* Spectro's Selenium. |
| **2** | **Decouple discovery from fetching.** Enumerate papers via fully-open scholarly APIs (CrossRef / OpenAlex), which are *not* Cloudflare-gated, and reserve Scrapling for the protected PDF download. | No anti-bot fight for metadata; canonical PDF URLs handed to us directly. |
| **3** | **SI-first, highest-yield targeting.** Go straight for the Supporting-Information PDF, where the per-compound data lives. | **100+ spectra from <5 HTTP requests** instead of crawling thousands of pages. Maximum data per byte. |
| **4** | **IR×NMR co-occurrence scoring.** Rank candidate papers by how many compounds report *both* modalities before spending bandwidth. | Spend requests only on the richest sources; surface paired (NMR+IR) samples — Spectro's ideal training input. |
| **5** | **Format normaliser to the *exact* Spectro schema.** Reorder journal `δ 7.85 (d, J, 2H)` → Spectro `7.85 (2H, d)`; ¹³C → `(nC, s)`. | Harvest drops straight into their training pipeline — closes the loop with the paper. |
| **6** | **Structure resolution = the missing label.** IUPAC name → **OPSIN** → SMILES → **RDKit** (InChIKey) → **SELFIES**. | SELFIES is Spectro's decoder target, and InChIKey gives free cross-source dedup + **molecule-level join of paper-NMR with NIST-IR** — precisely how Spectro built its set. |
| **6½** | **NIST IR capstone** — fetch IR JDX from **NIST** (Spectro's *own* IR source) keyed by InChIKey, with a self-contained JCAMP-DX (SQZ/DIF/DUP) decoder. | Reconstructs Spectro's exact multi-modal data build (paper-NMR ⋈ NIST-IR), but via Scrapling instead of Selenium + manual downloads. *Insight surfaced:* NIST only catalogues **common** molecules — novel paper compounds won't match, which is exactly why **scraping IR straight from the paper (222 paired records here) beats the NIST join** for real-world chemistry. |
| **7** | **Two-tier fetch with stealth fallback.** Escalate to `StealthyFetcher` (camoufox, solves Cloudflare Turnstile) **only** when TLS impersonation is genuinely blocked. | Pay the heavy browser cost ~never; stay fast by default, robust under pressure. |
| **8** | **Polite, resilient, reproducible.** Per-host rate-limit, exponential-backoff retries, on-disk response cache (re-runs never re-hit servers), full provenance (DOI + URL + licence) on every record. | Production-grade and citation-ready; nearly all sources are CC-BY. |

---

## 3. Results (checked-in harvest)

From **15 seed papers / 29 PDFs (≈57 MB)**, with zero fetch failures and no
browser launched (all via TLS impersonation):

| Metric | Count |
|--------|------:|
| **NMR records scraped from public papers** | **373** |
| **…with co-reported IR (paired NMR + IR)** | **222** |
| …with resolved structure (SMILES + SELFIES + InChIKey) | 41 |
| NIST IR spectra joined (demo panel of common molecules) | 10 |

**The goal — "more than 100 NMR and IR spectra from public papers" — is met
~3.3× over** (and ~2× over on the stricter *paired* count). Outputs are in
`data/output/`.

#### Scaled run (`data/scaled/`, via `scripts/scale_harvest.py`)

Sweeping 20 topics across both Beilstein journals with the quality gate on:

| Metric | Count |
|--------|------:|
| papers / PDFs fetched | 167 / 258 (409 MB) |
| **NMR records** | **1,205** |
| **…with IR** | **537** |
| with structure (SMILES+SELFIES+InChIKey) | 76 |
| quarantined by quality gate | 8 |
| **quality score** | **98.9/100** (¹³C obs/unique median **1.0**, SELFIES round-trip 76/76, 0 dupes, 0 fetch failures) |

i.e. **>12× the goal**, with quality holding at scale — a direct demonstration
that the pipeline runs unattended for ~20 min and stays clean automatically.

### Data quality (`spectro_scraper/quality.py`, score **99/100**)

Quality is audited automatically on every harvest, the strongest axis being a
**physics-based cross-check against the resolved structure** — a molecule's ¹³C
signal count cannot exceed its carbon count, and its ¹H integration cannot
exceed its hydrogen count, so the structure itself becomes ground truth:

| Check | Result |
|---|---|
| ¹H shifts in −5…17.5 ppm | **99.97%** valid (the 0.03% are real chelated-enol OH ~16 ppm) |
| ¹³C shifts in −10…235 ppm | **100%** valid |
| IR bands in 350…4000 cm⁻¹ | **100%** valid (0/3324 out of range) |
| ¹³C signals ≤ carbon count | **40/40**, 0 impossible; obs/symmetry-unique median **0.94** |
| ¹H integration vs. formula | 11 exact, 29 under (exchangeable OH/NH — benign), 1 over |
| SELFIES → SMILES round-trip | **41/41** |
| InChIKey duplicates | **0** |

Getting there surfaced and fixed three real parser bugs, each caught by the
audit: ¹³C lists bleeding into the next compound's name; the Bruker `δH/δC`
anchor firing inside Greek-lettered ¹³C assignments (`CδH3`); and SI page
markers (`S17`) inlined by PDF extraction being misread as shifts. Run it with
`python -m spectro_scraper.quality data/output/spectra.jsonl`.

## 4. Architecture

```
spectro_scraper/
├── discover.py     # open scholarly APIs (CrossRef) → Paper(doi, pdf_links, …)
├── fetch.py        # ResilientFetcher: Scrapling + retry/backoff + cache + stealth fallback
├── pdf.py          # download + robust PDF text extraction (pypdf)
├── sources/        # per-source adapters that locate main + SI PDFs
│   ├── beilstein.py   #   Beilstein JOC (gold OA, IR+NMR-rich, predictable SI URLs)
│   ├── chemrxiv.py    #   ChemRxiv  (the task's named source; Cloudflare-proof)
│   └── generic.py
├── extract.py      # regex engine: segment compounds, parse ¹H/¹³C NMR, IR, HRMS, yield
├── normalize.py    # Spectro-format strings + OPSIN→SMILES→SELFIES + InChIKey
├── pipeline.py     # orchestration + dedup + JSONL/Spectro output + stats
└── cli.py          # command-line entry point
```

The extractor handles the real reporting conventions seen in the wild:
standard `1H NMR (…) δ …`, the Bruker `δH(…)/δC(…)` notation, `δ =` vs `δ`,
unicode dash/space zoo, PDF line-break hyphenation, IR reported *before or after*
NMR, and `IR (ATR) / FT-IR / vmax = / cm⁻¹` variants.

---

## 5. Usage

```bash
pip install -r requirements.txt
# (optional, for stealth fallback) scrapling install   # downloads camoufox

# Harvest the curated, IR+NMR-rich seed papers (>100 spectra):
python -m spectro_scraper.cli --seeds data/seeds.yaml --target 150

# ...plus the Spectro-style NIST IR join (common molecules):
python -m spectro_scraper.cli --seeds data/seeds.yaml --nist-ir

# A single DOI (ChemRxiv or any journal):
python -m spectro_scraper.cli --doi 10.3762/bjoc.17.181

# Discover + harvest by topic from CrossRef:
python -m spectro_scraper.cli --search "total synthesis" --issn 1860-5397 --rows 25

# Demonstrate the NIST IR capstone end-to-end (saves JDX files):
python scripts/nist_ir_demo.py

# Audit data quality (structure cross-checks, shift validity, dedup):
python -m spectro_scraper.quality data/output/spectra.jsonl
```

### Scaling out (multi-journal, crash-safe)

```bash
# Sweep many topics across both Beilstein gold-OA journals (bjoc + bjnano),
# with the quality gate on and disk checkpointing every 50 records.
# Re-run with the same --out to resume; quarantined records are written aside.
python scripts/scale_harvest.py --target 1500 --out data/scaled

# Any harvest can enable the per-record validation gate:
python -m spectro_scraper.cli --search synthesis --issn 1860-5397 --quality-gate
```

Measured throughput is ~6–7 s/paper single-stream (mostly per-host politeness),
~6 records/paper; the binding constraint is courtesy + IR scarcity, not compute,
so reach scales with the number of OA hosts crawled in parallel. See the gold-OA
corpus estimate in the PR description (~10⁵–10⁶ addressable papers).

### Outputs (`data/output/`)
* `spectra.jsonl` — full records (raw + parsed peaks + IR bands + provenance).
* `spectra_spectro.jsonl` — the **Spectro-ready** view:

```json
{"id":"WXYZ...-N","label":"3a","smiles":"CC(=O)CCc1ccccc1","selfies":"[C][C]...",
 "h_nmr":"δ 7.85 (2H, d), 7.29-7.51 (5H, m), 2.96 (2H, t), 2.13 (3H, s)",
 "c_nmr":"δ 208.1 (1C, s), 141.2 (1C, s), ...",
 "ir_bands_cm-1":[3024,1715,1602,1452],"source_doi":"10.3762/bjoc..."}
```

* `spectra_report.json` — harvest statistics + fetcher telemetry.

---

## 6. Reproducing the harvest

`data/seeds.yaml` lists open-access organic-chemistry papers selected for high
NMR yield, with a subset confirmed IR-rich, plus the Spectro preprint itself as a
demonstration of the (Cloudflare-gated) ChemRxiv path. `data/output/` is checked
in so the result is inspectable without re-running.

## 7. Ethics & licensing

Only **open-access** papers (CC-BY and similar) are harvested, via public
metadata APIs and publisher-hosted PDFs, with polite per-host rate limiting and
exponential backoff. Every record retains its source DOI, URL and licence so the
derived dataset stays attributable and reusable.

## 8. Tests

```bash
python tests/test_extract.py     # 8 golden-string tests, no network needed
```
