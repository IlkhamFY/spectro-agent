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
  {"benchmark_main:R57": ["CCO", "COC"]}

Compounds:

### benchmark_main:R57
Molecular formula: C17H10ClN3O4
IR bands (cm-1): [3409.0, 3067.0, 2915.0, 1738.0, 1635.0, 1590.0, 1464.0, 1398.0, 1311.0, 1246.0, 1163.0, 1079.0, 857.0, 793.0, 744.0, 529.0, 468.0]
1H NMR: 14.84 (s, 1H), 10.81 (s, 1H), 8.54 (s, 1H), 8.05 (s, 1H), 7.89 (d, J = 8.0 Hz, 1H), 7.62 (t, J = 8.0 Hz, 1H), 7.40 (t, J = 8.0 Hz, 1H), 7.12-7.38 (m, 3H)
13C NMR: δ 193.01 (1C, s), 168.12 (1C, s), 163.20 (1C, s), 154.16 (1C, s), 142.11 (1C, s), 140.02 (1C, s), 135.81 (1C, s), 132.23 (1C, s), 130.29 (1C, s), 129.65 (1C, s), 128.11 (1C, s), 127.56 (1C, s), 126.34 (1C, s), 123.12 (1C, s), 116.71 (1C, s)

### benchmark_main:R59
Molecular formula: C25H25NO2
IR bands (cm-1): [3329.0, 3064.0, 2957.0, 2923.0, 1672.0, 1605.0, 1560.0, 1442.0, 1374.0, 1208.0, 1093.0]
1H NMR: 0.84 (t, J = 6.9 Hz, 3H), 1.26-1.33 (m, 4H), 1.40 (quin, J = 6.9 Hz, 2H), 1.72 (quin, J = 7.2 Hz, 2H), 3.25 (t, J = 7.2 Hz, 2H), 6.89 (s, 1H), 7.20-7.26 (m, 2H), 7.35-7.47 (m, 5H), 7.62 (td, J = 6.6, 1.2 Hz, 2H), 8.00 (dd, J = 8.1, 1.5 Hz, 1H), 8.60 (brs, 1H)
13C NMR: δ 14.1 (1C, s), 22.6 (1C, s), 26.9 (1C, s), 28.9 (1C, s), 31.6 (1C, s), 43.2 (1C, s), 101.8 (1C, s), 106.4 (1C, s), 108.4 (1C, s), 117.2 (1C, s), 118.8 (1C, s), 123.2 (1C, s), 124.2 (1C, s), 127.4 (1C, s), 128.5 (1C, s), 128.9 (1C, s), 130.0 (1C, s), 136.5 (1C, s), 140.9 (1C, s), 148.5 (1C, s), 151.1 (1C, s), 152.4 (1C, s), 163.2 (1C, s)

### benchmark_main:R61
Molecular formula: C34H28N4O4S
IR bands (cm-1): [3413.0, 3373.0, 3058.0, 2922.0, 1702.0, 1698.0, 1622.0, 1597.0, 1494.0, 1457.0, 1353.0, 1319.0, 1185.0, 1157.0, 1091.0, 1011.0]
1H NMR: 10.74 (s, 1H, NH of indole), 8.40 (s, 1H, ArH), 8.08 (d, J = 8.24 Hz, 1H, ArH), 7.91 (d, J = 6.88 Hz, 1H, ArH), 7.72 (d, J = 8.28 Hz, 1H, ArH), 7.56 (m, 1H, ArH), 7.44 (m, 3H, ArH), 7.26 (m, 5H, ArH), 7.11 (m, 4H, ArH), 7.01 (m, 2H, ArH), 6.87 (t, J = 7.32 Hz, 1H, ArH), 3.83 (m, 1H, CH-C = O), 3.01 (dd, J = 6.44, 6.40 Hz, 1H, CHa of CH2), 2.79 (dd, J = 7.80, 7.76 Hz, 1H, CHb of CH2), 2.26 (m, 3H, CH3)
13C NMR: δ 173.2 (1C, s), 163.9 (1C, s), 143.9 (1C, s), 142.9 (1C, s), 142.7 (1C, s), 141.5 (1C, s), 138.5 (1C, s), 136.6 (1C, s), 129.9 (1C, s), 129.8 (1C, s), 129.6 (1C, s), 129.4 (1C, s), 129.0 (1C, s), 128.7 (1C, s), 127.4 (1C, s), 126.9 (1C, s), 126.8 (1C, s), 126.1 (1C, s), 125.8 (1C, s), 124.5 (1C, s), 124.4 (1C, s), 121.3 (1C, s), 118.8 (1C, s), 118.3 (1C, s), 111.9 (1C, s), 111.8 (1C, s), 109.4 (1C, s), 57.1 (1C, s), 28.8 (1C, s), 21.5 (1C, s)

### benchmark_main:R68
Molecular formula: C19H18O2
IR bands (cm-1): [2937.0, 1705.0, 1587.0, 1493.0, 1280.0, 1041.0, 702.0]
1H NMR: 7.35 (d, 1H, J = 7.3 Hz, ArH), 7.19 (dd, 2H, J = 7.8 and 7.3 Hz, ArH), 7.12 (t, 1H, J = 7.3 Hz, ArH), 6.90-6.80 (m, 3H, ArH), 3.94 (s, 3H, ArOCH3), 2.97 (d, 1H, J = 17.1 Hz, CHaHbCO), 2.86 (d, 1H, J = 17.1 Hz, CHaHbCO), 2.72-2.62 (m, 2H, CH2), 2.62-2.52 (m, 1H, CHaHb), 1.85-1.72 (m, 2H, CH2), 1.60-1.45 (m, 1H, CHaHb) ppm
13C NMR: δ 202.2 (1C, s), 158.4 (1C, s), 155.4 (1C, s), 147.0 (1C, s), 135.5 (1C, d), 128.2 (1C, d), 127.8 (1C, s), 127.0 (1C, d), 126.1 (1C, d), 123.2 (1C, s), 110.4 (1C, d), 56.6 (1C, t), 55.8 (1C, q), 46.8 (1C, s), 34.9 (1C, t), 24.1 (1C, t)

### benchmark_main:R71
Molecular formula: C30H28N4O8Sn
IR bands (cm-1): [3464.0, 3144.0, 3053.0, 2980.0, 2936.0, 2874.0, 1628.0, 1595.0, 1580.0, 1504.0, 1481.0, 1470.0, 1431.0, 1408.0, 1368.0, 1327.0, 1263.0, 1225.0, 1198.0, 1144.0, 1105.0, 1061.0, 1009.0, 972.0, 899.0, 883.0, 835.0, 802.0, 764.0, 735.0, 694.0, 669.0, 600.0, 581.0, 544.0, 507.0, 453.0, 424.0]
1H NMR: 7.79-7.81 (m, 4H, Ar-H), 7.69-7.70 (m, 1H, Ar-H), 7.45-7.50 (m, 6H, Ar-H), 7.42 (dd, J1 = 3.5 Hz, J2 = 0.7 Hz, 1H, Ar-H), 6.62 (q, J = 1.7 Hz, 1H, Ar-H), 3.09 (q, J = 7.6 Hz, 2H, -CH2CH3), 1.29 (t, J = 7.6 Hz, 3H, -CH2CH3)
13C NMR: δ 167.24 (1C, s), 163.10 (1C, s), 160.19 (1C, s), 147.15 (1C, s), 146.58 (1C, s), 136.13 (1C, s), 135.47 (1C, s), 131.50 (1C, s), 129.43 (1C, s), 117.58 (1C, s), 112.30 (1C, s), 21.25 (1C, s), 10.81 (1C, s)

### benchmark_main:R72
Molecular formula: C28H23NO3SSe
IR bands (cm-1): [3238.0, 3101.0, 1638.0, 1571.0, 1455.0, 1231.0, 826.0, 738.0]
1H NMR: 2.34 (s, 3H), 3.86 (s, 3H), 6.91-6.94 (m, 4H), 7.04 (t, J = 7.2 Hz, 2H), 7.09 (d, J = 8.1 Hz, 3H), 7.24-7.32 (m, 5H), 7.41 (t, J = 7.9 Hz, 1H), 7.45 (d, J = 7.8 Hz, 1H), 8.39 (d, J = 8.4 Hz, 1H)
13C NMR: δ 21.7 (1C, s), 55.2 (1C, s), 110.1 (1C, s), 112.6 (1C, s), 116.4 (1C, s), 121.1 (1C, s), 123.0 (1C, s), 124.7 (1C, s), 125.6 (1C, s), 126.0 (1C, s), 126.9 (1C, s), 129.0 (1C, s), 129.4 (1C, s), 132.0 (1C, s), 132.3 (1C, s), 133.0 (1C, s), 134.9 (1C, s), 137.6 (1C, s), 144.9 (1C, s), 145.0 (1C, s), 160.3 (1C, s)
