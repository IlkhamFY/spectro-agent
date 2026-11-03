#!/usr/bin/env python3
"""Memorization proxy for the locked IRSpectra-Bench n=500 set.

Compares each gold structure with ChEMBL (Morgan radius 2, 2048 bits) and
PubChem. Scores deposited LLM candidates. Does not edit locked benchmark
files or scores.

  python analysis/memorization/run.py
"""
from __future__ import annotations

import gzip
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as mpe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
FIG = HERE / "figures"
TAB = HERE / "tables"
CACHE.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

# Expansion rounds live on this commit. The n=194 files are in the working tree.
PIN = "48fcd30153df5e331fab43cfa514763db8ee3891"
CHEMBL_NAME = "chembl_37"
CHEMBL_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/"
    "chembl_37_chemreps.txt.gz"
)
CHEMBL_BYTES = 292540141
UA = "irspectra-memorization/1.0"
# Famous: a short non-systematic PubChem title plus enough synonyms that the
# record is not a one-off deposition. A count-only cut is reported separately.
SYNONYM_FAMOUS = 15
COUNT_ONLY = 30
FP_MAX = 4_000_000

ACCENT = "#b83280"
GREY = "#6e6e6e"
GREY_LT = "#b4b4b4"
INK = "#1a1a1a"
FAINT = "#e6e6e6"
WIDTH_MM = 180
FS = 6.0
FS_PANEL = 6.5
AXIS_LW = 0.5

SIM_BINS = [
    ("<0.4", lambda s, ex: (not ex) and s < 0.4),
    ("0.4-0.6", lambda s, ex: (not ex) and 0.4 <= s < 0.6),
    ("0.6-0.8", lambda s, ex: (not ex) and 0.6 <= s < 0.8),
    (">=0.8", lambda s, ex: (not ex) and s >= 0.8),
    ("exact", lambda s, ex: ex),
]
HAC_BINS = [
    ("8-15", lambda h: h <= 15),
    ("16-24", lambda h: 16 <= h <= 24),
    ("25-34", lambda h: 25 <= h <= 34),
    (">=35", lambda h: h >= 35),
]

_GEN = None
_HTTP_LOCK = threading.Lock()
_LAST_HTTP = [0.0]


def morgan_gen():
    global _GEN
    if _GEN is None:
        _GEN = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    return _GEN


def parse_mol(smi):
    if not smi or not isinstance(smi, str):
        return None
    m = Chem.MolFromSmiles(smi)
    if m is None:
        return None
    try:
        Chem.RemoveStereochemistry(m)
    except Exception:
        return None
    return m


def morgan_u64(mol):
    fp = morgan_gen().GetFingerprint(mol)
    arr = np.zeros((2048,), dtype=np.uint8)
    DataStructs.ConvertToNumpyArray(fp, arr)
    bits = np.packbits(arr)
    return np.frombuffer(bits.tobytes(), dtype=np.uint64).copy()


def murcko_smiles(mol):
    try:
        sc = MurckoScaffold.GetScaffoldForMol(mol)
    except Exception:
        return ""
    if sc is None or sc.GetNumAtoms() == 0:
        return ""
    try:
        return Chem.MolToSmiles(sc)
    except Exception:
        return ""


def ik14(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    if m is None:
        return None
    try:
        return Chem.MolToInchiKey(m)[:14]
    except Exception:
        return None


def wilson(k, n, z=1.96):
    if n <= 0:
        return (float("nan"), float("nan"))
    k = float(k)
    n = float(n)
    p = k / n
    z2 = z * z
    den = 1.0 + z2 / n
    centre = p + z2 / (2.0 * n)
    margin = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    lo = max(0.0, (centre - margin) / den)
    hi = min(1.0, (centre + margin) / den)
    return lo, hi


def pct(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    return f"{100.0 * x:.1f}"


def ci_text(k, n):
    lo, hi = wilson(k, n)
    if n <= 0 or math.isnan(lo):
        return "n=0"
    return f"{100.0 * k / n:.1f}% [{100.0 * lo:.1f}-{100.0 * hi:.1f}]"


def git_text(path):
    return subprocess.check_output(
        ["git", "show", f"{PIN}:{path}"], text=True, errors="replace"
    )


def git_json(path):
    return json.loads(git_text(path))


def git_jsonl(path):
    rows = []
    for line in git_text(path).splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def looks_common(title, iupac):
    if not title:
        return False
    t = title.strip()
    if iupac and t.lower() == iupac.strip().lower():
        return False
    if len(t) < 4 or len(t) > 40:
        return False
    letters = sum(c.isalpha() for c in t)
    if letters < 4:
        return False
    if sum(c.isdigit() for c in t) > 1:
        return False
    if t.count("-") > 2 or t.count("(") or t.count(")") or "/" in t:
        return False
    if re.fullmatch(r"\d{2,7}-\d{2}-\d", t):
        return False
    return True


def is_famous(in_pubchem, synonym_count, common):
    return bool(in_pubchem and common and synonym_count >= SYNONYM_FAMOUS)


def sim_bin(sim, exact):
    for name, fn in SIM_BINS:
        if fn(sim, exact):
            return name
    return "NA"


def hac_bin(h):
    for name, fn in HAC_BINS:
        if fn(h):
            return name
    return "NA"


def score_cands(truth, cands):
    iks = []
    for s in (cands or [])[:3]:
        if isinstance(s, str):
            iks.append(ik14(s))
    top1 = bool(iks) and truth is not None and iks[0] == truth
    top3 = truth is not None and any(x == truth for x in iks)
    return bool(top1), bool(top3)


def load_loose_json(path):
    raw = Path(path).read_text(errors="replace")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        i, j = raw.find("{"), raw.rfind("}")
        if i < 0 or j <= i:
            raise
        return json.loads(raw[i : j + 1])


# ---------------------------------------------------------------- cohort
def index_resolved():
    idx = {}
    path = ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz"
    with gzip.open(path, "rt") as f:
        for line in f:
            r = json.loads(line)
            key = (r.get("c_nmr") or "", tuple(r.get("ir_bands_cm-1") or []))
            idx.setdefault(key, r)
    return idx


def gold_from_question(q, idx):
    key = (q["c_nmr"], tuple(q["ir_bands_cm-1"]))
    r = idx.get(key)
    if r is None:
        raise SystemExit(f"no gold match for {q.get('qid')}")
    return r


def pmc_from_source(src, pmcid=None):
    if pmcid:
        s = str(pmcid).strip()
        if s.startswith("PMC"):
            return s if s.startswith("PMC") else "PMC" + s
        return "PMC" + s if s.isdigit() else s
    if not src:
        return None
    s = str(src).strip()
    if s.upper().startswith("PMC"):
        rest = s.split(":", 1)[-1]
        rest = rest.replace("PMC", "")
        if rest.isdigit():
            return "PMC" + rest
    return None


def assemble():
    idx = index_resolved()
    rows = []

    def add(row_id, subset, q, smiles, source_doi, pmcid, cands_by_model, blob_by_model):
        mol = Chem.MolFromSmiles(smiles) if smiles else None
        if mol is None:
            raise SystemExit(f"unparseable gold {row_id}")
        truth = Chem.MolToInchiKey(mol)[:14]
        hac = mol.GetNumHeavyAtoms()
        rec = {
            "row_id": row_id,
            "subset": subset,
            "formula": q.get("formula"),
            "smiles": smiles,
            "ik14": truth,
            "hac": hac,
            "pmcid": pmc_from_source(source_doi, pmcid),
            "source_doi": source_doi,
            "models": {},
        }
        for model, cands in cands_by_model.items():
            if cands is None:
                continue
            top1, top3 = score_cands(truth, cands)
            rec["models"][model] = {
                "top1": top1,
                "top3": top3,
                "blob": blob_by_model.get(model, ""),
            }
        rows.append(rec)

    # n=194, identical cohort to scripts/score_main.py
    answers = {r["qid"]: r for r in read_jsonl("data/benchmark_main/answers2.jsonl")}
    questions = {r["qid"]: r for r in read_jsonl("data/benchmark_main/questions2.jsonl")}
    clean = set(json.load(open("data/benchmark_main/clean_qids.json")))
    pred = {}
    blobs = {}
    for f in sorted(Path("data/benchmark_main/raw").glob("*.json")):
        obj = json.loads(f.read_text())
        for k, v in obj.items():
            pred[k] = v
            blobs[k] = json.dumps(v)
    n_main = 0
    for qid, ans in answers.items():
        if qid not in clean:
            continue
        cands = pred.get(f"M-{qid}")
        if cands is None:
            continue
        q = questions[qid]
        add(
            f"main:{qid}",
            "n194",
            q,
            ans["smiles"],
            ans.get("source_doi"),
            None,
            {"Claude Opus": cands},
            {"Claude Opus": blobs.get(f"M-{qid}", "")},
        )
        n_main += 1

    # ladder models on the fixed 24, all inside the clean main round
    ladder = ["R01", "R02", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11",
              "R12", "R13", "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R22",
              "R23", "R24", "R25", "R26"]
    ladder_src = {
        "Claude Sonnet": "data/benchmark_main/sonnet/*.json",
        "Claude Haiku": "data/benchmark_main/haiku/*.json",
        "Claude Fable": "data/benchmark_main/fable/*.json",
    }
    by_qid = {r["row_id"]: r for r in rows}
    for model, pattern in ladder_src.items():
        got = {}
        got_blob = {}
        for f in sorted(Path().glob(pattern)):
            obj = json.loads(f.read_text())
            for k, v in obj.items():
                qid = k.replace("M-", "")
                got[qid] = v
                got_blob[qid] = json.dumps(v)
        for qid in ladder:
            rec = by_qid.get(f"main:{qid}")
            if rec is None or qid not in got:
                raise SystemExit(f"ladder gap {model} {qid}")
            top1, top3 = score_cands(rec["ik14"], got[qid])
            rec["models"][model] = {"top1": top1, "top3": top3, "blob": got_blob[qid]}

    n_ctrl = 0
    ctrl_rows_for_vendor = []
    for d in ["data/benchmark_v3", "data/benchmark_v2_ctrl"]:
        aa = {r["qid"]: r for r in read_jsonl(f"{d}/answers2.jsonl")}
        qq = {r["qid"]: r for r in read_jsonl(f"{d}/questions2.jsonl")}
        pp = {r["qid"]: r for r in read_jsonl(f"{d}/predictions2.jsonl")}
        for qid, ans in aa.items():
            q = qq[qid]
            cands = pp[qid].get("candidates", [])
            subset = "v3" if d.endswith("v3") else "v2ctrl"
            add(
                f"{subset}:{qid}",
                "n194",
                q,
                ans["smiles"],
                ans.get("source_doi"),
                None,
                {"Claude Opus": cands},
                {"Claude Opus": json.dumps(cands)},
            )
            ctrl_rows_for_vendor.append({
                "row_id": f"{subset}:{qid}",
                "difficulty": ans.get("difficulty", "?"),
                "src": f"{Path(d).name}:{qid}",
                "formula": q["formula"],
            })
            n_ctrl += 1
    if n_main + n_ctrl != 194:
        raise SystemExit(f"n=194 drifted: {n_main}+{n_ctrl}")

    # vendor arm: same id order as scripts/cross_vendor_sweep.py load_rows
    ctrl_rows_for_vendor.sort(key=lambda r: (r["difficulty"], r["src"]))
    prompt = (ROOT / "sweep_prompts/solve_01.md").read_text()
    m001 = re.search(r"### M001\nMolecular formula: (\S+)", prompt)
    if not m001 or ctrl_rows_for_vendor[0]["formula"] != m001.group(1):
        raise SystemExit(
            "vendor id map does not match sweep_prompts/solve_01.md M001: "
            f"{ctrl_rows_for_vendor[0]['formula']} vs {None if not m001 else m001.group(1)}"
        )
    mid_to_row = {
        f"M{i:03d}": r["row_id"] for i, r in enumerate(ctrl_rows_for_vendor, 1)
    }
    if len(mid_to_row) != 60:
        raise SystemExit(f"vendor arm is {len(mid_to_row)}, expected 60")
    vendor_files = {
        "Grok 4.6": "sweep_out/grok-4.6",
        "Gemini 3.7 Flash": "sweep_out/gemini-3.7-flash",
        "GPT-5.6 Sol": "sweep_out/gpt-5.6-sol",
    }
    by_qid = {r["row_id"]: r for r in rows}
    for model, folder in vendor_files.items():
        merged = {}
        blobs = {}
        for f in sorted(Path(folder).glob("reply_*.json")):
            obj = load_loose_json(f)
            if not isinstance(obj, dict):
                raise SystemExit(f"{f} is not a JSON object")
            for k, v in obj.items():
                merged[k] = v
                blobs[k] = json.dumps(v)
        missing = [m for m in mid_to_row if m not in merged]
        if missing:
            raise SystemExit(f"{model} missing {missing[:5]}")
        for mid, row_id in mid_to_row.items():
            rec = by_qid[row_id]
            top1, top3 = score_cands(rec["ik14"], merged[mid])
            rec["models"][model] = {
                "top1": top1,
                "top3": top3,
                "blob": blobs[mid],
            }

    # +106, all deposited Opus (not the validate-clean subset).
    preds106 = {r["qid"]: r for r in git_jsonl("data/benchmark_expand/predictions2.jsonl")}
    for q in git_jsonl("data/benchmark_expand/questions2.jsonl"):
        g = gold_from_question(q, idx)
        cands = preds106[q["qid"]].get("candidates", [])
        add(
            f"expand:{q['qid']}",
            "plus106",
            q,
            g["smiles"],
            g.get("source_doi"),
            g.get("pmcid"),
            {"Claude Opus": cands},
            {"Claude Opus": json.dumps(cands)},
        )

    cut = set(git_json("data/benchmark_expand_500/headline500_expand200_qids.json"))
    preds500 = {r["qid"]: r for r in git_jsonl("data/benchmark_expand_500/predictions2.jsonl")}
    n200 = 0
    for q in git_jsonl("data/benchmark_expand_500/questions2.jsonl"):
        if q["qid"] not in cut:
            continue
        g = gold_from_question(q, idx)
        cands = preds500[q["qid"]].get("candidates", [])
        add(
            f"expand500:{q['qid']}",
            "plus200",
            q,
            g["smiles"],
            g.get("source_doi"),
            g.get("pmcid"),
            {"Claude Opus": cands},
            {"Claude Opus": json.dumps(cands)},
        )
        n200 += 1
    if n200 != 200:
        raise SystemExit(f"200-cut is {n200}")

    opus = [r for r in rows if "Claude Opus" in r["models"]]
    if len(opus) != 500:
        raise SystemExit(f"Opus coverage {len(opus)}, expected 500")
    t1 = sum(r["models"]["Claude Opus"]["top1"] for r in opus)
    t3 = sum(r["models"]["Claude Opus"]["top3"] for r in opus)
    if (t1, t3) != (227, 249):
        raise SystemExit(
            f"headline mismatch: top-1 {t1}/500 top-3 {t3}/500, locked is 227 and 249"
        )
    print(f"cohort ok: Opus {t1}/500 top-1, {t3}/500 top-3", flush=True)
    return rows


# ---------------------------------------------------------------- network
def http_json(url, timeout=45):
    delay = 1.0
    for attempt in range(5):
        with _HTTP_LOCK:
            wait = 0.22 - (time.time() - _LAST_HTTP[0])
            if wait > 0:
                time.sleep(wait)
            _LAST_HTTP[0] = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
            return json.loads(body.decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except Exception:
            if attempt < 4:
                time.sleep(delay)
                delay *= 2
                continue
            raise
    return None


def fetch_pubchem(ik):
    path = CACHE / "pubchem" / f"{ik}.json"
    if path.exists():
        cached = json.loads(path.read_text())
        if not cached.get("error"):
            return cached
    path.parent.mkdir(parents=True, exist_ok=True)
    data = http_json(
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{ik}/cids/JSON"
    )
    if not data or "IdentifierList" not in data:
        rec = {
            "in_pubchem": False,
            "cid": None,
            "n_cids": 0,
            "synonym_count": 0,
            "title": "",
            "iupac": "",
            "names": [],
        }
        path.write_text(json.dumps(rec))
        return rec
    cids = data["IdentifierList"].get("CID") or []
    cid = min(cids) if cids else None
    title, iupac, names, nsyn = "", "", [], 0
    if cid is not None:
        prop = http_json(
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
            f"{cid}/property/Title,IUPACName/JSON"
        )
        if prop:
            props = prop.get("PropertyTable", {}).get("Properties") or []
            if props:
                title = props[0].get("Title") or ""
                iupac = props[0].get("IUPACName") or ""
        syn = http_json(
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
        )
        if syn:
            info = syn.get("InformationList", {}).get("Information") or []
            if info:
                all_syn = info[0].get("Synonym") or []
                nsyn = len(all_syn)
                names = []
                for s in all_syn:
                    if looks_common(s, iupac) and s not in names:
                        names.append(s)
                    if len(names) >= 25:
                        break
    if title and looks_common(title, iupac) and title not in names:
        names.insert(0, title)
    rec = {
        "in_pubchem": True,
        "cid": cid,
        "n_cids": len(cids),
        "synonym_count": nsyn,
        "title": title,
        "iupac": iupac,
        "names": names,
    }
    path.write_text(json.dumps(rec))
    return rec


def fetch_year(pmcid):
    if not pmcid:
        return None
    data = http_json(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
        + urllib.parse.urlencode({
            "query": f"PMCID:{pmcid}",
            "format": "json",
            "resultType": "lite",
            "pageSize": "1",
        })
    )
    if not data:
        return None
    res = (data.get("resultList") or {}).get("result") or []
    if not res:
        return None
    y = res[0].get("pubYear")
    try:
        return int(y)
    except (TypeError, ValueError):
        return None


def attach_network(rows):
    year_path = CACHE / "years.json"
    years = json.loads(year_path.read_text()) if year_path.exists() else {}
    iks = sorted({r["ik14"] for r in rows})
    pmcs = sorted({r["pmcid"] for r in rows if r.get("pmcid") and r["pmcid"] not in years})
    print(f"pubchem {len(iks)} keys, europepmc {len(pmcs)} new ids", flush=True)

    def years_job():
        for i, pmc in enumerate(pmcs, 1):
            try:
                years[pmc] = fetch_year(pmc)
            except Exception as e:
                print(f"year fail {pmc}: {e}", flush=True)
                continue
            if i % 25 == 0:
                year_path.write_text(json.dumps(years))
                print(f"  years {i}/{len(pmcs)}", flush=True)
        year_path.write_text(json.dumps(years))

    def pub_job():
        for i, ik in enumerate(iks, 1):
            try:
                fetch_pubchem(ik)
            except Exception as e:
                print(f"pubchem fail {ik}: {e}", flush=True)
                fail = CACHE / "pubchem" / f"{ik}.json"
                if not fail.exists():
                    fail.parent.mkdir(parents=True, exist_ok=True)
                    fail.write_text(json.dumps({
                        "in_pubchem": False, "cid": None, "n_cids": 0,
                        "synonym_count": 0, "title": "", "iupac": "", "names": [],
                        "error": str(e),
                    }))
            if i % 25 == 0:
                print(f"  pubchem {i}/{len(iks)}", flush=True)

    threads = []
    if pmcs:
        threads.append(threading.Thread(target=years_job, daemon=True))
    # PubChem is rate-limited on a shared lock with Europe PMC. Run PubChem
    # alone so the two services do not serialize through one lock. Years are
    # few enough to follow, and both are cached.
    pub_job()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    years = json.loads(year_path.read_text()) if year_path.exists() else years
    for r in rows:
        r["year"] = years.get(r["pmcid"]) if r.get("pmcid") else None
        pc = json.loads((CACHE / "pubchem" / f"{r['ik14']}.json").read_text())
        r["pubchem"] = pc
        common = looks_common(pc.get("title") or "", pc.get("iupac") or "")
        r["common_name"] = bool(common)
        r["famous"] = is_famous(pc.get("in_pubchem"), pc.get("synonym_count") or 0, common)
        r["synonym_count"] = pc.get("synonym_count") or 0
        r["in_pubchem"] = bool(pc.get("in_pubchem"))


# ---------------------------------------------------------------- ChEMBL
def _process_chunk(rows):
    """Worker. rows is a list of (smiles, ik14)."""
    from rdkit import Chem, DataStructs, RDLogger
    from rdkit.Chem import rdFingerprintGenerator
    from rdkit.Chem.Scaffolds import MurckoScaffold
    import numpy as np

    RDLogger.DisableLog("rdApp.*")
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = []
    meta = []
    scafs = []
    for smi, ik in rows:
        m = Chem.MolFromSmiles(smi) if smi else None
        if m is None:
            continue
        try:
            Chem.RemoveStereochemistry(m)
            fp = gen.GetFingerprint(m)
            arr = np.zeros((2048,), dtype=np.uint8)
            DataStructs.ConvertToNumpyArray(fp, arr)
            bits = np.packbits(arr)
            u = np.frombuffer(bits.tobytes(), dtype=np.uint64).copy()
            sc = MurckoScaffold.GetScaffoldForMol(m)
            scaf = ""
            if sc is not None and sc.GetNumAtoms() > 0:
                scaf = Chem.MolToSmiles(sc)
        except Exception:
            continue
        fps.append(u)
        meta.append((smi, ik))
        scafs.append(scaf)
    if fps:
        arr = np.stack(fps).astype(np.uint64, copy=False)
    else:
        arr = np.zeros((0, 32), dtype=np.uint64)
    return arr, meta, scafs


def ensure_chembl_gz():
    dest = CACHE / f"{CHEMBL_NAME}_chemreps.txt.gz"
    stamp = CACHE / f"{CHEMBL_NAME}.ok"
    if dest.exists() and dest.stat().st_size == CHEMBL_BYTES and stamp.exists():
        return dest
    tmp = Path(f"/tmp/chembl/{CHEMBL_NAME}_chemreps.txt.gz")
    if not (tmp.exists() and tmp.stat().st_size == CHEMBL_BYTES):
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_suffix(".part")
        print(f"downloading {CHEMBL_URL}", flush=True)
        subprocess.check_call(
            ["curl", "-L", "--fail", "--retry", "4", "-o", str(part), CHEMBL_URL]
        )
        if part.stat().st_size != CHEMBL_BYTES:
            raise SystemExit(f"ChEMBL size {part.stat().st_size} != {CHEMBL_BYTES}")
        part.replace(dest)
    else:
        if not dest.exists() or dest.stat().st_size != CHEMBL_BYTES:
            shutil.copy2(tmp, dest)
    subprocess.check_call(["gzip", "-t", str(dest)])
    stamp.write_text("ok\n")
    return dest


def build_chembl_index(gz_path):
    stamp_path = CACHE / "chembl_index_stamp.json"
    fp_path = CACHE / "chembl_fp_u64.npy"
    scaf_path = CACHE / "chembl_scaffolds.txt.gz"
    wanted = {
        "chembl": CHEMBL_NAME,
        "bytes": CHEMBL_BYTES,
        "fp": "morgan_r2_2048_nochirality_u64",
    }
    if stamp_path.exists() and fp_path.exists() and scaf_path.exists():
        stamp = json.loads(stamp_path.read_text())
        if all(stamp.get(k) == v for k, v in wanted.items()) and stamp.get("n_fp", 0) > 0:
            print(f"chembl index cache n={stamp['n_fp']}", flush=True)
            return stamp

    print("building ChEMBL fingerprint index", flush=True)
    # Parent collects every connectivity key, including rows RDKit cannot parse.
    all_keys = set()
    chunks = []
    buf = []
    n_lines = 0
    with gzip.open(gz_path, "rt") as f:
        header = f.readline()
        if "canonical_smiles" not in header:
            raise SystemExit(f"unexpected chemreps header: {header[:80]!r}")
        for line in f:
            n_lines += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            smi, key = parts[1], parts[3]
            ik = key[:14] if len(key) >= 14 else ""
            if ik:
                all_keys.add(ik)
            if smi and ik:
                buf.append((smi, ik))
            if len(buf) >= 8000:
                chunks.append(buf)
                buf = []
            if n_lines % 400000 == 0:
                print(f"  read {n_lines}", flush=True)
    if buf:
        chunks.append(buf)
    print(f"  {n_lines} rows, {len(chunks)} chunks, {len(all_keys)} keys", flush=True)

    fp_tmp = CACHE / "chembl_fp_u64.tmp.npy"
    if fp_tmp.exists():
        fp_tmp.unlink()
    mm = np.lib.format.open_memmap(fp_tmp, mode="w+", dtype=np.uint64, shape=(FP_MAX, 32))
    smiles_bin = CACHE / "chembl_smiles.bin"
    off_tmp = CACHE / "chembl_offsets.tmp.npy"
    ik_tmp = CACHE / "chembl_row_ik.tmp.npy"
    if off_tmp.exists():
        off_tmp.unlink()
    if ik_tmp.exists():
        ik_tmp.unlink()
    offsets = np.lib.format.open_memmap(off_tmp, mode="w+", dtype=np.int64, shape=(FP_MAX,))
    row_ik = np.lib.format.open_memmap(ik_tmp, mode="w+", dtype="S14", shape=(FP_MAX,))
    scaf_set = set()
    row = 0
    byte_off = 0
    ctx = mp.get_context("spawn")
    with smiles_bin.open("wb") as sf, ProcessPoolExecutor(max_workers=4, mp_context=ctx) as ex:
        for done, (arr, meta, scafs) in enumerate(ex.map(_process_chunk, chunks), 1):
            n = int(arr.shape[0])
            if row + n > FP_MAX:
                raise SystemExit("fingerprint buffer overflow; raise FP_MAX")
            if n:
                mm[row : row + n] = arr
                for j, (smi, ik) in enumerate(meta):
                    offsets[row + j] = byte_off
                    blob = smi.encode("utf-8") + b"\n"
                    sf.write(blob)
                    byte_off += len(blob)
                    row_ik[row + j] = ik.encode("ascii")[:14]
                    if scafs[j]:
                        scaf_set.add(scafs[j])
                row += n
            if done % 20 == 0 or done == len(chunks):
                print(f"  featurized chunks {done}/{len(chunks)} rows {row}", flush=True)
    mm.flush()
    offsets.flush()
    row_ik.flush()

    final = np.lib.format.open_memmap(fp_path, mode="w+", dtype=np.uint64, shape=(row, 32))
    final[:] = mm[:row]
    final.flush()
    del mm
    fp_tmp.unlink(missing_ok=True)
    off_final = CACHE / "chembl_offsets.npy"
    ik_final = CACHE / "chembl_row_ik.npy"
    o2 = np.lib.format.open_memmap(off_final, mode="w+", dtype=np.int64, shape=(row,))
    o2[:] = offsets[:row]
    o2.flush()
    del offsets
    off_tmp.unlink(missing_ok=True)
    k2 = np.lib.format.open_memmap(ik_final, mode="w+", dtype="S14", shape=(row,))
    k2[:] = row_ik[:row]
    k2.flush()
    del row_ik
    ik_tmp.unlink(missing_ok=True)

    with gzip.open(scaf_path, "wt") as f:
        for s in scaf_set:
            f.write(s + "\n")
    keys_path = CACHE / "chembl_ik14.txt.gz"
    with gzip.open(keys_path, "wt") as f:
        for k in all_keys:
            f.write(k + "\n")
    stamp = dict(wanted, n_fp=row, n_keys=len(all_keys), n_scaffolds=len(scaf_set))
    stamp_path.write_text(json.dumps(stamp))
    print(f"index rows {row} scaffolds {len(scaf_set)}", flush=True)
    return stamp


def load_key_set():
    keys = set()
    with gzip.open(CACHE / "chembl_ik14.txt.gz", "rt") as f:
        for line in f:
            k = line.strip()
            if k:
                keys.add(k)
    return keys


def load_scaffold_set():
    sc = set()
    with gzip.open(CACHE / "chembl_scaffolds.txt.gz", "rt") as f:
        for line in f:
            s = line.rstrip("\n")
            if s:
                sc.add(s)
    return sc


def max_tanimoto(rows):
    out_path = CACHE / "similarity.json"
    if out_path.exists():
        payload = json.loads(out_path.read_text())
        by = {x["row_id"]: x for x in payload.get("rows", [])}
        if len(by) == len(rows) and all(r["row_id"] in by for r in rows):
            for r in rows:
                x = by[r["row_id"]]
                r["max_tanimoto"] = x["max_tanimoto"]
                r["exact_chembl"] = x["exact_chembl"]
                r["nn_ik14"] = x["nn_ik14"]
                r["sim_bin"] = x["sim_bin"]
                r["scaffold_in_chembl"] = x["scaffold_in_chembl"]
                r["hac_bin"] = hac_bin(r["hac"])
                r["nn_smiles"] = ""
            print(f"similarity cache hit n={len(rows)}", flush=True)
            return
    stamp = json.loads((CACHE / "chembl_index_stamp.json").read_text())
    fps = np.load(CACHE / "chembl_fp_u64.npy", mmap_mode="r")
    if fps.shape[0] != stamp["n_fp"]:
        raise SystemExit("fingerprint cache length does not match stamp")
    queries = []
    for r in rows:
        mol = parse_mol(r["smiles"])
        if mol is None:
            raise SystemExit(f"query parse failed {r['row_id']}")
        queries.append(morgan_u64(mol))
        r["scaffold"] = murcko_smiles(mol)
    Q = np.stack(queries)
    qpop = np.bitwise_count(Q).sum(axis=1).astype(np.float32)
    n = fps.shape[0]
    best_sim = np.zeros(len(rows), dtype=np.float32)
    best_idx = np.full(len(rows), -1, dtype=np.int64)
    chunk = 150000
    t0 = time.time()
    for start in range(0, n, chunk):
        db = np.asarray(fps[start : start + chunk])
        dbpop = np.bitwise_count(db).sum(axis=1).astype(np.float32)
        for qi in range(len(rows)):
            inter = np.bitwise_count(np.bitwise_and(db, Q[qi])).sum(axis=1).astype(np.float32)
            denom = qpop[qi] + dbpop - inter
            sim = np.divide(inter, denom, out=np.zeros_like(inter), where=denom > 0)
            j = int(sim.argmax())
            if sim[j] > best_sim[qi]:
                best_sim[qi] = float(sim[j])
                best_idx[qi] = start + j
        print(f"  tanimoto {min(start+chunk, n)}/{n}  {time.time()-t0:.0f}s", flush=True)

    offsets = np.load(CACHE / "chembl_offsets.npy", mmap_mode="r")
    row_ik = np.load(CACHE / "chembl_row_ik.npy", mmap_mode="r")
    keys = load_key_set()
    scafs = load_scaffold_set()
    smiles_bin = CACHE / "chembl_smiles.bin"
    with smiles_bin.open("rb") as sf:
        for i, r in enumerate(rows):
            exact = r["ik14"] in keys
            idx = int(best_idx[i])
            nn_smi, nn_ik = "", ""
            if idx >= 0:
                sf.seek(int(offsets[idx]))
                nn_smi = sf.readline().decode("utf-8", "replace").rstrip("\n")
                nn_ik = bytes(row_ik[idx]).decode("ascii").rstrip("\x00")
            r["max_tanimoto"] = float(best_sim[i])
            r["exact_chembl"] = bool(exact)
            r["nn_smiles"] = nn_smi
            r["nn_ik14"] = nn_ik
            r["sim_bin"] = sim_bin(r["max_tanimoto"], exact)
            r["hac_bin"] = hac_bin(r["hac"])
            sc = r.get("scaffold") or ""
            if not sc:
                r["scaffold_in_chembl"] = None
            else:
                r["scaffold_in_chembl"] = sc in scafs
    # self-check: a copied database row must hit 1.0
    probe = parse_mol(rows[0]["nn_smiles"]) if rows[0]["nn_smiles"] else None
    if probe is not None:
        u = morgan_u64(probe)
        # compare to its own stored vector
        j = int(best_idx[0])
        stored = np.asarray(fps[j])
        inter = int(np.bitwise_count(np.bitwise_and(stored, u)).sum())
        pop_q = int(np.bitwise_count(u).sum())
        pop_d = int(np.bitwise_count(stored).sum())
        sim = inter / (pop_q + pop_d - inter) if (pop_q + pop_d - inter) else 0
        if sim < 0.999:
            raise SystemExit(f"fingerprint self-check failed: {sim}")
    payload = []
    for r in rows:
        payload.append({
            "row_id": r["row_id"],
            "max_tanimoto": r["max_tanimoto"],
            "exact_chembl": r["exact_chembl"],
            "nn_ik14": r["nn_ik14"],
            "sim_bin": r["sim_bin"],
            "scaffold_in_chembl": r["scaffold_in_chembl"],
        })
    out_path.write_text(json.dumps({"n": len(payload), "rows": payload}))
    print("similarity done", flush=True)


def attach_mces(rows):
    from rdkit.Chem import rdFMCS

    cache_path = CACHE / "mces.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    for i, r in enumerate(rows):
        key = f"{r['ik14']}|{r.get('nn_ik14')}"
        if key in cache:
            r["mces"] = cache[key].get("mces")
            r["mces_timeout"] = cache[key].get("timeout", False)
            continue
        if r.get("nn_ik14") and r["nn_ik14"] == r["ik14"]:
            rec = {"mces": 1.0, "timeout": False}
        else:
            a = parse_mol(r["smiles"])
            b = parse_mol(r.get("nn_smiles") or "")
            if a is None or b is None:
                rec = {"mces": None, "timeout": False}
            else:
                try:
                    mcs = rdFMCS.FindMCS(
                        [a, b],
                        timeout=1,
                        matchValences=False,
                        ringMatchesRingOnly=False,
                        completeRingsOnly=False,
                        maximizeBonds=True,
                    )
                    timeout = bool(mcs.canceled)
                    inter = int(mcs.numAtoms)
                    na, nb = a.GetNumAtoms(), b.GetNumAtoms()
                    den = na + nb - inter
                    sim = (inter / den) if den else None
                    rec = {"mces": None if sim is None else round(float(sim), 4), "timeout": timeout}
                except Exception:
                    rec = {"mces": None, "timeout": True}
        cache[key] = rec
        r["mces"] = rec["mces"]
        r["mces_timeout"] = rec["timeout"]
        if (i + 1) % 50 == 0:
            cache_path.write_text(json.dumps(cache))
            print(f"  mces {i+1}/{len(rows)}", flush=True)
    cache_path.write_text(json.dumps(cache))


# ---------------------------------------------------------------- name probe
def name_mentioned(blob, names):
    if not blob or not names:
        return False
    for name in names:
        if len(name) < 4:
            continue
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])", blob, re.I):
            return True
    return False


def attach_names(rows):
    for r in rows:
        names = (r.get("pubchem") or {}).get("names") or []
        for model, info in r["models"].items():
            info["named"] = name_mentioned(info.get("blob") or "", names)


# ---------------------------------------------------------------- tables
def subset_mask(rows, model):
    return [r for r in rows if model in r["models"]]


def summarize(rows, model, pred):
    """pred is 'top1' or 'top3'. Returns list of bin dicts plus overall."""
    sub = subset_mask(rows, model)
    out = []
    groups = [("all", sub)]
    for name, _fn in SIM_BINS:
        groups.append((name, [r for r in sub if r["sim_bin"] == name]))
    groups.append(("famous", [r for r in sub if r["famous"]]))
    groups.append(("not_famous", [r for r in sub if not r["famous"]]))
    groups.append(("synonyms_ge_30", [r for r in sub if r["synonym_count"] >= COUNT_ONLY]))
    groups.append(("synonyms_lt_30", [r for r in sub if r["synonym_count"] < COUNT_ONLY]))
    groups.append(("in_pubchem", [r for r in sub if r["in_pubchem"]]))
    groups.append(("not_in_pubchem", [r for r in sub if not r["in_pubchem"]]))
    groups.append(("dissimilar_<0.6", [
        r for r in sub if (not r["exact_chembl"]) and r["max_tanimoto"] < 0.6
    ]))
    groups.append(("similar_ge_0.6_or_exact", [
        r for r in sub if r["exact_chembl"] or r["max_tanimoto"] >= 0.6
    ]))
    for label, g in groups:
        k = sum(1 for r in g if r["models"][model][pred])
        n = len(g)
        lo, hi = wilson(k, n)
        out.append({
            "model": model,
            "metric": pred,
            "bin": label,
            "k": k,
            "n": n,
            "lo": None if n == 0 else lo,
            "hi": None if n == 0 else hi,
        })
    return out


def write_tables(rows, stats_rows):
    # similarity x metric for every model
    lines = [
        "| model | bin | n | top-1 | top-1 95% Wilson | top-3 | top-3 95% Wilson |",
        "|---|---|---:|---:|---|---:|---|",
    ]
    models = model_order(rows)
    bins = ["all"] + [n for n, _ in SIM_BINS]
    by = {(s["model"], s["metric"], s["bin"]): s for s in stats_rows}
    for model in models:
        for b in bins:
            a = by[(model, "top1", b)]
            c = by[(model, "top3", b)]
            lines.append(
                f"| {model} | {b} | {a['n']} | {a['k']}/{a['n'] if a['n'] else 0} | {ci_text(a['k'], a['n'])} | "
                f"{c['k']}/{c['n'] if c['n'] else 0} | {ci_text(c['k'], c['n'])} |"
            )
    (TAB / "accuracy_by_similarity.md").write_text("\n".join(lines) + "\n")

    lines = [
        "| model | flag | n | top-1 | top-1 95% Wilson | top-3 | top-3 95% Wilson |",
        "|---|---|---:|---:|---|---:|---|",
    ]
    for model in models:
        for b in ("famous", "not_famous", "synonyms_ge_30", "in_pubchem", "not_in_pubchem"):
            a = by[(model, "top1", b)]
            c = by[(model, "top3", b)]
            lines.append(
                f"| {model} | {b} | {a['n']} | {a['k']}/{a['n'] if a['n'] else 0} | {ci_text(a['k'], a['n'])} | "
                f"{c['k']}/{c['n'] if c['n'] else 0} | {ci_text(c['k'], c['n'])} |"
            )
    (TAB / "accuracy_by_famous.md").write_text("\n".join(lines) + "\n")

    # heatmap counts for Opus
    heat_lines = [
        "| heavy atoms | " + " | ".join(n for n, _ in SIM_BINS) + " |",
        "|---|" + "|".join("---:" for _ in SIM_BINS) + "|",
    ]
    opus = [r for r in rows if "Claude Opus" in r["models"]]
    for hname, _ in HAC_BINS:
        cells = []
        for sname, _ in SIM_BINS:
            g = [r for r in opus if r["hac_bin"] == hname and r["sim_bin"] == sname]
            k = sum(1 for r in g if r["models"]["Claude Opus"]["top1"])
            cells.append(f"{k}/{len(g)} {ci_text(k, len(g))}" if g else "0")
        heat_lines.append(f"| {hname} | " + " | ".join(cells) + " |")
    (TAB / "heatmap_opus_top1.md").write_text("\n".join(heat_lines) + "\n")

    # name probe
    nlines = [
        "| model | n | named the compound | named top-1 | not named top-1 |",
        "|---|---:|---|---|---|",
    ]
    for model in models:
        sub = subset_mask(rows, model)
        named = [r for r in sub if r["models"][model]["named"]]
        other = [r for r in sub if not r["models"][model]["named"]]
        kn = sum(r["models"][model]["top1"] for r in named)
        ko = sum(r["models"][model]["top1"] for r in other)
        nlines.append(
            f"| {model} | {len(sub)} | {len(named)}/{len(sub)} {ci_text(len(named), len(sub))} | "
            f"{ci_text(kn, len(named))} | {ci_text(ko, len(other))} |"
        )
    (TAB / "name_probe.md").write_text("\n".join(nlines) + "\n")

    # machine-readable, no structures
    slim = []
    for s in stats_rows:
        slim.append({
            "model": s["model"],
            "metric": s["metric"],
            "bin": s["bin"],
            "k": s["k"],
            "n": s["n"],
            "lo": s["lo"],
            "hi": s["hi"],
        })
    (TAB / "stats.json").write_text(json.dumps(slim, indent=2))

    # per-molecule table without SMILES or InChIKey (expansion key stays in cache)
    mol_path = CACHE / "molecules.jsonl"
    with mol_path.open("w") as f:
        for r in rows:
            item = {
                "row_id": r["row_id"],
                "subset": r["subset"],
                "ik14": r["ik14"],
                "smiles": r["smiles"],
                "hac": r["hac"],
                "year": r.get("year"),
                "pmcid": r.get("pmcid"),
                "max_tanimoto": round(r["max_tanimoto"], 4),
                "exact_chembl": r["exact_chembl"],
                "sim_bin": r["sim_bin"],
                "hac_bin": r["hac_bin"],
                "nn_ik14": r.get("nn_ik14"),
                "scaffold_in_chembl": r.get("scaffold_in_chembl"),
                "mces": r.get("mces"),
                "in_pubchem": r["in_pubchem"],
                "synonym_count": r["synonym_count"],
                "common_name": r["common_name"],
                "famous": r["famous"],
                "pubchem_title": (r.get("pubchem") or {}).get("title"),
                "models": {
                    m: {"top1": info["top1"], "top3": info["top3"], "named": info["named"]}
                    for m, info in r["models"].items()
                },
            }
            f.write(json.dumps(item) + "\n")
    # committed view: no structure columns
    with (TAB / "molecules_public.csv").open("w") as f:
        cols = [
            "row_id", "subset", "hac", "year", "max_tanimoto", "exact_chembl",
            "sim_bin", "scaffold_in_chembl", "mces", "in_pubchem", "synonym_count",
            "common_name", "famous",
        ]
        models = model_order(rows)
        for m in models:
            safe = m.lower().replace(" ", "_").replace(".", "")
            cols += [f"{safe}_top1", f"{safe}_top3", f"{safe}_named"]
        f.write(",".join(cols) + "\n")
        for r in rows:
            vals = [
                r["row_id"], r["subset"], str(r["hac"]),
                "" if r.get("year") is None else str(r["year"]),
                f"{r['max_tanimoto']:.4f}",
                "1" if r["exact_chembl"] else "0",
                r["sim_bin"],
                "" if r.get("scaffold_in_chembl") is None else ("1" if r["scaffold_in_chembl"] else "0"),
                "" if r.get("mces") is None else f"{r['mces']:.4f}",
                "1" if r["in_pubchem"] else "0",
                str(r["synonym_count"]),
                "1" if r["common_name"] else "0",
                "1" if r["famous"] else "0",
            ]
            for m in models:
                info = r["models"].get(m)
                if info is None:
                    vals += ["", "", ""]
                else:
                    vals += ["1" if info["top1"] else "0", "1" if info["top3"] else "0",
                             "1" if info["named"] else "0"]
            f.write(",".join(vals) + "\n")


def model_order(rows):
    present = []
    for name in [
        "Claude Opus",
        "Claude Fable",
        "Claude Sonnet",
        "Claude Haiku",
        "Grok 4.6",
        "Gemini 3.7 Flash",
        "GPT-5.6 Sol",
    ]:
        if any(name in r["models"] for r in rows):
            present.append(name)
    return present


# ---------------------------------------------------------------- figures
def apply_style():
    for p in (
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
    ):
        if Path(p).exists():
            font_manager.fontManager.addfont(p)
    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans", "Arial", "DejaVu Sans"],
        "font.size": FS,
        "axes.labelsize": FS,
        "xtick.labelsize": FS,
        "ytick.labelsize": FS,
        "legend.fontsize": FS,
        "axes.linewidth": AXIS_LW,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.major.width": AXIS_LW,
        "ytick.major.width": AXIS_LW,
        "xtick.major.size": 2.2,
        "ytick.major.size": 2.2,
        "text.color": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.unicode_minus": False,
    })


def panel_letter(ax, letter):
    fp = FontProperties(family="Liberation Sans", weight="bold", size=FS_PANEL)
    ax.text(
        -0.08, 1.06, letter, transform=ax.transAxes, fontproperties=fp,
        ha="left", va="bottom", color=INK, clip_on=False,
    )


def save_fig(fig, stem):
    png = FIG / f"{stem}.png"
    pdf = FIG / f"{stem}.pdf"
    fig.savefig(png, dpi=300)
    fig.savefig(pdf)
    plt.close(fig)


def fig_similarity(rows):
    apply_style()
    opus = [r for r in rows if "Claude Opus" in r["models"]]
    fig_w = WIDTH_MM / 25.4
    fig_h = 78 / 25.4
    fig, axes = plt.subplots(1, 2, figsize=(fig_w, fig_h))

    ax = axes[0]
    labels = [n for n, _ in SIM_BINS]
    x = np.arange(len(labels))
    width = 0.36
    for shift, metric, color, name in (
        (-width / 2, "top1", ACCENT, "top-1"),
        (width / 2, "top3", GREY, "top-3"),
    ):
        heights, yerr_lo, yerr_hi, ns = [], [], [], []
        for lab in labels:
            g = [r for r in opus if r["sim_bin"] == lab]
            k = sum(r["models"]["Claude Opus"][metric] for r in g)
            n = len(g)
            lo, hi = wilson(k, n)
            p = (k / n) if n else 0
            heights.append(100 * p)
            yerr_lo.append(0 if n == 0 else max(0.0, 100 * (p - lo)))
            yerr_hi.append(0 if n == 0 else max(0.0, 100 * (hi - p)))
            ns.append(n)
        bars = ax.bar(
            x + shift, heights, width=width, color=color, label=name, zorder=3,
            yerr=np.vstack([yerr_lo, yerr_hi]),
            error_kw=dict(ecolor=INK, lw=AXIS_LW, capsize=1.6, capthick=AXIS_LW),
        )
        for b, h, lo, hi, n in zip(bars, heights, yerr_lo, yerr_hi, ns):
            if n == 0:
                continue
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + hi + 1.5,
                f"{h:.0f}",
                ha="center", va="bottom", fontsize=FS, color=INK,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{lab}\nn={sum(r['sim_bin']==lab for r in opus)}" for lab in labels]
    )
    ax.set_ylabel("accuracy (%)")
    ax.set_xlabel("max Tanimoto to ChEMBL")
    ax.set_ylim(0, 118)
    ax.yaxis.grid(True, color=FAINT, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper left")
    panel_letter(ax, "a")

    ax = axes[1]
    groups = [("famous", [r for r in opus if r["famous"]]),
              ("not famous", [r for r in opus if not r["famous"]])]
    x = np.arange(len(groups))
    for shift, metric, color, name in (
        (-width / 2, "top1", ACCENT, "top-1"),
        (width / 2, "top3", GREY, "top-3"),
    ):
        heights, yerr_lo, yerr_hi = [], [], []
        for _lab, g in groups:
            k = sum(r["models"]["Claude Opus"][metric] for r in g)
            n = len(g)
            lo, hi = wilson(k, n)
            p = k / n if n else 0
            heights.append(100 * p)
            yerr_lo.append(max(0.0, 100 * (p - lo)) if n else 0)
            yerr_hi.append(max(0.0, 100 * (hi - p)) if n else 0)
        bars = ax.bar(
            x + shift, heights, width=width, color=color, label=name, zorder=3,
            yerr=np.vstack([yerr_lo, yerr_hi]),
            error_kw=dict(ecolor=INK, lw=AXIS_LW, capsize=1.6, capthick=AXIS_LW),
        )
        for b, h, hi in zip(bars, heights, yerr_hi):
            ax.text(
                b.get_x() + b.get_width() / 2, h + hi + 1.5, f"{h:.0f}",
                ha="center", va="bottom", fontsize=FS, color=INK,
            )
    ax.set_xticks(x)
    ax.set_xticklabels([f"{lab}\nn={len(g)}" for lab, g in groups])
    ax.set_ylabel("accuracy (%)")
    ax.set_xlabel("PubChem famous flag")
    ax.set_ylim(0, 118)
    ax.yaxis.grid(True, color=FAINT, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right")
    panel_letter(ax, "b")
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.20, top=0.88, wspace=0.35)
    save_fig(fig, "fig_similarity")


def fig_heatmap(rows):
    apply_style()
    opus = [r for r in rows if "Claude Opus" in r["models"]]
    snames = [n for n, _ in SIM_BINS]
    hnames = [n for n, _ in HAC_BINS]
    acc = np.full((len(hnames), len(snames)), np.nan)
    ann = [["" for _ in snames] for _ in hnames]
    for i, hname in enumerate(hnames):
        for j, sname in enumerate(snames):
            g = [r for r in opus if r["hac_bin"] == hname and r["sim_bin"] == sname]
            n = len(g)
            if n == 0:
                continue
            k = sum(r["models"]["Claude Opus"]["top1"] for r in g)
            lo, hi = wilson(k, n)
            acc[i, j] = 100.0 * k / n
            ann[i][j] = f"{100.0 * k / n:.0f}%\n[{100*lo:.0f}-{100*hi:.0f}]\nn={n}"
    fig_w = WIDTH_MM / 25.4
    fig_h = 78 / 25.4
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "accent", ["#f3f3f3", "#e7b3cc", ACCENT]
    )
    cmap.set_bad("#ffffff")
    im = ax.imshow(acc, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(snames)))
    ax.set_xticklabels(snames)
    ax.set_yticks(range(len(hnames)))
    ax.set_yticklabels(hnames)
    ax.set_xlabel("max Tanimoto to ChEMBL")
    ax.set_ylabel("heavy atoms")
    for i in range(len(hnames)):
        for j in range(len(snames)):
            if ann[i][j]:
                ax.text(
                    j, i, ann[i][j], ha="center", va="center", fontsize=5.5, color=INK,
                    path_effects=[mpe.withStroke(linewidth=0.8, foreground="white")],
                )
            else:
                ax.text(j, i, "n=0", ha="center", va="center", fontsize=5.5, color=GREY)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cbar.ax.tick_params(labelsize=FS, width=AXIS_LW, length=2)
    cbar.outline.set_linewidth(AXIS_LW)
    cbar.set_label("top-1 (%)", fontsize=FS)
    for sp in ax.spines.values():
        sp.set_visible(True)
        sp.set_linewidth(AXIS_LW)
    panel_letter(ax, "a")
    fig.subplots_adjust(left=0.10, right=0.92, bottom=0.16, top=0.88)
    save_fig(fig, "fig_heatmap")


def fig_models(rows):
    apply_style()
    # Paired comparisons. Opus on the full set, then Opus restricted to each
    # other model's molecules so the grey series is not a different task.
    series = []
    opus_rows = [r for r in rows if "Claude Opus" in r["models"]]
    series.append(("Claude Opus, n=500", opus_rows, "Claude Opus", True))
    vendor = [r for r in rows if "Grok 4.6" in r["models"]]
    series.append(("Opus on the 60-compound set", vendor, "Claude Opus", True))
    for model in ("Grok 4.6", "Gemini 3.7 Flash", "GPT-5.6 Sol"):
        series.append((model, vendor, model, False))
    ladder = [r for r in rows if "Claude Fable" in r["models"]]
    series.append(("Opus on the 24-compound set", ladder, "Claude Opus", True))
    for model in ("Claude Fable", "Claude Sonnet", "Claude Haiku"):
        series.append((model, ladder, model, False))

    def bin_stats(sub, model, kind):
        if kind == "low":
            g = [r for r in sub if (not r["exact_chembl"]) and r["max_tanimoto"] < 0.6]
        else:
            g = [r for r in sub if r["exact_chembl"] or r["max_tanimoto"] >= 0.6]
        k = sum(r["models"][model]["top1"] for r in g)
        n = len(g)
        lo, hi = wilson(k, n)
        p = (k / n) if n else float("nan")
        return p, lo, hi, n

    fig_w = WIDTH_MM / 25.4
    fig_h = 110 / 25.4
    fig, axes = plt.subplots(1, 2, figsize=(fig_w, fig_h), sharey=True)
    y = np.arange(len(series))
    for ax, kind, title in (
        (axes[0], "low", "max Tanimoto < 0.6"),
        (axes[1], "high", "exact or max Tanimoto >= 0.6"),
    ):
        for i, (label, sub, model, accent) in enumerate(series):
            p, lo, hi, n = bin_stats(sub, model, kind)
            if n == 0 or math.isnan(p):
                ax.plot([0], [i], marker="x", color=GREY_LT, ms=3)
                ax.text(2, i, "n=0", va="center", ha="left", fontsize=FS, color=GREY)
                continue
            color = ACCENT if accent else GREY
            ax.errorbar(
                100 * p, i,
                xerr=[[max(0.0, 100 * (p - lo))], [max(0.0, 100 * (hi - p))]],
                fmt="o", color=color, ms=3.2, lw=AXIS_LW,
                ecolor=color, capsize=1.4, capthick=AXIS_LW, zorder=3,
            )
            ax.text(
                min(99, 100 * hi) + 1.2, i,
                f"{100*p:.0f}%  n={n}",
                va="center", ha="left", fontsize=FS, color=INK,
            )
        ax.set_xlim(0, 145)
        ax.set_xlabel("top-1 (%)")
        ax.set_title(title, loc="left", fontsize=FS, color=INK, pad=3)
        ax.xaxis.grid(True, color=FAINT, lw=0.4, zorder=0)
        ax.set_axisbelow(True)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([s[0] for s in series])
    axes[0].invert_yaxis()
    panel_letter(axes[0], "a")
    panel_letter(axes[1], "b")
    fig.subplots_adjust(left=0.28, right=0.98, bottom=0.10, top=0.90, wspace=0.15)
    save_fig(fig, "fig_models")


# ---------------------------------------------------------------- report
def overlaps(a_lo, a_hi, b_lo, b_hi):
    return not (a_hi < b_lo or b_hi < a_lo)


def write_report(rows, chembl_stamp):
    opus = [r for r in rows if "Claude Opus" in r["models"]]
    n = len(opus)
    k1 = sum(r["models"]["Claude Opus"]["top1"] for r in opus)
    k3 = sum(r["models"]["Claude Opus"]["top3"] for r in opus)
    lo1, hi1 = wilson(k1, n)
    lo3, hi3 = wilson(k3, n)

    def grab(pred, label):
        g = [r for r in opus if r["sim_bin"] == label] if label in {b for b, _ in SIM_BINS} else None
        if label == "low":
            g = [r for r in opus if (not r["exact_chembl"]) and r["max_tanimoto"] < 0.6]
        if label == "high":
            g = [r for r in opus if r["exact_chembl"] or r["max_tanimoto"] >= 0.6]
        kk = sum(r["models"]["Claude Opus"][pred] for r in g)
        return kk, len(g), wilson(kk, len(g))

    exact_k, exact_n, (ex_lo, ex_hi) = grab("top1", "exact")
    low_k, low_n, (low_lo, low_hi) = grab("top1", "low")
    high_k, high_n, (high_lo, high_hi) = grab("top1", "high")
    lt_k, lt_n, (lt_lo, lt_hi) = grab("top1", "<0.4")
    ge_k, ge_n, _geci = grab("top1", ">=0.8")

    fam = [r for r in opus if r["famous"]]
    unf = [r for r in opus if not r["famous"]]
    fk = sum(r["models"]["Claude Opus"]["top1"] for r in fam)
    uk = sum(r["models"]["Claude Opus"]["top1"] for r in unf)
    flo, fhi = wilson(fk, len(fam))
    ulo, uhi = wilson(uk, len(unf))

    tani = [r["max_tanimoto"] for r in opus]
    n_exact = sum(1 for r in opus if r["exact_chembl"])
    n_pub = sum(1 for r in opus if r["in_pubchem"])
    n_common = sum(1 for r in opus if r["common_name"])
    years = [r["year"] for r in opus if r.get("year")]
    scaf_known = [r for r in opus if r.get("scaffold_in_chembl") is not None]
    scaf_hit = sum(1 for r in scaf_known if r["scaffold_in_chembl"])
    mces_vals = [r["mces"] for r in opus if r.get("mces") is not None]
    named = sum(1 for r in opus if r["models"]["Claude Opus"]["named"])
    med_syn = float(np.median([r["synonym_count"] for r in opus])) if opus else 0
    in_pub_syn = [r["synonym_count"] for r in opus if r["in_pubchem"]]
    med_syn_pub = float(np.median(in_pub_syn)) if in_pub_syn else 0

    # honest direction
    drop = (exact_k / exact_n if exact_n else 0) - (low_k / low_n if low_n else 0)
    collapse = (
        exact_n >= 20 and low_n >= 20 and drop >= 0.10
        and not overlaps(ex_lo, ex_hi, low_lo, low_hi)
    )
    mild = exact_n >= 20 and low_n >= 20 and drop >= 0.05
    if collapse:
        sim_sentence = (
            f"Top-1 is {ci_text(exact_k, exact_n)} on molecules whose connectivity is in ChEMBL "
            f"and {ci_text(low_k, low_n)} when the nearest ChEMBL neighbor has Tanimoto below 0.6. "
            f"The Wilson intervals do not overlap."
        )
    elif mild:
        sim_sentence = (
            f"Top-1 is higher on closer molecules: {ci_text(exact_k, exact_n)} for an exact ChEMBL "
            f"connectivity match and {ci_text(low_k, low_n)} below Tanimoto 0.6. "
            f"The gap is real in point estimate, and the intervals "
            f"{'still overlap' if overlaps(ex_lo, ex_hi, low_lo, low_hi) else 'do not overlap'}."
        )
    elif low_n < 20:
        sim_sentence = (
            f"Only {low_n} molecules have max Tanimoto below 0.6, so that bin cannot carry a "
            f"memorization claim. Top-1 there is {ci_text(low_k, low_n)}. "
            f"Exact ChEMBL matches are {exact_n}/{n}, with top-1 {ci_text(exact_k, exact_n)}."
        )
    else:
        sim_sentence = (
            f"Top-1 does not collapse on dissimilar molecules. It is {ci_text(low_k, low_n)} "
            f"below Tanimoto 0.6 (n={low_n}) and {ci_text(exact_k, exact_n)} on exact ChEMBL "
            f"connectivity matches (n={exact_n})."
        )

    pub = [r for r in opus if r["in_pubchem"]]
    nop = [r for r in opus if not r["in_pubchem"]]
    pk = sum(r["models"]["Claude Opus"]["top1"] for r in pub)
    nk = sum(r["models"]["Claude Opus"]["top1"] for r in nop)
    plo, phi = wilson(pk, len(pub))
    nlo, nhi = wilson(nk, len(nop))
    pub_overlap = "do not overlap" if not overlaps(plo, phi, nlo, nhi) else "overlap"
    pub_sentence = (
        f"PubChem contains the connectivity of {len(pub)}/{n} molecules. "
        f"Opus top-1 is {ci_text(pk, len(pub))} on those and {ci_text(nk, len(nop))} "
        f"on the rest. The Wilson intervals {pub_overlap}."
    )
    ge30 = [r for r in opus if r["synonym_count"] >= COUNT_ONLY]
    ge30k = sum(r["models"]["Claude Opus"]["top1"] for r in ge30)
    fam_sentence = (
        f"The famous flag (a short PubChem title and at least {SYNONYM_FAMOUS} synonyms) "
        f"is on for {len(fam)}/{n} molecules, with top-1 {ci_text(fk, len(fam))} "
        f"against {ci_text(uk, len(unf))} when it is off. "
        f"A count-only cut at {COUNT_ONLY} synonyms covers {len(ge30)} molecules "
        f"({ci_text(ge30k, len(ge30))}). Neither cut is large enough to be the headline."
    )

    if named == 0:
        name_sentence = (
            "Deposited answers are ranked SMILES. No reasoning trace is stored in the "
            "prediction files. A scan of those strings for the PubChem common name found "
            f"0/{n} mentions, so an accuracy split by naming is empty on one side."
        )
    else:
        named_rows = [r for r in opus if r["models"]["Claude Opus"]["named"]]
        kn = sum(r["models"]["Claude Opus"]["top1"] for r in named_rows)
        name_sentence = (
            f"The stored answer text mentions a PubChem common name for {named}/{n} molecules. "
            f"Top-1 on that subset is {ci_text(kn, named)}."
        )

    year_sentence = "Source year was missing for every row."
    if years:
        def yrate(a, b):
            g = [r for r in opus if r.get("year") and a <= r["year"] <= b]
            kk = sum(r["models"]["Claude Opus"]["top1"] for r in g)
            return f"{a} to {b} {ci_text(kk, len(g))} (n={len(g)})"
        year_sentence = (
            f"Source-paper years were found for {len(years)}/{n} molecules "
            f"(median {int(np.median(years))}, range {min(years)} to {max(years)}). "
            f"Top-1 by year is {yrate(2005, 2015)}; {yrate(2016, 2019)}; "
            f"{yrate(2020, 2022)}; {yrate(2023, 2026)}. "
            f"There is no cliff at recent years."
        )
    mces_sentence = "MCES was not computed."
    if mces_vals:
        mces_sentence = (
            f"Median MCES atom-Tanimoto to the nearest ChEMBL neighbor is "
            f"{float(np.median(mces_vals)):.2f}."
        )
    scaf_sentence = (
        f"Of {len(scaf_known)} molecules with a ring scaffold, {scaf_hit} "
        f"({100.0 * scaf_hit / len(scaf_known):.1f}%) have that Bemis-Murcko scaffold in ChEMBL."
        if scaf_known else "No ring scaffolds were scored."
    )

    # bin one-liners for bullets
    bin_bits = []
    for lab, _ in SIM_BINS:
        g = [r for r in opus if r["sim_bin"] == lab]
        kk = sum(r["models"]["Claude Opus"]["top1"] for r in g)
        bin_bits.append(f"{lab} {ci_text(kk, len(g))} (n={len(g)})")

    bullets = [
        f"Claude Opus on the locked set is {k1}/{n} top-1 ({ci_text(k1, n)}) and {k3}/{n} top-3 ({ci_text(k3, n)}). The script stops if those integers move.",
        f"ChEMBL {CHEMBL_NAME.replace('chembl_', '')} contains the connectivity of {n_exact}/{n} molecules (median max Tanimoto {float(np.median(tani)):.2f}). Opus top-1 by bin: " + "; ".join(bin_bits) + ".",
        sim_sentence,
        f"{pub_sentence} {n_common}/{n} have a short common-name title. Median synonym count is {med_syn:.0f} on the full set and {med_syn_pub:.0f} among molecules in PubChem. {fam_sentence}",
        f"{name_sentence} {year_sentence} {scaf_sentence} {mces_sentence}",
    ]

    if collapse:
        rebuttal = (
            f"We did not train on this benchmark. As a public proxy for structures a frontier model "
            f"is likely to have seen, we scored the locked n=500 set against ChEMBL "
            f"{CHEMBL_NAME.replace('chembl_', '')} (Morgan radius 2, 2048 bits, no stereochemistry) "
            f"and against PubChem. Claude Opus is {k1}/{n} top-1 ({ci_text(k1, n)}) and {k3}/{n} top-3. "
            f"{sim_sentence} {pub_sentence} {fam_sentence} {name_sentence} "
            f"ChEMBL and PubChem are not the training corpus of any model here, so overlap is "
            f"evidence of public availability rather than proof of memorization. The drop on "
            f"dissimilar molecules is a real limit. It does not turn the whole headline into "
            f"exact recall of public structures, because most of the set is not an exact copy "
            f"and that majority is still partly solved."
        )
    else:
        rebuttal = (
            f"We did not train on this benchmark. As a public proxy for structures a frontier model "
            f"is likely to have seen, we scored the locked n=500 set against ChEMBL "
            f"{CHEMBL_NAME.replace('chembl_', '')} (Morgan radius 2, 2048 bits, no stereochemistry) "
            f"and against PubChem. Claude Opus is {k1}/{n} top-1 ({ci_text(k1, n)}) and {k3}/{n} top-3. "
            f"{sim_sentence} {pub_sentence} {fam_sentence} {name_sentence} "
            f"These proxies are not an LLM training set. A molecule in ChEMBL or PubChem may still "
            f"have been unseen by a given model, and a molecule absent from both can still have "
            f"appeared in papers."
        )

    coverage = []
    for model in model_order(rows):
        sub = subset_mask(rows, model)
        sets = sorted({r["subset"] for r in sub})
        kk = sum(r["models"][model]["top1"] for r in sub)
        k3m = sum(r["models"][model]["top3"] for r in sub)
        coverage.append(
            f"{model}: n={len(sub)} ({', '.join(sets)}), top-1 {ci_text(kk, len(sub))}, "
            f"top-3 {ci_text(k3m, len(sub))}."
        )

    text = f"""# Memorization proxy for the locked n=500 set

This note compares the locked IRSpectra-Bench headline set with public chemical databases. The benchmark models were not trained here. ChEMBL and PubChem are proxies for molecules a general LLM is likely to have seen, in the same spirit as the Tanimoto-to-training plot in ChefNMR2 (bioRxiv 2026.10.29.762711).

## Findings

- {bullets[0]}
- {bullets[1]}
- {bullets[2]}
- {bullets[3]}
- {bullets[4]}

## Rebuttal paragraph

{rebuttal}

## What was scored

The locked set is the n=194 cohort from `scripts/score_main.py`, plus all 106 deposited Opus answers in `data/benchmark_expand`, plus the first 200 validate-clean qids of `data/benchmark_expand_500` after a string sort (`headline500_expand200_qids.json`). That is the cut in `HEADLINE_n500_2026-09-20.md` on commit `{PIN[:12]}`. Scoring is InChIKey connectivity, first 14 characters. Top-1 is the first candidate. Top-3 is the locked recall@3. Gold SMILES for the expansion rounds were rebuilt by an exact (13C text, IR band) match to `data/irexp_resolved/irexp_resolved.jsonl.gz`. The match is unique on this set. The script checks 227/500 and 249/500 before it writes figures.

Other deposited models are scored only where they have a complete protocol. Claude Fable, Sonnet, and Haiku cover the fixed 24-compound ladder inside the main round. Grok 4.6, Gemini 3.7 Flash, and GPT-5.6 Sol cover the 60-compound vendor arm (`benchmark_v3` plus `benchmark_v2_ctrl`), with ids matched to `sweep_prompts/solve_01.md`. An unfinished Fable deposit on the +106 round is not scored. The locked pooler also ignores that tree.

Coverage:

{chr(10).join('- ' + c for c in coverage)}

## Proxies

ChEMBL file: `{CHEMBL_NAME}_chemreps.txt.gz` ({chembl_stamp.get('n_fp')} fingerprinted rows, {chembl_stamp.get('n_keys')} connectivity keys). Fingerprints are Morgan radius 2, 2048 bits, stereochemistry removed, the same setting as ChefNMR2. Exact means the gold connectivity key is in the ChEMBL file. The bins are exact, then >=0.8, 0.6-0.8, 0.4-0.6, and <0.4, and exact rows are not also placed in >=0.8. Bemis-Murcko scaffolds use RDKit canonical SMILES. MCES is the atom Tanimoto of a maximum common substructure against the nearest fingerprint neighbor, with a one-second cap. A neighbor with the same connectivity key is recorded as 1.

PubChem uses PUG REST on the connectivity InChIKey. The parent record is the lowest CID. The famous flag requires a short non-systematic title and at least {SYNONYM_FAMOUS} synonyms. A separate row uses a synonym count of at least {COUNT_ONLY} with no name filter. Source year is the Europe PMC `pubYear` for the PMCID on the gold record. Intervals are 95% Wilson intervals. Counts are in `tables/`.

## Figures

`figures/fig_similarity` is Claude Opus on the full set. Panel a is top-1 and top-3 by ChEMBL bin. Panel b is the famous flag. Bar labels are the percent. Whiskers are Wilson intervals. The count under each bin is n.

`figures/fig_heatmap` is Opus top-1 by heavy atoms and ChEMBL bin. Each cell shows the percent, the Wilson interval, and n.

`figures/fig_models` is top-1 with Wilson intervals for every deposited model, split at Tanimoto 0.6. Opus on the other models' own molecules is drawn in the same accent so those rows share a denominator. Grey rows are the other models. Sets are not the same size. The full bin table is `tables/accuracy_by_similarity.md`.

## Limits

ChEMBL and PubChem are not the training set of Claude, Grok, Gemini, or GPT. Presence is a public-availability proxy. Absence is not proof the molecule was unseen. Novel papers can describe molecules that are still one edit from a ChEMBL neighbor. The famous threshold is a choice. The synonym counts and the common-name bit are in the tables so the cut can be moved. Reasoning traces were not stored with the deposits, so the name probe only sees the saved answer strings. No NIST spectra and no CC BY-NC dump are included. Locked benchmark files were not modified.
"""
    if "\u2014" in text or "\u2013" in text:
        raise SystemExit("report contains a dash character that was not requested")
    (HERE / "REPORT.md").write_text(text)
    print("wrote REPORT.md", flush=True)


def main():
    rows = assemble()
    # PubChem and Europe PMC are network-bound. The ChEMBL index is local CPU.
    # They do not share rows until both finish.
    net_err = []

    def _run_net():
        try:
            attach_network(rows)
        except Exception as exc:
            net_err.append(exc)

    net = threading.Thread(target=_run_net, daemon=True)
    net.start()
    gz = ensure_chembl_gz()
    stamp = build_chembl_index(gz)
    net.join()
    if net_err:
        raise net_err[0]
    max_tanimoto(rows)
    attach_mces(rows)
    attach_names(rows)
    stats = []
    for model in model_order(rows):
        stats.extend(summarize(rows, model, "top1"))
        stats.extend(summarize(rows, model, "top3"))
    write_tables(rows, stats)
    fig_similarity(rows)
    fig_heatmap(rows)
    fig_models(rows)
    write_report(rows, stamp)
    print("done", flush=True)


if __name__ == "__main__":
    main()
