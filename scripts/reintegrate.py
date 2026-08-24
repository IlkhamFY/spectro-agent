#!/usr/bin/env python3
"""Splice the compressed slices back into docs/PAPER.md.

The manuscript was cut by eight editors working in parallel on eight contiguous slices.
Reassembly is by exact substring, not by heading search: each slice was taken verbatim
out of PAPER.md, so if a slice is no longer found in the file the manuscript has moved
underneath the edit and the splice must not be attempted -- a heading-based splice would
happily paste a stale slice over a newer one and lose the difference silently.

Detail that belongs in Methods rather than in Results is not deleted by the editors; it
is listed at the end of a slice under a `<!-- MOVED-TO-METHODS -->` comment. This script
strips those comments, prints them, and leaves relocating the content to a human -- an
automatic append would put hyperparameters in whatever order the slices happened to
finish in.

  python scripts/reintegrate.py --check      # report only
  python scripts/reintegrate.py --write      # apply
"""
import re
import sys
from pathlib import Path

PAPER = Path("docs/PAPER.md")
SLICES = Path("/tmp/sec")
MOVED = re.compile(r"<!--\s*MOVED-TO-METHODS\s*-->(.*?)(?:-->|\Z)", re.S)


def main() -> int:
    write = "--write" in sys.argv
    paper = PAPER.read_text()
    original = paper
    moved, missing, applied = [], [], []

    for src in sorted(SLICES.glob("g?_*.md")):
        if src.name.endswith(".out.md"):
            continue
        out = src.with_suffix(".out.md")
        if not out.exists():
            missing.append(f"{src.stem}: no .out.md")
            continue
        before, after = src.read_text(), out.read_text()
        if before not in paper:
            missing.append(f"{src.stem}: slice no longer present in PAPER.md "
                           "(it changed after the slice was taken) -- NOT spliced")
            continue
        note = MOVED.search(after)
        if note:
            moved.append((src.stem, note.group(1).strip()))
            after = after[:note.start()].rstrip() + "\n\n"
        # A slice that does not end on a blank line can butt a horizontal rule up
        # against the next heading. Pandoc then reads `---` followed by a `#` line as a
        # YAML metadata block -- `#` is a YAML comment -- and dies fourteen lines later
        # on the first colon it meets. Keep the separator paragraph-separated.
        if not after.endswith("\n\n"):
            after = after.rstrip("\n") + "\n\n"
        paper = paper.replace(before, after, 1)
        applied.append((src.stem, len(before.split()), len(after.split())))

    for stem, b, a in applied:
        print(f"  {stem:12s} {b:5d} -> {a:5d} words")
    for m in missing:
        print(f"  SKIP {m}")

    bw, aw = len(original.split()), len(paper.split())
    print(f"\nmanuscript {bw} -> {aw} words "
          f"({len(applied)}/8 slices, {100 * (bw - aw) // max(bw, 1)}% cut)")

    if moved:
        print("\nrelocate into Methods by hand:")
        for stem, body in moved:
            print(f"\n--- from {stem} ---\n{body}")

    if write:
        PAPER.write_text(paper)
        print(f"\nwrote {PAPER}")
    else:
        print("\n(dry run; pass --write to apply)")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
