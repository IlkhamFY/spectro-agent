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
  {"benchmark_expand_500:R04": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R04
Molecular formula: C12H10Cl2N4S
IR bands (cm-1): [3315.0, 3248.0, 3088.0, 3069.0, 2946.0, 2860.0, 1593.0, 1543.0, 1430.0]
1H NMR: 7.83 (d, J = 2.5 Hz, H2′), 7.77 (d, J = 8.7 Hz, H5′) 7.59 (s, H3), 7.61-7.59 (m, H6′), 6.69 (br, NH2), 4.26 (t, J = 8.0 Hz, H4″), 3.33 (t, J = 8.0 Hz, H5″)
13C NMR: δ 159.8 (1C, s), 146.8 (1C, s), 140.6 (1C, s), 137.8 (1C, s), 131.6 (1C, s), 131.1 (1C, s), 129.4 (1C, s), 124.6 (1C, s), 123.1 (1C, s), 98.3 (1C, s), 63.6 (1C, s), 32.2 (1C, s)

### benchmark_expand_500:R06
Molecular formula: C27H31NO3
IR bands (cm-1): [3479.0, 1693.0, 2224.0, 1446.0, 758.0, 696.0, 1468.0, 1030.0, 891.0]
1H NMR: 0.57 (3Н, s, СН3-20), 0.97 (2H, m, H-1α,3α), 1.14 (3Н, s, СН3-19), 1.22 (1Н, m, H-5α), 1.43 (1Н, m, Н-2), 1.54-1.67 (2Н, m, Н-11,9), 1.72-1.89 (5H, m, Н-11,6,1β,2,7), 1.93 (1Н, m, Н-6), 2.07 (1Н, dm, J = 13.3 Hz, Н-3β), 2.36 (1Н, m, Н-7), 2.50 (1Н, m, Н-12), 2.75 (1Н, m, Н-12), 4.53, 4.84 (2Н, both s, Н-17), 7.10 (1Н, s, Н-14), 7.30 (1Н, t, J = 7.6 Hz, Н-4′), 7.38 (2Н, m, Н-3′,5′), 7.60 (2Н, d, J = 7.6 Hz, Н-2′, Н-6′)
13C NMR: δ 12.33 (1C, s), 19.58 (1C, s), 23.74 (1C, s), 24.05 (1C, s), 25.84 (1C, s), 28.63 (1C, s), 37.76 (1C, s), 38.31 (1C, s), 38.80 (1C, s), 40.08 (1C, s), 43.66 (1C, s), 55.99 (1C, s), 55.78 (1C, s), 106.07 (1C, s), 118.57 (1C, s), 123.98 (1C, s), 126.03 (1C, s), 127.94 (1C, s), 128.32 (1C, s), 130.08 (1C, s), 144.43 (1C, s), 147.62 (1C, s), 151.00 (1C, s), 161.17 (1C, s), 180.16 (1C, s)

### benchmark_expand_500:R07
Molecular formula: C23H14N2O3
IR bands (cm-1): [2923.0, 1727.0, 1683.0, 1451.0, 1379.0, 1324.0, 1079.0, 701.0]
1H NMR: 7.79 (dd, J = 3.2, 5.6 Hz, 2H), 7.71 (dd, J = 3.2, 5.6 Hz, 2H), 7.67-7.62 (m, 3H), 7.49-7.47 (m, 1H), 7.29-7.26 (m, 5H), 6.81 (s, 1H)
13C NMR: δ 168.3 (1C, s), 166.5 (1C, s), 135.8 (1C, s), 134.6 (1C, s), 134.5 (1C, s), 132.3 (1C, s), 131.4 (1C, s), 129.3 (1C, s), 128.4 (1C, s), 127.4 (1C, s), 125.6 (1C, s), 125.1 (1C, s), 123.8 (1C, s), 123.3 (1C, s), 121.3 (1C, s), 114.8 (1C, s), 109.0 (1C, s)

### benchmark_expand_500:R09
Molecular formula: C17H20N8O2
IR bands (cm-1): [3291.0, 2928.0, 2861.0, 2363.0, 2325.0, 1585.0]
1H NMR: 8.03 (d, 2H, J = 8.7 Hz, Ar-H), 7.90 (s, 2H, Ar-NH-), 7.68 (t, 2H, J = 7.5 Hz, Ar-H), 7.43 (d, 2H, J = 8.4 Hz, Ar-H), 7.25 (t, 2H, J = 7.5 Hz, Ar-H), 3.46 (s, 4H, -CH2CH2CH2-), 1.90 (s,2H, -CH2CH2CH2-)
13C NMR: δ 159.8 (1C, s), 149.0 (1C, s), 136.3 (1C, s), 130.7 (1C, s), 126.5 (1C, s), 125.0 (1C, s), 120.5 (1C, s), 38.6 (1C, s), 28.5 (1C, s)

### benchmark_expand_500:R10
Molecular formula: C13H18O5
IR bands (cm-1): [2900.0, 1760.0, 1740.0, 1440.0]
1H NMR: 3.70 (s, 3H, CO2Me), 2.66 (t, J = 8.6 Hz, 1H), 2.55 (dd, J = 13.9, 8.8 Hz, 1H), 2.05 (dd, J = 13.9, 8.4 Hz, 1H), 1.64 (s, 3H, Me), 1.60 (s, 3H, Me), 1.49 (s, 3H, Me), 1.36 (s, 3H, Me)
13C NMR: δ 201.4 (1C, s), 169.3 (1C, s), 168.4 (1C, s), 80.2 (1C, s), 59.2 (1C, s), 56.4 (1C, s), 53.5 (1C, s), 44.4 (1C, s), 36.5 (1C, s), 28.7 (1C, s), 22.6 (1C, s), 19.8 (1C, s), 18.7 (1C, s)

### benchmark_expand_500:R100
Molecular formula: C20H21N3O5
IR bands (cm-1): [3432.0, 3153.0, 3090.0, 2999.0, 2934.0, 2839.0, 1670.0, 1585.0, 1522.0, 1462.0, 1412.0, 1330.0, 1258.0, 1216.0, 1182.0, 1130.0, 1033.0, 982.0, 839.0, 827.0, 811.0, 652.0, 609.0]
1H NMR: 8.06 (1H, s, H-3″), 7.61 (2H, dd, J = 6.8, 2.1 Hz, H-2‴, H-6‴), 7.21 (2H, s, H-2′, H-6′), 7.02 (2H, dd, J = 6.7, 2.2 Hz, H-3‴, H-5‴), 5.34 (2H, s, H-1″), 3.90 (6H, s, 3′,5′-OCH3), 3.87 (3H, s, 4‴-OCH3), 2.59 (3H, s, H-2) ppm
13C NMR: δ 197.1 (1C, s), 160.0 (1C, s), 153.4 (1C, s), 145.3 (1C, s), 140.9 (1C, s), 133.1 (1C, s), 130.7 (1C, s), 122.3 (1C, s), 121.5 (1C, s), 114.9 (1C, s), 105.8 (1C, s), 66.6 (1C, s), 57.0 (1C, s), 55.8 (1C, s)
