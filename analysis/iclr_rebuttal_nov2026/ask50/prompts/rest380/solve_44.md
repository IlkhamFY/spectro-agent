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
  {"benchmark_expand:R70": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R70
Molecular formula: C20H19NO
IR bands (cm-1): [3235.0, 2862.0, 2805.0, 1625.0, 1611.0, 1574.0, 1509.0, 1434.0, 1417.0, 1339.0, 1246.0, 1209.0, 1051.0, 1019.0, 940.0, 910.0, 826.0, 768.0, 698.0, 669.0, 584.0, 559.0, 506.0, 468.0, 424.0]
1H NMR: 7.91 (d, J = 7.3 Hz, 2H), 7.46-7.37 (m, 3H), 7.26 (d, J = 7.9 Hz, 2H), 7.21 (d, J = 8.0 Hz, 2H), 6.07 (s, 1H), 3.89 (s, 2H), 3.05 (s, 3H), 2.42 (s, 3H), 2.37 (s, 1H)
13C NMR: δ 188.3 (1C, s), 163.9 (1C, s), 141.3 (1C, s), 138.9 (1C, s), 133.1 (1C, s), 131.0 (1C, s), 129.5 (1C, s), 128.3 (1C, s), 128.1 (1C, s), 127.9 (1C, s), 96.9 (1C, s), 78.2 (1C, s), 73.1 (1C, s), 42.1 (1C, s), 37.9 (1C, s), 21.6 (1C, s)

### benchmark_expand:R72
Molecular formula: C14H14N2O3S
IR bands (cm-1): [3239.0, 1672.0, 1591.0, 1542.0, 1333.0, 1166.0]
1H NMR: 2.04 (s, 3H, CH3CO), 6.99 (t, J = 7.1 Hz, 1H, ArH), 7.04 (d, J = 8.3 Hz, 2H, ArH), 7.19 (t, J = 7.7 Hz, 2H, ArH), 10.28 (s, 1H, NHCO)
13C NMR: δ 24.4 (1C, s), 119.1 (1C, s), 120.6 (1C, s), 124.6 (1C, s), 128.4 (1C, s), 129.6 (1C, s), 133.5 (1C, s), 138.1 (1C, s), 143.4 (1C, s)

### benchmark_expand:R75
Molecular formula: C12H24O2
IR bands (cm-1): [1206.0, 1156.0, 1103.0, 1060.0]
1H NMR: 3.57 (d, J = 11.5 Hz, 2H, CH2), 3.54 (d, J = 11.5 Hz, 2H, CH2), 1.42 (c, J = 7.5 Hz, 2H, CH2), 1.40 (s, 6H, 2xCH3), 1.33-1.27 (m, 4H, 2xCH2), 1.19-1.13 (m, 2H, CH2), 0.91 (t, J = 7.5 Hz, 3H, CH3), 0.81 (t, J = 7.5 Hz, 3H, CH3) ppm
13C NMR: δ 98.1 (1C, s), 68.1 (1C, s), 35.0 (1C, s), 31.3 (1C, s), 24.9 (1C, s), 24.3 (1C, s), 23.7 (1C, s), 23.6 (1C, s), 14.2 (1C, s)

### benchmark_expand:R78
Molecular formula: C20H38O
IR bands (cm-1): [3287.0, 2916.0, 2849.0, 1466.0]
1H NMR: 4.35 (1H, t, J = 7.0 Hz, H-3), 2.44 (1H, d, J = 2.0 Hz, H-1), 1.69 (2H, q, J = 7.0 Hz, H2-4), 1.44 (2H, qi, J = 7.0 Hz, H2-5), 1.22-1.31 (28H, bm), 0.87 (3H, t, J = 7.0 Hz, H3-20)
13C NMR: δ 85.1 (1C, s), 72.7 (1C, s), 62.2 (1C, s), 37.6 (1C, s), 31.9 (1C, s), 29.8 (1C, s), 29.7 (1C, s), 29.6 (1C, s), 29.4 (1C, s), 29.2 (1C, s), 25.1 (1C, s), 22.8 (1C, s)

### benchmark_expand:R81
Molecular formula: C14H14S4
IR bands (cm-1): [792.0, 868.0, 964.0, 1196.0, 1212.0, 1343.0, 1423.0, 1497.0, 2852.0, 2918.0, 3067.0, 3294.0]
1H NMR: 1.85 (qu, J = 7.0 Hz, 2H), 1.97 (t, J = 2.5Hz, 1H), 2.35 (dt, J = 7.0 and 2.5 Hz, 2H), 2.51 (s, 3H), 2.91 (t, J = 7 Hz, 2H), 6.96-7.01 (m, 4H)
13C NMR: δ 17.1 (1C, s), 22.0 (1C, s), 27.9 (1C, s), 37.5 (1C, s), 69.1 (1C, s), 83.1 (1C, s), 123.7 (1C, s), 123.9 (1C, s), 131.6 (1C, s), 133.4 (1C, s), 134.5 (1C, s), 136.9 (1C, s), 138.9 (1C, s), 140.4 (1C, s)

### benchmark_expand:R82
Molecular formula: C14H12FNO2
IR bands (cm-1): [2944.0, 1643.0, 1578.0, 1501.0, 1438.0, 1278.0, 1223.0, 1198.0]
1H NMR: 8.32 (s, 1H), 7.55 (d, J = 1.9 Hz, 1H), 7.38 (dd, J = 8.3, 1.9 Hz, 1H), 7.25-7.15 (m, 2H), 7.08 (dd, J = 11.8, 5.5 Hz, 2H), 6.92 (dd, J = 8.3, 2.1 Hz, 1H), 6.14 (s, 1H, OH), 3.93 (s, 3H)
13C NMR: δ 162.27 (1C, s), 159.85 (1C, s), 159.73 (1C, s), 149.63 (1C, s), 148.19 (1C, s), 146.05 (1C, s), 129.88 (1C, s), 122.39 (1C, s), 122.34 (1C, s), 122.26 (1C, s), 115.89 (1C, s), 115.67 (1C, s), 113.94 (1C, s), 110.42 (1C, s), 55.99 (1C, s)
