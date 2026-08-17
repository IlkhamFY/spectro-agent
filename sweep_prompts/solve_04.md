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

### M019
Molecular formula: C24H32ClNO3S
IR bands (cm-1): [3254.0, 2925.0, 2854.0, 1703.0, 1587.0, 1476.0, 1333.0, 1162.0, 1089.0, 1014.0, 823.0, 755.0, 624.0, 537.0, 485.0]
1H NMR: 0.88 (t, 3H, J = 6.9 Hz, C11′), 1.08-1.38 (m, 18H, C2′-C10′), 2.62 (t, 2H, J = 7.9 Hz, C1′), 7.17-7.25 (m, 2H, C3, C5), 7.32-7.44 (m, 2H, C4, C6), 7.49-7.59 (m, 2H, C3″, C5″), 8.04-8.14 (m, 2H, C2″, C6″), 8.59 (s, 1H, N-H)
13C NMR: δ 14.2 (1C, s), 22.7 (1C, s), 29.3 (1C, s), 29.4 (1C, s), 29.5 (1C, s), 29.6 (1C, s), 29.7 (1C, s), 31.7 (1C, s), 31.9 (1C, s), 33.2 (1C, s), 126.0 (1C, s), 127.1 (1C, s), 129.3 (1C, s), 130.1 (1C, s), 130.9 (1C, s), 131.8 (1C, s), 131.9 (1C, s), 136.8 (1C, s), 140.8 (1C, s), 142.8 (1C, s), 166.4 (1C, s)

### M020
Molecular formula: C15H15ClF2O3SSi
IR bands (cm-1): [3092.0, 2957.0, 2900.0, 1606.0, 1585.0, 1494.0, 1381.0, 1190.0, 1087.0, 1018.0, 840.0, 611.0, 486.0]
1H NMR: 7.91 (d, J = 8.6 Hz, 2H), 7.58 (d, J = 8.6 Hz, 2H), 7.21 (t, J = 9.7 Hz, 1H), 7.02 (dd, J = 10.9 Hz, 6.2 Hz, 1H), 0.25 (s, 9H); 13C{1H} NMR (75 MHz, CDCl3): δ 150.3 (dd, J = 252.0 Hz, 14.3 Hz, ArF), 149.5 (dd, J = 7.5 Hz, 3.0 Hz, ArF), 148.5 (dd, J = 248.6 Hz, 11.6 Hz, ArF), 141.4, 134.6, 129.8, 129.8 (d, J = 2.3 Hz, ArF), 129.7, 123.2 (d, J = 15.8 Hz, ArF), 109.8 (d, J = 20.3 Hz, ArF), -0.9
13C NMR: δ 150.3 (1C, dd), 149.5 (1C, dd), 148.5 (1C, dd), 141.4 (1C, s), 134.6 (1C, s), 129.8 (1C, s), 129.8 (1C, d), 129.7 (1C, s), 123.2 (1C, d), 109.8 (1C, d), -0.9 (1C, s)

### M021
Molecular formula: C16H13ClN2O
IR bands (cm-1): [3319.0, 1683.0, 1569.0, 1463.0]
1H NMR: 9.42 (s, 1H, NH), 9.12 (s, 1H, NH), 7.19-7.78 (m, 9H, Ar-H), 5.60 (d, 1H, J = 4.3 Hz, C=CH), 5.01 (d,1H, J = 4.3 Hz, CH)
13C NMR: δ 150.2 (1C, s), 141.3 (1C, s), 136.6 (1C, s), 134.2 (1C, s), 132.3 (1C, s), 128.6 (1C, s), 128.3 (1C, s), 128.7 (1C, s), 126.4 (1C, s), 97.5 (1C, s), 51.9 (1C, s)

### M022
Molecular formula: C14H11N3O3
IR bands (cm-1): [3296.0, 3193.0, 3074.0, 2923.0, 1652.0, 1610.0, 1530.0, 1485.0, 1352.0, 1257.0, 1153.0, 1033.0, 904.0, 752.0]
1H NMR: 8.57 (s, 1H), 8.39 (s, 1H), 8.22-8.19 (m, 1H), 7.97-7.95 (d, J = 8.0 Hz, 1H), 7.71-7.63 (m, 2H), 7.36 (s, 1H), 7.30-7.26 (m, 1H), 6.82-6.80 (d, J = 8.0 Hz, 1H), 6.72-6.69 (m, 1H), 5.98 (s, 1H)
13C NMR: δ 163.39 (1C, s), 147.68 (1C, s), 147.27 (1C, s), 144.24 (1C, s), 133.57 (1C, s), 133.32 (1C, s), 129.97 (1C, s), 127.41 (1C, s), 123.23 (1C, s), 121.55 (1C, s), 117.53 (1C, s), 114.91 (1C, s), 114.58 (1C, s), 65.19 (1C, s)

### M023
Molecular formula: C26H32N2O6Si
IR bands (cm-1): [2952.0, 1766.0, 1688.0, 1646.0, 1435.0, 1249.0, 1068.0, 837.0, 754.0]
1H NMR: 7.46-7.42 (2H, m), 7.41-7.32 (4H, m), 7.28 (1H, s), 5.46 (1H, d, J = 9.9 Hz), 5.22 (2H, dd, J = 14.3, 12.6 Hz), 4.61 (1H, dd, J = 9.9, 3.2 Hz), 4.54 (1H, d, J = 9.9 Hz), 4.23 (1H, m), 3.95 (3H, s), 3.88 (1H, m), 3.74-3.51 (3H, m), 2.77 (1H, ddd, J = 11.0, 9.9, 1.2 Hz), 0.87-0.81 (2H, m), 0.04 (9H, s). 13C{1H} NMR (100 MHz, CDCl3): δ 206.9, 168.8, 166.0, 151.4, 148.2, 135.9, 133.9, 128.9, 128.5, 127.6, 120.7, 111.6, 107.9, 78.3, 71.1, 67.3, 56.4, 54.9, 52.4, 37.4, 18.5, -1.2
13C NMR: δ 206.9 (1C, s), 168.8 (1C, s), 166.0 (1C, s), 151.4 (1C, s), 148.2 (1C, s), 135.9 (1C, s), 133.9 (1C, s), 128.9 (1C, s), 128.5 (1C, s), 127.6 (1C, s), 120.7 (1C, s), 111.6 (1C, s), 107.9 (1C, s), 78.3 (1C, s), 71.1 (1C, s), 67.3 (1C, s), 56.4 (1C, s), 54.9 (1C, s), 52.4 (1C, s), 37.4 (1C, s), 18.5 (1C, s), -1.2 (1C, s)

### M024
Molecular formula: C24H20BrN3O3S
IR bands (cm-1): [3045.0, 3276.0, 2921.0, 2852.0, 1713.0, 1614.0, 1545.0, 1468.0, 1373.0, 1330.0, 1268.0, 1181.0, 1155.0, 1094.0, 1012.0, 925.0]
1H NMR: 8.02 (s, 1H), 7.46-7.30 (m, 7H), 7.22 (dd, J = 17.8, 7.7 Hz, 2H), 7.05 (dd, J = 13.9, 6.9 Hz, 2H), 6.76 (s, 1H), 6.61 (s, 1H), 6.23 (s, 1H), 3.95 (s, 2H), 3.70 (s, 3H)
13C NMR: δ 147.6 (1C, s), 138.8 (1C, s), 137.3 (1C, s), 136.5 (1C, s), 133.0 (1C, s), 131.0 (1C, s), 128.7 (1C, s), 126.7 (1C, s), 126.3 (1C, s), 124.0 (1C, s), 123.6 (1C, s), 122.6 (1C, s), 122.1 (1C, s), 120.4 (1C, s), 120.0 (1C, s), 119.4 (1C, s), 119.4 (1C, s), 117.6 (1C, s), 115.6 (1C, s), 111.5 (1C, s), 109.5 (1C, s), 33.6 (1C, s), 32.8 (1C, s)
