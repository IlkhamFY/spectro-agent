#!/usr/bin/env python3
"""
Build complete experimental NMR + IR + structure triples from the paper crawl.

NMRexp gives NMR+structure at scale but no IR. The paper crawl (data/bulk) is the
complementary asset: records with **co-reported NMR and IR from the same paper**.
Here we resolve their compound names to structures (OPSIN, in one batched JVM
call) so each becomes a complete Spectro triple:

    { smiles, selfies, h_nmr, c_nmr, ir_bands_cm-1 (real, experimental), doi }

and report the InChIKey overlap with the NMRexp set (those NMRexp molecules can
be augmented with real IR).

    python scripts/build_ir_triples.py
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from py2opsin import py2opsin                                   # noqa: E402
from spectro_scraper.normalize import canonical_and_keys       # noqa: E402

CRAWL = "data/bulk/spectra.jsonl"
NMREXP = "data/training_nmrexp/train.jsonl"
OUT = Path("data/training_ir")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    recs = []
    for line in open(CRAWL):
        r = json.loads(line)
        if r.get("ir_bands") and r.get("name") and (r.get("spectro_h") or r.get("spectro_c")):
            recs.append(r)
    print(f"IR-paired records with names: {len(recs):,}", flush=True)

    names = [r["name"] for r in recs]
    smiles: list[str] = []
    CH = 2000
    for i in range(0, len(names), CH):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out = py2opsin(names[i:i + CH])
        smiles.extend(out if isinstance(out, list) else [out])
        print(f"  OPSIN {min(i+CH, len(names)):,}/{len(names):,}", flush=True)

    # NMRexp InChIKeys, to measure how many triples can augment NMRexp with IR.
    nmrexp_ik = set()
    if Path(NMREXP).exists():
        for line in open(NMREXP):
            ik = json.loads(line).get("id")
            if ik:
                nmrexp_ik.add(ik)

    jf = (OUT / "train.jsonl").open("w")
    seen = set(); kept = 0; overlap = 0
    for r, smi in zip(recs, smiles):
        if not smi:
            continue
        canon, inchikey, selfies = canonical_and_keys(smi)
        if not (selfies and inchikey):
            continue
        if inchikey in seen:
            continue
        seen.add(inchikey)
        if inchikey in nmrexp_ik:
            overlap += 1
        jf.write(json.dumps({
            "id": inchikey,
            "smiles": canon or smi,
            "selfies": selfies,
            "h_nmr": r.get("spectro_h"),
            "c_nmr": r.get("spectro_c"),
            "ir_bands_cm-1": r.get("ir_bands"),          # REAL experimental IR
            "source_doi": r.get("source_doi"),
            "source": "paper-crawl",
            "in_nmrexp": inchikey in nmrexp_ik,
        }, ensure_ascii=False) + "\n")
        kept += 1
    jf.close()
    stats = {"ir_triples": kept,
             "with_real_ir": kept,
             "overlap_with_nmrexp": overlap,
             "note": "experimental NMR+IR+structure from paper crawl; "
                     f"{overlap} also in NMRexp (can add IR to those)"}
    (OUT / "stats.json").write_text(json.dumps(stats, indent=2))
    print(f"\nWrote {kept:,} complete NMR+IR+structure triples -> {OUT}/train.jsonl")
    print(f"  {overlap:,} share an InChIKey with the NMRexp set (IR-augmentable)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
