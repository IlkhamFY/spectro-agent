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
  {"benchmark_main:R23": ["CCO", "COC"]}

Compounds:

### benchmark_main:R23
Molecular formula: C15H17NO
IR bands (cm-1): [3390.0, 2924.0, 2853.0, 1613.0, 1463.0, 1295.0, 1243.0, 1180.0, 1038.0, 821.0]
1H NMR: 1.22 (t, J = 6.7 Hz, 3 H), 2.58 (q, J = 6.7 Hz, 2 H), 3.80 (s, 3 H), 5.40 (br. s, 1 H), 6.85-6.89 (m, 4 H), 7.03-7.07 (m, 4 H)
13C NMR: δ 15.8 (1C, s), 28.0 (1C, s), 55.6 (1C, s), 114.7 (1C, s), 116.5 (1C, s), 121.2 (1C, s), 128.6 (1C, s), 135.9 (1C, s), 136.6 (1C, s), 142.6 (1C, s), 154.8 (1C, s)

### benchmark_main:R24
Molecular formula: C10H8Br4O2
IR bands (cm-1): [994.0, 955.0, 924.0, 853.0, 1716.0, 608.0, 432.0, 960.0, 863.0, 840.0, 766.0, 736.0, 707.0, 691.0, 671.0, 629.0, 607.0, 570.0]
1H NMR: 8.05 (d, J = 8.8 Hz, 2H), 7.96 (d, J = 8.8 Hz, 2H), 6.41 (s, 1H), 3.94 (s, 3H) ppm; 13C{1H} NMR (100 MHz, CDCl3): δ = 164.9, 143.1, 130.4, 128.5, 127.8, 70.1, 52.7, 51.4 ppm
13C NMR: δ 164.9 (1C, s), 143.1 (1C, s), 130.4 (1C, s), 128.5 (1C, s), 127.8 (1C, s), 70.1 (1C, s), 52.7 (1C, s)

### benchmark_main:R26
Molecular formula: C15H19NO2
IR bands (cm-1): [3399.0, 2970.0, 1742.0, 1582.0, 1522.0, 1454.0, 1216.0]
1H NMR: 8.12 (d, J = 8.4 Hz, 1H), 7.39 (s, 1H), 7.32 (ddd, J = 7.7, 1.6, 0.5 Hz, 1H), 7.26 (dddd, J = 8.2, 7.4, 1.6, 0.5 Hz, 1H), 6.94 (td, J = 7.6, 1.2 Hz, 1H), 4.24 (q, J = 7.1 Hz, 2H), 1.37 (s, 9H), 1.32 (t, J = 7.1 Hz, 3H) ppm. 13C{1H} NMR (100.62 MHz, CDCl3): δ 153.4, 139.0, 131.3, 128.9, 122.2, 117.4, 112.1, 106.0, 74.5, 61.3, 31.1 (3×), 28.4, 14.6 ppm
13C NMR: δ 153.4 (1C, s), 139.0 (1C, s), 131.3 (1C, s), 128.9 (1C, s), 122.2 (1C, s), 117.4 (1C, s), 112.1 (1C, s), 106.0 (1C, s), 74.5 (1C, s), 61.3 (1C, s), 31.1 (1C, s), 28.4 (1C, s)

### benchmark_main:R29
Molecular formula: C10H18O2
IR bands (cm-1): [2970.0, 2879.0, 1712.0, 1451.0, 1377.0, 1282.0, 1114.0, 713.0]
1H NMR: 9.77 (t, J = 1.7 Hz, 1H), 4.11-4.05 (m, 0.29H minor, C5-H), 4.05-3.98 (m, 0.71H major, C5-H), 2.46 (t, J = 7.2 Hz, 2H), 2.02-1.95 (m, 1H), 1.83-1.75 (m, 1H), 1.75-1.64 (m, 2H), 1.57-1.44 (m, 4H), 1.23 (d, J = 6.0 Hz, 3H), 1.21 (s, 2H), 1.20 (s, 1H)
13C NMR: δ 202.7 (1C, s), 82.4 (1C, s), 75.0 (1C, s), 44.3 (1C, s), 40.8 (1C, s), 37.4 (1C, s), 33.8 (1C, s), 27.3 (1C, s), 21.8 (1C, s), 17.3 (1C, s)

### benchmark_main:R32
Molecular formula: C14H16N2O2
IR bands (cm-1): [3245.0, 3011.0, 3014.0, 1720.0, 1602.0]
1H NMR: 8.31 (s, NH), 7.37-7.34 (dd, 2H, J = 7.21 Hz, J = 7.12 Hz), 7.35 (d, 1CH, J = 7.31 Hz), 7.26-7.21 (d, 2H, J = 7.29 Hz), 6.52 (s, 1H), 6.14 (s, 1H, CH), 4.51 (s, -CH2), 3.78 (d, 1H, J = 7.42 Hz), 3.54 (d, 1H, J = 7.43 Hz), 3.29 (s, -CH3), 2.28 (s, NH)
13C NMR: δ 206.9 (1C, s), 177.3 (1C, s), 129.4 (1C, s), 135.2 (1C, s), 136.7 (1C, s), 127.9 (1C, s), 129.3 (1C, s), 127.2 (1C, s), 67.8 (1C, s), 54.9 (1C, s), 52.3 (1C, s)

### benchmark_main:R34
Molecular formula: C14H12N2O2
IR bands (cm-1): [3217.0, 3056.0, 3039.0, 3027.0, 1614.0, 1588.0, 1548.0, 1509.0, 1356.0, 1280.0, 1212.0, 1172.0, 1110.0, 1056.0, 960.0, 844.0, 763.0, 661.0, 630.0, 614.0, 510.0, 492.0]
1H NMR: 11.64 (s, 1H, NHCO), 10.13 (s, 1H, OH), 8.43 (s, 1H, CH=N), 7.81 (d, 3J = 8.7 Hz, 2H, H-2,6), 7.71 (d, 3J = 6.4 Hz, 2H, ArH-2,6), 7.38-7.48 (m, 3H, ArH-3,4,5), 6.87 (d, 3J = 8.7 Hz, 2H, H-3,5) ppm
13C NMR: δ 162.77 (1C, s), 160.66 (1C, s), 146.82 (1C, s), 130.47 (1C, s), 129.79 (1C, s), 129.65 (1C, s), 128.75 (1C, s), 126.90 (1C, s), 123.81 (1C, s)
