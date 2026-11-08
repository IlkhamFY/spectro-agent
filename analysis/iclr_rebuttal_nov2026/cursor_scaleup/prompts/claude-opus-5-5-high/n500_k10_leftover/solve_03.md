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
  {"benchmark_expand:R22": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R22
Molecular formula: C19H31NO5
IR bands (cm-1): [2976.0, 2933.0, 2888.0, 2855.0, 1684.0, 1625.0, 1442.0, 1317.0, 1157.0, 1097.0, 1074.0, 1030.0]
1H NMR: 9.43 (s, 0.5H), 9.42 (s, 1H), 6.62-6.57 (m, 1.5H), 6.16 (dd, J = 11.6, 0.8 Hz, 1H), 6.00 (d, J = 11.6 Hz, 0.5H), 5.84 (dd, J = 11.6, 8.6 Hz, 1H), 5.83 (dd, J = 11.6, 8.6 Hz, 0.5H), 4.83-4.77 (m, 1H), 4.74-4.68 (m, 0.5H), 4.68 (d, J = 6.7 Hz, 1H), 4.65 (d, J = 6.7 Hz, 0.5H), 4.58 (d, J = 6.7 Hz, 1.5H), 4.57-4.53 (m, 1H), 3.80 (qd, J = 6.5, 3.4 Hz, 1H), 3.77 (qd, J = 6.5, 3.3 Hz, 0.5H), 3.70-3.66 (m, 0.5H), 3.64-3.56 (m, 1.5H), 3.34 (s, 3H), 3.33 (s, 1.5H), 3.24 (s, 3H), 3.21 (s, 1.5H), 2.60-2.54 (m, 3H), 2.07-1.94 (m, 3H), 1.77-1.74 (m, 4H), 1.68-1.56 (m, 3H), 1.34 (d, J = 6.4 Hz, 1.5H), 1.31 (d, J = 6.4 Hz, 3H), 1.19 (d, J = 6.5 Hz, 1.5H), 1.18 (d, J = 6.5 Hz, 3H)
13C NMR: δ 195.2 (1C, s), 195.1 (1C, s), 168.2 (1C, s), 167.9 (1C, s), 150.1 (1C, s), 149.8 (1C, s), 143.0 (1C, s), 142.1 (1C, s), 141.00 (1C, s), 140.94 (1C, s), 123.5 (1C, s), 122.9 (1C, s), 95.0 (1C, s), 94.7 (1C, s), 76.72 (1C, s), 76.70 (1C, s), 75.9 (1C, s), 75.8 (1C, s), 70.7 (1C, s), 69.8 (1C, s), 55.5 (1C, s), 55.4 (1C, s), 53.0 (1C, s), 47.4 (1C, s), 36.0 (1C, s), 35.9 (1C, s), 35.2 (1C, s), 32.2 (1C, s), 31.7 (1C, s), 29.3 (1C, s), 28.0 (1C, s), 27.7 (1C, s), 27.5 (1C, s), 21.2 (1C, s), 21.1 (1C, s), 18.1 (1C, s), 9.6 (1C, s)

### benchmark_expand:R23
Molecular formula: C18H17BrClNO2S
IR bands (cm-1): [2924.0, 1659.0, 1596.0, 1488.0, 1441.0, 1344.0, 1159.0, 1093.0, 906.0, 814.0, 707.0, 481.0, 409.0]
1H NMR: 7.69 (d, J = 7.8 Hz, 2H), 7.40 (d, J = 7.9 Hz, 1H), 7.35 (s, 1H), 7.30 (d, J = 7.9 Hz, 2H), 7.24 (d, J = 7.8 Hz, 1H), 7.19 (t, J = 7.8 Hz, 1H), 5.73 (s, 1H), 5.29 (d, J = 6.4 Hz, 1H), 4.23 (d, J = 18.2 Hz, 1H), 3.41-3.36 (m, 1H), 2.67-2.61 (m, 1H), 2.56 (d, J = 17.7 Hz, 1H), 2.44 (s, 3H). 13C{1H} NMR (125 MHz, CDCl3) δ 144.1, 140.4, 137.3, 131.4, 130.6, 130.5, 130.1, 128.8, 127.2, 125.9, 123.0, 121.0, 53.7, 41.6, 33.9, 21.8
13C NMR: δ 144.1 (1C, s), 140.4 (1C, s), 137.3 (1C, s), 131.4 (1C, s), 130.6 (1C, s), 130.5 (1C, s), 130.1 (1C, s), 128.8 (1C, s), 127.2 (1C, s), 125.9 (1C, s), 123.0 (1C, s), 121.0 (1C, s), 53.7 (1C, s), 41.6 (1C, s), 33.9 (1C, s), 21.8 (1C, s)

### benchmark_expand:R27
Molecular formula: C22H16FN3O3S
IR bands (cm-1): [1595.0, 1558.0, 1456.0, 1447.0, 1408.0, 1394.0, 1275.0, 1261.0, 1189.0, 869.0, 852.0, 764.0, 752.0]
1H NMR: 8.50 (dd, J = 8.1, 1.5 Hz, 1H), 7.94-7.86 (m, 1H), 7.77 (td, J = 7.8, 1.4 Hz, 1H), 7.59-7.42 (m, 3H), 7.28 (dtd, J = 15.2, 8.2, 1.3 Hz, 2H), 5.71-5.57 (m, 1H), 5.13 (dd, J = 11.7, 9.8 Hz, 1H), 4.94 (d, J = 3.2 Hz, 1H), 4.87-4.75 (m, 2H), 3.83-3.68 (m, 1H), 3.17 (dd, J = 13.9, 7.7 Hz, 1H), 2.86 (dd, J = 13.8, 7.4 Hz, 1H)
13C NMR: δ 178.4 (1C, s), 162.5 (1C, s), 159.2 (1C, s), 152.7 (1C, s), 138.5 (1C, s), 134.6 (1C, s), 131.1 (1C, d), 130.3 (1C, s), 129.0 (1C, d), 126.8 (1C, s), 125.0 (1C, d), 120.9 (1C, d), 118.8 (1C, d), 116.1 (1C, s), 115.9 (1C, d), 115.4 (1C, s), 114.8 (1C, s), 50.3 (1C, s), 49.1 (1C, s), 46.9 (1C, s), 44.9 (1C, s), 42.1 (1C, s)

### benchmark_expand:R30
Molecular formula: C37H44O6Si
IR bands (cm-1): [2931.0, 2857.0, 1748.0, 1429.0, 1275.0, 1109.0, 962.0, 704.0]
1H NMR: 7.70-7.64 (m, 4H), 7.43-7.32 (m, 8H), 7.30-7.20 (m, 2H), 6.94 (s, 1H), 6.40 (s, 1H), 5.62 (dd, J = 3.6, 2.6 Hz, 1H), 3.81-3.74 (m, 2H), 3.70-3.64 (s, 3H), 2.57 (t, J = 7.2 Hz, 2H), 1.84 (pd, J = 7.6, 3.7 Hz, 2H), 1.45 (s, 9H), 1.09-1.02 (m, 9H)
13C NMR: δ 165.6 (1C, s), 152.4 (1C, s), 138.9 (1C, s), 138.8 (1C, s), 135.6 (1C, s), 133.9 (1C, s), 132.4 (1C, s), 129.6 (1C, s), 128.1 (1C, s), 127.9 (1C, s), 127.7 (1C, s), 126.4 (1C, s), 123.6 (1C, s), 95.8 (1C, s), 82.5 (1C, s), 77.9 (1C, s), 73.9 (1C, s), 62.6 (1C, s), 52.0 (1C, s), 31.7 (1C, s), 27.8 (1C, s), 26.9 (1C, s), 19.3 (1C, s), 16.2 (1C, s)

### benchmark_expand:R32
Molecular formula: C24H28N4O6S2
IR bands (cm-1): [1351.0, 1514.0, 1566.0, 1239.0, 1077.0, 3345.0, 1667.0, 3060.0]
1H NMR: 7.71 (d, J = 8.9 Hz, 2H, H-2’’ & H-6’’), 7.57 (s, 1H, NH), 7.37 (d, J = 8.8 Hz, 2H, H-3’’’ & H-5’’’), 7.01 (d, J = 8.9 Hz, 2H, H-3’’ & H-5’’), 6.90 (d, 2H, H-2’’’ & H-6’’’), 4.05 (s, 2H, H -1’’’’), 4.03(q, 2H, H-7’’’), 3.98-3.96 (m, 1H, He-2’), 3.89 (s, 3H, H-7’’), 3.68-3.66 (m, 1H, Ha-2’), 3.13-3.10 (m, 1H, H-3’), 2.65-2.62 (m, 1H, He-6’), 2.47-2.43 (m, 1H, Ha-6’), 2.15-2.12 (m, 1H, Ha-5’), 1.92-1.89 (m, 2H, Ha-4’), 1.79-1.75 (m, 1H, He-5’), 1.74-1.61 (m, 1H, He-4’), 1.42 (t, J = 13.9 Hz, 3H, H-8’’’)
13C NMR: δ 163.13 (1C, s), 161.00 (1C, s), 160.61 (1C, s), 160.22 (1C, s), 155.17 (1C, s), 132.29 (1C, s), 129.73 (1C, s), 127.62 (1C, s), 119.68 (1C, s), 115.26 (1C, s), 114.35 (1C, s), 63.81 (1C, s), 55.62 (1C, s), 52.63 (1C, s), 48.63 (1C, s), 46.29 (1C, s), 33.55 (1C, s), 27.21 (1C, s), 23.81 (1C, s)

### benchmark_expand:R33
Molecular formula: C20H13IO2
IR bands (cm-1): [2174.0, 1627.0, 1596.0, 1572.0, 1508.0, 1290.0, 1258.0, 1235.0, 1162.0, 1028.0]
1H NMR: 8.31-8.27 (3H, m), 8.06 (1H, dd, J = 7.3, 1.4 Hz), 7.91 (1H, dd, J = 8.2, 1.1 Hz), 7.86 (1H, dd, J = 8.2, 1.2 Hz), 7.48 (1H, dd, J = 8.1, 7.3 Hz), 7.15 (1H, dd, J = 8.1, 7.4 Hz), 6.99 (2H, app d, J = 9.0 Hz), 3.90 (3H, s). 13C{1H} NMR (100 MHz; CDCl3) δ: 176.6, 164.5, 143.0, 138.3, 134.9, 132.6, 132.5, 132.2, 130.4, 130.2, 127.6, 125.4, 120.3, 113.9, 99.1, 93.0, 91.6, 55.6
13C NMR: δ 176.6 (1C, s), 164.5 (1C, s), 143.0 (1C, s), 138.3 (1C, s), 134.9 (1C, s), 132.6 (1C, s), 132.5 (1C, s), 132.2 (1C, s), 130.4 (1C, s), 130.2 (1C, s), 127.6 (1C, s), 125.4 (1C, s), 120.3 (1C, s), 113.9 (1C, s), 99.1 (1C, s), 93.0 (1C, s), 91.6 (1C, s), 55.6 (1C, s)
