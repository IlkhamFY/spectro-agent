#!/usr/bin/env python3
"""Apply Crossref / late Europe-PMC licence recovery for empty_unknown IRexp rows.

Policy (conservative — Sci Data honesty):
  - Promote empty/unknown → a licence pool **only** when Crossref exposes an
    explicit Creative Commons URL or ACS AuthorChoice CC-BY / CC-BY-NC* page,
    OR when a fresh Europe PMC query now returns a licence string.
  - Do **not** promote on Elsevier/Springer TDM-only Crossref licence links
    (those are text-mining terms, not article redistribution CC terms).

Inputs:
  data/audit/empty_licence_crossref_probe.json   (from probe run)
  data/irexp/irexp.jsonl.gz
  data/irexp/pmc_licence_lookup.jsonl.gz

Outputs:
  restamped irexp.jsonl.gz + licence_pools/* + pmc_licence_summary.json
  data/audit/empty_licence_recovery_summary.json

  python3 scripts/apply_crossref_licence_recovery.py
  python3 scripts/apply_crossref_licence_recovery.py --dry-run
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from join_pmc_licences import classify_epmc_license  # noqa: E402

PROBE = Path("data/audit/empty_licence_crossref_probe.json")
CORPUS = Path("data/irexp/irexp.jsonl.gz")
LOOKUP = Path("data/irexp/pmc_licence_lookup.jsonl.gz")
SUMMARY = Path("data/irexp/pmc_licence_summary.json")
OUT_AUDIT = Path("data/audit/empty_licence_recovery_summary.json")
POOLS = Path("data/irexp/licence_pools")


def promotions_from_probe(probe: dict) -> dict[str, dict]:
    """pmcid → {license, license_pool, license_raw, license_source, doi?}"""
    out: dict[str, dict] = {}
    for r in probe["records"]:
        pmcid = r["pmcid"]
        if r.get("status") == "epmc_now_has_license":
            lic, pool = classify_epmc_license(r.get("epmc_license"), found=True)
            out[pmcid] = {
                "license": lic,
                "license_pool": pool,
                "license_raw": r.get("epmc_license"),
                "license_source": "europepmc_requery",
                "doi": r.get("doi"),
            }
        elif r.get("pool") and r.get("license"):
            out[pmcid] = {
                "license": r["license"],
                "license_pool": r["pool"],
                "license_raw": (r.get("crossref_urls") or [None])[0],
                "license_source": "crossref",
                "doi": r.get("doi"),
                "crossref_urls": r.get("crossref_urls"),
            }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--probe", type=Path, default=PROBE)
    args = ap.parse_args()

    probe = json.loads(args.probe.read_text())
    promo = promotions_from_probe(probe)
    print(f"promotions ready for {len(promo)} PMCIDs", flush=True)

    # Update lookup cache in memory
    lookup: dict[str, dict] = {}
    with gzip.open(LOOKUP, "rt") as f:
        for line in f:
            row = json.loads(line)
            lookup[row["pmcid"]] = row

    for pmcid, meta in promo.items():
        row = lookup.get(pmcid, {"pmcid": pmcid, "found": True})
        row.update(
            {
                "license_raw": meta["license_raw"],
                "license": meta["license"],
                "license_pool": meta["license_pool"],
                "found": True,
                "license_source_override": meta["license_source"],
                "recovery_doi": meta.get("doi"),
                "recovered_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        if meta.get("crossref_urls"):
            row["crossref_urls"] = meta["crossref_urls"]
        lookup[pmcid] = row

    before = Counter()
    after = Counter()
    moved = Counter()
    n = 0
    stamped_rows: list[dict] = []

    with gzip.open(CORPUS, "rt") as f:
        for line in f:
            rec = json.loads(line)
            n += 1
            before[rec.get("license_pool")] += 1
            pmcid = rec.get("pmcid")
            if (
                rec.get("license_pool") == "empty_unknown"
                and pmcid
                and pmcid in promo
            ):
                old = rec.get("license_pool")
                meta = promo[pmcid]
                rec["license"] = meta["license"]
                rec["license_raw"] = meta["license_raw"]
                rec["license_pool"] = meta["license_pool"]
                rec["license_source"] = meta["license_source"]
                moved[(old, meta["license_pool"])] += 1
            after[rec.get("license_pool")] += 1
            stamped_rows.append(rec)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": probe["summary"]["policy"],
        "probe": str(args.probe),
        "pmcids_promoted": len(promo),
        "records_before_pools": dict(before),
        "records_after_pools": dict(after),
        "records_moved": {f"{a}->{b}": c for (a, b), c in moved.items()},
        "delta_commercial": after.get("commercial", 0) - before.get("commercial", 0),
        "delta_empty_unknown": after.get("empty_unknown", 0)
        - before.get("empty_unknown", 0),
        "total_records": n,
        "dry_run": args.dry_run,
    }
    print(json.dumps(summary, indent=2))

    if args.dry_run:
        OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
        OUT_AUDIT.write_text(json.dumps(summary, indent=2) + "\n")
        print("dry-run: no corpus rewrite")
        return 0

    # Rewrite lookup
    tmp_lookup = str(LOOKUP) + ".tmp"
    with gzip.open(tmp_lookup, "wt") as f:
        for pid in sorted(lookup):
            f.write(json.dumps(lookup[pid], ensure_ascii=False) + "\n")
    os.replace(tmp_lookup, LOOKUP)

    # Rewrite corpus
    tmp_corpus = str(CORPUS) + ".tmp"
    with gzip.open(tmp_corpus, "wt") as f:
        for rec in stamped_rows:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp_corpus, CORPUS)

    # Rewrite pools
    POOLS.mkdir(parents=True, exist_ok=True)
    handles = {
        k: gzip.open(POOLS / f"irexp_{k}.jsonl.gz", "wt")
        for k in ("commercial", "non_commercial", "sharealike", "empty_unknown", "other")
    }
    try:
        for rec in stamped_rows:
            pool = rec.get("license_pool") or "empty_unknown"
            if pool not in handles:
                pool = "other"
            handles[pool].write(json.dumps(rec, ensure_ascii=False) + "\n")
    finally:
        for h in handles.values():
            h.close()

    # Update pmc_licence_summary.json
    license_counts = Counter(r.get("license") for r in stamped_rows)
    pool_record_counts = Counter(r.get("license_pool") for r in stamped_rows)
    source_counts = Counter(
        "chemotion"
        if str(r.get("source_doi") or "").startswith("10.22000")
        else "pmc"
        for r in stamped_rows
    )
    pmcids = {r.get("pmcid") for r in stamped_rows if r.get("pmcid")}
    summary_doc = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "license_counts": dict(license_counts),
        "pool_record_counts": dict(pool_record_counts),
        "source_counts": dict(source_counts),
        "total_records": n,
        "unique_pmcids": len(pmcids),
        "rebuilt_from_stamped_corpus": True,
        "source": str(CORPUS),
        "crossref_recovery_applied": True,
        "crossref_recovery": {
            "pmcids_promoted": len(promo),
            "records_moved": summary["records_moved"],
            "delta_commercial": summary["delta_commercial"],
        },
        "policy": {
            "commercial_includes": ["CC0", "CC-BY"],
            "commercial_zenodo_primary": True,
            "empty_unknown": "excluded from commercial Zenodo pool",
            "non_commercial": "held aside in irexp_non_commercial.jsonl.gz",
            "other": "held aside (includes CC-BY-ND / non-CC terms)",
            "sharealike_includes": ["CC-BY-SA", "CC-BY-SA-4.0 (Chemotion)"],
            "crossref_recovery": (
                "empty/unknown promoted only on explicit CC / ACS AuthorChoice "
                "Crossref URLs or late Europe PMC licence strings; TDM-only ignored"
            ),
        },
        "pool_files": {
            "commercial": "data/irexp/licence_pools/irexp_commercial.jsonl.gz",
            "empty_unknown": "data/irexp/licence_pools/irexp_empty_unknown.jsonl.gz",
            "non_commercial": "data/irexp/licence_pools/irexp_non_commercial.jsonl.gz",
            "other": "data/irexp/licence_pools/irexp_other.jsonl.gz",
            "sharealike": "data/irexp/licence_pools/irexp_sharealike.jsonl.gz",
        },
    }
    SUMMARY.write_text(json.dumps(summary_doc, indent=2) + "\n")

    # Update irexp_stats.json lightly
    stats_path = Path("data/irexp/irexp_stats.json")
    if stats_path.exists():
        stats = json.loads(stats_path.read_text())
        stats["licence_pool_commercial"] = pool_record_counts.get("commercial", 0)
        stats["licence_pool_non_commercial"] = pool_record_counts.get(
            "non_commercial", 0
        )
        stats["licence_pool_sharealike"] = pool_record_counts.get("sharealike", 0)
        stats["licence_pool_empty_unknown"] = pool_record_counts.get(
            "empty_unknown", 0
        )
        stats["licence_pool_other"] = pool_record_counts.get("other", 0)
        stats["note"] = (
            stats.get("note", "")
            + " Crossref/EPMC empty-licence recovery applied 2026-08-27."
        )
        stats_path.write_text(json.dumps(stats, indent=2) + "\n")

    OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    OUT_AUDIT.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote stamped corpus, pools, {SUMMARY}, {OUT_AUDIT}")
    return 0


if __name__ == "__main__":
    # Fix import: join_pmc_licences lives under scripts/
    raise SystemExit(main())
