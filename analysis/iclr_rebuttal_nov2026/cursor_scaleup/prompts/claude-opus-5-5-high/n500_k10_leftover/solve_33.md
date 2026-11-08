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
  {"benchmark_main:R28": ["CCO", "COC"]}

Compounds:

### benchmark_main:R28
Molecular formula: C22H28N2O2
IR bands (cm-1): [3277.0, 3028.0, 1753.0, 1240.0, 1080.0]
1H NMR: 7.27 (10H, m), 6.09 (1H, br s), 4.75 (1H, m), 3.72 (2H, d, J = 13.8 Hz), 3.58 (1H, t, J = 8.4 Hz), 3.55 (2H, d, J = 13.8 Hz), 3.12 (1H, t, J = 8.4 Hz), 2.67 (1H, dd, J = 7.0, 5.6 Hz), 1.96 (1H, heptet, J = 6.6 Hz), 1.73 (6H, q, J = 7.0 Hz), 1.27 (1H, m), 0.92 (3H, d, J = 6.6 Hz), 0.73 (3H, d, J = 6.2 Hz)
13C NMR: δ 160.3 (1C, s), 140.1 (1C, s), 129.4 (1C, s), 128.4 (1C, s), 127.1 (1C, s), 78.9 (1C, s), 57.0 (1C, s), 55.0 (1C, s), 43.9 (1C, s), 35.6 (1C, s), 24.5 (1C, s), 23.4 (1C, s), 22.4 (1C, s)

### benchmark_main:R30
Molecular formula: C23H18N2O4
IR bands (cm-1): [3429.0, 2962.0, 2220.0, 1734.0, 1689.0, 1607.0, 1553.0, 1427.0, 1312.0, 1194.0, 1050.0, 767.0]
1H NMR: 8.43 (d, J = 7.1 Hz, 1H), 7.94 (d, J = 8.2 Hz, 1H), 7.80 (d, J = 8.2 Hz, 1H), 7.64 (m, 3H), 6.77 (d, J = 5.0 Hz, 2H), 4.57 (m, 2H), 4.41 (m, 2H), 1.44 (m, 6H)
13C NMR: δ 167.9 (1C, s), 166.4 (1C, s), 151.6 (1C, s), 146.2 (1C, s), 135.0 (1C, s), 133.4 (1C, s), 133.0 (1C, s), 132.1 (1C, s), 130.1 (1C, s), 129.8 (1C, s), 128.4 (1C, s), 128.0 (1C, s), 126.5 (1C, s), 124.9 (1C, s), 124.1 (1C, s), 121.3 (1C, s), 115.7 (1C, s), 106.6 (1C, s), 92.6 (1C, s), 62.0 (1C, s), 61.8 (1C, s), 14.1 (1C, s), 14.1 (1C, s)

### benchmark_main:R31
Molecular formula: C27H26N2O3
IR bands (cm-1): [1647.0, 1483.0, 1466.0, 1442.0, 1291.0, 1208.0, 1172.0, 1091.0, 1046.0, 1028.0, 909.0, 774.0, 729.0, 700.0]
1H NMR: 7.56-7.49 (m, 1H), 7.44 (td, J = 7.5, 1.3 Hz, 1H), 7.37 (td, J = 7.5, 1.5 Hz, 1H), 7.28-7.15 (m, 4H), 7.06-6.99 (m, 2H), 6.99-6.93 (m, 2H), 6.83 (dd, J = 8.8, 2.4 Hz, 1H), 5.13 (d, J = 16.9 Hz, 1H), 5.07-4.99 (m, 2H), 4.91 (d, J = 10.3 Hz, 1H), 3.93-3.84 (m, 4H), 3.62 (ddd, J = 15.0, 6.1, 1.4 Hz, 1H), 3.49 (ddd, J = 16.4, 13.9, 6.1 Hz, 1H), 3.16 (s, 3H), 2.89 (ddd, J = 16.5, 4.4, 1.4 Hz, 1H) ppm
13C NMR: δ 172.3 (1C, s), 154.4 (1C, s), 138.0 (1C, s), 137.4 (1C, s), 134.7 (1C, s), 132.9 (1C, s), 130.5 (1C, s), 129.3 (1C, s), 129.3 (1C, s), 128.9 (1C, s), 128.7 (1C, s), 128.2 (1C, s), 127.1 (1C, s), 126.1 (1C, s), 112.6 (1C, s), 111.4 (1C, s), 109.0 (1C, s), 100.3 (1C, s), 75.7 (1C, s), 56.2 (1C, s), 55.9 (1C, s), 47.7 (1C, s), 44.9 (1C, s)

### benchmark_main:R33
Molecular formula: C24H25F3N2O3
IR bands (cm-1): [3500.0, 2000.0, 3159.0, 2926.0, 2358.0, 1661.0, 1582.0, 447.0]
1H NMR: 10.31 (s, 1H, -NH), 8.01 (d, 1H), 7.92 (t, 1H), 7.83 (t, 1H), 7.60 (d, 1H), 6.71 (s, 1H), 6.69 (s, 1H), 4.13 (m, 2H, J = 5.6, 1.1 Hz), 2.61 (br s, 2H), 2.50 (s, 2H), 2.16 (m, 3H, J = 6.2, 7.6 Hz), 1.23 (t, 3H)
13C NMR: δ 187.7 (1C, s), 180.5 (1C, s), 170.2 (1C, s), 163.3 (1C, s), 141.6 (1C, s), 137.7 (1C, s), 134.4 (1C, s), 134.0 (1C, s), 132.0 (1C, s), 132.0 (1C, s), 129.1 (1C, s), 127.6 (1C, s), 126.9 (1C, s), 112.8 (1C, s), 109.3 (1C, s), 104.5 (1C, s), 102.4 (1C, s), 58.2 (1C, s), 19.3 (1C, s), 17.6 (1C, s), 15.8 (1C, s), 15.3 (1C, s), 14.4 (1C, s), 12.4 (1C, s)

### benchmark_main:R35
Molecular formula: C22H15NO4
IR bands (cm-1): [1714.0, 1691.0, 1462.0, 822.0, 752.0]
1H NMR: 8.38-8.36 (d, J = 13.74 Hz, 2H), 7.82-7.80 (d, J = 13.74 Hz, 2H), 7.21-7.18 (dd, J = 7.72 Hz, J = 7.75 Hz, 2H), 6.95-6.93 (d, J = 7.75 Hz, 2H), 6.77-6.75 (d, J = 7.75 Hz, 1H), 6.10(s, 2H), 5.48-5.46 (q, 2H), 5.36 (s, 2H), 4.49 (s, 2H), 2.12(d, 6H)
13C NMR: δ 187.9 (1C, s), 152.5 (1C, s), 149.1 (1C, s), 133.0 (1C, s), 132.9 (1C, s), 129.0 (1C, s), 128.2 (1C, s), 126.1 (1C, s), 114.6 (1C, s), 114.1 (1C, s), 121.4 (1C, s), 54.9 (1C, s)

### benchmark_main:R39
Molecular formula: C28H25NO2
IR bands (cm-1): [3155.0, 3394.0, 3029.0, 1950.0, 1682.0, 1564.0]
1H NMR: 7.57-7.56 (dd, J1 = 1 Hz, J2 = 8 Hz, 3H), 7.48-7.38 (m, 12H), 7.06 (s, 1H), 6.92 (d, J = 4 Hz, 2H), 4.56 (d, J = 4.5 Hz, 2H), 3.97-3.93 (q, 2H), 0.76 (t, J = 7 Hz, 3H) ppm
13C NMR: δ 169.9 (1C, s), 149.3 (1C, s), 145.0 (1C, s), 144.7 (1C, s), 143.7 (1C, s), 140.8 (1C, s), 138.9 (1C, s), 128.8 (1C, s), 128.7 (1C, s), 128.1 (1C, s), 128.0 (1C, s), 127.9 (1C, s), 127.3 (1C, s), 127.2 (1C, s), 126.7 (1C, s), 117.9 (1C, s), 112.4 (1C, s), 109.2 (1C, s), 60.4 (1C, s), 47.7 (1C, s)
