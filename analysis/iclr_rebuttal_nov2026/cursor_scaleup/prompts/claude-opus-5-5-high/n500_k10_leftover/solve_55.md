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
  {"benchmark_expand_500:R189": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R189
Molecular formula: C14H23NO4
IR bands (cm-1): [1200.0, 1340.0, 1363.0, 1448.0, 1506.0, 1558.0, 1683.0, 1699.0, 1734.0]
1H NMR: 0.90 (3H, t, J = 7.0 Hz), 1.25-1.56 (6H, m), 1.78-1.92 (2H, m), 3.08 (1H, br), 3.71 (3H, s), 3.74 (3H, s), 4.17-4.18 (1H, m), 4.88 (1H, br), 5.09-5.15 (2H, m), 5.81 (1H, ddd, J = 17.1, 10.7, 6.4 Hz)
13C NMR: δ 13.86 (1C, s), 19.88 (1C, s), 21.03 (1C, s), 22.45 (1C, s), 34.59 (1C, s), 36.52 (1C, s), 50.96 (1C, s), 51.99 (1C, s), 52.75 (1C, s), 55.07 (1C, s), 115.16 (1C, s), 139.00 (1C, s), 157.08 (1C, s), 172.86 (1C, s)

### benchmark_expand_500:R19
Molecular formula: C8H10N2O2
IR bands (cm-1): [3122.0, 3088.0, 2943.0, 2823.0, 1673.0, 1568.0, 1507.0, 1492.0, 1429.0, 1404.0, 1343.0, 1202.0, 1179.0, 1009.0]
1H NMR: 3.78 (s, 3H, CH3), 4.79 (dt, J = 5.6, 1.5 Hz, 2H, OCH2), 5.29 (dq, J = 10.5, 1.4 Hz, 1H, OCH2CHCH2), 5.43 (dq, J = 17.2, 1.6 Hz, 1H, OCH2CHCH2), 6.09 (ddt, J = 17.2, 10.5, 5.6 Hz, 1H, OCH2CHCH2), 7.69 (s, 1H, 5-H), 9.75 (s, 1H, CHO)
13C NMR: δ 39.7 (1C, s), 69.9 (1C, s), 109.5 (1C, s), 118.3 (1C, s), 132.6 (1C, s), 133.4 (1C, s), 163.1 (1C, s)

### benchmark_expand_500:R190
Molecular formula: C11H24O
IR bands (cm-1): [3728.0, 3627.0, 3344.0, 2925.0, 2825.0, 1464.0, 1378.0, 1056.0, 721.0]
1H NMR: 3.60 (t, J = 6.7 Hz, 2H), 1.57-1.49 (m, 2H), 1.35-1.20 (m, 16H), 0.86 (t, J = 6.8 Hz, 3H)
13C NMR: δ 63.1 (1C, s), 32.8 (1C, s), 31.9 (1C, s), 29.6 (1C, s), 29.4 (1C, s), 29.3 (1C, s), 25.7 (1C, s), 22.7 (1C, s), 14.1 (1C, s)

### benchmark_expand_500:R191
Molecular formula: C16H22O4
IR bands (cm-1): [734.0, 921.0, 1749.0, 1730.0, 498.0, 455.0, 849.0, 700.0, 677.0, 648.0]
1H NMR: 7.35-7.15 (m, 5H), 4.40-4.26 (m, 2H), 3.32 (q, J = 7.3 Hz, 1H), 2.94 (t, J = 7.1 Hz, 2H), 1.42 (s, 9H), 1.34 (d, J = 7.3 Hz, 3H) ppm
13C NMR: δ 172.77 (1C, s), 171.69 (1C, s), 139.97 (1C, s), 130.75 (1C, s), 130.32 (1C, s), 128.38 (1C, s), 83.59 (1C, s), 67.67 (1C, s), 36.71 (1C, s), 28.90 (1C, s)

### benchmark_expand_500:R197
Molecular formula: C13H19NO2S
IR bands (cm-1): [3011.0, 2975.0, 2925.0, 1625.0, 1361.0, 1275.0, 1163.0, 1079.0, 985.0, 835.0, 817.0, 786.0, 753.0]
1H NMR: 7.64 (d, J = 8.1 Hz, 2H, 2 × Ar-H), 7.31 (d, J = 8.2 Hz, 2H, 2 × Ar-H), 2.76 (s, 3H, SCH3), 2.39 (s, 3H, Ar-CH3), 1.44 (s, 9H, (CH3)3); 13C{1H} NMR (101 MHz, CDCl3) δ 164.4 (C=O), 142.8 (Ar-Cq), 133.6 (Ar-Cq), 130.5 (2 × Ar-C), 126.1 (2 × Ar-C), 78.9 (C(CH3)3), 35.8 (SCH3), 28.4 (C(CH3)3), 21.4 (Ar-CH3)
13C NMR: δ 164.4 (1C, s), 142.8 (1C, s), 133.6 (1C, s), 130.5 (1C, s), 126.1 (1C, s), 78.9 (1C, s), 35.8 (1C, s), 28.4 (1C, s), 21.4 (1C, s)

### benchmark_expand_500:R198
Molecular formula: C18H21NO2
IR bands (cm-1): [3447.0, 2978.0, 2877.0, 2240.0, 2214.0, 1737.0, 1449.0, 1370.0, 1256.0, 1150.0, 840.0, 695.0, 513.0]
1H NMR: 7.39-7.31 (m, 4H), 7.29-7.24 (m, 1H), 6.85 (t, J = 2.6 Hz, 1H), 2.78-2.71 (m, 2H), 2.59-2.50 (m, 1H), 2.32-2.24 (m, 1H), 2.14-2.03 (m, 1H), 2.01-1.90 (m, 1H), 1.52 (s, 9H)
13C NMR: δ 166.7 (1C, s), 141.3 (1C, s), 136.4 (1C, s), 128.6 (1C, s), 128.5 (1C, s), 128.3 (1C, s), 127.5 (1C, s), 127.1 (1C, s), 120.1 (1C, s), 83.8 (1C, s), 53.6 (1C, s), 36.4 (1C, s), 30.8 (1C, s), 27.7 (1C, s), 25.1 (1C, s)
