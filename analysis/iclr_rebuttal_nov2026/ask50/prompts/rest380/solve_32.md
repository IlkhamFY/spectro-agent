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
  {"benchmark_main:R16": ["CCO", "COC"]}

Compounds:

### benchmark_main:R16
Molecular formula: C25H19N5O3S
IR bands (cm-1): [3421.0, 3160.0, 1744.0, 1725.0, 1693.0]
1H NMR: 11.54 (s, 0.5H), 11.33 (s, 0.5H), 10.86 (s, 0.5H), 8.14 (s, 0.5H), 8.11 (d, 1H, J = 5.5 Hz), 7.75 (s, 1H), 7.57-7.46 (m, 2H), 7.41-7.28 (m, 6H), 7.08-7.03 (m, 1H), 6.93 (d, 1H, J = 5.5 Hz), 5.38 (s, 2H), 4.69 (s, 1H), 4.24 (s, 1H); MS: [m/z, 469]
13C NMR: δ 29.5 (1C, s), 47.5 (1C, s), 111.6 (1C, s), 115.6 (1C, s), 119.1 (1C, s), 122.1 (1C, s), 123.1 (1C, s), 126.3 (1C, s), 126.6 (1C, s), 127.1 (1C, s), 127.2 (1C, s), 127.9 (1C, s), 129.0 (1C, s), 135.3 (1C, s), 135.4 (1C, s), 136.0 (1C, s), 142.9 (1C, s), 147.1 (1C, s), 156.9 (1C, s), 161.2 (1C, s), 163.0 (1C, s)

### benchmark_main:R17
Molecular formula: C16H15N5O2S
IR bands (cm-1): [3317.0, 3178.0, 3072.0, 2931.0, 1697.0, 1627.0, 1559.0, 1496.0]
1H NMR: 12.36 (s, 1H), 8.25-8.23 (d, J = 7.2 Hz, 2H, arom.), 7.49-7.39 (m, 3H, arom. & NH2), 6.98 (s, 1H), 3.77 (s,3H, CH3), 2.13 (s, 3H, CH3)
13C NMR: δ 176.08 (1C, s), 170.11 (1C, s), 164.93 (1C, s), 156.80 (1C, s), 153.99 (1C, s), 139.05 (1C, s), 134.24 (1C, s), 131.78 (1C, s), 129.87 (1C, s), 128.74 (1C, s), 124.38 (1C, s), 87.85 (1C, s), 36.29 (1C, s)

### benchmark_main:R20
Molecular formula: C22H21NO5
IR bands (cm-1): [2195.0, 1797.0, 1761.0, 1727.0, 1644.0, 1278.0, 1158.0, 1103.0]
1H NMR: 8.28 (dd, 1H, J = 8.0, 1.6 Hz), 7.72 (dd, 2H, J = 7.8, 1.6 Hz), 7.63 (ddd, 1H, J = 8.0, 8.0, 1.6 Hz), 7.54-7.46 (m, 2H), 7.42 (dd, 2H, J = 7.8, 7.8 Hz), 7.24 (dd, 1H, J = 8.0, 1.6 Hz), 3.72 (s, 3H), 1.36 (s, 9H)
13C NMR: δ 176.1 (1C, s), 153.0 (1C, s), 150.5 (1C, s), 138.3 (1C, s), 133.9 (1C, s), 133.6 (1C, s), 133.4 (1C, s), 131.9 (1C, s), 130.8 (1C, s), 130.0 (1C, s), 128.5 (1C, s), 128.3 (1C, s), 119.9 (1C, s), 93.1 (1C, s), 87.8 (1C, s), 83.3 (1C, s), 53.7 (1C, s), 27.6 (1C, s)

### benchmark_main:R21
Molecular formula: C15H15NO2
IR bands (cm-1): [3447.0, 1651.0, 1555.0, 1524.0, 1490.0, 1358.0, 1292.0, 1213.0, 1065.0, 1014.0, 828.0, 783.0, 595.0]
1H NMR: 12.44 (br s, 1H), 8.43 (d, 1H, J = 5.32 Hz), 8.06 (d, 1H, J = 1.24 Hz), 7.60-7.54 (m, 2H), 3.70-3.64 (m, 1H), 3.33 (s, 1H), 2.76-2.71 (m, 2H), 1.23 (t, 3H, J = 7.56 Hz), 1.00-0.90 (m, 4H)
13C NMR: δ 199.6 (1C, s), 175.8 (1C, s), 143.9 (1C, s), 141.1 (1C, s), 137.6 (1C, s), 133.2 (1C, s), 128.4 (1C, s), 124.3 (1C, s), 119.3 (1C, s), 117.8 (1C, s), 28.3 (1C, s), 19.3 (1C, s), 15.9 (1C, s), 11.7 (1C, s)

### benchmark_main:R25
Molecular formula: C15H13Cl2N3O2S2
IR bands (cm-1): [3080.0, 2978.0, 1585.0, 1325.0, 1150.0]
1H NMR: 2.43 (s, 3H; -CH3), 3.32 (s, 3H; N-CH3), 4.94 (s, 2H; -CH2-), 7.28 (t, 1H; J = 7.5 Hz; Ar-H), 7.35 (d, 1H; J = 8.4 Hz; Ar-H), 7.60 (t, 1H; J = 7.8 Hz; Ar-H), 7.69 (s, 1H; Ar-H), 8.34 (d, 1H; J = 8.1 Hz; Ar-H) ppm
13C NMR: δ 17.8 (1C, s), 33.3 (1C, s), 50.2 (1C, s), 120.1 (1C, s), 122.6 (1C, s), 124.3 (1C, s), 125.6 (1C, s), 126.6 (1C, s), 128.6 (1C, s), 133.3 (1C, s), 136.5 (1C, s), 142.9 (1C, s), 143.0 (1C, s), 151.6 (1C, s)

### benchmark_main:R27
Molecular formula: C23H22Br2N2O3
IR bands (cm-1): [3012.0, 2948.0, 1681.0, 1618.0, 1508.0, 1460.0, 1268.0, 1130.0, 975.0, 841.0, 797.0]
1H NMR: 11.71 (s, 1H), 8.91 (d, J = 7.3 Hz, 2H), 8.20 (d, J = 6.9 Hz, 2H), 7.73 (d, J = 15.6 Hz, 1H), 7.67 (d, J = 8.4 Hz, 2H), 7.46 (d, J = 8.4 Hz, 2H), 7.32-7.25 (m, 2H), 7.06 (d, J = 8.9 Hz, 1H), 6.85 (d, J = 15.7 Hz, 1H), 5.69 (s, 2H), 3.82 (d, J = 3.7 Hz, 6H)
13C NMR: δ 166.17 (1C, s), 152.91 (1C, s), 151.83 (1C, s), 149.45 (1C, s), 145.66 (1C, s), 145.66 (1C, s), 144.87 (1C, s), 134.51 (1C, s), 132.57 (1C, s), 132.57 (1C, s), 131.32 (1C, s), 131.32 (1C, s), 127.18 (1C, s), 123.40 (1C, s), 123.05 (1C, s), 118.08 (1C, s), 115.62 (1C, s), 115.62 (1C, s), 112.28 (1C, s), 110.86 (1C, s), 61.18 (1C, s), 56.14 (1C, s), 55.98 (1C, s)
