#!/usr/bin/env python3
"""Compile docs/scientific_data/scientific_data.tex → scientific_data.pdf.

TeX is the Overleaf source of truth. Markdown (SCIENTIFIC_DATA.md) remains working notes.
Does not touch docs/paper.tex, docs/PAPER.md, or scripts/build_pdf.py.

Requires tectonic (preferred) or xelatex+bibtex. Soft-fails with instructions if missing.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_DIR = os.path.join(ROOT, "docs/scientific_data")
TEX = os.path.join(TEX_DIR, "scientific_data.tex")
OUT = os.path.join(TEX_DIR, "scientific_data.pdf")


def _engine() -> str | None:
    env = os.environ.get("PDF_ENGINE")
    if env and (os.path.isfile(env) or shutil.which(env)):
        return env if os.path.isfile(env) else shutil.which(env)
    for cand in ("/tmp/tectonic", "tectonic", "xelatex"):
        if cand.startswith("/") and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
        found = shutil.which(cand)
        if found:
            return found
    return None


def _run(cmd: list[str], cwd: str) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    if not os.path.isfile(TEX):
        print(f"missing {TEX}", file=sys.stderr)
        return 1
    engine = _engine()
    if not engine:
        print("no PDF engine (tectonic/xelatex); install tectonic or TeX Live",
              file=sys.stderr)
        return 3

    print(f"building {OUT} from {TEX} with {engine} …")
    base = os.path.basename(TEX)
    if os.path.basename(engine) == "tectonic" or engine.endswith("/tectonic"):
        rc = _run(
            [engine, "--keep-logs", "--keep-intermediates", "-o", TEX_DIR, TEX],
            cwd=TEX_DIR,
        )
    else:
        # xelatex + bibtex loop
        for _ in range(2):
            rc = _run([engine, "-interaction=nonstopmode", base], cwd=TEX_DIR)
            if rc != 0:
                break
        bibtex = shutil.which("bibtex")
        if bibtex and os.path.isfile(os.path.join(TEX_DIR, "scientific_data.aux")):
            _run([bibtex, "scientific_data"], cwd=TEX_DIR)
        for _ in range(2):
            rc = _run([engine, "-interaction=nonstopmode", base], cwd=TEX_DIR)

    if not os.path.isfile(OUT):
        print("build produced no PDF", file=sys.stderr)
        return 4
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
