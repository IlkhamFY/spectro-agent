#!/usr/bin/env python3
"""Light PDF build for the Scientific Data Descriptor (Track 2).

Markdown-first authoring lives in docs/scientific_data/SCIENTIFIC_DATA.md.
This script renders a single-column article PDF into
docs/scientific_data/scientific_data.pdf without touching docs/paper.pdf or
scripts/build_pdf.py (combined reading-copy pipeline).

Requires: pandoc + (tectonic or xelatex). Soft-fails with instructions if missing.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, "docs/scientific_data/SCIENTIFIC_DATA.md")
BIB = os.path.join(ROOT, "docs/scientific_data/references.bib")
OUT = os.path.join(ROOT, "docs/scientific_data/scientific_data.pdf")
CSL = os.path.join(ROOT, "docs/rsc.csl")


def _engine() -> str | None:
    env = os.environ.get("PDF_ENGINE")
    if env and shutil.which(env):
        return env
    for cand in ("/tmp/tectonic", "tectonic", "xelatex"):
        if cand.startswith("/") and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
        if shutil.which(cand):
            return cand
    return None


def main() -> int:
    if not os.path.isfile(MD):
        print(f"missing {MD}", file=sys.stderr)
        return 1
    try:
        import pypandoc  # noqa: F401
    except ImportError:
        print("pypandoc not installed; keep markdown-first or pip install pypandoc",
              file=sys.stderr)
        return 2
    engine = _engine()
    if not engine:
        print("no PDF engine (tectonic/xelatex); markdown remains the source of truth",
              file=sys.stderr)
        return 3

    extra = [
        f"--pdf-engine={engine}",
        "-V", "geometry:margin=1in",
        "-V", "fontsize=11pt",
        "-V", "documentclass=article",
        "--citeproc",
    ]
    if os.path.isfile(BIB):
        extra += [f"--bibliography={BIB}"]
    if os.path.isfile(CSL):
        extra += [f"--csl={CSL}"]

    with tempfile.TemporaryDirectory() as td:
        # pypandoc wants cwd-friendly paths; write via absolute OUT
        print(f"building {OUT} with {engine} …")
        import pypandoc
        pypandoc.convert_file(
            MD,
            "pdf",
            outputfile=OUT,
            extra_args=extra,
        )
    if not os.path.isfile(OUT):
        print("build produced no PDF", file=sys.stderr)
        return 4
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
