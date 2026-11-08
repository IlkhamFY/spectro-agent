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
  {"benchmark_expand_500:R43": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R43
Molecular formula: C13H7O2S2-
IR bands (cm-1): [1713.0, 1458.0, 1435.0, 1350.0, 1273.0, 1211.0, 1169.0, 1076.0, 1034.0, 991.0, 779.0]
1H NMR: 8.29 (d, J = 8.0, 1H), 7.77 (d, J = 8.0, 1H), 7.63-7.53 (m, 1H), 7.48-7.25 (m, 4H), 3.85 (s, 3H); 13C{1H}NMR (CDCl3, 75 MHz): δ = 164.4, 145.8, 138.5, 138.0, 133.8, 128.9, 125.6, 125.4, 125.0, 124.5, 122.4, 121.6, 51.7; GC-
13C NMR: δ 164.4 (1C, s), 145.8 (1C, s), 138.5 (1C, s), 138.0 (1C, s), 133.8 (1C, s), 128.9 (1C, s), 125.6 (1C, s), 125.4 (1C, s), 125.0 (1C, s), 124.5 (1C, s), 122.4 (1C, s), 121.6 (1C, s)

### benchmark_expand_500:R44
Molecular formula: C24H44N6O7
IR bands (cm-1): [3299.0, 3072.0, 2971.0, 2928.0, 2856.0, 1723.0, 1693.0, 1646.0, 1533.0, 1448.0, 1411.0, 1388.0, 1362.0, 1335.0, 1306.0, 1258.0, 1192.0, 1078.0, 1022.0, 874.0, 759.0, 670.0, 493.0]
1H NMR: 7.53-7.48 (m, 2H), 3.62 (q, J = 4.0 Hz, 2H), 3.53 (q, J = 4.0 Hz, 2H), 3.44 (t, J = 8.0 Hz, 2H), 3.24-3.14 (m, 4H), 1.98-1.90 (m, 4H), 1.50-1.36 (m, 4H), 1.18 (s, 18H) ppm
13C NMR: δ 173.2 (1C, s), 173.0 (1C, s), 150.2 (1C, s), 73.6 (1C, s), 64.0 (1C, s), 55.6 (1C, s), 55.5 (1C, s), 38.8 (1C, s), 35.9 (1C, s), 27.6 (1C, s)

### benchmark_expand_500:R46
Molecular formula: C28H18ClFN4OS
IR bands (cm-1): [3112.0, 1651.0, 1323.0, 1105.0, 1411.0]
1H NMR: 3.93 (s, 3H, -OCH3), 7.28-7.41 (m, 5H, Ar-H), 7.49-7.54 (m, 4H, Ar-H), 7.55-7.80 (m, 3H, Ar-H), 7.83 (d, 1H, Ar-H, J = 8.0 Hz), 8.42 (s, 1H, Ar-H), 9.11 (s, 1H, Ar-H)
13C NMR: δ 56.5 (1C, s), 83.4 (1C, s), 103.7 (1C, s), 105.1 (1C, s), 114.9 (1C, s), 115.3 (1C, s), 115.6 (1C, s), 118.7 (1C, s), 121.2 (1C, s), 123.5 (1C, s), 126.5 (1C, s), 128.9 (1C, s), 130.5 (1C, s), 132.7 (1C, s), 134.7 (1C, s), 137.5 (1C, s), 137.7 (1C, s), 139.8 (1C, s), 147.2 (1C, s), 148.2 (1C, s), 149.7 (1C, s), 151.6 (1C, s), 152.1 (1C, s), 153.2 (1C, s), 167.5 (1C, s)

### benchmark_expand_500:R47
Molecular formula: C8H16N2
IR bands (cm-1): [3223.0, 2922.0, 1452.0, 1340.0, 1136.0, 833.0, 619.0]
1H NMR: 2.90-2.94 (t, 2H), 2.78-2.85 (q, 2H), 2.17-2.19 (q, 2H), 1.65-1.67 (d, J = 8 Hz, 2H), 1.59-1.62 (d, J = 12 Hz, 2H), 1.49 (s, 2H), 1.25- 1.30 (t, 2H), 1.13-1.18 (t, 2H)
13C NMR: δ 61.6 (1C, s), 47.4 (1C, s), 32.2 (1C, s)

### benchmark_expand_500:R51
Molecular formula: C23H21N5O3S2
IR bands (cm-1): [3424.0, 3058.0, 2925.0, 1749.0, 1674.0, 1595.0]
1H NMR: 1.20 (t, 3H, J = 7.1 Hz, CH2CH 3), 2.26 (s, 3H, CH3-Ar), 2.76 (s, 3H, CH3-thiazole), 4.19 (q, 2H, J = 7.1 Hz, CH 2CH3), 7.00-8.02 (m, 9H, ArH), 10.73 (s, br, 1H, D2O-exchangeable NH)
13C NMR: δ 13.9 (1C, s), 16.8 (1C, s), 20.1 (1C, s), 61.5 (1C, s), 114.5 (1C, s), 115.8 (1C, s), 117.1 (1C, s), 120.9 (1C, s), 121.9 (1C, s), 126.2 (1C, s), 128.1 (1C, s), 129.6 (1C, s), 130.8 (1C, s), 131.8 (1C, s), 138.3 (1C, s), 140.0 (1C, s), 159.4 (1C, s), 163.0 (1C, s)

### benchmark_expand_500:R52
Molecular formula: C30H25Br2N
IR bands (cm-1): [3068.0, 3046.0, 2961.0, 2866.0, 1584.0, 1502.0, 1452.0, 1418.0, 1375.0, 1263.0, 1025.0, 935.0, 829.0, 756.0]
1H NMR: 8.26 (d, J=8.3 Hz, 2H), 8.10 (d, J=8.4 Hz, 2H), 7.65 (d, J=8.1 Hz, 2H), 7.57 (ddd, J=8.4, 6.7, 1.1 Hz, 2H), 7.37 (ddd, J=8.2, 6.7, 1.0 Hz, 2H), 7.22-7.14 (m, 2H), 7.00 (d, J=8.0 Hz, 2H), 6.75-6.66 (m, 2H), 1.27 (s, 9H) ppm
13C NMR: δ 148.0 (1C, s), 145.7 (1C, s), 145.4 (1C, s), 133.7 (1C, s), 131.6 (1C, s), 130.4 (1C, s), 128.1 (1C, s), 127.9 (1C, s), 127.4 (1C, s), 126.4 (1C, s), 125.4 (1C, s), 125.1 (1C, s), 121.6 (1C, s), 119.5 (1C, s), 34.5 (1C, s)
