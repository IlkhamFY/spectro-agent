#!/usr/bin/env python3
"""
Split IRexp by *real* per-record licences (after `scripts/join_pmc_licences.py`).

Source discriminator (legacy / manuscript gate A): Chemotion DOI prefix 10.22000 vs PMC.
Licence discriminator (Sci Data / Zenodo): `license_pool` stamped on each record.

  python scripts/split_license_pools.py                  # report source + licence pools
  python scripts/split_license_pools.py --write OUT/      # write licence-pool files
  python scripts/split_license_pools.py --write-sources OUT/  # write pmc vs chemotion only

If records lack `license_pool` (pre-join corpus), this script refuses to invent CC-BY
and exits non-zero unless --allow-unstamped is passed (source split only).
"""
from __future__ import annotations

import gzip
import json
import os
import sys

SRC = "data/irexp/irexp.jsonl.gz"
CHEMOTION_DOI_PREFIX = "10.22000"

COMMERCIAL_POOL = "commercial"
POOL_ORDER = (
    "commercial",
    "non_commercial",
    "sharealike",
    "empty_unknown",
    "other",
)


def source_pool_of(rec: dict) -> str:
    """-> 'chemotion' or 'pmc' (provenance only; not a licence claim)."""
    doi = rec.get("source_doi") or ""
    return "chemotion" if doi.startswith(CHEMOTION_DOI_PREFIX) else "pmc"


# Back-compat alias used by scripts/check_manuscript.py gate A
pool_of = source_pool_of


def licence_pool_of(rec: dict) -> str | None:
    """Return stamped license_pool, or None if missing."""
    p = rec.get("license_pool")
    if p:
        return p
    lic = (rec.get("license") or "").upper().replace("_", "-")
    if lic in ("CC-BY-SA-4.0", "CC-BY-SA"):
        return "sharealike"
    if lic in ("CC-BY", "CC-BY-4.0", "CC0", "CC-ZERO"):
        return "commercial"
    if "NC" in lic:
        return "non_commercial"
    if lic in ("EMPTY", "UNKNOWN"):
        return "empty_unknown"
    if lic:
        return "other"
    return None


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = None
    write_sources = False
    allow_unstamped = "--allow-unstamped" in argv
    if "--write" in argv:
        out = argv[argv.index("--write") + 1]
    if "--write-sources" in argv:
        write_sources = True
        out = argv[argv.index("--write-sources") + 1]

    source_counts = {"pmc": 0, "chemotion": 0}
    licence_counts = {k: 0 for k in POOL_ORDER}
    license_label_counts: dict[str, int] = {}
    missing_stamp = 0
    n = 0

    handles = {}
    source_handles = {}
    if out:
        os.makedirs(out, exist_ok=True)
        if write_sources:
            source_handles = {
                k: gzip.open(f"{out}/irexp_{k}.jsonl.gz", "wt") for k in source_counts
            }
        else:
            handles = {
                k: gzip.open(f"{out}/irexp_{k}.jsonl.gz", "wt") for k in POOL_ORDER
            }

    for line in gzip.open(SRC, "rt"):
        rec = json.loads(line)
        n += 1
        sk = source_pool_of(rec)
        source_counts[sk] += 1
        lp = licence_pool_of(rec)
        if lp is None:
            missing_stamp += 1
            lp = "empty_unknown"
        if lp not in licence_counts:
            licence_counts[lp] = 0
        licence_counts[lp] += 1
        lab = rec.get("license") or "(unstamped)"
        license_label_counts[lab] = license_label_counts.get(lab, 0) + 1

        if source_handles:
            row = dict(rec)
            row.setdefault("license_pool", lp)
            source_handles[sk].write(json.dumps(row) + "\n")
        if handles:
            handles[lp].write(json.dumps(rec) + "\n")

    for h in list(handles.values()) + list(source_handles.values()):
        h.close()

    print(f"{SRC}: {n:,} records")
    print("Source pools (provenance; not licence claims):")
    for k in ("pmc", "chemotion"):
        print(f"  {k:<12} {source_counts[k]:>7,}")
    print("Licence pools (from stamped license_pool / license):")
    for k in POOL_ORDER:
        print(f"  {k:<16} {licence_counts.get(k, 0):>7,}")
    print("license labels:")
    for k, v in sorted(license_label_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<20} {v:>7,}")

    if missing_stamp:
        msg = (f"WARNING: {missing_stamp:,} records lack license_pool/license — "
               f"run scripts/join_pmc_licences.py first")
        print(msg, file=sys.stderr)
        if not allow_unstamped and not write_sources:
            return 2

    if out and not write_sources:
        print(f"\nwrote licence pools under {out}/ "
              f"(commercial = Zenodo primary; NC/empty/other held aside)")
        print("Commercial redistributable count: "
              f"{licence_counts.get(COMMERCIAL_POOL, 0):,}")
    elif out and write_sources:
        print(f"\nwrote provenance pools under {out}/ "
              f"(irexp_pmc.jsonl.gz, irexp_chemotion.jsonl.gz)")
    else:
        print("\nRe-run with --write OUT/ for licence pools, "
              "or --write-sources OUT/ for PMC vs Chemotion provenance files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
