#!/usr/bin/env python3
"""
Ingest the Chemotion FT-IR deposit (RADAR4Chem, DOI 10.22000/OGoEQGlsZGElrgst,
CC-BY-SA-4.0) into the IRexp schema.

Chemotion is an open electronic-lab-notebook repository: chemists deposit the
*real measured* spectra that back their publications. The IR collection holds
2,116 ATR-IR analyses, each with a canonical SMILES and an author-curated band
list (in the record's ``content`` field, e.g. "IR (ATR) = 2972 (w), 1709 (m),
... cm-1"). That is the gold-standard, experimentally-measured counterpart to the
band lists we scrape from paper PDFs -- so we parse it with the *same* extractor
for consistency, resolve the structure (RDKit canonical + InChIKey + SELFIES),
and emit IRexp rows.

    python scripts/chemotion_to_irexp.py \
        --root data/chemotion/extracted/10.22000-OGoEQGlsZGElrgst/data/dataset \
        --out data/chemotion/chemotion_ir.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.extract import (  # noqa: E402
    _IR_RE, _capture_payload, _parse_ir_bands, _is_instrument_range,
    _looks_like_band_list, normalize_text)
from spectro_scraper.normalize import canonical_and_keys  # noqa: E402

DOI = "10.22000/OGoEQGlsZGElrgst"
LICENSE = "CC-BY-SA-4.0"


def _content_text(c: str) -> str:
    """Flatten a Chemotion Quill-delta ``content`` field into plain text."""
    try:
        ops = json.loads(c)["ops"]
        return "".join(o["insert"] for o in ops if isinstance(o.get("insert"), str))
    except Exception:
        return ""


def _bands_from_content(content: str):
    """Parse an author-curated IR band list out of a record's content, using the
    exact same gate as the paper-scraping path (so bands are comparable)."""
    txt = normalize_text(_content_text(content))
    m = _IR_RE.search(txt)
    if not m:
        return None
    payload = _capture_payload(txt, m.end())
    bands = _parse_ir_bands(payload)
    if (bands and not _is_instrument_range(bands, payload)
            and _looks_like_band_list(payload) and len(bands) >= 4):
        # de-dup + sort for a stable record (bands are a set of wavenumbers)
        return sorted(set(bands))
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/chemotion/extracted/"
                    "10.22000-OGoEQGlsZGElrgst/data/dataset")
    ap.add_argument("--out", default="data/chemotion/chemotion_ir.jsonl")
    args = ap.parse_args(argv)

    meta = json.load(open(Path(args.root) / "meta_data.json"))
    print(f"loaded {len(meta):,} Chemotion IR analyses", flush=True)

    # molecule -> richest band list (InChIKey keyed; some molecules have repeats)
    best: dict[str, dict] = {}
    parsed = no_bands = no_struct = 0
    for rec in meta:
        smi = rec.get("cano_smiles")
        if not smi:
            continue
        bands = _bands_from_content(rec.get("content", ""))
        if not bands:
            no_bands += 1
            continue
        canon, inchikey, selfies = canonical_and_keys(str(smi))
        if not (inchikey and selfies):
            no_struct += 1
            continue
        parsed += 1
        row = {
            "id": inchikey,
            "inchikey": inchikey,
            "has_structure": True,
            "smiles": canon or str(smi),
            "selfies": selfies,
            "ir_bands_cm-1": bands,
            "h_nmr": None, "c_nmr": None,        # join NMR by InChIKey separately
            "ir_source": "experimental",
            "source": "Chemotion",
            "source_doi": DOI,
            "license": LICENSE,
        }
        prev = best.get(inchikey)
        if prev is None or len(bands) > len(prev["ir_bands_cm-1"]):
            best[inchikey] = row

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for row in best.values():
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    stats = {
        "analyses_in": len(meta),
        "parsed_with_bands_and_structure": parsed,
        "unique_molecules": len(best),
        "skipped_no_bands": no_bands,
        "skipped_no_structure": no_struct,
        "source": "Chemotion FT-IR (RADAR4Chem)",
        "source_doi": DOI, "license": LICENSE,
    }
    (out.parent / "chemotion_stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    print(f"\nWrote {len(best):,} unique-molecule IR records -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
