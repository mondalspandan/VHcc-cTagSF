import os, time, sys, Stacker
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV]",15,0,25,dataset="smu")
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV] (1 mu), HT > 100",15,0,25,selections=["is_M","HT"],cuts=[[1,1],[100,1e4]],dataset="smu")
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV] (1 e), HT > 100",15,0,25,selections=["is_E","HT"],cuts=[[1,1],[100,1e4]],dataset="sele")
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 25<p^{jet}_{T}<35 + 1 mu",15,0,25,selections=[["jet_Pt","muJet_idx"],"is_M"],cuts=[[25,35],[1,1]])
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 25<p^{jet}_{T}<35 + 1 e",15,0,25,selections=[["jet_Pt","muJet_idx"],"is_E"],cuts=[[25,35],[1,1]])
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 35<p^{jet}_{T}<50",15,0,25,selections=[["jet_Pt","muJet_idx"]],cuts=[[35,50]])
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 50<p^{jet}_{T}<70",15,0,25,selections=[["jet_Pt","muJet_idx"]],cuts=[[50,70]])
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 70<p^{jet}_{T}<200",15,0,25,selections=[["jet_Pt","muJet_idx"]],cuts=[[70,200]])

DYPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190219_DY_pt20/"
TTPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190219_TT_pt20/"
WcPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190206_pt20/"

if len(sys.argv) > 1:
    start_idx = 1 + float(sys.argv[1])
else:
    start_idx = 1

def applyCuts(ln,reg=""):
    ln = ln.replace('ZMASSCUT','[85,95,\"invert\"]')
    # ln = ln.replace('CVXBINNING','varBin1=[0.,0.2,0.4,0.6,0.8,1.],varBin2=[0.,0.2,0.4,0.6,0.8,1.]')
    ln = ln.replace('CVXBINNING','varBin1=[0.,0.2,0.35,0.5,0.7,1.],varBin2=[0.,0.2,0.35,0.5,0.7,1.]')


    ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",filePre="TT",rootPath="'+TTPath+'"')
    ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="OS-SS Events",filePre="Wc",rootPath="'+WcPath+'"')
    ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",filePre="DY",rootPath="'+DYPath+'"')

#    ln = ln.replace('CVXBINNING','varBin1=[0,0.2,0.35,0.5,0.7,1.],varBin2=[0,0.4,0.525,0.65,0.8,1.]')
    # ln = ln.replace('CVXBINNING','makeCustomH=True')

    ln = ln.replace('ESEL','selections=["is_E","signWeight","jetMuPt_by_jetPt",QCDSELE,"jet_nJet"]')    # ,["jet_CvsB","muJet_idx"]
    ln = ln.replace('ECUT','cuts=[[1,1],[-1,1],[0,0.6],QCDCUTE,[0,4]]')
    ln = ln.replace('MSEL','selections=["is_M","Z_Mass","Z_Mass","signWeight","jetMuPt_by_jetPt",QCDSELM,"jet_nJet"]')
    ln = ln.replace('MCUT','cuts=[[1,1],[85,95,\"invert\"],[0,12,\"invert\"],[-1,1],[0,0.4],QCDCUTM,[0,4]]')                             #,[-1,0.5],[1,1e4]]

    # # ttbar CR
    # ln = ln.replace('TTSELE','selections=["is_E","signWeight","jetMuPt_by_jetPt",QCDSELE,"jet_nJet"]')    #
    # ln = ln.replace('TTCUTE','cuts=[[1,1],[-1,1],[0,0.6],QCDCUTE,[5,100]]')
    # ln = ln.replace('TTSELM','selections=["is_M","Z_Mass","Z_Mass","signWeight","jetMuPt_by_jetPt",QCDSELM,"jet_nJet"]')
    # ln = ln.replace('TTCUTM','cuts=[[1,1],[85,95,\"invert\"],[0,12,\"invert\"],[-1,1],[0,0.4],QCDCUTM,[5,100]]')                             #,[-1,0.5],[1,1e4]]

    ln = ln.replace('TTSELME','selections=["is_ME"]')
    ln = ln.replace('TTCUTME','cuts=[[1,1]]')
    ln = ln.replace('TTSELMM','selections=["is_MM","Z_Mass","met_Pt"]')
    ln = ln.replace('TTCUTMM','cuts=[[1,1],[75,105,"reverse"],[40,1e4]]')
    ln = ln.replace('TTSELEE','selections=["is_EE","Z_Mass","met_Pt"]')
    ln = ln.replace('TTCUTEE','cuts=[[1,1],[75,105,"reverse"],[40,1e4]]')

#    ln = ln.replace(',QCDSELM','')
#    ln = ln.replace(',QCDCUTM','')
#    ln = ln.replace(',QCDSELE','')
#    ln = ln.replace(',QCDCUTE','')

    ln = ln.replace('QCDSELM','["M_RelIso",0],"hardMu_Jet_PtRatio",["M_dz",0],["M_dxy",0],["M_sip3d",0]')
    ln = ln.replace('QCDCUTM','[0,0.05],[0,0.75,"reverse"],[-0.01,0.01],[-0.002,0.002],[0,2]')
    ln = ln.replace('QCDSELE','["E_RelIso",0],"hardE_Jet_PtRatio",["E_dz",0],["E_dxy",0],["E_sip3d",0]')
    ln = ln.replace('QCDCUTE','[0,0.05],[0,0.75,"reverse"],[-0.02,0.02],[-0.01,0.01],[0,2.5]')

    if not reg=="": ln = ln.replace('REG',reg)
    return ln

arguments = '''
    # Wc selection
           # "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (mu)",25,0,25,MSEL,MCUT,dataset="smu",WCWEIGHT
           # "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (e)",25,0,25,ESEL,ECUT,dataset="sele",WCWEIGHT
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (mu)",25,0,100,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
#             ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e)",25,0,100,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT
#             ["jet_Eta","muJet_idx"],r"#eta_{jet} (mu)",20,-2.8,2.8,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
#             ["jet_Eta","muJet_idx"],r"#eta_{jet} (e)",20,-2.8,2.8,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT
#             ["jet_Phi","muJet_idx"],r"#phi_{jet} (mu)",20,-3.2,3.2,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
#             ["jet_Phi","muJet_idx"],r"#phi_{jet} (e)",20,-3.2,3.2,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT

               ["jet_CvsL","muJet_idx"],r"Jet CvsL (mu)",25,0,1,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
               ["jet_CvsL","muJet_idx"],r"Jet CvsL (e)",25,0,1,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT
               ["jet_CvsB","muJet_idx"],r"Jet CvsB (mu)",25,0,1,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
               ["jet_CvsB","muJet_idx"],r"Jet CvsB (e)",25,0,1,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT
#             ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,MSEL,MCUT,dataset="smu",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,WCWEIGHT
#             ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,ESEL,ECUT,dataset="sele",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="2D_e",makeROOT=True,WCWEIGHT


    # Semileptonic TT
#             "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (mu)",25,0,25,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTWEIGHT
#             "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (e)",25,0,25,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTWEIGHT
#             ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (mu)",25,0,100,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTWEIGHT
#             ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e)",25,0,100,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTWEIGHT
#             ["jet_Eta","muJet_idx"],r"#eta_{jet} (mu)",20,-2.8,2.8,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTWEIGHT
#             ["jet_Eta","muJet_idx"],r"#eta_{jet} (e)",20,-2.8,2.8,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTWEIGHT
#             ["jet_Phi","muJet_idx"],r"#phi_{jet} (mu)",20,-3.2,3.2,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTWEIGHT
#             ["jet_Phi","muJet_idx"],r"#phi_{jet} (e)",20,-3.2,3.2,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTWEIGHT
#               ["jet_CvsL","muJet_idx"],r"Jet CvsL (mu)",25,0,1,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTWEIGHT
#               ["jet_CvsL","muJet_idx"],r"Jet CvsL (e)",25,0,1,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTWEIGHT
#               ["jet_CvsB","muJet_idx"],r"Jet CvsB (mu)",25,0,1,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTWEIGHT
#               ["jet_CvsB","muJet_idx"],r"Jet CvsB (e)",25,0,1,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTWEIGHT
#            ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSELM,TTCUTM,dataset="smu",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTWEIGHT
#            ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSELE,TTCUTE,dataset="sele",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="2D_e",makeROOT=True,TTWEIGHT

#             "met_Pt",r"E^{miss}_{T}",30,0,300,TTSEL,TTCUT,dataset="",TTWEIGHT

#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (#mu e)",20,-3.2,3.2,TTSELME,TTCUTME,dataset="smu",TTWEIGHT
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (#mu e)",20,-2.8,2.8,TTSELME,TTCUTME,dataset="smu",TTWEIGHT
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu e)",28,20,300,TTSELME,TTCUTME,dataset="smu",TTWEIGHT

#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (e e)",20,-3.2,3.2,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (e e)",20,-2.8,2.8,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e e)",28,20,300,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT

#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (#mu #mu)",20,-3.2,3.2,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (#mu #mu)",20,-2.8,2.8,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu #mu)",28,20,300,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT

#              ["jet_CvsL","muJet_idx"],"Jet CvsL",25,0,1,TTSEL,TTCUT,dataset="",makeROOT=True,TTWEIGHT
#              ["jet_CvsB","muJet_idx"],"Jet CvsB",25,0,1,TTSEL,TTCUT,dataset="",makeROOT=True,TTWEIGHT
#            ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSEL,TTCUT,dataset="",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTWEIGHT



    # Dileptonic TT
            ["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu e)",25,0,1,TTSELME,TTCUTME,dataset="mue",makeROOT=True,TTWEIGHT
            ["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu e)",25,0,1,TTSELME,TTCUTME,dataset="mue",makeROOT=True,TTWEIGHT
#            ["jet_CvsL",0],"CvsL",5,0,1,TTSELME,TTCUTME,dataset="smu",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTWEIGHT
#           
            ["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu #mu)",25,0,1,TTSELMM,TTCUTMM,dataset="dmu",makeROOT=True,TTWEIGHT
            ["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu #mu)",25,0,1,TTSELMM,TTCUTMM,dataset="dmu",makeROOT=True,TTWEIGHT
#            ["jet_CvsL",0],"CvsL",5,0,1,TTSELMM,TTCUTMM,dataset="dmu",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTWEIGHT
#           
            ["jet_CvsL","muJet_idx"],r"Jet CvsL (e e)",25,0,1,TTSELEE,TTCUTEE,dataset="deg",makeROOT=True,TTWEIGHT
            ["jet_CvsB","muJet_idx"],r"Jet CvsB (e e)",25,0,1,TTSELEE,TTCUTEE,dataset="deg",makeROOT=True,TTWEIGHT
#            ["jet_CvsL",0],"CvsL",5,0,1,TTSELEE,TTCUTEE,dataset="deg",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTWEIGHT


        # DY
#           "met_Pt",r"E^{miss}_{T}",25,0,100,dataset="dmu",DYWEIGHT
#             ["jet_Phi",0],r"#phi_{jet}",20,-3.2,3.2,dataset="dmu",DYWEIGHT
#             ["jet_Eta",0],r"#eta_{jet}",20,-2.8,2.8,dataset="dmu",DYWEIGHT
#             ["jet_Pt",0],r"p^{jet}_{T} [GeV]",25,0,100,dataset="dmu",DYWEIGHT
              ["jet_CvsL",0],"Jet CvsL",25,0,1,dataset="dmu",makeROOT=True,DYWEIGHT
              ["jet_CvsB",0],"Jet CvsB",25,0,1,dataset="dmu",makeROOT=True,DYWEIGHT
#            ["jet_CvsL",0],"CvsL",5,0,1,dataset="dmu",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,DYWEIGHT
            '''


'''
LegacyArguments =
            "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (mu)",25,0,25,MSEL,MCUT,dataset="smu"
            "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (e)",25,0,25,ESEL,ECUT,dataset="sele"

           ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (mu)",25,0,100,MSEL,MCUT,dataset="smu"
           ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e)",25,0,100,ESEL,ECUT,dataset="sele"
           #
            ["jet_Eta","muJet_idx"],r"#eta_{jet} (mu)",20,-2.8,2.8,MSEL,MCUT,dataset="smu"
            ["jet_Eta","muJet_idx"],r"#eta_{jet} (e)",20,-2.8,2.8,ESEL,ECUT,dataset="sele"

            ["jet_Phi","muJet_idx"],r"#phi_{jet} (mu)",20,-3.2,3.2,MSEL,MCUT,dataset="smu"
            ["jet_Phi","muJet_idx"],r"#phi_{jet} (e)",20,-3.2,3.2,ESEL,ECUT,dataset="sele"

#            ["jet_Mass","muJet_idx"],r"m_{jet} [GeV] (mu)",20,0,40,MSEL,MCUT,dataset="smu"
#            ["jet_Mass","muJet_idx"],r"m_{jet} [GeV] (e)",20,0,40,ESEL,ECUT,dataset="sele"
#
#
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (mu)",25,0,100,TTSELM,TTCUTM,dataset="smu"
#           ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e)",25,0,100,TTSELE,TTCUTE,dataset="sele"
#           #
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (mu)",20,-2.8,2.8,TTSELM,TTCUTM,dataset="smu"
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (e)",20,-2.8,2.8,TTSELE,TTCUTE,dataset="sele"
#
#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (mu)",20,-3.2,3.2,TTSELM,TTCUTM,dataset="smu"
#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (e)",20,-3.2,3.2,TTSELE,TTCUTE,dataset="sele"

#            ["jet_Mass","muJet_idx"],r"m_{jet} [GeV] (mu)",20,0,40,TTSELM,TTCUTM,dataset="smu"
#            ["jet_Mass","muJet_idx"],r"m_{jet} [GeV] (e)",20,0,40,TTSELE,TTCUTE,dataset="sele"



            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (mu)",25,0,100,DYSEL,DYCUT,dataset="smu"
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (mu)",20,-2.8,2.8,DYSEL,DYCUT,dataset="smu"
#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (mu)",20,-3.2,3.2,DYSEL,DYCUT,dataset="smu"
#            ["jet_Mass","muJet_idx"],r"m_{jet} [GeV] (mu)",20,0,40,DYSEL,DYCUT,dataset="smu"




#           "jet_nJet","# jets [GeV] (mu)",10,0,10,MSEL,MCUT,dataset="smu"
#             "jet_nJet","# jets [GeV] (e)",10,0,10,ESEL,ECUT,dataset="sele"

#            ["jet_btagCMVA","muJet_idx"],r"Jet cMVAv2 (mu)",25,-1,1,MSEL,MCUT,dataset="smu"
#            ["jet_btagCMVA","muJet_idx"],r"Jet cMVAv2 (e)",25,-1,1,ESEL,ECUT,dataset="sele"

#            ["jet_btagCSVV2","muJet_idx"],r"Jet CSVv2 (mu)",25,0,1,MSEL,MCUT,dataset="smu"
#            ["jet_btagCSVV2","muJet_idx"],r"Jet CSVv2 (e)",25,0,1,ESEL,ECUT,dataset="sele"

#            ["jet_btagDeepB","muJet_idx"],r"Jet DeepCSV b+bb (mu)",25,0,1,MSEL,MCUT,dataset="smu"
#            ["jet_btagDeepB","muJet_idx"],r"Jet DeepCSV b+bb (e)",25,0,1,ESEL,ECUT,dataset="sele"

#            ["jet_btagDeepC","muJet_idx"],r"Jet DeepCSV c (mu)",25,0,1,MSEL,MCUT,dataset="smu"
#            ["jet_btagDeepC","muJet_idx"],r"Jet DeepCSV c (e)",25,0,1,ESEL,ECUT,dataset="sele"

#            ["jet_CvsL","muJet_idx"],r"Jet CvsL (mu)",25,0,1,MSEL,MCUT,dataset="smu",makeROOT=True
#           ["jet_CvsL","muJet_idx"],r"Jet CvsL (e)",25,0,1,ESEL,ECUT,dataset="sele",makeROOT=True

#           ["jet_CvsB","muJet_idx"],r"Jet CvsB (mu)",25,0,1,MSEL,MCUT,dataset="smu",makeROOT=True
#           ["jet_CvsB","muJet_idx"],r"Jet CvsB (e)",25,0,1,ESEL,ECUT,dataset="sele",makeROOT=True

#           ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,MSEL,MCUT,dataset="smu",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="2D_m",makeROOT=True
#           ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,ESEL,ECUT,dataset="sele",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",filePre="2D_e",makeROOT=True

           # ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,MSEL,MCUT,brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="col text",filePre="2D_m_heat"
           # ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,ESEL,ECUT,brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="col text",filePre="2D_e_heat"


#             "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (no PU wt) (e)",25,0,25,ESEL,ECUT,dataset="sele",MCWeightName="eventWeightnoPU",filePre="NoPUWt"
#
#             "numOf_cJet",r"# LHE c jets (e)",4,0,4,ESEL,ECUT
#             "numOf_cJet",r"# LHE c jets (mu)",4,0,4,MSEL,MCUT

#             "jetMu_iso",r"Soft Muon rel. isolation (R = 0.4) (mu)",40,0,8,MSEL,MCUT,dataset="smu"
#             "jetMu_iso",r"Soft Muon rel. isolation (R = 0.4) (e)",40,0,8,ESEL,ECUT,dataset="sele"
#
#             "jetMuPt_by_jetPt",r"p^{soft #mu}_{T}/p^{jet}_{T} (mu)",20,0,1,MSEL,MCUT,dataset="smu"
#             "jetMuPt_by_jetPt",r"p^{soft #mu}_{T}/p^{jet}_{T} (e)",20,0,1,ESEL,ECUT,dataset="sele"
#
#             "jetMu_PtRel",r"p^{soft #mu}_{T,rel} (mu)",25,0,2.5,MSEL,MCUT,dataset="smu"
#             "jetMu_PtRel",r"p^{soft #mu}_{T,rel} (e)",25,0,2.5,ESEL,ECUT,dataset="sele"
#
            # "nPV","Number of reconstructed PVs (mu)",25,0,50,MSEL,MCUT,dataset="smu"
            # "nPV","Number of reconstructed PVs (e)",25,0,50,ESEL,ECUT,dataset="sele"
            #
            # "nPV","Number of reconstructed PVs (mu)",25,0,50,MSEL,MCUT,dataset="smu",MCWeightName="eventWeightnoPU",filePre="NoPUWt"
            # "nPV","Number of reconstructed PVs (e)",25,0,50,ESEL,ECUT,dataset="sele",MCWeightName="eventWeightnoPU",filePre="NoPUWt"
#
#             ["jet_muEF","muJet_idx"],"Jet Muon Energy fraction (mu)",25,0,1,MSEL,MCUT,dataset="smu"
#             ["jet_muEF","muJet_idx"],"Jet Muon Energy fraction (e)",25,0,1,ESEL,ECUT,dataset="sele"

#            "nPVGood","Number of good reconstructed PVs (mu)",40,0,40,MSEL,MCUT,dataset="smu"
#            "nPVGood","Number of good reconstructed PVs (e)",40,0,40,ESEL,ECUT,dataset="sele"

#             "muptbyjetpt",r"p^{#mu}_{T}/p^{jet}_{T} (no cuts) (mu)",20,0,1,selections=["is_M","Z_Mass"],cuts=[[1,1],[85,95,\"invert\"]],dataset="smu",filePre="NoCuts"
#             "muptbyjetpt",r"p^{#mu}_{T}/p^{jet}_{T} (no cuts) (e)",20,0,1,selections=["is_E"],cuts=[[1,1]],dataset="sele",filePre="NoCuts"

#            "jetMu_sip3d",r"Soft Muon IP3D Sig (mu)",40,0,8,MSEL,MCUT,dataset="smu"
#            "jetMu_sip3d",r"Soft Muon IP3D Sig (e)",40,0,8,ESEL,ECUT,dataset="sele"
#
            # ["E_Pt",0],r"p^{hard e}_{T} [GeV] (e)",30,0,150,ESEL,ECUT,dataset="sele"
            # ["M_Pt",0],r"p^{hard #mu}_{T} [GeV] (mu)",30,0,150,MSEL,MCUT,dataset="smu"

#             ["E_Pt",0],r"p^{hard e}_{T} [GeV] (e)",30,0,150,ESEL,ECUT,dataset="sele",isLog=True,MCWeightName="eventWeight/EleIDSF",filePre="NoEWeight"
#             ["M_Pt",0],r"p^{hard #mu}_{T} [GeV] (mu)",30,0,150,MSEL,MCUT,dataset="smu",isLog=True,MCWeightName="eventWeight/MuIDSF",filePre="NoMuWeight"

#             ["E_Eta",0],r"#eta^{hard e}_{T} [GeV] (e)",28,-2.8,2.8,ESEL,ECUT,dataset="sele"
#             ["M_Eta",0],r"#eta^{hard #mu}_{T} [GeV] (mu)",28,-2.8,2.8,MSEL,MCUT,dataset="smu"

#             ["E_Eta",0],r"#eta^{hard e}_{T} [GeV] (e)",28,-2.8,2.8,ESEL,ECUT,dataset="sele",MCWeightName="eventWeight/EleIDSF",filePre="NoEWeight"
#             ["M_Eta",0],r"#eta^{hard #mu}_{T} [GeV] (mu)",28,-2.8,2.8,MSEL,MCUT,dataset="smu",MCWeightName="eventWeight/MuIDSF",filePre="NoMuWeight"

#             ["E_dz",0],"Hard electron dz (e)",40,-0.2,0.2,ESEL,ECUT,dataset="sele"
#             ["M_dz",0],"Hard muon dz (mu)",40,-0.2,0.2,MSEL,MCUT,dataset="smu"
#
#             ["E_dxy",0],"Hard electron dxy (e)",40,-0.04,0.04,ESEL,ECUT,dataset="sele"
#             ["M_dxy",0],"Hard muon dxy (mu)",40,-0.04,0.04,MSEL,MCUT,dataset="smu"

#             ["E_dz",0],"Hard electron dz (e)",40,-0.05,0.05,ESEL,ECUT,dataset="sele",filePre="zoomed"
#             ["M_dz",0],"Hard muon dz (mu)",40,-0.05,0.05,MSEL,MCUT,dataset="smu",filePre="zoomed"
#
#             ["E_dxy",0],"Hard electron dxy (e)",40,-0.015,0.015,ESEL,ECUT,dataset="sele",filePre="zoomed"
#             ["M_dxy",0],"Hard muon dxy (mu)",40,-0.01,0.01,MSEL,MCUT,dataset="smu",filePre="zoomed"

#             ["E_sip3d",0],"Hard electron IP3D significance (e)",40,0,5,ESEL,ECUT,dataset="sele"
#             ["M_sip3d",0],"Hard muon IP3D significance (mu)",40,0,5,MSEL,MCUT,dataset="smu"

#             ["E_ip3d",0],"Hard electron IP3D (e)",40,0,0.01,ESEL,ECUT,dataset="sele",filePre="peak2"
#            ["M_ip3d",0],"Hard muon IP3D (mu)",40,0,0.01,MSEL,MCUT,dataset="smu",filePre="peak2"
#
#             ["E_RelIso",0],"Hard electron Rel Iso (R=0.3) (e)",20,0,0.10,ESEL,ECUT,dataset="sele"
#             ["M_RelIso",0],"Hard muon Rel Iso (R=0.4) (mu)",30,0,0.15,MSEL,MCUT,dataset="smu"
#
#             "hardE_Jet_PtRatio","p^{hard e}_{T}/p^{jet}_{T} (e)",40,0.4,1.2,ESEL,ECUT,dataset="sele"
#             "hardMu_Jet_PtRatio","p^{hard mu}_{T}/p^{jet}_{T} (mu)",40,0.4,1.2,MSEL,MCUT,dataset="smu"

#             "E_ip3derror","Hard electron IP3D error (e)",40,0,0.01,ESEL,ECUT,dataset="sele",filePre="peak2"
#             "M_ip3derror","Hard electron IP3D error (mu)",40,0,0.01,MSEL,MCUT,dataset="smu",filePre="peak2"


# n - 1
#             ["E_dz",0],"Hard electron dz (e)",40,-0.2,0.2,ESEL,ECUT,dataset="sele",nminus1=True
#             ["M_dz",0],"Hard muon dz (mu)",40,-0.2,0.2,MSEL,MCUT,dataset="smu",nminus1=True
#
#             ["E_dxy",0],"Hard electron dxy (e)",40,-0.04,0.04,ESEL,ECUT,dataset="sele",nminus1=True
#             ["M_dxy",0],"Hard muon dxy (mu)",40,-0.04,0.04,MSEL,MCUT,dataset="smu",nminus1=True
#
#             ["E_sip3d",0],"Hard electron IP3D significance (e)",40,0,6,ESEL,ECUT,dataset="sele",nminus1=True
#             ["M_sip3d",0],"Hard muon IP3D significance (mu)",40,0,6,MSEL,MCUT,dataset="smu",nminus1=True
#
#             ["E_ip3d",0],"Hard electron IP3D (e)",40,0,0.05,ESEL,ECUT,dataset="sele",nminus1=True
#             ["M_ip3d",0],"Hard muon IP3D (mu)",40,0,0.05,MSEL,MCUT,dataset="smu",nminus1=True
#
#             ["E_RelIso",0],"Hard electron Rel Iso (R=0.3) (e)",20,0,0.10,ESEL,ECUT,dataset="sele",nminus1=True
#             ["M_RelIso",0],"Hard muon Rel Iso (R=0.4) (mu)",30,0,0.15,MSEL,MCUT,dataset="smu",nminus1=True
#
#             "hardE_Jet_PtRatio","p^{hard e}_{T}/p^{jet}_{T} (e)",40,0.4,1.2,ESEL,ECUT,dataset="sele",nminus1=True
#             "hardMu_Jet_PtRatio","p^{hard mu}_{T}/p^{jet}_{T} (mu)",40,0.4,1.2,MSEL,MCUT,dataset="smu",nminus1=True
# -----
#            #


#            "dR_jet_jetMu",r"#Delta R_{jet, soft #mu} (mu)",20,0,0.4,MSEL,MCUT,dataset="smu"
#            "dR_jet_jetMu",r"#Delta R_{jet, soft #mu} (e)",20,0,0.4,ESEL,ECUT,dataset="sele"

#            "dPhi_muJet_MET",r"#Delta #phi_{jet, MET} (mu)",35,0,3.5,MSEL,MCUT,dataset="smu"
#            "dPhi_muJet_MET",r"#Delta #phi_{jet, MET} (e)",35,0,3.5,ESEL,ECUT,dataset="sele"

#            "min_dPhi_jet_MET",r"Minimum #Delta #phi_{jet, MET} (mu)",35,0,3.5,MSEL,MCUT,dataset="smu"
#            "min_dPhi_jet_MET",r"Minimum #Delta #phi_{jet, MET} (e)",35,0,3.5,ESEL,ECUT,dataset="sele"

##            "dR_lep_jet",r"#Delta R_{jet, hard #mu} (mu)",25,0,5,MSEL,MCUT,dataset="smu"
##            "dR_lep_jet",r"#Delta R_{jet, hard e} (e)",25,0,5,ESEL,ECUT,dataset="sele"

#            "met_Pt",r"E^{miss}_{T} (mu)",30,0,150,MSEL,MCUT,dataset="smu"
#            "met_Pt",r"E^{miss}_{T} (e)",30,0,150,ESEL,ECUT,dataset="sele"

#            "W_Pt",r"p^{W}_{T} [GeV] (mu)",50,0,300,MSEL,MCUT,dataset="smu"
#            "W_Pt",r"p^{W}_{T} [GeV] (e)",50,0,300,ESEL,ECUT,dataset="sele"

#            "W_Tmass",r"M^{W}_{T} [GeV] (mu)",30,0,300,MSEL,MCUT,dataset="smu"
#            "W_Tmass",r"M^{W}_{T} [GeV] (e)",30,0,300,ESEL,ECUT,dataset="sele"

#            "HT",r"HT [GeV] (mu)",20,0,400,MSEL,MCUT,dataset="smu"
#            "HT",r"HT [GeV] (e)",20,0,400,ESEL,ECUT,dataset="sele"

#            "LHE_HT",r"Generator HT [GeV] (mu)",20,0,400,MSEL,MCUT
#            "LHE_HT",r"Generator HT [GeV] (e)",20,0,400,ESEL,ECUT

#            "LHE_Njets",r"Generator nJets (mu)",10,0,10,MSEL,MCUT
#            "LHE_Njets",r"Generator nJets (e)",10,0,10,ESEL,ECUT

#            "Z_Mass",r"M_{#mu#mu} (no cuts) [GeV] (mu)",30,0,150,selections=["is_M"],cuts=[[1,1]],dataset="smu",filePre="noCuts"

##            "Z_Mass_best",r"Best M_{#mu#mu} [GeV] (mu)",30,0,150,selections=["is_M"],cuts=[[1,1]],dataset="smu"

#              "Z_Mass",r"M_{#mu#mu} [GeV] (n-1) (mu)",30,0,150,MSEL.remove("Z_Mass"),MCUT.remove([12,80]),dataset="smu",filePre="(n-1)"

#             ["jet_lepFiltCustom","muJet_idx"],r"Jet Lepton Filter (mu)",2,0,2,MSEL,MCUT,dataset="smu"
#             ["jet_lepFiltCustom","muJet_idx"],r"Jet Lepton Filter (e)",2,0,2,ESEL,ECUT,dataset="sele"

#            ["jet_lepFiltCustom","muJet_idx"],r"Jet Lepton Filter (N-1) (mu)",2,0,2,selections=["is_M","Z_Mass",["jet_muEF","muJet_idx"]],cuts=[[1,1],[85,95,\"invert\"],[-1,0.5]],dataset="smu",filePre="(n-1)"

#             ["jet_muEF","muJet_idx"],"Jet Muon Energy fraction (n-1) (mu)",25,0,1,selections=["is_M","Z_Mass","jetMu_iso"],cuts=[[1,1],[85,95,\"invert\"],[1,1e4]],dataset="smu",filePre="(n-1)"


#            "jetMu_dz",r"Soft Muon dz (mu)",40,-0.2,0.2,MSEL,MCUT,dataset="smu"
#            "jetMu_dz",r"Soft Muon dz (e)",40,-0.2,0.2,ESEL,ECUT,dataset="sele"

#            "jetMu_dxy",r"Soft Muon dxy (mu)",40,-0.04,0.04,MSEL,MCUT,dataset="smu"
#            "jetMu_dxy",r"Soft Muon dxy (e)",40,-0.04,0.04,ESEL,ECUT,dataset="sele"

#            "nMuJet","# jets with soft muon (mu)",4,0,4,MSEL,MCUT,dataset="smu"
#            "nMuJet","# jets with soft muon (e)",4,0,4,ESEL,ECUT,dataset="sele"


#             ["jet_chEmEF","muJet_idx"],"Jet charged EM Energy fraction (mu)",20,0,1,MSEL,MCUT,dataset="smu"
#             ["jet_chEmEF","muJet_idx"],"Jet charged EM Energy fraction (e)",20,0,1,ESEL,ECUT,dataset="sele"
#
#             ["jet_jetId","muJet_idx"],"Jet ID (mu)",4,0,4,MSEL,MCUT,dataset="smu"
#             ["jet_jetId","muJet_idx"],"Jet ID (e)",4,0,4,ESEL,ECUT,dataset="sele"

#             ["jet_jetId","muJet_idx"],"Jet ID, nGenJet = 0 (mu)",4,0,4,MSEL+["LHE_Njets"],MCUT+[[0,0]]
#             ["jet_jetId","muJet_idx"],"Jet ID, nGenJet = 0 (e)",4,0,4,ESEL+["LHE_Njets"],ECUT+[[0,0]]
#
#             ["jet_nMuons","muJet_idx"],"# muons in jet (mu)",4,0,4,MSEL,MCUT,dataset="smu"
#             ["jet_nMuons","muJet_idx"],"# muons in jet (e)",4,0,4,ESEL,ECUT,dataset="sele"
            '''
args=[applyCuts(line.strip()) for line in arguments.split("\n") if not line.strip()=="" and not line.strip().startswith("#")]

if len(args)<2:
    # Interactive
    for line in args:
        exec("Stacker.plotStack("+line.strip()+")")
else:
    # Jobs
    os.system("mkdir -p stackerLogs")
    for i, line in enumerate(args):
        tempPy = open("tempPy.py","w")
        tempPy.write("import Stacker\n")
        pythonLine = "Stacker.plotStack("+line.strip()+")"
        tempPy.write(pythonLine)
        tempPy.close()
        os.system("nohup python -u tempPy.py &> stackerLogs/"+str(int(i+start_idx))+".log &")
        print "Submitted %d jobs: "%(i+start_idx) + line.strip()
        time.sleep(2)
