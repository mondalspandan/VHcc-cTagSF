from ROOT import *
import os, sys

gROOT.SetBatch(1)
gStyle.SetOptStat(0)
gStyle.SetPaintTextFormat("4.3f")
gStyle.SetTitleSize(0.03,"t")

SFoldfl = TFile.Open("/home/spandan/MEGA/Work/Vhcc/VHcc-cTagSF/SFExtractor/data/Plots_190306_pt20_Inclusivett/190306_pt20_central/cTag_SFs_80X_Spandan_allsysts.root","READ")
SFnewfl = TFile.Open("/home/spandan/MEGA/Work/Vhcc/VHcc-cTagSF/SFExtractor/data/Plots_190306_pt20_Inclusivett_onlycentral/190306_pt20_central/cTag_SFs_80X_Spandan.root","READ")

for f in ['c','b','l']:
    new = SFnewfl.Get("SF%s_hist_central"%f)

    oldNom = SFoldfl.Get("SF%s_hist_central"%f)
    oldUp = SFoldfl.Get("SF%s_hist_Total_Up"%f)
    oldDown = SFoldfl.Get("SF%s_hist_Total_Down"%f)

    err = new.Clone()
    for i in range(1,err.GetNbinsX()+1):
        for j in range(1,err.GetNbinsY()+1):
            if oldNom.GetBinContent(i,j) == 0: continue
            if (i==1 or j==1) and not (i==1 and j==1):
                err.SetBinContent(i,j,-2)
                continue
            unc = max(abs(oldUp.GetBinContent(i,j)-oldNom.GetBinContent(i,j)),abs(oldDown.GetBinContent(i,j)-oldNom.GetBinContent(i,j)))
            unc = (unc**2 + new.GetBinError(i,j)**2)**0.5
            diff = new.GetBinContent(i,j)-oldNom.GetBinContent(i,j)
#            print diff, unc
            diffinSD = diff/unc
            err.GetZaxis().SetRangeUser(-1.,1.)
            err.SetBinContent(i,j,diffinSD)
            err.SetBinError(i,j,0.)

    canv = TCanvas("c","c",900,800)
    canv.cd()
    gPad.SetMargin(.12,.15,.1,.1)
    err.SetTitle("#frac{SF_{incl}-SF_{lept}}{#sigma} for SF_{%s}"%f)
    err.Draw("col text")
    canv.SaveAs("DiffinSD_%s.png"%f)
