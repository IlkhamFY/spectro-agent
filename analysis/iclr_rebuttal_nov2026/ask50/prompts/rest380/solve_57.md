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
  {"benchmark_expand_500:R209": ["CCO", "COC"]}

Compounds:

### benchmark_expand_500:R209
Molecular formula: C16H14O2
IR bands (cm-1): [3028.0, 2862.0, 1684.0, 1598.0, 1580.0, 1481.0, 1455.0, 1375.0, 1286.0, 1236.0]
1H NMR: 10.58 (s, 1H), 7.86 (dd, J = 7.9, 1.8 Hz, 1H), 7.55 (td, J = 8.0, 1.8 Hz, 1H), 7.43 (d, J = 7.0 Hz, 2H), 7.35 (t, J = 7.6 Hz, 2H), 7.31-7.27 (m, 1H), 7.05 (dt, J = 7.5, 3.2 Hz, 2H), 6.77 (d, J = 16.0 Hz, 1H), 6.43 (dt, J = 16.0, 5.7 Hz, 1H), 4.84 (dd, J = 5.7, 1.4 Hz, 2H). 13C{1H} NMR (100 MHz, CDCl3): δ 189.9, 161.1, 136.2, 136.0, 133.7, 128.8, 128.7, 128.3, 126.8, 125.3, 123.6, 121.1, 113.1, 69.3
13C NMR: δ 189.9 (1C, s), 161.1 (1C, s), 136.2 (1C, s), 136.0 (1C, s), 133.7 (1C, s), 128.8 (1C, s), 128.7 (1C, s), 128.3 (1C, s), 126.8 (1C, s), 125.3 (1C, s), 123.6 (1C, s), 121.1 (1C, s), 113.1 (1C, s), 69.3 (1C, s)

### benchmark_expand_500:R21
Molecular formula: C15H19NO3S
IR bands (cm-1): [3537.0, 2922.0, 2855.0, 2223.0, 1598.0, 1446.0, 1342.0, 1162.0, 1092.0, 898.0, 766.0]
1H NMR: 1.55 (t, J = 2.2 Hz, 3H), 1.84 (br s, 1H), 2.43 (s, 3H), 3.86 (d, J = 7.2 Hz, 2H), 4.01 (d, J = 2.4 Hz, 2H), 4.20 (d, J = 6.8 Hz, 2H), 5.48-5.52 (m, 1H), 5.84-5.88 (m, 1H), 7.31 (d, J = 7.2 Hz, 2H), 7.73 (d, J = 7.2 Hz, 2H)
13C NMR: δ 3.3 (1C, s), 21.6 (1C, s), 36.7 (1C, s), 43.0 (1C, s), 58.0 (1C, s), 71.8 (1C, s), 82.1 (1C, s), 125.8 (1C, s), 128.0 (1C, s), 129.5 (1C, s), 134.2 (1C, s), 135.8 (1C, s), 143.6 (1C, s)

### benchmark_expand_500:R211
Molecular formula: C12H16O3S
IR bands (cm-1): [3492.0, 1478.0, 1284.0, 1185.0]
1H NMR: 7.78 (d, J = 8.3 Hz, 2H), 7.35 (d, J = 8.3 Hz, 2H), 4.31 (br s, 1H), 3.58 (qt, J = 6.7 Hz, 1H), 2.45 (s, 3H), 2.28-2.13 (m, 4H), 1.95-1.84 (m, 2H), 1.79-1.74 (m, 1H)
13C NMR: δ 144.9 (1C, s), 135.0 (1C, s), 130.0 (1C, s), 128.6 (1C, s), 72.6 (1C, s), 63.2 (1C, s), 36.2 (1C, s), 35.5 (1C, s), 24.6 (1C, s), 21.6 (1C, s)

### benchmark_expand_500:R214
Molecular formula: C13H26O3Si
IR bands (cm-1): [2958.0, 2931.0, 2859.0, 1742.0, 1682.0]
1H NMR: 4.66 (q, J = 6.6 Hz, 1H), 4.15 (q, J = 7.1 Hz, 2H), 3.02 (s 1H), 1.56 (d, J = 6.7 Hz, 3H), 1.26 (t, J = 7.1 Hz, 3H), 0.94 (s, 9H), 0.14 (s, 6H)
13C NMR: δ 170.8 (1C, s), 144.4 (1C, s), 106.4 (1C, s), 60.9 (1C, s), 43.0 (1C, s), 25.9 (1C, s), 18.4 (1C, s), 14.3 (1C, s), 11.19 (1C, s), -3.9 (1C, s)

### benchmark_expand_500:R22
Molecular formula: C14H16O2
IR bands (cm-1): [2972.0, 2940.0, 2367.0, 1717.0, 1613.0, 1578.0, 1508.0, 1454.0, 1385.0, 1310.0, 1270.0, 1177.0, 1105.0, 1020.0, 752.0]
1H NMR: 7.94 (d, 2H, 3JHH = 8.4 Hz, o-ArH), 7.23 (d, 2H, 3JHH = 8.4 Hz, m-ArH), 4.36 (t, 2H, 3JHH = 7.1 Hz, -CH2O(CO)-), 2.61 (tt, 2H, 3JHH = 7.1 Hz, 4JHH = 2.4 Hz, -C≡CCH2-CH2-), 2.40 (s, 3H, -CH3), 2.15 (qt, 2H, 3JHH = 7.5 Hz, 4JHH = 2.4 Hz, Me-CH2-C≡), 1.11 (t, 3H, 3JHH = 7.5 Hz, -CH3)
13C NMR: δ 166.5 (1C, s), 143.7 (1C, s), 129.8 (1C, s), 129.1 (1C, s), 127.5 (1C, s), 83.6 (1C, s), 80.0 (1C, s), 63.2 (1C, s), 21.8 (1C, s), 19.5 (1C, s), 14.2 (1C, s), 12.5 (1C, s)

### benchmark_expand_500:R220
Molecular formula: C15H14Br2N2O3
IR bands (cm-1): [3081.0, 2961.0, 1751.0, 1702.0, 1655.0, 1619.0, 1598.0, 1427.0, 1243.0, 1179.0, 1091.0, 985.0, 937.0, 924.0, 798.0, 782.0, 761.0, 743.0, 708.0, 686.0, 657.0, 563.0, 546.0]
1H NMR: 8.51 (s, 1H), 8.04 (d, J = 8.0 Hz, 2H), 7.81 (t, J = 8.0 Hz, 1H), 7.61 (t, J = 8.0 Hz, 2H), 3.79 (t, J = 6.0 Hz, 2H), 3.58 (t, J = 6.0 Hz, 2H), 1.81 (m, 4H) ppm
13C NMR: δ 167.9 (1C, s), 158.5 (1C, s), 149.2 (1C, s), 143.9 (1C, s), 135.6 (1C, s), 130.9 (1C, s), 130.5 (1C, s), 129.4 (1C, s), 96.1 (1C, s), 48.5 (1C, s), 32.7 (1C, s), 29.2 (1C, s)
