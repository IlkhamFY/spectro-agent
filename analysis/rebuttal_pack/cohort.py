"""Load the locked n=500 roster and every deposited prediction. Does not write an answer key.

Ground truth for the two expansion arms is rebuilt in memory by the same unique
(formula, IR, 13C) join used when those arms were scored. The join reads
data/irexp_resolved/irexp_resolved.jsonl.gz and discards the spectra.
"""
from __future__ import annotations

import gzip
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[2]
EXPAND_SHA = "48fcd30153df5e331fab43cfa514763db8ee3891"
GOLD = ROOT / "data" / "irexp_resolved" / "irexp_resolved.jsonl.gz"

# Locked fverify wall. Not recomputed here. Wilson intervals use these counts.
WALL = {
    "n": 500,
    "verified": 204,
    "misranked": 45,
    "never_proposed": 251,
    "recalled": 249,
    "source": "data/fverify_n500/WALL_n500.md on cursor/fverify-n500-unify-629c",
}

ABLATION_PREFIX = {
    "full": "full",
    "noir": "noIR",
    "noh": "noH",
    "noc": "noC",
    "formulair": "formulaIR",
    "noformula": "noFormula",
}


def _q_c13(s):
    return tuple(round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", s or ""))


def _g_c13(s):
    if "(" in (s or ""):
        return _q_c13(s)
    return tuple(round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", s or ""))


def _ir_key(bands):
    return tuple(round(float(x), 1) for x in (bands or []))


def _git_show(sha, path):
    return subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=ROOT)


def _read_jsonl_bytes(blob):
    rows = []
    for line in blob.decode().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _index_gold(formulas):
    by = defaultdict(list)
    with gzip.open(GOLD, "rt") as fh:
        for line in fh:
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
            by[(form, _ir_key(r.get("ir_bands_cm-1")), _g_c13(r.get("c_nmr")))].append({
                "smiles": Chem.MolToSmiles(m),
                "ik": (r.get("inchikey") or Chem.MolToInchiKey(m))[:14],
                "pool": r.get("license_pool") or "unknown",
                "hac": m.GetNumHeavyAtoms(),
            })
    return by


def _match(q, gold):
    key = (q["formula"], _ir_key(q.get("ir_bands_cm-1")), _q_c13(q.get("c_nmr")))
    hits = gold.get(key, [])
    if len(hits) != 1:
        raise SystemExit(f"{q.get('qid')}: expected 1 gold hit, got {len(hits)}")
    return hits[0]


def _item_from_question(q, hit, cohort, arm, cands):
    h = (q.get("h_nmr") or "").strip()
    c = (q.get("c_nmr") or "").strip()
    ir = q.get("ir_bands_cm-1") or []
    return {
        "uid": f"{cohort}:{q['qid']}",
        "cohort": cohort,
        "qid": q["qid"],
        "arm": arm,
        "smiles": hit["smiles"],
        "ik": hit["ik"],
        "difficulty": q.get("difficulty") or "?",
        "hac": int(hit["hac"]),
        "formula": q["formula"],
        "pool": hit["pool"],
        "opus": list(cands or [])[:3],
        "nmr": [],
        "has_ir": bool(ir),
        "has_h": bool(h),
        "has_c": bool(c),
    }


def _load_main_194(gold):
    """Same cohort as scripts/score_main.py: clean main + all of v3 + all of v2_ctrl."""
    items = []
    answers = {json.loads(l)["qid"]: json.loads(l) for l in open(ROOT / "data/benchmark_main/answers2.jsonl")}
    questions = {json.loads(l)["qid"]: json.loads(l) for l in open(ROOT / "data/benchmark_main/questions2.jsonl")}
    clean = set(json.load(open(ROOT / "data/benchmark_main/clean_qids.json")))
    pred = {}
    for f in sorted((ROOT / "data/benchmark_main/raw").glob("*.json")):
        pred.update(json.load(open(f)))
    for qid, ans in answers.items():
        if qid not in clean:
            continue
        cands = pred.get(f"M-{qid}")
        if cands is None:
            continue
        q = questions[qid]
        # Prefer the committed answer key for this locked slice. The join only supplies the licence pool.
        hit = _match(q, gold)
        if hit["ik"] != ans["inchikey"][:14]:
            raise SystemExit(f"main {qid}: join InChIKey != committed answer key")
        q = dict(q)
        q["difficulty"] = ans.get("difficulty") or q.get("difficulty")
        items.append(_item_from_question(q, hit, "locked-main", "locked194", cands))

    for cohort, directory, arm in (
        ("locked-v3", "benchmark_v3", "locked194"),
        ("locked-v2ctrl", "benchmark_v2_ctrl", "locked194"),
    ):
        base = ROOT / "data" / directory
        aa = {json.loads(l)["qid"]: json.loads(l) for l in open(base / "answers2.jsonl")}
        qq = {json.loads(l)["qid"]: json.loads(l) for l in open(base / "questions2.jsonl")}
        pp = {json.loads(l)["qid"]: json.loads(l) for l in open(base / "predictions2.jsonl")}
        for qid, ans in aa.items():
            q = dict(qq[qid])
            q["difficulty"] = ans.get("difficulty") or q.get("difficulty")
            hit = _match(q, gold)
            if hit["ik"] != ans["inchikey"][:14]:
                raise SystemExit(f"{directory} {qid}: join InChIKey != committed answer key")
            cands = pp[qid].get("candidates", [])
            items.append(_item_from_question(q, hit, cohort, arm, cands))
    if len(items) != 194:
        raise SystemExit(f"locked slice is {len(items)}, expected 194")
    return items


def _load_expansion(gold, sha, round_dir, cohort, arm, keep=None):
    qs = _read_jsonl_bytes(_git_show(sha, f"{round_dir}/questions2.jsonl"))
    preds = {r["qid"]: r.get("candidates", []) for r in _read_jsonl_bytes(_git_show(sha, f"{round_dir}/predictions2.jsonl"))}
    items = []
    for q in qs:
        if keep is not None and q["qid"] not in keep:
            continue
        hit = _match(q, gold)
        items.append(_item_from_question(q, hit, cohort, arm, preds.get(q["qid"], [])))
    return items


def _attach_nmr(items):
    path = Path(__file__).resolve().parent / "inputs" / "nmrtrans" / "predictions.jsonl"
    hits_path = Path(__file__).resolve().parent / "inputs" / "nmrtrans" / "hits.jsonl"
    pred = {}
    for line in open(path):
        r = json.loads(line)
        pred[r["uid"]] = r.get("candidates") or []
    official = {}
    for line in open(hits_path):
        r = json.loads(line)
        official[r["uid"]] = (str(r["top1"]) == "True", str(r["recall"]) == "True")
    missing = []
    for it in items:
        cands = pred.get(it["uid"])
        if cands is None:
            missing.append(it["uid"])
            continue
        it["nmr"] = list(cands)[:3]
    if missing:
        raise SystemExit(f"NMRTrans predictions missing for {len(missing)} items, e.g. {missing[:5]}")
    return official


def _parse_prompt_blocks(text):
    rows = []
    for block in text.split("### ")[1:]:
        lines = block.splitlines()
        mid = lines[0].strip()
        formula = ""
        ir = []
        c_nmr = ""
        for ln in lines[1:]:
            if ln.startswith("Molecular formula:"):
                formula = ln.split(":", 1)[1].strip()
            elif ln.startswith("IR bands"):
                raw = ln.split(":", 1)[1].strip()
                try:
                    ir = json.loads(raw.replace("'", '"'))
                except Exception:
                    ir = []
            elif ln.startswith("13C NMR:"):
                c_nmr = ln.split(":", 1)[1].strip()
        rows.append({"mid": mid, "formula": formula, "ir": ir, "c_nmr": c_nmr})
    return rows


def _map_mids(items):
    """Map modality M-ids onto the 60-compound forward-verify slice (v3 + v2_ctrl)."""
    prompt = (ROOT / "data/modality/prompt_full.txt").read_text()
    blocks = _parse_prompt_blocks(prompt)
    lookup = {}
    for directory, cohort in (("benchmark_v3", "locked-v3"), ("benchmark_v2_ctrl", "locked-v2ctrl")):
        for line in open(ROOT / "data" / directory / "questions2.jsonl"):
            q = json.loads(line)
            lookup[(q["formula"], _ir_key(q.get("ir_bands_cm-1")), _q_c13(q.get("c_nmr")))] = f"{cohort}:{q['qid']}"
    mid_to_uid = {}
    for b in blocks:
        key = (b["formula"], _ir_key(b["ir"]), _q_c13(b["c_nmr"]))
        uid = lookup.get(key)
        if uid is None:
            raise SystemExit(f"prompt {b['mid']} did not match a v3/v2_ctrl question")
        mid_to_uid[b["mid"]] = uid
    if len(mid_to_uid) != 60:
        raise SystemExit(f"expected 60 M-ids, got {len(mid_to_uid)}")
    return mid_to_uid


def _load_sweep():
    out = {}
    base = ROOT / "sweep_out"
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        merged = {}
        clash = []
        for f in sorted(d.glob("reply_*.json")):
            data = json.load(open(f))
            for k, v in data.items():
                if k in merged and merged[k] != v:
                    clash.append(k)
                merged.setdefault(k, v)
        if merged:
            out[d.name] = merged
            if clash:
                print(f"warning: {d.name} has {len(clash)} conflicting reply keys; kept the first")
    return out


def _load_ablation():
    text = subprocess.check_output(["git", "branch", "-r"], cwd=ROOT, text=True)
    found = {}
    for line in text.splitlines():
        ref = line.strip()
        name = ref.split("/", 1)[-1]
        if "/ablation-" not in "/" + name and "ablation-" not in name:
            continue
        # origin/cursor/ablation-full-b01-8db1
        m = re.search(r"ablation-([a-z0-9]+)-b(\d+)-", name)
        if not m:
            continue
        prefix, batch = m.group(1), m.group(2)
        cond = ABLATION_PREFIX.get(prefix)
        if cond is None:
            continue
        listing = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", ref], cwd=ROOT, text=True)
        paths = [p for p in listing.splitlines() if p.endswith(f"/b{batch}.json") and "campaign_2026" in p]
        if len(paths) != 1:
            raise SystemExit(f"{ref}: expected one campaign json, found {paths}")
        blob = subprocess.check_output(["git", "show", f"{ref}:{paths[0]}"], cwd=ROOT)
        data = json.loads(blob)
        # Trust the directory name under raw/ when it is present.
        parts = paths[0].split("/")
        if "raw" in parts:
            cond = parts[parts.index("raw") + 1]
        slot = found.setdefault(cond, {})
        overlap = set(slot).intersection(data)
        if overlap:
            raise SystemExit(f"{cond}: duplicate ids {list(overlap)[:5]}")
        slot.update(data)
    return found


def _load_committed_modality():
    out = {}
    mod = ROOT / "data" / "modality"
    for cond, name in (("full", "out_full.json"), ("formulaonly", "out_formulaonly.json")):
        p = mod / name
        if p.exists():
            out[cond] = json.load(open(p))
    return out


def _load_ladder():
    """24-compound Claude ladder. Keys in the raw files are M-<qid> or bare qids."""
    subset = [
        "R01", "R02", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12", "R13",
        "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R22", "R23", "R24", "R25", "R26",
    ]
    folders = {
        "Opus": ROOT / "data/benchmark_main/raw",
        "Sonnet": ROOT / "data/benchmark_main/sonnet",
        "Haiku": ROOT / "data/benchmark_main/haiku",
        "Fable": ROOT / "data/benchmark_main/fable",
    }
    out = {}
    for model, folder in folders.items():
        pred = {}
        if not folder.exists():
            continue
        for f in sorted(folder.glob("*.json")):
            try:
                data = json.load(open(f))
            except Exception:
                continue
            for k, v in data.items():
                pred.setdefault(k.replace("M-", ""), v)
        out[model] = {q: pred.get(q) for q in subset}
    return subset, out


def load():
    if not GOLD.exists():
        raise SystemExit(f"missing gold corpus: {GOLD}")
    # Formulas we will join. Read question formulas first so the index stays small.
    formulas = set()
    for directory in ("benchmark_main", "benchmark_v3", "benchmark_v2_ctrl"):
        for line in open(ROOT / "data" / directory / "questions2.jsonl"):
            formulas.add(json.loads(line)["formula"])
    for round_dir in ("data/benchmark_expand", "data/benchmark_expand_500"):
        for row in _read_jsonl_bytes(_git_show(EXPAND_SHA, f"{round_dir}/questions2.jsonl")):
            formulas.add(row["formula"])
    gold = _index_gold(formulas)

    items = _load_main_194(gold)
    items += _load_expansion(gold, EXPAND_SHA, "data/benchmark_expand", "expand", "plus106")
    cut = json.loads(_git_show(EXPAND_SHA, "data/benchmark_expand_500/headline500_expand200_qids.json"))
    cut = set(cut)
    e500_all = _load_expansion(gold, EXPAND_SHA, "data/benchmark_expand_500", "expand500", "expand200_or_rest")
    for it in e500_all:
        it["arm"] = "expand200" if it["qid"] in cut else "expand500_rest"
    headline = [it for it in items if it["arm"] != "expand500_rest"] + [it for it in e500_all if it["arm"] == "expand200"]
    rest = [it for it in e500_all if it["arm"] != "expand200"]
    # items currently holds 194+106 only. headline must be 500.
    if len(headline) != 500:
        raise SystemExit(f"headline length {len(headline)}")
    official_hits = _attach_nmr(headline)

    clean500 = json.loads(_git_show(EXPAND_SHA, "data/benchmark_expand_500/clean_qids.json"))
    return {
        "expand500_clean": clean500,
        "headline": headline,
        "expand500_rest": rest,
        "expand500_all": e500_all,
        "nmr_official": official_hits,
        "mid_to_uid": _map_mids(headline),
        "sweep": _load_sweep(),
        "ablation": _load_ablation(),
        "committed_modality": _load_committed_modality(),
        "ladder": _load_ladder(),
        "wall": WALL,
        "expand_sha": EXPAND_SHA,
    }
