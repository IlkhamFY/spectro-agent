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
  {"benchmark_expand_500:R200": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R200
Molecular formula: C20H25NO2
IR bands (cm-1): [3326.0, 1705.0, 1602.0, 1546.0, 1118.0]
1H NMR: 7.38-7.29 (m, 5H), 6.88 (s, 1H), 6.37 (s, 1H), 6.33 (s, 1H), 4.37 (d, J = 6.4 Hz, 2H), 3.87 (s, 3H), 2.67 (d, J = 6.8 Hz, 2H), 2.24 (s, 3H), 1.73-1.73 (m, 1H), 0.90 (d, J = 6.8 Hz, 6H) ppm
13C NMR: δ 170.7 (1C, s), 149.9 (1C, s), 143.8 (1C, s), 142.4 (1C, s), 139.3 (1C, s), 128.6 (1C, s), 127.3 (1C, s), 127.1 (1C, s), 121.2 (1C, s), 110.8 (1C, s), 110.1 (1C, s), 51.7 (1C, s), 47.7 (1C, s), 45.4 (1C, s), 30.5 (1C, s), 22.7 (1C, s)

### benchmark_expand_500:R205
Molecular formula: C16H12O3Se
IR bands (cm-1): [2959.0, 1643.0, 1581.0, 1552.0, 1462.0, 1245.0, 1022.0]
1H NMR: 8.22 (dd, JH-H = 8.3 Hz, JH-H = 1.6 Hz, 1H), 7.66-7.59 (m, 4H), 7.41-7.37 (m, 2H), 6.86 (d, JH-H = 8.8 Hz, 2H), 3.80 (s, 3H)
13C NMR: δ 175.3 (1C, s), 160.2 (1C, s), 156.3 (1C, s), 153.8 (1C, s), 137.1 (1C, s), 133.6 (1C, s), 126.1 (1C, s), 125.3 (1C, s), 122.8 (1C, s), 119.3 (1C, s), 118.0 (1C, s), 117.0 (1C, s), 115.3 (1C, s)

### benchmark_expand_500:R208
Molecular formula: C17H12O3
IR bands (cm-1): [1747.0, 1660.0, 1614.0, 1582.0, 1497.0, 1454.0, 1254.0, 1023.0, 733.0, 697.0]
1H NMR: 7.71 (dd, J = 7.6, 0.8 Hz, 1H), 7.62 (t, J = 8.4 Hz, 1H), 7.57 (d, J = 7.2 Hz, 2H), 7.40 (t, J = 7.2 Hz, 2H), 7.33-7.31 (m, 2H), 6.86, (s, 2H), 5.27 (s, 2H)
13C NMR: δ 185.3 (1C, s), 184.2 (1C, s), 158.6 (1C, s), 140.9 (1C, s), 136.3 (1C, s), 136.1 (1C, s), 134.9 (1C, s), 134.2 (1C, s), 128.8 (1C, s), 128.0 (1C, s), 126.7 (1C, s), 120.3 (1C, s), 119.7 (1C, s), 119.5 (1C, s), 70.9 (1C, s)

### benchmark_expand_500:R210
Molecular formula: C13H12O
IR bands (cm-1): [3051.0, 2978.0, 1384.0, 865.0, 826.0, 742.0]
1H NMR: 7.86 (d, J = 1.6 Hz, 1H), 7.84-7.81 (m, 3H), 7.50-7.44 (m, 3H), 3.06 (d, J = 5.5 Hz, 1H), 2.90 (d, J = 5.5 Hz, 1H), 1.83 (s, 3H)
13C NMR: δ 138.6 (1C, s), 133.1 (1C, s), 132.7 (1C, s), 128.1 (1C, s), 127.9 (1C, s), 127.5 (1C, s), 126.2 (1C, s), 125.9 (1C, s), 124.4 (1C, s), 123.1 (1C, s), 57.0 (1C, s), 56.9 (1C, s), 21.8 (1C, s)

### benchmark_expand_500:R212
Molecular formula: C28H23N7O4
IR bands (cm-1): [3427.0, 3286.0, 1665.0, 1648.0, 1591.0, 1569.0, 1521.0]
1H NMR: 10.49 (s, 1H, NH, exchangeable by D2O), 8.99 (t, 1H, J4 =2.4 Hz,), 8.71 (dd, 1H, J3 = 8.0 Hz, J4 = 2.4 Hz), 8.58 (s, 1H), 8.25 (ddd, 1H, J3 = 8.0 Hz, J4 = 2.4 Hz, J4 = 0.8 Hz), 8.02-7.97 (m, 4H), 7.73 (t, 1H, J3 = 8.0 Hz), 7.63-7.52 (m, 3H), 7.28 (d, 2H, J3 = 8.0 Hz), 4.32 (br s, 4H), 3.78 (t, 4H, J3 = 4.8 Hz)
13C NMR: δ 166.07 (1C, s), 155.42 (1C, s), 153.38 (1C, s), 151.27 (1C, s), 148.23 (1C, s), 140.00 (1C, s), 139.85 (1C, s), 138.84 (1C, s), 134.82 (1C, s), 134.05 (1C, s), 132.02 (1C, s), 130.35 (1C, s), 130.24 (1C, s), 128.70 (1C, s), 127.89 (1C, s), 124.58 (1C, s), 124.05 (1C, s), 121.96 (1C, s), 121.25 (1C, s), 119.18 (1C, s), 66.40 (1C, s), 45.44 (1C, s)

### benchmark_expand_500:R213
Molecular formula: C34H29NO
IR bands (cm-1): [2969.0, 2929.0, 1629.0, 1467.0, 1425.0, 1282.0, 1067.0, 818.0, 749.0]
1H NMR: 8.87 (s, 1H), 8.82 (d, J = 8.9 Hz, 2H), 8.75 (d, J = 9.1 Hz, 1H), 8.07 (d, J = 9.1 Hz, 1H), 8.04 (d, J = 8.5 Hz, 2H), 7.99 (s, 1H), 7.86 (d, J = 8.2 Hz, 1H), 7.83 (d, J = 8.5 Hz, 1H), 7.77-7.73 (m, 1H), 7.70-7.66 (m, 1H), 7.47 (br d, J = 8.4 Hz, 2H), 7.42-7.38 (m, 1H), 7.33-7.29 (br m, 1H), 3.65-2.49 (br m, 4H), 2.41 (s, 3H), 0.94 (s, 3H), 0.36 (br t, J = 6.9 Hz, 3H). 13C{1H} NMR (100 MHz, CDCl3): δ = 169.8, 137.0, 135.3, 135.0, 132.8, 132.4, 132.1, 131.9, 130.9, 130.6, 129.6, 128.8, 128.7, 128.2, 128.0, 127.8, 127.1, 127.0, 126.7, 125.5, 124.6, 123.3, 122.4, 121.1, 43.1, 37.9, 21.4, 14.0, 11.4
13C NMR: δ 169.8 (1C, s), 137.0 (1C, s), 135.3 (1C, s), 135.0 (1C, s), 132.8 (1C, s), 132.4 (1C, s), 132.1 (1C, s), 131.9 (1C, s), 130.9 (1C, s), 130.6 (1C, s), 129.6 (1C, s), 128.8 (1C, s), 128.7 (1C, s), 128.2 (1C, s), 128.0 (1C, s), 127.8 (1C, s), 127.1 (1C, s), 127.0 (1C, s), 126.7 (1C, s), 125.5 (1C, s), 124.6 (1C, s), 123.3 (1C, s), 122.4 (1C, s), 121.1 (1C, s), 43.1 (1C, s), 37.9 (1C, s), 21.4 (1C, s), 14.0 (1C, s), 11.4 (1C, s)
