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
  {"benchmark_main:R74": ["CCO", "COC"]}

Compounds:

### benchmark_main:R74
Molecular formula: C18H29N
IR bands (cm-1): [3409.0, 3065.0, 3017.0, 2926.0, 2854.0, 1655.0, 1602.0, 1505.0, 1457.0, 1346.0, 1215.0, 1195.0, 1108.0, 1059.0, 743.0]
1H NMR: 0.88 (t, J = 7.2 Hz, 3 H, CH3), 1.20-1.37 (m, 12 H, 6 CH2), 1.57 (m, 2 H, CH2), 1.93 (tt, J = 5.7 Hz, J = 6.4 Hz, 2 H, CH2, 3-H), 2.74 (t, J = 6.4 Hz, 2 H, CH2, 4-H), 3.21 (t, J = 7.6 Hz, 2 H, CH2), 3.27 (t, J = 5.7 Hz, 2 H, CH2, 2-H), 6.53 (dd, J = 7.3 Hz, J = 7.4 Hz, 1 H, 6-H), 6.55 (d, J = 8.2 Hz, 1 H, 8-H), 6.92 (d, J = 7.3 Hz, 1 H, 5-H), 7.03 (dd, J = 7.4 Hz, J = 8.2 Hz, 1 H, 7-H)
13C NMR: δ 14.1 (1C, s), 22.2 (1C, s), 22.7 (1C, s), 26.1 (1C, s), 27.3 (1C, s), 28.2 (1C, s), 29.3 (1C, s), 29.6 (1C, s), 29.6 (1C, s), 31.89 (1C, s), 49.4 (1C, s), 51.5 (1C, s), 110.4 (1C, s), 115.1 (1C, s), 122.1 (1C, s), 127.0 (1C, s), 129.1 (1C, s), 145.3 (1C, s)

### benchmark_main:R75
Molecular formula: C22H21NO4
IR bands (cm-1): [3072.0, 1813.0, 1691.0, 1652.0, 1603.0, 1463.0, 1307.0, 1223.0, 995.0, 884.0, 760.0]
1H NMR: 8.03 (d, J = 7.8 Hz, 2H), 7.84 (t, J = 10.2 Hz, 1H), 7.59 (t, J = 7.4 Hz, 1H), 7.49 (t, J = 7.6 Hz, 2H), 7.39 (t, J = 7.7 Hz, 1H), 6.97 (t, J = 7.5 Hz, 1H), 6.87 (t, J = 8.4 Hz, 1H), 4.74 (dd, J = 13.0, 2.9 Hz, 1H), 3.22 (dd, J = 16.9, 13.0 Hz, 1H), 2.92 (dd, J = 16.9, 2.9 Hz, 1H), 1.93 (dd, J = 13.8, 6.3 Hz, 1H), 1.84 (dd, J = 13.8, 6.5 Hz, 1H), 1.66-1.60 (m, 1H), 0.91 (d, J = 6.7 Hz, 3H), 0.90 (d, J = 6.6 Hz, 3H)
13C NMR: δ 191.1 (1C, s), 178.6 (1C, s), 161.7 (1C, s), 160.6 (1C, s), 136.3 (1C, s), 133.2 (1C, s), 129.0 (1C, s), 128.4 (1C, s), 126.9 (1C, s), 125.7 (1C, s), 122.0 (1C, s), 121.0 (1C, s), 118.0 (1C, s), 80.7 (1C, s), 75.9 (1C, s), 41.1 (1C, s), 38.1 (1C, s), 24.8 (1C, s), 24.0 (1C, s), 23.5 (1C, s)

### benchmark_main:R80
Molecular formula: C17H14ClN3O3
IR bands (cm-1): [2926.0, 1721.0, 1491.0, 1262.0, 1093.0, 1014.0, 831.0]
1H NMR: 8.51 (s, 1H), 7.44-7.37 (m, 3H), 7.35-7.30 (m, 2H), 7.16 (d, J = 8.3 Hz, 2H), 7.02 (d, J = 8.3 Hz, 2H), 5.13 (s, 1H), 1.73 (s, 3H) ppm
13C NMR: δ 152.8 (1C, s), 148.5 (1C, s), 136.6 (1C, s), 131.1 (1C, s), 131.0 (1C, s), 130.8 (1C, s), 128.1 (1C, s), 126.6 (1C, s), 125.3 (1C, s), 124.4 (1C, s), 107.4 (1C, s), 54.2 (1C, s)

### benchmark_main:R81
Molecular formula: C15H9BrO2
IR bands (cm-1): [1768.0, 1652.0, 1601.0, 1463.0, 1357.0, 1266.0, 1075.0, 945.0, 746.0, 678.0, 522.0]
1H NMR: 8.29 (d, J = 7.92 Hz, 1H), 7.95 (d, J = 7.72 Hz, 1H), 7.87 (d, J = 7.8 Hz, 1H), 7.77-7.73 (m, 1H), 7.63-7.56 (m, 2H), 7.39-7.36 (m, 1H), 7.17-7.13 (m, 1H), 6.87 (s, 1H)
13C NMR: δ 166.96 (1C, s), 145.76 (1C, s), 140.52 (1C, s), 134.78 (1C, s), 133.05 (1C, s), 132.65 (1C, s), 131.98 (1C, s), 130.37 (1C, s), 129.62 (1C, s), 127.92 (1C, s), 125.72 (1C, s), 124.71 (1C, s), 123.56 (1C, s), 120.41 (1C, s), 105.15 (1C, s)

### benchmark_main:R83
Molecular formula: C27H22N2O3S
IR bands (cm-1): [3060.0, 2965.0, 2920.0, 1780.0, 1706.0, 1684.0, 1596.0, 1577.0, 1466.0, 1446.0, 1368.0, 1232.0, 1192.0, 1173.0, 1028.0, 772.0, 740.0, 687.0]
1H NMR: 8.20 (d, J = 7.3 Hz, 2H, Ar-H), 7.71 (dd, J = 7.4 Hz, 1H, Ar-H), 7.64-7.56 (m, 2H, Ar-H), 7.22 (d, J = 8.0 Hz, 1H, Ar-H), 7.17 (d, J = 7.6 Hz, 1H, Ar-H), 7.11 (dd, J = 7.6 Hz, 2H, Ar-H), 7.06-6.95 (m, 2H, Ar-H), 6.78 (dd, J = 7.8 Hz, 1H, Ar-H), 6.21 (s, 1H, N-CH), 5.69 (d, J = 8.7 Hz, 1H, S-CH-N), 4.36 (d, J = 9.5 Hz, 1H, CH), 3.90 (t, J = 8.6 Hz, 1H, CH), 1.98 (s, 3H, CH3), 1.07 (s, 3H, CH3)
13C NMR: δ 195.3 (1C, s), 176.1 (1C, s), 172.8 (1C, s), 145.8 (1C, s), 136.0 (1C, s), 135.6 (1C, s), 134.9 (1C, s), 133.9 (1C, s), 133.8 (1C, s), 130.4 (1C, s), 129.0 (1C, s), 128.8 (1C, s), 128.1 (1C, s), 126.0 (1C, s), 125.4 (1C, s), 122.4 (1C, s), 121.4 (1C, s), 109.9 (1C, s), 70.5 (1C, s), 67.6 (1C, s), 50.3 (1C, s), 47.7 (1C, s), 17.4 (1C, s), 15.6 (1C, s)

### benchmark_main:R85
Molecular formula: C17H14N2O3S2
IR bands (cm-1): [3057.0, 1726.0, 1678.0, 1542.0]
1H NMR: 2.62 (t, J = 7.4 Hz, 2H, CH2CO), 4.26 (t, J = 7.4 Hz, 2H, NCH2), 7.16-7.89 (m, 9H, HAr+CH, Hthiophene)
13C NMR: δ 32.0 (1C, s), 50.0 (1C, s), 123.5 (1C, s), 127.2 (1C, s), 128.3 (1C, s), 128.9 (1C, s), 130.0 (1C, s), 130.1 (1C, s), 131.5 (1C, s), 133.5 (1C, s), 138.4 (1C, s), 140.0 (1C, s), 172.1 (1C, s), 175.3 (1C, s), 179.3 (1C, s)
