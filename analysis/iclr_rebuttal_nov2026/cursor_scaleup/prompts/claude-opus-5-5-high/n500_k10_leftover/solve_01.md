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
  {"benchmark_expand:R03": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R03
Molecular formula: C9H11N5O2
IR bands (cm-1): [3460.0, 3358.0, 3050.0, 2363.0, 1678.0, 1615.0, 1594.0]
1H NMR: 8.40 (s, 1H, Ar-NH-), 8.20 (d, 1H, J = 7.8 Hz, Ar-H), 8.13 (d, 1H, J = 8.1 Hz, Ar-H), 7.94 (ddd, 1H, J = 8.1 ,7.5, 1.2 Hz, Ar-H), 7.76 (s, 2H, -NH2), 7.57 (ddd, 1H, J = 7.8, 7.2, 1.2 Hz, Ar-H), 3.47 (d, 2H, J = 2.7 Hz, -NHCH2CH2CH2NH2), 2.88 (t, 2H, J = 7.5 Hz, - NHCH2CH2CH2NH2), 1.90 (m, 2H, -NHCH2CH2CH2NH2)
13C NMR: δ 150.5 (1C, s), 138.7 (1C, s), 136.1 (1C, s), 130.7 (1C, s), 127.9 (1C, s), 121.5 (1C, s), 117.5 (1C, s)

### benchmark_expand:R05
Molecular formula: C25H32O5
IR bands (cm-1): [3291.0, 2928.0, 1705.0, 1437.0, 1302.0, 1211.0]
1H NMR: 7.50 (1H, d, J = 1.5 Hz), 7.46 (1H, d, J = 1.5 Hz), 6.14 (1H, s), 4.80 (1H, s), 4.79 (1H, s), 3.87 (3H, s), 2.74 (1H, d, J = 14.1 Hz), 2.70 (1H, d, J = 14.1 Hz), 2.62-2.55 (2H, m), 2.25 (1H, d, J = 12.8 Hz), 2.17 (1H, m), 2.12-2.09 (1H, m), 1.80 (1H, qd, J = 13.0, 3.2 Hz), 1.69-1.61 (1H, m), 1.45-1.18 (5H, m), 1.15 (3H, s), 1.15-1.12 (1H, m), 1.03 (3H, d, J = 6.1 Hz), 0.94 (3H, s)
13C NMR: δ 216.4 (1C, s), 166.8 (1C, s), 149.5 (1C, s), 144.0 (1C, s), 128.2 (1C, s), 124.3 (1C, s), 120.6 (1C, s), 111.3 (1C, s), 77.4 (1C, s), 76.6 (1C, s), 57.3 (1C, s), 52.0 (1C, s), 49.2 (1C, s), 47.4 (1C, s), 42.4 (1C, s), 37.5 (1C, s), 36.9 (1C, s), 35.6 (1C, s), 32.3 (1C, s), 26.7 (1C, s), 25.3 (1C, s), 22.0 (1C, s), 18.9 (1C, s), 18.0 (1C, s), 17.4 (1C, s)

### benchmark_expand:R06
Molecular formula: C21H15N3O2
IR bands (cm-1): [2933.0, 2251.0, 1769.0, 1720.0, 1501.0]
1H NMR: 2.76 (dd, J = 17.1, 5.4 Hz, 1H, H-4β), 3.02-3.13 (m, 2H, H-4α, H-7α), 3.41-3.49 (m, 1H, H-7β), 3.46 (dd, J = 10.8, 5.4 Hz, 1H, H-5), 7.35-7.50 (m, 10H, H-Ar)
13C NMR: δ 24.5 (1C, s), 32.5 (1C, s), 37.3 (1C, s), 46.6 (1C, s), 113.3 (1C, s), 113.6 (1C, s), 121.1 (1C, s), 125.3 (1C, s), 127.9 (1C, s), 128.0 (1C, s), 128.5 (1C, s), 129.7 (1C, s), 129.8 (1C, s), 129.8 (1C, s), 132.8 (1C, s), 134.9 (1C, s), 153.6 (1C, s)

### benchmark_expand:R08
Molecular formula: C26H18Cl2N2O2
IR bands (cm-1): [3445.0, 1653.0, 1618.0, 1576.0, 1481.0, 1408.0, 1358.0, 1229.0, 984.0]
1H NMR: 8.79 (s, 1H, Qu-2-H), 8.30 (d, J = 8.0 Hz, 1H, Cl-Ar-CH=), 7.76-7.94 (m, 3H, Ar-CH=, Qu-5,7-H), 7.53-7.57 (m, 2H, Qu-6-H, Cl-Ar-3-H), 7.38-7.47 (m, 3H, Ar-3-H, Cl-Ar-5,6-H), 7.29-7.31 (m, 2H, Cl-Ar-4-H), 7.38-7.41 (m, 2H, Cl-Ar-C=CH, Ar-5-H), 7.15-7.17 (m, 2H, Ar-C=CH, Ar-4H), 6.78 (d, J = 16.5 Hz, 1H, Ar-6-H), 2.77 (s, 3H, CH3)
13C NMR: δ 188.5 (1C, s), 167.1 (1C, s), 153.2 (1C, s), 151.8 (1C, s), 151.1 (1C, s), 139.1 (1C, s), 137.5 (1C, s), 136.7 (1C, s), 135.4 (1C, s), 134.6 (1C, s), 134.1 (1C, s), 133.3 (1C, s), 131.8 (1C, s), 131.7 (1C, s), 129.2 (1C, s), 128.4 (1C, s), 128.0 (1C, s), 127.6 (1C, s), 127.4 (1C, s), 126.7 (1C, s), 125.8 (1C, s), 123.6 (1C, s), 121.0 (1C, s), 116.1 (1C, s), 17.7 (1C, s)

### benchmark_expand:R10
Molecular formula: C10H5ClO2
IR bands (cm-1): [658.0, 582.0, 936.0, 769.0]
1H NMR: 6.76 (s, 1H), 7.63 (t, J = 7.8 Hz, 1H), 7.77 (t, J = 7.8 Hz, 1H), 7.90 (d, J = 7.8 Hz, 1H), 8.17 (d, J = 7.8 Hz, 1H)
13C NMR: δ 127.7 (1C, s), 128.0 (1C, s), 130.2 (1C, s), 130.6 (1C, s), 132.2 (1C, s), 132.7 (1C, s), 135.9 (1C, s), 152.8 (1C, s), 178.1 (1C, s), 178.4 (1C, s)

### benchmark_expand:R101
Molecular formula: C17H18N4O2
IR bands (cm-1): [2980.0, 1614.0, 1512.0, 1426.0, 1283.0, 1244.0, 1103.0, 856.0, 816.0]
1H NMR: 9.50 (s, 1H, NH), 7.90 (s, 1H, H-8), 7.70 (d, 2H, J = 8.2 Hz, ArH-2’H, 6’H), 7.53 (s, 1H, H-5), 7.25 (d, 2H, J = 8.2 Hz, ArH-3’H, 5’H), 4.29 (q, 2H, J = 6.9 Hz, CH3CH2O-), 4.02 (s, 3H, CH3O-), 2.34 (s, 3H, ArH-4’CH3), 1.44 (t, 3H, J = 6.8 Hz, CH3CH2O-); LC-MS: 311.2 (M+H)+
13C NMR: δ 154.16 (1C, s), 153.19 (1C, s), 150.30 (1C, s), 141.62 (1C, s), 138.86 (1C, s), 128.72 (1C, s), 124.04 (1C, s), 122.70 (1C, s), 106.77 (1C, s), 103.82 (1C, s), 100.12 (1C, s), 64.73 (1C, s), 56.72 (1C, s), 20.89 (1C, s), 14.46 (1C, s)
