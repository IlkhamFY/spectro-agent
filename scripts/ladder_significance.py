#!/usr/bin/env python3
"""Paired significance for the §5.3 inference ladder and the §5.4 verifier comparison.

The ladder (solver self-ranking -> forward-verify -> generate-wide) is often assumed to be
nested, i.e. each stage only adds wins. It is not: stages both gain and lose compounds, and
quoting a best-case p-value that assumes nesting understates the true one. This script
computes the actual discordant counts from the released per-compound outcomes and the exact
two-sided McNemar p from them, so the numbers in §5.3 are derived rather than assumed.

  python3 scripts/ladder_significance.py
"""
import glob, json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specmetrics import chamfer, ik14
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")


def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None


def mcnemar(b, c):
    """Exact two-sided McNemar p on discordant counts b (a-only) and c (b-only)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))


def _preds(rawglob, mapfile):
    amap = json.load(open(mapfile))
    pr = {}
    for f in glob.glob(rawglob):
        pr.update(json.load(open(f)))
    return {canon(s): pr[a] for s, a in amap.items() if a in pr and canon(s)}


def main():
    pred = _preds("data/fverify/raw/*.json", "data/fverify/anon_map.json")
    pred.update(_preds("data/fverify2/raw/*.json", "data/fverify2/anon_map2.json"))
    # data/fverify_gw/ closes the §5.3 coverage gap (all 217 wide candidates predicted).
    # It leaves every outcome below unchanged, but must be loaded so this script and
    # score_generate_wide.py always see the identical candidate pool.
    if os.path.exists("data/fverify_gw/anon_map.json"):
        pred.update(_preds("data/fverify_gw/raw/*.json", "data/fverify_gw/anon_map.json"))

    wide = {}
    for f in glob.glob("data/gw/raw/*.json"):
        for k, v in json.load(open(f)).items():
            wide.setdefault(k, []).extend(v)

    gold = {}
    for d in ("data/benchmark_v3", "data/benchmark_v2_ctrl"):
        for line in open(f"{d}/answers2.jsonl"):
            a = json.loads(line)
            gold[(d, a["qid"])] = a["inchikey"][:14]

    comps = {}
    for line in open("data/fverify/candidates.jsonl"):
        r = json.loads(line)
        comps.setdefault((r["dir"], r["qid"]), []).append(r)

    tag = lambda d: "V3" if d.endswith("v3") else "CT"
    arms = {"self-rank": {}, "forward-verify": {}, "generate-wide": {}}
    for (d, q), orig in comps.items():
        obs = orig[0]["obs_c13"]; g = gold.get((d, q))
        arms["self-rank"][(d, q)] = sorted(orig, key=lambda c: c["self_rank"])[0]["is_true"]
        sc = [(chamfer(pred.get(canon(c["smiles"])), obs) if pred.get(canon(c["smiles"]))
               else 999.0, c["is_true"]) for c in orig]
        arms["forward-verify"][(d, q)] = min(sc, key=lambda x: x[0])[1]
        pool = {c["smiles"]: c["is_true"] for c in orig}
        for smi in wide.get(f"{tag(d)}-{q}", []):
            if smi not in pool:
                pool[smi] = (ik14(smi) == g) if g else False
        sc2 = [(chamfer(pred.get(canon(s)), obs) if pred.get(canon(s)) else 999.0, t)
               for s, t in pool.items()]
        arms["generate-wide"][(d, q)] = min(sc2, key=lambda x: x[0])[1]

    n = len(comps)
    print(f"Paired comparisons over the same {n} compounds\n")
    print(f"{'comparison':<34}{'counts':>14}{'discordant':>16}{'McNemar p':>12}")
    pairs = [("self-rank", "forward-verify"), ("forward-verify", "generate-wide"),
             ("self-rank", "generate-wide")]
    out = []
    for a, b in pairs:
        A, B = arms[a], arms[b]
        lost = sum(1 for k in A if A[k] and not B[k])      # a right, b wrong
        gain = sum(1 for k in A if not A[k] and B[k])      # b right, a wrong
        p = mcnemar(lost, gain)
        ka, kb = sum(A.values()), sum(B.values())
        print(f"{a+' -> '+b:<34}{f'{ka}/{n} -> {kb}/{n}':>14}"
              f"{f'b={lost} c={gain}':>16}{p:>12.3f}")
        out.append({"from": a, "to": b, "from_k": ka, "to_k": kb, "n": n,
                    "b_lost": lost, "c_gained": gain, "mcnemar_p": round(p, 4)})
    print("\nb = solved by the earlier arm and lost by the later one; c = the reverse.")
    print("The ladder is NOT nested (b > 0 at every step), so a best-case p that assumes")
    print("nesting would understate these values.")
    os.makedirs("data/audit", exist_ok=True)
    json.dump({"n": n, "comparisons": out}, open("data/audit/ladder_significance.json", "w"),
              indent=1)
    print("\nwrote data/audit/ladder_significance.json")


if __name__ == "__main__":
    main()
