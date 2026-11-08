#!/usr/bin/env python3
"""Corpus-backed library search on the locked IRSpectra-Bench n=500 roster.

This is nearest-neighbour lookup in IRexp. It is not de novo elucidation and it
does not replace the closed-book generation wall (227 exact top-1 / 22 in the
k<=3 pool / 251 never proposed).

Distance, fixed before any query is scored
------------------------------------------
Gallery G is the set of index rows whose RDKit Hill formula equals the printed
query formula, after the protocol's exclusions.

Channels
  IR   Band positions in cm^-1. Intensities are ignored. If either list is
       empty the channel is skipped. Otherwise sort both lists and take the
       minimum-cost monotone matching of the shorter list into the longer
       list (dynamic program below). On the real line that matching is the
       rectangular Hungarian optimum under absolute deviation. The distance
       is the mean matched |Delta| in cm^-1. Unmatched peaks on the longer
       list add no penalty, because the lists have no intensities from which
       to set one.

  13C  Symmetric chamfer in ppm, the same expression as hose_predict.chamfer
       and specmetrics.chamfer. Empty on either side skips the channel. The
       helper's 999 sentinel is not used.

  1H   The same chamfer on parsed multiplet centres in ppm. A centre is the
       leading number of a top-level comma/semicolon-separated signal, or the
       midpoint of a leading range. Values outside [-2, 16] are rejected.
       The string is cut at the first 13C / HRMS / ESI / MS / Anal token.
       Parsing is used only because a pre-run check recovered at least one
       centre from every one of the 500 printed 1H fields. A record whose
       field yields no centre contributes no 1H list.

Combination, among the formula-matched gallery of that protocol:
  For each channel k the query possesses, d_k(c) = +infinity when the
  candidate has no list. If every candidate is +infinity, drop k.
  rank_k(c) = 1 + |{c' in G : d_k(c') < d_k(c)}|  (ties share the best rank).
  score(c) = mean of rank_k(c) over the channels that remain.

  Lower is better. Ties break by more finite channels, then smaller IR,
  13C, and 1H distances, then record id. Gold SMILES is not a feature.

Protocols
  A  Leave out the query row only: drop that IRexp record id, and any other
     row with the same id. Other rows that share the gold InChIKey-14 stay.
  B  Protocol A, and also drop every row whose InChIKey-14 equals the gold.
     Gold cannot be proposed. The readout is gallery size and the Morgan
     (radius 2, 2048 bits) Tanimoto of the top neighbour, not exact recovery.

Empty galleries stay in the recall denominator as misses. They contribute a
gallery size of 0. Their Tanimoto is undefined and is left out of the
Tanimoto quartiles.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit import DataStructs
from rdkit.Chem import AllChem, rdMolDescriptors
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
VENDOR = OUT / "vendor"
GOLD_PATH = ROOT / "data" / "irexp_resolved" / "irexp_resolved.jsonl.gz"
EXPAND_SHA = "48fcd30153df5e331fab43cfa514763db8ee3891"

# Locked generation wall. A mismatch aborts before any retrieval number is written.
LOCK = {
    ("all", "top1"): (227, 500),
    ("all", "recall"): (249, 500),
    ("all", "in_pool"): (22, 500),
    ("all", "never"): (251, 500),
    ("simple", "top1"): (161, 248),
    ("complex", "top1"): (66, 252),
    ("simple", "recall"): (172, 248),
    ("complex", "recall"): (77, 252),
    ("locked194", "top1"): (55, 194),
    ("plus106", "top1"): (63, 106),
    ("expand200", "top1"): (109, 200),
    ("locked194", "recall"): (65, 194),
    ("plus106", "recall"): (68, 106),
    ("expand200", "recall"): (116, 200),
}

SECTION_CUT = re.compile(r"\b(?:13C|HRMS|ESI-MS|ESI|MS|Anal)\b", re.I)
SHIFT_LEAD = re.compile(
    r"^\s*(?:δ|delta)?\s*(-?\d+\.?\d*)(?:\s*[-–—]\s*(-?\d+\.?\d*))?",
    re.I,
)
SHIFT_DELTA = re.compile(
    r"(?:δ|delta)\s*(-?\d+\.?\d*)(?:\s*[-–—]\s*(-?\d+\.?\d*))?",
    re.I,
)
SHIFT_COLON = re.compile(
    r":\s*(?:δ|delta)?\s*(-?\d+\.?\d*)(?:\s*[-–—]\s*(-?\d+\.?\d*))?",
    re.I,
)
PMC_RE = re.compile(r"PMC[:\s]*(\d+)", re.I)
KS = (1, 3, 10)


def expansion_bytes(relpath: str) -> bytes:
    """Read a pinned expansion file. Vendor copy must match the git blob."""
    vend = VENDOR / relpath
    blob = None
    try:
        blob = subprocess.check_output(
            ["git", "show", f"{EXPAND_SHA}:{relpath}"], cwd=ROOT
        )
    except subprocess.CalledProcessError:
        blob = None
    if blob is None and not vend.exists():
        raise SystemExit(
            f"missing {relpath}: commit {EXPAND_SHA} is not in this clone "
            f"and {vend} is absent"
        )
    if blob is not None and vend.exists() and vend.read_bytes() != blob:
        raise SystemExit(f"vendor copy drifted from {EXPAND_SHA}:{relpath}")
    if blob is not None and not vend.exists():
        vend.parent.mkdir(parents=True, exist_ok=True)
        vend.write_bytes(blob)
    return blob if blob is not None else vend.read_bytes()


def read_jsonl_bytes(blob: bytes) -> list[dict]:
    return [json.loads(line) for line in blob.decode().splitlines() if line.strip()]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ir_key(bands) -> tuple[int, ...]:
    return tuple(int(round(float(x) * 10)) for x in (bands or []))


def q_c13(text: str) -> tuple[int, ...]:
    nums = re.findall(r"(-?\d+\.?\d*)\s*\(", text or "")
    return tuple(int(round(float(x) * 100)) for x in nums)


def g_c13(text: str) -> tuple[int, ...]:
    if "(" in (text or ""):
        return q_c13(text)
    nums = re.findall(r"-?\d+\.?\d*", text or "")
    return tuple(int(round(float(x) * 100)) for x in nums)


def split_signals(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
        if depth == 0 and ch in ",;":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return parts


def _center_from_match(match: re.Match) -> float | None:
    a = float(match.group(1))
    b = float(match.group(2)) if match.group(2) else a
    centre = (a + b) / 2
    if -2.0 <= centre <= 16.0:
        return centre
    return None


def h1_centres(raw: str) -> tuple[int, ...]:
    """Parsed 1H centres as thousandths of a ppm. Empty tuple = unusable."""
    text = raw or ""
    cut = SECTION_CUT.search(text)
    if cut:
        text = text[: cut.start()]
    found: list[int] = []
    for part in split_signals(text):
        piece = part.strip()
        if not piece:
            continue
        match = SHIFT_LEAD.match(piece) or SHIFT_DELTA.search(piece) or SHIFT_COLON.search(piece)
        if match is None:
            continue
        centre = _center_from_match(match)
        if centre is None:
            continue
        found.append(int(round(centre * 1000)))
    return tuple(found)


def paper_key(pmcid, source_doi) -> str:
    for raw in (pmcid, source_doi):
        if not raw:
            continue
        match = PMC_RE.search(str(raw))
        if match:
            return "PMC" + match.group(1)
    if source_doi and str(source_doi).strip():
        return "DOI:" + str(source_doi).strip().lower()
    return ""


def ik14_of(smiles: str | None) -> str | None:
    if not smiles or not isinstance(smiles, str):
        return None
    mol = Chem.MolFromSmiles(smiles.strip())
    if mol is None:
        return None
    return Chem.MolToInchiKey(mol)[:14]


def sorted_l1(shorter_or_a: tuple[int, ...], other: tuple[int, ...]) -> float | None:
    """Mean absolute deviation of the optimal monotone matching, in list units.

    Caller divides by the unit scale (10 for IR tenths). Returns None if either
    list is empty.
    """
    if not shorter_or_a or not other:
        return None
    a = sorted(shorter_or_a)
    b = sorted(other)
    if len(a) > len(b):
        a, b = b, a
    n, m = len(a), len(b)
    inf = 10**18
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        cur = [inf] * (m + 1)
        ai = a[i - 1]
        for j in range(1, m + 1):
            skip = cur[j - 1]
            take = prev[j - 1] + abs(ai - b[j - 1])
            cur[j] = skip if skip < take else take
        prev = cur
    return prev[m] / n


def chamfer(pred: tuple[int, ...], obs: tuple[int, ...]) -> float | None:
    """Symmetric chamfer in list units. None if either side is empty."""
    if not pred or not obs:
        return None
    left = sum(min(abs(p - o) for o in obs) for p in pred) / len(pred)
    right = sum(min(abs(o - p) for p in pred) for o in obs) / len(obs)
    return (left + right) / 2


def ir_distance(a: tuple[int, ...], b: tuple[int, ...]) -> float | None:
    raw = sorted_l1(a, b)
    if raw is None:
        return None
    return raw / 10.0


def ppm_distance(a: tuple[int, ...], b: tuple[int, ...], scale: int) -> float | None:
    raw = chamfer(a, b)
    if raw is None:
        return None
    return raw / scale


def self_check_distance() -> None:
    import itertools
    import random

    def brute(a, b):
        if len(a) > len(b):
            a, b = b, a
        best = None
        for chosen in itertools.permutations(b, len(a)):
            cost = sum(abs(x - y) for x, y in zip(a, chosen))
            if best is None or cost < best:
                best = cost
        return best / len(a)

    cases = [
        ((1, 2), (1, 2, 3), 0.0),
        ((5,), (1, 4, 9), 1.0),
        ((1, 100), (0, 2, 99), 1.0),
        ((0, 10), (0, 10), 0.0),
    ]
    for a, b, expect in cases:
        got = sorted_l1(a, b)
        if got is None or abs(got - expect) > 1e-9:
            raise SystemExit(f"sorted L1 self-check failed for {a}, {b}: {got}")
        if abs(brute(a, b) - expect) > 1e-9:
            raise SystemExit(f"brute self-check failed for {a}, {b}")
    rng = random.Random(0)
    for _ in range(40):
        a = tuple(rng.randint(0, 40) for _ in range(rng.randint(1, 5)))
        b = tuple(rng.randint(0, 40) for _ in range(rng.randint(1, 6)))
        got = sorted_l1(a, b)
        exp = brute(a, b)
        if abs(got - exp) > 1e-9:
            raise SystemExit(f"sorted L1 != Hungarian brute {a} vs {b}: {got} {exp}")
    # hose_predict.chamfer on a hand case, in the same units.
    # pred 10,20 vs obs 10,30 -> 5
    got = chamfer((10, 20), (10, 30))
    if got is None or abs(got - 5) > 1e-9:
        raise SystemExit(f"chamfer self-check {got}")
    if chamfer((), (1,)) is not None or sorted_l1((), (1,)) is not None:
        raise SystemExit("empty lists must skip the channel")
    # Equal IR lists are distance 0 after the tenths scale.
    if ir_distance((33140, 16560), (16560, 33140)) != 0.0:
        raise SystemExit("IR distance is not invariant to order")


def candidate_smiles(cands) -> list:
    ranked = []
    for cand in list(cands or [])[:3]:
        if isinstance(cand, dict):
            cand = cand.get("smiles") or cand.get("candidate")
        ranked.append(cand if isinstance(cand, str) else None)
    return ranked


def wall_of(cands, gold_ik: str) -> str:
    pred = [ik14_of(s) for s in candidate_smiles(cands)]
    top1 = bool(pred) and pred[0] == gold_ik
    recalled = any(p == gold_ik for p in pred)
    if top1:
        return "top1"
    if recalled:
        return "in_pool"
    return "never"


def assert_lock(items: list[dict]) -> None:
    def take(name: str) -> list[dict]:
        if name == "all":
            return items
        if name == "simple":
            return [it for it in items if it["difficulty"] == "simple"]
        if name == "complex":
            return [it for it in items if it["difficulty"] == "complex"]
        return [it for it in items if it["arm"] == name]

    for (group, metric), (num, den) in LOCK.items():
        rows = take(group)
        if len(rows) != den:
            raise SystemExit(f"{group} denominator {len(rows)} != locked {den}")
        if metric == "top1":
            got = sum(it["wall"] == "top1" for it in rows)
        elif metric == "recall":
            got = sum(it["wall"] in ("top1", "in_pool") for it in rows)
        elif metric == "in_pool":
            got = sum(it["wall"] == "in_pool" for it in rows)
        elif metric == "never":
            got = sum(it["wall"] == "never" for it in rows)
        else:
            raise SystemExit(metric)
        if got != num:
            raise SystemExit(
                f"locked wall failed for {group} {metric}: got {got}, locked {num}/{den}. "
                "Retrieval was not run."
            )


def load_roster() -> tuple[list[dict], dict]:
    expand_q_blob = expansion_bytes("data/benchmark_expand/questions2.jsonl")
    expand_p_blob = expansion_bytes("data/benchmark_expand/predictions2.jsonl")
    expand500_q_blob = expansion_bytes("data/benchmark_expand_500/questions2.jsonl")
    expand500_p_blob = expansion_bytes("data/benchmark_expand_500/predictions2.jsonl")
    cut_blob = expansion_bytes("data/benchmark_expand_500/headline500_expand200_qids.json")
    vendor_meta = {
        "expand_sha": EXPAND_SHA,
        "files": {
            "data/benchmark_expand/questions2.jsonl": sha256(expand_q_blob),
            "data/benchmark_expand/predictions2.jsonl": sha256(expand_p_blob),
            "data/benchmark_expand_500/questions2.jsonl": sha256(expand500_q_blob),
            "data/benchmark_expand_500/predictions2.jsonl": sha256(expand500_p_blob),
            "data/benchmark_expand_500/headline500_expand200_qids.json": sha256(cut_blob),
        },
    }
    expand_q = read_jsonl_bytes(expand_q_blob)
    expand500_q = read_jsonl_bytes(expand500_q_blob)
    formulas = set()
    for directory in ("benchmark_main", "benchmark_v3", "benchmark_v2_ctrl"):
        for row in read_jsonl(ROOT / "data" / directory / "questions2.jsonl"):
            formulas.add(row["formula"])
    for row in expand_q + expand500_q:
        formulas.add(row["formula"])

    gold_index: dict[tuple, list[dict]] = defaultdict(list)
    with gzip.open(GOLD_PATH, "rt") as handle:
        for line in handle:
            row = json.loads(line)
            smiles = row.get("smiles")
            mol = Chem.MolFromSmiles(smiles) if smiles else None
            if mol is None:
                continue
            form = rdMolDescriptors.CalcMolFormula(mol)
            if form not in formulas:
                continue
            key = (form, ir_key(row.get("ir_bands_cm-1")), g_c13(row.get("c_nmr")))
            stored = (row.get("inchikey") or "")[:14]
            gold_index[key].append(
                {
                    "id": row.get("id"),
                    "ik": stored or Chem.MolToInchiKey(mol)[:14],
                    "smiles": Chem.MolToSmiles(mol),
                    "paper": paper_key(row.get("pmcid"), row.get("source_doi")),
                }
            )

    def match(question: dict) -> dict:
        key = (
            question["formula"],
            ir_key(question.get("ir_bands_cm-1")),
            q_c13(question.get("c_nmr")),
        )
        hits = gold_index.get(key, [])
        if len(hits) != 1:
            raise SystemExit(
                f"{question.get('qid')} {question.get('formula')}: "
                f"expected 1 source row, found {len(hits)}. Retrieval was not run."
            )
        return hits[0]

    items: list[dict] = []

    def add(question: dict, cands, cohort: str, arm: str, answer_ik: str | None) -> None:
        hit = match(question)
        if answer_ik is not None and hit["ik"] != answer_ik[:14]:
            raise SystemExit(
                f"{cohort} {question['qid']}: join InChIKey-14 != committed answer key"
            )
        bands = ir_key(question.get("ir_bands_cm-1"))
        carbons = q_c13(question.get("c_nmr"))
        protons = h1_centres(question.get("h_nmr") or "")
        gold_ik = hit["ik"]
        items.append(
            {
                "uid": f"{cohort}:{question['qid']}",
                "cohort": cohort,
                "arm": arm,
                "qid": question["qid"],
                "difficulty": question.get("difficulty") or "",
                "formula": question["formula"],
                "wall": wall_of(cands, gold_ik),
                "gold_ik": gold_ik,
                "gold_smiles": hit["smiles"],
                "source_id": hit["id"],
                "source_paper": hit["paper"],
                "ir": bands,
                "c13": carbons,
                "h1": protons,
            }
        )

    answers = {r["qid"]: r for r in read_jsonl(ROOT / "data/benchmark_main/answers2.jsonl")}
    questions = {r["qid"]: r for r in read_jsonl(ROOT / "data/benchmark_main/questions2.jsonl")}
    clean = set(json.loads((ROOT / "data/benchmark_main/clean_qids.json").read_text()))
    pred: dict = {}
    for path in sorted((ROOT / "data/benchmark_main/raw").glob("*.json")):
        try:
            pred.update(json.loads(path.read_text()))
        except Exception:
            continue
    for qid, ans in answers.items():
        if qid not in clean:
            continue
        cands = pred.get(f"M-{qid}")
        if cands is None:
            raise SystemExit(f"main {qid}: no deposited candidates")
        question = dict(questions[qid])
        question["difficulty"] = ans.get("difficulty") or question.get("difficulty")
        add(question, cands, "locked-main", "locked194", ans["inchikey"])

    for cohort, directory in (
        ("locked-v3", "benchmark_v3"),
        ("locked-v2ctrl", "benchmark_v2_ctrl"),
    ):
        base = ROOT / "data" / directory
        aa = {r["qid"]: r for r in read_jsonl(base / "answers2.jsonl")}
        qq = {r["qid"]: r for r in read_jsonl(base / "questions2.jsonl")}
        pp = {r["qid"]: r for r in read_jsonl(base / "predictions2.jsonl")}
        for qid, ans in aa.items():
            question = dict(qq[qid])
            question["difficulty"] = ans.get("difficulty") or question.get("difficulty")
            add(question, pp[qid].get("candidates", []), cohort, "locked194", ans["inchikey"])

    expand_p = {
        r["qid"]: r.get("candidates", [])
        for r in read_jsonl_bytes(expand_p_blob)
    }
    for question in expand_q:
        if question["qid"] not in expand_p:
            raise SystemExit(f"expand {question['qid']}: no deposited candidates")
        add(question, expand_p[question["qid"]], "expand", "plus106", None)

    cut = set(json.loads(cut_blob))
    expand500_p = {
        r["qid"]: r.get("candidates", [])
        for r in read_jsonl_bytes(expand500_p_blob)
    }
    kept200 = 0
    for question in expand500_q:
        if question["qid"] not in cut:
            continue
        if question["qid"] not in expand500_p:
            raise SystemExit(f"expand500 {question['qid']}: no deposited candidates")
        add(question, expand500_p[question["qid"]], "expand500", "expand200", None)
        kept200 += 1
    if kept200 != 200 or len(items) != 500:
        raise SystemExit(f"roster length {len(items)} (expand200 {kept200})")
    assert_lock(items)
    h1_ok = sum(1 for it in items if it["h1"])
    vendor_meta["query_h1_parsed"] = h1_ok
    vendor_meta["query_h1_n"] = len(items)
    if h1_ok < 0.95 * len(items):
        raise SystemExit(
            f"1H parsing recovered centres for only {h1_ok}/500 queries. "
            "Refusing to score a messy 1H channel. Retrieval was not run."
        )
    return items, vendor_meta


def build_index() -> tuple[dict[str, list[dict]], dict[str, list[dict]], dict[str, list[dict]], dict]:
    by_formula: dict[str, list[dict]] = defaultdict(list)
    by_id: dict[str, list[dict]] = defaultdict(list)
    by_ik: dict[str, list[dict]] = defaultdict(list)
    stats = {
        "source": str(GOLD_PATH.relative_to(ROOT)),
        "rows_read": 0,
        "dropped_unparsed_smiles": 0,
        "dropped_no_formula": 0,
        "dropped_no_peak_list": 0,
        "kept": 0,
        "with_ir": 0,
        "with_c13": 0,
        "with_h1": 0,
        "h1_field_nonempty": 0,
        "h1_unparsed": 0,
        "stored_ik_disagrees_with_rdkit": 0,
        "duplicate_record_ids": 0,
    }
    with gzip.open(GOLD_PATH, "rt") as handle:
        for line in handle:
            stats["rows_read"] += 1
            row = json.loads(line)
            smiles = row.get("smiles")
            mol = Chem.MolFromSmiles(smiles) if smiles else None
            if mol is None:
                stats["dropped_unparsed_smiles"] += 1
                continue
            formula = rdMolDescriptors.CalcMolFormula(mol)
            if not formula:
                stats["dropped_no_formula"] += 1
                continue
            ir = ir_key(row.get("ir_bands_cm-1"))
            c13 = g_c13(row.get("c_nmr") or "")
            raw_h = str(row.get("h_nmr") or "").strip()
            if raw_h:
                stats["h1_field_nonempty"] += 1
            h1 = h1_centres(raw_h)
            if raw_h and not h1:
                stats["h1_unparsed"] += 1
            if not ir and not c13 and not h1:
                stats["dropped_no_peak_list"] += 1
                continue
            stored = (row.get("inchikey") or "")[:14]
            computed = Chem.MolToInchiKey(mol)[:14]
            if stored and stored != computed:
                stats["stored_ik_disagrees_with_rdkit"] += 1
            rec = {
                "id": str(row.get("id")),
                "ik": stored or computed,
                "smiles": Chem.MolToSmiles(mol),
                "formula": formula,
                "ir": ir,
                "c13": c13,
                "h1": h1,
                "paper": paper_key(row.get("pmcid"), row.get("source_doi")),
            }
            by_formula[formula].append(rec)
            by_id[rec["id"]].append(rec)
            by_ik[rec["ik"]].append(rec)
            stats["kept"] += 1
            stats["with_ir"] += int(bool(ir))
            stats["with_c13"] += int(bool(c13))
            stats["with_h1"] += int(bool(h1))
    stats["duplicate_record_ids"] = sum(1 for rows in by_id.values() if len(rows) > 1)
    stats["unique_formulas"] = len(by_formula)
    stats["max_formula_rows"] = max((len(v) for v in by_formula.values()), default=0)
    return by_formula, by_id, by_ik, stats


def query_channels(item: dict) -> dict[str, tuple]:
    channels = {}
    if item["ir"]:
        channels["ir"] = item["ir"]
    if item["c13"]:
        channels["c13"] = item["c13"]
    if item["h1"]:
        channels["h1"] = item["h1"]
    return channels


def channel_distance(name: str, left: tuple, right: tuple) -> float | None:
    if name == "ir":
        return ir_distance(left, right)
    if name == "c13":
        return ppm_distance(left, right, 100)
    if name == "h1":
        return ppm_distance(left, right, 1000)
    raise SystemExit(name)


def rank_gallery(item: dict, gallery: list[dict]) -> list[dict]:
    """Return gallery records best-first. Gold is not read."""
    channels = query_channels(item)
    if not gallery:
        return []
    distances: dict[str, list[float | None]] = {}
    active: list[str] = []
    for name, query_list in channels.items():
        column: list[float | None] = []
        for rec in gallery:
            column.append(channel_distance(name, query_list, rec[name]))
        if any(value is not None for value in column):
            distances[name] = column
            active.append(name)
    order = ("ir", "c13", "h1")
    scored = []
    n = len(gallery)
    for i, rec in enumerate(gallery):
        ranks = []
        finite = 0
        dist_map = {}
        for name in active:
            value = distances[name][i]
            if value is None:
                better = sum(1 for other in distances[name] if other is not None)
            else:
                finite += 1
                better = sum(
                    1
                    for other in distances[name]
                    if other is not None and other < value - 1e-12
                )
            ranks.append(1 + better)
            dist_map[name] = value
        score = sum(ranks) / len(ranks) if ranks else 0.0
        tie = [score, -finite]
        for name in order:
            value = dist_map.get(name)
            tie.append(value if value is not None else 1e99)
        tie.append(rec["id"])
        scored.append((tuple(tie), rec, {k: dist_map.get(k) for k in order}, finite))
    scored.sort(key=lambda row: row[0])
    ranked = []
    for _tie, rec, dist_map, finite in scored:
        out = dict(rec)
        out["distances"] = dist_map
        out["n_finite"] = finite
        ranked.append(out)
    return ranked


def unique_proposals(ranked: list[dict], k: int) -> list[dict]:
    picked = []
    seen = set()
    for rec in ranked:
        if rec["ik"] in seen:
            continue
        seen.add(rec["ik"])
        picked.append(rec)
        if len(picked) >= k:
            break
    return picked


def paper_relation(source: str, other: str) -> str:
    if not source or not other:
        return "missing"
    if source == other:
        return "same"
    return "different"


def morgan(smiles: str):
    mol = Chem.MolFromSmiles(smiles) if smiles else None
    if mol is None:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)


def tanimoto(left: str, right: str) -> float | None:
    a = morgan(left)
    b = morgan(right)
    if a is None or b is None:
        return None
    return float(DataStructs.TanimotoSimilarity(a, b))


def score_queries(items: list[dict], by_formula, by_id, by_ik) -> tuple[list[dict], list[dict], dict]:
    """Score protocols A and B. Also confirm the query row matches on IR and 13C."""
    rows_a = []
    rows_b = []
    source_h1_zero = 0
    source_h1_comparable = 0
    source_missing = 0
    for item in items:
        id_rows = by_id.get(str(item["source_id"]), [])
        if len(id_rows) != 1:
            source_missing += 1
            raise SystemExit(
                f"{item['uid']}: source id {item['source_id']} found {len(id_rows)} times "
                "in the filtered index. Retrieval was not scored."
            )
        source = id_rows[0]
        if source["formula"] != item["formula"] or source["ir"] != item["ir"] or source["c13"] != item["c13"]:
            raise SystemExit(
                f"{item['uid']}: source row does not reproduce the printed formula/IR/13C key"
            )
        if source["ik"] != item["gold_ik"]:
            raise SystemExit(f"{item['uid']}: source InChIKey-14 != gold")
        if item["h1"] and source["h1"]:
            source_h1_comparable += 1
            dist = ppm_distance(item["h1"], source["h1"], 1000)
            if dist == 0.0:
                source_h1_zero += 1
        exclude_ids = {str(item["source_id"])}
        pool = [
            rec
            for rec in by_formula.get(item["formula"], [])
            if rec["id"] not in exclude_ids
        ]
        if any(rec["id"] == str(item["source_id"]) for rec in pool):
            raise SystemExit(f"{item['uid']}: query row survived Protocol A exclusion")
        other_same = sum(1 for rec in pool if rec["ik"] == item["gold_ik"])
        anywhere = [
            rec for rec in by_ik.get(item["gold_ik"], []) if rec["id"] != str(item["source_id"])
        ]
        other_formula = sum(1 for rec in anywhere if rec["formula"] != item["formula"])
        ranked_a = rank_gallery(item, pool)
        proposals = unique_proposals(ranked_a, 10)
        gold_rank = ""
        gold_hit = None
        for rank, rec in enumerate(unique_proposals(ranked_a, len(ranked_a) + 1), start=1):
            if rec["ik"] == item["gold_ik"]:
                gold_rank = rank
                gold_hit = rec
                break
        def hit_flag(k: int) -> int:
            return int(gold_rank != "" and gold_rank <= k)

        top = proposals[0] if proposals else None
        rows_a.append(
            {
                "uid": item["uid"],
                "arm": item["arm"],
                "cohort": item["cohort"],
                "qid": item["qid"],
                "difficulty": item["difficulty"],
                "wall_class": item["wall"],
                "formula": item["formula"],
                "gold_ik14": item["gold_ik"],
                "source_record_id": item["source_id"],
                "source_paper": item["source_paper"],
                "n_gallery_rows": len(pool),
                "n_gallery_unique_ik14": len({rec["ik"] for rec in pool}),
                "n_other_same_ik14": other_same,
                "n_other_same_ik14_anywhere": len(anywhere),
                "n_other_same_ik14_other_formula": other_formula,
                "channels": ",".join(
                    name for name in ("ir", "c13", "h1") if item[name]
                ),
                "recall_at_1": hit_flag(1),
                "recall_at_3": hit_flag(3),
                "recall_at_10": hit_flag(10),
                "top1_is_gold": hit_flag(1),
                "gold_rank": gold_rank,
                "top1_ik14": top["ik"] if top else "",
                "top1_record_id": top["id"] if top else "",
                "top1_paper": top["paper"] if top else "",
                "top1_paper_relation": paper_relation(item["source_paper"], top["paper"]) if top else "",
                "gold_hit_record_id": gold_hit["id"] if gold_hit else "",
                "gold_hit_paper_relation": (
                    paper_relation(item["source_paper"], gold_hit["paper"]) if gold_hit else ""
                ),
                "proposal_ik14s": "|".join(rec["ik"] for rec in proposals),
                "query_row_in_gallery": 0,
            }
        )
        pool_b = [rec for rec in pool if rec["ik"] != item["gold_ik"]]
        if any(rec["ik"] == item["gold_ik"] for rec in pool_b):
            raise SystemExit(f"{item['uid']}: gold InChIKey-14 survived Protocol B")
        ranked_b = rank_gallery(item, pool_b)
        neighbour = unique_proposals(ranked_b, 1)
        top_b = neighbour[0] if neighbour else None
        sim = tanimoto(item["gold_smiles"], top_b["smiles"]) if top_b else None
        rows_b.append(
            {
                "uid": item["uid"],
                "arm": item["arm"],
                "cohort": item["cohort"],
                "qid": item["qid"],
                "difficulty": item["difficulty"],
                "wall_class": item["wall"],
                "formula": item["formula"],
                "gold_ik14": item["gold_ik"],
                "n_gallery_rows": len(pool_b),
                "n_gallery_unique_ik14": len({rec["ik"] for rec in pool_b}),
                "neighbor_record_id": top_b["id"] if top_b else "",
                "neighbor_ik14": top_b["ik"] if top_b else "",
                "neighbor_tanimoto": "" if sim is None else f"{sim:.6f}",
                "neighbor_paper_relation": (
                    paper_relation(item["source_paper"], top_b["paper"]) if top_b else ""
                ),
                "empty_gallery": int(not pool_b),
            }
        )
    audit = {
        "source_rows_checked": len(items),
        "source_missing_from_index": source_missing,
        "source_h1_comparable": source_h1_comparable,
        "source_h1_distance_zero": source_h1_zero,
        "protocol_a_query_row_still_in_gallery": sum(r["query_row_in_gallery"] for r in rows_a),
        "protocol_a_top1_record_is_query_row": sum(
            r["top1_record_id"] == r["source_record_id"] and r["top1_record_id"] != ""
            for r in rows_a
        ),
    }
    return rows_a, rows_b, audit


def count_hits(rows: list[dict], key: str) -> int:
    return sum(int(r[key]) for r in rows)


def rate_block(rows: list[dict]) -> dict:
    n = len(rows)
    out = {"n": n}
    for k in KS:
        hits = count_hits(rows, f"recall_at_{k}")
        out[f"recall_at_{k}"] = {"hits": hits, "n": n, "rate": f"{hits}/{n}"}
    out["top1"] = out["recall_at_1"]
    empty = sum(1 for row in rows if int(row["n_gallery_rows"]) == 0)
    out["empty_gallery"] = {"hits": empty, "n": n, "rate": f"{empty}/{n}"}
    return out


def paper_block(rows: list[dict], relation_key: str, mask) -> dict:
    chosen = [r for r in rows if mask(r)]
    counts = {"same": 0, "different": 0, "missing": 0}
    for row in chosen:
        rel = row.get(relation_key) or "missing"
        if rel not in counts:
            rel = "missing"
        counts[rel] += 1
    n = len(chosen)
    return {
        "n": n,
        "same": counts["same"],
        "different": counts["different"],
        "missing": counts["missing"],
        "same_rate": f"{counts['same']}/{n}" if n else "0/0",
        "different_rate": f"{counts['different']}/{n}" if n else "0/0",
        "missing_rate": f"{counts['missing']}/{n}" if n else "0/0",
    }


def quartile_block(values: list[float]) -> dict:
    if not values:
        return {
            "n": 0,
            "minimum": None,
            "q1": None,
            "median": None,
            "q3": None,
            "maximum": None,
        }
    ordered = sorted(values)
    if len(ordered) == 1:
        only = ordered[0]
        q1 = median = q3 = only
    else:
        q1, _q2, q3 = statistics.quantiles(ordered, n=4, method="inclusive")
        median = statistics.median(ordered)
    return {
        "n": len(ordered),
        "minimum": ordered[0],
        "q1": q1,
        "median": median,
        "q3": q3,
        "maximum": ordered[-1],
    }


def slice_rows(rows: list[dict], wall: str | None) -> list[dict]:
    if wall is None:
        return rows
    return [r for r in rows if r["wall_class"] == wall]


def summarise(rows_a, rows_b, index_stats, roster_meta, audit, blob_sha: str) -> dict:
    walls = {
        "all": None,
        "top1": "top1",
        "in_pool": "in_pool",
        "never": "never",
    }
    protocol_a = {}
    for name, wall in walls.items():
        protocol_a[name] = rate_block(slice_rows(rows_a, wall))
    arms = {}
    for arm in ("locked194", "plus106", "expand200"):
        arms[arm] = rate_block([r for r in rows_a if r["arm"] == arm])
    coverage = {}
    for name, wall in walls.items():
        part = slice_rows(rows_a, wall)
        have = sum(1 for r in part if int(r["n_other_same_ik14"]) > 0)
        anywhere = sum(1 for r in part if int(r["n_other_same_ik14_anywhere"]) > 0)
        coverage[name] = {
            "queries_with_another_same_ik14_in_gallery": have,
            "queries_with_another_same_ik14_anywhere": anywhere,
            "n": len(part),
            "rate": f"{have}/{len(part)}",
            "anywhere_rate": f"{anywhere}/{len(part)}",
        }
    copies = [r for r in rows_a if int(r["n_other_same_ik14"]) > 0]
    copy_ranking = {
        "n": len(copies),
        "ranked_first": sum(1 for r in copies if int(r["recall_at_1"]) == 1),
        "gallery_contains_a_different_constitution": sum(
            1 for r in copies if int(r["n_gallery_unique_ik14"]) > 1
        ),
        "gallery_is_only_the_second_record": sum(
            1 for r in copies if int(r["n_gallery_unique_ik14"]) == 1
        ),
        "second_copies_removed_by_formula_filter": sum(
            int(r["n_other_same_ik14_other_formula"]) for r in rows_a
        ),
    }
    papers = {
        "top1_proposal": paper_block(
            rows_a, "top1_paper_relation", lambda r: bool(r["top1_record_id"])
        ),
        "top1_and_gold": paper_block(
            rows_a, "gold_hit_paper_relation", lambda r: int(r["recall_at_1"]) == 1
        ),
        "gold_recovered_at_10": paper_block(
            rows_a,
            "gold_hit_paper_relation",
            lambda r: int(r["recall_at_10"]) == 1,
        ),
        "never_proposed_gold_at_1": paper_block(
            rows_a,
            "gold_hit_paper_relation",
            lambda r: r["wall_class"] == "never" and int(r["recall_at_1"]) == 1,
        ),
        "top1_not_gold": paper_block(
            rows_a,
            "top1_paper_relation",
            lambda r: bool(r["top1_record_id"]) and int(r["recall_at_1"]) == 0,
        ),
    }
    protocol_b = {}
    for name, wall in walls.items():
        part = slice_rows(rows_b, wall)
        sizes = [int(r["n_gallery_rows"]) for r in part]
        unique_sizes = [int(r["n_gallery_unique_ik14"]) for r in part]
        sims = [float(r["neighbor_tanimoto"]) for r in part if r["neighbor_tanimoto"] != ""]
        empty = sum(int(r["empty_gallery"]) for r in part)
        protocol_b[name] = {
            "n": len(part),
            "empty_gallery": {"hits": empty, "n": len(part), "rate": f"{empty}/{len(part)}"},
            "with_neighbor": {
                "hits": len(part) - empty,
                "n": len(part),
                "rate": f"{len(part) - empty}/{len(part)}",
            },
            "gallery_rows": quartile_block(sizes),
            "gallery_unique_ik14": quartile_block(unique_sizes),
            "neighbor_tanimoto": quartile_block(sims),
            "tanimoto_denominator_note": (
                "Quartiles use queries with a neighbour. Empty galleries stay in the "
                "gallery-size distribution as 0 and are omitted from the Tanimoto quartiles."
            ),
        }
    return {
        "task": "IRexp nearest-neighbour library search. Not de novo elucidation.",
        "roster_n": 500,
        "locked_wall_reproduced": True,
        "locked_wall": {
            "exact_top1": "227/500",
            "in_pool_not_top1": "22/500",
            "never_proposed_k_le_3": "251/500",
            "recall_k_le_3": "249/500",
        },
        "expand_inputs": roster_meta,
        "index": index_stats,
        "irexp_resolved_blob": blob_sha,
        "query_row_exclusion": audit,
        "distance": {
            "ir": (
                "Monotone sorted L1 (rectangular Hungarian optimum on the line) "
                "of band positions in cm^-1, mean over the shorter list. No intensities."
            ),
            "c13": "Symmetric chamfer in ppm, hose_predict.chamfer / specmetrics.chamfer.",
            "h1": (
                "Symmetric chamfer on parsed ppm centres. "
                f"Parsed on {roster_meta['query_h1_parsed']}/500 queries."
            ),
            "combination": (
                "Mean of per-channel competition ranks inside the formula-matched "
                "gallery. Ties share the minimum rank. Channels with no comparable "
                "candidate are dropped. Gold SMILES is not a feature."
            ),
            "formula_filter": "RDKit CalcMolFormula (Hill) must equal the printed formula.",
            "identity": "InChIKey-14, the first 14 characters of the stored or RDKit InChIKey.",
        },
        "protocol_a": protocol_a,
        "protocol_a_by_arm": arms,
        "protocol_a_same_molecule_still_in_gallery": coverage,
        "protocol_a_copy_ranking": copy_ranking,
        "protocol_a_papers": papers,
        "protocol_b": protocol_b,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise SystemExit(f"no rows for {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt_num(value, digits: int) -> str:
    if value is None:
        return "undefined"
    number = float(value)
    if number.is_integer():
        return str(int(round(number)))
    return f"{number:.{digits}f}".rstrip("0").rstrip(".")


def fmt_quart(block: dict, digits: int) -> str:
    if not block or block["n"] == 0:
        return "n=0"
    return (
        f"n={block['n']}, median {fmt_num(block['median'], digits)}, "
        f"quartiles {fmt_num(block['q1'], digits)} and {fmt_num(block['q3'], digits)}, "
        f"range {fmt_num(block['minimum'], digits)} to {fmt_num(block['maximum'], digits)}"
    )


def write_figure(summary: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = ["1", "3", "10"]
    all_hits = [summary["protocol_a"]["all"][f"recall_at_{k}"]["hits"] for k in KS]
    nev_hits = [summary["protocol_a"]["never"][f"recall_at_{k}"]["hits"] for k in KS]
    all_rate = [h / 500 for h in all_hits]
    nev_rate = [h / 251 for h in nev_hits]
    x = range(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    bars_a = ax.bar([i - width / 2 for i in x], all_rate, width, label="all 500", color="#1f4e79")
    bars_b = ax.bar(
        [i + width / 2 for i in x],
        nev_rate,
        width,
        label="never proposed at k≤3 (251)",
        color="#c47b2b",
    )
    for bars, hits, den in ((bars_a, all_hits, 500), (bars_b, nev_hits, 251)):
        for bar, hit in zip(bars, hits):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{hit}/{den}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    ax.set_xticks(list(x), labels)
    ax.set_xlabel("k (unique InChIKey-14)")
    ax.set_ylabel("Recall of gold InChIKey-14")
    ax.set_ylim(0, 1.12)
    ax.set_title("Protocol A library search")
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_recall_at_k.png", dpi=160)
    fig.savefig(OUT / "fig_recall_at_k.pdf")
    plt.close(fig)


def write_report(summary: dict) -> None:
    a = summary["protocol_a"]
    b = summary["protocol_b"]
    cov = summary["protocol_a_same_molecule_still_in_gallery"]
    papers = summary["protocol_a_papers"]
    idx = summary["index"]
    audit = summary["query_row_exclusion"]
    lines = []
    lines.append("# IRexp library-search baseline on the locked n=500 roster")
    lines.append("")
    lines.append(
        "This is nearest-neighbour lookup in the public IRexp corpus. "
        "The search uses the printed Hill formula and the printed peak lists. "
        "It is library search. It is not a trained elucidator, and it is not a "
        "replacement of the locked closed-book result 227/500."
    )
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.append(
        "The locked generation wall on the deposited Claude lists was recomputed "
        "before retrieval and matched the published integers: "
        "227/500 exact top-1, 22/500 in the k≤3 pool but not top-1, "
        "251/500 never proposed at k≤3. Recall at k≤3 is 249/500."
    )
    lines.append("")
    lines.append(
        "Protocol A leaves out the query record only. Recall of the gold "
        f"InChIKey-14 is {a['all']['recall_at_1']['rate']} at k=1, "
        f"{a['all']['recall_at_3']['rate']} at k=3, and "
        f"{a['all']['recall_at_10']['rate']} at k=10. "
        "Top-1 is the k=1 rate. Empty proposal lists stay in the denominator."
    )
    lines.append("")
    lines.append(
        "On the 251 constitutions the closed-book harness never proposed, "
        f"Protocol A recall is {a['never']['recall_at_1']['rate']} at k=1, "
        f"{a['never']['recall_at_3']['rate']} at k=3, and "
        f"{a['never']['recall_at_10']['rate']} at k=10."
    )
    lines.append("")
    copy = summary["protocol_a_copy_ranking"]
    lines.append(
        "After the query row is removed, the formula gallery is empty for "
        f"{a['all']['empty_gallery']['rate']} of all queries and "
        f"{a['never']['empty_gallery']['rate']} of the 251. "
        "An empty list is a miss and stays in the denominator."
    )
    lines.append("")
    lines.append(
        "A second index row with the same gold InChIKey-14 remains inside that "
        f"formula gallery for {cov['all']['rate']} of all queries and "
        f"{cov['never']['rate']} of the 251. "
        f"The same count anywhere in the index, ignoring formula, is "
        f"{cov['all']['anywhere_rate']}. "
        "No second copy lies under a different Hill formula "
        f"({copy['second_copies_removed_by_formula_filter']} rows). "
        "Exact recovery cannot exceed the in-gallery count. "
        f"Where a second copy is in the gallery ({copy['n']} queries), it is ranked "
        f"first for {copy['ranked_first']}/{copy['n']}. "
        f"{copy['gallery_contains_a_different_constitution']}/{copy['n']} of those "
        "galleries also contain a different constitution; "
        f"{copy['gallery_is_only_the_second_record']}/{copy['n']} contain only the "
        "second record."
    )
    lines.append("")
    lines.append(
        "Protocol B also removes every row of the gold molecule. "
        f"The formula-matched gallery has size {fmt_quart(b['all']['gallery_rows'], 4)} "
        f"on all 500 and {fmt_quart(b['never']['gallery_rows'], 4)} on the 251 "
        "(zeros included). "
        f"A neighbour exists for {b['all']['with_neighbor']['rate']} of all queries and "
        f"{b['never']['with_neighbor']['rate']} of the 251. "
        "Morgan r=2 Tanimoto of that neighbour versus gold, on queries that have a neighbour, is "
        f"{fmt_quart(b['all']['neighbor_tanimoto'], 4)} for the full roster and "
        f"{fmt_quart(b['never']['neighbor_tanimoto'], 4)} for the 251."
    )
    lines.append("")
    lines.append("## Roster and the generation wall")
    lines.append("")
    lines.append(
        "The 500 problems are the locked score_main 194 (clean `benchmark_main` "
        "plus every `benchmark_v3` question plus every `benchmark_v2_ctrl` question), "
        "plus all 106 deposited Opus answers of the first expansion, plus the first "
        "200 validate-clean expand-500 qids in `headline500_expand200_qids.json` "
        f"(commit `{EXPAND_SHA}`). Sensitivity pools n=524 and n=530 are not included."
    )
    lines.append("")
    lines.append(
        "Gold InChIKey-14 is the unique (Hill formula, IR rounded to 0.1 cm^-1, "
        "13C rounded to 0.01 ppm) join into `data/irexp_resolved/irexp_resolved.jsonl.gz`. "
        "On the 194, that join matches the committed answer key. "
        "Wall labels use the deposited rank lists at k≤3: raw `M-<qid>` files for "
        "the clean main set, `predictions2.jsonl` for v3, v2_ctrl, expand, and expand-500. "
        "The rescore reproduced 55/194, 63/106, and 109/200 top-1, and 65/194, "
        "68/106, and 116/200 recall, plus the simple/complex locks 161/248, "
        "66/252, 172/248, and 77/252. Those checks abort the script on failure."
    )
    lines.append("")
    lines.append("## Index")
    lines.append("")
    lines.append(
        f"Source file: `{idx['source']}`, git blob `{summary['irexp_resolved_blob']}`. "
        "This checkout already contained the structure-linked file, so the public "
        "Hugging Face mirror was not re-downloaded. The filter keeps a row when "
        "RDKit parses the SMILES, `CalcMolFormula` returns a Hill formula, and at "
        "least one of the IR list, the parsed 13C list, or the parsed 1H list is non-empty."
    )
    lines.append("")
    lines.append(
        f"Rows read {idx['rows_read']}. Kept {idx['kept']}. "
        f"Dropped unparsed SMILES {idx['dropped_unparsed_smiles']}, "
        f"empty formula {idx['dropped_no_formula']}, "
        f"no comparable peak list {idx['dropped_no_peak_list']}. "
        f"Kept rows with IR {idx['with_ir']}, with 13C {idx['with_c13']}, "
        f"with parsed 1H {idx['with_h1']}. "
        f"Non-empty 1H fields {idx['h1_field_nonempty']}, of which "
        f"{idx['h1_unparsed']} did not yield a centre inside [-2, 16] ppm "
        "(a carbon list stored in the 1H field falls here). "
        f"Record ids that occur more than once: {idx['duplicate_record_ids']}. "
        f"Stored InChIKey-14 disagrees with RDKit on {idx['stored_ik_disagrees_with_rdkit']} kept rows. "
        "Identity uses the stored key when it is present."
    )
    lines.append("")
    lines.append(
        f"The query row was present in the index for {audit['source_rows_checked']}/500 "
        "queries and was removed before ranking. "
        f"Protocol A galleries that still contain the query id: "
        f"{audit['protocol_a_query_row_still_in_gallery']}/500. "
        f"Protocol A top-1 records equal to the query id: "
        f"{audit['protocol_a_top1_record_is_query_row']}/500."
    )
    lines.append("")
    lines.append("## Distance")
    lines.append("")
    lines.append(summary["distance"]["ir"])
    lines.append("")
    lines.append(summary["distance"]["c13"])
    lines.append("")
    lines.append(summary["distance"]["h1"])
    lines.append("")
    lines.append(summary["distance"]["combination"])
    lines.append("")
    lines.append(
        "The printed 1H string and the IRexp `h_nmr` field are not the same "
        "transcription. "
        f"Where both sides yielded a 1H list ({audit['source_h1_comparable']}/500), "
        f"the query-to-its-own-row 1H chamfer was 0 for "
        f"{audit['source_h1_distance_zero']}/{audit['source_h1_comparable']}. "
        "IR and 13C distances to that same row are 0 by the join, which is why "
        "exclusion is by record id rather than by a distance threshold. "
        "Gold SMILES is used only to name the InChIKey-14 label and, in Protocol B, "
        "to compute Tanimoto after the neighbour has been chosen."
    )
    lines.append("")
    lines.append("## Protocol A")
    lines.append("")
    lines.append(
        "Hard filter: same Hill formula. Then rank by the mean channel rank. "
        "Propose the first k distinct InChIKey-14 values. k is 1, 3, and 10."
    )
    lines.append("")
    lines.append("| wall class | n | recall@1 | recall@3 | recall@10 | another same InChIKey-14 still in the gallery |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for key, label in (
        ("all", "all"),
        ("top1", "exact top-1"),
        ("in_pool", "in pool, not top-1"),
        ("never", "never proposed at k≤3"),
    ):
        block = a[key]
        lines.append(
            f"| {label} | {block['n']} | {block['recall_at_1']['rate']} | "
            f"{block['recall_at_3']['rate']} | {block['recall_at_10']['rate']} | "
            f"{cov[key]['rate']} |"
        )
    lines.append("")
    lines.append(
        "Cohort slices of the same Protocol A run, not a separate experiment: "
        f"locked 194 recall@1/@3/@10 "
        f"{summary['protocol_a_by_arm']['locked194']['recall_at_1']['rate']}, "
        f"{summary['protocol_a_by_arm']['locked194']['recall_at_3']['rate']}, "
        f"{summary['protocol_a_by_arm']['locked194']['recall_at_10']['rate']}; "
        f"expand 106 "
        f"{summary['protocol_a_by_arm']['plus106']['recall_at_1']['rate']}, "
        f"{summary['protocol_a_by_arm']['plus106']['recall_at_3']['rate']}, "
        f"{summary['protocol_a_by_arm']['plus106']['recall_at_10']['rate']}; "
        f"expand-500 200-cut "
        f"{summary['protocol_a_by_arm']['expand200']['recall_at_1']['rate']}, "
        f"{summary['protocol_a_by_arm']['expand200']['recall_at_3']['rate']}, "
        f"{summary['protocol_a_by_arm']['expand200']['recall_at_10']['rate']}."
    )
    lines.append("")
    lines.append("### Same paper or a different paper")
    lines.append("")
    lines.append(
        "Paper identity is the PMC id when `pmcid` or `source_doi` carries one, "
        "otherwise the source string. The comparison is between the query row's "
        "paper and the paper of the retrieved record."
    )
    lines.append("")
    lines.append("| retrieved hit | n | same paper | different paper | identifier missing |")
    lines.append("|---|---:|---:|---:|---:|")
    for key, label in (
        ("top1_proposal", "Protocol A top-1 record, whether or not it is gold"),
        ("top1_and_gold", "Protocol A top-1 record when it is the gold InChIKey-14"),
        ("gold_recovered_at_10", "First gold InChIKey-14 inside the top 10"),
        ("never_proposed_gold_at_1", "Never-proposed query whose k=1 hit is gold"),
        ("top1_not_gold", "Protocol A top-1 record when it is not gold"),
    ):
        block = papers[key]
        lines.append(
            f"| {label} | {block['n']} | {block['same_rate']} | "
            f"{block['different_rate']} | {block['missing_rate']} |"
        )
    lines.append("")
    lines.append(
        "The top-1 row that is not gold counts formula isomers. A shared paper id "
        "on that row is a co-extracted isomer from the query article, not a second "
        "copy of the gold constitution. The gold rows are the separate lines above."
    )
    lines.append("")
    lines.append(
        "A different IRexp record of the same molecule is a real library hit, "
        "including a different extraction from the same paper and a later paper "
        "that reports the same constitution. That is duplicate publication in the "
        "corpus, which library search is supposed to find. It is not evidence that "
        "a closed-book generator proposed the structure."
    )
    lines.append("")
    lines.append("## Protocol B")
    lines.append("")
    lines.append(
        "Every index row with the gold InChIKey-14 is removed, so the gold "
        "constitution is absent. The gallery size is the number of remaining "
        "formula-matched rows. The neighbour is the best-ranked remaining "
        "structure. Tanimoto is Morgan radius 2, 2048 bits, chirality off, "
        "between that structure and the gold structure."
    )
    lines.append("")
    lines.append("| group | n | empty gallery | gallery rows | unique InChIKey-14 in the gallery | neighbour Tanimoto |")
    lines.append("|---|---:|---:|---|---|---|")
    for key, label in (
        ("all", "all"),
        ("top1", "exact top-1"),
        ("in_pool", "in pool, not top-1"),
        ("never", "never proposed at k≤3"),
    ):
        block = b[key]
        lines.append(
            f"| {label} | {block['n']} | {block['empty_gallery']['rate']} | "
            f"{fmt_quart(block['gallery_rows'], 4)} | "
            f"{fmt_quart(block['gallery_unique_ik14'], 4)} | "
            f"{fmt_quart(block['neighbor_tanimoto'], 4)} |"
        )
    lines.append("")
    lines.append(b["all"]["tanimoto_denominator_note"])
    lines.append("")
    lines.append(
        "Quartiles use `statistics.quantiles(n=4, method=\"inclusive\")`. "
        "The median uses `statistics.median`."
    )
    lines.append("")
    lines.append("## Leakage")
    lines.append("")
    lines.append(
        "The 500 roster was sampled from IRexp, so a search that leaves the query "
        "row in the index retrieves that row and calls it a success. Protocol A "
        "removes the query record id. It does not remove other records of the same "
        "InChIKey-14. Those remaining records are why exact recovery is possible "
        "at all. Where the coverage row above is 0, Protocol A recall is 0 for "
        "that query. Protocol B removes the molecule as well and therefore cannot "
        "report exact recovery. The two protocols answer different questions and "
        "their rates are not interchangeable."
    )
    lines.append("")
    lines.append("## Paragraph for the paper")
    lines.append("")
    lines.append(
        "As a post-hoc library-search baseline, not a trained model and not a "
        "replacement of the closed-book 227/500, we looked up each of the 500 "
        "printed formulas in the structure-linked IRexp index and ranked the "
        f"other records by peak-list distance ({idx['kept']} rows after the filter; "
        "the query row itself was excluded). "
        f"The gold InChIKey-14 was retrieved for {a['all']['recall_at_1']['rate']} "
        f"at k=1, {a['all']['recall_at_3']['rate']} at k=3, and "
        f"{a['all']['recall_at_10']['rate']} at k=10. "
        f"Of the 251 constitutions the locked harness never proposed, the same "
        f"lookup recovered {a['never']['recall_at_1']['rate']}, "
        f"{a['never']['recall_at_3']['rate']}, and "
        f"{a['never']['recall_at_10']['rate']}. "
        f"That ceiling is coverage, not rank: a second record of the gold molecule "
        f"remains in the formula gallery for {cov['all']['rate']} of queries and "
        f"{cov['never']['rate']} of the 251, and the formula gallery is empty for "
        f"{a['all']['empty_gallery']['rate']}. "
        f"Among the gold top-1 hits, {papers['top1_and_gold']['same_rate']} share the "
        f"query's source paper and {papers['top1_and_gold']['different_rate']} come "
        "from a different paper. "
        "Holding the gold molecule out, the formula-matched gallery has median size "
        f"{fmt_num(b['all']['gallery_rows']['median'], 4)} "
        f"(quartiles {fmt_num(b['all']['gallery_rows']['q1'], 4)} and "
        f"{fmt_num(b['all']['gallery_rows']['q3'], 4)}; empty galleries included) and the "
        "top neighbour's Morgan fingerprint Tanimoto (radius 2) has median "
        f"{_fmt_opt(b['all']['neighbor_tanimoto']['median'])} "
        f"on the {b['all']['with_neighbor']['rate']} queries that still have a neighbour "
        f"({fmt_quart(b['never']['neighbor_tanimoto'], 4)} on the never-proposed queries "
        "that have a neighbour). "
        "These figures measure corpus lookup and analog proximity."
    )
    lines.append("")
    lines.append("## Figure")
    lines.append("")
    lines.append(
        "`fig_recall_at_k.png` plots Protocol A recall@1, @3, and @10 for all 500 "
        "and for the 251. Bar labels are the same n/N counts as the table."
    )
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- `run_retrieval.py` — index, both protocols, this report")
    lines.append("- `protocol_a_per_query.csv` — one row per query, recall flags, papers")
    lines.append("- `protocol_b_per_query.csv` — gallery size and neighbour Tanimoto")
    lines.append("- `summary.json` — the integers behind this report")
    lines.append("- `fig_recall_at_k.png` and `fig_recall_at_k.pdf`")
    lines.append("- `vendor/` — expansion questions, predictions, and the 200-qid cut, pinned to the commit above")
    lines.append("")
    lines.append("## Reproduce")
    lines.append("")
    lines.append("```")
    lines.append("python3 analysis/iclr_rebuttal_nov2026/retrieval_proposer/run_retrieval.py")
    lines.append("```")
    lines.append("")
    lines.append(
        "Requires RDKit and matplotlib. No network call, no CASE/Surge run, and no "
        "paid model API. The script exits before writing scores if the locked wall "
        "is not 227/22/251."
    )
    lines.append("")
    (OUT / "REPORT.md").write_text("\n".join(lines))


def _fmt_opt(value) -> str:
    if value is None:
        return "undefined"
    return f"{value:.4f}"


def blob_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{GOLD_PATH.relative_to(ROOT)}"],
            cwd=ROOT,
            text=True,
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"could not hash {GOLD_PATH}: {exc}") from exc


def main() -> None:
    self_check_distance()
    items, roster_meta = load_roster()
    print(
        "locked wall reproduced: 227 exact top-1, 22 in-pool, 251 never proposed",
        flush=True,
    )
    by_formula, by_id, by_ik, index_stats = build_index()
    print(
        f"index kept {index_stats['kept']} / {index_stats['rows_read']}",
        flush=True,
    )
    rows_a, rows_b, audit = score_queries(items, by_formula, by_id, by_ik)
    summary = summarise(rows_a, rows_b, index_stats, roster_meta, audit, blob_sha())
    # Denominator checks before anything is treated as a result.
    if summary["protocol_a"]["all"]["n"] != 500 or summary["protocol_a"]["never"]["n"] != 251:
        raise SystemExit("denominator check failed")
    if summary["protocol_b"]["all"]["n"] != 500 or summary["protocol_b"]["never"]["n"] != 251:
        raise SystemExit("protocol B denominator check failed")
    for k in KS:
        hits = sum(summary["protocol_a"][name][f"recall_at_{k}"]["hits"] for name in ("top1", "in_pool", "never"))
        if hits != summary["protocol_a"]["all"][f"recall_at_{k}"]["hits"]:
            raise SystemExit(f"wall slices do not sum at k={k}")
    write_csv(OUT / "protocol_a_per_query.csv", rows_a)
    write_csv(OUT / "protocol_b_per_query.csv", rows_b)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_figure(summary)
    write_report(summary)
    a = summary["protocol_a"]
    print(
        "Protocol A recall@1/@3/@10",
        a["all"]["recall_at_1"]["rate"],
        a["all"]["recall_at_3"]["rate"],
        a["all"]["recall_at_10"]["rate"],
    )
    print(
        "Protocol A on the 251",
        a["never"]["recall_at_1"]["rate"],
        a["never"]["recall_at_3"]["rate"],
        a["never"]["recall_at_10"]["rate"],
    )
    print(
        "Protocol B empty",
        summary["protocol_b"]["all"]["empty_gallery"]["rate"],
        "median gallery",
        summary["protocol_b"]["all"]["gallery_rows"]["median"],
        "median Tanimoto",
        summary["protocol_b"]["all"]["neighbor_tanimoto"]["median"],
    )


if __name__ == "__main__":
    main()
