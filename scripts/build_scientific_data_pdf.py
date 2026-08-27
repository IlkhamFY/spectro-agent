#!/usr/bin/env python3
"""Compile docs/scientific_data/scientific_data.tex → scientific_data.pdf.

Uses the vendored Springer Nature sn-jnl class (pdflatex,sn-nature).
TeX is the Overleaf source of truth. Markdown (SCIENTIFIC_DATA.md) remains working notes.
Does not touch docs/paper.tex, docs/PAPER.md, or scripts/build_pdf.py.

Requires tectonic (preferred) or pdflatex/xelatex + bibtex. Soft-fails with instructions if missing.
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
    # Prefer tectonic, then pdflatex (matches [pdflatex] class option), then xelatex.
    for cand in ("/tmp/tectonic", "tectonic", "pdflatex", "xelatex"):
        if cand.startswith("/") and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
        found = shutil.which(cand)
        if found:
            return found
    return None


def _run(cmd: list[str], cwd: str, env: dict[str, str] | None = None) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=cwd, env=env)


def main() -> int:
    if not os.path.isfile(TEX):
        print(f"missing {TEX}", file=sys.stderr)
        return 1
    cls = os.path.join(TEX_DIR, "sn-jnl.cls")
    if not os.path.isfile(cls):
        print(f"missing vendored class {cls}; see docs/scientific_data/sn-article/",
              file=sys.stderr)
        return 2
    engine = _engine()
    if not engine:
        print("no PDF engine (tectonic/pdflatex/xelatex); install tectonic or TeX Live",
              file=sys.stderr)
        return 3

    # Ensure class + bst next to the .tex are found (Overleaf-equivalent flat layout).
    env = os.environ.copy()
    texinputs = env.get("TEXINPUTS", "")
    bstinputs = env.get("BSTINPUTS", "")
    env["TEXINPUTS"] = TEX_DIR + os.pathsep + texinputs
    env["BSTINPUTS"] = TEX_DIR + os.pathsep + bstinputs

    print(f"building {OUT} from {TEX} with {engine} …")
    base = os.path.basename(TEX)
    if os.path.basename(engine) == "tectonic" or engine.endswith("/tectonic"):
        rc = _run(
            [engine, "--keep-logs", "--keep-intermediates", "-o", TEX_DIR, TEX],
            cwd=TEX_DIR,
            env=env,
        )
    else:
        # latex + bibtex loop (pdflatex preferred for sn-jnl [pdflatex])
        for _ in range(2):
            rc = _run([engine, "-interaction=nonstopmode", base], cwd=TEX_DIR, env=env)
            if rc != 0:
                break
        bibtex = shutil.which("bibtex")
        if bibtex and os.path.isfile(os.path.join(TEX_DIR, "scientific_data.aux")):
            _run([bibtex, "scientific_data"], cwd=TEX_DIR, env=env)
        for _ in range(2):
            rc = _run([engine, "-interaction=nonstopmode", base], cwd=TEX_DIR, env=env)

    if not os.path.isfile(OUT):
        print("build produced no PDF", file=sys.stderr)
        return 4
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
