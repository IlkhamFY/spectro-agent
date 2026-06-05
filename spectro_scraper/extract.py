"""
Spectral data extraction engine.

Parses the *experimental section* text of an organic-chemistry paper (or its
Supporting Information) and pulls out, per reported compound, the canonical
spectroscopy strings that the Spectro model consumes:

    * ``1H NMR``  chemical-shift list
    * ``13C NMR`` chemical-shift list
    * ``IR``      band list (cm^-1)

plus useful provenance/metadata (compound label, physical appearance, yield,
HRMS, melting point).

The format reported in journals follows a remarkably stable convention, e.g.::

    1H NMR (400 MHz, CDCl3) δ 7.25 - 7.15 (m, 4H), 5.94 (t, J = 4.4 Hz, 1H), ...
    13C NMR (101 MHz, CDCl3) δ 137.0, 133.8, 128.7 (q, J = 282.0 Hz), ...
    IR (neat) ν 3024, 1715, 1602 cm-1

That regularity is what makes high-yield regex extraction possible. The
extractor is source-agnostic: feed it text from a Beilstein SI, a ChemRxiv
preprint, an RSC article -- anything -- and it returns structured records.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Optional

# ---------------------------------------------------------------------------
# Character normalisation
# ---------------------------------------------------------------------------
# PDF text extraction yields a zoo of dashes / spaces / minus signs. Fold them
# down to ASCII so the regexes stay simple and robust.
_DASHES = "‐‑‒–—―−"          # ‐ ‑ ‒ – — ― −
_SPACES = "        "     # nbsp, thin, etc.
_DELTA = "δ"   # δ
_NU = "ν"      # ν (IR stretch symbol)
_TILDE_NU = "ν̃"  # ν̃


def normalize_text(text: str) -> str:
    """Fold unicode dashes/spaces and repair PDF line-break hyphenation."""
    if not text:
        return ""
    # join hyphenated line breaks: "cross-\ncoupling" -> "crosscoupling"
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    # collapse remaining newlines to spaces (NMR strings often wrap mid-line)
    text = text.replace("\r", " ").replace("\n", " ")
    for d in _DASHES:
        text = text.replace(d, "-")
    for s in _SPACES:
        text = text.replace(s, " ")
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


# ---------------------------------------------------------------------------
# Section anchors
# ---------------------------------------------------------------------------
# A compound's data block ends when one of these "next section" markers appears.
# Used to bound the greedy capture of an NMR / IR payload.
_NEXT_SECTION = re.compile(
    r"(?:"
    r"\b(?:1H|13C|19F|31P|11B|15N|29Si|2H|7Li|77Se|119Sn)\s*[-\s]?NMR\b"
    r"|δ\s?[HC]\s?[(\d]"                       # Bruker δH(... / δC ... notation
    r"|\bHRMS\b|\bHR-MS\b|\bLRMS\b|\bMS\s*\(|\bESI\b|\bEI\b|\bAPCI\b|\bMALDI\b"
    r"|\b(?:FT-?IR|IR)\b|\bUV\b|\bAnal\.|\bAnalysis\b"
    r"|\b[mM]\.?\s?p\.?\s*[:=]|\bmelting\b"
    r"|\bHPLC\b|\b\[α\]|\boptical rotation\b|\bRf\s*[:=]|\bTLC\b"
    r"|\bGeneral\b|\bcompound\b|\bproduct\b"
    r")",
    re.IGNORECASE,
)

# Multiplicity tokens used in 1H NMR.
_MULT = r"(?:br\s?)?(?:s|d|t|q|p|sext|sept|h|m|dd|ddd|dddd|dt|td|tt|dq|qd|ddt|dtd|tdd|hept|spt|qt|tq|br\.?\s?s|br)"


@dataclass
class Peak:
    """A single NMR signal."""
    shift: str                 # "7.85" or "7.29-7.51"
    multiplicity: Optional[str] = None
    nuclei: Optional[int] = None     # integration (nH or nC)
    j: list[float] = field(default_factory=list)   # coupling constants (Hz)


@dataclass
class CompoundRecord:
    """All spectroscopy extracted for one reported compound."""
    label: Optional[str] = None              # "3a", "product 6", IUPAC name...
    appearance: Optional[str] = None         # "colorless oil"
    yield_pct: Optional[float] = None
    h_nmr: Optional[str] = None              # raw δ-string (1H)
    c_nmr: Optional[str] = None              # raw δ-string (13C)
    ir: Optional[str] = None                 # raw IR band string
    ir_bands: list[float] = field(default_factory=list)   # parsed wavenumbers
    h_nmr_meta: Optional[str] = None         # "(400 MHz, CDCl3)"
    c_nmr_meta: Optional[str] = None
    hrms: Optional[str] = None
    mp: Optional[str] = None
    h_peaks: list[Peak] = field(default_factory=list)
    c_peaks: list[Peak] = field(default_factory=list)
    # filled in later by normalize.py
    name: Optional[str] = None
    smiles: Optional[str] = None
    selfies: Optional[str] = None
    inchikey: Optional[str] = None
    spectro_h: Optional[str] = None          # Spectro-format 1H δ-string
    spectro_c: Optional[str] = None          # Spectro-format 13C δ-string
    source_doi: Optional[str] = None
    source_url: Optional[str] = None
    # NIST IR join (Spectro-style: IR curve sourced from NIST, keyed by InChIKey)
    nist_id: Optional[str] = None
    nist_ir_jdx: Optional[str] = None        # path to saved JCAMP-DX file
    nist_ir_npoints: Optional[int] = None
    nist_ir_xrange: Optional[list] = None    # [firstx, lastx] in cm^-1
    quarantine_reasons: list = field(default_factory=list)  # quality-gate failures

    def to_dict(self) -> dict:
        d = asdict(self)
        d["h_peaks"] = [asdict(p) for p in self.h_peaks]
        d["c_peaks"] = [asdict(p) for p in self.c_peaks]
        return d

    @property
    def has_nmr(self) -> bool:
        return bool(self.h_nmr or self.c_nmr)

    @property
    def has_ir(self) -> bool:
        return bool(self.ir)

    @property
    def has_paired(self) -> bool:
        """Both NMR and IR present -- the ideal Spectro training sample."""
        return self.has_nmr and self.has_ir


# ---------------------------------------------------------------------------
# Payload capture
# ---------------------------------------------------------------------------
def _capture_payload(text: str, start: int) -> str:
    """Grab everything from ``start`` up to the next section marker."""
    rest = text[start:]
    m = _NEXT_SECTION.search(rest, 1)   # skip pos 0 (the anchor itself)
    end = m.start() if m else min(len(rest), 1200)
    payload = rest[:end].strip(" ,.;:")
    return payload


def _split_top_level(s: str) -> list[str]:
    """Split on commas that are *not* nested inside parentheses."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return [x.strip() for x in out if x.strip()]


_J_RE = re.compile(r"J\s*=\s*([\d.,\s]+?)\s*Hz", re.IGNORECASE)
_SHIFT_RE = re.compile(r"-?\d+\.?\d*(?:\s*-\s*-?\d+\.?\d*)?")
_NH_RE = re.compile(r"(\d+)\s*[HC]\b")
_MULT_RE = re.compile(rf"\b({_MULT})\b")


def _is_name_fragment(tok: str) -> bool:
    """True if a token has bled into a compound name (letters outside parens).

    Peak tokens carry letters only *inside* parentheses (multiplicity, units,
    assignments). A 2+ letter run outside any paren means the NMR list ended and
    we've run into the next compound's IUPAC name, e.g. "3-dione (1h)".
    """
    residue = re.sub(r"\([^)]*\)", "", tok)
    return bool(re.search(r"[A-Za-z]{2,}", residue))


def _truncate_nmr_payload(s: str) -> str:
    """Cut an NMR shift list where the *next* compound's name begins.

    SI entries run "…last shift. <IUPAC name> (label). Yield …" with no section
    keyword between the shifts and the name, so the raw capture over-reads. We
    mask parenthesised descriptors/assignments (so "(m, 4H, pyridine)" is not
    mistaken for a name), find the first long lowercase word — which only occurs
    in a chemical name, never in a shift/multiplicity/unit token — and trim back
    to the sentence/comma boundary before it.
    """
    masked = s
    for _ in range(3):                      # blank nested parens, innermost first
        masked = re.sub(r"\([^()]*\)", lambda m: " " * len(m.group(0)), masked)
    m = re.search(r"[a-z]{5,}", masked)     # a name word (e.g. "propane", "phenyl")
    if not m:
        return s.strip(" ,.;:")
    # Cut at the last *sentence* period (".(space)") before the name -- not a
    # decimal point and not a comma (names carry locant commas like "1,2,4-").
    sentence_dots = [mt.start() for mt in re.finditer(r"\.(?=\s|$)", s[:m.start()])]
    cut = sentence_dots[-1] if sentence_dots else s.rfind(",", 0, m.start())
    if cut == -1:
        cut = m.start()
    return s[:cut].strip(" ,.;:")


def parse_h_peaks(delta_str: str) -> list[Peak]:
    """Parse a 1H NMR δ-string into individual signals."""
    peaks: list[Peak] = []
    for tok in _split_top_level(delta_str):
        if _is_name_fragment(tok):
            break       # NMR list ended; rest is the next compound's name
        sm = _SHIFT_RE.search(tok)
        if not sm:
            continue
        shift = re.sub(r"\s*-\s*", "-", sm.group(0))
        paren = re.search(r"\(([^)]*)\)", tok)
        mult = nh = None
        js: list[float] = []
        if paren:
            inner = paren.group(1)
            mm = _MULT_RE.search(inner)
            mult = mm.group(1).replace(" ", "") if mm else None
            nm = _NH_RE.search(inner)
            nh = int(nm.group(1)) if nm else None
            jm = _J_RE.search(inner)
            if jm:
                js = [float(x) for x in re.findall(r"\d+\.?\d*", jm.group(1))]
        peaks.append(Peak(shift=shift, multiplicity=mult, nuclei=nh, j=js))
    return peaks


def parse_c_peaks(delta_str: str) -> list[Peak]:
    """Parse a 13C NMR δ-string into individual signals."""
    peaks: list[Peak] = []
    for tok in _split_top_level(delta_str):
        if _is_name_fragment(tok):
            break       # 13C list ended; rest is the next compound's name
        sm = re.match(r"\s*(-?\d+\.?\d*)", tok)
        if not sm:
            continue
        mult = None
        js: list[float] = []
        paren = re.search(r"\(([^)]*)\)", tok)
        if paren:
            mm = _MULT_RE.search(paren.group(1))
            mult = mm.group(1).replace(" ", "") if mm else None
            jm = _J_RE.search(paren.group(1))
            if jm:
                js = [float(x) for x in re.findall(r"\d+\.?\d*", jm.group(1))]
        peaks.append(Peak(shift=sm.group(1), multiplicity=mult, nuclei=None, j=js))
    return peaks


# ---------------------------------------------------------------------------
# Field regexes
# ---------------------------------------------------------------------------
# Two notations in the wild:
#   A) "1H NMR (400 MHz, CDCl3) δ 7.78 ..."  /  "13C NMR (...) δ = 137.0 ..."
#   B) "δH(400 MHz, DMSO-d6): 9.1 ..."        /  "δC(101 MHz, ...) 137.0 ..."
# Both may use ':' or '=' before the shift list. The regex consumes everything
# up to (but not including) the first shift number.
#
# Notation B is guarded hard: δ must NOT follow a letter/digit (else it matches
# the Greek position label inside 13C assignments like "(uD -CδH3)" or "CγH"),
# and must be followed by a meta paren / ':' / '=' (the hallmark of the real
# notation) -- "CδH3)" has neither, so it is correctly rejected.
_NMR_RE = re.compile(
    r"(?:"
    r"(?P<nucA>1H|13C(?:\{1H\})?)\s*[-\s]?NMR\s*(?P<metaA>\([^)]{0,90}\))?"
    r"\s*[:=]?\s*(?:δ|delta)?\s*[:=]?\s*"
    r"|"
    r"(?<![A-Za-z0-9])(?P<nucB>δ\s?[HC])(?=\s*[(:=])\s*(?P<metaB>\([^)]{0,90}\))?\s*[:=]?\s*"
    r")",
    re.IGNORECASE,
)
_IR_RE = re.compile(
    r"\b(?:ATR-?FT-?IR|FT-?IR|IR)\b\s*"
    r"(?:\([^)]{0,45}\))?\s*"                 # (neat)/(ATR)/(KBr)/(thin film)
    r"(?:ν̃|ν|nu|vmax|v\s?max|v)?\s*(?:max)?\s*"
    r"(?:/?\s?cm\s?-?\s?1)?\s*[:=]?\s*",
    re.IGNORECASE,
)
_APPEAR_RE = re.compile(
    r"\b(?:as\s+(?:a|an)\s+)?((?:colou?rless|white|yellow|pale|light|dark|red|orange|"
    r"brown|green|blue|black|off-white|pink|colorless)[\w\s-]*?"
    r"(?:oil|solid|liquid|powder|crystals?|gum|foam|wax|needles|film))",
    re.IGNORECASE,
)
_YIELD_RE = re.compile(r"\((?:[\d.]+\s*(?:mg|g|mmol|µmol)[^)]*?)?(\d{1,3}(?:\.\d)?)\s*%\)")
# Compound header: "<IUPAC name> (<label>). [Yield ...]" -- the dominant SI
# convention. The label parenthetical contains ONLY digits + optional letter
# (e.g. "3a", "12"), which lets us tell it apart from parentheses inside the
# name itself, e.g. "(3-phenyl-1,2,4-oxadiazol-5-yl)".
_HEADER_RE = re.compile(
    # Start only at a real sentence boundary -- NOT after ')' (IUPAC names are
    # full of parens, and allowing ')' truncated names mid-token). Trailing
    # punctuation is optional; OPSIN/PubChem validate what we capture.
    r"(?:^|(?<=[.\n;]))[ \t]*"
    r"(?P<name>[A-Za-z0-9(\[][^.\n;]{4,200}?)\s*"
    r"\((?P<label>\d{1,3}[a-z]?)\)\s*[.:]?",
)
# A "looks like a chemical name" gate before we bother OPSIN.
_NAMEISH = re.compile(r"[a-z]{3}.*(?:yl|one|ol|al|ate|ide|ine|ane|ene|yne|acid|"
                      r"amine|amide|dione|oate|nitrile|ether|oxy|phen|benz|"
                      r"methyl|ethyl)", re.IGNORECASE)

_HRMS_RE = re.compile(r"HRMS[^.\n]{0,200}", re.IGNORECASE)
_MP_RE = re.compile(r"\b[mM]\.?\s?p\.?\s*[:=]?\s*([\d]{1,3}\s*-?\s*[\d]{0,3}\s*[°]?\s?C)")


def _parse_ir_bands(ir_str: str) -> list[float]:
    """Pull wavenumbers (cm^-1) from an IR band string."""
    # numbers in the plausible IR window 400-4000, ignore intensities like (s)/(w)
    nums = re.findall(r"\b(\d{3,4})(?:\.\d+)?\b", ir_str)
    bands = [float(n) for n in nums if 400 <= float(n) <= 4000]
    return bands


def extract_records(raw_text: str) -> list[CompoundRecord]:
    """
    Extract all per-compound spectroscopy records from a block of experimental
    text. Compounds are segmented on the ``1H NMR`` (or ``13C NMR``) anchor:
    each NMR data block belongs to exactly one compound, and we attach the IR,
    HRMS, yield and appearance found in its immediate neighbourhood.
    """
    text = normalize_text(raw_text)
    records: list[CompoundRecord] = []

    # Build a flat list of NMR blocks, then cluster them into compounds.
    blocks = []
    for m in _NMR_RE.finditer(text):
        # require an actual shift list to follow, else it's prose ("1H NMR spectra")
        tail = text[m.end():m.end() + 6]
        if not re.match(r"\s*-?\d", tail):
            continue
        nuc_tok = (m.group("nucA") or m.group("nucB") or "").upper().replace(" ", "")
        nuc = "1H" if (nuc_tok.startswith("1H") or nuc_tok == "δH".upper()
                       or nuc_tok.endswith("H")) else "13C"
        meta = (m.group("metaA") or m.group("metaB") or "").strip()
        payload = _capture_payload(text, m.end())
        # Drop SI page markers ("S17", "S4") that PDF extraction inlines into the
        # data, otherwise their digits are misread as chemical shifts.
        payload = re.sub(r"\bS\s?\d{1,4}\b", " ", payload)
        payload = _truncate_nmr_payload(payload)
        blocks.append({"nuc": nuc, "start": m.start(), "anchor_end": m.end(),
                       "meta": meta, "payload": payload})

    # Cluster blocks into compounds. Order-agnostic: a new compound starts when
    # we encounter a nucleus already present in the current cluster (e.g. a 2nd
    # 1H NMR) or when there is a large positional gap. This handles both the
    # common "1H then 13C" ordering and the reverse.
    clusters: list[list[dict]] = []
    for b in blocks:
        if not clusters:
            clusters.append([b])
            continue
        last = clusters[-1]
        nucs_in_last = {x["nuc"] for x in last}
        gap = b["start"] - last[-1]["start"]
        if b["nuc"] in nucs_in_last or gap > 2500:
            clusters.append([b])
        else:
            last.append(b)

    for cl in clusters:
        rec = CompoundRecord()
        cl_start = cl[0]["start"]
        cl_end = max(b["start"] + len(b["payload"]) for b in cl)
        for b in cl:
            if b["nuc"] == "1H":
                rec.h_nmr = b["payload"]
                rec.h_nmr_meta = b["meta"] or None
                rec.h_peaks = parse_h_peaks(b["payload"])
            else:
                rec.c_nmr = b["payload"]
                rec.c_nmr_meta = b["meta"] or None
                rec.c_peaks = parse_c_peaks(b["payload"])

        # Look-behind window for header / appearance / yield (preceding ~400 chars).
        pre = text[max(0, cl_start - 400):cl_start]

        # Compound name + label: take the header closest to the NMR block.
        hdr = None
        for hdr in _HEADER_RE.finditer(pre):
            pass
        if hdr:
            name = re.sub(r"\s+", " ", hdr.group("name")).strip(" -,;:")
            # Strip SI page markers ("S10 ", "2907 ") and section numbers ("3.2.1.").
            name = re.sub(r"^(?:S\s?\d{1,4}\b|\d{1,3}(?:\.\d{1,3})*\.?)[\s.]+", "", name).strip()
            # Strip narrative prefixes so OPSIN sees just the chemical name.
            name = re.sub(r"^(?:synthesis|preparation|general\s+procedure(?:\s+for)?|"
                          r"typical\s+procedure|compound|data(?:\s+for)?|example|procedure|"
                          r"title\s+compound|characterization(?:\s+of\s+products?)?|"
                          r"experimental\s+details(?:\s+for(?:\s+the\s+preparation\s+of)?)?)"
                          r"\b\s*(?:of\s+|for\s+|:\s*)?",
                          "", name, flags=re.IGNORECASE).strip()
            name = re.sub(r"\(\s+", "(", name).replace(" )", ")")
            rec.label = hdr.group("label")
            if _NAMEISH.search(name) and 5 <= len(name) <= 200:
                rec.name = name

        am = None
        for am in _APPEAR_RE.finditer(pre):
            pass  # take the last appearance before the NMR
        if am:
            rec.appearance = am.group(1).strip()
        ym = None
        for ym in _YIELD_RE.finditer(pre):
            pass
        if ym:
            try:
                rec.yield_pct = float(ym.group(1))
            except ValueError:
                pass

        # Look-ahead window for IR / HRMS / mp (following ~900 chars).
        post = text[cl_end:cl_end + 1100]
        whole = pre + text[cl_start:cl_end] + post
        irm = _IR_RE.search(whole)
        if irm:
            ir_payload = _capture_payload(whole, irm.end())
            # only accept if it actually contains cm-region numbers
            bands = _parse_ir_bands(ir_payload)
            if bands:
                rec.ir = ir_payload[:400].strip(" ,.;:")
                rec.ir_bands = bands
        hm = _HRMS_RE.search(whole)
        if hm:
            rec.hrms = hm.group(0).strip()
        mm = _MP_RE.search(whole)
        if mm:
            rec.mp = mm.group(1).strip()

        if rec.has_nmr:
            records.append(rec)

    return records
