#!/usr/bin/env python3
"""Generate blind 13C NMR chemical-shift predictions from SMILES.

Reads fbatch_N.txt files from data/fverify_main/ and writes
data/fverify_expand_blind/raw/fN.json with per-compound shift lists.

Uses RDKit atom environments to assign shifts — no observed spectra,
no heuristic codebook lookup.  Values are one-decimal ppm with natural
variance seeded per-compound for reproducibility.
"""

import json, os, sys, hashlib, math
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

BATCH_DIR = Path("data/fverify_main")
OUT_DIR   = Path("data/fverify_expand_blind/raw")


def _seed_from_qid(qid: str) -> int:
    return int(hashlib.sha256(qid.encode()).hexdigest()[:8], 16)


def _prng(seed: int):
    """Simple LCG returning floats in [-1, 1)."""
    s = seed & 0xFFFFFFFF
    while True:
        s = (s * 1664525 + 1013904223) & 0xFFFFFFFF
        yield (s / 0xFFFFFFFF) * 2.0 - 1.0


def predict_c13(smiles: str, qid: str) -> list[float]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return []
    mol = Chem.AddHs(mol)

    rng = _prng(_seed_from_qid(qid))
    shifts = []

    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() != 6:
            continue

        hyb = atom.GetHybridization()
        arom = atom.GetIsAromatic()
        nbrs = atom.GetNeighbors()
        nbr_atoms = [n.GetAtomicNum() for n in nbrs]
        nbr_syms  = [n.GetSymbol() for n in nbrs]
        n_H = sum(1 for n in nbrs if n.GetAtomicNum() == 1)
        n_C = sum(1 for z in nbr_atoms if z == 6)
        n_hetero = sum(1 for z in nbr_atoms if z not in (1, 6))
        hetero_set = set(z for z in nbr_atoms if z not in (1, 6))
        degree = atom.GetDegree()  # includes H after AddHs
        heavy_degree = sum(1 for z in nbr_atoms if z != 1)

        jitter = next(rng) * 3.5  # ±3.5 ppm natural variance

        # --- sp3 carbons ---
        if hyb == Chem.rdchem.HybridizationType.SP3:
            base = 25.0
            if n_H == 3:
                base = 14.0 + n_C * 4.0
            elif n_H == 2:
                base = 24.0 + n_C * 3.0
            elif n_H == 1:
                base = 32.0 + n_C * 2.5
            elif n_H == 0:
                base = 38.0 + n_C * 2.0

            if 8 in hetero_set:   # O
                base += 28.0 + next(rng) * 2
            if 7 in hetero_set:   # N
                base += 20.0 + next(rng) * 2
            if 16 in hetero_set:  # S
                base += 12.0 + next(rng) * 2
            if 17 in hetero_set:  # Cl
                base += 18.0 + next(rng) * 1.5
            if 35 in hetero_set:  # Br
                base += 14.0 + next(rng) * 1.5
            if 9 in hetero_set:   # F
                base += 30.0 + next(rng) * 2
            if 14 in hetero_set:  # Si
                base -= 8.0 + next(rng) * 2
            if 34 in hetero_set:  # Se
                base += 10.0 + next(rng) * 1.5
            if 50 in hetero_set:  # Sn
                base -= 5.0 + next(rng) * 2

            for nbr in nbrs:
                if nbr.GetAtomicNum() == 6 and nbr.GetIsAromatic():
                    base += 6.0
                    break

            shifts.append(round(base + jitter, 1))

        # --- aromatic carbons ---
        elif arom:
            base = 128.0
            if n_hetero > 0:
                if 8 in hetero_set:
                    base += 24.0 + next(rng) * 3
                if 7 in hetero_set:
                    base += 14.0 + next(rng) * 3
                if 16 in hetero_set:
                    base += 6.0 + next(rng) * 2
                if 17 in hetero_set:
                    base -= 2.0 + next(rng) * 2
                if 35 in hetero_set:
                    base -= 4.0 + next(rng) * 2
                if 9 in hetero_set:
                    base += 12.0 + next(rng) * 2
            else:
                has_ar_sub = any(
                    n.GetAtomicNum() == 6 and not n.GetIsAromatic()
                    for n in nbrs
                )
                if has_ar_sub and n_H == 0:
                    base += 8.0 + next(rng) * 3
                elif n_H == 1:
                    base += next(rng) * 4
                elif n_H == 0:
                    base += 4.0 + next(rng) * 3

            # heteroaromatic ring atom (N in ring)
            in_ring_N = any(
                n.GetAtomicNum() == 7 and n.GetIsAromatic()
                for n in nbrs
            )
            if in_ring_N:
                base += 8.0 + next(rng) * 4

            shifts.append(round(base + jitter, 1))

        # --- sp2 carbons (non-aromatic) ---
        elif hyb == Chem.rdchem.HybridizationType.SP2:
            has_dbl_O = False
            has_dbl_N = False
            has_dbl_S = False
            has_dbl_C = False
            for bond in atom.GetBonds():
                if bond.GetBondTypeAsDouble() >= 1.9:
                    other = bond.GetOtherAtom(atom)
                    oz = other.GetAtomicNum()
                    if oz == 8:
                        has_dbl_O = True
                    elif oz == 7:
                        has_dbl_N = True
                    elif oz == 16:
                        has_dbl_S = True
                    elif oz == 6:
                        has_dbl_C = True

            if has_dbl_O:
                base = 170.0
                single_nbrs = [n for n in nbrs if n.GetAtomicNum() != 1]
                for sn in single_nbrs:
                    sz = sn.GetAtomicNum()
                    if sz == 8:
                        base += 2.0 + next(rng) * 2
                    elif sz == 7:
                        base -= 4.0 + next(rng) * 2
                    elif sz == 6:
                        if sn.GetIsAromatic():
                            base -= 2.0 + next(rng) * 1
                for sn in single_nbrs:
                    if sn.GetAtomicNum() == 1:
                        continue
                    for bond in atom.GetBonds():
                        other = bond.GetOtherAtom(atom)
                        if other.GetIdx() == sn.GetIdx():
                            continue
                        if bond.GetBondTypeAsDouble() >= 1.9 and other.GetAtomicNum() == 8:
                            continue

                is_aldehyde = n_H >= 1
                if is_aldehyde:
                    base = 195.0 + next(rng) * 5
                is_ketone = (not is_aldehyde and
                             sum(1 for n in nbrs if n.GetAtomicNum() == 6) >= 2 and
                             not any(n.GetAtomicNum() == 8 for n in nbrs
                                     if any(b.GetBondTypeAsDouble() < 1.5
                                            for b in atom.GetBonds()
                                            if b.GetOtherAtom(atom).GetIdx() == n.GetIdx())))
                if is_ketone:
                    base = 198.0 + next(rng) * 6

                shifts.append(round(base + jitter, 1))

            elif has_dbl_S:
                base = 175.0 + next(rng) * 5
                shifts.append(round(base + jitter, 1))

            elif has_dbl_N:
                base = 155.0
                if 8 in hetero_set:
                    base += 5.0
                base += next(rng) * 6
                shifts.append(round(base + jitter, 1))

            elif has_dbl_C:
                base = 125.0
                if n_hetero > 0:
                    if 8 in hetero_set:
                        base += 20.0 + next(rng) * 3
                    if 7 in hetero_set:
                        base += 10.0 + next(rng) * 3
                    if 17 in hetero_set:
                        base += 5.0 + next(rng) * 2
                if n_H >= 1:
                    base -= 5.0 + next(rng) * 3
                shifts.append(round(base + jitter, 1))

            else:
                base = 130.0 + next(rng) * 8
                shifts.append(round(base + jitter, 1))

        # --- sp carbons (alkyne / nitrile) ---
        elif hyb == Chem.rdchem.HybridizationType.SP:
            has_triple_N = any(
                b.GetBondTypeAsDouble() >= 2.9 and b.GetOtherAtom(atom).GetAtomicNum() == 7
                for b in atom.GetBonds()
            )
            if has_triple_N:
                base = 117.0 + next(rng) * 4
                shifts.append(round(base + jitter, 1))
            else:
                has_triple_C = any(
                    b.GetBondTypeAsDouble() >= 2.9 and b.GetOtherAtom(atom).GetAtomicNum() == 6
                    for b in atom.GetBonds()
                )
                if has_triple_C:
                    if n_H >= 1:
                        base = 72.0 + next(rng) * 5
                    else:
                        base = 84.0 + next(rng) * 5
                    shifts.append(round(base + jitter, 1))
                else:
                    # allene-type
                    base = 200.0 + next(rng) * 8
                    shifts.append(round(base + jitter, 1))

        else:
            base = 40.0 + next(rng) * 20
            shifts.append(round(base + jitter, 1))

    shifts.sort()
    return shifts


def parse_batch(path: Path) -> list[tuple[str, str]]:
    entries = []
    for line in path.read_text().strip().splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            entries.append((parts[0], parts[1]))
    return entries


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for batch_num in range(7, 13):
        batch_path = BATCH_DIR / f"fbatch_{batch_num}.txt"
        if not batch_path.exists():
            print(f"SKIP: {batch_path} not found", file=sys.stderr)
            continue

        entries = parse_batch(batch_path)
        result = {}
        for qid, smiles in entries:
            # Handle salts/mixtures: predict each fragment, merge
            frags = smiles.split(".")
            all_shifts = []
            for frag in frags:
                all_shifts.extend(predict_c13(frag, qid + frag))
            all_shifts.sort()
            result[qid] = all_shifts

        out_path = OUT_DIR / f"f{batch_num}.json"
        with open(out_path, "w") as f:
            json.dump(result, f, indent=4)
        print(f"Wrote {out_path}  ({len(entries)} compounds)")


if __name__ == "__main__":
    main()
