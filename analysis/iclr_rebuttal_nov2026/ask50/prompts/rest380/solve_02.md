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
  {"benchmark_expand:R102": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R102
Molecular formula: C32H45N9O6
IR bands (cm-1): [3550.0, 3000.0, 2961.0, 2916.0, 2871.0, 2847.0, 1651.0, 1444.0, 1394.0, 1373.0, 1335.0, 1298.0, 1119.0, 1097.0, 978.0, 868.0, 825.0, 498.0]
1H NMR: 0.18 (t, J=7.3 Hz, 6H), 2.04-2.12 (m, 4H), 3.23 (s+s, 8H), 3.39 (s, 4H), 3.82 (s, 4H), 4.26 (s, 2H), 7.35 (d, J=1.5 Hz, 1H), 7.38 (dd, J=8.0/1.7 Hz, 1H), 7.40 (d, J=1.5 Hz, 1H), 7.45 (d, J=1.7 Hz, 1H), 7.94 (d, J=8.0 Hz, 1H) ppm
13C NMR: δ 8.8 (1C, s), 34.0 (1C, s), 56.7 (1C, s), 58.4 (1C, s), 58.6 (1C, s), 58.7 (1C, s), 60.2 (1C, s), 60.4 (1C, s), 124.5 (1C, s), 125.1 (1C, s), 129.6 (1C, s), 131.7 (1C, s), 133.5 (1C, s), 137.4 (1C, s), 141.1 (1C, s), 142.3 (1C, s), 152.3 (1C, s), 152.9 (1C, s), 176.3 (1C, s)

### benchmark_expand:R11
Molecular formula: C14H14N4
IR bands (cm-1): [3433.0, 3344.0, 3433.0, 2952.0, 2850.0, 1703.0, 1609.0, 1570.0, 1497.0, 1455.0, 1435.0, 1303.0, 1272.0, 1170.0, 1142.0, 1094.0, 1020.0, 930.0, 900.0, 856.0, 808.0]
1H NMR: 6.67 (d, 3J6,5 = 8.2 Hz, 2H, 6-H), 6.24 (dd, 3J5,6 = 8.2 Hz, 4J5,3 = 2.3 Hz, 2H, 5-H), 5.97 (d, 4J3,5 = 2.3 Hz, 2H, 3-H), 5.15 (br.s, 4H, 4-NH2), 2.63 (mc, 4H, 7-Ha, 7-Hb,)
13C NMR: δ 155.87 (1C, s), 146.76 (1C, s), 130.15 (1C, d), 115.18 (1C, s), 112.88 (1C, d), 103.11 (1C, d), 30.44 (1C, t)

### benchmark_expand:R13
Molecular formula: C12H8ClNOS
IR bands (cm-1): [3034.0, 2921.0, 2855.0, 1701.0, 1619.0, 1467.0, 1307.0, 1228.0, 1067.0, 791.0, 701.0, 662.0, 556.0]
1H NMR: 9.32 (1H, s), 7.19 (1H, t, J = 3.6 Hz), 7.17 (1H, s), 7.15-7.14 (1H, m), 6.93-6.92 (2H, m), 6.77 (1H, d, J = 8.4 Hz), 4.80 (1H, s)
13C NMR: δ 177.2 (1C, s), 140.0 (1C, s), 136.6 (1C, s), 130.4 (1C, s), 128.8 (1C, s), 128.1 (1C, s), 127.1 (1C, s), 126.4 (1C, s), 125.6 (1C, s), 125.5 (1C, s), 111.3 (1C, s), 47.7 (1C, s)

### benchmark_expand:R14
Molecular formula: C20H13NO2
IR bands (cm-1): [2984.0, 2220.0, 1540.0, 1474.0, 1246.0, 774.0]
1H NMR: 8.27 (d, J = 8.4 Hz, 1H), 8.16 (d, J = 8.8 Hz, 2H), 7.91 (d, J = 8.4 Hz, 1H), 7.73 (d, J = 8.8 Hz, 1H), 7.67-7.60 (m, 2H), 7.54-7.50 (m, 1H), 7.03 (d, J = 8.8 Hz, 2H), 3.89 (s, 3H); 13C{1H} NMR (100 MHz, CDCl3) δ 161.7, 161.1, 148.7, 132.0, 128.6, 128.0, 127.1, 126.1, 125.4, 123.4, 120.8, 120.7, 119.8, 117.2, 114.8, 114.6, 87.4, 55.5
13C NMR: δ 161.7 (1C, s), 161.1 (1C, s), 148.7 (1C, s), 132.0 (1C, s), 128.6 (1C, s), 128.0 (1C, s), 127.1 (1C, s), 126.1 (1C, s), 125.4 (1C, s), 123.4 (1C, s), 120.8 (1C, s), 120.7 (1C, s), 119.8 (1C, s), 117.2 (1C, s), 114.8 (1C, s), 114.6 (1C, s), 87.4 (1C, s), 55.5 (1C, s)

### benchmark_expand:R18
Molecular formula: C30H33FO6
IR bands (cm-1): [2926.0, 2854.0, 1699.0, 1625.0, 1623.0, 1596.0, 1446.0, 1382.0, 1318.0, 1206.0, 1122.0, 1039.0, 994.0, 973.0, 823.0]
1H NMR: 0.87 (3H, t, J = 6.4 Hz), 1.24 (16H, bs), 1.45 (2H, m), 2.26 (3H), 2.44 (2H, m), 4.93 (1H, s), 6.19 (1H, s), 6.92 (1H, m), 7.03 (1H, m), 7.14 (1H, m), 7.25 (1H, m)
13C NMR: δ 14.1 (1C, s), 20.1 (1C, s), 22.6 (1C, s), 22.7 (1C, s), 28.0 (1C, s), 29.3 (1C, s), 29.5 (1C, s), 29.6 (1C, s), 31.9 (1C, s), 33.0 (1C, s), 98.4 (1C, s), 101.9 (1C, s), 114.8 (1C, s), 115.8 (1C, s), 124.4 (1C, s), 130.1 (1C, s), 117.5 (1C, s), 119.9 (1C, s), 143.3 (1C, s), 147.9 (1C, s), 151.1 (1C, s), 158.7 (1C, s), 161.9 (1C, s), 162.9 (1C, s), 163.0 (1C, s), 179.4 (1C, s)

### benchmark_expand:R21
Molecular formula: C20H23N3O5
IR bands (cm-1): [2942.0, 2809.0, 1632.0, 1615.0, 1515.0, 1350.0, 858.0, 829.0]
1H NMR: 8.25 (d, J = 12.0 Hz, 2H), 7.88 (d, J = 12.0 Hz, 1H), 7.58 (d, J = 6.0 Hz, 2H), 6.51 (t, J = 6.0 Hz, 1H), 6.47 (s, 1H), 3.90 (s, 3H), 3.77 (s, 2H), 3.68 (s, 2H), 2.74 (m, 4H), 2.64 (m, 4H) ppm
13C NMR: δ 161.36 (1C, s), 160.30 (1C, s), 142.40 (1C, s), 141.22 (1C, s), 126.87 (1C, s), 124.75 (1C, s), 118.78 (1C, s), 103.01 (1C, s), 96.46 (1C, s), 57.17 (1C, s), 50.80 (1C, s), 48.37 (1C, s)
