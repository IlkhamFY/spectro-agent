"""InChIKey-14 scoring. Rank 1 is top-1. Recall is the key anywhere in the ranked list."""
from __future__ import annotations

import json
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")


def ik14(smiles: str | None) -> str | None:
    if not smiles:
        return None
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToInchiKey(mol)[:14]


def score_ranked(ranked: list[str], gold: str) -> dict:
    seen: list[str] = []
    invalid = 0
    for smiles in ranked:
        key = ik14(smiles)
        if key is None:
            invalid += 1
            continue
        if key not in seen:
            seen.append(key)
    hit_at = seen.index(gold) + 1 if gold in seen else None
    return {
        "top1": hit_at == 1,
        "recall": hit_at is not None,
        "hit_rank": hit_at,
        "n_ranked": len(ranked),
        "n_unique_ik": len(seen),
        "n_invalid": invalid,
    }


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    top1 = sum(1 for r in rows if r["top1"])
    recall = sum(1 for r in rows if r["recall"])
    return {"n": n, "top1": top1, "recall": recall}
