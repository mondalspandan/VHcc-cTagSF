from ROOT import *
import sys, os, math, numpy as np
from tabulate import tabulate

indir = sys.argv[1]

subdirs = [os.path.join(indir,i) for i in os.listdir(indir) if os.path.isdir(os.path.join(indir,i)) and "compare" not in i]

SDvals = {}

skipBins = [1,2,4,5]

        
for subdir in subdirs:
    rootlist = [os.path.join(subdir,i) for i in os.listdir(subdir) if i.endswith(".root")]

    def get_wted_mean_std(values, weights):    
        average = np.average(values, weights=weights)
        variance = np.average((values-average)**2, weights=weights)
        return average, math.sqrt(variance)
        
    def get_std_usingerr(values, weights, inverrorsq):    
        average = np.average(values, weights=weights)
#        print values
#        print weights
#        print average
#        print (values-average)
#        print inverrorsq
        variance = np.average((values-average)**2, weights=inverrorsq)
        return math.sqrt(variance)

#    WcEfiles = []
#    WcMfiles = []
#    TTSemiEfiles = []
#    TTSemiMfiles = []
#    TTEEfiles = []
#    TTMMfiles = []
#    TTMEfiles = []
#    DYfiles = []

#    for fl in rootlist:
#        if 'is_E_' in fl and 'nJet_0-4' in fl:
#            WcEfiles.append(fl)
#        elif 'is_M_' in fl and 'nJet_0-4' in fl:
#            WcMfiles.append(fl)
#        elif 'is_E_' in fl and 'nJet_5-' in fl:
#            TTSemiEfiles.append(fl)
#        elif 'is_M_' in fl and 'nJet_5-' in fl:
#            TTSemiMfiles.append(fl)
#        elif 'is_ME_' in fl:
#            TTMEfiles.append(fl)
#        elif 'is_MM_' in fl:
#            TTMMfiles.append(fl)
#        elif 'is_EE_' in fl:
#            TTEEfiles.append(fl)
#        else:
#            DYfiles.append(fl)

    def getsampname(fl):
#        if fl in WcEfiles:
#            name =  "WcE"
#        if fl in WcMfiles:
#            name =  "WcM"
#        if fl in TTSemiEfiles:
#            name =  "TTSemiE"
#        if fl in TTSemiMfiles:
#            name =  "TTSemiM"
#        if fl in TTMMfiles:
#            name =  "TTMM"
#        if fl in TTMEfiles:
#            name =  "TTME"
#        if fl in TTEEfiles:
#            name =  "TTEE"
#        if fl in DYfiles:
#            name =  "DY"
        fl2 = fl.split('/')[-1]
        name = ''.join(fl2.split('_')[:2])
        if "CvsL" in fl2: name = "CvsL_" + name
        if "CvsB" in fl2: name = "CvsB_" + name
        return name
    
    dirname = '_'.join(subdir.rstrip('/').split('/')[-1].split('_')[2:])
    SDvals[dirname] = {}
    for fl in sorted(rootlist):
        fl2 = fl.split('/')[-1]
        if "CvsL" not in fl2 and "CvsB" not in fl2: continue
        inp = TFile.Open(fl)
        hList = [i.GetName() for i in inp.GetListOfKeys()]
        if "Data" not in hList or "MCSum" not in hList or inp.Get("Data").ClassName() == "TH2F":
            print "Skipping",fl
            continue
        hData = inp.Get("Data")
        hMC = inp.Get("MCSum")        
        ratio = hData.Clone()
        ratio.Divide(hMC)
#        if "Wc" in getsampname(fl):
#            print hData.GetBinContent(1),hData.GetBinError(1), hMC.GetBinContent(1), hMC.GetBinError(1), ratio.GetBinContent(1), ratio.GetBinError(1)
        datavals = []
        ratiovals = []
        inverrsqvals = []
        for ibin in range(1,ratio.GetNbinsX()+1):
            if ibin in skipBins: continue
            datavals.append(hData.GetBinContent(ibin))
            ratiovals.append(ratio.GetBinContent(ibin))
            if hData.GetBinContent(ibin) > 0 and hData.GetBinError(ibin) > 0 and ratio.GetBinError(ibin) > 0:
                inverrsqvals.append(1./ratio.GetBinError(ibin)**2)
#                inverrsqvals.append(1./hData.GetBinContent(ibin))
#                if ratio.GetBinContent(ibin) == 0.: print hData.GetBinError(ibin)
            else:
                inverrsqvals.append(0.)
            
#        SDvals[dirname][getsampname(fl)] = get_wted_mean_std(ratiovals,datavals)[1]
        SDvals[dirname][getsampname(fl)] = get_std_usingerr(ratiovals,inverrsqvals,inverrsqvals)
#        print

table = []
oldcolname = []
for dirname in ["central"]+sorted(SDvals):
    row = [' '.join(dirname.split('_'))] 
    colnames = ["SF_Name"]    
    for selname, sds in sorted(SDvals[dirname].iteritems()):
        row.append(sds)
        colnames.append(selname)
    table.append(row)
#    print colnames
    if oldcolname ==[]: oldcolname=colnames
    if colnames!= oldcolname:
        print "WARNING: Mismatch"
print tabulate(table,headers=colnames)

print "\n\n"
table2=[]
for irow in range(1,len(table)):
    row2=[table[irow][0]]
    for icol in range(1,len(table[irow])):
        dSF = (table[irow][icol]-table[0][icol])/table[0][icol]*100
        row2.append(dSF)
    table2.append(row2)
print tabulate(table2,headers=colnames)
