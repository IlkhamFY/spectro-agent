#!/usr/bin/env python3
"""How many prompts name a ring system, and does it help?

The benchmark hands the model the spectral strings as printed, which is what puts real
multiplicities and J values in front of it. It also carries whatever the authors wrote in
their peak assignments, and some of them name the scaffold: `2CH2·pyrrolidine`,
`H7·quinox`, `pyridazinone H5`. That is not a formula-level hint, it is part of the
answer -- so the paper's blanket "no name, SMILES or hint is given" is false for those
compounds and has to be replaced with a count.

The count is the point. If the affected compounds were solved at a high rate, the headline
would be partly a hint effect; this reports the rate so the claim can be checked rather
than asserted.

  python scripts/prompt_leakage.py
"""
import json
import re

# No \b before the stem: an assignment written "Hthiophene" carries the ring name just as
# plainly as "thiophene H-3" and the missing word boundary is a typography accident.
RING = re.compile(
    r"(pyrrolidin|pyrolidin|quinox|pyrazol|pyrimidin|indol|pyran|thiophen|thioph[ée]n|"
    r"furan|piperidin|piperazin|imidazol|triazol|traizol|pyridin|pyridazin|pyrrol|"
    r"morpholin|naphth|quinolin|oxazol|thiazol|isoxazol|coumarin|chromen|benzothi|"
    r"benzofur|purin|carbazol|adamant|azetidin|oxetan|tetrazol|indazol|benzimidazol)",
    re.I)

ROUNDS = ("data/benchmark_main", "data/benchmark_v3", "data/benchmark_v2_ctrl")


def _ik14(smiles):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    m = Chem.MolFromSmiles(smiles)
    return Chem.MolToInchiKey(m)[:14] if m else None


def main():
    import glob

    flagged, clean = [], []
    # Same cohort the headline scorer builds: the main round spectrally-validated and
    # solved, the two controlled rounds whole. Duplicating the selection here rather than
    # importing it keeps this check independent of the scorer it is checking.
    for d in ROUNDS:
        q = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/questions2.jsonl")}
        a = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        if d.endswith("benchmark_main"):
            keep = set(json.load(open(f"{d}/clean_qids.json")))
            pred = {}
            for f in glob.glob(f"{d}/raw/*.json"):
                try:
                    pred.update({k[2:]: v for k, v in json.load(open(f)).items()})
                except Exception:
                    pass
        else:
            keep = set(a)
            pred = {json.loads(l)["qid"]: json.loads(l).get("candidates", [])
                    for l in open(f"{d}/predictions2.jsonl")}
        for qid, ans in a.items():
            if qid not in keep or pred.get(qid) is None:
                continue
            cands = pred[qid]
            blob = (q[qid].get("h_nmr") or "") + " " + (q[qid].get("c_nmr") or "")
            hit = RING.search(blob)
            correct = bool(cands) and _ik14(cands[0]) == _ik14(ans["smiles"])
            row = (d.split("/")[-1], qid, hit.group(0).lower() if hit else None, correct)
            (flagged if hit else clean).append(row)

    n_f, n_c = len(flagged), len(clean)
    ok_f = sum(1 for r in flagged if r[3])
    ok_c = sum(1 for r in clean if r[3])
    print(f"prompts naming a ring system in a peak assignment : {n_f} of {n_f + n_c}")
    for r in sorted(flagged):
        print(f"   {r[0]:18s} {r[1]:6s} [{r[2]}]{'  solved' if r[3] else ''}")
    print()
    print(f"  top-1 on those {n_f:3d} : {ok_f}/{n_f} = {100 * ok_f / max(n_f, 1):.1f}%")
    print(f"  top-1 on the other {n_c:3d} : {ok_c}/{n_c} = {100 * ok_c / n_c:.1f}%")
    print("\nA scaffold name in the prompt did not make these compounds easier; they are"
          "\nharder than average, which is why the authors annotated them.")


if __name__ == "__main__":
    main()
