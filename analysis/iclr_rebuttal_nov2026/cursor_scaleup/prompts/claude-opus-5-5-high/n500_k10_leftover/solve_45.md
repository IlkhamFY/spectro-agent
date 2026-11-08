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
  {"benchmark_expand:R83": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R83
Molecular formula: C10H11ClN4S
IR bands (cm-1): [3055.0, 2987.0, 2940.0, 1901.0, 1685.0, 1593.0, 1491.0, 1448.0]
1H NMR: 7.41 (d, J = 8.4 Hz, 2H), 7.33 (d, J = 8.4 Hz, 2H), 6.02 (q, J = 7.2 Hz, 1H), 3.88 (s, 3H), 1.92 (d, J = 7.2 Hz, 3H)
13C NMR: δ 163.8 (1C, s), 136.8 (1C, s), 134.6 (1C, s), 129.0 (1C, s), 128.6 (1C, s), 57.1 (1C, s), 34.6 (1C, s), 20.0 (1C, s)

### benchmark_expand:R84
Molecular formula: C14H20O2
IR bands (cm-1): [3722.0, 3124.0, 2936.0, 2863.0, 1812.0, 1491.0, 1059.0, 1025.0, 760.0, 700.0, 613.0]
1H NMR: 7.37-7.30 (m, 4H), 7.29-7.24 (m, 1H), 5.16 (t, J = 7.6 Hz, 1H), 4.63 (dd, J = 7.9, 5.1 Hz, 1H), 3.58 (t, J = 6.7, 5.6 Hz, 2H), 2.30-2.21 (m, 2H), 2.18-2.10 (m, 1H), 2.09-2.00 (m, 1H), 1.93-1.85 (m, 1H), 1.84-1.76 (m, 1H), 1.63 (s, 3H)
13C NMR: δ 144.8 (1C, s), 138.1 (1C, s), 128.4 (1C, s), 127.5 (1C, s), 125.9 (1C, s), 120.5 (1C, s), 74.2 (1C, s), 62.3 (1C, s), 37.1 (1C, s), 36.1 (1C, s), 31.4 (1C, s), 16.2 (1C, s)

### benchmark_expand:R85
Molecular formula: C12H21NO2
IR bands (cm-1): [3491.0, 3263.0, 3081.0, 2966.0, 2858.0, 2325.0, 2161.0, 1934.0, 1731.0, 1635.0, 1427.0, 1363.0, 1300.0, 1265.0, 1234.0, 1115.0, 1073.0, 1025.0, 946.0, 911.0, 843.0, 779.0, 684.0]
1H NMR: 5.90 (dd, J = 17.4, 10.9 Hz, 1H), 4.97 (m, 1H), 4.95 (dd, J = 10.9, 1.3 Hz, 1H), 3.68-3.48 (m, 8H), 2.62 (q, J = 6.9 Hz, 1H), 1.07 (s, 3H), 1.06 (s, 3H), 1.05 (s, 3H) ppm. 13C{1H} NMR (CDCl3, 151 MHz): δ = 174.2, 146.6, 111.7, 67.2, 66.9, 47.0, 42.5, 42.1, 39.5, 24.8, 24.2, 13.7 ppm
13C NMR: δ 174.2 (1C, s), 146.6 (1C, s), 111.7 (1C, s), 67.2 (1C, s), 66.9 (1C, s), 47.0 (1C, s), 42.5 (1C, s), 42.1 (1C, s), 39.5 (1C, s), 24.8 (1C, s), 24.2 (1C, s)

### benchmark_expand:R89
Molecular formula: C15H11Br2NO
IR bands (cm-1): [3251.0, 3180.0, 3028.0, 2902.0, 1660.0, 1627.0, 1558.0, 1516.0, 1441.0, 1422.0, 1337.0, 1263.0, 1180.0, 970.0, 781.0, 766.0, 759.0, 721.0, 710.0, 694.0, 686.0, 626.0, 561.0, 501.0]
1H NMR: 10.12 (s, 1H), 7.75 (d, J = 7.8 Hz, 2H), 7.67-7.64 (m, 2H), 7.60 (d, J = 16 Hz, 1H), 7.48-7.40 (m, 3H), 7.21 (t, J = 8 Hz, 1H), 6.87 (d, J = 15.6 Hz, 1H)
13C NMR: δ 163.50 (1C, s), 140.85 (1C, s), 135.77 (1C, s), 134.50 (1C, s), 132.24 (1C, s), 130.19 (1C, s), 129.94 (1C, s), 129.05 (1C, s), 127.80 (1C, s), 124.33 (1C, s), 120.86 (1C, s)

### benchmark_expand:R90
Molecular formula: C7H11NO2
IR bands (cm-1): [3291.0, 2939.0, 2120.0, 1657.0, 1422.0, 1387.0]
1H NMR: 3.67 (s, 3H), 3.14 (s, 3H), 2.65 (t, J = 7.4 Hz, 2H), 2.54-2.39 (m, 2H), 2.01 (t, J = 2.7 Hz, 1H)
13C NMR: δ 172.5 (1C, s), 83.9 (1C, s), 68.7 (1C, s), 61.6 (1C, s), 32.3 (1C, s), 31.4 (1C, s), 14.0 (1C, s)

### benchmark_expand:R91
Molecular formula: C12H11BrFN3OSe
IR bands (cm-1): [3243.0, 3100.0, 1681.0, 1643.0]
1H NMR: 10.52 (d, J = 1.8 Hz, 1H), 9.25 (s, 5H), 7.65 (dd, J = 8.7, 5.5 Hz, 2H), 7.34 (t, J = 8.9 Hz, 2H), 6.47 (d, J = 1.5 Hz, 1H), 6.25 (s, 1H)
13C NMR: δ 170.32 (1C, s), 165.81 (1C, s), 164.18 (1C, s), 161.73 (1C, s), 149.04 (1C, s), 145.81 (1C, s), 131.25 (1C, s), 131.16 (1C, s), 127.52 (1C, s), 127.49 (1C, s), 122.61 (1C, s), 115.95 (1C, s), 115.74 (1C, s), 94.11 (1C, s)
