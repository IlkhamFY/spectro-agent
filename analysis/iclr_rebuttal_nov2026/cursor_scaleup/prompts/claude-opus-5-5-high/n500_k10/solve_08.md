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
  {"benchmark_main:R64": ["CCO", "COC"]}

Compounds:

### benchmark_main:R64
Molecular formula: C12H20O2
IR bands (cm-1): [2935.0, 2863.0, 1721.0, 1459.0, 1379.0, 1063.0, 902.0]
1H NMR: 9.78 (t, J = 1.7 Hz, 1H), 5.00 (s, 1H), 4.79 (s, 1H), 4.37 (t, J = 7.1 Hz, 0.79H major, C5-H), 4.32 (t, J = 7.3 Hz, 0.21H minor, C5-H), 2.47 (td, J = 7.3, 1.7 Hz, 2H), 2.11-1.99 (m, 1H), 1.87-1.78 (m, 1H), 1.78-1.66 (m, 4H), 1.64-1.50 (m, 5H), 1.28-1.17 (m, 3H)
13C NMR: δ 202.7 (1C, s), 145.7 (1C, s), 134.8 (1C, s), 110.2 (1C, s), 81.4 (1C, s), 44.3 (1C, s), 41.2 (1C, s), 37.0 (1C, s), 31.3 (1C, s), 25.8 (1C, s), 18.1 (1C, s), 17.4 (1C, s)

### benchmark_main:R66
Molecular formula: C14H23NO4
IR bands (cm-1): [3385.0, 2967.0, 2916.0, 2856.0, 1736.0, 1626.0, 1438.0, 1376.0, 1208.0, 1059.0, 1011.0, 833.0, 759.0, 643.0, 531.0]
1H NMR: 5.38-5.29 (m, 1H), 5.15-5.07 (m, 1H), 3.74 (s, 2H), 3.69 (s, 1H), 3.07-2.76 (m, 2H), 2.21-2.07 (m, 4H), 1.82 (d, J = 5.0 Hz, 1H), 1.77 (s, 2H), 1.68 (s, 3H), 1.62 (s, 3H)
13C NMR: δ 177.6 (1C, s), 172.6 (1C, s), 147.4 (1C, s), 133.0 (1C, s), 124.6 (1C, s), 115.2 (1C, s), 52.7 (1C, s), 45.9 (1C, s), 40.7 (1C, s), 35.4 (1C, s), 27.2 (1C, s), 25.8 (1C, s), 23.8 (1C, s)

### benchmark_main:R69
Molecular formula: C5H9N3S
IR bands (cm-1): [3384.0, 3167.0, 1650.0, 1603.0]
1H NMR: 11.144 (s, 1H, N-H), 8.043 (br, 1H, H-N-H), 7.697 (d, 1H, -CH=N, J = 8.50 Hz), 7.500 (br, 1H, H-N-H), 6.197-6.083 (m, 2H, -CH=CH-), 1.836 (d, 1H, -CH3, J = 5.50 Hz)
13C NMR: δ 177.599 (1C, s), 144.856 (1C, s), 138.172 (1C, s), 128.401 (1C, s), 18.393 (1C, s)

### benchmark_main:R70
Molecular formula: C9H8N2O2
IR bands (cm-1): [3263.0, 2231.0, 1670.0, 1616.0, 1558.0, 1509.0, 1417.0, 1305.0, 1262.0, 1172.0, 1038.0, 809.0, 766.0, 710.0, 568.0, 522.0]
1H NMR: 11.70 (broad s, 1H, NH), 7.47 (d, J = 8.0 Hz, 2H, Ar-H), 6.93 (d, J = 8.0 Hz, 2H, Ar-H), 3.71 (s, 3H, OCH3)
13C NMR: δ 157.0 (1C, s), 140.3 (1C, s), 129.8 (1C, s), 121.9 (1C, s), 114.4 (1C, s), 112.7 (1C, s), 55.4 (1C, s)

### benchmark_main:R73
Molecular formula: C8H7N5S
IR bands (cm-1): [3151.0, 1597.0, 1577.0, 1491.0, 1314.0, 1203.0, 1115.0, 931.0, 819.0]
1H NMR: 7.79 (d, 2H, J = 5.8 Hz, pyridine H-3,5), 8.78 (d, 2H, J = 5.8 Hz, pyridine H-2,6), 8.98 (s, 1H, traizole H), 9.59 (s, 1H, imine H), 14.01 (s, 1H, NH)
13C NMR: δ 121.75 (1C, s), 137.95 (1C, s), 139.29 (1C, s), 150.64 (1C, s), 157.65 (1C, s), 163.29 (1C, s)

### benchmark_main:R76
Molecular formula: C13H12N2O3S
IR bands (cm-1): [3413.0, 1615.0, 1486.0, 1338.0, 1243.0, 1137.0, 949.0, 853.0, 773.0, 617.0, 502.0]
1H NMR: 7.94 (d, J = 9.0 Hz, 2H), 7.47-7.43 (m, 2H), 7.27 (t, J = 7.4 Hz, 1H), 7.13-7.01 (m, 4H), 3.20 (s, 3H). 13C{1H} NMR (100 MHz, CDCl3): δ 164.3, 154.5, 144.0, 130.2, 127.1, 125.4, 120.6, 117.7, 34.8
13C NMR: δ 164.3 (1C, s), 154.5 (1C, s), 144.0 (1C, s), 130.2 (1C, s), 127.1 (1C, s), 125.4 (1C, s), 120.6 (1C, s), 117.7 (1C, s), 34.8 (1C, s)
