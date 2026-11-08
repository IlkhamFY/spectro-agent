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
  {"benchmark_expand_500:R201": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R201
Molecular formula: C12H9NO2
IR bands (cm-1): [3331.0, 3209.0, 1817.0, 1631.0, 1450.0]
1H NMR: 8.06-7.97 (m, 2H), 7.62-7.54 (m, 1H), 7.53-7.44 (m, 2H), 4.54 (t, J = 5.3 Hz, 1H), 2.91 (qdd, J1 = 16.9, J2 = 5.3, J3 = 2.6 Hz, 2H), 2.02 (t, J = 2.7 1H). 13C{1H} NMR (101 MHz, CDCl3) δ: 176.6, 162.9, 133.2, 132.0, 128.9 (2C), 128.2 (2C), 77.5, 71.9, 64.2, 21.7
13C NMR: δ 176.6 (1C, s), 162.9 (1C, s), 133.2 (1C, s), 132.0 (1C, s), 128.9 (1C, s), 128.2 (1C, s), 77.5 (1C, s), 71.9 (1C, s), 64.2 (1C, s), 21.7 (1C, s)

### benchmark_expand_500:R202
Molecular formula: C14H17N5
IR bands (cm-1): [3276.0, 3183.0, 3129.0, 3108.0, 3022.0, 2923.0, 2866.0, 1607.0, 1577.0, 1419.0, 1374.0, 1329.0, 1240.0, 1210.0, 1174.0, 1099.0, 1081.0, 1060.0, 988.0, 973.0, 946.0, 920.0, 887.0, 827.0, 809.0, 749.0, 737.0, 698.0]
1H NMR: 7.33 (d, J = 5.0 Hz, 4H), 7.29-7.17 (m, 1H), 6.46 (s, 1H), 4.48 (s, 2H), 2.21 (s, 6H) ppm. 13C{1H} NMR (101 MHz, DMSO-d6): δ 166.5, 166.1 (2C), 158.1, 140.7, 128.7 (2C), 127.5 (3C), 127.1, 110.5, 43.9, 24.0 (2C) ppm
13C NMR: δ 166.5 (1C, s), 166.1 (1C, s), 158.1 (1C, s), 140.7 (1C, s), 128.7 (1C, s), 127.5 (1C, s), 127.1 (1C, s), 110.5 (1C, s), 43.9 (1C, s)

### benchmark_expand_500:R203
Molecular formula: C21H40O
IR bands (cm-1): [3325.0, 2957.0, 2914.0, 2849.0, 2360.0, 2341.0, 1469.0]
1H NMR: 4.31 (1H, tq, J = 7.0, 2.0 Hz, H-4), 1.84 (3H, d, J = 2.0 Hz, H-1), 1.75 (1H, bs, -CH(OH)-), 1.65 (2H, m, H-5), 1.41 (2H, m, H2-6), 1.22-1.31 (28H, bm), 0.87 (3H, t, J = 6.5 Hz, H3-21)
13C NMR: δ 80.8 (1C, s), 80.5 (1C, s), 62.7 (1C, s), 38.1 (1C, s), 31.9 (1C, s), 29.7 (1C, s), 29.6 (1C, s), 29.5 (1C, s), 29.4 (1C, s), 29.3 (1C, s), 25.2 (1C, s), 22.7 (1C, s), 14.1 (1C, s)

### benchmark_expand_500:R204
Molecular formula: C15H14BrNO
IR bands (cm-1): [3446.0, 3365.0, 3029.0, 2923.0, 1682.0, 1624.0, 1584.0, 1516.0, 1396.0, 1201.0, 1070.0, 978.0, 815.0]
1H NMR: 7.80 (d, J = 8.8 Hz, 2H), 7.58 (d, J = 8.4 Hz, 2H), 7.02 (d, J = 8.4 Hz, 2H), 6.63 (d, J = 8.0 Hz, 2H), 3.52 (br s, 2H), 3.20 (t, J = 8.0 Hz, 2H), 2.94 (t, J = 7.6 Hz, 2H). 13C{1H} NMR (100.6 MHz, CDCl3): δ 198.7, 144.7, 135.8, 132.0, 131.1, 129.7, 129.3, 128.2, 115.5, 40.9, 29.4
13C NMR: δ 198.7 (1C, s), 144.7 (1C, s), 135.8 (1C, s), 132.0 (1C, s), 131.1 (1C, s), 129.7 (1C, s), 129.3 (1C, s), 128.2 (1C, s), 115.5 (1C, s), 40.9 (1C, s), 29.4 (1C, s)

### benchmark_expand_500:R206
Molecular formula: C18H19NO2Si
IR bands (cm-1): [2959.0, 2898.0, 2861.0, 2164.0, 1687.0, 1598.0, 1583.0, 1561.0, 1482.0, 1456.0, 1393.0, 1286.0, 1249.0, 1237.0, 1161.0, 1016.0, 869.0, 841.0, 758.0]
1H NMR: 10.51 (br, 1H), 8.65 (dd, J = 2.3, 0.9 Hz, 1H), 7.87 (dd, J = 7.7, 1.8 Hz, 1H), 7.77 (dd, J = 8.0, 2.3 Hz, 1H), 7.55 (ddd, J = 8.5, 7.3, 1.8 Hz, 1H), 7.51 (dd, J = 8.0, 0.9 Hz, 1H), 7.09 (ddd, 7.7, 7.3, 1.0, 1H), 7.03 (dd, J = 8.5, 1.0 Hz, 1H), 5.21 (s, 2H), 0.28 (s, 9H)
13C NMR: δ 189.3 (1C, s), 160.5 (1C, s), 150.7 (1C, s), 149.0 (1C, s), 143.3 (1C, s), 136.0 (1C, s), 135.3 (1C, s), 131.3 (1C, s), 129.2 (1C, s), 127.4 (1C, s), 121.8 (1C, s), 113.0 (1C, s), 103.4 (1C, s), 95.6 (1C, s), 68.0 (1C, s), 0.16 (1C, s)

### benchmark_expand_500:R207
Molecular formula: C13H26OSi
IR bands (cm-1): [3492.0, 2926.0, 2854.0, 1450.0, 1248.0, 1037.0, 895.0, 839.0, 693.0]
1H NMR: 5.82 (dt, J = 17.1, 10.5 Hz, 1H), 5.00 (dd, J = 10.2, 2.2 Hz, 1H), 4.89 (dd, J = 17.1, 2.0 Hz, 1H), 3.43 (dd, J = 7.2, 4.5 Hz, 1H),1.91-1.82 (m, 2H), 1.79-1.58 (m, 4H), 1.42-1.32 (m, 1H), 1.30-1.05 (m, 4H), 0.95 (dtd, J = 15.8, 12.3, 2.6 Hz, 2H), 0.05 (d, J = 11.7 Hz, 9H)
13C NMR: δ 135.6 (1C, s), 114.4 (1C, s), 76.2 (1C, s), 42.4 (1C, s), 39.3 (1C, s), 29.3 (1C, s), 28.5 (1C, s), 26.4 (1C, s), 26.2 (1C, s), 25.9 (1C, s), -2.1 (1C, s)
