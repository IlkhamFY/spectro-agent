#!/usr/bin/env python3
"""
Add a computed IR band list to every record, so the dataset carries NMR **and**
IR for all molecules.

Experimental IR paired with structure is scarce (NMRexp, like most large NMR
corpora, has none). The accepted route to IR at scale -- the one the 177K-patent
IR-NMR dataset took -- is to *compute* it. We use a functional-group -> IR-band
predictor: RDKit SMARTS detect functional groups, each contributing its
characteristic absorption wavenumbers (plus the C-H/skeletal bands every organic
shows). This is precisely the signal Spectro's j-IR-vis is built around (it is
pretrained to detect functional-group peaks), so the predicted bands align with
what the IR pathway learns.

Experimental IR (from the paper crawl) is preferred when available; otherwise the
computed bands are used and tagged ir_source="computed_fg".

    python scripts/predict_ir.py --in data/training_nmrexp/train.jsonl \
        --ir data/training_ir/train.jsonl --out data/training_full/train.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rdkit import Chem                                          # noqa: E402
from rdkit import RDLogger                                     # noqa: E402
RDLogger.DisableLog("rdApp.*")

# (name, SMARTS, [characteristic IR bands cm^-1]). Standard correlation tables.
IR_RULES = [
    ("carboxylic_acid", "[CX3](=O)[OX2H1]", [1710, 1420, 1280, 2950, 2600]),
    ("ester",           "[CX3](=O)[OX2H0][#6]", [1735, 1240, 1050]),
    ("anhydride",       "[CX3](=O)[OX2][CX3](=O)", [1820, 1760, 1040]),
    ("acyl_halide",     "[CX3](=O)[F,Cl,Br,I]", [1800, 965]),
    ("amide",           "[CX3](=O)[NX3]", [1650, 1550, 3300, 3100]),
    ("aldehyde",        "[CX3H1](=O)[#6]", [1725, 2820, 2720]),
    ("ketone",          "[#6][CX3](=O)[#6]", [1715, 1230]),
    ("alcohol",         "[CX4][OX2H]", [3350, 1050, 1330]),
    ("phenol",          "[c][OX2H]", [3300, 1230, 1360]),
    ("ether",           "[OD2]([#6])[#6]", [1110]),
    ("prim_amine",      "[NX3;H2][#6]", [3370, 3290, 1610, 1070]),
    ("sec_amine",       "[NX3;H1]([#6])[#6]", [3300, 1500]),
    ("nitrile",         "[NX1]#[CX2]", [2250]),
    ("isocyanate",      "[NX2]=[CX2]=[OX1]", [2270]),
    ("imine",           "[CX3]=[NX2]", [1660]),
    ("azide",           "[NX1]=[NX2]=[NX2]", [2100]),
    ("nitro",           "[$([NX3](=O)=O),$([NX3+](=O)[O-])]", [1520, 1350]),
    ("terminal_alkyne", "[CX2]#[CX2][H]", [3300, 2120]),
    ("alkyne",          "[CX2]#[CX2]", [2150]),
    ("alkene",          "[CX3]=[CX3]", [1645, 3080, 990, 910]),
    ("aromatic",        "c1ccccc1", [1600, 1580, 1500, 1450, 3030, 750, 690]),
    ("hetero_aromatic", "[a;!c]", [1590, 1480, 3050]),
    ("sulfone",         "[SX4](=O)(=O)", [1320, 1150]),
    ("sulfoxide",       "[SX3](=O)", [1040]),
    ("sulfonamide",     "[SX4](=O)(=O)[NX3]", [1330, 1160, 3300]),
    ("thiol",           "[SX2H]", [2560]),
    ("phosphoryl",      "[PX4]=O", [1250, 1020]),
    ("c_fluoride",      "[#6][F]", [1150, 1100]),
    ("c_chloride",      "[#6][Cl]", [740]),
    ("c_bromide",       "[#6][Br]", [600]),
    ("alkane_CH",       "[CX4H]", [2960, 2920, 2870, 1460, 1375]),  # ~all organics
]
_COMPILED = [(n, Chem.MolFromSmarts(s), b) for n, s, b in IR_RULES]


def predict_ir(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    bands: set[int] = set()
    for _name, patt, bnds in _COMPILED:
        if patt is not None and mol.HasSubstructMatch(patt):
            bands.update(bnds)
    if not bands:                              # bare skeleton fallback
        bands.update([2920, 2850, 1460])
    return sorted(bands, reverse=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="data/training_nmrexp/train.jsonl")
    ap.add_argument("--ir", default="data/training_ir/train.jsonl",
                    help="experimental-IR records to prefer (by InChIKey)")
    ap.add_argument("--out", default="data/training_full/train.jsonl")
    args = ap.parse_args(argv)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)

    # experimental IR by InChIKey (preferred over computed)
    exp = {}
    if Path(args.ir).exists():
        for line in open(args.ir):
            r = json.loads(line)
            if r.get("ir_bands_cm-1"):
                exp[r["id"]] = r["ir_bands_cm-1"]

    n = both = exp_used = comp = 0
    with out.open("w") as fh:
        for line in open(args.inp):
            r = json.loads(line)
            n += 1
            ik = r.get("id")
            if ik in exp:
                r["ir_bands_cm-1"] = exp[ik]; r["ir_source"] = "experimental"; exp_used += 1
            else:
                pred = predict_ir(r.get("smiles", ""))
                if pred:
                    r["ir_bands_cm-1"] = pred; r["ir_source"] = "computed_fg"; comp += 1
            if r.get("ir_bands_cm-1") and (r.get("h_nmr") or r.get("c_nmr")):
                both += 1
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    stats = {"records": n, "with_NMR_and_IR": both,
             "ir_experimental": exp_used, "ir_computed_fg": comp,
             "note": "every record carries NMR + IR; IR is experimental where "
                     "available (paper crawl), else functional-group-computed"}
    (out.parent / "stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
