#!/usr/bin/env python3
"""Offline completeness and constraint-funnel diagnostics for the locked n=500 roster.

Does not call a model. Does not edit a locked benchmark file. Does not rescore
the headline. Gold SMILES are joined only after isomer counts are computed,
and only as the offline wall label plus a post-hoc rule audit.

Roster (same cut as data/benchmark_expand_500/HEADLINE_n500_2026-09-20.md on
commit 48fcd30153df5e331fab43cfa514763db8ee3891):

    locked score_main 194  +  all 106 of the first expansion  +  the first 200
    validate-clean expand-500 qids (R01 through R75 in the committed sort).

Locked generation outcome, not recomputed as a new headline:

    227 exact top-1
     22 in the k<=3 pool but not top-1
    251 never proposed at k<=3

The script aborts if a rescore of the deposited SMILES does not reproduce
those three integers and the published slice totals.
"""
from __future__ import annotations

import csv
import gzip
import json
import math
import multiprocessing
import os
import re
import select
import signal
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem import rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXPAND_SHA = "48fcd30153df5e331fab43cfa514763db8ee3891"
GOLD_PATH = ROOT / "data" / "irexp_resolved" / "irexp_resolved.jsonl.gz"
SURGE = os.environ.get("SURGE", "/tmp/surge/src/surge")
CAP = 50000
MODEL_ID = "surge-2.0 -R valences N3/N5 S2/S4/S6 Se2/Se4/Se6 P3/P5 Sn4 B3 Si4 cap50000"

# Locked integers. A mismatch aborts; these are not fitted.
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

SURGE_CHECKS = {
    "C4H10": 2,
    "C6H6": 217,
    "C2H6O": 2,
    "C8H10": 4678,
    "C10H16O": 452458,
    "C4H12Sn": 9,
}

ELEMENT_FLAGS = ["-ESe2", "-ESfSe4", "-ESgSe6", "-ESn4"]

# IR presence rules. Fixed before any gold comparison.
# Windows are closed intervals on the printed wavenumber list.
IR_RULES = [
    {
        "rule_id": "carbonyl_1650_1850",
        "window_cm_1": "[1650, 1850]",
        "lo": 1650.0,
        "hi": 1850.0,
        "trigger": "at least one printed band inside the window",
        "requires": "at least one carbon-oxygen double bond",
        "smarts": ["[#6]=[#8]"],
        "note": (
            "Ketone, aldehyde, ester, acid, amide, urea, carbamate, anhydride, "
            "acyl halide. Not nitro (N=O) and not sulfoxide (S=O). "
            "Absence of a band is not a constraint: printed lists omit peaks."
        ),
    },
    {
        "rule_id": "oh_nh_3200_3600",
        "window_cm_1": "[3200, 3600]",
        "lo": 3200.0,
        "hi": 3600.0,
        "trigger": "at least one printed band inside the window",
        "requires": "at least one hydrogen on oxygen or nitrogen",
        "smarts": ["[#8,#7;!H0]"],
        "note": (
            "Alcohol, phenol, carboxylic acid, amine, amide, oxime. "
            "A terminal alkyne C-H stretch also falls near 3300 and is not "
            "an O-H or N-H. The rule is applied as stated; the post-hoc gold "
            "audit measures how often that costs the true structure."
        ),
    },
    {
        "rule_id": "triple_or_cumulative_2100_2260",
        "window_cm_1": "[2100, 2260]",
        "lo": 2100.0,
        "hi": 2260.0,
        "trigger": "at least one printed band inside the window",
        "requires": "a nitrile, alkyne, isocyanate, isothiocyanate, or azide",
        "smarts": [
            "[#6]#[#6]",
            "[#6]#[#7]",
            "[#7]=[#6]=[#8]",
            "[#7]=[#6]=[#16]",
            "[#7-]=[#7+]=[#7]",
            "[#7]=[#7+]=[#7-]",
        ],
        "note": (
            "The 2100-2260 cm-1 window is the nitrile and alkyne stretch. "
            "The same window also contains isocyanates, isothiocyanates, and "
            "azides. Those substructures are accepted so the rule matches the "
            "window rather than only two of the groups that absorb there."
        ),
    },
]

SECTION_CUT = re.compile(r"\b(?:13C|HRMS|ESI-MS|ESI|MS|Anal)\b", re.I)
CHARGE_RE = re.compile(r"(?<=[A-Za-z0-9])(\d*[+-]|[+-]\d*)$")
ELEM_RE = re.compile(r"([A-Z][a-z]?)(\d*)")
INTEGRAL_RE = re.compile(r"(?<![\d.A-Za-z-])(\d+(?:\.\d+)?)\s*H\b")
SHIFT_RE = re.compile(r"(?<![\d.])(-?\d+\.?\d*)(?:\s*-\s*(-?\d+\.?\d*))?")
BARE_MULT_RE = re.compile(
    r"(?<!\()(\d+\.?\d*)\s+((?:br\s*)?(?:dd|dt|td|tt|s|d|t|q|m))\b"
)
SMARTS = {
    rule["rule_id"]: [Chem.MolFromSmarts(s) for s in rule["smarts"]]
    for rule in IR_RULES
}
for rid, pats in SMARTS.items():
    if any(p is None for p in pats):
        raise SystemExit(f"bad SMARTS in {rid}")


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{EXPAND_SHA}:{path}"], cwd=ROOT)


def read_jsonl_bytes(blob: bytes) -> list[dict]:
    return [json.loads(line) for line in blob.decode().splitlines() if line.strip()]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def qnum(qid: str) -> int:
    m = re.search(r"(\d+)", qid or "")
    return int(m.group(1)) if m else 0


def ik14(smiles: str | None) -> str | None:
    if not smiles or not isinstance(smiles, str):
        return None
    mol = Chem.MolFromSmiles(smiles.strip())
    if mol is None:
        return None
    return Chem.MolToInchiKey(mol)[:14]


def ir_key(bands) -> tuple:
    return tuple(round(float(x), 1) for x in (bands or []))


def q_c13(s: str) -> tuple:
    return tuple(round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", s or ""))


def g_c13(s: str) -> tuple:
    if "(" in (s or ""):
        return q_c13(s)
    return tuple(round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", s or ""))


def parse_formula(formula: str) -> tuple[dict[str, int], str]:
    text = (formula or "").strip()
    charge = ""
    m = CHARGE_RE.search(text)
    body = text
    if m:
        charge = m.group(1)
        body = text[: m.start()]
    counts: dict[str, int] = {}
    pieces = []
    for el, num in ELEM_RE.findall(body):
        n = int(num or "1")
        counts[el] = counts.get(el, 0) + n
        pieces.append(el + (num or ""))
    if "".join(pieces) != body:
        raise SystemExit(f"formula did not parse cleanly: {formula}")
    return counts, charge


def compositions(n: int, k: int):
    if k == 1:
        yield (n,)
        return
    for i in range(n + 1):
        yield from ((i,) + rest for rest in compositions(n - i, k - 1))


def compositions_low_first(n: int):
    """(n_valence2, n_valence4, n_valence6) with the lowest valence first."""
    comps = list(compositions(n, 3))
    comps.sort(key=lambda t: (t[2], t[1], -t[0]))
    return comps


def valence_variants(counts: dict[str, int]) -> list[str]:
    """Disjoint surge formulas covering the valence model. Lowest valence first."""
    nN = counts.get("N", 0)
    nS = counts.get("S", 0)
    nSe = counts.get("Se", 0)
    nP = counts.get("P", 0)
    fixed = []
    for el in ("C", "H", "O", "F", "Cl", "Br", "I", "Si", "B", "Sn"):
        n = counts.get(el, 0)
        if n:
            fixed.append((el, n))
    unknown = set(counts) - {"C", "H", "O", "F", "Cl", "Br", "I", "Si", "B", "Sn", "N", "S", "Se", "P"}
    if unknown:
        raise SystemExit(f"no valence model for {sorted(unknown)} in {counts}")
    out = []
    for n3 in range(nN, -1, -1):  # most trivalent nitrogen first
        n5 = nN - n3
        for s2, s4, s6 in compositions_low_first(nS):
            for e2, e4, e6 in compositions_low_first(nSe):
                for p3 in range(nP, -1, -1):
                    p5 = nP - p3
                    tokens = []
                    for el, n in fixed:
                        if el == "H":
                            continue
                        tokens.append(el + (str(n) if n > 1 else ""))
                    if n3:
                        tokens.append("N" + (str(n3) if n3 > 1 else ""))
                    if n5:
                        tokens.append("Nx" + (str(n5) if n5 > 1 else ""))
                    if s2:
                        tokens.append("S" + (str(s2) if s2 > 1 else ""))
                    if s4:
                        tokens.append("Sx" + (str(s4) if s4 > 1 else ""))
                    if s6:
                        tokens.append("Sy" + (str(s6) if s6 > 1 else ""))
                    if e2:
                        tokens.append("Se" + (str(e2) if e2 > 1 else ""))
                    if e4:
                        tokens.append("Sf" + (str(e4) if e4 > 1 else ""))
                    if e6:
                        tokens.append("Sg" + (str(e6) if e6 > 1 else ""))
                    if p3:
                        tokens.append("P" + (str(p3) if p3 > 1 else ""))
                    if p5:
                        tokens.append("Px" + (str(p5) if p5 > 1 else ""))
                    h = counts.get("H", 0)
                    if h:
                        tokens.append("H" + (str(h) if h > 1 else ""))
                    out.append("".join(tokens))
    return out


def heavy_atoms(counts: dict[str, int]) -> int:
    return sum(n for el, n in counts.items() if el != "H")


def budget_seconds(counts: dict[str, int]) -> int:
    nv = heavy_atoms(counts)
    # Small formulas often finish with an exact count, including counts well
    # above 50,000. Larger ones are given a short count attempt, then a stream
    # that stops at 50,000.
    if nv <= 12:
        return 40
    if nv <= 15:
        return 15
    if nv <= 20:
        return 8
    return 5


def surge_cmd(mode: str, formula: str) -> list[str]:
    # mode is "-u" or "-S"
    return ["stdbuf", "-o0", "-e0", SURGE, mode, "-R", *ELEMENT_FLAGS, formula]


def parse_z_count(stderr: str) -> int | None:
    matches = re.findall(r">Z (?:generated|wrote) (.+?) in ", stderr)
    if not matches:
        return None
    nums = re.findall(r"\d+", matches[-1])
    if not nums:
        return None
    return int(nums[-1])


def zero_reason(stderr: str) -> str | None:
    if "impossible parity" in stderr or "negative DBE" in stderr or "edge range is empty" in stderr:
        return "impossible_under_valence"
    return None


def run_surge_count(formula: str, timeout: int) -> dict:
    cmd = surge_cmd("-u", formula)
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        err = exc.stderr or ""
        if isinstance(err, bytes):
            err = err.decode("utf-8", "replace")
        return {"surge_formula": formula, "status": "timeout", "seconds": round(time.time() - t0, 3), "stderr_tail": err[-300:]}
    err = proc.stderr or ""
    seconds = round(time.time() - t0, 3)
    if proc.returncode != 0:
        reason = zero_reason(err)
        if reason:
            return {"surge_formula": formula, "status": "exact", "N": 0, "seconds": seconds, "reason": reason}
        return {
            "surge_formula": formula,
            "status": "error",
            "seconds": seconds,
            "returncode": proc.returncode,
            "stderr_tail": err[-400:],
        }
    n = parse_z_count(err)
    if n is None:
        return {"surge_formula": formula, "status": "error", "seconds": seconds, "stderr_tail": err[-400:]}
    return {"surge_formula": formula, "status": "exact", "N": n, "seconds": seconds}


def stream_surge(formula: str, cap: int, timeout: int) -> dict:
    """Read SMILES until cap lines, process exit, or timeout. Proves N>=cap when hit."""
    cmd = surge_cmd("-S", formula)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    assert proc.stdout is not None
    n = 0
    buf = b""
    end = time.time() + timeout
    finished = False
    try:
        while n < cap and time.time() < end:
            remaining = end - time.time()
            ready, _, _ = select.select([proc.stdout], [], [], max(0.0, remaining))
            if not ready:
                break
            chunk = os.read(proc.stdout.fileno(), 1 << 16)
            if not chunk:
                finished = True
                break
            buf += chunk
            while b"\n" in buf and n < cap:
                line, buf = buf.split(b"\n", 1)
                if line.strip():
                    n += 1
        if finished and n < cap and buf.strip():
            n += 1
    finally:
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
        else:
            proc.wait()
    if n >= cap:
        return {"surge_formula": formula, "status": "ge_cap", "lower_bound": cap}
    if finished:
        return {"surge_formula": formula, "status": "exact", "N": n}
    return {"surge_formula": formula, "status": "timeout", "lower_bound": n}


def count_formula(printed: str) -> dict:
    counts, charge = parse_formula(printed)
    record = {
        "formula": printed,
        "model_id": MODEL_ID,
        "charge": charge,
        "n_C": counts.get("C", 0),
        "n_H": counts.get("H", 0),
        "heavy_atoms": heavy_atoms(counts),
        "variants": [],
    }
    if charge:
        record["status"] = "unsupported_charge"
        record["N"] = None
        record["lower_bound"] = None
        return record
    variants = valence_variants(counts)
    record["n_variants_possible"] = len(variants)
    timeout = budget_seconds(counts)
    total = 0
    lower = 0
    status = "exact"
    for variant in variants:
        if status == "ge_50000":
            break
        counted = run_surge_count(variant, timeout)
        if counted["status"] == "exact":
            total += counted["N"]
            lower += counted["N"]
            record["variants"].append(counted)
            if total >= CAP:
                status = "ge_50000"
                break
            continue
        if counted["status"] == "error":
            record["variants"].append(counted)
            record["status"] = "error"
            record["N"] = None
            record["lower_bound"] = lower
            return record
        # Count mode timed out. Stream until the cap or a short extra budget.
        streamed = stream_surge(variant, CAP, timeout)
        streamed["count_mode"] = "timeout"
        if streamed["status"] == "ge_cap":
            lower += CAP
            record["variants"].append({**counted, **streamed, "status": "ge_50000"})
            status = "ge_50000"
            break
        if streamed["status"] == "exact":
            total += streamed["N"]
            lower += streamed["N"]
            record["variants"].append({**streamed, "seconds": counted.get("seconds")})
            if total >= CAP:
                status = "ge_50000"
                break
            continue
        lower += int(streamed.get("lower_bound") or 0)
        record["variants"].append({**counted, **streamed})
        record["status"] = "unavailable"
        record["N"] = None
        record["lower_bound"] = lower
        return record
    if status == "ge_50000":
        # An exact total exists only when every valence state was counted.
        # Stopping once the sum reaches 50,000 leaves later states uncounted.
        complete = len(record["variants"]) == len(variants) and all(
            v.get("status") == "exact" for v in record["variants"]
        )
        if complete:
            record["status"] = "exact"
            record["N"] = total
            record["lower_bound"] = total
        else:
            record["status"] = "ge_50000"
            record["N"] = None
            record["lower_bound"] = max(lower, CAP)
        return record
    record["status"] = "exact"
    record["N"] = total
    record["lower_bound"] = total
    return record


def _worker(printed: str) -> dict:
    try:
        return count_formula(printed)
    except Exception as exc:  # noqa: BLE001 — recorded per formula, not swallowed silently
        return {"formula": printed, "model_id": MODEL_ID, "status": "error", "N": None, "error": repr(exc), "variants": []}


def recover_seconds(nv: int) -> int:
    if nv <= 20:
        return 24
    if nv <= 28:
        return 14
    return 8


def recover_one(printed: str) -> dict:
    """Second pass for formulas that emitted nothing inside the first budget.

    Streams the lowest-valence state until 50,000 SMILES or the recovery
    budget. A hit proves N >= 50,000. A finished stream below the cap is
    handed back to the exact counter so the other valence states are summed.
    """
    counts, charge = parse_formula(printed)
    nv = heavy_atoms(counts)
    variants = valence_variants(counts)
    secs = recover_seconds(nv)
    streamed = stream_surge(variants[0], CAP, secs)
    if streamed["status"] == "exact":
        rec = count_formula(printed)
        rec["recovery_attempted"] = True
        rec["recovery_seconds"] = secs
        return rec
    record = {
        "formula": printed,
        "model_id": MODEL_ID,
        "charge": charge,
        "n_C": counts.get("C", 0),
        "n_H": counts.get("H", 0),
        "heavy_atoms": nv,
        "n_variants_possible": len(variants),
        "recovery_attempted": True,
        "recovery_seconds": secs,
        "variants": [{
            "surge_formula": variants[0],
            "status": "ge_50000" if streamed["status"] == "ge_cap" else "timeout",
            "lower_bound": CAP if streamed["status"] == "ge_cap" else int(streamed.get("lower_bound") or 0),
            "recovery": True,
        }],
    }
    if streamed["status"] == "ge_cap":
        record["status"] = "ge_50000"
        record["N"] = None
        record["lower_bound"] = CAP
    else:
        record["status"] = "unavailable"
        record["N"] = None
        record["lower_bound"] = int(streamed.get("lower_bound") or 0)
    return record


def _worker_recover(printed: str) -> dict:
    try:
        return recover_one(printed)
    except Exception as exc:  # noqa: BLE001
        return {
            "formula": printed,
            "model_id": MODEL_ID,
            "status": "error",
            "N": None,
            "error": repr(exc),
            "variants": [],
            "recovery_attempted": True,
        }


def normalize_nmr(text: str) -> str:
    s = text or ""
    s = s.replace("Н", "H").replace("н", "H").replace("С", "C").replace("с", "C")
    for src, dst in (("\u2010", "-"), ("\u2011", "-"), ("\u2012", "-"), ("\u2013", "-"), ("\u2014", "-"), ("\u2212", "-"), ("\u00a0", " "), ("\u2009", " ")):
        s = s.replace(src, dst)
    return s


def cut_section(text: str) -> tuple[str, str]:
    m = SECTION_CUT.search(text)
    if not m:
        return text, ""
    return text[: m.start()], m.group(0)


def split_top(text: str) -> list[str]:
    out, depth, cur = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch in ",;" and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur).strip())
    return [tok for tok in out if tok]


def outside(text: str) -> str:
    chars = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
            chars.append(" ")
        elif ch == ")":
            depth = max(0, depth - 1)
            chars.append(" ")
        else:
            chars.append(ch if depth == 0 else " ")
    return "".join(chars)


def shift_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in SHIFT_RE.finditer(outside(text)) if m.group(0).strip()]


def integrals_in(text: str) -> list[float]:
    vals = []
    for m in INTEGRAL_RE.finditer(text):
        vals.append(float(m.group(1)))
    return vals


def repair_missing_paren(text: str) -> tuple[str, int]:
    repairs = 0
    while text.count(")") > text.count("(") and repairs < 3:
        m = BARE_MULT_RE.search(text)
        if not m:
            break
        text = text[: m.start(2)] + "(" + text[m.start(2) :]
        repairs += 1
    return text, repairs


def parse_1h(raw: str) -> dict:
    text = normalize_nmr(raw)
    text, cut = cut_section(text)
    text = re.sub(r"\s*ppm\s*$", "", text.strip())
    text, repairs = repair_missing_paren(text)
    balanced = text.count("(") == text.count(")")
    envs = []
    pending = None
    for tok in split_top(text):
        spans = shift_spans(tok) if balanced else []
        if balanced and not spans:
            ints = integrals_in(tok)
            if pending is not None and ints and "(" in tok:
                pending["integrals"].extend(ints)
                pending["text"] += " " + tok
            continue
        if not balanced:
            continue
        if len(spans) == 1:
            pending = {"text": tok, "integrals": integrals_in(tok)}
            envs.append(pending)
            continue
        pending = None
        for i, (a, b) in enumerate(spans):
            end = spans[i + 1][0] if i + 1 < len(spans) else len(tok)
            piece = tok[a:end]
            env = {"text": piece, "integrals": integrals_in(piece)}
            envs.append(env)
            pending = env
    if not balanced:
        # Paren depth is not usable. Count shifts that introduce a signal,
        # which in this roster sit immediately before an opening parenthesis.
        # Integrals are not treated as a complete parse.
        stripped = re.sub(r"J\s*=\s*[\d.,\s]*Hz", " ", text, flags=re.I)
        n_env = len(re.findall(
            r"(?<![\d.A-Za-z])-?\d+\.?\d*(?:\s*-\s*-?\d+\.?\d*)?(?=\s*\()",
            stripped,
        ))
        return {
            "n_env": n_env,
            "integral_sum": None,
            "integral_status": "unbalanced",
            "n_with_integral": 0,
            "n_missing_integral": n_env,
            "integrals": [],
            "section_cut": cut,
            "paren_repairs": repairs,
            "balanced": False,
        }
    integrals = []
    missing = 0
    ambiguous = False
    fractional = False
    for env in envs:
        vals = env["integrals"]
        if len(vals) == 1:
            integrals.append(vals[0])
            if abs(vals[0] - round(vals[0])) > 1e-9:
                fractional = True
        elif len(vals) == 0:
            missing += 1
        else:
            ambiguous = True
            missing += 1
    if not envs:
        status = "unparsed"
        total = None
    elif ambiguous:
        status = "ambiguous"
        total = None
    elif missing:
        status = "partial"
        total = None
    elif fractional:
        status = "complete_fractional"
        total = sum(integrals)
    else:
        status = "complete"
        total = int(sum(integrals))
    return {
        "n_env": len(envs),
        "integral_sum": total,
        "integral_status": status,
        "n_with_integral": len(integrals),
        "n_missing_integral": missing,
        "integrals": [int(v) if abs(v - round(v)) < 1e-9 else v for v in integrals] if status in {"complete", "complete_fractional"} else [],
        "section_cut": cut,
        "paren_repairs": repairs,
        "balanced": True,
    }


def parse_13c(raw: str) -> dict:
    text = normalize_nmr(raw)
    text, cut = cut_section(text)
    n = 0
    annot = []
    bare = 0
    for tok in split_top(text):
        spans = shift_spans(tok)
        if not spans:
            continue
        n += len(spans)
        found = [int(x) for x in re.findall(r"(\d+)\s*C\b", tok)]
        if found:
            annot.extend(found)
        else:
            bare += 1
    return {
        "n_13C": n,
        "n_annot": len(annot),
        "annot_sum": sum(annot) if annot else None,
        "annot_all_one": bool(annot) and all(v == 1 for v in annot) and bare == 0 and len(annot) == n,
        "section_cut": cut,
    }


def self_check_parser() -> None:
    a = parse_1h("8.26 (d, J = 2.4 Hz, 1H), 7.36 (d, J = 2.4 Hz, 1H), 6.27 (s, 2H), 3.86 (s, 3H)")
    assert (a["n_env"], a["integral_sum"], a["integral_status"]) == (4, 7, "complete"), a
    b = parse_1h("7.08-7.10 (d, J = 8 Hz, 2H), 7.32-7.34 (d, J = 8 Hz, 2H)")
    assert (b["n_env"], b["integral_sum"]) == (2, 4), b
    c = parse_1h("5.23 (d, 1H, J = 7.0 Hz); 13C{1H} NMR (150 MHz, CDCl3) δ 156.2 (d)")
    assert (c["n_env"], c["integral_sum"], c["section_cut"]) == (1, 1, "13C"), c
    d = parse_1h("6.86, (s, 2H), 5.27 (s, 2H)")
    assert (d["n_env"], d["integral_sum"]) == (2, 4), d
    e = parse_1h("7.77 (d, J = 8.1 Hz, 2H, Ar(4-CH3)-2,6-2H)")
    assert (e["n_env"], e["integral_sum"]) == (1, 2), e
    f = parse_1h("3.17 (4H; t; CH2N), 11.52 (1H; s; -NH-N)")
    assert (f["n_env"], f["integral_sum"]) == (2, 5), f
    g = parse_1h("1.25-1.38 (m, 5H) 0.87 (t, J = 7.6 Hz, 6H)")
    assert (g["n_env"], g["integral_sum"]) == (2, 11), g
    h = parse_1h("11.54 (s, 0.5H), 11.33 (s, 0.5H)")
    assert h["n_env"] == 2 and h["integral_status"] == "complete_fractional" and abs(h["integral_sum"] - 1.0) < 1e-9, h
    r127 = parse_1h(
        "2.00 (s, 6H, 2CH3), 2.70-2.94 (m, 2H, COCH2), 3.43-3.52 (m, 1H, CH), "
        "3.96-4.20 (m, 2H, NCH2), 5.65 (s, 2H, 2CH), 6.96 (s, 1H, CH=C), "
        "7.05 (s, 2H, NH2), 7.68 (d, J = 8.8 Hz, 2H, HAr), 7.80 d, J = 8.8 Hz, 2H, HAr), "
        "10.91 (s, 1H, NH) ppm"
    )
    assert (r127["n_env"], r127["integral_sum"], r127["paren_repairs"]) == (10, 21, 1), r127
    r224 = parse_1h(
        "8.80 (s, 1H, triazole CH), 7.87 (d, J = 8.4 Hz, 2H, Ar-H-3), "
        "7.68-7.57 (m, 4H, Ar-H), 7.45 (d, J = 7.3 Hz, 2H, Ar-H), "
        "7.40-7.14 (m, 5H, Ar-H), 5.49 (s, 2H, N-CH2(, 4.62 (s, 2H, S-CH2)"
    )
    assert r224["n_env"] == 7 and r224["integral_status"] == "unbalanced", r224
    c13 = parse_13c("δ 160.2 (1C, s), 142.2 (1C, s), 55.5 (1C, s)")
    assert c13["n_13C"] == 3 and c13["annot_all_one"], c13
    # Carbon and hydrogen filters on ethanol: classes 3,2,1.
    ethanol = Chem.MolFromSmiles("CCO")
    assert sorted(h_classes(ethanol)) == [1, 2, 3]
    assert pack_integrals([3, 2, 1], [3, 2, 1]) is True
    assert pack_integrals([6], [3, 3]) is False
    assert pack_integrals([3, 2, 1], [3, 2]) is True
    assert n_unique_carbons(ethanol) == 2


def triggered_rules(bands: list[float]) -> list[str]:
    hit = []
    for rule in IR_RULES:
        if any(rule["lo"] <= float(b) <= rule["hi"] for b in bands):
            hit.append(rule["rule_id"])
    return hit


def mol_matches(mol, rule_id: str) -> bool:
    return any(mol.HasSubstructMatch(pat) for pat in SMARTS[rule_id])


def n_unique_carbons(mol) -> int:
    m = Chem.Mol(mol)
    Chem.RemoveStereochemistry(m)
    ranks = list(Chem.CanonicalRankAtoms(m, breakTies=False))
    return len({ranks[a.GetIdx()] for a in m.GetAtoms() if a.GetSymbol() == "C"})


def h_classes(mol) -> list[int]:
    m = Chem.Mol(mol)
    Chem.RemoveStereochemistry(m)
    ranks = list(Chem.CanonicalRankAtoms(m, breakTies=False))
    grouped: dict[tuple, list[int]] = defaultdict(list)
    for atom in m.GetAtoms():
        h = atom.GetTotalNumHs()
        if h <= 0:
            continue
        grouped[ranks[atom.GetIdx()]].append(h)
    classes = []
    for hs in grouped.values():
        classes.append(len(hs) * hs[0])
    return classes


def pack_integrals(classes: list[int], integrals: list[int], node_cap: int = 200000):
    """True if each integral is a sum of whole constitutional H classes.

    Unused classes are allowed when the integrals sum to less than the
    formula hydrogen count. A class is never split, so diastereotopic CH2
    groups are not modelled. Returns None if the search exceeds node_cap.
    """
    classes = [c for c in classes if c > 0]
    integrals = [int(v) for v in integrals]
    if any(v <= 0 for v in integrals):
        return False
    if sum(classes) < sum(integrals):
        return False
    bins = sorted(integrals, reverse=True)
    leftover = sum(classes) - sum(integrals)
    if leftover:
        bins.append(leftover)
    bins = sorted(bins, reverse=True)
    classes = sorted(classes, reverse=True)
    nodes = 0

    def rec(i: int) -> bool | None:
        nonlocal nodes
        nodes += 1
        if nodes > node_cap:
            return None
        if i == len(classes):
            return all(b == 0 for b in bins)
        c = classes[i]
        seen = set()
        for j in range(len(bins)):
            if bins[j] < c or bins[j] in seen:
                continue
            seen.add(bins[j])
            bins[j] -= c
            ans = rec(i + 1)
            bins[j] += c
            if ans is None or ans:
                return ans
        return False

    return rec(0)


def index_gold(formulas: set[str]) -> dict:
    wanted = set(formulas)
    by = defaultdict(list)
    with gzip.open(GOLD_PATH, "rt") as fh:
        for line in fh:
            row = json.loads(line)
            smi = row.get("smiles")
            if not smi:
                continue
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                continue
            form = rdMolDescriptors.CalcMolFormula(mol)
            if form not in wanted:
                continue
            by[(form, ir_key(row.get("ir_bands_cm-1")), g_c13(row.get("c_nmr")))].append(
                {
                    "smiles": Chem.MolToSmiles(mol),
                    "ik": (row.get("inchikey") or Chem.MolToInchiKey(mol))[:14],
                }
            )
    return by


def match_gold(q: dict, gold: dict) -> dict:
    key = (q["formula"], ir_key(q.get("ir_bands_cm-1")), q_c13(q.get("c_nmr")))
    hits = gold.get(key, [])
    if len(hits) != 1:
        raise SystemExit(f"{q.get('qid')} {q.get('formula')}: expected 1 gold hit, got {len(hits)}")
    return hits[0]


def load_roster() -> list[dict]:
    formulas = set()
    for directory in ("benchmark_main", "benchmark_v3", "benchmark_v2_ctrl"):
        for row in read_jsonl(ROOT / "data" / directory / "questions2.jsonl"):
            formulas.add(row["formula"])
    expand_q = read_jsonl_bytes(git_show("data/benchmark_expand/questions2.jsonl"))
    expand500_q = read_jsonl_bytes(git_show("data/benchmark_expand_500/questions2.jsonl"))
    for row in expand_q + expand500_q:
        formulas.add(row["formula"])
    gold = index_gold(formulas)

    items = []
    answers = {r["qid"]: r for r in read_jsonl(ROOT / "data/benchmark_main/answers2.jsonl")}
    questions = {r["qid"]: r for r in read_jsonl(ROOT / "data/benchmark_main/questions2.jsonl")}
    clean = set(json.loads((ROOT / "data/benchmark_main/clean_qids.json").read_text()))
    pred = {}
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
        q = dict(questions[qid])
        q["difficulty"] = ans.get("difficulty") or q.get("difficulty")
        hit = match_gold(q, gold)
        if hit["ik"] != ans["inchikey"][:14]:
            raise SystemExit(f"main {qid}: join InChIKey != committed answer key")
        items.append(item_from(q, hit, "locked-main", "locked194", cands))

    for cohort, directory in (("locked-v3", "benchmark_v3"), ("locked-v2ctrl", "benchmark_v2_ctrl")):
        base = ROOT / "data" / directory
        aa = {r["qid"]: r for r in read_jsonl(base / "answers2.jsonl")}
        qq = {r["qid"]: r for r in read_jsonl(base / "questions2.jsonl")}
        pp = {r["qid"]: r for r in read_jsonl(base / "predictions2.jsonl")}
        for qid, ans in aa.items():
            q = dict(qq[qid])
            q["difficulty"] = ans.get("difficulty") or q.get("difficulty")
            hit = match_gold(q, gold)
            if hit["ik"] != ans["inchikey"][:14]:
                raise SystemExit(f"{directory} {qid}: join InChIKey != committed answer key")
            items.append(item_from(q, hit, cohort, "locked194", pp[qid].get("candidates", [])))

    expand_p = {r["qid"]: r.get("candidates", []) for r in read_jsonl_bytes(git_show("data/benchmark_expand/predictions2.jsonl"))}
    for q in expand_q:
        if q["qid"] not in expand_p:
            raise SystemExit(f"expand {q['qid']}: no deposited candidates")
        hit = match_gold(q, gold)
        items.append(item_from(q, hit, "expand", "plus106", expand_p[q["qid"]]))

    cut = set(json.loads(git_show("data/benchmark_expand_500/headline500_expand200_qids.json")))
    expand500_p = {r["qid"]: r.get("candidates", []) for r in read_jsonl_bytes(git_show("data/benchmark_expand_500/predictions2.jsonl"))}
    for q in expand500_q:
        if q["qid"] not in cut:
            continue
        if q["qid"] not in expand500_p:
            raise SystemExit(f"expand500 {q['qid']}: no deposited candidates")
        hit = match_gold(q, gold)
        items.append(item_from(q, hit, "expand500", "expand200", expand500_p[q["qid"]]))
    if len(items) != 500:
        raise SystemExit(f"roster length {len(items)}")
    return items


def item_from(q: dict, hit: dict, cohort: str, arm: str, cands) -> dict:
    bands = [float(x) for x in (q.get("ir_bands_cm-1") or [])]
    counts, charge = parse_formula(q["formula"])
    h = parse_1h(q.get("h_nmr") or "")
    c = parse_13c(q.get("c_nmr") or "")
    ranked = []
    for cand in list(cands or [])[:3]:
        if isinstance(cand, dict):
            cand = cand.get("smiles") or cand.get("candidate")
        ranked.append(cand if isinstance(cand, str) else None)
    gold_ik = hit["ik"]
    pred_ik = [ik14(s) for s in ranked]
    top1 = bool(pred_ik) and pred_ik[0] is not None and pred_ik[0] == gold_ik
    recalled = gold_ik is not None and any(p == gold_ik for p in pred_ik)
    if top1:
        wall = "top1"
    elif recalled:
        wall = "in_pool"
    else:
        wall = "never"
    return {
        "uid": f"{cohort}:{q['qid']}",
        "cohort": cohort,
        "qid": q["qid"],
        "arm": arm,
        "difficulty": q.get("difficulty") or "",
        "formula": q["formula"],
        "charge": charge,
        "n_C": counts.get("C", 0),
        "n_H": counts.get("H", 0),
        "heavy_atoms": heavy_atoms(counts),
        "n_13C": c["n_13C"],
        "c13_annot_all_one": c["annot_all_one"],
        "n_ir": len(bands),
        "n_1H_env": h["n_env"],
        "h_integral_sum": h["integral_sum"],
        "h_integral_status": h["integral_status"],
        "h_integrals": h["integrals"],
        "h_section_cut": h["section_cut"],
        "h_paren_repairs": h["paren_repairs"],
        "ir_bands": bands,
        "ir_rules": triggered_rules(bands),
        "wall_class": wall,
        "top1": top1,
        "recalled": recalled,
        # Retained for the post-hoc audit only. Not read by the counter.
        "gold_smiles": hit["smiles"],
        "gold_ik": gold_ik,
    }


def assert_lock(items: list[dict]) -> None:
    def take(name):
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
            got = sum(it["top1"] for it in rows)
        elif metric == "recall":
            got = sum(it["recalled"] for it in rows)
        elif metric == "in_pool":
            got = sum(it["wall_class"] == "in_pool" for it in rows)
        elif metric == "never":
            got = sum(it["wall_class"] == "never" for it in rows)
        else:
            raise SystemExit(metric)
        if got != num:
            raise SystemExit(f"lock failed {group} {metric}: got {got}, locked {num}/{den}")


def self_check_surge() -> None:
    if not Path(SURGE).exists():
        raise SystemExit(f"surge binary not found at {SURGE}")
    for formula, expected in SURGE_CHECKS.items():
        rec = run_surge_count(formula, 30)
        if rec.get("status") != "exact" or rec.get("N") != expected:
            raise SystemExit(f"surge self-check {formula}: expected {expected}, got {rec}")
    # Higher selenium valence is wired.
    rec = run_surge_count("C2H6Sf", 10)
    if rec.get("status") != "exact" or not rec.get("N"):
        raise SystemExit(f"surge Se(IV) self-check failed: {rec}")


def load_count_cache() -> dict[str, dict]:
    path = OUT / "formula_counts.jsonl"
    got = {}
    if not path.exists():
        return got
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("model_id") == MODEL_ID and rec.get("formula"):
            got[rec["formula"]] = rec
    return got


def append_count(rec: dict) -> None:
    path = OUT / "formula_counts.jsonl"
    with path.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def enumerate_formulas(formulas: list[str]) -> dict[str, dict]:
    cache = load_count_cache()
    if os.environ.get("RECOVER") == "1":
        retry = [f for f in formulas if cache.get(f, {}).get("status") == "unavailable" and not cache.get(f, {}).get("recovery_attempted")]
        print(f"recovery pass {len(retry)}", flush=True)
        if retry:
            ctx = multiprocessing.get_context("spawn")
            with ctx.Pool(processes=3) as pool:
                for i, rec in enumerate(pool.imap_unordered(_worker_recover, retry), 1):
                    cache[rec["formula"]] = rec
                    append_count(rec)
                    if i % 10 == 0 or i == len(retry):
                        print(f"  recovered {i}/{len(retry)} last={rec['formula']} status={rec['status']} N={rec.get('N')} lb={rec.get('lower_bound')}", flush=True)
    pending = [f for f in formulas if f not in cache]
    print(f"formulas {len(formulas)} cached {len(formulas) - len(pending)} pending {len(pending)}", flush=True)
    if pending:
        ctx = multiprocessing.get_context("spawn")
        with ctx.Pool(processes=3) as pool:
            for i, rec in enumerate(pool.imap_unordered(_worker, pending), 1):
                cache[rec["formula"]] = rec
                append_count(rec)
                if i % 10 == 0 or i == len(pending):
                    print(f"  counted {i}/{len(pending)} last={rec['formula']} status={rec['status']} N={rec.get('N')}", flush=True)
    return {f: cache[f] for f in formulas}


def generate_mols(record: dict) -> dict:
    """Parse every SMILES for an exact formula under the cap. No gold input."""
    mols = []
    unparsed = 0
    lines = 0
    seen = set()
    for variant in record["variants"]:
        if variant.get("status") != "exact":
            return {"error": "variant_not_exact", "mols": [], "unparsed": 0, "lines": 0}
        proc = subprocess.run(surge_cmd("-S", variant["surge_formula"]), capture_output=True, text=True, timeout=120)
        if proc.returncode != 0 and not zero_reason(proc.stderr or ""):
            return {"error": (proc.stderr or "")[-300:], "mols": [], "unparsed": 0, "lines": lines}
        for line in proc.stdout.splitlines():
            smi = line.strip()
            if not smi:
                continue
            lines += 1
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                unparsed += 1
                continue
            key = Chem.MolToInchiKey(mol)[:14]
            if key in seen:
                continue
            seen.add(key)
            mols.append(mol)
    return {"mols": mols, "unparsed": unparsed, "lines": lines, "error": ""}


def apply_filters(items: list[dict], counts: dict[str, dict]) -> None:
    by_formula = defaultdict(list)
    for it in items:
        by_formula[it["formula"]].append(it)
    for formula, group in by_formula.items():
        rec = counts[formula]
        for it in group:
            it["N_formula_status"] = rec["status"]
            it["N_formula"] = rec.get("N")
            it["N_formula_lower_bound"] = rec.get("lower_bound")
            it["N_after_ir"] = None
            it["N_after_ir_carbon"] = None
            it["N_after_filters"] = None
            it["filter_status"] = "not_applied"
            it["n_parsed"] = None
            it["n_unparsed"] = None
            it["n_h_undecided"] = None
            it["h_filter_applied"] = False
        if rec.get("status") != "exact" or rec.get("N") is None or rec["N"] >= CAP or rec["N"] == 0:
            if rec.get("status") == "exact" and rec.get("N") == 0:
                for it in group:
                    it["N_after_filters"] = 0
                    it["N_after_ir"] = 0
                    it["N_after_ir_carbon"] = 0
                    it["filter_status"] = "empty_formula"
            continue
        generated = generate_mols(rec)
        if generated.get("error"):
            for it in group:
                it["filter_status"] = "generate_error"
                it["filter_error"] = generated["error"]
            continue
        mols = generated["mols"]
        for it in group:
            it["n_parsed"] = len(mols)
            it["n_unparsed"] = generated["unparsed"]
            it["n_smiles_lines"] = generated["lines"]
            rules = it["ir_rules"]
            h_ok = it["h_integral_status"] == "complete" and it["h_integral_sum"] is not None and it["h_integral_sum"] <= it["n_H"]
            n_ir = n_c = n_pass = n_und = 0
            for mol in mols:
                if rules and not all(mol_matches(mol, rid) for rid in rules):
                    continue
                n_ir += 1
                if n_unique_carbons(mol) < it["n_13C"]:
                    continue
                n_c += 1
                if h_ok:
                    verdict = pack_integrals(h_classes(mol), it["h_integrals"])
                    if verdict is None:
                        n_und += 1
                        continue
                    if not verdict:
                        continue
                n_pass += 1
            it["N_after_ir"] = n_ir
            it["N_after_ir_carbon"] = n_c
            it["h_filter_applied"] = h_ok
            it["n_h_undecided"] = n_und
            if n_und:
                it["filter_status"] = "h_filter_undecided"
                it["N_after_filters"] = None
                it["N_pass_lower"] = n_pass
                it["N_pass_upper"] = n_pass + n_und
            else:
                it["filter_status"] = "applied"
                it["N_after_filters"] = n_pass
            if generated["unparsed"]:
                it["filter_status"] = it["filter_status"] + "+unparsed"


def gold_audit(items: list[dict]) -> None:
    """Offline only. Does not change N."""
    for it in items:
        mol = Chem.MolFromSmiles(it["gold_smiles"])
        it["posthoc_gold_parsed"] = mol is not None
        if mol is None:
            it["posthoc_ir_pass"] = None
            it["posthoc_carbon_pass"] = None
            it["posthoc_h_pass"] = None
            continue
        it["posthoc_ir_pass"] = all(mol_matches(mol, rid) for rid in it["ir_rules"]) if it["ir_rules"] else True
        it["posthoc_carbon_pass"] = n_unique_carbons(mol) >= it["n_13C"]
        if it["h_integral_status"] == "complete" and it["h_integral_sum"] is not None and it["h_integral_sum"] <= it["n_H"]:
            verdict = pack_integrals(h_classes(mol), it["h_integrals"])
            it["posthoc_h_pass"] = None if verdict is None else bool(verdict)
        else:
            it["posthoc_h_pass"] = None
        it["posthoc_unique_C"] = n_unique_carbons(mol)


def log10_or_blank(n):
    if n is None or n <= 0:
        return ""
    return f"{math.log10(n):.6f}"


def chance(k: int, n):
    if n is None or n <= 0:
        return "", ""
    return f"{k}/{n}", f"{k / n:.8e}"


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def median(vals: list[float]):
    if not vals:
        return None
    return float(statistics.median(vals))


def quartiles(vals: list[float]) -> dict:
    if not vals:
        return {"n": 0, "median": None, "q1": None, "q3": None, "min": None, "max": None}
    ordered = sorted(vals)
    if len(ordered) >= 2:
        qs = statistics.quantiles(ordered, n=4, method="inclusive")
        q1, q3 = qs[0], qs[2]
    else:
        q1 = q3 = ordered[0]
    return {
        "n": len(ordered),
        "median": ordered[len(ordered) // 2] if len(ordered) % 2 else statistics.median(ordered),
        "q1": q1,
        "q3": q3,
        "min": ordered[0],
        "max": ordered[-1],
    }


def ratio_bin(n13: int, nC: int) -> str:
    if nC <= 0:
        return "undefined"
    if n13 > nC:
        return "n_13C > n_C"
    if n13 == nC:
        return "n_13C = n_C"
    r = n13 / nC
    if r >= 0.8:
        return "0.80-0.99"
    if r >= 0.6:
        return "0.60-0.79"
    if r >= 0.4:
        return "0.40-0.59"
    return "<0.40"


BIN_ORDER = ["n_13C > n_C", "n_13C = n_C", "0.80-0.99", "0.60-0.79", "0.40-0.59", "<0.40"]
WALL_ORDER = ["top1", "in_pool", "never"]
WALL_LABEL = {
    "top1": "exact top-1",
    "in_pool": "in pool, not top-1",
    "never": "never proposed at k<=3",
}


def completeness_table(items: list[dict]) -> list[dict]:
    rows = []
    groups = [("all", items)]
    for diff in ("simple", "complex"):
        groups.append((diff, [it for it in items if it["difficulty"] == diff]))
    for wall in WALL_ORDER:
        groups.append((wall, [it for it in items if it["wall_class"] == wall]))
    for diff in ("simple", "complex"):
        for wall in WALL_ORDER:
            groups.append((f"{diff}|{wall}", [it for it in items if it["difficulty"] == diff and it["wall_class"] == wall]))
    for name, rows_in in groups:
        n = len(rows_in)
        if n == 0:
            continue
        ratios = [it["n_13C"] / it["n_C"] for it in rows_in if it["n_C"]]
        complete = [it for it in rows_in if it["h_integral_status"] in {"complete", "complete_fractional"}]
        complete_int = [it for it in rows_in if it["h_integral_status"] == "complete"]
        rows.append({
            "group": name,
            "n": n,
            "n_13C_eq_n_C": sum(it["n_13C"] == it["n_C"] for it in rows_in),
            "n_13C_lt_n_C": sum(it["n_13C"] < it["n_C"] for it in rows_in),
            "n_13C_gt_n_C": sum(it["n_13C"] > it["n_C"] for it in rows_in),
            "median_n_C": median([it["n_C"] for it in rows_in]),
            "median_n_H": median([it["n_H"] for it in rows_in]),
            "median_n_13C": median([it["n_13C"] for it in rows_in]),
            "median_n_ir": median([it["n_ir"] for it in rows_in]),
            "median_n_1H_env": median([it["n_1H_env"] for it in rows_in]),
            "median_n_13C_over_n_C": median(ratios),
            "min_n_13C_over_n_C": min(ratios) if ratios else None,
            "max_n_13C_over_n_C": max(ratios) if ratios else None,
            "h_integral_complete": len(complete),
            "h_integral_complete_integer": len(complete_int),
            "h_sum_eq_n_H": sum(it["h_integral_sum"] == it["n_H"] for it in complete),
            "h_sum_lt_n_H": sum(it["h_integral_sum"] < it["n_H"] for it in complete),
            "h_sum_gt_n_H": sum(it["h_integral_sum"] > it["n_H"] for it in complete),
            "section_cut": sum(bool(it["h_section_cut"]) for it in rows_in),
            "carbonyl_rule": sum("carbonyl_1650_1850" in it["ir_rules"] for it in rows_in),
            "oh_nh_rule": sum("oh_nh_3200_3600" in it["ir_rules"] for it in rows_in),
            "triple_rule": sum("triple_or_cumulative_2100_2260" in it["ir_rules"] for it in rows_in),
            "top1": sum(it["top1"] for it in rows_in),
            "recalled": sum(it["recalled"] for it in rows_in),
        })
    return rows


def figure_bins(items: list[dict]) -> list[dict]:
    rows = []
    for name in BIN_ORDER:
        group = [it for it in items if ratio_bin(it["n_13C"], it["n_C"]) == name]
        n = len(group)
        top1 = sum(it["top1"] for it in group)
        recalled = sum(it["recalled"] for it in group)
        rows.append({
            "bin": name,
            "n": n,
            "top1": top1,
            "recall_k3": recalled,
            "in_pool_not_top1": sum(it["wall_class"] == "in_pool" for it in group),
            "never": sum(it["wall_class"] == "never" for it in group),
            "simple": sum(it["difficulty"] == "simple" for it in group),
            "complex": sum(it["difficulty"] == "complex" for it in group),
        })
    if sum(r["top1"] for r in rows) != 227 or sum(r["recall_k3"] for r in rows) != 249 or sum(r["n"] for r in rows) != 500:
        raise SystemExit(f"figure bins do not add to the lock: {rows}")
    return rows


def formula_category(rec: dict) -> str:
    if rec["status"] == "exact" and rec.get("N") is not None:
        n = rec["N"]
        if n < 1000:
            return "exact_<1000"
        if n < 10000:
            return "exact_1000_9999"
        if n < CAP:
            return "exact_10000_49999"
        return "exact_ge_50000"
    if rec["status"] == "ge_50000":
        return "censored_ge_50000"
    if rec["status"] == "unsupported_charge":
        return "unsupported_charge"
    return "unavailable"


def n_category_table(items: list[dict], counts: dict[str, dict]) -> list[dict]:
    cats = ["exact_<1000", "exact_1000_9999", "exact_10000_49999", "exact_ge_50000", "censored_ge_50000", "unsupported_charge", "unavailable"]
    rows = []
    for wall in ["all", *WALL_ORDER]:
        group = items if wall == "all" else [it for it in items if it["wall_class"] == wall]
        tally = Counter(formula_category(counts[it["formula"]]) for it in group)
        row = {"group": wall, "n": len(group)}
        for cat in cats:
            row[cat] = tally.get(cat, 0)
        rows.append(row)
    return rows


def log_summary(items: list[dict], key: str) -> dict:
    out = {}
    for wall in ["all", *WALL_ORDER]:
        group = items if wall == "all" else [it for it in items if it["wall_class"] == wall]
        vals = []
        for it in group:
            n = it.get(key)
            if isinstance(n, int) and n > 0:
                vals.append(math.log10(n))
        out[wall] = quartiles(vals)
    return out


def write_figure(items: list[dict], bins: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4))
    ax = axes[0]
    data = [[it["n_13C"] / it["n_C"] for it in items if it["wall_class"] == wall] for wall in WALL_ORDER]
    bp = ax.boxplot(data, tick_labels=["top-1\n227", "in pool\n22", "never\n251"], showfliers=True, patch_artist=True)
    colors = ["#0072B2", "#E69F00", "#009E73"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.axhline(1.0, color="#444444", lw=0.6, ls="--")
    ax.set_ylabel("printed 13C signals / formula carbons")
    ax.set_title("n_13C / n_C by locked wall class")

    ax = axes[1]
    xs = list(range(len(bins)))
    top_rate = [100 * r["top1"] / r["n"] if r["n"] else 0 for r in bins]
    rec_rate = [100 * r["recall_k3"] / r["n"] if r["n"] else 0 for r in bins]
    width = 0.38
    ax.bar([x - width / 2 for x in xs], top_rate, width, label="top-1", color="#0072B2")
    ax.bar([x + width / 2 for x in xs], rec_rate, width, label="recall at k≤3", color="#56B4E9")
    ax.axhline(100 * 227 / 500, color="#0072B2", lw=0.7, ls="--")
    ax.axhline(100 * 249 / 500, color="#56B4E9", lw=0.7, ls="--")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{r['bin']}\nn={r['n']}" for r in bins], fontsize=7)
    ax.set_ylabel("percent of the bin")
    ax.set_ylim(0, 100)
    ax.set_title("Locked outcome by 13C completeness")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_completeness_vs_outcome.png", dpi=160)
    fig.savefig(OUT / "fig_completeness_vs_outcome.pdf")
    plt.close(fig)


def fmt_q(q: dict) -> str:
    if not q or not q.get("n"):
        return "n=0"
    def f(x):
        return "NA" if x is None else f"{x:.3f}"
    return f"n={q['n']}, median {f(q['median'])}, IQR {f(q['q1'])} to {f(q['q3'])}, range {f(q['min'])} to {f(q['max'])}"


def write_report(items, counts, comp_rows, bins, cat_rows, audit_summary) -> None:
    by = {r["group"]: r for r in comp_rows}
    allr = by["all"]
    status_counts = Counter(rec["status"] for rec in counts.values())
    exact = [rec for rec in counts.values() if rec["status"] == "exact"]
    under = [rec for rec in exact if rec["N"] < CAP]
    applied = [it for it in items if it.get("filter_status", "").startswith("applied") or it.get("filter_status") == "empty_formula"]
    lines = []
    a = lines.append
    a("# Constraint funnel on the locked IRSpectra-Bench n=500 roster")
    a("")
    a("Offline diagnostics only. No model was called. The locked generation outcome is unchanged:")
    a("")
    a("- 227 exact top-1")
    a("- 22 in the k≤3 pool but not top-1")
    a("- 251 never proposed at k≤3")
    a("")
    a("Recall at k≤3 is 249/500 (227 + 22). These three integers are the generation wall, not the forward-verify chamfer classes (204 verified, 45 mis-ranked, 251 never proposed). This directory does not replace either set.")
    a("")
    a("A rescore of the deposited rank lists against the offline structures reproduced every locked slice total before any isomer count was interpreted: 55/194, 63/106, and 109/200 top-1; 65/194, 68/106, and 116/200 recall; simple 161/248 and 172/248; complex 66/252 and 77/252.")
    a("")
    a("## Roster")
    a("")
    a(f"Source commit for the two expansion arms: `{EXPAND_SHA}`.")
    a("")
    a("The 500 problems are the locked `score_main` 194 (clean main + all of benchmark_v3 + all of benchmark_v2_ctrl), plus all 106 deposited Opus answers of the first expansion, plus the first 200 validate-clean expand-500 qids in `headline500_expand200_qids.json` (R01 through R75 in that file's sort). Sensitivity pools n=524 and n=530 are not in this roster.")
    a("")
    a("Gold structures were recovered by the same unique (formula, IR, 13C) join used when those arms were scored. On the 194, the join InChIKey-14 matches the committed answer key. Gold SMILES were not an input to surge and were not a filter. They are attached afterwards as the wall label, and separately as a post-hoc check of whether the true structure would have survived the rules.")
    a("")
    a("## A. Printed-list completeness")
    a("")
    a("Counts are taken from the printed question fields.")
    a("")
    a("- `n_C` and `n_H` are atom counts in the printed molecular formula. Three formulas carry a trailing charge (`C11H16NO3S2-`, `C13H7O2S2-`, `C32H48NO4-`). The charge is recorded and is not added to the hydrogen count.")
    a("- `n_13C` is the number of 13C chemical-shift signals after a top-level comma/semicolon split. A hyphenated range is one signal. Every one of the 500 stored 13C strings labels each signal `(1C, ...)`, and that parenthetical is 1 for every signal, so it is not an independent carbon integration. It is not summed as a measured carbon count.")
    a("- `n_ir` is the length of the printed IR list, including any repeated wavenumbers.")
    a(f"- `n_1H_env` is the number of 1H signals. The string is cut at the first `13C`, `MS`, `HRMS`, `ESI`, or `Anal` token ({allr['section_cut']}/500 fields continue into a later section). A hyphenated range is one signal. A missing comma between two signals is split. One missing opening parenthesis (locked-main R127) is repaired before the count. expand500 R224 stays unbalanced; its seven environments are counted and its integrals are not treated as complete.")
    a("- The summed proton count is reported only when every environment has one integral. Fractional integrals (`0.5H`) are summed and then excluded from the integer hydrogen filter.")
    a("")
    a(f"On all 500: median n_C {allr['median_n_C']}, median n_H {allr['median_n_H']}, median n_13C {allr['median_n_13C']}, median n_IR {allr['median_n_ir']}, median 1H environments {allr['median_n_1H_env']}, median n_13C/n_C {allr['median_n_13C_over_n_C']:.4f}.")
    a("")
    a(f"13C signal count versus formula carbons: {allr['n_13C_eq_n_C']}/500 equal, {allr['n_13C_lt_n_C']}/500 fewer signals than carbons, {allr['n_13C_gt_n_C']}/500 more signals than carbons.")
    a("")
    a(f"1H integrals parse for every environment in {allr['h_integral_complete']}/500 problems ({allr['h_integral_complete_integer']} of those sums are integers; the rest contain a fractional integral). Among the parsed sums, {allr['h_sum_eq_n_H']} equal n_H, {allr['h_sum_lt_n_H']} are below n_H, and {allr['h_sum_gt_n_H']} exceed n_H.")
    a("")
    a(f"Section cuts in the 1H field: {allr['section_cut']}/500.")
    a("")
    a("By locked wall class (denominators are the locked class sizes):")
    a("")
    a("| wall class | n | n_13C = n_C | n_13C < n_C | n_13C > n_C | median n_13C/n_C | 1H integrals complete | sum = n_H |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|")
    for wall in WALL_ORDER:
        r = by[wall]
        a(f"| {WALL_LABEL[wall]} | {r['n']} | {r['n_13C_eq_n_C']} | {r['n_13C_lt_n_C']} | {r['n_13C_gt_n_C']} | {r['median_n_13C_over_n_C']:.4f} | {r['h_integral_complete']} | {r['h_sum_eq_n_H']} |")
    a("")
    a("By the simple/complex label already stored on the questions (248 simple, 252 complex):")
    a("")
    a("| stratum | n | n_13C = n_C | n_13C < n_C | n_13C > n_C | median n_13C/n_C | median n_IR | median 1H environments | top-1 | recall k≤3 |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for name in ("simple", "complex"):
        r = by[name]
        a(f"| {name} | {r['n']} | {r['n_13C_eq_n_C']} | {r['n_13C_lt_n_C']} | {r['n_13C_gt_n_C']} | {r['median_n_13C_over_n_C']:.4f} | {r['median_n_ir']} | {r['median_n_1H_env']} | {r['top1']}/{r['n']} | {r['recalled']}/{r['n']} |")
    a("")
    a("The stratum top-1 and recall cells are the locked 161/248, 66/252, 172/248, and 77/252. They are reprinted so the completeness columns sit next to them.")
    a("")
    a("### Suggested figure")
    a("")
    a("`fig_completeness_vs_outcome.png` has two panels. The left panel is n_13C/n_C by the three locked wall classes, including the lists with more signals than carbons. The right panel is top-1 and recall at k≤3 inside bins of that ratio. Dashed lines are the locked rates 227/500 and 249/500. Bin counts:")
    a("")
    a("| bin of n_13C/n_C | n | top-1 | recall k≤3 | in pool, not top-1 | never proposed |")
    a("|---|---:|---:|---:|---:|---:|")
    for r in bins:
        a(f"| {r['bin']} | {r['n']} | {r['top1']} | {r['recall_k3']} | {r['in_pool_not_top1']} | {r['never']} |")
    a("")
    a("The top-1 column sums to 227 and the recall column sums to 249. This is a stratification of the locked outcome, not a new score.")
    a("")
    a("## B. Constraint funnel")
    a("")
    a("### IR rule table")
    a("")
    a("Rules fire on presence only. A missing band does not exclude a functional group, because the completeness counts above show that the printed lists are not full spectra.")
    a("")
    a("| rule | window (cm-1) | required substructure | problems triggered |")
    a("|---|---|---|---:|")
    a(f"| carbonyl_1650_1850 | 1650-1850 | `[#6]=[#8]` | {allr['carbonyl_rule']}/500 |")
    a(f"| oh_nh_3200_3600 | 3200-3600 | `[#8,#7;!H0]` | {allr['oh_nh_rule']}/500 |")
    a(f"| triple_or_cumulative_2100_2260 | 2100-2260 | alkyne, nitrile, isocyanate, isothiocyanate, or azide | {allr['triple_rule']}/500 |")
    a("")
    a("No nitro two-band rule is applied. The fingerprint pair is not specific on a short peak list. Full SMARTS and the boundary notes are in `ir_rule_table.csv`.")
    a("")
    a("### Isomer generator")
    a("")
    a("Constitutional isomers were counted with surge 2.0 (`-R`, aromaticity filter on) built against nauty 2.9.3. Self-checks, computed here, match the generator's known counts: C4H10 = 2, C2H6O = 2, C6H6 = 217, C10H16O = 452458, C8H10 = 4678 under `-R`, C4H12Sn = 9 with `-ESn4`.")
    a("")
    a("Valence model, summed as disjoint surge element types: C 4, O 2, H 1, F/Cl/Br/I 1, Si 4, B 3, Sn 4 (`-ESn4`), N 3 or 5 (`N`/`Nx`), S 2, 4, or 6 (`S`/`Sx`/`Sy`), Se 2, 4, or 6 (`-ESe2`/`-ESfSe4`/`-ESgSe6`), P 3 or 5 (`P`/`Px`). Lowest-valence parity failure is the same parity for every higher state that adds an even number of valence units. A formula is the sum of those states.")
    a("")
    a("Count mode is `surge -u -R`. The first budget is 40 s at or below 12 heavy atoms, 15 s at or below 15, 8 s at or below 20, and 5 s above that. When count mode does not finish, SMILES are streamed with a cap of 50,000. Hitting the cap proves N ≥ 50,000 for that state and therefore for the formula. It is not an exact count. Formulas that still emit nothing get one more stream of the lowest-valence state: 24 s, 14 s, or 8 s on the same heavy-atom cuts. The filters below are applied only when the summed count is exact and below 50,000, as requested.")
    a("")
    a(
        f"Unique formulas in the 500: {len(counts)}. "
        f"Exact count: {status_counts.get('exact', 0)}. "
        f"Proved at least 50,000 without an exact total: {status_counts.get('ge_50000', 0)}. "
        f"Not finished inside the time budget: {status_counts.get('unavailable', 0)}. "
        f"Charged formulas surge will not take: {status_counts.get('unsupported_charge', 0)}. "
        f"Exact and below 50,000, so the filters were run: {len(under)}."
    )
    filtered_rows = [
        it for it in items
        if isinstance(it.get("N_formula"), int) and it["N_formula"] < CAP and it.get("N_formula_status") == "exact"
    ]
    if filtered_rows:
        a("")
        a("Those exact counts below 50,000, and the filters, are:")
        a("")
        a("| problem | wall class | formula | N_formula | parsed | N after IR | N after IR and carbon | hydrogen filter | N_after_filters |")
        a("|---|---|---|---:|---:|---:|---:|---|---:|")
        for it in sorted(filtered_rows, key=lambda r: (r["formula"], r["uid"])):
            a(
                f"| {it['uid']} | {WALL_LABEL[it['wall_class']]} | {it['formula']} | {it['N_formula']} | "
                f"{it.get('n_parsed')} | {it.get('N_after_ir')} | {it.get('N_after_ir_carbon')} | "
                f"{'yes' if it.get('h_filter_applied') else 'no'} | {it.get('N_after_filters')} |"
            )
        zeros = [it for it in filtered_rows if it.get("N_after_filters") == 0]
        if zeros:
            a("")
            for it in zeros:
                fired = ", ".join(it["ir_rules"]) if it["ir_rules"] else "no IR rule"
                holds = "yes" if it.get("posthoc_ir_pass") else "no"
                a(
                    f"{it['uid']} ({it['formula']}) is the zero. Printed bands fire {fired}. "
                    f"The true structure satisfies that IR test: {holds}. "
                    "k/N is left blank when the remaining count is 0."
                )
    a("")
    a("Three charged formulas are outside surge's neutral graph model (`unsupported_charge`). Their completeness rows are present. Their isomer counts are blank, not guessed.")
    a("")
    a("A blank count is not a large count. Median heavy-atom counts by generator status:")
    a("")
    a("| status | formulas | median heavy atoms |")
    a("|---|---:|---:|")
    for status_name in ("exact", "ge_50000", "unavailable", "unsupported_charge"):
        group = [rec for rec in counts.values() if rec["status"] == status_name and rec.get("heavy_atoms") is not None]
        if not group:
            continue
        med = statistics.median([rec["heavy_atoms"] for rec in group])
        med_s = str(int(med)) if float(med).is_integer() else f"{med:.1f}"
        a(f"| {status_name} | {len(group)} | {med_s} |")
    a("")
    a("Formulas that finished, or that were proved to be at least 50,000, are the smaller ones. The unfinished formulas are heavier. That split follows the time budget, not a measured isomer total, so it is not used as a log10.")
    a("")
    a("### Carbon-count and hydrogen-count filters")
    a("")
    a("Applied only inside an exact formula with N < 50,000, and only to RDKit-parsed surge SMILES.")
    a("")
    a("- Carbon: the number of symmetry-distinct carbons (RDKit `CanonicalRankAtoms`, stereochemistry removed) is at least the printed 13C signal count. Accidental overlap and missing signals both make the structure have more distinct carbons than observed signals, so the inequality is the direction that stays valid. Equality is not required. If the printed list has more signals than formula carbons, no isomer passes.")
    a("- Hydrogen: applied only when every 1H environment has one positive integer integral and the sum is at most n_H. Each constitutional proton class (equivalent atoms times hydrogens on each) must be used whole. Classes may combine into one observed integral. Classes may be left unused when the integral sum is below n_H. Classes are not split, so a diastereotopic CH2 counted as one 2H class will fail a spectrum that shows two 1H signals. That limitation is measured by the gold audit rather than patched against the answers.")
    a("- IR rules that fired are required as well. A problem with no band inside the three windows has no IR constraint.")
    a("")
    a("`N_after_filters` is the number of parsed isomers that pass the fired IR rules, the carbon inequality, and the hydrogen partition when that partition is applicable. Unparsed surge SMILES, which are concentrated in the pentavalent-nitrogen drawings, are counted beside this number and are not called passes. If any hydrogen search is undecided, `N_after_filters` is left blank.")
    a("")
    a(f"Problems with a filter result: {len(applied)}/{len(items)}.")
    a("")
    a("### log10(N) against the wall classes")
    a("")
    a("Exact log10 values are reported only for exact positive counts. A formula proved only to be at least 50,000 is censored and is not entered as log10(50000).")
    a("")
    a("Formula-count category by wall class (each problem once; shared formulas are not reweighted):")
    a("")
    a("| group | n | exact <1000 | 1000-9999 | 10000-49999 | exact ≥50000 | censored ≥50000 | charge | unavailable |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in cat_rows:
        a(f"| {row['group']} | {row['n']} | {row['exact_<1000']} | {row['exact_1000_9999']} | {row['exact_10000_49999']} | {row['exact_ge_50000']} | {row['censored_ge_50000']} | {row['unsupported_charge']} | {row['unavailable']} |")
    a("")
    a("log10 of exact N_formula, problems whose formula count finished and is positive:")
    a("")
    for wall, text in audit_summary["log10_formula"].items():
        a(f"- {wall}: {text}")
    a("")
    a("log10 of N_after_filters, only where the filter ran and the remaining count is positive:")
    a("")
    for wall, text in audit_summary["log10_filtered"].items():
        a(f"- {wall}: {text}")
    a("")
    a("### Chance baseline")
    a("")
    a("For each problem the denominator is N_after_filters when that count exists, otherwise the exact N_formula. k/N is reported at k=3 and k=10. Censored and unavailable denominators are left blank. They are not replaced by 50,000. Where a denominator exists and is positive, the mean of the 3/N values is a property of that subset only.")
    a("")
    a(f"Problems with an exact positive chance denominator: {audit_summary['n_chance']}/500.")
    a(f"Of those, the denominator is N_after_filters for {audit_summary['n_chance_filtered']} and N_formula for {audit_summary['n_chance_formula']}.")
    a("")
    for wall, text in audit_summary["chance"].items():
        a(f"- {wall}: {text}")
    a("")
    a("### Post-hoc gold audit")
    a("")
    a("This section uses the true structure after N was computed. It does not remove isomers and it was not used to choose the windows.")
    a("")
    a(f"Where a carbonyl-window band is printed ({audit_summary['audit']['carbonyl_n']} problems), the true structure contains `[#6]=[#8]` in {audit_summary['audit']['carbonyl_pass']} cases.")
    a(f"Where a 3200-3600 band is printed ({audit_summary['audit']['oh_n']} problems), the true structure has an O-H or N-H in {audit_summary['audit']['oh_pass']} cases.")
    a(f"Where a 2100-2260 band is printed ({audit_summary['audit']['triple_n']} problems), the true structure matches the triple-bond or cumulative-bond SMARTS in {audit_summary['audit']['triple_pass']} cases.")
    a(f"Carbon inequality on the true structure: {audit_summary['audit']['carbon_pass']}/500.")
    a(f"Hydrogen partition, on the {audit_summary['audit']['h_n']} problems where the integer filter applies: pass {audit_summary['audit']['h_pass']}, fail {audit_summary['audit']['h_fail']}.")
    a("")
    a("Fails are expected when a printed band is not the functional group the window names (alkyne C-H inside 3200-3600, an overtone, a solvent band) or when diastereotopic protons split a CH2. Those fails are why absence rules were not added, and why N_after_filters should be read as the size of this explicit constraint set rather than as the size of the true spectroscopic preimage.")
    a("")
    a("## Files")
    a("")
    a("- `completeness_by_item.csv` — one row per problem, printed counts and the locked wall class")
    a("- `completeness_by_group.csv` — the citation table for wall class and stratum")
    a("- `figure_completeness_bins.csv` — the figure's exact bin counts")
    a("- `fig_completeness_vs_outcome.png` and `.pdf`")
    a("- `ir_rule_table.csv`")
    a("- `formula_counts.jsonl` — per-formula surge record, including every valence state")
    a("- `isomer_counts_by_formula.csv`")
    a("- `funnel_by_item.csv` — N_formula, N_after_filters, and k/N")
    a("- `formula_count_by_wall.csv`")
    a("- `posthoc_gold_audit.csv`")
    a("- `summary.json`")
    a("")
    a("## Reproduce")
    a("")
    a("surge 2.0 was built from https://github.com/StructureGenerator/surge against nauty 2.9.3. The binary used here is `/tmp/surge/src/surge` (override with `SURGE`). RDKit parses SMILES for the filters. Gold comes from `data/irexp_resolved/irexp_resolved.jsonl.gz` on this checkout. Expansion questions and predictions are read with `git show` from the pinned commit and are not copied into this branch.")
    a("")
    a("```")
    a("python3 analysis/iclr_rebuttal_nov2026/constraint_funnel/run_analysis.py")
    a("```")
    a("")
    a("A formula already present in `formula_counts.jsonl` with this model id is reused. Delete that file to rerun surge.")
    a("")
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")


def build_audit_summary(items: list[dict]) -> dict:
    def subset(rule):
        return [it for it in items if rule in it["ir_rules"]]

    def passes(rows, key):
        return sum(it.get(key) is True for it in rows)

    carb = subset("carbonyl_1650_1850")
    oh = subset("oh_nh_3200_3600")
    tri = subset("triple_or_cumulative_2100_2260")
    h_rows = [it for it in items if it.get("posthoc_h_pass") is not None or (
        it["h_integral_status"] == "complete" and it["h_integral_sum"] is not None and it["h_integral_sum"] <= it["n_H"]
    )]
    # posthoc_h_pass is None when the filter does not apply; it is True/False when it does.
    h_eval = [it for it in items if it.get("posthoc_h_pass") is True or it.get("posthoc_h_pass") is False]
    chance_rows = []
    n_filt = n_form = 0
    for it in items:
        if it.get("N_after_filters") not in (None, "") and it.get("filter_status", "").startswith("applied"):
            den = it["N_after_filters"]
            src = "filtered"
        elif it.get("N_formula_status") == "exact" and it.get("N_formula") not in (None, 0):
            den = it["N_formula"]
            src = "formula"
        else:
            continue
        if not isinstance(den, int) or den <= 0:
            continue
        chance_rows.append((it["wall_class"], 3 / den, src))
        if src == "filtered":
            n_filt += 1
        else:
            n_form += 1
    chance_text = {}
    for wall in ["all", *WALL_ORDER]:
        vals = [v for w, v, _ in chance_rows if wall == "all" or w == wall]
        if not vals:
            chance_text[wall] = "no exact denominator"
        else:
            chance_text[wall] = (
                f"n={len(vals)}, median 3/N = {statistics.median(vals):.3e}, "
                f"mean 3/N = {statistics.fmean(vals):.3e}"
            )
    log_f = {}
    log_a = {}
    for wall, q in log_summary(items, "N_formula").items():
        log_f[wall] = fmt_q(q)
    for wall, q in log_summary(items, "N_after_filters").items():
        log_a[wall] = fmt_q(q)
    return {
        "n_chance": len(chance_rows),
        "n_chance_filtered": n_filt,
        "n_chance_formula": n_form,
        "chance": chance_text,
        "log10_formula": log_f,
        "log10_filtered": log_a,
        "audit": {
            "carbonyl_n": len(carb),
            "carbonyl_pass": sum(mol_rule_pass(it, "carbonyl_1650_1850") for it in carb),
            "oh_n": len(oh),
            "oh_pass": sum(mol_rule_pass(it, "oh_nh_3200_3600") for it in oh),
            "triple_n": len(tri),
            "triple_pass": sum(mol_rule_pass(it, "triple_or_cumulative_2100_2260") for it in tri),
            "carbon_pass": sum(it.get("posthoc_carbon_pass") is True for it in items),
            "h_n": len(h_eval),
            "h_pass": sum(it.get("posthoc_h_pass") is True for it in h_eval),
            "h_fail": sum(it.get("posthoc_h_pass") is False for it in h_eval),
        },
    }


def mol_rule_pass(it: dict, rule_id: str) -> bool:
    mol = Chem.MolFromSmiles(it["gold_smiles"])
    if mol is None:
        return False
    return mol_matches(mol, rule_id)


def per_rule_audit(items: list[dict]) -> list[dict]:
    rows = []
    for rule in IR_RULES:
        group = [it for it in items if rule["rule_id"] in it["ir_rules"]]
        rows.append({
            "rule_id": rule["rule_id"],
            "n_triggered": len(group),
            "gold_passes": sum(mol_rule_pass(it, rule["rule_id"]) for it in group),
            "gold_fails": sum(not mol_rule_pass(it, rule["rule_id"]) for it in group),
        })
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("parser self-check", flush=True)
    self_check_parser()
    print("surge self-check", flush=True)
    self_check_surge()
    print("load roster", flush=True)
    items = load_roster()
    assert_lock(items)
    print("lock reproduced 227/22/251", flush=True)
    items.sort(key=lambda it: (it["arm"], it["cohort"], qnum(it["qid"]), it["qid"]))

    comp_rows = completeness_table(items)
    bins = figure_bins(items)
    write_csv(OUT / "completeness_by_group.csv", comp_rows, list(comp_rows[0].keys()))
    write_csv(OUT / "figure_completeness_bins.csv", bins, list(bins[0].keys()))
    write_figure(items, bins)

    formulas = sorted({it["formula"] for it in items})
    counts = enumerate_formulas(formulas)
    print("apply filters", flush=True)
    apply_filters(items, counts)
    print("gold audit", flush=True)
    gold_audit(items)
    audit = build_audit_summary(items)
    cat_rows = n_category_table(items, counts)

    comp_fields = [
        "uid", "cohort", "qid", "arm", "difficulty", "wall_class", "formula", "charge",
        "n_C", "n_H", "n_13C", "n_13C_over_n_C", "n_ir", "n_1H_env",
        "h_integral_sum", "h_integral_status", "h_section_cut", "h_paren_repairs",
        "ir_rules", "c13_annot_all_one",
    ]
    comp_out = []
    for it in items:
        comp_out.append({
            **{k: it[k] for k in comp_fields if k not in {"n_13C_over_n_C", "ir_rules"}},
            "n_13C_over_n_C": f"{it['n_13C'] / it['n_C']:.6f}" if it["n_C"] else "",
            "ir_rules": ";".join(it["ir_rules"]),
            "h_integral_sum": "" if it["h_integral_sum"] is None else it["h_integral_sum"],
        })
    write_csv(OUT / "completeness_by_item.csv", comp_out, comp_fields)

    funnel_fields = [
        "uid", "wall_class", "difficulty", "formula", "N_formula_status", "N_formula",
        "N_formula_lower_bound", "log10_N_formula", "n_parsed", "n_unparsed",
        "N_after_ir", "N_after_ir_carbon", "h_filter_applied", "N_after_filters",
        "log10_N_after_filters", "filter_status", "chance_denominator", "chance_source",
        "chance_k3", "chance_k3_decimal", "chance_k10", "chance_k10_decimal", "ir_rules",
    ]
    funnel_out = []
    for it in items:
        if str(it.get("filter_status", "")).startswith("applied") and isinstance(it.get("N_after_filters"), int):
            den, src = it["N_after_filters"], "N_after_filters"
        elif it.get("N_formula_status") == "exact" and isinstance(it.get("N_formula"), int):
            den, src = it["N_formula"], "N_formula"
        else:
            den, src = None, ""
        c3, c3d = chance(3, den if isinstance(den, int) and den > 0 else None)
        c10, c10d = chance(10, den if isinstance(den, int) and den > 0 else None)
        funnel_out.append({
            "uid": it["uid"],
            "wall_class": it["wall_class"],
            "difficulty": it["difficulty"],
            "formula": it["formula"],
            "N_formula_status": it.get("N_formula_status", ""),
            "N_formula": "" if it.get("N_formula") is None else it["N_formula"],
            "N_formula_lower_bound": "" if it.get("N_formula_lower_bound") is None else it["N_formula_lower_bound"],
            "log10_N_formula": log10_or_blank(it["N_formula"] if it.get("N_formula_status") == "exact" else None),
            "n_parsed": "" if it.get("n_parsed") is None else it["n_parsed"],
            "n_unparsed": "" if it.get("n_unparsed") is None else it["n_unparsed"],
            "N_after_ir": "" if it.get("N_after_ir") is None else it["N_after_ir"],
            "N_after_ir_carbon": "" if it.get("N_after_ir_carbon") is None else it["N_after_ir_carbon"],
            "h_filter_applied": it.get("h_filter_applied", False),
            "N_after_filters": "" if it.get("N_after_filters") is None else it["N_after_filters"],
            "log10_N_after_filters": log10_or_blank(it.get("N_after_filters") if isinstance(it.get("N_after_filters"), int) else None),
            "filter_status": it.get("filter_status", ""),
            "chance_denominator": "" if not den else den,
            "chance_source": src,
            "chance_k3": c3,
            "chance_k3_decimal": c3d,
            "chance_k10": c10,
            "chance_k10_decimal": c10d,
            "ir_rules": ";".join(it["ir_rules"]),
        })
    write_csv(OUT / "funnel_by_item.csv", funnel_out, funnel_fields)

    formula_rows = []
    for formula in formulas:
        rec = counts[formula]
        formula_rows.append({
            "formula": formula,
            "status": rec["status"],
            "N": "" if rec.get("N") is None else rec["N"],
            "lower_bound": "" if rec.get("lower_bound") is None else rec["lower_bound"],
            "log10_N": log10_or_blank(rec["N"] if rec["status"] == "exact" else None),
            "heavy_atoms": rec.get("heavy_atoms", ""),
            "charge": rec.get("charge", ""),
            "n_variants_run": len(rec.get("variants") or []),
            "n_variants_possible": rec.get("n_variants_possible", ""),
            "category": formula_category(rec),
        })
    write_csv(
        OUT / "isomer_counts_by_formula.csv",
        formula_rows,
        ["formula", "status", "N", "lower_bound", "log10_N", "heavy_atoms", "charge", "n_variants_run", "n_variants_possible", "category"],
    )
    write_csv(OUT / "formula_count_by_wall.csv", cat_rows, list(cat_rows[0].keys()))
    write_csv(
        OUT / "ir_rule_table.csv",
        [
            {
                "rule_id": r["rule_id"],
                "window_cm_1": r["window_cm_1"],
                "trigger": r["trigger"],
                "requires": r["requires"],
                "smarts": " OR ".join(r["smarts"]),
                "note": r["note"],
                "absence_used": False,
            }
            for r in IR_RULES
        ],
        ["rule_id", "window_cm_1", "trigger", "requires", "smarts", "note", "absence_used"],
    )
    audit_rows = []
    for it in items:
        audit_rows.append({
            "uid": it["uid"],
            "wall_class": it["wall_class"],
            "ir_rules": ";".join(it["ir_rules"]),
            "posthoc_ir_pass": it.get("posthoc_ir_pass"),
            "posthoc_carbon_pass": it.get("posthoc_carbon_pass"),
            "posthoc_h_pass": "" if it.get("posthoc_h_pass") is None else it.get("posthoc_h_pass"),
            "posthoc_unique_C": "" if it.get("posthoc_unique_C") is None else it["posthoc_unique_C"],
            "n_13C": it["n_13C"],
            "n_C": it["n_C"],
        })
    write_csv(
        OUT / "posthoc_gold_audit.csv",
        audit_rows,
        ["uid", "wall_class", "ir_rules", "posthoc_ir_pass", "posthoc_carbon_pass", "posthoc_h_pass", "posthoc_unique_C", "n_13C", "n_C"],
    )
    rule_audit = per_rule_audit(items)
    summary = {
        "expand_sha": EXPAND_SHA,
        "model_id": MODEL_ID,
        "surge": SURGE,
        "locked_wall": {"top1": 227, "in_pool_not_top1": 22, "never_proposed_k_le_3": 251, "n": 500},
        "lock_reproduced": True,
        "n_formulas": len(formulas),
        "formula_status": dict(Counter(rec["status"] for rec in counts.values())),
        "completeness_all": next(r for r in comp_rows if r["group"] == "all"),
        "figure_bins": bins,
        "formula_by_wall": cat_rows,
        "ir_rule_audit": rule_audit,
        "audit": audit["audit"],
        "chance": {
            "n": audit["n_chance"],
            "n_filtered_denominator": audit["n_chance_filtered"],
            "n_formula_denominator": audit["n_chance_formula"],
            "by_wall": audit["chance"],
        },
        "log10_N_formula": audit["log10_formula"],
        "log10_N_after_filters": audit["log10_filtered"],
        "n_filter_applied": sum(str(it.get("filter_status", "")).startswith("applied") or it.get("filter_status") == "empty_formula" for it in items),
        "n_13C_gt_n_C": [
            {"uid": it["uid"], "formula": it["formula"], "n_C": it["n_C"], "n_13C": it["n_13C"]}
            for it in items if it["n_13C"] > it["n_C"]
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_report(items, counts, comp_rows, bins, cat_rows, audit)
    print("wrote", OUT, flush=True)


if __name__ == "__main__":
    main()
