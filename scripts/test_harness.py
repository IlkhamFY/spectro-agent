#!/usr/bin/env python3
"""
Offline tests for the parts of the harness that turn a model's reply into a number.

No network, no API key, no model. Everything here is a pure function, and every case is
one that has already cost something in this repository or is one keystroke away from it.

The function under most suspicion is `extract_json`. When it fails it does not raise --
it returns `{}`, the caller records "no candidates", and the vendor takes a zero in the
recall column that is indistinguishable from a model that answered wrongly. A silent
zero is the most expensive kind of bug this codebase can have, because it looks like a
finding.

  python scripts/test_harness.py        # exits non-zero on any failure
"""
import importlib.util, json, os, sys

sys.path.insert(0, "scripts")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


FAIL = []


def check(name, got, want):
    if got != want:
        FAIL.append(f"{name}\n      got:  {got!r}\n      want: {want!r}")


def main():
    orr = load("openrouter_run", "scripts/openrouter_run.py")
    bp = load("build_pdf", "scripts/build_pdf.py")

    # ---- extract_json: every wrapper a model has actually used ------------------
    want = {"M001": ["CCO", "COC"]}
    for label, raw in [
        ("bare json",        '{"M001": ["CCO", "COC"]}'),
        ("fenced json",      '```json\n{"M001": ["CCO", "COC"]}\n```'),
        ("bare fence",       '```\n{"M001": ["CCO", "COC"]}\n```'),
        ("prose before",     'Here are my answers:\n{"M001": ["CCO", "COC"]}'),
        ("prose either side", 'Sure!\n{"M001": ["CCO", "COC"]}\nHope that helps.'),
        ("fence plus prose", 'Result:\n```json\n{"M001": ["CCO", "COC"]}\n```\nDone.'),
        ("leading newline",  '\n\n{"M001": ["CCO", "COC"]}\n'),
    ]:
        check(f"extract_json/{label}", orr.extract_json(raw), want)

    # The cases above all also parse via the outermost-brace fallback, so on their own
    # they do not test the fence path at all -- deleting the fence handling left them
    # green. This one separates the two: prose containing braces *before* a fenced
    # payload defeats outermost-brace matching, because the span it grabs starts in the
    # prose. Only stripping the fence first recovers the answer.
    check("extract_json/fence needed, braces in the prose",
          orr.extract_json('I weighed {A, B} and settled on:\n'
                           '```json\n{"M001": ["CCO", "COC"]}\n```'), want)

    # SMILES are full of braces and brackets; the brace-matching fallback has to survive
    # a payload whose *values* contain them, not just the object delimiters.
    smi = {"M001": ["C[C@H](N)C(=O)O", "c1ccc2c(c1)[nH]c1ccccc12"]}
    check("extract_json/smiles with brackets",
          orr.extract_json("answer:\n" + json.dumps(smi)), smi)

    # Failure must be empty, not an exception -- callers treat {} as "no candidates".
    for label, raw in [("empty", ""), ("none", None), ("prose only", "I cannot answer."),
                       ("truncated", '{"M001": ["CCO",')]:
        check(f"extract_json/{label} -> empty", orr.extract_json(raw), {})

    # ---- split_batches: one context per batch, header carried into each ---------
    prompt = "HEADER LINE\n\n## batch 1\nP001 CCO\n\n## batch 2\nP002 COC\n"
    parts = orr.split_batches(prompt)
    check("split_batches/count", len(parts), 2)
    check("split_batches/header in every part",
          all(p.startswith("HEADER LINE") for p in parts), True)
    check("split_batches/no cross-contamination",
          ("P002" in parts[0], "P001" in parts[1]), (False, False))
    # A prompt with no batch markers is a single batch, not zero.
    check("split_batches/unbatched", len(orr.split_batches("HEADER\nP001 CCO\n")), 1)

    # ---- proportional_tables: the separator must clear pandoc's 72-column bar ----
    md = ("| metric | a | b |\n|---|--:|--:|\n"
          "| scaffold-level (best Tanimoto >= 0.45) | 56% | 73% |\n")
    out = bp.proportional_tables(md)
    sep = [l for l in out.split("\n") if set(l) <= set("|-: ") and "-" in l][0]
    check("proportional_tables/over pandoc's --columns", len(sep) > 72, True)
    # widest column must get the largest share, or the wrapping this fixes comes back
    cells = [c for c in sep.strip("|").split("|")]
    check("proportional_tables/widest column is widest",
          len(cells[0]) == max(len(c) for c in cells), True)
    # right-alignment markers must survive, or every numeric column silently left-aligns
    check("proportional_tables/keeps right alignment",
          all(c.endswith(":") for c in cells[1:]), True)
    # a table already proportional must not be mangled
    check("proportional_tables/idempotent",
          bp.proportional_tables(out), out)

    # ---- breakable_paths: only inside code spans -------------------------------
    ZW = bp.ZWSP
    check("breakable_paths/breaks after a slash, inside code spans only",
          bp.breakable_paths("see `scripts/forward_verify.py` now"),
          f"see `scripts/{ZW}forward_verify.py` now")
    # Not after "_": that splits one identifier into what reads as two names --
    # MODALITY_ABLATION.md printed as "MODALITY_" / "ABLATION.md" in the ESI.
    check("breakable_paths/does not break an identifier at an underscore",
          bp.breakable_paths("`docs/MODALITY_ABLATION.md`"),
          f"`docs/{ZW}MODALITY_ABLATION.md`")
    # A trailing separator must not take a break either, or the following comma is
    # stranded at the head of the next line.
    check("breakable_paths/no break after a trailing separator",
          bp.breakable_paths("`data/audit/`, and"), f"`data/{ZW}audit/`, and")
    check("breakable_paths/leaves prose alone",
          bp.breakable_paths("a/b and c_d in prose"), "a/b and c_d in prose")
    check("breakable_paths/leaves plain code alone",
          bp.breakable_paths("`RDKit`"), "`RDKit`")

    if FAIL:
        print(f"HARNESS TESTS: {len(FAIL)} failure(s)\n")
        for f in FAIL:
            print("  " + f)
        sys.exit(1)
    print("HARNESS TESTS: all pass")
    print("  extract_json survives fences, prose, bracketed SMILES; fails to {} not an exception")
    print("  split_batches gives one self-contained context per batch")
    print("  proportional_tables clears pandoc's 72-column threshold and keeps alignment")
    print("  breakable_paths touches code spans only")


if __name__ == "__main__":
    main()
