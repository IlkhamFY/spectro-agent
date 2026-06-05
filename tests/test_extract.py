"""
Unit tests for the extraction + normalisation engine.

These use *golden strings* drawn from the real reporting conventions seen across
Beilstein / ChemRxiv / RSC papers -- including the Spectro paper's own example
-- so the parser's behaviour is pinned without needing the network.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spectro_scraper.extract import (  # noqa: E402
    extract_records, parse_h_peaks, parse_c_peaks, normalize_text,
)
from spectro_scraper.normalize import to_spectro_h, to_spectro_c  # noqa: E402


# Standard ACS/RSC format: "1H NMR (...) δ ... 13C NMR (...) δ ... IR ..."
ACS = (
    "4-phenylbutan-2-one (3a). Colorless oil (85% yield). "
    "1H NMR (400 MHz, CDCl3) δ 7.85 (d, J = 8.0 Hz, 2H), 7.29-7.51 (m, 5H), "
    "2.96 (t, J = 7.5 Hz, 2H), 2.13 (s, 3H). "
    "13C NMR (101 MHz, CDCl3) δ 208.1, 141.2, 128.5, 126.1, 45.3, 30.1. "
    "IR (neat) ν 3024, 1715, 1602, 1452 cm-1. "
    "HRMS (ESI) calcd for C10H12O 148.0888."
)

# Bruker δH / δC notation with '=' and assignment labels, IR before NMR.
BRUKER = (
    "Mp = 263 C; IR (ATR): 3295, 2922, 1715, 1670, 1599 cm-1; "
    "δH(400 MHz, DMSO-d6): 9.10 (s, 1H, NH), 7.78 (ddd, J = 7.8, 1.4 Hz, 1H, 6-H), "
    "7.54-7.49 (m, 5H, H arom). "
    "δC(101 MHz, DMSO-d6): 165.2, 143.1, 128.7, 122.4."
)

# The Spectro paper's own canonical example (13C before 1H, count-first format).
SPECTRO = (
    "13C NMR (101 MHz, CDCl3) δ 73.9, 94.8, 126.5, 127.8, 128.4, 134.6. "
    "1H NMR (400 MHz, CDCl3) δ 5.47 (s, 1H), 7.29-7.51 (m, 5H)."
)


def test_acs_single_compound():
    recs = extract_records(ACS)
    assert len(recs) == 1
    r = recs[0]
    assert r.h_nmr and r.c_nmr and r.ir
    assert r.has_paired
    assert len(r.h_peaks) == 4
    assert len(r.c_peaks) == 6
    assert 1715.0 in r.ir_bands and 3024.0 in r.ir_bands


def test_h_peak_parsing():
    peaks = parse_h_peaks("7.85 (d, J = 8.0 Hz, 2H), 2.13 (s, 3H)")
    assert peaks[0].shift == "7.85"
    assert peaks[0].multiplicity == "d"
    assert peaks[0].nuclei == 2
    assert peaks[0].j == [8.0]
    assert peaks[1].nuclei == 3 and peaks[1].multiplicity == "s"


def test_c_peak_parsing():
    peaks = parse_c_peaks("208.1, 141.2, 128.7 (q, J = 282.0 Hz)")
    assert [p.shift for p in peaks] == ["208.1", "141.2", "128.7"]
    assert peaks[2].multiplicity == "q"
    assert peaks[2].j == [282.0]


def test_bruker_delta_notation():
    recs = extract_records(BRUKER)
    assert len(recs) == 1
    r = recs[0]
    assert r.h_nmr and r.c_nmr, "δH/δC notation must be recognised"
    assert r.has_ir and 1715.0 in r.ir_bands
    assert r.mp is not None


def test_spectro_example_single_record():
    recs = extract_records(SPECTRO)
    # 13C-then-1H ordering must still collapse to ONE compound
    assert len(recs) == 1
    r = recs[0]
    assert r.h_nmr and r.c_nmr


def test_spectro_format_ordering():
    recs = extract_records(ACS)
    sh = to_spectro_h(recs[0])
    sc = to_spectro_c(recs[0])
    # integration-first, Spectro-style: "7.85 (2H, d)"
    assert "(2H, d)" in sh
    assert "(3H, s)" in sh
    assert sc.startswith("δ ") and "(1C, s)" in sc


def test_two_compounds_segmented():
    text = ACS + " Next compound. " + ACS.replace("3a", "3b")
    recs = extract_records(text)
    assert len(recs) == 2


def test_normalize_dehyphenation():
    assert "crosscoupling" in normalize_text("cross-\ncoupling reaction")


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} tests passed")
    sys.exit(0 if passed == len(fns) else 1)
