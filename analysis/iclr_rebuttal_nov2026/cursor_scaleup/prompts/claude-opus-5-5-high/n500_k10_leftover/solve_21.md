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
  {"benchmark_expand_500:R215": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R215
Molecular formula: C12H12N2OS
IR bands (cm-1): [3125.0, 3094.0, 3063.0, 3024.0, 2974.0, 1620.0, 1579.0, 1523.0, 1478.0, 1452.0, 1418.0, 1381.0, 1272.0, 1193.0, 1166.0, 1145.0, 1103.0, 1069.0, 1055.0, 887.0, 833.0, 817.0, 786.0, 755.0, 695.0, 664.0, 625.0]
1H NMR: 1.83-1.98 (m, 1H), 1.98-2.15 (m, 2H), 2.88 (d, J = 5.9 Hz, 1H), 3.31-3.51 (m, 3H), 3.53-3.60 (m, 1H), 4.28 (d, J = 6.2 Hz, 1H), 7.29 (d, J = 8.1 Hz, 1H), 7.32-7.39 (m, 1H), 7.58 (td, J = 7.7, 1.2 Hz, 1H), 7.83 (dd, J = 7.7, 1.5 Hz, 1H)
13C NMR: δ 23.2 (1C, s), 29.5 (1C, s), 47.4 (1C, s), 60.3 (1C, s), 122.3 (1C, s), 126.2 (1C, s), 128.3 (1C, s), 130.8 (1C, s), 132.7 (1C, s), 137.0 (1C, s), 164.7 (1C, s), 202.5 (1C, s)

### benchmark_expand_500:R216
Molecular formula: C17H28O2
IR bands (cm-1): [2959.0, 2908.0, 2867.0, 2851.0, 1738.0]
1H NMR: 5.18 (s, 1H), 4.19 (dd, J1 = 11 Hz, J2 = 3.2 Hz, 1H), 3.89 (dd, J1 = 11 Hz, J2 = 6.9 Hz, 1H), 22.48 (s, 1H), 2.05 (s, 3H), 1.95 (m, 1H), 1.94-1.91 (m, 2H), 1.83- 1.77 (m, 2H), 1.63 (br s, 3H), 1.59-1.52 (m, 2H), 1.50-1.35 (m, 1H), 1.26-1.17 (m, 3H), 1.07-0.98 (m, 1 H), 0.97 (d, J = 7.1 Hz, 3H), 0.91 (d, J = 3.0 Hz, 1H), 0.86 (d, J = 6.9 Hz, 3H)
13C NMR: δ 171.5 (1C, s), 135.5 (1C, s), 120.5 (1C, s), 68.70 (1C, s), 43.32 (1C, s), 42.15 (1C, s), 37.55 (1C, s), 35.70 (1C, s), 33.97 (1C, s), 27.78 (1C, s), 26.79 (1C, s), 26.44 (1C, s), 25.94 (1C, s), 23.94 (1C, s), 21.12 (1C, s), 19.89 (1C, s), 15.46 (1C, s)

### benchmark_expand_500:R217
Molecular formula: C21H12BrClF3NO3
IR bands (cm-1): [3305.0, 2933.0, 2857.0, 1738.0, 1650.0, 1589.0, 1537.0, 1479.0, 1452.0, 1411.0, 1323.0, 1258.0, 1242.0, 1169.0, 1130.0, 1111.0, 1068.0, 1016.0, 861.0, 770.0, 698.0, 675.0]
1H NMR: 10.65 (1H, bs, NH), 8.26 (2H, d, J = 7.9 Hz, H2′′, H6′′), 7.94 (2H, d, J = 7.9 Hz, H3′′, H5′′), 7.85 (1H, s, H2′), 7.82 (1H, d, J = 8.3 Hz, H3), 7.72 (1H, d, J = 1.9 Hz, H6), 7.65-7.53 (2H, m, H4, H6′), 7.31 (1H, m, H5′), 7.23 (1H, m, H4′)
13C NMR: δ 163.4 (1C, s), 163.2 (1C, s), 148.8 (1C, s), 140.4 (1C, s), 136.0 (1C, s), 133.7 (1C, q), 131.1 (1C, s), 130.9 (1C, s), 130.8 (1C, s), 128.2 (1C, s), 127.9 (1C, s), 126.7 (1C, s), 126.6 (1C, s), 126.2 (1C, q), 123.9 (1C, s), 123.4 (1C, q), 122.3 (1C, s), 121.6 (1C, s), 118.8 (1C, s)

### benchmark_expand_500:R218
Molecular formula: C14H17N7O2S
IR bands (cm-1): [3378.0, 3072.0, 3015.0, 2950.0, 2875.0, 1681.0, 1643.0, 1606.0, 1578.0, 1521.0, 1498.0, 1460.0, 1271.0, 1128.0, 968.0, 934.0, 784.0, 762.0, 539.0]
1H NMR: 3.10 (s, 3H, CH3), 3.69-3.74 (m, 4H, CH2-CH2), 4.45 (t, 2H, CH2), 4.66 (t, 2H, CH2), 5.49 (br.s, 1H, NH), 7.27 (t, 1H, Ar), 7.42 (t, 2H, Ar), 7.79 (d, J = 7.7 Hz, 2H, Ar)
13C NMR: δ 43.43 (1C, s), 45.75 (1C, br), 46.75 (1C, s), 50.83 (1C, s), 53.00 (1C, br), 122.05 (1C, s), 129.26 (1C, s), 137.95 (1C, s), 144.34 (1C, s), 155.45 (1C, s), 154.93 (1C, s)

### benchmark_expand_500:R219
Molecular formula: C23H35N5
IR bands (cm-1): [3500.0, 2500.0, 3256.0, 3132.0, 2926.0, 2852.0, 1661.0, 1631.0, 1575.0, 1521.0]
1H NMR: 1.34-1.48 (complex signal, 10H, 3-H2, 4-H2, 5-H2, 6-H2, 7-H2), 1.58 (tt, J = J′ = 6.8 Hz, 2H, 2-H2), 1.84 (tt, J = J′ = 7.2 Hz, 2H, 8-H2), 1.94-2.00 (complex signal, 4H, 2′-H2, 3′-H2), 2.70 (br t, J = 6.0 Hz, 2H, 1′-H2), 3.02 (br t, J = 6.4 Hz, 2H, 4′-H2), 3.16 (t, J = 6.8 Hz, 2H, 1-H2), 3.95 (t, J = 7.2 Hz, 2H, 9-H2), 4.85 (s, +NH, +NH2, NH, NH2), 7.59 (ddd, J = 8.8 Hz, J′ = 6.8 Hz, J″ = 1.2 Hz, 1H, 7′-H), 7.76 (dd, J = 8.4 Hz, J′ = 1.2 Hz, 1H, 5′-H), 7.85 (ddd, J = 8.4 Hz, J′ = 6.8 Hz, J″ = 1.2 Hz, 1H, 6′-H), 8.40 (br d, J = 8.8 Hz, 1H, 8′-H)
13C NMR: δ 21.8 (1C, s), 22.9 (1C, s), 24.9 (1C, s), 27.6 (1C, s), 29.3 (1C, s), 29.8 (1C, s), 30.1 (1C, s), 30.4 (1C, s), 31.5 (1C, s), 42.4 (1C, s), 49.1 (1C, s), 112.8 (1C, s), 116.9 (1C, s), 120.1 (1C, s), 126.3 (1C, s), 126.4 (1C, s), 134.1 (1C, s), 139.7 (1C, s), 151.6 (1C, s), 157.9 (1C, s), 158.5 (1C, s)

### benchmark_expand_500:R223
Molecular formula: C40H56F6N4O6
IR bands (cm-1): [3276.0, 3076.0, 2926.0, 2859.0, 1675.0, 1621.0, 1546.0, 1460.0, 1202.0, 1133.0]
1H NMR: 7.61-7.54 (6H, m, H-3, 2H-5), 7.43-7.37 (6H, m, 2H-6, H-7), 6.62 (2H, d, J = 15.9 Hz, H-2), 3.43 (4H, t, J = 6.5 Hz, H2-2′), 3.07-2.96 (8H, m, H2-4′, H2-5′), 1.94 (4H, tt, J = 6.5, 6.5 Hz, H2-3′), 1.76-1.65 (4H, m, H2-7′), 1.48-1.27 (16H, m, H2-8′, H2-9′, H2-10′, H2-11′)
13C NMR: δ 169.7 (1C, s), 142.5 (1C, s), 136.1 (1C, s), 131.1 (1C, s), 130.0 (1C, s), 128.9 (1C, s), 121.1 (1C, s), 48.8 (1C, s), 46.3 (1C, s), 37.0 (1C, s), 30.7 (1C, s), 30.5 (1C, s), 30.2 (1C, s), 27.8 (1C, s), 27.5 (1C, s)
