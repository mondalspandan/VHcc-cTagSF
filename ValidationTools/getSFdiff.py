from ROOT import *
import sys
sys.path.append('../SFExtractor')
from binning import *
gROOT.SetBatch(1)
gStyle.SetOptStat(0)
gStyle.SetPaintTextFormat("4.3f")

file1 = "../SFExtractor/data/Plots_190306_pt20_dileptonic/190306_pt20_central/cTag_SFs_80X_Spandan_allsysts.root"
file2 = "../SFExtractor/data/Plots_190306_pt20_semileptonic/190306_pt20_central/cTag_SFs_80X_Spandan_allsysts.root"

root1 = TFile.Open(file1,"READ")
root2 = TFile.Open(file2,"READ")

SF1 = root1.Get("SFb_hist_central")
SF2 = root2.Get("SFb_hist_central")

SF1up = root1.Get("SFb_hist_Total_Up")
SF1down = root1.Get("SFb_hist_Total_Down")

SF2up = root2.Get("SFb_hist_Total_Up")
SF2down = root2.Get("SFb_hist_Total_Down")

histdiff = SF1.Clone()
histdiff2 = SF1.Clone()

for binx in range(1,SF1.GetNbinsX()+1):
    for biny in range(1,SF1.GetNbinsY()+1):
        diff = abs(SF1.GetBinContent(binx,biny)-SF2.GetBinContent(binx,biny))
        err1 = max(abs(SF1up.GetBinContent(binx,biny)-SF1.GetBinContent(binx,biny)),abs(SF1down.GetBinContent(binx,biny)-SF1.GetBinContent(binx,biny)))
        err2 = max(abs(SF2up.GetBinContent(binx,biny)-SF2.GetBinContent(binx,biny)),abs(SF2down.GetBinContent(binx,biny)-SF2.GetBinContent(binx,biny)))
        if err1==0 or err2==0:
            histdiff.SetBinContent(binx,biny,0)
            histdiff2.SetBinContent(binx,biny,0)
        else:
            histdiff.SetBinContent(binx,biny,diff/err1)
            histdiff2.SetBinContent(binx,biny,diff/err2)
        
def saveHist(hist,outName,denname):
    c = TCanvas("c","c",1200,1200)
    gPad.SetMargin(0.13,0.18,0.11,0.17)
    hist.SetMarkerSize(1.5)
    hist.GetXaxis().CenterTitle()
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.)
    hist.GetYaxis().CenterTitle()
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleOffset(1.2)
#        hist.GetZaxis().SetRangeUser(1e-14,1e-7)
    hist.GetZaxis().SetTitle(r"#frac{|SF_{b}^{Dilept}-SF_{b}^{Semilept}|}{#epsilon^{"+denname+"}_{b}}")
    hist.GetZaxis().CenterTitle()
    hist.GetZaxis().SetTitleSize(0.025)
    hist.GetZaxis().SetTitleOffset(2.2)
    hist.Draw("COLZ TEXT")
    box = TPaveText(custom_bins_CvsB_jet1[0],1,1,1+.15*(custom_bins_CvsB_jet1[-1]-custom_bins_CvsB_jet1[0]))
    box.SetBorderSize(1)
    box.SetFillStyle(0)
    box.Draw("same")
    latex_cms = TLatex()
    latex_cms.SetTextFont(42)
    latex_cms.SetTextSize(0.04)
    latex_cms.SetTextAlign(11)
    latex_cms.DrawLatexNDC(0.15,0.9,"#bf{CMS} #it{Preliminary}")
    latex_cms.DrawLatexNDC(0.15,0.85,"Wc/TTb/DYl selection")
    latex_cms.DrawLatexNDC(0.65,0.9,"DeepCSV")
    latex_cms.DrawLatexNDC(0.67,0.85,"c-tagger")
    latex_cms.DrawLatexNDC(0.6,0.95,"35.9 fb^{-1} (13 TeV)")
    c.SaveAs("SFdiff_"+outName+".png")
    
saveHist(histdiff,"di_in_din","Dilept")
saveHist(histdiff2,"semi_in_din","Semilept")
