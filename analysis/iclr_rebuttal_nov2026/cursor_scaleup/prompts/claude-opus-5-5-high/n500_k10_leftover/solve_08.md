# Blind structure-elucidation task

You are given real experimental spectra for organic molecules. For EACH compound
you are given the molecular formula, the IR band list, and the printed 1H and 13C
NMR lists. No name, SMILES, InChI, or other hint is given.

For each compound, propose up to 10 distinct constitutions, best first, as SMILES.

Rules:
  - Use only the spectra in this file. Do not open any other file, do not search
    the web, and do not look up a name, a structure, or an identifier.
  - Do not enumerate isomers with a database or a structure generator. You may
    use RDKit only to check that a SMILES you already wrote parses and has this
    molecular formula.
  - Every candidate must match the given molecular formula exactly.
  - Order candidates by your own confidence, most likely first.
  - If you cannot honestly propose 10 different constitutions, return fewer.
    Do not pad with duplicates or with structures that break the formula.
  - If you know more distinct formula-matching constitutions than 10, stop at 10
    unless you would have written them anyway. Do not invent fillers.

Return ONLY a JSON object mapping each id to a list of SMILES strings, e.g.:
  {"benchmark_expand:R74": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R74
Molecular formula: C17H18ClNO5
IR bands (cm-1): [2985.0, 2355.0, 1737.0, 1580.0, 1318.0, 1241.0, 1161.0, 1065.0, 1026.0, 947.0, 844.0, 679.0, 597.0]
1H NMR: 7.51 (d, J = 8.8 Hz, 2H), 7.40 (d, J = 8.4 Hz, 2H), 4.83 (s, 1H), 4.27-4.21 (m, 4H), 2.52 (s, 3H), 1.25 (t, J = 7.2 Hz, 6H) ppm. 13C{1H}NMR (100 MHz, CDCl3) δ 166.8, 160.5, 147.3, 134.7, 129.1, 128.2, 127.6, 126.4, 62.2, 50.8, 14.0, 13.9 ppm
13C NMR: δ 166.8 (1C, s), 160.5 (1C, s), 147.3 (1C, s), 134.7 (1C, s), 129.1 (1C, s), 128.2 (1C, s), 127.6 (1C, s), 126.4 (1C, s), 62.2 (1C, s), 50.8 (1C, s), 14.0 (1C, s)

### benchmark_expand:R76
Molecular formula: C33H26Br2N4O10
IR bands (cm-1): [3174.0, 3067.0, 1653.0, 1530.0]
1H NMR: 11.23 (s, 2H, OH), 8.74 (s, 1H, NH), 8.32 (d, J=7.23Hz, 2H, Ph), 7.62 (2H, s, Ph), 7.72 (d, J=7.41Hz, 2H, Ph), 7.45 (d, J=7.20Hz, 2H, Ph), 7.17 (d, J=7.40Hz, 2H, Ph), 7.15 (s, 2H,), 4.62(s, 1H, CH), 4.12 (s, 4H, CH2-Br), 2.43 (s, 6H)
13C NMR: δ 191.4 (1C, s), 175.3 (1C, s), 167.2 (1C, s), 144.2 (1C, s), 127.4 (1C, s), 126.1 (1C, s), 123.1 (1C, s), 164.3 (1C, s), 134.1 (1C, s), 129.2 (1C, s), 128.4 (1C, s), 119.1 (1C, s), 118.2 (1C, s), 147.2 (1C, s), 102.1 (1C, s), 41.2 (1C, s), 31.2 (1C, s)

### benchmark_expand:R77
Molecular formula: C17H15N5O2S
IR bands (cm-1): [3044.0, 2946.0, 2359.0, 1636.0, 1264.0, 960.0, 853.0]
1H NMR: 8.14-8.28 (m, 5H, ArH), 7.24-7.39 (m, 4H, ArH), 8.44 (s, H, NCH), 6.12 (d, J = 6.8 Hz, H, CH), 5.25 (d, J = 6.8 Hz, H, CH), 3.31 (s, 2H, CH2)1.58 (s, H, SH)
13C NMR: δ 116.15 (1C, s), 120.24 (1C, s), 122.31 (1C, s), 124.01 (1C, s), 124.27 (1C, s), 126.14 (1C, s), 128.01 (1C, s), 130.29 (1C, s), 132.57 (1C, s), 134.92 (1C, s), 136.49 (1C, s), 136.48 (1C, s), 74.15 (1C, s), 119.87 (1C, s), 136.87 (1C, s), 144.68 (1C, s), 161.10 (1C, s)

### benchmark_expand:R79
Molecular formula: C25H18ClNO2
IR bands (cm-1): [3054.0, 2946.0, 1695.0, 1659.0, 1640.0, 1568.0, 1491.0, 1403.0, 1096.0, 753.0, 707.0]
1H NMR: 7.97 (dd, J = 7.9, 1.4 Hz, 1H), 7.70-7.63 (m, 1H), 7.62-7.55 (m, 2H), 7.44-7.30 (m, 8H), 7.30-7.23 (m, 1H), 5.59 (d, J = 2.2 Hz, 1H), 5.34 (d, J = 2.2 Hz, 1H), 3.65 (s, 3H)
13C NMR: δ 160.15 (1C, s), 159.50 (1C, s), 159.22 (1C, s), 140.92 (1C, s), 140.39 (1C, s), 132.96 (1C, s), 132.04 (1C, s), 131.65 (1C, s), 129.50 (1C, s), 128.80 (1C, s), 128.56 (1C, s), 128.00 (1C, s), 127.45 (1C, s), 123.07 (1C, s), 122.05 (1C, s), 114.79 (1C, s), 111.77 (1C, s), 111.26 (1C, s), 105.22 (1C, s), 51.27 (1C, s), 29.08 (1C, s)

### benchmark_expand:R80
Molecular formula: C24H16N2O
IR bands (cm-1): [3135.0, 2953.0, 2149.0, 852.0]
1H NMR: 1.68 (s, 6 H,), 3.59 (s, 2 H), 3.64 (s, 1 H), 3.72 (s, 1 H), 7.77-7.80 (m, 2 H), 7.87 (d, J = 8 Hz, 1 H), 7.94 (d, J = 8 Hz, 1 H), 8.06-8.08 (m, 1 H), 9.41-9.44 (m, 1 H)
13C NMR: δ 29.9 (1C, s), 41.4 (1C, s), 80.9 (1C, s), 84.8 (1C, s), 85.0 (1C, s), 90.8 (1C, s), 113.2 (1C, s), 122.4 (1C, s), 122.6 (1C, s), 123.8 (1C, s), 125.4 (1C, s), 126.7 (1C, s), 128.5 (1C, s), 130.3 (1C, s), 131.8 (1C, s), 131.9 (1C, s), 134.0 (1C, s), 139.7 (1C, s), 141.7 (1C, s), 142.8 (1C, s)

### benchmark_expand:R86
Molecular formula: C13H10O3
IR bands (cm-1): [3304.0, 3069.0, 2924.0, 1764.0, 1721.0, 1619.0, 1262.0]
1H NMR: 7.52 (d, J = 9.5 Hz, 1H, H-5), 7.00-6.80 (m, 2H, H-6,8), 6.15 (s, 1H, H-3), 4.76 (d, J = 2.5 Hz, 2H, H-1’), 2.59 (t, J = 2.5 Hz, 1H, H3’), 2.40 (s, 3H, H-11)
13C NMR: δ 161.1 (1C, s), 160.4 (1C, s), 155.0 (1C, s), 152.5 (1C, s), 125.7 (1C, s), 114.3 (1C, s), 112.7 (1C, s), 112.4 (1C, s), 102.2 (1C, s), 77.5 (1C, s), 76.5 (1C, s), 56.2 (1C, s), 18.7 (1C, s)
