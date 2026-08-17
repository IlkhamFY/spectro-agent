# Blind structure-elucidation task

You are given real experimental spectra (from the published literature) for a set of
organic molecules. For EACH compound you are given the molecular formula (from HRMS),
the IR band list, and the 1H and 13C NMR shift lists. No name, SMILES, or hint is given.

For each compound, propose the 3 most likely structures, best first, as SMILES.

Rules:
  - Use only the spectra provided. Do not use external lookups or tools.
  - Candidates must match the given molecular formula exactly.
  - Order candidates by your own confidence (most likely first).

Return ONLY a JSON object mapping each id to a list of 3 SMILES strings, e.g.:
  {"M001": ["CCO", "COC", "..."], "M002": ["...", "...", "..."], ...}

Compounds:

### M037
Molecular formula: C15H30N2O
IR bands (cm-1): [3209.0, 2955.0, 1658.0, 1467.0, 1367.0, 1165.0, 918.0, 722.0]
1H NMR: 0.89 (d, J = 6.6, 3H, C-3CH2CHCH3), 0.90 (d, J = 6.2, 3H, C-5CH2CHCH3), 0.91 (d, J = 5.6, 3H, C-6CHCH3), 0.93 (d, J = 6.9, 3H, C-3CH2CHCH3), 0.94 (d, J = 6.8, 3H, C-5CH2CHCH3), 0.98 (d, J = 6.7, 3H, C-6CHCH3), 1.30 (ddd, J = 13.9, 7.1, 6.5, 1H, C-5CH2), 1.33 (ddd, J = 13.9, 8.2, 5.6, 1H, C-5CH2), 1.40 (ddd, J = 14.2, 10.0, 4.1, 1H, C-3CH2), 1.65 (nonet, J = 6.7, 1H, C-5CH2CH), 1.74 (m, 1H, C-3CH2CH), 1.88 (ddd, J = 13.7, 10.3, 3.3, 1H, C-3CH2), 1.91 (hepd, J = 6.8, 2.5, 1H, C-6CH), 3.06 (dd, J = 6.7, 3.6, 1H, C-6H), 3.15 (dt, J = 7.8, 5.3, 1H, C-5H), 3.40 (dd, J = 10.2, 3.4, 1H, C-3H), 6.22 (brs, 1H, N1H)
13C NMR: δ 17.7 (1C, s), 21.0 (1C, s), 21.5 (1C, s), 22.4 (1C, s)

### M038
Molecular formula: C9H9BrO
IR bands (cm-1): [2967.0, 1679.0, 1600.0, 1569.0, 1455.0, 1382.0, 1290.0, 1259.0, 1207.0, 1185.0, 1006.0, 978.0, 735.0]
1H NMR: 7.70-7.65 (m, 1H, Ar), 7.43 (td, J = 7.5, 1.5 Hz, 1H, Ar), 7.33-7.27 (m, 2H, Ar), 4.42 (s, 2H, CH 2Br), 2.53 (s, 3H, CH 3)
13C NMR: δ 194.3 (1C, s), 139.9 (1C, s), 134.6 (1C, s), 132.5 (1C, s), 132.5 (1C, s), 129.1 (1C, s), 125.9 (1C, s), 33.8 (1C, s), 21.6 (1C, s)

### M039
Molecular formula: C17H30O3Si
IR bands (cm-1): [3473.0, 2959.0, 2933.0, 2858.0, 1722.0, 1596.0, 1514.0, 1473.0, 1391.0, 1365.0, 1257.0, 1071.0, 1026.0, 1011.0]
1H NMR: 6.11 (1H, d, J = 3.2 Hz), 6.09 (1H, d, J = 3.2 Hz), 4.27 (1H, d, J = 6.9 Hz), 3.66 (2H, s), 2.14 (3H, s), 2.00 (1H, octuplet, J = 6.7 Hz), 0.94 (3H, d, J = 6.7 Hz), 0.87 (9H, s), 0.79 (3H, d, J = 6.7 Hz), 0.03 (3H, s), -0.12 (3H, s)
13C NMR: δ 204.4 (1C, s), 156.7 (1C, s), 146.8 (1C, s), 108.6 (1C, s), 107.5 (1C, s), 74.1 (1C, s), 43.5 (1C, s), 34.3 (1C, s), 28.9 (1C, s), 25.8 (1C, s), 18.7 (1C, s), 18.3 (1C, s), 18.2 (1C, s), -4.9 (1C, s), -5.2 (1C, s)

### M040
Molecular formula: C14H10N2O3S
IR bands (cm-1): [2925.0, 2156.0, 1581.0, 1486.0, 1340.0, 1244.0, 1091.0, 843.0]
1H NMR: 8.18 (d, 1H, J = 2.7 Hz), 8.05 (dd, 1H, J = 9.0, 2.7 Hz), 7.61-7.56 (m, 2H), 7.09-7.04 (m, 2H), 6.90 (d, 1H, J = 9.0 Hz), 2.37 (s, 3H); 13C{1H} NMR (CDCl3, 101 MHz): δ 159.6 (C), 157.6 (C), 143.8 (C), 133.4 (2 × CH), 130.7 (C), 127.2 (CH), 123.4 (CH), 120.7 (2 × CH), 119.1 (C), 117.9 (CH), 110.8 (C), 16.5 (CH3)
13C NMR: δ 159.6 (1C, s), 157.6 (1C, s), 143.8 (1C, s), 133.4 (1C, s), 130.7 (1C, s), 127.2 (1C, s), 123.4 (1C, s), 120.7 (1C, s), 119.1 (1C, s), 117.9 (1C, s), 110.8 (1C, s), 16.5 (1C, s)

### M041
Molecular formula: C10H18O3Si
IR bands (cm-1): [2960.0, 2178.0, 1736.0, 1252.0, 1081.0, 848.0]
1H NMR: 3.86 (s, 3H), 3.08 (t, J = 7.2 Hz, 2H), 2.53 (t, J = 7.2 Hz, 2H), 0.11 (s, 9H)
13C NMR: δ 191.9 (1C, s), 160.9 (1C, s), 104.4 (1C, s), 85.8 (1C, s), 53.1 (1C, s), 38.7 (1C, s), 13.9 (1C, s), 0.0 (1C, s)

### M042
Molecular formula: C13H19NO4S
IR bands (cm-1): [3423.0, 3279.0, 2949.0, 2872.0, 1706.0, 1598.0, 1497.0, 1458.0, 1420.0, 1384.0, 1339.0, 1168.0, 1152.0, 1122.0, 1091.0, 1020.0]
1H NMR: 7.97 (d, J = 8.60 Hz, 1H, NH), 7.61 (d, J = 8.55 Hz, 2H, Ar-H), 7.31 (d, J = 8.55 Hz, 2H, ArH), 3.60 (m, 1H, CH-CO2H), 2.33 (s, 3H, CH3-Ar), 1.53 (m, 1H, CH), 1.34 (m, 2H, CH2), 0.76 (d, J = 6.85 Hz, 3H, CH3), 0.65 (d, J = 6.30 Hz, 3H, CH3)
13C NMR: δ 173.8 (1C, s), 142.9 (1C, s), 138.9 (1C, s), 129.9 (1C, s), 128.6 (1C, s), 127.0 (1C, s), 126.0 (1C, s), 54.5 (1C, s), 41.5 (1C, s), 24.4 (1C, s), 23.1 (1C, s), 21.6 (1C, s)
