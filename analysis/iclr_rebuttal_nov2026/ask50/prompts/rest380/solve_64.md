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
  {"benchmark_main:R107": ["CCO", "COC"]}

Compounds:

### benchmark_main:R107
Molecular formula: C13H24O2
IR bands (cm-1): [2958.0, 2869.0, 1710.0, 1459.0, 1376.0, 1110.0, 1038.0, 884.0, 742.0]
1H NMR: 9.77 (t, J = 1.7 Hz, 1H), 3.96 (dd, J = 8.0, 6.4 Hz, 0.22H minor, C5-H), 3.85 (dq, J = 8.8, 6.1 Hz, 0.78H major, C5-H), 2.46 (t, J = 7.4 Hz, 2H), 1.99-1.92 (m, 1H), 1.82-1.73 (m, 1H), 1.72-1.66 (m, 2H), 1.66-1.56 (m, 3H), 1.56-1.44 (m, 2H), 1.44-1.37 (m, 1H), 1.37-1.23 (m, 4H), 1.19 (d, J = 2.7 Hz, 3H), 0.89 (t, J = 6.9 Hz, 3H)
13C NMR: δ 202.8 (1C, s), 82.0 (1C, s), 79.3 (1C, s), 44.3 (1C, s), 40.7 (1C, s), 37.1 (1C, s), 36.2 (1C, s), 31.8 (1C, s), 28.2 (1C, s), 27.1 (1C, s), 22.9 (1C, s), 17.3 (1C, s), 14.1 (1C, s)

### benchmark_main:R108
Molecular formula: C12H12ClN3
IR bands (cm-1): [3317.0, 2949.0, 1612.0, 1593.0, 1544.0]
1H NMR: 2.31 (s, 6H, 2CH3), 6.59 (s, 1H, Ar Pyr), 7.29 (d, J = 8.8, 2H, Ar), 7.95 (d, J = 8.8, 2H, Ar), 8.59 (s, 1H, NH)
13C NMR: δ 23.9 (1C, s), 112.2 (1C, s), 120.9 (1C, s), 126.1 (1C, s), 129.1 (1C, s), 140.9 (1C, s), 160.7 (1C, s), 168.2 (1C, s)
