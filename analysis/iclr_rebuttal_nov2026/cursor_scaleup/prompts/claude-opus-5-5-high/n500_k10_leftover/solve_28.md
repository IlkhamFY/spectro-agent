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
  {"benchmark_main:R09": ["CCO", "COC"]}

Compounds:

### benchmark_main:R09
Molecular formula: C18H20BrN3
IR bands (cm-1): [3280.0, 2946.0, 2914.0, 1610.0, 1501.0, 1461.0, 1363.0, 1341.0, 1231.0, 1067.0, 716.0]
1H NMR: 8.33 (s, 1H), 7.77 (d, J = 8.1 Hz, 2H), 7.42 (d, J = 9.4 Hz, 1H), 7.23 (d, J = 7.9 Hz, 2H), 7.17 (d, J = 9.4 Hz, 1H), 3.15 (s, 1H), 2.39 (s, 3H), 1.04 (s, 9H)
13C NMR: δ 140.44 (1C, s), 140.24 (1C, s), 137.44 (1C, s), 131.72 (1C, s), 129.08 (1C, s), 127.96 (1C, s), 127.29 (1C, s), 123.67 (1C, s), 123.63 (1C, s), 117.85 (1C, s), 106.23 (1C, s), 56.53 (1C, s), 30.31 (1C, s), 21.34 (1C, s)

### benchmark_main:R103
Molecular formula: C16H17N3O4
IR bands (cm-1): [2975.0, 2802.0, 2112.0, 1703.0, 1635.0, 1565.0, 1512.0, 1400.0, 1387.0, 1212.0, 1100.0, 1052.0, 998.0, 957.0, 888.0, 765.0, 745.0, 677.0]
1H NMR: 1.72 (s, 6H, 2 × C-CH3), 2.60 (d, J = 0.9 Hz, 1H, CH≡C), 3.89 (s, 3H, OMe), 3.93 (s, 3H, CO2Me), 6.91 (s, 1H, CH=C), 7.33 (dd, J = 8.5, 1.9 Hz, 1H, H6′), 7.45 (d, J = 8.5 Hz, 1H, H5′), 7.52 (d, J = 1.9 Hz, 1H, H2′)
13C NMR: δ 29.4 (1C, s), 52.8 (1C, s), 55.9 (1C, s), 73.9 (1C, s), 73.9 (1C, s), 113.9 (1C, s), 121.5 (1C, s), 123.8 (1C, s), 123.9 (1C, s), 125.7 (1C, s), 128.5 (1C, s), 146.1 (1C, s), 152.0 (1C, s), 164.1 (1C, s)

### benchmark_main:R104
Molecular formula: C21H20N4O
IR bands (cm-1): [3136.0, 1598.0, 1498.0, 835.0]
1H NMR: 11.80 (s, 1H), 9.60 (s, 1H), 8.01 (s, 1H), 7.62 (d, J = 8.3 Hz, 1H), 7.61-7.56 (m, 2H), 7.33-7.26 (m, 2H), 7.10 (m, 2H), 6.87 (d, J = 2.2 Hz, 1H), 6.85-6.79 (m, 2H), 5.44 (p, J = 7.2 Hz, 1H), 2.25 (s, 3H), 1.50 (d, J = 7.0 Hz, 3H)
13C NMR: δ 156.9 (1C, s), 154.3 (1C, s), 151.1 (1C, s), 142.6 (1C, s), 135.3 (1C, s), 134.0 (1C, s), 128.7 (1C, s), 126.02 (1C, s), 125.97 (1C, s), 123.0 (1C, s), 115.7 (1C, s), 103.7 (1C, s), 94.6 (1C, s), 48.4 (1C, s), 22.9 (1C, s), 20.6 (1C, s)

### benchmark_main:R105
Molecular formula: C23H20BrN3O2S
IR bands (cm-1): [3364.0, 3179.0, 3075.0, 1677.0]
1H NMR: 10.09 (s, 1H, Ar-NH=N), 7.97 (s, 1H, Pyrroline-1-H), 7.77 (d, J = 8.1 Hz, 2H, Ar(4-CH3)-2,6-2H), 7.42 (d, J = 8.7 Hz, 3H, Thiophene-3,5-2H, Ar(4-Br)-3-H), 7.31 (d, J = 5.0 Hz, 1H, Ar(4-Br)-5-H), 7.21 (t, J = 8.1 Hz, 4H, Thiophene-4-H, Ar(4-CH3)-3,5-2H, Ar(4-Br)-2-H), 6.96-6.90 (m, 1H, Ar(4-Br)-6-H), 5.38 (s, 2H, CH2), 4.37 (s, 2H, Pyrroline-5-2H), 2.32 (s, 3H, CH3)
13C NMR: δ 171.95 (1C, s), 166.92 (1C, s), 145.02 (1C, s), 137.89 (1C, s), 137.70 (1C, s), 134.65 (1C, s), 132.62 (1C, s), 132.25 (1C, s), 129.53 (1C, s), 126.77 (1C, s), 125.94 (1C, s), 124.61 (1C, s), 124.06 (1C, s), 115.40 (1C, s), 111.25 (1C, s), 103.82 (1C, s), 61.82 (1C, s), 43.63 (1C, s), 21.29 (1C, s)

### benchmark_main:R109
Molecular formula: C23H31NO
IR bands (cm-1): [3444.0, 2925.0, 2853.0, 1624.0, 1599.0, 1487.0, 1421.0, 760.0]
1H NMR: 8.40 (dd, J = 8.0, 1.6 Hz, 1H, H-5), 7.58 (td, J = 8.0, 1.6 Hz, 1H, H-7), 7.36 (d, J = 8.4 Hz, 1H, H-8), 7.31 (t, J = 7.6 Hz, 1H, H-6), 6.42 (s, 1H, H-3), 6.39 (dt, J = 15.2, 6.8 Hz, 1H, H-2′), 6.31 (d, J = 15.2 Hz, 1H, H-1′), 6.03 (ddt, J = 17.2, 10.8, 4.0 Hz, 1H, N-CH2-CHCH2), 5.30 (d, J = 10.8 Hz, 1H, N-CH2-CHCHHb), 4.99 (d, J = 17.2 Hz, 1H, N-CH2-CHCHaH), 4.75 (dt, J = 4.0, 1.6 Hz, 2H, N-CH2-CHCH2), 2.23 (q, J = 6.8 Hz, 2H, H-3′), 1.47 (quint, J = 7.2 Hz, 2H, H-4′), 1.31-1.23 (m, 12H, H-5′-10′), 0.87 (t, J = 6.8 Hz, 3H, H-11′)
13C NMR: δ 177.8 (1C, s), 152.2 (1C, s), 142.2 (1C, s), 140.8 (1C, s), 132.1 (1C, s), 131.1 (1C, s), 126.6 (1C, s), 126.5 (1C, s), 123.2 (1C, s), 123.2 (1C, s), 117.5 (1C, s), 115.9 (1C, s), 109.3 (1C, s), 50.0 (1C, s), 33.0 (1C, s), 31.8 (1C, s), 29.5 (1C, s), 29.4 (1C, s), 29.2 (1C, s), 29.1 (1C, s), 28.6 (1C, s), 22.6 (1C, s), 14.0 (1C, s)

### benchmark_main:R112
Molecular formula: C33H26N10O11
IR bands (cm-1): [3320.0, 3050.0, 2980.0, 1677.0, 1577.0, 1372.0]
1H NMR: 11.59 (s, 1H, NH), 10.60 (s, 1H, NH), 8.83 (s, 1H, Ar), 8.62-8.54 (m, 1H, Ar), 8.33 (d, J = 9.8 Hz, 1H, Ar), 8.26 (s, 1H, Ar), 8.08 (d, J = 9.8 Hz, 1H, Ar), 7.62-7.47 (m, 4H, Ar), 7.42-7.22 (m, 5H, Ar), 5.42 (s, 2H, CH2), 5.23 (s, 2H, CH2), 3.84 (s, 6H, OCH3)
13C NMR: δ 165.3 (1C, s), 162.3 (1C, s), 157.4 (1C, s), 157.1 (1C, s), 156.7 (1C, s), 156.1 (1C, s), 155.8 (1C, s), 155.4 (1C, s), 150.3 (1C, s), 150.1 (1C, s), 149.7 (1C, s), 144.8 (1C, s), 144.1 (1C, s), 142.7 (1C, s), 137.1 (1C, s), 130.2 (1C, s), 129.5 (1C, s), 128.1 (1C, s), 127.2 (1C, s), 127.0 (1C, s), 123.5 (1C, s), 123.4 (1C, s), 122.9 (1C, s), 120.9 (1C, s), 120.7 (1C, s), 117.2 (1C, s), 113.4 (1C, s), 109.7 (1C, s), 109.2 (1C, s), 61.8 (1C, s), 56.4 (1C, s), 55.9 (1C, s), 52.3 (1C, s)
