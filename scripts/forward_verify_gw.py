#!/usr/bin/env python3
"""
Close the §5.3 prediction-coverage gap.

The generate-wide arm proposed 217 distinct NEW candidates, but only 65 of them were
forward-predicted in the original run; an unpredicted candidate gets an infinite match
distance and can never be selected, so the reported top-1 was an explicit LOWER BOUND.
This preps the remaining candidates for the same blind forward predictor, so §5.3 can
report a measured number instead of a bound.

Protocol is identical to scripts/forward_verify.py: canonicalise, pool, shuffle,
anonymise, batch. The predictor sees the SMILES alone -- no observed spectrum, no
compound identity.

  prep : write data/fverify_gw/anon_map.json + gbatch_*.txt for the missing candidates
  gap  : report how many wide candidates still lack a forward prediction
"""
import json, glob, os, random, sys
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

OUT   = "data/fverify_gw"
BATCH = 17


def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None


def _preds(rawglob, mapfile):
    amap = json.load(open(mapfile))
    pred = {}
    for f in glob.glob(rawglob):
        pred.update(json.load(open(f)))
    return {canon(s): pred[a] for s, a in amap.items() if a in pred and canon(s)}


def predicted():
    """Every SMILES that already has a forward-predicted 13C spectrum."""
    p = _preds("data/fverify/raw/*.json", "data/fverify/anon_map.json")
    p.update(_preds("data/fverify2/raw/*.json", "data/fverify2/anon_map2.json"))
    if os.path.exists(f"{OUT}/anon_map.json"):
        p.update(_preds(f"{OUT}/raw/*.json", f"{OUT}/anon_map.json"))
    return p


def wide_new():
    """Distinct generate-wide proposals that are NOT in the original candidate pool."""
    orig = {canon(json.loads(l)["smiles"]) for l in open("data/fverify/candidates.jsonl")}
    wide = set()
    for f in glob.glob("data/gw/raw/*.json"):
        for _, v in json.load(open(f)).items():
            for s in v:
                c = canon(s)
                if c:
                    wide.add(c)
    return wide - orig, wide


def gap():
    new, wide = wide_new()
    have = predicted()
    miss = sorted(s for s in new if s not in have)
    print(f"distinct wide proposals: {len(wide)}   new (beyond the original pool): {len(new)}")
    print(f"already forward-predicted: {len(new)-len(miss)}   still missing: {len(miss)}")
    return miss


def prep():
    os.makedirs(f"{OUT}/raw", exist_ok=True)
    miss = gap()
    if not miss:
        print("nothing to do -- coverage is complete")
        return
    random.seed(23); random.shuffle(miss)
    amap = {s: f"W{i:03d}" for i, s in enumerate(miss)}
    json.dump(amap, open(f"{OUT}/anon_map.json", "w"))
    for bi in range((len(miss) + BATCH - 1) // BATCH):
        chunk = miss[bi * BATCH:(bi + 1) * BATCH]
        open(f"{OUT}/gbatch_{bi+1}.txt", "w").write(
            "\n".join(f"{amap[s]}  {s}" for s in chunk) + "\n")
    print(f"wrote {bi+1} batch files to {OUT}/gbatch_*.txt")


if __name__ == "__main__":
    prep() if sys.argv[1] == "prep" else gap()
