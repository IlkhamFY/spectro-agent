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
  {"benchmark_expand_500:R11": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R11
Molecular formula: C16H22N2O
IR bands (cm-1): [3478.0, 3275.0, 3066.0, 2972.0, 2910.0, 2819.0, 2329.0, 2084.0, 1922.0, 1732.0, 1639.0, 1598.0, 1497.0, 1435.0, 1375.0, 1336.0, 1276.0, 1225.0, 1154.0, 1095.0, 1021.0, 909.0, 757.0, 693.0]
1H NMR: 7.31-7.26 (m, 2H), 6.96-6.89 (m, 3H), 5.78 (dddd, J = 16.8, 10.2, 7.6, 6.5 Hz, 1H), 5.07 (dq, J = 17.1, 1.6 Hz, 1H), 5.03 (ddt, J = 10.2, 2.1, 1.1 Hz, 1H), 3.86-3.74 (m, 2H), 3.73-3.63 (m, 2H), 3.22-3.10 (m, 4H), 2.80 (sextet, J = 6.9 Hz, 1H), 2.46 (dtt, J = 14.9, 6.7, 1.4 Hz, 1H), 2.16 (m, 1H), 1.16 (d, J = 6.8 Hz, 3H) ppm. 13C{1H} NMR (CDCl3, 151 MHz): δ = 174.5, 151.1, 136.2, 129.4 (2C), 120.7, 116.8, 116.7 (2C), 50.1, 49.7, 45.6, 41.8, 38.3, 35.5, 17.5 ppm
13C NMR: δ 174.5 (1C, s), 151.1 (1C, s), 136.2 (1C, s), 129.4 (1C, s), 120.7 (1C, s), 116.8 (1C, s), 116.7 (1C, s), 50.1 (1C, s), 49.7 (1C, s), 45.6 (1C, s), 41.8 (1C, s), 38.3 (1C, s), 35.5 (1C, s)

### benchmark_expand_500:R110
Molecular formula: C6H8O2
IR bands (cm-1): [3382.0, 3084.0, 2985.0, 2933.0, 1743.0, 1659.0, 1448.0, 1376.0, 1342.0, 1321.0, 1209.0, 1188.0, 1103.0, 1082.0, 1048.0, 1028.0, 997.0, 929.0, 866.0, 763.0, 610.0, 574.0, 540.0]
1H NMR: 7.02 (quint, 3JH,H = 4JH,H = 1.6 Hz, 1JC,H = 171.3 Hz, 1H, CH), 5.01-4.94 (m, 1H, CH), 1.90 (dd, 4JH,H = 5JH,H = 1.6 Hz, 1JC,H = 128.8 Hz, 3H, CH3), 1.39 (d, 3JH,H = 6.8 Hz, 1JC,H = 129.0 Hz, 3H, CH3)
13C NMR: δ 173.9 (1C, s), 149.6 (1C, s), 129.3 (1C, s), 77.1 (1C, s), 18.7 (1C, s), 10.2 (1C, s)

### benchmark_expand_500:R113
Molecular formula: C8H10N2O2
IR bands (cm-1): [3378.0, 2908.0, 1608.0, 1587.0, 1541.0, 1486.0, 1463.0, 1407.0, 1386.0, 1290.0, 1261.0, 1189.0, 1118.0, 1094.0, 1036.0, 1001.0]
1H NMR: 8.09 (dd, 3J = 9.0 Hz, 4J = 2.5 Hz, 1H), 7.99-7.96 (d, 4J = 2.5 Hz, 1H), 6.53 (d, 3J = 9.0 Hz, 1H), 4.37 (br. s, 1H), 3.00 (d, 3J = 5.0 Hz, 3H), 2.17 (s, 3H). 13C{1H} NMR (CDCl3, 100 MHz) δ 152.6, 137.6, 126.0, 124.9, 121.0, 107.4, 30.5, 17.3
13C NMR: δ 152.6 (1C, s), 137.6 (1C, s), 126.0 (1C, s), 124.9 (1C, s), 121.0 (1C, s), 107.4 (1C, s), 30.5 (1C, s), 17.3 (1C, s)

### benchmark_expand_500:R115
Molecular formula: C17H25BrFNO2
IR bands (cm-1): [2976.0, 2938.0, 2861.0, 2818.0, 2766.0, 1748.0, 1732.0, 1562.0, 1459.0, 1432.0, 1392.0, 1368.0, 1283.0, 1250.0, 1148.0, 1092.0, 1076.0, 1033.0, 1005.0, 965.0, 944.0, 903.0, 842.0, 783.0, 763.0, 742.0, 715.0]
1H NMR: 7.57 (1H, d, J = 8.0 Hz, ArH), 7.38 (1H, d, J = 8.0 Hz, ArH), 7.06 (1H, ddq, J = 8.0, 8.0, 0.5 Hz, ArH), 2.66-2.34 (4H, m, CH2), 2.47 (3H, d, 5JFH = 2.8 Hz, ArCH3), 2.26 (6H, s, N(CH3)2), 1.43 (9H, s, tBu); 13C{1H} NMR (101 MHz, CDCl3) δ 169.0 (d, 2JFC = 26 Hz), 138.4 (d, 2JFC = 21 Hz), 136.4, 133.1 (d, 3JFC = 2 Hz), 127.7 (d, JFC = 2 Hz), 126.6, 125.5 (d, 3JFC = 8 Hz), 96.0 (d, 1JFC = 190 Hz), 83.0, 53.5 (d, 3JFC = 5 Hz), 45.5, 34.9 (d, 2JFC = 22 Hz), 27.7, 20.3 (d, 4JFC = 7 Hz)
13C NMR: δ 169.0 (1C, d), 138.4 (1C, d), 136.4 (1C, s), 133.1 (1C, d), 127.7 (1C, d), 126.6 (1C, s), 125.5 (1C, d), 96.0 (1C, d), 83.0 (1C, s), 53.5 (1C, d), 45.5 (1C, s), 34.9 (1C, d), 27.7 (1C, s), 20.3 (1C, d)

### benchmark_expand_500:R118
Molecular formula: C19H30O2
IR bands (cm-1): [2924.0, 2854.0, 1726.0, 1601.0, 1575.0, 1464.0, 1433.0, 1256.0, 1189.0, 1104.0, 1081.0, 750.0, 710.0]
1H NMR: 0.88 (t, 3H, J = 6.6 Hz, C11′), 1.14-1.44 (m, 16H, C3′-C10′), 1.49-1.67 (m, 2H, C2′), 2.93 (t, 2H, J = 7.8 Hz, C1′), 3.88 (s, 3H, C8), 7.15-7.29 (m, 2H, C3, C5), 7.40 (ddd, 1H, J = 1.3, 7.5 Hz, C4), 7.84 (dd, 1H, J = 1.1, 7.8 Hz, C6)
13C NMR: δ 14.1 (1C, s), 22.7 (1C, s), 29.4 (1C, s), 29.5 (1C, s), 29.6 (1C, s), 29.7 (1C, s), 29.7 (1C, s), 29.8 (1C, s), 31.8 (1C, s), 31.9 (1C, s), 34.5 (1C, s), 51.8 (1C, s), 125.6 (1C, s), 129.5 (1C, s), 130.5 (1C, s), 130.9 (1C, s), 131.8 (1C, s), 144.7 (1C, s), 168.3 (1C, s)

### benchmark_expand_500:R12
Molecular formula: C12H12N4
IR bands (cm-1): [3444.0, 3395.0, 3351.0, 3310.0, 3058.0, 2923.0, 1646.0, 1597.0, 1541.0, 1467.0, 1427.0, 883.0, 752.0, 696.0]
1H NMR: 4.65 (s, 2H, NH2 + D2O exchangeable), 5.36 (s, 2H, NH2 + D2O exchangeable), 7.44-7.55 (m, 4H, Ph), 7.71-7.77 (m, 2H, 1H Ph and 1H pyridine), 8.30 (s, 1H, pyridine), 8.58 (d, 1H, pyridine, J = 5 Hz) ppm
13C NMR: δ 117.02 (1C, s), 120.06 (1C, s), 128.55 (1C, s), 129.46 (1C, s), 129.55 (1C, s), 138.00 (1C, s), 148.34 (1C, s), 148.90 (1C, s), 151.40 (1C, s)
