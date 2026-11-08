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
  {"benchmark_expand:R42": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R42
Molecular formula: C12H14N4S
IR bands (cm-1): [3028.0, 2983.0, 2380.0, 2983.0, 1745.0, 1618.0, 1541.0, 1448.0, 1404.0, 1348.0]
1H NMR: 7.39-7.37 (m, 2H), 7.33-7.29 (m, 2H), 7.27-7.24 (m, 1H), 6.71 (d, J = 16 Hz, 1H), 6.38 (dd, J = 16.0, 7.6 Hz, 1H), 5.66-5.58 (m, 1H), 3.91 (s, 3H), 1.74 (d, J = 6.8 Hz, 3H)
13C NMR: δ 163.39 (1C, s), 135.59 (1C, s), 133.60 (1C, s), 128.58 (1C, s), 128.31 (1C, s), 126.69 (1C, s), 125.92 (1C, s), 56.59 (1C, s), 34.53 (1C, s), 19.44 (1C, s)

### benchmark_expand:R45
Molecular formula: C12H13N3S4
IR bands (cm-1): [792.0, 867.0, 964.0, 1069.0, 1245.0, 1421.0, 1498.0, 1687.0, 2092.0, 2859.0, 2920.0, 3068.0]
1H NMR: 1.89 (qu, J = 7.0 Hz, 2H), 2.50 (s, 3H), 2.87 (t, J = 7.0 Hz, 2H), 3.44 (t, J = 7.0 Hz, 2H), 6.97-7.01 (m, 4H)
13C NMR: δ 21.9 (1C, s), 28.4 (1C, s), 35.6 (1C, s), 49.5 (1C, s), 123.7 (1C, s), 123.9 (1C, s), 131.5 (1C, s), 132.7 (1C, s), 134.8 (1C, s), 136.9 (1C, s), 138.9 (1C, s), 140.6 (1C, s)

### benchmark_expand:R51
Molecular formula: C12H13N3O3S2
IR bands (cm-1): [3358.0, 3021.0, 2981.0, 1706.0]
1H NMR: 1.24 (t, 3H, CH3, J = 6.8 Hz), 2.60 (s, 3H, CH3), 4.21 (q, 2H, CH2, J = 6.8 Hz), 7.05 (d, 1H, CH-thiazole, J = 4 Hz), 7.40 (d, 1H, CH-thiazole, J = 4 Hz), 7.82 (s, 2H, NH2), 12.16 (s, 1H, NH) ppm
13C NMR: δ 14.34 (1C, s), 16.33 (1C, s), 59.41 (1C, s), 106.25 (1C, s), 112.01 (1C, s), 112.03 (1C, s), 132.14 (1C, s), 143.69 (1C, s), 162.02 (1C, s), 164.03 (1C, s), 165.00 (1C, s)

### benchmark_expand:R53
Molecular formula: C15H18O5
IR bands (cm-1): [3508.0, 2911.0, 1755.0, 1575.0, 1509.0, 1423.0, 1270.0, 1207.0, 1141.0, 1012.0, 977.0, 795.0]
1H NMR: 1.07 (d, 6H, J = 6.8 Hz, 2CH3), 2.91-3.05 (m, 1H, CH(CH3)2), 3.83 (s, 3H, OCH3), 4.73 (s, 2H, OCH2), 6.86-6.98 (m, 1H, Ar-H), 6.94 (d, 1H, J = 16.0 Hz, CH), 7.23 (dd, 1H, J = 8.4, 1.8 Hz, Ar-H), 7.39 (d, 1H, J = 1.8 Hz, Ar-H), 7.54 (d, 1H, J = 16.0 Hz, CH), 13.09 (br. s, 1H, COOH)
13C NMR: δ 18.6 (1C, s), 38.2 (1C, s), 55.9 (1C, s), 65 (1C, s), 111.3 (1C, s), 113 (1C, s), 122.7 (1C, s), 123.1 (1C, s), 128 (1C, s), 141.9 (1C, s), 149.3 (1C, s), 149.4 (1C, s), 169.8 (1C, s), 202.9 (1C, s)

### benchmark_expand:R55
Molecular formula: C15H17N5OS
IR bands (cm-1): [3227.0, 3149.0, 2835.0, 1600.0]
1H NMR: 10.42 (1H, s, NH), 9.49 (1H, d, J = 1.3 Hz, H-3), 8.52 (1H, d, J = 1.3 Hz, H-6), 8.42 (1H, bs, NH2), 8.23 (1H, bs, NH2), 7.23-7.16 (2H, m, AA′, BB′, benzyl H-2, H-6), 6.87-6.81 (2H, m, AA′, BB′, benzyl H-3, H-5), 4.07 (2H, s, CH2), 3.69 (3H, s, OCH3), 2.33 (3H, s, CH3)
13C NMR: δ 179.3 (1C, s), 158.0 (1C, s), 155.8 (1C, s), 148.0 (1C, s), 146.5 (1C, s), 142.5 (1C, s), 142.3 (1C, s), 130.9 (1C, s), 130.1 (1C, s), 114.1 (1C, s), 55.2 (1C, s), 39.9 (1C, s), 12 (1C, s)

### benchmark_expand:R56
Molecular formula: C14H17N3O2
IR bands (cm-1): [3479.0, 3067.0, 2964.0, 2876.0, 1688.0, 1646.0, 1607.0, 1583.0, 1490.0, 1453.0, 1428.0, 1402.0, 1343.0, 1288.0, 1258.0, 1190.0, 926.0, 897.0, 784.0, 757.0, 730.0, 700.0, 672.0, 646.0, 600.0, 547.0, 511.0]
1H NMR: 7.24-7.28 (m, 2H), 7.18-7.23 (m, 3H), 6.88 (s, 2H), 4.89 (s, 2H), 4.70 (s, 1H), 3.70-3.75 (m, 2H), 1.51 (sxt, J = 7.5 Hz, 2H), 0.84 (t, J = 7.4 Hz, 3H); 13C{1H} NMR (176 MHz, DMSO-d6) δ 161.2, 154.6, 151.5, 138.4, 128.2, 127.4, 126.8, 74.9, 43.3, 43.0, 20.9, 10.8
13C NMR: δ 161.2 (1C, s), 154.6 (1C, s), 151.5 (1C, s), 138.4 (1C, s), 128.2 (1C, s), 127.4 (1C, s), 126.8 (1C, s), 74.9 (1C, s), 43.3 (1C, s), 43.0 (1C, s), 20.9 (1C, s), 10.8 (1C, s)
