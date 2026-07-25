#!/usr/bin/env python3
"""Limitation fixes (extraction noise + ground-truth integrity): for every
benchmark compound check that the resolved ground-truth structure is
self-consistent with its reported spectrum, and recompute metrics on the
spectrally-clean subset. Pure RDKit, no LLM."""
import json, glob, re, os, sys
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
from rdkit.Chem import rdMolDescriptors

FORCE = "--force" in sys.argv
SHRINK_TOL = 0.10          # refuse to overwrite a committed clean set that shrank by more than this

# SELFIES is a HARD dependency of this audit, not an optional extra: it backs one of the
# four integrity checks. Resolve it once, up front, and die loudly if it is absent --
# importing it per-compound inside a try/except silently marks every ground truth
# "selfies-rt-fail" and then overwrites the committed clean_qids.json with an empty set.
try:
    import selfies as sf
except ImportError:
    sys.exit("FATAL: this integrity audit requires the 'selfies' package, which is not installed.\n"
             "  install:  pip install 'selfies>=2.1'   (or: pip install -r requirements.txt)\n"
             "  refusing to run -- without it the SELFIES round-trip check cannot be evaluated,\n"
             "  and a degraded/empty clean set must never be written over the committed one.")

def obs_c13(s): return [float(x) for x in re.findall(r'(-?\d+\.?\d*)\s*\(', s or "")]
def n_sym_carbons(m):                      # symmetry-unique carbons
    ranks = list(Chem.CanonicalRankAtoms(m, breakTies=False))
    cs = {ranks[a.GetIdx()] for a in m.GetAtoms() if a.GetSymbol()=="C"}
    return len(cs)

def write_clean(path, clean):
    """Write clean_qids.json, but never silently shrink a committed clean set: a broken
    checker looks exactly like a mass ground-truth failure, so a large drop needs --force."""
    old = None
    if os.path.exists(path):
        try: old = set(json.load(open(path)))
        except (OSError, ValueError): old = None          # unreadable/corrupt -> nothing to protect
    if old and len(clean) < len(old)*(1-SHRINK_TOL) and not FORCE:
        lost, gained = sorted(old-clean), sorted(clean-old)
        print(f"    REFUSING to overwrite {path}: clean set {len(old)} -> {len(clean)} "
              f"({100*(1-len(clean)/len(old)):.0f}% smaller, tolerance {SHRINK_TOL:.0%})")
        print(f"      dropped ({len(lost)}): {', '.join(lost[:12])}{' ...' if len(lost)>12 else ''}")
        if gained: print(f"      newly clean ({len(gained)}): {', '.join(gained[:12])}{' ...' if len(gained)>12 else ''}")
        print("      investigate first; if the shrink is real, re-run deliberately with --force")
        return False
    json.dump(sorted(clean), open(path,"w"))
    return True

refused = 0
for d in ["data/benchmark_v3","data/benchmark_v2_ctrl"]:
    q={json.loads(l)["qid"]:json.loads(l) for l in open(f"{d}/questions2.jsonl")}
    a={json.loads(l)["qid"]:json.loads(l) for l in open(f"{d}/answers2.jsonl")}
    clean=set(); flags={}
    for qid,ans in a.items():
        m=Chem.MolFromSmiles(ans["smiles"])
        nobs=len(obs_c13(q[qid]["c_nmr"])); nC=sum(1 for at in m.GetAtoms() if at.GetSymbol()=="C")
        nsym=n_sym_carbons(m)
        # formula + SELFIES sanity
        fmla_ok = rdMolDescriptors.CalcMolFormula(m)==q[qid]["formula"]
        # Only a genuine per-compound failure may set rt_ok=False. Encoder/DecoderError mean
        # this structure is not SELFIES-round-trippable; anything else is the checker itself
        # breaking, which must crash rather than be recorded as a dirty ground truth.
        try:
            rtm = Chem.MolFromSmiles(sf.decoder(sf.encoder(ans["smiles"])))
            rt_ok = rtm is not None and Chem.MolToSmiles(rtm)==Chem.MolToSmiles(m)
        except (sf.EncoderError, sf.DecoderError): rt_ok=False
        reason=[]
        if nobs>nC: reason.append(f"13C-overread({nobs}>{nC})")     # contamination / merged
        if nobs < max(2,nsym//2): reason.append(f"13C-sparse({nobs}<{nsym})")
        if not fmla_ok: reason.append("formula-mismatch")
        if not rt_ok: reason.append("selfies-rt-fail")
        if reason: flags[qid]=reason
        else: clean.add(qid)
    print(f"{d}: {len(clean)}/{len(a)} spectrally-clean ground truths; {len(flags)} flagged")
    for qid,r in list(flags.items())[:6]: print(f"    {qid}: {r}")
    if not write_clean(f"{d}/clean_qids.json", clean): refused += 1

if refused: sys.exit(f"\n{refused} clean_qids.json file(s) left unchanged (see above). Nothing was overwritten.")
