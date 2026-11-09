# Blind structure-elucidation task

You are given real experimental spectra for organic molecules. For EACH compound
you are given the molecular formula, the IR band list, and the printed 1H and 13C
NMR lists. No name, SMILES, InChI, or other hint is given.

For each compound, propose up to 50 distinct constitutions, best first, as SMILES.

Rules:
  - Use only the spectra in this file. Do not open any other file, do not search
    the web, and do not look up a name, a structure, or an identifier.
  - Do not enumerate isomers with a database or a structure generator. You may
    use RDKit only to check that a SMILES you already wrote parses and has this
    molecular formula.
  - Every candidate must match the given molecular formula exactly.
  - Order candidates by your own confidence, most likely first.
  - If you cannot honestly propose 50 different constitutions, return fewer.
    Do not pad with duplicates or with structures that break the formula.
  - If you know more distinct formula-matching constitutions than 50, stop at 50
    unless you would have written them anyway. Do not invent fillers.

Return ONLY a JSON object mapping each id to a list of SMILES strings, e.g.:
  {"benchmark_main:R122": ["CCO", "COC"]}

Compounds:

### benchmark_main:R122
Molecular formula: C24H20N4O2
IR bands (cm-1): [3356.0, 3238.0, 3006.0, 2937.0, 1690.0, 1620.0, 1546.0, 1493.0, 1466.0, 1324.0, 1254.0, 1135.0, 1086.0]
1H NMR: 1.81-1.93 (m, 2H, aliphatic CH2), 2.06-2.17 (m, 2H, aliphatic CH2), 2.69 (d, J = 4.3 Hz, 2H, aliphatic CH2), 3.77 (s, 3H, N-CH3), 6.45 (d, J = 7.5 Hz, 1H, Ar H), 6.53 (d, J = 7.3 Hz, 2H, Ar H), 6.80 (t, J = 7.2 Hz, 1H, Ar H), 6.88 (d, J = 7.0 Hz, 1H, Ar H), 6.98-7.08 (m, 3H, Ar H), 7.18 (t, J = 7.2 Hz, 1H, Ar H), 9.70 (s, 1H, NH), 10.04 (s, 1H, NH) ppm
13C NMR: δ 21.01 (1C, s), 27.72 (1C, s), 35.06 (1C, s), 37.12 (1C, s), 50.12 (1C, s), 99.81 (1C, s), 108.52 (1C, s), 108.92 (1C, s), 120.90 (1C, s), 123.03 (1C, s), 127.01 (1C, s), 127.06 (1C, s), 127.28 (1C, s), 128.39 (1C, s), 129.12 (1C, s), 132.50 (1C, s), 133.39 (1C, s), 137.23 (1C, s), 138.55 (1C, s), 142.30 (1C, s), 147.02 (1C, s), 153.88 (1C, s), 179.66 (1C, s)

### benchmark_main:R123
Molecular formula: C25H15Cl2NO
IR bands (cm-1): [3279.0, 3060.0, 2923.0, 1620.0, 1595.0]
1H NMR: 11.61 (s, 1H), 9.68 (d, J = 5.0 Hz, 1H), 7.75 (d, J = 7.2 Hz, 2H), 7.62 (s, 1H), 7.57-7.43 (m, 3H), 7.39-7.22 (m, 4H), 7.09 (d, J = 0.8 Hz, 1H), 6.51 (d, J = 1.0 Hz, 1H), 6.10 (d, J = 1.0 Hz, 1H)
13C NMR: δ 179.2 (1C, s), 153.3 (1C, s), 143.7 (1C, s), 143.5 (1C, s), 143.4 (1C, s), 143.4 (1C, s), 141.9 (1C, s), 139.3 (1C, s), 138.7 (1C, s), 129.2 (1C, s), 128.7 (1C, s), 128.4 (1C, s), 127.2 (1C, s), 127.1 (1C, s), 126.2 (1C, s), 123.8 (1C, s), 117.4 (1C, s), 113.7 (1C, s), 106.0 (1C, s), 99.9 (1C, s), 98.9 (1C, s)

### benchmark_main:R124
Molecular formula: C45H46N4O4S2
IR bands (cm-1): [3059.0, 2927.0, 1587.0, 1282.0, 1082.0, 815.0, 769.0, 669.0]
1H NMR: 7.96 (d, J = 8 Hz, 4H), 7.67 (s, 2H), 7.66-7.45 (m, 2H), 7.37-7.28 (m, 7H), 6.71 (s, 1H), 6.62 (d, J = 8.8 Hz, 3H), 6.45 (d, J = 8.4 Hz, 2H), 4.48-4.45 (m, 2H), 3.75 (s, 6H), 2.93-2.87 (m, 2H), 2.72 (s, 3H), 2.48 (6H), 2.10-2.02 (m, 2H)
13C NMR: δ 157.9 (1C, s), 144.0 (1C, s), 140.2 (1C, s), 136.1 (1C, s), 134.5 (1C, s), 132.7 (1C, s), 130.3 (1C, s), 129.7 (1C, s), 129.6 (1C, s), 129.0 (1C, s), 128.5 (1C, s), 127.3 (1C, s), 125.6 (1C, s), 125.0 (1C, s), 122.7 (1C, s), 113.3 (1C, s), 112.6 (1C, s), 111.7 (1C, s), 110.1 (1C, s), 55.3 (1C, s), 44.7 (1C, s), 35.6 (1C, s), 20.3 (1C, s)

### benchmark_main:R126
Molecular formula: C17H20N2O3S
IR bands (cm-1): [3384.0, 2979.0, 1633.0, 1531.0, 1452.0, 1332.0, 1259.0, 1213.0, 1157.0, 1089.0, 929.0, 829.0, 763.0, 624.0, 563.0, 441.0]
1H NMR: 1.21 (d, J = 6.6 Hz, 6H), 2.35 (s, 3H), 4.07-4.19 (m, 1H), 6.21 (d, J = 7.0 Hz, 1H), 7.03 (dd, J = 7.6 Hz, J = 7.6 Hz, 1H), 7.18 (d, J = 8.0 Hz, 2H), 7.36 (dd, J = 7.8 Hz, J = 7.8 Hz, 1H), 7.41 (d, J = 7.8 Hz, 1H), 7.62-7.67 (m, 3H), 10.97 (br s, 1H) ppm
13C NMR: δ 21.5 (1C, s), 22.4 (1C, s), 42.1 (1C, s), 121.4 (1C, s), 121.9 (1C, s), 123.6 (1C, s), 126.9 (1C, s), 127.1 (1C, s), 129.5 (1C, s), 132.3 (1C, s), 136.6 (1C, s), 138.7 (1C, s), 143.6 (1C, s)

### benchmark_main:R127
Molecular formula: C20H21N5O2S
IR bands (cm-1): [3403.0, 3325.0, 1693.0, 1678.0]
1H NMR: 2.00 (s, 6H, 2CH3), 2.70-2.94 (m, 2H, COCH2), 3.43-3.52 (m, 1H, CH), 3.96-4.20 (m, 2H, NCH2), 5.65 (s, 2H, 2CH), 6.96 (s, 1H, CH=C), 7.05 (s, 2H, NH2), 7.68 (d, J = 8.8 Hz, 2H, HAr), 7.80 d, J = 8.8 Hz, 2H, HAr), 10.91 (s, 1H, NH) ppm
13C NMR: δ 10.9 (1C, s), 11.0 (1C, s), 34.1 (1C, s), 35.7 (1C, s), 50.3 (1C, s), 100.9 (1C, s), 103.1 (1C, s), 119.3 (1C, s), 125.8 (1C, s), 126.7 (1C, s), 130.8 (1C, s), 138.1 (1C, s), 149.4 (1C, s), 168.2 (1C, s), 171.6 (1C, s)

### benchmark_main:R13
Molecular formula: C22H17ClN2
IR bands (cm-1): [3030.0, 2859.0, 1957.0, 1809.0, 1666.0, 1577.0, 1452.0, 1274.0, 1082.0, 1027.0]
1H NMR: 5.19 (s, 2H), 7.12 (d, J = 7.0 Hz, 2H), 7.21 (s, 1H), 7.31-7.37 (m, 5H), 7.41-7.42 (m, 3H), 7.58-7.60 (m, 2H), 7.75 (d, J = 8.5 Hz, 2H)
13C NMR: δ 50.6 (1C, s), 116.9 (1C, s), 126.2 (1C, s), 126.7 (1C, s), 128.1 (1C, s), 128.7 (1C, s), 128.7 (1C, s), 129.0 (1C, s), 129.1 (1C, s), 129.2 (1C, s), 130.3 (1C, s), 132.3 (1C, s), 132.6 (1C, s), 136.7 (1C, s), 140.5 (1C, s), 148.8 (1C, s)
