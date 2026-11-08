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
  {"benchmark_expand_500:R122": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R122
Molecular formula: C16H16N2O4
IR bands (cm-1): [3339.0, 3267.0, 3085.0, 3059.0, 3033.0, 2961.0, 2827.0, 2697.0, 1649.0, 1604.0, 1581.0, 1556.0, 1492.0, 1421.0, 1349.0, 1291.0, 1241.0, 1190.0, 1158.0, 1074.0, 1034.0, 1021.0, 923.0, 883.0, 800.0, 702.0, 685.0]
1H NMR: 5.50-5.55 (m, 2H), 5.95 (d, J = 4.5 Hz, 2H), 7.48 (t, J = 7.4 Hz, 3H), 7.54 (t, J = 7.2 Hz, 3H), 7.92 (d, J = 7.2 Hz, 4H), 8.69 (d, J = 7.8 Hz, 2H) ppm. 13C{1H} NMR (DMSO-d6): δ = 75.3, 127.9, 128.7, 131.8, 134.9, 166.6 ppm
13C NMR: δ 75.3 (1C, s), 127.9 (1C, s), 128.7 (1C, s), 131.8 (1C, s), 134.9 (1C, s)

### benchmark_expand_500:R126
Molecular formula: C7H4I2O3
IR bands (cm-1): [3256.0, 1667.0, 1582.0, 1480.0]
1H NMR: 11.32 (s, 1H), 8.25 (d, J = 2.1 Hz, 1H), 8.17 (d, J = 2.1 Hz, 1H)
13C NMR: δ 170.45 (1C, s), 160.81 (1C, s), 153.15 (1C, s), 139.32 (1C, s), 113.17 (1C, s), 87.05 (1C, s), 81.00 (1C, s)

### benchmark_expand_500:R13
Molecular formula: C12H13BrO4
IR bands (cm-1): [2950.0, 1738.0, 1730.0, 1604.0, 1464.0, 1236.0, 1122.0, 1040.0, 943.0, 715.0]
1H NMR: 8.30 (1H, d, J = 1.2 Hz, H-3), 8.01 (1H, dd, J = 8.4, 1.2 Hz, H-5), 7.80 (1H, d, J = 8.4 Hz, H-6), 4.44-4.39 (4H, m), 1.43-1.40 (6H, m)
13C NMR: δ 165.8 (1C, s), 164.5 (1C, s), 136.4 (1C, s), 135.0 (1C, s), 133.9 (1C, s), 130.8 (1C, s), 128.0 (1C, s), 121.2 (1C, s), 62.0 (1C, s), 61.7 (1C, s), 14.2 (1C, s)

### benchmark_expand_500:R131
Molecular formula: C15H30O3
IR bands (cm-1): [2960.0, 2935.0, 2873.0, 1729.0, 1467.0, 1074.0]
1H NMR: 4.45 (s, 1H), 3.59-3.37 (m, 4H), 2.50 (t, J = 7.6 Hz, 2H), 1.55-1.47 (m, 4H), 1.36-1.27 (m, 4H), 0.87-0.81 (m, 12H) ppm; 13C{1H}NMR (100 MHz, CDCl3): δ 205.6, 102.1, 66.5, 44.6, 33.7, 30.6, 26.6, 21.3, 18.2, 12.8 ppm
13C NMR: δ 205.6 (1C, s), 102.1 (1C, s), 66.5 (1C, s), 44.6 (1C, s), 33.7 (1C, s), 30.6 (1C, s), 26.6 (1C, s), 21.3 (1C, s), 18.2 (1C, s)

### benchmark_expand_500:R132
Molecular formula: C11H11FN4O
IR bands (cm-1): [3424.0, 3133.0, 3095.0, 2871.0, 1621.0, 1589.0, 1561.0, 1484.0, 1229.0, 1181.0]
1H NMR: 8.31 (s, 1H), 7.55-7.50 (m, 2H), 7.47-7.44 (m, 1H), 7.43-7.39 (m, 1H), 7.10-7.07 (m, 1H), 5.38-5.34 (d, J = 4.2 Hz, 2H), 3.69 (d, J = 0.7 Hz, 3H)
13C NMR: δ 163.22 (1C, d), 147.05 (1C, s), 132.48 (1C, d), 131.54 (1C, s), 130.46 (1C, d), 121.45 (1C, s), 121.40 (1C, d), 115.15 (1C, d), 112.75 (1C, d), 52.83 (1C, s), 45.63 (1C, s)

### benchmark_expand_500:R134
Molecular formula: C9H14N2O4
IR bands (cm-1): [3376.0, 3361.0, 1709.0, 1521.0, 1171.0]
1H NMR: 11.18 (s, 1H), 7.42 (d, J = 8.1 Hz, 1H), 4.33-4.24 (m, 1H), 2.85 (dd, J = 17.5, 9.4 Hz, 1H), 2.44 (dd, J = 17.5, 5.7 Hz, 1H), 1.37 (s, 9H)
13C NMR: δ 178.2 (1C, s), 176.5 (1C, s), 155.2 (1C, s), 78.8 (1C, s), 50.3 (1C, s), 36.4 (1C, s), 28.2 (1C, s)
