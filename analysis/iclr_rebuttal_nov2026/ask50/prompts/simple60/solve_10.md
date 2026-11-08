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
  {"benchmark_main:R92": ["CCO", "COC"]}

Compounds:

### benchmark_main:R92
Molecular formula: C10H10N2O2
IR bands (cm-1): [3274.0, 2233.0, 1682.0, 1618.0, 1558.0, 1509.0, 1475.0, 1391.0, 1252.0, 1173.0, 1117.0, 1049.0, 923.0, 836.0, 735.0, 705.0, 607.0, 523.0]
1H NMR: 11.72 (broad s, 1H, NH), 7.47 (d, J = 8.0 Hz, 2H, Ar-H), 6.91 (d, J = 8.0 Hz, 2H, Ar-H), 3.97 (q, J = 8.0 Hz, 2H, OCH2), 1.29 (t, J = 8.0 Hz, 2H, CH3)
13C NMR: δ 156.4 (1C, s), 140.4 (1C, s), 129.7 (1C, s), 122.0 (1C, s), 114.9 (1C, s), 112.8 (1C, s), 63.5 (1C, s), 14.8 (1C, s)

### benchmark_main:R93
Molecular formula: C12H15NO4S
IR bands (cm-1): [3415.0, 2957.0, 1737.0, 1619.0, 1597.0, 1494.0, 1449.0, 1345.0, 1306.0, 1199.0, 1159.0, 1095.0, 1013.0]
1H NMR: 7.65 (d, J = 8.6 Hz, 2H, ArH), 7.35 (d, J = 8.00 Hz, 2H, ArH), 4.04 (dd, J = 4.55, 5.15 Hz, 1H, CH-COOH), 3.29 (dd, J = 9.75, 5.15Hz, 1H, CHa of CH2-N), 3.09 (dd, J = 6.85, 7.45 Hz, 1H, CHb of CH2-N), 2.31 (s, 3H, CH3-Ar), 1.77 (m, 3H), 1.48 (t, J = 5.15 Hz, 1H)
13C NMR: δ 173.7 (1C, s), 143.9 (1C, s), 135.1 (1C, s), 130.3 (1C, s), 127.6 (1C, s), 66.9 (1C, s), 48.9 (1C, s), 30.9 (1C, s), 24.7 (1C, s), 21.4 (1C, s)

### benchmark_main:R94
Molecular formula: C10H12N2
IR bands (cm-1): [3291.0, 3042.0, 2938.0, 2862.0, 1650.0, 1599.0, 1402.0, 1318.0, 1258.0, 1041.0]
1H NMR: 7.30 (t, J = 7.8 Hz, 2H), 7.06 (dd, J = 17.1, 7.7 Hz, 3H), 3.85-3.67 (m, 4H), 2.00 (s, 3H)
13C NMR: δ 161.5 (1C, s), 141.5 (1C, s), 129.2 (1C, s), 124.1 (1C, s), 122.2 (1C, s), 52.1 (1C, s), 51.9 (1C, s), 16.0 (1C, s)

### benchmark_main:R95
Molecular formula: C14H13NO
IR bands (cm-1): [1649.0, 1633.0, 1603.0, 1497.0, 1482.0, 1262.0, 1204.0, 1159.0, 900.0, 762.0, 697.0]
1H NMR: 1.93 (d, J = 1.5 Hz, 3H, CH3-C2), 2.27 (d, J = 1.5 Hz, 3H, CH3-C5), 6.55 (q, J = 1.5 Hz, 1H, H-6), 6.78 (q, J = 1.5 Hz, 1H, H-3), 6.80-6.85 (m, 2H, H-2′), 7.17-7.22 (m, 1H, H-4′), 7.34-7.44 (m, 2H, H-3′)
13C NMR: δ 16.1 (1C, s), 18.0 (1C, s), 120.2 (1C, s), 125.4 (1C, s), 125.6 (1C, s), 129.2 (1C, s), 131.1 (1C, s), 141.5 (1C, s), 149.5 (1C, s), 150.2 (1C, s), 158.5 (1C, s), 188.4 (1C, s)

### benchmark_main:R98
Molecular formula: C10H12N4OS
IR bands (cm-1): [3467.0, 2971.0, 2845.0, 1607.0, 1515.0, 1453.0, 1251.0, 1170.0, 1089.0, 1021.0, 830.0, 625.0, 555.0]
1H NMR: 7.45 (2H, m), 7.03 (2H, m), 3.87 (3H, s), 3.38 (2H, q, J = 7.4 Hz), 1.48 (3H, t, J = 7.4 Hz). 13C{1H} NMR (100 MHz, CDCl3): δ 160.9, 154.5, 126.5, 125.7, 115.0, 55.8, 27.8, 14.7
13C NMR: δ 160.9 (1C, s), 154.5 (1C, s), 126.5 (1C, s), 125.7 (1C, s), 115.0 (1C, s), 55.8 (1C, s), 27.8 (1C, s), 14.7 (1C, s)

### benchmark_main:R99
Molecular formula: C16H18O5
IR bands (cm-1): [2983.0, 1748.0, 1702.0, 1262.0, 1203.0, 514.0]
1H NMR: 7.95 (s, 1H), 7.41-7.31 (m, 5H), 4.26 (q, J = 7.1 Hz, 2H), 3.73 (s, 3H), 3.72 (s, 2H), 3.60 (s, 2H), 1.33 (t, J = 7.1 Hz, 3H)
13C NMR: δ 200.3 (1C, s), 167.5 (1C, s), 167.3 (1C, s), 142.8 (1C, s), 135.0 (1C, s), 129.1 (1C, s), 128.9 (1C, s), 128.8 (1C, s), 126.3 (1C, s), 61.4 (1C, s), 52.5 (1C, s), 49.3 (1C, s), 42.0 (1C, s), 14.3 (1C, s)
