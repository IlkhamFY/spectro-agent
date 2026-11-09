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
  {"benchmark_expand_500:R157": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R157
Molecular formula: C18H21NO3
IR bands (cm-1): [2981.0, 2937.0, 2240.0, 1736.0, 1606.0, 1512.0, 1465.0, 1253.0, 1178.0, 1103.0, 1034.0, 831.0, 531.0]
1H NMR: 7.31-7.23 (m, 2H), 6.92-6.84 (m, 2H), 6.76 (t, J = 2.6 Hz, 1H), 5.08 (hept, J = 6.3 Hz, 1H), 3.80 (s, 3H), 2.80-2.64 (m, 2H), 2.59-2.49 (m, 1H), 2.33-2.22 (m, 1H), 2.15-2.04 (m, 1H), 2.01-1.89 (m, 1H), 1.31 (t, J = 6.3 Hz, 6H)
13C NMR: δ 167.5 (1C, s), 159.0 (1C, s), 138.6 (1C, s), 129.9 (1C, s), 129.0 (1C, s), 126.8 (1C, s), 120.0 (1C, s), 113.8 (1C, s), 70.7 (1C, s), 55.2 (1C, s), 52.9 (1C, s), 36.5 (1C, s), 30.7 (1C, s), 25.1 (1C, s), 21.4 (1C, s), 21.3 (1C, s)

### benchmark_expand_500:R159
Molecular formula: C13H10F3NO3
IR bands (cm-1): [3129.0, 2929.0, 2851.0, 1702.0, 1599.0, 1441.0, 1320.0, 1166.0, 1133.0, 1062.0, 929.0, 846.0, 815.0]
1H NMR: 8.1 (d, J = 8.0 Hz, 2H), 7.85 (d, J = 8.4 Hz, 2H), 6.82 (s, 1H), 3.15 (t, J = 6.3 Hz, 2H), 2.83 (t, J = 6.4 Hz, 2H); 13C{1H}NMR (125 MHz, CD3COCD3): δ 173.7, 172.3, 161.0, 133.3, 130.9 (q, J = 32.3 Hz), 127.2 (2C), 125.9 (d, J = 3.5 Hz, 2C), 124.2 (q, J = 271.4 Hz), 99.3, 30.8, 21.9
13C NMR: δ 173.7 (1C, s), 172.3 (1C, s), 161.0 (1C, s), 133.3 (1C, s), 130.9 (1C, q), 127.2 (1C, s), 125.9 (1C, d), 124.2 (1C, q), 99.3 (1C, s), 30.8 (1C, s), 21.9 (1C, s)

### benchmark_expand_500:R160
Molecular formula: C16H32O3
IR bands (cm-1): [3285.0, 2917.0, 2849.0, 1740.0, 1473.0, 1463.0, 1435.0, 1412.0, 1382.0, 1313.0, 1286.0, 1264.0, 1240.0, 1217.0, 1196.0, 1175.0, 1117.0, 1071.0, 1061.0, 1049.0, 1025.0, 1013.0, 992.0, 973.0, 926.0, 884.0, 731.0, 720.0, 701.0]
1H NMR: 3.64 (s, 3H, OCH3), 3.61 (t, J = 6.7 Hz, 2H, H15), 2.28 (t, J = 7.5 Hz, 2H, H2), 1.72 (s, 1H, OH), 1.59 (quint, J = 7.1 Hz, 2H, H3), 1.54 (quint, J = 7.1 Hz, 2H, H14), 1.37-1.14 (m, 20H, H4-H13)
13C NMR: δ 174.5 (1C, s), 63.1 (1C, s), 51.6 (1C, s), 34.2 (1C, s), 32.9 (1C, s), 29.71 (1C, s), 29.68 (1C, s), 29.5 (1C, s), 29.4 (1C, s), 29.3 (1C, s), 25.9 (1C, s), 25.1 (1C, s)

### benchmark_expand_500:R162
Molecular formula: C14H11ClO3
IR bands (cm-1): [3310.0, 1675.0, 1590.0, 1152.0]
1H NMR: 10.06 (br, 1H, OH), 9.84 (s, 1H, CHO), 7.61-7.59 (m, 2H, Ar-H), 7.55 (d, 1H, J = 1.80 Hz, Ar-H), 7.50-7.49 (m, 2H, Ar-H), 7.43 (d, 1H, J = 1.80 Hz, Ar-H), 3.93 (s, 3H, OCH3)
13C NMR: δ 56.13 (1C, s), 109.02 (1C, s), 126.51 (1C, s), 127.11 (1C, s), 128.10 (1C, s), 128.28 (1C, s), 130.86 (1C, s), 131.95 (1C, s), 135.88 (1C, s), 148.41 (1C, s), 149.69 (1C, s), 191.23 (1C, s)

### benchmark_expand_500:R166
Molecular formula: C9H14OSi
IR bands (cm-1): [3470.0, 3067.0, 3017.0, 2955.0, 2897.0, 1595.0, 1572.0, 1472.0, 1437.0, 1323.0, 1246.0, 1122.0, 1072.0, 852.0, 754.0, 621.0]
1H NMR: 7.37 (dd, J = 7.2 Hz, 1.3 Hz, 1H), 7.22 (td, J = 7.7 Hz, 1.4 Hz, 1H), 6.92 (t, J = 7.3 Hz, 1H), 6.64 (d, J = 8.0 Hz, 1H), 4.83 (s, 1H), 0.31 (s, 9H); 13C{1H} NMR (75 MHz, CDCl3): δ 160.3, 135.3, 130.7, 125.4, 120.5, 114.4, -1.0
13C NMR: δ 160.3 (1C, s), 135.3 (1C, s), 130.7 (1C, s), 125.4 (1C, s), 120.5 (1C, s), 114.4 (1C, s), -1.0 (1C, s)

### benchmark_expand_500:R167
Molecular formula: C11H13FO2
IR bands (cm-1): [754.0, 496.0, 732.0, 696.0]
1H NMR: 7.53-7.48 (m, 2H, Ar), 7.42-7.29 (m, 3H, Ar), 4.24 (q, JH-H = 7.2 Hz, 2H, OEt), 1.93 (d, JH-F = 22.4 Hz, 3H, Me), 1.26 (t, JH-H = 7.2 Hz, 3H, OEt)
13C NMR: δ 170.9 (1C, d), 139.3 (1C, d), 128.5 (1C, d), 128.4 (1C, s), 124.6 (1C, d), 94.6 (1C, d), 61.9 (1C, s), 24.8 (1C, d)
