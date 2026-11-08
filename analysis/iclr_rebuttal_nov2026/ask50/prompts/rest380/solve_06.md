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
  {"benchmark_expand:R50": ["CCO", "COC"]}

Compounds:

### benchmark_expand:R50
Molecular formula: C23H14O4
IR bands (cm-1): [3100.0, 2700.0, 1680.0, 1663.0, 1609.0, 1570.0, 1501.0, 1485.0, 1454.0, 1418.0, 1350.0, 1312.0, 1173.0, 1111.0, 1094.0, 1032.0, 1007.0, 966.0, 953.0, 924.0, 745.0]
1H NMR: 3.66 (d, J = 17.9 Hz, 1H), 3.85 (d, J = 17.9 Hz, 1H), 6.80-6.85 (m, 3H), 6.93 (t, J = 7.3 Hz, 1H), 7.09-7.14 (m, 2H), 7.22 (t, J = 7.6 Hz, 1H), 7.29 (d, J = 8.2 Hz, 1H), 7.52 (t, J = 7.5 Hz, 1H), 7.85 (d, J = 8.0 Hz, 1H), 11.71 (s, 1H)
13C NMR: δ 32.6 (1C, s), 96.2 (1C, s), 105.0 (1C, s), 113.4 (1C, s), 113.9 (1C, s), 116.0 (1C, s), 117.4 (1C, s), 122.2 (1C, s), 122.3 (1C, s), 122.6 (1C, s), 123.9 (1C, s), 125.6 (1C, s), 128.2 (1C, s), 129.3 (1C, s), 131.7 (1C, s), 138.4 (1C, s), 152.8 (1C, s), 152.9 (1C, s), 160.4 (1C, s)

### benchmark_expand:R52
Molecular formula: C21H29NO13
IR bands (cm-1): [3369.0, 1655.0, 1609.0, 1503.0, 1487.0, 1446.0, 1247.0, 1219.0, 1155.0, 1074.0, 1035.0, 1035.0, 931.0, 760.0]
1H NMR: 1.97 (s, 3H, CH3CON), 3.15 (t, J 2,1 = J 2,3 = 9.2 Hz, 1H, H-2), 3.46 (dd, J 4,5 = 9.8, J 4,3 = 8.9 Hz, 1H, H-4), 3.56 (dd, J 2′,3′ = 9.9, J 2′,3′ = 7.7 Hz, 1H, H-2′), 3.64 (dd, J 3′,2′ = 9.9, J 3′,4′ = 3.4 Hz, 1H, H-3′), 3.67 (ddd, J 5′,6′a = 7.3, J 5′,6′a = 4.7, J 5′,4′ = 1.2 Hz, 1H, H-5′), 3.67-3.77 (m, 3H, H-3,5,6′b), 3.77 (dd, J gem = 11.6, J 6′a,5 = 7.3 Hz, 1H, H-6′b), 3.79 (dd, J gem = 12.3, J 6a,5 = 5.2 Hz, 1H, H-6a), 3.93 (dd, J 4′,3′ = 3.4, J 4′,5′ = 1.1 Hz, 1H, H-4′), 3.97 (dd, J gem = 12.3, J 6b,5 = 2.4 Hz, 1H, H-6b), 4.41 (d, J 1′,2′ = 7.7 Hz, 1H, H-1′), 5.58 (br s, 1H, H-1), 6.05 (s, 2H, CH2), 6.91 (dd, J 6″,5′′ = 8.2, J 6″,2′′ = 2.1 Hz, 1H, H-6″), 6.94 (d, J 2″,6′′ = 2.1 Hz, 1H, H-2″), 6.98 (d, J 5″,6′′ = 8.2 Hz, 1H, H-5″)
13C NMR: δ 22.72 (1C, s), 61.20 (1C, s), 61.48 (1C, s), 69.21 (1C, s), 70.10 (1C, s), 71.59 (1C, s), 73.33 (1C, s), 75.81 (1C, s), 76.15 (1C, s), 77.31 (1C, s), 79.02 (1C, s), 82.16 (1C, s), 102.41 (1C, s), 103.39 (1C, s), 108.76 (1C, s), 111.07 (1C, s), 124.19 (1C, s), 131.45 (1C, s), 148.02 (1C, s), 176.69 (1C, s)

### benchmark_expand:R54
Molecular formula: C23H16ClN3
IR bands (cm-1): [3062.0, 3007.0, 2957.0, 1605.0, 1512.0, 1486.0, 1380.0, 1309.0, 1143.0, 1015.0, 910.0, 761.0]
1H NMR: 8.70 (d, 1H, J = 8.4 Hz), 8.66 (s, 1H), 8.53 (d, 1H, J = 8.0 Hz), 8.33 (d, 1H, J = 7.8 Hz), 8.19 (dd, 2H, J = 7.8, 1.2 Hz), 7.81 (t, 1H, J = 7.8 Hz), 7.73 (t, 1H, J = 8.0 Hz), 7.70 (dd, 1H, J = 8.0, 1.2 Hz), 7.62-7.58 ppm (m, 3H)
13C NMR: δ 158.9 (1C, s), 153.3 (1C, s), 143.6 (1C, s), 138.0 (1C, s), 135.9 (1C, s), 132.7 (1C, s), 131.7 (1C, s), 129.9 (1C, s), 129.2 (1C, s), 128.3 (1C, s), 128.2 (1C, s), 127.9 (1C, s), 127.3 (1C, s), 124.1 (1C, s), 124.0 (1C, s), 122.2 (1C, s)

### benchmark_expand:R57
Molecular formula: C21H11ClF2N4O
IR bands (cm-1): [3417.0, 1657.0, 1547.0, 3062.0, 748.0, 1238.0]
1H NMR: 12.42 (s, 1H), 8.54 (s, 1H), 8.21-8.22 (d, 1H, J=4 Hz), 8.10-8.12 (d, 1H, J=8 Hz), 8.08-8.10 (d, 1H, J=8 Hz), 8.01-8.03 (d, 1H, J=8 Hz), 7.82-7.85 (t, 1H, J=12 Hz), 7.51-7.52 (d, 1H, J=4 Hz), 7.22-7.24 (t, 1H, J=8 Hz), 6.98-7.01 (t, 1H, J=12 Hz), 6.742-6.745 (d, 1H, J=1.2 Hz)
13C NMR: δ 162.0 (1C, s), 161.7 (1C, s), 152.2 (1C, s), 148.4 (1C, s), 146.4 (1C, s), 145.8 (1C, s), 145.6 (1C, s), 139.8 (1C, s), 139.6 (1C, s), 131.8 (1C, s), 131.3 (1C, s), 131.1 (1C, s), 130.8 (1C, s), 124.0 (1C, s), 123.8 (1C, s), 117.1 (1C, s), 112.9 (1C, s), 112.5 (1C, s), 112.3 (1C, s)

### benchmark_expand:R58
Molecular formula: C15H17IN4O
IR bands (cm-1): [3335.0, 3162.0, 2936.0, 1663.0, 1598.0, 1444.0, 1395.0, 985.0, 771.0, 630.0]
1H NMR: 7.83 (dd, J = 6.6, 2.3 Hz, 1H), 7.50 (tt, J = 7.5, 5.6 Hz, 2H), 7.38 (dd, J = 6.6, 2.2 Hz, 1H), 6.56 (br s, 1H), 5.89 (br s, 1H), 4.34 (tt, J = 11.6, 4.0 Hz, 1H), 2.18-2.11 (m, 2H), 2.05 (qd, J = 12.5, 3.5 Hz, 2H), 2.00-1.94 (m, 2H), 1.78 (dt, J = 12.8, 3.5 Hz, 1H), 1.46 (qt, J = 13.0, 3.5 Hz, 2H), 1.33 (qt, J = 13.0, 3.5 Hz, 1H) ppm
13C NMR: δ 170.4 (1C, s), 149.9 (1C, s), 135.8 (1C, s), 131.4 (1C, s), 130.4 (1C, s), 129.5 (1C, s), 129.2 (1C, s), 127.8 (1C, s), 80.2 (1C, s), 61.6 (1C, s), 32.7 (1C, s), 25.3 (1C, s)

### benchmark_expand:R61
Molecular formula: C18H11BrN2O5S
IR bands (cm-1): [3076.0, 2969.0, 1748.0, 1696.0, 1605.0, 1527.0, 1216.0]
1H NMR: 8.42 (d, J = 8.7 Hz, 2H), 8.34 (d, J = 8.7 Hz, 2H), 8.02 (s, 1H), 7.80 (d, J = 8.3 Hz, 2H), 7.65 (d, J = 8.3 Hz, 2H), 5.46 (s, 2H)
13C NMR: δ 191.5 (1C, s), 167.2 (1C, s), 165.5 (1C, s), 151.1 (1C, s), 138.8 (1C, s), 136.0 (1C, s), 133.3 (1C, s), 132.4 (1C, s), 132.2 (1C, s), 130.4 (1C, s), 130.0 (1C, s), 124.5 (1C, s), 122.0 (1C, s)
