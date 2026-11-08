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
  {"benchmark_expand_500:R124": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R124
Molecular formula: C26H20N4O4S
IR bands (cm-1): [3381.0, 1691.0, 1626.0, 1579.0, 1528.0, 1506.0, 1482.0, 1431.0, 1414.0, 1350.0, 1306.0, 1253.0, 1214.0, 1202.0, 1174.0, 1119.0, 1080.0, 996.0, 849.0, 713.0]
1H NMR: 11.14 (s, 1H), 8.50 (d, J = 4.8 Hz, 1H), 8.38 (dd, J = 2.4, 7.2 Hz, 2H), 8.02 (d, J = 9.0 Hz, 2H), 7.63-7.59 (m, 3H), 7.51 (s, 1H), 7.40 (s, 1H), 7.35 (d, J = 9.0 Hz, 2H), 6.53 (d, J = 5.4 Hz, 1H), 3.95 (s, 3H), 3.93 (s, 3H)
13C NMR: δ 184.9 (1C, s), 173.0 (1C, s), 159.6 (1C, s), 156.2 (1C, s), 152.6 (1C, s), 150.7 (1C, s), 149.3 (1C, s), 148.8 (1C, s), 146.4 (1C, s), 134.6 (1C, s), 131.7 (1C, s), 131.1 (1C, s), 129.0 (1C, s), 128.1 (1C, s), 122.9 (1C, s), 121.3 (1C, s), 115.2 (1C, s), 107.8 (1C, s), 103.4 (1C, s), 99.0 (1C, s), 55.7 (1C, s), 55.6 (1C, s)

### benchmark_expand_500:R125
Molecular formula: C27H26N2O3
IR bands (cm-1): [1644.0, 1464.0, 1452.0, 1431.0, 1349.0, 1315.0, 1293.0, 1229.0, 1182.0, 1083.0, 1032.0, 1014.0, 908.0, 727.0, 699.0]
1H NMR: 7.61-7.50 (m, 1H), 7.28-7.11 (m, 6H), 7.10-7.04 (m, 2H), 7.01-6.95 (m, 2H), 6.89 (dd, J = 8.6, 2.7 Hz, 1H), 5.17 (d, J = 17.0 Hz, 1H), 5.09-4.99 (m, 2H), 4.85 (d, J = 10.2 Hz, 1H), 3.91 (td, J = 14.5, 4.6 Hz, 1H), 3.85 (s, 3H), 3.69-3.46 (m, 2H), 3.15 (s, 3H), 2.91 (ddd, J = 16.4, 4.5, 1.3 Hz, 1H) ppm
13C NMR: δ 172.1 (1C, s), 160.0 (1C, s), 138.7 (1C, s), 138.1 (1C, s), 137.4 (1C, s), 134.0 (1C, s), 131.9 (1C, s), 128.7 (1C, s), 128.6 (1C, s), 127.1 (1C, s), 126.1 (1C, s), 122.4 (1C, s), 121.4 (1C, s), 119.7 (1C, s), 118.2 (1C, s), 115.8 (1C, s), 112.7 (1C, s), 110.5 (1C, s), 108.9 (1C, s), 75.6 (1C, s), 56.2 (1C, s), 55.5 (1C, s), 47.5 (1C, s), 45.0 (1C, s)

### benchmark_expand_500:R127
Molecular formula: C11H10BrNO2
IR bands (cm-1): [3291.0, 2985.0, 1683.0, 1619.0, 1516.0]
1H NMR: 9.12 (br s, 1H), 7.68 (d, J = 8.6 Hz, 1H), 7.41-7.36 (m, 2H), 7.25-7.21 (m, 1H), 4.46 (q, J = 7.3 Hz, 2H), 1.46 (t, J = 7.3 Hz, 3H) ppm
13C NMR: δ 161.0 (1C, s), 135.3 (1C, s), 128.0 (1C, s), 126.6 (1C, s), 124.1 (1C, s), 121.5 (1C, s), 121.3 (1C, s), 112.0 (1C, s), 98.3 (1C, s), 61.5 (1C, s)

### benchmark_expand_500:R128
Molecular formula: C38H60O3
IR bands (cm-1): [1694.0, 1507.0, 1383.0, 1298.0]
1H NMR: 7.45 (2H, d, J = 8.4 Hz), 7.06 (1H, d, J = 16.4 Hz), 6.91 (2H, J = 8.4 Hz), 6.92 (1H, d, J = 16.0 Hz), 6.66 (2H, d, J = 2.4 Hz), 6.40 (1H, t, J = 2.0 Hz), 4.00 (6H, m), 1.83 (6H, m), 1.50 (6H, m), 1.36 (24H, m), 0.94 (9H, m)
13C NMR: δ 160.5 (1C, s), 158.9 (1C, s), 139.6 (1C, s), 129.8 (1C, s), 128.6 (1C, s), 127.7 (1C, s), 126.5 (1C, s), 114.7 (1C, s), 104.8 (1C, s), 100.5 (1C, s), 68.0 (1C, s), 31.8 (1C, s), 29.4 (1C, s), 29.3 (1C, s), 29.2 (1C, s), 26.1 (1C, s), 26.0 (1C, s), 22.6 (1C, s), 14.1 (1C, s)

### benchmark_expand_500:R129
Molecular formula: C27H23N3O4
IR bands (cm-1): [3443.0, 1699.0, 1633.0, 1510.0, 1324.0, 1071.0]
1H NMR: 3.03 (t, J = 7.0 Hz, 2H, CH2), 3.68 (s, 1H, OCH3), 3.96-4,03 (m, 2H, NCH2), 4.93 (s, 1H, ArH), 6.78 (d, J = 8.5 Hz, 2H, ArH), 7.09 (d, J = 8.5 Hz, 2H, ArH), 7.20-7.29 (m, 2H, ArH), 7.32-7.37 (m, 5H, ArH), 7.46-7.50 (m, 1H, ArH), 7.82 (d, J = 7.5 Hz, 1H, ArH), 9.98 (s, 1H, NH), 11.36-11.43 (m, 1H, NH)
13C NMR: δ 35.3 (1C, s), 37.2 (1C, s), 44.1 (1C, s), 55.5 (1C, s), 110.7 (1C, s), 113.9 (1C, s), 121.1 (1C, s), 121.6 (1C, s), 127.1 (1C, s), 128.9 (1C, s), 129.0 (1C, s), 129.0 (1C, s), 129.4 (1C, s), 130.6 (1C, s), 132.7 (1C, s), 135.8 (1C, s), 136.5 (1C, s), 138.6 (1C, s), 151.7 (1C, s), 151.9 (1C, s), 158.3 (1C, s), 190.9 (1C, s)

### benchmark_expand_500:R130
Molecular formula: C15H16N4O
IR bands (cm-1): [2934.0, 2853.0, 2773.0, 1652.0, 1627.0, 1380.0, 1131.0, 1009.0, 851.0, 770.0]
1H NMR: 12.65 (br s, 1H), 8.25 (d, J = 8.0 Hz, 1H), 8.17 (d, J = 7.9 Hz, 1H), 7.85 (t, J = 7.5 Hz, 1H), 7.56 (t, J = 7.7 Hz, 1H), 4.64 (tt, J = 11.5, 3.8 Hz, 1H), 2.10-2.04 (m, 2H), 1.95-1.84 (m, 4H), 1.70 (d, J = 12.8 Hz, 1H), 1.43 (qt, J = 13.1, 3.9 Hz, 2H), 1.30 (qt, J = 13.0, 6.5 Hz, 1H) ppm
13C NMR: δ 162.2 (1C, s), 134.2 (1C, s), 133.8 (1C, s), 130.5 (1C, s), 129.1 (1C, s), 127.3 (1C, s), 126.5 (1C, s), 123.7 (1C, s), 121.1 (1C, s), 57.0 (1C, s), 32.5 (1C, s), 25.4 (1C, s)
