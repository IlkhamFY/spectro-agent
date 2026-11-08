"""Parse printed 1H / 13C peak lists. Does not read a structure."""
from __future__ import annotations

import re

_GROUP = re.compile(
    r"((?:-?\d+\.?\d*\s*(?:[-–]\s*-?\d+\.?\d*)?\s*,\s*)*"
    r"-?\d+\.?\d*(?:\s*[-–]\s*-?\d+\.?\d*)?)\s*\(([^)]*)\)"
)
_SHIFT = re.compile(r"-?\d+\.?\d*(?:\s*[-–]\s*-?\d+\.?\d*)?")
# Proton count, not the H in Hz. "7.2 Hz" must not become 7.2H.
_NH = re.compile(r"(\d+\.?\d*)\s*H\b", re.I)
_JCLAUSE = re.compile(r"J\s*=\s*[0-9.,\s]+Hz", re.I)
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*")
_MULT_OK = re.compile(
    r"^(?:br\s*)?(?:\d+)?(?:s|d|t|q|m|p|h|hept|dd|dt|td|dq|qd|tt|qq|ddd|ddt|dtd|tdd|ddd)$",
    re.I,
)
_C_ENTRY = re.compile(
    r"(-?\d+\.?\d*)(?:\s*[-–]\s*-?\d+\.?\d*)?\s*(?:\(\s*(\d+)\s*C\b)?",
    re.I,
)


def _midpoint(token: str) -> float:
    parts = re.split(r"\s*[-–]\s*", token.strip())
    vals = [float(p) for p in parts if p]
    return sum(vals) / len(vals)


def _integral(inner: str) -> float | None:
    """Printed proton count.

    Accepts `3H`, `2 H`, and the hyphen form `5-H`.
    Rejects position labels `5H′` and `5H d` (no comma between the count and the
    multiplet). A missing count is left missing.
    """
    hyphen = re.search(r"(\d+\.?\d*)\s*-\s*H\b", inner)
    if hyphen:
        return float(hyphen.group(1))
    match = re.search(r"(\d+\.?\d*)\s*H(?!['′])\b", inner, re.I)
    if not match:
        return None
    tail = inner[match.end():]
    if re.match(r"\s+[A-Za-z]", tail) and not tail.lstrip().startswith(","):
        return None
    return float(match.group(1))


def _multiplicity(inner: str) -> str:
    """First multiplet token after the integral and the J clause are removed."""
    cleaned = _NH.sub(" ", inner)
    cleaned = _JCLAUSE.sub(" ", cleaned)
    toks = _WORD.findall(cleaned)
    i = 0
    while i < len(toks):
        tok = toks[i]
        if tok.lower() == "br" and i + 1 < len(toks):
            joined = f"br {toks[i + 1]}"
            if _MULT_OK.match(joined) or _MULT_OK.match(toks[i + 1]):
                return joined
        if _MULT_OK.match(tok):
            return tok
        i += 1
    return "m"


def parse_h(text: str) -> tuple[list[tuple[float, float, str]], dict]:
    """Return (shift_ppm, nH, multiplicity) and a small parse report.

    Several shifts that share one parenthesis split the printed integral equally.
    A peak with no printed proton count is dropped, not filled in as 1H.
    """
    peaks: list[tuple[float, float, str]] = []
    dropped_no_h = 0
    groups = 0
    # A semicolon between a shift and its parenthesis otherwise splits the group.
    text = (text or "").replace(";", " ")
    for match in _GROUP.finditer(text):
        groups += 1
        shifts = [_midpoint(tok) for tok in _SHIFT.findall(match.group(1)) if tok.strip()]
        inner = match.group(2)
        mult = _multiplicity(inner)
        nh = _integral(inner)
        if nh is None or not shifts:
            dropped_no_h += len(shifts) or 1
            continue
        each = nh / len(shifts)
        for shift in shifts:
            peaks.append((shift, each, mult))
    return peaks, {"groups": groups, "peaks": len(peaks), "dropped_no_h": dropped_no_h}


def parse_c(text: str) -> list[float]:
    """One ppm per printed carbon. `(nC)` repeats the shift n times.

    A range uses the midpoint once (or n times when an nC count is printed).
    """
    out: list[float] = []
    for match in _C_ENTRY.finditer(text or ""):
        ppm = float(match.group(1))
        # The nC count is a separate integer; do not also emit it as a shift.
        n = int(match.group(2) or 1)
        if n < 1 or n > 30:
            n = 1
        out.extend([ppm] * n)
    return out


def formula_h(formula: str) -> int | None:
    found = re.findall(r"H(\d*)", formula or "")
    if not found:
        return 0 if formula else None
    return sum(int(n) if n else 1 for n in found)
