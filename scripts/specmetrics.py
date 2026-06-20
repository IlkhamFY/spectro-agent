#!/usr/bin/env python3
"""Shared spectral-metric and matching primitives — the single source of truth for
the symmetric 13C chamfer distance and the InChIKey-connectivity match used by every
scorer/diagnostic. (Consolidates copies previously duplicated across scripts.)"""
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

def chamfer(pred, obs):
    """Symmetric chamfer distance between predicted and observed 13C shift lists."""
    if not pred or not obs:
        return 999.0
    a = sum(min(abs(x - y) for y in obs) for x in pred) / len(pred)
    b = sum(min(abs(y - x) for x in pred) for y in obs) / len(obs)
    return (a + b) / 2

def ik14(smiles):
    """InChIKey connectivity block (first 14 chars) or None if unparseable."""
    m = Chem.MolFromSmiles(smiles) if smiles else None
    return Chem.MolToInchiKey(m)[:14] if m else None
