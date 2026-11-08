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
  {"benchmark_expand_500:R146": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R146
Molecular formula: C25H18N4O5
IR bands (cm-1): [3024.0, 1717.0, 1609.0, 1527.0, 1453.0, 1330.0]
1H NMR: 8.15 (d, J = 8.0 Hz, 1H), 7.80 (s, 1H, H4 coumarin), 7.77 (s, 1H, triazole), 7.67 (d, J = 8.0 Hz, 2H), 7.63 (dd, J = 7.5, 7.0 Hz, 1H), 7.55-7.50 (m, 3H, benzyl), 7.36 (d, J = 8.0 Hz, 1H), 7.29 (dd, J = 8.0, 7.0 Hz, 1H), 7.12 (d, J = 8.0 Hz, 1H), 7.06 (d, J = 8.0 Hz, 2H), 5.96 (s, 2H, OCH2), 5.29 (s, 2H, NCH2)
13C NMR: δ 160.7 (1C, s), 158.7 (1C, s), 153.4 (1C, s), 150.8 (1C, s), 144.6 (1C, s), 138.8 (1C, s), 138.7 (1C, s), 134.5 (1C, s), 131.1 (1C, s), 130.6 (1C, s), 130.0 (1C, s), 127.8 (1C, s), 127.7 (1C, s), 125.5 (1C, s), 125.4 (1C, s), 124.5 (1C, s), 123.9 (1C, s), 123.8 (1C, s), 119.8 (1C, s), 116.4 (1C, s), 114.9 (1C, s), 62.1 (1C, s), 50.9 (1C, s)

### benchmark_expand_500:R147
Molecular formula: C20H31NO7
IR bands (cm-1): [2957.0, 2925.0, 2857.0, 2827.0, 1726.0, 1470.0, 1153.0, 1005.0]
1H NMR: 7.49 (1H, s), 5.26 (2H, s), 5.16 (1H, d, J = 7.2 Hz), 5.07 (1H, d, J = 6.8 Hz), 4.61 (1H, d, J = 1.2 Hz), 4.27 (1H, ddd, J = 1.2, 6.0, 7.6 Hz), 4.00 (2H, s), 3.61 (3H, s), 3.50 (3H, s), 3.32 (3H, s), 2.59 (1H, br-s), 2.03 (1H, m), 1.82 (1H, m), 1.57 (1H, m), 1.43 (1H, m), 1.40-1.25 (1H, overlapped), 0.91 (3H, t, J = 6.8 Hz)
13C NMR: δ 162.6 (1C, s), 152.6 (1C, s), 150.5 (1C, s), 128.1 (1C, s), 120.0 (1C, s), 119.0 (1C, s), 102.4 (1C, s), 95.4 (1C, s), 81.2 (1C, s), 68.5 (1C, s), 57.9 (1C, s), 57.2 (1C, s), 56.8 (1C, s), 42.5 (1C, s), 32.0 (1C, s), 30.9 (1C, s), 30.0 (1C, s), 25.2 (1C, s), 22.9 (1C, s), 14.4 (1C, s)

### benchmark_expand_500:R148
Molecular formula: C20H18BrN5O2S
IR bands (cm-1): [3376.0, 2923.0, 1593.0, 1477.0, 1331.0, 827.0, 621.0]
1H NMR: 12.22 (d, 1H, J = 2.2 Hz), 8.09 (s, 1H), 7.98 (d, 1H, J = 8.0 Hz), 7.96-7.94 (m, 2H), 7.89-7.86 (m, 2H), 7.52-7.49 (m, 2H), 7.40-7.37 (m, 4H), 7.25 (d, 1H, J = 2.0 Hz), 5.45 (quint., 1H, J = 7.2 Hz), 1.53 (d, 3H, J = 7.0 Hz)
13C NMR: δ 155.2 (1C, s), 152.4 (1C, s), 151.9 (1C, s), 145.0 (1C, s), 142.2 (1C, s), 134.8 (1C, s), 132.0 (1C, s), 131.1 (1C, s), 128.3 (1C, s), 126.4 (1C, s), 124.6 (1C, s), 119.4 (1C, s), 104.0 (1C, s), 98.2 (1C, s), 48.4 (1C, s), 22.7 (1C, s)

### benchmark_expand_500:R149
Molecular formula: C24H23N3O3
IR bands (cm-1): [3393.0, 2961.0, 2578.0, 1659.0, 1636.0, 1548.0, 1486.0, 1446.0, 1407.0, 1333.0, 1217.0, 1160.0, 1126.0, 1042.0, 978.0]
1H NMR: 1.16 (d, 6H, J = 6.8 Hz, -CH(CH3)2), 2.23 (s, 3H, Ar-CH3), 3.09 (hept, 1H, J = 6.8 Hz, -CH(CH3)2), 6.82 (s, 1H, H-t), 6.87 (d, 2H, J = 8.0 Hz, aromatic protons), 7.98 (t, 1H, J = 6.6 Hz, H-b), 7.03 (t, 1H, J = 7.2 Hz, aromatic proton), 7.33 (t, 2H, J = 7.7 Hz, aromatic protons), 7.47 (t, 1H, J = 7.8 Hz, H-c), 8.10 (d, 1H, J = 8.7 Hz, H-d), 8.31 (s, 1H, H-q), 8.58 (d, 1H, J = 6.6 Hz, H-a), 8.98 (s, 1H, -NH), 13.01 (v br s, 1H, -OH)
13C NMR: δ 17.0 (1C, s), 23.0 (1C, s), 26.6 (1C, s), 89.5 (1C, s), 112.9 (1C, s), 116.4 (1C, s), 117.1 (1C, d), 119.1 (1C, s), 122.1 (1C, s), 122.2 (1C, s), 126.2 (1C, s), 127.7 (1C, s), 129.0 (1C, s), 129.9 (1C, s), 134.2 (1C, s), 137.6 (1C, s), 141.5 (1C, s), 147.5 (1C, s), 158.5 (1C, s), 160.8 (1C, s), 162.1 (1C, h)

### benchmark_expand_500:R15
Molecular formula: C24H20Cl2N4O3S2
IR bands (cm-1): [3230.0, 2920.0, 1683.0, 1634.0, 1575.0, 1487.0, 1344.0, 1144.0]
1H NMR: 2.16 (s, 3H, CH3Ph), 2.43 (s, 3H, CH3), 4.33 (s, 2H, SCH2), 7.29-7.30 (d, J = 7.8 Hz, 2H, arom.), 7.43-7.47 (m, 3H, H-3, arom.), 7.72 (s, 1H, H-6), 7.90-8.02 (m, 3H, H-5, H-6, H-7 phthalazine), 8.26-8.28 (d, J = 7.8 Hz, 1H, H-8 phthalazine), 8.92 (s, 1H, C=NH), 9.27 (s, 1H, SO2NH)
13C NMR: δ 19.1 (1C, s), 19.5 (1C, s), 36.5 (1C, s), 126.8 (1C, s), 127.1 (1C, s), 127.5 (1C, s), 129.0 (1C, s), 129.3 (1C, s), 129.9 (1C, s), 131.4 (1C, s), 131.7 (1C, s), 132.5 (1C, s), 133.0 (1C, s), 133.2 (1C, s), 135.1 (1C, s), 136.1 (1C, s), 136.5 (1C, s), 137.9 (1C, s), 138.9 (1C, s), 144.9 (1C, s), 155.0 (1C, s), 157.9 (1C, s)

### benchmark_expand_500:R150
Molecular formula: C19H20O5
IR bands (cm-1): [3004.0, 2931.0, 2831.0, 2038.0, 1980.0, 1699.0, 1627.0, 1594.0, 1512.0, 1461.0, 1419.0, 1301.0, 1237.0, 1132.0, 1020.0, 978.0, 806.0, 763.0, 603.0, 558.0, 522.0]
1H NMR: 3.81 (s, 3H), 3.88 (s, 3H), 3.89 (s, 3H), 5.17 (s, 2H), 6.33 (d, 1H, Jtrans = 15.9 Hz), 6.84 (d,1H, J = 8.4 Hz), 6.90 (d, 2H, J = 8.7 Hz), 7.03 (d, 1H, J = 2.1 Hz), 7.08 (dd, 1H, J = 2.1 Hz, J = 8.4 Hz), 7.35 (d, 2H, J = 8.7 Hz), 7.64 (d, 1H, Jtrans = 15.9 Hz)
13C NMR: δ 55.3 (1C, s), 55.8 (1C, s), 55.9 (1C, s), 66.1 (1C, s), 109.6 (1C, s), 111.0 (1C, s), 114.0 (1C, s), 115.7 (1C, s), 122.6 (1C, s), 127.4 (1C, s), 128.3 (1C, s), 130.1 (1C, s), 144.9 (1C, s), 149.2 (1C, s), 151.1 (1C, s), 159.6 (1C, s), 167.1 (1C, s)
