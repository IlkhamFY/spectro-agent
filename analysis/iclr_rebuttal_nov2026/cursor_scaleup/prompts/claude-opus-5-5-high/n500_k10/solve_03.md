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
  {"benchmark_main:R138": ["CCO", "COC"]}

Compounds:

### benchmark_main:R138
Molecular formula: C10H13NO3
IR bands (cm-1): [2980.0, 1604.0, 1590.0, 1515.0, 1492.0, 1370.0, 1343.0, 1263.0, 1163.0, 1112.0, 897.0]
1H NMR: 8.16 (d, J = 9.2 Hz, 2H), 7.05 (d, J = 9.2 Hz, 2H), 1.46 (s, 9H)
13C NMR: δ 161.9 (1C, s), 142.5 (1C, s), 125.2 (1C, s), 121.7 (1C, s), 80.6 (1C, s), 28.9 (1C, s)

### benchmark_main:R139
Molecular formula: C13H25NO2
IR bands (cm-1): [2932.0, 2866.0, 1691.0, 1416.0, 1366.0, 1173.0, 1148.0, 926.0, 878.0, 768.0]
1H NMR: 4.18 (br s, 1H), 3.94 (br d, 1H), 2.72 (br t, 1H), 1.16-1.70 (m, 10H), 1.42 (s, 9H), 0.89 (t, J = 7.2 Hz, 3H)
13C NMR: δ 155.3 (1C, s), 79.0 (1C, s), 50.3 (1C, s), 38.3 (1C, s), 32.1 (1C, s), 28.6 (1C, s), 25.9 (1C, s), 19.6 (1C, s), 19.2 (1C, s)

### benchmark_main:R140
Molecular formula: C16H14
IR bands (cm-1): [3288.0, 3032.0, 2974.0, 2869.0, 2111.0, 1595.0, 1293.0, 835.0, 762.0, 627.0, 531.0]
1H NMR: 7.70-7.53 (m, 4H), 7.52-7.41 (m, 4H), 7.36-7.33 (m, 1H), 3.83 (qd, J = 7.2, 2.4 Hz, 1H), 2.30 (d, J = 2.5 Hz, 1H), 1.57 (d, J = 7.2 Hz, 3H)
13C NMR: δ 141.9 (1C, s), 141.1 (1C, s), 140.0 (1C, s), 128.9 (1C, s), 127.6 (1C, s), 127.4 (1C, s), 127.4 (1C, s), 127.3 (1C, s), 87.3 (1C, s), 70.5 (1C, s), 31.5 (1C, s), 24.4 (1C, s)

### benchmark_main:R18
Molecular formula: C14H19FOSi
IR bands (cm-1): [3071.0, 2959.0, 1645.0, 1512.0, 1250.0, 844.0]
1H NMR: 7.03 (m, 2 H), 6.90 (m, 2 H), 2.67 (m, 2 H), 1.60 (dt, J = 4.5, 9.0 Hz, 1 H), 1.23 (m, 1 H), 0.90 (dt, J = 5.0, 8.5 Hz, 1 H), 0.72 (dt, J = 5.0, 8.5 Hz, 1 H), 0.18 (s, 9 H)
13C NMR: δ 247.1 (1C, s), 161.1 (1C, d), 138.3 (1C, d), 127.5 (1C, d), 114.9 (1C, d), 53.0 (1C, s), 22.1 (1C, s), 16.3 (1C, s), 15.2 (1C, s), -3.2 (1C, s)

### benchmark_main:R19
Molecular formula: C9H9ClO3S
IR bands (cm-1): [3480.0, 3021.0, 1490.0, 1297.0, 1214.0, 1177.0, 1132.0, 1096.0, 1011.0, 828.0, 754.0, 638.0, 543.0]
1H NMR: 7.57 (d, J = 8.7 Hz, 2H, 2 × Ar-H), 7.48 (d, J = 8.6 Hz, 2H, 2 × Ar-H), 6.83 (s, 1H, OH), 4.68 (d, J = 15.3 Hz, 2H, CHH-S-CHH), 4.37 (d, J = 15.4 Hz, 2H, CHH-S-CHH); 13C{1H} NMR (101 MHz, DMSO) δ 143.0 (Ar-Cq), 132.4 (Ar-Cq), 128.3 (2 × Ar-C), 127.2 (2 × Ar-C), 78.3 (2 × CH2-S), 62.5 (Cq)
13C NMR: δ 143.0 (1C, s), 132.4 (1C, s), 128.3 (1C, s), 127.2 (1C, s), 78.3 (1C, s), 62.5 (1C, s)

### benchmark_main:R22
Molecular formula: C17H26OSi
IR bands (cm-1): [2926.0, 2828.0, 1634.0, 1399.0, 1125.0, 1026.0, 699.0]
1H NMR: 0.60 (q, J = 7.6 Hz, 6 H), 0.95 (t, J = 7.6 Hz, 9 H), 2.20-2.29 (m, 1 H), 2.30-2.37 (m, 1 H), 4.40-4.42 (m, 2 H), 4.48 (dd, J = 10.0 and 3.2 Hz, 1 H), 6.03-6.04 (m, 1 H), 5.89-5.95 (m, 1 H), 7.25-7.30 (m, 1 H), 7.33-7.40 (m, 4 H)
13C NMR: δ 2.6 (1C, s), 7.6 (1C, s), 35.5 (1C, s), 68.0 (1C, s), 76.0 (1C, s), 126.1 (1C, s), 127.7 (1C, s), 128.6 (1C, s), 134.2 (1C, s), 135.7 (1C, s), 143.2 (1C, s)
