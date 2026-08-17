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

### M055
Molecular formula: C10H10F3I
IR bands (cm-1): [3100.0, 3400.0, 1450.0, 1330.0, 1164.0, 1126.0, 1074.0, 797.0, 702.0]
1H NMR: 2.14 (quintet, 2H, -CH2), 2.80 (t, J = 7.3, 2H, -CH2), 3.41 (t, J = 6.6, 2H, -CH2), 7.39-7.49 (m, 4H, ArH)
13C NMR: δ 141.34 (1C, s), 132.01 (1C, s), 131.02 (1C, q), 128.97 (1C, s), 125.53 (1C, s), 123.26 (1C, s), 36.02 (1C, s), 34.55 (1C, s), 5.72 (1C, s)

### M056
Molecular formula: C16H22N2O4
IR bands (cm-1): [976.0, 939.0, 841.0, 788.0, 731.0, 607.0, 575.0, 528.0, 479.0, 455.0, 897.0, 853.0, 787.0, 749.0, 712.0]
1H NMR: 7.88 (dd, J1 = 8.3 Hz, J2 = 1.4 Hz, 1H), 7.77 (dd, J1 = 8.3 Hz, J2 = 0.9 Hz, 1H), 7.55-7.59 (m, 1H), 7.33-7.38 (m, 1H), 3.33 (d, J = 10.1 Hz, 1H), 3.02 (d, J = 5.5 Hz, 1H), 2.90-2.96 (m, 1H), 2.82 (d, J = 10.1 Hz, 1H), 2.55 (q, J = 8.6 Hz, 1H), 2.42 (s, 3H), 2.18 (s, 1H), 1.37 (s, 9H) ppm
13C NMR: δ 172.65 (1C, s), 148.21 (1C, s), 139.93 (1C, s), 133.05 (1C, s), 129.01 (1C, s), 127.17 (1C, s), 124.70 (1C, s), 81.75 (1C, s), 67.17 (1C, s), 57.22 (1C, s), 56.44 (1C, s), 41.84 (1C, s), 38.56 (1C, s)

### M057
Molecular formula: C10H11ClN2O
IR bands (cm-1): [3246.0, 1688.0, 1543.0, 1355.0, 1303.0, 1236.0, 1024.0, 935.0, 817.0, 630.0, 589.0, 509.0, 490.0]
1H NMR: 8.44 (broad s, 1H, NH), 7.16 (d, J = 8.4 Hz, 2H, Ar-H), 7.13 (d, J = 8.4 Hz, 2H, Ar-H), 2.56 (s, 3H, C(O)-CH3), 2.33 (s, 3H, CH3-p-tolyl)
13C NMR: δ 188.3 (1C, s), 139.0 (1C, s), 133.2 (1C, s), 130.0 (1C, s), 124.6 (1C, s), 114.4 (1C, s)

### M058
Molecular formula: C13H12Br2N2O2S
IR bands (cm-1): [3440.0, 3356.0, 3255.0, 1614.0, 1597.0, 1478.0, 1317.0, 1154.0, 812.0, 664.0]
1H NMR: 7.64 (d, J = 7.63 Hz, 2H), 7.31 (d, J = 7.78 Hz, 2H), 7.02 (s, 1H), 6.66 (s, 1H), 5.93 (bs, 1H), 4.16 (bs, 2H), 2.46 (s, 3H)
13C NMR: δ 144.8 (1C, s), 144.6 (1C, s), 135.1 (1C, s), 132.7 (1C, s), 129.8 (1C, s), 127.5 (1C, s), 124.7 (1C, s), 121.1 (1C, s), 121.0 (1C, s), 111.1 (1C, s), 21.6 (1C, s)

### M059
Molecular formula: C17H26N2O3
IR bands (cm-1): [3319.0, 3075.0, 2968.0, 2931.0, 1690.0, 1649.0, 1528.0, 1168.0]
1H NMR: 7.30-7.25 (m, 2H), 7.23-7.20 (m, 3H), 6.94 (br, 1H), 5.32 (d, J = 8.65 Hz, 1H), 4.45-4.41 (m, 1H), 4.34-4.30 (m, 1H), 3.97 (t, J = 7.75 Hz, 1H), 2.10-2.05 (m, 1H), 1.38 (s, 9H), 0.93 (d, J = 6.70 Hz, 3H), 0.89 (d, J = 6.70 Hz, 3H)
13C NMR: δ 172.0 (1C, s), 156.2 (1C, s), 138.2 (1C, s), 128.7 (1C, s), 127.7 (1C, s), 127.6 (1C, s), 127.5 (1C, s), 79.9 (1C, s), 60.2 (1C, s), 43.4 (1C, s), 31.0 (1C, s), 28.5 (1C, s), 19.5 (1C, s), 18.2 (1C, s)

### M060
Molecular formula: C14H12N2O2
IR bands (cm-1): [3068.0, 3047.0, 2980.0, 1726.0, 1307.0, 1286.0, 1140.0, 1055.0, 1025.0, 974.0, 948.0, 781.0, 756.0, 700.0]
1H NMR: 6.46 (1H, d, J= 9.56 Hz), 7.23-7.27 (2H, m), 7.59 (1H, d, J= 8.8 Hz), 7.75 (1H, d, J= 9.6 Hz), 8.84 (1H, m), 8.89 (1H, d, J= 2.4 Hz), 9.48 (1H, d, J= 1.2 Hz)
13C NMR: δ 65.87 (1C, s), 121.01 (1C, s), 125.72 (1C, s), 127.31 (1C, s), 127.61 (1C, s), 134.79 (1C, s), 134.88 (1C, s), 142.42 (1C, s), 143.42 (1C, s), 145.35 (1C, s), 146.70 (1C, s), 162.74 (1C, s)
