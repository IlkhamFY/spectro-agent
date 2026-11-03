"""Structure features. Prediction-versus-truth only. Not a training-set comparison."""
from __future__ import annotations

from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs, rdFMCS, rdMolDescriptors
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

# Presence classes. A molecule can sit in more than one.
FG_SMARTS = [
    ("carboxylic acid", "[CX3](=O)[OX2H1]"),
    ("ester", "[#6][CX3](=O)[OX2H0][#6]"),
    ("amide", "[NX3][CX3](=O)[#6]"),
    ("aldehyde", "[CX3H1](=O)[#6]"),
    ("ketone", "[#6][CX3](=O)[#6]"),
    ("nitrile", "[CX2]#[NX1]"),
    ("nitro", "[$([NX3](=O)=O),$([NX3+](=O)[O-])]"),
    ("phenol", "[OX2H][c]"),
    ("alcohol", "[OX2H][CX4]"),
    ("amine", "[NX3;H2,H1;!$(NC=O)]"),
    ("aryl halide", "[c][F,Cl,Br,I]"),
    ("ether", "[#6;!$(C=O)][OD2][#6;!$(C=O)]"),
    ("heteroaromatic", "[a;!#6]"),
]
_FG = [(name, Chem.MolFromSmarts(s)) for name, s in FG_SMARTS]


def mol(smi):
    if not smi or not isinstance(smi, str):
        return None
    return Chem.MolFromSmiles(smi)


def ik14(smi):
    m = mol(smi)
    if m is None:
        return None
    return Chem.MolToInchiKey(m)[:14]


def formula_of(smi):
    m = mol(smi)
    if m is None:
        return None
    return rdMolDescriptors.CalcMolFormula(m)


def hac_bin(h):
    h = int(h)
    if h <= 15:
        return "<=15"
    if h <= 20:
        return "16-20"
    if h <= 25:
        return "21-25"
    if h <= 30:
        return "26-30"
    return ">30"


HAC_ORDER = ["<=15", "16-20", "21-25", "26-30", ">30"]


def ring_class(m):
    ri = m.GetRingInfo()
    n = ri.NumRings()
    aromatic = any(a.GetIsAromatic() for a in m.GetAtoms())
    if n == 0:
        return "acyclic"
    if n == 1:
        return "single aromatic ring" if aromatic else "single aliphatic ring"
    return "polycyclic aromatic" if aromatic else "polycyclic aliphatic"


RING_ORDER = [
    "acyclic",
    "single aliphatic ring",
    "single aromatic ring",
    "polycyclic aliphatic",
    "polycyclic aromatic",
]


def functional_groups(m):
    hit = []
    for name, q in _FG:
        if q is not None and m.HasSubstructMatch(q):
            hit.append(name)
    return hit


def morgan(smi):
    m = mol(smi)
    if m is None:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)


def tanimoto(smi_a, smi_b):
    fa, fb = morgan(smi_a), morgan(smi_b)
    if fa is None or fb is None:
        return None
    return float(DataStructs.TanimotoSimilarity(fa, fb))


def mces(smi_a, smi_b, timeout=2):
    """Bond-MCS size. Similarity is MCS bonds / max(bonds). Distance is the symmetric difference."""
    a, b = mol(smi_a), mol(smi_b)
    if a is None or b is None:
        return None
    res = rdFMCS.FindMCS(
        [a, b],
        timeout=timeout,
        ringMatchesRingOnly=True,
        atomCompare=rdFMCS.AtomCompare.CompareElements,
        bondCompare=rdFMCS.BondCompare.CompareOrder,
        completeRingsOnly=False,
    )
    if res.canceled or res.numBonds < 0:
        return None
    na, nb = a.GetNumBonds(), b.GetNumBonds()
    k = int(res.numBonds)
    denom = max(na, nb)
    sim = (k / denom) if denom else None
    dist = na + nb - 2 * k
    return {"bonds": k, "sim": sim, "dist": dist}


def changed_atoms(truth_smi, pred_smi):
    """Atom indices in the prediction that the MCS does not cover. Empty if the match fails."""
    a, b = mol(truth_smi), mol(pred_smi)
    if a is None or b is None:
        return []
    res = rdFMCS.FindMCS(
        [a, b],
        timeout=2,
        ringMatchesRingOnly=True,
        atomCompare=rdFMCS.AtomCompare.CompareElements,
        bondCompare=rdFMCS.BondCompare.CompareOrder,
    )
    if res.canceled or not res.smartsString:
        return []
    q = Chem.MolFromSmarts(res.smartsString)
    if q is None:
        return []
    hit = b.GetSubstructMatch(q)
    if not hit:
        return []
    covered = set(hit)
    return [i for i in range(b.GetNumAtoms()) if i not in covered]


def score_cands(truth_ik, cands):
    flags = []
    for smi in (cands or [])[:3]:
        flags.append(ik14(smi) == truth_ik and truth_ik is not None)
    top1 = bool(flags) and flags[0]
    rec = any(flags)
    return top1, rec
