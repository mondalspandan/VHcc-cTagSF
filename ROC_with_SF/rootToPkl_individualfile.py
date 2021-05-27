import os, sys
import uproot 
#import pyxrootd
import pandas as pd 
import numpy as np
from glob import glob
'''
fli17 = [
   '/store/mc/RunIIFall17NanoAODv5/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/30000/FF1AB135-0861-C748-939E-AC7C90C0C8A3.root',
'/store/mc/RunIIFall17NanoAODv5/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/30000/FE189D18-A28E-DE42-B03D-5A1945AA833C.root',
'/store/mc/RunIIFall17NanoAODv5/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/30000/FAE936D1-0264-0B48-8F62-932718C1DA06.root',
'/store/mc/RunIIFall17NanoAODv5/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/30000/F90416C2-DCBD-B049-9210-E58316149320.root',
]

flist17 = [ "root://xrootd-cms.infn.it//"+f for f in fli17]
'''
di= "/pnfs/desy.de/cms/tier2//store/mc/RunIIFall17NanoAODv5/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/"
#di="/nfs/dust/cms/user/spmondal/ROC_with_SF/"
#di='/pnfs/desy.de/cms/tier2//store/mc/RunIIAutumn18NanoAODv7/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/'

flist17 = glob(di+"*/*.root")


infile = sys.argv[1]

#print flist17
branches = [
"Jet_btagDeepFlavC",
"Jet_btagDeepFlavB",
#"Jet_btagDeepFlavUDS",
"Jet_btagDeepC",
"Jet_btagDeepB",
"Jet_pt",
"Jet_btagCMVA",
"Jet_btagCSVV2",
#"GenJet_hadronFlavour",
"Jet_qgl",
"Jet_hadronFlavour",
"Jet_partonFlavour",
"Jet_jetId",
"Jet_puId",
"Jet_eta",
"Jet_phi"]

outdir = "/nfs/dust/cms/user/spmondal/ROOTtoPKL"
os.system("mkdir -p "+outdir)

outf = "%s/%s.pkl"%(outdir,infile.split("/")[-1].rstrip('.root'))

sumdf = pd.DataFrame()
for df in uproot.iterate(infile, 'Events', 
    branches,
    entrysteps=300000,
    flatten=True,
    outputtype=pd.DataFrame
                        ):
    
    print(df.shape)
    sumdf = pd.concat([sumdf, df])

print "Total:", sumdf.shape
sumdf.to_pickle(outf) 
