#!/usr/bin/env python3
"""
Additively raise IRexp structure-resolution by re-running the *improved* name
capture over the source papers and attaching resolved structures to the existing
records -- without disturbing the spectra payloads or the record set.

The existing IRexp records store only spectra (no name), so structure can't be
re-derived in place. But the record content key ``(h_nmr, c_nmr, ir_bands)`` is
stable and unchanged by the name-capture improvements, so we:

  1. re-fetch each source PMC paper (PMC-OA S3, no rate limit, resumable),
  2. re-extract with the improved extractor -> (content-key -> cleaned name),
  3. batch-resolve unique names via OPSIN -> SMILES -> RDKit InChIKey + SELFIES,
  4. stream the existing irexp.jsonl and fill smiles/selfies/inchikey on every
     record whose content key now has a resolved structure.

Resumable: fetched texts are cached on disk and the name map is checkpointed, so
a container restart just continues.

    python scripts/reresolve_structures.py            # full corpus
    python scripts/reresolve_structures.py --limit 500  # quick partial
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.extract import extract_records              # noqa: E402
from spectro_scraper.normalize import (                          # noqa: E402
    to_spectro_h, to_spectro_c, name_to_smiles, canonical_and_keys)

S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
IREXP = Path("data/irexp/irexp.jsonl")
CACHE = Path("data/cache/pmc_text")
NAME_MAP = Path("data/cache/ckh_name.jsonl")     # checkpoint: {ckh, name}
DONE = Path("data/cache/reresolve_done.txt")


def ckh(h_nmr: str, c_nmr: str, ir_bands) -> str:
    """Stable content-key hash for a record (matches across re-extraction)."""
    s = (h_nmr or "") + "" + (c_nmr or "") + "" + \
        ",".join(str(b) for b in (ir_bands or []))
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def s3_txt(num: str) -> str:
    p = CACHE / f"{num}.txt"
    if p.exists() and p.stat().st_size > 0:
        return p.read_text(errors="replace")
    for v in (1, 2):
        try:
            req = urllib.request.Request(f"{S3}/PMC{num}.{v}/PMC{num}.{v}.txt",
                                         headers={"User-Agent": "spectro-agent"})
            t = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            CACHE.mkdir(parents=True, exist_ok=True)
            p.write_text(t)
            return t
        except Exception:
            continue
    return ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=24)
    args = ap.parse_args(argv)

    # distinct PMC ids present in the dataset
    pmc = []
    seen = set()
    for line in IREXP.open():
        sd = json.loads(line).get("source_doi") or ""
        if isinstance(sd, str) and sd.startswith("PMC:"):
            n = sd.split(":", 1)[1]
            if n not in seen:
                seen.add(n); pmc.append(n)
    if args.limit:
        pmc = pmc[:args.limit]
    print(f"{len(pmc):,} distinct PMC papers to (re)process", flush=True)

    done = set(DONE.read_text().split()) if DONE.exists() else set()
    todo = [n for n in pmc if n not in done]
    print(f"  {len(done):,} already done, {len(todo):,} to go", flush=True)

    # ---- Phase 1: fetch + re-extract -> (content-key -> name) -----------------
    NAME_MAP.parent.mkdir(parents=True, exist_ok=True)
    nmf = NAME_MAP.open("a")
    donef = DONE.open("a")

    def work(num):
        txt = s3_txt(num)
        pairs = []
        if txt:
            for rec in extract_records(txt):
                if rec.ir_bands and rec.name:
                    pairs.append((ckh(to_spectro_h(rec), to_spectro_c(rec),
                                      rec.ir_bands), rec.name))
        return num, pairs

    processed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for num, pairs in ex.map(work, todo):
            for k, name in pairs:
                nmf.write(json.dumps({"k": k, "n": name}, ensure_ascii=False) + "\n")
            donef.write(num + "\n")
            processed += 1
            if processed % 500 == 0:
                nmf.flush(); donef.flush()
                print(f"  ...{processed:,}/{len(todo):,} papers", flush=True)
    nmf.close(); donef.close()

    # ---- Phase 2: resolve unique names via OPSIN -----------------------------
    ckh_name = {}
    for line in NAME_MAP.open():
        d = json.loads(line)
        ckh_name.setdefault(d["k"], d["n"])
    names = sorted({n for n in ckh_name.values()})
    print(f"\n{len(ckh_name):,} content-keys carry a name; {len(names):,} unique names",
          flush=True)

    from py2opsin import py2opsin
    smis = py2opsin(names) if names else []
    name_struct = {}
    ok = 0
    for nm, smi in zip(names, smis if isinstance(smis, list) else []):
        if not smi:
            continue
        canon, inchikey, selfies = canonical_and_keys(smi)
        if inchikey and selfies:
            name_struct[nm] = (canon or smi, inchikey, selfies)
            ok += 1
    print(f"OPSIN+RDKit resolved {ok:,}/{len(names):,} unique names", flush=True)

    ckh_struct = {k: name_struct[n] for k, n in ckh_name.items() if n in name_struct}
    print(f"{len(ckh_struct):,} content-keys now resolve to a structure", flush=True)

    # ---- Phase 3: apply additively to the dataset ----------------------------
    out = IREXP.with_suffix(".jsonl.new")
    filled = already = 0
    total = 0
    with IREXP.open() as fin, out.open("w") as fout:
        for line in fin:
            r = json.loads(line)
            total += 1
            has = bool(r.get("selfies") or r.get("inchikey"))
            if has:
                already += 1
            else:
                k = ckh(r.get("h_nmr") or "", r.get("c_nmr") or "",
                        r.get("ir_bands_cm-1") or [])
                st = ckh_struct.get(k)
                if st:
                    r["smiles"], r["inchikey"], r["selfies"] = st
                    r["has_structure"] = True
                    filled += 1
            fout.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(out, IREXP)

    now = already + filled
    print("\n=== RESULT ===")
    print(f"records:                 {total:,}")
    print(f"had structure before:    {already:,} ({100*already//total}%)")
    print(f"newly filled:            +{filled:,}")
    print(f"with structure now:      {now:,} ({100*now//total}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
