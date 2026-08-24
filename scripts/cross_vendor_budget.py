#!/usr/bin/env python3
"""Cross-vendor recall at a matched candidate budget.

Recall in [@tab:cross-vendor-decomposition-60] is "is the true structure anywhere in the
model's candidate list", and the lists are not the same length. Claude returns 2.20
candidates per compound over this arm; every comparison model returns exactly 3.00
(Composer 2.82). A longer list can only help recall, so the comparison is tilted -- and
it is tilted in the direction that flatters the competitors, which is the direction a
paper is least likely to notice.

The paper already corrects the *other* half of the same asymmetry: Claude's singletons
inflate its verification precision, and the multi-candidate column exists to undo that.
This script supplies the missing half, by reporting recall at k=1, 2 and 3 so a reader can
compare at a budget every model actually met.

  python scripts/cross_vendor_budget.py
"""
import glob
import json
import os

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

KEY = "data/cross_vendor/key.json"
CLAUDE = (("data/benchmark_v3", "benchmark_v3"),
          ("data/benchmark_v2_ctrl", "benchmark_v2_ctrl"))


def ik14(smiles):
    m = Chem.MolFromSmiles(smiles)
    return Chem.MolToInchiKey(m)[:14] if m else None


def recall_at_k(cands_by_id, truth):
    hits, n, total = [0, 0, 0], 0, 0
    for mid, cands in cands_by_id.items():
        if mid not in truth or not isinstance(cands, list):
            continue
        n += 1
        total += len(cands)
        got = [ik14(c) for c in cands]
        for k in range(3):
            if truth[mid] in got[:k + 1]:
                hits[k] += 1
    return n, hits, (total / n if n else 0)


def main():
    key = json.load(open(KEY))["key"]
    truth = {mid: v["true_ik"] for mid, v in key.items()}
    src2mid = {v["src"]: mid for mid, v in key.items()}

    rows = []
    # ours, assembled from the two rounds the 60-compound arm is drawn from
    ours = {}
    for path, prefix in CLAUDE:
        for line in open(f"{path}/predictions2.jsonl"):
            r = json.loads(line)
            for k in ("candidates", "smiles", "preds", "answers"):
                if isinstance(r.get(k), list):
                    mid = src2mid.get(f"{prefix}:{r['qid']}")
                    if mid:
                        ours[mid] = r[k]
                    break
    rows.append(("Claude Opus (ours)", *recall_at_k(ours, truth)))

    for f in sorted(glob.glob("data/cross_vendor/solve_*.json")):
        d = json.load(open(f))
        if not isinstance(d, dict):
            continue
        n, hits, mean = recall_at_k(d, truth)
        if n:
            rows.append((os.path.basename(f)[6:-5], n, hits, mean))

    print(f"{'model':22s} {'n':>3s} {'r@1':>7s} {'r@2':>7s} {'r@3':>7s}   candidates")
    for name, n, hits, mean in rows:
        print(f"{name:22s} {n:3d} "
              + " ".join(f"{100 * h / n:6.1f}%" for h in hits)
              + f"   {mean:.2f}")
    print("\nr@3 is the paper's headline recall; r@1 is the only budget every model met.")


if __name__ == "__main__":
    main()
