#!/usr/bin/env python3
"""Rescore the locked n=500 roster from committed deposits. No model calls.

Ground truth for expansion arms is the unique (formula, IR, 13C) join used
by analysis/rebuttal_pack/cohort.py on cursor/rebuttal-analysis-pack-783b.
"""
from __future__ import annotations

import gzip
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[3]
SHA = "48fcd30153df5e331fab43cfa514763db8ee3891"
GOLD = ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz"


def q_c13(s):
    return tuple(round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", s or ""))


def g_c13(s):
    if "(" in (s or ""):
        return q_c13(s)
    return tuple(round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", s or ""))


def ir_key(bands):
    return tuple(round(float(x), 1) for x in (bands or []))


def git_show(path):
    return subprocess.check_output(["git", "show", f"{SHA}:{path}"], cwd=ROOT)


def read_jsonl(blob):
    rows = []
    for line in blob.decode().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def index_gold(formulas):
    by = defaultdict(list)
    n = 0
    with gzip.open(GOLD, "rt") as fh:
        for line in fh:
            n += 1
            r = json.loads(line)
            smi = r.get("smiles")
            if not smi:
                continue
            m = Chem.MolFromSmiles(smi)
            if m is None:
                continue
            form = rdMolDescriptors.CalcMolFormula(m)
            if form not in formulas:
                continue
            by[(form, ir_key(r.get("ir_bands_cm-1")), g_c13(r.get("c_nmr")))].append(r)
    print(f"gold rows scanned {n}; formula-filtered keys {len(by)}")
    return by


def match(q, gold):
    key = (q["formula"], ir_key(q.get("ir_bands_cm-1")), q_c13(q.get("c_nmr")))
    hits = gold.get(key, [])
    if len(hits) != 1:
        return None, len(hits)
    return hits[0], 1


def ik14_smi(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    if m is None:
        return None
    return Chem.MolToInchiKey(m)[:14]


def score_cands(cands, tik):
    hit = top1 = False
    n = 0
    for rank, smi in enumerate((cands or [])[:3]):
        ik = ik14_smi(smi)
        if ik is None:
            continue
        n += 1
        if ik == tik:
            hit = True
            if rank == 0:
                top1 = True
    return top1, hit, n


def murcko(smi):
    m = Chem.MolFromSmiles(smi)
    if m is None:
        return None
    try:
        return MurckoScaffold.MurckoScaffoldSmiles(mol=m)
    except Exception:
        return None


def load_jsonl_path(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def main():
    formulas = set()
    local_q = {}
    for directory in ("benchmark_main", "benchmark_v3", "benchmark_v2_ctrl"):
        for row in load_jsonl_path(ROOT / "data" / directory / "questions2.jsonl"):
            formulas.add(row["formula"])
            local_q[(directory, row["qid"])] = row
    expand_q = read_jsonl(git_show("data/benchmark_expand/questions2.jsonl"))
    e500_q = read_jsonl(git_show("data/benchmark_expand_500/questions2.jsonl"))
    for row in expand_q + e500_q:
        formulas.add(row["formula"])
    gold = index_gold(formulas)

    # predictions
    pred_main = {}
    for f in sorted((ROOT / "data/benchmark_main/raw").glob("*.json")):
        pred_main.update(json.load(open(f)))
    pred_v3 = {r["qid"]: r.get("candidates", []) for r in load_jsonl_path(ROOT / "data/benchmark_v3/predictions2.jsonl")}
    pred_ct = {r["qid"]: r.get("candidates", []) for r in load_jsonl_path(ROOT / "data/benchmark_v2_ctrl/predictions2.jsonl")}
    pred_ex = {r["qid"]: r.get("candidates", []) for r in read_jsonl(git_show("data/benchmark_expand/predictions2.jsonl"))}
    pred_500 = {r["qid"]: r.get("candidates", []) for r in read_jsonl(git_show("data/benchmark_expand_500/predictions2.jsonl"))}
    cut = set(json.loads(git_show("data/benchmark_expand_500/headline500_expand200_qids.json")))
    clean500 = set(json.loads(git_show("data/benchmark_expand_500/clean_qids.json")))
    clean_main = set(json.load(open(ROOT / "data/benchmark_main/clean_qids.json")))

    items = []
    # locked 194
    ans_main = {r["qid"]: r for r in load_jsonl_path(ROOT / "data/benchmark_main/answers2.jsonl")}
    for qid, ans in ans_main.items():
        if qid not in clean_main:
            continue
        q = local_q[("benchmark_main", qid)]
        hit, n = match(q, gold)
        if hit is None:
            raise SystemExit(f"main {qid}: gold hits {n}")
        if (hit.get("inchikey") or "")[:14] != ans["inchikey"][:14]:
            raise SystemExit(f"main {qid}: join ik != answer key")
        items.append(("locked194", qid, q, hit, pred_main.get(f"M-{qid}")))
    for directory, pred, arm in (
        ("benchmark_v3", pred_v3, "locked194"),
        ("benchmark_v2_ctrl", pred_ct, "locked194"),
    ):
        for ans in load_jsonl_path(ROOT / "data" / directory / "answers2.jsonl"):
            q = local_q[(directory, ans["qid"])]
            hit, n = match(q, gold)
            if hit is None:
                raise SystemExit(f"{directory} {ans['qid']}: gold hits {n}")
            if (hit.get("inchikey") or "")[:14] != ans["inchikey"][:14]:
                raise SystemExit(f"{directory} {ans['qid']}: join ik != answer key")
            items.append((arm, ans["qid"], q, hit, pred.get(ans["qid"], [])))

    for q in expand_q:
        hit, n = match(q, gold)
        if hit is None:
            raise SystemExit(f"expand {q['qid']}: gold hits {n}")
        items.append(("plus106", q["qid"], q, hit, pred_ex.get(q["qid"], [])))
    for q in e500_q:
        hit, n = match(q, gold)
        if hit is None:
            raise SystemExit(f"e500 {q['qid']}: gold hits {n}")
        arm = "cut200" if q["qid"] in cut else ("clean_rest" if q["qid"] in clean500 else "dirty")
        items.append((arm, q["qid"], q, hit, pred_500.get(q["qid"], [])))

    def summarize(name, rows):
        t1 = rec = 0
        by = Counter()
        by_t1 = Counter()
        by_rec = Counter()
        cand_n = []
        for arm, qid, q, hit, cands in rows:
            tik = (hit.get("inchikey") or Chem.MolToInchiKey(Chem.MolFromSmiles(hit["smiles"])))[:14]
            top1, hitb, n = score_cands(cands, tik)
            t1 += int(top1)
            rec += int(hitb)
            d = q.get("difficulty") or "?"
            by[d] += 1
            by_t1[d] += int(top1)
            by_rec[d] += int(hitb)
            cand_n.append(len(cands or []))
        n = len(rows)
        print(f"\n=== {name} n={n} top1 {t1}/{n} recall {rec}/{n} ===")
        for d in ("simple", "complex"):
            if by[d]:
                print(f"  {d}: n={by[d]} top1 {by_t1[d]}/{by[d]} recall {by_rec[d]}/{by[d]}")
        if cand_n:
            print(f"  candidates: mean {sum(cand_n)/len(cand_n):.3f}  ==3 {sum(x==3 for x in cand_n)}  <3 {sum(x<3 for x in cand_n)}  >3 {sum(x>3 for x in cand_n)}")
        return t1, rec, n

    locked = [r for r in items if r[0] == "locked194"]
    plus = [r for r in items if r[0] == "plus106"]
    cut = [r for r in items if r[0] == "cut200"]
    rest = [r for r in items if r[0] == "clean_rest"]
    dirty = [r for r in items if r[0] == "dirty"]
    headline = locked + plus + cut
    summarize("locked194", locked)
    summarize("plus106", plus)
    summarize("cut200", cut)
    summarize("HEADLINE", headline)
    summarize("clean_rest R76-R99", rest)
    summarize("e500 dirty", dirty)
    summarize("e500 all", cut + rest + dirty)
    summarize("clean224", cut + rest)

    # concentration on headline
    dois = []
    iks = []
    scaffolds = []
    pools = Counter()
    for arm, qid, q, hit, cands in headline:
        dois.append(hit.get("source_doi") or hit.get("pmcid") or "MISSING")
        ik = (hit.get("inchikey") or "")[:14]
        iks.append(ik)
        scaffolds.append(murcko(hit.get("smiles")))
        pools[hit.get("license_pool") or "?"] += 1
    doi_c = Counter(dois)
    scaf_c = Counter(s for s in scaffolds if s)
    print("\n=== concentration on headline ===")
    print(f"unique source_doi {len(doi_c)} / {len(dois)}")
    print(f"papers with >1 compound {sum(v>1 for v in doi_c.values())}")
    print(f"max compounds in one paper {max(doi_c.values())}")
    print("top papers", doi_c.most_common(8))
    print(f"unique InChIKey-14 {len(set(iks))} / {len(iks)} dupes {len(iks)-len(set(iks))}")
    print(f"unique Murcko {len(scaf_c)} / {len(scaffolds)} empty {sum(s is None or s=='' for s in scaffolds)}")
    print(f"scaffolds with >1 compound {sum(v>1 for v in scaf_c.values())} max {max(scaf_c.values())}")
    print("top scaffolds", scaf_c.most_common(6))
    hacs = []
    for arm, qid, q, hit, cands in headline:
        m = Chem.MolFromSmiles(hit["smiles"])
        hacs.append(m.GetNumHeavyAtoms())
    hacs.sort()
    mid = (hacs[249] + hacs[250]) / 2
    print(f"heavy atoms n=500 min {hacs[0]} p50_pair {hacs[249]},{hacs[250]} median {mid} max {hacs[-1]} mean {sum(hacs)/len(hacs):.2f}")
    print("license pools", dict(pools))
    # cross-slice ik collisions
    def iks_of(rows):
        out = set()
        for arm, qid, q, hit, cands in rows:
            out.add((hit.get("inchikey") or "")[:14])
        return out
    a, b, c = iks_of(locked), iks_of(plus), iks_of(cut)
    print(f"ik overlap locked&106 {len(a&b)} locked&200 {len(a&c)} 106&200 {len(b&c)}")

    # per-slice doi
    for name, rows in (("locked", locked), ("plus106", plus), ("cut200", cut)):
        dc = Counter((hit.get("source_doi") or "MISSING") for *_, hit, __ in [(r[0], r[1], r[2], r[3], r[4]) for r in rows])
        # rewrite cleanly
        dc = Counter()
        for arm, qid, q, hit, cands in rows:
            dc[hit.get("source_doi") or "MISSING"] += 1
        print(f"{name}: papers {len(dc)} max/paper {max(dc.values())} multi {sum(v>1 for v in dc.values())}")


if __name__ == "__main__":
    main()
