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
  {"benchmark_expand:R62": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R62
Molecular formula: C21H15Cl2NO
IR bands (cm-1): [3374.0, 3060.0, 2925.0, 1683.0]
1H NMR: 8.28 (s, 1H, C3-H), 7.95 (s, 1H, C1-H), 7.59 (s, 1H, C10-H), 7.44 (d, J = 6.5 Hz, 1H, C7-H), 7.33-7.30 (m, 2H, C18-H), 6.87 (d, J = 6.5 Hz, 1H, C8-H), 6.66 (s, 1H, NH), 7.56-7.54 (m, 3H, C17-H, C19-H), 4.05 (s, 2H, C15-H), 3.98 (s, 2H, C12-H)
13C NMR: δ 162.7 (1C, s), 160.0 (1C, s), 146.7 (1C, s), 139.0 (1C, s), 138.7 (1C, s), 137.3 (1C, s), 136.9 (1C, s), 135.5 (1C, s), 129.3 (1C, s), 128.5 (1C, s), 127.2 (1C, s), 124.0 (1C, s), 120.8 (1C, s), 119.5 (1C, s), 117.9 (1C, s), 116.0 (1C, s), 114.3 (1C, s), 49.8 (1C, s), 36.7 (1C, s)

### benchmark_expand:R63
Molecular formula: C19H15ClO2Se
IR bands (cm-1): [3381.0, 3057.0, 2936.0, 1618.0, 1511.0, 1577.0, 1463.0]
1H NMR: 7.78 (d, J = 8.8 Hz, 1H), 7.70 (d, J = 8.8 Hz, 1H), 7.62 (d, J = 2.6 Hz, 1H), 7.23-7.15 (m, 2H), 7.07-7.00 (m, 2H), 6.96 (dd, J = 3.0, 1.3 Hz, 1H), 6.89 (s, 1H), 6.66 (d, J = 15.6 Hz, 1H), 6.58-6.49 (m, 1H), 3.92 (s, 3H)
13C NMR: δ 159.60 (1C, s), 156.56 (1C, s), 139.19 (1C, s), 137.51 (1C, s), 132.37 (1C, s), 130.27 (1C, s), 128.05 (1C, s), 126.29 (1C, s), 124.72 (1C, s), 124.69 (1C, s), 121.84 (1C, s), 116.73 (1C, s), 116.05 (1C, s), 114.07 (1C, s), 107.14 (1C, s), 106.19 (1C, s), 55.52 (1C, s)

### benchmark_expand:R65
Molecular formula: C25H22N2OS
IR bands (cm-1): [3175.0, 3070.0, 3032.0, 2597.0, 1714.0, 1624.0]
1H NMR: 9.47(s,1H), 9.26(s,1H), 7.97-7.94(dd, J = 7.33 Hz, J = 7.37 Hz, 2H, Ar-ring), 7.86-7.84(dd, J = 7.31 Hz, J = 7.35 Hz, 2H,), 7.63-7.59(d, 1H, J = 6.21 Hz, Ar-ring), 7.53-7.51(2H, dd, J = 7.31 Hz, J = 7.35 Hz Ph), 7.50-7.44(3H, m, Ar-ring), 7.40-7.37(dd, J = 7.33 Hz, J = 7.37 Hz, 2H, Ar ring), 7.35-7.32(d, J = 6.21 Hz, 1H, Ar ring), 7.26-7.24(dd, J = 7.31 Hz, J = 7.35 Hz, 2H, Ar ring), 6.56-6.54(d, J = 6.20 Hz, 1H), 6.19-6.17(d, J = 6.21 Hz, 1H), 3.84-3.82(m, 1H), 2.94-2.92(d, J = 6.21 Hz, 2H)
13C NMR: δ 197.4 (1C, s), 182.0 (1C, s), 136.7 (1C, s), 133.1 (1C, s), 128.8 (1C, s), 128.6 (1C, s), 136.4 (1C, s), 128.6 (1C, s), 128.5 (1C, s), 127.9 (1C, s), 135.2 (1C, s), 134.4 (1C, s), 116.1 (1C, s), 20.6 (1C, s), 134.6 (1C, s), 128.1 (1C, s), 55.6 (1C, s), 50.1 (1C, s)

### benchmark_expand:R68
Molecular formula: C24H18N2O
IR bands (cm-1): [2922.0, 1590.0, 1500.0, 1452.0, 1384.0, 1214.0, 1122.0, 744.0]
1H NMR: 8.14 (d, J = 8.0 Hz, 1H), 7.99 (m, 1H), 7.79 (d, J = 7.6 Hz, 1H), 7.41 (m, 1H), 7.33 (m, 1H), 7.12 (td, J = 8.0, 1.6 Hz, 1H), 7.05 (m, 2H), 7.00 (dd, J = 8.4, 1.2 Hz, 1H), 6.78 (m, 1H), 6.69 (td, J = 7.2, 1.2 Hz, 1H), 6.63 (s, 1H), 6.61 (s, 1H), 6.47 (dd, J = 7.6, 1.6 Hz, 1H), 6.41 (d, J = 1.2 Hz, 1H), 1.88 (d, J = 1.2 Hz, 3H)
13C NMR: δ 155.8 (1C, s), 134.7 (1C, s), 134.4 (1C, s), 134.3 (1C, s), 133.9 (1C, s), 131.9 (1C, s), 129.7 (1C, s), 129.3 (1C, s), 129.0 (1C, s), 127.1 (1C, s), 124.6 (1C, s), 122.8 (1C, s), 121.5 (1C, s), 121.4 (1C, s), 121.0 (1C, s), 120.9 (1C, s), 119.9 (1C, s), 118.2 (1C, s), 117.1 (1C, s), 112.0 (1C, s), 100.2 (1C, s), 58.4 (1C, s), 22.9 (1C, s), 17.3 (1C, s)

### benchmark_expand:R71
Molecular formula: C18H15N3O3
IR bands (cm-1): [3060.0, 1698.0, 1617.0, 1542.0, 1440.0, 1382.0, 1288.0, 1230.0, 1120.0, 956.0]
1H NMR: 9.86 (brs, 1H), 7.73 (dt, J = 8.4, 0.8 Hz, 1H), 7.52-7.46 (m, 3H), 7.42-7.38 (m, 2H), 7.24 (d, J = 8.4 Hz, 1H), 7.14 (ddd, J = 9.2, 7.2, 0.8 Hz, 1H), 4.28 (q, J = 5.6 Hz, 1H), 3.06 (dd, J = 17.6, 9.6 Hz, 1H), 2.74 (dd, J = 18.0, 5.6 Hz, 1H), 2.71 (s, 3H)
13C NMR: δ 178.2 (1C, s), 176.5 (1C, s), 156.9 (1C, s), 143.3 (1C, s), 139.6 (1C, s), 137.4 (1C, s), 131.4 (1C, s), 129.4 (1C, s), 129.3 (1C, s), 128.8 (1C, s), 128.3 (1C, s), 121.0 (1C, s), 120.8 (1C, s), 114.6 (1C, s), 111.0 (1C, s), 44.1 (1C, s), 38.6 (1C, s), 24.8 (1C, s)

### benchmark_expand:R73
Molecular formula: C22H13F3N2O2
IR bands (cm-1): [3071.0, 1767.0, 1667.0, 1604.0]
1H NMR: 9.85 (d, J = 6.8 Hz, 1H), 7.88 (d, J = 9.2 Hz, 1H), 7.73-7.66 (m, 3H), 7.60 (t, J = 7.6 Hz, 1H), 7.41-7.35 (m, 6H), 7.31-7.28 (m, 1H)
13C NMR: δ 191.6 (1C, s), 184.3 (1C, s), 156.8 (1C, s), 148.3 (1C, s), 136.4 (1C, s), 134.5 (1C, s), 133.0 (1C, s), 131.3 (1C, q), 131.29 (1C, s), 129.4 (1C, s), 129.3 (1C, s), 128.7 (1C, s), 124.7 (1C, q), 123.8 (1C, q), 119.1 (1C, s), 117.8 (1C, s), 116.2 (1C, s)
