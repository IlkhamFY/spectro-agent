"""
Normalisation to the *exact* Spectro input format + structure resolution.

The Spectro paper (chemrxiv-2024-37v2j) feeds the model NMR strings shaped like::

    13C NMR: δ 73.9 (1C, s), 94.8 (1C, s), 126.5 (2C, s), ...
    1H  NMR: δ 5.47 (1H, s), 7.29-7.51 (5H, m), ...

i.e. ``shift (count<nucleus>, multiplicity)`` -- note the integration comes
*first*, the multiplicity second. Journals report the reverse order
(``7.85 (d, J = 8.0 Hz, 2H)``). :func:`to_spectro_h` / :func:`to_spectro_c`
rewrite an extracted record into the canonical Spectro ordering so the harvest
drops straight into their training pipeline.

Structure resolution (optional, best-effort, all dependencies degrade
gracefully if missing):

    IUPAC name --OPSIN--> SMILES --RDKit--> InChIKey (dedup)
                                 --SELFIES--> Spectro decoder target
"""

from __future__ import annotations

from .extract import CompoundRecord, Peak

# Optional chemistry stack -- import lazily / defensively.
try:
    from rdkit import Chem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    _HAVE_RDKIT = True
except Exception:  # pragma: no cover
    _HAVE_RDKIT = False

try:
    import selfies as _sf
    _HAVE_SELFIES = True
except Exception:  # pragma: no cover
    _HAVE_SELFIES = False

import warnings as _warnings

try:
    from py2opsin import py2opsin
    _HAVE_OPSIN = True
except Exception:  # pragma: no cover
    _HAVE_OPSIN = False


def _fmt_peak_h(p: Peak) -> str:
    n = f"{p.nuclei}H" if p.nuclei else "?H"
    mult = p.multiplicity or "m"
    return f"{p.shift} ({n}, {mult})"


def _fmt_peak_c(p: Peak) -> str:
    # 13C integration (#equivalent carbons) is rarely reported; Spectro uses it
    # but defaults are fine. We emit "1C, s" unless we know better.
    n = f"{p.nuclei}C" if p.nuclei else "1C"
    mult = p.multiplicity or "s"
    return f"{p.shift} ({n}, {mult})"


def to_spectro_h(rec: CompoundRecord) -> str | None:
    if not rec.h_peaks:
        return None
    return "δ " + ", ".join(_fmt_peak_h(p) for p in rec.h_peaks)


def to_spectro_c(rec: CompoundRecord) -> str | None:
    if not rec.c_peaks:
        return None
    return "δ " + ", ".join(_fmt_peak_c(p) for p in rec.c_peaks)


def name_to_smiles(name: str) -> str | None:
    """IUPAC name -> SMILES via OPSIN (offline, no network)."""
    if not (_HAVE_OPSIN and name):
        return None
    name = name.strip().strip(".:;,")
    if len(name) < 4 or len(name) > 200:
        return None
    try:
        with _warnings.catch_warnings():
            _warnings.simplefilter("ignore")
            smi = py2opsin(name)
        return smi or None
    except Exception:
        return None


def canonical_and_keys(smiles: str) -> tuple[str | None, str | None, str | None]:
    """SMILES -> (canonical SMILES, InChIKey, SELFIES)."""
    canon = inchikey = selfies = None
    if _HAVE_RDKIT and smiles:
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                canon = Chem.MolToSmiles(mol)
                inchikey = Chem.MolToInchiKey(mol)
        except Exception:
            pass
    src = canon or smiles
    if _HAVE_SELFIES and src:
        try:
            selfies = _sf.encoder(src)
        except Exception:
            selfies = None
    return canon, inchikey, selfies


def enrich(rec: CompoundRecord) -> CompoundRecord:
    """Fill Spectro-format strings + structure fields on a record in place."""
    rec.spectro_h = to_spectro_h(rec)
    rec.spectro_c = to_spectro_c(rec)

    # Resolve a structure when the label looks like a chemical name.
    candidate = rec.name or rec.label
    smiles = None
    if candidate:
        smiles = name_to_smiles(candidate)
    if smiles:
        canon, inchikey, selfies = canonical_and_keys(smiles)
        rec.smiles = canon or smiles
        rec.inchikey = inchikey
        rec.selfies = selfies
    return rec


def capabilities() -> dict:
    return {"rdkit": _HAVE_RDKIT, "selfies": _HAVE_SELFIES, "opsin": _HAVE_OPSIN}
