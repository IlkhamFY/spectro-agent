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
  {"benchmark_main:R55": ["CCO", "COC"]}

Compounds:

### benchmark_main:R55
Molecular formula: C9H11NO4S
IR bands (cm-1): [3448.0, 3277.0, 2957.0, 1730.0, 1598.0, 1440.0, 1354.0, 1321.0, 1185.0, 1111.0, 1094.0]
1H NMR: 7.89 (t, J = 6.3 Hz, 1H, NH), 7.64 (d, J = 8.6 Hz, 2H, ArH), 7.33 (d, J = 8.05 Hz, 2H, ArH), 3.51 (d, J = 5.7 Hz, CH2), 2.34 (s, 3H, CH3)
13C NMR: δ 170.8 (1C, s), 143.1 (1C, s), 138.4 (1C, s), 130.0 (1C, s), 127.1 (1C, s), 44.3 (1C, s), 21.5 (1C, s)

### benchmark_main:R56
Molecular formula: C7H18Sn
IR bands (cm-1): [2956.0, 2872.0, 2896.0, 2229.0, 2116.0, 1464.0, 1457.0, 1412.0, 1377.0, 1292.0, 1250.0, 1151.0, 919.0, 873.0, 661.0]
1H NMR: 0.82 (m, 2H, CH3-CH2-CH2-CH2-Sn), 0.89 (t, J = 7.27 Hz, 3H, CH3-CH2-CH2-CH2-Sn), 1.30 (m, 2H, CH2), 1.48 (m, 2H, CH2)
13C NMR: δ 10.76 (1C, s), 13.85 (1C, s), 27.14 (1C, s), 29.13 (1C, s)

### benchmark_main:R58
Molecular formula: C17H26OSi
IR bands (cm-1): [3033.0, 2952.0, 1644.0, 1011.0, 730.0]
1H NMR: 7.22 (m, 2 H), 7.12 (m, 1 H), 7.06 (m, 2 H), 2.73 (dd, A of ABX system, J = 6.6, 17.4 Hz, 1 H), 2.56 (dd, B of ABX system, J = 7.2, 16.8 Hz, 1 H), 1.62 (dt, J = 4.8, 9.0 Hz, 1 H), 1.33 (m, 1 H), 0.96 (m, heavily overlapped, 1 H), 0.96 (t, J = 7.8 Hz, 9 H), 0.73 (m, heavily overlapped, 1 H), 0.73 (q, J = 7.8 Hz, 6 H)
13C NMR: δ 247.0 (1C, s), 142.9 (1C, s), 128.2 (1C, s), 125.9 (1C, s), 125.4 (1C, s), 54.8 (1C, s), 22.6 (1C, s), 16.5 (1C, s), 15.7 (1C, s), -7.2 (1C, s), -2.1 (1C, s)

### benchmark_main:R60
Molecular formula: C9H16O
IR bands (cm-1): [2927.0, 2854.0, 1449.0, 821.0]
1H NMR: 2.60 (d, J = 4.9 Hz, 1H), 2.53 (d, J = 4.9 Hz, 1H), 1.81-1.68 (m, 5H), 1.23 (s, 3H), 1.21-1.03 (m, 6H)
13C NMR: δ 59.9 (1C, s), 53.6 (1C, s), 44.5 (1C, s), 28.9 (1C, s), 28.5 (1C, s), 26.4 (1C, s), 26.2 (1C, s), 26.1 (1C, s), 18.0 (1C, s)

### benchmark_main:R62
Molecular formula: C13H10BrN3O2S
IR bands (cm-1): [3337.0, 3191.0, 1655.0, 1586.0, 1468.0, 1331.0, 785.0]
1H NMR: 11.78 (s, 1H, NH), 11.30 (s, 1H, NH), 8.72 (s, 1H, H-2), 8.60 (s, 1H, H-6), 7.62 (s, 1H, H-4), 6.88-6.85 (m, 1H, H-5′), 6.76-6.73 (m, 1H, H-4′), 6.62 (d, J = 2.0 Hz, 1H, H-2′), 6.42 (t, J = 7.5 Hz, 1H, H-6′), 3.66 (br. s, 1H, OH)
13C NMR: δ 179.5 (1C, s), 169.3 (1C, s), 140.3 (1C, s), 140.1 (1C, s), 139.4 (1C, s), 134.3 (1C, s), 131.2 (1C, s), 128.9 (1C, s), 127.5 (1C, s), 125.7 (1C, s), 125.3 (1C, s), 123.6 (1C, s), 123.4 (1C, s)

### benchmark_main:R63
Molecular formula: C11H12N2O2S2
IR bands (cm-1): [3070.0, 2863.0, 1600.0, 1458.0, 1412.0, 1314.0, 1258.0, 1146.0, 1093.0, 1072.0, 812.0, 730.0, 662.0]
1H NMR: 8.68 (d, J = 2.0 Hz, 1H), 7.67 (m, 2H), 7.23 (dd, J1 = 8.6 Hz, J2 = 0.8 Hz, 2H), 7.09 (m, 1H), 5.65 (bt, J = 6.3 Hz, 1H), 4.32 (d, J = 6.3 Hz, 2H), and 2.39 (s, 3H) ppm
13C NMR: δ 153.6 (1C, s), 152.3 (1C, s), 143.4 (1C, s), 136.9 (1C, s), 129.6 (1C, s), 127.1 (1C, s), 115.7 (1C, s), 42.9 (1C, s)
