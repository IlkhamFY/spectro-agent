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
  {"benchmark_expand:R16": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R16
Molecular formula: C15H23N3O3
IR bands (cm-1): [3384.0, 3335.0, 2980.0, 2961.0, 2925.0, 2865.0, 1681.0, 1485.0, 1418.0, 1369.0, 1270.0, 1249.0, 1236.0]
1H NMR: 1.40 (9H, s, C(CH3)3), 1.46 (2H, dddd, J = 13.2, 9.2, 9.1 and 4.1 Hz, H-3′, 5′axial), 1.87 (2H, ddd, J = 13.2, 5.8 and 3.3 Hz, H-3′, 5′equ), 3.12 (2H, brs, H-2′, 6′axial), 3.66 (2H, ddd, J = 13.2, 4.9 and 4.9 Hz, H-2′, 6′equ), 4.74 (2H, brs, ArNH2), 4.93 (1H, tt, J = 8.3, 3.8 Hz, H-4′), 6.51 (1H, d, J = 8.6 Hz, H-3), 6.98 (1H, dd, J = 8.6, 2.9 Hz, H-4), 7.48 (1H, d, J = 2.9 Hz, H-6)
13C NMR: δ 28.1 (1C, s), 30.7 (1C, s), 40.6 (1C, s), 69.3 (1C, s), 78.6 (1C, s), 110.9 (1C, s), 126.3 (1C, s), 131.1 (1C, s), 139.4 (1C, s), 153.9 (1C, s), 154.3 (1C, s)

### benchmark_expand:R17
Molecular formula: C15H12O3
IR bands (cm-1): [3465.0, 3428.0, 1639.0, 1586.0]
1H NMR: 8.07 (d, J = 8.8 Hz, 2H, H9-9′), 7.70 (d, J = 8.6 Hz, 2H, H5-5′), 7.69 (s, 2H, H2 and H3), 6.96 (d, J = 8.6 Hz, 2H, H10-10′), 6.91 (d, J = 8.7 Hz, 2H, H6-6′)
13C NMR: δ 188.0 (1C, s), 162.5 (1C, s), 160.6 (1C, s), 144.0 (1C, s), 131.7 (1C, s), 131.4 (1C, s), 131.3 (1C, s), 127.9 (1C, s), 119.7 (1C, s), 116.7 (1C, s), 116.1 (1C, s)

### benchmark_expand:R19
Molecular formula: C8H5IN2O
IR bands (cm-1): [3286.0, 2231.0, 1698.0, 1670.0, 1602.0, 1542.0, 1483.0, 1396.0, 1313.0, 1289.0, 1249.0, 1062.0, 1006.0, 928.0, 829.0, 694.0, 505.0]
1H NMR: 11.93 (broad s, 1H, NH), 7.74 (d, J = 8.8 Hz, 2H, Ar-H), 7.37 (d, J = 8.8 Hz, 2H, Ar-H)
13C NMR: δ 140.8 (1C, s), 138.0 (1C, s), 136.5 (1C, s), 122.4 (1C, s), 112.5 (1C, s), 90.4 (1C, s)

### benchmark_expand:R20
Molecular formula: C16H13NO4
IR bands (cm-1): [3288.0, 2939.0, 1654.0, 1521.0, 1347.0, 1251.0, 1172.0, 1026.0]
1H NMR: 8.17 (d, J = 8.2 Hz, 1H), 7.79-7.71 (m, 1H), 7.69-7.60 (m, 1H), 7.50 (dd, J = 7.5, 1.1 Hz, 1H), 7.45 (d, J = 8.7 Hz, 2H), 7.20 (d, J = 16.2 Hz, 1H), 6.94-6.82 (m, 3H), 3.83 (s, 3H)
13C NMR: δ 193.1 (1C, s), 162.2 (1C, s), 146.9 (1C, s), 146.5 (1C, s), 136.7 (1C, s), 134.1 (1C, s), 130.6 (1C, s), 130.5 (1C, s), 129.0 (1C, s), 126.8 (1C, s), 124.7 (1C, s), 124.1 (1C, s), 114.6 (1C, s), 55.6 (1C, s)

### benchmark_expand:R24
Molecular formula: C18H20O3
IR bands (cm-1): [3001.0, 2920.0, 2850.0, 1737.0, 1603.0, 1580.0, 1490.0, 1457.0, 1411.0, 1329.0, 1222.0, 1200.0, 1156.0, 1113.0, 1063.0, 1031.0]
1H NMR: 7.63 (d, J = 8.4 Hz, 2H), 7.38 (d, J = 3.2 Hz, 2H), 7.24 (d, J = 8.4 Hz, 2H), 6.16 (s, 2H), 3.88 (s, 6H), 3.84 (s, 3H)
13C NMR: δ 160.1 (1C, s), 159.4 (1C, s), 138.7 (1C, s), 135.3 (1C, s), 130.1 (1C, s), 128.1 (1C, s), 126.5 (1C, s), 126.0 (1C, s), 124.9 (1C, s), 120.7 (1C, s), 108.5 (1C, s), 90.8 (1C, s), 55.8 (1C, s), 55.3 (1C, s), 20.0 (1C, s)

### benchmark_expand:R25
Molecular formula: C12H22O3
IR bands (cm-1): [2926.0, 2858.0, 1720.0, 1643.0, 1459.0, 1361.0, 1313.0, 1237.0, 1150.0, 1034.0, 728.0]
1H NMR: 4.15 (t, J = 6.8 Hz, 2H), 3.46 (s, 2H), 2.29 (s, 3H), 1.69-1.62 (m, 2H), 1.29 (s, 6H), 0.89 (t, J = 6.8 Hz, 3H)
13C NMR: δ 200.7 (1C, s), 167.2 (1C, s), 89.8 (1C, s), 65.6 (1C, s), 64.1 (1C, s), 50.2 (1C, s), 31.8 (1C, s), 30.1 (1C, s), 29.2 (1C, s), 28.7 (1C, s), 28.5 (1C, s), 25.9 (1C, s), 22.6 (1C, s), 21.2 (1C, s), 14.1 (1C, s)
