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
  {"benchmark_expand_500:R133": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R133
Molecular formula: C27H32O2
IR bands (cm-1): [3032.0, 2956.0, 2929.0, 2857.0, 1717.0, 1649.0, 1609.0, 1419.0, 1380.0, 1186.0, 944.0, 849.0, 649.0]
1H NMR: 7.76 (d, J = 8.1 Hz, 4H), 7.32 (d, J = 8.1 Hz, 4H), 6.77 (s, 2H), 2.70-2.66 (m, 4H), 1.69-1.61 (m, 4H), 1.36-1.33 (m, 8H), 0.90 (t, J = 6.9 Hz, 6H) ppm
13C NMR: δ 180.5 (1C, s), 163.5 (1C, s), 146.9 (1C, s), 129.2 (1C, s), 128.9 (1C, s), 125.9 (1C, s), 110.7 (1C, s), 35.8 (1C, s), 31.4 (1C, s), 30.8 (1C, s), 22.5 (1C, s)

### benchmark_expand_500:R136
Molecular formula: C14H8ClNO2
IR bands (cm-1): [3327.0, 3279.0, 1763.0, 1742.0, 1620.0, 1506.0, 1474.0, 1452.0, 1367.0, 1349.0, 1308.0, 1272.0, 1258.0, 1220.0, 1194.0, 1160.0, 1122.0, 1090.0, 1012.0, 966.0, 915.0, 842.0, 821.0, 811.0, 753.0, 742.0, 703.0, 655.0, 584.0, 567.0, 541.0, 513.0, 497.0, 460.0, 448.0]
1H NMR: 11.15 (bs, 1H, NH), 7.90 (dd, J = 8.2, 2.0 Hz, 1H, ArH), 7.78 (d, J = 1.9 Hz, 1H, ArH), 7.71-7.67 (m, 2H, ArH), 7.52-7.47 (m, 2H, ArH), 7.00 (d, J = 8.2 Hz, 1H, ArH)
13C NMR: δ 184.3 (1C, s), 159.5 (1C, s), 150.2 (1C, s), 137.6 (1C, s), 136.4 (1C, s), 133.5 (1C, s), 132.3 (1C, s), 128.9 (1C, s), 128.0 (1C, s), 122.5 (1C, s), 118.5 (1C, s), 112.7 (1C, s)

### benchmark_expand_500:R139
Molecular formula: C24H32N8O2S
IR bands (cm-1): [1435.0, 1493.0, 1548.0, 1578.0, 2927.0, 3339.0]
1H NMR: 9.26 (d, J = 44.4 Hz, 3H, NH-SO2 and NH-triazine), 8.04 (d, J = 4.0 Hz, 1H, H-C5‴′), 7.93 (d, J = 8.2 Hz, 1H, H-C2‴′), 7.69 (d, J = 16.1 Hz, 4H, H-C2′/3′/5′/6′), 7.13 (d, J = 8.6 Hz, 1H, H-C4‴′), 6.88 (t, 1H, H-C3‴′), 3.70 (s, 1H, H-C1″), 3.53 (s, 4H, H-C1‴), 2.05-1.50 (m, 4H, H-C2″/6″), 1.21 (d, J = 17.4 Hz, 6H, H-C3″/4″/5″), 1.11 ppm (s, 6H, H-C2‴)
13C NMR: δ 164.7 (1C, s), 163.9 (1C, s), 152.7 (1C, s), 144.7 (1C, s), 139.5 (1C, s), 132.5 (1C, s), 127.4 (1C, s), 118.1 (1C, s), 116.3 (1C, s), 113.1 (1C, s), 49.1 (1C, s), 40.7 (1C, s), 32.5 (1C, s), 25.1 (1C, s)

### benchmark_expand_500:R140
Molecular formula: C27H33ClN4O5
IR bands (cm-1): [3278.0, 2978.0, 2927.0, 1706.0, 1593.0, 1494.0, 1370.0, 1267.0, 1245.0, 1150.0, 1010.0, 973.0, 827.0, 699.0]
1H NMR: 7.51-7.36 (m, 2H), 7.28-7.14 (m, 3H), 7.14-7.07 (m, 2H), 7.06 (m, 2H), 6.85 (br s, 1H), 3.33 (d, J = 12.6 Hz, 1H), 3.03 (d, J = 12.5 Hz, 1H), 2.37 (s, 3H), 1.68-1.46 (m, 9H), 1.45-1.24 (m, 9H) ppm. 13C{1H} NMR (101 MHz, CDCl3) δ 172.1, 160.6, 156.0, 153.0, 137.8, 136.0, 131.3, 129.7 (2C), 129.0, 128.5 (2C), 128.2, 128.1 (2C), 127.8, 125.3, 120.0, 81.9, 39.0, 28.2 (3C), 28.0 (3C), 14.4 ppm
13C NMR: δ 172.1 (1C, s), 160.6 (1C, s), 156.0 (1C, s), 153.0 (1C, s), 137.8 (1C, s), 136.0 (1C, s), 131.3 (1C, s), 129.7 (1C, s), 129.0 (1C, s), 128.5 (1C, s), 128.2 (1C, s), 128.1 (1C, s), 127.8 (1C, s), 125.3 (1C, s), 120.0 (1C, s), 81.9 (1C, s), 39.0 (1C, s), 28.2 (1C, s), 28.0 (1C, s)

### benchmark_expand_500:R142
Molecular formula: C15H14Cl2N6O3
IR bands (cm-1): [3385.0, 3251.0, 1732.0, 1675.0, 1544.0, 1474.0, 1381.0, 1216.0, 1102.0, 1014.0, 813.0, 710.0, 643.0, 573.0, 479.0, 426.0]
1H NMR: 8.33 (d, 1JC-H = 192.1 Hz, 1H, HC=N), 8.01 (d, J = 9.0 Hz, 1CH), 7.83 (br. s, 1H, NH), 7.61 (d, J = 2.3 Hz, 1CH), 7.39 (dd, J = 9.0, 2.3 Hz, 1CH), 5.41 (br. s, 2H, NH2), 4.77 (d, 1JC-H = 143.0 Hz, 2H, NCH2), 4.16 (q, J = 7.1 Hz, 2H, OCH2), 1.21 (t, J = 7.1 Hz, 3H, Me) ppm
13C NMR: δ 168.4 (1C, s), 146.4 (1C, s), 144.0 (1C, s), 137.3 (1C, s), 130.6 (1C, s), 129.0 (1C, s), 128.0 (1C, s), 124.7 (1C, s), 122.1 (1C, s), 120.0 (1C, s), 119.5 (1C, s), 119.4 (1C, s), 61.3 (1C, s), 52.2 (1C, s)

### benchmark_expand_500:R145
Molecular formula: C16H12BrN3O
IR bands (cm-1): [3462.0, 3376.0, 3336.0, 3231.0, 3186.0, 3066.0, 2192.0, 1640.0, 1512.0, 1413.0, 1173.0, 1126.0, 1036.0]
1H NMR: 7.39 (d, J = 7.9 Hz, 1H, Hg), 7.31-7.24 (m, 2H, Hf, He), 7.19 (s, 1H, Hh), 6.86 (s, 2H, NH, OH), 6.65 (d, J = 8.5 Hz, 1H, Hc), 6.32-6.28 (m, 1H, Hb), 6.24 (d, J = 2.1 Hz, 1H, Ha), 5.28 (s, 2H, NH2), 4.58 (s, 1H, Hd)
13C NMR: δ 161.0 (1C, s), 150.0 (1C, s), 149.5 (1C, s), 149.4 (1C, s), 131.3 (1C, s), 130.4 (1C, s), 129.9 (1C, s), 127.0 (1C, s), 122.3 (1C, s), 121.2 (1C, s), 111.7 (1C, s), 109.7 (1C, s), 100.4 (1C, s), 56.3 (1C, s)
