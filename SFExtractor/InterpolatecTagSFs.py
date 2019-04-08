import ROOT
import os
import sys
from argparse import ArgumentParser
from math import sqrt
import numpy as np
#from scipy.optimize import fmin,fminbound,minimize,brentq,ridder,fsolve
from binning import *
from array import array
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import interpolate
from scipy.interpolate import RectBivariateSpline

skip1bins=True

ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPaintTextFormat("4.3f")

parser = ArgumentParser()
parser.add_argument('--indir', default="FILL",help='input directory that contains all the Histograms with syst variations')
#parser.add_argument('--ApplyBiasUnc', action='store_true', help='Apply the bias Unc')
args = parser.parse_args()

basedir = args.indir
subdirs = [i for i in os.listdir(basedir) if os.path.isdir(basedir+"/"+i)]
centraldir = [i for i in subdirs if "central" in i][0]
systdirs = [i for i in subdirs if not "central" in i and not "Bias" in i]
biasdirs = [i for i in subdirs if "Bias" in i]

if skip1bins:
    custom_bins_CvsL_jet1 = custom_bins_CvsL_jet1[1:]
    custom_bins_CvsB_jet1 = custom_bins_CvsB_jet1[1:]

x = custom_bins_CvsL_jet1
x = [x[idx] + (x[idx+1]-x[idx])/2. for idx in range(len(x)-1)] #Get bin centers
y = custom_bins_CvsB_jet1
y = [y[idx] + (y[idx+1]-y[idx])/2. for idx in range(len(y)-1)]
X, Y = np.meshgrid(x, y, copy=False)
print X,Y
Z = X**2 + Y**2 #Just dummy as container!!
#print Z

central_SF_file = ROOT.TFile(basedir+"/"+centraldir+"/cTag_SFs_80X_Spandan_allsysts.root","READ")
histos_names = [i.GetName() for i in central_SF_file.GetListOfKeys()]
print histos_names

smoothed_SF_file = ROOT.TFile(basedir+"/"+centraldir+"/cTag_SFs_80X_Spandan_smooth.root","RECREATE")


results_dict = {
    "central":{"SFb":{},"SFc":{},"SFl":{}},
    "Up": {"SFb":{},"SFc":{},"SFl":{}},
    "Down":{"SFb":{},"SFc":{},"SFl":{}}
}

for hist_name in histos_names:
    print hist_name
    #if not("central" in hist_name or "_Down" in hist_name or "_Up" in hist_name): continue
    flav = hist_name.split("_")[0]
    syst = hist_name.split("_")[2:]
    central_SF_file.cd()
    hist_ = central_SF_file.Get(hist_name)
    for binx in range(hist_.GetNbinsX()):
        for biny in range(hist_.GetNbinsY()):
            correction=0
            if skip1bins:
                correction=1
                if (binx==0 or biny==0): continue
            Z[binx-correction][biny-correction] = hist_.GetBinContent(binx+1,biny+1)
    #print Z
    X_ = X.flatten()
    Y_ = Y.flatten()

    f = RectBivariateSpline(x, y, Z, kx=1, ky=1) # Linear Interpolation
#    f = RectBivariateSpline(x, y, Z, kx=2, ky=2) # Quadratic Interpolation
#    f = RectBivariateSpline(x, y, Z, kx=3, ky=3) # Cubic Interpolation

    min_ = -.2
    if skip1bins: min_=0.
    max_ = 1
    bins_ = 60
    #xx = np.arange(0,1,0.05)
    xx = np.arange(min_,1.+(max_-min_)/float(bins_),(max_-min_)/float(bins_))
    #print "-->",xx
    xxx = np.asarray([i+((max_-min_)/float(2*bins_)) for i in xx])
    #print "-->",xx
    #yy = np.arange(0,1,0.05)
    yy = np.arange(min_,1.+(max_-min_)/float(bins_),(max_-min_)/float(bins_))
    yyy = np.asarray([i+((max_-min_)/float(2*bins_)) for i in yy])
    zz = f(xxx,yyy)
    
    
    outhist = ROOT.TH2D(hist_name,"",len(xx),min(xx),max(xx),len(yy),min(yy),max(yy))
    for binx,row in enumerate(zz):
        for biny,entry in enumerate(row):
            #print binx+1,biny+1,entry
            if entry< 0: entry = 0.001
            outhist.SetBinContent(binx+1,biny+1,entry)
    
    if skip1bins:
        outhist.SetBinContent(0,0,hist_.GetBinContent(1,1))
        for binx,row in enumerate(zz):
            outhist.SetBinContent(binx+1,0,hist_.GetBinContent(1,1))
        for biny,entry in enumerate(row):
            outhist.SetBinContent(0,biny+1,hist_.GetBinContent(1,1))                
    
    smoothed_SF_file.cd()
    outhist.Write()
    
    if "central" in hist_name:
    
        cSFb = ROOT.TCanvas("cSFb","cSFb",600,600)
        ROOT.gPad.SetMargin(0.13,0.18,0.11,0.17)
        outhist.SetMarkerSize(1.5)
        outhist.GetXaxis().CenterTitle()
        outhist.GetXaxis().SetTitleSize(0.05)
        outhist.GetXaxis().SetTitleOffset(1.)
        outhist.GetYaxis().CenterTitle()
        outhist.GetYaxis().SetTitleSize(0.05)
        outhist.GetYaxis().SetTitleOffset(1.2)
        outhist.GetZaxis().SetRangeUser(0.,2)
        outhist.GetZaxis().CenterTitle()
        outhist.GetZaxis().SetTitleSize(0.05)
        outhist.GetZaxis().SetTitleOffset(1.2)
        outhist.Draw("COLZ")
        if "SFb" in hist_name:
            outhist.SetTitle(";CvsL discriminator;CvsB discriminator;SF_{b}")
        elif "SFc" in hist_name:
            outhist.SetTitle(";CvsL discriminator;CvsB discriminator;SF_{c}")
        elif "SFl" in hist_name:
            outhist.SetTitle(";CvsL discriminator;CvsB discriminator;SF_{light}")
        hist_.Draw("same")
        box = ROOT.TPaveText(min_,1,1,1+.15*(max_-min_))
        box.SetBorderSize(1)
        box.SetFillStyle(0)
        box.Draw("same")
        latex_cms = ROOT.TLatex()
        latex_cms.SetTextFont(42)
        latex_cms.SetTextSize(0.04)
        latex_cms.SetTextAlign(11)
        latex_cms.DrawLatexNDC(0.15,0.9,"#bf{CMS} #it{Preliminary}")
        latex_cms.DrawLatexNDC(0.15,0.85,"W+c/TTb/DYl selection")
        latex_cms.DrawLatexNDC(0.65,0.9,"DeepCSV")
        latex_cms.DrawLatexNDC(0.67,0.85,"c-tagger")
        latex_cms.DrawLatexNDC(0.6,0.95,"35.9 fb^{-1} (13 TeV)")
        line3 = ROOT.TLine()
        line3.SetLineColor(ROOT.kGray+2)
        line3.SetLineStyle(2)
        line3.SetLineWidth(1)
        for border in custom_bins_CvsL_jet1[1:-1]:
            line3.DrawLine(border, 0, border, 1)
        for border in custom_bins_CvsB_jet1[1:-1]:
            line3.DrawLine(0, border, 1, border)
        cSFb.SaveAs(basedir+"/"+centraldir+"/"+flav+"_cTag_smooth.png")
#        cSFb.SaveAs(basedir+"/"+centraldir+"/"+flav+"_cTag_smooth.pdf")
#        cSFb.SaveAs(basedir+"/"+centraldir+"/"+flav+"_cTag_smooth.C")
    
    
    
        # c = ROOT.TCanvas("c"+flav,"c"+flav,800,600)
#         outhist.Draw("colz")
#         hist_.Draw("same text")
#         outhist.GetZaxis().SetRangeUser(0,2)
#     
#         c.SaveAs("testing_smoothing_"+flav+".pdf") 
    

smoothed_SF_file.Close()
central_SF_file.Close()
   
    
       
#     results_dict[syst][flav]["values"] = Z
#     results_dict[syst][flav]["smooth"] = ZZ
#     
#     # fig = plt.figure()
# #     ax = fig.add_subplot(111, projection='3d')
# #     ax.plot_surface(XX, YY, ZZ, rstride=1, cstride=1, alpha=0.3)
# #     ax.scatter(X, Y, Z, c='r')
# #     plt.xlabel('X')
# #     plt.ylabel('Y')
# #     plt.show()
# #     plt.clf()
# 
# for fl in ["SFb","SFc","SFl"]:
#     print fl 
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     ax.plot_surface(XX, YY, results_dict["Up"][fl]["smooth"], rstride=1, cstride=1, alpha=0.3)
#     ax.plot_surface(XX, YY, results_dict["Down"][fl]["smooth"], rstride=1, cstride=1, alpha=0.3)
#     ax.scatter(X, Y, results_dict["central"][fl]["values"], c='r')
#     #ax.scatter(X, Y, results_dict["Up"][fl]["values"], c='g')
#     #ax.scatter(X, Y, results_dict["Down"][fl]["values"], c='b')
#     plt.xlabel('X')
#     plt.ylabel('Y')
#     plt.show()
#   
#     plt.clf()


                
