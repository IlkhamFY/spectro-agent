#!/usr/bin/env python3
"""
spectro-agent — narrated end-to-end demo.

Walks through how the agent parses a real chemistry paper and scrapes structured
spectra, printing each stage so the run can be screen-recorded (or its output
captured) for a walkthrough / advert:

    discover -> fetch (Cloudflare-proof) -> read experimental text ->
    extract per-compound IR + 1H/13C NMR -> resolve structure -> Spectro JSON

    python scripts/demo.py                 # default: a Beilstein J. Org. Chem. SI
    python scripts/demo.py --doi 10.3762/bjoc.20.188
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.fetch import ResilientFetcher          # noqa: E402
from spectro_scraper.pdf import extract_pdf_text            # noqa: E402
from spectro_scraper.extract import extract_records, normalize_text  # noqa: E402
from spectro_scraper.normalize import enrich, capabilities  # noqa: E402
from spectro_scraper.sources import select_adapter          # noqa: E402
from spectro_scraper.discover import lookup_doi             # noqa: E402

C = {"h": "\033[1;36m", "g": "\033[1;32m", "y": "\033[1;33m",
     "d": "\033[2m", "b": "\033[1m", "x": "\033[0m"}


def hr(title):
    print(f"\n{C['h']}{'━'*72}\n  {title}\n{'━'*72}{C['x']}", flush=True)


def typ(s, d=0.0):
    print(s, flush=True)
    if d:
        time.sleep(d)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doi", default="10.3762/bjoc.20.188")
    ap.add_argument("--pause", type=float, default=0.0, help="seconds between steps (for recording)")
    a = ap.parse_args(argv)
    P = a.pause
    f = ResilientFetcher(min_interval=0.5)

    print(f"\n{C['b']}┌─ spectro-agent ─ live parse of a public chemistry paper ─┐{C['x']}")
    print(f"{C['d']}  capabilities: {capabilities()}{C['x']}")

    # ── 1. DISCOVER ──────────────────────────────────────────────────────
    hr("1 │ DISCOVER  — find the paper via the open CrossRef API (no anti-bot)")
    typ(f"  DOI: {C['y']}{a.doi}{C['x']}", P)
    paper = lookup_doi(a.doi)
    typ(f"  title    : {paper.title[:70]}", )
    typ(f"  publisher: {paper.publisher}")
    adapter = select_adapter(paper)
    typ(f"  adapter  : {C['g']}{adapter.name}{C['x']}  (knows this publisher's PDF + SI layout)", P)

    # ── 2. FETCH ─────────────────────────────────────────────────────────
    hr("2 │ FETCH  — Scrapling TLS-impersonation (Cloudflare-proof, no browser)")
    cands = adapter.pdf_candidates(paper, f)
    si = [u for k, u in cands if k == "si"] or [u for _, u in cands]
    url = si[0]
    typ(f"  GET {C['d']}{url}{C['x']}")
    t0 = time.time()
    res = f.get(url, binary=True)
    dt = (time.time() - t0) * 1000
    typ(f"  -> HTTP {C['g']}{res.status}{C['x']}  {len(res.content)/1e6:.2f} MB  "
        f"in {dt:.0f} ms   (plain curl here returns 403)", P)

    # ── 3. READ ──────────────────────────────────────────────────────────
    hr("3 │ READ  — extract the experimental-section text from the PDF")
    text = normalize_text(extract_pdf_text(res.content))
    typ(f"  parsed {len(text):,} characters of experimental text")
    m = re.search(r"[A-Z][^.]{8,80}\((?:\d{1,3}[a-z]?)\)\.\s*[A-Z]", text)
    i = m.start() if m else text.find("1H NMR")
    excerpt = text[i:i+300]
    typ(f"\n  {C['d']}what the agent reads (raw):{C['x']}")
    typ(f"  {C['d']}{excerpt}…{C['x']}", P)

    # ── 4. EXTRACT ───────────────────────────────────────────────────────
    hr("4 │ EXTRACT  — segment compounds, parse IR + ¹H/¹³C NMR per compound")
    recs = extract_records(text)
    data = [r for r in recs if r.h_peaks or r.c_peaks or r.ir_bands]
    ir = sum(1 for r in data if r.ir_bands)
    typ(f"  found {C['g']}{len(data)}{C['x']} compounds with spectra  "
        f"({sum(1 for r in data if r.h_peaks)} with ¹H, "
        f"{sum(1 for r in data if r.c_peaks)} with ¹³C, {ir} with IR)", P)

    # ── 5. RESOLVE STRUCTURE ─────────────────────────────────────────────
    hr("5 │ RESOLVE  — compound name → SMILES (OPSIN) → SELFIES + InChIKey")
    for r in data:
        enrich(r)
    resolved = sum(1 for r in data if r.smiles)
    full = sum(1 for r in data if r.smiles and r.ir_bands and r.h_peaks and r.c_peaks)
    # showcase the most complete record: a full IR + ¹H + ¹³C + structure sample.
    sample = max(data, key=lambda r: (bool(r.ir_bands), bool(r.smiles),
                                      bool(r.h_peaks), bool(r.c_peaks),
                                      len(r.ir_bands)))
    typ(f"  resolved {C['g']}{resolved}{C['x']} structures  "
        f"→ {C['g']}{full}{C['x']} full multimodal (IR + ¹H + ¹³C + structure)", P)

    # ── 6. OUTPUT ────────────────────────────────────────────────────────
    hr("6 │ OUTPUT  — one structured, Spectro-ready record")
    rec = {
        "name": sample.name, "label": sample.label,
        "smiles": sample.smiles, "selfies": (sample.selfies or "")[:60] + "…",
        "inchikey": sample.inchikey,
        "h_nmr": sample.spectro_h, "c_nmr": (sample.spectro_c or "")[:70] + "…",
        "ir_bands_cm-1": sample.ir_bands[:10],
        "source_doi": a.doi,
    }
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    print(f"\n{C['b']}└─ one paper → {len(data)} structured spectra "
          f"({full} full multimodal), in seconds, fully open ─┘{C['x']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
