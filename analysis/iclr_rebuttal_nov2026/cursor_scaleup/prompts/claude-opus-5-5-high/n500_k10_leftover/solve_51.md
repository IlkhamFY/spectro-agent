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
  {"benchmark_expand_500:R151": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R151
Molecular formula: C14H11BrN2O3
IR bands (cm-1): [3291.0, 3238.0, 3039.0, 2917.0, 1616.0, 1604.0, 1543.0, 1507.0, 1472.0, 1341.0, 1276.0, 1265.0, 1197.0, 1187.0, 1170.0, 1105.0, 847.0, 831.0, 765.0, 689.0, 649.0, 623.0, 610.0, 560.0, 476.0]
1H NMR: 12.01 (s, 1H, NHCO), 11.42 (s, 1H, Ar-2-OH), 10.19 (s, 1H, 4-OH), 8.57 (s, 1H, CH=N), 7.83 (d, 3J = 8.7 Hz, 2H, H-2,6), 7.76 (d, 4J = 2.5 Hz, 1H, ArH-6), 7.41 (dd, 3J = 8.7 Hz, 4J = 2.5 Hz, 1H, ArH-4), 6.89 (d, 3J = 8.7 Hz, 1H, ArH-3), 6.87 (d, 3J = 8.7 Hz, 2H, ArH-3,5) ppm
13C NMR: δ 162.50 (1C, s), 160.91 (1C, s), 156.33 (1C, s), 148.92 (1C, s), 133.25 (1C, s), 130.54 (1C, s), 129.74 (1C, s), 123.04 (1C, s), 121.26 (1C, s), 118.59 (1C, s), 115.05 (1C, s)

### benchmark_expand_500:R152
Molecular formula: C11H15NO4
IR bands (cm-1): [2979.0, 2937.0, 1571.0, 1534.0, 1496.0, 1463.0, 1442.0, 1392.0, 1367.0, 1308.0, 1290.0, 1272.0, 1222.0, 1160.0, 1037.0, 878.0, 836.0, 813.0, 794.0]
1H NMR: 7.24 (d, J = 3.1 Hz, 1H), 7.12 (d, J = 9.1 Hz, 1H), 7.02 (dd, J = 9.1, 3.2 Hz, 1H), 3.82 (s, 3H), 1.35 (s, 9H)
13C NMR: δ 154.9 (1C, s), 145.8 (1C, s), 142.4 (1C, s), 126.6 (1C, s), 119.5 (1C, s), 108.9 (1C, s), 82.4 (1C, s), 55.9 (1C, s), 28.6 (1C, s)

### benchmark_expand_500:R153
Molecular formula: C11H20O2
IR bands (cm-1): [2953.0, 2928.0, 2856.0, 1728.0, 1658.0, 1460.0, 1436.0, 1378.0, 1313.0, 1270.0, 1197.0, 1170.0, 1127.0, 1041.0, 979.0, 921.0, 854.0, 720.0]
1H NMR: 0.89 (t, J = 6.8 Hz, 3 H), 1.29 (m, 8 H), 1.46 (m, 2 H), 2.16-2.23 (m, 2 H), 3.73 (s, 3 H), 5.82 (d, J = 15.6 Hz, 1 H), 6.98 (dt, J = 15.4, 7.0 Hz, 1 H)
13C NMR: δ 14.2 (1C, s), 22.8 (1C, s), 28.2 (1C, s), 29.3 (1C, s), 31.9 (1C, s), 32.4 (1C, s), 51.5 (1C, s), 120.9 (1C, s), 150.0 (1C, s)

### benchmark_expand_500:R154
Molecular formula: C13H12BrClN2O2S
IR bands (cm-1): [3284.0, 3110.0, 3063.0, 3043.0, 3024.0, 2980.0, 2933.0, 1632.0, 1601.0, 1585.0, 1540.0, 1493.0, 1424.0, 1356.0, 1340.0, 1166.0, 1120.0, 1109.0, 869.0, 851.0, 816.0, 728.0, 768.0, 703.0]
1H NMR: 8.36 (d, J = 2.4 Hz, 1H), 7.96 (d, J = 2.4 Hz, 1H), 7.10 (t, J = 5.5 Hz, 3H), 7.08-7.04 (m, 2H), 5.55 (d, J = 7.3 Hz, 1H), 4.58 (p, J = 7.0 Hz, 1H), 1.55 (d, J = 7.0 Hz, 3H)
13C NMR: δ 152.54 (1C, s), 145.68 (1C, s), 141.51 (1C, s), 139.66 (1C, s), 136.35 (1C, s), 128.50 (1C, s), 128.26 (1C, s), 126.26 (1C, s), 118.99 (1C, s), 54.85 (1C, s), 22.7 (1C, s)

### benchmark_expand_500:R155
Molecular formula: C12H13NO5
IR bands (cm-1): [2960.0, 1741.0, 1704.0, 1663.0, 1198.0, 1168.0, 980.0, 778.0]
1H NMR: 3.75 (s, 3H, CH2CO2CH3), 3.77 (s, 3H, =CHCO2CH3), 5.24 (s, 2H, CH2), 6.41 (d, J = 15.8 Hz, 1H, H-2), 6.70 (d, J = 4.0 Hz, 1H, H-3′), 6.97 (d, J = 4.0 Hz, 1H, H-4′), 7.41 (d, J = 15.8 Hz, 1H, H-3), 9.53 (CHO)
13C NMR: δ 46.3 (1C, s), 52.0 (1C, s), 52.8 (1C, s), 111.4 (1C, s), 121.1 (1C, s), 124.6 (1C, s), 129.7 (1C, s), 133.7 (1C, s), 137.7 (1C, s), 166.7 (1C, s), 168.3 (1C, s), 180.2 (1C, s)

### benchmark_expand_500:R156
Molecular formula: C17H16O3
IR bands (cm-1): [3003.0, 2967.0, 2876.0, 2839.0, 1683.0, 1600.0, 1575.0, 1484.0, 1464.0, 1435.0, 1375.0, 1308.0, 1290.0, 1244.0, 1155.0, 1048.0, 1002.0, 972.0]
1H NMR: 10.57 (d, J = 0.7 Hz, 1H), 7.86 (dd, J = 8.0, 1.9 Hz, 1H), 7.55 (ddd, J = 8.3, 7.4, 1.9 Hz, 1H), 7.30-7.21 (m, 1H), 7.09-6.98 (m, 3H), 6.95 (t, J = 2.1 Hz, 1H), 6.84 (ddd, J = 8.2, 2.6, 0.9 Hz, 1H), 6.74 (d, J = 15.9 Hz, 1H), 6.42 (dt, J = 16.0, 5.7 Hz, 1H), 4.83 (dd, J = 5.7, 1.6 Hz, 2H), 3.83 (s, 3H). 13C{1H} NMR (100 MHz, CDCl3): δ 189.9, 161.1, 160.0, 137.7, 136.0, 133.5, 129.8, 128.7, 125.3, 123.9, 121.1, 119.4, 114.0, 113.1, 112.1, 69.2, 55.4
13C NMR: δ 189.9 (1C, s), 161.1 (1C, s), 160.0 (1C, s), 137.7 (1C, s), 136.0 (1C, s), 133.5 (1C, s), 129.8 (1C, s), 128.7 (1C, s), 125.3 (1C, s), 123.9 (1C, s), 121.1 (1C, s), 119.4 (1C, s), 114.0 (1C, s), 113.1 (1C, s), 112.1 (1C, s), 69.2 (1C, s), 55.4 (1C, s)
