from ROOT import *
import sys
from plotTools import plotSFs
sys.path.append('../SFExtractor')
gROOT.SetBatch(1)
gStyle.SetOptStat(0)
gStyle.SetPaintTextFormat("4.3f")

file1 = "data/Plots_190928_2017_incl_191125_NoTempRemodel_puritythreshold/Plots_190928_2017_incl/DeepCSV_ctagSF_MiniAOD94X_2017_pTincl.root"
file2 = "data/Plots_200120_2017PULoose/ctagSF_2017_Spandan_CvsL_.root"
outdir = "data/Plots_200120_2017PULoose/"

root1 = TFile.Open(file1,"READ")
root2 = TFile.Open(file2,"READ")

for flav in ["SFc_hist","SFb_hist","SFl_hist"]:
    SF1 = root1.Get(flav)
    SF2 = root2.Get(flav)

    SF1up = root1.Get(flav+"_TotalUncUp")
    SF1down = root1.Get(flav+"_TotalUncDown")

    SF2up = root2.Get(flav+"_TotalUncUp")
    SF2down = root2.Get(flav+"_TotalUncDown")

    histdiff = SF1.Clone()
    histdiff2 = SF1.Clone()

    for binx in range(0,SF1.GetNbinsX()+1):
        for biny in range(0,SF1.GetNbinsY()+1):
            if (binx == 0 and biny != 0) or (binx != 0 and biny == 0): continue
            diff = SF2.GetBinContent(binx,biny)-SF1.GetBinContent(binx,biny)
            errup = SF1up.GetBinContent(binx,biny)
            errdown = SF1down.GetBinContent(binx,biny)
            errup2 = SF2up.GetBinContent(binx,biny)
            errdown2 = SF2down.GetBinContent(binx,biny)
            #err2 = max(abs(SF2up.GetBinContent(binx,biny)-SF2.GetBinContent(binx,biny)),abs(SF2down.GetBinContent(binx,biny)-SF2.GetBinContent(binx,biny)))
             
            if diff >= 0:
                if errup==0:
                    histdiff.SetBinContent(binx,biny,0)
                else:
                    histdiff.SetBinContent(binx,biny,diff/max(errup,errdown2))
            else:
                if errdown==0:
                    histdiff.SetBinContent(binx,biny,0)
                else:
                    histdiff.SetBinContent(binx,biny,diff/max(errdown,errup2))
            #histdiff.GetZaxis().SetRangeUser(-2,2.)
            
            
            if errup == 0. or errdown == 0.:
                histdiff2.SetBinContent(binx,biny,0)
            else:
                histdiff2.SetBinContent(binx,biny,max(errup2/errup,errdown2/errdown))
            
    histdiff.SetMaximum(2.)
    histdiff.SetMinimum(-2.)
    histdiff2.SetMaximum(3.)
    histdiff2.SetMinimum(.9)
    plotSFs(histdiff,outdir+"/diff_"+flav+".png",True,noUnc=True,palette=104)
    plotSFs(histdiff2,outdir+"/uncratio_"+flav+".png",True,noUnc=True,palette=89)
