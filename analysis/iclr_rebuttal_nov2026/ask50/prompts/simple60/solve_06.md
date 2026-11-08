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
  {"benchmark_main:R43": ["CCO", "COC"]}

Compounds:

### benchmark_main:R43
Molecular formula: C17H15BrN2OS
IR bands (cm-1): [3628.0, 3306.0, 2352.0, 1732.0, 1698.0, 1656.0, 1564.0, 746.0]
1H NMR: 9.71 (s, 1H), 8.91 (d, J = 8.4 Hz, 1H), 7.72 (d, J = 8.0 Hz, 1H), 7.67 (d, J = 8.0 Hz, 1H), 7.49 (t, J = 7.6 Hz, 1H), 7.34 (t, J = 7.6 Hz, 1H), 7.21 (t, J = 7.6 Hz, 1H), 7.01 (t, J = 8.0 Hz, 1H), 6.91 (d, J = 8.0 Hz, 1H), 3.78 (s, 3H), 2.34 (s, 3H)
13C NMR: δ 194.2 (1C, s), 150.1 (1C, s), 135.7 (1C, s), 135.2 (1C, s), 130.8 (1C, s), 129.4 (1C, s), 127.98 (1C, s), 127.80 (1C, s), 127.2 (1C, s), 125.1 (1C, s), 121.4 (1C, s), 120.5 (1C, s), 119.7 (1C, s), 110.5 (1C, s), 57.8 (1C, s), 56.1 (1C, s), 28.7 (1C, s)

### benchmark_main:R44
Molecular formula: C7H10O4
IR bands (cm-1): [3504.0, 2956.0, 1705.0, 1281.0, 1202.0, 1138.0, 688.0]
1H NMR: 3.77 (s, 1H), 2.59 (t, J = 8.1 Hz, 1H), 2.08-1.95 (m, 1H)
13C NMR: δ 177.9 (1C, s), 172.2 (1C, s), 100.1 (1C, s), 52.9 (1C, s), 52.6 (1C, s), 29.0 (1C, s), 16.3 (1C, s)

### benchmark_main:R46
Molecular formula: C20H20O2
IR bands (cm-1): [1645.0, 1601.0, 1409.0, 1299.0, 961.0, 752.0, 723.0]
1H NMR: 8.00 (d, J = 2.4 Hz, 2H), 7.88-7.78 (m, 4H), 7.31-7.24 (m, 2H), 2.35 (s, 12H) ppm; 13C{1H} NMR (101 MHz, chloroform-d) δ 189.6, 143.7, 137.4, 134.9 (2C), 130.1, 123.0, 126.7, 20.2, 19.8 ppm; ATR-
13C NMR: δ 189.6 (1C, s), 143.7 (1C, s), 137.4 (1C, s), 134.9 (1C, s), 130.1 (1C, s), 123.0 (1C, s), 126.7 (1C, s), 20.2 (1C, s)

### benchmark_main:R50
Molecular formula: C11H8N4O2
IR bands (cm-1): [3241.0, 2241.0, 1689.0, 1560.0, 1538.0, 1496.0, 1255.0, 1038.0, 945.0, 889.0, 713.0]
1H NMR: 11.91 (broad s, 1H, NH), 11.39 (broad s, 1H, NH), 7.68 (d, J = 2.4 Hz, 1H, Ar-H), 7.40 (dd, J = 8.4, 2.4 Hz, 1H, Ar-H), 7.29 (d, J = 8.4 Hz, 1H, Ar-H), 2.20 (s, 3H, CH3)
13C NMR: δ 141.7 (1C, s), 140.7 (1C, s), 134.9 (1C, s), 133.7 (1C, s), 131.4 (1C, s), 129.9 (1C, s), 119.0 (1C, s), 116.9 (1C, s), 112.6 (1C, s), 112.4 (1C, s), 17.4 (1C, s)

### benchmark_main:R51
Molecular formula: C11H17NO2
IR bands (cm-1): [3344.0, 1589.0, 1512.0, 1463.0, 1417.0, 1259.0, 1234.0, 1138.0, 1025.0]
1H NMR: 6.81 (d, J = 7.9 Hz, 1H), 6.76-6.66 (m, 2H), 3.87 (s, 3H), 3.86 (s, 3H), 3.20-3.09 (m, 1H), 2.67 (dd, J = 13.4, 5.2 Hz, 1H), 2.51-2.33 (m, 2H), 1.63 (s, 1H), 1.12 (d, J = 6.3 Hz, 3H)
13C NMR: δ 148.83 (1C, s), 147.47 (1C, s), 132.30 (1C, s), 121.14 (1C, s), 112.41 (1C, s), 111.24 (1C, s), 55.91 (1C, s), 55.83 (1C, s), 48.55 (1C, s), 46.14 (1C, s), 23.51 (1C, s)

### benchmark_main:R52
Molecular formula: C6H8O5
IR bands (cm-1): [2964.0, 1745.0, 1682.0, 1655.0, 1437.0, 1252.0, 1205.0, 932.0, 908.0, 787.0]
1H NMR: 10.29-9.10 (br, 1H), 7.03 (dt, J = 15.8, 4.3 Hz, 1H), 6.06 (d, J = 15.8 Hz, 1H), 4.82 (dd, J = 4.4, 2.0 Hz, 2H), 3.81 (s, 3H)
13C NMR: δ 171.1 (1C, s), 155.4 (1C, s), 143.4 (1C, s), 121.6 (1C, s), 65.8 (1C, s), 55.3 (1C, s)
