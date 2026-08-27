#!/usr/bin/env python3
"""Extraction-recall *proxy* audit for IRexp (PMC OA).

True recall needs a human to mark every IR characterisation string in a paper.
This script provides a reproducible **automatic proxy on the harvest path**:

  1. Reservoir-sample n distinct PMC source articles that contributed ≥1 IRexp row.
  2. Re-fetch PMC-OA S3 plain text (same path as ``scripts/s3_ir_harvest.py``);
     fall back to Europe PMC XML only if S3 misses.
  3. Re-run spectro_scraper.extract.extract_records (same gates as harvest).
  4. Compare re-extracted IR band-sets to the released IRexp rows for that PMCID
     (integer ±1 cm⁻¹ multiset overlap).

Metrics:
  - released-band confirmation in re-extract (precision of release vs parser)
  - list-level recall proxy: fraction of released IR lists recovered
  - papers where re-extract finds *extra* lists vs curated release

Not a substitute for human recall; it bounds parser self-consistency on the
text actually harvested.

  python3 scripts/audit_extraction_recall.py --n 40 --seed 0
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from spectro_scraper.extract import extract_records, normalize_text  # noqa: E402

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML"
S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
CORPUS = "data/irexp/irexp.jsonl.gz"


def _band_key(bands: list[float]) -> frozenset[int]:
    return frozenset(int(round(b)) for b in bands)


def _near(a: frozenset[int], b: frozenset[int]) -> bool:
    if not a or not b:
        return False
    small, large = (a, b) if len(a) <= len(b) else (b, a)
    return all(any((x + d) in large for d in (0, -1, 1)) for x in small)


def load_by_pmcid(path: str) -> dict[str, list[dict]]:
    by: dict[str, list[dict]] = defaultdict(list)
    with gzip.open(path, "rt") as f:
        for line in f:
            d = json.loads(line)
            doi = str(d.get("source_doi") or "")
            if not doi.startswith("PMC"):
                continue
            num = doi.replace("PMC:", "").replace("PMC", "")
            by["PMC" + num].append(d)
    return by


def fetch_s3(pmcid: str) -> str | None:
    num = pmcid.replace("PMC", "")
    for v in (1, 2):
        try:
            req = urllib.request.Request(
                f"{S3}/PMC{num}.{v}/PMC{num}.{v}.txt",
                headers={"User-Agent": "spectro-agent-qc"},
            )
            return urllib.request.urlopen(req, timeout=25).read().decode(
                "utf-8", "replace"
            )
        except Exception:
            continue
    return None


def fetch_epmc(pmcid: str) -> str | None:
    try:
        with urllib.request.urlopen(EPMC.format(pmcid), timeout=45) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="data/audit/extraction_recall_proxy.json")
    args = ap.parse_args()

    by = load_by_pmcid(CORPUS)
    pmcids = sorted(by.keys())
    rng = random.Random(args.seed)
    sample = rng.sample(pmcids, min(args.n, len(pmcids)))

    rows = []
    papers_ok = 0
    released_bands_total = released_bands_hit = 0
    reextract_lists = matched_lists = 0
    unmatched_released = 0
    released_lists_total = 0
    extra_list_papers = 0
    src_counts: dict[str, int] = defaultdict(int)

    for i, pmcid in enumerate(sample, 1):
        text = fetch_s3(pmcid)
        source = "s3" if text else None
        if not text:
            text = fetch_epmc(pmcid)
            source = "epmc" if text else None
        if not text:
            rows.append({"pmcid": pmcid, "status": "unfetchable"})
            continue
        papers_ok += 1
        src_counts[source] += 1

        released = by[pmcid]
        released_keys = [_band_key(r.get("ir_bands_cm-1") or []) for r in released]
        re_recs = [r for r in extract_records(normalize_text(text)) if r.ir_bands]
        re_keys = [_band_key(r.ir_bands) for r in re_recs]

        re_nums: set[int] = set()
        for k in re_keys:
            re_nums |= set(k)
            for x in k:
                re_nums |= {x - 1, x + 1}
        rb = sum(len(k) for k in released_keys)
        rh = sum(1 for k in released_keys for b in k if b in re_nums)
        released_bands_total += rb
        released_bands_hit += rh

        reextract_lists += len(re_keys)
        hits = sum(1 for rk in re_keys if any(_near(rk, lk) for lk in released_keys))
        matched_lists += hits
        orphan = sum(
            1 for lk in released_keys if not any(_near(lk, rk) for rk in re_keys)
        )
        unmatched_released += orphan
        released_lists_total += len(released_keys)
        extra = len(re_keys) > len(released_keys)
        if extra:
            extra_list_papers += 1

        rows.append(
            {
                "pmcid": pmcid,
                "status": "ok",
                "text_source": source,
                "n_released_rows": len(released),
                "n_reextract_ir_lists": len(re_keys),
                "released_bands": rb,
                "released_bands_in_reextract": rh,
                "reextract_lists_matched": hits,
                "released_lists_unmatched": orphan,
                "extra_reextract_vs_release": extra,
            }
        )
        print(
            f"  [{i:>3}/{len(sample)}] {pmcid:<14} src={source} "
            f"released={len(released)} re={len(re_keys)} "
            f"bands {rh}/{rb} orphan_rel={orphan}",
            flush=True,
        )

    def wilson_ci(successes: int, n: int, z: float = 1.96):
        if n <= 0:
            return None
        p = successes / n
        denom = 1 + z * z / n
        centre = p + z * z / (2 * n)
        margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
        return [
            round((centre - margin) / denom, 4),
            round((centre + margin) / denom, 4),
        ]

    ok = [r for r in rows if r.get("status") == "ok"]
    full = sum(1 for r in ok if r.get("released_lists_unmatched", 0) == 0)
    list_recall = 1 - unmatched_released / max(released_lists_total, 1)
    summary = {
        "method": (
            "Automatic recall proxy on the harvest path: re-fetch PMC-OA S3 plain "
            "text (fallback Europe PMC XML); re-run extract_records; compare IR "
            "band-sets to released IRexp rows for the same PMCID (±1 cm⁻¹). "
            "Not a human recall audit."
        ),
        "sampled_papers": len(sample),
        "fetched": papers_ok,
        "pool_pmcs": len(pmcids),
        "seed": args.seed,
        "n": args.n,
        "text_sources": dict(src_counts),
        "released_bands_confirmed_in_reextract": {
            "hit": released_bands_hit,
            "total": released_bands_total,
            "rate": round(released_bands_hit / released_bands_total, 4)
            if released_bands_total
            else None,
            "wilson95": wilson_ci(released_bands_hit, released_bands_total)
            if released_bands_total
            else None,
        },
        "reextract_lists_matched_to_release": {
            "matched": matched_lists,
            "total": reextract_lists,
            "rate": round(matched_lists / reextract_lists, 4)
            if reextract_lists
            else None,
            "wilson95": wilson_ci(matched_lists, reextract_lists)
            if reextract_lists
            else None,
        },
        "list_level_recall_proxy": round(list_recall, 4),
        "list_level_recall_proxy_wilson95": wilson_ci(
            released_lists_total - unmatched_released, released_lists_total
        )
        if released_lists_total
        else None,
        "released_lists_unmatched_total": unmatched_released,
        "released_lists_total": released_lists_total,
        "papers_all_released_lists_recovered": {
            "count": full,
            "of": len(ok),
            "rate": round(full / len(ok), 4) if ok else None,
            "wilson95": wilson_ci(full, len(ok)) if ok else None,
        },
        "papers_with_extra_reextract_lists": extra_list_papers,
    }
    out = {"summary": summary, "records": rows}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
