####################################################
#   Stack Plotting Tool for c-tagging SF Measurement
#   By Spandan Mondal
#   RWTH Aachen University, Germany
#   CMS Experiment, CERN
#   https://cern.ch/spmondal
####################################################

from ROOT import *
import os, sys
#from VHcc_Weights import eff_xsec
from array import array
gROOT.SetBatch(True)
gStyle.SetOptStat(0)
gStyle.SetLegendBorderSize(0)

lumi = 35900
# outDir="Plots_190116_3mva80rewt_OS-SS_MuPtJetPtRatioCut_noQCD_RelIso_hardLepJetPtRatio_dxyz_sip3d_nJet/"
outDir="Plots_190220_ReWeighted_2"
# outDir="Plots_190124_Test"
yTitle="Events"
MCWeightName="eventWeight"          #"genWeight"      #
DataWeightName="eventWeight"        #   "eventWeight"
rootPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190228_pt20/"
useQCD = False
moreQCD = False
testMode = False

def getbrText(brName):
    if type(brName) is str:
        return brName
    else:
        return brName[0] + "_" + str(brName[1])

def makeHisto(dir,treeName,brName,brLabel,nbins,start,end,weightName="",selections="",cuts=[], divideByFlav=False, brName2D="",nbins2=5,start2=0,end2=1,varBin1=[],varBin2=[],makeCustomH=False):
    if "|" in dir:                      # dir can be one directory string, or dir = "dir1|dir2|dir3|..."
        dirList = dir.split("|")
    else:
        dirList = [dir]
    rootFiles=[]
    for iDir in dirList:
        rootFiles += [os.path.join(iDir,i) for i in os.listdir(iDir) if i.endswith(".root")]

    myChain = TChain(treeName)
    nTotalEvents = 0
    for fl in rootFiles:
        iF = TFile.Open(fl)
        if bool(iF) == False or iF.IsZombie():
            print "Error in file %s, skipping."%fl
            continue
        myChain.Add(fl)
        hTotal = iF.Get("h_total")
        nTotalEvents += hTotal.Integral()
        iF.Close()
        if testMode: break

    nEntries = myChain.GetEntries()

    brText = getbrText(brName)
    if brLabel == "": brLabel = brText

    # if makeCustomH:
    #     customHisto = TH2Poly()
    #     customHisto.AddBin(0.,0.,.2,.2)
    #     customHisto.AddBin(0.2,0.,.4,.2)
    #     customHisto.AddBin(0.4,0.,.6,.2)
    #     customHisto.AddBin(0.6,0.,1.,.2)
    #
    #     customHisto.AddBin(0.,0.2,.2,.4)
    #     customHisto.AddBin(0.2,0.2,.4,.4)
    #     customHisto.AddBin(0.4,0.2,.6,.4)
    #
    #     customHisto.AddBin(0.,0.4,.2,.6)
    #     customHisto.AddBin(0.2,0.4,.4,.6)
    #     customHisto.AddBin(0.4,0.4,.6,.6)
    #
    #     customHisto.AddBin(0.6,0.2,1.,.6)
    #
    #     customHisto.AddBin(0.,0.6,.2,.8)
    #     customHisto.AddBin(0.,0.8,.2,1.)
    #
    #     customHisto.AddBin(0.2,0.6,.6,1.)
    #     customHisto.AddBin(0.6,0.6,1.,1.)

    blankArray=array('d',[])
    if not divideByFlav:
        if brName2D == "" and not makeCustomH:
            myHisto = TH1F(brText+dir,brLabel,nbins,start,end)
        # elif makeCustomH:
        #     myHisto = customHisto.Clone()
        #     myHisto.SetNameTitle(brText+dir,brLabel)
        else:
            if varBin1==blankArray and varBin2==blankArray:
                myHisto = TH2F(brText+dir,brLabel,nbins,start,end,nbins2,start2,end2)
            elif varBin1!=blankArray and varBin2==blankArray:
                myHisto = TH2F(brText+dir,brLabel,nbins,varBin1,nbins2,start2,end2)
            elif varBin1==blankArray and varBin2!=blankArray:
                myHisto = TH2F(brText+dir,brLabel,nbins,start,end,nbins2,varBin2)
            else:
                myHisto = TH2F(brText+dir,brLabel,nbins,varBin1,nbins2,varBin2)
        myHisto.Sumw2()
    else:
        myHisto=[]
        for idx in range(4):
            if brName2D == "" and not makeCustomH:
                myHisto.append(TH1F(brText+dir+str(idx),brLabel,nbins,start,end))
            # elif makeCustomH:
            #     myHisto.append(customHisto.Clone())
            #     myHisto[idx].SetNameTitle(brText+dir+str(idx),brLabel)
            else:
                if varBin1==blankArray and varBin2==blankArray:
                    myHisto.append(TH2F(brText+dir+str(idx),brLabel,nbins,start,end,nbins2,start2,end2))
                elif varBin1!=blankArray and varBin2==blankArray:
                    myHisto.append(TH2F(brText+dir+str(idx),brLabel,nbins,varBin1,nbins2,start2,end2))
                elif varBin1==blankArray and varBin2!=blankArray:
                    myHisto.append(TH2F(brText+dir+str(idx),brLabel,nbins,start,end,nbins2,varBin2))
                else:
                    myHisto.append(TH2F(brText+dir+str(idx),brLabel,nbins,varBin1,nbins2,varBin2))
            myHisto[idx].Sumw2()

    for iEvent in range(nEntries):
        if iEvent > 0 and iEvent%1000000 == 0: print "Processed %d of %d events in %s."%(iEvent,nEntries,dir)
        myChain.GetEntry(iEvent)

        # =========== Function to read specified leaf ===========
        def parseBrStr(input):
            '''
                input == string             : load tree->string
                input == [string,int]       : load tree->string[int]
                input == [string1,string2]  : load tree->string1[tree->string2]
            '''
            if type(input) is str:
                if input == "M_ip3derror":          # Add customized calculations on variables here
                    return parseBrStr(["M_ip3d",0])/parseBrStr(["M_sip3d",0])
                elif input == "E_ip3derror":
                    return parseBrStr(["E_ip3d",0])/parseBrStr(["E_sip3d",0])
                return myChain.__getattr__(input)
            elif type(input) is list:
                vectorBr = list(myChain.__getattr__(input[0]))
                vecIdx = input[1]
                if type(vecIdx) is int:
                    if "Cvs" in input[0] and vectorBr[vecIdx] < 0.: return -0.1
                    return vectorBr[vecIdx]
                elif type(vecIdx) is str:
                    if "Cvs" in input[0] and vectorBr[ int(myChain.__getattr__(vecIdx)) ] < 0.: return -0.1
                    return vectorBr[ int(myChain.__getattr__(vecIdx)) ]
                else:
                    raise ValueError
            else:
                raise ValueError
        # ------------------------------------------------------------

        if weightName == "":
            eventWeight = 1.
        elif "/" in weightName:
            eventWeight = myChain.__getattr__(weightName.split('/')[0])/myChain.__getattr__(weightName.split('/')[1])
        elif "*" in weightName:
            eventWeight = 1.
            for wt in weightName.split('*'):
                eventWeight *= myChain.__getattr__(wt)
        else:
            eventWeight = myChain.__getattr__(weightName)


        if not selections == "":
            keepEvent = True
            for iSel, selection in enumerate(selections):
                sel  = parseBrStr(selection)
                if len(cuts[iSel]) == 2:
                    discardBool = sel < cuts[iSel][0] or sel > cuts[iSel][1]
                elif len(cuts[iSel]) > 2:
                    discardBool = sel > cuts[iSel][0] and sel < cuts[iSel][1]
                else:
                    raise ValueError
                if discardBool:
                    keepEvent = False
                    break
            if not keepEvent: continue

        # =========== Divide WJets according to jet flavour =======
        '''
            myHisto[0]: c jets
            myHisto[1]: c jet + c jet
            myHisto[2]: uds jets
            myHisto[3]: b jets
        '''
        if divideByFlav:
            hFlv = list(myChain.__getattr__("jet_hadronFlv"))
            iJet = int(myChain.__getattr__("muJet_idx"))
            if iJet < 0: iJet = 0
            numOf_cJet = int(myChain.__getattr__("numOf_cJet"))
            flv = hFlv[iJet]
            if flv==5:
                histoIdx = 3
            elif flv==4:
                if numOf_cJet%2 == 0:
                    histoIdx = 1
                else:
                    histoIdx = 0
            else:
                histoIdx = 2
        # ---------------------------------------------------------

        # # ====== Extract HT bins from inclusive samples =======
        # if "JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" in dir:      # or "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-" in dir:
        #     LHE_HT = float(myChain.__getattr__("LHE_HT"))
        #     if LHE_HT > 100: continue
        # # -----------------------------------------------------

#       ====== Extract nGenJets from inclusive sample =======
        if "WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" in dir:
            LHE_Njets = float(myChain.__getattr__("LHE_Njets"))
            if LHE_Njets > 0 and LHE_Njets < 5: continue
       # -----------------------------------------------------

        brVal = parseBrStr(brName)
        # print brVal, dir

        if reWeight and divideByFlav:
            ctagWt = 1.
            for iJ in range(int(parseBrStr("jet_nJet"))):
                CvsLval = parseBrStr(["jet_CvsL",iJ])
                CvsBval = parseBrStr(["jet_CvsB",iJ])
                if False: #CvsLval < 0. or CvsBval < 0:
                    ctagWt *= 1.
                else:
#                    ctagWtOld = ctagWt
                    flav = int(parseBrStr(["jet_hadronFlv",iJ]))
                    xbin = cWtHist.GetXaxis().FindBin(CvsLval)
                    ybin = cWtHist.GetYaxis().FindBin(CvsBval)
                    if flav == 4:
                        ctagWt *= cWtHist.GetBinContent(xbin,ybin)
                    elif flav == 5:
                        ctagWt *= bWtHist.GetBinContent(xbin,ybin)
                    else:
                        ctagWt *= lWtHist.GetBinContent(xbin,ybin)
#                    if CvsLval < 0.: print CvsLval, CvsBval, ctagWt/ctagWtOld 
            eventWeight *= ctagWt
        
        
        if brName2D == "":
            if not divideByFlav:
                myHisto.Fill(brVal,eventWeight)
            else:
                myHisto[histoIdx].Fill(brVal,eventWeight)
        else:
            brVal2 = parseBrStr(brName2D)
            # =============== Treating ==1 bins ==================
            if brName[0] == "jet_CvsL" and brName2D[0] == "jet_CvsB":
                if brVal >= 1.:
                    brVal = 0.99999
                if brVal2 >= 1.:
                    brVal2 = 0.99999
#                if brVal < 0:
#                    brVal = 0.001
#                if brVal2 < 0:
#                    brVal2 = 0.001
            # ===================================================        
            if not divideByFlav:
                myHisto.Fill(brVal,brVal2,eventWeight)
            else:
                myHisto[histoIdx].Fill(brVal,brVal2,eventWeight)

    print dir, nTotalEvents
    return myHisto, nTotalEvents

def plotStack(brName,brLabel,nbins,start,end,selections="",cuts=[], dataset="", isLog=False, filePre="", MCWeightName=MCWeightName, DataWeightName=DataWeightName, nminus1=False, doCombine=False,brName2D="",brLabel2="",nbins2=5,start2=0,end2=1, finalHistList=[], histoDList=[], drawStyle="",varBin1=[],varBin2=[],makeROOT=False,noRatio=False,makeCustomH=False,yTitle=yTitle,outDir=outDir,rootPath=rootPath,pathSuff="",useXSecUnc="",MCStat="",dataStat="",SFfile="",drawDataMCRatioLine=False,normTotalMC=False):
    
    if not brName2D=="": noRatio=True
    
    global wtFile, cWtHist, bWtHist, lWtHist, reWeight
    if SFfile!="":
        reWeight = True
        wtFile = TFile.Open(SFfile,"READ")
        cWtHist = wtFile.Get("SFc_hist_central")
        bWtHist = wtFile.Get("SFb_hist_central")
        lWtHist = wtFile.Get("SFl_hist_central")
        outDir.rstrip('/')
        outDir += "_" + SFfile.split('.')[0].split('_')[1]
        print "Using c-tag SF file:", SFfile
    else:
        reWeight = False
    
    if not outDir.endswith("/"): outDir += "/"
    os.system("mkdir -p "+outDir)
    # ================= Define names, locations, etc. ===================
    # colours = [kCyan,kBlue,kGreen,kRed,kOrange,kOrange-7,kMagenta,kYellow,kGray+2,kWhite]
    colours=[]
    colourNames = [kCyan,kYellow,kMagenta,kBlue,kGreen,kRed,kGray]
    for col in colourNames:
        colours.append(col)
        colours.append(col+1)
        colours.append(col+3)
        colours.append(col-9)

    sampleNames =   ["W+c","W+cc","W+uds","W+b"]*5   + \
                    ["DY+c","DY+cc","DY+uds","DY+b"]     + \
                    ["ttbar->c","ttbar->cc","ttbar->uds","ttbar->b"]       + \
                    ["ST->c","ST->cc","ST->uds","ST->b"]*5+ \
                    ["VV->c","VV->cc","VV->uds","VV->b"]*3

    if useQCD:
        if moreQCD: sampleNames += ["QCD->c","QCD->cc","QCD->uds","QCD->b"]*4
        sampleNames += ["QCD->c","QCD->cc","QCD->uds","QCD->b"]*8

    WPaths      = [
                    rootPath+"WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                   rootPath+"W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                   rootPath+"W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                   rootPath+"W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                   rootPath+"W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/"
                    #
                    # rootPath+"WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                    # rootPath+"WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                    # rootPath+"WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                    # rootPath+"WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                    # rootPath+"WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                    # rootPath+"WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
                    # rootPath+"WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/"
                  ]

    samplePaths = [
#                    rootPath+"DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
#                    rootPath+"DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
#                    rootPath+"DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
#                    rootPath+"DYJetsToLL_M-50_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
#                    rootPath+"DYJetsToLL_M-50_HT-800to1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
#                    rootPath+"DYJetsToLL_M-50_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",
#                    rootPath+"DYJetsToLL_M-50_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/",

#                    rootPath+"DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/",
                    rootPath+"DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",

                    rootPath+"TT_TuneCUETP8M2T4_13TeV-powheg-pythia8",

                    rootPath+"ST_s-channel_4f_InclusiveDecays_13TeV-amcatnlo-pythia8",
                    rootPath+"ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1",
                    rootPath+"ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1",
                    rootPath+"ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4",
                    rootPath+"ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1",
                    #
                    rootPath+"WW_TuneCUETP8M1_13TeV-pythia8",
                    rootPath+"WZ_TuneCUETP8M1_13TeV-pythia8",
                    rootPath+"ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8"
                    # rootPath+"ZZTo2Q2Nu_13TeV_amcatnloFXFX_madspin_pythia8",
                    ]
    if useQCD:
        if moreQCD:
            samplePaths += [
                    rootPath+"QCD_Pt-15to20_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-20to30_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-50to80_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8"]

        samplePaths += [
                    rootPath+"QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
                    rootPath+"QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8"
                    ]


    AllSamplePaths = WPaths+samplePaths

    AllSamplePaths = [i.rstrip('/')+pathSuff for i in AllSamplePaths]

    sMuPath     =   rootPath+"SingleMuon/"
    sElePath    =   rootPath+"SingleElectron/"
    dMuPath     =   rootPath+"DoubleMuon/"
    dEGPath     =   rootPath+"DoubleEG/"
    dMuEGPath     =   rootPath+"MuonEG/"

    WXSecs   = [
                61526.7,        #inclusive
               11786.1,        #W1Jets
               3854.2,         #W2Jets
               1273.6,         #W3Jets
               701.4           #W4Jets

                 # 1345*1.21,      #100-200
                 # 359.7*1.21,     #200-400
                 # 48.91*1.21,     #400-600
                 # 12.05*1.21,     #600-800
                 # 5.501*1.21,     #800-1200
                 # 1.329*1.21,     #1200-2500
                 # 0.03216*1.21    #2500-inf
                ]

    OtherXSecs=[
#                147.4*1.23,     # DYJets 100-200
#                41.04*1.23,     # 200-400
#                5.674*1.23,     # 400-600
#                1.358*1.23,     # 600-800
#                0.6229*1.23,    # 800-1200
#                0.1512*1.23,    # 1200-2500
#                0.003659*1.23,  # 2500-inf

#                2075.14*3,      #inclusive DYJets amcatnlo
                6225.42,    #inclusive DYJets MG

                831.76,          # ttbar

                10.12,         # ST
                26.38,
                44.33,
                35.85,
                35.85,
                #
                64.3,          # VV
                23.43,
                3.222
                # 4.033,
                ]


    if useQCD:
        if moreQCD:
            OtherXSecs += [
                    1273190000*0.003,
                    558528000*0.0053,      # QCD Mu enriched
                    139803000*0.01182,
                    19222500*0.02276
                    ]
        OtherXSecs += [
                2758420*0.03844,
                469797*0.05362,
                117989*0.07335,
                7820.25*0.10196,
                645.528*0.12242,
                187.109*0.13412,
                32.3486*0.14552,
                10.4305*0.15544
                ]


    WXSecsUnc= [    2312,
                    31.57,
                    11.22,
                    3.36,
                    1.85

                    # 1.2*1.21,
                    # 0.2*1.21,
                    # 0.072*1.21,
                    # 0.0073*1.21,
                    # 0.017*1.21,
                    # 0.0025*1.21,
                    # 0.000104*1.21
                    ]
    OtherXSecUnc = [
                     # 0.1399*1.23,       # DYJets HT binned
                     # 0.04009*1.23,
                     # 0.005455*1.23,
                     # 0.001307*1.23,
                     # 0.0005996*1.23,
                     # 0.0001884*1.23,
                     # 5.548e-6*1.23,

                    124.5,                 #Incl DY
                    64.26,                 # ttbar

                    0.01334,               # ST
                    1.32,
                    1.76,
                    1.7,
                    1.7,

                    0.02817,                # VV
                    0.01048,
                    0.004901
                    # 0.007222
    ]

    if useQCD:
        if moreQCD:
            OtherXSecUnc += [
                    0,
                    0,      # QCD Mu enriched
                    0,
                    0
                    ]
        OtherXSecUnc += [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
                ]

    XSecMap = {
                'W' : [0,4],
                'DY': [5,5],
                'TT': [6,6],
                'ST': [7,11],
                'VV': [12,14]
            }

    AllXSecs = WXSecs+OtherXSecs
    AllXSecUnc = WXSecsUnc+OtherXSecUnc

    assert len(AllXSecs)==len(AllXSecUnc)
    assert len(AllXSecs)==len(AllSamplePaths)

    if '_' in useXSecUnc:
        procName = useXSecUnc.split('_')[1]
        direction = useXSecUnc.split('_')[2]
        for idx in range(XSecMap[procName][0],XSecMap[procName][1]+1):
            if direction == "up":
                AllXSecs[idx] += AllXSecUnc[idx]
            elif direction == "down":
                AllXSecs[idx] -= AllXSecUnc[idx]
            else:
                raise ValueError
        print "Using XSec uncertainty:", useXSecUnc

    XSecs     =[y for x in AllXSecs for y in 4*[x]]
    # print "XSecs:", XSecs

    # XSecsUnc  =[y for x in WXSecsUnc for y in 4*[x]]

    finalHists = {}
    sampleNamesSet = list(sorted(set(sampleNames),key=sampleNames.index))

    if not dataset=="":
        if dataset=="smu":
            datadir = sMuPath
        elif dataset=="sele":
            datadir = sElePath
        elif dataset=="dmu":
            datadir = dMuPath
        elif dataset=="deg":
            datadir = dEGPath
        elif dataset=="mue":
            datadir = dMuEGPath
            global lumi
            lumi = 35608
        else:
            raise ValueError

    c = TCanvas("main",brLabel,1200,1200)
    c.SetCanvasSize(1200,1200)
#    c.SetWindowSize(1200,1200)

    # ======================= Selection info =========================
    if nminus1:
        if brName in selections:
            selIdx = selections.index(brName)
            del selections[selIdx]
            del cuts[selIdx]
            print "Plotting (n-1) cuts plot..."
        else:
            print "Failed to plot (n-1) cuts plot, plotting all-cuts plot instead..."
    if len(selections) > 0:
        print "Selections:"
        for iSel, selName in enumerate(selections):
            if len(cuts[iSel])<=2:
                rangeText ="in"
            else:
                rangeText = "not in"
            print "  ->",selName,rangeText,"["+str(cuts[iSel][0])+","+str(cuts[iSel][1])+"]"
    # ----------------------------------------------------------------

    # =================== Generate output filename ===================
    if not filePre=="": filePre += "_"
    if nminus1: filePre += "nminus1_"
    saveName = filePre+getbrText(brName)
    if not selections == "":
        for iSel, selection in enumerate(selections):
            if selection in [["M_RelIso",0],"hardMu_Jet_PtRatio",["M_dz",0],["M_dxy",0],["M_sip3d",0]]: continue
            if selection in [["E_RelIso",0],"hardE_Jet_PtRatio",["E_dz",0],["E_dxy",0],["E_sip3d",0]]: continue
            saveName += "+"
            if type(selection) is str:
                saveName += selection+"_"+str(cuts[iSel][0])+"-"+str(cuts[iSel][1])
            elif type(selection) is list:
                saveName += selection[0]+"_"+str(selection[1])+"_"+str(cuts[iSel][0])+"-"+str(cuts[iSel][1])
    # ----------------------------------------------------------------

    if not doCombine:
        # ================= Make individual histograms ===================
        # WHists = []
        integrals = []
        # for WPath in WPaths:
        #     histo, nTot = makeHisto(WPath,"Events",brName,brLabel,nbins,start,end,weightName=MCWeightName,divideByFlav=True,selections=selections,cuts=cuts,brName2D=brName2D,nbins2=nbins2,start2=start2,end2=end2,varBin1=array('d',varBin1),varBin2=array('d',varBin2))
        #     for idx in range(4):
        #         WHists.append(histo[idx])
        #         integrals.append(nTot)
        #         # integrals.append(eff_xsec[WPath.strip('/').split('/')[-1]])
        #
        # allHists = WHists[:]
        # for dir in samplePaths:
        #     histo, nTot = makeHisto(dir,"Events",brName,brLabel,nbins,start,end,weightName=MCWeightName,selections=selections,cuts=cuts,brName2D=brName2D,nbins2=nbins2,start2=start2,end2=end2,varBin1=array('d',varBin1),varBin2=array('d',varBin2))
        #     allHists.append(histo)
        #     integrals.append(nTot)
        #     # integrals.append(eff_xsec[dir.strip('/').split('/')[-1]])
        allHists=[]
        for dir in AllSamplePaths:
            histo, nTot = makeHisto(dir,"Events",brName,brLabel,nbins,start,end,weightName=MCWeightName,divideByFlav=True,selections=selections,cuts=cuts,brName2D=brName2D,nbins2=nbins2,start2=start2,end2=end2,varBin1=array('d',varBin1),varBin2=array('d',varBin2),makeCustomH=makeCustomH)
            for idx in range(4):
                allHists.append(histo[idx])
                integrals.append(nTot)
        # ----------------------------------------------------------------

        # ================= Evaluate normalization factors ===================
        normFactors = []

        for ind, iHist in enumerate(allHists):
            if integrals[ind] > 0:
                normF = lumi * XSecs[ind] / integrals[ind]
                # normF = integrals[ind]
            else:
                normF = 0

            nSelEvents = iHist.Integral()
            normFactors.append(normF)
            iHist.Scale(normF)
            print sampleNames[ind],": Total MC:", integrals[ind], "; Selected Events:", nSelEvents, "; Norm Factor:", normF, "; Events in stack:", iHist.Integral()
        # -------------------------------------------------------------------

        # ===================== Evaluate MC stat errors ======================
        histoErr = allHists[0].Clone()
        for iHist in range(1,len(allHists)):
            histoErr.Add(allHists[iHist])
        # --------------------------------------------------------------------

        # ================= Concatenate histograms of same samples ===============
        for sampName in sampleNamesSet:
            histCount = 0
            for ind, sampName2 in enumerate(sampleNames):
                if sampName==sampName2:
                    if histCount==0:
                        tempHist = allHists[ind].Clone()
                    else:
                        tempHist.Add(allHists[ind])
                    histCount += 1

            if not MCStat=="":
                direction = MCStat.split("_")[1]
                if brName2D=="":
                    for binx in range(1,tempHist.GetNbinsX()+1):
                        if direction=="up":
                            tempHist.SetBinContent(binx,tempHist.GetBinContent(binx)+tempHist.GetBinError(binx))
                            tempHist.SetBinError(binx,0.)
                        elif direction=="down":
                            tempHist.SetBinContent(binx,tempHist.GetBinContent(binx)-tempHist.GetBinError(binx))
                            tempHist.SetBinError(binx,0.)
                        else:
                            raise ValueError
                else:
                    for binx in range(1,tempHist.GetNbinsX()+1):
                        for biny in range(1,tempHist.GetNbinsY()+1):
                            if direction=="up":
                                tempHist.SetBinContent(binx,biny,tempHist.GetBinContent(binx,biny)+tempHist.GetBinError(binx,biny))
                                tempHist.SetBinError(binx,biny,0.)
                            elif direction=="down":
                                tempHist.SetBinContent(binx,biny,tempHist.GetBinContent(binx,biny)-tempHist.GetBinError(binx,biny))
                                tempHist.SetBinError(binx,biny,0.)
                            else:
                                raise ValueError

            finalHists[sampName] = tempHist.Clone()


        # -------------------------------------------------------------------

    #Combine
    if doCombine:
        for ind, iName in enumerate(sampleNamesSet):
            finalHists[iName] = finalHistList[0][iName]
            for iHistList in range(1,len(finalHistList)):
                finalHists[iName].Add(finalHistList[iHistList][iName])

    # Colour and legend
    legTopMargin = 0.90 - int(dataset=="" or noRatio)*0.04
    legend = TLegend(0.15, 0.7, 0.89, legTopMargin,"") #,"brNDC"
    legend.SetFillStyle(0)

    legend.SetTextSize(0.02)
    legend.SetNColumns(4)

    for ind, iName in enumerate(sampleNamesSet):
        finalHists[iName].SetFillColor(colours[ind])
        legend.AddEntry(finalHists[iName],iName,"f")
        print iName,":", finalHists[iName].Integral()

    # ================= Make stack histogram ===================
    myStack = THStack("myStack","")

    sampleNamesSet.reverse()
    for iName in sampleNamesSet:
        myStack.Add(finalHists[iName],"hist")
    print "Created stack histogram."
    # ----------------------------------------------------------

    # ===================== Make data histo ==========================
    if not dataset=="":        
        histoD, nTot = makeHisto(datadir,"Events",brName,brLabel,nbins,start,end,weightName=DataWeightName,selections=selections,cuts=cuts,brName2D=brName2D,nbins2=nbins2,start2=start2,end2=end2,varBin1=array('d',varBin1),varBin2=array('d',varBin2),makeCustomH=makeCustomH)
        
        if normTotalMC:
            MCCount = myStack.GetStack().Last().Integral()
            DataCount = histoD.Integral()
            MCNormFactor = DataCount/MCCount
            
            myStack.Delete()
            myStack = THStack("myStack","")

            for iName in sampleNamesSet:
                finalHists[iName].Scale(MCNormFactor)
                myStack.Add(finalHists[iName],"hist")
            
            histoErr.Scale(MCNormFactor)

        if not dataStat=="":
            direction = dataStat.split("_")[1]
            if brName2D=="":
                for binx in range(1,histoD.GetNbinsX()+1):
                    if direction=="up":
                        histoD.SetBinContent(binx,histoD.GetBinContent(binx)+histoD.GetBinError(binx))
                        histoD.SetBinError(binx,0.)
                    elif direction=="down":
                        histoD.SetBinContent(binx,histoD.GetBinContent(binx)-histoD.GetBinError(binx))
                        histoD.SetBinError(binx,0.)
                    else:
                        raise ValueError
            else:
                for binx in range(1,histoD.GetNbinsX()+1):
                    for biny in range(1,histoD.GetNbinsY()+1):
                        if direction=="up":
                            histoD.SetBinContent(binx,biny,histoD.GetBinContent(binx,biny)+histoD.GetBinError(binx,biny))
                            histoD.SetBinError(binx,biny,0.)
                        elif direction=="down":
                            histoD.SetBinContent(binx,biny,histoD.GetBinContent(binx,biny)-histoD.GetBinError(binx,biny))
                            histoD.SetBinError(binx,biny,0.)
                        else:
                            raise ValueError

        histoD.SetMarkerColor(kBlack)
        histoD.SetMarkerStyle(20)
        histoD.SetMarkerSize(1.8)
        histoD.SetLineColor(1)
    # ----------------------------------------------------------
    if doCombine:
        if len(histoDList)>0:
            dataset="combinemode"
            histoD = histoDList[0]
            for iHistList in range(1,len(histoDList)):
                histoD.Add(histoDList[iHistList])

            histoD.SetMarkerColor(kBlack)
            histoD.SetMarkerStyle(20)
            histoD.SetMarkerSize(1.8)
            histoD.SetLineColor(1)

    # ======================== Draw ============================
    if not dataset=="" and not noRatio:
        upperCanvas = TPad("up","up",0,0.20,1,1)
        upperCanvas.SetBottomMargin(0.03)
        upperCanvas.SetTopMargin(0.06)
        upperCanvas.SetLogy(isLog)
        upperCanvas.Draw()
        upperCanvas.cd()

    TGaxis.SetMaxDigits(4)
    if brName2D=="":
        myStack.Draw()
    else:
        myStack.Draw(drawStyle)
    if dataset=="" or noRatio: myStack.GetXaxis().SetTitle(brLabel)
    if brName2D=="":
        myStack.GetYaxis().SetTitle(yTitle)
    else:
        myStack.GetYaxis().SetTitle(brLabel2)
        myStack.GetHistogram().GetZaxis().SetTitle(yTitle)

    myStack.GetYaxis().SetLabelSize(0.03)
    if not "col" in drawStyle.lower(): legend.Draw()

    if brName2D=="": histoErr.Draw("e2 same")
    # histoErr.Sumw2()
    histoErr.SetFillColor(kGray+3)
    histoErr.SetLineColor(kGray+3)
    histoErr.SetMarkerSize(0)
    histoErr.SetFillStyle(3013)

    histoMC = myStack.GetStack().Last()
    histoBkg=myStack.GetStack().Before(histoMC)
    if dataset=="":
        print "Total MC:", histoMC.Integral()
    else:
        print "Total MC:", histoMC.Integral(), ", Data:",histoD.Integral()

    if not dataset=="":
        histoD.Draw("same p e")
        legend.AddEntry(histoD,"Data","PL")
        maxY = histoD.GetMaximum()
        if brName2D=="" and not testMode:
            if not isLog:
                if myStack.GetMinimum() >= 0: myStack.SetMinimum(1e-3)
                myStack.SetMaximum(maxY*1.5)
            else:
                myStack.SetMinimum(11)
                myStack.SetMaximum(maxY*8)

        if not noRatio:
            c.cd()
            lowerCanvas = TPad("down","down",0,0,1,0.22)
            lowerCanvas.Draw()
            lowerCanvas.cd()
            lowerCanvas.SetTicky(1)
            lowerCanvas.SetLeftMargin(0.1)
            lowerCanvas.SetRightMargin(0.1)
            lowerCanvas.SetTopMargin(0.0)
            lowerCanvas.SetBottomMargin(0.32)
            lowerCanvas.SetFrameFillStyle(0)
            lowerCanvas.SetFrameBorderMode(0)
            lowerCanvas.SetGridy()

            histoRatio = histoD.Clone()
            histoRatio.Divide(histoMC)

            histoRatio.GetYaxis().SetTitle("Data/MC")
            histoRatio.GetYaxis().SetTitleSize(0.11)
            histoRatio.GetYaxis().SetTitleOffset(0.4)
            histoRatio.GetYaxis().SetTitleFont(42)
            histoRatio.GetYaxis().SetLabelSize(0.08)
            histoRatio.GetYaxis().CenterTitle()
            histoRatio.GetYaxis().SetLabelFont(42)

            histoRatio.GetXaxis().SetTitle(brLabel)
            histoRatio.GetXaxis().SetLabelSize(0.1)
            histoRatio.GetXaxis().SetTitleSize(0.12)
            histoRatio.GetXaxis().SetTitleOffset(1)
            histoRatio.GetXaxis().SetTitleFont(42)
            histoRatio.GetXaxis().SetTickLength(0.07)
            histoRatio.GetXaxis().SetLabelFont(42)
            histoRatio.SetTitle("")

            histoRatio.Draw("P e")
            histoRatio.SetMaximum(1.49)
            histoRatio.SetMinimum(0.51)

            hLine = TLine(start,1,end,1)
            hLine.SetLineColor(kRed)
            hLine.Draw()
            
            if drawDataMCRatioLine:
                MCCount = histoMC.Integral()
                DataCount = histoD.Integral()
                MCNormFactor = DataCount/MCCount
                hLine2 = TLine(start,MCNormFactor,end,MCNormFactor)
                hLine2.SetLineColor(kBlue)
                hLine2.Draw()
                
    # ----------------------------------------------------------

    # ======================== LaTeX ==========================
    texTL = TLatex()
    texTL.SetTextSize(0.036)

    texTR = TLatex()
    texTR.SetTextSize(0.032)
    texTR.SetTextAlign(31)

    if dataset=="" or noRatio:
        texTL.DrawLatexNDC(0.13,0.87, "CMS #it{#bf{Preliminary}}")
        texTR.DrawLatexNDC(0.89,0.91, "#bf{"+str(lumi/1000.)+" fb^{-1} (13 TeV)}")
    else:
        upperCanvas.cd()
        texTL.DrawLatexNDC(0.13,0.91, "CMS #it{#bf{Preliminary}}")
        texTR.DrawLatexNDC(0.89,0.95, "#bf{"+str(lumi/1000.)+" fb^{-1} (13 TeV)}")
    # ----------------------------------------------------------

    c.SaveAs(outDir+saveName+".png")

    if makeROOT:
        rootName = outDir+saveName+".root"
        outROOT = TFile.Open(rootName,'RECREATE')
        for ind, iName in enumerate(sampleNamesSet):
            outHName = iName.replace('+','plus')
            outHName = outHName.replace('->','to')
            finalHists[iName].SetNameTitle(outHName,getbrText(brName))
            finalHists[iName].Write()
        histoMC.SetNameTitle("MCSum",getbrText(brName))
        histoMC.Write()
        if not dataset=="":
            histoD.SetNameTitle("Data",getbrText(brName))
            histoD.Write()
        # myStack.SetNameTitle("MCStack",getbrText(brName))
        # myStack.Write()
        histoSig=finalHists[sampleNamesSet[-1]]
        histoSig.SetNameTitle("MCSig",getbrText(brName))
        histoSig.Write()
        histoBkg.SetNameTitle("MCBkg",getbrText(brName))
        histoBkg.Write()
        outROOT.Close()
        print rootName, "created."

    if not doCombine:
        if dataset=="":
            return finalHists
        else:
            return finalHists, histoD

if __name__ == "__main__":
    if len(sys.argv)>1: testMode=True
#    plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV] (mu)",15,0,25,selections=["is_M"],cuts=[[1,1]],dataset="smu",makeROOT=True,noRatio=True)
    plotStack(["jet_CvsL","muJet_idx"],"CvsL",5,0,1,selections=["is_M"],cuts=[[1,1]],dataset="smu",brName2D=["jet_CvsB","muJet_idx"], brLabel2="CvsB",nbins2=5,start2=0,end2=1,drawStyle="",makeROOT=True,SFfile="SFs_semilepExtended.root")
