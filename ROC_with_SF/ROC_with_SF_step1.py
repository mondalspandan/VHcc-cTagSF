import pickle, os, sys, mplhep as hep, numpy as np
from sklearn.metrics import roc_curve
from cTagSFReaderv2 import *
import matplotlib.pyplot as plt
from ROOT import TFile

if "2018" in sys.argv:
    dcsvFile = "DeepCSV_ctagSF_MiniAOD102X_2018_pTincl.root"
    djetFile = "DeepJet_ctagSF_MiniAOD102X_2018_pTincl.root"
else:
    dcsvFile = "DeepCSV_ctagSF_MiniAOD94X_2017_pTincl_v3_2_interp.root"
    djetFile = "DeepJet_ctagSF_MiniAOD94X_2017_pTincl_v3_2_interp.root"

def getSysts(flname):
    systlist = []
    SFfile = TFile(flname,"READ")    
    if not SFfile or SFfile.IsZombie():
        raise ValueError('cTagSFReader: File %s is not found or corrupted.'%flname)
    
    histnamelist = [i.GetName() for i in SFfile.GetListOfKeys()]
    
    for hname in histnamelist:
        #hists[hname] = SFfile.Get(hname)
        if len(hname.split('_')) > 2:
            systlist.append('_'.join(hname.split('_')[2:]))
            
    systlist = sorted(list(set(systlist)))
    
    return systlist


#print sys.path
infile = "/net/scratch_cms3a/mondal/ROC_with_SF/"
infile += "ttbar_had_nan.pkl"  #'nanott17.pkl'
if "2018" in sys.argv:
    infile += "ttbar_had_nan_18.pkl"
with open(infile, 'rb') as f:
    df17 = pickle.load(f)

#Remove weird deepcsv events
def cleandf(tdf):
    cdf = tdf[(tdf['Jet_btagDeepB'] < 1) & (tdf['Jet_btagDeepC'] < 1)
             & (tdf['Jet_btagDeepB'] > 0) & (tdf['Jet_btagDeepC'] > 0) 
             & (abs(tdf['Jet_eta']) < 2.5)]#&(tdf.fj_sdmass < mhigh) & (tdf.fj_sdmass>mlow)]
    cdf = cdf[:3000000]
    return cdf

df17 = cleandf(df17)

systs = getSysts(dcsvFile)
print "DeepCSV systematics:", systs

for df in [df17]:
    df['fj_pt'] = df['Jet_pt']
    df['truthb'] = (df['Jet_hadronFlavour'] == 5).astype(int)
    df['predictb'] = (df['Jet_hadronFlavour'] == 5).astype(int)
    df['truthc'] = (df['Jet_hadronFlavour'] == 4).astype(int)
    df['predictc'] = (df['Jet_hadronFlavour'] == 4).astype(int)
    df['truthudsg'] = (df['Jet_hadronFlavour'] < 4).astype(int)
    df['predictudsg'] = (df['Jet_hadronFlavour'] < 4).astype(int)
    #df['truthuds'] = ((df['Jet_hadronFlavour'] < 4) & ((abs(df['Jet_partonFlavour']) == 1) | (abs(df['Jet_partonFlavour']) == 2) | (abs(df['Jet_partonFlavour']) == 3)) ).astype(int)
    #df['predictuds'] = ((df['Jet_hadronFlavour'] < 4) & ((abs(df['Jet_partonFlavour']) == 1) | (abs(df['Jet_partonFlavour']) == 2) | (abs(df['Jet_partonFlavour']) == 3)) ).astype(int)
    #df['truthg'] = ((df['Jet_hadronFlavour'] < 4) & (df['Jet_partonFlavour'] == 21)).astype(int)
    #df['predictg'] = ((df['Jet_hadronFlavour'] < 4) & (df['Jet_partonFlavour'] == 21)).astype(int)
    
    df['dCvL'] = df['Jet_btagDeepC']/(1 - df['Jet_btagDeepB'])
    df['dCvB'] = df['Jet_btagDeepC']/(df['Jet_btagDeepC'] + df['Jet_btagDeepB'])
    df['dBvL'] = df['Jet_btagDeepB']/(1 - df['Jet_btagDeepC'])
    df['dBvC'] = df['Jet_btagDeepB']/(df['Jet_btagDeepC'] + df['Jet_btagDeepB'])
    
    
    for syst in ["central"]+systs:
        if "StatDown" in syst: continue        
        df['DeepCSVWt_'+syst] = getSF(df['Jet_hadronFlavour'].values, df['dCvL'].values, df['dCvB'].values, dcsvFile, syst)
        #df['DeepCSVWt_'+syst] = df.apply(lambda x: getSF(x['Jet_hadronFlavour'], x['dCvL'], x['dCvB'], syst), axis=1, result_type='expand')
    
    #df['dCplusB'] = df['Jet_btagDeepC']+df['Jet_btagDeepB']
    
    df['CSVv2BvL'] = df['Jet_btagCSVV2']
    
#print df[df['dCplusB'] > 1]
systs = getSysts(djetFile)
print "DeepJet systematics:", systs

for df in [df17]:
    #df['dfBvL'] = df['Jet_btagDeepFlavB']
    df['dfCvL'] = df['Jet_btagDeepFlavC']/(1 - df['Jet_btagDeepFlavB'])
    df['dfCvB'] = df['Jet_btagDeepFlavC']/(df['Jet_btagDeepFlavC'] + df['Jet_btagDeepFlavB'])
    df['dfBvL'] = df['Jet_btagDeepFlavB']/(1 - df['Jet_btagDeepFlavC'])
    df['dfBvC'] = df['Jet_btagDeepFlavB']/(df['Jet_btagDeepFlavC'] + df['Jet_btagDeepFlavB'])
    #df['dfCvUDS'] = df['Jet_btagDeepFlavC']/(df['Jet_btagDeepFlavC'] +  df['Jet_btagDeepFlavUDS'])
    #df['dfCvG'] = df['Jet_btagDeepFlavC']/(1 - df['Jet_btagDeepFlavB'] - df['Jet_btagDeepFlavUDS'])
    #df['dfUDSvG'] = df['Jet_btagDeepFlavUDS']/(1 - df['Jet_btagDeepFlavB'] - df['Jet_btagDeepFlavC'])
    
    for syst in ["central"]+systs:
        if "StatDown" in syst: continue
        df['DeepFlavWt_'+syst] = getSF(df['Jet_hadronFlavour'].values, df['dfCvL'].values, df['dfCvB'].values, djetFile, syst)
        #df['DeepFlavWt_'+syst] = df.apply(lambda x: getSF(x['Jet_hadronFlavour'], x['dfCvL'], x['dfCvB'], syst), axis=1, result_type='expand')
    
    #df['dfCplusB'] = df['Jet_btagDeepFlavC']+df['Jet_btagDeepFlavB']

print df.head
if "2018" in sys.argv:
    flname = "nanott18.pkl"
else:
    flname = "nanott17_small_interp.pkl"
df17.to_pickle("/net/scratch_cms3a/mondal/ROC_with_SF/"+flname) #,'df') #,mode='w')
