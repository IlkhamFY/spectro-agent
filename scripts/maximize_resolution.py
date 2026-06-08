#!/usr/bin/env python3
"""
Maximise IRexp structure resolution and (re)build the 100%-resolved split.

Pipeline (each stage durable + resumable so container restarts never redo work):

  1. content-key -> name map  (data/irexp/ckh_name.jsonl.gz, committed)
     Built once by re-fetching the source PMC papers and re-extracting with the
     improved name capture. If the committed map exists, fetching is skipped.
  2. name -> structure cache  (data/irexp/name_struct_cache.jsonl.gz, committed)
     OPSIN (offline) first; PubChem (authoritative, network) for names OPSIN
     can't parse -- trivial/natural-product names. Both cached so reruns are free.
  3. apply additively to data/irexp/irexp.jsonl (matches on the stable content
     key, fills only smiles/selfies/inchikey) + regenerate data/irexp_resolved/
     (the 100%-structure-resolved split) and stats.

    python scripts/maximize_resolution.py            # full
    python scripts/maximize_resolution.py --no-pubchem
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.extract import extract_records              # noqa: E402
from spectro_scraper.normalize import (                          # noqa: E402
    to_spectro_h, to_spectro_c, canonical_and_keys)

S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
IREXP = Path("data/irexp/irexp.jsonl")
CKH_NAME = Path("data/irexp/ckh_name.jsonl.gz")             # durable, committed
STRUCT_CACHE = Path("data/irexp/name_struct_cache.jsonl.gz")  # durable, committed
TXT_CACHE = Path("data/cache/pmc_text")                     # ephemeral
DONE = Path("data/cache/maximize_done.txt")                # ephemeral


def ckh(h_nmr: str, c_nmr: str, ir_bands) -> str:
    s = (h_nmr or "") + "" + (c_nmr or "") + "" + \
        ",".join(str(b) for b in (ir_bands or []))
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def s3_txt(num: str) -> str:
    p = TXT_CACHE / f"{num}.txt"
    if p.exists() and p.stat().st_size > 0:
        return p.read_text(errors="replace")
    for v in (1, 2):
        try:
            req = urllib.request.Request(f"{S3}/PMC{num}.{v}/PMC{num}.{v}.txt",
                                         headers={"User-Agent": "spectro-agent"})
            t = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            TXT_CACHE.mkdir(parents=True, exist_ok=True); p.write_text(t)
            return t
        except Exception:
            continue
    return ""


def build_name_map(workers: int) -> dict:
    """content-key-hash -> name, durable in CKH_NAME."""
    ckh_name = {}
    if CKH_NAME.exists():
        for line in gzip.open(CKH_NAME, "rt"):
            d = json.loads(line); ckh_name.setdefault(d["k"], d["n"])
        print(f"loaded {len(ckh_name):,} cached content-key->name pairs", flush=True)
        return ckh_name

    pmc, seen = [], set()
    for line in IREXP.open():
        sd = json.loads(line).get("source_doi") or ""
        if isinstance(sd, str) and sd.startswith("PMC:"):
            n = sd.split(":", 1)[1]
            if n not in seen:
                seen.add(n); pmc.append(n)
    done = set(DONE.read_text().split()) if DONE.exists() else set()
    todo = [n for n in pmc if n not in done]
    print(f"building name map: {len(todo):,} papers to fetch", flush=True)
    TXT_CACHE.mkdir(parents=True, exist_ok=True)
    tmp = CKH_NAME.with_suffix(".tmp.jsonl")
    out = tmp.open("a"); donef = DONE.open("a")

    def work(num):
        txt = s3_txt(num); pairs = []
        if txt:
            for rec in extract_records(txt):
                if rec.ir_bands and rec.name:
                    pairs.append((ckh(to_spectro_h(rec), to_spectro_c(rec),
                                      rec.ir_bands), rec.name))
        return num, pairs

    n = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for num, pairs in ex.map(work, todo):
            for k, name in pairs:
                out.write(json.dumps({"k": k, "n": name}, ensure_ascii=False) + "\n")
                ckh_name.setdefault(k, name)
            donef.write(num + "\n"); n += 1
            if n % 1000 == 0:
                out.flush(); donef.flush(); print(f"  ...{n:,}/{len(todo):,}", flush=True)
    out.close(); donef.close()
    # freeze to the committed gz
    with gzip.open(CKH_NAME, "wt") as g:
        for k, name in ckh_name.items():
            g.write(json.dumps({"k": k, "n": name}, ensure_ascii=False) + "\n")
    tmp.unlink(missing_ok=True)
    print(f"name map built: {len(ckh_name):,} pairs -> {CKH_NAME}", flush=True)
    return ckh_name


def load_struct_cache() -> dict:
    cache = {}
    if STRUCT_CACHE.exists():
        for line in gzip.open(STRUCT_CACHE, "rt"):
            d = json.loads(line)
            cache[d["n"]] = (d.get("smiles"), d.get("inchikey"), d.get("selfies"))
    return cache


def save_struct_cache(cache: dict):
    with gzip.open(STRUCT_CACHE, "wt") as g:
        for n, (smi, ik, sf) in cache.items():
            g.write(json.dumps({"n": n, "smiles": smi, "inchikey": ik,
                                "selfies": sf}, ensure_ascii=False) + "\n")


def pubchem(name: str) -> str | None:
    try:
        url = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
               f"{urllib.parse.quote(name)}/property/CanonicalSMILES/TXT")
        r = urllib.request.urlopen(url, timeout=20).read().decode().strip()
        return r.splitlines()[0] if r else None
    except Exception:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--no-pubchem", action="store_true")
    ap.add_argument("--pubchem-workers", type=int, default=6)
    args = ap.parse_args(argv)

    ckh_name = build_name_map(args.workers)
    names = sorted(set(ckh_name.values()))
    print(f"{len(names):,} unique in-text names", flush=True)

    cache = load_struct_cache()
    print(f"struct cache: {len(cache):,} names already attempted", flush=True)

    # ---- OPSIN batch on names not yet attempted ------------------------------
    from py2opsin import py2opsin
    todo = [n for n in names if n not in cache]
    if todo:
        smis = py2opsin(todo)
        smis = smis if isinstance(smis, list) else [None] * len(todo)
        for nm, smi in zip(todo, smis):
            if smi:
                canon, ik, sf = canonical_and_keys(smi)
                cache[nm] = (canon or smi, ik, sf) if (ik and sf) else (None, None, None)
            else:
                cache[nm] = (None, None, None)   # mark attempted; PubChem retries below
        save_struct_cache(cache)
    opsin_ok = sum(1 for v in cache.values() if v[1])
    print(f"after OPSIN: {opsin_ok:,}/{len(names):,} names resolved", flush=True)

    # ---- PubChem fallback for OPSIN failures (authoritative) ------------------
    if not args.no_pubchem:
        misses = [n for n in names if not cache.get(n, (None, None, None))[1]
                  and 4 <= len(n) <= 120 and "pubchem:" + n not in cache]
        print(f"PubChem fallback on {len(misses):,} OPSIN-miss names", flush=True)

        def pc(nm):
            time.sleep(0.05)
            smi = pubchem(nm)
            if smi:
                canon, ik, sf = canonical_and_keys(smi)
                if ik and sf:
                    return nm, (canon or smi, ik, sf)
            return nm, None

        done = 0
        with ThreadPoolExecutor(max_workers=args.pubchem_workers) as ex:
            for nm, res in ex.map(pc, misses):
                if res:
                    cache[nm] = res
                cache["pubchem:" + nm] = (None, None, None)  # mark attempted
                done += 1
                if done % 1000 == 0:
                    save_struct_cache(cache)
                    got = sum(1 for v in cache.values() if v[1])
                    print(f"  ...PubChem {done:,}/{len(misses):,} (total resolved {got:,})",
                          flush=True)
        save_struct_cache(cache)

    resolved_names = {n: cache[n] for n in names if cache.get(n, (None,)*3)[1]}
    print(f"\nresolved names total: {len(resolved_names):,}/{len(names):,}", flush=True)
    ckh_struct = {k: resolved_names[n] for k, n in ckh_name.items() if n in resolved_names}

    # ---- apply additively + rebuild split ------------------------------------
    out = IREXP.with_suffix(".jsonl.new")
    filled = already = total = 0
    res_out = gzip.open("data/irexp_resolved/irexp_resolved.jsonl.gz", "wt")
    trip = 0
    with IREXP.open() as fin, out.open("w") as fout:
        for line in fin:
            r = json.loads(line); total += 1
            if not (r.get("selfies") or r.get("inchikey")):
                st = ckh_struct.get(ckh(r.get("h_nmr") or "", r.get("c_nmr") or "",
                                        r.get("ir_bands_cm-1") or []))
                if st:
                    r["smiles"], r["inchikey"], r["selfies"] = st
                    r["has_structure"] = True; filled += 1
            if r.get("selfies") or r.get("inchikey"):
                already += 1
                res_out.write(json.dumps(r, ensure_ascii=False) + "\n")
                if r.get("h_nmr") or r.get("c_nmr"):
                    trip += 1
            fout.write(json.dumps(r, ensure_ascii=False) + "\n")
    res_out.close(); os.replace(out, IREXP)
    with gzip.open("data/irexp/irexp.jsonl.gz", "wt") as g, IREXP.open() as f:
        for line in f:
            g.write(line)

    pct = 100 * already // total
    print("\n=== RESULT ===")
    print(f"records:              {total:,}")
    print(f"newly filled:         +{filled:,}")
    print(f"with structure now:   {already:,} ({pct}%)")
    print(f"100%-resolved split:  {already:,} records ({trip:,} with NMR)")

    json.dump({"records": total, "all_experimental_IR": total,
               "with_co_reported_NMR": sum(1 for l in IREXP.open()
                   if (json.loads(l).get("h_nmr") or json.loads(l).get("c_nmr"))),
               "with_structure": already,
               "note": ("IRexp experimental IR (PMC-OA CC-BY + Chemotion CC-BY-SA). "
                        "Structure resolved from in-text names via OPSIN (offline) + "
                        "PubChem fallback (trivial/natural-product names). "
                        "data/irexp_resolved/ is the 100%-structure-resolved split.")},
              open("data/irexp/irexp_stats.json", "w"), indent=2)
    json.dump({"records": already, "structure_resolution": "100% (by construction)",
               "with_co_reported_NMR": trip,
               "note": "Structure-complete split of IRexp (IR + structure on every record)."},
              open("data/irexp_resolved/stats.json", "w"), indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
