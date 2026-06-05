#!/usr/bin/env python3
"""
Demonstrate the NIST IR capstone end-to-end.

Spectro built its IR set by downloading JDX files from NIST and joining them to
NMR by molecule. This script does exactly that -- via Scrapling instead of
Selenium/manual downloads -- for a panel of common molecules (the kind that
populate Spectro's 6,833-molecule set and that NIST actually catalogues),
saving the raw JCAMP-DX plus a decoded curve summary.

    python scripts/nist_ir_demo.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.fetch import ResilientFetcher          # noqa: E402
from spectro_scraper.sources.nist import NISTIRClient, parse_jdx  # noqa: E402

# (name, InChIKey) -- common organics present in NIST with IR spectra.
PANEL = [
    ("benzaldehyde",  "HUMNYLRZRPPJDN-UHFFFAOYSA-N"),
    ("aniline",       "PAYRUJLWNCNPSJ-UHFFFAOYSA-N"),
    ("indole",        "SIKJAQJRHWYJAI-UHFFFAOYSA-N"),
    ("phenol",        "ISWSIDIOOBJBQZ-UHFFFAOYSA-N"),
    ("toluene",       "YXFVVABEGXRONW-UHFFFAOYSA-N"),
    ("benzoic acid",  "WPYMKLBDIGXBTP-UHFFFAOYSA-N"),
    ("nitrobenzene",  "LQNUZADURLCDLV-UHFFFAOYSA-N"),
    ("anisole",       "RDOXTESZEPMUJZ-UHFFFAOYSA-N"),
    ("styrene",       "PPBRXRYQALVLMV-UHFFFAOYSA-N"),
    ("acetophenone",  "KWOLFJPFCHCOCG-UHFFFAOYSA-N"),
    ("p-cresol",      "IWDCLRJOBJJRNH-UHFFFAOYSA-N"),
    ("cyclohexanone", "JHIVVAPYMSGYDF-UHFFFAOYSA-N"),
]


def main() -> int:
    client = NISTIRClient(ResilientFetcher(min_interval=0.5))
    out = []
    for name, ik in PANEL:
        info = client.fetch_ir(inchikey=ik, name=name, save_as=ik)
        if not info:
            print(f"  -- {name:14s}: no NIST IR")
            continue
        parsed = parse_jdx(Path(info["jdx_path"]).read_text(encoding="latin-1"))
        print(f"  ok {name:14s}: NIST {info['nist_id']:>9s}  "
              f"{info['npoints']:4d} pts  {info['xunits']}  "
              f"{info['x_range'][0]:.0f}-{info['x_range'][1]:.0f}  "
              f"-> {Path(info['jdx_path']).name}")
        out.append({"name": name, "inchikey": ik, **{k: info[k] for k in
                    ("nist_id", "jdx_path", "npoints", "xunits", "x_range")}})

    Path("data/output").mkdir(parents=True, exist_ok=True)
    Path("data/output/nist_ir_index.json").write_text(json.dumps(out, indent=2))
    print(f"\n{len(out)}/{len(PANEL)} molecules joined to a NIST IR spectrum "
          f"(JDX files in data/output/nist_ir/)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
