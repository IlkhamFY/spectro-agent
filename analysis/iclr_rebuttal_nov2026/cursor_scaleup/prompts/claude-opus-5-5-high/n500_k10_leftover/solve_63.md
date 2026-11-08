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
  {"benchmark_main:R04": ["CCO", "COC"]}

Compounds:

### benchmark_main:R04
Molecular formula: C12H10FNO
IR bands (cm-1): [3403.0, 1600.0, 1444.0, 1046.0, 698.0]
1H NMR: 8.42 (d, 1H, J = 4.5 Hz), 7.40-7.37 (m, 2H), 7.37-7.30 (m, 3H), 7.29-7.24 (m, 2H), 5.99 (d, 1H, J = 6.2 Hz), 5.23 (d, 1H, J = 7.0 Hz); 13C{1H} NMR (150 MHz, CDCl3) δ 156.2 (d, JCF = 257 Hz), 149.0 (d, JCF = 17 Hz), 143.8 (d, JCF = 6 Hz), 142.1, 128.4, 127.8, 126.7, 124.0 (d, JCF = 3 Hz), 123.51 (d, JCF = 18 Hz) 70.1 (d, JCF = 3 Hz)
13C NMR: δ 156.2 (1C, d), 149.0 (1C, d), 143.8 (1C, d), 142.1 (1C, s), 128.4 (1C, s), 127.8 (1C, s), 126.7 (1C, s), 124.0 (1C, d), 123.51 (1C, d)

### benchmark_main:R10
Molecular formula: C14H20O
IR bands (cm-1): [2961.0, 2930.0, 2873.0, 1686.0, 1620.0, 1597.0, 1459.0, 1448.0, 1379.0, 1205.0, 735.0]
1H NMR: 7.95-7.97 (m, 2H), 7.53-7.58 (m, 1H), 7.46 (t, J = 7.6 Hz, 2H), 2.94 (t, J = 7.6 Hz, 2H), 1.67-1.72 (m, 2H), 1.25-1.38 (m, 5H) 0.87 (t, J = 7.6 Hz, 6H). 13C{1H} NMR (100.6 MHz, CDCl3): δ 201.1, 137.2, 133.0, 128.7, 128.2, 40.3, 36.2, 27.3, 25.4, 11.0
13C NMR: δ 201.1 (1C, s), 137.2 (1C, s), 133.0 (1C, s), 128.7 (1C, s), 128.2 (1C, s), 40.3 (1C, s), 36.2 (1C, s), 27.3 (1C, s), 25.4 (1C, s), 11.0 (1C, s)

### benchmark_main:R100
Molecular formula: C11H8F3N
IR bands (cm-1): [3401.0, 2920.0, 2851.0, 1738.0, 1343.0, 1112.0]
1H NMR: 8.49 (s, 1H), 7.58 (q, J = 8.6, 11.7 Hz, 4H), 6.93 (s, 1H), 6.65 (s, 1H), 6.37-6.34 (m, 1H). 13C{1H} NMR (75 MHz, CDCl3): δ 135.9 (C), 130.6 (C), 127.7 (q, 2JCF = 32.8 Hz, C), 125.9 (q, 3JCF = 3.9 Hz, 2 × CH), 124.3 (q, 1JCF = 271.6 Hz, CF3), 123.6 (2 × CH), 120.2 (CH), 110.7 (CH), 107.7 (CH)
13C NMR: δ 135.9 (1C, s), 130.6 (1C, s), 127.7 (1C, q), 125.9 (1C, q), 124.3 (1C, q), 123.6 (1C, s), 120.2 (1C, s), 110.7 (1C, s), 107.7 (1C, s)

### benchmark_main:R101
Molecular formula: C14H16N4O2S
IR bands (cm-1): [3302.0, 2958.0, 2908.0, 2866.0, 1614.0, 1587.0, 1545.0, 1504.0, 1438.0, 1409.0]
1H NMR: 13.03 (d, 1H, J = 14.8 Hz, NH), 8.62 (d, 1H, J = 14.4 Hz, CH=), 7.76 (d, 1H, J = 7.6 Hz, Ar-H), 7.63 (d, 1H, J = 8.8 Hz, Ar-H), 7.49 (t, 1H, J = 9.6 Hz, Ar-H), 7.28 (t, 1H, J = 8.4 Hz, Ar-H), 4.46 (m, 4H, 2CH2), 1.22 (m, 6H, 2CH3)
13C NMR: δ 178.4 (1C, s), 160.5 (1C, s), 159.2 (1C, s), 138.1 (1C, s), 135.6 (1C, s), 130.7 (1C, s), 118.3 (1C, s), 94.6 (1C, s), 42.4 (1C, s), 41.7 (1C, s)

### benchmark_main:R102
Molecular formula: C12H21NO
IR bands (cm-1): [3301.0, 2959.0, 2925.0, 1605.0, 1513.0, 1465.0, 1384.0, 1364.0]
1H NMR: 0.97 (t, 3H, J = 7.3 Hz), 1.19 (s, 9H), 1.39-1.43 (m, 2H), 1.56-1.66 (m, 2H), 2.24 (dd, 1H, J1 = 12.6 and J2 = 16.1 Hz), 2.40 (dd, 1H, J1 = 4.9 and J2 = 16.1 Hz), 3.55-3.63 (m, 1H), 4.76 (br s, 1H), 5.12 (s, 1H)
13C NMR: δ 13.9 (1C, s), 18.8 (1C, s), 28.6 (1C, s), 35.3 (1C, s), 36.3 (1C, s), 41.1 (1C, s), 53.1 (1C, s), 96.0 (1C, s), 172.6 (1C, s), 193.5 (1C, s)

### benchmark_main:R106
Molecular formula: C15H13N
IR bands (cm-1): [3292.0, 2976.0, 2930.0, 2870.0, 2325.0, 2107.0, 1594.0, 1473.0, 1293.0, 1018.0, 841.0, 740.0, 693.0, 644.0]
1H NMR: 8.67 (d, J = 2.3 Hz, 1H), 7.97-7.95 (m, 2H), 7.79 (dd, J = 8.2, 2.3 Hz, 1H), 7.68 (d, J = 8.2 Hz, 1H), 7.49-7.42 (m, 2H), 7.42-7.36 (m, 1H), 3.83 (qd, J = 7.2, 2.5 Hz, 1H), 2.30 (d, J = 2.5 Hz, 1H), 1.55 (d, J = 7.2 Hz, 3H)
13C NMR: δ 156.3 (1C, s), 148.6 (1C, s), 139.3 (1C, s), 136.6 (1C, s), 135.3 (1C, s), 129.0 (1C, s), 128.9 (1C, s), 127.0 (1C, s), 120.5 (1C, s), 85.9 (1C, s), 71.1 (1C, s), 29.2 (1C, s), 24.2 (1C, s)
