# spectro-agent — live walkthrough

**Watch the agent read a real, public chemistry paper and turn it into
training-ready structured spectra — in seconds, fully open, no browser.**

<p align="center">
  <img src="docs/demo.svg" alt="spectro-agent parsing a Beilstein paper end-to-end" width="850">
</p>

> The animation above is a real recording of `python scripts/demo.py` against
> [Beilstein J. Org. Chem. **2024**, 20, 188](https://doi.org/10.3762/bjoc.20.188)
> (*Heterocycle-guided synthesis of m-hetarylanilines*, CC-BY).
> Static frame: [`docs/demo.png`](docs/demo.png) · full text trace:
> [`docs/demo_run.txt`](docs/demo_run.txt).

---

## What you're watching — six stages, one paper

| # | Stage | What the agent does |
|---|-------|---------------------|
| **1** | **DISCOVER** | Resolve a DOI through the open **CrossRef** API → title, publisher, license. A per-publisher *adapter* (here `beilstein`) knows exactly where that journal hides its PDF + Supporting-Information layout. |
| **2** | **FETCH** | Pull the 5.6 MB SI PDF with **Scrapling**'s TLS/JA3 browser-impersonation. The server returns **HTTP 200** — *plain `curl` to the same URL returns `403`* (Cloudflare). No headless browser, no Selenium. |
| **3** | **READ** | Extract and normalise ~40 k characters of experimental-section text from the PDF (dash/space folding, de-hyphenation, page-marker stripping). |
| **4** | **EXTRACT** | Segment the text into per-compound blocks and regex-parse **IR bands + ¹H / ¹³C NMR** for each. One paper → **29 compounds with spectra** (29 ¹H, 29 ¹³C, 20 IR). |
| **5** | **RESOLVE** | Turn each IUPAC name into structure: **OPSIN** name→SMILES, then **RDKit** canonical + InChIKey, then **SELFIES**. → **29 structures**, of which **20 are full multimodal** (IR + ¹H + ¹³C + structure). |
| **6** | **OUTPUT** | Emit one clean, Spectro-ready JSON record — exactly the format the [Spectro](https://chemrxiv.org/doi/full/10.26434/chemrxiv-2024-37v2j) molecule-elucidation model consumes. |

The result for this single paper:

```json
{
  "name": "N-Benzyl-5-(3-phenyl-1,2,4-oxadiazol-5-yl)-[1,1'-biphenyl]-3-amine",
  "label": "3aa",
  "smiles": "c1ccc(CNc2cc(-c3ccccc3)cc(-c3nc(-c4ccccc4)no3)c2)cc1",
  "selfies": "[C][=C][C][=C][Branch2]…",
  "inchikey": "OTNKFQPXPWYHOF-UHFFFAOYSA-N",
  "h_nmr": "δ 8.26-8.11 (2H, m), 7.83 (1H, d), 7.61 (2H, dd), … 4.48 (2H, s)",
  "c_nmr": "δ 176.2 (1C, s), 169.1 (1C, s), 148.5 (1C, s), …",
  "ir_bands_cm-1": [3432.0, 1613.0, 1581.0, 1562.0, 1464.0, 1455.0, 1445.0],
  "source_doi": "10.3762/bjoc.20.188"
}
```

---

## Why it's worth advertising

- **Real, not synthetic.** Every spectrum is *experimental* — scraped from what
  chemists actually measured and published. No computed/DFT IR. The Nature NMRexp
  study showed experimental data is what makes these models work.
- **Cloudflare-proof, browser-free.** TLS-impersonation gets `200`s where `curl`
  gets `403`s — at a fraction of the cost and flakiness of a headless browser.
- **Closes the full loop.** Not just "scrape text" — name → SMILES → SELFIES +
  InChIKey, with physics quality-gates, so the output is *trainable as-is*.
- **Fully open & reproducible.** Only open-access (CC-BY) papers, public APIs
  (CrossRef, NCBI PMC), and open tools (Scrapling, OPSIN, RDKit, SELFIES).

### What this scales to
Run across the open-access corpus, the same pipeline has produced **IRexp** —
the largest open, NMR-paired experimental-IR dataset we know of:

| | count |
|---|--:|
| Unique real experimental IR records | **119,345** |
| …with co-reported NMR | 87,075 |
| …full multimodal (IR + NMR + structure) | **27,856** |

(See [`data/irexp_release/`](data/irexp_release/). The closest comparable —
Wiley KnowItAll — is closed and licensed; this is the open counterpart.)

---

## Reproduce it yourself

```bash
# default: the Beilstein paper shown above
python scripts/demo.py

# any DOI; --pause adds delay between stages (nice for screen-recording)
python scripts/demo.py --doi 10.3762/bjoc.20.188 --pause 0.9
```

To regenerate the animation (requires `termtosvg`):

```bash
termtosvg docs/demo.svg -g 108x70 -c "python scripts/demo.py --pause 0.9"
```
