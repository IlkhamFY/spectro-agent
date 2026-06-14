#!/usr/bin/env python3
"""Generate the frozen, pre-registered expert-audit sample described in
docs/EXPERT_AUDIT_PROTOCOL.md.

Draws a difficulty-stratified 30-compound sample (15 simple / 15 complex) from the
60-compound forward-verification set (data/fverify), which uniquely carries both the
model's ranked candidates (self_rank, is_true) and the observed spectra. Emits a
BLIND reviewer package (prompts + rendered structures + scoring sheet) and a SEPARATE
answer key, so a human panel can score Task 1 (elucidation correctness) and Task 2
(verifier calibration) without seeing the ground truth.

Deterministic: seed=0. Re-running reproduces byte-identical sample.jsonl / key.jsonl.
"""
import json, os, random
from collections import defaultdict
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

SEED = 0
N_PER_STRATUM = 15
OUT = "data/audit"
STRUCT = f"{OUT}/structures"
CAND_LABELS = "ABCDEFGH"

def load_jsonl(p): return [json.loads(l) for l in open(p)]

def heavy_atoms(smi):
    m = Chem.MolFromSmiles(smi)
    return m.GetNumHeavyAtoms() if m else None

def render(smi, path, size=(330, 240)):
    m = Chem.MolFromSmiles(smi)
    if m is None: return False
    Draw.MolToImage(m, size=size).save(path)
    return True

def main():
    os.makedirs(STRUCT, exist_ok=True)
    cands = load_jsonl("data/fverify/candidates.jsonl")

    # questions (prompts) + answers (ground truth) per source dir
    prompts, truth = {}, {}
    for d in {c["dir"] for c in cands}:
        for q in load_jsonl(f"{d}/questions2.jsonl"):
            prompts[(d, q["qid"])] = q
        for a in load_jsonl(f"{d}/answers2.jsonl"):
            truth[(d, a["qid"])] = a

    # group candidates per compound
    by = defaultdict(list)
    for c in cands:
        by[(c["dir"], c["qid"])].append(c)

    compounds = []
    for (d, qid), cs in by.items():
        cs = sorted(cs, key=lambda c: c.get("self_rank", 99))
        a = truth.get((d, qid), {})
        true_smi = a.get("smiles")
        ha = a.get("heavy_atoms") or (heavy_atoms(true_smi) if true_smi else None)
        compounds.append(dict(dir=d, qid=qid, difficulty=cs[0]["difficulty"],
            heavy_atoms=ha, prompt=prompts.get((d, qid), {}),
            true_smiles=true_smi, true_inchikey=a.get("inchikey"),
            top1=cs[0]["smiles"], cands=cs))

    # stratified draw, seeded
    rng = random.Random(SEED)
    sample = []
    for strat in ("simple", "complex"):
        pool = sorted([c for c in compounds if c["difficulty"] == strat],
                      key=lambda c: (c["dir"], c["qid"]))           # stable order
        sample += rng.sample(pool, min(N_PER_STRATUM, len(pool)))
    sample.sort(key=lambda c: (c["difficulty"], c["dir"], c["qid"]))

    blind, key = [], []
    n_recall = 0
    for i, c in enumerate(sample, 1):
        aid = f"A{i:02d}"
        p = c["prompt"]
        recall = any(x["is_true"] for x in c["cands"])
        n_recall += recall

        # Task 1: render the model's top-1 (blind, unlabelled)
        render(c["top1"], f"{STRUCT}/{aid}_top1.png")

        # Task 2 (recall-positive only): shuffle full candidate set, render each
        cand_block = None
        if recall:
            shuffled = c["cands"][:]
            rng.shuffle(shuffled)
            cand_block = []
            true_idx = -1
            for j, x in enumerate(shuffled):
                lbl = CAND_LABELS[j]
                render(x["smiles"], f"{STRUCT}/{aid}_cand{lbl}.png")
                cand_block.append({"label": lbl, "smiles": x["smiles"]})
                if x["is_true"]: true_idx = j
            key_true_label = CAND_LABELS[true_idx] if true_idx >= 0 else None

        blind.append({
            "audit_id": aid, "difficulty": c["difficulty"],
            "heavy_atoms": c["heavy_atoms"], "formula": p.get("formula"),
            "ir_bands_cm-1": p.get("ir_bands_cm-1"), "h_nmr": p.get("h_nmr"),
            "c_nmr": p.get("c_nmr"),
            "model_top1_smiles": c["top1"],
            "n_candidates": len(c["cands"]),
            "task2_applicable": recall,
            "candidates_shuffled": cand_block,    # None if not recall-positive
        })
        key.append({
            "audit_id": aid, "source": f'{c["dir"]}:{c["qid"]}',
            "true_smiles": c["true_smiles"], "true_inchikey": c["true_inchikey"],
            "model_top1_smiles": c["top1"],
            "top1_correct": _same(c["top1"], c["true_inchikey"]),
            "recall_positive": recall,
            "true_candidate_label": (key_true_label if recall else None),
        })

    with open(f"{OUT}/sample.jsonl", "w") as f:
        for r in blind: f.write(json.dumps(r) + "\n")
    with open(f"{OUT}/key.jsonl", "w") as f:
        for r in key: f.write(json.dumps(r) + "\n")
    write_scoring_sheet(blind)
    n_correct = sum(k["top1_correct"] for k in key)
    print(f"wrote {len(blind)} compounds to {OUT}/sample.jsonl "
          f"({sum(b['difficulty']=='simple' for b in blind)} simple / "
          f"{sum(b['difficulty']=='complex' for b in blind)} complex)")
    print(f"  recall-positive (Task 2 applicable): {n_recall}")
    print(f"  key: model top-1 correct on {n_correct}/{len(key)} (kept in key.jsonl only)")
    print(f"  rendered structures -> {STRUCT}/  ;  scoring sheet -> {OUT}/scoring_sheet.md")

def _same(smi, inchikey):
    if not smi or not inchikey: return False
    m = Chem.MolFromSmiles(smi)
    if not m: return False
    return Chem.MolToInchiKey(m).split("-")[0] == inchikey.split("-")[0]

def write_scoring_sheet(blind):
    L = ["# Expert-audit scoring sheet (blinded)",
         "",
         "Reviewer: ____________________   Date: __________   (do not consult the literature)",
         "",
         "You are shown, for each compound, the exact spectra given to the model and one or",
         "more candidate **structures** (rendered images in `structures/`). You do **not**",
         "see which is correct. See `README.md` / `docs/EXPERT_AUDIT_PROTOCOL.md` for the rubric.",
         ""]
    for b in blind:
        aid = b["audit_id"]
        L += [f"## {aid}  ({b['difficulty']}, {b['heavy_atoms']} heavy atoms)", "",
              f"- **Formula:** {b['formula']}",
              f"- **IR (cm⁻¹):** {b['ir_bands_cm-1']}",
              f"- **¹H NMR:** {b['h_nmr']}",
              f"- **¹³C NMR:** {b['c_nmr']}", "",
              "### Task 1 — is the model's proposed structure consistent with the spectra?",
              f"Structure: `structures/{aid}_top1.png`", "",
              "- Consistency with ALL spectra (1=contradicted … 5=fully): **____**",
              "- Verdict (circle): correct / wrong-regiochemistry / wrong-scaffold / uninterpretable",
              "- Single most diagnostic peak (support or refute): ______________________________",
              ""]
        if b["task2_applicable"]:
            opts = "  ".join(f"`structures/{aid}_cand{c['label']}.png` = **{c['label']}**"
                             for c in b["candidates_shuffled"])
            L += ["### Task 2 — rank the candidate set by spectral fit (best first)",
                  opts, "",
                  "- Your ranking (best → worst), by letter: ______________________________",
                  "- Confidence in your top pick (1–5): **____**", ""]
        L += ["---", ""]
    open(f"{OUT}/scoring_sheet.md", "w").write("\n".join(L))

if __name__ == "__main__":
    main()
