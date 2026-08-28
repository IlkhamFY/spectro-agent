#!/usr/bin/env python3
"""Unified export: matplotlib figures and SVG schematics → PDF + 600 dpi PNG.

Uses Inkscape CLI when available; falls back to cairosvg for raster.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DPI_PNG = 600


def _inkscape() -> str | None:
    return shutil.which("inkscape")


def save_figure(path: str | Path, fig=None, dpi: int = DPI_PNG) -> Path:
    """Save matplotlib figure as PNG + PDF twins."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = fig or plt.gcf()
    stem = path.with_suffix("")
    png = stem.with_suffix(".png")
    pdf = stem.with_suffix(".pdf")
    fig.savefig(png, dpi=dpi, pad_inches=0.05, facecolor="white")
    fig.savefig(pdf, pad_inches=0.05, facecolor="white")
    return png


def save_svg_bundle(svg_path: str | Path, dpi: int = DPI_PNG) -> tuple[Path, Path, Path]:
    """Export SVG schematic to PDF + PNG (Inkscape preferred, cairosvg fallback)."""
    svg_path = Path(svg_path)
    stem = svg_path.with_suffix("")
    pdf = stem.with_suffix(".pdf")
    png = stem.with_suffix(".png")
    svg_path.parent.mkdir(parents=True, exist_ok=True)

    ink = _inkscape()
    if ink:
        _inkscape_export(ink, svg_path, pdf, export_type="pdf")
        _inkscape_export(ink, svg_path, png, export_type="png", dpi=dpi)
    else:
        _cairosvg_export(svg_path, pdf, png, dpi=dpi)

    return svg_path, pdf, png


def _inkscape_export(
    ink: str,
    src: Path,
    dest: Path,
    *,
    export_type: str,
    dpi: int = DPI_PNG,
) -> None:
    cmd = [
        ink,
        str(src),
        f"--export-type={export_type}",
        f"--export-filename={dest}",
    ]
    if export_type == "png":
        cmd.append(f"--export-dpi={dpi}")
    subprocess.run(cmd, check=True, capture_output=True)


def _cairosvg_export(src: Path, pdf: Path, png: Path, *, dpi: int) -> None:
    import cairosvg

    cairosvg.svg2pdf(url=str(src), write_to=str(pdf))
    scale = dpi / 96.0
    cairosvg.svg2png(url=str(src), write_to=str(png), scale=scale)
