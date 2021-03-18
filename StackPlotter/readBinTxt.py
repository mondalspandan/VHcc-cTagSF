import os, sys
from ROOT import *
from scipy.optimize import minimize

minus1binIdx = 3
firstbinIdx = 6
lastbinIdx = 30

def evalExpr(expr):
    return sum([eval(i) for i in expr.split(" + ")])
    
def evalMCSum(expr,SFlist):
    count = 0
    for a in ['c','b','l']:
        exec("%s00 = %f"%(a,SFlist[count]))
        count +=1 
        for x in range(1,6):
            for y in range(1,6):
                exec("%s%d%d = %f"%(a,x,y,SFlist[count]))
                count +=1
    return eval(expr) #sum([eval(i) for i in expr.split(" + ")])
    
def chi2(SFlist,MCSumList,MCUncList,DataValList,DataUncList,DataMCRatio):
    sm = 0.
    for ibin in range(len(MCSumList)):
        MCSum = evalMCSum(MCSumList[ibin],SFlist)
        MCUnc = MCUncList[ibin]
        DataVal = DataValList[ibin]
        DataUnc = DataUncList[ibin]
        
        sm += (DataVal - MCSum*DataMCRatio)**2/(MCUnc**2+DataUnc**2)
    print SFlist,sm
    return sm
        

if len(sys.argv) < 2:
    print "Usage: python readBinTxt.py directory"
    sys.exit(1)
    
direc = sys.argv[1]

rootlist = [i for i in os.listdir(direc) if "Cvs" in i and i.endswith(".root")]
txtlist = [i for i in os.listdir(direc) if "Cvs" in i and i.endswith(".txt")]

dataMCRatioDict = {}
MCFixedDict = {}
MCUncDict = {}
DataValDict = {}
DataUncDict = {}

for rootfl in sorted(rootlist):
    rf = TFile.Open(direc+"/"+rootfl,"READ")
    MCSum = rf.Get("MCSum")
    Data =  rf.Get("Data")
    
    MCFixedList = []
    MCUncList = []
    DataValList = []
    DataUncList = []
    DataMCRatio = Data.Integral()/MCSum.Integral()
    
    
    MCUncList.append(MCSum.GetBinError(minus1binIdx))
    DataUncList.append(Data.GetBinError(minus1binIdx))
    MCFixedList.append(MCSum.GetBinContent(minus1binIdx))
    DataValList.append(Data.GetBinContent(minus1binIdx))
    
    for ibin in range(firstbinIdx,lastbinIdx+1):
        MCUncList.append(MCSum.GetBinError(ibin))
        DataUncList.append(Data.GetBinError(ibin))
        MCFixedList.append(MCSum.GetBinContent(ibin))
        DataValList.append(Data.GetBinContent(ibin))
        
    fl = rootfl.rstrip(".root")
    dataMCRatioDict[fl] = DataMCRatio
    MCFixedDict[fl] = MCFixedList
    MCUncDict[fl] = MCUncList
    DataValDict[fl] = DataValList
    DataUncDict[fl] = DataUncList
    
    rf.Close()
    
for txtfl in sorted(txtlist):
    fl = txtfl.rstrip(".txt")
    os.system("rm -f temp.py")
    os.system("cp %s/%s temp.py"%(direc,txtfl))
    
    import temp
    nBins = len(MCUncList)
    MCSumList = []
    for ibin in range(nBins):
        sumtxt = ""
        for sampname in temp.normFact:
            iTxt = temp.binWtDict[sampname][str(ibin)]
            if iTxt=="": continue
#            sumtxt += "(%s)*%f  +  "%(iTxt,temp.normFact[sampname])
            sumtxt += iTxt.replace(' + ', '*%f + '%temp.normFact[sampname])+'*%f + '%temp.normFact[sampname]
        sumtxt = sumtxt.rstrip(" + ")
        if sumtxt == "": sumtxt = "0"
        
        termdict = {}
        for iterm in sumtxt.split(" + "):            
            coeff = '*'.join(sorted(iterm.split('*')[:-2]))
            num = eval('*'.join(iterm.split('*')[-2:]))
            if coeff not in termdict:
                termdict[coeff] = num
#                print iterm, coeff, num
            else:
                termdict[coeff] += num
            
        newsum = ""
        for coeff in termdict:
            newsum += "%s*%f + "%(coeff,termdict[coeff])
        newsum = newsum.rstrip(" + ")
        if newsum == "": newsum = "0"
        MCSumList.append(newsum)
#    for ibin in range(len(MCSumList)):
#        expr = MCSumList[ibin]
##        for x in range(-1,6):
##            for y in range(-1,6):
##                expr = expr.replace("c%d%d*"%(x,y),"1.*").replace("b%d%d*"%(x,y),"1.*").replace("l%d%d*"%(x,y),"1.*")
#        val = evalMCSum(expr,[1.]*78)
#        print val    
#    print MCFixedDict[fl]
    print fl
    res = minimize(chi2,[1.]*(nBins*3),(MCSumList,MCUncDict[fl],DataValDict[fl],DataUncDict[fl],dataMCRatioDict[fl]),method='SLSQP',bounds=[(0.5,2.)]*(nBins*3),options = {'eps': .01})
    print res
    break
