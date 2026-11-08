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
  {"benchmark_expand_500:R30": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R30
Molecular formula: C23H17N3
IR bands (cm-1): [3061.0, 3004.0, 2957.0, 1611.0, 1562.0, 1527.0, 1484.0, 1349.0, 1193.0, 925.0, 763.0]
1H NMR: 8.98 (d, 1H, J = 7.8 Hz), 8.88 (d, 1H, J = 8.4 Hz), 8.55 (d, 1H, J = 8.0 Hz), 8.18 (d, 1H, J = 8.0 Hz), 8.15 (dd, 2H, J = 7.8, 1.2 Hz), 8.07 (t, 1H, J = 7.6 Hz), 7.88 (t, 1H, J = 7.8 Hz), 7.84 (t, 1H, J = 7.6 Hz), 7.81 (t, 1H, J = 7.6 Hz), 7.73-7.70 ppm (m, 3H)
13C NMR: δ 159.6 (1C, s), 152.5 (1C, s), 142.4 (1C, s), 133.8 (1C, s), 133.0 (1C, s), 131.9 (1C, s), 130.5 (1C, s), 129.7 (1C, s), 129.6 (1C, s), 128.3 (1C, s), 127.9 (1C, s), 125.7 (1C, s), 124.5 (1C, s), 123.4 (1C, s), 123.0 (1C, s)

### benchmark_expand_500:R37
Molecular formula: C20H16N6OS
IR bands (cm-1): [2956.0, 2924.0, 2853.0, 1541.0, 1534.0, 1491.0, 1467.0, 1446.0, 1335.0, 1298.0, 1277.0, 1260.0, 1230.0, 1116.0, 1026.0, 908.0, 885.0, 751.0, 723.0, 509.0]
1H NMR: 4.02-4.05 (m, 4H), 4.50-4.54 (m, 4H), 7.35-7.48 (m, 6H), 8.18 (d, J = 7.1 Hz, 2H)
13C NMR: δ 47.1 (1C, s), 67.0 (1C, s), 111.6 (1C, s), 120.3 (1C, s), 121.2 (1C, s), 124.5 (1C, s), 126.0 (1C, s), 140.3 (1C, s), 142.6 (1C, s), 145.4 (1C, s), 148.6 (1C, s), 152.1 (1C, s)

### benchmark_expand_500:R38
Molecular formula: C14H12N4O
IR bands (cm-1): [3368.0, 3242.0, 3071.0, 2948.0, 1730.0]
1H NMR: 2.48 (s, 3H, CH3), 7.34 - 7.66 (m, 6H, naphthyl-H), 8.18 - 8.21 (d, J = 8.1 Hz, 1H, naphthyl-H), 9.16 (s, 1H, NH, exchangeable with D2O), 12.66 (s, 1H, NH-hydrazone, exchangeable with D2O)
13C NMR: δ 14.1 (1C, s), 106.3 (1C, s), 120.2 (1C, s), 122.1 (1C, s), 122.3 (1C, s), 124.2 (1C, s), 125.5 (1C, s), 127.1 (1C, s), 129.4 (1C, s), 131.0 (1C, s), 143.1 (1C, s), 147.2 (1C, s), 182.2 (1C, s)

### benchmark_expand_500:R39
Molecular formula: C28H21FN4O2
IR bands (cm-1): [3469.0, 3280.0, 2925.0, 2891.0, 2201.0, 1571.0]
1H NMR: 8.87-8.83 (m, 1H, Ar-H), 8.39-8.34 (m, 1H, Ar-H), 7.94 (d, J = 8.9 Hz, 2H, Ar-H), 7.81-7.77 (m, 2H, Ar-H), 7.41 (s, 1H, Ar-H), 7.37-7.28 (m, 4H, Ar-H, NH2), 7.22-7.14 (m, 2H, Ar-H), 7.10 (d, J = 9.0 Hz, 2H, Ar-H), 5.27 (s, 1H, H4), 4.14 (q, J = 6.7 Hz, 2H, CH2), 1.36 (t, J = 6.8 Hz, 3H, CH3)
13C NMR: δ 162.30 (1C, s), 160.96 (1C, s), 147.53 (1C, s), 146.07 (1C, s), 143.96 (1C, s), 132.72 (1C, s), 132.55 (1C, s), 131.35 (1C, s), 131.15 (1C, s), 130.35 (1C, s), 128.81 (1C, s), 128.32 (1C, s), 125.76 (1C, s), 124.11 (1C, s), 121.98 (1C, s), 120.85 (1C, s), 117.80 (1C, s), 116.95 (1C, s), 116.67 (1C, s), 115.90 (1C, s), 112.18 (1C, s), 64.57 (1C, s), 55.67 (1C, s), 31.52 (1C, s)

### benchmark_expand_500:R40
Molecular formula: C24H24BrClN2O2
IR bands (cm-1): [3437.0, 2081.0, 1667.0, 1564.0, 1490.0, 1454.0, 1412.0, 1366.0, 1254.0, 1167.0, 1094.0, 1046.0]
1H NMR: 8.44 (s, 1H), 7.66 (s, 1H), 7.26-7.23 (m, 3H), 7.19 (s, 1H), 7.11 (d, J = 8.4 Hz, 2H), 7.08 (d, J = 2.4 Hz, 1H), 6.25 (s, 1H), 5.67 (s, 1H), 3.90-3.87 (m, 1H), 3.72-3.65 (m, 1H), 3.06-2.89 (m, 2H), 1.35 (s, 9H) ppm
13C NMR: δ 154.6 (1C, s), 135.8 (1C, s), 135.4 (1C, s), 132.6 (1C, s), 129.8 (1C, s), 128.6 (1C, s), 127.2 (1C, s), 124.9 (1C, s), 122.7 (1C, s), 122.1 (1C, s), 113.0 (1C, s), 112.9 (1C, s), 80.0 (1C, s), 59.6 (1C, s), 46.2 (1C, s), 29.2 (1C, s)

### benchmark_expand_500:R42
Molecular formula: C22H15ClO3
IR bands (cm-1): [3054.0, 2925.0, 1689.0, 1658.0, 1602.0, 1583.0, 1466.0, 1447.0, 1231.0, 1035.0, 755.0]
1H NMR: 5.45 (d, J = 12.0 Hz, 1 H), 6.44 (d, J = 12.0 Hz, 1 H), 7.10-7.14 (m, 2 H), 7.22-7.26 (m, 2 H), 7.41-7.48 (m, 4 H), 7.57-7.61 (m, 2 H), 7.90-7.96 (m, 3 H)
13C NMR: δ 57.7 (1C, s), 78.4 (1C, s), 118.1 (1C, s), 120.4 (1C, s), 122.0 (1C, s), 127.2 (1C, s), 127.5 (1C, s), 128.7 (1C, s), 128.8 (1C, s), 130.4 (1C, s), 130.6 (1C, s), 133.7 (1C, s), 134.1 (1C, s), 134.2 (1C, s), 136.9 (1C, s), 137.2 (1C, s), 161.2 (1C, s), 189.3 (1C, s), 195.1 (1C, s)
