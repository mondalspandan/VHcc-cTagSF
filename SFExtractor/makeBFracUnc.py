from ROOT import TFile
import sys, os

indir = sys.argv[1]
direction = sys.argv[2]

centraldir = [i for i in os.listdir(indir) if i.endswith("central")][0]

dirpred = centraldir.rstrip("central")
updir = dirpred+"bFrag_up"
downdir = dirpred+"bFrag_down"

if direction == "up": subdir = updir
elif direction == "down": subdir = downdir
else:
    print "Usage: python makeBFracUnc.py path/to/parent/dir up[/down]"
    sys.exit(1)
thisdir = "%s/%s/"%(indir,subdir)
os.system("mkdir -p "+thisdir)
os.system("scp %s/%s/*.root %s"%(indir,centraldir,thisdir))

rootfiles = [i for i in os.listdir(thisdir) if i.endswith(".root") and not i.endswith("_.root")]
for root in rootfiles:
    if "DeepFlav" in root:
        print "Using DeepJet params."
        if subdir == updir:
            a1 = .948
            a2 = .078
            a3 = .020
        else:
            a1 = 1.042
            a2 = -.063
            a3 = -.015
    else:
        print "Using DeepCSV params."
        if subdir == updir:
            a1 = .986
            a2 = .056
            a3 = -.034
        else:
            a1 = 1.009
            a2 = -.044
            a3 = 0.030
    fl = TFile.Open(thisdir+root,"UPDATE")
    CvsBrange = root.rstrip(".root").split('_')[-1].split('-')
    low = float(CvsBrange[0])
    high = float(CvsBrange[1])
    CvsBval = (high+low)/2
    b = fl.Get("b")
    MCSum = fl.Get("MCSum")
    for ibin in range(11,61):
        cvllow = b.GetXaxis().GetBinLowEdge(ibin)
        cvlhigh = b.GetXaxis().GetBinLowEdge(ibin+1)
        CvsLval = (cvllow+cvlhigh)/2

        oldval = b.GetBinContent(ibin)
        newval = oldval/(a1+(a2*CvsLval)+(a3*CvsBval))
        b.SetBinContent(ibin,newval)
        MCSum.SetBinContent(ibin,MCSum.GetBinContent(ibin)-oldval+newval)

    fl.Write("",TFile.kOverwrite)
    fl.Close()
print "Done with",subdir

