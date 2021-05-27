from ROOT import TFile

SFfile = ""
hists = {}
systlist = []

def loadFile(flname):
    global SFfile, hists, systlist
    SFfile = TFile(flname,"READ")
    
    if not SFfile or SFfile.IsZombie():
        raise ValueError('cTagSFReader: File %s is not found or corrupted.'%flname)
    
    histnamelist = [i.GetName() for i in SFfile.GetListOfKeys()]
    for hname in histnamelist:
        hists[hname] = SFfile.Get(hname)
        if len(hname.split('_')) > 2:
            systlist.append('_'.join(hname.split('_')[2:]))
        
    print "cTagSFReader: Loaded SF root file %s"%flname
    systlist = sorted(list(set(systlist)))

def getSysts():
    return systlist
    
def getSF(flav,cvsl,cvsb,syst=""):
    
    if flav not in [0, 4, 5, "l", "b", "c"]:
        raise ValueError('cTagSFReader: Incorrect value for flavour: %s'%flav)
        
    if flav in [0,"l"]:
        flavpref = "l"
    elif flav in [4,"c"]:
        flavpref = "c"
    elif flav in [5,"b"]:
        flavpref = "b"
    
    if syst == "" or syst == "central": systsuff = ""
    else: systsuff = '_'+syst
        
    if cvsl >= 1:
#        print "cTagSFReader: Warning: Requested CvsL = %f, using 0.999999 instead."%cvsl
        cvsl = 0.999999
    if cvsb >= 1:
#        print "cTagSFReader: Warning: Requested CvsB = %f, using 0.999999 instead."%cvsb
        cvsb = 0.999999
        
    hname = "SF%s_hist%s"%(flavpref,systsuff)
    
    if hname not in hists:
        raise ValueError('cTagSFReader: Incorrect value for systematic: %s. Histogram %s not found.'%(syst,hname))
    
    hist = hists[hname]
    xbin = hist.GetXaxis().FindBin(cvsl)
    ybin = hist.GetYaxis().FindBin(cvsb)
    
    SF = hist.GetBinContent(xbin,ybin)
    
    if "Stat" in syst: return abs(SF - getSF(flav,cvsl,cvsb))
    return SF