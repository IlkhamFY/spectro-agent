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
  {"benchmark_expand:R01": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R01
Molecular formula: C12H14O3
IR bands (cm-1): [2928.0, 2845.0, 1674.0, 1596.0, 1443.0, 1257.0, 1198.0, 1112.0, 1028.0, 815.0, 549.0, 406.0]
1H NMR: 10.30 (s, 1 H), 7.79 (d, J = 8.5 Hz, 1 H), 6.52 (dd, J = 9.0, 2.5 Hz, 1 H), 6.41 (d, J = 2.5 Hz, 1 H), 5.92-5.84 (m, 1 H), 5.19-5.15 (m, 1 H), 5.11 (d, J = 10.0 Hz, 1 H), 4.08 (t, J = 6.5 Hz, 2 H), 3.84 (s, 3 H), 2.60-2.56 (m, 2 H); 13C{1H} NMR (125 MHz, CDCl3) δ 188.5, 166.3, 163.3, 134.1, 130.4, 119.4, 117.8, 106.2, 98.8, 67.9, 55.8, 33.6
13C NMR: δ 188.5 (1C, s), 166.3 (1C, s), 163.3 (1C, s), 134.1 (1C, s), 130.4 (1C, s), 119.4 (1C, s), 117.8 (1C, s), 106.2 (1C, s), 98.8 (1C, s), 67.9 (1C, s), 55.8 (1C, s), 33.6 (1C, s)

### benchmark_expand:R02
Molecular formula: C16H24O4Si
IR bands (cm-1): [1738.0, 1597.0, 1280.0, 1203.0, 1161.0, 909.0]
1H NMR: 7.94 (d, J = 8.7 Hz, 2H), 6.91 (d, J = 8.7 Hz, 2H), 4.43 (q, J = 7.2 Hz, 2H), 1.42 (t, J = 7.2 Hz, 3H), 0.99 (s, 9H), 0.25 (s, 6H)
13C NMR: δ 185.1 (1C, s), 164.3 (1C, s), 162.1 (1C, s), 132.6 (1C, s), 126.0 (1C, s), 120.4 (1C, s), 62.2 (1C, s), 25.6 (1C, s), 18.3 (1C, s), 14.2 (1C, s), -4.3 (1C, s)

### benchmark_expand:R04
Molecular formula: C12H15BrO
IR bands (cm-1): [3400.0, 2922.0, 2850.0, 1701.0, 1606.0, 1495.0, 1448.0, 1279.0, 1174.0]
1H NMR: 7.28 (d, J = 4.0 Hz, 1H), 7.04 (dd, J = 8.0 Hz, 1H), 6.93 (d, 1H), 5.37 (s, 1H), 2.44-2.38 (m, 1H), 1.84-1.68 (m, 5H), 1.39-1.19 (m, 5H) ppm
13C NMR: δ 150.2 (1C, s), 142.0 (1C, s), 130.0 (1C, s), 127.6 (1C, s), 115.8 (1C, s), 110.0 (1C, s), 43.5 (1C, s), 34.6 (1C, s), 26.8 (1C, s)

### benchmark_expand:R07
Molecular formula: C8H5NO2
IR bands (cm-1): [3171.0, 2871.0, 2233.0, 1679.0, 1584.0, 1505.0, 1440.0, 1367.0, 1296.0, 1254.0, 1105.0, 955.0, 841.0]
1H NMR: 9.78 (s, 1H, CHO), 8.17 (d, J = 2.0 Hz, 1H, Ar), 7.98 (dd, J = 8.5, 2.0 Hz, 1H, Ar), 7.13 (d, J = 8.5 Hz, 1H, Ar)
13C NMR: δ 190.7 (1C, s), 165.6 (1C, s), 137.3 (1C, s), 135.3 (1C, s), 128.7 (1C, s), 117.3 (1C, s), 116.5 (1C, s), 100.1 (1C, s)

### benchmark_expand:R09
Molecular formula: C14H21NO3
IR bands (cm-1): [2928.0, 2856.0, 1594.0, 1514.0, 1342.0, 1112.0]
1H NMR: 8.18 (AB-d, J 9.2, 2H, H3), 6.93 (AB-d, J 9.2, 2H, H2), 4.04 (t, J 6.4, 2H, H5), 1.82 (q, J 7.4, 2H, H6), 1.46 (q, J 7.6, 2H, H7), 1.29 (m, 8H, H8-11), 0.89 (t, J 7.2, 3H, H12)
13C NMR: δ 164.4 (1C, s), 141.5 (1C, s), 126.0 (1C, s), 114.5 (1C, s), 69.1 (1C, s), 31.9 (1C, s), 29.4 (1C, s), 29.3 (1C, s), 29.1 (1C, s), 26.0 (1C, s), 22.8 (1C, s), 14.2 (1C, s)

### benchmark_expand:R100
Molecular formula: C12H11N3O5
IR bands (cm-1): [2955.0, 1724.0, 1595.0, 1421.0, 1155.0, 1023.0, 854.0, 767.0]
1H NMR: 8.30 (d, J = 8.9 Hz, 2H), 8.08 (d, J = 8.9 Hz, 2H), 5.96 (s, 1H), 4.28 (q, J = 7.1 Hz, 2H), 1.29 (t, J = 7.1 Hz, 3H)
13C NMR: δ 161.9 (1C, s), 155.1 (1C, s), 145.3 (1C, s), 144.1 (1C, s), 143.6 (1C, s), 125.2 (1C, s), 121.7 (1C, s), 90.1 (1C, s), 60.9 (1C, s), 14.6 (1C, s)
