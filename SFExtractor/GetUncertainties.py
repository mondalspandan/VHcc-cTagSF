from ROOT import *
import os, sys, json, argparse
import numpy as np
from array import array
from math import sqrt
from plotTools import plotSFs
from scipy.interpolate import interp1d

gROOT.SetBatch(1)
gStyle.SetOptStat(0)
gErrorIgnoreLevel = 4001

parser = argparse.ArgumentParser("Second step to extract SFs")
parser.add_argument('-i', '--inputdir',type=str,default="")
parser.add_argument('-skip','--skipDist',type=str,default="CvsB")
parser.add_argument('-out','--outputSuffix',type=str,default="")
parser.add_argument('-scansuff','--scanSuffix',type=str,default="_5_1_0.020")
parser.add_argument('-noUnc','--noUnc',action="store_true",default=False)
parser.add_argument('-symm','--symm',action="store_true",default=False)
#parser.add_argument('-scan','--scanResults',action="store_true",default=False)
args = parser.parse_args()
print args

interp = False
symmetrize = False

if __name__ == '__main__': maindir = args.inputdir

allSFDict = {}
allStatUncDict = {}

def interpolateHist(hist,histunc):
    blocksize = 5
    nbins = hist.GetNbinsX()
    delta = 1e-6
    
    for iy in range(1,hist.GetNbinsY()+1,blocksize):
        xvals = []
        xerrs = []
        noms = []
        ups = []
        downs = []
        lastxlow = 0
        for ix in range(1,nbins+2):
            nomval = hist.GetBinContent(ix,iy)
            upunc = histunc.GetBinContent(ix,iy)
            downunc = upunc

            if ix==1:
                oldnom = nomval
                oldup = upunc
                olddown = downunc

            xlow = hist.GetXaxis().GetBinLowEdge(ix) 
            xhigh = hist.GetXaxis().GetBinLowEdge(ix+1)
            if abs(oldnom-nomval)>delta         \
                or abs(oldup-upunc)>delta       \
                or abs(olddown-downunc)>delta   \
                or xlow-lastxlow >= 0.1         \
                or ix == nbins+1:

                xval = (lastxlow+xlow)/2
                xerr = (xlow-lastxlow)/2
                xvals.append(xval)
                xerrs.append(xerr)
                noms.append(oldnom)
                ups.append(oldup)
                downs.append(olddown)
                lastxlow = xlow
                oldnom = nomval
                oldup = upunc
                olddown = downunc

        interpx,interpy = [],[]
        for inom, nom in enumerate(noms):
            if nom == 1 and ups[inom] == 1 and downs[inom] == 1:
                pass
            else:
                interpx.append(xvals[inom])
                interpy.append(nom)
        
        if len(interpx) <= 1 : continue
        interfunc = interp1d(interpx, interpy, fill_value="extrapolate")

        for ix in range(1,nbins+2):
            if hist.GetBinContent(ix,iy) == 1 and histunc.GetBinContent(ix,iy) == 1: continue
            xlow = hist.GetXaxis().GetBinLowEdge(ix) 
            xhigh = hist.GetXaxis().GetBinLowEdge(ix+1)
            xmid = (xlow+xhigh)/2
            yval = interfunc(xmid)
            for iiy in range(blocksize):
                hist.SetBinContent(ix,iy+iiy,yval)

    return hist

for subdir in sorted([i for i in os.listdir(maindir) if os.path.isdir(maindir+"/"+i)]):
    
    indir = maindir+"/"+subdir+"/results%s/"%args.scanSuffix
    if not os.path.isdir(indir) or len(os.listdir(indir)) == 0:
        print "Skipping %s/%s. Did you run the fit for this directory?"%(maindir,subdir)
        continue
    #print "Entering directory: "+indir
    
    systName = '_'.join(subdir.split("_")[2:])
    allSFDict[systName] = {}
    allStatUncDict[systName] = {}
    
    rootfiles = sorted([i for i in os.listdir(indir) if i.endswith(".root") and not "_unc" in i and not args.skipDist in i and not args.skipDist in i])
    
    for fl in rootfiles:
        rfl = TFile.Open(indir+fl,"READ")
        thishist = rfl.Get("SF")
        thishist.SetDirectory(0)
        allSFDict[systName][fl.rstrip(".root")] = thishist
        
        uncfl = TFile.Open(indir+fl.rstrip(".root")+"_unc.root","READ")
        thisunc = uncfl.Get("SF")
        thisunc.SetDirectory(0)
        allStatUncDict[systName][fl.rstrip(".root")] = thisunc

        if interp:
            allSFDict[systName][fl.rstrip(".root")] = interpolateHist(thishist,thisunc)

if args.skipDist=="CvsL": skipSuff = "CvsB"
else: skipSuff = "CvsL"

interptext = ""
if interp: interptext = "_interp"
symmtext = ""
if symmetrize: symmtext = "_symm"

outSFs = TFile.Open(maindir+"/ctagSF_2017_Spandan_%s_%s%s%s.root"%(skipSuff,args.outputSuffix,interptext,symmtext),"RECREATE")
UncDictUp = {}
UncDictDown = {}
SystOnlyUp = {}
SystOnlyDown = {}
StatUp = {}
StatDown = {}
 

def removeErrs(hist):
    hist.SetBinError(0,0,0.)
    for ix in range(1,hist.GetNbinsX()+1):
        for iy in range(1,hist.GetNbinsY()+1):        
            hist.SetBinError(ix,iy,0.)
    return hist

# First do statistical uncertainties
for SF in allSFDict["central"]:
    UncDictUp[SF] = allStatUncDict["central"][SF].Clone()
    SystOnlyUp[SF] = allStatUncDict["central"][SF].Clone()
    StatUp[SF] = allSFDict["central"][SF].Clone()
    StatDown[SF] = allSFDict["central"][SF].Clone()
    for ix in range(0,UncDictUp[SF].GetNbinsX()+1):
        for iy in range(0,UncDictUp[SF].GetNbinsY()+1):
            if (ix == 0 or iy == 0) and not (ix==0 and iy==0): continue
            #if ix ==5 and iy == 20: print SF, ix, iy, UncDictUp[SF].GetBinContent(ix,iy),allSFDict["central"][SF].GetBinContent(ix,iy)
            UncDictUp[SF].SetBinError(ix,iy,0.)
            SystOnlyUp[SF].SetBinContent(ix,iy,0.)
            SystOnlyUp[SF].SetBinError(ix,iy,0.)
            StatUp[SF].SetBinContent(ix,iy,allSFDict["central"][SF].GetBinContent(ix,iy)+UncDictUp[SF].GetBinContent(ix,iy))
            StatDown[SF].SetBinContent(ix,iy,max(0.,allSFDict["central"][SF].GetBinContent(ix,iy)-UncDictUp[SF].GetBinContent(ix,iy)))
    
    UncDictDown[SF] = UncDictUp[SF].Clone()
    SystOnlyDown[SF] = SystOnlyUp[SF].Clone()
    
    outSFs.cd()
    centralSF = removeErrs(allSFDict["central"][SF].Clone())
    thishist = SF.replace("DeepFlavCvsL","hist").replace("CvsL","hist")
    centralSF.SetNameTitle(thishist,thishist)
    centralSF.Write()    
    
for SF in sorted(allSFDict["central"]):
    StatUp[SF] = removeErrs(StatUp[SF])
    StatDown[SF] = removeErrs(StatDown[SF])
    thishist = SF.replace("DeepFlavCvsL","hist").replace("CvsL","hist")
    StatUp[SF].SetNameTitle(thishist+"_StatUp",thishist+"_StatUp")
    StatDown[SF].SetNameTitle(thishist+"_StatDown",thishist+"_StatDown")
    StatUp[SF].Write()
    StatDown[SF].Write()

#Now do systematics
for SF in sorted(allSFDict["central"]):
    centralSF = allSFDict["central"][SF]
    thishist = SF.replace("DeepFlavCvsL","hist").replace("CvsL","hist")    

    symmdiffdict = {}

    for syst in sorted(allSFDict):
        if syst == "central": continue
        systvar = removeErrs(allSFDict[syst][SF].Clone())
        
        for ix in range(0,centralSF.GetNbinsX()+1):
            for iy in range(0,centralSF.GetNbinsY()+1):
                if (ix == 0 or iy == 0) and not (ix==0 and iy==0): continue
                if centralSF.GetBinContent(ix,iy) == 1. and UncDictUp[SF].GetBinContent(ix,iy) == 1. and UncDictDown[SF].GetBinContent(ix,iy) == 1.:
                    systvar.SetBinContent(ix,iy,1.)
        
        outSFs.cd()
        systvar.SetNameTitle(thishist+"_"+syst.replace('_up','Up').replace('_down','Down'),thishist+"_"+syst.replace('_up','Up').replace('_down','Down'))
        systvar.Write()
        
        if symmetrize:
            if "up" in syst.lower():
                oppname = syst.replace("up","down").replace("Up","Down")
            elif "down" in syst.lower():
                oppname = syst.replace("down","up").replace("Down","Up")

            if oppname in symmdiffdict.keys(): oppexists = True
            else: 
                oppexists = False
                symmdiffdict[syst] = {}

            print SF,syst,oppname, oppexists

        for ix in range(0,centralSF.GetNbinsX()+1):
            for iy in range(0,centralSF.GetNbinsY()+1):
                if (ix == 0 or iy == 0) and not (ix==0 and iy==0): continue
                
                if centralSF.GetBinContent(ix,iy) == 1. and UncDictUp[SF].GetBinContent(ix,iy) == 1. and UncDictDown[SF].GetBinContent(ix,iy) == 1.: continue
                diff = systvar.GetBinContent(ix,iy) - centralSF.GetBinContent(ix,iy)

                if symmetrize and not oppexists:
                    symmdiffdict[syst][(ix,iy)] = diff
                
                if diff > 0:
                    oldUnc = UncDictUp[SF].GetBinContent(ix,iy)
                    oldUncSyst = SystOnlyUp[SF].GetBinContent(ix,iy)

                    #Symmetrize
                    doUsualStuff = True
                    if symmetrize and oppexists:
                        oldUncDown = UncDictDown[SF].GetBinContent(ix,iy)
                        oldUncSystDown = SystOnlyDown[SF].GetBinContent(ix,iy)                        
                        
                        oppdiff = symmdiffdict[oppname][(ix,iy)]
                        if oppdiff > 0:
                            if abs(diff) > abs(oppdiff):
                                newUnc = sqrt(oldUnc**2 - oppdiff**2 + diff**2)
                                newUncSyst = sqrt(oldUncSyst**2 - oppdiff**2 + diff**2)
                                UncDictUp[SF].SetBinContent(ix,iy,newUnc)
                                SystOnlyUp[SF].SetBinContent(ix,iy,newUncSyst)

                            newUncDown = sqrt(oldUncDown**2 + (abs(diff) - abs(oppdiff))**2)
                            newUncSystDown = sqrt(oldUncSystDown**2 + (abs(diff) - abs(oppdiff))**2)
                            UncDictDown[SF].SetBinContent(ix,iy,newUncDown)
                            SystOnlyDown[SF].SetBinContent(ix,iy,newUncSystDown)
                            doUsualStuff = False
                    # ====

                    if doUsualStuff:
                        newUnc = sqrt(oldUnc**2 + diff**2)
                        newUncSyst = sqrt(oldUncSyst**2 + diff**2)
                        UncDictUp[SF].SetBinContent(ix,iy,newUnc)
                        SystOnlyUp[SF].SetBinContent(ix,iy,newUncSyst)

                elif diff < 0:
                    oldUnc = UncDictDown[SF].GetBinContent(ix,iy)
                    oldUncSyst = SystOnlyDown[SF].GetBinContent(ix,iy)

                    #Symmetrize
                    doUsualStuff = True
                    if symmetrize and oppexists:
                        oldUncUp = UncDictUp[SF].GetBinContent(ix,iy)
                        oldUncSystUp = SystOnlyUp[SF].GetBinContent(ix,iy)                        
                        
                        oppdiff = symmdiffdict[oppname][(ix,iy)]
                        if oppdiff < 0:
                            if abs(diff) > abs(oppdiff):
                                newUnc = sqrt(oldUnc**2 - oppdiff**2 + diff**2)
                                newUncSyst = sqrt(oldUncSyst**2 - oppdiff**2 + diff**2)
                                UncDictDown[SF].SetBinContent(ix,iy,newUnc)
                                SystOnlyDown[SF].SetBinContent(ix,iy,newUncSyst)

                            newUncUp = sqrt(oldUncUp**2 + (abs(diff) - abs(oppdiff))**2)
                            newUncSystUp = sqrt(oldUncSystUp**2 + (abs(diff) - abs(oppdiff))**2)
                            UncDictUp[SF].SetBinContent(ix,iy,newUncUp)
                            SystOnlyUp[SF].SetBinContent(ix,iy,newUncSystUp)
                            doUsualStuff = False
                    # ====

                    if doUsualStuff:
                        newUnc = sqrt(oldUnc**2 + diff**2)
                        newUncSyst = sqrt(oldUncSyst**2 + diff**2)
                        UncDictDown[SF].SetBinContent(ix,iy,newUnc)
                        SystOnlyDown[SF].SetBinContent(ix,iy,newUncSyst)

for SF in sorted(allSFDict["central"]): 
    thishist = SF.replace("DeepFlavCvsL","hist").replace("CvsL","hist") 
    UncDictUp[SF].SetNameTitle(thishist+"_TotalUncUp",thishist+"_TotalUncUp")
    UncDictDown[SF].SetNameTitle(thishist+"_TotalUncDown",thishist+"_TotalUncDown")
    UncDictUp[SF].Write()
    UncDictDown[SF].Write()
for SF in sorted(allSFDict["central"]):
    SystOnlyUp[SF].Add(allSFDict["central"][SF])
    SystOnlyDown[SF].Add(allSFDict["central"][SF],-1)
    SystOnlyDown[SF].Scale(-1)
    thishist = SF.replace("DeepFlavCvsL","hist").replace("CvsL","hist")
    SystOnlyUp[SF].SetNameTitle(thishist+"_ValuesSystOnlyUp",thishist+"_ValuesSystOnlyUp")
    SystOnlyDown[SF].SetNameTitle(thishist+"_ValuesSystOnlyDown",thishist+"_ValuesSystOnlyDown")
    SystOnlyUp[SF].Write()
    SystOnlyDown[SF].Write()
    
            

for SF in sorted(allSFDict["central"]):     
    thishist = SF.replace("DeepFlavCvsL","hist").replace("CvsL","hist")
    centralwitherrs = allSFDict["central"][SF].Clone()
    maxUpDownerrs = allStatUncDict["central"][SF].Clone()
    for ix in range(0,centralwitherrs.GetNbinsX()+1):
        for iy in range(0,centralwitherrs.GetNbinsY()+1):
            if (ix == 0 or iy == 0) and not (ix==0 and iy==0): continue
            centralwitherrs.SetBinError(ix,iy,max(UncDictUp[SF].GetBinContent(ix,iy),UncDictDown[SF].GetBinContent(ix,iy)))
            maxUpDownerrs.SetBinContent(ix,iy,max(UncDictUp[SF].GetBinContent(ix,iy),UncDictDown[SF].GetBinContent(ix,iy)))
            
    centralwitherrs.SetName(thishist+"_withMaxUncs")
    centralwitherrs.Write()
    
    #plotSFs(centralwitherrs,maindir+"/2017_New_%s_maxUnc.png"%SF,True)
    hist = allSFDict["central"][SF]
    hist.SetTitle(hist.GetTitle().split()[0])
    if "DeepFlav" in hist.GetXaxis().GetTitle(): pref = "DeepJet"
    else: pref = "DeepCSV"
    hist.SetTitle(pref+" "+hist.GetTitle().split()[0])
    hist.GetXaxis().SetTitle(pref+" CvsL")
    hist.GetYaxis().SetTitle(pref+" CvsB")
    
    if args.noUnc: plotSFs(allSFDict["central"][SF],maindir+"/2017_New_asymm_%s_%s.png"%(SF,args.outputSuffix),True,noUnc=True)
    else: plotSFs(allSFDict["central"][SF],maindir+"/2017_New_asymm_%s_%s.png"%(SF,args.outputSuffix),True,UncUpHist=UncDictUp[SF],UncDownHist=UncDictDown[SF],forceSymm=args.symm)
    
    #centralwitherrs2 = centralwitherrs.RebinY(5)
    #centralwitherrs2.SetName(SF+"_withMaxUncsRebinned")
    #maxerrs = centralwitherrs2.Clone()
    #for ix in range(1,centralwitherrs.GetNbinsX()+1):
        #for iy in range(1,centralwitherrs.GetNbinsY()+1):
            #centralwitherrs2.SetBinContent(ix,iy,centralwitherrs2.GetBinContent(ix,iy)/5)
            #centralwitherrs2.SetBinError(ix,iy,centralwitherrs2.GetBinError(ix,iy)/sqrt(5))
            #maxerrs.SetBinContent(ix,iy,centralwitherrs2.GetBinError(ix,iy))
            
    ##centralwitherrs2.Write()
    #c = TCanvas("c","c",800,800)
    #c.cd()
    #gStyle.SetPaintTextFormat("4.3f")
    #centralwitherrs2.SetBarOffset(-0.2)
    #centralwitherrs2.SetMarkerSize(1.3)
    #centralwitherrs2.Draw("colz text89")

    #maxerrs.SetBarOffset(0.2)
    #maxerrs.SetMarkerColor(kRed)
    #maxerrs.Draw("text89 same")
    #c.SaveAs(maindir+"/2017_%s.png"%SF)
    
    #maxUpDownerrs.Draw("colz")
    #c.SaveAs(maindir+"/2017_%s_maxUncOnly.png"%SF)
