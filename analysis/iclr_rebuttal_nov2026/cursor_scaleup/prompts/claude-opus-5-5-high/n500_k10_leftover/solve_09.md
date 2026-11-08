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
  {"benchmark_expand:R87": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R87
Molecular formula: C22H22ClN5O
IR bands (cm-1): [3345.0, 2901.0, 1662.0, 1627.0, 1583.0, 1480.0, 1430.0, 1391.0, 1348.0, 1310.0, 1243.0, 1108.0, 952.0, 788.0, 638.0]
1H NMR: 1.73 (m, 6H, CH2(Ad)), 1.99 (m, 6H, CH2(Ad)), 2.04 (m, 3H, CH(Ad)), 7.21 (d, 1H, J = 7.65 Hz, Ph), 7.43 (t, 1H, J = 7.90 Hz, Ph), 7.91 (d, 1H, J = 6.55 Hz, Ph), 8.32 (s, 1H, Ph), 8.34 (s, 1H, C8H), 10.35 (s, 1H, C6NHPh), 13.35 (s, 1H, N9H) ppm
13C NMR: δ 27.5 (1C, s), 35.9 (1C, s), 38.5 (1C, s), 46.1 (1C, s), 119.2 (1C, s), 122.1 (1C, s), 122.6 (1C, s), 128.6 (1C, s), 138.3 (1C, s), 138.9 (1C, s), 152.0 (1C, s)

### benchmark_expand:R88
Molecular formula: C19H22N2O5
IR bands (cm-1): [3408.0, 3075.0, 2979.0, 1751.0, 1593.0, 1513.0, 1328.0, 1209.0, 1079.0]
1H NMR: 8.25 (d, J = 2.7 Hz, 1H, Ar), 8.10 (dd, J = 2.7, 9.0 Hz, 1H, Ar), 7.20-7.14 (m, 2H, Ar), 6.76 (d, J = 9.1 Hz, 1H, Ar), 6.72 (t, J = 7.3 Hz, 1H, Ar), 6.67-6.62 (m, 2H, Ar), 4.872 (dd, J = 7.2, 5.0 Hz, 1H, CH), 4.50 (d, J = 16.0 Hz, 1H, CHH), 4.41 (d, J = 16.0 Hz, 2H; 1H, CHH, 1H NH: D2O exchangeable), 3.77 (s, 3H, OCH3), 2.11-1.94 (m, 2H, CH2), 1.56 (sext, J = 7.5 Hz, 2H, CH2), 0.99 (t, J = 7.4 Hz, 3H, CH3)
13C NMR: δ 171.0 (1C, s), 160.3 (1C, s), 147.7 (1C, s), 142.00 (1C, s), 129.9 (1C, s), 129.3 (1C, s), 124.5 (1C, s), 117.9 (1C, s), 113.1 (1C, s), 110.9 (1C, s), 76.5 (1C, s), 52.2 (1C, s), 43.1 (1C, s), 34.5 (1C, s), 18.5 (1C, s)

### benchmark_expand:R92
Molecular formula: C24H28N2O
IR bands (cm-1): [3435.0, 3052.0, 2932.0, 2796.0, 1604.0, 1553.0, 1451.0, 1384.0, 1263.0, 1173.0, 1028.0]
1H NMR: 7.58 (s, 1H), 7.58-7.51 (m, 2H), 7.34-7.25 (m, 1H), 7.18 (s, 2H), 7.17 (s, 2H), 7.13-7.08 (m, 1H), 7.04-6.97 (m, 2H), 3.80 (d, J = 6.7 Hz, 2H), 3.78 (s, 3H), 3.36 (s, 2H), 2.84-2.66 (m, 2H), 2.48-2.36 (m, 1H), 1.94-1.83 (m, 2H), 1.83-1.72 (m, 2H), 1.41-1.32 (m, 2H)
13C NMR: δ 157.46 (1C, s), 138.42 (1C, s), 135.71 (1C, s), 133.70 (1C, s), 129.20 (1C, s), 128.91 (1C, s), 128.20 (1C, s), 127.17 (1C, s), 126.99 (1C, s), 126.35 (1C, s), 118.81 (1C, s), 105.67 (1C, s), 63.09 (1C, s), 55.32 (1C, s), 54.18 (1C, s), 52.37 (1C, s), 50.82 (1C, s), 32.63 (1C, s)

### benchmark_expand:R94
Molecular formula: C17H13N3O2S
IR bands (cm-1): [3450.0, 2923.0, 2852.0, 1607.0, 1554.0, 1468.0, 1382.0, 1235.0, 1152.0, 861.0, 785.0, 739.0, 689.0]
1H NMR: 4.27 (s, 2H, CH2), 6.70 (d, 2H, Ar-H, J = 8.8 Hz), 7.07 (s, 1H, =C-H), 7.19-7.23 (m, 1H, Ar-H), 7.29-7.31 (m, 1H, Ar-H), 7.34 (d, 2H, Ar-H, J = 8.8 Hz), 7.68 (d, 1H, Ar-H, J = 8.2 Hz), 7.85 (d, 1H, Ar-H, J = 8.2 Hz), 9.24 (s, 1H, -OH), 10.20 (s, 1H, N-H)
13C NMR: δ 165.12 (1C, s), 155.44 (1C, s), 153.78 (1C, s), 141.76 (1C, s), 130.39 (1C, s), 129.64 (1C, s), 128.52 (1C, s), 124.86 (1C, s), 122.28 (1C, s), 121.27 (1C, s), 116.57 (1C, s), 115.22 (1C, s), 112.67 (1C, s), 111.99 (1C, s), 34.99 (1C, s)

### benchmark_expand:R97
Molecular formula: C33H27N9O8
IR bands (cm-1): [3240.0, 3030.0, 2975.0, 1661.0, 1575.0, 1372.0]
1H NMR: 11.67 (s, 1H, NH), 10.48 (s, 1H, NH), 8.73-8.70 (m, 2H, Ar), 8.27 (s, 1H, Ar), 8.22 (d, J = 7.1 Hz, 1H, Ar), 7.95 (d, J = 9.6 Hz, 1H, Ar), 7.52 (m, 2H, Ar), 7.39 (m, 2H, Ar), 7.16-7.11 (m, 3H, Ar), 7.04 (m, 3H, Ar), 5.32 (s, 2H, CH2), 5.16 (s, 2H, CH2), 3.88 (s, 3H, OCH3), 2.21 (s, 3H, CH3)
13C NMR: δ 163.7 (1C, s), 161.0 (1C, s), 152.8 (1C, s), 152.6 (1C, s), 152.5 (1C, s), 146.3 (1C, s), 145.1 (1C, s), 142.7 (1C, s), 135.8 (1C, s), 132.6 (1C, s), 129.8 (1C, s), 129.7 (1C, s), 129.6 (1C, s), 129.1 (1C, s), 129.0 (1C, s), 128.9 (1C, s), 128.1 (1C, s), 127.9 (1C, s), 126.3 (1C, s), 125.6 (1C, s), 125.0 (1C, s), 124.5 (1C, s), 123.1 (1C, s), 119.1 (1C, s), 117.3 (1C, s), 116.7 (1C, s), 114.4 (1C, s), 66.1 (1C, s), 55.8 (1C, s), 52.1 (1C, s), 20.3 (1C, s)

### benchmark_expand_500:R03
Molecular formula: C34H27BrN2O6
IR bands (cm-1): [3854.0, 3729.0, 3668.0, 3633.0, 1740.0, 1712.0, 1617.0, 1498.0, 1376.0, 1232.0, 1180.0, 1004.0, 858.0, 804.0, 736.0, 620.0]
1H NMR: 8.62 (s, 1H), 7.82 (d, J = 7.6 Hz, 1H), 7.66 (d, J = 8.8 Hz, 2H), 7.62 (d, J = 8.8 Hz, 2H), 7.40 (t, J = 7.8 Hz, 1H), 7.32 (ψt, J = 7.6 Hz, 1H), 7.28 (ψt, J = 7.6 Hz, 1H), 7.13 (ψt, J = 8.4 Hz, 2H), 7.05 (t, J = 7.4 Hz, 2H), 6.90 (ψt, J = 7.0 Hz, 1H), 6.69 (d, J = 7.6 Hz, 1H), 6.52 (d, J = 6.8 Hz, 2H), 6.38 (d, J = 7.6 Hz, 1H), 5.72 (s, 1H), 4.87 (d, J = 16.2 Hz, 1H), 4.65 (s, 1H), 4.51 (d, J = 16.2 Hz, 1H), 3.64 (q, J = 7.0 Hz, 2H), 0.70 (t, J = 7.1 Hz, 3H)
13C NMR: δ 175.0 (1C, s), 167.2 (1C, s), 164.7 (1C, s), 150.8 (1C, s), 144.1 (1C, s), 137.6 (1C, s), 135.7 (1C, s), 131.2 (1C, s), 131.0 (1C, s), 130.7 (1C, s), 128.9 (1C, s), 128.4 (1C, s), 127.5 (1C, s), 126.7 (1C, s), 126.2 (1C, s), 125.0 (1C, s), 124.9 (1C, s), 123.7 (1C, s), 121.4 (1C, s), 117.5 (1C, s), 115.0 (1C, s), 109.9 (1C, s), 77.3 (1C, s), 71.8 (1C, s), 63.1 (1C, s), 59.1 (1C, s), 47.1 (1C, s), 42.7 (1C, s)
