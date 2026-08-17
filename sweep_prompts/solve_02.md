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

### M007
Molecular formula: C27H38O3Si
IR bands (cm-1): [2956.0, 2858.0, 1735.0, 1445.0, 1428.0, 1156.0, 822.0, 737.0, 701.0, 649.0]
1H NMR: 7.67 (d, J = 6.5 Hz, 4H), 7.45-7.33 (m, 6H), 5.12 (t, J = 1.4 Hz, 1H), 4.11 (q, J = 7.1 Hz, 2H), 3.64 (t, J = 6.3 Hz, 2H), 2.37 (t, J = 6.1 Hz, 2H), 2.30-2.24 (m, 2H), 2.07 (q, J = 7.4 Hz, 2H), 1.64-1.55 (m, 5H), 1.24 (t, J = 7.1 Hz, 3H), 1.05 (s, 9H)
13C NMR: δ 173.5 (1C, s), 135.5 (1C, s), 134.0 (1C, s), 133.7 (1C, s), 129.5 (1C, s), 127.6 (1C, s), 124.8 (1C, s), 63.3 (1C, s), 60.2 (1C, s), 34.7 (1C, s), 33.2 (1C, s), 32.6 (1C, s), 26.8 (1C, s), 24.1 (1C, s), 19.2 (1C, s), 15.9 (1C, s), 14.3 (1C, s)

### M008
Molecular formula: C32H31N3O2
IR bands (cm-1): [2956.0, 2932.0, 2832.0, 1597.0, 1582.0, 1493.0, 1462.0, 1423.0, 1258.0, 1239.0, 1122.0, 1056.0, 1025.0, 1005.0, 974.0, 866.0, 837.0, 801.0, 756.0, 736.0]
1H NMR: 0.71 (t, J = 7.6 Hz, 3H, CH3), 1.10 (sext, J = 7.6 Hz, 2H, CH2), 1.49 (quin, J = 7.6 Hz, 2H, CH2), 3.85 (s, 6H, 2 × OCH3), 4.20 (t, J = 7.6 Hz, 2H, CH2), 7.02 (d, J = 7.6 Hz, 2H, ArH), 7.07 (t, J = 7.6 Hz, 2H, ArH), 7.35-7.40 (m, 4H, ArH), 7.70 (d, J = 8.4 Hz, 4H, ArH), 7.73 (d, J = 8.4 Hz, 4H, ArH)
13C NMR: δ 13.2 (1C, s), 19.4 (1C, s), 32.0 (1C, s), 44.8 (1C, s), 55.6 (1C, s), 111.5 (1C, s), 121.0 (1C, s), 126.3 (1C, s), 128.5 (1C, s), 129.2 (1C, s), 129.7 (1C, s), 130.0 (1C, s), 130.8 (1C, s), 140.3 (1C, s), 155.5 (1C, s), 156.5 (1C, s)

### M009
Molecular formula: C25H18FNO2
IR bands (cm-1): [3040.0, 1691.0, 1658.0, 1642.0, 1574.0, 1489.0, 1406.0, 1102.0, 755.0, 702.0]
1H NMR: 7.99 (d, J = 7.8 Hz, 1H), 7.65 (t, J = 7.9 Hz, 1H), 7.51 (d, J = 10.3 Hz, 1H), 7.45-7.19 (m, 9H), 7.00-6.85 (m, 1H), 5.62 (s, 1H), 5.35 (s, 1H), 3.64 (s, 3H)
13C NMR: δ 162.87 (1C, d), 160.15 (1C, s), 159.81 (1C, s), 159.48 (1C, s), 140.96 (1C, s), 140.33 (1C, s), 136.59 (1C, d), 131.67 (1C, s), 129.73 (1C, d), 128.81 (1C, s), 128.02 (1C, s), 127.47 (1C, s), 124.13 (1C, d), 123.13 (1C, s), 122.10 (1C, s), 114.97 (1C, s), 114.75 (1C, s), 113.41 (1C, d), 111.77 (1C, s), 111.26 (1C, s), 105.41 (1C, d), 51.34 (1C, s), 29.07 (1C, s)

### M010
Molecular formula: C44H52F6N4O6
IR bands (cm-1): [3420.0, 3280.0, 3065.0, 3028.0, 2938.0, 2849.0, 2497.0, 1672.0, 1641.0, 1199.0, 1175.0, 1126.0, 719.0, 699.0]
1H NMR: 8.53-8.43 (4H, br s, NH2-12), 8.18 (2H, t, J = 5.9 Hz, NH-8), 7.32-7.25 (16H, m, H-5, H-6), 7.20-7.14 (4H, m, H-7), 4.48 (2H, t, J = 8.1 Hz, H-3), 3.05 (4H, dt, J = 6.4, 6.2 Hz, H2-9), 2.88 (4H, d, J = 8.1 Hz, H2-2), 2.75-2.67 (4H, br s, H2-13), 2.58-2.52 (4H, m, H2-11), 1.61-1.56 (4H, m, H2-10), 1.56-1.51 (4H, m, H2-14)
13C NMR: δ 171.0 (1C, s), 144.1 (1C, s), 128.4 (1C, s), 127.5 (1C, s), 126.2 (1C, s), 46.8 (1C, s), 46.1 (1C, s), 44.2 (1C, s), 41.1 (1C, s), 35.2 (1C, s), 26.0 (1C, s)

### M011
Molecular formula: C17H12FN3O4
IR bands (cm-1): [3174.0, 3070.0, 2987.0, 2937.0, 2868.0, 2376.0, 2314.0, 1668.0, 1608.0, 1531.0, 1489.0, 1411.0, 1342.0]
1H NMR: 6.69 (t, J = 6.0 Hz, 1H, Ar-H), 7.17-7.26 (m, 2 H, Ar-H), 7.35-7.38 (m, 1H, Ar-H), 7.94 (d, J = 12.4 Hz, 1H, Ar-H), 7.75-7.89 (m, 1H, Ar-H), 8.04 (d, J = 8.8 Hz, 1H, Ar-H) ppm
13C NMR: δ 102.3 (1C, s), 106.6 (1C, s), 107.5 (1C, s), 108.6 (1C, s), 115.3 (1C, s), 117.6 (1C, s), 126.9 (1C, s), 128.2 (1C, s), 130.1 (1C, s), 148.5 (1C, s), 150.5 (1C, s), 161.7 (1C, s), 164.1 (1C, s), 169.8 (1C, s), 174.6 (1C, s)

### M012
Molecular formula: C22H21N3O3
IR bands (cm-1): [3200.0, 3100.0, 3028.0, 2990.0, 2954.0, 1685.0, 1604.0, 1273.0, 748.0]
1H NMR: 11.88, 11.50 (2s, 1H, OH, D2O exchangeable), 11.13, 11.04 (2s, 1H, OH/NH, D2O exchangeable), 8.43, 8.34 (2s, 1H, N = CH), 7.73-7.69, 7.55-7.53 (2 m, 1H, ArH), 7.63 (dd, J = 2.4, 8.4 Hz, 2H, ArH), 7.31 (dd, J = 3.2, 8.4 Hz, 2H, ArH), 7.27-7.23 & 7.00-6.96 (2 m, 1H, ArH), 6.93-6.85 (m, 2H, ArH) 6.59 (t, J = 4.4 Hz, 1H, C4H-pyrrole), 6.15, 6.12 (2d, J = 4.4, 4.4 Hz, 1H, C3H-pyrrole), 4.16, 3.78 (2s, 2H, CH2C=O) 3.90, 3.87 (2s, 3H, N-CH3), 2.39 (s, 3H, ArCH3)
13C NMR: δ 184.8 (1C, s), 184.7 (1C, s), 170.3 (1C, s), 164.9 (1C, s), 157.7 (1C, s), 156.8 (1C, s), 147.5 (1C, s), 142.0 (1C, s), 141.8 (1C, s), 141.6 (1C, s), 137.7 (1C, s), 137.5 (1C, s), 137.4 (1C, s), 137.1 (1C, s), 131.8 (1C, s), 131.6 (1C, s), 130.8 (1C, s), 130.6 (1C, s), 129.7 (1C, s), 129.4 (1C, s), 129.3 (1C, s), 129.2 (1C, s), 129.1 (1C, s), 122.2 (1C, s), 122.1 (1C, s), 120.5 (1C, s), 119.9 (1C, s), 119.8 (1C, s), 119.0 (1C, s), 116.8 (1C, s), 116.6 (1C, s), 110.0 (1C, s), 109.8 (1C, s), 33.5 (1C, s), 33.4 (1C, s), 32.8 (1C, s), 31.2 (1C, s), 21.5 (1C, s)
