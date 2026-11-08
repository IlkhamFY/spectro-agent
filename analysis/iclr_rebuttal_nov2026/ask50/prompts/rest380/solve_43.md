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
  {"benchmark_expand:R59": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R59
Molecular formula: C13H18O3
IR bands (cm-1): [1707.0, 1590.0, 1511.0, 1452.0, 1156.0, 1139.0, 1032.0]
1H NMR: 6.86 (d, J = 8.4 Hz, 1H), 6.73 (d, J = 6.2 Hz, 2H), 4.51 (m, J = 6.1 Hz, 1H), 3.85 (s, 3H), 3.63 (s, 2H), 2.16 (s, 3H), 2.14 (d, J = 7.4 Hz, 0H), 1.37 (dd, J = 6.1, 1.7 Hz, 6H)
13C NMR: δ 206.87 (1C, s), 150.56 (1C, s), 146.49 (1C, s), 127.17 (1C, s), 121.59 (1C, s), 116.07 (1C, s), 113.15 (1C, s), 71.53 (1C, s), 55.99 (1C, s), 50.69 (1C, s), 29.11 (1C, s), 22.14 (1C, s)

### benchmark_expand:R60
Molecular formula: C13H17NO5
IR bands (cm-1): [3438.0, 2941.0, 2977.0, 2903.0, 1700.0, 1510.0, 1343.0, 1148.0, 843.0]
1H NMR: 7.29 (d, 2H, J = 7.5 Hz, Ar-H), 6.86 (d, 2H, J = 7.5 Hz, Ar-H), 5.01 (dd, J = 8.8, 4.0 Hz, 1H, CH), 3.78 (s, 3H, OCH3), 3.15 (bs, 1H, OH), 2.71-2.54 (m, 2H, CH2) and 1.44 (s, 9H, 3 CH3). 13C{1H}-NMR (CDCl3) δ 171.9, 159.1, 134.9, 127.0 (2C), 113.8 (2C), 81.4, 70.0, 55.2, 44.3, and 28.0
13C NMR: δ 171.3 (1C, s), 150.0 (1C, s), 147.3 (1C, s), 126.5 (1C, s), 123.6 (1C, s), 82.1 (1C, s), 69.4 (1C, s)

### benchmark_expand:R64
Molecular formula: C8H12O2
IR bands (cm-1): [2985.0, 2933.0, 2847.0, 1731.0, 1677.0, 1450.0, 1376.0, 1344.0, 1284.0, 1242.0, 1202.0, 1181.0, 1152.0, 1110.0, 1036.0, 990.0, 924.0, 834.0, 761.0, 696.0, 553.0]
1H NMR: 6.11 (m, 1H, CH2), 5.86 (ddd, 3JH,H = 5.8, 10.5, 16.3 Hz, 1H, CH), 5.54 (quin, 2JH,H = 4JH,H = 1.6 Hz, 1H, CH2), 5.43-5.35 (m, 1H, CH), 5.24 (dt, 2JH,H = 1.2 Hz, 3JH,H = 17.2 Hz, 1H, CH2), 5.12 (dt, 2JH,H = 1.2 Hz, 3JH,H = 10.5 Hz, 1H, CH2), 1.93 (dd, 4JH,H = 1.1, 1.6 Hz, 3H, CH3), 1.34 (d, 3JH,H = 6.5 Hz, 1JC,H = 127.8 Hz, 3H, CH3)
13C NMR: δ 166.4 (1C, s), 137.7 (1C, s), 136.6 (1C, s), 125.4 (1C, s), 115.5 (1C, s), 77.1 (1C, s), 19.9 (1C, s), 18.2 (1C, s)

### benchmark_expand:R66
Molecular formula: C15H31NO3Si
IR bands (cm-1): [2956.0, 2932.0, 2898.0, 2858.0, 1668.0]
1H NMR: 3.73-3.62 (m, 1H), 3.59 (s, 3H), 3.14 (s, 3H), 1.59 (s, 3H), 1.58 (s, 3H), 1.24 (d, J = 7.2 Hz, 3H), 0.93 (s, 9H), 0.14 (s, 3H), 0.12 (s, 3H)
13C NMR: δ 174.8 (1C, s), 143.7 (1C, s), 109.9 (1C, s), 77.4 (1C, s), 60.7 (1C, s), 41.1 (1C, s), 26.2 (1C, s), 18.9 (1C, s), 18.7 (1C, s), 18.6 (1C, s), 14.8 (1C, s), -3.3 (1C, s), -3.4 (1C, s)

### benchmark_expand:R67
Molecular formula: C18H15F3O
IR bands (cm-1): [3060.0, 2975.0, 2933.0, 1683.0, 1615.0, 1448.0, 1414.0, 1325.0, 1165.0, 1122.0, 1067.0, 1016.0, 972.0, 822.0, 705.0]
1H NMR: 1.44 (d, J = 6.8 Hz, 3H), 4.35 (apparent quintet, J = 6.9 Hz, 1H), 6.49 (dd, J = 16.0, 7.3 Hz, 1H), 6.55 (d, J = 16.0 Hz, 1H), 7.43 (br d, J = 8.2 Hz, 2H), 7.48 (br t, J = 7.7 Hz, 2H), 7.53 (br d, J = 8.2 Hz, 2H), 7.55-7.59 (m, 1H), 7.99-8.03 (m, 2H). 13C{1H} NMR (CDCl3, 125 MHz): δ 17.9, 44.9, 124.3 (q, J = 271.9 Hz), 125.6 (q, J = 3.8 Hz), 126.6, 128.7, 128.9, 129.5 (q, J = 32.5 Hz), 130.4, 132.7, 133.4, 136.4, 140.6, 200.9
13C NMR: δ 17.9 (1C, s), 44.9 (1C, s), 124.3 (1C, q), 125.6 (1C, q), 126.6 (1C, s), 128.7 (1C, s), 128.9 (1C, s), 129.5 (1C, q), 130.4 (1C, s), 132.7 (1C, s), 133.4 (1C, s), 136.4 (1C, s), 140.6 (1C, s), 200.9 (1C, s)

### benchmark_expand:R69
Molecular formula: C8H7ClN2O3
IR bands (cm-1): [3288.0, 2991.0, 1735.0, 1696.0, 1596.0, 1489.0, 1202.0, 1175.0, 827.0, 481.0]
1H NMR: 11.08 (br. s, 1H), 9.36 (br. s, 1H), 8.11 (dd, J = 8.5, 1.5 Hz, 1H), 7.60 (ddd, J = 8.5, 6.9, 1.5 Hz, 1H), 7.09 (dd, J = 8.6, 1.2 Hz, 1H), 6.90 (ddd, J = 8.4, 7.0, 1.3 Hz, 1H)
13C NMR: δ 162.1 (1C, s), 159.0 (1C, s), 147.8 (1C, s), 129.0 (1C, s), 122.7 (1C, s), 114.3 (1C, s)
