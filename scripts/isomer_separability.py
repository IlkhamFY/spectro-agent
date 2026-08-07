#!/usr/bin/env python3
"""
How far apart does the forward predictor actually place two candidates for the same
compound?

§5.1 motivates forward-verification by asserting that "regioisomers, crucially, have
different forward-predicted ¹³C shifts", supported by one worked example. That is the
mechanism the whole method rests on, so it deserves a distribution rather than an
anecdote — and the distribution turns out to qualify it sharply.

For every pair of candidates proposed for the same target, we take the chamfer distance
between their two *predicted* spectra (not against the observed one). If that distance
is smaller than the predictor's own ~2 ppm error, the predictor cannot reliably tell the
two apart no matter how different the real spectra are.

  python scripts/isomer_separability.py
"""
import glob, itertools, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specmetrics import chamfer
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

ARMS = ["data/fverify", "data/fverify_main"]
PREDICTOR_ERROR_PPM = 2.0


def canon(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToSmiles(m) if m else None


def predictions():
    out = {}
    for arm in ARMS:
        amap = json.load(open(f"{arm}/anon_map.json"))
        raw = {}
        for f in glob.glob(f"{arm}/raw/*.json"):
            raw.update(json.load(open(f)))
        out.update({canon(s): raw[a] for s, a in amap.items()
                    if a in raw and canon(s)})
    return out


def main():
    P = predictions()
    comps = {}
    for arm in ARMS:
        for l in open(f"{arm}/candidates.jsonl"):
            r = json.loads(l)
            comps.setdefault((arm, r["dir"], r["qid"]), []).append(r)

    iso, non = [], []
    for cands in comps.values():
        for a, b in itertools.combinations(cands, 2):
            pa, pb = P.get(canon(a["smiles"])), P.get(canon(b["smiles"]))
            ma, mb = Chem.MolFromSmiles(a["smiles"]), Chem.MolFromSmiles(b["smiles"])
            if not pa or not pb or ma is None or mb is None:
                continue
            same = (rdMolDescriptors.CalcMolFormula(ma)
                    == rdMolDescriptors.CalcMolFormula(mb))
            (iso if same else non).append(chamfer(pa, pb))

    print("Chamfer between the PREDICTED spectra of two candidates for one target")
    print(f"(the predictor's own error is ~{PREDICTOR_ERROR_PPM:.0f} ppm)\n")
    for name, v in (("isomeric pairs (regioisomer-like)", iso),
                    ("non-isomeric pairs", non)):
        if not v:
            print(f"  {name}: none"); continue
        v = sorted(v)
        below = 100 * sum(1 for x in v if x < PREDICTOR_ERROR_PPM) / len(v)
        print(f"  {name:<38} n={len(v):>4}  median {v[len(v)//2]:5.2f} ppm   "
              f"within predictor error: {below:4.1f}%")
    if iso:
        v = sorted(iso)
        print(f"\n  isomeric quartiles: q1 {v[len(v)//4]:.2f}  median "
              f"{v[len(v)//2]:.2f}  q3 {v[3*len(v)//4]:.2f} ppm")
    print("\nReading: candidates for the same target are usually predicted to lie closer\n"
          "together than the predictor's own accuracy. Verification still works (§5.2),\n"
          "but on a thin margin — which is the quantitative root of the precision fall in\n"
          "§5.3, the high derangement floor in §5.5, and the ceiling named in §5.4.")


if __name__ == "__main__":
    main()
