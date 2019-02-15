from ROOT import *
from array import array

import glob, sys, time, os
import numpy as np
import nuSolutions as nu
import types, math

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
isNano = True

parentDir = 'VHcc_2016V4bis_Nov18/'
if "spmondal" in fullName and fullName.startswith('/pnfs/'):
    pref = ""
#    parentDir = 'VHbbPostNano2016_V5_CtagSF/'
    parentDir = fullName.split('/')[8]+"/"
    isNano = False
if fullName.startswith('/store/'):
    if "lmastrol" in fullName:
        pref = "/pnfs/desy.de/cms/tier2"
        isNano = False
    else:
        pref = "root://xrootd-cms.infn.it//"
        parentDir="NanoCrabProdXmas/"
elif fullName.startswith('root:'):
    pref = ""
else:
    pref = "file:"

if isLocal: pref = "file:"

iFile = TFile.Open(pref+fileName)

inputTree = iFile.Get("Events")
inputTree.SetBranchStatus("*",1)

sampName=fullName.split(parentDir)[1].split('/')[0]
channel=sampName
if "_" in channel: channel=channel.split("_")[0]
# channel="Generic"
if not 'Single' in channel and not 'Double' in channel and not 'MuonEG' in channel:
    isMC = True
else:
    isMC = False
print "Using channel =",channel, "; isMC:", isMC
print "Using jet pT with JEC correction:", JECName

if not isMC and JECName!="nom":
    print "Cannot run data with JEC systematics!! Exiting."
    sys.exit()

dirName=open("dirName.sh",'w')
if isMC and JECName!="nom":
    sampName += "_"+JECName
dirName.write("echo \""+sampName+"\"")
dirName.close()
# ==============================================================================

# =============================== SF files =====================================
# PU
# PU2016File = TFile('scalefactors/pileUPinfo2016.root')
# pileup2016histo = PU2016File.Get('hpileUPhist')

# EGamma
EID2016File = TFile('scalefactors/egammaSF_mva80.root')
EGamma2016histo2d = EID2016File.Get('EGamma_SF2D')

# Muon
MuID2016BFFile = TFile('scalefactors/RunBCDEF_SF_ID.root')
MuID2016BFhisto2d = MuID2016BFFile.Get('NUM_TightID_DEN_genTracks_eta_pt')
MuID2016GHFile = TFile('scalefactors/RunGH_SF_ID.root')
MuID2016GHhisto2d = MuID2016GHFile.Get('NUM_TightID_DEN_genTracks_eta_pt')

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
jet_qgl            = std.vector('double')()

jet_chEmEF         = std.vector('double')()
jet_jetId          = std.vector('double')()
jet_muonIdx1       = std.vector('double')()
jet_muEF           = std.vector('double')()
jet_muPtRatio      = std.vector('double')()
jet_nMuons         = std.vector('double')()
jet_lepFiltCustom  = std.vector('double')()

jet_btagCMVA       = std.vector('double')()
jet_btagCSVV2      = std.vector('double')()
jet_btagDeepB      = std.vector('double')()
jet_btagDeepC      = std.vector('double')()

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

leadCvsL_jetidx      = array('d',[0])
leadCvsB_jetidx      = array('d',[0])

QCDveto             = array('d',[0])

nPV                 = array('d',[0])
nPVGood             = array('d',[0])
nSV                 = array('d',[0])

if isMC:
    jet_hadronFlv      = std.vector('double')()
jet_nJet           = array('d',[0])
met_Pt             = array('d',[0])
met_signif         = array('d',[0])
is_EE               = array('d',[0])
is_MM               = array('d',[0])
is_ME               = array('d',[0])
# is_H_mass_CR       = array('d',[0])
# is_W_mass_CR       = array('d',[0])

Z_Mass           = array('d',[0])
Z_Pt             = array('d',[0])
Z_Eta            = array('d',[0])
Z_Phi            = array('d',[0])

Z2_Mass           = array('d',[0])
Z3_Mass           = array('d',[0])

Z_Mass_best      = array('d',[0])
dR_mu_mu_best    = array('d',[0])

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
outputTree.Branch('jet_qgl'          ,jet_qgl      )

outputTree.Branch('jet_chEmEF'          ,jet_chEmEF      )
outputTree.Branch('jet_jetId'           ,jet_jetId      )
outputTree.Branch('jet_muonIdx1'        ,jet_muonIdx1      )
outputTree.Branch('jet_muEF'            ,jet_muEF      )
outputTree.Branch('jet_muPtRatio'            ,jet_muPtRatio      )
outputTree.Branch('jet_nMuons'          ,jet_nMuons      )
outputTree.Branch('jet_lepFiltCustom'   ,jet_lepFiltCustom      )

outputTree.Branch('jet_btagCMVA'    ,jet_btagCMVA      )
outputTree.Branch('jet_btagDeepB'   ,jet_btagDeepB      )
outputTree.Branch('jet_btagDeepC'   ,jet_btagDeepC      )
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

outputTree.Branch('leadCvsB_jetidx'        ,leadCvsB_jetidx     ,'leadCvsB_jetidx/D')
outputTree.Branch('leadCvsL_jetidx'        ,leadCvsL_jetidx     ,'leadCvsL_jetidx/D')

outputTree.Branch('QCDveto'        ,QCDveto     ,'QCDveto/D')

outputTree.Branch('nPV'     ,nPV        ,'nPV/D')
outputTree.Branch('nPVGood' ,nPVGood    ,'nPVGood/D')
outputTree.Branch('nSV'     ,nSV        ,'nSV/D')

if isMC:
    outputTree.Branch('jet_hadronFlv'    ,jet_hadronFlv )
outputTree.Branch('met_Pt'           ,met_Pt          ,'met_Pt/D'     )
outputTree.Branch('met_Phi'          ,met_Phi         ,'met_Phi/D')
outputTree.Branch('met_signif'       ,met_signif      ,'met_signif/D')

outputTree.Branch('Z_Mass'           ,Z_Mass          ,'Z_Mass/D'     )
outputTree.Branch('Z_Pt'             ,Z_Pt            ,'Z_Pt/D'     )
outputTree.Branch('Z_Eta'            ,Z_Eta           ,'Z_Eta/D'     )
outputTree.Branch('Z_Phi'            ,Z_Phi           ,'Z_Phi/D'     )

outputTree.Branch('Z2_Mass'           ,Z2_Mass          ,'Z2_Mass/D'     )
outputTree.Branch('Z3_Mass'           ,Z3_Mass          ,'Z3_Mass/D'     )

outputTree.Branch('Z_Mass_best'      ,Z_Mass_best     ,'Z_Mass_best/D'     )
outputTree.Branch('dR_mu_mu_best'    ,dR_mu_mu_best   ,'dR_mu_mu_best/D'     )


outputTree.Branch('W_Mass'           ,W_Mass          ,'W_Mass/D'     )
outputTree.Branch('W_Pt'             ,W_Pt            ,'W_Pt/D'     )
outputTree.Branch('W_Eta'            ,W_Eta           ,'W_Eta/D'     )
outputTree.Branch('W_Phi'            ,W_Phi           ,'W_Phi/D'     )

outputTree.Branch('W_Mass_nuSol'     ,W_Mass_nuSol    ,'W_Mass_nuSol/D'     )
outputTree.Branch('W_Pt_nuSol'       ,W_Pt_nuSol      ,'W_Pt_nuSol/D'     )
outputTree.Branch('W_Eta_nuSol'      ,W_Eta_nuSol     ,'W_Eta_nuSol/D'     )
outputTree.Branch('W_Phi_nuSol'      ,W_Phi_nuSol     ,'W_Phi_nuSol/D'     )

outputTree.Branch('is_EE'     ,is_EE    ,'is_EE/D'     )
outputTree.Branch('is_MM'     ,is_MM    ,'is_MM/D'     )
outputTree.Branch('is_ME'     ,is_ME    ,'is_ME/D'     )

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
    m_List                   = []
    m_plus_List              = []
    m_minus_List             = []
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
    isElec              = False
    isMuon              = False
    isMuE               = False
#     is_H_mass_CR[0]     = 0
#     is_W_mass_CR[0]     = 0

    is_EE[0]             = False
    is_MM[0]             = False
    is_ME[0]             = False

    run[0]              = -1000
    lumiBlock[0]        = -1000
    event[0]            = -1000
    LHE_HT[0]           = -1000
    LHE_Njets[0]        = -1000

    muTrig[0]           = -1
    eleTrig[0]          = -1

    HT[0]               = -1000

    Z_Mass[0]           = -1000
    Z_Pt[0]             = -1000
    Z_Eta[0]            = -1000
    Z_Phi[0]            = -1000

    Z2_Mass[0]           = -1000
    Z3_Mass[0]           = -1000

    Z_Mass_best[0]      = -1000
    dR_mu_mu_best[0]    = -1000

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
    jet_qgl.clear()

    jet_chEmEF.clear()
    jet_jetId.clear()
    jet_muonIdx1.clear()
    jet_muEF.clear()
    jet_muPtRatio.clear()
    jet_nMuons.clear()
    jet_lepFiltCustom.clear()

    jet_btagCMVA.clear()
    jet_btagDeepB.clear()
    jet_btagDeepC.clear()
    jet_btagCSVV2.clear()

    if isMC:
        jet_hadronFlv.clear()

    met_Pt[0]             = -1
    met_Phi[0]            = -1000
    met_signif[0]         = -1000
    # ==========================================================================

    if JECName=="nom":
        jetPt = entry.Jet_Pt
        jetMass = entry.Jet_mass
        metPt = entry.MET_Pt
        metPhi = entry.MET_Phi
    else:
        exec("jetPt = entry.Jet_pt_"+JECName)
        exec("jetMass = entry.Jet_mass_"+JECName)
        exec("metPt = entry.MET_pt_"+JECName)
        exec("metPhi = entry.MET_phi_"+JECName)

    # =========================== Select Leptons ===============================
    if debug == True:
        print "Preselection 1 : 1e, 1mu"
        print "                 electron selection : pt > 30 and eta<2.5"
        print "                 electron selection : Electron_mvaSpring16GP_WP80 > 0 "                # cutBased >= 3 (Medium)"
        # print "                 electron selection : Electron_pfRelIso03_all <= 0.15"
        print "                 muon selection : pt > 30 and eta<2.4"
        print "                 muon selection : Muon_tightId > 0"
        print "                 muon selection : Muon_pfRelIso04_all <= 0.15"

    for i in range(0, len(entry.Electron_pt)):
        if entry.Electron_pt[i]<30 or abs(entry.Electron_eta[i])>2.5: continue
        if abs(entry.Electron_eta[i]) > 1.442 and abs(entry.Electron_eta[i]) < 1.556: continue
        if entry.Electron_mvaSpring16GP_WP80[i]<=0: continue
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

    for i in range(0, len(entry.Muon_pt)):
        if entry.Muon_pt[i]<30 or abs(entry.Muon_eta[i])>2.4: continue
        if entry.Muon_tightId[i]<=0: continue
        if entry.Muon_pfRelIso04_all[i]>0.15: continue
        m_Pt_List.append(entry.Muon_pt[i])
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
            hardMu_Jet_PtRatio[0] = entry.Muon_pt[i]/jetPt[hardMu_jetidx]
    # ==========================================================================

    # =======================  1 e+- 1 mu-+ cut ===========================
    if len(m_Pt_List) == 1 and len(e_Pt_List) == 1:
        is_ME[0] = 1
        if e_Charge_List[0]*m_Charge_List[0] > 0 : continue
        mu = TLorentzVector()
        e = TLorentzVector()
        mu.SetPtEtaPhiM(m_Pt_List[0],m_Eta_List[0],m_Phi_List[0],m_Mass_List[0])
        e.SetPtEtaPhiM(e_Pt_List[0],e_Eta_List[0],e_Phi_List[0],e_Mass_List[0])
        Z_cand = mu + e

    elif len(m_Pt_List) == 2 and len(e_Pt_List) == 0:
        is_MM[0] = 1
        if m_Charge_List[0]*m_Charge_List[1] > 0 : continue
        mu1 = TLorentzVector()
        mu2 = TLorentzVector()
        mu1.SetPtEtaPhiM(m_Pt_List[0],m_Eta_List[0],m_Phi_List[0],m_Mass_List[0])
        mu2.SetPtEtaPhiM(m_Pt_List[1],m_Eta_List[1],m_Phi_List[1],m_Mass_List[1])
        Z_cand = mu1 + mu2
        if (Z_cand.M() > 81. and Z_cand.M() < 101.) or Z_cand.M() < 12.: continue

    elif len(m_Pt_List) == 0 and len(e_Pt_List) == 2:
        is_EE[0] = 1
        if e_Charge_List[0]*e_Charge_List[1] > 0 : continue
        e1 = TLorentzVector()
        e2 = TLorentzVector()
        e1.SetPtEtaPhiM(e_Pt_List[0],e_Eta_List[0],e_Phi_List[0],e_Mass_List[0])
        e2.SetPtEtaPhiM(e_Pt_List[1],e_Eta_List[1],e_Phi_List[1],e_Mass_List[1])
        Z_cand = e1 + e2
        if (Z_cand.M() > 81. and Z_cand.M() < 101.) or Z_cand.M() < 12.: continue
    else:
        continue

    # NOTE: This is not a real Z, it's just named Z for ease of implementation
    Z_Mass[0] = Z_cand.M()
    Z_Eta[0] = Z_cand.Eta()
    Z_Phi[0] = Z_cand.Phi()
    Z_Pt[0] = Z_cand.Pt()
    # ==========================================================================

    # ========================== Get MET, MET Cut =============================
    met_Pt[0]              = metPt
    met_Phi[0]             = metPhi
    met_signif[0]          = entry.MET_significance

    mW = 80.38
    mH = 125 + mW
    MET = TLorentzVector()
    MET.SetPtEtaPhiM(metPt, 0., metPhi, 0.)
    sigma2 = np.array([((MET.Px()*.1)**2,0),(0,(MET.Py()*.1)**2)])

    # if metPt < 40: continue
    # ==========================================================================

    # ============================ Jet selection ===============================
    if debug == True:
        print "                 Jet selection : jet_pt > 20 and jet_eta < 2.4"
        print "                 Jet selection : Jet_jetId >= 3"                 # Tight in 2016
        print "                 Jet selection : Jet_lepFilter = True"           # or Jet Mu EF < 0.8
        print "                 Jet selection : Jet_puId >= 0"

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
    # for i in range(0, len(entry.Muon_pt)):
    #     if entry.Muon_tightId[i]<=0: continue
    #     if entry.Muon_dxy[i]>0.05: continue
    #     if entry.Muon_dz[i]>0.2: continue
    #     if entry.Muon_pt[i]<15: continue
    #     if entry.Muon_pfRelIso04_all[i]>0.5: continue
    #
    #     jetInd = entry.Muon_jetIdx[i]
    #     if jetInd >= 0:
    #         jetFilterFlags[jetInd] = False
    # --------------------------------------------------------------------------

    HT_temp = 0
    totalJetEnergy = 0
    totalJetCvsL = 0
    totalJetCvsLpt = 0
    min_dPhi_jet_MET[0] = 1000
    for i in range(0, len(jetPt)):
        if jetPt[i]<20 or abs(entry.Jet_eta[i])>2.4: continue
        if entry.Jet_jetId[i] < 3: continue
        if entry.Jet_puId[i] < 0: continue
#        if jetFilterFlags[i] == False: continue

        Jet_muEF = 1 - (entry.Jet_chEmEF[i] + entry.Jet_chHEF[i] + entry.Jet_neEmEF[i] + entry.Jet_neHEF[i])
        # if Jet_muEF > 0.8: continue
        if entry.Jet_muonIdx1[i] >= 0:
            muPtRatio = entry.Muon_pt[entry.Jet_muonIdx1[i]]/jetPt[i]
        else:
            muPtRatio = -1.

        jet =  TLorentzVector()
        jet.SetPtEtaPhiM(jetPt[i],entry.Jet_eta[i],entry.Jet_phi[i],jetMass[i])
        #
        jetList.append(jet)

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

        jet_chEmEF.push_back(entry.Jet_chEmEF[i])
        jet_jetId.push_back(entry.Jet_jetId[i])
        jet_muonIdx1.push_back(entry.Jet_muonIdx1[i])
        jet_muEF.push_back(Jet_muEF)
        jet_muPtRatio.push_back(muPtRatio)
        jet_nMuons.push_back(entry.Jet_nMuons[i])
        # jet_lepFiltCustom.push_back(jetFilterFlags[i])

        jet_btagCMVA.push_back(entry.Jet_btagCMVA[i])
        jet_btagDeepB.push_back(entry.Jet_btagDeepB[i])
        jet_btagDeepC.push_back(entry.Jet_btagDeepC[i])
        jet_btagCSVV2.push_back(entry.Jet_btagCSVV2[i])

        if isMC:
            j_hadronFlv_List.append(entry.Jet_hadronFlavour[i])
    HT[0]                  = HT_temp

    if totalJetEnergy!=0:
        centrality[0]          = HT_temp/totalJetEnergy
    if HT_temp!=0:
        avgCvsLpT[0]           = (totalJetCvsLpt+1)/HT_temp

    if debug == True:
        print "Preselection 2 : at least two jets with jet_pt > 20 and jet_eta < 2.4"
    if len(jetList)<2: continue


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
    # VBoson = 0
    #
    # # Electron channel
    # if not isElec and len(m_Pt_List)==1:
    #     for i in range(0, len(m_Pt_List)):
    #         mu =  TLorentzVector()
    #         mu.SetPtEtaPhiM(m_Pt_List[i],m_Eta_List[i],m_Phi_List[i],m_Mass_List[i])
    #         muon.append(mu)
    #     VBoson      = (muon[0]+MET)
    #     DPhi_METlep[0] = (muon[0]).DeltaPhi(MET)
    #     W_Mass[0]   = (muon[0]+MET).M()
    #     W_Tmass[0]  = (muon[0]+MET).Mt()
    #     W_Pt[0]     = (muon[0]+MET).Pt()
    #     W_Eta[0]    = (muon[0]+MET).Eta()
    #     W_Phi[0]    = (muon[0]+MET).Phi()
    #
    # # Muon channel
    # if not isMuon and len(e_Pt_List)==1:
    #     for i in range(0, len(e_Pt_List)):
    #         el =  TLorentzVector()
    #         el.SetPtEtaPhiM(e_Pt_List[i],e_Eta_List[i],e_Phi_List[i],e_Mass_List[i])
    #         elec.append(el)
    #     VBoson      = (elec[0]+MET)
    #     DPhi_METlep[0] = (elec[0]).DeltaPhi(MET)
    #     W_Mass[0]   = (elec[0]+MET).M()
    #     W_Tmass[0]  = (elec[0]+MET).Mt()
    #     W_Pt[0]     = (elec[0]+MET).Pt()
    #     W_Eta[0]    = (elec[0]+MET).Eta()
    #     W_Phi[0]    = (elec[0]+MET).Phi()
    #
    # if debug == True:
    #     print "Preselection 3 : W_pt > 50"
    # # if W_Pt[0]<50: continue
    # if W_Mass[0] < 55: continue
    # ==========================================================================

    # ========================= Trigger selection ==============================
    if debug == True:
        print "Preselection 4 : TRIGGERS"
    if is_ME[0]:
        if "Double" in channel: continue
        # if ( entry.HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL == 0 ) and ( entry.HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL == 0 ): continue
        if ( entry.HLT_IsoMu24 == 0 ) and ( entry.HLT_IsoTkMu24 == 0 ): continue
    elif is_MM[0]:
        if "DoubleEG" in channel or "MuonEG" in channel: continue
        if ( entry.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL == 0 ) and ( entry.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ == 0 ) \
             and ( entry.HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL == 0 )  and ( entry.HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ == 0 ) : continue
    elif is_EE[0]:
        if "DoubleMuon" in channel or "MuonEG" in channel: continue
        if ( entry.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL == 0 ) and ( entry.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ == 0 ): continue
    else:
        continue

    TriggerPass = True

    # ==========================================================================

    # ========================= Soft Muon inside jets ==========================
    jetMu_Charge = -1000
    nMuJet[0] = 0

    foundMuJet = False
    for ij in range(len(j_Pt_List)):
        if foundMuJet: break
        for i in [j_MuonIdx1_List[ij],j_MuonIdx2_List[ij]]:
            if i < 0: continue
            if entry.Muon_pt[i]>25 or abs(entry.Muon_eta[i])>2.4: continue
            if entry.Muon_tightId[i]<=0: continue
            if entry.Muon_pfRelIso04_all[i]<0.2: continue

            jetMu = TLorentzVector()
            jetMu.SetPtEtaPhiM(entry.Muon_pt[i],entry.Muon_eta[i],entry.Muon_phi[i],entry.Muon_mass[i])

            dRmj = jetMu.DeltaR(jetList[ij])
            if dRmj > 0.4: continue

            foundMuJet = True
            jetMu_Pt[0] = entry.Muon_pt[i]
            jetMu_iso[0] = entry.Muon_pfRelIso04_all[i]
            jetMu_dz[0] = entry.Muon_dz[i]
            jetMu_dxy[0] = entry.Muon_dxy[i]
            jetMu_sip3d[0] = entry.Muon_sip3d[i]
            jetMu_Charge = entry.Muon_charge[i]
            muJet_idx[0] = ij
            dR_jet_jetMu[0] = dRmj
            dPhi_muJet_MET[0] = jetList[ij].DeltaPhi(MET)
            jetMuPt_by_jetPt[0] =  entry.Muon_pt[i]/j_Pt_List[ij]
            jetMu_PtRel[0] = entry.Muon_pt[i]*math.sin(jetMu.Angle(jetList[ij].Vect()))     #p_{T,rel} = |M|sin(theta): M = Muon pT, theta = angle between jet and muon

            # Make Z
            if is_MM[0]:
                Z2_Mass[0] = (jetMu+mu1).M()
                Z3_Mass[0] = (jetMu+mu2).M()

    if jetMu_Pt[0] < 0: continue
    # ==========================================================================

    # ========================== Higgs Jets stuff ==============================
#     if isMC:
#         hJets_Pt         = sorted(zip(jetList,jet_Pt_List,         jet_FL_List                ), key = lambda pair : pair[1], reverse=True)[0:3]
#         hJets_CvsL       = sorted(zip(jetList,jet_CvsL_List,       jet_FL_List, jet_CvsB_List ), key = lambda pair : pair[1], reverse=True)[0:4]
#         hJets_CvsB       = sorted(zip(jetList,jet_CvsB_List,       jet_FL_List                ), key = lambda pair : pair[1], reverse=True)[0:3]
#         hJets_CvsB_CvsL  = sorted(zip(jetList,jet_CvsB_CvsL_List,  jet_FL_List                ), key = lambda pair : pair[1], reverse=True)[0:3]
#         hJets_CvsB_CvsL2 = sorted(zip(jetList,jet_CvsB_CvsL_List2, jet_FL_List                ), key = lambda pair : pair[1], reverse=True)[0:3]
#
#         numOf_cJet[0] = jet_FL_List.count(4)
#         numOf_bJet[0] = jet_FL_List.count(5)
#         numOf_lJet[0] = jet_FL_List.count(0)
#
#         ######################### FLAGS for splitting W + jets #######################
#     if 'JetsToLNu' in channel:
#         if jet_FL_List.count(4) >= 2:
#             Flag_W_jet[0] = 1
#         elif jet_FL_List.count(4) == 1 and jet_FL_List.count(5) == 1:
#             Flag_W_jet[0] = 2
#         elif jet_FL_List.count(4) == 1 and jet_FL_List.count(0) == 1:
#             Flag_W_jet[0] = 3
#         elif jet_FL_List.count(5) >= 2:
#             Flag_W_jet[0] = 4
#         elif jet_FL_List.count(5) == 1 and jet_FL_List.count(0) == 1:
#             Flag_W_jet[0] = 5
#         else:
#             Flag_W_jet[0] = 6
#
# #     if 'JetsToLNu' in channel:
# #         if jet_FL_List.count(5) >= 2:
# #             Flag_W_jet[0] = 1
# #         elif jet_FL_List.count(4) == 1 and jet_FL_List.count(5) == 1:
# #             Flag_W_jet[0] = 2
# #         elif jet_FL_List.count(4) >= 2:
# #             Flag_W_jet[0] = 3
# #         elif jet_FL_List.count(5) == 1 and jet_FL_List.count(0) == 1:
# #             Flag_W_jet[0] = 4
# #         elif jet_FL_List.count(4) == 1 and jet_FL_List.count(0) == 1:
# #             Flag_W_jet[0] = 5
# #         else:
# #             Flag_W_jet[0] = 6
#
#     if len(jet_Pt_List)>1:
#         if not isMC:
#             hJets_Pt         = sorted(zip(jetList,jet_Pt_List,                         ), key = lambda pair : pair[1], reverse=True)[0:3]
#             hJets_CvsL       = sorted(zip(jetList,jet_CvsL_List,       jet_CvsB_List   ), key = lambda pair : pair[1], reverse=True)[0:4]
#             hJets_CvsB       = sorted(zip(jetList,jet_CvsB_List,                       ), key = lambda pair : pair[1], reverse=True)[0:3]
#             hJets_CvsB_CvsL  = sorted(zip(jetList,jet_CvsB_CvsL_List,                  ), key = lambda pair : pair[1], reverse=True)[0:3]
#             hJets_CvsB_CvsL2 = sorted(zip(jetList,jet_CvsB_CvsL_List2,                 ), key = lambda pair : pair[1], reverse=True)[0:3]
#
#
#         sum_hJets_Pt         = hJets_Pt[0][0]         +   hJets_Pt[1][0]
#         sum_hJets_CvsL       = hJets_CvsL[0][0]       +   hJets_CvsL[1][0]
#         sum_hJets_CvsB       = hJets_CvsB[0][0]       +   hJets_CvsB[1][0]
#         sum_hJets_CvsB_CvsL  = hJets_CvsB_CvsL[0][0]  +   hJets_CvsB_CvsL[1][0]
#         sum_hJets_CvsB_CvsL2 = hJets_CvsB_CvsL2[0][0] +   hJets_CvsB_CvsL2[1][0]
#
#         HIGGS_Pt[0]         = sum_hJets_Pt.M()
#         HIGGS_CvsL_Mass[0]  = sum_hJets_CvsL.M()
#         HIGGS_CvsL_Pt[0]    = sum_hJets_CvsL.Pt()
#         HIGGS_CvsL_Eta[0]   = sum_hJets_CvsL.Eta()
#         HIGGS_CvsL_Phi[0]   = sum_hJets_CvsL.Phi()
#         HIGGS_CvsB[0]       = sum_hJets_CvsB.M()
#
#         DPhi_VH[0]          = (sum_hJets_CvsL).DeltaPhi(VBoson)
#         DR_cc[0]            = (hJets_CvsL[0][0]).DeltaR(hJets_CvsL[1][0])
#
#         top_Mass[0] = (VBoson+hJets_CvsB[-1][0]).M()
#
#         if not isMuon and len(e_Pt_List)==1:
#             lepDR_cc[0]         = (elec[0]).DeltaR(sum_hJets_CvsL)
#             M_lep_c[0]          = (elec[0]+hJets_CvsL[0][0]).M()
#         if not isElec and len(m_Pt_List)==1:
#             lepDR_cc[0]         = (muon[0]).DeltaR(sum_hJets_CvsL)
#             M_lep_c[0]          = (muon[0]+hJets_CvsL[0][0]).M()
#         HIGGS_CvsB_CvsL[0]  = sum_hJets_CvsB_CvsL.M()
#         HIGGS_CvsB_CvsL2[0] = sum_hJets_CvsB_CvsL2.M()
#
#         pt_CvsLJet1[0]       = hJets_CvsL[0][0].Pt()
#         pt_CvsLJet2[0]       = hJets_CvsL[1][0].Pt()
#         eta_CvsLJet1[0]      = hJets_CvsL[0][0].Eta()
#         eta_CvsLJet2[0]      = hJets_CvsL[1][0].Eta()
#         phi_CvsLJet1[0]      = hJets_CvsL[0][0].Phi()
#         phi_CvsLJet2[0]      = hJets_CvsL[1][0].Phi()
#         CvsL_CvsLJet1[0]     = hJets_CvsL[0][1]
#         CvsL_CvsLJet2[0]     = hJets_CvsL[1][1]
#         if isMC:
#             CvsB_CvsLJet1[0]     = hJets_CvsL[0][3]
#             CvsB_CvsLJet2[0]     = hJets_CvsL[1][3]
#             hadronFlavour_CsvLJet1[0] = hJets_CvsL[0][2]
#             hadronFlavour_CsvLJet2[0] = hJets_CvsL[1][2]
#         if not isMC:
#             CvsB_CvsLJet1[0]     = hJets_CvsL[0][2]
#             CvsB_CvsLJet2[0]     = hJets_CvsL[1][2]
#
#         if isMC:
#             if hJets_Pt[0][2] == 4 and hJets_Pt[1][2] == 4:
#                 cc_sum_hJets_Pt         = hJets_Pt[0][0]         +   hJets_Pt[1][0]
#                 cc_HIGGS_Pt[0]          = cc_sum_hJets_Pt.M()
#             if hJets_CvsL[0][2] == 4 and hJets_CvsL[1][2] == 4:
#                 cc_sum_hJets_CvsL       = hJets_CvsL[0][0]       +   hJets_CvsL[1][0]
#                 cc_HIGGS_CvsL[0]        = cc_sum_hJets_CvsL.M()
#
#             if hJets_CvsB[0][2] == 4 and hJets_CvsB[1][2] == 4:
#                 cc_sum_hJets_CvsB       = hJets_CvsB[0][0]       +   hJets_CvsB[1][0]
#                 cc_HIGGS_CvsB[0]        = cc_sum_hJets_CvsB.M()
#             if hJets_CvsB_CvsL[0][2] == 4 and hJets_CvsB_CvsL[1][2] == 4:
#                 cc_sum_hJets_CvsB_CvsL  = hJets_CvsB_CvsL[0][0]  +   hJets_CvsB_CvsL[1][0]
#                 cc_HIGGS_CvsB_CvsL[0]   = cc_sum_hJets_CvsB_CvsL.M()
#             if hJets_CvsB_CvsL2[0][2] == 4 and hJets_CvsB_CvsL2[1][2] == 4:
#                 cc_sum_hJets_CvsB_CvsL2 = hJets_CvsB_CvsL2[0][0] +   hJets_CvsB_CvsL2[1][0]
#                 cc_HIGGS_CvsB_CvsL2[0]  = cc_sum_hJets_CvsB_CvsL2.M()
#
#
#             if (hJets_Pt[0][2] == 4 and hJets_Pt[1][2] != 4) or (hJets_Pt[0][2] != 4 and hJets_Pt[1][2] == 4):
#                 co_sum_hJets_Pt         = hJets_Pt[0][0]         +   hJets_Pt[1][0]
#                 co_HIGGS_Pt[0]          = co_sum_hJets_Pt.M()
#             if (hJets_CvsL[0][2] == 4 and hJets_CvsL[1][2] != 4) or (hJets_CvsL[0][2] != 4 and hJets_CvsL[1][2] == 4):
#                 co_sum_hJets_CvsL       = hJets_CvsL[0][0]       +   hJets_CvsL[1][0]
#                 co_HIGGS_CvsL[0]        = co_sum_hJets_CvsL.M()
#
#             if (hJets_CvsB[0][2] == 4 and hJets_CvsB[1][2] != 4) or (hJets_CvsB[0][2] != 4 and hJets_CvsB[1][2] == 4):
#                 co_sum_hJets_CvsB       = hJets_CvsB[0][0]       +   hJets_CvsB[1][0]
#                 co_HIGGS_CvsB[0]        = co_sum_hJets_CvsB.M()
#             if (hJets_CvsB_CvsL[0][2] == 4 and hJets_CvsB_CvsL[1][2] != 4) or (hJets_CvsB_CvsL[0][2] != 4 and hJets_CvsB_CvsL[1][2] == 4):
#                 co_sum_hJets_CvsB_CvsL  = hJets_CvsB_CvsL[0][0]  +   hJets_CvsB_CvsL[1][0]
#                 co_HIGGS_CvsB_CvsL[0]   = co_sum_hJets_CvsB_CvsL.M()
#             if (hJets_CvsB_CvsL2[0][2] == 4 and hJets_CvsB_CvsL2[1][2] != 4) or (hJets_CvsB_CvsL2[0][2] != 4 and hJets_CvsB_CvsL2[1][2] == 4):
#                 co_sum_hJets_CvsB_CvsL2 = hJets_CvsB_CvsL2[0][0] +   hJets_CvsB_CvsL2[1][0]
#                 co_HIGGS_CvsB_CvsL2[0]  = co_sum_hJets_CvsB_CvsL2.M()
#
#
#             if (hJets_Pt[0][2] != 4 and hJets_Pt[1][2] != 4):
#                 oo_sum_hJets_Pt         = hJets_Pt[0][0]         +   hJets_Pt[1][0]
#                 oo_HIGGS_Pt[0]          = oo_sum_hJets_Pt.M()
#             if (hJets_CvsL[0][2] != 4 and hJets_CvsL[1][2] != 4):
#                 oo_sum_hJets_CvsL       = hJets_CvsL[0][0]       +   hJets_CvsL[1][0]
#                 oo_HIGGS_CvsL[0]        = oo_sum_hJets_CvsL.M()
#             if (hJets_CvsB[0][2] != 4 and hJets_CvsB[1][2] != 4):
#                 oo_sum_hJets_CvsB       = hJets_CvsB[0][0]       +   hJets_CvsB[1][0]
#                 oo_HIGGS_CvsB[0]        = oo_sum_hJets_CvsB.M()
#             if (hJets_CvsB_CvsL[0][2] != 4 and hJets_CvsB_CvsL[1][2] != 4):
#                 oo_sum_hJets_CvsB_CvsL  = hJets_CvsB_CvsL[0][0]  +   hJets_CvsB_CvsL[1][0]
#                 oo_HIGGS_CvsB_CvsL[0]   = oo_sum_hJets_CvsB_CvsL.M()
#             if (hJets_CvsB_CvsL2[0][2] != 4 and hJets_CvsB_CvsL2[1][2] != 4):
#                 oo_sum_hJets_CvsB_CvsL2 = hJets_CvsB_CvsL2[0][0] +   hJets_CvsB_CvsL2[1][0]
#                 oo_HIGGS_CvsB_CvsL2[0]  = oo_sum_hJets_CvsB_CvsL2.M()
#
#     ETSum = 0
# #     FWM_0 = 0
#     FWM_1 = 0
#     FWM_2 = 0
#     FWM_3 = 0
#     FWM_4 = 0
#     for jet in jetList:
#         ETSum += jet.Et()
#     for jet1 in jetList:
#         for jet2 in jetList:
#             EToverETSum2 = jet1.Et()*jet2.Et()/ETSum**2
#             cosTheta_ij = (jet1.Px()*jet2.Px() + jet1.Py()*jet2.Py() + jet1.Pz()*jet2.Pz())/(jet1.Rho()*jet2.Rho())
# #             FWM_0 += EToverETSum2
#             FWM_1 += EToverETSum2*cosTheta_ij
#             FWM_2 += EToverETSum2*0.5   * (  3*pow(cosTheta_ij,2)- 1)
#             FWM_3 += EToverETSum2*0.5   * (  5*pow(cosTheta_ij,3)- 3*cosTheta_ij)
#             FWM_4 += EToverETSum2*0.125 * ( 35*pow(cosTheta_ij,4)- 30*pow(cosTheta_ij,2)+3)
# #     FWmoment_0[0] = FWM_0
#     FWmoment_1[0] = FWM_1
#     FWmoment_2[0] = FWM_2
#     FWmoment_3[0] = FWM_3
#     FWmoment_4[0] = FWM_4
    # ==========================================================================

    # ============================= Store leptons ==============================

    for i, ePt in enumerate(e_Pt_List):
        E_Mass.push_back(e_Mass_List[i])
        E_Pt.push_back(ePt)
        E_Eta.push_back(e_Eta_List[i])
        E_Phi.push_back(e_Phi_List[i])
        E_Charge.push_back(e_Charge_List[i])

        # Neutrino stuff
        # if len(jet_Pt_List)>1:
        #     Nu = TLorentzVector()
        #     solver_CvsL = nu.singleNeutrinoSolution((hJets_CvsL[0][0]+hJets_CvsL[1][0]),elec[0],(MET.Px(),MET.Py()),sigma2,mW**2,mH**2)
        #     Neutrino = solver_CvsL.nu
        #     if type(Neutrino) is not types.BooleanType:
        #         Nu.SetXYZM(Neutrino[0],Neutrino[1],Neutrino[2],0)
        #         W_Mass_nuSol[0] = (Nu + elec[0]).M()
        #         W_Pt_nuSol[0]   = (Nu + elec[0]).Pt()
        #         W_Eta_nuSol[0]  = (Nu + elec[0]).Eta()
        #         W_Phi_nuSol[0]  = (Nu + elec[0]).Phi()
        #         solver_chi2[0] = solver_CvsL.chi2
    # if isMuon:
    # is_M[0] = isMuon
    for i, mPt in enumerate(m_Pt_List):
        M_Mass.push_back(m_Mass_List[i])
        M_Pt.push_back(mPt)
        M_Eta.push_back(m_Eta_List[i])
        M_Phi.push_back(m_Phi_List[i])
        M_Charge.push_back(m_Charge_List[i])

        # Neutrino stuff
        # if len(jet_Pt_List)>1:
        #     Nu = TLorentzVector()
        #     solver_CvsL = nu.singleNeutrinoSolution((hJets_CvsL[0][0]+hJets_CvsL[1][0]),muon[0],(MET.Px(),MET.Py()),sigma2,mW**2,mH**2)
        #     Neutrino = solver_CvsL.nu
        #     if type(Neutrino) is not types.BooleanType:
        #         Nu.SetXYZM(Neutrino[0],Neutrino[1],Neutrino[2],0)
        #         W_Mass_nuSol[0] = (Nu + muon[0]).M()
        #         W_Pt_nuSol[0]   = (Nu + muon[0]).Pt()
        #         W_Eta_nuSol[0]  = (Nu + muon[0]).Eta()
        #         W_Phi_nuSol[0]  = (Nu + muon[0]).Phi()
        #         solver_chi2[0] = solver_CvsL.chi2
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

#     if HIGGS_CvsL_Mass[0]<90 or HIGGS_CvsL_Mass[0]>150:
#         is_H_mass_CR[0] = 1
#     if W_Mass[0]<65 or W_Mass[0]>95:
#         is_W_mass_CR[0] = 1


    # ========================= Flags for W to cc or bb ========================
    # if isMC:
    #     dau1c_index   = -1
    #     dau2c_index   = -1
    #     dau1b_index   = -1
    #     dau2b_index   = -1
    #     num_Z         = 0
    #     genpart_List  = []
    #
    #     for genpart in range(entry.nGenPart):
    #         if entry.GenPart_pdgId[genpart] == 23 and ( entry.GenPart_statusFlags[genpart] & 8192 ) == 8192 :
    #             genpart_List.append(genpart)
    #             num_Z += 1
    #     if len(genpart_List) == 2:
    #         for mother_index in genpart_List:
    #            for genpart in range(entry.nGenPart):
    #                if abs(entry.GenPart_pdgId[genpart]) == 4 and entry.GenPart_genPartIdxMother[genpart] == mother_index:
    #                    if dau1c_index > -1 and dau2c_index > -1: continue
    #                    elif dau1c_index > -1 :
    #                        dau2c_index = genpart
    #                    else :
    #                        dau1c_index = genpart
    #            for genpart in range(entry.nGenPart):
    #                if abs(entry.GenPart_pdgId[genpart]) == 5 and entry.GenPart_genPartIdxMother[genpart] == mother_index:
    #                    if dau1b_index > -1 and dau2b_index > -1: continue
    #                    elif dau1b_index > -1 :
    #                        dau2b_index = genpart
    #                    else :
    #                        dau1b_index = genpart
    #         if dau1c_index > -1 and dau2c_index > -1:
    #             if  abs(entry.GenPart_pdgId[dau1c_index]) == 4 and abs(entry.GenPart_pdgId[dau2c_index]) == 4: is_ZtoCCorBB[0] = 1
    #         elif dau1b_index > -1 and dau2b_index > -1:
    #             if  abs(entry.GenPart_pdgId[dau1b_index]) == 5 and abs(entry.GenPart_pdgId[dau2b_index]) == 5: is_ZtoCCorBB[0] = 2
    #         else: is_ZtoCCorBB[0] = 0
    # ==========================================================================

    # ============================ Calculate weights ===========================
    # Sign Weights
    # if isElec:
    #     signWeight[0] = e_Charge_List[0]*jetMu_Charge*(-1.)
    # elif isMuon:
    #     signWeight[0] = m_Charge_List[0]*jetMu_Charge*(-1.)
    # else:
    #     continue

    genWeight[0] = 1.
    PUWeight[0]  = 1.
    PUWeight_up[0] = 1.
    PUWeight_down[0] = 1.
    EleIDSF[0] = 1.
    EleIDSF_up[0] = 1.
    EleIDSF_down[0] = 1.
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

    if isMC:
        # MC Gen Weight
        genWeight[0] = entry.genWeight

        # PU Weights
        PUWeight[0] = entry.puWeight
        if PUWeight[0]!=0:
            PUWeight_up[0] = entry.puWeightUp/PUWeight[0]
            PUWeight_down[0] = entry.puWeightDown/PUWeight[0]

        # LHE Scale
        if not 'QCD' in channel and not 'ST' in channel and not 'WW' in channel and not 'WZ' in channel:
            LHEScaleList = list(entry.LHEScaleWeight)

            LHEScaleWeight_muR_up[0] = LHEScaleList[7]
            LHEScaleWeight_muR_down[0] = LHEScaleList[1]

        # LHEScaleWeight_muF_up[0] = LHEScaleList[5]
            LHEScaleWeight_muF_down[0] = LHEScaleList[3]
            LHEScaleWeight_muF_up[0] = LHEScaleList[5]

        # Electron ID
        for i in range(len(e_Pt_List)):
            xbin = EGamma2016histo2d.GetXaxis().FindBin(e_Eta_List[i])
            ybin = EGamma2016histo2d.GetYaxis().FindBin(e_Pt_List[i])
            EleID = EGamma2016histo2d.GetBinContent(xbin,ybin)
            EleIDErr = EGamma2016histo2d.GetBinError(xbin,ybin)

            EleIDSF[0] *= EleID
            EleIDSF_up[0] *= (EleID+EleIDErr)
            EleIDSF_down[0] *= (EleID-EleIDErr)

        if EleIDSF[0]!=0:
            EleIDSF_up[0] /= EleIDSF[0]
            EleIDSF_down[0] /= EleIDSF[0]

        ## Muon ID
        for i in range(len(m_Pt_List)):
            xbin = MuID2016BFhisto2d.GetXaxis().FindBin(m_Eta_List[i])
            ybin = MuID2016BFhisto2d.GetYaxis().FindBin(m_Pt_List[i])
            MuIDBF = MuID2016BFhisto2d.GetBinContent(xbin,min(6,ybin))
            MuIDBF_err = MuID2016BFhisto2d.GetBinError(xbin,min(6,ybin))

            xbin = MuID2016GHhisto2d.GetXaxis().FindBin(m_Eta_List[i])
            ybin = MuID2016GHhisto2d.GetYaxis().FindBin(m_Pt_List[i])
            MuIDGH = MuID2016GHhisto2d.GetBinContent(xbin,min(6,ybin))
            MuIDGH_err = MuID2016GHhisto2d.GetBinError(xbin,min(6,ybin))

            MuIDSF[0] *= 0.55*MuIDBF + 0.45*MuIDGH

            MuIDSF_up[0] *= (0.55*(MuIDBF+MuIDBF_err) + 0.45*(MuIDGH+MuIDGH_err))
            MuIDSF_down[0] *= (0.55*(MuIDBF-MuIDBF_err) + 0.45*(MuIDGH-MuIDGH_err))
        if MuIDSF[0]!=0:
            MuIDSF_up[0] /= MuIDSF[0]
            MuIDSF_down[0] /= MuIDSF[0]

    eventWeight[0] = genWeight[0] * PUWeight[0] * EleIDSF[0] * MuIDSF[0]
    # print eventWeight[0], PUWeight_up[0],PUWeight_down[0],MuIDSF_up[0],MuIDSF_down[0]

    # ==========================================================================

    # ============================ Fill output tree ============================
    if len(j_Pt_List) >= 1 and TriggerPass:
        run[0]              = entry.run
        lumiBlock[0]        = entry.luminosityBlock
        event[0]            = entry.event
        if isMC and not 'WW' in channel and not 'WZ' in channel and not 'QCD' in channel:
            LHE_HT[0]           = entry.LHE_HT
            if type(entry.LHE_Njets) is str:
                LHE_Njets[0]        = ord(entry.LHE_Njets)
            else:
                LHE_Njets[0]        = entry.LHE_Njets

        nPV[0] = entry.PV_npvs
        nPVGood[0] = entry.PV_npvsGood
        nSV[0] = entry.nSV

        # if isMuon:
        #     QCDveto[0] = int( M_RelIso[0] < 0.05 and (hardMu_Jet_PtRatio < 0 or hardMu_Jet_PtRatio > 0.75) and abs(M_dz[0]) < .01 and abs(M_dxy[0]) < .002 and M_sip3d[0] < 0.2 )
        # elif isElec:
        #     QCDveto[0] = int( E_RelIso[0] < 0.05 and (hardE_Jet_PtRatio < 0 or hardE_Jet_PtRatio > 0.75) and abs(E_dz[0]) < .02 and abs(E_dxy[0]) < .01 and E_sip3d[0] < 0.25 )

        # SoftActivityJetHT[0]       = entry.SoftActivityJetHT
        # SoftActivityJetNjets2[0]   = entry.SoftActivityJetNjets2
        # SoftActivityJetNjets5[0]   = entry.SoftActivityJetNjets5
        # SoftActivityJetNjets10[0]  = entry.SoftActivityJetNjets10

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
