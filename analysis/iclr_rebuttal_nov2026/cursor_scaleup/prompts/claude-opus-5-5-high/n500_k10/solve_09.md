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
  {"benchmark_main:R77": ["CCO", "COC"]}

Compounds:

### benchmark_main:R77
Molecular formula: C7H9NO2
IR bands (cm-1): [3500.0, 2750.0, 2349.0, 1767.0, 1695.0, 1403.0, 1243.0, 978.0, 914.0, 870.0, 751.0, 720.0]
1H NMR: 1.85 (s, 3H, CH3), 2.69 (dd, J1 = 16.9 Hz, J2 = 8.2 Hz, 1H, -CHHCN), 2.86 (dd, J1 = 16.9 Hz, J2 = 7.0 Hz, 1H, -CHHCN), 3.48 (t, J = 7.1 Hz, 1H, CHCOOH), 5.09 (s, 1H, CHH=), 5.16 (s, 1H, CHH=) ppm
13C NMR: δ 18.7 (1C, s), 20.2 (1C, s), 48.0 (1C, s), 117.1 (1C, s), 117.4 (1C, s), 138.7 (1C, s)

### benchmark_main:R78
Molecular formula: C16H16N2O4
IR bands (cm-1): [3529.0, 3227.0, 3072.0, 2968.0, 2936.0, 1643.0, 1579.0, 1558.0, 1516.0, 1495.0, 1458.0]
1H NMR: 3.81 (s, 6H, H6), 6.97 (s, 2H, H3), 7.51 (t, 2H, J1=7.8, J1=7.2 Hz, H12), 7.57 (t, H, J1=7.2, J1=7.2 Hz, H13), 7.88 (d, 2H, J=7.2 Hz, H11), 8.32 (s, 1H, H7), 8.92 (s, 1H, H5) 11.72 (s, 1H, H8)
13C NMR: δ 56.48 (1C, s), 125.02 (1C, s), 128.04 (1C, s), 128.94 (1C, s), 132.11 (1C, s), 134.09 (1C, s), 138.40 (1C, s)

### benchmark_main:R79
Molecular formula: C13H9FN2O
IR bands (cm-1): [1015.0, 1056.0, 1334.0, 1597.0, 1670.0]
1H NMR: 9.36 (d, 1H, J = 1.4, H-3′), 8.37 (d, 1H, J = 2.5, H-6′), 8.70-8.68 (m, 1H, H-5′), 8.23 (d, 1H, J = 16.2, β-CH), 8.10 (d, 1H, J = 16.2, α-CH), 7.80-7.70 (m, 1H, H-6), 7.45-7.35 (m, 1H, H-4), 7.24-7.08 (2H, H3, H-5)
13C NMR: δ 188.6 (1C, s), 161.9 (1C, d), 148.3 (1C, s), 147.5 (1C, s), 144.9 (1C, s), 143.4 (1C, s), 138.0 (1C, d), 132.4 (1C, d), 129.5 (1C, d), 124.5 (1C, d), 122.9 (1C, d), 123.3 (1C, d)

### benchmark_main:R84
Molecular formula: C11H14N2O4
IR bands (cm-1): [3379.0, 3314.0, 2951.0, 1695.0, 1624.0, 1592.0, 1582.0, 1513.0, 1411.0, 1282.0, 1231.0]
1H NMR: 12.42 (brs, 1H), 7.17 (d, J = 8.6 Hz, 2H), 6.87 (d, J = 8.6 Hz, 2H), 6.55 (t, J = 5.8 Hz, 1H), 6.14 (t, J = 5.8 Hz, 1H), 4.13 (d, J = 5.8 Hz, 2H), 3.72 (s, 3H), 3.71 (d, J = 5.8 Hz, 2H)
13C NMR: δ 173.0 (1C, s), 158.5 (1C, s), 158.4 (1C, s), 133.1 (1C, s), 128.8 (1C, s), 114.0 (1C, s), 55.5 (1C, s), 42.8 (1C, s), 42.0 (1C, s)

### benchmark_main:R87
Molecular formula: C10H12O4S
IR bands (cm-1): [3486.0, 3024.0, 2955.0, 2913.0, 2840.0, 1610.0, 1512.0, 1466.0, 1416.0, 1376.0, 1291.0, 1253.0, 1209.0, 1179.0, 1132.0, 1111.0, 1033.0, 1010.0, 964.0, 894.0, 827.0, 748.0, 646.0, 601.0, 550.0, 486.0, 475.0, 424.0]
1H NMR: 7.42 (d, J = 8.8 Hz, 2H, 2 × Ar-H), 6.96 (d, J = 8.8 Hz, 2H, 2 × Ar-H), 4.63 (d, J = 14.9 Hz, 2H, CHH-S-CHH), 4.42 (d, J = 14.9 Hz, 2H, CHH-S-CHH), 3.84 (s, 3H, OCH3); 13C{1H} NMR (101 MHz, CDCl3) δ 159.9 (Ar-CqOMe), 133.1 (Ar-CqCq), 126.2 (2 × Ar-CH), 114.4 (2 × Ar-CH), 78.2 (CH2SO2CH2), 64.6 (Cq), 55.4 (OCH3)
13C NMR: δ 159.9 (1C, s), 133.1 (1C, s), 126.2 (1C, s), 114.4 (1C, s), 78.2 (1C, s), 64.6 (1C, s), 55.4 (1C, s)

### benchmark_main:R88
Molecular formula: C14H15N3O2
IR bands (cm-1): [3420.0, 3336.0, 3182.0, 1632.0, 1607.0, 1579.0, 1490.0, 1450.0, 1418.0, 1270.0, 1129.0, 993.0, 925.0, 789.0, 762.0, 733.0, 692.0, 635.0, 593.0, 530.0, 437.0]
1H NMR: 7.31-7.35 (m, 2H), 7.23-7.27 (m, 1H), 7.17-7.20 (m, 2H), 6.84 (s, 2H), 5.78 (ddt, J = 17.2, 10.3, 5.2, 5.2 Hz, 1H), 5.07 (s, 2H), 5.03 (dq, J = 10.3, 1.5 Hz, 2H), 4.99 (dq, J = 17.2, 1.6 Hz, 1H), 4.73 (s, 1H), 4.33 (dt, J = 5.2, 1.5 Hz, 2H); 13C{1H} NMR (176 MHz, DMSO-d6) δ 160.9, 154.6, 151.4, 136.6, 133.6, 128.5, 127.2, 126.4, 115.7, 75.2, 44.6, 42.0
13C NMR: δ 160.9 (1C, s), 154.6 (1C, s), 151.4 (1C, s), 136.6 (1C, s), 133.6 (1C, s), 128.5 (1C, s), 127.2 (1C, s), 126.4 (1C, s), 115.7 (1C, s), 75.2 (1C, s), 44.6 (1C, s), 42.0 (1C, s)
