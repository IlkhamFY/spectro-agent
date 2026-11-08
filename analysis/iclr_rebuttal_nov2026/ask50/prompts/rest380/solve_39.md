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
  {"benchmark_expand:R103": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R103
Molecular formula: C13H9NO3
IR bands (cm-1): [3119.0, 2926.0, 2849.0, 2692.0, 2579.0, 2228.0, 1726.0, 1682.0, 1584.0, 1520.0, 1422.0, 1299.0, 1169.0, 1029.0, 858.0, 810.0, 760.0]
1H NMR: 13.20 (broad s exch D2O, 1H, COOH), 8.08-8.02 (m, 1H, H7), 7.93-7.88 (m, 1H, H11), 7.67-7.62 (m, 1H, H9), 7.33 (d, J = 3.6 Hz, 1H, H3), 7.28 (d, J = 3.6 Hz, 1H, H4), 2.39 (s, 3H, CH3) ppm
13C NMR: δ 159.56 (1C, s), 154.49 (1C, s), 145.39 (1C, s), 140.84 (1C, s), 132.82 (1C, s), 130.66 (1C, s), 129.51 (1C, s), 125.61 (1C, s), 120.13 (1C, s), 118.82 (1C, s), 112.64 (1C, s), 110.06 (1C, s)

### benchmark_expand:R104
Molecular formula: C14H9FO3
IR bands (cm-1): [1685.0, 1611.0, 1598.0, 1577.0, 1396.0, 787.0]
1H NMR: 6.73 (d, J = 8.3 Hz, 1H), 6.99 (m, 2H), 7.33 (t, J = 7.5 Hz, 1H), 7.54 (m, 1H), 7.62 (ddd, J = 8.3, 7.5, 1.5 Hz, 1H), 7.99 (dd, J = 7.5, 1.5 Hz, 1H), 10.44 (s, 1H), 10.51 (s, 1H), 10.43 (s, 1H)
13C NMR: δ 112.5 (1C, s), 112.7 (1C, s), 115.0 (1C, s), 115.1 (1C, s), 119.7 (1C, s), 125.3 (1C, s), 127.7 (1C, s), 129.8 (1C, s), 136.4 (1C, s), 136.5 (1C, s), 158.5 (1C, s), 159.0 (1C, s), 186.2 (1C, s), 188.9 (1C, s)

### benchmark_expand:R105
Molecular formula: C8H10INO2S
IR bands (cm-1): [3097.0, 3041.0, 3013.0, 2968.0, 2928.0, 2832.0, 1589.0, 1477.0, 1280.0, 1192.0, 1065.0, 990.0, 958.0, 760.0]
1H NMR: 7.95 (dd, J = 8.0, 1.8 Hz, 1H), 7.63 (ddd, J = 8.4, 7.5, 1.8 Hz, 1H), 7.15 (ddd, J = 8.0, 7.5, 1.0 Hz, 1H), 7.07 (dd, J = 8.4, 1.0 Hz, 1H), 3.99 (s, 3H), 3.49 (s, 3H). 13C{1H} NMR (126 MHz, CDCl3): δ 156.9, 135.7, 131.7, 127.3, 120.9, 112.8, 56.7, 41.0
13C NMR: δ 156.9 (1C, s), 135.7 (1C, s), 131.7 (1C, s), 127.3 (1C, s), 120.9 (1C, s), 112.8 (1C, s), 56.7 (1C, s), 41.0 (1C, s)

### benchmark_expand:R106
Molecular formula: C17H23NO4
IR bands (cm-1): [3404.0, 2942.0, 2648.0, 2536.0, 1697.0, 1597.0, 1511.0, 1455.0, 1258.0, 1138.0]
1H NMR: 7.35 (d, J = 15.9 Hz, 1H), 7.17 (d, J = 1.9 Hz, 1H), 7.06 (dd, J = 8.3, 1.9 Hz, 1H), 6.98 (d, J = 8.3 Hz, 1H), 6.37 (d, J = 15.9 Hz, 1H), 4.33 (t, J = 5.1 Hz, 2H), 3.89 (s, 3H), 3.41 (t, J = 5.1 Hz, 2H), 3.29-3.17 (m, 4H), 1.90-1.78 (m, 4H), 1.71-1.60 (m, 2H) (signal for RCO2H was not detected)
13C NMR: δ 169.1 (1C, s), 149.8 (1C, s), 148.9 (1C, s), 144.5 (1C, s), 129.4 (1C, s), 122.1 (1C, s), 116.7 (1C, s), 114.3 (1C, s), 110.5 (1C, s), 63.3 (1C, s), 55.8 (1C, s), 55.2 (1C, s), 53.6 (1C, s), 22.8 (1C, s), 21.2 (1C, s)

### benchmark_expand:R12
Molecular formula: C19H27NO2
IR bands (cm-1): [2935.0, 2858.0, 1641.0, 1425.0, 1362.0]
1H NMR: 7.33-7.23 (m, 5H), 5.70-5.60 (m, 2H), 5.39 (bs), 3.60 (d, 1H, J = 9.0 Hz), 4.48 (m, 3H), 4.01 (d, 2H, J = 3.2 Hz), 3.09 (t, J = 12.3 Hz), 2.58 (t, 1H, J = 12.3 Hz), 2.31-2.21 (m, 2H), 1.79-1.76 (m, 1H), 1.67-1.58 (m, 6H), 1.36 (m, 1H), 0.93 (t, 3H, J = 7.2 Hz)
13C NMR: δ 176.6 (1C, s), 172.3 (1C, s), 171.8 (1C, s), 138.1 (1C, s), 137.9 (1C, s), 131.4 (1C, s), 130.9 (1C, s), 128.3 (1C, s), 127.7 (1C, s), 127.6 (1C, s), 72.2 (1C, s), 71.9 (1C, s), 70.3 (1C, s), 69.9 (1C, s), 53.6 (1C, s), 48.7 (1C, s), 41.8 (1C, s), 37.2 (1C, s), 35.8 (1C, s), 35.5 (1C, s), 35.1 (1C, s), 30.2 (1C, s), 28.6 (1C, s), 26.2 (1C, s), 25.2 (1C, s), 19.6 (1C, s), 19.4 (1C, s), 18.8 (1C, s), 18.6 (1C, s), 18.2 (1C, s), 13.9 (1C, s), 13.5 (1C, s)

### benchmark_expand:R15
Molecular formula: C14H15N3O2S
IR bands (cm-1): [3635.0, 3019.0, 2959.0, 1731.0, 1535.0, 1442.0, 1359.0]
1H NMR: 12.53 (s, 1H), 7.67 (dd, J = 8.2, 1.3 Hz, 1H), 7.37-7.32 (m, 1H), 6.96-6.89 (m, 2H), 5.88 (ddt, J = 17.2, 10.2, 5.5 Hz, 1H), 5.24 (dq, J = 17.2, 1.6 Hz, 1H), 5.21 (dt, J = 10.3, 1.5 Hz, 1H), 4.37 (dt, J = 5.4, 1.5 Hz, 2H), 4.13 (s, 2H), 2.54 (s, 3H)
13C NMR: δ 171.5 (1C, s), 167.2 (1C, s), 161.5 (1C, s), 159.1 (1C, s), 132.0 (1C, s), 131.1 (1C, s), 129.3 (1C, s), 119.1 (1C, s), 119.0 (1C, s), 117.7 (1C, s), 117.1 (1C, s), 44.9 (1C, s), 32.7 (1C, s), 14.4 (1C, s)
