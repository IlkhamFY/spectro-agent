"""
NIST WebBook IR source + JCAMP-DX decoder.

This is the *capstone* that mirrors how Spectro actually built its dataset:
Spectro pulled **IR spectra from NIST as JDX files** and joined them to NMR by
molecule. We do exactly that -- but via Scrapling's TLS impersonation instead of
manual downloads, and we key the join on the **InChIKey** resolved from the
paper-scraped compound name (OPSIN -> RDKit).

    paper compound name --OPSIN--> SMILES --RDKit--> InChIKey
                                                        │  resolve at NIST
                                                        ▼
                              NIST IR JCAMP-DX (the full spectral curve)

Flow per molecule:
    1. resolve_id(inchikey|name) -> NIST registry id "C100527"
    2. fetch_ir_jdx(id)          -> raw JCAMP-DX bytes (saved to disk = Spectro's
                                     native IR input format)
    3. parse_jdx(text)           -> {meta, x[cm^-1], y} via a self-contained ASDF
                                     (SQZ/DIF/DUP) decompressor.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..fetch import ResilientFetcher

NIST = "https://webbook.nist.gov/cgi/cbook.cgi"


# ---------------------------------------------------------------------------
# JCAMP-DX (X++(Y..Y)) ASDF decompression -- self-contained, no deps.
# ---------------------------------------------------------------------------
_SQZ = {c: str(i) for i, c in enumerate("@ABCDEFGHI")}            # +0..+9
_SQZ.update({c: "-" + str(i + 1) for i, c in enumerate("abcdefghi")})  # -1..-9
_DIF = {c: i for i, c in enumerate("%JKLMNOPQR")}                 # +0..+9
_DIF.update({c: -(i + 1) for i, c in enumerate("jklmnopqr")})    # -1..-9
_DUP = {c: i + 1 for i, c in enumerate("STUVWXYZ")}              # x1..x8
_DUP["s"] = 9


def _tokenize_asdf(field: str) -> list:
    """Split a data field into numeric tokens, expanding SQZ/DIF/DUP markers."""
    tokens, cur, mode = [], "", None
    for ch in field:
        if ch in _SQZ:
            if cur:
                tokens.append((mode, cur))
            cur, mode = _SQZ[ch], "SQZ"
        elif ch in _DIF:
            if cur:
                tokens.append((mode, cur))
            cur, mode = str(_DIF[ch]), "DIF"
        elif ch in _DUP:
            if cur:
                tokens.append((mode, cur))
            tokens.append(("DUP", str(_DUP[ch])))
            cur, mode = "", None
        elif ch.isdigit():
            cur += ch
        elif ch == ".":
            cur += ch
        elif ch in "+-":
            if cur:
                tokens.append((mode, cur))
            cur, mode = ("-" if ch == "-" else ""), "AFFN"
        elif ch in " \t,":
            if cur:
                tokens.append((mode, cur))
            cur, mode = "", None
        # ignore others
    if cur:
        tokens.append((mode, cur))
    return tokens


def _decode_xydata(lines: list[str]) -> list[float]:
    """Decode the Y stream from JCAMP XYDATA lines (ASDF aware)."""
    ys: list[float] = []
    last = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("$$"):
            continue
        toks = _tokenize_asdf(line)
        if not toks:
            continue
        # first token on each line is X (drop it); rest are Y
        first_mode = toks[0][0]
        body = toks[1:] if first_mode in ("AFFN", "SQZ", None) else toks[1:]
        for mode, val in body:
            if mode == "DUP":
                n = int(val)
                if last is not None:
                    ys.extend([last] * (n - 1))
            elif mode == "DIF":
                if last is None:
                    last = float(val)
                else:
                    last = last + float(val)
                ys.append(last)
            else:  # SQZ or AFFN -> absolute value
                last = float(val)
                ys.append(last)
    return ys


def parse_jdx(text: str) -> dict:
    """Parse a JCAMP-DX IR file into {meta, x, y}. Robust to compression."""
    meta = {}
    for m in re.finditer(r"##([A-Z0-9 _/.-]+)=\s*([^\r\n]*)", text):
        meta[m.group(1).strip().upper()] = m.group(2).strip()

    def fnum(k, default=None):
        try:
            return float(meta.get(k, default))
        except (TypeError, ValueError):
            return default

    firstx, lastx = fnum("FIRSTX"), fnum("LASTX")
    npoints = int(fnum("NPOINTS", 0) or 0)
    yfactor = fnum("YFACTOR", 1.0) or 1.0
    xfactor = fnum("XFACTOR", 1.0) or 1.0

    # Extract the data block after ##XYDATA=(X++(Y..Y))
    y: list[float] = []
    dm = re.search(r"##XYDATA=\(X\+\+\(Y\.\.Y\)\)\s*(.*?)##END", text,
                   re.DOTALL | re.IGNORECASE)
    if dm:
        y = _decode_xydata(dm.group(1).splitlines())
        y = [v * yfactor for v in y]

    # Reconstruct the X (wavenumber) grid from header (linear, exact for NIST).
    x: list[float] = []
    n = len(y) if y else npoints
    if firstx is not None and lastx is not None and n > 1:
        step = (lastx - firstx) / (n - 1)
        x = [firstx + i * step for i in range(n)]

    return {
        "meta": {
            "title": meta.get("TITLE"),
            "xunits": meta.get("XUNITS"),
            "yunits": meta.get("YUNITS"),
            "firstx": firstx, "lastx": lastx,
            "npoints": npoints, "resolution": meta.get("RESOLUTION"),
            "state": meta.get("STATE"), "origin": meta.get("ORIGIN"),
        },
        "x": x, "y": y,
    }


# ---------------------------------------------------------------------------
# NIST client
# ---------------------------------------------------------------------------
class NISTIRClient:
    def __init__(self, fetcher: ResilientFetcher | None = None,
                 save_dir="data/output/nist_ir"):
        self.f = fetcher or ResilientFetcher(min_interval=0.5)
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def resolve_id(self, inchikey: str | None = None,
                   name: str | None = None) -> str | None:
        """Resolve a molecule to its NIST registry id (e.g. 'C100527')."""
        if inchikey:
            url = f"{NIST}?InChI={inchikey}"
        elif name:
            from urllib.parse import quote
            url = f"{NIST}?Name={quote(name)}&Units=SI"
        else:
            return None
        res = self.f.get(url)
        if not res.ok:
            return None
        m = re.search(r"cbook\.cgi\?(?:ID|GetInChI)=(C\d+)", res.text)
        if m:
            return m.group(1)
        # a direct hit lands on the species page whose URL carries the id
        m = re.search(r'/cgi/cbook\.cgi\?ID=(C\d+)', res.text)
        return m.group(1) if m else None

    def has_ir(self, nist_id: str) -> bool:
        res = self.f.get(f"{NIST}?ID={nist_id}&Units=SI&Type=IR-SPEC")
        return res.ok and ("INFRARED" in res.text.upper()
                           or "Infrared Spectrum" in res.text)

    def fetch_ir_jdx(self, nist_id: str, index: int = 0) -> bytes | None:
        url = f"{NIST}?JCAMP={nist_id}&Index={index}&Type=IR"
        res = self.f.get(url, binary=True)
        if res.ok and res.content[:2] == b"##":
            return res.content
        return None

    def fetch_ir(self, inchikey: str | None = None, name: str | None = None,
                 save_as: str | None = None) -> dict | None:
        """Full path: resolve -> fetch IR JDX -> save -> parse curve."""
        nist_id = self.resolve_id(inchikey=inchikey, name=name)
        if not nist_id:
            return None
        jdx = self.fetch_ir_jdx(nist_id)
        if not jdx:
            return None
        stem = save_as or inchikey or nist_id
        path = self.save_dir / f"{stem}.jdx"
        path.write_bytes(jdx)
        parsed = parse_jdx(jdx.decode("latin-1"))
        return {
            "nist_id": nist_id,
            "jdx_path": str(path),
            "npoints": len(parsed["y"]) or parsed["meta"]["npoints"],
            "xunits": parsed["meta"]["xunits"],
            "x_range": [parsed["meta"]["firstx"], parsed["meta"]["lastx"]],
            "meta": parsed["meta"],
        }
