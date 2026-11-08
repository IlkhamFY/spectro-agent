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
  {"benchmark_expand_500:R135": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R135
Molecular formula: C16H13NO2
IR bands (cm-1): [3073.0, 3046.0, 2923.0, 2225.0, 1652.0, 1601.0, 1468.0, 1225.0, 1023.0, 812.0, 543.0]
1H NMR: 7.84 (d, J = 8.0 Hz, 1H), 7.76-7.73 (m, 2H), 7.71-7.68 (m, 2H), 7.20 (dd, J = 8.0, 1.6 Hz, 1H), 7.13 (d, J = 1.5 Hz, 1H), 4.00 (s, 3H), 2.64 (s, 3H)
13C NMR: δ 199.2 (1C, s), 159.5 (1C, s), 144.8 (1C, s), 144.7 (1C, s), 132.9 (1C, s), 131.5 (1C, s), 128.2 (1C, s), 128.1 (1C, s), 119.8 (1C, s), 118.8 (1C, s), 112.1 (1C, s), 110.7 (1C, s), 55.9 (1C, s), 32.0 (1C, s)

### benchmark_expand_500:R137
Molecular formula: C9H9FO2
IR bands (cm-1): [2953.0, 1742.0, 1606.0, 1513.0, 1231.0]
1H NMR: 7.33 (dd, J = 8.7, 5.4 Hz, 2 H), 7.03 (t, J = 8.7 Hz, 2 H), 5.06 (s, 2 H), 2.08 (s, 3 H) ppm
13C NMR: δ 170.8 (1C, s), 162.6 (1C, d), 131.8 (1C, d), 130.2 (1C, d), 115.5 (1C, d), 65.6 (1C, s)

### benchmark_expand_500:R14
Molecular formula: C13H27NO
IR bands (cm-1): [2954.0, 2929.0, 2872.0, 1708.0, 1461.0, 1409.0, 1345.0, 1315.0, 1232.0, 1118.0, 1051.0, 935.0, 712.0]
1H NMR: 0.65 (t, J = 7.4 Hz, 3H), 0.86 (t, J = 7.4 Hz, 3H), 0.91 (t, J = 7.4 Hz, 3H), 1.39 (sex, J = 7.4 Hz, 2H), 1.60 (m, 2H,), 1.83, 1.94 (ABq, JAB = 14.3 Hz, Jq = 7.4 Hz, 4H), 2.95 (m, 2H); 13C{1H} NMR (75 MHz; CDCl3, δ): 7.02, 13.65, 22.24, 25.97, 27.14, 27.65, 80.57, 122.45, 159.55, 199.05. 3.2.8
13C NMR: δ 7.02 (1C, s), 13.65 (1C, s), 22.24 (1C, s), 25.97 (1C, s), 27.14 (1C, s), 27.65 (1C, s), 80.57 (1C, s), 122.45 (1C, s), 159.55 (1C, s), 199.05 (1C, s)

### benchmark_expand_500:R141
Molecular formula: C17H24N2O2S
IR bands (cm-1): [3347.0, 3016.0, 2874.0, 1407.0, 1333.0, 1156.0, 1060.0, 1031.0]
1H NMR: 7.24-7.30, 7.32-7.35 (2m, 3H, 2H, Ph), 6.26 (m, 1H, CHPh), 4.60-4.65 (m, 1H, CH2OH), 4.34-4.42 (m, 3H, OCH2(Bu) (2H), CH2OH (1H)), 3.09 (br.s, 1H, OH), 2.09 (s, 3H, Me), 1.79-1.84 (m, 2H, Bu), 1.72 (s, 3H, Me), 1.52-1.58 (m, 2H, Bu), 1.00 (t, J = 7.4 Hz, 3H, CH3, Bu) ppm
13C NMR: δ 157.4 (1C, s), 136.7 (1C, s), 126.9 (1C, s), 127.8 (1C, s), 128.7 (1C, s), 118.8 (1C, s), 120.1 (1C, s), 76.8 (1C, t), 62.8 (1C, t), 60.9 (1C, d), 29.9 (1C, t), 19.0 (1C, t), 13.8 (1C, q), 7.4 (1C, s)

### benchmark_expand_500:R143
Molecular formula: C9H8O
IR bands (cm-1): [3288.0, 2962.0, 2854.0, 2116.0, 1493.0, 1458.0]
1H NMR: 7.55 (2H, d, J = 7.5 Hz, Ph), 7.40(2H, t, J = 7.0 Hz, Ph), 7.34 (1H, t, J = 7.0 Hz, Ph), 5.45 (1H, d, J = 1.5 Hz, -CH(OH)-), 2.67 (1H, d, J = 2.0 Hz, H-C≡C-)
13C NMR: δ 140.0 (1C, s), 128.6 (1C, s), 128.4 (1C, s), 126.6 (1C, s), 83.5 (1C, s), 74.8 (1C, s)

### benchmark_expand_500:R144
Molecular formula: C14H22N2O
IR bands (cm-1): [3318.0, 2964.0, 2931.0, 2865.0, 1627.0, 1594.0, 1508.0, 1424.0, 1324.0, 1236.0, 1141.0, 1052.0, 800.0, 747.0]
1H NMR: 7.18 (d, J = 8.6 Hz, 2H), 7.00 (d, J = 8.3 Hz, 2H), 6.06 (s, 1H), 3.90 (hept, J = 6.9 Hz, 2H), 2.21 (s, 3H), 1.25 (s, 6H), 1.23 (s, 6H)
13C NMR: δ 154.8 (1C, s), 136.7 (1C, s), 132.1 (1C, s), 129.3 (1C, s), 119.8 (1C, s), 45.4 (1C, s), 21.5 (1C, s), 20.7 (1C, s)
