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

### M001
Molecular formula: C21H18ClN3O3S
IR bands (cm-1): [3435.0, 3236.0, 2974.0, 2209.0, 1732.0, 1584.0]
1H NMR: 1.16 (t, 3H, J = 7.5 Hz, OCH2CH3), 3.08 (m, 4H, CH2-CH2), 3.35, 6.55 (2 s, 4H, D2O exchangeable, 2NH2), 4.14 (q, 2H, J = 7.5 Hz, OCH2CH3), 6.85 (s, 1H, pyran H-4), 7.26-7.75 (m, 4H, C6H4)
13C NMR: δ 15.6 (1C, s), 49.6 (1C, s), 54.1 (1C, s), 98.4 (1C, s), 116.6 (1C, s), 118.1 (1C, s), 119.5 (1C, s), 120.8 (1C, s), 122.7 (1C, s), 124.5 (1C, s), 125.4 (1C, s), 126.8 (1C, s), 127.1 (1C, s), 129.9 (1C, s), 132.8 (1C, s), 135.3 (1C, s), 139.7 (1C, s)

### M002
Molecular formula: C16H12O5
IR bands (cm-1): [1610.0, 1680.0, 3450.0, 1325.0]
1H NMR: 5.14 (2H d, J = 11.2 Hz), 7.80 (5H d, J = 8.9), 6.90 (6H d, J = 8.9), 6.49 (8H d, J = 2.7 Hz), 7.19 (2H′ d, J =1.5), 7.42 (3H′ m), 6.76 (5H′ d, J = 8.0) 6.79 (6H′ d, J = 8.0), 3.76 (3-OCH3)
13C NMR: δ 151.4 (1C, s), 153.5 (1C, s), 173.5 (1C, s), 126.5 (1C, s), 121.8 (1C, s), 165.9 (1C, s), 102 (1C, s), 156.9 (1C, s), 115.8 (1C, s), 123.8 (1C, s), 114.3 (1C, s), 148.1 (1C, s), 145.4 (1C, s), 114.1 (1C, s), 118.5 (1C, s)

### M003
Molecular formula: C20H30O4
IR bands (cm-1): [2954.0, 2925.0, 2854.0, 1735.0, 1686.0, 1608.0, 1574.0, 1501.0, 1463.0, 1418.0, 1368.0, 1258.0, 1213.0, 1159.0, 1031.0, 985.0, 928.0, 874.0]
1H NMR: 7.26 (s, 1H), 7.16 (d, J = 8.4 Hz, 1H), 6.96 (dd, J = 8.4, 2.8 Hz, 1H), 4.13 (q, J = 7.2 Hz, 2H), 3.84 (s, 3H), 3.82 (s, 2H), 2.89 (t, J = 7.6 Hz, 2H), 1.71-1.64 (m, 2H), 1.34-1.23 (m, 13H), 0.87 (t, J = 6.4 Hz, 3H); 13C{1H} NMR (100 MHz, CDCl3): δ 203.8, 171.9, 158.5, 138.8, 133.4, 126.0, 115.9, 115.5, 60.6, 55.5, 40.8, 39.1, 31.8, 29.4, 29.3, 29.1, 24.2, 22.6, 14.2, 14.1
13C NMR: δ 203.8 (1C, s), 171.9 (1C, s), 158.5 (1C, s), 138.8 (1C, s), 133.4 (1C, s), 126.0 (1C, s), 115.9 (1C, s), 115.5 (1C, s), 60.6 (1C, s), 55.5 (1C, s), 40.8 (1C, s), 39.1 (1C, s), 31.8 (1C, s), 29.4 (1C, s), 29.3 (1C, s), 29.1 (1C, s), 24.2 (1C, s), 22.6 (1C, s), 14.2 (1C, s), 14.1 (1C, s)

### M004
Molecular formula: C29H28N2OS
IR bands (cm-1): [3106.0, 2932.0, 1688.0, 1492.0, 1356.0, 1149.0, 1028.0, 972.0, 855.0]
1H NMR: 7.64 (dd, J = 1.2, 8.4 Hz, 2H), 7.47 (t, J = 7.8 Hz, 2H), 7.34 (d, J = 7.2 Hz, 2H), 7.29 (t, J = 7.8 Hz, 1H), 7.26 (d, J = 7.2 Hz, 1H), 7.23 (t, J = 7.2 Hz, 2H), 7.13 (d, J = 7.8 Hz, 1H), 7.09 (d, J = 6.0 Hz, 1H), 7.06 (d, J = 7.2 Hz, 1H), 6.94 (d, J = 7.2 Hz, 1H), 5.67 (d, J = 1.2 Hz, 1H), 5.64 (d, J = 1.2 Hz, 1H), 5.44 (s, 1H), 5.05 (s, 1H), 2.26 (t, J = 7.8 Hz, 2H), 2.25 (s, 3H), 2.06 (t, J = 7.8 Hz, 2H), 1.95 (s, 3H); 13C{1H} NMR (150 MHz, CDCl3): δ 164.6, 155.5, 145.1, 140.1, 138.4, 137.2, 136.0, 130.0, 129.5, 129.3, 128.7, 128.0, 127.8, 127.8, 127.7, 126.3, 124.1, 118.5, 117.8, 114.3, 31.3, 31.1, 21.2, 15.3
13C NMR: δ 164.6 (1C, s), 155.5 (1C, s), 145.1 (1C, s), 140.1 (1C, s), 138.4 (1C, s), 137.2 (1C, s), 136.0 (1C, s), 130.0 (1C, s), 129.5 (1C, s), 129.3 (1C, s), 128.7 (1C, s), 128.0 (1C, s), 127.8 (1C, s), 127.8 (1C, s), 127.7 (1C, s), 126.3 (1C, s), 124.1 (1C, s), 118.5 (1C, s), 117.8 (1C, s), 114.3 (1C, s), 31.3 (1C, s), 31.1 (1C, s), 21.2 (1C, s), 15.3 (1C, s)

### M005
Molecular formula: C15H11NO
IR bands (cm-1): [2952.0, 1620.0, 1496.0, 1457.0, 1376.0, 1246.0, 1217.0, 1166.0, 950.0, 898.0, 763.0, 701.0]
1H NMR: 10.09 (s, 1H), 8.99 (d, J = 2 Hz, 1H), 8.41 (s, 1H), 7.89 (d, J = 9 Hz, 1H), 7.84 (d, J = 7.5 Hz, 2H), 7.53 (dd, J = 7.5, 7.5 Hz, 2H), 7.44 (dd, J = 7.5, 7.5 Hz, 1H), 7.31 (dd, J = 2, 9 Hz, 1H), 7.23 (d, J = 2 Hz, 1H)
13C NMR: δ 155.9 (1C, s), 146.1 (1C, s), 142.2 (1C, s), 137.4 (1C, s), 132.8 (1C, s), 131.1 (1C, s), 130.1 (1C, s), 129.2 (1C, s), 128.0 (1C, s), 127.1 (1C, s), 122.0 (1C, s), 108.7 (1C, s)

### M006
Molecular formula: C25H22N6S2
IR bands (cm-1): [3367.0, 1625.0, 1533.0, 1486.0, 1454.0, 1421.0, 1380.0]
1H NMR: 11.31 (s, 1H), 7.37 (d, J = 8.0 Hz, 2H), 7.22-7.20 (m, 1H), 7.15-7.14 (m, 1H), 7.07 (d, J = 8.4 Hz, 2H), 6.81-6.79 (m, 1H), 6.75-6.73 (m, 2H), 6.59-6.58 (m, 1H), 4.88 (s, 2H), 3.91 (s, 3H), 3.65 (s, 3H), 2.23 (s, 3H)
13C NMR: δ 147.2 (1C, s), 144.9 (1C, s), 143.2 (1C, s), 138.1 (1C, s), 138.0 (1C, s), 135.9 (1C, s), 135.2 (1C, s), 135.0 (1C, s), 131.3 (1C, s), 129.4 (1C, s), 127.7 (1C, s), 127.4 (1C, s), 126.2 (1C, s), 124.1 (1C, s), 124.0 (1C, s), 122.9 (1C, s), 114.8 (1C, s), 100.1 (1C, s), 94.4 (1C, s), 36.1 (1C, s), 35.2 (1C, s), 21.1 (1C, s)
