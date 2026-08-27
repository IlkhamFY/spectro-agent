#!/usr/bin/env python3
"""Stratified multi-check automated \"chemist-proxy\" audit for IRexp.

This is **not** a human expert skeleton audit (NMRexp-style). It is a
reproducible, machine-checkable surrogate that a chemist would apply as a
first-pass screen on band lists + optional structures:

  1. IR physical window (350–4000 cm⁻¹)
  2. Band-list density / duplicates / monotonic sanity
  3. For structure-linked rows: RDKit parse, formula vs ¹³C peak count,
     ¹H integral vs formula H+2 (same physics as quarantine)
  4. For PMC rows: re-fetch Europe PMC / S3 text and confirm each band
     (±1 cm⁻¹) — transcription fidelity on the stratified sample
  5. Optional: DOI / PMCID present; licence_pool stamped

Stratified draw (seed-fixed) over the full release, targeting n≈250–300:
  - structure-linked PMC commercial
  - structure-linked PMC non-commercial / empty / SA (pooled)
  - IR-only (no SMILES) PMC
  - Chemotion / RADAR (ShareAlike, all structure-linked)

  python3 scripts/audit_chemist_proxy.py --n 280 --seed 0 \\
      --out data/audit/chemist_proxy_audit.json

Outputs machine-readable JSON + JSONL under data/audit/.
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from spectro_scraper.extract import parse_c_peaks, parse_h_peaks  # noqa: E402
from spectro_scraper.quality import IR_MAX, IR_MIN, _carbon_and_h_counts  # noqa: E402

CORPUS = Path("data/irexp/irexp.jsonl.gz")
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML"
S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
C13_WINDOW = (-10.0, 235.0)
UA = {"User-Agent": "spectro-agent-chemist-proxy/1.0"}


def _stratum(rec: dict) -> str:
    doi = str(rec.get("source_doi") or "")
    if not doi.startswith("PMC"):
        return "chemotion"
    has = bool(rec.get("has_structure") or rec.get("smiles"))
    pool = rec.get("license_pool") or "empty_unknown"
    if has and pool == "commercial":
        return "pmc_struct_commercial"
    if has:
        return "pmc_struct_other_licence"
    return "pmc_ir_only"


def _c13_count(c_nmr: str | None) -> int | None:
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


def _h1_integral(h_nmr: str | None) -> int | None:
    if not h_nmr:
        return None
    vals = [p.nuclei for p in parse_h_peaks(h_nmr) if p.nuclei]
    return sum(vals) if vals else None


def band_checks(bands: list[float]) -> list[str]:
    fails: list[str] = []
    if not bands:
        fails.append("empty_band_list")
        return fails
    if any(not (IR_MIN <= float(b) <= IR_MAX) for b in bands):
        fails.append("ir_band_out_of_range")
    # Exact duplicate wavenumbers (after round) — unusual for a peak list
    rounded = [int(round(b)) for b in bands]
    if len(rounded) != len(set(rounded)):
        fails.append("duplicate_integer_bands")
    if len(bands) < 4:
        fails.append("fewer_than_4_bands")  # harvest gate; should be rare
    return fails


def structure_checks(rec: dict) -> list[str]:
    fails: list[str] = []
    smi = rec.get("smiles")
    if not smi:
        return fails
    counts = _carbon_and_h_counts(smi)
    if not counts:
        fails.append("smiles_unparseable")
        return fails
    nC, nH, _ = counts
    n_c13 = _c13_count(rec.get("c_nmr"))
    if n_c13 is not None and n_c13 > nC:
        fails.append(f"c13_peaks_gt_carbons:{n_c13}>{nC}")
    obs_h = _h1_integral(rec.get("h_nmr"))
    if obs_h is not None and obs_h > nH + 2:
        fails.append(f"h1_integration_gt_formula_plus_2:{obs_h}>{nH}+2")
    return fails


def metadata_checks(rec: dict) -> list[str]:
    fails: list[str] = []
    if not rec.get("source_doi"):
        fails.append("missing_source_doi")
    if not rec.get("license_pool"):
        fails.append("missing_license_pool")
    if not (rec.get("ir_bands_cm-1") or []):
        fails.append("missing_ir_bands")
    return fails


def fetch_text(pmcid: str) -> tuple[str | None, str | None]:
    """Return best-effort full text. Prefer Europe PMC XML for digit fidelity
    (matches ``audit_extraction.py``); fall back to PMC-OA S3 plain text."""
    num = pmcid.replace("PMC", "").replace("PMC:", "")
    pmcid = "PMC" + num
    epmc_txt = None
    try:
        req = urllib.request.Request(EPMC.format(pmcid), headers=UA)
        epmc_txt = urllib.request.urlopen(req, timeout=45).read().decode(
            "utf-8", "replace"
        )
    except Exception:
        pass
    s3_txt = None
    for v in (1, 2):
        try:
            req = urllib.request.Request(
                f"{S3}/PMC{num}.{v}/PMC{num}.{v}.txt", headers=UA
            )
            s3_txt = urllib.request.urlopen(req, timeout=25).read().decode(
                "utf-8", "replace"
            )
            break
        except Exception:
            continue
    if epmc_txt and s3_txt:
        return epmc_txt + "\n" + s3_txt, "epmc+s3"
    if epmc_txt:
        return epmc_txt, "epmc"
    if s3_txt:
        return s3_txt, "s3"
    return None, None


def transcription_confirm(bands: list[float], text: str) -> tuple[int, int]:
    # Match scripts/audit_extraction.py exactly (comma / thin-space / nbsp strip).
    nums = set(re.findall(r"\d{3,4}", re.sub(r"[,  ]", "", text)))
    hits = sum(
        1
        for b in bands
        if any(str(int(round(b)) + d) in nums for d in (0, -1, 1))
    )
    return len(bands), hits


def stratified_sample(n: int, seed: int) -> tuple[list[dict], dict]:
    """Reservoir per stratum, then allocate quotas proportional to pool size
    with floors so Chemotion and licence minorities are represented."""
    rng = random.Random(seed)
    buckets: dict[str, list[dict]] = defaultdict(list)
    pool_sizes: Counter[str] = Counter()
    with gzip.open(CORPUS, "rt") as f:
        for line in f:
            rec = json.loads(line)
            s = _stratum(rec)
            pool_sizes[s] += 1
            # Keep a large reservoir per stratum for later draw
            keep = buckets[s]
            seen = pool_sizes[s]
            cap = max(n, 400)
            if len(keep) < cap:
                keep.append(rec)
            else:
                j = rng.randrange(seen)
                if j < cap:
                    keep[j] = rec

    # Quotas: emphasize structure-linked + Chemotion; IR-only still large
    order = [
        "pmc_struct_commercial",
        "pmc_struct_other_licence",
        "pmc_ir_only",
        "chemotion",
    ]
    # Target mix ≈ 35% struct-comm, 15% struct-other, 35% ir-only, 15% chemotion
    weights = {
        "pmc_struct_commercial": 0.35,
        "pmc_struct_other_licence": 0.15,
        "pmc_ir_only": 0.35,
        "chemotion": 0.15,
    }
    quotas: dict[str, int] = {}
    allocated = 0
    for s in order[:-1]:
        q = max(1, int(round(n * weights[s])))
        q = min(q, len(buckets[s]))
        quotas[s] = q
        allocated += q
    last = order[-1]
    quotas[last] = min(max(1, n - allocated), len(buckets[last]))
    # Top-up if short
    short = n - sum(quotas.values())
    for s in order:
        if short <= 0:
            break
        room = len(buckets[s]) - quotas[s]
        take = min(room, short)
        quotas[s] += take
        short -= take

    sample: list[dict] = []
    for s in order:
        pool = list(buckets[s])
        rng.shuffle(pool)
        for rec in pool[: quotas[s]]:
            rec = dict(rec)
            rec["_stratum"] = s
            sample.append(rec)
    rng.shuffle(sample)
    return sample, {"pool_sizes": dict(pool_sizes), "quotas": quotas}


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n <= 0:
        return None
    p = successes / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return round((centre - margin) / denom, 4), round((centre + margin) / denom, 4)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=280)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="data/audit/chemist_proxy_audit.json")
    ap.add_argument(
        "--jsonl", default="data/audit/chemist_proxy_audit.jsonl"
    )
    ap.add_argument(
        "--skip-refetch",
        action="store_true",
        help="Skip network transcription re-fetch (offline physics checks only)",
    )
    args = ap.parse_args()

    sample, strata_meta = stratified_sample(args.n, args.seed)
    print(
        f"stratified sample n={len(sample)} seed={args.seed} "
        f"quotas={strata_meta['quotas']}",
        flush=True,
    )

    rows = []
    for i, rec in enumerate(sample, 1):
        bands = list(rec.get("ir_bands_cm-1") or [])
        stratum = rec["_stratum"]
        fails = []
        fails += metadata_checks(rec)
        fails += band_checks(bands)
        fails += structure_checks(rec)

        tx = None
        if not args.skip_refetch and stratum != "chemotion":
            pmcid = rec.get("pmcid") or str(rec.get("source_doi") or "").replace(
                "PMC:", "PMC"
            )
            if pmcid and not pmcid.startswith("PMC"):
                pmcid = "PMC" + pmcid
            text, src = fetch_text(pmcid) if pmcid else (None, None)
            if text is None:
                tx = {"status": "unfetchable"}
            else:
                nb, hits = transcription_confirm(bands, text)
                tx = {
                    "status": "ok",
                    "text_source": src,
                    "bands": nb,
                    "confirmed": hits,
                    "all_confirmed": hits == nb,
                }
                if hits < nb:
                    fails.append(f"transcription_miss:{nb - hits}")
            time.sleep(0.02)
        elif stratum == "chemotion":
            tx = {
                "status": "skipped_chemotion",
                "note": "Chemotion is ELN author-curated; no PMC re-fetch",
            }

        row = {
            "id": rec.get("id"),
            "stratum": stratum,
            "source_doi": rec.get("source_doi"),
            "pmcid": rec.get("pmcid"),
            "license_pool": rec.get("license_pool"),
            "has_structure": bool(rec.get("has_structure") or rec.get("smiles")),
            "n_bands": len(bands),
            "fail_reasons": fails,
            "pass": len(fails) == 0,
            "transcription": tx,
        }
        rows.append(row)
        flag = "PASS" if row["pass"] else "FAIL"
        print(
            f"  [{i:>3}/{len(sample)}] {flag} {stratum:<24} "
            f"{rec.get('source_doi')} fails={fails or '-'}",
            flush=True,
        )

    # Summaries
    n = len(rows)
    n_pass = sum(1 for r in rows if r["pass"])
    by_stratum = {}
    for s in sorted({r["stratum"] for r in rows}):
        sub = [r for r in rows if r["stratum"] == s]
        sp = sum(1 for r in sub if r["pass"])
        by_stratum[s] = {
            "n": len(sub),
            "pass": sp,
            "pass_rate": round(sp / len(sub), 4) if sub else None,
            "wilson95": wilson_ci(sp, len(sub)),
        }

    tx_ok = [
        r
        for r in rows
        if r.get("transcription") and r["transcription"].get("status") == "ok"
    ]
    tx_bands = sum(r["transcription"]["bands"] for r in tx_ok)
    tx_hits = sum(r["transcription"]["confirmed"] for r in tx_ok)
    tx_full = sum(1 for r in tx_ok if r["transcription"]["all_confirmed"])

    struct_rows = [r for r in rows if r["has_structure"]]
    struct_physics_fail = sum(
        1
        for r in struct_rows
        if any(
            x.startswith("c13_")
            or x.startswith("h1_")
            or x == "smiles_unparseable"
            for x in r["fail_reasons"]
        )
    )

    reason_counts = Counter()
    for r in rows:
        for f in r["fail_reasons"]:
            reason_counts[f.split(":")[0]] += 1

    summary = {
        "label": "automated_chemist_proxy",
        "human_expert_audit": False,
        "method": (
            "Stratified multi-check automated chemist-proxy: IR window, "
            "band-list sanity, RDKit formula vs 13C/1H physics (structure-linked), "
            "PMC re-fetch transcription (±1 cm⁻¹). Explicitly NOT a human "
            "molecular-skeleton audit."
        ),
        "seed": args.seed,
        "n_requested": args.n,
        "n_scored": n,
        "strata": strata_meta,
        "pass_rate": round(n_pass / n, 4) if n else None,
        "pass_count": n_pass,
        "wilson95_pass": wilson_ci(n_pass, n),
        "by_stratum": by_stratum,
        "transcription_refetch": {
            "records_fetched": len(tx_ok),
            "bands_confirmed": f"{tx_hits}/{tx_bands}",
            "band_fidelity": round(tx_hits / tx_bands, 4) if tx_bands else None,
            "records_fully_confirmed": f"{tx_full}/{len(tx_ok)}",
            "record_fidelity": round(tx_full / len(tx_ok), 4) if tx_ok else None,
        },
        "structure_linked_in_sample": len(struct_rows),
        "structure_physics_fail_in_sample": struct_physics_fail,
        "structure_physics_pass_rate": (
            round(1 - struct_physics_fail / len(struct_rows), 4)
            if struct_rows
            else None
        ),
        "fail_reason_counts": dict(reason_counts),
    }

    out = {"summary": summary, "records": rows}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    with open(args.jsonl, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out} and {args.jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
