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
  {"benchmark_main:R86": ["CCO", "COC"]}

Compounds:

### benchmark_main:R86
Molecular formula: C17H13N5
IR bands (cm-1): [3362.0, 3283.0, 1617.0, 1525.0, 1439.0, 1390.0, 1321.0, 1251.0, 1203.0, 1171.0, 1106.0, 1039.0, 1017.0, 962.0, 929.0, 826.0, 759.0, 709.0, 681.0, 657.0]
1H NMR: 8.31 (s, 1H, CH), 7.89 (dd, J = 7.5, 1.7 Hz, 2 H, 2CH), 7.76 (dd, J = 7.4, 1.2 Hz, 2 H, 2CH), 7.67 (t, J = 7.3 Hz, 2 H, 2CH), 7.64-7.53 (m, 4 H, 4CH), 3.86 (s, 2 H, NH2)
13C NMR: δ 155.52 (1C, s), 154.86 (1C, s), 150.96 (1C, s), 136.16 (1C, s), 130.92 (1C, s), 130.35 (1C, s), 129.67 (1C, s), 129.54 (1C, s), 129.06 (1C, s), 128.72 (1C, s), 128.33 (1C, s), 127.82 (1C, s), 124.88 (1C, s)

### benchmark_main:R89
Molecular formula: C25H18N2O7
IR bands (cm-1): [3320.0, 3062.0, 2976.0, 1741.0, 1687.0, 1588.0, 1553.0, 1526.0, 1441.0]
1H NMR: 8.66 (s, 1H), 8.32 (d, J = 7.8 Hz, 1H), 8.25 (d, J = 8.1 Hz, 1H), 7.94 (d, J = 7.5 Hz, 1H), 7.89-7.76 (m, 3H), 7.68 (d, J = 7.5 Hz, 1H), 7.13 (s, 1H), 7.05 (d, J = 10.7 Hz, 5H), 6.24 (d, J = 12.2 Hz, 1H), 4.78 (d, J = 12.2 Hz, 1H), 2.80 (d, J = 15.5 Hz, 1H), 2.73 (d, J = 15.6 Hz, 1H). 13C{1H} NMR (100 MHz, DMSO-d6) δ 203.1, 200.8, 148.3, 147.4, 142.3, 141.8, 136.9, 133.6, 133.1, 130.3, 128.9, 128.3, 127.9, 123.4, 123.0, 121.2, 93.6, 80.3, 60.7, 53.9, 47.6
13C NMR: δ 203.1 (1C, s), 200.8 (1C, s), 148.3 (1C, s), 147.4 (1C, s), 142.3 (1C, s), 141.8 (1C, s), 136.9 (1C, s), 133.6 (1C, s), 133.1 (1C, s), 130.3 (1C, s), 128.9 (1C, s), 128.3 (1C, s), 127.9 (1C, s), 123.4 (1C, s), 123.0 (1C, s), 121.2 (1C, s), 93.6 (1C, s), 80.3 (1C, s), 60.7 (1C, s), 53.9 (1C, s), 47.6 (1C, s)

### benchmark_main:R90
Molecular formula: C18H19N3O2
IR bands (cm-1): [1713.0, 1649.0, 1556.0, 1450.0]
1H NMR: 8.61 (s, 1H, Ar-CH), 8.14 (d, J = 7.45 Hz, 1H, Ar-CH), 7.57 (d, J = 7.45 Hz, 1H, Ar-CH), 7.34-7.28 (m, 2H, Ar-CH), 6.70 (s, 1H, vinylic proton), 3.53 (s, 4H, CH2 × 2), 3.15 (s, 3H, NCH3), 1.62 (s, 6H, CH2 × 3)
13C NMR: δ 170.8 (1C, s), 161.0 (1C, s), 154.9 (1C, s), 148.0 (1C, s), 140.0 (1C, s), 126.6 (1C, s), 125.4 (1C, s), 123.6 (1C, s), 121.4 (1C, s), 117.4 (1C, s), 111.9 (1C, s), 104.4 (1C, s), 48.3 (1C, s), 30.3 (1C, s), 25.6 (1C, s), 24.2 (1C, s)

### benchmark_main:R91
Molecular formula: C24H21ClN4O2S
IR bands (cm-1): [3447.0, 3328.0, 3067.0, 2925.0, 1695.0, 1624.0, 1581.0, 1546.0, 1206.0]
1H NMR: 8.09 (d, J = 7.0 Hz, 1H), 7.91-7.80 (m, 1H), 7.63 (d, J = 8.1 Hz, 1H), 7.60-7.53 (m, 3H), 7.50 (d, J = 8.1 Hz, 1H), 7.48-7.43 (m, 2H), 7.35 (d, J = 8.3 Hz, 2H), 7.24 (d, J = 8.3 Hz, 2H), 6.49 (t, J = 5.9 Hz, 1H), 6.23 (t, J = 5.6 Hz, 1H), 4.18 (d, J = 6.0 Hz, 2H), 3.44 (t, J = 6.3 Hz, 2H), 3.22 (t, J = 6.3 Hz, 2H)
13C NMR: δ 161.3 (1C, s), 158.3 (1C, s), 157.6 (1C, s), 147.8 (1C, s), 140.5 (1C, s), 136.5 (1C, s), 135.4 (1C, s), 131.5 (1C, s), 130.3 (1C, s), 130.0 (1C, s), 129.9 (1C, s), 129.3 (1C, s), 128.6 (1C, s), 127.0 (1C, s), 126.6 (1C, s), 126.4 (1C, s), 120.0 (1C, s), 42.7 (1C, s), 38.7 (1C, s)

### benchmark_main:R96
Molecular formula: C17H23N3O
IR bands (cm-1): [3470.0, 2970.0, 1644.0, 1490.0, 1092.0]
1H NMR: 7.88 (s, 1H), 7.74 (d, J = 8.4 Hz, 2H), 7.44 (d, J = 8.3 Hz, 2H), 5.77-5.70 (m, 1H), 4.06 (d, J = 11.4 Hz, 1H), 3.76 (t, J = 9.7 Hz, 1H), 2.51-2.43 (m, 1H), 2.14-2.08 (m, 2H), 1.75-1.71 (m, 2H), 1.67-1.62 (m, 1H), 1.33 (s, 9H)
13C NMR: δ 151.7 (1C, s), 148.1 (1C, s), 131.5 (1C, s), 127.3 (1C, s), 125.9 (1C, s), 125.7 (1C, s), 89.1 (1C, s), 67.5 (1C, s), 34.7 (1C, s), 31.3 (1C, s), 29.4 (1C, s), 24.8 (1C, s), 21.9 (1C, s)

### benchmark_main:R97
Molecular formula: C22H15N3O5
IR bands (cm-1): [3073.0, 1703.0, 1601.0, 1517.0, 1486.0, 1344.0, 1098.0]
1H NMR: 8.34 (dd, J = 7.0, 2.0 Hz, 2H), 8.24 (dd, J = 7.0, 2.0 Hz, 2H), 7.56 (dd, J = 7.0, 2.0 Hz, 2H), 7.48 (dd, J = 7.0, 2.0 Hz, 2H), 7.29 (dd, J = 7.5, 1.0 Hz, 1H), 6.83 (d, J = 8.0 Hz, 1H), 6.76 (td, J = 8.0, 1.0 Hz, 1H), 6.45 (d, J = 7.5, 1H), 3.20 (s, 3H) ppm
13C NMR: δ 166.0 (1C, s), 148.4 (1C, s), 148.1 (1C, s), 147.1 (1C, s), 146.3 (1C, s), 145.6 (1C, s), 144.3 (1C, s), 130.9 (1C, s), 130.6 (1C, s), 130.4 (1C, s), 127.5 (1C, s), 124.8 (1C, s), 123.63 (1C, s), 123.61 (1C, s), 122.2 (1C, s), 121.4 (1C, s), 108.7 (1C, s)
