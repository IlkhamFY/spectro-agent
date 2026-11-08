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
  {"benchmark_main:R12": ["CCO", "COC"]}

Compounds:

### benchmark_main:R12
Molecular formula: C17H15BrO3
IR bands (cm-1): [2918.0, 2850.0, 1633.0, 1571.0, 1454.0, 1410.0, 1368.0, 1329.0, 1307.0, 1276.0, 1222.0, 1204.0, 1159.0, 1114.0, 1072.0, 1031.0, 978.0, 945.0, 898.0, 863.0, 815.0, 787.0, 760.0, 699.0, 667.0, 626.0, 606.0, 583.0, 557.0, 529.0, 485.0]
1H NMR: 2.33 (s, 3H), 3.94 (s, 3H), 6.24 (d, J = 1.5 Hz, 1H), 6.43-6.46 (m, 1H), 7.28 (t, J = 7.8 Hz, 1H), 7.51 (dd, J = 7.9, 1.8 Hz, 2H), 7.67 (d, J = 15.6 Hz, 1H), 7.74 (t, J = 1.8 Hz, 1H), 7.84 (d, J = 15.6 Hz, 1H), 13.27 (s, 1H)
13C NMR: δ 22.61 (1C, s), 56.09 (1C, s), 102.99 (1C, s), 109.79 (1C, s), 111.49 (1C, s), 123.15 (1C, s), 127.21 (1C, s), 129.18 (1C, s), 130.53 (1C, s), 131.03 (1C, s), 132.97 (1C, s), 137.80 (1C, s), 140.70 (1C, s), 148.23 (1C, s), 161.03 (1C, s), 165.35 (1C, s), 193.65 (1C, s)

### benchmark_main:R125
Molecular formula: C14H18O3
IR bands (cm-1): [2976.0, 2918.0, 2864.0, 1759.0, 1744.0, 1599.0, 1584.0, 1404.0, 1357.0, 1211.0, 1161.0, 1111.0, 1084.0, 937.0, 895.0, 839.0, 768.0, 745.0]
1H NMR: 6.58 (s, 1H), 6.14-6.02 (m, 1H), 5.44 (dq, J = 17.3, 1.7 Hz,1H), 5.28 (dq, J = 10.5, 1.5 Hz, 1H), 4.50 (dt, J = 5.0, 1.6 Hz, 2H), 2.34 (s, 3H), 2.18 (s, 3H), 2.13 (s, 3H), 2.07 (s, 3H)
13C NMR: δ 169.5 (1C, s), 154.2 (1C, s), 141.8 (1C, s), 133.8 (1C, s), 129.8 (1C, s), 127.1 (1C, s), 124.3 (1C, s), 116.9 (1C, s), 111.6 (1C, s), 69.4 (1C, s), 20.6 (1C, s), 16.7 (1C, s), 13.1 (1C, s), 12.1 (1C, s)

### benchmark_main:R128
Molecular formula: C14H22N2O2
IR bands (cm-1): [3350.0, 3324.0, 3100.0, 2952.0, 2923.0, 1618.0, 1579.0, 1513.0, 1253.0, 1241.0, 1172.0, 1109.0, 1031.0, 811.0]
1H NMR: 7.16 (d, J = 8.6 Hz, 2H), 6.87 (d, J = 8.6 Hz, 2H), 6.14 (t, J = 5.8 Hz, 1H), 5.83 (t, J = 5.5 Hz, 1H), 4.11 (d, J = 5.8, 2H), 3.73 (s, 3H), 2.99 (q, J = 6.7 Hz, 2H), 1.42-1.15 (m, 6H), 0.87 (t, J = 7.5 Hz, 3H)
13C NMR: δ 158.4 (1C, s), 133.4 (1C, s), 128.8 (1C, s), 114.1 (1C, s), 55.5 (1C, s), 42.8 (1C, s), 39.7 (1C, s), 30.2 (1C, s), 22.3 (1C, s), 14.4 (1C, s)

### benchmark_main:R129
Molecular formula: C15H24OS
IR bands (cm-1): [3094.0, 2953.0, 2926.0, 2853.0, 2793.0, 2708.0, 1692.0, 1466.0, 1406.0, 1119.0, 721.0]
1H NMR: 0.88 (t, J = 6.8 Hz, 3H), 1.26-1.35 (m, 14H), 1.68 (quintet, J = 6.8 Hz, 2H), 2.80 (t, J = 7.2 Hz, 2H), 7.20 (d, J = 2 Hz, 1H), 7.90 (d, J = 1.6 Hz, 1H), 9.81 (s, 1H). 13C{1H} NMR (150 MHz, CDCl3, rt): δ 14.1, 22.7, 29.0, 29.27, 29.29, 29.5, 29.6, 29.9, 31.3, 31.9, 121.5, 135.4, 142.9, 148.3, 185.2
13C NMR: δ 14.1 (1C, s), 22.7 (1C, s), 29.0 (1C, s), 29.27 (1C, s), 29.29 (1C, s), 29.5 (1C, s), 29.6 (1C, s), 29.9 (1C, s), 31.3 (1C, s), 31.9 (1C, s), 121.5 (1C, s), 135.4 (1C, s), 142.9 (1C, s), 148.3 (1C, s), 185.2 (1C, s)

### benchmark_main:R136
Molecular formula: C16H18N2O
IR bands (cm-1): [3290.0, 3090.0, 3026.0, 2977.0, 2917.0, 1627.0, 1585.0, 1561.0, 1517.0, 1448.0, 1310.0, 1228.0, 1018.0, 829.0, 741.0]
1H NMR: 7.28-7.24 (m, 1H), 7.23 (d, J = 2.7 Hz, 3H), 7.21 (dt, J = 2.7, 1.4 Hz, 1H), 7.19 (s, 1H), 7.10 (s, 1H), 7.09-7.05 (m, 2H), 6.99 (d, J = 8.4 Hz, 2H), 5.67 (d, J = 7.6 Hz, 1H), 4.89 (p, J = 7.0 Hz, 1H), 2.25 (s, 3H), 1.33 (d, J = 6.9 Hz, 3H)
13C NMR: δ 155.8 (1C, s), 144.2 (1C, s), 136.1 (1C, s), 132.9 (1C, s), 129.6 (1C, s), 128.6 (1C, s), 127.0 (1C, s), 125.9 (1C, s), 120.8 (1C, s), 49.7 (1C, s), 22.9 (1C, s), 20.7 (1C, s)

### benchmark_main:R137
Molecular formula: C18H31NO3
IR bands (cm-1): [3282.0, 2918.0, 2849.0, 1624.0, 1464.0, 1199.0, 1002.0]
1H NMR: 6.22 (d, J = 3.2 Hz, 1H), 6.17 (d, J = 3.2 Hz, 1H), 4.46 (s, 2H), 4.33 (s, 2H), 2.20 (t, J = 7.5 Hz, 2H), 1.60 (apparent t, J = 7.3 Hz, 2H), 1.30 (d, J = 4.4 Hz, 16H), 0.90 (t, J = 6.8 Hz, 3H)
13C NMR: δ 175.2 (1C, s), 154.6 (1C, s), 152.1 (1C, s), 108.4 (1C, s), 107.9 (1C, s), 56.5 (1C, s), 36.3 (1C, s), 36.1 (1C, s), 32.2 (1C, s), 29.9 (1C, s), 29.8 (1C, s), 29.6 (1C, s), 29.6 (1C, s), 29.4 (1C, s), 26.1 (1C, s), 22.9 (1C, s), 13.6 (1C, s)
