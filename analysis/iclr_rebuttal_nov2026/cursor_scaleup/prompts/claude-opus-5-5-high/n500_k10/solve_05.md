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
  {"benchmark_main:R36": ["CCO", "COC"]}

Compounds:

### benchmark_main:R36
Molecular formula: C14H19N3O
IR bands (cm-1): [3468.0, 2959.0, 1648.0, 1381.0, 1126.0]
1H NMR: 7.89 (s, 1H), 7.81 (d, J = 7.1 Hz, 2H), 7.42 (t, J = 7.4 Hz, 2H), 7.34 (t, J = 7.4 Hz, 1H), 5.76 (q, J = 6.0 Hz, 1H), 3.26 (dd, J = 9.2, 6.9 Hz, 1H), 3.08 (dd, J = 9.2, 6.6 Hz, 1H), 1.82 (d, J = 6.0 Hz, 3H), 1.78 (dd, J = 13.4, 6.7 Hz, 1H), 0.85 (d, J = 6.7 Hz, 3H), 0.80 (d, J = 6.7 Hz, 3H)
13C NMR: δ 147.7 (1C, s), 131.2 (1C, s), 130.4 (1C, s), 128.8 (1C, s), 128.5 (1C, s), 126.0 (1C, s), 89.9 (1C, s), 75.8 (1C, s), 28.2 (1C, s), 20.8 (1C, s), 19.2 (1C, s), 19.1 (1C, s)

### benchmark_main:R37
Molecular formula: C14H14BrNO3S
IR bands (cm-1): [3454.0, 3214.0, 2955.0, 1319.0, 1156.0, 694.0]
1H NMR: 4.00 (d, 2H, J = 6 Hz, CH2), 4.87 (d, 2H, J = 5.2 Hz, CH2), 5.42 (bs, 1H, OH, D2O exch.), 7.20 (bs, 2H, CHAr), 7.38 (bs, 3H, CHAr), 7.59-7.63 (m, 1H, CHAr), 7.75-7.78 (m, 2H, CHAr), 8.23 (bs, 1H, NH, D2O exch.)
13C NMR: δ 45.6 (1C, s), 59.9 (1C, s), 122.0 (1C, s), 127.0 (1C, s), 127.2 (1C, s), 127.9 (1C, s), 128.5 (1C, s), 130.4 (1C, s), 130.7 (1C, s), 130.8 (1C, s), 132.9 (1C, s), 137.2 (1C, s), 141.2 (1C, s), 141.5 (1C, s)

### benchmark_main:R38
Molecular formula: C13H15NO4
IR bands (cm-1): [2970.0, 2936.0, 1725.0, 1642.0, 1608.0, 1537.0, 1382.0, 1370.0, 1269.0, 1205.0, 1185.0, 1072.0, 829.0]
1H NMR: 7.48 (s, 1H), 7.32 (d, J = 8.5 Hz, 2H), 7.21 (d, J = 8.5 Hz, 2H), 4.34 (q, J = 7.0 Hz, 2H), 2.64 (q, J = 7.5 Hz, 2H), 1.33 (t, J = 7.0 Hz, 3H), 1.2 (t, J = 7.5 Hz, 3H)
13C NMR: δ 159.51 (1C, s), 149.51 (1C, s), 139.58 (1C, s), 133.03 (1C, s), 130.15 (1C, s), 129.08 (1C, s), 126.47 (1C, s), 63.05 (1C, s), 29.00 (1C, s), 15.11 (1C, s), 14.16 (1C, s)

### benchmark_main:R40
Molecular formula: C12H15NO3
IR bands (cm-1): [3309.0, 1658.0, 1535.0, 1187.0, 910.0, 755.0, 593.0]
1H NMR: 12.17 (br s, 1H), 9.77 (s, 1H), 7.62 (d, 2H, J = 8.2 Hz), 7.31 (t, 2H, J = 7.3 Hz), 7.05 (t, 1H, J = 7.2 Hz), 5.7 (s, 2H), 3.08 (d, 1H, J = 3.6 Hz), 2.93 (d, 1H, J = 3.6 Hz), 2.65 (dd, 2H, J = 6, 4.6 Hz), 2.32 (dd, 2H, J = 5.5, 4.4 Hz)
13C NMR: δ 175.03 (1C, s), 172.10 (1C, s), 139.50 (1C, s), 128.55 (1C, s), 125.71 (1C, s), 124.54 (1C, s), 122.77 (1C, s), 119.08 (1C, s), 40.05 (1C, s), 39.21 (1C, s), 26.71 (1C, s), 26.04 (1C, s)

### benchmark_main:R41
Molecular formula: C6H13NO2
IR bands (cm-1): [2940.0, 2857.0, 1073.0, 1037.0]
1H NMR: 5.68 (m, 1H), 4.80 (dd, J = 6.0, 3.0 Hz, 1H), 3.98-3.92 (m, 1H), 3.58-3.55 (m, 1H), 2.78 (s, 3H), 1.83-1.75 (m, 1H), 1.74-1.69 (m, 1H), 1.59-1.46 (m, 4H)
13C NMR: δ 101.3 (1C, s), 63.3 (1C, s), 39.7 (1C, s), 29.4 (1C, s), 25.5 (1C, s), 20.4 (1C, s)

### benchmark_main:R42
Molecular formula: C10H8ClN3O3S
IR bands (cm-1): [3336.0, 3070.0, 2943.0, 2765.0, 1620.0, 1600.0, 1554.0, 1354.0, 1188.0, 721.0]
1H NMR: 14.46 (brs, 1H, NHCS), 7.64 (d, J = 1.47 Hz, 1H, ArH), 7.53 (dd, J = 8.42, 1.83 Hz, 1H, ArH), 6.90 (d, J = 8.42 Hz, 1H, ArH), 6.26 (s, 2H, CH2)
13C NMR: δ 176.74 (1C, s), 160.29 (1C, s), 148.34 (1C, s), 127.38 (1C, s), 125.93 (1C, s), 125.66 (1C, s), 116.74 (1C, s), 115.03 (1C, s), 109.83 (1C, s)
