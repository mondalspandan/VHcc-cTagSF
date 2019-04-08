from ROOT import *
from scipy.optimize import minimize
import os
from binning import *
gROOT.SetBatch(1)
gStyle.SetOptStat(0)
gStyle.SetPaintTextFormat("4.3f")


SFFile1 = "data/Plots_190306_pt20_semileptonic/190306_pt20_central/cTag_SFs_80X_Spandan_allsysts.root"
SFFile2 = "data/Plots_190306_pt20_dileptonic/190306_pt20_central/cTag_SFs_80X_Spandan_allsysts.root"
OutDir = "data/Plots_190306_pt20_SFsCombined/190306_pt20_central/"

skip1bins=True

os.system("mkdir -p "+OutDir)
RFl1 = TFile.Open(SFFile1,"READ")
RFl2 = TFile.Open(SFFile2,"READ")
ROut = TFile.Open(OutDir+"/cTag_SFs_80X_Spandan_allsysts.root","RECREATE")

hList = [i.GetName() for i in list(RFl1.GetListOfKeys())]
for hName in hList:
    if "central" in hName:
        hList.remove(hName)
        hList = [hName]+hList

central_hist_comb={}

Error_Up_1 = {}
Error_Up_2 = {}
Error_Down_1 = {}
Error_Down_2 = {}
combErr_Up = {}
combErr_Down = {}

for f in ['b','c','l']:
    Error_Up_1[f]=RFl1.Get("SF"+f+"_hist_Total_Up")
    Error_Up_2[f]=RFl2.Get("SF"+f+"_hist_Total_Up")
    Error_Down_1[f]=RFl1.Get("SF"+f+"_hist_Total_Down")
    Error_Down_2[f]=RFl2.Get("SF"+f+"_hist_Total_Down")
    
    Error_Up_1[f].SetDirectory(0)
    Error_Up_2[f].SetDirectory(0)
    Error_Down_1[f].SetDirectory(0)
    Error_Down_2[f].SetDirectory(0)
    
    combErr_Up[f] = Error_Up_1[f].Clone()
    combErr_Down[f] = Error_Down_1[f].Clone()
    for binx in range(0,combErr_Up[f].GetNbinsX()+1):
        for biny in range(0,combErr_Up[f].GetNbinsY()+1):
            combErr_Up[f].SetBinContent(binx,biny,0.)
            combErr_Down[f].SetBinContent(binx,biny,0.)



for hName in hList:
    if "_Total_" in hName: continue
    
    SF_1 = RFl1.Get(hName)
    SF_2 = RFl2.Get(hName)
    SF_1.SetDirectory(0)
    SF_2.SetDirectory(0)
    outSF = SF_1.Clone()
    
    for binx in range(0,SF_1.GetNbinsX()+1):
        for biny in range(0,SF_1.GetNbinsY()+1):
            x1=SF_1.GetBinContent(binx,biny)
            x2=SF_2.GetBinContent(binx,biny)
            e1=max( abs(Error_Up_1[hName[2]].GetBinContent(binx,biny)-x1) , abs(Error_Down_1[hName[2]].GetBinContent(binx,biny)-x1) )
            e2=max( abs(Error_Up_2[hName[2]].GetBinContent(binx,biny)-x2) , abs(Error_Down_2[hName[2]].GetBinContent(binx,biny)-x2) )
            if e1==0 or e2==0:
                print e1, e2, hName, binx, biny
            
            def chi2(val):
                return ((x1-val)/e1)**2+((x2-val)/e2)**2
            
            combVal = minimize(chi2,1.).x
            outSF.SetBinContent(binx,biny,combVal)
            
    ROut.cd()
    outSF.Write()
    
    if "central" in hName:
        central_hist_comb[hName[2]]=outSF.Clone()
    else:
        for binx in range(0,SF_1.GetNbinsX()+1):
            for biny in range(0,SF_1.GetNbinsY()+1):
                diff = outSF.GetBinContent(binx,biny) - central_hist_comb[hName[2]].GetBinContent(binx,biny)                
                if diff > 0:
                    olderr = combErr_Up[hName[2]].GetBinContent(binx,biny)
                    newerr = olderr**2+diff**2
                    combErr_Up[hName[2]].SetBinContent(binx,biny,newerr**0.5)
                elif diff < 0:
                    olderr = combErr_Down[hName[2]].GetBinContent(binx,biny)
                    newerr = olderr**2+diff**2
                    combErr_Down[hName[2]].SetBinContent(binx,biny,newerr**0.5)

def remove1bins(hist):    
    for binx in range(hist.GetNbinsX()):
        for biny in range(hist.GetNbinsY()):
            if (binx==0 or biny==0) and not (binx==0 and biny==0):
                hist.SetBinContent(binx+1,biny+1,0.)
                hist.SetBinError(binx+1,biny+1,0.)
    return hist
    
def saveHist(hist,outName):
    if skip1bins:
        hist=remove1bins(hist)
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
    hist.GetZaxis().CenterTitle()
    hist.GetZaxis().SetTitleSize(0.05)
    hist.GetZaxis().SetTitleOffset(1.2)
    hist.Draw("COLZ TEXT E")
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
    c.SaveAs(OutDir+"/"+outName+".png")

central_with_unc = {}
relErr_Up = {}
relErr_Down = {}
for f in ['b','c','l']:
    central_with_unc[f] = central_hist_comb[f].Clone()
    for binx in range(0,central_with_unc[f].GetNbinsX()+1):
        for biny in range(0,central_with_unc[f].GetNbinsY()+1):
            central_with_unc[f].SetBinError(binx,biny,max(combErr_Up[f].GetBinContent(binx,biny),combErr_Down[f].GetBinContent(binx,biny)))
    saveHist(central_with_unc[f],"Unc_SF"+f+"_cTag")
    
    relErr_Up[f] = combErr_Up[f].Clone()
    combErr_Up[f].Add(central_hist_comb[f])
    combErr_Up[f].Write()
    relErr_Down[f] = combErr_Down[f].Clone()
    combErr_Down[f].Add(central_hist_comb[f],-1)
    combErr_Down[f].Scale(-1)
    combErr_Down[f].Write()
    


# Plot the up and down uncertainty values
max_value = 2
SFb_histUp=relErr_Up['b']
SFc_histUp=relErr_Up['c']
SFl_histUp=relErr_Up['l']
SFb_histDown=relErr_Down['b']
SFc_histDown=relErr_Down['c']
SFl_histDown=relErr_Down['l']

if skip1bins:
    SFb_histUp=remove1bins(SFb_histUp)
    SFb_histDown=remove1bins(SFb_histDown)
    SFc_histUp=remove1bins(SFc_histUp)
    SFc_histDown=remove1bins(SFc_histDown)
    SFl_histUp=remove1bins(SFl_histUp)
    SFl_histDown=remove1bins(SFl_histDown)

cSFb = TCanvas("cSFb","cSFb",1800,1200)
cSFb.Divide(3,2)
cSFb.cd(2)
gPad.SetMargin(0.15,0.2,0.15,0.1)
SFb_histUp.SetMarkerSize(1.5)
SFb_histUp.SetMarkerColor(0)
SFb_histUp.GetXaxis().CenterTitle()
SFb_histUp.GetXaxis().SetTitleSize(0.05)
SFb_histUp.GetXaxis().SetTitleOffset(1.2)
SFb_histUp.GetYaxis().CenterTitle()
SFb_histUp.GetYaxis().SetTitleSize(0.05)
SFb_histUp.GetYaxis().SetTitleOffset(1.2)
SFb_histUp.GetZaxis().SetRangeUser(0.,max_value)
SFb_histUp.GetZaxis().CenterTitle()
SFb_histUp.GetZaxis().SetTitleSize(0.05)
SFb_histUp.GetZaxis().SetTitleOffset(1.2)
SFb_histUp.Draw("COLZ TEXT")
latex_cms = TLatex()
latex_cms.SetTextFont(42)
latex_cms.SetTextSize(0.048)
latex_cms.SetTextAlign(11)
latex_cms.DrawLatexNDC(0.15,0.92,"#bf{CMS} #it{Preliminary}")
latex_cms.DrawLatexNDC(0.56,0.92,"35.9 fb^{-1} (13 TeV)")
cSFb.cd(1)
gPad.SetMargin(0.15,0.2,0.15,0.1)
SFc_histUp.SetMarkerSize(1.5)
SFc_histUp.SetMarkerColor(0)
SFc_histUp.GetXaxis().CenterTitle()
SFc_histUp.GetXaxis().SetTitleSize(0.05)
SFc_histUp.GetXaxis().SetTitleOffset(1.2)
SFc_histUp.GetYaxis().CenterTitle()
SFc_histUp.GetYaxis().SetTitleSize(0.05)
SFc_histUp.GetYaxis().SetTitleOffset(1.2)
SFc_histUp.GetZaxis().SetRangeUser(0.,max_value)
SFc_histUp.GetZaxis().CenterTitle()
SFc_histUp.GetZaxis().SetTitleSize(0.05)
SFc_histUp.GetZaxis().SetTitleOffset(1.2)
SFc_histUp.Draw("COLZ TEXT")
latex_cms.DrawLatexNDC(0.15,0.92,"#bf{CMS} #it{Preliminary}")
latex_cms.DrawLatexNDC(0.56,0.92,"35.9 fb^{-1} (13 TeV)")
cSFb.cd(3)
gPad.SetMargin(0.15,0.2,0.15,0.1)
SFl_histUp.SetMarkerSize(1.5)
SFl_histUp.SetMarkerColor(0)
SFl_histUp.GetXaxis().CenterTitle()
SFl_histUp.GetXaxis().SetTitleSize(0.05)
SFl_histUp.GetXaxis().SetTitleOffset(1.2)
SFl_histUp.GetYaxis().CenterTitle()
SFl_histUp.GetYaxis().SetTitleSize(0.05)
SFl_histUp.GetYaxis().SetTitleOffset(1.2)
SFl_histUp.GetZaxis().SetRangeUser(0.,max_value)
SFl_histUp.GetZaxis().CenterTitle()
SFl_histUp.GetZaxis().SetTitleSize(0.05)
SFl_histUp.GetZaxis().SetTitleOffset(1.2)
SFl_histUp.Draw("COLZ TEXT")
latex_cms.DrawLatexNDC(0.15,0.92,"#bf{CMS} #it{Preliminary}")
latex_cms.DrawLatexNDC(0.56,0.92,"35.9 fb^{-1} (13 TeV)")
cSFb.cd(5)
gPad.SetMargin(0.15,0.2,0.15,0.1)
SFb_histDown.SetMarkerSize(1.5)
SFb_histDown.SetMarkerColor(0)
SFb_histDown.GetXaxis().CenterTitle()
SFb_histDown.GetXaxis().SetTitleSize(0.05)
SFb_histDown.GetXaxis().SetTitleOffset(1.2)
SFb_histDown.GetYaxis().CenterTitle()
SFb_histDown.GetYaxis().SetTitleSize(0.05)
SFb_histDown.GetYaxis().SetTitleOffset(1.2)
SFb_histDown.GetZaxis().SetRangeUser(0.,max_value)
SFb_histDown.GetZaxis().CenterTitle()
SFb_histDown.GetZaxis().SetTitleSize(0.05)
SFb_histDown.GetZaxis().SetTitleOffset(1.2)
SFb_histDown.Draw("COLZ TEXT")
latex_cms.DrawLatexNDC(0.15,0.92,"#bf{CMS} #it{Preliminary}")
latex_cms.DrawLatexNDC(0.56,0.92,"35.9 fb^{-1} (13 TeV)")
cSFb.cd(4)
gPad.SetMargin(0.15,0.2,0.15,0.1)
SFc_histDown.SetMarkerSize(1.5)
SFc_histDown.SetMarkerColor(0)
SFc_histDown.GetXaxis().CenterTitle()
SFc_histDown.GetXaxis().SetTitleSize(0.05)
SFc_histDown.GetXaxis().SetTitleOffset(1.2)
SFc_histDown.GetYaxis().CenterTitle()
SFc_histDown.GetYaxis().SetTitleSize(0.05)
SFc_histDown.GetYaxis().SetTitleOffset(1.2)
SFc_histDown.GetZaxis().SetRangeUser(0.,max_value)
SFc_histDown.GetZaxis().CenterTitle()
SFc_histDown.GetZaxis().SetTitleSize(0.05)
SFc_histDown.GetZaxis().SetTitleOffset(1.2)
SFc_histDown.Draw("COLZ TEXT")
latex_cms.DrawLatexNDC(0.15,0.92,"#bf{CMS} #it{Preliminary}")
latex_cms.DrawLatexNDC(0.56,0.92,"35.9 fb^{-1} (13 TeV)")
cSFb.cd(6)
gPad.SetMargin(0.15,0.2,0.15,0.1)
SFl_histDown.SetMarkerSize(1.5)
SFl_histDown.SetMarkerColor(0)
SFl_histDown.GetXaxis().CenterTitle()
SFl_histDown.GetXaxis().SetTitleSize(0.05)
SFl_histDown.GetXaxis().SetTitleOffset(1.2)
SFl_histDown.GetYaxis().CenterTitle()
SFl_histDown.GetYaxis().SetTitleSize(0.05)
SFl_histDown.GetYaxis().SetTitleOffset(1.2)
SFl_histDown.GetZaxis().SetRangeUser(0.,max_value)
SFl_histDown.GetZaxis().CenterTitle()
SFl_histDown.GetZaxis().SetTitleSize(0.05)
SFl_histDown.GetZaxis().SetTitleOffset(1.2)
SFl_histDown.Draw("COLZ TEXT")
latex_cms.DrawLatexNDC(0.15,0.92,"#bf{CMS} #it{Preliminary}")
latex_cms.DrawLatexNDC(0.56,0.92,"35.9 fb^{-1} (13 TeV)")
cSFb.SaveAs(OutDir+"/SFs_cTag_UpDown_relative.png")

