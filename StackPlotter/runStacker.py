import os, time, sys, Stacker
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV]",15,0,25,dataset="smu")
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV] (1 mu), HT > 100",15,0,25,selections=["is_M","HT"],cuts=[[1,1],[100,1e4]],dataset="smu")
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV] (1 e), HT > 100",15,0,25,selections=["is_E","HT"],cuts=[[1,1],[100,1e4]],dataset="sele")
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 25<p^{jet}_{T}<35 + 1 mu",15,0,25,selections=[["jet_Pt","muJet_idx"],"is_M"],cuts=[[25,35],[1,1]])
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 25<p^{jet}_{T}<35 + 1 e",15,0,25,selections=[["jet_Pt","muJet_idx"],"is_E"],cuts=[[25,35],[1,1]])
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 35<p^{jet}_{T}<50",15,0,25,selections=[["jet_Pt","muJet_idx"]],cuts=[[35,50]])
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 50<p^{jet}_{T}<70",15,0,25,selections=[["jet_Pt","muJet_idx"]],cuts=[[50,70]])
# plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV], 70<p^{jet}_{T}<200",15,0,25,selections=[["jet_Pt","muJet_idx"]],cuts=[[70,200]])

DYPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190708_2017_DY/"
TTPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190708_2017_TT/"
WcPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190805_2017_Wc/"

if len(sys.argv) > 1:
    start_idx = 1 + float(sys.argv[1])
else:
    start_idx = 1

def applyCuts(ln,reg=""):
    ln = ln.replace('ZMASSCUT','[85,95,\"invert\"]')
    ln = ln.replace('CVXBINNING','varBin1=[0.,0.2,0.4,0.6,0.8,1.],varBin2=[0.,0.2,0.4,0.6,0.8,1.]')
    # ln = ln.replace('CVXBINNING','varBin1=[0.,0.2,0.35,0.5,0.7,1.],varBin2=[0.,0.2,0.35,0.5,0.7,1.]')


    ln = ln.replace('TTWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",filePre="TTDi",drawDataMCRatioLine=True,rootPath="'+TTPath+'"')
    ln = ln.replace('TTSEMIWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="Events",filePre="TTSemi",drawDataMCRatioLine=True,rootPath="'+WcPath+'"')
    ln = ln.replace('WCWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="OS-SS Events",filePre="Wc",drawDataMCRatioLine=True,rootPath="'+WcPath+'"')
    ln = ln.replace('DYWEIGHTNOPU','MCWeightName="eventWeight/PUWeight",DataWeightName="eventWeight",yTitle="Events",filePre="DYNoPU",drawDataMCRatioLine=True,rootPath="'+DYPath+'"')
    ln = ln.replace('DYWEIGHT','MCWeightName="eventWeight",DataWeightName="eventWeight",yTitle="Events",filePre="DY",drawDataMCRatioLine=True,rootPath="'+DYPath+'"')
    
    ln = ln.replace('LEPWEIGHT','MCWeightName="eventWeightUnsigned",DataWeightName="eventWeightUnsigned",yTitle="Events",filePre="Lep",drawDataMCRatioLine=True,rootPath="'+WcPath+'"')

#    ln = ln.replace('CVXBINNING','varBin1=[0,0.2,0.35,0.5,0.7,1.],varBin2=[0,0.4,0.525,0.65,0.8,1.]')
    # ln = ln.replace('CVXBINNING','makeCustomH=True')

    ln = ln.replace('ESEL','selections=["is_E","signWeight","jetMuPt_by_jetPt",QCDSELE,"jet_nJet","diLepVeto"]')    # ,["jet_CvsB","muJet_idx"]
    ln = ln.replace('ECUT','cuts=[[1,1],[-1,1],[0,0.6],QCDCUTE,[0,4],[0,0]]')
    ln = ln.replace('MSEL','selections=["is_M","signWeight","jetMuPt_by_jetPt",QCDSELM,"jet_nJet","diLepVeto","Z_Mass_best","Z_Mass_min",["jet_muplusneEmEF","muJet_idx"],"jetMu_iso"]')   #"Z_Mass","Z_Mass","Z_Mass_max","Z_Mass_min"
    ln = ln.replace('MCUT','cuts=[[1,1],[-1,1],[0,0.4],QCDCUTM,[0,4],[0,0],[80,100,\"invert\"],[0,12,\"invert\"],[0,0.7],[0,0.5,"invert"]]')           #[85,95,\"invert\"],[80,1e5,"invert"],[0,12,"invert"]                  #,[-1,0.5],[1,1e4]]
    
    # Prompt Lepton CR    
    ln = ln.replace('LEPSEL','selections=["is_M","signWeight","Z_Mass","jetMuPt_by_jetPt",QCDSELM,"jet_nJet","diLepVeto"]')
    ln = ln.replace('LEPCUT','cuts=[[1,1],[1,1],[85,95],[0,1.5],QCDCUTM,[0,4],[0,0]]')
    
    # ttbar CR
    #Dileptonic
    ln = ln.replace('TTSELME','selections=["is_ME"]')
    ln = ln.replace('TTCUTME','cuts=[[1,1]]')
    ln = ln.replace('TTSELMM','selections=["is_MM","Z_Mass","Z_Mass","met_Pt"]')
    ln = ln.replace('TTCUTMM','cuts=[[1,1],[75,105,"reverse"],[0,12,\"invert\"],[40,1e4]]')
    ln = ln.replace('TTSELEE','selections=["is_EE","Z_Mass","Z_Mass","met_Pt"]')
    ln = ln.replace('TTCUTEE','cuts=[[1,1],[75,105,"reverse"],[0,12,\"invert\"],[40,1e4]]')

    #Semileptonic
    ln = ln.replace('TTSELE','selections=["is_E","signWeight","jetMuPt_by_jetPt",QCDSELE,"jet_nJet","diLepVeto","jetMu_Pt"]')    #
    ln = ln.replace('TTCUTE','cuts=[[1,1],[-1,1],[0,0.6],QCDCUTE,[5,100],[0,0],[5,25]]')
    ln = ln.replace('TTSELM','selections=["is_M","Z_Mass","Z_Mass","signWeight","jetMuPt_by_jetPt",QCDSELM,"jet_nJet","diLepVeto","jetMu_Pt"]')
    ln = ln.replace('TTCUTM','cuts=[[1,1],[85,95,\"invert\"],[0,12,\"invert\"],[-1,1],[0,0.4],QCDCUTM,[5,100],[0,0],[5,25]]')                             #,[-1,0.5],[1,1e4]]

    #DY
    ln = ln.replace('DYSELM','selections=["is_M",["M_Pt",0],"Z_Pt"]')
    ln = ln.replace('DYCUTM','cuts=[[1,1],[0,20,"invert"],[0,15,"invert"]]')
    ln = ln.replace('DYSELE','selections=["is_E",["E_Pt",0],"Z_Pt"]')
    ln = ln.replace('DYCUTE','cuts=[[1,1],[0,27,"invert"],[0,15,"invert"]]')

    # ln = ln.replace(',QCDSELM','')
    # ln = ln.replace(',QCDCUTM','')
    # ln = ln.replace(',QCDSELE','')
    # ln = ln.replace(',QCDCUTE','')

    ln = ln.replace('QCDSELM','["M_RelIso",0],"hardMu_Jet_PtRatio",["M_dz",0],["M_dxy",0],["M_sip3d",0]')
    ln = ln.replace('QCDCUTM','[0,0.05],[0,0.75,"reverse"],[-0.01,0.01],[-0.002,0.002],[0,2]')
    ln = ln.replace('QCDSELE','["E_RelIso",0],"hardE_Jet_PtRatio",["E_dz",0],["E_dxy",0],["E_sip3d",0]')
    ln = ln.replace('QCDCUTE','[0,0.05],[0,0.75,"reverse"],[-0.02,0.02],[-0.01,0.01],[0,2.5]')

    if not reg=="": ln = ln.replace('REG',reg)
    return ln

arguments = '''
    # Wc selection
           #"jetMu_Pt",r"p^{soft mu}_{T} [GeV] (#mu)",25,0,25,MSEL,MCUT,dataset="smu",WCWEIGHT
#           "jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (e)",25,0,25,ESEL,ECUT,dataset="sele",WCWEIGHT
#             ["jet_Eta","muJet_idx"],r"eta_{jet} (#mu)",20,-2.8,2.8,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
#             ["jet_Eta","muJet_idx"],r"#eta_{jet} (e)",20,-2.8,2.8,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT
#             ["jet_Phi","muJet_idx"],r"phi_{jet} (#mu)",20,-3.2,3.2,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
#             ["jet_Phi","muJet_idx"],r"#phi_{jet} (e)",20,-3.2,3.2,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT

             #["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu)",25,0,100,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT
#              ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e)",25,0,100,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT
             #["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu)",30,-0.2,1,MSEL,MCUT,dataset="smu",makeROOT=True,binWtTxt=False,WCWEIGHT
#             ["jet_CvsL","muJet_idx"],r"Jet CvsL (e)",30,-0.2,1,ESEL,ECUT,dataset="sele",makeROOT=True,binWtTxt=False,WCWEIGHT
             #["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu)",30,-0.2,1,MSEL,MCUT,dataset="smu",makeROOT=True,binWtTxt=False,WCWEIGHT
#             ["jet_CvsB","muJet_idx"],r"Jet CvsB (e)",30,-0.2,1,ESEL,ECUT,dataset="sele",makeROOT=True,binWtTxt=False,WCWEIGHT
             
           #"Z_Mass",r"M_{#mu#mu} [GeV] (#mu)",40,0,120,MSEL,MCUT,dataset="smu",WCWEIGHT
           #"Z_Pt",r"p_{T}^{#mu#mu} [GeV] (#mu)",50,0,100,MSEL,MCUT,dataset="smu",WCWEIGHT
           #"Z_Pt_best",r"best p_{T}^{#mu#mu} [GeV] (#mu)",50,0,100,MSEL,MCUT,dataset="smu",WCWEIGHT
           #"Z_Mass_best",r"best M_{#mu#mu} [GeV] (#mu)",40,0,120,MSEL,MCUT,dataset="smu",WCWEIGHT,nminus1=True
           #"Z_Mass_min",r"min M_{#mu#mu} [GeV] (#mu)",40,0,120,MSEL,MCUT,dataset="smu",WCWEIGHT,nminus1=True
           #["jet_neEmEF","muJet_idx"],"Jet neutral EM EF",25,0,1,MSEL,MCUT,dataset="smu",WCWEIGHT
           #["jet_muplusneEmEF","muJet_idx"],"Jet Muon + neutral EM EF",25,0,1,MSEL,MCUT,dataset="smu",WCWEIGHT,nminus1=True
           #["jet_puId","muJet_idx"],"Jet PU ID",8,0,8,MSEL,MCUT,dataset="smu",WCWEIGHT
           #"diLepVeto",r"Dilepton veto (#mu)",2,0,2,MSEL,MCUT,dataset="smu",WCWEIGHT,nminus1=True
           #"jetMu_iso",r"Soft Muon rel. isolation (R = 0.4) (mu)",20,0,4,MSEL,MCUT,dataset="smu",WCWEIGHT,nminus1=True
           #"jetMuPt_by_jetPt",r"p^{soft #mu}_{T}/p^{jet}_{T} (#mu)",25,0,1,MSEL,MCUT,dataset="smu",WCWEIGHT,nminus1=True
           
           #"LHE_Vpt","LHE p_T^V",40,0,200,MSEL,MCUT,WCWEIGHT
           #"LHE_Vpt","LHE p_T^V",40,0,200,ESEL,ECUT,WCWEIGHT
           

           #  ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,MSEL,MCUT,dataset="smu",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,WCWEIGHT
           #  ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,ESEL,ECUT,dataset="sele",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,WCWEIGHT
           
          "jet_nJet","# jets [GeV] (mu)",10,0,10,MSEL,MCUT,dataset="smu",makeROOT=True,WCWEIGHT,nminus1=True
          "jet_nJet","# jets [GeV] (e)",10,0,10,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT,nminus1=True

            # ["E_Pt",0],r"p^{hard e}_{T} [GeV] (e)",30,0,150,ESEL,ECUT,dataset="sele",makeROOT=True,WCWEIGHT
            # "met_Pt",r"E^{miss}_{T} (mu)",30,0,150,MSEL,MCUT,dataset="smu",WCWEIGHT
            # "met_Pt",r"E^{miss}_{T} (e)",30,0,150,ESEL,ECUT,dataset="sele",WCWEIGHT



    # Lepton selection
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu)",25,0,100,LEPSEL,LEPCUT,dataset="smu",makeROOT=True,LEPWEIGHT
#             ["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu)",30,-0.2,1,LEPSEL,LEPCUT,dataset="smu",makeROOT=True,LEPWEIGHT
#             ["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu)",30,-0.2,1,LEPSEL,LEPCUT,dataset="smu",makeROOT=True,LEPWEIGHT




    # Semileptonic TT
            #"jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (mu)",25,0,25,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTSEMIWEIGHT
            #"jetMu_Pt",r"p^{soft #mu}_{T} [GeV] (e)",25,0,25,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTSEMIWEIGHT

#             ["jet_Eta","muJet_idx"],r"#eta_{jet} (mu)",20,-2.8,2.8,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTSEMIWEIGHT
#             ["jet_Eta","muJet_idx"],r"#eta_{jet} (e)",20,-2.8,2.8,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTSEMIWEIGHT
#             ["jet_Phi","muJet_idx"],r"#phi_{jet} (mu)",20,-3.2,3.2,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTSEMIWEIGHT
#             ["jet_Phi","muJet_idx"],r"#phi_{jet} (e)",20,-3.2,3.2,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTSEMIWEIGHT

                #["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (mu)",25,20,120,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTSEMIWEIGHT
                #["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e)",25,20,120,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTSEMIWEIGHT
                #["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu)",30,-0.2,1,TTSELM,TTCUTM,dataset="smu",makeROOT=True,binWtTxt=False,TTSEMIWEIGHT
                #["jet_CvsL","muJet_idx"],r"Jet CvsL (e)",30,-0.2,1,TTSELE,TTCUTE,dataset="sele",makeROOT=True,binWtTxt=False,TTSEMIWEIGHT
                #["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu)",30,-0.2,1,TTSELM,TTCUTM,dataset="smu",makeROOT=True,binWtTxt=False,TTSEMIWEIGHT
                #["jet_CvsB","muJet_idx"],r"Jet CvsB (e)",30,-0.2,1,TTSELE,TTCUTE,dataset="sele",makeROOT=True,binWtTxt=False,TTSEMIWEIGHT

#            ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSELM,TTCUTM,dataset="smu",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTSEMIWEIGHT
#            ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSELE,TTCUTE,dataset="sele",brName2D=["jet_CvsB","muJet_idx"],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTSEMIWEIGHT
#             "jet_nJet","# jets [GeV] (mu)",10,0,10,TTSELM,TTCUTM,dataset="smu",makeROOT=True,TTSEMIWEIGHT
#             "jet_nJet","# jets [GeV] (mu)",10,0,10,TTSELE,TTCUTE,dataset="sele",makeROOT=True,TTSEMIWEIGHT
            # ["E_Pt",0],r"p^{hard e}_{T} [GeV] (e)",30,0,150,dataset="sele",makeROOT=True,TTSEMIWEIGHT
            
            "jet_nJet","# jets [GeV] (mu)",10,0,10,TTSELM,TTCUTM,dataset="smu",TTSEMIWEIGHT,makeROOT=True,nminus1=True
            "jet_nJet","# jets [GeV] (e)",10,0,10,TTSELE,TTCUTE,dataset="sele",TTSEMIWEIGHT,makeROOT=True,nminus1=True

             # "met_Pt",r"E^{miss}_{T} (e)",30,0,150,TTSELE,TTCUTE,dataset="sele",TTSEMIWEIGHT
            # "met_Pt",r"E^{miss}_{T} (mu)",30,0,150,TTSELM,TTCUTM,dataset="smu",TTSEMIWEIGHT
            
            #"jetMuPt_by_jetPt",r"p^{soft #mu}_{T}/p^{jet}_{T} (mu)",25,0,1,TTSELM,TTCUTM,dataset="smu",TTSEMIWEIGHT
            #"jetMuPt_by_jetPt",r"p^{soft #mu}_{T}/p^{jet}_{T} (e)",25,0,1,TTSELE,TTCUTE,dataset="sele",TTSEMIWEIGHT

#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (#mu e)",20,-3.2,3.2,TTSELME,TTCUTME,dataset="smu",TTSEMIWEIGHT
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (#mu e)",20,-2.8,2.8,TTSELME,TTCUTME,dataset="smu",TTSEMIWEIGHT
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu e)",28,20,300,TTSELME,TTCUTME,dataset="smu",TTSEMIWEIGHT

#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (e e)",20,-3.2,3.2,TTSELEE,TTCUTEE,dataset="deg",TTSEMIWEIGHT
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (e e)",20,-2.8,2.8,TTSELEE,TTCUTEE,dataset="deg",TTSEMIWEIGHT
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e e)",28,20,300,TTSELEE,TTCUTEE,dataset="deg",TTSEMIWEIGHT

#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (#mu #mu)",20,-3.2,3.2,TTSELMM,TTCUTMM,dataset="dmu",TTSEMIWEIGHT
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (#mu #mu)",20,-2.8,2.8,TTSELMM,TTCUTMM,dataset="dmu",TTSEMIWEIGHT
#            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu #mu)",28,20,300,TTSELMM,TTCUTMM,dataset="dmu",TTSEMIWEIGHT

#              ["jet_CvsL","muJet_idx"],"Jet CvsL",30,-0.2,1,TTSEL,TTCUT,dataset="",makeROOT=True,TTSEMIWEIGHT
#              ["jet_CvsB","muJet_idx"],"Jet CvsB",30,-0.2,1,TTSEL,TTCUT,dataset="",makeROOT=True,TTSEMIWEIGHT
#            ["jet_CvsL","muJet_idx"],"CvsL",5,0,1,TTSEL,TTCUT,dataset="",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTSEMIWEIGHT



    # Dileptonic TT
            #["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu e)",36,20,200,TTSELME,TTCUTME,dataset="mue",TTWEIGHT
            #["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu e)",30,-0.2,1,TTSELME,TTCUTME,dataset="mue",makeROOT=True,binWtTxt=False,TTWEIGHT
            #["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu e)",30,-0.2,1,TTSELME,TTCUTME,dataset="mue",makeROOT=True,binWtTxt=False,TTWEIGHT
           # ["jet_CvsL",0],"CvsL",5,0,1,TTSELME,TTCUTME,dataset="smu",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTWEIGHT

          #["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (#mu #mu)",25,20,120,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
            #["jet_CvsL","muJet_idx"],r"Jet CvsL (#mu #mu)",30,-0.2,1,TTSELMM,TTCUTMM,dataset="dmu",makeROOT=True,binWtTxt=False,TTWEIGHT
            #["jet_CvsB","muJet_idx"],r"Jet CvsB (#mu #mu)",30,-0.2,1,TTSELMM,TTCUTMM,dataset="dmu",makeROOT=True,binWtTxt=False,TTWEIGHT
           # ["jet_CvsL",0],"CvsL",5,0,1,TTSELMM,TTCUTMM,dataset="dmu",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTWEIGHT

          #["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (e e)",25,20,120,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
            #["jet_CvsL","muJet_idx"],r"Jet CvsL (e e)",30,-0.2,1,TTSELEE,TTCUTEE,dataset="deg",makeROOT=True,binWtTxt=False,TTWEIGHT
            #["jet_CvsB","muJet_idx"],r"Jet CvsB (e e)",30,-0.2,1,TTSELEE,TTCUTEE,dataset="deg",makeROOT=True,binWtTxt=False,TTWEIGHT
           # ["jet_CvsL",0],"CvsL",5,0,1,TTSELEE,TTCUTEE,dataset="deg",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,TTWEIGHT

           #"Z_Mass",r"M_{#mu#mu} [GeV] (#mu #mu)",30,0,180,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
           #"Z_Pt",r"p_{T}^{#mu#mu} [GeV] (#mu #mu)",30,0,180,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
           #"Z_Mass",r"M_{ee} [GeV] (e e)",30,0,180,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
           #"Z_Pt",r"p_{T}^{ee} [GeV] (e e)",30,0,180,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT
           
           #"jetMuPt_by_jetPt",r"p^{soft #mu}_{T}/p^{jet}_{T} (#mu #mu)",25,0,1,TTSELMM,TTCUTMM,dataset="dmu",TTWEIGHT
           #"jetMuPt_by_jetPt",r"p^{soft #mu}_{T}/p^{jet}_{T} (#mu e)",25,0,1,TTSELME,TTCUTME,dataset="mue",TTWEIGHT
           #"jetMuPt_by_jetPt",r"p^{soft #mu}_{T}/p^{jet}_{T} (e e)",25,0,1,TTSELEE,TTCUTEE,dataset="deg",TTWEIGHT


        # DY

             #["jet_Pt",0],r"p^{jet}_{T} [GeV] (#mu#mu)",50,20,120,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
              #["jet_CvsL",0],"Jet CvsL (#mu#mu)",30,-0.2,1,DYSELM,DYCUTM,dataset="dmu",makeROOT=True,binWtTxt=False,DYWEIGHT
              #["jet_CvsB",0],"Jet CvsB (#mu#mu)",30,-0.2,1,DYSELM,DYCUTM,dataset="dmu",makeROOT=True,binWtTxt=False,DYWEIGHT
              
              #"jet_nJet","# jets (#mu#mu)",10,0,10,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
             #"Z_Mass",r"M_{#mu#mu} [GeV] (#mu#mu)",60,75,105,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
             #"Z_Pt",r"p_{T}^{#mu#mu} [GeV] (#mu#mu)",50,0,50,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
             #"Z_Pt",r"p_{T}^{#mu#mu} [GeV] (#mu#mu)",50,0,150,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT,filePre2="Extend"
             
             #["M_Pt",0],r"p^{#mu1}_{T} [GeV] (#mu#mu)",50,0,100,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
            #["M_Pt",1],r"p^{#mu2}_{T} [GeV] (#mu#mu)",50,0,100,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT

#            ["jet_CvsL",0],"CvsL",5,0,1,DYSELM,DYCUTM,dataset="dmu",brName2D=["jet_CvsB",0],brLabel2="CvsB",nbins2=5,CVXBINNING,drawStyle="",makeROOT=True,DYWEIGHT

            # "met_Pt",r"E^{miss}_{T} (#mu#mu)",25,0,100,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
            #  ["jet_Phi",0],r"#phi_{jet} (#mu#mu)",20,-3.2,3.2,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
            #  ["jet_Eta",0],r"#eta_{jet} (#mu#mu)",20,-2.8,2.8,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
            # 
            #  "nPVGood","Number of good reconstructed PVs (#mu#mu)",70,0,70,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
            #  "nPVGood","Number of good reconstructed PVs (no PU rw) (#mu#mu)",70,0,70,DYSELM,DYCUTM,dataset="dmu",DYWEIGHTNOPU
            #  ["jet_muPtRatio",0],r"p_{T}^{#mu}/p_{T}^{jet} (#mu#mu)",40,-1,1,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
            # 
            # "dR_Z_jet",r"#deltaR_{Z,jet} (#mu#mu)",30,0,5,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
            # "dR_mu_jet_min",r"min. #deltaR_{#mu,jet} (#mu#mu)",30,0,5,DYSELM,DYCUTM,dataset="dmu",DYWEIGHT
            
            #["jet_Pt",0],r"p^{jet}_{T} [GeV] (ee)",50,20,120,DYSELE,DYCUTE,dataset="deg",DYWEIGHT
              #["jet_CvsL",0],"Jet CvsL (ee)",30,-0.2,1,DYSELE,DYCUTE,dataset="deg",makeROOT=True,binWtTxt=False,DYWEIGHT
              #["jet_CvsB",0],"Jet CvsB (ee)",30,-0.2,1,DYSELE,DYCUTE,dataset="deg",makeROOT=True,binWtTxt=False,DYWEIGHT
              
              #"jet_nJet","# jets (ee)",10,0,10,DYSELE,DYCUTE,dataset="deg",DYWEIGHT
             #"Z_Mass",r"M_{ee} [GeV] (ee)",60,75,105,DYSELE,DYCUTE,dataset="deg",DYWEIGHT
             #"Z_Pt",r"p_{T}^{ee} [GeV] (ee)",50,0,50,DYSELE,DYCUTE,dataset="deg",DYWEIGHT
             #"Z_Pt",r"p_{T}^{ee} [GeV] (ee)",50,0,150,DYSELE,DYCUTE,dataset="deg",DYWEIGHT,filePre2="Extend"
             
              #["E_Pt",0],r"p^{#mu1}_{T} [GeV] (ee)",50,0,100,DYSELE,DYCUTE,dataset="deg",DYWEIGHT
              #["E_Pt",1],r"p^{#mu2}_{T} [GeV] (ee)",50,0,100,DYSELE,DYCUTE,dataset="deg",DYWEIGHT
            
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



            ["jet_Pt","muJet_idx"],r"p^{jet}_{T} [GeV] (mu)",25,0,100,DYSELM,DYCUTM,dataset="smu"
#            ["jet_Eta","muJet_idx"],r"#eta_{jet} (mu)",20,-2.8,2.8,DYSELM,DYCUTM,dataset="smu"
#            ["jet_Phi","muJet_idx"],r"#phi_{jet} (mu)",20,-3.2,3.2,DYSELM,DYCUTM,dataset="smu"
#            ["jet_Mass","muJet_idx"],r"m_{jet} [GeV] (mu)",20,0,40,DYSELM,DYCUTM,dataset="smu"




#           "jet_nJet","# jets [GeV] (mu)",10,0,10,MSEL,MCUT,dataset="smu"
#             "jet_nJet","# jets [GeV] (e)",10,0,10,ESEL,ECUT,dataset="sele"

#            ["jet_btagCMVA","muJet_idx"],r"Jet cMVAv2 (mu)",25,-1,1,MSEL,MCUT,dataset="smu"
#            ["jet_btagCMVA","muJet_idx"],r"Jet cMVAv2 (e)",25,-1,1,ESEL,ECUT,dataset="sele"

#            ["jet_btagCSVV2","muJet_idx"],r"Jet CSVv2 (mu)",30,-0.2,1,MSEL,MCUT,dataset="smu"
#            ["jet_btagCSVV2","muJet_idx"],r"Jet CSVv2 (e)",30,-0.2,1,ESEL,ECUT,dataset="sele"

#            ["jet_btagDeepB","muJet_idx"],r"Jet DeepCSV b+bb (mu)",30,-0.2,1,MSEL,MCUT,dataset="smu"
#            ["jet_btagDeepB","muJet_idx"],r"Jet DeepCSV b+bb (e)",30,-0.2,1,ESEL,ECUT,dataset="sele"

#            ["jet_btagDeepC","muJet_idx"],r"Jet DeepCSV c (mu)",30,-0.2,1,MSEL,MCUT,dataset="smu"
#            ["jet_btagDeepC","muJet_idx"],r"Jet DeepCSV c (e)",30,-0.2,1,ESEL,ECUT,dataset="sele"

#            ["jet_CvsL","muJet_idx"],r"Jet CvsL (mu)",30,-0.2,1,MSEL,MCUT,dataset="smu",makeROOT=True
#           ["jet_CvsL","muJet_idx"],r"Jet CvsL (e)",30,-0.2,1,ESEL,ECUT,dataset="sele",makeROOT=True

#           ["jet_CvsB","muJet_idx"],r"Jet CvsB (mu)",30,-0.2,1,MSEL,MCUT,dataset="smu",makeROOT=True
#           ["jet_CvsB","muJet_idx"],r"Jet CvsB (e)",30,-0.2,1,ESEL,ECUT,dataset="sele",makeROOT=True

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

if len(args)<1:
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
        time.sleep(0.5)
