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

### M043
Molecular formula: C12H12Cl2O2
IR bands (cm-1): [3005.0, 2938.0, 1686.0, 1597.0, 1584.0, 1427.0, 1317.0, 1269.0, 1242.0, 1045.0, 866.0, 773.0]
1H NMR: 1.49 (d, J = 7.5 Hz, 1H), 1.65 (s, 3H), 2.29 (d, J = 7.5 Hz, 1H), 3.89 (s, 3H), 7.15-7.18 (m, 1H), 7.44-7.48 (m, 2H), 7.54-7.55 (m, 1H); 13C{1H} NMR (125 MHz, CDCl3): δ = 20.8, 29.6, 39.8, 55.4, 62.5, 113.7, 120.1, 122.3, 129.7, 135.8, 159.9, 195.3
13C NMR: δ 20.8 (1C, s), 29.6 (1C, s), 39.8 (1C, s), 55.4 (1C, s), 62.5 (1C, s), 113.7 (1C, s), 120.1 (1C, s), 122.3 (1C, s), 129.7 (1C, s), 135.8 (1C, s), 159.9 (1C, s), 195.3 (1C, s)

### M044
Molecular formula: C12H12O3
IR bands (cm-1): [2831.0, 2750.0, 2235.0, 1694.0]
1H NMR: 10.60 (s, 1H), 7.39 (t, J = 8.1 Hz, 1H), 7.15 (d, J = 7.1, 1H), 7.13 (d, J = 7.3, 1H), 5.27 (s, 2H), 3.50 (s, 3H), 2.12 (s, 3H); 13C{1H} NMR (101 MHz, CDCl3) δ 190.7, 158.5, 134.2, 127.53, 127.49, 126.3, 115.1, 95.0, 93.2, 77.1, 56.6, 4.9
13C NMR: δ 190.7 (1C, s), 158.5 (1C, s), 134.2 (1C, s), 127.53 (1C, s), 127.49 (1C, s), 126.3 (1C, s), 115.1 (1C, s), 95.0 (1C, s), 93.2 (1C, s), 77.1 (1C, s), 56.6 (1C, s), 4.9 (1C, s)

### M045
Molecular formula: C17H26O3
IR bands (cm-1): [3451.0, 2940.0, 2862.0, 1713.0, 1516.0, 1452.0, 1367.0, 1267.0, 1036.0, 804.0]
1H NMR: 6.80 (1H, d, J = 8.0 Hz, H-5′), 6.67 (1H, d, J = 1.8 Hz, H-2′), 6.64 (1H, dd, J = 8.0, 1.8 Hz, H-6′), 3.85 (3H, s, -OCH3), 2.86-2.63 (4H, m, H-1, -2), 2.36 (2H, t, J = 7.4 Hz, H-4), 1.58-1.51 (2H, m, H-5), 1.24 (8H, m, H-6~9), 0.88 (3H, t, J = 6.2 Hz, H-10)
13C NMR: δ 210.6 (1C, s), 146.3 (1C, s), 143.8 (1C, s), 133.1 (1C, s), 120.7 (1C, s), 114.3 (1C, s), 111.0 (1C, s), 55.8 (1C, s), 44.6 (1C, s), 43.1 (1C, s), 31.6 (1C, s), 29.5 (1C, s), 29.1 (1C, s), 29.0 (1C, s), 23.8 (1C, s), 22.5 (1C, s)

### M046
Molecular formula: C13H13ClN2O3S
IR bands (cm-1): [3344.0, 3324.0, 3253.0, 3111.0, 3078.0, 2860.0, 2995.0, 1617.0, 1325.0, 1315.0, 1153.0, 1138.0]
1H NMR: 3.00-5.00 (2H, broad, Ar-OH and N-H), 7.22-7.16 (4H, m, Ar-H and -SO2NH2), 7.11-7.09 (1H, d, J = 8, Ar-H), 7.02 (1H, s, Ar-H), 6.96-6.94 (1H, t, J = 8, Ar-H), 6.78-6.74 (1H, t, J = 8, Ar-H), 6.68-6.66 (1H, t, J = 8, Ar-H), 4.27 (2H, s, Ar-CH2)
13C NMR: δ 151.03 (1C, s), 149.20 (1C, s), 145.17 (1C, s), 130.28 (1C, s), 129.00 (1C, s), 127.46 (1C, s), 121.10 (1C, s), 119.83 (1C, s), 114.52 (1C, s), 113.34 (1C, s), 112.31 (1C, s), 109.62 (1C, s), 42.18 (1C, s)

### M047
Molecular formula: C14H14BrNO3S
IR bands (cm-1): [3273.0, 2920.0, 1402.0, 1065.0, 676.0]
1H NMR: 3.45 (bs, 1H, OH, D2O exch.), 4.14 (d, 2H, J = 6.4 Hz, CH2), 4.93 (s, 2H, CH2), 6.18 (m, 1H, NH, D2O exch.), 7.03 (t, 1H, J = 7.6 Hz, CHAr), 7.15 (t, 1H, J = 7.4 Hz, CHAr), 7.28 (d, 1H, J = 6.8 Hz, CHAr), 7.33-7.49 (m, 4H, CHAr), 7.87 (d, 1H, J = 8.0 Hz, CHAr)
13C NMR: δ 47.4 (1C, s), 63.5 (1C, s), 123.4 (1C, s), 127.6 (1C, s), 128.3 (1C, s), 129.4 (1C, s), 129.6 (1C, s), 130.3 (1C, s), 131.3 (1C, s), 132.7 (1C, s), 133.1 (1C, s), 135.6 (1C, s), 137.8 (1C, s), 138.4 (1C, s)

### M048
Molecular formula: C18H14O2
IR bands (cm-1): [3059.0, 1735.0, 1677.0, 1658.0, 1612.0, 1450.0, 1222.0, 1141.0, 698.0]
1H NMR: 7.95 (d, J = 7.2 Hz, 2H), 7.65 (t, J = 10.6 Hz, 1H), 7.52 (t, J = 7.7 Hz, 2H), 7.36-7.46 (m, 3H), 7.26-7.31 (m, 2H), 7.16 (d, J = 11.0 Hz, 1H), 6.48-6.61 (m, 1H), 5.71 (d, J = 16.9 Hz, 1H), 5.56 (d, J = 10.1 Hz, 1H)
13C NMR: δ 196.1 (1C, s), 195.1 (1C, s), 147.0 (1C, s), 138.5 (1C, s), 134.9 (1C, s), 133.3 (1C, s), 133.2 (1C, s), 132.8 (1C, s), 130.3 (1C, s), 129.9 (1C, s), 129.2 (1C, s), 129.1 (1C, s), 128.6 (1C, s), 128.5 (1C, s)
