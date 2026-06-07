#!/usr/bin/env python3
"""
S3 IR harvester -- the fast path to 250k experimental IR.

NCBI/EBI APIs are polite-rate-limited (~3-6 req/s). The PMC Open-Access AWS
bucket (s3://pmc-oa-opendata, public, no auth, NO rate limit) serves the same
full text as plain .txt at `PMC<id>.<v>/PMC<id>.<v>.txt`. Fetching from S3 at
high concurrency flips the bottleneck from network to CPU (~tens-to-hundreds of
papers/sec), so 250k becomes hours not days.

Discovery: NCBI esearch (cheap) enumerates IR-reporting OA PMCIDs across the
corpus (year/month sliced). Fetch: S3 .txt, many workers. Extract: local
regex -> IR band lists (same engine, instrument-range filtered). Streaming,
deduped, resumable (shared ir.jsonl / seen_papers with the API crawl).

    python scripts/s3_ir_harvest.py --target 250000 --out data/irexp --workers 48
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.discover import search_ncbi_pmc            # noqa: E402
from spectro_scraper.extract import extract_records, normalize_text  # noqa: E402
from spectro_scraper.normalize import to_spectro_h, to_spectro_c     # noqa: E402

S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
# Target papers with real per-compound IR *characterization* (a method tag), not
# generic "cm-1"/"infrared" mentions (materials/analytical prose -> false IR).
IR_MARK = ('("IR (KBr" OR "IR (neat" OR "IR (ATR" OR "IR (film" OR "IR (CHCl" '
           'OR "FT-IR (" OR "FTIR (" OR "IR (thin" OR "νmax" OR "ν max" '
           'OR "IR (Nujol" OR "ATR-FTIR" OR "ATR-IR" OR "IR (cm" OR "IR(KBr" '
           'OR "(KBr): " OR "(neat): " OR "(ATR): " OR "cm-1" OR "cm−1")')
YEARS = list(range(2026, 2004, -1))


def s3_txt(num: str) -> str:
    for v in (1, 2):
        try:
            req = urllib.request.Request(f"{S3}/PMC{num}.{v}/PMC{num}.{v}.txt",
                                         headers={"User-Agent": "spectro-agent"})
            return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        except Exception:
            continue
    return ""


def _hash(r: dict) -> str:
    ir = ",".join(str(b) for b in (r.get("ir_bands_cm-1") or []))
    return hashlib.sha256((ir + "##" + (r.get("h_nmr") or "")).encode()).hexdigest()[:20]


def collect(num: str):
    txt = s3_txt(num)
    if not txt:
        return num, []
    out = []
    for rec in extract_records(normalize_text(txt)):
        if not rec.ir_bands:
            continue
        out.append({
            "ir_bands_cm-1": rec.ir_bands, "ir_raw": rec.ir,
            "h_nmr": to_spectro_h(rec), "c_nmr": to_spectro_c(rec),
            "name": rec.name, "source_doi": f"PMC:{num}",
        })
    return num, out


def discover_nums(seen: set, want: int) -> list:
    nums, got = [], set()
    need = min(max(want, 1) * 3, 400000)
    for year in YEARS:
        for month in range(1, 13):
            term = f'{IR_MARK} AND {year}/{month:02d}[pdat] AND open access[filter]'
            try:
                papers, _ = search_ncbi_pmc(term, retmax=9000)
            except Exception:
                continue
            for p in papers:
                num = (p.doi or "").split(":", 1)[-1]
                if num and num not in seen and num not in got:
                    got.add(num); nums.append(num)
            time.sleep(0.34)
            if len(nums) >= need:
                return nums
    return nums


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=250000)
    ap.add_argument("--out", default="data/irexp")
    ap.add_argument("--workers", type=int, default=48)
    args = ap.parse_args(argv)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    keys, seen = set(), set()
    jf_p, pf_p = out / "ir.jsonl", out / "seen_papers.txt"
    if jf_p.exists():
        for l in jf_p.open():
            try:
                r = json.loads(l); keys.add(_hash(r))
            except Exception:
                pass
    if pf_p.exists():
        seen = {x.split(":")[-1] for x in pf_p.read_text().split()}
    kept = sum(1 for _ in jf_p.open()) if jf_p.exists() else 0
    print(f"resume: {kept} IR records, {len(seen)} papers done", flush=True)

    nums = discover_nums(seen, args.target - kept)
    print(f"discovered {len(nums)} fresh IR PMCIDs (S3 path); target {args.target}",
          flush=True)

    jf = jf_p.open("a"); pf = pf_p.open("a")
    t0 = time.time(); dp = 0; nmr = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(collect, n): n for n in nums}
        try:
            for fut in as_completed(futs):
                dp += 1
                try:
                    num, recs = fut.result()
                except Exception:
                    num, recs = futs[fut], []
                pf.write(f"PMC:{num}\n")
                for r in recs:
                    k = _hash(r)
                    if k in keys:
                        continue
                    keys.add(k); jf.write(json.dumps(r, ensure_ascii=False) + "\n")
                    kept += 1; nmr += bool(r.get("h_nmr") or r.get("c_nmr"))
                if dp % 500 == 0:
                    jf.flush(); pf.flush()
                    rate = dp / max(time.time() - t0, 1)
                    print(f"  papers={dp} IRrecords={kept} (NMR {nmr}) "
                          f"{rate:.0f} papers/s, {kept/max(time.time()-t0,1)*60:.0f} IR/min",
                          flush=True)
                if kept >= args.target:
                    break
        finally:
            ex.shutdown(wait=False, cancel_futures=True)
            jf.flush(); pf.flush(); jf.close(); pf.close()
    print(f"\n=== S3 IRexp: {kept} IR records ({nmr} NMR-paired) from {dp} papers "
          f"in {(time.time()-t0)/60:.1f} min ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
