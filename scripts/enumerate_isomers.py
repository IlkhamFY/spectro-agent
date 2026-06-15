#!/usr/bin/env python3
"""Scaffold-constrained regioisomer enumeration.

The model is scaffold-accurate but mis-places substituents (regiochemistry). Given a
model candidate, enumerate same-formula constitutional isomers by relocating each
pendant substituent to every aromatic C-H on its ring system (covers ortho/meta/para
and heteroaromatic position isomerism, e.g. picolinamide <-> nicotinamide), plus
pairwise swaps of two distinct substituents. Pure RDKit, deterministic.
"""
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

def _canon(m):
    try:
        s = Chem.MolToSmiles(m)
        mm = Chem.MolFromSmiles(s)
        return Chem.MolToSmiles(mm) if mm else None
    except Exception:
        return None

def _pendant_bonds(mol):
    """bonds (ringAromAtom -> substituentAtom) that are single, not in a ring."""
    out = []
    for b in mol.GetBonds():
        if b.IsInRing() or b.GetBondType() != Chem.BondType.SINGLE:
            continue
        a1, a2 = b.GetBeginAtom(), b.GetEndAtom()
        for ring_at, sub_at in ((a1, a2), (a2, a1)):
            if ring_at.GetIsAromatic() and ring_at.IsInRing() and not sub_at.IsInRing():
                out.append((ring_at.GetIdx(), sub_at.GetIdx()))
    return out

def _arom_ch(mol):
    """aromatic carbons bearing at least one H (available substitution sites)."""
    return [a.GetIdx() for a in mol.GetAtoms()
            if a.GetIsAromatic() and a.GetSymbol() == "C" and a.GetTotalNumHs() > 0]

def _heteroatom_walk(mol, base, f0, out, cap):
    """Swap a ring heteroatom (N/O/S) with an aromatic C-H in the same ring -> ring
    position isomers (e.g. pyridine 2- vs 3-). Element-swap keeps the formula."""
    ri = mol.GetRingInfo()
    het = [a.GetIdx() for a in mol.GetAtoms()
           if a.GetIsAromatic() and a.GetSymbol() in ("N", "O", "S") and a.IsInRing()]
    ch = _arom_ch(mol)
    for h in het:
        for c in ch:
            # only within a shared aromatic ring
            if not any(h in r and c in r for r in ri.AtomRings()):
                continue
            rw = Chem.RWMol(mol)
            hz, cz = rw.GetAtomWithIdx(h), rw.GetAtomWithIdx(c)
            sym_h = hz.GetSymbol()
            hz.SetAtomicNum(6); hz.SetNumExplicitHs(0); hz.SetNoImplicit(False)
            cz.SetAtomicNum({"N": 7, "O": 8, "S": 16}[sym_h])
            cz.SetNumExplicitHs(0); cz.SetNoImplicit(False)
            m = rw.GetMol()
            try:
                Chem.SanitizeMol(m); s = _canon(m)
            except Exception:
                s = None
            if s and s != base:
                out.add(s)
            if len(out) >= cap:
                return

def _move(mol, ring_idx, sub_idx, tgt_idx):
    rw = Chem.RWMol(mol)
    rw.RemoveBond(ring_idx, sub_idx)
    rw.AddBond(tgt_idx, sub_idx, Chem.BondType.SINGLE)
    m = rw.GetMol()
    try:
        Chem.SanitizeMol(m)
    except Exception:
        return None
    return _canon(m)

def enumerate_regioisomers(smiles, cap=300):
    """Return a set of canonical same-formula regioisomer SMILES (excludes input)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return set()
    f0 = rdMolDescriptors.CalcMolFormula(mol)
    base = _canon(mol)
    out = set()
    pend = _pendant_bonds(mol)
    sites = _arom_ch(mol)
    # single-substituent relocation
    for ring_idx, sub_idx in pend:
        for tgt in sites:
            if tgt == ring_idx:
                continue
            s = _move(mol, ring_idx, sub_idx, tgt)
            if s and s != base:
                out.add(s)
            if len(out) >= cap:
                return out
    # pairwise swap of two distinct pendant substituents
    for i in range(len(pend)):
        for j in range(i + 1, len(pend)):
            (r1, s1), (r2, s2) = pend[i], pend[j]
            if len({r1, s1, r2, s2}) < 4:
                continue
            rw = Chem.RWMol(mol)
            rw.RemoveBond(r1, s1); rw.RemoveBond(r2, s2)
            rw.AddBond(r1, s2, Chem.BondType.SINGLE)
            rw.AddBond(r2, s1, Chem.BondType.SINGLE)
            m = rw.GetMol()
            try:
                Chem.SanitizeMol(m); s = _canon(m)
            except Exception:
                s = None
            if s and s != base:
                out.add(s)
            if len(out) >= cap:
                return out
    # ring heteroatom position isomers
    _heteroatom_walk(mol, base, f0, out, cap)
    # keep only valid same-formula isomers
    return {s for s in out
            if (mm := Chem.MolFromSmiles(s)) and rdMolDescriptors.CalcMolFormula(mm) == f0}

if __name__ == "__main__":
    # self-test: picolinamide should yield the nicotinamide regioisomer
    pico = "CC(C)(C)NC(=O)c1ccccn1"
    nico = Chem.MolToSmiles(Chem.MolFromSmiles("CC(C)(C)NC(=O)c1cccnc1"))
    iso = enumerate_regioisomers(pico)
    print(f"picolinamide -> {len(iso)} regioisomers; nicotinamide recovered: {nico in iso}")
    for s in sorted(iso): print("  ", s)
