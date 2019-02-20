outDir = "190219_pt20"
DYPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190219_DY_pt20/"
TTPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190219_TT_pt20/"
WcPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190206_pt20/"
systs = ["central","PUWeight_up","PUWeight_down",
         "MuIDSF_up","MuIDSF_down","EleIDSF_up","EleIDSF_down",
         "LHEScaleWeight_muR_up","LHEScaleWeight_muR_down","LHEScaleWeight_muF_up","LHEScaleWeight_muF_down",
         "jesTotalUp","jesTotalDown","jerUp","jerDown",
         "XSec_W_up","XSec_W_down","XSec_DY_up","XSec_DY_down","XSec_TT_up","XSec_TT_down","XSec_ST_up","XSec_ST_down","XSec_VV_up","XSec_VV_down",
         "MCStat_up","MCStat_down","dataStat_up","dataStat_down"
         ]
plotExtra=True

outDir = outDir.rstrip('/')

def applyCuts(ln,reg=""):
    ln = ln.replace('ZMASSCUT','[85,95,\"invert\"]')
    ln = ln.replace('CVXBINNING','varBin1=[0.,0.2,0.4,0.6,0.8,1.],varBin2=[0.,0.2,0.4,0.6,0.8,1.]')
    if "central" in syst:
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME"')
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME"')
        ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="TTPATH"')
        ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="OS-SS Events",outDir="OUTDIR_SYSTNAME",rootPath="WCPATH"')
        ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="DYPATH"')
    elif "MCStat" in syst:
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME",MCStat="SYSTNAME"')
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME",MCStat="SYSTNAME"')
        ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",MCStat="SYSTNAME",rootPath="TTPATH"')
        ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="OS-SS Events",outDir="OUTDIR_SYSTNAME",MCStat="SYSTNAME",rootPath="WCPATH"')
        ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="DYPATH",MCStat="SYSTNAME"')
    elif "dataStat" in syst:
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME",dataStat="SYSTNAME"')
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME",dataStat="SYSTNAME"')
        ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",dataStat="SYSTNAME",rootPath="TTPATH"')
        ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="OS-SS Events",outDir="OUTDIR_SYSTNAME",dataStat="SYSTNAME",rootPath="WCPATH"')
        ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="DYPATH",dataStat="SYSTNAME"')
    elif syst.startswith("je"):
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME",pathSuff="_SYSTNAME"')
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME",pathSuff="_SYSTNAME"')
        ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",pathSuff="_SYSTNAME",rootPath="TTPATH"')
        ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="OS-SS Events",outDir="OUTDIR_SYSTNAME",pathSuff="_SYSTNAME",rootPath="WCPATH"')
        ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="DYPATH",pathSuff="_SYSTNAME"')
    elif "XSec" in syst:
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME",useXSecUnc="SYSTNAME"')
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME",useXSecUnc="SYSTNAME"')
        ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",useXSecUnc="SYSTNAME",rootPath="TTPATH"')
        ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="OS-SS Events",outDir="OUTDIR_SYSTNAME",useXSecUnc="SYSTNAME",rootPath="WCPATH"')
        ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="DYPATH",useXSecUnc="SYSTNAME"')
    # elif "LepID" in syst:
    #     direc = syst.split('_')[-1]
    #     # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned*EleIDSF_DIRECTION",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME"')
    #     # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned*MuIDSF_DIRECTION",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME"')
    #     ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight*MuIDSF_DIRECTION*EleIDSF_DIRECTION",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME"')
    #     ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight*EleIDSF_DIRECTION",DataWeightName="eventWeight",yTitle="OS-SS Events",outDir="OUTDIR_SYSTNAME"')
    #     ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight*MuIDSF_DIRECTION",DataWeightName="eventWeight",yTitle="OS-SS Events",outDir="OUTDIR_SYSTNAME"')
    #     ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight*MuIDSF_DIRECTION",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="DYPATH"')
    #     ln = ln.replace('DIRECTION',direc)
    else:
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned*SYSTNAME",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME"')
        # ln = ln.replace('TTWEIGHT','MCWeightName="eventWeightUnsigned*SYSTNAME",DataWeightName="eventWeightUnsigned",yTitle="OS+SS Events",outDir="OUTDIR_SYSTNAME"')
        ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight*SYSTNAME",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="TTPATH"')
        ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight*SYSTNAME",DataWeightName="eventWeight",yTitle="OS-SS Events",outDir="OUTDIR_SYSTNAME",rootPath="WCPATH"')
        ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight*SYSTNAME",DataWeightName="eventWeight",yTitle="Events",outDir="OUTDIR_SYSTNAME",rootPath="DYPATH"')

    ln = ln.replace('OUTDIR',outDir)
    ln = ln.replace('SYSTNAME',syst)
    ln = ln.replace('DYPATH',DYPath)
    ln = ln.replace('TTPATH',TTPath)
    ln = ln.replace('WCPATH',WcPath)

    ln = ln.replace('ESEL','selections=["is_E","signWeight","jetMuPt_by_jetPt",QCDSELE,"jet_nJet"]')    # ,["jet_CvsB","muJet_idx"]
    ln = ln.replace('ECUT','cuts=[[1,1],[-1,1],[0,0.6],QCDCUTE,[0,4]]')
    ln = ln.replace('MSEL','selections=["is_M","Z_Mass","Z_Mass","signWeight","jetMuPt_by_jetPt",QCDSELM,"jet_nJet"]')
    ln = ln.replace('MCUT','cuts=[[1,1],[85,95,\"invert\"],[0,12,\"invert\"],[-1,1],[0,0.4],QCDCUTM,[0,4]]')                             #,[-1,0.5],[1,1e4]]

    # # DY CR
    # ln = ln.replace('DYSEL','selections=["is_M","signWeight","jetMuPt_by_jetPt",QCDSELM,"jet_nJet"]')            #  #  ,["jet_muEF","muJet_idx"],"jetMu_iso"]')     #["jet_lepFiltCustom","muJet_idx"],
    # ln = ln.replace('DYCUT','cuts=[[1,1],[-1,1],[0.4,1.5],QCDCUTM,[0,4]]')

    # ttbar CR
    # ln = ln.replace('TTSELEE','selections=["is_E","signWeight","jetMuPt_by_jetPt",QCDSELE,"jet_nJet"]')    #
    # ln = ln.replace('TTCUTEE','cuts=[[1,1],[-1,1],[0,0.6],QCDCUTE,[5,100]]')
    # ln = ln.replace('TTSELMM','selections=["is_M","Z_Mass","Z_Mass","signWeight","jetMuPt_by_jetPt",QCDSELM,"jet_nJet"]')
    # ln = ln.replace('TTCUTMM','cuts=[[1,1],[85,95,\"invert\"],[0,12,\"invert\"],[-1,1],[0,0.4],QCDCUTM,[5,100]]')                             #,[-1,0.5],[1,1e4]]
    ln = ln.replace('TTSELME','selections=["is_ME"]')
    ln = ln.replace('TTCUTME','cuts=[[1,1]]')
    ln = ln.replace('TTSELMM','selections=["is_MM","Z_Mass","met_Pt"]')
    ln = ln.replace('TTCUTMM','cuts=[[1,1],[75,105,"reverse"],[40,1e4]]')
    ln = ln.replace('TTSELEE','selections=["is_EE","Z_Mass","met_Pt"]')
    ln = ln.replace('TTCUTEE','cuts=[[1,1],[75,105,"reverse"],[40,1e4]]')

    ln = ln.replace('QCDSELM','["M_RelIso",0],"hardMu_Jet_PtRatio",["M_dz",0],["M_dxy",0],["M_sip3d",0]')
    ln = ln.replace('QCDCUTM','[0,0.05],[0,0.75,"reverse"],[-0.01,0.01],[-0.002,0.002],[0,2]')
    ln = ln.replace('QCDSELE','["E_RelIso",0],"hardE_Jet_PtRatio",["E_dz",0],["E_dxy",0],["E_sip3d",0]')
    ln = ln.replace('QCDCUTE','[0,0.05],[0,0.75,"reverse"],[-0.02,0.02],[-0.01,0.01],[0,2.5]')

    if not reg=="": ln = ln.replace('REG',reg)
    return ln

arguments = '''
           ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,MSEL,MCUT,dataset="smu",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="Wc_m",makeROOT=True,WCWEIGHT
           ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,ESEL,ECUT,dataset="sele",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="Wc_e",makeROOT=True,WCWEIGHT

           ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSELMM,TTCUTMM,dataset="dmu",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="TT_mm",makeROOT=True,TTWEIGHT
           ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSELEE,TTCUTEE,dataset="deg",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="TT_ee",makeROOT=True,TTWEIGHT
           ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSELME,TTCUTME,dataset="mue",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="TT_me",makeROOT=True,TTWEIGHT

           ["jet_CvsL",0],"CvsL",5,0,1,dataset="dmu",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="DY_m",makeROOT=True,DYWEIGHT
'''

onlyCentral = '''
            "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (mu)",25,0,25,MSEL,MCUT,dataset="smu",WCWEIGHT
            "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (e)",25,0,25,ESEL,ECUT,dataset="sele",WCWEIGHT
           ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (mu)",25,0,100,MSEL,MCUT,dataset="smu",WCWEIGHT
            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e)",25,0,100,ESEL,ECUT,dataset="sele",WCWEIGHT
            ["jet_Eta","muJet_idx"],r"#eta_{jet} (mu)",20,-2.8,2.8,MSEL,MCUT,dataset="smu",WCWEIGHT
            ["jet_Eta","muJet_idx"],r"#eta_{jet} (e)",20,-2.8,2.8,ESEL,ECUT,dataset="sele",WCWEIGHT
            ["jet_Phi","muJet_idx"],r"#phi_{jet} (mu)",20,-3.2,3.2,MSEL,MCUT,dataset="smu",WCWEIGHT
            ["jet_Phi","muJet_idx"],r"#phi_{jet} (e)",20,-3.2,3.2,ESEL,ECUT,dataset="sele",WCWEIGHT

              ["jet_CvsL","muJet_idx"],r"Jet CvsL (mu)",25,0,1,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
              ["jet_CvsL","muJet_idx"],r"Jet CvsL (e)",25,0,1,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT
              ["jet_CvsB","muJet_idx"],r"Jet CvsB (mu)",25,0,1,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
              ["jet_CvsB","muJet_idx"],r"Jet CvsB (e)",25,0,1,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT


             "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (#mu #mu)",25,0,25,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
             "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (e e)",25,0,25,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
             "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (#mu e)",25,0,25,TTSELME,TTCUTME,dataset="mue",TTWEIGHT
            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu #mu)",25,0,100,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e e)",25,0,100,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu e)",25,0,100,TTSELME,TTCUTME,dataset="mue",TTWEIGHT
            ["jet_Eta","muJet_idx"],r"#eta_{jet} (#mu #mu)",20,-2.8,2.8,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
            ["jet_Eta","muJet_idx"],r"#eta_{jet} (e e)",20,-2.8,2.8,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
            ["jet_Eta","muJet_idx"],r"#eta_{jet} (#mu e)",20,-2.8,2.8,TTSELME,TTCUTME,dataset="mue",TTWEIGHT
            ["jet_Phi","muJet_idx"],r"#phi_{jet} (#mu #mu)",20,-3.2,3.2,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
            ["jet_Phi","muJet_idx"],r"#phi_{jet} (e e)",20,-3.2,3.2,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
            ["jet_Phi","muJet_idx"],r"#phi_{jet} (#mu e)",20,-3.2,3.2,TTSELME,TTCUTME,dataset="mue",TTWEIGHT
              ["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu #mu)",25,0,1,TTSELMM,TTCUTMM,dataset="dmu",makeROOT=True,TTWEIGHT
              ["jet_CvsL","muJet_idx"],r"Jet CvsL (e e)",25,0,1,TTSELEE,TTCUTEE,dataset="deg",makeROOT=True,TTWEIGHT
              ["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu e)",25,0,1,TTSELME,TTCUTME,dataset="mue",makeROOT=True,TTWEIGHT
              ["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu #mu)",25,0,1,TTSELMM,TTCUTMM,dataset="dmu",makeROOT=True,TTWEIGHT
              ["jet_CvsB","muJet_idx"],r"Jet CvsB (e e)",25,0,1,TTSELEE,TTCUTEE,dataset="deg",makeROOT=True,TTWEIGHT
              ["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu e)",25,0,1,TTSELME,TTCUTME,dataset="mue",makeROOT=True,TTWEIGHT



            ["jet_Phi",0],r"#phi_{jet}",20,-3.2,3.2,dataset="dmu",DYWEIGHT
            ["jet_Eta",0],r"#eta_{jet}",20,-2.8,2.8,dataset="dmu",DYWEIGHT
            ["jet_Pt",0],r"p^{jet}_{T} [GeV]",25,0,100,dataset="dmu",DYWEIGHT
             ["jet_CvsL",0],r"Jet CvsL",25,0,1,dataset="dmu",makeROOT=True,DYWEIGHT
             ["jet_CvsB",0],r"Jet CvsB",25,0,1,dataset="dmu",makeROOT=True,DYWEIGHT
'''

# Jobs
cmdList = open("cmdList.txt","w")
for systname in systs:
    global syst
    syst=systname
    args=[applyCuts(line.strip()) for line in arguments.split("\n") if not line.strip()=="" and not line.strip().startswith("#")]
    for i, line in enumerate(args):
#        cmdList.write("import Stacker; ")
        cmdList.write("Stacker.plotStack("+line.strip()+")\n")

    if plotExtra and "central" in systname:
        args=[applyCuts(line.strip()) for line in onlyCentral.split("\n") if not line.strip()=="" and not line.strip().startswith("#")]
        for i, line in enumerate(args):
    #        cmdList.write("import Stacker; ")
            cmdList.write("Stacker.plotStack("+line.strip()+")\n")
cmdList.close()
