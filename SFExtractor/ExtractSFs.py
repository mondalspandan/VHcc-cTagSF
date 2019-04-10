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
import matplotlib.pyplot as plt
from PIL import Image

skip1bins=True

ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)

parser = ArgumentParser()
parser.add_argument('--indir', default="190129_Systs",help='input directory that contains all the Histograms with syst variations')
parser.add_argument('--rate', default=7.5e-3,help='allowed rate of change in SF per iteration')
#parser.add_argument('--NormalizeMCToData', default=True,help='Normalize Data-to-MC')
parser.add_argument('--NormalizeMCToData', action='store_true', default=True, help='skip new features')
parser.add_argument('--AdaptiveIteration', action='store_true', default=True, help='Order the iterative fit from purest region to impure')
parser.add_argument('--semileptonic', action='store_true', help='Use only semileptonic ttbar selection instead of combined')
parser.add_argument('--dileptonic', action='store_true', help='Use only dileptonic ttbar selection instead of combined')
parser.add_argument('--verbose', action='store_true', help='More info in stdout')

# The following two flags are for validation tests. Ignore for normal SF derivation
parser.add_argument('--injectSF', default="",help='apply SFs of a given flavour from the start')
parser.add_argument('--increaseFlav', default="",help='increase given flavour contribution by 20%')
parser.add_argument('--increaseFlavPseudo', default="",help='increase given flavour contribution by 20%, use pseudodata')
SFsource = "SFs_inclTTbar.root"

args = parser.parse_args()
rate = float(args.rate)

basedir = args.indir
subdirs = [i for i in os.listdir(basedir) if os.path.isdir(basedir+"/"+i)]
if args.injectSF == "":
    injectSF = False
else:
    injectSF = True
    SFfl = ROOT.TFile.Open(SFsource)
    SFhist = SFfl.Get("SF"+args.injectSF.lower()+"_hist_central")
    if not SFhist:
        print "Incorrect input for injectSF."
        raise ValueError

print "Normalize MC To Data:", args.NormalizeMCToData
print "Adaptive order of iteration:", args.AdaptiveIteration

#****************************************************
#
# DERIVE TOTAL UNCERTAINTY FROM TEMPLATES TO BE USED IN CHI2 CALCULATION
#
#****************************************************
syst_dirs = [i for i in subdirs if not "central" in i]
central_dir = [i for i in subdirs if "central" in i]

histo_dict_uncPositive = {}
histo_dict_uncPositive["jet1"] = {
    "b" : ROOT.TH2D("b1_uncPositive",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
    "c" : ROOT.TH2D("c1_uncPositive",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
    "l" : ROOT.TH2D("l1_uncPositive",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
}
histo_dict_uncPositive["jet2"] = {
    "b" : ROOT.TH2D("b2_uncPositive",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
    "c" : ROOT.TH2D("c2_uncPositive",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
    "l" : ROOT.TH2D("l2_uncPositive",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
}
histo_dict_uncPositive["jet3"] = {
    "b" : ROOT.TH2D("b3_uncPositive",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
    "c" : ROOT.TH2D("c3_uncPositive",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
    "l" : ROOT.TH2D("l3_uncPositive",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
}

histo_dict_uncNegative = {}
histo_dict_uncNegative["jet1"] = {
    "b" : ROOT.TH2D("b1_uncNegative",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
    "c" : ROOT.TH2D("c1_uncNegative",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
    "l" : ROOT.TH2D("l1_uncNegative",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
}
histo_dict_uncNegative["jet2"] = {
    "b" : ROOT.TH2D("b2_uncNegative",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
    "c" : ROOT.TH2D("c2_uncNegative",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
    "l" : ROOT.TH2D("l2_uncNegative",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
}
histo_dict_uncNegative["jet3"] = {
    "b" : ROOT.TH2D("b3_uncNegative",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
    "c" : ROOT.TH2D("c3_uncNegative",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
    "l" : ROOT.TH2D("l3_uncNegative",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
}

histo_dict_uncTotal = {}
histo_dict_uncTotal["jet1"] = {
    "b" : ROOT.TH2D("b1_uncTotal",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
    "c" : ROOT.TH2D("c1_uncTotal",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
    "l" : ROOT.TH2D("l1_uncTotal",";DeepCSV CvsL first jet;DeepCSV CvsB first jet;Events",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1)),
}
histo_dict_uncTotal["jet2"] = {
    "b" : ROOT.TH2D("b2_uncTotal",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
    "c" : ROOT.TH2D("c2_uncTotal",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
    "l" : ROOT.TH2D("l2_uncTotal",";DeepCSV CvsL second jet;DeepCSV CvsB second jet;Events",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2)),
}
histo_dict_uncTotal["jet3"] = {
    "b" : ROOT.TH2D("b3_uncTotal",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
    "c" : ROOT.TH2D("c3_uncTotal",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
    "l" : ROOT.TH2D("l3_uncTotal",";DeepCSV CvsL third jet;DeepCSV CvsB third jet;Events",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3)),
}

# SFb_hist = ROOT.TH2D("SFb_hist",";CvsL;CvsB;SFb",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
# SFc_hist = ROOT.TH2D("SFc_hist",";CvsL;CvsB;SFc",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2))
# SFl_hist = ROOT.TH2D("SFl_hist",";CvsL;CvsB;SFl",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3))

def getcbld(fl):
    inp = ROOT.TFile.Open(fl,'READ')
    hList = [i.GetName() for i in list(inp.GetListOfKeys())]
    h={}

    for ihist, hName in enumerate(hList):
        h[hName]=inp.Get(hName)

    c = h["Wplusc"].Clone()
    c.Add(h["Wpluscc"])

    b = h["Wplusb"].Clone()
    l = h["Wplusuds"].Clone()
    d = h["Data"].Clone()

    c.SetDirectory(0)
    b.SetDirectory(0)
    l.SetDirectory(0)
    d.SetDirectory(0)

    for ihist, hName in enumerate(hList):
        if hName.startswith("W"): continue
        if hName.endswith("c"):
            c.Add(h[hName])
        elif hName.endswith("b"):
            b.Add(h[hName])
        elif hName.endswith("uds"):
            l.Add(h[hName])
    inp.Close()

    if args.increaseFlavPseudo=="c":
        cnew=c.Clone()
        cnew.Scale(1.2)
        bnew=b.Clone()
        lnew=l.Clone()
        def getint(hist):
            nbinx = hist.GetNbinsX()
            nbiny = hist.GetNbinsY()
            return hist.Integral(0,nbinx+1,0,nbiny+1)
        bkgevents = getint(b)+getint(c)+getint(l)-getint(cnew)
        bkgscale = bkgevents/(getint(b)+getint(l))
        bnew.Scale(bkgscale)
        lnew.Scale(bkgscale)
        cnew.Add(bnew)
        cnew.Add(lnew)
        d=cnew.Clone()

    if args.increaseFlavPseudo=="b":
        bnew=b.Clone()
        bnew.Scale(1.2)
        cnew=c.Clone()
        lnew=l.Clone()
        def getint(hist):
            nbinx = hist.GetNbinsX()
            nbiny = hist.GetNbinsY()
            return hist.Integral(0,nbinx+1,0,nbiny+1)
        bkgevents = getint(b)+getint(c)+getint(l)-getint(bnew)
        bkgscale = bkgevents/(getint(c)+getint(l))
        cnew.Scale(bkgscale)
        lnew.Scale(bkgscale)
        bnew.Add(cnew)
        bnew.Add(lnew)
        d=bnew.Clone()

    if args.increaseFlavPseudo=="l":
        lnew=l.Clone()
        lnew.Scale(1.2)
        cnew=c.Clone()
        bnew=b.Clone()
        def getint(hist):
            nbinx = hist.GetNbinsX()
            nbiny = hist.GetNbinsY()
            return hist.Integral(0,nbinx+1,0,nbiny+1)
        bkgevents = getint(b)+getint(c)+getint(l)-getint(lnew)
        bkgscale = bkgevents/(getint(c)+getint(b))
        cnew.Scale(bkgscale)
        bnew.Scale(bkgscale)
        lnew.Add(cnew)
        lnew.Add(bnew)
        d=lnew.Clone()

    if args.NormalizeMCToData:
        nbinx = d.GetNbinsX()
        nbiny = d.GetNbinsY()
        MC_Total = float(b.Integral(0,nbinx+1,0,nbiny+1) + c.Integral(0,nbinx+1,0,nbiny+1) + l.Integral(0,nbinx+1,0,nbiny+1))
        Data_Total = float(d.Integral(0,nbinx+1,0,nbiny+1))
        scale = Data_Total / MC_Total
        if args.verbose: print "        MC: %d, Data: %d, Scale: %f"%(MC_Total, Data_Total, scale)
        c.Scale(scale)
        b.Scale(scale)
        l.Scale(scale)

    return c,b,l,d

def combineChannels(flE,flM,fl3=[]):
    if args.verbose: print "    Processing first channel:"
    ce,be,le,de = getcbld(flE)
    if args.verbose: print "    Processing second channel:"
    cm,bm,lm,dm = getcbld(flM)
    ce.Add(cm)
    be.Add(bm)
    le.Add(lm)
    de.Add(dm)

    if args.verbose: print "    Processing more channels:"
    for fl in fl3:
        c3,b3,l3,d3 = getcbld(fl)
        ce.Add(c3.Clone())
        be.Add(b3.Clone())
        le.Add(l3.Clone())
        de.Add(d3.Clone())
    return ce, be, le, de

def makeDict(dir,wantData=False):
    rootFileList = [os.path.join(dir,i) for i in os.listdir(dir) if i.endswith('.root')]
    for fl in rootFileList:
        # ============== Old naming conventions ==============
        # print fl
        # if '2D_e' in fl and 'jetMuPt_by_jetPt_0-0.6' in fl and 'jet_nJet_0-4' in fl:
        #     WcEFile = fl
        # elif '2D_m' in fl and 'jetMuPt_by_jetPt_0-0.4' in fl and 'jet_nJet_0-4' in fl:
        #     WcMFile = fl
        # ## elif '2D_m' in fl and 'jetMuPt_by_jetPt_0.4-' in fl:
        # ##     DYMFile = fl
        # elif '2D_m_jet_CvsL_0.' in fl:
        #     DYMFile = fl
        # ## elif '2D_e' in fl and 'jet_nJet_5-' in fl:
        # ##     TTEFile = fl
        # ## elif '2D_m' in fl and 'jet_nJet_5-' in fl:
        # ##     TTMFile = fl
        # elif '2D_e' in fl and 'is_EE' in fl:
        #     TTEEFile = fl
        # elif '2D_m' in fl and 'is_MM' in fl:
        #     TTMMFile = fl
        # elif '2D_e' in fl and 'is_ME' in fl:
        #     TTMEFile = fl
        #=====================================================
        if "Wc_m_" in fl:
            WcMFile = fl
        elif "Wc_e_" in fl:
            WcEFile = fl
        elif "TT_mm_" in fl:
            TTMMFile = fl
        elif "TT_ee_" in fl:
            TTEEFile = fl
        elif "TT_me_" in fl:
            TTMEFile = fl
        elif "DY_m_" in fl:
            DYMFile = fl
        elif "TT_semi_m" in fl:
            TTSemiMFile = fl
        elif "TT_semi_e" in fl:
            TTSemiEFile = fl

    if args.verbose: print "Processing W+c selection:"
    cW,bW,lW,dW = combineChannels(WcEFile,WcMFile)

    if args.verbose: print "Processing TT selection:"
    if args.semileptonic:
        cTT,bTT,lTT,dTT = combineChannels(TTSemiEFile,TTSemiMFile)
        print "Using Semileptonic ttbar selection."
    elif args.dileptonic:
        cTT,bTT,lTT,dTT = combineChannels(TTEEFile,TTMMFile,[TTMEFile])
        print "Using Dileptonic ttbar selection."
    else:
        cTT,bTT,lTT,dTT = combineChannels(TTEEFile,TTMMFile,[TTMEFile,TTSemiEFile,TTSemiMFile])
        print "Using combined dileptonic and semileptonic ttbar selection."
# #    cW,bW,lW,dW = getcbld(WcEFile)
# #    cTT,bTT,lTT,dTT = getcbld(TTEFile)
#     cW,bW,lW,dW = getcbld(WcMFile)
#     cTT,bTT,lTT,dTT = getcbld(TTMFile)
    if args.verbose: print "Processing DY selection:"
    cDY,bDY,lDY,dDY = getcbld(DYMFile)

    nbinx = cW.GetNbinsX()
    nbiny = cW.GetNbinsY()
#    print "Report:"
    WTotal = cW.Integral(0,nbinx+1,0,nbiny+1)+bW.Integral(0,nbinx+1,0,nbiny+1)+lW.Integral(0,nbinx+1,0,nbiny+1)
    TTTotal = cTT.Integral(0,nbinx+1,0,nbiny+1)+bTT.Integral(0,nbinx+1,0,nbiny+1)+lTT.Integral(0,nbinx+1,0,nbiny+1)
    DYTotal = cDY.Integral(0,nbinx+1,0,nbiny+1)+bDY.Integral(0,nbinx+1,0,nbiny+1)+lDY.Integral(0,nbinx+1,0,nbiny+1)
    if args.verbose:
        print "W Region:  Events: %d, c=%f %%, b=%f %%, l=%f %%, data: %d"%(WTotal,cW.Integral(0,nbinx+1,0,nbiny+1)/WTotal*100,bW.Integral(0,nbinx+1,0,nbiny+1)/WTotal*100,lW.Integral(0,nbinx+1,0,nbiny+1)/WTotal*100, dW.Integral(0,nbinx+1,0,nbiny+1))
        print "TT Region: Events: %d, c=%f %%, b=%f %%, l=%f %%, data: %d"%(TTTotal,cTT.Integral(0,nbinx+1,0,nbiny+1)/TTTotal*100,bTT.Integral(0,nbinx+1,0,nbiny+1)/TTTotal*100,lTT.Integral(0,nbinx+1,0,nbiny+1)/TTTotal*100, dTT.Integral(0,nbinx+1,0,nbiny+1))
        print "DY Region: Events: %d, c=%f %%, b=%f %%, l=%f %%, data: %d"%(DYTotal,cDY.Integral(0,nbinx+1,0,nbiny+1)/DYTotal*100,bDY.Integral(0,nbinx+1,0,nbiny+1)/DYTotal*100,lDY.Integral(0,nbinx+1,0,nbiny+1)/DYTotal*100, dDY.Integral(0,nbinx+1,0,nbiny+1))

    '''
    jet1 is b-enriched aka my TT region.
    jet2 is c-enriched aka my Wc region.
    jet3 is l-enriched aka my DY region.
    '''
    outdict = {}
    if not wantData:
        outdict['jet1'] = {'b' : bTT, 'c' : cTT, 'l' : lTT}
        outdict['jet2'] = {'b' : bW,  'c' : cW,  'l' : lW }
        outdict['jet3'] = {'b' : bDY, 'c' : cDY, 'l' : lDY}
    else:
        outdict = {'jet1' : dTT, 'jet2' : dW, 'jet3' : dDY}

    return outdict

#central_MC_histo_dict = pickle.load(open(basedir+"/"+central_dir[0]+"/MC_histograms2D.pkl","rb"))
central_MC_histo_dict = makeDict(os.path.join(basedir,central_dir[0]))

# First initialize the Up and Down systematics histos with statistical uncertainties
for jet, flavor_dict in histo_dict_uncPositive.iteritems():
        for flav, hist in flavor_dict.iteritems():
            for binx in range(hist.GetNbinsX()):
                for biny in range(hist.GetNbinsY()):
                    if skip1bins and (binx==0 or biny==0) and not (binx==0 and biny==0): continue
#                    if central_MC_histo_dict[jet][flav].GetBinContent(binx+1,biny+1) >= 0 :
#                        stat_unc = sqrt(central_MC_histo_dict[jet][flav].GetBinContent(binx+1,biny+1))
#                    else:
#                        stat_unc = 1
                    stat_unc = central_MC_histo_dict[jet][flav].GetBinError(binx+1,biny+1)
                    histo_dict_uncPositive[jet][flav].SetBinContent(binx+1,biny+1,stat_unc)
                    histo_dict_uncNegative[jet][flav].SetBinContent(binx+1,biny+1,stat_unc)


for systdir in syst_dirs:
    print "\n\nProcessing: %s"%systdir
    dict_tmp  = makeDict(os.path.join(basedir,systdir))
    for jet, flavor_dict in dict_tmp.iteritems():
        for flav, hist in flavor_dict.iteritems():
            syst_histo = hist
            central_histo = central_MC_histo_dict[jet][flav]
            diff_hist = syst_histo.Clone()
            diff_hist.Add(central_histo,-1)
            for binx in range(diff_hist.GetNbinsX()):
                for biny in range(diff_hist.GetNbinsY()):
                    if skip1bins and (binx==0 or biny==0) and not (binx==0 and biny==0): continue
                    if diff_hist.GetBinContent(binx+1,biny+1) > 0:
                        old_unc = histo_dict_uncPositive[jet][flav].GetBinContent(binx+1,biny+1)
                        histo_dict_uncPositive[jet][flav].SetBinContent(binx+1,biny+1,sqrt(old_unc**2 + diff_hist.GetBinContent(binx+1,biny+1)**2))
                    elif diff_hist.GetBinContent(binx+1,biny+1) < 0:
                        old_unc = histo_dict_uncNegative[jet][flav].GetBinContent(binx+1,biny+1)
                        histo_dict_uncNegative[jet][flav].SetBinContent(binx+1,biny+1,sqrt(old_unc**2 + diff_hist.GetBinContent(binx+1,biny+1)**2))

# Take a per-bin uncertainty, calculated as the average between the Up and Down total systematic
for jet, flavor_dict in histo_dict_uncTotal.iteritems():
    for flav, hist in flavor_dict.iteritems():
        for binx in range(hist.GetNbinsX()):
            for biny in range(hist.GetNbinsY()):
                if skip1bins and (binx==0 or biny==0) and not (binx==0 and biny==0): continue
                Positive_content = histo_dict_uncPositive[jet][flav].GetBinContent(binx+1,biny+1)
                Negative_content = histo_dict_uncNegative[jet][flav].GetBinContent(binx+1,biny+1)
                #print Positive_content,Negative_content
                hist.SetBinContent(binx+1,biny+1,np.mean([Positive_content,Negative_content]))
#                if central_MC_histo_dict[jet][flav].GetBinContent(binx+1,biny+1) != 0: print  binx+1,biny+1, np.mean([Positive_content,Negative_content])/float(central_MC_histo_dict[jet][flav].GetBinContent(binx+1,biny+1))


#****************************************************
#
# For each of the systematics, do the entire SF calculation
#
#****************************************************

for i in subdirs:
    if i.endswith("central"):
        cenName = i
        break
subdirs.remove(cenName)
subdirs = [cenName]+subdirs

for directory in [i for i in subdirs]:
    print "STARTING TO PROCESS %s"%directory
    current_dir=basedir+"/"+directory
    histo_dict = makeDict(current_dir)
    datahisto_dict = makeDict(current_dir,True)
#    for jet, hist in datahisto_dict.iteritems():
#        for binx in range(hist.GetNbinsX()):
#            for biny in range(hist.GetNbinsY()):
#                stat_unc = central_MC_histo_dict[jet][flav].GetBinError(binx+1,biny+1)
##                print stat_unc


    if not os.path.isdir(current_dir+"/fitPlots"): os.mkdir(current_dir+"/fitPlots")

#    print datahisto_dict["jet1"].Integral()

    for jet,flav_dict in histo_dict.iteritems():
            for flav,hist in flav_dict.iteritems():
                print jet, flav, hist.Integral()

#    if args.NormalizeMCToData:
#        #scale = 1.085
##        print "Renomalize MC to data with scaleing factor: %.3f"%scale
#        for jet,flav_dict in histo_dict.iteritems():
#            nbinx = datahisto_dict[jet].GetNbinsX()
#            nbiny = datahisto_dict[jet].GetNbinsY()
#
#            MC_Total = float(histo_dict[jet]["b"].Integral(0,nbinx+1,0,nbiny+1) + histo_dict[jet]["c"].Integral(0,nbinx+1,0,nbiny+1) + histo_dict[jet]["l"].Integral(0,nbinx+1,0,nbiny+1))
#            Data_Total = float(datahisto_dict[jet].Integral(0,nbinx+1,0,nbiny+1))
#            scale = Data_Total / MC_Total
#            print "Scale for jet,", jet,":",scale,"; MC:",MC_Total,"; Data:", Data_Total
#            for flav,hist in flav_dict.iteritems():
#                hist.Scale(scale)

#    for jet,flav_dict in histo_dict.iteritems():
#            for flav,hist in flav_dict.iteritems():
#                print hist.Integral()

    convergence_dict = {}
    suff = '_'.join(directory.split('_')[2:])
    SFb_hist = ROOT.TH2D("SFb_hist_"+suff,";CvsL discriminator;CvsB discriminator;SF_{b}",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
    SFc_hist = ROOT.TH2D("SFc_hist_"+suff,";CvsL discriminator;CvsB discriminator;SF_{c}",nbins_CvsL_jet2,array("d",custom_bins_CvsL_jet2),nbins_CvsB_jet2,array("d",custom_bins_CvsB_jet2))
    SFl_hist = ROOT.TH2D("SFl_hist_"+suff,";CvsL discriminator;CvsB discriminator;SF_{light}",nbins_CvsL_jet3,array("d",custom_bins_CvsL_jet3),nbins_CvsB_jet3,array("d",custom_bins_CvsB_jet3))

    chi2b_hist = ROOT.TH2D("chi2b_"+suff,";CvsL discriminator;CvsB discriminator;#chi^{2}_{b}",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
    chi2c_hist = ROOT.TH2D("chi2c_"+suff,";CvsL discriminator;CvsB discriminator;#chi^{2}_{c}",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
    chi2l_hist = ROOT.TH2D("chi2l_"+suff,";CvsL discriminator;CvsB discriminator;#chi^{2}_{l}",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))
    chi2_hist = ROOT.TH2D("chi2_"+suff,";CvsL discriminator;CvsB discriminator;#chi^{2}",nbins_CvsL_jet1,array("d",custom_bins_CvsL_jet1),nbins_CvsB_jet1,array("d",custom_bins_CvsB_jet1))

    boxes  = []
    boxesb = []
    boxesc = []
    boxesl = []

    fit_unc_dict = {}

    for binx in range(histo_dict["jet1"]["b"].GetNbinsX()):
        for biny in range(histo_dict["jet1"]["b"].GetNbinsY()):
            if skip1bins and (binx==0 or biny==0) and not (binx==0 and biny==0): continue

           # if not (binx==1 and biny==1): continue

            convergence_dict[(binx,biny)] = {"SFb":[],"SFc":[],"SFl":[]}

            print binx+1,biny+1#,histo_dict["jet1"]["b"].GetBinContent(binx+1,biny+1)

            if injectSF:
                toInject = SFhist.GetBinContent(binx+1,biny+1)
                print "Injecting SF = %f for flavour %s."%(toInject,args.injectSF)
                for jet in ["jet1","jet2","jet3"]:
                    histo_dict[jet][args.injectSF].SetBinContent(binx+1,biny+1,histo_dict[jet][args.injectSF].GetBinContent(binx+1,biny+1)*toInject)
            if args.increaseFlav != "":
                print "Increasing %s flavour contribution by 20%%."%(args.increaseFlav)
                for jet in ["jet1","jet2","jet3"]:
                    histo_dict[jet][args.increaseFlav].SetBinContent(binx+1,biny+1,histo_dict[jet][args.increaseFlav].GetBinContent(binx+1,biny+1)*1.2)

            N_MC_b1 = histo_dict["jet1"]["b"].GetBinContent(binx+1,biny+1)
            N_MC_c1 = histo_dict["jet1"]["c"].GetBinContent(binx+1,biny+1)
            N_MC_l1 = histo_dict["jet1"]["l"].GetBinContent(binx+1,biny+1)
            N_MC_b2 = histo_dict["jet2"]["b"].GetBinContent(binx+1,biny+1)
            N_MC_c2 = histo_dict["jet2"]["c"].GetBinContent(binx+1,biny+1)
            N_MC_l2 = histo_dict["jet2"]["l"].GetBinContent(binx+1,biny+1)
            N_MC_b3 = histo_dict["jet3"]["b"].GetBinContent(binx+1,biny+1)
            N_MC_c3 = histo_dict["jet3"]["c"].GetBinContent(binx+1,biny+1)
            N_MC_l3 = histo_dict["jet3"]["l"].GetBinContent(binx+1,biny+1)
            N_Data_1 = datahisto_dict["jet1"].GetBinContent(binx+1,biny+1)
            N_Data_2 = datahisto_dict["jet2"].GetBinContent(binx+1,biny+1)
            N_Data_3 = datahisto_dict["jet3"].GetBinContent(binx+1,biny+1)

            #Protection against empty regions (only relevant to compare to WPs from c-tagger)
            if (N_MC_b1+N_MC_c1+N_MC_l1) == 0: N_MC_l1=1
            if (N_MC_b2+N_MC_c2+N_MC_l2) == 0: N_MC_l2=1
            if (N_MC_b3+N_MC_c3+N_MC_l3) == 0: N_MC_l3=1
            # if N_MC_b1 < 0: N_MC_b1 = 0.
            # if N_MC_b2 < 0: N_MC_b2 = 0.
            # if N_MC_b3 < 0: N_MC_b3 = 0.
            # if N_MC_c1 < 0: N_MC_c1 = 0.
            # if N_MC_c2 < 0: N_MC_c2 = 0.
            # if N_MC_c3 < 0: N_MC_c3 = 0.
            # if N_MC_l1 < 0: N_MC_l1 = 0.
            # if N_MC_l2 < 0: N_MC_l2 = 0.
            # if N_MC_l3 < 0: N_MC_l3 = 0.
            if N_Data_1 == 0: N_Data_1 = 1
            if N_Data_2 == 0: N_Data_2 = 1
            if N_Data_3 == 0: N_Data_3 = 1

            print "Jet1: Fraction of (b,c,l): (%.3f,%.3f,%.3f)"%(N_MC_b1/(N_MC_b1+N_MC_c1+N_MC_l1),N_MC_c1/(N_MC_b1+N_MC_c1+N_MC_l1),N_MC_l1/(N_MC_b1+N_MC_c1+N_MC_l1))
            print "Jet2: Fraction of (b,c,l): (%.3f,%.3f,%.3f)"%(N_MC_b2/(N_MC_b2+N_MC_c2+N_MC_l2),N_MC_c2/(N_MC_b2+N_MC_c2+N_MC_l2),N_MC_l2/(N_MC_b2+N_MC_c2+N_MC_l2))
            if not (N_MC_b3+N_MC_c3+N_MC_l3) == 0: print "Jet3: Fraction of (b,c,l): (%.3f,%.3f,%.3f)"%(N_MC_b3/(N_MC_b3+N_MC_c3+N_MC_l3),N_MC_c3/(N_MC_b3+N_MC_c3+N_MC_l3),N_MC_l3/(N_MC_b3+N_MC_c3+N_MC_l3))

            # uncertainty on this bin
            Total_Unc_b1 = histo_dict_uncTotal["jet1"]["b"].GetBinContent(binx+1,biny+1)
            Total_Unc_b2 = histo_dict_uncTotal["jet2"]["b"].GetBinContent(binx+1,biny+1)
            Total_Unc_b3 = histo_dict_uncTotal["jet3"]["b"].GetBinContent(binx+1,biny+1)
            Total_Unc_c1 = histo_dict_uncTotal["jet1"]["c"].GetBinContent(binx+1,biny+1)
            Total_Unc_c2 = histo_dict_uncTotal["jet2"]["c"].GetBinContent(binx+1,biny+1)
            Total_Unc_c3 = histo_dict_uncTotal["jet3"]["c"].GetBinContent(binx+1,biny+1)
            Total_Unc_l1 = histo_dict_uncTotal["jet1"]["l"].GetBinContent(binx+1,biny+1)
            Total_Unc_l2 = histo_dict_uncTotal["jet2"]["l"].GetBinContent(binx+1,biny+1)
            Total_Unc_l3 = histo_dict_uncTotal["jet3"]["l"].GetBinContent(binx+1,biny+1)

            stat_Unc_d1 = datahisto_dict["jet1"].GetBinError(binx+1,biny+1)
            stat_Unc_d2 = datahisto_dict["jet2"].GetBinError(binx+1,biny+1)
            stat_Unc_d3 = datahisto_dict["jet3"].GetBinError(binx+1,biny+1)

#            inital_guess = np.average([float(N_Data_1)/float(N_MC_b1+N_MC_c1+ N_MC_l1), float(N_Data_2)/float(N_MC_b2+N_MC_c2+ N_MC_l2), float(N_Data_3)/float(N_MC_b3+N_MC_c3+ N_MC_l3)],weights=np.asarray([N_Data_1,N_Data_2,N_Data_3]))
            inital_guess = 1.
            SFs_result = np.asarray([inital_guess,inital_guess,inital_guess])

            convergence_dict[(binx,biny)]["SFb"].append(SFs_result[0])
            convergence_dict[(binx,biny)]["SFc"].append(SFs_result[1])
            convergence_dict[(binx,biny)]["SFl"].append(SFs_result[2])


            def chi2_b(SFs):
                N_Data_b1 = N_Data_1 - SFs_result[1]*N_MC_c1 - SFs_result[2]*N_MC_l1
                if N_Data_b1<=0: N_Data_b1 = 1
                # return float(pow(SFs[0]*N_MC_b1 -(N_Data_b1) ,2))/float((SFs[0]*N_MC_b1)**2)#  +  frac_b2*float(pow(SFs[0]*N_MC_b2 -(N_Data_b2) ,2))/float(N_Data_b2) +  frac_b3*float(pow(SFs[0]*N_MC_b3 -(N_Data_b3),2))/float(N_Data_b3)
                return float(pow(SFs[0]*N_MC_b1 -(N_Data_b1) ,2))/float(N_Data_1)

            def chi2_c(SFs):
                N_Data_c2 = N_Data_2 - SFs_result[0]*N_MC_b2 - SFs_result[2]*N_MC_l2
                if N_Data_c2<=0: N_Data_c2 = 1
                # return float(pow(SFs[1]*N_MC_c2 -(N_Data_c2) ,2))/float((SFs[1]*N_MC_c2)**2)# +  frac_c3*float(pow(SFs[1]*N_MC_c3 -(N_Data_c3) ,2))/float(N_Data_c3)
                return float(pow(SFs[1]*N_MC_c2 -(N_Data_c2) ,2))/float(N_Data_2)

            def chi2_l(SFs):
                N_Data_l3 = N_Data_3 - SFs_result[0]*N_MC_b3 - SFs_result[1]*N_MC_c3
                if N_Data_l3<=0: N_Data_l3 = 1
                # return float(pow(SFs[2]*N_MC_l3 -(N_Data_l3) ,2))/float((SFs[2]*N_MC_l3)**2)
                return float(pow(SFs[2]*N_MC_l3 -(N_Data_l3) ,2))/float(N_Data_3)

            def chi2(SFs):
    #             return chi2_b(SFs) + chi2_l(SFs)
                # return float(pow(SFs[0]*N_MC_b1 + SFs[1]*N_MC_c1 + SFs[2]*N_MC_l1 - N_Data_1,2))/float(N_Data_1)  +  float(pow(SFs[0]*N_MC_b2 + SFs[1]*N_MC_c2 + SFs[2]*N_MC_l2 - N_Data_2,2))/float(N_Data_2)  +  float(pow(SFs[0]*N_MC_b3 + SFs[1]*N_MC_c3 + SFs[2]*N_MC_l3 - N_Data_3,2))/float(N_Data_3)
                return float(pow(SFs[0]*N_MC_b1 + SFs[1]*N_MC_c1 + SFs[2]*N_MC_l1 - N_Data_1,2))/float(N_Data_1)  +  float(pow(SFs[0]*N_MC_b2 + SFs[1]*N_MC_c2 + SFs[2]*N_MC_l2 - N_Data_2,2))/float(N_Data_2)  +  float(pow(SFs[0]*N_MC_b3 + SFs[1]*N_MC_c3 + SFs[2]*N_MC_l3 - N_Data_3,2))/float(N_Data_3)


            print N_MC_b1,N_MC_c1, N_MC_l1,N_MC_b1+N_MC_c1+ N_MC_l1, N_Data_1
            print N_MC_b2,N_MC_c2, N_MC_l2,N_MC_b2+N_MC_c2+ N_MC_l2, N_Data_2
            print N_MC_b3,N_MC_c3, N_MC_l3,N_MC_b3+N_MC_c3+ N_MC_l3, N_Data_3


            perfCanvas = ROOT.TCanvas("perf","perf",600,600)

            chist = ROOT.TH1F("c","c",10,-5,5)
            bhist = ROOT.TH1F("b","b",10,-5,5)
            lhist = ROOT.TH1F("l","l",10,-5,5)
            dhist = ROOT.TH1F("d","d",10,-5,5)
            chist.Sumw2()
            bhist.Sumw2()
            lhist.Sumw2()
            dhist.Sumw2()

            chist.SetBinContent(2,N_MC_c1)
            chist.SetBinContent(3,N_MC_c2)
            chist.SetBinContent(4,N_MC_c3)
            chist.SetBinError(2,Total_Unc_c1)
            chist.SetBinError(3,Total_Unc_c2)
            chist.SetBinError(4,Total_Unc_c3)
            chist.SetFillColor(ROOT.kCyan)

            bhist.SetBinContent(2,N_MC_b1)
            bhist.SetBinContent(3,N_MC_b2)
            bhist.SetBinContent(4,N_MC_b3)
            bhist.SetBinError(2,Total_Unc_b1)
            bhist.SetBinError(3,Total_Unc_b2)
            bhist.SetBinError(4,Total_Unc_b3)
            bhist.SetFillColor(ROOT.kMagenta)

            lhist.SetBinContent(2,N_MC_l1)
            lhist.SetBinContent(3,N_MC_l2)
            lhist.SetBinContent(4,N_MC_l3)
            lhist.SetBinError(2,Total_Unc_l1)
            lhist.SetBinError(3,Total_Unc_l2)
            lhist.SetBinError(4,Total_Unc_l3)
            lhist.SetFillColor(ROOT.kYellow+1)

            dhist.SetBinContent(2,N_Data_1)
            dhist.SetBinContent(3,N_Data_2)
            dhist.SetBinContent(4,N_Data_3)
            dhist.SetBinError(2,stat_Unc_d1)
            dhist.SetBinError(3,stat_Unc_d2)
            dhist.SetBinError(4,stat_Unc_d3)
            dhist.SetBinContent(7,N_Data_1)
            dhist.SetBinContent(8,N_Data_2)
            dhist.SetBinContent(9,N_Data_3)
            dhist.SetBinError(7,stat_Unc_d1)
            dhist.SetBinError(8,stat_Unc_d2)
            dhist.SetBinError(9,stat_Unc_d3)



            print SFs_result
            convergence_dict[(binx,biny)]["SFb"].append(SFs_result[0])
            convergence_dict[(binx,biny)]["SFc"].append(SFs_result[1])
            convergence_dict[(binx,biny)]["SFl"].append(SFs_result[2])


            improved = True
            i = 0
            max_niter = 2000
            verbose=False

            if not args.AdaptiveIteration:
                lPriority = 0
                bPriority = 1
                cPriority = 2
            else:
                bPurity = N_MC_b1/(N_MC_b1+N_MC_c1+N_MC_l1)
                cPurity = N_MC_c2/(N_MC_b2+N_MC_c2+N_MC_l2)
                lPurity = N_MC_l3/(N_MC_b3+N_MC_c3+N_MC_l3)

                purityList = sorted([bPurity,cPurity,lPurity],reverse=True)
                lPriority = purityList.index(lPurity)
                bPriority = purityList.index(bPurity)
                cPriority = purityList.index(cPurity)
            print "Order of iteration: l =", lPriority,", b = ", bPriority,", c = ",cPriority

            while improved:
                if verbose: print "Starting Iter %i"%i
                if verbose: print "INITIAL SFs: ",SFs_result
                if verbose: print "INITIAL Chi2: ",chi2_b(SFs_result),chi2_c(SFs_result),chi2_l(SFs_result)
                previous_SF = deepcopy(SFs_result)
                previous_chi2_b = chi2_b(SFs_result)
                previous_chi2_c = chi2_c(SFs_result)
                previous_chi2_l = chi2_l(SFs_result)

                for prio in range(3):
                    exec("improved_"+args.injectSF.lower()+" = True")
                    if prio == lPriority and args.injectSF.lower() != "l":
                        #
                        # First optimize SFl
                        #
                        improved_l = True
                        if verbose: print " PROCESSING FLAVOUR: UDSG"
                        minimizedSFl = minimize(chi2_l,SFs_result, bounds=np.c_[SFs_result-rate, SFs_result+rate])
                        if verbose: print "MINIMIZED SF:", minimizedSFl.x
                        SFs_result=minimizedSFl.x
                        if verbose: print "MINIMIZED CHI2: ", chi2_b(SFs_result),chi2_c(SFs_result),chi2_l(SFs_result)
                        if i != 0 and chi2_b(SFs_result)+chi2_c(SFs_result)+chi2_l(SFs_result)  >= previous_chi2_b +previous_chi2_c +previous_chi2_l:
                           SFs_result = previous_SF
                           if verbose: print "TOTAL CHI2 DID NOT IMPROVE!!!"
                           improved_l = False
                        else:
                            previous_SF = deepcopy(SFs_result)

                        convergence_dict[(binx,biny)]["SFl"].append(SFs_result[2])

                    if prio == bPriority and args.injectSF.lower() != "b":
                        #
                        # Then optimize SFb
                        #
                        improved_b = True
                        if verbose: print " PROCESSING FLAVOUR: B"
                        minimizedSFb = minimize(chi2_b,SFs_result, bounds=np.c_[SFs_result-rate, SFs_result+rate])
                        #print minimizedSFb
                        if verbose: print "MINIMIZED SF:", minimizedSFb.x
                        SFs_result=minimizedSFb.x
                        if verbose: print "MINIMIZED CHI2: ", chi2_b(SFs_result),chi2_c(SFs_result),chi2_l(SFs_result)
                        if i != 0 and chi2_b(SFs_result)+chi2_c(SFs_result)+chi2_l(SFs_result)  >= previous_chi2_b +previous_chi2_c +previous_chi2_l:
                            SFs_result = previous_SF
                            if verbose: print "TOTAL CHI2 DID NOT IMPROVE!!!"
                            improved_b = False
                        else:
                            previous_SF = deepcopy(SFs_result)


                        previous_chi2_b = chi2_b(SFs_result)
                        previous_chi2_c = chi2_c(SFs_result)
                        previous_chi2_l = chi2_l(SFs_result)

                        convergence_dict[(binx,biny)]["SFb"].append(SFs_result[0])

                    if prio == cPriority and args.injectSF.lower() != "c":
                        #
                        # Finally optimize SFc
                        #
                        improved_c = True
                        if verbose: print " PROCESSING FLAVOUR: C"
                        minimizedSFc = minimize(chi2_c,SFs_result, bounds=np.c_[SFs_result-rate, SFs_result+rate])
                        if verbose: print "MINIMIZED SF:", minimizedSFc.x
                        SFs_result=minimizedSFc.x
                        if verbose: print "MINIMIZED CHI2: ", chi2_b(SFs_result),chi2_c(SFs_result),chi2_l(SFs_result)
                        if i != 0 and chi2_b(SFs_result)+chi2_c(SFs_result)+chi2_l(SFs_result)  >= previous_chi2_b +previous_chi2_c +previous_chi2_l:
                            SFs_result = previous_SF
                            if verbose: print "TOTAL CHI2 DID NOT IMPROVE!!!"
                            improved_c = False
                        else:
                            previous_SF = deepcopy(SFs_result)

                        previous_chi2_b = chi2_b(SFs_result)
                        previous_chi2_c = chi2_c(SFs_result)
                        previous_chi2_l = chi2_l(SFs_result)

                        convergence_dict[(binx,biny)]["SFc"].append(SFs_result[1])


                if verbose: print "Ending Iter %i"%i,SFs_result, "chi2 = ", chi2_b(SFs_result)+chi2_c(SFs_result)+chi2_l(SFs_result)
                if verbose: print ""
                # if i != 0 and chi2_b(SFs_result[0])+chi2_c(SFs_result[1])+chi2_l(SFs_result[2])  > previous_chi2_b +previous_chi2_c +previous_chi2_l:
    #                 SFs_result = previous_SF
    #                 break

                i+=1
                if i > max_niter: break
                if not improved_b and not improved_c and not improved_l:
                    improved = False


            print "DONE in %i iterations"%i

            print "FINAL ", SFs_result, "Chi2: ",chi2_b(SFs_result),chi2_c(SFs_result),chi2_l(SFs_result)
            print "Jet1: Corrected # MC: ", SFs_result[0]*N_MC_b1+SFs_result[1]*N_MC_c1+SFs_result[2]*N_MC_l1, "# Data: ", N_Data_1
            print "Jet2: Corrected # MC: ", SFs_result[0]*N_MC_b2+SFs_result[1]*N_MC_c2+SFs_result[2]*N_MC_l2, "# Data: ", N_Data_2
            print "Jet3: Corrected # MC: ", SFs_result[0]*N_MC_b3+SFs_result[1]*N_MC_c3+SFs_result[2]*N_MC_l3, "# Data: ", N_Data_3

            ROOT.TGaxis.SetMaxDigits(3)
            chist.SetBinContent(7,N_MC_c1*SFs_result[1])
            chist.SetBinContent(8,N_MC_c2*SFs_result[1])
            chist.SetBinContent(9,N_MC_c3*SFs_result[1])
            chist.SetBinError(7,Total_Unc_c1*SFs_result[1]**0.5)
            chist.SetBinError(8,Total_Unc_c2*SFs_result[1]**0.5)
            chist.SetBinError(9,Total_Unc_c3*SFs_result[1]**0.5)

            bhist.SetBinContent(7,N_MC_b1*SFs_result[0])
            bhist.SetBinContent(8,N_MC_b2*SFs_result[0])
            bhist.SetBinContent(9,N_MC_b3*SFs_result[0])
            bhist.SetBinError(7,Total_Unc_b1*SFs_result[0]**0.5)
            bhist.SetBinError(8,Total_Unc_b2*SFs_result[0]**0.5)
            bhist.SetBinError(9,Total_Unc_b3*SFs_result[0]**0.5)

            lhist.SetBinContent(7,N_MC_l1*SFs_result[2])
            lhist.SetBinContent(8,N_MC_l2*SFs_result[2])
            lhist.SetBinContent(9,N_MC_l3*SFs_result[2])
            lhist.SetBinError(7,Total_Unc_l1*SFs_result[2]**0.5)
            lhist.SetBinError(8,Total_Unc_l2*SFs_result[2]**0.5)
            lhist.SetBinError(9,Total_Unc_l3*SFs_result[2]**0.5)

            histoErr=chist.Clone()
            histoErr.Add(bhist)
            histoErr.Add(lhist)

            x1 = SFb_hist.GetXaxis().GetBinLowEdge(binx+1)
            x2 = SFb_hist.GetXaxis().GetBinUpEdge(binx+1)
            y1 = SFb_hist.GetYaxis().GetBinLowEdge(biny+1)
            y2 = SFb_hist.GetYaxis().GetBinUpEdge(biny+1)

            title=r"\text{CvsL} \in [%.1f,%.1f], \text{CvsB} \in [%.1f,%.1f]"%(x1,x2,y1,y2)
            if x1<0:
                title = "CvsL, CvsB = -1"

            StackP = ROOT.THStack("Stack","")
            StackP.Add(lhist)
            StackP.Add(bhist)
            StackP.Add(chist)

            dhist.SetMarkerColor(ROOT.kBlack)
            dhist.SetMarkerStyle(20)
            dhist.SetMarkerSize(1.5)
            dhist.SetLineColor(1)

            legend = ROOT.TLegend(0.45, 0.75, 0.55, .89,"")
            legend.SetFillStyle(1001)
            legend.SetTextSize(0.03)

            legend.AddEntry(chist,"c","f")
            legend.AddEntry(bhist,"b","f")
            legend.AddEntry(lhist,"l","f")
            legend.AddEntry(dhist,"Data","PL")

            dMax = dhist.GetMaximum()

            # ratioPlot = ROOT.TRatioPlot(StackP,dhist)

            StackP.SetMaximum(dMax*1.3)

            StackP.Draw("hist")
#            ratioPlot.Draw()
            histoErr.Draw("same e2")
            dhist.Draw("same p e")


            histoErr.SetFillColor(ROOT.kGray+3)
            histoErr.SetLineColor(ROOT.kGray+3)
            histoErr.SetMarkerSize(0)
            histoErr.SetFillStyle(3013)

            StackP.GetXaxis().SetBinLabel(2,r"t\bar{t} (b)")
            StackP.GetXaxis().SetBinLabel(3,"W+c")
            StackP.GetXaxis().SetBinLabel(4,"DY+l")

            StackP.GetXaxis().SetBinLabel(7,r"t\bar{t} (b)")
            StackP.GetXaxis().SetBinLabel(8,"W+c")
            StackP.GetXaxis().SetBinLabel(9,"DY+l")

            StackP.GetXaxis().SetLabelSize(0.05)
            StackP.GetYaxis().SetTitle("Events")

            vLine = ROOT.TLine()
            vLine.SetLineWidth(1)
            vLine.DrawLineNDC(0.5,0.1,0.5,0.9)
            legend.Draw()

            titleText=ROOT.TLatex()
            titleText.SetTextSize(0.045)
            titleText.SetTextAlign(22)
            titleText.DrawLatexNDC(0.3,0.85, "Pre-fit")
            titleText.DrawLatexNDC(0.7,0.85, "Post-fit")
            headText=ROOT.TLatex()
            headText.SetTextSize(0.05)
            headText.SetTextAlign(21)
            headText.DrawLatexNDC(0.5,0.92, title)

            perfCanvas.SaveAs(current_dir+"/fitPlots/fitPlot"+str(binx)+"_biny_"+str(biny)+".png")
            ROOT.gPad.SetLogy()
            StackP.SetMaximum(dMax*5)
            StackP.SetMinimum(101)
            perfCanvas.SaveAs(current_dir+"/fitPlots/fitPlot_log_"+str(binx)+"_biny_"+str(biny)+".png")



            xvalues_SFb = np.arange(SFs_result[0]-1,SFs_result[0]+1,0.001)
            yvalues_SFb = np.asarray([chi2(np.asarray([i,SFs_result[1],SFs_result[2]])) - chi2(SFs_result) - 1  for i in xvalues_SFb])
            # plt.plot(xvalues_SFb,yvalues_SFb)
#             plt.plot(xvalues_SFb,np.zeros(len(xvalues_SFb)))
#             plt.show()
            ysign_SFb = np.sign(yvalues_SFb)
            signchange_SFb = ((np.roll(ysign_SFb, 1) - ysign_SFb) != 0).astype(int)
            print xvalues_SFb[signchange_SFb == 1]
            if len(xvalues_SFb[signchange_SFb == 1]) == 2: fit_unc_SFb = (xvalues_SFb[signchange_SFb == 1][1] - xvalues_SFb[signchange_SFb == 1][0])/2.
            else: fit_unc_SFb = 1.

            xvalues_SFc = np.arange(SFs_result[1]-1,SFs_result[1]+1,0.001)
            yvalues_SFc = np.asarray([chi2(np.asarray([SFs_result[0],i,SFs_result[2]])) - chi2(SFs_result) - 1 for i in xvalues_SFc])
            ysign_SFc = np.sign(yvalues_SFc)
            signchange_SFc = ((np.roll(ysign_SFc, 1) - ysign_SFc) != 0).astype(int)
            if len(xvalues_SFc[signchange_SFc == 1]) == 2: fit_unc_SFc = (xvalues_SFc[signchange_SFc == 1][1] - xvalues_SFc[signchange_SFc == 1][0])/2.
            else: fit_unc_SFc = 1.

            xvalues_SFl = np.arange(SFs_result[2]-1,SFs_result[2]+1,0.001)
            yvalues_SFl = np.asarray([chi2(np.asarray([SFs_result[0],SFs_result[1],i])) - chi2(SFs_result) - 1 for i in xvalues_SFl])
            ysign_SFl = np.sign(yvalues_SFl)
            signchange_SFl = ((np.roll(ysign_SFl, 1) - ysign_SFl) != 0).astype(int)
            if len(xvalues_SFl[signchange_SFl == 1]) == 2: fit_unc_SFl = (xvalues_SFl[signchange_SFl == 1][1] - xvalues_SFl[signchange_SFl == 1][0])/2.
            else: fit_unc_SFl = 1.

            print "SFb = ",SFs_result[0], " +- ", fit_unc_SFb
            print "SFc = ",SFs_result[1], " +- ", fit_unc_SFc
            print "SFl = ",SFs_result[2], " +- ", fit_unc_SFl
            # print "SFb = ",SFs_result[0], " +- ", sqrt(result.hess_inv[0][0])
#             print "SFc = ",SFs_result[1], " +- ", sqrt(result.hess_inv[1][1])
#             print "SFl = ",SFs_result[2], " +- ", sqrt(result.hess_inv[2][2])

            fit_unc_dict[(binx+1,biny+1)] = [fit_unc_SFb,fit_unc_SFc,fit_unc_SFl]

            print "FINAL CHI2: ",chi2(SFs_result)
            #sys.exit(1)


            # SFb_hist.SetBinContent(binx+1,biny+1,histo_dict["jet1"]["b"].GetBinContent(binx+1,biny+1)*SFs_result[0])
            # SFc_hist.SetBinContent(binx+1,biny+1,histo_dict["jet2"]["c"].GetBinContent(binx+1,biny+1)*SFs_result[1])
            # SFl_hist.SetBinContent(binx+1,biny+1,histo_dict["jet3"]["l"].GetBinContent(binx+1,biny+1)*SFs_result[2])

            SFb_hist.SetBinContent(binx+1,biny+1,SFs_result[0])
            SFc_hist.SetBinContent(binx+1,biny+1,SFs_result[1])
            SFl_hist.SetBinContent(binx+1,biny+1,SFs_result[2])

            chi2b_hist.SetBinContent(binx+1,biny+1,chi2_b(SFs_result))
            chi2c_hist.SetBinContent(binx+1,biny+1,chi2_c(SFs_result))
            chi2l_hist.SetBinContent(binx+1,biny+1,chi2_l(SFs_result))
            chi2_hist.SetBinContent(binx+1,biny+1,chi2(SFs_result))


            if chi2(SFs_result) > 1e-4*(N_Data_1+N_Data_2+N_Data_3):
                x1 = SFb_hist.GetXaxis().GetBinLowEdge(binx+1)
                x2 = SFb_hist.GetXaxis().GetBinUpEdge(binx+1)
                y1 = SFb_hist.GetYaxis().GetBinLowEdge(biny+1)
                y2 = SFb_hist.GetYaxis().GetBinUpEdge(biny+1)
                b = ROOT.TBox(x1, y1, x2, y2)
                b.SetFillStyle(0)
                b.SetLineWidth(4)
                b.SetLineColor(ROOT.kRed)
                boxes.append(b.Clone())

            if chi2_b(SFs_result) > 1e-2*N_Data_1:
                x1 = SFb_hist.GetXaxis().GetBinLowEdge(binx+1)
                x2 = SFb_hist.GetXaxis().GetBinUpEdge(binx+1)
                y1 = SFb_hist.GetYaxis().GetBinLowEdge(biny+1)
                y2 = SFb_hist.GetYaxis().GetBinUpEdge(biny+1)
                b = ROOT.TBox(x1, y1, x2, y2)
                b.SetFillStyle(0)
                b.SetLineWidth(4)
                b.SetLineColor(ROOT.kRed)
                boxesb.append(b.Clone())
            if chi2_c(SFs_result) > 1e-2*N_Data_2:
                x1 = SFc_hist.GetXaxis().GetBinLowEdge(binx+1)
                x2 = SFc_hist.GetXaxis().GetBinUpEdge(binx+1)
                y1 = SFc_hist.GetYaxis().GetBinLowEdge(biny+1)
                y2 = SFc_hist.GetYaxis().GetBinUpEdge(biny+1)
                b = ROOT.TBox(x1, y1, x2, y2)
                b.SetFillStyle(0)
                b.SetLineWidth(4)
                b.SetLineColor(ROOT.kRed)
                boxesc.append(b.Clone())
            if chi2_l(SFs_result) > 1e-2*N_Data_3:
                x1 = SFl_hist.GetXaxis().GetBinLowEdge(binx+1)
                x2 = SFl_hist.GetXaxis().GetBinUpEdge(binx+1)
                y1 = SFl_hist.GetYaxis().GetBinLowEdge(biny+1)
                y2 = SFl_hist.GetYaxis().GetBinUpEdge(biny+1)
                b = ROOT.TBox(x1, y1, x2, y2)
                b.SetFillStyle(0)
                b.SetLineWidth(4)
                b.SetLineColor(ROOT.kRed)
                boxesl.append(b.Clone())

            # uncertainties
            # def unc_b(SFb):
    #             return chi2_b([SFb,SFs_result[1],SFs_result[2]]) - chi2_b(SFs_result) - 1
    #         zeros_b_low = fsolve(unc_b,SFs_result[0]-0.5)
    #         zeros_b_high = fsolve(unc_b,SFs_result[0]+0.5)
    #         print "unc SFb = ",SFs_result[0], "- ", SFs_result[0]-zeros_b_low[0]," + ", zeros_b_high[0]-SFs_result[0]
    #
            print ""
            print "********************"
            print ""

    # SFb_hist.Divide(histo_dict["jet1"]["b"])
    # SFc_hist.Divide(histo_dict["jet2"]["c"])
    # SFl_hist.Divide(histo_dict["jet3"]["l"])


     # Add fit uncertainty
    for binx in range(histo_dict["jet1"]["b"].GetNbinsX()):
        for biny in range(histo_dict["jet1"]["b"].GetNbinsY()):
            if skip1bins and (binx==0 or biny==0) and not (binx==0 and biny==0): continue
            # SFb_hist.SetBinError(binx+1,biny+1,sqrt(SFb_hist.GetBinError(binx+1,biny+1)**2 + fit_unc_dict[(binx+1,biny+1)][0]**2))
            # SFc_hist.SetBinError(binx+1,biny+1,sqrt(SFc_hist.GetBinError(binx+1,biny+1)**2 + fit_unc_dict[(binx+1,biny+1)][1]**2))
            # SFl_hist.SetBinError(binx+1,biny+1,sqrt(SFl_hist.GetBinError(binx+1,biny+1)**2 + fit_unc_dict[(binx+1,biny+1)][2]**2))
            SFb_hist.SetBinError(binx+1,biny+1,fit_unc_dict[(binx+1,biny+1)][0])
            SFc_hist.SetBinError(binx+1,biny+1,fit_unc_dict[(binx+1,biny+1)][1])
            SFl_hist.SetBinError(binx+1,biny+1,fit_unc_dict[(binx+1,biny+1)][2])


    ROOT.gStyle.SetPaintTextFormat("4.3f")

    cSFb = ROOT.TCanvas("cSFb","cSFb",800,800)
    #cSFb.SetMargin(0,0,0,0)
    #cSFb.Divide(3)
    #cSFb.cd(1)
    ROOT.gPad.SetMargin(0.13,0.18,0.11,0.17)
    SFb_hist.SetMarkerSize(1.5)
    SFb_hist.GetXaxis().CenterTitle()
    SFb_hist.GetXaxis().SetTitleSize(0.05)
    SFb_hist.GetXaxis().SetTitleOffset(1.)
    SFb_hist.GetYaxis().CenterTitle()
    SFb_hist.GetYaxis().SetTitleSize(0.05)
    SFb_hist.GetYaxis().SetTitleOffset(1.2)
    SFb_hist.GetZaxis().SetRangeUser(0.,2.)
    SFb_hist.GetZaxis().CenterTitle()
    SFb_hist.GetZaxis().SetTitleSize(0.05)
    SFb_hist.GetZaxis().SetTitleOffset(1.2)
    SFb_hist.Draw("COLZ TEXT E")
    box = ROOT.TPaveText(custom_bins_CvsB_jet1[0],1,1,1+.15*(custom_bins_CvsB_jet1[-1]-custom_bins_CvsB_jet1[0]))
    box.SetBorderSize(1)
    box.SetFillStyle(0)
    box.Draw("same")
    for b in boxesb:
        b.Draw("same")
    latex_cms = ROOT.TLatex()
    latex_cms.SetTextFont(42)
    latex_cms.SetTextSize(0.04)
    latex_cms.SetTextAlign(11)
    latex_cms.DrawLatexNDC(0.15,0.9,"#bf{CMS} #it{Preliminary}")
    latex_cms.DrawLatexNDC(0.15,0.85,"Wc/TTb/DYl selection")
    latex_cms.DrawLatexNDC(0.65,0.9,"DeepCSV")
    latex_cms.DrawLatexNDC(0.67,0.85,"c-tagger")
    latex_cms.DrawLatexNDC(0.6,0.95,"35.9 fb^{-1} (13 TeV)")
    cSFb.SaveAs(current_dir+"/SFb_cTag.png")
#    cSFb.SaveAs(current_dir+"/SFb_cTag.pdf")
#    cSFb.SaveAs(current_dir+"/SFb_cTag.C")

    cSFc = ROOT.TCanvas("cSFc","cSFc",1200,1200)
    #cSFc.SetMargin(0,0,0,0)
    #cSFc.Divide(3)
    #cSFc.cd(1)
    ROOT.gPad.SetMargin(0.13,0.18,0.11,0.17)
    SFc_hist.SetMarkerSize(1.5)
    SFc_hist.GetXaxis().CenterTitle()
    SFc_hist.GetXaxis().SetTitleSize(0.05)
    SFc_hist.GetXaxis().SetTitleOffset(1.)
    SFc_hist.GetYaxis().CenterTitle()
    SFc_hist.GetYaxis().SetTitleSize(0.05)
    SFc_hist.GetYaxis().SetTitleOffset(1.2)
    SFc_hist.GetZaxis().SetRangeUser(0.,2.)
    SFc_hist.GetZaxis().CenterTitle()
    SFc_hist.GetZaxis().SetTitleSize(0.05)
    SFc_hist.GetZaxis().SetTitleOffset(1.2)
    SFc_hist.Draw("COLZ TEXT E")
    #box = ROOT.TPaveText(0.,1,1,1.15)
    #box.SetBorderSize(1)
    #box.SetFillStyle(0)
    box.Draw("same")
    for b in boxesc:
        b.Draw("same")
    latex_cms = ROOT.TLatex()
    latex_cms.SetTextFont(42)
    latex_cms.SetTextSize(0.04)
    latex_cms.SetTextAlign(11)
    latex_cms.DrawLatexNDC(0.15,0.9,"#bf{CMS} #it{Preliminary}")
    latex_cms.DrawLatexNDC(0.15,0.85,"Wc/TTb/DYl selection")
    latex_cms.DrawLatexNDC(0.65,0.9,"DeepCSV")
    latex_cms.DrawLatexNDC(0.67,0.85,"c-tagger")
    latex_cms.DrawLatexNDC(0.6,0.95,"35.9 fb^{-1} (13 TeV)")
    cSFc.SaveAs(current_dir+"/SFc_cTag.png")
#    cSFc.SaveAs(current_dir+"/SFc_cTag.pdf")
#    cSFc.SaveAs(current_dir+"/SFc_cTag.C")

    cSFl = ROOT.TCanvas("cSFl","cSFl",1200,1200)
    #cSFl.SetMargin(0,0,0,0)
    #cSFl.Divide(3)
    #cSFl.cd(1)
    ROOT.gPad.SetMargin(0.13,0.18,0.11,0.17)
    SFl_hist.SetMarkerSize(1.5)
    SFl_hist.GetXaxis().CenterTitle()
    SFl_hist.GetXaxis().SetTitleSize(0.05)
    SFl_hist.GetXaxis().SetTitleOffset(1.)
    SFl_hist.GetYaxis().CenterTitle()
    SFl_hist.GetYaxis().SetTitleSize(0.05)
    SFl_hist.GetYaxis().SetTitleOffset(1.2)
    SFl_hist.GetZaxis().SetRangeUser(0.,2.)
    SFl_hist.GetZaxis().CenterTitle()
    SFl_hist.GetZaxis().SetTitleSize(0.05)
    SFl_hist.GetZaxis().SetTitleOffset(1.2)
    SFl_hist.Draw("COLZ TEXT E")
    #box = ROOT.TPaveText(0.,1,1,1.15)
    #box.SetBorderSize(1)
    #box.SetFillStyle(0)
    box.Draw("same")
    for b in boxesl:
        b.Draw("same")
    latex_cms = ROOT.TLatex()
    latex_cms.SetTextFont(42)
    latex_cms.SetTextSize(0.04)
    latex_cms.SetTextAlign(11)
    latex_cms.DrawLatexNDC(0.15,0.9,"#bf{CMS} #it{Preliminary}")
    latex_cms.DrawLatexNDC(0.15,0.85,"Wc/TTb/DYl selection")
    latex_cms.DrawLatexNDC(0.65,0.9,"DeepCSV")
    latex_cms.DrawLatexNDC(0.67,0.85,"c-tagger")
    latex_cms.DrawLatexNDC(0.6,0.95,"35.9 fb^{-1} (13 TeV)")
    cSFl.SaveAs(current_dir+"/SFl_cTag.png")
#    cSFl.SaveAs(current_dir+"/SFl_cTag.pdf")
#    cSFl.SaveAs(current_dir+"/SFl_cTag.C")

   # cSFb.cd(2)
#    ROOT.gPad.SetMargin(0.2,0.2,0.1,0.2)
#    SFc_hist.SetMarkerSize(1.5)
#    SFc_hist.GetXaxis().CenterTitle()
#    SFc_hist.GetXaxis().SetTitleSize(0.05)
#    SFc_hist.GetXaxis().SetTitleOffset(1.2)
#    SFc_hist.GetYaxis().CenterTitle()
#    SFc_hist.GetYaxis().SetTitleSize(0.05)
#    SFc_hist.GetYaxis().SetTitleOffset(1.2)
#    SFc_hist.GetZaxis().SetRangeUser(0.,2.)
#    SFc_hist.GetZaxis().CenterTitle()
#    SFc_hist.GetZaxis().SetTitleSize(0.05)
#    SFc_hist.GetZaxis().SetTitleOffset(1.2)
#    SFc_hist.Draw("COLZ TEXT E")
#    cSFb.cd(3)
#    ROOT.gPad.SetMargin(0.2,0.2,0.1,0.2)
#    SFl_hist.SetMarkerSize(1.5)
#    SFl_hist.GetXaxis().CenterTitle()
#    SFl_hist.GetXaxis().SetTitleSize(0.05)
#    SFl_hist.GetXaxis().SetTitleOffset(1.2)
#    SFl_hist.GetYaxis().CenterTitle()
#    SFl_hist.GetYaxis().SetTitleSize(0.05)
#    SFl_hist.GetYaxis().SetTitleOffset(1.2)
#    SFl_hist.GetZaxis().SetRangeUser(0.,2.)
#    SFl_hist.GetZaxis().CenterTitle()
#    SFl_hist.GetZaxis().SetTitleSize(0.05)
#    SFl_hist.GetZaxis().SetTitleOffset(1.2)
#    SFl_hist.Draw("COLZ TEXT E")
    #cSFb.SaveAs(current_dir+"/SFs_cTag.png")
    #cSFb.SaveAs(current_dir+"/SFs_cTag.pdf")

    outf = ROOT.TFile(current_dir+"/cTag_SFs_80X_Spandan.root","RECREATE")
    outf.cd()

    if skip1bins:
        for binx in range(histo_dict["jet1"]["b"].GetNbinsX()):
            for biny in range(histo_dict["jet1"]["b"].GetNbinsY()):
                if (binx==0 or biny==0) and not (binx==0 and biny==0):
                    SFl_hist.SetBinContent(binx+1,biny+1,SFl_hist.GetBinContent(1,1))
                    SFb_hist.SetBinContent(binx+1,biny+1,SFb_hist.GetBinContent(1,1))
                    SFc_hist.SetBinContent(binx+1,biny+1,SFc_hist.GetBinContent(1,1))
                    SFl_hist.SetBinError(binx+1,biny+1,SFl_hist.GetBinError(1,1))
                    SFb_hist.SetBinError(binx+1,biny+1,SFb_hist.GetBinError(1,1))
                    SFc_hist.SetBinError(binx+1,biny+1,SFc_hist.GetBinError(1,1))

        for binx in range(histo_dict["jet1"]["b"].GetNbinsX()+1):
            SFl_hist.SetBinContent(binx,0,SFl_hist.GetBinContent(1,1))
            SFb_hist.SetBinContent(binx,0,SFb_hist.GetBinContent(1,1))
            SFc_hist.SetBinContent(binx,0,SFc_hist.GetBinContent(1,1))
            SFl_hist.SetBinError(binx,0,SFl_hist.GetBinError(1,1))
            SFb_hist.SetBinError(binx,0,SFb_hist.GetBinError(1,1))
            SFc_hist.SetBinError(binx,0,SFc_hist.GetBinError(1,1))
        for biny in range(histo_dict["jet1"]["b"].GetNbinsY()+1):
            SFl_hist.SetBinContent(0,biny,SFl_hist.GetBinContent(1,1))
            SFb_hist.SetBinContent(0,biny,SFb_hist.GetBinContent(1,1))
            SFc_hist.SetBinContent(0,biny,SFc_hist.GetBinContent(1,1))
            SFl_hist.SetBinError(0,biny,SFl_hist.GetBinError(1,1))
            SFb_hist.SetBinError(0,biny,SFb_hist.GetBinError(1,1))
            SFc_hist.SetBinError(0,biny,SFc_hist.GetBinError(1,1))
    SFl_hist.Write()
    SFb_hist.Write()
    SFc_hist.Write()

    outf.Close()


    if not os.path.isdir(current_dir+"/convergencePlots"): os.mkdir(current_dir+"/convergencePlots")

    for (binx,biny), SF_dict in convergence_dict.iteritems():
        cc = ROOT.TCanvas("cc","cc",800,400)
        niter = np.array([float(i) for i in range(len(SF_dict["SFb"]))])
        SFb_list = np.array(SF_dict["SFb"])
        SFc_list = np.array(SF_dict["SFc"])
        SFl_list = np.array(SF_dict["SFl"])
        graph_b = ROOT.TGraph(len(niter),niter,SFb_list)
        graph_c = ROOT.TGraph(len(niter),niter,SFc_list)
        graph_l = ROOT.TGraph(len(niter),niter,SFl_list)
        mg = ROOT.TMultiGraph()
        mg.Add(graph_b)
        mg.Add(graph_c)
        mg.Add(graph_l)

        cc.cd()
        ROOT.gPad.SetMargin(0.12,0.25,0.15,0.1)
        mg.Draw("AL")
        graph_b.SetLineColor(2)
        graph_b.SetLineWidth(2)
        graph_c.SetLineColor(3)
        graph_c.SetLineWidth(2)
        graph_l.SetLineColor(4)
        graph_l.SetLineWidth(2)
        mg.GetXaxis().SetTitle("iteration")
        mg.GetXaxis().SetTitleSize(0.07)
        mg.GetXaxis().SetTitleOffset(0.95)
        mg.GetXaxis().SetLabelSize(0.06)
        mg.GetYaxis().SetTitle("SF")
        mg.GetYaxis().SetTitleSize(0.07)
        mg.GetYaxis().SetTitleOffset(0.9)
        mg.GetYaxis().SetLabelSize(0.06)
        mg.GetYaxis().CenterTitle()
        l = ROOT.TLegend(0.76,0.15,0.95,0.7)
        l.SetBorderSize(0)
        #l.SetHeader("bin_CvsL: "+str(binx+1)+", bin_CvsB: "+str(biny+1))
        l.AddEntry(graph_b,"b jets","l")
        l.AddEntry(graph_c,"c jets","l")
        l.AddEntry(graph_l,"l jets","l")
        l.Draw("same")
        latex = ROOT.TLatex()
        latex.SetTextFont(42)
        latex.SetTextSize(0.07)
        latex.DrawLatexNDC(0.77,0.83,"bin CvsL: "+str(binx+1))
        latex.DrawLatexNDC(0.77,0.73,"bin CvsB: "+str(biny+1))
        latex.DrawLatexNDC(0.16,0.83,"#bf{CMS} #it{Preliminary}")
        latex.DrawLatexNDC(0.56,0.92,"35.9 fb^{-1} (13 TeV)")
        cc.Update()
        cc.SaveAs(current_dir+"/convergencePlots/convergence_binx_"+str(binx)+"_biny_"+str(biny)+".png")
        del graph_b
        del graph_c
        del graph_l
        del mg

    def saveHist(hist,outName):
        c = ROOT.TCanvas("c","c",1200,1200)
        c.SetLogz()
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
        c.SaveAs(current_dir+"/"+outName+".png")

    ROOT.gStyle.SetPaintTextFormat(".1e")

    saveHist(chi2b_hist,"chi2b")
    saveHist(chi2c_hist,"chi2c")
    saveHist(chi2l_hist,"chi2l")
    saveHist(chi2_hist,"chi2")

    hor=600
    ver=600
    result = Image.new("RGB", (hor*5, ver*5), color=(255,255,255,0))
    for i in range(1,6):
        for j in range(1,6):
            img = Image.open(current_dir+"/fitPlots/fitPlot_log_%d_biny_%d.png"%(i,j))
    #            img.thumbnail((hor, ver), Image.ANTIALIAS)
            x = (i-1)*hor
            y = (5-j)*ver
            result.paste(img, (x, y))
    result.save(current_dir+"/fitPlots/fitPlot_log_grid.png")

sys.exit(len(boxesb)+len(boxesc)+len(boxesl))
