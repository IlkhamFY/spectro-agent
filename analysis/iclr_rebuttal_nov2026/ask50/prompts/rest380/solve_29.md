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
  {"benchmark_main:R114": ["CCO", "COC"]}

Compounds:

### benchmark_main:R114
Molecular formula: C16H9ClN2O3
IR bands (cm-1): [3080.0, 1765.0, 1599.0, 1540.0, 1486.0, 1445.0, 1397.0, 1251.0, 1125.0, 940.0]
1H NMR: 10.81 (1H, s), 8.90 (1H, d, J = 2.7 Hz), 8.14 (1H, d, J = 2.4 Hz), 7.52 (1H, t, J = 4.2 Hz), 7.37-7.35 (2H, m), 3.80 (3H, s)
13C NMR: δ 159.2 (1C, s), 157.8 (1C, s), 155.2 (1C, s), 150.1 (1C, s), 148.9 (1C, s), 141.4 (1C, s), 132.6 (1C, s), 132.3 (1C, s), 128.5 (1C, s), 127.1 (1C, s), 126.0 (1C, s), 120.8 (1C, s), 113.5 (1C, s), 111.0 (1C, s), 104.3 (1C, s), 30.8 (1C, s)

### benchmark_main:R116
Molecular formula: C36H43N3O3
IR bands (cm-1): [2969.0, 1889.0, 1683.0, 1605.0, 1520.0, 1457.0, 1359.0, 1263.0, 1191.0, 1078.0, 907.0, 811.0, 725.0]
1H NMR: 9.45 (s, 1 H, CHO), 7.20-7.16 (m, 3 H, CHAr), 7.02 (d, J = 8.8 Hz, 2 H, CHAr), 6.97-6.91 (m, 3 H, CHAr), 6.88 (d, J = 8.8 Hz, 2 H, CHAr), 6.53 (d, J = 8.8 Hz, 2 H, CHAr), 6.49 (d, J = 8.8 Hz, 2 H, CHAr), 5.74 (t, J = 7.4 Hz, 1 H, =CH), 4.69 (dd, J = 10.2, 5.9 Hz, 1 H, CHNO2), 3.36-3.31 (m, 1 H, CHPh), 3.30-3.21 (m, 8 H, NCH2), 3.10 (s, 1 H, CH), 2.76-2.59 (m, 2 H, CH2), 2.33 (ddt, J = 29.6, 14.6, 7.2 Hz, 2 H, CH2), 1.09 (t, J = 7.0 Hz, 6 H, CH3), 1.06 (t, J = 7.0 Hz, 6 H, CH3)
13C NMR: δ 192.4 (1C, s), 153.0 (1C, s), 147.1 (1C, s), 146.8 (1C, s), 145.4 (1C, s), 137.6 (1C, s), 136.4 (1C, s), 130.8 (1C, s), 129.7 (1C, s), 128.9 (1C, s), 128.3 (1C, s), 128.0 (1C, s), 127.8 (1C, s), 126.6 (1C, s), 119.2 (1C, s), 111.2 (1C, s), 111.1 (1C, s), 83.4 (1C, s), 46.7 (1C, s), 44.3 (1C, s), 44.2 (1C, s), 41.0 (1C, s), 33.6 (1C, s), 23.9 (1C, s), 12.7 (1C, s), 12.6 (1C, s)

### benchmark_main:R117
Molecular formula: C15H15N3
IR bands (cm-1): [3103.0, 3035.0, 2960.0, 1618.0, 1576.0, 1450.0, 1379.0, 1344.0, 1205.0, 1133.0, 873.0, 842.0, 813.0, 780.0, 722.0, 644.0, 605.0, 500.0, 469.0]
1H NMR: 7.61 (s, 1H, H-5), 7.50-7.44 (m, 5H, H-3″, H-4″, H-5”), 7.00 (dd, J = 1.3, 2.8 Hz, 1H, H-4’), 6.57 (dd, J = 1.3, 3.8 Hz, 1H, H-3′), 6.30 (dd, J = 2.8, 3.8 Hz, 1H, H-2’), 5.44 (s, 2H, H-1”), 3.94 (s, 3H, H-1”’) ppm
13C NMR: δ 137.3 (1C, s), 135.2 (1C, s), 131.5 (1C, s), 130.5 (1C, s), 130.4 (1C, s), 129.8 (1C, s), 122.7 (1C, s), 118.8 (1C, s), 116.5 (1C, s), 112.2 (1C, s), 110.7 (1C, s), 54.2 (1C, s)

### benchmark_main:R119
Molecular formula: C17H19N3O4S
IR bands (cm-1): [3340.0, 3084.0, 2979.0, 1693.0, 1664.0, 1596.0, 1528.0, 1499.0, 1480.0, 1375.0, 1167.0]
1H NMR: 1.0-1.1(d, J = 32 Hz, 3H), 2.4(s, 1H), 3.0(s, 3H), 3.7-4.0(m, 2H), 7.0(s,1H), 7.2(s, 2H), 7.5-7.8(m, 3H), 8.1(s, 1H), 8.2(s, 2H), 9.8-9.8(m, 2H)
13C NMR: δ 19.0 (1C, s), 43.0 (1C, s), 52.3 (1C, s), 119.4 (1C, s), 119.5 (1C, s), 123.7 (1C, s), 123.9 (1C, s), 126.8 (1C, s), 127.0 (1C, s), 129.2 (1C, s), 129.4 (1C, s), 132.8 (1C, s), 139.2 (1C, s), 141.2 (1C, s), 172.1 (1C, s)

### benchmark_main:R120
Molecular formula: C16H9ClN2O4
IR bands (cm-1): [3227.0, 1675.0, 1596.0, 1508.0, 1344.0]
1H NMR: 7.51-7.60 (m, 2H, ArH), 7.80-7.95 (m, 4H, ArH), 8.04 (d, J = 7.2 Hz, 2H, ArH), 9.58 (s, 1H, NH)
13C NMR: δ 117.6 (1C, s), 117.9 (1C, s), 118.6 (1C, s), 126.7 (1C, s), 127.0 (1C, s), 129.6 (1C, s), 130.9 (1C, s), 132.2 (1C, s), 134.0 (1C, s), 135.2 (1C, s), 141.0 (1C, s), 143.3 (1C, s), 148.0 (1C, s), 177.5 (1C, s), 180.3 (1C, s)

### benchmark_main:R121
Molecular formula: C29H28N2O7S
IR bands (cm-1): [3325.0, 3019.0, 2926.0, 1677.0, 1629.0, 1333.0, 1125.0]
1H NMR: 3.43 (s, 3H, SO2CH3), 3.69 (s, 3H, OCH3), 3.77 (s, 6H, 2OCH3), 3.83 (s, 2H, CH2), 6.52 (s, 2H, trimethoxyphenyl H-2, H-6), 7.44-7.48 (m, 2H, indole H-5, H-6), 7.49-7.52 (m, 3H, phenyl H-2, H-6 and CH=CHCO), 7.53 (d, 1H, J = 7.2 Hz, indole H-7), 7.93 (d, 2H, J = 8 Hz, phenyl H-3, H-5), 8.21 (d, 1H, J = 7.6 Hz, indole H-4), 8.23-8.29 (m, 2H, indole H-2 and CH=CHCO), 10.47 (s, 1H, NH, D2O exchangeable)
13C NMR: δ 41.33 (1C, s), 44.07 (1C, s), 56.28 (1C, s), 60.43 (1C, s), 107.18 (1C, s), 112.89 (1C, s), 113.65 (1C, s), 118.88 (1C, s), 121.11 (1C, s), 123.96 (1C, s), 125.35 (1C, s), 126.01 (1C, s), 126.52 (1C, s), 127.30 (1C, s), 129.94 (1C, s), 131.40 (1C, s), 135.20 (1C, s), 135.85 (1C, s), 138.11 (1C, s), 144.32 (1C, s), 145.1 (1C, s), 152.98 (1C, s), 168.90 (1C, s)
