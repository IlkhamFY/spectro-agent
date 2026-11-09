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
  {"benchmark_expand:R26": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R26
Molecular formula: C14H19NO5
IR bands (cm-1): [3088.0, 2977.0, 2934.0, 2892.0, 1703.0, 1615.0, 1580.0, 1535.0, 1467.0, 1438.0, 1378.0, 1351.0, 1320.0, 1269.0, 1180.0, 1122.0, 1099.0, 1034.0]
1H NMR: 9.01 (s, 1H), 8.48-8.31 (m, 2H), 7.56 (t, J = 7.2 Hz, 1H), 5.07 (s, 1H), 3.94-3.85 (m, 2H), 1.22 (d, J = 6.0 Hz, 6H) 1.07 (d, J = 6.0 Hz, 6H) ppm; 13C{1H}NMR (100 MHz, CDCl3): δ 192.7, 148.0, 136.1, 134.4, 129.2, 127.3, 125.5, 102.2, 71.0, 22.9, 22.2 ppm
13C NMR: δ 192.7 (1C, s), 148.0 (1C, s), 136.1 (1C, s), 134.4 (1C, s), 129.2 (1C, s), 127.3 (1C, s), 125.5 (1C, s), 102.2 (1C, s), 71.0 (1C, s), 22.9 (1C, s)

### benchmark_expand:R28
Molecular formula: C14H12IN3O2
IR bands (cm-1): [3451.0, 3247.0, 3071.0, 2884.0, 1663.0, 1548.0, 649.0]
1H NMR: 12.07 (s, 1H), 11.41 (s, 1H), 8.65 (d, J = 4.5 Hz, 2H), 8.21 (d, J = 1.5 Hz, 1H), 7.78 (d, J = 5.0 Hz, 2H), 7.74-7.69 (m, 1H), 6.88 (d, J = 8.5 Hz, 1H), 2.33 (s, 3H)
13C NMR: δ 161.2 (1C, s), 156.8 (1C, s), 150.5 (1C, s), 145.3 (1C, s), 142.1 (1C, s), 139.1 (1C, s), 137.5 (1C, s), 121.0 (1C, s), 120.2 (1C, s), 82.2 (1C, s), 13.8 (1C, s)

### benchmark_expand:R29
Molecular formula: C13H26O
IR bands (cm-1): [3471.0, 2957.0, 2934.0, 1606.0, 1456.0, 1252.0, 1045.0, 773.0]
1H NMR: 5.10 (t, J = 7.1 Hz, 1H), 3.63 (t, J = 6.7 Hz, 2H), 2.07-1.89 (m, 2H), 1.68 (s, 3H), 1.60 (s, 3H), 1.59-1.52 (m, 2H), 1.44-1.24 (m, 8H), 1.18-1.08 (m, 2H), 0.86 (d, J = 6.6 Hz, 3H)
13C NMR: δ 131.0 (1C, s), 125.0 (1C, s), 63.0 (1C, s), 37.1 (1C, s), 36.9 (1C, s), 32.8 (1C, s), 32.4 (1C, s), 26.8 (1C, s), 26.1 (1C, s), 25.7 (1C, s), 25.6 (1C, s), 19.6 (1C, s), 17.6 (1C, s)

### benchmark_expand:R31
Molecular formula: C17H34O2Si
IR bands (cm-1): [3369.0, 2955.0, 2928.0, 2856.0, 1463.0, 1252.0, 1049.0, 1005.0]
1H NMR: 5.87-5.74 (1H, m), 5.47 (1H, ddd, J = 11.4, 8.3, 1.0 Hz), 5.36 (1H, ddd, J = 11.4, 8.3, 0.9 Hz), 5.18-5.10 (2H, m), 4.50-4.35 (2H, m), 2.34-2.18 (2H, m), 1.93 (1H, br s), 1.59-1.48 (1H, m), 1.44-1.19 (5H, m), 0.91-0.87 (12H, m), 0.07 (3H, s), 0.05 (3H, s)
13C NMR: δ 135.6 (1C, s), 134.1 (1C, s), 130.5 (1C, s), 118.2 (1C, s), 69.0 (1C, s), 67.1 (1C, s), 42.2 (1C, s), 38.2 (1C, s), 27.5 (1C, s), 25.8 (1C, s), 22.6 (1C, s), 18.2 (1C, s), 14.0 (1C, s), -4.3 (1C, s), -4.8 (1C, s)

### benchmark_expand:R36
Molecular formula: C13H18O3
IR bands (cm-1): [711.0, 748.0, 1029.0, 1278.0, 1398.0, 1451.0, 1495.0, 1601.0, 2876.0, 2935.0]
1H NMR: 1.27 (d, 3H, CH3-), 1.32 (d, 3H, CH3-), 2.03-2.05 (acetone-d6), 2.81 (s, H2O), 3.48 (dd, 1H, J = 5.2, 9.8 Hz, -CH2-OBn), 3.55 (dd, 1H, J = 5.3, 9.8 Hz, -CH2-OBn), 3.71 (dd, 1H, J = 6.3, 8.2 Hz, O-CH2-Ar), 4.03 (dd, 1H, J = 6.4, 8.2 Hz, O-CH2-Ar), 4.24 (m, 1H, H-4), 4.55 (s, 2H, -OCH2Ar), 7.26-7.35 (m, 5H, Ar-H)
13C NMR: δ 25.7 (1C, s), 27.1 (1C, s), 67.4 (1C, s), 72.0 (1C, s), 73.7 (1C, s), 75.6 (1C, s), 109.5 (1C, s), 128.2 (1C, s), 128.3 (1C, s), 129.0 (1C, s), 139.6 (1C, s)

### benchmark_expand:R37
Molecular formula: C11H14N2O3
IR bands (cm-1): [2670.0, 3320.0, 1718.0, 1590.0]
1H NMR: 1.96 (s, 3H, CH3), 2.47 (t, J = 6.9 Hz, 2H, CH2CO), 3.20 (t, J = 8.7 Hz, 2H, NHCH2), 3.77 (s, 1H, NHCH2), 6.50 (d, J = 8.7 Hz, 2H, HAr), 7.27 (d, J = 8.7 Hz, 2H, HAr), 9.51 (s, 1H, NHCO), 11.81 (br s, 1H, COOH)
13C NMR: δ 23.72 (1C, s), 33.83 (1C, s), 39.21 (1C, s), 112.04 (1C, s), 120.91 (1C, s), 128.81 (1C, s), 144.75 (1C, s), 167.28 (1C, s), 173.31 (1C, s)
