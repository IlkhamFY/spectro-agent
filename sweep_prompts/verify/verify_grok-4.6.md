# Forward 13C prediction task

For each candidate structure below (given as SMILES), predict its 13C NMR chemical
shift list (in ppm) from the structure alone. This is the forward direction only:
you are NOT given any observed spectrum and must not assume one.

Return ONLY a JSON object mapping each id to a list of predicted 13C shifts (numbers
in ppm), e.g.: {"P001": [21.0, 60.5, 171.2], "P002": [...], ...}

Candidates:

## batch 1
P000  O=C1C=CCN1Cc1ccccn1
P001  Cc1ccc(S(=O)(=O)Nc2cc(Br)c(Br)cc2N)cc1
P002  O=[N+]([O-])c1ccccc1C1COCCO1
P003  C=C(c1ccccc1)c1nc2ccc(F)cc2c(-c2ccccc2)c1C(=O)OC
P004  Cc1cc([N+](=O)[O-])ccc1Oc1ccc(N=C=S)cc1
P005  CCCCn1c(-c2ccc(-c3ccccn3)cc2)nc(-c2ccc(OC)cc2)c1-c1ccc(OC)cc1
P006  CC(C)(C)NC(=O)c1ccncc1
P007  Cc1ccc(C(=O)c2ccc(O)c(CC(=O)NN=Cc3cccn3C)c2)cc1
P008  CC(=O)C(Br)=NNc1cccc(Cl)c1
P009  COc1ccc(Oc2ccccc2Br)c(OC)c1
P010  C=CC=C(C(=O)C(=O)c1ccccc1)c1ccccc1
P011  C=Cc1ccc(CCc2sc(NC(=O)c3ccccc3)nc2CCc2cccc(C)c2)cc1
P012  CC#Cc1cccc(OCOC)c1C=O
P013  O=c1ccc2cc(CCn3ccnc3)ccc2o1
P014  CC(C)Cc1ccc(C(C)C(=O)NNS(=O)(=O)c2cc(Cl)ccc2Cl)cc1
P015  COc1cc(C(=O)N2CCc3c([nH]c4ccccc34)C2Cc2ccccc2)cc(OC)c1OC
P016  Oc1ccc2ncc(-c3ccccc3)cc2c1
## batch 2
P017  Cc1ccc(S(=O)(=O)NC(CC(C)C)C(=O)O)cc1
P018  CN1CCC(C(=O)OC(C)(C)C)(c2ccccc2[N+](=O)[O-])C1
P019  COc1ccc2c(=O)c(-c3ccc(O)c(O)c3)coc2c1
P020  CCOc1ccc2nc(CC(O)(c3coc4ccccc4c3=O)C(F)(F)F)ccc2c1
P021  Cc1ccc(C(=O)c2cc(CC(=O)NN=Cc3cccn3C)ccc2O)cc1
P022  CCCCn1c(-c2ccccc2-c2ccccn2)nc(-c2ccc(OC)cc2)c1-c1ccc(OC)cc1
P023  O=C1NC(c2cccc([N+](=O)[O-])c2)Nc2ccccc21
P024  C/N=C(\Cl)C(=O)Nc1ccc(C)cc1
P025  CCOC(=O)C1=C(Sc2ccccc2N)OC(N)=C(C#N)C1c1ccc(Cl)cc1
P026  CCOC(=O)C1=C(N)OC(Sc2ccccc2N)=C(C#N)C1c1ccccc1Cl
P027  Cc1cc(C)c(-n2nc(C(F)(F)F)cc2[Se]c2ccc3ncccc3c2)c(C)c1
P028  C[Si](C)(C)c1cc(F)c(F)cc1OS(=O)(=O)c1ccc(Cl)cc1
P029  COc1cc(OC)c(C2c3[nH]c4ccccc4c3CCN2C(=O)Cc2ccccc2)c(OC)c1
P030  Cn1ccnc1Cc1ccc2ccc(=O)oc2c1
P031  CCCCCCCCC(=O)c1cc(OC)ccc1CC(=O)OCC
P032  CC(C)NC(=NS(=O)(=O)c1ccc([N+](=O)[O-])cc1)NC(C)C
P033  CCN(CC)C(=O)c1c(-c2ccccc2)cc(C)cc1-c1cc2ccc3cccc4ccc(c1)c2c34
## batch 3
P034  CC(=O)C(Cl)=NNc1ccc(C)cc1
P035  C=CCc1c(C)c(C)c(C)c(OC)c1OC
P036  COc1ccc(Oc2ccccc2Br)cc1OC
P037  CN1CCCC1(C(=O)OC(C)(C)C)c1ccccc1[N+](=O)[O-]
P038  Cn1cc(CC2C(=O)N(S(=O)(=O)c3ccc(N)cc3)c3ccc(Br)cc32)c2ccccc21
P039  CN1CCN(CCCCc2cn(Cc3cc(-c4ccccc4)cc(Cn4cc(CCCCN5CCN(C)CC5)nn4)n3)nn2)CC1
P040  COc1ccccc1C(=O)C1(C)CC1(Cl)Cl
P041  Cc1ccc(S(=O)(=O)NC(CC(=O)O)CC(C)C)cc1
P042  FC(F)(F)c1cccc(CCCI)c1
P043  O=C1NC(c2ccccc2[N+](=O)[O-])Nc2ccccc21
P044  C=C(c1ccccc1)c1c(C(=O)OC)c(-c2ccccc2)nc2cc(F)ccc12
P045  CC(=O)Cc1cc(C(O[Si](C)(C)C(C)(C)C)C(C)C)co1
P046  CCCCCCC(=O)CCc1ccc(OC)c(O)c1
P047  Cc1cc(C)c(-n2nc(C(F)(F)F)cc2[Se]c2cccc3ncccc23)c(C)c1
P048  CCCn1c(-c2ccccc2)nc2ccccc21
P049  C=C(c1ccc(CC)cc1)c1nc(NC(=O)c2ccccc2)sc1CCc1ccc(C)cc1
P050  CSc1ccc(O)c(C#N)c1
## batch 4
P051  CCCCCCCCC(=O)c1ccc(OC)cc1CC(=O)OCC
P052  COc1ccc(-c2coc3cc(O)ccc3c2=O)cc1O
P053  CCN(CC)C(=O)c1c(-c2ccccc2)cc(C)cc1-c1ccc2ccc3cccc4ccc1c2c34
P054  COC(=O)C1C(=O)c2c([nH]c3cc(OC)c(O)cc23)C(c2ccccc2)N1COCC[Si](C)(C)C
P055  C=Cc1ccc(CCc2nc(NC(=O)c3ccccc3)sc2CCc2ccc(C)cc2)cc1
P056  O=C1c2ccccc2-c2c1c1ccccc1c1nc(-c3ccc(Cl)c(Cl)c3)c(-c3ccccc3)nc21
P057  C=Cc1ccc(-c2nnc(Cc3nnn(-c4ccc(C(=O)Nc5ccc(OC)cc5)cc4)n3)s2)cc1
P058  COC(=O)C(O)CCC#C[Si](C)(C)C
P059  CC(C)(C)NC(=O)c1ccccn1
P060  NC(=O)Nc1cccc(-n2cc(C(=O)O)c(=O)c3cc(F)ccc32)c1
P061  O=S(=O)(NCc1ccc(Br)cc1)c1ccccc1CO
P062  C=CCc1c(C)c(OC)c(C)c(C)c1OC
P063  Cc1ccc(Cn2nc(C3CC=CS3)nc2-c2nnc(-c3cn(C)c4ccccc34)s2)cc1
P064  O=C1NC(=S)N(c2ccc(C(F)(F)F)cc2)/C1=C/c1cccc2ccccc12
P065  Cn1c(=O)n(O)c(=O)c2ccccc21
P066  COC(=O)C(=O)CCC#C[Si](C)(C)C
P067  Cc1cc([N+](=O)[O-])ccc1Oc1ccc(SC#N)cc1
## batch 5
P068  O=C1c2ccccc2-c2c1c1ccccc1c1nc(-c3cccc(Cl)c3)c(-c3ccc(Cl)cc3)nc21
P069  C=C(c1ccccc1)c1c(C(=O)OC)c(-c2ccccc2)nc2ccc(F)cc12
P070  NS(=O)(=O)c1ccc(NCc2cc(Cl)ccc2O)cc1
P071  C#CCN(C(=O)OC)S(=O)C(C)(C)C
P072  Cc1ccc(S(=O)(=O)Nc2cc(Br)cc(Br)c2N)cc1
P073  CC(C)N1C/C(=C/c2cccc(F)c2)C(=O)/C(=C/c2cccc(F)c2)C1
P074  O=[N+]([O-])c1cccc(C2COCCO2)c1
P075  CN1CC(c2ccccc2[N+](=O)[O-])CC1C(=O)OC(C)(C)C
P076  COc1ccc(OC)c(Oc2ccccc2Br)c1
P077  CCCn1nc(-c2ccccc2)c2ccccc21
P078  O=C1c2ccccc2C(=O)C1C1=C(c2ccc(Cl)cc2)N(Cc2ccccc2)C(c2cccc(Cl)c2)C(C2C(=O)c3ccccc3C2=O)C1c1ccccc1
P079  Oc1cccc2ncc(-c3ccccc3)cc12
P080  CC(C)N(C(=N)NS(=O)(=O)c1ccc([N+](=O)[O-])cc1)C(C)C
P081  CCCCCCCCCCc1ccccc1C(=O)NS(=O)(=O)c1ccc(Cl)cc1
P082  CC(=O)Cc1ccc(C(O[Si](C)(C)C(C)(C)C)C(C)C)o1
P083  C=CC=C(C(=O)c1ccccc1)C(=O)c1ccccc1
P084  CC(=NNc1ccc(C)cc1)C(=O)Cl
## batch 6
P085  CCOc1ccc2ncc(CC(O)(c3coc4ccccc4c3=O)C(F)(F)F)cc2c1
P086  Cc1ccccc1C(=O)CBr
P087  Cn1cc(CC2(N)C(=O)N(S(=O)(=O)c3ccccc3)c3ccc(Br)cc32)c2ccccc21
P088  CCCCCCCCC(=O)c1ccc(CC(=O)OCC)c(OC)c1
P089  NS(=O)(=O)c1ccc(NCc2ccccc2O)cc1Cl
P090  O=C1c2ccccc2C(=O)C1C1=C(c2ccc(Cl)cc2)N(Cc2ccccc2)C(c2ccc(Cl)cc2)C(C2C(=O)c3ccccc3C2=O)C1c1ccccc1
P091  CC(C)N1C/C(=C/c2ccccc2F)C(=O)/C(=C/c2ccccc2F)C1
P092  Oc1ccc2cc(-c3ccccc3)cnc2c1
P093  NS(=O)(=O)c1ccc(NCc2ccccc2O)c(Cl)c1
P094  CCN1CCN(CCCc2cn(Cc3cc(-c4ccccc4)cc(Cn4cc(CCCN5CCN(CC)CC5)nn4)n3)nn2)CC1
P095  O=C1NC(c2ccc(Cl)cc2)=CC(c2ccccc2)N1
P096  CC(C)[C@H](NC(=O)OC(C)(C)C)C(=O)NCc1ccccc1
P097  Cc1cc(C)c(-n2nc(C(F)(F)F)cc2[Se]c2ccnc3ccccc23)c(C)c1
P098  O=S(=O)(NCc1ccc(CO)cc1)c1ccccc1Br
P099  C#CC(C)c1ccc(OC)cc1-c1ccc(F)cc1
P100  O=C(CC(c1ccccc1)c1ccccc1)NCCC[NH2+]CCCC[NH2+]CCCNC(=O)CC(c1ccccc1)c1ccccc1.O=C([O-])C(F)(F)F.O=C([O-])C(F)(F)F
P101  O=c1ccc2ccc(CCn3ccnc3)cc2o1
## batch 7
P102  CC#Cc1c(C=O)cccc1OCOC
P103  Cc1ccc(C(=O)c2c(O)cccc2CC(=O)NN=Cc2cccn2C)cc1
P104  CCCCCCCCCCc1ccccc1C(=O)NS(=O)(=O)c1ccccc1Cl
P105  C[Si](C)(C)c1ccc(F)c(F)c1OS(=O)(=O)c1ccc(Cl)cc1
P106  CC#Cc1cccc(C=O)c1OCOC
P107  O=C1NC(=S)N(c2cccc(C(F)(F)F)c2)/C1=C/c1cccc2ccccc12
P108  COC(=O)C1NC(c2ccccc2)c2c(c3cc(O)c(OC)cc3n2COCC[Si](C)(C)C)C1=O
P109  CCCCCCCCCCc1ccccc1S(=O)(=O)NC(=O)c1ccc(Cl)cc1
P110  O=C1C=CCCN1c1ccccn1
P111  Cc1ccc(O)c(SC#N)c1
P112  CC(C)N(C(N)=NS(=O)(=O)c1ccc([N+](=O)[O-])cc1)C(C)C
P113  CC(C)CC1NC(C(C)C)C(CC(C)C)NC1=O
P114  Cc1ccc(S(=O)(=O)Nc2c(N)cc(Br)cc2Br)cc1
P115  CC(C)Cc1ccc(NC(=O)C(C)NS(=O)(=O)c2ccc(Cl)c(Cl)c2)cc1
P116  COC(=O)C1NC(c2ccccc2)c2c(c3cc(OC)c(O)cc3n2COCC[Si](C)(C)C)C1=O
P117  COC(=O)C(=O)CCC=C[Si](C)(C)C
P118  Cn1cc(CC2(N)C(=O)N(S(=O)(=O)c3ccccc3)c3ccccc32)c2ccc(Br)cc21
## batch 8
P119  Nc1ccccc1N1C=CCC1=O
P120  CCOC(=O)CC/C(C)=C\CCCO[Si](c1ccccc1)(c1ccccc1)C(C)(C)C
P121  CCOc1ccc2c(=O)c(C(O)(Cc3ccc4ccccc4n3)C(F)(F)F)coc2c1
P122  O=C1NC(c2ccccc2)=CC(c2ccc(Cl)cc2)N1
P123  CC(C)CC1NC(=O)C(C(C)C)NC1CC(C)C
P124  Cc1cccc(C(=O)CBr)c1
P125  C1=NN(c2ccccc2)CC1
P126  c1ccc(C2=NCCN2)cc1
P127  CC(C)C(NC(=O)OC(C)(C)C)C(=O)NCc1ccccc1
P128  NC(=O)Nc1ccccc1-n1cc(C(=O)O)c(=O)c2ccc(F)cc21
P129  CSc1cc([N+](=O)[O-])ccc1Oc1ccc(C#N)cc1
P130  COc1cc(-c2coc3cc(O)ccc3c2=O)ccc1O
P131  C#CCOC(=O)N(C)S(=O)C(C)(C)C
P132  CCOC(=O)CC/C=C(\C)CCCO[Si](c1ccccc1)(c1ccccc1)C(C)(C)C
P133  COc1ccc(C(=O)C2(C)CC2(Cl)Cl)cc1
P134  FC(F)(F)c1ccccc1CCCI
P135  O=C1NC(c2ccc([N+](=O)[O-])cc2)Nc2ccccc21
## batch 9
P136  CCC(C)C(NS(=O)(=O)c1ccc(C)cc1)C(=O)O
P137  CC(C)NC(=O)C(Cc1ccccc1)NC(=O)OC(C)(C)C
P138  CCc1ccc(-c2cc(Cn3cc(CCCN4CCN(C)CC4)nn3)nc(Cn3cc(CCCN4CCN(C)CC4)nn3)c2)cc1
P139  CCOC(=O)CC/C(C)=C/CCCO[Si](c1ccccc1)(c1ccccc1)C(C)(C)C
P140  NCCCNCCCCN(CCCNC(=O)CC(c1ccccc1)c1ccccc1)C(=O)CC(c1ccccc1)c1ccccc1.O=C(O)C(F)(F)F.O=C(O)C(F)(F)F
P141  CC(C)Cc1ccc(C(C)C(=O)NNS(=O)(=O)c2ccc(Cl)c(Cl)c2)cc1
P142  O=C1NC(c2ccccc2)=CC(c2ccccc2Cl)N1
P143  CCCCCCC(=O)CCc1ccc(O)c(OC)c1
P144  C#CC(C)c1cc(OC)ccc1-c1ccc(F)cc1
P145  C#CC(C)c1cc(-c2ccc(F)cc2)ccc1OC
P146  CC(=O)c1ccccc1CBr
P147  CC(=O)Cc1ccoc1C(O[Si](C)(C)C(C)(C)C)C(C)C
P148  Cc1cc(SC#N)ccc1O
P149  CC(C)(C)NC(=O)c1cccnc1
P150  C=CCc1c(OC)c(C)c(C)c(C)c1OC
P151  O=[N+]([O-])c1ccc(C2COCCO2)cc1
P152  COc1ccc(NC(=O)c2ccc(-c3nnn(Cc4nnc(/C=C/c5ccccc5)s4)n3)cc2)cc1
## batch 10
P153  CC(C)N1C/C(=C/c2ccc(F)cc2)C(=O)/C(=C/c2ccc(F)cc2)C1
P154  CCOC(=O)C1=C(N)OC(Sc2ccccc2N)=C(C#N)C1c1ccc(Cl)cc1
P155  COc1cccc(C(=O)C2(C)CC2(Cl)Cl)c1
P156  CCCCCCC(=O)CCc1cccc(OC)c1O
P157  C#CCN(C(=O)OC(C)(C)C)S(C)=O
P158  O=C1c2ccccc2C(=O)C1C1=C(c2ccccc2)N(Cc2ccc(Cl)cc2)C(c2ccc(Cl)cc2)C(C2C(=O)c3ccccc3C2=O)C1c1ccccc1
P159  O=C(CC(c1ccccc1)c1ccccc1)NCCCNCCCCNCCCNC(=O)CC(c1ccccc1)c1ccccc1.O=C(O)C(F)(F)F.O=C(O)C(F)(F)F
P160  CC(=O)C(Br)=NNc1ccc(Cl)cc1
P161  NC(=O)Nc1ccccc1-n1cc(C(=O)O)c(=O)c2cc(F)ccc21
P162  COc1ccc(-c2nnc(-c3cn(CC(=O)NC4c5ccccc5Nc5ccccc54)nn3)s2)cc1
P163  O=c1[nH]c2ccccc2c(=O)n1CO
P164  Cc1ccc(Cn2nc(-c3cn(C)c4ccccc34)nc2-c2nnc(C3CC=CS3)s2)cc1
P165  COc1cc(OC)c(C2c3[nH]c4ccccc4c3CCN2C(=O)Cc2ccccc2)cc1OC
P166  CC(=O)C(Cl)=NNc1ccc(Br)cc1
P167  CC(C)CC1NC(CC(C)C)C(C(C)C)NC1=O
P168  C=CC(=CC(=O)c1ccccc1)C(=O)c1ccccc1
P169  Oc1ccc2ccccc2c1/C=N/c1nc(-c2ccc(C(F)(F)F)cc2)cs1
## batch 11
P170  CCCCn1c(-c2ccc(-c3ccncc3)cc2)nc(-c2ccccc2OC)c1-c1ccccc1OC
P171  Cc1ccc(Cn2nc(-c3c(C)[nH]c4ccccc34)nc2-c2nnc(C3CC=CS3)s2)cc1
P172  C1=NCCN1c1ccccc1
P173  FC(F)(F)c1ccc(CCCI)cc1
P174  O=S(=O)(NCc1ccccc1CO)c1ccccc1Br
P175  COC(=O)n1c(=O)[nH]c2ccccc21
P176  CCCc1nc2ccccc2n1-c1ccccc1
P177  O=C1c2ccccc2-c2c1c1ccccc1c1nc(-c3ccc(Cl)cc3)c(-c3ccc(Cl)cc3)nc21
