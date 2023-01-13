from ROOT import TFile
import sys,os
indir = sys.argv[1]

rtfiles = [i for i in os.listdir(indir) if i.endswith('.root')]
print "Filename MCVal DataVal"
for rt in sorted(rtfiles):
    rf = TFile.Open(indir+"/"+rt,"READ")
    MCval = rf.Get("MCSum").Integral()
    DataVal = rf.Get("Data").Integral()
    print MCval,DataVal
