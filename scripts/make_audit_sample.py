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

    # stratified draw, seeded — this is the Task 1 panel and must stay unbiased
    rng = random.Random(SEED)
    sample = []
    for strat in ("simple", "complex"):
        pool = sorted([c for c in compounds if c["difficulty"] == strat],
                      key=lambda c: (c["dir"], c["qid"]))           # stable order
        sample += rng.sample(pool, min(N_PER_STRATUM, len(pool)))
    sample.sort(key=lambda c: (c["difficulty"], c["dir"], c["qid"]))
    task1_ids = {(c["dir"], c["qid"]) for c in sample}

    # Task 2 needs every eligible compound, and cannot be bought by enlarging the draw
    # above. Recall-positive implies nothing about difficulty, but it *does* correlate
    # with the model's top-1 being right -- a correct top-1 is recall-positive by
    # definition. Forcing eligible compounds into the stratified sample would therefore
    # raise the rate of correct answers the Task 1 panel sees, which is exactly the
    # quantity Task 1 exists to judge. So the extra ones are carried as TASK 2 ONLY:
    # they are ranked, they carry no Task 1 block, and the Task 1 draw is untouched.
    eligible = [c for c in compounds
                if any(x["is_true"] for x in c["cands"])
                and len({x["smiles"] for x in c["cands"]}) > 1]
    extra = sorted([c for c in eligible if (c["dir"], c["qid"]) not in task1_ids],
                   key=lambda c: (c["difficulty"], c["dir"], c["qid"]))
    sample += extra

    blind, key = [], []
    n_recall = 0
    for i, c in enumerate(sample, 1):
        aid = f"A{i:02d}"
        p = c["prompt"]
        task1 = (c["dir"], c["qid"]) in task1_ids
        # Task 2 is shown wherever there is something to rank -- NOT only where the true
        # structure is present. Gating it on recall leaked Task 1 twice over. In the
        # extreme, a recall-positive compound with one candidate told the reviewer that
        # candidate was the truth, and hence that the model's top-1 was right, with no
        # chemistry at all: three of thirty verdicts, every one toward "correct". Less
        # obviously but more pervasively, the mere presence of a Task 2 block marked a
        # compound as recall-positive, and a correct top-1 is recall-positive by
        # definition -- measured across the Task 1 panel, that raised the rate of correct
        # answers from 12% to 67%, a five-fold prior available without reading a spectrum.
        # Gating it on "more than one candidate" only inverted the signal: the seven
        # compounds left without a Task 2 block were the ones the model answered with a
        # single structure, and answering with one structure correlates with being right
        # (43% against 17%). So Task 2 appears on EVERY compound. Its presence now carries
        # no information at all. A lone candidate is a trivial ranking and costs the
        # reviewer seconds, and it is excluded from the precision figure for the same
        # reason §5.2 excludes it there -- a verifier facing no choice scores by
        # construction. Sets with no true structure also measure something the
        # recall-gated design could not: whether an expert declines to be confident when
        # nothing on offer is correct.
        n_distinct = len({x["smiles"] for x in c["cands"]})
        recall = any(x["is_true"] for x in c["cands"])
        task2 = n_distinct >= 1
        n_recall += recall

        # Task 1: render the model's top-1 (blind, unlabelled image only)
        if task1:
            render(c["top1"], f"{STRUCT}/{aid}_top1.png")

        # Task 2 (recall-positive only): shuffle full candidate set, render each.
        # Separate RNG stream so shuffling is decoupled from the sampling draw.
        cand_labels = None
        key_cands = None
        key_true_label = None
        if task2:
            shuffled = c["cands"][:]
            random.Random(SEED + 1000 + i).shuffle(shuffled)   # per-compound, decoupled
            cand_labels, key_cands = [], []
            for j, x in enumerate(shuffled):
                if j >= len(CAND_LABELS):       # guard: more candidates than labels
                    break
                lbl = CAND_LABELS[j]
                render(x["smiles"], f"{STRUCT}/{aid}_cand{lbl}.png")
                cand_labels.append(lbl)
                key_cands.append({"label": lbl, "smiles": x["smiles"], "is_true": x["is_true"]})
                if x["is_true"]: key_true_label = lbl

        # BLIND record: spectra + image references only — NO SMILES, NO model-pick id.
        blind.append({
            "audit_id": aid, "difficulty": c["difficulty"],
            "heavy_atoms": c["heavy_atoms"], "formula": p.get("formula"),
            "ir_bands_cm-1": p.get("ir_bands_cm-1"), "h_nmr": p.get("h_nmr"),
            "c_nmr": p.get("c_nmr"),
            "task1_applicable": task1,
            "task1_structure_image": f"{aid}_top1.png" if task1 else None,
            "n_candidates": len(c["cands"]),
            "task2_applicable": task2,
            "task2_candidate_labels": cand_labels,    # None if not recall-positive
        })
        # KEY (held out, git-ignored): all structures + answers live here only.
        key.append({
            "audit_id": aid, "source": f'{c["dir"]}:{c["qid"]}',
            "true_smiles": c["true_smiles"], "true_inchikey": c["true_inchikey"],
            "model_top1_smiles": c["top1"],
            "task1_applicable": task1,
            "top1_correct": _same(c["top1"], c["true_inchikey"]) if task1 else None,
            "recall_positive": recall,
            "true_candidate_label": key_true_label,
            "candidates": key_cands,
        })

    with open(f"{OUT}/sample.jsonl", "w") as f:
        for r in blind: f.write(json.dumps(r) + "\n")
    with open(f"{OUT}/key.jsonl", "w") as f:
        for r in key: f.write(json.dumps(r) + "\n")
    write_scoring_sheet(blind)
    n_correct = sum(bool(k["top1_correct"]) for k in key if k["task1_applicable"])
    n_task1 = sum(1 for k in key if k["task1_applicable"])
    print(f"wrote {len(blind)} compounds to {OUT}/sample.jsonl "
          f"({sum(b['difficulty']=='simple' for b in blind)} simple / "
          f"{sum(b['difficulty']=='complex' for b in blind)} complex)")
    n_t2 = sum(1 for b in blind if b["task2_applicable"])
    scored = [b for b in blind if b["task2_applicable"]
              and key[[k["audit_id"] for k in key].index(b["audit_id"])]["recall_positive"]] \
        if False else None
    kd = {k["audit_id"]: k for k in key}
    n_scored = sum(1 for b in blind if b["task2_applicable"]
                   and kd[b["audit_id"]]["recall_positive"])
    n_t1 = sum(1 for b in blind if b["task1_applicable"])
    print(f"  Task 1 panel: {n_t1} (stratified draw, untouched by the Task 2 additions)")
    print(f"  Task 2 shown on every rankable compound: {n_t2}")
    n_prec = sum(1 for b in blind if b["task2_applicable"]
                 and len(b["task2_candidate_labels"] or []) > 1
                 and kd[b["audit_id"]]["recall_positive"])
    print(f"    {n_prec} carry the true structure AND a real choice -> verifier precision")
    print(f"    {n_scored - n_prec} carry the truth but only one candidate -> excluded from")
    print(f"      precision, as §5.2 excludes them: a verifier facing no choice scores by")
    print(f"      construction")
    print(f"    {n_t2 - n_scored} carry no true structure -> whether an expert declines to")
    print(f"      be confident when nothing on offer is correct")
    print(f"  recall-positive overall: {n_recall}")
    print(f"  key: model top-1 correct on {n_correct}/{n_task1} (kept in key.jsonl only)")
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
         "",
         "IMPORTANT: where a compound has a Task 2, complete the Task-2 ranking **before**",
         "looking at the Task-1 structure — the model's top-1 is one of the Task-2 candidates,",
         "so ranking first keeps your Task-2 judgement independent of the model's choice.",
         ""]
    for b in blind:
        aid = b["audit_id"]
        L += [f"## {aid}  ({b['difficulty']}, {b['heavy_atoms']} heavy atoms)", "",
              f"- **Formula:** {b['formula']}",
              f"- **IR (cm⁻¹):** {b['ir_bands_cm-1']}",
              f"- **¹H NMR:** {b['h_nmr']}",
              f"- **¹³C NMR:** {b['c_nmr']}", ""]
        if b["task2_applicable"]:
            opts = "  ".join(f"`structures/{aid}_cand{lbl}.png` = **{lbl}**"
                             for lbl in b["task2_candidate_labels"])
            L += ["### Task 2 — rank the candidate set by spectral fit (best first) — DO FIRST",
                  opts, "",
                  "- Your ranking (best → worst), by letter: ______________________________",
                  "- Confidence in your top pick (1–5): **____**", ""]
        if b["task1_applicable"]:
            L += ["### Task 1 — is the model's proposed structure consistent with the spectra?",
                  f"Structure: `structures/{aid}_top1.png`", "",
                  "- Consistency with ALL spectra (1=contradicted … 5=fully): **____**",
                  "- Verdict (circle): correct / wrong-regiochemistry / wrong-scaffold / uninterpretable",
                  "- Single most diagnostic peak (support or refute): ______________________________",
                  ""]
        else:
            L += ["*(Task 2 only — this compound carries no Task 1 item.)*", ""]
        L += ["---", ""]
    open(f"{OUT}/scoring_sheet.md", "w").write("\n".join(L))

if __name__ == "__main__":
    main()
