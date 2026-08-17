# Forward 13C prediction task

For each candidate structure below (given as SMILES), predict its 13C NMR chemical
shift list (in ppm) from the structure alone. This is the forward direction only:
you are NOT given any observed spectrum and must not assume one.

Return ONLY a JSON object mapping each id to a list of predicted 13C shifts (numbers
in ppm), e.g.: {"P001": [21.0, 60.5, 171.2], "P002": [...], ...}

Candidates:

## batch 1
P000  COc1ccc(Oc2ccccc2Br)cc1OC
P001  CCN1CCN(CCCn2cc(Cc3cc(-c4ccccc4)cc(Cc4cn(CCCN5CCN(CC)CC5)nn4)n3)nn2)CC1
P002  CC(=NCl)C(=O)Nc1ccc(C)cc1
P003  C=C(C)c1ccc(N=c2sc(C)c(C)n(CCc3ccccc3)c2=O)cc1-c1ccccc1
P004  COc1cccc2c(C(NS(=O)(=O)c3ccc(Br)cc3)c3c[nH]c4ccccc34)c[nH]c12
P005  CCN1CCN(CCCc2cn(Cc3cc(-c4ccccc4)cc(Cn4cc(CCCN5CCN(CC)CC5)nn4)n3)nn2)CC1
P006  COc1ccc(C(=O)C2(C)CC2(Cl)Cl)cc1
P007  CCc1cc(N=C2SC(=C(C)C=C(C)c3ccccc3)N(c3ccccc3)C2=O)ccc1C
P008  CC#Cc1cccc(C=O)c1OCOC
P009  Cc1ccc(SC#N)c(O)c1
P010  C=CC(=O)Nc1cccc([N+](=O)[O-])c1
P011  O=C1c2ccccc2-c2c1nc(-c1ccc(Cl)cc1)c1c(-c3ccc(Cl)cc3)c3ccccc3nc21
P012  CCn1c(Cc2ccccc2)nc2ccccc21
P013  Cc1cc(C)c([Se]c2c(-c3ccc(C(F)(F)F)cn3)nc3ccccn23)c(C)c1
P014  CCN(CC)C(=O)c1c(-c2c(C)c3ccccc3c3ccccc23)c2ccccc2c2ccccc12
P015  COC(=O)C(c1cn(COCC[Si](C)(C)C)c2ccccc12)C(C[N+](=O)[O-])C(=O)c1ccccc1
P016  Cc1cc(C)c([Se]c2nc3ccccc3n2-c2ccc(C(F)(F)F)cn2)c(C)c1
## batch 2
P017  CC(C)CC1NC(=O)C(C(C)C)NC1CC(C)C
P018  Cc1ccc(-c2ccc(C(=O)CC(=O)NN=Cc3ccc(O)cc3)n2C)cc1
P019  O=C(c1ccccc1)c1c[nH]c2ccccc12
P020  O=C(Nc1ccccc1-c1nc2ccccc2s1)c1cccc(C(F)(F)F)c1
P021  Cc1ccc(-c2nnc(SCc3c(-c4nc5c(s4)-c4ccccc4C5)nn(C)c3C)[nH]2)cc1
P022  CCCn1c(-c2ccccc2)nc2ccccc21
P023  C#CCc1ccc2nc(-c3nn(C)c(C)c3CSc3nnc(-c4ccc(C)cc4)[nH]3)sc2c1
P024  CCC(C)C(NS(=O)(=O)c1ccc(C)cc1)C(=O)O
P025  CC(C)(C)NC(=O)c1cccnc1
P026  CC(C)N1CC(=Cc2ccccc2F)C(=O)C(=Cc2ccccc2F)C1
P027  O=[N+]([O-])c1ccccc1C1OCCCO1
P028  COc1ccc(-c2coc3cc(O)ccc3c2=O)cc1O
P029  Cc1ccc(-c2ccc(C(=O)CC(=O)NN=Cc3ccccc3O)n2C)cc1
P030  C[Si](C)(C)c1cc(OS(=O)(=O)c2ccc(Cl)cc2)c(F)cc1F
P031  COC(=O)C(=O)C(c1cn(COCC[Si](C)(C)C)c2ccccc12)C(C[N+](=O)[O-])c1ccccc1
P032  C[Si](C)(C)c1ccc(OS(=O)(=O)c2ccc(Cl)cc2)c(F)c1F
P033  CC(=O)C(Cl)=NNc1ccc(Br)cc1
## batch 3
P034  C=CC=CC(=O)c1ccc(C(=O)c2ccccc2)cc1
P035  O=C(OCC=Cc1cccnc1)c1cccnc1
P036  FC(F)(F)c1cccc(CCCI)c1
P037  Cc1ccc(S(=O)(=O)Nc2cc(Br)c(Br)cc2N)cc1
P038  CCOc1ccc2nc(CC(O)(c3cc4ccccc4oc3=O)C(F)(F)F)ccc2c1
P039  CN1CC(C(=O)OC(C)(C)C)C(c2ccccc2[N+](=O)[O-])C1
P040  O=C1c2ccccc2-c2c1c(-c1ccc(Cl)cc1)nc1c(-c3ccc(Cl)cc3)c3ccccc3nc21
P041  Cc1ccc([N+](=O)[O-])cc1Oc1ccc(SC#N)cc1
P042  O=C1C=CCCN1c1ccncc1
P043  C=C(C(=O)C1(c2ccccc2)C(=O)N(C)c2ccccc21)c1ccc(F)cc1
P044  CC(=O)C(Cl)=NNc1ccc(C)cc1
P045  Cc1ccccc1C(=O)CBr
P046  CCCCCCCCCCCc1ccc(C(=O)NS(=O)(=O)c2cccc(Cl)c2)cc1
P047  O=C1NC(c2ccc(Cl)cc2)=CC(c2ccccc2)N1
P048  COc1ccc(NC(=O)CSc2nnc3c4ccccc4n4c(Cc5ccccc5)nnc4n23)cc1
P049  COc1ccc2[nH]cc(C(NS(=O)(=O)c3ccc(Br)cc3)c3c[nH]c4ccccc34)c2c1
P050  CCCCCCCC(=O)CCc1ccc(O)c(OC)c1
## batch 4
P051  CCCCn1nc(-c2ccc(-c3ccccc3OC)cc2)nc1-c1ccc(-c2ccccc2OC)cc1
P052  CN1CCN(CCCCc2cn(Cc3cc(-c4ccccc4)cc(Cn4cc(CCCCN5CCN(C)CC5)nn4)n3)nn2)CC1
P053  C=CCc1c(C)c(OC)c(C)c(C)c1OC
P054  CCCCn1c(-c2ccc(-c3ccccc3OC)cc2)nnc1-c1ccc(-c2ccccc2OC)cc1
P055  C=CCc1c(C)c(C)c(OC)c(OC)c1C
P056  CN1CC(C(=O)OC(C)(C)C)C(c2ccc([N+](=O)[O-])cc2)C1
P057  CC(=O)c1ccccc1CBr
P058  Cc1cc(C)c([Se]n2c(-c3ccc(C(F)(F)F)cn3)nc3ccccc32)c(C)c1
P059  C=CC=CC(=O)c1cccc(C(=O)c2ccccc2)c1
P060  Cc1ccc(Oc2ccc(SC#N)cc2)c([N+](=O)[O-])c1
P061  C=C(C(=O)C1(c2ccccc2)C(=O)N(C)c2ccc(F)cc21)c1ccccc1
P062  CCCCCCCCC(=O)c1cc(OC)ccc1CC(=O)OCC
P063  COc1ccc(OC)c(Oc2ccccc2Br)c1
P064  COc1ccccc1C(=O)C1(C)CC1(Cl)Cl
P065  O=C1NC(c2cccc([N+](=O)[O-])c2)Nc2ccccc21
P066  C=C(C(=O)C1(c2ccccc2)C(=O)N(C)c2ccccc21)c1cccc(F)c1
P067  NS(=O)(=O)c1ccc(CNc2ccccc2O)c(Cl)c1
## batch 5
P068  C#CCOC(=O)N(C)S(=O)C(C)(C)C
P069  CC(C)(C)NC(=O)c1ccncc1
P070  CC(C)N1CC(=Cc2ccc(F)cc2)C(=O)C(=Cc2ccc(F)cc2)C1
P071  O=C1c2ccccc2C(=O)C12C(c1ccc(Cl)cc1)N(Cc1ccccc1)C(c1ccc(Cl)cc1)C1(C(=O)c3ccccc3C1=O)C2/C=C/c1ccccc1
P072  CCOC(=O)c1c(N)sc2c1CCC1=C2OC(N)=C(C#N)C1c1cccc(Cl)c1
P073  O=C1NC(c2ccccc2Cl)=CC(c2ccccc2)N1
P074  CCCc1ccccc1-c1nc2ccccc2[nH]1
P075  COC(=O)CCC#CC(=O)[Si](C)(C)C
P076  Oc1ccc2ccc(-c3ccccc3)nc2c1
P077  CC(C)Cc1ccc(C(C)C(=O)NNS(=O)(=O)c2cc(Cl)ccc2Cl)cc1
P078  CCCCCCCCC(=O)c1ccc(OC)c(CC(=O)OCC)c1
P079  CC(=O)C(Cl)=NNc1cccc(C)c1
P080  C=CC(=O)Nc1ccccc1[N+](=O)[O-]
P081  CC#Cc1cccc(OCOC)c1C=O
P082  CCOc1ccc2ccc(CC(O)(c3cc4ccccc4oc3=O)C(F)(F)F)nc2c1
P083  COc1ccc(NC(=O)CSc2nnc3c4nnc(Cc5ccccc5)n4c4ccccc4n23)cc1
P084  Cc1ccc(S(=O)(=O)Nc2cc(Br)c(N)cc2Br)cc1
## batch 6
P085  CCCCCCCC(=O)CCc1ccc(OC)c(O)c1
P086  O=C(CC(c1ccccc1)c1ccccc1)NCCCCNCCCNCCCNC(=O)CC(c1ccccc1)c1ccccc1.O=C(O)C(F)(F)F.O=C(O)C(F)(F)F
P087  FC(F)(F)c1ccccc1CCCI
P088  CC(C)N1CC(=Cc2cccc(F)c2)C(=O)C(=Cc2cccc(F)c2)C1
P089  Cc1cccc(C(=O)CBr)c1
P090  NS(=O)(=O)c1ccc(Cl)c(CNc2ccccc2O)c1
P091  CCN(CC)C(=O)c1c(-c2cc3ccccc3c3cc(C)ccc23)c2ccccc2c2ccccc12
P092  COc1cc2c(cc1OC)C(C1(OC)c3ccccc3C(=O)N1Cc1ccccc1)N(C)C=C2
P093  CC(C)NC(=NS(=O)(=O)c1cccc([N+](=O)[O-])c1)NC(C)C
P094  COc1ccc2c(C(NS(=O)(=O)c3ccc(Br)cc3)c3c[nH]c4ccccc34)c[nH]c2c1
P095  O=C1c2ccccc2-c2c1c(-c1ccc(Cl)cc1)nc1c(-c3ccc(Cl)cc3)nc3ccccc3c21
P096  C#CC(C)c1ccc(OC)c(-c2ccc(F)cc2)c1
P097  O=C(NCCCNCCCCNCCCNC(=O)C(Cc1ccccc1)c1ccccc1)C(Cc1ccccc1)c1ccccc1.O=C(O)C(F)(F)F.O=C(O)C(F)(F)F
P098  O=S(=O)(NCc1ccccc1Br)c1ccccc1CO
P099  CC#Cc1c(C=O)cccc1OCOC
P100  O=C1NC(c2ccc([N+](=O)[O-])cc2)Nc2ccccc21
P101  CCCCCCCCC(=O)c1ccc(OC)cc1CC(=O)OCC
## batch 7
P102  Cc1ccc(S(=O)(=O)NC(CC(C)C)C(=O)O)cc1
P103  CC#Cc1ccc2nc(-c3nn(C)c(C)c3CSc3nnc(-c4ccc(C)cc4)[nH]3)sc2c1
P104  O=C(OCC=Cc1ccccn1)c1cccnc1
P105  COC(=O)C(=O)CCC#C[Si](C)(C)C
P106  CCCCCCCCCCCc1ccc(C(=O)NS(=O)(=O)c2ccc(Cl)cc2)cc1
P107  COc1cccc(C(=O)C2(C)CC2(Cl)Cl)c1
P108  Cc1ccc(O)c(SC#N)c1
P109  CC(C)Cc1ccc(C(C)C(=O)NNS(=O)(=O)c2ccc(Cl)c(Cl)c2)cc1
P110  CC(C)C(NC(=O)OCc1ccccc1)C(=O)NC(C)(C)C
P111  Cc1ccc(-c2ccc(C(=O)CC(=O)NN=Cc3cccc(O)c3)n2C)cc1
P112  CC(C)CC1NC(CC(C)C)C(C(C)C)NC1=O
P113  COC(=O)C(C(=O)c1ccccc1)C(C[N+](=O)[O-])c1cn(COCC[Si](C)(C)C)c2ccccc12
P114  CN1CCC(c2ccccc2[N+](=O)[O-])C1C(=O)OC(C)(C)C
P115  Cc1ccc(S(=O)(=O)Nc2cc(Br)cc(Br)c2N)cc1
P116  O=C(CC(c1ccccc1)c1ccccc1)NCCCNCCCCNCCCNC(=O)CC(c1ccccc1)c1ccccc1.O=C(O)C(F)(F)F.O=C(O)C(F)(F)F
P117  CCOC(=O)CCCC=C(C)CCO[Si](c1ccccc1)(c1ccccc1)C(C)(C)C
P118  CCOC(=O)c1c(N)sc2c1CCC1=C2OC(N)=C(C#N)C1c1ccc(Cl)cc1
## batch 8
P119  O=C1C=CCCN1c1ccccn1
P120  CC(C)C(NC(=O)OC(C)(C)C)C(=O)NCc1ccccc1
P121  N#CCCNc1ccccc1
P122  C1=NN(c2ccccc2)CC1
P123  O=C(CCl)NN=Cc1ccc(Br)cc1
P124  O=C(Nc1ccccc1-c1nc2ccccc2s1)c1ccccc1C(F)(F)F
P125  O=S(=O)(NCc1cccc(Br)c1)c1ccccc1CO
P126  C=CCc1c(C)c(OC)c(C)c(OC)c1C
P127  COc1ccc(Oc2ccccc2Br)c(OC)c1
P128  COC(=O)C(O)CCC#C[Si](C)(C)C
P129  C#CCOC(=O)N(S(C)=O)C(C)(C)C
P130  CCOC(=O)c1c(N)sc2c1CCC1=C2C(c2ccc(Cl)cc2)C(C#N)=C(N)O1
P131  COc1cc2c(cc1OC)C(CC1(OC)c3ccccc3C(=O)N1Cc1ccccc1)=NCC2
P132  O=[N+]([O-])c1cccc(C2COCCO2)c1
P133  O=C(OCC=Cc1ccncc1)c1cccnc1
P134  CC(C)NC(=NS(=O)(=O)c1ccccc1[N+](=O)[O-])NC(C)C
P135  CC(C)NC(=NS(=O)(=O)c1ccc([N+](=O)[O-])cc1)NC(C)C
## batch 9
P136  CCOc1ccc2nc(CC(O)(c3cc(=O)oc4ccccc34)C(F)(F)F)ccc2c1
P137  CCOC(=O)CCCC(C)=CCO[Si](c1ccccc1)(c1ccccc1)C(C)(C)C
P138  Oc1ccc2nc(-c3ccccc3)ccc2c1
P139  CC(C)CC1NC(C(C)C)C(CC(C)C)NC1=O
P140  O=C1C=CCCN1c1cccnc1
P141  CCC(=O)c1ccc(C(O[Si](C)(C)C(C)(C)C)C(C)C)o1
P142  C#CC(C)c1ccc(-c2ccc(F)cc2)cc1OC
P143  C#CC(C)c1cc(-c2ccc(F)cc2)ccc1OC
P144  CC(=O)Cc1ccc(C(O[Si](C)(C)C(C)(C)C)C(C)C)o1
P145  CC(=O)Cc1cc(C(O[Si](C)(C)C(C)(C)C)C(C)C)co1
P146  C[Si](C)(C)c1c(OS(=O)(=O)c2ccc(Cl)cc2)ccc(F)c1F
P147  CC(C)(C)NC(=O)c1ccccn1
P148  C=CC=CC(=O)c1ccccc1C(=O)c1ccccc1
P149  O=C1c2ccccc2C(=O)C12C(/C=C/c1ccccc1)N(Cc1ccccc1)C(c1ccc(Cl)cc1)C1(C(=O)c3ccccc3C1=O)C2c1ccc(Cl)cc1
P150  COc1ccc(-c2coc3c(O)cc(O)cc3c2=O)cc1
P151  CC(C)Cc1ccc(C(C)C(=O)NNS(=O)(=O)c2ccc(Cl)cc2Cl)cc1
P152  CCN(CC)C(=O)c1c(-c2cc3ccccc3c3ccc(C)cc23)c2ccccc2c2ccccc12
## batch 10
P153  COc1ccc(NC(=O)CSc2nnc3n2c2ccccc2c2nnc(Cc4ccccc4)n23)cc1
P154  CCCCCCC(=O)CCCc1ccc(O)c(OC)c1
P155  C#CCN(C(=O)OC(C)(C)C)S(C)=O
P156  O=C1NC(c2ccccc2[N+](=O)[O-])Nc2ccccc21
P157  O=C(Nc1ccccc1-c1nc2ccccc2s1)c1ccc(C(F)(F)F)cc1
P158  CC(=CC(C)=C1SC(=Nc2ccc(C)cc2)C(=O)N1CCc1ccccc1)c1ccccc1
P159  NS(=O)(=O)c1cc(CNc2ccccc2O)ccc1Cl
P160  COc1cc2c(cc1OC)C(CC1(OC)C(=O)N(Cc3ccccc3)c3ccccc31)=NCC2
P161  O=S(=O)(NCc1ccc(Br)cc1)c1ccccc1CO
P162  Cc1cc([N+](=O)[O-])ccc1Oc1ccc(SC#N)cc1
P163  COc1c(-c2ccc(O)cc2)oc2cc(O)ccc2c1=O
P164  CC(=O)C(Br)=NNc1ccc(Cl)cc1
P165  CC(C)CC(NC(=O)OC(C)(C)C)C(=O)Nc1ccccc1
P166  C=CC(=O)Nc1ccc([N+](=O)[O-])cc1
P167  O=[N+]([O-])c1ccccc1C1COCCO1
P168  CCCCCCCCCCCc1ccc(S(=O)(=O)NC(=O)c2ccc(Cl)cc2)cc1
P169  Cc1cc(SC#N)ccc1O
## batch 11
P170  C1=NCCN1c1ccccc1
P171  FC(F)(F)c1ccc(CCCI)cc1
P172  O=C1c2ccccc2C(=O)C12C(c1ccc(Cl)cc1)C(c1ccc(Cl)cc1)N(Cc1ccccc1)C1(C(=O)c3ccccc3C1=O)C2/C=C/c1ccccc1
P173  COC(=O)C(NS(=O)(=O)c1ccc(C)cc1)C(C)C
P174  CCCCn1nc(-c2ccc(-c3ccccc3OC)cc2)c(-c2ccc(-c3ccccc3OC)cc2)n1
P175  O=C1NC(c2ccccc2)=CC(c2ccc(Cl)cc2)N1
