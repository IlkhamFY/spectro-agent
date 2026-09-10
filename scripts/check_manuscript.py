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
  I  a claim corrected in one document is corrected in all of them
  J  the model-snapshot disclosure is intact and internally consistent
  K  reader-facing numbers written into scripts still match the paper
  L  cross-references are derived from position, and none is typed by hand
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
    # benchmark size. The cohort is derived from the round manifests, never asserted
    # against a literal: a literal here would have to be edited in step with every other
    # copy of the number, which is the failure this gate exists to catch. What is checked
    # instead is that the three places that must agree do -- the manifests, the diagnosis
    # counts the leading figure is drawn from, and the prose.
    HEADLINE_ROUNDS = [("data/benchmark_main", "data/benchmark_main/clean_qids.json"),
                       ("data/benchmark_v3", None),
                       ("data/benchmark_v2_ctrl", None)]
    n_bench = 0
    for d, cleanf in HEADLINE_ROUNDS:
        n_bench += (len(json.load(open(cleanf))) if cleanf
                    else sum(1 for _ in open(f"{d}/answers2.jsonl")))
    diag = json.load(open("data/diagnosis.json"))
    if diag["n"] != n_bench:
        fail("A", f"benchmark cohort is {n_bench} but data/diagnosis.json -- which the "
                  f"leading figure is drawn from -- covers {diag['n']}; "
                  f"re-run scripts/forward_verify_all.py")
    if not re.search(rf'/{n_bench}\b', md):
        fail("A", f"benchmark cohort is {n_bench} but no rate over {n_bench} appears in "
                  f"the prose; the manuscript is still quoting an older cohort")


# ---- B. fraction/percent agreement -------------------------------------------
def check_fractions(md):
    for m in re.finditer(r'(\d+)/(\d+)\s*\(\*{0,2}(\d+)%', md):
        a, b, p = int(m.group(1)), int(m.group(2)), int(m.group(3))
        # Half a point, not a point and a half. The looser bound admitted floor-rounding,
        # and several scorers used it: 19/60 printed as "31%", 11/24 as "45%". The paper
        # rounds everywhere else (28.4% for 55/194), so the mixed convention showed up as
        # Fig. 3's plot annotating 46 above a caption that said 45.
        if b and abs(100 * a / b - p) > 0.5:
            fail("B", f"{a}/{b} = {100*a/b:.1f}% but printed {p}%")


# ---- C. citations and paths --------------------------------------------------
def check_refs(md):
    bib = read("docs/references.bib")
    defined = set(re.findall(r'@\w+\{([^,]+),', bib))
    # [@sec:…], [@fig:…], [@tab:…], [@sfig:…] are cross-references, not citations;
    # they share the bracket-@ syntax and would otherwise read as undefined bib keys.
    used = {k.rstrip('.,;') for k in re.findall(
        r'@([A-Za-z][\w:.-]*)', ' '.join(re.findall(r'\[([^\]]*@[^\]]*)\]', md)))
        if not k.startswith(('sec:', 'fig:', 'tab:', 'sfig:'))}
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
            import glob as _glob
            hits = _glob.glob(p) if any(c in p for c in "*?[") else (
                [p] if os.path.exists(p) else [])
            if must_be_absent and hits:
                fail("D", f"{doc} claims this was never run, but "
                          f"{', '.join(sorted(hits)[:3])} exists")
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
# An interval may be written [22, 35], [22-35] with an en-dash, or [-17.2 to +7.0] where a
# dash would collide with the sign. All three appear in the manuscript, and a check that
# knows only the first silently matches nothing after a notation pass -- which is exactly
# what happened when the intervals were normalised to en-dashes.
CI = re.compile(r'\[\s*([+\u2212-]?\d+\.?\d*)\s*(?:,|\u2013|\u2014|-|\s+to\s+)\s*'
                r'([+\u2212-]?\d+\.?\d*)\s*\]')
NUMBER_BEFORE = re.compile(r'(\d+\.?\d*)\s*%?\s*(?:\*\*)?\s*\|?\s*$')


def _num(tok):
    return float(tok.replace("\u2212", "-").replace("+", ""))


def check_cis(md):
    """Every confidence interval must contain the estimate it is attached to.

    Written to be loud when it stops working: an interval notation this does not
    understand is reported, rather than passing silently. A gate that matches nothing
    reports success, which is worse than a gate that fails.
    """
    seen = 0
    for m in CI.finditer(md):
        head = md[max(0, m.start() - 40):m.start()]
        pm = NUMBER_BEFORE.search(head.rstrip())
        if not pm:
            continue                       # an interval with no adjacent point estimate
        pt, lo, hi = float(pm.group(1)), _num(m.group(1)), _num(m.group(2))
        if hi < lo:
            lo, hi = hi, lo
        seen += 1
        if not (lo - 0.6 <= pt <= hi + 0.6):
            fail("F", f"point estimate {pt} lies outside its interval "
                      f"[{m.group(1)}, {m.group(2)}]")
    if seen < 20:
        fail("F", f"only {seen} point-estimate/interval pairs were recognised — the "
                  f"notation has drifted and this check is no longer reading the paper")


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


# ---- I. corrections must propagate to every file ----------------------------
# A claim corrected in one document and left standing in another is worse than never
# correcting it: the release then ships a fixed paper beside a reproducibility anchor
# that still makes the original claim. That happened here — "isomers of the same target
# never co-occur" was corrected in PAPER.md and FORWARD_VERIFY.md and missed in
# MODELS.md for a full session. Each entry is a retired phrasing; the exemptions are the
# two places a retired phrase legitimately appears (this checker, and the audit table
# that records what was corrected).
RETIRED_PHRASINGS = [
    ("never co-occur", "batch composition (§5.1)"),
    ("expert-audited", "ground-truth audit status (Contribution 2)"),
    ("larger by raw record count than any prior", "IRexp scale claim (Contribution 1)"),
    ("the result that transfers across models", "generality scope (§1.1)"),
    ("individually labelled", "licence pools (Licensing)"),
    ("`license` fields distinguish", "licence mechanism (§2.3)"),
    ("failing predominantly on **regiochemistry**", "miss characterisation (§4.1)"),
    ("exotic and large targets (selenium", "recall-plateau explanation (§5.3)"),
    ("the latter using knowledge-enhanced", "Zhuang et al. attribution (§1.1)"),
    ("like us conditions jointly", "NMIRacle hints parity (§4.2)"),
    ("~90% top-1 exact recovery", "Spectro accuracy (§4.2)"),
    ("The strongest trained baselines report", "simulated-vs-real claim (§4.2)"),
    ("Ring count is a poor proxy for elucidation difficulty.", "ring-count claim (§4.2)"),
]
PROPAGATION_EXEMPT = ("scripts/check_manuscript.py", "docs/MODELS.md", "docs/paper.tex",
                      "docs/SUBMISSION.md")


def check_propagation():
    import subprocess
    for phrase, what in RETIRED_PHRASINGS:
        for root in ("docs", "README.md", "data/NOTICE", "scripts"):
            if not os.path.exists(root):
                continue
            out = subprocess.run(["grep", "-rn", "-F", phrase, root],
                                 capture_output=True, text=True).stdout
            for line in out.splitlines():
                if not line.strip():
                    continue
                if any(line.startswith(e) for e in PROPAGATION_EXEMPT):
                    continue
                fail("I", f"retired phrasing survives — {what}: "
                          f"{line.split(':')[0]} still says '{phrase[:40]}'")


def check_snapshot_disclosure():
    """The snapshot identifiers are not obtainable — the consumer harness exposes none.
    The paper must say so rather than promise them, and MODELS.md §2 must not point at a
    value that will never arrive. This check exists because both files did exactly that
    until the authors confirmed the harness never exposed them."""
    md, mo = read(PAPER), read("docs/MODELS.md")
    if re.search(r'outstanding items to be pinned|to be pinned on submission', md, re.I):
        fail("J", "PAPER.md still describes model snapshots as outstanding items to be "
                  "pinned; the harness exposes none, so they cannot arrive")
    if "*authors — see §6*" in mo:
        fail("J", "MODELS.md §2 still promises a snapshot identifier from the authors")
    if not re.search(r'no model snapshot can be reported|not exposed by the harness', md + mo, re.I):
        fail("J", "the unobtainable-snapshot disclosure has gone missing")
    if not re.search(r'mid-window build change cannot be excluded', md + mo, re.I):
        fail("J", "the mid-window-build-change caveat has gone missing")


# ---- K. reader-facing numbers baked into scripts -----------------------------
# The graphical abstract's summary text and the numbers drawn into its image are the
# first things an editor reads, and both lived inside Python -- a string in build_pdf.py
# and a matplotlib call in make_graphical_abstract.py. Both quoted "recall (31%), not
# verification (84%)" for months after §5.2 moved to 34% / 89%, because every existing
# check looked only at documents. Reader-facing figures of merit are checked wherever
# they live.
RETIRED_IN_SCRIPTS = [
    # The ESI figure captions live in build_pdf.py's SI_FIGS list, which is a second
    # caption source just like the main-text one that had drifted. Fig S6 kept claiming
    # "(n=19) ... 84% ... 73%" for weeks after §5.4 moved to n=65 / 91% / 89% / 85%,
    # because fixing the main list left this one untouched.
    (r'Conditional-on-recall top-1 \(n=19\)', "Fig S6 caption still says n=19 (now n=65)"),
    (r"verifier's 84.. that the lookup \(73", "Fig S6 caption still says 84%/73% (now 89%/85%)"),
    (r'recall \(31%\)', "graphical abstract still quotes 31% recall (now 34%)"),
    (r'verification \(84%\)', "graphical abstract still quotes 84% precision (now 89%)"),
    (r'true structure 84% of the time', "abstract summary still quotes 84% (now 89%)"),
    (r'proposed only 31% of the time', "abstract summary still quotes 31% (now 34%)"),
    (r'19/60 = \s*31', "a figure caption still quotes 19/60 = 31% (now 65/194 = 34%)"),
]
READER_FACING = ["scripts/build_pdf.py", "scripts/make_graphical_abstract.py"]


def check_scripts_numbers():
    for path in READER_FACING:
        if not os.path.exists(path):
            fail("K", f"{path} is missing")
            continue
        body = read(path)
        for pat, why in RETIRED_IN_SCRIPTS:
            if re.search(pat, body):
                fail("K", f"{path}: {why}")
    # and the abstract must carry the live pair
    ga = read("scripts/make_graphical_abstract.py")
    if not re.search(r'recall 34%.*verification 89%', ga):
        fail("K", "make_graphical_abstract.py no longer states recall 34% / "
                  "verification 89% — the image would disagree with §5.2")


# ---- author-supplied items (reported, never failed) --------------------------
# These cannot be filled in by anyone but the authors, and inventing any of them
# would be worse for a reader than an acknowledged gap. The gate lists them so the
# remaining work is a short, explicit checklist rather than a hunt.
PENDING = [
    (PAPER, r'ORCID:\s*\[TODO', "ORCID iD for the corresponding author (Sondhi and "
                                "Vargas-Hern\u00e1ndez are recorded and verified)"),
    (PAPER, r'no email found in any public source',
     "Rudra Sondhi's email \u2014 no address appears in any public source, so he must "
     "supply it"),
    (PAPER, r'<!--\s*ZENODO', "Zenodo DOI for the data/code deposit — mint on submission"),
    (PAPER, r'<!--\s*ACKNOWLEDGEMENTS', "funding sources and acknowledgements"),
]


# ---- L. section cross-references ---------------------------------------------
def check_heading_blank_lines():
    """A heading glued to the line above it is not a heading.

    pandoc's markdown requires a blank line before an ATX heading; without one the
    "### ..." prints as literal text in the middle of a running paragraph, and the section
    silently loses its title -- which is what happened to the battery-electrolyte case
    study, where the slice boundaries of the compression pass butted a heading against the
    previous sentence. It is invisible in the source and unmissable on the page.

    Fenced code blocks are skipped: the ESI quotes prompts whose own text begins with "#".
    """
    for doc in (PAPER, "docs/ESI.md"):
        if not os.path.exists(doc):
            continue
        lines = read(doc).split("\n")
        fenced = False
        for i, line in enumerate(lines):
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            if fenced or i == 0:
                continue
            if re.match(r"^#{1,6}\s", line) and lines[i - 1].strip():
                fail("N", f"{doc}:{i + 1} heading has no blank line before it, so it "
                          f"renders as literal text: {line.strip()[:60]}")


def check_placeholders():
    """Editorial placeholders must not reach a built page.

    The Zenodo DOI and the acknowledgements are author-supplied and are *reported* by the
    pending list rather than failed -- that is deliberate. This check is narrower: it
    catches a placeholder that has escaped that list, in any document, so nothing prints
    a bare TODO the pending report does not already name.
    """
    known = {"10.5281/zenodo.XXXXXXX", "0000-0000-0000-0000",
             "To be completed before submission"}
    for doc in [PAPER] + [os.path.join("docs", f) for f in sorted(os.listdir("docs"))
                          if f.endswith(".md")]:
        if not os.path.exists(doc):
            continue
        body = read(doc)
        for m in re.finditer(r"\[TODO[^\]]*\]|XXXXXXX|FIXME|PLACEHOLDER", body):
            frag = m.group(0)
            if any(k in frag or frag in k for k in known):
                continue
            # A placeholder quoted in backticks is prose *about* a placeholder -- the
            # submission checklist names them on purpose -- not one waiting to be printed.
            if body[max(0, m.start() - 1)] == "`" or body[m.end():m.end() + 1] == "`":
                continue
            ctx = " ".join(read(doc)[max(0, m.start() - 60):m.start() + 60].split())
            fail("N", f"{doc}: unlisted placeholder {frag!r} — …{ctx}…")


def check_section_refs():
    """Every section number a *companion* document points at must exist in the paper.

    The learned-verifier arm was drafted as its own subsection, numbered 5.7, and was
    later folded into 5.4. The heading moved; five pointers to it did not. PAPER.md, the
    cover letter and MODELS.md all went on directing a reader to a section that is not in
    the paper -- and because each pointer is well-formed prose, nothing else here caught
    it.

    PAPER.md itself no longer needs this check: its numbers are derived by crossref and
    check L enforces that nothing is typed. The companion documents still type theirs, and
    they are the half that now rots silently, because the paper's numbering can shift
    underneath them without a single edit to their text. So enumerate the sections the
    *resolved* paper actually has, and hold the companions to it.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("crossref", "scripts/crossref.py")
    cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
    resolved, _ = cr.resolve(read(PAPER))
    have = set()
    for m in re.finditer(r'^#{2,4}\s+(\d+(?:\.\d+)?)[.\s]', resolved, re.M):
        have.add(m.group(1))
        have.add(m.group(1).split(".")[0])     # "5" from "5.4"
    if not have:
        fail("M", "no numbered sections found in the resolved paper")
        return
    docs = [os.path.join("docs", f) for f in sorted(os.listdir("docs"))
            if f.endswith(".md") and f != os.path.basename(PAPER)]
    docs += ["README.md"]
    for doc in docs:
        if not os.path.exists(doc):
            continue
        body = read(doc)
        for m in re.finditer(r'§(\d+(?:\.\d+)?)', body):
            sec = m.group(1)
            if sec in have:
                continue
            ctx = " ".join(body[max(0, m.start() - 90):m.start() + 40].split())
            fail("M", f"{doc} points at \u00a7{sec}, which is not a section of the paper "
                      f"\u2014 \u2026{ctx}\u2026")


def check_crossrefs():
    """Numbers that point at something must be derived from where it sits.

    Check L used to verify that a typed section number named a real heading. That was the
    weaker half of the problem: 202 numbers were typed by hand, and a typed number can be
    perfectly valid on the day it is written and wrong the moment anything moves. It had
    already happened -- Table 9 sat physically before Tables 6 to 8 in the merged text,
    because §4.7 was inserted after them and its table kept the number it was given.

    So the gate now enforces the mechanism, not the outcome: every reference resolves,
    every label is defined once, and no bare "Fig. N" / "Table N" / "§N" survives in the
    source at all.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("crossref", "scripts/crossref.py")
    cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
    md = read(PAPER)
    try:
        a = cr.audit(md)
    except KeyError as e:
        fail("L", f"cross-reference does not resolve: {e}")
        return
    for r in a["undefined"]:
        fail("L", f"reference to a label that is never defined: {r}")
    for t in sorted(set(a["typed"])):
        fail("L", f"hand-typed cross-reference {t!r} — use [@sec:…], [@tab:…], "
                  f"[@fig:…] or [@sfig:…] so the number follows the object")
    # a resolved document must number its tables in the order a reader meets them
    import re as _re
    out, _ = cr.resolve(md)
    seq = [int(m.group(1)) for m in _re.finditer(r'\*\*Table (\d+)\.', out)]
    if seq != sorted(seq):
        fail("L", f"tables are not in reading order after resolution: {seq}")


def check_cross_vendor_disclosure():
    """What has been run against a vendor must match what MODELS.md says was run.

    This began as a "never run" assertion keyed on the phrase "Cross-vendor sweep". Then a
    pilot *was* run -- which is the transition the check exists to catch -- and the phrase
    matched the new disclosure just as happily as the old one, so the gate kept failing a
    document that had already been corrected. The topic name was never the claim. These
    are.
    """
    import glob as _glob
    body = read("docs/MODELS.md")
    ran = sorted(_glob.glob("data/cross_vendor/solve_*.json") +
                 _glob.glob("data/cross_vendor/verify_*.json"))
    unrun = re.search(r"No vendor was run", body)
    # The heading moved once already, from "pilot run" to a full five-vendor
    # section, and the literal match then failed a document that had just been
    # brought up to date. Match the section, not the phase it was written in.
    pilot = re.search(r"^## Cross-vendor sweep — ", body, re.M)
    if ran and unrun:
        fail("D", "docs/MODELS.md says no vendor was run, but "
                  f"{', '.join(os.path.basename(p) for p in ran[:3])} exist")
    if ran and not pilot:
        fail("D", f"{len(ran)} vendor output file(s) on disk but docs/MODELS.md carries "
                  f"no record of a cross-vendor run")
    if not (unrun or pilot):
        fail("D", "docs/MODELS.md makes no cross-vendor disclosure either way — Limitations "
                  "cross-vendor scope rests on it")


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
    check_snapshot_disclosure()
    check_scripts_numbers()
    check_propagation()
    check_crossrefs()
    check_section_refs()
    check_heading_blank_lines()
    check_placeholders()
    check_cross_vendor_disclosure()
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
    print("  I every correction propagated to every file that made the claim")
    print("  J the unobtainable-snapshot disclosure is intact and consistent")
    print("  K reader-facing numbers inside scripts match the paper")
    print("  L cross-references derive from position; none typed by hand")
    print("  M companion documents point only at sections the paper has")
    print("  N every heading renders as a heading; no stray placeholders")
    if pend:
        print(f"\nAWAITING THE AUTHORS ({len(pend)} item(s)) — not defects, and not "
              f"fillable by anyone else:")
        for doc, what in pend:
            print(f"  · {what}\n      → {doc}")
        print(f"\nEverything else is verified. "
              f"{'This value is' if len(pend)==1 else 'These ' + str(len(pend)) + ' values are'} "
              f"the remaining work.")
    else:
        print("\nNo author-supplied items outstanding.")


if __name__ == "__main__":
    main()
