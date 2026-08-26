#!/usr/bin/env python3
"""
Join each PMC accession in IRexp to Europe PMC licence metadata, classify pools,
stamp every record, and write segregated release files.

  # lookup + stamp (network; resumable cache)
  python scripts/join_pmc_licences.py

  # report-only from an existing stamped corpus / cache
  python scripts/join_pmc_licences.py --report-only

Outputs (under data/irexp/ by default):
  pmc_licence_lookup.jsonl.gz   — one row per unique PMCID (cache)
  pmc_licence_summary.json      — counts + policy
  irexp.jsonl.gz                — full corpus with license* fields (in-place stamp)
  licence_pools/
    irexp_commercial.jsonl.gz       — Zenodo/Sci Data primary redistributable
    irexp_non_commercial.jsonl.gz   — NC* held aside
    irexp_sharealike.jsonl.gz       — Chemotion + any PMC CC-BY-SA
    irexp_empty_unknown.jsonl.gz    — empty / no EPMC hit (excluded from commercial)
    irexp_other.jsonl.gz            — other non-empty non-NC terms (e.g. ND)

Policy: keep the full corpus on disk with per-record licence; ship the commercial
pool as the primary redistributable artifact; exclude empty/unknown from that pool.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Iterable

EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CHEMOTION_DOI_PREFIX = "10.22000"
DEFAULT_SRC = "data/irexp/irexp.jsonl.gz"
DEFAULT_OUT_DIR = "data/irexp"
USER_AGENT = "spectro-agent-licence-join/1.0 (IRexp remediation; mailto:research@example.org)"

# Europe PMC `license` strings → (normalized SPDX-ish label, pool class)
# Pool classes:
#   commercial      — CC0 / CC-BY (primary Zenodo redistributable)
#   non_commercial  — any NC*
#   sharealike      — CC-BY-SA (PMC) — kept with Chemotion SA pool
#   other           — CC-BY-ND and other non-empty non-NC (held aside; ND blocks derivatives)
#   empty_unknown   — missing / no EPMC result
COMMERCIAL_RAW = {
    "cc0", "cc zero", "cc-zero", "public domain", "pd",
    "cc by", "cc-by", "cc by 4.0", "cc-by-4.0", "cc by 3.0", "cc-by-3.0",
}
SHAREALIKE_RAW = {
    "cc by-sa", "cc-by-sa", "cc by sa", "cc-by sa",
    "cc by-sa 4.0", "cc-by-sa-4.0", "cc by-sa 3.0", "cc-by-sa-3.0",
}
ND_RAW = {
    "cc by-nd", "cc-by-nd", "cc by nd", "cc-by nd",
    "cc by-nd 4.0", "cc-by-nd-4.0",
}
NC_PREFIXES = ("cc by-nc", "cc-by-nc", "cc by nc", "cc-by nc")


def _norm_key(raw: str | None) -> str:
    return " ".join((raw or "").strip().lower().replace("_", "-").split())


def classify_epmc_license(raw: str | None, *, found: bool) -> tuple[str, str]:
    """Return (normalized_license, pool_class)."""
    if not found:
        return "UNKNOWN", "empty_unknown"
    key = _norm_key(raw)
    if not key:
        return "EMPTY", "empty_unknown"
    if key in COMMERCIAL_RAW or key.startswith("cc by ") and "nc" not in key and "sa" not in key and "nd" not in key:
        # bare "cc by" / versioned BY
        if "nc" in key:
            pass
        elif "sa" in key:
            return "CC-BY-SA", "sharealike"
        elif "nd" in key:
            return "CC-BY-ND", "other"
        else:
            if key in ("cc0", "cc zero", "cc-zero", "public domain", "pd"):
                return "CC0", "commercial"
            return "CC-BY", "commercial"
    if key in SHAREALIKE_RAW or ("sa" in key and "nc" not in key and key.startswith("cc")):
        return "CC-BY-SA", "sharealike"
    if key in ND_RAW or ("nd" in key and "nc" not in key and key.startswith("cc")):
        return "CC-BY-ND", "other"
    if any(key.startswith(p) or p in key for p in NC_PREFIXES) or "nc" in key.split():
        # refine NC flavour
        if "nd" in key and "sa" in key:
            return "CC-BY-NC-ND", "non_commercial"  # unusual combo
        if "nd" in key:
            return "CC-BY-NC-ND", "non_commercial"
        if "sa" in key:
            return "CC-BY-NC-SA", "non_commercial"
        return "CC-BY-NC", "non_commercial"
    return (raw or "OTHER").strip().upper() or "OTHER", "other"


def pmc_accession(source_doi: str) -> str | None:
    """PMC:123 / PMC:PMC123 / PMC123 → PMC123."""
    if not source_doi:
        return None
    s = source_doi.strip()
    if s.upper().startswith("PMC:"):
        s = s.split(":", 1)[1]
    s = s.strip()
    if not s.upper().startswith("PMC"):
        if s.isdigit():
            return f"PMC{s}"
        return None
    num = s[3:] if s.upper().startswith("PMC") else s
    num = num.lstrip(":")
    if not num.isdigit():
        return None
    return f"PMC{num}"


def load_cache(path: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not os.path.exists(path):
        return out
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as f:
        for line in f:
            rec = json.loads(line)
            pid = rec.get("pmcid")
            if pid:
                out[pid] = rec
    return out


def write_cache(path: str, rows: Iterable[dict]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt") as f:
        for rec in rows:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def epmc_batch(pmcids: list[str], timeout: float = 90.0) -> dict[str, dict]:
    """Query Europe PMC for a batch of PMCIDs; return map pmcid → result fields."""
    q = " OR ".join(f"PMCID:{p}" for p in pmcids)
    params = urllib.parse.urlencode({
        "query": q,
        "format": "json",
        "resultType": "core",
        "pageSize": str(max(len(pmcids), 1)),
    })
    url = f"{EUROPEPMC}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    found: dict[str, dict] = {}
    for r in data.get("resultList", {}).get("result", []) or []:
        pid = r.get("pmcid")
        if not pid:
            continue
        if not pid.upper().startswith("PMC"):
            pid = f"PMC{pid}"
        found[pid] = {
            "pmcid": pid,
            "license_raw": r.get("license"),
            "doi": r.get("doi"),
            "isOpenAccess": r.get("isOpenAccess"),
            "inEPMC": r.get("inEPMC"),
            "found": True,
        }
    return found


def fetch_licences(
    pmcids: list[str],
    cache: dict[str, dict],
    *,
    batch_size: int = 80,
    workers: int = 6,
    sleep_s: float = 0.05,
    max_retries: int = 5,
) -> dict[str, dict]:
    pending = [p for p in pmcids if p not in cache]
    if not pending:
        return cache

    print(f"Europe PMC lookup: {len(pmcids):,} unique PMCIDs; "
          f"{len(cache):,} cached; {len(pending):,} to fetch "
          f"(batch={batch_size}, workers={workers})", flush=True)

    batches = [pending[i:i + batch_size] for i in range(0, len(pending), batch_size)]
    done = 0

    def one(batch: list[str]) -> dict[str, dict]:
        last_err = None
        for attempt in range(max_retries):
            try:
                found = epmc_batch(batch)
                # mark misses
                out = {}
                for p in batch:
                    if p in found:
                        row = found[p]
                    else:
                        row = {"pmcid": p, "license_raw": None, "found": False}
                    lic, pool = classify_epmc_license(row.get("license_raw"), found=row.get("found", True))
                    row["license"] = lic
                    row["license_pool"] = pool
                    row["queried_at"] = datetime.now(timezone.utc).isoformat()
                    out[p] = row
                time.sleep(sleep_s)
                return out
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                last_err = e
                time.sleep(min(2 ** attempt, 30))
        raise RuntimeError(f"EPMC batch failed after retries: {last_err}")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, b): b for b in batches}
        for fut in as_completed(futs):
            part = fut.result()
            cache.update(part)
            done += len(part)
            if done % 800 < batch_size or done >= len(pending):
                print(f"  fetched {min(done, len(pending)):,}/{len(pending):,}", flush=True)
    return cache


def stamp_and_split(
    src: str,
    out_dir: str,
    cache: dict[str, dict],
    *,
    write_pools: bool = True,
    rewrite_src: bool = True,
) -> dict:
    pools_dir = os.path.join(out_dir, "licence_pools")
    if write_pools:
        os.makedirs(pools_dir, exist_ok=True)

    pool_names = ("commercial", "non_commercial", "sharealike", "empty_unknown", "other")
    handles = {}
    if write_pools:
        handles = {
            k: gzip.open(os.path.join(pools_dir, f"irexp_{k}.jsonl.gz"), "wt")
            for k in pool_names
        }

    counts = Counter()
    license_counts = Counter()
    pool_record_counts = Counter()
    n = 0
    tmp_src = src + ".stamped.tmp" if rewrite_src else None
    out_f = gzip.open(tmp_src, "wt") if tmp_src else None

    try:
        with gzip.open(src, "rt") as f:
            for line in f:
                rec = json.loads(line)
                n += 1
                doi = rec.get("source_doi") or ""
                if doi.startswith(CHEMOTION_DOI_PREFIX):
                    rec["license"] = "CC-BY-SA-4.0"
                    rec["license_raw"] = "CC-BY-SA-4.0"
                    rec["license_pool"] = "sharealike"
                    rec["license_source"] = "chemotion"
                    counts["chemotion"] += 1
                else:
                    pid = pmc_accession(doi)
                    if not pid:
                        rec["license"] = "UNKNOWN"
                        rec["license_raw"] = None
                        rec["license_pool"] = "empty_unknown"
                        rec["license_source"] = "unrecognised_doi"
                        counts["unrecognised"] += 1
                    else:
                        meta = cache.get(pid) or {
                            "pmcid": pid, "license_raw": None, "found": False,
                        }
                        found = bool(meta["found"]) if "found" in meta else False
                        lic, pool = classify_epmc_license(meta.get("license_raw"), found=found)
                        rec["license"] = lic
                        rec["license_raw"] = meta.get("license_raw")
                        rec["license_pool"] = pool
                        rec["license_source"] = "europepmc"
                        rec["pmcid"] = pid
                        counts["pmc"] += 1

                license_counts[rec["license"]] += 1
                pool_record_counts[rec["license_pool"]] += 1
                if out_f:
                    out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if handles:
                    handles[rec["license_pool"]].write(json.dumps(rec, ensure_ascii=False) + "\n")
    finally:
        if out_f:
            out_f.close()
        for h in handles.values():
            h.close()

    if tmp_src:
        os.replace(tmp_src, src)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": src,
        "total_records": n,
        "source_counts": dict(counts),
        "license_counts": dict(license_counts),
        "pool_record_counts": dict(pool_record_counts),
        "unique_pmcids": len(cache),
        "pmcid_license_counts": dict(Counter(
            (c.get("license") or "UNKNOWN") for c in cache.values()
        )),
        "pmcid_pool_counts": dict(Counter(
            (c.get("license_pool") or "empty_unknown") for c in cache.values()
        )),
        "policy": {
            "commercial_zenodo_primary": True,
            "commercial_includes": ["CC0", "CC-BY"],
            "sharealike_includes": ["CC-BY-SA", "CC-BY-SA-4.0 (Chemotion)"],
            "non_commercial": "held aside in irexp_non_commercial.jsonl.gz",
            "empty_unknown": "excluded from commercial Zenodo pool",
            "other": "held aside (includes CC-BY-ND / non-CC terms)",
        },
        "pool_files": {
            k: os.path.join(pools_dir, f"irexp_{k}.jsonl.gz") for k in pool_names
        } if write_pools else {},
    }
    return summary


def print_report(summary: dict) -> None:
    print(f"\nTotal records: {summary['total_records']:,}")
    print("By source:")
    for k, v in sorted(summary.get("source_counts", {}).items()):
        print(f"  {k:<16} {v:>8,}")
    print("By license_pool (records):")
    for k, v in sorted(summary.get("pool_record_counts", {}).items(), key=lambda kv: -kv[1]):
        print(f"  {k:<16} {v:>8,}")
    print("By license (records):")
    for k, v in sorted(summary.get("license_counts", {}).items(), key=lambda kv: -kv[1]):
        print(f"  {k:<16} {v:>8,}")
    print("Unique PMCID licence (articles):")
    for k, v in sorted(summary.get("pmcid_license_counts", {}).items(), key=lambda kv: -kv[1]):
        print(f"  {k:<16} {v:>8,}")


def collect_pmcids(src: str) -> list[str]:
    seen = set()
    out = []
    with gzip.open(src, "rt") as f:
        for line in f:
            doi = json.loads(line).get("source_doi") or ""
            if doi.startswith(CHEMOTION_DOI_PREFIX):
                continue
            pid = pmc_accession(doi)
            if pid and pid not in seen:
                seen.add(pid)
                out.append(pid)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    ap.add_argument("--cache", default=None, help="lookup cache path (default: OUT/pmc_licence_lookup.jsonl.gz)")
    ap.add_argument("--batch-size", type=int, default=80)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--report-only", action="store_true",
                    help="Do not hit the network; summarise from stamped src / cache")
    ap.add_argument("--no-rewrite-src", action="store_true",
                    help="Do not overwrite SRC; only write pool files + summary")
    ap.add_argument("--no-pools", action="store_true")
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    cache_path = args.cache or os.path.join(args.out_dir, "pmc_licence_lookup.jsonl.gz")
    cache = load_cache(cache_path)

    if not args.report_only:
        pmcids = collect_pmcids(args.src)
        cache = fetch_licences(
            pmcids, cache,
            batch_size=args.batch_size,
            workers=args.workers,
        )
        # persist classified cache
        rows = []
        for p in sorted(cache):
            row = dict(cache[p])
            lic, pool = classify_epmc_license(row.get("license_raw"), found=bool(row.get("found", True)))
            row["license"] = lic
            row["license_pool"] = pool
            rows.append(row)
        write_cache(cache_path, rows)
        cache = {r["pmcid"]: r for r in rows}
        print(f"Wrote cache {cache_path} ({len(cache):,} PMCIDs)", flush=True)

        summary = stamp_and_split(
            args.src, args.out_dir, cache,
            write_pools=not args.no_pools,
            rewrite_src=not args.no_rewrite_src,
        )
    else:
        # rebuild summary from stamped file if possible
        if not cache:
            print("No cache and --report-only; scanning stamped records only", flush=True)
        summary = stamp_and_split(
            args.src, args.out_dir, cache,
            write_pools=not args.no_pools,
            rewrite_src=False if args.report_only else not args.no_rewrite_src,
        )
        # if report-only, avoid rewriting pools unless asked — re-run stamp with no rewrite
        # Above already wrote pools; for pure report, use --no-pools

    summary_path = os.path.join(args.out_dir, "pmc_licence_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print_report(summary)
    print(f"\nSummary: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
