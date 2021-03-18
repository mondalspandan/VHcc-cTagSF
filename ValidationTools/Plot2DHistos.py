from ROOT import *

gROOT.SetBatch(1)
gStyle.SetOptStat(0)
gStyle.SetPaintTextFormat("4.3f")

count = 1
def export(hist,title="",rng=[0,.4]):
    if title == "": title = hist.GetTitle()
    global count
    hist.SetTitle(title)
    hist.SetMarkerSize(1.5)
    hist.GetXaxis().SetTitle("CvsL discriminator")
    hist.GetYaxis().SetTitle("CvsB discriminator")
    hist.GetZaxis().SetRangeUser(rng[0],rng[1])
    canv = TCanvas("c","",900,800)
    gPad.SetMargin(.12,.15,.1,.1)
    hist.Draw("colz text")
    
    canv.SaveAs("out/%d_%s.png"%(count,hist.GetName()))
    count += 1

f = TFile.Open("SoftMuBiasOut_Pt-1--1.root","READ")

bAll2D = f.Get("bAll2D")
bAll2D.Scale(1./bAll2D.Integral())
export(bAll2D,"For all b jets")

bWithMu2D = f.Get("bWithMu2D")
bWithMu2D.Scale(1./bWithMu2D.Integral())
export(bWithMu2D,"For b jets with Soft Muon")

bRatio = bAll2D.Clone()
bRatio.Divide(bWithMu2D)
export(bRatio,"Transfer factor for b (b_{All}/b_{with #mu})",[.5,1.5])

cAll2D = f.Get("cAll2D")
cAll2D.Scale(1./cAll2D.Integral())
export(cAll2D,"For all c jets")

cWithMu2D = f.Get("cWithMu2D")
cWithMu2D.Scale(1./cWithMu2D.Integral())
export(cWithMu2D,"For c jets with Soft Muon")

cRatio = cAll2D.Clone()
cRatio.Divide(cWithMu2D)
export(cRatio,"Transfer factor for c (c_{All}/c_{with #mu})",[.5,1.5])
