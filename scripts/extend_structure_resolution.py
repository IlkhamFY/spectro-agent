#!/usr/bin/env python3
"""
Extend IRexp structure resolution beyond the 43,060 records that the original
"<IUPAC name> (<label>)." header capture could name.

The record set is frozen: nothing is added, dropped, or re-extracted. For each
record that still has no structure, the source PMC text is re-read, the record's
own data block is located (its 1H/13C shift list and/or its exact IR band list),
and the text immediately before that block is searched for a compound name using
a wider set of the header conventions seen in PMC main text (section headings,
"Name label Yield ...", "Name, label, was synthesized", "Name (trivial, 1):").
Every candidate must parse in OPSIN and, where the record carries NMR, pass the
same structure-vs-NMR physics gates that scripts/quarantine_structure_nmr.py
applies to the released corpus. IR-only records (no NMR to gate against) only
accept a header-style candidate that sits directly before the IR block.

Three sub-commands, each durable:

  eval   score every pattern class on records that ALREADY have a structure
         (does the class re-find the known InChIKey-14?) -> decides what ships
  find   write the id-keyed sidecar of new (id -> smiles/inchikey/selfies)
         with full provenance; touches nothing else
  apply  fill the sidecar into data/irexp/irexp.jsonl.gz, regenerate the
         100%-resolved split + stats, and stage HF publish files

    python scripts/extend_structure_resolution.py eval
    python scripts/extend_structure_resolution.py find  [--patterns hdr,lbl,sec,was,ckh,snap]
    python scripts/extend_structure_resolution.py apply --sidecar data/irexp/structure_additions_<date>.jsonl.gz

Source text: PMC OA S3 plain text (https://pmc-oa-opendata.s3.amazonaws.com),
cached under data/cache/pmc_text/ (gitignored). OPSIN results are cached in
data/irexp/name_struct_cache_v2.jsonl.gz (the committed v1 cache is left as is).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import warnings
from collections import Counter, defaultdict
from datetime import date
from multiprocessing import Pool
from pathlib import Path

warnings.simplefilter("ignore")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spectro_scraper.extract import (  # noqa: E402
    _IR_RE, _NAMEISH, _capture_payload, _clean_name, _is_instrument_range,
    _looks_like_band_list, _parse_ir_bands, normalize_text, parse_c_peaks,
    parse_h_peaks)
from spectro_scraper.normalize import canonical_and_keys  # noqa: E402
from spectro_scraper.quality import _carbon_and_h_counts  # noqa: E402

S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
CORPUS = ROOT / "data/irexp/irexp.jsonl.gz"
CKH_NAME = ROOT / "data/irexp/ckh_name.jsonl.gz"
SNAPSHOT = ROOT / "data/irexp/ir_harvest_snapshot.jsonl.gz"
CACHE_V2 = ROOT / "data/irexp/name_struct_cache_v2.jsonl.gz"
TEXT_DIR = ROOT / "data/cache/pmc_text"
RESOLVED = ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz"
OPSIN_OPTS = {"allow_acid": True, "allow_bad_stereo": True}
C13_WINDOW = (-10.0, 235.0)
MIN_HEAVY = 5
IR_ONLY_MAX_DIST = 400        # header must sit directly before an IR-only block
WINDOW = 1500                 # look-behind for records with NMR
CHUNK_MAX_DIST = 500          # sentence-chunk fallback only this close

# ---------------------------------------------------------------------------
# Name patterns (all anchored at a sentence/heading boundary)
# ---------------------------------------------------------------------------
LABEL = (r"(?:[A-Za-z]{1,3}\d{1,3}-[A-Za-z]{1,3}|[A-Za-z]{1,3}-?\d{1,3}[a-z]{0,2}|"
         r"\d{1,3}[a-z]\d{1,2}|\d{1,3}[a-z]{0,3}|\d{1,3}-[A-Z][a-z]?|\d?[A-Z]{2,4}-\d{1,2}|"
         r"[IVX]{1,5}[a-z]?)[′'’]?")
_COLOURS = (r"[Ww]hite|[Yy]ellow|[Cc]olou?rless|[Pp]ale|[Bb]rown|[Oo]range|[Rr]ed\b|"
            r"[Gg]reen|[Bb]lue|[Bb]lack|[Pp]ink|[Oo]ff-white|[Gg]rey|[Gg]ray|[Pp]urple|"
            r"[Vv]iscous|[Aa]morphous|[Cc]rystal")
_FOLLOW = (r"[.:;]|\(\d{1,3}(?:\.\d+)?\s*%|\(1H\b|"
           r"Yield|yield|Prepared|prepared|Chromatography|Obtained|obtained|[Ww]as\b|"
           r"[Ww]ere\b|" + _COLOURS + r"|[Mm]\.?\s?[Pp]\.?\s*[:=.\d]|Rf\b|R\s?f\s*[:=]|"
           r"IR\b|FT-?IR|1H\b|13C\b|δ|HRMS|MS\b|UV\b|Anal")
NAME_CORE = r"(?P<name>[A-Za-z0-9(\[][^.\n;]{4,220}?)"
NAME_END = r"(?P<name>[A-Za-z0-9(\[][^.\n;:]{4,220}?[A-Za-z)\]])"  # no ':' inside; may not end in '-' or ','
PATTERNS = {
    # "<name> (<label>)." incl. "(<trivial name>, 1)", "(6f, Table 3)", "(1a′)"
    "hdr": re.compile(
        r"(?:^|(?<=[.\n;]))[ \t]*" + NAME_CORE +
        r"\s*\((?:[^()]{0,80},\s*)?(?P<label>" + LABEL + r")"
        r"(?:,\s*Table\s*\d+|,\s*\d{1,3}(?:\.\d)?\s*%)?\)\s*[.:,]?"),
    # "<name> <label> Yield/White/Prepared/...": label without parentheses
    "lbl": re.compile(
        r"(?:^|(?<=[.\n;:]))[ \t]*" + NAME_END +
        r"\s+(?P<label>" + LABEL + r")(?![,\-\d])\s*(?=" + _FOLLOW + r")"),
    # "2.2.1. <name> Yield: 78%" numbered heading, no label at all
    "sec": re.compile(
        r"(?:^|\n|(?<=[.;])\s)(?:\d{1,2}(?:\.\d{1,2}){1,4}\.?|[A-Z]\d{1,2}\.)\s+"
        r"(?:(?:Synthesis|Preparation|Synthesis and characteri[sz]ation)\s+of\s+)?"
        r"(?P<name>[A-Za-z0-9(\[][^\n;]{6,220}?)"
        r"(?=\s*(?:\((?:" + LABEL + r"|\d{1,3}(?:\.\d)?\s*%)[^)]{0,40}\)|:|Yield|yield|"
        + _COLOURS + r"|[Mm]\.?\s?[Pp]\.?\s*[:=.\d]|Rf\b|IR\b|FT-?IR|1H\b|13C\b|δ|\n))"),
    # "<name>, 3ce, was synthesized as ..."
    "was": re.compile(
        NAME_CORE + r",\s*(?P<label>" + LABEL + r"),\s*(?:was|were)\b"),
}
HEADER_PATTERNS = ("hdr", "lbl", "sec", "was")      # allowed for IR-only records
_SHIFT = re.compile(r"-?\d+\.\d+")


def ckh(h, c, ir) -> str:
    s = (h or "") + (c or "") + ",".join(str(b) for b in (ir or []))
    return hashlib.sha1(s.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Text access
# ---------------------------------------------------------------------------
def load_text(pmcid: str, fetch: bool = True) -> tuple[str, str]:
    """-> (raw text, version tag). Cached under TEXT_DIR; fetched from S3 on miss."""
    p = TEXT_DIR / f"{pmcid}.txt"
    if p.exists() and p.stat().st_size > 0:
        return p.read_text(errors="replace"), "cache"
    if not fetch:
        return "", ""
    for v in (1, 2, 3):
        try:
            req = urllib.request.Request(
                f"{S3}/{pmcid}.{v}/{pmcid}.{v}.txt",
                headers={"User-Agent": "spectro-agent-irexp-resolve/1.0 (research)"})
            t = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
            TEXT_DIR.mkdir(parents=True, exist_ok=True)
            p.write_text(t)
            return t, f"s3v{v}"
        except Exception:
            continue
    return "", ""


# ---------------------------------------------------------------------------
# Name cleaning -> OPSIN-ready variants
# ---------------------------------------------------------------------------
def clean_more(n: str) -> str:
    s = re.sub(r"\s+", " ", n).strip()
    s = re.sub(r"^(?:\d{1,4}\)|\d{2,4}|[A-Z]?\d{1,3}[a-z]?[.):])\s+", "", s)   # "8) ", "0393 ", "3a. "
    s = re.sub(r"\s+(?:\d{1,3}[a-z]{0,2}|[A-Z]{1,2}\d{1,3}[a-z]?)[′'’]?$", "", s)  # trailing " 8o"
    s = re.sub(r"(?<=[A-Za-z)])\d{1,3}$", "", s)                               # glued ref "…imine43"
    s = re.sub(r"\s*\(\s*[A-Z]{2,6}\s*$", "", s)                               # dangling "(THN"
    s = re.sub(r"(\d)\s*H\s*-", r"\1H-", s)                                    # "1 H -indol"
    s = re.sub(r"\s*-\s*([NOSP])\s*-\s*", r"-\1-", s)                          # "- N -("
    s = re.sub(r"\s*,\s*", ",", s)                                             # locant "6, 7-"
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    s = re.sub(r"^(?:pure|crude|title compound|the|compound|product)\s+", "", s, flags=re.I)
    s = re.sub(r"^(?:[A-Za-z ]+?(?:data|characteri[sz]ation|procedures?|substrates?|analysis)"
               r"\s+(?:of|for)?\s*)", "", s, flags=re.I)
    return s.strip(" .,;:-")


def variants(raw: str) -> list[str]:
    base = _clean_name(raw)
    out = []
    for v in (clean_more(base), base, re.sub(r"\)\s+(?=[a-z])", ")", clean_more(base)),
              re.sub(r"\]\s+(?=[a-z])", "]", clean_more(base))):
        v = v.strip()
        if 5 <= len(v) <= 220 and v not in out and _NAMEISH.search(v):
            out.append(v)
    return out


# ---------------------------------------------------------------------------
# Per-paper work (runs in a worker process)
# ---------------------------------------------------------------------------
def _locate_shifts(text: str, nmr: str, n: int = 4) -> list[int]:
    """Positions where the record's first n shift values occur in order."""
    vals = _SHIFT.findall(nmr or "")
    vals = [v for v in vals if abs(float(v)) < 260][:n]
    if len(vals) < 2:
        return []
    pat = r"(?<![\d.])" + r"\b.{0,120}?(?<![\d.])".join(re.escape(v) for v in vals) + r"\b"
    return [m.start() for m in re.finditer(pat, text, re.S)]


_NMR_TOKEN = re.compile(r"(?:\b(?:1\s?H|13\s?C)[\s-]*NMR\b|(?<![A-Za-z0-9])δ\s?[HC]?\s?[(:=]|\bNMR\b)")
# another compound's shift list: an NMR token followed by a number within 120 chars
_NMR_DATA = re.compile(r"(?:\b(?:1\s?H|13\s?C)[\s-]*NMR\b|(?<![A-Za-z0-9])δ\s?[HC]\s?[(:=])[^\d]{0,120}\d")


_IR_ANY = re.compile(r"\b(?:ATR-?FT-?IR|FT-?IR|IR)\b")


def _foreign_ir_between(between: str, own_bands) -> bool:
    """True if an IR band list that is NOT the record's own sits in `between`."""
    own = set(own_bands or [])
    for m in _IR_ANY.finditer(between):
        tail = between[m.end():m.end() + 260]
        bands = _parse_ir_bands(tail)
        if len(bands) < 3 or not _looks_like_band_list(tail):
            continue
        if own and len(own & set(bands)) >= min(2, len(own)):
            continue                                  # the record's own IR
        return True
    return False


def _foreign_nmr_between(between: str, own_shifts: list[str]) -> bool:
    """True if an NMR shift list that is NOT the record's own sits in `between`
    (i.e. the candidate header belongs to a different compound)."""
    for m in _NMR_DATA.finditer(between):
        tail = between[m.end() - 1:m.end() + 200]
        if not any(re.search(r"(?<![\d.])" + re.escape(v) + r"\b", tail) for v in own_shifts):
            return True
    return False


def _nmr_anchor(text: str, pos: int):
    """Start of the '1H NMR' / 'δ' token that introduces the shift list at pos,
    or None when no such token precedes it (a coincidental shift match)."""
    lo = max(0, pos - 220)
    m = None
    for m in _NMR_TOKEN.finditer(text[lo:pos]):
        pass
    return lo + m.start() if m else None


def paper_work(job: dict) -> dict:
    """job: {pmcid, records:[{id,h,c,bands,alt_bands,has_ik,names:{pattern:name}}]}"""
    pmcid, recs = job["pmcid"], job["records"]
    raw, ver = load_text(pmcid, fetch=job.get("fetch", True))
    if not raw:
        return {"pmcid": pmcid, "results": {r["id"]: {"loc": "notext"} for r in recs}}
    text = normalize_text(raw)

    # every IR characterisation block in the paper, with its parsed band list
    anchors = []
    for m in _IR_RE.finditer(text):
        payload = _capture_payload(text, m.end())
        bands = _parse_ir_bands(payload)
        if bands and not _is_instrument_range(bands, payload) and _looks_like_band_list(payload):
            anchors.append((m.start(), tuple(bands)))
    by_bands = defaultdict(list)
    for pos, b in anchors:
        by_bands[b].append(pos)
    rec_band_count = Counter(tuple(r["bands"]) for r in recs)

    def ir_pos(r):
        for key in (tuple(r["bands"]), tuple(r.get("alt_bands") or ())):
            if key and len(by_bands.get(key, [])) == 1 and rec_band_count[tuple(r["bands"])] == 1:
                return by_bands[key][0], "exact"
        # fuzzy: one anchor whose bands overlap >=80% with the record's (F1 drift)
        rb = set(r["bands"])
        if len(rb) >= 4:
            hits = [pos for pos, b in anchors
                    if len(rb & set(b)) >= 0.8 * len(rb) and abs(len(b) - len(rb)) <= 2]
            if len(hits) == 1 and rec_band_count[tuple(r["bands"])] == 1:
                return hits[0], "fuzzy"
        return None, None

    # locate every record's block start (resolved ones too: they bound windows)
    starts = {}
    results = {}
    for r in recs:
        ipos, imode = ir_pos(r)
        npos = None
        if r["h"] or r["c"]:
            hp = _locate_shifts(text, r["h"]) if r["h"] else []
            cp = _locate_shifts(text, r["c"]) if r["c"] else []
            cands = hp or cp
            if len(cands) > 1 and ipos is not None:      # disambiguate by IR proximity
                cands = [p for p in cands if abs(p - ipos) < 3000] or cands
            if len(cands) > 1 and hp and cp:
                cands = [p for p in hp if any(abs(p - q) < 3000 for q in cp)] or cands
            if len(cands) == 1:
                npos = _nmr_anchor(text, cands[0])
            elif len(cands) > 1:
                anchored = [p for p in cands if _nmr_anchor(text, p) is not None]
                if len(anchored) == 1:
                    npos = _nmr_anchor(text, anchored[0])
        if npos is not None:
            start = npos if ipos is None or abs(ipos - npos) > 3000 else min(ipos, npos)
            mode = "nmr" + ("+ir" if ipos is not None else "")
        elif ipos is not None:
            start, mode = ipos, "ir:" + imode
        else:
            results[r["id"]] = {"loc": "unlocated"}
            continue
        starts[r["id"]] = start
        results[r["id"]] = {"loc": mode, "start": start}

    order = sorted(starts.values())
    for r in recs:
        res = results[r["id"]]
        wanted = r["has_ik"] if job.get("eval") else not r["has_ik"]
        if not wanted or "start" not in res:
            continue
        start = res["start"]
        own_shifts = [v for nmr in (r["h"], r["c"]) for v in _SHIFT.findall(nmr or "")[:3]]
        prev = max([s for s in order if s < start], default=0)
        lo = max(prev, start - WINDOW, 0)
        win = text[lo:start]
        cands = []
        for pid, rx in PATTERNS.items():
            for m in rx.finditer(win):
                between = text[lo + m.end():start]
                cands.append({"pattern": pid, "raw": m.group("name"),
                              "label": (m.groupdict().get("label") or None),
                              "dist": start - (lo + m.end()),
                              "nmr_between": (_foreign_nmr_between(between, own_shifts)
                                              or _foreign_ir_between(between, r["bands"]))})
        if r["h"] or r["c"]:
            for chunk in re.split(r"[.;\n]\s+|\s+[Yy]ield\b", win[-CHUNK_MAX_DIST:]):
                chunk = chunk.strip()
                if 8 <= len(chunk) <= 220:
                    cands.append({"pattern": "chunk", "raw": chunk, "label": None,
                                  "dist": CHUNK_MAX_DIST})
        for pid, nm in (r.get("names") or {}).items():          # ckh / snapshot names
            cands.append({"pattern": pid, "raw": nm, "label": None, "dist": 0})
        res["cands"] = cands
        res["ir_only"] = not (r["h"] or r["c"])
        res["window"] = (lo, start)
    return {"pmcid": pmcid, "version": ver, "results": results}


# ---------------------------------------------------------------------------
# OPSIN + structure validity + physics gates (main process)
# ---------------------------------------------------------------------------
def load_cache_v2() -> dict:
    cache = {}
    if CACHE_V2.exists():
        for line in gzip.open(CACHE_V2, "rt"):
            d = json.loads(line)
            cache[d["n"]] = (d.get("smiles"), d.get("inchikey"), d.get("selfies"))
    return cache


def save_cache_v2(cache: dict) -> None:
    tmp = CACHE_V2.with_suffix(".gz.tmp")
    with gzip.open(tmp, "wt") as g:
        for n, (smi, ik, sf) in cache.items():
            g.write(json.dumps({"n": n, "smiles": smi, "inchikey": ik, "selfies": sf,
                                "opsin": OPSIN_OPTS}, ensure_ascii=False) + "\n")
    os.replace(tmp, CACHE_V2)


def valid_structure(smiles: str):
    """Canonical (smiles, inchikey, selfies) or None if not a sane closed-shell molecule."""
    from rdkit import Chem
    if not smiles or "*" in smiles:
        return None
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or mol.GetNumHeavyAtoms() < MIN_HEAVY:
        return None
    if any(a.GetNumRadicalElectrons() or a.GetIsotope() for a in mol.GetAtoms()):
        return None
    if sum(a.GetFormalCharge() for a in mol.GetAtoms()) != 0:
        return None                          # truncated "...pentanoate" anions, metal complexes
    frags = Chem.GetMolFrags(mol, asMols=True)
    if len(frags) > 1:                       # salts: keep HCl/HBr/Na+ style counter-ions only;
        big = max(range(len(frags)), key=lambda i: frags[i].GetNumHeavyAtoms())
        if any(f.GetNumHeavyAtoms() > 2 for i, f in enumerate(frags) if i != big):
            return None                      # e.g. "X diacetate" parsed as X + 2 acetic acid
    canon, ik, sf = canonical_and_keys(smiles)
    return (canon, ik, sf) if (canon and ik and sf) else None


def resolve_names(names: list[str], cache: dict) -> dict:
    """Batch-OPSIN every name not yet in the v2 cache; return name -> triple|None."""
    from py2opsin import py2opsin
    todo = sorted(n for n in set(names) if n not in cache)
    if todo:
        t0 = time.time()
        for i in range(0, len(todo), 20000):
            chunk = todo[i:i + 20000]
            smis = py2opsin(chunk, tmp_fpath=str(ROOT / "data/cache/py2opsin_v2_input.txt"),
                            **OPSIN_OPTS)
            smis = smis if isinstance(smis, list) else [None] * len(chunk)
            for nm, smi in zip(chunk, smis):
                cache[nm] = valid_structure(smi) or (None, None, None) if smi else (None, None, None)
        save_cache_v2(cache)
        print(f"OPSIN: {len(todo):,} new names in {time.time()-t0:.0f}s "
              f"({sum(1 for n in todo if cache[n][1]):,} parsed)", flush=True)
    return {n: (cache[n] if cache[n][1] else None) for n in set(names)}


def frag_ik14(smiles):
    """InChIKey-14 of the largest fragment (salt / counter-ion insensitive)."""
    from rdkit import Chem
    if not smiles:
        return None
    mol = Chem.MolFromSmiles(max(smiles.split("."), key=len))
    return Chem.MolToInchiKey(mol)[:14] if mol else None


def c13_count(c_nmr):
    if not c_nmr:
        return None
    n = 0
    for p in parse_c_peaks(c_nmr):
        try:
            v = float(re.findall(r"-?\d+\.?\d*", p.shift or "")[0])
        except (IndexError, ValueError):
            continue
        if C13_WINDOW[0] <= v <= C13_WINDOW[1]:
            n += 1
    return n


def h1_integral(h_nmr):
    if not h_nmr:
        return None
    vals = [p.nuclei for p in parse_h_peaks(h_nmr) if p.nuclei]
    return sum(vals) if vals else None


def gates(smiles: str, h_nmr, c_nmr) -> dict:
    counts = _carbon_and_h_counts(smiles)
    if not counts:
        return {"pass": False, "reason": "smiles_unparseable"}
    nC, nH, _ = counts
    g = {"nC": nC, "nH": nH, "c13_peaks": c13_count(c_nmr), "h1_integral": h1_integral(h_nmr),
         "pass": True, "reason": None}
    if g["c13_peaks"] is not None and g["c13_peaks"] > nC:
        g["pass"], g["reason"] = False, f"c13_peaks_gt_carbons:{g['c13_peaks']}>{nC}"
    elif g["h1_integral"] is not None and g["h1_integral"] > nH + 2:
        g["pass"], g["reason"] = False, f"h1_integration_gt_formula_plus_2:{g['h1_integral']}>{nH}+2"
    return g


def choose(res: dict, rec: dict, lookup: dict, allowed: set):
    """Nearest-first over candidates; first OPSIN-valid, gate-passing one wins."""
    cands = [c for c in res.get("cands", [])
             if c["pattern"] in allowed and not c.get("nmr_between")]
    if res.get("ir_only"):
        cands = [c for c in cands if c["pattern"] in HEADER_PATTERNS
                 and c["dist"] <= IR_ONLY_MAX_DIST]
    cands.sort(key=lambda c: c["dist"])
    rejected = []
    for c in cands:
        for v in c["_variants"]:
            trip = lookup.get(v)
            if not trip:
                continue
            g = gates(trip[0], rec["h"], rec["c"])
            if g["pass"]:
                return c, v, trip, g, rejected
            rejected.append({"pattern": c["pattern"], "name": v, "reason": g["reason"]})
            break                       # one structure per candidate string
    return None, None, None, None, rejected


# ---------------------------------------------------------------------------
# Corpus loading + job construction
# ---------------------------------------------------------------------------
def load_corpus():
    recs = []
    for line in gzip.open(CORPUS, "rt"):
        recs.append(json.loads(line))
    return recs


def load_hf_bands(path: Path | None) -> dict:
    """id -> F1 (re-parsed) bands where they differ from the tracked corpus."""
    alt = {}
    if path and path.exists():
        for line in gzip.open(path, "rt"):
            r = json.loads(line)
            if r.get("ir_bands_old_cm-1") and r["ir_bands_old_cm-1"] != r["ir_bands_cm-1"]:
                alt[r["id"]] = r["ir_bands_cm-1"]
    return alt


def load_side_names(recs):
    """Per record id: names captured by earlier passes (ckh map, harvest snapshot)."""
    ckh_name = {}
    for line in gzip.open(CKH_NAME, "rt"):
        d = json.loads(line)
        ckh_name.setdefault(d["k"], d["n"])
    by_key = {}
    by_loose = {}
    for r in recs:
        by_key[ckh(r.get("h_nmr"), r.get("c_nmr"), r.get("ir_bands_cm-1"))] = r["id"]
        by_loose.setdefault((r.get("source_doi"), tuple(r.get("ir_bands_cm-1") or [])), []).append(r["id"])
    names = defaultdict(dict)
    for k, n in ckh_name.items():
        if k in by_key:
            names[by_key[k]]["ckh"] = n
    if SNAPSHOT.exists():
        for line in gzip.open(SNAPSHOT, "rt"):
            d = json.loads(line)
            if not d.get("name"):
                continue
            k = ckh(d.get("h_nmr"), d.get("c_nmr"), d.get("ir_bands_cm-1"))
            if k in by_key:
                names[by_key[k]].setdefault("snap", d["name"])
            else:
                ids = by_loose.get((d.get("source_doi"), tuple(d.get("ir_bands_cm-1") or [])), [])
                if len(ids) == 1:
                    names[ids[0]].setdefault("snap", d["name"])
    return names


def build_jobs(recs, alt_bands, side_names, only_unresolved: bool, eval_mode: bool, fetch: bool):
    by_p = defaultdict(list)
    for r in recs:
        p = r.get("pmcid")
        if not p:
            continue
        by_p[p].append({"id": r["id"], "h": r.get("h_nmr"), "c": r.get("c_nmr"),
                        "bands": r.get("ir_bands_cm-1") or [], "alt_bands": alt_bands.get(r["id"]),
                        "has_ik": bool(r.get("inchikey")), "names": side_names.get(r["id"], {})})
    jobs = []
    for p, rs in by_p.items():
        want = [x for x in rs if (x["has_ik"] if eval_mode else not x["has_ik"])]
        if not want:
            continue
        if only_unresolved and not (TEXT_DIR / f"{p}.txt").exists() and not fetch:
            continue
        jobs.append({"pmcid": p, "records": rs, "eval": eval_mode, "fetch": fetch})
    return jobs


def run_papers(jobs, workers):
    out = {}
    versions = {}
    t0 = time.time()
    with Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(paper_work, jobs, chunksize=8), 1):
            out.update(r["results"])
            versions[r["pmcid"]] = r.get("version", "")
            if i % 2000 == 0:
                print(f"  papers {i:,}/{len(jobs):,} ({time.time()-t0:.0f}s)", flush=True)
    return out, versions


def attach_variants_and_resolve(results, cache):
    names = []
    for res in results.values():
        for c in res.get("cands", []):
            c["_variants"] = variants(c["raw"])
            names.extend(c["_variants"])
    lookup = resolve_names(names, cache)
    return lookup


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------
def cmd_eval(args):
    recs = load_corpus()
    alt = load_hf_bands(Path(args.hf_commercial) if args.hf_commercial else None)
    side = load_side_names(recs)
    jobs = build_jobs(recs, alt, side, only_unresolved=False, eval_mode=True, fetch=args.fetch)
    # only papers whose text is already cached (the ones with unresolved records)
    jobs = [j for j in jobs if (TEXT_DIR / f"{j['pmcid']}.txt").exists()]
    if args.limit:
        jobs = jobs[:args.limit]
    print(f"eval: {len(jobs):,} papers", flush=True)
    results, _ = run_papers(jobs, args.workers)
    by_id = {r["id"]: r for r in recs}
    cache = load_cache_v2()
    lookup = attach_variants_and_resolve(results, cache)
    classes = list(PATTERNS) + ["chunk", "ckh", "snap"]
    stats = {}
    for cls in classes + ["ALL", "ALL-nochunk"]:
        allowed = set(classes) if cls == "ALL" else (set(classes) - {"chunk"} if cls == "ALL-nochunk" else {cls})
        st = Counter()
        for rid, res in results.items():
            if "cands" not in res:
                continue
            rec = by_id[rid]
            r = {"h": rec.get("h_nmr"), "c": rec.get("c_nmr")}
            st["eligible"] += 1
            st["eligible_ir_only"] += bool(res.get("ir_only"))
            c, v, trip, g, _ = choose(res, r, lookup, allowed)
            if not c:
                continue
            key = "ir_only" if res.get("ir_only") else "nmr"
            st[f"chosen_{key}"] += 1
            st[f"agree_{key}"] += (trip[1][:14] == (rec.get("inchikey") or "")[:14])
            st[f"agree_frag_{key}"] += (frag_ik14(trip[0]) == frag_ik14(rec.get("smiles")))
        stats[cls] = dict(st)
        for key in ("nmr", "ir_only"):
            ch = st.get(f"chosen_{key}", 0)
            stats[cls][f"precision_{key}"] = round(st.get(f"agree_{key}", 0) / ch, 4) if ch else None
            stats[cls][f"precision_frag_{key}"] = round(st.get(f"agree_frag_{key}", 0) / ch, 4) if ch else None
    print(json.dumps(stats, indent=1))
    loc = Counter(res["loc"] for res in results.values())
    print("location modes:", dict(loc))
    out = ROOT / f"data/irexp/structure_additions_{date.today().isoformat()}.eval.json"
    out.write_text(json.dumps({"papers": len(jobs), "location_modes": dict(loc),
                               "per_pattern": stats, "opsin": OPSIN_OPTS,
                               "note": "precision = chosen structure's InChIKey-14 equals the "
                                       "record's existing InChIKey-14 (records already resolved "
                                       "by the v1 header capture)"}, indent=1))
    print("wrote", out)


def cmd_find(args):
    recs = load_corpus()
    alt = load_hf_bands(Path(args.hf_commercial) if args.hf_commercial else None)
    side = load_side_names(recs)
    jobs = build_jobs(recs, alt, side, only_unresolved=True, eval_mode=False, fetch=args.fetch)
    if args.limit:
        jobs = jobs[:args.limit]
    print(f"find: {len(jobs):,} papers with unresolved records", flush=True)
    results, versions = run_papers(jobs, args.workers)
    by_id = {r["id"]: r for r in recs}
    cache = load_cache_v2()
    lookup = attach_variants_and_resolve(results, cache)
    allowed = set(args.patterns.split(","))
    out = ROOT / f"data/irexp/structure_additions_{date.today().isoformat()}.jsonl.gz"
    st = Counter()
    pat = Counter()
    rej = Counter()
    with gzip.open(out, "wt") as g:
        for rid, res in results.items():
            rec = by_id[rid]
            if rec.get("inchikey"):
                continue
            st["unresolved"] += 1
            st["loc_" + res["loc"].split(":")[0]] += 1
            if "cands" not in res:
                continue
            r = {"h": rec.get("h_nmr"), "c": rec.get("c_nmr")}
            c, v, trip, gt, rejected = choose(res, r, lookup, allowed)
            for x in rejected:
                rej[x["reason"].split(":")[0]] += 1
            if not c:
                st["no_candidate"] += 1
                continue
            st["resolved"] += 1
            st["resolved_ir_only"] += bool(res.get("ir_only"))
            pat[c["pattern"]] += 1
            g.write(json.dumps({
                "id": rid, "pmcid": rec.get("pmcid"), "license_pool": rec.get("license_pool"),
                "smiles": trip[0], "inchikey": trip[1], "selfies": trip[2],
                "name_raw": c["raw"], "name_used": v, "pattern": c["pattern"],
                "label": c["label"], "dist_chars": c["dist"], "ir_only": bool(res.get("ir_only")),
                "location": res["loc"], "text_version": versions.get(rec.get("pmcid"), ""),
                "opsin": OPSIN_OPTS, "gates": gt, "rejected_before": rejected[:5],
            }, ensure_ascii=False) + "\n")
    print(json.dumps({"counts": dict(st), "by_pattern": dict(pat),
                      "gate_rejections": dict(rej)}, indent=1))
    print("wrote", out)


def _write_gz(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as g:
        for r in rows:
            g.write(json.dumps(r, ensure_ascii=False) + "\n")


def cmd_apply(args):
    adds = {}
    for line in gzip.open(args.sidecar, "rt"):
        d = json.loads(line)
        adds[d["id"]] = d
    recs = load_corpus()
    filled = 0
    ik_before = {r["inchikey"] for r in recs if r.get("inchikey")}
    for r in recs:
        a = adds.get(r["id"])
        if a and not r.get("inchikey"):
            r["smiles"], r["inchikey"], r["selfies"] = a["smiles"], a["inchikey"], a["selfies"]
            r["has_structure"] = True
            filled += 1
    res = [r for r in recs if r.get("inchikey")]
    _write_gz(CORPUS, recs)
    _write_gz(RESOLVED, res)
    any_nmr = sum(1 for r in recs if r.get("h_nmr") or r.get("c_nmr"))
    res_nmr = sum(1 for r in res if r.get("h_nmr") or r.get("c_nmr"))
    quad = sum(1 for r in res if r.get("h_nmr") and r.get("c_nmr"))
    pools = Counter(r["license_pool"] for r in res)
    stats = json.loads((ROOT / "data/irexp/irexp_stats.json").read_text())
    stats.update({"records": len(recs), "all_experimental_IR": len(recs),
                  "with_co_reported_NMR": any_nmr, "with_structure": len(res),
                  "with_structure_unique_inchikey": len({r["inchikey"] for r in res}),
                  "structure_by_license_pool": dict(pools),
                  "structure_resolution_passes": [
                      "v1: '<name> (<label>).' header capture, OPSIN + PubChem fallback (43,060)",
                      f"v2: {Path(args.sidecar).name} — wider header conventions, OPSIN "
                      f"(allow_acid, allow_bad_stereo), structure-vs-NMR gates (+{len(adds):,})"]})
    (ROOT / "data/irexp/irexp_stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    (ROOT / "data/irexp_resolved/stats.json").write_text(json.dumps({
        "records": len(res), "structure_resolution": "100% (by construction)",
        "with_co_reported_NMR": res_nmr, "full_IR_1H_13C_structure": quad,
        "note": "Structure-complete split of IRexp (IR + structure on every record)."},
        indent=2) + "\n")
    print(f"apply: +{filled:,} -> with_structure {len(res):,} / {len(recs):,}; "
          f"unique InChIKey {len({r['inchikey'] for r in res}):,} "
          f"(new keys not seen before: {len({r['inchikey'] for r in res} - ik_before):,}); "
          f"resolved with NMR {res_nmr:,}; quadruples {quad:,}; pools {dict(pools)}")

    # ---- HF commercial staging (F1 bands + flags come from the downloaded HF file) ----
    if args.hf_commercial:
        stage = ROOT / f"data/irexp_rebuild_{date.today().strftime('%Y%m%d')}/hf_publish"
        stage.mkdir(parents=True, exist_ok=True)
        rows = []
        for line in gzip.open(args.hf_commercial, "rt"):
            r = json.loads(line)
            a = adds.get(r["id"])
            if a and not r.get("inchikey"):
                r["smiles"], r["inchikey"], r["selfies"] = a["smiles"], a["inchikey"], a["selfies"]
                r["has_structure"] = True
            rows.append(r)
        resolved = [r for r in rows if r.get("inchikey")]
        _write_gz(stage / "irexp_commercial.jsonl.gz", rows)
        _write_gz(stage / "irexp_resolved_commercial.jsonl.gz", resolved)
        # train_no_bench_commercial = resolved_commercial minus benchmark InChIKey-14 identities
        import glob
        bench = set()
        for path in sorted(glob.glob(str(ROOT / "data/benchmark_*/answers2.jsonl"))):
            for line in open(path):
                a = json.loads(line)
                ik = (a.get("inchikey") or "")[:14]
                if not ik and a.get("smiles"):
                    ik = (canonical_and_keys(a["smiles"])[1] or "")[:14]
                if ik:
                    bench.add(ik)
        train = [r for r in resolved if (r.get("inchikey") or "")[:14] not in bench]
        _write_gz(stage / "train_no_bench_commercial.jsonl.gz", train)
        bs = {"date": date.today().isoformat(), "sidecar": str(Path(args.sidecar).name),
              "source_hf_commercial": str(args.hf_commercial),
              "source_hf_revision": args.hf_revision or None,
              "commercial": len(rows), "resolved_commercial": len(resolved),
              "train_no_bench_commercial": len(train), "benchmark_ik14_set_size": len(bench),
              "skipped_benchmark_ik14": len(resolved) - len(train),
              "added_structures_commercial": sum(1 for r in rows if r["id"] in adds),
              "f2_resolved": sum(1 for r in resolved if r.get("ir_shared_in_paper")),
              "f3_resolved": sum(1 for r in resolved if r.get("ir_table_flatten_suspect")),
              "invariant": "train_no_bench_commercial ⊆ resolved_commercial ⊆ commercial"}
        (stage / "build_stats.json").write_text(json.dumps(bs, indent=2) + "\n")
        print("staged HF files:", json.dumps(bs, indent=1))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("eval", "find"):
        p = sub.add_parser(name)
        p.add_argument("--workers", type=int, default=max(2, os.cpu_count() - 2))
        p.add_argument("--limit", type=int, default=0, help="first N papers only")
        p.add_argument("--fetch", action="store_true", help="fetch missing texts from S3")
        p.add_argument("--hf-commercial", default="", help="HF irexp_commercial.jsonl.gz (F1 bands)")
        if name == "find":
            p.add_argument("--patterns", default="hdr,lbl,sec,was,ckh,snap",
                           help="pattern classes allowed to ship (see eval)")
    p = sub.add_parser("apply")
    p.add_argument("--sidecar", required=True)
    p.add_argument("--hf-commercial", default="")
    p.add_argument("--hf-revision", default="",
                   help="Hub commit sha of --hf-commercial, recorded in build_stats.json")
    args = ap.parse_args(argv)
    {"eval": cmd_eval, "find": cmd_find, "apply": cmd_apply}[args.cmd](args)


if __name__ == "__main__":
    main()
