# Blind structure-elucidation task

You are given real experimental spectra for organic molecules. For EACH compound
you are given the molecular formula, the IR band list, and the printed 1H and 13C
NMR lists. No name, SMILES, InChI, or other hint is given.

For each compound, propose up to 50 distinct constitutions, best first, as SMILES.

Rules:
  - Use only the spectra in this file. Do not open any other file, do not search
    the web, and do not look up a name, a structure, or an identifier.
  - Do not enumerate isomers with a database or a structure generator. You may
    use RDKit only to check that a SMILES you already wrote parses and has this
    molecular formula.
  - Every candidate must match the given molecular formula exactly.
  - Order candidates by your own confidence, most likely first.
  - If you cannot honestly propose 50 different constitutions, return fewer.
    Do not pad with duplicates or with structures that break the formula.
  - If you know more distinct formula-matching constitutions than 50, stop at 50
    unless you would have written them anyway. Do not invent fillers.

Return ONLY a JSON object mapping each id to a list of SMILES strings, e.g.:
  {"benchmark_main:R11": ["CCO", "COC"]}

Compounds:

### benchmark_main:R11
Molecular formula: C13H11ClN2O3S
IR bands (cm-1): [3311.0, 3230.0, 3140.0, 3400.0, 3064.0, 3032.0, 1616.0, 1330.0, 1162.0]
1H NMR: 13.89 (1H, s, Ar-OH), 9.04 (1H, s, -CH=N-), 7.41 (2H, s, -SO2NH2), 7.90-7.88 (2H, d, J = 8, Ar-H), 7.63-7.58 (4H, m, Ar-H) , 7.02-6.98 (1H, t, J = 8, Ar-H)
13C NMR: δ 165.85 (1C, s), 156.83 (1C, s), 150.09 (1C, s), 142.96 (1C, s), 134.52 (1C, s), 131.96 (1C, s), 127.42 (1C, s), 122.99 (1C, s), 121.92 (1C, s), 120.64 (1C, s), 119.40 (1C, s)

### benchmark_main:R110
Molecular formula: C12H18N2S
IR bands (cm-1): [3312.0, 2975.0, 2930.0, 1532.0, 1441.0, 1347.0, 1280.0, 1136.0, 862.0, 698.0]
1H NMR: 7.46-7.22 (m, 5H), 5.55 (br s, 1H), 4.87 (d, J = 4.9 Hz, 2H), 3.66 (q, J = 7.1 Hz, 4H), 1.23 (t, J = 7.1 Hz, 6H)
13C NMR: δ 180.6 (1C, s), 138.4 (1C, s), 128.9 (1C, s), 128.0 (1C, s), 127.7 (1C, s), 50.3 (1C, s), 45.3 (1C, s), 12.8 (1C, s)

### benchmark_main:R111
Molecular formula: C19H22O
IR bands (cm-1): [3582.0, 3496.0, 3082.0, 3059.0, 3026.0, 2969.0, 2931.0, 2876.0, 1599.0, 1494.0, 1447.0, 1371.0, 1262.0, 1161.0, 1073.0, 1030.0, 967.0, 909.0, 751.0, 701.0]
1H NMR: 0.69 (t, J = 7.4 Hz, 3H), 0.90 (d, J = 6.9 Hz, 3H), 1.83 (br s, 1H), 1.85-1.99 (m, 2H), 2.72 (dq, J = 8.9, 6.9 Hz, 1H), 6.24 (dd, J = 15.9, 8.9 Hz, 1H), 6.48 (d, J = 15.9 Hz, 1H), 7.19-7.25 (m, 2H), 7.28-7.33 (m, 2H), 7.33-7.40 (m, 6H). 13C{1H} NMR (CDCl3, 125 MHz): δ 7.9, 15.6, 33.7, 48.0, 79.1, 126.0, 126.3, 126.4, 127.3, 128.0, 128.7, 131.5, 132.0, 137.6, 144.7
13C NMR: δ 7.9 (1C, s), 15.6 (1C, s), 33.7 (1C, s), 48.0 (1C, s), 79.1 (1C, s), 126.0 (1C, s), 126.3 (1C, s), 126.4 (1C, s), 127.3 (1C, s), 128.0 (1C, s), 128.7 (1C, s), 131.5 (1C, s), 132.0 (1C, s), 137.6 (1C, s), 144.7 (1C, s)

### benchmark_main:R113
Molecular formula: C12H12BN3O3
IR bands (cm-1): [3346.0, 3176.0, 1679.0, 1527.0, 1348.0, 638.0]
1H NMR: 10.62 (s, 1H, CONH), 8.72 (d, J = 2.6 Hz, 1H, PzH), 8.60 (d, J = 2.6 Hz, 1H, PzH), 7.95 (bs, 2H, BO2H2), 7.81-7.73 (m, 4H, ArH), 2.75 (s, 3H, CH3)
13C NMR: δ 164.40 (1C, s), 153.59 (1C, s), 146.21 (1C, s), 145.96 (1C, s), 141.31 (1C, s), 140.66 (1C, s), 135.38 (1C, s), 119.29 (1C, s), 22.97 (1C, s)

### benchmark_main:R115
Molecular formula: C12H12N4O2
IR bands (cm-1): [3348.0, 3278.0, 3201.0, 3062.0, 1735.0, 1670.0, 1597.0, 1558.0, 1489.0, 1377.0, 1253.0, 1161.0, 1045.0]
1H NMR: 10.8 (d, J:12.4 Hz, -NH), 8,21 (d, J: 12 Hz, urea-CH=C), 7.94 (d, J: 7.6 Hz, 2H, Ar CH), 7.79 (s, 2H, -NH2), 7.41 (t, J: 16 Hz, 2H, Ar CH), 7.15 (t, J: 14.8 Hz, H, Ar CH), 2.24 (s, 3H, -CH3). The
13C NMR: δ 164.5 (1C, s), 153.1 (1C, s), 150.3 (1C, s), 143.5 (1C, s), 139.2 (1C, s), 129.3 (1C, s), 124.5 (1C, s), 118.1 (1C, s), 104.8 (1C, s), 12 (1C, s)

### benchmark_main:R118
Molecular formula: C11H24O2Si
IR bands (cm-1): [2954.0, 2929.0, 2857.0, 1728.0, 1472.0, 1462.0, 1388.0, 1254.0, 1097.0, 1005.0, 881.0, 834.0, 776.0]
1H NMR: 0.04 (s, 6H), 0.88 (s, 9H), 1.11 (d, J = 7.0 Hz, 3H), 1.58-1.68 (m, 1H), 1.90-2.01 (m, 1H), 2.44-2.56 (m, 1H), 3.62-3.74 (m, 2H), 9.65 (d, J = 1.8 Hz, 1H)
13C NMR: δ -5.32 (1C, s), -5.31 (1C, s), 13.3 (1C, s), 18.4 (1C, s), 26.0 (1C, s), 33.9 (1C, s), 43.7 (1C, s), 60.4 (1C, s), 205.0 (1C, s)
