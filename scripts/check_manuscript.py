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

    truth = {n_irexp: "IRexp records", n_res: "structure-linked records",
             quad: "IR+1H+13C+structure quadruples",
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
CROSS = [
    ("docs/FORWARD_VERIFY.md", ["58/65", "65/194", "55/194", "30/37"]),
    ("README.md", []),
]


def check_cross(md):
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


def main():
    md = read(PAPER)
    for fn in (check_dataset_counts, check_fractions, check_refs,
               check_not_run, check_cross, check_cis):
        fn(md)
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


if __name__ == "__main__":
    main()
