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
  {"benchmark_expand_500:R24": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R24
Molecular formula: C11H15NO2
IR bands (cm-1): [3357.0, 2873.0, 1606.0, 1585.0, 1489.0, 1373.0, 1311.0, 1293.0, 1159.0, 1107.0, 964.0, 931.0, 750.0]
1H NMR: 6.26 (dd, J = 8.0, 1.4 Hz, 1H), 6.77 (dt, J = 7.5, 1.2 Hz, 1H), 6.70 (t, J = 7.8 Hz, 1H), 5.43 (brs, 2H), 5.23 (ddd, J = 11.2, 6.1, 5.1 Hz, 1H), 4.97 (ddd, J = 7.2, 6.1, 1.0 Hz, 2H), 4.88-4.79 (m, 2H), 2.29 (s, 3H); 13C{1H} NMR (101 MHz, CDCl3) δ 145.0, 131.7, 123.8 (2C), 119.7, 109.2 (2C), 78.2 (2C), 70.8, 17.6
13C NMR: δ 145.0 (1C, s), 131.7 (1C, s), 123.8 (1C, s), 119.7 (1C, s), 109.2 (1C, s), 78.2 (1C, s), 70.8 (1C, s), 17.6 (1C, s)

### benchmark_expand_500:R28
Molecular formula: C8H7N3O
IR bands (cm-1): [3064.0, 2900.0, 2197.0, 1691.0, 1589.0, 1446.0, 1213.0, 998.0, 907.0, 809.0, 752.0, 686.0, 622.0]
1H NMR: 7.91 (dd, J = 8.4, 1.2 Hz, 2H), 7.65-7.61 (m, 1H), 7.52-7.49 (m, 2H), 4.57 (s, 2H)
13C NMR: δ 193.25 (1C, s), 134.38 (1C, s), 134.15 (1C, s), 129.00 (1C, s), 127.92 (1C, s), 54.88 (1C, s)

### benchmark_expand_500:R29
Molecular formula: C13H13NO2
IR bands (cm-1): [3379.0, 1601.0, 1526.0, 1504.0, 1459.0, 1291.0, 1239.0, 1174.0, 1110.0, 1027.0, 735.0]
1H NMR: 3.79 (s, 3H, CH3O), 6.50 (br s, 1H, NH), 6.28 (ddd, J = 8.0, 2.4, 0.6 Hz, 1H, H-4), 6.37 (t, J = 2.4 Hz, 1H, H-2), 6.44 (ddd, J = 8.0, 2.4, 0.6 Hz, 1H, H-6), 6.82-6.89 (m, 2H, H-3′), 7.04 (t, J = 8.0 Hz, 1H, H-5), 7.04-7.10 (m, 2H, H-2′)
13C NMR: δ 55.5 (1C, s), 101.9 (1C, s), 106.3 (1C, s), 108.0 (1C, s), 114.6 (1C, s), 122.9 (1C, s), 130.3 (1C, s), 135.1 (1C, s), 146.9 (1C, s), 155.4 (1C, s), 156.7 (1C, s)

### benchmark_expand_500:R32
Molecular formula: C13H13NO5
IR bands (cm-1): [1732.0, 1711.0, 1608.0, 1529.0, 1464.0, 844.0]
1H NMR: 0.9 (t, J = 7.1 Hz, 3H) (methyl), 1.3 (s, 3H) (acetyl), 2.8 (q, J = 7.1 Hz, 2H) (methylene), 6.1 (s, 1H) (methyne), 7.68-7.62 (m, 2H) (aromatic), 7.95-7.89 (m, 2H) (aromatic)
13C NMR: δ 15 (1C, s), 30 (1C, s), 45 (1C, s), 125 (1C, s), 130 (1C, s), 145 (1C, s), 165 (1C, s), 175 (1C, s), 200 (1C, s)

### benchmark_expand_500:R33
Molecular formula: C13H13F3N2S
IR bands (cm-1): [3030.0, 2959.0, 2929.0, 1572.0, 1494.0, 1453.0, 1401.0, 1148.0, 1092.0]
1H NMR: 7.33-7.27 (m, 3H), 6.93-6.92 (m, 2H), 5.30 (s, 2H), 2.23 (s, 3H), 2.04 (s, 3H). 13C{1H} NMR (151 MHz, CDCl3): δ 138.3, 136.0, 129.3, 129.1, 128.2 (q, 1JC-F = 312.2 Hz), 128.0, 126.5 (q, 3JC-F = 2.8 Hz), 126.1, 48.6, 13.1, 9.9
13C NMR: δ 138.3 (1C, s), 136.0 (1C, s), 129.3 (1C, s), 129.1 (1C, s), 128.2 (1C, q), 128.0 (1C, s), 126.5 (1C, q), 126.1 (1C, s), 48.6 (1C, s), 13.1 (1C, s), 9.9 (1C, s)

### benchmark_expand_500:R34
Molecular formula: C18H23NO3
IR bands (cm-1): [3079.0, 3024.0, 2974.0, 2932.0, 2857.0, 1779.0, 1697.0, 1455.0, 1385.0, 1350.0, 1240.0, 1211.0, 1196.0, 1101.0, 913.0, 703.0]
1H NMR: 1.23 (d, J = 6.88 Hz, 3H), 1.43 (m, 3H), 1.76 (m, 1H), 2.01 (m, 2H), 2.77 (dd, J = 13.2, 9.5 Hz, 1H), 3.27 (dd, J = 13.3, 3.1 Hz, 1H), 3.72 (m, 1H), 4.19 (m, 2H), 4.67 (m, 1H), 4.95 (m, 1H), 5.01 (dq, J = 17.2, 1.7 Hz, 1H), 5.79 (m, 1H), 7.19-7.36 (m, 5H)
13C NMR: δ 17.5 (1C, s), 26.6 (1C, s), 33.0 (1C, s), 33.8 (1C, s), 37.7 (1C, s), 38.0 (1C, s), 55.5 (1C, s), 66.1 (1C, s), 114.8 (1C, s), 127.5 (1C, s), 129.0 (1C, s), 129.6 (1C, s), 135.4 (1C, s), 138.6 (1C, s), 153.2 (1C, s), 177.3 (1C, s)
