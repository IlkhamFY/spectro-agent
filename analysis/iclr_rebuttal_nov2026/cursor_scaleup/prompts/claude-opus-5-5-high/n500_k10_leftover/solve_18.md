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
  {"benchmark_expand_500:R181": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R181
Molecular formula: C23H30BrNO5
IR bands (cm-1): [989.0, 978.0, 898.0, 771.0, 664.0, 608.0, 512.0, 467.0, 445.0]
1H NMR: 1.84 (s, 3H), 3.41 (m, 1H), 3.80 (s, 3H), 3.84 (s, 9H), 3.91 (m, 1H), 3.95 (d, 1H, J =13.7 Hz), 4.19 (d, 1H, J =13.7 Hz), 4.39 (m, 1H), 4.72 (dd, 2H, J =7.9, 15.2 Hz), 4.89 (d, 1H, J =14.4 Hz), 5.78 (d, 1H, J =15.4), 6.86 (s, 1H), 6.90 (s, 1H), 6.91 (s, 1H), 7.0 (s, 1H)
13C NMR: δ 17.90 (1C, s), 23.51 (1C, s), 42.42 (1C, s), 54.46 (1C, s), 55.29 (1C, s), 55.31 (1C, s), 55.98 (1C, s), 64.07 (1C, s), 66.33 (1C, s), 67.12 (1C, s), 74.83 (1C, s), 105.62 (1C, s), 105.74 (1C, s), 109.81 (1C, s), 111.48 (1C, s), 123.68 (1C, s), 123.70 (1C, s), 124.96 (1C, s), 125.49 (1C, s), 148.49 (1C, s), 149.84 (1C, s), 150.39 (1C, s), 150.49 (1C, s)

### benchmark_expand_500:R183
Molecular formula: C22H24N4O2S
IR bands (cm-1): [3049.0, 2950.0, 2867.0, 1679.0, 1592.0, 1248.0]
1H NMR: 0.89-0.94 (t, 3H, J = 9 Hz, CH3), 1.24-1.41 (m, 4H, 2 CH2), 1.73-1.75 (m, 2H, CH2), 2.67 (s, 3H, COCH3), 4.01-4.05 (t, 2H, J = 6 Hz, CH2-O), 7.00-7.70 (m, 9H, Ar-H), 8.40 (s, 1H, CHN) ppm
13C NMR: δ 14.4 (1C, s), 21.4 (1C, s), 22.6 (1C, s), 28.2 (1C, s), 28.8 (1C, s), 68.1 (1C, s), 113.7 (1C, s), 116.9 (1C, s), 120.2 (1C, s), 127.1 (1C, s), 130.5 (1C, s), 131.6 (1C, s), 135.8 (1C, s), 136.5 (1C, s), 148.7 (1C, s), 150.4 (1C, s), 154.7 (1C, s), 159.4 (1C, s), 165.5 (1C, s)

### benchmark_expand_500:R184
Molecular formula: C22H19NO5
IR bands (cm-1): [442.0, 600.0, 581.0, 752.0]
1H NMR: 8.13 (s, 1H), 7.64 (d, J = 7.8 Hz, 1H), 7.61 (d, J = 8.4 Hz, 1H), 7.55-7.50 (m, 1H), 7.36-7.31 (m, 1H), 7.29 (s, 2H), 3.96 (s, 3H), 3.95 (s, 6H), 2.52 (s, 3H)
13C NMR: δ 186.84 (1C, s), 156.02 (1C, s), 152.97 (1C, s), 146.69 (1C, s), 142.81 (1C, s), 137.35 (1C, s), 130.85 (1C, s), 129.76 (1C, s), 128.75 (1C, s), 123.80 (1C, s), 121.17 (1C, s), 117.63 (1C, s), 112.40 (1C, s), 107.06 (1C, s), 105.62 (1C, s), 61.04 (1C, s), 56.37 (1C, s), 9.29 (1C, s)

### benchmark_expand_500:R186
Molecular formula: C26H42N4O2
IR bands (cm-1): [3186.0, 1795.0, 1635.0, 1188.0, 1105.0, 863.0, 742.0]
1H NMR: 7.18 (d, J = 8.7 Hz, 2H), 3.79 (d, J = 10.6 Hz, 2H), 2.60 (s, 4H), 2.28 (s, 6H), 2.00 (d, J = 11.6 Hz, 2H), 1.84-1.60 (m, 6H), 1.44-1.13 (m, 20H)
13C NMR: δ 182.78 (1C, s), 168.77 (1C, s), 68.01 (1C, s), 52.24 (1C, s), 51.13 (1C, s), 48.88 (1C, s), 34.41 (1C, s), 24.33 (1C, s), 23.82 (1C, s), 23.10 (1C, s), 22.74 (1C, s), 21.62 (1C, s)

### benchmark_expand_500:R188
Molecular formula: C10H8N2O2
IR bands (cm-1): [642.0, 754.0, 797.0, 974.0, 1103.0, 1319.0, 1425.0, 1470.0, 1516.0, 1618.0, 2367.0, 3402.0, 3746.0]
1H NMR: 12.25 (s, 1H, NH), 8.42 (d, J = 13.2 Hz, 1H, CH), 8.25 (s, 1H, ArH), 8.02 (d, J = 13.8 Hz, 1H, CH), 7.96 (d, J = 7.8 Hz, 1H, ArH), 7.54 (d, J = 3.9 Hz, 1H, ArH), 7.30-7.27 (m, 1H, ArH), 7.26-7.23 (m, 1H, ArH)
13C NMR: δ 138.2 (1C, s), 136.7 (1C, s), 135.2 (1C, s), 131.6 (1C, s), 125.1 (1C, s), 123.8 (1C, s), 122.4 (1C, s), 120.9 (1C, s), 113.3 (1C, s), 108.7 (1C, s)

### benchmark_expand_500:R192
Molecular formula: C17H15N3O
IR bands (cm-1): [3356.0, 3259.0, 3089.0, 1672.0]
1H NMR: 2.39 (s, 3H, H3C), 6.90 (m, 2H, H-3′, 5′), 7.17 (s, 2H, H2N), 7.33-7.37 (m, 3H, ArH), 7.79 (s, 1H, ArH), 8.15 (d, 2H, J = 12.6 Hz, ArH), 8.21 (d, 1H, J = 12.6 Hz, ArH), 14.03 (s, 1H, HO)
13C NMR: δ 20.97 (1C, s), 99.49 (1C, s), 117.55 (1C, s), 118.05 (1C, s), 118.62 (1C, s), 127.10 (1C, s), 128.01 (1C, s), 129.24 (1C, s), 132.58 (1C, s), 134.20 (1C, s), 140.68 (1C, s), 160.34 (1C, s), 165.07 (1C, s), 165.23 (1C, s)
