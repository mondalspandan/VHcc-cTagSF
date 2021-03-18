from ROOT import *
from array import array

import glob, sys, time, os, sys
import numpy as np
import nuSolutions as nu
import types, math, json
import itertools

start_time = time.time()
############### FOR INTERACTIVE RUN ##############
# fileName = "/store/user/lmastrol/VHcc_2016V4_Aug18/JetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/arizzi-RunIIMoriond17-DeepAndR105/180909_010329/0000/tree_1.root"
#fileName = "/store/user/lmastrol/VHcc_2016V4_Aug18/SingleElectron/arizzi-NanoDeepAndReg2016Run2094/180817_113615/0000/tree_122.root"
# channel  = 'JetsToLNu'
#version = 'v2'
##################################################

start_time = time.time()
JECNameList = ["nom","jesTotalUp","jesTotalDown","jerUp","jerDown"]

# ==================== File stuff and condor compatibility =====================
fileName = str(sys.argv[1])
fullName = fileName
isLocal = False
if len(sys.argv) > 2:
    JECidx = int(sys.argv[2])
else:
    JECidx = 0
JECName = JECNameList[JECidx]

maxEvents=-1

print "#########"*10
print "start_time : ",time.ctime()
print "processing on : ",fullName

debug = False
isNano = False
pref = ""
parentDir = ""
era = 2016

pnfspref = "/pnfs/desy.de/cms/tier2/"

if os.path.isfile(fullName):
    pref = ""
elif os.path.isfile(pnfspref+fullName):
    pref = pnfspref    
elif fullName.startswith("root:"):
    pref = ""
    print "Input file name is in AAA format."
else:
    pref = "root://xrootd-cms.infn.it//"
    print "Forcing AAA."
    if not fullName.startswith("/store/"):
        fileName = "/" + '/'.join(fullName.split('/')[fullName.split('/').index("store"):])
print "Will open file %s."%(pref+fileName)

parentDirList = ["VHcc_2017V5_Dec18/","NanoCrabProdXmas/","/2016/","2016_v2/","/2017/","2017_v2","/2018/","VHcc_2016V4bis_Nov18/"]
for iParent in parentDirList:
    if iParent in fullName: parentDir = iParent
if parentDir == "": fullName.split('/')[8]+"/"

if "2017" in fullName: era = 2017
if "2018" in fullName: era = 2018

#if "spmondal" in fullName and fullName.startswith('/pnfs/'):
##    parentDir = 'VHbbPostNano2016_V5_CtagSF/'
    #parentDir = fullName.split('/')[8]+"/"
    #if "2017" in fullName: era = 2017
    #if "/2017/" in fullName: parentDir = "2017/"
        
#if "VHcc_2017V5_Dec18" in fullName and fullName.startswith('/pnfs/'):
    #parentDir = 'VHcc_2017V5_Dec18/'
    #era = 2017
#if fullName.startswith('/store/'):
    #if "lmastrol" in fullName:
        #pref = "/pnfs/desy.de/cms/tier2"
    #else:
        #pref = "root://xrootd-cms.infn.it//"
        #parentDir="NanoCrabProdXmas/"
        #isNano = True
#elif fullName.startswith('root:'):
    #pref = ""
#else:
    #pref = "file:"

iFile = TFile.Open(pref+fileName)

inputTree = iFile.Get("Events")
inputTree.SetBranchStatus("*",1)

sampName=fullName.split(parentDir)[1].split('/')[0]
channel=sampName
sampNo=fullName.split(parentDir)[1].split('/')[1].split('_')[-1]
dirNo=fullName.split(parentDir)[1].split('/')[3][-1]
flNo=fullName.split(parentDir)[1].split('/')[-1].rstrip('.root').split('_')[-1]
outNo= "%s_%s_%s"%(sampNo,dirNo,flNo)

if "_" in channel: channel=channel.split("_")[0]
# channel="Generic"
if not 'Single' in channel and not 'Double' in channel and not 'EGamma' in channel:
    isMC = True
else:
    isMC = False
print "Using channel =",channel, "; isMC:", isMC, "; era: %d"%era
print "Using jet pT with JEC correction:", JECName
print "Output file will be numbered", outNo, "by condor."

if not isMC and JECName!="nom":
    print "Cannot run data with JEC systematics!! Exiting."
    sys.exit()

dirName=open("dirName.sh",'w')
if isMC and JECName!="nom":
    sampName += "_"+JECName
dirName.write("echo \""+sampName+"\"")
dirName.close()

flName=open("flName.sh",'w')
flName.write("echo \"%s\""%outNo)
flName.close()

if "OUTPUTDIR" in os.environ:
    condoroutdir = os.environ["OUTPUTDIR"]
    condoroutfile = "%s/%s/outTree_%s.root"%(condoroutdir,sampName,outNo)
    if os.path.isfile("%s/%s/outTree_%s.root"%(condoroutdir,sampName,outNo)):
         print "Output file already exists. Aborting job."
         print "Outfile file: %s"%condoroutfile
         sys.exit(99)
# ==============================================================================

# =============================== SF files =====================================
# PU
# PU2016File = TFile('scalefactors/pileUPinfo2016.root')
# pileup2016histo = PU2016File.Get('hpileUPhist')

# EGamma
if era == 2016: EIDFile = TFile('scalefactors/egammaSF_mva80.root')
elif era == 2017: EIDFile = TFile('scalefactors2017/ElectronIDSF_94X_MVA80WP.root')
elif era == 2018: EIDFile = TFile('scalefactors2018/ElectronIDSF_2018_MVA80WP.root')
EGammaHisto2d = EIDFile.Get('EGamma_SF2D')

if era == 2017:
    ERecoFile = TFile('scalefactors2017/ElectronRecoSF_94X.root')
#    ETrigFile = TFile('scalefactors2017/Ele32_L1DoubleEG_TrigSF_vhcc.root')    
#    ETrigHisto = ETrigFile.Get('TrigSF')

if era == 2018:
    ERecoFile = TFile('scalefactors2018/ElectronRecoSF_2018.root')    

if era == 2017 or era == 2018:
    ERecoHisto2d = ERecoFile.Get('EGamma_SF2D')
    
    etrigf = open("scalefactors2017/VHbb1ElectronTrigger2017.json",'r')
    etrigjson = json.load(etrigf)["singleEleTrigger"]["eta_pt_ratio"]
    etrigf.close()

# Muon
if era == 2016:
    MuID2016BFFile = TFile('scalefactors/RunBCDEF_SF_ID.root')
    MuID2016BFhisto2d = MuID2016BFFile.Get('NUM_TightID_DEN_genTracks_eta_pt')
    MuID2016GHFile = TFile('scalefactors/RunGH_SF_ID.root')
    MuID2016GHhisto2d = MuID2016GHFile.Get('NUM_TightID_DEN_genTracks_eta_pt')

if era == 2017:
    MuID2017BFFile = TFile('scalefactors2017/RunBCDEF_SF_ID.root')
    MuID1718histo2d = MuID2017BFFile.Get('NUM_TightID_DEN_genTracks_pt_abseta')
    MuIso2017BFFile = TFile('scalefactors2017/RunBCDEF_SF_ISO.root')
    MuIso1718histo2d = MuIso2017BFFile.Get('NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta')
    MuTrig2017BFFile = TFile('scalefactors2017/singleMuonTrig.root')
    MuTrig1718histo2d = MuTrig2017BFFile.Get('IsoMu27_PtEtaBins/pt_abseta_ratio')
    MuIDlowpT2017BFFile = TFile('scalefactors2017/RunBCDEF_SF_MuID_lowpT.root')
    MuIDlowpT1718histo2d = MuIDlowpT2017BFFile.Get('NUM_TightID_DEN_genTracks_pt_abseta')

if era == 2018:
    MuID2018File = TFile('scalefactors2018/RunABCD_SF_ID.root')
    MuID1718histo2d = MuID2018File.Get('NUM_TightID_DEN_TrackerMuons_pt_abseta')
    MuIso2018File = TFile('scalefactors2018/RunABCD_SF_ISO.root')
    MuIso1718histo2d = MuIso2018File.Get('NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta')
    MuTrig2018File = TFile('scalefactors2018/singleMuonTrig.root')
    MuTrig1718histo2d = MuTrig2018File.Get('IsoMu24_PtEtaBins/pt_abseta_ratio')
    MuIDlowpT2018File = TFile('scalefactors2018/RunABCD_SF_MuID_lowpT.root')
    MuIDlowpT1718histo2d = MuIDlowpT2018File.Get('NUM_TightID_DEN_genTracks_pt_abseta')

def getSF(dict, pT, eta):
    for etas in dict:
        rng = etas.split(':')[1].strip('[').strip(']').split(',')
        if eta >= float(rng[0]) and eta <= float(rng[1]):
            subdict = dict[etas]
            for pTs in subdict:
                rng2 = pTs.split(':')[1].strip('[').strip(']').split(',')
                if pT >= float(rng2[0]) and pT <= float(rng2[1]):
                    tuple = subdict[pTs]
                    return tuple['value'],tuple['error']
            break
    return 1.,0.

#PU 2018 only
if era == 2018:
    PUdatafile = TFile('scalefactors2018/dataPileup2018.root')
    PUmcfile = TFile('scalefactors2018/mcPileup2018.root')
    hdataPU = PUdatafile.Get("pileup")
    hdataPU_up = PUdatafile.Get("pileup_plus")
    hdataPU_down = PUdatafile.Get("pileup_minus")
    hmcPU = PUmcfile.Get("pu_mc")
    hdataPU.Scale(1./hdataPU.Integral())
    hdataPU_up.Scale(1./hdataPU_up.Integral())
    hdataPU_down.Scale(1./hdataPU_down.Integral())
    hmcPU.Scale(1./hmcPU.Integral())
    maxpu = max(hdataPU.GetBinLowEdge(hdataPU.GetNbinsX()),hdataPU_up.GetBinLowEdge(hdataPU_up.GetNbinsX()),hdataPU_down.GetBinLowEdge(hdataPU_down.GetNbinsX()),hmcPU.GetBinLowEdge(hmcPU.GetNbinsX()))
    
    hpuweight = hdataPU.Clone()
    hpuweight.Divide(hmcPU)
    hpuweight_up = hdataPU_up.Clone()
    hpuweight_up.Divide(hmcPU)
    hpuweight_down = hdataPU_down.Clone()
    hpuweight_down.Divide(hmcPU)
    
def getPUweight(ntrueint,variation):
    if ntrueint < 0 or ntrueint > maxpu-1: return 0.
    if variation == 0: temppu = hpuweight
    elif variation == 1: temppu = hpuweight_up
    elif variation == -1: temppu = hpuweight_down
    else: raise ValueError
    return temppu.GetBinContent(temppu.GetXaxis().FindBin(ntrueint))

# ==============================================================================

oFile = TFile("outTree.root",'RECREATE')
oFile.cd()

# ====================== Declare leaf variables/vectors ========================
h_total = TH1F('h_total','h_total',2,0,2)
h_nEvent = TH1F('h_nEvent','h_nEvent',2,0,2)
h_postp = TH1F('h_postp','h_postp',2,0,2)

run              = array('d',[0])
lumiBlock        = array('d',[0])
event            = array('d',[0])
LHE_HT           = array('d',[0])
LHE_Njets        = array('d',[0])
LHE_Vpt          = array('d',[0])

eventWeight      = array('d',[0])
signWeight       = array('d',[0])
genWeight        = array('d',[0])
PUWeight         = array('d',[0])
EleIDSF          = array('d',[0])
MuIDSF           = array('d',[0])
eventWeightnoPU  = array('d',[0])
eventWeightUnsigned  = array('d',[0])

PUWeight_up         = array('d',[0])
PUWeight_down       = array('d',[0])
EleIDSF_up          = array('d',[0])
EleIDSF_down        = array('d',[0])
MuIDSF_up           = array('d',[0])
MuIDSF_down         = array('d',[0])
LHEScaleWeight_muR_up    = array('d',[0])
LHEScaleWeight_muR_down  = array('d',[0])
LHEScaleWeight_muF_up  = array('d',[0])
LHEScaleWeight_muF_down  = array('d',[0])
PSWeightISR_up    = array('d',[0])
PSWeightISR_down  = array('d',[0])
PSWeightFSR_up    = array('d',[0])
PSWeightFSR_down  = array('d',[0])

muTrig           = array('d',[0])
eleTrig          = array('d',[0])

E_Mass           = std.vector('double')()
E_Pt             = std.vector('double')()
E_Eta            = std.vector('double')()
E_Phi            = std.vector('double')()
E_Charge         = std.vector('double')()
E_RelIso         = std.vector('double')()
E_sip3d          = std.vector('double')()
E_ip3d           = std.vector('double')()
E_dxy            = std.vector('double')()
E_dz             = std.vector('double')()
hardE_Jet_PtRatio = array('d',[0])

M_Pt             = std.vector('double')()
M_Eta            = std.vector('double')()
M_Phi            = std.vector('double')()
M_Charge         = std.vector('double')()
M_RelIso         = std.vector('double')()
M_sip3d          = std.vector('double')()
M_ip3d           = std.vector('double')()
M_dxy            = std.vector('double')()
M_dz             = std.vector('double')()
hardMu_Jet_PtRatio = array('d',[0])

HT               = array('d',[0])
jet_Pt             = std.vector('double')()
jet_Eta            = std.vector('double')()
jet_Phi            = std.vector('double')()
jet_Mass           = std.vector('double')()
jet_CvsL           = std.vector('double')()
jet_CvsB           = std.vector('double')()
jet_DeepFlavCvsL   = std.vector('double')()
jet_DeepFlavCvsB   = std.vector('double')()
jet_qgl            = std.vector('double')()

jet_chEmEF         = std.vector('double')()
jet_neEmEF         = std.vector('double')()
jet_muplusneEmEF   = std.vector('double')()
jet_jetId          = std.vector('double')()
jet_puId           = std.vector('double')()
jet_muonIdx1       = std.vector('double')()
jet_muEF           = std.vector('double')()
jet_nMuons         = std.vector('double')()
jet_lepFiltCustom  = std.vector('double')()

jet_btagCMVA       = std.vector('double')()
jet_btagCSVV2      = std.vector('double')()
jet_btagDeepB      = std.vector('double')()
jet_btagDeepC      = std.vector('double')()
jet_btagDeepFlavB  = std.vector('double')()

jetMu_Pt           = array('d',[0])
jetMu_iso          = array('d',[0])
jetMu_dz           = array('d',[0])
jetMu_dxy          = array('d',[0])
jetMu_sip3d        = array('d',[0])
muJet_idx          = array('d',[0])
dR_jet_jetMu       = array('d',[0])
dR_lep_jet         = array('d',[0])
nMuJet             = array('d',[0])
dPhi_muJet_MET     = array('d',[0])
min_dPhi_jet_MET   = array('d',[0])
jetMuPt_by_jetPt   = array('d',[0])
jetMu_PtRel        = array('d',[0])
nTightMu           = array('d',[0])

leadCvsL_jetidx      = array('d',[0])
leadCvsB_jetidx      = array('d',[0])

semitChi2          = array('d',[0])
semitWCandMass     = array('d',[0])
semitWCandpT       = array('d',[0])
semittCandMass     = array('d',[0])
semittCandpT       = array('d',[0])
semitc1idx         = array('d',[0])
semitc2idx         = array('d',[0])

QCDveto             = array('d',[0])

nPV                 = array('d',[0])
nPVGood             = array('d',[0])
nSV                 = array('d',[0])

if isMC:
    jet_hadronFlv      = std.vector('double')()
    jet_isHardLep      = std.vector('double')()
    
jet_nJet           = array('d',[0])
met_Pt             = array('d',[0])
met_signif         = array('d',[0])
is_E               = array('d',[0])
is_M               = array('d',[0])
diLepVeto          = array('d',[0])
# is_H_mass_CR       = array('d',[0])
# is_W_mass_CR       = array('d',[0])

Z_Mass           = array('d',[0])
Z_Pt             = array('d',[0])
Z_Eta            = array('d',[0])
Z_Phi            = array('d',[0])

Z_Mass_best      = array('d',[0])
Z_Pt_best      = array('d',[0])
dR_mu_mu_best    = array('d',[0])
Z_Mass_max       = array('d',[0])
Z_Mass_min       = array('d',[0])
Z_Mass_withJet   = array('d',[0])

W_Mass           = array('d',[0])
W_Pt             = array('d',[0])
W_Eta            = array('d',[0])
W_Phi            = array('d',[0])

W_Mass_nuSol     = array('d',[0])
W_Pt_nuSol       = array('d',[0])
W_Eta_nuSol      = array('d',[0])
W_Phi_nuSol      = array('d',[0])

numOf_cJet       = array('d',[0])
numOf_bJet       = array('d',[0])
numOf_lJet       = array('d',[0])
pt_Of_cJet       = std.vector('double')()
pt_Of_bJet       = std.vector('double')()
pt_Of_lJet       = std.vector('double')()
eta_Of_cJet       = std.vector('double')()
eta_Of_lJet       = std.vector('double')()
phi_Of_cJet       = std.vector('double')()
phi_Of_lJet       = std.vector('double')()
pt_CvsLJet1       = array('d',[0])
pt_CvsLJet2       = array('d',[0])
eta_CvsLJet1      = array('d',[0])
eta_CvsLJet2      = array('d',[0])
phi_CvsLJet1      = array('d',[0])
phi_CvsLJet2      = array('d',[0])
CvsL_CvsLJet1     = array('d',[0])
CvsL_CvsLJet2     = array('d',[0])
CvsB_CvsLJet1     = array('d',[0])
CvsB_CvsLJet2     = array('d',[0])
if isMC:
    hadronFlavour_CsvLJet1  = array('d',[0])
    hadronFlavour_CsvLJet2  = array('d',[0])
    is_ZtoCCorBB       = array('d',[0])
HIGGS_Pt         = array('d',[0])
HIGGS_FL         = array('d',[0])
HIGGS_CvsL_Mass  = array('d',[0])
HIGGS_CvsL_Pt    = array('d',[0])
HIGGS_CvsL_Eta   = array('d',[0])
HIGGS_CvsL_Phi   = array('d',[0])
HIGGS_CvsB       = array('d',[0])
HIGGS_CvsB_CvsL  = array('d',[0])
HIGGS_CvsB_CvsL2 = array('d',[0])

cc_HIGGS_Pt         = array('d',[0])
cc_HIGGS_FL         = array('d',[0])
cc_HIGGS_CvsL       = array('d',[0])
cc_HIGGS_CvsB       = array('d',[0])
cc_HIGGS_CvsB_CvsL  = array('d',[0])
cc_HIGGS_CvsB_CvsL2 = array('d',[0])

co_HIGGS_Pt         = array('d',[0])
co_HIGGS_FL         = array('d',[0])
co_HIGGS_CvsL       = array('d',[0])
co_HIGGS_CvsB       = array('d',[0])
co_HIGGS_CvsB_CvsL  = array('d',[0])
co_HIGGS_CvsB_CvsL2 = array('d',[0])

oo_HIGGS_Pt         = array('d',[0])
oo_HIGGS_FL         = array('d',[0])
oo_HIGGS_CvsL       = array('d',[0])
oo_HIGGS_CvsB       = array('d',[0])
oo_HIGGS_CvsB_CvsL  = array('d',[0])
oo_HIGGS_CvsB_CvsL2 = array('d',[0])

M_Mass              = std.vector('double')()
met_Phi             = array('d',[0])
eta_Of_bJet         = std.vector('double')()
phi_Of_bJet         = std.vector('double')()
Flag_W_jet          = array('d',[0])
solver_chi2         = array('d',[0])

########################## MVA VARIABLES ##########################
SoftActivityJetHT       = array('d',[0])
SoftActivityJetNjets2   = array('d',[0])
SoftActivityJetNjets5   = array('d',[0])
SoftActivityJetNjets10  = array('d',[0])

DPhi_VH             = array('d',[0])
DPhi_METlep         = array('d',[0])
W_Tmass             = array('d',[0])
top_Mass            = array('d',[0])
DR_cc               = array('d',[0])
lepDR_cc            = array('d',[0])
M_lep_c             = array('d',[0])
centrality          = array('d',[0])
avgCvsLpT           = array('d',[0])
FWmoment_1         = array('d',[0])
FWmoment_2         = array('d',[0])
FWmoment_3         = array('d',[0])
FWmoment_4         = array('d',[0])

###################################################################
# ==============================================================================

# =============================== Declare output branches =====================
outputTree = TTree("Events","Events")

outputTree.Branch('run'              ,run           ,'run/D'        )
outputTree.Branch('lumiBlock'        ,lumiBlock     ,'lumiBlock/D'  )
outputTree.Branch('event'            ,event         ,'event/D'      )
outputTree.Branch('LHE_HT'           ,LHE_HT        ,'LHE_HT/D'     )
outputTree.Branch('LHE_Njets'        ,LHE_Njets     ,'LHE_Njets/D'     )
outputTree.Branch('LHE_Vpt'          ,LHE_Vpt       ,'LHE_Vpt/D'     )

outputTree.Branch('eventWeight'      ,eventWeight   ,'eventWeight/D'     )
outputTree.Branch('signWeight'       ,signWeight    ,'signWeight/D'     )
outputTree.Branch('genWeight'        ,genWeight     ,'genWeight/D'     )
outputTree.Branch('PUWeight'         ,PUWeight      ,'PUWeight/D'     )
outputTree.Branch('EleIDSF'          ,EleIDSF       ,'EleIDSF/D'     )
outputTree.Branch('MuIDSF'           ,MuIDSF        ,'MuIDSF/D'     )
outputTree.Branch('eventWeightnoPU'  ,eventWeightnoPU   ,'eventWeightnoPU/D'     )
outputTree.Branch('eventWeightUnsigned'      ,eventWeightUnsigned   ,'eventWeightUnsigned/D'     )

outputTree.Branch('PUWeight_up'         ,PUWeight_up      ,'PUWeight_up/D'     )
outputTree.Branch('PUWeight_down'       ,PUWeight_down    ,'PUWeight_down/D'     )
outputTree.Branch('EleIDSF_up'          ,EleIDSF_up       ,'EleIDSF_up/D'     )
outputTree.Branch('EleIDSF_down'          ,EleIDSF_down       ,'EleIDSF_down/D'     )
outputTree.Branch('MuIDSF_up'           ,MuIDSF_up        ,'MuIDSF_up/D'     )
outputTree.Branch('MuIDSF_down'           ,MuIDSF_down        ,'MuIDSF_down/D'     )
LHEScaleWeight_muF_up  = array('d',[0])
outputTree.Branch('LHEScaleWeight_muR_up'           ,LHEScaleWeight_muR_up        ,'LHEScaleWeight_muR_up/D'     )
outputTree.Branch('LHEScaleWeight_muR_down'         ,LHEScaleWeight_muR_down      ,'LHEScaleWeight_muR_down/D'     )
# outputTree.Branch('LHEScaleWeight_muF_up'           ,LHEScaleWeight_muF_up        ,'LHEScaleWeight_muF_up/D'     )
outputTree.Branch('LHEScaleWeight_muF_down'         ,LHEScaleWeight_muF_down      ,'LHEScaleWeight_muF_down/D'     )
outputTree.Branch('LHEScaleWeight_muF_up'         ,LHEScaleWeight_muF_up      ,'LHEScaleWeight_muF_up/D'     )

outputTree.Branch('PSWeightISR_up'           ,PSWeightISR_up        ,'PSWeightISR_up/D'     )
outputTree.Branch('PSWeightISR_down'         ,PSWeightISR_down      ,'PSWeightISR_down/D'     )
outputTree.Branch('PSWeightFSR_down'         ,PSWeightFSR_down      ,'PSWeightFSR_down/D'     )
outputTree.Branch('PSWeightFSR_up'           ,PSWeightFSR_up        ,'PSWeightFSR_up/D'     )

outputTree.Branch('muTrig'           ,muTrig        ,'muTrig/D'          )
outputTree.Branch('eleTrig'          ,eleTrig       ,'eleTrig/D'         )

outputTree.Branch('E_Mass'           ,E_Mass        )
outputTree.Branch('E_Pt'             ,E_Pt          )
outputTree.Branch('E_Eta'            ,E_Eta         )
outputTree.Branch('E_Phi'            ,E_Phi         )
outputTree.Branch('E_Charge'         ,E_Charge      )
outputTree.Branch('E_RelIso'         ,E_RelIso      )
outputTree.Branch('E_dz'             ,E_dz      )
outputTree.Branch('E_dxy'            ,E_dxy      )
outputTree.Branch('E_sip3d'          ,E_sip3d      )
outputTree.Branch('E_ip3d'           ,E_ip3d      )
outputTree.Branch('hardE_Jet_PtRatio'         ,hardE_Jet_PtRatio      ,'hardE_Jet_PtRatio/D')

outputTree.Branch('M_Mass'           ,M_Mass        )
outputTree.Branch('M_Pt'             ,M_Pt          )
outputTree.Branch('M_Eta'            ,M_Eta         )
outputTree.Branch('M_Phi'            ,M_Phi         )
outputTree.Branch('M_Charge'         ,M_Charge      )
outputTree.Branch('M_RelIso'         ,M_RelIso      )
outputTree.Branch('M_dz'             ,M_dz      )
outputTree.Branch('M_dxy'            ,M_dxy      )
outputTree.Branch('M_sip3d'          ,M_sip3d      )
outputTree.Branch('M_ip3d'           ,M_ip3d      )
outputTree.Branch('hardMu_Jet_PtRatio'         ,hardMu_Jet_PtRatio      ,'hardMu_Jet_PtRatio/D')

outputTree.Branch('HT'               ,HT            ,'HT/D'     )
outputTree.Branch('jet_Pt'           ,jet_Pt        )
outputTree.Branch('jet_Eta'          ,jet_Eta       )
outputTree.Branch('jet_Phi'          ,jet_Phi       )
outputTree.Branch('jet_Mass'         ,jet_Mass      )
outputTree.Branch('jet_nJet'         ,jet_nJet      ,'jet_nJet/D')
outputTree.Branch('jet_CvsL'         ,jet_CvsL      )
outputTree.Branch('jet_CvsB'         ,jet_CvsB      )
outputTree.Branch('jet_DeepFlavCvsL' ,jet_DeepFlavCvsL      )
outputTree.Branch('jet_DeepFlavCvsB' ,jet_DeepFlavCvsB      )
outputTree.Branch('jet_qgl'          ,jet_qgl      )

outputTree.Branch('jet_chEmEF'          ,jet_chEmEF      )
outputTree.Branch('jet_neEmEF'          ,jet_neEmEF      )
outputTree.Branch('jet_muplusneEmEF'    ,jet_muplusneEmEF)

outputTree.Branch('jet_jetId'           ,jet_jetId      )
outputTree.Branch('jet_puId'            ,jet_puId      )
outputTree.Branch('jet_muonIdx1'        ,jet_muonIdx1      )
outputTree.Branch('jet_muEF'            ,jet_muEF      )
outputTree.Branch('jet_nMuons'          ,jet_nMuons      )
outputTree.Branch('jet_lepFiltCustom'   ,jet_lepFiltCustom      )

outputTree.Branch('jet_btagCMVA'    ,jet_btagCMVA      )
outputTree.Branch('jet_btagDeepB'   ,jet_btagDeepB      )
outputTree.Branch('jet_btagDeepC'   ,jet_btagDeepC      )
outputTree.Branch('jet_btagDeepFlavB'   ,jet_btagDeepFlavB      )
outputTree.Branch('jet_btagCSVV2'   ,jet_btagCSVV2     )

outputTree.Branch('jetMu_Pt'         ,jetMu_Pt      ,'jetMu_Pt/D')
outputTree.Branch('jetMu_PtRel'      ,jetMu_PtRel   ,'jetMu_PtRel/D')
outputTree.Branch('jetMu_iso'        ,jetMu_iso     ,'jetMu_iso/D')
outputTree.Branch('jetMu_dz'         ,jetMu_dz      ,'jetMu_dz/D')
outputTree.Branch('jetMu_dxy'        ,jetMu_dxy     ,'jetMu_dxy/D')
outputTree.Branch('jetMu_sip3d'      ,jetMu_sip3d   ,'jetMu_sip3d/D')
outputTree.Branch('muJet_idx'        ,muJet_idx     ,'muJet_idx/D')
outputTree.Branch('nMuJet'           ,nMuJet        ,'nMuJet/D')
outputTree.Branch('dR_jet_jetMu'     ,dR_jet_jetMu  ,'dR_jet_jetMu/D')
outputTree.Branch('dR_lep_jet'       ,dR_lep_jet    ,'dR_lep_jet/D')
outputTree.Branch('dPhi_muJet_MET'   ,dPhi_muJet_MET,'dPhi_muJet_MET/D')
outputTree.Branch('min_dPhi_jet_MET' ,min_dPhi_jet_MET,'min_dPhi_jet_MET/D')
outputTree.Branch('jetMuPt_by_jetPt' ,jetMuPt_by_jetPt,'jetMuPt_by_jetPt/D')
outputTree.Branch('nTightMu'         ,nTightMu      ,'nTightMu/D')

outputTree.Branch('leadCvsB_jetidx'        ,leadCvsB_jetidx     ,'leadCvsB_jetidx/D')
outputTree.Branch('leadCvsL_jetidx'        ,leadCvsL_jetidx     ,'leadCvsL_jetidx/D')

outputTree.Branch('semitChi2'        ,semitChi2          ,'semitChi2/D')
outputTree.Branch('semitWCandMass'   ,semitWCandMass     ,'semitWCandMass/D')
outputTree.Branch('semitWCandpT'     ,semitWCandpT       ,'semitWCandpT/D')
outputTree.Branch('semittCandMass'   ,semittCandMass     ,'semittCandMass/D')
outputTree.Branch('semittCandpT'     ,semittCandpT       ,'semittCandpT/D')
outputTree.Branch('semitc1idx'       ,semitc1idx         ,'semitc1idx/D')
outputTree.Branch('semitc2idx'       ,semitc2idx         ,'semitc2idx/D')

outputTree.Branch('QCDveto'        ,QCDveto     ,'QCDveto/D')

outputTree.Branch('nPV'     ,nPV        ,'nPV/D')
outputTree.Branch('nPVGood' ,nPVGood    ,'nPVGood/D')
outputTree.Branch('nSV'     ,nSV        ,'nSV/D')

if isMC:
    outputTree.Branch('jet_hadronFlv'    ,jet_hadronFlv )
    outputTree.Branch('jet_isHardLep'    ,jet_isHardLep )
    
outputTree.Branch('met_Pt'           ,met_Pt          ,'met_Pt/D'     )
outputTree.Branch('met_Phi'          ,met_Phi         ,'met_Phi/D')
outputTree.Branch('met_signif'       ,met_signif      ,'met_signif/D')

outputTree.Branch('Z_Mass'           ,Z_Mass          ,'Z_Mass/D'     )
outputTree.Branch('Z_Pt'             ,Z_Pt            ,'Z_Pt/D'     )
outputTree.Branch('Z_Eta'            ,Z_Eta           ,'Z_Eta/D'     )
outputTree.Branch('Z_Phi'            ,Z_Phi           ,'Z_Phi/D'     )

outputTree.Branch('Z_Mass_best'      ,Z_Mass_best     ,'Z_Mass_best/D'     )
outputTree.Branch('Z_Pt_best'        ,Z_Pt_best       ,'Z_Pt_best/D'     )
outputTree.Branch('dR_mu_mu_best'    ,dR_mu_mu_best   ,'dR_mu_mu_best/D'     )
outputTree.Branch('Z_Mass_max'       ,Z_Mass_max      ,'Z_Mass_max/D'     )
outputTree.Branch('Z_Mass_min'       ,Z_Mass_min      ,'Z_Mass_min/D'     )
outputTree.Branch('Z_Mass_withJet'   ,Z_Mass_withJet  ,'Z_Mass_withJet/D'     )


outputTree.Branch('W_Mass'           ,W_Mass          ,'W_Mass/D'     )
outputTree.Branch('W_Pt'             ,W_Pt            ,'W_Pt/D'     )
outputTree.Branch('W_Eta'            ,W_Eta           ,'W_Eta/D'     )
outputTree.Branch('W_Phi'            ,W_Phi           ,'W_Phi/D'     )

outputTree.Branch('W_Mass_nuSol'     ,W_Mass_nuSol    ,'W_Mass_nuSol/D'     )
outputTree.Branch('W_Pt_nuSol'       ,W_Pt_nuSol      ,'W_Pt_nuSol/D'     )
outputTree.Branch('W_Eta_nuSol'      ,W_Eta_nuSol     ,'W_Eta_nuSol/D'     )
outputTree.Branch('W_Phi_nuSol'      ,W_Phi_nuSol     ,'W_Phi_nuSol/D'     )

outputTree.Branch('is_E'     ,is_E    ,'is_E/D'     )
outputTree.Branch('is_M'     ,is_M    ,'is_M/D'     )
outputTree.Branch('diLepVeto'     ,diLepVeto    ,'diLepVeto/D'     )

# outputTree.Branch('is_H_mass_CR'     ,is_H_mass_CR    ,'is_H_mass_CR/D'     )
# outputTree.Branch('is_W_mass_CR'     ,is_W_mass_CR    ,'is_W_mass_CR/D'     )

outputTree.Branch('Flag_W_jet'       ,Flag_W_jet      ,'Flag_W_jet/D'     )
outputTree.Branch('solver_chi2'      ,solver_chi2     ,'solver_chi2/D'     )
outputTree.Branch('numOf_cJet'       ,numOf_cJet      ,'numOf_cJet/D'     )
outputTree.Branch('numOf_bJet'       ,numOf_bJet      ,'numOf_bJet/D'     )
outputTree.Branch('numOf_lJet'       ,numOf_lJet      ,'numOf_lJet/D'     )

outputTree.Branch('pt_Of_cJet'       ,pt_Of_cJet    )
outputTree.Branch('pt_Of_bJet'       ,pt_Of_bJet    )
outputTree.Branch('pt_Of_lJet'       ,pt_Of_lJet    )

outputTree.Branch('eta_Of_cJet'       ,eta_Of_cJet  )
outputTree.Branch('eta_Of_bJet'       ,eta_Of_bJet  )
outputTree.Branch('eta_Of_lJet'       ,eta_Of_lJet  )

outputTree.Branch('phi_Of_cJet'       ,phi_Of_cJet  )
outputTree.Branch('phi_Of_bJet'       ,phi_Of_bJet  )
outputTree.Branch('phi_Of_lJet'       ,phi_Of_lJet  )

outputTree.Branch('pt_CvsLJet1'       ,pt_CvsLJet1      ,'pt_CvsLJet1/D'     )
outputTree.Branch('pt_CvsLJet2'       ,pt_CvsLJet2      ,'pt_CvsLJet2/D'     )

outputTree.Branch('eta_CvsLJet1'       ,eta_CvsLJet1      ,'eta_CvsLJet1/D'     )
outputTree.Branch('eta_CvsLJet2'       ,eta_CvsLJet2      ,'eta_CvsLJet2/D'     )

outputTree.Branch('phi_CvsLJet1'       ,phi_CvsLJet1      ,'phi_CvsLJet1/D'     )
outputTree.Branch('phi_CvsLJet2'       ,phi_CvsLJet2      ,'phi_CvsLJet2/D'     )

outputTree.Branch('CvsL_CvsLJet1'       ,CvsL_CvsLJet1      ,'CvsL_CvsLJet1/D'     )
outputTree.Branch('CvsL_CvsLJet2'       ,CvsL_CvsLJet2      ,'CvsL_CvsLJet2/D'     )

outputTree.Branch('CvsB_CvsLJet1'       ,CvsB_CvsLJet1      ,'CvsB_CvsLJet1/D'     )
outputTree.Branch('CvsB_CvsLJet2'       ,CvsB_CvsLJet2      ,'CvsB_CvsLJet2/D'     )
if isMC:
    outputTree.Branch('hadronFlavour_CsvLJet1' ,hadronFlavour_CsvLJet1 ,'hadronFlavour_CsvLJet1/D'     )
    outputTree.Branch('hadronFlavour_CsvLJet2' ,hadronFlavour_CsvLJet2 ,'hadronFlavour_CsvLJet2/D'     )
    outputTree.Branch('is_ZtoCCorBB'     ,is_ZtoCCorBB    ,'is_ZtoCCorBB/D'     )
outputTree.Branch('HIGGS_Pt'         ,HIGGS_Pt        ,'HIGGS_Pt/D'       )
outputTree.Branch('HIGGS_CvsL_Mass'  ,HIGGS_CvsL_Mass ,'HIGGS_CvsL_Mass/D')
outputTree.Branch('HIGGS_CvsL_Pt'    ,HIGGS_CvsL_Pt   ,'HIGGS_CvsL_Pt/D')
outputTree.Branch('HIGGS_CvsL_Eta'   ,HIGGS_CvsL_Eta  ,'HIGGS_CvsL_Eta/D')
outputTree.Branch('HIGGS_CvsL_Phi'   ,HIGGS_CvsL_Phi  ,'HIGGS_CvsL_Phi/D')
outputTree.Branch('HIGGS_CvsB'       ,HIGGS_CvsB      ,'HIGGS_CvsB/D'     )
outputTree.Branch('HIGGS_CvsB_CvsL'  ,HIGGS_CvsB_CvsL ,'HIGGS_CvsB_CvsL/D')
outputTree.Branch('HIGGS_CvsB_CvsL2' ,HIGGS_CvsB_CvsL2,'HIGGS_CvsB_CvsL2/D')

outputTree.Branch('cc_HIGGS_Pt'         ,cc_HIGGS_Pt        ,'cc_HIGGS_Pt/D'       )
outputTree.Branch('cc_HIGGS_CvsL'       ,cc_HIGGS_CvsL      ,'cc_HIGGS_CvsL/D'     )
outputTree.Branch('cc_HIGGS_CvsB'       ,cc_HIGGS_CvsB      ,'cc_HIGGS_CvsB/D'     )
outputTree.Branch('cc_HIGGS_CvsB_CvsL'  ,cc_HIGGS_CvsB_CvsL ,'cc_HIGGS_CvsB_CvsL/D')
outputTree.Branch('cc_HIGGS_CvsB_CvsL2' ,cc_HIGGS_CvsB_CvsL2,'cc_HIGGS_CvsB_CvsL2/D')

outputTree.Branch('co_HIGGS_Pt'         ,co_HIGGS_Pt        ,'co_HIGGS_Pt/D'       )
outputTree.Branch('co_HIGGS_CvsL'       ,co_HIGGS_CvsL      ,'co_HIGGS_CvsL/D'     )
outputTree.Branch('co_HIGGS_CvsB'       ,co_HIGGS_CvsB      ,'co_HIGGS_CvsB/D'     )
outputTree.Branch('co_HIGGS_CvsB_CvsL'  ,co_HIGGS_CvsB_CvsL ,'co_HIGGS_CvsB_CvsL/D')
outputTree.Branch('co_HIGGS_CvsB_CvsL2' ,co_HIGGS_CvsB_CvsL2,'co_HIGGS_CvsB_CvsL2/D')

outputTree.Branch('oo_HIGGS_Pt'         ,oo_HIGGS_Pt        ,'oo_HIGGS_Pt/D'       )
outputTree.Branch('oo_HIGGS_CvsL'       ,oo_HIGGS_CvsL      ,'oo_HIGGS_CvsL/D'     )
outputTree.Branch('oo_HIGGS_CvsB'       ,oo_HIGGS_CvsB      ,'oo_HIGGS_CvsB/D'     )
outputTree.Branch('oo_HIGGS_CvsB_CvsL'  ,oo_HIGGS_CvsB_CvsL ,'oo_HIGGS_CvsB_CvsL/D')
outputTree.Branch('oo_HIGGS_CvsB_CvsL2' ,oo_HIGGS_CvsB_CvsL2,'oo_HIGGS_CvsB_CvsL2/D')

########################## MVA VARIABLES ##########################
outputTree.Branch('SoftActivityJetHT'                 ,SoftActivityJetHT                  ,'SoftActivityJetHT/D'            )
outputTree.Branch('SoftActivityJetNjets2'             ,SoftActivityJetNjets2              ,'SoftActivityJetNjets2/D'        )
outputTree.Branch('SoftActivityJetNjets5'             ,SoftActivityJetNjets5              ,'SoftActivityJetNjets5/D'        )
outputTree.Branch('SoftActivityJetNjets10'            ,SoftActivityJetNjets10             ,'SoftActivityJetNjets10/D'       )
outputTree.Branch('DPhi_VH'                     ,DPhi_VH          ,'DPhi_VH/D'          )
outputTree.Branch('DPhi_METlep'                 ,DPhi_METlep      ,'DPhi_METlep/D'      )
outputTree.Branch('W_Tmass'                     ,W_Tmass          ,'W_Tmass/D'          )
outputTree.Branch('top_Mass'                    ,top_Mass         ,'top_Mass/D'     )
outputTree.Branch('DR_cc'                       ,DR_cc            ,'DR_cc/D'         )
outputTree.Branch('lepDR_cc'                    ,lepDR_cc         ,'lepDR_cc/D'   )
outputTree.Branch('M_lep_c'                     ,M_lep_c          ,'M_lep_c/D'       )
outputTree.Branch('centrality'                  ,centrality       ,'centrality/D'       )
outputTree.Branch('avgCvsLpT'                   ,avgCvsLpT        ,'avgCvsLpT/D'        )
# outputTree.Branch('FWmoment_0'                 ,FWmoment_0      ,'FWmoment_0/D'      )
outputTree.Branch('FWmoment_1'                 ,FWmoment_1      ,'FWmoment_1/D'      )
outputTree.Branch('FWmoment_2'                 ,FWmoment_2      ,'FWmoment_2/D'      )
outputTree.Branch('FWmoment_3'                 ,FWmoment_3      ,'FWmoment_3/D'      )
outputTree.Branch('FWmoment_4'                 ,FWmoment_4      ,'FWmoment_4/D'      )
###################################################################
# ==============================================================================

# ==================== Hacks to run with NanoAOD (1 of 2) ======================
validBranches = [str(br.GetName()) for br in inputTree.GetListOfBranches()]
# for i in validBranches:
#     if "MET" in i or "met" in i: print i
nEntries = inputTree.GetEntries()
count = 0
notFound=[]
# ==============================================================================

# Begin event loop
for entry in inputTree:
    if maxEvents > 0 and count >= maxEvents: break

    if count%10000 ==0:
        print "Number of events processed: %d of %d"%(count,nEntries)
    count+=1
    h_postp.Fill(1.)

    # ================== Hacks to run with NanoAOD (1 of 2) ====================
    def getEntry(string,type):
        if string == "MET_Pt": string = "MET_pt"
        if string == "MET_Phi": string = "MET_phi"
        if string in validBranches:
            exec("x = entry."+string)
            return x
        else:
            if not string in notFound:
                print "WARNING ::: Branch %s was not found in the tree. Replacing with dummy value."%string
                notFound.append(string)
            if string == "Jet_lepFilter": return [1 for i in range(100)]
            if type == 'fl':
                return -1
            else:
                return [0 for i in range(100)]
    # ==========================================================================

    # ====================== Initialize variables/vectors ======================
    TriggerPass = False
    elec                = []
    muon                = []

    el_List             = []
    mu_List             = []
    jetList             = []
    jet_FL_List         = []
    jet_Pt_List         = []
    jet_CvsL_List       = []
    jet_CvsB_List       = []
    jet_CvsB_CvsL_List  = []
    jet_CvsB_CvsL_List2 = []

    e_Pt_List                = []
    e_Eta_List               = []
    e_Phi_List               = []
    e_Charge_List            = []
    e_Mass_List              = []
    hardE_Jet_PtRatio[0]     = -1000

    m_Pt_List                = []
    m_Eta_List               = []
    m_Phi_List               = []
    m_Charge_List            = []
    m_Mass_List              = []
    hardMu_Jet_PtRatio[0]    = -1000

    j_Pt_List                = []
    j_Eta_List               = []
    j_Phi_List               = []
    j_Mass_List              = []
    j_CvsL_List              = []
    j_CvsB_List              = []
    j_qgl_List               = []
    j_MuonIdx1_List          = []
    j_MuonIdx2_List          = []

    if isMC:
        j_hadronFlv_List         = []
        is_ZtoCCorBB[0]     = -100
    isElec              = True
    isMuon              = True
#     is_H_mass_CR[0]     = 0
#     is_W_mass_CR[0]     = 0

    is_E[0]             = False
    is_M[0]             = False
    diLepVeto[0]        = False

    run[0]              = -1000
    lumiBlock[0]        = -1000
    event[0]            = -1000
    LHE_HT[0]           = -1000
    LHE_Njets[0]        = -1000
    LHE_Vpt[0]          = -1000

    muTrig[0]           = -1
    eleTrig[0]          = -1

    HT[0]               = -1000

    Z_Mass[0]           = -1000
    Z_Pt[0]             = -1000
    Z_Eta[0]            = -1000
    Z_Phi[0]            = -1000

    Z_Mass_best[0]      = -1000
    Z_Pt_best[0]      = -1000
    dR_mu_mu_best[0]    = -1000
    Z_Mass_max[0]       = -1000
    Z_Mass_min[0]       = 1000
    Z_Mass_withJet[0]   = -1000

    W_Mass[0]           = -1000
    W_Pt[0]             = -1000
    W_Eta[0]            = -1000
    W_Phi[0]            = -1000

    W_Mass_nuSol[0]     = -1000
    W_Pt_nuSol[0]       = -1000
    W_Eta_nuSol[0]      = -1000
    W_Phi_nuSol[0]      = -1000

    HIGGS_CvsL_Mass[0]  = -1000
    HIGGS_CvsL_Pt[0]    = -1000
    HIGGS_CvsL_Eta[0]   = -1000
    HIGGS_CvsL_Phi[0]   = -1000

    pt_Of_cJet.clear()
    pt_Of_bJet.clear()
    pt_Of_lJet.clear()

    eta_Of_cJet.clear()
    eta_Of_bJet.clear()
    eta_Of_lJet.clear()

    phi_Of_cJet.clear()
    phi_Of_bJet.clear()
    phi_Of_lJet.clear()

    jetMu_Pt[0]            = -1.
    jetMu_PtRel[0]         = -1000.
    jetMu_iso[0]           = -1.
    jetMu_dz[0]            = -1000.
    jetMu_dxy[0]           = -1000.
    jetMu_sip3d[0]         = -1000.
    
    nTightMu[0]            = -1.
    muJet_idx[0]           = -1.
    nMuJet[0]              = -1.
    dR_lep_jet[0]          = -1000
    dR_jet_jetMu[0]        = -1000
    dPhi_muJet_MET[0]      = -1
    min_dPhi_jet_MET[0]    = -1
    jetMuPt_by_jetPt[0]    = -1
    leadCvsB_jetidx[0]        = -1
    leadCvsL_jetidx[0]        = -1
    QCDveto[0]              = -1

    semitChi2[0]            = -1
    semitWCandMass[0]       = -1
    semitWCandpT[0]         = -1
    semittCandMass[0]       = -1
    semittCandpT[0]         = -1
    semitc1idx[0]           = -1
    semitc2idx[0]           = -1

    nPV[0]                 = -1
    nPVGood[0]             = -1
    nSV[0]                 = -1

    jet_nJet[0]            = -1
    Flag_W_jet[0]          = -1000
    solver_chi2[0]         = -1000
    numOf_cJet[0]          = -1
    numOf_bJet[0]          = -1
    numOf_lJet[0]          = -1

    cc_HIGGS_Pt[0]         = -1
    cc_HIGGS_CvsL[0]       = -1
    cc_HIGGS_CvsB[0]       = -1
    cc_HIGGS_CvsB_CvsL[0]  = -1
    cc_HIGGS_CvsB_CvsL2[0] = -1

    co_HIGGS_Pt[0]         = -1
    co_HIGGS_CvsL[0]       = -1
    co_HIGGS_CvsB[0]       = -1
    co_HIGGS_CvsB_CvsL[0]  = -1
    co_HIGGS_CvsB_CvsL2[0] = -1

    oo_HIGGS_Pt[0]         = -1
    oo_HIGGS_CvsL[0]       = -1
    oo_HIGGS_CvsB[0]       = -1
    oo_HIGGS_CvsB_CvsL[0]  = -1
    oo_HIGGS_CvsB_CvsL2[0] = -1

    pt_CvsLJet1[0]       = -1
    pt_CvsLJet2[0]       = -1
    eta_CvsLJet1[0]      = -1000
    eta_CvsLJet2[0]      = -1000
    phi_CvsLJet1[0]      = -1000
    phi_CvsLJet2[0]      = -1000
    CvsL_CvsLJet1[0]     = -1
    CvsL_CvsLJet2[0]     = -1
    CvsB_CvsLJet1[0]     = -1
    CvsB_CvsLJet2[0]     = -1

    SoftActivityJetHT[0]       = -1000.0
    SoftActivityJetNjets2[0]   = -1000
    SoftActivityJetNjets5[0]   = -1000
    SoftActivityJetNjets10[0]  = -1000
    DPhi_VH[0]                 = -1000.0
    DPhi_METlep[0]             = -1000.0
    W_Tmass[0]                 = -1000.0
    top_Mass[0]                = -1000.0
    DR_cc[0]                   = -1000.0
    lepDR_cc[0]                = -1000.0
    M_lep_c[0]                 = -1000
    centrality[0]              = -1000.0
    avgCvsLpT[0]               = -1000.0

    if isMC:
        hadronFlavour_CsvLJet1[0] = -100
        hadronFlavour_CsvLJet2[0] = -100
    E_Mass.clear()
    E_Pt.clear()
    E_Eta.clear()
    E_Phi.clear()
    E_Charge.clear()
    E_RelIso.clear()
    E_dz.clear()
    E_dxy.clear()
    E_sip3d.clear()
    E_ip3d.clear()

    M_Mass.clear()
    M_Pt.clear()
    M_Eta.clear()
    M_Phi.clear()
    M_Charge.clear()
    M_RelIso.clear()
    M_dz.clear()
    M_dxy.clear()
    M_sip3d.clear()
    M_ip3d.clear()

    jet_Pt.clear()
    jet_Eta.clear()
    jet_Phi.clear()
    jet_Mass.clear()
    jet_CvsL.clear()
    jet_CvsB.clear()
    jet_DeepFlavCvsL.clear()
    jet_DeepFlavCvsB.clear()
    jet_qgl.clear()

    jet_chEmEF.clear()
    jet_neEmEF.clear()
    jet_muplusneEmEF.clear()
    jet_jetId.clear()
    jet_puId.clear()
    jet_muonIdx1.clear()
    jet_muEF.clear()
    jet_nMuons.clear()
    jet_lepFiltCustom.clear()

    jet_btagCMVA.clear()
    jet_btagDeepB.clear()
    jet_btagDeepC.clear()
    jet_btagCSVV2.clear()
    jet_btagDeepFlavB.clear()

    if isMC:
        jet_hadronFlv.clear()
        jet_isHardLep.clear()

    met_Pt[0]             = -1
    met_Phi[0]            = -1000
    met_signif[0]         = -1000
    # ==========================================================================
    # print list(entry.Jet_Pt),list(entry.Jet_pt_jesTotalUp), list(entry.Jet_pt_jesTotalDown), list(entry.Jet_pt_jerUp), list(entry.Jet_pt_jerDown)
    if JECName=="nom":
        jetPt = entry.Jet_Pt
        jetMass = entry.Jet_mass
        metPt = entry.MET_Pt
        metPhi = entry.MET_Phi
    else:
        exec("jetPt = entry.Jet_pt_"+JECName)
        exec("jetMass = entry.Jet_mass_"+JECName)
        exec("metPt = entry.MET_T1Smear_pt_"+JECName)
        exec("metPhi = entry.MET_T1Smear_phi_"+JECName)

    # =========================== Select Leptons ===============================
    if era == 2016:
        ElectronID = entry.Electron_mvaSpring16GP_WP80
        elePtCut = 30
    elif era == 2017 or era == 2018:
        if "Electron_mvaFall17V2Iso_WP80" in validBranches:
            ElectronID = entry.Electron_mvaFall17V2Iso_WP80
        else:
            ElectronID = entry.Electron_mvaFall17Iso_WP80
        elePtCut = 34
    
    if "Muon_pt_corrected" in validBranches: Muon_pt = entry.Muon_pt_corrected
    elif "Muon_corrected_pt" in validBranches: Muon_pt = entry.Muon_corrected_pt
    else: Muon_pt = entry.Muon_pt

    if debug == True:
        print "Preselection 1 : Single Lepton"
        print "                 electron selection : pt > 30 and eta<2.5"
        print "                 electron selection : Electron_mvaSpring16GP_WP80 > 0 "                # cutBased >= 3 (Medium)"
        # print "                 electron selection : Electron_pfRelIso03_all <= 0.15"
        print "                 muon selection : pt > 30 and eta<2.4"
        print "                 muon selection : Muon_tightId > 0"
        print "                 muon selection : Muon_pfRelIso04_all <= 0.15"

    for i in range(0, len(entry.Electron_pt)):
        if entry.Electron_pt[i]<elePtCut or abs(entry.Electron_eta[i])>2.5: continue
        if abs(entry.Electron_eta[i]) > 1.442 and abs(entry.Electron_eta[i]) < 1.556: continue
        if ElectronID[i]<=0: continue
        # if entry.Electron_cutBased[i]<3: continue
        # if entry.Electron_pfRelIso03_all[i]>0.15: continue
        e_Pt_List.append(entry.Electron_pt[i])
        e_Eta_List.append(entry.Electron_eta[i])
        e_Phi_List.append(entry.Electron_phi[i])
        e_Charge_List.append(entry.Electron_charge[i])
        e_Mass_List.append(entry.Electron_mass[i])

        #Additions to check quality of hard ele
        E_RelIso.push_back(entry.Electron_pfRelIso03_all[i])
        E_dz.push_back(entry.Electron_dz[i])
        E_dxy.push_back(entry.Electron_dxy[i])
        E_sip3d.push_back(entry.Electron_sip3d[i])
        E_ip3d.push_back(entry.Electron_ip3d[i])
        hardE_jetidx = entry.Electron_jetIdx[i]
        if hardE_jetidx >= 0:
            hardE_Jet_PtRatio[0] = entry.Electron_pt[i]/jetPt[hardE_jetidx]

    for i in range(0, len(Muon_pt)):
        if Muon_pt[i]<30 or abs(entry.Muon_eta[i])>2.4: continue
        if entry.Muon_tightId[i]<=0: continue
        if entry.Muon_pfRelIso04_all[i]>0.15: continue
        m_Pt_List.append(Muon_pt[i])
        m_Eta_List.append(entry.Muon_eta[i])
        m_Phi_List.append(entry.Muon_phi[i])
        m_Charge_List.append(entry.Muon_charge[i])
        m_Mass_List.append(entry.Muon_mass[i])

        #Additions to check quality of hard muon
        M_RelIso.push_back(entry.Muon_pfRelIso04_all[i])
        M_dz.push_back(entry.Muon_dz[i])
        M_dxy.push_back(entry.Muon_dxy[i])
        M_sip3d.push_back(entry.Muon_sip3d[i])
        M_ip3d.push_back(entry.Muon_ip3d[i])
        hardMu_jetidx = entry.Muon_jetIdx[i]
        if hardMu_jetidx >= 0:
            hardMu_Jet_PtRatio[0] = Muon_pt[i]/jetPt[hardMu_jetidx]
    # ==========================================================================

    # ======================== Exactly 1 Lepton cut ============================
    if len(e_Pt_List) + len(m_Pt_List) != 1: continue

    if len(e_Pt_List) == 1:
        isMuon = False
        el_List = sorted(zip(e_Pt_List,e_Charge_List), key = lambda pair : pair[0], reverse=True)[0:2]
        hardlep = TLorentzVector()
        hardlep.SetPtEtaPhiM(e_Pt_List[0], e_Eta_List[0], e_Phi_List[0], e_Mass_List[0])

    if len(m_Pt_List) == 1:
        isElec = False
        mu_List = sorted(zip(m_Pt_List,m_Charge_List), key = lambda pair : pair[0], reverse=True)[0:2]
        hardlep = TLorentzVector()
        hardlep.SetPtEtaPhiM(m_Pt_List[0], m_Eta_List[0], m_Phi_List[0], m_Mass_List[0])
    # ==========================================================================

    # ================ Second lepton matching ttbar dileptonic =================
    nEleDilep = 0
    nMuDilep = 0

    for i in range(0, len(entry.Electron_pt)):
        if entry.Electron_pt[i]<15 or abs(entry.Electron_eta[i])>2.5: continue
        if abs(entry.Electron_eta[i]) > 1.442 and abs(entry.Electron_eta[i]) < 1.556: continue
        if ElectronID[i]<=0: continue
        nEleDilep += 1

    for i in range(0, len(Muon_pt)):
        if Muon_pt[i]<12 or abs(entry.Muon_eta[i])>2.4: continue
        if entry.Muon_tightId[i]<=0: continue
        if entry.Muon_pfRelIso04_all[i]>0.15: continue
        nMuDilep += 1

    if (nEleDilep == 2 and nMuDilep == 0) or (nEleDilep == 0 and nMuDilep == 2) or (nEleDilep == 1 and nMuDilep == 1):
        diLepVeto[0] = 1
    # ==========================================================================

    # ============================== Get MET ===================================
    met_Pt[0]              = metPt
    met_Phi[0]             = metPhi
#    met_signif[0]          = entry.MET_significance

    mW = 80.38
    mH = 125 + mW
    MET = TLorentzVector()
    MET.SetPtEtaPhiM(metPt, 0., metPhi, 0.)
    sigma2 = np.array([((MET.Px()*.1)**2,0),(0,(MET.Py()*.1)**2)])
    # ==========================================================================

    # ============================ Jet selection ===============================
    if debug == True:
        print "                 Jet selection : jet_pt > 20 and jet_eta < 2.4/2.5"
        print "                 Jet selection : Jet_jetId >= 3"                 # Tight in 2016
        print "                 Jet selection : Jet_lepFilter = True"           # or Jet Mu EF < 0.8
        print "                 Jet selection : Jet_puId >= 7"

    # # ------------------------ Custom Jet_lepFilter ----------------------------
    # # (different from that in the VHcc postprocessor)
    # jetFilterFlags = [True]*len(jetPt)
    # for i in range(0, len(entry.Electron_pt)):
    #     if entry.Electron_cutBased[i]<3: continue
    #     if entry.Electron_pt[i]<20: continue
    #     # if entry.Electron_pfRelIso03_all[i]>0.15: continue
    #
    #     jetInd = entry.Electron_jetIdx[i]
    #     if jetInd >= 0:
    #         jetFilterFlags[jetInd] = False
    #
    # for i in range(0, len(Muon_pt)):
    #     if entry.Muon_tightId[i]<=0: continue
    #     if entry.Muon_dxy[i]>0.05: continue
    #     if entry.Muon_dz[i]>0.2: continue
    #     if Muon_pt[i]<15: continue
    #     if entry.Muon_pfRelIso04_all[i]>0.5: continue
    #
    #     jetInd = entry.Muon_jetIdx[i]
    #     if jetInd >= 0:
    #         jetFilterFlags[jetInd] = False
    # # --------------------------------------------------------------------------
    
    HT_temp = 0
    totalJetEnergy = 0
    totalJetCvsL = 0
    totalJetCvsLpt = 0
    min_dPhi_jet_MET[0] = 1000
    if era == 2016: jetetamax = 2.4
    elif era == 2017 or era == 2018: jetetamax = 2.5
    for i in range(0, len(jetPt)):
        if jetPt[i]<20 or abs(entry.Jet_eta[i])>jetetamax: continue
        if entry.Jet_jetId[i] < 5: continue
        if entry.Jet_puId[i] < 7 and jetPt[i] < 50: continue
#        if jetFilterFlags[i] == False: continue

        Jet_muEF = 1 - (entry.Jet_chEmEF[i] + entry.Jet_chHEF[i] + entry.Jet_neEmEF[i] + entry.Jet_neHEF[i])
        Jet_muplusneEmEF = 1 - (entry.Jet_chEmEF[i] + entry.Jet_chHEF[i] + entry.Jet_neHEF[i])
        # if Jet_muEF > 0.8: continue

        jet =  TLorentzVector()
        jet.SetPtEtaPhiM(jetPt[i],entry.Jet_eta[i],entry.Jet_phi[i],jetMass[i])
        
        if jet.DeltaR(hardlep) < 0.4: continue
        
        jetList.append(jet)

        MET = TLorentzVector()
        MET.SetPtEtaPhiM(metPt, 0., metPhi, 0.)
        dPhi_jet_MET = jet.DeltaPhi(MET)
        if dPhi_jet_MET < min_dPhi_jet_MET[0]: min_dPhi_jet_MET[0] = dPhi_jet_MET

        if isMC:
            jet_FL_List.append(entry.Jet_hadronFlavour[i])
        jet_Pt_List.append(jetPt[i])
        jet_CvsL_List.append(entry.Jet_CvsL[i])
        jet_CvsB_List.append(entry.Jet_CvsB[i])
        jet_CvsB_CvsL_List.append((entry.Jet_CvsB[i])+(entry.Jet_CvsL[i]))
        jet_CvsB_CvsL_List2.append((entry.Jet_CvsB[i])**2+(entry.Jet_CvsL[i])**2)

        HT_temp         += jetPt[i]
        totalJetEnergy  += jet.E()
        if entry.Jet_CvsL[i]>0:
            totalJetCvsLpt  += entry.Jet_CvsL[i]*jetPt[i]

        j_Pt_List.append(jetPt[i])
        j_Eta_List.append(entry.Jet_eta[i])
        j_Phi_List.append(entry.Jet_phi[i])
        j_Mass_List.append(jetMass[i])
        j_CvsL_List.append(entry.Jet_CvsL[i])
        j_CvsB_List.append(entry.Jet_CvsB[i])
        j_qgl_List.append(entry.Jet_qgl[i])
        j_MuonIdx1_List.append(entry.Jet_muonIdx1[i])
        j_MuonIdx2_List.append(entry.Jet_muonIdx2[i])
        
        if "Jet_DeepFlavCvsL" in validBranches:
            jet_DeepFlavCvsL.push_back(entry.Jet_DeepFlavCvsL[i])
            jet_DeepFlavCvsB.push_back(entry.Jet_DeepFlavCvsB[i])
        
        jet_chEmEF.push_back(entry.Jet_chEmEF[i])
        jet_neEmEF.push_back(entry.Jet_neEmEF[i])
        jet_muplusneEmEF.push_back(Jet_muplusneEmEF)
        jet_jetId.push_back(entry.Jet_jetId[i])
        jet_puId.push_back(entry.Jet_puId[i])
        jet_muonIdx1.push_back(entry.Jet_muonIdx1[i])
        jet_muEF.push_back(Jet_muEF)
        jet_nMuons.push_back(entry.Jet_nMuons[i])
        # jet_lepFiltCustom.push_back(jetFilterFlags[i])

        jet_btagCMVA.push_back(entry.Jet_btagCMVA[i])
        jet_btagDeepB.push_back(entry.Jet_btagDeepB[i])
        jet_btagDeepC.push_back(entry.Jet_btagDeepC[i])
        jet_btagCSVV2.push_back(entry.Jet_btagCSVV2[i])
        jet_btagDeepFlavB.push_back(entry.Jet_btagDeepFlavB[i])

        if isMC:
            j_hadronFlv_List.append(entry.Jet_hadronFlavour[i])
            
            foundLep = False
            for iGen in range(entry.nGenPart):
                if entry.GenPart_status[iGen] != 1: continue
                genPart =  TLorentzVector()
                genPart.SetPtEtaPhiM(entry.GenPart_pt[iGen],entry.GenPart_eta[iGen],entry.GenPart_phi[iGen],entry.GenPart_mass[iGen])                
                if jet.DeltaR(genPart) > 0.4: continue
                if abs(entry.GenPart_pdgId[iGen]) not in [11,13,15]: continue
                if int(str(bin(entry.GenPart_statusFlags[iGen]))[-1]) == 1:
                    foundLep = True
                    break                   
            jet_isHardLep.push_back(foundLep)
                
    HT[0]                  = HT_temp

    if totalJetEnergy!=0:
        centrality[0]          = HT_temp/totalJetEnergy
    if HT_temp!=0:
        avgCvsLpT[0]           = (totalJetCvsLpt+1)/HT_temp

    if debug == True:
        print "Preselection 2 : at least one jet with jet_pt > 20 and jet_eta < 2.4/2.5"
    if len(jetList)<1: continue


    leadCvsB_jetidx[0] = jet_CvsB_List.index(max(jet_CvsB_List))
    leadCvsL_jetidx[0] = jet_CvsL_List.index(max(jet_CvsL_List))

    # Save jets according to hadron flavour
    if isMC:
        for i in range(0,len(j_hadronFlv_List)):
            if j_hadronFlv_List[i] == 4:
                eta_Of_cJet.push_back(j_Eta_List[i])
                pt_Of_cJet.push_back(j_Pt_List[i])
                phi_Of_cJet.push_back(j_Phi_List[i])
            elif j_hadronFlv_List[i] == 5:
                eta_Of_bJet.push_back(j_Eta_List[i])
                pt_Of_bJet.push_back(j_Pt_List[i])
                phi_Of_bJet.push_back(j_Phi_List[i])
            elif j_hadronFlv_List[i] == 0:
                eta_Of_lJet.push_back(j_Eta_List[i])
                pt_Of_lJet.push_back(j_Pt_List[i])
                phi_Of_lJet.push_back(j_Phi_List[i])
    # ==========================================================================

    # ========================== Construct W boson =============================
    VBoson = 0

    # Electron channel
    if not isElec and len(m_Pt_List)==1:
        for i in range(0, len(m_Pt_List)):
            mu =  TLorentzVector()
            mu.SetPtEtaPhiM(m_Pt_List[i],m_Eta_List[i],m_Phi_List[i],m_Mass_List[i])
            muon.append(mu)
        MET = TLorentzVector()
        MET.SetPtEtaPhiM(metPt, 0., metPhi, 0.)
        VBoson      = (muon[0]+MET)
        DPhi_METlep[0] = (muon[0]).DeltaPhi(MET)
        W_Mass[0]   = (muon[0]+MET).M()
        W_Tmass[0]  = (muon[0]+MET).Mt()
        W_Pt[0]     = (muon[0]+MET).Pt()
        W_Eta[0]    = (muon[0]+MET).Eta()
        W_Phi[0]    = (muon[0]+MET).Phi()

    # Muon channel
    if not isMuon and len(e_Pt_List)==1:
        for i in range(0, len(e_Pt_List)):
            el =  TLorentzVector()
            el.SetPtEtaPhiM(e_Pt_List[i],e_Eta_List[i],e_Phi_List[i],e_Mass_List[i])
            elec.append(el)
        VBoson      = (elec[0]+MET)
        DPhi_METlep[0] = (elec[0]).DeltaPhi(MET)
        W_Mass[0]   = (elec[0]+MET).M()
        W_Tmass[0]  = (elec[0]+MET).Mt()
        W_Pt[0]     = (elec[0]+MET).Pt()
        W_Eta[0]    = (elec[0]+MET).Eta()
        W_Phi[0]    = (elec[0]+MET).Phi()

    if debug == True:
        print "Preselection 3 : W_pt > 50"
    # if W_Pt[0]<50: continue
    if W_Mass[0] < 55: continue
    # ==========================================================================

    # ========================= Trigger selection ==============================
    if debug == True:
        print "Preselection 4 : TRIGGERS"
        print "HLT_IsoMu24"
        print "HLT_IsoTkMu24"
        print "HLT_Ele27_WPTight_Gsf"
    if era == 2016:
        if ( entry.HLT_IsoMu24 == 0 ) and ( entry.HLT_IsoTkMu24 == 0 ) and (entry.HLT_Ele27_WPTight_Gsf == 0 )  : continue
    elif era == 2017:
        # if "HLT_Ele32_WPTight_Gsf" in validBranches:
        #     eleTrig2017 = (bool(entry.HLT_Ele32_WPTight_Gsf_L1DoubleEG) and bool(entry.HLT_Ele35_WPTight_Gsf_L1EGMT)) or bool(entry.HLT_Ele32_WPTight_Gsf)
        # else:
        #     eleTrig2017 = (bool(entry.HLT_Ele32_WPTight_Gsf_L1DoubleEG) and bool(entry.HLT_Ele35_WPTight_Gsf_L1EGMT))
        eleTrig2017 = entry.HLT_Ele32_WPTight_Gsf_L1DoubleEG
        if ( entry.HLT_IsoMu27 == 0 ) and ( eleTrig2017 == 0 )  : continue
    elif era == 2018:
        if ( entry.HLT_IsoMu24 == 0 ) and ( entry.HLT_Ele32_WPTight_Gsf == 0 ): continue
        
    TriggerPass = True

    if era == 2016: #Not used, hence not done for 2017
        if ( entry.HLT_IsoMu24 == 1 ) or ( entry.HLT_IsoTkMu24 == 1 ):
            muTrig[0] = 1
        else:
            muTrig[0] = 0
        if (entry.HLT_Ele27_WPTight_Gsf == 1 ):
            eleTrig[0] = 1
        else:
            eleTrig[0] = 0
    # ==========================================================================

    # ========================= Soft Muon inside jets ==========================
#    minDR = 7
    jetMu_Charge = -1000
    nMuJet[0] = 0

    foundMuJet = False
    for ij in range(len(j_Pt_List)):
        if foundMuJet: break
        if isMuon:
            dRjl = jetList[ij].DeltaR(muon[0])
        elif isElec:
            dRjl = jetList[ij].DeltaR(elec[0])
        if dRjl < 0.5: continue

        for i in [j_MuonIdx1_List[ij],j_MuonIdx2_List[ij]]:
            if i < 0: continue
            if Muon_pt[i]>25 or abs(entry.Muon_eta[i])>2.4: continue
            if entry.Muon_tightId[i]<=0: continue
            if entry.Muon_pfRelIso04_all[i]<0.2: continue

            jetMu = TLorentzVector()
            jetMu.SetPtEtaPhiM(Muon_pt[i],entry.Muon_eta[i],entry.Muon_phi[i],entry.Muon_mass[i])

            dRmj = jetMu.DeltaR(jetList[ij])
            if dRmj > 0.4: continue

            foundMuJet = True
            jetMu_Pt[0] = Muon_pt[i]
            jetMu_Eta = entry.Muon_eta[i]
            jetMu_iso[0] = entry.Muon_pfRelIso04_all[i]
            jetMu_dz[0] = entry.Muon_dz[i]
            jetMu_dxy[0] = entry.Muon_dxy[i]
            jetMu_sip3d[0] = entry.Muon_sip3d[i]
            jetMu_Charge = entry.Muon_charge[i]
            muJet_idx[0] = ij
            dR_jet_jetMu[0] = dRmj
            dR_lep_jet[0] = dRjl
            MET = TLorentzVector()
            MET.SetPtEtaPhiM(metPt, 0., metPhi, 0.)
            dPhi_muJet_MET[0] = jetList[ij].DeltaPhi(MET)
            jetMuPt_by_jetPt[0] =  Muon_pt[i]/j_Pt_List[ij]
            jetMu_PtRel[0] = Muon_pt[i]*math.sin(jetMu.Angle(jetList[ij].Vect()))     #p_{T,rel} = |M|sin(theta): M = Muon pT, theta = angle between jet and muon

            # Construct Z
            if isMuon and jetMu_Charge*m_Charge_List[0] < 0:
                Z_Mass[0]   = (muon[0]+jetMu).M()
                Z_Pt[0]     = (muon[0]+jetMu).Pt()
                Z_Eta[0]    = (muon[0]+jetMu).Eta()
                Z_Phi[0]    = (muon[0]+jetMu).Phi()
                Z_Mass_withJet[0] = (muon[0]+jetList[ij]).M()

#                Z_Mass_best[0] = Z_Mass[0]
                dR_mu_mu_best[0] = jetMu.DeltaR(muon[0])    

    if jetMu_Pt[0] < 0: continue
    # ==========================================================================
    
    # ================== Find all possible combos for Z mass ===================
    
    mupluslist = []
    muminuslist = []
    
    nMu = 0
    for i in range(0, len(Muon_pt)):
        if entry.Muon_tightId[i]<=0: continue
        nMu += 1
        thisMu = TLorentzVector()
        thisMu.SetPtEtaPhiM(Muon_pt[i],entry.Muon_eta[i],entry.Muon_phi[i],entry.Muon_mass[i])
        if entry.Muon_charge[i] > 0:
            mupluslist.append(thisMu)
        else:
            muminuslist.append(thisMu)
    
    nTightMu[0] = nMu
    minDiff = 1000
    
    for muplus in mupluslist:
        for muminus in muminuslist:
            combmass = (muplus+muminus).M()
            if combmass > Z_Mass_max[0]: Z_Mass_max[0] = combmass
            if combmass < Z_Mass_min[0]: Z_Mass_min[0] = combmass
            if abs(combmass - 91.) < minDiff:
                minDiff = abs(combmass - 91.)
                Z_Mass_best[0] = combmass
                Z_Pt_best[0] = (muplus+muminus).Pt()
            
    # ==========================================================================
            
    # ========================= Find best Z mass ===============================
    # Find mu+mu- pair with inv mass closest to Z mass
    # NOT USED
    # minDiff = abs(Z_Mass[0] - 91.)
    #
    # if isMuon:
    #     for i in range(0, len(Muon_pt)):
    #         if Muon_pt[i]>30 or abs(entry.Muon_eta[i])>2.4: continue
    #         if entry.Muon_tightId[i]<=0: continue
    #         if entry.Muon_charge[i]*m_Charge_List[0] > 0: continue
    #
    #         otherMu = TLorentzVector()
    #         otherMu.SetPtEtaPhiM(Muon_pt[i],entry.Muon_eta[i],entry.Muon_phi[i],entry.Muon_mass[i])
    #
    #         newZ_Mass = (muon[0]+otherMu).M()
    #         if abs(newZ_Mass - 91.) < minDiff:
    #             minDiff = abs(newZ_Mass - 91.)
    #             Z_Mass_best[0] = newZ_Mass
    #             dR_mu_mu_best[0] = otherMu.DeltaR(muon[0])
    # ==========================================================================


    # ============================= Store leptons ==============================
    if isElec:
        is_E[0] = isElec
        for i, ePt in enumerate(e_Pt_List):
            E_Mass.push_back(e_Mass_List[i])
            E_Pt.push_back(ePt)
            E_Eta.push_back(e_Eta_List[i])
            E_Phi.push_back(e_Phi_List[i])
            E_Charge.push_back(e_Charge_List[i])

    if isMuon:
        is_M[0] = isMuon
        for i, mPt in enumerate(m_Pt_List):
            M_Mass.push_back(m_Mass_List[i])
            M_Pt.push_back(mPt)
            M_Eta.push_back(m_Eta_List[i])
            M_Phi.push_back(m_Phi_List[i])
            M_Charge.push_back(m_Charge_List[i])

    # ==========================================================================

    # ============================== Store jets ================================
    if isMC:
        numOf_bJet[0] = 0
        numOf_cJet[0] = 0
        numOf_lJet[0] = 0
    for i, jPt in enumerate(j_Pt_List):
        jet_Mass.push_back(j_Mass_List[i])
        jet_Pt.push_back(jPt)
        jet_Eta.push_back(j_Eta_List[i])
        jet_Phi.push_back(j_Phi_List[i])
        jet_CvsL.push_back(j_CvsL_List[i])
        jet_CvsB.push_back(j_CvsB_List[i])
        jet_qgl.push_back(j_qgl_List[i])
        if isMC:
            jet_hadronFlv.push_back(j_hadronFlv_List[i])
            if j_hadronFlv_List[i]==5:
                numOf_bJet[0] += 1
            elif j_hadronFlv_List[i]==4:
                numOf_cJet[0] += 1
            else:
                numOf_lJet[0] += 1
    jet_nJet[0]            = len(j_Pt_List)
    # ==========================================================================

    # ==================== Semileptonic tt c jet enrichment ====================
    if jet_nJet[0] >= 4:
        permutejets = range(int(jet_nJet[0]))
        permutejets.remove(int(muJet_idx[0]))
        
        if signWeight[0] > 0:               #OS    
            btagvals = [jet_btagDeepB[i] for i in permutejets]
            largestbtagidx = btagvals.index(max(btagvals))
            del permutejets[largestbtagidx]
            hadbcand = jetList[largestbtagidx]    
        else:                               #SS
            hadbcand = jetList[int(muJet_idx[0])]
        allperms = list(itertools.permutations(permutejets,2))
            
        minChi2 = 1e10
        for thisperm in allperms:
            ccand = jetList[thisperm[0]]
            scand = jetList[thisperm[1]]
            # if signWeight[0] > 0:  hadbcand = jetList[thisperm[2]]

            Wcand = ccand + scand
            tcand = Wcand + hadbcand
            thisChi2 = (Wcand.M() - 80.3)**2 + (tcand.M() - 172.5)**2
            if thisChi2 < minChi2:
                semitChi2[0]            = thisChi2
                semitWCandMass[0]       = Wcand.M()
                semitWCandpT[0]         = Wcand.Pt()
                semittCandMass[0]       = tcand.M()
                semittCandpT[0]         = tcand.Pt()
                semitc1idx[0]           = thisperm[0]
                semitc2idx[0]           = thisperm[1]
                minChi2 = thisChi2

        # if semitChi2[0] < 1000: print semitWCandMass[0],semittCandMass[0],semitChi2[0],jet_hadronFlv[int(semitc1idx[0])],jet_hadronFlv[int(semitc2idx[0])],jet_hadronFlv[int(muJet_idx[0])],jet_hadronFlv[largestbtagidx]

    # ==========================================================================

    # ============================ Calculate weights ===========================
    # Sign Weights
    if isElec:
        signWeight[0] = e_Charge_List[0]*jetMu_Charge*(-1.)
    elif isMuon:
        signWeight[0] = m_Charge_List[0]*jetMu_Charge*(-1.)
    else:
        continue

    genWeight[0] = 1.
    PUWeight[0]  = 1.
    PUWeight_up[0] = 1.
    PUWeight_down[0] = 1.
    EleIDSF[0] = 1.
    EleIDSF_up[0] = 1.
    EleIDSF_down[0] = 1.
    EleRecoSF = 1.
    EleRecoErr = 0.
    EleTrigSF = 1.
    EleTrigErr = 0.
    MuIDSF[0] = 1.
    MuIDSF_up[0] = 1.
    MuIDSF_down[0] = 1.
    eventWeightUnsigned[0] = 1.
    eventWeight[0] = 1.
    eventWeightnoPU[0] = 1.
    LHEScaleWeight_muR_up[0] = 1.
    LHEScaleWeight_muR_down[0] = 1.
    # LHEScaleWeight_muF_up[0] = 1.
    LHEScaleWeight_muF_down[0] = 1.
    LHEScaleWeight_muF_up[0] = 1.
    PSWeightISR_up[0] = 1.
    PSWeightISR_down[0] = 1.
    PSWeightFSR_down[0] = 1.
    PSWeightFSR_up[0] = 1.

    if isMC:
        # MC Gen Weight
        genWeight[0] = entry.genWeight

        # PU Weights
        if era != 2018:
            PUWeight[0] = entry.puWeight
            if PUWeight[0]!=0:
                PUWeight_up[0] = entry.puWeightUp/PUWeight[0]
                PUWeight_down[0] = entry.puWeightDown/PUWeight[0]
        else:
            PUWeight[0] = getPUweight(entry.Pileup_nTrueInt,0)
            if PUWeight[0]!=0:
                PUWeight_up[0] = getPUweight(entry.Pileup_nTrueInt,1)/PUWeight[0]
                PUWeight_down[0] = getPUweight(entry.Pileup_nTrueInt,-1)/PUWeight[0]

        # LHE Scale
        if "LHEScaleWeight" in validBranches:
            LHEScaleList = list(entry.LHEScaleWeight)

            if len(LHEScaleList) > 7:
                LHEScaleWeight_muR_up[0] = LHEScaleList[7]
                LHEScaleWeight_muR_down[0] = LHEScaleList[1]

            # LHEScaleWeight_muF_up[0] = LHEScaleList[5]
                LHEScaleWeight_muF_down[0] = LHEScaleList[3]
                LHEScaleWeight_muF_up[0] = LHEScaleList[5]
            
        if "TT" in channel:
            PSWeight = list(entry.PSWeight)
            
            PSWeightISR_up[0] = PSWeight[2]
            PSWeightISR_down[0] = PSWeight[0]
            PSWeightFSR_up[0] = PSWeight[3]
            PSWeightFSR_down[0] = PSWeight[1]

        # Electron ID
        if isElec:
            xbin = EGammaHisto2d.GetXaxis().FindBin(e_Eta_List[0])
            ybin = min(EGammaHisto2d.GetYaxis().FindBin(e_Pt_List[0]),EGammaHisto2d.GetNbinsY())
            EleIDonly = EGammaHisto2d.GetBinContent(xbin,ybin)
            EleIDErr = EGammaHisto2d.GetBinError(xbin,ybin)

            if era == 2017 or era == 2018:
                xbin = ERecoHisto2d.GetXaxis().FindBin(e_Eta_List[0])
                ybin = min(ERecoHisto2d.GetYaxis().FindBin(e_Pt_List[0]),ERecoHisto2d.GetNbinsY())
                EleRecoSF = ERecoHisto2d.GetBinContent(xbin,ybin)
                EleRecoErr = ERecoHisto2d.GetBinError(xbin,ybin)

                # xbin = ETrigHisto.GetXaxis().FindBin(e_Pt_List[0])
                # EleTrigSF = ETrigHisto.GetBinContent(xbin)
                # EleTrigErr = ETrigHisto.GetBinError(xbin)
                # print e_Pt_List[0],EleTrigSF,EleTrigErr

                EleTrigTuple = getSF(etrigjson,e_Pt_List[0],e_Eta_List[0])
                EleTrigSF = EleTrigTuple[0]
                EleTrigErr = EleTrigTuple[1]

            EleIDSF[0] = EleIDonly*EleRecoSF*EleTrigSF
            # print e_Pt_List[0],EleTrigSF,EleTrigErr

            if EleIDSF[0]!=0:
                EleIDSF_up[0] = ((EleIDonly+EleIDErr)*(EleRecoSF+EleRecoErr)*(EleTrigSF+EleTrigErr))/EleIDSF[0]
                EleIDSF_down[0] = ((EleIDonly-EleIDErr)*(EleRecoSF-EleRecoErr)*(EleTrigSF-EleTrigErr))/EleIDSF[0]

            if era == 2017 or era == 2018:
                ybin = MuIDlowpT1718histo2d.GetYaxis().FindBin(abs(jetMu_Eta))
                xbin = MuIDlowpT1718histo2d.GetXaxis().FindBin(jetMu_Pt[0])
                MuIDlowpTBF = MuIDlowpT1718histo2d.GetBinContent(xbin,ybin)
                MuIDlowpTBF_err = MuIDlowpT1718histo2d.GetBinError(xbin,ybin)

                MuIDSF[0] = MuIDlowpTBF
                if MuIDSF[0]!=0:
                    MuIDSF_up[0] = (MuIDlowpTBF+MuIDlowpTBF_err) / MuIDSF[0]
                    MuIDSF_down[0] = (MuIDlowpTBF-MuIDlowpTBF_err) / MuIDSF[0]

        # Muon ID
        if isMuon:
            if era == 2016:
                xbin = MuID2016BFhisto2d.GetXaxis().FindBin(m_Eta_List[0])
                ybin = MuID2016BFhisto2d.GetYaxis().FindBin(m_Pt_List[0])
                MuIDBF = MuID2016BFhisto2d.GetBinContent(xbin,min(6,ybin))
                MuIDBF_err = MuID2016BFhisto2d.GetBinError(xbin,min(6,ybin))

                xbin = MuID2016GHhisto2d.GetXaxis().FindBin(m_Eta_List[0])
                ybin = MuID2016GHhisto2d.GetYaxis().FindBin(m_Pt_List[0])
                MuIDGH = MuID2016GHhisto2d.GetBinContent(xbin,min(6,ybin))
                MuIDGH_err = MuID2016GHhisto2d.GetBinError(xbin,min(6,ybin))

                MuIDSF[0] = 0.55*MuIDBF + 0.45*MuIDGH
                if MuIDSF[0]!=0:
                    MuIDSF_up[0] = (0.55*(MuIDBF+MuIDBF_err) + 0.45*(MuIDGH+MuIDGH_err))/MuIDSF[0]
                    MuIDSF_down[0] = (0.55*(MuIDBF-MuIDBF_err) + 0.45*(MuIDGH-MuIDGH_err))/MuIDSF[0]

            elif era == 2017 or era == 2018:
                nbins = MuID1718histo2d.GetNbinsX()
                ybin = MuID1718histo2d.GetYaxis().FindBin(abs(m_Eta_List[0]))
                xbin = MuID1718histo2d.GetXaxis().FindBin(m_Pt_List[0])
                MuIDBF = MuID1718histo2d.GetBinContent(max(1,min(nbins,xbin)),ybin)
                MuIDBF_err = MuID1718histo2d.GetBinError(max(1,min(nbins,xbin)),ybin)

                nbins = MuIso1718histo2d.GetNbinsX()
                ybin = MuIso1718histo2d.GetYaxis().FindBin(abs(m_Eta_List[0]))
                xbin = MuIso1718histo2d.GetXaxis().FindBin(m_Pt_List[0])
                MuIsoBF = MuIso1718histo2d.GetBinContent(max(1,min(nbins,xbin)),ybin)
                MuIsoBF_err = MuIso1718histo2d.GetBinError(max(1,min(nbins,xbin)),ybin)

                ybin = MuTrig1718histo2d.GetYaxis().FindBin(abs(m_Eta_List[0]))
                xbin = MuTrig1718histo2d.GetXaxis().FindBin(m_Pt_List[0])
                MuTrigBF = MuTrig1718histo2d.GetBinContent(xbin,ybin)
                MuTrigBF_err = MuTrig1718histo2d.GetBinError(xbin,ybin)

                ybin = MuIDlowpT1718histo2d.GetYaxis().FindBin(abs(jetMu_Eta))
                xbin = MuIDlowpT1718histo2d.GetXaxis().FindBin(jetMu_Pt[0])
                MuIDlowpTBF = MuIDlowpT1718histo2d.GetBinContent(xbin,ybin)
                MuIDlowpTBF_err = MuIDlowpT1718histo2d.GetBinError(xbin,ybin)

                MuIDSF[0] = MuIDBF * MuIsoBF * MuTrigBF * MuIDlowpTBF
                if MuIDSF[0]!=0:
                    MuIDSF_up[0] = ((MuIDBF+MuIDBF_err) * (MuIsoBF+MuIsoBF_err) * (MuTrigBF+MuTrigBF_err) * (MuIDlowpTBF+MuIDlowpTBF_err)) / MuIDSF[0]
                    MuIDSF_down[0] = ((MuIDBF-MuIDBF_err) * (MuIsoBF-MuIsoBF_err) * (MuTrigBF-MuTrigBF_err) * (MuIDlowpTBF-MuIDlowpTBF_err)) / MuIDSF[0]

    eventWeight[0] = signWeight[0] * genWeight[0] * PUWeight[0] * EleIDSF[0] * MuIDSF[0]
    #print PUWeight_up[0],PUWeight_down[0],EleIDSF_up[0],EleIDSF_down[0],MuIDSF_up[0],MuIDSF_down[0]

    eventWeightUnsigned[0] = eventWeight[0]/signWeight[0]
    eventWeightnoPU[0] = signWeight[0] * genWeight[0] * EleIDSF[0] * MuIDSF[0]
    # ==========================================================================

    # ============================ Fill output tree ============================
    if (isMuon or isElec) and len(j_Pt_List) >= 1 and W_Mass[0]>=55 and TriggerPass and jetMu_Pt[0] > 0.:
        run[0]              = entry.run
        lumiBlock[0]        = entry.luminosityBlock
        event[0]            = entry.event
        if "LHE_HT" in validBranches:
            LHE_HT[0]           = entry.LHE_HT
        if "LHE_Njets" in validBranches:
            if type(entry.LHE_Njets) is str:
                LHE_Njets[0]        = ord(entry.LHE_Njets)
            else:
                LHE_Njets[0]        = entry.LHE_Njets
        if "LHE_Vpt" in validBranches:
            LHE_Vpt[0]        = entry.LHE_Vpt

        nPV[0] = entry.PV_npvs
        nPVGood[0] = entry.PV_npvsGood
        nSV[0] = entry.nSV

        if isMuon:
            QCDveto[0] = int( M_RelIso[0] < 0.05 and (hardMu_Jet_PtRatio[0] < 0 or hardMu_Jet_PtRatio[0] > 0.75) and abs(M_dz[0]) < .01 and abs(M_dxy[0]) < .002 and M_sip3d[0] < 0.2 )
        elif isElec:
            QCDveto[0] = int( E_RelIso[0] < 0.05 and (hardE_Jet_PtRatio[0] < 0 or hardE_Jet_PtRatio[0] > 0.75) and abs(E_dz[0]) < .02 and abs(E_dxy[0]) < .01 and E_sip3d[0] < 0.25 )

        SoftActivityJetHT[0]       = entry.SoftActivityJetHT
        SoftActivityJetNjets2[0]   = entry.SoftActivityJetNjets2
        SoftActivityJetNjets5[0]   = entry.SoftActivityJetNjets5
        SoftActivityJetNjets10[0]  = entry.SoftActivityJetNjets10
        
        #if is_M[0] and (Z_Mass[0] < 85 or Z_Mass[0] > 95) and jetMuPt_by_jetPt[0] < 0.4:
            #M_JetPhoMu = -1.
            #for ipho in range(entry.nPhoton):
                #if entry.Photon_mvaID_WP90[ipho] == 0: continue
                #Pho = TLorentzVector()
                #Pho.SetPtEtaPhiM(entry.Photon_pt[ipho],entry.Photon_eta[ipho],entry.Photon_phi[ipho],entry.Photon_mass[ipho])
                #if Pho.DeltaR(muon[0]) < 0.4: M_JetPhoMu = (jetList[int(muJet_idx[0])]+muon[0]+Pho).M()
            #print "jet+Mu inv mass:",(jetList[int(muJet_idx[0])]+muon[0]).M(), "nPhoton:", entry.nPhoton, "M_JetPhoMu:", M_JetPhoMu

        outputTree.Fill()
    else:
        continue
    # ==========================================================================

h_postp.Write()
outputTree.Write()

# ========================= Store gen event count ==============================
nEventTree = iFile.Get("Runs")
nEventCount = 0
nEventWeight = 0
if isMC:
    for entry2 in nEventTree:
        nEventCount += entry2.genEventCount
        nEventWeight += entry2.genEventSumw
    print "Total event processed by Nano AOD post processor : ", nEventCount
    h_total.SetBinContent(2,nEventWeight)
    h_nEvent.SetBinContent(2,nEventCount)
h_total.Write()
h_nEvent.Write()
# ==============================================================================

print "Total events processed : ",count
print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))
