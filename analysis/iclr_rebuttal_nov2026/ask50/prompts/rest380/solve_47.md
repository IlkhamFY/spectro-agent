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
  {"benchmark_expand_500:R02": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R02
Molecular formula: C11H16NO3S2-
IR bands (cm-1): [1132.0, 1324.0, 1576.0, 1588.0, 1602.0, 1632.0, 1688.0, 3238.0]
1H NMR: 0.90 (d, J = 6.8 Hz, 3H, CH(CH3)2), 1.03 (d, J = 6.9 Hz, 3H, CH(CH3)2), 1.88 (s, 3H, CH3), 2.40 (m, 1H, CH(CH3)2), 7.40 (d, J = 7.92 Hz, 2H, Ar-H), 7.82 (d, J = 8.0 Hz, 2H, Ar-H), 10.22 (s, 1H, NH)
13C NMR: δ 23.24 (1C, s), 24.63 (1C, s), 25.15 (1C, s), 36.47 (1C, s), 119.13 (1C, s), 119.13 (1C, s), 123.85 (1C, s), 123.85 (1C, s), 140.13 (1C, s), 144.39 (1C, s), 169.29 (1C, s)

### benchmark_expand_500:R05
Molecular formula: C12H12BrN3
IR bands (cm-1): [3408.0, 2962.0, 1595.0, 1564.0, 1519.0]
1H NMR: 2.33 (s, 6H, 2CH3), 6.47 (s, 1H, Ar Pyr), 7.36 (d, J = 8.7, 2H, Ar), 7.54 (d, J = 8.7, 2H, Ar), 7.67 (s, 1H, NH)
13C NMR: δ 23.9 (1C, s), 111.9 (1C, s), 114.1 (1C, s), 120.4 (1C, s), 131.6 (1C, s), 139.1 (1C, s), 159.4 (1C, s), 167.6 (1C, s)

### benchmark_expand_500:R08
Molecular formula: C12H10ClNO2Se
IR bands (cm-1): [3088.0, 2952.0, 2854.0, 2149.0, 1716.0, 1583.0, 1453.0, 1287.0, 1197.0, 1082.0, 793.0]
1H NMR: 7.84 (s, 1H), 7.45 (d, J = 8.7 Hz, 2H), 7.37 (d, J = 8.2 Hz, 2H), 4.15 (s, 2H), 3.88 (s, 3H)
13C NMR: δ 166.8 (1C, s), 141.8 (1C, s), 135.8 (1C, s), 132.2 (1C, s), 130.6 (1C, s), 129.3 (1C, s), 127.7 (1C, s), 102.4 (1C, s), 52.8 (1C, s), 25.4 (1C, s)

### benchmark_expand_500:R101
Molecular formula: C11H10Br2O2
IR bands (cm-1): [3083.0, 3011.0, 2956.0, 1709.0, 1625.0, 1582.0, 1448.0, 1357.0, 1285.0, 1215.0, 1156.0]
1H NMR: 3.90 (s, 3H), 4.24 (s, 2H), 7.26 (t, J 7.8 Hz, 1H), 7.42 (t, J 7.8 Hz, 1H), 7.63 (d, J 7.8 Hz, 1H), 7.68 (d, J 7.8 Hz, 1H), 7.84 (s, 1H)
13C NMR: δ 26.3 (1C, s), 52.7 (1C, s), 124.5 (1C, s), 127.7 (1C, s), 129.7 (1C, s), 130.3 (1C, s), 130.8 (1C, s), 133.1 (1C, s), 134.8 (1C, s), 141.8 (1C, s), 166.1 (1C, s)

### benchmark_expand_500:R104
Molecular formula: C17H16O4
IR bands (cm-1): [2997.0, 2955.0, 2929.0, 2845.0, 2162.0, 1714.0, 1657.0, 1604.0, 1554.0, 1280.0, 1247.0, 831.0, 768.0]
1H NMR: 8.09 (d, J = 8.0 Hz, 2H), 7.81 (d, J = 8.0 Hz, 1H), 7.63 (d, J = 8.0 Hz, 2H), 7.20 (d, J = 8.0 Hz, 1H), 7.14 (s, 1H), 3.97 (s, 3H), 3.91 (s, 3H), 2.62 (s, 3H)
13C NMR: δ 199.3 (1C, s), 166.9 (1C, s), 159.5 (1C, s), 145.6 (1C, s), 144.7 (1C, s), 131.3 (1C, s), 130.3 (1C, s), 129.9 (1C, s), 127.5 (1C, s), 127.4 (1C, s), 119.8 (1C, s), 110.7 (1C, s), 55.8 (1C, s), 52.4 (1C, s), 32.1 (1C, s)

### benchmark_expand_500:R109
Molecular formula: C7H13N3
IR bands (cm-1): [3421.0, 1617.0, 1490.0, 1460.0, 1413.0]
1H NMR: 7.23 (d, J = 2.4 Hz, 1H), 5.24 (d, J = 2.4 Hz, 1H), 3.63 (br s, 2H), 1.49 (s, 9H)
13C NMR: δ 153.69 (1C, s), 126.82 (1C, s), 92.15 (1C, s), 57.39 (1C, s), 29.70 (1C, s)
