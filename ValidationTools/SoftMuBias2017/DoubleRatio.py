import os, sys
from ROOT import TFile, TCanvas, TLine, kRed, TLegend, gStyle, kBlack
gStyle.SetLegendBorderSize(0)
withmudir = "../data/191205_2017_central_2017_pTincl/"
nomudir = "../data/201015_softMu_central_2017_pTincl_v2/"

discname = "DeepCSV"
if "DeepFlav" in nomudir: discname = "DeepJet"

withmufiles = [i for i in os.listdir(withmudir) if i.startswith("TT_semi") and i.endswith(".root")]
nomufiles = [i for i in os.listdir(nomudir) if i.startswith("TT_semi") and "syst" not in i and i.endswith(".root")]

for disc in ["CvsL","CvsB"]:
    legend = TLegend(0.35, 0.75, 0.85, 0.90,"") #,"brNDC"
    legend.SetFillStyle(0)
    legend.SetTextSize(0.035)

    wmuMC = []
    wmuData = []
    nmuMC = []
    nmuData = []
    for wmu in withmufiles:
        if disc not in wmu: continue
        rfl = TFile.Open(withmudir+wmu,"READ")
        MC = rfl.Get("MCSum")
        D = rfl.Get("Data")
        MC.SetDirectory(0)
        D.SetDirectory(0)
        rfl.Close()
        
        if wmuMC == []:
            wmuMC = MC.Clone()
            wmuData = D.Clone()
        else:
            wmuMC.Add(MC)
            wmuData.Add(D)
    for nmu in nomufiles:
        if disc not in nmu: continue
        rfl = TFile.Open(nomudir+nmu)
        MC = rfl.Get("MCSum")
        D = rfl.Get("Data")
        MC.SetDirectory(0)
        D.SetDirectory(0)
        rfl.Close()
        if nmuMC == []:
            nmuMC = MC.Clone()
            nmuData = D.Clone()
        else:
            nmuMC.Add(MC)
            nmuData.Add(D)

    normwmu = wmuData.Integral()/wmuMC.Integral()
    normnmu = nmuData.Integral()/nmuMC.Integral()
    doublenorm = normwmu/normnmu
    wmuRatio = wmuData.Clone()
    wmuRatio.Divide(wmuMC)
    nmuRatio = nmuData.Clone()
    nmuRatio.Divide(nmuMC)
    DoubleRatio = wmuRatio.Clone()
    DoubleRatio.Divide(nmuRatio)
    DoubleRatio.GetXaxis().SetTitle(discname+" "+disc)
    DoubleRatio.GetYaxis().SetTitle("Ratio")

    wmuRatio.SetLineColor(30)
    wmuRatio.SetMarkerColor(30)
    wmuRatio.SetMarkerStyle(34)

    nmuRatio.SetLineColor(45)
    nmuRatio.SetMarkerColor(45)
    nmuRatio.SetMarkerStyle(47)

    c = TCanvas("c","c",800,800)
    DoubleRatio.Draw("le")
    wmuRatio.Draw("p e same")
    nmuRatio.Draw("p e same")
    DoubleRatio.SetMinimum(0.6)
    DoubleRatio.SetMaximum(1.4)
    DoubleRatio.SetTitle("Double Ratio: "+disc) 

    lines = []
    def drawHline(yval,col):
        lines.append(TLine(-0.2,yval,1,yval))
        lines[-1].SetLineColor(col)
        lines[-1].SetLineWidth(2)
        lines[-1].Draw()

    drawHline(1,kRed)
    drawHline(normwmu,30)
    drawHline(normnmu,45)
    drawHline(doublenorm,kBlack)

    legend.AddEntry(wmuRatio,"Data/MC Ratio with soft muon")
    legend.AddEntry(nmuRatio,"Data/MC Ratio without soft muon")    
    legend.AddEntry(DoubleRatio,"Double Ratio (#frac{with}{without})")

    legend.Draw()
    c.SetTicky(1)
    c.SetLeftMargin(0.1)
    c.SetRightMargin(0.1)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetGridy()
    c.SaveAs("DoubleRatio%s.png"%disc)