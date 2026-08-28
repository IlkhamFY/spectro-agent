#!/usr/bin/env python3
"""IRexp pipeline schematic — NMRexp Fig. 2 style (Panel A workflow + Panel B QC).

Hand-crafted vector SVG with icons, cleaning-rules table, and rejection examples.
"""
from __future__ import annotations

import sys
from pathlib import Path

import svgwrite

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

# Canvas: double-column @ 2× for crisp export
W, H = 920, 680
FONT = "Liberation Sans, Helvetica, Arial, sans-serif"
SHADOW = "#C8CDD2"
BG = "#FFFFFF"

C_HEADER = "#2E5F8F"
C_PMC = "#4A7EBB"
C_PROC = "#5B8DB8"
C_LIC = "#D97B32"
C_FAIL = "#C44E52"
C_OK = "#3D8B5E"
C_GREY = "#E8EAEC"


def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;")


def _panel_label(dwg, letter: str, x: float, y: float):
    dwg.add(dwg.text(letter, insert=(x, y), font_family=FONT, font_size="14px",
                      font_weight="bold", fill=fs.INK))


def _pdf_icon(dwg, x, y, scale=1.0):
    g = dwg.g(transform=f"translate({x},{y}) scale({scale})")
    g.add(dwg.rect(insert=(0, 4), size=(28, 34), rx=2, fill="white",
                    stroke=C_PMC, stroke_width=1.2))
    g.add(dwg.rect(insert=(0, 4), size=(28, 10), fill=C_PMC))
    g.add(dwg.text("PDF", insert=(14, 12), text_anchor="middle", font_family=FONT,
                    font_size="6px", font_weight="bold", fill="white"))
    g.add(dwg.line(start=(5, 20), end=(23, 20), stroke=fs.NOTE, stroke_width=0.8))
    g.add(dwg.line(start=(5, 25), end=(18, 25), stroke=fs.NOTE, stroke_width=0.8))
    dwg.add(g)


def _db_icon(dwg, x, y, color=C_PMC, label="DB"):
    g = dwg.g()
    g.add(dwg.ellipse(center=(x, y), r=(22, 6), fill=color, opacity=0.3))
    g.add(dwg.rect(insert=(x - 22, y), size=(44, 18), fill=color, opacity=0.2))
    g.add(dwg.ellipse(center=(x, y + 18), r=(22, 6), fill=color, opacity=0.35))
    g.add(dwg.ellipse(center=(x, y), r=(22, 6), fill="none", stroke=color, stroke_width=1.2))
    g.add(dwg.line(start=(x - 22, y), end=(x - 22, y + 18), stroke=color, stroke_width=1.2))
    g.add(dwg.line(start=(x + 22, y), end=(x + 22, y + 18), stroke=color, stroke_width=1.2))
    g.add(dwg.text(label, insert=(x, y + 9), text_anchor="middle", font_family=FONT,
                    font_size="7px", font_weight="bold", fill=fs.INK))
    dwg.add(g)


def _arrow_h(dwg, x0, y0, x1, y1, color=fs.INK, label: str = ""):
    dwg.add(dwg.line(start=(x0, y0), end=(x1 - 8, y1), stroke=color, stroke_width=1.4))
    dwg.add(dwg.polygon(points=[(x1, y1), (x1 - 9, y1 - 4), (x1 - 9, y1 + 4)], fill=color))
    if label:
        mx = (x0 + x1) / 2
        dwg.add(dwg.rect(insert=(mx - len(label) * 2.2, y0 - 16), size=(len(label) * 4.4, 12),
                          rx=2, fill="white", opacity=0.9))
        dwg.add(dwg.text(label, insert=(mx, y0 - 7), text_anchor="middle", font_family=FONT,
                          font_size="6.5px", fill=C_PROC, font_weight="bold"))


def _arrow_v(dwg, x, y0, y1, color=fs.INK, label: str = ""):
    dwg.add(dwg.line(start=(x, y0), end=(x, y1 - 8), stroke=color, stroke_width=1.4))
    dwg.add(dwg.polygon(points=[(x, y1), (x - 4, y1 - 9), (x + 4, y1 - 9)], fill=color))
    if label:
        dwg.add(dwg.text(label, insert=(x + 8, (y0 + y1) / 2), font_family=FONT,
                          font_size="6.5px", fill=C_LIC, font_weight="bold"))


def _stage_box(dwg, x, y, w, h, title, lines, color=C_HEADER, icon_fn=None):
    g = dwg.g()
    g.add(dwg.rect(insert=(x + 2, y + 2), size=(w, h), rx=6, fill=SHADOW, opacity=0.5))
    g.add(dwg.rect(insert=(x, y), size=(w, h), rx=6, fill="white", stroke=color, stroke_width=1.3))
    g.add(dwg.rect(insert=(x, y), size=(w, 18), rx=6, fill=color))
    g.add(dwg.rect(insert=(x, y + 12), size=(w, 6), fill=color))
    g.add(dwg.text(title, insert=(x + w / 2, y + 13), text_anchor="middle",
                    font_family=FONT, font_size="8px", font_weight="bold", fill="white"))
    ty = y + 32
    if icon_fn:
        icon_fn(dwg, x + w / 2 - 14, y + 22)
        ty = y + 62
    for i, line in enumerate(lines):
        g.add(dwg.text(line, insert=(x + w / 2, ty + i * 11), text_anchor="middle",
                        font_family=FONT, font_size="7px", fill=fs.NOTE))
    dwg.add(g)


def _cleaning_table(dwg, x, y):
    """NMRexp-style 2×3 cleaning rules inset."""
    g = dwg.g()
    w, h = 200, 72
    g.add(dwg.rect(insert=(x, y), size=(w, h), rx=3, fill="white",
                    stroke=C_HEADER, stroke_width=1.0))
    g.add(dwg.rect(insert=(x, y), size=(w, 16), fill=C_HEADER))
    g.add(dwg.text("Cleaning rules", insert=(x + w / 2, y + 11), text_anchor="middle",
                    font_family=FONT, font_size="7px", font_weight="bold", fill="white"))
    rules = [
        ("Band count", "≥ 3 peaks in 350–4000 cm⁻¹"),
        ("Duplicate bands", "Reject identical integers"),
        ("Structure physics", "¹³C peaks ≤ C count; ¹H integral ≤ H+2"),
    ]
    cw = w / 3
    for i, (hdr, body) in enumerate(rules):
        cx = x + i * cw
        g.add(dwg.rect(insert=(cx + 1, y + 18), size=(cw - 2, 14), fill=C_GREY))
        g.add(dwg.text(hdr, insert=(cx + cw / 2, y + 28), text_anchor="middle",
                        font_family=FONT, font_size="6px", font_weight="bold", fill=fs.INK))
        g.add(dwg.text(body, insert=(cx + cw / 2, y + 48), text_anchor="middle",
                        font_family=FONT, font_size="5.5px", fill=fs.NOTE))
    g.add(dwg.text("+ 7 more rules", insert=(x + w / 2, y + h - 6), text_anchor="middle",
                    font_family=FONT, font_size="6px", fill=C_PMC, font_style="italic"))
    dwg.add(g)


def _qc_row(dwg, y, structure_lines, text_lines, highlight, reason, rejected=True):
    """Panel B rejection example row."""
    g = dwg.g()
    # Structure placeholder (skeletal hexagon)
    sx = 50
    g.add(dwg.circle(center=(sx, y + 28), r=14, fill="none", stroke=fs.INK, stroke_width=1.2))
    g.add(dwg.line(start=(sx - 10, y + 20), end=(sx + 10, y + 36), stroke=fs.INK, stroke_width=1))
    g.add(dwg.line(start=(sx - 8, y + 38), end=(sx + 8, y + 18), stroke=fs.INK, stroke_width=1))

    # Text block
    tx, tw, th = 100, 520, 56
    g.add(dwg.rect(insert=(tx, y), size=(tw, th), rx=3, fill="#FAFBFC", stroke=fs.GHOST))
    for i, line in enumerate(text_lines):
        g.add(dwg.text(line, insert=(tx + 8, y + 14 + i * 12), font_family="monospace",
                        font_size="6.5px", fill=fs.INK))
    # Red highlight box
    g.add(dwg.rect(insert=(tx + highlight[0], y + highlight[1]),
                    size=(highlight[2], highlight[3]),
                    fill="none", stroke=C_FAIL, stroke_width=1.5))
    g.add(dwg.text(reason, insert=(tx + 8, y + th + 10), font_family=FONT,
                    font_size="7px", fill=C_FAIL, font_weight="bold"))
    if rejected:
        g.add(dwg.text("✕", insert=(W - 55, y + 30), font_family=FONT, font_size="36px",
                        fill=C_FAIL, font_weight="bold"))
    dwg.add(g)


def build_svg(out_path: Path) -> Path:
    dwg = svgwrite.Drawing(str(out_path), size=(f"{W}px", f"{H}px"),
                            viewBox=f"0 0 {W} {H}")
    dwg.add(dwg.rect(insert=(0, 0), size=(W, H), fill=BG))

    # ---- Panel A label & title ------------------------------------------------
    _panel_label(dwg, "A", 18, 28)
    dwg.add(dwg.text("Workflow of data extraction and quality control",
                      insert=(W / 2, 24), text_anchor="middle", font_family=FONT,
                      font_size="11px", font_weight="bold", fill=fs.INK))

    # Dashed workflow boundary
    dwg.add(dwg.rect(insert=(12, 36), size=(W - 24, 340), rx=8,
                      fill="none", stroke=fs.GHOST, stroke_width=1.0,
                      stroke_dasharray="6,4"))

    # Row 1 stages
    y1 = 55
    stages = [
        (30, "PMC OA text", ["188,016 PMCIDs scanned", "S3 plain-text .txt"], C_PMC, _pdf_icon),
        (175, "IR extract", ["Regex band lists", "+ co-reported NMR"], C_PROC, None),
        (320, "Structure resolve", ["OPSIN → RDKit", "SMILES / InChIKey"], C_PROC, None),
        (465, "Licence join", ["Europe PMC stamp", "+ Crossref recovery"], C_LIC, None),
        (610, "Release pools", ["HF + Zenodo", "JSONL per pool"], C_HEADER, None),
    ]
    sw, sh = 128, 88
    for i, (x, title, lines, col, icon) in enumerate(stages):
        _stage_box(dwg, x, y1, sw, sh, title, lines, col, icon)
        if i < len(stages) - 1:
            _arrow_h(dwg, x + sw + 2, y1 + sh / 2, stages[i + 1][0] - 2, y1 + sh / 2,
                     color=col, label=["", "Regex\nextract", "OPSIN", "Licence\njoin"][i] if i < 4 else "")

    # Chemotion branch
    _stage_box(dwg, 30, y1 + 105, 128, 70, "Chemotion ELN",
               ["1,888 CC-BY-SA rows", "same extractor"], C_OK, None)
    _arrow_h(dwg, 158, y1 + 140, 175, y1 + sh / 2 + 20, color=C_OK, label="merge")

    # Mol-IR pair callout
    dwg.add(dwg.rect(insert=(300, y1 + 108), size=(140, 36), rx=4, fill="#EEF3F8",
                      stroke=C_PMC, stroke_width=1.0, stroke_dasharray="4,3"))
    dwg.add(dwg.text("121,233 IR band lists", insert=(370, y1 + 128), text_anchor="middle",
                      font_family=FONT, font_size="8px", font_weight="bold", fill=C_HEADER))

    # Cleaning arrow down
    _arrow_v(dwg, 460, y1 + sh + 8, y1 + sh + 55, color=C_LIC, label="Cleaning")
    _cleaning_table(dwg, 360, y1 + sh + 60)

    # Final database box
    fx, fy, fw, fh = 620, y1 + sh + 45, 250, 130
    dwg.add(dwg.rect(insert=(fx + 2, fy + 2), size=(fw, fh), rx=8, fill=SHADOW, opacity=0.4))
    dwg.add(dwg.rect(insert=(fx, fy), size=(fw, fh), rx=8, fill="#EEF3F8", stroke=C_HEADER, stroke_width=1.5))
    dwg.add(dwg.rect(insert=(fx, fy), size=(fw, 22), rx=8, fill=C_HEADER))
    dwg.add(dwg.text("Final database", insert=(fx + fw / 2, fy + 15), text_anchor="middle",
                      font_family=FONT, font_size="9px", font_weight="bold", fill="white"))
    dwg.add(dwg.text("121,233 band lists  /  43,060 structure-linked",
                      insert=(fx + fw / 2, fy + 38), text_anchor="middle",
                      font_family=FONT, font_size="8px", font_weight="bold", fill=C_HEADER))
    _db_icon(dwg, fx + 45, fy + 70, C_PMC, "IRexp")
    # JSON snippet
    dwg.add(dwg.rect(insert=(fx + 95, fy + 48), size=(140, 72), rx=3, fill="white",
                      stroke=fs.GHOST))
    snippet = [
        '{"ir_bands_cm-1": [2923,',
        '  2854, 1735, 1450],',
        ' "source_doi": "PMC:...",',
        ' "license_pool": "commercial"}',
    ]
    for i, line in enumerate(snippet):
        dwg.add(dwg.text(line, insert=(fx + 100, fy + 60 + i * 11), font_family="monospace",
                          font_size="6px", fill=fs.NOTE))
    dwg.add(dwg.text("Well-structured: ready for ML training",
                      insert=(fx + fw / 2, fy + fh - 8), text_anchor="middle",
                      font_family=FONT, font_size="6.5px", fill=C_OK, font_style="italic"))

    _arrow_h(dwg, 738, y1 + sh / 2, fx - 4, fy + 30, color=C_HEADER)

    # ---- Panel B: QC examples -------------------------------------------------
    _panel_label(dwg, "B", 18, 400)
    dwg.add(dwg.text("Examples of cleaning (QC rejections)",
                      insert=(W / 2, 396), text_anchor="middle", font_family=FONT,
                      font_size="10px", font_weight="bold", fill=fs.INK))
    dwg.add(dwg.rect(insert=(12, 408), size=(W - 24, 255), rx=8,
                      fill="none", stroke=fs.GHOST, stroke_width=1.0,
                      stroke_dasharray="6,4"))

    _qc_row(dwg, 420,
            [],  # structure drawn inline
            ["IR (KBr): 3421, 2923, 2854, 1735, 1450, 1375 cm⁻¹",
             "¹H NMR (400 MHz, CDCl₃): δ 7.25 (2H, d), 6.80 (2H, d)"],
            (55, 2, 200, 12),
            "Band count too low (<3 peaks after gate), filtered")

    _qc_row(dwg, 490,
            [],
            ["IR (neat): 3200, 2950, 1680, 4100, 1520 cm⁻¹",
             "¹³C NMR: δ 171.2, 133.5, 128.1, 115.4"],
            (95, 2, 45, 12),
            "IR band outside 350–4000 cm⁻¹, filtered")

    _qc_row(dwg, 560,
            [],
            ["IR (film): 3050, 2920, 1650, 1450 cm⁻¹",
             "¹H NMR: δ 8.10 (5H), 7.45 (5H), 6.20 (10H)  —  integral sum = 20H",
             "Formula C₆H₅NO₂ (7 H)"],
            (55, 26, 280, 12),
            "¹H integration > formula H+2, quarantined")

    dwg.save()
    return out_path


def main() -> None:
    out_dir = ROOT / "docs/scientific_data/figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    svg = out_dir / "fig_irexp_pipeline.svg"
    build_svg(svg)
    print(f"wrote {svg}")


if __name__ == "__main__":
    main()
