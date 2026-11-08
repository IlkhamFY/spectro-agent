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
  {"benchmark_expand_500:R224": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R224
Molecular formula: C23H18BrN5S
IR bands (cm-1): [925.0, 597.0, 507.0, 523.0, 854.0]
1H NMR: 8.80 (s, 1H, triazole CH), 7.87 (d, J = 8.4 Hz, 2H, Ar-H-3 ‶,5 ‶), 7.68-7.57 (m, 4H, Ar-H), 7.45 (d, J = 7.3 Hz, 2H, Ar-H), 7.40-7.14 (m, 5H, Ar-H), 5.49 (s, 2H, N-CH2(, 4.62 (s, 2H, S-CH2)
13C NMR: δ 143.7 (1C, s), 137.7 (1C, s), 135.6 (1C, s), 133.5 (1C, s), 131 (1C, s), 130.2 (1C, s), 129.4 (1C, s), 128.9 (1C, s), 127.9 (1C, s), 122.3 (1C, s), 122.2 (1C, s), 118.2 (1C, s), 110.5 (1C, s), 39.3 (1C, s), 31.1 (1C, s)

### benchmark_expand_500:R225
Molecular formula: C25H18FN5O4
IR bands (cm-1): [3441.0, 1686.0, 1328.0, 1201.0, 989.0]
1H NMR: 10.75 (s, 1H), 8.33 (s, 1H), 7.93 (ddt, J = 20.0, 5.5, 3.2 Hz, 4H), 7.58 (dt, J = 11.6, 2.1 Hz, 1H), 7.46-7.25 (m, 4H), 7.21 (d, J = 8.5 Hz, 2H), 6.93 (td, J = 8.4, 2.5 Hz, 1H), 5.41 (s, 2H), 5.27 (s, 2H)
13C NMR: δ 167.72 (1C, s), 165.10 (1C, s), 163.79 (1C, s), 158.11 (1C, s), 142.90 (1C, s), 140.61 (1C, s), 135.07 (1C, s), 132.03 (1C, s), 131.13 (1C, s), 113.04 (1C, s), 129.25 (1C, s), 126.92 (1C, s), 125.18 (1C, s), 123.79 (1C, s), 115.48 (1C, s), 115.45 (1C, s), 110.86 (1C, s), 106.67 (1C, s), 61.70 (1C, s)

### benchmark_expand_500:R229
Molecular formula: C24H22ClN3O2
IR bands (cm-1): [3195.0, 3103.0, 3025.0, 2998.0, 2928.0, 2835.0, 1672.0, 1621.0, 1558.0, 1493.0, 1442.0, 1407.0, 1338.0, 1284.0, 1254.0, 1200.0, 1138.0, 1086.0, 1045.0, 977.0, 947.0, 799.0, 748.0, 708.0, 680.0, 634.0, 593.0, 550.0, 497.0]
1H NMR: 8.41 (t, 1H, J = 5.9 Hz), 8.17 (d, 1H, J = 5.2 Hz), 8.09 (d, 1H, J = 8.6 Hz), 7.88 (d, 1H, J = 5.2 Hz), 7.59 (d, 2H, J = 8.5 Hz), 7.49-7.42 (m, 3H), 7.26 (d, 1H, J = 2.0 Hz), 6.87 (dd, 1H, J = 8.6, 2.1 Hz), 6.55 (d, 1H, J = 15.8 Hz), 4.67 (t, 2H, J = 6.8 Hz), 3.89 (s, 3H), 3.59 (q, 2H, J = 6.5 Hz), 2.99 (s, 3H)
13C NMR: δ 165.53 (1C, s), 160.50 (1C, s), 142.90 (1C, s), 140.63 (1C, s), 137.83 (1C, s), 134.64 (1C, s), 133.99 (1C, s), 133.70 (1C, s), 129.29 (1C, s), 128.98 (1C, s), 128.48 (1C, s), 122.44 (1C, s), 122.38 (1C, s), 114.28 (1C, s), 112.26 (1C, s), 109.39 (1C, s), 93.50 (1C, s), 55.39 (1C, s), 43.34 (1C, s), 39.10 (1C, s), 23.07 (1C, s)

### benchmark_expand_500:R230
Molecular formula: C7H4BrIN2O
IR bands (cm-1): [3064.0, 2944.0, 1703.0, 1605.0, 1572.0, 1481.0, 1444.0, 1247.0, 1023.0, 954.0, 825.0]
1H NMR: 11.06 (s, 1H), 10.99 (s, 1H), 7.42 (d, J = 1.7 Hz, 1H), 7.05 (d, J = 1.7 Hz, 1H)
13C NMR: δ 155.0 (1C, s), 132.9 (1C, s), 131.0 (1C, s), 130.7 (1C, s), 113.3 (1C, s), 111.3 (1C, s), 73.9 (1C, s)

### benchmark_expand_500:R25
Molecular formula: C36H47N3O6S
IR bands (cm-1): [3350.0, 2924.0, 2869.0, 2360.0, 1685.0, 1666.0, 1641.0, 1521.0, 1481.0, 1449.0, 1387.0, 1364.0, 1341.0, 1267.0, 1245.0, 1213.0, 1195.0, 1154.0, 1070.0, 1039.0, 1006.0, 977.0, 912.0, 900.0, 883.0, 866.0, 830.0, 762.0, 716.0, 689.0, 673.0]
1H NMR: 10.50 (s, 1H, NH), 8.81 (s, 1H, ArH), 7.91-7.84 (m, 2H, ArH), 7.77-7.59 (m, 7H, NH, ArH), 7.47 (t, J = 7.8 Hz, 2H, ArH), 7.37 (t, J = 7.1 Hz, 1H, ArH), 4.81 (bs, 1H, NH), 3.49 (q, J = 6.3 Hz, 2H, CH2), 3.30-3.15 (m, 4H, CH2), 1.88-1.71 (m, 4H, CH2), 1.45 (s, 9H, CH3), 1.49-1.16 (m, 10H, CH2), 0.86 (t, J = 7.1 Hz, 3H, CH3)
13C NMR: δ 191.5 (1C, s), 162.9 (1C, s), 156.9 (1C, s), 141.1 (1C, s), 140.8 (1C, s), 140.6 (1C, s), 137.9 (1C, s), 135.2 (1C, s), 135.0 (1C, s), 133.5 (1C, s), 129.0 (1C, s), 127.9 (1C, s), 127.7 (1C, s), 127.3 (1C, s), 127.2 (1C, s), 119.4 (1C, s), 118.6 (1C, s), 79.9 (1C, s), 52.8 (1C, s), 37.3 (1C, s), 36.4 (1C, s), 31.8 (1C, s), 30.2 (1C, s), 29.1 (1C, s), 29.0 (1C, s), 28.5 (1C, s), 28.2 (1C, s), 23.6 (1C, s), 22.7 (1C, s), 14.2 (1C, s)

### benchmark_expand_500:R27
Molecular formula: C22H17Cl2N3O
IR bands (cm-1): [3400.0, 3300.0, 3010.0, 2250.0, 1680.0, 1650.0, 850.0, 453.0]
1H NMR: 7.63 (s, 1H, CHC), 7.58 (dd, J = 8, 7.7 Hz, 2H, ArH), 7.57 (dd, J = 7.5, 8.2 Hz, 2H, ArH), 7.55 (dd, J = 8, 7.4 Hz, 2H, ArH), 7.54 (dd, J = 8, 7.6 Hz, 2H, ArH), 7.53 (s, 2H, NH2 D2O exchangeable), 7.52 (s, 1H, C4-H) 4.75 (s, 2H, CH2-N), 4.74 (s, 2H, CH2-N), 1.84 (s, 3H, CH3)
13C NMR: δ 185.3 (1C, s), 161.4 (1C, s), 148.58 (1C, s), 142.9 (1C, s), 142.4 (1C, s), 136.8 (1C, s), 134.4 (1C, s), 130.8 (1C, s), 129.1 (1C, s), 129.0 (1C, s), 128.7 (1C, s), 124.42 (1C, s), 115.84 (1C, s), 115.80 (1C, s), 115.09 (1C, s), 115.01 (1C, s), 55.72 (1C, s), 47.11 (1C, s), 42.43 (1C, s), 20.93 (1C, s)
