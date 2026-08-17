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

### M013
Molecular formula: C22H21F2NO
IR bands (cm-1): [3450.0, 2875.0, 1675.0, 1600.0, 1508.0, 1030.0, 759.0]
1H NMR: 7.74 (s, 2H, Hβ và Hβ′), 7.42-7.36 (m, 4H, H-Ar), 7.15-7.09 (m, 4H, H-Ar), 3.83 (s, 4H, H8 và H8′), 2.94 (hept, J = 6.5 Hz, 1H, H9), 1.06 (d, J = 6.5 Hz, 6H, H10 và H10′)
13C NMR: δ 187.7 (1C, s), 162.9 (1C, s), 134.8 (1C, s), 133.7 (1C, s), 132.2 (1C, s), 131.6 (1C, s), 115.8 (1C, s), 53.63 (1C, s), 50.4 (1C, s), 18.5 (1C, s)

### M014
Molecular formula: C21H13F3N2OS
IR bands (cm-1): [3011.0, 1688.0, 1716.0, 1596.0, 1300.0]
1H NMR: 13.56 (s, 1H), 9.21 (d, J = 8.8 Hz, 1H), 8.25-8.21 (m, 2H), 8.12 (s, 1H), 8.00 (dd, J = 26.1, 8.0 Hz, 2H), 7.76 (d, J = 7.6 Hz, 1H), 7.67-7.56 (m, 4H), 7.49 (t, J = 7.5 Hz, 1H) ppm; 13C{1H} NMR (125 MHz, DMSO-d6): δ 162.9, 161.8, 147.8, 136.4, 130.3, 128.6, 127.6, 124.0, 123.1, 122.3, 122.0, 121.7, 117.7, 117.0, 116.3, 114.5 ppm
13C NMR: δ 162.9 (1C, s), 161.8 (1C, s), 147.8 (1C, s), 136.4 (1C, s), 130.3 (1C, s), 128.6 (1C, s), 127.6 (1C, s), 124.0 (1C, s), 123.1 (1C, s), 122.3 (1C, s), 122.0 (1C, s), 121.7 (1C, s), 117.7 (1C, s), 117.0 (1C, s), 116.3 (1C, s)

### M015
Molecular formula: C23H18F3NO4
IR bands (cm-1): [3450.0, 2852.0, 2806.0, 2732.0, 1657.0, 1597.0, 1383.0, 1352.0, 1269.0, 786.0, 763.0]
1H NMR: 8.60 (s, 1H), 8.44 (s, 1H), 7.96 (d, J = 8.4 Hz, 1H), 7.80 (d, J = 9.2 Hz, 1H), 7.50-7.44 (m, 2H), 7.40 (d, J = 8.4 Hz, 1H), 7.31 (dd, J = 9.2, 2.7 Hz, 1H), 7.25-7.17 (m, 2H), 6.98 (d, J = 2.7 Hz, 1H), 4.50 (d, J = 14.6 Hz, 1H), 4.10 (dd, J = 7.0, 2.9 Hz, 2H), 3.67 (d, J = 14.6 Hz, 1H), 1.45 (t, J = 7.0 Hz, 3H)
13C NMR: δ 159.2 (1C, s), 157.2 (1C, s), 155.2 (1C, s), 154.0 (1C, s), 146.0 (1C, s), 142.2 (1C, s), 136.4 (1C, s), 132.3 (1C, s), 129.5 (1C, s), 128.6 (1C, s), 128.2 (1C, s), 126.0 (1C, s), 124.9 (1C, s), 124.6 (1C, q), 124.4 (1C, s), 123.2 (1C, s), 118.7 (1C, s), 116.1 (1C, s), 105.7 (1C, s), 76.8 (1C, q), 63.9 (1C, s), 37.1 (1C, s), 14.7 (1C, s)

### M016
Molecular formula: C35H51N11
IR bands (cm-1): [3109.0, 3057.0, 2937.0, 2794.0, 1558.0, 1457.0, 1296.0, 1161.0, 1051.0, 814.0, 705.0]
1H NMR: 7.41-7.30 (m, 5-H), 7.02 (d, J = 6.4 Hz, 2-H), 5.30 (s, 4-H), 2.64; (t, J = 7.3 Hz, 4-H), 2.56 (br s, 6-H), 2.50 (br s, 8-H), 2.37 (t, J = 7.0 Hz, 4-H), 2.28 (br s, 6-H), 1.80 (quint, J = 7.3 Hz, 4-H) ppm
13C NMR: δ 159.5 (1C, s), 154.2 (1C, s), 148.4 (1C, s), 136.8 (1C, s), 130.0 (1C, s), 129.8 (1C, s), 129.3 (1C, s), 126.2 (1C, s), 123.2 (1C, s), 58.6 (1C, s), 55.5 (1C, s), 53.6 (1C, s), 49.5 (1C, s), 45.9 (1C, s), 27.2 (1C, s), 24.0 (1C, s)

### M017
Molecular formula: C16H16N2
IR bands (cm-1): [3059.0, 2965.0, 2876.0, 1647.0, 1523.0, 1282.0, 1249.0]
1H NMR: 7.75-7.78 (m, 2 H), 7.68 (d, J = 7.5 Hz, 1 H), 7.64 (d, J = 7.5 Hz, 1 H), 7.55-7.60 (m, 3 H), 7.28 (td, J = 1.2 Hz, J = 7.3 Hz, 1 H), 7.24 (td, J = 1.2 Hz, J = 7.3 Hz, 1 H), 4.26 (t, J = 8.0 Hz, 2 H), 1.68 (sextet, J = 7.5 Hz, 2 H), 0.72 (t, J = 7.5 Hz, 3 H) ppm. 13C{1H} NMR (DMSO-d6, 125 MHz): δ = 153.0, 142.6, 135.6, 130.6, 129.6, 129.1, 128.7, 122.3, 121.8, 119.1, 110.8, 45.5, 22.5, 10.8 ppm
13C NMR: δ 153.0 (1C, s), 142.6 (1C, s), 135.6 (1C, s), 130.6 (1C, s), 129.6 (1C, s), 129.1 (1C, s), 128.7 (1C, s), 122.3 (1C, s), 121.8 (1C, s), 119.1 (1C, s), 110.8 (1C, s), 45.5 (1C, s), 22.5 (1C, s)

### M018
Molecular formula: C34H29NO
IR bands (cm-1): [2974.0, 1634.0, 1624.0, 1424.0, 1285.0, 1094.0, 1068.0, 889.0, 811.0, 748.0]
1H NMR: 8.86 (br s, 1H), 8.78 (d, J = 8.3 Hz, 1H), 8.77 (d, J = 9.2 Hz, 1H), 8.75 (d, J = 9.1 Hz, 1H), 8.05 (d, J = 9.0 Hz, 1H), 8.03-7.99 (m, 2H), 7.97 (s, 1H), 7.83 (br d, J = 7.8 Hz, 2H), 7.79 (s, 1H), 7.75-7.71 (m, 1H), 7.68-7.65 (m, 1H), 7.52-7.44 (m, 2H), 3.77-2.92 (br m, 4H), 2.50 (s, 3H), 0.96 (br s, 3H), 0.57 (t, J = 7.1 Hz, 3H). 13C{1H} NMR (100 MHz, CDCl3): δ = 170.3, 136.3, 133.3, 132.4, 131.8, 131.5, 130.5, 130.0, 129.6, 128.7 (2C), 128.6, 128.1, 127.9 (2C), 127.0 (2C), 126.9 (2C), 126.7, 126.2, 125.5, 123.2, 122.4, 121.1, 42.7, 38.2, 21.1, 13.9, 11.8
13C NMR: δ 170.3 (1C, s), 136.3 (1C, s), 133.3 (1C, s), 132.4 (1C, s), 131.8 (1C, s), 131.5 (1C, s), 130.5 (1C, s), 130.0 (1C, s), 129.6 (1C, s), 128.7 (1C, s), 128.6 (1C, s), 128.1 (1C, s), 127.9 (1C, s), 127.0 (1C, s), 126.9 (1C, s), 126.7 (1C, s), 126.2 (1C, s), 125.5 (1C, s), 123.2 (1C, s), 122.4 (1C, s), 121.1 (1C, s), 42.7 (1C, s), 38.2 (1C, s), 21.1 (1C, s), 13.9 (1C, s), 11.8 (1C, s)
