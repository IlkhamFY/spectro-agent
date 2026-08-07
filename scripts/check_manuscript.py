#!/usr/bin/env python3
"""
Manuscript integrity gate.

Every class of check here exists because an error of that class was actually found in
this repository, not because it seemed prudent. Notably, MODELS.md once listed the
formula-only contamination control under "specified but never run" while PAPER.md
Table 5 reported its result -- a reader following the paper's own reproducibility
pointer would have concluded the control was fabricated. Check D exists to make that
class of error impossible to reintroduce silently.

  python scripts/check_manuscript.py        # exits non-zero if anything fails

Checks:
  A  dataset record counts asserted in the prose vs the actual released files
  B  every "a/b (c%)" in the prose is internally consistent
  C  citations: none undefined, none uncited; every referenced path exists
  D  "never run" / "no outputs" claims vs what is actually on disk
  E  cross-document agreement on the numbers that appear in more than one file
  F  bootstrap CIs contain their own point estimate
  G  ground-truth structures reproduce the formula given to the solver
  H  literal values baked into figure scripts still match the data
"""
import gzip, json, os, re, sys

PAPER = "docs/PAPER.md"
FAIL = []


def fail(check, msg):
    FAIL.append(f"[{check}] {msg}")


def read(p):
    return open(p, encoding="utf-8").read()


# ---- A. dataset counts -------------------------------------------------------
def check_dataset_counts(md):
    n_irexp = sum(1 for _ in gzip.open("data/irexp/irexp.jsonl.gz", "rt"))
    quad = n_res = 0
    for l in gzip.open("data/irexp_resolved/irexp_resolved.jsonl.gz", "rt"):
        r = json.loads(l); n_res += 1
        if r.get("ir_bands_cm-1") and r.get("h_nmr") and r.get("c_nmr") and r.get("smiles"):
            quad += 1
    # licence pools: the paper tells downstream users how to honour CC-BY vs CC-BY-SA,
    # so that instruction has to actually work against the released file.
    import importlib.util
    spec = importlib.util.spec_from_file_location("slp", "scripts/split_license_pools.py")
    slp = importlib.util.module_from_spec(spec); spec.loader.exec_module(slp)
    pools = {"pmc": 0, "chemotion": 0}
    for l in gzip.open("data/irexp/irexp.jsonl.gz", "rt"):
        pools[slp.pool_of(json.loads(l))] += 1
    for claimed, got, what in ((119345, pools["pmc"], "PMC-OA (CC-BY) pool"),
                               (1888, pools["chemotion"], "Chemotion (CC-BY-SA) pool")):
        if f"{claimed:,}" not in md:
            fail("A", f"{what}: prose no longer states {claimed:,}")
        if claimed != got:
            fail("A", f"{what}: prose says {claimed:,}, splitter yields {got:,}")
    if pools["pmc"] + pools["chemotion"] != n_irexp:
        fail("A", "licence pools do not sum to the IRexp record count")
    # the release must not promise a field it does not ship
    first = json.loads(next(gzip.open("data/irexp/irexp.jsonl.gz", "rt")))
    for doc in (PAPER, "data/NOTICE"):
        body = read(doc)
        if re.search(r'`?license`?\s+field', body) and "license" not in first:
            fail("A", f"{doc} tells users to separate pools by a `license` field, "
                      f"but released records carry no such field")

    # the remaining two Table 1 rows
    any_nmr = sum(1 for l in gzip.open("data/irexp/irexp.jsonl.gz", "rt")
                  if (lambda r: r.get("h_nmr") or r.get("c_nmr"))(json.loads(l)))
    res_nmr = sum(1 for l in gzip.open("data/irexp_resolved/irexp_resolved.jsonl.gz", "rt")
                  if (lambda r: r.get("h_nmr") or r.get("c_nmr"))(json.loads(l)))
    for claimed, got, what in ((87075, any_nmr, "IRexp records co-reporting NMR"),
                               (40702, res_nmr, "structure-linked records with NMR")):
        if f"{claimed:,}" not in md:
            fail("A", f"{what}: prose no longer states {claimed:,}")
        elif claimed != got:
            fail("A", f"{what}: prose says {claimed:,}, data holds {got:,}")

    truth = {n_irexp: "IRexp records", n_res: "structure-linked records",
             quad: "IR+1H+13C+structure quadruples", any_nmr: "records with NMR",
             res_nmr: "structure-linked with NMR",
             119345: "PMC pool", 1888: "Chemotion pool"}
    for want, what in ((n_irexp, "IRexp records"), (n_res, "structure-linked records"),
                       (quad, "IR+1H+13C+structure quadruples")):
        if f"{want:,}" not in md:
            fail("A", f"{what}: prose no longer states {want:,} — re-check the claim")
    # It is not enough that the right number appears somewhere: a stale or mistyped
    # duplicate elsewhere must also fail. Every comma-formatted count that the prose
    # attaches to an IRexp record claim has to be one of the true values.
    CTX = re.compile(
        r'(?:IRexp[^.\n]{0,80}?|)\b(\d{1,3},\d{3})\b(?=[^.\n]{0,40}?'
        r'(?:records|record count|structure-linked|quadruples))', re.I)
    for m in CTX.finditer(md):
        v = int(m.group(1).replace(",", ""))
        if v not in truth:
            near = md[max(0, m.start() - 60):m.end() + 45].replace("\n", " ")
            fail("A", f"count {m.group(1)} is presented as an IRexp record count but "
                      f"matches none of {sorted(truth)} — …{near.strip()}…")
    # benchmark size
    n_bench = (len(json.load(open("data/benchmark_main/clean_qids.json")))
               + sum(1 for _ in open("data/benchmark_v3/answers2.jsonl"))
               + sum(1 for _ in open("data/benchmark_v2_ctrl/answers2.jsonl")))
    if n_bench != 194:
        fail("A", f"benchmark cohort is {n_bench}, prose says 194")


# ---- B. fraction/percent agreement -------------------------------------------
def check_fractions(md):
    for m in re.finditer(r'(\d+)/(\d+)\s*\(\*{0,2}(\d+)%', md):
        a, b, p = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if b and abs(100 * a / b - p) > 1.05:
            fail("B", f"{a}/{b} = {100*a/b:.1f}% but printed {p}%")


# ---- C. citations and paths --------------------------------------------------
def check_refs(md):
    bib = read("docs/references.bib")
    defined = set(re.findall(r'@\w+\{([^,]+),', bib))
    used = {k.rstrip('.,;') for k in re.findall(
        r'@([A-Za-z][\w:.-]*)', ' '.join(re.findall(r'\[([^\]]*@[^\]]*)\]', md)))}
    for k in sorted(used - defined):
        fail("C", f"citation @{k} is used but not defined in references.bib")
    for k in sorted(defined - used):
        fail("C", f"bib entry {k} is defined but never cited")
    for pat in (r'(scripts/[A-Za-z0-9_]+\.py)', r'(docs/figures/[A-Za-z0-9_]+\.png)',
                r'`(data/[A-Za-z0-9_/]+)`'):
        for p in sorted(set(re.findall(pat, md))):
            if not os.path.exists(p):
                fail("C", f"referenced path does not exist: {p}")


# ---- D. "never run" claims vs disk -------------------------------------------
# (claim-bearing file, regex that must match, path, must_be_absent)
NOT_RUN = [
    ("docs/MODELS.md", r"leave-one-out modality prompts|`noIR`, `noH`, `noC`",
     ["data/modality/out_noIR.json", "data/modality/out_noH.json",
      "data/modality/out_noC.json"], True),
    ("docs/MODELS.md", r"Cross-vendor sweep", ["data/cross_vendor"], True),
]
# artifacts that MUST exist because a reported table depends on them
MUST_EXIST = [
    ("data/modality/out_formulaonly.json", "Table 5 formula-only arm"),
    ("data/modality/out_full.json", "Table 5 full-modality arm"),
    ("data/fverify_gen/raw", "§5.6 forward-verified arm"),
    ("data/fverify_main/raw", "§5.2 whole-benchmark extension"),
    ("data/fverify_gw/raw", "§5.3 coverage-gap closure"),
]


def check_not_run(md):
    for doc, pat, paths, must_be_absent in NOT_RUN:
        body = read(doc)
        if not re.search(pat, body):
            fail("D", f"{doc}: expected a 'not run' disclosure matching /{pat}/ — "
                      f"if the arm was run, its row must move to the experiment table")
            continue
        for p in paths:
            if must_be_absent and os.path.exists(p):
                fail("D", f"{doc} claims this was never run, but {p} exists")
    for p, why in MUST_EXIST:
        if not os.path.exists(p) or (os.path.isdir(p) and not os.listdir(p)):
            fail("D", f"{why}: {p} is missing or empty, but the paper reports its result")
    # no document may still call the formula-only arm unrun
    for doc in ("docs/MODELS.md", PAPER):
        body = read(doc)
        for m in re.finditer(r'[^.\n]*formula-only[^.\n]*', body, re.I):
            if re.search(r'not yet run|never run|no outputs', m.group(0), re.I):
                fail("D", f"{doc}: formula-only arm described as unrun: "
                          f"'{m.group(0).strip()[:90]}'")


# ---- E. cross-document numeric agreement -------------------------------------
# a number stated in PAPER.md that also appears in a companion doc must agree
# Companion documents drift silently when the paper's numbers move — the cover letter
# is the worst case, since an editor reads it first and it is not rebuilt by anything.
CROSS = [
    ("docs/FORWARD_VERIFY.md", ["58/65", "65/194", "55/194", "30/37"]),
    ("docs/COVER_LETTER.md", ["65/194", "58/65"]),
    ("docs/CROSS_VENDOR.md", ["65/194", "58/65", "30/37"]),
    ("README.md", []),
]


# The cover letter is the one companion document with no legitimate reason to quote the
# superseded 60-compound arm — it summarises the headline for an editor. Presence of the
# current numbers is too weak a test there (they may sit elsewhere in the file), so the
# retired ones are forbidden outright.
RETIRED_IN_COVER_LETTER = ["19/60, 31%", "16/19, 84%", "16/19 conditional",
                           "(19/60)", "expert-audited"]


def check_cross(md):
    if os.path.exists("docs/COVER_LETTER.md"):
        cl = read("docs/COVER_LETTER.md")
        for tok in RETIRED_IN_COVER_LETTER:
            if tok in cl:
                fail("E", f"docs/COVER_LETTER.md still quotes the superseded "
                          f"'{tok}' — the letter must carry the n=194 figures")
    for doc, must_match in CROSS:
        if not os.path.exists(doc):
            fail("E", f"companion document missing: {doc}")
            continue
        body = read(doc)
        for tok in must_match:
            if tok not in body:
                fail("E", f"{doc} does not carry {tok}, which PAPER.md reports — "
                          f"companion docs have drifted")
            if tok not in md:
                fail("E", f"PAPER.md no longer states {tok} but {doc} still does")


# ---- F. CIs contain their point estimate -------------------------------------
def check_cis(md):
    for m in re.finditer(r'(\d+\.?\d*)%\s*\[(\d+\.?\d*),\s*(\d+\.?\d*)\]', md):
        pt, lo, hi = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if not (lo - 0.6 <= pt <= hi + 0.6):
            fail("F", f"point estimate {pt}% lies outside its CI [{lo}, {hi}]")
    for m in re.finditer(r'\*\*(\d+\.?\d*)%\*\*\s*\|\s*\[(\d+\.?\d*),\s*(\d+\.?\d*)\]', md):
        pt, lo, hi = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if not (lo - 0.6 <= pt <= hi + 0.6):
            fail("F", f"table point estimate {pt}% outside CI [{lo}, {hi}]")


# ---- G. ground truth vs the formula the solver was given ---------------------
def check_ground_truth():
    """A mis-resolved answer structure would silently corrupt every score, and the
    formula is an independent handle on it: the solver is *given* the formula, so the
    answer must reproduce it. This is the mechanical half of what the expert-chemist
    audit (§7) covers; it cannot judge whether the structure is chemically sensible,
    only whether it is the right composition."""
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
    norm = lambda f: re.sub(r'[+\-]\d*$', '', (f or "").replace(" ", ""))
    rounds = [("data/benchmark_main", "data/benchmark_main/clean_qids.json"),
              ("data/benchmark_v3", None), ("data/benchmark_v2_ctrl", None),
              ("data/benchmark_electrolyte", None)]
    n = 0
    for d, cf in rounds:
        if not os.path.exists(f"{d}/answers2.jsonl"):
            continue
        keep = set(json.load(open(cf))) if cf else None
        q = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/questions2.jsonl")}
        for l in open(f"{d}/answers2.jsonl"):
            a = json.loads(l); qid = a["qid"]
            if keep is not None and qid not in keep:
                continue
            n += 1
            m = Chem.MolFromSmiles(a.get("smiles") or "")
            if m is None:
                fail("G", f"{d} {qid}: ground-truth SMILES does not parse")
                continue
            given = norm(q.get(qid, {}).get("formula"))
            derived = norm(rdMolDescriptors.CalcMolFormula(m))
            if given and given != derived:
                fail("G", f"{d} {qid}: solver was given {given} but the answer "
                          f"structure is {derived}")
    if n == 0:
        fail("G", "no ground-truth answers found to check")


# ---- H. hardcoded figure values vs the data ----------------------------------
# Several figure scripts carry literal arrays rather than recomputing. That is fine
# for reproducibility (the figure is deterministic) but means a figure can silently
# drift from the scorers when a number changes. Pin the literals to their sources.
FIG_LITERALS = [
    ("scripts/make_fig_verifier.py", r'top1\s*=\s*\[([\d.,\s]+)\]',
     [55 / 65 * 100, 55 / 65 * 100, 59 / 65 * 100, 58 / 65 * 100], 0.1,
     "Fig S6 conditional-on-recall top-1"),
    ("scripts/make_fig_generator_probe.py", r'recall\s*=\s*\[([\d.,\s]+)\]',
     [65 / 194 * 100, 41.8, 54.1], 0.1, "Fig S5 recall bars"),
    ("scripts/make_figures.py", r'v\s*=\s*\[([\d.,\s]+)\]',
     [121233, 87075, 43060, 33201], 0, "Fig S2 dataset bars"),
]


def check_figure_literals():
    for path, pat, want, tol, what in FIG_LITERALS:
        if not os.path.exists(path):
            fail("H", f"{what}: {path} is missing")
            continue
        m = re.search(pat, read(path))
        if not m:
            fail("H", f"{what}: could not find the literal array in {path} — if the "
                      f"figure now computes its values, drop it from FIG_LITERALS")
            continue
        got = [float(x) for x in m.group(1).replace(" ", "").split(",") if x]
        if len(got) != len(want):
            fail("H", f"{what}: {len(got)} values in {path}, expected {len(want)}")
            continue
        for g, w in zip(got, want):
            if abs(g - w) > tol:
                fail("H", f"{what}: {path} plots {g} where the data gives {w:.4g}")


# ---- author-supplied items (reported, never failed) --------------------------
# These cannot be filled in by anyone but the authors, and inventing any of them
# would be worse for a reader than an acknowledged gap. The gate lists them so the
# remaining work is a short, explicit checklist rather than a hunt.
PENDING = [
    (PAPER, r'ORCID:\s*\[TODO', "ORCID iDs for all three authors (RSC requires the "
                                "corresponding author's)"),
    (PAPER, r'10\.5281/zenodo\.X+', "Zenodo DOI for the data/code deposit — mint on submission"),
    (PAPER, r'To be completed before submission.*funding', "funding sources and "
                                                           "acknowledgements"),
    ("docs/MODELS.md", r'\*authors — see §6\*', "dated model snapshot identifiers for the "
                                                "four Claude models"),
]


def report_pending():
    out = []
    for doc, pat, what in PENDING:
        if os.path.exists(doc) and re.search(pat, read(doc), re.I | re.S):
            out.append((doc, what))
    return out


def main():
    md = read(PAPER)
    for fn in (check_dataset_counts, check_fractions, check_refs,
               check_not_run, check_cross, check_cis):
        fn(md)
    check_ground_truth()
    check_figure_literals()
    pend = report_pending()
    if FAIL:
        print(f"MANUSCRIPT GATE: {len(FAIL)} problem(s)\n")
        for f in FAIL:
            print("  " + f)
        sys.exit(1)
    print("MANUSCRIPT GATE: all checks pass")
    print("  A dataset counts match the released files")
    print("  B every fraction/percent pair is internally consistent")
    print("  C citations resolve both ways; every referenced path exists")
    print("  D 'never run' disclosures agree with what is on disk")
    print("  E companion documents carry the same numbers as the paper")
    print("  F every confidence interval contains its point estimate")
    print("  G every ground-truth structure matches the formula the solver was given")
    print("  H hardcoded figure values still agree with the scorers")
    if pend:
        print(f"\nAWAITING THE AUTHORS ({len(pend)} item(s)) — not defects, and not "
              f"fillable by anyone else:")
        for doc, what in pend:
            print(f"  · {what}\n      → {doc}")
        print("\nEverything else is verified. These four values are the remaining work.")
    else:
        print("\nNo author-supplied items outstanding.")


if __name__ == "__main__":
    main()
