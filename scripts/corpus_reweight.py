#!/usr/bin/env python3
"""What the headline accuracy would be on the corpus, not on the benchmark.

IRSpectra-Bench is stratified 50/50 by design: `benchmark_v2.sample2` fills each
difficulty stratum to `n//2`, so "98 simple / 96 complex" is a property of the sampler,
not an observation about chemistry in the literature. The eligible corpus is nothing like
balanced -- it is mostly complex -- and complex compounds are where the model fails.

That makes 28.4% a per-stratum-weighted average with weights the authors chose. It is the
right number for measuring the difficulty gradient, and the wrong number to quote as "how
often does this work on a paper you pick up". Both belong in the paper, which is why this
script computes the second one.

Reweighting uses the paper's own per-stratum accuracies and the corpus stratum
frequencies, under the same eligibility filters the sampler applies -- parsed SMILES,
IR + 1H + 13C all present, 8-60 heavy atoms, at least three multiplets in each NMR
string. The one sampler filter it cannot apply is `raw_1h_for`, which needs a network
fetch per record; that filter is orthogonal to difficulty, and the ESI records it as an
assumption rather than a proof.

  python scripts/corpus_reweight.py
"""
import gzip
import json

from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

GOLD = "data/irexp_resolved/irexp_resolved.jsonl.gz"

# Per-stratum top-1 and recall from the released scorer, as reported in the paper.
ACC = {"simple": (47 / 98, 53 / 98), "complex": (8 / 96, 12 / 96)}


def difficulty(mol) -> str:
    """Verbatim from benchmark_v2.difficulty -- duplicated rather than imported because
    importing that module pulls in the scraper stack, which needs network libraries this
    analysis does not."""
    ri = mol.GetRingInfo()
    nrings = ri.NumRings()
    hac = mol.GetNumHeavyAtoms()
    fused = any(ri.NumAtomRings(a.GetIdx()) >= 2 for a in mol.GetAtoms())
    spiro = rdMolDescriptors.CalcNumSpiroAtoms(mol) > 0
    bridge = rdMolDescriptors.CalcNumBridgeheadAtoms(mol) > 0
    if spiro or bridge or nrings >= 3 or fused or hac > 24:
        return "complex"
    if nrings <= 2 and hac <= 22:
        return "simple"
    return "complex"


def main():
    counts = {"simple": 0, "complex": 0}
    hac = []
    for line in gzip.open(GOLD, "rt"):
        r = json.loads(line)
        smi = r.get("smiles")
        if not (smi and r.get("h_nmr") and r.get("c_nmr") and r.get("ir_bands_cm-1")):
            continue
        m = Chem.MolFromSmiles(smi)
        if m is None or not (8 <= m.GetNumHeavyAtoms() <= 60):
            continue
        if r["h_nmr"].count("(") < 3 or r["c_nmr"].count("(") < 3:
            continue
        counts[difficulty(m)] += 1
        hac.append(m.GetNumHeavyAtoms())

    n = sum(counts.values())
    w = counts["simple"] / n
    hac.sort()
    print(f"eligible corpus            n = {n}")
    print(f"  simple                   {counts['simple']:6d}  ({100 * w:.1f}%)")
    print(f"  complex                  {counts['complex']:6d}  ({100 * (1 - w):.1f}%)")
    print(f"  median heavy atoms       {hac[len(hac) // 2]}")
    print()
    print(f"benchmark                  n = 194   simple 98 (50.5%)   median 20")
    print(f"  simple enriched          {w and (98 / 194) / w:.1f}x over the corpus")
    print()
    for i, name in enumerate(("top-1", "recall (top-3)")):
        bench = (98 * ACC["simple"][i] + 96 * ACC["complex"][i]) / 194
        corpus = w * ACC["simple"][i] + (1 - w) * ACC["complex"][i]
        print(f"{name:16s} benchmark {100 * bench:5.1f}%     "
              f"corpus-reweighted {100 * corpus:5.1f}%")


if __name__ == "__main__":
    main()
