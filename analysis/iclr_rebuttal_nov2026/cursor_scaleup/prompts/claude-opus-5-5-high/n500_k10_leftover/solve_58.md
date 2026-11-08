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
  {"benchmark_expand_500:R221": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R221
Molecular formula: C16H16O3
IR bands (cm-1): [2983.0, 2210.0, 1708.0, 1676.0, 1222.0, 771.0]
1H NMR: 7.84 (s, 1H), 7.45-7.37 (m, 5H), 4.33 (q, J = 7.1 Hz, 2H), 3.56 (s, 2H), 2.31 (s, 3H), 1.37 (t, J = 7.1 Hz, 3H)
13C NMR: δ 184.7 (1C, s), 166.6 (1C, s), 141.7 (1C, s), 134.6 (1C, s), 129.4 (1C, s), 129.3 (1C, s), 128.8 (1C, s), 125.9 (1C, s), 90.5 (1C, s), 81.0 (1C, s), 61.4 (1C, s), 32.8 (1C, s), 18.4 (1C, s), 14.3 (1C, s)

### benchmark_expand_500:R222
Molecular formula: C11H11NO
IR bands (cm-1): [2990.0, 2950.0, 1738.0, 1704.0, 1598.0, 1481.0, 1443.0, 1276.0, 1055.0, 755.0]
1H NMR: 9.57 (s, 1H), 7.37-7.33 (m, 2H), 7.19 (d, J = 7.9 Hz, 2H), 7.09-7.06 (m, 1H), 5.41 (s, 1H), 2.73-2.70 (m, 2H), 2.24-2.21 (m, 2H). 13C{1H} NMR (100 MHz, DMSO-d6): δ 203.9, 171.8, 140.4, 129.2, 123.4, 119.9, 100.9, 32.8, 28.4
13C NMR: δ 203.9 (1C, s), 171.8 (1C, s), 140.4 (1C, s), 129.2 (1C, s), 123.4 (1C, s), 119.9 (1C, s), 100.9 (1C, s), 32.8 (1C, s), 28.4 (1C, s)

### benchmark_expand_500:R226
Molecular formula: C11H9F7OS
IR bands (cm-1): [2926.0, 1478.0, 1444.0, 1343.0, 1308.0, 1221.0, 1150.0, 1086.0, 1032.0, 970.0, 970.0, 746.0, 692.0]
1H NMR: 7.61-7.52 (m, 5H), 3.15 (td, J = 12.7, 4.5 Hz, 1H), 2.82 (td, J = 12.7, 4.5 Hz, 1H), 2.69-2.59 (m, 1H), 2.27-2.16 (m, 1H); 13C{1H} NMR (126 MHz, CDCl3): δ 141.8, 131.6, 129.5, 123.8, 120.8 (dq, J = 253.0, 45.1 Hz), 90.9 (dsep, J = 205.8, 31.6 Hz), 47.5, 20.8 (d, J = 21 Hz)
13C NMR: δ 141.8 (1C, s), 131.6 (1C, s), 129.5 (1C, s), 123.8 (1C, s), 120.8 (1C, dq), 90.9 (1C, s), 47.5 (1C, s), 20.8 (1C, d)

### benchmark_expand_500:R227
Molecular formula: C15H27NO
IR bands (cm-1): [2956.0, 2925.0, 2853.0, 2817.0, 1448.0, 1376.0, 1324.0, 1252.0, 1190.0, 1117.0, 1076.0, 1045.0, 1009.0, 947.0, 921.0, 864.0]
1H NMR: 3.78-3.70 (m, 4H), 3.44-3.38 (m, 1H), 2.68-2.63 (m, 2H), 2.51-2.46 (m, 2H), 2.201 (dt, J = 7.2 Hz, 2.0 Hz, 2H), 1.54-1.47 (m, 2H), 1.40-1.36 (m, 2H), 1.32-1.28 (m, 9H), 0.89 (t, J = 6.6 Hz, 3H); 13C{1H} NMR (100 MHz, CDCl3): δ 85.5, 78.1, 67.0, 52.2, 49.4, 31.7, 29.0, 28.8, 28.7, 22.5, 19.2, 18.6, 14.0
13C NMR: δ 85.5 (1C, s), 78.1 (1C, s), 67.0 (1C, s), 52.2 (1C, s), 49.4 (1C, s), 31.7 (1C, s), 29.0 (1C, s), 28.8 (1C, s), 28.7 (1C, s), 22.5 (1C, s), 19.2 (1C, s), 18.6 (1C, s), 14.0 (1C, s)

### benchmark_expand_500:R228
Molecular formula: C12H16N4
IR bands (cm-1): [3288.0, 3065.0, 3029.0, 2975.0, 2930.0, 2874.0, 1639.0]
1H NMR: 1.06 (d, 6H, CH3), 3.39 (m, 1H, CH), 3.82 (s, 2H, CH2-ph), 7.21 (br. s, 1H, NH, D2O exchangeable), 7.22-7.31 (m, 5H, Ar-H, J = 7.26, 7.30 Hz), 7.95 (br. s, 1H, NH, D2O exchangeable)
13C NMR: δ 22.86 (1C, s), 39.84 (1C, s), 42.90 (1C, s), 126.69 (1C, s), 128.62 (1C, s), 129.34 (1C, s), 137.13 (1C, s), 155.40 (1C, s), 169.51 (1C, s)

### benchmark_expand_500:R23
Molecular formula: C15H21NO4
IR bands (cm-1): [3315.0, 2935.0, 2868.0, 1712.0, 1657.0, 1610.0, 1535.0, 1462.0, 1439.0, 1408.0, 1367.0, 1282.0, 1259.0, 1176.0, 1103.0, 1074.0, 1024.0, 962.0, 858.0, 769.0, 725.0, 694.0, 501.0]
1H NMR: 7.98 (d, J = 8.7 Hz, 2H), 7.68 (d, J = 8.7 Hz, 2H), 4.36 (q, J = 7.2 Hz, 2H), 3.59 (t, J = 6.6 Hz, 2H), 2.42 (t, J = 7.6 Hz, 2H), 1.75 (quin, J = 7.6 Hz, 2H), 1.60 (quin, J = 7.1 Hz, 2H), 1.45 (quin, J = 7.1 Hz, 2H), 1.40 (t, J = 7.2 Hz, 3H)
13C NMR: δ 173.20 (1C, s), 166.53 (1C, s), 142.76 (1C, s), 130.16 (1C, s), 124.79 (1C, s), 118.62 (1C, s), 61.40 (1C, s), 60.63 (1C, s), 36.70 (1C, s), 31.70 (1C, s), 25.02 (1C, s), 24.99 (1C, s), 13.64 (1C, s)
