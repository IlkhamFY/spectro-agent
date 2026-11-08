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
  {"benchmark_main:R01": ["CCO", "COC"]}

Compounds:

### benchmark_main:R01
Molecular formula: C14H16FN5O
IR bands (cm-1): [3314.0, 1656.0, 1592.0, 1551.0, 1448.0, 1357.0]
1H NMR: 1.26 (s, 2H, CH2), 1.38 (s, 4H, 2CH2), 1.52 (s, 4H, 2CH2), 7.08-7.10 (d, J = 8 Hz, 2H, Ar-H), 7.32-7.34 (d, J = 8 Hz, 2H, Ar-H)
13C NMR: δ 25.56 (1C, s), 57.74 (1C, s), 65.40 (1C, s), 123.63 (1C, s), 122.9 (1C, s), 129.39 (1C, s), 136.28 (1C, s), 152.23 (1C, s), 156.63 (1C, s)

### benchmark_main:R02
Molecular formula: C14H8N2O4
IR bands (cm-1): [1757.0, 1629.0, 1608.0, 1530.0, 1349.0]
1H NMR: 8.52 (d, 1H, J = 2.2 Hz, ArH), 8.41 (d, 1H, J = 8.6 Hz, ArH), 8.33 (d, 2H, J = 7.4 Hz, ArH), 8.29 (dd, 1H, J = 8.6, 2.2 Hz, ArH), 7.64 (t, 1H, J = 7.4 Hz, ArH), 7.55 (t, 2H, J = 7.4 Hz, ArH)
13C NMR: δ 159.0 (1C, s), 157.9 (1C, s), 152.9 (1C, s), 148.1 (1C, s), 133.6 (1C, s), 130.4 (1C, s), 129.3 (1C, s), 129.0 (1C, s), 128.7 (1C, s), 122.5 (1C, s), 122.0 (1C, s), 121.3 (1C, s)

### benchmark_main:R05
Molecular formula: C12H11Cl2N3O2S
IR bands (cm-1): [3051.0, 2970.0, 2875.0, 1615.0, 1336.0, 1151.0]
1H NMR: 1.63 (4H, qu, 2CH2·pyrrolidine), 3.26 (4H, t, 2N-CH2·pyrolidine), 8.22 (d, 1H, J = 8.0 Hz, H7·quinox), 8.28 (d, 1H, J = 8.0 Hz, H8·quinox), 8.42 (s, 1H, H5·quinox)
13C NMR: δ 25.10 (1C, s), 48.31 (1C, s), 125.99 (1C, s), 127.68 (1C, s), 130.03 (1C, s), 138.99 (1C, s), 139.53 (1C, s), 141.78 (1C, s), 147.09 (1C, s), 147.77 (1C, s)

### benchmark_main:R06
Molecular formula: C29H30FNO2
IR bands (cm-1): [2959.0, 1641.0, 1510.0, 1402.0, 1220.0, 700.0]
1H NMR: 7.43 (d, J = 8.0 Hz, 2H, ArH), 7.24-7.30 (m, 6H, ArH), 7.10-7.13 (m, 1H, ArH), 5.29 (s, 1H, CH), 2.21 (AB, J = 16.0 Hz, 2H, CH2), 2.14 (AB, J = 16.0 Hz, 2H, CH2), 2.08 (AB, J = 16.0 Hz, 2H, CH2), 1.83 (AB, J = 16.0 Hz, 2H, CH2), 0.97 (s, 6H, 2 × CH3), 0.82 (s, 6H, 3 × CH3)
13C NMR: δ 195.7 (1C, s), 162.5 (1C, d), 149.5 (1C, s), 146.0 (1C, s), 135.1 (1C, s), 135.0 (1C, s), 131.8 (1C, s), 128.1 (1C, s), 127.8 (1C, s), 126.0 (1C, s), 117.2 (1C, s), 114.8 (1C, s), 50.2 (1C, s), 41.9 (1C, s), 32.6 (1C, s), 32.4 (1C, s), 29.8 (1C, s), 26.8 (1C, s)

### benchmark_main:R07
Molecular formula: C18H13BrClNO
IR bands (cm-1): [3319.0, 3058.0, 2987.0, 2949.0, 2917.0, 2859.0, 1905.0, 1585.0, 1476.0, 1392.0, 1348.0, 1322.0, 1162.0, 1123.0, 1085.0, 989.0]
1H NMR: 8.26 (d, J = 2.2 Hz, 1H), 7.85 (d, J = 8.9 Hz, 1H), 7.70 (dd, J = 2.3, 8.9 Hz, 1H), 7.53-7.48 (m, 2H), 7.45-7.40 (m, 2H), 4.46-4.39 (m, 2H), 2.72 (t, J = 6.3 Hz, 2H), 2.03-1.97 (m, 2H)
13C NMR: δ 159.91 (1C, s), 156.71 (1C, s), 145.86 (1C, s), 138.58 (1C, s), 134.58 (1C, s), 132.71 (1C, s), 130.76 (1C, s), 130.24 (1C, s), 128.54 (1C, s), 123.91 (1C, s), 121.18 (1C, s), 119.46 (1C, s), 111.35 (1C, s), 67.21 (1C, s), 23.80 (1C, s), 21.75 (1C, s)

### benchmark_main:R08
Molecular formula: C16H11ClO2
IR bands (cm-1): [2920.0, 1776.0, 1654.0, 1482.0, 1437.0, 1280.0, 1105.0, 964.0, 756.0, 538.0, 486.0]
1H NMR: 8.31-8.28 (m, 1H), 7.74 (d, J = 7.84 Hz, 2H), 7.56-7.54 (m, 1H), 7.41 (dd, J = 7.96 Hz, 1.24 Hz, 1H), 7.34-7.30 (m, 1H), 7.24-7.19 (m, 1H), 6.82 (s, 1H), 2.50 (s, 3H)
13C NMR: δ 167.12 (1C, s), 146.07 (1C, s), 141.11 (1C, s), 138.20 (1C, s), 136.05 (1C, s), 133.75 (1C, s), 131.76 (1C, s), 131.20 (1C, s), 129.67 (1C, s), 129.18 (1C, s), 127.27 (1C, s), 125.58 (1C, s), 123.86 (1C, s), 120.19 (1C, s), 101.55 (1C, s), 21.71 (1C, s)
