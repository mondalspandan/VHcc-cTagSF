from ROOT import *
gROOT.SetBatch(1)
gStyle.SetOptStat(0)
import os,sys

histos=["leptonsCons","realLightCons"]
cols = [kBlue,kRed,kGreen,kYellow]
f = sys.argv[1]

rf = TFile.Open(f,"READ")
canv = TCanvas("c1","c",800,600)
leg = TLegend(.5,.8,.9,.9)

for i, h in enumerate(histos):
#    print h
    hist = rf.Get(h)
    hist.SetLineColor(cols[i])
    hist.SetLineWidth(2)
    hist.Scale(1./hist.Integral())
    leg.AddEntry(hist)
    hist.SetTitle("")
    hist.GetXaxis().SetTitle("# constituents in jets")
    hist.GetYaxis().SetTitle("Normalized")
    hist.Draw("e same")
    
leg.Draw()
canv.SaveAs("%s.png"%histos[0])
