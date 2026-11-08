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
  {"benchmark_expand_500:R103": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R103
Molecular formula: C27H27NO4
IR bands (cm-1): [2925.0, 1744.0, 1689.0, 1530.0, 1449.0, 1270.0, 1156.0, 1030.0, 736.0, 696.0]
1H NMR: 7.78-7.77 (d, J = 7.2 Hz, 2H), 7.61-7.60 (d, J = 7.2 Hz, 2H), 7.42-7.40 (t, J = 7.2 Hz, 2H), 7.36-7.31 (m, 3H), 5.35 (br, 1H), 5.23-5.15 (m, 2H), 4.41-4.36 (m, 3H), 4.25-4.22 (t, J = 7.2 Hz, 1H), 2.23-2.18 (m, 1H), 0.96-0.95 (d, J = 6.6 Hz, 3H), 0.88-0.87 (d, J = 7.2 Hz, 3H)
13C NMR: δ 172.2 (1C, s), 156.4 (1C, s), 144.1 (1C, s), 143.9 (1C, s), 141.5 (1C, s), 135.5 (1C, s), 128.8 (1C, s), 128.7 (1C, s), 128.6 (1C, s), 127.9 (1C, s), 127.2 (1C, s), 125.3 (1C, s), 120.2 (1C, s), 67.3 (1C, s), 67.2 (1C, s), 59.2 (1C, s), 47.4 (1C, s), 31.5 (1C, s), 19.2 (1C, s), 17.7 (1C, s)

### benchmark_expand_500:R106
Molecular formula: C23H17FO5
IR bands (cm-1): [3029.0, 2996.0, 2952.0, 1726.0, 1657.0, 1579.0, 1459.0, 1401.0, 1297.0, 1151.0, 1129.0, 941.0, 907.0, 880.0, 847.0, 794.0, 750.0, 724.0, 697.0, 673.0, 646.0, 568.0, 523.0, 483.0]
1H NMR: 8.15 (d, J = 8.0 Hz, 1H), 7.59 (d, J = 8.0 Hz, 2H), 7.57 (s, 1H), 7.55 (d, J = 1.2 Hz, 1H), 7.48 (t, J = 7.4 Hz, 1H), 7.32 (t, J = 7.8 Hz, 2H), 7.13 (t, J = 7.8 Hz, 1H), 6.94 (d, J = 7.7 Hz, 1H), 6.87 (d, J = 1.8 Hz, 1H), 3.95 (s, 3H), 3.64 (s, 3H)
13C NMR: δ 196.5 (1C, s), 168.2 (1C, s), 165.4 (1C, s), 161.9 (1C, d), 144.1 (1C, s), 138.0 (1C, d), 137.3 (1C, s), 137.2 (1C, s), 136.5 (1C, d), 133.7 (1C, s), 129.7 (1C, s), 129.6 (1C, s), 129.5 (1C, s), 129.4 (1C, s), 128.5 (1C, s), 128.4 (1C, s), 125.6 (1C, d), 116.8 (1C, d), 115.2 (1C, d), 53.0 (1C, s), 52.5 (1C, s)

### benchmark_expand_500:R108
Molecular formula: C16H15N5O2S
IR bands (cm-1): [3465.0, 3074.0, 2972.0, 2941.0, 1689.0, 1597.0, 1506.0]
1H NMR: 2.07 (s, 3H), 2.87 (s, 2H), 3.36 (s, 2H), 5.90 (t, J = 6.5 Hz, 1H), 7.19 (t, J = 7.3 Hz, 1H), 7.40 (t, J = 8.0 Hz, 2H), 7.67 (t, J = 8.0 Hz, 2H), 11.18 (s, 2H)
13C NMR: δ 12.6 (1C, s), 23.8 (1C, s), 47.8 (1C, s), 51.2 (1C, s), 100.2 (1C, s), 120.5 (1C, s), 125.2 (1C, s), 129.4 (1C, s), 139.9 (1C, s), 142.8 (1C, s), 146.0 (1C, s), 150.9 (1C, s), 171.7 (1C, s)

### benchmark_expand_500:R111
Molecular formula: C25H18ClN5O4
IR bands (cm-1): [3414.0, 3254.0, 1773.0, 1731.0]
1H NMR: 11.71 (s, 0.25H), 11.59 (s, 0.75H), 9.56 (s, 1H), 8.17 (s, 0.25H), 8.01 (s, 0.75H), 7.68-7.64 (m, 2H), 7.45 (d, 4H, J = 6.5 Hz), 7.363-7.346 (m, 7H), 4.62 (s, 1.5H), 4.23 (s, 0.5H)
13C NMR: δ 69.59 (1C, s), 126.55 (1C, s), 126.70 (1C, s), 126.97 (1C, s), 127.86 (1C, s), 128.10 (1C, s), 128.44 (1C, s), 129.68 (1C, s), 129.89 (1C, s), 133.80 (1C, s), 139.54 (1C, s), 144.23 (1C, s), 147.21 (1C, s), 154.89 (1C, s), 155.07 (1C, s), 162.56 (1C, s), 167.09 (1C, s)

### benchmark_expand_500:R112
Molecular formula: C24H34BrNO3
IR bands (cm-1): [2919.0, 2851.0, 1644.0, 1606.0, 1551.0, 1494.0, 1464.0, 1429.0, 1413.0, 1317.0, 1292.0, 1252.0, 1149.0, 1062.0, 1000.0, 821.0, 807.0]
1H NMR: 8.31 (d, J = 2.1 Hz, 1H), 7.74 (dd, J = 9.0, 2.3 Hz, 1H), 7.17 (d, J = 9.0 Hz, 1H), 3.61 (s, 3H), 3.27 (t, J = 7.4 Hz, 2H), 1.70 (dt, J = 14.9, 7.4 Hz, 2H), 1.40 (s, 2H), 1.25 (s, 18H), 0.88 (d, J = 6.5 Hz, 3H)
13C NMR: δ 209.71 (1C, s), 173.06 (1C, s), 161.21 (1C, s), 140.61 (1C, s), 137.54 (1C, s), 128.63 (1C, s), 117.29 (1C, s), 116.07 (1C, s), 115.17 (1C, s), 106.28 (1C, s), 61.69 (1C, s), 56.13 (1C, s), 55.98 (1C, s), 43.09 (1C, s), 32.06 (1C, s), 29.82 (1C, s), 29.78 (1C, s), 29.69 (1C, s), 29.67 (1C, s), 29.49 (1C, s), 29.41 (1C, s), 24.37 (1C, s), 22.82 (1C, s), 14.23 (1C, s)

### benchmark_expand_500:R114
Molecular formula: C23H19N3O4
IR bands (cm-1): [3558.0, 3489.0, 3403.0, 3160.0, 2836.0, 1522.0, 1152.0, 1061.0, 825.0, 757.0]
1H NMR: 9.46 (s, 1H), 8.59 (s, 1H), 8.13 (d, J = 7.6 Hz, 1H), 8.06 (d, J = 8.2 Hz, 2H), 7.99 (d, J = 7.6 Hz, 1H), 7.94 (d, J = 8.2 Hz, 2H), 7.58 (t, J = 7.6 Hz, 1H), 6.89 (s, 2H), 6.55 (s, 1H), 3.84 (s, 6H)
13C NMR: δ 170.7 (1C, s), 161.5 (1C, s), 147.5 (1C, s), 141.4 (1C, s), 140.7 (1C, s), 136.5 (1C, s), 130.7 (1C, s), 129.5 (1C, s), 129.3 (1C, s), 128.8 (1C, s), 128.7 (1C, s), 126.7 (1C, s), 120.7 (1C, s), 120.3 (1C, s), 105.4 (1C, s), 100.4 (1C, s), 55.8 (1C, s)
