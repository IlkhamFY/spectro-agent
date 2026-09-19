#!/usr/bin/env python3
"""Formula-audit the deposited candidates of one blind round.

A deposit is BAD when *none* of its candidate SMILES reproduces the molecular
formula stated in the question. That is not a scoring pass -- it needs no
answer key -- it only checks that the solver answered the question it was
asked. A deposit whose three candidates all have the wrong formula carries no
information about the solver's chemistry and has to be re-solved.

Charge bookkeeping differs between sources (a question may quote the anion
`C11H16NO3S2-` while a candidate is drawn as the neutral acid, or vice versa),
so a candidate also counts as matching when its heavy-atom counts agree and
its hydrogen count differs only by the charge it carries.

    python scripts/audit_expand500_formulas.py data/benchmark_expand_500
"""
import argparse, glob, json, os, re, sys
from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors
RDLogger.DisableLog("rdApp.*")

TOKEN = re.compile(r"([A-Z][a-z]?)(\d*)")


def parse_formula(f):
    """Return ({element: count}, charge) for a Hill-notation formula string."""
    f = f.strip().replace(" ", "")
    charge = 0
    m = re.search(r"([+-]\d*|\d*[+-])$", f)
    if m and m.group(0):
        tail = m.group(0)
        f = f[: m.start()]
        sign = -1 if "-" in tail else 1
        digits = tail.strip("+-")
        charge = sign * (int(digits) if digits else 1)
    counts = {}
    pos = 0
    while pos < len(f):
        m = TOKEN.match(f, pos)
        if not m or not m.group(1):
            return None, None
        counts[m.group(1)] = counts.get(m.group(1), 0) + (int(m.group(2)) if m.group(2) else 1)
        pos = m.end()
    return counts, charge


def compatible(cand, want):
    """True when candidate formula `cand` answers question formula `want`."""
    if cand.strip() == want.strip():
        return True
    c_counts, c_q = parse_formula(cand)
    w_counts, w_q = parse_formula(want)
    if c_counts is None or w_counts is None:
        return False
    if c_counts == w_counts and c_q == w_q:
        return True
    heavy_c = {k: v for k, v in c_counts.items() if k != "H"}
    heavy_w = {k: v for k, v in w_counts.items() if k != "H"}
    if heavy_c != heavy_w:
        return False
    # protonation state: losing n protons drops n hydrogens and n charge units
    dh = c_counts.get("H", 0) - w_counts.get("H", 0)
    dq = c_q - w_q
    return dh == dq and abs(dh) <= max(1, abs(c_q), abs(w_q))


def candidate_formula(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return rdMolDescriptors.CalcMolFormula(mol)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round", nargs="?", default="data/benchmark_expand_500")
    ap.add_argument("--questions", default=None)
    ap.add_argument("--json", action="store_true", help="emit the BAD list as JSON")
    a = ap.parse_args()

    qpath = a.questions or os.path.join(a.round, "questions2.jsonl")
    want = {}
    with open(qpath) as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                want[r["qid"]] = r["formula"]

    bad, unparseable, missing = [], [], []
    rows = []
    for path in sorted(glob.glob(os.path.join(a.round, "raw", "single_R*.json"))):
        payload = json.load(open(path))
        if isinstance(payload, dict):
            items = list(payload.items())
        else:
            items = [(r["qid"], r.get("candidates", [])) for r in payload]
        for qid, cands in items:
            if qid not in want:
                missing.append(qid)
                continue
            formulas = [candidate_formula(s) for s in cands]
            hits = [f is not None and compatible(f, want[qid]) for f in formulas]
            if None in formulas:
                unparseable.append(qid)
            rows.append((qid, want[qid], list(zip(cands, formulas, hits))))
            if not any(hits):
                bad.append(qid)

    def key(q):
        return int(re.sub(r"\D", "", q) or 0)

    bad = sorted(set(bad), key=key)
    if a.json:
        print(json.dumps(bad))
        return 1 if bad else 0

    print(f"deposits audited : {len(rows)}")
    print(f"unparseable SMILES in : {len(set(unparseable))} deposits")
    print(f"qids not in questions : {sorted(set(missing), key=key) or 'none'}")
    print(f"BAD (no candidate matches the question formula): {len(bad)}")
    for qid in bad:
        w = dict((r[0], r) for r in rows)[qid]
        print(f"  {qid}  want {w[1]}")
        for smi, f, _ in w[2]:
            print(f"      got {f}  {smi}")
    if not bad:
        print("  none")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
