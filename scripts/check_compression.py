#!/usr/bin/env python3
"""Gate the compression pass: prose may shrink, evidence may not move.

Eight editors cut eight slices of the manuscript in parallel. Each was told that a
gate verifies their work; this is that gate. It compares a slice before and after and
enforces the one asymmetry that makes parallel editing safe at all — **deleting a whole
sentence is allowed, mutating what a sentence asserts is not**.

Concretely, after the cut:

  numbers        every numeral that survives must have been in the source. A numeral in
                 the output that is not in the input is a fabricated statistic, which is
                 the single worst failure mode of an LLM asked to shorten a results
                 section. Dropped numerals are fine; invented ones are fatal.
  citations      [@key] must survive one-for-one. A dropped citation is an unsupported
                 claim or a lost attribution, so this one is symmetric: no drops, no
                 inventions.
  cross-refs     [@sec:|tab:|fig:|sfig:] may be dropped with their sentence but never
                 invented. A table or figure that ends up with no reference at all is
                 reported separately, because it breaks reading order downstream.
  headings       exact equality, labels included. The reintegration step splices slices
                 back by heading, so a renamed heading silently loses a section.
  tables         every table row byte-identical. Captions are prose and may be trimmed.
  hedges         a shrinking count of epistemic qualifiers is reported, not failed — it
                 is a judgement call whether a hedge died with a redundant sentence or
                 was quietly deleted to save words, and a human should look.

  python scripts/check_compression.py before.md after.md
  python scripts/check_compression.py --pairs /tmp/sec        # *.md vs *.out.md
"""
import re
import sys
from collections import Counter
from pathlib import Path

XREF_NS = ("sec:", "fig:", "tab:", "sfig:")

# 3.30 and 3,300 and 12th all count. The inner group has to end on a digit or a
# trailing sentence comma rides along and reads as a different number.
# A bare "-" before a digit is a range dash as often as a minus, so sign is not captured.
NUM = re.compile(r"\d(?:[\d,]*\d)?(?:\.\d+)?")
CITE_GROUP = re.compile(r"\[([^\]]*@[^\]]*)\]")
KEY = re.compile(r"@([A-Za-z][\w:.-]*)")
HEADING = re.compile(r"^#{1,6}\s+.*$", re.M)
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.M)

# Relocated-to-Methods notes are scaffolding, not manuscript: they restate numbers that
# are still in the prose, so counting them would read a legitimate cut as a fabrication.
# reintegrate.py strips the same block, so both tools see the same text.
MOVED = re.compile(r"<!--\s*MOVED-TO-METHODS\s*-->.*\Z", re.S)

HEDGES = (
    "consistent with", "cannot exclude", "we do not claim", "may reflect",
    "on this sample", "lower bound", "upper bound", "not powered", "suggests",
    "appears", "likely", "we cannot", "does not establish", "is not evidence",
    "provisional", "preliminary", "caution", "confounded", "may be",
)


def _keys(md: str):
    """Bib keys and cross-reference labels, kept apart — they fail differently."""
    bib, xref = Counter(), Counter()
    for group in CITE_GROUP.findall(md):
        for k in KEY.findall(group):
            k = k.rstrip(".,;")
            (xref if k.startswith(XREF_NS) else bib)[k] += 1
    return bib, xref


def _hedges(md: str) -> int:
    low = md.lower()
    return sum(low.count(h) for h in HEDGES)


def compare(before: str, after: str, label: str) -> list[str]:
    errs, warns = [], []
    after = MOVED.sub("", after)

    # --- numbers: one-directional. Losing a sentence is a cut; gaining a digit is a lie.
    b_num, a_num = Counter(NUM.findall(before)), Counter(NUM.findall(after))
    invented = a_num - b_num
    if invented:
        errs.append("invented numbers (not present in the source): "
                    + ", ".join(f"{n}x{c}" if c > 1 else n
                                for n, c in sorted(invented.items())))

    # --- citations: symmetric. Both directions are a defect.
    b_bib, a_bib = _keys(before)[0], _keys(after)[0]
    for key in sorted(set(b_bib) - set(a_bib)):
        errs.append(f"dropped citation [@{key}] — re-attach it to a surviving claim")
    for key in sorted(set(a_bib) - set(b_bib)):
        errs.append(f"invented citation [@{key}]")

    # --- cross-references: drops are allowed with their sentence, inventions are not.
    b_x, a_x = _keys(before)[1], _keys(after)[1]
    for key in sorted(set(a_x) - set(b_x)):
        errs.append(f"invented cross-reference [@{key}]")
    for key in sorted(set(b_x) - set(a_x)):
        # a table or figure defined in this slice that nothing points at any more
        kind = key.split(":")[0]
        (errs if kind in ("tab", "fig") else warns).append(
            f"cross-reference [@{key}] no longer appears"
            + (" — the float it points at is now unreferenced"
               if kind in ("tab", "fig") else ""))

    # --- headings: exact, because reintegration splices on them
    b_h, a_h = HEADING.findall(before), HEADING.findall(after)
    if b_h != a_h:
        for h in b_h:
            if h not in a_h:
                errs.append(f"heading lost or altered: {h.strip()}")
        for h in a_h:
            if h not in b_h:
                errs.append(f"heading added or altered: {h.strip()}")
        if sorted(b_h) == sorted(a_h):
            errs.append("headings reordered")

    # --- tables: rows are data
    b_t = Counter(r.strip() for r in TABLE_ROW.findall(before))
    a_t = Counter(r.strip() for r in TABLE_ROW.findall(after))
    if b_t != a_t:
        for row in sorted(b_t - a_t):
            errs.append(f"table row changed or dropped: {row[:90]}")
        for row in sorted(a_t - b_t):
            errs.append(f"table row added or reworded: {row[:90]}")

    # --- typed numbers the cross-reference machinery is supposed to own
    typed = re.findall(r"(?<![A-Za-z])(?:Fig\.|Figure|Table)\s+S?\d|§\s?\d", after)
    if typed:
        errs.append(f"typed float numbers reintroduced: {sorted(set(typed))}")

    # --- hedges: advisory. A hedge may legitimately die with its sentence.
    b_hg, a_hg = _hedges(before), _hedges(after)
    if a_hg < b_hg * 0.6:
        warns.append(f"epistemic qualifiers fell {b_hg} -> {a_hg} "
                     "(>40% of the hedging is gone — read the diff before accepting)")

    bw, aw = len(before.split()), len(after.split())
    head = f"{label}: {bw} -> {aw} words ({100 * (bw - aw) // max(bw, 1)}% cut)"
    print(("FAIL " if errs else "ok   ") + head)
    for w in warns:
        print(f"       warn: {w}")
    for e in errs:
        print(f"       ERR:  {e}")
    return errs


def main() -> int:
    args = sys.argv[1:]
    pairs = []
    if args[:1] == ["--pairs"]:
        root = Path(args[1])
        for src in sorted(root.glob("*.md")):
            if src.name.endswith(".out.md"):
                continue
            out = src.with_suffix(".out.md")
            if out.exists():
                pairs.append((src, out))
            else:
                print(f"---  {src.name}: no .out.md yet")
    elif len(args) == 2:
        pairs = [(Path(args[0]), Path(args[1]))]
    else:
        print(__doc__)
        return 2

    if not pairs:
        print("nothing to compare")
        return 1

    bad = 0
    for src, out in pairs:
        bad += len(compare(src.read_text(), out.read_text(), src.stem))
    print()
    print(f"{len(pairs)} slice(s) compared, {bad} error(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
