#!/usr/bin/env python3
"""IRexp pipeline schematic — programmatic SVG (BioRender-class layout).

Generates fig_irexp_pipeline.svg; export via scidata_export.save_svg_bundle().
"""
from __future__ import annotations

import sys
from pathlib import Path

import svgwrite

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

# Canvas: 183 mm ≈ 690 px at 96 dpi; use 690×260 viewBox units
W, H = 690, 260
MARGIN = 16

STAGES = [
    ("1", "Discover", "NCBI esearch\n+ OA filter", fs.MUTED),
    ("2", "Fetch", "PMC-OA S3\nplain text", fs.SKY),
    ("3", "Extract", "Regex band lists\n+ NMR strings", fs.BLUE),
    ("4", "Resolve", "OPSIN / RDKit\n→ SMILES", fs.MUTED),
    ("5", "Licence", "Europe PMC join\n+ Crossref recovery", fs.SKY),
    ("6", "Release", "JSONL pools\n+ HF / Zenodo", fs.BLUE),
]

CHEMO = ("C", "Chemotion\nRADAR4Chem", "ELN band lists\n+ structures", fs.GREEN)


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;")


def build_svg(out_path: Path) -> Path:
    dwg = svgwrite.Drawing(
        str(out_path),
        size=(f"{W}px", f"{H}px"),
        viewBox=f"0 0 {W} {H}",
    )
    dwg.add(dwg.defs)

    # Subtle background
    dwg.add(dwg.rect(insert=(0, 0), size=(W, H), fill="#FAFBFC", rx=4))

    font = "Liberation Sans, Helvetica, Arial, sans-serif"

    def text_block(parent, x, y, lines, size=9, weight="normal", fill=fs.INK, anchor="middle"):
        lh = size * 1.28
        for i, line in enumerate(lines.split("\n")):
            parent.add(dwg.text(
                line,
                insert=(x, y + i * lh),
                text_anchor=anchor,
                font_family=font,
                font_size=f"{size}px",
                font_weight=weight,
                fill=fill,
            ))

    def stage_box(x, y, num, title, sub, accent, w=88, h=72):
        g = dwg.g()
        # Shadow
        g.add(dwg.rect(
            insert=(x + 2, y + 2), size=(w, h), rx=8, ry=8,
            fill="#E8EAEC",
            opacity=0.5,
        ))
        # Body
        g.add(dwg.rect(
            insert=(x, y), size=(w, h), rx=8, ry=8,
            fill="white", stroke=accent, stroke_width=1.6,
        ))
        # Accent bar top
        g.add(dwg.rect(
            insert=(x, y), size=(w, 5), rx=8, ry=8,
            fill=accent,
        ))
        g.add(dwg.rect(insert=(x, y + 3), size=(w, 3), fill=accent))
        # Number badge
        bx, by = x + 14, y + 16
        g.add(dwg.circle(center=(bx, by), r=10, fill=fs.INK))
        g.add(dwg.text(
            num, insert=(bx, by + 4),
            text_anchor="middle", font_family=font,
            font_size="10px", font_weight="bold", fill="white",
        ))
        text_block(g, x + w / 2, y + 30, title, size=10, weight="bold")
        text_block(g, x + w / 2, y + 46, sub, size=8, fill=fs.NOTE)
        dwg.add(g)
        return x + w / 2, y + h / 2

    # Title
    dwg.add(dwg.text(
        "IRexp construction pipeline (released corpus)",
        insert=(W / 2, 22),
        text_anchor="middle",
        font_family=font,
        font_size="11px",
        font_weight="bold",
        fill=fs.INK,
    ))

    # Main row
    n = len(STAGES)
    gap = (W - 2 * MARGIN - n * 88) / (n - 1)
    y_main = 58
    centres = []
    for i, (num, title, sub, col) in enumerate(STAGES):
        x = MARGIN + i * (88 + gap)
        cx, cy = stage_box(x, y_main, num, title, sub, col)
        centres.append((cx, cy, x, y_main))

    # Arrows between stages
    for i in range(len(centres) - 1):
        x0 = centres[i][2] + 88 + 4
        x1 = centres[i + 1][2] - 4
        y = centres[i][1]
        dwg.add(dwg.line(
            start=(x0, y), end=(x1 - 8, y),
            stroke=fs.INK, stroke_width=1.2,
        ))
        dwg.add(dwg.polygon(
            points=[(x1, y), (x1 - 9, y - 4), (x1 - 9, y + 4)],
            fill=fs.INK,
        ))

    # Chemotion branch
    cx = centres[2][0]
    chem_x = cx - 44
    chem_y = 168
    stage_box(chem_x, chem_y, CHEMO[0], CHEMO[1], CHEMO[2], CHEMO[3], w=96, h=68)
    # Merge arrow
    dwg.add(dwg.line(
        start=(cx, chem_y), end=(cx, y_main + 72 + 4),
        stroke=fs.GREEN, stroke_width=1.3,
    ))
    dwg.add(dwg.polygon(
        points=[(cx, y_main + 72 + 4), (cx - 4, y_main + 72 - 4), (cx + 4, y_main + 72 - 4)],
        fill=fs.GREEN,
    ))
    # Side label
    dwg.add(dwg.text(
        "same extractor",
        insert=(cx + 58, (chem_y + y_main + 72) / 2),
        text_anchor="middle",
        font_family=font,
        font_size="8px",
        fill=fs.GREEN,
        transform=f"rotate(90 {cx + 58} {(chem_y + y_main + 72) / 2})",
    ))

    # Footer
    dwg.add(dwg.text(
        "Outputs: irexp.jsonl.gz, licence pools, irexp_resolved — numeric fields only (no PDFs / figures)",
        insert=(W / 2, H - 14),
        text_anchor="middle",
        font_family=font,
        font_size="8px",
        fill=fs.NOTE,
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
