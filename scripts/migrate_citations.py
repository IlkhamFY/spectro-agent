#!/usr/bin/env python3
"""One-shot migration: hand-numbered superscript citations -> pandoc [@key] syntax.

The manuscript used Unicode superscripts (e.g. "Alberts et al.23") both for citations
AND for chemistry (13C, 1H, cm-1, chi-squared, 1J/2J couplings, powers of ten) and for
author-affiliation markers. This script converts ONLY the citation sites, using explicit
exclusion rules, and merges adjacent citations into one bracket ([@a; @b]).

Run with --dry-run to review, then without to apply. Kept in-tree as the audit trail for
how the reference list became docs/references.bib.
"""
import re, sys

SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
DIGIT = {c: str(i) for i, c in enumerate(SUP)}

# reference number -> BibTeX key(s). Ref 14 bundled two distinct papers in the old
# hand-numbered list; a real bibliography lets them be separate entries.
KEYS = {
    1: ["chacko2024spectro"], 2: ["kamber2026chemist"], 3: ["lowe2011opsin"],
    4: ["landrum_rdkit"], 5: ["krenn2020selfies"], 6: ["pmc_oa"],
    7: ["chemotion2024"], 8: ["nist_webbook"], 9: ["rogers2010ecfp"],
    10: ["wang2023selfconsistency"], 11: ["hu2024multitask"], 12: ["yang2026nmrtrans"],
    13: ["ottomano2025nmiracle"], 14: ["su2025spectrallm", "shen2025molspectllm"],
    15: ["zhuang2025treesearch"], 16: ["smith2010dp4"], 17: ["grimblat2015dp4plus"],
    18: ["pickard2001gipaw"], 19: ["ashbrook2016nmrcryst"], 20: ["guo2024molpuzzle"],
    21: ["praski2025embeddings"], 22: ["sdbs"], 23: ["alberts2024ir"],
    24: ["kuhn2015nmrshiftdb2"], 25: ["bremser1978hose"], 26: ["kim2023pubchem"],
}

AFFILIATION_LINES = {3, 4}   # author affiliation markers, not citations


def is_citation(line, start, end, lineno):
    """True only for genuine citation superscripts."""
    if lineno in AFFILIATION_LINES:
        return False
    before, after = line[:start], line[end:]
    # chemistry: superscript labels an element/nucleus (13C, 1H, 19F, 31P) or a coupling
    if re.match(r"^[HCFNOP]\b|^[HCFNOP][^a-z]|^J", after):
        return False
    # hybridisation (sp3) and powers of ten (10^5)
    if before.endswith("sp") or re.search(r"10$", before):
        return False
    # units (cm-1) and chi-squared
    if before.endswith("cm⁻") or before.endswith("χ"):
        return False
    # a lone superscript minus is never a citation
    if "⁻" in line[start:end]:
        return False
    return True


def convert(text):
    out, n = [], 0
    for lineno, line in enumerate(text.split("\n"), 1):
        res, last = [], 0
        for m in re.finditer(f"[{SUP}]+", line):
            s, e = m.span()
            if not is_citation(line, s, e, lineno):
                continue
            val = int("".join(DIGIT[c] for c in m.group()))
            if val not in KEYS:
                continue
            res.append((s, e, "[" + "; ".join("@" + k for k in KEYS[val]) + "]"))
        for s, e, rep in res:
            n += 1
        if res:
            buf = []
            for s, e, rep in res:
                buf.append(line[last:s]); buf.append(rep); last = e
            buf.append(line[last:])
            line = "".join(buf)
        out.append(line)
    text = "\n".join(out)
    # merge adjacent citations: "[@a] [@b]" and "[@a][@b]" -> "[@a; @b]"
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\]\s+\[@", "; @", text)
        text = re.sub(r"\]\[@", "; @", text)
    return text, n


def main():
    path = "docs/PAPER.md"
    src = open(path).read()
    new, n = convert(src)
    if "--dry-run" in sys.argv:
        import difflib
        for l in difflib.unified_diff(src.split("\n"), new.split("\n"),
                                      "before", "after", n=0, lineterm=""):
            print(l)
        print(f"\n-- would convert {n} citation superscripts --")
        return
    open(path, "w").write(new)
    print(f"converted {n} citation superscripts in {path}")


if __name__ == "__main__":
    main()
