from ROOT import *
import os, sys, json, pickle
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import numpy.polynomial.polynomial as poly
from scipy.optimize import minimize
from array import array
import scipy.odr as odr
import argparse, gc
from glob import glob

gROOT.SetBatch(1)
gStyle.SetOptStat(0)
gErrorIgnoreLevel = 4001
#gSystem.RedirectOutput("/dev/null")


# ================== Set parameters =====================
plotProgress = False
firstbinidx = 11
learningrate = 0.005		#0.002 for DeepCSV 2017, 0.005 for DeepJet 2017
maxrelerr = 0.01
maxbinstocombine = 5
minbinstocombine = 1
nBins = 50
maxIters = 2000
preStopIters = 50
purityThreshold = 0.1	#0.1 for 2017
njetThreshold = 5
useWcMu = True
doMinus1 = True
exporttemplates = False
# ======================================================


# ================== Load arguments =====================
parser = argparse.ArgumentParser("Adaptive binnning based fit for c-tagger shape calibration")
parser.add_argument('-i','--inputdir',type=str,default="")
parser.add_argument('-max','--maxbinstocombine',type=int,default=5)
parser.add_argument('-min','--minbinstocombine',type=int,default=1)
parser.add_argument('-err','--maxrelerr',type=float,default=0.02)
parser.add_argument('-r','--range',type=str,default="")
parser.add_argument('--doDeepJet', action="store_true", default=False)
parser.add_argument('--indepbinning', action="store_true", default=False)
parser.add_argument('--pseudo', action="store_true", default=False)
parser.add_argument('--doTempRemodel', action="store_true", default=False)
parser.add_argument('--force', action="store_true", default=False)
parser.add_argument('-v','--verbose', action="store_true", default=False)

args = parser.parse_args()
print args

maxbinstocombine = args.maxbinstocombine
minbinstocombine = args.minbinstocombine
maxrelerr = args.maxrelerr
doDeepJet = args.doDeepJet
pseudo = args.pseudo
inputrange = args.range
indepbin = args.indepbinning
verb = args.verbose

indir = args.inputdir
isSyst = "central" not in indir
if not isSyst: indepbin = True

deepSuff = ""
if doDeepJet:
    deepSuff = "DeepFlav"
    #doMinus1 = False

if inputrange!="" and inputrange!="m1": doMinus1 = False

pseudoPre = ""
if pseudo: pseudoPre = "pseudo"

if inputrange == "": print "For faster processing, parallellize using: 'python X.py -r prep',\nthen 'parallel python X.py -i centraldir -r :::: rangelist.txt',\nthen 'python X.py -i centraldir -r comb',\nthen 'parallel python X.py -i ::: alldir* ::: -r :::: rangelist.txt',\nthen 'parallel python X.py -r comb -i ::: alldir*'"
# ======================================================
    

# ================== Create directories =====================
print "\n"*2+"="*40 +"\nEntering directory: "+indir+"\n"+"="*40 +"\n"

workdir = indir+"/work_%d_%d_%.3f/"%(maxbinstocombine,minbinstocombine,maxrelerr)
progdir = workdir + "prog/"
resultsname="results_%d_%d_%.3f"%(maxbinstocombine,minbinstocombine,maxrelerr)

if len(glob("%s/%s/*.root"%(indir,resultsname))) > 0 and not args.force:
    print "Already ran on this directory. To rerun and overwrite, use --force."
    sys.exit()

os.system("mkdir -p "+progdir)
os.system("mkdir -p %s/%s"%(indir,resultsname))
# ======================================================


# ================== Load root files =====================
#rootlist = [i for i in os.listdir(indir) if i.endswith('.root')         \
            #and i.startswith("jet_Cvs") and "+jet_Cvs" in i             \
            #and not (i.startswith("jet_CvsL") and "+jet_CvsL" in i)     \
            #and not (i.startswith("jet_CvsB") and "+jet_CvsB" in i)     
            #and not "_-0.2" in i        ]

if not doDeepJet:
    rootlist = [i for i in os.listdir(indir) if i.endswith('.root')         \
                and "%sCvsL"%deepSuff in i and "%sCvsB_0."%deepSuff in i and "DeepFlav" not in i]
else:
    rootlist = [i for i in os.listdir(indir) if i.endswith('.root')         \
                and "%sCvsL"%deepSuff in i and "%sCvsB_0."%deepSuff in i]
            
incllist = [i for i in os.listdir(indir) if i.endswith('.root')         \
            and (("jet_%sCvsL"%deepSuff in i and "%sCvsB"%deepSuff not in i) or ("jet_%sCvsB"%deepSuff in i and "%sCvsL"%deepSuff not in i)) ]
# ======================================================


# ================== Load data from root files =====================
distdict = {}
minus1bindict = {}
rnglist = []

for rfile in sorted(rootlist):    

    # ------------------- Load all histograms --------------------
    #if "TT" in rfile and "semi" not in rfile:
    #    print "WARNING: Skipped",rfile
    #    continue
    ifile = TFile.Open(indir+"/"+rfile, "READ") 
    c = ifile.Get("c")
    b = ifile.Get("b")
    l = ifile.Get("uds")
    lep = ifile.Get("lep")
    d = ifile.Get(pseudoPre+"Data")
    
    l.Add(lep)
    
    c.SetDirectory(0)
    b.SetDirectory(0)
    l.SetDirectory(0)
    d.SetDirectory(0)
    # ------------------------------------------------------------
    
    # ------------------- Load inclusive file --------------------
    inclmatch = [i for i in incllist if i.startswith('_'.join(rfile.split("_")[:5]))]
    if len(inclmatch) > 1: print "WARNING: Ambiguous mapping to inclusive root file for %s."%rfile
    elif len(inclmatch) < 1:
        print "\nERROR: Matching inclusive file not found for %s."%rfile
        continue
    
    inclfile = TFile.Open(indir+"/"+inclmatch[0], "READ")
    MCSum = inclfile.Get("MCSum")
    DataSum = inclfile.Get(pseudoPre+"Data")
    cincl = inclfile.Get("c")
    bincl = inclfile.Get("b")
    lincl = inclfile.Get("uds")
    lepincl = inclfile.Get("lep")
    
    DataMCRatio = DataSum.Integral()/MCSum.Integral()
    #DataMCRatio2 = DataSum.Integral(0,DataSum.GetNbinsX()+1)/MCSum.Integral(0,MCSum.GetNbinsX()+1)
    if pseudo: DataMCRatio = 1.
    #print inclmatch[0],DataMCRatio,DataMCRatio2
    # ------------------------------------------------------------
    
    # ------------------- Store -1 bin values --------------------
    minus1temp = {}
    for ibin in range(1,DataSum.GetNbinsX()):
        if MCSum.GetBinContent(ibin) != 0:
            #print ibin
            minus1temp['c'] = cincl.GetBinContent(ibin)*DataMCRatio
            minus1temp['b'] = bincl.GetBinContent(ibin)*DataMCRatio
            minus1temp['l'] = (lincl.GetBinContent(ibin)+lepincl.GetBinContent(ibin))*DataMCRatio
            minus1temp['d'] = DataSum.GetBinContent(ibin)
            minus1temp['derr'] = DataSum.GetBinError(ibin)
            minus1temp['mcerr'] = MCSum.GetBinError(ibin)
            minus1temp['cerr'] = cincl.GetBinError(ibin)*DataMCRatio
            minus1temp['berr'] = bincl.GetBinError(ibin)*DataMCRatio
            minus1temp['lerr'] = (lincl.GetBinError(ibin)**2+lepincl.GetBinError(ibin)**2)**0.5 * DataMCRatio
            break
    ###
    inclfile.Close()
    
    c.Scale(DataMCRatio)
    b.Scale(DataMCRatio)
    l.Scale(DataMCRatio)   
    # ------------------------------------------------------------
    
    # ------------------- Store histograms by range --------------------
    name = '_'.join(rfile.split('_')[:2])
    
    if "jet_%sCvsB"%deepSuff in rfile: dist = "%sCvsB"%deepSuff
    elif "jet_%sCvsL"%deepSuff in rfile: dist = "%sCvsL"%deepSuff
    
    rng = rfile.rstrip(".root").split("_")[-1]
    if rng not in rnglist: rnglist.append(rng)
    
    if not dist in distdict:  distdict[dist] = {}
    if not rng in distdict[dist]: distdict[dist][rng] = {}
    if not name in distdict[dist][rng]: distdict[dist][rng][name] = {}  
    
    outname = "%s+%s+%s"%(name,dist,rng)
    
    for hist, label in [(c,"c"),(b,"b"),(l,"l"),(d,"data")]:
        hist.SetTitle(outname+"_"+label)
        distdict[dist][rng][name][label] = hist.Clone()
        
#        canv = TCanvas("c1","c1",1000,1000)
#        hist.Draw()
#        canv.SaveAs("%s/%s_%s.png"%(workdir,outname,label))
    if dist == "%sCvsL"%deepSuff:
        minus1bindict[name] = minus1temp.copy()

    ifile.Close()
    # ------------------------------------------------------------
# ======================================================

if inputrange=="prep":
    outtxt = open("rangelist.txt","w")
    outtxt.write("m1")
    for rng in rnglist:
        outtxt.write("\n"+rng)
    outtxt.close()
    print "Written to rangelist.txt."
    sys.exit(0)

# ================== Merge channels of each selection =====================
mergedDict = {}
for dist in distdict:
    mergedDict[dist] = {}
    for rng in distdict[dist]:
        mergedDict[dist][rng] = {"Wc":{}, "TT":{}, "DY":{} }
        for name in distdict[dist][rng]:
            mergename = name.split("_")[0]
            for flav in distdict[dist][rng][name]:
                if flav in mergedDict[dist][rng][mergename]: mergedDict[dist][rng][mergename][flav].Add(distdict[dist][rng][name][flav])
                else: mergedDict[dist][rng][mergename][flav] = distdict[dist][rng][name][flav].Clone()
                if flav == "c": mergedDict[dist][rng][mergename][flav].SetFillColor(kCyan)
                elif flav == "b": mergedDict[dist][rng][mergename][flav].SetFillColor(kMagenta)
                elif flav == "l": mergedDict[dist][rng][mergename][flav].SetFillColor(kYellow)
                mergedDict[dist][rng][mergename][flav].GetXaxis().SetTitle(dist)
                mergedDict[dist][rng][mergename][flav].GetYaxis().SetTitle("Jets")

# -1 bin
mergedminus1Dict = {"Wc":{}, "TT":{}, "DY":{} }
for reg in minus1bindict:
    if reg == "Wc_m": continue
    mreg = reg.split('_')[0]
    for flav in minus1bindict[reg]:
        if flav not in mergedminus1Dict[mreg]: mergedminus1Dict[mreg][flav] = 0.
        mergedminus1Dict[mreg][flav] += minus1bindict[reg][flav]
# ======================================================


# ================== Get purity =====================
def getMCSum(flavdict):
    return flavdict['b']+flavdict['c']+flavdict['l']

purityList = [(mergedminus1Dict['TT']['b']/getMCSum(mergedminus1Dict['TT']),'TT','b'),
              (mergedminus1Dict['Wc']['c']/getMCSum(mergedminus1Dict['Wc']),'Wc','c'),
              (mergedminus1Dict['DY']['l']/getMCSum(mergedminus1Dict['DY']),'DY','l')]

purityList.sort(reverse=True)
# ======================================================


# ================== Do minus 1 bin =====================
SFm1 = {'c':1., 'b':1., 'l':1.}
SFm1Err = {'c':1., 'b':1., 'l':1.}
# print mergedminus1Dict

if doMinus1:
    print "Starting with -1 bin"
    
    if doDeepJet:
        # -------------------- Just a straightforward division ----------------------
        reg = 'TT'
        SFm1['b'] = (mergedminus1Dict[reg]['d']-mergedminus1Dict[reg]['c']-mergedminus1Dict[reg]['l'])/mergedminus1Dict[reg]['b']
        SFm1Err['b'] = (                \
                            (mergedminus1Dict[reg]['derr'] + mergedminus1Dict[reg]['berr'] + mergedminus1Dict[reg]['cerr']) /        \
                            (mergedminus1Dict[reg]['d']-mergedminus1Dict[reg]['c']-mergedminus1Dict[reg]['l'])                       \
                            + mergedminus1Dict[reg]['berr']/mergedminus1Dict[reg]['b']                                               \
                       )* SFm1['b']
        # ---------------------------------------------------------------------------
        
    else:
        globchi2list = []
        # -------------------- Iterative fit for -1 bin ----------------------
        for iIter in range(maxIters):
            # print SFm1
            globchi2 = 0.
            for reg in ['TT','Wc','DY']:
                diff = mergedminus1Dict[reg]['d']-mergedminus1Dict[reg]['b']*SFm1['b']-mergedminus1Dict[reg]['c']*SFm1['c']-mergedminus1Dict[reg]['l']*SFm1['l']
                globchi2 += diff**2/(mergedminus1Dict[reg]['derr']**2 + mergedminus1Dict[reg]['mcerr']**2)
        
            #print '\t-1 bin: Iteration %d: Global chi^2 = %f'%(iIter,globchi2)
            globchi2list.append(globchi2)
            if iIter > preStopIters+1:
                if globchi2list.index(min(globchi2list)) < iIter - preStopIters:
                    print "Iteration %d: Chi2 did not improve in the last %d iterations, stopping. Starting Chi2 = %f. Lowest Chi2 = %f."%(iIter,preStopIters,globchi2list[0],min(globchi2list))
                    break
            for num, reg, flav in purityList:
                flavdict = mergedminus1Dict[reg]
                sig = flavdict[flav] * SFm1[flav]
                sigData = flavdict['d']
                for iflav in ['c','b','l']:
                    if iflav == flav: continue
                    sigData -= flavdict[iflav] * SFm1[iflav]
                if sig == 0: newSF = SFm1[flav]
                else: newSF = sigData/sig
                if newSF > SFm1[flav]: SFm1[flav] = min(SFm1[flav]+learningrate,newSF)
                elif newSF < SFm1[flav]: SFm1[flav] = max(SFm1[flav]-learningrate,newSF)
            
                if flavdict['d']!=0. and flavdict[flav]!=0.:
                    relerrdata = (flavdict['derr']+flavdict['cerr']+flavdict['berr']+flavdict['lerr']-flavdict[flav+'err']) / flavdict['d']
                    relerrsig = flavdict[flav+'err']/flavdict[flav]
                    SFm1Err[flav] = newSF * (relerrdata+relerrsig)
                else:
                    SFm1Err[flav] = newSF
        # ---------------------------------------------------------------------------
    
    print SFm1
    print SFm1Err
if inputrange=="m1":
    pickle.dump([SFm1,SFm1Err],open("%s/SFs_%s.pkl"%(workdir,inputrange),"wb"))
    sys.exit(0)
# ======================================================

def getintglerr(hist):
    intgl = 0.
    herr = 0.
    for ibin in range(firstbinidx,hist.GetNbinsX()+1):
        intgl += hist.GetBinContent(ibin)
        herr += (hist.GetBinError(ibin))**2
    herr = herr**0.5
    return intgl, herr

# ====================== Template remodelling, deprecated ========================
for dist in mergedDict:
    for rng in mergedDict[dist]:        
        for flav in ["c", "b", "l", "data"]:
            if exporttemplates:
                if "CvsB" in dist:
                    canv = TCanvas("c1","c1",500,1200)
                    canv.Divide(1,3)
                else:
                    canv = TCanvas("c1","c1",500,1200) #,1200,340)
                    canv.Divide(1,3)            

            IntDict = {}
            IntErrDict = {}
            count = 1
            for name in mergedDict[dist][rng]:
                if exporttemplates: canv.cd(count)
                hist = mergedDict[dist][rng][name][flav]
#                print dist, rng, name, flav, hist.GetTitle()
                IntDict[name], IntErrDict[name] = getintglerr(hist)                
#                hist.SetTitle(hist.GetTitle()+" %f"%(IntErrDict[name]/IntDict[name]))
                if exporttemplates: hist.Draw()
                count += 1
            outname = "%s/%s+%s+%s.png"%(workdir,dist,rng,flav)
            if exporttemplates:
                plt.savefig(outname)
                plt.clf()
                print "Exported "+outname
                canv.SaveAs(outname)
            sortedlist = []
            for i in IntDict:
                if IntDict[i] == 0: sortedlist.append((1,i))
                else: sortedlist.append((abs(IntErrDict[i]/IntDict[i]),i))
            sortedlist = sorted(sortedlist)
            
            if not args.doTempRemodel: continue
            relerrmax = sortedlist[-1][0]
            if flav!="data" and relerrmax > 0.1:
                catname = sortedlist[-1][1]
                histbest = mergedDict[dist][rng][sortedlist[0][1]][flav].Clone()
                histbest2 = mergedDict[dist][rng][sortedlist[1][1]][flav].Clone()
#                print IntDict[catname]/histbest.Integral()
                histbest.Scale(max(0.00001,IntDict[catname])/histbest.Integral())
                if histbest2.Integral()>0: histbest2.Scale(max(0.00001,IntDict[catname])/histbest2.Integral())
                for ibin in range(firstbinidx,histbest.GetNbinsX()+1):
                    newerr = histbest.GetBinContent(ibin)*IntErrDict[catname]/histbest.Integral()
#                    print newerr,abs(histbest.GetBinContent(ibin)-histbest2.GetBinContent(ibin))
                    if newerr < abs(histbest.GetBinContent(ibin)-histbest2.GetBinContent(ibin)):
                        a = histbest.GetBinContent(ibin)
                        b = histbest.GetBinError(ibin)
                        c = histbest2.GetBinContent(ibin)
                        d = histbest2.GetBinError(ibin)
                        newbincont = (a*d*d+b*b*c)/(b*b+d*d)
#                        print histbest.GetBinContent(ibin),newbincont
                        histbest.SetBinContent(ibin,newbincont)
                        newerr = abs(histbest.GetBinContent(ibin)-histbest2.GetBinContent(ibin))
                    histbest.SetBinError(ibin,newerr)
                histbest.SetTitle(mergedDict[dist][rng][catname][flav].GetTitle()+"_fixed")
                #histbest.SetTitle(str(["%.3f"% i for i,j in sortedlist]))
                mergedDict[dist][rng][catname][flav] = histbest.Clone()
                
                if "CvsB" in dist:
                    canv = TCanvas("c1","c1",500,1200)
                    canv.Divide(1,3)
                else:
                    canv = TCanvas("c1","c1",500,1200) #,1200,340)
                    canv.Divide(1,3)
                count = 1
                for name in mergedDict[dist][rng]:
                    canv.cd(count)
                    hist = mergedDict[dist][rng][name][flav]                        
                    hist.Draw()
                    count += 1
                outname = "%s/%s+%s+%s_fixed.png"%(workdir,dist,rng,flav)
                canv.SaveAs(outname)

# ======================================================

# ================== Define some functions ==================            
def getPurity(cbldDict,flav):
    totalMC = 0.
    for fl in ["c", "b", "l"]:
        totalMC += cbldDict[fl].Integral()
    if totalMC == 0.: return 0.
    return cbldDict[flav].Integral()/totalMC

def getdataMCRat(cbldDict):
    totalMC = 0.
    for fl in ["c", "b", "l"]:
        totalMC += cbldDict[fl].Integral()
    return cbldDict["data"].Integral()/totalMC
    #return 1.

def applyWts(hist,flavparams):
    histfinal = hist.Clone()
    
    if not hist.Integral(1,firstbinidx-1) == 0.: start =  1
    else: start = firstbinidx
    for ibin in range(start,hist.GetNbinsX()+1):
        x = (hist.GetBinLowEdge(ibin)+hist.GetBinLowEdge(ibin+1))/2
        #factor = poly.polyval(x,flavparams)
        binning = flavparams[0]
        vals = flavparams[1]
        factor = 1.
        for i in range(len(binning)-1):
            if x >= binning[i] and x < binning[i+1]:
                factor = vals[i]
        if factor < 0.: factor = 0
        histfinal.SetBinContent(ibin,hist.GetBinContent(ibin)*factor)
        histfinal.SetBinError(ibin,hist.GetBinError(ibin)*factor)
    return histfinal

def getTotalChi2(cbldDict,params):
    totalMC = ""
    for fl in ["c", "b", "l"]:
        hist = applyWts(cbldDict[fl],params[fl])
        if totalMC == "": totalMC = hist.Clone()
        else: totalMC.Add(hist)
    data = cbldDict["data"]
    sm = 0.
    for ibin in range(firstbinidx,totalMC.GetNbinsX()+1):
        diff = totalMC.GetBinContent(ibin)-data.GetBinContent(ibin)
        unc2 = totalMC.GetBinError(ibin)**2+data.GetBinError(ibin)**2
        if unc2 > 0: sm += diff**2/unc2
    return sm

def getGlobalChi2(selDict,params):
        WcChi2 = getTotalChi2(selDict["Wc"],params)
        TTChi2 = getTotalChi2(selDict["TT"],params)
        DYChi2 = getTotalChi2(selDict["DY"],params)
        GlobalChi2 = WcChi2 + TTChi2 + DYChi2
        return GlobalChi2

def getValsFromHist(hist):
    xvals = []
    xerrs = []
    yvals = []
    yerrs = []
    for ibin in range(1,hist.GetNbinsX()+1):
        xvals.append((hist.GetBinLowEdge(ibin) + hist.GetBinLowEdge(ibin+1))/2)
        xerrs.append((hist.GetBinLowEdge(ibin+1) - hist.GetBinLowEdge(ibin))/2)
        yval = hist.GetBinContent(ibin)
        #if ibin == hist.GetNbinsX(): yval += hist.GetBinContent(ibin+1)
        yvals.append(yval)
        yerr = 0.
        if hist.GetBinError(ibin) > 0.: yerr = hist.GetBinError(ibin)
        yerrs.append(yerr)
    return xvals,xerrs,yvals,yerrs
# ======================================================


# ================== Begin main iterative fit ==================   
SFResults = {}
if plotProgress: os.system("rm -f %s/*"%progdir)
print "Starting iterative fit..."
for dist in mergedDict:
    if inputrange=="": 
        #--------------------- Norm crosscheck --------------------------
        print "====================== Norm crosscheck ======================"
        Wcyield = mergedminus1Dict["Wc"]["c"]+mergedminus1Dict["Wc"]["b"]+mergedminus1Dict["Wc"]["l"]
        TTyield = mergedminus1Dict["TT"]["c"]+mergedminus1Dict["TT"]["b"]+mergedminus1Dict["TT"]["l"]
        DYyield = mergedminus1Dict["DY"]["c"]+mergedminus1Dict["DY"]["b"]+mergedminus1Dict["DY"]["l"]
        WcDataYield = mergedminus1Dict["Wc"]["d"]
        TTDataYield = mergedminus1Dict["TT"]["d"]
        DYDataYield = mergedminus1Dict["DY"]["d"]
        Wcf = {'c':mergedminus1Dict["Wc"]["c"],'b':mergedminus1Dict["Wc"]["b"],'l':mergedminus1Dict["Wc"]["l"]}
        TTf = {'c':mergedminus1Dict["TT"]["c"],'b':mergedminus1Dict["TT"]["b"],'l':mergedminus1Dict["TT"]["l"]}
        DYf = {'c':mergedminus1Dict["DY"]["c"],'b':mergedminus1Dict["DY"]["b"],'l':mergedminus1Dict["DY"]["l"]}
        for rng in sorted(mergedDict[dist]):
            Wc, TT, DY = 0, 0, 0
         
            for flav in ['c','b','l']:
                Wc += mergedDict[dist][rng]["Wc"][flav].Integral()
                TT += mergedDict[dist][rng]["TT"][flav].Integral()
                DY += mergedDict[dist][rng]["DY"][flav].Integral()
                Wcf[flav] += mergedDict[dist][rng]["Wc"][flav].Integral()
                TTf[flav] += mergedDict[dist][rng]["TT"][flav].Integral()
                DYf[flav] += mergedDict[dist][rng]["DY"][flav].Integral()
            #print rng, Wc, mergedDict[dist][rng]["Wc"]["data"].Integral()
            #print rng, TT, mergedDict[dist][rng]["TT"]["data"].Integral()
            #print rng, DY, mergedDict[dist][rng]["DY"]["data"].Integral()
            Wcyield += Wc
            TTyield += TT
            DYyield += DY
            WcDataYield += mergedDict[dist][rng]["Wc"]["data"].Integral()
            TTDataYield += mergedDict[dist][rng]["TT"]["data"].Integral()
            DYDataYield += mergedDict[dist][rng]["DY"]["data"].Integral()
        
        print Wcyield,WcDataYield,Wcf
        print TTyield,TTDataYield,TTf
        print DYyield,DYDataYield,DYf
        print "==========================================================="
        print
    #----------------------------------------------------------
    
    SFResults[dist] = {}
    for rng in sorted(mergedDict[dist]): 
        if inputrange!="" and inputrange!=rng: continue

        if not indepbin:
            centdir = '/'.join(indir.rstrip('/').split('/')[:-1])
            lastdir = indir.rstrip('/').split('/')[-1]
            lastdirnew = '/'+'_'.join(lastdir.split('_')[:2])+'_central'
            centdir += lastdirnew

            matchfl = centdir+'/work*/*%s*.pkl'%rng
            matchlist = glob(matchfl)
            if len(matchlist) == 0:
                print "Did not find %s. Did you run bin-wise on central?"%matchfl
                sys.exit(0)
            elif len(matchlist) > 1:
                print "Found multiple matches for %s. Choosing first of %s."%(matchfl,matchlist)
            unpack = pickle.load(open(matchlist[0],'rb'))
            centdict = unpack[dist][rng]

        #--------------------- Start fit per range --------------------------
        print "Doing %s, in range %s."%(dist,rng)
        purityWc = getPurity(mergedDict[dist][rng]["Wc"],"c")
        purityTT = getPurity(mergedDict[dist][rng]["TT"],"b")
        purityDY = getPurity(mergedDict[dist][rng]["DY"],"l")
        
        purityList = sorted([(purityWc,"Wc","c"),(purityTT,"TT","b"),(purityDY,"DY","l")],reverse=True)
        
        nBinsLoc = mergedDict[dist][rng]["Wc"]["c"].GetNbinsX()-firstbinidx+1
        binWidth = 1./nBinsLoc
        nomBinning = np.arange(0.,1.+binWidth,binWidth)
        
        nomParam = [nomBinning,[1.]*nBinsLoc]
        
        initParams = {}
        initParams["c"] = nomParam
        initParams["b"] = nomParam
        initParams["l"] = nomParam
        
        params = {}
        params["c"] = initParams["c"][:]
        params["b"] = initParams["b"][:]
        params["l"] = initParams["l"][:]    
        
        GlobalChi2List = []
        paramsList = []
        
        ratios = {}
        for iIter in range(maxIters+1): 
            if plotProgress:
                bigcanv = TCanvas("cb","cb",1500,1200)
                bigcanv.SetTopMargin(500)
                bigcanv.Divide(3,3,.001,.001)
            stack = {}            
            sigs = {}
            datas = {}
            for isel in range(len(purityList)):           
                sel = purityList[isel][1]
                flav = purityList[isel][2]
                data = mergedDict[dist][rng][sel]["data"]
                #sig = applyWts(mergedDict[dist][rng][sel][flav],params[flav]).Clone()
                sig = mergedDict[dist][rng][sel][flav].Clone()
                bkg = ""
                mcsum = sig.Clone()
                for fl in ['b','c','l']:
                    if fl == flav: continue
                    mcsum.Add(mergedDict[dist][rng][sel][fl])
                
                def getBinCont(hist):
                    bincont = []
                    for xbin in range(2,hist.GetNbinsX()+1):
                        bincont.append(hist.GetBinContent(xbin))
                    return np.array(bincont)
                
                if iIter == 0:
                    sig2 = sig.Clone()
                    
                    sig2.Rebin(maxbinstocombine)
                    mcsum.Rebin(maxbinstocombine)
                    bincontsig = getBinCont(sig2)
                    bincontmcsum = getBinCont(mcsum)
                    if verb:
                        print "Stat examination:", sel, flav, bincontsig
                        print "Stat examination:", sel, "mcsum", bincontmcsum
                        print "Stat examination:", sel, "purity", bincontsig/bincontmcsum
                        print
                
                if iIter > 0:
                    for fl in ["c", "b", "l"]:
                        if fl == flav: continue
                        if bkg == "": bkg = applyWts(mergedDict[dist][rng][sel][fl],params[fl]).Clone()
                        else: bkg.Add(applyWts(mergedDict[dist][rng][sel][fl],params[fl]))
                    
                    sigData = data.Clone()
                    sigData.Add(bkg,-1.)
                    
                    def getNextBinBound(histD,histMC,firstIdx):
                        for nextBinIdx in range(firstIdx+minbinstocombine,histD.GetNbinsX()+2):
                            datasum = 0.
                            dataerr = 0.
                            mcsum = 0.
                            mcerr = 0.
                            for ibin in range(firstIdx,nextBinIdx):
                                dataerr += histD.GetBinError(ibin)**2
                                datasum += histD.GetBinContent(ibin)
                                mcerr += histMC.GetBinError(ibin)**2
                                mcsum += histMC.GetBinContent(ibin)
                            dataerr = dataerr**0.5
                            mcerr = mcerr**0.5
                            if datasum == 0. or mcsum == 0.: relerr = 1. 
                            else: relerr = abs(dataerr/datasum) + abs(mcerr/mcsum)
                            if relerr <= maxrelerr or nextBinIdx==histD.GetNbinsX()+1 or (nextBinIdx-firstIdx)>=maxbinstocombine:
                                return nextBinIdx
                        return histD.GetNbinsX()+1
                    
                    if indepbin:
                        nextBinIdx = firstbinidx
                        newbinning = [0.]
                        while nextBinIdx < sigData.GetNbinsX()+1:
                            nextBinIdx = getNextBinBound(sigData,sig,nextBinIdx)
                            newbinning.append(round(sigData.GetBinLowEdge(nextBinIdx),2))
                        #print newbinning
                        newbinning = array('d',newbinning)
                    else:
                        newbinning = centdict[flav][0]

                    thismcsum = mcsum.Clone()
                    thismcsum = thismcsum.Rebin(len(newbinning)-1,sig.GetName()+"_rebin",newbinning)
                    sig = sig.Rebin(len(newbinning)-1,sig.GetName()+"_rebin",newbinning)
                    sigData = sigData.Rebin(len(newbinning)-1,sigData.GetName()+"_rebin",newbinning)
                    
                    ratioH = sigData.Clone()
                    ratioH.Divide(sig)
            
       
                    SFs = []
                    SFUncs = []
                    oldbinning = params[flav][0]
                    oldSFs = params[flav][1]
                    for ibin in range(1,ratioH.GetNbinsX()+1):
                        if ratioH.GetBinContent(ibin) <= 0 or sigData.GetBinContent(ibin) <= 0 or sig.GetBinContent(ibin) <= 0 or sig.GetBinContent(ibin)/thismcsum.GetBinContent(ibin)<purityThreshold or sig.GetBinContent(ibin)<njetThreshold or thismcsum.GetBinContent(ibin)<njetThreshold:
                            #print sig.GetBinContent(ibin)/thismcsum.GetBinContent(ibin), sig.GetBinContent(ibin)
                            ratioH.SetBinContent(ibin,1.)
                            ratioH.SetBinError(ibin,1.)
                            
                        thisbinx = (ratioH.GetBinLowEdge(ibin)+ratioH.GetBinLowEdge(ibin+1))/2
                        for ibin2 in range(0,len(oldbinning)-1):
                            if thisbinx >= oldbinning[ibin2] and thisbinx < oldbinning[ibin2+1]:
                                oldSF = oldSFs[ibin2]
                                break
                        newSF = ratioH.GetBinContent(ibin)
                        if newSF > oldSF: newSFmod = min(newSF,oldSF+learningrate)
                        elif newSF < oldSF: newSFmod = max(newSF,oldSF-learningrate)
                        else: newSFmod = newSF
                        #print '\t',oldSF,newSF,newSFmod
                        SFs.append(newSFmod)
                        if newSF == 0: SFUncs.append(ratioH.GetBinError(ibin))
                        else: SFUncs.append(ratioH.GetBinError(ibin)/newSF*newSFmod) 
                    
                    params[flav] = [newbinning,SFs,SFUncs]
                    del sig,sigData,ratioH
                    
                    #canv = TCanvas("c1","c1",1500,500)
                    #canv.Divide(3,1)
                    #canv.cd(1)            
                    #sig.Draw("hist e")
                    #sig.SetMaximum(sigData.GetMaximum()*1.3)
                    #sig.SetMinimum(sigData.GetMinimum()*1.3)
                    #sigData.Draw("same")  
                    #canv.cd(2) 
                    #hist = applyWts(sig,params[flav]).Clone()
                    #hist.SetMaximum(sigData.GetMaximum()*1.3)
                    #hist.SetMinimum(sigData.GetMinimum()*1.3)
                    #hist.Draw("hist e")
                    #sigData.Draw("same")
                    #canv.cd(3)
                    #ratioH.SetMarkerSize(1)
                    #ratioH.SetMaximum(2.)
                    #ratioH.SetMinimum(0.)
                    #ratioH.Draw("p e")
                    
                    #outname = "%s/test_%s+%s+%d_%s.png"%(workdir,dist,rng,isel,flav)            
                    #canv.SaveAs(outname)
                
                if plotProgress:
                    for isel2 in range(len(purityList)): 
                        sel2 = purityList[isel2][1]
                        flav2 = purityList[isel2][2]
                        data2 = mergedDict[dist][rng][sel2]["data"]
                        #sig = applyWts(mergedDict[dist][rng][sel][flav],params[flav]).Clone()
                        sig2 = mergedDict[dist][rng][sel2][flav2].Clone()
                        bkg2 = ""
                        for fl in ["c", "b", "l"]:
                            if fl == flav2: continue
                            if bkg2 == "": bkg2 = applyWts(mergedDict[dist][rng][sel2][fl],params[fl]).Clone()
                            else: bkg2.Add(applyWts(mergedDict[dist][rng][sel2][fl],params[fl]))                    
                        sigData2 = data2.Clone()
                        sigData2.Add(bkg2,-1.)
                        
                        bigcanv.cd(isel2*3+1)
                        stack[isel2] = THStack("stack_%d"%isel2,sel)
                        for fl in ["l","b","c"]:
                            hist = applyWts(mergedDict[dist][rng][sel2][fl],params[fl]).Clone()
                            hist.GetXaxis().SetRangeUser(0.,1.)
                            stack[isel2].Add(hist)
                        stack[isel2].SetTitle(sel2)
                        stack[isel2].SetMaximum(data2.GetMaximum()*1.2)                
                        stack[isel2].Draw("hist e")
                        
                        data2.Draw("same e")   
                        
                        #if iIter==0 or (iIter>0 and isel2 >= isel):
                        bigcanv.cd(isel2*3+2)  
                        sigs[isel2] = applyWts(sig2,params[flav2]).Clone()
                        datas[isel2] = sigData2.Clone()
                        sigs[isel2].SetMaximum(sigData2.GetMaximum()*1.2)
                        sigs[isel2].GetXaxis().SetRangeUser(0.,1.)
                        sigs[isel2].SetTitle("%s: %s"%(sel2,flav2))
                        sigs[isel2].Draw("hist e")
                        datas[isel2].Draw("same")                    
                        
                        if iIter > 1:
                            bigcanv.cd(isel2*3+3)
                            ratios[isel2].Draw("p e")
                        
                    if iIter > 0:
                        #bigcanv.cd(isel*3+2)
                        #sigs[isel] = sig.Clone()
                        #sigs[isel].Draw("hist e")
                        #datas[isel] = sigData.Clone()
                        #datas[isel].Draw("same")                        
                        
                        bigcanv.cd(isel*3+3)
                        ratios[isel] = ratioH.Clone()
                        ratios[isel].SetTitle("SF %s"%flav)
                        ratios[isel].Draw("p e")                
                    
                    if iIter == 0 and isel>0: continue
                    outname = "%s/prog_%s+%s+%d_%d.png"%(progdir,dist,rng,iIter,isel)  
                    bigcanv.SaveAs(outname)
                
                
            GlobalChi2 = getGlobalChi2(mergedDict[dist][rng], params) 
            #print "\tIteration %d, global chi2 is %f."%(iIter,GlobalChi2)
            GlobalChi2List.append(GlobalChi2)
            paramsList.append(params.copy())
            if iIter > preStopIters+1:
                if GlobalChi2List.index(min(GlobalChi2List)) < iIter - preStopIters:
                    print "Iteration %d: Chi2 did not improve in the last %d iterations, stopping. Starting Chi2 = %f. Lowest Chi2 = %f."%(iIter,preStopIters,GlobalChi2List[0],min(GlobalChi2List))
                    break
            
        iBest = GlobalChi2List.index(min(GlobalChi2List))
        SFResults[dist][rng] = paramsList[GlobalChi2List.index(min(GlobalChi2List))]
        #print SFResults[dist][rng]
        # print "SFc:", dist,rng,SFResults[dist][rng]['c']
        # print "SFb:", dist,rng,SFResults[dist][rng]['b']
        # print "SFl:", dist,rng,SFResults[dist][rng]['l']
        if plotProgress: os.system("rm -f %s/prog_%s+%s+{%d..%d}_*.png"%(progdir,dist,rng,iBest+1,len(GlobalChi2List)))
        
        plt.plot([i for i in range(iBest)],GlobalChi2List[:iBest])
        plt.yscale('log')
        plt.title("%s in %s"%(dist,rng))
        plt.savefig("%s/Chi2_%s+%s.png"%(workdir,dist,rng))
        plt.clf()
        
        fitC = TCanvas("fit","fit",1600,2000)
        fitC.Divide(2,3)
        stackPre = {}
        dataPre = {}
        for isel, sel in enumerate(["Wc","TT","DY"]):
            fitC.cd(isel*2+1)
            data = mergedDict[dist][rng][sel]["data"]
            stackPre[sel] = THStack("stack_%s"%sel,sel)            
            for fl in ["l","b","c"]:
                hist = mergedDict[dist][rng][sel][fl].Clone()
                hist.GetXaxis().SetRangeUser(0.,1.)
                stackPre[sel].Add(hist)
            stackPre[sel].SetTitle(sel)
            stackPre[sel].SetMaximum(data.GetMaximum()*1.2)                
            stackPre[sel].Draw("hist e")
            dataPre[sel] = data.Clone()
            dataPre[sel].SetMarkerStyle(20)
            dataPre[sel].SetMarkerSize(1.8)
            dataPre[sel].Draw("p same")
            
        stackPost = {}
        dataPost = {}
        for isel, sel in enumerate(["Wc","TT","DY"]):
            fitC.cd(isel*2+2)
            data = mergedDict[dist][rng][sel]["data"]
            stackPost[sel] = THStack("stack_%s"%sel,sel)            
            for fl in ["l","b","c"]:
                hist = applyWts(mergedDict[dist][rng][sel][fl],SFResults[dist][rng][fl]).Clone()
                hist.GetXaxis().SetRangeUser(0.,1.)
                stackPost[sel].Add(hist)
            stackPost[sel].SetTitle(sel)
            stackPost[sel].SetMaximum(data.GetMaximum()*1.2)                
            stackPost[sel].Draw("hist e")
            dataPost[sel] = data.Clone()
            dataPost[sel].SetMarkerStyle(20)
            dataPost[sel].SetMarkerSize(1.8)
            dataPost[sel].Draw("p same")
        outname = "%s/Fit_%s+%s.png"%(workdir,dist,rng)            
        fitC.SaveAs(outname)

        #---------------------------------------------------------------
        
        #del sig, bkg, sigData, dataPost, dataPre, hist, ratioH, ratios, datas, sigs
# ==================================================================

if inputrange == "comb":
    SFResults = {}
    pkllist = sorted(glob("%s/SFs_*.pkl"%workdir))
    for fl in pkllist:
        unpack = pickle.load(open(fl,"rb"))
        flname = fl.split("/")[-1]
        if "m1" in flname:
            SFm1,SFm1Err = unpack
        else:
            for key in unpack:
                if key not in SFResults: SFResults[key] = {}
                for key2 in unpack[key]:
                    SFResults[key][key2] = unpack[key][key2]
                    print "Reading:", key, key2

elif inputrange!="":
    pickle.dump(SFResults,open("%s/SFs_%s.pkl"%(workdir,inputrange),"wb"))
    sys.exit(0)


# ======================= Export SFs ========================   
w = 1./nBins

def exportSF(SFvals,flname,title,unc=False,minus1=1.0):
    sfhist = TH2F("SF",title,nBins,0.,1.,nBins,0.,1.)
    for ix in range(nBins):
        for iy in range(nBins):
            sfhist.Fill(ix*w+w/2,iy*w+w/2,SFvals[ix,iy])
    sfhist.SetBinContent(0,0,minus1)
    sfhist.SetMinimum(0.)       
    if unc: sfhist.SetMaximum(1.)   
    else: sfhist.SetMaximum(2.)   
    sfhist.GetXaxis().SetTitle("%s CvsL"%deepSuff)
    sfhist.GetYaxis().SetTitle("%s CvsB"%deepSuff)
    sfcanv = TCanvas("sf","sf",1200,1200)
    gStyle.SetPaintTextFormat("4.3f")
    sfcanv.cd()    
    sfhist.Draw("colz")
    sfcanv.SaveAs(indir+"/%s/"%resultsname+flname+".png")
    outfl = TFile.Open(indir+"/%s/"%resultsname+flname+".root","RECREATE")
    sfhist.Write()
    outfl.Close()

for flav in ['c','b','l']:
    SFcvsl = np.zeros([nBins,nBins])
    SFcvsb = np.zeros([nBins,nBins])
    SFcomblist = np.zeros([nBins,nBins])
    
    SFcvslunc = np.zeros([nBins,nBins])
    SFcvsbunc = np.zeros([nBins,nBins])
    
    for ix in range(nBins):
        for iy in range(nBins):
            x = w*ix+w/2
            y = w*iy+w/2     
            for rng in SFResults["%sCvsL"%deepSuff]:
                low = float(rng.split('-')[0])
                high = float(rng.split('-')[1])
                if y >= low and y < high:
                    dist = SFResults["%sCvsL"%deepSuff][rng][flav]
                    bins = dist[0]
                    SF = dist[1]
                    SFerr = dist[2]
                    yeL = (high-low)/2
                    for iSF in range(len(SF)):
                        if x >= bins[iSF] and x < bins[iSF+1]:
                            SFvalL = SF[iSF]
                            SFuncL = SFerr[iSF]
                            xeL = (bins[iSF+1]-bins[iSF])/2
                            break
                    break
            '''for rng in SFResults["%sCvsB"%deepSuff]:
                low = float(rng.split('-')[0])
                high = float(rng.split('-')[1])
                if x >= low and x < high:
                    dist = SFResults["%sCvsB"%deepSuff][rng][flav]
                    bins = dist[0]
                    SF = dist[1]
                    SFerr = dist[2]
                    xeB = (high-low)/2
                    for iSF in range(len(SF)):
                        if y >= bins[iSF] and y < bins[iSF+1]:
                            SFvalB = SF[iSF]
                            SFuncB = SFerr[iSF]
                            yeB = (bins[iSF+1]-bins[iSF])/2
                            break
                    break            
            a = SFvalL
            b = SFuncL*xeL*yeL
            c = SFvalB
            d = SFuncB*xeB*yeB
            SFcomb = (a*d*d+b*b*c)/(b*b+d*d)
            SFcombunc = ((SFuncL**2+SFuncB**2)**0.5)/2
            SFcombunc2 = 1./((1./(SFuncL*SFuncL)+1./(SFuncB*SFuncB))**0.5)
            SFcombunc3 = (((1./b**2)*(SFvalL-SFcomb)**2+(1./d**2)*(SFvalB-SFcomb)**2)/(1./b**2+1./d**2))**0.5
            #if SFcombunc3>0.2: print x,y,SFvalL,SFuncL,SFvalB,SFuncB,SFcomb,SFcombunc,SFcombunc2,SFcombunc3
            '''
            SFcvsl[ix,iy] = SFvalL
            #SFcvsb[ix,iy] = SFvalB
            SFcvslunc[ix,iy] = SFuncL
            #SFcvsbunc[ix,iy] = SFuncB
            #SFcomblist[ix,iy] = SFcomb
            
    exportSF(SFcvsl,"SF%s_%sCvsL"%(flav,deepSuff),"SF%s in bins of CvsB"%flav,minus1=SFm1[flav])
#    exportSF(SFcvsb,"SF%s_%sCvsB"%(flav,deepSuff),"SF%s in bins of CvsL"%flav,minus1=SFm1[flav])
    exportSF(SFcvslunc,"SF%s_%sCvsL_unc"%(flav,deepSuff),"Uncertainty in SF%s in bins of CvsB"%flav,unc=True,minus1=SFm1Err[flav])
#    exportSF(SFcvsbunc,"SF%s_%sCvsB_unc"%(flav,deepSuff),"Uncertainty in SF%s in bins of CvsL"%flav,unc=True,minus1=SFm1Err[flav])
    #exportSF(SFcomblist,"SF%s"%flav,"SF%s"%flav)
    #plt.imshow(SFcvsl)
    #plt.show()
    #plt.imshow(SFcvsb)
    #plt.show()
    
# ==================================================================

#for flav in ['c','b','l']:  
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    #markers = ['o','^']
    #cols = ["red","blue"]
    
    #for ids, dist in enumerate(SFResults):  
        #xs = []
        #xerr = []
        #ys = []
        #yerr = []
        #zs = []
        #zerr = []
        #for rng in SFResults[dist]:
            #low = float(rng.split('-')[0])
            #high = float(rng.split('-')[1])
            #if "CvsL" in dist:
                #y = (low+high)/2
                #ye = (high-low)/2
            #else:
                #x = (low+high)/2
                #xe = (high-low)/2
            
            #bins = SFResults[dist][rng][flav][0]
            #SF = SFResults[dist][rng][flav][1]
            #SFerr = SFResults[dist][rng][flav][2]
            #for iSF in range(len(SF)):
                #binmid = (bins[iSF]+bins[iSF+1])/2
                #binerr = (bins[iSF+1]-bins[iSF])/2
                #if "CvsL" in dist:
                    #x = binmid
                    #xe = binerr
                #else:
                    #y = binmid
                    #ye = binerr
                #z = SF[iSF]
                #xs.append(x)
                #xerr.append(xe)
                #ys.append(y)
                #yerr.append(ye)
                #zs.append(z)
                #zerr.append(SFerr[iSF])
        ##dx = [0.005]*len(xs)
        ##dy = [0.005]*len(ys)
        #dz = [0.005]*len(zs)
        #ax.bar3d(np.array(xs)-np.array(xerr), np.array(ys)-np.array(xerr), zs, np.array(xerr)*2, np.array(yerr)*2, dz, color = cols[ids]) #marker = markers[ids],
    #for i in np.arange(0, len(xs)):
        #ax.plot([xs[i], xs[i]], [ys[i], ys[i]], [zs[i]+zerr[i], zs[i]-zerr[i]], marker="_",c = "black")
        ##ax.plot([xs[i]-xerr[i], xs[i]+xerr[i]], [ys[i], ys[i]], [zs[i], zs[i]], marker="_",c = "black")
        ##ax.plot([xs[i], xs[i]], [ys[i]-yerr[i], ys[i]+yerr[i]], [zs[i], zs[i]], marker="_",c = "black")
    #ax.set_xlabel('CvsL')
    #ax.set_ylabel('CvsB')
    #ax.set_zlabel('SF')
    #ax.set_zlim3d(0, 2.5)
    #plt.title("SF %s"%flav)
    
    #def poly2D(x,y,px,py):
        #return poly.polyval(x,px) + poly.polyval(y,py)
    
    #plt.show()

    
# 
