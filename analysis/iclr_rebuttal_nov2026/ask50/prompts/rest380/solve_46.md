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
  {"benchmark_expand:R93": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R93
Molecular formula: C14H15NO4
IR bands (cm-1): [3224.0, 2938.0, 1755.0, 1615.0, 1581.0, 1553.0]
1H NMR: 8.50 (1H, d, J = 8 Hz), 8.03 (1H, s), 7.03 (1H, d, J = 8 Hz), 6.93 (3H, t, J = 8 Hz), 6.40 (1H, s), 3.92 (3H, s), 2.62 (2H, t, J = 8 Hz), 1.78 (2H, h, J = 8 Hz), 1.05 (3H, t, J = 8 Hz)
13C NMR: δ 168.59 (1C, s), 164.32 (1C, s), 147.80 (1C, s), 146.31 (1C, s), 124.43 (1C, s), 119.85 (1C, s), 119.12 (1C, s), 117.97 (1C, s), 115.87 (1C, s), 56.36 (1C, s), 27.96 (1C, s), 28.00 (1C, s), 19.86 (1C, s), 13.92 (1C, s)

### benchmark_expand:R95
Molecular formula: C10H7Br2FO
IR bands (cm-1): [3336.0, 3252.0, 3172.0, 3103.0, 3075.0, 3024.0, 1831.0, 1842.0, 1765.0, 1725.0, 1673.0, 1600.0, 1499.0, 1408.0, 1353.0, 1227.0, 940.0, 919.0, 775.0, 752.0, 635.0, 586.0, 514.0]
1H NMR: 7.84 (d, J = 16 Hz, 1H), 7.65 (q, J = 2.8 Hz, 2H), 7.26 (d, J = 6 Hz, 2H), 7.14 (s, 1H), 7.14 (d, J = 16.8 Hz, 1H), 5.92 (s, 1H) ppm; 13C{1H} NMR (100 MHz, CDCl3) δ 185.4, 164.5, (J = 251.9 Hz), 146.3, 130.9 (d, J = 8.7 Hz), 130.1 (d, J = 2.3 Hz), 117.4 (d, J = 2.5 Hz), 116.3 (d, J = 21.9 Hz), 42.5 ppm
13C NMR: δ 185.4 (1C, s), 164.5 (1C, s), 146.3 (1C, s), 130.9 (1C, d), 130.1 (1C, d), 117.4 (1C, d), 116.3 (1C, d)

### benchmark_expand:R96
Molecular formula: C11H9FN4O3
IR bands (cm-1): [3322.0, 3243.0, 3064.0, 2834.0, 2697.0, 1885.0, 1695.0, 1622.0, 1591.0, 1577.0, 1521.0, 1465.0, 1416.0, 1368.0, 1307.0, 1295.0, 1265.0, 1252.0, 1227.0, 1187.0, 1151.0, 1131.0, 1115.0, 1086.0, 1071.0, 1033.0, 1001.0, 965.0, 944.0, 916.0, 895.0, 847.0, 827.0, 811.0, 781.0, 750.0, 713.0, 697.0, 649.0, 630.0, 613.0, 584.0, 572.0, 544.0, 512.0, 496.0, 444.0, 426.0, 410.0, 503.0, 942.0, 1165.0, 506.0, 2855.0, 890.0, 568.0, 994.0, 998.0]
1H NMR: 8.36 (d, 3JH4P/H6P,H5P = 4.8, 2H, H4P, H6P), 7.99-8.02 (m, 1H, H3), 7.91 (d, 3JH20,H12 = 9.0 Hz, 1H, H20), 7.68-7.70 (m, 1H, H6), 7.39-7.42 (m, 1H, H4), 7.05-7.08 (dd, 3JH12,H20 = 9.0 Hz, 3JH12,H21 = 5.4 Hz, 1H, H12), 6.73 (t, 3JH5P,H4P/H6P = 4.8 Hz, 1H, H5P), 6.59 (d, 3JH21,H12 = 5.4 Hz, 1H, H21)
13C NMR: δ 163.6 (1C, d), 161.1 (1C, s), 158.0 (1C, s), 144.5 (1C, d), 140.5 (1C, d), 127.2 (1C, d), 115.1 (1C, m), 111.8 (1C, s), 71.1 (1C, s)

### benchmark_expand:R98
Molecular formula: C9H10O3
IR bands (cm-1): [3400.0, 1670.0, 1590.0, 1515.0]
1H NMR: 2.57 (3H, s, C2-CH3), 3.96 (3H, s, C4-OCH3), 6.06 (1H, s, OH), 6.95 (1H, d, J = 8.5 Hz, H-6), 7.55 (1H, d, J = 1.8 Hz, H-3), 7.55 (1H, dd, J = 8.5, 1.8 Hz, H-5)
13C NMR: δ 26.2 (1C, s), 56.1 (1C, s), 109.7 (1C, s), 113.7 (1C, s), 124.0 (1C, s), 130.2 (1C, s), 146.6 (1C, s), 150.3 (1C, s), 196.8 (1C, s)

### benchmark_expand:R99
Molecular formula: C21H38O
IR bands (cm-1): [3309.0, 2922.0, 2850.0, 2099.0, 1650.0]
1H NMR: 5.90 (1H, dt, J = 15.0, 7.5 Hz, H-5), 5.59 (1H, dd, J = 15.0, 6.0 Hz, H-4), 4.82 (1H, d, J = 6.0 Hz, H-3), 2.56 (1H, d, J = 2.5 Hz, H-1), 2.05 (2H, q, J = 7.5 Hz, H2-6), 1.51 (1H, m, H-18), 1.40 (2H, m, H2-7), 1.35 (1H, m, H-13), 1.15-1.26 (16H, brm), 1.07 (2H, m, H-12b, H-14b), 0.86 (6H, d, J = 7.0 Hz, H3-19, H3-20), 0.82 (3H, d, J = 6.5 Hz, H3-21)
13C NMR: δ 134.5 (1C, s), 128.3 (1C, s), 83.3 (1C, s), 73.8 (1C, s), 62.7 (1C, s), 39.3 (1C, s), 37.0 (1C, s), 32.7 (1C, s), 31.9 (1C, s), 29.6 (1C, s), 28.8 (1C, s), 27.9 (1C, s), 27.7 (1C, s), 27.0 (1C, s), 22.6 (1C, s)

### benchmark_expand_500:R01
Molecular formula: C13H11BrN2O3
IR bands (cm-1): [3469.0, 3356.0, 3097.0, 3010.0, 2954.0, 2928.0, 2904.0, 2834.0, 2532.0, 1607.0, 1578.0, 1496.0, 1461.0, 1388.0, 1358.0, 1321.0, 1287.0, 1241.0, 1174.0, 1028.0, 876.0, 819.0, 696.0]
1H NMR: 8.26 (d, J = 2.4 Hz, 1H), 7.36 (d, J = 2.4 Hz, 1H), 7.29 (d, J = 8.7 Hz, 2H), 7.02 (d, J = 8.7 Hz, 2H), 6.27 (s, 2H), 3.86 (s, 3H)
13C NMR: δ 160.2 (1C, s), 142.2 (1C, s), 138.9 (1C, s), 132.9 (1C, s), 132.8 (1C, s), 130.4 (1C, s), 127.6 (1C, s), 127.4 (1C, s), 115.1 (1C, s), 107.4 (1C, s), 55.5 (1C, s)
