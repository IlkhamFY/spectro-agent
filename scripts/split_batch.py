#!/usr/bin/env python3
"""Split an exported solver batch into halves.

A six-compound batch can push one solver turn past the 64k output-token ceiling, and the
agent dies with nothing to deposit. Halving the batch keeps every compound inside the
2-12 compounds-per-context envelope the main round already used, so the halves are
solved under the same protocol, only in a smaller context.

    python scripts/split_batch.py /tmp/blind/benchmark_expand/batch_04.txt
    -> batch_04a.txt, batch_04b.txt beside it (the original is left in place)
"""
import os, re, sys

def split(path):
    text = open(path).read()
    # compounds start at a qid header line: "R19 | formula ..."
    blocks = re.split(r"\n(?=R\d+ \| )", text.strip("\n"))
    blocks = [b.strip("\n") for b in blocks if b.strip()]
    half = (len(blocks) + 1) // 2
    stem, ext = os.path.splitext(path)
    out = []
    for tag, part in (("a", blocks[:half]), ("b", blocks[half:])):
        if not part:
            continue
        p = f"{stem}{tag}{ext}"
        open(p, "w").write("\n\n".join(part) + "\n")
        out.append((p, [b.split(" | ")[0] for b in part]))
    return out

if __name__ == "__main__":
    for path in sys.argv[1:]:
        for p, qids in split(path):
            print(f"{p}: {', '.join(qids)}")
