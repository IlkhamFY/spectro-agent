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
  {"benchmark_expand_500:R50": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R50
Molecular formula: C12H14O2
IR bands (cm-1): [2925.0, 2852.0, 1617.0, 1461.0, 1247.0, 1176.0, 1035.0, 737.0]
1H NMR: 2.18-2.26 (m, 1 H), 2.33-2.43 (m, 1 H), 3.80 (s, 3 H), 4.28-4.41 (m, 2 H), 4.51 (dd, J = 10.0 and 3.2 Hz, 1 H), 5.78-5.82 (m, 1 H), 5.89-5.94 (m, 1 H), 6.89 (d, J = 8.8 Hz, 2 H), 7.30 (d, J = 8.8 Hz, 2 H)
13C NMR: δ 33.0 (1C, s), 55.5 (1C, s), 66.8 (1C, s), 75.5 (1C, s), 114.0 (1C, s), 124.8 (1C, s), 126.7 (1C, s), 127.5 (1C, s), 135.0 (1C, s), 159.3 (1C, s)

### benchmark_expand_500:R53
Molecular formula: C12H18N2O5S
IR bands (cm-1): [3376.0, 2925.0, 1683.0, 1470.0]
1H NMR: 8.44 (s, 1H), 6.17 (s, 1H), 4.04 (d, J = 9.6 Hz, 1H), 3.95 (dd, J = 11.9, 3.6 Hz, 1H), 3.90 (dd, J = 11.8, 2.6 Hz, 1H), 3.77 (d, J = 11.3 Hz, 1H), 3.70 (d, J = 11.3 Hz, 1H), 3.34 (ddd, J = 9.5, 3.6, 2.6 Hz, 1H), 1.90 (d, J = 1.2 Hz, 3H), 0.98 (s, 3H) ppm
13C NMR: δ 166.3 (1C, s), 153.0 (1C, s), 140.8 (1C, s), 110.9 (1C, s), 78.7 (1C, s), 65.0 (1C, s), 64.1 (1C, s), 61.0 (1C, s), 55.5 (1C, s), 54.6 (1C, s), 17.3 (1C, s)

### benchmark_expand_500:R54
Molecular formula: C10H7ClF3N3O
IR bands (cm-1): [3294.0, 1689.0, 1655.0, 1491.0, 1349.0, 1316.0, 1194.0, 1133.0, 1085.0, 828.0]
1H NMR: 4.18 (dbr, J ≈ 1.5 Hz, 2 H, CH2), 5.39 (sbr, 1 H, NH), 7.36-7.38, 7.51-7.53 (2 m, 2 H each)
13C NMR: δ 43.8 (1C, t), 118.2 (1C, q), 125.7 (1C, s), 128.9 (1C, d), 132.7 (1C, s), 136.9 (1C, q), 138.5 (1C, s), 157.8 (1C, s)

### benchmark_expand_500:R56
Molecular formula: C18H30INOS
IR bands (cm-1): [2911.0, 2849.0, 1472.0, 1444.0, 1220.0, 1206.0, 1175.0, 1092.0, 1011.0, 967.0, 756.0, 749.0, 713.0, 686.0]
1H NMR: 7.77-7.83 (m, 2H), 7.65-7.70 (m, 1H), 7.57-7.64 (m, 2H), 3.44 (ddd, J = 14.0, 11.4, 5.1 Hz, 1H), 3.33 (ddd, J = 14.0, 11.3, 5.0 Hz, 1H), 1.74-1.85 (m, 1H), 1.57-1.68 (m, 1H), 1.15-1.35 (m, 18H), 0.88 (t, J = 6.9 Hz, 3H). 13C{1H} NMR (126 MHz, CDCl3): δ 138.9, 133.6, 129.6, 129.0, 55.2, 31.9, 29.6, 29.6, 29.5, 29.4, 29.3, 29.0, 28.1, 23.8, 22.7, 14.2
13C NMR: δ 138.9 (1C, s), 133.6 (1C, s), 129.6 (1C, s), 129.0 (1C, s), 55.2 (1C, s), 31.9 (1C, s), 29.6 (1C, s), 29.6 (1C, s), 29.5 (1C, s), 29.4 (1C, s), 29.3 (1C, s), 29.0 (1C, s), 28.1 (1C, s), 23.8 (1C, s), 22.7 (1C, s), 14.2 (1C, s)

### benchmark_expand_500:R58
Molecular formula: C8H14O3
IR bands (cm-1): [2970.0, 2896.0, 2827.0, 1733.0, 1456.0, 1378.0, 1216.0, 1152.0, 1103.0, 1038.0, 920.0]
1H NMR: 1.13 (d, J = 7.0 Hz, 3H), 2.65-2.75 (m, 1H), 3.41 (s, 3H), 3.81 (dd, J = 5.0, 2.3 Hz, 1H), 4.69 (d, J = 6.5 Hz, 1H), 4.74 (d, J = 6.5 Hz, 1H), 5.06-5.12 (m, 2H), 5.77-5.89 (m, 1H), 9.61 (d, J = 2.3 Hz, 1H)
13C NMR: δ 16.3 (1C, s), 39.8 (1C, s), 56.2 (1C, s), 85.7 (1C, s), 97.2 (1C, s), 116.4 (1C, s), 138.1 (1C, s), 203.2 (1C, s)

### benchmark_expand_500:R59
Molecular formula: C12H8N2O
IR bands (cm-1): [3059.0, 2985.0, 2232.0, 1464.0, 1210.0, 1094.0, 767.0, 706.0]
1H NMR: 8.35 (d, J = 5.0 Hz, 1H), 7.59-7.49 (m, 5H), 7.41 (d, J = 5.0 Hz, 1H)
13C NMR: δ 153.0 (1C, s), 143.9 (1C, s), 137.4 (1C, s), 132.8 (1C, s), 130.1 (1C, s), 129.9 (1C, s), 128.6 (1C, s), 128.0 (1C, s), 122.2 (1C, s), 115.1 (1C, s)
