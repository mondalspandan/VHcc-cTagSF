####################################################
#   Stack Plotting Tool v2 for c-tagging SF Measurement
#   By Spandan Mondal
#   RWTH Aachen University, Germany
#   CMS Experiment, CERN
#   https://cern.ch/spmondal
####################################################

from ROOT import *
import ROOT
import os, sys, json
#from VHcc_Weights import eff_xsec
from array import array
gROOT.SetBatch(True)
gStyle.SetOptStat(0)
gStyle.SetLegendBorderSize(0)
from samplesDict import *

TH1DModel = ROOT.RDF.TH1DModel
TH2DModel = ROOT.RDF.TH2DModel

lumi = 35900
# outDir="Plots_190116_3mva80rewt_OS-SS_MuPtJetPtRatioCut_noQCD_RelIso_hardLepJetPtRatio_dxyz_sip3d_nJet/"
outDir="Plots_20201030_test"
# outDir="Plots_190124_Test"
yTitle="Events"
MCWeightName="eventWeight"          #"genWeight"      #
DataWeightName="eventWeight"        #   "eventWeight"
rootPath = "/nfs/dust/cms/user/spmondal/ctag_condor/190805_2017_Wc/"
useQCD = False
moreQCD = False
testMode = False
splitbypT = True

splitDYbyHT = False
splitWbynJets = False
splitWbynJetsNLO = False
splitWbyVPt = False

taggerPref = ""
makeBinWtTxt = False
CvLTxtBinning = [-1.,0,.2,.4,.6,.8,1.]
CvBTxtBinning = [-1.,0,.2,.4,.6,.8,1.]


gInpFunc = '''int getBJetIdx(ROOT::VecOps::RVec<double> DiscCvsB, int muJetIdx) {
    auto vec = DiscCvsB;
    vec.erase(vec.begin() + muJetIdx);
    return std::min_element(vec.begin(),vec.end()) - vec.begin();  //index of the jet with lowest DiscCvsB value
}
int getCJetIdx(ROOT::VecOps::RVec<double> DiscCvsB, ROOT::VecOps::RVec<double> DiscCvsL, int muJetIdx) {
    auto bjetidx = getBJetIdx(DiscCvsB,muJetIdx);

    int maxidx = 0, itn = 0;
    double maxval = -1;
    for(auto it = std::begin(DiscCvsL); it != std::end(DiscCvsL); ++it) {
        if (itn == muJetIdx || itn == bjetidx) { itn++; continue; }
        if (*it > maxval) {
            maxval = *it;
            maxidx = itn;
        }
        itn++;
    }
    return maxidx;  //index of the jet with highest DiscCsvL value
}
'''
# gInterpreter.Declare(gInpFunc)

def getbrText(brName):
    if not '[' in brName:
        return brName
    else:
        return brName.replace('[','_').rstrip(']')

def makeHisto(dir,treeName,brName,brLabel,nbins,start,end,weightName="",selections="", divideByFlav=False, brName2D="",nbins2=5,start2=0,end2=1,varBin1=[],varBin2=[],getSFUnc=False,customJetInd="",useEventCount=False,ptwt="1.",filePre=""):
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
#        if "Run2018A" in fl or "Run2018B" in fl or "Run2018C" in fl: continue
        iF = TFile.Open(fl)
        if bool(iF) == False or iF.IsZombie() or iF.TestBit(TFile.kRecovered):
            print "Error in file %s, skipping."%fl
            continue
        myChain.Add(fl)
        if useEventCount: hTotal = iF.Get("h_nEvent")
        else:  hTotal = iF.Get("h_total")
        nTotalEvents += hTotal.Integral()
        iF.Close()
        if testMode: break

    brText = getbrText(brName)
    if brLabel == "": brLabel = brText

    blankArray=array('d',[])
    #if not divideByFlav:
        #if brName2D == "" and not makeCustomH:
            #myHisto = TH1F(brText+dir,brLabel,nbins,start,end)
        ## elif makeCustomH:
        ##     myHisto = customHisto.Clone()
        ##     myHisto.SetNameTitle(brText+dir,brLabel)
        #else:
            #if varBin1==blankArray and varBin2==blankArray:
                #myHisto = TH2F(brText+dir,brLabel,nbins,start,end,nbins2,start2,end2)
            #elif varBin1!=blankArray and varBin2==blankArray:
                #myHisto = TH2F(brText+dir,brLabel,nbins,varBin1,nbins2,start2,end2)
            #elif varBin1==blankArray and varBin2!=blankArray:
                #myHisto = TH2F(brText+dir,brLabel,nbins,start,end,nbins2,varBin2)
            #else:
                #myHisto = TH2F(brText+dir,brLabel,nbins,varBin1,nbins2,varBin2)
        #myHisto.Sumw2()
    #else:
        #myHisto=[]
        #for idx in range(4):
            #if brName2D == "" and not makeCustomH:
                #myHisto.append(TH1F(brText+dir+str(idx),brLabel,nbins,start,end))
            ## elif makeCustomH:
            ##     myHisto.append(customHisto.Clone())
            ##     myHisto[idx].SetNameTitle(brText+dir+str(idx),brLabel)
            #else:
                #if varBin1==blankArray and varBin2==blankArray:
                    #myHisto.append(TH2F(brText+dir+str(idx),brLabel,nbins,start,end,nbins2,start2,end2))
                #elif varBin1!=blankArray and varBin2==blankArray:
                    #myHisto.append(TH2F(brText+dir+str(idx),brLabel,nbins,varBin1,nbins2,start2,end2))
                #elif varBin1==blankArray and varBin2!=blankArray:
                    #myHisto.append(TH2F(brText+dir+str(idx),brLabel,nbins,start,end,nbins2,varBin2))
                #else:
                    #myHisto.append(TH2F(brText+dir+str(idx),brLabel,nbins,varBin1,nbins2,varBin2))
            #myHisto[idx].Sumw2()
    
    DF = ROOT.RDataFrame(myChain)
    
    if brName2D == "":
        histoModel = TH1DModel(brText+dir,brLabel,nbins,start,end)
    else:
        histoModel = TH2DModel(brText+dir,brLabel,nbins,start,end,nbins2,start,end)
    
    if customJetInd != "":
        jetind = customJetInd
    elif "jet_" in brName and '[' in brName:
        jetind = brName.split('[')[1].split(']')[0]
    else:
        jetind = "max(0.,muJet_idx)"

    if weightName == "":
        eventWeight = 1.
    else:
        if 'TTTo' not in dir and 'PSWeight' in weightName:

            #eventWeight = '*'.join([i for i in weightName.split('*') if 'PSWeight' not in i])
            eventWeight = weightName.replace("*PSWeightFSR_down","").replace("*PSWeightFSR_up","").replace("*PSWeightISR_down","").replace("*PSWeightISR_up","")
        else:
            eventWeight = weightName
        if useEventCount: eventWeight = "(%s)/genWeight"%(eventWeight)
    eventWeight = eventWeight + "*(%s)"%ptwt.replace("JETIDX",jetind)

    # WJet LO reweighting
    NLOwt = 1.
    if "amcatnlo" not in dir:
        if "Wc_m" in filePre or "TT_semim" in filePre:
            if "JetsToLNu_Tune" in dir:
                if era=="2017": NLOwt = 1.239926888
                elif era=="2018": NLOwt = 1.68348
        elif "Wc_e" in filePre or "TT_semie" in filePre:
            if "JetsToLNu_Tune" in dir:
                if era=="2017": NLOwt = 1.275986578
                elif era=="2018": NLOwt = 1.372276

        if NLOwt != 1.:
            print "Reweighting LO WJet by factor",NLOwt
            eventWeight = eventWeight + "*" + str(NLOwt)


    DF = DF.Define("newWeight",eventWeight)
    
    sampSels = ""
    if splitDYbyHT and "DYJetsToLL_M-50_Tune" in dir:   sampSels += " && LHE_HT < 100"
    if splitWbynJets and "WJetsToLNu_Tune" in dir:      sampSels += " && (LHE_Njets < 1 || LHE_Njets > 4)"
    if splitWbynJetsNLO and "WJetsToLNu_Tune" in dir:      sampSels += " && LHE_Njets > 2"
    if splitWbyVPt and ("WJetsToLNu_Tune" in dir or "WJetsToLNu_0J" in dir or "WJetsToLNu_1J" in dir or "WJetsToLNu_2J" in dir):      sampSels += " && LHE_Vpt < 100"
    
    if "Cvs" in brName:
        newbrexp = "max(min(%s,0.999999),-0.1) > -0.099 && max(min(%s,0.999999),-0.1) <=0 ? 1e-3 : max(min(%s,0.999999),-0.1)"%(brName,brName,brName)
        DF = DF.Define("newBr",newbrexp)
        newBr = "newBr"
        if brName2D != "":
            newbrexp2 = "max(min(%s,0.999999),-0.1)"%(brName2D)
            DF = DF.Define("newBr2",newbrexp2)
            newBr2 = "newBr2"
    else:
        DF = DF.Define("newBr",brName)
        newBr = "newBr"   
        newBr2 = "newBr2"      
    
    if reWeight and divideByFlav:
        DF = DF.Define("newWeight2",
                       '''  float ctagWt = 1.;
                            int flav, xbin, ybin;
                            float CvsLval,CvsBval,jetpT;
                            TH2F *wtHist;
                            for (int ij=0; ij<jet_nJet;ij++) {
                                //if (ij==muJet_idx) continue;
                                flav = int(jet_hadronFlv[ij]);
                                CvsLval = jet_%sCvsL[ij];
                                CvsBval = jet_%sCvsB[ij];
                                jetpT = jet_Pt[ij];
                                if (flav == 4) {
                                    if (splitbypT) {
                                        if (jetpT < 40)  wtHist = cWtHist_below40;
                                        else wtHist = cWtHist_above40;
                                    }
                                    else {
                                        wtHist = cWtHist;
                                    }
                                }
                                else if (flav == 5) {
                                    if (splitbypT) {
                                        if (jetpT < 40)  wtHist = bWtHist_below40;
                                        else wtHist = bWtHist_above40;
                                    }
                                    else {
                                        wtHist = bWtHist;
                                    }
                                }
                                else {
                                    if (splitbypT) {
                                        if (jetpT < 40)  wtHist = lWtHist_below40;
                                        else wtHist = lWtHist_above40;
                                    }
                                    else {
                                        wtHist = lWtHist;
                                    }
                                }
                                
                                xbin = wtHist->GetXaxis()->FindBin(CvsLval);
                                ybin = wtHist->GetYaxis()->FindBin(CvsBval);
                                ctagWt *= wtHist->GetBinContent(xbin,ybin);
                            }
                            return newWeight*ctagWt;
                       '''%(taggerPref,taggerPref)
                       )
    else:
        DF = DF.Define("newWeight2","newWeight")
    
    if divideByFlav:
        myHisto = []
        
        for flav, hadflav in [('c',4),('b',5),('uds',0),('lep',0)]:
            flavSel = " && jet_hadronFlv[%s] == %d"%(jetind,hadflav)
            if flav == 'uds':
                flavSel += " && jet_isHardLep[%s] == 0"%jetind
            elif flav == 'lep':
                flavSel += " && jet_isHardLep[%s] == 1"%jetind
                
            #flavSel = " && ( (muJet_idx < 0 && jet_hadronFlv[0] == %d) || (muJet_idx >= 0 && jet_hadronFlv[muJet_idx] == %d))"%(hadflav,hadflav)
            #if flav == 'uds':
                #flavSel += " && ( (muJet_idx < 0 && jet_isHardLep[0] == 0) || (muJet_idx >= 0 && jet_isHardLep[muJet_idx] == 0) )"
            #elif flav == 'lep':
                #flavSel += " && ( (muJet_idx < 0 && jet_isHardLep[0] == 1) || (muJet_idx >= 0 && jet_isHardLep[muJet_idx] == 1) )"

            thisflavDF = DF.Filter(selections + sampSels + flavSel)    
            if brName2D == "":
                myHisto.append( thisflavDF    \
                                .Histo1D(   histoModel,
                                            newBr,
                                            "newWeight2"
                                        )
                                )
            else:
                myHisto.append( thisflavDF    \
                                .Histo2D(   histoModel,
                                            newBr, newBr2,
                                            "newWeight2"
                                        )
                                )
            if getSFUnc:
                flName = dir.split('/')[-1]
                thisflavDF.Snapshot("Events","StackerTemp.root")
                tempf = TFile("StackerTemp.root","READ")
                temptree = tempf.Get("Events")
                if "muJet_idx==0?1:0" in jetind:
                    txtind = '1 if int(ev.muJet_idx) == 0 else 0'
                elif jetind.isdigit(): txtind = str(jetind)
                else: txtind = "ev."+str(jetind)
                for ev in temptree:
                    exec("indtxt = int(%s)"%txtind)
                    # print indtxt
                    exec("flav2 = ev.jet_hadronFlv[%s]"%indtxt)
                    exec("CvsBval = ev.jet_%sCvsB[%s]"%(taggerPref,indtxt))
                    exec("CvsLval = min(ev.jet_%sCvsL[%s],0.99999)"%(taggerPref,indtxt))
                    exec("xaxisval = ev.jet_%sCvs%s[%s]"%(taggerPref,("L" if "CvsL" in brName else "B"),indtxt))
                    oldwt = ev.newWeight2
                    if flav2 == 4:
                        wtHist = ROOT.cWtHist
                        wtHistUp = ROOT.cWtHistStatUp
                    elif flav2 == 5:
                        wtHist = ROOT.bWtHist
                        wtHistUp = ROOT.bWtHistStatUp
                    else:
                        wtHist = ROOT.lWtHist
                        wtHistUp = ROOT.lWtHistStatUp

                    binidx = SFUnc.GetXaxis().FindBin(xaxisval)
                    xbin = wtHist.GetXaxis().FindBin(CvsLval)
                    ybin = wtHist.GetYaxis().FindBin(CvsBval)   
                    ctagWt = wtHist.GetBinContent(xbin,ybin)
                    ctagWtUp = wtHistUp.GetBinContent(xbin,ybin)
                    # if ctagWt > 0:                        
                    #     statUnc = (ctagWtUp - ctagWt)/ctagWt*abs(oldwt)
                    # else:
                    #     print "** Found weird ctagWt = %f, for CvsB = %f and CvsL = %f."%(ctagWt,CvsBval,CvsLval)
                    #     statUnc = abs(oldwt)

                    thisKey = (flav2,ctagWt,ctagWtUp)
                    if thisKey not in SFBinCounts:
                        SFBinCounts[binidx][thisKey] = {}
                    if flName in SFBinCounts[binidx][thisKey]:
                        SFBinCounts[binidx][thisKey][flName] += oldwt
                    else:
                        SFBinCounts[binidx][thisKey][flName] = oldwt

                    if binidx == 18: print thisKey,oldwt,CvsBval,CvsLval 
                tempf.Close()
                print "    Evaluated SF uncertainties for flavour", flav

                '''
                        TFile root_file("StackerTemp.root");
                        TTreeReader reader("Events", &root_file);
                        TTreeReaderValue<vector<float>> jet_hadronFlv(reader, "jet_hadronFlv");

                            int flav2 = jet_hadronFlv[%s];
                            float CvsBval2 = jet_%sCvsB[%s];
                            float CvsLval2 = jet_%sCvsL[%s];
                            float xaxisval = %s; '''%(jetind,taggerPref,jetind,taggerPref,jetind,newBr)
                    
                '''
                            TH2F *wtHist2, *wtHistUp;
                            float ctagWt2, ctagWtUp, statUnc, wt;
                            int binidx, xbin2, ybin2;
                            string binname;
                            
                            if (flav2 == 4) {
                                wtHist2 = cWtHist;
                                wtHistUp = cWtHistStatUp;
                            }
                            else if (flav2 == 5) {
                                wtHist2 = bWtHist;
                                wtHistUp = bWtHistStatUp;
                            }
                            else {
                                wtHist2 = lWtHist;
                                wtHistUp = lWtHistStatUp;
                            }
                            binidx = SFUnc->GetXaxis()->FindBin(xaxisval);
                            xbin2 = wtHist2->GetXaxis()->FindBin(CvsLval2);
                            ybin2 = wtHist2->GetYaxis()->FindBin(CvsBval2);
                            ctagWt2 = wtHist2->GetBinContent(xbin2,ybin2);
                            ctagWtUp = wtHistUp->GetBinContent(xbin2,ybin2);
                            statUnc = ctagWtUp - ctagWt2;
                            binname = to_string(flav2)+'_'+to_string(ctagWt2)+'_'+to_string(ctagWtUp);

                            auto it = std::find(SFBinNames[binidx].begin(), SFBinNames[binidx].end(), binname);
                            if(it != SFBinNames[binidx].end()) {                            
                                int index = std::distance(SFBinNames[binidx].begin(), it);
                                int oldcount = SFBinCounts[binidx][index];
                                wt = (pow((oldcount+1),2)-pow(oldcount,2))*pow(statUnc,2);
                                SFBinCounts[binidx][index] = oldcount+1;
                            } else {
                                SFBinNames[binidx].push_back(binname);
                                SFBinCounts[binidx].push_back(1);
                                wt = pow(statUnc,2);
                            }
                            SFUnc->Fill(xaxisval,wt);
                            return wt;
                        '''

                # thisflavDF = thisflavDF.Define("FilledSFUnc", uncsffunc)

                # vec = vector('string')()
                # vec.push_back("jet_hadronFlv[%s]"%jetind)
                # vec.push_back("jet_%sCvsL[%s]"%(taggerPref,jetind))
                # vec.push_back("jet_%sCvsB[%s]"%(taggerPref,jetind))
                # vec.push_back(newBr)
                # thisflavDF.Foreach(ROOT.fillUnc,vec)
#            print selections + sampSels + flavSel, newBr
    else:
        if brName2D == "":
            myHisto = DF.Filter(selections + sampSels)     \
                            .Histo1D(   histoModel,
                                        newBr,
                                        "newWeight2"
                                    )       
        else:
            myHisto = DF.Filter(selections + sampSels)     \
                            .Histo2D(   histoModel,
                                        newBr,newBr2,
                                        "newWeight2"
                                    )    
    
    
    print dir, nTotalEvents    
        
    
    if divideByFlav:
        retHistos = []
        for hist in myHisto:
            retHistos.append(hist.Clone())
#            print hist.Integral()
        return retHistos, nTotalEvents
    
    return myHisto.Clone(), nTotalEvents

def plotStack(brName,brLabel,nbins,start,end,selections="",cuts=[], dataset="", isLog=False, filePre="",filePre2="",filePost="", MCWeightName=MCWeightName, DataWeightName=DataWeightName, nminus1=False, doCombine=False,brName2D="",brLabel2="",nbins2=5,start2=0,end2=1, finalHistList=[], histoDList=[], drawStyle="",varBin1=[],varBin2=[],makePNG=True,makeROOT=False,noRatio=False,yTitle=yTitle,outDir=outDir,rootPath=rootPath,pathSuff="",useXSecUnc="",MCStat="",dataStat="",SFfile="",SFhistSuff="",drawDataMCRatioLine=False,normTotalMC=False,binWtTxt=False,getSFUnc = False,customJetInd="",normByPtDir=""):
    if not makePNG and not makeROOT:
        print "Neither PNG nor ROOT output was asked for. Exiting."
        sys.exit(1)
    filePre += filePre2
    global lumi,era
    if '_2018_' in rootPath or 'UL2018' in rootPath:
        era = "2018"
        lumi = 59960
    elif '_2017_' in rootPath or 'UL2017' in rootPath:
        era = "2017"
        lumi = 41540
    elif "UL2016Pre" in rootPath:
        era = "UL2016Pre"
        lumi = 19500
    elif "UL2016Post" in rootPath:
        era = "UL2016Post"
        lumi = 16800
    else:
        era = "2016"

    if not brName2D=="": noRatio=True
    
    global wtFile, cWtHist, bWtHist, lWtHist, reWeight, makeBinWtTxt, taggerPref
    if SFfile!="":
        reWeight = True
        
        #wtFile = TFile.Open(SFfile,"READ")
        #cWtHist = wtFile.Get("SFc_hist_central")
        #bWtHist = wtFile.Get("SFb_hist_central")
        #lWtHist = wtFile.Get("SFl_hist_central")
        
        if "DeepJet" in SFfile:
            taggerPref = "DeepFlav"
        else:
            taggerPref = ""

        if "CvsB" in SFfile: adapDir = "CvsB"
        else: adapDir = "CvsL"
        
        splitbypT = False
        if "above40" in SFfile or "below40" in SFfile:
            splitbypT = True
            
        print "Tagger Pref:", taggerPref
        print "Split by pT:", splitbypT
        
        if splitbypT:
            gInpCmd = '''
                    TFile *wtFile = new TFile("%s");
                    TH2F *cWtHist_below40 = (TH2F*)wtFile->Get("below40_SFc_PREFCvsL");
                    TH2F *bWtHist_below40 = (TH2F*)wtFile->Get("below40_SFb_PREFCvsL");
                    TH2F *lWtHist_below40 = (TH2F*)wtFile->Get("below40_SFl_PREFCvsL");
                    TH2F *cWtHist_above40 = (TH2F*)wtFile->Get("above40_SFc_PREFCvsL");
                    TH2F *bWtHist_above40 = (TH2F*)wtFile->Get("above40_SFb_PREFCvsL");
                    TH2F *lWtHist_above40 = (TH2F*)wtFile->Get("above40_SFl_PREFCvsL");
                    
                    TH2F *cWtHist,*bWtHist,*lWtHist;
                    int splitbypT = 1;
            '''%(SFfile).replace("PREF",taggerPref)
            
        else:
            gInpCmd = '''
                    TFile *wtFile = new TFile("%s");
                    TH2F *cWtHist = (TH2F*)wtFile->Get("SFc_histHISTSUFF");
                    TH2F *bWtHist = (TH2F*)wtFile->Get("SFb_histHISTSUFF");
                    TH2F *lWtHist = (TH2F*)wtFile->Get("SFl_histHISTSUFF");

                    TH2F *cWtHistStatUp = (TH2F*)wtFile->Get("SFc_hist_StatUp");
                    TH2F *bWtHistStatUp = (TH2F*)wtFile->Get("SFb_hist_StatUp");
                    TH2F *lWtHistStatUp = (TH2F*)wtFile->Get("SFl_hist_StatUp");
                    
                    TH2F *cWtHist_below40,*bWtHist_below40,*lWtHist_below40,*cWtHist_above40,*bWtHist_above40,*lWtHist_above40;
                    int splitbypT = 0;
            '''%(SFfile)

        
        gInpCmd = gInpCmd.replace("PREF",taggerPref).replace("ADAP",adapDir).replace("HISTSUFF",SFhistSuff)
        print "\nLoading SF histograms:"
        print gInpCmd  
        gInterpreter.ProcessLine(gInpCmd)
        
        outDir.rstrip('/')
        outDir += "_" + '_'.join(SFfile.rstrip('.root').split('_')[3:])
        print "Updated outdir:",outDir
        print "Using c-tag SF file:", SFfile

        if getSFUnc:
            global SFUnc, SFBinCounts
            SFUnc = TH1F(getbrText(brName)+"_Unc",brLabel,nbins,start,end)
            SFBinCounts = {}
            for ib in range(nbins+2):
                SFBinCounts[ib] = {}
            # gInterpreter.ProcessLine("TH1F *SFUnc = new TH1F(\"%s\",\"%s\",%d,%f,%f);"%(getbrText(brName)+"Unc",brLabel,nbins,start,end))
            # gInterpreter.ProcessLine("vector<vector<string>> SFBinNames; vector<vector<int>> SFBinCounts;")
            # for ib in range(nbins+2):
            #     gInpNew = '''
            #                 vector<string> SFBinNames_%d;
            #                 vector<int> SFBinCounts_%d;
            #                 SFBinNames.push_back(SFBinNames_%d);
            #                 SFBinCounts.push_back(SFBinCounts_%d);
            #     '''%(ib,ib,ib,ib)
                # gInterpreter.ProcessLine(gInpNew)
            # print "Declared quantities to calculate SF uncertainty propagation."
    else:
        reWeight = False
        
    if binWtTxt:
        makeBinWtTxt = True
        binWtTxtFileDict = {}
        normFactByFl = {}
        dataBinErrs = {}
        MCBinErrs = {}

    if normByPtDir!="":
        ptfile = [i for i in os.listdir(normByPtDir) if i.startswith(filePre+"_jet_Pt") and i.endswith(".root")]
        if len(ptfile) < 1:
            print "Did not file Pt file in ",normByPtDir
            sys.exit(3)
        elif len(ptfile) > 1:
            print "WARNING: Found ambiguous matching for Pt file."
        ptfl = TFile.Open(normByPtDir+"/"+ptfile[0],"READ")
        ptd = ptfl.Get("Data")
        ptm = ptfl.Get("MCSum")
        normfact = ptd.Integral(0,ptd.GetNbinsX()+1)/ptm.Integral(0,ptm.GetNbinsX()+1)
        ptm.Scale(normfact)
        ptratio = ptd.Clone()
        ptratio.Divide(ptm)
        ptbinning, ptnorm = [], []
        for ibin in range(1,ptratio.GetNbinsX()+2):
            ptbinning.append(ptratio.GetXaxis().GetBinLowEdge(ibin))
            ptnorm.append(ptratio.GetBinContent(ibin))
        ptfl.Close()
        lastelem = len(ptbinning)-1
        ptwt = ""
        for ibin in range(lastelem):
            ptwt += "(jet_Pt[JETIDX] >= %f && jet_Pt[JETIDX] < %f) ? %f : "%(ptbinning[ibin],ptbinning[ibin+1],ptnorm[ibin])
        ptwt += "(jet_Pt[JETIDX] >= %f) ? %f : 1"%(ptbinning[lastelem],ptnorm[lastelem])
    else: ptwt = "1."

    if not outDir.endswith("/"): outDir += "/"
    os.system("mkdir -p "+outDir)

    # ================= Define names, locations, etc. ===================
    # colours = [kCyan,kBlue,kGreen,kRed,kOrange,kOrange-7,kMagenta,kYellow,kGray+2,kWhite]

    if era == "2016" or "UL2016" in era: samplesDict = samplesDict2016
    elif era == "2017": samplesDict = samplesDict2017
    elif era == "2018": samplesDict = samplesDict2017

    sampleNames = []
    AllSamplePaths = []
    AllXSecs = []
    AllXSecUnc = []

    modXSecFracs = {
        ("DYJets","b") : 0.025,
        ("DYJets","c") : 0.09,
        ("WJets","c") : 0.08
    } 

    if '_' in useXSecUnc:
        if "BRUnc" in useXSecUnc:
            procName = ""
            modprocName = useXSecUnc.split('_')[2]
            modflav = useXSecUnc.split('_')[3]
            direction = useXSecUnc.split('_')[4]
            if modflav == "b": modflavnum = 1
            elif modflav == "c": modflavnum = 0
            else: raise ValueError
            print "Using modded XSec for %s flavour of %s process."%(modflav,modprocName)
        else:
            procName = useXSecUnc.split('_')[1]
            direction = useXSecUnc.split('_')[2]
            print "Using XSec uncertainty:", useXSecUnc
            modprocName = ""
    else:
        procName = ""
        modprocName = ""

    samplesInDir = os.listdir(rootPath)
    if len([i for i in samplesInDir if i.startswith("W1JetsToLNu_")]) > 0:
        global splitWbynJets
        splitWbynJets = True
        print "Will split WJets samples by jet multiplicity."
    if len([i for i in samplesInDir if i.startswith("WJetsToLNu_0J")]) > 0:
        global splitWbynJetsNLO
        splitWbynJetsNLO = True
        print "Will split WJets NLO samples by jet multiplicity."
    if len([i for i in samplesInDir if i.startswith("WJetsToLNu_Pt")]) > 0:
        global splitWbyVPt
        splitWbyVPt = True
        print "Will split WJets NLO samples by LHE V Pt."
    if len([i for i in samplesInDir if i.startswith("DYJetsToLL_M-50_HT-")]) > 0:
        global splitDYbyHT
        splitDYbyHT = True
        print "Will split DYJets samples by HT bins."

    colours=[]
    colourNames = [kCyan,kYellow,kMagenta,kBlue,kGreen,kRed,kGray]
    samplesToProc = ["WJets","DYJets","ttbar","ST"] #,"VV"]
    if "QCD" in samplesDict:
        if samplesDict["QCD"][0][0].rstrip('/') in samplesInDir:
            samplesToProc.append("QCD")

    for isamp, sName in enumerate(samplesToProc):
        sampleUsed = False
        for samplist in samplesDict[sName]:
            matchlist = [s for s in samplesInDir if samplist[0].strip('/') in s and 'jer' not in s and 'jesTotal' not in s]
            if len(matchlist) == 0:
                print "WARNING: No match found for "+samplist[0]
                continue
            if len(matchlist) > 1:
                print "WARNING: Found multiple matches %s for sample %s."%(matchlist,samplist)
            
            sampname = matchlist[0]
            # if samplist[0].rstrip('/') not in samplesInDir: continue
            sampleUsed = True
            sampleNames += [sName+"(c)",sName+"(b)",sName+"(uds)",sName+"(lep)"]

            AllSamplePaths.append(rootPath+sampname.rstrip('/'))
            XSecNom = samplist[1]

            if sName == procName:
                if direction == "up":     XSecNom += samplist[2]
                elif direction == "down": XSecNom -= samplist[2]
                else:                     raise ValueError

            for i in range(4):
                XSecNomTemp = XSecNom
                if sName == modprocName and i == modflavnum:
                    modfrac = modXSecFracs[(modprocName,modflav)]
                    if direction == "up":     XSecNomTemp += XSecNom*modfrac
                    elif direction == "down": XSecNomTemp -= XSecNom*modfrac
                    else:                     raise ValueError                    
                AllXSecs.append(XSecNomTemp)

        if sampleUsed:
            col = colourNames[isamp]
            colours.append(col)
            colours.append(col-9)
            colours.append(col+2)
            colours.append(col-10)

    AllSamplePaths = [i.rstrip('/')+pathSuff for i in AllSamplePaths]

    sMuPath     =   rootPath+"SingleMuon/"
    sElePath    =   rootPath+"SingleElectron/"
    dMuPath     =   rootPath+"DoubleMuon/"
    dEGPath     =   rootPath+"DoubleEG/"
    dMuEGPath   =   rootPath+"MuonEG/"
    EGPath2018  =   rootPath+"EGamma/"

    finalHists = {}
    sampleNamesSet = list(sorted(set(sampleNames),key=sampleNames.index))

    if not dataset=="":
        if (dataset=="sele" or dataset=="deg") and era=="2018":
            datadir = EGPath2018
        elif dataset=="smu":
            datadir = sMuPath
        elif dataset=="sele":
            datadir = sElePath
        elif dataset=="dmu":
            datadir = dMuPath
        elif dataset=="deg":
            datadir = dEGPath
        elif dataset=="mue":
            datadir = dMuEGPath
            # if era == 2016:
            #     lumi = 35608
        else:
            raise ValueError

    c = TCanvas("main",brLabel,1200,1200)
    c.SetCanvasSize(1200,1200)
#    c.SetWindowSize(1200,1200)

    print "Using era: %s, Lumi: %d"%(era,lumi)

    # ======================= Selection info =========================
    if nminus1:
        if brName in selections:
            selList = selections.split("&&")
            updatedSel = [sel.strip() for sel in selList if not brName in sel]
            selections = ' && '.join(updatedSel)            
            print "Plotting (n-1) cuts plot..."
        else:
            print "Failed to plot (n-1) cuts plot, plotting all-cuts plot instead..."
    if len(selections) > 0:
        print "Selections:"
        for isel in selections.split('&&'):            
            print '  --> '+isel.strip()
        
    # ----------------------------------------------------------------

    # =================== Generate output filename ===================
    if not filePre=="": filePre += "_"
    if nminus1: filePre += "nminus1_"
    saveName = filePre+getbrText(brName)+SFhistSuff+"_"+filePost
    for rem in [" ","?",":","="]:
        saveName = saveName.replace(rem,"")
    #if not selections == "":
        #for iSel, selection in enumerate(selections):
            #if selection in ["hardMu_Jet_PtRatio",["M_dz",0],["M_dxy",0],["M_sip3d",0]]: continue
            #if selection in ["hardE_Jet_PtRatio",["E_dz",0],["E_dxy",0],["E_sip3d",0]]: continue
            #saveName += "+"
            #if type(selection) is str:
                #saveName += selection+"_"+str(cuts[iSel][0])+"-"+str(cuts[iSel][1])
            #elif type(selection) is list:
                #saveName += selection[0]+"_"+str(selection[1])+"_"+str(cuts[iSel][0])+"-"+str(cuts[iSel][1])
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
        histsToFlMap = []
        for dir in AllSamplePaths:
            flName = dir.split('/')[-1]
            print "Starting with "+dir
            evCount = False
            if "amcatnlo" not in dir and (era=="2017" or "UL2016" in era):
                print "Skipping genWeights for",dir
                evCount = True
            histo, nTot = makeHisto(dir,"Events",brName,brLabel,nbins,start,end,weightName=MCWeightName,divideByFlav=True,selections=selections,brName2D=brName2D,nbins2=nbins2,start2=start2,end2=end2,varBin1=array('d',varBin1),varBin2=array('d',varBin2),getSFUnc=getSFUnc,customJetInd=customJetInd,useEventCount=evCount,ptwt=ptwt,filePre=filePre)
            for idx in range(4):
                allHists.append(histo[idx].Clone())
                integrals.append(nTot)
                histsToFlMap.append(flName)
            print "Done."
            if makeBinWtTxt: binWtTxtFileDict[flName] = binWtDict
        
        # gInterpreter.ProcessLine("TFile *nf = new TFile(\"text.root\",\"RECREATE\"); nf->cd(); SFUnc->Write(); nf->Close()")
        # ----------------------------------------------------------------

        # ================= Evaluate normalization factors ===================
        normFactors = []

        for ind, iHist in enumerate(allHists):
            if integrals[ind] > 0:
                normF = lumi * AllXSecs[ind] / integrals[ind]
                # normF = integrals[ind]
            else:
                normF = 0

            nSelEvents = iHist.Integral()
            normFactors.append(normF)
            iHist.Scale(normF)
            if makeBinWtTxt: normFactByFl[histsToFlMap[ind]] = normF
                
            print histsToFlMap[ind], sampleNames[ind],": Total MC:", integrals[ind], "; Selected Events:", nSelEvents, "; Norm Factor:", normF, "; Events in stack:", iHist.Integral()
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

    totalMC = 0
    for ind, iName in enumerate(sampleNamesSet):
        totalMC += finalHists[iName].Integral()
    if totalMC==0: totalMC=1
    for ind, iName in enumerate(sampleNamesSet):
        finalHists[iName].SetFillColor(colours[ind])
        legend.AddEntry(finalHists[iName],iName,"f")
        print iName,":", finalHists[iName].Integral(), ":",finalHists[iName].Integral()*100/totalMC,"%"

    # ================= Make stack histogram ===================
    myStack = THStack("myStack","")

    sampleNamesSet.reverse()
    for iName in sampleNamesSet:
        myStack.Add(finalHists[iName],"hist")
    print "Created stack histogram."
    # ----------------------------------------------------------

    # ===================== Make data histo ==========================
    if not dataset=="":
        histoD, nTot = makeHisto(datadir,"Events",brName,brLabel,nbins,start,end,weightName=DataWeightName,selections=selections,brName2D=brName2D,nbins2=nbins2,start2=start2,end2=end2,varBin1=array('d',varBin1),varBin2=array('d',varBin2))

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
                if MCCount > 0.:
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

    if makePNG: c.SaveAs(outDir+saveName+".png")

    if makeROOT:
        rootName = outDir+saveName+".root"
        outROOT = TFile.Open(rootName,'RECREATE')
        cHist = ""
        bHist = ""
        lHist = ""
        lepHist = ""
        for ind, iName in enumerate(sampleNamesSet):
            outHName = iName.replace('+','plus')
            outHName = outHName.replace('->','to')
            outHName = outHName.replace('(','_').rstrip(")")
            finalHists[iName].SetNameTitle(outHName,getbrText(brName))
            finalHists[iName].Write()
            if iName.endswith("(c)"):
                if cHist == "": cHist = finalHists[iName].Clone()
                else: cHist.Add(finalHists[iName])
            elif iName.endswith("(b)"):
                if bHist == "": bHist = finalHists[iName].Clone()
                else: bHist.Add(finalHists[iName])
            elif iName.endswith("(uds)"):
                if lHist == "": lHist = finalHists[iName].Clone()
                else: lHist.Add(finalHists[iName])
            elif iName.endswith("(lep)"):
                if lepHist == "": lepHist = finalHists[iName].Clone()
                else: lepHist.Add(finalHists[iName])
        cHist.SetNameTitle("c",getbrText(brName))
        cHist.Write()
        bHist.SetNameTitle("b",getbrText(brName))
        bHist.Write()
        lHist.SetNameTitle("uds",getbrText(brName))
        lHist.Write()
        lepHist.SetNameTitle("lep",getbrText(brName))
        lepHist.Write()
            
        histoMC.SetNameTitle("MCSum",getbrText(brName))
        histoMC.Write()
        if not dataset=="":
            histoD.SetNameTitle("Data",getbrText(brName))
            histoD.Write()
        # myStack.SetNameTitle("MCStack",getbrText(brName))
        # myStack.Write()
        #histoSig=finalHists[sampleNamesSet[-1]]
        #histoSig.SetNameTitle("MCSig",getbrText(brName))
        #histoSig.Write()
        #histoBkg.SetNameTitle("MCBkg",getbrText(brName))
        #histoBkg.Write()

        if getSFUnc:
            for ib in range(nbins+2):
                uncsum2 = 0.
                for thiskey in SFBinCounts[ib]:
                    statUnc = thiskey[2]-thiskey[1]
                    wtsum = 0
                    for flName in SFBinCounts[ib][thiskey]:
                        normfactor = normFactors[histsToFlMap.index(flName)]
                        wtsum += normfactor*SFBinCounts[ib][thiskey][flName]
                    uncsum2 += (wtsum*statUnc)**2
                    if ib == 18: print wtsum,statUnc
                SFUnc.SetBinContent(ib,uncsum2**0.5)
            SFUnc.SetNameTitle("SFUnc",getbrText(brName))
            SFUnc.Write()

        outROOT.Close()
        print rootName, "created."
    
    if makeBinWtTxt:
        binTxtName = outDir+saveName+".txt"
        with open(binTxtName,'w') as binFile:
            binFile.write("normFact = ")
            binFile.write(str(json.dumps(normFactByFl, indent=4, sort_keys=True)))
            binFile.write("\n\n")
            binFile.write("binWtDict = ")
            binFile.write(str(json.dumps(binWtTxtFileDict, indent=4, sort_keys=True)))
            
        print "Written %s."%binTxtName

    if not doCombine:
        if dataset=="":
            return finalHists
        else:
            return finalHists, histoD

if __name__ == "__main__":
    if len(sys.argv)>1: testMode=True
#    plotStack("jetMu_Pt",r"p^{#mu}_{T} [GeV] (mu)",15,0,25,selections=["is_M"],cuts=[[1,1]],dataset="smu",makeROOT=True,noRatio=True)
    #plotStack("jet_CvsL[muJet_idx]","CvsL",5,0,1,selections=["is_M"],dataset="smu",brName2D=["jet_CvsB","muJet_idx"], brLabel2="CvsB",nbins2=5,start2=0,end2=1,drawStyle="",makeROOT=True)
    plotStack("jet_CvsL[muJet_idx]",r"Jet CvsL (#mu)",30,-0.2,1,        \
        selections = "is_M ==1 && jetMuPt_by_jetPt < 0.4 && M_RelIso[0] < 0.05 && (hardMu_Jet_PtRatio > 0.75 || hardMu_Jet_PtRatio < 0.) && abs(M_dz[0]) < 0.01 && abs(M_dxy[0]) < 0.002 && M_sip3d[0] < 2 && jet_nJet <= 3 && diLepVeto == 0 && (Z_Mass_best < 80 || Z_Mass_best > 100) && (Z_Mass_min > 12 || Z_Mass_min < 0) && jet_muplusneEmEF[muJet_idx] < 0.7 && jetMu_iso > 0.5",  \
            dataset="smu",makeROOT=True)
