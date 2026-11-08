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
  {"benchmark_expand_500:R17": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R17
Molecular formula: C25H20Cl2N4O2
IR bands (cm-1): [3416.0, 1663.0, 1616.0, 1582.0, 1499.0, 1314.0, 1011.0, 726.0]
1H NMR: 11.65 (s, 1H), 7.33 (d, J = 8.4 Hz, 2H), 7.28 (d, J = 8.4 Hz, 2H), 7.12 (d, J = 8.4 Hz, 2H), 7.02 (d, J = 8.4 Hz, 2H), 5.07 (s, 1H), 3.98 (s, 3H), 2.13 (s, 3H), 1.95 (s, 3H)
13C NMR: δ 190.2 (1C, s), 161.2 (1C, s), 156.4 (1C, s), 141.7 (1C, s), 138.6 (1C, s), 136.5 (1C, s), 133.3 (1C, s), 131.6 (1C, s), 130.2 (1C, s), 129.4 (1C, s), 129.0 (1C, s), 126.0 (1C, s), 111.6 (1C, s), 48.9 (1C, s), 34.1 (1C, s), 17.1 (1C, s), 15.3 (1C, s)

### benchmark_expand_500:R171
Molecular formula: C28H30N2O3
IR bands (cm-1): [3009.0, 2940.0, 1636.0, 1493.0, 1454.0, 1337.0, 1059.0, 698.0, 442.0, 442.0, 442.0, 620.0]
1H NMR: 7.34-7.22 (5H, m, 10-O-Bn-H), 7.13-7.04 (3H, m, 3-N-Bn-H), 6.75-6.73 (2H, m, 3-N-Bn-H), 6.75 (1H, s, 7-H), 4.98 (1H, d, J = 11.5 Hz, 10-OCH2Ph), 4.84 (1H, d, J = 15.1 Hz, 3-N-CH2Ph), 4.74 (1H, d, J = 11.5 Hz, 10-OCH2Ph), 4.10 (1H, d, J = 15.1 Hz, 3-N-CH2Ph), 3.89 (1H, brd, J = 4.4 Hz, 1-H), 3.68-3.65 (1H, m, 2-H), 3.68 (1H, d, J = 6.3 Hz, 5-H), 3.67 (3H, s, 9-OCH3), 3.16 (1H, dd, J = 17.1, 6.3 Hz, 6-H), 2.92 (1H, d, J = 11.7 Hz, 2-H), 2.86 (1H, d, J = 17.1 Hz, 6-H), 2.29 (3H, s, 11-N-CH3), 2.29 (3H, s, 8-CH3)
13C NMR: δ 170.2 (1C, s), 149.3 (1C, s), 148.3 (1C, s), 137.3 (1C, s), 136.3 (1C, s), 131.2 (1C, d), 128.4 (1C, d), 128.0 (1C, d), 128.2 (1C, s), 127.1 (1C, d), 126.8 (1C, d), 126.0 (1C, d), 125.6 (1C, s), 74.1 (1C, t), 59.9 (1C, q), 59.3 (1C, d), 51.5 (1C, d), 50.5 (1C, t), 48.5 (1C, t), 39.7 (1C, q), 27.4 (1C, t), 15.6 (1C, q)

### benchmark_expand_500:R172
Molecular formula: C32H46N2O7
IR bands (cm-1): [3442.0, 2922.0, 1735.0, 1687.0, 1457.0, 1418.0, 1366.0, 1291.0, 1253.0, 1160.0, 1072.0, 1047.0, 976.0, 837.0]
1H NMR: 8.89 (dd, J = 4.1 Hz, 1.6 Hz, 1H), 8.33 (dm, J = 8.3 Hz, 1H), 8.05 (br s, 1H), 7.95 (d, J = 8.4 Hz, 1H), 7.63 (dd, J = 8.4 Hz, 1.4 Hz, 1H), 7.50 (dd, J = 8.3 Hz, 4.2 Hz, 1H), 5.93 (m, 1H), 5.26 (d, J = 7.6 Hz, 1H, OH), 4.26 (d, J = 6.4 Hz, 1H, OH), 4.19 (m, 1H), 3.43 (m, 1H), 3.37 (m, 1H), 3.23 (m, 2H), 3.10 (m, 1H), 2.96 (m, 1H), 2.42 (dd, J = 14.4 Hz, 10.6 Hz, 1H), 2.11 (m, 2H), 1.55 (m, 1H), 1.43 (m, 1H), 1.33 (s, 9H), 1.32 (s, 3H), 1.30-1.16 (m, 4H), 1.02 (d, J = 6.7 Hz, 3H), 0.93 (s, 3H), 0.90 (d, J = 6.8 Hz, 3H)
13C NMR: δ 217.8 (1C, s), 170.5 (1C, s), 154.3 (1C, s), 150.6 (1C, s), 147.5 (1C, s), 141.7 (1C, s), 135.5 (1C, s), 128.0 (1C, s), 127.0 (1C, s), 125.1 (1C, s), 124.3 (1C, s), 121.2 (1C, s), 78.1 (1C, s), 74.0 (1C, s), 73.1 (1C, s), 71.3 (1C, s), 52.7 (1C, s), 47.0 (1C, s), 44.2 (1C, s), 42.2 (1C, s), 38.6 (1C, s), 36.0 (1C, s), 35.5 (1C, s), 27.9 (1C, s), 27.0 (1C, s), 24.7 (1C, s), 20.5 (1C, s), 20.0 (1C, s), 17.2 (1C, s), 14.1 (1C, s)

### benchmark_expand_500:R176
Molecular formula: C23H36O6
IR bands (cm-1): [2955.0, 2930.0, 2855.0, 1735.0, 1683.0, 1593.0, 1568.0, 1495.0, 1454.0, 1403.0, 1332.0, 1289.0, 1164.0, 1136.0, 1115.0, 1047.0, 1005.0, 967.0, 918.0, 837.0]
1H NMR: 7.02 (s, 1H), 4.08 (t, J = 6.8 Hz, 2H), 3.90 (s, 3H), 3.89 (s, 3H), 3.88 (s, 2H), 3.82 (s, 3H), 2.85 (t, J = 7.2 Hz, 2H), 1.68-1.57 (m, 4H), 1.41-1.24 (m, 10H), 0.91 (t, J = 7.2 Hz, 3H), 0.86 (t, J = 7.2 Hz, 3H); 13C{1H} NMR (100 MHz, CDCl3): δ 203.0, 172.1, 152.8, 151.8, 145.0, 133.6, 121.8, 108.4, 64.5, 61.0, 60.7, 56.2, 41.1, 31.8, 31.6, 30.6, 29.2, 29.1, 24.3, 22.5, 19.1, 14.0, 13.6
13C NMR: δ 203.0 (1C, s), 172.1 (1C, s), 152.8 (1C, s), 151.8 (1C, s), 145.0 (1C, s), 133.6 (1C, s), 121.8 (1C, s), 108.4 (1C, s), 64.5 (1C, s), 61.0 (1C, s), 60.7 (1C, s), 56.2 (1C, s), 41.1 (1C, s), 31.8 (1C, s), 31.6 (1C, s), 30.6 (1C, s), 29.2 (1C, s), 29.1 (1C, s), 24.3 (1C, s), 22.5 (1C, s), 19.1 (1C, s), 14.0 (1C, s), 13.6 (1C, s)

### benchmark_expand_500:R178
Molecular formula: C21H23N3O2S
IR bands (cm-1): [3235.0, 3030.0, 2970.0, 1684.0]
1H NMR: 9.57 (s,1H, NH Amide), 8.04 (d, J = 8.00 Hz, 1H, H5), 7.77 (t, J = 7.70 Hz, 1H, H7), 7.53 (d, J = 8.20 Hz, 1H, H8), 7.42 (t, J = 7.50 Hz, 1H, H6), 7.05-7.00 (m,3H, H4, H3, H5), 4.79-4.64 (m, 1H, CHIsopropyl), 4.23 (s, 2H, CH2), 2.09 (s, 6H, 2 × CH3), 1.60 (d, J = 6.60 Hz, 6H, 2xCH3) ppm
13C NMR: δ 165.7 (1C, s), 161.4 (1C, s), 156.5 (1C, s), 146.7 (1C, s), 135.7 (1C, s), 135.3 (1C, s), 134.9 (1C, s), 128.0 (1C, s), 127.0 (1C, s), 126.6 (1C, s), 126.3 (1C, s), 126.0 (1C, s), 120.4 (1C, s), 36.4 (1C, s), 19.6 (1C, s), 18.5 (1C, s)

### benchmark_expand_500:R179
Molecular formula: C23H24BrN3O5
IR bands (cm-1): [3354.0, 3234.0, 3124.0, 2933.0, 2858.0, 2160.0, 1768.0, 1702.0, 1618.0, 1479.0, 1352.0, 1259.0, 1196.0, 1119.0, 823.0, 746.0]
1H NMR: 11.15 (s, 1H), 9.67 (s, 1H), 8.48 (d, J = 8.4 Hz, 1H), 7.81 (dd, J = 8.4, 7.2 Hz, 1H), 7.60 (d, J = 7.2 Hz, 1H), 5.15 (dd, J = 12.9, 5.4 Hz, 1H), 2.90 (m, 1H), 2.67-2.51 (m, 2H), 2.46 (t, J = 7.7 Hz, 2H), 2.21 (t, J = 7.3 Hz, 2H), 2.06 (m, 1H), 1.62 (quint, J = 7.97 Hz, 2H), 1.44 (quint, J = 7.3 Hz, 2H), 1.38-1.24 (m, 6H)
13C NMR: δ 173.3 (1C, s), 172.5 (1C, s), 170.3 (1C, s), 168.3 (1C, s), 167.2 (1C, s), 137.1 (1C, s), 136.6 (1C, s), 132.0 (1C, s), 126.7 (1C, s), 118.8 (1C, s), 117.4 (1C, s), 81.0 (1C, s), 49.4 (1C, s), 45.9 (1C, s), 37.0 (1C, s), 31.5 (1C, s), 28.9 (1C, s), 28.7 (1C, s), 28.6 (1C, s), 28.2 (1C, s), 25.2 (1C, s), 22.5 (1C, s), 19.4 (1C, s)
