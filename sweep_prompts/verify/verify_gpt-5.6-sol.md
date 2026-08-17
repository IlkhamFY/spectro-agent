# Forward 13C prediction task

For each candidate structure below (given as SMILES), predict its 13C NMR chemical
shift list (in ppm) from the structure alone. This is the forward direction only:
you are NOT given any observed spectrum and must not assume one.

Return ONLY a JSON object mapping each id to a list of predicted 13C shifts (numbers
in ppm), e.g.: {"P001": [21.0, 60.5, 171.2], "P002": [...], ...}

Candidates:

## batch 1
P000  C=CCc1c(C)c(C)c(OC)c(C)c1OC
P001  CC(C)C[C@@H]1N[C@H](CC(C)C)C(=O)N[C@@H]1C(C)C
P002  Cc1ccc(-c2c(-c3cn(C)c4ccccc34)ncc(N=C(N)N(C#N)C(=S)S)c2C)cc1
P003  C=CC=C(C(=O)c1ccccc1)C(=O)c1ccccc1
P004  Cc1ccc(C(=O)c2ccc(CC(=O)NN=Cc3ccc(O)cc3)n2C)cc1
P005  CC(=O)C(Cl)=NNc1cccc(Br)c1
P006  c1ccc(C2=C(c3cccnn3)OCCO2)cc1
P007  O=C(NCCC[NH2+]CCCC[NH2+]CCCNC(=O)[C@@H](Cc1ccccc1)c1ccccc1)[C@@H](Cc1ccccc1)c1ccccc1.O=C([O-])C(F)(F)F.O=C([O-])C(F)(F)F
P008  O=[N+]([O-])c1ccc(C2COCCO2)cc1
P009  CSc1cc([N+](=O)[O-])ccc1Oc1ccc(C#N)cc1
P010  COC(=O)ONc1ccccc1C#N
P011  c1ccc(C2=C(c3cnccn3)OCCO2)cc1
P012  CC(=O)Cc1coc(C(O[Si](C)(C)C(C)(C)C)C(C)C)c1
P013  CC#Cc1cccc(C=O)c1OCOC
P014  O=S(=O)(c1cccc(CNCO)c1)c1ccccc1Br
P015  CCOC(=O)c1c2c(c3c(C#N)c(N)sc3c1N)OCCC2c1ccc(Cl)cc1
P016  CCCCCCCCC(=O)c1ccc(CC(=O)OCC)cc1OC
## batch 2
P017  CC(=O)/C(Cl)=N\Nc1ccc(C)cc1
P018  Cc1cc(C)c([Se]c2nc(C(F)(F)F)ncc2-c2c[nH]c3ccccc23)c(C)c1
P019  Cc1ccc(S(=O)(=O)Nc2c(N)cc(Br)cc2Br)cc1
P020  Cc1ccc(S(=O)(=O)Nc2c(Br)ccc(Br)c2N)cc1
P021  CCCCCCCCCCCc1ccccc1C(=O)NS(=O)(=O)c1ccc(Cl)cc1
P022  CCCCCCCC(=O)CCc1ccc(O)c(OC)c1
P023  CN1CCC(c2ccccc2[N+](=O)[O-])C1C(=O)OC(C)(C)C
P024  COc1c(-c2ccccc2O)oc2cc(O)ccc2c1=O
P025  CCOC(=O)c1c(N)c2c(c3c(N)c(C#N)sc13)OCCC2c1ccc(Cl)cc1
P026  C=C(C)CCC(C)=Cc1ccc(C2SC(=Nc3ccccc3)N(c3ccccc3)C2=O)cc1
P027  CC(C)N1CC(=Cc2ccc(F)cc2)C(=O)C(=Cc2ccc(F)cc2)C1
P028  Cc1ccc(O)c(SC#N)c1
P029  Cn1c(=O)[nH]c2ccc(CCc3cn(S(=O)(=O)c4ccccc4)c4ccc(Br)cc34)cc21
P030  COc1ccc(Oc2ccccc2Br)c(OC)c1
P031  Cc1cc(SC#N)ccc1O
P032  FC(F)(F)c1cccc(CCCI)c1
P033  c1ccc(-c2cc(-c3[nH]ccc3N3CCNCCNCCNCC3)nc(-c3[nH]ccc3N3CCNCCNCCNCC3)c2)cc1
## batch 3
P034  CCOC(=O)CCC/C(C)=C/CCO[Si](c1ccccc1)(c1ccccc1)C(C)(C)C
P035  CC(=O)c1cccc(CBr)c1
P036  CC#Cc1c(C=O)cccc1OCOC
P037  CSc1ccc(Oc2ccc(C#N)cc2)c([N+](=O)[O-])c1
P038  COc1[nH]c(=O)c2ccccc2[n+]1[O-]
P039  COc1cccc(C(=O)C2(C)CC2(Cl)Cl)c1
P040  COc1c(-c2ccc(O)cc2)oc2cc(O)ccc2c1=O
P041  C[Si](C)(C)c1cc(F)c(OS(=O)(=O)c2ccc(Cl)cc2)c(F)c1
P042  Cn1c(=O)[nH]c2cc(CCc3cn(S(=O)(=O)c4ccccc4)c4cc(Br)ccc34)ccc21
P043  N=C1CCN1c1ccccc1
P044  O=C1NC(c2ccc(Cl)cc2)=CC(c2ccccc2)N1
P045  C=C=C(CCC(=O)O[Si](C)(C)C)OC
P046  CC(=O)c1ccccc1CBr
P047  O=C1C=CCCN1c1ccccn1
P048  FC(F)(F)c1ccc(CCCI)cc1
P049  CCN(CC)C(=O)c1ccc(-c2cc3ccc4ccc(-c5ccc(C)cc5)c5ccc(c2)c3c45)cc1
P050  C=C=C(CCC(=O)OC)O[Si](C)(C)C
## batch 4
P051  Cc1cc(C)c([Se]c2nc(-c3c[nH]c4ccccc34)ncc2C(F)(F)F)c(C)c1
P052  CCCn1c(-c2ccccc2)nc2ccccc21
P053  O=C1Nc2ccccc2NC1c1ccccc1[N+](=O)[O-]
P054  O=C(c1ccccc1)C1C2C(c3ccc(Cl)c(Cl)c3)=CC=CC(=O)N(c3ccccc3-c3ccccc32)C(C(=O)c2ccccc2)C1C(=O)c1ccccc1
P055  CCCC[C@H](NS(=O)(=O)c1ccc(C)cc1)C(=O)O
P056  CC(=O)/C(Cl)=N/Nc1cccc(C)c1
P057  CCCn1nc(-c2ccccc2)c2ccccc21
P058  CC(=O)/C(Cl)=N/Nc1ccc(C)cc1
P059  COc1c(=O)[nH]c2ccccc2[n+]1[O-]
P060  CC(C)CC(NC(=O)OC(C)(C)C)C(=O)Nc1ccccc1
P061  COC(=O)C1C(c2cn(C)c3ccccc23)=CC(c2cn(C)c3ccccc23)C2OCCOC12
P062  Oc1cccc2cc(-c3ccccc3)cnc12
P063  O=C(Nc1nc2ccccc2s1)c1ccc(-c2cccc(C(F)(F)F)c2)cc1
P064  CCOC(=O)CC/C(C)=C/CCCO[Si](c1ccccc1)(c1ccccc1)C(C)(C)C
P065  O=C(Nc1nc2ccccc2s1)c1ccc(-c2ccccc2C(F)(F)F)cc1
P066  COc1ccc(NC(=O)CSc2nnc(-c3nnc(-c4ccccc4)c(-c4ccccc4)n3)[nH]2)cc1
P067  O=C1Nc2ccccc2NC1c1cccc([N+](=O)[O-])c1
## batch 5
P068  Cc1ccc(C(=O)c2ccc(CC(=O)NN=Cc3cccc(O)c3)n2C)cc1
P069  O=C1Nc2ccccc2NC1c1ccc([N+](=O)[O-])cc1
P070  C=C=C(CO[Si](C)(C)C)CC(=O)OC
P071  Nc1nc(=O)[nH]cc1F.O=c1oc2ccccc2c2cc(O)ccc12
P072  C#CCOS(C)(=O)=NC(=O)C(C)(C)C
P073  Cn1c(=O)c2c(c3cc(F)ccc31)C(c1ccccc1)C=C(c1ccccc1)O2
P074  CC(C)[C@@H](NC(=O)OC(C)(C)C)C(=O)NCc1ccccc1
P075  O=[N+]([O-])c1ccccc1C1COCCO1
P076  COC(=O)C1C(c2cn(C)c3ccccc23)=CCC2OCCOC21c1cn(C)c2ccccc12
P077  CSc1cc(Oc2ccc(C#N)cc2)ccc1[N+](=O)[O-]
P078  Cn1c(=O)c2c(c3c(F)cccc31)C(c1ccccc1)C=C(c1ccccc1)O2
P079  N#Cc1ccc(C2=C(c3ccc(Cl)cc3)C(c3ccc(C#N)cc3)=C(c3ccc(Cl)cc3)C2=O)cc1
P080  c1ccc(C2=C(c3ccncn3)OCCO2)cc1
P081  CC(C)NC(=NS(=O)(=O)c1ccc([N+](=O)[O-])cc1)NC(C)C
P082  CCCCn1c(-c2ccccc2-c2ccc(OC)cc2)nnc1-c1ccccc1-c1ccc(OC)cc1
P083  CC(C)(C)NC(=O)c1ccccn1
P084  C=CCc1c(C)c(OC)c(C)c(C)c1OC
## batch 6
P085  CC(=O)Cc1ccc([C@@H](O[Si](C)(C)C(C)(C)C)C(C)C)o1
P086  CN1CCCC1(C(=O)OC(C)(C)C)c1ccccc1[N+](=O)[O-]
P087  Cc1cc(C)c([Se]c2cnc(C(F)(F)F)nc2-c2c[nH]c3ccccc23)c(C)c1
P088  FC(F)(F)c1ccccc1CCCI
P089  CCCCCCCCCCCc1ccccc1S(=O)(=O)NC(=O)c1ccc(Cl)cc1
P090  O=C(/C=C\C=C\C(=O)c1ccccc1)c1ccccc1
P091  NS(=O)(=O)c1cccc(Cl)c1NCc1ccccc1O
P092  CC(C)[C@H](NC(=O)OC(C)(C)C)C(=O)NCc1ccccc1
P093  N#Cc1ccccc1C1=C(c2ccccc2Cl)C(c2ccccc2C#N)=C(c2ccccc2Cl)C1=O
P094  O=C(/C=C/C=C/C(=O)c1ccccc1)c1ccccc1
P095  CCOC(=O)CCC/C(C)=C\CCO[Si](c1ccccc1)(c1ccccc1)C(C)(C)C
P096  COc1ccccc1NC(=O)CSc1nnc(-c2nnc(-c3ccccc3)c(-c3ccccc3)n2)[nH]1
P097  CCCCCCCC(=O)CCc1ccc(OC)c(O)c1
P098  O=C(Nc1nc2ccccc2s1)c1ccc(-c2ccc(C(F)(F)F)cc2)cc1
P099  Oc1ccc2cc(-c3ccccc3)cnc2c1
P100  C#CC(C)c1cc(OC)cc(F)c1-c1ccccc1
P101  O=C(NCCC[NH2+]CCCC[NH2+]CCCNC(=O)[C@H](Cc1ccccc1)c1ccccc1)[C@@H](Cc1ccccc1)c1ccccc1.O=C([O-])C(F)(F)F.O=C([O-])C(F)(F)F
## batch 7
P102  [C-]#[N+]CCNc1ccccc1
P103  CC(=O)C(Br)=NNc1ccc(Cl)cc1
P104  Cc1ccc(C(=O)c2ccc(CC(=O)NN=Cc3ccccc3O)n2C)cc1
P105  CCCCn1c(-c2ccccc2-c2cccc(OC)c2)nnc1-c1ccccc1-c1cccc(OC)c1
P106  Cc1cc(N=C=S)ccc1O
P107  CC(=O)C(Cl)=NNc1ccc(Br)cc1
P108  O=C(c1ccccc1)C1C2C(c3cc(Cl)ccc3Cl)=CC=CC(=O)N(c3ccccc3-c3ccccc32)C(C(=O)c2ccccc2)C1C(=O)c1ccccc1
P109  COc1cc(C(=O)OCc2ccccc2)c2c(c1)N1CCN(C(=O)OCC[Si](C)(C)C)CC1C2=O
P110  CCCCn1c(-c2ccccc2-c2ccccc2OC)nnc1-c1ccccc1-c1ccccc1OC
P111  Cc1ccc(-c2ncc(N=C(N)N(C#N)C(=S)S)c(C)c2-c2cn(C)c3ccccc23)cc1
P112  Cc1ccc(S(=O)(=O)Nc2cc(Br)cc(Br)c2N)cc1
P113  CC(C)NC(=NS(=O)(=O)c1cccc([N+](=O)[O-])c1)NC(C)C
P114  CC(C)Cc1ccc(C(C)NC(=O)NS(=O)(=O)c2ccc(Cl)c(Cl)c2)cc1
P115  Cn1c(=O)[nH]c2cccc(CCc3cn(S(=O)(=O)c4ccccc4)c4cccc(Br)c34)c21
P116  CC(C)N1CC(=Cc2ccccc2F)C(=O)C(=Cc2ccccc2F)C1
P117  COc1cc(C(=O)OCc2ccccc2)cc2c1C(=O)C1CN(C(=O)OCC[Si](C)(C)C)CCN21
P118  COc1c(-c2cccc(O)c2)oc2cc(O)ccc2c1=O
## batch 8
P119  N#CCCNc1ccccc1
P120  O=C1NC(c2ccccc2Cl)=CC(c2ccccc2)N1
P121  CCOc1ccc2c(c1)Oc1ccccc1C2(Cc1cccc([N+](=O)[O-])c1)C(F)(F)F
P122  CN1CC(c2ccccc2[N+](=O)[O-])CC1C(=O)OC(C)(C)C
P123  O=C1C=CCCN1c1cccnc1
P124  CC(C)Cc1ccc(C(C)NC(=O)NS(=O)(=O)c2cc(Cl)ccc2Cl)cc1
P125  Cn1c(=O)c2c(c3ccc(F)cc31)C(c1ccccc1)C=C(c1ccccc1)O2
P126  C=C(C)CCC(C)=Cc1ccc(N=C2SC(c3ccccc3)C(=O)N2c2ccccc2)cc1
P127  CCN(CC)C(=O)c1ccc(-c2cc3ccc4cccc5cc(-c6ccc(C)cc6)c(c2)c3c45)cc1
P128  CC(C)C[C@@H]1N[C@H](CC(C)C)[C@H](C(C)C)NC1=O
P129  Nc1nc(=O)[nH]cc1F.O=C1c2ccc(O)cc2-c2cc(O)ccc21
P130  C[Si](C)(C)c1cc(OS(=O)(=O)c2ccc(Cl)cc2)cc(F)c1F
P131  COc1ccc(C(=O)C2(C)CC2(Cl)Cl)cc1
P132  C#CCS(C)(=O)=NC(=O)OC(C)(C)C
P133  CCOc1ccc2c(c1)Oc1ccccc1C2(Cc1ccccc1[N+](=O)[O-])C(F)(F)F
P134  COc1cccc(Oc2ccccc2Br)c1OC
P135  NS(=O)(=O)c1cc(Cl)ccc1NCc1ccccc1O
## batch 9
P136  O=C(c1ccccc1)C1C2C(c3ccc(Cl)cc3Cl)=CC=CC(=O)N(c3ccccc3-c3ccccc32)C(C(=O)c2ccccc2)C1C(=O)c1ccccc1
P137  CCCCCCCCC(=O)c1cc(OC)ccc1CC(=O)OCC
P138  CCCCCCCC(=O)CCc1ccc(O)cc1OC
P139  COC(=O)C1(c2cn(C)c3ccccc23)C(c2cn(C)c3ccccc23)=CCC2OCCOC21
P140  CCOc1ccc2c(c1)Oc1ccccc1C2(Cc1ccc([N+](=O)[O-])cc1)C(F)(F)F
P141  Nc1nc(=O)[nH]cc1F.O=c1c2ccccc2oc2ccc(O)cc12
P142  CC(C)N1CC(=Cc2cccc(F)c2)C(=O)C(=Cc2cccc(F)c2)C1
P143  O=C1CCC=CN1c1ccccn1
P144  CCCCCCCCC(=O)c1ccc(CC(=O)OCC)c(OC)c1
P145  C#CC(C)c1cc(F)c(-c2ccccc2)cc1OC
P146  C#CC(C)c1cc(F)c(-c2ccccc2)c(OC)c1
P147  CC(C)(C)NC(=O)c1ccncc1
P148  CC(C)(C)NC(=O)c1cccnc1
P149  Cc1ccc(-c2c(C)ncc(N=C(N)N(C#N)C(=S)S)c2-c2cn(C)c3ccccc23)cc1
P150  CC(C)C[C@@H]1N[C@@H](CC(C)C)[C@H](C(C)C)NC1=O
P151  CC#Cc1cccc(OCOC)c1C=O
P152  O=[N+]([O-])c1cccc(C2COCCO2)c1
## batch 10
P153  COc1ccccc1C(=O)C1(C)CC1(Cl)Cl
P154  CC(C)NC(=NS(=O)(=O)c1ccccc1[N+](=O)[O-])NC(C)C
P155  CCOC(=O)c1c(N)c2c(c3c(C#N)c(N)sc13)OCCC2c1ccc(Cl)cc1
P156  C[Si](C)(C)c1cc(F)c(F)cc1OS(=O)(=O)c1ccc(Cl)cc1
P157  CCCCCCCCCCCc1ccc(S(=O)(=O)NC(=O)c2ccc(Cl)cc2)cc1
P158  C#CCOC(=O)N=S(C)(=O)C(C)(C)C
P159  O=S(=O)(c1cccc(Br)c1)c1ccccc1CNCO
P160  O=C(NCCC[NH2+]CCCC[NH2+]CCCNC(=O)C(Cc1ccccc1)c1ccccc1)C(Cc1ccccc1)c1ccccc1.O=C([O-])C(F)(F)F.O=C([O-])C(F)(F)F
P161  CC(=O)Cc1ccc([C@H](O[Si](C)(C)C(C)(C)C)C(C)C)o1
P162  NS(=O)(=O)c1ccc(Cl)cc1NCc1ccccc1O
P163  COc1cccc(NC(=O)CSc2nnc(-c3nnc(-c4ccccc4)c(-c4ccccc4)n3)[nH]2)c1
P164  Oc1ccc2ncc(-c3ccccc3)cc2c1
P165  Cc1ccc(S(=O)(=O)N[C@H](CC(C)C)C(=O)O)cc1
P166  COc1ccc(Oc2ccccc2Br)cc1OC
P167  CC(=O)c1ccc(CBr)cc1
P168  CC(C)Cc1ccc(C(C)NC(=O)NS(=O)(=O)c2ccc(Cl)cc2Cl)cc1
P169  C=CCc1c(C)c(C)c(C)c(OC)c1OC
## batch 11
P170  c1ccc(-c2cc(-c3cc(N4CCNCCNCCNCC4)c[nH]3)nc(-c3cc(N4CCNCCNCCNCC4)c[nH]3)c2)cc1
P171  CCCn1cnc2ccc(-c3ccccc3)cc21
P172  Cc1ccc(S(=O)(=O)N[C@@H](CC(C)C)C(=O)O)cc1
P173  C=C(C)CCC(C)=Cc1ccc(N2C(=O)C(c3ccccc3)SC2=Nc2ccccc2)cc1
P174  N#Cc1cccc(C2=C(c3cccc(Cl)c3)C(c3cccc(C#N)c3)=C(c3cccc(Cl)c3)C2=O)c1
P175  O=S(=O)(c1ccccc1Br)c1ccccc1CNCO
P176  c1ccc(-c2cc(-c3ccc(N4CCNCCNCCNCC4)[nH]3)nc(-c3ccc(N4CCNCCNCCNCC4)[nH]3)c2)cc1
P177  COc1cc2c(cc1C(=O)OCc1ccccc1)C(=O)C1CN(C(=O)OCC[Si](C)(C)C)CCN21
P178  CCN(CC)C(=O)c1ccc(-c2cc3ccc4cc(-c5ccc(C)cc5)cc5ccc(c2)c3c45)cc1
P179  O=C1NC(c2ccccc2)=CC(c2ccc(Cl)cc2)N1
