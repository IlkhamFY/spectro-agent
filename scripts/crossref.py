#!/usr/bin/env python3
"""
Resolve cross-references so figure, table and section numbers are derived, not typed.

The manuscript carried 202 hand-typed numbers -- 19 "Fig. N", 23 "Table N" and 160 "§N".
Every one of them is a claim about where something sits in the document, and nothing
checked it. Insert a figure and each later number is silently wrong; move a section and
160 pointers rot at once. The §5.7 incident was this failure with only five pointers
involved.

Numbers now come from position. The source names things, the build counts them:

    ## Benchmark design {#sec:benchmark}     ->  "3. Benchmark design"
    **Table {#tab:headline}. Caption**       ->  "Table 2. Caption"
    ![caption](fig.png){#fig:models}         ->  Fig. 5
    ... as [@sec:benchmark] sets out ...     ->  "§3"
    ... [@tab:headline] reports ...          ->  "Table 2"
    ... [@fig:models] shows ...              ->  "Fig. 5"

`resolve()` returns the text with every reference replaced by its true number, and
`audit()` returns what it found so a gate can insist that nothing was typed by hand and
that no label is defined twice, referenced-but-undefined, or defined-but-never-referenced.
"""
import re

REF = re.compile(r'\[@(sec|fig|tab|sfig):([A-Za-z0-9_-]+)\]')
DEF_SEC = re.compile(r'^(#{2,4})\s+(.*?)\s*\{#sec:([A-Za-z0-9_-]+)\}\s*$', re.M)
DEF_TAB = re.compile(r'\*\*Table\s*\{#tab:([A-Za-z0-9_-]+)\}\.\s*', re.M)
# a caption may itself carry a reference, so the bracket class has to nest one level
DEF_FIG = re.compile(r'(!\[(?:[^\[\]]|\[[^\[\]]*\])*\]\([^)]*\))\{#fig:([A-Za-z0-9_-]+)\}')

# Prose that types a number the build should be deriving. Deliberately narrow: it must
# look like a reference, not like "Table 2 of ref. 14" or a bare numeral.
TYPED = re.compile(r'(?<![A-Za-z])(?:Fig\.|Figure|Table)\s+(?:S?\d+)|§\s?\d')


def _number_sections(text, prefix=""):
    """Assign 1, 1.1, 2 ... to '##'/'###' headings in document order.

    `prefix` stamps the ESI's own numbering: S1, S1.1, S2."""
    nums, counters = {}, [0, 0, 0]
    out = []
    for line in text.split("\n"):
        m = re.match(r'^(#{2,4})\s+(.*)$', line)
        if not m:
            out.append(line); continue
        depth = len(m.group(1)) - 2                 # ## -> 0, ### -> 1
        title = m.group(2)
        lbl = re.search(r'\{#sec:([A-Za-z0-9_-]+)\}', title)
        # unnumbered front/back matter keeps its heading and takes no number
        if re.match(r'(Abstract|References|Acknowledgements|Conflicts|Author '
                    r'Contributions|Use of AI|Data and code|Licensing|Supporting)',
                    re.sub(r'\s*\{#.*', '', title), re.I):
            out.append(re.sub(r'\s*\{#sec:[^}]*\}', '', line)); continue
        counters[depth] += 1
        for d in range(depth + 1, 3):
            counters[d] = 0
        num = prefix + ".".join(str(c) for c in counters[:depth + 1] if c)
        clean = re.sub(r'\s*\{#sec:[^}]*\}', '', title)
        clean = re.sub(r'^\d+(\.\d+)*\.?\s+', '', clean)      # drop any typed number
        if lbl:
            nums[f"sec:{lbl.group(1)}"] = num
        # "1." at top level, "1.1" below it -- journal house style
        dot = "." if depth == 0 else ""
        out.append(f"{m.group(1)} {num}{dot} {clean}")
    return "\n".join(out), nums


def _number(text, pattern, kind, fmt, prefix=""):
    """Number tables/figures in document order, stripping the label marker."""
    nums, n = {}, 0
    def sub(m):
        nonlocal n
        n += 1
        key = m.group(2) if kind == "fig" else m.group(1)
        nums[f"{kind}:{key}"] = f"{prefix}{n}"
        return fmt(m, n)
    return pattern.sub(sub, text), nums


def si_labels():
    """ESI figures are numbered by build_pdf.SI_FIGS, so read their order from there.

    They live in a second document, so nothing in PAPER.md can count them -- which is
    exactly why they were the last six numbers still typed by hand.
    """
    import os, re as _re
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_pdf.py")
    try:
        body = open(src, encoding="utf-8").read()
    except OSError:
        return {}
    block = _re.search(r'SI_FIGS\s*=\s*\[(.*?)\n\]', body, _re.S)
    if not block:
        return {}
    files = _re.findall(r'\(\s*"([^"]+\.png)"', block.group(1))
    out = {}
    for i, fn in enumerate(files, 1):
        key = _re.sub(r'\.png$|^fig\d*_?', '', fn).strip('_') or fn
        out[f"sfig:{key.replace('_', '-')}"] = f"S{i}"
    return out


def resolve(md, external=None, prefix=""):
    """-> (text with every reference replaced by its number, label map).

    `external` carries labels defined in another document. The ESI is numbered
    independently -- its own sections are S1, S2 -- but it points back into the article,
    so it needs the article's label map to resolve those references. Local definitions
    win, so an ESI section that reuses a label name shadows the article's rather than
    silently taking its number.

    `prefix` numbers this document's own sections and tables S1, S2 ... , which is what
    keeps an ESI table from colliding with Table 1 of the article."""
    md, sec = _number_sections(md, prefix)
    md, tab = _number(md, DEF_TAB, "tab", lambda m, n: f"**Table {prefix}{n}. ", prefix)
    md, fig = _number(md, DEF_FIG, "fig", lambda m, n: m.group(1))
    labels = {**(external or {}), **sec, **tab, **fig, **si_labels()}
    # A non-breaking space between the label and its number. "Fig. 3" split across a line
    # break reads as a sentence ending in "Fig." and a new one starting with a numeral;
    # it happened twice in the built PDF. pandoc turns U+00A0 into a LaTeX tie.
    NB = "\u00a0"
    word = {"sec": "§", "tab": "Table" + NB, "fig": "Fig." + NB, "sfig": "Fig." + NB}
    def sub(m):
        key = f"{m.group(1)}:{m.group(2)}"
        if key not in labels:
            raise KeyError(f"reference to undefined label {key}")
        return f"{word[m.group(1)]}{labels[key]}"
    return REF.sub(sub, md), labels


def audit(md):
    """-> dict of findings for the manuscript gate."""
    used = {f"{a}:{b}" for a, b in REF.findall(md)}
    _, labels = resolve(md)
    stripped = REF.sub("", md)
    return {
        "labels": labels,
        "undefined": sorted(used - set(labels)),
        "unused": sorted(set(labels) - used),
        "typed": sorted(set(TYPED.findall(stripped)) | {
            m.group(0) for m in TYPED.finditer(stripped)}),
    }


if __name__ == "__main__":
    import sys
    src = open(sys.argv[1] if len(sys.argv) > 1 else "docs/PAPER.md", encoding="utf-8").read()
    a = audit(src)
    print(f"labels defined : {len(a['labels'])}")
    print(f"undefined refs : {a['undefined'] or 'none'}")
    print(f"unused labels  : {a['unused'] or 'none'}")
    print(f"hand-typed     : {len(a['typed'])}")
