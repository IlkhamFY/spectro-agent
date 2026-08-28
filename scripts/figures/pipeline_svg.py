#!/usr/bin/env python3
"""IRexp pipeline schematic — NMRexp Fig. 2A style hero SVG.

PMC + Chemotion branches → extract → resolve → licence pools → release.
Hand-crafted vector SVG with Bézier connectors and flat-modern card design.
"""
from __future__ import annotations

import sys
from pathlib import Path

import svgwrite

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

# Canvas: 183 mm full width @ 96 dpi ≈ 690 px
W, H = 700, 320
FONT = "Liberation Sans, Helvetica, Arial, sans-serif"
SHADOW = "#D8DCE0"
BG = "#FAFBFC"

# Colour tokens
C_PMC = fs.BLUE
C_CHEMO = fs.GREEN
C_PROC = fs.SKY
C_LIC = fs.ORANGE
C_OUT = fs.MUTED


def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;")


def _shadow(dwg, x, y, w, h, rx=10):
    dwg.add(dwg.rect(insert=(x + 2, y + 2), size=(w, h), rx=rx, ry=rx,
                     fill=SHADOW, opacity=0.45))


def _card(dwg, x, y, w, h, accent, title, lines, num=None, rx=10):
    g = dwg.g()
    _shadow(dwg, x, y, w, h, rx)
    g.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx,
                    fill="white", stroke=accent, stroke_width=1.4))
    g.add(dwg.rect(insert=(x, y), size=(w, 5), rx=rx, ry=rx, fill=accent))
    g.add(dwg.rect(insert=(x, y + 3), size=(w, 3), fill=accent))
    if num:
        bx, by = x + 16, y + 18
        g.add(dwg.circle(center=(bx, by), r=10, fill=fs.INK))
        g.add(dwg.text(str(num), insert=(bx, by + 4), text_anchor="middle",
                        font_family=FONT, font_size="9px", font_weight="bold", fill="white"))
        ty = y + 34
    else:
        ty = y + 22
    g.add(dwg.text(title, insert=(x + w / 2, ty), text_anchor="middle",
                    font_family=FONT, font_size="9.5px", font_weight="bold", fill=fs.INK))
    lh = 11.5
    for i, line in enumerate(lines):
        g.add(dwg.text(line, insert=(x + w / 2, ty + 14 + i * lh), text_anchor="middle",
                        font_family=FONT, font_size="7.5px", fill=fs.NOTE))
    dwg.add(g)


def _arrow(dwg, x0, y0, x1, y1, color=fs.INK, width=1.3):
    dwg.add(dwg.line(start=(x0, y0), end=(x1 - 7, y1), stroke=color, stroke_width=width))
    dwg.add(dwg.polygon(
        points=[(x1, y1), (x1 - 8, y1 - 3.5), (x1 - 8, y1 + 3.5)],
        fill=color,
    ))


def _bezier_arrow(dwg, pts, color=fs.INK, width=1.2):
    """pts = [(x0,y0), (x1,y1), (x2,y2), (x3,y3)] cubic bezier."""
    x0, y0 = pts[0]
    x1, y1 = pts[1]
    x2, y2 = pts[2]
    x3, y3 = pts[3]
    path = dwg.path(d=f"M {x0},{y0} C {x1},{y1} {x2},{y2} {x3},{y3}",
                    fill="none", stroke=color, stroke_width=width)
    dwg.add(path)
    # arrowhead at end
    dwg.add(dwg.polygon(
        points=[(x3, y3), (x3 - 8, y3 - 3.5), (x3 - 8, y3 + 3.5)],
        fill=color,
    ))


def _pool_cylinder(dwg, cx, cy, label, sub, color):
    """Database icon."""
    g = dwg.g()
    g.add(dwg.ellipse(center=(cx, cy - 8), r=(28, 7), fill=color, opacity=0.25))
    g.add(dwg.rect(insert=(cx - 28, cy - 8), size=(56, 22), fill=color, opacity=0.18))
    g.add(dwg.ellipse(center=(cx, cy + 14), r=(28, 7), fill=color, opacity=0.35))
    g.add(dwg.ellipse(center=(cx, cy - 8), r=(28, 7), fill="none", stroke=color, stroke_width=1.2))
    g.add(dwg.line(start=(cx - 28, cy - 8), end=(cx - 28, cy + 14), stroke=color, stroke_width=1.2))
    g.add(dwg.line(start=(cx + 28, cy - 8), end=(cx + 28, cy + 14), stroke=color, stroke_width=1.2))
    g.add(dwg.text(label, insert=(cx, cy + 30), text_anchor="middle",
                    font_family=FONT, font_size="7.5px", font_weight="bold", fill=fs.INK))
    g.add(dwg.text(sub, insert=(cx, cy + 42), text_anchor="middle",
                    font_family=FONT, font_size="6.5px", fill=fs.NOTE))
    dwg.add(g)


def build_svg(out_path: Path) -> Path:
    dwg = svgwrite.Drawing(str(out_path), size=(f"{W}px", f"{H}px"),
                            viewBox=f"0 0 {W} {H}")
    dwg.add(dwg.rect(insert=(0, 0), size=(W, H), fill=BG, rx=4))

    # Title
    dwg.add(dwg.text("IRexp construction pipeline", insert=(W / 2, 22),
                      text_anchor="middle", font_family=FONT, font_size="11px",
                      font_weight="bold", fill=fs.INK))

    # ---- Row 1: Sources -------------------------------------------------------
    y_src = 42
    _card(dwg, 30, y_src, 100, 62, C_PMC, "PMC-OA", ["NCBI esearch", "S3 plain text"], num="1")
    _card(dwg, 30, y_src + 78, 100, 62, C_CHEMO, "Chemotion", ["RADAR4Chem ELN", "CC-BY-SA-4.0"], num="C")

    # Merge point
    mx, my = 175, y_src + 70
    dwg.add(dwg.circle(center=(mx, my), r=6, fill=fs.INK))
    _bezier_arrow(dwg, [(130, y_src + 31), (155, y_src + 31), (160, my), (mx - 8, my)], C_PMC)
    _bezier_arrow(dwg, [(130, y_src + 109), (155, y_src + 109), (160, my), (mx - 8, my)], C_CHEMO)
    dwg.add(dwg.text("same extractor", insert=(148, my + 18), text_anchor="middle",
                      font_family=FONT, font_size="7px", fill=C_CHEMO, font_style="italic"))

    # ---- Row 1 continued: Processing stages -----------------------------------
    stages = [
        (2, "Extract", ["Regex band lists", "+ NMR strings"], C_PROC),
        (3, "Resolve", ["OPSIN / RDKit", "→ SMILES"], C_PROC),
        (4, "Licence", ["Europe PMC join", "+ Crossref recovery"], C_LIC),
    ]
    x = 195
    sw, sh = 96, 68
    gap = 18
    centres = []
    for num, title, lines, col in stages:
        _card(dwg, x, y_src + 36, sw, sh, col, title, lines, num=num)
        centres.append((x + sw / 2, y_src + 36 + sh / 2, x))
        x += sw + gap

    # Arrows between stages
    _arrow(dwg, mx + 8, my, 193, y_src + 70)
    for i in range(len(centres) - 1):
        x0 = centres[i][2] + sw + 2
        x1 = centres[i + 1][2] - 2
        y = centres[i][1]
        _arrow(dwg, x0, y, x1, y)

    # ---- Row 2: Licence pools -------------------------------------------------
    y_pool = 200
    dwg.add(dwg.text("Licence pools", insert=(W / 2, y_pool - 8),
                      text_anchor="middle", font_family=FONT, font_size="8px",
                      font_weight="bold", fill=fs.NOTE))

    pools = [
        ("commercial", "CC-BY/CC0", C_PMC),
        ("non-commercial", "NC*", C_LIC),
        ("ShareAlike", "CC-BY-SA", C_CHEMO),
        ("empty/unknown", "excluded", C_OUT),
    ]
    px = 80
    pgap = 130
    for name, sub, col in pools:
        _pool_cylinder(dwg, px, y_pool + 30, name, sub, col)
        px += pgap

    # Arrow from licence stage to pools
    lic_cx = centres[-1][0]
    _arrow(dwg, lic_cx, y_src + 36 + sh + 2, lic_cx, y_pool - 18, C_LIC)
    dwg.add(dwg.line(start=(80, y_pool - 18), end=(W - 80, y_pool - 18),
                      stroke=C_LIC, stroke_width=1.0))
    for px2 in [80, 210, 340, 470]:
        _arrow(dwg, px2, y_pool - 18, px2, y_pool - 10, C_LIC, width=1.0)

    # ---- Release box ----------------------------------------------------------
    _card(dwg, W - 130, y_src + 36, 110, 68, fs.BLUE, "Release", [
        "JSONL pools",
        "HF / Zenodo",
    ], num="5")
    _arrow(dwg, centres[-1][2] + sw + 2, centres[-1][1],
           W - 132, y_src + 70)

    # Footer
    dwg.add(dwg.text(
        "Outputs: irexp.jsonl.gz, licence pools, irexp_resolved — numeric fields only (no PDFs / figures)",
        insert=(W / 2, H - 12), text_anchor="middle",
        font_family=FONT, font_size="7px", fill=fs.NOTE,
    ))

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
