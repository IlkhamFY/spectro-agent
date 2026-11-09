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
  {"benchmark_expand_500:R55": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R55
Molecular formula: C24H22N4O6
IR bands (cm-1): [3430.0, 1640.0, 1588.0, 1506.0, 1343.0, 1304.0, 1217.0, 1013.0]
1H NMR: 8.09-8.04 (m, 2H), 7.58 (s, 1H), 7.50-7.45 (m, 2H), 7.08 (t, J = 7.9 Hz, 1H), 6.80-6.76 (m, 1H), 6.76-6.72 (m, 1H), 6.68 (d, J = 7.7 Hz, 1H), 3.77-3.66 (m, 4H), 3.57 (s, 3H), 3.06-2.95 (m, 4H) ppm. 13C{1H} NMR (126 MHz, DMSO-d6): δ = 169.9, 166.1, 158.5, 153.8, 151.5, 146.8, 146.5, 138.4, 131.9, 130.9, 128.8, 122.6, 122.4, 120.0, 116.0, 112.6, 54.8, 44.2, 43.0, 42.6 ppm
13C NMR: δ 169.9 (1C, s), 166.1 (1C, s), 158.5 (1C, s), 153.8 (1C, s), 151.5 (1C, s), 146.8 (1C, s), 146.5 (1C, s), 138.4 (1C, s), 131.9 (1C, s), 130.9 (1C, s), 128.8 (1C, s), 122.6 (1C, s), 122.4 (1C, s), 120.0 (1C, s), 116.0 (1C, s), 112.6 (1C, s), 54.8 (1C, s), 44.2 (1C, s), 43.0 (1C, s)

### benchmark_expand_500:R57
Molecular formula: C22H20N4O2
IR bands (cm-1): [3302.0, 3150.0, 1676.0, 1601.0, 1315.0, 1235.0]
1H NMR: 2.25 (s, 3H, Ar-Me), 5.30 (s, 2H, -NCH2CO-), 5.35 (s, 2H, -OCH2), 7.14 (d, 2H, J = 8.0 Hz, Ar-H), 7.21 (d, 1H, J = 8.0 Hz, Ar-H), 7.36 (t, 1H, J = 8.0 Hz, Ar-H), 7.47 (d, 3H, J = 8.0 Hz, Ar-H), 7.54 (s, 1H, Ar-H), 7.84 (d, 3H, J = 8.0 Hz, Ar-H), 8.32 (s, 1H, triazole) and 10.41 (s, 1H, -NH)
13C NMR: δ 21.2 (1C, s), 52.9 (1C, s), 61.8 (1C, s), 107.8 (1C, s), 119.4 (1C, s), 119.9 (1C, s), 124.4 (1C, s), 127.2 (1C, s), 127.5 (1C, s), 128.3 (1C, s), 129.3 (1C, s), 130.0 (1C, s), 130.1 (1C, s), 133.5 (1C, s), 134.9 (1C, s), 136.6 (1C, s), 143.1 (1C, s)

### benchmark_expand_500:R60
Molecular formula: C20H14BrNO2
IR bands (cm-1): [3355.0, 1684.0, 1568.0, 1258.0, 1109.0]
1H NMR: 8.12-8.10 (dd, J1 = 1 Hz, J2 = 8 Hz, 1H), 7.74-7.72 (dd, J1 = 1.5 Hz, J2 = 6 Hz, 2H), 7.72-7.48 (m, 2H), 7.50-7.48 (dd, J1 = 1 Hz, J2 = 8 Hz, 2H), 7.36-7.33 (m, 2H), 6.88 (s, 1H), 5.70 (s, 1H), 3.09 (d, J = 5 Hz, 3H) ppm
13C NMR: δ 163.8 (1C, s), 153.3 (1C, s), 136.6 (1C, s), 130.1 (1C, s), 129.1 (1C, s), 128.9 (1C, s), 128.6 (1C, s), 127.5 (1C, s), 125.2 (1C, s), 124.3 (1C, s), 123.4 (1C, s), 123.3 (1C, s), 118.9 (1C, s), 117.3 (1C, s), 111.1 (1C, s), 108.1 (1C, s), 106.7 (1C, s)

### benchmark_expand_500:R62
Molecular formula: C19H19Cl2NO
IR bands (cm-1): [3429.0, 3068.0, 2929.0, 1668.0]
1H NMR: 7.88 (s, 1H, C3-H), 7.72 (d, J = 9.5 Hz, 1H, C7-H), 7.61 (s, 1H, C1-H), 7.36 (d, J = 9.5 Hz, 1H, C8-H), 7.16 (s, 1H, C10-H), 6.92 (s, 1H, NH), 3.79 (s, 2H, C12-H), 3.68 (s, 2H, C15-H), 2.45 (t, J = 13.5 Hz, 2H, C16-H), 1.55-1.47 (m, 2H, C17-H), 1.08-1.03 (m, 2H, C18-H), 0.66 (t, J = 22.5 Hz, 3H, C19-H)
13C NMR: δ 162.7 (1C, s), 147.8 (1C, s), 145.5 (1C, s), 139.3 (1C, s), 136.3 (1C, s), 132.1 (1C, s), 131.8 (1C, s), 128.3 (1C, s), 127.4 (1C, s), 123.8 (1C, s), 122.0 (1C, s), 118.9 (1C, s), 45.3 (1C, s), 36.7 (1C, s), 32.9 (1C, s), 28.2 (1C, s), 21.3 (1C, s), 18.4 (1C, s)

### benchmark_expand_500:R64
Molecular formula: C14H10N4O4
IR bands (cm-1): [3489.0, 3337.0, 2854.0, 1674.0, 1641.0, 1608.0, 1393.0, 1360.0, 951.0]
1H NMR: 5.86 (s, 2H, NH2), 6.87 (d, J = 2.1 Hz, 1H, H-3), 7.19 (d, J = 2.1 Hz, 1H, H-5), 7.55-7.65 (m, 3H, H-3, H-4, H-5 Ph), 8.09 (dd, J = 7.5 Hz, J = 0.8 Hz, 2H, H-2, H-6, Ph), 10.67 (s, 1H, OH). 13C{1H} NMR (126 MHz, DMSO-d6): δ 113.4, 117.7, 125.3, 127.2, 129.5, 132.2, 144.9, 149.1, 157.5, 168.6, 169.1, 177.3
13C NMR: δ 113.4 (1C, s), 117.7 (1C, s), 125.3 (1C, s), 127.2 (1C, s), 129.5 (1C, s), 132.2 (1C, s), 144.9 (1C, s), 149.1 (1C, s), 157.5 (1C, s), 168.6 (1C, s), 169.1 (1C, s), 177.3 (1C, s)

### benchmark_expand_500:R65
Molecular formula: C13H11N3O5S
IR bands (cm-1): [2919.0, 1709.0, 1573.0, 1522.0, 1357.0, 1226.0]
1H NMR: 2.70 (d, 2JHH = 16.8 Hz, 2H, CH2), 3.07-3.46 (m, 3H, CH2 and CH2S), 3.99-4.09 (m, 1H, CH2N), 4.33-4.41 (m, 1H, CH2N), 4.81 (d, 3JHH = 8.1 Hz, 1H, CH), 7.42 (d, 3JHH = 8.7 Hz, 2H, Ar), 8.15 (d, 3JHH = 8.7 Hz, 2H, Ar)
13C NMR: δ 29.1 (1C, s), 38.2 (1C, s), 49.5 (1C, s), 124.2 (1C, s), 124.6 (1C, s), 128.3 (1C, s), 147.2 (1C, s), 148.7 (1C, s), 160.4 (1C, s), 166.3 (1C, s)
