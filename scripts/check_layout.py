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

MARGIN = {
    "docs/paper.pdf": 40.0,      # ~1.5 cm, ChemRxiv two-column A4
    "docs/paper_esi.pdf": 72.0,  # 1 in, ESI stays single-column letter
}
SLOP = 6.0             # glyph overhang, italic correction, two-column float overhang
MIN_PT = 5.9           # below this, type is not legible in print
MAX_RULE_GAP = 9.5     # a bottom rule should sit as close as the header rule does
MAX_SHORT_PAGE = 150.0 # a prose page should not stop this far above its foot
FAIL = []


def fail(doc, page, what):
    FAIL.append(f"{doc} p{page}: {what}")


def check(path):
    d = fitz.open(path)
    margin = MARGIN.get(path, 72.0)
    for i in range(d.page_count):
        pg = d[i]
        right = pg.rect.width - margin

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

        # --- a page abandoned well before its foot, with no float to explain it.
        # Reserving space for a table longer than the page cannot succeed, and the attempt
        # ended the ESI's first page 330pt short. A figure legitimately leaves a band; a
        # page of nothing but prose should not.
        words = pg.get_text("words")
        if words and i < d.page_count - 1 and not pg.get_images():
            gap = (pg.rect.height - margin) - max(w[3] for w in words)
            if gap > MAX_SHORT_PAGE:
                fail(path, i + 1, f"page ends {gap:.0f}pt above the bottom margin with no "
                                  f"figure to explain it")

        # --- a table split leaving a fragment: rules on the page with almost nothing
        # between them and nothing after. Table 1 once put a single row on the following
        # page with no header and no caption above it.
        rules_all = sorted([dr["rect"] for dr in pg.get_drawings()
                            if dr["rect"].height < 1.5 and dr["rect"].width > 400],
                           key=lambda r: r.y0)
        if rules_all and len(rules_all) <= 2:
            body = [w for w in pg.get_text("words") if w[0] > margin - 6]
            inside = {round(w[3]) for w in body
                      if rules_all[0].y1 < w[1] and w[3] < rules_all[-1].y0}
            after = {round(w[3]) for w in body if w[1] > rules_all[-1].y1}
            if len(inside) <= 1 and len(after) <= 1:
                fail(path, i + 1, "a table fragment: ruled rows with no header, no caption "
                                  "and nothing following them on the page")

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
    print("  no blank pages, and none abandoned above its foot")
    print("  every table's bottom rule sits as close as its header rule")
    print("  no table split leaves a fragment on its own page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
