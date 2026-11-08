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
  {"benchmark_expand_500:R116": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R116
Molecular formula: C32H48NO4-
IR bands (cm-1): [3423.0, 3305.0, 2924.0, 2853.0, 1643.0, 1513.0, 1248.0]
1H NMR: 7.35-7.23 (m, 5H, Ar-H), 7.16 (d, J = 8.2 Hz, 2H, Ar-H), 6.85 (d, J = 8.2 Hz, 2H, Ar-H), 5.70 (s, 1H, NH), 4.61 (d, J = 11.5 Hz, 1H, OCH2), 4.54 (d, J = 11.5 Hz, 1H, OCH2), 4.34 (dd, J = 14.5, 5.5 Hz, 1H, NCH2), 4.30 (dd, J = 14.5, 5.5 Hz, 1H, NCH2), 3.79 (s, 3H, OCH3), 3.52 (m, 1H, H-4), 3.36 (ddd, J = 5.3, 5.3, 5.1 Hz, 1H, H-5), 2.30-2.23 (m, 2H), 2.26 (s, 1H, OH), 2.05 (ddd, J = 14.0, 7.3, 7.3 Hz, 1H, H-2), 1.88 (ddd, J = 14.0, 7.0, 7.0 Hz, 1H, H-2), 1.52-1.40 (m, 3H), 1.35-1.20 (m, 19H), 0.88 (t, J = 6.6 Hz, 3H, CH3)
13C NMR: δ 172.4 (1C, s), 159.1 (1C, s), 138.3 (1C, s), 130.4 (1C, s), 129.2 (1C, s), 128.5 (1C, s), 127.9 (1C, s), 127.8 (1C, s), 114.1 (1C, s), 81.2 (1C, s), 72.7 (1C, s), 72.6 (1C, s), 55.3 (1C, s), 43.1 (1C, s), 33.5 (1C, s), 31.9 (1C, s), 31.8 (1C, s), 29.7 (1C, s), 29.4 (1C, s), 26.0 (1C, s), 25.8 (1C, s), 22.7 (1C, s), 14.1 (1C, s)

### benchmark_expand_500:R117
Molecular formula: C20H29NO4S
IR bands (cm-1): [2996.0, 2913.0, 2847.0, 1912.0, 1733.0, 1651.0, 1593.0, 1459.0, 1413.0, 1371.0, 1320.0, 1237.0, 1177.0, 1132.0, 1090.0, 1024.0, 933.0, 831.0, 784.0, 756.0]
1H NMR: 7.78-7.68 (m, 3H, ArH), 7.36-7.28 (m, 1H, ArH), 3.64-3.56 (m, 2H, CH2), 1.83-1.72 (m, 2H, CH2), 1.41-1.14 (m, 18H, CH2), 0.85 (t, J = 7.1 Hz, 3H, CH3)
13C NMR: δ 178.8 (1C, s), 156.5 (1C, s), 146.9 (1C, s), 137.9 (1C, s), 125.1 (1C, s), 125.0 (1C, s), 119.4 (1C, s), 114.1 (1C, s), 53.7 (1C, s), 31.3 (1C, s), 29.0 (1C, s), 28.9 (1C, s), 28.7 (1C, s), 28.7 (1C, s), 28.4 (1C, s), 27.3 (1C, s), 22.1 (1C, s), 22.1 (1C, s), 14.0 (1C, s)

### benchmark_expand_500:R119
Molecular formula: C18H15N3O4S
IR bands (cm-1): [3324.0, 3283.0, 1721.0, 1652.0, 1589.0, 1518.0, 1237.0]
1H NMR: 11.70 (s, 1H, NH-C=O), 10.00 (s, 2H, NH-C=S), 9.01 (s, 1H, C-H, H-4), 7.69 (d, 1H, J = 7.8 Hz, H-8), 7.40-7.37 (m, 1H, H-6), 7.30-7.17 (m, 2H, H-7, H-5), 7.00-6.91 (m, 2H, H-4′, H-5′), 6.90-6.75 (m, 2H, H-2′, H-6′), 3.76 (s, 3H, OCH3)
13C NMR: δ 180.7 (1C, s), 163.2 (1C, s), 159.4 (1C, s), 150.4 (1C, s), 140.7 (1C, s), 133.7 (1C, s), 131.3 (1C, s), 129.9 (1C, s), 129.1 (1C, s), 127.5 (1C, s), 125.7 (1C, s), 124.5 (1C, s), 120.7 (1C, s), 120.0 (1C, s), 119.6 (1C, s), 117.0 (1C, s), 111.5 (1C, s), 55.5 (1C, s)

### benchmark_expand_500:R120
Molecular formula: C12H12O3
IR bands (cm-1): [2926.0, 2924.0, 2839.0, 1599.0, 1485.0, 1467.0, 1325.0, 1285.0, 1063.0]
1H NMR: 7.04 (2H, t, J = 0.91 Hz, Ar-H), 6.97 (2H, s, =CH), 5.68 (2H, s, CH), 3.85 (6H, s, CH3O)
13C NMR: δ 146.1 (1C, s), 143.6 (1C, s), 107.0 (1C, s), 82.8 (1C, s), 56.7 (1C, s)

### benchmark_expand_500:R121
Molecular formula: C35H27N3
IR bands (cm-1): [3296.0, 3056.0, 2971.0, 2911.0, 2814.0, 1611.0, 1528.0, 1494.0, 1473.0, 1447.0, 1349.0, 1224.0, 1169.0, 926.0, 742.0, 704.0, 644.0, 624.0, 550.0, 442.0]
1H NMR: 7.92-7.86 (m, 2 H), 7.74 (d, J = 7.8 Hz, 2 H), 7.52-7.42 (m, 2 H), 7.40-7.20 (m, 7 H), 6.96 (d, J = 7.8 Hz, 2 H), 6.87 (t, J = 7.8 Hz, 1 H), 6.78 (t, J = 7.8 Hz, 2 H), 4.82 (m, 1 H), 3.42 (s, 1 H), 2.88 (m, 1 H), 2.40 (m, 1 H), 2.22-2.00 (m, 4 H), 1.78 (m, 1 H)
13C NMR: δ 160.8 (1C, s), 147.9 (1C, s), 138.7 (1C, s), 134.0 (1C, s), 132.0 (1C, s), 130.7 (1C, s), 130.2 (1C, s), 129.6 (1C, s), 129.1 (1C, s), 127.5 (1C, s), 126.9 (1C, s), 126.6 (1C, s), 126.5 (1C, s), 125.8 (1C, s), 124.0 (1C, s), 122.9 (1C, s), 122.2 (1C, s), 120.6 (1C, s), 110.6 (1C, s), 110.2 (1C, s), 81.5 (1C, s), 70.0 (1C, s), 71.2 (1C, s), 69.6 (1C, s), 56.1 (1C, s), 43.4 (1C, s), 42.9 (1C, s), 26.5 (1C, s), 25.1 (1C, s), 17.5 (1C, s)

### benchmark_expand_500:R123
Molecular formula: C22H16ClIO4S
IR bands (cm-1): [3007.0, 1683.0, 1604.0, 1506.0, 1321.0, 1259.0, 1033.0, 831.0, 786.0, 557.0]
1H NMR: 8.22 (d, J = 7.4 Hz, 1H), 7.57-7.48 (m, 6H), 7.37 (t, J = 7.2 Hz, 2H), 7.10 (d, J = 8.7 Hz, 2H), 6.78 (d, J = 8.7 Hz, 2H), 3.85 (s, 3H)
13C NMR: δ 189.3 (1C, s), 161.0 (1C, s), 149.5 (1C, s), 141.1 (1C, s), 135.7 (1C, s), 134.6 (1C, s), 134.1 (1C, s), 133.7 (1C, s), 133.1 (1C, s), 132.5 (1C, s), 132.4 (1C, s), 129.7 (1C, s), 129.1 (1C, s), 128.8 (1C, s), 127.6 (1C, s), 115.7 (1C, s), 113.7 (1C, s), 55.9 (1C, s)
