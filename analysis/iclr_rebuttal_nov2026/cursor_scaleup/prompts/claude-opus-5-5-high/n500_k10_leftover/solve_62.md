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
  {"benchmark_expand_500:R61": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R61
Molecular formula: C11H12BrFO2
IR bands (cm-1): [746.0, 592.0, 471.0, 748.0, 638.0]
1H NMR: 7.64-7.55 (m, 2H, Ar), 7.42-7.34 (m, 1H, Ar), 7.25-7.18 (m, 1H, Ar), 4.27 (q, JH-H = 7.2 Hz, 2H, OEt), 1.98 (d, JH-F = 23.6 Hz, 3H, 2-Me), 1.27 (t, JH-H = 7.2 Hz, 3H, OEt)
13C NMR: δ 169.3 (1C, d), 139.0 (1C, d), 134.0 (1C, s), 130.0 (1C, d), 127.4 (1C, d), 127.0 (1C, d), 120.6 (1C, d), 95.2 (1C, d), 62.2 (1C, s), 23.3 (1C, d)

### benchmark_expand_500:R63
Molecular formula: C13H10ClN3O2S
IR bands (cm-1): [3323.0, 3161.0, 3089.0, 2982.0, 1592.0, 1527.0, 1482.0, 1407.0, 1362.0, 1298.0, 1187.0, 1143.0, 1047.0, 863.0, 695.0]
1H NMR: 10.15 (s, 2H, NH), 8.35 (d, 1H, J = 2.4 Hz, H-2), 7.81 (dd, 1H, J1 = J2 = 2.4 Hz, H-6), 7.70 (d, 1H, J = 9.0 Hz, H-5), 7.47-7.44 (m, 2H, H-2′, H-6′), 7.37 (t, 2H, J = 7.8 Hz, H-3′, H-5′), 7.18 (t, 1H, J = 7.35 Hz, H-4′)
13C NMR: δ 179.95 (1C, s), 147.09 (1C, s), 140.05 (1C, s), 139.08 (1C, s), 131.53 (1C, s), 128.92 (1C, s), 128.62 (1C, s), 125.31 (1C, s), 124.20 (1C, s), 119.98 (1C, s), 119.65 (1C, s)

### benchmark_expand_500:R67
Molecular formula: C12H13NO4S
IR bands (cm-1): [3265.0, 3019.0, 2930.0, 2848.0, 2125.0, 1670.0, 1595.0, 1498.0, 1312.0, 1238.0, 1088.0, 984.0, 867.0]
1H NMR: 7.93-7.90 (m, 2H, 2 × Ar-H), 7.08-7.04 (m, 2H, 2 × Ar-H), 4.70-4.66 (m, 1H, OCHH), 4.65-4.60 (m, 1H, OCHH), 3.90 (s, 3H, OCH3), 3.32 (s, 3H, SCH3), 2.43 (t, J = 2.5 Hz, 1H, CCH); 13C{1H} NMR (101 MHz, CDCl3) δ 164.1 (Ar-Cq), 158.1 (C=O), 129.6 (2 × Ar-C), 128.8(Ar-Cq), 115.0 (2 × Ar-C), 78.0 (CCH), 74.6 (CCH), 55.8 (OCH3), 53.3 (CH2), 44.9 (SCH3)
13C NMR: δ 164.1 (1C, s), 158.1 (1C, s), 129.6 (1C, s), 128.8 (1C, s), 115.0 (1C, s), 78.0 (1C, s), 74.6 (1C, s), 55.8 (1C, s), 53.3 (1C, s), 44.9 (1C, s)

### benchmark_expand_500:R70
Molecular formula: C12H11N
IR bands (cm-1): [3383.0, 3034.0, 2922.0, 1595.0, 1493.0, 1319.0, 1172.0, 1084.0, 876.0, 745.0, 689.0, 505.0]
1H NMR: 7.26 (t, J = 7.8 Hz, 4H), 7.07 (d, J = 7.7 Hz, 4H), 6.92 (t, J = 7.3 Hz, 2H), 5.69 (s, 1H); 13C{1H} NMR (75 MHz, CDCl3): δ 143.1, 129.3, 121.0, 117.8
13C NMR: δ 143.1 (1C, s), 129.3 (1C, s), 121.0 (1C, s), 117.8 (1C, s)

### benchmark_expand_500:R72
Molecular formula: C16H21N
IR bands (cm-1): [3297.0, 2935.0, 2908.0, 2801.0, 1496.0, 1337.0, 1313.0, 750.0, 700.0, 641.0]
1H NMR: 1.24-1.39 (m, 3H), 1.56-1.62 (m, 2H), 1.75-1.81 (m, 2H), 2.15-2.22 (m, 2H), 2.24 (t, J = 2.5 Hz, 1H), 2.62-2.66 (m, 2H), 2.87-2.92 (m, 2H), 3.30 (d, J = 2.5 Hz, 2H), 7.16-7.21 (m, 3H), 7.26-7.31 (m, 2H)
13C NMR: δ 32.05 (1C, s), 32.89 (1C, s), 34.58 (1C, s), 38.15 (1C, s), 47.03 (1C, s), 52.34 (1C, s), 72.74 (1C, s), 79.02 (1C, s), 125.44 (1C, s), 128.10 (1C, s), 142.43 (1C, s)

### benchmark_expand_500:R74
Molecular formula: C15H19FN4O
IR bands (cm-1): [3406.0, 3128.0, 3100.0, 2978.0, 1495.0, 1468.0, 1393.0, 1309.0, 1281.0, 1209.0, 1082.0]
1H NMR: 7.92 (s, 1H), 7.70-7.68 (m, 1H), 7.59-7.57 (m, 1H), 7.29-7.27 (m, 1H), 7.07-7.03 (m, 1H), 5.37 (d, J = 5.2 Hz, 2H), 2.32 (d, J = 1.8 Hz, 3H), 1.53 (s, 9H)
13C NMR: δ 161.35 (1C, d), 147.42 (1C, s), 128.95 (1C, d), 127.16 (1C, s), 126.23 (1C, d), 125.44 (1C, d), 124.79 (1C, d), 120.67 (1C, s), 115.45 (1C, d), 70.70 (1C, s), 46.67 (1C, s), 27.87 (1C, s), 14.55 (1C, d)
