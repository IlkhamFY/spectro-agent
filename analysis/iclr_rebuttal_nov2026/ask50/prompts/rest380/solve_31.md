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
  {"benchmark_main:R130": ["CCO", "COC"]}

Compounds:

### benchmark_main:R130
Molecular formula: C11H6ClN3O2
IR bands (cm-1): [3448.0, 3246.0, 3204.0, 1657.0, 1628.0, 1583.0, 1542.0, 1501.0, 1448.0]
1H NMR: 9.10 (d, J = 6.7 Hz, 1H, H-1), 8.65 (br.s, 1H, exchange with D2O, NH), 8.15 (br.s, 1H, exchange with D2O, NH), 7.95 (d, J = 9.0 Hz, 1H, H-4), 7.78 (m, 1H, H-3), 7.43 (t, J = 6.9 Hz, 1H, H-2)
13C NMR: δ 171.9 (1C, s), 168.6 (1C, s), 148.9 (1C, s), 148.5 (1C, s), 147.3 (1C, s), 132.1 (1C, s), 128.6 (1C, s), 119.2 (1C, s), 118.6 (1C, s), 118.3 (1C, s), 114.9 (1C, s)

### benchmark_main:R132
Molecular formula: C28H27NO2Si
IR bands (cm-1): [3058.0, 2952.0, 1643.0, 1618.0, 1591.0, 1492.0, 1384.0, 1126.0, 992.0, 751.0, 696.0]
1H NMR: 8.14 (d, J = 8.0 Hz, 1H), 7.50-7.40 (m, 5H), 7.33-7.26 (m, 4H), 7.26-7.17 (m, 4H), 6.29 (s, 1H), 3.58 (s, 3H), 0.32 (s, 9H)
13C NMR: δ 161.44 (1C, s), 153.77 (1C, s), 144.05 (1C, s), 139.26 (1C, s), 135.00 (1C, s), 133.29 (1C, s), 130.76 (1C, s), 128.14 (1C, s), 127.65 (1C, s), 126.78 (1C, s), 123.25 (1C, s), 121.73 (1C, s), 116.08 (1C, s), 113.74 (1C, s), 111.17 (1C, s), 82.88 (1C, s), 29.36 (1C, s), 0.52 (1C, s)

### benchmark_main:R133
Molecular formula: C23H17NO6
IR bands (cm-1): [3300.0, 2900.0, 3300.0, 1728.0, 1661.0, 1610.0, 1544.0, 1497.0, 1466.0, 1446.0, 1232.0, 854.0, 754.0, 722.0, 694.0, 669.0, 650.0]
1H NMR: 8.94 (1H, d, J = 7.4 Hz, N-H), 8.17 (1H, dd, J = 7.9 and 1.6 Hz, H-8), 8.10 (1H, d, J = 9.2 Hz, H-1), 7.85 (1H, ddd, J = 8.6, 7.0 and 1.6 Hz, H-6), 7.63 (1H, dd, J = 8.4 and 1.0Hz, H-5), 7.47 (1H, ddd, J = 7.9, 7.0 and 1.0 Hz, H-7), 7.43 (2H, m, H-5′), 7.38 (2H, m, H-4′), 7.30 (1H, m, H-6′), 7.11 (1H, dd, J = 9.2 and 2.4 Hz, H-2), 7.10 (1H, d, J = 2.4 Hz, H-4), 5.41 (1H, d, J = 7.5 Hz, H-2′), 4.88 (1H, d, J = 14.8 Hz, OCH2) and 4.84 (1H, d, J = 14.8 Hz, OCH2) ppm
13C NMR: δ 174.9 (1C, s), 171.5 (1C, s), 166.7 (1C, s), 163.5 (1C, s), 157.3 (1C, s), 155.6 (1C, s), 136.9 (1C, s), 135.1 (1C, s), 128.6 (1C, s), 128.1 (1C, s), 127.6 (1C, s), 125.9 (1C, s), 124.4 (1C, s), 121.2 (1C, s), 117.9 (1C, s), 115.3 (1C, s), 114.0 (1C, s), 101.5 (1C, s), 66.8 (1C, s)

### benchmark_main:R134
Molecular formula: C18H16N2O6Se2
IR bands (cm-1): [3255.0, 2951.0, 1681.0, 1573.0]
1H NMR: 10.42(s, 2H,2NH), 8.39(s, 2H,2CHO), 8.36-8.12(s, 2H, Ar-H), 7.92(d, 2H, Ar-H), 7.60(d, J = 6.2 Hz, 2H, Ar-H), 3.75(s, 6H, 2OCH3)
13C NMR: δ 166 (1C, s), 161 (1C, s), 139 (1C, s), 138 (1C, s), 135 (1C, s), 124 (1C, s), 122 (1C, s), 118 (1C, s), 53 (1C, s)

### benchmark_main:R135
Molecular formula: C24H25ClN6O3
IR bands (cm-1): [3065.0, 2966.0, 1686.0, 1570.0, 1247.0, 1024.0, 836.0]
1H NMR: 3.17 (4H; t; CH2N; b + b’), 3.38 (4H; t; CH2N; a + a’), 3.80 (3H; s; OCH3), 5.04 (2H; s; CH2CO), 6.91 (1H; d; J = 4.1 Hz, pyridazinone H5), 6.92-7.96 (9H; m; phenyl protons and pyridazinone H4), 8.16 (1H; s; -N=CH-), 11.52 (1H; s; -NH-N)
13C NMR: δ 46.5 (1C, s), 49.1 (1C, s), 52.9 (1C, s), 55.8 (1C, s), 114.8 (1C, s), 115.9 (1C, s), 118.1 (1C, s), 127.0 (1C, s), 128.9 (1C, s), 129.2 (1C, s), 131.0 (1C, s), 144.1 (1C, s), 147.3 (1C, s), 148.2 (1C, s), 149.1 (1C, s), 155.9 (1C, s), 158.2 (1C, s), 163.5 (1C, s)

### benchmark_main:R15
Molecular formula: C19H17BrO3
IR bands (cm-1): [2921.0, 1698.0, 1607.0, 1485.0, 1408.0, 1360.0, 1284.0, 1229.0, 1182.0, 1131.0, 972.0, 810.0]
1H NMR: 7.91-7.82 (m, 3H, Ar + CHCHCO), 7.67 (d, J = 2.5 Hz, 1H, Ar), 7.39 (dd, J = 9.0, 2.5 Hz, 1H, Ar), 7.31 (d, J = 8.0 Hz, 2H, Ar), 6.79 (d, J = 16.5 Hz, 1H, CHCHCO), 6.68 (d, J = 9.0 Hz, 1H, Ar), 5.35 (s, 2H, OCH 2), 2.44 (s, 3H, COCH3), 2.36 (s, 3H, CCH 3)
13C NMR: δ 198.8 (1C, s), 193.0 (1C, s), 155.9 (1C, s), 145.4 (1C, s), 136.9 (1C, s), 134.0 (1C, s), 131.9 (1C, s), 131.3 (1C, s), 129.8 (1C, s), 129.2 (1C, s), 128.2 (1C, s), 126.2 (1C, s), 114.3 (1C, s), 114.3 (1C, s), 71.2 (1C, s), 27.5 (1C, s), 21.9 (1C, s)
