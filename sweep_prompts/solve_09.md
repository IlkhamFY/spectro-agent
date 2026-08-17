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

### M049
Molecular formula: C9H10N2
IR bands (cm-1): [3351.0, 3054.0, 2874.0, 1663.0, 1603.0, 1507.0, 1386.0, 1326.0, 1254.0, 877.0, 753.0]
1H NMR: 8.22 (s, 1H), 7.19 (t, J = 7.9 Hz, 2H), 6.73 (t, J = 7.3 Hz, 1H), 6.63 (d, J = 7.7 Hz, 2H), 3.56 (dd, J = 11.6, 5.9 Hz, 2H), 3.33 (t, J = 5.8 Hz, 2H)
13C NMR: δ 161.9 (1C, s), 147.9 (1C, s), 129.5 (1C, s), 118.1 (1C, s), 113.0 (1C, s), 43.9 (1C, s), 37.9 (1C, s)

### M050
Molecular formula: C10H11NO4
IR bands (cm-1): [3111.0, 3089.0, 3039.0, 2927.0, 2900.0, 1520.0, 1338.0, 1309.0, 1196.0, 1176.0, 1032.0, 1005.0, 972.0, 937.0, 870.0, 731.0]
1H NMR: 8.07 (dd, J = 8.3, 1.4 Hz, 1H), 7.82 (dd, J = 7.8, 1.3 Hz, 1H), 7.66 (td, J = 7.6, 1.4 Hz, 1H), 7.46 (td, J = 7.8, 1.5 Hz, 1H), 4.84-4.79 (m, 3H), 4.70 (dq, J = 10.9, 5.1 Hz, 3H); 13C{1H} NMR (101 MHz, CDCl3) δ 147.2, 134.2, 133.9, 128.8, 128.4, 124.8, 78.5 (2C), 72.8, 67.4
13C NMR: δ 147.2 (1C, s), 134.2 (1C, s), 133.9 (1C, s), 128.8 (1C, s), 128.4 (1C, s), 124.8 (1C, s), 78.5 (1C, s), 72.8 (1C, s), 67.4 (1C, s)

### M051
Molecular formula: C9H8BrClN2O
IR bands (cm-1): [3248.0, 1687.0, 1595.0, 1543.0, 1481.0, 1357.0, 1225.0, 1071.0, 1027.0, 935.0, 828.0, 578.0, 504.0]
1H NMR: 8.45 (broad s, 1H, NH), 7.46 (d, J = 8.8 Hz, 2H, Ar-H), 7.12 (d, J = 8.8 Hz, 2H, Ar-H), 2.56 (s, 3H, CH3)
13C NMR: δ 188.2 (1C, s), 140.4 (1C, s), 132.5 (1C, s), 125.9 (1C, s), 116.0 (1C, s), 115.9 (1C, s)

### M052
Molecular formula: C14H13BrO3
IR bands (cm-1): [3063.0, 2999.0, 2955.0, 2833.0, 1600.0, 1580.0, 1510.0, 1470.0, 1440.0, 1260.0, 1229.0, 1150.0, 1045.0, 1028.0, 959.0, 854.0, 754.0]
1H NMR: 7.61 (dd, J = 8.0 Hz, 1.5 Hz, 1H), 7.21 (td, J = 7.8 Hz, 1.3 Hz, 1H), 6.95 (td, J = 7.7 Hz, 1.4 Hz, 1H), 6.86 (dd, J = 8.2 Hz, 1.4 Hz, 1H), 6.81 (d, J = 8.7 Hz, 1H), 6.66 (d, J = 2.7 Hz, 1H), 6.50 (dd, J = 8.7 Hz, 2.7 Hz, 1H), 3.87 (s, 3H), 3.84 (s, 3H); 13C{1H} NMR (75 MHz, CDCl3): δ 154.6, 150.1, 149.9, 145.6, 133.6, 128.5, 124.1, 118.8, 113.6, 111.6, 110.0, 104.0, 56.2, 55.9
13C NMR: δ 154.6 (1C, s), 150.1 (1C, s), 149.9 (1C, s), 145.6 (1C, s), 133.6 (1C, s), 128.5 (1C, s), 124.1 (1C, s), 118.8 (1C, s), 113.6 (1C, s), 111.6 (1C, s), 110.0 (1C, s), 104.0 (1C, s), 56.2 (1C, s), 55.9 (1C, s)

### M053
Molecular formula: C17H15FO
IR bands (cm-1): [3306.0, 3297.0, 2975.0, 2957.0, 2931.0, 1607.0, 1492.0]
1H NMR: 7.62 (d, J = 7.8 Hz, 1H), 7.56-7.49 (m, 2H), 7.15-7.08 (m, 3H), 6.99 (d, J = 1.7 Hz, 1H), 4.21 (qd, J = 7.0, 2.4 Hz, 1H), 3.90 (s, 3H), 2.23 (d, J = 2.5 Hz, 1H), 1.48 (d, J = 7.1 Hz, 3H)
13C NMR: δ 162.6 (1C, d), 140.5 (1C, s), 137.5 (1C, s), 130.3 (1C, s), 128.8 (1C, d), 128.3 (1C, s), 119.7 (1C, s), 115.7 (1C, d), 109.5 (1C, s), 87.7 (1C, s), 69.6 (1C, s), 55.7 (1C, s), 25.3 (1C, s), 22.8 (1C, s)

### M054
Molecular formula: C10H14N2O
IR bands (cm-1): [2966.0, 1679.0, 1522.0, 1461.0, 1365.0, 1231.0, 998.0, 751.0, 621.0]
1H NMR: 8.21 (s, 1H), 7.90-7.89 (d, J = 7.8 Hz, 1H), 7.86-7.84 (t, J = 6.6 Hz, 2H), 7.79-7.77 (m, 1H), 7.55-7.51 (m, 2H), 6.23 (br s, 1H), 1.52 (s, 9H)
13C NMR: δ 163.6 (1C, s), 151.0 (1C, s), 147.9 (1C, s), 137.9 (1C, s), 126.0 (1C, s), 121.9 (1C, s), 51.0 (1C, s), 28.9 (1C, s)
