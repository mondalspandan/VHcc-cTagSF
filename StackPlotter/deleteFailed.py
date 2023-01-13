import glob, os, sys
from ROOT import TFile

idir = sys.argv[1]

files = glob.glob(idir+"/*/*.root")

for f in files:
  rf = TFile.Open(f,"READ")
  if not rf: 
    newdir = "%s/failed/%s"%(idir,f.split('/')[-2])
    os.system("mkdir -p "+newdir)
    os.system("mv %s %s"%(f,newdir))
