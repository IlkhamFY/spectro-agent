# Blind structure-elucidation task

You are given real experimental spectra (from the published literature) for a set of
organic molecules. For EACH compound you are given the molecular formula (from HRMS),
the IR band list, and the 1H and 13C NMR shift lists. No name, SMILES, or hint is given.

For each compound, propose the 3 most likely structures, best first, as SMILES.

Rules:
  - Use only the spectra provided. Do not use external lookups or tools.
  - Candidates must match the given molecular formula exactly.
  - Order candidates by your own confidence (most likely first).

Return ONLY a JSON object mapping each id to a list of 3 SMILES strings, e.g.:
  {"M001": ["CCO", "COC", "..."], "M002": ["...", "...", "..."], ...}

Compounds:

### M031
Molecular formula: C9H8N2O3
IR bands (cm-1): [3001.0, 2900.0, 1750.0, 1480.0, 1158.0, 1087.0, 1019.0]
1H NMR: 10.00 (brs, 1H, CONH), 8.2 (dd, 1H, J = 7.5 Hz, ArH), 7.8 (dd, 1H, J = 7.2 Hz, ArH), 7.45 (t, 1H, J = 6.7 Hz, ArH), 7.2 (t, 1H, J = 6.5 Hz, ArH)
13C NMR: δ 150.33 (1C, s), 149.21 (1C, s), 140.00 (1C, s), 129.00 (1C, s), 126.11 (1C, s), 121.52 (1C, s), 73.00 (1C, s), 72.81 (1C, s), 72.33 (1C, s), 72.00 (1C, s), 54.69 (1C, s)

### M032
Molecular formula: C9H15NO3S
IR bands (cm-1): [3265.0, 2915.0, 2125.0, 1670.0, 1461.0, 1260.0, 992.0, 872.0, 783.0, 723.0]
1H NMR: 4.73-4.69 (m, 1H, OCHH), 4.86-4.64 (m, 1H, OCHH), 3.28 (s, 3H, SCH3), 2.45 (t, J = 2.5 Hz, CCH), 1.51 (s, 9H, C(CH3)3); 13C{1H} NMR (101 MHz, CDCl3) δ 159.2 (C=O), 78.3 (CCH), 74.5 (CCH), 60.5 (C(CH3)3), 53.3 (OCH2), 32.1 (SCH3), 22.9 (C(CH3)3)
13C NMR: δ 159.2 (1C, s), 78.3 (1C, s), 74.5 (1C, s), 60.5 (1C, s), 53.3 (1C, s), 32.1 (1C, s), 22.9 (1C, s)

### M033
Molecular formula: C10H10N2O
IR bands (cm-1): [3514.0, 3061.0, 2958.0, 2913.0, 1699.0, 1659.0, 1607.0, 1587.0, 1572.0]
1H NMR: 8.56 (d, J = 8.5 Hz, 1H), 8.39 (br, 1H), 7.75-7.70 (m, 1H), 7.06 (t, J = 5.3 Hz, 1H), 6.17 (t, J = 2.8 Hz, 1H), 5.48 (t, J = 2.4 Hz, 1H), 4.11 (t, J = 6.9 Hz, 2H), 2.91-2.86 (m, 2H). Water (1.54)
13C NMR: δ 167.6 (1C, s), 152.2 (1C, s), 147.7 (1C, s), 141.0 (1C, s), 137.8 (1C, s), 119.9 (1C, s), 117.7 (1C, s), 115.1 (1C, s), 44.0 (1C, s), 23.6 (1C, s)

### M034
Molecular formula: C8H7NOS
IR bands (cm-1): [816.0, 884.0, 1589.0, 2161.0, 3373.0]
1H NMR: 2.22 (s, 3H, CH3), 6.65 (s, 1H, OH), 6.79 (H6: d, J = 8.4 Hz, 1H), 7.23 (H5: dd, J = 8.4, 2.8 Hz, 1H), 7.31 (H3: d, J = 2.8 Hz, 1H)
13C NMR: δ 15.7 (1C, s), 112.2 (1C, s), 112.6 (1C, s), 116.6 (1C, s), 127.1 (1C, s), 131.4 (1C, s), 135 (1C, s), 156.5 (1C, s)

### M035
Molecular formula: C13H20N4O4S
IR bands (cm-1): [3337.0, 2953.0, 1547.0, 1519.0, 1428.0]
1H NMR: 8.29 (d, J = 9 Hz, 2H), 8.06 (d, J = 9 Hz, 2H), 4.06-3.84 (m, 2H), 1.19 (d, J = 5.4 Hz, 12H)
13C NMR: δ 153.5 (1C, s), 149.8 (1C, s), 149.2 (1C, s), 127.1 (1C, s), 123.8 (1C, s), 43.6 (1C, s), 22.9 (1C, s)

### M036
Molecular formula: C14H20O2
IR bands (cm-1): [2994.0, 2936.0, 2845.0, 1638.0, 1558.0, 1454.0, 1383.0, 1223.0, 1084.0, 1038.0, 1002.0, 937.0, 837.0, 758.0]
1H NMR: 5.97-5.92 (m, 1H), 5.00 (dq, J = 10.0, 1.9 Hz, 1H), 4.90 (dq, J = 17.5, 2.0 Hz, 1H), 3.66 (s, 3H), 3.64 (s, 3H), 3.43 (dt, J = 4.0 Hz, 1.7 Hz, 2H), 2.19 (s, 9H)
13C NMR: δ 153.2 (1C, s), 153.0 (1C, s), 136.9 (1C, s), 129.3 (1C, s), 128.9 (1C, s), 128.2 (1C, s), 128.1 (1C, s), 114.9 (1C, s), 61.2 (1C, s), 60.3 (1C, s), 31.4 (1C, s), 12.9 (1C, s), 12.8 (1C, s), 12.0 (1C, s)
