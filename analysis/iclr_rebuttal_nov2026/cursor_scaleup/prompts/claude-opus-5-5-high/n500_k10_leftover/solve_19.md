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
  {"benchmark_expand_500:R193": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R193
Molecular formula: C17H23N3O5S
IR bands (cm-1): [3067.0, 2983.0, 2864.0, 1728.0, 1690.0, 1647.0, 1599.0, 1534.0, 1431.0]
1H NMR: 8.75 (1H, br s, NH), 7.34 (1H, d, J = 10.8 Hz, Ar-CH), 6.51 (1H, d, J = 10.4 Hz, Ar-CH), 6.34 (1H, s, CH), 4.31-4.11 (4H, m, 2 × CH2), 1.43 (9H, s, C(CH3)3), 1.33 (3H, t, J = 7.2 Hz, CH3), 1.26 (3H, t, J = 7.2 Hz, CH3)
13C NMR: δ 170.6 (1C, s), 168.1 (1C, s), 160.8 (1C, s), 157.3 (1C, s), 154.8 (1C, s), 136.7 (1C, s), 118.2 (1C, s), 72.5 (1C, s), 61.9 (1C, s), 59.3 (1C, s), 52.6 (1C, s)

### benchmark_expand_500:R194
Molecular formula: C12H15N3O4S
IR bands (cm-1): [3363.0, 1685.0, 1546.0, 1440.0, 1325.0, 1219.0, 1157.0, 1085.0, 773.0]
1H NMR: 9.05 (s, 1H), 8.37 (s, 1H), 7.64 (d, J = 8.8 Hz, 1H), 7.43 (t, J = 7.8 Hz, 1H), 7.02 (t, J = 6.8 Hz, 1H), 4.51-4.46 (m, 2H), 3.75-3.69 (m, 2H), 1.47-1.43 (m, 6H)
13C NMR: δ 160.4 (1C, s), 149.3 (1C, s), 146.0 (1C, s), 128.8 (1C, s), 128.0 (1C, s), 116.8 (1C, s), 114.3 (1C, s), 100.3 (1C, s), 61.1 (1C, s), 48.2 (1C, s), 14.7 (1C, s), 8.2 (1C, s)

### benchmark_expand_500:R195
Molecular formula: C18H15BrN2O4
IR bands (cm-1): [3255.0, 1671.0, 1580.0, 1350.0, 1248.0, 695.0]
1H NMR: 9.16 (s, 1H), 7.94 (dd, J = 4.9, 1.8 Hz, 1H), 7.65-7.57 (m, 1H), 7.53 (dd, J = 7.8, 1.7 Hz, 1H), 7.48-7.31 (m, 3H), 7.24 (td, J = 7.6, 1.7 Hz, 1H), 6.69 (dd, J = 21.4, 8.0 Hz, 2H), 6.53 (dd, J = 7.0, 5.1 Hz, 1H), 6.32 (s, 2H), 5.62 (t, J = 6.1 Hz, 1H), 4.25-4.15 (m, 2H)
13C NMR: δ 174.2 (1C, s), 167.9 (1C, s), 157.5 (1C, s), 148.2 (1C, s), 147.8 (1C, s), 142.5 (1C, s), 139.1 (1C, s), 137.2 (1C, s), 133.1 (1C, s), 129.8 (1C, s), 129.7 (1C, s), 128.1 (1C, s), 123.5 (1C, s), 113.1 (1C, s), 109.4 (1C, s), 109.3 (1C, s), 59.8 (1C, s), 51.8 (1C, s)

### benchmark_expand_500:R196
Molecular formula: C23H20N2
IR bands (cm-1): [1594.0, 1499.0, 1320.0, 1225.0]
1H NMR: 7.60 (t, J = 8.8 Hz, 3H, ArH), 7.53 (d, J = 8.2 Hz, 2H, ArH), 7.41 (d, J = 8.0 Hz, 2H), 7.30 (d, J = 16.3 Hz, 1H, -CH=CH-), 7.25-7.16 (m, 3H, ArH), 7.02-6.96 (m, 2H, ArH), 6.87-6.80 (m, 1H, ArH), 6.54 (d, J = 16.3 Hz, 1H, -CH=CH-), 5.36 (dd, J = 12.4, 6.6 Hz, 1H, -CH-, C5 of dihydropyrazole), 3.76 (dd, J = 16.7, 12.4 Hz, 1H, -CH2-, C4 of dihydropyrazole), 3.01 (dd, J = 16.8, 6.6 Hz, 1H, -CH2-, C4 of dihydropyrazole)
13C NMR: δ 147.7 (1C, s), 146.1 (1C, s), 143.7 (1C, s), 140.1 (1C, s), 131.1 (1C, s), 130.0 (1C, s), 129.7 (1C, s), 129.3 (1C, s), 126.5 (1C, q), 126.8 (1C, s), 126.3 (1C, s), 125.9 (1C, q), 124.7 (1C, d), 123.9 (1C, s), 120.2 (1C, s), 113.6 (1C, s)

### benchmark_expand_500:R199
Molecular formula: C20H28O4
IR bands (cm-1): [2967.0, 1749.0, 1450.0, 1186.0, 1097.0, 1060.0, 897.0]
1H NMR: 1.26 (s, 6H), 1.66 (s, 6H), 1.69-1.78 (m, 2H), 2.21-2.42 (m, 4H), 2.63 (ddd, 2J = 17.6 Hz, 3J = 13.7, 9.4 Hz, 2H), 3.99 (d, 2J = 12.7 Hz, 2H), 4.10 (d, 2J = 12.7 Hz, 2H), 4.78 (virt. dt, 4J = 3.0 Hz, 2J ≅ 4J = 1.6 Hz, 2H), 4.83-4.94 (m, 2H). 13C{1H} NMR (126 MHz, CDCl3, 300 K): δ 19.1 (q), 19.6 (q), 32.7 (t), 37.2 (t), 44.4 (s), 70.3 (t), 85.8 (s), 110.5 (t), 142.3 (s), 214.0 (s)
13C NMR: δ 19.1 (1C, q), 19.6 (1C, q), 32.7 (1C, t), 37.2 (1C, t), 44.4 (1C, s), 70.3 (1C, t), 85.8 (1C, s), 110.5 (1C, t), 142.3 (1C, s), 214.0 (1C, s)

### benchmark_expand_500:R20
Molecular formula: C22H20ClN3O2
IR bands (cm-1): [3058.0, 2926.0, 2844.0, 1609.0, 1445.0, 1256.0, 1159.0]
1H NMR: 7.55-7.47 (m, 2H), 7.07-6.99 (m, 3H), 6.64 (s, 1H), 6.43 (d, J = 9.8 Hz, 1H), 5.70 (d, J = 9.8 Hz, 1H), 3.88 (s, 3H), 3.39 (d, J = 16.6 Hz, 1H), 3.01-2.90 (m, 2H), 2.78-2.68 (m, 1H), 2.37-2.28 (m, 1H), 2.28 (s, 3H), 1.96-1.87 (m, 1H)
13C NMR: δ 159.8 (1C, s), 150.5 (1C, s), 141.1 (1C, s), 137.1 (1C, s), 130.9 (1C, s), 129.9 (1C, s), 128.3 (1C, s), 126.4 (1C, s), 126.3 (1C, s), 124.6 (1C, s), 123.4 (1C, s), 120.5 (1C, s), 118.9 (1C, s), 114.7 (1C, s), 76.3 (1C, s), 55.6 (1C, s), 33.6 (1C, s), 32.3 (1C, s), 20.1 (1C, s), 17.7 (1C, s)
