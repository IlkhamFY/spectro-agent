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
  {"benchmark_expand_500:R177": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R177
Molecular formula: C12H14N2O6
IR bands (cm-1): [3129.0, 3074.0, 2986.0, 2939.0, 1662.0, 1637.0, 1588.0, 1529.0, 1509.0, 1341.0]
1H NMR: 1.19 (6H, t, J = 7.1 Hz, OCH2CH3), 4.19 (4H, qd, J = 7.1, 1.9 Hz, OCH2CH3), 5.41 (1H, s, ArCH(CO2Et)2), 7.77 (1H, d, J = 8.6 Hz, H-3), 8.64 (1H, dd, J = 8.6, 2.7 Hz, H-4), 9.33 (1H, d, J = 2.7 Hz, H-6)
13C NMR: δ 13.9 (1C, s), 59.2 (1C, s), 61.8 (1C, s), 125.0 (1C, s), 132.4 (1C, s), 143.7 (1C, s), 144.3 (1C, s), 158.9 (1C, s), 166.5 (1C, s)

### benchmark_expand_500:R18
Molecular formula: C17H17NO4
IR bands (cm-1): [3336.0, 3031.0, 2964.0, 2919.0, 2871.0, 2837.0, 2360.0, 2167.0, 2032.0, 1962.0, 1847.0, 1714.0, 1627.0, 1600.0, 1576.0, 1512.0, 1446.0, 1576.0]
1H NMR: 3.89 (s, 6H), 5.24 (s, 2H), 6.37 (d, 1H, Jtrans = 15.9 Hz), 6.86 (d, 1H), 7.07 (d, 1H), 7.12 (s, 1H), 7.28 (d, 2H, J = 6.3 Hz), 7.69 (d, 1H, Jtrans = 15.9 Hz), 8.59 (d, 2H, J = 6.3 Hz)
13C NMR: δ 55.9 (1C, s), 56.0 (1C, s), 64.1 (1C, s), 109.6 (1C, s), 111.0 (1C, s), 114.7 (1C, s), 121.9 (1C, s), 122.9 (1C, s), 127.1 (1C, s), 145.9 (1C, s), 149.2 (1C, s), 150.0 (1C, s), 151.4 (1C, s)

### benchmark_expand_500:R180
Molecular formula: C14H20N2O3S
IR bands (cm-1): [3328.0, 3273.0, 1694.0, 1596.0, 1539.0, 1312.0, 1147.0]
1H NMR: 0.90-1.60 (m, 10H, 5 × CH2), 2.07 (s, 3H, CH3CO), 2.86 (br s, 1H, CHN), 7.47 (d, J = 7.3 Hz, 1H, NHSO2), 7.72 (s, 4H, ArH), 10.30 (s, 1H, NHCO)
13C NMR: δ 24.1 (1C, s), 24.4 (1C, s), 24.9 (1C, s), 33.3 (1C, s), 52.1 (1C, s), 118.7 (1C, s), 127.4 (1C, s), 136.0 (1C, s), 142.5 (1C, s)

### benchmark_expand_500:R182
Molecular formula: C9H7FN2O2
IR bands (cm-1): [3013.0, 2869.0, 1755.0, 1486.0, 1157.0, 1081.0, 1020.0]
1H NMR: 10.40 (brs, 1H,CONH), 8.34 (s, 1H, ArH),7.80 (d, 2H, J = 7.6 Hz, ArH), 7.64 (d,1H, J = 7.4 Hz, ArH), 2.21 (s, 3H, ArCH3)
13C NMR: δ 164.69 (1C, s), 150.10 (1C, s), 149.88 (1C, s), 123.22 (1C, s), 122.00 (1C, s), 121.03 (1C, s), 120.33 (1C, s), 114.23 (1C, s), 22.00 (1C, s)

### benchmark_expand_500:R185
Molecular formula: C12H22O
IR bands (cm-1): [3311.0, 2923.0, 2854.0, 2360.0, 2342.0, 1465.0]
1H NMR: 4.36 (1H, td, J = 6.5, 2.0 Hz, H-3), 2.45 (1H, d, J = 2.5 Hz, H-1), 1.71 (2H, m, H2-4), 1.44 (2H, qi, J = 6.5 Hz, H2-5), 1.22-1.31 (12H, bm), 0.87 (3H, t, J = 6.5 Hz, H3-12)
13C NMR: δ 85.0 (1C, s), 72.8 (1C, s), 62.3 (1C, s), 37.6 (1C, s), 31.9 (1C, s), 29.5 (1C, s), 29.3 (1C, s), 29.2 (1C, s), 25.0 (1C, s), 22.6 (1C, s)

### benchmark_expand_500:R187
Molecular formula: C8H17BrO
IR bands (cm-1): [720.0, 830.0, 1050.0, 1075.0, 1125.0, 1225.0, 1265.0, 1385.0, 1425.0, 1470.0, 2860.0, 2935.0, 2970.0, 3380.0]
1H NMR: 0.89 (t, 3 H, J = 6.5 Hz), 1.25-1.63 (m, 8 H), 1.86 (q, 2 H, J = 7.1 Hz), 2.22 (s, 1 H), 3.42 (d, 2 H, J = 7.1 Hz), 3.75-3.84 (m, 1 H)
13C NMR: δ 14.01 (1C, s), 22.52 (1C, s), 25.58 (1C, s), 29.14 (1C, s), 31.68 (1C, s), 35.05 (1C, s), 40.73 (1C, s), 71.02 (1C, s)
