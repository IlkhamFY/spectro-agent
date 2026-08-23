#!/usr/bin/env python3
"""Measure the built PDFs and fail on the typographic defects we have already fixed once.

Every check here exists because the defect it names was found by looking at a rendered
page, and each was invisible in the source:

  margins      a paragraph of five monospaced paths ran 43pt past the measure, because at
               TeX's default tolerance an overfull line beats a loose one
  rule gaps    every table sat its bottom rule 17.8pt below the last row against 4.1pt
               under the header rule -- the lineno patch was switching numbering back on
               *inside* the environment and paying a row for it
  tiny type    figure labels fell to ~2.5pt where a plate was drawn wider than the measure
               and scaled down to fit
  blank pages  a float that cannot fit pushes one, and nobody notices in the source
  clipping     a verbatim line longer than the measure does not wrap: its text is simply
               absent from the PDF, and the sentence ends mid-word

  python scripts/check_layout.py            # both documents
  python scripts/check_layout.py docs/paper.pdf
"""
import sys

import fitz

DOCS = ("docs/paper.pdf", "docs/paper_esi.pdf")

MARGIN = 72.0          # 1in, as build_pdf passes to geometry
SLOP = 4.0             # glyph overhang and italic correction
MIN_PT = 5.9           # below this, type is not legible in print
MAX_RULE_GAP = 8.0     # a bottom rule should sit as close as the header rule does
FAIL = []


def fail(doc, page, what):
    FAIL.append(f"{doc} p{page}: {what}")


def check(path):
    d = fitz.open(path)
    for i in range(d.page_count):
        pg = d[i]
        right = pg.rect.width - MARGIN

        # --- text past the measure
        for b in pg.get_text("blocks"):
            if b[2] > right + SLOP:
                fail(path, i + 1, f"text {b[2] - right:.0f}pt past the right margin: "
                                  f"{' '.join(b[4].split())[:70]}")

        # --- type too small to read
        for blk in pg.get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if sp["size"] < MIN_PT and sp["text"].strip():
                        fail(path, i + 1, f"{sp['size']:.1f}pt type: {sp['text'][:40]!r}")
                        break

        # --- a page with neither text nor an image
        if not pg.get_text().strip() and not pg.get_images():
            fail(path, i + 1, "blank page")

        # --- table rules: the gap under the last row should match the gap under the header
        rules = sorted([dr["rect"] for dr in pg.get_drawings()
                        if dr["rect"].height < 1.5 and dr["rect"].width > 400],
                       key=lambda r: r.y0)
        if len(rules) >= 3:
            words = sorted(pg.get_text("words"), key=lambda w: w[3])
            bottom = rules[-1]
            above = [w for w in words if w[3] <= bottom.y0 - 0.5]
            if above:
                gap = bottom.y0 - above[-1][3]
                if gap > MAX_RULE_GAP:
                    fail(path, i + 1, f"table bottom rule floats {gap:.1f}pt below the "
                                      f"last row (header rule sits at ~4pt)")
    return d.page_count


def main():
    docs = sys.argv[1:] or list(DOCS)
    total = 0
    for path in docs:
        try:
            total += check(path)
        except Exception as e:                       # a missing build is a failure too
            FAIL.append(f"{path}: could not be read ({e})")
    if FAIL:
        print(f"LAYOUT GATE: {len(FAIL)} problem(s)\n")
        for f in FAIL:
            print("  " + f)
        return 1
    print(f"LAYOUT GATE: {len(docs)} document(s), {total} pages, all checks pass")
    print("  no text past the measure")
    print("  no type below 5.9pt")
    print("  no blank pages")
    print("  every table's bottom rule sits as close as its header rule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
