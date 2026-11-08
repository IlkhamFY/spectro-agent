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
  {"benchmark_expand_500:R35": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R35
Molecular formula: C12H10ClN3O5
IR bands (cm-1): [3208.0, 3018.0, 2980.0, 1740.0, 1699.0, 1555.0, 1363.0, 1217.0]
1H NMR: 9.22 (s, 2H, NH), 7.55 (m, 4Ph), 5.37 (dd, 1H, J = 13.9 Hz, CH2NO2), 5.07 (dd, 1H, J = 13.9 Hz, CH2NO2), 4.73 (m, 1H, CHPh)
13C NMR: δ 164.4 (1C, s), 152.3 (1C, s), 143.5 (1C, s), 132.2 (1C, s), 131.8 (1C, s), 131.4 (1C, s), 130.5 (1C, s), 119.2 (1C, s), 84.8 (1C, s), 78.9 (1C, s)

### benchmark_expand_500:R36
Molecular formula: C14H18O3
IR bands (cm-1): [2943.0, 2870.0, 1699.0, 1606.0, 1576.0, 1419.0, 1389.0, 1275.0, 1213.0, 1173.0, 1119.0, 1034.0, 989.0, 852.0, 827.0]
1H NMR: 9.97 (d, J = 2.5 Hz, 1H), 7.80 (dd, J = 2.5, 6.4 Hz, 2H), 7.36 (d, J = 6.4 Hz, 2H), 4.57 (s, 1H), 3.86 (m, 1H), 3.78 (m, 1H), 3.50 (m, 1H), 3.41 (m, 1H), 2.84-2.76 (m, 2H), 1.97-1.93 (m, 2H), 1.84 (m, 1H), 1.72 (m, 1H), 1.61-1.50 (m, 4H)
13C NMR: δ 192.2 (1C, s), 149.8 (1C, s), 134.7 (1C, s), 130.1 (1C, s), 129.2 (1C, s), 99.3 (1C, s), 66.7 (1C, s), 62.6 (1C, s), 32.9 (1C, s), 31.1 (1C, s), 30.9 (1C, s), 25.6 (1C, s), 19.8 (1C, s)

### benchmark_expand_500:R41
Molecular formula: C14H14O2
IR bands (cm-1): [3060.0, 2926.0, 1653.0, 1617.0, 1493.0, 1450.0, 1409.0, 1061.0, 937.0, 866.0, 772.0, 691.0]
1H NMR: 7.75 (dd, J = 7.7, 1.8 Hz, 1H), 7.51-7.46 (m, 1H), 6.72 (s, 1H), 6.19 (s, 1H), 2.60 (t, J = 7.5 Hz, 1H), 1.82-1.73 (m, 1H), 1.03 (t, J = 7.4 Hz, 1H) ppm
13C NMR: δ 180.1 (1C, s), 168.8 (1C, s), 163.6 (1C, s), 131.5 (1C, s), 131.3 (1C, s), 129.0 (1C, s), 125.8 (1C, s), 114.0 (1C, s), 111.1 (1C, s), 35.6 (1C, s), 20.3 (1C, s)

### benchmark_expand_500:R45
Molecular formula: C10H11N3S
IR bands (cm-1): [3418.0, 3262.0, 3154.0, 3027.0, 1591.0, 1536.0, 1451.0, 1371.0]
1H NMR: 6.88 (dd, J = 16.1, 9.2 Hz, 1H olefinic CH), 7.03 (d, J = 16.1 Hz, 1H, olefinic CH), 7.45-7.34 (m, 3H, arom.CH), 7.57 (d, J = 7.2 Hz, 2H, arom.CH), 7.68 (s, 1H, NH), 7.92 (d, J = 9.2 Hz, 1H, CH=N), 8.22, 11.44 (s, 2H, NH2) ppm
13C NMR: δ 119.12 (1C, s), 125.52 (1C, s), 127.40 (1C, s), 129.32 (1C, s), 136.32 (1C, s), 139.34 (1C, s), 145.19 (1C, s)

### benchmark_expand_500:R48
Molecular formula: C14H24O
IR bands (cm-1): [3335.0, 2959.0, 2925.0, 2866.0, 2827.0, 1456.0, 1373.0, 1359.0, 1258.0, 1205.0, 1031.0, 970.0, 939.0]
1H NMR: 5.95 (dq, J = 15.8, 0.9 Hz, 1H), 5.22 (dd, J = 15.8, 8.3 Hz, 1H), 3.53 (dd, J = 10.3, 5.7 Hz, 1H), 3.43 (dd, J = 10.3, 7.7 Hz, 1H), 2.47-2.38 (m, 1H), 1.99-1.95 (m, 2H), 1.67 (d, J = 0.9 Hz, 3H), 1.62-1.57 (m, 2H), 1.46-1.43 (m, 2H), 1.05 (d, J = 6.6 Hz, 3H), 0.99 (s, 3H), and 0.98 (s, 3H)
13C NMR: δ 137.3 (1C, s), 136.1 (1C, s), 129.1 (1C, s), 128.3 (1C, s), 67.4 (1C, s), 40.6 (1C, s), 39.3 (1C, s), 33.8 (1C, s), 32.6 (1C, s), 28.8 (1C, s), 28.7 (1C, s), 21.5 (1C, s), 19.2 (1C, s)

### benchmark_expand_500:R49
Molecular formula: C9H17ClO3
IR bands (cm-1): [2972.0, 2874.0, 1809.0, 1728.0, 1702.0, 1481.0, 1460.0, 1397.0, 1366.0, 1284.0, 1158.0, 1130.0, 1042.0, 1006.0, 940.0, 861.0, 770.0, 747.0, 669.0, 579.0, 546.0]
1H NMR: 4.23-4.21 (m, 2H, H-5), 3.72 (t, JH-H = 5.8 Hz, 2H, H-8), 3.72-3.70 (m, 2H, H-6), 3.61 (t, JH-H = 5.8 Hz, 2H, H-9), 1.20 (s, 9H, H-1/1′/1′′) ppm
13C NMR: δ 178.6 (1C, s), 71.3 (1C, s), 69.3 (1C, s), 63.5 (1C, s), 42.8 (1C, s), 38.8 (1C, s)
