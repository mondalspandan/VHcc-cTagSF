####################################################
#   Extract c-tagging Scale Factors through Iterative Fit
#   Original code by Seth Moortgat (VUB Brussels),
#   for ttcc: https://github.com/smoortga/ttcc
#   Adapted for VHcc by Spandan Mondal (RWTH Aachen)
####################################################

import ROOT
import os
import sys
from argparse import ArgumentParser
from math import sqrt
import pickle
import numpy as np
from scipy.optimize import fmin,fminbound,minimize,brentq,ridder,fsolve
from copy import deepcopy
from binning import *
from array import array
from tabulate import tabulate
from matplotlib import pyplot as plt
from PIL import Image

skip1bins=True

ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)

parser = ArgumentParser()
parser.add_argument('--indir', default="190129_Systs",help='input directory that contains all the Histograms with syst variations')
parser.add_argument('--ApplyBiasUnc', action='store_true', help='Apply the bias Unc')
args = parser.parse_args()

basedir = args.indir
subdirs = [i for i in os.listdir(basedir) if os.path.isdir(basedir+"/"+i)]
centraldir = [i for i in subdirs if "central" in i][0]
systdirs = [i for i in subdirs if not "central" in i and not "Bias" in i]
biasdirs = [i for i in subdirs if "Bias" in i]


SFb_histUp = ROOT.TH2D("SFb_hist_Total_Up",";CvsL discriminator;CvsB discriminator;| SF_{b}^{central} - SF_{b}^{up} |",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
SFc_histUp = ROOT.TH2D("SFc_hist_Total_Up",";CvsL discriminator;CvsB discriminator;| SF_{c}^{central} - SF_{c}^{up} |",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2))
SFl_histUp = ROOT.TH2D("SFl_hist_Total_Up",";CvsL discriminator;CvsB discriminator;| SF_{l}^{central} - SF_{l}^{up} |",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3))
SFb_histDown = ROOT.TH2D("SFb_hist_Total_Down",";CvsL discriminator;CvsB discriminator;| SF_{b}^{central} - SF_{b}^{down}|",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
SFc_histDown = ROOT.TH2D("SFc_hist_Total_Down",";CvsL discriminator;CvsB discriminator;| SF_{c}^{central} - SF_{c}^{down}|",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2))
SFl_histDown = ROOT.TH2D("SFl_hist_Total_Down",";CvsL discriminator;CvsB discriminator;| SF_{l}^{central} - SF_{l}^{down}|",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3))

central_SF_file = ROOT.TFile(basedir+"/"+centraldir+"/cTag_SFs_80X_Spandan.root","update")
hList = [i.GetName() for i in list(central_SF_file.GetListOfKeys())]
SFb_histCentral = central_SF_file.Get([h for h in hList if h.startswith('SFb')][0])
SFc_histCentral = central_SF_file.Get([h for h in hList if h.startswith('SFc')][0])
SFl_histCentral = central_SF_file.Get([h for h in hList if h.startswith('SFl')][0])
SFb_histCentral.SetDirectory(0)
SFc_histCentral.SetDirectory(0)
SFl_histCentral.SetDirectory(0)
central_SF_file.Close()

central_SF_file = ROOT.TFile(basedir+"/"+centraldir+"/cTag_SFs_80X_Spandan_allsysts.root","RECREATE")

FitUncb = {}
FitUncc = {}
FitUncl = {}

for binx in range(-1,SFb_histUp.GetNbinsX()):
    for biny in range(-1,SFb_histUp.GetNbinsY()):        
        FitUncb[(binx+1,biny+1)] = SFb_histCentral.GetBinError(binx+1,biny+1)
        FitUncc[(binx+1,biny+1)] = SFc_histCentral.GetBinError(binx+1,biny+1)
        FitUncl[(binx+1,biny+1)] = SFl_histCentral.GetBinError(binx+1,biny+1)
        
        SFb_histCentral.SetBinError(binx+1,biny+1,0.)
        SFc_histCentral.SetBinError(binx+1,biny+1,0.)
        SFl_histCentral.SetBinError(binx+1,biny+1,0.)

central_SF_file.cd()
SFb_histCentral.Write()
SFc_histCentral.Write()
SFl_histCentral.Write()

# start with fit uncertainties
for binx in range(-1,SFb_histUp.GetNbinsX()):
    for biny in range(-1,SFb_histUp.GetNbinsY()):
        SFb_histUp.SetBinContent(binx+1,biny+1,FitUncb[(binx+1,biny+1)])
        SFb_histDown.SetBinContent(binx+1,biny+1,FitUncb[(binx+1,biny+1)])
        SFc_histUp.SetBinContent(binx+1,biny+1,FitUncc[(binx+1,biny+1)])
        SFc_histDown.SetBinContent(binx+1,biny+1,FitUncc[(binx+1,biny+1)])
        SFl_histUp.SetBinContent(binx+1,biny+1,FitUncl[(binx+1,biny+1)])
        SFl_histDown.SetBinContent(binx+1,biny+1,FitUncl[(binx+1,biny+1)])


systContrib = {}
totalcount = 0.
diff_histos = {}

binwiseUncCont = {}
binwiseUncCont['b'] = {}
binwiseUncCont['c'] = {}
binwiseUncCont['l'] = {}

for systdir in sorted(systdirs):
    currentdir = basedir + "/" + systdir
    tmp_file_ = ROOT.TFile(currentdir+"/cTag_SFs_80X_Spandan.root")
    hList = [i.GetName() for i in list(tmp_file_.GetListOfKeys())]
    tmp_SFb_hist = tmp_file_.Get([h for h in hList if h.startswith('SFb')][0])
    tmp_SFc_hist = tmp_file_.Get([h for h in hList if h.startswith('SFc')][0])
    tmp_SFl_hist = tmp_file_.Get([h for h in hList if h.startswith('SFl')][0])

    print systdir
    if not 'XSec' in systdir:
        central_SF_file.cd()
        for hist in [tmp_SFb_hist,tmp_SFc_hist,tmp_SFl_hist]:
            writehist = hist.Clone()
            for binx in range(-1,hist.GetNbinsX()):
                for biny in range(-1,hist.GetNbinsY()):                    
                    writehist.SetBinError(binx+1,biny+1,0.)
            writehist.Write()
    tmp_file_.cd()

    diff_SFb = tmp_SFb_hist.Clone()
    diff_SFc = tmp_SFc_hist.Clone()
    diff_SFl = tmp_SFl_hist.Clone()
    
    for binx in range(-1,hist.GetNbinsX()):
        for biny in range(-1,hist.GetNbinsY()):
            diff_SFb.SetBinError(binx+1,biny+1,0.)
            diff_SFc.SetBinError(binx+1,biny+1,0.)
            diff_SFl.SetBinError(binx+1,biny+1,0.)

    diff_SFb.Add(SFb_histCentral,-1)
    diff_SFc.Add(SFc_histCentral,-1)
    diff_SFl.Add(SFl_histCentral,-1)


    diff_histos[systdir] = {}
    diff_histos[systdir]['b'] = diff_SFb.Clone()
    diff_histos[systdir]['c'] = diff_SFc.Clone()
    diff_histos[systdir]['l'] = diff_SFl.Clone()
    diff_histos[systdir]['b'].SetDirectory(0)
    diff_histos[systdir]['c'].SetDirectory(0)
    diff_histos[systdir]['l'].SetDirectory(0)

    upcount = 0.
    downcount = 0.
    
    systname=''.join(systdir.split('_')[2:])
    for flav in ['b','c','l']:
        binwiseUncCont[flav][systname]={}

    for binx in range(-1,diff_SFb.GetNbinsX()):
        for biny in range(-1,diff_SFb.GetNbinsY()):
            
            binwiseUncCont['b'][systname][(binx+1,biny+1)] = abs(diff_SFb.GetBinContent(binx+1,biny+1))
            binwiseUncCont['c'][systname][(binx+1,biny+1)] = abs(diff_SFc.GetBinContent(binx+1,biny+1))
            binwiseUncCont['l'][systname][(binx+1,biny+1)] = abs(diff_SFl.GetBinContent(binx+1,biny+1))

            if diff_SFb.GetBinContent(binx+1,biny+1) > 0:
                old_bin_content_SFbUp = SFb_histUp.GetBinContent(binx+1,biny+1)
                new_bin_content_SFbUp = sqrt(old_bin_content_SFbUp**2 + diff_SFb.GetBinContent(binx+1,biny+1)**2)
                SFb_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFbUp)
                upcount += diff_SFb.GetBinContent(binx+1,biny+1)**2
            elif diff_SFb.GetBinContent(binx+1,biny+1) < 0:
                old_bin_content_SFbDown = SFb_histDown.GetBinContent(binx+1,biny+1)
                new_bin_content_SFbDown = sqrt(old_bin_content_SFbDown**2 + diff_SFb.GetBinContent(binx+1,biny+1)**2)
                SFb_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFbDown)
                downcount += diff_SFb.GetBinContent(binx+1,biny+1)**2

            if diff_SFc.GetBinContent(binx+1,biny+1) > 0:
                old_bin_content_SFcUp = SFc_histUp.GetBinContent(binx+1,biny+1)
                new_bin_content_SFcUp = sqrt(old_bin_content_SFcUp**2 + diff_SFc.GetBinContent(binx+1,biny+1)**2)
                SFc_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFcUp)
                upcount += diff_SFc.GetBinContent(binx+1,biny+1)**2
            elif diff_SFc.GetBinContent(binx+1,biny+1) < 0:
                old_bin_content_SFcDown = SFc_histDown.GetBinContent(binx+1,biny+1)
                new_bin_content_SFcDown = sqrt(old_bin_content_SFcDown**2 + diff_SFc.GetBinContent(binx+1,biny+1)**2)
                SFc_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFcDown)
                downcount += diff_SFc.GetBinContent(binx+1,biny+1)**2

            if diff_SFl.GetBinContent(binx+1,biny+1) > 0:
                old_bin_content_SFlUp = SFl_histUp.GetBinContent(binx+1,biny+1)
                new_bin_content_SFlUp = sqrt(old_bin_content_SFlUp**2 + diff_SFl.GetBinContent(binx+1,biny+1)**2)
                SFl_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFlUp)
                upcount += diff_SFl.GetBinContent(binx+1,biny+1)**2
            elif diff_SFl.GetBinContent(binx+1,biny+1) < 0:
                old_bin_content_SFlDown = SFl_histDown.GetBinContent(binx+1,biny+1)
                new_bin_content_SFlDown = sqrt(old_bin_content_SFlDown**2 + diff_SFl.GetBinContent(binx+1,biny+1)**2)
                SFl_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFlDown)
                downcount += diff_SFl.GetBinContent(binx+1,biny+1)**2

    avgcount = (upcount+downcount)        # Very rough estimate
    systContrib[systdir] = avgcount
    totalcount += avgcount

contriblist=[]
for systdir in sorted(systdirs):
    contriblist.append([systdir,systContrib[systdir]/totalcount*100])
print tabulate(contriblist,headers=['Name','Approx. contribution'])

#if args.ApplyBiasUnc:
#    currentdir = basedir + "/" + biasdirs[0]
#    tmp_file_ = ROOT.TFile(currentdir+"/cTag_SFs_80X_Spandan.root")
#    tmp_SFb_hist = tmp_file_.Get("SFb_hist_"+biasdirs[0])
#    tmp_SFc_hist = tmp_file_.Get("SFc_hist_"+biasdirs[0])
#    tmp_SFl_hist = tmp_file_.Get("SFl_hist_"+biasdirs[0])
#    central_SF_file.cd()
#    tmp_SFb_hist.Write()
#    tmp_SFc_hist.Write()
#    tmp_SFl_hist.Write()
#    tmp_file_.cd()

#    diff_SFb = tmp_SFb_hist.Clone()
#    diff_SFc = tmp_SFc_hist.Clone()
#    diff_SFl = tmp_SFl_hist.Clone()

#    diff_SFb.Add(SFb_histCentral,-1)
#    diff_SFc.Add(SFc_histCentral,-1)
#    diff_SFl.Add(SFl_histCentral,-1)

#    # add in quadrature the difference between two methods (with and without bias) divided by 2
#    for binx in range(diff_SFb.GetNbinsX()):
#        for biny in range(diff_SFb.GetNbinsY()):
#                old_bin_content_SFbUp = SFb_histUp.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFbUp = sqrt(old_bin_content_SFbUp**2 + (diff_SFb.GetBinContent(binx+1,biny+1)/2.)**2)
#                SFb_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFbUp)
#                old_bin_content_SFbDown = SFb_histDown.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFbDown = sqrt(old_bin_content_SFbDown**2 + (diff_SFb.GetBinContent(binx+1,biny+1)/2.)**2)
#                SFb_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFbDown)

#                old_bin_content_SFcUp = SFc_histUp.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFcUp = sqrt(old_bin_content_SFcUp**2 + (diff_SFc.GetBinContent(binx+1,biny+1)/2.)**2)
#                SFc_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFcUp)
#                old_bin_content_SFcDown = SFc_histDown.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFcDown = sqrt(old_bin_content_SFcDown**2 + (diff_SFc.GetBinContent(binx+1,biny+1)/2.)**2)
#                SFc_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFcDown)

#                old_bin_content_SFlUp = SFl_histUp.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFlUp = sqrt(old_bin_content_SFlUp**2 + (diff_SFl.GetBinContent(binx+1,biny+1)/2.)**2)
#                SFl_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFlUp)
#                old_bin_content_SFlDown = SFl_histDown.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFlDown = sqrt(old_bin_content_SFlDown**2 + (diff_SFl.GetBinContent(binx+1,biny+1)/2.)**2)
#                SFl_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFlDown)


# =============== Find pathological cases ====================
#print "="*10, "Pathological Cases:", "="*10
#recompute = []
#for binx in range(SFb_histCentral.GetNbinsX()):
#    for biny in range(SFb_histCentral.GetNbinsY()):
#        centralVal = SFb_histCentral.GetBinContent(binx+1,biny+1)
#        upVal = centralVal + 2*SFb_histUp.GetBinContent(binx+1,biny+1)
#        downVal = centralVal - 2*SFb_histDown.GetBinContent(binx+1,biny+1)
#        if upVal < 1. or downVal > 1.:
#            print "b:",(binx+1,biny+1),":", centralVal,upVal, downVal
#            recompute.append(['b',(binx+1,biny+1)])
#            SFb_histUP.SetBinContent(binx+1,biny+1,SFb_histUP_stat.GetBinContent(binx+1,biny+1))
#            SFb_histDown.SetBinContent(binx+1,biny+1,SFb_histDown_stat.GetBinContent(binx+1,biny+1))
#        else:
#            SFb_histCentral.SetBinContent(binx+1,biny+1,1.)

#for binx in range(SFc_histCentral.GetNbinsX()):
#    for biny in range(SFc_histCentral.GetNbinsY()):
#        centralVal = SFc_histCentral.GetBinContent(binx+1,biny+1)
#        upVal = centralVal + 2*SFc_histUp.GetBinContent(binx+1,biny+1)
#        downVal = centralVal - 2*SFc_histDown.GetBinContent(binx+1,biny+1)
#        if upVal < 1. or downVal > 1.:
#            print "c:",(binx+1,biny+1),":", centralVal,upVal, downVal
#            recompute.append(['c',(binx+1,biny+1)])
#            SFc_histUP.SetBinContent(binx+1,biny+1,SFc_histUP_stat.GetBinContent(binx+1,biny+1))
#            SFc_histDown.SetBinContent(binx+1,biny+1,SFc_histDown_stat.GetBinContent(binx+1,biny+1))
#        else:
#            SFc_histCentral.SetBinContent(binx+1,biny+1,1.)

#for binx in range(SFl_histCentral.GetNbinsX()):
#    for biny in range(SFl_histCentral.GetNbinsY()):
#        centralVal = SFl_histCentral.GetBinContent(binx+1,biny+1)
#        upVal = centralVal + 2*SFl_histUp.GetBinContent(binx+1,biny+1)
#        downVal = centralVal - 2*SFl_histDown.GetBinContent(binx+1,biny+1)
#        if upVal < 1. or downVal > 1.:
#            print "l:",(binx+1,biny+1),":", centralVal,upVal, downVal
#            recompute.append(['l',(binx+1,biny+1)])
#            SFl_histUP.SetBinContent(binx+1,biny+1,SFl_histUP_stat.GetBinContent(binx+1,biny+1))
#            SFl_histDown.SetBinContent(binx+1,biny+1,SFl_histDown_stat.GetBinContent(binx+1,biny+1))
#        else:
#            SFl_histCentral.SetBinContent(binx+1,biny+1,1.)

#syscomps = []
#for systdir in systdirs:
#    compname = '_'.join(systdir.split('_')[:-1])
#    if not compname+"_up" in systdirs or not compname+"_down" in systdirs:
#        print "WARNING: Systematic %s does not contain both variations. It will be skipped."%compname
#    else:
#        if compname not in syscomps: syscomps.append(compname)

#
#for systdir in syscomps:
#    currentdir = basedir + "/" + systdir
#    tmp_file_up = ROOT.TFile(currentdir+'_up'+"/cTag_SFs_80X_Spandan.root")
#    hList = [i.GetName() for i in list(tmp_file_up.GetListOfKeys())]
#    tmp_SFb_hist_up = tmp_file_up.Get([h for h in hList if h.startswith('SFb')][0])
#    tmp_SFc_hist_up = tmp_file_up.Get([h for h in hList if h.startswith('SFc')][0])
#    tmp_SFl_hist_up = tmp_file_up.Get([h for h in hList if h.startswith('SFl')][0])
#
#    tmp_file_down = ROOT.TFile(currentdir+'_down'+"/cTag_SFs_80X_Spandan.root")
#    hList = [i.GetName() for i in list(tmp_file_down.GetListOfKeys())]
#    tmp_SFb_hist_down = tmp_file_down.Get([h for h in hList if h.startswith('SFb')][0])
#    tmp_SFc_hist_down = tmp_file_down.Get([h for h in hList if h.startswith('SFc')][0])
#    tmp_SFl_hist_down = tmp_file_down.Get([h for h in hList if h.startswith('SFl')][0])

#    diff_SFb_up = tmp_SFb_hist_up.Clone()
#    diff_SFc_up = tmp_SFc_hist_up.Clone()
#    diff_SFl_up = tmp_SFl_hist_up.Clone()

#    diff_SFb_up.Add(SFb_histCentral,-1)
#    diff_SFc_up.Add(SFc_histCentral,-1)
#    diff_SFl_up.Add(SFl_histCentral,-1)
#
#    diff_SFb_down = tmp_SFb_hist_down.Clone()
#    diff_SFc_down = tmp_SFc_hist_down.Clone()
#    diff_SFl_down = tmp_SFl_hist_down.Clone()

#    diff_SFb_down.Add(SFb_histCentral,-1)
#    diff_SFc_down.Add(SFc_histCentral,-1)
#    diff_SFl_down.Add(SFl_histCentral,-1)

#    for binx in range(diff_SFb.GetNbinsX()):
#        for biny in range(diff_SFb.GetNbinsY()):

#            if diff_SFb.GetBinContent(binx+1,biny+1) > 0:
#                old_bin_content_SFbUp = SFb_histUp.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFbUp = sqrt(old_bin_content_SFbUp**2 + diff_SFb.GetBinContent(binx+1,biny+1)**2)
#                SFb_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFbUp)
#            elif diff_SFb.GetBinContent(binx+1,biny+1) < 0:
#                old_bin_content_SFbDown = SFb_histDown.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFbDown = sqrt(old_bin_content_SFbDown**2 + diff_SFb.GetBinContent(binx+1,biny+1)**2)
#                SFb_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFbDown)

#            if diff_SFc.GetBinContent(binx+1,biny+1) > 0:
#                old_bin_content_SFcUp = SFc_histUp.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFcUp = sqrt(old_bin_content_SFcUp**2 + diff_SFc.GetBinContent(binx+1,biny+1)**2)
#                SFc_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFcUp)
#            elif diff_SFc.GetBinContent(binx+1,biny+1) < 0:
#                old_bin_content_SFcDown = SFc_histDown.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFcDown = sqrt(old_bin_content_SFcDown**2 + diff_SFc.GetBinContent(binx+1,biny+1)**2)
#                SFc_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFcDown)

#            if diff_SFl.GetBinContent(binx+1,biny+1) > 0:
#                old_bin_content_SFlUp = SFl_histUp.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFlUp = sqrt(old_bin_content_SFlUp**2 + diff_SFl.GetBinContent(binx+1,biny+1)**2)
#                SFl_histUp.SetBinContent(binx+1,biny+1,new_bin_content_SFlUp)
#            elif diff_SFl.GetBinContent(binx+1,biny+1) < 0:
#                old_bin_content_SFlDown = SFl_histDown.GetBinContent(binx+1,biny+1)
#                new_bin_content_SFlDown = sqrt(old_bin_content_SFlDown**2 + diff_SFl.GetBinContent(binx+1,biny+1)**2)
#                SFl_histDown.SetBinContent(binx+1,biny+1,new_bin_content_SFlDown)


# ================================= Fit uncertainties ==================================
SFb_histUp_temp = ROOT.TH2D("SFb_hist_FitUnc_Up",";CvsL discriminator;CvsB discriminator;| SF_{b}^{central} - SF_{b}^{FitUnc_up} |",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
SFc_histUp_temp = ROOT.TH2D("SFc_hist_FitUnc_Up",";CvsL discriminator;CvsB discriminator;| SF_{c}^{central} - SF_{c}^{FitUnc_up} |",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2))
SFl_histUp_temp = ROOT.TH2D("SFl_hist_FitUnc_Up",";CvsL discriminator;CvsB discriminator;| SF_{l}^{central} - SF_{l}^{FitUnc_up} |",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3))
SFb_histDown_temp = ROOT.TH2D("SFb_hist_FitUnc_Down",";CvsL discriminator;CvsB discriminator;| SF_{b}^{central} - SF_{b}^{FitUnc_down}|",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
SFc_histDown_temp = ROOT.TH2D("SFc_hist_FitUnc_Down",";CvsL discriminator;CvsB discriminator;| SF_{c}^{central} - SF_{c}^{FitUnc_down}|",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2))
SFl_histDown_temp = ROOT.TH2D("SFl_hist_FitUnc_Down",";CvsL discriminator;CvsB discriminator;| SF_{l}^{central} - SF_{l}^{FitUnc_down}|",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3))

for binx in range(-1,SFb_histUp_temp.GetNbinsX()):
    for biny in range(-1,SFb_histUp_temp.GetNbinsY()):
        SFb_histUp_temp.SetBinContent(binx+1,biny+1,FitUncb[(binx+1,biny+1)])
        SFb_histDown_temp.SetBinContent(binx+1,biny+1,FitUncb[(binx+1,biny+1)])
        SFc_histUp_temp.SetBinContent(binx+1,biny+1,FitUncb[(binx+1,biny+1)])
        SFc_histDown_temp.SetBinContent(binx+1,biny+1,FitUncb[(binx+1,biny+1)])
        SFl_histUp_temp.SetBinContent(binx+1,biny+1,FitUncb[(binx+1,biny+1)])
        SFl_histDown_temp.SetBinContent(binx+1,biny+1,FitUncb[(binx+1,biny+1)])
#        print FitUncb[(binx+1,biny+1)]
        
SFb_histUp_temp.Add(SFb_histCentral)
SFc_histUp_temp.Add(SFc_histCentral)
SFl_histUp_temp.Add(SFl_histCentral)

SFb_histDown_temp.Add(SFb_histCentral,-1)
SFb_histDown_temp.Scale(-1)
SFc_histDown_temp.Add(SFc_histCentral,-1)
SFc_histDown_temp.Scale(-1)
SFl_histDown_temp.Add(SFl_histCentral,-1)
SFl_histDown_temp.Scale(-1)

for hist in [SFb_histUp_temp,SFb_histDown_temp,SFc_histUp_temp,SFc_histDown_temp,SFl_histUp_temp,SFl_histDown_temp]:
    for binx in range(-1,hist.GetNbinsX()):
        for biny in range(-1,hist.GetNbinsY()):
            hist.SetBinError(binx+1,biny+1,0.)

central_SF_file.cd()
SFb_histUp_temp.Write()
SFc_histUp_temp.Write()
SFl_histUp_temp.Write()
SFb_histDown_temp.Write()
SFc_histDown_temp.Write()
SFl_histDown_temp.Write()

# ======================================================================================
        

def combineUnc(dirs,systname):
    SFb_histUp_temp = ROOT.TH2D("SFb_hist_"+systname+"_Up",";CvsL discriminator;CvsB discriminator;| SF_{b}^{central} - SF_{b}^{"+systname+"_up} |",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
    SFc_histUp_temp = ROOT.TH2D("SFc_hist_"+systname+"_Up",";CvsL discriminator;CvsB discriminator;| SF_{c}^{central} - SF_{c}^{"+systname+"_up} |",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2))
    SFl_histUp_temp = ROOT.TH2D("SFl_hist_"+systname+"_Up",";CvsL discriminator;CvsB discriminator;| SF_{l}^{central} - SF_{l}^{"+systname+"_up} |",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3))
    SFb_histDown_temp = ROOT.TH2D("SFb_hist_"+systname+"_Down",";CvsL discriminator;CvsB discriminator;| SF_{b}^{central} - SF_{b}^{"+systname+"_down}|",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
    SFc_histDown_temp = ROOT.TH2D("SFc_hist_"+systname+"_Down",";CvsL discriminator;CvsB discriminator;| SF_{c}^{central} - SF_{c}^{"+systname+"_down}|",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2))
    SFl_histDown_temp = ROOT.TH2D("SFl_hist_"+systname+"_Down",";CvsL discriminator;CvsB discriminator;| SF_{l}^{central} - SF_{l}^{"+systname+"_down}|",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3))
    
    for binx in range(-1,SFb_histUp_temp.GetNbinsX()):
        for biny in range(-1,SFb_histUp_temp.GetNbinsY()):
            SFb_histUp_temp.SetBinContent(binx+1,biny+1,0.)
            SFb_histDown_temp.SetBinContent(binx+1,biny+1,0.)
            SFc_histUp_temp.SetBinContent(binx+1,biny+1,0.)
            SFc_histDown_temp.SetBinContent(binx+1,biny+1,0.)
            SFl_histUp_temp.SetBinContent(binx+1,biny+1,0.)
            SFl_histDown_temp.SetBinContent(binx+1,biny+1,0.)
        
    for systdir in dirs:    
        for binx in range(-1,diff_histos[systdir]['b'].GetNbinsX()):
            for biny in range(-1,diff_histos[systdir]['b'].GetNbinsY()):

                if  diff_histos[systdir]['b'].GetBinContent(binx+1,biny+1) > 0:
                    old_bin_content_SFbUp = SFb_histUp_temp.GetBinContent(binx+1,biny+1)
                    new_bin_content_SFbUp = sqrt(old_bin_content_SFbUp**2 +  diff_histos[systdir]['b'].GetBinContent(binx+1,biny+1)**2)
                    SFb_histUp_temp.SetBinContent(binx+1,biny+1,new_bin_content_SFbUp)
                elif diff_histos[systdir]['b'].GetBinContent(binx+1,biny+1) < 0:
                    old_bin_content_SFbDown = SFb_histDown_temp.GetBinContent(binx+1,biny+1)
                    new_bin_content_SFbDown = sqrt(old_bin_content_SFbDown**2 +  diff_histos[systdir]['b'].GetBinContent(binx+1,biny+1)**2)
                    SFb_histDown_temp.SetBinContent(binx+1,biny+1,new_bin_content_SFbDown)

                if diff_histos[systdir]['c'].GetBinContent(binx+1,biny+1) > 0:
                    old_bin_content_SFcUp = SFc_histUp_temp.GetBinContent(binx+1,biny+1)
                    new_bin_content_SFcUp = sqrt(old_bin_content_SFcUp**2 + diff_histos[systdir]['c'].GetBinContent(binx+1,biny+1)**2)
                    SFc_histUp_temp.SetBinContent(binx+1,biny+1,new_bin_content_SFcUp)
                elif diff_histos[systdir]['c'].GetBinContent(binx+1,biny+1) < 0:
                    old_bin_content_SFcDown = SFc_histDown_temp.GetBinContent(binx+1,biny+1)
                    new_bin_content_SFcDown = sqrt(old_bin_content_SFcDown**2 + diff_histos[systdir]['c'].GetBinContent(binx+1,biny+1)**2)
                    SFc_histDown_temp.SetBinContent(binx+1,biny+1,new_bin_content_SFcDown)

                if diff_histos[systdir]['l'].GetBinContent(binx+1,biny+1) > 0:
                    old_bin_content_SFlUp = SFl_histUp_temp.GetBinContent(binx+1,biny+1)
                    new_bin_content_SFlUp = sqrt(old_bin_content_SFlUp**2 + diff_histos[systdir]['l'].GetBinContent(binx+1,biny+1)**2)
                    SFl_histUp_temp.SetBinContent(binx+1,biny+1,new_bin_content_SFlUp)
                elif diff_histos[systdir]['l'].GetBinContent(binx+1,biny+1) < 0:
                    old_bin_content_SFlDown = SFl_histDown_temp.GetBinContent(binx+1,biny+1)
                    new_bin_content_SFlDown = sqrt(old_bin_content_SFlDown**2 + diff_histos[systdir]['l'].GetBinContent(binx+1,biny+1)**2)
                    SFl_histDown_temp.SetBinContent(binx+1,biny+1,new_bin_content_SFlDown)
                    
    SFb_histUp_temp.Add(SFb_histCentral)
    SFc_histUp_temp.Add(SFc_histCentral)
    SFl_histUp_temp.Add(SFl_histCentral)
    
    SFb_histDown_temp.Add(SFb_histCentral,-1)
    SFb_histDown_temp.Scale(-1)
    SFc_histDown_temp.Add(SFc_histCentral,-1)
    SFc_histDown_temp.Scale(-1)
    SFl_histDown_temp.Add(SFl_histCentral,-1)
    SFl_histDown_temp.Scale(-1)
    
    for hist in [SFb_histUp_temp,SFb_histDown_temp,SFc_histUp_temp,SFc_histDown_temp,SFl_histUp_temp,SFl_histDown_temp]:
        for binx in range(-1,hist.GetNbinsX()):
            for biny in range(-1,hist.GetNbinsY()):
                hist.SetBinError(binx+1,biny+1,0.)
    
    central_SF_file.cd()
    SFb_histUp_temp.Write()
    SFc_histUp_temp.Write()
    SFl_histUp_temp.Write()
    SFb_histDown_temp.Write()
    SFc_histDown_temp.Write()
    SFl_histDown_temp.Write()
    
XSecDirs = [i for i in systdirs if "XSec" in i]
combineUnc(XSecDirs,"XSecs")

SFb_histCentral_totalUnc=SFb_histCentral.Clone()
SFb_histCentral_totalUnc.SetName("SFb_hist_central_TotalUnc")
SFc_histCentral_totalUnc=SFc_histCentral.Clone()
SFc_histCentral_totalUnc.SetName("SFc_hist_central_TotalUnc")
SFl_histCentral_totalUnc=SFl_histCentral.Clone()
SFl_histCentral_totalUnc.SetName("SFl_hist_central_TotalUnc")

for binx in range(-1,SFb_histCentral.GetNbinsX()):
    for biny in range(-1,SFb_histCentral.GetNbinsY()):
        SFb_histCentral_totalUnc.SetBinError(binx+1,biny+1,max(SFb_histUp.GetBinContent(binx+1,biny+1),SFb_histDown.GetBinContent(binx+1,biny+1)))
        SFc_histCentral_totalUnc.SetBinError(binx+1,biny+1,max(SFc_histUp.GetBinContent(binx+1,biny+1),SFc_histDown.GetBinContent(binx+1,biny+1)))
        SFl_histCentral_totalUnc.SetBinError(binx+1,biny+1,max(SFl_histUp.GetBinContent(binx+1,biny+1),SFl_histDown.GetBinContent(binx+1,biny+1)))


#SFb_histCentral_totalUnc.Write()
#SFc_histCentral_totalUnc.Write()
#SFl_histCentral_totalUnc.Write()

ROOT.gStyle.SetPaintTextFormat("4.3f")

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
    c = ROOT.TCanvas("c","c",1200,1200)
    ROOT.gPad.SetMargin(0.13,0.18,0.11,0.17)
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
    box = ROOT.TPaveText(custom_bins_CvsB_jet1[0],1,1,1+.15*(custom_bins_CvsB_jet1[-1]-custom_bins_CvsB_jet1[0]))
    box.SetBorderSize(1)
    box.SetFillStyle(0)
    box.Draw("same")
    latex_cms = ROOT.TLatex()
    latex_cms.SetTextFont(42)
    latex_cms.SetTextSize(0.04)
    latex_cms.SetTextAlign(11)
    latex_cms.DrawLatexNDC(0.15,0.9,"#bf{CMS} #it{Preliminary}")
    latex_cms.DrawLatexNDC(0.15,0.85,"Wc/TTb/DYl selection")
    latex_cms.DrawLatexNDC(0.65,0.9,"DeepCSV")
    latex_cms.DrawLatexNDC(0.67,0.85,"c-tagger")
    latex_cms.DrawLatexNDC(0.6,0.95,"35.9 fb^{-1} (13 TeV)")
    c.SaveAs(basedir+"/"+centraldir+"/"+outName+".png")

saveHist(SFb_histCentral_totalUnc,"Unc_SFb_cTag")
saveHist(SFc_histCentral_totalUnc,"Unc_SFc_cTag")
saveHist(SFl_histCentral_totalUnc,"Unc_SFl_cTag")

#max_value = max(SFb_histUp.GetBinContent(SFb_histUp.GetMaximumBin()), SFb_histDown.GetBinContent(SFb_histUp.GetMaximumBin()), SFc_histUp.GetBinContent(SFc_histUp.GetMaximumBin()), SFc_histDown.GetBinContent(SFc_histUp.GetMaximumBin()), SFl_histUp.GetBinContent(SFl_histUp.GetMaximumBin()), SFl_histDown.GetBinContent(SFl_histUp.GetMaximumBin()))
max_value=2

if skip1bins:
    SFb_histUp=remove1bins(SFb_histUp)
    SFb_histDown=remove1bins(SFb_histDown)
    SFc_histUp=remove1bins(SFc_histUp)
    SFc_histDown=remove1bins(SFc_histDown)
    SFl_histUp=remove1bins(SFl_histUp)
    SFl_histDown=remove1bins(SFl_histDown)

cSFb = ROOT.TCanvas("cSFb","cSFb",1800,1200)
cSFb.Divide(3,2)
cSFb.cd(2)
ROOT.gPad.SetMargin(0.15,0.2,0.15,0.1)
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
latex_cms = ROOT.TLatex()
latex_cms.SetTextFont(42)
latex_cms.SetTextSize(0.048)
latex_cms.SetTextAlign(11)
latex_cms.DrawLatexNDC(0.15,0.92,"#bf{CMS} #it{Preliminary}")
latex_cms.DrawLatexNDC(0.56,0.92,"35.9 fb^{-1} (13 TeV)")
cSFb.cd(1)
ROOT.gPad.SetMargin(0.15,0.2,0.15,0.1)
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
ROOT.gPad.SetMargin(0.15,0.2,0.15,0.1)
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
ROOT.gPad.SetMargin(0.15,0.2,0.15,0.1)
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
ROOT.gPad.SetMargin(0.15,0.2,0.15,0.1)
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
ROOT.gPad.SetMargin(0.15,0.2,0.15,0.1)
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
cSFb.SaveAs(basedir+"/"+centraldir+"/SFs_cTag_UpDown_relative.png")
cSFb.SaveAs(basedir+"/"+centraldir+"/SFs_cTag_UpDown_relative.pdf")



# Save absolute values of up-down w.r.t. central in histograms
SFb_histUp_absolute = SFb_histUp.Clone()
SFb_histUp_absolute.Add(SFb_histCentral)
SFc_histUp_absolute = SFc_histUp.Clone()
SFc_histUp_absolute.Add(SFc_histCentral)
SFl_histUp_absolute = SFl_histUp.Clone()
SFl_histUp_absolute.Add(SFl_histCentral)
#outfileUp = ROOT.TFile(basedir+"/"+centraldir+"/DeepCSV_cTag_SFs_Up_94X.root","RECREATE")
#outfileUp.cd()
central_SF_file.cd()
SFb_histUp_absolute.Write()
SFc_histUp_absolute.Write()
SFl_histUp_absolute.Write()
#outfileUp.Close()

#
# NOTE: SF down variations have a lower bound at 0!! This needs te be checked
#
SFb_histDown_absolute = SFb_histDown.Clone()
SFb_histDown_absolute.Add(SFb_histCentral,-1)
SFb_histDown_absolute.Scale(-1)
for binx in range(-1,SFb_histDown_absolute.GetNbinsX()):
    for biny in range(-1,SFb_histDown_absolute.GetNbinsY()):
        if SFb_histDown_absolute.GetBinContent(binx+1,biny+1) < 0: SFb_histDown_absolute.SetBinContent(binx+1,biny+1,0.0)

SFc_histDown_absolute = SFc_histDown.Clone()
SFc_histDown_absolute.Add(SFc_histCentral,-1)
SFc_histDown_absolute.Scale(-1)
for binx in range(-1,SFc_histDown_absolute.GetNbinsX()):
    for biny in range(-1,SFc_histDown_absolute.GetNbinsY()):
        if SFc_histDown_absolute.GetBinContent(binx+1,biny+1) < 0: SFc_histDown_absolute.SetBinContent(binx+1,biny+1,0.0)

SFl_histDown_absolute = SFl_histDown.Clone()
SFl_histDown_absolute.Add(SFl_histCentral,-1)
SFl_histDown_absolute.Scale(-1)
for binx in range(-1,SFl_histDown_absolute.GetNbinsX()):
    for biny in range(-1,SFl_histDown_absolute.GetNbinsY()):
        if SFl_histDown_absolute.GetBinContent(binx+1,biny+1) < 0: SFl_histDown_absolute.SetBinContent(binx+1,biny+1,0.0)

#outfileDown = ROOT.TFile(basedir+"/"+centraldir+"/DeepCSV_cTag_SFs_Down_94X.root","RECREATE")
#outfileDown.cd()
central_SF_file.cd()
SFb_histDown_absolute.Write()
SFc_histDown_absolute.Write()
SFl_histDown_absolute.Write()
#outfileDown.Close()
central_SF_file.Close()

# ======== Bin-wise contribution of each systematic to uncertainties =========

os.system("mkdir -p "+basedir+"/"+centraldir+"/UncContribPlots/")

for flav in ['b','c','l']:
    for binx in range(1,SFb_histCentral.GetNbinsX()+1):
        for biny in range(1,SFb_histCentral.GetNbinsY()+1):
            
            def getSummedUncs(systlist,caps=False):
                Err = 0.
                direcs=['up','down']
                if caps: direcs=['Up','Down']
                for syst in systlist:
                    for direc in direcs:
                        Err += binwiseUncCont[flav][syst+direc][(binx,biny)]**2
                return Err #**0.5
            
            statMCErr = getSummedUncs(['MCStat'])
            statdataErr = getSummedUncs(['dataStat'])
            XSecDYErr = getSummedUncs(['XSecDY'])
            XSecSTErr = getSummedUncs(['XSecST'])
            XSecTTErr = getSummedUncs(['XSecTT'])
            XSecVVErr = getSummedUncs(['XSecVV'])
            XSecWErr = getSummedUncs(['XSecW'])
            lepIDErr = getSummedUncs(['EleIDSF','MuIDSF'])
            JECErr = getSummedUncs(['jer','jesTotal'],True)
            LHEErr = getSummedUncs(['LHEScaleWeightmuF','LHEScaleWeightmuR'])
            PUErr = getSummedUncs(['PUWeight'])            
                        
            XSecErr = XSecDYErr+XSecSTErr+XSecTTErr+XSecVVErr+XSecWErr
            StatErr = statMCErr+statdataErr
            SystErr = lepIDErr + JECErr+ LHEErr+PUErr
            sumErr = (statMCErr+statdataErr+XSecErr+lepIDErr+JECErr+LHEErr+PUErr)/100            
            if sumErr==0.: continue            
#            print binx,biny, statMCErr/sumErr, statdataErr/sumErr, XSecErr/sumErr, lepIDErr/sumErr, JECErr/sumErr, LHEErr/sumErr, PUErr/sumErr
            XSecErr /= sumErr
            StatErr /= sumErr
            SystErr /= sumErr
            
            threshold = 2
            custlabel=[]
            if StatErr>threshold:
                custlabel.append("Stat.")
            else:
                custlabel.append("")
            if XSecErr>threshold:
                custlabel.append("XSec")
            else:
                custlabel.append("")
            if SystErr>threshold:
                custlabel.append("Syst.")
            else:
                custlabel.append("")
            
            fig, ax = plt.subplots(figsize=(5,5))
            
            size = 0.4
            vals = [[statMCErr,statdataErr], [XSecDYErr,XSecSTErr,XSecTTErr,XSecVVErr,XSecWErr], [lepIDErr, JECErr, LHEErr, PUErr]]
            
            flatvals=[i/sumErr for sub in vals for i in sub]
            
            flatlabels=["MC","Data","DY","ST","TT","VV","W","lepID","JEC","LHE","PU"]
            printlabels=[]
            for i,val in enumerate(flatvals):
                if val > 5:
                    printlabels.append(flatlabels[i])
                else:
                    printlabels.append("")

            cmap1 = plt.get_cmap("Reds")
            cmap2 = plt.get_cmap("Greens")
            cmap3 = plt.get_cmap("Blues")
            outer_colors = [cmap1(200),cmap2(200),cmap3(200)]
            inner_colors = [cmap1(100), cmap1(150),     cmap2(50),cmap2(80),cmap2(110),cmap2(140),cmap2(170),     cmap3(40), cmap3(80),cmap3(120),cmap3(160)]
            wedges, texts = ax.pie([sum(elem)/sumErr for elem in vals], radius=1, colors=outer_colors,
                   wedgeprops=dict(width=size, edgecolor='w'), labels=custlabel, labeldistance=1.05)

            wedges2, texts2 = ax.pie(flatvals, radius=(1-size), colors=inner_colors,
                   wedgeprops=dict(width=size, edgecolor='w'), labels=printlabels, labeldistance=0.7)
                   
            x1 = SFb_histCentral.GetXaxis().GetBinLowEdge(binx)
            x2 = SFb_histCentral.GetXaxis().GetBinUpEdge(binx)
            y1 = SFb_histCentral.GetYaxis().GetBinLowEdge(biny)
            y2 = SFb_histCentral.GetYaxis().GetBinUpEdge(biny)
            tit=r'$\mathrm{SF}_{%s}$: CvsL $\in$ [%.1f,%.1f], CvsB $\in$ [%.1f,%.1f]'%(flav,x1,x2,y1,y2)
            if binx==1: tit = "CvsX = -1"

            ax.set(aspect="equal", title=tit)
            plt.setp(texts, size=15, weight="bold")
            plt.setp(texts2, size=10, ha="center", va="center", rotation_mode = 'anchor')
            plt.tight_layout()
            plt.savefig(basedir+"/"+centraldir+"/UncContribPlots/flav-%s-binx-%d-biny-%d.png"%(flav,binx,biny))
            plt.close()
            
    hor=500
    ver=500
    result = Image.new("RGB", (hor*5, ver*5))#, color=(255,255,255,0))
    for i in range(1,6):
        for j in range(1,6):
            img = Image.open(basedir+"/"+centraldir+"/UncContribPlots/flav-%s-binx-%d-biny-%d.png"%(flav,i+1,j+1))
    #            img.thumbnail((hor, ver), Image.ANTIALIAS)
            x = (i-1)*hor
            y = (5-j)*ver
            result.paste(img, (x, y))
    result.save(basedir+"/"+centraldir+"/UncContribPlots/grid-flav-%s.png"%flav)

